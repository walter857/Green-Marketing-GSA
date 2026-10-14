#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: Keyword Planner forecast of future search terms for Master Grass.

Pulls keyword ideas (Iowa, English) for the drainage, landscaping and hardscaping seed sets,
keeps ideas that could actually reach a live PHRASE/EXACT keyword or the PMax drainage themes,
and prints ONLY aggregated single-word vocabulary (count of ideas + summed monthly searches)
that falls outside the service/intent/place whitelist. Ideas stay on disk.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import CID, SNAP, client, q  # noqa: E402

OUT = SNAP / "audit-2026-09-26"
c = client()
iowa = [r.geo_target_constant.resource_name for r in q(c, """
    SELECT geo_target_constant.resource_name, geo_target_constant.canonical_name
    FROM geo_target_constant WHERE geo_target_constant.canonical_name = 'Iowa,United States'
    AND geo_target_constant.target_type = 'State'""")]
assert len(iowa) == 1, iowa
SEEDS = {
    "drainage": ["french drain", "french drain installation", "yard drainage", "yard drainage solutions",
                 "drainage contractor", "standing water in yard", "yard grading", "yard leveling",
                 "lawn grading", "land grading", "french drain contractor", "backyard drainage"],
    "landscaping": ["landscaping", "landscaping company", "landscaping contractor", "landscaping services",
                    "landscape installation", "landscapers", "mulch installation", "landscape rock",
                    "river rock landscaping", "landscaping borders"],
    "hardscaping": ["hardscaping", "hardscape contractor", "paver patio", "paver installation",
                    "patio installation", "patio builders", "retaining wall", "retaining wall contractor",
                    "fire pit installation", "outdoor kitchen", "outdoor kitchen contractor"],
}
svc = c.get_service("KeywordPlanIdeaService")
ideas = {}
for grp, seeds in SEEDS.items():
    req = c.get_type("GenerateKeywordIdeasRequest")
    req.customer_id = CID
    req.language = "languageConstants/1000"
    req.geo_target_constants.extend(iowa)
    req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    req.keyword_seed.keywords.extend(seeds)
    req.page_size = 10000
    try:
        n = 0
        for r in svc.generate_keyword_ideas(request=req):
            ideas.setdefault(r.text.lower(), {"groups": set(), "avg": 0})
            ideas[r.text.lower()]["groups"].add(grp)
            ideas[r.text.lower()]["avg"] = max(ideas[r.text.lower()]["avg"], r.keyword_idea_metrics.avg_monthly_searches or 0)
            n += 1
        print(f"{grp}: {n} ideas")
    except Exception as ex:  # noqa: BLE001
        print(f"{grp}: ERROR {str(ex)[:300]}")
(OUT / "kp_ideas_iowa.json").write_text(json.dumps({k: {"groups": sorted(v["groups"]), "avg": v["avg"]}
                                                      for k, v in ideas.items()}), encoding="utf-8")
print(f"unique ideas: {len(ideas)} (on disk only)")

TOK = re.compile(r"[a-z0-9']+")
kw = json.loads((OUT / "keywords.json").read_text(encoding="utf-8"))
live = [(TOK.findall(r["ad_group_criterion"]["keyword"]["text"].lower()), r["ad_group_criterion"]["keyword"]["match_type"])
        for r in kw if r["campaign"]["id"] in ("23905193676", "23914692658")
        and not r["ad_group_criterion"].get("negative") and r["ad_group_criterion"].get("status") == "ENABLED"]
DRAIN = re.compile(r"\b(drain\w*|grading|grade|regrad\w*|level\w*|standing water|soggy|wet yard|pooling|puddl\w*|runoff|swale)\b")


def stem(t):
    return t[:-1] if t.endswith("s") and len(t) > 3 else t


def reachable(tokens):
    st = [stem(t) for t in tokens]
    for kt, mt in live:
        k = [stem(t) for t in kt]
        n = len(k)
        if mt == "PHRASE" and any(st[i:i + n] == k for i in range(len(st) - n + 1)):
            return True
        if mt == "EXACT" and st == k:
            return True
    return False


WHITE = set("""a an the in on of for to and or my me is it at by with near you i do does can your our
landscaping landscape landscaper landscapers landscapes hardscaping hardscape hardscapes paver pavers patio patios
retaining wall walls fire pit pits firepit outdoor kitchen kitchens french drain drains drainage grading grade
yard yards lawn leveling level mulch rock rocks river border borders edging bed beds installation install installer
installers installing installed contractor contractors company companies service services builder builders build
construction local best near me quote quotes estimate estimates cost costs price prices pricing hire professional pros
pro residential design designer designs solutions solution system systems contractor's backyard front back home
house around custom new ideas""".split())
voc = Counter()
vol = Counter()
nreach = Counter()
for text, m in ideas.items():
    toks = TOK.findall(text)
    r_search = reachable(toks)
    r_pmax = bool(DRAIN.search(text))
    if not (r_search or r_pmax):
        continue
    nreach["search" if r_search else "pmax_only"] += 1
    for t in set(toks):
        if t not in WHITE and not t.isdigit():
            voc[t] += 1
            vol[t] += m["avg"]
print(f"reachable ideas: {dict(nreach)}")
print("\nnon-whitelist words inside reachable ideas (word: ideas / summed avg monthly searches):")
rows = sorted(voc, key=lambda t: (-vol[t], -voc[t]))
print("  " + " | ".join(f"{t}:{voc[t]}/{vol[t]}" for t in rows[:260]))
