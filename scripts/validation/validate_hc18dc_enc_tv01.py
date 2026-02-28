#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys

HEX_RE = re.compile(r"^[0-9a-fA-F]*$")
# ISO8601: YYYY-MM-DDTHH:MM:SS[.mmm][Z|+-HH:MM]
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")

def fail(msg: str) -> None:
    print("FAIL:", msg)
    raise SystemExit(1)

def ok(msg: str) -> None:
    print("[OK]", msg)

def is_hex(s: str) -> bool:
    return bool(HEX_RE.match(s))

def hex_len_bytes(h: str) -> int:
    if len(h) % 2 != 0:
        fail(f"hex length must be even, got len={len(h)}")
    return len(h) // 2

def validate_iso8601(s: str, label: str) -> None:
    if not ISO_RE.match(s):
        fail(f"{label} is not a valid ISO8601 timestamp: {s}")

def main(path: str) -> int:
    tv = json.load(open(path, "r", encoding="utf-8"))

    # suite_id
    if tv.get("suite_id") != "HC18DC-ENC-v0.1":
        fail(f"suite_id must be HC18DC-ENC-v0.1, got {tv.get('suite_id')}")

    # key / nonce / delimiter
    key_hex = tv.get("key_master_hex", "")
    nonce_hex = tv.get("nonce_hex", "")
    delim = tv.get("delimiter_per_byte")

    if not is_hex(key_hex) or len(key_hex) != 64:
        fail("key_master_hex must be 64 hex chars (32 bytes)")
    if not is_hex(nonce_hex) or len(nonce_hex) != 48:
        fail("nonce_hex must be 48 hex chars (24 bytes)")
    if delim != "TURN+Q1":
        fail(f"delimiter_per_byte must be TURN+Q1, got {delim}")

    ok("suite_id/key/nonce/delimiter PASS")

    # record object checks
    rec_obj = tv.get("record_object")
    if not isinstance(rec_obj, dict):
        fail("record_object must be an object")
    
    # mandatory fields
    for f in ("txn_id", "from_account", "timestamp"):
        if f not in rec_obj:
            fail(f"record_object missing mandatory field: {f}")
    
    validate_iso8601(rec_obj["timestamp"], "record_object.timestamp")
    ok("record_object mandatory fields & ISO8601 PASS")

    # expected fields
    exp = tv.get("expected")
    if not isinstance(exp, dict):
        fail("expected must be an object")

    for k in ("record_jcs_utf8_hex", "ciphertext_hex", "tag_hex"):
        if k not in exp:
            fail(f"expected.{k} missing")

    rec_hex = exp["record_jcs_utf8_hex"].strip()
    ct_hex = exp["ciphertext_hex"].strip()
    tag_hex = exp["tag_hex"].strip()

    if not is_hex(rec_hex):
        fail("expected.record_jcs_utf8_hex must be hex")
    if not is_hex(ct_hex):
        fail("expected.ciphertext_hex must be hex")
    if not is_hex(tag_hex) or len(tag_hex) != 32:
        fail("expected.tag_hex must be 32 hex chars (16 bytes)")

    # Optional JCS Validation (requires rfc8785)
    try:
        import rfc8785
        got_jcs = rfc8785.dumps(rec_obj).hex()
        if got_jcs != rec_hex.lower():
            fail(f"expected.record_jcs_utf8_hex mismatch with actual JCS of record_object\n  got: {got_jcs}\n  exp: {rec_hex.lower()}")
        ok("JCS validation PASS (rfc8785)")
    except ImportError:
        ok("JCS validation SKIPPED (rfc8785 not installed)")

    rec_len = hex_len_bytes(rec_hex)
    ct_len  = hex_len_bytes(ct_hex)
    tag_len = hex_len_bytes(tag_hex)

    ok(f"expected hex format PASS (pt_len={rec_len}, ct_len={ct_len}, tag_len={tag_len})")

    # ciphertext length should match plaintext length (stream XOR)
    if ct_len != rec_len:
        fail(f"ciphertext length mismatch: ct_len={ct_len} must equal pt_len={rec_len}")
    ok("ciphertext_len == plaintext_len PASS")

    # optional length fields consistency
    if "plaintext_len_bytes" in exp and exp["plaintext_len_bytes"] != rec_len:
        fail("expected.plaintext_len_bytes does not match record_jcs_utf8_hex length")
    if "ciphertext_len_bytes" in exp and exp["ciphertext_len_bytes"] != ct_len:
        fail("expected.ciphertext_len_bytes does not match ciphertext_hex length")

    ok("optional length fields PASS (if present)")

    print("PASS: HC18DC-ENC v0.1 test-vector strict validation ok")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_hc18dc_enc_tv01.py hc18dc_enc_tv01.json")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
