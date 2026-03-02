import os
import pytest
from hijaiyyahlang.dataset import load_mh28_csv, cod_word
from hijaiyyahlang.core import audit_v18

@pytest.mark.skipif(not os.path.exists("../hl-release-HL-18-v1.0/MH-28-v1.0-18D.csv"), reason="Release CSV not found")
def test_letters_injective():
    """Fail if any two of the 28 letters share the same v18 vector."""
    csv_path = "../hl-release-HL-18-v1.0/MH-28-v1.0-18D.csv"
    ds = load_mh28_csv(csv_path)
    vectors = {}
    for letter, v in ds.table.items():
        v_tuple = tuple(v)
        if v_tuple in vectors:
            pytest.fail(f"Collision: letters '{letter}' and '{vectors[v_tuple]}' share the same v18: {v}")
        vectors[v_tuple] = letter

@pytest.mark.skipif(not os.path.exists("../hl-release-HL-18-v1.0/MH-28-v1.0-18D.csv"), reason="Release CSV not found")
def test_letters_audit():
    """Fail if any of the 28 letters fails the HL-18 audit identities."""
    csv_path = "../hl-release-HL-18-v1.0/MH-28-v1.0-18D.csv"
    ds = load_mh28_csv(csv_path)
    for letter, v in ds.table.items():
        ar = audit_v18(v)
        assert ar.ok, f"Audit failed for letter '{letter}': {ar.checks}"

def test_audit_pass_all_letters():
    # Attempt to find the CSV in the expected release folder relative to this test
    # (assuming we run from repo root)
    csv_path = "../hl-release-HL-18-v1.0/MH-28-v1.0-18D.csv"
    if not os.path.exists(csv_path):
        pytest.skip("Release CSV not found for smoke test")
        
    ds = load_mh28_csv(csv_path)
    for h,v in ds.table.items():
        ar = audit_v18(v)
        assert ar.ok, (h, v, ar)
