# DESIGN.md — dezz-osint (landing etalase)

Kontrak arah desain landing (ditulis SEBELUM coding, mengikuti
`~/workspace/github-actions/ui-anti-slop.md` §4). Landing ini etalase
untuk CLI Python + server MCP `dezz-osint`, bukan app web pengganti:
yang ditampilkan adalah perintah asli, output asli yang terverifikasi,
dan cara install — produknya tetap jalan di terminal.

## Referensi (tour dulu, baru bangun)

Kebutuhan + keyword: tool OSINT/CLI keamanan untuk investigator,
dipakai analis dan mahasiswa; halaman harus terbaca sebagai berkas
penyelidikan, bukan landing SaaS generik.

Kandidat yang ditour:

1. **Dribbble — "ThreatLens: Enterprise Cybersecurity SaaS Dashboard"
   oleh DIGIMARIX**
   (https://dribbble.com/shots/27543906-ThreatLens-Enterprise-Cybersecurity-SaaS-Dashboard)
   — arsitektur blok data kontras tinggi, tiap blok punya satu aksen
   fungsional, tipografi geometris tegas (Satoshi), hijau keamanan
   sebagai warna sinyal. Cocok: dunia SOC/ops.
2. **Undercurrent — "War Room Admin Console", tema Cybercommand**
   (https://www.undercurrent.ai/guides/mockup-guide.html)
   — stripe severitas di tepi kiri kartu (merah HIGH, amber MEDIUM,
   mint LOW), IBM Plex Mono untuk nuansa pusat operasi, label mode
   yang jujur. Cocok: cap verdict + penanda `[verified]` / `[?]` /
   `[SKIP]` yang sudah jadi bahasa CLI ini.
3. DashboardPack — "Signal Dashboard" (terminal-inspired DevOps,
   JetBrains Mono, dark-first neon green) — DITOLAK: dark + neon
   hijau fosfor = klise orde-kedua (near-black + lime asam) dan
   terlalu mirip template dashboard; tidak ada ruang untuk nuansa
   berkas/investigasi.

**Pemenang: #1 (ThreatLens)**, struktur yang dicloning: grid blok data
dengan satu aksen fungsional per blok + header ringkas berisi status
sistem. Yang diubah: latar gelap SOC diganti **kertas berkas
penyelidikan** (terang, editorial) — karena dunia produk ini bukan
ruang operasi gelap melainkan meja investigator: target ditempel,
benang merah ditarik dari target ke mesin, tiap temuan dicap
verdict-nya. Stripe severitas #2 dipakai sebagai cap verdict di tepi
kartu temuan. Warna hijau neon ThreatLens diganti teal verifikasi
yang kalem — sinyal tetap fungsional, bukan dekorasi neon.

## Palet (6 warna bernama, tiap warna punya tugas)

| Nama | Hex | Peran |
|---|---|---|
| Kertas | `#EFE9DD` | latar halaman — meja berkas, bukan layar gelap |
| Tinta | `#1B1712` | teks utama + judul |
| Sinyal | `#B42318` | merah sinyal — benang merah, CTA utama, temuan breach |
| Teal Verifikasi | `#0F5B5E` | temuan `[verified]`, link, aksen fungsional blok data |
| Kuning Kandidat | `#B7791F` | kandidat `[?]` — belum terverifikasi, cek manual |
| Garis | `#D5CDBD` | garis pemisah / border kartu di atas kertas |

Tidak ada gradient di mana pun. Merah sinyal dan teal tidak pernah
dicampur menjadi gradient — keduanya tampil sebagai bidang solid.
Bukan krim+terracotta (merah sinyal `#B42318` bukan terracotta),
bukan near-black+lime, bukan dark blue/slate.

## Tipografi (2 keluarga)

- **Archivo** (display, 800, tracking rapat) — judul poster berkas,
  angka besar, nama perintah. Rasa arsip investigasi yang tegas.
- **JetBrains Mono** (data/terminal) — perintah, output terminal,
  URL, label mesin, angka. Semua angka memakai
  `font-variant-numeric: tabular-nums`.

## Layout (satu kalimat)

Dossier dua kolom asimetris: rel kiri (sticky) berisi indeks berkas +
cara install, kolom kanan berisi jendela terminal interaktif +
tabel 14 mesin + contoh dossier + MCP — benang merah vertikal
menghubungkan target ke tiap mesin.

## Satu detail khas

**Benang merah + cap verdict**: garis merah solid ditarik dari kartu
target ke tiap kartu mesin/temuan (seperti string board investigasi),
dan tiap temuan dicap stempel miring ber-border tebal —
`[verified]`, `[?]`, atau `[SKIP]` — bahasa cap yang sama persis
dengan output CLI (`[verified]` hanya dari API, `[?]` = kandidat,
`[SKIP]` = butuh kunci/layanan, bukan hasil palsu).

## Geometri

Radius 10px lembut di kartu (bukan 4px tajam repo #43), border solid
1px warna Garis, bayangan tipis satu arah `0 2px 0` warna Garis
(naik 1px saat hover). Grid 8pt; padding kartu minimal 16px; radius
dalam = radius luar − padding.

## Beda dari repo sebelumnya (#43 lyric-popup-kelas-it)

Minimal 3 dari 5 sumbu, di sini 5 dari 5:

| Sumbu | #43 | #44 ini |
|---|---|---|
| Palet | panggung gelap `#171310` + amber sorot + ungu solid | kertas terang `#EFE9DD` + merah sinyal + teal verifikasi |
| Tipografi | Anton + Space Grotesk | Archivo + JetBrains Mono |
| Layout | panggung satu kolom + setlist vertikal | dossier dua kolom asimetris, rel kiri sticky |
| Radius/spacing | 4px tajam + border 3px + bayangan keras | 10px lembut + border 1px + bayangan tipis |
| Detail khas | kotak lirik melayang DVD-bounce + typewriter | benang merah + cap verdict `[verified]`/`[?]`/`[SKIP]` |

## Larangan P0 (dicek `scripts/check-static.mjs`)

Nol gradient, nol headline gradient, bukan Inter/Roboto, bukan hero
tengah + 3 kartu identik, ikon SVG satu bobot (stroke 1.5–2px) bukan
emoji, nol statistik vanity (semua angka di landing adalah angka
nyata repo: 13 tool MCP, 3793 entri katalog, 233 modul SpiderFoot,
14 perintah CLI — semuanya terverifikasi 19 Nov 2026), nol copy
generik, nol `rounded-2xl shadow-lg`, footer satu baris (bukan
4 kolom). Orde-kedua: bukan krim+terracotta, bukan near-black+lime,
label mono all-caps hanya satu kicker, tanpa hiasan 01/02/03, palet
multi-hue (bukan satu hue), bukan dark blue/slate.

## Gate 7 sumbu (nilai sendiri sebelum merge, tiap sumbu minimal 4/5)

1. anti-slop purity — 5: nol P0 + nol orde-kedua (gate otomatis).
2. UX speed & 1-to-3 — 5: satu aksi utama per viewport (salin
   perintah install), sekunder maks 3 (pilih perintah terminal,
   salin mcp.json, lompat ke docs).
3. Tipografi — 5: 2 font, tabular-nums di semua angka/output,
   body ≤75ch.
4. Spacing & geometri — 5: grid 8pt, radius 10px, padding kartu ≥16px.
5. Motion — 5: transisi <200ms ease-out, pergantian tab terminal
   instan (0ms, aksi yang diulang), `prefers-reduced-motion`
   mematikan animasi benang.
6. A11y — 5: focus ring merah sinyal, aria-label di semua tombol
   ikon, tag semantik, kontras AA (tinta di kertas, kertas di teal).
7. Mobile — 5: rel kiri menumpuk di atas konten, tanpa scroll
   horizontal di 390px (diuji e2e).

## Tes siluet

Thumbnail hitam-putih landing harus tetap terbaca sebagai "berkas
penyelidikan dengan jendela terminal dan benang merah", bukan halaman
produk generik: rel indeks di kiri + jendela terminal besar + garis
merah vertikal + cap stempel adalah siluetnya. Kalau siluetnya bisa
jadi landing SaaS apa pun, revisi.
