from __future__ import annotations

from hgss.crypto.hsm_pkcs11 import PKCS11KeyProvider, PKCS11Config

def test_hsm_provider_contract():
    p = PKCS11KeyProvider(PKCS11Config(slot=0, key_handle="HSM-KEY-01", device_serial="SERIAL-001"))
    k_aead, k_mac, ref = p.derive_keys(
        key_id=b"\x01"*16,
        vc1_agg=b"\x02"*32,
        geo_agg=b"\x03"*32,
        aead_alg="aesgcm",
    )
    assert len(k_aead) == 32
    assert len(k_mac) == 32
    assert ref.provider == "pkcs11"
    assert ref.handle == "HSM-KEY-01"
