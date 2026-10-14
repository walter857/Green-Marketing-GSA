#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: collect candidate images for the Master Grass drainage PMax from the live
drainage landing page and the live website (owner-approved source, 2026-09-26).

GET only, no query parameters (never seed the page cache), no form interaction. Downloads each
image once at its largest available rendition and records a manifest; nothing is uploaded here.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from PIL import Image
from playwright.sync_api import sync_playwright

SCRATCH = Path(r"C:\Users\walte\AppData\Local\Temp\claude\D--MG-green-marketing-gsa\3b0eb8b7-b932-46e6-9855-433dc884c0da\scratchpad\mg_images")
RAW = SCRATCH / "raw"
RAW.mkdir(parents=True, exist_ok=True)
PAGES = [
    "https://offer.mastergrasslawncare.com/french-drain/",
    "https://offer.mastergrasslawncare.com/yard-grading/",
    "https://mastergrasslawncare.com/",
    "https://mastergrasslawncare.com/services/landscaping/french-drains/",
    "https://mastergrasslawncare.com/services/landscaping/",
    "https://mastergrasslawncare.com/services/",
    "https://mastergrasslawncare.com/gallery/",
    "https://mastergrasslawncare.com/our-work/",
]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/141.0.0.0 Safari/537.36")


def biggest(srcset: str, base: str) -> str | None:
    best, bw = None, -1
    for part in (srcset or "").split(","):
        bits = part.strip().split()
        if not bits:
            continue
        w = int(bits[1][:-1]) if len(bits) > 1 and bits[1].endswith("w") and bits[1][:-1].isdigit() else 0
        if w > bw:
            best, bw = urljoin(base, bits[0]), w
    return best


found: dict[str, set] = {}
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, user_agent=UA)
    pg = ctx.new_page()
    for u in PAGES:
        try:
            r = None
            for _ in range(4):
                r = pg.goto(u, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)
                if "Robot Challenge" not in pg.title():
                    break
            # scroll to trigger lazy loading
            for y in range(0, 12000, 900):
                pg.evaluate(f"window.scrollTo(0,{y})")
                time.sleep(0.25)
            time.sleep(2)
            final = pg.url
            status = r.status if r else None
            urls = pg.evaluate("""() => {
              const out = [];
              document.querySelectorAll('img').forEach(i => out.push({src: i.currentSrc || i.src, srcset: i.srcset || i.getAttribute('data-srcset') || '', lazy: i.getAttribute('data-src') || i.getAttribute('data-lazy-src') || '', alt: i.alt || ''}));
              document.querySelectorAll('*').forEach(e => { const bg = getComputedStyle(e).backgroundImage; if (bg && bg.startsWith('url(')) out.push({src: bg.slice(5, -2), srcset: '', lazy: '', alt: 'css-bg'}); });
              return out; }""")
            print(f"{status} {final} images:{len(urls)}")
            if status and status >= 400:
                continue
            for x in urls:
                cand = biggest(x["srcset"], final) or (urljoin(final, x["lazy"]) if x["lazy"] else None) or x["src"]
                if not cand or cand.startswith("data:") or not cand.startswith("http"):
                    continue
                if not re.search(r"\.(jpe?g|png|webp)(\?|$)", cand, re.I):
                    continue
                found.setdefault(cand, set()).add((urlparse(final).netloc + urlparse(final).path, x["alt"][:80]))
        except Exception as exc:  # noqa: BLE001
            print("ERR", u, str(exc)[:200])
    b.close()

man = []
seen_hash = set()
for url, where in found.items():
    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=60)
        if resp.status_code != 200:
            continue
        data = resp.content
        h = hashlib.sha1(data).hexdigest()[:12]
        if h in seen_hash:
            continue
        im = Image.open(io.BytesIO(data))
        w, hgt = im.size
        if w < 600 or hgt < 300:
            continue
        seen_hash.add(h)
        ext = (im.format or "jpg").lower().replace("jpeg", "jpg")
        name = f"{h}_{w}x{hgt}.{ext}"
        (RAW / name).write_bytes(data)
        man.append({"file": name, "url": url, "w": w, "h": hgt, "kb": len(data) // 1024,
                    "pages": sorted(p for p, _ in where), "alt": sorted({a for _, a in where if a})[:3]})
    except Exception as exc:  # noqa: BLE001
        print("DLERR", url[:100], str(exc)[:120])
(SCRATCH / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
print(f"\nkept {len(man)} images >=600x300")
for m in sorted(man, key=lambda m: -m["w"] * m["h"]):
    print(f"  {m['file']:<32} {m['kb']:>5}KB  pages={len(m['pages'])} {m['pages'][0][:55]:<55} alt={m['alt'][:1]}")
