import hashlib

def get_sha256(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

files = ["MH-28-v1.0-18D.csv", "MH_18x28.in", "MH_18x28.out"]
for f in files:
    try:
        print(f"{f}: {get_sha256(f)}")
    except FileNotFoundError:
        print(f"{f}: Not found")
