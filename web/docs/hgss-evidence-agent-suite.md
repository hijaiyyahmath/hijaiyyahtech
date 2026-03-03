---
title: HGSS Evidence Agent Suite (Production)
description: Audit-grade evidence generation, verification, and storage system. Fail-closed, append-only, canonical CBOR format.
keywords: HGSS, evidence, audit, trace, verification, blockchain-alternative, banking
layout: default
lang: en
---

# HGSS Evidence Agent Suite (Production) — v1.0

**Status**: Production / Frozen Release | **Platform**: Windows + Linux (x86_64) | **Last Updated**: March 2026

---

## 🎯 Executive Summary

**HGSS Evidence Agent Suite** adalah sistem blockchain-alternative untuk audit-grade evidence per transaksi. Dirancang untuk sistem yang membutuhkan:

- ✅ **Bukti kanonik** yang byte-stable (Canonical CBOR, RFC 8949)
- ✅ **Verifikasi ketat** menolak evidence yang tidak memenuhi schema frozen
- ✅ **Penyimpanan append-only/WORM** — tidak boleh ubah/hapus
- ✅ **Trace playback deterministik** — step-by-step + 28-lane timeline per huruf Hijaiyyah
- ✅ **Fail-closed architecture** — jika gagal tetap simpan untuk forensik

**Primary Domain**: Banking, Compliance, Supply Chain, Justice Systems

---

## 🚀 Quick Start

### Download & Install

| Platform | Installer | Installation |
|----------|-----------|--------------|
| **Windows** | [HGSS-Evidence-Agent-Suite-1.0.exe](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/HGSS-Evidence-Agent-Suite-1.0.exe) | Double-click → Next → Finish |
| **Linux (Debian/Ubuntu)** | [hgss-agent-suite_1.0_amd64.deb](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/hgss-agent-suite_1.0_amd64.deb) | `sudo dpkg -i ...` + `systemctl enable --now ...` |
| **Linux (RHEL/Fedora)** | [hgss-agent-suite-1.0-1.el8.x86_64.rpm](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/hgss-agent-suite-1.0-1.el8.x86_64.rpm) | `sudo dnf install ...` + `systemctl enable --now ...` |

### Launch & Login

```bash
# Windows: Start Menu → "HGSS Viewer"
# Linux: $ hgss-viewer

# Login Credentials (change on first run):
#   Username: admin
#   Password: admin
```

---

## 📊 Core Features

### 1. Evidence Collection & Strict Verification

```
Input: event.cbor + trace.jsonl
   ↓
Collect (read Canonical CBOR)
   ↓
Recompute trace_sha256 from trace.jsonl (31 events)
   ↓
Compare: computed vs locked value
   ↓
Strict Verify: schema frozen (AUDIT_EVIDENCE_SCHEMA.md)
   ↓
Output: verify_report.json (PASS / FAIL / TRAP)
   ↓
Store: append-only WORM (even if FAIL/TRAP)
```

### 2. Transaction List & Detail View

**List**:
- 20 transaksi per halaman
- Kolom: timestamp, policy ID, nonce, digests, status
- Sort + filter by date range, status, policy

**Detail**:
- Evidence node digests (lease, nonce, commitment, MAC, AAD, ciphertext, trace, event)
- File downloads (event.cbor, trace.jsonl, hc18dc.cbor, verify_report.json)
- Status indicator (🟢 PASS | 🔴 FAIL/TRAP)

### 3. Global Trace Playback

Step-by-step instruksi navigator:
- Step counter: 0/30
- Instruction decoder: PC, opcode, operands (rd, ra, rb, etc)
- Play/Pause/Next/Previous buttons
- Goto specific step

### 4. 28-Lane Timeline (Hijaiyyah Alphabet)

Visual timeline menampilkan lane aktif per huruf (ا..ي):

```
Lane 0  (ا): [====●========]
Lane 1  (ب): [          ]  (inactive)
Lane 2  (ت): [    ===●====   ]
...
Lane 27 (ي): [              ●==]

Legend: ● = current step, === = active range
```

**Derivation**: Deterministik dari ISA semantics (LDH_V18 instruction detection), tanpa menciptakan data fiktif.

### 5. Print HGSS (Export Summary)

Tombol **"Print HGSS"** menghasilkan ringkasan comprehensive:

- **Format**: PDF (default) | HTML | JSON
- **Content**:
  - Event ID + Timestamp
  - Evidence digests (trace_sha256, event_sha256, etc)
  - Verification status + all checks
  - Storage path + retention policy reference

---

## 🔒 Technical Architecture

### Component Stack

```
┌──────────────────────────────────────────────┐
│ Agent Service (Rust/Go)                      │
│ - Collector                                  │
│ - Recompute & Compare (trace_sha256)         │
│ - Strict Verifier Wrapper                    │
│ - Lane Deriver (deterministic)               │
│ - Append-Only Store Writer                   │
└──────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────┐
│ Storage (WORM / Append-Only)                 │
│ store/tx/<event_sha256>/                     │
│   ├── event.cbor [N]                         │
│   ├── trace.jsonl [N]                        │
│   ├── trace_lanes.jsonl [N]                  │
│   ├── verify_report.json [N]                 │
│   ├── hc18dc.cbor [N]                        │
│   └── index.json [N]                         │
└──────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────────────┐
│ Viewer UI (Tauri/Electron)                   │
│ - Login                                      │
│ - List & Detail                              │
│ - Playback                                   │
│ - Lane Timeline                              │
│ - Print/Export                               │
└──────────────────────────────────────────────┘
```

### Data Formats

| File | Format | Purpose | Status |
|------|--------|---------|--------|
| `event.cbor` | RFC 8949 Canonical CBOR | Evidence event (locked) | [N] Normative |
| `trace.jsonl` | JSON Lines (31 events) | Execution trace bytes | [N] Normative |
| `trace_lanes.jsonl` | JSON Lines + lane fields | 28-lane timeline (derived) | [N] Normative |
| `verify_report.json` | JSON object | Verification results | [N] Normative |
| `hc18dc.cbor` | Canonical CBOR | Final artifact (HC18DC) | [N] Normative |
| `index.json` | JSON object | Fast lookup metadata | [N] Informative |
| `auditlog.jsonl` | Single-line JSON | Human-readable log | [I] Informative |

### Locked Values (v1.0)

```
trace_sha256 = "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363"
trace_event_count = 31
event_sha256 = <computed from canonical CBOR>
```

All digests computed with:
- **Canonical encoding**: RFC 8949 deterministic CBOR
- **Hash function**: SHA-256 (lowercase hex, 64 chars)
- **Immutable**: No override allowed

---

## 🔐 Security & Compliance

### Design Principles

1. **Fail-Closed**: Default deny; jika gagal → status FAIL/TRAP + forensic store
2. **Append-Only**: No delete/modify after write
3. **Canonical**: RFC 8949 for byte-stable, reproducible hashing
4. **Locked Digests**: trace_sha256, trace_event_count, event_sha256 tidak bisa diubah
5. **Deterministic**: Lane timeline dari ISA semantics, bukan tebakan

### Authentication & Authorization

- **Default Credential**: admin/admin (force change on first login)
- **Storage**: Hashed passwords (bcrypt cost=12 minimum)
- **Access**:
  - **Agent**: Minimal privilege (read input, write to store)
  - **Viewer**: Read-only access (no modification)
- **Audit Logging**: Semua akses dicatat (append-only)

### Cryptography

- ✅ **SHA-256**: Standard digests
- ✅ **HMAC-SHA256**: Message authentication
- ✅ **RFC 8949**: Canonical CBOR (deterministic)
- ❌ **No MD5/SHA1**: Deprecated, disabled

### Compliance

- 🏦 **Banking**: PCI-DSS v4.0 compatible
- 📋 **Records**: NIST SP 800-161 supply chain security
- ⚖️ **Justice**: 30+ tahun evidence retention offline-readable

---

## 📚 Documentation

### Full Specifications

1. **[HGSS Evidence Agent Suite Spec (Normatif)](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/blob/main/spec/HGSS_EVIDENCE_AGENT_SUITE_SPEC.md)**
   - Scope (IN/OUT)
   - Deliverable (Windows MSI, Linux deb/rpm)
   - Repository structure (file-level)
   - Storage layout (normatif)
   - Artifact formats (CBOR, JSONL, JSON)
   - Lane derivation algorithm
   - End-to-end workflow
   - UI pages (login, list, detail, playback, print)
   - Installation (Windows, Linux)
   - Domain aplikasi (banking, compliance, supply chain, justice)
   - Tech stack
   - Security & compliance
   - Testing & release checklist
   - **Appendix A**: Template index.json, verify_report.json, trace_lanes.jsonl examples
   - **Appendix B**: End-to-end flow illustration
   - **Appendix C**: Implementation checklist

2. **[AUDIT_EVIDENCE_SCHEMA.md (Frozen)](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/blob/main/spec/AUDIT_EVIDENCE_SCHEMA.md)**
   - Evidence event schema (§1-12)
   - Trace structure definition
   - Canonicalization rules (RFC 8949)
   - Lock rules & constraints

3. **[README.md (Quick Start)](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/blob/main/README.md)**
   - Overview
   - Installation (Windows, Linux)
   - Features & architecture
   - Testing

### Example Artifacts

```
spec/
  HGSS_EVIDENCE_AGENT_SUITE_SPEC.md
  AUDIT_EVIDENCE_SCHEMA.md

agent/tests/fixtures/
  trace.jsonl                   # 31 test events
  event.cbor                    # example evidence
  policy.toml                   # example policy

tools/
  hgss_verify_evidence.py       # strict verifier (Python)
  hgss_make_example_event.py    # demo generator
```

---

## 🧪 Testing & Validation

### Unit Tests

```bash
cd agent
cargo test
# ✅ trace_sha256_recompute()
# ✅ cbor_canonical_encode()
# ✅ lanes_derive_deterministic()
# ✅ verify_report_generation()
```

### Integration Tests

```bash
cargo test --test integration_test
# Full pipeline: collect → verify → store → UI read
```

### Fixtures & Test Vectors

```
agent/tests/fixtures/
  trace.jsonl          # 31 events (locked)
  event.cbor           # canonical event
  policy.toml          # example policy
  expected_digests     # locked values for verification
```

---

## 🔄 Workflow: Transaksi End-to-End

```
1) Upstream System
   ├─ Hasilkan event.cbor (Canonical CBOR)
   └─ Hasilkan trace.jsonl (31 events)

2) Agent Service
   ├─ Collect: Parse event.cbor + trace.jsonl
   ├─ Recompute: trace_sha256 dari trace_events
   ├─ Compare: computed vs locked
   ├─ Strict Verify: Run hgss_verify_evidence.py
   ├─ Derive: trace_lanes.jsonl (28-lane)
   └─ Store: Folder append-only

3) Storage
   └─ store/tx/<event_sha256>/
      ├─ event.cbor
      ├─ trace.jsonl
      ├─ trace_lanes.jsonl
      ├─ verify_report.json (PASS/FAIL/TRAP)
      ├─ hc18dc.cbor
      └─ index.json

4) UI Access
   ├─ Login → Transaction List
   ├─ Click detail → Node digests + verification
   ├─ Trace Playback (step-by-step)
   ├─ Lane Timeline (28-lane visualization)
   └─ Print HGSS (PDF/HTML/JSON export)
```

---

## 💀 Use Cases

### Banking (Primary)

- Setiap transaksi → evidence kanonik
- Auditor buka bundle tahunan, verifikasi ulang
- 7+ tahun retention offline-readable
- PCI-DSS compliance

### Compliance & Risk

- Keputusan AI/ML → evidence trail
- Explainability via trace lanes
- Regulatory audit-ready

### Supply Chain & Logistics

- Event per kargo shipment
- Evidence chain deterministic offline-verifiable
- Blockchain alternative (no smart contracts)

### Government / Justice

- Dokumen hashing/signing dengan audit trail
- 30+ tahun archival
- Forensic analysis support

---

## 🎓 Scientific Foundation

Suite ini dibangun di atas:

- **Matematika Hijaiyyah** (18-dimensional word space, CSGi codex)
- **HL-18** (HijaiyyahLang deterministic word-to-vector)
- **HISA** (Hijaiyyah ISA v1.0, fail-closed instruction set, 16 trap types)
- **HISA-VM** (4-stage pipeline, full auditability)
- **HCPU** (Hardware reference implementations: Silicon, Photonic, Quantum)
- **HCVM** (Cryptographic VM extended with CBOR, SHA-256, HMAC, signatures)
- **HC18DC** (Canonical output format, frozen schema)

---

## 📦 Download & Install

### Installers

**Latest Release: v1.0**

| Platform | Package | SHA256 |
|----------|---------|--------|
| Windows (MSI) | [HGSS-Evidence-Agent-Suite-1.0.exe](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/HGSS-Evidence-Agent-Suite-1.0.exe) | [checksums.txt](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/SHA256SUMS.txt) |
| Linux (Debian) | [hgss-agent-suite_1.0_amd64.deb](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/hgss-agent-suite_1.0_amd64.deb) | [checksums.txt](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/SHA256SUMS.txt) |
| Linux (RPM) | [hgss-agent-suite-1.0-1.el8.x86_64.rpm](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/hgss-agent-suite-1.0-1.el8.x86_64.rpm) | [checksums.txt](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/SHA256SUMS.txt) |

### Offline Auditor Bundle

📦 **[Complete Offline Bundle](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/HGSS-Auditor-Bundle-v1.0.tar.gz)** (schema + tools + test vectors)

- spec/AUDIT_EVIDENCE_SCHEMA.md (frozen)
- tools/hgss_verify_evidence.py (strict verifier)
- Test fixtures (31-event example)
- Offline verification guide

---

## 🤝 Contributing & Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/issues)
- 📧 **Email**: support@hijaiyyahmath.org
- 📚 **Docs**: [Full Documentation](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/blob/main/spec/HGSS_EVIDENCE_AGENT_SUITE_SPEC.md)
- 🔗 **Website**: [hijaiyyahmath.org](https://hijaiyyahmath.org)

---

## 📄 License

**MIT License** — See [LICENSE](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/blob/main/LICENSE)

---

## Citation

```bibtex
@software{hgss_evidence_agent_suite_2026,
  title = {HGSS Evidence Agent Suite},
  subtitle = {Production-Grade Audit Evidence System},
  author = {Hijaiyyah Math Team},
  year = {2026},
  url = {https://github.com/hijaiyyahmath/hgss-evidence-agent-suite},
  version = {1.0},
  note = {Frozen specification, blockchain-alternative evidence architecture}
}
```

---

**Version**: 1.0 (Frozen) | **Last Updated**: March 2026 | **Status**: Production Ready
