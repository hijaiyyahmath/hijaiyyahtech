import pytest
from hisavm.vm import HisaVM, Trap
from hisavm.isa import enc_audit
from hisavm.bytecode import words_to_bytes_le
from hisavm.master import load_master_csv
from pathlib import Path

def test_core1_audit_requires_setflag():
    # Fix pathing for test environment
    root = Path(__file__).resolve().parents[1]
    data_csv = root / "data" / "MH-28-v1.0-18D.csv"
    data_hij28 = root / "data" / "HIJAIYYAH_28.txt"
    
    v18_by_index, _ = load_master_csv(data_csv, data_hij28, strict_formulas=True)
    code = words_to_bytes_le([enc_audit(0)])  # AUDIT V0 without SETFLAG
    vm = HisaVM(code, v18_by_index)
    with pytest.raises(Trap) as e:
        vm.run()
    assert vm.st.ERR == 5
