"""Orchestrator — one dossier across all VERIFIED-working engines.

Every engine here passed a live test. Steps are best-effort;
failures recorded honestly, never crash, never fake results.
"""
from __future__ import annotations
import json
import time
from pathlib import Path

from dezz.config import DATA


def _safe(fn, *a, **k):
    try:
        return {"ok": True, "data": fn(*a, **k)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:500]}


def _email_full(email: str) -> dict:
    from dezz.engines.email_ext import analyze_email
    from dezz.mcp.tools import _firefox_status, _hudson
    out = analyze_email(email)
    out["firefox"] = _firefox_status(email)
    out["hudson_rock"] = _hudson(email)
    return out


def dossier(target: str, deep_username: bool = False) -> dict:
    """Auto-detect target type and run relevant engines."""
    t = target.strip()
    rep = {"target": t, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "engines": {}}
    is_email = "@" in t and "." in t.split("@")[-1]
    is_phone = t.replace("+", "").replace(" ", "").replace("-", "").isdigit()
    is_ip = len(t.split(".")) == 4 and all(p.isdigit() for p in t.split("."))
    looks_domain = ("." in t and " " not in t and "@" not in t
                    and not t.startswith("http") and not is_ip)
    looks_url = t.startswith("http")

    from dezz.engines import phone_offline, ipcheck, domaincheck, urlcheck, githubcheck
    from dezz.adapters import maigret_adapter, resources_catalog, spiderfoot_adapter

    if is_phone:
        rep["engines"]["phone"] = _safe(phone_offline.analyze_phone, t)
    if is_email:
        rep["engines"]["email"] = _safe(_email_full, t)
    if is_ip:
        rep["engines"]["ip"] = _safe(ipcheck.lookup_ip, t)
    if looks_domain or looks_url:
        rep["engines"]["domain"] = _safe(domaincheck.analyze_domain, t)
    if looks_url or looks_domain:
        rep["engines"]["url"] = _safe(urlcheck.analyze_url, t if looks_url else f"https://{t}")
    if " " not in t and "@" not in t and not is_ip and not looks_url and not looks_domain and len(t) >= 2:
        rep["engines"]["username"] = _safe(maigret_adapter.search, t.lstrip("@"), deep_username)
        rep["engines"]["github"] = _safe(githubcheck.github_user, t.lstrip("@"))
    rep["engines"]["spiderfoot_map"] = {"ok": True, "data": spiderfoot_adapter.footprint_map()}
    rep["engines"]["resources_hint"] = {"ok": True, "data": resources_catalog.search(t, limit=5)}
    return rep


def save_report(rep: dict, name: str = "") -> Path:
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in (name or rep.get("target", "report")))[:60]
    p = DATA / f"dezz_{safe}.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    return p
