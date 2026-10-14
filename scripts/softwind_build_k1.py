#!/usr/bin/env python3
"""Build PLAN-K1 - August 27 CPC control and delivery diagnosis (DRAFT).

Budget is NOT the active delivery constraint, so PLAN-I1D is deliberately NOT
created. This builds the Stage-12 diagnostic plan instead, targeting the
constraint the fresh data actually proves: an unbounded cost per click on an
uncapped Maximize Clicks strategy that now sits behind a $333.33 daily budget.

Read-only against Google Ads. Writes local plan + fingerprint artifacts only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
SERVICE = "Power Washing"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
PLANS = ROOT / "clients/softwind-power-washing/plans"
OUT_YAML = PLANS / "2026-08-27-plan-k1-cpc-control.yaml"
OUT_FP = PLANS / "2026-08-27-k1-fingerprint.json"

CEILING_USD = 30.00
CEILING_MICROS = 30_000_000


def normalize(plan: dict) -> dict:
    """Repository-standard canonical payload (matches softwind_plan_fingerprint)."""
    p = plan["change_plan"]
    t = p["target"]
    actions = []
    for a in p.get("actions", []):
        actions.append({
            "action_id": a["action_id"],
            "priority": a["priority"],
            "resource_type": a["resource_type"],
            "operation": a["operation"],
            "customer_id": a.get("customer_id", t["child_customer_id"]),
            "campaign_id": a.get("campaign_id"),
            "ad_group_id": a.get("ad_group_id"),
            "resource_id": a.get("resource_id"),
            "current_value": a.get("current_value"),
            "proposed_value": a.get("proposed_value"),
            "object_count": a.get("object_count", 1),
        })
    actions.sort(key=lambda x: x["action_id"])
    return {
        "target": {
            "exact_child_account_name": t["exact_child_account_name"],
            "child_customer_id": t["child_customer_id"],
            "exact_service": t["exact_service"],
        },
        "plan_id": p["plan_id"],
        "approval_type": p["approval_type"],
        "actions": actions,
        "action_count": len(actions),
        "object_count": sum(a["object_count"] for a in actions),
    }


def main() -> int:
    now = datetime.now(TZ)
    constraint = json.loads(
        (ROOT / "clients/softwind-power-washing/snapshots/"
                "constraint-2026-08-27.json").read_text(encoding="utf-8"))
    m = constraint["math"]

    plan = {"change_plan": {
        "plan_id": "PLAN-K1",
        "plan_title": "August 27 CPC control and delivery diagnosis",
        "approval_type": "BIDDING",
        "priority": "R1",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "ads_mutation_count": 2,
        "requires_separate_enable_approval": False,
        "supersedes": None,
        "reopens": {
            "plan_id": "PLAN-I1C",
            "settled_decision": (
                "PLAN-I1C recorded 'No CPC ceiling. Adding one during the August "
                "rescue would suppress spend, which is the opposite of the "
                "objective.'"),
            "new_material_evidence": (
                "On 2026-08-26 a SINGLE click on 'power washing near me' PHRASE "
                "cost $82.22 - the whole day's spend, and exactly the 2x daily "
                "ceiling of the then-$41.11 budget. That 2x ceiling was the only "
                "thing bounding the price. PLAN-I1C raised campaign A to $333.33 "
                "at 18:00:30 that same day, which lifted the effective per-click "
                "brake from $82.22 to $666.66 while leaving the CPC ceiling unset."),
        },
        "target": {
            "exact_child_account_name": NAME,
            "child_customer_id": CID,
            "manager_customer_id": "3373711342",
            "exact_service": SERVICE,
            "vertical": "similar-local-service",
        },
        "date_discrepancy_on_record": {
            "owner_supplied_header": "August 28, 2026 09:52 America/New_York",
            "actual_account_local_at_snapshot": now.isoformat(),
            "resolution": (
                "Four independent sources agree the account-local date is "
                "2026-08-27: the host clock in America/New_York; the same clock "
                "in UTC; the Google Ads API's own 'segments.date DURING "
                "YESTERDAY', which returns 2026-08-26; and the newest "
                "change_event in the account, 2026-08-26 18:00:31. The owner's "
                "MTD and remaining figures were correct; only the date line was "
                "one day ahead. All math in this plan uses 2026-08-27."),
        },
        "fresh_snapshot": {
            "account_local_timestamp": constraint["snapshot_account_local"],
            "mtd_spend_S": m["S_mtd_spend"],
            "per_campaign_mtd": m["S_per_campaign"],
            "target": m["TARGET"],
            "remaining_budget_R": m["R_remaining"],
            "remaining_calendar_days_D_including_today": m[
                "D_remaining_calendar_days_incl_today"],
            "remaining_hours_H_to_sept_1_0000": m["H_remaining_hours_to_sept_1_0000"],
            "required_average_per_calendar_day": m[
                "required_avg_per_remaining_calendar_day"],
            "required_rolling_24_hour_pace": m["required_rolling_24h_pace"],
            "remaining_scheduled_serving_hours": m["remaining_scheduled_serving_hours"],
            "required_spend_per_scheduled_serving_hour": m[
                "required_spend_per_scheduled_serving_hour"],
            "remaining_serving_days": m["remaining_serving_days"],
            "serving_hour_detail": m["remaining_serving_hour_detail"],
        },
        "primary_delivery_constraint": [
            "DEMAND LIMITED", "RANK LIMITED", "SCHEDULE LIMITED"],
        "constraint_evidence": {
            "NOT_account_spending_limit": (
                "account_budget rows report approved/adjusted/proposed "
                "spending_limit_type INFINITE; both billing_setup rows are "
                "APPROVED, the live one FOREVER with no end date; amount_served "
                "$253.39 against no cap. The Google Ads API exposes no "
                "customer-level daily spending limit field at all "
                "(GoogleAdsFieldService 'customer.%limit%' returns zero rows), so "
                "a UI-only new-account cap cannot be positively excluded by API - "
                "but 0.00% Lost IS (budget) on both campaigns is inconsistent "
                "with one binding."),
            "NOT_billing_or_verification": (
                "customer.status ENABLED; two APPROVED billing setups; no "
                "payment-failure or verification signal in any readable field."),
            "NOT_budget_limited": (
                "campaign.primary_status is ELIGIBLE on both campaigns with an "
                "EMPTY primary_status_reasons list - Google is not reporting "
                "'Limited by budget'. Search Lost IS (budget) is 0.00% on both "
                "campaigns for 2026-08-20..26."),
            "NOT_policy_or_eligibility": (
                "214 of 214 enabled keywords are system_serving_status ELIGIBLE "
                "and approval_status APPROVED, with zero RARELY_SERVED. 44 of 44 "
                "enabled ads are APPROVED and REVIEWED."),
            "NOT_negative_conflict": (
                "94 campaign negatives checked against every enabled keyword "
                "text: 0 conflicts. 0 shared negative lists attached."),
            "IS_demand_limited": (
                "Campaign B bidding_strategy_system_status is LIMITED_BY_INVENTORY "
                "- Google's own term for insufficient inventory. Search "
                "impression share for 2026-08-20..26 is already 81.03% (A) and "
                "85.71% (B): the account wins roughly four of every five "
                "available impressions, so very little remains to buy inside "
                "this footprint."),
            "IS_rank_limited": (
                "Search Lost IS (rank) 18.97% (A) / 14.29% (B) for "
                "2026-08-20..26 is the entire residual - all lost impressions "
                "are lost to rank, none to budget."),
            "IS_schedule_limited": (
                "Only %.2f of the %.2f remaining clock hours are inside the live "
                "Mon-Sat 08:00-18:00 schedule - %.0f%%. Sunday 2026-08-30 has no "
                "daypart at all, so 4 serving days remain, not 5."
                % (m["remaining_scheduled_serving_hours"],
                   m["H_remaining_hours_to_sept_1_0000"],
                   m["remaining_scheduled_serving_hours"]
                   / m["H_remaining_hours_to_sept_1_0000"] * 100)),
        },
        "budget_decision_rule_stage_8": {
            "1_remaining_month_billing_capacity_below_2500": {
                "verdict": "TRUE ONLY AT STANDARD DELIVERY",
                "detail": (
                    "4 remaining serving days x $374.44 = $1,497.76 at 1x, which "
                    "is below the $2,246.61 remaining. At the 2x Maximize Clicks "
                    "ceiling it is $2,995.52, which is above it. This is the only "
                    "one of the five criteria that can be read as true, and it is "
                    "pure arithmetic - it says nothing about whether demand exists "
                    "to convert capacity into spend."),
            },
            "2_daily_spending_limit_below_required_pace": {
                "verdict": "FALSE",
                "detail": ("Combined 2x delivery ceiling $748.88/day exceeds the "
                           "required $491.02 rolling-24h pace."),
            },
            "3_campaigns_currently_limited_by_budget": {
                "verdict": "FALSE",
                "detail": "primary_status ELIGIBLE, primary_status_reasons empty, both.",
            },
            "4_lost_is_budget_shows_material_missed_demand": {
                "verdict": "FALSE",
                "detail": "Search Lost IS (budget) 0.00% on both campaigns.",
            },
            "5_fresh_data_proves_demand_throttled_by_budget": {
                "verdict": "FALSE",
                "detail": ("Impression share 81-86%; campaign B explicitly "
                           "LIMITED_BY_INVENTORY. Budget is not throttling."),
            },
            "conclusion": (
                "BUDGET IS NOT THE ACTIVE DELIVERY CONSTRAINT. Four of five "
                "evidence-based criteria are false; the one arguable criterion is "
                "arithmetic capacity, which a budget rise cannot convert into "
                "spend when impression share is already 81-86% and Google reports "
                "LIMITED_BY_INVENTORY. PLAN-I1D is therefore NOT created."),
        },
        "cpc_evidence": {
            "every_billable_click_since_2026_08_17":
                constraint["billable_clicks_since_aug17"],
            "click_count": constraint["click_count"],
            "total_click_cost": constraint["click_cost_total"],
            "average_cpc": 36.20,
            "escalation_sequence_usd": [5.71, 22.13, 22.11, 26.66, 40.07, 54.49, 82.22],
            "documented_local_top_of_page_high": 28.23,
            "top_of_page_high_source": (
                "Keyword Planner restricted to the twelve keyword texts the "
                "account actually runs, read 2026-08-25; recorded in the "
                "2026-08-26 correction round."),
            "clicks_above_top_of_page_high": 3,
            "worst_click_multiple_of_top_of_page_high": 2.91,
            "emergency_stop_condition_from_2026_08_26": (
                "single click >=$40 investigate, >=$60 STOP; rolling >=$38 "
                "investigate, >=$45 STOP"),
            "stop_condition_status": (
                "BREACHED. The $82.22 click on 2026-08-26 exceeds the $60 single-"
                "click STOP line, and the $54.49 click on 2026-08-25 exceeds the "
                "$40 investigate line. The trailing-three-click average of $49.65 "
                "exceeds the $45 rolling STOP line."),
            "search_term_quality": (
                "The expensive clicks are NOT junk traffic. 'power washing near "
                "me', 'power wash near me' and 'powerwashing companies near me' "
                "are all core BOFU intents inside the approved service. The "
                "problem is the price paid, not the term bought."),
        },
        "why_a_ceiling_and_not_a_budget_change": (
            "A budget rise cannot buy impressions that do not exist: impression "
            "share is 81-86% and Google reports LIMITED_BY_INVENTORY. What the "
            "$333.33 budget did do is remove the only bound on price. Until "
            "18:00 on 2026-08-26 the 2x ceiling on a $41.11 budget capped any "
            "single day - and in practice any single click - at $82.22. That "
            "bound is now $666.66 on campaign A with no CPC ceiling set. A "
            "$30.00 ceiling restores price discipline without touching either "
            "budget, so the geo expansion that went live at 17:49 on 2026-08-26 "
            "keeps its full headroom to prove itself."),
        "ceiling_selection": {
            "selected_usd": CEILING_USD,
            "basis": (
                "Set just above the $28.23 documented local top-of-page high so "
                "rank on the head terms is preserved, while the tail is hard-"
                "capped. Lost IS (rank) has already fallen to 18.97%/14.29%, so "
                "the account is winning most auctions at prices well under the "
                "ceiling; the ceiling binds only the outliers."),
            "rejected_24_00": (
                "PLAN-B's $24.00 sits BELOW the $28.23 top-of-page high and would "
                "cost head-term rank in an account that is already rank-limited. "
                "PLAN-B stays on hold rather than being executed."),
            "rejected_no_ceiling": (
                "Status quo. Leaves an unbounded per-click price behind a $333.33 "
                "budget with a proven $82.22 click and a monotonically rising "
                "price trend. Rejected."),
            "rejected_60_00": (
                "A ceiling at the observed worst click would ratify the outlier "
                "rather than prevent it, and sits 2.1x above the top-of-page "
                "high. Rejected."),
            "measured_cost_of_the_ceiling": (
                "Applied retroactively to the 7 clicks already bought, a $30.00 "
                "ceiling would have cut spend from $253.39 to about $166.61 - it "
                "REDUCES August spend by roughly $87. That is 4% of the $1,950+ "
                "gap to $2,500, a gap that is unreachable either way. Trading 4% "
                "of an unreachable goal for a hard bound on a $200 click is the "
                "correct trade."),
        },
        "spend_goal_reality": {
            "target": 2500.0,
            "mtd": m["S_mtd_spend"],
            "required_rolling_24h_pace": m["required_rolling_24h_pace"],
            "required_per_scheduled_serving_hour": m[
                "required_spend_per_scheduled_serving_hour"],
            "observed_run_rate_per_serving_day": m[
                "observed_run_rate_per_serving_day_aug24_26"],
            "observed_per_serving_hour": round(
                m["observed_run_rate_per_serving_day_aug24_26"] / 10, 2),
            "gap_multiple": round(
                m["required_spend_per_scheduled_serving_hour"]
                / (m["observed_run_rate_per_serving_day_aug24_26"] / 10), 1),
            "clicks_required_at_current_avg_cpc": round(m["R_remaining"] / 36.20),
            "clicks_required_per_serving_day": round(
                m["R_remaining"] / 36.20 / m["remaining_serving_days"], 1),
            "clicks_observed_per_serving_day": 0.7,
            "impressions_required_per_serving_day_at_observed_ctr": round(
                m["R_remaining"] / 36.20 / m["remaining_serving_days"] / 0.0526),
            "impressions_observed_per_serving_day": 13,
            "current_impression_share": "81.03% (A) / 85.71% (B)",
            "projection_floor_status_quo": m["projected_august_at_current_run_rate"],
            "projection_with_geo_lift_at_capped_cpc": 628.0,
            "projection_with_geo_lift_at_current_cpc": 705.0,
            "projection_with_geo_lift_at_escalated_60_cpc": 1001.0,
            "verdict": (
                "$2,500 IS NOT REACHABLE. The honest August ceiling is roughly "
                "$550-$1,000, and the top of that range is only attainable by "
                "continuing to pay about $60 per click - which the work order's "
                "own constraint forbids. Reaching $2,500 would need 62 more "
                "clicks in 4 serving days, 12.4 per day against an observed 0.7, "
                "from an account that already wins 81-86% of available "
                "impressions."),
        },
        "explicitly_not_included": [
            "No budget change of any kind. Neither budget is raised or lowered.",
            "No bidding strategy change - Maximize Clicks (TARGET_SPEND) stays.",
            "No keyword, negative, ad, asset, location, schedule or conversion change.",
            "No campaign pause, and no enable of any paused resource.",
            "No Broad Match, Search Partners, Display, Performance Max, Demand Gen, "
            "AI Max, DSA, Final URL expansion or automatically created assets.",
        ],
        "actions": [
            {"action_id": "R1-K1-01", "priority": "R1",
             "resource_type": "CAMPAIGN", "operation": "UPDATE",
             "customer_id": CID, "campaign_id": CAMP_A,
             "campaign_name": "Power Washing", "resource_id": CAMP_A,
             "current_value": {"bidding_strategy_type": "TARGET_SPEND",
                               "target_spend_cpc_bid_ceiling_micros": None,
                               "target_spend_cpc_bid_ceiling_usd": None},
             "proposed_value": {"target_spend_cpc_bid_ceiling_micros": CEILING_MICROS,
                                "target_spend_cpc_bid_ceiling_usd": CEILING_USD,
                                "field_mask": "target_spend.cpc_bid_ceiling_micros"},
             "rollback": "Clear target_spend.cpc_bid_ceiling_micros (restore unset).",
             "object_count": 1},
            {"action_id": "R1-K1-02", "priority": "R1",
             "resource_type": "CAMPAIGN", "operation": "UPDATE",
             "customer_id": CID, "campaign_id": CAMP_B,
             "campaign_name": "Power Washing #2", "resource_id": CAMP_B,
             "current_value": {"bidding_strategy_type": "TARGET_SPEND",
                               "target_spend_cpc_bid_ceiling_micros": None,
                               "target_spend_cpc_bid_ceiling_usd": None},
             "proposed_value": {"target_spend_cpc_bid_ceiling_micros": CEILING_MICROS,
                                "target_spend_cpc_bid_ceiling_usd": CEILING_USD,
                                "field_mask": "target_spend.cpc_bid_ceiling_micros"},
             "rollback": "Clear target_spend.cpc_bid_ceiling_micros (restore unset).",
             "object_count": 1},
        ],
        "change_counts": {
            "budgets_changed": 0, "bidding_settings_changed": 2,
            "cpc_ceilings_added": 2, "locations_changed": 0,
            "keywords_changed": 0, "ads_changed": 0, "assets_changed": 0,
            "negatives_changed": 0, "schedules_changed": 0,
            "conversion_actions_changed": 0, "google_ads_mutations_total": 2,
        },
        "pre_execution_sequence": [
            "Fresh identity re-read; assert name, id, manager false, test false, "
            "USD, America/New_York.",
            "Fresh drift snapshot; assert both budgets still $333.33 / $41.11, "
            "both bidding TARGET_SPEND, both ceilings still unset, 80 positive "
            "and 1 negative location each, schedule 6 dayparts each.",
            "Recompute the fingerprint and assert it still matches the approved one.",
            "Assert the update mask is exactly target_spend.cpc_bid_ceiling_micros.",
            "Run validate_only on the CampaignService mutate and require PASS.",
            "Apply the two campaign mutations. Stop on any partial failure.",
        ],
        "readback_qa": [
            "Re-read both campaigns; assert target_spend.cpc_bid_ceiling_micros "
            "== 30000000.",
            "Assert bidding_strategy_type is still TARGET_SPEND on both.",
            "Assert campaign_budget.amount_micros is UNCHANGED at 333330000 and "
            "41110000.",
            "Assert 80 positive and 1 negative location criteria per campaign, "
            "all ENABLED.",
            "Assert 214 enabled keywords, 44 enabled ads, 94 campaign negatives, "
            "12 ad schedules, 4 conversion actions, 30 ad groups - all unchanged.",
            "Run an immediate fresh pacing report.",
        ],
        "monitoring_after_execution": [
            "Confirm the first billable click after the ceiling is <= $30.00.",
            "If Lost IS (rank) rises above 35% on either campaign for a full "
            "serving day, re-evaluate the ceiling with fresh evidence.",
            "No automated budget or bid writes. Every further change needs a new "
            "snapshot, plan, fingerprint and explicit approval.",
        ],
        "open_questions_for_owner": [
            {"id": "K1-Q1",
             "question": (
                 "$2,500 is not reachable in the 4 remaining serving days. "
                 "Confirm the August target should be restated to the achievable "
                 "$550-$1,000 range rather than chased."),
             "recommendation": "Restate the target. Do not chase.",
             "effect_if_unanswered": (
                 "Work proceeds on the achievable range; no spend-chasing action "
                 "is taken.")},
            {"id": "K1-Q2",
             "question": (
                 "Schedule expansion is the single largest remaining delivery "
                 "lever - it would add roughly 66 servable hours. It stays BLOCKED "
                 "on SCHED-Q1..Q6, chiefly: is (631) 502-7946 answered outside "
                 "Mon-Fri 08:00-18:00, and what is the callback commitment for an "
                 "after-hours form lead?"),
             "recommendation": (
                 "Answer both. If after-hours calls are not answered, expand to "
                 "form-capture hours only rather than 24/7."),
             "effect_if_unanswered": (
                 "Schedule stays Mon-Sat 08:00-18:00 and 66 hours stay unusable.")},
            {"id": "K1-Q3",
             "question": (
                 "7 clicks and $253.39 have produced 0 conversions. WhatConverts "
                 "DNI is proven broken and a foreign tag AW-17878095007 is "
                 "actively firing on the landing pages. Approve PLAN-A2/A3 "
                 "controlled tests so measurement is trusted before September."),
             "recommendation": "Approve PLAN-A2 and PLAN-A3.",
             "effect_if_unanswered": (
                 "September spend continues against unverified conversion "
                 "tracking.")},
        ],
        "no_automation_clause": (
            "No future budget or bid change is automated. Every further "
            "adjustment requires a new snapshot, a new plan, a new fingerprint "
            "and a new explicit approval."),
        "approval_owner": "Walter Correa",
        "approver_email": "access@greenmarketing.com",
        "evidence_files": [
            "snapshots/snapshot-2026-08-28.json",
            "snapshots/pacing-2026-08-28.json",
            "snapshots/dateprobe-2026-08-27.json",
            "snapshots/constraint-2026-08-27.json",
        ],
    }}

    assert_no_embedded_secrets(plan)
    payload = normalize(plan)
    fp = approval_code(payload)
    plan["change_plan"]["fingerprint"] = fp
    plan["change_plan"]["approval_phrase"] = (
        "APPROVE PLAN-K1 %s FOR %s" % (fp, CID))

    OUT_YAML.write_text(
        "# PLAN-K1 - AUGUST 27 CPC CONTROL AND DELIVERY DIAGNOSIS\n"
        "#\n"
        "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
        "# Stage-12 diagnostic plan. Budget is NOT the active delivery\n"
        "# constraint, so PLAN-I1D was deliberately NOT created.\n"
        "# BIDDING ONLY - two campaign CPC ceilings. No budget is touched.\n\n"
        + yaml.safe_dump(plan, sort_keys=False, width=96, allow_unicode=True),
        encoding="utf-8")

    fpdoc = {
        "generated_account_local": now.isoformat(),
        "target": {"exact_child_account_name": NAME, "child_customer_id": CID,
                   "exact_service": SERVICE, "manager_customer_id": "3373711342"},
        "fingerprint_function":
            "gm_gsa.safety.approval_code (SHA-256, first 12 hex, upper)",
        "plan_id": "PLAN-K1",
        "plan_file": OUT_YAML.name,
        "approval_type": "BIDDING",
        "fingerprint": fp,
        "action_count": payload["action_count"],
        "object_count": payload["object_count"],
        "ads_mutation_count": 2,
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "approval_phrase": "APPROVE PLAN-K1 %s FOR %s" % (fp, CID),
        "plan_i1d": {
            "created": False,
            "reason": ("Budget is not the active delivery constraint. Stage 8 "
                       "criteria 2, 3, 4 and 5 are all FALSE on fresh data; only "
                       "the arithmetic capacity criterion is arguable, and a "
                       "budget rise cannot convert capacity into spend at 81-86% "
                       "impression share with LIMITED_BY_INVENTORY."),
        },
        "canonical_payload": payload,
    }
    OUT_FP.write_text(json.dumps(fpdoc, indent=2), encoding="utf-8")

    print("PLAN-K1 built.")
    print("  file        : %s" % OUT_YAML)
    print("  fingerprint : %s" % fp)
    print("  actions     : %d   objects: %d   ads mutations: 2"
          % (payload["action_count"], payload["object_count"]))
    print("  status      : NOT APPROVED / DO NOT EXECUTE")
    print("  approval    : APPROVE PLAN-K1 %s FOR %s" % (fp, CID))
    print("\nPLAN-I1D: NOT CREATED - budget is not the active delivery constraint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
