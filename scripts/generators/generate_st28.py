import json
import csv
import os
import sys

# Add the src path to sys.path so we can import hijaiyahlang
sys.path.append(os.path.abspath("hijaiyahlang-hl18/src"))
from hijaiyahlang.core import audit_v18

csv_path = "hl-release-HL-18-v1.0/MH-28-v1.0-18D.csv"
output_path = "hl-release-HL-18-v1.0/ST-28-v0.1.json"

# Jeem trace extracted from Arabic_letter_Jeem.png
JEEM_TRACE = [
    ["SEG_Q", 1], ["D0", 166], ["D1", 1], ["D2", 1], ["TURN+Q1", 1], ["D2", 106], ["D1", 1], ["D0", 1], ["TURN-Q1", 1], ["D0", 225], ["D1", 1], ["D0", 1]
]

def generate():
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return

    letters = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            letter = row["letter"]
            # Fields for v18
            v18_fields = [
                "ThetaHat", "nt", "nf", "nm", "km", "kt", "kd", "ka", "kz",
                "qa", "qt", "qd", "qs", "qz", "AN", "AK", "AQ", "hamzah_marker"
            ]
            v18 = [int(row[field]) for field in v18_fields]
            
            # Audit
            audit = audit_v18(v18)
            audit_dict = {
                "ok": audit.ok,
                "U": audit.U,
                "rho": audit.rho,
                "mod4": audit.mod4,
                "checks": audit.checks
            }
            
            # Trace
            trace = []
            if letter == "ج":
                trace = JEEM_TRACE
            
            letters.append({
                "letter": letter,
                "v18": v18,
                "audit": audit_dict,
                "trace": trace
            })

    output = {
        "suite": "HL-18-v1.0-trace",
        "version": "0.1",
        "dataset_file": "MH-28-v1.0-18D.csv",
        "letters": letters
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    generate()
