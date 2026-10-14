#!/usr/bin/env python3
"""Ambient | 2026-09-23b | Set the owner-specified conversion priorities.

Scope: conversion_action.primary_for_goal ONLY. No budget, bid, keyword, ad, targeting or
delivery-status change. Nothing deleted, nothing disabled, capture untouched.

PLAN A - execute now. Every change is either explicitly instructed or provably lossless.
PLAN B - built and validated, NOT executed. Each of its two changes would remove the only
         Primary measurement an event currently has, so each carries a release condition.

--build / --validate / --execute-a / --validate-b
"""
from __future__ import annotations
import sys, json, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-23b"
LIVE = ROOT / "receipts" / "live"
PLAN_A, PLAN_B = "AMB-0923B-CONV-A", "AMB-0923B-CONV-B"

PLAN_A_CHANGES = {
    "7643656486": {"name": "WC Lead", "to": True,
                   "why": "Owner instruction 2026-09-23: WC Lead MUST be Primary. This "
                          "supersedes AMB-0923-CONV-2, which demoted it. Its goal combo "
                          "CONTACT|WEBSITE is already biddable at account level and on "
                          "every enabled campaign, so Primary here genuinely takes "
                          "effect rather than being a label."},
    "7643656075": {"name": "WC Calls", "to": True,
                   "why": "Owner instruction 2026-09-23: WC Calls MUST be Primary. Its "
                          "goal combo CONTACT|CALL_FROM_ADS is already biddable. NOTE: it "
                          "has recorded zero conversions to date; Primary status does not "
                          "make it deliver, and the delivery fault is diagnosed "
                          "separately."},
    "6885576934": {"name": "Ambient Cooling - Lp - Phone call leads", "to": False,
                   "why": "Native WEBSITE_CALL action overlapping the WC call route. Safe "
                          "to demote NOW because it has recorded ZERO conversions for its "
                          "entire lifetime, so no measurement is lost. Stays ENABLED as a "
                          "diagnostic."},
}

# Held back deliberately. Each would blank out the ONLY Primary measurement its event has.
PLAN_B_CHANGES = {
    "6885463625": {
        "name": "Ambient Cooling - LP -Submit Lead Forms", "to": False,
        "why": "Native WEBPAGE form action. It DOES overlap WC Lead - but only on the "
               "offer subdomain. WhatConverts profile 105803 registers one form selector, "
               "#gform_1, so it has never captured a main-site #gform_2 submission. 13 of "
               "the 18 currently enabled heating ad groups point at MAIN-SITE pages. "
               "Demoting this today leaves those 13 ad groups with NO Primary measurement "
               "for a form submission at all.",
        "release_condition": "Execute once a labelled main-site test submission produces a "
                             "Web Form lead in WhatConverts profile 105803 carrying the "
                             "main-site field labels.",
        "measured_loss_if_executed_today": "5 conversions / 90 days, and all future "
                                           "main-site form submissions.",
    },
    "1068114183": {
        "name": "Calls from ads", "to": False,
        "why": "Native AD_CALL action overlapping the WC Calls route. WC Calls has "
               "recorded zero conversions ever, so demoting this today leaves call-asset "
               "calls with NO Primary measurement.",
        "release_condition": "Execute once WC Calls records its first accepted upload.",
        "measured_loss_if_executed_today": "5 conversions / 90 days.",
    },
}
UNCHANGED = {
    "7389995485": "GA4 form_submission import - stays SECONDARY per instruction.",
}


def snapshot(c):
    live = {}
    for r in q(c, """SELECT conversion_action.id, conversion_action.name,
                     conversion_action.status, conversion_action.type,
                     conversion_action.category, conversion_action.origin,
                     conversion_action.primary_for_goal,
                     conversion_action.include_in_conversions_metric
                     FROM conversion_action WHERE conversion_action.status='ENABLED'"""):
        a = r.conversion_action
        live[str(a.id)] = {"name": a.name, "type": E(a.type_), "category": E(a.category),
                           "origin": E(a.origin), "primary": a.primary_for_goal,
                           "in_conv_metric": a.include_in_conversions_metric}
    return live


def goals(c):
    g = {}
    for r in q(c, """SELECT customer_conversion_goal.category,
                     customer_conversion_goal.origin,
                     customer_conversion_goal.biddable FROM customer_conversion_goal"""):
        x = r.customer_conversion_goal
        g[f"{E(x.category)}|{E(x.origin)}"] = x.biddable
    return g


def build(c):
    live = snapshot(c)
    gl = goals(c)
    for name, table in ((PLAN_A, PLAN_A_CHANGES), (PLAN_B, PLAN_B_CHANGES)):
        changes = []
        for aid, meta in table.items():
            cur = live.get(aid)
            if cur is None:
                sys.exit(f"ABORT: {aid} not found or not ENABLED")
            if cur["name"] != meta["name"]:
                sys.exit(f"ABORT: {aid} is {cur['name']!r}, expected {meta['name']!r}")
            key = f"{cur['category']}|{cur['origin']}"
            changes.append({
                "conversion_action_id": aid, "name": cur["name"], "type": cur["type"],
                "category": cur["category"], "origin": cur["origin"],
                "goal_key": key, "goal_biddable": gl.get(key, False),
                "from_primary_for_goal": cur["primary"],
                "to_primary_for_goal": meta["to"],
                "takes_effect": bool(meta["to"] and gl.get(key, False)),
                "why": meta["why"],
                **({"release_condition": meta["release_condition"],
                    "measured_loss_if_executed_today":
                        meta["measured_loss_if_executed_today"]}
                   if "release_condition" in meta else {})})
        plan = {
            "customer_id": CID, "exact_account_name": EXACT_NAME,
            "never_write_to_mcc": GM_MANAGER, "built_local": STAMP,
            "plan_name": name,
            "approval_class": "update-conversion-action-primary-flag",
            "scope": "conversion_action.primary_for_goal ONLY",
            "nothing_deleted": True, "nothing_disabled": True, "capture_untouched": True,
            "no_budget_bid_keyword_ad_targeting_or_status_change": True,
            "supersedes": "AMB-0923-CONV-2 / 2550EA4C9BDC for the two WC actions",
            "unchanged_by_instruction": UNCHANGED,
            "bidding_impact": "None today: every enabled campaign is TARGET_SPEND "
                              "(Maximize Clicks with a CPC ceiling), which does not "
                              "consume conversion goals. This governs REPORTING and "
                              "prepares for conversion bidding.",
            "changes": changes,
            "operations": [{"op": "SET_CONVERSION_ACTION_PRIMARY_FLAG",
                            "conversion_action_id": ch["conversion_action_id"],
                            "name": ch["name"],
                            "from": f"primary_for_goal={ch['from_primary_for_goal']}",
                            "to": f"primary_for_goal={ch['to_primary_for_goal']}",
                            "field_mask": "primary_for_goal"} for ch in changes],
            "rollback": "Flip primary_for_goal back on the same ids. Nothing is removed "
                        "or reconfigured.",
        }
        if name == PLAN_B:
            plan["DO_NOT_EXECUTE_YET"] = (
                "Both changes remove the ONLY Primary measurement their event currently "
                "has. Execute each only when its release_condition is met.")
        plan["operation_count"] = len(plan["operations"])
        plan["fingerprint"] = approval_code(plan)
        PLANS.mkdir(parents=True, exist_ok=True)
        (PLANS / f"{name}.json").write_text(json.dumps(plan, indent=1, default=str),
                                            encoding="utf-8")
        print(f"\n{name}  fingerprint {plan['fingerprint']}  "
              f"{plan['operation_count']} operations")
        for ch in changes:
            eff = "" if ch["to_primary_for_goal"] is False else (
                "  (goal biddable, takes effect)" if ch["takes_effect"]
                else "  (goal NOT biddable - would be label only)")
            print(f"   {ch['conversion_action_id']} {ch['name'][:42]:42s} "
                  f"{ch['from_primary_for_goal']} -> {ch['to_primary_for_goal']}{eff}")


def apply(c, name, dry):
    plan = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8"))
    fp = plan.pop("fingerprint"); re_fp = approval_code(plan); plan["fingerprint"] = fp
    assert fp == re_fp, f"FINGERPRINT MISMATCH disk={fp} recomputed={re_fp}"
    print(f"{name}: fingerprint {fp} verified, {plan['operation_count']} operations")
    svc = c.get_service("ConversionActionService")
    ops = []
    for o in plan["operations"]:
        op = c.get_type("ConversionActionOperation")
        op.update.resource_name = svc.conversion_action_path(
            CID, o["conversion_action_id"])
        op.update.primary_for_goal = o["to"].endswith("True")
        op.update_mask.paths.append("primary_for_goal")
        ops.append(op)
    r = c.get_type("MutateConversionActionsRequest")
    r.customer_id = CID
    r.operations.extend(ops)
    r.partial_failure = False
    r.validate_only = dry
    try:
        svc.mutate_conversion_actions(request=r)
    except Exception as ex:
        print(f"FAILED {str(ex)[:500]}")
        sys.exit(2)
    print(f"  {'VALIDATED' if dry else 'COMMITTED'} {len(ops)} operations")
    return plan


def readback(c, plan):
    print("\n=== READBACK ===")
    ids = [o["conversion_action_id"] for o in plan["operations"]] + \
          list(PLAN_B_CHANGES) + list(UNCHANGED)
    live = snapshot(c)
    gl = goals(c)
    rec = {"plan": plan["plan_name"], "fingerprint": plan["fingerprint"],
           "when": datetime.datetime.now(TZ).isoformat(), "assertions": [], "FAIL": 0}

    def check(label, ok, detail=""):
        rec["assertions"].append({"check": label, "pass": bool(ok),
                                  "detail": str(detail)[:200]})
        if not ok:
            rec["FAIL"] += 1
            print(f"   FAIL {label}: {detail}")

    for o in plan["operations"]:
        aid = o["conversion_action_id"]
        want = o["to"].endswith("True")
        v = live.get(aid, {})
        print(f"   {aid} {v.get('name','?')[:42]:42s} primary={v.get('primary')} "
              f"inConv={v.get('in_conv_metric')} status=ENABLED")
        check(f"{aid} primary_for_goal={want}", v.get("primary") is want, v.get("primary"))
    for aid, why in UNCHANGED.items():
        v = live.get(aid, {})
        check(f"{aid} still Secondary", v.get("primary") is False, v.get("primary"))

    bid = []
    for aid, v in live.items():
        if v["primary"] and gl.get(f"{v['category']}|{v['origin']}"):
            bid.append({"id": aid, "name": v["name"], "type": v["type"]})
    rec["actually_biddable_after"] = bid
    print(f"\n   actions that ACTUALLY drive bidding now: {len(bid)}")
    for b in sorted(bid, key=lambda x: x["name"]):
        print(f"      {b['id']} {b['type'][:22]:22s} {b['name']}")
    check("WC Lead biddable", any(b["id"] == "7643656486" for b in bid))
    check("WC Calls biddable", any(b["id"] == "7643656075" for b in bid))

    LIVE.mkdir(parents=True, exist_ok=True)
    p = LIVE / f"{plan['plan_name']}-{STAMP}.json"
    p.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(f"\n=== {len(rec['assertions'])} assertions, {rec['FAIL']} FAIL ===")
    print(f"WROTE {p}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--validate-b", action="store_true")
    ap.add_argument("--execute-a", action="store_true")
    args = ap.parse_args()
    c = client()
    identity_gate(c, verbose=False)
    print(f"identity re-confirmed {CID}")
    if args.build:
        build(c)
    elif args.validate:
        apply(c, PLAN_A, dry=True)
        print("EXTERNAL WRITES: 0")
    elif args.validate_b:
        apply(c, PLAN_B, dry=True)
        print("PLAN B VALIDATED ONLY - NOT EXECUTED. EXTERNAL WRITES: 0")
    elif args.execute_a:
        plan = apply(c, PLAN_A, dry=False)
        readback(c, plan)


if __name__ == "__main__":
    main()
