from pathlib import Path
from hisavm.master import load_master_csv

def test_ldh_index_4_is_jim_and_hattheta_3():
    root = Path(__file__).resolve().parents[1]
    data_csv = root / "data" / "MH-28-v1.0-18D.csv"
    data_hij28 = root / "data" / "HIJAIYYAH_28.txt"
    
    v18_by_index, rows = load_master_csv(data_csv, data_hij28, strict_formulas=True)
    # Based on the user snippet, Jim index 4 should have ThetaHat 3
    assert v18_by_index[4][0] == 3 
    assert "ج" in rows
