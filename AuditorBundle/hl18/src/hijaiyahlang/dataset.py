from __future__ import annotations
import csv
from dataclasses import dataclass
from typing import Dict, List, Tuple, Sequence

Vector18 = Sequence[int]
NORMATIVE_28 = "ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن و ه ي".split()

V18_FIELDS_CANON = [
    "ThetaHat", "nt", "nf", "nm", "km", "kt", "kd", "ka", "kz",
    "qa", "qt", "qd", "qs", "qz", "AN", "AK", "AQ", "hamzah_marker"
]

ALT_HAMZAH_FIELDS = ["eps", "epsilon", "hamzah", "hamzah_marker"]

@dataclass(frozen=True)
class Dataset18:
    table: Dict[str, List[int]]

    def require(self, letter: str) -> List[int]:
        if letter not in self.table:
            raise ValueError(f"Letter {letter!r} not in dataset")
        return self.table[letter]

HL18Dataset = Dataset18

def load_mh28_csv(path: str) -> Dataset18:
    with open(path, "r", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        # Handle cases where DictReader might miss headers if BOM is present
        raw_header = [h.strip() for h in r.fieldnames or []]
        
        # Resolve hamzah marker column name
        hamzah_col = "hamzah_marker"
        for k in ALT_HAMZAH_FIELDS:
            if k in raw_header:
                hamzah_col = k
                break
        
        # Map our canon names to actual column names in this CSV
        # (mostly identical except for hamzah)
        column_map = {canon: canon for canon in V18_FIELDS_CANON[:-1]}
        column_map["hamzah_marker"] = hamzah_col

        # Validation
        required = ["letter"] + list(column_map.values())
        for col in required:
            if col not in raw_header:
                raise ValueError(f"CSV missing required column: {col}")

        table: Dict[str, List[int]] = {}
        for row in r:
            h = (row.get("letter") or "").strip()
            if not h or h == ".": continue # ignore empty or tail dots
            
            try:
                v18 = [int(row[column_map[k]]) for k in V18_FIELDS_CANON]
            except (ValueError, TypeError) as e:
                raise ValueError(f"Non-integer value for letter '{h}' in v18 columns") from e
                
            table[h] = v18

    if len(table) != 28:
        raise ValueError(f"Expected 28 letters, got {len(table)}")
    return Dataset18(table=table)

def cod_word(word: str, ds: Dataset18) -> List[int]:
    out = [0]*18
    for ch in word:
        if ch not in ds.table:
            raise ValueError(f"Unknown letter outside H28: {ch!r}")
        v = ds.table[ch]
        out = [a+b for a,b in zip(out, v)]
    return out
