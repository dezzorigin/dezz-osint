"""Smoke tests — every assertion is a LIVE-verified behavior. No mocks."""
import json
import os
import subprocess
import sys
import tempfile as _tf
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

results = []
def check(name, fn):
    try:
        fn()
        print(f"[ok] {name}")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        results.append(False)


def t_phone():
    from dezz.engines.phone_offline import analyze_phone
    assert analyze_phone("+6281234567890")["valid"] is True

def t_ip():
    from dezz.engines.ipcheck import lookup_ip
    assert lookup_ip("8.8.8.8")["country"] == "United States"

def t_github():
    from dezz.engines.githubcheck import github_user
    assert github_user("torvalds")["exists"] is True

def t_domain():
    from dezz.engines.domaincheck import analyze_domain
    assert analyze_domain("example.com")["A"]

def t_email_structured():
    from dezz.mcp.tools import _firefox_status, _hudson
    from dezz.engines.email_ext import analyze_email
    assert analyze_email("test@example.com")["valid_format"] is True
    assert "checked" in _firefox_status("test@example.com")
    assert "checked" in _hudson("test@example.com")

def t_username_fast_honest():
    from dezz.adapters.maigret_adapter import fast_search
    r = fast_search("torvalds")
    assert "candidates_unverified" in r and "note" in r

def t_resources():
    from dezz.adapters.resources_catalog import count, search
    assert count() > 1000 and search("sherlock", limit=5)

def t_sf_real():
    from dezz.adapters.spiderfoot_adapter import status, search_modules, build_scan_cmd
    st = status()
    assert st["module_count"] > 200
    assert search_modules("dns")
    cmd = build_scan_cmd("example.com")
    assert "sfp_dnsresolve" in cmd["modules"] and "run_manually" in cmd

def t_mcp():
    p1 = subprocess.run([sys.executable, "-m", "dezz.mcp.server"],
                        input=b'{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}\n',
                        capture_output=True, cwd=str(ROOT), timeout=30)
    tools = json.loads(p1.stdout.decode().strip().splitlines()[-1])["result"]["tools"]
    assert len(tools) == 13, len(tools)
    p2 = subprocess.run([sys.executable, "-m", "dezz.mcp.server"],
                        input=b'{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"ip_lookup","arguments":{"ip":"8.8.8.8"}}}\n',
                        capture_output=True, cwd=str(ROOT), timeout=60)
    assert "United States" in p2.stdout.decode()
    import tempfile as _tf
    gps = os.path.join(_tf.gettempdir(), "dezz_smoke_gps.jpg")
    if not os.path.exists(gps):  # t_exif usually creates it; make it here too (order-independent)
        from PIL import Image
        import piexif
        img = Image.new("RGB", (50, 50), "blue")
        img.save(gps, exif=piexif.dump({"GPS": {
            piexif.GPSIFD.GPSLatitudeRef: "S",
            piexif.GPSIFD.GPSLatitude: [(6, 1), (12, 1), (0, 1)],
            piexif.GPSIFD.GPSLongitudeRef: "E",
            piexif.GPSIFD.GPSLongitude: [(106, 1), (49, 1), (0, 1)]}}))
    p3 = subprocess.run([sys.executable, "-m", "dezz.mcp.server"],
                        input=json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                          "params": {"name": "image_exif", "arguments": {"source": gps}}}).encode() + b"\n",
                        capture_output=True, cwd=str(ROOT), timeout=60)
    assert "-6.2" in p3.stdout.decode()

def t_dl_probe():
    from dezz.engines.media_dl import probe
    r = probe("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
    assert r.get("title") and r.get("has_video"), r

def t_server_shape():
    import sys as _s
    _s.path.insert(0, "server")
    from starlette.requests import Request
    from main import CobaltReq, cobalt_compat
    scope = {"type": "http", "method": "POST", "path": "/",
             "headers": [(b"x-forwarded-for", b"127.0.0.99")]}
    out = cobalt_compat(CobaltReq(url="https://www.youtube.com/watch?v=aqz-KE-bpKQ",
                                  videoQuality="max", downloadMode="auto"),
                        Request(scope))
    d = out if isinstance(out, dict) else {}
    assert d.get("status") == "redirect" and d.get("url", "").startswith("https://"), str(d)[:150]

def t_no_dead_imports():
    import subprocess as sp
    dead = ["idcheck", "instaemailfind", "scrap", "paste", "sololearn"]
    found = [d for d in dead if list((ROOT / "dezz" / "engines").rglob(f"{d}.py"))]
    assert not found, f"dead modules still present: {found}"

def t_tookie_available():
    from dezz.adapters.tookie_adapter import is_available, scan
    if is_available():
        r = scan("torvalds", threads=20)
        assert r["count"] > 0
    else:
        try:
            scan("torvalds")
            raise AssertionError("should have raised")
        except RuntimeError as e:
            assert "git clone" in str(e), e

def t_photon_available():
    from dezz.adapters.photon_adapter import is_available, crawl
    if is_available():
        r = crawl("https://example.com")
        assert r.get("engine") == "photon"
    else:
        r = crawl("https://example.com")  # fallback bawaan wajib jalan
        assert r.get("engine") == "dezz-builtin" and r.get("pages_crawled", 0) >= 1, r

def t_tor_honest():
    from dezz.adapters.torbot_adapter import status
    st = status()
    assert st["tor_binary"] is False and st["runnable"] is False

def t_exif():
    import tempfile, os
    from PIL import Image
    import piexif
    from dezz.engines.image_exif import analyze_image
    img = Image.new("RGB", (50, 50), "blue")
    exif_d = {"GPS": {piexif.GPSIFD.GPSLatitudeRef: "S",
                      piexif.GPSIFD.GPSLatitude: [(6, 1), (12, 1), (0, 1)],
                      piexif.GPSIFD.GPSLongitudeRef: "E",
                      piexif.GPSIFD.GPSLongitude: [(106, 1), (49, 1), (0, 1)]}}
    p = os.path.join(tempfile.gettempdir(), "dezz_smoke_gps.jpg")
    img.save(p, exif=piexif.dump(exif_d))
    r = analyze_image(p)
    assert r.get("gps", {}).get("lat") == -6.2, r

def t_catalog_grown():
    from dezz.adapters.resources_catalog import count
    assert count() >= 3000, count()

if __name__ == "__main__":
    for n, f in [("phone", t_phone), ("ip", t_ip), ("github", t_github),
                 ("domain", t_domain), ("email-structured", t_email_structured),
                 ("username-fast-honest", t_username_fast_honest),
                 ("resources", t_resources), ("spiderfoot-real", t_sf_real),
                 ("mcp", t_mcp), ("no-dead-modules", t_no_dead_imports),
                 ("tookie-available", t_tookie_available),
                 ("photon-available", t_photon_available),
                 ("tor-honest", t_tor_honest), ("exif", t_exif),
                 ("catalog-grown", t_catalog_grown), ("dl-probe", t_dl_probe),
                 ("server-shape", t_server_shape)]:
        check(n, f)
    sys.exit(0 if all(results) else 1)
