#!/usr/bin/env python3
"""Resolve unique qualified leads for the five paid campaigns.

Pulls WhatConverts leads, keeps only paid-search-attributable rows, joins GCLID to campaign
through Google Ads click_view, and reports COUNTS ONLY. No name, phone, email, address, IP,
recording or transcript is printed or written.
"""
from __future__ import annotations
import base64, json, os, sys, urllib.request, urllib.error, datetime, hashlib
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
PROFILE = "105803"
auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()
START, END = "2026-08-14", "2026-09-10"

PII = {"caller_name", "caller_number", "contact_name", "contact_email_address",
       "contact_phone_number", "email_address", "phone_number", "message", "ip_address",
       "call_transcription", "recording", "play_recording", "caller_city", "caller_zip",
       "city", "zip", "lead_url", "landing_url", "additional_fields", "custom_fields",
       "mapped_fields", "contact_company_name", "phone_name", "tracking_number",
       "destination_number", "spotted_keywords", "lead_analysis"}


def fetch(page):
    url = (f"https://app.whatconverts.com/api/v1/leads?profile_id={PROFILE}"
           f"&start_date={START}&end_date={END}&leads_per_page=250&page_number={page}")
    r = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}",
                                             "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


print("=== WHATCONVERTS LEAD ANALYSIS (counts only, no PII) ===")
leads, page = [], 1
while True:
    d = fetch(page)
    got = d.get("leads", [])
    leads += got
    if page >= (d.get("total_pages") or 1) or not got:
        break
    page += 1
print(f"  leads pulled {START}..{END}: {len(leads)}")

safe = [{k: v for k, v in l.items() if k not in PII} for l in leads]

print(f"\n  lead_type   : {dict(Counter(str(l.get('lead_type')) for l in safe))}")
print(f"  lead_status : {dict(Counter(str(l.get('lead_status')) for l in safe))}")
print(f"  quotable    : {dict(Counter(str(l.get('quotable')) for l in safe))}")
print(f"  spam        : {dict(Counter(str(l.get('spam')) for l in safe))}")
print(f"  duplicate   : {dict(Counter(str(l.get('duplicate')) for l in safe))}")
print(f"  lead_source : {dict(Counter(str(l.get('lead_source')) for l in safe))}")
print(f"  lead_medium : {dict(Counter(str(l.get('lead_medium')) for l in safe))}")

with_g = [l for l in safe if (l.get("gclid") or "").strip()]
print(f"\n  rows carrying a GCLID: {len(with_g)} / {len(safe)}")
print(f"    their lead_source : {dict(Counter(str(l.get('lead_source')) for l in with_g))}")
print(f"    their lead_medium : {dict(Counter(str(l.get('lead_medium')) for l in with_g))}")
print(f"    their lead_type   : {dict(Counter(str(l.get('lead_type')) for l in with_g))}")
print(f"    their quotable    : {dict(Counter(str(l.get('quotable')) for l in with_g))}")
print(f"    their lead_status : {dict(Counter(str(l.get('lead_status')) for l in with_g))}")

print("\n=== GCLID -> CAMPAIGN JOIN VIA GOOGLE ADS click_view ===")
c = client()
identity_gate(c, verbose=False)
gclids = {(l.get("gclid") or "").strip() for l in with_g}
gclids.discard("")
dates = sorted({(l.get("date_created") or "")[:10] for l in with_g if l.get("date_created")})
print(f"  distinct GCLIDs: {len(gclids)}   lead dates: {dates}")
gmap = {}
probe = sorted({d for d in dates} |
               {(datetime.date.fromisoformat(d) - datetime.timedelta(days=k)).isoformat()
                for d in dates for k in (1, 2, 3, 7, 14, 30) if d})
probe = [d for d in probe if "2026-08-01" <= d <= "2026-09-10"]
for d in probe:
    try:
        for r in q(c, f"SELECT click_view.gclid, campaign.id, ad_group.id, segments.date "
                      f"FROM click_view WHERE segments.date = '{d}'"):
            g = r.click_view.gclid
            if g in gclids:
                gmap[g] = {"campaign_id": str(r.campaign.id),
                           "campaign": NAME.get(str(r.campaign.id), str(r.campaign.id)),
                           "ad_group": str(r.ad_group.id), "click_date": r.segments.date}
    except Exception as e:
        print(f"    click_view {d}: {type(e).__name__}: {str(e)[:110]}")
        break
print(f"  GCLIDs resolved to a campaign: {len(gmap)} / {len(gclids)}")
print(f"  by campaign: {dict(Counter(v['campaign'] for v in gmap.values()))}")

print("\n=== UNIQUE QUALIFIED LEADS ATTRIBUTABLE TO THE FIVE PAID CAMPAIGNS ===")
QUAL_YES = {"yes"}
rows = []
for l in with_g:
    g = (l.get("gclid") or "").strip()
    m = gmap.get(g)
    if not m or m["campaign_id"] not in FIVE:
        continue
    dur = l.get("call_duration_seconds") or 0
    try:
        dur = int(dur)
    except Exception:
        dur = 0
    rows.append({
        "campaign": m["campaign"], "campaign_id": m["campaign_id"],
        "click_date": m["click_date"], "lead_date": (l.get("date_created") or "")[:10],
        "lead_type": l.get("lead_type"), "lead_status": l.get("lead_status"),
        "quotable": str(l.get("quotable")), "spam": l.get("spam"),
        "duplicate": l.get("duplicate"), "call_duration_seconds": dur,
        "sales_value": l.get("sales_value"), "quote_value": l.get("quote_value"),
        "lead_key": hashlib.sha256(g.encode()).hexdigest()[:16]})
print(f"  paid-attributable lead rows: {len(rows)}")
if rows:
    for r in rows:
        meets = ((r["lead_type"] == "Web Form") or
                 (r["lead_type"] in ("Phone Call", "Text Message")
                  and r["call_duration_seconds"] >= 60))
        r["meets_60s_or_form"] = meets
        r["unique_qualified"] = (r["lead_status"] == "Unique" and r["quotable"].lower() in QUAL_YES
                                 and meets and not r["spam"])
    print(f"  {'campaign':<20}{'clickdate':<12}{'type':<14}{'status':<9}{'quotable':<10}"
          f"{'secs':>6}{'unique_qualified':>18}")
    for r in sorted(rows, key=lambda z: (z["campaign"], z["click_date"])):
        print(f"  {r['campaign']:<20}{r['click_date']:<12}{str(r['lead_type']):<14}"
              f"{str(r['lead_status']):<9}{r['quotable']:<10}{r['call_duration_seconds']:>6}"
              f"{str(r['unique_qualified']):>18}")
    agg = defaultdict(lambda: {"rows": 0, "unique_qualified": 0})
    for r in rows:
        agg[r["campaign"]]["rows"] += 1
        agg[r["campaign"]]["unique_qualified"] += 1 if r["unique_qualified"] else 0
    print(f"\n  UNIQUE QUALIFIED LEADS BY CAMPAIGN: "
          f"{ {k: v['unique_qualified'] for k, v in agg.items()} }")
else:
    print("  none: no GCLID from WhatConverts resolves to one of the five paid campaigns.")

print("\n=== COST PER UNIQUE QUALIFIED LEAD ===")
MAXQ = {"AC Repair": 150.0, "HVAC Repair": 250.0, "HVAC Installation": 280.0,
        "HVAC Replacement": 280.0, "Gas Boiler Repair": 250.0}
cost = {}
for r in q(c, f"SELECT campaign.id, metrics.cost_micros, metrics.conversions FROM campaign "
              f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '{START}' AND '2026-09-09'"):
    cost[NAME[str(r.campaign.id)]] = {"cost": round(r.metrics.cost_micros / 1e6, 2),
                                      "records": round(r.metrics.conversions, 2)}
uq = {k: v["unique_qualified"] for k, v in
      (agg.items() if rows else [])} if rows else {}
print(f"  {'campaign':<20}{'cost':>10}{'records':>9}{'uniqQL':>8}{'CPQL':>11}{'maxCPQL':>9}"
      f"  verdict")
for k in ["AC Repair", "HVAC Repair", "HVAC Installation", "HVAC Replacement",
          "Gas Boiler Repair"]:
    cv = cost.get(k, {"cost": 0, "records": 0})
    n = uq.get(k, 0)
    cpql = cv["cost"] / n if n else None
    verdict = "-" if cpql is None else ("WITHIN" if cpql <= MAXQ[k] else "OVER")
    print(f"  {k:<20}{cv['cost']:>10.2f}{cv['records']:>9.0f}{n:>8}"
          f"{(f'{cpql:.2f}' if cpql else 'n/a'):>11}{MAXQ[k]:>9.0f}  {verdict}")

out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "window": [START, END], "profile": PROFILE,
       "total_leads": len(leads), "rows_with_gclid": len(with_g),
       "gclids_resolved": len(gmap),
       "aggregate": {
           "lead_type": dict(Counter(str(l.get("lead_type")) for l in safe)),
           "lead_status": dict(Counter(str(l.get("lead_status")) for l in safe)),
           "quotable": dict(Counter(str(l.get("quotable")) for l in safe)),
           "lead_source": dict(Counter(str(l.get("lead_source")) for l in safe))},
       "paid_attributable_rows": rows,
       "unique_qualified_by_campaign": uq,
       "cost_and_records": cost,
       "pii_policy": "names, numbers, emails, addresses, IPs, recordings and transcripts are "
                     "excluded before any write; GCLID is stored only as a 16-char SHA-256 prefix"}
p = EVID / "2026-09-10-whatconverts-lead-analysis.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p.relative_to(ROOT)}  (no PII, no credentials)")
