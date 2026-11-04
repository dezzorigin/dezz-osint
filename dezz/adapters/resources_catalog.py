"""awesome-osint resources catalog — parsed from jivoi/awesome-osint README.

1444 entries, offline searchable. Used by CLI `resources` + MCP tool.
Source of truth: dezz/resources_catalog.json (built at setup).
"""
from __future__ import annotations
import json
from pathlib import Path

_CATALOG = Path(__file__).parent.parent / "resources_catalog.json"


def _load() -> list:
    try:
        return json.loads(_CATALOG.read_text(encoding="utf-8"))
    except Exception:
        return []


def search(query: str, category: str = "", limit: int = 20) -> list:
    q = (query or "").lower().strip()
    c = (category or "").lower().strip()
    out = []
    for e in _load():
        if c and c not in e.get("category", "").lower():
            continue
        hay = f"{e.get('name','')} {e.get('note','')} {e.get('category','')} {e.get('url','')}".lower()
        if not q or q in hay:
            out.append(e)
        if len(out) >= limit:
            break
    return out


def categories() -> list:
    cats = {}
    for e in _load():
        cats[e.get("category", "?")] = cats.get(e.get("category", "?"), 0) + 1
    return sorted(cats.items(), key=lambda x: -x[1])


def count() -> int:
    return len(_load())
