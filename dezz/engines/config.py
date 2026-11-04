"""Central config for dezz-osint — secure API keys via environment variables.

Inspired by theHarvester / Sherlock / PhoneInfoga pattern:
- free passive sources first (no key needed)
- premium APIs only if user provides key via .env
- never hardcode secrets in source
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional, env vars still work

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # dezz-osint/
DATA_DIR = BASE_DIR / "Data"
DATA_DIR.mkdir(exist_ok=True)


def get_key(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


# Optional premium keys (all features work without them, degraded gracefully)
GOOGLE_API_KEY = get_key("GOOGLE_API_KEY")
GOOGLE_CX = get_key("GOOGLE_CX")
NUMVERIFY_API_KEY = get_key("NUMVERIFY_API_KEY")
IPSTACK_API_KEY = get_key("IPSTACK_API_KEY")
RAPIDAPI_WHATSAPP_KEY = get_key("RAPIDAPI_WHATSAPP_KEY")
GITHUB_TOKEN = get_key("GITHUB_TOKEN")  # optional, raises rate limit 60 -> 5000/hr

# Free passive sources (no key, ala theHarvester free defaults + crt.sh + DNS Google)
DNS_DOH_URL = "https://dns.google/resolve"
CRT_SH_URL = "https://crt.sh/"
HACKERTARGET_URL = "https://api.hackertarget.com"
IP_API_URL = "http://ip-api.com/json"  # free, no key, 45 req/min
RDAP_BOOTSTRAP = "https://data.iana.org/rdap/dns.json"
WAYBACK_CDX = "http://web.archive.org/cdx/search/cdx"
GITHUB_API = "https://api.github.com"

REQUEST_TIMEOUT = int(get_key("NETRA_TIMEOUT", "12"))
MAX_WORKERS = int(get_key("NETRA_WORKERS", "10"))

HEADERS_DEFAULT = {"User-Agent": "dezz-osint/1.0 (+https://github.com/dezzorigin/dezz-osint)"}


def data_path(filename: str) -> Path:
    return DATA_DIR / filename
