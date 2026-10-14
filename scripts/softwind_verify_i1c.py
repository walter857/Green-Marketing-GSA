#!/usr/bin/env python3
"""Fresh same-minute post-geo spend snapshot, full recalculation of PLAN-I1C's
inputs and split, and fingerprint revalidation.

Read-only. Nothing is executed. If any input has moved, this reports the change
rather than silently presenting a stale approval command.
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.google_ads import enum_name                     # noqa: E402
from gm_gsa.safety import approval_code                     # noqa: E402

CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
TZ = ZoneInfo("America/New_York")
TARGET = 2500.0
EXPECTED_FP = "8CC6CABFC74F"
EXPECTED_BUDGETS = {"24103511039": 333.33, "24145053510": 41.11}

CLIENT = ROOT / "clients/softwind-power-washing"
PLAN_FILE = CLIENT / "plans/2026-08-26-plan-i1c-budget-after-full-geo.yaml"
OUT = CLIENT / "snapshots/i1c-revalidation-2026-08-26.json"

Q_ID = """
SELECT customer.id, customer.descriptive_name, customer.manager,
       customer.test_account, customer.currency_code, customer.time_zone
FROM customer LIMIT 1
"""
Q_MTD = """
SELECT campaign.id, metrics.cost_micros, metrics.impressions, metrics.clicks,
       metrics.average_cpc, metrics.search_impression_share,
       metrics.search_budget_lost_impression_share,
       metrics.search_rank_lost_impression_share
FROM campaign
WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-26'
  AND campaign.status != 'REMOVED'
"""
Q_TODAY = """
SELECT campaign.id, metrics.cost_micros, metrics.impressions, metrics.clicks
FROM campaign
WHERE segments.date = '2026-08-26' AND campaign.status != 'REMOVED'
"""
Q_CAMP = """
SELECT campaign.id, campaign.bidding_strategy_type,
       campaign.target_spend.cpc_bid_ceiling_micros,
       campaign_budget.id, campaign_budget.amount_micros
FROM campaign WHERE campaign.status != 'REMOVED'
"""
Q_LOC = """
SELECT campaign.id, campaign_criterion.negative
FROM campaign_criterion
WHERE campaign_criterion.type = 'LOCATION' AND campaign.status != 'REMOVED'
"""


def normalize(plan):
    cp = plan["change_plan"]
    t = cp["target"]
    acts = [{"action_id": a["action_id"], "priority": a["priority"],
             "resource_type": a["resource_type"], "operation": a["operation"],
             "customer_id": a.get("customer_id", t["child_customer_id"]),
             "campaign_id": a.get("campaign_id"),
             "ad_group_id": a.get("ad_group_id"),
             "resource_id": a.get("resource_id"),
             "current_value": a.get("current_value"),
             "proposed_value": a.get("proposed_value"),
             "object_count": a.get("object_count", 1)}
            for a in cp["actions"]]
    acts.sort(key=lambda x: x["action_id"])
    return {"target": {"exact_child_account_name": t["exact_child_account_name"],
                       "child_customer_id": t["child_customer_id"],
                       "exact_service": t["exact_service"]},
            "plan_id": cp["plan_id"], "approval_type": cp["approval_type"],
            "actions": acts, "action_count": len(acts),
            "object_count": sum(a["object_count"] for a in acts)}


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    out = {"snapshot_account_local": now.isoformat(), "read_only": True}
    fail = []

    def gate(label, cond, detail=""):
        print("   %-56s %s %s" % (label, "PASS" if cond else "CHANGED", detail))
        if not cond:
            fail.append(label)

    # ---- identity --------------------------------------------------------
    print("1. IDENTITY GATE")
    for row in svc.search(customer_id=CID, query=Q_ID):
        c = row.customer
        out["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                           "manager": c.manager, "test_account": c.test_account,
                           "currency": c.currency_code,
                           "time_zone": c.time_zone}
    i = out["identity"]
    gate("account is '%s'" % NAME, i["name"] == NAME)
    gate("customer id is %s" % CID, i["id"] == CID)
    gate("manager false / test false",
         i["manager"] is False and i["test_account"] is False)
    gate("currency USD, tz America/New_York",
         i["currency"] == "USD" and i["time_zone"] == "America/New_York")
    if fail:
        print("\nIDENTITY MISMATCH - STOPPING")
        return 1

    # ---- fresh spend -----------------------------------------------------
    mtd, today = {}, {}
    for row in svc.search(customer_id=CID, query=Q_MTD):
        m = row.metrics
        mtd[str(row.campaign.id)] = {
            "cost": round(m.cost_micros / 1e6, 2), "impressions": m.impressions,
            "clicks": m.clicks, "average_cpc": round(m.average_cpc / 1e6, 2),
            "search_impression_share": m.search_impression_share or None,
            "lost_is_budget": m.search_budget_lost_impression_share or None,
            "lost_is_rank": m.search_rank_lost_impression_share or None}
    for row in svc.search(customer_id=CID, query=Q_TODAY):
        m = row.metrics
        today[str(row.campaign.id)] = {"cost": round(m.cost_micros / 1e6, 2),
                                       "impressions": m.impressions,
                                       "clicks": m.clicks}
    camps = {}
    for row in svc.search(customer_id=CID, query=Q_CAMP):
        cp2, b = row.campaign, row.campaign_budget
        camps[str(cp2.id)] = {
            "bidding": enum_name(cp2.bidding_strategy_type),
            "cpc_ceiling": cp2.target_spend.cpc_bid_ceiling_micros or None,
            "budget_id": str(b.id), "budget_micros": b.amount_micros,
            "budget_usd": round(b.amount_micros / 1e6, 2)}
    loc = {c: {"positive": 0, "negative": 0} for c in CAMPAIGNS}
    for row in svc.search(customer_id=CID, query=Q_LOC):
        cid = str(row.campaign.id)
        if cid in loc:
            loc[cid]["negative" if row.campaign_criterion.negative
                     else "positive"] += 1

    S = round(sum(v["cost"] for v in mtd.values()), 2)
    R = round(TARGET - S, 2)
    sept1 = datetime(2026, 9, 1, tzinfo=TZ)
    H = (sept1 - now).total_seconds() / 3600.0
    D = 31 - now.day + 1
    req_day = R / D
    req_24h = R / (H / 24.0)

    out.update({"mtd": mtd, "today": today, "campaigns": camps,
                "location_counts": loc, "mtd_spend_S": S,
                "remaining_R": R, "remaining_days_D": D,
                "remaining_hours_H": round(H, 2),
                "required_avg_per_calendar_day": round(req_day, 2),
                "required_rolling_24h_pace": round(req_24h, 2)})

    print("\n2. FRESH SAME-MINUTE SPEND SNAPSHOT  %s" % now.isoformat())
    for cid, cname in CAMPAIGNS.items():
        print("   %-18s MTD $%8.2f  impr %4d  clicks %2d  IS %-8s | "
              "today $%7.2f impr %3d clicks %d"
              % (cname, mtd[cid]["cost"], mtd[cid]["impressions"],
                 mtd[cid]["clicks"],
                 ("%.4f" % mtd[cid]["search_impression_share"])
                 if mtd[cid]["search_impression_share"] else "n/a",
                 today[cid]["cost"], today[cid]["impressions"],
                 today[cid]["clicks"]))
    print("   %-18s %d positive / %d negative locations"
          % ("geo A", loc["24103511039"]["positive"],
             loc["24103511039"]["negative"]))
    print("   %-18s %d positive / %d negative locations"
          % ("geo B", loc["24145053510"]["positive"],
             loc["24145053510"]["negative"]))
    print()
    print("   MTD spend S                : $%.2f" % S)
    print("   Remaining R                : $%.2f" % R)
    print("   Remaining calendar days D  : %d" % D)
    print("   Remaining hours H          : %.2f" % H)
    print("   Required per calendar day  : $%.2f" % req_day)
    print("   Required rolling 24h pace  : $%.2f" % req_24h)

    # ---- recalculate the split from scratch ------------------------------
    print("\n3. RECALCULATED SPLIT (same algorithm, fresh inputs)")
    addressable = {}
    for cid in CAMPAIGNS:
        is_share = mtd[cid]["search_impression_share"] or 0.0001
        addressable[cid] = mtd[cid]["impressions"] / is_share
    tot = sum(addressable.values())
    share = {cid: addressable[cid] / tot for cid in CAMPAIGNS}
    min_combined = math.ceil((R / D) * 100) / 100
    raw = {cid: min_combined * share[cid] for cid in CAMPAIGNS}
    floor = {cid: camps[cid]["budget_usd"] for cid in CAMPAIGNS}
    budgets, floored, deficit = {}, [], 0.0
    for cid in CAMPAIGNS:
        if raw[cid] < floor[cid]:
            budgets[cid] = floor[cid]
            deficit += floor[cid] - raw[cid]
            floored.append(cid)
    rest = [c for c in CAMPAIGNS if c not in budgets]
    tot_rest = sum(raw[c] for c in rest) or 1.0
    for c in rest:
        budgets[c] = round(raw[c] - deficit * (raw[c] / tot_rest), 2)
    combined = round(sum(budgets.values()), 2)
    if combined < min_combined:
        top = max(rest, key=lambda c: budgets[c])
        budgets[top] = round(budgets[top] + (min_combined - combined), 2)
        combined = round(sum(budgets.values()), 2)

    out["recalculated"] = {
        "addressable_impressions": {c: round(addressable[c], 1)
                                    for c in CAMPAIGNS},
        "demand_share": {c: round(share[c], 4) for c in CAMPAIGNS},
        "min_combined_daily_budget": min_combined,
        "raw_before_floor": {c: round(raw[c], 2) for c in CAMPAIGNS},
        "floored_at_current_budget": floored,
        "budgets": budgets, "combined": combined,
        "mid_month_check": round(S + combined * D, 2),
        "meets_2500": (S + combined * D) >= TARGET - 0.02}

    for cid, cname in CAMPAIGNS.items():
        tag = "  (floored at current)" if cid in floored else ""
        print("   %-18s share %6.2f%%  raw $%7.2f -> $%7.2f%s"
              % (cname, share[cid] * 100, raw[cid], budgets[cid], tag))
    print("   combined                   : $%.2f" % combined)
    print("   mid-month rule             : %.2f + %.2f x %d = %.2f  (meets 2500: %s)"
          % (S, combined, D, S + combined * D,
             out["recalculated"]["meets_2500"]))

    # ---- compare against the approved plan -------------------------------
    print("\n4. PLAN REVALIDATION")
    plan = yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))
    cp = plan["change_plan"]
    fp = approval_code(normalize(plan))
    plan_budgets = {a["campaign_id"]: a["proposed_value"]["amount_usd"]
                    for a in cp["actions"]}
    full_plan_budgets = dict(plan_budgets)
    for cid in CAMPAIGNS:
        full_plan_budgets.setdefault(cid, camps[cid]["budget_usd"])

    out["plan_fingerprint_recomputed"] = fp
    out["plan_proposed_budgets"] = full_plan_budgets

    gate("fingerprint still %s" % EXPECTED_FP, fp == EXPECTED_FP, "got %s" % fp)
    gate("plan status still NOT APPROVED",
         cp["approval_status"] == "NOT APPROVED")
    for cid, cname in CAMPAIGNS.items():
        gate("%s proposed budget is $%.2f" % (cname, EXPECTED_BUDGETS[cid]),
             abs(full_plan_budgets[cid] - EXPECTED_BUDGETS[cid]) < 0.005,
             "plan says $%.2f" % full_plan_budgets[cid])
        gate("%s recalculation still yields $%.2f" % (cname,
                                                      EXPECTED_BUDGETS[cid]),
             abs(budgets[cid] - EXPECTED_BUDGETS[cid]) < 0.005,
             "recalc says $%.2f" % budgets[cid])
        gate("%s current budget unchanged ($41.11)" % cname,
             camps[cid]["budget_micros"] == 41110000)
        gate("%s bidding still TARGET_SPEND, no CPC ceiling" % cname,
             camps[cid]["bidding"] == "TARGET_SPEND"
             and camps[cid]["cpc_ceiling"] is None)
    gate("geo state intact (80 positive, 1 negative each)",
         all(loc[c]["positive"] == 80 and loc[c]["negative"] == 1
             for c in CAMPAIGNS))

    out["revalidation_passed"] = not fail
    out["changed_items"] = fail
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print()
    if fail:
        print("INPUTS HAVE MOVED - %d item(s) changed:" % len(fail))
        for f in fail:
            print("   %s" % f)
        print("\nPLAN-I1C MUST BE REGENERATED. Do NOT approve %s." % EXPECTED_FP)
        return 2
    print("PLAN-I1C UNCHANGED AND VALID")
    print("   fingerprint %s" % fp)
    print("   Power Washing    / 24103511039 : $333.33/day")
    print("   Power Washing #2 / 24145053510 : $41.11/day (unchanged, no mutation)")
    print()
    print("   APPROVE PLAN-I1C %s FOR %s" % (fp, CID))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
