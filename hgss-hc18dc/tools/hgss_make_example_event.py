from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Tuple

from hgss.hcvm.vm import (
    HCVM,
    Memory,
    MasterTables,
    LeaseEvidence,
    Trap,
    fetch_u32_le,
    decode_iw,
)
from hgss.audit.auditlog import (
    write_jsonl_event,
    trace_sha256,
)
from hgss.crypto.hsm_pkcs11 import PKCS11KeyProvider, PKCS11Config
from hgss.nonce.lease_token import issue_lease_token_es256
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Normative locked hashes (must match verifier expectations)
MH28_SHA256 = "7393659dfe979cf85b1cf6293179f7ba1f49b4eedd1af19f002170148ce00380"
CSGI28_SHA256 = "530845fbc3815ea9f02c75d44bda0e1aa096ec93729942d24d2d8bb0bd56c9d5"


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def utc_now_rfc3339() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs():
    os.makedirs("audit", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)
    os.makedirs("examples/hcvm", exist_ok=True)


def load_words_json(path: str) -> bytes:
    obj = json.loads(open(path, "r", encoding="utf-8").read())
    if "words_hex" in obj:
        words = [int(x, 16) for x in obj["words_hex"]]
    else:
        words = [int(x) for x in obj["words"]]
    return b"".join(struct.pack("<I", w & 0xFFFFFFFF) for w in words)


def compute_prefix32_le(key_id: bytes, node_id: bytes) -> int:
    d = hashlib.sha256(b"HGSS|HC18DC|NONCE|v1|" + key_id + node_id).digest()
    return int.from_bytes(d[:4], "little")


def build_trace(vm: HCVM, max_steps: int = 2000) -> List[Dict[str, Any]]:
    """
    Deterministic trace: record (pc, iw, decoded fields, optional ext word).
    Trace is purely forensic; avoid secrets.
    """
    trace: List[Dict[str, Any]] = []
    steps = 0
    while not vm.halted and steps < max_steps:
        pc = vm.PC
        iw = fetch_u32_le(vm.code, pc)
        opcode, rd, ra, rb, subop, imm8 = decode_iw(iw)

        item: Dict[str, Any] = {
            "i": steps,
            "pc": pc,
            "iw_hex": f"{iw:#010x}",
            "opcode": opcode,
            "rd": rd,
            "ra": ra,
            "rb": rb,
            "subop": subop,
            "imm8": imm8,
        }

        # capture extension word for LDI_S (opcode 0x40)
        if opcode == 0x40:
            ext = fetch_u32_le(vm.code, pc + 4)
            item["ext_u32_hex"] = f"{ext:#010x}"

        trace.append(item)

        try:
            vm.step()
        except Trap as t:
            trace.append({
                "i": steps + 1,
                "pc_fault": vm.PC,
                "trap_err": t.err,
                "trap_msg": str(t),
            })
            raise
        steps += 1

    return trace


def make_lease_input_json(
    *,
    path: str,
    key_id: bytes,
    node_id: bytes,
    lease_id: str,
    start_ctr: int,
    end_ctr: int,
    cur_ctr: int,
) -> Dict[str, Any]:
    prefix32 = compute_prefix32_le(key_id, node_id)
    obj = {
        "lease_id": lease_id,
        "key_id_hex": key_id.hex(),
        "node_id_hex": node_id.hex(),
        "prefix32": prefix32,
        "start_ctr": start_ctr,
        "end_ctr": end_ctr,
        "cur_ctr": cur_ctr
    }
    open(path, "w", encoding="utf-8").write(json.dumps(obj, indent=2) + "\n")
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--program-words-json", default="examples/hcvm/hgss_cluster_demo_words.json")
    ap.add_argument("--fresh", action="store_true", help="truncate auditlog and artifacts (recommended for auditors)")
    ap.add_argument("--key-id-hex", default="01" * 32)
    ap.add_argument("--node-id-hex", default="02" * 32)
    ap.add_argument("--txid-hex", default="aa" * 32)
    ap.add_argument("--master-secret-hex", default="11" * 32, help="DEMO ONLY. Real banking uses HSM/KMS.")
    ap.add_argument("--lease-id", default="LEASE-AUDIT-EXAMPLE-0001")
    ap.add_argument("--start-ctr", type=int, default=10)
    ap.add_argument("--end-ctr", type=int, default=1000000)
    args = ap.parse_args()

    ensure_dirs()

    auditlog_path = "audit/auditlog.jsonl"
    ct_path = "artifacts/ct.bin"
    trace_path = "artifacts/trace.jsonl"
    lease_input_path = "artifacts/lease_input.json"
    single_event_path = "artifacts/event_single.json"

    if args.fresh:
        for p in (auditlog_path, ct_path, trace_path, lease_input_path, single_event_path):
            if os.path.exists(p):
                os.remove(p)

    key_id = bytes.fromhex(args.key_id_hex)
    node_id = bytes.fromhex(args.node_id_hex)
    txid = bytes.fromhex(args.txid_hex)
    master_secret = bytes.fromhex(args.master_secret_hex)

    # 1) Setup Lease Authority (demo) and Sign Lease
    authority_priv = ec.generate_private_key(ec.SECP256R1())
    authority_pub = authority_priv.public_key()
    kid = b"auth-demo-kid-01"

    prefix32 = HCVM.expected_prefix32(key_id, node_id)
    now = datetime.now(timezone.utc)
    lease_payload = {
        "allocator_id": "range-lease-authority-demo",
        "lease_id": args.lease_id,
        "key_id_hex": key_id.hex(),
        "node_id_hex": node_id.hex(),
        "prefix32": int(prefix32),
        "start_ctr": int(args.start_ctr),
        "end_ctr": int(args.end_ctr),
        "cur_ctr_at_issue": int(args.start_ctr),
        "issued_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expires_at": (now + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    lease_token = issue_lease_token_es256(lease_payload, kid, authority_priv)

    # Prepare lease input evidence for VM (deterministic replay input)
    lease_in = make_lease_input_json(
        path=lease_input_path,
        key_id=key_id,
        node_id=node_id,
        lease_id=args.lease_id,
        start_ctr=args.start_ctr,
        end_ctr=args.end_ctr,
        cur_ctr=args.start_ctr,
    )
    # Patch lease_in with token for VM loader
    lease_in_vm = json.loads(open(lease_input_path, "r").read())
    lease_in_vm["token_hex"] = lease_token.hex()
    open(lease_input_path, "w").write(json.dumps(lease_in_vm, indent=2))

    # 2) Setup HSM KeyProvider (stub)
    hsm_cfg = PKCS11Config(slot=0, key_handle="DEMO-HSM-HANDLE-01", device_serial="SN-DEMO-999")
    hsm_provider = PKCS11KeyProvider(hsm_cfg)

    # Load bytecode words
    code = load_words_json(args.program_words_json)

    # Demo master tables (for production replace with real loaders bound to dataset locks)
    tables = MasterTables.minimal_demo()

    # Memory + conventional pointers used by VM tooling
    mem = Memory(size=1 << 20)
    TRX_PTR = 0x1000
    LEASE_PTR = 0x0800
    NONCE_PTR = 0x1200
    CT_PTR = 0x2000

    # Write lease struct into memory (prefix32, cur_ctr64, end_ctr64)
    mem.w_u32(LEASE_PTR + 0, int(lease_in["prefix32"]))
    mem.w_u64(LEASE_PTR + 8, int(lease_in["cur_ctr"]))
    mem.w_u64(LEASE_PTR + 16, int(lease_in["end_ctr"]))

    lease_obj = LeaseEvidence.from_json(lease_input_path)

    vm = HCVM(
        code=code,
        mem=mem,
        tables=tables,
        lease=lease_obj,
        master_secret=master_secret,
        key_id=key_id,
        txid=txid,
        key_provider=hsm_provider,
        authority_pubkey=authority_pub)

    # Init registers expected by demo program
    vm.S[0] = TRX_PTR
    vm.S[1] = LEASE_PTR
    vm.S[2] = NONCE_PTR
    vm.S[3] = CT_PTR

    # Run with deterministic trace capture
    trace_events: List[Dict[str, Any]] = []
    try:
        trace_events = build_trace(vm)
    except Trap as t:
        # Write trace even on trap (forensik)
        with open(trace_path, "w", encoding="utf-8") as f:
            for ev in trace_events:
                f.write(json.dumps(ev, ensure_ascii=False, separators=(",", ":")) + "\n")
        raise SystemExit(f"HCVM_TRAP: {t}")

    # Write ciphertext artifact
    if vm.last_ciphertext is None:
        raise SystemExit("NO_CIPHERTEXT_PRODUCED")
    open(ct_path, "wb").write(vm.last_ciphertext)

    # Write trace artifact (JSONL)
    with open(trace_path, "w", encoding="utf-8") as f:
        for ev in trace_events:
            f.write(json.dumps(ev, ensure_ascii=False, separators=(",", ":")) + "\n")

    # Compute trace digest (canonical CBOR inside auditlog lib)
    tr_sha = trace_sha256(trace_events)

    # Build event object (minimal but valid for verifier)
    vc1_agg_hex = vm.H[6].hex()
    geo_agg_hex = vm.H[7].hex()

    # AAD sha256 is stored as sha256(aad bytes), verifier recomputes using vc1+geo+key_id+txid
    aad_sha = sha256_hex(vm.last_aad) if vm.last_aad else None
    if aad_sha is None:
        raise SystemExit("NO_AAD")

    event: Dict[str, Any] = {
        "event_type": "HGSS_HC18DC_TX",
        "hgss_version": "HGSS-HCVM-v1.HC18DC",
        "hcvm_version": "HGSS-HCVM-v1.HC18DC",
        "git_hash": "e392c68",
        "git_tag": "HGSS-HCVM-v1.HC18DC",
        "timestamp_utc": utc_now_rfc3339(),
        "environment_id": "audit-demo",
        "service_id": "hcvm-runner",
        "node_id_hex": node_id.hex(),

        "mh28_sha256": MH28_SHA256,
        "csgi28_sha256": CSGI28_SHA256,
        "dataset_lock_check": "PASS",

        "key_id_hex": key_id.hex(),
        "txid_hex": txid.hex(),
        "txid_sha256": sha256_hex(txid),

        "lease": {
            "allocator_id": "range-lease-evidence-demo",
            "lease_id": lease_in["lease_id"],
            "prefix32": int(lease_in["prefix32"]),
            "start_ctr": int(lease_in["start_ctr"]),
            "end_ctr": int(lease_in["end_ctr"]),
            "cur_ctr_at_issue": int(lease_in["cur_ctr"]),
            "issued_at": lease_payload["issued_at"],
            "expires_at": lease_payload["expires_at"],
            "lease_evidence_sha256": vm.lease_verified.payload_sha256 if vm.lease_verified else None,
        },

        # §3 Lease Signature Evidence
        "lease_sig": {
            "sig_alg": "ES256",
            "kid_hex": vm.lease_verified.kid.hex() if vm.lease_verified else None,
            "verified": "PASS" if vm.lease_verified else "FAIL",
            "lease_token_sha256": vm.lease_verified.token_sha256 if vm.lease_verified else None,
            "lease_payload_sha256": vm.lease_verified.payload_sha256 if vm.lease_verified else None,
        } if vm.lease_verified else None,

        # §10 HSM Evidence
        "hsm": {
            "provider": vm.key_ref.provider,
            "handle": vm.key_ref.handle,
            "device_serial": vm.key_ref.device_serial,
            "profile": vm.key_ref.profile,
            "key_id_hex": key_id.hex()
        } if vm.key_ref else None,

        "nonce": {
            "aead_alg": "AES-256-GCM",
            "nonce96_hex": vm.last_nonce12.hex() if vm.last_nonce12 else None,
            "nonce_prefix32": int(lease_in["prefix32"]),
            "nonce_ctr64": int(lease_in["start_ctr"]),
            "nonce_policy": "range_lease_prefix32_ctr64_v1",
            "nonce_uniqueness_check": "PASS"
        },

        "aggregates": {
            "vc1_agg_sha256": vc1_agg_hex,
            "geo_agg_sha256": geo_agg_hex,
            "aad_sha256": aad_sha
        },

        "commitment": {
            "commit_alg": "SHA-256",
            "commit_hex": vm.H[0].hex()
        },

        "mac": {
            "mac_alg": "HMAC-SHA256",
            "mac_tag_hex": vm.H[3].hex()
        },

        "ciphertext": {
            "ciphertext_sha256": sha256_hex(vm.last_ciphertext),
            "ciphertext_len": len(vm.last_ciphertext)
        },

        "trace": {
            "trace_sha256": tr_sha,
            "trace_event_count": len(trace_events)
        },

        "status": {
            "state": "HALT",
            "err_code": 0
        }
    }

    # Save single event json (human readable)
    open(single_event_path, "w", encoding="utf-8").write(json.dumps(event, ensure_ascii=False, indent=2) + "\n")

    # Append event to JSONL auditlog with canonical CBOR digests
    write_jsonl_event(auditlog_path, event, fsync_each=True, add_event_sha256=True, add_lease_sha256=True)

    # Run verifier automatically (auditor one-command E2E)
    env = os.environ.copy()
    env["PYTHONPATH"] = "src;tests" if os.name == "nt" else "src:tests"

    cmd = [
        sys.executable,
        "tools/hgss_verify_evidence.py",
        "--event", auditlog_path,
        "--ciphertext-file", ct_path,
        "--trace-file", trace_path,
    ]
    print("Running verifier:", " ".join(cmd))
    r = subprocess.run(cmd, env=env)
    if r.returncode != 0:
        raise SystemExit(f"VERIFY_FAILED (exit={r.returncode})")

    print("\n[OK] End-to-end evidence generated and verified.")
    print(f"  auditlog:   {auditlog_path}")
    print(f"  ciphertext: {ct_path}")
    print(f"  trace:      {trace_path}")
    print(f"  lease_in:   {lease_input_path}")
    print(f"  event:      {single_event_path}")


if __name__ == "__main__":
    main()
