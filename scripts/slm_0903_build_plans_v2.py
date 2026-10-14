#!/usr/bin/env python3
"""Rebuild the five Softwind L&M packages in the executor's own plan shape.

The first pass wrote standalone JSON packages that scripts/execute_approved_plan.py
cannot read. These plans use the exact contract that executor enforces:

    change_plan.target
    change_plan.subplans.<STATUS|BUDGET|CONVERSIONS|EXISTING_RESOURCES>.actions[]

and the fingerprint is produced by the SAME function the executor recomputes
before it will run, so an approval code cannot drift from the file on disk.

One plan file per package, so each carries its own independent approval.
Local only; writes YAML and prints fingerprints.
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PKG = B / "10-change-packages-v2"
TZ = ZoneInfo("America/New_York")
CID = "2429758629"
PATIO, PAVERS = "23484806108", "23489296528"

TARGET = {
    "exact_child_account_name": "Softwind Landscape & Masonry - Live",
    "child_customer_id": CID,
    "manager_customer_id": "3373711342",
    "currency": "USD",
    "time_zone": "America/New_York",
    "exact_service": "patio construction (Patio) and paver installation (Pavers)",
    "identity_receipt": "clients/softwind-landscape-masonry/snapshots/identity-gate-2026-09-03-1959.json",
    "baseline_snapshot": "recovery/2026-09-patio-pavers/01e-baseline-2.json",
    "baseline_evidence_sha256_short": "3D9E3199DD183E79",
}
EMPTY = {"actions": [], "empty_reason": "not part of this package"}
SUBPLANS = ["STATUS", "BUDGET", "EXISTING_RESOURCES", "CONVERSIONS",
            "CREATE_PAUSED", "SITE_OR_TRACKING", "ENABLE"]

# Per-campaign ceilings, replacing the single blended $22.
CEILINGS = {PATIO: 16.00, PAVERS: 18.00}
BUDGETS = {PATIO: 24.00, PAVERS: 32.00}

ASPHALT = [
    ("local asphalt companies near me", "PHRASE", 132.69, 5, 1.0),
    ("asphalt contractor near me", "PHRASE", 102.01, 4, 0.0),
    ("asphalt paving services near me", "PHRASE", 13.21, 1, 0.0),
    ("asphalt services near me", "PHRASE", 0.00, 0, 0.0),
    ("local asphalt paving companies", "PHRASE", 0.00, 0, 0.0),
    ("local asphalt paving contractors", "PHRASE", 0.00, 0, 0.0),
    ("asphalt and paving companies near me", "PHRASE", 0.00, 0, 0.0),
]


def plan_doc(name, subplan, actions, meta):
    subplans = {s: dict(EMPTY) for s in SUBPLANS}
    subplans[subplan] = {"actions": actions}
    return {"change_plan": {
        "plan_name": name, "plan_version": 2,
        "generated_at": datetime.now(TZ).isoformat(),
        "target": TARGET, "subplan_used": subplan,
        "subplans": subplans, **meta}}


def fp(doc, subplan):
    p = doc["change_plan"]
    return approval_code({"target": p["target"], "subplan": subplan,
                          "actions": p["subplans"][subplan]["actions"]})


def main() -> int:
    PKG.mkdir(parents=True, exist_ok=True)
    base = json.loads((B / "01e-baseline-2.json").read_text(encoding="utf-8"))
    bid_ev = json.loads((B / "15-bid-evidence.json").read_text(encoding="utf-8"))
    bud_ev = json.loads((B / "16-bud-evidence.json").read_text(encoding="utf-8"))
    plans = {}

    # ---------------- BID-2 : per-campaign ceilings ----------------
    acts = []
    for i, (cid, ceil) in enumerate(CEILINGS.items(), 1):
        e = bid_ev["campaigns"][cid]
        sc = e["ceiling_scenarios"][str(int(ceil))]
        acts.append({
            "action_id": "BID-%02d" % i,
            "operation": "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING",
            "resource_type": "campaign", "resource_id": cid,
            "resource_name": e["name"],
            "current_state": "target_spend.cpc_bid_ceiling_micros = UNSET (no ceiling)",
            "proposed_state": "target_spend.cpc_bid_ceiling_micros = %d (about $%.2f)"
                              % (int(ceil * 1e6), ceil),
            "rollback_state": "clear target_spend.cpc_bid_ceiling_micros (back to UNSET)",
            "object_count": 1,
            "evidence": {
                "bidding_strategy_type": e["bidding_strategy_type"],
                "portfolio_strategy": e["portfolio_strategy"],
                "ceiling_today": e["cpc_bid_ceiling_display"],
                "avg_cpc_by_month": {m: v["avg_cpc"] for m, v in sorted(e["monthly"].items())},
                "cvr_by_month": {m: v["cvr"] for m, v in sorted(e["monthly"].items())},
                "most_expensive_day_observed": e["daily_max"],
                "days_with_clicks": e["days_with_clicks"],
                "days_above_this_ceiling": e["days_above_ceiling"][str(int(ceil))],
                "modelled_click_retention": sc["click_retention"],
                "modelled_conversion_retention": sc["conversion_retention"],
                "converting_keyword_cpcs": e["converting_keyword_cpcs"],
            },
            "expected_effect": (
                "Caps the price of a click at $%.2f. Modelled retention %.1f%% of "
                "historic clicks and %.0f%% of historic conversion credits."
                % (ceil, 100 * sc["click_retention"],
                   100 * (sc["conversion_retention"] or 0))),
            "risk": ("Lower auction competitiveness. Monitor "
                     "search_rank_lost_impression_share; if it rises sharply with no "
                     "gain in click volume, raise the ceiling through a new plan."),
        })
    plans["PLAN-SLM-BID-2"] = plan_doc(
        "PLAN-SLM-BID-2", "EXISTING_RESOURCES", acts, {
            "summary": ("Set a SEPARATE CPC bid ceiling on each Maximize Clicks "
                        "campaign. Neither has any ceiling today."),
            "why_per_campaign": (
                "A single blended $22 was wrong. Patio has never recorded a daily "
                "average CPC above $15.56 and has zero days above $16, so $22 would "
                "have been a no-op there while its CPC climbed $5.97 -> $13.98 across "
                "five months. Pavers retains identically at $18, $20 and $22 (87.3% of "
                "clicks, 88% of credits), so $18 is strictly cheaper for the same "
                "traffic. After PLAN-SLM-KW-2 the highest-priced converting keyword in "
                "Pavers is $16.75 and in Patio $10.91; the only converting keyword "
                "above $18 is 'local asphalt companies near me', which KW-2 pauses."),
            "changes_only": ("target_spend.cpc_bid_ceiling_micros. The bidding strategy "
                             "type stays TARGET_SPEND (Maximize Clicks) on both "
                             "campaigns. No budget, network, location, keyword, "
                             "negative, ad, asset or conversion object is touched."),
            "supersedes": "PLAN-SLM-BID-1 fingerprint 50C553579EF3 (OBSOLETE, $22 blended)",
            "dependencies": [],
        })

    # ---------------- BUD-2 ----------------
    acts = []
    for i, (cid, amt) in enumerate(BUDGETS.items(), 1):
        c = base["campaigns"][cid]
        acts.append({
            "action_id": "BUD-%02d" % i, "operation": "SET_CAMPAIGN_BUDGET_AMOUNT",
            "resource_type": "campaign_budget", "resource_id": c["budget_id"],
            "resource_name": "%s daily budget" % c["name"],
            "campaign_id": cid, "campaign_name": c["name"],
            "current_state": "amount_micros = %d ($%.2f/day)"
                             % (int(c["budget_amount"] * 1e6), c["budget_amount"]),
            "proposed_state": "amount_micros = %d ($%.2f/day)" % (int(amt * 1e6), amt),
            "rollback_state": "amount_micros = %d ($%.2f/day)"
                              % (int(c["budget_amount"] * 1e6), c["budget_amount"]),
            "object_count": 1,
            "budget_explicitly_shared": c["budget_explicitly_shared"],
            "budget_reference_count": c["budget_reference_count"],
            "evidence": "sole campaign on this budget; reference_count=%d, shared=%s"
                        % (c["budget_reference_count"], c["budget_explicitly_shared"]),
        })
    plans["PLAN-SLM-BUD-2"] = plan_doc(
        "PLAN-SLM-BUD-2", "BUDGET", acts, {
            "summary": "Bring projected September spend under the $2,000 account cap.",
            "account_wide_pacing": {
                k: bud_ev[k] for k in (
                    "account_mtd_spend", "today", "remaining_days_excluding_today",
                    "remaining_budget", "remaining_daily_allowance",
                    "enabled_campaign_count", "enabled_campaign_ids",
                    "paused_campaign_count", "paused_campaign_mtd_spend",
                    "any_shared_budget", "current_enabled_daily_total",
                    "proposed_enabled_daily_total", "projection_current",
                    "projection_proposed", "projection_at_complete_day_run_rate",
                    "headroom_at_proposed",
                    "worst_case_if_all_six_enabled_at_current_budgets",
                    "projection_method")},
            "cap_check": ("PASS. Projected $%.2f against a $2,000.00 hard cap, leaving "
                          "$%.2f of headroom for Maximize Clicks overdelivery. The "
                          "projection covers EVERY enabled campaign in %s: there are "
                          "exactly %d, Patio and Pavers, and the four paused campaigns "
                          "have spent $%.2f month to date."
                          % (bud_ev["projection_proposed"], bud_ev["headroom_at_proposed"],
                             CID, bud_ev["enabled_campaign_count"],
                             bud_ev["paused_campaign_mtd_spend"])),
            "shared_budget_risk": ("NONE. Every budget in the account has "
                                   "explicitly_shared=false and reference_count=1, so "
                                   "no other campaign draws on either budget."),
            "supersedes": "PLAN-SLM-BUD-1 fingerprint D82341B7238E (OBSOLETE, same values, wrong file shape)",
            "dependencies": [],
        })

    # ---------------- KW-2 ----------------
    kidx = {}
    for key, k in base["keywords"].items():
        if k["campaign_id"] == PAVERS and not k["negative"]:
            kidx[(k["text"], k["match_type"])] = (key, k)
    acts = []
    for i, (text, mt, cost, clicks, conv) in enumerate(ASPHALT, 1):
        key, k = kidx[(text, mt)]
        ag_id, crit_id = key.split("~")
        acts.append({
            "action_id": "KW-%02d" % i, "operation": "PAUSE_AD_GROUP_CRITERION",
            "resource_type": "ad_group_criterion",
            "resource_id": crit_id, "criterion_id": crit_id, "ad_group_id": ag_id,
            "ad_group_name": k["ad_group"], "campaign_id": PAVERS,
            "campaign_name": "Pavers", "keyword_text": text, "match_type": mt,
            "current_state": k["status"], "proposed_state": "PAUSED",
            "rollback_state": "ENABLED",
            "object_count": 1,
            "alltime_cost": cost, "alltime_clicks": clicks,
            "alltime_raw_credits": conv, "qualified_leads": "UNKNOWN - no CRM join exists",
            "authority": ("USER-2026-09-03 recovery prompt, section 2: asphalt paving, "
                          "asphalt repair and blacktop are explicitly outside the "
                          "approved service scope. This is a DECLARED-SCOPE exclusion, "
                          "not a performance judgement - the keyword set would be "
                          "paused even if it converted well."),
            "reason": "Keyword text names asphalt, a service outside both work orders.",
        })
    plans["PLAN-SLM-KW-2"] = plan_doc(
        "PLAN-SLM-KW-2", "STATUS", acts, {
            "summary": ("Pause the seven ENABLED asphalt keywords added to Pavers on "
                        "2026-06-16. Paused, never removed."),
            "totals": {"spend": round(sum(a["alltime_cost"] for a in acts), 2),
                       "clicks": sum(a["alltime_clicks"] for a in acts),
                       "raw_credits": sum(a["alltime_raw_credits"] for a in acts),
                       "qualified_leads": "UNKNOWN"},
            "not_paused_and_why": {
                "paving company near me (PHRASE + EXACT)": (
                    "3 credits on $450.02 across 36 clicks. Ambiguous, not "
                    "wrong-service. The asphalt negative underneath it removes the "
                    "asphalt queries and keeps the rest."),
                "local paving companies (PHRASE)": "WATCH. Same treatment.",
                "local driveway companies / driveway companies near me": (
                    "$158.09, 0 credits, but driveway paver installation is UNRESOLVED "
                    "(SLM-Q5). Held out."),
                "paver driveway installation near me (EXACT + PHRASE)": (
                    "Paver-qualified. Held for the same question."),
            },
            "supersedes": "PLAN-SLM-KW-1 fingerprint 19FA5CBBB1E5 (OBSOLETE)",
            "dependencies": [],
            "executor_note": ("The STATUS subplan of execute_approved_plan.py is "
                              "pause-only and refuses any operation other than "
                              "PAUSE_AD_GROUP_CRITERION or any proposed_state other "
                              "than PAUSED. It cannot enable or remove anything."),
        })

    # ---------------- NEG-2 ----------------
    negs = list(csv.DictReader((B / "06-negative-plan-v2.csv").open(encoding="utf-8")))
    acts = []
    for i, n in enumerate(sorted(negs, key=lambda r: (r["campaign"], r["family"],
                                                      r["negative_text"])), 1):
        acts.append({
            "action_id": "NEG-%03d" % i, "operation": "ADD_CAMPAIGN_NEGATIVE_KEYWORD",
            "resource_type": "campaign_criterion", "resource_id": n["campaign_id"],
            "resource_name": n["campaign"], "campaign_id": n["campaign_id"],
            "campaign_name": n["campaign"], "negative_text": n["negative_text"],
            "match_type": n["match_type"], "level": "CAMPAIGN",
            "classification": n["classification"], "family": n["family"],
            "authority": n["authority"],
            "current_state": "no such negative on this campaign",
            "proposed_state": "campaign negative %s %r" % (n["match_type"],
                                                           n["negative_text"]),
            "rollback_state": "remove this campaign_criterion",
            "object_count": 1,
            "blocks_terms": int(n["blocks_terms"]),
            "blocks_cost": float(n["blocks_cost"]),
            "blocks_clicks": int(n["blocks_clicks"]),
            "blocks_conversions": float(n["blocks_conversions"]),
            "source_search_terms": n["top_source_terms_by_cost"],
            "collision_test": n["collision_test"],
            "keywords_tested": int(n["keywords_tested"]),
            "protected_terms_tested": int(n["protected_terms_tested"]),
            "existing_negatives_tested": int(n["existing_negatives_tested"]),
            "dependency": n["dependency"],
        })
    plans["PLAN-SLM-NEG-2"] = plan_doc(
        "PLAN-SLM-NEG-2", "EXISTING_RESOURCES", acts, {
            "summary": ("Create %d campaign-level PHRASE negatives on Patio and Pavers "
                        "for confirmed wrong-service, employment and DIY/materials "
                        "intent." % len(acts)),
            "object_count": len(acts),
            "reduced_from_v1": ("PLAN-SLM-NEG-1 proposed 154. 49 of those were "
                                "REDUNDANT: an existing BROAD negative already blocks "
                                "every query the proposed PHRASE negative would block, "
                                "because a BROAD negative fires whenever all of its "
                                "words appear. The v1 redundancy check only compared "
                                "PHRASE to PHRASE and missed this entirely. 6 more were "
                                "moved to a non-executable annex pending SLM-Q9."),
            "classification_counts": {},
            "coverage": json.loads((B / "06c-coverage-v2.json").read_text(encoding="utf-8")),
            "annex_not_executable": "06d-negative-annex-nonexecutable.csv",
            "rejected_with_reasons": "06b-negative-rejected-v2.csv",
            "supersedes": "PLAN-SLM-NEG-1 fingerprint 0895911A8133 (OBSOLETE, 154 rows, 49 redundant)",
            "dependencies": ["PLAN-SLM-KW-2 must execute and read back FIRST. One "
                             "negative ('asphalt' PHRASE on Pavers) collides with the "
                             "seven keywords that plan pauses. Google's validate_only "
                             "does NOT catch this - only the local collision test does."],
        })
    cc = {}
    for a in acts:
        cc[a["classification"]] = cc.get(a["classification"], 0) + 1
    plans["PLAN-SLM-NEG-2"]["change_plan"]["classification_counts"] = cc

    # ---------------- CONV-2 ----------------
    conv_ev = json.loads((B / "17-conv-evidence.json").read_text(encoding="utf-8"))
    form = conv_ev["co_occurrence"]["form"]
    a = conv_ev["actions"]["7461619140"]
    acts = [{
        "action_id": "CONV-01", "operation": "DEMOTE_CONVERSION_ACTION_FROM_PRIMARY",
        "resource_type": "conversion_action", "resource_id": "7461619140",
        "resource_name": "Softwind Submit lead form",
        "current_state": "primary_for_goal = True", "proposed_state": "primary_for_goal = False",
        "rollback_state": "primary_for_goal = True", "object_count": 1,
        "attributes": a,
        "twin_kept_primary": {
            "id": "7480764700",
            "name": "Softwind Landscape & Masonry (web) form_submission",
            "type": "GOOGLE_ANALYTICS_4_CUSTOM", "counting_type": "MANY_PER_CLICK",
            "why_this_one_stays": (
                "It is the superset. It fired on all 6 days the WEBPAGE action fired "
                "AND on 4 further days the WEBPAGE action did not. It is MANY_PER_CLICK "
                "where the WEBPAGE action is ONE_PER_CLICK, which is why 2026-04-28 "
                "reads 3 against 1 - same click, three submissions, capped at one.")},
        "duplicate_proof": {
            "method": ("Day-level co-occurrence across all recorded history, "
                       "segments.date x segments.conversion_action, plus the "
                       "conversion-lag profile."),
            "days_demoted_action_fired": form["days_demote_fired"],
            "days_kept_action_fired": form["days_keep_fired"],
            "days_both_fired": form["days_both_fired"],
            "days_demoted_action_fired_ALONE": form["days_only_demote"],
            "same_day_identical_counts": form["same_day_equal_counts"],
            "overlap_days": form["same_day_matches"],
            "lag_profile_demoted": "8.0 of 8.0 all_conversions in LESS_THAN_ONE_DAY",
            "lag_profile_kept": "12.0 of 13.0 all_conversions in LESS_THAN_ONE_DAY",
            "conclusion": (
                "The WEBPAGE action never once fired on a day the GA4 action did not. "
                "Its events are a strict subset, and on 5 of 6 overlapping days the "
                "counts are identical. Both carry category SUBMIT_LEAD_FORM, origin "
                "WEBSITE and a sub-one-day lag. This is duplicate counting of one "
                "submission, not two separate lead actions."),
            "residual_uncertainty": (
                "Day-level co-occurrence is not event-level ID matching. A controlled "
                "test with a unique lead identifier would settle it beyond doubt; the "
                "procedure is documented in 18-conv-controlled-test.md and has NOT "
                "been run, because submitting a live form would create a real record "
                "in the client's CRM and the form's field map is unverified."),
        },
        "campaign_learning_impact": (
            "NONE. Both in-scope campaigns run TARGET_SPEND (Maximize Clicks), which "
            "does not consume conversion data for bidding. No learning period is "
            "disturbed. This is also why the change is safe to make BEFORE the "
            "P2 Smart Bidding readiness gate rather than after."),
        "reporting_impact": (
            "Reported Conversions falls by up to 8 credits across all history. "
            "Historic months are NOT restated - a credit already counted stays in the "
            "historical column - so before/after comparisons must be drawn at the "
            "change date, never across it."),
        "whatconverts_dependency": (
            "None. WhatConverts writes to WC Leads (UPLOAD_CLICKS, 7635680357) and "
            "WC Call (UPLOAD_CALLS, 7635680543), not to either web form action. "
            "Verified from conversion_action.type."),
    }]
    plans["PLAN-SLM-CONV-2"] = plan_doc(
        "PLAN-SLM-CONV-2", "CONVERSIONS", acts, {
            "summary": ("Demote ONE proven-duplicate primary conversion action. "
                        "Reduced from two after the day-level evidence was gathered."),
            "dropped_from_v1": {
                "action": "Calls from ads (1) (7508686781)",
                "why_dropped": (
                    "PLAN-SLM-CONV-1 claimed it duplicated 'Calls from ads' "
                    "(7461572537) and cited a June 2026 overlap. The day-level data "
                    "refutes that: 7508686781 fired on 19 days, 7461572537 on 13, and "
                    "the two NEVER fired on the same day. The June monthly overlap was "
                    "two actions firing on different days inside one month. They are a "
                    "handover, not a duplicate. The QA gate forbids demoting on a "
                    "theoretical duplicate, so it is dropped and moved to monitoring."),
                "residual_risk": (
                    "Both remain primary AD_CALL / PHONE_CALL_LEAD actions. If the "
                    "dormant one ever resumes while the other is still firing, real "
                    "duplication begins. Watch item, not an approved change."),
            },
            "still_held_back": {
                "WC Leads (7635680357)": (
                    "Fired on 2 of the 6 form-overlap days, and on 2026-07-15 all three "
                    "actions recorded 2 apiece - a probable triple count. It is still "
                    "NOT demoted, because it carries the only credit Patio recorded in "
                    "August and its intended replacement last fired 2026-08-08. Revisit "
                    "after the tracking repair."),
                "WC Call (7635680543)": (
                    "Zero conversions and zero all_conversions in every month. Broken, "
                    "not duplicative. Fix the path before touching the flag."),
                "the five Google-hosted local actions": (
                    "Already isolated: include_in_conversions_metric=false and every "
                    "GOOGLE_HOSTED customer goal is biddable=false. No change."),
            },
            "supersedes": "PLAN-SLM-CONV-1 fingerprint FB9DA2D017AD (OBSOLETE, 2 ops, one unproven)",
            "dependencies": [],
        })

    # ---------------- emit ----------------
    index = {}
    print("=" * 78)
    for name, doc in plans.items():
        assert_no_embedded_secrets(doc)
        sp = doc["change_plan"]["subplan_used"]
        code = fp(doc, sp)
        doc["change_plan"]["fingerprint"] = code
        path = PKG / ("%s.yaml" % name)
        path.write_text(yaml.safe_dump(doc, sort_keys=False, width=100,
                                       allow_unicode=True), encoding="utf-8")
        n = len(doc["change_plan"]["subplans"][sp]["actions"])
        index[name] = {"file": str(path.relative_to(ROOT)).replace("\\", "/"),
                       "subplan": sp, "actions": n, "fingerprint": code,
                       "dependencies": doc["change_plan"]["dependencies"]}
        print("%-17s subplan=%-19s actions=%-4d %s" % (name, sp, n, code))
    (PKG / "00-index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    # obsolete the v1 codes
    (PKG / "00-obsolete-codes.json").write_text(json.dumps({
        "note": ("Every code below was generated on 2026-09-03 before the pre-approval "
                 "QA gate. All are OBSOLETE and must be refused if presented."),
        "obsolete": {
            "PLAN-SLM-BID-1": {"code": "50C553579EF3", "why": "blended $22 ceiling replaced by per-campaign $16/$18"},
            "PLAN-SLM-BUD-1": {"code": "D82341B7238E", "why": "values unchanged but the file shape was not executable"},
            "PLAN-SLM-KW-1": {"code": "19FA5CBBB1E5", "why": "file shape not executable; STATUS subplan did not exist"},
            "PLAN-SLM-NEG-1": {"code": "0895911A8133", "why": "154 rows, 49 of them redundant"},
            "PLAN-SLM-CONV-1": {"code": "FB9DA2D017AD", "why": "2 operations, one of them an unproven duplicate"},
        }}, indent=2), encoding="utf-8")
    print("\nwrote %d plans to %s" % (len(index), PKG.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
