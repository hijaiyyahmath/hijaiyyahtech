# Hijaiyah-Codex Monorepo

Welcome to the **Hijaiyah-Codex** monorepo. This project is a consolidated environment for the research, development, and audit of Hijaiyah-based cryptographic and AI systems.

## 0. Project Modules
- [hijaiyahlang-hl18](./hijaiyahlang-hl18): Core language processing and glyph features.
- [hisa-vm](./hisa-vm): Normative Virtual Machine for audit trail execution.
- [hgss-hc18dc](./hgss-hc18dc): Normative Oracle and evidence verification suite.
- [hijaiyyah-ai-hgss](./hijaiyyah-ai-hgss): Industrial AI harness with guarded repair loops.
- [cmm18c](./cmm18c): Mathematical models and RTL specifications.
- [glyph/](./glyph): Normative SVG/PNG assets.

## 1. Programmable Runner (Makefile)
The monorepo provides a standardized interface for development and audit:

```bash
# Check environment and normative locks
make env

# Run unit tests in all modules
make test

# Run minimal core demos
make demo

# Execute the full pipeline (env + test + demo)
make all
```

*For Windows systems without `make`, use `python scripts/run_all.py`.*

## 2. Documentation
- [REPO_MAP.md](./REPO_MAP.md): Detailed module relationships and data flow.
- [RUNBOOK.md](./RUNBOOK.md): Operational commands for developers and auditors.
- [docs/DATA_GOVERNANCE.md](./docs/DATA_GOVERNANCE.md): Rules for normative data integrity.

## 3. Normative Locks
Locked Release: `HGSS-HCVM-v1.HC18DC` @ `e392c68`.
