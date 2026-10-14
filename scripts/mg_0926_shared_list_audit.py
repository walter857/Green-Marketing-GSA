#!/usr/bin/env python3
"""2026-09-26 LOCAL: would the account's existing shared negative lists be safe on the live campaigns?

For each ENABLED NEGATIVE_KEYWORDS shared set: count members that would block a live positive
keyword, a converting live-campaign term, or a KEEP/WATCH term; and the historical live-campaign
cost it would have blocked. Prints counts; prints conflicting NEGATIVE KEYWORDS (advertiser
content) but never search terms.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "mastergrass-lawn-care" / "snapshots" / "audit-2026-09-26"
ST = ROOT / "reports" / "mastergrass-lawn-care" / "st"
LIVE = {"23905193676", "23914692658"}
TOK = re.compile(r"[a-z0-9']+")


def toks(s):
    return TOK.findall(s.lower())


def blocks(neg, mt, q):
    if mt == "EXACT":
        return neg == q
    if mt == "PHRASE":
        n = len(neg)
        return any(q[i:i + n] == neg for i in range(len(q) - n + 1)) if n and n <= len(q) else False
    return bool(neg) and set(neg) <= set(q)


sets = {r["shared_set"]["id"]: r["shared_set"] for r in json.loads((SNAP / "shared_sets.json").read_text())}
members = defaultdict(list)
for r in json.loads((SNAP / "shared_criteria.json").read_text(encoding="utf-8")):
    k = r.get("shared_criterion", {}).get("keyword")
    if k:
        members[r["shared_set"]["id"]].append((k["text"].lower(), k["match_type"]))

kw = json.loads((SNAP / "keywords.json").read_text(encoding="utf-8"))
live_pos = sorted({r["ad_group_criterion"]["keyword"]["text"].lower() for r in kw
                   if r["campaign"]["id"] in LIVE and not r["ad_group_criterion"].get("negative")
                   and r["ad_group_criterion"].get("status") == "ENABLED"})
terms = []
with (ST / "verdicts.csv").open(encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        terms.append((toks(row["term"]), row["verdict"], float(row["cost_all"]), float(row["conv_all"])))
pos_t = [(p, toks(p)) for p in live_pos]

for sid, s in sorted(sets.items(), key=lambda kv: kv[1]["name"]):
    if s.get("type_") != "NEGATIVE_KEYWORDS" or s.get("status") != "ENABLED":
        continue
    mem = members.get(sid, [])
    kw_conf, keep_conf, conv_conf = set(), 0, 0
    neg_cost = keep_cost = 0.0
    for text, mt in mem:
        nt = toks(text)
        for p, pt in pos_t:
            if blocks(nt, mt, pt):
                kw_conf.add((text, mt, p))
    blocked_keep = blocked_neg = 0
    for qt, v, cost, conv in terms:
        hit = any(blocks(toks(t), mt, qt) for t, mt in mem)
        if not hit:
            continue
        if conv > 0:
            conv_conf += 1
        if v in ("KEEP", "WATCH"):
            blocked_keep += 1; keep_cost += cost
        else:
            blocked_neg += 1; neg_cost += cost
    print(f"\n{s['name']} ({sid}) members {len(mem)} refs {s.get('reference_count')}")
    print(f"  blocks live positive keywords: {len(kw_conf)} | blocks converting terms: {conv_conf}")
    print(f"  would have blocked NEGATIVE-verdict terms: {blocked_neg} (${neg_cost:,.2f}) | "
          f"KEEP/WATCH terms: {blocked_keep} (${keep_cost:,.2f})")
    for text, mt, p in sorted(kw_conf)[:12]:
        print(f"    conflict: negative {mt} '{text}' blocks live keyword '{p}'")
