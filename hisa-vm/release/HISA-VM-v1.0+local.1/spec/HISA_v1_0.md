# HISA-VM v1.0 (Release-Grade) — HISA-VM-v1.0+local.1

Status: NORMATIVE  
Release ID: `HISA-VM-v1.0+local.1`  
Tag: `hisa-vm-v1.0-local.1`  
Dimension: 18 (v18 lanes, u32)  
Encoding: IW32 MSB-first fields, little-endian word stream

## 0) Objective
HISA-VM adalah Virtual Machine deterministik (audit-grade, fail-closed) untuk menjalankan audit pipeline Codex v18:
- load v18 master (28 huruf) dari MH-28 CSV
- enforce CORE-1 conformance (SETFLAG adjacency sebelum AUDIT)
- validate formulas derived (AN/AK/AQ + U/rho + eps range + mod4 gate)

## 1) Normative Inputs
- Master CSV: `data/MH-28-v1.0-18D.csv` (CSV dengan kolom `letter` dan fitur)
- Normative order: `data/HIJAIYYAH_28.txt` (28 huruf dalam urutan index)

## 2) Determinism Contract
Given identical:
- bytecode bytes
- master CSV bytes
- HIJAIYYAH_28 bytes
the VM MUST produce identical:
- HALT/TRAP outcome
- trap code (ERR) and steps count

No randomness is permitted in core execution.

## 3) Fail-Closed Policy
Any violation of:
- instruction encoding (must-be-zero fields),
- CORE-1 adjacency,
- v18 audit gates
MUST immediately TRAP/HALT with an ERR code.

## 4) Verification (Auditor runnable)
```powershell
$env:PYTHONPATH="src;tests"
python -m pytest -q
python tools/build-hisa-release.py
python tools/verify-hisa-release.py --spec specs/HISA_release_integrity_local.yaml --check-manifest
python tools/hisa-run.py --program release/HISA-VM-v1.0+local.1/bytecode/audit_jim.bin
```
Expected:
- pytest PASS
- verify PASS (hash lock + semantic checks)
- demo HALT (err=0)
