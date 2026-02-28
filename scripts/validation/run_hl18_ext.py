import yaml
from collections import defaultdict

NUM_KEYS = ["ThetaHat","ThetaDeg","nt","nf","nm","km","kt","kd","ka","kz","qa","qt","qd","qs","qz","U","rho","AN","AK","AQ","hamzah_marker"]

def add(a, b):
    out = dict(a)
    for k in NUM_KEYS:
        out[k] = out.get(k, 0) + b.get(k, 0)
    return out

def derived_U(r):
    return r["qt"] + 4*r["qd"] + r["qs"] + r["qz"] + 2*r["kz"]

def v18_tuple(r):
    # 18D tuple (per spec)
    return (
        r["ThetaHat"],
        r["nt"], r["nf"], r["nm"],
        r["km"], r["kt"], r["kd"], r["ka"], r["kz"],
        r["qa"], r["qt"], r["qd"], r["qs"], r["qz"],
        r["AN"], r["AK"], r["AQ"],
        r["hamzah_marker"],
    )

def cod_tokens(tokens, L):
    total = {k:0 for k in NUM_KEYS}
    for t in tokens:
        total = add(total, L[t])
    return total

def run(path="HL18_tests_ext.yaml"):
    data = yaml.safe_load(open(path, "r", encoding="utf-8"))
    L = data["letters_master_csv"]

    # A) per-letter derived formula checks
    for h, r in L.items():
        # ThetaDeg check
        assert r["ThetaDeg"] == 90 * r["ThetaHat"], f"ThetaDeg mismatch {h}"

        # U check
        u = derived_U(r)
        assert u == r["U"], f"U mismatch {h}: derived {u} vs table {r['U']}"

        # rho check
        rho = r["ThetaHat"] - r["U"]
        assert rho == r["rho"], f"rho mismatch {h}: derived {rho} vs table {r['rho']}"

        # AN/AK/AQ checks
        AN = r["nt"] + r["nf"] + r["nm"]
        AK = r["km"] + r["kt"] + r["kd"] + r["ka"] + r["kz"]
        AQ = r["qa"] + r["qt"] + r["qd"] + r["qs"] + r["qz"]
        assert AN == r["AN"], f"AN mismatch {h}"
        assert AK == r["AK"], f"AK mismatch {h}"
        assert AQ == r["AQ"], f"AQ mismatch {h}"

    # B) string aggregation checks (U/rho + cong)
    for t in data["urho_string_tests"]:
        name = t["name"]
        exp = t["expect"]

        if "w" in t:
            agg = cod_tokens(t["w"], L)
        else:
            agg1 = cod_tokens(t["w1"], L)
            agg2 = cod_tokens(t["w2"], L)
            if exp.get("cong", False):
                assert v18_tuple(agg1) == v18_tuple(agg2), f"cong fail {name}"
            agg = agg1

        assert agg["ThetaHat"] == exp["ThetaHat"], f"ThetaHat mismatch {name}"
        assert agg["U"] == exp["U"], f"U mismatch {name}"
        assert agg["rho"] == exp["rho"], f"rho mismatch {name}"

        # ThetaHat = U + rho must hold
        assert agg["ThetaHat"] == agg["U"] + agg["rho"], f"ThetaHat != U+rho {name}"

        # U formula must match aggregated components
        U2 = agg["qt"] + 4*agg["qd"] + agg["qs"] + agg["qz"] + 2*agg["kz"]
        assert U2 == agg["U"], f"U formula mismatch {name}: {U2} vs {agg['U']}"

    # C) injective check for v18
    seen = defaultdict(list)
    for h, r in L.items():
        seen[v18_tuple(r)].append(h)
    collisions = {vec: hs for vec, hs in seen.items() if len(hs) > 1}

    inj = data["injective_v18_test"]
    if inj["expect_injective"]:
        assert not collisions, f"NOT injective v18: {collisions}"
        assert len(seen) == inj["expect_unique_count"], "unique count mismatch"

    print("PASS: derived per-letter (U,rho,AN,AK,AQ,ThetaDeg), PASS: string U/rho aggregation, PASS: injective v18.")

if __name__ == "__main__":
    run()
