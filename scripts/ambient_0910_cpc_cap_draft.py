#!/usr/bin/env python3
"""Gas Boiler Repair and HVAC Replacement are still on UNCAPPED Maximize Clicks.
Draft the ceilings that were never applied to them. VALIDATE-ONLY - creates nothing."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

c = client()
print("=== VERIFIED CURRENT STATE OF THE TWO UNCAPPED CAMPAIGNS ===")
cur = {}
for r in q(c, f"SELECT campaign.id, campaign.name, campaign.status, "
              f"campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros, "
              f"campaign_budget.amount_micros FROM campaign WHERE campaign.id IN ({IN5})"):
    cur[str(r.campaign.id)] = {
        "name": r.campaign.name, "status": E(r.campaign.status),
        "strategy": E(r.campaign.bidding_strategy_type),
        "ceiling_micros": r.campaign.target_spend.cpc_bid_ceiling_micros,
        "budget": r.campaign_budget.amount_micros/1e6}
for cid in ["24132507744", "24132507753"]:
    v = cur[cid]
    print(f"  {NAME[cid]:<20}{v['status']:<9}{v['strategy']:<16}"
          f"budget ${v['budget']:>7.2f}/day  ceiling "
          f"{('$%.2f' % (v['ceiling_micros']/1e6)) if v['ceiling_micros'] else 'NONE'}")
    assert v["ceiling_micros"] == 0, "already capped - do not draft"
    assert v["strategy"] == "TARGET_SPEND", "not Maximize Clicks - different field"

TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "AC Repair",
          "related_services": ["HVAC Repair", "HVAC Installation", "HVAC Replacement",
                               "Gas Boiler Repair"]}
ops = [
 {"operation": "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING", "resource": "campaign",
  "resource_id": "24132507744", "resource_name": "Gas Boiler Repair",
  "campaign_name": cur["24132507744"]["name"],
  "current_state": "target_spend.cpc_bid_ceiling_micros UNSET - uncapped Maximize Clicks",
  "proposed_state": "target_spend.cpc_bid_ceiling_micros = 25000000 ($25.00)",
  "field_mask": ["target_spend.cpc_bid_ceiling_micros"],
  "reason": "This campaign was left uncapped when AC Repair, HVAC Repair and HVAC Installation "
            "received ceilings on 2026-09-04 16:56. $25.00 matches HVAC Repair, whose maximum "
            "cost per unique qualified lead is the same $250. The campaign has taken 0 valid "
            "clicks and 42 invalid clicks since 2026-08-14 on a $5.00/day budget, so the "
            "ceiling costs no measured delivery today and bounds the price if it starts serving.",
  "rollback": "clear target_spend.cpc_bid_ceiling_micros back to unset, the verified "
              "pre-change value",
  "risk": "LOW - reversible setting change on a campaign with zero valid clicks in 27 days",
  "unrelated_resource_assertion":
      "bidding_strategy_type stays TARGET_SPEND; campaign_budget.amount_micros stays 5000000; "
      "AC Repair 25000000, HVAC Repair 25000000 and HVAC Installation 30000000 unchanged"},
 {"operation": "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING", "resource": "campaign",
  "resource_id": "24132507753", "resource_name": "HVAC Replacement",
  "campaign_name": cur["24132507753"]["name"],
  "current_state": "target_spend.cpc_bid_ceiling_micros UNSET - uncapped Maximize Clicks",
  "proposed_state": "target_spend.cpc_bid_ceiling_micros = 30000000 ($30.00)",
  "field_mask": ["target_spend.cpc_bid_ceiling_micros"],
  "reason": "Also left uncapped on 2026-09-04. Uncapped, it paid $30.50 per valid click "
            "(5 valid clicks, 82 invalid, $152.52) and produced 0 unique qualified leads. "
            "$30.00 matches HVAC Installation, which carries the same $280 maximum cost per "
            "unique qualified lead.",
  "rollback": "clear target_spend.cpc_bid_ceiling_micros back to unset, the verified "
              "pre-change value",
  "risk": "LOW - reversible setting change; $30.00 is above the $30.50 observed average only "
          "by rounding, so measured delivery loss is expected to be small but is NOT zero",
  "unrelated_resource_assertion":
      "bidding_strategy_type stays TARGET_SPEND; campaign_budget.amount_micros stays 20000000; "
      "AC Repair 25000000, HVAC Repair 25000000 and HVAC Installation 30000000 unchanged"}]

plan = {"plan_name": "AMB-0910-CPC-CAP-1", "approval_class": "reversible-setting-change",
        "generated_local": datetime.datetime.now(TZ).isoformat(), "target": TARGET,
        "summary": "Apply the max-CPC ceilings that Gas Boiler Repair and HVAC Replacement "
                   "never received. 2 operations. No budget, keyword, negative, geo or ad "
                   "is touched.",
        "object_count": 2, "partial_failure": False, "atomic": True, "operations": ops,
        "notes": {
          "why_now": "change_event shows ceilings were applied to three of five campaigns on "
                     "2026-09-04 16:56 (GOOGLE_ADS_WEB_CLIENT, access@greenmarketingfl.com) "
                     "from an empty old_resource. These two were missed. They are the only "
                     "remaining uncapped Maximize Clicks campaigns in the account.",
          "measured_effect_of_the_existing_ceilings":
              "Cost per valid click across the five fell from $46.66 (2026-08-14..2026-09-03, "
              "uncapped) to $25.93 (2026-09-05..2026-09-09, capped). Daily spend fell from "
              "$382.15 to $20.74. The capped window is 5 settled days and 4 valid clicks, "
              "which is directionally consistent with the ceiling binding but far too short "
              "to call the effect established.",
          "tension_with_the_spend_goal":
              "This lowers, not raises, the ceiling on spend. Under the stated priority order "
              "qualified-lead economics outranks spend utilization, so this is the correct "
              "trade. It is stated explicitly rather than buried.",
          "not_a_forecast": "No lead, cost or ranking outcome is promised. These are bounds "
                            "on price per click, not predictions of volume.",
          "requires_new_approval": True}}
plan["fingerprint"] = approval_code({"target": TARGET, "plan": plan["plan_name"],
                                     "operations": ops})
(CLIENT_DIR / "plans" / f"{plan['plan_name']}.json").write_text(
    json.dumps(plan, indent=1, default=str), encoding="utf-8")
print(f"\n=== {plan['plan_name']} ops={plan['object_count']} "
      f"fingerprint={plan['fingerprint']} ===")
for o in ops:
    print(f"  {o['resource_name']:<20}{o['current_state']}")
    print(f"  {'':<20}-> {o['proposed_state']}")
print(f"WROTE clients/ambient-cooling-heating/plans/{plan['plan_name']}.json")
