#!/usr/bin/env python3
"""2026-09-28 READ-ONLY: which synonym keyword carries the S4 forecast jump, and is it hiring intent?

Per synonym (Exact + Phrase, current 14 geos, $8 cap, $16.44/day, 2026-09-29..12-20):
  - Google's click/cost forecast
  - whitelist intent share of the Keyword Planner ideas that the PHRASE keyword would reach
Aggregates only; idea texts are written to disk and never printed.
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, E, client, write  # noqa: E402

c = client()
svc = c.get_service("KeywordPlanIdeaService")
KMT = c.enums.KeywordMatchTypeEnum
LANG = "languageConstants/1000"
GEOS14 = ["1021635", "1021647", "1021696", "1021783", "9024651", "9024671", "9024703",
          "9024728", "9024746", "9024748", "9024753", "9024754", "9195288", "9233865"]
# planner ideas cap geo at 10: the ten with the largest reach, per the 2026-09-16 sample
GEOS10 = ["1021696", "9024746", "1021635", "9024753", "9024703",
          "9024754", "9024671", "9024748", "1021783", "9195288"]
SYN = ["permanent holiday lights", "permanent holiday lighting", "permanent outdoor lights",
       "permanent outdoor lighting", "permanent roofline lighting", "permanent house lights",
       "permanent led christmas lights", "year round christmas lights"]
SERVICE = re.compile(r"\b(install|installs|installer|installers|installation|installed|installing|company|companies|"
                     r"contractor|contractors|service|services|near me|quote|quotes|estimate|professional|pro|"
                     r"hire|cost|costs|price|prices|pricing|lincoln|nebraska|ne|omaha)\b")


def forecast(keywords):
    req = c.get_type("GenerateKeywordForecastMetricsRequest")
    req.customer_id = CID
    req.currency_code = "USD"
    req.forecast_period.start_date = "2026-09-29"
    req.forecast_period.end_date = "2026-12-20"
    camp = req.campaign
    camp.language_constants.append(LANG)
    camp.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in GEOS14])
    camp.bidding_strategy.maximize_clicks_bidding_strategy.daily_target_spend_micros = 16_440_000
    camp.bidding_strategy.maximize_clicks_bidding_strategy.max_cpc_bid_ceiling_micros = 8_000_000
    ag = c.get_type("ForecastAdGroup")
    for text, mt in keywords:
        k = c.get_type("KeywordInfo")
        k.text = text
        k.match_type = getattr(KMT, mt)
        ag.keywords.append(k)
    camp.ad_groups.append(ag)
    try:
        m = svc.generate_keyword_forecast_metrics(request=req).campaign_forecast_metrics
        return {"clicks": round(m.clicks, 1), "cost": round(m.cost_micros / 1e6, 2)}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)[:200]}


def contains_phrase(text, phrase):
    qt = re.findall(r"[a-z0-9']+", text.lower())
    pt = phrase.split()
    alt = [w[:-1] if w.endswith("s") else w for w in pt]
    n = len(pt)
    return any(qt[i:i + n] in (pt, alt) for i in range(len(qt) - n + 1))


print("=== KEYWORD IDEAS seeded on the 8 synonyms (Lincoln sample, 10 geos) ===")
req = c.get_type("GenerateKeywordIdeasRequest")
req.customer_id = CID
req.language = LANG
req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in GEOS10])
req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
req.keyword_seed.keywords.extend(SYN)
ideas = []
try:
    for r in svc.generate_keyword_ideas(request=req):
        m = r.keyword_idea_metrics
        ideas.append({"text": r.text, "avg": m.avg_monthly_searches or 0, "comp": E(m.competition),
                      "months": {f"{E(x.month)}-{x.year}": x.monthly_searches for x in m.monthly_search_volumes}})
except Exception as exc:  # noqa: BLE001
    print(f"  FAILED: {str(exc)[:300]}")
write(EVID / "2026-09-28-synonym-ideas-RAW.json", ideas)
print(f"  ideas returned: {len(ideas)}")

out = {}
print(f"\n  {'synonym':<32} {'fc_clicks':>9} {'fc_cost':>8} | {'reach_terms':>11} {'svc_terms':>9} "
      f"{'svc_vol':>7} {'other_vol':>9} {'exact_bucket_avg':>16} {'NOV25':>6}")
for s in SYN:
    f = forecast([(s, "EXACT"), (s, "PHRASE")])
    time.sleep(2)
    reach = [i for i in ideas if contains_phrase(i["text"], s)]
    svc_terms = [i for i in reach if SERVICE.search(i["text"].lower())]
    other = [i for i in reach if not SERVICE.search(i["text"].lower())]
    exact = [i for i in ideas if i["text"].lower() == s]
    ex_avg = exact[0]["avg"] if exact else None
    ex_nov = exact[0]["months"].get("NOVEMBER-2025") if exact else None
    out[s] = {"forecast": f, "reach_terms": len(reach), "service_terms": len(svc_terms),
              "service_vol": sum(i["avg"] for i in svc_terms), "other_vol": sum(i["avg"] for i in other),
              "exact_bucket_avg": ex_avg, "exact_nov25": ex_nov}
    fc = f"{f.get('clicks', 'ERR'):>9} {f.get('cost', 'ERR'):>8}"
    print(f"  {s:<32} {fc} | {len(reach):>11} {len(svc_terms):>9} {out[s]['service_vol']:>7} "
          f"{out[s]['other_vol']:>9} {str(ex_avg):>16} {str(ex_nov):>6}")
write(EVID / "2026-09-28-synonyms.json", out)
