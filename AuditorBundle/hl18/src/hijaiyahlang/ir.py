"""
ir.py — HVM IR Codex Compiler (HijaiyahLang → IR Instructions)

Compiles HL word sequences into stack-based IR instructions.
Input standardized via letter_id (NFC + strip tatweel, H28-only).
"""
from __future__ import annotations
import struct
import unicodedata
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional

from hijaiyahlang.dataset import Dataset18


class Op(IntEnum):
    LOAD     = 0x01
    ADD      = 0x02
    AUDIT    = 0x03
    MOD      = 0x04
    HALT     = 0x05
    VALIDATE = 0x06  # non-normative side-effect
    LEARN    = 0x07  # non-normative side-effect

NORMATIVE_OPS = {Op.LOAD, Op.ADD, Op.AUDIT, Op.MOD, Op.HALT}


@dataclass(frozen=True)
class IRInst:
    op: Op
    arg: Optional[str | int] = None   # letter for LOAD, modulus for MOD

    def __repr__(self) -> str:
        if self.arg is not None:
            return f"{self.op.name} {self.arg!r}"
        return self.op.name


# ── Letter ID normalization ──────────────────────────────────

H28_SET = set("ابتثجحخدذرزسشصضطظعغفقكلمنوهي")

def letter_id(s: str) -> str:
    """NFC normalize + strip Arabic Tatweel (U+0640)."""
    s = unicodedata.normalize("NFC", s)
    return s.replace("\u0640", "")


def validate_letter(ch: str) -> str:
    """Returns letter_id or raises ValueError."""
    lid = letter_id(ch)
    if lid not in H28_SET:
        raise ValueError(f"Invalid letter outside H28: {ch!r} (lid={lid!r})")
    return lid


# ── Compiler ─────────────────────────────────────────────────

def compile_word(word: str, ds: Dataset18, *,
                 audit: bool = True,
                 validate: bool = False,
                 learn: bool = False) -> List[IRInst]:
    """
    Compile a Hijaiyah word into IR instructions.
    word: string of Hijaiyah letters (e.g. "بسم")
    """
    letters = [validate_letter(ch) for ch in word]
    if len(letters) == 0:
        raise ValueError("Empty word")

    # Resolve each letter_id to its dataset key
    # (dataset may store "هـ" with tatweel as key)
    resolved: List[str] = []
    for lid in letters:
        if lid in ds.table:
            resolved.append(lid)
        else:
            # Try finding a key that normalizes to this letter_id
            found = None
            for k in ds.table:
                if letter_id(k) == lid:
                    found = k
                    break
            if found is None:
                raise ValueError(f"Letter {lid!r} not in dataset")
            resolved.append(found)

    insts: List[IRInst] = []

    # LOAD first letter
    insts.append(IRInst(Op.LOAD, resolved[0]))

    # LOAD + ADD for subsequent letters
    for key in resolved[1:]:
        insts.append(IRInst(Op.LOAD, key))
        insts.append(IRInst(Op.ADD))

    # Normative audit
    if audit:
        insts.append(IRInst(Op.AUDIT))

    # Non-normative side-effects
    if validate:
        insts.append(IRInst(Op.VALIDATE))
    if learn:
        insts.append(IRInst(Op.LEARN))

    insts.append(IRInst(Op.HALT))
    return insts


# ── IR Serialization (portable bytecode) ─────────────────────

MAGIC = b"HLIR"
VERSION = 1

def serialize_ir(insts: List[IRInst]) -> bytes:
    """Serialize IR instructions to portable bytecode."""
    buf = bytearray(MAGIC)
    buf += struct.pack(">H", VERSION)
    buf += struct.pack(">H", len(insts))
    for inst in insts:
        buf.append(inst.op)
        if inst.op == Op.LOAD:
            encoded = inst.arg.encode("utf-8")
            buf.append(len(encoded))
            buf += encoded
        elif inst.op == Op.MOD:
            buf += struct.pack(">H", inst.arg)
        else:
            buf.append(0)  # no arg
    return bytes(buf)


def deserialize_ir(data: bytes) -> List[IRInst]:
    """Deserialize portable IR bytecode."""
    if data[:4] != MAGIC:
        raise ValueError(f"Bad IR magic: {data[:4]!r}")
    ver = struct.unpack_from(">H", data, 4)[0]
    if ver != VERSION:
        raise ValueError(f"Unsupported IR version: {ver}")

    count = struct.unpack_from(">H", data, 6)[0]
    offset = 8
    insts: List[IRInst] = []
    for _ in range(count):
        op = Op(data[offset]); offset += 1
        if op == Op.LOAD:
            arglen = data[offset]; offset += 1
            arg = data[offset:offset+arglen].decode("utf-8")
            offset += arglen
            insts.append(IRInst(op, arg))
        elif op == Op.MOD:
            arg = struct.unpack_from(">H", data, offset)[0]; offset += 2
            insts.append(IRInst(op, arg))
        else:
            offset += 1  # skip 0-byte no-arg marker
            insts.append(IRInst(op))
    return insts
