# hijaiyyahtech 
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

---
