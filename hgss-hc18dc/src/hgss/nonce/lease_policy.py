from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

def parse_rfc3339_utc(ts: str) -> datetime:
    # Minimal parser: expects Z
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).astimezone(timezone.utc)

@dataclass(frozen=True)
class LeasePolicy:
    fail_closed: bool = True

    def check_not_expired(self, expires_at_rfc3339: str, now_utc: datetime | None = None) -> bool:
        now = now_utc or datetime.now(timezone.utc)
        exp = parse_rfc3339_utc(expires_at_rfc3339)
        return now <= exp
