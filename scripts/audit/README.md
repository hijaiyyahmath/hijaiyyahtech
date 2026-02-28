# Audit & Integrity Scripts
Location: `scripts/audit/`

This folder contains the core logic for verifying the integrity and audit trails of the Hijaiyah Codex release.

## Key Scripts
- `audit_script.py`: Main forensic audit execution logic.
- `check_integrity.py`: Hash-based file system integrity validator.
- `get_hashes.py` / `hash_verification.py`: Utilities for calculating and comparing SHA-256 fingerprints.
- `verify_release_integrity.py`: Release-level consistency checks.
- `create_manifest.py` / `update_manifest.py`: Tools for generating and sealing release manifests.
