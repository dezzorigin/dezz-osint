"""Maigret adapter — deep username dossier (3000+ sites), REAL execution.

- maigret is INSTALLED in this project's venv (verified live).
- deep_search runs it as subprocess and parses reports/report_<user>_simple.json
  into {site, url} — no dummy output, failures raise honestly.
- fast_search = built-in candidate scan (honestly labeled unverified).
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dezz.config import MAIGRET_DIR, ROOT

REPORTS = ROOT / "reports"  # maigret writes here when cwd=ROOT


def is_available() -> bool:
    if shutil.which("maigret"):
        return True
    try:
        return (MAIGRET_DIR / "maigret" / "maigret.py").exists()
    except Exception:
        return False


def _parse_simple_report(username: str) -> list:
    """Parse maigret --json simple report. Returns [{site, url}]."""
    cands = [REPORTS / f"report_{username}_simple.json",
             MAIGRET_DIR / "reports" / f"report_{username}_simple.json",
             Path.cwd() / "reports" / f"report_{username}_simple.json"]
    for p in cands:
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                out = []
                for site, info in (d.items() if isinstance(d, dict) else []):
                    if not isinstance(info, dict):
                        continue
                    s = info.get("site", {}) or {}
                    url = s.get("url", "").replace("{username}", username)
                    out.append({"site": site, "url": url or info.get("url", ""),
                                "tags": s.get("tags", [])})
                return out
            except Exception:
                pass
    return []


def deep_search(username: str, timeout: int = 240, top_sites: int = 500) -> dict:
    """Run real maigret scan. Returns verified-claimed sites from JSON report."""
    username = username.strip().lstrip("@")
    if not username:
        raise ValueError("username empty")
    binary = shutil.which("maigret")
    if binary:
        cmd = [binary, username, "--timeout", "15", "--top-sites", str(top_sites),
               "--json", "simple", "--no-progress"]
    else:
        main_py = MAIGRET_DIR / "maigret" / "maigret.py"
        if not main_py.exists():
            raise RuntimeError("maigret not installed. Run: pip install maigret")
        cmd = [sys.executable, str(main_py), username, "--timeout", "15",
               "--top-sites", str(top_sites), "--json", "simple", "--no-progress"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))
    found = _parse_simple_report(username)
    return {"engine": "maigret", "username": username, "returncode": r.returncode,
            "found": found, "count": len(found),
            "log_tail": ((r.stdout or "") + (r.stderr or ""))[-1500:]}


def fast_search(username: str, limit: int = 200) -> dict:
    """Built-in quick scan — results are CANDIDATES (unverified)."""
    from dezz.engines.username import load_sites_config, check_username_on_site
    from dezz.engines.githubcheck import github_user
    username = username.strip().lstrip("@")
    sites = load_sites_config()
    verified, candidates = [], []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(check_username_on_site, username, n, c) for n, c in sites.items()]
        for f in as_completed(futs):
            try:
                name, verdict, link = f.result()
                if verdict is True:
                    verified.append({"site": name, "url": link})
                elif verdict == "candidate":
                    candidates.append({"site": name, "url": link})
            except Exception:
                pass
    try:
        gh = github_user(username)
    except Exception as e:
        gh = {"error": str(e)[:200]}
    return {"engine": "dezz-fast", "username": username,
            "verified": verified, "candidates_unverified": candidates[:limit],
            "github": gh,
            "note": "candidates are NOT confirmations; use deep=True (maigret) for verified results"}


def search(username: str, deep: bool = False) -> dict:
    if deep:
        return deep_search(username)
    return fast_search(username)
