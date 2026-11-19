# dezz-osint

**CLI OSINT pasif + server MCP — 14 perintah, 13 tool MCP, 0 kunci wajib.**
Satu target masuk (nomor, username, email, IP, domain, URL, foto),
mesin-mesin yang cocok jalan, hasilnya dicap jujur: `[verified]`
hanya dari API, `[?]` = kandidat yang harus dicek manual, `[SKIP]` =
butuh kunci/layanan — tidak pernah mengarang hasil.

> Etalase web: **https://dezz-osint.pages.dev** — perintah, contoh
> output asli, dan cara install. Produknya tetap CLI + MCP yang jalan
> di terminal, bukan web app.

## Status

Proper (rantai P1 repo #44): README + docs lengkap, CI hijau
(ruff + pytest + OSV sweep + e2e), rilis GitHub Releases
`v1.0-proper`, landing live di Cloudflare Pages.

## Perintah

| Perintah | Yang dilakukan | Sumber (pasif) |
|---|---|---|
| `dezz phone +62812…` | intel nomor HP: operator, daerah, E164, wa.me | `phonenumbers` (offline) |
| `dezz username X` | jejak username — cepat / `--engine maigret` / `--engine tookie` | GitHub API, Maigret, Tookie (262 situs) |
| `dezz email a@b.com` | MX + Gravatar + Firefox + HudsonRock breach | DNS, Firefox Monitor, HudsonRock |
| `dezz ip 8.8.8.8` | geolokasi + ISP | ip-api.com (tanpa kunci) |
| `dezz domain example.com` | DNS-over-HTTPS + subdomain crt.sh + RDAP | dns.google, crt.sh |
| `dezz url https://…` | header + judul + arsip Wayback | HTTP, Wayback CDX |
| `dezz crawl https://…` | sedot isi website | Photon asli / crawler bawaan |
| `dezz exif foto.jpg` | metadata + GPS foto | EXIF lokal |
| `dezz github user` | profil + repo teratas | api.github.com |
| `dezz dl <link>` | info/download video-audio (1000+ situs) | yt-dlp |
| `dezz resources "kata"` | cari dari katalog 3793 tool OSINT (offline) | `resources_catalog.json` |
| `dezz sf --search dns` | rancang pemindaian dari 233 modul SpiderFoot | `spiderfoot_modules.json` |
| `dezz tor` | status layanan Tor (gate jujur) | Tor lokal |
| `dezz dossier <target>` | kupas tuntas: semua mesin yang cocok + arsip JSON | semua di atas |

Jalankan tanpa argumen (`dezz`) untuk menu interaktif bernomor.

## Contoh output asli (terverifikasi 19 Nov 2026)

```bash
$ dezz ip 8.8.8.8
IP: 8.8.8.8
lokasi: Ashburn, Virginia, United States
koordinat: 39.03, -77.5
ISP: Google LLC
organisasi: Google Public DNS
```

```bash
$ dezz github torvalds
Linus Torvalds
332412 followers · 12 repo
lokasi: Portland, OR
https://github.com/torvalds
```

Angka followers/repo adalah angka live saat dicek — berubah
seiring waktu.

```bash
$ dezz resources "sherlock"
# → Sherlock (github.com/sherlock-project/sherlock), SherlockEye, …
#    dari katalog offline 3793 entri

$ dezz sf --search dns
# → sfp_dnsresolve, sfp_adguard_dns, … dari 233 modul SpiderFoot
```

## Install

```bash
git clone https://github.com/dezzorigin/dezz-osint.git
cd dezz-osint
python3 -m venv .venv && source .venv/bin/activate
pip install .
dezz phone +6281234567890
```

Atau satu perintah:

```bash
curl -sSL https://raw.githubusercontent.com/dezzorigin/dezz-osint/main/install.sh | bash
```

Install memakan waktu beberapa menit — `maigret` + `selenium`
itu berat. Kunci opsional (semua perintah inti jalan tanpanya):

```bash
cp .env.example .env   # isi yang perlu saja
```

Butuh Python ≥3.10.

## MCP — 13 tool

Server stdio JSON-RPC 2.0 (MCP 2024-11-05). `mcp.json` di root
(ganti `cwd` ke path repo kamu):

```json
{
  "mcpServers": {
    "dezz-osint": {
      "command": "python",
      "args": ["-m", "dezz.mcp.server"],
      "cwd": "/path/to/dezz-osint",
      "env": {}
    }
  }
}
```

Tool: `phone_lookup`, `username_search`, `email_recon`,
`ip_lookup`, `domain_recon`, `github_lookup`, `url_recon`,
`osint_resources`, `spiderfoot_plan`, `full_dossier`, `web_crawl`,
`image_exif`, `media_download`. Cek cepat:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  | python -m dezz.mcp.server
```

## Aturan pakai (non-negotiable)

- **Target yang sah saja**: data sendiri atau atas izin eksplisit
  (cek nomor penipu, cek kebocoran email sendiri).
- **Pasif saja**: tidak ada brute-force, login paksa, atau pelacakan
  real-time.
- **Kandidat bukan fakta**: `[?]` berarti belum terverifikasi.
- **Breach = ganti password**: tool ini tidak pernah mengembalikan
  password — kalau ada yang meminta, tolak.

## Struktur

```
dezz/
  cli.py            # argparse + menu interaktif + banner
  orchestrator.py   # dossier(): tebak jenis target, jalankan yang cocok
  config.py         # VERSION, path checkout upstream
  engines/          # phone, email, ip, domain, url, github, exif, dl, …
  adapters/         # maigret, tookie, photon, spiderfoot, katalog, torbot
  mcp/              # server.py + tools.py (13 tool)
  docs/SOURCES.md   # verdict live-test tiap upstream
server/             # dezz-extract: backend yt-dlp pengganti Cobalt (terpisah)
skills/dezz-osint/  # SKILL.md — cara agen memakai tool ini
docs/               # PRD → arsitektur → cara pakai → testing → deploy
tests/              # pytest (perilaku live, tanpa mock) + smoke.py lama
```

## Docs

- `docs/DESIGN.md` — kontrak arah desain landing (referensi, palet, gate 7 sumbu)
- `docs/ARCHITECTURE.md` — lapisan + alur + prinsip kejujuran
- `docs/USAGE.md` — semua perintah + contoh + MCP + server pendamping
- `docs/TESTING.md` — apa yang diuji + cara menjalankan
- `docs/DEPLOY.md` — Pages (landing) + GitHub Releases (CLI)
- `docs/diagrams.html` — diagram SVG arsitektur + alur dossier
- `dezz/docs/SOURCES.md` — verdict live-test tiap repo upstream

## Testing

```bash
pip install -r requirements.txt
pip install pytest
python3 -m pytest tests/test_cli.py -q
```

CI (`.github/workflows/ci.yml`): ruff + pytest + static-checks
(html-validate + gate P0) + advisory-sweep (OSV) + Playwright e2e
landing + smoke file deploy.

## Lisensi

MIT — lihat [LICENSE](./LICENSE).

---
_Dikembangkan oleh **dezzorigin** (Nabil Aulia Dika)._
