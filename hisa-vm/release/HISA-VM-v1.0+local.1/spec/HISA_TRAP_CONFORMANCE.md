# HISA Trap & Conformance v1.0 — HISA-VM-v1.0+local.1

Status: NORMATIVE

## 1) CORE-1 Conformance (always-on)
Every `AUDIT Vs` MUST be immediately preceded by:
`SETFLAG CLOSED_HINT, b` where b in {0,1}.

Violation => TRAP/HALT with ERR=5 (CONFORMANCE_SETFLAG_REQUIRED).

## 2) Trap Policy (fail-closed)
On TRAP:
- execution stops immediately
- ERR is set
- program MUST be considered invalid for audit-grade processing

## 3) Trap Codes (Normative)
| ERR | Name | Condition |
|---:|---|---|
| 1 | ILLEGAL_OPCODE | opcode not recognized |
| 2 | ILLEGAL_ENCODING | must-be-zero rule violated; invalid imm8; etc |
| 3 | ILLEGAL_REG | register index out of range (if detected) |
| 4 | ILLEGAL_FLAG | SETFLAG subop not 0 (only CLOSED_HINT allowed) |
| 5 | CONFORMANCE_SETFLAG_REQUIRED | AUDIT without SETFLAG immediately before |
| 6 | AUDIT_DERIVED_MISMATCH | AN/AK/AQ mismatch vs recompute |
| 7 | AUDIT_RHO_NEGATIVE | rho = hatTheta - U < 0 |
| 8 | AUDIT_MOD4 | CLOSED_HINT=1 and hatTheta % 4 != 0 |
| 9 | AUDIT_EPS_RANGE | eps not in {0,1} |

## 4) Audit Formulas (Normative)
Given v18 lanes (HL-18 order):
- AN = nt + nf + nm
- AK = km + kt + kd + ka + kz
- AQ = qa + qt + qd + qs + qz
- U  = qt + 4*qd + qs + qz + 2*kz
- rho = hatTheta - U

## 5) CLOSED_HINT gate (Normative)
If CLOSED_HINT=1 then:
- hatTheta % 4 MUST equal 0
Else TRAP ERR=8.
