# Audit Demo Plan — HGSS-HCVM-v1.HC18DC (e392c68)

## 0) Goal
Menyediakan demo **one-command** yang menghasilkan bukti audit lengkap sesuai [Audit Evidence Schema (Frozen)](spec/AUDIT_EVIDENCE_SCHEMA.md).

## 1) Verification Script
`tools/hgss_make_example_event.py --fresh`

## 2) PASS Criteria
1. **Exit Code**: Harus 0.
2. **Artifacts Exist**:
   - `audit/auditlog.jsonl`
   - `artifacts/ct.bin`
   - `artifacts/trace.jsonl`
   - `artifacts/lease_input.json`
3. **Signature**: `lease_sig.verified` pada auditlog harus `PASS`.
4. **Verifier Output**: Harus mencetak `[OK] End-to-end evidence generated and verified.`

## 3) FAIL Criteria
1. **Missing Schema Keys**: Jika ada field wajib di §1-§11 SCHEMA yang hilang.
2. **Hex Length Mismatch**: Jika panjang digest SHA-256 bukan 64 hex.
3. **Invalid Signature**: Jika token COSE dirusak atau kadaluwarsa.
4. **Data Lock Failure**: Jika hash dataset MH28/CSGI28 tidak sesuai konstanta normatif.
