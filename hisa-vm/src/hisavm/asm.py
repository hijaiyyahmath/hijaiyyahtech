# src/hisavm/asm.py
from __future__ import annotations

import re
from typing import List

from hisavm.isa import enc_ldh_v18, enc_setflag_closed_hint, enc_audit, enc_halt
from hisavm.bytecode import words_to_bytes_le

RE_COMMENT = re.compile(r";.*$")

def parse_reg(token: str) -> int:
    token = token.strip().upper()
    if not token.startswith("V"):
        raise ValueError(f"REG_EXPECTED_V: {token}")
    n = int(token[1:])
    if not (0 <= n <= 15):
        raise ValueError("VREG_OOB")
    return n

def assemble_text(text: str) -> bytes:
    words: List[int] = []

    for line in text.splitlines():
        line = RE_COMMENT.sub("", line).strip()
        if not line:
            continue
        # normalize commas
        line = line.replace(",", " ")
        parts = [p for p in line.split() if p]
        op = parts[0].upper()

        if op == "LDH_V18":
            # LDH_V18 V0, 4
            if len(parts) != 3:
                raise ValueError("LDH_V18_ARITY")
            vd = parse_reg(parts[1])
            idx = int(parts[2].lstrip("#"))
            words.append(enc_ldh_v18(vd, idx))

        elif op == "SETFLAG":
            # SETFLAG CLOSED_HINT, 0
            if len(parts) != 3:
                raise ValueError("SETFLAG_ARITY")
            flag = parts[1].upper()
            if flag != "CLOSED_HINT":
                raise ValueError("ONLY_CLOSED_HINT_SUPPORTED")
            b = int(parts[2])
            words.append(enc_setflag_closed_hint(b))

        elif op == "AUDIT":
            # AUDIT V0
            if len(parts) != 2:
                raise ValueError("AUDIT_ARITY")
            vs = parse_reg(parts[1])
            words.append(enc_audit(vs))

        elif op == "HALT":
            if len(parts) != 1:
                raise ValueError("HALT_ARITY")
            words.append(enc_halt())

        else:
            raise ValueError(f"UNKNOWN_OPCODE:{op}")

    return words_to_bytes_le(words)
