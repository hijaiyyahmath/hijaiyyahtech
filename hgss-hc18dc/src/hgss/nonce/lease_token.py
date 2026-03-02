from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Tuple

import cbor2
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)
from cryptography.exceptions import InvalidSignature


COSE_ALG_ES256 = -7  # ES256
COSE_HDR_ALG = 1     # label
COSE_HDR_KID = 4     # label

def cbor_canon(obj: Any) -> bytes:
    return cbor2.dumps(obj, canonical=True)

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def ecdsa_der_to_raw_p256(sig_der: bytes) -> bytes:
    r, s = decode_dss_signature(sig_der)
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")

def ecdsa_raw_to_der_p256(sig_raw: bytes) -> bytes:
    if len(sig_raw) != 64:
        raise ValueError("SIG_RAW_LEN")
    r = int.from_bytes(sig_raw[:32], "big")
    s = int.from_bytes(sig_raw[32:], "big")
    return encode_dss_signature(r, s)

def cose_sig_structure(protected_bstr: bytes, payload_bstr: bytes) -> bytes:
    # Sig_structure = ["Signature1", protected, external_aad, payload]
    external_aad = b""
    return cbor_canon(["Signature1", protected_bstr, external_aad, payload_bstr])

@dataclass(frozen=True)
class LeaseTokenVerified:
    payload_map: Dict[str, Any]
    kid: bytes
    alg: int
    payload_sha256: str
    token_sha256: str

def decode_cose_sign1(token: bytes) -> Tuple[bytes, Dict[str, Any], bytes, bytes]:
    """
    Returns (protected_bstr, unprotected_map, payload_bstr, signature_bstr_raw).
    token = CBOR array of 4 items.
    """
    arr = cbor2.loads(token)
    if not (isinstance(arr, list) and len(arr) == 4):
        raise ValueError("COSE_SIGN1_FORMAT")
    protected = arr[0]
    unprotected = arr[1]
    payload = arr[2]
    signature = arr[3]
    if not isinstance(protected, (bytes, bytearray)):
        raise ValueError("COSE_PROTECTED_NOT_BSTR")
    if not isinstance(unprotected, dict):
        raise ValueError("COSE_UNPROTECTED_NOT_MAP")
    if not isinstance(payload, (bytes, bytearray)):
        raise ValueError("COSE_PAYLOAD_NOT_BSTR")
    if not isinstance(signature, (bytes, bytearray)):
        raise ValueError("COSE_SIG_NOT_BSTR")
    return bytes(protected), dict(unprotected), bytes(payload), bytes(signature)

def verify_lease_token_es256(token: bytes, pubkey: ec.EllipticCurvePublicKey) -> LeaseTokenVerified:
    protected_bstr, unprot, payload_bstr, sig_raw = decode_cose_sign1(token)

    protected_map = cbor2.loads(protected_bstr) if protected_bstr else {}
    if not isinstance(protected_map, dict):
        raise ValueError("COSE_PROTECTED_BAD")

    alg = protected_map.get(COSE_HDR_ALG)
    kid = protected_map.get(COSE_HDR_KID, b"")
    if alg != COSE_ALG_ES256:
        raise ValueError("COSE_ALG_NOT_ES256")
    if not isinstance(kid, (bytes, bytearray)):
        raise ValueError("COSE_KID_BAD")
    kid_b = bytes(kid)

    # Verify signature (COSE uses raw signature (r||s); cryptography expects DER)
    sig_der = ecdsa_raw_to_der_p256(sig_raw)
    msg = cose_sig_structure(protected_bstr, payload_bstr)
    try:
        pubkey.verify(sig_der, msg, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature:
        raise ValueError("LEASE_SIGNATURE_INVALID")

    payload_map = cbor2.loads(payload_bstr)
    if not isinstance(payload_map, dict):
        raise ValueError("LEASE_PAYLOAD_NOT_MAP")

    return LeaseTokenVerified(
        payload_map=dict(payload_map),
        kid=kid_b,
        alg=int(alg),
        payload_sha256=sha256_hex(cbor_canon(payload_map)),
        token_sha256=sha256_hex(token),
    )

def issue_lease_token_es256(payload_map: Dict[str, Any], kid: bytes, privkey: ec.EllipticCurvePrivateKey) -> bytes:
    protected_map = {COSE_HDR_ALG: COSE_ALG_ES256, COSE_HDR_KID: kid}
    protected_bstr = cbor_canon(protected_map)
    unprotected_map: Dict[str, Any] = {}
    payload_bstr = cbor_canon(payload_map)

    msg = cose_sig_structure(protected_bstr, payload_bstr)
    sig_der = privkey.sign(msg, ec.ECDSA(hashes.SHA256()))
    sig_raw = ecdsa_der_to_raw_p256(sig_der)

    token = [protected_bstr, unprotected_map, payload_bstr, sig_raw]
    return cbor_canon(token)
