# Monitoring & Incident Response Runbook — HGSS-HCVM-v1.HC18DC (e392c68)

Status: OPERATIONAL (Banking-grade runbook)

## 0) Objective
Mencegah dan merespons kejadian fatal bagi AES-GCM:
- nonce reuse / collision
- lease authority compromise
- lease exhaustion bursts
- signature verification failures

## 1) Key Metrics (MUST)
### 1.1 Nonce Uniqueness
- Count of (key_id, nonce96) duplicates — MUST be 0
- Rate of nonce allocations per node/prefix32
- Lease consumption rate and remaining counters in active lease

### 1.2 Lease Authority Signature
- Signature verification failures (PASS/FAIL)
- Expired lease attempts
- Unknown kid usage

### 1.3 Crypto Health
- AEAD decrypt failures (tag mismatch)
- HMAC verification failures
- Dataset lock mismatches

### 1.4 System Health
- Lease service latency, error rate
- DB lock contention / CAS retry rate
- WORM storage write failures

## 2) Alerting (Recommended)
Severity levels:
- SEV1: nonce duplicate detected OR confirmed nonce reuse
- SEV1: lease authority signing key compromise suspected
- SEV2: sustained signature failures or lease expiry spikes
- SEV2: leasing service down / cannot allocate nonces
- SEV3: transient errors / elevated retries

## 3) SEV1 Response — Nonce Duplicate / Reuse
Immediate actions:
1. Freeze encryption for affected key_id (stop issuing ciphertext)
2. Rotate key_id (new derived keys)
3. Quarantine nodes involved (node_id)
4. Preserve evidence:
   - auditlog events around incident window
   - lease records, lease tokens, trace digests
5. Forensics:
   - determine if duplication came from:
     - lease overlap (allocator bug)
     - node rollback (durability failure)
     - forged lease token (signature bypass)
6. Post-incident:
   - revoke affected lease_id ranges
   - patch allocator / durability mechanism
   - publish incident report for compliance

## 4) SEV1 Response — Lease Authority Compromise
Immediate actions:
1. Revoke authority signing key (kid) in verifier trust store
2. Rotate signing key in HSM/KMS
3. Reject all leases signed by compromised kid (fail closed)
4. Re-issue leases with new kid
5. Audit:
   - search for events with kid==compromised
   - validate integrity of lease_token_sha256 logs

## 5) SEV2 Response — Leasing Exhaustion / Service Outage
Actions:
- Increase block_size (temporary) if safe
- Add capacity to lease service
- Switch allocator pattern if lock contention severe (pessimistic -> CAS) with change control

## 6) Evidence Queries (Operational)
For any incident, the minimum evidence queries:
- Find duplicates: GROUP BY (key_id, nonce96) HAVING COUNT(*)>1
- Find signature failures: lease_sig.verified == FAIL
- Find dataset lock failures: dataset_lock_check != PASS
- Find decrypt/tag failures (if logged)

## 7) Post-incident Controls
- Add invariant checks in CI gates
- Add canary tests for lease overlap
- Improve durability of cur_ctr persistence
- WORM retention policy verification
