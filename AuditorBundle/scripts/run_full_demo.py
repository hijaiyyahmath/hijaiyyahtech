from __future__ import annotations
import json, subprocess, os
from pathlib import Path

def run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    env = os.environ.copy()
    cp = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
    return cp.returncode, cp.stdout.decode("utf-8","replace"), cp.stderr.decode("utf-8","replace")

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    artifacts = root / "artifacts" / "runs"
    artifacts.mkdir(parents=True, exist_ok=True)

    # 1) Integrity verify (HL-18 release)
    cmd_verify = ["verify-hl18-release", "--spec", "specs/HL18_release_integrity_local.yaml", "--check-manifest"]
    rc, out, err = run(cmd_verify, root)
    (artifacts / "verify_stdout.txt").write_text(out, encoding="utf-8")
    (artifacts / "verify_stderr.txt").write_text(err, encoding="utf-8")
    if rc != 0:
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")
        raise SystemExit("FAIL: verify-hl18-release")

    # 2) Demo audit letter Jim (ج)
    jim_dir = artifacts / "audit_jim"
    cmd_jim = [
        "hl18", "hisa-audit-letter",
        "--release-dir", "release/HL-18-v1.0+local.1",
        "--letter-id", "ج",
        "--closed-hint", "0",
        "--hisa-spec", "specs/HISA_integration_local.yaml",
        "--artifacts-dir", str(jim_dir),
    ]
    rc, out, err = run(cmd_jim, root)
    jim_dir.mkdir(parents=True, exist_ok=True)
    (jim_dir / "stdout.json").write_text(out, encoding="utf-8")
    (jim_dir / "stderr.txt").write_text(err, encoding="utf-8")
    if rc != 0:
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")
        raise SystemExit("FAIL: hisa-audit-letter Jim")

    # 3) Demo audit word "سلام" (HL-18 -> v18 -> overlay -> HISA-VM)
    w_dir = artifacts / "audit_word_salam"
    cmd_word = [
        "hl18", "hisa-audit-word",
        "--release-dir", "release/HL-18-v1.0+local.1",
        "--text", "سلام",
        "--closed-hint", "0",
        "--hisa-spec", "specs/HISA_integration_local.yaml",
        "--artifacts-dir", str(w_dir),
    ]
    rc, out, err = run(cmd_word, root)
    w_dir.mkdir(parents=True, exist_ok=True)
    (w_dir / "stdout.json").write_text(out, encoding="utf-8")
    (w_dir / "stderr.txt").write_text(err, encoding="utf-8")
    if rc != 0:
        print(f"STDOUT: {out}")
        print(f"STDERR: {err}")
        raise SystemExit("FAIL: hisa-audit-word سلام")

    # 4) Summary
    summary = {
        "ok": True,
        "outputs": {
            "jim": str((jim_dir / "stdout.json").relative_to(root)),
            "word_salam": str((w_dir / "stdout.json").relative_to(root)),
        }
    }
    (artifacts / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("OK: run_full_demo completed. See artifacts/runs/")

if __name__ == "__main__":
    main()
