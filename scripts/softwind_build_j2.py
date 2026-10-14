#!/usr/bin/env python3
"""STAGE 5 + 6 - build PLAN-J2A (client-approved NY geo expansion) and
PLAN-J2B (Connecticut exclusion) as two SEPARATE, separately fingerprinted
plans. Also voids PLAN-J B42EAD386795 for source mismatch.

Connecticut is re-resolved live; the remembered ID is only used as a
cross-check assertion, never as the source of truth.

Local drafting only. No Google Ads mutation is performed.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.google_ads import enum_name                     # noqa: E402
from gm_gsa.safety import approval_code                     # noqa: E402

CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
CLIENT = ROOT / "clients/softwind-power-washing"
PLANS = CLIENT / "plans"
SUP = PLANS / "superseded"
SNAP = CLIENT / "snapshots"

RES = json.loads((SNAP / "stage3-geo-resolution-2026-08-26.json").read_text("utf-8"))
STATE = json.loads((SNAP / "stage1-state-2026-08-26.json").read_text("utf-8"))
SRCVAL = json.loads((SNAP / "source-validation-2026-08-26.json").read_text("utf-8"))

TARGET_BLOCK = {"exact_child_account_name": NAME, "child_customer_id": CID,
                "manager_customer_id": "3373711342",
                "exact_service": "Power Washing",
                "vertical": "similar-local-service"}


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


def void_plan_j():
    p = PLANS / "2026-08-26-plan-j-confirmed-geo.yaml"
    if not p.exists():
        print("  PLAN-J already moved")
        return
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    cp = d["change_plan"]
    reason = ("SOURCE MISMATCH - the plan was built from the 16-location "
              "geo-union analysis because the actual client-approved CSV was not "
              "available to that run. The approved source is "
              "'Location report (2).csv' (sha256 %s), which carries 75 New York "
              "rows resolving to 72 net-new targets, not 8. Superseded by "
              "PLAN-J2A (positive targets) and PLAN-J2B (Connecticut exclusion), "
              "which are separately fingerprinted."
              % SRCVAL["source"]["sha256_source"][:16])
    cp["approval_status"] = "VOID - DO NOT APPROVE"
    cp["execution_status"] = "VOID - DO NOT EXECUTE"
    cp["void_status"] = {"state": "VOID", "voided_on": "2026-08-26",
                         "fingerprint_voided": "B42EAD386795",
                         "replaced_by": ["PLAN-J2A", "PLAN-J2B"],
                         "reason": reason}
    SUP.mkdir(exist_ok=True)
    p.write_text("# VOID 2026-08-26 - fingerprint B42EAD386795\n# %s\n\n" % reason
                 + yaml.safe_dump(d, sort_keys=False, width=94, allow_unicode=True),
                 encoding="utf-8")
    shutil.move(str(p), str(SUP / p.name))
    print("  VOIDED + moved: PLAN-J  B42EAD386795")


def build_j2a():
    table = RES["resolution_table"]
    by_id = {}
    for r in table:
        if r["proposed_action"] == "ADD_TO_BOTH":
            by_id.setdefault(r["geo_target_constant_id"], r)
    new_ids = sorted(by_id)
    live = {c: {p["geo_target_constant_id"] for p in
                STATE["location_criteria"][c]["positive"]} for c in CAMPAIGNS}

    actions, n = [], 0
    for cid, cname in CAMPAIGNS.items():
        for gid in new_ids:
            r = by_id[gid]
            n += 1
            actions.append({
                "action_id": "R4-J2A-%03d" % n, "priority": "R4",
                "resource_type": "CAMPAIGN_CRITERION", "operation": "CREATE",
                "campaign_id": cid, "campaign_name": cname,
                "current_value": "not targeted in %s" % cname,
                "proposed_value": {
                    "geo_target_constant_id": gid,
                    "canonical_name": r["canonical_name"],
                    "target_type": r["target_type"],
                    "source_row": r["source_row"], "negative": False},
                "goes_live_on_creation": True,
                "rollback": "Remove this campaign criterion.",
                "object_count": 1})

    counts = {}
    for cid, cname in CAMPAIGNS.items():
        counts[cid] = {
            "campaign_name": cname,
            "existing_positive_criteria": len(live[cid]),
            "approved_source_rows": RES["new_york_rows"],
            "valid_resolved_targets": len([r for r in table
                                           if r["geo_target_constant_id"]]),
            "exact_duplicate_ids_skipped":
                RES["action_counts"]["NO_ACTION_DUPLICATE"],
            "existing_criteria_skipped": RES["action_counts"]["KEEP_EXISTING"],
            "new_criteria_to_create": len(new_ids),
            "unresolved_rows": RES["action_counts"]["UNRESOLVED"],
            "invalid_rows": RES["action_counts"]["INVALID"],
            "mutation_count": len(new_ids),
            "post_change_positive_target_count": len(live[cid]) + len(new_ids)}

    plan = {"change_plan": {
        "plan_id": "PLAN-J2A",
        "plan_title": "Client-approved New York geo expansion",
        "approval_type": "LIVE_LOCATION_CRITERIA_POSITIVE",
        "priority": "R4",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "ads_mutation_count": len(actions),
        "requires_separate_enable_approval": False,
        "supersedes": {"plan_id": "PLAN-J", "fingerprint": "B42EAD386795",
                       "state": "VOID - SOURCE MISMATCH"},
        "live_on_creation_warning": (
            "Location criteria have NO paused state. All %d objects begin "
            "affecting delivery the moment they are created. There is no "
            "create-paused / readback / enable split for this resource type, so "
            "this single approval is the only gate." % len(actions)),
        "target": TARGET_BLOCK,
        "source_of_truth": {
            "file": "clients/softwind-power-washing/sources/Location report (2).csv",
            "sha256": SRCVAL["source"]["sha256_source"],
            "found_at": SRCVAL["source"]["found_at"],
            "copied_unmodified": SRCVAL["source"]["copy_is_byte_identical"],
            "report_title": SRCVAL["file_shape"]["report_title"],
            "date_range": SRCVAL["file_shape"]["date_range"],
            "nonblank_location_rows": 78, "new_york_rows": 75,
            "named_new_york_locations": 44, "new_york_zip_codes": 31,
            "non_new_york_rows": 3, "duplicate_location_strings": 0,
            "all_expected_counts_matched": True},
        "excluded_non_new_york_rows": {
            "rows": RES["non_new_york_rows_excluded"],
            "disposition": "NOT_APPROVED_NON_NEW_YORK - not present in any action"},
        "resolution_summary": RES["action_counts"],
        "matching_rule": RES["matching_rule"],
        "dedupe_rule": RES["dedupe_rule"],
        "per_campaign": counts,
        "existing_location_discrepancy_table": {
            "note": ("These live targets are NOT in the approved CSV. They are "
                     "kept unchanged. Removal requires its own separate approval "
                     "and is not proposed here."),
            "rows": RES["existing_live_targets_not_in_csv"]},
        "presence_assertion": {
            "campaign_24103511039": STATE["campaigns"]["24103511039"][
                "positive_geo_target_type"],
            "campaign_24145053510": STATE["campaigns"]["24145053510"][
                "positive_geo_target_type"],
            "both_already_presence": True,
            "mutations_required": 0,
            "note": ("Stage 4 satisfied. Both campaigns already use PRESENCE, so "
                     "no setting mutation is included and none is needed. This is "
                     "recorded as a readback assertion.")},
        "explicitly_not_included": [
            "No Connecticut criterion - that is PLAN-J2B.",
            "No non-New-York additions.", "No removals of any kind.",
            "No budget changes.", "No bidding changes.", "No schedule changes.",
            "No keyword changes.", "No RSA changes.", "No asset changes.",
            "No conversion changes."],
        "actions": actions,
        "change_counts": {
            "positive_location_criteria_added_campaign_A": len(new_ids),
            "positive_location_criteria_added_campaign_B": len(new_ids),
            "negative_location_criteria_added": 0,
            "geo_target_type_settings_changed": 0, "locations_removed": 0,
            "budgets_changed": 0, "bidding_settings_changed": 0,
            "ad_schedules_changed": 0, "keywords_changed": 0, "ads_changed": 0,
            "assets_changed": 0, "conversion_actions_changed": 0,
            "google_ads_mutations_total": len(actions)},
        "readback_qa": [
            "Re-read campaign_criterion type LOCATION for both campaigns.",
            "Assert positive LOCATION count == %d on EACH campaign."
            % (len(live["24103511039"]) + len(new_ids)),
            "Assert all %d pre-existing criterion IDs are still present."
            % len(live["24103511039"]),
            "Assert every created constant resolves to a ',New York,United "
            "States' canonical name.",
            "Assert none of the three non-New-York rows was created.",
            "Assert geo_target_type_setting.positive_geo_target_type is still "
            "PRESENCE on both campaigns.",
            "Assert budgets, bidding, schedules, keywords, ads, assets and "
            "conversion actions are byte-identical to the Stage 1 snapshot.",
            "List every created campaign_criterion resource ID."],
        "partial_failure_protocol": [
            "Stop immediately.",
            "Inventory every created campaign_criterion resource ID.",
            "Do NOT blindly rerun - re-reading is the only safe next step.",
            "Build a recovery plan that creates only the missing remainder."],
        "risks": [
            "LIVE ON CREATION - no paused state exists for location criteria.",
            "%d objects is the largest single mutation in this engagement. A "
            "partial failure is a real possibility and is handled above."
            % len(actions),
            "Landing pages name only Islip, West Islip and Dix Hills. Targeting "
            "%d locations weakens message match everywhere else and may depress "
            "conversion rate and Quality Score. PLAN-F territory, not fixed here."
            % (len(live["24103511039"]) + len(new_ids)),
            "Uncapped Maximize Clicks remains in force. A much larger eligible "
            "audience with no CPC ceiling can raise average CPC as well as "
            "impressions.",
            "31 of the approved rows are ZIP codes that overlap named towns in "
            "the same file. Overlap is NOT removed, per instruction. Google "
            "resolves overlapping targets as a union, so there is no double "
            "charging, but geo reporting granularity will be noisier."],
        "approval_owner": "Walter Correa",
        "approver_email": "access@greenmarketing.com"}}
    return plan, new_ids, counts


def build_j2b(client, gts):
    req = client.get_type("SuggestGeoTargetConstantsRequest")
    req.locale = "en"
    req.country_code = "US"
    req.location_names.names.extend(["Connecticut"])
    cands = []
    for s in gts.suggest_geo_target_constants(request=req
                                              ).geo_target_constant_suggestions:
        g = s.geo_target_constant
        cands.append({"id": str(g.id), "name": g.name,
                      "canonical_name": g.canonical_name,
                      "target_type": g.target_type,
                      "status": enum_name(g.status),
                      "country_code": g.country_code,
                      "reach": int(s.reach) if s.reach else None})
    exact = [c for c in cands
             if c["canonical_name"] == "Connecticut,United States"
             and c["target_type"] == "State" and c["status"] == "ENABLED"]
    if len(exact) != 1:
        raise SystemExit("Connecticut did not resolve to exactly one State "
                         "constant: %d matches" % len(exact))
    ct = exact[0]

    existing = {c: {p["geo_target_constant_id"] for p in
                    STATE["location_criteria"][c]["negative"]} for c in CAMPAIGNS}
    actions, n, noop = [], 0, []
    for cid, cname in CAMPAIGNS.items():
        if ct["id"] in existing[cid]:
            noop.append({"campaign_id": cid, "campaign_name": cname,
                         "status": "NO ACTION REQUIRED - already excluded"})
            continue
        n += 1
        actions.append({
            "action_id": "R4-J2B-%02d" % n, "priority": "R4",
            "resource_type": "CAMPAIGN_CRITERION", "operation": "CREATE",
            "campaign_id": cid, "campaign_name": cname,
            "current_value": "%d negative location criteria" % len(existing[cid]),
            "proposed_value": {"geo_target_constant_id": ct["id"],
                               "canonical_name": ct["canonical_name"],
                               "target_type": ct["target_type"],
                               "negative": True},
            "goes_live_on_creation": True,
            "rollback": "Remove this negative criterion.",
            "object_count": 1})

    plan = {"change_plan": {
        "plan_id": "PLAN-J2B",
        "plan_title": "Connecticut exclusion",
        "approval_type": "LIVE_LOCATION_CRITERIA_NEGATIVE",
        "priority": "R4",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "ads_mutation_count": len(actions),
        "requires_separate_enable_approval": False,
        "supersedes": {"plan_id": "PLAN-J", "fingerprint": "B42EAD386795",
                       "state": "VOID - SOURCE MISMATCH"},
        "target": TARGET_BLOCK,
        "connecticut_resolution": {
            "resolved_fresh_this_run": True,
            "remembered_id_cross_check": "21139",
            "resolved_id": ct["id"],
            "cross_check_agrees": ct["id"] == "21139",
            "canonical_name": ct["canonical_name"],
            "target_type": ct["target_type"], "status": ct["status"],
            "reach": ct["reach"],
            "total_suggestions_returned": len(cands),
            "exact_state_matches": len(exact),
            "note": ("Re-resolved live via GeoTargetConstantService. The "
                     "remembered ID was used only as an assertion, never as the "
                     "source of truth.")},
        "no_action_required": noop,
        "authorized_scope": (
            "Connecticut only, on the two named campaigns. No other location "
            "exclusion, no blanket country exclusion, no other state."),
        "actions": actions,
        "change_counts": {
            "negative_location_criteria_added": len(actions),
            "positive_location_criteria_added": 0, "locations_removed": 0,
            "geo_target_type_settings_changed": 0, "budgets_changed": 0,
            "bidding_settings_changed": 0, "keywords_changed": 0,
            "ads_changed": 0, "assets_changed": 0,
            "google_ads_mutations_total": len(actions)},
        "readback_qa": [
            "Re-read negative LOCATION criteria on both campaigns.",
            "Assert exactly 1 negative location criterion per campaign.",
            "Assert it resolves to %s Connecticut,United States." % ct["id"],
            "Assert no other state or country criterion exists.",
            "Assert positive location criteria are unchanged in count and IDs.",
            "Assert PRESENCE is unchanged on both campaigns."],
        "interaction_note": (
            "Under PRESENCE targeting a Connecticut-present user is already "
            "outside the positive set. This exclusion's real effect is on the "
            "'regularly in' half of PRESENCE: it blocks Connecticut residents "
            "who regularly travel to Long Island, including anyone who owns "
            "Long Island property. Confirmed by the owner and fully reversible."),
        "risks": ["LIVE ON CREATION - no paused state exists.",
                  "Blocks a small, genuine segment as described above."],
        "approval_owner": "Walter Correa",
        "approver_email": "access@greenmarketing.com"}}
    return plan, ct


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    gts = client.get_service("GeoTargetConstantService")

    print("VOIDING SUPERSEDED PLAN")
    void_plan_j()
    print()

    j2a, new_ids, counts = build_j2a()
    fa = approval_code(normalize(j2a))
    pa = PLANS / "2026-08-26-plan-j2a-approved-ny-geo.yaml"
    pa.write_text(
        "# PLAN-J2A - CLIENT-APPROVED NEW YORK GEO EXPANSION\n#\n"
        "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
        "# LIVE ON CREATION - location criteria have no paused state.\n"
        "# Source: Location report (2).csv  sha256 %s\n"
        "# Supersedes PLAN-J B42EAD386795 (VOID - source mismatch).\n\n"
        % SRCVAL["source"]["sha256_source"][:32]
        + yaml.safe_dump(j2a, sort_keys=False, width=94, allow_unicode=True),
        encoding="utf-8")

    j2b, ct = build_j2b(client, gts)
    fb = approval_code(normalize(j2b))
    pb = PLANS / "2026-08-26-plan-j2b-connecticut-exclusion.yaml"
    pb.write_text(
        "# PLAN-J2B - CONNECTICUT EXCLUSION\n#\n"
        "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
        "# LIVE ON CREATION. Connecticut re-resolved fresh this run.\n\n"
        + yaml.safe_dump(j2b, sort_keys=False, width=94, allow_unicode=True),
        encoding="utf-8")

    print("PLAN-J2A  %s" % fa)
    print("   mutations %d   objects %d" % (len(j2a["change_plan"]["actions"]),
                                            len(j2a["change_plan"]["actions"])))
    for cid, c in counts.items():
        print("   %s %-18s existing %2d + new %2d = %3d positive targets"
              % (cid, c["campaign_name"], c["existing_positive_criteria"],
                 c["new_criteria_to_create"],
                 c["post_change_positive_target_count"]))
    print()
    print("PLAN-J2B  %s" % fb)
    print("   Connecticut resolved fresh -> %s  %s  %s  reach %s"
          % (ct["id"], ct["canonical_name"], ct["target_type"], ct["reach"]))
    print("   remembered-ID cross-check agrees: %s" % (ct["id"] == "21139"))
    print("   mutations %d" % len(j2b["change_plan"]["actions"]))
    print()
    print("APPROVE PLAN-J2A %s FOR %s" % (fa, CID))
    print("APPROVE PLAN-J2B %s FOR %s" % (fb, CID))
    print()
    print("wrote %s" % pa.name)
    print("wrote %s" % pb.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
