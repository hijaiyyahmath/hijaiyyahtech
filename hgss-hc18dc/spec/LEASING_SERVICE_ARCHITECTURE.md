# Leasing Service Architecture (Nonce Range Leasing 2b) — HGSS-HCVM-v1.HC18DC (e392c68)

Status: NORMATIVE (Production Spec)

## 0) Scope
Dokumen ini mendefinisikan arsitektur layanan **Range Leasing** untuk nonce AES-GCM (HGSS/HC18DC),
termasuk DB schema dan pola alokasi atomik.

## 1) Nonce Model (Normative)
Nonce96 = prefix32 || ctr64

- prefix32 = Trunc32_LE(SHA-256("HGSS|HC18DC|NONCE|v1|" || key_id || node_id))
- ctr64 dialokasikan dalam range [start_ctr..end_ctr] melalui lease service.

Uniqueness MUST hold per (key_id, prefix32).

## 2) Lease Token (Normative)
Layanan leasing MUST mengeluarkan lease sebagai:
- lease payload (canonical CBOR map) + COSE_Sign1 ES256 signature (Lease Authority)
atau
- lease payload + signature bukti setara (jika disetujui security office).
HGSS verifier MUST fail-closed jika signature invalid/expired.

## 3) Database Schema (Reference, Normative Fields)
### 3.1 Table: `nonce_counters`
Stores high-water mark per (key_id, prefix32).

Columns (suggested):
- key_id (BINARY(32) or VARBINARY) NOT NULL
- prefix32 (INT UNSIGNED) NOT NULL
- next_ctr64 (BIGINT UNSIGNED) NOT NULL
- updated_at (TIMESTAMP) NOT NULL
PRIMARY KEY (key_id, prefix32)

### 3.2 Table: `nonce_leases`
Stores issued lease ranges.

Columns:
- lease_id (UUID) PRIMARY KEY
- key_id (BINARY/VARBINARY) NOT NULL
- node_id (BINARY/VARBINARY) NOT NULL
- prefix32 (INT UNSIGNED) NOT NULL
- start_ctr64 (BIGINT UNSIGNED) NOT NULL
- end_ctr64 (BIGINT UNSIGNED) NOT NULL
- cur_ctr_at_issue (BIGINT UNSIGNED) NOT NULL
- issued_at (TIMESTAMP) NOT NULL
- expires_at (TIMESTAMP) NOT NULL
- status (ENUM: ACTIVE, EXPIRED, REVOKED) NOT NULL
- lease_token_sha256 (CHAR(64)) NOT NULL
- lease_payload_sha256 (CHAR(64)) NOT NULL

Index:
- (key_id, prefix32, issued_at)
- (node_id, status)

## 4) Atomic Allocation Patterns
### 4.1 Pattern A — Pessimistic Locking (Recommended default for banking)
Transaction (SQL sketch):
1. BEGIN;
2. SELECT next_ctr64 FROM nonce_counters
   WHERE key_id=? AND prefix32=? FOR UPDATE;
3. start = next_ctr64
4. end = start + block_size - 1
5. UPDATE nonce_counters SET next_ctr64 = end+1, updated_at=NOW()
   WHERE key_id=? AND prefix32=?;
6. INSERT nonce_leases(... start,end,issued_at,expires_at,status=ACTIVE, ...)
7. COMMIT;

Properties:
- Simple, strong uniqueness guarantee.
- Throughput depends on contention per (key_id,prefix32).

### 4.2 Pattern B — Optimistic / CAS (Allowed if DB supports)
Requires compare-and-swap:
- UPDATE nonce_counters SET next_ctr64 = new
  WHERE key_id=? AND prefix32=? AND next_ctr64 = old;
Retry loop on conflict.

Properties:
- Higher throughput under contention.
- More complex; MUST have bounded retries + metrics.

## 5) Block Size Policy (Operational Guidance)
Block size MUST be chosen so that:
- lease refresh overhead is low,
- blast radius of node crash is acceptable (burn remaining range).
Common choices: 1e6 or 1e7 counters per lease.

## 6) Crash & Burn Policy (Normative)
Banking-grade default:
- On crash, remaining ctr in lease MUST be considered burned unless monotonic durable state is proven.
- Lease service MUST support REVOKE on incident response.

## 7) Audit Requirements
Every lease issuance MUST be logged (append-only) with:
- lease_id, key_id, node_id, prefix32, start_ctr64, end_ctr64, issued_at, expires_at, status
- lease_token_sha256, lease_payload_sha256
- authority kid + signature verification result (PASS)

## 8) Security Boundaries
- Lease Authority signing key MUST be stored in HSM/KMS.
- DB credentials MUST be least-privilege.
- Lease service MUST have SLO/availability; nonce allocation failure is a hard-block for encryption.
