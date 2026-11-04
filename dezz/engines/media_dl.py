"""Media downloader engine — yt-dlp wrapper (all-in-one downloader).

Live-tested: YouTube probe + audio download work (ffmpeg present for merge).
Supports 1000+ sites via yt-dlp. Downloads go to Data/downloads/ (gitignored).
Respects site ToS — user downloads content they have the right to save.
"""
from __future__ import annotations
from pathlib import Path

from dezz.engines.config import data_path

DL_DIR = Path(data_path("downloads"))
DL_DIR.mkdir(exist_ok=True)


def _ydl_opts(extra: dict | None = None) -> dict:
    o = {"quiet": True, "no_warnings": True, "no_playlist": True,
         "socket_timeout": 20}
    if extra:
        o.update(extra)
    return o


def probe(url: str) -> dict:
    """Ambil info (judul/uploader/durasi/format) TANPA download. Cepat."""
    from yt_dlp import YoutubeDL
    with YoutubeDL(_ydl_opts()) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            return {"url": url, "error": str(e)[:300]}
    if not info:
        return {"url": url, "error": "tidak ada info (situs tak didukung?)"}
    fmts = info.get("formats") or []
    has_video = any(f.get("vcodec") not in (None, "none") for f in fmts)
    has_audio = any(f.get("acodec") not in (None, "none") for f in fmts)
    dur = info.get("duration") or 0
    return {"url": url, "site": info.get("extractor_key") or info.get("extractor"),
            "title": info.get("title"), "uploader": info.get("uploader"),
            "duration_s": dur,
            "duration": f"{dur // 60}:{dur % 60:02d}" if dur else "?",
            "has_video": has_video, "has_audio": has_audio,
            "format_count": len(fmts)}


def download(url: str, audio_only: bool = False) -> dict:
    """Download beneran. Video: mp4 terbaik. Audio: mp3 via ffmpeg."""
    from yt_dlp import YoutubeDL
    meta = probe(url)
    if meta.get("error"):
        return meta
    tpl = str(DL_DIR / "%(title).80s [%(id)s].%(ext)s")
    if audio_only:
        if not meta.get("has_audio"):
            return {"url": url, "error": "tidak ada trek audio"}
        opts = _ydl_opts({"format": "bestaudio/best",
                          "postprocessors": [{"key": "FFmpegExtractAudio",
                                             "preferredcodec": "mp3",
                                             "preferredquality": "192"}],
                          "outtmpl": tpl})
    else:
        opts = _ydl_opts({"format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
                          "merge_output_format": "mp4",
                          "outtmpl": tpl})
    try:
        with YoutubeDL(opts) as ydl:
            code = ydl.download([url])
        files = sorted(DL_DIR.glob("*"), key=lambda p: p.stat().st_mtime)
        newest = files[-1] if files else None
        if code != 0 or newest is None:
            return {"url": url, "error": f"yt-dlp exit {code}"}
        mb = newest.stat().st_size / 1e6
        return {"url": url, "title": meta.get("title"), "file": str(newest),
                "size_mb": round(mb, 1),
                "mode": "audio(mp3)" if audio_only else "video(mp4)"}
    except Exception as e:
        return {"url": url, "error": str(e)[:300]}


def supported_sites() -> list:
    """Daftar extractor yt-dlp (1000+). Ringan: dari daftar bawaan."""
    try:
        from yt_dlp.extractor import gen_extractor_classes
        names = sorted({e.IE_NAME for e in gen_extractor_classes()})
        return [n for n in names if n != "generic"][:50]
    except Exception:
        return ["youtube", "tiktok", "instagram", "twitter", "facebook",
                "soundcloud", "spotify", "reddit", "vimeo"]
