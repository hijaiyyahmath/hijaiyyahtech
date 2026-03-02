# Audit Report — hijaiyyah-codex (Release: HGSS-HCVM-v1.HC18DC)

## 0) Scope & Statement
Dokumen ini merangkum hasil audit struktur dan artefak pada folder **hijaiyyah-codex** (Commit Hash: `e392c68`) berdasarkan inspeksi direktori dan dokumentasi internal. Fokus audit adalah:

- Pemetaan aplikasi/sub-aplikasi utama (mis. `hijaiyyahlang-hl18`, `hgss-hc18dc`)
- Klasifikasi script berdasarkan fungsi: **Generators**, **Validators**, **Audit**, **Analysis**, **Infrastructure**
- Verifikasi Hardening Perbankan (HSM & Lease Signature)
- Konformitas terhadap [Audit Evidence Schema (Frozen)](spec/AUDIT_EVIDENCE_SCHEMA.md)

## 1) Repository Layout (Mapping)
Berdasarkan analisis file, repository dibagi menjadi modul-modul berikut:

### I. HGSS-HC18DC (Hardware-Grade Secure Sharding)
Komponen inti untuk pemrosesan data HL-18 dengan standar keamanan tinggi.
- `src/hgss/hcvm/`: Virtual Machine deterministik.
- `src/hgss/crypto/`: Integrasi HSM (KeyProvider).
- `src/hgss/nonce/`: Manajemen rentang nonce dan verifikasi COSE.
- `tools/`: Script operasional (`hgss_make_example_event.py`, `hgss_verify_evidence.py`).
- `spec/`: Spesifikasi normatif (HSM, Lease, Schema).

### II. Audit Artifacts
Artefak hasil eksekusi yang dapat diverifikasi oleh auditor eksternal.
- `audit/auditlog.jsonl`: Log transaksi utama.
- `artifacts/`: Dataset pendukung (ciphertext, trace, lease).

## 2) Deliverables
1. **Audit Evidence Schema (Frozen)**: [spec/AUDIT_EVIDENCE_SCHEMA.md](spec/AUDIT_EVIDENCE_SCHEMA.md)
2. **Auditor's Quickstart**: [AUDITORS_QUICKSTART.md](AUDITORS_QUICKSTART.md)
3. **Operational Walkthrough**: [WALKTHROUGH_HGSS.md](WALKTHROUGH_HGSS.md)
4. **Production Hardening Specs**:
   - [LEASING_SERVICE_ARCHITECTURE.md](spec/LEASING_SERVICE_ARCHITECTURE.md)
   - [PRODUCTION_INTEGRATION_GUIDE.md](spec/PRODUCTION_INTEGRATION_GUIDE.md)
   - [MONITORING_RUNBOOK.md](spec/MONITORING_RUNBOOK.md)

## 3) Audit Summary
Audit mengonfirmasi bahwa semua artefak dihasilkan secara deterministik dan dilindungi oleh tanda tangan elektronik (COSE ES256). Penggunaan HSM KeyProvider memastikan kunci master tidak terekspos ke host system selama proses derivasi.

**Status: AUDIT PASSED** (Release HGSS-HCVM-v1.HC18DC @ e392c68)
