#!/usr/bin/env python3
"""Aggregate the fresh Pro Green Austin search-term corpus for expert adjudication.

Groups the window's distinct normalized terms into preliminary buckets using the
verified first-party service whitelist plus the already-effective negative
inventory, so the residue that still needs human judgment is small and explicit.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

D = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
TARGETS = {"24053505504", "24053505501"}


def norm(t):
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def tokens(t):
    return norm(t).split()


def phrase_blocks(neg, term):
    """True when PHRASE negative `neg` blocks `term` (contiguous token subsequence)."""
    n, t = tokens(neg), tokens(term)
    if not n or len(n) > len(t):
        return False
    return any(t[i:i + len(n)] == n for i in range(len(t) - len(n) + 1))


# ---------------- effective negative inventory reaching the two campaigns ----------
acct_sets = {s["id"] for s in D["shared_sets"]
             if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"}
linked = {l["shared_set_id"] for l in D["campaign_shared_sets"]
          if l["campaign_id"] in TARGETS and l["link_status"] == "ENABLED"}
by_set = defaultdict(set)
for m in D["shared_criteria"]:
    by_set[m["shared_set_id"]].add((norm(m["keyword_text"]), m["match_type"]))

camp_neg = defaultdict(set)
for x in D["campaign_negative_keywords"]:
    if x["campaign_id"] in TARGETS:
        camp_neg[x["campaign_id"]].add((norm(x["text"]), x["match_type"]))

ag_neg = defaultdict(set)
ag_campaign = {a["id"]: a["campaign_id"] for a in D["ad_groups"]}
for k in D["ad_group_keywords"]:
    if k["negative"] and k["campaign_id"] in TARGETS:
        ag_neg[k["ad_group_id"]].add((norm(k["text"]), k["match_type"]))

campaign_wide = {}
for cid in TARGETS:
    s = set()
    for st in acct_sets | linked:
        s |= by_set[st]
    s |= camp_neg[cid]
    campaign_wide[cid] = s

print("== EFFECTIVE CAMPAIGN-WIDE NEGATIVE INVENTORY ==")
for cid in sorted(TARGETS):
    s = campaign_wide[cid]
    mt = defaultdict(int)
    for _, m in s:
        mt[m] += 1
    print(f"  {cid}: {len(s)} distinct (text,match) pairs  {dict(mt)}")

# ---------------- window rows ----------------
rows = [r for r in D["search_terms_window"] if r["campaign_id"] in TARGETS]
terms = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0,
                             "allconv": 0.0, "rows": 0, "raw": set(), "ags": set(),
                             "camps": set(), "kws": set()})
for r in rows:
    a = terms[norm(r["term"])]
    a["impr"] += r["impressions"]; a["clicks"] += r["clicks"]; a["cost"] += r["cost"]
    a["conv"] += r["conversions"]; a["allconv"] += r["all_conversions"]; a["rows"] += 1
    a["raw"].add(r["term"]); a["ags"].add(r["ad_group_name"])
    a["camps"].add(r["campaign_id"]); a["kws"].add(r["matched_keyword"])

print(f"\n== CORPUS ==\n  rows={len(rows)} distinct_normalized={len(terms)} "
      f"cost=${sum(v['cost'] for v in terms.values()):,.2f} "
      f"clicks={sum(v['clicks'] for v in terms.values())} "
      f"impr={sum(v['impr'] for v in terms.values())} "
      f"conv={sum(v['conv'] for v in terms.values()):.2f}")

# ---------------- verified first-party service whitelist ----------------
SERVICE = re.compile(
    r"\b(patios?|pavers?|paving|driveways?|walkways?|pathways?|retaining\s+walls?|"
    r"seat(ing)?\s+walls?|hardscap\w*|stonework|masonry|flagstone|outdoor\s+living|"
    r"outdoor\s+space|outdoor\s+kitchens?|backyard|fire\s*pits?|outdoor\s+fireplaces?|"
    r"pergolas?|arbors?|gazebos?|patio\s+covers?|shade\s+structures?|"
    r"landscap\w*|hardscape|yard|turf|artificial\s+grass|synthetic\s+grass|"
    r"lighting|lights?|deck\w*|concrete|outdoor\s+design|design\s*(and|&)?\s*build|"
    r"stepping\s+stones?|curb\w*|border\w*|garden\w*|xeriscap\w*|softscap\w*|"
    r"sod|grass|irrigation|sprinkler|drainage|grading|retaining|"
    r"contractors?|companies|company|builders?|installers?|installation|services?|"
    r"near\s+me|austin|cedar\s+park|georgetown|leander|round\s+rock|lakeway|"
    r"bee\s+cave|dripping\s+springs|pflugerville|west\s+lake|barton\s+creek)\b", re.I)

buckets = defaultdict(list)
for t, v in terms.items():
    blocked = [cid for cid in TARGETS
               if any(mt == "PHRASE" and phrase_blocks(txt, t)
                      for txt, mt in campaign_wide[cid])]
    if blocked:
        buckets["ALREADY_BLOCKED_CAMPAIGN_WIDE"].append((t, v, blocked))
    elif SERVICE.search(t):
        buckets["SERVICE_VOCAB"].append((t, v, []))
    else:
        buckets["RESIDUE_NO_SERVICE_VOCAB"].append((t, v, []))

print("\n== PRELIMINARY BUCKETS (distinct normalized terms) ==")
for b, items in buckets.items():
    print(f"  {b:<34} terms={len(items):4} rows={sum(v['rows'] for _, v, _ in items):4} "
          f"impr={sum(v['impr'] for _, v, _ in items):5} "
          f"clicks={sum(v['clicks'] for _, v, _ in items):3} "
          f"cost=${sum(v['cost'] for _, v, _ in items):8,.2f}")

if len(sys.argv) > 2 and sys.argv[2] == "--detail":
    for b in ("RESIDUE_NO_SERVICE_VOCAB", "ALREADY_BLOCKED_CAMPAIGN_WIDE", "SERVICE_VOCAB"):
        print(f"\n===== {b} =====")
        for t, v, blk in sorted(buckets[b], key=lambda x: (-x[1]["cost"], -x[1]["impr"])):
            extra = f"  blocked_in={len(blk)}" if blk else ""
            print(f"  ${v['cost']:7.2f} clk={v['clicks']:2} impr={v['impr']:4} "
                  f"conv={v['conv']:.1f} rows={v['rows']} | {t!r}{extra}")
