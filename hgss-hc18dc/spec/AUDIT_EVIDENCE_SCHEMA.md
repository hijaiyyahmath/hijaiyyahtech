# Audit Evidence Schema (Frozen) — HGSS-HCVM-v1.HC18DC (e392c68)

Status: **FROZEN / NORMATIVE**  
This schema locks JSON/CBOR interoperability for HGSS audit events across languages and platforms.

All fields marked MUST are required for compliance.

---

## 0. Conventions (Normative)

### 0.1 Types
- `tstr` : CBOR text string / JSON string (UTF-8)
- `uint` : CBOR unsigned integer / JSON integer (non-negative)
- `bstr` : CBOR byte string (only used in CBOR mode; JSON uses hex encoding)

### 0.2 Hex encoding
All digests and binary identifiers stored in JSON MUST be:
- lowercase hex
- no `0x` prefix
- fixed length as specified

### 0.3 Version Lock
- `hgss_version` MUST equal: `HGSS-HCVM-v1.HC18DC`
- `git_hash` MUST equal: `e392c68`

---

## 1. Event Envelope (Top-level Map)

Top-level structure MUST be a map with keys below.

| Key | Type | Constraints | Description |
|---|---|---|---|
| `event_type` | `tstr` | MUST be `HGSS_HC18DC_TX` | Event class |
| `hgss_version` | `tstr` | MUST be `HGSS-HCVM-v1.HC18DC` | Release/version identifier |
| `git_hash` | `tstr` | MUST be `e392c68` | Commit hash lock |
| `git_tag` | `tstr` | MUST be `HGSS-HCVM-v1.HC18DC` | Tag lock |
| `timestamp_utc` | `tstr` | RFC3339 UTC (endswith `Z`) | Event timestamp |
| `node_id_hex` | `tstr` | 64 hex chars (=32 bytes) | Cluster node identity |
| `key_id_hex` | `tstr` | 64 hex chars (=32 bytes) | Active key identifier (public) |
| `txid_hex` | `tstr` | 64 hex chars (=32 bytes) | Transaction id (public) |
| `mh28_sha256` | `tstr` | 64 hex chars | Locked MH28 dataset seal |
| `csgi28_sha256` | `tstr` | 64 hex chars | Locked CSGI28 dataset seal |
| `lease` | `map` | see §2 | Nonce lease evidence |
| `lease_sig` | `map` | see §3 | Lease token signature evidence |
| `nonce` | `map` | see §4 | Nonce used for AEAD |
| `aggregates` | `map` | see §5 | VC1/GEO/AAD digests |
| `commitment` | `map` | see §6 | Commitment evidence |
| `mac` | `map` | see §7 | MAC evidence |
| `ciphertext` | `map` | see §8 | Ciphertext digest/len |
| `trace` | `map` | see §9 | Trace digest/count |
| `hsm` | `map` | see §10 | HSM KeyRef evidence |
| `status` | `map` | see §11 | HALT/TRAP status |
| `event_sha256` | `tstr` | 64 hex chars | Canonical CBOR digest of the event (see §12) |

---

## 2. Lease Evidence Object (`lease`)

| Key | Type | Constraints | Description |
|---|---|---|---|
| `allocator_id` | `tstr` | non-empty | Allocator service identity |
| `lease_id` | `tstr` | non-empty | Unique lease identifier |
| `prefix32` | `uint` | 0..2^32-1 | Nonce prefix (derived from key+node) |
| `start_ctr` | `uint` | 0..2^64-1 | Start of counter range |
| `end_ctr` | `uint` | 0..2^64-1 | End of counter range |
| `cur_ctr_at_issue` | `uint` | start<=cur<=end | Counter at lease issue |
| `issued_at` | `tstr` | RFC3339 UTC | Lease issue time |
| `expires_at` | `tstr` | RFC3339 UTC | Lease expiry time |
| `lease_evidence_sha256` | `tstr` | 64 hex chars | SHA-256(canonical CBOR of normalized lease) |

---

## 3. Lease Signature Evidence (`lease_sig`) — COSE Sign1 ES256

| Key | Type | Constraints | Description |
|---|---|---|---|
| `sig_alg` | `tstr` | MUST be `ES256` | Signature algorithm |
| `kid_hex` | `tstr` | lowercase hex (length >= 2) | Authority key id |
| `verified` | `tstr` | `PASS` or `FAIL` | Result of signature verification |
| `lease_token_sha256` | `tstr` | 64 hex chars | SHA-256(raw COSE_Sign1 bytes) |
| `lease_payload_sha256` | `tstr` | 64 hex chars | SHA-256(canonical CBOR payload map) |

---

## 4. Nonce Evidence (`nonce`)

| Key | Type | Constraints | Description |
|---|---|---|---|
| `aead_alg` | `tstr` | MUST be `AES-256-GCM` | AEAD suite |
| `nonce96_hex` | `tstr` | 24 hex chars (=12 bytes) | Nonce = prefix32||ctr64 |
| `nonce_prefix32` | `uint` | 0..2^32-1 | Prefix used |
| `nonce_ctr64` | `uint` | 0..2^64-1 | Counter used |
| `nonce_policy` | `tstr` | MUST be `range_lease_prefix32_ctr64_v1` | Policy id |
| `nonce_uniqueness_check` | `tstr` | `PASS` or `FAIL` | Dedup/monitor status |

---

## 5. Aggregates (`aggregates`)

| Key | Type | Constraints | Description |
|---|---|---|---|
| `vc1_agg_sha256` | `tstr` | 64 hex chars | VC-1 aggregate digest |
| `geo_agg_sha256` | `tstr` | 64 hex chars | Geometry aggregate digest |
| `aad_sha256` | `tstr` | 64 hex chars | SHA-256(AAD bytes) |

---

## 6. Commitment (`commitment`)

| Key | Type | Constraints | Description |
|---|---|---|---|
| `commit_alg` | `tstr` | MUST be `SHA-256` | Commitment algorithm |
| `commit_hex` | `tstr` | 64 hex chars | Commitment digest |

---

## 7. MAC (`mac`)

| Key | Type | Constraints | Description |
|---|---|---|---|
| `mac_alg` | `tstr` | MUST be `HMAC-SHA256` | MAC algorithm |
| `mac_tag_hex` | `tstr` | 64 hex chars | Tag |

---

## 8. Ciphertext (`ciphertext`)

| Key | Type | Constraints | Description |
|---|---|---|---|
| `ciphertext_sha256` | `tstr` | 64 hex chars | SHA-256(ciphertext bytes) |
| `ciphertext_len` | `uint` | >= 0 | Ciphertext length |

---

## 9. Trace (`trace`)

| Key | Type | Constraints | Description |
|---|---|---|---|
| `trace_sha256` | `tstr` | 64 hex chars | SHA-256(canonical CBOR trace object) |
| `trace_event_count` | `uint` | >= 0 | Trace event count |

---

## 10. HSM Evidence (`hsm`)

| Key | Type | Constraints | Description |
|---|---|---|---|
| `provider` | `tstr` | e.g. `pkcs11` / `kms` | Provider id |
| `handle` | `tstr` | non-empty | HSM label/handle or KMS key resource |
| `device_serial` | `tstr` | optional | HSM device serial |
| `profile` | `tstr` | `A` or `B` | Integration profile |
| `key_id_hex` | `tstr` | 64 hex chars | Must equal top-level key_id_hex |

---

## 11. Status (`status`)

| Key | Type | Constraints | Description |
|---|---|---|---|
| `state` | `tstr` | `HALT` or `TRAP` | Execution result |
| `err_code` | `uint` | 0 if HALT | Trap code |

---

## 12. Canonicalization & Hashing (Normative)

### 12.1 Canonical CBOR
All CBOR hashing MUST use **RFC 8949 Canonical CBOR**:
- definite-length encoding (no indefinite)
- map key ordering per RFC 8949 canonical rules (by key length, then bytewise)
- no floats in normative fields

### 12.2 event_sha256 definition
`event_sha256` MUST equal:
- `SHA-256( canonical_cbor(event_without_event_sha256) )`

The `event_sha256` field MUST NOT be included in the hashed object to avoid self-reference.

### 12.3 Digest strings
All digest strings MUST be lowercase hex, fixed-length:
- SHA-256: 64 hex chars
