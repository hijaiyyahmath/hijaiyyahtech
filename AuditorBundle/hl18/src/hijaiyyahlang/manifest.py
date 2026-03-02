from __future__ import annotations
import json
from typing import Any, Dict, List, Tuple

def load_manifest(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def check_manifest_minimal(man: Dict[str, Any], *, release_id: str, dimension: int, dataset_sha256: str, metrics_expected: Dict[str, Any]) -> List[Dict[str, Any]]:
    problems: List[Dict[str, Any]] = []

    def get_any(keys):
        for k in keys:
            if k in man:
                return man[k]
        return None

    got_release = get_any(["hl_release_id","release_id","id"])
    if got_release is not None and str(got_release) != str(release_id):
        problems.append({"field":"release_id","expected":release_id,"got":got_release})

    got_dim = get_any(["dimension","dim"])
    if got_dim is not None and int(got_dim) != int(dimension):
        problems.append({"field":"dimension","expected":dimension,"got":got_dim})

    got_ds = get_any(["dataset_18d_sha256","dataset_sha256","datasetHash"])
    if got_ds is not None and str(got_ds).lower() != str(dataset_sha256).lower():
        problems.append({"field":"dataset_18d_sha256","expected":dataset_sha256,"got":got_ds})

    got_metrics = get_any(["metrics","normaliz_metrics","normaliz"])
    if isinstance(got_metrics, dict):
        for k,vexp in metrics_expected.items():
            if k in got_metrics and got_metrics[k] != vexp:
                problems.append({"field":f"metrics.{k}","expected":vexp,"got":got_metrics[k]})

    return problems

def check_manifest_strict(manifest: Dict[str, Any], release_id: str, dimension: int, dataset_sha: str, artifacts: List[Dict[str, Any]]) -> Tuple[bool, str | None]:
    """Perform a strict, audit-grade verification of the manifest against expected values."""
    if manifest.get("hl_release_id") != release_id: 
        return False, f"release_id mismatch: {manifest.get('hl_release_id')} != {release_id}"
    if manifest.get("dimension") != dimension: 
        return False, "dimension mismatch"
    # Use case-insensitive comparison for SHA
    m_ds = str(manifest.get("dataset_18d_sha256") or manifest.get("dataset_sha256") or "")
    if m_ds.lower() != str(dataset_sha).lower(): 
        return False, f"dataset_sha mismatch: {m_ds} != {dataset_sha}"
    
    m_artifacts = manifest.get("artifacts", {})
    for art in artifacts:
        path = art["path"]
        # Skip self-reference check for MANIFEST.json in strict mode to avoid circular hash dependency
        if path.lower().endswith("manifest.json"):
            continue
            
        expected_sha = art["sha256"]
        if str(m_artifacts.get(path)).lower() != str(expected_sha).lower():
            return False, f"artifact mismatch: {path}"
            
    return True, None
