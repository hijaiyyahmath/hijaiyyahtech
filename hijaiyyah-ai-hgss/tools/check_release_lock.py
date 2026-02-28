import os
import sys
import argparse
from pathlib import Path

# Normative Locks for this Release
RELEASE_VERSION = "HGSS-HCVM-v1.HC18DC"
RELEASE_COMMIT = "e392c68"

# Files that MUST contain the locks
SYNC_FILES = [
    "spec/RELEASE_LOCK.md",
    "spec/SYSTEM_OVERVIEW.md",
    "spec/TASK_HGSS_EVIDENCE_JSON.md",
    "src/hijaiyyah_ai_hgss/validators/schema_frozen.py",
    "src/hijaiyyah_ai_hgss/config.py"
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expected", default=RELEASE_VERSION)
    ap.add_argument("--expected-hash", default=RELEASE_COMMIT)
    args = ap.parse_args()

    failed_files = []
    root = Path(__file__).resolve().parents[1]

    print(f"Hijaiyyah-AI Release Lock Check: {args.expected} @ {args.expected_hash}")
    print("-" * 50)

    for rel_path in SYNC_FILES:
        target = root / rel_path
        if not target.exists():
            print(f"[MISSING] {rel_path}")
            failed_files.append(rel_path)
            continue
        
        content = target.read_text(encoding="utf-8")
        v_ok = args.expected in content
        h_ok = args.expected_hash in content
        
        status = "[OK]" if (v_ok and h_ok) else "[FAIL]"
        details = []
        if not v_ok: details.append(f"missing version {args.expected}")
        if not h_ok: details.append(f"missing hash {args.expected_hash}")
        
        print(f"{status} {rel_path} {'(' + ', '.join(details) + ')' if details else ''}")
        if not (v_ok and h_ok):
            failed_files.append(rel_path)

    print("-" * 50)
    if failed_files:
        print(f"RESULT: FAILED ({len(failed_files)} files out of sync)")
        sys.exit(1)
    else:
        print("RESULT: PASS (All normative files synchronized)")
        sys.exit(0)

if __name__ == "__main__":
    main()
