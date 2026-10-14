#!/usr/bin/env python3
"""Ambient | 2026-09-23 | Full conversion-action + goal architecture audit.

READ-ONLY. EXTERNAL WRITES: 0.

Answers the questions the screenshots cannot:
  * what every conversion action actually IS (id, type, category, status, counting,
    attribution, primary_for_goal, enhanced conversions, lookback windows)
  * whether "Primary" actually feeds bidding, which is decided by the CUSTOMER and
    CAMPAIGN conversion GOAL layers, not by the primary_for_goal flag alone
  * which actions have recent activity and which are inert
  * the account-level call reporting / call conversion defaults
  * per-campaign goal overrides
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-23"
WC_LEAD, WC_CALLS = "7643656486", "7643656075"


def main():
    c = client()
    identity_gate(c, verbose=True)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0}

    # ---------------------------------------------------- 1. every action
    print("\n=== 1. EVERY CONVERSION ACTION ===")
    acts = {}
    for r in q(c, """SELECT conversion_action.id, conversion_action.name,
                     conversion_action.status, conversion_action.type,
                     conversion_action.category, conversion_action.origin,
                     conversion_action.primary_for_goal,
                     conversion_action.counting_type,
                     conversion_action.attribution_model_settings.attribution_model,
                     conversion_action.attribution_model_settings.data_driven_model_status,
                     conversion_action.click_through_lookback_window_days,
                     conversion_action.view_through_lookback_window_days,
                     conversion_action.phone_call_duration_seconds,
                     conversion_action.include_in_conversions_metric,
                     conversion_action.value_settings.default_value,
                     conversion_action.value_settings.always_use_default_value
                     FROM conversion_action"""):
        a = r.conversion_action
        acts[str(a.id)] = {
            "name": a.name, "status": E(a.status), "type": E(a.type_),
            "category": E(a.category), "origin": E(a.origin),
            "primary_for_goal": a.primary_for_goal,
            "counting": E(a.counting_type),
            "attribution": E(a.attribution_model_settings.attribution_model),
            "ddm_status": E(a.attribution_model_settings.data_driven_model_status),
            "click_lookback": a.click_through_lookback_window_days,
            "view_lookback": a.view_through_lookback_window_days,
            "call_duration_secs": a.phone_call_duration_seconds,
            "include_in_conversions_metric": a.include_in_conversions_metric,
            "default_value": a.value_settings.default_value,
            "always_default": a.value_settings.always_use_default_value}
    out["conversion_actions"] = acts
    print(f"   {len(acts)} actions total")
    print(f"{'id':12s} {'st':8s} {'P?':3s} {'type':22s} {'category':18s} {'count':10s} "
          f"{'dur':4s} name")
    for k, v in sorted(acts.items(), key=lambda x: (x[1]["status"], x[1]["name"])):
        if v["status"] == "REMOVED":
            continue
        print(f"{k:12s} {v['status'][:8]:8s} {'YES' if v['primary_for_goal'] else '-':3s} "
              f"{v['type'][:22]:22s} {v['category'][:18]:18s} {v['counting'][:10]:10s} "
              f"{v['call_duration_secs'] or '':4} {v['name'][:40]}")

    # --------------------------------------- 2. the two WhatConverts actions
    print("\n=== 2. THE TWO WHATCONVERTS ACTIONS (screenshot discrepancy) ===")
    for k in (WC_LEAD, WC_CALLS):
        v = acts.get(k, {})
        print(f"\n   {k} {v.get('name')}")
        for f in ("status", "type", "category", "origin", "primary_for_goal", "counting",
                  "attribution", "click_lookback", "view_lookback", "call_duration_secs",
                  "include_in_conversions_metric", "default_value", "always_default"):
            print(f"      {f:32s} {v.get(f)}")
    out["wc_actions_live_state"] = {k: acts.get(k) for k in (WC_LEAD, WC_CALLS)}

    # ------------------------------------------- 3. customer-level goal layer
    print("\n=== 3. CUSTOMER CONVERSION GOALS (what actually drives bidding) ===")
    cg = {}
    for r in q(c, """SELECT customer_conversion_goal.category,
                     customer_conversion_goal.origin,
                     customer_conversion_goal.biddable FROM customer_conversion_goal"""):
        g = r.customer_conversion_goal
        cg[f"{E(g.category)}|{E(g.origin)}"] = g.biddable
    out["customer_conversion_goals"] = cg
    for k, v in sorted(cg.items()):
        if v:
            print(f"   BIDDABLE     {k}")
    nb = [k for k, v in cg.items() if not v]
    print(f"   not biddable: {len(nb)} combinations")

    # --------------------------------------------- 4. campaign goal overrides
    print("\n=== 4. CAMPAIGN-LEVEL GOAL OVERRIDES ===")
    ccg = {}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                     campaign_conversion_goal.category,
                     campaign_conversion_goal.origin,
                     campaign_conversion_goal.biddable
                     FROM campaign_conversion_goal
                     WHERE campaign.status != 'REMOVED'"""):
        g = r.campaign_conversion_goal
        if g.biddable:
            ccg.setdefault(str(r.campaign.id),
                           {"name": r.campaign.name, "status": E(r.campaign.status),
                            "biddable": []})["biddable"].append(
                f"{E(g.category)}|{E(g.origin)}")
    out["campaign_conversion_goals_biddable"] = ccg
    for cid, v in sorted(ccg.items()):
        print(f"   {cid} {v['status']:8s} {len(v['biddable']):2d} biddable  "
              f"{v['name'][:44]}")
        for b in sorted(v["biddable"]):
            print(f"        {b}")

    # ---------------------------------- 5. which actions map to biddable goals
    print("\n=== 5. DOES 'PRIMARY' ACTUALLY FEED BIDDING? ===")
    verdict = {}
    for k, v in acts.items():
        if v["status"] != "ENABLED":
            continue
        key = f"{v['category']}|{v['origin']}"
        biddable = cg.get(key, False)
        verdict[k] = {"name": v["name"], "primary_flag": v["primary_for_goal"],
                      "goal_key": key, "goal_biddable": biddable,
                      "actually_bids": bool(v["primary_for_goal"] and biddable)}
    out["bidding_reality"] = verdict
    print(f"{'id':12s} {'flag':6s} {'goal':8s} {'BIDS?':7s} name")
    for k, v in sorted(verdict.items(), key=lambda x: (not x[1]["actually_bids"],
                                                       x[1]["name"])):
        print(f"{k:12s} {str(v['primary_flag'])[:5]:6s} "
              f"{str(v['goal_biddable'])[:5]:8s} "
              f"{'YES' if v['actually_bids'] else 'no':7s} {v['name'][:44]}")
    bids = [k for k, v in verdict.items() if v["actually_bids"]]
    out["actually_biddable_action_ids"] = bids
    print(f"\n   actions that ACTUALLY drive bidding: {len(bids)}")

    # ------------------------------------------- 6. account call settings
    print("\n=== 6. ACCOUNT CALL REPORTING / CONVERSION DEFAULTS ===")
    for r in q(c, """SELECT customer.id,
                     customer.call_reporting_setting.call_reporting_enabled,
                     customer.call_reporting_setting.call_conversion_reporting_enabled,
                     customer.call_reporting_setting.call_conversion_action,
                     customer.conversion_tracking_setting.conversion_tracking_id,
                     customer.conversion_tracking_setting.google_ads_conversion_customer,
                     customer.conversion_tracking_setting.conversion_tracking_status,
                     customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
                     customer.conversion_tracking_setting.accepted_customer_data_terms
                     FROM customer"""):
        cr = r.customer.call_reporting_setting
        ct = r.customer.conversion_tracking_setting
        d = {"call_reporting_enabled": cr.call_reporting_enabled,
             "call_conversion_reporting_enabled": cr.call_conversion_reporting_enabled,
             "account_call_conversion_action": cr.call_conversion_action or None,
             "conversion_tracking_id": ct.conversion_tracking_id,
             "conversion_customer": ct.google_ads_conversion_customer,
             "tracking_status": E(ct.conversion_tracking_status),
             "enhanced_conversions_for_leads": ct.enhanced_conversions_for_leads_enabled,
             "accepted_customer_data_terms": ct.accepted_customer_data_terms}
        out["account_call_and_tracking"] = d
        for kk, vv in d.items():
            print(f"   {kk:42s} {vv}")

    # ------------------------------------------- 7. recent activity per action
    print("\n=== 7. ACTIVITY: last 90 days and September, per action ===")
    now = datetime.datetime.now(TZ)
    lo90 = (now - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")
    act90, actsep = {}, {}
    for tag, a, b in (("d90", lo90, today), ("sep", "2026-09-01", today)):
        store = act90 if tag == "d90" else actsep
        for r in q(c, f"""SELECT segments.conversion_action,
                          segments.conversion_action_name,
                          metrics.all_conversions, metrics.conversions,
                          metrics.all_conversions_value
                          FROM customer
                          WHERE segments.date BETWEEN '{a}' AND '{b}'"""):
            aid = r.segments.conversion_action.rsplit("/", 1)[-1]
            d = store.setdefault(aid, {"name": r.segments.conversion_action_name,
                                       "all_conv": 0.0, "conv": 0.0, "value": 0.0})
            d["all_conv"] += r.metrics.all_conversions
            d["conv"] += r.metrics.conversions
            d["value"] += r.metrics.all_conversions_value
    out["activity_90d"] = act90
    out["activity_september"] = actsep
    print(f"{'id':12s} {'90d all':>9s} {'90d conv':>9s} {'Sep all':>9s} {'Sep conv':>9s}  name")
    allids = sorted(set(act90) | set(actsep) | {k for k, v in acts.items()
                                                if v["status"] == "ENABLED"})
    for k in allids:
        a9 = act90.get(k, {})
        asp = actsep.get(k, {})
        nm = a9.get("name") or asp.get("name") or acts.get(k, {}).get("name", "?")
        print(f"{k:12s} {a9.get('all_conv',0):9.2f} {a9.get('conv',0):9.2f} "
              f"{asp.get('all_conv',0):9.2f} {asp.get('conv',0):9.2f}  {nm[:40]}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"conv-audit-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
