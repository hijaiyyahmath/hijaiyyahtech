import pytest

from src.cmm18c.isa import enc_ldv, enc_halt
from src.cmm18c.vm import CMM18CV10
from src.cmm18c.errors import TrapCause
from _util import assemble_words

class DummyMem:
    def read_v18(self, addr: int):
        return [0]*18

def test_ldv_misaligned_ptr_traps_err10():
    # LDV V0, [S0 + 0] ; HALT
    code = assemble_words(
        enc_ldv(vd=0, sa=0),
        0x00000000,          # off32 extension word
        enc_halt(),
    )
    vm = CMM18CV10(code=code, memory=DummyMem())
    vm.s_regs[0] = 0x00001004     # misaligned (not %16)
    vm.run()
    assert vm.trapped
    assert vm.trap_cause == TrapCause.MISALIGNED_V18_PTR
