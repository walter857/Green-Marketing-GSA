#!/usr/bin/env python3
"""Build the Softwind L&M 2026-09 recovery change packages and fingerprints.

Local only. Writes normalized plan YAML/JSON into 10-change-packages/ and
prints the approval codes. It creates nothing in Google Ads.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PKG = B / "10-change-packages"
TZ = ZoneInfo("America/New_York")
PATIO, PAVERS = "23484806108", "23489296528"

TARGET = {
    "exact_child_account_name": "Softwind Landscape & Masonry - Live",
    "child_customer_id": "2429758629",
    "manager_customer_id": "3373711342",
    "currency": "USD",
    "time_zone": "America/New_York",
    "identity_receipt": "snapshots/identity-gate-2026-09-03-1809.json",
    "work_orders": [
        "work-order-a-patio-construction.yaml (patio construction, campaign Patio)",
        "work-order-b-paver-installation.yaml (paver installation, campaign Pavers)",
    ],
}

ASPHALT_PAUSE = [
    ("local asphalt companies near me", "PHRASE", 132.69, 5, 1.0),
    ("asphalt contractor near me", "PHRASE", 102.01, 4, 0.0),
    ("asphalt paving services near me", "PHRASE", 13.21, 1, 0.0),
    ("asphalt services near me", "PHRASE", 0.00, 0, 0.0),
    ("local asphalt paving companies", "PHRASE", 0.00, 0, 0.0),
    ("local asphalt paving contractors", "PHRASE", 0.00, 0, 0.0),
    ("asphalt and paving companies near me", "PHRASE", 0.00, 0, 0.0),
]


def load(name):
    return json.loads((B / name).read_text(encoding="utf-8"))


def main() -> int:
    PKG.mkdir(parents=True, exist_ok=True)
    snap = load("01-before-snapshot.json")
    perf = load("01b-before-performance.json")
    stamp = datetime.now(TZ).isoformat()
    snap_stamp = snap["snapshot_taken_account_local"]

    # ---------- pacing arithmetic, all inputs shown ----------
    sept = [r for r in perf["account_daily"] if r["date"] >= "2026-09-01"]
    mtd = round(sum(r["cost"] for r in sept), 2)
    complete = [r for r in sept if r["date"] < perf["today_account_local"]]
    avg_complete = round(sum(r["cost"] for r in complete) / len(complete), 2)
    avg_incl_today = round(mtd / len(sept), 2)
    days_in_month = 30
    day_of_month = int(perf["today_account_local"][-2:])
    remaining_days = days_in_month - day_of_month
    remaining_budget = round(max(0.0, 2000.0 - mtd), 2)
    remaining_allowance = round(remaining_budget / remaining_days, 2)
    proj_complete = round(mtd + avg_complete * remaining_days, 2)
    proj_incl = round(mtd + avg_incl_today * remaining_days, 2)
    cur_budgets = {PATIO: 33.0, PAVERS: 33.0}
    new_budgets = {PATIO: 24.0, PAVERS: 32.0}
    proj_new = round(mtd + sum(new_budgets.values()) * remaining_days, 2)
    proj_current = round(mtd + sum(cur_budgets.values()) * remaining_days, 2)

    pacing = {
        "account_month": "2026-09", "timezone": "America/New_York",
        "read_at": perf["read_taken_account_local"],
        "hard_cap_usd": 2000.00,
        "account_mtd_spend": mtd,
        "mtd_days_recorded": len(sept),
        "today_is_partial": True,
        "avg_daily_complete_days_only": avg_complete,
        "avg_daily_including_partial_today": avg_incl_today,
        "remaining_days_excluding_today": remaining_days,
        "remaining_budget": remaining_budget,
        "remaining_daily_allowance": remaining_allowance,
        "current_combined_daily_budget": sum(cur_budgets.values()),
        "projected_at_current_budget": proj_current,
        "projected_at_complete_day_run_rate": proj_complete,
        "projected_at_run_rate_including_today": proj_incl,
        "proposed_combined_daily_budget": sum(new_budgets.values()),
        "projected_at_proposed_budget": proj_new,
        "headroom_for_maximize_clicks_overdelivery": round(2000.0 - proj_new, 2),
        "formulas": {
            "remaining_budget": "max(0, 2000 - account_MTD_spend)",
            "remaining_daily_allowance": "remaining_budget / remaining_days",
            "projected_month_end": "account_MTD_spend + daily_rate * remaining_days",
        },
        "missing_costs_not_included": [
            "agency management fee", "ClickCease subscription",
            "WhatConverts subscription", "landing-page hosting",
        ],
    }
    (B / "08-budget-pacing-plan.csv").write_text(
        "metric,value,formula_or_source\n" + "\n".join(
            '%s,%s,"%s"' % (k, v, pacing["formulas"].get(k, "read or derived"))
            for k, v in pacing.items() if not isinstance(v, (dict, list))),
        encoding="utf-8")

    packages = {}

    # =================== PLAN-SLM-BID-1 ===================
    packages["PLAN-SLM-BID-1"] = {
        "plan_name": "PLAN-SLM-BID-1", "version": 1,
        "operation_class": "BIDDING_STRATEGY_FIELD_CHANGE",
        "approval_label": "APPROVE-BIDDING",
        "generated_at": stamp, "source_snapshot": snap_stamp,
        "target": TARGET,
        "summary": ("Set a CPC bid ceiling on the two Maximize Clicks campaigns. "
                    "Neither campaign has any ceiling today, so nothing bounds the "
                    "price of a click."),
        "actions": [
            {"resource_type": "campaign", "resource_id": cid,
             "resource_name": nm,
             "field": "campaign.target_spend.cpc_bid_ceiling_micros",
             "current_value": None, "current_value_display": "no ceiling set",
             "proposed_value": 22000000, "proposed_value_display": "$22.00",
             "object_count": 1}
            for cid, nm in ((PATIO, "Patio"), (PAVERS, "Pavers"))],
        "evidence": {
            "bidding_strategy_both_campaigns": "TARGET_SPEND (Maximize Clicks)",
            "ceiling_today": "none on either campaign (Paver Sealing, paused, carries $7.50)",
            "realised_avg_cpc_august": {"Patio": 11.29, "Pavers": 21.24},
            "realised_avg_cpc_september_to_date": {"Patio": 13.98, "Pavers": 22.76},
            "single_worst_day": "2026-09-03 Pavers, $83.49 for 3 clicks = $27.83 per click",
            "in_scope_converting_term_avg_cpcs": [2.71, 11.60, 19.98, 30.06],
            "wrong_service_converting_term_avg_cpcs": [13.73, 14.11, 46.54],
            "modelled_retention_at_22": "about 87% of historic clicks",
            "note_on_the_30_dollar_click": (
                "The $30.06 term carried 2 conversion credits on ONE click. Those two "
                "credits are almost certainly the same form submission counted twice by "
                "(web) form_submission and WC Leads - the duplicate PLAN-SLM-CONV-1 "
                "addresses. Treated as one lead, not two."),
        },
        "risk": ("A ceiling lowers auction competitiveness. At $22 it binds Pavers "
                 "(realised $22.76) and barely touches Patio (realised $13.98). "
                 "If lost-impression-share-to-rank rises sharply without a rise in "
                 "click volume, raise it back through a new plan."),
        "rollback": ("Clear campaign.target_spend.cpc_bid_ceiling_micros on both "
                     "campaigns through a new approved plan. No other object changes."),
        "step_down_path": ("This is step 1. After PLAN-SLM-NEG-1 has 14 days of data, "
                           "re-derive the ceiling from post-negative CPC and consider "
                           "$18, then $16. Do not step down before that evidence exists."),
        "validation": "google-ads validate_only on the two campaign mutations",
        "dependencies": [],
        "unchanged": ("budgets, bidding strategy type, networks, locations, keywords, "
                      "negatives, ads, assets, conversion actions, the other four campaigns"),
    }

    # =================== PLAN-SLM-BUD-1 ===================
    packages["PLAN-SLM-BUD-1"] = {
        "plan_name": "PLAN-SLM-BUD-1", "version": 1,
        "operation_class": "CAMPAIGN_BUDGET_CHANGE",
        "approval_label": "APPROVE-BUDGETS",
        "generated_at": stamp, "source_snapshot": snap_stamp,
        "target": TARGET,
        "summary": ("Bring projected September spend under the $2,000 account-wide hard "
                    "cap with headroom for Maximize Clicks overdelivery, cutting Patio "
                    "exposure first."),
        "actions": [
            {"resource_type": "campaign_budget",
             "resource_id": snap["campaigns"][cid]["campaign_budget_resource"].split("/")[-1],
             "campaign_id": cid, "campaign_name": nm,
             "field": "campaign_budget.amount_micros",
             "current_value": int(cur_budgets[cid] * 1e6),
             "current_value_display": "$%.2f/day" % cur_budgets[cid],
             "proposed_value": int(new_budgets[cid] * 1e6),
             "proposed_value_display": "$%.2f/day" % new_budgets[cid],
             "budget_is_explicitly_shared": False,
             "budget_reference_count": 1,
             "object_count": 1}
            for cid, nm in ((PATIO, "Patio"), (PAVERS, "Pavers"))],
        "pacing": pacing,
        "evidence": {
            "cap_is_already_breached_on_paper": (
                "At the current $66.00/day combined budget the projection is $%.2f, "
                "which is $%.2f over the $2,000 cap before any overdelivery."
                % (proj_current, proj_current - 2000)),
            "maximize_clicks_overdelivers": (
                "Observed daily account spend above the $66 combined budget on "
                "2026-08-22 ($103.21) and 2026-09-03 ($122.59, still partial)."),
            "why_patio_is_cut_first": (
                "August Patio spent $949.84 for 1 raw credit at 1.16% CVR. All-time, "
                "Patio is $586 per credit against Pavers' $296 ($457 after removing "
                "Pavers' 3 wrong-service credits)."),
            "counter_evidence_recorded": (
                "Patio buys cheaper clicks ($13.98 vs $22.76 in September), carries a "
                "smaller wrong-service share ($234.01 vs $331.78 of visible spend), and "
                "holds the account's best converting keyword, 'patio pavers contractor' "
                "PHRASE, at 3 credits on $314.39. The cut is deliberately modest for "
                "that reason: Patio keeps 73% of its budget."),
        },
        "risk": ("Lower budgets reduce daily click volume in an account already buying "
                 "only 3-6 clicks a day. This is accepted because the cap is an owner "
                 "instruction and PLAN-SLM-NEG-1 plus PLAN-SLM-BID-1 recover click "
                 "volume per dollar."),
        "rollback": "Restore 33000000 on both budgets through a new approved plan.",
        "validation": "google-ads validate_only on the two campaign_budget mutations",
        "dependencies": [],
        "unchanged": ("bidding, delivery method, the four paused campaigns and their "
                      "budgets, all keywords, negatives, ads, conversions"),
    }

    # =================== PLAN-SLM-KW-1 ===================
    packages["PLAN-SLM-KW-1"] = {
        "plan_name": "PLAN-SLM-KW-1", "version": 1,
        "operation_class": "KEYWORD_STATUS_CHANGE",
        "approval_label": "APPROVE-KEYWORD-PAUSES",
        "generated_at": stamp, "source_snapshot": snap_stamp,
        "target": TARGET,
        "summary": ("Pause the seven ENABLED asphalt keywords added to the Pavers "
                    "campaign on 2026-06-16. Asphalt paving is outside both work "
                    "orders. Paused, never removed, so the rollback is one field."),
        "actions": [],
        "evidence": {
            "total_spend_on_these_seven": 247.91,
            "total_clicks": 10, "total_raw_credits": 1.0,
            "the_one_credit": ("'local asphalt companies near me' produced 1 credit at a "
                               "$14.11 term average CPC. It is an asphalt lead, outside "
                               "both approved services."),
            "why_pause_and_not_remove": ("Pause is one reversible field. Removal is "
                                         "destructive and would need its own approval."),
            "unlocks": ("The 'asphalt' PHRASE campaign negative in PLAN-SLM-NEG-1 is "
                        "blocked while these seven keywords are enabled, because a "
                        "negative may never block the account's own live keyword."),
        },
        "explicitly_not_paused": {
            "paving company near me (PHRASE and EXACT)": (
                "3 credits on $450.02 across 36 clicks - the account's best converting "
                "keyword family. It is ambiguous, not wrong-service. The asphalt "
                "negative underneath it removes the asphalt queries and keeps the rest."),
            "local paving companies (PHRASE)": "WATCH. Same treatment.",
            "local driveway companies / driveway companies near me (PHRASE)": (
                "$158.09 and 0 credits, but driveway paver installation is an "
                "UNRESOLVED service. Held for question SLM-Q5 rather than paused now."),
            "paver driveway installation near me (EXACT and PHRASE)": (
                "Paver-qualified. Held for the same question."),
        },
        "risk": ("Loses the asphalt lead route. That is the intent: asphalt is outside "
                 "both work orders and the client profile."),
        "rollback": "Set status back to ENABLED on the same seven criteria.",
        "validation": "google-ads validate_only on seven ad_group_criterion mutations",
        "dependencies": [],
        "unchanged": ("every other keyword, all negatives, budgets, bids, ads, "
                      "conversions, the Patio campaign entirely"),
    }
    kwidx = {(k["text"], k["match_type"]): k for k in snap["keywords"]
             if k["campaign_id"] == PAVERS and not k["negative"]}
    for text, mt, cost, clicks, conv in ASPHALT_PAUSE:
        k = kwidx.get((text, mt))
        if not k:
            raise SystemExit("keyword not found in snapshot: %r %s" % (text, mt))
        packages["PLAN-SLM-KW-1"]["actions"].append({
            "resource_type": "ad_group_criterion",
            "criterion_id": k["criterion_id"], "ad_group_id": k["ad_group_id"],
            "ad_group_name": k["ad_group_name"], "campaign_id": PAVERS,
            "campaign_name": "Pavers", "keyword_text": text, "match_type": mt,
            "field": "ad_group_criterion.status",
            "current_value": k["status"], "proposed_value": "PAUSED",
            "all_time_cost": cost, "all_time_clicks": clicks,
            "all_time_raw_credits": conv, "object_count": 1,
        })

    # =================== PLAN-SLM-NEG-1 ===================
    negs = list(csv.DictReader((B / "06-negative-plan.csv").open(encoding="utf-8")))
    cov = load("06c-coverage.json")
    fam = defaultdict(lambda: [0, 0.0, 0.0])
    for n in negs:
        f = fam[n["family"]]
        f[0] += 1; f[1] += float(n["blocks_cost"]); f[2] += float(n["blocks_conversions"])
    packages["PLAN-SLM-NEG-1"] = {
        "plan_name": "PLAN-SLM-NEG-1", "version": 1,
        "operation_class": "CAMPAIGN_NEGATIVE_KEYWORD_CREATE",
        "approval_label": "APPROVE-NEGATIVES",
        "generated_at": stamp, "source_snapshot": snap_stamp,
        "target": TARGET,
        "summary": ("Create %d campaign-level negative keywords across Patio and Pavers "
                    "covering twelve confirmed wrong-service families. All PHRASE. No "
                    "bare noun the account sells." % len(negs)),
        "object_count": len(negs),
        "placement": "CAMPAIGN level on 23484806108 and 23489296528 only",
        "match_types_used": sorted({n["match_type"] for n in negs}),
        "families": {k: {"negatives": v[0], "visible_cost_blocked": round(v[1], 2),
                         "raw_credits_blocked": round(v[2], 1)}
                     for k, v in sorted(fam.items(), key=lambda x: -x[1][1])},
        "coverage": cov,
        "actions_file": "06-negative-plan.csv",
        "actions_digest": approval_code({"rows": [
            {k: n[k] for k in sorted(n)} for n in negs]}, 16),
        "collision_testing": {
            "tested_against_own_keyword_texts": "all 461 positive keywords in Patio and Pavers, ENABLED and PAUSED",
            "tested_against_protected_search_terms": "every KEEP, WATCH, UNRESOLVED and UNCLASSIFIED term in the corpus",
            "tested_against_existing_negatives": "1,452 (Patio) / 1,448 (Pavers) already blocking, for redundancy",
            "google_limits_checked": "<=10 words and <=80 characters per negative",
            "agency_protected_terms_never_used": ["near me", "quote", "price", "pricing",
                                                  "cost", "best", "hire", "local", "emergency"],
            "candidates_rejected": 4,
            "rejected_file": "06b-negative-rejected.csv",
        },
        "why_this_is_needed_despite_1452_existing_negatives": (
            "Every existing campaign negative on Patio and Pavers is BROAD (420 and 416), "
            "and the linked 'General List' shared set is 1,109 BROAD of 1,111. A BROAD "
            "negative only blocks a query containing ALL of its words, so 'asphalt paving' "
            "never blocked 'asphalt contractor near me'. This plan is PHRASE throughout."),
        "raw_credits_this_plan_blocks": 3.0,
        "note_on_blocked_credits": (
            "The plan blocks 3 historic credits on purpose: one sealcoating, one asphalt "
            "and one paver-sealing term. All three are outside both work orders. Paver "
            "sealing has its own PAUSED campaign in this account (23914857298)."),
        "risk": ("A negative that is too broad blocks real demand. Mitigated by the "
                 "collision test above: any candidate touching a live or paused own "
                 "keyword, or any protected search term, was rejected rather than softened."),
        "rollback": "Remove the created campaign_criterion rows. No other object changes.",
        "validation": "local preflight then google-ads validate_only in batches",
        "dependencies": ["PLAN-SLM-KW-1 must execute and read back FIRST. The 'asphalt' "
                         "PHRASE negative on Pavers collides with the seven keywords that "
                         "plan pauses."],
        "unchanged": ("all positive keywords, the 1,452 existing negatives, the shared "
                      "sets and their links, the 235 ClickCease IP blocks per campaign, "
                      "budgets, bids, ads, assets, conversions, the other four campaigns"),
    }

    # =================== PLAN-SLM-CONV-1 ===================
    ca = {c["id"]: c for c in snap["conversion_actions"]}
    packages["PLAN-SLM-CONV-1"] = {
        "plan_name": "PLAN-SLM-CONV-1", "version": 1,
        "operation_class": "CONVERSION_ACTION_PRIMARY_FLAG_CHANGE",
        "approval_label": "APPROVE-CONVERSIONS",
        "generated_at": stamp, "source_snapshot": snap_stamp,
        "target": TARGET,
        "summary": ("Demote the two duplicate primary conversion actions. Twelve actions "
                    "are primary today and seven of them count into the Conversions "
                    "column; two of those seven duplicate another."),
        "actions": [
            {"resource_type": "conversion_action", "resource_id": "7461619140",
             "resource_name": "Softwind Submit lead form",
             "type": "WEBPAGE", "category": "SUBMIT_LEAD_FORM",
             "field": "conversion_action.primary_for_goal",
             "current_value": True, "proposed_value": False, "object_count": 1,
             "reason": ("Duplicates 'Softwind Landscape & Masonry (web) form_submission' "
                        "(7480764700, GA4). Both fire on the same submission and both "
                        "count: Mar 1/3, Apr 3/5, May 1/1, Jun 1/1, Jul 2/2, Aug 0/1. The "
                        "GA4 action is the more complete of the two and stays primary."),
             "verified_not_required_by_whatconverts": (
                 "WhatConverts writes to WC Leads (UPLOAD_CLICKS, 7635680357) and WC Call "
                 "(UPLOAD_CALLS, 7635680543), not to either web form action.")},
            {"resource_type": "conversion_action", "resource_id": "7508686781",
             "resource_name": "Calls from ads (1)",
             "type": "AD_CALL", "category": "PHONE_CALL_LEAD",
             "field": "conversion_action.primary_for_goal",
             "current_value": True, "proposed_value": False, "object_count": 1,
             "reason": ("Duplicates 'Calls from ads' (7461572537). Both are AD_CALL / "
                        "PHONE_CALL_LEAD and both are primary. (1) recorded Feb-Jun and "
                        "has recorded nothing since June 2026; 7461572537 has carried "
                        "every call credit since. In June 2026 BOTH fired - 6 and 1 - "
                        "which is a duplicate-primary window that must not recur."),
             "counting_type_conflict": ("7461572537 is ONE_PER_CLICK at 30 seconds; "
                                        "7508686781 is MANY_PER_CLICK at 60 seconds.")},
        ],
        "held_for_a_later_package": {
            "WC Leads (7635680357)": (
                "Also primary, category CONTACT, and a WhatConverts upload of the same "
                "form submissions. It is a third credit for one lead. It is NOT demoted "
                "now because it currently carries the only conversion credit the Patio "
                "campaign recorded in August, and its intended replacement - the GA4 form "
                "action - last fired 2026-08-08. Demote it only after the WhatConverts "
                "repair is verified."),
            "WC Call (7635680543)": (
                "Primary but has recorded ZERO conversions and zero all_conversions, in "
                "every month, on every campaign. all_conversions is not gated by goal "
                "biddability, so a zero there proves no event was ever recorded. The "
                "upload path has never worked. Fix the path before touching the flag."),
            "Calls from ads minimum duration": (
                "7461572537 counts a call at 30 seconds; every other action on the "
                "account uses 60. Raising it to 60 changes what counts as a lead and "
                "breaks comparability with history, so it needs the owner's answer - "
                "question SLM-Q7."),
        },
        "explicitly_left_alone": {
            "the five Google-hosted local actions": (
                "Clicks to call, Directions, Menu views, Other engagements and Website "
                "visits are primary_for_goal=true but include_in_conversions_metric=false, "
                "and their customer conversion goals (PAGE_VIEW, GET_DIRECTIONS, "
                "CONTACT/GOOGLE_HOSTED, ENGAGEMENT/GOOGLE_HOSTED) are all biddable=false. "
                "They are already correctly isolated as diagnostics. 120 'Other "
                "engagements' in Jul-Aug never entered the Conversions column. No change."),
            "include_in_conversions_metric": (
                "Not touched anywhere. The field is deprecated and effectively immutable; "
                "primary_for_goal plus the goal layer is the real gate."),
        },
        "risk": ("Reported Conversions will fall. That is the point - the column has been "
                 "counting one lead more than once. Historic months are NOT restated: a "
                 "credit already counted stays in the historical column forever, so "
                 "before/after comparisons must be drawn at the change date."),
        "rollback": "Set primary_for_goal back to true on the same two action IDs.",
        "validation": "google-ads validate_only on two conversion_action mutations",
        "dependencies": [],
        "unchanged": ("no conversion action is deleted, renamed, recategorised or "
                      "restatused; counting type, attribution model, lookback windows, "
                      "value settings and call durations are all untouched; campaign and "
                      "customer conversion goals are untouched"),
    }

    # ---------------- emit ----------------
    print("=" * 78)
    print("SOFTWIND LANDSCAPE & MASONRY - 2026-09 PATIO/PAVERS RECOVERY")
    print("account %s / %s" % (TARGET["exact_child_account_name"],
                               TARGET["child_customer_id"]))
    print("=" * 78)
    index = {}
    for name in ("PLAN-SLM-CONV-1", "PLAN-SLM-BID-1", "PLAN-SLM-BUD-1",
                 "PLAN-SLM-KW-1", "PLAN-SLM-NEG-1"):
        p = packages[name]
        assert_no_embedded_secrets(p)
        fp = approval_code(p)
        p["fingerprint"] = fp
        objs = p.get("object_count") or sum(a.get("object_count", 1) for a in p["actions"])
        (PKG / ("%s.json" % name)).write_text(
            json.dumps(p, indent=2, default=str), encoding="utf-8")
        index[name] = {"fingerprint": fp, "objects": objs,
                       "label": p["approval_label"],
                       "operation_class": p["operation_class"],
                       "dependencies": p["dependencies"]}
        print("\n%-16s %-28s objects=%-4d  %s" % (name, p["operation_class"], objs, fp))
        print("   APPROVE %s %s FOR %s" % (p["approval_label"], fp,
                                           TARGET["child_customer_id"]))
        if p["dependencies"]:
            print("   depends on: %s" % p["dependencies"][0][:70])
    (PKG / "00-index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print("\nwrote %d packages to %s" % (len(index), PKG.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
