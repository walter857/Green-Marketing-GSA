#!/usr/bin/env python3
"""Emit PLAN-E2A (revised negatives) and PLAN-I1B (budget on fresh pacing)."""
from __future__ import annotations

import json
import yaml
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "clients/softwind-power-washing/plans"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
TZ = ZoneInfo("America/New_York")

rev = json.loads((SNAP / "h-impact-e2-revision-2026-08-26.json").read_text(encoding="utf-8"))
snap = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))

TARGET = {"exact_child_account_name": "Softwind Power Washing - Live",
          "child_customer_id": "1521725229",
          "manager_customer_id": "3373711342",
          "exact_service": "Power Washing",
          "vertical": "similar-local-service"}

# ---------------------------------------------------------------- PLAN-E2A
e = rev["plan_e2a_revised"]
acts = []
for a in e["actions"]:
    acts.append({
        "action_id": a["action_id"], "priority": "R2",
        "resource_type": "CAMPAIGN_CRITERION",
        "operation": "CREATE_NEGATIVE_KEYWORD",
        "customer_id": "1521725229",
        "campaign_id": a["campaign_id"], "campaign_name": a["campaign"],
        "ad_group_id": None, "resource_id": "NEW negative keyword",
        "exact_term": a["negative_keyword"], "match_type": a["match_type"],
        "level": "CAMPAIGN",
        "current_value": "47 campaign negatives; none blocks this term",
        "proposed_value": {"text": a["negative_keyword"],
                           "match_type": a["match_type"], "negative": True},
        "current_matching_search_terms": a["triggering_search_terms"],
        "impressions": a["impressions"], "clicks": a["clicks"],
        "cost": a["cost"], "conversions": a["conversions"],
        "why": a["reason_out_of_scope"],
        "blocks_approved_keywords": a["blocks_approved_keywords"],
        "blocks_planned_skag_keywords": a["blocks_planned_skag_keywords"],
        "goes_live_immediately": True,
        "expected_effect": ("Blocks the observed out-of-scope query. Total account-wide "
                            "exposure across all six mutations is 8 impressions and "
                            "$0.00 - it cannot move pacing in either direction."),
        "rollback": a["rollback"],
        "approval_required": "YES - LIVE CHANGE, effective on creation",
        "object_count": 1})

planE2A = {"change_plan": {
    "plan_id": "PLAN-E2A",
    "plan_title": "Revised out-of-scope negatives - house cleaning narrowed to Exact",
    "approval_type": "LIVE_NEGATIVE_KEYWORDS", "priority": "R2",
    "approval_status": "NOT APPROVED", "execution_status": "DO NOT EXECUTE",
    "recommended_approval_order": 3,
    "ads_mutation_count": len(acts),
    "requires_separate_enable_approval": False,
    "supersedes": {"plan_id": "PLAN-E2", "fingerprint": "09E91EA674C8",
                   "status": "VOID", "voided_on": "2026-08-26",
                   "reason": ("PHRASE 'house cleaning' was too broad. Under modern "
                              "matching it could block legitimate exterior phrasings "
                              "such as 'exterior house cleaning' or 'house cleaning "
                              "power wash'. Narrowed to EXACT [house cleaning services "
                              "near me], which blocks only the single observed "
                              "interior-maid query.")},
    "target": TARGET,
    "what_changed": e["change"],
    "policy_check": (
        "Green Marketing protected terms - near me, quote, price, pricing, cost, best, "
        "hire, local, emergency - are NOT used as standalone negatives. The one EXACT "
        "negative contains 'near me' only as part of a complete, literal, out-of-scope "
        "query string; it blocks that exact phrase and nothing else, so no protected "
        "term is broadly suppressed."),
    "not_a_pacing_tool": (
        "Total exposure across all six mutations is 8 impressions and $0.00 spend "
        "account-wide since launch. These cannot and are not intended to influence "
        "pacing."),
    "conditional_on": e["conditional_on"],
    "keyword_universe_checked": e["keyword_universe_checked"],
    "blocks_zero_approved_keywords": e["blocks_zero_approved_keywords"],
    "blocks_zero_planned_skag_keywords": e["blocks_zero_planned_skag_keywords"],
    "actions": acts,
    "verification_after_execution": [
        "Read back campaign_criterion on both campaigns and assert 50 negatives each.",
        "Re-check the search terms report after 7 days; confirm no in-scope query "
        "disappeared."],
    "change_counts": {
        "campaigns_changed": 0, "campaigns_paused": 0, "budgets_changed": 0,
        "bidding_settings_changed": 0, "ad_schedules_changed": 0,
        "ad_groups_enabled": 0, "ad_groups_created_paused": 0, "keywords_enabled": 0,
        "keywords_created_paused": 0, "rsas_created_paused": 0, "ads_changed": 0,
        "negatives_added": len(acts), "assets_changed": 0, "final_urls_changed": 0,
        "conversion_actions_changed": 0, "google_ads_mutations_total": len(acts),
        "objects_that_go_live_immediately": len(acts)},
    "approval_owner": "Walter Correa",
    "approver_email": "access@greenmarketing.com"}}

# ---------------------------------------------------------------- PLAN-I1B
ts = datetime.fromisoformat(snap["snapshot_account_local"])
sep1 = datetime(2026, 9, 1, tzinfo=TZ)
mtd = snap["spend_mtd"]
S = mtd["combined"]["cost"]
R = round(2500.0 - S, 2)
D = 6
H = (sep1 - ts).total_seconds() / 3600.0
per = mtd["per_campaign"]

# addressable per campaign, from each campaign's own impressions / its own IS
addr = {}
for cid, days in (("24103511039", 22), ("24145053510", 8)):
    p = per[cid]
    a = p["impressions"] / p["search_is"]
    addr[cid] = {"impressions": p["impressions"], "search_is": p["search_is"],
                 "total_addressable_mtd": round(a, 1), "active_days": days,
                 "addressable_per_day": round(a / days, 2)}
tot = sum(v["addressable_per_day"] for v in addr.values())
share = {c: v["addressable_per_day"] / tot for c, v in addr.items()}
combined = round(R / D, 2)
A_amt = round(combined * share["24103511039"], 2)
B_amt = round(combined - A_amt, 2)

planI1B = {"change_plan": {
    "plan_id": "PLAN-I1B",
    "plan_title": "August budget headroom on fresh 2026-08-26 16:01 pacing",
    "approval_type": "BUDGET", "priority": "R1",
    "approval_status": "NOT APPROVED", "execution_status": "DO NOT EXECUTE",
    "recommended_approval_order": 6, "ads_mutation_count": 2,
    "requires_separate_enable_approval": False,
    "supersedes": [
        {"plan_id": "PLAN-I1", "fingerprint": "9308DFCF8741", "status": "VOID",
         "reason": ("Its $299.93/$88.21 split was derived from a 10:02 snapshot and "
                    "from PLAN-I2's demand assumptions, both now superseded.")},
        {"plan_id": "PLAN-I1A", "fingerprint": "5B9BCFA06FD5",
         "status": "VOID - replaced by this populated plan",
         "reason": ("PLAN-I1A was an actions-empty specification awaiting demand "
                    "inputs. Those inputs are now resolved: PLAN-I2A-C is void, so no "
                    "new SKAG serves in August, and PLAN-I5 is a routing fix that adds "
                    "no incremental demand. The budget can therefore be computed.")}],
    "target": TARGET,
    "fresh_snapshot": {
        "snapshot_account_local": snap["snapshot_account_local"],
        "identity_gate": snap["identity_gate"],
        "mtd_spend_S": S, "remaining_budget_R": R,
        "remaining_calendar_days_D": D,
        "remaining_hours_H": round(H, 2),
        "required_average_per_remaining_calendar_day": round(R / D, 2),
        "required_rolling_24_hour_pace": round(R / (H / 24), 2),
        "per_campaign": {c: {
            "campaign": per[c]["campaign"], "impressions": per[c]["impressions"],
            "clicks": per[c]["clicks"], "cost": per[c]["cost"],
            "avg_cpc": per[c]["avg_cpc"],
            "search_impression_share": per[c]["search_is"],
            "lost_is_budget": per[c]["lost_is_budget"],
            "lost_is_rank": per[c]["lost_is_rank"]} for c in per}},
    "demand_basis": {
        "rule": ("Allocation follows ADDRESSABLE DEMAND, not rank-loss headroom. With "
                 "Maximize Clicks uncapped, budget aimed at rank headroom is spent by "
                 "bidding UP, not by finding more queries."),
        "addressable": addr,
        "share_campaign_A": round(share["24103511039"], 4),
        "share_campaign_B": round(share["24145053510"], 4),
        "resources_actually_enabled_in_august": (
            "Only what is live today, plus - if approved - PLAN-I2A-E's House Washing "
            "Company Near Me, which Keyword Planner shows carries NO reportable local "
            "volume. PLAN-I2A-C is VOID. PLAN-I5 is create-paused and is a routing fix "
            "that adds ZERO incremental impressions. No approved geo expansion exists. "
            "Therefore the demand denominator is essentially unchanged from today."),
        "approved_geo_footprint": (
            "UNCHANGED - the current 8 targets. No geo expansion is approved, so no "
            "geo multiplier is applied to this budget.")},
    "actions": [
        {"action_id": "R1-I1B-01", "priority": "R1",
         "resource_type": "CAMPAIGN_BUDGET", "operation": "UPDATE",
         "customer_id": "1521725229", "campaign_id": "24103511039",
         "campaign_name": "Power Washing", "ad_group_id": None,
         "resource_id": "customers/1521725229/campaignBudgets/15764226923",
         "field_mask": "amount_micros",
         "current_value": {"budget_id": "15764226923", "amount_micros": 41110000,
                           "amount_usd": 41.11,
                           "capacity_remaining_6_days": 246.66},
         "proposed_value": {"amount_micros": int(round(A_amt * 1_000_000)),
                            "amount_usd": A_amt,
                            "capacity_remaining_6_days": round(A_amt * D, 2),
                            "two_x_daily_ceiling": round(A_amt * 2, 2)},
         "change_amount_usd": round(A_amt - 41.11, 2),
         "why": ("Campaign A holds %s addressable impressions/day against B's %s - a "
                 "%.1f%% share. It also carries 113 of the account's 127 MTD "
                 "impressions and held 100%% impression share today."
                 % (addr["24103511039"]["addressable_per_day"],
                    addr["24145053510"]["addressable_per_day"],
                    share["24103511039"] * 100)),
         "evidence": "snapshots/rescue-snapshot-2026-08-26.json at 16:01:33",
         "expected_effect": ("Makes $%.2f billable on this campaign. Expected ACTUAL "
                             "spend is far lower - see the honest_projection block."
                             % (A_amt * D)),
         "risk": ("HIGH on efficiency. Uncapped Maximize Clicks with %.1fx the budget "
                  "in a pool that held 100%% impression share today will bid UP, not "
                  "find more queries." % (A_amt / 41.11)),
         "rollback": "Set amount_micros back to 41110000 ($41.11).",
         "approval_required": "YES - budget change, separate approval",
         "object_count": 1},
        {"action_id": "R1-I1B-02", "priority": "R1",
         "resource_type": "CAMPAIGN_BUDGET", "operation": "UPDATE",
         "customer_id": "1521725229", "campaign_id": "24145053510",
         "campaign_name": "Power Washing #2", "ad_group_id": None,
         "resource_id": "customers/1521725229/campaignBudgets/15802443075",
         "field_mask": "amount_micros",
         "current_value": {"budget_id": "15802443075", "amount_micros": 41110000,
                           "amount_usd": 41.11,
                           "capacity_remaining_6_days": 246.66},
         "proposed_value": {"amount_micros": int(round(B_amt * 1_000_000)),
                            "amount_usd": B_amt,
                            "capacity_remaining_6_days": round(B_amt * D, 2),
                            "two_x_daily_ceiling": round(B_amt * 2, 2)},
         "change_amount_usd": round(B_amt - 41.11, 2),
         "why": ("Campaign B holds 70.0%% impression share with only 30.0%% rank loss "
                 "and %s addressable impressions/day - the least unclaimed volume in "
                 "the account. $%.2f/day already exceeds anything it has ever spent "
                 "($62.18 across 8 days)."
                 % (addr["24145053510"]["addressable_per_day"], B_amt)),
         "evidence": "same snapshot",
         "expected_effect": "Makes $%.2f billable on this campaign." % (B_amt * D),
         "risk": "LOW-MEDIUM. At 100% top impression share, extra budget mostly raises price.",
         "rollback": "Set amount_micros back to 41110000 ($41.11).",
         "approval_required": "YES - budget change, separate approval",
         "object_count": 1}],
    "mid_month_rule_check": {
        "formula": "MTD + combined budget x remaining days",
        "calculation": "%.2f + %.2f x %d = %.2f" % (S, combined, D, S + combined * D),
        "meets_2500": (S + combined * D) >= 2499.99},
    "honest_projection": {
        "headline": ("This budget will almost certainly NOT be spent, and the corrected "
                     "demand analysis is the reason."),
        "detail": ("Every demand-side plan has now been reclassified as a ROUTING or "
                   "RELEVANCE improvement rather than net-new volume: all five proposed "
                   "keywords are already matched by enabled keywords today. PLAN-I2A-C "
                   "is void. No geo expansion is approved. Campaign A held 100%% "
                   "impression share on 24 impressions today - there is nothing further "
                   "to buy at any budget. Raising the budget from $82.22 to $%.2f "
                   "creates headroom; it does not create auction demand."
                   % combined),
        "expected_actual_august_spend": ("$350-$500 without a geo decision, against a "
                                         "$2,500 target."),
        "what_would_actually_change_it": ("Walter's service-area confirmation. It is "
                                          "the only lever with a measured multiplier "
                                          "(up to 4.58x) attached to it.")},
    "change_counts": {
        "campaigns_changed": 0, "campaigns_paused": 0, "budgets_changed": 2,
        "bidding_settings_changed": 0, "ad_schedules_changed": 0,
        "ad_groups_enabled": 0, "ad_groups_created_paused": 0, "keywords_enabled": 0,
        "keywords_created_paused": 0, "rsas_created_paused": 0, "ads_changed": 0,
        "negatives_added": 0, "assets_changed": 0, "final_urls_changed": 0,
        "conversion_actions_changed": 0, "google_ads_mutations_total": 2},
    "approval_owner": "Walter Correa",
    "approver_email": "access@greenmarketing.com"}}

(PLANS / "2026-08-26-plan-e2a-revised-negatives.yaml").write_text(
    "# PLAN-E2A - REVISED OUT-OF-SCOPE NEGATIVES\n#\n"
    "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
    "# Supersedes PLAN-E2 (fingerprint 09E91EA674C8, now VOID).\n"
    "# All six go LIVE on creation. No paused state, no second gate.\n\n"
    + yaml.safe_dump(planE2A, sort_keys=False, width=90, allow_unicode=True),
    encoding="utf-8")
(PLANS / "2026-08-26-plan-i1b-budget-fresh-pacing.yaml").write_text(
    "# PLAN-I1B - AUGUST BUDGET HEADROOM ON FRESH PACING\n#\n"
    "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
    "# Supersedes PLAN-I1 (9308DFCF8741 VOID) and PLAN-I1A (5B9BCFA06FD5 VOID).\n"
    "# Budget-only. Read honest_projection before approving.\n\n"
    + yaml.safe_dump(planI1B, sort_keys=False, width=90, allow_unicode=True),
    encoding="utf-8")

print("PLAN-E2A : %d mutations" % len(acts))
print("PLAN-I1B : 2 budget mutations")
print("  snapshot %s" % snap["snapshot_account_local"])
print("  S=$%.2f R=$%.2f D=%d H=%.2f required/day=$%.2f required24h=$%.2f"
      % (S, R, D, H, R / D, R / (H / 24)))
print("  addressable/day  A=%s  B=%s  -> share %.1f%% / %.1f%%"
      % (addr["24103511039"]["addressable_per_day"],
         addr["24145053510"]["addressable_per_day"],
         share["24103511039"] * 100, share["24145053510"] * 100))
print("  A $41.11 -> $%.2f   (capacity $%.2f)" % (A_amt, A_amt * D))
print("  B $41.11 -> $%.2f   (capacity $%.2f)" % (B_amt, B_amt * D))
print("  combined $%.2f  mid-month check: %.2f + %.2f x %d = %.2f"
      % (combined, S, combined, D, S + combined * D))
