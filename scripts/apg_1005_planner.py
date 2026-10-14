#!/usr/bin/env python3
"""2026-10-05 READ-ONLY Keyword Planner research for Apogee Lawns (8164626278).

Seasonality (up to 48 months of monthly history) and in-season bid ranges for the current
keywords and for candidates taken from the 2026-09-21..10-05 search-term report.
Geo sets: the approved area (10 largest of 14 targets - the service caps geo at 10), Lincoln
city alone, and - SHAPE ONLY, never volume for this account - Nebraska state and the US.
Planner rows are rounded buckets; close variants share a bucket; rows are never summed.
Omaha is EXCLUDED by a settled decision and is not queried.
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
    "nebraska_state_SHAPE_ONLY": ["21162"],
    "united_states_SHAPE_ONLY": ["2840"],
}
CANDIDATES = [
    # live keywords
    "permanent christmas lights", "permanent christmas light installation", "permanent christmas lights installer",
    # buyer / local variants seen in the search-term report
    "permanent christmas lights lincoln ne", "permanent christmas lights near me",
    "permanent christmas light installation near me", "permanent christmas lights installation near me",
    "permanent holiday light installation", "permanent holiday light installation near me",
    "permanent lighting installation", "permanent outdoor lighting installation",
    # cost research seen in the search-term report (protected terms, intent-checked, never auto-negated)
    "permanent christmas lights cost", "permanent lights on house cost",
    "how much does it cost to have permanent christmas lights installed", "cost to install permanent outdoor lights",
    # broad product family seen as close variants of the head term
    "permanent outdoor lights", "permanent lights on house", "permanent house lights", "year round christmas lights",
    # seasonal-service family (different service: hanging/removal is EXCLUDED; shape reference only)
    "christmas light installation", "christmas light installers near me", "christmas light installation lincoln ne",
    # brands / names seen in queries or verified first-party
    "brilliant by night", "everlights",
]
START = (2022, 10)
END = (2026, 9)
MONTHS = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
          "OCTOBER", "NOVEMBER", "DECEMBER"]
out = {"run_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
       "network": "GOOGLE_SEARCH", "language": LANG, "geo_sets": GEO_SETS, "requested_range": [START, END],
       "historical": {}, "notes": [
           "Planner values are rounded buckets, not exact counts; close variants share one bucket; never sum rows",
           "Nebraska and US rows describe seasonal SHAPE only; they are not demand inside the service area",
       ]}


def hist(geos, start, end):
    req = c.get_type("GenerateKeywordHistoricalMetricsRequest")
    req.customer_id = CID
    req.keywords.extend(CANDIDATES)
    req.language = LANG
    req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in geos])
    req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    rng = req.historical_metrics_options.year_month_range
    rng.start.year, rng.start.month = start[0], c.enums.MonthOfYearEnum[MONTHS[start[1] - 1]]
    rng.end.year, rng.end.month = end[0], c.enums.MonthOfYearEnum[MONTHS[end[1] - 1]]
    resp = svc.generate_keyword_historical_metrics(request=req)
    rows = []
    for r in resp.results:
        m = r.keyword_metrics
        rows.append({"text": r.text, "close_variants": list(r.close_variants),
                     "avg": m.avg_monthly_searches if m._pb.HasField("avg_monthly_searches") else None,
                     "competition": E(m.competition), "comp_index": m.competition_index,
                     "top_low": round(m.low_top_of_page_bid_micros / 1e6, 2) if m.low_top_of_page_bid_micros else None,
                     "top_high": round(m.high_top_of_page_bid_micros / 1e6, 2) if m.high_top_of_page_bid_micros else None,
                     "monthly": {f"{x.year}-{MONTHS.index(E(x.month)) + 1:02d}": x.monthly_searches
                                 for x in m.monthly_search_volumes}})
    return rows


for label, geos in GEO_SETS.items():
    for start in (START, (2024, 10)):
        try:
            out["historical"][label] = hist(geos, start, END)
            out.setdefault("range_used", {})[label] = [start, END]
            break
        except Exception as exc:  # noqa: BLE001
            out["historical"][label] = {"error": str(exc)[:400]}
            print(f"  {label} start={start} failed: {str(exc)[:160]}")
            time.sleep(4)
    time.sleep(4)

write(EVID / "2026-10-05-planner.json", out)
for label, rows in out["historical"].items():
    print(f"\n--- {label} range={out.get('range_used', {}).get(label)} ---")
    if isinstance(rows, dict):
        print("  ERROR", rows["error"][:200])
        continue
    for r in rows:
        mo = r["monthly"]
        last = [mo.get(f"2025-{m:02d}") for m in (9, 10, 11, 12)]
        print(f"  {r['text'][:62]:<62} avg={str(r['avg']):>6} SepOctNovDec25={last} comp={r['competition']:<7} "
              f"top=${r['top_low']}-{r['top_high']} months={len(mo)} cv={len(r['close_variants'])}")
