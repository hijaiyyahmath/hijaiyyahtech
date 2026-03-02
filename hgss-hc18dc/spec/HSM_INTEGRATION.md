# HSM Integration — HGSS-HCVM-v1.HC18DC (e392c68)

## 1) Goal
Key material MUST be managed by HSM/KMS. Host MUST NOT persist plaintext master secret.

## 2) KeyProvider Contract (Normative)
System MUST obtain AEAD/MAC keys via KeyProvider:
- derive_keys(key_id, vc1_agg, geo_agg, aead_alg) -> (k_aead32, k_mac32, key_ref)

Key lengths MUST be 32 bytes each.

## 3) Production Profiles
- Profile A (pragmatic): HSM derives and exports session keys (RAM-only).
- Profile B (strict): HSM performs AEAD/HMAC, keys never leave.

## 4) Audit Requirements
Audit event MUST contain:
- key_ref.provider
- key_ref.handle (HSM label/id or KMS resource id)
- key_id
No secret key bytes may be logged.
