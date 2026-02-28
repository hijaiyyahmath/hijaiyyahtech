from __future__ import annotations
import sys
import os

# Add src to sys.path to allow imports if running as script
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from hisavm.release.build_release import build_release

if __name__ == "__main__":
    out = build_release("release")
    print(f"Built release: {out}")
