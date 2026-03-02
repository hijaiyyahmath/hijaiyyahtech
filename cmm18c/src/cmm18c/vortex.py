from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple, List

LANES = 18

@dataclass(frozen=True)
class VortexEnergy:
    hat_theta: int
    U: int
    rho: int

def lane_parity_u32(x: int) -> int:
    return x & 1

def jim_vector_from_master(master: dict) -> List[int]:
    """
    master: mapping {letter_id: v18_list_of_18_ints}
    Must contain key 'ج' (NFC), from sealed master table.
    """
    J = master.get("ج")
    if J is None:
        # Fallback if normalization differs in literal check
        import unicodedata
        jeem = unicodedata.normalize("NFC", "ج")
        J = master.get(jeem)
        
    if J is None:
        raise KeyError("MASTER_MISSING_JIM_JEEM: expected key 'ج'")
    if len(J) != LANES:
        raise ValueError("MASTER_INVALID_DIM_FOR_JIM")
    return [int(x) for x in J]

def vortex_mask_from_jim(J: List[int]) -> List[int]:
    if len(J) != LANES:
        raise ValueError("JIM_DIM_INVALID")
    return [lane_parity_u32(x) for x in J]

def vortex_bit(V: List[int], mask: List[int]) -> int:
    if len(V) != LANES:
        raise ValueError("V18_DIM_INVALID")
    if len(mask) != LANES:
        raise ValueError("MASK_DIM_INVALID")
    acc = 0
    for j in range(LANES):
        acc ^= (lane_parity_u32(int(V[j])) & int(mask[j]))
    return acc  # 0 or 1

def energy_metrics(V: List[int]) -> VortexEnergy:
    """
    HL-18 lane order assumed:
      0 hatTheta
      8 k_z
      10 q_t
      11 q_d
      12 q_s
      13 q_z
    """
    if len(V) != LANES:
        raise ValueError("V18_DIM_INVALID")
    hat_theta = int(V[0])
    k_z = int(V[8])
    q_t = int(V[10])
    q_d = int(V[11])
    q_s = int(V[12])
    q_z = int(V[13])

    U = q_t + 4*q_d + q_s + q_z + 2*k_z
    rho = hat_theta - U
    return VortexEnergy(hat_theta=hat_theta, U=U, rho=rho)

def vc1(V: List[int], mask: List[int]) -> Tuple[int, VortexEnergy]:
    b = vortex_bit(V, mask)
    e = energy_metrics(V)
    return b, e

def vc1_stream(Vs: Iterable[List[int]], mask: List[int]) -> Tuple[List[int], List[VortexEnergy]]:
    bits: List[int] = []
    energies: List[VortexEnergy] = []
    for V in Vs:
        b, e = vc1(V, mask)
        bits.append(b)
        energies.append(e)
    return bits, energies
