from typing import List
from .constants import NUM_VECTOR_REGS, NUM_SCALAR_REGS, DIMENSION

class RegisterFile:
    def __init__(self):
        # V0..V15: 18x u32
        self.vector = [[0] * DIMENSION for _ in range(NUM_VECTOR_REGS)]
        # R0..R7: u64
        self.scalar = [0] * NUM_SCALAR_REGS

    def write_v(self, reg_idx: int, data: List[int]):
        if 0 <= reg_idx < NUM_VECTOR_REGS:
            self.vector[reg_idx] = list(data)

    def read_v(self, reg_idx: int) -> List[int]:
        return list(self.vector[reg_idx])

    def write_r(self, reg_idx: int, data: int):
        if 0 <= reg_idx < NUM_SCALAR_REGS:
            self.scalar[reg_idx] = data

    def read_r(self, reg_idx: int) -> int:
        return self.scalar[reg_idx]
