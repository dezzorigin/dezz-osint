"""GitHub user enrichment via public REST API — ala Sherlock/Maigret enrichment.

Why API not scraping (old scrap.py gitinfo):
- scraping github.com HTML is fragile (class names change weekly)
- api.github.com/users/{u} is stable, free, no key (60 req/hr), JSON
- optional GITHUB_TOKEN raises to 5000 req/hr
"""
import json
import requests
from rich import print
from .config import GITHUB_API, GITHUB_TOKEN, HEADERS_DEFAULT, REQUEST_TIMEOUT, data_path


def _headers():
    h = dict(HEADERS_DEFAULT)
    h["Accept"] = "application/vnd.github.v3+json"
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def github_user(username: str) -> dict:
    username = username.strip().lstrip("@")
    out = {"username": username}
    try:
        r = requests.get(f"{GITHUB_API}/users/{username}", headers=_headers(), timeout=REQUEST_TIMEOUT)
        if r.status_code == 404:
            out["exists"] = False
            return out
        r.raise_for_status()
        d = r.json()
        out.update({
            "exists": True,
            "name": d.get("name"),
            "bio": d.get("bio"),
            "company": d.get("company"),
            "location": d.get("location"),
            "email_public": d.get("email"),
            "blog": d.get("blog"),
            "twitter": d.get("twitter_username"),
            "public_repos": d.get("public_repos"),
            "followers": d.get("followers"),
            "following": d.get("following"),
            "created_at": d.get("created_at"),
            "avatar": d.get("avatar_url"),
            "profile": d.get("html_url"),
        })
        # top repos (by stars, max 5) — extra signal like Maigret does
        try:
            rr = requests.get(f"{GITHUB_API}/users/{username}/repos?per_page=100&sort=updated",
                              headers=_headers(), timeout=REQUEST_TIMEOUT)
            if rr.status_code == 200:
                repos = rr.json()
                repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:5]
                out["top_repos"] = [
                    {"name": x.get("full_name"), "stars": x.get("stargazers_count"),
                     "lang": x.get("language"), "url": x.get("html_url")}
                    for x in repos
                ]
        except Exception:
            pass
    except requests.RequestException as e:
        out["error"] = str(e)
    return out


def print_github_report(username: str):
    info = github_user(username)
    with open(data_path(f"github_{username}.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"[yellow]github_{username}.json saved in Data folder[/yellow]")
    if not info.get("exists"):
        print(f"[red][-][/red] GitHub user '{username}' not found.")
        return info
    print(f"\n[bold cyan]=== GitHub: {username} ===[/bold cyan]")
    for k in ("name", "bio", "company", "location", "email_public", "blog",
              "twitter", "public_repos", "followers", "following", "created_at", "profile"):
        print(f"  {k:13}: {info.get(k)}")
    if info.get("top_repos"):
        print("  top_repos:")
        for r in info["top_repos"]:
            print(f"    - {r['name']} ★{r['stars']} [{r['lang']}] {r['url']}")
    return info


if __name__ == "__main__":
    u = input("GitHub username: ").strip()
    print_github_report(u)
