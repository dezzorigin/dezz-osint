#!/usr/bin/env python3
"""dezz-osint — unified OSINT CLI. Only wired engines are live-tested.

  phone     offline number intel (carrier/region/E164/wa.me) — always works
  username  fast candidates + GitHub | --engine maigret (deep) | --engine tookie (262 sites)
  email     MX + Gravatar + Firefox + HudsonRock breach — all live-tested
  ip        geo/ISP via ip-api (no key)
  domain    DNS-over-HTTPS + crt.sh subdomains + RDAP
  url       headers + Wayback | crawl = REAL Photon crawl (deep)
  exif      image metadata/GPS (local file or URL)
  tor       TorBot status (needs Tor service; honest gate, no fake scans)
  github    public API enrichment
  dossier   kupas tuntas: tebak jenis target, jalankan semua yang cocok, simpan JSON
  resources search awesome-osint catalog (1444 entries)
  sf        pindai website menyeluruh (koleksi SpiderFoot, jalan manual)
  mcp       start MCP server (stdio)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rich import print as rprint
from rich.table import Table
from dezz.config import VERSION

BANNER = f"[bold magenta]dezz-osint v{VERSION}[/bold magenta] · tested engines only"


HACK = "#00ff00"


def _center(lines, color="bold magenta"):
    import shutil
    w = shutil.get_terminal_size((80, 24)).columns
    for ln in lines:
        pad = max(0, (w - len(ln)) // 2)
        rprint(f"[{color}]{' ' * pad}{ln}[/]")


def _figlet():
    """Font terbesar yang muat di lebar terminal (tinggi max 12 baris)."""
    import shutil
    size = shutil.get_terminal_size((80, 24))
    try:
        from pyfiglet import figlet_format
        for font in ("bloody", "graffiti", "doom", "banner", "big", "slant", "standard"):
            try:
                art = figlet_format("DEZZ OSINT", font=font).rstrip("\n").splitlines()
            except Exception:
                continue
            if art and len(art) <= 12 and max(map(len, art)) <= size.columns - 2:
                return art
    except Exception:
        pass
    return ["DEZZ OSINT"]


def _hacker_reveal(lines, color=HACK):
    """Efek decrypt: tiap baris di-scramble acak lalu resolve. Non-TTY = cetak biasa."""
    import random
    import shutil
    import sys as _s
    import time as _t
    glyphs = "!<>-_\\/[]{}=+*^?#01"
    w = shutil.get_terminal_size((80, 24)).columns
    for ln in lines:
        pad = max(0, (w - len(ln)) // 2)
        if not _s.stdout.isatty():
            rprint(f"[bold {color}]{' ' * pad}{ln}[/]")
            continue
        n_scramble = 2 if len(lines) > 7 else 3
        for _ in range(n_scramble):
            scr = "".join(c if c == " " else random.choice(glyphs) for c in ln)
            _s.stdout.write(f"\r\x1b[1;32m{' ' * pad}{scr}\x1b[0m")
            _s.stdout.flush()
            _t.sleep(0.04)
        _s.stdout.write(f"\r\x1b[1;32m{' ' * pad}{ln}\x1b[0m\n")
    _s.stdout.flush()


def show_banner():
    """Banner ASCII hijau hacker, tengah, tanpa kotak panel."""
    _hacker_reveal(_figlet())
    _center([f"dezz-osint v{VERSION} · passive OSINT toolkit"], color="white")
    _center(["pasif — hanya untuk data sendiri / atas izin"], color="#a1a1aa")
    rprint()


MENU = [
    ("run", "Cari tahu segalanya tentang satu target"),
    ("phone", "Lacak nomor HP tak dikenal"),
    ("username", "Cari username di seluruh internet"),
    ("email", "Cek apakah email pernah bocor"),
    ("ip", "Lacak lokasi sebuah IP"),
    ("domain", "Intip data sebuah website"),
    ("url", "Cek keamanan sebuah link"),
    ("crawl", "Sedot semua isi website"),
    ("dl", "Download video/musik (1000+ situs)"),
    ("exif", "Bedah foto (kamera dan lokasi)"),
    ("github", "Intip akun GitHub seseorang"),
    ("resources", "Cari tools OSINT lainnya"),
    ("sf", "Pindai website menyeluruh"),
    ("tor", "Cek koneksi Tor"),
]

PROMPTS = {
    "run": "Tempel targetnya (nomor / username / email / IP / domain): ",
    "phone": "Nomor HP-nya (mis. +62812...): ",
    "username": "Username-nya: ",
    "email": "Email-nya: ",
    "ip": "IP-nya (mis. 8.8.8.8): ",
    "domain": "Website-nya (mis. example.com): ",
    "url": "Link-nya (mis. https://...): ",
    "crawl": "Website yang mau disedot: ",
    "dl": "Link video/musiknya: ",
    "exif": "File foto / link foto: ",
    "github": "Username GitHub-nya: ",
    "resources": "Mau cari tools tentang apa: ",
    "sf": "Mau gali info apa? (mis. subdomain) — kosong = rancang pemindaian: ",
}


QUIT = ("__quit__", "Keluar")

# True jika engine baru saja dijalankan (diset di _jalan) — dipakai main loop
# untuk jeda konfirmasi sebelum balik ke menu.
_BARU_JALAN = False


def _arrow_pick(options):
    """Menu polos bernomor — rapi tanpa kotak, sama di semua terminal.

    Balik: index pilihan, atau None kalau keluar.
    """
    options = list(options) + [QUIT]
    rprint()
    rprint("[bold green]Mau ngapain?[/bold green]")
    for i, (_, desc) in enumerate(options, 1):
        if desc == "Keluar":
            rprint(f"  [dim]{i:>2}. {desc}[/dim]")
        else:
            rprint(f"  [cyan]{i:>2}[/cyan]. {desc}")
    try:
        raw = input("Ketik nomor: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
    if not raw.isdigit():
        return None
    n = int(raw)
    if 1 <= n <= len(options):
        return None if options[n - 1][0] == "__quit__" else n - 1
    rprint("[red]Nomor tidak ada, coba lagi.[/red]")
    return -99


def _tunggu_kembali():
    """Jeda konfirmasi: hasil dibaca dulu, Enter baru balik ke menu.

    Dilewati otomatis kalau input bukan terminal (pipe/test).
    """
    if not sys.stdin.isatty():
        return
    try:
        rprint("[dim]Tekan Enter untuk kembali...[/dim]", end=" ")
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    rprint()


PANJANG_BATAS = 30  # di atas ini ditanya: tampil di sini atau .md


def _simpan_md(target: str, sections: list) -> Path:
    """Simpan hasil sebagai laporan .md yang enak dibaca. Return path."""
    from datetime import datetime
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in target)[:60] or "hasil"
    p = Path(__file__).resolve().parent.parent / "Data" / f"dezz_{safe}.md"
    p.parent.mkdir(exist_ok=True)
    isi = [f"# Hasil dezz-osint: {target}", "",
           f"_Dibuat: {datetime.now().strftime('%Y-%m-%d %H:%M')}_", ""]
    for judul, teks in sections:
        isi += [f"## {judul}", "", teks, ""]
    p.write_text("\n".join(isi), encoding="utf-8")
    return p


def _keluarkan(judul: str, teks: str, target: str = ""):
    """Tampilkan hasil teks; kalau panjang, tanya: di sini atau .md?

    Tidak pernah cetak JSON mentah ke layar.
    """
    baris = teks.splitlines()
    lines = [l for l in baris if l.strip()]
    if len(lines) <= PANJANG_BATAS or not sys.stdin.isatty():
        rprint(f"\n[bold green]{judul}[/bold green]")
        rprint(teks)
        return
    rprint(f"\n[yellow]Hasil panjang ({len(lines)} baris).[/yellow]")
    try:
        pilih = input("[1] tampilkan di sini / [2] simpan .md / [3] keduanya (default 1): ").strip() or "1"
    except (EOFError, KeyboardInterrupt):
        pilih = "1"
    if pilih in ("2", "3"):
        p = _simpan_md(target or judul, [(judul, teks)])
        rprint(f"[green]tersimpan: {p}[/green]")
    if pilih in ("1", "3"):
        rprint(f"\n[bold green]{judul}[/bold green]")
        rprint(teks)


def _jalan(lagi_apa, fn):
    """Bungkus engine: loading bar hacker + kabar selesai + durasi."""
    global _BARU_JALAN
    _BARU_JALAN = True
    import sys as _s
    import threading
    import time as _t
    if not _s.stdout.isatty():
        rprint(f"\n[yellow]Lagi jalan: {lagi_apa} ...[/yellow]")
        t0 = _t.time()
        try:
            fn()
        except KeyboardInterrupt:
            rprint("[red]Diberhentikan.[/red]")
        rprint(f"[green]Selesai dalam {_t.time() - t0:.1f} detik.[/green]\n")
        return
    stop = []
    t0 = _t.time()

    def spin():
        w, pos, d = 14, 0, 1
        while not stop:
            cells = ["-"] * w
            cells[pos] = "#"
            _s.stdout.write(
                f"\r\x1b[1;32m[ {''.join(cells)} ] {lagi_apa} {_t.time() - t0:.1f}s\x1b[0m")
            _s.stdout.flush()
            pos += d
            if pos in (0, w - 1):
                d *= -1
            _t.sleep(0.08)

    th = threading.Thread(target=spin, daemon=True)
    th.start()
    try:
        fn()
    except KeyboardInterrupt:
        stop.append(1)
        th.join(timeout=0.3)
        _s.stdout.write("\r\x1b[J")
        rprint("[red]Diberhentikan.[/red]")
        return
    stop.append(1)
    th.join(timeout=0.3)
    _s.stdout.write("\r\x1b[J")
    _s.stdout.flush()
    rprint(f"[bold #00ff00][OK] Selesai dalam {_t.time() - t0:.1f} detik.[/]\n")


def _menu_cari_segala():
    """Submenu #1: pilih mau cari apa + dikasih tahu formatnya, baru jalan."""
    from argparse import Namespace
    rprint()
    rprint("[bold green]Mau cari apa?[/bold green]")
    opsi = [
        ("phone", "Nomor HP", "cth: +62812xxxxxxx"),
        ("username", "Username", "cth: torvalds"),
        ("email", "Email", "cth: nama@gmail.com"),
        ("ip", "Alamat IP", "cth: 8.8.8.8"),
        ("domain", "Website / domain", "cth: example.com"),
        ("url", "Link lengkap", "cth: https://example.com/artikel"),
        ("github", "Akun GitHub", "cth: torvalds"),
        ("dl", "Download video/musik", "cth: link youtube/tiktok"),
        ("exif", "Foto", "file lokal / link gambar"),
        ("auto", "Bingung — tebakkan otomatis", "tempel apa saja"),
    ]
    for i, (_, nama, cth) in enumerate(opsi, 1):
        rprint(f"  [cyan]{i:>2}[/cyan]. {nama} [dim]({cth})[/dim]")
    try:
        raw = input("Ketik nomor: ").strip()
    except (EOFError, KeyboardInterrupt):
        return True
    if not raw.isdigit() or not 1 <= int(raw) <= len(opsi):
        rprint("[yellow]Batal — balik ke menu.[/yellow]")
        return True
    pilih = opsi[int(raw) - 1][0]
    if pilih == "username":
        target = input("Username-nya: ").strip()
        if not target:
            return True
        eng = input("Seberapa dalam? [1=cepat / 2=dalam-maigret / 3=lebar-tookie] (default 1): ").strip() or "1"
        eng = {"1": "fast", "2": "maigret", "3": "tookie"}.get(eng, "fast")
        _jalan(f"mencari '{target}' di internet",
               lambda: cmd_username(Namespace(target=target, engine=eng, deep=(eng == "maigret"))))
        return True
    FORMAT = {
        "phone": "Nomor HP-nya (cth +62812...): ",
        "email": "Email-nya (cth nama@gmail.com): ",
        "ip": "IP-nya (cth 8.8.8.8): ",
        "domain": "Website-nya (cth example.com): ",
        "url": "Link-nya (cth https://...): ",
        "github": "Username GitHub-nya: ",
        "dl": "Link video/musiknya: ",
        "exif": "File foto / link foto: ",
        "auto": "Tempel targetnya: ",
    }
    target = input(FORMAT[pilih]).strip()
    if not target:
        rprint("[yellow]Kosong — balik ke menu.[/yellow]")
        return True
    calls = {
        "phone": lambda: cmd_phone(Namespace(target=target)),
        "email": lambda: cmd_email(Namespace(target=target)),
        "ip": lambda: cmd_ip(Namespace(target=target)),
        "domain": lambda: cmd_domain(Namespace(target=target)),
        "url": lambda: cmd_url(Namespace(target=target)),
        "github": lambda: cmd_github(Namespace(target=target)),
        "dl": lambda: cmd_dl(Namespace(target=target, mode="")),
        "exif": lambda: cmd_exif(Namespace(target=target)),
        "auto": lambda: cmd_dossier(Namespace(target=target, deep_username=False)),
    }
    _jalan(f"memproses '{target}'", calls[pilih])
    return True


def interactive_menu():
    """Menu utama. Returns False kalau user keluar."""
    from argparse import Namespace
    idx = _arrow_pick(MENU)
    if idx is None:
        return False
    if idx == -99:
        rprint("[red]Nomor tidak ada, coba lagi.[/red]")
        return True
    cmd = MENU[idx][0]
    try:
        if cmd == "run":
            return _menu_cari_segala()
        if cmd == "username":
            target = input(PROMPTS["username"]).strip()
            if not target:
                return True
            eng = input("Seberapa dalam? [1=cepat / 2=dalam / 3=lebar] (default 1): ").strip() or "1"
            eng = {"1": "fast", "2": "maigret", "3": "tookie"}.get(eng, "fast")
            _jalan(f"mencari '{target}' di internet",
                   lambda: cmd_username(Namespace(target=target, engine=eng, deep=(eng == "maigret"))))
            return True
        if cmd == "resources":
            kw = input(PROMPTS["resources"]).strip()
            _jalan(f"mencari tools tentang '{kw}'",
                   lambda: cmd_resources(Namespace(target=kw, category="", limit=20)))
            return True
        if cmd == "sf":
            kw = input(PROMPTS["sf"]).strip()
            if kw:
                _jalan(f"mencari alat pemindai '{kw}'",
                       lambda: cmd_sf(Namespace(target="", search=kw)))
            else:
                target = input("Website yang mau dipindai: ").strip()
                if not target:
                    return True
                _jalan(f"merancang pemindaian untuk '{target}'",
                       lambda: cmd_sf(Namespace(target=target, search="")))
            return True
        if cmd == "tor":
            _jalan("mengecek koneksi Tor", lambda: cmd_tor(Namespace(target="")))
            return True
        target = input(PROMPTS[cmd]).strip()
        if not target:
            rprint("[yellow]Kosong — balik ke menu.[/yellow]")
            return True
        calls = {
            "phone": lambda: cmd_phone(Namespace(target=target)),
            "email": lambda: cmd_email(Namespace(target=target)),
            "ip": lambda: cmd_ip(Namespace(target=target)),
            "domain": lambda: cmd_domain(Namespace(target=target)),
            "url": lambda: cmd_url(Namespace(target=target)),
            "github": lambda: cmd_github(Namespace(target=target)),
            "crawl": lambda: cmd_crawl(Namespace(target=target)),
            "dl": lambda: cmd_dl(Namespace(target=target)),
            "exif": lambda: cmd_exif(Namespace(target=target)),
            "run": lambda: cmd_dossier(Namespace(target=target, deep_username=False)),
        }
        _jalan(f"memproses '{target}'", calls[cmd])
    except (EOFError, KeyboardInterrupt):
        rprint("\n[yellow]Balik ke menu.[/yellow]")
    return True


def cmd_phone(a):
    from dezz.engines.phone_offline import print_phone_report
    from dezz.engines.Numbercheck import search_google
    print_phone_report(a.target)
    search_google(a.target)  # runs only if GOOGLE_API_KEY+CX set, else honest SKIP


def cmd_username(a):
    from dezz.adapters.maigret_adapter import search, is_available
    from dezz.engines.githubcheck import print_github_report
    eng = (a.engine or ("maigret" if a.deep else "fast")).lower()
    if eng == "tookie":
        from dezz.adapters.tookie_adapter import scan as tookie_scan
        rprint(f"[bold green]Hasil username ({eng}): {a.target}[/bold green]")
        try:
            r = tookie_scan(a.target)
        except RuntimeError as e:
            rprint(f"[yellow]{e}[/yellow]")
            return
        baris = [f"{r.get('count', 0)} kandidat ([?] = belum terverifikasi, cek manual):"]
        baris += [f"  [?] {f['url']}" for f in (r.get("candidates_unverified") or [])[:40]]
        gh = print_github_text(a.target)
        if gh:
            baris += ["", gh]
        _keluarkan(f"Hasil username: {a.target}", "\n".join(baris), a.target)
        return
    if eng == "maigret" or a.deep:
        rprint(f"[bold green]Hasil username (maigret): {a.target}[/bold green]")
        r = search(a.target, deep=True)
        baris = [f"{r.get('count', 0)} profil diklaim:"]
        baris += [f"  [+] {f['site']}: {f['url']}" for f in (r.get("found") or [])[:40]]
        gh = print_github_text(a.target)
        if gh:
            baris += ["", gh]
        _keluarkan(f"Hasil username: {a.target}", "\n".join(baris), a.target)
        return
    rprint(f"[bold green]Hasil username (cepat): {a.target}[/bold green]")
    r = search(a.target, deep=False)
    baris = []
    for f in (r.get("verified") or []):
        baris.append(f"  [verified] {f['site']}: {f['url']}")
    cands = r.get("candidates_unverified") or []
    baris.append(f"{len(cands)} kandidat (konfirmasi manual):")
    baris += [f"  [?] {f['site']}: {f['url']}" for f in sorted(cands, key=lambda x: x["site"])[:30]]
    gh = r.get("github") or {}
    if gh.get("exists"):
        baris += ["", f"GitHub terverifikasi: {gh.get('name')} · {gh.get('followers')} followers · {gh.get('profile')}"]
    _keluarkan(f"Hasil username: {a.target}", "\n".join(baris), a.target)
    _ = is_available()


def print_github_text(username: str) -> str:
    """Ringkasan GitHub sebagai teks (bukan cetak langsung)."""
    from dezz.engines.githubcheck import github_user
    try:
        gh = github_user(username.lstrip("@"))
    except Exception:
        return ""
    if not gh.get("exists"):
        return "GitHub: akun tidak ada"
    return (f"GitHub terverifikasi: {gh.get('name')} · "
            f"{gh.get('followers')} followers · {gh.get('profile')}")


def cmd_email(a):
    from dezz.mcp.tools import _firefox_status, _hudson
    from dezz.engines.email_ext import analyze_email
    info = analyze_email(a.target)
    info["firefox"] = _firefox_status(a.target)
    info["hudson_rock"] = _hudson(a.target)
    b = [f"Email: {a.target}",
         f"format: {'ok' if info.get('valid_format') else 'aneh'}"]
    mx = info.get("mx_records") or []
    b.append(f"server mail: {mx[0] if mx else 'tidak ketemu'}")
    g = info.get("gravatar") or {}
    if g.get("registered"):
        b.append(f"Gravatar: {g.get('username') or 'terdaftar'}")
    ff = info.get("firefox") or {}
    if ff.get("checked"):
        b.append(f"Firefox: {'terdaftar' if ff.get('exists') else 'tidak terdaftar'}")
    hr = info.get("hudson_rock") or {}
    if hr.get("checked"):
        b.append(f"breach: {'BOCOR — ganti password!' if hr.get('compromised') else 'bersih'}")
    if hr.get("compromised"):
        b.append("BAHAYA: email ini muncul di log pencuri info (stealer).")
    _keluarkan(f"Hasil email: {a.target}", "\n".join(b), a.target)


def cmd_ip(a):
    from dezz.engines.ipcheck import lookup_ip
    d = lookup_ip(a.target)
    if d.get("error"):
        rprint(f"[red]Gagal: {d['error']}[/red]")
        return
    teks = (f"IP: {d.get('ip')}\n"
            f"lokasi: {d.get('city', '?')}, {d.get('region', '?')}, {d.get('country', '?')}\n"
            f"koordinat: {d.get('lat')}, {d.get('lon')}\n"
            f"ISP: {d.get('isp', '?')}\n"
            f"organisasi: {d.get('org', '?')}")
    _keluarkan(f"Hasil IP: {d.get('ip')}", teks, a.target)


def cmd_domain(a):
    from dezz.engines.domaincheck import print_domain_report
    print_domain_report(a.target)


def cmd_url(a):
    from dezz.engines.urlcheck import print_url_report
    print_url_report(a.target)


def cmd_github(a):
    from dezz.engines.githubcheck import print_github_report
    print_github_report(a.target)


def _tampil_hasil(rep):
    """Tampilkan SEMUA temuan langsung di terminal, rapi per engine.

    JSON lengkap tetap tersimpan sebagai arsip — tapi yang utama dibaca
    di sini, bukan di file.
    """
    LABEL = {"phone": "Nomor HP", "username": "Username", "github": "GitHub",
             "email": "Email", "ip": "Lokasi IP", "domain": "Website",
             "url": "Link", "exif": "Foto"}

    def s_phone(d):
        if not d.get("valid"):
            return "nomor tidak valid"
        baris = [f"{d.get('international', '')}",
                 f"operator: {d.get('carrier') or '?'} · daerah: {d.get('region') or '?'}",
                 f"E164: {d.get('e164_format', '')}"]
        e164 = (d.get("e164_format") or "").lstrip("+")
        if e164:
            baris.append(f"wa.me/{e164} · t.me/+{e164}")
        return "\n".join(baris)

    def s_username(d):
        v = d.get("verified") or []
        c = d.get("candidates_unverified") or []
        found = d.get("found") or []  # maigret deep
        baris = []
        for f in found[:10]:
            baris.append(f"  [+] {f.get('site')}: {f.get('url')}")
        for f in v[:10]:
            baris.append(f"  [+] {f.get('site')}: {f.get('url')}")
        for f in c[:8]:
            baris.append(f"  [?] {f.get('site')}: {f.get('url')}")
        total = d.get("count", len(found) + len(v) + len(c))
        head = f"{total} cocok"
        if c and not found:
            head += " ([?] = kandidat, konfirmasi manual)"
        return head + ("\n" + "\n".join(baris) if baris else "")

    def s_github(d):
        if not d.get("exists"):
            return "akun tidak ada"
        baris = [f"{d.get('name') or d.get('username')}",
                 f"{d.get('followers')} followers · {d.get('public_repos')} repo"]
        if d.get("location"):
            baris.append(f"lokasi: {d.get('location')}")
        for r in (d.get("top_repos") or [])[:3]:
            baris.append(f"  ★ {r.get('name')} ({r.get('lang')})")
        baris.append(d.get("profile") or "")
        return "\n".join(x for x in baris if x)

    def s_email(d):
        b = ["format ok" if d.get("valid_format") else "format aneh"]
        mx = d.get("mx_records") or []
        if mx:
            b.append(f"server mail: {mx[0]}")
        g = d.get("gravatar") or {}
        if g.get("registered"):
            b.append(f"Gravatar: {g.get('username') or 'terdaftar'}")
        ff = d.get("firefox") or {}
        if ff.get("checked"):
            b.append("Firefox: terdaftar" if ff.get("exists") else "Firefox: tidak terdaftar")
        hr = d.get("hudson_rock") or {}
        if hr.get("checked"):
            b.append("breach: BERSIH" if not hr.get("compromised") else "breach: BOCOR")
        if hr.get("compromised"):
            b.append("BAHAYA: muncul di log pencuri info — ganti password")
        return "\n".join(b)

    def s_ip(d):
        if d.get("error"):
            return str(d["error"])[:120]
        return (f"{d.get('city', '?')}, {d.get('country', '?')}\n"
                f"ISP: {d.get('isp', '?')}\n"
                f"koordinat: {d.get('lat')}, {d.get('lon')}")

    def s_domain(d):
        baris = [f"A: {'; '.join((d.get('A') or [])[:3]) or '?'}"]
        if d.get("MX"):
            baris.append(f"MX: {'; '.join(d['MX'][:2])}")
        subs = d.get("subdomains_crtsh") or []
        baris.append(f"subdomain crt.sh ({len(subs)}):")
        baris += [f"  - {s}" for s in subs[:12]]
        if len(subs) > 12:
            baris.append(f"  ... +{len(subs) - 12} lagi (lengkap di JSON)")
        return "\n".join(baris)

    def s_url(d):
        baris = [f"{d.get('status')} {d.get('final_url', '')}",
                 f"server: {d.get('server') or '?'}"]
        if d.get("title_hint"):
            baris.append(f"judul: {d['title_hint']}")
        if d.get("wayback_note"):
            baris.append(f"arsip: {d['wayback_note']}")
        return "\n".join(baris)

    def s_generic(d):
        if isinstance(d, dict):
            items = [(k, v) for k, v in d.items() if isinstance(v, (str, int, float, bool))][:5]
            return "\n".join(f"{k}: {v}" for k, v in items) or "(detail di file JSON)"
        return str(d)[:200]

    FUN = {"phone": s_phone, "username": s_username, "github": s_github,
           "email": s_email, "ip": s_ip, "domain": s_domain, "url": s_url}
    sections = []
    for eng in ("phone", "username", "github", "email", "ip", "domain", "url", "exif"):
        res = rep["engines"].get(eng)
        if not res or not res.get("ok"):
            continue
        try:
            sections.append((LABEL[eng], FUN.get(eng, s_generic)(res.get("data") or {})))
        except Exception:
            continue
    res = rep["engines"].get("resources_hint")
    data = (res.get("data") or []) if res else []
    if data:
        refs = []
        for e in data[:3]:
            if isinstance(e, dict):
                refs.append(f"  - {e.get('name')}: {e.get('url')}")
            elif isinstance(e, (list, tuple)) and len(e) >= 3:
                refs.append(f"  - {e[1]}: {e[2]}")
        if refs:
            sections.append(("Referensi", "\n".join(refs)))
    if not sections:
        rprint("[yellow]Tidak ada temuan.[/yellow]")
        return
    teks = ""
    for judul, isi in sections:
        teks += f"\n-- {judul} --\n{isi}\n"
    _keluarkan(f"Hasil kupas tuntas: {rep.get('target', '')}", teks.strip(), rep.get("target", ""))


def cmd_dossier(a):
    from dezz.orchestrator import dossier, save_report
    rprint(f"[bold green]Kupas tuntas: {a.target}[/bold green]")
    rep = dossier(a.target, deep_username=a.deep_username)
    p = save_report(rep)
    _tampil_hasil(rep)
    rprint(f"[dim]arsip JSON: {p}[/dim]")


def cmd_resources(a):
    from dezz.adapters.resources_catalog import search, count
    res = search(a.target or "", a.category or "", a.limit)
    t = Table(title=f"awesome-osint ({count()} total, showing {len(res)})")
    t.add_column("Category"); t.add_column("Name"); t.add_column("URL")
    for e in res:
        t.add_row(e["category"], e["name"], e["url"])
    rprint(t)


def cmd_sf(a):
    from dezz.adapters.spiderfoot_adapter import build_scan_cmd, status, search_modules
    if a.search:
        res = search_modules(a.search)
        t = Table(title=f"Alat pemindai buat '{a.search}' ({len(res)})")
        t.add_column("Kode"); t.add_column("Nama"); t.add_column("Fungsi")
        for m in res:
            t.add_row(m["module"], m["name"], m["summary"][:90])
        rprint(t)
        return
    st = status()
    rprint(f"koleksi alat siap: [bold]{st['module_count']}[/bold]")
    rprint(json.dumps(build_scan_cmd(a.target), indent=2))


def cmd_crawl(a):
    from dezz.adapters.photon_adapter import crawl
    rprint(f"[bold green]Menyedot: {a.target}[/bold green]")
    try:
        r = crawl(a.target)
    except RuntimeError as e:
        rprint(f"[yellow]{e}[/yellow]")
        return
    for k in ("internal", "external", "scripts", "files", "endpoints"):
        if r.get(k + "_count"):
            rprint(f"[green]{k}: {r[k+'_count']}[/green]")
            for u in (r.get(k) or [])[:15]:
                rprint(f"  - {u}")


def cmd_exif(a):
    from dezz.engines.image_exif import print_image_report
    print_image_report(a.target)


def cmd_tor(a):
    from dezz.adapters.torbot_adapter import status
    rprint(json.dumps(status(), indent=2))


def cmd_dl(a):
    from dezz.engines.media_dl import probe, download
    url = (a.target or "").strip()
    if not url:
        rprint("[yellow]Kosong — balik ke menu.[/yellow]")
        return
    info = probe(url)
    if info.get("error"):
        rprint(f"[red]Gagal: {info['error']}[/red]")
        return
    rprint(f"\n[bold green]{info.get('title')}[/bold green]")
    rprint(f"  situs: {info.get('site')} · uploader: {info.get('uploader') or '?'}")
    rprint(f"  durasi: {info.get('duration')} · video: {'ya' if info.get('has_video') else 'tidak'} · audio: {'ya' if info.get('has_audio') else 'tidak'}")
    mode = getattr(a, "mode", "") or ""
    if not mode:
        if not sys.stdin.isatty():
            rprint("[dim]mode info saja (jalan non-interaktif). Pakai: dezz dl <link> --audio / --video[/dim]")
            return
        try:
            mode = input("[1] video mp4 / [2] audio mp3 / [3] info saja (default 1): ").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            return
        mode = {"1": "video", "2": "audio", "3": "info"}.get(mode, "video")
    if mode == "info":
        return
    audio_only = (mode == "audio")
    hasil = download(url, audio_only=audio_only)
    if hasil.get("error"):
        rprint(f"[red]Gagal: {hasil['error']}[/red]")
        return
    rprint(f"[green]tersimpan:[/green] {hasil['file']} ({hasil.get('size_mb')} MB)")


def build_parser():
    p = argparse.ArgumentParser(prog=Path(sys.argv[0]).name, description="dezz-osint — tested engines only")
    sub = p.add_subparsers(dest="cmd", required=False)
    for name in ("phone", "email", "ip", "domain", "url", "github", "dossier", "crawl", "exif", "tor", "run"):
        s = sub.add_parser(name)
        s.add_argument("target", nargs="?", default="")
        s.add_argument("--deep", action="store_true", help="username: real maigret scan")
        s.add_argument("--deep-username", action="store_true", help="kupas tuntas: + scan maigret asli")
    d = sub.add_parser("dl")
    d.add_argument("target", nargs="?", default="")
    d.add_argument("--audio", dest="mode", action="store_const", const="audio", default="",
                   help="download audio mp3")
    d.add_argument("--video", dest="mode", action="store_const", const="video",
                   help="download video mp4")
    d.add_argument("--probe", dest="mode", action="store_const", const="info",
                   help="info saja, tanpa download")
    u = sub.add_parser("username")
    u.add_argument("target")
    u.add_argument("--deep", action="store_true", help="real maigret scan")
    u.add_argument("--engine", default="fast", choices=["fast", "maigret", "tookie"],
                   help="fast=candidates+github, maigret=deep verified, tookie=262-site scan")
    r = sub.add_parser("resources")
    r.add_argument("target", nargs="?", default="")
    r.add_argument("--category", default="")
    r.add_argument("--limit", type=int, default=20)
    s = sub.add_parser("sf")
    s.add_argument("target", nargs="?", default="")
    s.add_argument("--search", default="", help="search module catalog, e.g. --search dns")
    sub.add_parser("mcp")
    return p


def main():
    global _BARU_JALAN
    show_banner()
    args = build_parser().parse_args()
    if not args.cmd:
        while True:
            if not interactive_menu():
                break
            if _BARU_JALAN:
                _BARU_JALAN = False
                _tunggu_kembali()
        return
    if args.cmd in ("run", "dossier") and not (args.target or "").strip():
        rprint("[yellow]Belum ada target — pilih dari menu:[/yellow]")
        while True:
            if not interactive_menu():
                break
            if _BARU_JALAN:
                _BARU_JALAN = False
                _tunggu_kembali()
        return
    {"phone": cmd_phone, "username": cmd_username, "email": cmd_email,
     "ip": cmd_ip, "domain": cmd_domain, "url": cmd_url, "github": cmd_github,
     "dossier": cmd_dossier, "run": cmd_dossier, "resources": cmd_resources, "sf": cmd_sf,
     "crawl": cmd_crawl, "exif": cmd_exif, "tor": cmd_tor, "dl": cmd_dl,
     }.get(args.cmd, lambda a: rprint("see --help"))(args) if args.cmd != "mcp" else None
    if args.cmd == "mcp":
        from dezz.mcp import server as _s
        _s.main()


if __name__ == "__main__":
    main()
