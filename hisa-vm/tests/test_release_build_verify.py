from pathlib import Path
from hisavm.release.build_release import build_release
from hisavm.release.verify_release import verify_release_tree
import shutil
import os

def test_release_build_and_verify(tmp_path):
    # Fix: Run build and verify in a temporary directory
    # We need to ensure we can find the spec and data dirs
    # For simplicity, we symlink/copy them to the tmp_path or just run from project root
    
    root = Path(__file__).resolve().parents[1]
    
    # We must be in project root for build_release to find spec/ and data/ correctly
    # So we change CWD temporarily
    old_cwd = os.getcwd()
    os.chdir(root)
    try:
        out_root = tmp_path / "release"
        out_dir = build_release(out_root=str(out_root))
        assert (out_dir / "MANIFEST.json").exists()
        verify_release_tree(str(out_dir))
    finally:
        os.chdir(old_cwd)
