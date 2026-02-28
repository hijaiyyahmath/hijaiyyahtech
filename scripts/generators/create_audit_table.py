import json

path = "hl-release-HL-18-v1.0/ST-28-v0.1.json"
out_path = "hl-release-HL-18-v1.0/h28_tag36_table.jsonl"

with open(path, "r", encoding="utf-8") as f:
    doc = json.load(f)

with open(out_path, "w", encoding="utf-8") as f:
    for x in doc["letters"]:
        entry = {"letter": x["letter"], "tag36_hex": x["tag36_hex"]}
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Created {out_path}")
print("\n[(letter, tag36_hex)] for 28 letters:")
tags = [(x["letter"], x["tag36_hex"]) for x in doc["letters"]]
print(tags)
print(f"\nUnique tags count: {len(set(t[1] for t in tags))}")
