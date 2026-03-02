#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
from pathlib import Path
from typing import Dict, Iterable, Tuple

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", "node_modules", "dist", ".next"}
EXCLUDE_FILES = {".DS_Store"}

REQUIRED_ARTIFACTS = [
    "release/HL-18-v1.0+local.1/artifacts/MANIFEST.json",
    "release/HL-18-v1.0+local.1/artifacts/HB18.json",
    "release/HL-18-v1.0+local.1/artifacts/HYP18.json",
    "release/HL-18-v1.0+local.1/artifacts/EQ18.json",
    "release/HL-18-v1.0+local.1/artifacts/CONG18.json",
    "release/HL-18-v1.0+local.1/artifacts/LATTICE18.json",
    "release/HL-18-v1.0+local.1/MH-28-v1.0-18D.csv",
    "release/CSGI-28-v1.0.json",
]

def require_files(bundle_dir: Path, rel_paths: list[str]) -> None:
    missing = []
    for rp in rel_paths:
        p = bundle_dir / rp
        if not p.exists():
            missing.append(rp)
    if missing:
        raise SystemExit(
            "FAIL: bundle missing required HL-18 release artifacts:\n- " + "\n- ".join(missing)
        )

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def iter_files(bundle_dir: Path) -> Iterable[Path]:
    for p in sorted(bundle_dir.rglob("*")):
        if p.is_dir():
            continue
        rel_parts = p.relative_to(bundle_dir).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        if p.name in EXCLUDE_FILES:
            continue
        yield p

def build_manifest(bundle_dir: Path, bundle_id: str) -> Dict[str, str]:
    """
    Returns mapping relpath -> sha256 for all files except MANIFEST.json and SHA256SUMS.txt
    (to avoid self-referential hashing).
    """
    files: Dict[str, str] = {}
    for p in iter_files(bundle_dir):
        rel = p.relative_to(bundle_dir).as_posix()
        if rel in ("MANIFEST.json", "SHA256SUMS.txt"):
            continue
        files[rel] = sha256_file(p)
    return files

def write_manifest(bundle_dir: Path, bundle_id: str, files: Dict[str, str]) -> Path:
    out = {
        "bundle_id": bundle_id,
        "hash": "sha256",
        "files": files,
    }
    manifest_path = bundle_dir / "MANIFEST.json"
    manifest_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest_path

def write_sha256sums(bundle_dir: Path, files: Dict[str, str], manifest_path: Path) -> Path:
    """
    Writes AuditorBundle/SHA256SUMS.txt listing:
      <sha256>  <relpath>
    Includes MANIFEST.json at the end (hashed after it is written).
    """
    lines = []
    for rel in sorted(files.keys()):
        lines.append(f"{files[rel]}  {rel}")
    man_sha = sha256_file(manifest_path)
    lines.append(f"{man_sha}  MANIFEST.json")
    out_path = bundle_dir / "SHA256SUMS.txt"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path

def tar_reproducible(bundle_dir: Path, out_tar: Path) -> None:
    """
    Creates reproducible tar.gz:
      - sorted file order
      - mtime=0
      - uid/gid=0
      - uname/gname empty
    """
    out_tar.parent.mkdir(parents=True, exist_ok=True)

    def filter_tarinfo(ti: tarfile.TarInfo) -> tarfile.TarInfo:
        ti.uid = 0
        ti.gid = 0
        ti.uname = ""
        ti.gname = ""
        ti.mtime = 0
        # executable perms for scripts/audit.sh
        if ti.name.endswith("scripts/audit.sh"):
            ti.mode = 0o755
        else:
            ti.mode = 0o644
        return ti

    with tarfile.open(out_tar, "w:gz") as tf:
        # Important: add folder as "AuditorBundle/..." inside tar
        base_name = bundle_dir.name
        # Sort files for reproducibility
        all_files = sorted(list(iter_files(bundle_dir)))
        for p in all_files:
            rel = p.relative_to(bundle_dir).as_posix()
            arcname = f"{base_name}/{rel}"
            tf.add(p, arcname=arcname, recursive=False, filter=filter_tarinfo)

def write_tarball_sha256(dist_dir: Path, tar_path: Path) -> Path:
    """
    Writes dist/SHA256SUMS.txt for the tarball only (for pre-extract verification).
    """
    dist_dir.mkdir(parents=True, exist_ok=True)
    s = sha256_file(tar_path)
    out = dist_dir / "SHA256SUMS.txt"
    out.write_text(f"{s}  {tar_path.name}\n", encoding="utf-8")
    return out

def main() -> None:
    ap = argparse.ArgumentParser(description="Build AuditorBundle MANIFEST + SHA256SUMS + reproducible tar.gz")
    ap.add_argument("--bundle-dir", default="AuditorBundle", help="Path to AuditorBundle directory")
    ap.add_argument("--bundle-id", required=True, help="Bundle ID string (written into MANIFEST.json)")
    ap.add_argument("--dist-dir", default="dist", help="Output directory for tar.gz and tarball SHA256SUMS.txt")
    ap.add_argument("--tar-name", default=None, help="Optional tar.gz filename; default uses bundle-id")
    args = ap.parse_args()

    bundle_dir = Path(args.bundle_dir).resolve()
    if not bundle_dir.exists():
        raise SystemExit(f"bundle-dir not found: {bundle_dir}")

    dist_dir = Path(args.dist_dir).resolve()
    tar_name = args.tar_name or f"{args.bundle_id}.tar.gz"
    out_tar = dist_dir / tar_name

    # 0) Hardening: check required artifacts
    require_files(bundle_dir, REQUIRED_ARTIFACTS)

    # 1) MANIFEST.json + SHA256SUMS.txt inside bundle
    files = build_manifest(bundle_dir, args.bundle_id)
    manifest_path = write_manifest(bundle_dir, args.bundle_id, files)
    sha_path = write_sha256sums(bundle_dir, files, manifest_path)

    # 2) Build tar.gz (reproducible)
    tar_reproducible(bundle_dir, out_tar)

    # 3) dist/SHA256SUMS.txt for tarball
    tar_sha_path = write_tarball_sha256(dist_dir, out_tar)

    print("OK")
    print("bundle_dir:", bundle_dir)
    print("wrote:", manifest_path)
    print("wrote:", sha_path)
    print("built:", out_tar)
    print("wrote:", tar_sha_path)

if __name__ == "__main__":
    main()
