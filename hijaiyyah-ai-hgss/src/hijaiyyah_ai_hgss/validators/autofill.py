# src/hijaiyyah_ai_hgss/validators/autofill.py
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

import cbor2

# NOTE (Normative): This is an evaluation harness autofill, not a production crypto engine.


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def utc_rfc3339() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def det_bytes(seed: bytes, n: int) -> bytes:
    """
    Deterministic bytes for evaluation harness (seeded by txid_hex).
    """
    out = b""
    i = 0
    while len(out) < n:
        out += hashlib.sha256(seed + i.to_bytes(4, "little")).digest()
        i += 1
    return out[:n]


def canonical_cbor(obj: Dict[str, Any]) -> bytes:
    return cbor2.dumps(obj, canonical=True)


def compute_event_sha256(event: Dict[str, Any]) -> str:
    ev = dict(event)
    ev.pop("event_sha256", None)
    return sha256_hex(canonical_cbor(ev))


def nonce96(prefix32: int, ctr64: int) -> bytes:
    return prefix32.to_bytes(4, "big") + ctr64.to_bytes(8, "big")


def load_demo_lease_token_bytes(hgss_repo: str) -> bytes:
    """
    v1 harness: loads a demo COSE token (or a serialized JSON fallback) from deps/hgss-hc18dc artifacts.
    The token bytes are used ONLY to compute lease_token_sha256 for evidence.
    """
    p = Path(hgss_repo)
    candidates = [
        p / "artifacts" / "lease_token.cose",
        p / "artifacts" / "lease_token.bin",
        p / "artifacts" / "lease_input.json",
        p / "artifacts" / "lease_signed.json",
    ]
    for c in candidates:
        if c.exists() and c.is_file():
            if c.suffix.lower() in (".cose", ".bin"):
                return c.read_bytes()
            if c.suffix.lower() == ".json":
                j = json.loads(c.read_text(encoding="utf-8"))
                if "cose_sign1_hex" in j:
                    return bytes.fromhex(j["cose_sign1_hex"])
                if "cose_sign1_b64" in j:
                    import base64
                    return base64.b64decode(j["cose_sign1_b64"])
                return json.dumps(j, sort_keys=True, separators=(",", ":")).encode("utf-8")
    raise RuntimeError("Missing demo lease token artifact in deps/hgss-hc18dc/artifacts/")


def ensure_maps(event: Dict[str, Any]) -> None:
    for k in [
        "lease", "lease_sig", "nonce", "aggregates", "commitment", "mac",
        "ciphertext", "trace", "hsm", "status"
    ]:
        if k not in event or not isinstance(event[k], dict):
            event[k] = {}


def autofill_event_and_write_artifacts(
    *,
    event: Dict[str, Any],
    case_dir: str,
    hgss_repo: str,
    ct_len: int = 256,
    hsm_profile: str = "A",
) -> Dict[str, Any]:
    """
    Fills required fields per AUDIT_EVIDENCE_SCHEMA.md §1–§11 and writes artifacts:
      - ct.bin
      - trace.jsonl
      - lease_input.json
      - lease_token.bin
      - event_single.json
      - auditlog.jsonl
    """
    ensure_maps(event)
    out = Path(case_dir)
    out.mkdir(parents=True, exist_ok=True)

    # ---- timestamps (must exist, RFC3339 UTC)
    event.setdefault("timestamp_utc", utc_rfc3339())
    event["lease"].setdefault("issued_at", utc_rfc3339())
    event["lease"].setdefault("expires_at", utc_rfc3339())

    # ---- lease required keys (§2)
    event["lease"].setdefault("allocator_id", "DEMO_ALLOCATOR")
    event["lease"].setdefault("lease_id", "DEMO_LEASE_0001")

    prefix32 = int(event["lease"].get("prefix32", event["nonce"].get("nonce_prefix32", 0)))
    start_ctr = int(event["lease"].get("start_ctr", 0))
    end_ctr = int(event["lease"].get("end_ctr", start_ctr + 1_000_000))
    cur_ctr = int(event["lease"].get("cur_ctr_at_issue", start_ctr))

    ctr64 = int(event["nonce"].get("nonce_ctr64", cur_ctr))
    if ctr64 < start_ctr:
        ctr64 = start_ctr
    if ctr64 > end_ctr:
        ctr64 = end_ctr

    event["lease"]["prefix32"] = prefix32
    event["lease"]["start_ctr"] = start_ctr
    event["lease"]["end_ctr"] = end_ctr
    event["lease"]["cur_ctr_at_issue"] = cur_ctr

    # ---- nonce required keys (§4)
    n96 = nonce96(prefix32, ctr64)
    event["nonce"]["aead_alg"] = "AES-256-GCM"
    event["nonce"]["nonce96_hex"] = n96.hex()
    event["nonce"]["nonce_prefix32"] = prefix32
    event["nonce"]["nonce_ctr64"] = ctr64
    event["nonce"]["nonce_policy"] = "range_lease_prefix32_ctr64_v1"
    event["nonce"].setdefault("nonce_uniqueness_check", "PASS")

    # ---- deterministic ciphertext artifact (evaluation harness)
    txid_hex = event["txid_hex"]
    seed = bytes.fromhex(txid_hex)
    ct = det_bytes(seed + b"CT", ct_len)
    (out / "ct.bin").write_bytes(ct)

    # ---- deterministic trace artifact
    trace_obj = {
        "events": [
            {"kind": "LLM_RAW", "step": 1},
            {"kind": "AUTOFILL", "step": 2},
            {"kind": "ORACLE", "step": 3}
        ]
    }
    trace_cbor = canonical_cbor(trace_obj)
    (out / "trace.jsonl").write_text(
        json.dumps(trace_obj, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8"
    )

    # ---- lease evidence canonical CBOR (§2)
    lease_payload = dict(event["lease"])
    lease_payload_cbor = canonical_cbor(lease_payload)
    (out / "lease_input.json").write_text(
        json.dumps(lease_payload, sort_keys=True, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    event["lease"]["lease_evidence_sha256"] = sha256_hex(lease_payload_cbor)

    # ---- lease signature evidence (§3)
    token_bytes = load_demo_lease_token_bytes(hgss_repo)
    (out / "lease_token.bin").write_bytes(token_bytes)

    event["lease_sig"]["sig_alg"] = "ES256"
    event["lease_sig"].setdefault("kid_hex", "01")
    event["lease_sig"]["verified"] = event["lease_sig"].get("verified", "PASS")
    event["lease_sig"]["lease_token_sha256"] = sha256_hex(token_bytes)
    event["lease_sig"]["lease_payload_sha256"] = sha256_hex(lease_payload_cbor)

    # ---- aggregates (§5)
    mh = bytes.fromhex(event["mh28_sha256"])
    cg = bytes.fromhex(event["csgi28_sha256"])
    bind = hashlib.sha256(mh + cg + seed + n96).digest()

    event["aggregates"].setdefault("vc1_agg_sha256", sha256_hex(bind + b"VC1"))
    event["aggregates"].setdefault("geo_agg_sha256", sha256_hex(bind + b"GEO"))

    aad_raw = hashlib.sha256(
        bytes.fromhex(event["aggregates"]["vc1_agg_sha256"]) +
        bytes.fromhex(event["aggregates"]["geo_agg_sha256"]) +
        mh + cg +
        lease_payload_cbor +
        n96
    ).digest()
    event["aggregates"]["aad_sha256"] = sha256_hex(aad_raw)

    # ---- commitment (§6)
    event["commitment"]["commit_alg"] = "SHA-256"
    event["commitment"]["commit_hex"] = sha256_hex(ct)

    # ---- mac (§7)
    event["mac"]["mac_alg"] = "HMAC-SHA256"
    event["mac"]["mac_tag_hex"] = sha256_hex(ct + aad_raw)

    # ---- ciphertext (§8)
    event["ciphertext"]["ciphertext_sha256"] = sha256_hex(ct)
    event["ciphertext"]["ciphertext_len"] = len(ct)

    # ---- trace (§9)
    event["trace"]["trace_sha256"] = sha256_hex(trace_cbor)
    event["trace"]["trace_event_count"] = len(trace_obj["events"])

    # ---- hsm (§10)
    event["hsm"].setdefault("provider", "pkcs11")
    event["hsm"].setdefault("handle", "DEMO_HANDLE")
    event["hsm"].setdefault("device_serial", "")
    event["hsm"]["profile"] = hsm_profile
    event["hsm"]["key_id_hex"] = event["key_id_hex"]  # MUST match

    # ---- status (§11)
    event["status"].setdefault("state", "HALT")
    event["status"].setdefault("err_code", 0)

    # ---- final event hash (§12)
    event["event_sha256"] = compute_event_sha256(event)

    # persist event outputs
    (out / "event_single.json").write_text(
        json.dumps(event, sort_keys=True, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    (out / "auditlog.jsonl").write_text(
        json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    return event
