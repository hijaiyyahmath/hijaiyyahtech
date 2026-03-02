from __future__ import annotations
import argparse, json, os
from pathlib import Path
from typing import Any, Dict, List

from hijaiyyahlang.hashutil import sha256_file
from hijaiyyahlang.spec import load_release_spec, ReleaseSpec
from hijaiyyahlang.normaliz_out import parse_metrics
from hijaiyyahlang.manifest import load_manifest, check_manifest_strict, check_manifest_minimal # Added check_manifest_minimal

def rpath(base: str, p: str) -> str:
    if os.path.isabs(p): return p
    # Use forward slashes for internal path consistency in manifest checks
    return os.path.normpath(os.path.join(base, p)).replace('\\', '/')

def check_file(path: str, expected: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"ok": False, "path": path, "expected": expected, "got": "MISSING"}
    got = sha256_file(path)
    return {"ok": got.lower()==expected.lower(), "path": path, "expected": expected, "got": got}

def check_manifest_sync(root: Path, spec: ReleaseSpec) -> Dict[str, Any]:
    m_path = root / "artifacts" / "MANIFEST.json"
    if not m_path.exists():
        return {"ok": False, "error": "MANIFEST.json missing"}
    
    try:
        with open(m_path, "r", encoding="utf-8") as f:
            m = json.load(f)
    except Exception as e:
        return {"ok": False, "error": str(e)}

    # Convert list of ArtifactSpec to list of dicts for the strict check
    art_dicts = [{"path": a.path.replace('\\', '/'), "sha256": a.sha256} for a in spec.artifacts]
    
    strict_ok, reason = check_manifest_strict(
        m, 
        spec.release_id, 
        spec.dimension, 
        spec.dataset_sha256, 
        art_dicts
    )

    return {"ok": strict_ok, "error": None if strict_ok else f"Manifest mismatch: {reason}"}

def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--check-manifest", action="store_true")
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args(argv)

    spec_path = os.path.abspath(args.spec)
    # The spec is in specs/HL18_release_integrity_local.yaml, so repo_root is one level up
    repo_root = os.path.dirname(os.path.dirname(spec_path))
    spec = load_release_spec(spec_path)
    base = os.path.normpath(os.path.join(repo_root, spec.release_root)).replace('\\', '/')

    results = []

    # dataset
    results.append(("dataset_18d", check_file(rpath(base, spec.dataset_path), spec.dataset_sha256)))

    # normaliz in/out
    results.append(("normaliz.input", check_file(rpath(base, spec.normaliz_in_path), spec.normaliz_in_sha256)))
    outp = rpath(base, spec.normaliz_out_path)
    results.append(("normaliz.output", check_file(outp, spec.normaliz_out_sha256)))

    # metrics parse
    metrics_ok = {"ok": False, "path": outp, "error": None, "found": None, "expected": spec.metrics_expected}
    if os.path.exists(outp):
        txt = open(outp, "r", encoding="utf-8", errors="replace").read()
        found = parse_metrics(txt)
        metrics_ok["found"] = found
        problems = []
        for k,v in spec.metrics_expected.items():
            if k not in found:
                problems.append({"metric": k, "expected": v, "got": None})
            elif found[k] != v:
                problems.append({"metric": k, "expected": v, "got": found[k]})
        if not problems:
            metrics_ok["ok"] = True
        else:
            metrics_ok["error"] = problems
    results.append(("normaliz.metrics", metrics_ok))

    # artifacts
    for i,a in enumerate(spec.artifacts):
        p = rpath(base, a.path)
        results.append((f"artifact[{i}].sha256", check_file(p, a.sha256)))
        if a.size_bytes is not None:
            if not os.path.exists(p):
                results.append((f"artifact[{i}].size", {"ok": False, "path": p, "error": "file_not_found"}))
            else:
                got = os.path.getsize(p)
                results.append((f"artifact[{i}].size", {"ok": got==a.size_bytes, "path": p, "expected": a.size_bytes, "got": got}))

    # optional manifest sync
    if args.check_manifest:
        sync_res = check_manifest_sync(Path(base), spec)
        results.append(("manifest.sync", sync_res))

    ok_all = all(x[1]["ok"] is True for x in results)

    report = {
        "spec": spec_path,
        "release_id": spec.release_id,
        "dimension": spec.dimension,
        "ok": ok_all,
        "results": [{"name": n, **d} for n,d in results],
    }

    if ok_all:
        print("PASS: HL release integrity verified.")
        rc = 0
    else:
        print("FAIL: HL release integrity check failed.")
        for n,d in results:
            if not d.get("ok", False):
                print(f"- {n}: {d}")
        rc = 1

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    return rc

if __name__ == "__main__":
    import sys
    sys.exit(main())
