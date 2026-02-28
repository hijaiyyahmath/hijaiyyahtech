import json
import hashlib

def verify():
    path = "hl-release-HL-18-v1.0/ST-28-v0.1.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
    except FileNotFoundError:
        print("ST-28-v0.1.json not found.")
        return

    # 1. Vortex Count
    res = [(x["letter"], x["vortex_count"]) for x in doc["letters"] if x["vortex_count"]!=0]
    print(f"Vorcex!=0: {res}")
    
    # 2. SHA-256
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    print(f"SHA-256: {sha}")
    
    # 3. Jeem Check
    jeem = next((x for x in doc["letters"] if x["letter"] == "ج"), None)
    if jeem:
        raw = jeem.get("trace_raw_rle", [])
        norm = jeem.get("trace_rle", [])
        print(f"Jeem Raw RLE Turn Tokens: {[t[0] for t in raw if 'TURN' in t[0]]}")
        print(f"Jeem Norm RLE Turn Tokens: {[t[0] for t in norm if 'TURN' in t[0] or 'VORTEX' in t[0]]}")

if __name__ == "__main__":
    verify()
