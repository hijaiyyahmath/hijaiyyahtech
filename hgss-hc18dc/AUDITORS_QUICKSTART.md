# Auditor's Quickstart — HGSS-HCVM-v1.HC18DC (e392c68)

## 0. Objective
Verify the integrity and conformance of the HGSS/HC18DC crypto-transaction pipeline. 
The **Source of Truth** for data structures is the [Audit Evidence Schema (Frozen)](spec/AUDIT_EVIDENCE_SCHEMA.md).

## 1. Prerequisites
- Python 3.10+
- `pip install cbor2 cryptography`
- Repository verified at commit: `e392c68`

## 2. One-Command Verification
Run the end-to-end audit demo. This generates fresh evidence, signs it, and runs the verifier.
```powershell
# Set path and run demo
$env:PYTHONPATH="src;tests"
python tools/hgss_make_example_event.py --fresh
```

## 3. Conformance Checklist
- [ ] **Release Lock**: Version must be `HGSS-HCVM-v1.HC18DC`.
- [ ] **Hash Lock**: Git hash must be `e392c68`.
- [ ] **Signature**: Lease token must be COSE_Sign1 (ES256) with `verified: PASS`.
- [ ] **HSM**: `hsm.key_id_hex` must match event `key_id_hex`.
- [ ] **Determinism**: `event_sha256` must validate against canonical CBOR.

## 4. Key Artifacts
- **Audit Log**: `audit/auditlog.jsonl`
- **Ciphertext (AEAD output)**: `artifacts/ct.bin`
- **Trace**: `artifacts/trace.jsonl`
- **Schema**: `spec/AUDIT_EVIDENCE_SCHEMA.md`
