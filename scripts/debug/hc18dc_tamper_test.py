#!/usr/bin/env python3
import json
import subprocess
import os
import sys

# Paths
TV_PATH = "tests/vectors/hc18dc_enc_tv01.json"
RUNNER_SCRIPT = "hc18dc_enc_tv_runner.py"

def run_runner(path):
    """Runs the runner script and returns the return code and output."""
    res = subprocess.run([sys.executable, RUNNER_SCRIPT, path], capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr

def load_tv():
    with open(TV_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tv(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def test_tamper_ciphertext():
    print("--- Test Tamper 1: Modify 1 nibble in ciphertext ---")
    tv = load_tv()
    ct = tv["expected"]["ciphertext_hex"]
    # flip first nibble
    first = ct[0]
    flipped = '0' if first != '0' else '1'
    tv["expected"]["ciphertext_hex"] = flipped + ct[1:]
    
    tmp_path = "tests/vectors/hc18dc_enc_tv01_tamper_ct.json"
    save_tv(tv, tmp_path)
    
    code, out, err = run_runner(tmp_path)
    os.remove(tmp_path)
    
    if code != 0 and "ciphertext_hex mismatch" in out + err:
        print("[OK] Tamper detected (ciphertext mismatch)")
    elif code != 0 and "tag_hex mismatch" in out + err:
         print("[OK] Tamper detected (tag mismatch - ciphertext change affects tag calculation)")
    else:
        print(f"FAIL: Tamper NOT detected. Code: {code}")
        print("Output:", out)
        print("Error:", err)
        return False
    return True

def test_tamper_tag():
    print("--- Test Tamper 2: Modify 1 byte in tag ---")
    tv = load_tv()
    tag = tv["expected"]["tag_hex"]
    # flip last nibble
    last = tag[-1]
    flipped = '0' if last != '0' else '1'
    tv["expected"]["tag_hex"] = tag[:-1] + flipped
    
    tmp_path = "tests/vectors/hc18dc_enc_tv01_tamper_tag.json"
    save_tv(tv, tmp_path)
    
    code, out, err = run_runner(tmp_path)
    os.remove(tmp_path)
    
    if code != 0 and "tag_hex mismatch" in out + err:
        print("[OK] Tamper detected (tag mismatch)")
    else:
        print(f"FAIL: Tamper NOT detected. Code: {code}")
        print("Output:", out)
        print("Error:", err)
        return False
    return True

def main():
    if not os.path.exists(RUNNER_SCRIPT):
        print(f"Error: {RUNNER_SCRIPT} not found.")
        sys.exit(1)
    if not os.path.exists(TV_PATH):
        print(f"Error: {TV_PATH} not found.")
        sys.exit(1)

    print("Running Baseline (should PASS)...")
    code, out, err = run_runner(TV_PATH)
    if code != 0:
        print("Baseline FAILED!")
        print(out, err)
        sys.exit(1)
    print("[OK] Baseline PASS")

    s1 = test_tamper_ciphertext()
    s2 = test_tamper_tag()

    if s1 and s2:
        print("\nALL TAMPER TESTS PASSED.")
    else:
        print("\nTAMPER TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
