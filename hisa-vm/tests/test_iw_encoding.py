from hisavm.isa import enc_setflag_closed_hint, enc_audit, enc_ldh_v18, decode_iw
from hisavm.constants import OP_SETFLAG, OP_AUDIT, OP_LDH_V18

def test_setflag_literal():
    assert enc_setflag_closed_hint(0) == 0x30000000
    assert enc_setflag_closed_hint(1) == 0x30000001

def test_decode_fields():
    w = enc_ldh_v18(0, 4)
    iw = decode_iw(w)
    assert iw.opcode == OP_LDH_V18
    assert iw.rd == 0
    assert iw.imm8 == 4

    w2 = enc_audit(3)
    iw2 = decode_iw(w2)
    assert iw2.opcode == OP_AUDIT
    assert iw2.rd == 3
