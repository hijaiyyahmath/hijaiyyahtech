from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta

import cbor2
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

from hgss.nonce.lease_token import issue_lease_token_es256
from hgss.hcvm.vm import HCVM  # only to reuse prefix derivation if needed


def rfc3339(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output COSE_Sign1 token file (.cbor)")
    ap.add_argument("--key-id-hex", required=True)
    ap.add_argument("--node-id-hex", required=True)
    ap.add_argument("--lease-id", default="LEASE-0001")
    ap.add_argument("--allocator-id", default="lease-authority-demo")
    ap.add_argument("--start-ctr", type=int, default=10)
    ap.add_argument("--end-ctr", type=int, default=1000000)
    ap.add_argument("--kid-hex", default="a1"*8, help="authority signing key id (kid)")
    ap.add_argument("--privkey-pem", default=None, help="optional PEM private key; if missing, generate ephemeral")
    args = ap.parse_args()

    key_id = bytes.fromhex(args.key_id_hex)
    node_id = bytes.fromhex(args.node_id_hex)
    kid = bytes.fromhex(args.kid_hex)

    # Use same prefix32 derivation rule as HCVM
    prefix32 = HCVM.expected_prefix32(key_id, node_id)

    now = datetime.now(timezone.utc)
    payload = {
        "allocator_id": args.allocator_id,
        "lease_id": args.lease_id,
        "key_id_hex": key_id.hex(),
        "node_id_hex": node_id.hex(),
        "prefix32": int(prefix32),
        "start_ctr": int(args.start_ctr),
        "end_ctr": int(args.end_ctr),
        "cur_ctr_at_issue": int(args.start_ctr),
        "issued_at": rfc3339(now),
        "expires_at": rfc3339(now + timedelta(hours=24)),
    }

    if args.privkey_pem:
        pem = open(args.privkey_pem, "rb").read()
        priv = serialization.load_pem_private_key(pem, password=None)
        assert isinstance(priv, ec.EllipticCurvePrivateKey)
    else:
        priv = ec.generate_private_key(ec.SECP256R1())

    token = issue_lease_token_es256(payload, kid, priv)

    open(args.out, "wb").write(token)

    # Print public key PEM (auditor/verifier uses this)
    pub = priv.public_key()
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    print(pub_pem.decode("utf-8").strip())
    print(f"wrote: {args.out}")


if __name__ == "__main__":
    main()
