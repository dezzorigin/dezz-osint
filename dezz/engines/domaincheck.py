"""Domain / DNS OSINT — ala theHarvester free sources + Amass/crt.sh idea.

100% passive & keyless:
- DNS over HTTPS (dns.google/resolve) for A, MX, TXT, NS
- crt.sh Certificate Transparency for subdomains
- RDAP (rdap.verisign.com / rdap.org) for registrar info
- HackerTarget reverse-IP hint (free tier)

Use for: investigate domain footprint before deeper scan.
"""
import json
import requests
from rich import print
from .config import DNS_DOH_URL, CRT_SH_URL, REQUEST_TIMEOUT, HEADERS_DEFAULT, data_path


def doh(domain: str, rtype: str = "A"):
    """DNS-over-HTTPS via Google. Returns list of answers."""
    try:
        r = requests.get(DNS_DOH_URL, params={"name": domain, "type": rtype},
                         headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json().get("Answer", [])
    except Exception:
        return []


def crt_subdomains(domain: str, max_items: int = 50):
    """crt.sh wildcard search — same source theHarvester uses by default."""
    try:
        r = requests.get(CRT_SH_URL, params={"q": f"%.{domain}", "output": "json"},
                         headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT + 8)
        if r.status_code != 200 or not r.text.strip().startswith("["):
            return []
        seen = set()
        for entry in r.json():
            name = (entry.get("name_value") or "").strip().lower()
            for sub in name.split("\n"):
                sub = sub.strip().lstrip("*.")
                if sub and (sub.endswith(domain.lower())):
                    seen.add(sub)
                if len(seen) >= max_items:
                    break
        return sorted(seen)
    except Exception:
        return []


def rdap(domain: str):
    for base in ("https://rdap.verisign.com/com/v1/domain/",
                 "https://rdap.verisign.com/net/v1/domain/"):
        try:
            r = requests.get(base + domain, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                d = r.json()
                return {
                    "registrar": str([e.get("vcardArray", []) for e in d.get("entities", [])])[:500],
                    "creation": [ev.get("eventDate") for ev in d.get("events", []) if ev.get("eventAction") == "registration"],
                    "raw_status": d.get("status", [])[:10],
                }
        except Exception:
            continue
    return {}


def analyze_domain(domain: str) -> dict:
    domain = domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]
    result = {"domain": domain}
    result["A"] = [a.get("data") for a in doh(domain, "A")]
    result["MX"] = [a.get("data") for a in doh(domain, "MX")]
    result["TXT"] = [a.get("data") for a in doh(domain, "TXT")][:10]
    result["NS"] = [a.get("data") for a in doh(domain, "NS")]
    result["subdomains_crtsh"] = crt_subdomains(domain)
    result["rdap"] = rdap(domain)
    # reverse IP hint via HackerTarget free (may rate-limit — best effort)
    result["reverse_hint"] = None
    if result["A"]:
        try:
            import requests as rq
            rr = rq.get(f"https://api.hackertarget.com/reverseiplookup/?q={result['A'][0]}",
                        headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
            if rr.status_code == 200 and "error" not in rr.text.lower()[:100]:
                result["reverse_hint"] = rr.text.strip()[:2000]
        except Exception:
            pass
    return result


def print_domain_report(domain: str):
    info = analyze_domain(domain)
    with open(data_path(f"domain_{info['domain'].replace('/', '_')}.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"[dim]lengkap tersimpan: Data/domain_{info['domain']}.json[/dim]\n")
    print(f"[bold cyan]Domain: {info['domain']}[/bold cyan]")
    print(f"  A   : {', '.join(info['A'][:3]) if info['A'] else '-'}")
    print(f"  MX  : {', '.join(info['MX'][:3]) if info['MX'] else '-'}")
    print(f"  NS  : {', '.join(info['NS'][:3]) if info['NS'] else '-'}")
    txt = info['TXT'] or []
    if txt:
        print(f"  TXT : {txt[0][:100]}")
    subs = info.get("subdomains_crtsh", [])
    print(f"  Subdomain crt.sh ({len(subs)}):")
    for s in subs[:15]:
        print(f"    - {s}")
    if len(subs) > 15:
        print(f"    ... +{len(subs) - 15} lagi (lengkap di JSON)")
    rdap = info.get("rdap") or {}
    if rdap.get("creation"):
        print(f"  Terdaftar: {', '.join(rdap['creation'][:2])}")
    if rdap.get("raw_status"):
        print(f"  Status: {', '.join(rdap['raw_status'][:4])}")
    return info


def check_domain():
    d = input("Enter domain (example.com): ").strip()
    if d:
        print_domain_report(d)


if __name__ == "__main__":
    check_domain()
