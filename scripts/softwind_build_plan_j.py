#!/usr/bin/env python3
"""Build PLAN-J - confirmed geo configuration. LOCAL DRAFT ONLY.

Walter's confirmed instruction (2026-08-26):
  positive  = all VALID New York locations in the geo-union report
  exclusion = Connecticut, United States
  scope     = both Power Washing campaigns
  setting   = keep Presence
  extra     = no other states or countries without evidence or approval

This script writes a local YAML plan and a local JSON model. It performs no
Google Ads write of any kind.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.safety import approval_code                      # noqa: E402

SNAP = ROOT / "clients/softwind-power-washing/snapshots"
PLANS = ROOT / "clients/softwind-power-washing/plans"
CONF = json.loads((SNAP / "geo-confirmed-2026-08-26.json").read_text(encoding="utf-8"))

CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
CT_ID = "21139"

# Geographic containment is NOT modelled by Google's parent_geo_target (proved in
# correction 2: all 16 constants report parent "New York, United States"). These
# relationships are therefore recorded as ADVISORY ONLY and drive no action.
ADVISORY_CONTAINMENT = {
    "9198487": ["1023035", "1023482", "1022719", "1022748"],
    "9198814": ["1022729", "9052792"],
    "9198014": ["1023415"],
}


def main() -> int:
    valid = CONF["ny_validation"]["valid"]
    by_id = {v["id"]: v for v in valid}
    current = CONF["current_location_criteria"]
    settings = CONF["current_geo_target_type_setting"]

    already = {cid: {p["geo_target_constant_id"] for p in current[cid]["positive"]}
               for cid in CAMPAIGNS}
    to_add = {cid: [v["id"] for v in valid if v["id"] not in already[cid]]
              for cid in CAMPAIGNS}

    # ---- guard rails ----------------------------------------------------
    problems = []
    if not CONF["ny_validation"]["all_valid"]:
        problems.append("Not every New York constant validated.")
    if not CONF["connecticut"]["resolved_unambiguously"]:
        problems.append("Connecticut did not resolve to exactly one State constant.")
    for cid, s in settings.items():
        if cid in CAMPAIGNS and s["positive_geo_target_type"] != "PRESENCE":
            problems.append("%s positive geo type is %s, not PRESENCE"
                            % (cid, s["positive_geo_target_type"]))
    for cid in CAMPAIGNS:
        if current[cid]["negative"]:
            problems.append("%s already has %d negative location criteria"
                            % (cid, len(current[cid]["negative"])))
    non_ny = [v for v in valid if ",New York," not in v["canonical_name"] + ","]
    if non_ny:
        problems.append("Non-New-York location in the positive set: %s" % non_ny)

    # ---- actions --------------------------------------------------------
    actions, n = [], 0
    for cid, cname in CAMPAIGNS.items():
        for gid in to_add[cid]:
            n += 1
            v = by_id[gid]
            actions.append({
                "action_id": "R4-J-%02d" % n, "priority": "R4",
                "resource_type": "CAMPAIGN_CRITERION",
                "operation": "CREATE",
                "campaign_id": cid, "campaign_name": cname,
                "current_value": "%d positive location criteria; %s not targeted"
                                 % (len(already[cid]), v["canonical_name"]),
                "proposed_value": {"geo_target_constant_id": gid,
                                   "canonical_name": v["canonical_name"],
                                   "target_type": v["target_type"],
                                   "negative": False},
                "why": "Confirmed by Walter 2026-08-26 as a served New York location.",
                "goes_live_on_creation": True,
                "rollback": "Remove campaign criterion; footprint returns to 8 targets.",
                "object_count": 1})
    for cid, cname in CAMPAIGNS.items():
        n += 1
        actions.append({
            "action_id": "R4-J-%02d" % n, "priority": "R4",
            "resource_type": "CAMPAIGN_CRITERION",
            "operation": "CREATE",
            "campaign_id": cid, "campaign_name": cname,
            "current_value": "0 negative location criteria",
            "proposed_value": {"geo_target_constant_id": CT_ID,
                               "canonical_name": "Connecticut,United States",
                               "target_type": "State", "negative": True},
            "why": "Confirmed exclusion. Blocks Connecticut-present users who would "
                   "otherwise qualify through the 'regularly in' half of Presence.",
            "goes_live_on_creation": True,
            "rollback": "Remove the negative criterion.",
            "object_count": 1})

    plan = {"change_plan": {
        "plan_id": "PLAN-J",
        "plan_title": "Confirmed New York geo footprint + Connecticut exclusion",
        "approval_type": "LIVE_LOCATION_CRITERIA",
        "priority": "R4",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "ads_mutation_count": len(actions),
        "requires_separate_enable_approval": False,
        "live_on_creation_warning": (
            "Location criteria have NO paused state. Every one of these "
            "%d objects begins affecting delivery the moment it is created. "
            "There is no create-paused/readback/enable split available for this "
            "resource type, so this single approval is the only gate."
            % len(actions)),
        "target": {"exact_child_account_name": NAME, "child_customer_id": CID,
                   "manager_customer_id": "3373711342",
                   "exact_service": "Power Washing",
                   "vertical": "similar-local-service"},
        "confirmed_instruction": {
            "source": "Walter Correa, 2026-08-26, confirmation table",
            "positive_targeting": "All valid New York locations in the geo-union report",
            "location_exclusion": "Connecticut, United States",
            "campaign_scope": "Both Power Washing campaigns",
            "location_setting": "Keep Presence (people in or regularly in)",
            "extra_exclusions": "None without evidence or approval"},
        "interpretation_note": (
            "'The attached report' is read as the geo-union analysis delivered in "
            "correction 2 (snapshots/geo-union-2026-08-26.json), which is the only "
            "geo report produced for this account. It contains exactly 16 New York "
            "constants: the 8 currently targeted plus the 8 proposed. All 16 "
            "validated ENABLED. Every one is enumerated below so any mismatch with "
            "the intended list is visible before approval."),
        "validation": {
            "ny_constants_checked": CONF["ny_validation"]["checked"],
            "ny_constants_valid": len(valid),
            "ny_constants_invalid": len(CONF["ny_validation"]["invalid"]),
            "all_positive_targets_are_new_york_us": not non_ny,
            "connecticut_resolved_unambiguously": True,
            "connecticut_geo_target_constant_id": CT_ID,
            "connecticut_reach": CONF["connecticut"]["exact_match"][0]["reach"],
            "no_other_state_or_country_excluded": True,
            "presence_setting_verified_already_correct": {
                cid: settings[cid]["positive_geo_target_type"] for cid in CAMPAIGNS},
            "presence_mutations_required": 0,
            "blocking_problems": problems},
        "presence_finding": (
            "Both campaigns ALREADY report positive_geo_target_type = PRESENCE and "
            "negative_geo_target_type = PRESENCE. The instruction to keep Presence "
            "therefore requires ZERO mutations. It is recorded here as a verified "
            "assertion, not as a change, and the readback QA re-checks it."),
        "advisory_geographic_overlap": {
            "status": "ADVISORY ONLY - NO ACTION TAKEN",
            "why_not_actioned": (
                "Google's parent_geo_target does not model town-contains-hamlet: all "
                "16 constants report parent 'New York, United States'. Containment is "
                "therefore NOT API-provable, and nothing is removed on the strength of "
                "outside geographic knowledge. Overlapping location targets are "
                "resolved by Google as a union; they do not double-serve or "
                "double-charge."),
            "likely_subsumed_by_a_target_being_added": ADVISORY_CONTAINMENT,
            "consequence": (
                "Geo reporting granularity gets noisier - a click in Bay Shore may "
                "report against either Bay Shore or Town of Islip. No delivery or "
                "cost consequence. No removal is proposed; removing criteria was not "
                "requested and would be a destructive action needing its own approval.")},
        "actions": actions,
        "change_counts": {
            "positive_location_criteria_added_campaign_A": len(to_add["24103511039"]),
            "positive_location_criteria_added_campaign_B": len(to_add["24145053510"]),
            "negative_location_criteria_added": len(CAMPAIGNS),
            "geo_target_type_settings_changed": 0,
            "locations_removed": 0,
            "campaigns_changed": 0, "budgets_changed": 0,
            "bidding_settings_changed": 0, "keywords_changed": 0,
            "ads_changed": 0, "assets_changed": 0,
            "google_ads_mutations_total": len(actions)},
        "readback_qa": [
            "Re-read campaign_criterion for both campaigns.",
            "Assert positive LOCATION count == 16 on each campaign.",
            "Assert negative LOCATION count == 1 on each campaign and it is 21139.",
            "Assert campaign.geo_target_type_setting.positive_geo_target_type is "
            "still PRESENCE on both campaigns.",
            "Assert no keyword, budget, bid, ad, asset or schedule changed.",
            "Assert total campaign count is still 2."],
        "risks": [
            "LIVE ON CREATION - no paused state exists for location criteria.",
            "Landing pages name only Islip, West Islip and Dix Hills. Targeting 16 "
            "locations weakens message match for the other 13 and may depress "
            "conversion rate and Quality Score. This is PLAN-F territory and is NOT "
            "fixed by this plan.",
            "Uncapped Maximize Clicks is still in force (PLAN-B on HOLD). A larger "
            "eligible audience with no CPC ceiling can raise average CPC as well as "
            "impressions.",
            "The Connecticut exclusion is largely redundant under Presence targeting "
            "and blocks a small, genuine segment: Connecticut residents who own Long "
            "Island property. Confirmed by Walter and fully reversible."],
        "approval_owner": "Walter Correa",
        "approver_email": "access@greenmarketing.com"}}

    def normalize(p):
        cp = p["change_plan"]
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

    fp = approval_code(normalize(plan))
    out = PLANS / "2026-08-26-plan-j-confirmed-geo.yaml"
    out.write_text(
        "# PLAN-J - CONFIRMED NEW YORK GEO FOOTPRINT + CONNECTICUT EXCLUSION\n#\n"
        "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
        "# LIVE ON CREATION - location criteria have no paused state.\n"
        "# Built from Walter's confirmation table, 2026-08-26.\n\n"
        + yaml.safe_dump(plan, sort_keys=False, width=94, allow_unicode=True),
        encoding="utf-8")

    print("PLAN-J built   fingerprint %s   mutations %d" % (fp, len(actions)))
    print()
    print("BLOCKING PROBLEMS: %s" % (problems or "NONE"))
    print()
    for cid, cname in CAMPAIGNS.items():
        print("%s  %s" % (cid, cname))
        print("   already targeted : %d" % len(already[cid]))
        print("   adding           : %d" % len(to_add[cid]))
        for gid in to_add[cid]:
            v = by_id[gid]
            print("        + %-10s %-12s %s" % (gid, v["target_type"],
                                                v["canonical_name"]))
        print("   excluding        : %s  Connecticut,United States (State)" % CT_ID)
        print("   final footprint  : %d positive, 1 negative"
              % (len(already[cid]) + len(to_add[cid])))
        print()
    print("PRESENCE: %s -> 0 mutations required"
          % {cid: settings[cid]["positive_geo_target_type"] for cid in CAMPAIGNS})
    print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
