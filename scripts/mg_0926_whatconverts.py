#!/usr/bin/env python3
"""2026-09-26 READ-ONLY WhatConverts pull for Master Grass Lawn Care.

Finds the Master Grass WhatConverts account by name, pulls every lead 2026-01-01..2026-09-26
(spam and duplicates included, flagged), writes the redacted rows to disk and prints only
aggregates. Never prints a credential, a caller number, a name or an email.
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
OUT = ROOT / "clients" / "mastergrass-lawn-care" / "snapshots" / "audit-2026-09-26"

# Fields kept on disk. Contact PII (names, emails, caller numbers, free-text fields) is dropped.
KEEP = {
    "lead_id", "account_id", "account", "profile_id", "profile", "lead_type", "lead_status",
    "date_created", "last_updated", "quotable", "quote_value", "sales_value", "spam",
    "duplicate", "lead_source", "lead_medium", "lead_campaign", "lead_content", "lead_term",
    "lead_keyword", "lead_url", "landing_url", "lead_score", "gclid", "msclkid", "fbclid",
    "tracking_number", "destination_number", "call_duration", "call_duration_seconds",
    "call_status", "answer_status", "form_name", "device_type", "device_make", "browser",
    "operating_system", "ip_address_city", "city", "state", "country", "user_id",
    "first_touch", "lead_analysis", "additional_fields", "customer_journey", "valuable",
    "phone_name", "caller_city", "caller_state", "lead_state", "spotted_keywords", "line_type",
}


def get(path, **params):
    r = requests.get(f"{BASE}/{path}", auth=AUTH, params=params, timeout=60)
    ctype = r.headers.get("content-type", "")
    return r.status_code, (r.json() if ctype.startswith("application/json") else r.text[:300])


code, body = get("accounts", accounts_per_page=250)
accounts = body.get("accounts", []) if isinstance(body, dict) else []
print(f"accounts HTTP {code}: {len(accounts)} visible")
hits = [a for a in accounts if "master" in str(a.get("account_name", "")).lower()]
for a in hits:
    print(f"  candidate account_id={a.get('account_id')} name={a.get('account_name')} "
          f"profiles={[(p.get('profile_id'), p.get('profile_name')) for p in a.get('profiles', [])]}")
if len(hits) != 1:
    sys.exit(f"STOP: expected exactly one Master Grass WhatConverts account, found {len(hits)}")
acct = str(hits[0]["account_id"])

leads, page = [], 1
while page <= 40:
    code, body = get("leads", account_id=acct, start_date="2026-01-01", end_date="2026-09-26",
                     leads_per_page=250, page_number=page)
    if code != 200 or not isinstance(body, dict):
        print(f"  leads page {page} HTTP {code}: {str(body)[:200]}")
        break
    batch = body.get("leads", [])
    leads += batch
    if page == 1:
        print(f"  total_leads reported: {body.get('total_leads')}")
    if len(batch) < 250:
        break
    page += 1

bad = [l.get("lead_id") for l in leads if str(l.get("account_id")) != acct]
if bad:
    sys.exit(f"STOP: {len(bad)} leads outside account {acct}")

all_keys = sorted({k for l in leads for k in l})
red = [{k: v for k, v in l.items() if k in KEEP} for l in leads]
(OUT / "wc_leads_2026.json").write_text(json.dumps(red, indent=0), encoding="utf-8")
(OUT / "wc_field_names.json").write_text(json.dumps(all_keys, indent=0), encoding="utf-8")
print(f"  leads pulled: {len(leads)} -> wc_leads_2026.json (redacted)")
print(f"  field names ({len(all_keys)}): {all_keys}")
