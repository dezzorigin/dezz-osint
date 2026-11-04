"""Image metadata / EXIF intelligence — dezz's own clean engine.

Inspired by the EXIF capability in TermuxHackz/X-osint (a tkinter GUI app
that cannot run headless, so NOT wired). This is our own headless
implementation using Pillow (already installed): EXIF tags, GPS -> lat/lon,
device/software hints. Passive, local-only — never uploads anywhere.
"""
from __future__ import annotations
import io
import json
import requests
from rich import print
from dezz.engines.config import REQUEST_TIMEOUT, HEADERS_DEFAULT, data_path

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def _dms_to_deg(dms, ref) -> float | None:
    try:
        d = float(dms[0]) + float(dms[1]) / 60 + float(dms[2]) / 3600
        if str(ref) in ("S", "W"):
            d = -d
        return round(d, 6)
    except Exception:
        return None


def analyze_image(source: str) -> dict:
    """source = local path or http(s) URL. Returns EXIF dict, never raises."""
    out: dict = {"source": source}
    if not HAS_PIL:
        out["error"] = "Pillow not installed (pip install pillow)"
        return out
    try:
        if source.startswith(("http://", "https://")):
            r = requests.get(source, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content))
        else:
            img = Image.open(source)
        out.update({"format": img.format, "size": list(img.size), "mode": img.mode})
        raw = img.getexif() or {}
        tags = {}
        gps: dict = {}
        try:
            gps_ifd = raw.get_ifd(0x8825) if hasattr(raw, "get_ifd") else {}
            for gk, gv in dict(gps_ifd).items():
                gps[GPSTAGS.get(gk, str(gk))] = gv
        except Exception:
            pass
        for k, v in raw.items():
            name = TAGS.get(k, str(k))
            if name == "GPSInfo":
                continue  # handled above via get_ifd
            tags[name] = str(v)[:300]
        out["exif"] = tags
        # parse GPS (values may be tuples/IFDRational — normalize to float)
        def _num(x):
            try:
                return float(x)
            except Exception:
                try:
                    return float(x.numerator) / float(x.denominator)
                except Exception:
                    return None
        if gps and "GPSLatitude" in gps and "GPSLongitude" in gps:
            try:
                lat_t = [ _num(v) for v in gps["GPSLatitude"] ]
                lon_t = [ _num(v) for v in gps["GPSLongitude"] ]
                if None not in lat_t and None not in lon_t:
                    out["gps"] = {
                        "lat": _dms_to_deg(lat_t, gps.get("GPSLatitudeRef")),
                        "lon": _dms_to_deg(lon_t, gps.get("GPSLongitudeRef")),
                    }
                else:
                    out["gps_raw"] = {k: str(v)[:200] for k, v in gps.items()}
                if out.get("gps", {}).get("lat") is not None:
                    out["maps_link"] = f"https://www.google.com/maps?q={out['gps']['lat']},{out['gps']['lon']}"
                    out["privacy_warning"] = "IMAGE CONTAINS GPS LOCATION — do not share publicly."
            except Exception:
                out["gps_raw"] = {k: str(v)[:200] for k, v in gps.items()}
        elif gps:
            out["gps_raw"] = {k: str(v)[:200] for k, v in gps.items()}
        interesting = {k: tags[k] for k in ("Make", "Model", "Software", "DateTime", "DateTimeOriginal") if k in tags}
        out["device_hints"] = interesting
    except Exception as e:
        out["error"] = str(e)[:300]
    return out


def print_image_report(source: str):
    info = analyze_image(source)
    safe = "".join(c if c.isalnum() else "_" for c in source.split("/")[-1])[:40] or "image"
    with open(data_path(f"exif_{safe}.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print("[yellow]EXIF report saved in Data folder[/yellow]")
    if info.get("error"):
        print(f"[red][!][/red] {info['error']}")
        return info
    print(f"  Format : {info.get('format')} {info.get('size')}")
    print(f"  EXIF tags: {len(info.get('exif', {}))}")
    for k, v in (info.get("device_hints") or {}).items():
        print(f"  {k}: {v}")
    if info.get("gps"):
        print(f"  [bold red]GPS: {info['gps']} — {info.get('privacy_warning')}[/bold red]")
        print(f"  Maps: {info.get('maps_link')}")
    else:
        print("  GPS: none found")
    return info


if __name__ == "__main__":
    import sys
    print_image_report(sys.argv[1] if len(sys.argv) > 1 else input("Image path/URL: ").strip())
