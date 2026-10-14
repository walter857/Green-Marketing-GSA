#!/usr/bin/env python3
"""STAGE A COMPLETION - APG-0916-CONV-A2, fingerprint D1CAB205DDDA.

Approval received 2026-09-16: "APPROVE APG CREATE-PAUSED D1CAB205DDDA"
Creates the 2 call conversion actions with the API-forced field corrections.
Never touches 7772803337. One mutate per object. Stops on first failure.
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, GM_MANAGER, TZ, RECEIPTS, client, q, write, E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402

PLAN = ROOT / "clients/apogee-lawns/plans/APG-0916-CONV-A2.yaml"
EXPECTED_FP = "D1CAB205DDDA"
OBJ1_ID = "7772803337"

c = client()
created: list[dict] = []
fails: list[str] = []


def gate(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' -> ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)


print("=" * 78 + "\nPRE-EXECUTION GATES\n" + "=" * 78)
plan = load_yaml(str(PLAN))
gate(approval_code(plan) == EXPECTED_FP, "fingerprint matches approval", approval_code(plan))

wo = load_yaml(str(ROOT / "clients/apogee-lawns/work-order.yaml"))
cl = load_yaml(str(ROOT / "clients/apogee-lawns/client.yaml"))
gate(not validate_work_order(wo, cl), "validate_work_order clean")

row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
                     customer.test_account, customer.time_zone, customer.currency_code,
                     customer.conversion_tracking_setting.google_ads_conversion_customer
              FROM customer""")[0].customer
gate(str(row.id) == CID, "customer.id", str(row.id))
gate(row.descriptive_name == EXACT_NAME, "descriptive_name", row.descriptive_name)
gate(not row.manager and not row.test_account, "not manager / not test")
gate((row.conversion_tracking_setting.google_ads_conversion_customer or "").split("/")[-1] == CID,
     "conversion ownership is this child")
links = {x.customer_manager_link.manager_customer.split("/")[-1]: E(x.customer_manager_link.status)
         for x in q(c, "SELECT customer_manager_link.manager_customer, customer_manager_link.status FROM customer_manager_link")}
gate(links.get(GM_MANAGER) == "ACTIVE", "manager link ACTIVE")

existing = q(c, "SELECT conversion_action.id, conversion_action.name, conversion_action.type FROM conversion_action")
ids_now = sorted(str(r.conversion_action.id) for r in existing)
gate(ids_now == [OBJ1_ID], f"exactly 1 existing action and it is {OBJ1_ID}", str(ids_now))
call_types = [r for r in existing if E(r.conversion_action.type_) in ("AD_CALL", "WEBSITE_CALL", "CLICK_TO_CALL")]
gate(not call_types, "no pre-existing call-type conversion action", str(len(call_types)))

if fails:
    sys.exit("\nHARD STOP. Gates failed: " + "; ".join(fails))
print("\nALL GATES PASS. Issuing 2 create operations.\n")

svc = c.get_service("ConversionActionService")
ET, EC = c.enums.ConversionActionTypeEnum, c.enums.ConversionActionCategoryEnum
ES, ECo = c.enums.ConversionActionStatusEnum, c.enums.ConversionActionCountingTypeEnum
EA = c.enums.AttributionModelEnum

SPECS = [
    (2, "Call | Permanent Lights | Ads | 60s", "AD_CALL"),
    (3, "Call | Permanent Lights | Website | 60s", "WEBSITE_CALL"),
]


def detail(exc):
    out = []
    f = getattr(exc, "failure", None)
    if f:
        for e in f.errors:
            loc = ".".join(x.field_name for x in e.location.field_path_elements) if e.location and e.location.field_path_elements else ""
            out.append(f"{e.message} @ '{loc}'")
    return " | ".join(out) or str(exc)[:300]


for ordinal, name, type_name in SPECS:
    print(f"--- object {ordinal}: {name}  ({type_name})")
    op = c.get_type("ConversionActionOperation")
    ca = op.create
    ca.name = name
    ca.type_ = getattr(ET, type_name)
    ca.category = EC.PHONE_CALL_LEAD
    ca.status = ES.ENABLED
    ca.primary_for_goal = False
    ca.counting_type = ECo.ONE_PER_CLICK
    ca.click_through_lookback_window_days = 30
    # view_through_lookback_window_days DELIBERATELY NOT SET (API forbids it here)
    ca.attribution_model_settings.attribution_model = EA.GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN
    ca.value_settings.default_value = 0.0
    ca.value_settings.always_use_default_value = True   # API requires true for call types
    ca.phone_call_duration_seconds = 60
    try:
        resp = svc.mutate_conversion_actions(customer_id=CID, operations=[op])
        rn = resp.results[0].resource_name
        created.append({"ordinal": ordinal, "name": name, "resource_name": rn, "id": rn.split("/")[-1]})
        print(f"    CREATED {rn}")
    except Exception as exc:  # noqa: BLE001
        d = detail(exc)
        print(f"    FAILED: {d[:400]}")
        print("\nPARTIAL FAILURE - STOPPING. Created so far:")
        for x in created:
            print(f"    {x['ordinal']}. {x['id']}  {x['name']}")
        write(RECEIPTS / "2026-09-16-stageA2-PARTIAL-FAILURE.json",
              {"created": created, "failed_ordinal": ordinal, "error": d[:2000],
               "when": datetime.datetime.now(TZ).isoformat()})
        sys.exit(2)

print(f"\n{len(created)} objects created.\n")
print("=" * 78 + "\nFULL STAGE A READBACK (all 3 actions)\n" + "=" * 78)

rows = q(c, """
    SELECT conversion_action.id, conversion_action.resource_name, conversion_action.name,
           conversion_action.status, conversion_action.type, conversion_action.category,
           conversion_action.origin, conversion_action.primary_for_goal,
           conversion_action.counting_type,
           conversion_action.click_through_lookback_window_days,
           conversion_action.view_through_lookback_window_days,
           conversion_action.attribution_model_settings.attribution_model,
           conversion_action.attribution_model_settings.data_driven_model_status,
           conversion_action.value_settings.default_value,
           conversion_action.value_settings.always_use_default_value,
           conversion_action.phone_call_duration_seconds,
           conversion_action.include_in_conversions_metric,
           conversion_action.owner_customer, conversion_action.tag_snippets
    FROM conversion_action
    ORDER BY conversion_action.id
""")
EXPECT = {
    "Lead | Permanent Lights | Form Submit | Thank You": ("WEBPAGE", "SUBMIT_LEAD_FORM", 0),
    "Call | Permanent Lights | Ads | 60s": ("AD_CALL", "PHONE_CALL_LEAD", 60),
    "Call | Permanent Lights | Website | 60s": ("WEBSITE_CALL", "PHONE_CALL_LEAD", 60),
}
readback, qa_fail = [], 0
for r in rows:
    a = r.conversion_action
    et, ec_, ed = EXPECT.get(a.name, ("?", "?", 0))
    labels = sorted({m for t in a.tag_snippets for m in re.findall(r"AW-\d+/[A-Za-z0-9_\-]+", t.event_snippet or "")})
    rec = {"id": str(a.id), "resource_name": a.resource_name, "name": a.name,
           "status": E(a.status), "type": E(a.type_), "category": E(a.category),
           "origin": E(a.origin), "primary_for_goal": a.primary_for_goal,
           "counting_type": E(a.counting_type),
           "click_window_days": a.click_through_lookback_window_days,
           "view_window_days": a.view_through_lookback_window_days,
           "attribution_model": E(a.attribution_model_settings.attribution_model),
           "ddm_status": E(a.attribution_model_settings.data_driven_model_status),
           "default_value": a.value_settings.default_value,
           "always_use_default_value": a.value_settings.always_use_default_value,
           "phone_call_duration_seconds": a.phone_call_duration_seconds,
           "include_in_conversions_metric": a.include_in_conversions_metric,
           "owner": (a.owner_customer or "").split("/")[-1],
           "send_to": labels}
    checks = {"type": rec["type"] == et, "category": rec["category"] == ec_,
              "ENABLED": rec["status"] == "ENABLED",
              "SECONDARY": rec["primary_for_goal"] is False,
              "ONE_PER_CLICK": rec["counting_type"] == "ONE_PER_CLICK",
              "click_window_30": rec["click_window_days"] == 30,
              "value_0": float(rec["default_value"]) == 0.0,
              "duration": (rec["phone_call_duration_seconds"] == ed) if ed else True,
              "owner": rec["owner"] == CID}
    bad = [k for k, v in checks.items() if not v]
    qa_fail += len(bad)
    rec["qa"] = "PASS" if not bad else "FAIL: " + ",".join(bad)
    readback.append(rec)
    print(f"\n  {rec['id']}  {rec['name']}")
    print(f"    {rec['type']}/{rec['category']}  origin={rec['origin']}  status={rec['status']}")
    print(f"    SECONDARY={rec['primary_for_goal'] is False}  counting={rec['counting_type']}  "
          f"click={rec['click_window_days']}d  view={rec['view_window_days']}")
    print(f"    attribution={rec['attribution_model']} ddm={rec['ddm_status']}")
    print(f"    value default={rec['default_value']} always_use={rec['always_use_default_value']}  "
          f"duration={rec['phone_call_duration_seconds']}s  in_conv_metric={rec['include_in_conversions_metric']}")
    print(f"    send_to={rec['send_to'] or '(none - expected for call types)'}")
    print(f"    QA: {rec['qa']}")

cust = q(c, """SELECT customer.conversion_tracking_setting.conversion_tracking_status,
                      customer.call_reporting_setting.call_conversion_action,
                      customer.call_reporting_setting.call_reporting_enabled
               FROM customer""")[0].customer
goals = q(c, "SELECT customer_conversion_goal.category, customer_conversion_goal.origin, customer_conversion_goal.biddable FROM customer_conversion_goal")
goal_rows = [{"category": E(g.customer_conversion_goal.category),
              "origin": E(g.customer_conversion_goal.origin),
              "biddable": g.customer_conversion_goal.biddable} for g in goals]
biddable = sorted({g["category"] for g in goal_rows if g["biddable"]})

print("\n" + "=" * 78)
print(f"READBACK QA: {len(readback)}/3 actions, {qa_fail} field failures")
print("=" * 78)
print(f"  conversion_tracking_status : {E(cust.conversion_tracking_setting.conversion_tracking_status)}")
print(f"  call_reporting_enabled     : {cust.call_reporting_setting.call_reporting_enabled}")
print(f"  call_conversion_action ptr : {cust.call_reporting_setting.call_conversion_action or '(none)'}")
print(f"  customer_conversion_goals  : {len(goal_rows)} rows; biddable categories = {biddable}")
for g in goal_rows:
    print(f"      {g['category']:<20} origin={g['origin']:<10} biddable={g['biddable']}")

write(RECEIPTS / "2026-09-16-stageA-COMPLETE-receipt.json", {
    "plans": ["APG-0916-CONV-A (9BA1F4AE3CCA)", "APG-0916-CONV-A2 (D1CAB205DDDA)"],
    "executed_local": datetime.datetime.now(TZ).isoformat(),
    "customer_id": CID, "account_name": EXACT_NAME,
    "scope_approved_by": wo["work_order"]["scope_approval"]["approved_by"],
    "total_mutations": 3, "deletes_or_removes": 0, "enables": 0,
    "created_this_run": created, "readback": readback, "readback_field_failures": qa_fail,
    "conversion_tracking_status": E(cust.conversion_tracking_setting.conversion_tracking_status),
    "call_reporting_enabled": cust.call_reporting_setting.call_reporting_enabled,
    "call_conversion_action_pointer": cust.call_reporting_setting.call_conversion_action,
    "customer_conversion_goals": goal_rows, "biddable_goal_categories": biddable,
})
print("\nSTAGE A COMPLETE." if qa_fail == 0 else "\nSTAGE A COMPLETE WITH QA FAILURES.")
