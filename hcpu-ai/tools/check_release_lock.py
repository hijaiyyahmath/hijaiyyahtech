import os
import sys

RELEASE_ID = "HCPU-AI-v1.0+local.1"

FILES_TO_CHECK = [
    "spec/HCPU_AI_v1_0.md",
    "spec/HCPU_AI_MODES.md",
    "spec/HCPU_AI_TRAP_CONFORMANCE.md",
    "spec/HCPU_AI_RELEASE_LOCK.md",
    "src/hcpu_ai/constants.py",
]

def check():
    print(f"[*] Checking HCPU-AI Release Lock: {RELEASE_ID}")
    missing = 0
    for fpath in FILES_TO_CHECK:
        if not os.path.exists(fpath):
            print(f" [ERR] File not found: {fpath}")
            missing += 1
            continue
        
        with open(fpath, "r") as f:
            content = f.read()
            if RELEASE_ID not in content:
                print(f" [FAIL] Release ID mismatch in {fpath}")
                missing += 1
            else:
                print(f" [PASS] {fpath}")

    if missing > 0:
        print(f"\n[FAIL] Release lock check FAILED with {missing} issues.")
        sys.exit(1)
    else:
        print(f"\n[PASS] All files locked correctly.")

if __name__ == "__main__":
    check()
