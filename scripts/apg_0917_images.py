#!/usr/bin/env python3
"""2026-09-17 Apogee approved PPC image derivatives.

Source: the 11 inline images embedded in the landing-page build document, which
dedupe to 5 unique client photographs. Originals are never modified.
Only cropping and resizing are performed. No lighting is added, removed or altered.
No stock or generated imagery.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

from PIL import Image
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SRC = Path(r"C:\Users\walte\AppData\Local\Temp\claude\D--MG-green-marketing-gsa\1e974fe5-5177-4478-be1a-0514305fa975\scratchpad\apg_images\unique")
OUT = SRC.parent / "approved"
OUT.mkdir(parents=True, exist_ok=True)

# AG folder that holds the landing-page doc
AG_FOLDER = "17QCv3pWWpPjv6tVZEjnTXNcrkMEspILL"

# -------------------------------------------------------------------------
# Editorial decisions, made after visually inspecting every unique image.
# crop = (left, top, right, bottom) in ORIGINAL pixels, or None for full frame.
# -------------------------------------------------------------------------
PLAN = {
    "u01_1066ea402b07.jpg": {
        "slug": "apogee-permanent-lights-warm-white-brick-ranch",
        "approved": True,
        "crop": None,
        "privacy_crop": "none required",
        "alt": "Brick ranch home in Lincoln outlined with warm-white permanent roofline lights at night",
        "lp_placement": "Hero image, section 2",
        "ads_placement": "Primary landscape image asset",
        "notes": "Cleanest warm-white frame. Gables and roofline both lit. No vehicles, no plates, no house number, no notifications.",
    },
    "u02_bb1d0ae87d21.jpg": {
        "slug": None,
        "approved": False,
        "crop": None,
        "privacy_crop": "n/a - excluded",
        "reject_reason": "Visible motion blur in the foreground branches and a soft subject, plus two vehicles in the driveway. u05 shows the same red-and-green look with better sharpness.",
    },
    "u03_7f3bfa751d18.jpg": {
        "slug": "apogee-permanent-lights-warm-white-wide-elevation",
        "approved": True,
        "crop": (0, 150, 2048, 1000),
        "privacy_crop": "bottom cropped to remove a large empty dark lawn, not for privacy",
        "alt": "Wide view of a home with warm-white permanent lighting along the roofline and gables",
        "lp_placement": "Section 5 main image",
        "ads_placement": "Secondary landscape image asset",
        "notes": "Strong wide elevation. Cropped to lift the house out of a large dark foreground.",
    },
    "u04_ba941c7c01b6.jpg": {
        "slug": "apogee-permanent-lights-professional-installation",
        "approved": True,
        "crop": None,
        "privacy_crop": "none required",
        "alt": "Installer ladders beside a home with newly installed warm-white permanent roofline lighting",
        "lp_placement": "Section 8 three-step process, professional installation step",
        "ads_placement": "Hold. Ladders read as work-in-progress and suit the landing page better than an ad.",
        "notes": "Shows real professional installation in progress. No vehicles, no plates, no house number.",
    },
    "u05_aafdab3f0dbf.jpg": {
        "slug": "apogee-permanent-lights-red-and-green-roofline",
        "approved": True,
        "crop": (0, 0, 2048, 900),
        "privacy_crop": "PRIVACY CROP. Bottom 636 px removed to exclude two vehicles whose licence plates were legible - a black pickup and a red SUV in the driveway.",
        "alt": "Home outlined with red and green permanent roofline lights at night",
        "lp_placement": "Section 6 custom looks card",
        "ads_placement": "Seasonal colour landscape image asset",
        "notes": "Best red-and-green frame. Roofline detail is fully preserved above the crop line.",
    },
}

DERIVS = [("1200x1200", 1200, 1200), ("1200x628", 1200, 628)]


def crop_to_ratio(im, tw, th):
    """Centre crop-to-fill, then resize. Never distorts."""
    target = tw / th
    w, h = im.size
    cur = w / h
    if cur > target:
        nw = int(h * target)
        left = (w - nw) // 2
        im = im.crop((left, 0, left + nw, h))
    else:
        nh = int(w / target)
        top = max(0, int((h - nh) * 0.35))   # bias upward: the lights are up high
        im = im.crop((0, top, w, top + nh))
    return im.resize((tw, th), Image.LANCZOS)


manifest = []
print("=== BUILDING DERIVATIVES ===")
for fn, spec in PLAN.items():
    p = SRC / fn
    if not spec["approved"]:
        print(f"\n  EXCLUDED  {fn}")
        print(f"            {spec['reject_reason']}")
        manifest.append({"original": fn, "approved": False,
                         "reject_reason": spec["reject_reason"]})
        continue
    im = Image.open(p)
    im = im.convert("RGB")
    ow, oh = im.size
    if spec["crop"]:
        im = im.crop(spec["crop"])
    print(f"\n  {fn}  original {ow}x{oh} -> working {im.size[0]}x{im.size[1]}")
    print(f"     privacy: {spec['privacy_crop']}")
    entry = {"original": fn, "approved": True, "slug": spec["slug"],
             "original_dimensions": f"{ow}x{oh}",
             "privacy_crop": spec["privacy_crop"], "alt_text": spec["alt"],
             "landing_page_placement": spec["lp_placement"],
             "google_ads_placement": spec["ads_placement"],
             "notes": spec["notes"], "derivatives": []}
    for label, tw, th in DERIVS:
        out = crop_to_ratio(im.copy(), tw, th)
        name = f"{spec['slug']}-{label}.jpg"
        fp = OUT / name
        out.save(fp, "JPEG", quality=88, optimize=True, progressive=True)
        kb = fp.stat().st_size // 1024
        print(f"     -> {name}  {tw}x{th}  {kb}KB")
        entry["derivatives"].append({"filename": name, "dimensions": f"{tw}x{th}",
                                     "file_type": "JPG", "size_kb": kb})
    manifest.append(entry)

# -------------------------------------------------------------------------
print("\n=== UPLOADING TO DRIVE ===")
creds = Credentials.from_authorized_user_file(r"D:\MG\secrets\green-marketing-drive-token.json")
drive = build("drive", "v3", credentials=creds, cache_discovery=False)

q = (f"'{AG_FOLDER}' in parents and name='Approved PPC Images' "
     f"and mimeType='application/vnd.google-apps.folder' and trashed=false")
found = drive.files().list(q=q, fields="files(id,name)", supportsAllDrives=True).execute().get("files", [])
if found:
    folder_id = found[0]["id"]
    print(f"  folder exists: {folder_id}")
else:
    folder_id = drive.files().create(
        body={"name": "Approved PPC Images", "mimeType": "application/vnd.google-apps.folder",
              "parents": [AG_FOLDER]},
        fields="id", supportsAllDrives=True).execute()["id"]
    print(f"  folder created: {folder_id}")

uploaded = {}
for f in sorted(OUT.glob("*.jpg")):
    ex = drive.files().list(q=f"'{folder_id}' in parents and name='{f.name}' and trashed=false",
                            fields="files(id)", supportsAllDrives=True).execute().get("files", [])
    media = MediaIoBaseUpload(io.BytesIO(f.read_bytes()), mimetype="image/jpeg", resumable=False)
    if ex:
        fid = drive.files().update(fileId=ex[0]["id"], media_body=media,
                                   fields="id", supportsAllDrives=True).execute()["id"]
        print(f"  updated {f.name} -> {fid}")
    else:
        fid = drive.files().create(body={"name": f.name, "parents": [folder_id]},
                                   media_body=media, fields="id",
                                   supportsAllDrives=True).execute()["id"]
        print(f"  uploaded {f.name} -> {fid}")
    uploaded[f.name] = fid

for e in manifest:
    for d in e.get("derivatives", []):
        d["drive_file_id"] = uploaded.get(d["filename"])

# manifest as a Drive file
man = {
    "client": "Apogee Lawns LLC",
    "google_ads_account": "8164626278",
    "service": "Permanent Christmas light installation",
    "generated": "2026-09-17",
    "source": ("The 11 images embedded in the landing-page build document "
               "19MQ3J11WiUuFQZn9kCRih3sBh0BR5kp_wE_ctcxY8Ok, which dedupe to 5 unique "
               "client photographs. No Apogee Christmas-light image folder exists in "
               "Drive; the AG Images folder is empty and IMG_4098.PNG / IMG_4099.PNG "
               "do not exist anywhere in this Drive."),
    "rules_applied": [
        "Originals are never modified. Every derivative is a new file.",
        "Only cropping and resizing. No lighting added, removed or digitally altered.",
        "No stock imagery. No AI-generated imagery.",
        "No text, logo or CTA overlays.",
        "Images containing legible licence plates are cropped to remove them or excluded.",
    ],
    "drive_folder_id": folder_id,
    "images": manifest,
}
mp = OUT / "apogee-approved-ppc-images-manifest.json"
mp.write_text(json.dumps(man, indent=2), encoding="utf-8")
ex = drive.files().list(q=f"'{folder_id}' in parents and name='{mp.name}' and trashed=false",
                        fields="files(id)", supportsAllDrives=True).execute().get("files", [])
media = MediaIoBaseUpload(io.BytesIO(mp.read_bytes()), mimetype="application/json")
if ex:
    mfid = drive.files().update(fileId=ex[0]["id"], media_body=media, fields="id",
                                supportsAllDrives=True).execute()["id"]
else:
    mfid = drive.files().create(body={"name": mp.name, "parents": [folder_id]},
                                media_body=media, fields="id",
                                supportsAllDrives=True).execute()["id"]
print(f"  manifest -> {mfid}")

print("\n=== SUMMARY ===")
ok = [e for e in manifest if e["approved"]]
print(f"  unique client photos inspected : 5")
print(f"  approved                       : {len(ok)}")
print(f"  excluded                       : {len(manifest) - len(ok)}")
print(f"  derivatives created            : {sum(len(e['derivatives']) for e in ok)}")
print(f"  privacy crops performed        : {sum(1 for e in ok if e['privacy_crop'].startswith('PRIVACY'))}")
print(f"  Drive folder                   : https://drive.google.com/drive/folders/{folder_id}")
print(f"  manifest file                  : https://drive.google.com/file/d/{mfid}/view")
Path(r"D:\MG\green-marketing-gsa\clients\apogee-lawns\approved-ppc-images-manifest.json").write_text(
    json.dumps(man, indent=2), encoding="utf-8")
print("  local copy: clients/apogee-lawns/approved-ppc-images-manifest.json")
