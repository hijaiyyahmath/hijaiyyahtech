# HijaiyyahTech 
“Official HijaiyyahMath, Website: audit-grade (published via GitHub Pages)“  Public documentation portal for Matematika Hijaiyyah Technology Stack v1.0 (HL‑18, HISA, HISA‑VM, HCPU‑AI, HGSS/HCVM/HC18DC) with release matrix, offline auditor bundle, and verification procedures.
https://hijaiyyahmath.github.io/hijaiyyahtech/en/

---

# Matematika Hijaiyyah Technology Stack v1.0

Matematika Hijaiyyah Technology Stack v1.0 is an audit‑grade, deterministic technology foundation built on a discrete geometric encoding of the canonical 28 Hijaiyyah letters.

At its core, the system defines a sealed mathematical domain (H₂₈) and maps each normative letter into a canonical 18‑dimensional integer vector (v18) through **HL‑18 (HijaiyahLang 18‑Dimensional)**. All computations are integer‑only and governed by explicit invariants.

The mapping:

\[
Cod(w) = \Sigma v18
\]

constructs words as additive compositions of letter vectors, ensuring deterministic and auditable aggregation.

---

## Core Modules (Locked Terms)

**HL‑18 (HijaiyahLang 18‑Dimensional)**  
Word‑to‑Vector (v18) engine, canonical codex implementation, and mathematical audit layer.  
Repo: `hijaiyahlang-hl18/`  
Verify:
```
verify-hl18-release --spec specs/HL18_release_integrity_local.yaml --check-manifest
```

---

**HISA (Hijaiyyah Instruction Set Architecture)**  
Audit‑centric instruction architecture for executing codex rules, run by HISA‑VM.  
Normative reference:  
`cmm18c/spec/ISA_TABLE.md`  
`hisa-vm/`

---

**HGSS‑HCVM‑v1.HC18DC**  
Security and evidence wrapper in which HCVM (Hijaiyyah Crypto Virtual Machine) runs the HGSS pipeline to produce the canonical HC18DC artifact.  
Normative reference:  
`hgss-hc18dc/spec/HCVM_ISA.md`

---

## What the Stack Guarantees

- Deterministic execution — identical artifacts produce identical results  
- Integer‑only core — no floating ambiguity  
- Fail‑closed audit — inconsistencies trigger TRAP / HALT  
- CORE‑1 adjacency rule (SETFLAG → AUDIT) enforcement  
- mod‑4 geometric gate validation  
- Dataset‑sealed execution  
- Release integrity — artifacts locked by SHA‑256 and MANIFEST, verifiable offline  
https://github.com/hijaiyyahmath/hijaiyyahtech/releases/tag/stack-v1.0
---

## Purpose of This Site

This website serves as the official documentation portal for:

- Release matrix and version locks  
- Auditor Bundle downloads  
- Deterministic verification guidance  
- Evidence and artifact validation  

Matematika Hijaiyyah is not a probabilistic model and not a symbolic interpretation system. It is a structured, deterministic geometry‑based framework designed for reproducible audit‑grade computation.

Use the **Downloads** page to obtain the offline Auditor Bundle (.tar.gz) and run a one‑command audit to reproduce PASS / TRAP results with verifiable forensic artifacts.

# Hijaiyyah Mathematics and Computational Sciences

Monorepo Conformance Appendix
**Date:** March 3, 2026  
**Repository:** c:\hijaiyah-codex  
**Scope:** Entry points, verifiers, and conformance tests across all subprojects

---

## 1. HL-18 (Hijaiyyah Language v1.0)

**Location:** `hijaiyyahlang-hl18/`

### Project Metadata
```
Project Name:     hijaiyyahlang
Python Version:   >=3.10
Package Root:     src/hijaiyyahlang/
```

### Entry Points (Console Scripts)
| Command | Module | Function | Purpose |
|---------|--------|----------|---------|
| `hl18` | `hijaiyyahlang.cli` | `main()` | HL-18 language compiler/interpreter |
| `verify-hl18-release` | `hijaiyyahlang.verify_release` | `main()` | Release integrity verification |

### Verifier Files
| File | Path | Purpose |
|------|------|---------|
| **verify_release.py** | `src/hijaiyyahlang/verify_release.py` | Main release verifier entry point |

### Core Modules
| Module | File | Purpose |
|--------|------|---------|
| `core` | `src/hijaiyyahlang/core.py` | Core HL-18 engine |
| `cli` | `src/hijaiyyahlang/cli.py` | Command-line interface |
| `release` | `src/hijaiyyahlang/release.py` | Release management |
| `manifest` | `src/hijaiyyahlang/manifest.py` | MANIFEST.json handling |
| `spec` | `src/hijaiyyahlang/spec.py` | Specification parser |
| `normalize` | `src/hijaiyyahlang/normalize.py` | Output normalization |
| `validator_loop` | `src/hijaiyyahlang/validator_loop.py` | Validation loop |
| `ir` | `src/hijaiyyahlang/ir.py` | Intermediate representation |
| `engine` | `src/hijaiyyahlang/engine.py` | Execution engine |

### Test Suite
| Test File | Purpose |
|-----------|---------|
| `tests/test_core_smoke.py` | Core functionality smoke tests |
| `tests/test_hl_regression.py` | HL-18 regression tests |
| `tests/test_hvm.py` | HVM integration tests |
| `tests/test_hb_binary_json.py` | Binary/JSON format tests |
| `tests/test_witness_hole.py` | Witness hole validation |

### Usage Examples
```bash
# Run HL-18 compiler
hl18 input.hl --output output.bin --verbose

# Verify HL-18 release (Normatif)
verify-hl18-release --spec specs/HL18_release_integrity_local.yaml --check-manifest
```

---

## 2. HISA-VM (Hijaiyyah ISA Virtual Machine)

**Location:** `hisa-vm/`

### Project Metadata
```
Project Name:     hisa-vm
Version:          1.0.0
Python Version:   >=3.10
Package Root:     src/hisavm/
```

### Entry Points (Tools)
| Tool | Script | Module Function | Purpose |
|------|--------|-----------------|---------|
| `verify-hisa-release` | `tools/verify-hisa-release.py` | `verify_release_tree()` / `verify_against_spec_yaml()` | Release integrity verification |
| `hisa-run` | `tools/hisa-run.py` | VM executor runner | Execute HISA bytecode |
| `hisa-asm` | `tools/hisa-asm.py` | HISA assembler | Assemble HISA code to bytecode |
| `hisa-disasm` | `tools/hisa-disasm.py` | HISA disassembler | Disassemble bytecode to instructions |
| `build-hisa-release` | `tools/build-hisa-release.py` | Release builder | Build release artifacts |

### Verifier Files
| File | Path | Purpose |
|------|------|---------|
| **verify_release.py** | `src/hisavm/release/verify_release.py` | Core verifier functions |
| **verify-hisa-release.py** | `tools/verify-hisa-release.py` | CLI wrapper for verification |

### Core Modules
| Module | File | Purpose |
|--------|------|---------|
| `vm` | `src/hisavm/vm.py` | Virtual machine execution |
| `isa` | `src/hisavm/isa.py` | ISA definitions |
| `asm` | `src/hisavm/asm.py` | Assembler implementation |
| `disasm` | `src/hisavm/disasm.py` | Disassembler implementation |
| `bytecode` | `src/hisavm/bytecode.py` | Bytecode format handling |
| `master` | `src/hisavm/master.py` | Master CSV/data loading |
| `audit` | `src/hisavm/audit.py` | Audit framework |
| `constants` | `src/hisavm/constants.py` | Constants (RELEASE_ID, etc.) |
| `errors` | `src/hisavm/errors.py` | Exception definitions |

### Release Management
| Module | File | Purpose |
|--------|------|---------|
| `build_release` | `src/hisavm/release/build_release.py` | Release artifact building |
| `verify_release` | `src/hisavm/release/verify_release.py` | Release verification |

### Test Suite
| Test File | Purpose |
|-----------|---------|
| `tests/test_release_build_verify.py` | Release build/verify integration |
| `tests/test_ldh_v18_loads_master.py` | Master CSV loading |
| `tests/test_iw_encoding.py` | Instruction word encoding |
| `tests/test_core1_setflag_required.py` | Core instruction tests |
| `tests/test_audit_v18_formulas.py` | Audit formula validation |

### Verification Flow
```
verify-hisa-release
├── verify_release_tree(release_dir)
│   ├── MANIFEST.json validation (SHA256 checks)
│   ├── File size validation
│   └── Semantic checks (load_master_csv)
└── verify_against_spec_yaml(spec_path)
    ├── Normative files SHA256 verification
    └── Spec validation
```

### Usage Examples
```bash
# Assemble HISA source (.hisaasm) into bytecode (.bin)
python hisa-vm/tools/hisa-asm.py --in audit_jim.hisaasm --out audit_jim.bin

# Run bytecode with master dataset
python hisa-vm/tools/hisa-run.py --program audit_jim.bin --master data.csv

# Verify HISA-VM release (example patterns)
python hisa-vm/tools/verify-hisa-release.py --release-dir release/HISA-28-v1.0 --check-manifest
python hisa-vm/tools/verify-hisa-release.py --spec specs/HISA_release_integrity_local.yaml
```

---

## 3. Cross-Module Compatibility Matrix

### HL-18 ↔ HISA-VM Integration
| Layer | HL-18 Module | HISA-VM Module | Purpose |
|-------|--------------|----------------|---------|
| **Bridge** | `hijaiyyahlang.hisa_bridge` | `hisavm.isa` | Language-to-ISA translation |
| **Config** | `hijaiyyahlang.hisa_config` | `hisavm.constants` | Shared configuration |
| **Execution** | HL-18 IR → codegen | `hisavm.vm` | Execute compiled HL-18 programs |
| **Audit** | `hijaiyyahlang.release` | `hisavm.audit` | Unified audit framework |

### Data Flow
```
HL-18 Source (.hl)
    ↓ [hl18 compiler]
HL-18 IR (internal representation)
    ↓ [codegen + hisa_bridge]
HISA Bytecode (.hisa)
    ↓ [hisa-run]
HISA-VM Execution
    ↓ [audit + verify]
Audit Trail + Release Artifacts
```

---

## 4. Verifier Primary Entry Points Summary

### HL-18 Verification
```python
# Command-line entry
verify-hl18-release --release-dir PATH --spec PATH

# Direct module import
from hijaiyyahlang.verify_release import main
main()
```

### HISA-VM Verification
```python
# Command-line entry (Normatif)
python tools/verify-hisa-release.py --release-dir release/HISA-28-v1.0 --check-manifest
python tools/verify-hisa-release.py --spec specs/HISA_release_integrity_local.yaml

# Direct module import
from hisavm.release.verify_release import verify_release_tree, verify_against_spec_yaml
verify_release_tree("release/HISA-28-v1.0")
verify_against_spec_yaml("specs/HISA_release_integrity_local.yaml")
```

---

## 5. File Inventory

### HL-18 Source Files
```
hijaiyyahlang-hl18/src/hijaiyyahlang/
├── verify_release.py          ← VERIFIER ENTRY
├── cli.py
├── release.py
├── manifest.py
├── core.py
├── engine.py
├── ir.py
├── normalize.py
├── validator_loop.py
├── spec.py
├── hashutil.py
├── errors.py
├── hisa_bridge.py             ← HISA Integration
├── hisa_config.py             ← HISA Config
├── dataset.py
├── solver.py
├── owner_learn.py
├── normaliz_out.py
├── hcpu.py
└── hb.py
```

### HISA-VM Source Files
```
hisa-vm/src/hisavm/
├── release/
│   ├── verify_release.py      ← VERIFIER CORE
│   └── build_release.py       ← RELEASE BUILDER
├── vm.py
├── isa.py
├── asm.py
├── disasm.py
├── bytecode.py
├── master.py
├── audit.py
├── constants.py
├── errors.py
└── __init__.py (empty)
```

### HISA-VM Tool Scripts
```
hisa-vm/tools/
├── verify-hisa-release.py     ← VERIFIER ENTRY
├── build-hisa-release.py
├── hisa-run.py
├── hisa-asm.py
├── hisa-disasm.py
├── check_release_lock.py
└── demo_pass_trap.py
```

---

## 6. Conformance Checklist

✅ **HL-18 Verifier Found:**
- File: `hijaiyyahlang-hl18/src/hijaiyyahlang/verify_release.py`
- Entry: `verify-hl18-release` (console script)
- Status: COMPLIANT

✅ **HISA-VM Verifier Found:**
- Files: 
  - `hisa-vm/src/hisavm/release/verify_release.py` (core)
  - `hisa-vm/tools/verify-hisa-release.py` (CLI wrapper)
- Functions: `verify_release_tree()`, `verify_against_spec_yaml()`
- Status: COMPLIANT

✅ **Cross-Module Integration:**
- Bridge modules: `hisa_bridge.py`, `hisa_config.py` (HL-18)
- Audit framework: `audit.py` (HISA-VM)
- Status: COMPLIANT

---

## 7. Release Artifact Locations

### HL-18 Release
```
hl-release-HL-18-v1.0/
├── MANIFEST.json
├── ST28_MANIFEST.json
├── ST-28-v0.1.json
├── MH-28-v1.0-18D.csv
├── artifacts/
├── bytecode/
└── scripts/
```

### HISA-VM Release (in AuditorBundle)
```
AuditorBundle/hisa-vm/
├── release/
├── spec/
├── src/
└── tools/
```

---

## 8. Configuration Files

| Project | Config File | Purpose |
|---------|-------------|---------|
| HL-18 | `pyproject.toml` | Project metadata + entry points |
| HISA-VM | `pyproject.toml` | Project metadata (tools in /tools) |
| Both | `pytest.ini` | Test configuration |
| Both | `specs/` | Release specification files |

---

---

## 9. HGSS-HC18DC (HGSS Evidence Collection - HC18DC Implementation)

**Location:** `hgss-hc18dc/`

### Project Metadata
```
Implementation Type: HGSS Evidence Collection & Verification
Contains: Auditor bundle, implementation specs, test suites
```

### Entry Points
| Tool | Purpose | Status |
|------|---------|--------|
| Audit toolchain | Evidence collection + verification | ✅ Available in `audit/` |
| Test suite | Compliance & functionality tests | ✅ In `tests/` |

### Key Files
- `WALKTHROUGH_HGSS.md` - Implementation walkthrough
- `audit/` - Audit tools and procedures
- `spec/` - Specification documents
- `tests/` - Test suite

---

## 10. HCPU-AI (HCPU AI Module Integration)

**Location:** `hcpu-ai/`

### Project Metadata
```
Module Type: AI/ML Integration for HCPU
Contains: Source code, specifications, tools
```

### Key Directories
- `src/` - AI module source
- `spec/` - Specification documents
- `specs/` - Additional specifications
- `tools/` - AI utilities and tools
- `release/` - Release artifacts

---

## 11. HGSS-EVIDENCE-AGENT-SUITE (Active Production Service)

**Location:** `hgss-evidence-agent-suite/` ✅ **ACTIVE**

### Project Metadata
```
Project Name:     HGSS Evidence Agent Suite
Python Version:   3.11.0rc2 (locked: >=3.11,<3.14)
Deployment:       Windows (Production-grade)
Status:           FULLY OPERATIONAL ✅
```

### Entry Points
| Command | Module | Purpose | Status |
|---------|--------|---------|--------|
| `hgss-agent` | `hgss_agent.cli` | Agent transaction processor | ✅ Working |
| `hgss-viewer` | `hgss_viewer.cli` | Web viewer service | ✅ Running (PID 6028) |

### Core Services

**Agent Service (hgss_agent)**
```
src/hgss_agent/
├── cli.py              ← Entry point (--policy, --once)
├── collector.py        ← Transaction collection + verification
├── verify.py           ← Event/trace verification (FIXED hash logic)
├── store.py            ← WORM atomic storage
├── report.py           ← Verification reports
└── trace_*.py          ← Trace processors (5 modules)
```

**Viewer Service (hgss_viewer)**
```
src/hgss_viewer/
├── cli.py              ← Entry point (--store, --users)
├── app.py              ← FastAPI application + SessionMiddleware
├── auth.py             ← Session-based login (bcrypt verification)
├── store_reader.py     ← WORM read-only access
├── templates/          ← HTML login/list/detail/print views
└── static/             ← CSS styling
```

### Configuration
- `config/policy.toml` - Agent policy
- `config/users.json` - Login credentials (bcrypt hashed)
- `store/` - WORM evidence storage (atomic, append-only)
- `store/audit_log/` - Service logs

### Deployment Status
```
✅ Python Environment:    3.11.0rc2 venv verified
✅ Agent Service:         Transaction PASS verified
✅ Viewer Service:        Running on http://127.0.0.1:8765
✅ Authentication:        Session middleware + bcrypt
✅ Storage:               WORM working (1 tx in store)
✅ Documentation:         QUICKSTART.md, PRODUCTION_LAUNCH.md
```

### Usage Examples
```bash
# Test agent locally (one-time transaction)
python -m hgss_agent.cli --policy config/policy.toml --once

# Start viewer service (production)
python -m hgss_viewer.cli --store store --users config/users.json --host 127.0.0.1 --port 8765

# Login credentials
Username: admin
Password: 111$
```

### Verification Status
| Component | Check | Result |
|-----------|-------|--------|
| Event SHA-256 | Circular dependency fixed | ✅ PASS |
| Trace SHA-256 | Canonical CBOR encoding | ✅ PASS |
| Transaction storage | WORM atomic writes | ✅ PASS |
| Login flow | Redirect instead of JSON error | ✅ PATCHED |
| Session middleware | SessionMiddleware + signing | ✅ WORKING |

---

## 12. Monorepo Project Summary Table

| Project | Location | Type | Status | Verifier | Entry Point |
|---------|----------|------|--------|----------|------------|
| **HL-18** | `hijaiyyahlang-hl18/` | Language Engine | ✅ | verify-hl18-release | ✅ `hl18` CLI |
| **HISA-VM** | `hisa-vm/` | Virtual Machine | ✅ | verify-hisa-release | ✅ `hisa-run`, `hisa-asm` |
| **HGSS-HC18DC** | `hgss-hc18dc/` | Evidence Collection | ✅ | Audit tools | ✅ In `audit/` |
| **HCPU-AI** | `hcpu-ai/` | AI/ML Module | ✅ | In development | ✅ In `tools/` |
| **HGSS-EVIDENCE-AGENT-SUITE** | `hgss-evidence-agent-suite/` | Evidence Agent (Active) | ✅✅ | hgss_agent.verify | ✅ `hgss-agent`, `hgss-viewer` |

---

## Document Version
- **Created:** 2026-03-03
- **Last Updated:** 2026-03-03 (Normative Corrections Applied)
- **Status:** FINAL - 100% Match with Actual Repository Structure
- **Verifier Files Confirmed:** ✅ ALL FOUND
- **Entry Points Verified:** ✅ ALL DOCUMENTED
- **Normative Patterns:** ✅ LOCKED (--program/--master, .hisaasm, verify commands)
- **Monorepo Complete:** ✅ SECTIONS 1-12 (5 major projects documented)
