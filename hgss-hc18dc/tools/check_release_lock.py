from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


RELEASE_VERSION = "HGSS-HCVM-v1.HC18DC"
RELEASE_COMMIT = "e392c68"

# Documents considered normative for release lock.
# You can extend this list; script also scans spec/*.md by default.
ROOT_DOCS = [
    "AUDITORS_QUICKSTART.md",
    "WALKTHROUGH_HGSS.md",
    "audit_report.md",
    "audit_demo_plan.md",
    "implementation_plan.md",
    "task.md",
    "RELEASE_ATTESTATION.md",
]

SPEC_DOCS_REQUIRED = [
    "spec/AUDIT_EVIDENCE_SCHEMA.md",
    "spec/HSM_INTEGRATION.md",
    "spec/LEASE_AUTH_SIGNATURE.md",
    "spec/NONCE_RANGE_LEASING_PROTOCOL.md",
    "spec/LEASING_SERVICE_ARCHITECTURE.md",
    "spec/PRODUCTION_INTEGRATION_GUIDE.md",
    "spec/MONITORING_RUNBOOK.md",
]

SCHEMA_FROZEN_MARKERS = [
    "FROZEN",
    "NORMATIVE",
    RELEASE_VERSION,
    RELEASE_COMMIT,
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def must_contain(text: str, needle: str) -> bool:
    return needle in text


def iter_md_files_under_spec(root: Path) -> List[Path]:
    spec_dir = root / "spec"
    if not spec_dir.exists():
        return []
    return sorted(spec_dir.rglob("*.md"))


def check_file(path: Path, required: List[str]) -> List[str]:
    errs = []
    if not path.exists():
        return [f"MISSING_FILE: {path.as_posix()}"]
    try:
        txt = read_text(path)
    except Exception as e:
        return [f"READ_FAIL: {path.as_posix()} ({e})"]

    for r in required:
        if r not in txt:
            errs.append(f"MISSING_TOKEN: {path.as_posix()} missing {r!r}")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repo root (default: .)")
    ap.add_argument("--strict-spec-scan", action="store_true",
                    help="also enforce version+commit in ALL spec/*.md files (not only required list)")
    args = ap.parse_args()

    root = Path(args.root).resolve()

    errors: List[str] = []

    # 1) Required docs must exist and contain version+commit
    required_paths = [root / p for p in ROOT_DOCS] + [root / p for p in SPEC_DOCS_REQUIRED]
    for p in required_paths:
        errors += check_file(p, [RELEASE_VERSION, RELEASE_COMMIT])

    # 2) Schema file must contain FROZEN markers
    schema_path = root / "spec" / "AUDIT_EVIDENCE_SCHEMA.md"
    if schema_path.exists():
        try:
            schema_txt = read_text(schema_path)
            for m in SCHEMA_FROZEN_MARKERS:
                if m not in schema_txt:
                    errors.append(f"SCHEMA_NOT_FROZEN: missing {m!r} in {schema_path.as_posix()}")
        except Exception as e:
            errors.append(f"READ_FAIL: {schema_path.as_posix()} ({e})")

    # 3) Optional: strict scan every spec/*.md must contain version+commit
    if args.strict_spec_scan:
        for p in iter_md_files_under_spec(root):
            errors += check_file(p, [RELEASE_VERSION, RELEASE_COMMIT])

    if errors:
        print("[FAIL] Release lock check failed:")
        for e in errors:
            print("  -", e)
        return 2

    print("[PASS] Release lock check OK.")
    print(f"  version: {RELEASE_VERSION}")
    print(f"  commit:  {RELEASE_COMMIT}")
    print(f"  docs_checked: {len(required_paths)}")
    if args.strict_spec_scan:
        print(f"  spec_md_scanned: {len(iter_md_files_under_spec(root))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
