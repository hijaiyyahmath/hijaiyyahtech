
import os
import sys
from pathlib import Path

# Add HISA-VM to PYTHONPATH
hisa_vm_root = Path(r"c:\hijaiyyah-codex\hisa-vm")
sys.path.append(str(hisa_vm_root / "src"))

from hisavm.vm import HisaVM, Trap
from hisavm.isa import enc_setflag_closed_hint, enc_audit, enc_halt
from hisavm.bytecode import words_to_bytes_le
from hisavm.master import load_master_csv

def run_demo():
    # Load Master Data
    data_csv = hisa_vm_root / "data" / "MH-28-v1.0-18D.csv"
    data_hij28 = Path(r"c:\hijaiyyah-codex\hisa-vm\data\HIJAIYYAH_28.txt")
    
    v18_by_index, _ = load_master_csv(data_csv, data_hij28, strict_formulas=True)

    print("=== HISA-VM OUTPUT DEMO ===")

    # --- CASE 1: PASS ---
    print("\n[CASE 1: PASS (Successful Audit)]")
    # Sequence: SETFLAG(0x1) -> AUDIT V0 -> HALT
    # This is valid because SETFLAG precedes AUDIT.
    code_pass = words_to_bytes_le([
        enc_setflag_closed_hint(1), 
        enc_audit(0),
        enc_halt()
    ])
    vm_pass = HisaVM(code_pass, v18_by_index)
    try:
        vm_pass.run()
        print("Status: HALT_SUCCESS")
        print(f"Registers: PC={vm_pass.st.PC}, CLOSED_HINT={vm_pass.st.CLOSED_HINT}, ERR={vm_pass.st.ERR}")
        print("Audit Result: PASS (No Trap)")
    except Exception as e:
        print(f"Unexpected Error: {e}")

    # --- CASE 2: TRAP ---
    print("\n[CASE 2: TRAP (CORE-1 Adjacency Violation)]")
    # Sequence: AUDIT V0 -> HALT
    # This is INVALID because SETFLAG was not called before AUDIT.
    code_trap = words_to_bytes_le([
        enc_audit(0),
        enc_halt()
    ])
    vm_trap = HisaVM(code_trap, v18_by_index)
    try:
        vm_trap.run()
        print("Status: SUCCESS (Unexpected)")
    except Trap as t:
        print(f"Status: TRAP_TRIGGERED")
        print(f"Trap Code: {t}")
        print(f"Registers: PC={vm_trap.st.PC}, CLOSED_HINT={vm_trap.st.CLOSED_HINT}, ERR={vm_trap.st.ERR}")
        print("Reason: ERR=5 (HISA_ERR_CORE1_SETFLAG_REQUIRED)")

if __name__ == "__main__":
    run_demo()
