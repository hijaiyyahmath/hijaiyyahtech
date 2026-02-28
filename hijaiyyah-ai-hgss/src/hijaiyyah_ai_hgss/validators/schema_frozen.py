import re
from hijaiyyah_ai_hgss.taxonomy import ValidationError, ErrorCategory

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX24 = re.compile(r"^[0-9a-f]{24}$")

RELEASE_VER = "HGSS-HCVM-v1.HC18DC"
RELEASE_HASH = "e392c68"
EVENT_TYPE = "HGSS_HC18DC_TX"

REQUIRED_TOP = [
  "event_type","hgss_version","git_hash","git_tag","timestamp_utc",
  "node_id_hex","key_id_hex","txid_hex","mh28_sha256","csgi28_sha256",
  "lease","lease_sig","nonce","aggregates","commitment","mac",
  "ciphertext","trace","hsm","status","event_sha256"
]

def _is_tstr(x): return isinstance(x, str)
def _is_map(x): return isinstance(x, dict)
def _is_uint(x): return isinstance(x, int) and x >= 0

def validate_schema(event: dict):
    errs = []

    if not _is_map(event):
        return [ValidationError(ErrorCategory.FORMAT_INVALID_JSON, "Top-level must be map/object", "$")]

    for k in REQUIRED_TOP:
        if k not in event:
            errs.append(ValidationError(ErrorCategory.SCHEMA_MISSING_KEY, f"Missing key: {k}", f"$.{k}"))

    if errs:
        return errs

    if event["event_type"] != EVENT_TYPE:
        errs.append(ValidationError(ErrorCategory.SCHEMA_TYPE_MISMATCH, f"event_type must be {EVENT_TYPE}", "$.event_type"))

    if event["hgss_version"] != RELEASE_VER:
        errs.append(ValidationError(ErrorCategory.VERSION_LOCK_FAIL, "hgss_version mismatch", "$.hgss_version"))

    if event["git_hash"] != RELEASE_HASH:
        errs.append(ValidationError(ErrorCategory.VERSION_LOCK_FAIL, "git_hash mismatch", "$.git_hash"))

    if event["git_tag"] != RELEASE_VER:
        errs.append(ValidationError(ErrorCategory.VERSION_LOCK_FAIL, "git_tag mismatch", "$.git_tag"))

    # fixed-length hex ids
    for k in ["node_id_hex","key_id_hex","txid_hex","mh28_sha256","csgi28_sha256"]:
        v = event[k]
        if not (_is_tstr(v) and HEX64.match(v)):
            errs.append(ValidationError(ErrorCategory.SCHEMA_HEX_LENGTH, f"{k} must be 64 lowercase hex", f"$.{k}"))

    # nonce96
    n = event["nonce"]
    if not _is_map(n):
        errs.append(ValidationError(ErrorCategory.SCHEMA_TYPE_MISMATCH, "nonce must be map", "$.nonce"))
    else:
        if n.get("nonce96_hex","") and not HEX24.match(n["nonce96_hex"]):
            errs.append(ValidationError(ErrorCategory.SCHEMA_HEX_LENGTH, "nonce96_hex must be 24 lowercase hex", "$.nonce.nonce96_hex"))

    return errs
