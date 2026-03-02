#!/usr/bin/env python3
import csv, sys, unicodedata

TATWEEL = "\u0640"
HIJAIYYAH_SET = set("ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن و ه ي".split())

def letter_id(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return s.replace(TATWEEL, "")

def die(msg):
    print("FAIL:", msg)
    sys.exit(1)

def I(row, k): 
    try: return int(row[k])
    except Exception: die(f"Bad int field {k} in row letter={row.get('letter')} value={row.get(k)!r}")

def main(path: str):
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)

    seen_letters = []
    v18_map = {}  # v18_tuple -> letter

    for i, row in enumerate(rows, 1):
        raw = row["letter"]
        lid = letter_id(raw)
        if lid not in HIJAIYYAH_SET:
            die(f"row {i}: letter_id not in HIJAIYYAH_SET: raw={raw!r} lid={lid!r}")
        seen_letters.append(lid)

        ThetaHat = I(row,"ThetaHat")
        nt,nf,nm = I(row,"nt"),I(row,"nf"),I(row,"nm")
        km,kt,kd,ka,kz = I(row,"km"),I(row,"kt"),I(row,"kd"),I(row,"ka"),I(row,"kz")
        qa,qt,qd,qs,qz = I(row,"qa"),I(row,"qt"),I(row,"qd"),I(row,"qs"),I(row,"qz")
        U_tbl, rho_tbl = I(row,"U"), I(row,"rho")

        AN = nt+nf+nm
        AK = km+kt+kd+ka+kz
        AQ = qa+qt+qd+qs+qz

        U = qt + 4*qd + qs + qz + 2*kz
        rho = ThetaHat - U

        if U != U_tbl:
            die(f"{lid}: U mismatch calc={U} tbl={U_tbl}")
        if rho != rho_tbl:
            die(f"{lid}: rho mismatch calc={rho} tbl={rho_tbl}")
        if rho < 0 or ThetaHat != U + rho:
            die(f"{lid}: audit identity failed (ThetaHat,U,rho)=({ThetaHat},{U},{rho})")

        # epsilon marker hamzah (sesuai klaim rilis kamu): ε(ك)=1, lainnya 0
        eps = 1 if lid == "ك" else 0

        v18 = (ThetaHat,nt,nf,nm, km,kt,kd,ka,kz, qa,qt,qd,qs,qz, AN,AK,AQ, eps)

        if v18 in v18_map:
            die(f"INJECTIVE FAIL: v18 collision {v18} for letters {v18_map[v18]!r} and {lid!r}")
        v18_map[v18] = lid

    if len(seen_letters) != 28:
        die(f"Expected 28 rows; got {len(seen_letters)}")
    if set(seen_letters) != HIJAIYYAH_SET:
        die(f"Letter set mismatch: missing={HIJAIYYAH_SET-set(seen_letters)} extra={set(seen_letters)-HIJAIYYAH_SET}")

    print("PASS: formulas OK (AN/AK/AQ implied; U/rho verified), 28/28 letters OK, v18 injective OK.")
    print("Unique v18 count:", len(v18_map))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_and_build_v18.py master.csv")
        sys.exit(2)
    main(sys.argv[1])
