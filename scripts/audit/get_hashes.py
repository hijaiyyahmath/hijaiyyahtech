import hashlib, os
d = 'hl-release-HL-18-v1.0'
files = [
    'generate_st28_full.py', 
    'validate_st28.py', 
    'verify_vortex.py', 
    'ST-28-v0.1.json', 
    'h28_tag36_table.jsonl', 
    'HijaiyyahGlyphPack.zip'
]
for f in files:
    p = os.path.join(d, f)
    if os.path.exists(p):
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        print(f"{f}: {h}")
    else:
        print(f"{f}: MISSING")
