#!/usr/bin/env python3
"""STAGE 11 - execute PLAN-I1C under exact approval.

APPROVED PHRASE: APPROVE PLAN-I1C 8CC6CABFC74F FOR 1521725229

Budget-only. Same guard rails as the geo executions: identity gate, same-minute
drift snapshot, fingerprint recomputation, validate_only dry run, atomic mutate,
full readback.

Also asserts the budget is NOT explicitly shared before writing, so the change
cannot reach a campaign outside this plan.
"""
from __future__ import annotations

import json
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

APPROVED_PLAN = "PLAN-I1C"
APPROVED_FP = "8CC6CABFC74F"
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
TZ = ZoneInfo("America/New_York")
TARGET = 2500.0

CLIENT = ROOT / "clients/softwind-power-washing"
PLAN_FILE = CLIENT / "plans/2026-08-26-plan-i1c-budget-after-full-geo.yaml"
OUT = CLIENT / "snapshots/i1c-execution-2026-08-26.json"

Q_ID = """
SELECT customer.id, customer.descriptive_name, customer.manager,
       customer.test_account, customer.currency_code, customer.time_zone
FROM customer LIMIT 1
"""
Q_CAMP = """
SELECT campaign.id, campaign.name, campaign.status,
       campaign.bidding_strategy_type,
       campaign.target_spend.cpc_bid_ceiling_micros,
       campaign.network_settings.target_content_network,
       campaign.network_settings.target_partner_search_network,
       campaign.geo_target_type_setting.positive_geo_target_type,
       campaign_budget.id, campaign_budget.amount_micros,
       campaign_budget.explicitly_shared, campaign_budget.delivery_method,
       campaign_budget.reference_count
FROM campaign WHERE campaign.status != 'REMOVED'
"""
Q_LOC = """
SELECT campaign.id, campaign_criterion.negative
FROM campaign_criterion
WHERE campaign_criterion.type = 'LOCATION' AND campaign.status != 'REMOVED'
"""
Q_SPEND = """
SELECT campaign.id, metrics.cost_micros, metrics.impressions, metrics.clicks
FROM campaign
WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-26'
  AND campaign.status != 'REMOVED'
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


def counts(svc):
    def one(q):
        return sum(1 for _ in svc.search(customer_id=CID, query=q))
    return {
        "keywords": one("SELECT ad_group_criterion.criterion_id FROM keyword_view "
                        "WHERE campaign.status != 'REMOVED'"),
        "ads": one("SELECT ad_group_ad.ad.id FROM ad_group_ad "
                   "WHERE ad_group_ad.status != 'REMOVED'"),
        "campaign_negative_keywords": one(
            "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
            "WHERE campaign_criterion.type='KEYWORD' "
            "AND campaign_criterion.negative=true"),
        "ad_schedules": one("SELECT campaign_criterion.criterion_id FROM "
                            "campaign_criterion WHERE "
                            "campaign_criterion.type='AD_SCHEDULE'"),
        "conversion_actions": one("SELECT conversion_action.id FROM "
                                  "conversion_action WHERE "
                                  "conversion_action.status != 'REMOVED'"),
        "campaign_assets": one("SELECT campaign_asset.asset FROM campaign_asset "
                               "WHERE campaign_asset.status != 'REMOVED'"),
        "ad_groups": one("SELECT ad_group.id FROM ad_group "
                         "WHERE ad_group.status != 'REMOVED'"),
    }


def read_state(svc):
    camps = {}
    for row in svc.search(customer_id=CID, query=Q_CAMP):
        c, b = row.campaign, row.campaign_budget
        camps[str(c.id)] = {
            "name": c.name, "status": enum_name(c.status),
            "bidding": enum_name(c.bidding_strategy_type),
            "cpc_ceiling": c.target_spend.cpc_bid_ceiling_micros or None,
            "display": c.network_settings.target_content_network,
            "partners": c.network_settings.target_partner_search_network,
            "positive_geo": enum_name(
                c.geo_target_type_setting.positive_geo_target_type),
            "budget_id": str(b.id), "budget_micros": b.amount_micros,
            "budget_usd": round(b.amount_micros / 1e6, 2),
            "explicitly_shared": b.explicitly_shared,
            "reference_count": b.reference_count,
            "delivery": enum_name(b.delivery_method)}
    loc = {c: {"positive": 0, "negative": 0} for c in CAMPAIGNS}
    for row in svc.search(customer_id=CID, query=Q_LOC):
        cid = str(row.campaign.id)
        if cid in loc:
            loc[cid]["negative" if row.campaign_criterion.negative
                     else "positive"] += 1
    return camps, loc


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cbs = client.get_service("CampaignBudgetService")

    started = datetime.now(TZ)
    log = {"stage": 11, "approved_plan": APPROVED_PLAN,
           "approved_fingerprint": APPROVED_FP,
           "started_account_local": started.isoformat()}
    fail = []

    def gate(label, cond, detail=""):
        print("   %-58s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        if not cond:
            fail.append(label)

    print("1. IDENTITY GATE")
    for row in svc.search(customer_id=CID, query=Q_ID):
        c = row.customer
        log["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                           "manager": c.manager, "test_account": c.test_account,
                           "currency": c.currency_code,
                           "time_zone": c.time_zone}
    i = log["identity"]
    gate("account is '%s'" % NAME, i["name"] == NAME)
    gate("customer id is %s" % CID, i["id"] == CID)
    gate("manager false / test false",
         i["manager"] is False and i["test_account"] is False)
    gate("currency USD, tz America/New_York",
         i["currency"] == "USD" and i["time_zone"] == "America/New_York")
    if fail:
        print("\nIDENTITY MISMATCH - ABORTING BEFORE ANY WRITE")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    print("\n2. SAME-MINUTE DRIFT SNAPSHOT")
    before, loc_before = read_state(svc)
    cnt_before = counts(svc)
    log["before"] = {"campaigns": before, "locations": loc_before,
                     "counts": cnt_before}
    for cid, cname in CAMPAIGNS.items():
        b = before[cid]
        gate("%s budget still $41.11" % cname, b["budget_micros"] == 41110000,
             "got %s" % b["budget_micros"])
        gate("%s bidding TARGET_SPEND, no CPC ceiling" % cname,
             b["bidding"] == "TARGET_SPEND" and b["cpc_ceiling"] is None)
        gate("%s budget NOT explicitly shared" % cname,
             b["explicitly_shared"] is False)
        gate("%s budget reference_count == 1" % cname,
             b["reference_count"] == 1, "got %s" % b["reference_count"])
        gate("%s geo intact: 80 positive / 1 negative" % cname,
             loc_before[cid]["positive"] == 80
             and loc_before[cid]["negative"] == 1)
        gate("%s PRESENCE unchanged" % cname, b["positive_geo"] == "PRESENCE")
    print("   inventory: %s" % cnt_before)
    if fail:
        print("\nDRIFT DETECTED - ABORTING BEFORE ANY WRITE")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    print("\n3. FINGERPRINT VERIFICATION")
    plan = yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))
    cp = plan["change_plan"]
    recomputed = approval_code(normalize(plan))
    log["fingerprint_recomputed"] = recomputed
    gate("plan_id is %s" % APPROVED_PLAN, cp["plan_id"] == APPROVED_PLAN)
    gate("recomputed fingerprint == %s" % APPROVED_FP,
         recomputed == APPROVED_FP, "got %s" % recomputed)
    gate("plan targets customer %s" % CID,
         cp["target"]["child_customer_id"] == CID)
    gate("approval_type is BUDGET", cp["approval_type"] == "BUDGET")
    gate("exactly 1 action", len(cp["actions"]) == 1)
    if fail:
        print("\nFINGERPRINT MISMATCH - ABORTING BEFORE ANY WRITE")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    print("\n4. BUILDING OPERATION")
    ops, intended = [], {}
    for a in cp["actions"]:
        cid = a["campaign_id"]
        bid = a["resource_id"]
        want = a["proposed_value"]["amount_micros"]
        if a["resource_type"] != "CAMPAIGN_BUDGET" or a["operation"] != "UPDATE":
            print("   REFUSING - action %s is not a budget update" % a["action_id"])
            return 1
        if bid != before[cid]["budget_id"]:
            print("   REFUSING - budget id mismatch for %s: plan %s, live %s"
                  % (cid, bid, before[cid]["budget_id"]))
            return 1
        if want < before[cid]["budget_micros"]:
            print("   REFUSING - action %s would REDUCE the budget" % a["action_id"])
            return 1
        op = client.get_type("CampaignBudgetOperation")
        bu = op.update
        bu.resource_name = cbs.campaign_budget_path(CID, bid)
        bu.amount_micros = want
        # Build the mask EXPLICITLY. protobuf_helpers.field_mask(None, ...) also
        # lists resource_name, which widens the mask beyond the one field this
        # plan authorises.
        op.update_mask.paths.append("amount_micros")
        ops.append(op)
        intended[cid] = want
        print("   %s %-18s budget %s: %d -> %d micros ($%.2f -> $%.2f)"
              % (cid, CAMPAIGNS[cid], bid, before[cid]["budget_micros"], want,
                 before[cid]["budget_usd"], want / 1e6))
    gate("exactly 1 operation built", len(ops) == 1)
    gate("update mask is amount_micros only",
         list(ops[0].update_mask.paths) == ["amount_micros"],
         str(list(ops[0].update_mask.paths)))
    untouched = [c for c in CAMPAIGNS if c not in intended]
    print("   untouched (no mutation): %s"
          % [CAMPAIGNS[c] for c in untouched])
    if fail:
        return 1

    print("\n5. VALIDATE-ONLY DRY RUN (nothing is applied)")
    req = client.get_type("MutateCampaignBudgetsRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    req.partial_failure = False
    req.validate_only = True
    try:
        cbs.mutate_campaign_budgets(request=req)
        print("   dry run PASSED")
        log["dry_run"] = "PASSED"
    except Exception as exc:                                  # noqa: BLE001
        print("   dry run FAILED - nothing was applied")
        print("   %s" % str(exc)[:1200])
        log["dry_run"] = "FAILED"
        log["dry_run_error"] = str(exc)[:4000]
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    print("\n6. EXECUTING - atomic, partial_failure=False")
    req.validate_only = False
    exec_at = datetime.now(TZ)
    try:
        resp = cbs.mutate_campaign_budgets(request=req)
    except Exception as exc:                                  # noqa: BLE001
        print("   MUTATE FAILED - request was atomic, nothing was applied")
        print("   %s" % str(exc)[:1500])
        log["execution"] = "FAILED_ATOMIC_NO_CHANGE"
        log["execution_error"] = str(exc)[:4000]
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    changed = [r.resource_name for r in resp.results]
    log["execution"] = "SUCCEEDED"
    log["executed_account_local"] = exec_at.isoformat()
    log["changed_resource_names"] = changed
    print("   updated %d budget(s)" % len(changed))
    for r in changed:
        print("      %s" % r)

    print("\n7. READBACK AND QA")
    after, loc_after = read_state(svc)
    cnt_after = counts(svc)
    log["after"] = {"campaigns": after, "locations": loc_after,
                    "counts": cnt_after}

    for cid, cname in CAMPAIGNS.items():
        exp = intended.get(cid, before[cid]["budget_micros"])
        gate("%s budget is now $%.2f" % (cname, exp / 1e6),
             after[cid]["budget_micros"] == exp,
             "got $%.2f" % after[cid]["budget_usd"])
        gate("%s bidding still TARGET_SPEND (Maximize Clicks)" % cname,
             after[cid]["bidding"] == "TARGET_SPEND")
        gate("%s NO CPC ceiling added" % cname,
             after[cid]["cpc_ceiling"] is None)
        gate("%s budget still not explicitly shared" % cname,
             after[cid]["explicitly_shared"] is False)
        gate("%s locations unchanged (80 positive / 1 negative)" % cname,
             loc_after[cid] == loc_before[cid], str(loc_after[cid]))
        gate("%s PRESENCE unchanged" % cname,
             after[cid]["positive_geo"] == "PRESENCE")
        gate("%s Search Partners and Display still OFF" % cname,
             after[cid]["partners"] is False and after[cid]["display"] is False)
    for cid in untouched:
        gate("%s budget genuinely untouched" % CAMPAIGNS[cid],
             after[cid]["budget_micros"] == before[cid]["budget_micros"])
    for k in cnt_before:
        gate("%s count unchanged (%d)" % (k, cnt_before[k]),
             cnt_after[k] == cnt_before[k],
             "was %d now %d" % (cnt_before[k], cnt_after[k]))

    # ---- pacing report --------------------------------------------------
    print("\n8. PACING REPORT")
    spend = {}
    for row in svc.search(customer_id=CID, query=Q_SPEND):
        m = row.metrics
        spend[str(row.campaign.id)] = {"cost": round(m.cost_micros / 1e6, 2),
                                       "impressions": m.impressions,
                                       "clicks": m.clicks}
    now = datetime.now(TZ)
    S = round(sum(v["cost"] for v in spend.values()), 2)
    R = round(TARGET - S, 2)
    sept1 = datetime(2026, 9, 1, tzinfo=TZ)
    H = (sept1 - now).total_seconds() / 3600.0
    D = 31 - now.day + 1
    combined = round(sum(after[c]["budget_usd"] for c in CAMPAIGNS), 2)
    pacing = {
        "timestamp": now.isoformat(), "mtd_spend_S": S, "per_campaign": spend,
        "remaining_R": R, "remaining_days_D": D, "remaining_hours_H": round(H, 2),
        "required_avg_per_calendar_day": round(R / D, 2),
        "required_rolling_24h_pace": round(R / (H / 24.0), 2),
        "combined_daily_budget": combined,
        "combined_daily_delivery_ceiling_2x": round(combined * 2, 2),
        "remaining_month_billing_capacity": round(combined * D, 2),
        "mid_month_projection": round(S + combined * D, 2),
        "meets_2500": (S + combined * D) >= TARGET - 0.02,
        "checkpoints": [
            "2026-08-27 pre-08:00 ET - before ads begin serving",
            "2026-08-27 09:00 ET", "2026-08-27 13:00 ET",
            "2026-08-27 17:00 ET", "2026-08-27 end of day"],
        "no_automation": ("No future budget change is automated. Every further "
                          "adjustment requires a new snapshot, plan, fingerprint "
                          "and explicit approval.")}
    log["pacing"] = pacing
    for k in ("mtd_spend_S", "remaining_R", "remaining_days_D",
              "remaining_hours_H", "required_rolling_24h_pace",
              "combined_daily_budget", "combined_daily_delivery_ceiling_2x",
              "remaining_month_billing_capacity", "mid_month_projection",
              "meets_2500"):
        print("   %-40s %s" % (k, pacing[k]))

    log["qa_failures"] = fail
    log["qa_passed"] = not fail
    OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")

    print()
    if fail:
        print("QA FAILURES: %d" % len(fail))
        for f in fail:
            print("   %s" % f)
        return 1
    print("PLAN-I1C EXECUTED AND VERIFIED")
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
