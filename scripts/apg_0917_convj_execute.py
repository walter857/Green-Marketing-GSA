#!/usr/bin/env python3
"""EXECUTE APG-0917-CONV-J, fingerprint C52D14071B08.

Approval 2026-09-17: "APPROVE APG CONV-FIX C52D14071B08"
Exactly one field on exactly one conversion action: 7773043879 primary_for_goal -> false.
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, GM_MANAGER, TZ, RECEIPTS, client, q, write, E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

PLAN = ROOT / "clients/apogee-lawns/plans/APG-0917-CONV-J.yaml"
EXPECTED_FP = "C52D14071B08"
TARGET = "7773043879"
REQUIRED = {"7772803337": True, "7773013199": True, "7773043879": False}

c = client()
fails = []


def gate(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' -> ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)


print("=" * 78 + "\nGATE\n" + "=" * 78)
plan = load_yaml(str(PLAN))
fp = approval_code(plan)
gate(fp == EXPECTED_FP, "CONV-J fingerprint matches approval", fp)

# CAMP-I fingerprint is recomputed too, for the report, but CAMP-I is NOT executed here.
campi = approval_code(load_yaml(str(ROOT / "clients/apogee-lawns/plans/APG-0917-CAMP-I.yaml")))
print(f"  [INFO] CAMP-I fingerprint on disk: {campi} (expected 4022CBA7FD51) "
      f"match={campi == '4022CBA7FD51'}")

row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
                     customer.test_account, customer.status, customer.currency_code,
                     customer.time_zone FROM customer""")[0].customer
gate(str(row.id) == CID, "customer.id", str(row.id))
gate(row.descriptive_name == EXACT_NAME, "descriptive_name", row.descriptive_name)
gate(not row.manager and not row.test_account, "not manager / not test")
gate(row.time_zone == "America/Chicago", "time zone", row.time_zone)
links = {x.customer_manager_link.manager_customer.split("/")[-1]: E(x.customer_manager_link.status)
         for x in q(c, "SELECT customer_manager_link.manager_customer, customer_manager_link.status FROM customer_manager_link")}
gate(links.get(GM_MANAGER) == "ACTIVE", f"manager {GM_MANAGER} link ACTIVE (never mutated)")

print("\n  -- pre-execution state --")
before = {}
for x in q(c, """SELECT conversion_action.id, conversion_action.name,
                        conversion_action.primary_for_goal, conversion_action.status,
                        conversion_action.include_in_conversions_metric
                 FROM conversion_action ORDER BY conversion_action.id"""):
    a = x.conversion_action
    before[str(a.id)] = a.primary_for_goal
    print(f"      {a.id}  primary={a.primary_for_goal}  in_conv={a.include_in_conversions_metric}  {a.name}")
gate(before.get(TARGET) is True, f"{TARGET} is currently PRIMARY (the from-state)")
gate(before.get("7772803337") is True, "7772803337 already PRIMARY, will not be touched")
gate(before.get("7773013199") is True, "7773013199 already PRIMARY, will not be touched")

print("\n  -- duplicate / partial resource check --")
counts = {}
for lbl, qy in [("campaigns", "SELECT campaign.id FROM campaign"),
                ("budgets", "SELECT campaign_budget.id FROM campaign_budget"),
                ("ad_groups", "SELECT ad_group.id FROM ad_group"),
                ("ads", "SELECT ad_group_ad.ad.id FROM ad_group_ad"),
                ("ad_group_criteria", "SELECT ad_group_criterion.criterion_id FROM ad_group_criterion"),
                ("campaign_criteria", "SELECT campaign_criterion.criterion_id FROM campaign_criterion"),
                ("assets", "SELECT asset.id FROM asset"),
                ("custom_conversion_goals", "SELECT custom_conversion_goal.id FROM custom_conversion_goal")]:
    n = len(q(c, qy))
    counts[lbl] = n
    print(f"      {lbl:<24} {n}")
gate(counts["campaigns"] == 0, "zero pre-existing campaigns")
gate(counts["budgets"] == 0, "zero pre-existing budgets")
gate(counts["custom_conversion_goals"] == 0, "zero custom conversion goals")

if fails:
    sys.exit("\nHARD STOP: " + "; ".join(fails))
print("\nALL GATES PASS. Issuing exactly 1 update operation.\n")

# ---------------------------------------------------------------- EXECUTE
svc = c.get_service("ConversionActionService")
op = c.get_type("ConversionActionOperation")
op.update.resource_name = f"customers/{CID}/conversionActions/{TARGET}"
op.update.primary_for_goal = False
from google.protobuf import field_mask_pb2  # noqa: E402
op.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["primary_for_goal"]))

print(f"--- updating {TARGET} : primary_for_goal true -> false, mask=['primary_for_goal']")
try:
    resp = svc.mutate_conversion_actions(customer_id=CID, operations=[op])
    rn = resp.results[0].resource_name
    print(f"    UPDATED {rn}")
except Exception as exc:  # noqa: BLE001
    detail = []
    f = getattr(exc, "failure", None)
    if f:
        for e in f.errors:
            loc = ".".join(x.field_name for x in e.location.field_path_elements) if e.location and e.location.field_path_elements else ""
            detail.append(f"{e.message} @ '{loc}'")
    msg = " | ".join(detail) or str(exc)[:300]
    print(f"    FAILED: {msg}")
    write(RECEIPTS / "2026-09-17-convj-FAILURE.json",
          {"error": msg, "when": datetime.datetime.now(TZ).isoformat(), "created": []})
    sys.exit(2)

# ---------------------------------------------------------------- READBACK
print("\n" + "=" * 78 + "\nREADBACK - ALL THREE ACTIONS\n" + "=" * 78)
readback, qa_fail = [], 0
for x in q(c, """SELECT conversion_action.id, conversion_action.resource_name,
                        conversion_action.name, conversion_action.status,
                        conversion_action.type, conversion_action.category,
                        conversion_action.origin, conversion_action.primary_for_goal,
                        conversion_action.counting_type,
                        conversion_action.click_through_lookback_window_days,
                        conversion_action.phone_call_duration_seconds,
                        conversion_action.include_in_conversions_metric,
                        conversion_action.attribution_model_settings.attribution_model,
                        conversion_action.value_settings.default_value,
                        conversion_action.owner_customer
                 FROM conversion_action ORDER BY conversion_action.id"""):
    a = x.conversion_action
    i = str(a.id)
    state = "PRIMARY" if a.primary_for_goal else "SECONDARY"
    want = "PRIMARY" if REQUIRED[i] else "SECONDARY"
    ok = a.primary_for_goal == REQUIRED[i]
    if not ok:
        qa_fail += 1
    rec = {"id": i, "resource_name": a.resource_name, "name": a.name, "state": state,
           "required": want, "match": ok, "status": E(a.status), "type": E(a.type_),
           "category": E(a.category), "origin": E(a.origin),
           "counting_type": E(a.counting_type),
           "click_window_days": a.click_through_lookback_window_days,
           "phone_call_duration_seconds": a.phone_call_duration_seconds,
           "include_in_conversions_metric": a.include_in_conversions_metric,
           "attribution_model": E(a.attribution_model_settings.attribution_model),
           "default_value": a.value_settings.default_value,
           "owner": (a.owner_customer or "").split("/")[-1]}
    readback.append(rec)
    print(f"\n  [{'OK ' if ok else 'FAIL'}] {i}  {state:<9} (required {want})")
    print(f"        {a.name}")
    print(f"        {E(a.type_)}/{E(a.category)} origin={E(a.origin)} status={E(a.status)}")
    print(f"        counting={E(a.counting_type)} click_window={a.click_through_lookback_window_days}d "
          f"dur={a.phone_call_duration_seconds}s value={a.value_settings.default_value}")
    print(f"        attribution={E(a.attribution_model_settings.attribution_model)} "
          f"in_conv_metric={a.include_in_conversions_metric} owner={rec['owner']}")

# prove nothing else changed on the target
tgt = next(r for r in readback if r["id"] == TARGET)
unchanged = {
    "name": tgt["name"] == "Call | Permanent Lights | Website | 60s",
    "status ENABLED": tgt["status"] == "ENABLED",
    "type WEBSITE_CALL": tgt["type"] == "WEBSITE_CALL",
    "category PHONE_CALL_LEAD": tgt["category"] == "PHONE_CALL_LEAD",
    "origin WEBSITE": tgt["origin"] == "WEBSITE",
    "counting ONE_PER_CLICK": tgt["counting_type"] == "ONE_PER_CLICK",
    "click window 30": tgt["click_window_days"] == 30,
    "duration 60s": tgt["phone_call_duration_seconds"] == 60,
    "value 0.0": float(tgt["default_value"]) == 0.0,
    "owner unchanged": tgt["owner"] == CID,
}
print(f"\n  -- {TARGET} side-effect check (everything except primary_for_goal) --")
for k, v in unchanged.items():
    print(f"      [{'OK ' if v else 'FAIL'}] {k}")
    if not v:
        qa_fail += 1

print("\n" + "=" * 78)
print(f"CONV-J RESULT: {qa_fail} failures")
print("=" * 78)

write(RECEIPTS / "2026-09-17-convj-receipt.json", {
    "plan_id": "APG-0917-CONV-J", "fingerprint": EXPECTED_FP,
    "approval": "APPROVE APG CONV-FIX C52D14071B08",
    "executed_local": datetime.datetime.now(TZ).isoformat(),
    "customer_id": CID, "account_name": EXACT_NAME,
    "mutations": 1, "update_mask": ["primary_for_goal"],
    "target": TARGET, "from": True, "to": False,
    "before": before, "readback": readback,
    "side_effect_check": unchanged, "qa_failures": qa_fail,
    "conv_g_status": "SATISFIED_EXTERNALLY_BY_VERIFIED_MANUAL_STATE",
    "campaigns_after": len(q(c, "SELECT campaign.id FROM campaign")),
})
print("CONV-J COMPLETE." if qa_fail == 0 else "CONV-J COMPLETE WITH FAILURES.")
