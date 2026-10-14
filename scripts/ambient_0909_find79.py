#!/usr/bin/env python3
"""Find where the prompt's '79 suspect enabled positive Exact keywords' actually live."""
from __future__ import annotations
import sys, json, re
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa

st = json.load(open(EVID / "2026-09-09-structure.json", encoding="utf-8"))
kws = st["positive_keywords"]

NAMED = [
    "apex heating and cooling frostburg md",
    "ars heating and cooling reviews",
    "ars hvac",
    "arundel cooling and heating reviews",
    "arundel heating and cooling maryland",
    "michael and son hvac",
    "hvac capacitor replacement near me",
    "midea hvac distributor near me",
]
print("=== EXACT-TEXT LOOKUP OF THE NAMED EXAMPLES, ACCOUNT-WIDE ===")
idx = defaultdict(list)
for k in kws:
    idx[k["text"].strip().lower()].append(k)
for t in NAMED:
    rows = idx.get(t, [])
    if not rows:
        print(f"  NOT FOUND anywhere in ad_group_criterion: [{t}]")
    for k in rows:
        print(f"  FOUND [{t}] -> crit={k['criterion_id']} match={k['match']} "
              f"critstatus={k['status']} AG={k['ad_group_id']}({k['ad_group_status']}) "
              f"camp={k['campaign_id']} {k['campaign_name'][:40]!r}({k['campaign_status']})")

print("\n=== ACCOUNT-WIDE positives whose criterion is ENABLED ===")
en = [k for k in kws if k["status"] == "ENABLED"]
print("criterion-ENABLED total:", len(en))
print("  by campaign status:", dict(Counter(k["campaign_status"] for k in en)))
print("  by ad group status:", dict(Counter(k["ad_group_status"] for k in en)))
servable = [k for k in en if k["ad_group_status"] == "ENABLED" and k["campaign_status"] == "ENABLED"]
print("  SERVABLE (3x ENABLED) account-wide:", len(servable))

print("\n=== ENABLED criteria in campaigns named like Installation / Replacement ===")
for k in en:
    if re.search(r"install|replac", k["campaign_name"], re.I):
        print(f"  camp={k['campaign_id']}({k['campaign_status']}) {k['campaign_name'][:45]:<45} "
              f"AG={k['ad_group_id']}({k['ad_group_status']}) {k['match']:<7} [{k['text']}]")

print("\n=== ALL 11 rows in HVAC Installation ad group 202339087634 ===")
for k in kws:
    if k["ad_group_id"] == "202339087634":
        print(f"  crit={k['criterion_id']:<14} {k['match']:<7} status={k['status']:<8} [{k['text']}]")

print("\n=== Company-name-looking positives anywhere with criterion ENABLED ===")
COMPANY = re.compile(r"\b(reviews|llc|inc|and son|& son|heating and cooling|hvac)\b", re.I)
cands = [k for k in en if re.search(r"\b(reviews|llc|inc|and son|& son)\b", k["text"], re.I)]
print("count:", len(cands))
for k in cands[:60]:
    print(f"  camp={k['campaign_id']}({k['campaign_status']}) AG={k['ad_group_id']}({k['ad_group_status']}) [{k['text']}]")
