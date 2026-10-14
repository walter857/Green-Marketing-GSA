#!/usr/bin/env python3
"""2026-09-28 (run B) READ-ONLY, reproducible Keyword Planner forecasts for Apogee Lawns.

Horizon 2026-09-29 .. 2026-12-20 - the SAME window as the first 2026-09-28 run, so results are
like-for-like, and it is still entirely in the future relative to this run. It is a forecast
window, not a campaign end date.

Tool limits in the installed google-ads v25 client (introspected, not assumed):
  CampaignToForecast = language_constants, geo_target_constants, bidding_strategy, ad_groups only;
  ForecastAdGroup = keywords only; response = campaign_forecast_metrics only.
  So a forecast CANNOT include negative keywords, the live tablet -100% exclusion, network
  settings, ad schedule or per-ad-group numbers, and it models ONE campaign with ONE budget.
  Each scenario changes one variable from S0 unless labelled combined.
"""
from __future__ import annotations

import datetime
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, client, write  # noqa: E402

c = client()
svc = c.get_service("KeywordPlanIdeaService")
KMT = c.enums.KeywordMatchTypeEnum
START, END = "2026-09-29", "2026-12-20"
DAYS = 83
LANG = "languageConstants/1000"
G14 = ["1021635", "1021647", "1021696", "1021783", "9024651", "9024671", "9024703",
       "9024728", "9024746", "9024748", "9024753", "9024754", "9195288", "9233865"]
OMAHA = ["1021721"]
BASE = [[("permanent christmas light installation", "PHRASE"), ("permanent christmas light installation", "EXACT"),
         ("permanent christmas lights installer", "PHRASE"), ("permanent christmas lights installer", "EXACT")],
        [("permanent christmas lights", "EXACT")]]
LOCAL_AG = [("permanent christmas lights lincoln", "PHRASE"), ("permanent christmas lights lincoln", "EXACT"),
            ("permanent christmas lights near me", "PHRASE"), ("permanent christmas lights near me", "EXACT")]
LOCAL_LINCOLN_ONLY = [("permanent christmas lights lincoln", "PHRASE"), ("permanent christmas lights lincoln", "EXACT")]
HOLIDAY_INSTALL = [("permanent holiday light installation", "PHRASE"), ("permanent holiday light installation", "EXACT"),
                   ("permanent holiday lights installer", "PHRASE"), ("permanent holiday lights installer", "EXACT")]
HOLIDAY_GENERIC_E = [("permanent holiday lights", "EXACT")]
HOLIDAY_GENERIC_EP = [("permanent holiday lights", "EXACT"), ("permanent holiday lights", "PHRASE")]
OUTDOOR_E = [("permanent outdoor lights", "EXACT")]
HEAD_PHRASE = [("permanent christmas lights", "PHRASE")]


def fc(ad_groups, geos=G14, cap=8.00, daily=16.44):
    req = c.get_type("GenerateKeywordForecastMetricsRequest")
    req.customer_id = CID
    req.currency_code = "USD"
    req.forecast_period.start_date = START
    req.forecast_period.end_date = END
    camp = req.campaign
    camp.language_constants.append(LANG)
    camp.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in geos])
    camp.bidding_strategy.maximize_clicks_bidding_strategy.daily_target_spend_micros = int(round(daily * 1e6))
    camp.bidding_strategy.maximize_clicks_bidding_strategy.max_cpc_bid_ceiling_micros = int(round(cap * 1e6))
    seen = set()
    for kws in ad_groups:
        ag = c.get_type("ForecastAdGroup")
        for text, mt in kws:
            if (text, mt) in seen:  # dedupe identical text+match type across ad groups
                continue
            seen.add((text, mt))
            k = c.get_type("KeywordInfo")
            k.text, k.match_type = text, getattr(KMT, mt)
            ag.keywords.append(k)
        camp.ad_groups.append(ag)
    try:
        m = svc.generate_keyword_forecast_metrics(request=req).campaign_forecast_metrics
        return {"clicks": round(m.clicks, 1), "cost": round(m.cost_micros / 1e6, 2),
                "avg_cpc": round(m.average_cpc_micros / 1e6, 2) if m.average_cpc_micros else None,
                "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                "request": {"geos": geos, "cap": cap, "daily": daily,
                            "ad_groups": [[f"{t}|{mt}" for t, mt in kws] for kws in ad_groups]}}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)[:300]}


SCEN = [
    ("S0 current build (baseline)", dict(ad_groups=BASE)),
    ("C1 CPC cap $6", dict(ad_groups=BASE, cap=6.00)),
    ("C2 CPC cap $10", dict(ad_groups=BASE, cap=10.00)),
    ("C3 CPC cap $12", dict(ad_groups=BASE, cap=12.00)),
    ("B1 daily $10.00", dict(ad_groups=BASE, daily=10.00)),
    ("B2 daily $25.00 (exceeds approved total; sensitivity only)", dict(ad_groups=BASE, daily=25.00)),
    ("K1 + head term PHRASE (isolated test)", dict(ad_groups=[BASE[0], BASE[1] + HEAD_PHRASE])),
    ("K2 + local ad group: lincoln + near me, P+E", dict(ad_groups=BASE + [LOCAL_AG])),
    ("K2b + local ad group: lincoln only, P+E", dict(ad_groups=BASE + [LOCAL_LINCOLN_ONLY])),
    ("K3 + holiday installation synonyms, P+E", dict(ad_groups=[BASE[0] + HOLIDAY_INSTALL, BASE[1]])),
    ("K4 + generic permanent holiday lights, E", dict(ad_groups=BASE + [HOLIDAY_GENERIC_E])),
    ("K5 + generic permanent holiday lights, E+P", dict(ad_groups=BASE + [HOLIDAY_GENERIC_EP])),
    ("K6 + permanent outdoor lights, E", dict(ad_groups=BASE + [OUTDOOR_E])),
    ("X1 combined: S0 + K2 at $16.44 and $8", dict(ad_groups=BASE + [LOCAL_AG])),
    ("X2 combined: S0 + K2 at $10 cap", dict(ad_groups=BASE + [LOCAL_AG], cap=10.00)),
    ("O1 CONDITIONAL research only: Omaha alone, current keywords, own $16.44", dict(ad_groups=BASE, geos=OMAHA)),
]
res = {}
print(f"window {START}..{END} ({DAYS} days) | Maximize Clicks | English | Google Search network implied\n")
print(f"  {'scenario':<66} {'clicks':>7} {'cost':>9} {'cpc':>6} {'d_clicks':>9} {'d_cost':>9}")
for label, kw in SCEN:
    r = fc(**kw)
    res[label] = r
    if "error" in r:
        print(f"  {label:<66} ERROR {r['error'][:120]}")
    else:
        b = res["S0 current build (baseline)"]
        print(f"  {label:<66} {r['clicks']:>7} {r['cost']:>9} {str(r['avg_cpc']):>6} "
              f"{r['clicks'] - b['clicks']:>+9.1f} {r['cost'] - b['cost']:>+9.2f}")
    time.sleep(2.5)
write(EVID / "2026-09-28b-forecasts.json", {"window": [START, END], "days": DAYS, "tool_limits": __doc__, "results": res})
