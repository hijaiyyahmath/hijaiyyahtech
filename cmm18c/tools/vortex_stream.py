import argparse
import json
import os
import sys

# Ensure cmm18c is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cmm18c.master import load_master_csv
from cmm18c.vortex import jim_vector_from_master, vortex_mask_from_jim, vc1_stream

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True, help="path to MH-28-v1.0-18D.csv")
    ap.add_argument("--letters", required=True, help="string of letters (e.g. جحخ) or space-separated ids")
    args = ap.parse_args()

    master = load_master_csv(args.master)  # returns dict: letter_id -> v18 list
    J = jim_vector_from_master(master)
    mask = vortex_mask_from_jim(J)

    # Clean up letters input
    input_str = args.letters.replace(" ", "")
    
    Vs = []
    actual_letters = []
    for ch in input_str:
        if ch not in master:
            # Try normalization
            import unicodedata
            nch = unicodedata.normalize("NFC", ch)
            if nch not in master:
                 raise SystemExit(f"UNKNOWN_LETTER_ID: {ch!r} (NFC: {nch!r})")
            ch = nch
        Vs.append(master[ch])
        actual_letters.append(ch)

    bits, energies = vc1_stream(Vs, mask)
    out = {
        "letters": actual_letters,
        "bits": bits,
        "energies": [e.__dict__ for e in energies],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
