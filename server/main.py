"""dezz-extract API — backend pengganti Cobalt untuk DezDownload.

Masalah: api.cobalt.tools publik sekarang wajib JWT
  -> {"status":"error","error":{"code":"error.api.auth.jwt.missing"}}
  Tanpa self-host + key, backend lama mati permanen.

Solusi ala Mori/yt-dlp: ekstraksi sendiri pakai yt-dlp.
Server TIDAK mem-proxy file (hemat bandwidth): hanya resolve direct CDN URL,
frontend redirect langsung ke sana (kayak Cobalt tunnel/redirect).

Kompatibilitas (frontend DezDownload NOL ubahan kode):
- POST /  (gaya Cobalt: {url, videoQuality, downloadMode})
  Set COBALT_API_URL=<server-ini> di Vercel. downr.ts jalan apa adanya.
- GET/POST /api/download?url=  (gaya dezz: {Status, Result{title, medias[]}})
- GET /api/probe?url=  info ringan. GET /health cek hidup.

Deploy: Docker ke Railway/Render/Fly/VPS (Vercel serverless tidak cocok:
timeout & tanpa ffmpeg; itulah kenapa pendekatan proxy-file gagal di sana).
"""
from __future__ import annotations
import time
from collections import defaultdict, deque
from typing import Any

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="dezz-extract", version="0.2.0")

# Rate limit sederhana tanpa deps baru: 30 ekstraksi/menit/IP (anti-viral-jebol).
# /health selalu bebas. Di-reverse-proxy, teruskan IP asli via X-Forwarded-For.
RATE_MAX, RATE_WINDOW = 30, 60.0
_hits: dict[str, deque] = defaultdict(deque)


def _limited(ip: str) -> bool:
    now = time.time()
    q = _hits[ip]
    while q and now - q[0] > RATE_WINDOW:
        q.popleft()
    if len(q) >= RATE_MAX:
        return True
    q.append(now)
    return False


def _ip(req: Request) -> str:
    fwd = req.headers.get("x-forwarded-for", "")
    return (fwd.split(",")[0].strip() or req.client.host) if req.client else "unknown"


class CobaltReq(BaseModel):
    url: str
    videoQuality: str = "max"
    downloadMode: str = "auto"  # auto | audio | mute


def _info(url: str) -> dict:
    from yt_dlp import YoutubeDL
    with YoutubeDL({"quiet": True, "no_warnings": True, "no_playlist": True,
                    "socket_timeout": 20}) as ydl:
        return ydl.extract_info(url, download=False) or {}


def _pick(info: dict, mode: str) -> dict | None:
    """Pilih 1 direct URL terbaik. Video: mp4 progresif (ada audio, tanpa merge)."""
    fmts = [f for f in (info.get("formats") or []) if f.get("url")]
    if not fmts:
        return None
    if mode == "audio":
        cands = [f for f in fmts if f.get("acodec") not in (None, "none")]
        cands.sort(key=lambda f: (f.get("abr") or 0), reverse=True)
        f = cands[0] if cands else None
        return {"url": f["url"], "filename": f"{info.get('title', 'audio')}.mp3"} if f else None
    # progresif mp4 dulu (tanpa merge), fallback apapun yg ada video+audio
    prog = [f for f in fmts if f.get("ext") == "mp4"
            and f.get("vcodec") not in (None, "none")
            and f.get("acodec") not in (None, "none")]
    if prog:
        prog.sort(key=lambda f: (f.get("height") or 0), reverse=True)
        f = prog[0]
    else:
        both = [f for f in fmts if f.get("vcodec") not in (None, "none")
                and f.get("acodec") not in (None, "none")]
        f = both[-1] if both else fmts[-1]
    return {"url": f["url"], "filename": f"{info.get('title', 'video')}.mp4"}


@app.get("/health")
def health():
    return {"ok": True, "service": "dezz-extract", "ts": time.time()}


@app.post("/")
def cobalt_compat(req: CobaltReq, request: Request):
    """Drop-in pengganti api.cobalt.tools — downr.ts DezDownload tak perlu diubah."""
    if _limited(_ip(request)):
        return JSONResponse({"status": "error", "error": {"code": "error.api.rate_limit"}},
                            status_code=429)
    try:
        info = _info(req.url.strip())
    except Exception as e:
        return JSONResponse({"status": "error", "error": {"code": "error.fetch.fail",
                             "message": str(e)[:200]}})
    if not info:
        return JSONResponse({"status": "error", "error": {"code": "error.link.invalid"}})
    got = _pick(info, req.downloadMode)
    if not got:
        return JSONResponse({"status": "error", "error": {"code": "error.fetch.fail"}})
    return {"status": "redirect", "url": got["url"], "filename": got["filename"]}


@app.get("/api/probe")
def probe(request: Request, url: str = Query(...)):
    if _limited(_ip(request)):
        return JSONResponse({"Status": False, "Error": "Terlalu banyak permintaan, coba lagi sebentar."},
                            status_code=429)
    try:
        info = _info(url.strip())
    except Exception as e:
        return {"Status": False, "Error": str(e)[:200]}
    if not info:
        return {"Status": False, "Error": "link tidak valid / tak didukung"}
    dur = info.get("duration") or 0
    return {"Status": True,
            "Result": {"title": info.get("title"), "uploader": info.get("uploader"),
                       "duration": f"{dur // 60}:{dur % 60:02d}" if dur else "?",
                       "thumbnail": info.get("thumbnail"),
                       "site": info.get("extractor_key") or info.get("extractor")}}


@app.api_route("/api/download", methods=["GET", "POST"])
async def download(request: Request, payload: dict | None = None, url: str = Query("")):
    if _limited(_ip(request)):
        return JSONResponse({"Status": False, "Error": "Terlalu banyak permintaan, coba lagi sebentar."},
                            status_code=429)
    link = (url or (payload or {}).get("url") or "").strip()
    if not link:
        return JSONResponse({"Status": False, "Error": "URL is required"}, status_code=400)
    try:
        info = _info(link)
    except Exception as e:
        return JSONResponse({"Status": False, "Error": str(e)[:200]}, status_code=502)
    if not info:
        return JSONResponse({"Status": False, "Error": "link tidak valid"}, status_code=422)
    medias: list[dict[str, Any]] = []
    v = _pick(info, "auto")
    if v:
        medias.append({"url": v["url"], "type": "video", "ext": "mp4",
                       "quality": "best", "label": "Video terbaik", "hasAudio": True})
    a = _pick(info, "audio")
    if a:
        medias.append({"url": a["url"], "type": "audio", "ext": "mp3",
                       "quality": "best", "label": "Audio terbaik", "hasAudio": True})
    if not medias:
        return JSONResponse({"Status": False, "Error": "tidak ada stream"}, status_code=422)
    return {"Status": True, "Code": 200, "Input": link,
            "Result": {"title": info.get("title"), "thumbnail": info.get("thumbnail"),
                       "author": info.get("uploader"), "source": "dezz-extract",
                       "duration": info.get("duration"), "medias": medias},
            "Error": None}
