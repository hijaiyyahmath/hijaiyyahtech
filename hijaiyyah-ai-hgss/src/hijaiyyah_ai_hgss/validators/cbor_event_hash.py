import hashlib
import cbor2
from hijaiyyah_ai_hgss.taxonomy import ValidationError, ErrorCategory

def canonical_cbor_sha256(event_wo_hash: dict) -> str:
    # Use cbor2 to produce a canonical CBOR byte stream
    return hashlib.sha256(cbor2.dumps(event_wo_hash, canonical=True)).hexdigest()

def validate_event_sha256(event: dict):
    # In Guarded mode, a placeholder is allowed temporarily, but valid output must have the real hash.
    # However, this validator's job is to CHECK if it matches.
    if event.get("event_sha256") in ("<<AUTO>>", ""):
        return [ValidationError(ErrorCategory.CBOR_HASH_MISMATCH, "event_sha256 is AUTO/empty", "$.event_sha256")]

    ev = dict(event)
    ev.pop("event_sha256", None)
    want = canonical_cbor_sha256(ev)
    got = event.get("event_sha256", "")
    
    if want != got:
        return [ValidationError(
            ErrorCategory.CBOR_HASH_MISMATCH, 
            f"event_sha256 mismatch. want={want}, got={got}", 
            "$.event_sha256"
        )]
    return []
