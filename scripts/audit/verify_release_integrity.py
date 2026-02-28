import hashlib, os, sys, json
try:
    import yaml
except ImportError:
    yaml = None

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def must_equal(name, got, exp):
    if got != exp:
        raise SystemExit(f"FAIL {name}: got {got} != expected {exp}")

def main(spec_path="HL18_release_integrity.yaml", root="."):
    # Handle YAML or JSON
    if spec_path.endswith(".json"):
        spec = json.load(open(spec_path, "r", encoding="utf-8"))
    else:
        try:
            spec = yaml.safe_load(open(spec_path, "r", encoding="utf-8"))
        except ImportError:
            # Fallback if yaml not found but json version exists
            json_spec = spec_path.replace(".yaml", ".json")
            if os.path.exists(json_spec):
                print(f"DEBUG: yaml module missing, falling back to {json_spec}")
                spec = json.load(open(json_spec, "r", encoding="utf-8"))
            else:
                raise

    # dataset
    d = spec["dataset"]["mh_28_v1_0_18d_csv"]
    p = os.path.join(root, d["path"])
    must_equal("dataset sha256", sha256_file(p), d["sha256"])

    # normaliz (optional if files present)
    nz = spec.get("normaliz", None)
    if nz:
        for k in ["input", "output"]:
            p = os.path.join(root, nz[k]["path"])
            if os.path.exists(p):
                must_equal(f"normaliz {k} sha256", sha256_file(p), nz[k]["sha256"])

    # artifacts
    for a in spec["artifacts"]:
        p = os.path.join(root, a["path"])
        must_equal(f"artifact {a['path']}", sha256_file(p), a["sha256"])

    print("PASS: Release integrity verified (dataset + artifacts + optional normaliz files).")

if __name__ == "__main__":
    main(*sys.argv[1:])  # args: [spec_path] [root]
