#!/usr/bin/env python3
"""Ambient | 2026-10-02 | v2 (fresh MTD, 8 Search + 2 PMax; supersedes OCT-1/NOV-1 computed at 07:10) | Budget plans for the owner's ~$1,000/month-per-campaign allocation. BUILD / EXECUTE.

  AMB-1002-BUD-OCT-2   the 8 ENABLED Search campaigns, October pro-rate: (1,000 - October spend so far) / calendar days left
                       incl. the change day. Google: after a mid-month change the month's limit = spend so far + new daily
                       budget x remaining days (support.google.com/google-ads/answer/10487143). Valid for a change ON 2026-10-02.
  AMB-1101-BUD-NOV-2   the same 8 budgets to $32.89 (1,000 / 30.4) - execute on/after 2026-11-01 (separate approval).
  build                      read + math + validate_only (0 writes)
  execute <PLAN> <FP> <N>    re-reads October spend live; refuses if any campaign's resulting October limit would exceed $1,000.50
PMax budgets ($32.89 each) live in the PMax build plans. Bids, ceilings, schedules, locations and statuses are untouched.
"""
from __future__ import annotations
import sys, json, re, datetime, calendar
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, PLANS, RECEIPTS, E, CID, EXACT_NAME  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402

ALLOC, STEADY = 1000.00, 32.89   # 1000 / 30.4 = 32.8947 -> 32.89 (x 30.4 = 999.86)
CHANGE_DAY = datetime.date(2026, 10, 2)
DAYS_LEFT = calendar.monthrange(2026, 10)[1] - CHANGE_DAY.day + 1   # 30 (Oct 2..31 inclusive)


def read(c):
    camps = {}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, campaign_budget.id, campaign_budget.amount_micros,
            campaign_budget.explicitly_shared, campaign_budget.reference_count FROM campaign WHERE campaign.status = 'ENABLED'
            AND campaign.advertising_channel_type IN ('SEARCH', 'PERFORMANCE_MAX')"""):
        camps[str(r.campaign.id)] = dict(name=r.campaign.name, budget_id=str(r.campaign_budget.id), budget=r.campaign_budget.amount_micros / 1e6,
                                         shared=r.campaign_budget.explicitly_shared, refs=r.campaign_budget.reference_count, oct=0.0, run=[])
    for r in q(c, f"""SELECT campaign.id, segments.date, metrics.cost_micros FROM campaign WHERE campaign.status = 'ENABLED'
            AND segments.date BETWEEN '2026-09-24' AND '{datetime.datetime.now(TZ).date().isoformat()}'"""):
        k = str(r.campaign.id)
        if k in camps:
            cost = r.metrics.cost_micros / 1e6
            if r.segments.date >= "2026-10-01":
                camps[k]["oct"] += cost
            camps[k]["run"].append((r.segments.date, cost))
    return camps


def plans(camps):
    oct_ops, nov_ops, rows = [], [], []
    for cid, v in sorted(camps.items(), key=lambda kv: kv[1]["name"]):
        remaining = round(ALLOC - v["oct"], 2)
        oct_daily = round(int(remaining / DAYS_LEFT * 100) / 100, 2)   # round DOWN to the cent so the limit stays <= $1,000
        limit = round(v["oct"] + oct_daily * DAYS_LEFT, 2)
        serving_days = [c for d, c in v["run"] if "2026-09-24" <= d <= "2026-10-01" and c > 0]
        run_rate = round(sum(serving_days) / 6, 2)   # 6 Mon-Fri serving days 09-24..10-01 (calendar denominator, zero days included)
        rows.append(dict(campaign_id=cid, campaign=v["name"], budget_id=v["budget_id"], shared=v["shared"], refs=v["refs"], current=v["budget"],
                         oct_mtd=round(v["oct"], 2), remaining=remaining, days_left=DAYS_LEFT, oct_daily=oct_daily,
                         oct_limit=limit, oct_change_pct=round(100 * (oct_daily - v["budget"]) / v["budget"], 1), steady=STEADY,
                         steady_change_pct=round(100 * (STEADY - v["budget"]) / v["budget"], 1), run_rate_per_serving_day=run_rate,
                         max_per_serving_day=round(2 * oct_daily, 2)))
        if abs(v["budget"] - oct_daily) >= 0.005:   # PMax budgets were set to the same formula at creation - no redundant op
            oct_ops.append(dict(op="SET_BUDGET", campaign_id=cid, campaign=v["name"], budget_id=v["budget_id"], from_usd=v["budget"], to_usd=oct_daily))
        nov_ops.append(dict(op="SET_BUDGET", campaign_id=cid, campaign=v["name"], budget_id=v["budget_id"], from_usd=oct_daily, to_usd=STEADY))
    common = dict(customer_id=CID, exact_account_name=EXACT_NAME, never_write_to_mcc="3373711342", approval_class="budget",
                  work_order="work-orders/work-order-budget-allocation-2026-10-02.yaml", unchanged="bidding, CPC ceilings ($18 repair), schedules, "
                  "locations, devices, statuses, conversions", monthly_basis="Google monthly limit = average daily budget x 30.4; daily spend may reach 2x")
    oct_plan = dict(plan_name="AMB-1002-BUD-OCT-2", valid_change_day=CHANGE_DAY.isoformat(), days_left_incl_change_day=DAYS_LEFT,
                    rule="October daily = (1,000 - October spend before the change) / calendar days left incl. change day, rounded down to the cent",
                    **common, operations=oct_ops)
    nov_plan = dict(plan_name="AMB-1101-BUD-NOV-2", execute_on_or_after="2026-11-01", rule="steady state $1,000 / 30.4 = $32.89/day (x 30.4 = $999.86)",
                    **common, operations=nov_ops)
    for p in (oct_plan, nov_plan):
        p["operation_count"] = len(p["operations"])
        p["fingerprint"] = approval_code({k: v for k, v in p.items() if k != "fingerprint"})
    return oct_plan, nov_plan, rows


def ops_for(c, plan):
    out = []
    for o in plan["operations"]:
        x = c.get_type("CampaignBudgetOperation"); x.update.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(CID, o["budget_id"])
        x.update.amount_micros = int(round(o["to_usd"] * 100)) * 10000; x.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["amount_micros"]))
        out.append(x)
    return out


def send(c, ops, validate):
    rq = c.get_type("MutateCampaignBudgetsRequest"); rq.customer_id = CID; rq.operations.extend(ops); rq.partial_failure = False; rq.validate_only = validate
    return c.get_service("CampaignBudgetService").mutate_campaign_budgets(request=rq)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    c = client()
    identity_gate(c, verbose=False)
    camps = read(c)
    if any(v["shared"] or v["refs"] != 1 for v in camps.values()):
        sys.exit("HARD STOP: a budget is shared - re-plan")
    oct_plan, nov_plan, rows = plans(camps)
    if mode == "build":
        pf = {}
        for p in (oct_plan, nov_plan):
            try:
                send(c, ops_for(c, p), True); pf[p["plan_name"]] = f"VALIDATED {p['operation_count']}"
            except Exception as ex:
                pf[p["plan_name"]] = "FAILED " + str(re.findall(r'message: "([^"]+)"', str(ex))[:3])
        print("preflight:", pf)
        if any(v.startswith("FAILED") for v in pf.values()):
            sys.exit("HARD STOP: validate_only failed")
        for p in (oct_plan, nov_plan):
            (PLANS / f"{p['plan_name']}.json").write_text(json.dumps(p, indent=1), encoding="utf-8")
            print(f"PLAN {p['plan_name']}: {p['fingerprint']} / {p['operation_count']} ops")
        (PLANS / "AMB-1002-BUD-math.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
        tot = lambda k: round(sum(r[k] for r in rows), 2)
        for r in rows:
            print(f"  {r['campaign_id']} {r['campaign'][18:58]:40s} budget {r['budget_id']} cur ${r['current']:>6} octMTD ${r['oct_mtd']:>6} rem ${r['remaining']:>7} "
                  f"oct ${r['oct_daily']:>5} ({r['oct_change_pct']:+}%) limit ${r['oct_limit']} | steady ${r['steady']} ({r['steady_change_pct']:+}%) | run ${r['run_rate_per_serving_day']}/srv-day max ${r['max_per_serving_day']}")
        print(f"  TOTAL current ${tot('current')}/day | Oct MTD ${tot('oct_mtd')} | Oct budgets ${tot('oct_daily')}/day | Oct limits ${tot('oct_limit')} | steady {len(rows)} x {STEADY} = ${round(len(rows) * STEADY, 2)}/day")
        return
    name = sys.argv[2]
    p = {"AMB-1002-BUD-OCT-2": oct_plan, "AMB-1101-BUD-NOV-2": nov_plan}[name]
    saved = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8")); fp = saved.pop("fingerprint")
    if name == "AMB-1002-BUD-OCT-2":
        if datetime.datetime.now(TZ).date() != CHANGE_DAY:
            sys.exit("ABORT: the October pro-rate is only valid on 2026-10-02 - rebuild for today")
        live = {o["campaign_id"]: round(camps[o["campaign_id"]]["oct"] + o["to_usd"] * DAYS_LEFT, 2) for o in saved["operations"]}
        over = {k: v for k, v in live.items() if v > ALLOC + 0.5}
        if over:
            sys.exit(f"ABORT: October limit would exceed $1,000 for {over} (spend moved since the plan) - rebuild")
        fp_live = fp   # amounts are fixed in the approved file; the live check above guards the limit
    else:
        if datetime.datetime.now(TZ).date() < datetime.date(2026, 11, 1):
            sys.exit("ABORT: execute on or after 2026-11-01")
        fp_live = fp
    if not (fp == approval_code(saved) == fp_live == sys.argv[3].upper() and int(sys.argv[4]) == saved["operation_count"]):
        sys.exit("ABORT: fingerprint mismatch")
    out = RECEIPTS / f"{name}-EXECUTED.json"
    if out.exists():
        sys.exit("ABORT: receipt exists")
    rec = dict(plan=name, fingerprint=fp, started_local=datetime.datetime.now(TZ).isoformat())
    try:
        rec["results"] = [r.resource_name for r in send(c, ops_for(c, saved), False).results]
    except Exception as ex:
        rec["status"] = "FAILED_NOTHING_WRITTEN"; rec["error"] = re.findall(r'message: "([^"]+)"', str(ex))[:3]
        out.write_text(json.dumps(rec, indent=1), encoding="utf-8"); sys.exit(f"FAILED: {rec['error']}")
    after = read(c)
    rec["readback"] = [{"campaign": o["campaign_id"], "expected": o["to_usd"], "got": round(after[o["campaign_id"]]["budget"], 2),
                        "pass": abs(after[o["campaign_id"]]["budget"] - o["to_usd"]) < 0.005} for o in saved["operations"]]
    rec["status"] = "EXECUTED" if all(x["pass"] for x in rec["readback"]) else "EXECUTED_READBACK_FAIL"
    rec["intervention_timestamp"] = datetime.datetime.now(TZ).isoformat()
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(f"{name} {fp}: {rec['status']}")


if __name__ == "__main__":
    main()
