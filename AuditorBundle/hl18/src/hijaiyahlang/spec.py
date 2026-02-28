from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import yaml

@dataclass(frozen=True)
class ArtifactSpec:
    path: str
    sha256: str
    size_bytes: Optional[int] = None

@dataclass(frozen=True)
class ReleaseSpec:
    release_id: str
    dimension: int
    dataset_path: str
    dataset_sha256: str
    normaliz_in_path: str
    normaliz_in_sha256: str
    normaliz_out_path: str
    normaliz_out_sha256: str
    metrics_expected: Dict[str, Any]
    artifacts: List[ArtifactSpec]
    release_root: str = "."

def _get_dataset(spec: Dict[str, Any]) -> tuple[str, str]:
    if isinstance(spec.get("dataset_18d"), dict):
        d = spec["dataset_18d"]
        return d["path"], d["sha256"]
    ds = spec.get("dataset")
    if isinstance(ds, dict):
        for _, v in ds.items():
            if isinstance(v, dict) and "path" in v and "sha256" in v:
                return v["path"], v["sha256"]
    raise ValueError("Spec: dataset node not found")

def load_release_spec(path: str) -> ReleaseSpec:
    with open(path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    if not isinstance(spec, dict):
        raise ValueError("Spec YAML must be a mapping")

    release_root = "."
    if isinstance(spec.get("paths"), dict) and isinstance(spec["paths"].get("release_root"), str):
        release_root = spec["paths"]["release_root"]

    ds_path, ds_sha = _get_dataset(spec)
    nz = spec["normaliz"]
    met = nz["metrics_expected"]

    artifacts: List[ArtifactSpec] = []
    for a in spec["artifacts"]:
        size = a.get("size_bytes", a.get("optional_size_bytes"))
        artifacts.append(
            ArtifactSpec(
                path=a["path"],
                sha256=a["sha256"],
                size_bytes=int(size) if size is not None else None,
            )
        )

    return ReleaseSpec(
        release_id=str(spec["release_id"]),
        dimension=int(spec["dimension"]),
        dataset_path=ds_path,
        dataset_sha256=str(ds_sha),
        normaliz_in_path=str(nz["input"]["path"]),
        normaliz_in_sha256=str(nz["input"]["sha256"]),
        normaliz_out_path=str(nz["output"]["path"]),
        normaliz_out_sha256=str(nz["output"]["sha256"]),
        metrics_expected=dict(met),
        artifacts=artifacts,
        release_root=release_root,
    )
