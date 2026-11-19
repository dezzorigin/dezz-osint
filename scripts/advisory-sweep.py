#!/usr/bin/env python3
"""Sweep dependensi produksi dezz-osint terhadap OSV (Open Source Vulnerabilities).

Pola repo #24-#43: 1 POST ke api.osv.dev/v1/querybatch untuk semua paket
produksi. JANGAN ganti ke `npm audit` (melaporkan advisory dev-only
sebagai temuan produksi) atau ke GitHub Advisory DB API + GITHUB_TOKEN
(401 deterministik di CI).

Repo ini (CLI Python + MCP) punya 13 dependensi produksi, semuanya
dipin == di requirements.txt (versi terbaru PyPI 19 Nov 2026) — dan
itulah yang di-sweep di sini, ekosistem PyPI.

Usage:
    python3 scripts/advisory-sweep.py
No token needed. Exit code 0 = production tree clean, 1 = findings,
2 = API error.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

SEVERITIES = ("HIGH", "CRITICAL")
OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"


def load_prod_packages(req_path):
    """name -> sorted list of versions, dari pin == di requirements.txt."""
    prod = {}
    if not os.path.exists(req_path):
        return prod
    with open(req_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            m = re.match(r"^([A-Za-z0-9_.-]+)==([^\s;]+)", line)
            if m:
                prod.setdefault(m.group(1).lower(), set()).add(m.group(2))
    return {name: sorted(vers) for name, vers in sorted(prod.items())}


def severity_of(vuln):
    ds = vuln.get("database_specific") or {}
    sev = (ds.get("severity") or "").upper()
    if sev in ("CRITICAL", "HIGH", "MODERATE", "LOW"):
        return sev
    for entry in vuln.get("severity", []) or []:
        try:
            score = float(entry.get("score", ""))
        except (TypeError, ValueError):
            continue
        if score >= 9.0:
            return "CRITICAL"
        if score >= 7.0:
            return "HIGH"
        if score >= 4.0:
            return "MODERATE"
        return "LOW"
    return None


def query_osv(queries):
    body = json.dumps({"queries": queries}).encode()
    req = urllib.request.Request(
        OSV_BATCH_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.build_opener().open(req, timeout=120) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read()[:500].decode("utf-8", "replace")
        print(f"ERROR: OSV API {e.code}: {detail}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: OSV request gagal: {e}", file=sys.stderr)
        return None


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prod = load_prod_packages(os.path.join(root, "requirements.txt"))
    if not prod:
        print("ERROR: tidak ada dependensi produksi terp pin di requirements.txt")
        return 2
    queries = []
    for name, vers in prod.items():
        for v in vers:
            queries.append({"package": {"name": name, "ecosystem": "PyPI"}, "version": v})
    print(f"sweep {len(queries)} paket: {', '.join(f'{n}=={v}' for n, vs in prod.items() for v in vs)}")
    data = query_osv(queries)
    if data is None:
        return 2
    results = data.get("results", [])
    findings = []
    for q, res in zip(queries, results):
        for vuln in res.get("vulns", []) or []:
            sev = severity_of(vuln)
            if sev in SEVERITIES:
                findings.append((q["package"]["name"], q["version"], vuln.get("id"), sev))
    if findings:
        print(f"FAIL: {len(findings)} temuan HIGH/CRITICAL:")
        for name, ver, vid, sev in findings:
            print(f"  {sev} {name}=={ver} {vid}")
        return 1
    print("OK: production tree bersih (tanpa HIGH/CRITICAL di OSV)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
