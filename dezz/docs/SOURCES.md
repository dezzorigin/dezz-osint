# SOURCES — verdict live-test per repo upstream (no dummy)

Legenda: ✅ wired (lolos live-test) · ⚠️ honest-gated (jujur butuh syarat) · 📚 knowledge/docs · ❌ ditolak (terbukti mati)

## Batch 1
| Repo | Peran di dezz | Verdict |
|---|---|---|
| pwnxotus/DIGI-NETRA | fast engines (vendored `dezz/engines/`) | ✅ 5/5 inti work; modul mati dihapus |
| soxoj/maigret | `username --engine maigret` (deep scan + parse JSON) | ✅ installed & tested |
| smicallef/spiderfoot | `sf` module search + verified scan cmd | ✅ katalog 200+ real |
| jivoi/awesome-osint | resources catalog (1444) | ✅ merged → 3793 |

## Batch 2
| Repo | Peran di dezz | Verdict |
|---|---|---|
| laramies/theHarvester | — (tidak di-wire) | ❌ HEAD upstream syntax error (`except A, B`) + butuh Python ≥3.14 (kita 3.12). Sumber gratisnya (crt.sh) sudah dicover `domaincheck` |
| s0md3v/Photon | `crawl` + MCP `web_crawl` (Photon asli bila checkout ada, fallback crawler bawaan — keduanya real) | ✅ plugin `--wayback` mati upstream → tidak dipakai |
| yt-dlp | `dl` + MCP `media_download` (probe info + download mp4/mp3, 1000+ situs) | ✅ probe + download live-tested |
| dezzorigin/DezDownload | `server/` dezz-extract backend pengganti Cobalt (drop-in `POST /`) | ✅ endpoint live-tested; Cobalt publik mati (`auth.jwt.missing`) |
| DedSecInside/TorBot | `tor` status gate | ⚠️ butuh Tor service (tidak ada di env ini) — menolak fake scan |
| cipher387/osint_stuff_tool_collection | — | ❌ format tweet-digest/HTML, yield rendah, tidak kompatibel parser |
| Astrosp/Awesome-OSINT-List | resources catalog | ✅ merged |
| apurvsinghgautam/robin | — (docs only) | ⚠️ butuh Tor + LLM API key, tak bisa live-test — pola MCP-nya jadi referensi |
| TermuxHackz/X-osint | — (tidak di-wire) | ❌ aplikasi tkinter GUI, tak bisa headless; ide EXIF diimplementasi ulang bersih di `engines/image_exif.py` |
| Alfredredbird/tookie-osint | `username --engine tookie` (real subprocess, 262 sites) | ✅ tested (39 hits utk `torvalds`) |
| Ph055a/OSINT_Collection | resources catalog | ✅ merged |
| elementalsouls/Claude-OSINT | knowledge (skills markdown, bukan executable) | 📚 metodologi, dirujuk di README |

Total katalog resources: **3793** (jivoi 1444 + astrosp/ph055a 2349, dedupe by URL).
MCP tools: **12** (10 lama + `web_crawl`, `image_exif`).
