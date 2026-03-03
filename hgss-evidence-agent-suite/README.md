# HGSS Evidence Agent Suite — Production Release v1.0

**Status**: Frozen / Production | **Platform**: Windows + Linux (x86_64)

---

## Overview

**HGSS Evidence Agent Suite** adalah sistem audit-grade untuk menangkap, memverifikasi, dan menyimpan evidence transaksi dengan karakteristik:

- ✅ **Fail-Closed**: Verifikasi ketat (strict); jika gagal tetap disimpan untuk forensik
- ✅ **Append-Only Storage**: WORM policy, tidak boleh modifikasi/hapus
- ✅ **Canonical Archives**: Semua evidence dalam Canonical CBOR (RFC 8949)
- ✅ **Deterministic Playback**: Trace dapat diulang step-by-step + 28-lane timeline
- ✅ **Banking-Grade**: PCI-DSS compatible, schema frozen, locked digests

**Locked Values (v1.0)**:
- `trace_sha256`: `63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363`
- `trace_event_count`: `31`
- All per-event verification checkpoints per `AUDIT_EVIDENCE_SCHEMA.md` (frozen)

---

## Installation

### Windows (Download & Run)

1. **Download installer**: [HGSS-Evidence-Agent-Suite-1.0.exe](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/HGSS-Evidence-Agent-Suite-1.0.exe)

2. **Install**:
   ```
   Double-click installer → Follow wizard (License, Location, Components)
   → Finish
   ```

3. **Service verification** (optional):
   ```powershell
   # Open Services (services.msc)
   # or in PowerShell:
   Get-Service hgss-agent | Select-Object Status
   # Output: Status = Running
   ```

4. **Launch UI**:
   ```
   Start Menu → "HGSS Viewer"
   → Login (default: admin/admin, change on first run)
   → View transactions
   ```

### Linux (Debian/Ubuntu)

```bash
# Download
wget https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/hgss-agent-suite_1.0_amd64.deb

# Install
sudo dpkg -i hgss-agent-suite_1.0_amd64.deb

# Enable & start
sudo systemctl enable --now hgss-agentd

# Launch viewer
hgss-viewer
```

### Linux (RHEL/Fedora)

```bash
# Download
wget https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases/download/v1.0/hgss-agent-suite-1.0-1.el8.x86_64.rpm

# Install
sudo dnf install hgss-agent-suite-1.0-1.el8.x86_64.rpm

# Enable & start
sudo systemctl enable --now hgss-agentd
hgss-viewer
```

---

## Features

### 🔍 Audit Evidence Collection & Verification

- **Collect**: Tangkap `event.cbor` (Canonical CBOR) + `trace.jsonl` (31 events)
- **Recompute**: Hitung ulang `trace_sha256` dari `trace.jsonl`, bandingkan dengan locked value
- **Strict Verify**: Jalankan Python verifier terhadap schema frozen (`AUDIT_EVIDENCE_SCHEMA.md`)
- **Store**: Simpan dalam folder append-only (`store/tx/<event_sha256>/`)

### 📊 Transaction List & Detail

- **List View**: Kolom timestamp, policy ID, nonce, digests, status (PASS/FAIL/TRAP)
- **Detail View**: Node digests, verification report, file downloads
- **Status Indicators**: Green (PASS) | Red (FAIL/TRAP)

### ▶️ Trace Playback & 28-Lane Timeline

- **Global Playback**: Step-by-step instruksi (i=0..30)
- **Lane Timeline**: 28-lane per huruf Hijaiyyah (ا..ي), diturunkan deterministik dari `trace.jsonl`
- **Visualization**: Timeline stacked lanes dengan active/inactive indicators

### 🖨️ Print HGSS (Export Summary)

Tombol **"Print HGSS"** menghasilkan:
- **PDF/HTML**: Summary ringkas (event_sha256, trace_sha256, status, digests)
- **JSON**: Structured export untuk archival

---

## Documentation

| Dokumen | Deskripsi |
|---------|-----------|
| [HGSS_EVIDENCE_AGENT_SUITE_SPEC.md](hgss-hc18dc/spec/HGSS_EVIDENCE_AGENT_SUITE_SPEC.md) | Spesifikasi normatif lengkap (Scope, Deliverable, Data Format, Workflow, UI) |
| [AUDIT_EVIDENCE_SCHEMA.md](hgss-hc18dc/spec/AUDIT_EVIDENCE_SCHEMA.md) | Evidence schema frozen v1.HC18DC |
| [HCVM_ISA.md](hgss-hc18dc/spec/HCVM_ISA.md) (referenced) | Instruction set (untuk ISA decode, LDH_V18 opcode) |

---

## Quick Start

### Run Agent Service

**Windows (already running post-install)**:
```powershell
# Check status
sc query hgss-agent
```

**Linux**:
```bash
sudo systemctl status hgss-agentd
```

### Open Viewer

```
Windows: Start Menu → "HGSS Viewer"
Linux:   $ hgss-viewer
```

**Login**:
- Username: `admin`
- Password: `admin` (change on first run, enforced by policy)

### View Transaction Example

1. In "Transaction List", click any PASS entry
2. Inspect **Node Digests** panel (lease, nonce, commitment, MAC, ciphertext, trace, event)
3. Click **"Playback Global Trace"** → step through 31 events
4. Click **"28-Lane Timeline"** → see active lanes per huruf
5. Click **"Print HGSS"** → export summary PDF

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│ Upstream System (Perbankan / HCVM)                  │
│   ↓ event.cbor + trace.jsonl                        │
├─────────────────────────────────────────────────────┤
│ HGSS Agent Service (Rust/Go backend)                │
│   • Collector (read event + trace)                  │
│   • Recompute trace_sha256 (strict compare)         │
│   • Verifier wrapper (call Python strict verifier)  │
│   • Derive lanes (deterministik, no dummy)          │
│   • Store (append-only WORM)                        │
│   ↓                                                  │
├─────────────────────────────────────────────────────┤
│ Storage: /var/lib/hgss/store/                       │
│   tx/<event_sha256>/                                │
│   ├── event.cbor [N]                                │
│   ├── trace.jsonl [N]                               │
│   ├── trace_lanes.jsonl [N]  (derived)              │
│   ├── verify_report.json [N]                        │
│   ├── hc18dc.cbor [N]                               │
│   ├── index.json [N]                                │
│   └── audit_log/                                    │
│                                                     │
├─────────────────────────────────────────────────────┤
│ HGSS Viewer (Tauri/Electron UI)                     │
│   • Login screen                                    │
│   • Transaction list & detail                       │
│   • Global playback + 28-lane timeline              │
│   • Print HGSS export                               │
│   → Read-only access (no modify)                    │
└─────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Fail-Closed**: Jika verify gagal → status FAIL/TRAP, evidence tetap disimpan
2. **Append-Only**: Tidak boleh ubah/hapus file yang sudah disimpan
3. **Canonical**: Canonical CBOR (RFC 8949) untuk byte-stable, reproducible hashing
4. **Locked Values**: `trace_sha256`, `trace_event_count`, `event_sha256` tidak bisa diubah
5. **Deterministic**: Lane timeline diturunkan dari ISA semantics, bukan tebakan

---

## Security

- **Authentication**: Username+password (hash: bcrypt/PBKDF2)
- **Authorization**: Agent (minimal privilege), Viewer (read-only)
- **Audit Logging**: Semua akses logged (append-only)
- **Data Integrity**: WORM policy, SHA-256 digests, HMAC-SHA256 MACs
- **Cryptography**: RFC 8949 Canonical CBOR, no MD5/SHA1

---

## Testing

```bash
# Unit tests
cd agent && cargo test   # atau go test ./...

# Integration tests
cargo test --test integration_test

# Fixtures
ls agent/tests/fixtures/
# trace.jsonl (31 events), event.cbor, policy.toml

# Example verification
cd tools
python hgss_verify_evidence.py \
  --event ../agent/tests/fixtures/event.cbor \
  --trace ../agent/tests/fixtures/trace.jsonl \
  --schema ../spec/AUDIT_EVIDENCE_SCHEMA.md
```

---

## Releases

| Version | Release Date | Windows MSI | Linux deb | Linux RPM | Notes |
|---------|--------------|------------|-----------|-----------|-------|
| 1.0 | March 2026 | ✅ | ✅ | ✅ | Initial production release, schema frozen |

**Download**: [GitHub Releases](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/releases)

---

## Roadmap

- **v1.0** (Current): Evidence collection, strict verify, append-only store, UI playback
- **v1.1** (Future): MFA (TOTP), REST API mode (headless), batch export
- **v1.2** (Future): Multi-tenant, LDAP integration, extended trace formats

---

## Support & Compliance

- **Audit Bundle**: Download complete offline bundle (spec + tools + test vectors)
- **Compliance**: PCI-DSS v4.0, NIST SP 800-161
- **Issues**: [GitHub Issues](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/issues)
- **Documentation**: [Full Spec](hgss-hc18dc/spec/HGSS_EVIDENCE_AGENT_SUITE_SPEC.md)

---

## License

MIT License — See [LICENSE](LICENSE) file

---

## Citation

If using in research or production:

```bibtex
@software{hgss_evidence_agent_suite_2026,
  title = {HGSS Evidence Agent Suite},
  author = {Hijaiyyah Math},
  year = {2026},
  url = {https://github.com/hijaiyyahmath/hgss-evidence-agent-suite},
  version = {1.0}
}
```

---

**Maintained By**: HGSS Evidence Agent Suite Team  
**Last Updated**: March 2026  
**Specification Version**: 1.0 Normatif (Frozen)
