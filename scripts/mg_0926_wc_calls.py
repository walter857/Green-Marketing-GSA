#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: Master Grass WhatConverts call forensics, 2026-06-01..09-26.

Pulls the default set, the duplicate set and the spam set, dedupes by lead_id, and keys each
caller by a per-run salted hash (never written, never printed). Writes a redacted file without
contact values and prints aggregates, masked tracking-number names and cluster labels only.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import secrets
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
SALT = secrets.token_bytes(16)
OUT = ROOT / "clients" / "mastergrass-lawn-care" / "snapshots" / "audit-2026-09-26"


def pull(**extra):
    out, page = [], 1
    while True:
        r = requests.get("https://app.whatconverts.com/api/v1/leads", auth=AUTH, timeout=60, params=dict(
            account_id=64716, profile_id=94840, start_date="2026-06-01", end_date="2026-09-26",
            leads_per_page=250, page_number=page, **extra))
        r.raise_for_status()
        b = r.json().get("leads", [])
        out += b
        if len(b) < 250:
            return out
        page += 1


sets = {"default": pull(), "duplicate": pull(duplicate="true"), "spam": pull(spam="true")}
by_id = {}
for name, ls in sets.items():
    for l in ls:
        assert str(l.get("account_id")) == "64716"
        by_id.setdefault(l["lead_id"], (name, l))
print("pulled:", {k: len(v) for k, v in sets.items()}, "unique:", len(by_id))


def hsh(v):
    d = "".join(ch for ch in str(v or "") if ch.isdigit())[-10:]
    return hashlib.sha256(SALT + d.encode()).hexdigest()[:8] if len(d) == 10 else None


def loc(l):
    return datetime.datetime.fromisoformat(l["date_created"].replace("Z", "+00:00")).astimezone(NY)


calls = [(s, l) for s, l in by_id.values() if l.get("lead_type") == "Phone Call"]
print(f"phone calls: {len(calls)}")

# ---- duration distribution + answer status ------------------------------------
bucket = Counter()
ans = Counter()
for s, l in calls:
    d = l.get("call_duration_seconds") or 0
    b = "0-19" if d < 20 else "20-39" if d < 40 else "40-44" if d < 45 else "45-49" if d < 50 else "50-89" if d < 90 else "90+"
    bucket[b] += 1
    ans[(l.get("answer_status"), l.get("call_status"))] += 1
print("duration buckets:", dict(sorted(bucket.items())))
print("answer_status x call_status:", ans.most_common(10))

# ---- per tracking number: set, source, gclid, duration --------------------------
print("\nper tracking-number name (phone_name) x set x source/medium:")
c = Counter((l.get("phone_name"), s, f"{l.get('lead_source')}/{l.get('lead_medium')}") for s, l in calls)
for k, v in sorted(c.items(), key=lambda x: (str(x[0][0]), -x[1])):
    print(f"  {v:>4} {k}")

# ---- caller clusters: same caller hitting several tracking numbers ---------------
by_caller = defaultdict(list)
for s, l in calls:
    k = hsh(l.get("caller_number") or l.get("contact_phone_number"))
    if k:
        by_caller[k].append((s, l))
multi = {k: v for k, v in by_caller.items() if len({x[1].get("phone_name") for x in v}) >= 3}
print(f"\ncallers seen: {len(by_caller)} | callers who rang 3+ different tracking numbers: {len(multi)}")
lab = {k: f"K{n:02d}" for n, k in enumerate(sorted(multi, key=lambda k: -len(multi[k])))}
for k in sorted(multi, key=lambda k: -len(multi[k]))[:6]:
    v = multi[k]
    nums = Counter(x[1].get("phone_name") for x in v)
    durs = Counter(x[1].get("call_duration_seconds") for x in v)
    days = sorted({loc(x[1]).strftime("%m-%d") for x in v})
    print(f"  {lab[k]} calls {len(v)} | numbers {dict(nums)} | top durations {durs.most_common(4)} | days {len(days)} ({days[0]}..{days[-1]})")

# ---- the paid numbers specifically ------------------------------------------------
PAID = {"GSA's Traffic", "GLE Traffic"}
print("\nevery call on the paid-search numbers (GSA's Traffic, GLE Traffic), with caller cluster:")
for s, l in sorted(calls, key=lambda x: x[1]["date_created"]):
    if l.get("phone_name") not in PAID:
        continue
    k = hsh(l.get("caller_number") or l.get("contact_phone_number"))
    print(f"  {loc(l):%m-%d %a %H:%M} {l.get('phone_name'):<14} set={s:<9} {l.get('lead_source')}/{l.get('lead_medium')} "
          f"dur={l.get('call_duration_seconds')} ans={l.get('answer_status')} status={l.get('lead_status')} "
          f"q={l.get('quotable')} caller={lab.get(k, 'single' if len(by_caller.get(k, [])) == 1 else 'repeat')}")

red = [{"set": s, **{f: l.get(f) for f in (
    "lead_id", "lead_type", "lead_status", "date_created", "quotable", "spam", "duplicate", "lead_source",
    "lead_medium", "gclid", "landing_url", "phone_name", "call_duration_seconds", "answer_status",
    "call_status", "caller_city", "caller_state")}} for s, l in by_id.values()]
(OUT / "wc_leads_jun_sep_all_sets.json").write_text(json.dumps(red, indent=0), encoding="utf-8")
print("\nwrote wc_leads_jun_sep_all_sets.json (redacted, no contact values)")
