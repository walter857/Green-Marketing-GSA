#!/usr/bin/env python3
"""Ambient | 2026-09-18 | Build the two correction plans. LOCAL DRAFT ONLY, no writes.

  AMB-0918-BUDGET-1  bring enabled daily budgets under the permanent ceiling
  AMB-0918-CONV-1    one real lead = exactly one Primary bidding conversion
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

STAMP = "2026-09-18"
CEILING_DAILY = 328.94          # permanent account ceiling, $10,000 / 30.4
NEW_HEATING_DAILY = 90.00       # $55 Furnace Repair + $35 Mini Split Installation
MAX_EXISTING = round(CEILING_DAILY - NEW_HEATING_DAILY, 2)   # 238.94

# ---------------------------------------------------------------- budget plan
# Evidence (settled): August 2026 and 1-16 September 2026, read 2026-09-18.
#   AC Repair          Aug $2,550.59 / 24 clk / 4 conv  CPA $637.65  CPC $106.27
#                      Sep $534.28 /  5 clk / 1 conv  CPA $534.28  CPC $106.86
#   HVAC Installation  Aug $2,474.53 /103 clk / 0 conv (10 all)     CPC $24.02
#                      Sep $727.04 / 20 clk / 3 conv  CPA $242.35   CPC $36.35
#   HVAC Repair        Aug $1,665.16 / 23 clk / 6 conv  CPA $277.53 CPC $72.40
#                      Sep $286.78 /  6 clk / 0 conv (7 all)        CPC $47.80
#   HVAC Replacement   Aug $152.52 / 5 clk / 0 conv;  Sep $0.00
#   Gas Boiler Repair  Aug $0.00;  Sep $0.00
BUDGETS = [
    {"campaign": "Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08",
     "campaign_id": "24132507747", "budget_id": "15787409441",
     "from": 176.15, "to": 95.00,
     "rationale": "Best conversion volume in the account and the only campaign whose CPA "
                  "improved into September ($242.35). Actual settled September delivery is "
                  "$45.44/day, so $95.00 still leaves roughly 2x headroom over real spend. "
                  "Largest single reduction in dollars without touching delivery."},
    {"campaign": "Search | NonBrand | AC Repair | Central MD | BOFU | 2026-08",
     "campaign_id": "24132507741", "budget_id": "15787409435",
     "from": 141.45, "to": 45.00,
     "rationale": "Deepest cut, on three independent signals: worst CPA in the account "
                  "($637.65 August, $534.28 September), the most expensive clicks by far "
                  "($106+ CPC in both windows), and Central Maryland cooling demand falls "
                  "through the autumn. NOT eliminated - it keeps enough budget for roughly "
                  "one click per day at the observed clearing price."},
    {"campaign": "Search | NonBrand | HVAC Repair | Central MD | BOFU | 2026-08",
     "campaign_id": "24132507750", "budget_id": "15787409444",
     "from": 78.95, "to": 70.00,
     "rationale": "Protected almost intact. Best CPA of any campaign ($277.53 August on 6 "
                  "conversions) and year-round repair demand. Actual September delivery is "
                  "$17.92/day, so $70.00 is already generous; this is the smallest "
                  "proportional cut on purpose."},
    {"campaign": "Search | NonBrand | HVAC Replacement | Central MD | BOFU | 2026-08",
     "campaign_id": "24132507753", "budget_id": "15787409447",
     "from": 20.00, "to": 15.00,
     "rationale": "Zero September delivery and zero conversions across both windows. Small "
                  "cut only, because replacement jobs carry high ticket value and the "
                  "campaign should stay reachable when demand returns."},
    {"campaign": "Search | NonBrand | Gas Boiler Repair | Central MD | BOFU | 2026-08",
     "campaign_id": "24132507744", "budget_id": "15787409438",
     "from": 5.00, "to": 12.00,
     "rationale": "The only INCREASE. It is the one enabled heating-adjacent campaign and "
                  "Maryland boiler demand starts now. $5.00/day cannot buy a single click "
                  "at this account's prices, which is why it has spent $0.00 all season."},
]
new_total = round(sum(b["to"] for b in BUDGETS), 2)
old_total = round(sum(b["from"] for b in BUDGETS), 2)
assert new_total <= MAX_EXISTING, f"{new_total} over {MAX_EXISTING}"

budget_plan = {
    "plan_name": "AMB-0918-BUDGET-1",
    "approval_class": "update-existing-budgets",
    "customer_id": CID,
    "exact_account_name": EXACT_NAME,
    "never_write_to_mcc": GM_MANAGER,
    "built_local": STAMP,
    "purpose": "Bring combined ENABLED daily budgets under the permanent account ceiling "
               "so the two paused heating campaigns can later be enabled without breaching "
               "it.",
    "evidence_windows": {"august_settled": "2026-08-01..2026-08-31",
                         "september_settled": "2026-09-01..2026-09-16",
                         "read_on": STAMP},
    "math": {
        "permanent_monthly_cap_usd": 10000.00,
        "days_per_month": 30.4,
        "permanent_daily_ceiling_usd": CEILING_DAILY,
        "new_heating_daily_usd": NEW_HEATING_DAILY,
        "max_existing_enabled_daily_usd": MAX_EXISTING,
        "current_enabled_daily_usd": old_total,
        "proposed_enabled_daily_usd": new_total,
        "reduction_usd_per_day": round(old_total - new_total, 2),
        "required_reduction_usd_per_day": round(old_total - MAX_EXISTING, 2),
        "combined_after_heating_enabled_usd": round(new_total + NEW_HEATING_DAILY, 2),
        "combined_monthly_equivalent_usd": round((new_total + NEW_HEATING_DAILY) * 30.4, 2),
        "headroom_under_daily_ceiling_usd": round(
            CEILING_DAILY - (new_total + NEW_HEATING_DAILY), 2),
    },
    "budgets": BUDGETS,
    "operations": [
        {"op": "UPDATE_CAMPAIGN_BUDGET_AMOUNT", "budget_id": b["budget_id"],
         "campaign": b["campaign"], "from_usd": b["from"], "to_usd": b["to"],
         "field_mask": "amount_micros"}
        for b in BUDGETS
    ],
    "does_not_touch": ["campaign status", "bidding strategy", "CPC ceilings", "keywords",
                       "ads", "assets", "conversion actions", "the two paused heating "
                       "campaigns", "budget sharing", "delivery method"],
    "honest_limitation": "Actual combined settled delivery across the five enabled "
                         "campaigns is about $96.76/day, far below both the current and the "
                         "proposed budgets. These are CEILING changes. They make the cap "
                         "compliant; they should not be expected to reduce actual spend, "
                         "and no CPL, CPQL or profitability improvement is claimed.",
    "reversible": "Every change is a single amount_micros write; the prior values are "
                  "recorded in this plan and can be restored exactly.",
}
budget_plan["operation_count"] = len(budget_plan["operations"])
budget_plan["fingerprint"] = approval_code(budget_plan)

# ------------------------------------------------------------ conversion plan
# Read 2026-09-18. The customer_conversion_goal layer already marks every GOOGLE_HOSTED
# category NON-BIDDABLE, which is why those actions report all_conversions > 0 but
# conversions = 0. The only genuine double-counts are on biddable goals.
CONV = [
    {"id": "7643656486", "name": "WC Lead", "category": "CONTACT", "origin": "WEBSITE",
     "type": "UPLOAD_CLICKS", "was": "PRIMARY", "becomes": "SECONDARY",
     "volume_90d_all": 8.0, "volume_90d_conversions": 4.0,
     "reason": "DOUBLE COUNT. A website form submission is already counted by 6885463625 "
               "on the biddable SUBMIT_LEAD_FORM/WEBSITE goal. This WhatConverts upload "
               "re-reports the same submission on the biddable CONTACT/WEBSITE goal, so one "
               "real lead produces two Primary conversions."},
    {"id": "7643656075", "name": "WC Calls", "category": "CONTACT",
     "origin": "CALL_FROM_ADS", "type": "UPLOAD_CALLS", "was": "PRIMARY",
     "becomes": "SECONDARY", "volume_90d_all": 0.0, "volume_90d_conversions": 0.0,
     "reason": "DOUBLE COUNT. A call placed from an ad is already counted by 1068114183 on "
               "the biddable PHONE_CALL_LEAD/CALL_FROM_ADS goal. This WhatConverts upload "
               "re-reports the same call on the biddable CONTACT/CALL_FROM_ADS goal."},
]
REMAIN_BIDDABLE = [
    {"id": "6885463625", "name": "Ambient Cooling - LP -Submit Lead Forms",
     "goal": "SUBMIT_LEAD_FORM / WEBSITE", "type": "WEBPAGE",
     "covers": "a form submitted on the website"},
    {"id": "1068114183", "name": "Calls from ads", "goal": "PHONE_CALL_LEAD / CALL_FROM_ADS",
     "type": "AD_CALL", "covers": "a call placed from the ad's call asset"},
    {"id": "6885576934", "name": "Ambient Cooling - Lp - Phone call leads",
     "goal": "PHONE_CALL_LEAD / WEBSITE", "type": "WEBSITE_CALL",
     "covers": "a call placed from a number on the website"},
]
conv_plan = {
    "plan_name": "AMB-0918-CONV-1",
    "approval_class": "update-conversion-action-primary-flag",
    "customer_id": CID,
    "exact_account_name": EXACT_NAME,
    "never_write_to_mcc": GM_MANAGER,
    "built_local": STAMP,
    "required_outcome": "One real lead = exactly one Primary bidding conversion.",
    "nothing_is_deleted": True,
    "historical_data_preserved": "Only primary_for_goal changes. Status stays ENABLED, no "
                                 "action is removed, and past conversions are not restated.",
    "page_view_x2_cannot_be_resolved_by_api": {
        "finding": "All five Google Business Profile (GOOGLE_HOSTED) conversion actions "
                   "are system-managed and reject every mutate with "
                   "mutate_error: MUTATE_NOT_ALLOWED. Verified individually by validate_only "
                   "on 6954620053, 6640721230, 6641739327, 6642551975 and 6642544931 - all "
                   "five REJECTED, while the two WhatConverts upload actions VALIDATED_OK.",
        "affected": ["PAGE_VIEW x2 (6641739327 Website visits, 6954620053 Menu views)"],
        "why_it_is_not_a_defect": "Both sit on the PAGE_VIEW/GOOGLE_HOSTED customer "
                                  "conversion goal, which is already NON-BIDDABLE. They "
                                  "cannot influence Smart Bidding and report conversions = 0. "
                                  "The duplication is a reporting artefact with no bidding "
                                  "effect, and Google does not expose a way to change it.",
        "if_the_owner_wants_it_gone": "It can only be changed in the Google Ads UI under "
                                      "Goals, or by unlinking the Google Business Profile. "
                                      "That is a separate decision and is NOT part of this "
                                      "plan.",
    },
    "goal_layer_finding": {
        "customer_conversion_goal_biddable": ["PHONE_CALL_LEAD/WEBSITE",
                                              "SUBMIT_LEAD_FORM/WEBSITE",
                                              "CONTACT/WEBSITE",
                                              "PHONE_CALL_LEAD/CALL_FROM_ADS",
                                              "CONTACT/CALL_FROM_ADS"],
        "customer_conversion_goal_not_biddable": ["PAGE_VIEW/GOOGLE_HOSTED",
                                                  "GET_DIRECTIONS/GOOGLE_HOSTED",
                                                  "CONTACT/GOOGLE_HOSTED",
                                                  "ENGAGEMENT/GOOGLE_HOSTED"],
        "why_it_matters": "The five Google Business Profile local-action Primaries sit on "
                          "NON-BIDDABLE goals, so they never influenced bidding. Their "
                          "duplication was cosmetic. The real defect was two WhatConverts "
                          "upload actions sharing biddable goals with the native tags.",
    },
    "changes": CONV,
    "primary_bidding_conversions_after": REMAIN_BIDDABLE,
    "non_biddable_primaries_left_alone": [
        {"id": "6640721230", "name": "Clicks to call", "goal": "CONTACT / GOOGLE_HOSTED",
         "note": "immutable via API; non-biddable; becomes the only CONTACT Primary"},
        {"id": "6641739327", "name": "Local actions - Website visits",
         "goal": "PAGE_VIEW / GOOGLE_HOSTED", "note": "immutable via API; non-biddable"},
        {"id": "6954620053", "name": "Local actions - Menu views",
         "goal": "PAGE_VIEW / GOOGLE_HOSTED",
         "note": "immutable via API; non-biddable; 0 events in 90 days"},
        {"id": "6642551975", "name": "Local actions - Other engagements",
         "goal": "ENGAGEMENT / GOOGLE_HOSTED"},
        {"id": "6642544931", "name": "Local actions - Directions",
         "goal": "GET_DIRECTIONS / GOOGLE_HOSTED"},
    ],
    "deliberate_deviation": {
        "item": "PHONE_CALL_LEAD keeps two Primary actions, not one.",
        "why": "1068114183 (AD_CALL, origin CALL_FROM_ADS) and 6885576934 (WEBSITE_CALL, "
               "origin WEBSITE) cannot both fire for the same interaction: a caller who "
               "taps the ad's call asset never reaches the website, and a caller who dials "
               "a number on the page did not use the ad's call asset. They are two distinct "
               "lead events on two distinct biddable goals. Collapsing them to one would "
               "stop counting a real lead type. The binding requirement - one real lead "
               "equals exactly one Primary bidding conversion - is fully satisfied.",
    },
    "operations": [
        {"op": "SET_CONVERSION_ACTION_SECONDARY", "conversion_action_id": ch["id"],
         "name": ch["name"], "from": "primary_for_goal=true",
         "to": "primary_for_goal=false", "field_mask": "primary_for_goal"}
        for ch in CONV
    ],
    "counts": {"enabled_primary_before": 10, "enabled_primary_after": 8,
               "biddable_primary_before": 5, "biddable_primary_after": 3,
               "contact_primary_before": 3, "contact_primary_after": 1,
               "phone_call_lead_primary": 2,
               "page_view_primary_unchanged_non_biddable": 2},
    "reversible": "Each change is a single primary_for_goal boolean and can be set back.",
}
conv_plan["operation_count"] = len(conv_plan["operations"])
conv_plan["fingerprint"] = approval_code(conv_plan)

PLANS.mkdir(parents=True, exist_ok=True)
for p in (budget_plan, conv_plan):
    f = PLANS / f"{p['plan_name']}.json"
    f.write_text(json.dumps(p, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {f}")

print(f"\n=== AMB-0918-BUDGET-1 ===")
for b in BUDGETS:
    print(f"  {b['campaign'][-34:]:34s} ${b['from']:7.2f} -> ${b['to']:7.2f}  "
          f"({b['to'] - b['from']:+7.2f})")
m = budget_plan["math"]
print(f"  enabled daily  ${m['current_enabled_daily_usd']:.2f} -> "
      f"${m['proposed_enabled_daily_usd']:.2f}  (cut ${m['reduction_usd_per_day']:.2f}, "
      f"required >= ${m['required_reduction_usd_per_day']:.2f})")
print(f"  + heating ${NEW_HEATING_DAILY:.2f} = ${m['combined_after_heating_enabled_usd']:.2f}"
      f"/day = ${m['combined_monthly_equivalent_usd']:,.2f}/month "
      f"(ceiling ${CEILING_DAILY}/day, headroom ${m['headroom_under_daily_ceiling_usd']:.2f})")
print(f"\n=== AMB-0918-CONV-1 ===")
for ch in CONV:
    print(f"  {ch['id']}  {ch['name'][:34]:34s} {ch['category']}/{ch['origin']}  "
          f"PRIMARY -> SECONDARY")
print("  PAGE_VIEW x2 left as-is: both GOOGLE_HOSTED actions are immutable via API and")
print("  already sit on a NON-BIDDABLE goal, so they cannot affect bidding.")
print("  biddable Primary 5 -> 3; enabled Primary 10 -> 8; CONTACT 3 -> 1; nothing deleted")
print(f"\nAPPROVE {budget_plan['plan_name']} {budget_plan['fingerprint']} "
      f"{budget_plan['operation_count']} operations FOR {CID}")
print(f"APPROVE {conv_plan['plan_name']} {conv_plan['fingerprint']} "
      f"{conv_plan['operation_count']} operations FOR {CID}")
print("\nEXTERNAL WRITES: 0 (local draft only)")
