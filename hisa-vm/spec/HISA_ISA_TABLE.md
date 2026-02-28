# HISA ISA Table v1.0 — HISA-VM-v1.0+local.1

Status: NORMATIVE  
Encoding definition is in: `spec/HISA_BYTECODE_ENCODING.md`

## 1) Registers
- Vector registers: V0..V15, each holds v18 (18×u32).
- Scalar registers: S0..S15 exist in VM state but are not required by v1.0 minimal ISA.

## 2) Opcodes (Normative v1.0)
| Mnemonic | Opcode | Length | Notes |
|---|---:|---:|---|
| `LDH_V18 Vd, #idx` | 0x10 | 4 bytes | Load v18 by letter index (0..27) into Vd |
| `SETFLAG CLOSED_HINT, b` | 0x30 | 4 bytes | b in {0,1}; encoding fixed to 0x30000000/01 |
| `AUDIT Vs` | 0x20 | 4 bytes | **Vs = Rd** (normative); CORE-1 enforced |
| `HALT` | 0xFF | 4 bytes | Normal termination |

## 3) Operand Mapping (Normative)
### 3.1 LDH_V18
- Vd = Rd
- idx = imm8
- Ra/Rb/subop MUST be 0

### 3.2 SETFLAG (CLOSED_HINT only)
- Rd=Ra=Rb MUST be 0
- subop MUST be 0
- imm8 MUST be 0 or 1
- Literal words:
  - `SETFLAG CLOSED_HINT,0` => `0x30000000`
  - `SETFLAG CLOSED_HINT,1` => `0x30000001`

### 3.3 AUDIT
- **Vs = Rd** (normative)
- Ra=Rb=subop=imm8 MUST be 0
- CORE‑1 adjacency: instruction immediately before AUDIT MUST be SETFLAG CLOSED_HINT,b.

### 3.4 HALT
- All fields besides opcode MUST be 0.

## 4) Semantic Summary (Normative)
- `LDH_V18` loads v18 from master table indexed by HIJAIYYAH_28 order.
- `SETFLAG` sets CLOSED_HINT used by mod-4 gate during AUDIT.
- `AUDIT` validates derived identities (AN/AK/AQ, U/rho, eps range, mod4 when closed_hint=1).
- Any failure => TRAP/HALT (fail-closed).
