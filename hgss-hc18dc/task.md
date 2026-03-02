# Task Checklist — HGSS-HCVM-v1.HC18DC (e392c68)

## A) Audit-Ready Checklist (Must)
- [x] Git tag & hash locked (release tag points to exact commit)
- [x] Banking-Grade Hardening (HSM + Lease Signature)
    - [x] Define `KeyProvider` and HSM stubs
    - [x] Implement COSE Lease Signature verification
    - [x] Integrate hardening into `HCVM` verify_locks
    - [x] Create documentation (spec/) and unit tests
- [x] Finalize Release & Schema Freeze (v1.HC18DC)
    - [x] Create `spec/AUDIT_EVIDENCE_SCHEMA.md` with frozen requirements
    - [x] Update `hgss_make_example_event.py` to match §2-§11 of schema
    - [x] Update `hgss_verify_evidence.py` with strict schema validation
- [x] Banking Integration Hardening (SHOULD)
    - [x] HSM/KMS Production Management (Zero-plaintext policy)
    - [x] Range Leasing Service Architecture (Atomic DB allocation, CAS logic)
    - [x] Nonce Uniqueness Monitoring & Incident Runbook
    - [x] Immutable Audit Log (WORM/Append-only) Configuration
    - [x] SBOM & Dependency Pinning (Hash-locked manifest)
    - [x] SAST & Secret Scanning (CI Integration)
- [x] One-command audit demo runnable (hgss_make_example_event --fresh)
- [x] Unit tests PASS (core pipeline + evidence verification)
- [x] Fail-closed behavior confirmed (TRAP/HALT on mismatch / lease exhaustion)
- [x] Formal Production Release Certificate issued
- [x] Release Evidence Summary tool (`print_release_state.py`) created
- [x] Formal Release Attestation (`RELEASE_ATTESTATION.md`) generated

## B) Banking Integration Checklist (Should)
- [x] Master secret handled by HSM/KMS (no plaintext secret in app logs)
- [x] Range leasing service documented (atomic allocation proof / DB schema)
- [x] Nonce uniqueness monitoring & incident response
- [x] Immutable audit log storage (WORM bucket / append-only)
- [x] SBOM generated + dependency pinning
- [x] SAST + secret scanning integrated into CI

## C) Evidence Artifacts Checklist (Per Transaction)
- [x] lease evidence + lease_evidence_sha256 (CBOR canonical)
- [x] nonce96 + policy id
- [x] commitment (sha256) + mac tag (hmac-sha256)
- [x] aad_sha256
- [x] ciphertext_sha256 (+ ciphertext bytes if allowed)
- [x] trace_sha256 (+ trace bytes if allowed)
- [x] event_sha256 (CBOR canonical digest)
