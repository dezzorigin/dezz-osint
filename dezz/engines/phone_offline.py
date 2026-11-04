"""Offline phone-number intelligence — ala PhoneInfoga (offline part).

Uses `phonenumbers` lib (same family as PhoneInfoga) — no API key,
works for Indonesia (+62) by default. Purely parsing public numbering plan.
"""
import json
from rich import print

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone, phonenumberutil
    HAS_LIB = True
except ImportError:
    HAS_LIB = False

from .config import data_path


def analyze_phone(raw: str, default_region: str = "ID") -> dict:
    """Parse & validate phone number offline. Returns dict, never raises."""
    raw = str(raw).strip().replace(" ", "").replace("-", "")
    result = {"input": str(raw), "valid": False}
    if not HAS_LIB:
        result["error"] = "phonenumbers lib not installed. Run: pip install phonenumbers"
        return result
    try:
        if not raw.startswith("+"):
            # assume default region if no country code
            num = phonenumbers.parse(raw, default_region)
        else:
            num = phonenumbers.parse(raw, None)
        result.update({
            "valid": phonenumbers.is_valid_number(num),
            "possible": phonenumbers.is_possible_number(num),
            "e164": phonenumbers.format_in_original_format(num, default_region) if hasattr(phonenumbers, "format_in_original_format") else str(raw),
            "international": phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "national": phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL),
            "e164_format": phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164),
            "country_code": num.country_code,
            "region": geocoder.description_for_number(num, "en"),
            "carrier": carrier.name_for_number(num, "en"),
            "timezones": timezone.time_zones_for_number(num),
            "type": str(phonenumberutil.number_type(num)),
        })
    except Exception as e:
        result["error"] = str(e)
    return result


def print_phone_report(raw: str, default_region: str = "ID"):
    info = analyze_phone(raw, default_region)
    with open(data_path("phone_offline.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print("[yellow]phone_offline.json saved in Data folder[/yellow]")
    if not info.get("valid"):
        print(f"[red][!][/red] Invalid / not-possible number: {raw}")
        if info.get("error"):
            print(f"Reason: {info['error']}")
        return info
    print(f"[green][+][/green] International : {info.get('international')}")
    print(f"[green][+][/green] E164          : {info.get('e164_format')}")
    print(f"[green][+][/green] Region        : {info.get('region')}")
    print(f"[green][+][/green] Carrier       : {info.get('carrier') or '-'}")
    print(f"[green][+][/green] Timezones     : {', '.join(info.get('timezones') or [])}")
    e164 = info.get("e164_format", "").lstrip("+")
    print(f"\n[cyan]Quick links (passive, no login):[/cyan]")
    print(f"  WhatsApp : https://wa.me/{e164}")
    print(f"  Telegram : https://t.me/+{e164}")
    print(f"  Truecaller search hint: google \"{info.get('international')} spam\"")
    return info


if __name__ == "__main__":
    n = input("Phone (+62... or 08...): ").strip()
    print_phone_report(n)
