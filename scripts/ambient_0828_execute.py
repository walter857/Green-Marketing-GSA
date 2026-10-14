#!/usr/bin/env python3
"""Ambient Cooling - Live | EXECUTE the three approved fingerprints.

  82ACD4953536C020  A-1  7 x CREATE PHRASE negative on campaign 24132507747
  6F2B6ABBCEB992E4  A-2  1 x CREATE BROAD  negative on campaign 24132507741
  E50EDFE7644A9B5F  D-1  1 x REMOVE shared_criterion 11252984411~11143481

Three atomic mutations, partial_failure=false, readback after each.
On any failure: stop, inventory what was returned, emit a recovery plan, do not retry.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, RECEIPTS, TZ, client, q, identity_gate, E, write,
)

STAMP = "2026-08-28"
HVAC_INSTALL, AC_REPAIR = "24132507747", "24132507741"
ACCOUNT_SET, HANOVER_CRIT = "11252984411", "11143481"
A1 = ["croppmetcalfe", "michael and sons", "michael & sons",
      "armbridge", "bluedot", "blauch", "hugee"]
A2 = ["automotive"]

REC = {"stage": "EXECUTION", "customer_id": CID,
       "approved_fingerprints": {"A-1": "82ACD4953536C020", "A-2": "6F2B6ABBCEB992E4",
                                 "D-1": "E50EDFE7644A9B5F"},
       "started_local": datetime.datetime.now(TZ).isoformat(),
       "executions": {}, "created_resource_names": [], "removed_resource_names": []}


def halt(reason, extra=None):
    REC["status"] = "HALTED"
    REC["halt_reason"] = reason
    REC["recovery"] = extra or {}
    REC["ended_local"] = datetime.datetime.now(TZ).isoformat()
    write(RECEIPTS / f"execution-HALTED-{STAMP}.json", REC)
    print(f"\n*** HALT: {reason} ***")
    if extra:
        print(json.dumps(extra, indent=2, default=str))
    sys.exit(1)


def gate(c, label):
    row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
                  customer.test_account, customer.time_zone, customer.currency_code
                  FROM customer""")[0].customer
    ok = (row.descriptive_name == "Ambient Cooling - Live" and str(row.id) == CID
          and not row.manager and not row.test_account
          and row.time_zone == "America/New_York" and row.currency_code == "USD")
    print(f"  identity gate before {label}: {'PASS' if ok else 'FAIL'} "
          f"({row.descriptive_name} / {row.id})")
    if not ok:
        halt(f"identity gate failed immediately before {label}")


def main():
    c = client()

    # ================= EXECUTION 1 =================
    print("== EXECUTION 1: A-1  7 PHRASE competitor negatives on 24132507747 ==")
    gate(c, "A-1")
    cc = c.get_service("CampaignCriterionService")
    ops = []
    for t in A1:
        op = c.get_type("CampaignCriterionOperation")
        crit = op.create
        crit.campaign = f"customers/{CID}/campaigns/{HVAC_INSTALL}"
        crit.negative = True
        crit.keyword.text = t
        crit.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
        ops.append(op)
    req = c.get_type("MutateCampaignCriteriaRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    req.partial_failure = False
    req.validate_only = False
    try:
        resp = cc.mutate_campaign_criteria(request=req)
    except Exception as exc:  # noqa: BLE001
        halt("A-1 mutation raised", {"error": str(exc)[:2000],
             "note": "partial_failure=false, so the batch should be atomic. "
                     "Verify with a fresh read before any retry."})
    names = [r.resource_name for r in resp.results]
    REC["created_resource_names"] += names
    REC["executions"]["A-1"] = {
        "fingerprint": "82ACD4953536C020", "campaign_id": HVAC_INSTALL,
        "operations_sent": len(ops), "results_returned": len(names),
        "executed_local": datetime.datetime.now(TZ).isoformat(),
        "resource_names": names,
        "partial_failure_error": str(resp.partial_failure_error) if resp.partial_failure_error else ""}
    print(f"  operations sent: {len(ops)}   results returned: {len(names)}")
    for n in names:
        print(f"     {n}")
    if len(names) != 7:
        halt("A-1 returned a result count other than 7",
             {"returned": names, "recovery": "REMOVE every returned resource name above"})

    print("\n  READBACK A-1:")
    back = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.resource_name,
                      campaign_criterion.criterion_id, campaign_criterion.keyword.text,
                      campaign_criterion.keyword.match_type, campaign_criterion.negative,
                      campaign_criterion.status FROM campaign_criterion
                      WHERE campaign.id = {HVAC_INSTALL}
                        AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.status!='REMOVED'"""):
        x = r.campaign_criterion
        back.append({"resource_name": x.resource_name, "criterion_id": str(x.criterion_id),
                     "text": x.keyword.text, "match": E(x.keyword.match_type),
                     "negative": x.negative, "status": E(x.status)})
    REC["executions"]["A-1"]["readback"] = back
    for b in sorted(back, key=lambda z: z["text"]):
        print(f"     [{b['match']:6s}] {b['text']:20s} id={b['criterion_id']:>12s} "
              f"neg={b['negative']} {b['status']}")
    a1_ok = (len(back) == 7
             and sorted(b["text"] for b in back) == sorted(A1)
             and all(b["match"] == "PHRASE" and b["negative"] and b["status"] == "ENABLED"
                     for b in back)
             and sorted(b["resource_name"] for b in back) == sorted(names))
    print(f"  A-1 readback: {'PASS' if a1_ok else 'FAIL'}")
    if not a1_ok:
        halt("A-1 readback mismatch",
             {"expected": sorted(A1), "observed": sorted(b["text"] for b in back),
              "created_resource_names": names,
              "recovery": "REMOVE the created resource names listed above, then re-verify"})
    REC["executions"]["A-1"]["readback_pass"] = True

    # ================= EXECUTION 2 =================
    print("\n== EXECUTION 2: A-2  1 BROAD 'automotive' on 24132507741 ==")
    print("  classification: PROACTIVE TRAFFIC PROTECTION, observed cost $0.00, "
          "not a measured saving")
    gate(c, "A-2")
    ops = []
    for t in A2:
        op = c.get_type("CampaignCriterionOperation")
        crit = op.create
        crit.campaign = f"customers/{CID}/campaigns/{AC_REPAIR}"
        crit.negative = True
        crit.keyword.text = t
        crit.keyword.match_type = c.enums.KeywordMatchTypeEnum.BROAD
        ops.append(op)
    req = c.get_type("MutateCampaignCriteriaRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    req.partial_failure = False
    req.validate_only = False
    try:
        resp = cc.mutate_campaign_criteria(request=req)
    except Exception as exc:  # noqa: BLE001
        halt("A-2 mutation raised", {"error": str(exc)[:2000],
             "already_created_in_A1": REC["created_resource_names"]})
    names2 = [r.resource_name for r in resp.results]
    REC["created_resource_names"] += names2
    REC["executions"]["A-2"] = {
        "fingerprint": "6F2B6ABBCEB992E4", "campaign_id": AC_REPAIR,
        "classification": "proactive traffic protection, observed cost $0.00",
        "operations_sent": len(ops), "results_returned": len(names2),
        "executed_local": datetime.datetime.now(TZ).isoformat(),
        "resource_names": names2}
    print(f"  operations sent: {len(ops)}   results returned: {len(names2)}")
    for n in names2:
        print(f"     {n}")
    if len(names2) != 1:
        halt("A-2 returned a result count other than 1", {"returned": names2})

    print("\n  READBACK A-2:")
    back2 = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.resource_name,
                      campaign_criterion.criterion_id, campaign_criterion.keyword.text,
                      campaign_criterion.keyword.match_type, campaign_criterion.negative,
                      campaign_criterion.status FROM campaign_criterion
                      WHERE campaign.id = {AC_REPAIR}
                        AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.status!='REMOVED'"""):
        x = r.campaign_criterion
        back2.append({"resource_name": x.resource_name, "criterion_id": str(x.criterion_id),
                      "text": x.keyword.text, "match": E(x.keyword.match_type),
                      "negative": x.negative, "status": E(x.status)})
    REC["executions"]["A-2"]["readback"] = back2
    for b in sorted(back2, key=lambda z: z["text"]):
        print(f"     [{b['match']:6s}] {b['text']:20s} id={b['criterion_id']:>12s} "
              f"neg={b['negative']} {b['status']}")
    a2_ok = (len(back2) == 4
             and sorted(b["text"] for b in back2) == ["auto", "automotive", "boat", "car"]
             and all(b["negative"] and b["status"] == "ENABLED" for b in back2))
    print(f"  A-2 readback: {'PASS' if a2_ok else 'FAIL'} "
          f"(expect car+auto+boat preserved plus automotive)")
    if not a2_ok:
        halt("A-2 readback mismatch",
             {"observed": sorted(b["text"] for b in back2),
              "created_resource_names": REC["created_resource_names"]})
    REC["executions"]["A-2"]["readback_pass"] = True

    # ================= EXECUTION 3 =================
    print("\n== EXECUTION 3: D-1  REMOVE account-level criterion 11143481 'hanover' ==")
    gate(c, "D-1")
    target = f"customers/{CID}/sharedCriteria/{ACCOUNT_SET}~{HANOVER_CRIT}"
    pre = {}
    for r in q(c, f"""SELECT shared_criterion.resource_name, shared_criterion.criterion_id,
                      shared_criterion.keyword.text, shared_criterion.keyword.match_type
                      FROM shared_criterion WHERE shared_set.id = {ACCOUNT_SET}"""):
        pre[str(r.shared_criterion.criterion_id)] = {
            "text": r.shared_criterion.keyword.text,
            "match": E(r.shared_criterion.keyword.match_type)}
    REC["executions"]["D-1"] = {"fingerprint": "E50EDFE7644A9B5F",
                                "members_before": len(pre), "target": target}
    print(f"  members before: {len(pre)}   target: {target}")
    if len(pre) != 59 or HANOVER_CRIT not in pre or pre[HANOVER_CRIT]["text"] != "hanover":
        halt("D-1 before-state drifted", {"members_before": len(pre),
                                          "hanover_present": HANOVER_CRIT in pre})

    sc = c.get_service("SharedCriterionService")
    op = c.get_type("SharedCriterionOperation")
    op.remove = target
    req = c.get_type("MutateSharedCriteriaRequest")
    req.customer_id = CID
    req.operations.append(op)
    req.partial_failure = False
    req.validate_only = False
    try:
        resp = sc.mutate_shared_criteria(request=req)
    except Exception as exc:  # noqa: BLE001
        halt("D-1 mutation raised", {"error": str(exc)[:2000],
             "already_created": REC["created_resource_names"]})
    rm = [r.resource_name for r in resp.results]
    REC["removed_resource_names"] += rm
    REC["executions"]["D-1"].update({
        "operations_sent": 1, "results_returned": len(rm),
        "executed_local": datetime.datetime.now(TZ).isoformat(),
        "resource_names": rm})
    print(f"  operations sent: 1   results returned: {len(rm)}")
    for n in rm:
        print(f"     removed {n}")
    if len(rm) != 1:
        halt("D-1 returned a result count other than 1", {"returned": rm})

    print("\n  READBACK D-1:")
    post = {}
    for r in q(c, f"""SELECT shared_criterion.resource_name, shared_criterion.criterion_id,
                      shared_criterion.keyword.text, shared_criterion.keyword.match_type
                      FROM shared_criterion WHERE shared_set.id = {ACCOUNT_SET}"""):
        post[str(r.shared_criterion.criterion_id)] = {
            "text": r.shared_criterion.keyword.text,
            "match": E(r.shared_criterion.keyword.match_type)}
    gone = HANOVER_CRIT not in post
    removed_set = set(pre) - set(post)
    added_set = set(post) - set(pre)
    changed = [k for k in set(pre) & set(post) if pre[k] != post[k]]
    geo = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id,
                      campaign_criterion.negative,
                      campaign_criterion.location.geo_target_constant
                      FROM campaign_criterion WHERE campaign.id IN ({IN5})
                        AND campaign_criterion.type='LOCATION'
                        AND campaign_criterion.status!='REMOVED'"""):
        if r.campaign_criterion.location.geo_target_constant.endswith("/1018614"):
            geo.append(NAME[str(r.campaign.id)])
    css = len(q(c, f"SELECT campaign.id FROM campaign_shared_set WHERE campaign.id IN ({IN5})"))
    held = ["thermostat", "thermostats", "ruud", "rudd", "ecobee", "frigidaire", "ducane"]
    held_still = sorted(v["text"] for v in post.values() if v["text"].lower() in held)
    REC["executions"]["D-1"].update({
        "members_after": len(post), "criterion_11143481_gone": gone,
        "removed_criterion_ids": sorted(removed_set), "added_criterion_ids": sorted(added_set),
        "changed_members": changed, "hanover_geo_still_targeted_on": geo,
        "campaign_shared_sets_on_five": css, "held_members_still_present": held_still})
    print(f"     members after                : {len(post)} (was {len(pre)})")
    print(f"     criterion 11143481 gone      : {gone}")
    print(f"     removed criterion ids        : {sorted(removed_set)}")
    print(f"     added criterion ids          : {sorted(added_set) or 'none'}")
    print(f"     changed members              : {changed or 'none'}")
    print(f"     Hanover geo 1018614 targeted : {geo}")
    print(f"     shared lists on the five     : {css}")
    print(f"     HELD members still present   : {held_still}")
    d1_ok = (gone and len(post) == 58 and removed_set == {HANOVER_CRIT}
             and not added_set and not changed and len(geo) == 5 and css == 0
             and sorted(held_still) == sorted(held))
    print(f"  D-1 readback: {'PASS' if d1_ok else 'FAIL'}")
    if not d1_ok:
        halt("D-1 readback mismatch", {"members_after": len(post),
                                       "removed": sorted(removed_set)})
    REC["executions"]["D-1"]["readback_pass"] = True

    REC["status"] = "COMPLETE"
    REC["total_operations_executed"] = 9
    REC["ended_local"] = datetime.datetime.now(TZ).isoformat()
    write(RECEIPTS / f"execution-receipt-{STAMP}.json", REC)
    print("\n== ALL THREE EXECUTIONS COMPLETE, 9 OPERATIONS, ALL READBACKS PASS ==")
    return REC


if __name__ == "__main__":
    main()
