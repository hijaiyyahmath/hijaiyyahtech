from __future__ import annotations

from cmm18c.errors import (
    TrapCause,
)

def audit_v18_or_trap(V: list[int], closed_hint: int):
    """
    Audit-grade (fail-closed): raise TrapException(err) in VM caller.
    Lane order (HL-18):
      0 hatTheta
      1..3 nt,nf,nm
      4..8 km,kt,kd,ka,kz
      9..13 qa,qt,qd,qs,qz
      14..16 AN,AK,AQ
      17 eps
    """
    from .errors import TrapException
    if len(V) != 18:
        raise TrapException(TrapCause.AUDIT_DERIVED_MISMATCH, "INVALID_DIM")

    hat = int(V[0])
    nt, nf, nm = map(int, V[1:4])
    km, kt, kd, ka, kz = map(int, V[4:9])
    qa, qt, qd, qs, qz = map(int, V[9:14])
    AN, AK, AQ = map(int, V[14:17])
    eps = int(V[17])

    if AN != (nt + nf + nm) or AK != (km + kt + kd + ka + kz) or AQ != (qa + qt + qd + qs + qz):
        raise TrapException(TrapCause.AUDIT_DERIVED_MISMATCH, "Derived total mismatch")

    U = qt + 4*qd + qs + qz + 2*kz
    rho = hat - U
    if rho < 0:
        raise TrapException(TrapCause.AUDIT_RHO_NEGATIVE, f"rho negative: {rho}")

    if eps not in (0, 1):
        raise TrapException(TrapCause.AUDIT_EPS_RANGE, f"eps invalid: {eps}")

    if closed_hint == 1 and (hat % 4) != 0:
        raise TrapException(TrapCause.AUDIT_MOD4, f"mod4 fail: hat={hat}")

    return True
