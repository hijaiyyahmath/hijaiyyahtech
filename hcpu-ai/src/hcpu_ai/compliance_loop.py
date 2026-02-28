from enum import Enum, auto
from typing import List, Optional, Any
from .trap import HCPUTrap, TrapCode

class ConformanceMode(Enum):
    CORE     = auto()  # execute + audit, no side effects
    FEEDBACK = auto()  # CORE + validator stats
    OWNER    = auto()  # FEEDBACK + deterministic owner model update

class ComplianceLoop:
    def __init__(self, mode: ConformanceMode = ConformanceMode.CORE):
        self.mode = mode
        self.feedback_log = []

    def before_step(self, pc: int, op: str):
        pass

    def after_step(self, pc: int, op: str, audit_result: Optional[Any] = None):
        if self.mode in (ConformanceMode.FEEDBACK, ConformanceMode.OWNER):
            if audit_result:
                self.feedback_log.append({"pc": pc, "op": op, "audit": audit_result})
        
        if op == "AUDIT" and audit_result and not audit_result.get("ok", False):
            raise HCPUTrap(TrapCode.AUDIT_FAIL, f"Audit failed at PC {pc}")
