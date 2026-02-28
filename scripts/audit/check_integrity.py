import json
from collections import Counter

path = "hl-release-HL-18-v1.0/ST-28-v0.1.json"
with open(path, "r", encoding="utf-8") as f:
    doc = json.load(f)

tags = [x["tag36_hex"] for x in doc["letters"]]
counts = Counter(tags)

collisions = {tag: count for tag, count in counts.items() if count > 1}
if collisions:
    print(f"COLLISIONS FOUND: {len(collisions)} tags are multi-valent")
    for tag, count in collisions.items():
        letters = [x["letter"] for x in doc["letters"] if x["tag36_hex"] == tag]
        print(f"  Tag {tag} -> {letters}")
else:
    print("PASS: All 28 Tag36 hashes are unique.")

vortices = [(x["letter"], x["vortex_count"]) for x in doc["letters"] if x["vortex_count"] != 0]
print(f"Vortex Checks: {vortices}")
