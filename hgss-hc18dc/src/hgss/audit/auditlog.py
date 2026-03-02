from __future__ import annotations

import json
import os
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

# Canonical CBOR is normative for evidence hashing.
# Install: pip install cbor2
try:
    import cbor2  # type: ignore
except Exception:  # pragma: no cover
    cbor2 = None


def sha256_bytes(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def require_cbor2():
    if cbor2 is None:
        raise RuntimeError("CBOR2_NOT_AVAILABLE: install 'cbor2' for canonical CBOR evidence hashing")


def canonical_cbor_dumps(obj: Any) -> bytes:
    """
    Normative canonical bytes for evidence hashing:
    - Canonical CBOR (RFC 8949 canonical encoding).
    """
    require_cbor2()
    # canonical=True ensures key ordering and definite-length encoding
    return cbor2.dumps(obj, canonical=True)


def canonical_json_dumps(obj: Any) -> bytes:
    """
    Non-normative fallback; should NOT be used for banking audit evidence.
    Provided only for debugging.
    """
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return s.encode("utf-8")


def event_digest_sha256(event_obj: Dict[str, Any]) -> str:
    """
    Computes SHA-256 over canonical CBOR of the event object with event_sha256 removed
    to avoid self-reference.
    """
    e = dict(event_obj)
    e.pop("event_sha256", None)
    b = canonical_cbor_dumps(e)
    return sha256_hex(b)


def normalize_lease_for_hash(lease: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normative lease evidence object to hash (canonical CBOR):
    Keep only keys relevant for audit; reject missing fields early.
    """
    required = [
        "allocator_id",
        "lease_id",
        "prefix32",
        "start_ctr",
        "end_ctr",
        "cur_ctr_at_issue",
    ]
    for k in required:
        if k not in lease:
            raise ValueError(f"LEASE_EVIDENCE_MISSING_FIELD:{k}")

    # key_id & node_id are stored at top-level in many events; allow either place.
    norm = {
        "allocator_id": str(lease["allocator_id"]),
        "lease_id": str(lease["lease_id"]),
        "prefix32": int(lease["prefix32"]),
        "start_ctr": int(lease["start_ctr"]),
        "end_ctr": int(lease["end_ctr"]),
        "cur_ctr_at_issue": int(lease["cur_ctr_at_issue"]),
    }
    # Optional timestamps/status (still hashed if present)
    for opt in (
        "lease_issued_at", "lease_expires_at", "status",
        "lease_token_sha256", "lease_payload_sha256", "lease_kid_hex",
        "lease_sig_alg", "lease_sig_verified"
    ):
        if opt in lease:
            norm[opt] = lease[opt]
    return norm


def lease_evidence_sha256(lease: Dict[str, Any]) -> str:
    """
    Normative: SHA-256(canonical CBOR of normalized lease evidence).
    """
    b = canonical_cbor_dumps(normalize_lease_for_hash(lease))
    return sha256_hex(b)


def trace_sha256(trace_obj: Any) -> str:
    """
    Normative: SHA-256(canonical CBOR of trace object).
    trace_obj should be a list[map] or map with deterministic content.
    """
    b = canonical_cbor_dumps(trace_obj)
    return sha256_hex(b)


def write_jsonl_event(
    path: str,
    event: Dict[str, Any],
    *,
    fsync_each: bool = True,
    add_event_sha256: bool = True,
    add_lease_sha256: bool = True,
) -> str:
    """
    Append-only JSONL writer.
    - Optionally computes and inserts:
      - lease.lease_evidence_sha256 (canonical CBOR)
      - event_sha256 (canonical CBOR)
    Returns event_sha256 (if computed) else empty string.
    """
    # Add lease evidence hash if requested
    if add_lease_sha256 and "lease" in event and isinstance(event["lease"], dict):
        lease = dict(event["lease"])
        # If key_id/node_id exist top-level, they remain top-level; lease hash is only lease fields.
        lease["lease_evidence_sha256"] = lease_evidence_sha256(lease)
        event["lease"] = lease

    ev_sha = ""
    if add_event_sha256:
        ev_sha = event_digest_sha256(event)
        event["event_sha256"] = ev_sha

    line = json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n"

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(line)
        f.flush()
        if fsync_each:
            os.fsync(f.fileno())

    return ev_sha
