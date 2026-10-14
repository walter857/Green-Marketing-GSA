#!/usr/bin/env python3
"""September pacing + lead forecast scenarios, and the post-audit unchanged-resource proof."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}
model = json.load(open(EVID / "2026-09-09-cpc-model.json", encoding="utf-8"))

print("=== SEPTEMBER PACING (settled 2026-09-01..2026-09-08) ===")
sept = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                            "conversions": 0.0, "all_conversions": 0.0})
for r in q(c, f"SELECT campaign.id, {METRICS} FROM campaign WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-09-01' AND '2026-09-08'"):
    k = NAME[str(r.campaign.id)]
    for f in ("impressions", "clicks", "conversions", "all_conversions"):
        sept[k][f] += getattr(r.metrics, f)
    sept[k]["cost"] += r.metrics.cost_micros / 1e6
spent = sum(v["cost"] for v in sept.values())
print(f"  September MTD settled spend (8 days): ${spent:,.2f}")
for k, v in sorted(sept.items(), key=lambda kv: -kv[1]["cost"]):
    print(f"    {k:<20} ${v['cost']:>9.2f}  clicks={v['clicks']:<4} conv={v['conversions']:.0f}")
print(f"  monthly maximum: $13,000.00   remaining: ${13000-spent:,.2f}")
print(f"  days remaining in September (09-09..09-30 inclusive): 22")
print(f"  headroom per remaining day: ${(13000-spent)/22:,.2f}")

pre_ceiling_daily = 8025.18 / 21   # 2026-08-14..09-03
post_ceiling_daily = 45.08 / 4     # 2026-09-05..09-08
print(f"\n  observed daily run rate BEFORE the 09-04 ceiling: ${pre_ceiling_daily:,.2f}/day")
print(f"  observed daily run rate AFTER  the 09-04 ceiling: ${post_ceiling_daily:,.2f}/day")

print("\n=== MONTH-END SPEND SCENARIOS FOR SEPTEMBER ===")
scen = {}
S = [
    ("A. Do nothing (ceilings stay as the owner set them)", post_ceiling_daily, 0.0,
     "AC Repair, HVAC Installation, HVAC Replacement and Gas Boiler have taken zero clicks "
     "since 2026-09-05. Only HVAC Repair squeezes an occasional click under $25."),
    ("B. AMB-0909-CPC-1 only (Installation $65, Repair $60)", 138.78 + 90.80 * 0.52, None,
     "HVAC Installation returns to roughly its pre-ceiling $138.78/day (its ceiling stops "
     "binding at $65) and HVAC Repair returns to about 52% of its $90.80/day, the modelled "
     "click survival at a $60 cap. AC Repair stays dark by design."),
    ("C. B + AC Repair ceiling raised to $130", 138.78 + 90.80 * 0.52 + 145.31 * 0.60, None,
     "Adds AC Repair back at the modelled 60% click survival of its $145.31/day pre-ceiling "
     "rate. NOT RECOMMENDED: modelled CPA at that cap is $281.19 against a $150 max CPQL."),
    ("D. Pre-ceiling behaviour fully restored (no caps at all)", pre_ceiling_daily, None,
     "The 2026-08-14..09-03 run rate. Reference point only."),
]
for label, daily, _x, note in S:
    proj = spent + daily * 22
    scen[label] = {"daily_rate": round(daily, 2), "projected_month_end": round(proj, 2),
                   "vs_cap": round(13000 - proj, 2), "note": note}
    flag = "WITHIN CAP" if proj <= 13000 else "*** OVER CAP ***"
    print(f"\n  {label}")
    print(f"     modelled daily rate ${daily:,.2f}  ->  September month-end ${proj:,.2f}  "
          f"({flag}, ${13000-proj:,.2f} vs cap)")
    print(f"     {note}")
out["september_scenarios"] = scen
out["september_mtd_settled"] = {k: {kk: round(vv, 2) for kk, vv in v.items()}
                                for k, v in sept.items()}

print("\n=== LEAD FORECAST (raw primary conversions; QUALIFIED IS UNKNOWN) ===")
print("  Raw primary CVR observed 2026-08-14..09-08, per campaign:")
econ = model["economic_bands"]
for k, v in econ.items():
    print(f"    {k:<20} rawCVR={v['raw_primary_cvr_pct']:>6.2f}%  observedCPC=${v['observed_cpc']}")
print("\n  Scenario B (recommended) monthly lead model for the remaining 22 days:")
fc = {}
for camp, daily, cvr, cpc in (("HVAC Installation", 138.78, 4.84, 27.54),
                              ("HVAC Repair", 90.80 * 0.52, 16.00, 36.47)):
    spend22 = daily * 22
    clicks = spend22 / cpc
    leads = clicks * cvr / 100
    fc[camp] = {"spend": round(spend22, 2), "clicks": round(clicks, 1),
                "raw_primary_leads": round(leads, 1),
                "raw_cpa": round(spend22 / leads, 2) if leads else None}
    print(f"    {camp:<20} spend=${spend22:>8,.2f}  clicks~{clicks:>5.0f}  "
          f"raw leads~{leads:>4.1f}  raw CPA ${spend22/leads if leads else 0:,.2f}")
tot_spend = sum(v["spend"] for v in fc.values())
tot_leads = sum(v["raw_primary_leads"] for v in fc.values())
print(f"    {'TOTAL':<20} spend=${tot_spend:>8,.2f}  raw leads~{tot_leads:.1f}  "
      f"blended raw CPA ${tot_spend/tot_leads:,.2f}")
print("\n  CONFIDENCE: LOW-TO-MODERATE. HVAC Installation's 4.84% raw CVR is contaminated by")
print("  the 'hvac installers' keyword (53 clicks, 0 conversions) that was removed 2026-08-29.")
print("  Using only the post-swap window (9 clicks, 3 conversions, 33.3% CVR) the same spend")
print(f"  would model ~{(138.78*22/47.29)*0.333:.0f} leads - a 7x spread. The sample is 9 clicks, so neither")
print("  end of that range is reliable. Qualified-lead rate is UNKNOWN: WHATCONVERTS_API_TOKEN")
print("  is empty, so no CPQL, sold-job rate, revenue or gross profit can be stated.")
out["lead_forecast_scenario_B"] = fc

print("\n=== POST-AUDIT UNCHANGED-RESOURCE PROOF ===")
proof = {}
proof["campaign_count_non_removed"] = len(q(c, "SELECT campaign.id FROM campaign "
                                               "WHERE campaign.status != 'REMOVED'"))
proof["enabled_campaigns"] = len(q(c, "SELECT campaign.id FROM campaign "
                                      "WHERE campaign.status = 'ENABLED'"))
proof["campaign_negatives_enabled_on_five"] = len(q(
    c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'KEYWORD' "
       f"AND campaign_criterion.negative = TRUE AND campaign_criterion.status = 'ENABLED'"))
proof["geo_targets_on_five"] = len(q(
    c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'LOCATION'"))
proof["ad_schedules_on_five"] = len(q(
    c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'AD_SCHEDULE'"))
proof["ip_blocks_account"] = len(q(
    c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
       "WHERE campaign_criterion.type = 'IP_BLOCK'"))
proof["shared_sets"] = len(q(c, "SELECT shared_set.id FROM shared_set"))
proof["conversion_actions_non_removed"] = len(q(
    c, "SELECT conversion_action.id FROM conversion_action "
       "WHERE conversion_action.status != 'REMOVED'"))
row = q(c, "SELECT customer.descriptive_name, customer.tracking_url_template FROM customer")[0]
proof["descriptive_name"] = row.customer.descriptive_name
proof["tracking_url_template_present"] = bool(row.customer.tracking_url_template)
proof["tracking_url_template_is_clickcease"] = "clickcease" in row.customer.tracking_url_template.lower()
proof["manager_links"] = {x.customer_manager_link.manager_customer.split("/")[-1]:
                          E(x.customer_manager_link.status) for x in
                          q(c, "SELECT customer_manager_link.manager_customer, "
                               "customer_manager_link.status FROM customer_manager_link")}
buds = {str(r.campaign_budget.id): round(r.campaign_budget.amount_micros / 1e6, 2)
        for r in q(c, "SELECT campaign_budget.id, campaign_budget.amount_micros "
                      "FROM campaign_budget WHERE campaign_budget.status = 'ENABLED'")}
proof["five_budgets"] = {b: buds.get(b) for b in ["15787409435", "15787409438", "15787409441",
                                                  "15787409444", "15787409447"]}
proof["checked_local"] = datetime.datetime.now(TZ).isoformat()
proof["read_only_run"] = True
proof["mutations_executed"] = 0
for k, v in proof.items():
    print(f"  {k}: {v}")
out["unchanged_proof"] = proof

write(EVID / "2026-09-09-pacing-and-unchanged-proof.json", out)
