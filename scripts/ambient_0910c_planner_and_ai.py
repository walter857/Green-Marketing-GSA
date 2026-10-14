#!/usr/bin/env python3
"""Keyword Planner historical volume + top-of-page ranges for the exact 75 Maryland
targets and the exact BOFU keyword set, plus a recorded attempt at Auction Insights
through the API. Market context only - these are NOT recommended bids."""
from __future__ import annotations
import sys, json, time, datetime
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
identity_gate(c, verbose=False)
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}

print("=== A. THE EXACT GEO TARGET SET ON THE FIVE ===")
geo = {}
for r in q(c, f"SELECT campaign.id, campaign_criterion.location.geo_target_constant, "
              f"campaign_criterion.negative, campaign_criterion.status "
              f"FROM campaign_criterion WHERE campaign.id IN ({IN5}) "
              f"AND campaign_criterion.type = 'LOCATION'"):
    g = r.campaign_criterion.location.geo_target_constant
    geo.setdefault(NAME[str(r.campaign.id)], []).append(
        (g, r.campaign_criterion.negative, E(r.campaign_criterion.status)))
for k, v in geo.items():
    neg = sum(1 for x in v if x[1])
    print(f"  {k:<20}{len(v):>4} location criteria, {neg} negative, "
          f"{len({x[0] for x in v})} distinct")
allgeo = sorted({x[0] for v in geo.values() for x in v if not x[1]})
print(f"  distinct POSITIVE geo constants across the five: {len(allgeo)}")
out["geo_targets"] = allgeo
same = all(sorted({x[0] for x in v if not x[1]}) == allgeo for v in geo.values())
print(f"  all five campaigns share an identical positive geo set: {same}")

print("\n=== B. THE EXACT BOFU KEYWORD SET ===")
kws = []
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group.status, "
              f"ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type "
              f"FROM ad_group_criterion WHERE campaign.id IN ({IN5}) "
              f"AND ad_group_criterion.type='KEYWORD' "
              f"AND ad_group_criterion.negative=FALSE "
              f"AND ad_group_criterion.status='ENABLED'"):
    if E(r.ad_group.status) != "ENABLED":
        continue
    kws.append((NAME[str(r.campaign.id)], r.ad_group_criterion.keyword.text,
                E(r.ad_group_criterion.keyword.match_type)))
seeds = sorted({k[1] for k in kws})
print(f"  serving positive keywords: {len(kws)}   distinct texts: {len(seeds)}")
for s in seeds:
    print(f"    {s}")
out["seed_keywords"] = seeds

print("\n=== C. KEYWORD PLANNER HISTORICAL METRICS ===")
print("  (max 10 geo targets per call; own quota that 429s fast - batching)")
svc = c.get_service("KeywordPlanIdeaService")
BATCH = [allgeo[i:i + 10] for i in range(0, len(allgeo), 10)]
print(f"  {len(allgeo)} geo constants -> {len(BATCH)} batches of <=10")
agg = {}
errors = []
for i, batch in enumerate(BATCH, 1):
    try:
        req = c.get_type("GenerateKeywordHistoricalMetricsRequest")
        req.customer_id = CID
        req.keywords.extend(seeds)
        req.geo_target_constants.extend(batch)
        req.language = "languageConstants/1000"
        req.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        resp = svc.generate_keyword_historical_metrics(request=req)
        for res in resp.results:
            m = res.keyword_metrics
            a = agg.setdefault(res.text, {"vol": 0, "low": [], "high": [], "comp": [],
                                          "batches": 0})
            a["vol"] += m.avg_monthly_searches or 0
            a["batches"] += 1
            if m.low_top_of_page_bid_micros:
                a["low"].append(m.low_top_of_page_bid_micros / 1e6)
            if m.high_top_of_page_bid_micros:
                a["high"].append(m.high_top_of_page_bid_micros / 1e6)
            if m.competition:
                a["comp"].append(E(m.competition))
        print(f"    batch {i}/{len(BATCH)}: {len(resp.results)} rows")
        time.sleep(1.2)
    except Exception as e:
        msg = f"{type(e).__name__}: {str(e)[:150]}"
        errors.append({"batch": i, "error": msg})
        print(f"    batch {i}/{len(BATCH)}: {msg}")
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            print("    quota exhausted - stopping planner sweep")
            break

if agg:
    print(f"\n  {'keyword':<32}{'sum vol':>9}{'batches':>9}{'TOPlow':>9}{'TOPhigh':>9}"
          f"{'competition':>14}")
    for k, v in sorted(agg.items(), key=lambda z: -z[1]["vol"]):
        lo = min(v["low"]) if v["low"] else None
        hi = max(v["high"]) if v["high"] else None
        comp = Counter(v["comp"]).most_common(1)[0][0] if v["comp"] else "-"
        print(f"  {k:<32}{v['vol']:>9}{v['batches']:>9}"
              f"{(f'${lo:.2f}' if lo else '-'):>9}{(f'${hi:.2f}' if hi else '-'):>9}"
              f"{comp:>14}")
    print("\n  WARNING: 'sum vol' adds the same keyword across overlapping geo batches and")
    print("  therefore OVERSTATES real demand. Synonyms also share one volume bucket.")
    print("  Treat TOPlow/TOPhigh as market context only. They are NOT recommended bids.")
out["planner"] = {k: {"summed_volume_DO_NOT_USE_AS_DEMAND": v["vol"], "batches": v["batches"],
                      "top_of_page_low": min(v["low"]) if v["low"] else None,
                      "top_of_page_high": max(v["high"]) if v["high"] else None,
                      "competition": Counter(v["comp"]).most_common(1)[0][0] if v["comp"] else None}
                  for k, v in agg.items()}
out["planner_errors"] = errors

print("\n\n=== D. AUCTION INSIGHTS THROUGH THE API ===")
for res, sel in [("campaign_search_term_insight", "campaign_search_term_insight.id"),
                 ("auction_insight", "auction_insight.domain")]:
    try:
        rows = q(c, f"SELECT {sel} FROM {res} LIMIT 1")
        print(f"  {res}: returned {len(rows)} rows")
    except Exception as e:
        code = "PERMISSION_DENIED" if "PERMISSION_DENIED" in str(e) else (
            "UNRECOGNIZED" if "not recognized" in str(e).lower()
            or "unrecognized" in str(e).lower() else type(e).__name__)
        print(f"  {res}: {code}")
        out.setdefault("auction_insights_api", {})[res] = code
print("  Auction Insights is not exposed to this developer token. The August 1-31 export")
print("  must come from the authenticated Google Ads UI.")

write(EVID / "2026-09-10c-planner-and-auction-insights.json", out)
