#!/usr/bin/env python3
"""Ambient | 2026-09-18 | validate_only for AMB-0918-BUDGET-1 and AMB-0918-CONV-1.

Nothing is created or changed. validate_only consumes mutate quota but commits nothing.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-18"
c = client()
row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
              customer.test_account FROM customer""")[0].customer
assert row.descriptive_name == EXACT_NAME and str(row.id) == CID and not row.manager \
    and not row.test_account, "IDENTITY GATE FAILED"
print(f"identity: {row.descriptive_name} / {row.id}\n")

res = {"when": datetime.datetime.now(TZ).isoformat(), "validate_only": True,
       "external_writes": 0, "checks": {}}


def load(name):
    p = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8"))
    fp = p.pop("fingerprint"); re_fp = approval_code(p); p["fingerprint"] = fp
    print(f"{name}: on-disk={fp} recomputed={re_fp} MATCH={fp == re_fp} "
          f"ops={p['operation_count']}")
    assert fp == re_fp, f"FINGERPRINT MISMATCH on {name}"
    return p


# ------------------------------------------------------------------- budgets
bp = load("AMB-0918-BUDGET-1")
print("\n=== AMB-0918-BUDGET-1 : preconditions ===")
live = {str(r.campaign_budget.id): r.campaign_budget for r in q(c, """
    SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
           campaign_budget.explicitly_shared, campaign_budget.reference_count,
           campaign_budget.status FROM campaign_budget
    WHERE campaign_budget.status != 'REMOVED'""")}
ok = True
for o in bp["operations"]:
    b = live.get(o["budget_id"])
    if b is None:
        print(f"  MISSING budget {o['budget_id']}"); ok = False; continue
    cur = b.amount_micros / 1e6
    good = abs(cur - o["from_usd"]) < 0.005
    ok &= good and not b.explicitly_shared and b.reference_count == 1
    print(f"  {o['budget_id']}  live=${cur:7.2f} expected_from=${o['from_usd']:7.2f} "
          f"{'OK' if good else 'DRIFT'}  shared={b.explicitly_shared} "
          f"refs={b.reference_count}  -> ${o['to_usd']:.2f}")
res["checks"]["budget_preconditions"] = "OK" if ok else "DRIFT"

ops = []
for o in bp["operations"]:
    op = c.get_type("CampaignBudgetOperation")
    op.update.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(
        CID, o["budget_id"])
    op.update.amount_micros = int(round(o["to_usd"] * 1e6))
    op.update_mask.paths.append("amount_micros")
    ops.append(op)
req = c.get_type("MutateCampaignBudgetsRequest")
req.customer_id = CID; req.operations.extend(ops)
req.partial_failure = False; req.validate_only = True
try:
    c.get_service("CampaignBudgetService").mutate_campaign_budgets(request=req)
    print(f"  VALIDATED_OK - {len(ops)} budget updates accepted, nothing changed")
    res["checks"]["budget_validate_only"] = f"VALIDATED_OK ({len(ops)})"
except Exception as ex:
    print(f"  FAILED: {str(ex)[:600]}")
    res["checks"]["budget_validate_only"] = f"FAILED: {str(ex)[:400]}"

m = bp["math"]
print(f"  math: ${m['current_enabled_daily_usd']:.2f} -> "
      f"${m['proposed_enabled_daily_usd']:.2f} (<= ${m['max_existing_enabled_daily_usd']}) "
      f"| +heating ${m['new_heating_daily_usd']:.2f} = "
      f"${m['combined_after_heating_enabled_usd']:.2f}/day "
      f"= ${m['combined_monthly_equivalent_usd']:,.2f}/mo")
assert m["proposed_enabled_daily_usd"] <= m["max_existing_enabled_daily_usd"]
assert m["combined_after_heating_enabled_usd"] <= 328.94
assert m["combined_monthly_equivalent_usd"] <= 10000.00
print("  ceiling arithmetic asserts: PASS")
res["checks"]["budget_math"] = "PASS"

# --------------------------------------------------------------- conversions
cp = load("AMB-0918-CONV-1")
print("\n=== AMB-0918-CONV-1 : preconditions ===")
ids = "', '".join(o["conversion_action_id"] for o in cp["operations"])
lc = {str(r.conversion_action.id): r.conversion_action for r in q(c, f"""
    SELECT conversion_action.id, conversion_action.name, conversion_action.status,
           conversion_action.primary_for_goal, conversion_action.category,
           conversion_action.origin, conversion_action.type
    FROM conversion_action WHERE conversion_action.id IN ('{ids}')""")}
ok = True
for o in cp["operations"]:
    a = lc.get(o["conversion_action_id"])
    if a is None:
        print(f"  MISSING action {o['conversion_action_id']}"); ok = False; continue
    good = a.primary_for_goal is True and E(a.status) == "ENABLED"
    ok &= good
    print(f"  {a.id}  primary={a.primary_for_goal} status={E(a.status):8s} "
          f"{E(a.category)}/{E(a.origin)}  {'OK' if good else 'DRIFT'}  {a.name[:40]}")
res["checks"]["conversion_preconditions"] = "OK" if ok else "DRIFT"

ops = []
for o in cp["operations"]:
    op = c.get_type("ConversionActionOperation")
    op.update.resource_name = c.get_service(
        "ConversionActionService").conversion_action_path(CID, o["conversion_action_id"])
    op.update.primary_for_goal = False
    op.update_mask.paths.append("primary_for_goal")
    ops.append(op)
req = c.get_type("MutateConversionActionsRequest")
req.customer_id = CID; req.operations.extend(ops)
req.partial_failure = False; req.validate_only = True
try:
    c.get_service("ConversionActionService").mutate_conversion_actions(request=req)
    print(f"  VALIDATED_OK - {len(ops)} conversion actions accepted, nothing changed")
    res["checks"]["conversion_validate_only"] = f"VALIDATED_OK ({len(ops)})"
except Exception as ex:
    print(f"  FAILED: {str(ex)[:600]}")
    res["checks"]["conversion_validate_only"] = f"FAILED: {str(ex)[:400]}"

# the three that must REMAIN primary and biddable
keep = "', '".join(k["id"] for k in cp["primary_bidding_conversions_after"])
print("\n  Primary bidding conversions AFTER this plan:")
for r in q(c, f"""SELECT conversion_action.id, conversion_action.name,
                  conversion_action.primary_for_goal, conversion_action.category,
                  conversion_action.origin, conversion_action.status
                  FROM conversion_action WHERE conversion_action.id IN ('{keep}')"""):
    a = r.conversion_action
    print(f"    {a.id}  primary={a.primary_for_goal} {E(a.category)}/{E(a.origin):14s} "
          f"{a.name[:44]}")
    assert a.primary_for_goal and E(a.status) == "ENABLED"
print("  survivors still ENABLED + PRIMARY: PASS")
res["checks"]["survivors"] = "PASS"

VRECEIPTS.mkdir(parents=True, exist_ok=True)
p = VRECEIPTS / f"AMB-0918-CORRECTIONS-{STAMP}.json"
p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print(f"\nAPPROVE AMB-0918-BUDGET-1 {bp['fingerprint']} {bp['operation_count']} "
      f"operations FOR {CID}")
print(f"APPROVE AMB-0918-CONV-1 {cp['fingerprint']} {cp['operation_count']} "
      f"operations FOR {CID}")
print("NOTHING WAS CHANGED. EXTERNAL WRITES: 0")
