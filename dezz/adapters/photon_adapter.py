"""Photon adapter — web crawl with honest fallback.

1. Checkout Photon (s0md3v/Photon) bila ada -> crawl asli.
2. Kalau tidak ada -> crawler bawaan dezz (BFS same-domain, tanpa deps baru).
Keduanya REAL (HTTP beneran), bukan dummy. Plugin --wayback Photon mati
upstream (JSONDecodeError) jadi tidak pernah dipakai; Wayback via urlcheck.
"""
from __future__ import annotations
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

from dezz.config import WORKSPACE
from dezz.engines.config import REQUEST_TIMEOUT, HEADERS_DEFAULT

PHOTON_DIR = WORKSPACE / "s0md3v-photon"

FILE_EXT = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".rar",
            ".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".csv", ".txt")


def is_available() -> bool:
    return (PHOTON_DIR / "photon.py").exists()


def _same_site(a: str, b: str) -> bool:
    na, nb = urlparse(a).netloc.lower(), urlparse(b).netloc.lower()
    if not na or not nb:
        return False
    na = na.split(":")[0].lstrip("www.")
    nb = nb.split(":")[0].lstrip("www.")
    return na == nb or na.endswith("." + nb) or nb.endswith("." + na)


def _builtin_crawl(url: str, max_pages: int = 20, timeout: int = 120) -> dict:
    """Crawler bawaan: BFS same-domain, kumpulin link/skrip/file/endpoint."""
    import requests
    t0 = time.time()
    seen, queue = set(), [url]
    internal, external, scripts, files, endpoints = set(), set(), set(), set(), set()
    pages = 0
    while queue and pages < max_pages and time.time() - t0 < timeout:
        cur = queue.pop(0)
        if cur in seen:
            continue
        seen.add(cur)
        try:
            r = requests.get(cur, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
            ctype = r.headers.get("Content-Type", "")
            if "html" not in ctype:
                continue
            pages += 1
            html = r.text
            for m in re.finditer(r'''(?:href|src|action|data-src)=(?:["']([^"'#]+)["']|([^\s>]+))''', html, re.I):
                raw_link = (m.group(1) or m.group(2) or "").strip()
                if not raw_link or raw_link.startswith(("data:", "javascript:", "mailto:")):
                    continue
                link = urljoin(cur, raw_link)
                if not link.startswith(("http://", "https://")):
                    continue
                low = link.lower().split("?")[0]
                if any(low.endswith(e) or ".js" in low for e in ("",)) and low.endswith(".js"):
                    scripts.add(link)
                elif low.endswith(FILE_EXT):
                    files.add(link)
                elif _same_site(url, link):
                    internal.add(link)
                    if link not in seen and len(queue) < max_pages * 2:
                        queue.append(link)
                else:
                    external.add(link)
            for m in re.finditer(r'''["']((?:/|https?://)[^"' ]*(?:api|endpoint|v\d/)[^"' ]*)["']''', html):
                endpoints.add(urljoin(cur, m.group(1)))
        except Exception:
            continue
    data = {"engine": "dezz-builtin", "input": url, "pages_crawled": pages,
            "internal": sorted(internal)[:200], "internal_count": len(internal),
            "external": sorted(external)[:200], "external_count": len(external),
            "scripts": sorted(scripts)[:200], "scripts_count": len(scripts),
            "files": sorted(files)[:200], "files_count": len(files),
            "endpoints": sorted(endpoints)[:200], "endpoints_count": len(endpoints)}
    if pages == 0:
        raise RuntimeError(f"tidak bisa mengambil {url} (cek koneksi/URL)")
    return data


def crawl(url: str, timeout: int = 180) -> dict:
    """Crawl asli: Photon bila checkout ada, fallback crawler bawaan."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    if is_available():
        return _photon_crawl(url, timeout)
    data = _builtin_crawl(url, timeout=min(timeout, 120))
    data["note"] = "crawler bawaan (checkout Photon tak ada — clone untuk hasil lebih dalam)"
    return data


def _photon_crawl(url: str, timeout: int = 180) -> dict:
    outdir = Path(tempfile.mkdtemp(prefix="dezz-photon-"))
    cmd = [sys.executable, "photon.py", "-u", url, "--timeout", "10", "-o", str(outdir)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(PHOTON_DIR))
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"photon crawl timed out after {timeout}s")
    data: dict = {"engine": "photon", "input": url, "returncode": r.returncode,
                  "outdir": str(outdir)}
    for name in ("internal.txt", "external.txt", "scripts.txt", "files.txt",
                 "fuzzable.txt", "endpoints.txt", "keys.txt"):
        p = outdir / name
        # photon nests output one level deeper sometimes
        if not p.exists():
            inner = sorted(outdir.glob(f"*/{name}"))
            p = inner[0] if inner else p
        if p.exists():
            try:
                lines = [l.strip() for l in p.read_text(errors="ignore").splitlines() if l.strip()]
                data[name.replace(".txt", "")] = lines[:200]
                data[name.replace(".txt", "") + "_count"] = len(lines)
            except Exception:
                pass
    if not any(k.endswith("_count") for k in data):
        raise RuntimeError(f"photon produced no output (stderr: {(r.stderr or '')[-300:]})")
    return data
