from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path

from hisavm.constants import RELEASE_ID
from hisavm.release.verify_release import verify_release_tree, verify_against_spec_yaml

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release-dir", default=f"release/{RELEASE_ID}")
    ap.add_argument("--spec", default=None, help="path to specs/HISA_release_integrity_local.yaml")
    ap.add_argument("--check-manifest", action="store_true", help="verify MANIFEST.json and semantic checks")
    args = ap.parse_args()

    if args.spec:
        # ensure we can find the spec file accurately
        spec_path = args.spec
        if not os.path.exists(spec_path) and os.path.exists(os.path.join("..", spec_path)):
            spec_path = os.path.join("..", spec_path)
            
        verify_against_spec_yaml(spec_path, check_manifest=args.check_manifest)
        print("PASS")
        return

    # fallback: verify only release tree manifest + semantic checks
    rel_dir = args.release_dir
    if not os.path.exists(rel_dir) and os.path.exists(os.path.join("..", rel_dir)):
         rel_dir = os.path.join("..", rel_dir)

    verify_release_tree(rel_dir)
    print("PASS")

if __name__ == "__main__":
    main()
