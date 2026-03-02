#!/usr/bin/env python3
import json, hashlib, sys, os, rfc8785, re
from collections import Counter

def sha256_file(path: str) -> str:
    """Calculates SHA-256 hash of a file. Returns error string on failure."""
    try:
        h = hashlib.sha256()
        if not os.path.exists(path):
            return "MISSING"
        if not os.path.isfile(path):
            return "ERROR:NotARegularFile"
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024*1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError as e:
        return f"ERROR:{e.__class__.__name__}"

def fail(msg): 
    print("FAIL:", msg)
    sys.exit(1)

def ok(msg):
    print(" [OK]", msg)

def is_sha256(s):
    return bool(re.fullmatch(r"[0-9a-f]{64}", str(s).lower()))

def is_tag36(s):
    # Tag36 is 36-bit, represented as 9-digit hex
    return bool(re.fullmatch(r"[0-9a-f]{9}", str(s).lower()))

def main(manifest_path="ST28_MANIFEST.json"):
    if not os.path.exists(manifest_path):
        fail(f"Manifest not found: {manifest_path}")
        
    # Resolve base directory relative to manifest for forensic path safety
    base_dir = os.path.dirname(os.path.abspath(manifest_path))
    base_real = os.path.realpath(base_dir)

    with open(manifest_path, "r", encoding="utf-8") as f:
        man = json.load(f)

    # Forensic Hardening: Check all normative required keys
    required_keys = ["release", "integrity", "manifest_sha256", "upstream_hl_dataset", "spec_lock"]
    for rk in required_keys:
        if rk not in man:
            fail(f"Malformed manifest: missing required key '{rk}'")

    print(f"--- ST-28 Release Integrity Audit: {man['release']} ---")
    
    # --- 1. Manifest Self-Seal Check (JCS) ---
    seal_expected = man.pop("manifest_sha256")
    if not is_sha256(seal_expected):
        fail(f"Invalid manifest_sha256 format: {seal_expected}")
    
    canonical_bytes = rfc8785.dumps(man)
    seal_got = hashlib.sha256(canonical_bytes).hexdigest()
    if seal_got.lower() != seal_expected.lower():
        fail(f"Manifest seal mismatch! expected={seal_expected} got={seal_got}")
    ok(f"Manifest Seal Verified: {seal_expected[:12]}...")

    # Restore the manifest_sha256
    man["manifest_sha256"] = seal_expected

    # --- 2. Strict Forensic Self-Lock (Path & Hash) ---
    runner_info = man["integrity"].get("verify_runner")
    if not runner_info:
        fail("Missing 'verify_runner' in manifest integrity block")
    
    runner_file = runner_info.get("file")
    runner_sha  = runner_info.get("sha256", "")
    if not runner_file or not is_sha256(runner_sha):
        fail("Malformed verify_runner node (missing file or sha256)")

    # Path Safety: No absolute paths allowed for integrity files
    if os.path.isabs(runner_file):
        fail(f"Security Policy Violation: verify_runner.file must be relative, got absolute: {runner_file}")

    # Strict Path Locking (commonpath check)
    manifest_runner_path = os.path.realpath(os.path.join(base_real, runner_file))
    if os.path.commonpath([base_real, manifest_runner_path]) != base_real:
        fail(f"Security Policy Violation: verify_runner path escapes base_dir: {runner_file}")

    this_path = os.path.realpath(__file__)
    if this_path != manifest_runner_path:
        fail(f"Self-lock path mismatch!\n  Executing: {this_path}\n  Manifest:  {manifest_runner_path}")

    # Hash Locking
    got = sha256_file(this_path).lower()
    if got.startswith("ERROR:"):
        fail(f"Self-lock hash error: {got}")
    
    exp = runner_sha.lower()
    if got != exp:
        fail(f"Self-lock hash mismatch!\n  Script altered or out of sync with manifest.\n  Exp: {exp}\n  Got: {got}")

    ok("Self-Lock Verified: execution matches manifest identity")

    # --- 3. Secure File Integrity Verification ---
    def check_file(node, label):
        filename = node.get("file")
        exp  = node.get("sha256", "").lower()
        if not filename or not exp:
            fail(f"Malformed integrity node for {label}")
        if not is_sha256(exp):
            fail(f"Invalid SHA-256 hash for {label}: {exp}")
        
        # Path safety: reject absolute paths and prevent jailbreak (commonpath)
        if os.path.isabs(filename):
            fail(f"Security Policy Violation: Absolute path forbidden for {label}: {filename}")
        
        full_path = os.path.realpath(os.path.join(base_real, filename))
        if os.path.commonpath([base_real, full_path]) != base_real:
            fail(f"Security Policy Violation: Path escape detected for {label}: {filename}")
        
        if not os.path.isfile(full_path):
            fail(f"{label} must be a regular file: {filename}")

        got = sha256_file(full_path).lower()
        if got.startswith("ERROR:"):
            fail(f"{label} hash error: {got}")
        if got != exp:
            fail(f"{label} hash mismatch: {filename} expected={exp} got={got}")
        ok(f"{label}: {filename}")

    # Verify upstream and all integrity components
    check_file(man["upstream_hl_dataset"], "upstream_hl_dataset")
    for key in ["generator_script", "source_glyphs", "validator_tool", 
                "vortex_auditor", "output_dataset", "audit_table"]:
        check_file(man["integrity"][key], key)

    # --- 4. Quality Audit: Hijaiyyah Set & Tag36 Uniqueness ---
    HIJAIYYAH_NFC = "ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن و هـ ي"
    hijaiyyah_set = set(HIJAIYYAH_NFC.split())
    audit_filename = man["integrity"]["audit_table"]["file"]
    
    # Path safe resolve for audit table
    audit_path = os.path.realpath(os.path.join(base_real, audit_filename))
    if not os.path.exists(audit_path):
        fail(f"Audit table file missing: {audit_path}")

    pairs = []
    with open(audit_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            try:
                obj = json.loads(line)
                letter = obj["letter"]
                tag = obj["tag36_hex"]
                
                if not is_tag36(tag):
                    fail(f"Invalid Tag36 format at {audit_filename}:{line_num}: {tag}")
                
                pairs.append((letter, tag))
            except (KeyError, json.JSONDecodeError) as e:
                fail(f"Malformed audit_table entry at line {line_num}: {e}")
    
    letters_seen = [p[0] for p in pairs]
    if len(letters_seen) != 28:
        fail(f"audit_table letters count must be 28; got {len(letters_seen)}")
    
    if set(letters_seen) != hijaiyyah_set:
        fail(f"audit_table missing letters: {hijaiyyah_set - set(letters_seen)}")
    
    tags = [p[1] for p in pairs]
    tag_counts = Counter(tags)
    dups = [t for t, n in tag_counts.items() if n > 1]
    if dups:
        fail(f"Tag36 Collision Detected (Non-Injective): {dups}")
    ok(f"Injective Hijaiyyah Set: 28/28 verified (Tag36 format OK)")

    # --- 5. Dataset Completeness & Cryptographic Gate Validation ---
    dataset_filename = man["integrity"]["output_dataset"]["file"]
    dataset_path = os.path.realpath(os.path.join(base_real, dataset_filename))
    if not os.path.exists(dataset_path):
        fail(f"Output dataset missing: {dataset_path}")
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        st = json.load(f)
    
    # Dataset letters completeness check
    letters = st.get("letters")
    if not isinstance(letters, list) or len(letters) != 28:
        fail(f"Dataset letters must be list of 28; got {type(letters)}")

    st_set = {x.get("letter") for x in letters}
    if st_set != hijaiyyah_set:
        fail(f"Dataset letter set mismatch: missing={hijaiyyah_set-st_set}")

    # Case-Insensitive Spec Block Digest Verification with strict format check
    spec_lock = man.get("spec_lock", {})
    spec_digest = spec_lock.get("digest_sha256")
    if not is_sha256(spec_digest):
        fail(f"Invalid spec_lock.digest_sha256 format: {spec_digest}")
    spec_sha_exp = spec_digest.lower()
    
    spec_block = st.get("spec", {})
    canonical_spec = rfc8785.dumps(spec_block)
    got_spec_sha = hashlib.sha256(canonical_spec).hexdigest().lower()
    if got_spec_sha != spec_sha_exp:
        fail(f"Spec block digest mismatch! expected={spec_sha_exp} got={got_spec_sha}")
    ok("Spec Block Lock Verified (RFC 8785 JCS)")

    # JIM Gate logic
    jeem = next((x for x in letters if x.get("letter") == "ج"), None)
    if not jeem:
        fail("Critical failure: Letter 'ج' (JEEM) missing in dataset")
        
    jcount = jeem.get("JIM_VORTEX_count", jeem.get("vortex_count", 0))
    if jcount != 1:
        fail(f"JIM gate failed: count(ج)={jcount}, expected 1")

    for x in letters:
        curr_letter = x.get("letter")
        if curr_letter == "ج": continue
        c0 = x.get("JIM_VORTEX_count", x.get("vortex_count", 0))
        if c0 != 0:
            fail(f"Non-JIM gate failed: '{curr_letter}' has JIM_VORTEX_count={c0}")

    print("\nPASS: ST-28 release integrity verified.")
    print(" - All SHA-256 locks and manifest seal verified")
    print(" - Forensically Clean: Strict Self-Lock & Path Safety enforced")
    print(" - Dataset quality: 28 letters present and unique")
    print(" - Cryptographic Gate: count(JEEM)=1; all others 0")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "ST28_MANIFEST.json"
    main(target)
