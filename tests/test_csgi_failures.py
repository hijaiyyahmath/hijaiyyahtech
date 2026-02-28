import os
import sys
import unittest

# Add root directory to path to import validator
sys.path.append(os.getcwd())
from verify_hl18_release import validate_csgi_dataset

class TestCSGIFailures(unittest.TestCase):
    def run_fail_test(self, filename, expected_err):
        path = os.path.join("tests", "fixtures", "csgi_fail", filename)
        print(f"Testing {filename}...")
        with self.assertRaises(ValueError) as cm:
            validate_csgi_dataset(path)
        
        err_msg = str(cm.exception)
        print(f"  Got error: {err_msg}")
        self.assertIn(expected_err, err_msg)

    def test_dup_key(self):
        self.run_fail_test("dup_key.json", "DUPLICATE_KEY_OR_NFC_COLLISION")

    def test_nfc_key_collision(self):
        self.run_fail_test("nfc_key_collision.json", "DUPLICATE_KEY_OR_NFC_COLLISION")

    def test_bad_polyline_jump(self):
        self.run_fail_test("bad_polyline_jump.json", "violates 8-neighborhood")

    def test_bad_endpoint_mismatch(self):
        self.run_fail_test("bad_endpoint_mismatch.json", "edge endpoint mismatch")

    def test_bad_degree_mismatch(self):
        self.run_fail_test("bad_degree_mismatch.json", "degree mismatch")

if __name__ == "__main__":
    unittest.main()
