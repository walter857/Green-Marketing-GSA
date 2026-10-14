#!/usr/bin/env python3
"""Effective-negative coverage probe for the two in-scope Pro Green Austin campaigns."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

D = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

TARGETS = {
    "24053505504": "Progreen Austin | Search | Outdoor Living & Design",
    "24053505501": "Progreen Austin | Search | Hardscape Construction",
}
PHASE1 = ["agc turf", "ulm austin", "garden goat", "agave landscaping", "astoria lighting"]


def norm(t):
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ---- campaign negatives on the two in-scope campaigns
cn = defaultdict(list)
for x in D["campaign_negative_keywords"]:
    if x["campaign_id"] in TARGETS:
        cn[x["campaign_id"]].append(x)

print("== CAMPAIGN NEGATIVES ON IN-SCOPE CAMPAIGNS ==")
for cid, name in TARGETS.items():
    rows = sorted(cn[cid], key=lambda r: norm(r["text"]))
    print(f"\n-- {cid} {name}  ({len(rows)}) --")
    for r in rows:
        print(f"   {r['match_type']:<7} {r['status']:<8} {r['criterion_id']:>12}  {r['text']!r}")

a = {(norm(r["text"]), r["match_type"]) for r in cn["24053505504"]}
b = {(norm(r["text"]), r["match_type"]) for r in cn["24053505501"]}
print(f"\n  identical sets: {a == b}   only-in-OLD: {sorted(a - b)}   only-in-HC: {sorted(b - a)}")

# ---- shared-list coverage reaching both campaigns
live_link_sets = defaultdict(set)
for l in D["campaign_shared_sets"]:
    if l["campaign_id"] in TARGETS and l["link_status"] == "ENABLED":
        live_link_sets[l["campaign_id"]].add(l["shared_set_id"])
acct_sets = {s["id"] for s in D["shared_sets"]
             if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"}
by_set = defaultdict(set)
for m in D["shared_criteria"]:
    by_set[m["shared_set_id"]].add((norm(m["keyword_text"]), m["match_type"]))

print("\n== SHARED / ACCOUNT-LEVEL COVERAGE ==")
print(f"  account-level sets: {sorted(acct_sets)} -> "
      f"{sum(len(by_set[s]) for s in acct_sets)} distinct (text,match) pairs")
for cid in TARGETS:
    sets = live_link_sets[cid]
    members = set().union(*[by_set[s] for s in sets]) if sets else set()
    acct = set().union(*[by_set[s] for s in acct_sets]) if acct_sets else set()
    print(f"  {cid}: linked sets={sorted(sets)} members={len(members)}  "
          f"account-level={len(acct)}  union={len(members | acct)}")

# ---- ad-group negatives
agneg = defaultdict(set)
ag_name = {}
ag_campaign = {}
for a_ in D["ad_groups"]:
    ag_name[a_["id"]] = a_["name"]
    ag_campaign[a_["id"]] = a_["campaign_id"]
for k in D["ad_group_keywords"]:
    if k["negative"] and k["campaign_id"] in TARGETS:
        agneg[k["ad_group_id"]].add((norm(k["text"]), k["match_type"]))
print("\n== AD-GROUP NEGATIVES ==")
print(f"  ad groups with negatives: {len(agneg)}  total rows: "
      f"{sum(len(v) for v in agneg.values())}")
sets_seen = Counter(frozenset(v) for v in agneg.values())
print(f"  distinct ad-group negative sets: {len(sets_seen)}")
allag = set().union(*agneg.values()) if agneg else set()
print(f"  union of all ad-group negative texts: {len(allag)}")
for t, mt in sorted(allag):
    holders = [ag_name[g] for g, v in agneg.items() if (t, mt) in v]
    print(f"    {mt:<7} {t!r:<40} in {len(holders)} ad groups")


def effective(cid, text, mt="PHRASE"):
    """Where a (text, match) pair is already blocked for a whole campaign."""
    key = (norm(text), mt)
    hits = []
    acct = set().union(*[by_set[s] for s in acct_sets]) if acct_sets else set()
    if key in acct:
        hits.append("ACCOUNT_LEVEL_LIST")
    sets = live_link_sets[cid]
    for s in sets:
        if key in by_set[s]:
            nm = next((x["name"] for x in D["shared_sets"] if x["id"] == s), s)
            hits.append(f"SHARED_LIST:{nm}")
    if key in {(norm(r["text"]), r["match_type"]) for r in cn[cid]}:
        hits.append("CAMPAIGN")
    ags = [g for g in agneg if ag_campaign.get(g) == cid and key in agneg[g]]
    if ags:
        hits.append(f"AD_GROUP x{len(ags)}/{sum(1 for g in ag_campaign.values() if g == cid)}")
    return hits


print("\n== PHASE 1 NEGATIVE COVERAGE CHECK ==")
for t in PHASE1:
    for cid, name in TARGETS.items():
        print(f"  {t!r:<24} {cid} -> {effective(cid, t) or 'NOT FOUND'}")

print("\n== CHANGE EVENTS: CAMPAIGN_CRITERION ==")
for e in sorted(D["change_events"], key=lambda x: x["change_date_time"]):
    if e["resource_type"] != "CAMPAIGN_CRITERION":
        continue
    print(f"  {e['change_date_time']}  {e['operation']:<7} "
          f"camp={e['campaign'].rsplit('/', 1)[-1]:>12}  "
          f"kw={e['new_campaign_keyword_text']!r} "
          f"{e['new_campaign_keyword_match_type']}  {e['client_type']}")

print("\n== CHANGE EVENTS: NON-CRITERION SUMMARY ==")
for e in sorted(D["change_events"], key=lambda x: x["change_date_time"]):
    if e["resource_type"] == "CAMPAIGN_CRITERION":
        continue
    print(f"  {e['change_date_time']}  {e['resource_type']:<14} {e['operation']:<7} "
          f"camp={e['campaign'].rsplit('/', 1)[-1]:>12} fields={','.join(e['changed_fields'])[:70]}")
