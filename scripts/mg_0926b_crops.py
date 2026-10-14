#!/usr/bin/env python3
"""2026-09-26 LOCAL: crop owner-approved live-site images for the drainage PMax.

Crop-to-fill with a per-image focus point, never stretch, never upscale; strip metadata; sRGB JPEG.
Output sizes: landscape 1.91:1 (<=1200x628), square 1:1 (<=1200), portrait 4:5 (<=960x1200).
Logo: the website's 192x192 transparent mark flattened onto white (PMax minimum is 128x128).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = Path(r"C:\Users\walte\AppData\Local\Temp\claude\D--MG-green-marketing-gsa\3b0eb8b7-b932-46e6-9855-433dc884c0da\scratchpad\mg_images")
OUT = Path(__file__).resolve().parents[1] / "clients" / "mastergrass-lawn-care" / "exports" / "pmax-drainage-images-2026-09-26"
OUT.mkdir(parents=True, exist_ok=True)
man = json.loads((S / "manifest_indexed.json").read_text())
RATIO = {"L": 1.91, "S": 1.0, "P": 0.8}
MAXW = {"L": 1200, "S": 1200, "P": 960}
# (index, slot, focus_x, focus_y)  focus in 0..1 of the source
PLAN = [
    (19, "L", .5, .5), (27, "L", .5, .55), (29, "L", .5, .55), (34, "L", .5, .6), (41, "L", .5, .5),
    (2, "L", .5, .5), (14, "L", .5, .55), (38, "L", .5, .5),
    (19, "S", .5, .5), (29, "S", .5, .5), (27, "S", .45, .5), (34, "S", .6, .55), (14, "S", .65, .5), (2, "S", .4, .5),
    (29, "P", .45, .5), (27, "P", .35, .5), (15, "P", .45, .5),
]


def crop(im, ratio, fx, fy):
    w, h = im.size
    if w / h > ratio:
        cw, ch = int(round(h * ratio)), h
    else:
        cw, ch = w, int(round(w / ratio))
    x = min(max(int(fx * w - cw / 2), 0), w - cw)
    y = min(max(int(fy * h - ch / 2), 0), h - ch)
    return im.crop((x, y, x + cw, y + ch))


rec = []
for idx, slot, fx, fy in PLAN:
    m = man[idx]
    im = Image.open(S / "raw" / m["file"]).convert("RGB")
    c = crop(im, RATIO[slot], fx, fy)
    if c.width > MAXW[slot]:
        c = c.resize((MAXW[slot], int(round(MAXW[slot] / RATIO[slot]))), Image.LANCZOS)
    else:  # exact ratio without upscaling
        c = c.resize((c.width, int(round(c.width / RATIO[slot]))), Image.LANCZOS) if slot != "S" else c.resize((c.width, c.width))
    name = f"mg_drain_{slot}_{idx:02d}.jpg"
    c.save(OUT / name, "JPEG", quality=90, optimize=True)
    data = (OUT / name).read_bytes()
    rec.append({"file": name, "slot": slot, "source_index": idx, "source_url": m["url"], "source_pages": m["pages"],
                "size": f"{c.width}x{c.height}", "ratio": round(c.width / c.height, 3), "kb": len(data) // 1024,
                "sha1": hashlib.sha1(data).hexdigest()[:12]})

logo = Image.open(S / "logos" / "cand_5.png").convert("RGBA")
bg = Image.new("RGB", logo.size, "white")
bg.paste(logo, mask=logo.split()[3])
bg.save(OUT / "mg_logo_square_192.png", "PNG", optimize=True)
rec.append({"file": "mg_logo_square_192.png", "slot": "LOGO", "source_url":
            "https://offer.mastergrasslawncare.com/wp-content/uploads/2026/05/cropped-apple-touch-icon-192x192.png",
            "size": f"{bg.width}x{bg.height}", "ratio": 1.0, "kb": (OUT / "mg_logo_square_192.png").stat().st_size // 1024})
(OUT / "manifest.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")

# review sheet
font = ImageFont.truetype("arial.ttf", 20)
tiles = [(r["file"], Image.open(OUT / r["file"]).convert("RGB")) for r in rec]
sheet = Image.new("RGB", (4 * 380, ((len(tiles) + 3) // 4) * 300), "white")
d = ImageDraw.Draw(sheet)
for i, (n, t) in enumerate(tiles):
    t.thumbnail((370, 260))
    x, y = (i % 4) * 380, (i // 4) * 300
    sheet.paste(t, (x + 5, y + 5))
    d.text((x + 5, y + 268), n, fill="black", font=font)
sheet.save(S / "crops_review.jpg", quality=80)
for r in rec:
    print(r["file"], r["size"], r["ratio"], f"{r['kb']}KB")
