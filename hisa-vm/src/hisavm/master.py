from __future__ import annotations

import csv
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional


LANES = 18
TATWEEL = "\u0640"

# Columns required from your CSV
COLS_INT = [
    "ThetaHat",
    "nt","nf","nm",
    "km","kt","kd","ka","kz",
    "qa","qt","qd","qs","qz",
    "U","rho",
    "AN","AK","AQ",
    "hamzah_marker",
]

# v18 lane mapping (normative for HISA-VM)
V18_COLS = [
    "ThetaHat",
    "nt","nf","nm",
    "km","kt","kd","ka","kz",
    "qa","qt","qd","qs","qz",
    "AN","AK","AQ",
    "hamzah_marker",
]

def letter_id(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return s.replace(TATWEEL, "")

def load_hijaiyyah_28(path: str | Path) -> List[str]:
    txt = Path(path).read_text(encoding="utf-8")
    # accept space/newline separated
    items = [letter_id(x) for x in txt.split() if x.strip()]
    if len(items) != 28:
        raise ValueError(f"HIJAIYYAH_28_INVALID_LEN: got {len(items)}")
    # ensure unique
    if len(set(items)) != 28:
        raise ValueError("HIJAIYYAH_28_NOT_UNIQUE")
    return items

@dataclass(frozen=True)
class MasterRow:
    letter: str              # normalized letter_id
    v18: List[int]           # length 18 (u32 semantics)
    U: int
    rho: int

def _parse_int(row: dict, k: str) -> int:
    try:
        return int(row[k])
    except Exception as e:
        raise ValueError(f"CSV_INT_PARSE_FAIL: key={k!r} value={row.get(k)!r}") from e

def _u32(x: int) -> int:
    return x & 0xFFFFFFFF

def recompute_U(v18: List[int]) -> int:
    # lane positions (HL-18 order)
    # 0 hatTheta
    # 8 k_z
    # 10 q_t
    # 11 q_d
    # 12 q_s
    # 13 q_z
    k_z = int(v18[8])
    q_t = int(v18[10])
    q_d = int(v18[11])
    q_s = int(v18[12])
    q_z = int(v18[13])
    return q_t + 4*q_d + q_s + q_z + 2*k_z

def recompute_rho(v18: List[int]) -> int:
    hat = int(v18[0])
    return hat - recompute_U(v18)

def recompute_AN_AK_AQ(v18: List[int]) -> Tuple[int,int,int]:
    nt,nf,nm = map(int, v18[1:4])
    km,kt,kd,ka,kz = map(int, v18[4:9])
    qa,qt,qd,qs,qz = map(int, v18[9:14])
    AN = nt+nf+nm
    AK = km+kt+kd+ka+kz
    AQ = qa+qt+qd+qs+qz
    return AN,AK,AQ

def load_master_csv(
    csv_path: str | Path,
    hijaiyyah_28_path: str | Path,
    *,
    strict_formulas: bool = True
) -> Tuple[List[List[int]], Dict[str, MasterRow]]:
    """
    Returns:
      - v18_by_index: list length 28 (index per HIJAIYYAH_28.txt order)
      - rows_by_letter: dict letter_id -> MasterRow

    strict_formulas:
      - checks AN/AK/AQ stored columns match recompute
      - checks U and rho columns match recompute
      - checks eps in {0,1}
    """
    hij = load_hijaiyyah_28(hijaiyyah_28_path)

    rows_by_letter: Dict[str, MasterRow] = {}

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames is None:
            raise ValueError("CSV_NO_HEADER")

        # minimal header check
        for k in (["letter"] + COLS_INT):
            if k not in rd.fieldnames:
                raise ValueError(f"CSV_MISSING_COLUMN:{k}")

        for raw in rd:
            ltr_raw = raw["letter"]
            ltr = letter_id(ltr_raw)
            if not ltr:
                raise ValueError("CSV_EMPTY_LETTER")

            if ltr in rows_by_letter:
                raise ValueError(f"CSV_DUPLICATE_LETTER_AFTER_NORMALIZE:{ltr!r}")

            # parse needed ints
            ints = {k: _parse_int(raw, k) for k in COLS_INT}

            v18 = [_u32(ints[k]) for k in V18_COLS]
            if len(v18) != LANES:
                raise ValueError("V18_DIM_INVALID")

            U_col = int(ints["U"])
            rho_col = int(ints["rho"])

            if strict_formulas:
                # eps range
                eps = int(v18[17])
                if eps not in (0, 1):
                    raise ValueError(f"EPS_RANGE_FAIL:{ltr!r} eps={eps}")

                # AN/AK/AQ consistency
                ANr, AKr, AQr = recompute_AN_AK_AQ(v18)
                ANc, AKc, AQc = int(v18[14]), int(v18[15]), int(v18[16])
                if (ANr,AKr,AQr) != (ANc,AKc,AQc):
                    raise ValueError(f"DERIVED_TOTALS_MISMATCH:{ltr!r} recompute={(ANr,AKr,AQr)} stored={(ANc,AKc,AQc)}")

                # U, rho consistency vs columns
                Ur = recompute_U(v18)
                rhor = int(v18[0]) - Ur
                if Ur != U_col:
                    raise ValueError(f"U_MISMATCH:{ltr!r} recompute={Ur} col={U_col}")
                if rhor != rho_col:
                    raise ValueError(f"RHO_MISMATCH:{ltr!r} recompute={rhor} col={rho_col}")

            rows_by_letter[ltr] = MasterRow(letter=ltr, v18=v18, U=U_col, rho=rho_col)

    # completeness check: must contain all 28 normative letters after normalization
    missing = [x for x in hij if x not in rows_by_letter]
    extra = [x for x in rows_by_letter.keys() if x not in set(hij)]
    if missing:
        raise ValueError(f"MASTER_MISSING_LETTERS:{missing}")
    if extra:
        # extra letters are not allowed for strict 28-letter core
        raise ValueError(f"MASTER_HAS_EXTRA_LETTERS:{extra}")

    v18_by_index = [rows_by_letter[h].v18 for h in hij]
    return v18_by_index, rows_by_letter
