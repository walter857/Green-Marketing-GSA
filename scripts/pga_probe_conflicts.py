#!/usr/bin/env python3
"""Positive keywords, converting queries and Phase-1 leakage timing."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

D = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
TARGETS = {"24053505504": "Outdoor Living & Design", "24053505501": "Hardscape Construction"}
PHASE1_EFFECTIVE = "2026-08-19 08:50:50"
PHASE1 = ["agc turf", "ulm austin", "garden goat", "agave landscaping", "astoria lighting",
          "mcdugald steele", "mirror lake landscaping", "spring texas"]


def norm(t):
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


print("== LIVE POSITIVE KEYWORDS (in-scope, ENABLED) ==")
pos = [k for k in D["ad_group_keywords"]
       if not k["negative"] and k["campaign_id"] in TARGETS and k["status"] == "ENABLED"]
by_ag = defaultdict(list)
for k in pos:
    by_ag[(k["campaign_id"], k["ad_group_name"])].append(k)
for (cid, ag), ks in sorted(by_ag.items(), key=lambda x: (x[0][0], x[0][1])):
    txt = " | ".join(f"[{k['match_type'][:1]}] {k['text']}" for k in sorted(ks, key=lambda z: z["match_type"]))
    print(f"  {TARGETS[cid]:<24} {ag:<28} {txt}")
print(f"  total enabled positive keywords: {len(pos)}")
print(f"  distinct normalized positive texts: {len({norm(k['text']) for k in pos})}")

print("\n== ALL-TIME QUERIES WITH conversions > 0 ==")
conv = defaultdict(lambda: {"conv": 0.0, "cost": 0.0, "clicks": 0, "camps": set()})
for r in D["search_terms_all_time_converting"]:
    a = conv[norm(r["term"])]
    a["conv"] += r["conversions"]; a["cost"] += r["cost"]; a["clicks"] += r["clicks"]
    a["camps"].add(r["campaign_name"])
for t, v in sorted(conv.items(), key=lambda x: -x[1]["conv"]):
    print(f"  conv={v['conv']:5.2f} clk={v['clicks']:3} cost=${v['cost']:8.2f}  {t!r}")
print(f"  distinct converting queries: {len(conv)}")

print("\n== ALL-TIME QUERIES WITH all_conversions > 0 (secondary evidence) ==")
allc = defaultdict(lambda: {"c": 0.0, "cost": 0.0})
for r in D["search_terms_all_time_all_conv"]:
    a = allc[norm(r["term"])]
    a["c"] += r["all_conversions"]; a["cost"] += r["cost"]
print(f"  distinct: {len(allc)}")
for t, v in sorted(allc.items(), key=lambda x: -x[1]["c"])[:40]:
    print(f"    allconv={v['c']:6.2f} cost=${v['cost']:8.2f}  {t!r}")

print(f"\n== PHASE-1 LEAKAGE TIMING (effective {PHASE1_EFFECTIVE} account time) ==")
bd = defaultdict(lambda: defaultdict(lambda: [0, 0, 0.0]))
for r in D["search_terms_window_by_date"]:
    if r["campaign_id"] not in TARGETS:
        continue
    n = norm(r["term"])
    for p in PHASE1:
        if p in n:
            v = bd[p][r["date"]]
            v[0] += r["impressions"]; v[1] += r["clicks"]; v[2] += r["cost"]
for p in PHASE1:
    days = bd.get(p)
    if not days:
        print(f"  {p!r:<26} no matching query in window")
        continue
    pre = [d for d in days if d <= "2026-08-19"]
    post = [d for d in days if d > "2026-08-19"]
    print(f"  {p!r:<26} dates={sorted(days)}")
    print(f"      on/before 2026-08-19: impr={sum(days[d][0] for d in pre)} "
          f"clicks={sum(days[d][1] for d in pre)} cost=${sum(days[d][2] for d in pre):.2f}")
    print(f"      after     2026-08-19: impr={sum(days[d][0] for d in post)} "
          f"clicks={sum(days[d][1] for d in post)} cost=${sum(days[d][2] for d in post):.2f}")

print("\n== 2026-08-19 DETAIL FOR PHASE-1 TERMS (execution day) ==")
for p in PHASE1:
    v = bd.get(p, {}).get("2026-08-19")
    if v:
        print(f"  {p!r:<26} impr={v[0]} clicks={v[1]} cost=${v[2]:.2f}")
