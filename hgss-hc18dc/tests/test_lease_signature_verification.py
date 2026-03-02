from __future__ import annotations

import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from hgss.nonce.lease_token import issue_lease_token_es256, verify_lease_token_es256

def test_lease_signature_verification_fail_on_tamper():
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    kid = b"kid-demo"

    payload = {
        "allocator_id": "auth",
        "lease_id": "L1",
        "key_id_hex": "01"*16,
        "node_id_hex": "02"*16,
        "prefix32": 123,
        "start_ctr": 10,
        "end_ctr": 20,
        "cur_ctr_at_issue": 10,
        "issued_at": "2026-02-26T00:00:00Z",
        "expires_at": "2026-02-27T00:00:00Z",
    }

    tok = issue_lease_token_es256(payload, kid, priv)
    ok = verify_lease_token_es256(tok, pub)
    assert ok.kid == kid

    # Tamper: flip one byte in token (signature must fail)
    tampered = bytearray(tok)
    tampered[-1] ^= 0x01

    with pytest.raises(ValueError) as e:
        verify_lease_token_es256(bytes(tampered), pub)
    assert "LEASE_SIGNATURE_INVALID" in str(e.value)
