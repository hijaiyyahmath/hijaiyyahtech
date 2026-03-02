from __future__ import annotations

import argparse
import json
import hashlib
import os
import sys
from typing import Any, Dict, Optional, Tuple

# Add src to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from hgss.audit.auditlog import (
    require_cbor2,
    lease_evidence_sha256,
    event_digest_sha256,
    trace_sha256,
)

# Hard-locked release metadata (Normative)
HGSS_VERSION = "HGSS-HCVM-v1.HC18DC"
GIT_HASH = "e392c68"

# Hard-locked dataset hashes (normative)
MH28_SHA256 = "7393659dfe979cf85b1cf6293179f7ba1f49b4eedd1af19f002170148ce00380"
CSGI28_SHA256 = "530845fbc3815ea9f02c75d44bda0e1aa096ec93729942d24d2d8bb0bd56c9d5"


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def hex_to_bytes(h: str) -> bytes:
    h = h.strip().lower()
    if h.startswith("0x"):
        h = h[2:]
    return bytes.fromhex(h)


def build_hgss_aad(
    mh28_sha256_hex: str,
    csgi28_sha256_hex: str,
    vc1_agg_hex: str,
    geo_agg_hex: str,
    key_id_hex: str,
    txid_hex: str,
) -> bytes:
    """
    Normative AAD builder: must match HCVM build_aad().
    AAD = b"|".join([
      b"HGSS", b"HC18DC", b"v1.0",
      MH28_SHA256_bytes, CSGI28_SHA256_bytes,
      VC1_AGG_bytes, GEO_AGG_bytes,
      b"KEYID="+key_id, b"TXID="+txid
    ])
    """
    return b"|".join([
        b"HGSS", b"HC18DC", b"v1.0",
        hex_to_bytes(mh28_sha256_hex),
        hex_to_bytes(csgi28_sha256_hex),
        hex_to_bytes(vc1_agg_hex),
        hex_to_bytes(geo_agg_hex),
        b"KEYID=" + hex_to_bytes(key_id_hex),
        b"TXID=" + hex_to_bytes(txid_hex),
    ])


def load_json_or_jsonl(path: str) -> list[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = f.read().strip()
    if not data:
        return []
    if data[0] == "{":
        try:
            return [json.loads(data)]
        except json.JSONDecodeError:
            pass
    # JSONL or Multiple JSON objects
    out = []
    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def verify_event(
    ev: Dict[str, Any],
    *,
    ciphertext_file: Optional[str] = None,
    ciphertext_hex: Optional[str] = None,
    trace_file: Optional[str] = None,
    strict_dataset_lock: bool = True,
    strict_event_digest: bool = True,
) -> Tuple[bool, list[str]]:
    errs: list[str] = []

    # 0) Schema & Version Lock Checks
    if ev.get("hgss_version") != HGSS_VERSION:
        errs.append("VERSION_MISMATCH")
    if ev.get("git_hash") != GIT_HASH:
        errs.append("GIT_HASH_MISMATCH")
    
    # §1.0 Top-level Key Presence Check
    required_keys = [
        "event_type", "hgss_version", "git_hash", "git_tag", "timestamp_utc",
        "node_id_hex", "key_id_hex", "txid_hex", "mh28_sha256", "csgi28_sha256",
        "lease", "lease_sig", "nonce", "aggregates", "commitment", "mac",
        "ciphertext", "trace", "hsm", "status", "event_sha256"
    ]
    for k in required_keys:
        if k not in ev:
            errs.append(f"REQUIRED_KEY_MISSING:{k}")

    # Check fixed-length hex fields (§1.0)
    for k in ["node_id_hex", "key_id_hex", "txid_hex", "mh28_sha256", "csgi28_sha256"]:
        val = ev.get(k, "")
        expected_len = 64
        if len(val) != expected_len:
            errs.append(f"HEX_LENGTH_INVALID:{k}:{len(val)}")

    # 1) dataset locks (§0.3 / §1.0)
    mh = ev.get("mh28_sha256")
    cg = ev.get("csgi28_sha256")
    for k, v in [("mh28_sha256", mh), ("csgi28_sha256", cg)]:
        if not v or len(v) != 64:
            errs.append(f"HEX_LENGTH_INVALID:{k}")

    if strict_dataset_lock:
        if mh != MH28_SHA256:
            errs.append("DATASET_LOCK_MH28_MISMATCH")
        if cg != CSGI28_SHA256:
            errs.append("DATASET_LOCK_CSGI28_MISMATCH")

    # 2) lease evidence sha
    lease = ev.get("lease")
    if isinstance(lease, dict):
        want = lease.get("lease_evidence_sha256")
        if not want:
            errs.append("LEASE_EVIDENCE_SHA_MISSING")
        else:
            calc = lease_evidence_sha256(lease)
            if calc != want:
                errs.append("LEASE_EVIDENCE_SHA_MISMATCH")
    else:
        errs.append("LEASE_OBJECT_MISSING")

    # 2.1) Banking Hardening: lease signature check (§3)
    lease_sig = ev.get("lease_sig")
    if isinstance(lease_sig, dict):
        if lease_sig.get("verified") != "PASS":
            errs.append("LEASE_SIGNATURE_NOT_VERIFIED")
        if lease_sig.get("sig_alg") != "ES256":
            errs.append("LEASE_SIG_ALG_INVALID")
        for k in ["lease_token_sha256", "lease_payload_sha256"]:
            val = lease_sig.get(k, "")
            if len(val) != 64:
                errs.append(f"LEASE_SIG_HEX_INVALID:{k}")
    else:
        errs.append("LEASE_SIG_OBJECT_MISSING")
    
    # 4) Banking Hardening: HSM check (§10)
    hsm = ev.get("hsm")
    if isinstance(hsm, dict):
        if not hsm.get("provider") or not hsm.get("handle"):
            errs.append("HSM_FIELDS_MISSING")
        if hsm.get("key_id_hex") != ev.get("key_id_hex"):
            errs.append("HSM_KEY_ID_MISMATCH")
    else:
        errs.append("HSM_OBJECT_MISSING")

    # 5) recompute AAD sha
    aggregates = ev.get("aggregates", {})
    aad_sha_want = aggregates.get("aad_sha256")
    vc1_hex = aggregates.get("vc1_agg_sha256")
    geo_hex = aggregates.get("geo_agg_sha256")
    key_id_hex = ev.get("key_id_hex")
    txid_hex = ev.get("txid_hex")
    if not (aad_sha_want and vc1_hex and geo_hex and key_id_hex and txid_hex and mh and cg):
        errs.append("AAD_COMPONENTS_MISSING")
    else:
        aad = build_hgss_aad(mh, cg, vc1_hex, geo_hex, key_id_hex, txid_hex)
        aad_sha_calc = sha256_hex(aad)
        if aad_sha_calc != aad_sha_want:
            errs.append("AAD_SHA256_MISMATCH")

    # 6) ciphertext sha
    ct_obj = ev.get("ciphertext", {})
    ct_sha_want = ct_obj.get("ciphertext_sha256")
    if ciphertext_file or ciphertext_hex:
        if ciphertext_file:
            ctb = open(ciphertext_file, "rb").read()
        else:
            ctb = hex_to_bytes(ciphertext_hex or "")
        ct_sha_calc = sha256_hex(ctb)
        if ct_sha_want and ct_sha_calc != ct_sha_want:
            errs.append("CIPHERTEXT_SHA256_MISMATCH")
    else:
        if not ct_sha_want:
            errs.append("CIPHERTEXT_SHA256_MISSING")

    # 7) trace sha
    trace_obj = ev.get("trace", {})
    trace_sha_want = trace_obj.get("trace_sha256")
    if trace_file:
        trace_events = load_json_or_jsonl(trace_file)
        trace_sha_calc = trace_sha256(trace_events)
        if trace_sha_want and trace_sha_calc != trace_sha_want:
            errs.append("TRACE_SHA256_MISMATCH")
    else:
        if trace_sha_want is None:
            errs.append("TRACE_SHA256_MISSING")

    # 8) nonce metadata (§4)
    nonce = ev.get("nonce")
    if isinstance(nonce, dict):
        if len(nonce.get("nonce96_hex", "")) != 24:
            errs.append("NONCE96_LENGTH_INVALID")
        if nonce.get("aead_alg") != "AES-256-GCM":
            errs.append("NONCE_ALG_INVALID")
    else:
        errs.append("NONCE_OBJECT_MISSING")

    # 9) event digest sha (§12.2)
    if strict_event_digest:
        want = ev.get("event_sha256")
        if not want:
            errs.append("EVENT_SHA256_MISSING")
        else:
            calc = event_digest_sha256(ev)
            if calc != want:
                errs.append("EVENT_SHA256_MISMATCH")

    return (len(errs) == 0), errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", required=True, help="Path to JSON or JSONL event log (single event or lines)")
    ap.add_argument("--ciphertext-file", default=None, help="Optional ciphertext file to verify ciphertext_sha256")
    ap.add_argument("--ciphertext-hex", default=None, help="Optional ciphertext hex to verify ciphertext_sha256")
    ap.add_argument("--trace-file", default=None, help="Optional trace JSON/JSONL to verify trace_sha256")
    ap.add_argument("--no-strict-dataset-lock", action="store_true")
    ap.add_argument("--no-strict-event-digest", action="store_true")
    args = ap.parse_args()

    # Canonical CBOR is normative
    require_cbor2()

    events = load_json_or_jsonl(args.event)
    if not events:
        raise SystemExit("NO_EVENTS")

    ok_all = True
    for i, ev in enumerate(events):
        ok, errs = verify_event(
            ev,
            ciphertext_file=args.ciphertext_file,
            ciphertext_hex=args.ciphertext_hex,
            trace_file=args.trace_file,
            strict_dataset_lock=not args.no_strict_dataset_lock,
            strict_event_digest=not args.no_strict_event_digest,
        )
        if ok:
            print(f"[PASS] event[{i}]")
        else:
            ok_all = False
            print(f"[FAIL] event[{i}] -> {errs}")

    raise SystemExit(0 if ok_all else 2)


if __name__ == "__main__":
    main()
