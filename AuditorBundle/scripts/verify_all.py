from __future__ import annotations
import subprocess
from pathlib import Path

def run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    cp = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return cp.returncode, cp.stdout.decode("utf-8","replace"), cp.stderr.decode("utf-8","replace")

def main() -> None:
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    root = Path(__file__).resolve().parents[1]
    
    # Ensure local sources are in path regardless of pip install success
    sys.path.insert(0, str(root / "hisa-vm" / "src"))
    sys.path.insert(0, str(root / "hl18" / "src"))
    
    art = root / "artifacts" / "verify_all"
    art.mkdir(parents=True, exist_ok=True)

    # A) HL-18 integrity
    cmd = ["verify-hl18-release", "--spec", "specs/HL18_release_integrity_local.yaml", "--check-manifest"]
    rc, out, err = run(cmd, root)
    (art / "verify-hl18-release.stdout.txt").write_text(out, encoding="utf-8")
    (art / "verify-hl18-release.stderr.txt").write_text(err, encoding="utf-8")
    if rc != 0:
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")
        raise SystemExit("FAIL: verify-hl18-release")

    # B) PASS conformance (Jim)
    cmd = [
        "hl18", "hisa-audit-letter",
        "--release-dir", "release/HL-18-v1.0+local.1",
        "--letter-id", "ج",
        "--closed-hint", "0",
        "--hisa-spec", "specs/HISA_integration_local.yaml",
        "--artifacts-dir", "artifacts/verify_all/pass_jim"
    ]
    rc, out, err = run(cmd, root)
    (art / "pass_jim.stdout.json").write_text(out, encoding="utf-8")
    (art / "pass_jim.stderr.txt").write_text(err, encoding="utf-8")
    if rc != 0:
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")
        raise SystemExit("FAIL: expected HALT state for PASS conformance")

    # C) TRAP CORE-1 conformance: program tanpa SETFLAG
    con_dir = root / "artifacts" / "verify_all" / "trap_core1"
    con_dir.mkdir(parents=True, exist_ok=True)

    src = con_dir / "trap_core1.hisaasm"
    src.write_text(
        "; CORE-1 negative test (missing SETFLAG)\n"
        "LDH_V18 V0, 4\n"
        "AUDIT V0\n"
        "HALT\n",
        encoding="utf-8"
    )
    binp = con_dir / "trap_core1.bin"

    # assemble
    cmd = ["python", "hisa-vm/tools/hisa-asm.py", "--in", str(src), "--out", str(binp)]
    rc, out, err = run(cmd, root)
    (con_dir / "asm.stdout.txt").write_text(out, encoding="utf-8")
    (con_dir / "asm.stderr.txt").write_text(err, encoding="utf-8")
    if rc != 0 or not binp.exists():
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")
        raise SystemExit("FAIL: assembling CORE-1 trap program")

    # run
    cmd = [
        "python", "hisa-vm/tools/hisa-run.py",
        "--hij28", "hisa-vm/data/HIJAIYYAH_28.txt",
        "--program", str(binp),
        "--master", "release/HL-18-v1.0+local.1/MH-28-v1.0-18D.csv"
    ]
    rc, out, err = run(cmd, root)
    (con_dir / "vm.stdout.txt").write_text(out, encoding="utf-8")
    (con_dir / "vm.stderr.txt").write_text(err, encoding="utf-8")
    if rc != 0:
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")
        raise SystemExit("FAIL: hisa-run failed during CORE-1 trap execution")
    
    # Check for TRAP(5) or CONFORMANCE_SETFLAG_REQUIRED
    if '"state": "TRAP"' not in out or "CORE1_REQUIRED" not in out:
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")
        raise SystemExit("FAIL: expected TRAP(5) CORE1_REQUIRED")

    print("OK: verify_all completed (integrity + PASS + TRAP CORE-1)")

if __name__ == "__main__":
    main()
