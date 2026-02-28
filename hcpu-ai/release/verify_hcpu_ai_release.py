import os
import sys
import yaml
import hashlib

def get_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def verify(spec_path, check_manifest):
    print(f"[*] Verifying HCPU-AI Release Integrity: {spec_path}")
    
    with open(spec_path, "r") as f:
        spec = yaml.safe_load(f)
    
    release_id = spec["release"]["id"]
    print(f"[*] Release ID: {release_id}")

    errors = 0
    
    # Check specs
    for fpath in spec["spec_files"]:
        expected = spec["sha256"].get(fpath)
        if not expected or expected == "<auto-fill>":
            print(f" [WARN] {fpath} not locked in YAML.")
            continue
        actual = get_sha256(fpath)
        if actual != expected:
            print(f" [FAIL] {fpath} hash mismatch!")
            print(f"   Expected: {expected}")
            print(f"   Actual:   {actual}")
            errors += 1
        else:
            print(f" [PASS] {fpath} verified.")

    if check_manifest:
        manifest_path = os.path.join("release", "MANIFEST.json")
        if not os.path.exists(manifest_path):
            print(f" [FAIL] Manifest missing: {manifest_path}")
            errors += 1
        else:
            print(f" [PASS] Manifest exists.")

    if errors > 0:
        print(f"\n[FAIL] Release integrity check FAILED with {errors} errors.")
        sys.exit(1)
    else:
        print(f"\n[PASS] Release integrity VERIFIED.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    verify(args.spec, args.check_manifest)
