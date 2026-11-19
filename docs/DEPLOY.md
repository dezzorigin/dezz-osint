# Deploy & Rilis — dezz-osint

Dua artefak, dua jalur — jangan dicampur:

| Artefak | Jalur | URL |
|---|---|---|
| Landing statis (etalase) | Cloudflare Pages | https://dezz-osint.pages.dev |
| CLI + MCP (produk) | GitHub Releases | https://github.com/dezzorigin/dezz-osint/releases |

## Landing → Cloudflare Pages

Landing (`index.html`, `styles.css`, `app.js`, `favicon.svg`,
`og-image.png`) di-deploy sebagai situs statis dengan
`~/workspace/github-actions/cf_pages.py` (token via vault):

```bash
python3 ~/workspace/github-actions/cf_pages.py create-project dezz-osint
python3 ~/workspace/github-actions/cf_pages.py deploy dezz-osint <dir-landing>
```

Fallback nama bila `dezz-osint` dipakai akun lain: `dezzosint`,
lalu `osint-dezz`. Nama bersufiks di hasil create = dipakai akun
lain — pindah ke fallback berikutnya.

Verifikasi live (pola repo #24–#43, `scripts/verify-live.py`):

```bash
python3 scripts/verify-live.py
```

Cek: root 200 + marker landing + semua tag og:/twitter: +
`og-image.png` 200 dengan content-type `image/*` (bukan
`text/html` — Pages fallback menipu) + ukuran ≥10 KB. Pakai UA
browser — UA default python kena 403 dari Cloudflare.

## CLI + MCP → GitHub Releases

CLI dirilis sebagai source + paket Python, bukan Pages:

```bash
git tag v1.0-proper
git push origin v1.0-proper
# lalu buat release di GitHub (catatan proper + aset sdist/wheel bila ada)
```

Tag `v1.0-proper` adalah tonggak "proper" rantai P1 — bukan
kenaikan versi paket (`pyproject.toml` tetap `0.2.0` sampai ada
perubahan fitur). Cek dulu tag/release yang sudah ada sebelum
membuat — jangan duplikat.

Install dari release:

```bash
pip install https://github.com/dezzorigin/dezz-osint/archive/refs/tags/v1.0-proper.tar.gz
# atau: git clone + pip install .
```

## Server pendamping (opsional)

`server/` (dezz-extract) butuh proses Python lama + /tmp — deploy
di VPS/Railway/Render/Fly via Dockerfile di `server/`. Jangan di
Vercel serverless (timeout & tanpa ffmpeg).
