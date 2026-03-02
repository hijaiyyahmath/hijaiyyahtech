# Nonce Range Leasing Protocol — HGSS-HCVM-v1.HC18DC (e392c68)

## 1) Overview
Nonce range leasing is the mechanism to ensure nonce uniqueness in a distributed HCVM cluster. 
A **Lease Authority** issues signed tokens granting a specific `node_id` a range of counters for a `key_id`.

## 2) Protocol Requirement (Normative)
- Every lease artifact MUST be wrapped in a **COSE_Sign1** envelope.
- The `prefix32` in the lease MUST match `SHA256(key_id || node_id)[:4]`.
- The `HCVM` MUST verify the signature against the Authority's public key before allowing `NONCE_NEXT`.

## 3) Replay Determinism
The signed lease token is recorded in the audit evidence. During forensic replay, the verifier uses the same token to ensure the counters and prefix match the original execution, maintaining 100% determinism.

## 4) Fail-Closed Policy
- **Signature Failure**: If the COSE signature is invalid, the VM MUST trigger `E_LEASE_SIGNATURE_INVALID` and HALT.
- **Expiration**: If the current system time exceeds `expires_at`, the VM MUST HALT.
- **Prefix Mismatch**: If the derived prefix does not match the token, the VM MUST HALT.
