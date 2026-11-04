"""Fast username scan — HONEST EDITION.

WARNING (verified by live test): generic status-code probing has false
positives on login-walled sites (Facebook/Instagram/Spotify return 200 for
everyone). Results are CANDIDATE links, NOT confirmed profiles.
For verified results use maigret (`dezz.py username X --deep`), which has
per-site error markers and is installed in this project.
"""
import requests
import json
import time
from pathlib import Path
from rich import print
from concurrent.futures import ThreadPoolExecutor, as_completed
from .githubcheck import print_github_report
from .config import MAX_WORKERS, data_path


def load_sites_config(path=None):
    if path is None:
        path = Path(__file__).parent / "murl.json"
    with open(path, 'r') as f:
        return json.load(f)

def check_username_on_site(username, site_name, site_config):
    url = site_config["url"].replace("{username}", username)
    headers = site_config.get("headers", {})
    timeout = site_config.get("timeout_seconds", 5)
    delay = site_config.get("rate_limit_delay", 1)
    allow_redirects = (site_config["redirect_behavior"] == "follow")

    try:
        response = requests.request(
            method=site_config["request_method"],
            url=url,
            headers=headers,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )

        if not site_config["detect_based_on_message"]:
            if response.status_code in site_config["not_found_status_codes"]:
                return site_name, False, None
            # status-only verdict: UNVERIFIED candidate (site may soft-404)
            return site_name, "candidate", url

        content = response.text
        if site_config["not_found_message"] and site_config["not_found_message"] in content:
            return site_name, False, None
        if site_config["found_message"] and site_config["found_message"] in content:
            return site_name, True, url

        return site_name, None, None
    except requests.RequestException:
        return site_name, None, None
    finally:
        time.sleep(delay)


def main(username: str | None = None):
    if username is None:
        print("[magenta]Enter username to search[/magenta]: ", end="")
        username = input().strip()
    username = username.strip()
    if not username:
        print("[red]Username kosong.[/red]")
        return
    sites = load_sites_config()
    verified, candidates = [], []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(check_username_on_site, username, site_name, site_config)
            for site_name, site_config in sites.items()
        ]

        for future in as_completed(futures):
            site_name, result, link = future.result()
            if result is True:
                print(f"[green][verified][/green] {site_name} : {link}")
                verified.append({"site": site_name, "url": link})
            elif result == "candidate":
                candidates.append({"site": site_name, "url": link})

    print(f"\n[yellow]{len(candidates)} candidate links (UNVERIFIED — visit to confirm, may be soft-404):[/yellow]")
    for c in sorted(candidates, key=lambda x: x["site"])[:40]:
        print(f"  [?] {c['site']}: {c['url']}")

    try:
        with open(data_path(f"username_{username}.json"), "w", encoding="utf-8") as f:
            json.dump({"username": username, "verified": verified,
                       "candidates_unverified": candidates,
                       "total_checked": len(sites),
                       "note": "candidates are NOT confirmations; use --deep (maigret) for verified results"},
                      f, ensure_ascii=False, indent=2)
        print(f"[yellow]username_{username}.json saved ({len(verified)} verified, {len(candidates)} candidates)[/yellow]")
    except Exception:
        pass

    try:
        print("\n[magenta][+][/magenta] GitHub API enrichment (verified source)...\n")
        print_github_report(username)
    except Exception as e:
        print(f"GitHub enrichment failed: {e}")

if __name__ == "__main__":
    main()
