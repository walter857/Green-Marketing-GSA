#!/usr/bin/env python3
"""Ambient | 2026-09-23 | Build + validate + execute the conversion-architecture repair.

Scope: conversion-action primary_for_goal flags ONLY. No budget, bid, keyword, ad,
targeting or delivery-status change. Nothing is deleted. Fully reversible.

--build      write the fingerprinted plan
--validate   validate_only against the API, write nothing
--execute    apply, then read back
"""
from __future__ import annotations
import sys, json, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-23"
LIVE = ROOT / "receipts" / "live"
PLAN_NAME = "AMB-0923-CONV-2"

# One Primary measurement path per underlying event.
#
# KEEP PRIMARY - three genuinely distinct events:
#   6885463625  WEBPAGE / SUBMIT_LEAD_FORM   website form submission   5 conv / 90d
#   1068114183  AD_CALL / PHONE_CALL_LEAD    call placed FROM an ad    5 conv / 90d
#   6885576934  WEBSITE_CALL / PHONE_CALL_LEAD  call placed from the website
#               (0 events so far, but it is the correct native home for that route and
#                measures a DIFFERENT event from a call-asset call, so it is not a duplicate)
#
# DEMOTE TO SECONDARY - each duplicates an event already counted above, or is inert:
DEMOTE = {
    "7389995485": {
        "name": "Ambient Cooling and Heating (web) form_submission",
        "type": "GOOGLE_ANALYTICS_4_CUSTOM", "category": "SUBMIT_LEAD_FORM",
        "why": "A GA4 import of the SAME website form submission already counted by the "
               "native WEBPAGE action 6885463625. Two Primary actions on one form "
               "submission double-counts it. 6 all_conversions in 90 days, 0 in the "
               "Conversions column, so it adds no measurement the native action lacks.",
    },
    "7643656486": {
        "name": "WC Lead",
        "type": "UPLOAD_CLICKS", "category": "CONTACT",
        "why": "WhatConverts uploads the SAME form submission that the native WEBPAGE "
               "action already counts, so on the offer subdomain one submission is "
               "counted twice. It is also incomplete: WhatConverts profile 105803 "
               "registers exactly one form selector, #gform_1, so it captures the offer "
               "subdomain and has NEVER captured a main-site #gform_2 submission. Proven "
               "by 7/7 web-form leads since 2026-08-01 originating on the offer "
               "subdomain, and by a controlled test on 2026-09-21 where the offer form "
               "produced lead 259273825 in 26 seconds and the main-site form produced "
               "nothing. Kept ENABLED as a Secondary diagnostic; capture is NOT disabled.",
    },
    "7643656075": {
        "name": "WC Calls",
        "type": "UPLOAD_CALLS", "category": "CONTACT",
        "why": "Zero conversions for its entire lifetime (0 in the last 120 days, 0 in 90, "
               "0 in September). UPLOAD_CALLS expects Google-forwarded call data; "
               "WhatConverts tracks calls on its OWN numbers, which are not Google "
               "forwarding numbers, so this action has no supported upload route and is "
               "structurally inert. Demoted rather than deleted so nothing is lost if the "
               "upload route is later corrected.",
    },
}
KEEP_PRIMARY = {
    "6885463625": "Ambient Cooling - LP -Submit Lead Forms (native form)",
    "1068114183": "Calls from ads (native call-asset call)",
    "6885576934": "Ambient Cooling - Lp - Phone call leads (native website call)",
}


def build(c):
    live = {}
    for r in q(c, """SELECT conversion_action.id, conversion_action.name,
                     conversion_action.status, conversion_action.type,
                     conversion_action.category, conversion_action.origin,
                     conversion_action.primary_for_goal,
                     conversion_action.include_in_conversions_metric
                     FROM conversion_action WHERE conversion_action.status = 'ENABLED'"""):
        a = r.conversion_action
        live[str(a.id)] = {"name": a.name, "type": E(a.type_),
                           "category": E(a.category), "origin": E(a.origin),
                           "primary_for_goal": a.primary_for_goal,
                           "in_conv_metric": a.include_in_conversions_metric}
    changes = []
    for aid, meta in DEMOTE.items():
        cur = live.get(aid)
        if cur is None:
            sys.exit(f"ABORT: {aid} not found or not ENABLED")
        if cur["name"] != meta["name"]:
            sys.exit(f"ABORT: {aid} name is {cur['name']!r}, expected {meta['name']!r}")
        changes.append({"conversion_action_id": aid, "name": cur["name"],
                        "type": cur["type"], "category": cur["category"],
                        "from_primary_for_goal": cur["primary_for_goal"],
                        "to_primary_for_goal": False, "why": meta["why"]})
    plan = {
        "customer_id": CID, "exact_account_name": EXACT_NAME,
        "never_write_to_mcc": GM_MANAGER, "built_local": STAMP,
        "plan_name": PLAN_NAME, "approval_class": "update-conversion-action-primary-flag",
        "scope": "conversion_action.primary_for_goal ONLY",
        "nothing_deleted": True, "nothing_disabled": True,
        "no_budget_bid_keyword_ad_targeting_or_status_change": True,
        "bidding_impact": "NONE today. Every enabled campaign uses TARGET_SPEND "
                          "(Maximize Clicks with a CPC ceiling), which does not consume "
                          "conversion goals. This corrects REPORTING and prepares for "
                          "conversion-based bidding later.",
        "supersedes_note": "AMB-0918-CONV-1 / A3370F96FA6E demoted 7643656486 and "
                           "7643656075 on 2026-09-18. Both read primary_for_goal=true "
                           "again on 2026-09-23. change_event returned no CONVERSION_ACTION "
                           "rows for the window (it is capped near 30 days and lags), so "
                           "the reversal mechanism is NOT proven from the API. The leading "
                           "hypothesis is the WhatConverts Google Ads integration "
                           "re-asserting its own actions when its configuration is saved, "
                           "because the screenshots show WC Lead and WC Calls selected as "
                           "the integration's Lead and Call conversion names. If that is "
                           "right, this repair will revert again unless the WhatConverts "
                           "side is corrected too.",
        "keep_primary": KEEP_PRIMARY,
        "changes": changes,
        "operations": [{"op": "SET_CONVERSION_ACTION_SECONDARY",
                        "conversion_action_id": ch["conversion_action_id"],
                        "name": ch["name"],
                        "from": f"primary_for_goal={ch['from_primary_for_goal']}",
                        "to": "primary_for_goal=false",
                        "field_mask": "primary_for_goal"} for ch in changes],
        "rollback": "Set primary_for_goal=true on the same three ids. Nothing is removed, "
                    "disabled or reconfigured, so reversal is a single flag flip each.",
    }
    plan["operation_count"] = len(plan["operations"])
    plan["fingerprint"] = approval_code(plan)
    PLANS.mkdir(parents=True, exist_ok=True)
    (PLANS / f"{PLAN_NAME}.json").write_text(json.dumps(plan, indent=1, default=str),
                                             encoding="utf-8")
    print(f"WROTE {PLANS / (PLAN_NAME + '.json')}")
    print(f"APPROVE {PLAN_NAME} {plan['fingerprint']} {plan['operation_count']} "
          f"operations FOR {CID}")
    for ch in changes:
        print(f"  {ch['conversion_action_id']} {ch['name'][:44]:44s} "
              f"{ch['from_primary_for_goal']} -> False")
    return plan


def ops_for(c, plan):
    ops = []
    svc = c.get_service("ConversionActionService")
    for o in plan["operations"]:
        op = c.get_type("ConversionActionOperation")
        op.update.resource_name = svc.conversion_action_path(
            CID, o["conversion_action_id"])
        op.update.primary_for_goal = False
        op.update_mask.paths.append("primary_for_goal")
        ops.append(op)
    return ops


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()

    c = client()
    identity_gate(c, verbose=False)
    print(f"identity re-confirmed for {CID}")

    if args.build:
        build(c)
        return

    plan = json.loads((PLANS / f"{PLAN_NAME}.json").read_text(encoding="utf-8"))
    fp = plan.pop("fingerprint"); re_fp = approval_code(plan); plan["fingerprint"] = fp
    assert fp == re_fp, f"FINGERPRINT MISMATCH disk={fp} recomputed={re_fp}"
    print(f"fingerprint verified {fp}  ops={plan['operation_count']}")

    ops = ops_for(c, plan)
    r = c.get_type("MutateConversionActionsRequest")
    r.customer_id = CID
    r.operations.extend(ops)
    r.partial_failure = False
    r.validate_only = bool(args.validate)
    try:
        resp = c.get_service("ConversionActionService").mutate_conversion_actions(request=r)
    except Exception as ex:
        print(f"FAILED {str(ex)[:600]}")
        sys.exit(2)
    print(f"{'VALIDATED' if args.validate else 'COMMITTED'} {len(ops)} operations")

    if args.validate:
        print("EXTERNAL WRITES: 0")
        return

    # -------------------------------------------------------------- readback
    print("\n=== READBACK ===")
    ids = ",".join(list(DEMOTE) + list(KEEP_PRIMARY))
    rec = {"plan": PLAN_NAME, "fingerprint": fp,
           "when": datetime.datetime.now(TZ).isoformat(), "customer_id": CID,
           "assertions": [], "FAIL": 0,
           "committed": [x.resource_name for x in resp.results]}
    seen = {}
    for row in q(c, f"""SELECT conversion_action.id, conversion_action.name,
                        conversion_action.status, conversion_action.primary_for_goal,
                        conversion_action.include_in_conversions_metric
                        FROM conversion_action
                        WHERE conversion_action.id IN ({ids})"""):
        a = row.conversion_action
        seen[str(a.id)] = {"name": a.name, "status": E(a.status),
                           "primary": a.primary_for_goal,
                           "in_conv": a.include_in_conversions_metric}

    def check(label, ok, detail=""):
        rec["assertions"].append({"check": label, "pass": bool(ok),
                                  "detail": str(detail)[:200]})
        if not ok:
            rec["FAIL"] += 1
            print(f"   FAIL {label}: {detail}")

    for aid in DEMOTE:
        v = seen.get(aid, {})
        print(f"   {aid} {v.get('name','?')[:44]:44s} primary={v.get('primary')} "
              f"status={v.get('status')}")
        check(f"{aid} demoted", v.get("primary") is False, v.get("primary"))
        check(f"{aid} still ENABLED", v.get("status") == "ENABLED", v.get("status"))
    for aid in KEEP_PRIMARY:
        v = seen.get(aid, {})
        print(f"   {aid} {v.get('name','?')[:44]:44s} primary={v.get('primary')} "
              f"status={v.get('status')}")
        check(f"{aid} still Primary", v.get("primary") is True, v.get("primary"))
        check(f"{aid} still ENABLED", v.get("status") == "ENABLED", v.get("status"))

    biddable = []
    cg = {}
    for row in q(c, """SELECT customer_conversion_goal.category,
                       customer_conversion_goal.origin,
                       customer_conversion_goal.biddable
                       FROM customer_conversion_goal"""):
        g = row.customer_conversion_goal
        cg[f"{E(g.category)}|{E(g.origin)}"] = g.biddable
    for row in q(c, """SELECT conversion_action.id, conversion_action.name,
                       conversion_action.category, conversion_action.origin,
                       conversion_action.primary_for_goal
                       FROM conversion_action
                       WHERE conversion_action.status='ENABLED'"""):
        a = row.conversion_action
        if a.primary_for_goal and cg.get(f"{E(a.category)}|{E(a.origin)}"):
            biddable.append({"id": str(a.id), "name": a.name})
    rec["actually_biddable_after"] = biddable
    print(f"\n   actions that ACTUALLY drive bidding after the change: {len(biddable)}")
    for b in biddable:
        print(f"      {b['id']} {b['name']}")
    check("exactly 3 biddable paths remain", len(biddable) == 3, len(biddable))

    LIVE.mkdir(parents=True, exist_ok=True)
    p = LIVE / f"{PLAN_NAME}-{STAMP}.json"
    p.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(f"\n=== {len(rec['assertions'])} assertions, {rec['FAIL']} FAIL ===")
    print(f"WROTE {p}")


if __name__ == "__main__":
    main()
