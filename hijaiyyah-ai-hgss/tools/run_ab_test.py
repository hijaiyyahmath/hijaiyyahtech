# tools/run_ab_test.py
from __future__ import annotations

import os, json, argparse, time
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

from hijaiyyah_ai_hgss.eval.dataset import load_jsonl_cases
from hijaiyyah_ai_hgss.validators.schema_frozen import validate_schema
from hijaiyyah_ai_hgss.validators.cbor_event_hash import validate_event_sha256
from hijaiyyah_ai_hgss.validators.hgss_oracle import hgss_oracle_verify
from hijaiyyah_ai_hgss.validators.autofill import autofill_event_and_write_artifacts

from hijaiyyah_ai_hgss.llm.openai_compat import OpenAICompatClient


def run_id():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z").replace(":","").replace("-","")


def extract_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        t = t.replace("```json", "").replace("```", "").strip()
    i = t.find("{"); j = t.rfind("}")
    if i == -1 or j == -1 or j <= i:
        raise ValueError("NO_JSON_OBJECT")
    return json.loads(t[i:j+1])


def top_err(errs) -> str:
    if not errs:
        return "PASS"
    e0 = errs[0]
    if isinstance(e0, dict):
        return e0.get("err_type","UNKNOWN")
    return getattr(e0, "err_type", "UNKNOWN")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", default="reports/ab_report.json")
    ap.add_argument("--hgss-repo", default=os.getenv("HGSS_REPO","deps/hgss-hc18dc"))
    ap.add_argument("--max-iters", type=int, default=int(os.getenv("MAX_REPAIR_ITERS","3")))
    ap.add_argument("--artifacts-root", default="artifacts/runs")
    args = ap.parse_args()

    cases = load_jsonl_cases(args.dataset)
    rid = run_id()
    root = Path(args.artifacts_root) / rid
    root.mkdir(parents=True, exist_ok=True)

    llm = OpenAICompatClient.from_env()

    baseline_pass = 0
    guarded_raw_pass = 0
    guarded_final_pass = 0
    guarded_steps_sum = 0

    baseline_hist = Counter()
    guarded_fail_hist = Counter()

    baseline_lat = []
    guarded_lat = []

    manifest = {
        "run_id": rid,
        "dataset": args.dataset,
        "hgss_lock": {"version":"HGSS-HCVM-v1.HC18DC","git_hash":"e392c68"},
        "cases": []
    }

    for c in cases:
        cid = c.get("id","NO_ID")
        case_dir = root / f"case_{cid}"
        case_dir.mkdir(parents=True, exist_ok=True)

        rec = {"id": cid, "baseline": {}, "guarded": {}}

        # ---------------- BASELINE (one-shot, no autofill, no repair)
        t0 = time.time()
        btxt = llm.generate(c["system_prompt"], c["user_prompt"])
        t1 = time.time()
        baseline_lat.append((t1-t0)*1000.0)
        (case_dir / "baseline_raw.txt").write_text(btxt, encoding="utf-8")

        berrs = []
        try:
            bev = extract_json(btxt)
            (case_dir / "baseline_event_raw.json").write_text(json.dumps(bev, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")

            e1 = validate_schema(bev)
            if e1:
                berrs = [x.__dict__ for x in e1]
            else:
                e2 = validate_event_sha256(bev)
                if e2:
                    berrs = [x.__dict__ for x in e2]
                else:
                    (case_dir / "baseline_event_single.json").write_text(json.dumps(bev, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")
                    e3 = hgss_oracle_verify(args.hgss_repo, str(case_dir / "baseline_event_single.json"))
                    if e3:
                        berrs = [x.__dict__ for x in e3]
                    else:
                        baseline_pass += 1
        except Exception as e:
            berrs = [{"err_type":"JSON_PARSE_FAIL","message":str(e),"path":"$"}]

        if berrs:
            baseline_hist[top_err(berrs)] += 1

        rec["baseline"]["ok_raw_at_1"] = (len(berrs) == 0)
        rec["baseline"]["err_top"] = "" if not berrs else top_err(berrs)

        # ---------------- GUARDED (repair loop + AUTOFILL + oracle)
        t0 = time.time()
        current = llm.generate(c["system_prompt"], c["user_prompt"])
        (case_dir / "guarded_iter_0_raw.txt").write_text(current, encoding="utf-8")

        errors = []
        final_ok = False
        steps_used = 0
        raw_ok_at1 = False

        for it in range(0, args.max_iters + 1):
            steps_used = it
            try:
                ev = extract_json(current)
            except Exception as e:
                errors = [{"err_type":"JSON_PARSE_FAIL","message":str(e),"path":"$"}]
            else:
                e1 = validate_schema(ev)
                if e1:
                    errors = [x.__dict__ for x in e1]
                else:
                    if it == 0:
                        raw_ok_at1 = True
                    ev2 = autofill_event_and_write_artifacts(
                        event=ev,
                        case_dir=str(case_dir),
                        hgss_repo=args.hgss_repo,
                        hsm_profile="A",
                    )
                    e2 = validate_event_sha256(ev2)
                    if e2:
                        errors = [x.__dict__ for x in e2]
                    else:
                        e3 = hgss_oracle_verify(args.hgss_repo, str(case_dir / "event_single.json"))
                        if e3:
                            errors = [x.__dict__ for x in e3]
                        else:
                            final_ok = True
                            errors = []
                            break

            if it == args.max_iters:
                break

            feedback = {
                "type": "HIJAIYYAH_AI_REPAIR_REQUEST",
                "errors": errors,
                "lock": {"version":"HGSS-HCVM-v1.HC18DC","git_hash":"e392c68"},
                "rule": "Return ONLY corrected JSON object. No markdown."
            }
            repair_user = f"Previous Output:\n{current}\n\nVALIDATION_FAILED:\n{json.dumps(feedback, ensure_ascii=False, indent=2)}"
            current = llm.generate("You are a strict JSON compliance repair assistant.", repair_user)
            (case_dir / f"guarded_iter_{it+1}_raw.txt").write_text(current, encoding="utf-8")

        t1 = time.time()
        guarded_lat.append((t1-t0)*1000.0)

        if raw_ok_at1:
            guarded_raw_pass += 1
        if final_ok:
            guarded_final_pass += 1
        else:
            guarded_fail_hist[top_err(errors) if errors else "UNKNOWN"] += 1

        guarded_steps_sum += steps_used

        rec["guarded"]["ok_raw_at_1"] = raw_ok_at1
        rec["guarded"]["ok_final_at_k"] = final_ok
        rec["guarded"]["repair_steps"] = steps_used
        rec["guarded"]["err_top"] = "" if final_ok else top_err(errors)

        manifest["cases"].append(rec)

    total = len(cases)
    report = {
        "run_id": rid,
        "hgss_lock": {"version":"HGSS-HCVM-v1.HC18DC","git_hash":"e392c68"},
        "dataset": {"path": args.dataset, "cases": total},
        "baseline": {
            "raw_pass_at_1": baseline_pass/total if total else 0.0,
            "error_hist": dict(baseline_hist)
        },
        "guarded": {
            "raw_pass_at_1": guarded_raw_pass/total if total else 0.0,
            "final_pass_at_k": guarded_final_pass/total if total else 0.0,
            "avg_repair_steps": guarded_steps_sum/total if total else 0.0,
            "error_hist_final_failures": dict(guarded_fail_hist)
        },
        "latency_ms": {
            "baseline_mean": sum(baseline_lat)/len(baseline_lat) if baseline_lat else 0.0,
            "guarded_mean": sum(guarded_lat)/len(guarded_lat) if guarded_lat else 0.0
        },
        "artifacts_root": str(root)
    }

    (root / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"[OK] report: {outp}")
    print(f"[OK] artifacts: {root}")


if __name__ == "__main__":
    main()
