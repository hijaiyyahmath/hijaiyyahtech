from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

import hashlib

from hgss.crypto.key_provider import KeyProvider, KeyRef, AeadAlg

@dataclass
class PKCS11Config:
    slot: int
    key_handle: str
    device_serial: str = ""
    profile: str = "A"

class PKCS11KeyProvider(KeyProvider):
    """
    STUB for real HSM:
    - Replace with python-pkcs11/PyKCS11 calls.
    - Recommended real mechanism: HMAC-SHA256 inside HSM to implement HKDF.
    """
    def __init__(self, cfg: PKCS11Config):
        self.cfg = cfg

    def derive_keys(self, *, key_id: bytes, vc1_agg: bytes, geo_agg: bytes, aead_alg: AeadAlg) -> Tuple[bytes, bytes, KeyRef]:
        # Placeholder deterministic derivation (NOT secure as HSM); only to satisfy contract in tests.
        info = b"|".join([
            b"HC18DC", b"KDF", b"v1.0",
            aead_alg.encode("ascii"),
            b"KEYID=" + key_id,
            b"VC1=" + vc1_agg,
            b"GEO=" + geo_agg,
            b"HANDLE=" + self.cfg.key_handle.encode("utf-8"),
        ])
        okm = hashlib.sha256(b"PKCS11_STUB_A|" + info).digest() + hashlib.sha256(b"PKCS11_STUB_B|" + info).digest()
        k_aead = okm[:32]
        k_mac  = okm[32:64]
        ref = KeyRef(
            provider="pkcs11",
            key_id=key_id,
            handle=self.cfg.key_handle,
            device_serial=self.cfg.device_serial,
            profile=self.cfg.profile
        )
        return k_aead, k_mac, ref
