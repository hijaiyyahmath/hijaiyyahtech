# HCPU-AI Release Lock

Release ini secara normatif terkunci pada parameter berikut:

- **HCPU-AI Version**: `HCPU-AI-v1.0+local.1`
- **HISA Dependency**: `HISA-VM-v1.0`
- **Mapping Context**: v18 (18-Dimensional)

## Verifikasi Integritas
Gunakan tool `release/verify_hcpu_ai_release.py` untuk memvalidasi:
1. Hash dari file spesifikasi di `/spec`.
2. Hash dari demo bytecode di `/release/bytecode/audit_jim.bin`.
3. Konsistensi `MANIFEST.json`.
