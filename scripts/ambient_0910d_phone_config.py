#!/usr/bin/env python3
"""Identify what each phone number IS before touching any routing.

410-705-6354  expected paid landing-page number and Google Ads call-asset destination
410-761-0932  organic / main site number
410-914-1456  UNAPPROVED for paid pages unless WhatConverts config proves it intentional
              inside the GSA Cooling Traffic profile

Read-only. No WhatConverts configuration is changed. Credential values are never printed,
logged or written, and no lead PII is retained.
"""
from __future__ import annotations
import base64, json, os, sys, urllib.request, urllib.error, datetime, re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import CID, FIVE, IN5, NAME, EVID, TZ, client, q, identity_gate  # noqa
from gm_gsa.config import load_dotenv_if_available  # noqa
from gm_gsa.google_ads import enum_name as E  # noqa

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()
PROFILE = "105803"
NUM = {"4107056354": "PAID landing-page number (expected)",
       "4107610932": "ORGANIC / main site number",
       "4109141456": "UNAPPROVED on paid pages - identify before acting"}
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "read_only": True,
       "note": "No WhatConverts configuration was modified."}


def redact(s):
    for v in (TOKEN, SECRET):
        if v:
            s = s.replace(v, "[REDACTED]")
    return s


def call(path):
    url = f"https://app.whatconverts.com/api/v1/{path}"
    r = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}",
                                             "Accept": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        return e.code, {"error": redact(body)}
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {redact(str(e))[:160]}"}


def digits(s):
    d = re.sub(r"\D", "", str(s or ""))
    return d[-10:] if len(d) >= 10 else d


print("=== WHATCONVERTS CONFIGURATION ENDPOINTS ===")
for path in ["accounts", "profiles", f"profiles?account_id={PROFILE}",
             "tracking-numbers", f"tracking-numbers?profile_id={PROFILE}",
             f"phone-numbers?profile_id={PROFILE}",
             f"numbers?profile_id={PROFILE}"]:
    st, body = call(path)
    keys = list(body)[:6] if isinstance(body, dict) else f"list[{len(body)}]"
    print(f"  {path:<44}HTTP {st}   {str(keys)[:110]}")
    out.setdefault("endpoints", {})[path] = {"status": st,
                                             "shape": str(keys)[:200]}
    if st == 200:
        out.setdefault("payloads", {})[path] = body

print("\n=== WHICH NUMBERS APPEAR IN THE LEAD DATA, AND IN WHICH ROLE? ===")
leads, page = [], 1
while True:
    st, d = call(f"leads?profile_id={PROFILE}&start_date=2026-08-14&end_date=2026-09-10"
                 f"&leads_per_page=250&page_number={page}")
    if st != 200:
        print(f"  leads page {page}: HTTP {st}")
        break
    got = d.get("leads", [])
    leads += got
    if page >= (d.get("total_pages") or 1) or not got:
        break
    page += 1
print(f"  leads pulled: {len(leads)}")

roles = {}
for l in leads:
    for field, role in [("tracking_number", "TRACKING NUMBER (what the caller dialled)"),
                        ("destination_number", "DESTINATION (where the call was routed)"),
                        ("phone_number", "SOURCE/CALLER-SIDE field")]:
        d = digits(l.get(field))
        if not d:
            continue
        roles.setdefault(d, Counter())[role] += 1
print(f"\n  {'number':<14}{'label':<44}role counts")
for d, cnt in sorted(roles.items(), key=lambda z: -sum(z[1].values())):
    label = NUM.get(d, "not one of the three named numbers")
    if d not in NUM and sum(cnt.values()) < 2:
        continue
    print(f"  {d:<14}{label:<44}{dict(cnt)}")
out["number_roles_in_lead_data"] = {d: dict(c) for d, c in roles.items()}

print("\n  the three named numbers specifically:")
for d, label in NUM.items():
    r = roles.get(d)
    print(f"    {d}  {label}")
    print(f"      {'appears as: ' + str(dict(r)) if r else 'DOES NOT APPEAR in any lead record'}")

print("\n\n=== GOOGLE ADS CALL ASSETS ===")
c = client()
identity_gate(c, verbose=False)
calls = []
for r in q(c, "SELECT asset.id, asset.type, asset.call_asset.phone_number, "
              "asset.call_asset.country_code, asset.call_asset.call_conversion_action, "
              "asset.call_asset.call_conversion_reporting_state "
              "FROM asset WHERE asset.type = 'CALL'"):
    a = r.asset
    calls.append({"asset_id": str(a.id), "number": a.call_asset.phone_number,
                  "digits": digits(a.call_asset.phone_number),
                  "country": a.call_asset.country_code,
                  "conversion_action": a.call_asset.call_conversion_action,
                  "reporting": E(a.call_asset.call_conversion_reporting_state)})
for x in calls:
    lbl = NUM.get(x["digits"], "*** NOT A NAMED NUMBER ***")
    print(f"  asset {x['asset_id']:<14}{x['number']:<18}{x['country']:<4}{x['reporting']:<34}{lbl}")
out["call_assets"] = calls

print("\n  call assets linked to the five campaigns:")
for r in q(c, f"SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type, "
              f"campaign_asset.status FROM campaign_asset WHERE campaign.id IN ({IN5})"):
    if "CALL" in E(r.campaign_asset.field_type):
        aid = r.campaign_asset.asset.split("/")[-1]
        m = next((x for x in calls if x["asset_id"] == aid), None)
        print(f"    {NAME[str(r.campaign.id)]:<20}asset {aid:<14}"
              f"{(m['number'] if m else '?'):<18}{E(r.campaign_asset.status)}")
        out.setdefault("campaign_call_links", []).append(
            {"campaign": NAME[str(r.campaign.id)], "asset_id": aid,
             "number": m["number"] if m else None,
             "status": E(r.campaign_asset.status)})

print("\n=== VERDICT ===")
paid_in_assets = any(x["digits"] == "4107056354" for x in calls)
unappr_in_assets = any(x["digits"] == "4109141456" for x in calls)
unappr_in_leads = "4109141456" in roles
print(f"  410-705-6354 present as a Google Ads call asset : {paid_in_assets}")
print(f"  410-914-1456 present as a Google Ads call asset : {unappr_in_assets}")
print(f"  410-914-1456 present anywhere in lead records   : {unappr_in_leads}")
if unappr_in_leads:
    print(f"      role(s) it plays: {dict(roles['4109141456'])}")
out["verdict"] = {"paid_number_is_a_call_asset": paid_in_assets,
                  "unapproved_number_is_a_call_asset": unappr_in_assets,
                  "unapproved_number_in_lead_records": unappr_in_leads,
                  "unapproved_number_roles": dict(roles.get("4109141456", {}))}
p = EVID / "2026-09-10d-phone-configuration.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p.relative_to(ROOT)}  (no credentials, no PII)")
