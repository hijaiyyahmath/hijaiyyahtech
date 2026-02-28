import sys
import os
import subprocess
from pathlib import Path

# Release Lock Constants
HGSS_VERSION_LOCK = "HGSS-HCVM-v1.HC18DC"
HGSS_COMMIT_LOCK = "e392c68"

def check_python_version():
    print(f"[*] Checking Python version...")
    if sys.version_info < (3, 10):
        print(f" [FAIL] Python 3.10+ required. Current: {sys.version}")
        return False
    print(f" [PASS] {sys.version.split()[0]}")
    return True

def check_required_folders():
    folders = [
        "hijaiyahlang-hl18",
        "hisa-vm",
        "hgss-hc18dc",
        "hijaiyyah-ai-hgss",
        "glyph"
    ]
    print(f"[*] Checking core modules...")
    missing = []
    for f in folders:
        if not os.path.isdir(f):
            missing.append(f)
    
    if missing:
        print(f" [FAIL] Missing modules: {', '.join(missing)}")
        return False
    print(f" [PASS] All core modules present.")
    return True

def check_hgss_lock():
    print(f"[*] Checking HGSS Normative Lock...")
    lock_tool = Path("hgss-hc18dc/tools/check_release_lock.py")
    if not lock_tool.exists():
        print(f" [FAIL] HGSS lock tool not found at {lock_tool}")
        return False
    
    try:
        # Run the internal HGSS lock check with its own root as CWD
        res = subprocess.run(
            [sys.executable, "tools/check_release_lock.py"], 
            cwd="hgss-hc18dc",
            capture_output=True, 
            text=True
        )
        if res.returncode == 0:
            print(f" [PASS] HGSS Lock Verified: {HGSS_VERSION_LOCK} @ {HGSS_COMMIT_LOCK}")
            return True
        else:
            print(f" [FAIL] HGSS Lock Mismatch or Error.")
            print(res.stdout)
            return False
    except Exception as e:
        print(f" [FAIL] Could not run HGSS lock check: {e}")
        return False

def check_root_data():
    files = ["MH-28-v1.0-18D.csv", "csgi/CSGI-28-v1.0.json"]
    print(f"[*] Checking root data (Bensin)...")
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        print(f" [FAIL] Missing root data files: {', '.join(missing)}")
        return False
    print(f" [PASS] Root data files present.")
    return True

def main():
    print("=== Hijaiyah-Codex Environment Check ===")
    success = True
    success &= check_python_version()
    success &= check_required_folders()
    success &= check_root_data()
    success &= check_hgss_lock()
    
    print("-" * 40)
    if success:
        print("RESULT: ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print("RESULT: ENVIRONMENT INCOMPLETE")
        sys.exit(1)

if __name__ == "__main__":
    main()
