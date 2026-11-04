"""MCP tool definitions — single source for MCP server + docs.

Model Context Protocol (2024-11-05): tools/list exposes these; tools/call executes.
All passive, authorized-use only. No auto-attack, no bruteforce, no key leaks.
"""
from __future__ import annotations

TOOLS = [
    {"name": "phone_lookup",
     "description": "Offline phone-number intelligence (PhoneInfoga-style offline: validity, region, carrier, E164, wa.me/t.me links). Input: phone like +62812xxxx.",
     "inputSchema": {"type": "object", "properties": {"phone": {"type": "string"}}, "required": ["phone"]}},
    {"name": "username_search",
     "description": "Username recon. fast: candidates (UNVERIFIED) + verified GitHub API. maigret: REAL deep scan (minutes). tookie: REAL 262-site scan (minutes).",
     "inputSchema": {"type": "object", "properties": {"username": {"type": "string"}, "deep": {"type": "boolean"}, "engine": {"type": "string"}}, "required": ["username"]}},
    {"name": "email_recon",
     "description": "Email recon (all live-verified): MX records, Gravatar, Firefox monitor, HudsonRock breach data.",
     "inputSchema": {"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]}},
    {"name": "ip_lookup",
     "description": "IP geolocation via free ip-api.com (country/city/ISP/ASN). No key needed.",
     "inputSchema": {"type": "object", "properties": {"ip": {"type": "string"}}, "required": ["ip"]}},
    {"name": "domain_recon",
     "description": "Domain recon ala theHarvester free: DNS-over-HTTPS (A/MX/TXT/NS), crt.sh subdomains, RDAP.",
     "inputSchema": {"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]}},
    {"name": "github_lookup",
     "description": "GitHub user enrichment via public REST API (profile, repos, followers). No key needed.",
     "inputSchema": {"type": "object", "properties": {"username": {"type": "string"}}, "required": ["username"]}},
    {"name": "url_recon",
     "description": "Website recon ala Photon-lite + Wayback: headers, server hints, title, Wayback snapshots.",
     "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "osint_resources",
     "description": "Search the awesome-osint catalog (1444 curated tools/resources) by keyword and category.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "category": {"type": "string"}, "limit": {"type": "number"}}, "required": ["query"]}},
    {"name": "spiderfoot_plan",
     "description": "SpiderFoot: search the REAL 200+ module catalog, or build a verified copy-paste scan command to run manually in the SpiderFoot checkout.",
     "inputSchema": {"type": "object", "properties": {"target": {"type": "string"}, "search": {"type": "string"}}, "required": []}},
    {"name": "full_dossier",
     "description": "Orchestrated multi-engine dossier: auto-detect target type, run all relevant engines, return unified JSON.",
     "inputSchema": {"type": "object", "properties": {"target": {"type": "string"}, "deep_username": {"type": "boolean"}}, "required": ["target"]}},
    {"name": "web_crawl",
     "description": "REAL Photon web crawl: internal/external URLs, scripts, files, endpoints. Takes ~1 min. (Photon wayback plugin is dead upstream — use url_recon for Wayback.)",
     "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "image_exif",
     "description": "Image metadata intel: EXIF tags, device hints, GPS lat/lon + maps link from local file or image URL. Local-only, no upload.",
     "inputSchema": {"type": "object", "properties": {"source": {"type": "string"}}, "required": ["source"]}},
    {"name": "media_download",
     "description": "All-in-one downloader (yt-dlp, 1000+ sites). mode=info: metadata only (fast). mode=video: mp4 terbaik. mode=audio: mp3. Downloads to Data/downloads/.",
     "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}, "mode": {"type": "string"}}, "required": ["url"]}},
]


def _firefox_status(email: str) -> dict:
    import requests
    from dezz.engines.config import REQUEST_TIMEOUT, HEADERS_DEFAULT
    try:
        r = requests.post("https://api.accounts.firefox.com/v1/account/status",
                          data={"email": email}, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            return {"checked": True, "exists": r.json().get("exists")}
        return {"checked": False, "http": r.status_code}
    except Exception as e:
        return {"checked": False, "error": str(e)[:200]}


def _hudson(email: str) -> dict:
    import requests
    from dezz.engines.config import REQUEST_TIMEOUT, HEADERS_DEFAULT
    try:
        r = requests.get("https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email",
                         headers={"api-key": "ROCKHUDSONROCK", **HEADERS_DEFAULT},
                         params={"email": email}, timeout=REQUEST_TIMEOUT + 5)
        if r.status_code != 200:
            return {"checked": False, "http": r.status_code}
        d = r.json()
        stealers = d.get("stealers") or []
        return {"checked": True, "compromised": bool(stealers),
                "message": (d.get("message") or "")[:300],
                "date_compromised": [s.get("date_compromised") for s in stealers[:5]],
                "total_corporate": sum(s.get("total_corporate_services", 0) for s in stealers),
                "total_user": sum(s.get("total_user_services", 0) for s in stealers)}
    except Exception as e:
        return {"checked": False, "error": str(e)[:200]}


def execute(name: str, args: dict) -> dict:
    """Run a tool, return JSON-serializable result. Never raises."""
    try:
        if name == "phone_lookup":
            from dezz.engines.phone_offline import analyze_phone
            return analyze_phone(args.get("phone", ""))
        if name == "username_search":
            if (args.get("engine") or "").lower() == "tookie":
                from dezz.adapters.tookie_adapter import scan as tookie_scan
                return tookie_scan(args.get("username", ""))
            from dezz.adapters.maigret_adapter import search
            return search(args.get("username", ""), bool(args.get("deep", False)) or args.get("engine") == "maigret")
        if name == "email_recon":
            from dezz.engines.email_ext import analyze_email
            email = args.get("email", "")
            base = analyze_email(email)
            base["firefox"] = _firefox_status(email)
            base["hudson_rock"] = _hudson(email)
            return base
        if name == "ip_lookup":
            from dezz.engines.ipcheck import lookup_ip
            return lookup_ip(args.get("ip", ""))
        if name == "domain_recon":
            from dezz.engines.domaincheck import analyze_domain
            return analyze_domain(args.get("domain", ""))
        if name == "github_lookup":
            from dezz.engines.githubcheck import github_user
            return github_user(args.get("username", ""))
        if name == "url_recon":
            from dezz.engines.urlcheck import analyze_url
            return analyze_url(args.get("url", ""))
        if name == "osint_resources":
            from dezz.adapters.resources_catalog import search as rs
            return {"results": rs(args.get("query", ""), args.get("category", ""), int(args.get("limit", 20) or 20))}
        if name == "spiderfoot_plan":
            from dezz.adapters.spiderfoot_adapter import build_scan_cmd, status, search_modules
            if args.get("search"):
                return {"modules": search_modules(args["search"]), "spiderfoot": status()}
            return {"plan": build_scan_cmd(args.get("target", "")), "spiderfoot": status()}
        if name == "full_dossier":
            from dezz.orchestrator import dossier
            return dossier(args.get("target", ""), bool(args.get("deep_username", False)))
        if name == "web_crawl":
            from dezz.adapters.photon_adapter import crawl
            return crawl(args.get("url", ""))
        if name == "image_exif":
            from dezz.engines.image_exif import analyze_image
            return analyze_image(args.get("source", ""))
        if name == "media_download":
            from dezz.engines.media_dl import probe, download
            mode = (args.get("mode") or "info").lower()
            if mode == "video":
                return download(args.get("url", ""), audio_only=False)
            if mode == "audio":
                return download(args.get("url", ""), audio_only=True)
            return probe(args.get("url", ""))
        return {"error": f"unknown tool: {name}"}
    except Exception as e:
        return {"error": str(e)[:1000]}
