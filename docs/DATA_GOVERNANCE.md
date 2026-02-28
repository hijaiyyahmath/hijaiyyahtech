# DATA GOVERNANCE POLICY — Hijaiyah-Codex

Status: NORMATIVE / IMMUTABLE BASELINE

## 1. Source of Truth
The following files are designated as the **Primary Bensin (Source of Truth)**:
- `MH-28-v1.0-18D.csv` (Root)
- `csgi/CSGI-28-v1.0.json` (CSGI Module)

## 2. Immutability Rules
- **No In-Place Edits**: These files MUST NOT be modified in-place.
- **Versioning**: Any change to these files requires a repository-wide release bump (e.g., v1.0 -> v1.1).
- **Audit Requirement**: Any modification must be accompanied by a recalculated Groebner basis and Normaliz verification in `cmm18c/` and `normaliz/`.

## 3. Hash Integrity
Every release must be signed and hashed. The integrity of these files is verified by:
- `scripts/env_check.py`
- `hisa-vm/src/hisavm/master.py`

## 4. Replication Policy
Sub-modules (e.g., `hl-release-HL-18-v1.0`) may contain copies of these files for self-containment. In the event of a discrepancy, the **Root Version** always prevails.

## 5. Metadata Sync
All `spec/` documents referencing these files (e.g., `HISA_ISA_TABLE.md`) must be updated concurrently to reflect the new dimensions, weights, or hashes.
