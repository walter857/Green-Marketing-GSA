#!/usr/bin/env python3
"""2026-09-16 READ-ONLY Keyword Planner evidence for Apogee Lawns permanent lighting.

KeywordPlanIdeaService caps geo_target_constants at 10 and has its own quota that 429s
fast. Synonyms share one volume bucket -- never sum rows to estimate total demand.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, client, write, E  # noqa: E402

c = client()
svc = c.get_service("KeywordPlanIdeaService")

picked = json.loads((EVID / "2026-09-16-geo-picked.json").read_text(encoding="utf-8"))
ALL_GEOS = [(t, v["id"], v["canonical"], v["reach"]) for t, v in picked.items()]
ALL_GEOS.sort(key=lambda x: -x[3])

GEO_SETS = {
    "lincoln_city_only": [("Lincoln, Nebraska", "1021696", "Lincoln,Nebraska,United States", 728000)],
    "top10_of_approved_area": ALL_GEOS[:10],
}
print("=== GEO SETS USED ===")
for label, gs in GEO_SETS.items():
    print(f"  {label}: {len(gs)} targets")
    for t, gid, canon, reach in gs:
        print(f"      {gid:>9} reach={reach:>7}  {canon}")
print(f"  (full approved area is {len(ALL_GEOS)} targets; planner cap is 10, so "
      f"'{'top10_of_approved_area'}' omits: "
      f"{[x[2] for x in ALL_GEOS[10:]]})")

BATCHES = {
    "ag1_core_permanent_christmas": [
        "permanent christmas light installation",
        "permanent christmas lights installer",
        "permanent christmas light installer",
        "permanent christmas lights installation",
        "permanent christmas lights",
        "permanent christmas lights near me",
        "permanent christmas lights lincoln ne",
        "permanent christmas lights cost",
        "permanent christmas light company",
        "permanent christmas lights installers near me",
    ],
    "ag2_permanent_holiday_and_phase2": [
        "permanent holiday light installation",
        "permanent holiday lights",
        "permanent holiday lights near me",
        "permanent holiday lighting",
        "permanent outdoor lighting installation",
        "year round outdoor lighting installer",
        "permanent roofline lighting installation",
        "permanent soffit lighting installation",
        "permanent exterior lighting",
        "permanent led lights for house",
    ],
    "ag3_brand_and_generic_test": [
        "everlights",
        "everlights installer",
        "everlights installation",
        "christmas light installation",
        "christmas light installers near me",
        "christmas light installation lincoln ne",
        "holiday light installation",
        "holiday lighting installers near me",
        "trimlight",
        "jellyfish lighting",
    ],
}

out = {
    "geo_sets": {k: [{"id": g[1], "canonical": g[2], "reach": g[3]} for g in v]
                 for k, v in GEO_SETS.items()},
    "geo_cap_note": "KeywordPlanIdeaService caps geo_target_constants at 10",
    "bucket_warning": ("Keyword Planner collapses synonyms into one shared volume bucket. "
                       "Rows are per-bucket ceilings, not additive demand."),
    "results": {},
}

for geo_label, geos in GEO_SETS.items():
    out["results"][geo_label] = {}
    for kw_label, seeds in BATCHES.items():
        try:
            req = c.get_type("GenerateKeywordHistoricalMetricsRequest")
            req.customer_id = CID
            req.keywords.extend(seeds)
            req.language = "languageConstants/1000"
            req.geo_target_constants.extend([f"geoTargetConstants/{g[1]}" for g in geos])
            req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
            resp = svc.generate_keyword_historical_metrics(request=req)
            rows = []
            for r in resp.results:
                m = r.keyword_metrics
                rows.append({
                    "text": r.text,
                    "avg_monthly_searches": m.avg_monthly_searches,
                    "competition": E(m.competition),
                    "competition_index": m.competition_index,
                    "low_top_bid_usd": round(m.low_top_of_page_bid_micros / 1e6, 2)
                    if m.low_top_of_page_bid_micros else None,
                    "high_top_bid_usd": round(m.high_top_of_page_bid_micros / 1e6, 2)
                    if m.high_top_of_page_bid_micros else None,
                    "close_variants": list(r.close_variants)[:8],
                    "monthly": [{"y": v.year, "m": E(v.month), "n": v.monthly_searches}
                                for v in m.monthly_search_volumes][-14:],
                })
            out["results"][geo_label][kw_label] = rows
            print(f"\n=== [{geo_label}] {kw_label} ({len(rows)} rows) ===")
            print(f"  {'searches':>9} {'comp':>12} {'idx':>4} {'TOPlow':>8} {'TOPhigh':>8}  keyword")
            for x in sorted(rows, key=lambda y: -(y["avg_monthly_searches"] or 0)):
                print(f"  {x['avg_monthly_searches'] or 0:>9} {x['competition']:>12} "
                      f"{x['competition_index']:>4} {str(x['low_top_bid_usd']):>8} "
                      f"{str(x['high_top_bid_usd']):>8}  {x['text']}")
                if x["close_variants"]:
                    print(f"      variants sharing this bucket: {x['close_variants']}")
        except Exception as ex:  # noqa: BLE001
            out["results"][geo_label][kw_label] = {"error": str(ex)[:500]}
            print(f"\n=== [{geo_label}] {kw_label} FAILED: {str(ex)[:300]}")
        time.sleep(5)

write(EVID / "2026-09-16-keyword-planner.json", out)
