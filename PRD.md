# PRD — dezz-osint

## 1. Informasi Proyek

| Field | Nilai |
|---|---|
| Nama Proyek | dezz-osint |
| Tech Stack | Python ≥3.10 (CLI + MCP stdio) |
| Status | Proper — v0.2.0 + rilis `v1.0-proper` (rantai P1 repo #44) |
| Penanggung Jawab | Nabil Aulia Dika (dezzorigin) |
| Versi Dokumen | 2.0 (ditulis ulang dari audit kode, 19 Nov 2026) |
| Tanggal | 2026-11-19 |

## 2. Latar Belakang

Investigasi OSINT sehari-hari terpecah ke banyak tool sekali pakai:
cek nomor di satu tempat, cek username di tempat lain, cek breach
di tempat ketiga — tiap tool punya format output dan tingkat
kejujuran berbeda. dezz-osint menyatukan yang sudah terbukti jalan
ke satu CLI + satu server MCP, dengan satu aturan: hasil yang tidak
terverifikasi dilabeli kandidat, yang butuh syarat dilabeli SKIP —
tidak ada yang pura-pura.

## 3. Masalah yang Diselesaikan

- Satu target, banyak pertanyaan — jawab sekaligus lewat `dossier`.
- Hasil tool OSINT sering dibaca sebagai fakta padahal hanya
  kandidat — CLI ini memisahkan `[verified]` / `[?]` / `[SKIP]`
  secara eksplisit.
- Agen AI (Claude Desktop, opencode) butuh OSINT tanpa keluar dari
  percakapan — server MCP 13 tool memakai engine yang sama dengan CLI.

## 4. Tujuan & Sasaran

- 14 perintah CLI bekerja dari satu biner `dezz` (menu interaktif
  bila tanpa argumen).
- 13 tool MCP menjawab `tools/list` + `tools/call` lewat stdio.
- Semua mesin inti jalan tanpa kunci API; kunci opsional hanya
  menaikkan limit / membuka sumber tambahan.
- Katalog 3793 tool OSINT bisa dicari offline; 233 modul SpiderFoot
  bisa dirancang pemindaiannya.
- Landing statis menjelaskan tool + perintah + output asli.

## 5. Ruang Lingkup

### In Scope
- CLI: phone, username (fast/maigret/tookie), email, ip, domain,
  url, crawl, exif, github, dl, resources, sf, tor, dossier/run, mcp.
- MCP server stdio (13 tool, protokol 2024-11-05).
- Katalog resources offline + katalog modul SpiderFoot.
- Server pendamping `server/` (dezz-extract, pengganti Cobalt).
- Docs lengkap + landing etalase + CI + rilis GitHub Releases.

### Out of Scope
- Pelacakan real-time, brute-force, login paksa, doxxing.
- Menjalankan SpiderFoot / Tor di dalam CLI (hanya dirancang /
  dicek statusnya — dijalankan manual / layanan terpisah).
- Backend web untuk CLI (landing hanya etalase statis).
- Menyimpan hasil di database (arsip JSON/MD di `Data/` sudah cukup).

## 6. Fitur & Persyaratan Fungsional

| # | Fitur | Kriteria terima |
|---|---|---|
| 1 | `phone` offline | Nomor +62 valid → operator/daerah/E164/wa.me; tanpa jaringan |
| 2 | `username` 3 engine | fast = kandidat + GitHub terverifikasi; maigret = deep; tookie = 262 situs |
| 3 | `email` breach | MX + Gravatar + Firefox + HudsonRock; BOCOR → anjuran ganti password |
| 4 | `ip` geo | `8.8.8.8` → United States (ip-api, tanpa kunci) |
| 5 | `domain` | A via DoH + subdomain crt.sh + RDAP |
| 6 | `url` | status + server + judul + arsip Wayback |
| 7 | `crawl` | Photon asli bila checkout ada, fallback bawaan bila tidak — keduanya nyata |
| 8 | `exif` | GPS foto → lat/lon desimal (contoh uji: −6.2) |
| 9 | `github` | `torvalds` → exists, followers, repo |
| 10 | `dl` | probe (judul/durasi) tanpa download; `--audio`/`--video` mengunduh |
| 11 | `resources` | `sherlock` ketemu dari 3793 entri offline |
| 12 | `sf` | `--search dns` ketemu modul; `build_scan_cmd` hanya modul yang ada |
| 13 | `tor` | tanpa Tor: `tor_binary: false, runnable: false` (jujur) |
| 14 | `dossier` | tebak jenis target, jalankan yang cocok, arsip JSON di `Data/` |
| 15 | MCP 13 tool | `tools/list` = 13; `ip_lookup 8.8.8.8` → United States |
| 16 | Menu interaktif | tanpa argumen → menu bernomor; hasil >30 baris ditawari simpan `.md` |

## 7. Persyaratan Non-Fungsional

- **Performa:** perintah pasif inti <15 dtk (timeout request 12 dtk);
  `maigret`/`tookie`/`crawl` boleh bermenit-menit (diperingatkan dulu).
- **Keamanan:** rahasia (`.env`) tidak boleh ter-commit; gunakan
  `.env.example`. Target sah saja (lihat §11).
- **Kejujuran:** kandidat `[?]`, terverifikasi `[verified]`, gate
  `[SKIP]` — tidak ada hasil palsu di lapisan mana pun.
- **Maintainability:** engine per file, adapter per upstream, verdict
  upstream tercatat di `dezz/docs/SOURCES.md`.
- **Portabilitas:** Linux/macOS/Windows, Python ≥3.10.

## 8. Arsitektur & Tech Stack

Python + `rich` (tampilan), `requests`/`beautifulsoup4` (HTTP),
`phonenumbers` (offline), `maigret` + `yt-dlp` + `selenium`
(adapter berat), `pillow`/`piexif` (EXIF), `python-dotenv` (kunci
opsional). Detail: `docs/ARCHITECTURE.md`, diagram:
`docs/diagrams.html`.

## 9. Milestone / Roadmap

| Fase | Status |
|---|---|
| Inisialisasi & mesin inti (live-test) | ✅ |
| MCP server 13 tool | ✅ |
| Katalog resources 3793 + SpiderFoot 233 | ✅ |
| Server pendamping dezz-extract | ✅ |
| Proper P1 #44: docs + CI + landing + rilis | ✅ (19 Nov 2026) |
| Screenshot README + rekaman terminal | ⏳ follow-up (butuh browser live) |

## 10. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Sumber gratis berubah/mati (ip-api, crt.sh, Cobalt) | Verdict di `SOURCES.md`; fallback bawaan (Photon); dezz-extract ganti Cobalt |
| Kandidat username dibaca sebagai fakta | Label `[?]` di semua output + docs |
| Hasil breach disalahgunakan | Anjuran ganti password; tool tidak mengembalikan password |
| Kunci bocor ke repo | `.env.example` + `.gitignore` (`.env`, `Data/`, `reports/`) |
| Dependency usang | Pin `==` di `requirements.txt` + OSV sweep di CI (HIGH/CRITICAL = gagal) |

## 11. Etika — target yang sah saja

Tool ini pasif dan hanya untuk target yang sah: data sendiri atau
atas izin eksplisit (cek nomor penipu, cek kebocoran email sendiri,
recon domain sendiri). Dilarang untuk doxxing, stalking,
pelecehan, atau pelacakan real-time. Lihat `skills/dezz-osint/SKILL.md`
(guardrails agen).

## 12. Kriteria Keberhasilan

- `pytest tests/test_cli.py` hijau di CI (perilaku live, tanpa mock).
- `dezz ip 8.8.8.8` → United States; `dezz github torvalds` → exists.
- MCP `tools/list` = 13 tool.
- Landing live di Pages + semua tag OG/Twitter + og-image 200 `image/*`.
- Rilis `v1.0-proper` di GitHub Releases.
- Tidak ada secret yang ter-commit.

## 13. Lampiran

- Struktur: lihat README.md
- Arsitektur: `docs/ARCHITECTURE.md` + `docs/diagrams.html`
- Cara pakai: `docs/USAGE.md`
- Testing: `docs/TESTING.md`
- Deploy/rilis: `docs/DEPLOY.md`
- Desain landing: `docs/DESIGN.md`
- Lisensi: MIT (LICENSE)
