from __future__ import annotations

from dataclasses import dataclass

# Opcodes (normative v1.0)
OP_LDV     = 0x11
OP_AUDIT   = 0x20
OP_SETFLAG = 0x30
OP_HALT    = 0xFF

# Flag IDs (normative v1.0)
FLAGID_CLOSED_HINT = 0  # subop=0

@dataclass(frozen=True)
class IW:
    opcode: int
    rd: int
    ra: int
    rb: int
    subop: int
    imm8: int

def decode_iw(word: int) -> IW:
    """Decode according to [opcode:8|Rd:4|Ra:4|Rb:4|subop:4|imm8:8]."""
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
    """AUDIT Vs uses Vs = Rd (normative)."""
    return enc_iw(OP_AUDIT, rd=vs, ra=0, rb=0, subop=0, imm8=0)

def enc_ldv(vd: int, sa: int) -> int:
    """LDV Vd, [Sa+off32] uses Vd=Rd, Sa=Ra, then extension word off32."""
    return enc_iw(OP_LDV, rd=vd, ra=sa, rb=0, subop=0, imm8=0)

def enc_halt() -> int:
    return enc_iw(OP_HALT, rd=0, ra=0, rb=0, subop=0, imm8=0)
