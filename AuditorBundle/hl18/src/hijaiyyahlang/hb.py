"""
hb.py — HijaiyyahLang Hilbert Basis API
Loads HB18.json / HB18.bin, provides membership & codec.
"""
from __future__ import annotations
import json
import struct
from dataclasses import dataclass, field
from typing import List, Optional

Vector = List[int]

MAGIC = b"HLHB18"
VERSION = 1
HEADER_SIZE = 12  # 6 magic + 4 version + 1 dim + 1 hb_size

@dataclass(frozen=True)
class HilbertBasis:
    dimension: int
    hb_size: int
    basis: List[Vector]

    def __post_init__(self):
        if len(self.basis) != self.hb_size:
            raise ValueError(f"basis length {len(self.basis)} != hb_size {self.hb_size}")
        for i, v in enumerate(self.basis):
            if len(v) != self.dimension:
                raise ValueError(f"basis[{i}] dimension {len(v)} != {self.dimension}")


# ── JSON codec ──────────────────────────────────────────────

def load_hb_json(path: str) -> HilbertBasis:
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return HilbertBasis(
        dimension=obj["dimension"],
        hb_size=obj["hb_size"],
        basis=[list(v) for v in obj["basis"]],
    )


# ── Binary codec ────────────────────────────────────────────

def load_hb_bin(path: str) -> HilbertBasis:
    with open(path, "rb") as f:
        data = f.read()

    if len(data) < HEADER_SIZE:
        raise ValueError("HB18.bin too short")
    if data[:6] != MAGIC:
        raise ValueError(f"Bad magic: {data[:6]!r}")

    ver = struct.unpack_from(">I", data, 6)[0]
    if ver != VERSION:
        raise ValueError(f"Unsupported version: {ver}")

    dim = data[10]
    hb_size = data[11]
    expected = HEADER_SIZE + dim * hb_size
    if len(data) < expected:
        raise ValueError(f"Truncated: need {expected}, got {len(data)}")

    basis: List[Vector] = []
    offset = HEADER_SIZE
    for _ in range(hb_size):
        row = list(data[offset : offset + dim])
        basis.append(row)
        offset += dim

    return HilbertBasis(dimension=dim, hb_size=hb_size, basis=basis)


def save_hb_bin(hb: HilbertBasis, path: str) -> None:
    buf = bytearray(MAGIC)
    buf += struct.pack(">I", VERSION)
    buf.append(hb.dimension)
    buf.append(hb.hb_size)
    for v in hb.basis:
        buf += bytes(v)
    with open(path, "wb") as f:
        f.write(buf)


# ── Monoid membership (brute greedy) ────────────────────────

def is_dominated(v: Vector) -> bool:
    """True if all components >= 0."""
    return all(x >= 0 for x in v)


def is_in_monoid_greedy(target: Vector, basis: List[Vector], max_depth: int = 200) -> bool:
    """
    Greedy DFS check: can `target` be written as sum of basis vectors?
    Returns True if decomposition found, False otherwise.
    Not guaranteed to find all solutions — used for witness hole testing.
    """
    if all(x == 0 for x in target):
        return True
    if max_depth <= 0:
        return False
    dim = len(target)
    for b in basis:
        rem = [target[i] - b[i] for i in range(dim)]
        if is_dominated(rem):
            if is_in_monoid_greedy(rem, basis, max_depth - 1):
                return True
    return False
