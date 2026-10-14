#!/usr/bin/env python3
"""Ambient | 2026-09-18 | EXECUTE the two approved correction plans.

  APPROVE AMB-0918-BUDGET-1 39097845F5F4 5 operations FOR 2401959466
  APPROVE AMB-0918-CONV-1   A3370F96FA6E 2 operations FOR 2401959466

Writes ONLY to child account 2401959466. Never to MCC 3373711342.
Each plan is one atomic mutate with partial_failure=False. Raw mutations are built from
the SAVED MANIFEST, never from a written recap. Nothing is enabled. The two heating
campaigns are not touched.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-18"
LIVE = ROOT / "receipts" / "live"
APPROVED = {"AMB-0918-BUDGET-1": ("39097845F5F4", 5),
            "AMB-0918-CONV-1": ("A3370F96FA6E", 2)}
HEATING = {"24257819463", "24257819466"}


def die(rec, tag, msg):
    rec["ABORT"] = msg
    LIVE.mkdir(parents=True, exist_ok=True)
    (LIVE / f"{tag}-{STAMP}-ABORT.json").write_text(
        json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(f"\n*** ABORT [{tag}]: {msg} ***")
    print(f"*** COMMITTED SO FAR: {json.dumps(rec.get('committed', {}), default=str)[:600]} ***")
    sys.exit(2)


c = client()
row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
              customer.test_account, customer.status FROM customer""")[0].customer
assert row.descriptive_name == EXACT_NAME and str(row.id) == CID and not row.manager \
    and not row.test_account, "IDENTITY GATE FAILED"
print(f"identity re-confirmed: {row.descriptive_name} / {row.id}")
print(f"writing only to {CID}; never to MCC {GM_MANAGER}\n")


def preflight(name):
    fp_want, ops_want = APPROVED[name]
    f = PLANS / f"{name}.json"
    if not f.exists():
        die({}, name, f"manifest missing: {f}")
    plan = json.loads(f.read_text(encoding="utf-8"))
    fp = plan.pop("fingerprint"); re_fp = approval_code(plan); plan["fingerprint"] = fp
    if not (fp == re_fp == fp_want):
        die({}, name, f"fingerprint mismatch: disk={fp} recomputed={re_fp} approved={fp_want}")
    if plan["operation_count"] != ops_want or len(plan["operations"]) != ops_want:
        die({}, name, f"operation count mismatch: plan={plan['operation_count']} "
                      f"raw={len(plan['operations'])} approved={ops_want}")
    if str(plan["customer_id"]) != CID or plan["exact_account_name"] != EXACT_NAME:
        die({}, name, f"plan targets a different account: {plan['customer_id']}")
    prior = sorted(LIVE.glob(f"{name}-*.json"))
    prior = [p for p in prior if "ABORT" not in p.name]
    if prior:
        die({}, name, f"already executed - receipts exist: {[p.name for p in prior]}")
    print(f"[{name}] manifest OK  fp={fp}  ops={ops_want}  no prior receipt")
    return plan


# ==================================================================== BUDGETS
name = "AMB-0918-BUDGET-1"
plan = preflight(name)
rec = {"plan": name, "fingerprint": APPROVED[name][0], "customer_id": CID,
       "mcc_never_written": GM_MANAGER, "started": datetime.datetime.now(TZ).isoformat(),
       "committed": {}, "nothing_enabled": True}

print(f"\n=== {name}: PRE-WRITE STATE ===")
live = {str(r.campaign_budget.id): r.campaign_budget for r in q(c, """
    SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
           campaign_budget.explicitly_shared, campaign_budget.reference_count
    FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'""")}
before = {}
for o in plan["operations"]:
    b = live.get(o["budget_id"])
    if b is None:
        die(rec, name, f"budget {o['budget_id']} not found")
    cur = round(b.amount_micros / 1e6, 2)
    if abs(cur - o["from_usd"]) > 0.005:
        die(rec, name, f"DRIFT on {o['budget_id']}: live ${cur} != plan from ${o['from_usd']}")
    if b.explicitly_shared or b.reference_count != 1:
        die(rec, name, f"budget {o['budget_id']} shared={b.explicitly_shared} "
                       f"refs={b.reference_count}, expected not-shared and exactly 1")
    before[o["budget_id"]] = cur
    print(f"  {o['budget_id']}  ${cur:7.2f} -> ${o['to_usd']:7.2f}  {o['campaign'][-30:]}")
rec["before"] = before

ops = []
for o in plan["operations"]:
    op = c.get_type("CampaignBudgetOperation")
    op.update.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(
        CID, o["budget_id"])
    op.update.amount_micros = int(round(o["to_usd"] * 1e6))
    op.update_mask.paths.append("amount_micros")
    ops.append(op)
req = c.get_type("MutateCampaignBudgetsRequest")
req.customer_id = CID; req.operations.extend(ops); req.partial_failure = False
try:
    r = c.get_service("CampaignBudgetService").mutate_campaign_budgets(request=req)
    rec["committed"]["budgets"] = [x.resource_name for x in r.results]
except Exception as ex:
    die(rec, name, f"budget mutate failed: {str(ex)[:600]}")
print(f"  EXECUTED_OK: {len(rec['committed']['budgets'])} budget updates")
rec["finished"] = datetime.datetime.now(TZ).isoformat()
LIVE.mkdir(parents=True, exist_ok=True)
(LIVE / f"{name}-{STAMP}.json").write_text(json.dumps(rec, indent=1, default=str),
                                           encoding="utf-8")

print(f"\n=== {name}: READBACK ===")
P = F = 0


def chk(label, ok, detail=""):
    global P, F
    P, F = (P + 1, F) if ok else (P, F + 1)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  -- {detail}" if detail else ""))


after = {str(r.campaign_budget.id): r.campaign_budget for r in q(c, f"""
    SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
           campaign_budget.explicitly_shared, campaign_budget.delivery_method,
           campaign_budget.reference_count, campaign_budget.status
    FROM campaign_budget
    WHERE campaign_budget.id IN ('{"', '".join(before)}')""")}
for o in plan["operations"]:
    b = after[o["budget_id"]]
    chk(f"budget {o['budget_id']} now ${o['to_usd']:.2f}",
        abs(b.amount_micros / 1e6 - o["to_usd"]) < 0.005, f"${b.amount_micros / 1e6:.2f}")
    chk(f"budget {o['budget_id']} still not shared", b.explicitly_shared is False)
    chk(f"budget {o['budget_id']} still STANDARD", E(b.delivery_method) == "STANDARD")
    chk(f"budget {o['budget_id']} reference_count 1", b.reference_count == 1,
        b.reference_count)
en = q(c, """SELECT campaign.id, campaign.name, campaign.status,
             campaign_budget.amount_micros FROM campaign
             WHERE campaign.status = 'ENABLED'""")
tot = round(sum(x.campaign_budget.amount_micros / 1e6 for x in en), 2)
chk("5 campaigns still ENABLED", len(en) == 5, len(en))
chk("combined ENABLED daily = $237.00", abs(tot - 237.00) < 0.005, f"${tot:.2f}")
heat = q(c, f"""SELECT campaign.id, campaign.name, campaign.status,
                campaign.primary_status, campaign_budget.amount_micros
                FROM campaign WHERE campaign.id IN ('{"', '".join(HEATING)}')""")
htot = round(sum(x.campaign_budget.amount_micros / 1e6 for x in heat), 2)
chk("both heating campaigns still PAUSED",
    all(E(x.campaign.status) == "PAUSED" for x in heat),
    [E(x.campaign.status) for x in heat])
chk("heating daily still $90.00", abs(htot - 90.00) < 0.005, f"${htot:.2f}")
chk("future total after enablement = $327.00", abs(tot + htot - 327.00) < 0.005,
    f"${tot + htot:.2f}")
chk("monthly equivalent = $9,940.80", abs((tot + htot) * 30.4 - 9940.80) < 0.05,
    f"${(tot + htot) * 30.4:,.2f}")
chk("at or under permanent max $328.94/day", (tot + htot) <= 328.94, f"${tot + htot:.2f}")
rec["readback"] = {"pass": P, "fail": F, "enabled_daily": tot, "heating_daily": htot,
                   "future_total": round(tot + htot, 2),
                   "monthly_equiv": round((tot + htot) * 30.4, 2)}
(LIVE / f"{name}-{STAMP}.json").write_text(json.dumps(rec, indent=1, default=str),
                                           encoding="utf-8")
budget_pf = (P, F)

# ================================================================ CONVERSIONS
name = "AMB-0918-CONV-1"
plan = preflight(name)
rec2 = {"plan": name, "fingerprint": APPROVED[name][0], "customer_id": CID,
        "mcc_never_written": GM_MANAGER, "started": datetime.datetime.now(TZ).isoformat(),
        "committed": {}, "nothing_deleted": True}

print(f"\n=== {name}: PRE-WRITE STATE ===")
ids = [o["conversion_action_id"] for o in plan["operations"]]
lc = {str(r.conversion_action.id): r.conversion_action for r in q(c, f"""
    SELECT conversion_action.id, conversion_action.name, conversion_action.status,
           conversion_action.primary_for_goal, conversion_action.category,
           conversion_action.origin, conversion_action.type
    FROM conversion_action WHERE conversion_action.id IN ('{"', '".join(ids)}')""")}
for o in plan["operations"]:
    a = lc.get(o["conversion_action_id"])
    if a is None:
        die(rec2, name, f"conversion action {o['conversion_action_id']} not found")
    if a.primary_for_goal is not True:
        die(rec2, name, f"DRIFT: {a.id} primary_for_goal={a.primary_for_goal}, expected True")
    if E(a.status) != "ENABLED":
        die(rec2, name, f"DRIFT: {a.id} status={E(a.status)}, expected ENABLED")
    print(f"  {a.id}  PRIMARY -> SECONDARY  {E(a.category)}/{E(a.origin)}  {a.name[:44]}")
rec2["before"] = {k: {"primary_for_goal": True, "status": E(v.status), "name": v.name}
                  for k, v in lc.items()}

ops = []
for o in plan["operations"]:
    op = c.get_type("ConversionActionOperation")
    op.update.resource_name = c.get_service(
        "ConversionActionService").conversion_action_path(CID, o["conversion_action_id"])
    op.update.primary_for_goal = False
    op.update_mask.paths.append("primary_for_goal")
    ops.append(op)
req = c.get_type("MutateConversionActionsRequest")
req.customer_id = CID; req.operations.extend(ops); req.partial_failure = False
try:
    r = c.get_service("ConversionActionService").mutate_conversion_actions(request=req)
    rec2["committed"]["conversion_actions"] = [x.resource_name for x in r.results]
except Exception as ex:
    die(rec2, name, f"conversion action mutate failed: {str(ex)[:600]}")
print(f"  EXECUTED_OK: {len(rec2['committed']['conversion_actions'])} conversion actions")
rec2["finished"] = datetime.datetime.now(TZ).isoformat()
(LIVE / f"{name}-{STAMP}.json").write_text(json.dumps(rec2, indent=1, default=str),
                                           encoding="utf-8")

print(f"\n=== {name}: READBACK ===")
P = F = 0
for o in plan["operations"]:
    a = q(c, f"""SELECT conversion_action.id, conversion_action.name,
                 conversion_action.status, conversion_action.primary_for_goal
                 FROM conversion_action
                 WHERE conversion_action.id = {o['conversion_action_id']}""")[0].conversion_action
    chk(f"{a.id} primary_for_goal now False", a.primary_for_goal is False, a.primary_for_goal)
    chk(f"{a.id} still ENABLED (not deleted, not paused)", E(a.status) == "ENABLED",
        E(a.status))
allc = q(c, """SELECT conversion_action.id, conversion_action.name,
               conversion_action.status, conversion_action.primary_for_goal,
               conversion_action.category, conversion_action.origin
               FROM conversion_action WHERE conversion_action.status != 'REMOVED'""")
chk("non-removed conversion action count still 16", len(allc) == 16, len(allc))
biddable_goals = {("PHONE_CALL_LEAD", "WEBSITE"), ("SUBMIT_LEAD_FORM", "WEBSITE"),
                  ("CONTACT", "WEBSITE"), ("PHONE_CALL_LEAD", "CALL_FROM_ADS"),
                  ("CONTACT", "CALL_FROM_ADS")}
bid_pri = [x.conversion_action for x in allc
           if x.conversion_action.primary_for_goal
           and E(x.conversion_action.status) == "ENABLED"
           and (E(x.conversion_action.category), E(x.conversion_action.origin))
           in biddable_goals]
chk("biddable Primary actions now 3", len(bid_pri) == 3,
    sorted(f"{a.id}:{E(a.category)}/{E(a.origin)}" for a in bid_pri))
for a in bid_pri:
    print(f"      PRIMARY {a.id}  {E(a.category)}/{E(a.origin):14s} {a.name[:44]}")
enabled_pri = [x for x in allc if x.conversion_action.primary_for_goal
               and E(x.conversion_action.status) == "ENABLED"]
chk("enabled Primary actions now 8", len(enabled_pri) == 8, len(enabled_pri))
gbp = [x.conversion_action for x in allc
       if E(x.conversion_action.origin) == "GOOGLE_HOSTED"]
chk("all 5 Google Business Profile actions untouched and still Primary",
    len(gbp) == 5 and all(a.primary_for_goal for a in gbp),
    [(str(a.id), a.primary_for_goal) for a in gbp])
rec2["readback"] = {"pass": P, "fail": F, "biddable_primary": len(bid_pri),
                    "enabled_primary": len(enabled_pri)}
(LIVE / f"{name}-{STAMP}.json").write_text(json.dumps(rec2, indent=1, default=str),
                                           encoding="utf-8")

print(f"\n{'=' * 62}")
print(f"AMB-0918-BUDGET-1 readback: {budget_pf[0]} PASS / {budget_pf[1]} FAIL")
print(f"AMB-0918-CONV-1   readback: {P} PASS / {F} FAIL")
print("NOTHING ENABLED. NOTHING DELETED. HEATING CAMPAIGNS UNTOUCHED AND PAUSED.")
sys.exit(1 if (budget_pf[1] or F) else 0)
