# Spesifikasi CMM‑18C (Codex Multidimensional Mesin‑18Cube) — Revisi Final v1.0

Bab ini mendefinisikan mesin komputasi universal berbasis Codex Hijaiyyah v18 (HL‑18) sebagai model pemrograman multidimensi yang standalone, deterministik, dan audit‑grade.

## X.0 Tujuan
Tujuan CMM‑18C‑v1.0 adalah menjadikan eksekusi program HijaiyyahLang/HL‑18 dan validasi Matematika Hijaiyyah sebagai komputasi standar yang:
- **Normatif & deterministik** (hasil sama untuk input sama, lintas VM/RTL).
- **Audit‑grade (fail‑closed)**: semua pelanggaran invariant → TRAP/HALT.
- **Portable**: bytecode 32‑bit word, little‑endian, lintas platform.
- **Hardware‑close**: Register Machine dengan scalar regs + vector regs 18‑lane.

## X.1 Model Data & Semantik Inti
### X.1.1 Tipe data utama: v18 (18‑lane, w=32)
Nilai dasar komputasi: $V \in \mathbb{N}_0^{18}$.
Lane width normatif: $w=32$ (unsigned, wraparound mod $2^{32}$).
Layout lane normatif (HL-18):
$V = [\hat{\Theta} \mid n_t, n_f, n_m \mid k_m, k_t, k_d, k_a, k_z \mid q_a, q_t, q_d, q_s, q_z \mid A_N, A_K, A_Q \mid \varepsilon]$

### X.1.2 Derived (audit) normatif (HL‑18)
- $A_N = n_t + n_f + n_m$
- $A_K = k_m + k_t + k_d + k_a + k_z$
- $A_Q = q_a + q_t + q_d + q_s + q_z$
- $U = q_t + 4q_d + q_s + q_z + 2k_z$
- $\rho = \hat{\Theta} - U$

**Kriteria audit normatif (CMM‑18C CORE):**
1. Semua lane integer dan $\ge 0$.
2. Derived totals $A_N, A_K, A_Q$ harus cocok dengan recompute.
3. $\rho \ge 0$.
4. $\varepsilon \in \{0, 1\}$.
5. **Gate mod‑4** (jika `FL.CLOSED_HINT=1`): $\hat{\Theta} \equiv 0 \pmod 4$.

## X.2 Arsitektur Register Machine (CORE-only)
### X.2.1 Register set
- **Vector registers**: V0..V15 (18×u32).
- **Scalar registers**: S0..S15 (u32, address/pointer).
- **PC**, **FL** (flags), **HALTED** state.

### X.2.2 Flags (FL)
- `CLOSED_HINT` (1 bit).
- `ERR` (8 bit): Kode TRAP cause.

### X.2.3 Kebijakan error: TRAP/HALT
Pelanggaran $\rightarrow$ TRAP/HALT langsung: eksekusi berhenti, `FL.ERR` di-set, PC dikunci.

## X.3 ISA Inti + Kebijakan Konformansi
| Kelas | Mnemonic | Opcode | Semantik |
|-------|----------|--------|----------|
| Memory | `LDV Vd, [Sa+off32]` | `0x11` | Load v18 (72 byte) |
| Flag | `SETFLAG CLOSED_HINT, b` | `0x30` | Set metadata hint |
| Audit | `AUDIT Vs` | `0x20` | Derived check + constraints |
| Control | `HALT` | `0xFF` | Berhenti normal |

## X.4 Bytecode Portable
- IW format: `[opcode:8 | Rd:4 | Ra:4 | Rb:4 | subop:4 | imm8:8]`
- **SETFLAG**: `opcode=0x30, subop=0, imm8∈{0,1}, Rd=Ra=Rb=0`.
- **LDV**: `opcode=0x11, Rd=Vd, Ra=Sa, Rb=subop=imm8=0`, diikuti extension `off32`.

## X.5 Pointer ABI & Alignment
- **v18 in memory**: `i32[18]` (72 bytes).
- **Alignment**: `addr ≡ 0 (mod 16)`. Gagal $\rightarrow$ `ERR=10` (MISALIGNED_V18_PTR).

## X.6 CORE‑1 Always‑On (Conformance Latch)
Setiap `AUDIT Vs` wajib didahului tepat 1 instruksi sebelumnya oleh `SETFLAG CLOSED_HINT, b`. Jika tidak $\rightarrow$ `ERR=5` (CONFORMANCE_SETFLAG_REQUIRED).

## X.10 Primary Vortex Jim (ج) & Vortex Channel VC‑1
### X.10.1 Definisi
- $J := v18\_master(letter\_id("ج"))$
- Mask vortex: $m_j = J_j \pmod 2$.

### X.10.2 VC‑1 Bit Channel
$b(V) = (\sum_{j=0}^{17} (V_j \pmod 2) \cdot m_j) \pmod 2$

### X.10.3 VC‑1 Energy Channel
$E(V) = (\hat{\Theta}, U, \rho)$
