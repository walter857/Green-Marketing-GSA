#!/usr/bin/env python3
"""Keyword Planner against the exact live service area (75 MD targets, sampled 10 per call)."""
from __future__ import annotations
import sys, json, time
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
geo = json.load(open(EVID / "2026-09-09-geo-targets.json", encoding="utf-8"))
names = geo["geo_names"]
targets = sorted({g["geo_id"] for g in geo["campaign_geo_criteria"]
                  if g["type"] == "LOCATION" and not g["negative"]})
print("live geo targets on the five:", len(targets))

# Keyword Planner caps geo_target_constants at 10. Use the largest / most representative
# Anne Arundel + Howard + Baltimore-area places that are actually in the live target set.
PREFERRED = ["Columbia", "Severn", "Severna Park", "Annapolis", "Glen Burnie", "Ellicott City",
             "Laurel", "Catonsville", "Bowie", "Odenton", "Pasadena", "Elkridge", "Crofton",
             "Arnold", "Jessup"]
chosen, chosen_names = [], []
for want in PREFERRED:
    for gid in targets:
        can = names.get(gid, {}).get("canonical", "")
        if can.startswith(want + ",Maryland"):
            if gid not in chosen and len(chosen) < 10:
                chosen.append(gid)
                chosen_names.append(can)
            break
print("planner geo sample (10 of 75):")
for a, b in zip(chosen, chosen_names):
    print(f"   {a}  {b}")

LANG = "languageConstants/1000"        # English
NETWORK = "GOOGLE_SEARCH"              # Google Search only, NOT search partners

SEEDS = {
    "AC repair": ["ac repair near me", "air conditioner repair near me", "ac repair",
                  "air conditioning repair near me", "ac repair company near me",
                  "emergency air conditioning repair near me", "repair my ac",
                  "ac repair service near me", "air conditioning service near me",
                  "hvac companies near me open now"],
    "HVAC/heating repair": ["hvac repair near me", "heating repair near me", "hvac company near me",
                            "hvac near me", "furnace repair near me", "heat and air repair",
                            "heating and cooling repair near me", "hvac contractor near me",
                            "hvac technician near me", "hvac service near me"],
    "New HVAC installation": ["hvac installation near me", "hvac installers near me",
                              "new hvac system cost", "hvac installation cost",
                              "heating and cooling installation near me",
                              "hvac ductwork installation near me", "hvac company near me",
                              "central air installation near me", "new ac installation near me",
                              "mini split installation near me"],
    "HVAC/AC/furnace replacement": ["hvac replacement near me", "ac replacement near me",
                                    "furnace replacement near me", "air conditioner replacement",
                                    "hvac system replacement cost", "replace hvac system",
                                    "heat pump replacement near me", "ac unit replacement cost",
                                    "new furnace cost", "hvac replacement cost"],
    "Gas boiler repair": ["gas boiler repair", "boiler repair near me", "gas boiler repair near me",
                          "boiler service near me", "boiler repair company",
                          "residential boiler repair", "gas boiler service",
                          "boiler technician near me", "steam boiler repair near me",
                          "hot water boiler repair"],
}

svc = c.get_service("KeywordPlanIdeaService")
results = {}
for label, seeds in SEEDS.items():
    print(f"\n=== PLANNER: {label} ({len(seeds)} seeds) ===")
    req = c.get_type("GenerateKeywordIdeasRequest")
    req.customer_id = CID
    req.language = LANG
    req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in chosen])
    req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    req.include_adult_keywords = False
    req.keyword_seed.keywords.extend(seeds)
    try:
        resp = svc.generate_keyword_ideas(request=req)
    except Exception as e:
        print("  FAILED:", type(e).__name__, str(e)[:300])
        results[label] = {"error": str(e)[:300]}
        continue
    rows = []
    for idea in resp:
        mi = idea.keyword_idea_metrics
        rows.append({
            "keyword": idea.text,
            "avg_monthly_searches": mi.avg_monthly_searches,
            "competition": E(mi.competition),
            "competition_index": mi.competition_index,
            "low_top_of_page_bid": round(mi.low_top_of_page_bid_micros / 1e6, 2),
            "high_top_of_page_bid": round(mi.high_top_of_page_bid_micros / 1e6, 2),
        })
    rows.sort(key=lambda r: -(r["avg_monthly_searches"] or 0))
    results[label] = {"seeds": seeds, "rows": rows, "n": len(rows)}
    print(f"  ideas returned: {len(rows)}")
    print(f"  {'kw':<44}{'searches':>9}{'comp':>8}{'idx':>5}{'TOPlow':>9}{'TOPhigh':>9}")
    for r in rows[:22]:
        print(f"  {r['keyword'][:44]:<44}{r['avg_monthly_searches']:>9}"
              f"{r['competition'][:6]:>8}{r['competition_index']:>5}"
              f"{r['low_top_of_page_bid']:>9}{r['high_top_of_page_bid']:>9}")
    seedrows = [r for r in rows if r["keyword"] in seeds]
    if seedrows:
        lows = [r["low_top_of_page_bid"] for r in seedrows if r["low_top_of_page_bid"]]
        highs = [r["high_top_of_page_bid"] for r in seedrows if r["high_top_of_page_bid"]]
        print(f"  SEED-ONLY top-of-page bid range: low ${min(lows) if lows else 0}-"
              f"${max(lows) if lows else 0}  high ${min(highs) if highs else 0}-"
              f"${max(highs) if highs else 0}")
        print(f"  SEED-ONLY total avg monthly searches: "
              f"{sum(r['avg_monthly_searches'] or 0 for r in seedrows)} "
              f"(NOTE: synonyms share one volume bucket - do not sum naively)")
    time.sleep(2)

write(EVID / "2026-09-09-keyword-planner.json", {
    "generated_local": __import__("datetime").datetime.now(TZ).isoformat(),
    "network": "GOOGLE_SEARCH (search partners excluded)",
    "language": "English (languageConstants/1000)",
    "geo_targets_used": [{"id": a, "canonical": b} for a, b in zip(chosen, chosen_names)],
    "geo_targets_live_total": len(targets),
    "geo_cap_note": "KeywordPlanIdeaService caps geo_target_constants at 10; 10 of the 75 live "
                    "targets were sampled, chosen as the largest population centres in the "
                    "live footprint. Figures therefore understate the full 75-place footprint.",
    "results": results,
})
