# CMM-18C Repository Walkthrough

Inisialisasi repository **CMM-18C v1.0** telah selesai. Repository ini berfungsi sebagai spesifikasi normatif dan model referensi untuk *Hardware Compliance Machine* yang mendasari eksekusi Hijaiyyahlang (HL-18).

## 1. Accomplishments

### 1.1 Normative Specifications (`spec/`)
Daftar dokumen hukum mesin yang telah dikunci:
- [CMM18C_v1_0.md](file:///c:/hijaiyyah-codex/cmm18c/spec/CMM18C_v1_0.md): Model mesin, register, dan relasi audit ($\hat{\Theta}, \rho, U, mod4$).
- [ISA_TABLE.md](file:///c:/hijaiyyah-codex/cmm18c/spec/ISA_TABLE.md): Definisi instruksi `SETFLAG`, `LDV`, dan `AUDIT`.
- [BYTECODE_ENCODING.md](file:///c:/hijaiyyah-codex/cmm18c/spec/BYTECODE_ENCODING.md): Format biner 32-bit untuk setiap instruksi.
- [TRAP_CONFORMANCE.md](file:///c:/hijaiyyah-codex/cmm18c/spec/TRAP_CONFORMANCE.md): Aturan *CORE-1* (SETFLAG $\to$ AUDIT adjacency) dan daftar kode error (TRAP 1-10).
- [LLVM_ABI_POINTER.md](file:///c:/hijaiyyah-codex/cmm18c/spec/LLVM_ABI_POINTER.md): Aturan alignment 16-byte untuk pointer `v18` paling lancar.

### 1.2 C Integration (`include/` & `examples/`)
- [cmm18c_types.h](file:///c:/hijaiyyah-codex/cmm18c/include/cmm18c_types.h): Definisi `uint32_t[18]` dengan `alignas(16)`.
- [audit_ptr_example.c](file:///c:/hijaiyyah-codex/cmm18c/examples/audit_ptr_example.c): Contoh pemanggilan intrinsic.

## 2. Audit Verification (Runnable)

Jalankan perintah berikut untuk memverifikasi integritas dan logika model:

### 2.1 Unit Tests (Regression)
```bash
cd c:/hijaiyyah-codex/cmm18c
$env:PYTHONPATH="src;tests"
python -m pytest -q
```
**Hasil yang diharapkan (8 Tests Passed):**
```text
........                                                                 [100%]
8 passed in 0.12s
```

| Test File | Status | Description |
|-----------|--------|-------------|
| `test_setflag_encoding.py` | PASS | Validasi biner SETFLAG & illegal flag trap |
| `test_core1_setflag_required.py` | PASS | Verifikasi trap AUDIT tanpa SETFLAG |
| `test_trap_audit_mod4.py` | PASS | Verifikasi trap $\hat{\Theta} \pmod 4$ |
| `test_trap_misaligned_ptr.py` | PASS | Verifikasi trap pointer (ERR=10) |
| `test_vortex_channel.py` | PASS | Verifikasi bit-energy channel VC-1 (JIM Vortex) |

### 2.2 CLI Tools (Entrypoints)
```bash
python tools/run_vm.py --help
python tools/disasm.py --help
```

## 3. Data & Integrity Lock

### 3.1 Hard-locked Data (SHA-256)
Audit integritas dataset HL-18 di folder `data/`:
- `MH-28-v1.0-18D.csv`: `7393659dfe979cf85b1cf6293179f7ba1f49b4eedd1af19f002170148ce00380`
- `CSGI-28-v1.0.json`: `530845fbc3815ea9f02c75d44bda0e1aa096ec93729942d24d2d8bb0bd56c9d5`

### 3.2 Repository State
- **Git Hash**: `0f10d98`
- **Git Tag**: `CMM-18C-v1.0` (HISA v1.0 Aligned)
