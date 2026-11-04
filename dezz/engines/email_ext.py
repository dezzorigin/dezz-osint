"""Email extras — Holehe-lite idea, keyless only.

- MX record check via DNS-over-HTTPS (does domain accept mail?)
- Gravatar existence via SHA256 hash (same as existing validator, but standalone)
- Disposable-domain heuristic (small built-in list)
Does NOT send mail / bruteforce / breach passwords — passive checks only.
"""
import hashlib
import json
import requests
from rich import print
from .config import DNS_DOH_URL, REQUEST_TIMEOUT, HEADERS_DEFAULT, data_path

DISPOSABLE_HINTS = {"tempmail", "10minutemail", "guerrillamail", "mailinator", "yopmail", "trashmail"}


def mx_check(domain: str):
    try:
        r = requests.get(DNS_DOH_URL, params={"name": domain, "type": "MX"},
                         headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return [a.get("data") for a in r.json().get("Answer", [])]
    except Exception:
        return []


def gravatar_exists(email: str) -> dict:
    h = hashlib.sha256(email.strip().lower().encode()).hexdigest()
    url = f"https://gravatar.com/{h}.json"
    try:
        r = requests.get(url, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200 and "displayName" in r.text:
            try:
                entry = r.json().get("entry", [{}])[0]
                return {"registered": True,
                        "username": entry.get("preferredUsername"),
                        "profile": entry.get("profileUrl")}
            except Exception:
                return {"registered": True}
        return {"registered": False}
    except Exception as e:
        return {"registered": None, "error": str(e)}


def analyze_email(email: str) -> dict:
    email = email.strip().lower()
    out = {"email": email, "valid_format": "@" in email and "." in email.split("@")[-1]}
    domain = email.split("@")[-1] if "@" in email else ""
    out["domain"] = domain
    out["mx_records"] = mx_check(domain) if domain else []
    out["gravatar"] = gravatar_exists(email)
    out["disposable_hint"] = any(x in domain for x in DISPOSABLE_HINTS)
    return out


def print_email_extra(email: str):
    info = analyze_email(email)
    with open(data_path("email_extra.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print("[yellow]email_extra.json saved in Data folder[/yellow]")
    print(f"  Format valid : {info['valid_format']}")
    print(f"  MX records   : {info['mx_records'] or 'none found'}")
    print(f"  Gravatar     : {info['gravatar']}")
    if info["disposable_hint"]:
        print("  [yellow]Hint: looks like disposable/temporary mail domain[/yellow]")
    return info


if __name__ == "__main__":
    e = input("Email: ").strip()
    print_email_extra(e)
