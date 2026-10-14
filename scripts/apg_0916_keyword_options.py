#!/usr/bin/env python3
"""2026-09-16 READ-ONLY keyword strategy evidence: Option A vs Option B.

Two independent reads:
  1. generate_keyword_ideas seeded on the head term, to characterise the INTENT
     composition of the query space around it (product vs service-hiring).
  2. generate_keyword_forecast_metrics by MATCH TYPE, so Option A and Option B are
     compared on modelled clicks and cost at the real $16.44 daily budget.

Forecasts are Google's model, not a promise of traffic.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, client, write, E  # noqa: E402

c = client()
svc = c.get_service("KeywordPlanIdeaService")

GEOS = ["1021696", "9024746", "1021635", "9024753", "9024703",
        "9024754", "9024671", "9024748", "1021783", "9195288"]
LANG = "languageConstants/1000"
out = {"geo_sample": GEOS, "geo_cap_note": "planner caps geo_target_constants at 10"}

# ---------------------------------------------------------------------------
# 1. INTENT COMPOSITION of the query space around the head term
# ---------------------------------------------------------------------------
print("=== 1. KEYWORD IDEAS SEEDED ON THE HEAD TERM ===")
req = c.get_type("GenerateKeywordIdeasRequest")
req.customer_id = CID
req.language = LANG
req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in GEOS])
req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
req.keyword_seed.keywords.append("permanent christmas lights")
ideas = []
try:
    for r in svc.generate_keyword_ideas(request=req):
        m = r.keyword_idea_metrics
        ideas.append({
            "text": r.text,
            "avg": m.avg_monthly_searches,
            "comp": E(m.competition),
            "low": round(m.low_top_of_page_bid_micros / 1e6, 2) if m.low_top_of_page_bid_micros else None,
            "high": round(m.high_top_of_page_bid_micros / 1e6, 2) if m.high_top_of_page_bid_micros else None,
        })
except Exception as exc:  # noqa: BLE001
    print(f"  FAILED: {type(exc).__name__}: {str(exc)[:300]}")

print(f"  ideas returned: {len(ideas)}")

# Intent classification. Every bucket is a WHITELIST of markers; anything that matches
# no marker is reported as UNCLASSIFIED rather than silently assumed to be service intent.
SERVICE = r"\b(install|installs|installer|installers|installation|company|companies|" \
          r"contractor|contractors|service|services|near me|quote|estimate|pro|pros|" \
          r"professional|hire|cost|price|pricing)\b"
PRODUCT = r"\b(amazon|walmart|lowes|lowe's|menards|costco|ebay|temu|home depot|buy|" \
          r"for sale|sale|kit|kits|bulb|bulbs|strip|strips|wire|clip|clips|" \
          r"controller|app|track|channel|housing|wholesale|shop|store|cheap)\b"
DIY = r"\b(diy|how to|do it yourself|install yourself|tutorial|instructions|" \
      r"homemade|make your own)\b"
BRAND = r"\b(everlights|trimlight|jellyfish|gemstone|govee|oelo|celebright|" \
        r"永|jellyfish lighting)\b"
RESEARCH = r"\b(vs|versus|review|reviews|best|worth it|compare|comparison|" \
           r"ideas|what are|are permanent)\b"


def classify(t):
    tl = t.lower()
    tags = []
    if re.search(BRAND, tl):
        tags.append("BRAND")
    if re.search(DIY, tl):
        tags.append("DIY")
    if re.search(PRODUCT, tl):
        tags.append("PRODUCT")
    if re.search(RESEARCH, tl):
        tags.append("RESEARCH")
    if re.search(SERVICE, tl):
        tags.append("SERVICE")
    return tags or ["UNCLASSIFIED"]


buckets = {}
for i in ideas:
    for t in classify(i["text"]):
        buckets.setdefault(t, {"n": 0, "vol": 0})
        buckets[t]["n"] += 1
        buckets[t]["vol"] += i["avg"] or 0

print("\n  INTENT COMPOSITION of the ideas around 'permanent christmas lights'")
print("  (a term can carry more than one tag; volume is the bucket ceiling, never additive)")
tot_vol = sum(i["avg"] or 0 for i in ideas)
for k, v in sorted(buckets.items(), key=lambda kv: -kv[1]["vol"]):
    share = (v["vol"] / tot_vol * 100) if tot_vol else 0
    print(f"    {k:<14} terms={v['n']:>4}  summed_volume={v['vol']:>7}  {share:5.1f}% of summed volume")

# service-only vs anything-not-service, on the terms a PHRASE head keyword would reach
def phrase_reaches(q_, phrase="permanent christmas lights"):
    pt = phrase.split()
    qt = re.findall(r"[a-z0-9']+", q_.lower())
    n = len(pt)
    # tolerate the singular/plural close variant Google applies to phrase match
    alt = ["light" if w == "lights" else w for w in pt]
    return any(qt[i:i + n] == pt or qt[i:i + n] == alt for i in range(len(qt) - n + 1))


reached = [i for i in ideas if phrase_reaches(i["text"])]
r_serviceish = [i for i in reached if "SERVICE" in classify(i["text"])]
r_nonservice = [i for i in reached if "SERVICE" not in classify(i["text"])]
print(f"\n  Terms a PHRASE \"permanent christmas lights\" keyword would reach: {len(reached)}")
print(f"    carrying a service-hiring marker : {len(r_serviceish):>4} terms, "
      f"{sum(x['avg'] or 0 for x in r_serviceish):>6} summed volume")
print(f"    NO service marker                : {len(r_nonservice):>4} terms, "
      f"{sum(x['avg'] or 0 for x in r_nonservice):>6} summed volume")
print("\n  Top 30 reached terms WITHOUT a service-hiring marker (the irrelevant-intent risk):")
for i in sorted(r_nonservice, key=lambda x: -(x["avg"] or 0))[:30]:
    print(f"    {i['avg'] or 0:>6}  {classify(i['text'])!s:<28} {i['text']}")

out["ideas_count"] = len(ideas)
out["intent_buckets"] = buckets
out["phrase_reached_total"] = len(reached)
out["phrase_reached_service"] = len(r_serviceish)
out["phrase_reached_nonservice"] = len(r_nonservice)
out["phrase_reached_nonservice_terms"] = sorted(
    r_nonservice, key=lambda x: -(x["avg"] or 0))[:60]
out["ideas"] = ideas

# ---------------------------------------------------------------------------
# 2. FORECAST BY MATCH TYPE
# ---------------------------------------------------------------------------
MT = c.enums.KeywordPlanNetworkEnum  # noqa: F841
KMT = c.enums.KeywordMatchTypeEnum


def forecast(label, keywords, ceiling_usd, start, end, daily=16.44):
    """keywords = [(text, 'EXACT'|'PHRASE')]"""
    req = c.get_type("GenerateKeywordForecastMetricsRequest")
    req.customer_id = CID
    req.currency_code = "USD"
    req.forecast_period.start_date = start
    req.forecast_period.end_date = end
    camp = req.campaign
    camp.language_constants.append(LANG)
    camp.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in GEOS])
    camp.bidding_strategy.maximize_clicks_bidding_strategy.daily_target_spend_micros = int(daily * 1e6)
    camp.bidding_strategy.maximize_clicks_bidding_strategy.max_cpc_bid_ceiling_micros = int(ceiling_usd * 1e6)
    ag = c.get_type("ForecastAdGroup")
    for text, mt in keywords:
        k = c.get_type("KeywordInfo")
        k.text = text
        k.match_type = getattr(KMT, mt)
        ag.keywords.append(k)
    camp.ad_groups.append(ag)
    try:
        resp = svc.generate_keyword_forecast_metrics(request=req)
        m = resp.campaign_forecast_metrics
        return {
            "clicks": round(m.clicks, 1),
            "cost": round(m.cost_micros / 1e6, 2),
            "avg_cpc": round(m.average_cpc_micros / 1e6, 2) if m.average_cpc_micros else None,
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}


OPTIONS = {
    "A_quality_first": [
        ("permanent christmas light installation", "EXACT"),
        ("permanent christmas light installation", "PHRASE"),
        ("permanent christmas lights installer", "EXACT"),
        ("permanent christmas lights installer", "PHRASE"),
    ],
    "B_head_exact_only": [("permanent christmas lights", "EXACT")],
    "B2_head_exact_plus_phrase": [
        ("permanent christmas lights", "EXACT"),
        ("permanent christmas lights", "PHRASE"),
    ],
    "A_plus_B_exact": [
        ("permanent christmas light installation", "EXACT"),
        ("permanent christmas light installation", "PHRASE"),
        ("permanent christmas lights installer", "EXACT"),
        ("permanent christmas lights installer", "PHRASE"),
        ("permanent christmas lights", "EXACT"),
    ],
}
WINDOWS = {
    "season_2026-09-21_to_12-20": ("2026-09-21", "2026-12-20"),
    "peak_nov_2026-11-01_to_11-30": ("2026-11-01", "2026-11-30"),
}
CEILINGS = [4.00, 6.00, 8.00, 10.00, 13.00]

print("\n\n=== 2. FORECAST BY MATCH TYPE (Maximize Clicks, $16.44/day) ===")
fc = {}
for wlabel, (s, e) in WINDOWS.items():
    fc[wlabel] = {}
    print(f"\n--- window {wlabel} ({s} .. {e}) ---")
    print(f"  {'option':<28} {'cap':>6} {'clicks':>8} {'cost':>9} {'avgCPC':>7}")
    for olabel, kws in OPTIONS.items():
        fc[wlabel][olabel] = {}
        for cap in CEILINGS:
            r = forecast(olabel, kws, cap, s, e)
            fc[wlabel][olabel][f"cap_{cap:.2f}"] = r
            if "error" in r:
                print(f"  {olabel:<28} {cap:>6.2f}   ERROR {r['error'][:70]}")
            else:
                print(f"  {olabel:<28} {cap:>6.2f} {r['clicks']:>8} {r['cost']:>9} "
                      f"{str(r['avg_cpc']):>7}")
            time.sleep(2)
out["forecasts"] = fc

write(EVID / "2026-09-16-keyword-options.json", out)
