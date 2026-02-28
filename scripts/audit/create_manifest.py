import hashlib, json, sys, os, rfc8785

def get_sha256(path):
    if not os.path.exists(path): return "0000000000000000000000000000000000000000000000000000000000000000"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def get_spec_digest(json_path):
    if not os.path.exists(json_path): return "0000000000000000000000000000000000000000000000000000000000000000"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    spec_block = data.get("spec", {})
    # RFC 8785 JCS Canonicalization (returns bytes)
    canonical_bytes = rfc8785.dumps(spec_block)
    digest = hashlib.sha256(canonical_bytes).hexdigest()
    if len(digest) != 64:
        raise ValueError(f"Invalid SHA-256 length: {len(digest)}")
    return digest

# Working directory inside release folder for clean relative paths
os.chdir("hl-release-HL-18-v1.0")

manifest = {
  "release": "ST-28-v0.1",
  "timestamp": "2026-02-15T05:00:00Z",
  "environment": {
    "python_runtime": "3.11.8",
    "libraries": {
      "opencv-python": "4.11.0.86",
      "scikit-image": "0.25.1",
      "numpy": "2.2.3",
      "networkx": "3.6.1",
      "pillow": "12.1.1",
      "rfc8785": "0.1.4"
    }
  },
  "upstream_hl_dataset": {
    "file": "MH-28-v1.0-18D.csv",
    "sha256": "6020188a7929ddf6231ac2f61c96ac0007761f8d0512dd7ce2ffd2ec018f12bd"
  },
  "spec_lock": {
    "digest_sha256": get_spec_digest("ST-28-v0.1.json"),
    "method": "sha256(RFC8785_Canonical(spec_block))"
  },
  "integrity": {
    "generator_script": {
      "file": "generate_st28_full.py",
      "sha256": get_sha256("generate_st28_full.py")
    },
    "source_glyphs": {
      "file": "HijaiyahGlyphPack.zip",
      "sha256": get_sha256("HijaiyahGlyphPack.zip")
    },
    "validator_tool": {
      "file": "validate_st28.py",
      "sha256": get_sha256("validate_st28.py")
    },
    "vortex_auditor": {
      "file": "verify_vortex.py",
      "sha256": get_sha256("verify_vortex.py")
    },
    "verify_runner": {
      "file": "verify_st28_release.py",
      "sha256": get_sha256("verify_st28_release.py")
    },
    "output_dataset": {
      "file": "ST-28-v0.1.json",
      "sha256": get_sha256("ST-28-v0.1.json")
    },
    "audit_table": {
      "file": "h28_tag36_table.jsonl",
      "sha256": get_sha256("h28_tag36_table.jsonl")
    }
  }
}

# Add self-hash (Release Seal)
# Hashing the manifest content EXCLUDING the manifest_sha256 field itself
manifest_canonical_bytes = rfc8785.dumps(manifest)
release_seal = hashlib.sha256(manifest_canonical_bytes).hexdigest()
manifest["manifest_sha256"] = release_seal

with open("ST28_MANIFEST.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"Created ST28_MANIFEST.json inside hl-release-HL-18-v1.0/")
print(f"Release Seal (manifest_sha256): {release_seal}")
