#!/usr/bin/env python3
"""Ambient | 2026-09-15 | Keyword Planner: commercial + generic BOFU demand. READ-ONLY.

KeywordPlanIdeaService caps geo_target_constants at 10 and has its own quota that 429s
quickly, so this makes a small number of batched calls with a pause between them.
"""
from __future__ import annotations
import sys, json, time, datetime
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-15"
c = client(); identity_gate(c, verbose=False)
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "read_only": True}

# Resolve the live geo targets on campaign 24132507747 and pick 10 representative places.
geo_ids = sorted({r.campaign_criterion.location.geo_target_constant.split("/")[-1]
                  for r in q(c, """SELECT campaign.id,
                                          campaign_criterion.location.geo_target_constant,
                                          campaign_criterion.negative
                                   FROM campaign_criterion
                                   WHERE campaign.id = 24132507747
                                     AND campaign_criterion.type = LOCATION
                                     AND campaign_criterion.negative = FALSE""")})
print(f"live geo targets on 24132507747: {len(geo_ids)}")
names = {}
for i in range(0, len(geo_ids), 40):
    batch = ",".join(f"'geoTargetConstants/{g}'" for g in geo_ids[i:i + 40])
    for r in q(c, f"""SELECT geo_target_constant.id, geo_target_constant.canonical_name,
                             geo_target_constant.target_type
                      FROM geo_target_constant
                      WHERE geo_target_constant.resource_name IN ({batch})"""):
        names[str(r.geo_target_constant.id)] = (r.geo_target_constant.canonical_name,
                                                E(r.geo_target_constant.target_type))
PREFERRED = ["Columbia,Maryland", "Severn,Maryland", "Severna Park,Maryland",
             "Annapolis,Maryland", "Glen Burnie,Maryland", "Ellicott City,Maryland",
             "Laurel,Maryland", "Catonsville,Maryland", "Bowie,Maryland", "Odenton,Maryland"]
chosen = []
for want in PREFERRED:
    for gid, (can, _) in names.items():
        if can.startswith(want) and gid not in chosen and len(chosen) < 10:
            chosen.append(gid)
            break
if len(chosen) < 10:
    for gid in geo_ids:
        if gid not in chosen and len(chosen) < 10:
            chosen.append(gid)
print("planner geo sample (max 10 of the live set):")
for g in chosen:
    print(f"   {g}  {names.get(g, ('?', '?'))[0]}")
out["geo_sample"] = [{"id": g, "canonical": names.get(g, ("?", "?"))[0]} for g in chosen]
out["geo_cap_note"] = ("KeywordPlanIdeaService caps geo_target_constants at 10; "
                       f"{len(chosen)} of {len(geo_ids)} live targets sampled")

svc = c.get_service("KeywordPlanIdeaService")
BATCHES = {
    "commercial": ["commercial hvac installation", "commercial hvac contractor",
                   "commercial hvac company", "commercial hvac replacement",
                   "rooftop unit installation", "commercial air conditioning installation",
                   "commercial heat pump installation", "commercial hvac services",
                   "commercial hvac installation near me", "commercial hvac repair"],
    "generic_bofu": ["hvac companies near me", "hvac company near me",
                     "hvac contractor near me", "hvac near me",
                     "heating and cooling companies near me", "hvac service near me",
                     "hvac technician near me", "air conditioning company near me",
                     "heating and cooling near me", "local hvac company near me"],
    "service_core": ["ac repair near me", "hvac repair near me", "hvac installers near me",
                     "hvac replacement near me", "gas boiler repair",
                     "furnace repair near me", "boiler repair near me",
                     "air conditioner repair near me", "hvac installation near me",
                     "ductwork installation near me"],
}
res = {}
for label, seeds in BATCHES.items():
    try:
        req = c.get_type("GenerateKeywordHistoricalMetricsRequest")
        req.customer_id = CID
        req.keywords.extend(seeds)
        req.language = "languageConstants/1000"
        req.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in chosen])
        req.keyword_plan_network = (
            c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH)
        resp = svc.generate_keyword_historical_metrics(request=req)
        rows = []
        for r in resp.results:
            m = r.keyword_metrics
            rows.append({"text": r.text,
                         "avg_monthly_searches": m.avg_monthly_searches,
                         "competition": E(m.competition),
                         "competition_index": m.competition_index,
                         "low_top_bid_usd": round(m.low_top_of_page_bid_micros / 1e6, 2)
                         if m.low_top_of_page_bid_micros else None,
                         "high_top_bid_usd": round(m.high_top_of_page_bid_micros / 1e6, 2)
                         if m.high_top_of_page_bid_micros else None,
                         "close_variants": list(r.close_variants)[:6]})
        res[label] = rows
        print(f"\n=== {label} ({len(rows)} rows) ===")
        print(f"  {'searches':>9} {'comp':>12} {'TOPlow':>8} {'TOPhigh':>8}  keyword")
        for x in sorted(rows, key=lambda y: -(y["avg_monthly_searches"] or 0)):
            print(f"  {x['avg_monthly_searches'] or 0:>9} {x['competition']:>12} "
                  f"{str(x['low_top_bid_usd']):>8} {str(x['high_top_bid_usd']):>8}  {x['text']}")
    except Exception as ex:
        res[label] = {"error": str(ex)[:400]}
        print(f"\n=== {label} FAILED: {str(ex)[:300]}")
    time.sleep(4)
out["planner"] = res

print("\n=== DEMAND NOTE ===")
print("  Synonyms share a single volume bucket in Keyword Planner. Summing raw rows")
print("  overstates real demand. Treat these as per-bucket ceilings, not additive totals.")
out["bucket_warning"] = ("synonyms share one volume bucket; do not sum rows to estimate "
                         "total demand")

p = SNAP / f"keyword-planner-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
