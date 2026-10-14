#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | the two separate-approval plans.

CONV-1  Conversion-goal integrity. Bidding-goal change, its own approval class.
DEL-1   Account-level negative removals. Destructive-action approval class.

Both are built, conflict-tested and validate-only checked. NOTHING is written
durably by this script.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys
from pathlib import Path

from google.protobuf import field_mask_pb2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, PLANS, SNAP, RECEIPTS, TZ,
    client, q, identity_gate, E, write,
)
from ambient_0827_negative_audit import SERVICE_PROBES, blocks  # noqa: E402

STAMP = "2026-08-27"
ACCOUNT_SET = "11252984411"

# Account-level negatives that demonstrably suppress in-scope demand for the
# five approved services. Each carries the exact reason and the proof.
REMOVE_CANDIDATES = {
    "hanover": ("Hanover, Maryland is geo target 1018614 and is an EXPLICITLY "
                "TARGETED city on all five campaigns. This negative blocks the "
                "account from its own targeted city."),
    "thermostat": ("Thermostat diagnosis and replacement is HVAC Repair work, "
                   "one of the five approved services."),
    "thermostats": ("Plural of the above. Negatives have no close variants, so "
                    "both forms are present and both suppress the same demand."),
    "ruud": "Ruud is an HVAC equipment brand. Ruud furnace and AC repair is HVAC Repair.",
    "rudd": "Common misspelling of Ruud. Same suppression.",
    "ecobee": "Ecobee is a thermostat brand. Ecobee installation is HVAC work.",
    "frigidaire": "Frigidaire is an HVAC equipment brand. Brand repair demand is in scope.",
    "ducane": "Ducane is an HVAC equipment brand. Brand repair demand is in scope.",
}
# Held back on purpose: needs a business fact this agent must not invent.
HELD_FOR_CLIENT_CONFIRMATION = {
    "commercial": ("Blocks 'commercial ac repair' and 'commercial boiler repair'. "
                   "Removing this is only correct if Ambient Cooling & Heating LLC "
                   "actually serves commercial customers. That is an unverified "
                   "business fact, so it is NOT proposed for removal."),
}


def fingerprint(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16].upper()


def main():
    c = client()
    print("== IDENTITY GATE ==")
    identity_gate(c, verbose=False)
    print("  PASS\n")

    st = json.loads((SNAP / f"search-terms-{STAMP}.json").read_text(encoding="utf-8"))
    verdicts = st["verdicts"]
    receipts = {"run_local": datetime.datetime.now(TZ).isoformat(),
                "customer_id": CID, "results": {}}

    # =====================================================================
    # CONV-1  conversion-goal integrity
    # =====================================================================
    print("== CONV-1  CONVERSION-GOAL INTEGRITY ==")
    actions = []
    for r in q(c, """SELECT conversion_action.id, conversion_action.name,
                     conversion_action.category, conversion_action.origin,
                     conversion_action.status, conversion_action.primary_for_goal,
                     conversion_action.include_in_conversions_metric,
                     conversion_action.type FROM conversion_action
                     WHERE conversion_action.status != 'REMOVED'"""):
        x = r.conversion_action
        actions.append({"id": str(x.id), "name": x.name, "category": E(x.category),
                        "origin": E(x.origin), "status": E(x.status),
                        "type": E(x.type_), "primary_for_goal": x.primary_for_goal,
                        "include_in_conversions_metric": x.include_in_conversions_metric})

    cgoals = []
    for r in q(c, f"""SELECT campaign.id, campaign_conversion_goal.category,
                      campaign_conversion_goal.origin, campaign_conversion_goal.biddable,
                      campaign_conversion_goal.resource_name
                      FROM campaign_conversion_goal WHERE campaign.id IN ({IN5})"""):
        x = r.campaign_conversion_goal
        cgoals.append({"campaign_id": str(r.campaign.id),
                       "campaign": NAME[str(r.campaign.id)],
                       "category": E(x.category), "origin": E(x.origin),
                       "biddable": x.biddable, "resource_name": x.resource_name})

    # which actions sit inside each biddable goal
    TARGETS = [("CONTACT", "WEBSITE"), ("CONTACT", "CALL_FROM_ADS")]
    goal_members = {}
    for cat, org in TARGETS:
        goal_members[f"{cat}/{org}"] = [
            a for a in actions if a["category"] == cat and a["origin"] == org]
    print("  biddable goals proposed for change, and the actions inside them:")
    for k, v in goal_members.items():
        print(f"     {k}")
        for a in v:
            print(f"        {a['id']} {a['name']:34s} type={a['type']:14s} "
                  f"primary_for_goal={a['primary_for_goal']} "
                  f"include_in_conversions={a['include_in_conversions_metric']}")

    # observed double count
    dbl = []
    for r in q(c, f"""SELECT campaign.id, search_term_view.search_term,
                      segments.conversion_action_name, metrics.conversions
                      FROM search_term_view WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-27'
                        AND metrics.conversions > 0"""):
        dbl.append({"campaign": NAME[str(r.campaign.id)],
                    "term": r.search_term_view.search_term,
                    "action": r.segments.conversion_action_name,
                    "conversions": round(r.metrics.conversions, 2)})
    from collections import defaultdict
    by_term = defaultdict(list)
    for d in dbl:
        by_term[d["term"]].append(d)
    doubles = {t: v for t, v in by_term.items() if len(v) > 1}
    print("\n  observed Primary-conversion double counting:")
    for t, v in doubles.items():
        print(f"     '{t}' -> {[(x['action'], x['conversions']) for x in v]}")
    total_primary = round(sum(d["conversions"] for d in dbl), 2)
    dup_count = round(sum(
        sum(x["conversions"] for x in v[1:]) for v in doubles.values()), 2)
    print(f"  Primary conversions reported: {total_primary}")
    print(f"  of which duplicated by a second action on the same query: {dup_count}")

    conv_plan = {
        "plan_name": "AMBIENT-CONV-1-2026-08-27",
        "approval_class": "conversion / bidding-goal change - SEPARATE approval",
        "generated_local": datetime.datetime.now(TZ).isoformat(),
        "customer_id": CID,
        "exact_child_account_name": "Ambient Cooling - Live",
        "problem": (
            "The customer conversion goals CONTACT/WEBSITE and CONTACT/CALL_FROM_ADS "
            "are biddable. Every conversion action inside a biddable goal is counted "
            "in the Conversions column and feeds Maximize Clicks conversion reporting, "
            "regardless of the action's primary_for_goal flag. That pulls the "
            "WhatConverts upload actions and the raw call-button click into the same "
            "totals as the landing-page form and the call-from-ads action."),
        "proof": {
            "wc_lead_action": ("7643656486 'WC Lead' reads primary_for_goal=False and "
                               "include_in_conversions_metric=False, yet contributed "
                               "1.0 to metrics.conversions on 'hvac companies near me "
                               "open now'."),
            "observed_double_counted_queries": {t: [(x["action"], x["conversions"])
                                                    for x in v]
                                                for t, v in doubles.items()},
            "primary_conversions_reported": total_primary,
            "primary_conversions_duplicated": dup_count,
            "inflation": f"{round(dup_count / total_primary * 100, 1)}% overstated"
            if total_primary else "n/a",
            "actions_pulled_in_by_the_two_goals": goal_members,
        },
        "proposed_change": {
            "operation": "UPDATE campaign_conversion_goal.biddable = false",
            "targets": [f"{cid}~CONTACT~WEBSITE" for cid in FIVE]
                       + [f"{cid}~CONTACT~CALL_FROM_ADS" for cid in FIVE],
            "object_count": 10,
            "before": [g for g in cgoals
                       if (g["category"], g["origin"]) in
                       [("CONTACT", "WEBSITE"), ("CONTACT", "CALL_FROM_ADS")]],
            "after": "biddable=false on those 10 campaign conversion goals",
            "kept_biddable": ["SUBMIT_LEAD_FORM/WEBSITE", "PHONE_CALL_LEAD/WEBSITE",
                              "PHONE_CALL_LEAD/CALL_FROM_ADS"],
            "effect": (
                "Primary conversions become exactly the landing-page form lead, the "
                "landing-page website call and the call-from-ads action. WhatConverts "
                "uploads and the raw call-button click stay visible as secondary "
                "diagnostics and stop inflating the bidding total."),
        },
        "risks": [
            "Reported Conversions will step DOWN. That is the correction, not a loss.",
            "Maximize Clicks does not bid to conversions, so bidding behaviour does "
            "not change today. The correction matters before any move to a "
            "conversion-based strategy.",
            "No conversion action is removed, paused or edited. Only goal "
            "biddability at campaign level changes.",
        ],
        "rollback": "Set biddable=true on the same 10 campaign conversion goals.",
        "unrelated_resource_assertions": [
            "no conversion action created, removed, paused or edited",
            "customer-level conversion goals untouched",
            "the known duplicate form action 6498555481 stays ENABLED and secondary",
            "WhatConverts actions 7643656075 and 7643656486 stay ENABLED",
            "campaigns, budgets, keywords, ads and assets untouched",
        ],
    }
    conv_fp = fingerprint({k: conv_plan[k] for k in
                           ("plan_name", "customer_id", "proposed_change")})
    conv_plan["fingerprint"] = conv_fp
    print(f"\n  CONV-1 fingerprint: {conv_fp}")

    # validate-only for CONV-1
    svc = c.get_service("CampaignConversionGoalService")
    ops = []
    for cid in FIVE:
        for cat, org in TARGETS:
            op = c.get_type("CampaignConversionGoalOperation")
            g = op.update
            g.resource_name = (f"customers/{CID}/campaignConversionGoals/"
                               f"{cid}~{cat}~{org}")
            g.biddable = False
            c.copy_from(op.update_mask, field_mask_pb2.FieldMask(paths=["biddable"]))
            ops.append(op)
    req = c.get_type("MutateCampaignConversionGoalsRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    req.validate_only = True
    try:
        resp = svc.mutate_campaign_conversion_goals(request=req)
        receipts["results"]["CONV-1"] = {"status": "VALIDATE_OK",
                                         "operations": len(ops),
                                         "results_returned": len(resp.results)}
        print(f"  CONV-1 validate-only: VALIDATE_OK ({len(ops)} operations)")
    except Exception as exc:  # noqa: BLE001
        receipts["results"]["CONV-1"] = {"status": "VALIDATE_FAIL",
                                         "error": str(exc)[:1500]}
        print(f"  CONV-1 validate-only: VALIDATE_FAIL\n{str(exc)[:900]}")
    conv_plan["validate_only"] = receipts["results"]["CONV-1"]

    # =====================================================================
    # DEL-1  destructive account-level negative removals
    # =====================================================================
    print("\n== DEL-1  ACCOUNT-LEVEL NEGATIVE REMOVALS (DESTRUCTIVE) ==")
    members = []
    for r in q(c, f"""SELECT shared_criterion.resource_name,
                      shared_criterion.criterion_id, shared_criterion.keyword.text,
                      shared_criterion.keyword.match_type FROM shared_criterion
                      WHERE shared_set.id = {ACCOUNT_SET}"""):
        members.append({"resource_name": r.shared_criterion.resource_name,
                        "criterion_id": str(r.shared_criterion.criterion_id),
                        "text": r.shared_criterion.keyword.text,
                        "match": E(r.shared_criterion.keyword.match_type)})
    by_text = {m["text"].lower(): m for m in members}

    removals = []
    missing = []
    for text, why in REMOVE_CANDIDATES.items():
        m = by_text.get(text)
        if not m:
            missing.append(text)
            continue
        probes = [p for p in SERVICE_PROBES if blocks(m["text"], m["match"], p)[0]]
        observed = [v for v in verdicts if blocks(m["text"], m["match"], v["search_term"])[0]]
        removals.append({
            "text": m["text"], "match": m["match"],
            "criterion_id": m["criterion_id"], "resource_name": m["resource_name"],
            "reason": why,
            "in_scope_service_probes_it_blocks": probes,
            "observed_terms_it_blocked": [v["search_term"] for v in observed],
            "observed_cost_it_blocked": round(sum(v["cost"] for v in observed), 2),
        })
    print(f"  members in list {ACCOUNT_SET}: {len(members)}")
    print(f"  proposed removals: {len(removals)}   not found: {missing}")
    for x in removals:
        print(f"     [{x['match']:6s}] {x['text']:14s} id={x['criterion_id']} "
              f"blocks_probes={x['in_scope_service_probes_it_blocks']}")
    print("  HELD BACK pending client confirmation:")
    for k, v in HELD_FOR_CLIENT_CONFIRMATION.items():
        print(f"     {k}: {v}")

    del_plan = {
        "plan_name": "AMBIENT-DEL-1-2026-08-27",
        "approval_class": "DESTRUCTIVE-ACTION approval - separate and explicit",
        "generated_local": datetime.datetime.now(TZ).isoformat(),
        "customer_id": CID,
        "exact_child_account_name": "Ambient Cooling - Live",
        "target": {
            "shared_set_id": ACCOUNT_SET,
            "shared_set_name": "account-level negative keywords list",
            "shared_set_type": "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS",
            "member_count_reported_by_api": 0,
            "actual_members_counted": len(members),
            "note": ("ACCOUNT_LEVEL_NEGATIVE_KEYWORDS applies account-wide and never "
                     "appears in campaign_shared_set. shared_set.member_count reports "
                     "0 for this type, so members must be counted from "
                     "shared_criterion."),
        },
        "operation": "REMOVE shared_criterion",
        "object_count": len(removals),
        "removals": sorted(removals, key=lambda z: z["text"]),
        "not_proposed": HELD_FOR_CLIENT_CONFIRMATION,
        "blast_radius": (
            "This list applies to the whole account, so removal also affects the 18 "
            "legacy campaigns. All 18 are PAUSED, so there is no live delivery impact "
            "beyond the five active Search campaigns."),
        "measured_loss_to_date": (
            "$0.00. None of these eight negatives matched a term in the observed "
            "corpus, because they suppress demand before it can be measured. The "
            "case for removal is recovered qualified demand, not a recovered cost."),
        "strongest_item": (
            "'hanover' blocks the account from Hanover, Maryland, geo target 1018614, "
            "which is an explicitly targeted city on all five campaigns."),
        "rollback": (
            "Re-create the eight shared_criterion members with the same text and "
            "BROAD match. Criterion IDs will differ after re-creation."),
        "unrelated_resource_assertions": [
            "the other 51 members of list 11252984411 stay unchanged",
            "no other shared set is touched",
            "no campaign_shared_set association is created or removed",
            "campaigns, budgets, keywords, ads, assets and conversions untouched",
        ],
    }
    del_fp = fingerprint({k: del_plan[k] for k in
                          ("plan_name", "customer_id", "operation", "removals")})
    del_plan["fingerprint"] = del_fp
    print(f"\n  DEL-1 fingerprint: {del_fp}")

    svc2 = c.get_service("SharedCriterionService")
    ops2 = []
    for x in removals:
        op = c.get_type("SharedCriterionOperation")
        op.remove = x["resource_name"]
        ops2.append(op)
    req2 = c.get_type("MutateSharedCriteriaRequest")
    req2.customer_id = CID
    req2.operations.extend(ops2)
    req2.validate_only = True
    try:
        resp2 = svc2.mutate_shared_criteria(request=req2)
        receipts["results"]["DEL-1"] = {"status": "VALIDATE_OK",
                                        "operations": len(ops2),
                                        "results_returned": len(resp2.results)}
        print(f"  DEL-1 validate-only: VALIDATE_OK ({len(ops2)} operations)")
    except Exception as exc:  # noqa: BLE001
        receipts["results"]["DEL-1"] = {"status": "VALIDATE_FAIL",
                                        "error": str(exc)[:1500]}
        print(f"  DEL-1 validate-only: VALIDATE_FAIL\n{str(exc)[:900]}")
    del_plan["validate_only"] = receipts["results"]["DEL-1"]

    write(PLANS / f"AMBIENT-CONV-1-{STAMP}.json", conv_plan)
    write(PLANS / f"AMBIENT-DEL-1-{STAMP}.json", del_plan)
    write(RECEIPTS / f"validate-only-separate-plans-{STAMP}.json", receipts)

    print("\n== APPROVAL LINES ==")
    print(f"  APPROVE CONVERSION GOAL PLAN {conv_fp} FOR {CID}")
    print(f"  APPROVE DESTRUCTIVE NEGATIVE REMOVAL PLAN {del_fp} FOR {CID}")
    return conv_plan, del_plan


if __name__ == "__main__":
    main()
