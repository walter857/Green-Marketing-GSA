#!/usr/bin/env python3
"""2026-09-28 READ-ONLY lever sizing for Apogee Lawns LLC - Live (8164626278).

1. Whitelist classification of the live search terms (aggregates only; raw terms stay on disk).
2. Hourly budget-lost impression share, to see whether the budget loss is pacing or a hard cap.
3. The owner's 2026-09-25 campaign-criterion edit, before/after.
4. Exact-canonical-name geo resolution for the expansion candidates.
5. Keyword forecasts for each lever over the remaining season.
Forecasts are Google's model, not a promise of traffic. Nothing here mutates.
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, E, client, q, write  # noqa: E402

c = client()
OUT = {}

print("=== 1. LIVE SEARCH TERMS - WHITELIST CLASSIFICATION (aggregates only) ===")
raw = json.loads((EVID / "2026-09-28-search-terms-RAW.json").read_text(encoding="utf-8"))
SERVICE = re.compile(r"\b(install|installs|installer|installers|installation|installed|installing|company|companies|"
                     r"contractor|contractors|service|services|near me|quote|quotes|estimate|professional|pro|"
                     r"hire|cost|costs|price|prices|pricing)\b")
LOCAL = re.compile(r"\b(lincoln|nebraska|ne|waverly|eagle|crete|ashland|omaha)\b")
HEAD_TOKENS = {"permanent", "christmas", "xmas", "light", "lights", "holiday"}
buckets = defaultdict(lambda: {"terms": 0, "impr": 0, "clicks": 0, "cost": 0.0})
for x in raw:
    t = x["term"].lower()
    toks = set(re.findall(r"[a-z0-9']+", t))
    if SERVICE.search(t):
        b = "SERVICE_MARKER"
    elif LOCAL.search(t):
        b = "LOCAL_MARKER_ONLY"
    elif toks <= HEAD_TOKENS:
        b = "BARE_HEAD_TERM_VARIANT"
    else:
        b = "OUT_OF_SCOPE"
    k = (b, x["kw"], x["mt"])
    buckets[k]["terms"] += 1
    buckets[k]["impr"] += x["impr"]
    buckets[k]["clicks"] += x["clicks"]
    buckets[k]["cost"] += x["cost"]
for k, v in sorted(buckets.items()):
    print(f"  {k[0]:<24} via {k[2]:<6} {k[1]:<40} terms={v['terms']} impr={v['impr']} clicks={v['clicks']} cost=${v['cost']:.2f}")
OUT["search_term_buckets"] = {"|".join(k): v for k, v in buckets.items()}

print("\n=== 2. BUDGET-LOST IS BY DAY x HOUR ===")
try:
    hr = q(c, """SELECT segments.date, segments.hour, metrics.impressions, metrics.search_impression_share,
        metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share
        FROM campaign WHERE segments.date BETWEEN '2026-09-21' AND '2026-09-28'""")
    lost_hours = defaultdict(int)
    for r in hr:
        m = r.metrics
        if m.search_budget_lost_impression_share > 0:
            lost_hours[r.segments.hour] += 1
            print(f"  {r.segments.date} h{r.segments.hour:02d} impr={m.impressions} IS={m.search_impression_share:.2f} "
                  f"lostB={m.search_budget_lost_impression_share:.2f} lostR={m.search_rank_lost_impression_share:.2f}")
    print(f"  hours carrying budget loss: {dict(sorted(lost_hours.items()))}")
except Exception as exc:  # noqa: BLE001
    print(f"  hourly IS not available: {str(exc)[:200]}")

print("\n=== 2b. SPEND vs BUDGET by day (does the budget ever bind?) ===")
d = q(c, """SELECT segments.date, metrics.cost_micros, metrics.clicks, campaign_budget.amount_micros
    FROM campaign WHERE segments.date BETWEEN '2026-09-21' AND '2026-09-28'""")
for r in d:
    print(f"  {r.segments.date} cost=${r.metrics.cost_micros/1e6:.2f} of ${r.campaign_budget.amount_micros/1e6:.2f} "
          f"clicks={r.metrics.clicks}")
cl = q(c, """SELECT segments.date, ad_group_criterion.keyword.text, metrics.clicks, metrics.cost_micros
    FROM keyword_view WHERE segments.date BETWEEN '2026-09-21' AND '2026-09-28' AND metrics.clicks > 0""")
for r in cl:
    print(f"  click day {r.segments.date} kw='{r.ad_group_criterion.keyword.text}' clicks={r.metrics.clicks} "
          f"cost=${r.metrics.cost_micros/1e6:.2f} per-click=${r.metrics.cost_micros/1e6/r.metrics.clicks:.2f}")

print("\n=== 3. OWNER EDIT 2026-09-25 ===")
ch = q(c, """SELECT change_event.change_date_time, change_event.change_resource_name, change_event.client_type,
    change_event.changed_fields, change_event.old_resource, change_event.new_resource
    FROM change_event WHERE change_event.change_date_time >= '2026-09-25 00:00:00'
    AND change_event.change_date_time <= '2026-09-25 23:59:59' LIMIT 50""")
for r in ch:
    e = r.change_event
    o, n = e.old_resource.campaign_criterion, e.new_resource.campaign_criterion
    print(f"  {e.change_date_time} {E(e.client_type)} {e.change_resource_name}")
    print(f"    fields={list(e.changed_fields.paths)}")
    print(f"    old: type={E(o.type_)} status={E(o.status)} bid_mod={o.bid_modifier} geo={o.location.geo_target_constant} "
          f"kw='{o.keyword.text}' neg={o.negative}")
    print(f"    new: type={E(n.type_)} status={E(n.status)} bid_mod={n.bid_modifier} geo={n.location.geo_target_constant} "
          f"kw='{n.keyword.text}' neg={n.negative}")
cid_crit = q(c, """SELECT campaign_criterion.resource_name, campaign_criterion.type, campaign_criterion.bid_modifier,
    campaign_criterion.status FROM campaign_criterion WHERE campaign_criterion.bid_modifier != 0""")
for r in cid_crit:
    x = r.campaign_criterion
    print(f"  non-zero bid modifier: {x.resource_name} {E(x.type_)} {x.bid_modifier} {E(x.status)}")

print("\n=== 4. GEO RESOLUTION (exact canonical name only) ===")
WANT = ["Omaha,Nebraska,United States", "Lancaster County,Nebraska,United States",
        "Sarpy County,Nebraska,United States", "Douglas County,Nebraska,United States"]
geo = {}
for cn in WANT:
    rows = q(c, f"""SELECT geo_target_constant.id, geo_target_constant.canonical_name, geo_target_constant.target_type,
        geo_target_constant.status FROM geo_target_constant WHERE geo_target_constant.canonical_name = '{cn}'""")
    for r in rows:
        g = r.geo_target_constant
        print(f"  {g.id:>9} {g.target_type:<10} {E(g.status):<8} {g.canonical_name}")
        if E(g.status) == "ENABLED":
            geo[cn] = str(g.id)
    if not rows:
        print(f"  NO EXACT MATCH for {cn}")
OUT["geo_resolved"] = geo

print("\n=== 5. FORECASTS - remaining season 2026-09-29 .. 2026-12-20 ===")
svc = c.get_service("KeywordPlanIdeaService")
KMT = c.enums.KeywordMatchTypeEnum
LANG = "languageConstants/1000"
CURRENT_GEOS = ["1021635", "1021647", "1021696", "1021783", "9024651", "9024671", "9024703",
                "9024728", "9024746", "9024748", "9024753", "9024754", "9195288", "9233865"]
BASE = [("permanent christmas light installation", "EXACT"), ("permanent christmas light installation", "PHRASE"),
        ("permanent christmas lights installer", "EXACT"), ("permanent christmas lights installer", "PHRASE"),
        ("permanent christmas lights", "EXACT")]
HEAD_PHRASE = [("permanent christmas lights", "PHRASE")]
SYN = [(t, m) for t in ["permanent holiday lights", "permanent holiday lighting", "permanent outdoor lights",
                        "permanent outdoor lighting", "permanent roofline lighting", "permanent house lights",
                        "permanent led christmas lights", "year round christmas lights"] for m in ("EXACT", "PHRASE")]
GENERIC = [(t, m) for t in ["christmas light installation", "christmas light installers",
                            "christmas lights installation"] for m in ("EXACT", "PHRASE")]


def forecast(keywords, geos, cap, daily, start="2026-09-29", end="2026-12-20"):
    req = c.get_type("GenerateKeywordForecastMetricsRequest")
    req.customer_id = CID
    req.currency_code = "USD"
    req.forecast_period.start_date = start
    req.forecast_period.end_date = end
    camp = req.campaign
    camp.language_constants.append(LANG)
    camp.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in geos])
    camp.bidding_strategy.maximize_clicks_bidding_strategy.daily_target_spend_micros = int(daily * 1e6)
    camp.bidding_strategy.maximize_clicks_bidding_strategy.max_cpc_bid_ceiling_micros = int(cap * 1e6)
    ag = c.get_type("ForecastAdGroup")
    for text, mt in keywords:
        k = c.get_type("KeywordInfo")
        k.text = text
        k.match_type = getattr(KMT, mt)
        ag.keywords.append(k)
    camp.ad_groups.append(ag)
    try:
        m = svc.generate_keyword_forecast_metrics(request=req).campaign_forecast_metrics
        return {"clicks": round(m.clicks, 1), "cost": round(m.cost_micros / 1e6, 2),
                "cpc": round(m.average_cpc_micros / 1e6, 2) if m.average_cpc_micros else None}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {str(exc)[:240]}"}


OMAHA = [geo["Omaha,Nebraska,United States"]] if "Omaha,Nebraska,United States" in geo else []
LANC = [geo["Lancaster County,Nebraska,United States"]] if "Lancaster County,Nebraska,United States" in geo else []
SCEN = [
    ("S0 current build, $8 cap", BASE, CURRENT_GEOS, 8.0, 16.44),
    ("S1 current build, $10 cap", BASE, CURRENT_GEOS, 10.0, 16.44),
    ("S2 current build, $12 cap", BASE, CURRENT_GEOS, 12.0, 16.44),
    ("S3 + head PHRASE", BASE + HEAD_PHRASE, CURRENT_GEOS, 8.0, 16.44),
    ("S4 + synonyms E+P", BASE + SYN, CURRENT_GEOS, 8.0, 16.44),
    ("S5 + head PHRASE + synonyms", BASE + HEAD_PHRASE + SYN, CURRENT_GEOS, 8.0, 16.44),
    ("S6 current kws + Lancaster Cty", BASE, CURRENT_GEOS + LANC, 8.0, 16.44),
    ("S7 current kws + Omaha", BASE, CURRENT_GEOS + OMAHA, 8.0, 16.44),
    ("S8 current kws + Omaha, $30/day", BASE, CURRENT_GEOS + OMAHA, 8.0, 30.0),
    ("S9 full (P+syn) + Omaha, $30/day", BASE + HEAD_PHRASE + SYN, CURRENT_GEOS + OMAHA, 8.0, 30.0),
    ("S10 generic install only, Lincoln area", GENERIC, CURRENT_GEOS, 8.0, 16.44),
    ("S11 generic install only, + Omaha", GENERIC, CURRENT_GEOS + OMAHA, 8.0, 16.44),
    ("S12 Omaha ONLY, current kws", BASE, OMAHA, 8.0, 16.44),
]
fc = {}
print(f"  {'scenario':<42} {'clicks':>7} {'cost':>9} {'cpc':>6}")
for label, kws, geos, cap, daily in SCEN:
    if not geos:
        print(f"  {label:<42} SKIPPED (geo unresolved)")
        continue
    r = forecast(kws, geos, cap, daily)
    fc[label] = r
    if "error" in r:
        print(f"  {label:<42} ERROR {r['error'][:150]}")
    else:
        print(f"  {label:<42} {r['clicks']:>7} {r['cost']:>9} {str(r['cpc']):>6}")
    time.sleep(2)
OUT["forecasts_2026-09-29_2026-12-20"] = fc

write(EVID / "2026-09-28-levers.json", OUT)
