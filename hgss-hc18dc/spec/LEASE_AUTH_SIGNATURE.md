# Lease Authority Signature — HGSS-HCVM-v1.HC18DC (e392c68)

## 1) Goal
Lease artifacts granting temporary nonce ranges MUST be signed by a trusted Lease Authority.

## 2) Format: COSE_Sign1 (ES256)
Audit verification REQUIRES standard COSE_Sign1 (RFC 9052) for interoperability.

### 2.1 Algorithm
- Algorithm: `ES256` (ECDSA P-256 + SHA-256)
- Private key MUST be managed by the Lease Authority.

## 3) Payload Structure (Canonical CBOR)
The payload MUST be a map containing:

| Key | Type | Description |
|---|---|---|
| `allocator_id` | `tstr` | Non-empty service identity |
| `lease_id` | `tstr` | Unique lease identifier |
| `key_id_hex` | `tstr` | Lowercase hex of the HCVM key |
| `node_id_hex` | `tstr` | Lowercase hex of the granted node |
| `prefix32` | `uint` | The 32-bit nonce prefix |
| `start_ctr` | `uint` | Lower counter bound |
| `end_ctr` | `uint` | Upper counter bound |
| `expires_at` | `tstr` | RFC3339 UTC time |

## 4) Verification Requirements
- **Pass/Fail**: The Boolean result of signature verification MUST be logged as `verified: PASS/FAIL`.
- **Digest Lock**: SHA-256 of the raw token MUST be logged to prevent disputes.
