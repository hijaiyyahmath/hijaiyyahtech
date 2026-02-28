from pathlib import Path
from hisavm.master import load_master_csv
from hisavm.audit import audit_v18_or_raise

def test_audit_formulas_pass_for_jim():
    root = Path(__file__).resolve().parents[1]
    data_csv = root / "data" / "MH-28-v1.0-18D.csv"
    data_hij28 = root / "data" / "HIJAIYYAH_28.txt"
    
    v18_by_index, rows = load_master_csv(data_csv, data_hij28, strict_formulas=True)
    Vjim = rows["ج"].v18
    audit_v18_or_raise(Vjim, closed_hint=0)
