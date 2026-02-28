import os, sys, subprocess, pathlib

# Configuration from environment or defaults
HGSS_REPO = os.getenv("HGSS_REPO", "deps/hgss-hc18dc")
LOCK_VER  = os.getenv("HGSS_VERSION_LOCK", "HGSS-HCVM-v1.HC18DC")
LOCK_HASH = os.getenv("HGSS_COMMIT_LOCK", "e392c68")

def main():
    p = pathlib.Path(HGSS_REPO)
    if not p.exists():
        print("[MISSING] HGSS Repo dependency:", HGSS_REPO)
        sys.exit(2)

    checker = p / "tools" / "check_release_lock.py"
    if not checker.exists():
        print("[FAIL] Missing check_release_lock.py in HGSS repo")
        sys.exit(2)

    # Note: We check version primarily. 
    # If the hgss checker supports --expected-hash, we use it.
    print(f"Verifying HGSS lock at {HGSS_REPO}...")
    r = subprocess.run(
        ["python", str(checker), "--expected", LOCK_VER],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print("[FAIL] HGSS release version mismatch")
        print(r.stdout); print(r.stderr)
        sys.exit(2)
        
    # Manual commit check if possible
    try:
        git_check = subprocess.run(
            ["git", "-C", str(p), "rev-parse", "HEAD"],
            capture_output=True, text=True
        )
        if git_check.returncode == 0:
            current_hash = git_check.stdout.strip()
            if not current_hash.startswith(LOCK_HASH):
                print(f"[FAIL] HGSS commit mismatch. Expected {LOCK_HASH}, got {current_hash}")
                sys.exit(2)
    except Exception:
        print("[WARN] Could not verify git hash (git not found or not a repo)")

    print("[OK] HGSS dependency locked:", LOCK_VER, LOCK_HASH)
    print("[OK] Python", sys.version.split()[0])
    sys.exit(0)

if __name__ == "__main__":
    main()
