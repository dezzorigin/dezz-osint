# dezz-extract — backend DezDownload (pengganti Cobalt)

**Kenapa ada:** `api.cobalt.tools` publik sekarang wajib JWT
(`error.api.auth.jwt.missing`, terverifikasi live) → backend lama
DezDownload (`lib/downr.ts` → Cobalt) mati permanen tanpa self-host + key.

**Solusi:** ekstraksi sendiri pakai yt-dlp, ala Mori. Server hanya resolve
direct CDN URL (tanpa proxy file — hemat bandwidth, kayak Cobalt redirect).

## Jalankan lokal

```bash
pip install -r server/requirements-server.txt
uvicorn server.main:app --port 8000
curl http://127.0.0.1:8000/health
```

## Sambungkan DezDownload (NOL ubahan kode frontend)

`downr.ts` manggil `POST {COBALT_API_URL}/` gaya Cobalt — server ini ngomong
protokol yang sama. Cukup set env di Vercel:

```
COBALT_API_URL=https://<server-kamu>   # tanpa path tambahan
```

`COBALT_API_KEY` tidak perlu (dikosongkan). Deploy ulang → web hidup lagi.

## Deploy backend (pilih satu)

Server ini butuh proses Python lama + /tmp — **jangan di Vercel serverless**
(timeout & tanpa ffmpeg; itu juga kenapa proxy-file gagal di sana):

```bash
# Railway / Render / Fly / VPS — satu perintah:
docker build -t dezz-extract server/
docker run -e PORT=8000 -p 8000:8000 dezz-extract
```

Gratisan tier cukup: tiap request cuma ekstraksi (±5–15 dtk), file mengalir
langsung CDN → user, bukan lewat server.

**Anti-jebol:** rate limit 30 ekstraksi/menit/IP (429 jujur bila lebih).
`/health` bebas limit. Di-reverse-proxy teruskan IP asli via `X-Forwarded-For`.

## Endpoint

| Method & path | Format | Dipakai siapa |
|---|---|---|
| `POST /` `{url, videoQuality, downloadMode}` | Cobalt `{status, url, filename}` | DezDownload `downr.ts` |
| `GET/POST /api/download?url=` | dezz `{Status, Result{title, medias[]}}` | umum |
| `GET /api/probe?url=` | info ringan | umum |
| `GET /health` | `{ok}` | monitoring |
