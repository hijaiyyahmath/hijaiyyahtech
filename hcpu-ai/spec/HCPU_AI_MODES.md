# HCPU-AI Operational Modes

HCPU-AI mendukung tiga mode kepatuhan (conformance modes) yang menentukan tingkat efek samping dan verifikasi:

## 1. CORE Mode
- **Deskripsi**: Mode eksekusi murni dan audit.
- **Efek Samping**: Tidak ada (pure).
- **Verifikasi**: Hanya menjalankan instruksi HISA (LOAD, ADD, AUDIT, MOD) dan memvalidasi gerbang audit.

## 2. FEEDBACK Mode
- **Deskripsi**: CORE + Injeksi statistik validator.
- **Efek Samping**: Pencatatan metadata validasi ke log feedback.
- **Verifikasi**: Digunakan untuk mengumpulkan metrik performa AI terhadap norma codex.

## 3. OWNER Mode
- **Deskripsi**: FEEDBACK + Pembelajaran kepemilikan (Owner Learning).
- **Efek Samping**: Update model pengenal pemilik secara offline (offline owner recognizer).
- **Verifikasi**: Mode paling ketat untuk personalisasi stack secara deterministik.
