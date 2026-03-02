# HISA (Hijaiyyah Instruction Set Architecture) — CMM-18C v1.0

Dokumen ini adalah definisi **normatif** instruksi inti CMM‑18C v1.0.
Semua implementasi (VM reference, RTL HC‑CPU, dan LLVM lowering) wajib sesuai.

## 1. Konvensi Umum (Normatif)
- Lane width: **w = 32-bit** (uint32 per lane)
- v18 = **18 lane** (72 bytes) dengan urutan HL‑18 (lihat spec utama).
- Bytecode word = 32-bit, serialized **little-endian**.
- Format Instruction Word (IW): lihat `spec/BYTECODE_ENCODING.md`.

## 2. CORE-only Conformance (Normatif, always-on)
**CORE-1 adjacency rule**:
Setiap instruksi `AUDIT Vs` **wajib** didahului tepat **1 instruksi sebelumnya**
oleh `SETFLAG CLOSED_HINT, b` dengan `b ∈ {0,1}`.
Jika tidak terpenuhi → **TRAP/HALT** dengan `ERR=5 CONFORMANCE_SETFLAG_REQUIRED`.

## 3. Instruction Set (Subset Normatif v1.0)

### 3.1 LDV — Load v18 dari memory pointer (pointer ABI)
**Mnemonic**: `LDV Vd, [Sa + off32]`  
**Opcode**: `0x11`  
**Panjang**: 8 bytes (IW + 1 extension word `off32`)

**Field mapping (IW)**:
- `Rd` = `Vd` (vector dest 0..15)
- `Ra` = `Sa` (scalar base 0..15)
- `Rb` must be 0
- `subop` must be 0
- `imm8` must be 0

**Extension word**:
- `off32` = u32 little-endian

**Semantik**:
- `addr = S[Sa] + off32` (u32 wrap)
- Alignment rule (normatif): `addr % 16 == 0`, jika tidak → TRAP `ERR=10 MISALIGNED_V18_PTR`
- Load 18×u32 little-endian dari memory:
  `Vd.lane[j] = mem_u32_le(addr + 4*j)` untuk j=0..17

**Trap (normatif)**:
- Field must-be-zero dilanggar → TRAP `ERR=2 ILLEGAL_ENCODING`
- Misaligned pointer → TRAP `ERR=10 MISALIGNED_V18_PTR`

---

### 3.2 SETFLAG — Injeksi metadata CLOSED_HINT
**Mnemonic**: `SETFLAG CLOSED_HINT, b`  
**Opcode**: `0x30`  
**Panjang**: 4 bytes

**Field mapping (IW)**:
- `Rd=Ra=Rb=0` wajib
- `subop = 0` (FlagID CLOSED_HINT)
- `imm8 = b` dengan `b ∈ {0,1}`, bit [7:1] harus 0

**Semantik**:
- `FL.CLOSED_HINT ← b`
- set latch `prev_was_setflag ← 1` (untuk CORE‑1)

**Trap (normatif)**:
- `subop != 0` → TRAP `ERR=4 ILLEGAL_FLAG`
- `imm8` bukan {0,1} atau field lain non‑zero → TRAP `ERR=2 ILLEGAL_ENCODING`

**Literal encoding** (normatif):
- `SETFLAG CLOSED_HINT,0` = `0x30000000`
- `SETFLAG CLOSED_HINT,1` = `0x30000001`

---

### 3.3 AUDIT — Audit v18 (Vs = Rd)
**Mnemonic**: `AUDIT Vs`  
**Opcode**: `0x20`  
**Panjang**: 4 bytes

**Field mapping (IW)**:
- `Rd = Vs` (vector source 0..15)  **(NORMATIF: Vs = Rd)**
- `Ra=Rb=0`, `subop=0`, `imm8=0` wajib

**Semantik (audit-grade, fail-closed)**:
Gunakan rumus HL‑18:
- Derived totals: `AN/AK/AQ` harus konsisten
- `U = q_t + 4*q_d + q_s + q_z + 2*k_z`
- `rho = hatTheta - U` harus `>= 0`
- `eps ∈ {0,1}`
- Jika `FL.CLOSED_HINT=1` maka wajib `hatTheta % 4 == 0`
Pelanggaran → TRAP/HALT dengan ERR sesuai taxonomy (lihat TRAP_CONFORMANCE).

**Conformance (CORE‑1)**:
Jika instruksi sebelumnya bukan `SETFLAG CLOSED_HINT,b` → TRAP `ERR=5`.

---

### 3.4 HALT
**Mnemonic**: `HALT`  
**Opcode**: `0xFF`  
**Panjang**: 4 bytes

**Field mapping (IW)**:
- Semua field selain opcode harus 0; pelanggaran → TRAP `ERR=2 ILLEGAL_ENCODING`

**Semantik**:
Stop normal (non-trap).
