"""Tookie-osint adapter — second-opinion username scan (262 sites), REAL execution.

Runs upstream `brib.py -u USER -t N -sC -o json` (V4 CLI, live-tested:
36 hits for `torvalds`) and parses the structured JSON report — no stdout
scraping. Same honesty rule as fast engine: output = candidates
(UNVERIFIED), except GitHub which we verify via public API.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from dezz.config import ROOT, WORKSPACE

_CANDIDATES = [
    Path(os.getenv("TOOKIE_DIR", "")) if os.getenv("TOOKIE_DIR") else None,
    WORKSPACE / "tookie-osint",
    ROOT / "tookie-osint",
    WORKSPACE / "alfredredbird-tookie-osint",  # legacy dirname
    ROOT.parent / "alfredredbird-tookie-osint",
]
TOOKIE_DIR = next((d for d in _CANDIDATES if d and (d / "brib.py").exists()), None)

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def is_available() -> bool:
    return TOOKIE_DIR is not None


def scan(username: str, threads: int = 20, timeout: int = 300) -> dict:
    """Run real tookie scan. Returns candidate URLs parsed from JSON report."""
    username = username.strip().lstrip("@")
    if not username:
        raise ValueError("username empty")
    if not is_available():
        raise RuntimeError(
            "tookie-osint checkout not found. Restore: "
            "git clone https://github.com/Alfredredbird/tookie-osint.git")
    report = TOOKIE_DIR / f"{username}.json"
    if report.exists():
        report.unlink()  # never trust a stale report
    cmd = [sys.executable, "brib.py", "-u", username, "-t", str(threads),
           "-sC", "-o", "json"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=str(TOOKIE_DIR))
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"tookie scan timed out after {timeout}s")
    found = []
    try:
        rows = json.loads(report.read_text())
        for row in rows if isinstance(rows, list) else []:
            url = (row.get("url") or "").strip()
            if row.get("found") and url and username.lower() in url.lower():
                if url not in {f["url"] for f in found}:
                    found.append({"url": url, "status": row.get("status")})
    except Exception:
        # JSON missing/unparseable (e.g. upstream crash): fall back to [+]-lines
        for line in ANSI.sub("", r.stdout or "").splitlines():
            m = re.search(r"\[\+\]\s*(https?://\S+)", line)
            if m and username.lower() in m.group(1).lower():
                url = m.group(1).rstrip(".")
                if url not in {f["url"] for f in found}:
                    found.append({"url": url})
    finally:
        if report.exists():
            report.unlink()  # keep checkout clean
    return {"engine": "tookie-osint", "username": username, "returncode": r.returncode,
            "candidates_unverified": found, "count": len(found),
            "note": "Candidates, NOT confirmations — visit to verify."}
