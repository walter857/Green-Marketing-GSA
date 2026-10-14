#!/usr/bin/env python3
"""Ambient | READ-ONLY verifier for the 410-415-9517 call-asset route (configured 2026-09-25).

For every Google call record (call_view) and every WhatConverts lead on 410-415-9517 since
--since, it lines up the five layers the owner asked for:
  1 forwarding      WC destination_number == 4107610932
  2 WC record       lead on 415-9517, type Phone Call, source/medium
  3 Google record   call_view row within +/-3 min (campaign, ad group, duration, status)
  4 upload          (UI only) WC lead detail -> Conversions -> Google Ads: status + Conversion Name
                    Expected: WC Calls. A WC Lead upload for the same call = still double counting.
  5 credit          WC Calls / Calls from ads / WC Lead conversions by conversion date
Counts and times only; no caller numbers or names are printed.

    python ambient_0925_call_watch.py --since 2026-09-28
"""
from __future__ import annotations
import sys, argparse, datetime, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ambient_0909_lib import client, q, identity_gate, E, TZ, CLIENT_DIR
from gm_gsa.config import load_dotenv_if_available
from gm_gsa.whatconverts import fetch_leads

ap = argparse.ArgumentParser(); ap.add_argument("--since", default="2026-09-25"); a = ap.parse_args()
load_dotenv_if_available(Path(__file__).resolve().parents[1] / ".env")
c = client(); identity_gate(c, verbose=False)
today = datetime.datetime.now(TZ).date().isoformat()

calls = []
for r in q(c, f"""SELECT call_view.start_call_date_time, call_view.call_duration_seconds, call_view.call_status,
        call_view.type, call_view.call_tracking_display_location, campaign.id, campaign.name, ad_group.id
        FROM call_view WHERE call_view.start_call_date_time >= '{a.since} 00:00:00'"""):
    v = r.call_view
    calls.append((v.start_call_date_time, v.call_duration_seconds, E(v.call_status), E(v.call_tracking_display_location),
                  str(r.campaign.id), r.campaign.name[19:55], str(r.ad_group.id)))
print(f"GOOGLE call records since {a.since}: {len(calls)}")
for x in sorted(calls): print("  ", x)

leads = fetch_leads("115814", "105803", a.since, today, client_yaml=CLIENT_DIR / "client.yaml")["leads"]
w = [l for l in leads if str(l.get("tracking_number") or "").endswith("4159517")]
print(f"\nWHATCONVERTS leads on 410-415-9517 since {a.since}: {len(w)}")
def et(ts: str) -> datetime.datetime:
    # WhatConverts API timestamps are UTC; Google call_view times are in the account zone (ET)
    d = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d.astimezone(TZ).replace(tzinfo=None)
for l in w:
    t_et = et(str(l.get("date_created")))
    near = [x for x in calls if abs((datetime.datetime.fromisoformat(x[0]) - t_et).total_seconds()) <= 180]
    t = t_et.isoformat()
    print(f"  lead {l.get('lead_id')} {t[:16]}ET {l.get('lead_type')} {l.get('lead_source')}/{l.get('lead_medium')} "
          f"dest..{str(l.get('destination_number') or '')[-4:]} dur={l.get('call_duration')} google_match={'YES ' + str(near[0][4:7]) if near else 'NO'}")

acts = {"7643656075": "WC Calls", "1068114183": "Calls from ads", "7643656486": "WC Lead"}
cred = collections.Counter()
for r in q(c, f"""SELECT segments.conversion_action, segments.date, campaign.id, metrics.all_conversions_by_conversion_date
        FROM campaign WHERE segments.date BETWEEN '{a.since}' AND '{today}' AND metrics.all_conversions_by_conversion_date > 0"""):
    k = r.segments.conversion_action.split("/")[-1]
    if k in acts: cred[(acts[k], r.segments.date, str(r.campaign.id))] += r.metrics.all_conversions_by_conversion_date
print("\nGOOGLE credit by conversion date:", {k: round(v, 2) for k, v in cred.items()} or "none")
print("\nUpload layer is UI-only: open each lead above in WhatConverts -> Conversions -> Google Ads and record the"
      " status and Conversion Name (expect WC Calls, not WC Lead).")
