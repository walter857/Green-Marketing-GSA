#!/usr/bin/env python3
"""STAGE 8 - execute PLAN-J2A under exact approval.

APPROVED PHRASE: APPROVE PLAN-J2A 529FE7F9386D FOR 1521725229

Guard rails, in order:
  1. Fresh identity gate.
  2. Fresh drift snapshot vs the Stage 1 state.
  3. Recompute the fingerprint from the plan file; abort unless it equals the
     approved value exactly.
  4. validate_only dry run of the complete request.
  5. Atomic execution (partial_failure = False) so the request cannot land
     half-applied.
  6. Full readback and QA assertions.

Executes PLAN-J2A ONLY. PLAN-J2B and PLAN-I1C are not approved and are not
touched.
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

APPROVED_PLAN = "PLAN-J2A"
APPROVED_FP = "529FE7F9386D"
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
TZ = ZoneInfo("America/New_York")

CLIENT = ROOT / "clients/softwind-power-washing"
PLANS = CLIENT / "plans"
SNAP = CLIENT / "snapshots"
PLAN_FILE = PLANS / "2026-08-26-plan-j2a-approved-ny-geo.yaml"
OUT = SNAP / "j2a-execution-2026-08-26.json"

STATE = json.loads((SNAP / "stage1-state-2026-08-26.json").read_text("utf-8"))

Q_ID = """
SELECT customer.id, customer.descriptive_name, customer.manager,
       customer.test_account, customer.currency_code, customer.time_zone
FROM customer LIMIT 1
"""
Q_CAMP = """
SELECT campaign.id, campaign.name, campaign.status,
       campaign.bidding_strategy_type,
       campaign.target_spend.cpc_bid_ceiling_micros,
       campaign.geo_target_type_setting.positive_geo_target_type,
       campaign.geo_target_type_setting.negative_geo_target_type,
       campaign_budget.id, campaign_budget.amount_micros
FROM campaign WHERE campaign.status != 'REMOVED'
"""
Q_LOC = """
SELECT campaign.id, campaign_criterion.criterion_id,
       campaign_criterion.resource_name, campaign_criterion.negative,
       campaign_criterion.status,
       campaign_criterion.location.geo_target_constant
FROM campaign_criterion
WHERE campaign_criterion.type = 'LOCATION' AND campaign.status != 'REMOVED'
"""
Q_GEO = """
SELECT geo_target_constant.id, geo_target_constant.canonical_name,
       geo_target_constant.status, geo_target_constant.target_type
FROM geo_target_constant
WHERE geo_target_constant.resource_name IN (%s)
"""
Q_COUNTS = """
SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id
FROM keyword_view WHERE campaign.status != 'REMOVED'
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


def read_locations(svc):
    loc = {c: {"positive": {}, "negative": {}} for c in CAMPAIGNS}
    for row in svc.search(customer_id=CID, query=Q_LOC):
        cid = str(row.campaign.id)
        cc = row.campaign_criterion
        if cid not in loc:
            continue
        gid = cc.location.geo_target_constant.split("/")[-1]
        loc[cid]["negative" if cc.negative else "positive"][gid] = {
            "criterion_id": str(cc.criterion_id),
            "resource_name": cc.resource_name,
            "status": enum_name(cc.status)}
    return loc


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    ccs = client.get_service("CampaignCriterionService")
    camp_svc = client.get_service("CampaignService")
    geo_svc = client.get_service("GeoTargetConstantService")

    started = datetime.now(TZ)
    log = {"stage": 8, "approved_plan": APPROVED_PLAN,
           "approved_fingerprint": APPROVED_FP,
           "started_account_local": started.isoformat()}
    fail = []

    def gate(label, cond, detail=""):
        print("   %-58s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        if not cond:
            fail.append(label)

    # ---------- 1. identity ------------------------------------------------
    print("1. FRESH IDENTITY GATE")
    ident = {}
    for row in svc.search(customer_id=CID, query=Q_ID):
        c = row.customer
        ident = {"id": str(c.id), "name": c.descriptive_name,
                 "manager": c.manager, "test_account": c.test_account,
                 "currency": c.currency_code, "time_zone": c.time_zone}
    log["identity"] = ident
    gate("account name is exactly '%s'" % NAME, ident.get("name") == NAME)
    gate("customer id is %s" % CID, ident.get("id") == CID)
    gate("manager is false", ident.get("manager") is False)
    gate("test_account is false", ident.get("test_account") is False)
    gate("currency is USD", ident.get("currency") == "USD")
    gate("time zone is America/New_York",
         ident.get("time_zone") == "America/New_York")
    if fail:
        print("\nIDENTITY MISMATCH - ABORTING BEFORE ANY WRITE")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    # ---------- 2. drift ---------------------------------------------------
    print("\n2. DRIFT CHECK vs STAGE 1 SNAPSHOT")
    camps = {}
    for row in svc.search(customer_id=CID, query=Q_CAMP):
        cp, b = row.campaign, row.campaign_budget
        camps[str(cp.id)] = {
            "name": cp.name, "status": enum_name(cp.status),
            "bidding": enum_name(cp.bidding_strategy_type),
            "cpc_ceiling": cp.target_spend.cpc_bid_ceiling_micros or None,
            "positive_geo": enum_name(
                cp.geo_target_type_setting.positive_geo_target_type),
            "negative_geo": enum_name(
                cp.geo_target_type_setting.negative_geo_target_type),
            "budget_id": str(b.id), "budget_micros": b.amount_micros}
    before = read_locations(svc)
    log["before"] = {"campaigns": camps,
                     "locations": {c: {"positive": sorted(before[c]["positive"]),
                                       "negative": sorted(before[c]["negative"])}
                                   for c in CAMPAIGNS}}
    gate("campaign count is still 2", len(camps) == 2)
    for cid in CAMPAIGNS:
        s1 = STATE["campaigns"][cid]
        gate("%s budget unchanged ($%.2f)" % (cid, s1["budget_usd"]),
             camps[cid]["budget_micros"] == s1["budget_micros"])
        gate("%s bidding unchanged (%s)" % (cid, s1["bidding_strategy"]),
             camps[cid]["bidding"] == s1["bidding_strategy"])
        gate("%s no CPC ceiling" % cid, camps[cid]["cpc_ceiling"] is None)
        gate("%s PRESENCE unchanged" % cid, camps[cid]["positive_geo"] == "PRESENCE")
        s1loc = {p["geo_target_constant_id"]
                 for p in STATE["location_criteria"][cid]["positive"]}
        gate("%s still has exactly 8 positive targets" % cid,
             len(before[cid]["positive"]) == 8)
        gate("%s positive target IDs unchanged" % cid,
             set(before[cid]["positive"]) == s1loc)
        gate("%s still has 0 negative locations" % cid,
             len(before[cid]["negative"]) == 0)
    if fail:
        print("\nDRIFT DETECTED - ABORTING BEFORE ANY WRITE")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    # ---------- 3. fingerprint --------------------------------------------
    print("\n3. FINGERPRINT VERIFICATION")
    plan = yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))
    cp = plan["change_plan"]
    recomputed = approval_code(normalize(plan))
    log["fingerprint_recomputed"] = recomputed
    gate("plan_id is %s" % APPROVED_PLAN, cp["plan_id"] == APPROVED_PLAN)
    gate("recomputed fingerprint == %s" % APPROVED_FP, recomputed == APPROVED_FP,
         "got %s" % recomputed)
    gate("plan targets customer %s" % CID,
         cp["target"]["child_customer_id"] == CID)
    gate("plan action count is 144", len(cp["actions"]) == 144)
    if fail:
        print("\nFINGERPRINT MISMATCH - ABORTING BEFORE ANY WRITE")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    # ---------- 4. build operations ---------------------------------------
    print("\n4. BUILDING OPERATIONS")
    ops, planned = [], {c: set() for c in CAMPAIGNS}
    for a in cp["actions"]:
        cid = a["campaign_id"]
        gid = a["proposed_value"]["geo_target_constant_id"]
        if a["proposed_value"]["negative"] is not False:
            print("   REFUSING - action %s is not positive" % a["action_id"])
            return 1
        if gid in before[cid]["positive"]:
            print("   REFUSING - %s already targeted in %s" % (gid, cid))
            return 1
        op = client.get_type("CampaignCriterionOperation")
        crit = op.create
        crit.campaign = camp_svc.campaign_path(CID, cid)
        crit.location.geo_target_constant = geo_svc.geo_target_constant_path(gid)
        crit.negative = False
        ops.append(op)
        planned[cid].add(gid)
    print("   built %d operations  (A=%d, B=%d)"
          % (len(ops), len(planned["24103511039"]), len(planned["24145053510"])))
    gate("operation count == 144", len(ops) == 144)
    gate("72 distinct targets per campaign",
         all(len(planned[c]) == 72 for c in CAMPAIGNS))
    if fail:
        return 1

    # ---------- 5. validate_only dry run ----------------------------------
    print("\n5. VALIDATE-ONLY DRY RUN (nothing is applied)")
    req = client.get_type("MutateCampaignCriteriaRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    req.partial_failure = False
    req.validate_only = True
    try:
        ccs.mutate_campaign_criteria(request=req)
        print("   dry run PASSED - Google accepted all 144 operations")
        log["dry_run"] = "PASSED"
    except Exception as exc:                                  # noqa: BLE001
        print("   dry run FAILED - nothing was applied")
        print("   %s" % str(exc)[:1200])
        log["dry_run"] = "FAILED"
        log["dry_run_error"] = str(exc)[:4000]
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    # ---------- 6. execute atomically -------------------------------------
    print("\n6. EXECUTING - atomic, partial_failure=False")
    req.validate_only = False
    exec_at = datetime.now(TZ)
    try:
        resp = ccs.mutate_campaign_criteria(request=req)
    except Exception as exc:                                  # noqa: BLE001
        print("   MUTATE FAILED - request was atomic, so nothing was applied")
        print("   %s" % str(exc)[:1500])
        log["execution"] = "FAILED_ATOMIC_NO_CHANGE"
        log["execution_error"] = str(exc)[:4000]
        after = read_locations(svc)
        log["post_failure_positive_counts"] = {
            c: len(after[c]["positive"]) for c in CAMPAIGNS}
        print("   post-failure positive counts: %s"
              % log["post_failure_positive_counts"])
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    created = [r.resource_name for r in resp.results]
    log["execution"] = "SUCCEEDED"
    log["executed_account_local"] = exec_at.isoformat()
    log["created_resource_names"] = created
    log["created_count"] = len(created)
    print("   created %d campaign criteria" % len(created))

    # ---------- 7. readback -----------------------------------------------
    print("\n7. READBACK")
    after = read_locations(svc)
    camps2 = {}
    for row in svc.search(customer_id=CID, query=Q_CAMP):
        c2, b2 = row.campaign, row.campaign_budget
        camps2[str(c2.id)] = {
            "bidding": enum_name(c2.bidding_strategy_type),
            "cpc_ceiling": c2.target_spend.cpc_bid_ceiling_micros or None,
            "positive_geo": enum_name(
                c2.geo_target_type_setting.positive_geo_target_type),
            "negative_geo": enum_name(
                c2.geo_target_type_setting.negative_geo_target_type),
            "budget_micros": b2.amount_micros}

    all_ids = sorted({g for c in CAMPAIGNS for g in after[c]["positive"]})
    resolved = {}
    for i in range(0, len(all_ids), 50):
        cond = ",".join("'geoTargetConstants/%s'" % x for x in all_ids[i:i + 50])
        for row in svc.search(customer_id=CID, query=Q_GEO % cond):
            g = row.geo_target_constant
            resolved[str(g.id)] = {"canonical_name": g.canonical_name,
                                   "target_type": g.target_type,
                                   "status": enum_name(g.status)}

    log["after"] = {
        "campaigns": camps2,
        "positive_counts": {c: len(after[c]["positive"]) for c in CAMPAIGNS},
        "negative_counts": {c: len(after[c]["negative"]) for c in CAMPAIGNS},
        "positive_ids": {c: sorted(after[c]["positive"]) for c in CAMPAIGNS}}

    print("\n8. QA ASSERTIONS")
    for cid, cname in CAMPAIGNS.items():
        pos = after[cid]["positive"]
        orig = set(before[cid]["positive"])
        gate("%s positive count == 80" % cname, len(pos) == 80,
             "got %d" % len(pos))
        gate("%s all 8 pre-existing targets still present" % cname,
             orig.issubset(set(pos)), "missing %s" % sorted(orig - set(pos)))
        gate("%s all 72 planned targets created" % cname,
             planned[cid].issubset(set(pos)),
             "missing %s" % sorted(planned[cid] - set(pos)))
        gate("%s no unexpected extra target" % cname,
             set(pos) == orig | planned[cid])
        gate("%s zero negative location criteria (J2B not approved)" % cname,
             len(after[cid]["negative"]) == 0)
        gate("%s every positive target is New York, US" % cname,
             all(",New York,United States" in resolved[g]["canonical_name"]
                 for g in pos))
        gate("%s every positive target ENABLED" % cname,
             all(resolved[g]["status"] == "ENABLED" for g in pos))
        gate("%s PRESENCE unchanged" % cname,
             camps2[cid]["positive_geo"] == "PRESENCE"
             and camps2[cid]["negative_geo"] == "PRESENCE")
        gate("%s budget unchanged" % cname,
             camps2[cid]["budget_micros"] == camps[cid]["budget_micros"])
        gate("%s bidding unchanged (%s)" % (cname, camps[cid]["bidding"]),
             camps2[cid]["bidding"] == camps[cid]["bidding"])
        gate("%s still no CPC ceiling" % cname, camps2[cid]["cpc_ceiling"] is None)

    non_ny = [g for c in CAMPAIGNS for g in after[c]["positive"]
              if ",New York,United States" not in resolved[g]["canonical_name"]]
    gate("ZERO non-New-York targets anywhere in the account", not non_ny,
         str(non_ny))
    gate("total created == 144", len(created) == 144)

    log["qa_failures"] = fail
    log["qa_passed"] = not fail
    OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")

    print()
    if fail:
        print("QA FAILURES: %d" % len(fail))
        for f in fail:
            print("   %s" % f)
        print("\nSTOPPING. Created resource IDs are inventoried in %s" % OUT.name)
        return 1
    print("PLAN-J2A EXECUTED AND VERIFIED - %d criteria created, 0 removed"
          % len(created))
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
