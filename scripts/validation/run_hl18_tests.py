import json
from collections import defaultdict

def v18_from_row(r, layout):
    return tuple(r[k] for k in layout)

def add_rows(a, b):
    return {k: a.get(k,0) + b.get(k,0) for k in set(a) | set(b)}

def cod_row_for_letter(letter, L):
    return L[letter]

def cod_row_for_sequence(seq, L):
    # Detect all keys from first entry
    first_letter = list(L.keys())[0]
    keys = L[first_letter].keys()
    total = {k: 0 for k in keys}
    for ch in seq:
        total = add_rows(total, cod_row_for_letter(ch, L))
    return total

def derived_U(r):
    return r["qt"] + 4*r["qd"] + r["qs"] + r["qz"] + 2*r["kz"]

def run(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    L = data["letters_master_csv"]
    layout = data["vector18_layout"]

    print(f"Running suite: {data.get('suite', 'unknown')}")

    # 1) Per-letter derived checks
    for h, r in L.items():
        # U formula
        u = derived_U(r)
        assert u == r["U"], f"U mismatch letter {h}: derived {u} vs table {r['U']}"
        # rho formula
        rho = r["ThetaHat"] - r["U"]
        assert rho == r["rho"], f"rho mismatch letter {h}: derived {rho} vs table {r['rho']}"
        # Sums
        assert (r["nt"] + r["nf"] + r["nm"]) == r["AN"], f"AN mismatch {h}"
        assert (r["km"] + r["kt"] + r["kd"] + r["ka"] + r["kz"]) == r["AK"], f"AK mismatch {h}"
        assert (r["qa"] + r["qt"] + r["qd"] + r["qs"] + r["qz"]) == r["AQ"], f"AQ mismatch {h}"
        # ThetaDeg
        assert (90 * r["ThetaHat"]) == r["ThetaDeg"], f"ThetaDeg mismatch {h}"

    # 2) Sequence U/rho aggregation tests
    for t in data.get("urho_string_tests", []):
        if "w" in t:
            agg = cod_row_for_sequence(t["w"], L)
        else:
            agg1 = cod_row_for_sequence(t["w1"], L)
            agg2 = cod_row_for_sequence(t["w2"], L)
            assert agg1["ThetaHat"] == agg2["ThetaHat"], f"cong fail ThetaHat {t['name']}"
            assert agg1 == agg2, f"cong fail: aggregates differ {t['name']}"
            agg = agg1

        exp = t["expect"]
        assert agg["ThetaHat"] == exp["ThetaHat"], f"ThetaHat mismatch {t['name']}"
        assert agg["U"] == exp["U"], f"U mismatch {t['name']}"
        assert agg["rho"] == exp["rho"], f"rho mismatch {t['name']}"

        # must satisfy ThetaHat = U + rho
        assert agg["ThetaHat"] == agg["U"] + agg["rho"], f"ThetaHat != U+rho {t['name']}"

        # derived U from aggregated components must match aggregated U
        U2 = agg["qt"] + 4*agg["qd"] + agg["qs"] + agg["qz"] + 2*agg["kz"]
        assert U2 == agg["U"], f"Aggregated U formula mismatch {t['name']}: {U2} vs {agg['U']}"

    # 3) Injective check v18
    seen = defaultdict(list)
    for h, r in L.items():
        vec = v18_from_row(r, layout)
        seen[vec].append(h)
    collisions = {vec: hs for vec, hs in seen.items() if len(hs) > 1}

    inj_cfg = data.get("injective_v18_test", {})
    if inj_cfg.get("expect_injective", True):
        if collisions:
            print("Collisions found:")
            for v, hs in collisions.items():
                print(f"  {v} -> {hs}")
        assert not collisions, f"NOT injective v18 suite"
        assert len(seen) == inj_cfg.get("expect_unique_count", 28), "Unique count mismatch"

    print("PASS: HL-18-v1.0-extension suite.")

if __name__ == "__main__":
    run("HL18_tests_ext.json")
