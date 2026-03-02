from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict

from .spec import load_release_spec
from .dataset import load_mh28_csv, HL18Dataset
from .manifest import load_manifest, check_manifest_strict

@dataclass(frozen=True)
class Release:
    release_id: str
    dataset_path: Path
    dataset: HL18Dataset
    spec: Any

def load_release(release_dir: str | Path, release_id: str, check_manifest: bool = True) -> Release:
    rd = Path(release_id)
    # The spec is typically in <release_dir>/specs/HL18_release_integrity_local.yaml
    # But for a vendored release, it might be in <release_dir>/HL18_release_integrity.yaml
    # Let's check common locations.
    root = Path(release_dir)
    spec_path = root / "specs" / "HL18_release_integrity_local.yaml"
    if not spec_path.exists():
        spec_path = root / "HL18_release_integrity.yaml"
    
    if not spec_path.exists():
        raise FileNotFoundError(f"Release spec not found in {root}")

    spec = load_release_spec(str(spec_path))
    if spec.release_id != release_id:
        raise ValueError(f"Release ID mismatch: expected {release_id}, got {spec.release_id}")

    # Resolve dataset path relative to spec base
    base = spec_path.parent.parent if spec_path.parent.name == "specs" else spec_path.parent
    ds_path = base / spec.dataset_path
    
    if check_manifest:
        m_path = base / "artifacts" / "MANIFEST.json"
        if not m_path.exists():
             raise FileNotFoundError(f"MANIFEST.json missing in {base}/artifacts")
        m = load_manifest(str(m_path))
        art_dicts = [{"path": a.path.replace('\\', '/'), "sha256": a.sha256} for a in spec.artifacts]
        ok, reason = check_manifest_strict(
            m, 
            spec.release_id, 
            spec.dimension, 
            spec.dataset_sha256, 
            art_dicts
        )
        if not ok:
            raise ValueError(f"Manifest check failed: {reason}")

    ds = load_mh28_csv(str(ds_path))
    return Release(
        release_id=spec.release_id,
        dataset_path=ds_path,
        dataset=ds,
        spec=spec
    )
