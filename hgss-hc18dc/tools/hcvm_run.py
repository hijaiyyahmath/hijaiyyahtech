from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hgss.hcvm.vm import HCVM, Memory, MasterTables, LeaseEvidence, Trap


def load_words_json(path: str) -> bytes:
    """
    JSON format: {"words_hex": ["0x40000000", ...]} or {"words": [1073741824, ...]}
    Produces little-endian bytes stream.
    """
    obj = json.loads(open(path, "r", encoding="utf-8").read())
    if "words_hex" in obj:
        words = [int(x, 16) for x in obj["words_hex"]]
    else:
        words = [int(x) for x in obj["words"]]
    return b"".join(struct.pack("<I", w & 0xFFFFFFFF) for w in words)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--program-words-json", required=True, help="Path to words json (demo bytecode)")
    ap.add_argument("--lease-json", required=True, help="Lease evidence json (range leasing output)")
    ap.add_argument("--key-id-hex", required=True, help="key_id hex (public identifier)")
    ap.add_argument("--txid-hex", required=True, help="txid hex (public transaction id)")
    ap.add_argument("--node-id-hex", required=False, help="node_id hex (optional; usually in lease json)")
    ap.add_argument("--master-secret-hex", required=True, help="master secret hex (demo; in bank should be HSM)")
    ap.add_argument("--out-json", required=False, help="write result json")
    args = ap.parse_args()

    code = load_words_json(args.program_words_json)
    lease = LeaseEvidence.from_json(args.lease_json)

    key_id = bytes.fromhex(args.key_id_hex)
    txid = bytes.fromhex(args.txid_hex)
    master_secret = bytes.fromhex(args.master_secret_hex)

    # Demo master tables (for real, replace with dataset loaders bound to locks)
    tables = MasterTables.minimal_demo()

    mem = Memory(size=1 << 20)

    # Conventional addresses used by demo program
    TRX_PTR = 0x1000
    LEASE_PTR = 0x0800
    NONCE_PTR = 0x1200
    CT_PTR = 0x2000

    # Write lease struct into memory (prefix32, cur_ctr64, end_ctr64)
    mem.w_u32(LEASE_PTR + 0, int(lease.prefix32))
    mem.w_u64(LEASE_PTR + 8, int(lease.cur_ctr))
    mem.w_u64(LEASE_PTR + 16, int(lease.end_ctr))

    vm = HCVM(
        code=code,
        mem=mem,
        tables=tables,
        lease=lease,
        master_secret=master_secret,
        key_id=key_id,
        txid=txid,
    )

    # Initialize registers expected by demo:
    vm.S[0] = TRX_PTR
    vm.S[1] = LEASE_PTR
    vm.S[2] = NONCE_PTR
    vm.S[3] = CT_PTR

    try:
        vm.run()
    except Trap as t:
        out = {"status": "TRAP", "err": t.err, "msg": str(t)}
        print(json.dumps(out, ensure_ascii=False, indent=2))
        sys.exit(1)

    out = {
        "status": "HALT",
        "err": vm.ERR,
        "nonce12_hex": (vm.last_nonce12.hex() if vm.last_nonce12 else None),
        "commit_hex": vm.H[0].hex(),
        "tag_hex": vm.H[3].hex(),
        "vc1_agg_hex": vm.H[6].hex(),
        "geo_agg_hex": vm.H[7].hex(),
        "ciphertext_len": vm.S[12],
        "ciphertext_hex_prefix": (vm.last_ciphertext[:32].hex() if vm.last_ciphertext else None),
        "aad_sha256_hex": ( hashlib.sha256(vm.last_aad).hexdigest() if vm.last_aad else None ),
    }

    s = json.dumps(out, ensure_ascii=False, indent=2)
    print(s)
    if args.out_json:
        open(args.out_json, "w", encoding="utf-8").write(s + "\n")


if __name__ == "__main__":
    main()
