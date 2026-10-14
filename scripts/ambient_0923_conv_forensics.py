#!/usr/bin/env python3
"""Ambient | 2026-09-23 | Forensics on the conversion-architecture discrepancy.

READ-ONLY. EXTERNAL WRITES: 0.

Four questions:
  1. AMB-0918-CONV-1 set WC Lead and WC Calls to Secondary on 2026-09-18, yet both read
     primary_for_goal=True today. WHO changed them back, and when?
  2. What is customers/2401959466/conversionActions/179, the account-level call
     conversion action? A short numeric id is not a normal account-created action.
  3. WC Lead shows activity in the last 90 days after previously reading zero all-time.
     When did uploads start, and are they accepted?
  4. Which actions are excluded from the Conversions metric while still flagged Primary -
     the combination that makes an action look like it bids when it contributes nothing.
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
    identity_gate(c, verbose=False)
    now = datetime.datetime.now(TZ)
    out = {"generated_local": now.isoformat(), "stamp": STAMP, "read_only": True,
           "external_writes": 0}

    # --------------------------------------------- 1. who re-promoted them
    print("=== 1. CHANGE HISTORY ON THE CONVERSION ACTIONS ===")
    lo = (now - datetime.timedelta(days=27)).strftime("%Y-%m-%d %H:%M:%S")
    hi = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    ev = []
    try:
        for r in q(c, f"""SELECT change_event.change_date_time, change_event.user_email,
                          change_event.client_type, change_event.change_resource_type,
                          change_event.change_resource_name,
                          change_event.resource_change_operation,
                          change_event.changed_fields
                          FROM change_event
                          WHERE change_event.change_date_time >= '{lo}'
                            AND change_event.change_date_time <= '{hi}'
                            AND change_event.change_resource_type = 'CONVERSION_ACTION'
                          ORDER BY change_event.change_date_time DESC
                          LIMIT 500"""):

            e = r.change_event
            ev.append({"when": e.change_date_time, "email": e.user_email,
                       "client": E(e.client_type),
                       "resource": e.change_resource_name.rsplit("/", 1)[-1],
                       "op": E(e.resource_change_operation),
                       "fields": list(e.changed_fields.paths)})
    except Exception as ex:
        ev = [{"error": str(ex)[:250]}]
    out["conversion_action_change_events"] = ev
    if not ev:
        print("   change_event returned NOTHING for CONVERSION_ACTION in the window.")
        print("   change_event is capped at ~30 days and lags by hours; absence here is")
        print("   not proof no change happened.")
    for e in ev[:30]:
        print(f"   {e.get('when')} {e.get('client','')[:22]:22s} {e.get('op',''):8s} "
              f"{e.get('resource','')} {e.get('fields')}")

    print("\n   --- change_status (resource-level, different retention) ---")
    cs = []
    try:
        lo2 = (now - datetime.timedelta(days=27)).strftime("%Y-%m-%d")
        for r in q(c, f"""SELECT change_status.last_change_date_time,
                          change_status.resource_type, change_status.resource_status
                          FROM change_status
                          WHERE change_status.last_change_date_time >= '{lo2}'
                          ORDER BY change_status.last_change_date_time DESC
                          LIMIT 300"""):
            cs.append({"when": r.change_status.last_change_date_time,
                       "type": E(r.change_status.resource_type),
                       "status": E(r.change_status.resource_status)})
    except Exception as ex:
        cs = [{"error": str(ex)[:200]}]
    agg = {}
    for x in cs:
        if "type" in x:
            agg[x["type"]] = agg.get(x["type"], 0) + 1
    print(f"   change_status rows by type: {agg}")
    out["change_status_rollup"] = agg

    # --------------------------------- 2. what is conversionActions/179
    print("\n=== 2. ACCOUNT-LEVEL CALL CONVERSION ACTION ===")
    found = {}
    for r in q(c, """SELECT conversion_action.id, conversion_action.name,
                     conversion_action.type, conversion_action.category,
                     conversion_action.status, conversion_action.origin,
                     conversion_action.owner_customer,
                     conversion_action.primary_for_goal,
                     conversion_action.phone_call_duration_seconds
                     FROM conversion_action WHERE conversion_action.id = 179"""):
        a = r.conversion_action
        found = {"id": str(a.id), "name": a.name, "type": E(a.type_),
                 "category": E(a.category), "status": E(a.status),
                 "origin": E(a.origin), "owner": a.owner_customer,
                 "primary_for_goal": a.primary_for_goal,
                 "call_duration": a.phone_call_duration_seconds}
    if found:
        for k, v in found.items():
            print(f"   {k:24s} {v}")
    else:
        print("   id 179 is NOT visible in this account's conversion_action list.")
        print("   That means it is a GOOGLE-OWNED system action, not one of Ambient's.")
    out["account_call_conversion_action_179"] = found or "not visible in this account"

    # --------------------------------------- 3. WC Lead / WC Calls by date
    print("\n=== 3. WC LEAD / WC CALLS ACTIVITY BY DATE (last 120 days) ===")
    lo3 = (now - datetime.timedelta(days=120)).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")
    byday = {}
    for r in q(c, f"""SELECT segments.date, segments.conversion_action,
                      segments.conversion_action_name,
                      metrics.all_conversions, metrics.conversions,
                      metrics.all_conversions_value
                      FROM customer
                      WHERE segments.date BETWEEN '{lo3}' AND '{today}'"""):
        aid = r.segments.conversion_action.rsplit("/", 1)[-1]
        if aid not in (WC_LEAD, WC_CALLS):
            continue
        d = byday.setdefault(r.segments.date, {})
        d[aid] = {"all": r.metrics.all_conversions, "conv": r.metrics.conversions,
                  "value": r.metrics.all_conversions_value}
    out["wc_activity_by_date"] = byday
    if not byday:
        print("   NO WhatConverts uploads recorded in 120 days.")
    for dte in sorted(byday):
        row = byday[dte]
        l = row.get(WC_LEAD, {})
        cl = row.get(WC_CALLS, {})
        print(f"   {dte}  WC Lead all={l.get('all',0):.2f} conv={l.get('conv',0):.2f} "
              f"val={l.get('value',0):.2f}   WC Calls all={cl.get('all',0):.2f}")

    # ------------------- 4. primary but excluded from the Conversions metric
    print("\n=== 4. PRIMARY FLAG vs include_in_conversions_metric ===")
    rows = []
    for r in q(c, """SELECT conversion_action.id, conversion_action.name,
                     conversion_action.status, conversion_action.type,
                     conversion_action.category, conversion_action.origin,
                     conversion_action.primary_for_goal,
                     conversion_action.include_in_conversions_metric
                     FROM conversion_action
                     WHERE conversion_action.status = 'ENABLED'"""):
        a = r.conversion_action
        rows.append({"id": str(a.id), "name": a.name, "type": E(a.type_),
                     "category": E(a.category), "origin": E(a.origin),
                     "primary": a.primary_for_goal,
                     "in_conv_metric": a.include_in_conversions_metric})
    out["primary_vs_metric"] = rows
    print(f"{'id':12s} {'P':3s} {'inConv':7s} {'type':20s} name")
    for x in sorted(rows, key=lambda y: (not y["primary"], y["name"])):
        flag = ""
        if x["primary"] and not x["in_conv_metric"]:
            flag = "   <<< PRIMARY but EXCLUDED from Conversions"
        print(f"{x['id']:12s} {'Y' if x['primary'] else '-':3s} "
              f"{'Y' if x['in_conv_metric'] else '-':7s} {x['type'][:20]:20s} "
              f"{x['name'][:38]}{flag}")

    # ------------------------------------- 5. overlap: what measures a form?
    print("\n=== 5. OVERLAP MAP - which actions measure the SAME underlying event ===")
    groups = {}
    for x in rows:
        key = x["category"]
        groups.setdefault(key, []).append(x)
    for k, v in sorted(groups.items()):
        prim = [y for y in v if y["primary"]]
        print(f"\n   {k}: {len(v)} actions, {len(prim)} PRIMARY")
        for y in v:
            print(f"      {'PRIMARY' if y['primary'] else '       '} {y['id']:12s} "
                  f"{y['type'][:20]:20s} {y['origin'][:14]:14s} {y['name'][:40]}")
    out["overlap_by_category"] = {k: [y["id"] for y in v] for k, v in groups.items()}

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"conv-forensics-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
