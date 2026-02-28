# RELEASE LOCK — Hijaiyyah-AI HGSS VM v1.0

Status: NORMATIVE / LOCKED

## 1. Project Identity
Project: Hijaiyyah-AI HGSS VM v1.0  
Purpose: Industrial A/B harness for LLM compliance against HGSS frozen evidence schema.

## 2. Normative Dependency Lock (HGSS)
This project is normatively bound to:

- HGSS Version Lock: `HGSS-HCVM-v1.HC18DC`
- HGSS Commit Lock: `e392c68`

The dependency repo MUST exist at:

`deps/hgss-hc18dc/`

Normative oracle artifacts:

- `deps/hgss-hc18dc/spec/AUDIT_EVIDENCE_SCHEMA.md`
- `deps/hgss-hc18dc/tools/hgss_verify_evidence.py`
- `deps/hgss-hc18dc/tools/check_release_lock.py`

Any mismatch invalidates results.

## 3. Guarded Mode v1.0 (Autofill Policy)
Guarded mode uses deterministic autofill:

- LLM generates semantic structure and non-hash fields.
- The system generates deterministic artifacts seeded by `txid_hex` and fills:
  - ciphertext_sha256, trace_sha256, lease_* digests
  - commitment/mac digests
  - canonical CBOR `event_sha256`

This policy maximizes industrial pass rates while preserving strict schema governance.

## 4. Forensic Artifacts Policy
Artifacts MUST be saved for every case (always-save):

`artifacts/runs/<run_id>/case_<id>/...`

This enables replay and forensic auditing.
