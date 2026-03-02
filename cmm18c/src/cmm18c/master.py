import csv
import unicodedata
from typing import Dict, List

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def letter_id(s: str) -> str:
    return nfc(s).replace("\u0640", "").strip()

def load_master_csv(path: str) -> Dict[str, List[int]]:
    """
    Loads MH-28-v1.0-18D.csv and returns a mapping:
    letter_id -> list of 18 integers.
    """
    master = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lid = letter_id(row["letter"])
            # Order: hatTheta, nt, nf, nm, km, kt, kd, ka, kz, qa, qt, qd, qs, qz, AN, AK, AQ, varsigma
            v18 = [
                int(row["ThetaHat"]),
                int(row["nt"]), int(row["nf"]), int(row["nm"]),
                int(row["km"]), int(row["kt"]), int(row["kd"]), int(row["ka"]), int(row["kz"]),
                int(row["qa"]), int(row["qt"]), int(row["qd"]), int(row["qs"]), int(row["qz"]),
                int(row["AN"]), int(row["AK"]), int(row["AQ"]),
                int(row["varsigma"])
            ]
            master[lid] = v18
    return master
