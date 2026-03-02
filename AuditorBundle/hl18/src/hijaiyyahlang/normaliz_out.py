from __future__ import annotations
import re
from typing import Any, Dict, Optional

def parse_metrics(out_text: str) -> Dict[str, Any]:
    found: Dict[str, Any] = {}

    def m_int(pat: str, key: str) -> None:
        m = re.search(pat, out_text, flags=re.I | re.M)
        if m:
            found[key] = int(m.group(1))

    m_int(r"(\d+)\s+Hilbert\s+basis\s+elements\b", "hilbert_basis_size")
    m_int(r"(\d+)\s+extreme\s+rays?\b", "extreme_rays")
    m_int(r"(\d+)\s+support\s+hyperplanes?\b", "support_hyperplanes")
    m_int(r"\brank\s*=\s*(\d+)", "rank")
    m_int(r"external\s+index\s*=\s*(\d+)", "external_index")
    m_int(r"internal\s+index\s*=\s*(\d+)", "internal_index")
    m_int(r"(\d+)\s+equations?\s*:", "equations")

    if re.search(r"original\s+monoid\s+is\s+not\s+integrally\s+closed", out_text, flags=re.I):
        found["integrally_closed"] = False
    elif re.search(r"original\s+monoid\s+is\s+integrally\s+closed", out_text, flags=re.I):
        found["integrally_closed"] = True

    return found
