#!/usr/bin/env python3
"""Does Source = Offline on tracking number 410-705-6354 mislabel paid-search leads?

READ-ONLY. No WhatConverts configuration is read-write, nothing is changed, no routing is
touched. Credential values are never printed, logged or written. No lead PII is retained.

Corrected configuration of record (supplied by the approval owner 2026-09-10):
  Profile            Ambient Cooling & Heating
  Profile ID         105803
  Tracking number    410-705-6354
  Number name        GSA Cooling Traffic      <- a TRACKING-NUMBER name, not a profile name
  Google Ads call    asset 407995613637
  Destination        410-761-0932  (forwarding only, never public)
  Mixed-source       410-914-1456  (must not be static on paid pages)
"""
from __future__ import annotations
import base64, json, os, sys, urllib.request, urllib.error, datetime, re
from pathlib import Path
from collections import Counter, defaultdict

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
PAID, DEST, MIXED = "4107056354", "4107610932", "4109141456"
CONFIG = {
    "profile": "Ambient Cooling & Heating", "profile_id": PROFILE,
    "tracking_number": "410-705-6354", "tracking_number_name": "GSA Cooling Traffic",
    "google_ads_call_asset": "407995613637",
    "forwarding_destination": "410-761-0932 - never public",
    "mixed_source_number": "410-914-1456 - never static on a paid page",
    "routing_change": "NONE. This run is read-only.",
    "correction": "GSA Cooling Traffic is the name of the TRACKING NUMBER, not a WhatConverts "
                  "profile. My session-D report recorded it as a missing profile name; that "
                  "was wrong. The profile is Ambient Cooling & Heating (105803)."}
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "read_only": True,
       "configuration_of_record": CONFIG}


def redact(s):
    for v in (TOKEN, SECRET):
        if v:
            s = s.replace(v, "[REDACTED]")
    return s


def call(path):
    r = urllib.request.Request(f"https://app.whatconverts.com/api/v1/{path}",
                               headers={"Authorization": f"Basic {auth}",
                                        "Accept": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return e.code, {"error": redact(e.read().decode("utf-8", errors="replace"))[:200]}
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {redact(str(e))[:150]}"}


def dg(s):
    d = re.sub(r"\D", "", str(s or ""))
    return d[-10:] if len(d) >= 10 else d


print("=== CONFIGURATION OF RECORD ===")
for k, v in CONFIG.items():
    print(f"  {k:<26}{v}")

leads, page = [], 1
while True:
    st, d = call(f"leads?profile_id={PROFILE}&start_date=2026-06-01&end_date=2026-09-10"
                 f"&leads_per_page=250&page_number={page}")
    if st != 200:
        print(f"\n  leads page {page}: HTTP {st}")
        break
    got = d.get("leads", [])
    leads += got
    if page >= (d.get("total_pages") or 1) or not got:
        break
    page += 1
print(f"\n=== {len(leads)} leads pulled 2026-06-01..2026-09-10 ===")

print("\n=== A. THE PAID NUMBER 410-705-6354, LEAD BY LEAD (no PII) ===")
paid = [l for l in leads if dg(l.get("tracking_number")) == PAID]
print(f"  leads on this number: {len(paid)}")
print(f"  {'date':<12}{'type':<13}{'source':<10}{'medium':<10}{'gclid':<7}{'utm_src':<10}"
      f"{'landing_url':<12}{'status':<9}quotable")
for l in sorted(paid, key=lambda z: str(z.get("date_created"))):
    has_g = bool(str(l.get("gclid") or "").strip())
    lu = str(l.get("landing_url") or "")
    print(f"  {str(l.get('date_created'))[:10]:<12}{str(l.get('lead_type')):<13}"
          f"{str(l.get('lead_source')):<10}{str(l.get('lead_medium')):<10}"
          f"{('YES' if has_g else 'no'):<7}"
          f"{str(l.get('utm_source') or '-'):<10}{('present' if lu else 'ABSENT'):<12}"
          f"{str(l.get('lead_status')):<9}{l.get('quotable')}")

by_type = defaultdict(lambda: {"n": 0, "gclid": 0, "src": Counter(), "med": Counter(),
                               "lp": 0})
for l in paid:
    t = str(l.get("lead_type"))
    e = by_type[t]
    e["n"] += 1
    e["src"][str(l.get("lead_source"))] += 1
    e["med"][str(l.get("lead_medium"))] += 1
    if str(l.get("gclid") or "").strip():
        e["gclid"] += 1
    if str(l.get("landing_url") or "").strip():
        e["lp"] += 1
print(f"\n  {'lead_type':<14}{'n':>4}{'with gclid':>12}{'landing_url':>13}   source / medium")
for t, e in by_type.items():
    print(f"  {t:<14}{e['n']:>4}{e['gclid']:>12}{e['lp']:>13}   "
          f"{dict(e['src'])} / {dict(e['med'])}")
out["paid_number_by_lead_type"] = {
    t: {"n": e["n"], "with_gclid": e["gclid"], "with_landing_url": e["lp"],
        "sources": dict(e["src"]), "mediums": dict(e["med"])} for t, e in by_type.items()}

print("\n=== B. CONTROL: DO *ANY* PHONE CALLS IN THIS PROFILE CARRY A GCLID? ===")
calls_all = [l for l in leads if str(l.get("lead_type")) in ("Phone Call", "Text Message")]
forms_all = [l for l in leads if str(l.get("lead_type")) == "Web Form"]
cg = sum(1 for l in calls_all if str(l.get("gclid") or "").strip())
fg = sum(1 for l in forms_all if str(l.get("gclid") or "").strip())
print(f"  Phone Call / Text Message : {len(calls_all):>4} leads, {cg:>3} carry a gclid "
      f"({100*cg/max(1,len(calls_all)):.1f}%)")
print(f"  Web Form                  : {len(forms_all):>4} leads, {fg:>3} carry a gclid "
      f"({100*fg/max(1,len(forms_all)):.1f}%)")
print("  -> if calls are 0% and forms are not, the click id is lost at the CALL boundary,")
print("     not at the page boundary.")
out["gclid_by_channel"] = {"calls": {"n": len(calls_all), "with_gclid": cg},
                           "forms": {"n": len(forms_all), "with_gclid": fg}}

print("\n=== C. WHAT DOES 'cpc' MEAN ON THIS NUMBER IF NO CLICK ID IS PRESENT? ===")
paid_cpc = [l for l in paid if str(l.get("lead_medium")) == "cpc"]
paid_org = [l for l in paid if str(l.get("lead_medium")) == "organic"]
print(f"  labelled cpc     : {len(paid_cpc)}  with gclid: "
      f"{sum(1 for l in paid_cpc if str(l.get('gclid') or '').strip())}  "
      f"with landing_url: {sum(1 for l in paid_cpc if str(l.get('landing_url') or '').strip())}")
print(f"  labelled organic : {len(paid_org)}  with gclid: "
      f"{sum(1 for l in paid_org if str(l.get('gclid') or '').strip())}  "
      f"with landing_url: {sum(1 for l in paid_org if str(l.get('landing_url') or '').strip())}")
print(f"  cpc lead types   : {dict(Counter(str(l.get('lead_type')) for l in paid_cpc))}")
print(f"  organic lead types: {dict(Counter(str(l.get('lead_type')) for l in paid_org))}")

print("\n=== D. GOOGLE ADS SIDE: WHAT CALL REPORTING IS CONFIGURED? ===")
c = client()
identity_gate(c, verbose=False)
for r in q(c, "SELECT asset.id, asset.call_asset.phone_number, "
              "asset.call_asset.call_conversion_reporting_state, "
              "asset.call_asset.call_conversion_action FROM asset "
              "WHERE asset.type = 'CALL' AND asset.id = 407995613637"):
    a = r.asset
    print(f"  asset {a.id}  {a.call_asset.phone_number}")
    print(f"    reporting state   : {E(a.call_asset.call_conversion_reporting_state)}")
    print(f"    conversion action : {a.call_asset.call_conversion_action or '(account level)'}")
    out["call_asset"] = {"id": str(a.id), "number": a.call_asset.phone_number,
                         "reporting": E(a.call_asset.call_conversion_reporting_state)}
print("\n  account-level call conversion actions:")
for r in q(c, "SELECT conversion_action.id, conversion_action.name, conversion_action.type, "
              "conversion_action.status, conversion_action.primary_for_goal "
              "FROM conversion_action WHERE conversion_action.status != 'REMOVED'"):
    ca = r.conversion_action
    if "CALL" in E(ca.type_) or "call" in ca.name.lower() or "phone" in ca.name.lower():
        print(f"    {ca.id:<14}{E(ca.type_):<26}{E(ca.status):<9}"
              f"primary={ca.primary_for_goal}  {ca.name[:44]}")

print("\n\n=== FINDING ===")
call_paid = [l for l in paid if str(l.get("lead_type")) in ("Phone Call", "Text Message")]
call_paid_g = sum(1 for l in call_paid if str(l.get("gclid") or "").strip())
form_paid = [l for l in paid if str(l.get("lead_type")) == "Web Form"]
form_paid_g = sum(1 for l in form_paid if str(l.get("gclid") or "").strip())
print(f"  On 410-705-6354: {len(call_paid)} call/text leads, {call_paid_g} with a gclid; "
      f"{len(form_paid)} web-form leads, {form_paid_g} with a gclid.")
out["finding"] = {
    "paid_number_calls": len(call_paid), "paid_number_calls_with_gclid": call_paid_g,
    "paid_number_forms": len(form_paid), "paid_number_forms_with_gclid": form_paid_g}
p = EVID / "2026-09-10e-wc-offline-source.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p.relative_to(ROOT)}  (read-only, no credentials, no PII)")
