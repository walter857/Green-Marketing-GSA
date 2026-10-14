#!/usr/bin/env python3
"""STAGE 8 (steps 9-11) - execute PLAN-J2B under exact approval.

APPROVED PHRASE: APPROVE PLAN-J2B 2A53E12D68F0 FOR 1521725229

Same guard rails as the J2A execution: identity gate, drift check against the
verified post-J2A state, fingerprint recomputation, validate_only dry run, then
an atomic mutate. Executes PLAN-J2B ONLY. PLAN-I1C is not approved and is not
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

APPROVED_PLAN = "PLAN-J2B"
APPROVED_FP = "2A53E12D68F0"
CT_ID = "21139"
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
TZ = ZoneInfo("America/New_York")

CLIENT = ROOT / "clients/softwind-power-washing"
PLANS = CLIENT / "plans"
SNAP = CLIENT / "snapshots"
PLAN_FILE = PLANS / "2026-08-26-plan-j2b-connecticut-exclusion.yaml"
OUT = SNAP / "j2b-execution-2026-08-26.json"

J2A = json.loads((SNAP / "j2a-execution-2026-08-26.json").read_text("utf-8"))

Q_ID = """
SELECT customer.id, customer.descriptive_name, customer.manager,
       customer.test_account, customer.currency_code, customer.time_zone
FROM customer LIMIT 1
"""
Q_CAMP = """
SELECT campaign.id, campaign.bidding_strategy_type,
       campaign.target_spend.cpc_bid_ceiling_micros,
       campaign.network_settings.target_content_network,
       campaign.network_settings.target_partner_search_network,
       campaign.geo_target_type_setting.positive_geo_target_type,
       campaign.geo_target_type_setting.negative_geo_target_type,
       campaign_budget.amount_micros
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
       geo_target_constant.target_type, geo_target_constant.status,
       geo_target_constant.country_code
FROM geo_target_constant
WHERE geo_target_constant.resource_name IN (%s)
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
    log = {"stage": "8.9-8.11", "approved_plan": APPROVED_PLAN,
           "approved_fingerprint": APPROVED_FP,
           "started_account_local": started.isoformat()}
    fail = []

    def gate(label, cond, detail=""):
        print("   %-58s %s %s" % (label, "PASS" if cond else "FAIL", detail))
        if not cond:
            fail.append(label)

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

    print("\n2. DRIFT CHECK vs VERIFIED POST-J2A STATE")
    camps = {}
    for row in svc.search(customer_id=CID, query=Q_CAMP):
        cp2, b = row.campaign, row.campaign_budget
        camps[str(cp2.id)] = {
            "bidding": enum_name(cp2.bidding_strategy_type),
            "cpc_ceiling": cp2.target_spend.cpc_bid_ceiling_micros or None,
            "display": cp2.network_settings.target_content_network,
            "partners": cp2.network_settings.target_partner_search_network,
            "positive_geo": enum_name(
                cp2.geo_target_type_setting.positive_geo_target_type),
            "negative_geo": enum_name(
                cp2.geo_target_type_setting.negative_geo_target_type),
            "budget_micros": b.amount_micros}
    before = read_locations(svc)
    log["before"] = {c: {"positive": len(before[c]["positive"]),
                         "negative": sorted(before[c]["negative"])}
                     for c in CAMPAIGNS}
    for cid, cname in CAMPAIGNS.items():
        exp = J2A["after"]["positive_ids"][cid]
        gate("%s still has 80 positive targets" % cname,
             len(before[cid]["positive"]) == 80,
             "got %d" % len(before[cid]["positive"]))
        gate("%s positive target IDs identical to J2A readback" % cname,
             sorted(before[cid]["positive"]) == exp)
        gate("%s still has 0 negative locations" % cname,
             len(before[cid]["negative"]) == 0,
             "got %d" % len(before[cid]["negative"]))
        gate("%s PRESENCE unchanged" % cname,
             camps[cid]["positive_geo"] == "PRESENCE"
             and camps[cid]["negative_geo"] == "PRESENCE")
        gate("%s budget unchanged ($41.11)" % cname,
             camps[cid]["budget_micros"] == 41110000)
        gate("%s bidding still TARGET_SPEND, no CPC ceiling" % cname,
             camps[cid]["bidding"] == "TARGET_SPEND"
             and camps[cid]["cpc_ceiling"] is None)
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
    gate("recomputed fingerprint == %s" % APPROVED_FP, recomputed == APPROVED_FP,
         "got %s" % recomputed)
    gate("plan targets customer %s" % CID,
         cp["target"]["child_customer_id"] == CID)
    gate("plan action count is 2", len(cp["actions"]) == 2)
    if fail:
        print("\nFINGERPRINT MISMATCH - ABORTING BEFORE ANY WRITE")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    print("\n4. RE-VERIFY THE CONNECTICUT CONSTANT LIVE")
    ct = {}
    for row in svc.search(customer_id=CID,
                          query=Q_GEO % ("'geoTargetConstants/%s'" % CT_ID)):
        g = row.geo_target_constant
        ct = {"id": str(g.id), "canonical_name": g.canonical_name,
              "target_type": g.target_type, "status": enum_name(g.status),
              "country_code": g.country_code}
    log["connecticut_constant"] = ct
    gate("21139 canonical is 'Connecticut,United States'",
         ct.get("canonical_name") == "Connecticut,United States")
    gate("21139 target type is State", ct.get("target_type") == "State")
    gate("21139 status is ENABLED", ct.get("status") == "ENABLED")
    gate("21139 country is US", ct.get("country_code") == "US")
    if fail:
        return 1

    print("\n5. BUILDING OPERATIONS")
    ops = []
    for a in cp["actions"]:
        pv = a["proposed_value"]
        if pv["negative"] is not True:
            print("   REFUSING - action %s is not a negative criterion"
                  % a["action_id"])
            return 1
        if pv["geo_target_constant_id"] != CT_ID:
            print("   REFUSING - action %s targets %s, not Connecticut"
                  % (a["action_id"], pv["geo_target_constant_id"]))
            return 1
        cid = a["campaign_id"]
        if CT_ID in before[cid]["negative"]:
            print("   REFUSING - Connecticut already excluded on %s" % cid)
            return 1
        op = client.get_type("CampaignCriterionOperation")
        crit = op.create
        crit.campaign = camp_svc.campaign_path(CID, cid)
        crit.location.geo_target_constant = geo_svc.geo_target_constant_path(CT_ID)
        crit.negative = True
        ops.append(op)
    gate("operation count == 2", len(ops) == 2)
    gate("both operations are negative and Connecticut-only", True)
    if fail:
        return 1

    print("\n6. VALIDATE-ONLY DRY RUN (nothing is applied)")
    req = client.get_type("MutateCampaignCriteriaRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    req.partial_failure = False
    req.validate_only = True
    try:
        ccs.mutate_campaign_criteria(request=req)
        print("   dry run PASSED")
        log["dry_run"] = "PASSED"
    except Exception as exc:                                  # noqa: BLE001
        print("   dry run FAILED - nothing was applied")
        print("   %s" % str(exc)[:1200])
        log["dry_run"] = "FAILED"
        log["dry_run_error"] = str(exc)[:4000]
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    print("\n7. EXECUTING - atomic, partial_failure=False")
    req.validate_only = False
    exec_at = datetime.now(TZ)
    try:
        resp = ccs.mutate_campaign_criteria(request=req)
    except Exception as exc:                                  # noqa: BLE001
        print("   MUTATE FAILED - request was atomic, so nothing was applied")
        print("   %s" % str(exc)[:1500])
        log["execution"] = "FAILED_ATOMIC_NO_CHANGE"
        log["execution_error"] = str(exc)[:4000]
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    created = [r.resource_name for r in resp.results]
    log["execution"] = "SUCCEEDED"
    log["executed_account_local"] = exec_at.isoformat()
    log["created_resource_names"] = created
    log["created_count"] = len(created)
    print("   created %d negative campaign criteria" % len(created))
    for r in created:
        print("      %s" % r)

    print("\n8. READBACK AND QA")
    after = read_locations(svc)
    camps2 = {}
    for row in svc.search(customer_id=CID, query=Q_CAMP):
        c2, b2 = row.campaign, row.campaign_budget
        camps2[str(c2.id)] = {
            "bidding": enum_name(c2.bidding_strategy_type),
            "cpc_ceiling": c2.target_spend.cpc_bid_ceiling_micros or None,
            "display": c2.network_settings.target_content_network,
            "partners": c2.network_settings.target_partner_search_network,
            "positive_geo": enum_name(
                c2.geo_target_type_setting.positive_geo_target_type),
            "negative_geo": enum_name(
                c2.geo_target_type_setting.negative_geo_target_type),
            "budget_micros": b2.amount_micros}
    log["after"] = {c: {"positive": len(after[c]["positive"]),
                        "negative": sorted(after[c]["negative"]),
                        "negative_detail": after[c]["negative"]}
                    for c in CAMPAIGNS}

    for cid, cname in CAMPAIGNS.items():
        gate("%s exactly 1 negative location criterion" % cname,
             len(after[cid]["negative"]) == 1,
             "got %d" % len(after[cid]["negative"]))
        gate("%s the negative is Connecticut 21139" % cname,
             list(after[cid]["negative"]) == [CT_ID])
        gate("%s positive count still 80" % cname,
             len(after[cid]["positive"]) == 80,
             "got %d" % len(after[cid]["positive"]))
        gate("%s positive target IDs unchanged by this plan" % cname,
             sorted(after[cid]["positive"]) == sorted(before[cid]["positive"]))
        gate("%s PRESENCE unchanged" % cname,
             camps2[cid]["positive_geo"] == "PRESENCE"
             and camps2[cid]["negative_geo"] == "PRESENCE")
        gate("%s budget unchanged" % cname,
             camps2[cid]["budget_micros"] == camps[cid]["budget_micros"])
        gate("%s bidding unchanged, still no CPC ceiling" % cname,
             camps2[cid]["bidding"] == "TARGET_SPEND"
             and camps2[cid]["cpc_ceiling"] is None)
        gate("%s Search Partners and Display still OFF" % cname,
             camps2[cid]["partners"] is False and camps2[cid]["display"] is False)

    all_neg = {g for c in CAMPAIGNS for g in after[c]["negative"]}
    gate("no location exclusion other than Connecticut exists",
         all_neg == {CT_ID}, str(sorted(all_neg)))
    gate("total created == 2", len(created) == 2)

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
    print("PLAN-J2B EXECUTED AND VERIFIED - %d exclusions created, 0 removed"
          % len(created))
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
