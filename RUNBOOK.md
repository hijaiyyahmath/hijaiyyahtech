# RUNBOOK — Hijaiyyah-Codex Operations

## 1. Environment Setup

### UNIX/Linux/macOS (Makefile)
```bash
# 1. Initialize & Check Locks
make env

# 2. Run Test Suite
make test

# 3. Complete Demo Run
make all
```

### Windows (PowerShell)
```powershell
# Set Environment
$env:PYTHONPATH = ".;./hijaiyyahlang-hl18/src;./hisa-vm/src;./hgss-hc18dc/src;./hijaiyyah-ai-hgss/src"

# Run Suite
python scripts/env_check.py
python scripts/run_tests_all.py
python scripts/run_all.py
```

## 2. Forensic Auditing
To audit the AI performance (HGSS/HCVM):
1. Ensure `LLM_API_KEY` is in `.env`.
2. Run `make demo`.
3. Inspect `reports/ab_report.json` and forensic logs in `artifacts/runs/`.

## 3. Data Integrity
Before any modification to root data:
1. Consult `docs/DATA_GOVERNANCE.md`.
2. Verify hashes against the latest release locking script.
