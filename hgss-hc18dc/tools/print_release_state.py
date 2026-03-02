import subprocess
import sys
import os

RELEASE_TAG = "HGSS-HCVM-v1.HC18DC"

def run_cmd(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return (result.stdout + result.stderr).strip()
    except Exception as e:
        return f"ERROR: {e}"

def main():
    print("=" * 60)
    print(f"RELEASE STATE SUMMARY: {RELEASE_TAG}")
    print("=" * 60)
    
    print(f"\n[1] GIT TAG CHECK: {RELEASE_TAG}")
    # Note: On some systems it might be git show-ref --tags
    print(run_cmd(["git", "show-ref", "--tags", RELEASE_TAG]))
    
    print("\n[2] GIT HEAD COMMIT:")
    print(run_cmd(["git", "rev-parse", "HEAD"]))
    
    print("\n[3] RELEASE LOCK VERIFICATION (Documents):")
    # Use sys.executable to ensure we use the same python environment
    print(run_cmd([sys.executable, "tools/check_release_lock.py", "--strict-spec-scan"]))
    
    print("\n" + "=" * 60)
    print("END OF EVIDENCE REPORT")
    print("=" * 60)

if __name__ == "__main__":
    main()
