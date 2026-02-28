# src/hisavm/isa.py
from __future__ import annotations

from dataclasses import dataclass
from hisavm.constants import OP_SETFLAG, OP_AUDIT, OP_LDH_V18, OP_HALT, FLAGID_CLOSED_HINT

@dataclass(frozen=True)
class IW:
    opcode: int
    rd: int
    ra: int
    rb: int
    subop: int
    imm8: int

def decode_iw(word: int) -> IW:
    return IW(
        opcode=(word >> 24) & 0xFF,
        rd=(word >> 20) & 0xF,
        ra=(word >> 16) & 0xF,
        rb=(word >> 12) & 0xF,
        subop=(word >> 8) & 0xF,
        imm8=word & 0xFF,
    )

def enc_iw(opcode: int, rd=0, ra=0, rb=0, subop=0, imm8=0) -> int:
    return ((opcode & 0xFF) << 24) | ((rd & 0xF) << 20) | ((ra & 0xF) << 16) | ((rb & 0xF) << 12) | ((subop & 0xF) << 8) | (imm8 & 0xFF)

def enc_setflag_closed_hint(b: int) -> int:
    assert b in (0, 1)
    return enc_iw(OP_SETFLAG, rd=0, ra=0, rb=0, subop=FLAGID_CLOSED_HINT, imm8=b)

def enc_audit(vs: int) -> int:
    # Normative: Vs = Rd
    return enc_iw(OP_AUDIT, rd=vs, ra=0, rb=0, subop=0, imm8=0)

def enc_ldh_v18(vd: int, letter_index: int) -> int:
    assert 0 <= letter_index <= 255
    return enc_iw(OP_LDH_V18, rd=vd, ra=0, rb=0, subop=0, imm8=letter_index)

def enc_halt() -> int:
    return enc_iw(OP_HALT, rd=0, ra=0, rb=0, subop=0, imm8=0)
