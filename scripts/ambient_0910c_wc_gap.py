#!/usr/bin/env python3
"""WhatConverts labels 21 leads lead_medium=cpc but only 8 carry a click identifier.
Either 13 paid leads lost their click ID, or the label is wrong. Find out which, because
it decides whether CPQL is being overstated. Counts only, no PII."""
from __future__ import annotations
import base64, json, os, sys, urllib.request, urllib.parse, datetime, hashlib, re
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
PROFILE, START, END = "105803", "2026-08-14", "2026-09-10"
auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()
ATTR = ("gclid", "gbraid", "wbraid", "utm_source", "utm_medium", "utm_campaign",
        "campaignid", "adgroupid", "keyword", "matchtype", "device")


def fetch(page):
    url = (f"https://app.whatconverts.com/api/v1/leads?profile_id={PROFILE}"
           f"&start_date={START}&end_date={END}&leads_per_page=250&page_number={page}")
    r = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}",
                                             "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def params(u):
    if not isinstance(u, str) or not u:
        return {}
    try:
        qs = urllib.parse.parse_qs(urllib.parse.urlsplit(u).query)
        return {k.lower(): qs[k][0][:120] for k in qs if k.lower() in ATTR}
    except Exception:
        return {}


leads, page = [], 1
while True:
    d = fetch(page)
    got = d.get("leads", [])
    leads += got
    if page >= (d.get("total_pages") or 1) or not got:
        break
    page += 1

rows = []
for l in leads:
    a = {}
    for f in ("landing_url", "lead_url"):
        a.update(params(l.get(f)))
    for k in ATTR:
        v = l.get(k)
        if isinstance(v, str) and v.strip():
            a.setdefault(k, v.strip()[:120])
    dur = l.get("call_duration_seconds") or 0
    try:
        dur = int(dur)
    except Exception:
        dur = 0
    rows.append({"date": (l.get("date_created") or "")[:10],
                 "src": str(l.get("lead_source")), "med": str(l.get("lead_medium")),
                 "type": str(l.get("lead_type")), "status": str(l.get("lead_status")),
                 "quotable": str(l.get("quotable")), "spam": l.get("spam"),
                 "secs": dur,
                 "has_gclid": bool(a.get("gclid")),
                 "has_gbraid": bool(a.get("gbraid") or a.get("wbraid")),
                 "has_utm": bool(a.get("utm_source")),
                 "has_vt": bool(a.get("campaignid")),
                 "landing_url_present": bool(str(l.get("landing_url") or "").strip()),
                 "gclid": a.get("gclid"), "attr_keys": sorted(a)})

print(f"=== {len(rows)} LEADS: DOES THE 'cpc' LABEL COME WITH A CLICK ID? ===")
print(f"  {'lead_source':<32}{'lead_medium':<12}{'n':>4}{'gclid':>7}{'gbraid':>8}"
      f"{'utm':>6}{'valtrack':>10}{'landingURL':>12}")
grp = defaultdict(list)
for r in rows:
    grp[(r["src"], r["med"])].append(r)
for (s, m), v in sorted(grp.items(), key=lambda z: -len(z[1])):
    print(f"  {s:<32}{m:<12}{len(v):>4}"
          f"{sum(x['has_gclid'] for x in v):>7}{sum(x['has_gbraid'] for x in v):>8}"
          f"{sum(x['has_utm'] for x in v):>6}{sum(x['has_vt'] for x in v):>10}"
          f"{sum(x['landing_url_present'] for x in v):>12}")

cpc = [r for r in rows if r["med"] == "cpc"]
withid = [r for r in cpc if r["has_gclid"] or r["has_gbraid"] or r["has_vt"]]
print(f"\n=== THE lead_medium='cpc' COHORT ===")
print(f"  labelled cpc                        : {len(cpc)}")
print(f"  of those, carrying a click id       : {len(withid)}")
print(f"  labelled cpc with NO click id       : {len(cpc) - len(withid)}")
print(f"  of those, landing_url captured      : "
      f"{sum(1 for r in cpc if not (r['has_gclid'] or r['has_gbraid'] or r['has_vt']) and r['landing_url_present'])}")
print(f"  their lead_type                     : "
      f"{dict(Counter(r['type'] for r in cpc if not (r['has_gclid'] or r['has_gbraid'] or r['has_vt'])))}")
print(f"  their dates                         : "
      f"{sorted({r['date'] for r in cpc if not (r['has_gclid'] or r['has_gbraid'] or r['has_vt'])})}")

print("\n=== COULD THOSE UNIDENTIFIED cpc LEADS BE REAL PAID CLICKS? ===")
c = client()
identity_gate(c, verbose=False)
noid_dates = sorted({r["date"] for r in cpc
                     if not (r["has_gclid"] or r["has_gbraid"] or r["has_vt"]) and r["date"]})
print(f"  {'date':<12}{'valid clicks on the five':>26}{'cpc leads w/o id':>19}")
byday = Counter(r["date"] for r in cpc
                if not (r["has_gclid"] or r["has_gbraid"] or r["has_vt"]))
clicks = {}
for r in q(c, f"SELECT segments.date, metrics.clicks FROM campaign "
              f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' "
              f"AND '2026-09-10'"):
    clicks[r.segments.date] = clicks.get(r.segments.date, 0) + r.metrics.clicks
zero = 0
for d in noid_dates:
    n = clicks.get(d, 0)
    if n == 0:
        zero += byday[d]
    print(f"  {d:<12}{n:>26}{byday[d]:>19}"
          f"{'   <-- ZERO paid clicks that day' if n == 0 else ''}")
print(f"\n  cpc-labelled leads with no click id landing on a day with ZERO paid clicks: {zero}")
print(f"  -> those cannot be paid-search leads from these five campaigns.")

print("\n=== gbraid / wbraid ROWS ===")
gb = [r for r in rows if r["has_gbraid"]]
print(f"  rows carrying gbraid or wbraid: {len(gb)}")
print(f"  of those, ALSO carrying gclid : {sum(1 for r in gb if r['has_gclid'])}")
print(f"  gbraid-only (no gclid)        : {sum(1 for r in gb if not r['has_gclid'])}")
print("  gbraid/wbraid identify iOS/app paid clicks that click_view cannot join by gclid.")
print("  Google Ads has no gbraid lookup in GAQL, so these are unjoinable by design.")

out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "total_leads": len(rows),
       "source_medium_matrix": {f"{s} | {m}": {
           "n": len(v), "gclid": sum(x["has_gclid"] for x in v),
           "gbraid": sum(x["has_gbraid"] for x in v),
           "utm": sum(x["has_utm"] for x in v),
           "valuetrack": sum(x["has_vt"] for x in v),
           "landing_url_present": sum(x["landing_url_present"] for x in v)}
           for (s, m), v in grp.items()},
       "cpc_cohort": {"labelled_cpc": len(cpc), "with_click_id": len(withid),
                      "without_click_id": len(cpc) - len(withid),
                      "without_id_on_zero_click_days": zero},
       "gbraid_rows": len(gb),
       "gbraid_only": sum(1 for r in gb if not r["has_gclid"])}
p = EVID / "2026-09-10c-wc-attribution-gap.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p.relative_to(ROOT)}")
