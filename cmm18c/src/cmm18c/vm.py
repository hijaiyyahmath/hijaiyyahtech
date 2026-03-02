from __future__ import annotations

import struct

from .isa import (
    decode_iw,
    OP_LDV, OP_AUDIT, OP_SETFLAG, OP_HALT,
    FLAGID_CLOSED_HINT,
)
from cmm18c.errors import (
    TrapCause,
    TrapException
)
from cmm18c.audit import audit_v18_or_trap

def fetch_u32_le(code: bytes, pc: int) -> int:
    if pc + 4 > len(code):
        raise TrapException(TrapCause.ILLEGAL_ENCODING, "FETCH_OOB")
    return struct.unpack_from("<I", code, pc)[0]

class CMM18CV10:
    def __init__(self, code: bytes, memory):
        self.code = code
        self.memory = memory

        self.pc = 0
        self.halted = False

        # Scalar regs S0..S15 (u32)
        self.s_regs = [0] * 16
        # Vector regs V0..V15, each is list[18]
        self.v_regs = [[0] * 18 for _ in range(16)]

        # Flags
        self.closed_hint = 0
        self.trapped = False
        self.trap_cause = TrapCause.NONE

        # CORE-1 latch
        self.prev_was_setflag = False

    def trap(self, cause: int, msg: str = ""):
        self.trapped = True
        self.trap_cause = cause
        self.halted = True
        print(f"TRAP {cause}: {msg}")

    def step(self):
        if self.halted or self.trapped:
            return

        try:
            iw_word = fetch_u32_le(self.code, self.pc)
            iw = decode_iw(iw_word)

            # --- SETFLAG ---
            if iw.opcode == OP_SETFLAG:
                if (iw.rd, iw.ra, iw.rb) != (0, 0, 0):
                    self.trap(TrapCause.ILLEGAL_ENCODING, "SETFLAG field non-zero")
                    return
                if iw.subop != FLAGID_CLOSED_HINT:
                    self.trap(TrapCause.ILLEGAL_FLAG, f"Unknown flag ID {iw.subop}")
                    return
                if iw.imm8 not in (0, 1):
                    self.trap(TrapCause.ILLEGAL_ENCODING, f"Invalid flag value {iw.imm8}")
                    return

                self.closed_hint = iw.imm8
                self.prev_was_setflag = True
                self.pc += 4
                return

            # For any non-SETFLAG, adjacency latch is consumed/cleared (normative CORE-1)
            prev = self.prev_was_setflag
            self.prev_was_setflag = False

            # --- LDV ---
            if iw.opcode == OP_LDV:
                if iw.rb != 0 or iw.subop != 0 or iw.imm8 != 0:
                    self.trap(TrapCause.ILLEGAL_ENCODING, "LDV field non-zero")
                    return

                off32 = fetch_u32_le(self.code, self.pc + 4)
                base = self.s_regs[iw.ra] & 0xFFFFFFFF
                addr = (base + (off32 & 0xFFFFFFFF)) & 0xFFFFFFFF

                if (addr & 0xF) != 0:
                    self.trap(TrapCause.MISALIGNED_V18_PTR, f"Address {addr:08x} not 16-byte aligned")
                    return

                self.v_regs[iw.rd] = self.memory.read_v18(addr)
                self.pc += 8
                return

            # --- AUDIT (Vs = Rd) ---
            if iw.opcode == OP_AUDIT:
                if not prev:
                    self.trap(TrapCause.CONFORMANCE_SETFLAG_REQ, "AUDIT without preceding SETFLAG")
                    return
                if iw.ra != 0 or iw.rb != 0 or iw.subop != 0 or iw.imm8 != 0:
                    self.trap(TrapCause.ILLEGAL_ENCODING, "AUDIT field non-zero")
                    return

                Vs = iw.rd  # NORMATIVE: Vs = Rd
                # audit-grade: any failure -> TRAP
                audit_v18_or_trap(self.v_regs[Vs], closed_hint=self.closed_hint)
                self.pc += 4
                return

            # --- HALT ---
            if iw.opcode == OP_HALT:
                # must be zero in other fields
                if iw.rd != 0 or iw.ra != 0 or iw.rb != 0 or iw.subop != 0 or iw.imm8 != 0:
                    self.trap(TrapCause.ILLEGAL_ENCODING, "HALT field non-zero")
                    return
                self.halted = True
                return

            self.trap(TrapCause.ILLEGAL_OPCODE, f"Opcode {iw.opcode:02x}")

        except TrapException as e:
            self.trapped = True
            self.trap_cause = e.cause
            self.halted = True
            print(f"TRAP {self.trap_cause}: {e.message}")

    def run(self, max_steps: int = 10_000):
        steps = 0
        while not self.halted and not self.trapped and steps < max_steps:
            self.step()
            steps += 1
        return steps
