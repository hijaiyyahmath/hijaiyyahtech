# HCPU-AI Trap & Conformance

HCPU-AI mengikuti taksonomi trap HISA v1.0 untuk memastikan kondisi "fail-closed".

| Trap Code | Name | Description |
| :--- | :--- | :--- |
| `0x01` | `ILLEGAL_ENCODING` | Instruksi tidak dikenal atau field tidak valid. |
| `0x02` | `CORE1_VIOLATION` | Pelanggaran aturan kedekatan (adjacency) CORE-1. |
| `0x03` | `AUDIT_FAIL` | Gagal verifikasi geometri (rho/checksum). |
| `0x04` | `MOD4_FAIL` | Pelanggaran normalisasi mod4. |
| `0x05` | `DATASET_LOCK_MISMATCH` | Checksum MH-28 tidak cocok dengan lock. |
| `0x06` | `DETERMINISM_ERROR` | Deteksi inkonsistensi internal. |
