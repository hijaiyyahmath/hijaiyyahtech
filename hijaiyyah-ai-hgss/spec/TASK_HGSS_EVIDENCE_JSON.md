# Task Definition: HGSS_EVIDENCE_JSON

## 1. Description
The agent is tasked with generating a single, valid JSON object that conforms to the `AUDIT_EVIDENCE_SCHEMA.md` as defined in the `HGSS-HCVM-v1.HC18DC` release.

## 2. Normative Constraints
- **Version**: MUST be `HGSS-HCVM-v1.HC18DC`.
- **Git Hash**: MUST be `e392c68`.
- **Schema Compliance**: All required keys MUST exist and conform to their specified formats (types and hex lengths).
- **Integrity**: The `event_sha256` MUST match the canonical CBOR hash of the event data (excluding the hash field itself).
- **Ground Truth**: The output MUST pass the evaluation by `hgss_verify_evidence.py`.

## 3. Evaluated Response Format
The response MUST be a raw JSON object string. Markdown code fences are allowed but will be stripped by the agent before validation.
