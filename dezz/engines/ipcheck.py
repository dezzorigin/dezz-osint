import requests
import json
from rich import print
from .config import IP_API_URL, IPSTACK_API_KEY, REQUEST_TIMEOUT, HEADERS_DEFAULT, data_path

def _lookup_ipapi(ip: str):
    """Free, no-key lookup (45 req/min). Primary source."""
    r = requests.get(f"{IP_API_URL}/{ip}?fields=status,message,country,regionName,city,lat,lon,isp,org,as,query",
                     headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    d = r.json()
    if d.get("status") != "success":
        raise ValueError(d.get("message", "ip-api lookup failed"))
    return {
        "ip": d.get("query"), "country": d.get("country"), "region": d.get("regionName"),
        "city": d.get("city"), "lat": d.get("lat"), "lon": d.get("lon"),
        "isp": d.get("isp"), "org": d.get("org"), "as": d.get("as"),
        "source": "ip-api.com (free, no key)",
    }

def _lookup_ipstack(ip: str):
    """Optional fallback if IPSTACK_API_KEY is set via .env."""
    url = f"https://api.ipstack.com/{ip}?access_key={IPSTACK_API_KEY}"
    r = requests.get(url, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    d = r.json()
    return {
        "ip": d.get("ip"), "country": d.get("country_name"), "region": d.get("region_name"),
        "city": d.get("city"), "lat": d.get("latitude"), "lon": d.get("longitude"),
        "isp": (d.get("connection") or {}).get("isp"),
        "source": "ipstack (key from env)",
    }

def lookup_ip(ip: str) -> dict:
    ip = ip.strip()
    try:
        return _lookup_ipapi(ip)
    except Exception as e:
        if IPSTACK_API_KEY:
            try:
                return _lookup_ipstack(ip)
            except Exception as e2:
                return {"ip": ip, "error": f"ip-api: {e} | ipstack: {e2}"}
        return {"ip": ip, "error": str(e)}

def check_ip_address():
    try:
        print("[magenta]Enter IP Address to search[/magenta]: ", end="")
        IP_ADD = input().strip()
        if not IP_ADD:
            print("[red]IP kosong.[/red]")
            return
        data = lookup_ip(IP_ADD)
        with open(data_path("ip_information.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("[yellow]ip_information.json saved in Data folder[/yellow]\n")
        if data.get("error"):
            print(f"[red]Lookup gagal: {data['error']}[/red]")
            return
        print(f"IP Address: {data.get('ip')}")
        print(f"Country: {data.get('country')}")
        print(f"Region: {data.get('region')}")
        print(f"City: {data.get('city')}")
        print(f"Latitude: {data.get('lat')}")
        print(f"Longitude: {data.get('lon')}")
        print(f"ISP: {data.get('isp')}")
        print(f"Source: {data.get('source')}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
    except Exception:
        print("Error: Unable to validate the IP address. Please check your input or try again later. or check your internet connection.")