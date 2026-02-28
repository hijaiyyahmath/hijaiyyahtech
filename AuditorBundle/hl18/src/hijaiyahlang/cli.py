import argparse, json, os, sys
from typing import Any, Dict, List

from hijaiyahlang.dataset import load_mh28_csv, cod_word
from hijaiyahlang.core import audit_v18, mod18

def main() -> None:
    # Ensure UTF-8 output for Hijaiyah characters
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(prog="hl18")
    ap.add_argument("--csv", required=False, help="Path ke MH-28-v1.0-18D.csv")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_cod = sub.add_parser("cod")
    p_cod.add_argument("word")

    p_aud = sub.add_parser("audit")
    p_aud.add_argument("word")

    p_mod = sub.add_parser("mod")
    p_mod.add_argument("word")
    p_mod.add_argument("m", type=int)

    # HISA-VM subcommands
    aud_l = sub.add_parser("hisa-audit-letter")
    aud_l.add_argument("--release-dir", required=True)
    aud_l.add_argument("--release-id", default="HL-18-v1.0+local.1")
    aud_l.add_argument("--letter-id", required=True)
    aud_l.add_argument("--closed-hint", type=int, choices=[0,1], default=0)
    aud_l.add_argument("--hisa-spec", required=True)
    aud_l.add_argument("--artifacts-dir", required=True)

    aud_w = sub.add_parser("hisa-audit-word")
    aud_w.add_argument("--release-dir", required=True)
    aud_w.add_argument("--release-id", default="HL-18-v1.0+local.1")
    aud_w.add_argument("--text", required=True)
    aud_w.add_argument("--closed-hint", type=int, choices=[0,1], default=0)
    aud_w.add_argument("--hisa-spec", required=True)
    aud_w.add_argument("--artifacts-dir", required=True)

    args = ap.parse_args() # Corrected from p.parse_args()

    if args.cmd in ("cod", "audit", "mod"):
        if not args.csv: # Ensure --csv is provided for these commands
            ap.error("--csv is required for 'cod', 'audit', and 'mod' commands.")
        ds = load_mh28_csv(args.csv)

    if args.cmd == "cod":
        v = cod_word(args.word, ds)
        print(json.dumps({"ok": True, "op": "cod", "word": args.word, "v18": v}, ensure_ascii=False))

    elif args.cmd == "audit":
        v = cod_word(args.word, ds)
        ar = audit_v18(v)
        print(json.dumps({
            "ok": ar.ok, "op": "audit", "word": args.word, "v18": v,
            "U": ar.U, "rho": ar.rho, "mod4": ar.mod4, "checks": ar.checks
        }, ensure_ascii=False))

    elif args.cmd == "mod":
        v = cod_word(args.word, ds)
        out = mod18(v, args.m)
        print(json.dumps({"ok": True, "op": "mod", "word": args.word, "m": args.m, "v18_mod": out}, ensure_ascii=False))

    elif args.cmd == "hisa-audit-letter":
        rel = load_release(args.release_dir, release_id=args.release_id, check_manifest=True)
        cfg = load_hisa_integration_spec(args.hisa_spec)
        vm = HISAVMRunner(cfg)
        lid = normalize_letter_id(args.letter_id)
        idx = index_of_letter(lid)
        workdir = Path(args.artifacts_dir)
        res = vm.audit_master_index(
            workdir=workdir,
            master_csv=rel.dataset_path,
            index=idx,
            closed_hint=args.closed_hint,
        )
        print(json.dumps({
            "mode": "letter",
            "letter_id": lid,
            "index": idx,
            "closed_hint": args.closed_hint,
            "hisa_vm": {
                "ok": res.ok, "status": res.status,
                "trap": res.trap, "trap_code": res.trap_code, "trap_name": res.trap_name,
                "registers": res.registers,
            }
        }, ensure_ascii=False, indent=2))

    elif args.cmd == "hisa-audit-word":
        rel = load_release(args.release_dir, release_id=args.release_id, check_manifest=True)
        cfg = load_hisa_integration_spec(args.hisa_spec)
        vm = HISAVMRunner(cfg)
        enc = encode_text(rel.dataset, args.text)
        workdir = Path(args.artifacts_dir)
        master_overlay = workdir / "master_overlay_28.csv"
        write_master_overlay_28(rel.dataset, enc.v18, master_overlay)

        res = vm.audit_master_index(
            workdir=workdir,
            master_csv=master_overlay,
            index=0,
            closed_hint=args.closed_hint,
        )
        print(json.dumps({
            "mode": "word",
            "text": args.text,
            "letters": enc.letters,
            "v18": list(enc.v18),
            "closed_hint": args.closed_hint,
            "master_overlay": str(master_overlay),
            "hisa_vm": {
                "ok": res.ok, "status": res.status,
                "trap": res.trap, "trap_code": res.trap_code, "trap_name": res.trap_name,
                "registers": res.registers,
            }
        }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
