# Arsitektur — dezz-osint

## Gambaran

`dezz-osint` adalah CLI Python pasif + server MCP (stdio) dalam satu
paket. Satu target masuk, mesin-mesin yang cocok jalan, hasilnya
ditampilkan sebagai teks yang bisa dibaca — JSON mentah tidak pernah
dicetak ke layar (kecuali arsip `Data/dezz_<target>.json`).

Diagram lengkap (SVG, tanpa Mermaid): `diagrams.html`.

## Lapisan

| Lapisan | Isi | Tugas |
|---|---|---|
| Antarmuka | `dezz/cli.py` (argparse + menu interaktif), `dezz.py` | Parse perintah, tampilkan banner + menu, bungkus engine dengan loading + durasi |
| Orkestrator | `dezz/orchestrator.py` | `dossier(target)`: tebak jenis target, jalankan semua engine yang cocok, simpan JSON |
| Mesin (engines) | `dezz/engines/*.py` | Logika per jenis target: phone, email, ip, domain, url, github, exif, media_dl, username |
| Adapter | `dezz/adapters/*.py` | Jembatan ke tool upstream: maigret, tookie, Photon, SpiderFoot, katalog awesome-osint, TorBot |
| MCP | `dezz/mcp/server.py`, `dezz/mcp/tools.py` | Server JSON-RPC 2.0 stdio (MCP 2024-11-05), 13 tool — tiap tool memanggil engine/adapter yang sama dengan CLI |
| Konfigurasi | `dezz/config.py`, `dezz/engines/config.py` | Path checkout upstream, `VERSION`, kunci opsional dari env/`.env` (tidak pernah hardcode) |
| Server pendamping | `server/main.py` | `dezz-extract`: backend yt-dlp pengganti Cobalt untuk DezDownload (`POST /` gaya Cobalt) — bukan bagian CLI |

## Alur satu perintah

```
pengguna ──▶ dezz <perintah> <target>
                │  (atau menu interaktif / MCP tools/call)
                ▼
           cli.cmd_* ──▶ engine/adapter ──▶ sumber publik pasif
                │            (ip-api, dns.google, crt.sh, api.github.com, …)
                ▼
           teks rapi per seksi (+ arsip JSON di Data/ untuk dossier)
```

## Prinsip kejujuran (dijaga di semua lapisan)

1. **Hanya mesin yang lolos live-test yang di-wire.** Modul yang
   terbukti mati dihapus dari tree (lihat `dezz/docs/SOURCES.md`).
2. **Kandidat ≠ konfirmasi.** Pencarian username cepat mengembalikan
   kandidat `[?]`; hanya data API (mis. GitHub) yang dicap
   `[verified]`.
3. **Gate yang jujur, bukan hasil palsu.** Butuh Tor service, kunci
   API, atau checkout upstream? CLI mencetak `SKIP` + cara
   memulihkannya — tidak pernah mengarang hasil.
4. **Pasif saja.** Tidak ada brute-force, tidak ada login paksa,
   tidak ada scraping halaman login. Target yang sah saja: data
   sendiri / atas izin.
5. **Rahasia tidak ke-commit.** Semua kunci lewat env/`.env`
   (lihat `.env.example`); `.gitignore` menutup `.env`, `Data/`,
   `reports/`, `*.egg-info/`.

## Mesin dan sumbernya

| Perintah | Engine/adapter | Sumber (pasif, tanpa kunci) |
|---|---|---|
| `phone` | `engines/phone_offline.py` + `Numbercheck.py` | `phonenumbers` (offline) + Google Custom Search (opsional, kunci) |
| `username` | `adapters/maigret_adapter.py`, `tookie_adapter.py` | Maigret (deep, subprocess), Tookie (262 situs), GitHub API (verifikasi) |
| `email` | `engines/email_ext.py` + `mcp/tools.py` | MX (DNS), Gravatar, Firefox Monitor, HudsonRock stealer log |
| `ip` | `engines/ipcheck.py` | ip-api.com (45 req/menit, tanpa kunci) |
| `domain` | `engines/domaincheck.py` | DNS-over-HTTPS (dns.google), crt.sh, RDAP |
| `url` | `engines/urlcheck.py` | Header HTTP + Wayback CDX |
| `crawl` | `adapters/photon_adapter.py` | Photon asli (bila checkout ada) atau crawler bawaan |
| `exif` | `engines/image_exif.py` | EXIF/GPS lokal (`pillow` + `piexif`) |
| `github` | `engines/githubcheck.py` | api.github.com (60 req/jam tanpa kunci) |
| `dl` | `engines/media_dl.py` | yt-dlp probe + download (1000+ situs) |
| `resources` | `adapters/resources_catalog.py` | `dezz/resources_catalog.json` — 3793 entri offline |
| `sf` | `adapters/spiderfoot_adapter.py` | `dezz/spiderfoot_modules.json` — 233 modul, perintah dijalankan manual |
| `tor` | `adapters/torbot_adapter.py` | Status layanan Tor lokal (gate jujur) |
| `dossier` / `run` | `orchestrator.py` | Semua yang cocok dengan jenis target |

## Keputusan yang sengaja TIDAK diambil

- **Tidak ada database.** Hasil dossier disimpan sebagai JSON/MD di
  `Data/` — cukup untuk tool personal, tanpa server yang harus dijaga.
- **Tidak ada server web untuk CLI.** Etalase web (`index.html`) adalah
  halaman statis; produknya tetap CLI + MCP.
- **Tidak ada kunci bawaan.** Semua sumber inti bekerja tanpa kunci;
  kunci opsional hanya menaikkan limit (GitHub) atau membuka sumber
  tambahan (Google Custom Search).
