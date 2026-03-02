# JIM Primary Vortex & Vortex Channel (VC-1) — CMM-18C v1.0 Extension

## Status
Normative codec layer on top of HL-18 v18. Does not modify CORE CPU semantics.

## Primary Vortex
Let J be the normative v18 vector for letter_id("ج") loaded from the hash-locked master table (MH-28-v1.0-18D.csv).

Define mask:
m_j = J_j mod 2, for j=0..17.

## Bit Channel (VC-1 bit)
For any v18 vector V (18 lanes uint32), define:
b(V) = ( Σ_j (V_j mod 2) * m_j ) mod 2.

## Energy Channel (VC-1 energy)
Use HL-18 audit-derived metrics:
E_T = hatTheta
U   = q_t + 4*q_d + q_s + q_z + 2*k_z
rho = hatTheta - U

Output energy tuple:
E(V) = (E_T, U, rho)

## VC-1 Output
VC1(V) = ( b(V), E(V) )

## Determinism
- J must be loaded by letter_id("ج") from the sealed master table.
- All arithmetic is integer-only.
