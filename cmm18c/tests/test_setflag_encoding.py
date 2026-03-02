import pytest

from src.cmm18c.isa import enc_setflag_closed_hint, enc_iw, OP_SETFLAG
from src.cmm18c.vm import CMM18CV10
from src.cmm18c.errors import TrapCause
from _util import assemble_words

class DummyMem:
    def read_v18(self, addr: int):
        return [0]*18

def test_setflag_word_exact():
    # IW = [opcode:8 | Rd:4 | Ra:4 | Rb:4 | subop:4 | imm8:8]
    # SETFLAG CLOSED_HINT, 1 => 0x30 | 0 | 0 | 0 | 0 | 1
    # 0x30000001
    assert enc_setflag_closed_hint(1) == 0x30000001
    assert enc_setflag_closed_hint(0) == 0x30000000

def test_setflag_illegal_encoding_traps():
    # Rd must be 0; make it 1 -> illegal encoding
    illegal = enc_iw(OP_SETFLAG, rd=1, subop=0, imm8=1)
    code = assemble_words(illegal)
    vm = CMM18CV10(code=code, memory=DummyMem())
    vm.run()
    assert vm.trapped
    assert vm.trap_cause == TrapCause.ILLEGAL_ENCODING
