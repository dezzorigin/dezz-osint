#!/usr/bin/env python3
"""Generate og-image.png 1200x630 untuk dezz-osint (PIL, lokal).

Desain mengikuti palet landing (docs/DESIGN.md): kertas #EFE9DD,
tinta #1B1712, sinyal #B42318 (benang merah), teal verifikasi
#0F5B5E, kuning kandidat #B7791F. Kartu berkas + benang merah +
cap verdict = detail khas repo ini. Bukan screenshot — kartu
preview yang digambar mengikuti palet landing.

Usage: python3 scripts/make-og-image.py  (tulis ke root repo)
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "og-image.png")

W, H = 1200, 630
KERTAS = (239, 233, 221)   # #EFE9DD
TINTA = (27, 23, 18)       # #1B1712
SINYAL = (180, 35, 24)     # #B42318
TEAL = (15, 91, 94)         # #0F5B5E
GARIS = (213, 205, 189)     # #D5CDBD
KARTU = (247, 243, 234)     # #F7F3EA
MUTED = (92, 85, 70)        # #5C5546

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

img = Image.new("RGB", (W, H), KERTAS)
d = ImageDraw.Draw(img)

# bingkai garis + benang merah vertikal (string board)
d.rectangle([28, 28, W - 28, H - 28], outline=GARIS, width=2)
d.line([(196, 60), (196, H - 60)], fill=SINYAL, width=4)
for y in (120, 300, 480):
    d.ellipse([188, y - 8, 204, y + 8], fill=SINYAL)

# kicker
f_kick = ImageFont.truetype(MONO_B, 28)
d.text((240, 66), "BERKAS PENYELIDIKAN  ·  CLI + MCP", font=f_kick, fill=SINYAL)

# judul
f_title = ImageFont.truetype(SANS_B, 116)
d.text((236, 118), "dezz-osint", font=f_title, fill=TINTA)

# subjudul
f_sub = ImageFont.truetype(SANS, 36)
d.text((240, 258), "Satu target, tiga belas mesin.", font=f_sub, fill=TINTA)
d.text((240, 306), "Hasil dicap: [verified] · [?] · [SKIP].", font=f_sub, fill=MUTED)

# kartu mini: contoh temuan IP
d.rounded_rectangle([240, 392, 940, 500], radius=10, fill=KARTU, outline=GARIS, width=2)
f_card = ImageFont.truetype(MONO, 28)
d.text((268, 414), "$ dezz ip 8.8.8.8", font=f_card, fill=TINTA)
d.text((268, 452), "Ashburn, US  ·  Google LLC", font=f_card, fill=TEAL)

# cap verdict
f_stamp = ImageFont.truetype(MONO_B, 30)
label = "[verified]"
tw = d.textlength(label, font=f_stamp)
x0, y0 = 968, 408
d.rectangle([x0, y0, x0 + tw + 28, y0 + 56], outline=TEAL, width=3)
d.text((x0 + 14, y0 + 10), label, font=f_stamp, fill=TEAL)

# meta + url
f_meta = ImageFont.truetype(MONO, 26)
d.text((240, 528), "14 perintah  ·  13 tool MCP  ·  3.793 entri katalog  ·  0 kunci wajib",
       font=f_meta, fill=MUTED)
f_url = ImageFont.truetype(MONO_B, 28)
d.text((240, 566), "dezz-osint.pages.dev", font=f_url, fill=SINYAL)

img.save(OUT, "PNG", optimize=True)
print(f"saved {OUT} ({os.path.getsize(OUT)} bytes)")
