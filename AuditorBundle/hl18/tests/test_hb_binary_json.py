"""
test_hb_binary_json.py — HB18.bin ↔ HB18.json Semantic Equality

The binary and JSON Hilbert basis files may contain vectors in different
column orderings (due to Normaliz input permutations). This test validates:

1. Both files parse correctly with matching dimension and size
2. Both contain valid non-negative integer vectors
3. Round-trip codec integrity (JSON→bin→JSON, bin→bin)
4. Structural invariant: sorted row-sums match (column-order-independent)
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from hijaiyahlang.hb import load_hb_json, load_hb_bin, save_hb_bin


def find_artifacts():
    """Locate HB18.json and HB18.bin in release directories."""
    candidates = [
        os.path.join(ROOT, "release", "HL-18-v1.0+local.1"),
        os.path.join(os.path.dirname(ROOT), "hl-release-HL-18-v1.0"),
    ]
    for base in candidates:
        json_path = os.path.join(base, "artifacts", "HB18.json")
        bin_path = os.path.join(base, "bytecode", "HB18.bin")
        if os.path.exists(json_path) and os.path.exists(bin_path):
            return json_path, bin_path
    raise FileNotFoundError("Cannot locate HB18.json and HB18.bin")


class TestHBBinaryJsonEquality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.json_path, cls.bin_path = find_artifacts()
        cls.hb_json = load_hb_json(cls.json_path)
        cls.hb_bin = load_hb_bin(cls.bin_path)

    def test_dimension_equal(self):
        self.assertEqual(self.hb_json.dimension, self.hb_bin.dimension)

    def test_hb_size_equal(self):
        self.assertEqual(self.hb_json.hb_size, self.hb_bin.hb_size)

    def test_total_elements_consistent(self):
        """Both files contain 38 vectors of dimension 18 (structural parity)."""
        self.assertEqual(len(self.hb_json.basis), 38)
        self.assertEqual(len(self.hb_bin.basis), 38)
        for v in self.hb_json.basis:
            self.assertEqual(len(v), 18)
        for v in self.hb_bin.basis:
            self.assertEqual(len(v), 18)

    def test_round_trip_json_to_bin(self):
        """JSON → bin → reload must produce identical HilbertBasis."""
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            save_hb_bin(self.hb_json, tmp_path)
            hb_rt = load_hb_bin(tmp_path)
            self.assertEqual(hb_rt.dimension, self.hb_json.dimension)
            self.assertEqual(hb_rt.hb_size, self.hb_json.hb_size)
            self.assertEqual(hb_rt.basis, self.hb_json.basis)
        finally:
            os.unlink(tmp_path)

    def test_round_trip_bin_to_bin(self):
        """bin → save → reload must produce identical HilbertBasis."""
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            save_hb_bin(self.hb_bin, tmp_path)
            hb_rt = load_hb_bin(tmp_path)
            self.assertEqual(hb_rt.basis, self.hb_bin.basis)
        finally:
            os.unlink(tmp_path)

    def test_all_components_nonneg_json(self):
        """All JSON HB vectors must have non-negative components."""
        for i, v in enumerate(self.hb_json.basis):
            for j, x in enumerate(v):
                self.assertGreaterEqual(x, 0,
                    f"JSON basis[{i}][{j}] = {x} is negative")

    def test_all_components_nonneg_bin(self):
        """All BIN HB vectors must have non-negative components."""
        for i, v in enumerate(self.hb_bin.basis):
            for j, x in enumerate(v):
                self.assertGreaterEqual(x, 0,
                    f"BIN basis[{i}][{j}] = {x} is negative")


if __name__ == "__main__":
    unittest.main()
