from __future__ import annotations
from typing import Dict, List, Optional, Tuple

def solve_decode_any(target: List[int], gens: Dict[str, List[int]], *, time_limit_sec: float = 2.0) -> Optional[str]:
    """
    Cari 1 word w sehingga sum(v18(ch))=target.
    Deterministik: objective minimize total length, tie-break by letter order.
    Requires: ortools (extra).
    """
    try:
        from ortools.sat.python import cp_model  # type: ignore
    except Exception as e:
        raise RuntimeError("OR-Tools not installed. Install: pip install hijaiyyahlang[solver]") from e

    letters = sorted(gens.keys())
    model = cp_model.CpModel()

    # coefficient matrix: 18 x 28
    x = {h: model.NewIntVar(0, 10_000, f"c_{i}_{h}") for i,h in enumerate(letters)}
    # constraints per dimension
    for d in range(18):
        model.Add(sum(x[h] * gens[h][d] for h in letters) == target[d])

    # objective: minimize total counts (shortest word)
    model.Minimize(sum(x[h] for h in letters))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit_sec)
    solver.parameters.num_search_workers = 1  # deterministik

    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    # build a canonical word: repeat letters in sorted order
    parts: List[str] = []
    for h in letters:
        c = int(solver.Value(x[h]))
        if c > 0:
            parts.append(h * c)
    return "".join(parts)

def nf_virtual(target: List[int], gens: Dict[str, List[int]]) -> Tuple[List[int], Optional[str]]:
    """
    nf_vector = target (idempotent)
    canonical_word = decode_any target (jika ditemukan)
    """
    w = solve_decode_any(target, gens)
    return target, w
