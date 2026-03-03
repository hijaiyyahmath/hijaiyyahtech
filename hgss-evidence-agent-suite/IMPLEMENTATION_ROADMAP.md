# HGSS Evidence Agent Suite — Implementation Roadmap

**Version**: 1.0 | **Status**: Specification & Repo Skeleton Ready | **Date**: March 2026

---

## ✅ Completed (Specification Phase)

### Documentation
- [x] **HGSS_EVIDENCE_AGENT_SUITE_SPEC.md** (normatif lengkap dengan Appendix A-C)
  - Scope, Deliverable, Repository structure
  - Storage layout, Artifact formats (CBOR, JSONL, JSON)
  - Lane derivation algorithm (deterministik, no dummy)
  - End-to-end workflow (fail-closed)
  - UI pages (login, list, detail, playback, print)
  - Installation guide (Windows, Linux)
  - Security & compliance considerations
  - **Appendix A**: Template index.json, verify_report.json, trace_lanes.jsonl examples
  - **Appendix B**: End-to-end flow illustration  
  - **Appendix C**: Implementation checklist

- [x] **AUDIT_EVIDENCE_SCHEMA.md** (schema frozen v1.HC18DC)
- [x] **README.md** (Quick start, features, architecture)
- [x] **LICENSE** (MIT)
- [x] **VERSION** (1.0)
- [x] **Makefile** (Build targets)
- [x] **Website documentation** (hijaiyyahtech.github.io)

### Locked Values
- [x] `trace_sha256` = `63717435d77bb16d2d3a76c010635ccf6575027b917b416d9c714692ad2a2363`
- [x] `trace_event_count` = `31`
- [x] All digests locked, no override allowed

---

## 🚀 Next Phase: Implementation (To-Do for Team)

### Agent Service (Rust or Go) — ~6-8 weeks

**Core Modules**:
- [ ] Canonical CBOR encoder/decoder (RFC 8949 tested)
- [ ] SHA256 & HMAC compute
- [ ] JSONL parser (trace events)
- [ ] ISA instruction decoder (for LDH_V18)
- [ ] Lane derivation algorithm
- [ ] Append-only store writer
- [ ] Python verifier wrapper
- [ ] Windows Service + Linux systemd integration

**Testing**:
- [ ] Unit tests (CBOR, SHA256, lanes, digest)
- [ ] Integration test (full pipeline)
- [ ] Fixtures (trace.jsonl, event.cbor, policy.toml)

### Viewer UI (Tauri or Electron) — ~4-6 weeks

**Pages**:
- [ ] Login screen
- [ ] Transaction list (sortable, paginated)
- [ ] Transaction detail (digests, file links)
- [ ] Global trace playback
- [ ] 28-lane timeline visualization
- [ ] Print HGSS (PDF/HTML/JSON export)

**Backend**:
- [ ] Storage reader (read-only)
- [ ] Auth handler
- [ ] File download server

### Packaging — ~2 weeks

**Windows**:
- [ ] WiX installer script (MSI)
- [ ] Service auto-start config
- [ ] Code signing (optional)

**Linux**:
- [ ] Debian package (deb) with postinst
- [ ] RHEL package (rpm) with spec
- [ ] systemd unit file

### CI/CD — ~1-2 weeks

- [ ] GitHub Actions workflows
- [ ] Build matrix (Windows, Ubuntu, Fedora)
- [ ] Unit + integration test gate
- [ ] Release asset signing
- [ ] SHA256 manifest generation

---

## 📋 Specification Completeness Checklist

### Requirements Coverage
- [x] Scope (IN/OUT)
- [x] Deliverable (Windows MSI, Linux deb/rpm)
- [x] Repository structure (file-level)
- [x] Storage layout (WORM, append-only)
- [x] Artifact formats (CBOR canonical, JSONL, JSON)
- [x] Lane derivation (deterministic, ISA-based)
- [x] End-to-end workflow (fail-closed)
- [x] UI functionality (6 pages)
- [x] Installation procedures (Windows, Linux)
- [x] Domain applications (banking, compliance, supply chain, justice)
- [x] Technology stack (Rust/Go, Tauri/Electron, Python)
- [x] Security & compliance (auth, WORM, crypto)
- [x] Testing strategy (unit + integration)
- [x] Release checklist

### Example Artifacts
- [x] index.json template (fast lookup)
- [x] verify_report.json template (validation output)
- [x] trace_lanes.jsonl example (3 concrete rows)

### Documentation
- [x] Spec document (normatif, ~1500 lines)
- [x] Quick start guide (README)
- [x] Website landing page
- [x] Implementation checklist (Appendix C)

---

## 🔗 Repository Structure (Skeleton Created)

```
hgss-evidence-agent-suite/
  README.md                    ✅
  LICENSE                      ✅
  VERSION                      ✅
  Makefile                     ✅
  
  spec/
    HGSS_EVIDENCE_AGENT_SUITE_SPEC.md    ✅ (normatif)
    AUDIT_EVIDENCE_SCHEMA.md             (referenced, frozen)
  
  agent/
    src/
      main.rs (or main.go)              [TODO]
      collector/                        [TODO]
      verifier/                         [TODO]
      trace/                            [TODO]
      storage/                          [TODO]
      policy/                           [TODO]
      crypto/                           [TODO]
    
    tests/
      fixtures/                         [TODO]
      integration_test.rs               [TODO]
    
    packaging/
      windows/                          [TODO]
      linux/                            [TODO]
      systemd/                          [TODO]
    
    Cargo.toml                          [TODO]
    Makefile                            [TODO]
  
  viewer/
    src/
      ui/                               [TODO]
      playback/                         [TODO]
      export/                           [TODO]
      auth/                             [TODO]
    
    Cargo.toml (or package.json)        [TODO]
    Makefile                            [TODO]
  
  tools/
    hgss_verify_evidence.py             [TODO]
    hgss_make_example_event.py          [TODO]
    audit_checklist.py                  [TODO]
  
  ci/
    build_windows.sh                    [TODO]
    build_linux.sh                      [TODO]
    test.sh                             [TODO]
```

---

## 🎯 Key Design Decisions (Frozen)

1. **Canonical CBOR (RFC 8949)**: All evidence stored in canonical format for byte-stable, reproducible hashing
2. **Locked Digests**: trace_sha256, trace_event_count, event_sha256 cannot be overridden
3. **Fail-Closed**: If verification fails → status FAIL/TRAP, evidence still stored for forensics
4. **Append-Only**: No delete/modify after write; WORM policy enforced
5. **Deterministic Lanes**: 28-lane timeline derived from ISA semantics (LDH_V18), not guesses
6. **Schema Frozen**: AUDIT_EVIDENCE_SCHEMA.md is normatif, no field additions without version bump

---

## 📞 Next Steps

### For Team Implementation
1. Choose language: **Rust** (recommended, memory-safe) or **Go** (simpler)
2. Choose UI framework: **Tauri** (lightweight) or **Electron** (more features)
3. Set up CI/CD with GitHub Actions
4. Implement agent service modules in dependency order (crypto → storage → collector → verifier)
5. Implement UI pages (login → list → detail → playback → lanes → print)
6. Add packaging (WiX for Windows, deb/rpm for Linux)
7. Test on fresh VMs (Windows 10+ , Ubuntu 20.04+, Fedora 35+)
8. Sign binaries (optional for production)
9. Publish releases on GitHub
10. Update website documentation

### For Deployment
1. Document operational procedures (service start/stop, log rotation, policy updates)
2. Create compliance audit bundle (schema + verifier + test vectors)
3. Publish security advisories process
4. Set up support channels (issues, email, documentation)

---

## 📊 Metrics & Goals

| Metric | Target | Notes |
|--------|--------|-------|
| Code coverage | >90% | Unit + integration tests |
| Documentation | 100% | Spec, README, inline comments |
| Installer testing | Windows + Ubuntu + Fedora | Fresh VM validation |
| Performance | <100ms per event collect | Acceptable for banking |
| Storage efficiency | <10KB per transaction | Index + metadata only |
| Audit log retention | Unlimited | Append-only, no rotation |

---

**Specification Frozen**: March 3, 2026  
**Ready for Implementation**: Yes ✅  
**Ready for Production Release**: Yes ✅ (after implementation + testing)

---

For questions or clarifications: [GitHub Issues](https://github.com/hijaiyyahmath/hgss-evidence-agent-suite/issues)
