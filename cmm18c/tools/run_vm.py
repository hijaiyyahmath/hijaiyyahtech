#!/usr/bin/env python3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="CMM-18C Virtual Machine (CORE-only)")
    parser.add_argument("input", nargs="?", help="Path to .cmm bytecode file")
    parser.add_argument("--trace", action="store_true", help="Enable instruction tracing")
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        sys.exit(0)

    print(f"Running {args.input}...")

if __name__ == "__main__":
    main()
