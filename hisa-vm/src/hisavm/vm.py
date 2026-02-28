# src/hisavm/vm.py
from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Optional, List, Dict

from hisavm.constants import (
    LANES, VREGS, SREGS,
    OP_LDH_V18, OP_SETFLAG, OP_AUDIT, OP_HALT,
    FLAGID_CLOSED_HINT,
)
from hisavm.errors import (
    ERR_NONE,
    ERR_ILLEGAL_OPCODE,
    ERR_ILLEGAL_ENCODING,
    ERR_ILLEGAL_FLAG,
    ERR_CONFORMANCE_SETFLAG_REQUIRED,
)
from hisavm.isa import decode_iw
from hisavm.audit import audit_v18_or_raise

class Trap(Exception):
    def __init__(self, err: int, msg: str = ""):
        super().__init__(f"TRAP({err}) {msg}")
        self.err = err

def fetch_u32_le(code: bytes, pc: int) -> int:
    if pc + 4 > len(code):
        raise Trap(ERR_ILLEGAL_ENCODING, "CODE_OOB")
    return struct.unpack_from("<I", code, pc)[0]

@dataclass
class VMState:
    PC: int = 0
    halted: bool = False
    ERR: int = ERR_NONE
    CLOSED_HINT: int = 0
    prev_was_setflag: bool = False
    # scalar regs
    S: List[int] = None
    # vector regs (v18)
    V: List[List[int]] = None

    def __post_init__(self):
        if self.S is None:
            self.S = [0] * SREGS
        if self.V is None:
            self.V = [[0] * LANES for _ in range(VREGS)]

class HisaVM:
    def __init__(self, code: bytes, v18_by_index: List[List[int]]):
        self.code = code
        self.v18_by_index = v18_by_index
        self.st = VMState()

    def trap(self, err: int, msg: str = ""):
        self.st.ERR = err
        self.st.halted = True
        raise Trap(err, msg)

    def step(self):
        st = self.st
        if st.halted:
            return

        w = fetch_u32_le(self.code, st.PC)
        iw = decode_iw(w)

        # SETFLAG (CLOSED_HINT only) — does not clear adjacency
        if iw.opcode == OP_SETFLAG:
            if (iw.rd, iw.ra, iw.rb) != (0,0,0):
                self.trap(ERR_ILLEGAL_ENCODING, "SETFLAG_FIELDS")
            if iw.subop != FLAGID_CLOSED_HINT:
                self.trap(ERR_ILLEGAL_FLAG, "SETFLAG_SUBOP")
            if iw.imm8 not in (0,1):
                self.trap(ERR_ILLEGAL_ENCODING, "SETFLAG_IMM8")
            st.CLOSED_HINT = iw.imm8
            st.prev_was_setflag = True
            st.PC += 4
            return

        # For any non-SETFLAG instruction, consume/clear adjacency latch (CORE-1)
        prev = st.prev_was_setflag
        st.prev_was_setflag = False

        # LDH_V18
        if iw.opcode == OP_LDH_V18:
            if (iw.ra, iw.rb, iw.subop) != (0,0,0):
                self.trap(ERR_ILLEGAL_ENCODING, "LDH_FIELDS")
            idx = iw.imm8
            if idx >= len(self.v18_by_index):
                self.trap(ERR_ILLEGAL_ENCODING, "LDH_IDX_OOB")
            st.V[iw.rd] = list(map(int, self.v18_by_index[idx]))
            st.PC += 4
            return

        # AUDIT (Vs = Rd)
        if iw.opcode == OP_AUDIT:
            if not prev:
                self.trap(ERR_CONFORMANCE_SETFLAG_REQUIRED, "CORE1_REQUIRED")
            if (iw.ra, iw.rb, iw.subop, iw.imm8) != (0,0,0,0):
                self.trap(ERR_ILLEGAL_ENCODING, "AUDIT_FIELDS")
            Vs = iw.rd
            try:
                audit_v18_or_raise(st.V[Vs], st.CLOSED_HINT)
            except RuntimeError as e:
                err = int(e.args[0]) if e.args else ERR_ILLEGAL_ENCODING
                self.trap(err, "AUDIT_FAIL")
            st.PC += 4
            return

        # HALT
        if iw.opcode == OP_HALT:
            if (iw.rd, iw.ra, iw.rb, iw.subop, iw.imm8) != (0,0,0,0,0):
                self.trap(ERR_ILLEGAL_ENCODING, "HALT_FIELDS")
            st.halted = True
            return

        self.trap(ERR_ILLEGAL_OPCODE, f"OP={iw.opcode:#x}")

    def run(self, max_steps: int = 100000) -> int:
        steps = 0
        while not self.st.halted and steps < max_steps:
            self.step()
            steps += 1
        return steps
