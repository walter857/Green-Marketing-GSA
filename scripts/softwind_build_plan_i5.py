#!/usr/bin/env python3
"""Build PLAN-I5 - create-paused expansion, re-scoped against PLAN-I2."""
from __future__ import annotations

import json
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
PLANS = ROOT / "clients/softwind-power-washing/plans"

e1 = yaml.safe_load((PLANS / "2026-08-26-plan-e1-create-paused-skags.yaml")
                    .read_text(encoding="utf-8"))["change_plan"]
inv = json.loads((SNAP / "rescue-inventory-ranking-2026-08-26.json").read_text(encoding="utf-8"))

# Only the Pressure Washing Near Me SKAG survives re-scoping.
keep = [a for a in e1["actions"] if a["action_id"] in ("P1-E01", "P1-E02", "P1-E03")]
renamed = []
for i, a in enumerate(keep, start=1):
    b = dict(a)
    b["action_id"] = "R5-I5-%02d" % i
    b["priority"] = "R5"
    renamed.append(b)

rsas = [r for r in e1["rsas"] if r["ad_group"] == "Pressure Washing Near Me"]

plan = {"change_plan": {
    "plan_id": "PLAN-I5",
    "plan_title": "Create paused - Pressure Washing Near Me (single SKAG)",
    "approval_type": "CREATE_PAUSED",
    "priority": "R5",
    "approval_status": "NOT APPROVED",
    "execution_status": "DO NOT EXECUTE",
    "recommended_approval_order": 6,
    "ads_mutation_count": sum(a["object_count"] for a in renamed),
    "requires_separate_enable_approval": True,
    "supersedes": {
        "plan_id": "PLAN-E1", "fingerprint": "40385B68584E",
        "status": "SUPERSEDED - NOT VOID",
        "reason": (
            "PLAN-E1 proposed TWO new SKAGs: Pressure Washing Near Me and House "
            "Washing Near Me. Re-checked on 2026-08-26 against PLAN-I2. The House "
            "Washing Near Me SKAG is now REDUNDANT: the keyword text 'house washing "
            "near me' lives inside the paused legacy Soft & House Washing ad group, "
            "which PLAN-I2 proposes to ENABLE. Enabling that group delivers the same "
            "40/month text with ZERO build and no create-paused/enable cycle, so "
            "building a duplicate SKAG for it would put two ad groups in the same "
            "campaign auction for one query. PLAN-E1's fingerprint is unchanged and "
            "it remains valid if PLAN-I2 is rejected."),
    },
    "target": e1["target"],
    "rescope_decision": {
        "checked": "2026-08-26 against fresh Keyword Planner and PLAN-I2 selection",
        "kept": [{
            "skag": "Pressure Washing Near Me",
            "keyword": "pressure washing near me",
            "local_monthly_volume": 70,
            "competition": "HIGH",
            "top_of_page_low": 8.75,
            "top_of_page_high": 24.53,
            "why_still_needed": (
                "Verified against every live AND every paused keyword text in both "
                "campaigns on 2026-08-26. The exact text 'pressure washing near me' "
                "appears NOWHERE. The legacy Pressure & Power Washing group that "
                "PLAN-I2 enables contains pressure washing service / company / "
                "contractor / estimate / quote / long island - all non-'near me' "
                "query shapes. A Phrase keyword \"pressure washing service\" does not "
                "match a query lacking the word 'service'. The gap is real and "
                "survives PLAN-I2."),
            "account_evidence": (
                "Search terms using 'pressure wash' phrasing have produced 15 "
                "impressions and ZERO clicks - 0% CTR - while 'power wash' phrasing "
                "runs 7.25%. Eleven of those fifteen were served by a power-washing "
                "ad group showing power-washing copy. This is a copy-match failure, "
                "not only a coverage gap."),
        }],
        "dropped": [{
            "skag": "House Washing Near Me",
            "keyword": "house washing near me",
            "local_monthly_volume": 40,
            "recent_trend_pct": -73.3,
            "why_dropped": (
                "Delivered faster and at zero build cost by PLAN-I2's enablement of "
                "the Soft & House Washing legacy group, which already contains this "
                "exact text with an approved RSA. Building a parallel SKAG would "
                "create an intra-campaign duplicate. Fresh Planner also shows this "
                "term's recent trend at -73.3%, so it is a weaker opportunity than "
                "it looked on 2026-08-25."),
            "reinstate_if": "PLAN-I2 is rejected, in which case PLAN-E1 stands as written.",
        }],
    },
    "rsa_validation": e1["rsa_validation"],
    "rsas": rsas,
    "cross_campaign_check": {
        "keyword": "pressure washing near me",
        "campaign_A_24103511039": "No live or paused keyword text matches. After "
                                  "PLAN-I2 enables Pressure & Power Washing into A, "
                                  "still no exact match - that group has no 'near me' text.",
        "campaign_B_24145053510": "No live or paused keyword text matches. Proposed here.",
        "currently_enabled_duplicate": False,
        "paused_duplicate": False,
        "recommended_ownership": "campaign 24145053510 (Power Washing #2) - EXCLUSIVE",
        "ownership_rationale": (
            "Campaign B owns the pressure / residential / house / soft washing family. "
            "Placing it in B keeps the pressure intent in one campaign. Note PLAN-I2 "
            "places the legacy Pressure & Power Washing group in campaign A; those "
            "are non-'near me' texts, so the two do not compete for the same query, "
            "but this pairing should be reviewed at the first pacing checkpoint."),
        "residual_risk": (
            "MEDIUM against campaign B's own live 'residential pressure washing near "
            "me' SKAG, which shares the substring. Intra-campaign, resolved by Ad "
            "Rank, acceptable."),
    },
    "actions": renamed,
    "post_creation_requirements": [
        "READBACK QA: re-read the ad group, both keywords and both RSAs from the API.",
        "Provide the created resource IDs.",
        "Verify keyword match types are exactly PHRASE and EXACT.",
        "Verify 2 RSAs present.",
        "Verify 15 headlines and 4 descriptions on each RSA.",
        "Verify Final URL is https://offer.softwindli.com/residential-pressure-washing/",
        "Verify policy approval status.",
        "ONLY THEN build a separate ENABLEMENT fingerprint. Creation and enablement "
        "must never share an approval.",
    ],
    "timing_warning": (
        "Create-paused plus readback QA plus a separate enable approval cannot "
        "realistically complete before 2026-08-28. That leaves at most 4 of the 6 "
        "remaining days of delivery, which is why this sits at R5 rather than higher. "
        "If the month-end objective is the priority, PLAN-I1, I2 and I3 deliver more "
        "spend sooner than this plan can."),
    "change_counts": {
        "campaigns_changed": 0, "campaigns_paused": 0, "budgets_changed": 0,
        "bidding_settings_changed": 0, "ad_schedules_changed": 0,
        "ad_groups_enabled": 0, "ad_groups_created_paused": 1,
        "keywords_enabled": 0, "keywords_created_paused": 2,
        "rsas_created_paused": 2, "ads_changed": 0, "negatives_added": 0,
        "assets_changed": 0, "final_urls_changed": 0,
        "conversion_actions_changed": 0,
        "google_ads_mutations_total": sum(a["object_count"] for a in renamed),
        "objects_that_can_serve_immediately": 0,
    },
    "approval_owner": e1["approval_owner"],
    "approver_email": e1["approver_email"],
}}

HDR = """# PLAN-I5 - CREATE PAUSED: PRESSURE WASHING NEAR ME
#
# STATUS: NOT APPROVED. DO NOT EXECUTE.
#
# SUPERSEDES PLAN-E1 in the recommendation order (PLAN-E1 is NOT void - its
# fingerprint 40385B68584E is unchanged and it stands if PLAN-I2 is rejected).
#
# Re-scoped from two SKAGs down to one. The House Washing Near Me SKAG is
# redundant once PLAN-I2 enables the legacy group that already contains that
# exact keyword text.
#
# Everything here is created PAUSED. Nothing in this plan can serve an
# impression. Enabling is a SECOND approval after readback QA.

"""
p = PLANS / "2026-08-26-plan-i5-create-paused-expansion.yaml"
p.write_text(HDR + yaml.safe_dump(plan, sort_keys=False, width=90, allow_unicode=True),
             encoding="utf-8")
print("wrote", p)
print("  actions:", len(renamed), "objects:", sum(a["object_count"] for a in renamed))
print("  kept:   Pressure Washing Near Me (70/mo)")
print("  dropped: House Washing Near Me - delivered by PLAN-I2 instead")
