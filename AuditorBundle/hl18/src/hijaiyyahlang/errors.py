from __future__ import annotations

class ConformanceError(Exception):
    """Raised when HISA integration spec or coordination fails."""
    pass

class TrapError(Exception):
    """Raised when an audit trap is encountered or expected."""
    pass
