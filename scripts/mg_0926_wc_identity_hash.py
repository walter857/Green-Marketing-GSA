#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: group Master Grass WhatConverts leads 2026-08-01..09-26 by a salted hash
of the normalized contact email / phone, so repeat contacts can be linked WITHOUT any contact
value reaching disk or stdout. Prints lead dates, types, sources and group labels only."""
from __future__ import annotations

import datetime
import hashlib
import os
import secrets
import sys
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import requests  # noqa: E402
from requests.auth import HTTPBasicAuth  # noqa: E402
from gm_gsa.config import load_dotenv_if_available  # noqa: E402

load_dotenv_if_available(ROOT / ".env")
AUTH = HTTPBasicAuth(os.environ["WHATCONVERTS_API_TOKEN"].strip(), os.environ["WHATCONVERTS_SECRET"].strip())
NY = ZoneInfo("America/New_York")
SALT = secrets.token_bytes(16)  # per-run salt: hashes are not reusable outside this run


def h(v):
    v = str(v or "").strip().lower()
    d = "".join(ch for ch in v if ch.isdigit())
    key = d[-10:] if ("@" not in v and len(d) >= 10) else v
    return hashlib.sha256(SALT + key.encode()).hexdigest()[:10] if key else None


leads, page = [], 1
while True:
    r = requests.get("https://app.whatconverts.com/api/v1/leads", auth=AUTH, timeout=60, params=dict(
        account_id=64716, profile_id=94840, start_date="2026-08-01", end_date="2026-09-26",
        leads_per_page=250, page_number=page))
    r.raise_for_status()
    b = r.json().get("leads", [])
    leads += b
    if len(b) < 250:
        break
    page += 1
assert all(str(l.get("account_id")) == "64716" for l in leads)

groups = defaultdict(set)
keys = {}
for l in leads:
    ks = set()
    for f in ("email_address", "contact_email_address", "caller_number", "contact_phone_number", "phone_number"):
        hv = h(l.get(f))
        if hv:
            ks.add(hv)
    # form field values may carry the contact too
    for v in (l.get("additional_fields") or {}).values() if isinstance(l.get("additional_fields"), dict) else []:
        s = str(v)
        if "@" in s or sum(ch.isdigit() for ch in s) >= 10:
            hv = h(s)
            if hv:
                ks.add(hv)
    keys[l["lead_id"]] = ks
    for k in ks:
        groups[k].add(l["lead_id"])

# union-find over shared keys
parent = {i: i for i in keys}


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


for ids in groups.values():
    ids = list(ids)
    for o in ids[1:]:
        parent[find(o)] = find(ids[0])
clusters = defaultdict(list)
for l in leads:
    clusters[find(l["lead_id"])].append(l)

focus = [l for l in leads if l.get("lead_type") == "Web Form" or "offer." in str(l.get("landing_url") or "")]
label = {}
for n, (root, ls) in enumerate(sorted(clusters.items(), key=lambda kv: -len(kv[1]))):
    label[root] = f"C{n:02d}"
print("offer-page / web-form leads since 2026-08-01, with contact-cluster label:")
for l in sorted(focus, key=lambda x: x["date_created"]):
    t = datetime.datetime.fromisoformat(l["date_created"].replace("Z", "+00:00")).astimezone(NY)
    root = find(l["lead_id"])
    others = [x for x in clusters[root] if x["lead_id"] != l["lead_id"]]
    print(f"  {t:%m-%d %H:%M} {l.get('lead_type'):<10} {l.get('lead_source')}/{l.get('lead_medium')} "
          f"gclid={'Y' if l.get('gclid') else '-'} status={l.get('lead_status')} cluster={label[root]} "
          f"cluster_size={len(clusters[root])} other_members={[(datetime.datetime.fromisoformat(x['date_created'].replace('Z', '+00:00')).astimezone(NY).strftime('%m-%d'), x.get('lead_type'), x.get('lead_source')) for x in others][:6]}")
