"""
test_hl_regression.py — Regression & Fuzzing Suite for HL-18

Covers:
1. All 28 letters pass audit_v18
2. Additive closure (v18(a) + v18(b) ∈ ℕ₀¹⁸)
3. Boundary: zero vector, max-component
4. Fuzz: random non-negative 18D vectors → audit_v18 must not crash
5. Determinism: same input → same result
"""
import os
import sys
import random
import csv
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from hijaiyyahlang.core import audit_v18, add18, sub18z, asN, mod18

V18_COLS = [
    "ThetaHat", "nt", "nf", "nm",
    "km", "kt", "kd", "ka", "kz",
    "qa", "qt", "qd", "qs", "qz",
    "AN", "AK", "AQ",
]
HAMZAH_ALTS = ["hamzah_marker", "hamzah", "varsigma", "epsilon", "eps"]


def load_letter_table():
    """Load 28 letter vectors from CSV with column mapping."""
    csv_path = os.path.join(ROOT, "MH-28-v1.0-18D.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(ROOT, "release",
                                "HL-18-v1.0+local.1", "MH-28-v1.0-18D.csv")
    table = {}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        header = [h.strip() for h in (r.fieldnames or [])]

        hamzah_col = None
        for alt in HAMZAH_ALTS:
            if alt in header:
                hamzah_col = alt
                break
        if hamzah_col is None:
            raise ValueError(f"No hamzah-marker column found in {header}")

        for row in r:
            letter = (row.get("letter") or "").strip()
            if not letter:
                continue
            v = [int(row[c]) for c in V18_COLS]
            v.append(int(row[hamzah_col]))
            table[letter] = v
    return table


class TestRegressionAllLetters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = load_letter_table()

    def test_28_letters_loaded(self):
        self.assertEqual(len(self.table), 28)

    def test_all_letters_audit_pass(self):
        """Every letter must pass audit_v18 with ok=True."""
        for letter, v in self.table.items():
            with self.subTest(letter=letter):
                result = audit_v18(v)
                self.assertTrue(result.ok,
                    f"Letter '{letter}' FAILED audit: {result.checks}")

    def test_rho_nonneg(self):
        """ρ must be ≥ 0 for all letters."""
        for letter, v in self.table.items():
            r = audit_v18(v)
            self.assertGreaterEqual(r.rho, 0,
                f"Letter '{letter}' has negative rho={r.rho}")


class TestAdditiveClosure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = load_letter_table()
        cls.letters = list(cls.table.keys())

    def test_pairwise_add_nonneg(self):
        """v18(a) + v18(b) must have all non-negative components."""
        for a in self.letters[:5]:
            for b in self.letters[:5]:
                s = add18(self.table[a], self.table[b])
                self.assertTrue(all(x >= 0 for x in s),
                    f"{a}+{b} has negative component: {s}")

    def test_add_audit_consistent(self):
        """Sum vectors should still satisfy structural formulas."""
        va = self.table["ب"]
        vb = self.table["ا"]
        s = add18(va, vb)
        # AN formula must still hold for the sum
        nt, nf, nm = s[1], s[2], s[3]
        AN = s[14]
        self.assertEqual(AN, nt + nf + nm)


class TestBoundary(unittest.TestCase):
    def test_zero_vector(self):
        """Zero vector should pass audit."""
        z = [0] * 18
        r = audit_v18(z)
        self.assertTrue(r.ok)
        self.assertEqual(r.U, 0)
        self.assertEqual(r.rho, 0)

    def test_wrong_dimension_raises(self):
        """Non-18D vector must raise ValueError."""
        with self.assertRaises(ValueError):
            audit_v18([1, 2, 3])

    def test_max_component(self):
        """Large values should not crash."""
        v = [100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        r = audit_v18(v)
        self.assertEqual(r.rho, 100)


class TestFuzzing(unittest.TestCase):
    FUZZ_ROUNDS = 200
    SEED = 42

    def test_random_vectors_no_crash(self):
        """Random non-negative 18D vectors must not crash audit_v18."""
        rng = random.Random(self.SEED)
        for _ in range(self.FUZZ_ROUNDS):
            v = [rng.randint(0, 20) for _ in range(18)]
            try:
                r = audit_v18(v)
            except Exception as e:
                self.fail(f"audit_v18 crashed on {v}: {e}")

    def test_random_determinism(self):
        """Same vector always produces the same audit result."""
        rng = random.Random(self.SEED)
        for _ in range(50):
            v = [rng.randint(0, 10) for _ in range(18)]
            r1 = audit_v18(v)
            r2 = audit_v18(v)
            self.assertEqual(r1, r2,
                f"Non-deterministic audit for {v}")


class TestMod18(unittest.TestCase):
    def test_mod4_identity(self):
        """mod18(v, 4) must produce all components in [0..3]."""
        v = [5, 7, 3, 0, 10, 2, 1, 4, 8, 6, 9, 11, 12, 13, 14, 15, 16, 17]
        m = mod18(v, 4)
        for x in m:
            self.assertIn(x, range(4))

    def test_mod_invalid_raises(self):
        with self.assertRaises(ValueError):
            mod18([0]*18, 0)


if __name__ == "__main__":
    unittest.main()
