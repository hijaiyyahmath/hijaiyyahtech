#!/usr/bin/env python3
from __future__ import annotations

import csv
import sys
import unicodedata
from typing import Dict, List, Tuple

HIJAIYYAH_SET = set("ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن و ه ي".split())
TATWEEL = "\u0640"

EXPECTED_HEADERS = [
    "letter","ThetaHat","nt","nf","nm","km","kt","kd","ka","kz",
    "qa","qt","qd","qs","qz","U","rho","AN","AK","AQ","varsigma"
]

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def to_int(s: str) -> int:
    s = str(s).strip()
    if s == "":
        raise ValueError("empty int")
    # izinkan "5.0" kalau ada
    if s.endswith(".0"):
        s = s[:-2]
    return int(s)

def letter_id(s: str) -> str:
    # sama seperti verifier kamu: NFC + strip tatweel
    return nfc(s).replace(TATWEEL, "").strip()

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python check_v18_duplicates.py MH-28-v1.0-18D.csv", file=sys.stderr)
        return 2

    path = sys.argv[1]

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            print("FAIL: CSV tanpa header", file=sys.stderr)
            return 1

        # normalisasi header NFC+strip
        headers = [nfc(h).strip() for h in reader.fieldnames]

        missing = [h for h in EXPECTED_HEADERS if h not in headers]
        if missing:
            print("FAIL: header CSV tidak cocok. Missing:", missing, file=sys.stderr)
            print("Got headers:", headers, file=sys.stderr)
            return 1

        vmap: Dict[Tuple[int, ...], List[str]] = {}
        seen_letters: List[str] = []
        rowno = 1  # header = row 1

        for row in reader:
            rowno += 1
            # ambil huruf
            raw_letter = row["letter"]
            lid = letter_id(raw_letter)
            if len(lid) != 1:
                print(f"FAIL: row {rowno} letter_id tidak 1 char: raw={raw_letter!r} id={lid!r}", file=sys.stderr)
                return 1
            seen_letters.append(lid)

            # bangun v18 = 18 dimensi (tanpa U,rho karena itu derived)
            try:
                v18 = (
                    to_int(row["ThetaHat"]),
                    to_int(row["nt"]), to_int(row["nf"]), to_int(row["nm"]),
                    to_int(row["km"]), to_int(row["kt"]), to_int(row["kd"]), to_int(row["ka"]), to_int(row["kz"]),
                    to_int(row["qa"]), to_int(row["qt"]), to_int(row["qd"]), to_int(row["qs"]), to_int(row["qz"]),
                    to_int(row["AN"]), to_int(row["AK"]), to_int(row["AQ"]),
                    to_int(row["varsigma"]),  # marker (ε/hamzah) kamu
                )
            except Exception as e:
                print(f"FAIL: row {rowno} parse int error: {e}", file=sys.stderr)
                return 1

            # audit U,rho (opsional tapi kita fail-kan jika mismatch)
            try:
                qt = to_int(row["qt"]); qd = to_int(row["qd"]); qs = to_int(row["qs"]); qz = to_int(row["qz"])
                kz = to_int(row["kz"])
                U_csv = to_int(row["U"])
                rho_csv = to_int(row["rho"])
                U_calc = qt + 4*qd + qs + qz + 2*kz
                rho_calc = to_int(row["ThetaHat"]) - U_calc
                if U_csv != U_calc:
                    print(f"FAIL: row {rowno} U mismatch for {lid}: csv={U_csv} calc={U_calc}", file=sys.stderr)
                    return 1
                if rho_csv != rho_calc:
                    print(f"FAIL: row {rowno} rho mismatch for {lid}: csv={rho_csv} calc={rho_calc}", file=sys.stderr)
                    return 1
                if rho_csv < 0:
                    print(f"FAIL: row {rowno} rho negatif untuk {lid}: rho={rho_csv}", file=sys.stderr)
                    return 1
            except Exception as e:
                print(f"FAIL: row {rowno} U/rho audit error: {e}", file=sys.stderr)
                return 1

            vmap.setdefault(v18, []).append(lid)

        # cek completeness 28 huruf
        if len(seen_letters) != 28:
            print(f"FAIL: jumlah baris huruf harus 28; got {len(seen_letters)}", file=sys.stderr)
            return 1

        lids_set = set(seen_letters)
        if lids_set != HIJAIYYAH_SET:
            missing = HIJAIYYAH_SET - lids_set
            extra = lids_set - HIJAIYYAH_SET
            print("FAIL: himpunan huruf tidak cocok dengan HIJAIYYAH_SET", file=sys.stderr)
            print(" missing:", " ".join(sorted(missing)), file=sys.stderr)
            print(" extra  :", " ".join(sorted(extra)), file=sys.stderr)
            return 1

        # cek collision v18
        collisions = [(v, hs) for v, hs in vmap.items() if len(hs) > 1]
        if collisions:
            print("FAIL: v18 collision detected", file=sys.stderr)
            for v, hs in collisions:
                print(f"- letters={hs} share v18={v}", file=sys.stderr)
            return 1

        print("PASS: injective v18 untuk 28 huruf (no duplicate v18).")
        print("PASS: audit U dan rho konsisten untuk semua baris.")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
