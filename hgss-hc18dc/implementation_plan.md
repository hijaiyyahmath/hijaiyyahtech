# Implementation Plan — HGSS-HCVM-v1.HC18DC (e392c68)

## 0) Objective
Membangun pipeline audit-grade yang memadukan aspek Matematika Hijaiyyah:
- dataset-seal (hash-locked)
- geometri (CSGI + GeoSeal)
- MainPath/closed_hint (metadata)
- codex v18
- VC-1 JIM Vortex
dan mengikat semuanya ke kriptografi standar (HKDF/HMAC/AEAD), lalu menyediakan evidence & verifier.

## 1) Completed Work
### 1.1 Repository audit mapping
- Deep scan struktur direktori
- Klasifikasi tool: generators/validators/audit/infra
- `audit_report.md` disusun

### 1.2 HGSS-HC18DC audit demo (E2E)
- Tool dibuat: `hgss_make_example_event.py`
- Evidence hashing: Canonical CBOR (RFC 8949) via `cbor2`
- Verifier dibuat: `hgss_verify_evidence.py`

## 2) Verification Commands
```powershell
cd c:/hijaiyyah-codex/hgss-hc18dc
$env:PYTHONPATH="src;tests"
python tools/hgss_make_example_event.py --fresh
```

## 3) Constraints / Notes
- Demo secret hardcoded: audit/demo only.
- Produksi: master secret MUST reside in HSM/KMS boundary.
- Range leasing eksternal (DB/KMS) direpresentasikan sebagai input evidence agar replay deterministik.

## 4) Next Steps (Production Integration)
- Integrasi HSM/KMS real
- Integrasi allocator range leasing eksternal + atomic DB transactions
- Immutable audit log storage (WORM)
