#!/usr/bin/env python3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="CMM-18C Disassembler")
    parser.add_argument("input", nargs="?", help="Path to .cmm bytecode file")
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(0)

    print(f"Disassembling {args.input}...")

if __name__ == "__main__":
    main()
