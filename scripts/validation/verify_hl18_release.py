#!/usr/bin/env python3
# verify_hl18_release.py
#
# Verifier rilis HL-18-v1.0:
# - cek SHA-256 semua file yang disebut di spec YAML
# - cek size HB18.bin (bila ada size_bytes)
# - parse MH_18x28.out (Normaliz output) dan cocokkan metrics_expected
# - (opsional) cek MANIFEST.json sinkron dengan spec
#
# Usage:
#   python verify_hl18_release.py --spec HL18_release_integrity.yaml
#   python verify_hl18_release.py --spec HL18_release_integrity.yaml --check-manifest
#   python verify_hl18_release.py --spec HL18_release_integrity.yaml --json out.json
#
# Dependency:
#   pip install pyyaml

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import unicodedata

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


# ----------------------------
# Utilities
# ----------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_text(path: str, encoding: str = "utf-8") -> str:
    with open(path, "r", encoding=encoding, errors="replace") as f:
        return f.read()

def norm_bool(v: Any) -> Optional[bool]:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "yes", "1"):
            return True
        if s in ("false", "no", "0"):
            return False
    return None

def die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)

def resolve_path(base_dir: str, p: str) -> str:
    # Keep absolute as-is; relative resolved from spec dir.
    if os.path.isabs(p):
        return p
    return os.path.normpath(os.path.join(base_dir, p))

@dataclass
class CheckResult:
    ok: bool
    name: str
    details: Dict[str, Any]

def ok(name: str, **details: Any) -> CheckResult:
    return CheckResult(True, name, details)

def fail(name: str, **details: Any) -> CheckResult:
    return CheckResult(False, name, details)


# ----------------------------
# CSGI Validation
# ----------------------------

HIJAIYYAH_SET = set("ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن و ه ي".split())

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

TATWEEL = "\u0640"

def letter_id(s: str) -> str:
    """
    Normative letter identity for audit:
    letter_id(s) = NFC(s) then remove all ARABIC TATWEEL (U+0640).
    Example: "هـ" -> "ه"
    """
    s = nfc(s)
    s = s.replace(TATWEEL, "")
    return s

def load_json_no_dups_nfc_keys(path: str) -> Any:
    # Strict JSON: reject duplicate keys and reject NFC key collisions.
    def hook(pairs):
        obj = {}
        for k, v in pairs:
            if not isinstance(k, str):
                raise ValueError("NON_STRING_KEY")
            k2 = nfc(k)
            if k2 in obj:
                raise ValueError(f"DUPLICATE_KEY_OR_NFC_COLLISION: {k!r} -> {k2!r}")
            obj[k2] = v
        return obj
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=hook)

def is_8_neighbor(p: List[int], q: List[int]) -> bool:
    dx = abs(p[0] - q[0]); dy = abs(p[1] - q[1])
    return (dx <= 1 and dy <= 1) and not (dx == 0 and dy == 0)

def validate_csgi_dataset(csgi_path: str) -> None:
    root = load_json_no_dups_nfc_keys(csgi_path)
    if not isinstance(root, dict):
        raise ValueError("CSGI root must be JSON object/dict")

    letters = root.get("letters")
    if not isinstance(letters, list):
        raise ValueError("CSGI dataset must contain 'letters' array")

    ver = root.get("csgi_dataset_version") or root.get("csgi_version")
    if ver != "CSGI-DATASET-1.0":
        raise ValueError(f"Invalid CSGI dataset version: {ver!r}")

    seen: List[str] = []
    for idx, entry in enumerate(letters):
        if not isinstance(entry, dict):
            raise ValueError(f"letters[{idx}] must be JSON object")

        for k in ("csgi_version", "letter", "embedding", "nodes", "edges", "meta"):
            if k not in entry:
                raise ValueError(f"letters[{idx}] missing field: {k}")

        # 4) lock entry csgi_version
        if entry.get("csgi_version") != "CSGI-1.0":
            raise ValueError(f"letters[{idx}].csgi_version must be 'CSGI-1.0'; got {entry.get('csgi_version')!r}")

        letter_raw = entry["letter"]
        if not isinstance(letter_raw, str):
            raise ValueError(f"letters[{idx}].letter must be string")

        lid = letter_id(letter_raw)
        if len(lid) != 1:
            raise ValueError(
                f"letters[{idx}].letter_id must be 1 char; got {lid!r} from {letter_raw!r}"
            )
        if lid not in HIJAIYYAH_SET:
            raise ValueError(
                f"letters[{idx}].letter_id not in HIJAIYYAH_SET; got {lid!r} from {letter_raw!r}"
            )
        seen.append(lid)

        meta = entry["meta"]
        if not isinstance(meta, dict) or meta.get("adjacency") != "8-neighborhood":
            raise ValueError(f"letters[{idx}].meta.adjacency must be '8-neighborhood'")

        nodes = entry["nodes"]
        edges = entry["edges"]
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError(f"letters[{idx}].nodes and .edges must be arrays")

        # 1) node x/y int + collect coords (+ optional degree)
        node_ids = set()
        node_xy: Dict[int, Tuple[int, int]] = {}
        node_deg: Dict[int, Optional[int]] = {}
        for ni, n_ in enumerate(nodes):
            if not isinstance(n_, dict) or not isinstance(n_.get("id"), int):
                raise ValueError(f"letters[{idx}].nodes[{ni}] contains invalid node record (missing int id)")
            nid = n_["id"]
            if nid in node_ids:
                raise ValueError(f"letters[{idx}] duplicate node id: {nid}")
            x = n_.get("x"); y = n_.get("y")
            if not (isinstance(x, int) and isinstance(y, int)):
                raise ValueError(f"letters[{idx}].nodes[{ni}] x/y must be int; got x={x!r} y={y!r}")
            d = n_.get("degree")
            if d is not None and not isinstance(d, int):
                raise ValueError(f"letters[{idx}].nodes[{ni}].degree must be int if present; got {d!r}")
            node_ids.add(nid)
            node_xy[nid] = (x, y)
            node_deg[nid] = d

        # 3) compute degree from node-to-node adjacency (unique neighbors)
        adj: Dict[int, set] = {nid: set() for nid in node_ids}

        for e_ in edges:
            if not isinstance(e_, dict):
                raise ValueError(f"letters[{idx}].edges contains invalid edge record")
            u = e_.get("u"); v = e_.get("v")
            if u not in node_ids or v not in node_ids:
                raise ValueError(f"letters[{idx}] edge endpoints u/v must reference existing node ids")
            pts = e_.get("points")
            if not isinstance(pts, list) or len(pts) < 2:
                raise ValueError(f"letters[{idx}] edge.points must be array length >= 2")

            # 2) edge endpoints must match node coords
            if pts[0] != [node_xy[u][0], node_xy[u][1]]:
                raise ValueError(f"letters[{idx}] edge endpoint mismatch: points[0]={pts[0]} != node(u)={node_xy[u]} (u={u})")
            if pts[-1] != [node_xy[v][0], node_xy[v][1]]:
                raise ValueError(f"letters[{idx}] edge endpoint mismatch: points[-1]={pts[-1]} != node(v)={node_xy[v]} (v={v})")

            adj[u].add(v); adj[v].add(u)

            prev = None
            for pi, p in enumerate(pts):
                if (not isinstance(p, list)) or len(p) != 2 or not all(isinstance(z, int) for z in p):
                    raise ValueError(f"letters[{idx}] points[{pi}] must be [int,int]")
                if prev is not None and not is_8_neighbor(prev, p):
                    raise ValueError(f"letters[{idx}] violates 8-neighborhood at points[{pi-1}] -> points[{pi}]")
                prev = p

        # 3) degree consistency check (only if node.degree present)
        for nid in node_ids:
            got_deg = len(adj[nid])
            exp_deg = node_deg.get(nid)
            if exp_deg is not None and exp_deg != got_deg:
                raise ValueError(f"letters[{idx}] degree mismatch for node id={nid}: expected={exp_deg} got={got_deg}")

        # 5) Specific Audit Claims matching (Parallel Verify)
        audit = meta.get("audit")
        if isinstance(audit, dict):
            # Theta-Hat claim for Waw
            if lid == "و":
                theta = audit.get("theta_hat")
                if theta is not None and theta != 5:
                    raise ValueError(f"Waw audit claim mismatch: theta_hat expected 5; got {theta}")

            # Loop claim for Fa/Waw
            if lid in ("ف", "و") and audit.get("topology") == "loop_not_closed":
                # A simple check: if it's 'not closed' (in the sense of being a pure cycle),
                # it must have at least one junction (degree > 2) involved in its edges.
                has_junction = any(node_deg.get(nid, 0) > 2 for nid in node_ids)
                if not has_junction:
                    raise ValueError(f"{lid} topological claim mismatch: 'loop_not_closed' but no junctions found")

    if len(seen) != 28:
        raise ValueError(f"CSGI letters count must be 28; got {len(seen)}")
    if set(seen) != HIJAIYYAH_SET:
        missing = HIJAIYYAH_SET - set(seen)
        extra = set(seen) - HIJAIYYAH_SET
        raise ValueError(f"CSGI letter set mismatch: missing={missing} extra={extra}")


# ----------------------------
# Spec loading (supports two shapes)
# ----------------------------

def load_spec(spec_path: str) -> Dict[str, Any]:
    if yaml is None:
        die("PyYAML tidak tersedia. Install: pip install pyyaml")
    data = yaml.safe_load(read_text(spec_path))
    if not isinstance(data, dict):
        die("Spec YAML harus berupa mapping/dict.")
    return data

def get_release_root(spec: Dict[str, Any]) -> str:
    # optional: paths.release_root
    paths = spec.get("paths") or {}
    if isinstance(paths, dict) and isinstance(paths.get("release_root"), str):
        return paths["release_root"]
    return "."

def get_dataset_node(spec: Dict[str, Any]) -> Tuple[str, str]:
    # supports:
    # dataset_18d: {path, sha256}
    # OR dataset: { mh_28_v1_0_18d_csv: {path, sha256} }
    if isinstance(spec.get("dataset_18d"), dict):
        n = spec["dataset_18d"]
        return n["path"], n["sha256"]

    ds = spec.get("dataset")
    if isinstance(ds, dict) and ds:
        # take first child mapping that contains path/sha256
        for _, v in ds.items():
            if isinstance(v, dict) and "path" in v and "sha256" in v:
                return v["path"], v["sha256"]

    die("Tidak menemukan dataset node. Pakai 'dataset_18d' atau 'dataset: {name:{path,sha256}}'")

def get_normaliz_nodes(spec: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    nz = spec.get("normaliz")
    if not isinstance(nz, dict):
        die("Spec harus punya node 'normaliz'.")
    inp = nz.get("input")
    out = nz.get("output")
    met = nz.get("metrics_expected")
    if not isinstance(inp, dict) or not isinstance(out, dict) or not isinstance(met, dict):
        die("normaliz.input, normaliz.output, normaliz.metrics_expected harus dict.")
    return inp, out, met


# ----------------------------
# Normaliz .out parsing
# ----------------------------

_METRIC_PATTERNS: Dict[str, List[re.Pattern]] = {
    # integers
    "hilbert_basis_size": [
        re.compile(r"Hilbert\s*basis\s*(size|elements)?\s*[:=]\s*(\d+)", re.I),
        re.compile(r"Hilbert\s*basis\s*elements\s*[:=]\s*(\d+)", re.I),
        re.compile(r"HilbertBasis\s*[:=]\s*(\d+)", re.I),
    ],
    "extreme_rays": [
        re.compile(r"Extreme\s*rays?\s*[:=]\s*(\d+)", re.I),
        re.compile(r"Nr\.\s*Extreme\s*Rays?\s*[:=]\s*(\d+)", re.I),
    ],
    "support_hyperplanes": [
        re.compile(r"Support\s*hyperplanes?\s*[:=]\s*(\d+)", re.I),
        re.compile(r"Nr\.\s*Support\s*Hyperplanes?\s*[:=]\s*(\d+)", re.I),
    ],
    "rank": [
        re.compile(r"\bRank\b\s*[:=]\s*(\d+)", re.I),
    ],
    "external_index": [
        re.compile(r"External\s*index\s*[:=]\s*(\d+)", re.I),
    ],
    "internal_index": [
        re.compile(r"Internal\s*index\s*[:=]\s*(\d+)", re.I),
    ],
    "equations": [
        re.compile(r"Equations?\s*[:=]\s*(\d+)", re.I),
        re.compile(r"Nr\.\s*Equations?\s*[:=]\s*(\d+)", re.I),
    ],
    # boolean
    "integrally_closed": [
        re.compile(r"Integrally\s*closed\s*[:=]\s*(true|false)", re.I),
        re.compile(r"\bintegrally_closed\b\s*[:=]\s*(true|false)", re.I),
    ],
}

def parse_normaliz_out_metrics(out_text: str, expected_keys: List[str]) -> Dict[str, Any]:
    found: Dict[str, Any] = {}
    for k in expected_keys:
        pats = _METRIC_PATTERNS.get(k, [])
        val: Optional[Any] = None
        for pat in pats:
            m = pat.search(out_text)
            if not m:
                continue
            # last capture group typically contains the numeric/bool value
            g = m.groups()[-1]
            if k == "integrally_closed":
                b = norm_bool(g)
                val = b if b is not None else g
            else:
                try:
                    val = int(g)
                except Exception:
                    val = g
            break
        if val is not None:
            found[k] = val
    return found


# ----------------------------
# MANIFEST.json check (optional)
# ----------------------------

def check_manifest_sync(manifest_path: str, spec: Dict[str, Any], base_dir: str) -> CheckResult:
    mp = resolve_path(base_dir, manifest_path)
    if not os.path.exists(mp):
        return fail("manifest.exists", path=mp, error="file_not_found")

    try:
        m = json.loads(read_text(mp))
    except Exception as e:
        return fail("manifest.parse", path=mp, error=str(e))

    # Minimal expectations (best-effort):
    # - release id
    # - dimension
    # - dataset sha256
    # - normaliz metrics (if present)
    exp_release = spec.get("release_id")
    exp_dim = spec.get("dimension")
    ds_path, ds_sha = get_dataset_node(spec)
    _, _, met_exp = get_normaliz_nodes(spec)

    problems: List[Dict[str, Any]] = []

    def get_any(d: Dict[str, Any], keys: List[str]) -> Optional[Any]:
        for kk in keys:
            if kk in d:
                return d[kk]
        return None

    # release id
    rel = get_any(m, ["hl_release_id", "release_id", "id"])
    if exp_release is not None and rel is not None and str(rel) != str(exp_release):
        problems.append({"field": "release_id", "expected": exp_release, "got": rel})

    # dimension
    dim = get_any(m, ["dimension", "dim"])
    if exp_dim is not None and dim is not None and int(dim) != int(exp_dim):
        problems.append({"field": "dimension", "expected": exp_dim, "got": dim})

    # dataset sha
    ds_m = get_any(m, ["dataset_18d_sha256", "dataset_sha256", "datasetHash"])
    if ds_m is not None and str(ds_m).lower() != str(ds_sha).lower():
        problems.append({"field": "dataset_18d_sha256", "expected": ds_sha, "got": ds_m})

    # metrics
    metrics_m = get_any(m, ["metrics", "normaliz_metrics", "normaliz"])
    if isinstance(metrics_m, dict):
        # compare only keys in metrics_expected
        for k, vexp in met_exp.items():
            if k not in metrics_m:
                continue
            vgot = metrics_m[k]
            if isinstance(vexp, bool):
                if norm_bool(vgot) != vexp:
                    problems.append({"field": f"metrics.{k}", "expected": vexp, "got": vgot})
            else:
                try:
                    if int(vgot) != int(vexp):
                        problems.append({"field": f"metrics.{k}", "expected": vexp, "got": vgot})
                except Exception:
                    if vgot != vexp:
                        problems.append({"field": f"metrics.{k}", "expected": vexp, "got": vgot})

    if problems:
        return fail("manifest.sync", path=mp, problems=problems)

    return ok("manifest.sync", path=mp, note="minimal fields matched (best-effort)")


# ----------------------------
# Main verification steps
# ----------------------------

def check_sha(name: str, path: str, expected_sha: str) -> CheckResult:
    if not os.path.exists(path):
        return fail(name, path=path, error="file_not_found")
    got = sha256_file(path)
    if got.lower() != expected_sha.lower():
        return fail(name, path=path, expected_sha256=expected_sha, got_sha256=got)
    return ok(name, path=path, sha256=got)

def check_size(name: str, path: str, expected_size: int) -> CheckResult:
    if not os.path.exists(path):
        return fail(name, path=path, error="file_not_found")
    got = os.path.getsize(path)
    if got != expected_size:
        return fail(name, path=path, expected_size_bytes=expected_size, got_size_bytes=got)
    return ok(name, path=path, size_bytes=got)

def verify_normaliz_metrics(out_path: str, metrics_expected: Dict[str, Any]) -> CheckResult:
    if not os.path.exists(out_path):
        return fail("normaliz.metrics", path=out_path, error="file_not_found")
    txt = read_text(out_path)
    keys = list(metrics_expected.keys())
    found = parse_normaliz_out_metrics(txt, keys)

    problems = []
    for k, vexp in metrics_expected.items():
        if k not in found:
            problems.append({"metric": k, "expected": vexp, "got": None, "error": "not_found_in_out"})
            continue
        vgot = found[k]
        if isinstance(vexp, bool):
            if norm_bool(vgot) != vexp:
                problems.append({"metric": k, "expected": vexp, "got": vgot})
        else:
            try:
                if int(vgot) != int(vexp):
                    problems.append({"metric": k, "expected": vexp, "got": vgot})
            except Exception:
                if vgot != vexp:
                    problems.append({"metric": k, "expected": vexp, "got": vgot})

    if problems:
        return fail("normaliz.metrics", path=out_path, found=found, problems=problems)

    return ok("normaliz.metrics", path=out_path, found=found)

def main() -> int:
    # Ensure UTF-8 output for Hijaiyyah characters and robust printing on Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="Path ke HL18_release_integrity.yaml")
    ap.add_argument("--check-manifest", action="store_true", help="Cek MANIFEST.json sinkron dengan spec (best-effort)")
    ap.add_argument("--json", dest="json_out", default=None, help="Tulis report JSON ke file")
    ap.add_argument("--lenient", action="store_true", help="Tidak fail-fast; tetap jalankan semua check dan laporkan semua mismatch.")
    args = ap.parse_args()

    spec_path = os.path.abspath(args.spec)
    base_dir = os.path.dirname(spec_path)

    spec = load_spec(spec_path)

    # resolve release_root (optional)
    release_root = get_release_root(spec)
    base_dir2 = resolve_path(base_dir, release_root)

    results: List[CheckResult] = []

    # dataset
    ds_path_rel, ds_sha = get_dataset_node(spec)
    ds_path = resolve_path(base_dir2, ds_path_rel)
    results.append(check_sha("dataset_18d.sha256", ds_path, ds_sha))

    # normaliz in/out sha
    nz_in, nz_out, metrics_expected = get_normaliz_nodes(spec)
    nz_in_path = resolve_path(base_dir2, nz_in["path"])
    nz_out_path = resolve_path(base_dir2, nz_out["path"])
    results.append(check_sha("normaliz.input.sha256", nz_in_path, nz_in["sha256"]))
    results.append(check_sha("normaliz.output.sha256", nz_out_path, nz_out["sha256"]))

    # parse metrics from .out
    results.append(verify_normaliz_metrics(nz_out_path, metrics_expected))

    # artifacts
    artifacts = spec.get("artifacts")
    if not isinstance(artifacts, list):
        die("Spec harus punya 'artifacts' list.")
    for i, a in enumerate(artifacts):
        if not isinstance(a, dict) or "path" not in a or "sha256" not in a:
            die(f"artifacts[{i}] harus dict berisi path dan sha256.")
        p = resolve_path(base_dir2, a["path"])
        results.append(check_sha(f"artifact[{i}].sha256", p, a["sha256"]))
        # size lock (support: size_bytes OR optional_size_bytes)
        size = a.get("size_bytes", a.get("optional_size_bytes"))
        if size is not None:
            try:
                size_int = int(size)
                results.append(check_size(f"artifact[{i}].size", p, size_int))
            except Exception:
                results.append(fail(f"artifact[{i}].size", path=p, error="invalid_size_field", value=size))

    # optional: CSGI dataset (semantic validation)
    csgi = spec.get("csgi_dataset")
    if isinstance(csgi, dict) and "path" in csgi and "sha256" in csgi:
        csgi_path = resolve_path(base_dir2, csgi["path"])
        results.append(check_sha("csgi_dataset.sha256", csgi_path, csgi["sha256"]))
        try:
            validate_csgi_dataset(csgi_path)
            results.append(ok("csgi_dataset.validate", path=csgi_path,
                              note="28/28 letters; letter_id(NFC+strip tatweel); no-dup keys; 8-neighborhood points"))
        except Exception as e:
            results.append(fail("csgi_dataset.validate", path=csgi_path, error=str(e)))
    else:
        # not declared: skip (keeps backward compatibility)
        results.append(ok("csgi_dataset.validate", note="not declared in spec (skipped)"))

    # optional manifest sync check
    if args.check_manifest:
        # find manifest artifact entry if present
        manifest_entry = None
        for a in artifacts:
            if isinstance(a, dict) and str(a.get("path", "")).lower().endswith("manifest.json"):
                manifest_entry = a
                break
        if manifest_entry is None:
            results.append(fail("manifest.sync", error="manifest_not_listed_in_artifacts"))
        else:
            results.append(check_manifest_sync(manifest_entry["path"], spec, base_dir2))

    # Determine pass/fail
    all_ok = all(r.ok for r in results)

    # Build report
    report = {
        "spec_path": spec_path,
        "release_id": spec.get("release_id"),
        "dimension": spec.get("dimension"),
        "ok": all_ok,
        "results": [
            {"ok": r.ok, "name": r.name, "details": r.details}
            for r in results
        ],
    }

    # Print summary
    if all_ok:
        print("PASS: HL release integrity verified.")
    else:
        print("FAIL: HL release integrity check failed.")
        for r in results:
            if not r.ok:
                print(f" - {r.name}: {r.details}")

    # Write JSON report if requested
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    return 0 if all_ok else 1


if __name__ == "__main__":
    main()
