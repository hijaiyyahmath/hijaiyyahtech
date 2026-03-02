# TRAP CONFORMANCE (CORE-only)

## Core-1 Rule
Every `AUDIT` instruction *must* be immediately preceded by exactly one `SETFLAG CLOSED_HINT, imm1` instruction in the execution stream.
- If an `AUDIT` is decoded and the `prev_was_setflag` hardware latch is `0`, the CPU must `TRAP/HALT` with `ERR=5` (`CMM18C_TRAP_CONFORMANCE_SETFLAG_REQ`).
- The `prev_was_setflag` latch is cleared after every instruction execution, except after `SETFLAG`, which sets it to `1`.

## Trap Policy
Any conformance violation or arithmetic constraint failure traps the CPU.

| Error | Name | Condition |
|-------|------|-----------|
| 5 | `CMM18C_TRAP_CONFORMANCE_SETFLAG_REQ` | `AUDIT` without preceding `SETFLAG` |
| 6 | `CMM18C_TRAP_AUDIT_DERIVED_MISMATCH` | `AN`, `AK`, or `AQ` value mismatch, or `U` calculation mismatch |
| 7 | `CMM18C_TRAP_AUDIT_RHO_NEGATIVE` | `rho < 0` |
| 8 | `CMM18C_TRAP_AUDIT_MOD4` | `HatTheta % 4 != 0` when `CLOSED_HINT == 1` |
| 9 | `CMM18C_TRAP_AUDIT_EPS_RANGE` | `Eps` is out of normative range |
| 10 | `CMM18C_TRAP_MISALIGNED_V18_PTR` | `LDV` effective address is not 16-byte aligned |
