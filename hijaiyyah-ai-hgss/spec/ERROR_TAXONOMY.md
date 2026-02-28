# Error Taxonomy — Hijaiyah-AI

Errors identified during the Guarded repair loop are categorized into the following taxonomy to provide precise feedback for LLM correction.

| Category | Description | Examples |
|---|---|---|
| `SCHEMA_MISSING_KEY` | A required top-level or nested key is absent. | `event_sha256` missing |
| `SCHEMA_TYPE_MISMATCH` | A field value has the wrong data type. | `version` is int instead of string |
| `SCHEMA_HEX_LENGTH` | A hex-encoded string has the wrong length. | SHA-256 not 64 chars |
| `VERSION_LOCK_FAIL` | The version or git_hash does not match the lock. | `e392c68` expected |
| `CBOR_HASH_MISMATCH` | `event_sha256` does not match recomputed hash. | Canonical CBOR check fail |
| `HGSS_VERIFIER_FAIL` | Ground truth verifier rejected the evidence. | Lease signature invalid |
| `FORMAT_INVALID_JSON` | Output is not a valid JSON string. | Unescaped chars, trailing commas |

## Feedback Mapping
Each error category triggers a specific "Hint" or "Correction Instruction" provided to the LLM during the repair loop.
