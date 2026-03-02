# Audit Walkthrough: HGSS-HCVM-v1.HC18DC (e392c68)
Release: **HGSS-HCVM-v1.HC18DC**

I have completed the audit and hardening of the `hgss-hc18dc` component. This guide provides the operational steps for auditors.

## 0. Key Documents
- **Quickstart**: [AUDITORS_QUICKSTART.md](AUDITORS_QUICKSTART.md) — 1-page verification guide.
- **Frozen Schema**: [spec/AUDIT_EVIDENCE_SCHEMA.md](spec/AUDIT_EVIDENCE_SCHEMA.md) — Source of Truth for data.
- **Audit Report**: [audit_report.md](audit_report.md) — Repository mapping and hardening accomplishments.

## 1. Operational Pipeline
The HCVM (Hijaiyyah Crypto Virtual Machine) implements standard instruction sets for HL-18 auditing, including VC-1 aggregation and AEAD encryption.

### 1.1 Cluster Demo (One-Command)
Generate fresh evidence and automatically verify it:
```powershell
cd c:/hijaiyyah-codex/hgss-hc18dc
$env:PYTHONPATH="src;tests"
python tools/hgss_make_example_event.py --fresh
```

### 1.2 Manual Verification
Verify an existing audit log and its artifacts:
```powershell
python tools/hgss_verify_evidence.py --event audit/auditlog.jsonl --ciphertext-file artifacts/ct.bin --trace-file artifacts/trace.jsonl
```

## 2. Hardening Confirmation
- **HSM Integration**: Master secrets never touch the host filesystem in plaintext.
- **Lease Signature**: Nonce ranges are signed by a central Authority via COSE_Sign1 (ES256).
- **Dataset Lock**: SHA-256 hashes for MH28 and CSGI28 are hard-locked in the verifier.

## 3. Unit Tests
Ensure all core logic and fail-closed behaviors remain intact:
```powershell
python -m pytest tests/test_full_hgss_pipeline.py -v
python -m pytest tests/test_lease_signature_verification.py -v
```

## 4. Status
- **Git Hash**: `e392c68`
- **Git Tag**: `HGSS-HCVM-v1.HC18DC`
- **Verification Result**: **PASS**
