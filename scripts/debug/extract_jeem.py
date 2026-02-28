import json

with open("hl-release-HL-18-v1.0/ST-28-v0.1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for letter in data["letters"]:
    if letter["letter"] == "ج":
        print(json.dumps(letter, indent=2, ensure_ascii=False))
        break
