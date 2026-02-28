# src/hisavm/audit.py
from __future__ import annotations
from hisavm.errors import (
    ERR_AUDIT_DERIVED_MISMATCH,
    ERR_AUDIT_RHO_NEGATIVE,
    ERR_AUDIT_EPS_RANGE,
    ERR_AUDIT_MOD4,
)

def recompute_AN_AK_AQ(v18: list[int]) -> tuple[int,int,int]:
    nt,nf,nm = map(int, v18[1:4])
    km,kt,kd,ka,kz = map(int, v18[4:9])
    qa,qt,qd,qs,qz = map(int, v18[9:14])
    return nt+nf+nm, km+kt+kd+ka+kz, qa+qt+qd+qs+qz

def recompute_U(v18: list[int]) -> int:
    k_z = int(v18[8])
    q_t = int(v18[10])
    q_d = int(v18[11])
    q_s = int(v18[12])
    q_z = int(v18[13])
    return q_t + 4*q_d + q_s + q_z + 2*k_z

def audit_v18_or_raise(v18: list[int], closed_hint: int) -> None:
    if len(v18) != 18:
        raise RuntimeError(ERR_AUDIT_DERIVED_MISMATCH)

    hat = int(v18[0])
    ANc, AKc, AQc = int(v18[14]), int(v18[15]), int(v18[16])
    ANr, AKr, AQr = recompute_AN_AK_AQ(v18)
    if (ANc,AKc,AQc) != (ANr,AKr,AQr):
        raise RuntimeError(ERR_AUDIT_DERIVED_MISMATCH)

    U = recompute_U(v18)
    rho = hat - U
    if rho < 0:
        raise RuntimeError(ERR_AUDIT_RHO_NEGATIVE)

    eps = int(v18[17])
    if eps not in (0,1):
        raise RuntimeError(ERR_AUDIT_EPS_RANGE)

    if closed_hint == 1 and (hat % 4) != 0:
        raise RuntimeError(ERR_AUDIT_MOD4)
