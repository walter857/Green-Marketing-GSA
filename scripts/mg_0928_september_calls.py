#!/usr/bin/env python3
"""2026-09-28 READ-ONLY: Master Grass September 2026 - every call, every missed call, callers never reached,
plus September Google Ads vs WhatConverts attribution.

Contact data stays in this process: callers become "Caller NN" labels from a per-run salted hash.
Lead IDs are printed so each missed call can be opened in WhatConverts for a call-back.
Writes reports/mastergrass-lawn-care/2026-09-28-september-calls.csv (no contact data).
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import os
import re
import secrets
import sys
from collections import Counter, defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import ROOT, E, client, q  # noqa: E402

import requests  # noqa: E402
from requests.auth import HTTPBasicAuth  # noqa: E402
from gm_gsa.config import load_dotenv_if_available  # noqa: E402

load_dotenv_if_available(ROOT / ".env")
AUTH = HTTPBasicAuth(os.environ["WHATCONVERTS_API_TOKEN"].strip(), os.environ["WHATCONVERTS_SECRET"].strip())
CT, NY = ZoneInfo("America/Chicago"), ZoneInfo("America/New_York")
SALT = secrets.token_bytes(16)
START, END = "2026-09-01", "2026-09-28"
PAID = {"GSA's Traffic": "Google Ads (search)", "GLE Traffic": "Google Ads (call ad)"}
FAIL = re.compile(r"not been set up yet|try your call again later", re.I)
VM = re.compile(r"leave (a|your) (message|name)|after the (tone|beep)|voice ?mail", re.I)
REP = ROOT / "reports" / "mastergrass-lawn-care"


def pull(**extra):
    out, page = [], 1
    while True:
        r = requests.get("https://app.whatconverts.com/api/v1/leads", auth=AUTH, timeout=60, params=dict(
            account_id=64716, profile_id=94840, start_date=START, end_date=END, leads_per_page=250, page_number=page, **extra))
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


def digits(v):
    return "".join(ch for ch in str(v or "") if ch.isdigit())[-10:]


def outcome(l):
    a, tx, d = l.get("answer_status") or "", str(l.get("call_transcription") or ""), l.get("call_duration_seconds") or 0
    if FAIL.search(tx):
        return "MISSED", "voicemail not set up (caller hung up on)"
    if a == "No Answer":
        return "MISSED", "no answer"
    if a == "Call Canceled":
        return "MISSED", "caller hung up while ringing"
    if VM.search(tx) and not re.search(r"master ?grass", tx, re.I):
        return "MISSED", "went to voicemail"
    if d >= 60:
        return "ANSWERED", "conversation 60s+"
    return "ANSWERED", "answered, under 60s"


def source(l):
    n = l.get("phone_name")
    return PAID.get(n) or {"GBP Traffic": "Google Business Profile", "LSA's Traffic": "Local Services Ads",
                          "FB Traffic": "Facebook", "Website Traffic": "Website"}.get(n, n or "Web form")


callers = {}
rows = []
for s, l in leads.values():
    t = datetime.datetime.fromisoformat(l["date_created"].replace("Z", "+00:00"))
    num = digits(l.get("caller_number") or l.get("contact_phone_number"))
    h = hashlib.sha256(SALT + num.encode()).hexdigest() if num else None
    if h and h not in callers:
        callers[h] = f"Caller {len(callers) + 1:02d}"
    r = {"lead_id": l["lead_id"], "set": s, "t_ct": t.astimezone(CT), "type": l.get("lead_type"), "source": source(l),
         "wc_label": f"{l.get('lead_source')}/{l.get('lead_medium')}", "dur": l.get("call_duration_seconds") or 0,
         "status": l.get("lead_status"), "caller": callers.get(h, "(no number)"), "quotable": l.get("quotable")}
    if r["type"] == "Phone Call":
        r["result"], r["detail"] = outcome(l)
    rows.append(r)
rows.sort(key=lambda r: r["t_ct"])
calls = [r for r in rows if r["type"] == "Phone Call"]
real = [r for r in calls if r["set"] != "spam"]

print(f"SEPTEMBER 1-28 WhatConverts: {len(rows)} leads | calls {len(calls)} (spam-flagged {sum(1 for r in calls if r['set'] == 'spam')}) | "
      f"texts {sum(1 for r in rows if r['type'] == 'Text Message')} | forms {sum(1 for r in rows if r['type'] == 'Web Form')}")
print("\n=== Calls by outcome (not spam) ===")
for k, v in Counter((r["result"], r["detail"]) for r in real).most_common():
    print(f"  {k[0]:<9} {k[1]:<42} {v}")
m = sum(1 for r in real if r["result"] == "MISSED")
print(f"  MISSED {m} of {len(real)} = {m / len(real):.0%}")
print("\n=== Missed rate by source ===")
for src in sorted({r["source"] for r in real}):
    sub = [r for r in real if r["source"] == src]
    mm = sum(1 for r in sub if r["result"] == "MISSED")
    conv = sum(1 for r in sub if r["detail"] == "conversation 60s+")
    print(f"  {src:<26} calls {len(sub):>3} | missed {mm:>3} ({mm / len(sub):.0%}) | real conversations {conv}")
print("\n=== Spam-flagged calls that were really the dead voicemail (possible hidden leads) ===")
sp = [r for r in calls if r["set"] == "spam"]
print(f"  spam-flagged calls {len(sp)} | of which voicemail-not-set-up {sum(1 for r in sp if r['detail'].startswith('voicemail not set up'))}"
      f" | by source {dict(Counter(r['source'] for r in sp))}")
print("\n=== Missed calls by weekday / hour (Central time, not spam) ===")
wd = Counter(r["t_ct"].strftime("%a") for r in real if r["result"] == "MISSED")
hr = Counter(r["t_ct"].hour for r in real if r["result"] == "MISSED")
print("  weekday:", {d: wd.get(d, 0) for d in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")})
print("  hour   :", {f"{h:02d}": hr[h] for h in sorted(hr)})

# caller roll-up: did the person ever reach someone in September, or leave a text / form?
byc = defaultdict(list)
for r in rows:
    if r["caller"] != "(no number)" and r["set"] != "spam":
        byc[r["caller"]].append(r)
never = []
for cid, rs in byc.items():
    cs = [r for r in rs if r["type"] == "Phone Call"]
    if not cs:
        continue
    reached = any(r["detail"] == "conversation 60s+" for r in cs)
    short_ans = any(r["detail"] == "answered, under 60s" for r in cs)
    texted = any(r["type"] == "Text Message" for r in rs)
    if not reached:
        never.append((cid, cs, short_ans, texted))
print(f"\n=== Callers in September: {sum(1 for rs in byc.values() if any(r['type'] == 'Phone Call' for r in rs))} | "
      f"NEVER had a 60s+ conversation: {len(never)} "
      f"(of which only ever missed: {sum(1 for n in never if all(r['result'] == 'MISSED' for r in n[1]))}) ===")
print("  caller     | calls | sources | first / last call (CT) | results | also texted | WhatConverts lead IDs")
for cid, cs, short_ans, texted in sorted(never, key=lambda n: n[1][0]["t_ct"]):
    print(f"  {cid:<10} | {len(cs)} | {', '.join(sorted({r['source'] for r in cs}))[:40]:<40} | "
          f"{cs[0]['t_ct']:%m-%d %a %H:%M} / {cs[-1]['t_ct']:%m-%d %H:%M} | "
          f"{', '.join(sorted({r['detail'] for r in cs}))[:60]:<60} | {'yes' if texted else 'no'} | {', '.join(str(r['lead_id']) for r in cs)}")

# ---------------- Google Ads September
c = client()
print("\n=== Google Ads September 1-28 ===")
tot = Counter()
for r in q(c, f"""SELECT campaign.name, metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions
                  FROM campaign WHERE segments.date BETWEEN '{START}' AND '{END}' AND metrics.impressions > 0"""):
    print(f"  {r.campaign.name[:40]:<40} spend ${r.metrics.cost_micros / 1e6:>8.2f} clicks {r.metrics.clicks:>3} impr {r.metrics.impressions:>5} conv {r.metrics.conversions:.1f}")
    tot["spend"] += r.metrics.cost_micros / 1e6
    tot["clicks"] += r.metrics.clicks
    tot["conv"] += r.metrics.conversions
print(f"  TOTAL spend ${tot['spend']:.2f} | clicks {tot['clicks']} | Google Ads conversions {tot['conv']:.1f}")
act = Counter()
for r in q(c, f"""SELECT segments.conversion_action_name, metrics.all_conversions_by_conversion_date FROM campaign
                  WHERE segments.date BETWEEN '{START}' AND '{END}' AND metrics.all_conversions_by_conversion_date > 0"""):
    act[r.segments.conversion_action_name] += r.metrics.all_conversions_by_conversion_date
print("  conversions by action (by conversion date):", {k: round(v, 1) for k, v in act.items()})
gcalls = [(datetime.datetime.fromisoformat(v.call_view.start_call_date_time).replace(tzinfo=NY).astimezone(CT), v.call_view.call_duration_seconds,
           E(v.call_view.call_tracking_display_location)) for v in q(c, "SELECT call_view.start_call_date_time, call_view.call_duration_seconds, call_view.call_tracking_display_location FROM call_view")]
gs = [g for g in gcalls if g[0].strftime("%Y-%m") == "2026-09"]
print(f"  Google forwarding-number calls in September: {len(gs)} -> {[f'{g[0]:%m-%d %H:%M} {g[1]}s {g[2]}' for g in gs]}")
paid = [r for r in rows if r["source"].startswith("Google Ads") or (r["type"] == "Web Form" and "cpc" in r["wc_label"].lower())]
print("\n=== September Google Ads leads in WhatConverts (paid numbers + paid forms) ===")
for r in paid:
    print(f"  {r['t_ct']:%m-%d %a %H:%M} CT {r['type']:<10} {r['source']:<22} WC label '{r['wc_label']}' {r['dur'] or ''}s "
          f"{r.get('detail', '')} | set={r['set']} status={r['status']} | lead {r['lead_id']}")

REP.mkdir(parents=True, exist_ok=True)
with (REP / "2026-09-28-september-calls.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["whatconverts_lead_id", "date_time_central", "weekday", "source", "whatconverts_label", "duration_s",
                "result", "detail", "caller", "whatconverts_set", "lead_status", "never_reached_in_september"])
    nv = {n[0] for n in never}
    for r in calls:
        w.writerow([r["lead_id"], f"{r['t_ct']:%Y-%m-%d %H:%M}", r["t_ct"].strftime("%a"), r["source"], r["wc_label"], r["dur"],
                    r["result"], r["detail"], r["caller"], r["set"], r["status"], "yes" if r["caller"] in nv else ""])
print("\nwrote reports/mastergrass-lawn-care/2026-09-28-september-calls.csv")
