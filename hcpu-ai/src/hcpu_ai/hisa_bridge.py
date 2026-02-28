import sys
import os
from typing import List, Any

# Ensure hisa-vm is in path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..", "hisa-vm", "src")))

try:
    from hisavm.vm import HisaVM, Trap as HisaTrap
    from hisavm.constants import LANES, VREGS, SREGS
    HISA_AVAILABLE = True
except ImportError:
    HISA_AVAILABLE = False

class HISABridge:
    """Delegates execution to hisa-vm if available."""
    def __init__(self, code: bytes, dataset: List[List[int]]):
        self.available = HISA_AVAILABLE
        if self.available:
            self.vm = HisaVM(code, dataset)
        else:
            self.vm = None

    def step(self):
        if self.vm:
            self.vm.step()

    def get_state(self):
        if self.vm:
            return {
                "PC": self.vm.st.PC,
                "V": self.vm.st.V,
                "S": self.vm.st.S,
                "halted": self.vm.st.halted,
                "ERR": self.vm.st.ERR
            }
        return None
