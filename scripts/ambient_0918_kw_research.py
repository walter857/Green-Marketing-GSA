#!/usr/bin/env python3
"""Ambient | 2026-09-18 | Keyword Planner research for the six new ad groups.

READ-ONLY (GenerateKeywordHistoricalMetrics is a read). Planner has its own quota that
429s quickly, so geo targets are capped at 10 per call and candidates are batched.

Planner volume is a 10-city sample of a 75-location service area. It is NOT scaled up, and
Planner forecasts are never reported as historical results.
"""
from __future__ import annotations
import sys, json, datetime, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-18"
snap = json.loads((SNAP / "heating-build-snapshot-2026-09-17.json").read_text(encoding="utf-8"))
GEO_ALL = snap["reusable_geo_target_ids"]
GEO = GEO_ALL[:10]          # hard API cap of 10 geo targets per call

# BOFU candidates, intent-separated. Each ad group's terms must match what its destination
# page actually sells - verified against the 2026-09-18 crawl.
CAND = {
    "Boiler Repair": [
        "boiler repair", "boiler repair near me", "boiler repair service",
        "residential boiler repair", "boiler repair company", "boiler not working",
        "emergency boiler repair", "commercial boiler repair"],
    "Oil Furnace Installation": [
        "oil furnace installation", "oil furnace install", "install oil furnace",
        "oil furnace installers near me", "new oil furnace installation",
        "oil furnace installation cost"],
    "Oil Heating System Replacement": [
        "oil heating system replacement", "replace oil heating system",
        "oil furnace replacement", "oil boiler replacement", "oil system replacement",
        "replace oil furnace cost"],
    "Heat Pump Installation": [
        "heat pump installation", "heat pump installers near me", "install heat pump",
        "heat pump installation cost", "new heat pump installation",
        "heat pump installation near me"],
    "Geothermal HVAC Installation": [
        "geothermal hvac installation", "geothermal heat pump installation",
        "geothermal heating installation", "geothermal hvac installers",
        "geothermal system installation", "geothermal heating and cooling installation"],
    "Tankless Water Heater Installation": [
        "tankless water heater installation", "tankless water heater installers near me",
        "install tankless water heater", "tankless water heater installation cost",
        "tankless water heater replacement", "gas tankless water heater installation"],
}

c = client()
svc = c.get_service("KeywordPlanIdeaService")
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
       "read_only": True, "external_writes": 0,
       "geo_sample": GEO, "geo_sample_size": len(GEO),
       "geo_total_in_service_area": len(GEO_ALL),
       "scaling_warning": "Planner volume below is a 10-city SAMPLE of a 75-location "
                          "service area. It is deliberately NOT scaled to 75. Synonyms also "
                          "collapse into one demand bucket, so rows must not be summed.",
       "ad_groups": {}}

for ag, terms in CAND.items():
    req = c.get_type("GenerateKeywordHistoricalMetricsRequest")
    req.customer_id = CID
    req.keywords.extend(terms)
    req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in GEO])
    req.keyword_plan_network = (
        c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH)
    req.language = c.get_service("GoogleAdsService").language_constant_path("1000")
    rows = []
    try:
        resp = svc.generate_keyword_historical_metrics(request=req)
        for r in resp.results:
            m = r.keyword_metrics
            rows.append({
                "text": r.text,
                "avg_monthly_searches": m.avg_monthly_searches,
                "competition": E(m.competition),
                "competition_index": m.competition_index,
                "low_top_of_page_usd": round(m.low_top_of_page_bid_micros / 1e6, 2),
                "high_top_of_page_usd": round(m.high_top_of_page_bid_micros / 1e6, 2),
                "close_variants": sorted(r.close_variants)[:6]})
    except Exception as ex:
        rows = [{"error": str(ex)[:300]}]
    out["ad_groups"][ag] = rows
    print(f"\n=== {ag} ===")
    for x in sorted(rows, key=lambda z: -(z.get("avg_monthly_searches") or 0)):
        if "error" in x:
            print(f"   ERROR {x['error'][:160]}"); continue
        print(f"   {x['text'][:42]:42s} vol={x['avg_monthly_searches']:>5}  "
              f"{x['competition'][:6]:6s} idx={x['competition_index']:>3}  "
              f"TOP ${x['low_top_of_page_usd']:>6.2f}-${x['high_top_of_page_usd']:>6.2f}"
              + (f"  variants={x['close_variants'][:2]}" if x["close_variants"] else ""))
    time.sleep(2)

p = SNAP / f"expansion-keyword-planner-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print("EXTERNAL WRITES: 0")
