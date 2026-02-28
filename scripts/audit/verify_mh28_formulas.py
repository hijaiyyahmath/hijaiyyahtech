#!/usr/bin/env python3
import csv, sys

def die(msg): print("FAIL:", msg); sys.exit(1)

path = sys.argv[1] if len(sys.argv) > 1 else "MH-28-18D-v1.0.csv"
with open(path, "r", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for i, row in enumerate(r, 1):
        def I(k): return int(row[k])
        nt,nf,nm = I("nt"),I("nf"),I("nm")
        km,kt,kd,ka,kz = I("km"),I("kt"),I("kd"),I("ka"),I("kz")
        qa,qt,qd,qs,qz = I("qa"),I("qt"),I("qd"),I("qs"),I("qz")
        AN,AK,AQ = I("AN"),I("AK"),I("AQ")
        U,rho,ThetaHat = I("U"),I("rho"),I("ThetaHat")
        if AN != nt+nf+nm: die(f"row {i} {row['letter']}: AN mismatch")
        if AK != km+kt+kd+ka+kz: die(f"row {i} {row['letter']}: AK mismatch")
        if AQ != qa+qt+qd+qs+qz: die(f"row {i} {row['letter']}: AQ mismatch")
        if U  != qt + 4*qd + qs + qz + 2*kz: die(f"row {i} {row['letter']}: U mismatch")
        if rho != ThetaHat - U: die(f"row {i} {row['letter']}: rho mismatch")
print("PASS: all derived formulas verified (AN/AK/AQ/U/rho).")
