from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

Vector = List[int]

@dataclass(frozen=True)
class AuditResult:
    ok: bool
    U: int
    rho: int
    mod4: int
    checks: Dict[str, bool]

def audit_v18(v: Vector) -> AuditResult:
    if len(v) != 18:
        raise ValueError("v18 must be length 18")

    ThetaHat = v[0]
    nt,nf,nm = v[1],v[2],v[3]
    km,kt,kd,ka,kz = v[4],v[5],v[6],v[7],v[8]
    qa,qt,qd,qs,qz = v[9],v[10],v[11],v[12],v[13]
    AN,AK,AQ = v[14],v[15],v[16]

    U = qt + 4*qd + qs + qz + 2*kz
    rho = ThetaHat - U
    checks = {
        "AN": (AN == nt+nf+nm),
        "AK": (AK == km+kt+kd+ka+kz),
        "AQ": (AQ == qa+qt+qd+qs+qz),
        "U":  (U == qt + 4*qd + qs + qz + 2*kz),
        "rho": (rho == ThetaHat - U),
        "rho_nonneg": (rho >= 0),
        "ThetaHat_eq_U_plus_rho": (ThetaHat == U + rho),
    }
    ok = all(checks.values())
    return AuditResult(ok=ok, U=U, rho=rho, mod4=(ThetaHat % 4), checks=checks)

def add18(a: Vector, b: Vector) -> Vector:
    if len(a)!=18 or len(b)!=18:
        raise ValueError("length must be 18")
    return [x+y for x,y in zip(a,b)]

def sub18z(a: Vector, b: Vector) -> List[int]:
    if len(a)!=18 or len(b)!=18:
        raise ValueError("length must be 18")
    return [x-y for x,y in zip(a,b)]

def asN(vz: List[int]) -> Vector:
    if any(x < 0 for x in vz):
        raise ValueError("asN FAIL: negative component exists")
    return list(vz)

def mod18(v: Vector, m: int) -> Vector:
    if m <= 0:
        raise ValueError("m must be > 0")
    return [x % m for x in v]

def cong(a: Vector, b: Vector) -> bool:
    return a == b
