# Testing — dezz-osint

## Yang diuji

Semua tes di `tests/test_cli.py` adalah perilaku yang
terverifikasi live — tanpa mock, tanpa `echo sukses`. Tes yang
butuh jaringan memakai target publik yang stabil (`8.8.8.8`,
`example.com`, `torvalds`).

| Tes | Apa yang dibuktikan |
|---|---|
| `test_cli_help` | `python -m dezz.cli --help` keluar 0 dan memuat sub-perintah |
| `test_cli_phone` | `dezz phone +6281234567890` jalan offline, keluar 0 |
| `test_phone_offline` | `analyze_phone("+6281234567890")["valid"] is True` |
| `test_ip_lookup` | `lookup_ip("8.8.8.8")["country"] == "United States"` |
| `test_github_user` | `github_user("torvalds")["exists"] is True` |
| `test_domain_doh` | `analyze_domain("example.com")["A"]` tidak kosong |
| `test_email_structured` | format ok + Firefox/HudsonRock mengembalikan status `checked` |
| `test_username_fast_honest` | `fast_search("torvalds")` punya `candidates_unverified` + `note` |
| `test_resources_catalog` | katalog >3000 entri, `sherlock` ketemu |
| `test_spiderfoot_real` | 233 modul, `sf --search dns` ketemu, `build_scan_cmd` berisi `sfp_dnsresolve` |
| `test_mcp_tools_list` | server MCP menjawab `tools/list` dengan 13 tool |
| `test_mcp_ip_lookup` | `tools/call ip_lookup 8.8.8.8` → "United States" |
| `test_mcp_image_exif` | `tools/call image_exif` pada JPG GPS → `-6.2` |
| `test_tor_honest` | tanpa Tor: `tor_binary is False`, `runnable is False` |
| `test_exif_gps` | JPG GPS 6°12′S 106°49′E → lat `-6.2` |
| `test_photon_fallback` | crawl example.com: Photon asli atau fallback bawaan, ≥1 halaman |
| `test_tookie_gate` | Tookie ada → scan >0; tidak ada → `RuntimeError` berisi "git clone" |
| `test_no_dead_modules` | modul mati (`idcheck`, `instaemailfind`, …) tidak ada di tree |
| `test_dossier_detects_ip` | `dossier("8.8.8.8")` menjalankan engine `ip` |

## Menjalankan lokal

```bash
pip install -r requirements.txt
pip install pytest
python3 -m pytest tests/test_cli.py -q
```

Tes lama `tests/smoke.py` (skrip `python3 tests/smoke.py`, 17 cek)
tetap ada sebagai arsip perilaku — CI menjalankan pytest.

## CI

Workflow `.github/workflows/ci.yml` (6 job):

1. **ruff** — `ruff check` pada `tests/` + `scripts/` (ketat) dan
   `ruff check --select E9` (syntax) pada `dezz/`.
2. **pytest** — install `requirements.txt` + pytest, jalankan
   `tests/test_cli.py`.
3. **static-checks** — html-validate landing + gate P0 anti-slop +
   tag OG/Twitter (`npm run validate`).
4. **advisory-sweep** — 13 dependensi produksi (pin `==` di
   `requirements.txt`) di-sweep ke OSV; HIGH/CRITICAL = gagal.
5. **playwright-e2e** — landing di server lokal (desktop + mobile
   390px).
6. **smoke** — file deploy ada & tidak kosong.

## Yang TIDAK diuji di VM dev (dan kenapa)

- Install lokal (`pip install .`) tidak dijalankan di VM dev —
  aturan sandbox: proses yang sudah I/O jaringan tidak boleh
  menulis file. Install + tes penuh diandalkan ke CI (runner
  GitHub).
- Screenshot/readme + rekaman terminal = follow-up (butuh browser
  live / VM pulih), bukan gate merge.
