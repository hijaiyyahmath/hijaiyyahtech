# HCPU-AI v1.0 (Release-Grade) — HCPU-AI-v1.0+local.1

## 1) Objective
HCPU-AI adalah reference execution engine (software) untuk stack Hijaiyyah yang bersifat hardware-close (register machine).
Fungsi utamanya adalah:
- Delegasi eksekusi instruksi ke HISA-VM.
- Menghasilkan audit trace deterministik.
- Menegakkan loop kepatuhan AI (Compliance Loop) dalam mode CORE, FEEDBACK, dan OWNER.
- Integrasi opsional dengan Hijaiyyah-AI HGSS untuk verifikasi bukti (evidence).

## 2) Identity
- **Release ID**: `HCPU-AI-v1.0+local.1`
- **ISA Contract**: HISA v1.0
- **Register Model**: Hybrid (Vector + Scalar)
- **Determinism**: Wajib, 100% reproducible.

## 3) Register Model
- **V0..V15**: Vector registers (18 lanes, u32) untuk data geometri.
- **R0..R7**: Scalar registers (u64) untuk control flow dan metadata.

## 4) Audit Policy
Setiap eksekusi harus menghasilkan trace yang mencakup state register sebelum/sesudah instruksi dan hasil Audit Gates (rho, mod4).
