from typing import List, Optional
from .constants import RELEASE_ID
from .registers import RegisterFile
from .trap import HCPUTrap, TrapCode
from .trace import Tracer
from .hisa_bridge import HISABridge
from .compliance_loop import ComplianceLoop, ConformanceMode
from .owner_model import OwnerModel

class HCPUAI:
    def __init__(self, code: bytes, dataset: List[List[int]], mode: ConformanceMode = ConformanceMode.CORE):
        self.regs = RegisterFile()
        self.tracer = Tracer()
        self.bridge = HISABridge(code, dataset)
        self.compliance = ComplianceLoop(mode)
        self.owner = OwnerModel()
        self.halted = False

    def step(self):
        if self.halted:
            return

        state = self.bridge.get_state()
        pc = state["PC"] if state else 0
        
        # In a real impl, we'd decode op from pc
        op = "EXEC" 

        self.compliance.before_step(pc, op)
        
        try:
            self.bridge.step()
            new_state = self.bridge.get_state()
            if new_state:
                # Sync registers back from bridge if needed (demo simplification)
                for i in range(len(new_state["V"])):
                    self.regs.write_v(i, new_state["V"][i])
                for i in range(len(new_state["S"])):
                    self.regs.write_r(i, new_state["S"][i])
                
                if new_state["halted"]:
                    self.halted = True
                    
                self.compliance.after_step(pc, op, {"ok": True} if not new_state["ERR"] else {"ok": False})
                
                if self.compliance.mode == ConformanceMode.OWNER:
                    # Deterministic side effect
                    self.owner.observe(f"PC_{pc}")

                self.tracer.record(pc, op, self.regs.vector, self.regs.scalar)
        except Exception as e:
            self.halted = True
            raise e

    def run(self, max_steps: int = 1000):
        steps = 0
        while not self.halted and steps < max_steps:
            self.step()
            steps += 1
        return steps
