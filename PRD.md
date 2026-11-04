# PRD — Dezz Osint

## 1. Informasi Proyek

| Field | Nilai |
|---|---|
| Nama Proyek | Dezz Osint |
| Repo | dezzorigin/dezz-osint |
| Tech Stack | Python |
| Status | Selesai (production-ready) |
| Penanggung Jawab | Nabil Aulia Dika |
| Versi Dokumen | 1.0 |
| Tanggal | 2026 |

## 2. Latar Belakang

Proyek ini dikembangkan sebagai bagian dari portofolio dan kebutuhan operasional. Dokumen ini mengikuti standar PRD nasional untuk memastikan ruang lingkup, fitur, dan kriteria keberhasilan terdefinisi dengan jelas.

## 3. Masalah yang Diselesaikan

Pengguna membutuhkan solusi digital yang efisien, terukur, dan mudah dipelihara untuk kebutuhan yang ditangani oleh proyek ini.

## 4. Tujuan & Sasaran

- Menyediakan fungsionalitas inti secara andal.
- Menjaga kualitas kode dan dokumentasi.
- Memudahkan onboarding kontributor baru.

## 5. Ruang Lingkup

### In Scope
- Fitur inti aplikasi sesuai struktur repo.
- Setup & konfigurasi pengembangan lokal.
- Dokumentasi (README + PRD).

### Out of Scope
- Infrastruktur production (kecuali disebutkan).
- Integrasi pihak ketiga yang belum dikonfigurasi.

## 6. Fitur & Persyaratan Fungsional

Struktur proyek (file/direktori utama):
- .env
- .env.example
- .gitignore
- Data/
- LICENSE
- README.md
- assets/
- dezz.py
- dezz/
- dezz_osint.egg-info/
- install.sh
- mcp.json
- pyproject.toml
- reports/
- requirements.txt
- server/
- skills/
- tests/

## 7. Persyaratan Non-Fungsional

- **Performa:** responsif untuk penggunaan normal.
- **Keamanan:** rahasia (`.env`) tidak boleh ter-commit; gunakan `.env.example`.
- **Maintainability:** kode terstruktur, terdokumentasi.
- **Portabilitas:** dapat dijalankan di Linux/macOS/Windows (sesuai stack).

## 8. Arsitektur & Tech Stack

Python

## 9. Milestone / Roadmap

| Fase | Status |
|---|---|
| Inisialisasi & scaffolding | ✅ |
| Pengembangan fitur inti | 🔄 |
| Testing & QA | ⏳ |
| Deployment | ⏳ |
| Dokumentasi | ✅ (README + PRD) |

## 10. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Konfigurasi env bocor | `.gitignore` + `.env.example` |
| Dependency usang | Audit berkala (`npm audit` / `pip list --outdated`) |
| Build artifact besar | Tambahkan ke `.gitignore` |

## 11. Kriteria Keberhasilan

- Aplikasi berjalan tanpa error di lingkungan dev.
- README & PRD lengkap dan up-to-date.
- Tidak ada secret yang ter-commit.

## 12. Lampiran

- Struktur: lihat README.md
- Lisensi: MIT (LICENSE)
