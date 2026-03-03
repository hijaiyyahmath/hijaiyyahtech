# HGSS Evidence Agent Suite (Production) — Spesifikasi Normatif

**Versi**: 1.0  
**Status**: Production / Frozen  
**Tanggal**: March 2026  
**Platform**: Windows + Linux (x86_64)  
**Tujuan**: Auditable, fail-closed evidence generation dan verification per transaksi

---

## 0. Scope (Normatif)

### IN SCOPE — Tujuan Aplikasi

1. **Menghasilkan dan/atau mengumpulkan HGSS evidence** per transaksi sesuai kontrak AUDIT_EVIDENCE_SCHEMA.md
2. **Memverifikasi ketat** menggunakan `hgss_verify_evidence.py` terhadap schema frozen
3. **Menyimpan dalam HC18DC** (Canonical CBOR per RFC 8949)
4. **Auditable playback trace**:
   - Trace global (step-by-step instruksi)
   - 28-lane timeline (per huruf/lane, deterministik dari trace.jsonl)
5. **Transparansi forensik** — fail-closed, append-only storage
6. **UI untuk membaca evidence** — login, list transaksi, detail, print summary

### OUT OF SCOPE — Tidak Dilakukan

1. **Plaintext transaksi perbankan** tidak ditampilkan di UI
2. **RAM dump bebas** — forensic RAM dibatasi buffer pipeline saja (trace/event/crypto staging), dikunci ke `trace_sha256` dan `event_sha256`
3. **Modifikasi evidence** — storage append-only, verifikasi fail-closed
4. **Interpretasi bisnis transaksi** — hanya bukti teknis, bukan approval/rejection

---

## 1. Deliverable Produk Terinstal

### 1.1 Windows

**Installer**: `HGSS-Evidence-Agent-Suite-<VERSION>.exe` (MSI-based)

**Komponen terinstal**:

| Komponen | Tipe | Deskripsi |
|----------|------|-----------|
| `hgss-agent` | Windows Service | Backend service, kolektor evidence, verifier |
| `hgss-viewer` | Desktop GUI | UI lokal (Qt/Electron/WPF), login + audit |
| `hgssctl` | CLI (opsional) | Command-line interface untuk admin |
| Systemd service config | Config | Auto-start pada boot |
| `C:\ProgramData\HGSS\` | Data folder | Storage default |

**Operasional**:
- Post-install: service otomatis aktif
- User membuka `hgss-viewer`, login (basic auth)
- Lihat transaksi, detail, print HGSS

### 1.2 Linux (Debian/Ubuntu + RHEL/Fedora)

**Packages**:
- Debian/Ubuntu: `hgss-agent-suite_<VERSION>.deb`
- RHEL/Fedora: `hgss-agent-suite-<VERSION>.rpm`

**Komponen terinstal**:

| Komponen | Tipe | Deskripsi |
|----------|------|-----------|
| `hgss-agentd` | Systemd service | Daemon, kolektor, verifier |
| `hgss-viewer` | CLI/Desktop UI | Desktop GUI atau CLI viewer |
| `hgssctl` | CLI | Admin command |
| `/var/lib/hgss/store/` | Data folder | Storage default |
| `/etc/hgss/` | Config folder | Policy config, credentials |

**Operasional**:
```bash
sudo systemctl enable --now hgss-agentd   # Enable & start
hgss-viewer                               # Launch UI (X11 / Wayland)
```

---

## 2. Struktur Repository (Normatif, File-Level)

Spesifikasi ini berlaku untuk monorepo atau repo terpisah. Struktur ini normatif untuk build suite dan CI/CD.

```
hgss-evidence-agent-suite/
├── README.md
├── LICENSE
├── VERSION
│
├── spec/
│   ├── AUDIT_EVIDENCE_SCHEMA.md       # Schema frozen (normatif)
│   ├── HCVM_ISA.md                    # Referensi ISA (optional mirror)
│   └── HGSS_EVIDENCE_AGENT_SUITE_SPEC.md  # This file
│
├── agent/
│   ├── src/
│   │   ├── main.rs (atau main.go)     # Agent core (service entry)
│   │   │
│   │   ├── collector/
│   │   │   ├── mod.rs                 # Kolektor evidence per transaksi
│   │   │   ├── event_reader.rs        # Baca event.cbor input
│   │   │   └── trace_reader.rs        # Baca trace.jsonl input
│   │   │
│   │   ├── verifier/
│   │   │   ├── mod.rs                 # Wrapper pemanggil hgss_verify_evidence.py
│   │   │   ├── schema_validator.rs    # Schema frozen checker
│   │   │   └── result.rs              # Struct hasil verifikasi
│   │   │
│   │   ├── trace/
│   │   │   ├── parse_jsonl.rs         # Parser trace.jsonl → list events
│   │   │   ├── digest_cbor.rs         # Builder canonical CBOR + SHA256
│   │   │   ├── lanes_derive.rs        # Derivasi trace_lanes.jsonl (28-lane)
│   │   │   └── models.rs              # TraceEvent struct, Lane struct
│   │   │
│   │   ├── storage/
│   │   │   ├── mod.rs                 # Storage ops
│   │   │   ├── worm_append.rs         # Append-only writer interface
│   │   │   ├── tx_store.rs            # Transaction folder layout
│   │   │   └── index.rs               # Indexing & lookup
│   │   │
│   │   ├── policy/
│   │   │   ├── mod.rs                 # Policy loader
│   │   │   ├── policy.rs              # Policy struct (trace allowed, memory limit, etc)
│   │   │   └── default_policy.toml    # Default policy template
│   │   │
│   │   └── crypto/
│   │       ├── cbor_canonical.rs      # RFC 8949 canonical CBOR encoder
│   │       └── digest.rs              # SHA256, HMAC helpers
│   │
│   ├── tests/
│   │   ├── integration_test.rs        # End-to-end test (collect → verify → store)
│   │   ├── trace_derive_test.rs       # 28-lane derivation test
│   │   └── fixtures/                  # Test data (trace.jsonl, event.cbor)
│   │
│   ├── packaging/
│   │   ├── windows/
│   │   │   ├── installer.wxs          # WiX installer script
│   │   │   ├── service_install.ps1    # PowerShell service installer
│   │   │   └── build.sh               # Build script
│   │   │
│   │   ├── linux/
│   │   │   ├── debian/
│   │   │   │   ├── control            # deb metadata
│   │   │   │   ├── postinst           # Post-install script
│   │   │   │   └── preinst            # Pre-install script
│   │   │   ├── redhat/
│   │   │   │   └── hgss-agent.spec    # RPM spec
│   │   │   └── build.sh               # Build script
│   │   │
│   │   └── systemd/
│   │       └── hgss-agentd.service    # Systemd unit file
│   │
│   ├── Cargo.toml (atau go.mod)       # Dependency manifest
│   └── Makefile                       # Build orchestration
│
├── viewer/
│   ├── src/
│   │   ├── main.rs (atau main.go)     # Viewer entry
│   │   │
│   │   ├── ui/
│   │   │   ├── login.rs               # Login window (username + password)
│   │   │   ├── list.rs                # Transaction list view
│   │   │   ├── detail.rs              # Transaction detail view
│   │   │   ├── playback.rs            # Trace playback (global + 28-lane)
│   │   │   └── styles.css             # UI theming
│   │   │
│   │   ├── playback/
│   │   │   ├── trace_player.rs        # Step-by-step trace navigator
│   │   │   └── lanes28.rs             # 28-lane timeline builder & renderer
│   │   │
│   │   ├── export/
│   │   │   ├── print_hgss.rs          # PDF/HTML/JSON export builder
│   │   │   └── templates/             # PDF/HTML templates
│   │   │       ├── summary.html
│   │   │       └── summary.json.template
│   │   │
│   │   ├── auth/
│   │   │   └── login.rs               # Auth handler (local credentials)
│   │   │
│   │   └── storage_reader.rs          # Read-only access ke /var/lib/hgss/store/
│   │
│   ├── Cargo.toml (atau package.json) # Viewer dependencies
│   └── Makefile
│
├── tools/
│   ├── hgss_verify_evidence.py        # Strict verifier (Python, normatif)
│   ├── print_release_state.py         # Release summary printer
│   ├── hgss_make_example_event.py     # Demo generator (optional)
│   └── audit_checklist.py             # Checklist validator
│
├── ci/
│   ├── build_windows.sh               # CI script: Windows build
│   ├── build_linux.sh                 # CI script: Linux build
│   ├── test.sh                        # Unit + integration tests
│   └── sign_binaries.sh               # Code signing (optional)
│
└── Makefile                           # Root orchestration

```

---

## 3. Struktur Penyimpanan Runtime (Normatif)

Semua transaksi disimpan deterministik dan mudah diaudit dengan policy append-only.

### 3.1 Root Storage (Default Paths)

| Platform | Path |
|----------|------|
| Windows | `%ProgramData%\HGSS\store\` |
| Linux | `/var/lib/hgss/store/` |

### 3.2 Layout Per Transaksi

**Konvensi ID**: Setiap transaksi menggunakan `<event_sha256>` (Canonical CBOR digest) sebagai folder ID unik. Ini memastikan determinism dan auditable.

```
store/
├── tx/
│   └── <event_sha256>/          # Contoh: a1b2c3d4e5f6...
│       ├── event.cbor           # [N] Evidence event (Canonical CBOR)
│       ├── auditlog.jsonl       # [I] Human-readable log (derived)
│       ├── trace.jsonl          # [N] Trace bytes (31 lines, locked)
│       ├── trace_lanes.jsonl    # [N] Derived 28-lane timeline
│       ├── verify_report.json   # [N] Strict verifier output
│       ├── hc18dc.cbor          # [N] HC18DC canonical artifact
│       ├── index.json           # [N] Small index (metadata)
│       │
│       └── print/
│           ├── hgss_summary.pdf # [I] "Print HGSS" output
│           └── hgss_summary.json
│
└── audit_log/
    └── agent.log               # [I] Agent operation log (append-only)
```

**Legend**:
- `[N]` = Normatif, frozen, part of verification contract
- `[I]` = Informational, derived, tidak crucial untuk verifikasi

### 3.3 Aturan Penyimpanan (Fail-Closed)

1. **Append-only**: Tidak boleh delete/modify file yang sudah ada di `tx/<event_sha256>/`
2. **Verify then store**: Sebelum folder ditandai selesai, `verify_report.json` harus ditulis
3. **Jika verifikasi FAIL/TRAP**: 
   - Folder tetap ada (forensik)
   - Status ditandai di `verify_report.json`
   - Evidence tidak ditolak, hanya ditandai FAILED
4. **Backup policy**: Agent memiliki option untuk backup ke external storage (optional)

---

## 4. Format Artefak (Normatif)

### 4.1 `event.cbor` — Canonical CBOR Evidence Event

**Format**: RFC 8949 Canonical CBOR (deterministic encoding)

**Struktur** (berdasarkan AUDIT_EVIDENCE_SCHEMA.md, Section 1-12):

```cbor
{
  "policy_id": "policy-uuid-v1.0",
  "nonce96": "hex-string-24-char",
  "nonce_lease_cycles": 128000,
  "lease_evidence": byte_string,
  "lease_evidence_sha256": "hex-64-char",
  
  "commitment": "hex-64-char",           # Plaintext commitment (if allowed)
  "commitment_mac_tag": "hex-64-char",   # HMAC-SHA256
  
  "aad": byte_string,
  "aad_sha256": "hex-64-char",
  
  "ciphertext": byte_string,
  "ciphertext_sha256": "hex-64-char",
  
  "trace_events": [
    {"i": 0, "pc": 0, "iw_hex": "0x40000000", "opcode": 64, ...},
    ...
    {"i": 30, "pc": 136, "iw_hex": "0xff000000", "opcode": 255, ...}
  ],
  "trace_sha256": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
  "trace_event_count": 31,
  
  "event_status": "PASS",         # atau FAIL, TRAP
  "event_timestamp_rfc3339": "2026-03-03T...",
  "event_sha256": "hex-64-char"   # Computed dari canonical CBOR(this object)
}
```

**Aturan**:
- Encoding harus RFC 8949 canonical (deterministic byte order)
- `trace_sha256` diperhitungkan dari `trace_events` list (lihat §4.3)
- `event_sha256` diperhitungkan dari keseluruhan event object
- Tidak boleh ada field tambahan di luar schema

### 4.2 `trace.jsonl` — Trace JSONL Bytes (Locked)

**Format**: JSON Lines (1 JSON object per line, newline-delimited)

**Wajib ada field per event**:

```json
{
  "i": 0,
  "pc": 0,
  "iw_hex": "0x40000000",
  "opcode": 64,
  "rd": 0,
  "ra": 0,
  "rb": 0,
  "subop": 0,
  "imm8": 0,
  "ext_u32_hex": "0x00000000"
}
```

**Aturan**:
- Total lines = `trace_event_count` (locked = 31)
- Urutan baris = naik (i=0, i=1, ..., i=30)
- Setiap field harus present, tipe harus valid
- No extra fields allowed (forward-compat hanya via schema version)
- File encoding = UTF-8

### 4.3 `trace_sha256` — Locked Digest (Normatif)

**Perhitungan**:

```
1. Parse trace.jsonl → list<TraceEvent> (urutan naik per i)
2. Encode list itu ke Canonical CBOR per RFC 8949
3. SHA256(canonical_bytes) = trace_sha256
4. Result: "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363"
```

**Aturan**:
- Calculation dilakukan di `agent/src/trace/digest_cbor.rs` (Rust) atau equivalent
- CBOR canonical = deterministic encoding (encoding integer, string, map keys lexicographically sorted)
- SHA256 output = lowercase hex string, 64 chars
- **LOCKED VALUE**: `trace_sha256_expected = "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363"`

**Verifikasi**:

```
trace_sha256_recomputed = SHA256(Canonical CBOR from trace.jsonl)
ASSERT(trace_sha256_recomputed == event.trace_sha256)
IF FAIL → report FAIL/TRAP in verify_report.json
```

### 4.4 `trace_event_count` — Locked Count

**Nilai**: 31 (sesuai data kamu)

**Perhitungan**:

```
trace_event_count = len(trace.jsonl lines)  # Harus = 31
```

**Verifikasi**:

```
actual_count = count_lines(trace.jsonl)
ASSERT(actual_count == event.trace_event_count)
IF FAIL → report FAIL/TRAP
```

### 4.5 `auditlog.jsonl` — Informational, Derived

**Format**: Single-line JSON object, derived dari `event.cbor` untuk human readability.

**Tujuan**: Memudahkan offline audit tanpa perlu CBOR decoder.

**Struktur** (superset dari event.cbor fields, flattened):

```json
{
  "policy_id": "policy-uuid-v1.0",
  "nonce96": "...",
  "nonce_lease_cycles": 128000,
  "lease_evidence_sha256": "...",
  "commitment": "...",
  "commitment_mac_tag": "...",
  "aad_sha256": "...",
  "ciphertext_sha256": "...",
  "trace_sha256": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
  "trace_event_count": 31,
  "event_status": "PASS",
  "event_timestamp_rfc3339": "2026-03-03T...",
  "event_sha256": "..."
}
```

### 4.6 `trace_lanes.jsonl` — Derived 28-Lane Timeline (Normatif Derivation)

**Tujuan**: Memungkinkan playback per lane (huruf) tanpa menciptakan data fiktif, mendasarkan pada instruksi semantik dari trace aktual.

**Format**: JSON Lines, setiap baris = trace event + lane metadata.

```json
{
  "i": 0,
  "pc": 0,
  "iw_hex": "0x40000000",
  "opcode": 64,
  "rd": 0,
  "ra": 0,
  "rb": 0,
  "subop": 0,
  "imm8": 0,
  "ext_u32_hex": "0x00000000",
  
  "letter_index_active": null,
  "letter_id_active": null,
  "lane_source": "unset"
}
```

**Lihat §5 untuk algoritma derivasi**.

### 4.7 `verify_report.json` — Strict Verifier Output

**Format**: JSON object, output dari `hgss_verify_evidence.py` setelah strict validation.

**Struktur**:

```json
{
  "verification_status": "PASS",    # atau "FAIL", "TRAP"
  "verification_timestamp": "2026-03-03T...",
  
  "checks": {
    "schema_compliance": {
      "passed": true,
      "message": "Schema matches AUDIT_EVIDENCE_SCHEMA.md v1.HC18DC"
    },
    "trace_digest_match": {
      "passed": true,
      "expected_sha256": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
      "computed_sha256": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
      "message": "trace_sha256 matches"
    },
    "trace_event_count_match": {
      "passed": true,
      "expected": 31,
      "actual": 31,
      "message": "Event count matches"
    },
    "nonce_lease_verify": {
      "passed": true,
      "message": "Nonce lease valid (not exhausted)"
    },
    "lease_evidence_verify": {
      "passed": true,
      "message": "Lease evidence signature valid"
    },
    "commitment_mac_verify": {
      "passed": true,
      "message": "MAC tag valid (HMAC-SHA256)"
    },
    "cbor_canonical": {
      "passed": true,
      "message": "Event CBOR is RFC 8949 canonical"
    }
  },
  
  "trap_codes": [],    # Jika TRAP: list trap codes (16 types per HISA spec)
  
  "evidence_digest": "...",    # event_sha256 dari event.cbor
  "trace_digest": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
  
  "notes": "All checks passed. Evidence is production-ready."
}
```

### 4.8 `hc18dc.cbor` — Canonical HC18DC Artifact

**Tujuan**: Final, publishable evidence artifact per AUDIT_EVIDENCE_SCHEMA.md frozen.

**Format**: Canonical CBOR (identical ke `event.cbor`, atau subset thereof sesuai HC18DC spec)

**Aturan**:
- Same structure as `event.cbor`
- Canonical CBOR encoding (RFC 8949)
- Dapat disimpan standalone untuk archival/publication
- Digest: computed as needed

### 4.9 `index.json` — Small Metadata Index

**Tujuan**: Fast lookup, tidak untuk verifikasi, hanya metadata.

**Struktur**:

```json
{
  "event_sha256": "a1b2c3d4e5f6...",
  "trace_sha256": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
  "trace_event_count": 31,
  "timestamp": "2026-03-03T10:30:45Z",
  "status": "PASS",
  "policy_id": "policy-uuid-v1.0",
  "nonce96": "...",
  "size_bytes": {
    "event_cbor": 2048,
    "trace_jsonl": 4096,
    "verify_report_json": 1024
  }
}
```

---

## 5. Derivasi 28-Lane Timeline (Deterministik, Tanpa Dummy)

Tujuan: per-huruf (0..27) lane timeline untuk trace playback, **tanpa menciptakan data fiktif**, deterministik dari instruksi semantik + urutan trace.

### 5.1 Mapping Index → Huruf (Locked, Normatif)

**Alphabet Hijaiyyah (28 huruf)**:

```
Index  Huruf  Index  Huruf  Index  Huruf  Index  Huruf
------  ------  ------  ------  ------  ------  ------  ------
0      ا      7      د      14     ط      21     ف
1      ب      8      ذ      15     ظ      22     ق
2      ت      9      ر      16     ع      23     ك
3      ث      10     ز      17     غ      24     ل
4      ج      11     س      18     ص      25     م
5      ح      12     ش      19     ض      26     ن
6      خ      13     ق      20     ق      27     و
                                                    28     ه
                                                    29     ي
```

**Correction**: Dengan 28 huruf + hamza, mapping adalah:

```
0=ا, 1=ب, 2=ت, 3=ث, 4=ج, 5=ح, 6=خ, 7=د, 8=ذ, 9=ر, 10=ز, 11=س, 12=ش, 13=ص, 14=ض, 15=ط, 16=ظ, 17=ع, 18=غ, 19=ف, 20=ق, 21=ك, 22=ل, 23=م, 24=ن, 25=و, 26=ه, 27=ي
```

**Ini locked**: Semua trace_lanes.jsonl harus menggunakan mapping ini.

### 5.2 Algoritma Derivasi (Normatif)

**Input**: 
- `trace.jsonl` (31 events dengan field `i`, `iw_hex`, `opcode`, dll)

**Output**:
- `trace_lanes.jsonl` (31 events + lane fields)

**Pseudo-code**:

```python
def derive_lanes(trace_jsonl_path: str) -> str:
    """
    Read trace.jsonl, add lane fields, write trace_lanes.jsonl
    """
    letter_map = [
        "ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", 
        "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", 
        "ق", "ك", "ل", "م", "ن", "و", "ه", "ي"
    ]
    
    trace_events = parse_jsonl(trace_jsonl_path)
    
    # State: current active lane (context)
    letter_index_active = None
    
    output_events = []
    
    for event in trace_events:
        i = event["i"]
        iw_hex = event["iw_hex"]
        opcode = event["opcode"]
        
        # Decode instruction semantics
        # Check: is this a LDH_V18 (Load Deterministic Hijaiyyah v18)?
        # Assume HISA opcode for LDH_V18 = some fixed value (e.g., 0x50)
        # If yes, extract operand index k (typically in rd or imm field)
        
        LDH_V18_OPCODE = 0x50  # Hypothetical; replace dengan actual HISA opcode
        
        if opcode == LDH_V18_OPCODE:
            # Load new lane
            k = event.get("rd", None)  # atau imm8, sesuai ISA
            if 0 <= k < 28:
                letter_index_active = k
                lane_source = "ldh_v18"
            else:
                # Operand out of range; remain unchanged
                lane_source = "inherit" if letter_index_active is not None else "unset"
        else:
            # Not a lane-switching instruction; inherit
            lane_source = "inherit" if letter_index_active is not None else "unset"
        
        # Derive letter_id_active
        letter_id_active = (
            letter_map[letter_index_active] 
            if letter_index_active is not None 
            else None
        )
        
        # Build output event
        output_event = {
            **event,  # Keep all original trace fields
            "letter_index_active": letter_index_active,
            "letter_id_active": letter_id_active,
            "lane_source": lane_source
        }
        
        output_events.append(output_event)
    
    # Write to trace_lanes.jsonl
    write_jsonl(trace_lanes_path, output_events)
    
    return trace_lanes_path
```

**Aturan**:

1. **LDH_V18 instruction detection**: Agent harus mendecode `iw_hex` menggunakan HISA ISA decoder. Jika opcode = LDH_V18, extract operand index.
2. **Context inheritance**: Jika bukan LDH_V18, inherit nilai terakhir `letter_index_active`. Jika belum pernah ada, set null.
3. **lane_source tracking**: Catat sumber (LDH instruction / inherited / unset)
4. **Deterministic**: Algorithm hanya bergantung pada trace events + ISA semantics, tidak ada random atau tebakan.

### 5.3 Keterangan: LDH_V18 Opcode

Agent perlu mengetahui opcode instruction HISA untuk LDH_V18. Ini terdapat di:
- `spec/HCVM_ISA.md` (instruction list)
- atau dari `src/hgss/hcvm/isa.rs` (atau equivalent)

**Contoh** (asumsi):
- Opcode 0x50 atau 80 decimal = LDH_V18
- Operand (lane index) berada di field `rd` atau `imm8` (sesuai spec)

---

## 6. Workflow Agent End-to-End (Fail-Closed)

Untuk setiap transaksi yang masuk (event.cbor + trace.jsonl):

### 6.1 Collect Phase

```
Input:
  - event.cbor (dari perbankan atau upstream system)
  - trace.jsonl (dari HISA-VM execution)
  
Actions:
  1. Read event.cbor → parse Canonical CBOR
  2. Read trace.jsonl → parse JSON Lines
  3. Extract locked values:
     - trace_sha256_expected := event.trace_sha256
     - trace_event_count_expected := event.trace_event_count
     - event_sha256_expected := event.event_sha256
```

### 6.2 Recompute & Compare Phase (Critical)

```
1. Parse trace.jsonl → list<TraceEvent>
2. Encode list ke Canonical CBOR
   canonical_bytes := RFC_8949_canonical_encode(trace_events)
3. Compute digest:
   trace_sha256_computed := SHA256(canonical_bytes)
4. Compare:
   IF trace_sha256_computed != trace_sha256_expected
     → Status = FAIL
     → Log: "trace_sha256 mismatch"
     → goto Store phase (dengan status FAIL)
5. Count events:
   actual_count := len(trace.jsonl lines)
   IF actual_count != trace_event_count_expected
     → Status = FAIL
     → Log: "event count mismatch"
     → goto Store phase
6. Recompute event_sha256 (sanity check):
   event_sha256_computed := SHA256(RFC_8949_canonical_encode(event))
   IF event_sha256_computed != event_sha256_expected
     → Status = FAIL
     → goto Store phase
```

### 6.3 Strict Verify Phase (Schema Frozen)

```
Action:
  Call hgss_verify_evidence.py dengan parameters:
  - input_event.cbor
  - input_trace.jsonl
  - reference_schema = spec/AUDIT_EVIDENCE_SCHEMA.md
  - policy = /etc/hgss/policy.toml
  
Function hgss_verify_evidence.py:
  1. Load schema dari file frozen
  2. Validate event.cbor against schema
     - Check required fields
     - Check field types
     - Check value constraints (e.g., nonce_lease_cycles > 0)
  3. Validate trace.jsonl against schema
     - Check every line is valid JSON
     - Check required fields per event
  4. Validate lease policy
     - Check nonce uniqueness (if history available)
     - Check lease cycles > 0, not exhausted
  5. Validate commitment & MAC
     - If commitment present, SHA256 must match
  6. Validate ciphertext
     - If ciphertext present, SHA256 must match
  7. Validate CBOR canonical
     - Re-encode event.cbor, ensure bytes match original (byte-exact)
  
Output:
  - verify_report.json (success / fail / trap)
  - If FAIL/TRAP: still return report, status = FAIL/TRAP

Status Codes:
  - PASS: All checks passed
  - FAIL: Schema violation, digest mismatch, policy violation
  - TRAP: Nonce exhaustion, lease expired, critical error
```

### 6.4 Generate Derived Artifacts Phase

```
Actions (if Recompute || Verify passed OR FAIL):
  1. Derive trace_lanes.jsonl
     Call derive_lanes(trace.jsonl) → trace_lanes.jsonl
  2. Write auditlog.jsonl
     Flatten event.cbor to JSON, add metadata, write single line
  3. Copy/link hc18dc.cbor
     (or derivation if needed per HC18DC spec)
```

### 6.5 Store Phase (Append-Only)

```
Actions:
  1. Create folder: store/tx/<event_sha256>/
     - If already exists, check if transaction is idempotent
     - (typically should not re-process same event_sha256)
  
  2. Write files (atomic or all-or-nothing):
     - event.cbor (copy input)
     - trace.jsonl (copy input)
     - verify_report.json (generated)
     - trace_lanes.jsonl (derived)
     - auditlog.jsonl (derived for readability)
     - hc18dc.cbor (final artifact)
     - index.json (metadata)
  
  3. Append to agent.log:
     timestamp, event_sha256, status (PASS/FAIL/TRAP), trace_sha256
  
  4. Policy compliance:
     - Folder permissions: read-only for agent owner, read for viewer user
     - No deletion allowed (WORM policy)
  
  Return:
    - Status: PASS, FAIL, or TRAP
    - event_sha256: folder ID
    - Message: human-readable result
```

### 6.6 Audit Logging

```
Log file: /var/lib/hgss/store/audit_log/agent.log (append-only)

Format per line:
  timestamp | operation | event_sha256 | status | trace_sha256 | message

Example:
  2026-03-03T10:30:45Z | collect | a1b2c3d4e5f6... | - | - | Input received
  2026-03-03T10:30:46Z | verify | a1b2c3d4e5f6... | PASS | 63717435... | Trace digest match
  2026-03-03T10:30:47Z | store | a1b2c3d4e5f6... | PASS | 63717435... | Evidence stored

Retention:
  - Never delete (append-only)
  - Optional rotation: create agent.log.1, agent.log.2, ... per size
```

---

## 7. UI Viewer — Fungsi dan Halaman

### 7.1 Login Page

**Tujuan**: Autentikasi user sebelum akses evidence.

**Field**:
- Username (text input)
- Password (masked input)
- Button: Login
- Message area: error/info

**Behavior**:
1. User entry username + password
2. Agent verifies against local credentials (atau LDAP if configured)
3. Success → grant session token, navigate to Transaction List
4. Failure → show error, stay on Login
5. Log login attempt (timestamp, username, success/failure)

**Credentials**:
- Default: username=`admin`, password=`admin` (CHANGE on first run)
- Storage: hashed (bcrypt atau PBKDF2), in `/etc/hgss/users.json` or local DB
- Audit: all login attempts logged

### 7.2 Transaction List Page

**Tujuan**: Overview dari semua transaksi.

**Table Columns**:

| Column | Type | Source |
|--------|------|--------|
| Timestamp | RFC3339 | event.timestamp |
| Policy ID | UUID | event.policy_id |
| Nonce96 | Hex (24) | event.nonce96 |
| Event SHA256 | Hex (first 16) | event_sha256 |
| Trace SHA256 | Hex (first 16) | trace_sha256 |
| Trace Events | Int | trace_event_count (31) |
| Status | PASS/FAIL/TRAP | verify_report.json |

**UI Elements**:
- Sortable columns (click header)
- Filter: by timestamp range, status, policy ID
- Pagination: 20 per page
- Action per row: click to open Detail view

**Data Source**:
- Read from `store/tx/*/index.json`
- Fast lookup (no CBOR decoding needed)

### 7.3 Transaction Detail Page

**Tujuan**: Deep dive into single transaction, inspect evidence fields, playback trace.

**Sections**:

#### 7.3.1 Overview Card
```
Event SHA256: a1b2c3d4e5f6...
Policy ID: policy-uuid-v1.0
Timestamp: 2026-03-03T10:30:45Z
Status: PASS / FAIL / TRAP
```

#### 7.3.2 Evidence Node Digests
```
Lease Evidence SHA256:  [hash] [Copy]
Nonce96:               [value] [Copy]
Commitment:            [hash] [Copy]
MAC Tag (HMAC-SHA256): [hash] [Copy]
AAD SHA256:            [hash] [Copy]
Ciphertext SHA256:     [hash] [Copy]
Trace SHA256:          [hash] [Copy]
  └─ trace_event_count: 31
Event SHA256:          [hash] [Copy]
```

#### 7.3.3 Verify Report
```
[Card: Verification Status]
Status: PASS
Timestamp: 2026-03-03T10:30:46Z

[Checks List]
✓ Schema Compliance
✓ Trace Digest Match
✓ Event Count Match
✓ Nonce Lease Valid
✓ Commitment MAC Valid
✓ CBOR Canonical

[Notes]
All checks passed. Evidence is production-ready.
```

#### 7.3.4 File Links
```
[Files]
[event.cbor] [Download]
[trace.jsonl] [Download]
[hc18dc.cbor] [Download]
[verify_report.json] [View]
[auditlog.jsonl] [View]
```

#### 7.3.5 Global Trace Playback
```
[Trace Player Widget]

Step: 0/30  [◀ Previous] [Play] [Next ▶] [▶▶ Goto step 30]

Step 0:
  PC: 0x0000
  Instruction: 0x40000000 (LOAD)
  Opcode: 64
  RD: 0, RA: 0, RB: 0
  Subop: 0, Imm8: 0
```

#### 7.3.6 28-Lane Timeline
```
[Lane Timeline Widget]

(Visual timeline: 0..30 steps, 28 lanes stacked vertically)

Lane 0 (ا):  [active step 5-10]
Lane 1 (ب):  [unset]
Lane 2 (ت):  [active step 12-20]
...
Lane 27 (ي): [active step 25-30]

Legend:
  Green = active (letter_index_active set)
  Gray = inherited or unset
```

### 7.4 Tombol "Print HGSS"

**Tujuan**: Generate printable/archivable summary dari transaksi.

**Output Format**:
- PDF (default)
- HTML (optional)
- JSON (optional)

**Isi Minimal** (hgss_summary.pdf / .html):

```
═══════════════════════════════════════════════════════════
    HGSS Evidence Agent Suite — Transaction Summary
═══════════════════════════════════════════════════════════

Generated: 2026-03-03T10:45:00Z
Event ID: a1b2c3d4e5f6...

[Section 1: Transaction Metadata]
  Policy ID:        policy-uuid-v1.0
  Timestamp:        2026-03-03T10:30:45Z
  Nonce96:          0x123456789abc...
  Status:           PASS

[Section 2: Evidence Digests (Node Proof)]
  Trace SHA256:     63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363
  Trace Event Count: 31
  
  Lease Evidence:   [hash]
  Commitment:       [hash]
  MAC Tag:          [hash]
  AAD:              [hash]
  Ciphertext:       [hash]
  Event SHA256:     [hash]

[Section 3: Verification Status]
  ✓ Schema Compliance
  ✓ Trace Digest Match
  ✓ Event Count Match
  ✓ Nonce Lease Valid
  ✓ Commitment MAC Valid
  ✓ CBOR Canonical
  
  Result: PASS
  Message: All checks passed. Evidence is production-ready.

[Section 4: Storage Details]
  Storage Path: /var/lib/hgss/store/tx/a1b2c3d4e5f6.../
  Files: event.cbor, trace.jsonl, hc18dc.cbor, verify_report.json
  Retention: Append-only (WORM policy)

[Section 5: Reference]
  Specification: AUDIT_EVIDENCE_SCHEMA.md v1.HC18DC
  Reference: HGSS Evidence Agent Suite v1.0
  
  For details: https://github.com/... [link to bundle]

═══════════════════════════════════════════════════════════
Printed: [Print timestamp]
═══════════════════════════════════════════════════════════
```

**Template**:
- viewer/src/export/templates/summary.html (Jinja2 / Handlebars)
- CSS untuk print-friendly styling

---

## 8. Installation & Usage — User-Friendly

### 8.1 Windows

**Step-by-Step**:

1. **Download installer**
   ```
   https://github.com/.../releases/HGSS-Evidence-Agent-Suite-1.0.exe
   ```

2. **Run installer**
   ```
   Double-click HGSS-Evidence-Agent-Suite-1.0.exe
   → Windows Installer wizard
   → Follow prompts (License, Install Location)
   → Click "Install"
   → Finish
   ```

3. **Verify installation**
   ```
   Open Windows Services (services.msc)
   → Scroll to "HGSS Agent Service"
   → Status should be "Running"
   ```

4. **Launch UI Viewer**
   ```
   Start Menu → search "HGSS Viewer"
   → Click to launch
   → Login window appears
   → Username: admin, Password: admin (change on first login)
   → Click "Login"
   → Transaction List view appears
   ```

5. **Test (optional)**
   ```
   Terminal (as admin):
   > hgssctl status
   → Shows service status, store location, etc.
   
   > hgssctl demo
   → Creates example transaction for testing
   ```

### 8.2 Linux (Debian/Ubuntu)

**Step-by-Step**:

1. **Download package**
   ```bash
   wget https://github.com/.../releases/hgss-agent-suite_1.0_amd64.deb
   ```

2. **Install package**
   ```bash
   sudo dpkg -i hgss-agent-suite_1.0_amd64.deb
   # or
   sudo apt install ./hgss-agent-suite_1.0_amd64.deb
   ```

3. **Enable & start service**
   ```bash
   sudo systemctl enable hgss-agentd
   sudo systemctl start hgss-agentd
   ```

4. **Verify service**
   ```bash
   sudo systemctl status hgss-agentd
   # Output: ● hgss-agentd.service - HGSS Evidence Agent Daemon
   #         Loaded: loaded (/etc/systemd/system/hgss-agentd.service; enabled)
   #         Active: active (running) since ...
   ```

5. **Launch UI Viewer**
   ```bash
   hgss-viewer
   # GUI window opens, or CLI prompt if running headless
   # Login with default credentials
   ```

### 8.3 Linux (RHEL/Fedora/CentOS)

**Step-by-Step**:

1. **Download RPM package**
   ```bash
   wget https://github.com/.../releases/hgss-agent-suite-1.0-1.el8.x86_64.rpm
   ```

2. **Install package**
   ```bash
   sudo rpm -i hgss-agent-suite-1.0-1.el8.x86_64.rpm
   # or
   sudo dnf install hgss-agent-suite-1.0-1.el8.x86_64.rpm
   ```

3. **Enable & start service**
   ```bash
   sudo systemctl enable hgss-agentd
   sudo systemctl start hgss-agentd
   ```

4. **Verify**
   ```bash
   sudo systemctl status hgss-agentd
   hgss-viewer
   ```

### 8.4 Headless (Linux Server, no GUI)

**For server deployment without X11 / Wayland**:

```bash
# Viewer runs in CLI mode or REST API mode
hgss-viewer --headless --api-port 8080

# Access via browser:
curl http://localhost:8080/api/transactions
curl http://localhost:8080/api/transactions/<event_sha256>/detail
curl http://localhost:8080/api/transactions/<event_sha256>/print
```

---

## 9. Domain Aplikasi (Use Cases)

Spesifikasi suite ini dirancang untuk sistem yang membutuhkan:

1. **Audit-grade evidence per transaksi/eksekusi**
   - Setiap eksekusi punya bukti kanonik + reproducible
   - Langit ke langit perbankan, compliance, legal

2. **Strict schema validation + locked digests**
   - Evidence tidak bisa dimodifikasi/ditafsir ulang
   - Fail-closed architecture

3. **Replay trace deterministik**
   - Bisa ulang-putar eksekusi step-by-step
   - Bisa analisis per lane/subsistem

4. **Append-only storage / WORM policy**
   - Forensik panjang tahun
   - Immutable audit log

### 9.1 Banking (Primary Domain)

- Setiap transaksi → event.cbor + trace.jsonl (dari crypto VM atau TEE)
- Agent verifikasi ketat, simpan HC18DC
- Auditor buka bundle tahunan, verifikasi ulang setiap transaksi
- Regulasi: PCI-DSS, Basel III, audit trail 7+ tahun

### 9.2 Compliance & Risk

- Setiap keputusan AI/ML → evidence artifact
- Explainability: print HGSS menunjukkan reasoning trail (via lanes)
- Nonprofitable auditable untuk regulasi

### 9.3 Supply Chain & Logistics

- Kargo tracking: setiap event punya proof
- Evidence chain: dari warehouse A ke B punya trace deterministic
- Blockchain alternative: offline-verifiable, no smart contract needed

### 9.4 Government / Justice

- Setiap dokumen hashing/signing punya audit trail
- Trace: siapa, kapan, dari-ke perangkat mana
- Archive: 30 tahun evidence offline-readable

---

## 10. Dependency & Technology Stack (Recommended)

### 10.1 Agent Service

**Language Options**:
- Rust (memory-safe, high performance, good for crypto)
- Go (simpler, good concurrency for I/O)

**Key Libraries**:

| Component | Rust | Go |
|-----------|------|-----|
| Canonical CBOR | `cbor::encode_canonical` | `github.com/fxamacker/cbor/v2` |
| SHA256 | `sha2::Sha256` | `crypto/sha256` |
| HMAC | `hmac::Hmac<Sha256>` | `crypto/hmac` |
| JSON | `serde_json` | `encoding/json` |
| CLI | `clap` | `github.com/urfave/cli` |
| Service | `daemonize` / `windows-service` | `yourbasic/daemon` |

### 10.2 Viewer UI

**Options**:
- **Tauri** (Rust-based, small footprint, web tech)
  - Frontend: React / Vue
  - Backend: Rust (IPC)
- **Electron** (Chromium-based, heavier, more flexible)
  - Frontend: React / Vue
  - Backend: Node.js or Rust bridge

### 10.3 Verifier Tool (Python)

**Language**: Python 3.9+

**Libraries**:
- `cbor2` — CBOR encode/decode
- `jsonschema` — schema validation
- `pydantic` — data validation
- `cryptography` — SHA256, HMAC, signature

### 10.4 Deployment & Packaging

**Windows**:
- WiX Toolset — `.msi` generator
- Authenticode signing (optional, for trust)

**Linux**:
- `cargo deb` — Debian package generator
- `cargo rpm` — RPM package generator
- systemd unit files (standardized)

---

## 11. Security & Compliance Considerations

### 11.1 Fail-Closed Architecture

```
Default behavior: DENY access unless verified
- If verify fails → status = FAIL, but evidence stored (forensic)
- If TRAP → status = TRAP, transaction logged, evidence stored
- UI shows status clearly: red for FAIL/TRAP
- No fallback/override without audit log
```

### 11.2 Credential Management

- Default password must be changed on first run (enforced)
- Hashing: bcrypt (cost=12) or PBKDF2-SHA256
- MFA: optional TOTP support (future)
- Token: JWT with short TTL (15 min) for session

### 11.3 Access Control

**Agent process**:
- Run as dedicated user: `hgss-agent` (Linux) or `Network Service` (Windows)
- Minimal privileges: read input, write to `/var/lib/hgss/store/`

**Viewer process**:
- Run as regular user (no special privileges)
- Read-only access to store (enforced by file permissions)

**Policy file** (`/etc/hgss/policy.toml`):
- Owned by root, mode 0644 (readable by agent)
- Signed/integrity-checked (optional: HMAC)

### 11.4 Audit Logging

- All access logged: login, access transaction, export, etc.
- Log tamper-evident: hashed chain (optional)
- Retention: same as evidence (never delete)

### 11.5 Cryptographic Digests

- SHA-256: current standard (RFC 3394)
- HMAC-SHA256: for MAC
- Future: SHA-3 option (if schema updated)
- No MD5 or SHA1

---

## 12. Testing & Validation

### 12.1 Unit Tests

```
tests/
├── trace_digest_test.rs      # test trace_sha256 computation
├── lanes_derive_test.rs      # test 28-lane derivation
├── cbor_canonical_test.rs    # test RFC 8949 encoding
├── verify_integration_test.rs # end-to-end flow
└── fixtures/
    ├── trace.jsonl           # test data (31 events)
    ├── event.cbor            # test data
    └── policy.toml           # test policy
```

### 12.2 Integration Test (End-to-End)

```python
# pseudocode
def test_full_pipeline():
    # Setup
    trace = load_test_trace("fixtures/trace.jsonl")  # 31 events
    event = load_test_event("fixtures/event.cbor")
    
    # Collect
    agent.collect(event, trace)
    
    # Recompute & verify
    trace_sha256_computed = compute_trace_sha256(trace)
    assert trace_sha256_computed == expected_value
    assert trace_event_count == 31
    
    # Verify
    report = hgss_verify_evidence(event, trace, schema)
    assert report.status == "PASS"
    assert report.checks.schema_compliance.passed
    assert report.trace_digest_match.passed
    
    # Store & derive
    tx_folder = agent.store(event)
    assert Path(tx_folder / "event.cbor").exists()
    assert Path(tx_folder / "trace_lanes.jsonl").exists()
    
    # UI read
    ui_list = viewer.read_transaction_list()
    assert len(ui_list) >= 1
    tx = ui_list[0]
    assert tx.status == "PASS"
```

---

## 13. Release Checklist

Sebelum publish ke production:

```
□ Code freeze: all commits tagged (v1.0)
□ Security audit: review crypto, file perms, auth
□ Unit tests: 100% pass
□ Integration tests: full pipeline pass
□ Documentation: README + man pages complete
□ Installer testing: try on fresh VM (Windows + Linux)
□ Bundle creation: offline auditor bundle complete
□ SHA256 manifest: signed with release key
□ GitHub release: tagged, notes, downloads
□ Website: downloads page updated
□ Announcement: release notes to stakeholders
```

---

## Appendix A: Template Artefak

### A.1 `index.json` — Struktur dan Contoh

**Tujuan**: Fast lookup untuk UI list, tanpa perlu decode/verify ulang.

**Struktur normatif**:

```json
{
  "event_sha256": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234ab",
  "trace_sha256": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
  "trace_event_count": 31,
  "timestamp_rfc3339": "2026-03-03T10:30:45.123456Z",
  "status": "PASS",
  "policy_id": "policy-v1.0-banking",
  "nonce96": "0x123456789abcdef0123456789abc",
  "size_bytes": {
    "event_cbor": 2048,
    "trace_jsonl": 4096,
    "verify_report_json": 1024
  },
  "verify_timestamp_rfc3339": "2026-03-03T10:30:46.234567Z",
  "files_present": {
    "event_cbor": true,
    "trace_jsonl": true,
    "trace_lanes_jsonl": true,
    "verify_report_json": true,
    "hc18dc_cbor": true
  }
}
```

**Aturan**:
- `event_sha256` MUST match folder ID.
- `status` MUST PASS / FAIL / TRAP, derived dari `verify_report.json`.
- Semua timestamp RFC3339 format.
- `files_present` memudahkan deteksi file corrupt atau missing.

---

### A.2 `verify_report.json` — Struktur Lengkap dan Contoh

**Tujuan**: Detail hasil strict verification.

**Struktur normatif**:

```json
{
  "verification_status": "PASS",
  "verification_timestamp_rfc3339": "2026-03-03T10:30:46.234567Z",
  "verifier_version": "hgss_verify_evidence.py v1.0",
  "schema_reference": "AUDIT_EVIDENCE_SCHEMA.md v1.HC18DC (frozen)",
  
  "checks": {
    "schema_compliance": {
      "passed": true,
      "message": "Event matches AUDIT_EVIDENCE_SCHEMA.md §1-12"
    },
    "trace_digest_match": {
      "passed": true,
      "expected_sha256": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
      "computed_sha256": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
      "message": "trace_sha256 recomputed matches locked value"
    },
    "trace_event_count_match": {
      "passed": true,
      "expected_count": 31,
      "actual_count": 31,
      "message": "Trace event count matches"
    },
    "trace_jsonl_format": {
      "passed": true,
      "lines_checked": 31,
      "message": "All trace.jsonl lines valid JSON, fields present"
    },
    "nonce_lease_verify": {
      "passed": true,
      "nonce96": "0x123456789abcdef0123456789abc",
      "nonce_lease_cycles": 128000,
      "message": "Nonce lease valid, cycles sufficient"
    },
    "lease_evidence_verify": {
      "passed": true,
      "lease_evidence_sha256_expected": "...",
      "lease_evidence_sha256_actual": "...",
      "message": "Lease evidence signature/MAC valid"
    },
    "commitment_mac_verify": {
      "passed": true,
      "commitment_present": true,
      "mac_tag_valid": true,
      "message": "Commitment MAC tag (HMAC-SHA256) verified"
    },
    "aad_sha256_match": {
      "passed": true,
      "expected": "...",
      "actual": "...",
      "message": "AAD digest matches"
    },
    "ciphertext_sha256_match": {
      "passed": true,
      "expected": "...",
      "actual": "...",
      "message": "Ciphertext digest matches"
    },
    "cbor_canonical": {
      "passed": true,
      "re_encoded_bytes_match": true,
      "message": "Event CBOR re-encoded bytes match original (RFC 8949 canonical)"
    },
    "event_sha256_match": {
      "passed": true,
      "expected": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234ab",
      "computed": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234ab",
      "message": "Event SHA256 (canonical digest) matches"
    }
  },
  
  "trap_codes": [],
  "trap_details": [],
  
  "evidence_summary": {
    "lease_evidence_sha256": "...",
    "trace_sha256": "63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363",
    "trace_event_count": 31,
    "commitment_sha256": "...",
    "aad_sha256": "...",
    "ciphertext_sha256": "...",
    "event_sha256": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234ab"
  },
  
  "overall_result": "PASS",
  "notes": "All evidence checks passed. Transaction is production-ready and audit-grade."
}
```

**Aturan normatif**:
- Jika **satu check FAIL**: `verification_status = "FAIL"`, output tetap ditulis, evidence disimpan untuk forensik.
- Jika **TRAP code triggered**: `verification_status = "TRAP"`, list trap codes dalam `trap_codes[]` dan `trap_details[]`.
- Semua digest MUST lowercase hex 64 chars.
- `checks.*` MUST berisi **passed** (boolean) + **message** (human-readable).

---

### A.3 `trace_lanes.jsonl` — Struktur dan Contoh Konkret

**Tujuan**: Timeline 28-lane untuk playback GUI.

**Struktur per baris**:

Setiap baris = trace event asli + 3 field lane tambahan:
- `letter_index_active` (int | null): indeks huruf aktif (0..27) atau null
- `letter_id_active` (string | null): huruf Hijaiyyah (ا..ي) atau null
- `lane_source` (string): `"ldh_v18"` | `"inherit"` | `"unset"`

**Contoh 3 baris pertama dari trace.jsonl kamu** (dengan asumsi opcode 80 decimal = LDH_V18):

```json
{"i":0,"pc":0,"iw_hex":"0x40000000","opcode":64,"rd":0,"ra":0,"rb":0,"subop":0,"imm8":0,"ext_u32_hex":"0x00000000","letter_index_active":null,"letter_id_active":null,"lane_source":"unset"}
{"i":1,"pc":8,"iw_hex":"0x40100000","opcode":64,"rd":1,"ra":0,"rb":0,"subop":0,"imm8":0,"ext_u32_hex":"0x00000000","letter_index_active":null,"letter_id_active":null,"lane_source":"unset"}
{"i":2,"pc":16,"iw_hex":"0x50050000","opcode":80,"rd":5,"ra":0,"rb":0,"subop":0,"imm8":0,"ext_u32_hex":"0x00000000","letter_index_active":5,"letter_id_active":"ح","lane_source":"ldh_v18"}
```

**Penjelasan**:
- **i=0, opcode=64**: LOAD (bukan LDH_V18) → `lane_source="unset"`, tidak ada lane aktif.
- **i=1, opcode=64**: LOAD lagi → `lane_source="unset"` (masih belum ada LDH_V18).
- **i=2, opcode=80**: Asumsi opcode 80 adalah LDH_V18, operand `rd=5` → set `letter_index_active=5` (huruf ح indeks 5) → `lane_source="ldh_v18"`.

**Aturan penulisan**:
- Urutan baris MUST sama dengan `trace.jsonl` (urut by `i`).
- Setiap baris MUST valid JSON (dapat di-parse dengan standar JSON parser).
- Field lama (i, pc, iw_hex, ..., ext_u32_hex) MUST tetap utuh, hanya ditambah 3 field baru.
- Tidak ada field tambahan selain yang ditetapkan.

---

## Appendix B: Contoh Flow Lengkap (Ilustratif)

### B.1 Input Transaksi
```
Masukan dari upstream (perbankan/HCVM):
  - event.cbor (Canonical CBOR, sudah locked trace_sha256/trace_event_count/event_sha256)
  - trace.jsonl (31 baris, UTF-8, JSON Lines)
```

### B.2 Agent Processing
```
1. Collect:
   Parse event.cbor, extract trace_sha256_expected="63717435...", trace_event_count_expected=31

2. Recompute:
   Parse trace.jsonl → 31 events
   Canonical CBOR encode → sha256 → "63717435..."
   MATCH ✓

3. Strict Verify:
   hgss_verify_evidence.py → all checks PASS
   Output: verify_report.json (status=PASS, all checks=true)

4. Derive:
   trace_lanes.jsonl (31 baris dengan lane fields)
   auditlog.jsonl (1 baris, derived human-readable, INFORMATIONAL)

5. Store:
   folder: store/tx/a1b2c3d4.../
   files: event.cbor, trace.jsonl, trace_lanes.jsonl, verify_report.json, hc18dc.cbor, index.json
   
   index.json: event_sha256, trace_sha256, trace_event_count, status=PASS, files_present={true,...}
   verify_report.json: all checks=true, status=PASS

6. UI Access:
   User login → list: [event_sha256, trace_sha256, 31, PASS]
   Click → detail: node digests, trace playback, lane timeline
   Print: hgss_summary.pdf dengan all verify checks + node digests
```

---

## Appendix C: Checklist Implementasi Software

Untuk pembuatan software suite (production-grade):

### C.1 Agent Service
- [ ] Canonical CBOR encoder/decoder (RFC 8949 tested)
- [ ] SHA256 digest compute + verification
- [ ] JSONL parser
- [ ] ISA instruction decoder (untuk LDH_V18 detection)
- [ ] Lane derivation algorithm
- [ ] Store/append-only writer
- [ ] Python verifier wrapper caller
- [ ] Audit log writer (append-only)
- [ ] Configuration loader (policy.toml sesuai spec normatif)
- [ ] Windows Service wrapper + Linux systemd unit

### C.2 Viewer UI
- [ ] Login screen (username+password, hashed storage)
- [ ] Transaction list (sortable, paginated, read from index.json)
- [ ] Transaction detail (digest display, file download)
- [ ] Global trace playback (step-by-step navigator)
- [ ] 28-lane timeline visualization (stacked lanes, animation play/pause)
- [ ] "Print HGSS" export (PDF/HTML/JSON template)
- [ ] Read-only file access (no modification button)
- [ ] Status indicator (PASS=green, FAIL/TRAP=red)

### C.3 Verifier Tool (hgss_verify_evidence.py)
- [ ] Schema loader (freeze AUDIT_EVIDENCE_SCHEMA.md)
- [ ] Event validation (all required fields, types, constraints)
- [ ] Trace validation (all lines valid JSON, count match)
- [ ] Lease/nonce validation (per policy rules)
- [ ] MAC/signature validation
- [ ] CBOR canonical check (re-encode and byte-compare)
- [ ] Output: verify_report.json (structured, all checks listed)

### C.4 Packaging
- [ ] Windows MSI installer (WiX)
- [ ] Linux deb package (control, postinst, systemd)
- [ ] Linux rpm package (.spec file, systemd)
- [ ] Code signing (optional but recommended for production)

### C.5 Testing
- [ ] Unit tests: canonical CBOR, SHA256, lane derivation
- [ ] Integration test: collect → verify → store → UI read
- [ ] Fixtures: trace.jsonl (31 events), event.cbor, policy.toml
- [ ] Test vectors: expected digest values (locked)

---

## References

1. **AUDIT_EVIDENCE_SCHEMA.md** — Evidence schema (frozen v1.HC18DC)
2. **RFC 8949** — Concise Binary Object Representation (CBOR)
3. **HCVM_ISA.md** — Instruction set specification
4. **PCI DSS 4.0** — Payment card industry compliance
5. **NIST SP 800-161** — Supply chain risk management

---

**Document Version**: 1.0 Normatif (dengan Appendix A-C)  
**Status**: Frozen / Production  
**Last Updated**: March 2026  
**Maintained By**: HGSS Evidence Agent Suite Team
