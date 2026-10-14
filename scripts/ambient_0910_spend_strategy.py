#!/usr/bin/env python3
"""Can Ambient spend $13,000/month at an acceptable cost per unique qualified lead?
Measured evidence only. No promise of any outcome."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
SETTLED = "2026-09-09"
MAXQ = {"AC Repair": 150.0, "HVAC Repair": 250.0, "HVAC Installation": 280.0,
        "HVAC Replacement": 280.0, "Gas Boiler Repair": 250.0}
UQL = {"AC Repair": 3, "HVAC Repair": 1, "HVAC Installation": 1,
       "HVAC Replacement": 0, "Gas Boiler Repair": 0}   # measured via WhatConverts GCLID join

print("=== 1. MEASURED COST PER UNIQUE QUALIFIED LEAD (2026-08-14 .. 2026-09-09) ===")
perf = {}
for r in q(c, f"SELECT campaign.id, metrics.impressions, metrics.clicks, metrics.cost_micros, "
              f"metrics.conversions, metrics.search_impression_share, "
              f"metrics.search_budget_lost_impression_share, "
              f"metrics.search_rank_lost_impression_share FROM campaign "
              f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' "
              f"AND '{SETTLED}'"):
    m = r.metrics
    k = NAME[str(r.campaign.id)]
    perf[k] = {"impr": m.impressions, "clicks": m.clicks,
               "cost": round(m.cost_micros / 1e6, 2), "records": round(m.conversions, 2),
               "is": round(m.search_impression_share * 100, 2),
               "lost_budget": round(m.search_budget_lost_impression_share * 100, 2),
               "lost_rank": round(m.search_rank_lost_impression_share * 100, 2),
               "uql": UQL[k]}
tot_cost = sum(v["cost"] for v in perf.values())
tot_uql = sum(v["uql"] for v in perf.values())
print(f"  {'campaign':<20}{'cost':>10}{'clicks':>8}{'records':>9}{'uniqQL':>8}{'CPQL':>11}"
      f"{'limit':>8}{'over by':>10}")
for k in ["AC Repair", "HVAC Repair", "HVAC Installation", "HVAC Replacement",
          "Gas Boiler Repair"]:
    v = perf[k]
    cpql = v["cost"] / v["uql"] if v["uql"] else None
    over = f"{cpql/MAXQ[k]:.1f}x" if cpql else "-"
    v["cpql"] = round(cpql, 2) if cpql else None
    print(f"  {k:<20}{v['cost']:>10.2f}{v['clicks']:>8}{v['records']:>9.0f}{v['uql']:>8}"
          f"{(f'{cpql:.2f}' if cpql else 'n/a'):>11}{MAXQ[k]:>8.0f}{over:>10}")
blended = tot_cost / tot_uql if tot_uql else None
print(f"  {'TOTAL':<20}{tot_cost:>10.2f}{sum(v['clicks'] for v in perf.values()):>8}"
      f"{sum(v['records'] for v in perf.values()):>9.0f}{tot_uql:>8}"
      f"{(f'{blended:.2f}' if blended else 'n/a'):>11}")
out["measured"] = perf
out["blended_cpql"] = round(blended, 2) if blended else None

print("\n=== 2. WHERE ARE THE LEADS ACTUALLY COMING FROM? ===")
wc = json.load(open(EVID / "2026-09-10-whatconverts-lead-analysis.json", encoding="utf-8"))
print(f"  total WhatConverts leads {wc['window'][0]}..{wc['window'][1]}: {wc['total_leads']}")
print(f"  carrying a Google Ads GCLID (i.e. paid search): {wc['rows_with_gclid']}")
print(f"  share of lead volume from paid search: "
      f"{100*wc['rows_with_gclid']/wc['total_leads']:.1f}%")
print(f"  lead_source mix: {wc['aggregate']['lead_source']}")
print("\n  -> the business IS generating leads. 91 of 99 came from Google Business Profile,")
print("     Local Services Ads and organic, at zero paid-search cost. Paid search bought 8.")
out["lead_source_reality"] = {"total": wc["total_leads"], "paid_search": wc["rows_with_gclid"],
                              "paid_share_pct": round(100*wc["rows_with_gclid"]/wc["total_leads"], 1),
                              "mix": wc["aggregate"]["lead_source"]}

print("\n=== 3. WHAT WOULD $13,000/MONTH BUY AT MEASURED EFFICIENCY? ===")
DAYS_OBS = 27  # 2026-08-14..2026-09-09 inclusive
monthly_obs = tot_cost / DAYS_OBS * 30.4
print(f"  observed spend {tot_cost:,.2f} over {DAYS_OBS} days = ${monthly_obs:,.2f}/month rate")
if blended:
    at13 = 13000 / blended
    print(f"  at the measured blended CPQL of ${blended:,.2f}, $13,000 buys "
          f"~{at13:.1f} unique qualified leads/month")
    need = 13000 / 250.0
    print(f"  to hit a ~$250 blended CPQL, $13,000 would need to buy ~{need:.0f} unique "
          f"qualified leads")
    print(f"  required efficiency gain: {blended/250.0:.1f}x")
    out["at_13k"] = {"leads_at_current_efficiency": round(at13, 1),
                     "leads_needed_for_250_cpql": round(need, 0),
                     "required_efficiency_gain_x": round(blended/250.0, 1)}

print("\n=== 4. IS $13,000 EVEN SPENDABLE ON THE CURRENT KEYWORD SET? ===")
kw = [r for r in q(c, f"SELECT ad_group_criterion.keyword.text FROM ad_group_criterion "
                      f"WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type='KEYWORD' "
                      f"AND ad_group_criterion.negative=FALSE "
                      f"AND ad_group_criterion.status='ENABLED'")]
print(f"  live positive keywords across all five campaigns: {len(kw)} "
      f"({len({r.ad_group_criterion.keyword.text for r in kw})} distinct texts)")
avg_is = sum(v["is"] for v in perf.values() if v["impr"]) / max(
    1, sum(1 for v in perf.values() if v["impr"]))
tot_impr = sum(v["impr"] for v in perf.values())
tot_clicks = sum(v["clicks"] for v in perf.values())
ctr = 100*tot_clicks/tot_impr if tot_impr else 0
cpc = tot_cost/tot_clicks if tot_clicks else 0
monthly_impr = tot_impr / DAYS_OBS * 30.4
print(f"  observed: {tot_impr} impressions in {DAYS_OBS} days = ~{monthly_impr:,.0f}/month")
print(f"  average Search impression share across the five: {avg_is:.1f}%")
if avg_is:
    total_avail = monthly_impr / (avg_is/100)
    max_clicks = total_avail * ctr/100
    max_spend = max_clicks * cpc
    print(f"  implied TOTAL available impressions at 100% IS: ~{total_avail:,.0f}/month")
    print(f"  at the observed {ctr:.2f}% CTR that is ~{max_clicks:,.0f} clicks/month")
    print(f"  at the observed ${cpc:.2f} CPC that is ~${max_spend:,.0f}/month MAXIMUM")
    print(f"  -> even at 100% impression share on today's 10 keywords, the ceiling is about "
          f"${max_spend:,.0f}, not $13,000")
    out["demand_ceiling"] = {"monthly_impressions": round(monthly_impr),
                             "avg_is_pct": round(avg_is, 1),
                             "total_available_impressions": round(total_avail),
                             "max_clicks": round(max_clicks), "observed_cpc": round(cpc, 2),
                             "max_monthly_spend_at_100pct_is": round(max_spend)}

print("\n=== 5. WHERE THE HEADROOM ACTUALLY IS ===")
print(f"  {'campaign':<20}{'IS':>7}{'lost RANK':>11}{'lost BUDGET':>13}   binding constraint")
for k, v in perf.items():
    b = "RANK" if v["lost_rank"] > v["lost_budget"] else (
        "BUDGET" if v["lost_budget"] > 0 else "neither")
    print(f"  {k:<20}{v['is']:>6.1f}%{v['lost_rank']:>10.1f}%{v['lost_budget']:>12.1f}%   {b}")
print("\n  Rank loss dominates on four of five campaigns. Rank is won with relevance and")
print("  landing-page experience, not with budget. Budget is only binding on HVAC")
print("  Installation, and its own CPQL is 10.6x over target.")
out["constraints"] = {k: {"is": v["is"], "lost_rank": v["lost_rank"],
                          "lost_budget": v["lost_budget"]} for k, v in perf.items()}

write(EVID / "2026-09-10-spend-strategy.json", out)
