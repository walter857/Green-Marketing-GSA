#!/usr/bin/env python3
"""STAGE A EXECUTION - APG-0916-CONV-A, fingerprint 9BA1F4AE3CCA.

Approval received 2026-09-16: "APPROVE APG CREATE-PAUSED 9BA1F4AE3CCA"

Creates exactly 3 conversion actions, all SECONDARY, on child 8164626278.
Each object is its own mutate call so a partial failure is precisely attributable.
STOPS on the first failure and inventories what was created. Never reruns blindly.
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, GM_MANAGER, TZ, RECEIPTS, client, q, write, E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

PLAN_PATH = ROOT / "clients/apogee-lawns/plans/APG-0916-CONV-A.yaml"
EXPECTED_FP = "9BA1F4AE3CCA"
APPROVAL = "APPROVE APG CREATE-PAUSED 9BA1F4AE3CCA"

created: list[dict] = []
c = client()

# =====================================================================
# GATE 1-5  (everything must pass before a single mutate is issued)
# =====================================================================
print("=" * 78)
print("PRE-EXECUTION GATES")
print("=" * 78)
fails = []


def gate(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' -> ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)


# --- fingerprint ------------------------------------------------------
plan = load_yaml(str(PLAN_PATH))
fp = approval_code(plan)
gate(fp == EXPECTED_FP, "plan fingerprint matches the approval", f"{fp}")

# --- work order -------------------------------------------------------
from gm_gsa.work_orders import validate_work_order  # noqa: E402
wo = load_yaml(str(ROOT / "clients/apogee-lawns/work-order.yaml"))
cl = load_yaml(str(ROOT / "clients/apogee-lawns/client.yaml"))
errs = validate_work_order(wo, cl)
gate(not errs, "validate_work_order returns no errors", f"{len(errs)} errors")
sc = wo["work_order"]["scope_approval"]
gate(sc.get("approved") is True, "scope_approval.approved is true")
gate(bool(str(sc.get("approved_by", "")).strip()) and "[[" not in str(sc.get("approved_by")),
     "scope_approval.approved_by is a real name", str(sc.get("approved_by")))

# --- fresh identity ---------------------------------------------------
row = q(c, """
    SELECT customer.id, customer.descriptive_name, customer.currency_code,
           customer.time_zone, customer.manager, customer.test_account, customer.status,
           customer.conversion_tracking_setting.google_ads_conversion_customer,
           customer.conversion_tracking_setting.cross_account_conversion_tracking_id
    FROM customer
""")[0].customer
cts = row.conversion_tracking_setting
gate(str(row.id) == CID, "customer.id == 8164626278", str(row.id))
gate(row.descriptive_name == EXACT_NAME, "descriptive_name exact match", row.descriptive_name)
gate(not row.manager, "not a manager account")
gate(not row.test_account, "not a test account")
gate(row.time_zone == "America/Chicago", "time zone", row.time_zone)
gate(row.currency_code == "USD", "currency", row.currency_code)
owner = (cts.google_ads_conversion_customer or "").split("/")[-1]
gate(owner == CID, "conversion ownership is this child", owner)
gate(str(cts.cross_account_conversion_tracking_id) == "0", "no cross-account conversion tracking")

links = {x.customer_manager_link.manager_customer.split("/")[-1]: E(x.customer_manager_link.status)
         for x in q(c, "SELECT customer_manager_link.manager_customer, customer_manager_link.status FROM customer_manager_link")}
gate(links.get(GM_MANAGER) == "ACTIVE", "Green Marketing manager link ACTIVE")

# --- fresh duplicate re-read -----------------------------------------
existing = q(c, """
    SELECT conversion_action.id, conversion_action.name, conversion_action.type,
           conversion_action.status
    FROM conversion_action
""")
gate(len(existing) == 0, "conversion_action count is still 0 (no duplicates)", str(len(existing)))
for r in existing:
    print(f"        EXISTING: {r.conversion_action.id} {r.conversion_action.name}")

if fails:
    print("\nHARD STOP. Gates failed: " + "; ".join(fails))
    sys.exit(1)
print("\nALL GATES PASS. Proceeding with 3 create operations.\n")

# =====================================================================
# EXECUTE
# =====================================================================
svc = c.get_service("ConversionActionService")
E_TYPE = c.enums.ConversionActionTypeEnum
E_CAT = c.enums.ConversionActionCategoryEnum
E_STATUS = c.enums.ConversionActionStatusEnum
E_COUNT = c.enums.ConversionActionCountingTypeEnum
E_ATTR = c.enums.AttributionModelEnum

SPECS = [
    # (ordinal, name, type, category, duration_seconds or None)
    (1, "Lead | Permanent Lights | Form Submit | Thank You", "WEBPAGE", "SUBMIT_LEAD_FORM", None),
    (3, "Call | Permanent Lights | Website | 60s", "WEBSITE_CALL", "PHONE_CALL_LEAD", 60),
    (2, "Call | Permanent Lights | Ads | 60s", "AD_CALL", "PHONE_CALL_LEAD", 60),
]


def build(name, type_name, cat_name, duration, attribution):
    op = c.get_type("ConversionActionOperation")
    ca = op.create
    ca.name = name
    ca.type_ = getattr(E_TYPE, type_name)
    ca.category = getattr(E_CAT, cat_name)
    ca.status = E_STATUS.ENABLED
    ca.primary_for_goal = False                 # SECONDARY
    ca.counting_type = E_COUNT.ONE_PER_CLICK
    ca.click_through_lookback_window_days = 30
    ca.view_through_lookback_window_days = 1
    ca.attribution_model_settings.attribution_model = getattr(E_ATTR, attribution)
    ca.value_settings.default_value = 0.0
    ca.value_settings.always_use_default_value = False
    if duration is not None:
        ca.phone_call_duration_seconds = duration
    return op


for ordinal, name, type_name, cat_name, duration in SPECS:
    print(f"--- object {ordinal}: {name}")
    print(f"    type={type_name} category={cat_name} primary_for_goal=False duration={duration}")
    attribution = "GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN"
    for attempt in (1, 2):
        try:
            op = build(name, type_name, cat_name, duration, attribution)
            resp = svc.mutate_conversion_actions(customer_id=CID, operations=[op])
            rn = resp.results[0].resource_name
            created.append({"ordinal": ordinal, "name": name, "resource_name": rn,
                            "id": rn.split("/")[-1], "attribution_used": attribution})
            print(f"    CREATED {rn}  (attribution={attribution})")
            break
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            detail = []
            fail = getattr(exc, "failure", None)
            if fail is not None:
                for e in fail.errors:
                    detail.append(e.message)
            detail_s = " | ".join(detail) or msg[:300]
            print(f"    ATTEMPT {attempt} FAILED: {detail_s[:400]}")
            if attempt == 1 and "attribution" in detail_s.lower():
                attribution = "GOOGLE_ADS_LAST_CLICK"
                print(f"    -> retrying this object with attribution={attribution} (documented fallback)")
                continue
            print("\n" + "=" * 78)
            print("PARTIAL FAILURE - STOPPING IMMEDIATELY. Nothing will be retried blindly.")
            print("=" * 78)
            print(f"  objects created before the failure: {len(created)}")
            for x in created:
                print(f"    {x['ordinal']}. {x['id']}  {x['name']}  attribution={x['attribution_used']}")
            print(f"  FAILED object: {ordinal} ({name})")
            print(f"  error: {detail_s[:600]}")
            write(RECEIPTS / "2026-09-16-stageA-PARTIAL-FAILURE.json",
                  {"created": created, "failed_ordinal": ordinal, "failed_name": name,
                   "error": detail_s[:2000],
                   "when": datetime.datetime.now(TZ).isoformat()})
            sys.exit(2)

print(f"\nAll {len(created)} objects created.\n")

# =====================================================================
# READBACK
# =====================================================================
print("=" * 78)
print("READBACK")
print("=" * 78)
ids = ",".join(x["id"] for x in created)
rows = q(c, f"""
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
           conversion_action.owner_customer,
           conversion_action.tag_snippets
    FROM conversion_action
    WHERE conversion_action.id IN ({ids})
""")

EXPECT = {
    "Lead | Permanent Lights | Form Submit | Thank You": ("WEBPAGE", "SUBMIT_LEAD_FORM", 0),
    "Call | Permanent Lights | Ads | 60s": ("AD_CALL", "PHONE_CALL_LEAD", 60),
    "Call | Permanent Lights | Website | 60s": ("WEBSITE_CALL", "PHONE_CALL_LEAD", 60),
}
readback = []
qa_fail = 0
for r in rows:
    a = r.conversion_action
    exp_type, exp_cat, exp_dur = EXPECT[a.name]
    labels = []
    for t in a.tag_snippets:
        ev = t.event_snippet or ""
        for m in re.findall(r"AW-\d+/[A-Za-z0-9_\-]+", ev):
            labels.append(m)
    labels = sorted(set(labels))
    rec = {
        "id": str(a.id), "resource_name": a.resource_name, "name": a.name,
        "status": E(a.status), "type": E(a.type_), "category": E(a.category),
        "origin": E(a.origin), "primary_for_goal": a.primary_for_goal,
        "counting_type": E(a.counting_type),
        "click_window_days": a.click_through_lookback_window_days,
        "view_window_days": a.view_through_lookback_window_days,
        "attribution_model": E(a.attribution_model_settings.attribution_model),
        "data_driven_model_status": E(a.attribution_model_settings.data_driven_model_status),
        "default_value": a.value_settings.default_value,
        "always_use_default_value": a.value_settings.always_use_default_value,
        "phone_call_duration_seconds": a.phone_call_duration_seconds,
        "include_in_conversions_metric": a.include_in_conversions_metric,
        "owner_customer": (a.owner_customer or "").split("/")[-1],
        "send_to_labels": labels,
    }
    readback.append(rec)

    checks = {
        "type": rec["type"] == exp_type,
        "category": rec["category"] == exp_cat,
        "status ENABLED": rec["status"] == "ENABLED",
        "primary_for_goal == False (SECONDARY)": rec["primary_for_goal"] is False,
        "counting ONE_PER_CLICK": rec["counting_type"] == "ONE_PER_CLICK",
        "click window 30": rec["click_window_days"] == 30,
        "default_value 0.0": float(rec["default_value"]) == 0.0,
        "always_use_default_value False": rec["always_use_default_value"] is False,
        "duration": (rec["phone_call_duration_seconds"] == exp_dur) if exp_dur else True,
        "owner is this child": rec["owner_customer"] == CID,
    }
    bad = [k for k, v in checks.items() if not v]
    qa_fail += len(bad)
    print(f"\n  {rec['id']}  {rec['name']}")
    print(f"    resource_name : {rec['resource_name']}")
    print(f"    type/category : {rec['type']} / {rec['category']}   origin={rec['origin']}")
    print(f"    SECONDARY     : primary_for_goal={rec['primary_for_goal']}")
    print(f"    counting      : {rec['counting_type']}   click_window={rec['click_window_days']}d  view={rec['view_window_days']}d")
    print(f"    attribution   : {rec['attribution_model']}  (ddm_status={rec['data_driven_model_status']})")
    print(f"    value         : default={rec['default_value']} always_use_default={rec['always_use_default_value']}")
    print(f"    call duration : {rec['phone_call_duration_seconds']}s")
    print(f"    in_conv_metric: {rec['include_in_conversions_metric']}")
    print(f"    send_to       : {labels or '(no event snippet - expected for call-type actions)'}")
    print(f"    QA            : {'ALL PASS' if not bad else 'FAIL -> ' + ', '.join(bad)}")

print("\n" + "=" * 78)
print(f"READBACK QA: {len(readback)}/3 actions read back, {qa_fail} field failures")
print("=" * 78)

# --- account-level effects -------------------------------------------
after = q(c, """
    SELECT customer.conversion_tracking_setting.conversion_tracking_status,
           customer.conversion_tracking_setting.conversion_tracking_id,
           customer.call_reporting_setting.call_conversion_action
    FROM customer
""")[0].customer
print("\n=== ACCOUNT-LEVEL AFTER ===")
print(f"  conversion_tracking_status : {E(after.conversion_tracking_setting.conversion_tracking_status)}")
print(f"  conversion_tracking_id     : {after.conversion_tracking_setting.conversion_tracking_id}")
print(f"  call_conversion_action ptr : {after.call_reporting_setting.call_conversion_action or '(none)'}")

total_now = len(q(c, "SELECT conversion_action.id FROM conversion_action"))
print(f"  conversion_action count    : {total_now} (expected exactly 3)")

goals = q(c, "SELECT customer_conversion_goal.category, customer_conversion_goal.biddable FROM customer_conversion_goal")
biddable = [E(g.customer_conversion_goal.category) for g in goals if g.customer_conversion_goal.biddable]
print(f"  customer_conversion_goals  : {len(goals)} rows, biddable={biddable}")

receipt = {
    "plan_id": "APG-0916-CONV-A",
    "fingerprint": EXPECTED_FP,
    "approval_string": APPROVAL,
    "executed_local": datetime.datetime.now(TZ).isoformat(),
    "customer_id": CID,
    "account_name": EXACT_NAME,
    "scope_approved_by": sc.get("approved_by"),
    "mutations_issued": len(created),
    "created": created,
    "readback": readback,
    "readback_field_failures": qa_fail,
    "conversion_action_count_after": total_now,
    "conversion_tracking_status_after": E(after.conversion_tracking_setting.conversion_tracking_status),
    "call_conversion_action_pointer_after": after.call_reporting_setting.call_conversion_action,
    "customer_conversion_goals_after": len(goals),
    "biddable_goals_after": biddable,
    "deletes_or_removes": 0,
}
write(RECEIPTS / "2026-09-16-stageA-receipt.json", receipt)
print("\nSTAGE A COMPLETE." if qa_fail == 0 else "\nSTAGE A COMPLETE WITH QA FAILURES - REVIEW ABOVE.")
