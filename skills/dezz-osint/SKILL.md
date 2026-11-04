---
name: dezz-osint
description: Passive OSINT via dezz-osint CLI/MCP — phone carrier lookup, username enumeration (fast/maigret/tookie), email breach check (Firefox/HudsonRock), IP geolocation, domain DNS + crt.sh subdomains, website headers + crawl, GitHub enrichment, image EXIF/GPS, 3793-entry offline catalog. Use when the user asks to investigate a phone number, username, email, IP, domain, website, GitHub account, image metadata, or says stalking/kepoin/cek nomor/cek bocor/dossier. Authorized targets only.
license: MIT
metadata:
  version: "0.2.0"
  author: dezzorigin
  based_on: dezzorigin/dezz-osint (MIT)
---

# dezz-osint

Passive OSINT engine. Every wired check passed a live test; anything needing
a key/service says SKIP instead of faking output. Verdict log lives in the
repo at `dezz/docs/SOURCES.md`.

## Running it

Preferred (installed): the `dezz` binary. Fallback (checkout): `python -m dezz.cli`
from the repo root, or `dezz.py`. MCP alternative: stdio server
`python -m dezz.mcp.server` (12 tools, MCP 2024-11-05).

## Route by target

| User wants | CLI | MCP tool |
|---|---|---|
| Phone number intel | `dezz phone +62812…` | `phone_lookup` |
| Username footprint | `dezz username X` (fast) · `--engine maigret` (deep) · `--engine tookie` (262 sites) | `username_search` (+`engine`) |
| Email breach check | `dezz email a@b.com` | `email_recon` |
| IP geolocation | `dezz ip 8.8.8.8` | `ip_lookup` |
| Domain recon | `dezz domain example.com` | `domain_recon` |
| Website headers/Wayback | `dezz url https://…` | `url_recon` |
| Full-site crawl | `dezz crawl https://…` | `web_crawl` |
| GitHub profile | `dezz github user` | `github_lookup` |
| Image EXIF/GPS | `dezz exif photo.jpg` | `image_exif` |
| Media download | `dezz dl <link> [--audio/--video/--probe]` | `media_download` |
| Everything at once | `dezz dossier <target>` / `dezz run` (menu) | `full_dossier` |
| Find an OSINT tool | `dezz resources "kata"` | `osint_resources` |
| SpiderFoot modules | `dezz sf --search dns` | `spiderfoot_plan` |

## Output rules

1. Present findings as readable text sections, never raw JSON.
2. Fast username hits are **candidates, NOT confirmations** — label `[?]`,
   only GitHub API data is `[verified]`. Never state a candidate as fact.
3. Long output (>30 lines): offer show-here vs save `.md` (`Data/dezz_<target>.md`).
4. Breach hits (`hudson_rock.compromised`): advise password rotation. This tool
   never returns passwords — if asked for any, refuse.
5. `crawl`/`--engine maigret|tookie` take minutes — say so before running.

## Guardrails (non-negotiable)

- Authorized targets only: the user's own data or explicit permission
  (self-check, scam-number verification, breach check on own email).
- Refuse: doxxing, harassment/stalking of a real person, real-time tracking,
  anything to embarrass or harm. Suggest the safety framing instead
  ("cek nomor penipu", "cek kebocoran dataku").
- Missing engine/checkout/key: report the honest SKIP + restore command,
  never invent results.
