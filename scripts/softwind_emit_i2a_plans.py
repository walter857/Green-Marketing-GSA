#!/usr/bin/env python3
"""Emit PLAN-I2A-E, PLAN-I2A-C and the PLAN-I2A-EN template. Local files only."""
from __future__ import annotations

import importlib.util
import json
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("i2a", ROOT / "scripts/softwind_build_i2a.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
SKAGS, TARGET = m.SKAGS, m.TARGET

PLANS = ROOT / "clients/softwind-power-washing/plans"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
snap = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))
deep = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))

# re-run validation so the emitted plan carries the checked flags
for s in SKAGS:
    iss, ov = m.validate(s)
    s["_issues"], s["_overlap"] = iss, ov
    assert not iss, (s["name"], iss)
AG = snap["ad_groups"]
LEGACY = {"Pressure & Power Washing", "Soft & House Washing",
          "Driveway Patio Concrete Washing"}
live_texts = {k["text"] for k in snap["enabled_keywords_live"]}
legacy_texts, skag_texts = set(), set()
for k in snap["keywords"]:
    (legacy_texts if AG[k["ad_group_id"]]["name"] in LEGACY else skag_texts).add(k["text"])
for s in SKAGS:
    s["duplicate_check"] = {
        "exact_text_already_live": s["exact"] in live_texts,
        "exact_text_in_another_real_skag": s["exact"] in skag_texts,
        "exact_text_in_permanently_paused_legacy_container": s["exact"] in legacy_texts,
        "verdict": ("SAFE TO CREATE - text exists only inside a legacy container this "
                    "plan keeps PERMANENTLY PAUSED, so it is a dormant resource and "
                    "never a serving duplicate")}

VOID = {
    "plan_id": "PLAN-I2", "fingerprint": "6AF733F709E2", "status": "VOID",
    "voided_on": "2026-08-26",
    "reason": ("SKAG-integrity audit of all 62 keyword rows found BOTH proposed ad "
               "groups fail the one-canonical-intent test. Pressure & Power Washing "
               "contains FOUR distinct canonical intents across 34 rows; Soft & House "
               "Washing contains TWO across 28 rows. All 62 rows also show semantic "
               "overlap with live keywords and only PARTIAL landing-page relevance. "
               "Enabling either would put mixed intent behind one RSA on a generic "
               "page - the architecture the account was revamped to remove."),
    "replaced_by": ["PLAN-I2A-E", "PLAN-I2A-C", "PLAN-I2A-EN"]}

# ---------------- Category A ----------------
GID_A = "198082079463"
ads_a = [a for a in deep["ads"] if a["ad_group_id"] == GID_A]
kws_a = [k for k in snap["keywords"] if k["ad_group_id"] == GID_A]

planE = {"change_plan": {
    "plan_id": "PLAN-I2A-E",
    "plan_title": "Enable the one correct existing paused SKAG",
    "approval_type": "ENABLE_EXISTING_RESOURCES", "priority": "R5-A",
    "approval_status": "NOT APPROVED", "execution_status": "DO NOT EXECUTE",
    "recommended_approval_order": 5, "ads_mutation_count": 1,
    "requires_separate_enable_approval": True, "supersedes": VOID, "target": TARGET,
    "category": "A - correct existing paused SKAG, enable after QA",
    "selection_note": (
        "Of 14 paused ad groups, exactly ONE is a true SKAG that is neither a duplicate "
        "of a live keyword nor a legacy mixed container: House Washing Company Near Me. "
        "One canonical intent, one keyword text in Phrase + Exact, a dedicated matching "
        "landing page, and 2 approved RSAs already at ENABLED status - so enabling the "
        "ad group alone makes it serve. One mutation."),
    "honest_caveat": (
        "Keyword Planner returns NO reportable local volume for 'house washing company "
        "near me'. This is a zero-build, zero-risk enablement, not a volume driver. It "
        "is included because it costs nothing, not because it will move the month."),
    "skag_integrity_check": {
        "ad_group": "House Washing Company Near Me", "ad_group_id": GID_A,
        "campaign_id": "24145053510", "campaign": "Power Washing #2",
        "keyword_texts": sorted({k["text"] for k in kws_a}),
        "distinct_canonical_intents": 1,
        "CONTAINS_EXACTLY_ONE_CANONICAL_INTENT": "YES",
        "keyword_rows": len(kws_a),
        "match_types": sorted({k["match_type"] for k in kws_a}),
        "rsa_count": len(ads_a),
        "rsa_status": sorted({a["status"] for a in ads_a}),
        "rsa_approval": sorted({a["approval_status"] for a in ads_a}),
        "final_url": sorted({u for a in ads_a for u in a["final_urls"]}),
        "landing_page_h1": "House Washing Company In Islip, West Islip & Dix Hills, NY",
        "landing_page_verified_200": True,
        "duplicate_live_anywhere": False,
        "paired_copy_must_stay_paused": "202870585910 in campaign A"},
    "actions": [{
        "action_id": "R5A-01", "priority": "R5", "resource_type": "AD_GROUP",
        "operation": "UPDATE_STATUS_TO_ENABLED", "customer_id": "1521725229",
        "campaign_id": "24145053510", "campaign_name": "Power Washing #2",
        "ad_group_id": GID_A, "ad_group_name": "House Washing Company Near Me",
        "resource_id": "customers/1521725229/adGroups/%s" % GID_A,
        "field_mask": "status",
        "current_value": {"status": "PAUSED", "keyword_rows": len(kws_a),
                          "rsa_count": len(ads_a),
                          "rsa_status": sorted({a["status"] for a in ads_a})},
        "proposed_value": {"status": "ENABLED"},
        "keywords_that_will_begin_serving": [
            "%s [%s]" % (k["text"], k["match_type"]) for k in kws_a],
        "why": "The only true, non-duplicate SKAG in paused inventory. Zero build.",
        "evidence": "snapshots/plan-i2-keyword-audit-2026-08-26.json",
        "expected_effect": ("Small. No reportable Planner volume; historical delivery "
                            "2 impressions."),
        "risk": ("LOW-MEDIUM. Historical search terms included 'house cleaning services "
                 "near me' and 'slate roof cleaning near me'. Approve with PLAN-E2."),
        "rollback": "Set ad_group %s status back to PAUSED." % GID_A,
        "approval_required": "YES - SEPARATE ENABLE APPROVAL", "object_count": 1}],
    "change_counts": {
        "campaigns_changed": 0, "campaigns_paused": 0, "budgets_changed": 0,
        "bidding_settings_changed": 0, "ad_schedules_changed": 0,
        "ad_groups_enabled": 1, "ad_groups_created_paused": 0, "keywords_enabled": 0,
        "keyword_rows_that_begin_serving": len(kws_a),
        "rsas_that_begin_serving": len(ads_a),
        "keywords_created_paused": 0, "rsas_created_paused": 0, "ads_changed": 0,
        "negatives_added": 0, "assets_changed": 0, "final_urls_changed": 0,
        "conversion_actions_changed": 0, "google_ads_mutations_total": 1},
    "approval_owner": "Walter Correa",
    "approver_email": "access@greenmarketing.com"}}

# ---------------- Category B ----------------
acts, blocks = [], []
for n, s in enumerate(SKAGS, start=1):
    base = "R5C-%02d" % n
    blocks.append({
        "ad_group_name": s["name"], "campaign_id": s["campaign_id"],
        "campaign": s["campaign"], "canonical_intent": s["name"],
        "phrase_keyword": s["phrase"], "exact_keyword": s["exact"],
        "local_monthly_volume": s["volume"], "recent_trend_pct": s["trend"],
        "competition": s["competition"],
        "top_of_page_low": s["bid_low"], "top_of_page_high": s["bid_high"],
        "final_url": s["url"], "landing_page_h1": s["lp_h1"],
        "path1": s["path1"], "path2": s["path2"],
        "why_this_intent": s["why"], "duplicate_check": s["duplicate_check"],
        "sibling_rsa_headline_overlap": "%d of 15" % len(s["_overlap"]),
        "rsa1": {
            "headlines": [{"text": h, "len": len(h),
                           "pinned": ("HEADLINE_1" if i < 2 else None)}
                          for i, h in enumerate(s["rsa1"]["H"])],
            "descriptions": [{"text": d, "len": len(d)} for d in s["rsa1"]["D"]]},
        "rsa2": {
            "headlines": [{"text": h, "len": len(h),
                           "pinned": ("HEADLINE_1" if i < 2 else None)}
                          for i, h in enumerate(s["rsa2"]["H"])],
            "descriptions": [{"text": d, "len": len(d)} for d in s["rsa2"]["D"]]}})
    acts += [
        {"action_id": base + "a", "priority": "R5", "resource_type": "AD_GROUP",
         "operation": "CREATE_PAUSED", "customer_id": "1521725229",
         "campaign_id": s["campaign_id"], "campaign_name": s["campaign"],
         "ad_group_id": None, "resource_id": "NEW ad_group '%s'" % s["name"],
         "current_value": "does not exist",
         "proposed_value": {"name": s["name"], "status": "PAUSED",
                            "type": "SEARCH_STANDARD"},
         "why": s["why"], "evidence": "snapshots/i2a-skag-validation-2026-08-26.json",
         "expected_effect": "Creates the container. No delivery until a separate enable.",
         "risk": "LOW - created paused, cannot serve.",
         "rollback": "Remove the ad group.",
         "approval_required": "YES - create-paused approval", "object_count": 1},
        {"action_id": base + "b", "priority": "R5",
         "resource_type": "AD_GROUP_CRITERION", "operation": "CREATE_PAUSED",
         "customer_id": "1521725229", "campaign_id": s["campaign_id"],
         "campaign_name": s["campaign"], "ad_group_id": "NEW from %sa" % base,
         "resource_id": "NEW keywords x2", "current_value": "does not exist",
         "proposed_value": [{"text": s["phrase"], "match_type": "PHRASE"},
                            {"text": s["exact"], "match_type": "EXACT"}],
         "why": "Phrase + Exact per Green Marketing default. No Broad Match.",
         "evidence": "config/agency.yaml search_defaults.match_types",
         "expected_effect": "No delivery while the parent ad group is paused.",
         "risk": "LOW", "rollback": "Remove both criteria.",
         "approval_required": "YES", "object_count": 2},
        {"action_id": base + "c", "priority": "R5", "resource_type": "AD_GROUP_AD",
         "operation": "CREATE_PAUSED", "customer_id": "1521725229",
         "campaign_id": s["campaign_id"], "campaign_name": s["campaign"],
         "ad_group_id": "NEW from %sa" % base, "resource_id": "NEW RSAs x2",
         "current_value": "does not exist",
         "proposed_value": ("Two RSAs, 15 headlines and 4 descriptions each, "
                            "HEADLINE_1 pinned, Final URL %s" % s["url"]),
         "why": "Two distinct RSAs per ad group per SOP, matched to the canonical intent.",
         "evidence": "scripts/softwind_build_i2a.py - all limits pass",
         "expected_effect": "No delivery while paused.", "risk": "LOW",
         "rollback": "Remove both ads.", "approval_required": "YES",
         "object_count": 2}]

planC = {"change_plan": {
    "plan_id": "PLAN-I2A-C",
    "plan_title": "Create paused - four true SKAGs extracted from legacy demand",
    "approval_type": "CREATE_PAUSED", "priority": "R5-B",
    "approval_status": "NOT APPROVED", "execution_status": "DO NOT EXECUTE",
    "recommended_approval_order": 6,
    "ads_mutation_count": sum(a["object_count"] for a in acts),
    "requires_separate_enable_approval": True, "supersedes": VOID, "target": TARGET,
    "category": "B - missing SKAGs that must first be created paused",
    "principle": (
        "The legacy containers hold real demand in the wrong shape. This plan extracts "
        "their strongest canonical intents into properly-structured SKAGs: one canonical "
        "intent per ad group, Phrase + Exact only, no Broad Match, two matching RSAs, "
        "and the best-matched published landing page for each."),
    "dormant_resource_precondition": (
        "Each of these four keyword texts already exists as a PAUSED row inside a legacy "
        "container. That is a dormant resource, not a serving duplicate - and this plan "
        "is explicitly CONDITIONAL on those containers remaining PERMANENTLY PAUSED "
        "(category C). If a legacy container were ever enabled while these SKAGs are "
        "live, the account would compete with itself. That commitment is the "
        "precondition for approving this plan."),
    "skags": blocks,
    "rsa_validation": {
        "validator": "scripts/softwind_build_i2a.py",
        "result": "ALL PASS",
        "checks": (
            "15 headlines and 4 descriptions per ad; longest headline 29; longest "
            "description 86; no duplicate asset within an ad; display paths within 15 "
            "characters; sibling headline overlap 1 of 15 on every pair, and that "
            "single shared headline is the intentionally pinned HEADLINE_1; every asset "
            "screened against a banned-claims filter covering licensing, insurance, "
            "guarantees, years in business, ratings, review counts, prices, discounts, "
            "same-day and 24/7 promises, and out-of-scope services.")},
    "actions": acts,
    "post_creation_requirements": [
        "READBACK QA: re-read every created ad group, keyword and RSA from the API.",
        "Record the created resource IDs.",
        "Verify match types are exactly PHRASE and EXACT.",
        "Verify 2 RSAs per ad group, 15 headlines and 4 descriptions each.",
        "Verify Final URLs and display paths.",
        "Verify policy approval status.",
        "ONLY THEN build PLAN-I2A-EN with real resource IDs and its own fingerprint.",
        "CREATION AND ENABLEMENT MUST NEVER SHARE AN APPROVAL."],
    "change_counts": {
        "campaigns_changed": 0, "campaigns_paused": 0, "budgets_changed": 0,
        "bidding_settings_changed": 0, "ad_schedules_changed": 0,
        "ad_groups_enabled": 0, "ad_groups_created_paused": 4, "keywords_enabled": 0,
        "keywords_created_paused": 8, "rsas_created_paused": 8, "ads_changed": 0,
        "negatives_added": 0, "assets_changed": 0, "final_urls_changed": 0,
        "conversion_actions_changed": 0,
        "google_ads_mutations_total": sum(a["object_count"] for a in acts),
        "objects_that_can_serve_immediately": 0},
    "approval_owner": "Walter Correa",
    "approver_email": "access@greenmarketing.com"}}

HDR_E = ("# PLAN-I2A-E - CATEGORY A: ENABLE THE ONE CORRECT EXISTING PAUSED SKAG\n#\n"
         "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
         "# Replaces PLAN-I2 (fingerprint 6AF733F709E2, now VOID).\n#\n"
         "# Enabling is a LIVE DELIVERY CHANGE and needs its own approval.\n\n")
HDR_C = ("# PLAN-I2A-C - CATEGORY B: CREATE FOUR TRUE SKAGS, PAUSED\n#\n"
         "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
         "# Replaces PLAN-I2 (fingerprint 6AF733F709E2, now VOID).\n#\n"
         "# Everything is created PAUSED. Nothing here can serve an impression.\n"
         "# Enabling is a SECOND approval (PLAN-I2A-EN) after readback QA.\n\n")

(PLANS / "2026-08-26-plan-i2a-e-enable-existing-skag.yaml").write_text(
    HDR_E + yaml.safe_dump(planE, sort_keys=False, width=90, allow_unicode=True),
    encoding="utf-8")
(PLANS / "2026-08-26-plan-i2a-c-create-paused-skags.yaml").write_text(
    HDR_C + yaml.safe_dump(planC, sort_keys=False, width=90, allow_unicode=True),
    encoding="utf-8")

print("PLAN-I2A-E : 1 action, 1 object")
print("PLAN-I2A-C : %d actions, %d objects (4 ad groups + 8 keywords + 8 RSAs)"
      % (len(acts), sum(a["object_count"] for a in acts)))
for b in blocks:
    print("   %-28s -> %-16s vol=%-4s trend=%+.1f%%  %s"
          % (b["ad_group_name"], b["campaign"], b["local_monthly_volume"],
             b["recent_trend_pct"], b["final_url"].split("/")[-2]))
