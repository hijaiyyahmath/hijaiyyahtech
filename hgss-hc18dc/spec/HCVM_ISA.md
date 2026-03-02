# HCVM (Hijaiyyah Crypto Virtual Machine) ISA — HGSS-HCVM-v1.HC18DC (e392c68)

Status: **NORMATIVE**.  
HCVM adalah mesin virtual kripto deterministik (audit-grade) untuk menjalankan pipeline **HGSS** menuju artefak **HC18DC**.

HGSS strength source: **Hijaiyyah geometry + dataset-seal**, diikat ke kripto standar (HKDF/HMAC/AEAD).

---

## 1) Instruction Word (IW) 32-bit (Normatif)

Format (MSB → LSB):
[opcode:8 | Rd:4 | Ra:4 | Rb:4 | subop:4 | imm8:8]

Bit positions:
- opcode = bits [31:24]
- Rd     = [23:20]
- Ra     = [19:16]
- Rb     = [15:12]
- subop  = [11:8]
- imm8   = [7:0]

Serialization: **little-endian** per word.

---

## 2) Register File (Normatif)

- Scalar regs: S0..S15 (u64 in implementation; address arithmetic uses low 32-bit wrap where stated)
- Vector regs: V0..V15, each stores v18 (18×u32, 72 bytes)
- Hash regs: H0..H7, each stores 32 bytes (SHA-256 digest)
- Flags:
  - CLOSED_HINT (0/1), set by SETFLAG
  - ERR code (trap cause)
  - HALTED

---

## 3) Dataset Locks (Normatif, Hard-Locked)

Runtime MUST enforce the following SHA-256 (fail-closed):
- MH28_SHA256 = 7393659dfe979cf85b1cf6293179f7ba1f49b4eedd1af19f002170148ce00380
- CSGI28_SHA256 = 530845fbc3815ea9f02c75d44bda0e1aa096ec93729942d24d2d8bb0bd56c9d5

VERIFY_LOCKS MUST TRAP if configured file hashes mismatch.

---

## 4) Nonce Policy (Normatif, Cluster 2b Range Leasing)

Nonce96 = prefix32 || ctr64 (little-endian byte layout):
- prefix32: u32 (4 bytes LE)
- ctr64:    u64 (8 bytes LE)

prefix32 derivation (Normatif):
prefix32 = Trunc32_LE( SHA-256("HGSS|HC18DC|NONCE|v1|" || key_id || node_id) )
Where Trunc32_LE means: interpret first 4 digest bytes as little-endian u32.

Lease evidence struct in memory (Normatif minimal for deterministic replay):
- prefix32 (u32 LE) at offset 0
- cur_ctr64 (u64 LE) at offset 8
- end_ctr64 (u64 LE) at offset 16
Total used offsets: 0..23 (24 bytes).

NONCE_NEXT MUST:
- verify prefix32 matches expected from (key_id,node_id) if verification enabled
- verify cur_ctr64 <= end_ctr64 else TRAP
- output nonce12 = prefix32||cur_ctr64 to destination buffer
- increment cur_ctr64 and store back (durably outside VM; VM updates memory copy)

---

## 5) CORE-1 Conformance (Normatif, always-on)

SETFLAG adjacency rule:
- Every AUDIT_V18 instruction MUST be preceded immediately by SETFLAG CLOSED_HINT,b (b in {0,1}).
- If not, TRAP/HALT.

---

## 6) Opcode Table (Subset Normatif v1.0 Demo)

### 0x40 LDI_S (Load Immediate Scalar)
- Form: LDI_S Sd, imm32
- IW: opcode=0x40, Rd=Sd, all other fields 0
- EXT: imm32 (u32 little-endian)
- Semantics: S[Sd] <- imm32

### 0x01 VERIFY_LOCKS
- Semantics: verify MH28/CSGI28 hashes (fail-closed); TRAP if mismatch

### 0x02 TRX_INIT
- Form: TRX_INIT S_ptr in Rd (scalar pointer)
- Semantics: init transcript builder with buffer base pointer S[Rd]

### 0x10 LDH_V18
- Form: LDH_V18 Vd, letter_index(imm8)
- Semantics: load v18 master (72 bytes) by index into V[Vd]

### 0x11 LDH_CSGI_H
- Form: LDH_CSGI_H Hd, letter_index(imm8)
- Semantics: load csgi_entry_sha256 (32 bytes) by index into H[Hd]

### 0x30 SETFLAG (CLOSED_HINT only)
Encoding identical to CMM-18C:
- SETFLAG CLOSED_HINT,0 => 0x30000000
- SETFLAG CLOSED_HINT,1 => 0x30000001

### 0x20 AUDIT_V18 (Vs = Rd, NORMATIF)
- Form: AUDIT_V18 Vs (Vs = Rd)
- MUST satisfy CORE-1 adjacency
- Semantics: HL-18 audit (derived totals, rho>=0, eps range, mod4 if CLOSED_HINT=1).
- Fail => TRAP.

### 0x12 VC1 (JIM Vortex)
- Form: VC1 Sd, Vs (Vs=Ra)
- Output:
  - S[Sd]   = vc1_bit (0/1)
  - S[Sd+1] = hatTheta
  - S[Sd+2] = U
  - S[Sd+3] = rho
- Uses Jim-mask from master v18 of index for letter "ج".

### 0x03 TRX_APPEND
- Form: TRX_APPEND Vs, Hcsgi
- Vs index in Ra; Hcsgi index in Rb
- Reads CLOSED_HINT from flag
- Appends canonical record and updates running aggregates (VC1_AGG, GEO_AGG)

### 0x04 TRX_FINALIZE
- Semantics:
  - finalize transcript bytes
  - store VC1_AGG in H6
  - store GEO_AGG in H7

### 0x05 COMMIT_SHA256
- Semantics: H0 <- SHA-256(transcript_bytes)

### 0x06 KDF_HKDF_SHA256
- Semantics: derive K_aead and K_mac from master_secret with:
  salt=MH28_SHA256
  info includes (aead_alg, key_id, H6, H7)
- Output stored internally (implementation-defined)

### 0x07 HMAC_SHA256
- Semantics: H3 <- HMAC-SHA256(K_mac, H0)

### 0x50 NONCE_NEXT
- Form: NONCE_NEXT Sdst, Slease
- Rd = Sdst pointer to 12-byte output buffer
- Ra = Slease pointer to lease struct
- Semantics per section 4.

### 0x70 AEAD_AESGCM_ENC
- Semantics:
  - encrypt transcript_bytes using AES-256-GCM with derived K_aead and nonce12 from memory
  - AAD = "HGSS|HC18DC|v1.0|" || MH28 || CSGI28 || H6 || H7 || key_id || txid
  - ciphertext written to memory at pointer S3 (must be non-zero) and length stored to S12

### 0xFF HALT
Stop normal.

---

## 7) Trap Policy (Audit-grade)
Any violation MUST TRAP/HALT immediately.
Implementation MUST record ERR code.

Minimum trap causes (recommended):
- 1 ILLEGAL_OPCODE
- 2 ILLEGAL_ENCODING
- 5 CONFORMANCE_SETFLAG_REQUIRED
- 6 AUDIT_DERIVED_MISMATCH
- 7 AUDIT_RHO_NEGATIVE
- 8 AUDIT_MOD4
- 9 AUDIT_EPS_RANGE
- 21 LEASE_EXHAUSTED
- 22 LEASE_PREFIX_MISMATCH
- 24 DATASET_LOCK_FAIL
- 25 CRYPTO_FAIL
