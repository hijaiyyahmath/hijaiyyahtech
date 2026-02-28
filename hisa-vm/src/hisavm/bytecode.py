# src/hisavm/bytecode.py
from __future__ import annotations
import struct
from typing import Iterable, List

def words_to_bytes_le(words: Iterable[int]) -> bytes:
    return b"".join(struct.pack("<I", w & 0xFFFFFFFF) for w in words)

def bytes_to_words_le(b: bytes) -> List[int]:
    if len(b) % 4 != 0:
        raise ValueError("BYTECODE_LEN_NOT_MULTIPLE_OF_4")
    out = []
    for i in range(0, len(b), 4):
        out.append(struct.unpack_from("<I", b, i)[0])
    return out

def load_bin(path: str) -> bytes:
    return open(path, "rb").read()

def save_bin(path: str, data: bytes) -> None:
    import os
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(path, "wb").write(data)
