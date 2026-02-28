#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import re
import hashlib
from typing import List, Tuple

import rfc8785

HEX_RE = re.compile(r"^[0-9a-fA-F]*$")

DIR_AXIS_DEFAULT = [0, 9, 2, 10, 4, 1, 3, 8]

def fail(msg: str) -> None:
    print("FAIL:", msg)
    raise SystemExit(1)

def ok(msg: str) -> None:
    print("[OK]", msg)

def hex_to_bytes(h: str) -> bytes:
    h = h.strip()
    if len(h) % 2 != 0:
        fail("hex length must be even")
    if not HEX_RE.match(h):
        fail("hex contains non-hex characters")
    return bytes.fromhex(h)

def bytes_to_hex(b: bytes) -> str:
    return b.hex()

def jcs_string(obj) -> str:
    # RFC8785 canonical JSON string
    return rfc8785.dumps(obj).decode("utf-8")

# -----------------------------
# HC18DC-ENC v0.1 Reference
# -----------------------------

def rot4(x: int, d: int) -> int:
    return (x + d) & 3

def encode_byte(b: int) -> List[str]:
    d0 = b % 8
    d1 = (b // 8) % 8
    d2 = (b // 64) % 8
    return [f"D{d0}", f"D{d1}", f"D{d2}", "TURN+Q1"]

def apply_token(C: List[int], token: str, dir_axis: List[int]) -> None:
    if token.startswith("D"):
        k = int(token[1])
        axis = dir_axis[k]
        C[axis] = rot4(C[axis], 1)
        return
    if token == "TURN+Q1":
        C[0] = rot4(C[0], 1)
        return
    fail(f"Token not allowed in ENC v0.1: {token}")

def apply_trace(C: List[int], tokens: List[str], dir_axis: List[int]) -> None:
    for t in tokens:
        apply_token(C, t, dir_axis)

def pack36(C: List[int]) -> int:
    v = 0
    for i in range(18):
        v |= (C[i] & 3) << (2 * i)
    return v  # 36-bit int

def extract8(v36: int, start: int) -> int:
    # start in 0..35
    out = 0
    for j in range(8):
        bit_index = (start + j) % 36
        bit = (v36 >> bit_index) & 1
        out |= (bit << j)
    return out  # 0..255

def keystream_byte(C: List[int], t: int, dir_axis: List[int]) -> int:
    v = pack36(C)
    start = (5 * t) % 36
    ks = extract8(v, start)
    # advance state deterministically
    apply_token(C, f"D{t % 8}", dir_axis)
    return ks

def init_state(key32: bytes, nonce24: bytes, dir_axis: List[int]) -> List[int]:
    if len(key32) != 32:
        fail("key_master must be 32 bytes")
    if len(nonce24) != 24:
        fail("nonce must be 24 bytes")

    C = [0] * 18
    # absorb key
    for b in key32:
        apply_trace(C, encode_byte(b), dir_axis)
    # absorb nonce
    for b in nonce24:
        apply_trace(C, encode_byte(b), dir_axis)
    return C

def encrypt_record_bytes(plaintext: bytes, key32: bytes, nonce24: bytes, dir_axis: List[int]) -> Tuple[bytes, bytes]:
    C = init_state(key32, nonce24, dir_axis)

    ct = bytearray(len(plaintext))
    for i, p in enumerate(plaintext):
        ks = keystream_byte(C, i, dir_axis)
        ct[i] = p ^ ks
        # duplex absorb plaintext byte
        apply_trace(C, encode_byte(p), dir_axis)

    # finalization fixed: 4x TURN+Q1
    apply_trace(C, ["TURN+Q1"] * 4, dir_axis)

    # tag 16 bytes
    tag = bytearray(16)
    n = len(plaintext)
    for j in range(16):
        tag[j] = keystream_byte(C, n + j, dir_axis)

    return bytes(ct), bytes(tag)

# -----------------------------
# Runner
# -----------------------------

def run(tv_path: str) -> None:
    tv = json.load(open(tv_path, "r", encoding="utf-8"))

    suite = tv.get("suite_id")
    if suite != "HC18DC-ENC-v0.1":
        fail(f"suite_id mismatch: expected HC18DC-ENC-v0.1, got {suite}")

    dir_axis = tv.get("dir_axis_map", DIR_AXIS_DEFAULT)
    if dir_axis != DIR_AXIS_DEFAULT:
        # allow override but must be length 8
        if not (isinstance(dir_axis, list) and len(dir_axis) == 8):
            fail("dir_axis_map must be list length 8")

    if tv.get("delimiter_per_byte") != "TURN+Q1":
        fail("delimiter_per_byte must be TURN+Q1 for this runner")

    key = hex_to_bytes(tv["key_master_hex"])
    nonce = hex_to_bytes(tv["nonce_hex"])

    # 1) compute record_jcs_utf8_hex
    record_obj = tv["record_object"]
    record_jcs = jcs_string(record_obj)
    record_bytes = record_jcs.encode("utf-8")
    got_record_hex = bytes_to_hex(record_bytes)

    exp_record_hex = tv["expected"].get("record_jcs_utf8_hex")
    if exp_record_hex is None:
        fail("expected.record_jcs_utf8_hex missing in tv")
    exp_record_hex = exp_record_hex.lower().replace(" ", "").replace("\n", "")

    if got_record_hex != exp_record_hex:
        fail("record_jcs_utf8_hex mismatch\n"
             f"  expected: {exp_record_hex}\n"
             f"  got     : {got_record_hex}")
    ok("record_jcs_utf8_hex matches")

    # 2) encrypt and compare ciphertext/tag
    ct, tag = encrypt_record_bytes(record_bytes, key, nonce, dir_axis)
    got_ct_hex = bytes_to_hex(ct)
    got_tag_hex = bytes_to_hex(tag)

    exp_ct_hex = tv["expected"].get("ciphertext_hex")
    exp_tag_hex = tv["expected"].get("tag_hex")
    if not exp_ct_hex or not exp_tag_hex:
        fail("expected.ciphertext_hex and expected.tag_hex must be filled")

    exp_ct_hex = exp_ct_hex.lower().replace(" ", "").replace("\n", "")
    exp_tag_hex = exp_tag_hex.lower().replace(" ", "").replace("\n", "")

    if got_ct_hex != exp_ct_hex:
        fail("ciphertext_hex mismatch\n"
             f"  expected: {exp_ct_hex}\n"
             f"  got     : {got_ct_hex}")
    ok("ciphertext_hex matches")

    if got_tag_hex != exp_tag_hex:
        fail("tag_hex mismatch\n"
             f"  expected: {exp_tag_hex}\n"
             f"  got     : {got_tag_hex}")
    ok("tag_hex matches")

    print("\nPASS: HC18DC-ENC v0.1 test-vector verified.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python hc18dc_enc_tv_runner.py tests/vectors/hc18dc_enc_tv01.json")
        raise SystemExit(2)
    run(sys.argv[1])

if __name__ == "__main__":
    main()
