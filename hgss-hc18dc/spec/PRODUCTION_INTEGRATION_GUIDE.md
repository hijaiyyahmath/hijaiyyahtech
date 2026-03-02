# Production Integration Guide — HGSS-HCVM-v1.HC18DC @ e392c68

Status: NORMATIVE/OPERATIONAL (Production Security)

## 0) Goal
Dokumen ini menjelaskan integrasi produksi perbankan untuk HGSS/HC18DC:
- Zero-plaintext master secret
- WORM/immutable audit storage
- SBOM + dependency pinning
- CI/CD security controls (SAST + secret scanning)

## 1) Zero-Plaintext Master Secret (Normative)
- Master secret MUST reside in HSM/KMS.
- Host MUST NOT persist plaintext master secret to disk.
- Host MUST NOT log secret material.
- Key derivation MUST use KeyProvider interface:
  - PKCS#11 (on-prem HSM) or cloud KMS.

Acceptable profiles:
- Profile A: HSM derives and exports ephemeral session keys (RAM only).
- Profile B: HSM performs AEAD/HMAC directly; keys never leave.

## 2) Audit Log Storage — WORM (Normative)
Audit logs MUST be append-only and immutable:
- AWS S3 Object Lock (Compliance mode) / Glacier Vault Lock
- Azure Immutable Blob Storage (time-based retention)
- On-prem WORM storage if required

Artifacts to store (minimum):
- audit/auditlog.jsonl (event evidence)
- optional: artifacts/ct.bin, artifacts/trace.jsonl (policy dependent)
- integrity: store sha256 manifests for each batch/day

## 3) Evidence Verification Gate (Normative)
CI/CD and runtime release gates MUST include:
- schema freeze conformance (spec/AUDIT_EVIDENCE_SCHEMA.md)
- canonical CBOR digest checks
- lease signature verification PASS
- dataset-seal lock checks PASS

## 4) SBOM + Dependency Pinning (Normative)
- SBOM MUST be generated per release (CycloneDX or SPDX).
- Python dependencies MUST be pinned (hash-locked) for production:
  - constraints.txt with hashes OR poetry/uv lock
- Supply chain MUST be validated (no unreviewed packages).

## 5) CI/CD Security Controls (Normative)
Minimum controls:
- SAST: semgrep/bandit (policy baseline)
- Secret scanning: gitleaks/trufflehog + pre-commit hooks
- Dependency scanning: pip-audit/safety
- Unit tests + audit demo test gate must pass.

## 6) Operational Controls
- Key rotation policy (key_id schedule)
- Node identity management (node_id uniqueness)
- Incident response readiness (see MONITORING_RUNBOOK.md)

## 7) Release Lock
All production deployments MUST assert:
- hgss_version == HGSS-HCVM-v1.HC18DC
- git_hash == e392c68
- dataset hashes match locked MH28/CSGI28
