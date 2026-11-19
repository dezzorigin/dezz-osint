"""pytest untuk dezz-osint — setiap assert adalah perilaku live.

Tanpa mock: perintah CLI dijalankan beneran (subprocess), engine
memanggil sumber publik yang sama dengan pemakaian nyata, MCP
server dijalankan beneran lewat stdio. Target uji dipilih yang
stabil: 8.8.8.8, example.com, torvalds.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PY = sys.executable


def run_cli(*args, timeout=120):
    """Jalankan `python -m dezz.cli ...` dari root repo."""
    return subprocess.run(
        [PY, "-m", "dezz.cli", *args],
        capture_output=True, text=True, cwd=str(ROOT), timeout=timeout,
    )


# ── CLI ──────────────────────────────────────────────────────────────────

def test_cli_help():
    p = run_cli("--help")
    assert p.returncode == 0
    assert "phone" in p.stdout
    assert "dossier" in p.stdout
    assert "username" in p.stdout


def test_cli_phone_offline():
    # Offline (phonenumbers) — tanpa kunci, tanpa jaringan wajib.
    p = run_cli("phone", "+6281234567890")
    assert p.returncode == 0
    assert "6281234567890" in p.stdout
    assert "wa.me" in p.stdout


def test_cli_ip_live():
    p = run_cli("ip", "8.8.8.8")
    assert p.returncode == 0
    assert "United States" in p.stdout
    assert "8.8.8.8" in p.stdout


def test_cli_resources_offline():
    p = run_cli("resources", "sherlock", "--limit", "5")
    assert p.returncode == 0
    assert "Sherlock" in p.stdout


def test_cli_sf_search():
    p = run_cli("sf", "--search", "dns")
    assert p.returncode == 0
    assert "sfp_dnsresolve" in p.stdout


# ── Engine: phone / ip / github / domain / email ──────────────────────────

def test_phone_offline():
    from dezz.engines.phone_offline import analyze_phone

    assert analyze_phone("+6281234567890")["valid"] is True


def test_ip_lookup():
    from dezz.engines.ipcheck import lookup_ip

    assert lookup_ip("8.8.8.8")["country"] == "United States"


def test_github_user():
    from dezz.engines.githubcheck import github_user

    assert github_user("torvalds")["exists"] is True


def test_domain_doh():
    from dezz.engines.domaincheck import analyze_domain

    assert analyze_domain("example.com")["A"]


def test_email_structured():
    from dezz.engines.email_ext import analyze_email
    from dezz.mcp.tools import _firefox_status, _hudson

    assert analyze_email("test@example.com")["valid_format"] is True
    assert "checked" in _firefox_status("test@example.com")
    assert "checked" in _hudson("test@example.com")


def test_username_fast_honest():
    from dezz.adapters.maigret_adapter import fast_search

    r = fast_search("torvalds")
    assert "candidates_unverified" in r and "note" in r


# ── Katalog & SpiderFoot ───────────────────────────────────────────────────

def test_resources_catalog():
    from dezz.adapters.resources_catalog import count, search

    assert count() > 1000
    assert search("sherlock", limit=5)


def test_catalog_grown():
    from dezz.adapters.resources_catalog import count

    assert count() >= 3000, count()


def test_spiderfoot_real():
    from dezz.adapters.spiderfoot_adapter import build_scan_cmd, search_modules, status

    st = status()
    assert st["module_count"] > 200
    assert search_modules("dns")
    cmd = build_scan_cmd("example.com")
    assert "sfp_dnsresolve" in cmd["modules"] and "run_manually" in cmd


# ── MCP server (stdio, beneran) ────────────────────────────────────────────

def _mcp_call(payload):
    p = subprocess.run(
        [PY, "-m", "dezz.mcp.server"],
        input=json.dumps(payload).encode() + b"\n",
        capture_output=True, cwd=str(ROOT), timeout=60,
    )
    assert p.returncode == 0, p.stderr.decode()[:300]
    return json.loads(p.stdout.decode().strip().splitlines()[-1])


def test_mcp_tools_list():
    out = _mcp_call({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    tools = out["result"]["tools"]
    assert len(tools) == 13, len(tools)
    names = {t["name"] for t in tools}
    assert {"phone_lookup", "ip_lookup", "full_dossier", "image_exif"} <= names


def test_mcp_ip_lookup():
    out = _mcp_call({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                     "params": {"name": "ip_lookup", "arguments": {"ip": "8.8.8.8"}}})
    assert "United States" in json.dumps(out)


def test_mcp_image_exif(tmp_path):
    from PIL import Image
    import piexif

    gps = tmp_path / "gps.jpg"
    img = Image.new("RGB", (50, 50), "blue")
    img.save(gps, exif=piexif.dump({"GPS": {
        piexif.GPSIFD.GPSLatitudeRef: "S",
        piexif.GPSIFD.GPSLatitude: [(6, 1), (12, 1), (0, 1)],
        piexif.GPSIFD.GPSLongitudeRef: "E",
        piexif.GPSIFD.GPSLongitude: [(106, 1), (49, 1), (0, 1)]}}))
    out = _mcp_call({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                     "params": {"name": "image_exif", "arguments": {"source": str(gps)}}})
    assert "-6.2" in json.dumps(out)


# ── EXIF / Tor / Photon / Tookie ───────────────────────────────────────────

def test_exif_gps(tmp_path):
    from PIL import Image
    import piexif
    from dezz.engines.image_exif import analyze_image

    p = tmp_path / "gps.jpg"
    img = Image.new("RGB", (50, 50), "blue")
    exif_d = {"GPS": {piexif.GPSIFD.GPSLatitudeRef: "S",
                      piexif.GPSIFD.GPSLatitude: [(6, 1), (12, 1), (0, 1)],
                      piexif.GPSIFD.GPSLongitudeRef: "E",
                      piexif.GPSIFD.GPSLongitude: [(106, 1), (49, 1), (0, 1)]}}
    img.save(p, exif=piexif.dump(exif_d))
    r = analyze_image(str(p))
    assert r.get("gps", {}).get("lat") == -6.2, r


def test_tor_honest():
    from dezz.adapters.torbot_adapter import status

    st = status()
    assert st["tor_binary"] is False and st["runnable"] is False


def test_photon_available():
    from dezz.adapters.photon_adapter import is_available, crawl

    if is_available():
        r = crawl("https://example.com")
        assert r.get("engine") == "photon"
    else:
        r = crawl("https://example.com")  # fallback bawaan wajib jalan
        assert r.get("engine") == "dezz-builtin" and r.get("pages_crawled", 0) >= 1, r


def test_tookie_gate():
    from dezz.adapters.tookie_adapter import is_available, scan

    if is_available():
        r = scan("torvalds", threads=20)
        assert r["count"] > 0
    else:
        with pytest.raises(RuntimeError, match="git clone"):
            scan("torvalds")


def test_dl_probe():
    from dezz.engines.media_dl import probe

    r = probe("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
    assert r.get("title") and r.get("has_video"), r


def test_server_shape():
    pytest.importorskip("starlette")
    sys.path.insert(0, str(ROOT / "server"))
    from starlette.requests import Request
    from main import CobaltReq, cobalt_compat

    scope = {"type": "http", "method": "POST", "path": "/",
             "headers": [(b"x-forwarded-for", b"127.0.0.99")]}
    out = cobalt_compat(CobaltReq(url="https://www.youtube.com/watch?v=aqz-KE-bpKQ",
                                  videoQuality="max", downloadMode="auto"),
                        Request(scope))
    d = out if isinstance(out, dict) else {}
    assert d.get("status") == "redirect" and d.get("url", "").startswith("https://"), str(d)[:150]


def test_no_dead_modules():
    dead = ["idcheck", "instaemailfind", "scrap", "paste", "sololearn"]
    found = [d for d in dead if list((ROOT / "dezz" / "engines").rglob(f"{d}.py"))]
    assert not found, f"dead modules still present: {found}"


# ── Dossier ────────────────────────────────────────────────────────────────

def test_dossier_detects_ip(tmp_path, monkeypatch):
    from dezz.orchestrator import dossier

    monkeypatch.chdir(tmp_path)
    rep = dossier("8.8.8.8")
    assert rep["engines"]["ip"]["ok"] is True
    assert rep["engines"]["ip"]["data"]["country"] == "United States"
