from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class ErrorCategory(Enum):
    SCHEMA_MISSING_KEY = "SCHEMA_MISSING_KEY"
    SCHEMA_TYPE_MISMATCH = "SCHEMA_TYPE_MISMATCH"
    SCHEMA_HEX_LENGTH = "SCHEMA_HEX_LENGTH"
    VERSION_LOCK_FAIL = "VERSION_LOCK_FAIL"
    CBOR_HASH_MISMATCH = "CBOR_HASH_MISMATCH"
    HGSS_VERIFIER_FAIL = "HGSS_VERIFIER_FAIL"
    FORMAT_INVALID_JSON = "FORMAT_INVALID_JSON"

@dataclass(frozen=True)
class ValidationError:
    category: ErrorCategory
    message: str
    path: str = "" # e.g. "lease_sig.verified"
