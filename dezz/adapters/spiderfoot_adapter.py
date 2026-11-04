"""SpiderFoot adapter — HONEST EDITION.

What is REAL here (verified against checkout):
- module inventory: 200+ sfp_* modules actually present on disk
- module metadata search: name/summary/useCases parsed from real source
- scan command builder: only emits module names verified to exist;
  the command runs MANUALLY in the SpiderFoot checkout (dezz does not
  pretend to run SpiderFoot scans itself).

What dezz covers natively instead (instant, keyless):
  sfp_archiveorg -> urlcheck Wayback | sfp_dns* -> domaincheck DoH |
  sfp_geoip-ish -> ipcheck ip-api | sfp_github -> githubcheck API
"""
from __future__ import annotations
import re
from functools import lru_cache
from pathlib import Path
from dezz.config import SPIDERFOOT_DIR

# Verified to exist in smicallef/spiderfoot checkout (checked live).
PRESET_PASSIVE = [
    "sfp_dnsresolve", "sfp_dnscommonsrv", "sfp_archiveorg",
    "sfp_github", "sfp_gravatar", "sfp_hackertarget",
    "sfp_crt", "sfp_builtwith", "sfp_whois", "sfp_dnsbrute",
]


@lru_cache(maxsize=1)
def _inventory() -> list:
    mods = []
    moddir = SPIDERFOOT_DIR / "modules"
    if moddir.exists():
        files = sorted(moddir.glob("sfp_*.py"))
    else:
        files = []
    for p in files:
        try:
            src = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        name = re.search(r"'name':\s*\"([^\"]+)\"", src)
        summ = re.search(r"'summary':\s*\"([^\"]+)\"", src)
        uses = re.search(r"'useCases':\s*(\[[^\]]*\])", src)
        mods.append({"module": p.stem,
                     "name": name.group(1) if name else p.stem,
                     "summary": summ.group(1) if summ else "",
                     "useCases": uses.group(1) if uses else ""})
    if not mods:
        # offline snapshot (233 modules, parsed from real checkout)
        try:
            import json as _j
            snap = Path(__file__).parent.parent / "spiderfoot_modules.json"
            mods = _j.loads(snap.read_text(encoding="utf-8"))
        except Exception:
            pass
    return mods


def status() -> dict:
    inv = _inventory()
    live = (SPIDERFOOT_DIR / "modules").exists()
    return {"checkout": str(SPIDERFOOT_DIR), "present": bool(inv),
            "module_count": len(inv), "live_checkout": live,
            "note": None if live else "Offline module snapshot in use; clone spiderfoot for live scans."}


def search_modules(query: str, limit: int = 15) -> list:
    q = (query or "").lower()
    out = [m for m in _inventory()
           if not q or q in f"{m['module']} {m['name']} {m['summary']}".lower()]
    return out[:limit]


def build_scan_cmd(target: str, modules: list | None = None) -> dict:
    """Build a REAL copy-paste command for the SpiderFoot checkout.

    Only includes modules verified on disk. The user runs it manually —
    dezz never claims the scan ran.
    """
    avail = {m["module"] for m in _inventory()}
    wanted = modules or PRESET_PASSIVE
    valid = [m for m in wanted if m in avail]
    missing = [m for m in wanted if m not in avail]
    cmd = f"cd {SPIDERFOOT_DIR} && python3 sf.py -s {target} -m {','.join(valid)}"
    return {"target": target, "modules": valid, "missing_skipped": missing,
            "run_manually": cmd,
            "note": "Run this command yourself in the spiderfoot checkout; "
                    "or use dezz light engines for instant keyless results.",
            "light_alternative": f"dezz dossier {target}"}


def footprint_map() -> dict:
    return {
        "domain/DNS": {"dezz": "engines.domaincheck (DoH + crt.sh + RDAP)", "spiderfoot": ["sfp_dnsresolve", "sfp_crt", "sfp_hackertarget"]},
        "ip/geo": {"dezz": "engines.ipcheck (ip-api free)", "spiderfoot": ["sfp_ipinfo", "sfp_ipstack"]},
        "username": {"dezz": "maigret deep (installed) / fast candidates", "spiderfoot": ["sfp_accounts"]},
        "email": {"dezz": "engines.email_ext + validator (firefox/hudson/emails)", "spiderfoot": ["sfp_email"]},
        "website/history": {"dezz": "engines.urlcheck (headers + Wayback CDX)", "spiderfoot": ["sfp_archiveorg", "sfp_builtwith"]},
        "github": {"dezz": "engines.githubcheck (public API)", "spiderfoot": ["sfp_github"]},
    }
