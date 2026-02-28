# tools/run_guarded_once.py
from __future__ import annotations

import os, json, argparse
from pathlib import Path
from datetime import datetime, timezone

from hijaiyyah_ai_hgss.eval.dataset import load_jsonl_cases
from hijaiyyah_ai_hgss.validators.schema_frozen import validate_schema
from hijaiyyah_ai_hgss.validators.cbor_event_hash import validate_event_sha256
from hijaiyyah_ai_hgss.validators.hgss_oracle import hgss_oracle_verify
from hijaiyyah_ai_hgss.validators.autofill import autofill_event_and_write_artifacts

from hijaiyyah_ai_hgss.llm.openai_compat import OpenAICompatClient  # must expose generate(system, user)


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
    for k in ("err_type","category","code"):
        if hasattr(e0, k):
            return str(getattr(e0, k))
        if isinstance(e0, dict) and k in e0:
            return str(e0[k])
    return "UNKNOWN"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--hgss-repo", default=os.getenv("HGSS_REPO","deps/hgss-hc18dc"))
    ap.add_argument("--max-iters", type=int, default=int(os.getenv("MAX_REPAIR_ITERS","3")))
    ap.add_argument("--artifacts-root", default="artifacts/runs")
    args = ap.parse_args()

    cases = load_jsonl_cases(args.dataset)
    case = next((c for c in cases if c.get("id") == args.case_id), None)
    if not case:
        raise SystemExit(f"Case not found: {args.case_id}")

    rid = run_id()
    case_dir = Path(args.artifacts_root) / rid / f"case_{args.case_id}"
    case_dir.mkdir(parents=True, exist_ok=True)

    llm = OpenAICompatClient.from_env()  # recommended helper; else construct with env vars

    # Initial generation
    current = llm.generate(case["system_prompt"], case["user_prompt"])
    (case_dir / "guarded_iter_0_raw.txt").write_text(current, encoding="utf-8")

    print(f"=== Guarded Debug === run_id={rid} case_id={args.case_id}")
    errors = []

    for it in range(0, args.max_iters + 1):
        try:
            ev = extract_json(current)
        except Exception as e:
            errors = [{"err_type":"JSON_PARSE_FAIL","message":str(e),"path":"$"}]
            print(f"[iter {it}] FAIL: {top_err(errors)}")
        else:
            # Stage 1: schema
            e1 = validate_schema(ev)
            if e1:
                errors = [x.__dict__ for x in e1]
                print(f"[iter {it}] FAIL: {top_err(errors)} (schema)")
            else:
                # Autofill + artifacts
                ev2 = autofill_event_and_write_artifacts(
                    event=ev,
                    case_dir=str(case_dir),
                    hgss_repo=args.hgss_repo,
                    hsm_profile="A",
                )
                # Stage 2: event_sha256
                e2 = validate_event_sha256(ev2)
                if e2:
                    errors = [x.__dict__ for x in e2]
                    print(f"[iter {it}] FAIL: {top_err(errors)} (event_sha256)")
                else:
                    # Stage 3: oracle
                    e3 = hgss_oracle_verify(args.hgss_repo, str(case_dir / "event_single.json"))
                    if e3:
                        errors = [x.__dict__ for x in e3]
                        print(f"[iter {it}] FAIL: {top_err(errors)} (oracle)")
                    else:
                        print(f"[iter {it}] PASS: ORACLE_OK")
                        print(f"[OK] artifacts: {case_dir}")
                        return

        # repair prompt
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

    print("[TRAP] max iters reached")
    print(f"[OUT] artifacts: {case_dir}")
    raise SystemExit(2)


if __name__ == "__main__":
    main()
