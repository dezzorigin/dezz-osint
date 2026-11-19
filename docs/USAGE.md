# Cara Pakai — dezz-osint

## Install

```bash
git clone https://github.com/dezzorigin/dezz-osint.git
cd dezz-osint
python3 -m venv .venv && source .venv/bin/activate
pip install .
```

Atau satu perintah (clone + venv + install + symlink `dezz`):

```bash
curl -sSL https://raw.githubusercontent.com/dezzorigin/dezz-osint/main/install.sh | bash
```

Catatan jujur: install memakan waktu beberapa menit — `maigret` +
`selenium` itu berat. Tanpa keduanya pun sebagian perintah tetap
jalan (phone offline, resources, sf, exif), tapi `username --engine
maigret` dan `crawl` butuh checkout-nya masing-masing.

Kunci opsional (semua perintah inti jalan tanpanya):

```bash
cp .env.example .env   # lalu isi yang perlu saja
```

Lihat `.env.example` untuk daftar lengkapnya.

## Menu interaktif

```bash
dezz
```

Menu bernomor: `run` (kupas tuntas), `phone`, `username`, `email`,
`ip`, `domain`, `url`, `crawl`, `dl`, `exif`, `github`, `resources`,
`sf`, `tor`. Hasil panjang (>30 baris) ditawari tampil di layar
atau simpan `.md` ke `Data/`.

## Perintah

### `dezz phone +6281234567890` — intel nomor HP (offline)

```text
Nomor: +62 812-3456-7890
operator: Telkomsel · daerah: Indonesia
E164: +6281234567890
wa.me/6281234567890 · t.me/+6281234567890
```

Tidak butuh jaringan, tidak butuh kunci. Google Custom Search
(`GOOGLE_API_KEY` + `GOOGLE_CX`) menambahkan pencarian web bila
kunci tersedia — tanpanya, CLI mencetak `SKIP` yang jujur.

### `dezz ip 8.8.8.8` — geolokasi IP (terverifikasi 19 Nov 2026)

```text
IP: 8.8.8.8
lokasi: Ashburn, Virginia, United States
koordinat: 39.03, -77.5
ISP: Google LLC
organisasi: Google Public DNS
```

Sumber: ip-api.com, tanpa kunci, 45 req/menit.

### `dezz github torvalds` — profil GitHub (terverifikasi 19 Nov 2026)

```text
Linus Torvalds
332412 followers · 12 repo
lokasi: Portland, OR
https://github.com/torvalds
```

Angka followers/repo adalah angka live saat dicek — berubah
seiring waktu. Sumber: api.github.com (60 req/jam tanpa kunci,
5000 req/jam dengan `GITHUB_TOKEN`).

### `dezz username torvalds` — jejak username

```bash
dezz username torvalds                  # cepat: kandidat + GitHub terverifikasi
dezz username torvalds --engine maigret # dalam: scan Maigret asli (menit)
dezz username torvalds --engine tookie  # lebar: 262 situs via Tookie
```

Hasil cepat jujur dilabeli: `[verified]` hanya untuk yang
terkonfirmasi API, sisanya `[?]` = kandidat, konfirmasi manual.
Untuk `torvalds`, Tookie menemukan 39 hit (terverifikasi saat
pengembangan).

### `dezz email nama@example.com` — cek kebocoran email

```text
Email: nama@example.com
format: ok
server mail: <MX pertama>
Gravatar: terdaftar / —
Firefox: terdaftar / tidak terdaftar
breach: BERSIH / BOCOR — ganti password!
```

Sumber: MX (DNS), Gravatar, Firefox Monitor, HudsonRock stealer
log. Kalau `breach: BOCOR`, ganti password — tool ini tidak pernah
mengembalikan password.

### `dezz domain example.com` — recon domain

DNS-over-HTTPS (dns.google) untuk A/MX/TXT/NS, crt.sh untuk
subdomain dari Certificate Transparency, RDAP untuk registrar.
Contoh nyata (19 Nov 2026): `example.com` → A `104.20.23.154`,
`172.66.147.243`.

### `dezz url https://example.com/artikel` — cek link

Header HTTP + judul + arsip Wayback (CDX).

### `dezz crawl https://example.com` — sedot isi website

Photon asli bila checkout Photon ada di sebelah repo, kalau tidak
crawler bawaan (`dezz-builtin`) — keduanya nyata, tidak ada yang
pura-pura. Keluaran: jumlah internal/external/scripts/files/endpoints.

### `dezz exif foto.jpg` — bedah metadata foto

EXIF + GPS lokal (file atau URL). Contoh uji: foto dengan GPS
6°12′S 106°49′E → lat `-6.2`, lon `106.816…`.

### `dezz dl <link> --probe` — info media tanpa download

```bash
dezz dl https://www.youtube.com/watch?v=aqz-KE-bpKQ --probe  # info saja
dezz dl <link> --audio   # mp3
dezz dl <link> --video   # mp4
```

Probe mengembalikan judul, situs, uploader, durasi (yt-dlp,
1000+ situs).

### `dezz resources "sherlock"` — cari tool OSINT lain

Katalog offline 3793 entri (digabung dari awesome-osint jivoi,
Astrosp, Ph055a). Contoh: `sherlock` → Sherlock
(github.com/sherlock-project/sherlock), SherlockEye, dan entri
terkait lainnya.

### `dezz sf --search dns` — rancang pemindaian SpiderFoot

```bash
dezz sf --search dns        # cari modul, mis. sfp_dnsresolve
dezz sf example.com         # bangun perintah scan (dijalankan manual)
```

Katalog 233 modul nyata dari checkout SpiderFoot. dezz TIDAK
berpura-pura menjalankan SpiderFoot — perintahnya dicetak untuk
dijalankan manual di checkout SpiderFoot.

### `dezz tor` — status Tor (gate jujur)

Tanpa layanan Tor di mesin, outputnya:

```json
{"tor_binary": false, "runnable": false}
```

Bukan hasil scan palsu — install Tor dulu, baru gate terbuka.

### `dezz dossier <target>` / `dezz run` — kupas tuntas

Tebak jenis target (nomor / email / IP / domain / URL / username),
jalankan semua engine yang cocok, tampilkan per seksi, simpan arsip
JSON ke `Data/dezz_<target>.json`.

## MCP — pakai dari Claude Desktop / opencode

`mcp.json` di root repo (ganti `cwd` ke path repo kamu):

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

Server stdio JSON-RPC 2.0 (MCP 2024-11-05), 13 tool:
`phone_lookup`, `username_search`, `email_recon`, `ip_lookup`,
`domain_recon`, `github_lookup`, `url_recon`, `osint_resources`,
`spiderfoot_plan`, `full_dossier`, `web_crawl`, `image_exif`,
`media_download`. Tiap tool memanggil engine yang sama dengan CLI.

Cek cepat server hidup:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  | python -m dezz.mcp.server
```

## Server pendamping — dezz-extract

`server/` adalah backend yt-dlp pengganti Cobalt untuk DezDownload
(`POST /` gaya Cobalt). Bukan bagian CLI; jalankan terpisah:

```bash
pip install -r server/requirements-server.txt
uvicorn server.main:app --port 8000
```

Lihat `server/README.md`. Deploy di VPS/Railway/Render/Fly
(Dockerfile tersedia) — jangan di Vercel serverless.
