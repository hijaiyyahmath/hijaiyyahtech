from enum import IntEnum

class TrapCode(IntEnum):
    NONE                   = 0x00
    ILLEGAL_ENCODING       = 0x01
    CORE1_VIOLATION        = 0x02
    AUDIT_FAIL             = 0x03
    MOD4_FAIL              = 0x04
    DATASET_LOCK_MISMATCH  = 0x05
    DETERMINISM_ERROR      = 0x06
    HALT                   = 0xFF

class HCPUTrap(Exception):
    def __init__(self, code: TrapCode, message: str):
        self.code = code
        self.message = message
        super().__init__(f"TRAP {code.name}: {message}")
