import sys
import os
import argparse

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from hcpu_ai.engine import HCPUAI
from hcpu_ai.compliance_loop import ConformanceMode

def run_demo(mode_str: str):
    mode = ConformanceMode[mode_str.upper()]
    print(f"[*] Starting HCPU-AI Demo (Mode: {mode.name})")
    
    # Mock HISA bytecode (SETFLAG 1, LDH 0, AUDIT 0, HALT)
    # Normative sequence for 'Jim' (index 4)
    from hisavm.isa import enc_setflag_closed_hint, enc_ldh_v18, enc_audit, enc_halt
    
    # Mock HISA bytecode (SETFLAG 1, LDH 0, AUDIT 0, HALT)
    # Normative sequence for 'Jim' (index 4)
    
    code = b""
    # LDH_V18(idx=4, rd=0)
    code += struct.pack("<I", enc_ldh_v18(0, 4))
    # SETFLAG(1)
    code += struct.pack("<I", enc_setflag_closed_hint(1))
    # AUDIT(rd=0)
    code += struct.pack("<I", enc_audit(0))
    # HALT
    code += struct.pack("<I", enc_halt())

    # Mock dataset (Alif, Ba, Ta, Tha, Jim)
    dataset = [[0]*18 for _ in range(5)]
    # Jim (index 4) features (v18) - constructed to pass hisa-vm audit
    # [hat, nt, nf, nm, km, kt, kd, ka, kz, qa, qt, qd, qs, qz, ANc, AKc, AQc, eps]
    # hat=12, U=9, rho=3, eps=0, closed_hint=1
    dataset[4] = [12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 5, 5, 0]

    engine = HCPUAI(code, dataset, mode)
    steps = engine.run()
    
    print(f"[+] HCPU-AI halted after {steps} steps.")
    print(f"[+] Final Audit Status: {'OK' if not engine.bridge.vm.st.ERR else 'FAIL'}")
    
    trace_path = os.path.join("release", "artifacts", "demo_trace.jsonl")
    engine.tracer.save_jsonl(trace_path)
    print(f"[+] Trace saved to {trace_path}")
    
    if mode == ConformanceMode.OWNER:
        print(f"[+] Owner State Hash: {engine.owner.get_state_hash()}")

if __name__ == "__main__":
    import struct
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="CORE", choices=["CORE", "FEEDBACK", "OWNER"])
    args = parser.parse_args()
    run_demo(args.mode)
