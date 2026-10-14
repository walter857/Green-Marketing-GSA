#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: Google Ads calls in WhatConverts that nobody answered, 2026-01-01..09-26.

"From Google Ads" = calls on the paid-search tracking numbers (phone_name "GSA's Traffic",
"GLE Traffic"). Local Services Ads ("LSA's Traffic") are reported separately. Pulls the
default, duplicate and spam sets (the API hides the last two by default) and classifies each
call from WhatConverts' answer status plus the carrier recording found in the transcript.
Prints dates, number names, durations and outcomes only - no caller data.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import requests  # noqa: E402
from requests.auth import HTTPBasicAuth  # noqa: E402
from gm_gsa.config import load_dotenv_if_available  # noqa: E402

load_dotenv_if_available(ROOT / ".env")
AUTH = HTTPBasicAuth(os.environ["WHATCONVERTS_API_TOKEN"].strip(), os.environ["WHATCONVERTS_SECRET"].strip())
NY = ZoneInfo("America/New_York")
CT = ZoneInfo("America/Chicago")
FAIL = re.compile(r"not been set up yet|try your call again later", re.I)
VM = re.compile(r"leave (a|your) (message|name)|after the (tone|beep)|voice ?mail", re.I)
PAID = ("GSA's Traffic", "GLE Traffic")
OUT = ROOT / "clients" / "mastergrass-lawn-care" / "snapshots" / "audit-2026-09-26"


def pull(**extra):
    out, page = [], 1
    while True:
        r = requests.get("https://app.whatconverts.com/api/v1/leads", auth=AUTH, timeout=60, params=dict(
            account_id=64716, profile_id=94840, start_date="2026-01-01", end_date="2026-09-26",
            lead_type="phone_call", leads_per_page=250, page_number=page, **extra))
        r.raise_for_status()
        b = r.json().get("leads", [])
        out += b
        if len(b) < 250:
            return out
        page += 1


by_id = {}
for name, ex in (("default", {}), ("duplicate", {"duplicate": "true"}), ("spam", {"spam": "true"})):
    for l in pull(**ex):
        assert str(l.get("account_id")) == "64716"
        by_id.setdefault(l["lead_id"], (name, l))
calls = list(by_id.values())
print(f"2026 phone calls (all sets): {len(calls)} | by number:",
      dict(Counter(l.get("phone_name") for _, l in calls).most_common()))


def outcome(l):
    a = l.get("answer_status") or ""
    tx = str(l.get("call_transcription") or "")
    d = l.get("call_duration_seconds") or 0
    if a == "No Answer":
        return "MISSED - no answer"
    if a == "Call Canceled":
        return "MISSED - caller hung up while ringing"
    if FAIL.search(tx):
        return "MISSED - voicemail not set up"
    if VM.search(tx) and not re.search(r"master ?grass", tx, re.I):
        return "MISSED - went to voicemail"
    if d >= 60:
        return "ANSWERED - conversation 60s+"
    return "ANSWERED - under 60s"


rows = []
for s, l in calls:
    t = datetime.datetime.fromisoformat(l["date_created"].replace("Z", "+00:00"))
    rows.append(dict(set=s, num=l.get("phone_name"), t_ct=t.astimezone(CT), month=t.astimezone(CT).strftime("%Y-%m"),
                     dur=l.get("call_duration_seconds") or 0, ans=l.get("answer_status"), out=outcome(l),
                     status=l.get("lead_status"), src=f"{l.get('lead_source')}/{l.get('lead_medium')}",
                     quotable=l.get("quotable")))

for label, nums in (("GOOGLE ADS SEARCH (GSA's + GLE numbers)", PAID), ("LOCAL SERVICES ADS (LSA's number)", ("LSA's Traffic",)),
                    ("ALL NUMBERS", None)):
    sel = [r for r in rows if (nums is None or r["num"] in nums) and r["set"] != "spam"]
    months = sorted({r["month"] for r in sel})
    outs = ["ANSWERED - conversation 60s+", "ANSWERED - under 60s", "MISSED - voicemail not set up",
            "MISSED - no answer", "MISSED - caller hung up while ringing", "MISSED - went to voicemail"]
    c = Counter((r["month"], r["out"]) for r in sel)
    print(f"\n=== {label}: {len(sel)} calls (spam excluded) ===")
    print(f"{'month':<8}{'calls':>6} | " + " | ".join(o.replace('ANSWERED - ', 'ans ').replace('MISSED - ', 'miss ')[:22] for o in outs) + " | missed total")
    for m in months:
        n = sum(1 for r in sel if r["month"] == m)
        missed = sum(c[(m, o)] for o in outs if o.startswith("MISSED"))
        print(f"{m:<8}{n:>6} | " + " | ".join(f"{c[(m, o)]:>22}" for o in outs) + f" | {missed:>4} ({missed/n:.0%})")
    tot = Counter(r["out"] for r in sel)
    missed = sum(v for k, v in tot.items() if k.startswith("MISSED"))
    print(f"TOTAL   {len(sel):>6} | " + " | ".join(f"{tot[o]:>22}" for o in outs) + f" | {missed:>4} ({missed/max(len(sel),1):.0%})")

print("\n=== every missed Google Ads Search call (Central time) ===")
for r in sorted(rows, key=lambda r: r["t_ct"]):
    if r["num"] in PAID and r["out"].startswith("MISSED"):
        print(f"  {r['t_ct']:%Y-%m-%d %a %H:%M} CT  {r['num']:<14} {r['dur']:>4}s  {r['out']:<40} WC set={r['set']:<9} status={r['status']}")
print("\n=== Google Ads Search calls by hour of day (Central), answered vs missed ===")
h = defaultdict(Counter)
for r in rows:
    if r["num"] in PAID and r["set"] != "spam":
        h[r["t_ct"].hour]["missed" if r["out"].startswith("MISSED") else "answered"] += 1
for k in sorted(h):
    print(f"  {k:02d}:00  answered {h[k]['answered']:>3}  missed {h[k]['missed']:>3}")
(OUT / "wc_calls_2026_outcomes.json").write_text(json.dumps(
    [{k: (v.isoformat() if isinstance(v, datetime.datetime) else v) for k, v in r.items()} for r in rows], indent=0), encoding="utf-8")
