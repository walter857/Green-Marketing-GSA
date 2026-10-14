#!/usr/bin/env python3
"""WhatConverts connectivity test. Never prints, logs or writes the credential values."""
from __future__ import annotations
import base64, json, os, sys, urllib.request, urllib.error, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available  # noqa

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
PROFILE = "105803"          # from work-order.yaml inputs.whatconverts_profile
BASE = "https://app.whatconverts.com/api/v1"

print("=== WHATCONVERTS CONNECTIVITY TEST ===")
print(f"  WHATCONVERTS_API_TOKEN : {'SET len=%d' % len(TOKEN) if TOKEN else 'EMPTY'}")
print(f"  WHATCONVERTS_SECRET    : {'SET len=%d' % len(SECRET) if SECRET else 'EMPTY'}")
print("  (values are never printed, logged or written to disk)")
if not TOKEN or not SECRET:
    sys.exit("  BLOCKED: one or both credentials are empty.")

auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()


def call(path, label):
    url = f"{BASE}/{path}"
    safe = url.replace(TOKEN, "[REDACTED]").replace(SECRET, "[REDACTED]")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Basic {auth}", "Accept": "application/json",
        "User-Agent": "GreenMarketing-GSA/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            body = r.read().decode("utf-8", errors="replace")
            print(f"  [{r.status}] {label}  <- {safe}")
            return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:400]
        red = body.replace(TOKEN, "[REDACTED]").replace(SECRET, "[REDACTED]")
        print(f"  [{e.code}] {label}  <- {safe}")
        print(f"        response: {red[:300]}")
        return e.code, None
    except Exception as e:
        print(f"  [ERR] {label}: {type(e).__name__}: "
              f"{str(e).replace(TOKEN,'[REDACTED]').replace(SECRET,'[REDACTED]')[:200]}")
        return None, None


out = {"tested_local": datetime.datetime.now(TZ).isoformat()
       if (TZ := __import__("zoneinfo").ZoneInfo("America/New_York")) else None,
       "token_present": True, "secret_present": True, "profile": PROFILE}

print("\n--- 1. list accessible profiles ---")
st, body = call("profiles", "GET /profiles")
out["profiles_status"] = st
profiles = []
if body:
    try:
        d = json.loads(body)
        profiles = d.get("profiles", d if isinstance(d, list) else [])
        print(f"        profiles returned: {len(profiles)}")
        for p in profiles[:25]:
            pid = str(p.get("profile_id", p.get("id", "?")))
            nm = p.get("profile_name", p.get("name", "?"))
            mark = "  <<< AMBIENT" if pid == PROFILE else ""
            print(f"          {pid:<10} {nm}{mark}")
        out["profiles"] = [{"id": str(p.get("profile_id", p.get("id", ""))),
                            "name": p.get("profile_name", p.get("name", ""))}
                           for p in profiles]
    except Exception as e:
        print(f"        could not parse profiles: {type(e).__name__}")

print("\n--- 2. leads for the Ambient profile, recent window ---")
st2, body2 = call(f"leads?profile_id={PROFILE}&start_date=2026-08-14&end_date=2026-09-10"
                  f"&leads_per_page=250", "GET /leads (Ambient, 2026-08-14..2026-09-10)")
out["leads_status"] = st2
if body2:
    try:
        d = json.loads(body2)
        leads = d.get("leads", [])
        print(f"        leads returned: {len(leads)}   total_leads={d.get('total_leads')}   "
              f"pages={d.get('total_pages')}")
        out["lead_count"] = len(leads)
        out["total_leads"] = d.get("total_leads")
        if leads:
            keys = sorted({k for l in leads for k in l.keys()})
            print(f"        available fields ({len(keys)}):")
            for i in range(0, len(keys), 6):
                print("          " + ", ".join(keys[i:i + 6]))
            out["fields"] = keys
            NEED = {"date": ["date_created", "date"],
                    "campaign": ["gclid_campaign", "campaign", "google_ads_campaign"],
                    "source": ["lead_source", "source"],
                    "type": ["lead_type"],
                    "join_key": ["gclid", "lead_id"],
                    "qualified": ["quotable", "lead_status", "quotable_status"],
                    "sold": ["sales_value", "quote_value"]}
            print("\n        required-field coverage:")
            for want, cands in NEED.items():
                found = [c for c in cands if c in keys]
                print(f"          {want:<12} {'OK ' + str(found) if found else 'MISSING ' + str(cands)}")
            out["field_coverage"] = {k: [c for c in v if c in keys] for k, v in NEED.items()}
            from collections import Counter
            print("\n        aggregate shape (NO PII printed):")
            for f in ("lead_type", "lead_status", "quotable", "lead_source"):
                if f in keys:
                    print(f"          {f}: {dict(Counter(str(l.get(f)) for l in leads))}")
            gcl = sum(1 for l in leads if l.get("gclid"))
            print(f"          rows with a gclid: {gcl} / {len(leads)}")
            out["rows_with_gclid"] = gcl
    except Exception as e:
        print(f"        could not parse leads: {type(e).__name__}: {str(e)[:160]}")

p = ROOT / "reports" / "ambient-cooling-heating" / "evidence" / "2026-09-10-whatconverts-test.json"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p.relative_to(ROOT)}  (contains no credential values and no PII)")
