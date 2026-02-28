import json

path = "hl-release-HL-18-v1.0/ST-28-v0.1.json"
try:
    with open(path, "r", encoding="utf-8") as f:
        doc = json.load(f)
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# Table
print("## Results\n")
print("| Letter | Tag36 | JIM_VORTEX_count | RLE Len |")
print("|--------|-------|------------------|---------|")
for x in doc["letters"]:
    let = x["letter"]
    tag = x["tag36_hex"]
    v = x["vortex_count"]
    rle = len(x["trace_rle"])
    print(f"| {let} | `{tag}` | {v} | {rle} |")

# Jeem Record
jeem = next(x for x in doc["letters"] if x["letter"] == "ج")
print("\n### Jeem Verification Record")
print("```json")
print(json.dumps(jeem, indent=2, ensure_ascii=False))
print("```")
