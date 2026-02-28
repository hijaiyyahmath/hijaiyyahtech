import sys
import argparse
from pathlib import Path

# Files that should contain the release ID
FILES_TO_CHECK = [
    "src/hisavm/constants.py",
    "spec/HISA_v1_0.md",
    "spec/HISA_ISA_TABLE.md",
    "spec/HISA_BYTECODE_ENCODING.md",
    "spec/HISA_TRAP_CONFORMANCE.md",
    "specs/HISA_release_integrity_local.yaml",
    "RELEASE_SYNC_TABLE.md",
]

def check_lock(expected_id: str):
    failed = []
    root = Path(__file__).resolve().parents[1]
    
    print(f"Checking HISA-VM Release Lock: {expected_id}")
    
    for rel_path in FILES_TO_CHECK:
        p = root / rel_path
        if not p.exists():
            print(f"[MISSING] {rel_path}")
            failed.append(rel_path)
            continue
            
        content = p.read_text(encoding="utf-8")
        if expected_id in content:
            print(f"[OK]      {rel_path}")
        else:
            print(f"[FAIL]    {rel_path} (Release ID not found)")
            failed.append(rel_path)
            
    if failed:
        print(f"\nERROR: Release lock failed for {len(failed)} files.")
        sys.exit(1)
    else:
        print("\nSUCCESS: All files are synchronized to release ID.")
        sys.exit(0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expected", required=True, help="Expected Release ID (e.g. HISA-VM-v1.0+local.1)")
    args = ap.parse_args()
    
    check_lock(args.expected)

if __name__ == "__main__":
    main()
