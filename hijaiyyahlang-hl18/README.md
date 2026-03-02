# HijaiyyahLang (HL-18)

Virtual engine and release verifier for HijaiyyahLang HL-18-v1.0.

## Release Identity (Local Build)
This repository is a local build of HL-18, release ID: **HL-18-v1.0+local.1**.

> [!IMPORTANT]
> This release is forensically consistent against `specs/HL18_release_integrity_local.yaml`. 
> It is **not** byte-identical to the canonical HL-18-v1.0 artifact pack (which prioritizes different metadata/formatting).

## Installation
```bash
python -m pip install -e .
```

## Verification
To verify the integrity of this local release:
```bash
python scripts/verify_hl18_release.py --spec specs/HL18_release_integrity_local.yaml --check-manifest
```

## Structure
- `release/HL-18-v1.0+local.1/`: Vendored release artifacts (Locked).
- `specs/HL18_release_integrity_local.yaml`: Local integrity specification.
- `src/hijaiyyahlang/`: Core library and CLI.
- `scripts/verify_hl18_release.py`: Forensic verifier.

## Usage
### CLI
```bash
# Word to Vector (v18)
hl18 --csv release/HL-18-v1.0+local.1/MH-28-v1.0-18D.csv cod "بت"

# Audit word
hl18 --csv release/HL-18-v1.0+local.1/MH-28-v1.0-18D.csv audit "بت"
```

### Library
```python
from hijaiyyahlang.dataset import load_mh28_csv, cod_word
from hijaiyyahlang.core import audit_v18

ds = load_mh28_csv("release/HL-18-v1.0+local.1/MH-28-v1.0-18D.csv")
v = cod_word("بت", ds)
ar = audit_v18(v)
print(ar.ok)
```
