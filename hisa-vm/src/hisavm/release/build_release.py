from __future__ import annotations

import json, os, shutil, hashlib
from pathlib import Path

# Fix: Use local imports for release build script
from hisavm.constants import RELEASE_ID, MASTER_CSV_PATH_DEFAULT, HIJAIYYAH_28_PATH_DEFAULT
from hisavm.asm import assemble_text
from hisavm.bytecode import save_bin

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1<<16), b""):
            h.update(chunk)
    return h.hexdigest()

def build_release(out_root: str = "release"):
    out_dir = Path(out_root) / RELEASE_ID
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "data").mkdir(parents=True)
    (out_dir / "spec").mkdir(parents=True)
    (out_dir / "bytecode").mkdir(parents=True)

    # Copy spec snapshots
    for p in Path("spec").glob("*.md"):
        shutil.copy2(p, out_dir / "spec" / p.name)

    # Copy data inputs
    shutil.copy2(MASTER_CSV_PATH_DEFAULT, out_dir / "data" / Path(MASTER_CSV_PATH_DEFAULT).name)
    shutil.copy2(HIJAIYYAH_28_PATH_DEFAULT, out_dir / "data" / Path(HIJAIYYAH_28_PATH_DEFAULT).name)

    # Build example bytecode
    asm_text = Path("examples/audit_jim.hisaasm").read_text(encoding="utf-8")
    b = assemble_text(asm_text)
    save_bin(str(out_dir / "bytecode" / "audit_jim.bin"), b)

    # Manifest
    entries = []
    # Walk the directory to include all files in manifest
    for fp in sorted(out_dir.rglob("*")):
        if fp.is_file() and fp.name != "MANIFEST.json":
            rel = fp.relative_to(out_dir).as_posix()
            entries.append({
                "path": rel,
                "size": fp.stat().st_size,
                "sha256": sha256_file(fp),
            })
    manifest = {
        "release_id": RELEASE_ID,
        "entries": entries,
    }
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out_dir

if __name__ == "__main__":
    build_release()
