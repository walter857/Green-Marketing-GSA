#!/usr/bin/env python3
"""STAGE 9 - PLAN-I1C, August budget headroom after full geo expansion.

Budget-only. Recalculates the split from fresh evidence rather than reusing
PLAN-I1B's allocation. No bidding change, no CPC ceiling.

Local computation + one fresh read-only spend snapshot.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.safety import approval_code                     # noqa: E402

CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
TZ = ZoneInfo("America/New_York")
CLIENT = ROOT / "clients/softwind-power-washing"
PLANS = CLIENT / "plans"
SNAP = CLIENT / "snapshots"

STATE = json.loads((SNAP / "stage1-state-2026-08-26.json").read_text("utf-8"))
RES = json.loads((SNAP / "stage3-geo-resolution-2026-08-26.json").read_text("utf-8"))
TARGET = 2500.0

Q_SPEND = """
SELECT campaign.id, metrics.cost_micros
FROM campaign
WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-26'
  AND campaign.status != 'REMOVED'
"""

Q_KW = """
SELECT campaign.id, ad_group_criterion.criterion_id,
       ad_group_criterion.keyword.text, ad_group_criterion.status,
       ad_group.status, campaign.status
FROM keyword_view
WHERE campaign.status = 'ENABLED' AND ad_group.status = 'ENABLED'
  AND ad_group_criterion.status = 'ENABLED'
"""


def normalize(plan):
    cp = plan["change_plan"]
    t = cp["target"]
    acts = [{"action_id": a["action_id"], "priority": a["priority"],
             "resource_type": a["resource_type"], "operation": a["operation"],
             "customer_id": a.get("customer_id", t["child_customer_id"]),
             "campaign_id": a.get("campaign_id"),
             "ad_group_id": a.get("ad_group_id"),
             "resource_id": a.get("resource_id"),
             "current_value": a.get("current_value"),
             "proposed_value": a.get("proposed_value"),
             "object_count": a.get("object_count", 1)}
            for a in cp["actions"]]
    acts.sort(key=lambda x: x["action_id"])
    return {"target": {"exact_child_account_name": t["exact_child_account_name"],
                       "child_customer_id": t["child_customer_id"],
                       "exact_service": t["exact_service"]},
            "plan_id": cp["plan_id"], "approval_type": cp["approval_type"],
            "actions": acts, "action_count": len(acts),
            "object_count": sum(a["object_count"] for a in acts)}


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)

    spend = {}
    for row in svc.search(customer_id=CID, query=Q_SPEND):
        spend[str(row.campaign.id)] = round(row.metrics.cost_micros / 1e6, 2)
    S = round(sum(spend.values()), 2)
    R = round(TARGET - S, 2)

    sept1 = datetime(2026, 9, 1, 0, 0, 0, tzinfo=TZ)
    H = (sept1 - now).total_seconds() / 3600.0
    D = 31 - now.day + 1                      # includes the day of the edit
    req_day = R / D
    req_24h = R / (H / 24.0)

    kw = {c: 0 for c in CAMPAIGNS}
    for row in svc.search(customer_id=CID, query=Q_KW):
        cid = str(row.campaign.id)
        if cid in kw:
            kw[cid] += 1

    # ---- allocation bases ------------------------------------------------
    m = STATE["mtd"]
    addressable = {}
    for cid in CAMPAIGNS:
        impr = m[cid]["impressions"]
        is_share = m[cid]["search_impression_share"] or 0.0001
        addressable[cid] = impr / is_share
    tot_addr = sum(addressable.values())

    tot_kw = sum(kw.values())
    models = {
        "1_demand_proportional": {
            cid: addressable[cid] / tot_addr for cid in CAMPAIGNS},
        "2_primary_campaign_weighted": {
            "24103511039": 0.85, "24145053510": 0.15},
        "3_equal_split": {cid: 0.5 for cid in CAMPAIGNS},
    }
    chosen = "1_demand_proportional"
    share = models[chosen]

    # Round the combined requirement UP to the cent so the mid-month rule cannot
    # fail on rounding.
    min_combined = math.ceil((R / D) * 100) / 100
    raw = {cid: min_combined * share[cid] for cid in CAMPAIGNS}

    # HEADROOM ONLY. A budget is never reduced below its current level: this plan
    # exists to create capacity, and cutting a campaign's budget would suppress
    # delivery, which is the opposite of the objective.
    floor = {cid: STATE["campaigns"][cid]["budget_usd"] for cid in CAMPAIGNS}
    budgets, floored, deficit = {}, [], 0.0
    for cid in CAMPAIGNS:
        if raw[cid] < floor[cid]:
            budgets[cid] = floor[cid]
            deficit += floor[cid] - raw[cid]
            floored.append(cid)
    rest = [c for c in CAMPAIGNS if c not in budgets]
    tot_rest = sum(raw[c] for c in rest) or 1.0
    for c in rest:
        budgets[c] = round(raw[c] - deficit * (raw[c] / tot_rest), 2)
    combined = round(sum(budgets.values()), 2)
    if combined < min_combined:
        top = max(rest, key=lambda c: budgets[c])
        budgets[top] = round(budgets[top] + (min_combined - combined), 2)
        combined = round(sum(budgets.values()), 2)

    # A budget set to its existing value is a redundant mutation - drop it.
    unchanged = [c for c in CAMPAIGNS
                 if abs(budgets[c] - STATE["campaigns"][c]["budget_usd"]) < 0.005]

    actions = []
    for n, (cid, cname) in enumerate(CAMPAIGNS.items(), start=1):
        cur = STATE["campaigns"][cid]
        if cid in unchanged:
            continue
        actions.append({
            "action_id": "R1-I1C-%02d" % n, "priority": "R1",
            "resource_type": "CAMPAIGN_BUDGET", "operation": "UPDATE",
            "campaign_id": cid, "campaign_name": cname,
            "resource_id": cur["budget_id"],
            "current_value": {"budget_id": cur["budget_id"],
                              "amount_micros": cur["budget_micros"],
                              "amount_usd": cur["budget_usd"]},
            "proposed_value": {"amount_micros": int(round(budgets[cid] * 1e6)),
                               "amount_usd": budgets[cid],
                               "field_mask": "amount_micros"},
            "increase_usd": round(budgets[cid] - cur["budget_usd"], 2),
            "daily_spending_ceiling_2x": round(budgets[cid] * 2, 2),
            "remaining_month_capacity": round(budgets[cid] * D, 2),
            "rollback_budget_usd": cur["budget_usd"],
            "object_count": 1})

    plan = {"change_plan": {
        "plan_id": "PLAN-I1C",
        "plan_title": "August budget headroom after full geo expansion",
        "approval_type": "BUDGET",
        "priority": "R1",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "ads_mutation_count": len(actions),
        "requires_separate_enable_approval": False,
        "depends_on": {
            "plan_id": "PLAN-J2A",
            "why": ("The allocation assumes the 72 net-new approved targets are "
                    "live. Raising the budget BEFORE the geo expansion makes "
                    "uncapped Maximize Clicks bid up on the current thin pool, "
                    "which spends more and buys the same clicks. Stage 9 also "
                    "requires this plan to be re-verified against a post-geo "
                    "snapshot before execution."),
            "must_execute_after": True},
        "target": {"exact_child_account_name": NAME, "child_customer_id": CID,
                   "manager_customer_id": "3373711342",
                   "exact_service": "Power Washing",
                   "vertical": "similar-local-service"},
        "fresh_snapshot": {
            "account_local_timestamp": now.isoformat(),
            "owner_decision_timestamp": "2026-08-26T17:10:00-04:00",
            "mtd_spend_S": S, "per_campaign_mtd": spend,
            "target": TARGET, "remaining_budget_R": R,
            "remaining_calendar_days_D_including_edit_day": D,
            "remaining_hours_H": round(H, 2),
            "required_average_per_calendar_day": round(req_day, 2),
            "required_rolling_24_hour_pace": round(req_24h, 2)},
        "mid_month_rule_check": {
            "formula": "S + combined_average_daily_budget * D >= 2500",
            "calculation": "%.2f + %.2f x %d = %.2f"
                           % (S, combined, D, S + combined * D),
            "meets_2500": (S + combined * D) >= TARGET - 0.02,
            "note": ("Google computes the monthly charging limit from the average "
                     "daily budget in force on each day, so raising the budget on "
                     "2026-08-26 creates capacity for the remaining %d days only, "
                     "never retroactively." % D)},
        "allocation_evidence": {
            "enabled_keyword_rows_by_campaign": kw,
            "mtd_impressions_by_campaign": {
                c: m[c]["impressions"] for c in CAMPAIGNS},
            "search_impression_share_by_campaign": {
                c: m[c]["search_impression_share"] for c in CAMPAIGNS},
            "lost_is_rank_by_campaign": {
                c: m[c]["search_lost_is_rank"] for c in CAMPAIGNS},
            "lost_is_budget_by_campaign": {
                c: m[c]["search_lost_is_budget"] for c in CAMPAIGNS},
            "addressable_impressions_mtd": {
                c: round(addressable[c], 1) for c in CAMPAIGNS},
            "approved_geo_targets_after_J2A": {
                c: 8 + RES["unique_new_target_count"] for c in CAMPAIGNS},
            "cross_campaign_overlap": (
                "Both campaigns will hold an IDENTICAL 80-target geo footprint "
                "and both serve Power Washing. They already overlap on keyword "
                "theme. Weighting toward the campaign that demonstrably converts "
                "impressions into delivery reduces, but does not remove, "
                "self-competition. PLAN-G consolidation remains the structural "
                "fix and is held for September."),
            "ability_to_spend": {
                "24103511039": ("PROVEN. Spent $82.22 on 2026-08-26, exactly its "
                                "2x ceiling, so it is delivery-capped today."),
                "24145053510": ("UNPROVEN. $0.00 on 2026-08-26 and only 14 "
                                "impressions MTD. It has never demonstrated it "
                                "can absorb budget.")}},
        "allocation_models_considered": {
            "1_demand_proportional": {
                "share": {c: round(models["1_demand_proportional"][c], 4)
                          for c in CAMPAIGNS},
                "usd": {c: round(min_combined * models["1_demand_proportional"][c], 2)
                        for c in CAMPAIGNS},
                "basis": "Addressable impressions = impressions / impression share.",
                "verdict": "SELECTED"},
            "2_primary_campaign_weighted": {
                "share": models["2_primary_campaign_weighted"],
                "usd": {c: round(min_combined * models["2_primary_campaign_weighted"][c], 2)
                        for c in CAMPAIGNS},
                "basis": "Fixed 85/15 toward the campaign with proven delivery.",
                "verdict": ("REJECTED - close to the selected model but the 85/15 "
                            "split is an assertion, not a measurement.")},
            "3_equal_split": {
                "share": models["3_equal_split"],
                "usd": {c: round(min_combined * 0.5, 2) for c in CAMPAIGNS},
                "basis": "50/50.",
                "verdict": ("REJECTED - would hand $%.2f/day to a campaign that "
                            "spent $0.00 today and holds 70%% impression share on "
                            "14 impressions. It would maximise self-competition "
                            "and under-fund the only campaign proven to deliver."
                            % round(min_combined * 0.5, 2))},
        },
        "headroom_only_rule": {
            "rule": ("No campaign budget is reduced below its current level. This "
                     "plan creates capacity; cutting a budget would suppress "
                     "delivery and work against the objective."),
            "campaigns_floored_at_current_budget": floored,
            "campaigns_with_no_change_so_no_mutation": unchanged,
            "note": ("Demand-proportional weighting alone would have set Power "
                     "Washing #2 to $24.33, BELOW its current $41.11. That would "
                     "have been a budget cut disguised as an allocation. It is "
                     "floored at its current value instead, and because the value "
                     "is unchanged it produces no mutation at all.")},
        "selected_allocation": {
            "model": chosen,
            "campaign_24103511039_usd": budgets["24103511039"],
            "campaign_24145053510_usd": budgets["24145053510"],
            "combined_usd": combined,
            "why": ("Demand-proportional tracks the only measured quantity that "
                    "differs between the two campaigns: how much addressable "
                    "search each one actually reaches. It funds proven delivery "
                    "without starving the second campaign, and it does not invent "
                    "a weighting.")},
        "explicitly_not_included": [
            "No CPC ceiling. Adding one during the August rescue would suppress "
            "spend, which is the opposite of the objective.",
            "No bidding strategy change - Maximize Clicks (TARGET_SPEND) stays.",
            "No location, keyword, ad, asset, negative, schedule or conversion "
            "change of any kind."],
        "actions": actions,
        "change_counts": {
            "budgets_changed": len(actions), "bidding_settings_changed": 0,
            "cpc_ceilings_added": 0, "locations_changed": 0,
            "keywords_changed": 0, "ads_changed": 0, "assets_changed": 0,
            "negatives_changed": 0, "schedules_changed": 0,
            "conversion_actions_changed": 0,
            "google_ads_mutations_total": len(actions)},
        "readback_qa": [
            "Re-read both campaign budgets; assert the new amount_micros.",
            "Assert bidding_strategy_type is still TARGET_SPEND on both.",
            "Assert target_spend.cpc_bid_ceiling_micros is still unset on both.",
            "Assert location criteria match the post-J2A approved state.",
            "Assert keywords, ads, negatives, assets, conversions and schedules "
            "are unchanged.",
            "Run the pacing report immediately."],
        "pacing_checkpoints": [
            "2026-08-27 before ads begin serving (pre-08:00 ET)",
            "2026-08-27 09:00 ET", "2026-08-27 13:00 ET",
            "2026-08-27 17:00 ET", "2026-08-27 end of day"],
        "no_automation_clause": (
            "No future budget change is automated. Every further adjustment "
            "requires a new snapshot, a new plan, a new fingerprint and a new "
            "explicit approval."),
        "approval_owner": "Walter Correa",
        "approver_email": "access@greenmarketing.com"}}

    fp = approval_code(normalize(plan))
    out = PLANS / "2026-08-26-plan-i1c-budget-after-full-geo.yaml"
    out.write_text(
        "# PLAN-I1C - AUGUST BUDGET HEADROOM AFTER FULL GEO EXPANSION\n#\n"
        "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
        "# BUDGET ONLY. Execute only AFTER PLAN-J2A readback QA passes.\n\n"
        + yaml.safe_dump(plan, sort_keys=False, width=94, allow_unicode=True),
        encoding="utf-8")

    print("STAGE 9 - PLAN-I1C   fingerprint %s" % fp)
    print()
    print("  account-local timestamp : %s" % now.isoformat())
    print("  MTD spend S             : $%.2f   %s" % (S, spend))
    print("  remaining R             : $%.2f" % R)
    print("  remaining days D        : %d   (includes 2026-08-26)" % D)
    print("  remaining hours H       : %.2f" % H)
    print("  required per day        : $%.2f" % req_day)
    print("  required 24h pace       : $%.2f" % req_24h)
    print()
    print("  ALLOCATION MODELS")
    for k, v in plan["change_plan"]["allocation_models_considered"].items():
        print("     %-30s A=$%-8.2f B=$%-8.2f  %s"
              % (k, v["usd"]["24103511039"], v["usd"]["24145053510"],
                 v["verdict"].split(" - ")[0]))
    print()
    print("  SELECTED")
    for cid, cname in CAMPAIGNS.items():
        cur = STATE["campaigns"][cid]
        tag = "  NO CHANGE - no mutation" if cid in unchanged else ""
        print("     %s %-18s $%.2f -> $%.2f  (+$%.2f)  2x ceiling $%.2f  "
              "month capacity $%.2f%s"
              % (cid, cname, cur["budget_usd"], budgets[cid],
                 budgets[cid] - cur["budget_usd"], budgets[cid] * 2,
                 budgets[cid] * D, tag))
    print("     combined $%.2f/day" % combined)
    print()
    mm = plan["change_plan"]["mid_month_rule_check"]
    print("  MID-MONTH RULE: %s  meets_2500=%s" % (mm["calculation"], mm["meets_2500"]))
    print()
    print("APPROVE PLAN-I1C %s FOR %s" % (fp, CID))
    print()
    print("wrote %s" % out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
