# HISA Bytecode Encoding v1.0 — HISA-VM-v1.0+local.1

Status: NORMATIVE

## 1) Instruction Word (IW) 32-bit
Format (MSB → LSB):
[opcode:8 | Rd:4 | Ra:4 | Rb:4 | subop:4 | imm8:8]

Bit positions:
- opcode: [31:24]
- Rd:     [23:20]
- Ra:     [19:16]
- Rb:     [15:12]
- subop:  [11:8]
- imm8:   [7:0]

## 2) Word Stream Endianness (Normative)
Each 32-bit IW is serialized to bytes using **little-endian**.

Example:
IW = 0x30000001 is stored as bytes: 01 00 00 30.

## 3) Must-be-zero rule (Normative)
Fields not used by an opcode MUST be zero.
If violated => TRAP ERR=2 (ILLEGAL_ENCODING).

## 4) Examples (Normative)
### 4.1 SETFLAG CLOSED_HINT,1
IW = 0x30000001

### 4.2 AUDIT V0 (Vs=Rd=0)
IW = 0x20000000

### 4.3 LDH_V18 V0, #4 (index 4 = ج)
IW = opcode 0x10, imm8=4:
IW = 0x10000004

### 4.4 HALT
IW = 0xFF000000

## 5) Demo program words (audit_jim)
Sequence:
- 0x10000004  (LDH_V18 V0,#4)
- 0x30000000  (SETFLAG CLOSED_HINT,0)
- 0x20000000  (AUDIT V0)
- 0xFF000000  (HALT)
