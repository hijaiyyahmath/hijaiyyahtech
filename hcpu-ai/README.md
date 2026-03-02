# HCPU-AI (Hijaiyyah Central Processing Unit for AI)

HCPU-AI is a deterministic, stack-based reference execution engine for the Hijaiyyah stack.

## Overview
- **ISA**: HISA v1.0
- **Release ID**: `HCPU-AI-v1.0+local.1`
- **Execution**: Delegates to `hisa-vm` for bit-exact HISA conformance.
- **AI Loops**: Integrated CORE, FEEDBACK, and OWNER modes for compliance.

## Quick Start
```powershell
$env:PYTHONPATH="src;../hisa-vm/src"
python tools/hcpu_ai_demo.py --mode OWNER
```

## Integrity Verification
```powershell
python release/verify_hcpu_ai_release.py --spec specs/HCPU_AI_release_integrity_local.yaml --check-manifest
```
