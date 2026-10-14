#!/usr/bin/env python3
"""Locate the 79 'suspect enabled positive Exact keywords' and prove their true serving state."""
from __future__ import annotations
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
import json

c = client()
st = json.load(open(EVID / "2026-09-09-structure.json", encoding="utf-8"))
kws = st["positive_keywords"]
ags = {a["id"]: a for a in st["ad_groups"]}

print("=== POSITIVE KEYWORDS INSIDE THE FIVE ENABLED CAMPAIGNS ===")
five_kw = [k for k in kws if k["campaign_id"] in FIVE]
print("total rows:", len(five_kw))
print("by (criterion status, ad_group status):",
      dict(Counter((k["status"], k["ad_group_status"]) for k in five_kw)))

# Group by ad group
byag = defaultdict(list)
for k in five_kw:
    byag[k["ad_group_id"]].append(k)

print("\n--- ad groups holding positives inside the five ---")
for agid, rows in sorted(byag.items(), key=lambda x: -len(x[1])):
    a = ags.get(agid, {})
    en = [r for r in rows if r["status"] == "ENABLED"]
    print(f"  AG {agid:>12} status={a.get('status'):<8} camp={a.get('campaign_id')} "
          f"({NAME.get(a.get('campaign_id'), '?')}) rows={len(rows)} criterion-ENABLED={len(en)} "
          f"name={a.get('name')}")

print("\n=== THE SUSPECT SET: criterion ENABLED but NOT servable ===")
suspect = [k for k in five_kw if k["status"] == "ENABLED"
           and not (k["ad_group_status"] == "ENABLED" and k["campaign_status"] == "ENABLED")]
print("count:", len(suspect))
print("by campaign:", dict(Counter(NAME[k["campaign_id"]] for k in suspect)))
print("by ad group:", dict(Counter(k["ad_group_id"] for k in suspect)))
print("by match:", dict(Counter(k["match"] for k in suspect)))
print("by system_serving_status:", dict(Counter(k["system_serving"] for k in suspect)))

print("\n=== TRULY LIVE positives (all three ENABLED) ===")
live = [k for k in five_kw if k["status"] == "ENABLED" and k["ad_group_status"] == "ENABLED"
        and k["campaign_status"] == "ENABLED"]
for k in sorted(live, key=lambda x: (NAME[x["campaign_id"]], x["match"])):
    print(f"  {NAME[k['campaign_id']]:<20} {k['match']:<7} {k['text']:<40} "
          f"crit={k['criterion_id']:<14} AG={k['ad_group_id']} QS={k['qs']} "
          f"ctr={k['qs_ctr']} rel={k['qs_creative']} lp={k['qs_lp']} eff_cpc=${k['eff_cpc']}")

# Full listing of suspects with text
print("\n=== SUSPECT LISTING (text) ===")
for k in sorted(suspect, key=lambda x: (NAME[x["campaign_id"]], x["text"])):
    print(f"  {NAME[k['campaign_id']]:<20} {k['match']:<7} AG={k['ad_group_id']} "
          f"agstatus={k['ad_group_status']:<8} crit={k['criterion_id']:<14} [{k['text']}]")

write(EVID / "2026-09-09-anomalous-positives.json",
      {"five_positive_rows": five_kw, "suspect": suspect, "truly_live": live})
