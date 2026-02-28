from __future__ import annotations
import argparse
from hisavm.asm import assemble_text
from hisavm.bytecode import save_bin

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    args = ap.parse_args()

    text = open(args.inp, "r", encoding="utf-8").read()
    b = assemble_text(text)
    save_bin(args.out, b)
    print(f"Wrote {len(b)} bytes -> {args.out}")

if __name__ == "__main__":
    main()
