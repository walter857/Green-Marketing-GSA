#!/usr/bin/env python3
"""Ambient | Match WhatConverts calls against Google's own call records.

READ-ONLY. EXTERNAL WRITES: 0.

Duration over 59s makes a call a CANDIDATE for upload. It does not make it ELIGIBLE.
Eligibility needs a Google forwarding number, i.e. Google must hold its own record of the
call. This joins the two sides on start time + duration to find out which WhatConverts
calls Google actually knows about.

Customer phone numbers are never printed.
"""
from __future__ import annotations
import os, sys, json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from requests.auth import HTTPBasicAuth
from gm_gsa.config import load_dotenv_if_available
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-24"
load_dotenv_if_available(ROOT / ".env")
AUTH = HTTPBasicAuth(os.environ["WHATCONVERTS_API_TOKEN"].strip(),
                     os.environ["WHATCONVERTS_SECRET"].strip())
WCB = "https://app.whatconverts.com/api/v1"
ACCT, PROF = "115814", "105803"
ASSET_NUM = "4107056354"          # the number on Google Ads call asset 407995613637


def wc(path, **kw):
    r = requests.get(f"{WCB}/{path}", auth=AUTH, params=kw, timeout=45)
    return r.status_code, (r.json()
                           if r.headers.get("content-type", "").startswith("application/json")
                           else r.text[:150])


def digits(s):
    return "".join(ch for ch in str(s or "") if ch.isdigit())[-10:]


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0, "pii_printed": False}

    # ---------------------------------------------- 1. Google's own call records
    print("=== 1. GOOGLE call_view - what Google itself recorded ===")
    gcalls = []
    fields_ok = True
    try:
        for r in q(c, """SELECT call_view.resource_name, call_view.caller_country_code,
                         call_view.caller_area_code, call_view.call_duration_seconds,
                         call_view.start_call_date_time, call_view.end_call_date_time,
                         call_view.call_status, call_view.type,
                         call_view.call_tracking_display_location,
                         campaign.id, campaign.name FROM call_view"""):
            v = r.call_view
            gcalls.append({"start": v.start_call_date_time,
                           "dur": v.call_duration_seconds,
                           "area": v.caller_area_code,
                           "status": E(v.call_status), "type": E(v.type_),
                           "display_loc": E(v.call_tracking_display_location),
                           "campaign_id": str(r.campaign.id),
                           "campaign": r.campaign.name})
    except Exception as ex:
        fields_ok = False
        print(f"   field error: {str(ex)[:200]}")
    print(f"   {len(gcalls)} Google call records")
    if gcalls:
        by_loc, by_type = {}, {}
        for g in gcalls:
            by_loc[g["display_loc"]] = by_loc.get(g["display_loc"], 0) + 1
            by_type[g["type"]] = by_type.get(g["type"], 0) + 1
        print(f"   by display location: {by_loc}")
        print(f"   by type            : {by_type}")
        ds = sorted(g["start"][:10] for g in gcalls if g["start"])
        print(f"   date range         : {ds[0]} .. {ds[-1]}")
        recent = [g for g in gcalls if g["start"] and g["start"][:10] >= "2026-08-01"]
        print(f"   since 2026-08-01    : {len(recent)}")
    out["google_call_records"] = len(gcalls)
    out["google_calls"] = gcalls[:400]

    # ------------------------------------------------ 2. WhatConverts calls
    print("\n=== 2. WHATCONVERTS calls on the Ads call-asset number ===")
    leads, page = [], 1
    while page <= 20:
        code, body = wc("leads", account_id=ACCT, profile_id=PROF,
                        start_date="2026-01-01", end_date="2026-09-24",
                        page_number=page, leads_per_page=250)
        if code != 200 or not isinstance(body, dict):
            break
        batch = body.get("leads", [])
        leads += batch
        if len(batch) < 250:
            break
        page += 1
    calls = [l for l in leads if l.get("lead_type") == "Phone Call"]
    asset = [l for l in calls if digits(l.get("tracking_number")) == ASSET_NUM]

    def dur(l):
        v = l.get("call_duration_seconds")
        if v in (None, ""):
            v = l.get("call_duration")
        try:
            return int(v)
        except Exception:
            return 0

    cand = [l for l in asset if dur(l) > 59]
    print(f"   {len(calls)} WC phone calls in 2026; {len(asset)} on {ASSET_NUM}; "
          f"{len(cand)} over 59s (CANDIDATES, not yet eligible)")

    # ------------------------------------- 3. join on start time + duration
    print("\n=== 3. JOIN: which WC candidates does Google also hold a record for? ===")

    def parse(ts):
        if not ts:
            return None
        t = str(ts).replace("Z", "+00:00")
        try:
            d = datetime.datetime.fromisoformat(t)
            return d if d.tzinfo else d.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            return None

    gidx = []
    for g in gcalls:
        p = parse(g["start"])
        if p:
            gidx.append((p, g))
    matched, unmatched = [], []
    for l in cand:
        lt = parse(l.get("date_created"))
        ld = dur(l)
        hit = None
        if lt:
            for gp, g in gidx:
                # Google timestamps are account-local; WC are UTC. Allow a wide window
                # and require the duration to agree within 5s, which is the real key.
                delta = abs((gp - lt).total_seconds())
                if delta <= 6 * 3600 and abs((g["dur"] or 0) - ld) <= 5:
                    hit = {"delta_s": round(delta), "g_dur": g["dur"],
                           "g_type": g["type"], "g_loc": g["display_loc"],
                           "g_campaign": g["campaign"][:40]}
                    break
        row = {"wc_date": l.get("date_created"), "wc_dur": ld,
               "src": f"{l.get('lead_source')}/{l.get('lead_medium')}",
               "google_record": hit}
        (matched if hit else unmatched).append(row)
    print(f"   candidates with a matching Google record : {len(matched)}")
    print(f"   candidates with NO matching Google record: {len(unmatched)}")
    print("\n   --- MATCHED (Google has a record -> import is possible) ---")
    for m in matched[:15]:
        g = m["google_record"]
        print(f"     {m['wc_date']} wc_dur={m['wc_dur']:4d}s {m['src'][:18]:18s} "
              f"| g_dur={g['g_dur']:4d}s {g['g_type'][:22]:22s} {g['g_loc'][:18]}")
    print("\n   --- UNMATCHED (no Google record -> import correctly ignored) ---")
    for u in unmatched[:15]:
        print(f"     {u['wc_date']} wc_dur={u['wc_dur']:4d}s {u['src'][:18]:18s}")
    out["candidates"] = len(cand)
    out["matched_to_google"] = matched
    out["unmatched"] = unmatched

    # ------------------------------------------- 4. upload diagnostics in Ads
    print("\n=== 4. GOOGLE ADS SIDE: has ANY upload ever landed on WC Calls? ===")
    tot = {}
    for r in q(c, """SELECT segments.conversion_action,
                     segments.conversion_action_name, metrics.all_conversions
                     FROM customer
                     WHERE segments.date BETWEEN '2026-01-01' AND '2026-09-24'"""):
        aid = r.segments.conversion_action.rsplit("/", 1)[-1]
        tot[aid] = tot.get(aid, 0) + r.metrics.all_conversions
    print(f"   WC Calls  7643656075 : {tot.get('7643656075', 0):.2f} all_conversions in 2026")
    print(f"   WC Lead   7643656486 : {tot.get('7643656486', 0):.2f}")
    print(f"   Calls from ads        : {tot.get('1068114183', 0):.2f}")
    out["2026_all_conversions"] = {k: round(v, 2) for k, v in tot.items()}

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"call-match-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0 | NO CUSTOMER PHONE NUMBERS PRINTED")


if __name__ == "__main__":
    main()
