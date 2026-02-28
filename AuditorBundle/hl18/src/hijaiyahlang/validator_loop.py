"""
validator_loop.py — Validator Feedback Loop with Error Taxonomy

Non-normative side-effect module: validates V18 vectors and accumulates
error statistics for learning feedback.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from hijaiyahlang.core import audit_v18, Vector
from hijaiyahlang.hb import HilbertBasis, is_in_monoid_greedy


class ErrorType(Enum):
    NONE               = auto()
    INVALID_DIM        = auto()
    NEGATIVE_COMPONENT = auto()
    DERIVED_MISMATCH   = auto()
    HB_NONMEMBER       = auto()
    CONE_VIOLATION     = auto()


@dataclass(frozen=True)
class FeedbackSignal:
    ok: bool
    error_type: ErrorType
    detail: str
    confidence: float  # 0.0 .. 1.0

    def __repr__(self) -> str:
        status = "PASS" if self.ok else f"FAIL({self.error_type.name})"
        return f"FeedbackSignal({status}, conf={self.confidence:.2f})"


@dataclass
class ValidationStats:
    total: int = 0
    passed: int = 0
    errors: Dict[str, int] = field(default_factory=dict)

    @property
    def error_rate(self) -> float:
        return (self.total - self.passed) / max(self.total, 1)

    @property
    def confidence(self) -> float:
        return self.passed / max(self.total, 1)


class ValidatorLoop:
    """
    Validates V18 vectors with deterministic error taxonomy.
    Accumulates error statistics for feedback-driven learning.
    """

    def __init__(self, hb: Optional[HilbertBasis] = None):
        self.hb = hb
        self.stats = ValidationStats()

    def validate(self, v: Vector) -> FeedbackSignal:
        """
        Validate a V18 vector. Returns FeedbackSignal.
        Check order: DIM → NEGATIVE → DERIVED → HB_MEMBER
        """
        self.stats.total += 1

        # 1. Dimension check
        if len(v) != 18:
            return self._fail(ErrorType.INVALID_DIM,
                              f"len={len(v)}, expected 18")

        # 2. Non-negativity
        for i, x in enumerate(v):
            if x < 0:
                return self._fail(ErrorType.NEGATIVE_COMPONENT,
                                  f"v[{i}]={x}")

        # 3. Derived formula checks (AN/AK/AQ/U/ρ)
        ar = audit_v18(v)
        if not ar.ok:
            failed = [k for k, v in ar.checks.items() if not v]
            return self._fail(ErrorType.DERIVED_MISMATCH,
                              f"failed: {failed}")

        # 4. Hilbert basis membership (optional, if HB loaded)
        if self.hb is not None:
            if not is_in_monoid_greedy(v, self.hb.basis, max_depth=100):
                return self._fail(ErrorType.HB_NONMEMBER,
                                  "not in monoid(HB18)")

        # All checks passed
        self.stats.passed += 1
        return FeedbackSignal(
            ok=True,
            error_type=ErrorType.NONE,
            detail="all checks passed",
            confidence=self.stats.confidence,
        )

    def _fail(self, err: ErrorType, detail: str) -> FeedbackSignal:
        key = err.name
        self.stats.errors[key] = self.stats.errors.get(key, 0) + 1
        return FeedbackSignal(
            ok=False,
            error_type=err,
            detail=detail,
            confidence=self.stats.confidence,
        )

    def update(self, feedback: FeedbackSignal,
               ground_truth: Optional[Vector] = None) -> None:
        """Learning step: record ground-truth for future improvement."""
        # Currently a no-op placeholder for future ML integration.
        # Stats are already accumulated in validate().
        pass
