import pytest

from src.cmm18c.isa import enc_audit
from src.cmm18c.vm import CMM18CV10
from src.cmm18c.errors import TrapCause
from _util import assemble_words

class DummyMem:
    def read_v18(self, addr: int):
        return [0]*18

def test_core1_audit_without_setflag_traps():
    code = assemble_words(enc_audit(0))  # AUDIT V0, but no SETFLAG before it
    vm = CMM18CV10(code=code, memory=DummyMem())
    vm.run()
    assert vm.trapped
    assert vm.trap_cause == TrapCause.CONFORMANCE_SETFLAG_REQ
