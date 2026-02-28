from __future__ import annotations
import json, hashlib
from pathlib import Path

from hisavm.master import load_master_csv

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1<<16), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_release_tree(release_dir: str):
    rd = Path(release_dir)
    manifest_path = rd / "MANIFEST.json"
    if not manifest_path.exists():
        raise SystemExit(f"MANIFEST_NOT_FOUND: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # sha256 check
    for ent in manifest["entries"]:
        fp = rd / ent["path"]
        if not fp.exists():
            raise SystemExit(f"MISSING_FILE:{ent['path']}")
        if fp.stat().st_size != ent["size"]:
            raise SystemExit(f"SIZE_MISMATCH:{ent['path']}")
        s = sha256_file(fp)
        if s != ent["sha256"]:
            raise SystemExit(f"SHA256_MISMATCH:{ent['path']}")

    # semantic check: load master and validate formulas
    master_csv = rd / "data" / "MH-28-v1.0-18D.csv"
    hij28 = rd / "data" / "HIJAIYYAH_28.txt"
    load_master_csv(master_csv, hij28, strict_formulas=True)

    return True

def verify_against_spec_yaml(spec_path: str, check_manifest: bool = True):
    try:
        import yaml  # type: ignore
    except Exception as e:
        raise SystemExit("MISSING_DEP: pyyaml required for --spec mode (pip install pyyaml)")

    spec = yaml.safe_load(Path(spec_path).read_text(encoding="utf-8"))

    # check locked files
    for ent in spec.get("normative_files", []):
        p = Path(ent["path"])
        # if running from hisa-vm root, paths in yaml might need prefix if they are relative to hisa-vm root
        # but the user defines them as data/ spec/ etc.
        if not p.exists():
            raise SystemExit(f"MISSING_FILE:{p.as_posix()}")
        got = sha256_file(p)
        want = ent["sha256"]
        if want.startswith("<"):
            raise SystemExit(f"SPEC_NOT_FINAL: sha256 not filled for {p.as_posix()}")
        if got != want:
            raise SystemExit(f"SHA256_MISMATCH:{p.as_posix()}")

    if check_manifest:
        base = Path(spec["release_tree"]["base_dir"])
        verify_release_tree(str(base))

    return True
