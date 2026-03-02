import pytest

from src.cmm18c.isa import enc_setflag_closed_hint, enc_audit, enc_halt
from src.cmm18c.vm import CMM18CV10
from src.cmm18c.errors import TrapCause
from _util import assemble_words

class DummyMem:
    def read_v18(self, addr: int):
        return [0]*18

def test_audit_mod4_traps_when_closed_hint_1():
    # Prepare V0 that passes derived and rho, but fails mod4: hatTheta = 5
    V = [0]*18
    V[0] = 5        # hatTheta
    # derived totals already 0; U=0; rho=5 OK; eps=0 OK

    code = assemble_words(
        enc_setflag_closed_hint(1),
        enc_audit(0),   # AUDIT V0 (Vs=Rd=0)
        enc_halt(),
    )
    vm = CMM18CV10(code=code, memory=DummyMem())
    vm.v_regs[0] = V
    vm.run()
    assert vm.trapped
    assert vm.trap_cause == TrapCause.AUDIT_MOD4
