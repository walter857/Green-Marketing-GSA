#!/usr/bin/env python3
"""2026-09-16 READ-ONLY WhatConverts lookup for the Apogee PPC tracking number.

Answers one question: is 402-526-5754 a DNI/pool number or a fixed number, and what
source is it stamped with? Never prints a credential.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import requests  # noqa: E402
from requests.auth import HTTPBasicAuth  # noqa: E402

from gm_gsa.config import load_dotenv_if_available  # noqa: E402

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
if not TOKEN or not SECRET:
    sys.exit("WhatConverts credentials missing or empty.")

AUTH = HTTPBasicAuth(TOKEN, SECRET)
BASE = "https://app.whatconverts.com/api/v1"
TARGET_DIGITS = "4025265754"
DEST_DIGITS = "4022027261"


def digits(s):
    return "".join(ch for ch in str(s or "") if ch.isdigit())[-10:]


def get(path, **params):
    try:
        r = requests.get(f"{BASE}/{path}", auth=AUTH, params=params, timeout=30)
        return r.status_code, (r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text[:300])
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {str(exc)[:200]}"


print("=== 1. ACCOUNTS ===")
code, body = get("accounts")
print(f"  HTTP {code}")
accounts = []
if isinstance(body, dict):
    accounts = body.get("accounts") or []
    for a in accounts:
        print(f"    account_id={a.get('account_id')}  {a.get('account_name')}")
else:
    print(f"    {body}")

print("\n=== 2. PROFILES ===")
code, body = get("profiles")
print(f"  HTTP {code}")
profiles = []
if isinstance(body, dict):
    profiles = body.get("profiles") or []
    for p in profiles:
        print(f"    profile_id={p.get('profile_id')}  {p.get('profile_name')}  account_id={p.get('account_id')}")
else:
    print(f"    {body}")

apogee = [p for p in profiles if "apogee" in str(p.get("profile_name", "")).lower()]
apogee_acc = [a for a in accounts if "apogee" in str(a.get("account_name", "")).lower()]
print(f"\n  profiles matching 'apogee': {[(p.get('profile_id'), p.get('profile_name')) for p in apogee]}")
print(f"  accounts matching 'apogee': {[(a.get('account_id'), a.get('account_name')) for a in apogee_acc]}")

print("\n=== 3. TRACKING NUMBERS ===")
found = []
tried = []
for path in ("phone-numbers", "tracking-numbers", "numbers"):
    code, body = get(path, per_page=250)
    tried.append((path, code))
    if code == 200 and isinstance(body, dict):
        key = next((k for k in body if isinstance(body[k], list)), None)
        rows = body.get(key) or []
        print(f"  {path}: HTTP {code}, {len(rows)} rows (key='{key}')")
        for n in rows:
            blob = "".join(ch for ch in json.dumps(n) if ch.isdigit())
            if TARGET_DIGITS in blob:
                found.append((path, n))
        break
    else:
        print(f"  {path}: HTTP {code}")
print(f"  endpoints tried: {tried}")

if found:
    print(f"\n=== 4. MATCHES FOR {TARGET_DIGITS} ===")
    for path, n in found:
        print(f"  from /{path}:")
        for k, v in n.items():
            if any(s in k.lower() for s in ("token", "secret", "key")):
                continue
            print(f"    {k}: {v}")
else:
    print(f"\n=== 4. NO DIRECT MATCH for {TARGET_DIGITS} in the number list ===")

print("\n=== 5. RECENT LEADS: does any carry these numbers? (last 90d, capped) ===")
code, body = get("leads", start_date="2026-06-18", end_date="2026-09-16", per_page=50)
print(f"  HTTP {code}")
if isinstance(body, dict):
    leads = body.get("leads") or []
    print(f"  leads returned: {len(leads)}")
    hit = 0
    for l in leads:
        blob = "".join(ch for ch in json.dumps(l) if ch.isdigit())
        if TARGET_DIGITS in blob or DEST_DIGITS in blob:
            hit += 1
    print(f"  leads referencing 402-526-5754 or 402-202-7261: {hit}")
    srcs = {}
    for l in leads:
        srcs[str(l.get("lead_source"))] = srcs.get(str(l.get("lead_source")), 0) + 1
    print(f"  lead_source mix: {srcs}")
else:
    print(f"  {body}")
