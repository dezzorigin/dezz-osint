"""Website / URL recon — lightweight ala Photon + Wayback Machine.

Keyless & passive:
- HTTP headers + server/tech hints
- final URL / redirects
- Wayback CDX: first/last snapshot + snapshot count
"""
import json
import requests
from rich import print
from urllib.parse import urlparse
from .config import WAYBACK_CDX, REQUEST_TIMEOUT, HEADERS_DEFAULT, data_path


def analyze_url(url: str) -> dict:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    out = {"input": url}
    try:
        r = requests.get(url, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        out.update({
            "final_url": r.url,
            "status": r.status_code,
            "server": r.headers.get("Server"),
            "powered_by": r.headers.get("X-Powered-By"),
            "tech_hints": {k: v for k, v in r.headers.items()
                           if k.lower() in ("server", "x-powered-by", "x-aspnet-version",
                                            "x-generator", "cf-ray", "x-cache", "via")},
            "title_hint": None,
        })
        # naive <title> extract (no bs4 dependency needed here)
        try:
            txt = r.text
            i, j = txt.lower().find("<title>"), txt.lower().find("</title>")
            if 0 <= i < j < i + 500:
                out["title_hint"] = txt[i + 7:j].strip()[:200]
        except Exception:
            pass
    except requests.RequestException as e:
        out["error"] = str(e)
        return out
    # Wayback CDX
    try:
        host = urlparse(out.get("final_url") or url).netloc or urlparse(url).netloc
        rr = requests.get(WAYBACK_CDX, params={
            "url": host + "/*", "output": "json", "fl": "timestamp,original,statuscode",
            "collapse": "digest", "limit": 5,
        }, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
        if rr.status_code == 200:
            try:
                data = rr.json()
                out["wayback_samples"] = data[:6]
                out["wayback_note"] = f"Check full history: https://web.archive.org/web/*/{host}"
            except Exception:
                out["wayback_note"] = f"https://web.archive.org/web/*/{host}"
        else:
            out["wayback_note"] = f"https://web.archive.org/web/*/{host}"
    except Exception:
        pass
    return out


def print_url_report(url: str):
    info = analyze_url(url)
    safe = urlparse(url).netloc.replace("/", "_") or "site"
    with open(data_path(f"url_{safe}.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"[yellow]url_{safe}.json saved in Data folder[/yellow]")
    if info.get("error"):
        print(f"[red][!][/red] {info['error']}")
        return info
    print(f"  Final URL : {info.get('final_url')}")
    print(f"  Status    : {info.get('status')}")
    print(f"  Server    : {info.get('server')}")
    print(f"  Title     : {info.get('title_hint')}")
    print(f"  Wayback   : {info.get('wayback_note')}")
    return info


def check_url():
    u = input("Enter URL (example.com): ").strip()
    if u:
        print_url_report(u)


if __name__ == "__main__":
    check_url()
