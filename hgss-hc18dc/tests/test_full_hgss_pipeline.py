from __future__ import annotations

import json
import struct
import hashlib
import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from hgss.hcvm.vm import HCVM, Memory, MasterTables, LeaseEvidence, Trap
from hgss.audit.auditlog import write_jsonl_event
from tools.hgss_verify_evidence import verify_event, build_hgss_aad


def words_to_bytes(words: list[int]) -> bytes:
    return b"".join(struct.pack("<I", w & 0xFFFFFFFF) for w in words)


def expected_prefix32(key_id: bytes, node_id: bytes) -> int:
    d = hashlib.sha256(b"HGSS|HC18DC|NONCE|v1|" + key_id + node_id).digest()
    return int.from_bytes(d[:4], "little")


def demo_program_words() -> list[int]:
    """
    This matches the demo semantics implemented in HCVM.
    We include S3 init via LDI_S to avoid external dependency.
    """
    def IW(op, rd=0, ra=0, rb=0, subop=0, imm8=0):
        return ((op & 0xFF)<<24)|((rd & 0xF)<<20)|((ra & 0xF)<<16)|((rb & 0xF)<<12)|((subop & 0xF)<<8)|(imm8 & 0xFF)

    SETFLAG0 = 0x30000000

    w = []
    # LDI_S S0, 0x1000
    w += [IW(0x40, rd=0), 0x00001000]
    # LDI_S S1, 0x0800
    w += [IW(0x40, rd=1), 0x00000800]
    # LDI_S S2, 0x1200
    w += [IW(0x40, rd=2), 0x00001200]
    # LDI_S S3, 0x2000 (ciphertext buffer)
    w += [IW(0x40, rd=3), 0x00002000]

    w += [IW(0x01)]        # VERIFY_LOCKS
    w += [IW(0x02, rd=0)]  # TRX_INIT uses S0

    # Record 1: ج index 4
    w += [IW(0x10, rd=0, imm8=4)]      # LDH_V18 V0,#4
    w += [IW(0x11, rd=0, imm8=4)]      # LDH_CSGI_H H0,#4
    w += [SETFLAG0]
    w += [IW(0x20, rd=0)]              # AUDIT_V18 V0 (Vs=Rd)
    w += [IW(0x12, rd=4, ra=0)]        # VC1 S4, V0
    w += [IW(0x03, ra=0, rb=0)]        # TRX_APPEND V0,H0

    # Record 2: ا index 0
    w += [IW(0x10, rd=0, imm8=0)]
    w += [IW(0x11, rd=0, imm8=0)]
    w += [SETFLAG0]
    w += [IW(0x20, rd=0)]
    w += [IW(0x12, rd=4, ra=0)]
    w += [IW(0x03, ra=0, rb=0)]

    # Record 3: م index 23
    w += [IW(0x10, rd=0, imm8=23)]
    w += [IW(0x11, rd=0, imm8=23)]
    w += [SETFLAG0]
    w += [IW(0x20, rd=0)]
    w += [IW(0x12, rd=4, ra=0)]
    w += [IW(0x03, ra=0, rb=0)]

    w += [IW(0x04)]  # TRX_FINALIZE
    w += [IW(0x05)]  # COMMIT_SHA256
    w += [IW(0x06)]  # KDF_HKDF
    w += [IW(0x07)]  # HMAC_SHA256
    w += [IW(0x50, rd=2, ra=1)]  # NONCE_NEXT dst=S2 lease=S1
    w += [IW(0x70)]  # AEAD_AESGCM_ENC
    w += [IW(0xFF)]  # HALT
    return w


def make_lease(tmp_path, key_id: bytes, node_id: bytes, start: int, end: int) -> str:
    prefix = expected_prefix32(key_id, node_id)
    lease = {
        "lease_id": "LEASE-TEST-001",
        "key_id_hex": key_id.hex(),
        "node_id_hex": node_id.hex(),
        "prefix32": prefix,
        "start_ctr": start,
        "end_ctr": end,
        "cur_ctr": start
    }
    p = tmp_path / "lease.json"
    p.write_text(json.dumps(lease, indent=2), encoding="utf-8")
    return str(p)


def run_once(code: bytes, lease_json: str, key_id: bytes, txid: bytes, master_secret: bytes) -> HCVM:
    lease = LeaseEvidence.from_json(lease_json)
    tables = MasterTables.minimal_demo()
    mem = Memory(size=1 << 20)

    TRX_PTR = 0x1000
    LEASE_PTR = 0x0800
    NONCE_PTR = 0x1200
    CT_PTR = 0x2000

    # inject lease struct into memory (input evidence for deterministic replay)
    mem.w_u32(LEASE_PTR + 0, lease.prefix32)
    mem.w_u64(LEASE_PTR + 8, lease.cur_ctr)
    mem.w_u64(LEASE_PTR + 16, lease.end_ctr)

    vm = HCVM(
        code=code,
        mem=mem,
        tables=tables,
        lease=lease,
        master_secret=master_secret,
        key_id=key_id,
        txid=txid,
    )
    vm.S[0] = TRX_PTR
    vm.S[1] = LEASE_PTR
    vm.S[2] = NONCE_PTR
    vm.S[3] = CT_PTR
    vm.run()
    return vm


def test_full_pipeline_cluster_range_lease_deterministic(tmp_path):
    key_id = bytes.fromhex("01" * 16)
    node_id = bytes.fromhex("02" * 16)
    txid = bytes.fromhex("aa" * 16)
    master_secret = bytes.fromhex("11" * 32)

    lease_json = make_lease(tmp_path, key_id, node_id, start=10, end=20)
    code = words_to_bytes(demo_program_words())

    vm1 = run_once(code, lease_json, key_id, txid, master_secret)
    vm2 = run_once(code, lease_json, key_id, txid, master_secret)

    # Deterministic replay: same inputs -> same outputs
    assert vm1.last_nonce12 == vm2.last_nonce12
    assert vm1.H[0] == vm2.H[0]  # commitment
    assert vm1.H[3] == vm2.H[3]  # tag
    assert vm1.last_ciphertext == vm2.last_ciphertext

    # Nonce must equal prefix||ctr where ctr=start=10
    prefix = expected_prefix32(key_id, node_id)
    expected_nonce = struct.pack("<I", prefix) + struct.pack("<Q", 10)
    assert vm1.last_nonce12 == expected_nonce

    # Lease counter was consumed -> in memory it becomes 11 (internal effect)

def test_lease_exhaustion_traps(tmp_path):
    key_id = bytes.fromhex("01" * 16)
    node_id = bytes.fromhex("02" * 16)
    txid = bytes.fromhex("aa" * 16)
    master_secret = bytes.fromhex("11" * 32)

    # start=end=5 => only one nonce available; but demo uses exactly one NONCE_NEXT, so ok
    lease_json_ok = make_lease(tmp_path, key_id, node_id, start=5, end=5)
    code = words_to_bytes(demo_program_words())
    vm_ok = run_once(code, lease_json_ok, key_id, txid, master_secret)
    assert vm_ok.last_nonce12.endswith(struct.pack("<Q", 5))

    # exhausted: cur_ctr set > end by crafting lease evidence
    prefix = expected_prefix32(key_id, node_id)
    bad = {
        "lease_id": "LEASE-BAD",
        "key_id_hex": key_id.hex(),
        "node_id_hex": node_id.hex(),
        "prefix32": prefix,
        "start_ctr": 5,
        "end_ctr": 5,
        "cur_ctr": 6
    }
    p = tmp_path / "lease_bad.json"
    p.write_text(json.dumps(bad, indent=2), encoding="utf-8")

    with pytest.raises(Trap) as e:
        run_once(code, str(p), key_id, txid, master_secret)
    assert e.value.err in (21, 22, 24, 25)

def test_audit_evidence_verification(tmp_path):
    key_id = bytes.fromhex("01" * 16)
    node_id = bytes.fromhex("02" * 16)
    txid = bytes.fromhex("aa" * 16)
    master_secret = bytes.fromhex("11" * 32)

    lease_json = make_lease(tmp_path, key_id, node_id, start=10, end=20)
    code = words_to_bytes(demo_program_words())

    vm = run_once(code, lease_json, key_id, txid, master_secret)

    # Construct event log
    event = {
        "mh28_sha256": "7393659dfe979cf85b1cf6293179f7ba1f49b4eedd1af19f002170148ce00380",
        "csgi28_sha256": "530845fbc3815ea9f02c75d44bda0e1aa096ec93729942d24d2d8bb0bd56c9d5",
        "key_id_hex": key_id.hex(),
        "txid_hex": txid.hex(),
        "lease": {
            "allocator_id": "ALLOC-001",
            "lease_id": "LEASE-TEST-001",
            "prefix32": vm.lease.prefix32,
            "start_ctr": vm.lease.start_ctr,
            "end_ctr": vm.lease.end_ctr,
            "cur_ctr_at_issue": vm.lease.cur_ctr,
        },
        "aggregates": {
            "vc1_agg_sha256": vm.H[6].hex(),
            "geo_agg_sha256": vm.H[7].hex(),
            "aad_sha256": hashlib.sha256(vm.last_aad).hexdigest(),
        },
        "ciphertext": {
            "ciphertext_sha256": hashlib.sha256(vm.last_ciphertext).hexdigest(),
            "length": vm.S[12]
        },
        "trace": {
            "trace_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # SHA-256 of empty CBOR list []
        }
    }

    log_path = tmp_path / "audit.jsonl"
    write_jsonl_event(str(log_path), event)

    # Verify event
    with open(log_path, "r", encoding="utf-8") as f:
        ev_loaded = json.loads(f.read())

    # Mocking trace file verification as empty trace for now
    ok, errs = verify_event(ev_loaded, ciphertext_hex=vm.last_ciphertext.hex())
    assert ok, f"Audit verification failed: {errs}"
