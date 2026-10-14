#!/usr/bin/env python3
"""2026-09-28 READ-ONLY: WhatConverts leads that belong to Google Ads but are labelled otherwise.

Pulls every 2026 WhatConverts lead for Master Grass (default + duplicate + spam sets) and Google Ads
evidence (call_view, 90 days of click_view gclids, conversions by conversion date) and classifies
each lead by the STRONGEST paid evidence it has:

  P1  call matched to a Google forwarding-number call (call_view AD / LANDING_PAGE) by time + duration
  P2  WhatConverts gclid equals a Google Ads click_view gclid
  P3  call or text on a paid-search tracking number (GSA's Traffic / GLE Traffic)
  P4  gclid / gbraid / wbraid present in the lead's landing URL or gclid field, not matchable in click_view
  S1  landing URL on the paid-only offer subdomain with no click id   (strong, not proof)
  W1  GBP-number call on a day Google Ads logged a Maps/location "Clicks to call" (weak)

Contact data never leaves this process: caller numbers become a per-run salted hash and an area code.
Output: lead-level rows with time, type, WC source/medium, number name, duration and evidence only.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import secrets
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import ROOT, E, client, q  # noqa: E402

import requests  # noqa: E402
from requests.auth import HTTPBasicAuth  # noqa: E402
from gm_gsa.config import load_dotenv_if_available  # noqa: E402

load_dotenv_if_available(ROOT / ".env")
AUTH = HTTPBasicAuth(os.environ["WHATCONVERTS_API_TOKEN"].strip(), os.environ["WHATCONVERTS_SECRET"].strip())
NY = ZoneInfo("America/New_York")
OUT = ROOT / "clients" / "mastergrass-lawn-care" / "snapshots" / "attribution-2026-09-28"
OUT.mkdir(parents=True, exist_ok=True)
SALT = secrets.token_bytes(16)
PAID_NUMS = {"GSA's Traffic", "GLE Traffic"}
TODAY = datetime.date(2026, 9, 28)


# ------------------------------------------------------------------ WhatConverts
def pull(**extra):
    out, page = [], 1
    while True:
        r = requests.get("https://app.whatconverts.com/api/v1/leads", auth=AUTH, timeout=60, params=dict(
            account_id=64716, profile_id=94840, start_date="2026-01-01", end_date=str(TODAY),
            leads_per_page=250, page_number=page, **extra))
        r.raise_for_status()
        b = r.json().get("leads", [])
        out += b
        if len(b) < 250:
            return out
        page += 1


leads = {}
for name, ex in (("default", {}), ("duplicate", {"duplicate": "true"}), ("spam", {"spam": "true"})):
    for l in pull(**ex):
        assert str(l.get("account_id")) == "64716"
        leads.setdefault(l["lead_id"], (name, l))
print(f"WhatConverts 2026 leads: {len(leads)} ({dict(Counter(s for s, _ in leads.values()))})")


def digits(v):
    return "".join(ch for ch in str(v or "") if ch.isdigit())[-10:]


def click_ids(l):
    ids = {}
    if l.get("gclid"):
        ids["gclid"] = str(l["gclid"])
    for f in ("landing_url", "lead_url"):
        u = str(l.get(f) or "")
        qs = parse_qs(urlparse(u).query)
        for k in ("gclid", "gbraid", "wbraid"):
            if qs.get(k):
                ids.setdefault(k, qs[k][0])
        if "utm_medium=cpc" in u or "utm_source=google" in u:
            ids.setdefault("utm_cpc", "1")
    return ids


rows = []
for s, l in leads.values():
    t = datetime.datetime.fromisoformat(l["date_created"].replace("Z", "+00:00")).astimezone(NY)
    caller = digits(l.get("caller_number") or l.get("contact_phone_number"))
    rows.append({
        "lead_id": l["lead_id"], "set": s, "t": t, "type": l.get("lead_type"), "src": f"{l.get('lead_source')}/{l.get('lead_medium')}",
        "num": l.get("phone_name"), "dur": l.get("call_duration_seconds") or 0, "status": l.get("lead_status"),
        "quotable": l.get("quotable"), "landing": str(l.get("landing_url") or ""), "ids": click_ids(l),
        "area": caller[:3] if len(caller) == 10 else None,
        "chash": hashlib.sha256(SALT + caller.encode()).hexdigest()[:8] if caller else None,
        "ans": l.get("answer_status"),
        "fail": bool(re.search(r"not been set up yet|try your call again later", str(l.get("call_transcription") or ""), re.I)),
    })

# ------------------------------------------------------------------ Google Ads
c = client()
calls = []
for r in q(c, """SELECT call_view.start_call_date_time, call_view.call_duration_seconds, call_view.type,
                        call_view.call_tracking_display_location,
                        call_view.call_status, call_view.caller_area_code, campaign.id, campaign.name FROM call_view"""):
    v = r.call_view
    calls.append({"t": datetime.datetime.fromisoformat(v.start_call_date_time).replace(tzinfo=NY), "dur": v.call_duration_seconds,
                  "kind": E(v.call_tracking_display_location), "status": E(v.call_status), "area": v.caller_area_code, "camp": r.campaign.name})
gclids = {}
d = TODAY - datetime.timedelta(days=89)
while d <= TODAY:
    for r in q(c, f"SELECT click_view.gclid, campaign.name, segments.click_type FROM click_view WHERE segments.date = '{d}'"):
        gclids[r.click_view.gclid] = (str(d), r.campaign.name, E(r.segments.click_type))
    d += datetime.timedelta(days=1)
conv = defaultdict(Counter)
for r in q(c, """SELECT segments.date, segments.conversion_action_name, metrics.all_conversions_by_conversion_date
                 FROM campaign WHERE segments.date BETWEEN '2026-01-01' AND '2026-09-28'
                 AND metrics.all_conversions_by_conversion_date > 0"""):
    conv[r.segments.date][r.segments.conversion_action_name] += r.metrics.all_conversions_by_conversion_date
loc_calls = Counter()
for r in q(c, """SELECT segments.date, segments.click_type, metrics.clicks FROM campaign
                 WHERE segments.date BETWEEN '2026-01-01' AND '2026-09-28' AND segments.click_type IN ('CALLS','LOCATION_EXPANSION','GET_DIRECTIONS') AND metrics.clicks > 0"""):
    loc_calls[r.segments.date] += r.metrics.clicks
print(f"Google Ads: call_view {len(calls)} calls | click_view gclids (90 d) {len(gclids)} | days with call/location clicks {len(loc_calls)}")

# ------------------------------------------------------------------ matching
used = set()
pairs = []
for ri, r in enumerate(rows):
    if r["type"] != "Phone Call" or r["num"] not in PAID_NUMS:
        continue  # a Google forwarding number can only ring the call-asset / landing-page numbers
    for i, cv in enumerate(calls):
        dt = abs((r["t"] - cv["t"]).total_seconds())
        dd = abs(r["dur"] - cv["dur"])
        area_ok = (not cv["area"]) or (not r["area"]) or cv["area"] == r["area"]
        if dt <= 150 and dd <= 15 and area_ok:
            pairs.append((dt + 4 * dd, ri, i))
taken_r = set()
for score, ri, i in sorted(pairs):
    if ri in taken_r or i in used:
        continue
    taken_r.add(ri)
    used.add(i)
    rows[ri]["gfn"] = calls[i]


def is_paid_label(src):
    s = src.lower()
    return "cpc" in s or "ppc" in s or "paid" in s or "adwords" in s or "google ads" in s


for r in rows:
    ev = []
    if r.get("gfn"):
        ev.append(f"P1 Google forwarding-number call ({r['gfn']['kind']}, {r['gfn']['camp'][:24]})")
    g = r["ids"].get("gclid")
    if g and g in gclids:
        ev.append(f"P2 gclid matches a Google Ads click on {gclids[g][0]} ({gclids[g][1][:24]}, {gclids[g][2]})")
    if r["num"] in PAID_NUMS:
        ev.append(f"P3 paid-search tracking number ({r['num']})")
    if r["ids"] and not any(e.startswith("P2") for e in ev):
        ev.append("P4 click id in lead (" + ",".join(sorted(k for k in r["ids"])) + ")")
    if not ev and "offer.mastergrasslawncare.com" in r["landing"]:
        ev.append("S1 landed on paid-only offer page, no click id")
    ctc = conv.get(r["t"].date().isoformat(), {}).get("Clicks to call", 0)
    if not ev and r["num"] == "GBP Traffic" and r["type"] == "Phone Call" and ctc:
        ev.append(f"W1 GBP call on a day Google Ads logged {ctc:g} Maps-ad 'Clicks to call'")
    r["ev"] = ev
    r["tier"] = ev[0][:2] if ev else None
    r["paid_label"] = is_paid_label(r["src"])

# ------------------------------------------------------------------ report
paid = [r for r in rows if r["tier"] in ("P1", "P2", "P3", "P4") and r["set"] != "spam"]
mis = [r for r in paid if not r["paid_label"]]
ok = [r for r in paid if r["paid_label"]]
over = [r for r in rows if r["paid_label"] and not r["tier"] and r["set"] != "spam"]
print(f"\nProven Google Ads leads (P1-P4, spam excluded): {len(paid)} | labelled paid {len(ok)} | MISLABELLED {len(mis)}")
print(f"Probable (S1 offer page, no click id): {sum(1 for r in rows if r['tier'] == 'S1' and r['set'] != 'spam')} | "
      f"weak (W1 GBP call on Maps-click day): {sum(1 for r in rows if r['tier'] == 'W1' and r['set'] != 'spam')}")
print(f"Labelled paid with NO paid evidence (possible over-attribution): {len(over)}")
print(f"Google calls in call_view with no WhatConverts match: {len(calls) - len(used)}")


def fmt(r):
    creds = "; ".join(f"{k} {v:g}" for k, v in sorted(conv.get(r["t"].date().isoformat(), {}).items())
                      if k in ("WC Call Lead", "WC Form Lead", "Calls from ads", "MasterGrass - Lp - Phone Call Leads",
                               "MasterGrass - Lp - Submit Lead Form", "Clicks to call"))
    call_out = ("VOICEMAIL-NOT-SET-UP" if r["fail"] else r["ans"]) if r["type"] == "Phone Call" else ""
    return (f"  {r['t']:%Y-%m-%d %a %H:%M} {r['type'][:10]:<10} WC='{r['src'][:24]}' num={str(r['num'])[:14]:<14} "
            f"{r['dur'] or '':>4}s {call_out:<20} set={r['set']:<9} status={r['status']} q={r['quotable']} | "
            f"{r['ev'][0] if r['ev'] else 'no paid evidence'} | Ads conv that day: {creds or 'none'}")


print("\n=== MISLABELLED: proven Google Ads leads WhatConverts shows as non-paid ===")
for r in sorted(mis, key=lambda r: r["t"]):
    print(fmt(r))
print("\n=== PROBABLE (offer page, no click id), non-paid label ===")
for r in sorted([r for r in rows if r["tier"] == "S1" and not r["paid_label"] and r["set"] != "spam"], key=lambda r: r["t"]):
    print(fmt(r))
print("\n=== Correctly labelled paid leads (for comparison), by month ===")
print("  ", dict(Counter(r["t"].strftime("%Y-%m") for r in ok)))
print("\n=== Labelled paid but no paid evidence ===")
for r in sorted(over, key=lambda r: r["t"]):
    print(fmt(r))
print("\n=== Google forwarding-number calls with NO WhatConverts record ===")
for i, cv in enumerate(calls):
    if i not in used and cv["t"].date() >= datetime.date(2026, 1, 1):
        print(f"  {cv['t']:%Y-%m-%d %a %H:%M} {cv['dur']}s {cv['kind']} {cv['status']} {cv['camp'][:30]}")
json.dump([{k: (v.isoformat() if isinstance(v, datetime.datetime) else v) for k, v in r.items() if k not in ("landing", "ids", "chash")}
           | {"click_id_kinds": sorted(r["ids"]), "gfn": ({**r["gfn"], "t": r["gfn"]["t"].isoformat()} if r.get("gfn") else None)}
           for r in rows], open(OUT / "wc_attribution_rows.json", "w"), indent=0, default=str)

print("\n=== S1 web forms grouped by contact (hashed) ===")
grp = defaultdict(list)
for r in rows:
    if r["tier"] == "S1" and r["type"] == "Web Form":
        grp[r["chash"]].append(r)
for k, v in sorted(grp.items(), key=lambda kv: -len(kv[1])):
    days = sorted({x["t"].strftime("%m-%d") for x in v})
    print(f"  contact {k or 'no-phone'}: {len(v)} forms on {len(days)} day(s) {days} | statuses {dict(Counter(x['status'] for x in v))}")
print("\n=== Weak tier W1 bounded by Google's Clicks-to-call count ===")
wd = defaultdict(list)
for r in rows:
    if r["tier"] == "W1" and r["set"] != "spam":
        wd[r["t"].date().isoformat()].append(r)
tot_bound = 0
for d, v in sorted(wd.items()):
    n = conv[d].get("Clicks to call", 0)
    tot_bound += min(n, len(v))
    print(f"  {d}: GBP calls {len(v)} | Google 'Clicks to call' {n:g} -> at most {min(n, len(v)):g} could be Maps-ad calls")
print(f"  upper bound of Maps-ad calls sitting under 'GBP Traffic': {tot_bound:g}")
print("\n=== Google forwarding-number calls (2026) with NO WhatConverts record, by month/location ===")
um = Counter()
for i, cv in enumerate(calls):
    if i not in used and cv["t"].year == 2026:
        um[(cv["t"].strftime("%Y-%m"), cv["kind"], cv["camp"][:26])] += 1
for k, v in sorted(um.items()):
    print(f"  {k} {v}")
print("  all call_view calls by year:", dict(Counter(cv["t"].year for cv in calls)))
