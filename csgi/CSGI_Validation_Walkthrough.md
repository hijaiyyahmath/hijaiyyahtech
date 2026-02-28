# CSGI Validation Wiring Walkthrough (HL‑18 Release)

## 1) Overview
Dokumen ini mendokumentasikan integrasi Character Skeleton Graph Interface (CSGI) ke dalam pipeline verifikasi rilis HL‑18‑v1.0. Tujuannya adalah menjadikan CSGI sebagai artefak rilis yang:
- **Hash‑locked**: integritas file dijamin melalui SHA‑256 (sesuai spec rilis).
- **Semantically validated**: konsistensi struktur graf diverifikasi dengan PASS/FAIL deterministik.

## 2) Accomplishments
### 2.1 Saved CSGI Fixtures
Fixture orisinal untuk audit visual dan pengembangan tool:
- `CSGI_fa.json`
- `CSGI_waw.json`
- `CSGI_jim.json` (extracted from SVG)

### 2.2 Verifier Patch (Audit‑Grade): `verify_hl18_release.py`
Hardening pada mesin validasi mencakup:

**A) Version Locking**
- Root dataset wajib `CSGI-DATASET-1.0`.
- Entri per huruf wajib `CSGI-1.0`.

**B) Strict JSON Parsing**
- Menolak duplicate keys.
- Menolak NFC key collisions.
- Menolak non‑string keys.

**C) Letter‑ID Normalization**
- Identitas audit ditentukan oleh:
  $$letter\_id(s) = NFC(s) \text{ lalu hapus seluruh } U+0640 \text{ (Tatweel)}$$
- Completeness check 28/28 dilakukan atas `letter_id`, bukan string mentah.

**D) Mandatory Metadata**
- Wajib `meta.adjacency == "8-neighborhood"` pada setiap entry.

**E) Structural Consistency**
- Koordinat node x/y wajib bertipe `int`.
- **Edge Endpoint Lock**: `points[0]` dan `points[-1]` harus sinkron dengan koordinat node `u` dan `v`.
- **Degree Consistency**: `node.degree` harus sama dengan derajat graf standar yang dihitung dari incident edges `(u,v)`. Edge dengan `u==v` (self‑loop) berkontribusi 2 pada degree.
- **Proximity Check**: langkah polyline wajib memenuhi kriteria 8‑neighborhood.

**F) Completeness**
- Dataset harus memuat tepat 28 huruf Hijaiyyah utama (set normatif) setelah normalisasi `letter_id`.

### 2.3 Spec Update: `HL18_release_integrity.yaml`
Pendaftaran dataset CSGI ke dalam spek integritas:
```yaml
csgi_dataset:
  path: ../CSGI-28-v1.0.json
  sha256: "530845fbc3815ea9f02c75d44bda0e1aa096ec93729942d24d2d8bb0bd56c9d5"
```

### 2.4 Full Dataset Generation
`CSGI-28-v1.0.json`: kumpulan 28 entri tervalidasi dan terkunci (hash‑locked).

## 3) HL API Test Results
HL API Module: `hb.py` — Hilbert Basis loader (JSON + binary codec) dengan monoid membership testing.

### 3.1 Witness Hole Test (integrally_closed = false)
`test_witness_hole.py` — PASS
- 38 HB elements, 28 letter vectors → 10 extra vectors teridentifikasi.
- Minimal 1 witness hole terkonfirmasi (tidak dapat didekomposisi menjadi jumlah vektor huruf).
- Kesimpulan: `integrally_closed = false` (evidence‑based).

### 3.2 HB18.bin ↔ HB18.json Semantic Roundtrip
`test_hb_binary_json.py` — PASS
- Dimensi (18) dan ukuran (38) cocok.
- Round‑trip codec integrity terverifikasi (JSON→bin→JSON dan bin→bin).
> **NOTE**
> Jika terdapat perbedaan urutan/permute kolom internal, itu dicatat sebagai perbedaan representasi, bukan perbedaan isi matematis (dimensi & himpunan vektor tetap konsisten sesuai pemeriksaan test).

### 3.3 Regression & Fuzzing
`test_hl_regression.py` — PASS (26 tests, 28 subtests)
- 28/28 letters lulus `audit_v18`.
- Additive closure, boundary cases, determinisme, dan 200‑round random fuzzing terverifikasi.

## 4) Hijaiyah Virtual Machine (HVM)
Architecture: Pure Stack VM with Conformance Modes

| Mode | Opcodes | Purpose |
|------|---------|---------|
| HVM‑CORE | LOAD, ADD, AUDIT, MOD, HALT | Normative, audit‑grade |
| HVM‑FEEDBACK | + VALIDATE | Side‑effect: validator stats |
| HVM‑OWNER | + VALIDATE + LEARN | Side‑effect: owner model |

Modules:

| Module | File | Function |
|--------|------|----------|
| IR Compiler | `ir.py` | HL word → IR instructions + portable bytecode |
| HCPU Engine | `hcpu.py` | Fetch‑decode‑execute + forensic trace |
| Validator Loop | `validator_loop.py` | Error taxonomy + feedback stats |
| Owner Recognizer | `owner_learn.py` | Bigram frequency model |

Test Results: `test_hvm.py` — 36 passed, 56 subtests
- IR compile/serialize/roundtrip, invalid letter rejection
- HCPU `run() == cod_word()` untuk semua 28 huruf
- AUDIT non‑destructive, MOD range checks
- Conformance mode opcode restrictions enforced
- Validator taxonomy verified: INVALID_DIM, NEGATIVE_COMPONENT, DERIVED_MISMATCH
- Owner model observe→recognize, save/load roundtrip, confidence increase
- Full pipeline: word → compile → execute → validate → learn untuk semua 28 huruf

## 5) Verification Results
### 5.1 Perintah auditor
```bash
# Release integrity
python verify_hl18_release.py --spec hl-release-HL-18-v1.0/HL18_release_integrity.yaml

# Feature formulas
python verify_mh28_formulas.py MH-28-v1.0-18D.csv

# MainPath regression
python csgi_mainpath_select.py CSGI_T_competitive.json
python csgi_mainpath_select.py CSGI_cycle_tails_competitive.json

# Full test suite (62 tests, 84 subtests)
cd hijaiyahlang-hl18 && python -m pytest tests/ -v
```

### 5.2 Hasil
| Command | Status |
|---------|--------|
| `verify_hl18_release.py` | PASS (csgi_dataset.sha256 + validate) |
| `verify_mh28_formulas.py MH-28-v1.0-18D.csv` | PASS (AN/AK/AQ/U/ρ verified) |
| `csgi_mainpath_select.py` (T‑comp) | PASS (Winner: 1‑2‑5‑4‑3‑7) |
| `csgi_mainpath_select.py` (Cycle) | PASS (Winner: 1‑2‑3‑5‑6) |
| `pytest tests/ -v` | 62 passed, 84 subtests |

## 6) Heh‑Tatweel Audit Case (Resolved)
- Raw letter: "هـ" (U+0647 + U+0640)
- Audit identity: `letter_id("هـ") == "ه"` (U+0647)
- Status: PASS (membership menggunakan `letter_id` normatif)

## 7) Normative Hijaiyyah Set (after `letter_id`)
ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن و ه ي
(varian visual seperti "هـ" diselesaikan menjadi "ه" secara otomatis).

## 8) MainPath Selection (Release‑Grade)
Tool: `csgi_mainpath_select.py`

Seleksi pemenang berdasarkan skor leksikografis (flattened):
$$S(P) = (Len(P), -Junc(P), Closed(P), Cov(P))$$
dengan tie‑breaking via EmbKey.

Regression tests:
| Test | Status | Winner |
|------|--------|--------|
| T‑Junction | PASS | 1‑2‑5‑4‑3‑7 |
| Cycle+Tails | PASS | 1‑2‑3‑5‑6 |

> **NOTE (Topological)**
> Loop tidak memaksa MainPath tertutup karena seleksi leksikografis memilih path dominan (Len‑first). Uji mod‑4 digunakan sebagai sanity check:
> $$closed \Rightarrow \hat{\Theta} \equiv 0 \pmod 4.$$
> Mod‑4 adalah syarat perlu untuk closed, bukan penentu tunggal.

## 9) Feature Formula Verification (MH‑28‑18D): PASS
Script: `verify_mh28_formulas.py`
Validasi konsistensi internal terhadap `MH-28-v1.0-18D.csv`:

| Formula | Definition | Reference (HL‑18) |
|---------|------------|-------------------|
| AN | $n_t + n_f + n_m$ | Total nuqṭah |
| AK | $k_m + k_t + k_d + k_a + k_z$ | Total khaṭṭ |
| AQ | $q_a + q_t + q_d + q_s + q_z$ | Total qaws |
| U | $q_t + 4q_d + q_s + q_z + 2k_z$ | Budget turning non‑primer (Bab I.9) |
| ρ | $\hat{\Theta} - U$ | Residu turning primer (Bab I.9) |

## 10) Original Jim CSGI Extraction
Ekstraksi orisinal dari `Arabic_letter_Jeem.svg` menggunakan `extract_csgi_jim.py`.
- **Struktur**: berhasil menguraikan 73 nodes dan polylines terkait.
- **Densifikasi**: polyline hasil ekstraksi SVG dinormalisasi menjadi representasi grid dengan langkah unit (densified 8‑neighborhood) sebelum validasi.
- **Validasi**: PASS (konsistensi degree dan topologi terverifikasi).

## 11) Core Implementation Snippets (Audit Reference)
Letter identity normalization:
```python
def letter_id(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return s.replace("\u0640", "")
```

Strict JSON loader:
```python
def load_json_no_dups_nfc_keys(path: str) -> Any:
    def hook(pairs):
        obj = {}
        for k, v in pairs:
            if not isinstance(k, str):
                raise ValueError("NON_STRING_KEY")
            k2 = unicodedata.normalize("NFC", k)
            if k2 in obj:
                raise ValueError(f"DUPLICATE_KEY_OR_NFC_COLLISION: {k!r}")
            obj[k2] = v
        return obj
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=hook)
```

Root version lock (robust):
```python
ver = root.get("csgi_dataset_version") or root.get("csgi_version")
if ver != "CSGI-DATASET-1.0":
    raise ValueError(f"Invalid CSGI dataset version: {ver!r}")
```
