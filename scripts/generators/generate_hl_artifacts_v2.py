#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HL Release Artifact Generator (v2)
- Reads Normaliz output (.out)
- Extracts: Hilbert basis, extreme rays, support hyperplanes, equations,
           congruences (optional), lattice basis (optional)
- Writes: HB*.json, HYP*.json, EQ*.json, CONG*.json, LATTICE*.json, MANIFEST.json
- Computes SHA-256 sidecars for each JSON and HB*.bin
- Builds HB*.bin (unsigned LEB128 varint)

No external dependencies.
"""

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

# -------------------------
# Hash helpers
# -------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    path.write_text(text, encoding="utf-8", newline="\n")

def write_json(path: Path, obj: Any) -> None:
    s = json.dumps(obj, ensure_ascii=False, indent=2)
    write_text(path, s + "\n")

def write_sha256_sidecar(path: Path) -> None:
    digest = sha256_file(path)
    write_text(Path(str(path) + ".sha256"), f"{digest}  {path.name}\n")

# -------------------------
# Varint (ULEB128 unsigned)
# -------------------------

def uleb128(n: int) -> bytes:
    if n < 0:
        raise ValueError("ULEB128 requires non-negative integer")
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | 0x80 if n else b)
        if not n:
            break
    return bytes(out)

# -------------------------
# Normaliz parsing
# -------------------------

EMBED_RE = re.compile(r"embedding dimension\s*=\s*(\d+)", re.IGNORECASE)
RANK_RE  = re.compile(r"rank\s*=\s*(\d+)", re.IGNORECASE)
EXTI_RE  = re.compile(r"external index\s*=\s*(\d+)", re.IGNORECASE)
INTI_RE  = re.compile(r"internal index\s*=\s*(\d+)", re.IGNORECASE)

def parse_int_list_line(line: str) -> Optional[List[int]]:
    line = line.strip()
    if not line or not re.match(r"^[\-\d]", line):
        return None
    try:
        return [int(x) for x in line.split()]
    except ValueError:
        return None

def try_find_section(lines: List[str], header: str) -> Optional[Tuple[int,int]]:
    pat = re.compile(rf"^\s*(\d+)\s+{re.escape(header)}\s*:\s*$", re.IGNORECASE)
    for i, ln in enumerate(lines):
        m = pat.match(ln)
        if m:
            return int(m.group(1)), i + 1
    return None

def parse_vectors(lines: List[str], start: int, count: int, dim: int, allow_dim_plus_one=False) -> List[List[int]]:
    vecs: List[List[int]] = []
    i = start
    while i < len(lines) and len(vecs) < count:
        nums = parse_int_list_line(lines[i])
        if nums is None:
            i += 1
            continue
        if len(nums) == dim:
            vecs.append(nums)
        elif allow_dim_plus_one and len(nums) == dim + 1:
            vecs.append(nums)
        else:
            raise ValueError(f"Bad vector length at line {i+1}: got {len(nums)}, expected {dim}{' or '+str(dim+1) if allow_dim_plus_one else ''}.")
        i += 1
    if len(vecs) != count:
        raise ValueError(f"Incomplete section parse: expected {count}, got {len(vecs)}")
    return vecs

def parse_normaliz_out(path_out: Path) -> Dict[str, Any]:
    lines = path_out.read_text(encoding="utf-8", errors="replace").splitlines()

    # Metrics scan
    dim = None
    metrics: Dict[str, Any] = {}
    for ln in lines:
        m = EMBED_RE.search(ln)
        if m:
            dim = int(m.group(1))
        m = RANK_RE.search(ln)
        if m:
            # handle "rank = 14 (maximal)" too
            metrics["rank"] = int(m.group(1))
        m = EXTI_RE.search(ln)
        if m:
            metrics["external_index"] = int(m.group(1))
        m = INTI_RE.search(ln)
        if m:
            metrics["internal_index"] = int(m.group(1))
        if "not integrally closed" in ln.lower():
            metrics["integrally_closed"] = False

    if dim is None:
        raise ValueError("embedding dimension not found in Normaliz output")
    metrics["embedding_dimension"] = dim
    metrics.setdefault("integrally_closed", True)

    # Required sections: Hilbert basis
    hb_sec = try_find_section(lines, "Hilbert basis elements")
    if hb_sec is None:
        raise ValueError("Hilbert basis elements section not found")
    hb_count, hb_start = hb_sec
    hb = parse_vectors(lines, hb_start, hb_count, dim)
    metrics["hilbert_basis_size"] = hb_count

    # Optional: extreme rays
    rays = []
    rays_sec = try_find_section(lines, "extreme rays")
    if rays_sec is not None:
        rays_count, rays_start = rays_sec
        rays = parse_vectors(lines, rays_start, rays_count, dim)
        metrics["extreme_rays"] = rays_count

    # Optional: support hyperplanes
    hyperplanes = []
    hyp_sec = try_find_section(lines, "support hyperplanes")
    if hyp_sec is not None:
        hyp_count, hyp_start = hyp_sec
        hyperplanes = parse_vectors(lines, hyp_start, hyp_count, dim)
        metrics["support_hyperplanes"] = hyp_count

    # Optional: equations
    equations = []
    eq_sec = try_find_section(lines, "equations")
    if eq_sec is not None:
        eq_count, eq_start = eq_sec
        equations = parse_vectors(lines, eq_start, eq_count, dim)
        metrics["equations"] = eq_count
    else:
        metrics["equations"] = 0

    # Optional: congruences (may not exist)
    congruences = []
    cong_sec = try_find_section(lines, "congruences")
    if cong_sec is not None:
        cong_count, cong_start = cong_sec
        raw = parse_vectors(lines, cong_start, cong_count, dim, allow_dim_plus_one=True)
        mods = set()
        for row in raw:
            if len(row) == dim + 1:
                congruences.append({"c": row[:dim], "modulus": row[-1]})
                mods.add(row[-1])
            else:
                congruences.append({"c": row, "modulus": None})
        metrics["congruences"] = cong_count
        if len(mods) == 1:
            metrics["congruence_modulus"] = list(mods)[0]
    else:
        metrics["congruences"] = 0
        metrics["congruence_modulus"] = None

    # Optional: lattice basis
    lattice = []
    lat_sec = try_find_section(lines, "basis elements of generated  lattice")
    if lat_sec is not None:
        lat_count, lat_start = lat_sec
        lattice = parse_vectors(lines, lat_start, lat_count, dim)
        metrics["lattice_basis_size"] = lat_count
    else:
        metrics["lattice_basis_size"] = 0

    return {
        "dimension": dim,
        "metrics": metrics,
        "hilbert_basis": hb,
        "extreme_rays": rays,
        "support_hyperplanes": hyperplanes,
        "equations": equations,
        "congruences": congruences,
        "lattice_basis": lattice
    }

# -------------------------
# Bytecode writer: HB*.bin
# -------------------------

def write_hb_bin(path_bin: Path, hb: List[List[int]], dim: int, version_u16: int = 0x0100) -> None:
    path_bin.parent.mkdir(parents=True, exist_ok=True)
    r = len(hb)
    # magic depends on dim (8 bytes total)
    magic = (f"HLHB{dim:02d}".encode("ascii") + b"\x00\x00")[:8]
    header = magic + struct.pack("<H", version_u16) + struct.pack("<B", dim) + struct.pack("<H", r) + struct.pack("<B", 1)
    body = bytearray()
    for vec in hb:
        if len(vec) != dim:
            raise ValueError("Hilbert basis vector dimension mismatch")
        for x in vec:
            if x < 0:
                raise ValueError("HB bin expects non-negative entries")
            body.extend(uleb128(x))
    path_bin.write_bytes(header + bytes(body))

# -------------------------
# Main
# -------------------------

def main():
    ap = argparse.ArgumentParser(description="Generate HL release artifacts from Normaliz .out")
    ap.add_argument("--release-id", default="HL-18-v1.0")
    ap.add_argument("--normaliz-out", required=True)
    ap.add_argument("--normaliz-version", default="3.11.0")
    ap.add_argument("--outdir", default="hl-release")
    ap.add_argument("--dataset-18d-sha256", default=None, help="SHA-256 of MH-28-v1.0-18D.csv")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    artifacts = outdir / "artifacts"
    bytecode = outdir / "bytecode"

    parsed = parse_normaliz_out(Path(args.normaliz_out))
    dim = parsed["dimension"]
    hb = parsed["hilbert_basis"]

    # Build JSON artifacts
    HB = {
        "type": "HL.HilbertBasis",
        "hl_release_id": args.release_id,
        "dimension": dim,
        "hb_size": len(hb),
        "basis_order": "as_listed",
        "basis": hb,
        "source": {"tool": f"Normaliz {args.normaliz_version}", "file": args.normaliz_out}
    }
    HYP = {
        "type": "HL.SupportHyperplanes",
        "hl_release_id": args.release_id,
        "dimension": dim,
        "count": len(parsed["support_hyperplanes"]),
        "format": "a_dot_x_ge_0",
        "hyperplanes": [{"a": a} for a in parsed["support_hyperplanes"]],
        "source": {"tool": f"Normaliz {args.normaliz_version}", "file": args.normaliz_out}
    }
    EQ = {
        "type": "HL.Equations",
        "hl_release_id": args.release_id,
        "dimension": dim,
        "count": len(parsed["equations"]),
        "equations": parsed["equations"],
        "semantics": "each row r enforces r·x = 0"
    }
    CONG = {
        "type": "HL.Congruences",
        "hl_release_id": args.release_id,
        "dimension": dim,
        "count": len(parsed["congruences"]),
        "modulus": parsed["metrics"].get("congruence_modulus"),
        "congruences": parsed["congruences"],
        "semantics": "each row c enforces c·x ≡ 0 (mod modulus)"
    }
    LATT = {
        "type": "HL.LatticeBasis",
        "hl_release_id": args.release_id,
        "dimension": dim,
        "rank": parsed["metrics"].get("rank"),
        "basis": parsed["lattice_basis"],
        "source": {"tool": f"Normaliz {args.normaliz_version}", "file": args.normaliz_out}
    }

    artifacts.mkdir(parents=True, exist_ok=True)
    bytecode.mkdir(parents=True, exist_ok=True)

    hb_json = artifacts / f"HB{dim}.json"
    hyp_json = artifacts / f"HYP{dim}.json"
    eq_json = artifacts / f"EQ{dim}.json"
    cong_json = artifacts / f"CONG{dim}.json"
    latt_json = artifacts / f"LATTICE{dim}.json"

    write_json(hb_json, HB); write_sha256_sidecar(hb_json)
    write_json(hyp_json, HYP); write_sha256_sidecar(hyp_json)
    write_json(eq_json, EQ); write_sha256_sidecar(eq_json)
    write_json(cong_json, CONG); write_sha256_sidecar(cong_json)
    write_json(latt_json, LATT); write_sha256_sidecar(latt_json)

    # Bytecode
    hb_bin = bytecode / f"HB{dim}.bin"
    write_hb_bin(hb_bin, hb, dim)
    write_sha256_sidecar(hb_bin)

    # Manifest
    manifest = {
        "hl_release_id": args.release_id,
        "dimension": dim,
        "dataset_18d_sha256": args.dataset_18d_sha256,
        "normaliz": {
            "input": {"path": "MH_18x28.in", "sha256": sha256_file(outdir / "MH_18x28.in") if (outdir / "MH_18x28.in").exists() else None},
            "output": {"path": Path(args.normaliz_out).name, "sha256": sha256_file(Path(args.normaliz_out))}
        },
        "metrics": parsed["metrics"],
        "artifacts": {
            f"artifacts/{hb_json.name}": sha256_file(hb_json),
            f"artifacts/{hyp_json.name}": sha256_file(hyp_json),
            f"artifacts/{eq_json.name}": sha256_file(eq_json),
            f"artifacts/{cong_json.name}": sha256_file(cong_json),
            f"artifacts/{latt_json.name}": sha256_file(latt_json),
            f"bytecode/{hb_bin.name}": sha256_file(hb_bin)
        },
        "notes": "Artifacts are tooling for HL (norm/valid). They do not define letters."
    }
    manifest_path = artifacts / "MANIFEST.json"
    write_json(manifest_path, manifest); write_sha256_sidecar(manifest_path)

    # ARTIFACTS.sha256
    lines = []
    for name in [hb_json.name, hyp_json.name, eq_json.name, cong_json.name, latt_json.name, "MANIFEST.json"]:
        lines.append(f"{sha256_file(artifacts / name)}  {name}")
    write_text(artifacts / "ARTIFACTS.sha256", "\n".join(lines) + "\n")

    print("OK")
    print("Dimension:", dim)
    print("Hilbert basis size:", len(hb))
    print("Outdir:", str(outdir.resolve()))
    print("Manifest:", str(manifest_path.resolve()))
    print("HB bin:", str(hb_bin.resolve()))

if __name__ == "__main__":
    main()
