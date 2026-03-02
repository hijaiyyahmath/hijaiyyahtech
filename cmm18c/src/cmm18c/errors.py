class TrapCause:
    NONE = 0
    ILLEGAL_OPCODE = 1
    ILLEGAL_ENCODING = 2
    ILLEGAL_REG = 3
    ILLEGAL_FLAG = 4
    CONFORMANCE_SETFLAG_REQ = 5
    AUDIT_DERIVED_MISMATCH = 6
    AUDIT_RHO_NEGATIVE = 7
    AUDIT_MOD4 = 8
    AUDIT_EPS_RANGE = 9
    MISALIGNED_V18_PTR = 10

class TrapException(Exception):
    def __init__(self, cause: int, message: str = ""):
        self.cause = cause
        self.message = message
        super().__init__(f"TRAP {cause}: {message}")
