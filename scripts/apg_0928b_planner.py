#!/usr/bin/env python3
"""2026-09-28 (run B) READ-ONLY Keyword Planner research for Apogee Lawns.

1. GenerateKeywordHistoricalMetrics for a fixed candidate list, approved area (10 largest of the
   14 targets - the service caps geo at 10), GOOGLE_SEARCH, English, with dated monthly history
   and Google's own close-variant grouping (dedupe key).
2. The same list for Lincoln city alone, and - CONDITIONAL RESEARCH ONLY - Omaha city, which the
   work order records as EXCLUDED (settled 2026-09-16). Omaha numbers authorize nothing.
3. GenerateKeywordIdeas seeded with installer language, stored to disk for the negative review.
Planner ideas are Google keyword suggestions, not this account's search terms.
"""
from __future__ import annotations

import datetime
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, E, client, write  # noqa: E402

c = client()
svc = c.get_service("KeywordPlanIdeaService")
LANG = "languageConstants/1000"
GEO_SETS = {
    "approved_area_top10": ["1021696", "9024746", "1021635", "9024753", "9024703",
                            "9024754", "9024671", "9024748", "1021783", "9195288"],
    "lincoln_city": ["1021696"],
    "omaha_city_CONDITIONAL_ONLY": ["1021721"],
}
OMITTED = ["1021647 Eagle", "9024728 68461", "9024651 68347", "9233865 Nemaha Precinct"]
CANDIDATES = [
    # existing coverage
    "permanent christmas lights", "permanent christmas light installation", "permanent christmas lights installer",
    # installer-language research seeds (permanent holiday = same approved service, verify intent)
    "permanent holiday light installation", "permanent holiday lights installer", "permanent holiday lighting installation",
    "permanent holiday lights installation", "permanent holiday lights", "permanent holiday lighting",
    # local / buyer modifiers on the head term
    "permanent christmas lights near me", "permanent christmas lights lincoln", "permanent christmas lights lincoln ne",
    "permanent christmas lights cost", "permanent christmas lights price", "permanent christmas light company",
    "permanent christmas lights installers near me", "permanent christmas light installation near me",
    "permanent christmas light installation cost", "permanent christmas lights installed",
    # ambiguous product / research families, evaluated separately
    "permanent outdoor lights", "permanent outdoor lighting", "permanent outdoor lighting installation",
    "permanent house lights", "permanent led christmas lights", "permanent roofline lighting",
    "year round christmas lights", "permanent christmas lights for house",
    # brand the client verifiably installs (first-party site: EverLights certified dealer)
    "everlights", "everlights permanent lighting",
]
out = {"run_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
       "network": "GOOGLE_SEARCH", "language": LANG, "geo_sets": GEO_SETS, "omitted_from_approved_area": OMITTED,
       "historical": {}, "notes": [
           "avg_monthly_searches and monthly values are Google Keyword Planner buckets, rounded; they are not exact counts",
           "close_variants lists the queries Google merged into the same row; rows sharing a bucket must not be summed",
       ]}


def hist(geos):
    req = c.get_type("GenerateKeywordHistoricalMetricsRequest")
    req.customer_id = CID
    req.keywords.extend(CANDIDATES)
    req.language = LANG
    req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in geos])
    req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    resp = svc.generate_keyword_historical_metrics(request=req)
    rows = []
    for r in resp.results:
        m = r.keyword_metrics
        rows.append({"text": r.text, "close_variants": list(r.close_variants),
                     "avg": m.avg_monthly_searches if m._pb.HasField("avg_monthly_searches") else None,
                     "competition": E(m.competition), "comp_index": m.competition_index,
                     "top_low": round(m.low_top_of_page_bid_micros / 1e6, 2) if m.low_top_of_page_bid_micros else None,
                     "top_high": round(m.high_top_of_page_bid_micros / 1e6, 2) if m.high_top_of_page_bid_micros else None,
                     "monthly": {f"{x.year}-{E(x.month)[:3]}": x.monthly_searches for x in m.monthly_search_volumes}})
    return rows


for label, geos in GEO_SETS.items():
    try:
        out["historical"][label] = hist(geos)
    except Exception as exc:  # noqa: BLE001
        out["historical"][label] = {"error": str(exc)[:300]}
    time.sleep(3)

print("=== HISTORICAL METRICS (Planner buckets; do not sum rows) ===")
for label, rows in out["historical"].items():
    print(f"\n--- {label} ---")
    if isinstance(rows, dict):
        print("  ERROR", rows["error"][:200])
        continue
    returned = {r["text"] for r in rows}
    missing = [k for k in CANDIDATES if k not in returned]
    for r in rows:
        mo = r["monthly"]
        season = [mo.get(k) for k in ("2025-SEP", "2025-OCT", "2025-NOV", "2025-DEC")]
        print(f"  {r['text']:<46} avg={str(r['avg']):>4} S/O/N/D25={season} comp={r['competition']:<8} "
              f"top=${r['top_low']}-{r['top_high']} cv={len(r['close_variants'])}")
    if missing:
        print(f"  not returned as own row (merged into a close-variant row or no data): {missing}")

print("\n=== KEYWORD IDEAS (installer-language seeds, approved area) -> disk only ===")
req = c.get_type("GenerateKeywordIdeasRequest")
req.customer_id = CID
req.language = LANG
req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in GEO_SETS["approved_area_top10"]])
req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
req.keyword_seed.keywords.extend(["permanent christmas light installation", "permanent holiday light installation",
                                  "permanent christmas lights installer", "permanent christmas lights",
                                  "permanent holiday lights", "permanent outdoor lighting installation"])
ideas = []
try:
    for r in svc.generate_keyword_ideas(request=req):
        m = r.keyword_idea_metrics
        ideas.append({"text": r.text, "avg": m.avg_monthly_searches or 0, "competition": E(m.competition),
                      "close_variants": list(r.close_variants)})
except Exception as exc:  # noqa: BLE001
    print("  ideas FAILED:", str(exc)[:200])
out["ideas_count"] = len(ideas)
print(f"  ideas returned: {len(ideas)}")
write(EVID / "2026-09-28b-planner.json", out)
write(EVID / "2026-09-28b-planner-ideas.json", ideas)
