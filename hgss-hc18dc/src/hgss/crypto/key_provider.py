from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Literal, Tuple

AeadAlg = Literal["aesgcm", "chacha20poly1305"]

@dataclass(frozen=True)
class KeyRef:
    provider: str          # "pkcs11" / "kms" / etc
    key_id: bytes          # logical key_id (public identifier)
    handle: str            # HSM label/handle or KMS resource id
    device_serial: str = ""  # optional
    profile: str = "A"       # "A" export session keys, "B" HSM does crypto

class KeyProvider(Protocol):
    def derive_keys(
        self,
        *,
        key_id: bytes,
        vc1_agg: bytes,
        geo_agg: bytes,
        aead_alg: AeadAlg
    ) -> Tuple[bytes, bytes, KeyRef]:
        """
        Return (k_aead32, k_mac32, key_ref).
        MUST be deterministic for same inputs *within the same key version*.
        Secrets MUST NOT be logged by provider.
        """
        ...
