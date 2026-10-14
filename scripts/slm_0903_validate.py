#!/usr/bin/env python3
"""validate_only preflight for the five Softwind L&M recovery packages.

Every request sets validate_only=True and partial_failure=False, so nothing
durable is created. It still consumes daily mutate quota (memory
validate-only-burns-mutate-quota), so this runs the plans as they will be
executed - not variants.

Writes 10-change-packages/00-validate-receipts.json
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from google.protobuf.field_mask_pb2 import FieldMask  # noqa: E402

CID = "2429758629"
B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PKG = B / "10-change-packages"
PATIO, PAVERS = "23484806108", "23489296528"


def err(exc) -> str:
    m = str(exc)
    for k in ("message: ", "FaultMessage: "):
        if k in m:
            m = m.split(k, 1)[1]
            break
    return m[:400]


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    idx = json.loads((PKG / "00-index.json").read_text(encoding="utf-8"))
    receipts = {"validated_at": datetime.now(ZoneInfo("America/New_York")).isoformat(),
                "customer_id": CID,
                "mode": "validate_only=True, partial_failure=False",
                "results": {}}

    def run(plan, svc_name, ops, batch=1000):
        svc = client.get_service(svc_name)
        req_t = {"CampaignService": "MutateCampaignsRequest",
                 "CampaignBudgetService": "MutateCampaignBudgetsRequest",
                 "AdGroupCriterionService": "MutateAdGroupCriteriaRequest",
                 "CampaignCriterionService": "MutateCampaignCriteriaRequest",
                 "ConversionActionService": "MutateConversionActionsRequest"}[svc_name]
        meth = getattr(svc, {
            "CampaignService": "mutate_campaigns",
            "CampaignBudgetService": "mutate_campaign_budgets",
            "AdGroupCriterionService": "mutate_ad_group_criteria",
            "CampaignCriterionService": "mutate_campaign_criteria",
            "ConversionActionService": "mutate_conversion_actions"}[svc_name])
        total, errors = 0, []
        for i in range(0, len(ops), batch):
            chunk = ops[i:i + batch]
            req = client.get_type(req_t)
            req.customer_id = CID
            req.operations.extend(chunk)
            req.validate_only = True
            req.partial_failure = False
            try:
                meth(request=req)
                total += len(chunk)
            except Exception as exc:  # noqa: BLE001
                errors.append({"batch_start": i, "size": len(chunk), "error": err(exc)})
        ok = not errors
        receipts["results"][plan] = {
            "fingerprint": idx[plan]["fingerprint"],
            "operations_submitted": len(ops), "operations_validated": total,
            "verdict": "PASS" if ok else "FAIL", "errors": errors}
        print("  %-16s %-4s %4d/%-4d ops   %s" % (
            plan, "PASS" if ok else "FAIL", total, len(ops), idx[plan]["fingerprint"]))
        for e in errors:
            print("        %s" % e["error"][:200])

    snap = json.loads((B / "01-before-snapshot.json").read_text(encoding="utf-8"))

    # -------- PLAN-SLM-CONV-1 --------
    ops = []
    for aid in ("7461619140", "7508686781"):
        op = client.get_type("ConversionActionOperation")
        op.update.resource_name = "customers/%s/conversionActions/%s" % (CID, aid)
        op.update.primary_for_goal = False
        op.update_mask.CopyFrom(FieldMask(paths=["primary_for_goal"]))
        ops.append(op)
    run("PLAN-SLM-CONV-1", "ConversionActionService", ops)

    # -------- PLAN-SLM-BID-1 --------
    ops = []
    for cid in (PATIO, PAVERS):
        op = client.get_type("CampaignOperation")
        op.update.resource_name = "customers/%s/campaigns/%s" % (CID, cid)
        op.update.target_spend.cpc_bid_ceiling_micros = 22000000
        op.update_mask.CopyFrom(
            FieldMask(paths=["target_spend.cpc_bid_ceiling_micros"]))
        ops.append(op)
    run("PLAN-SLM-BID-1", "CampaignService", ops)

    # -------- PLAN-SLM-BUD-1 --------
    ops = []
    for cid, amt in ((PATIO, 24000000), (PAVERS, 32000000)):
        bres = snap["campaigns"][cid]["campaign_budget_resource"]
        op = client.get_type("CampaignBudgetOperation")
        op.update.resource_name = bres
        op.update.amount_micros = amt
        op.update_mask.CopyFrom(FieldMask(paths=["amount_micros"]))
        ops.append(op)
    run("PLAN-SLM-BUD-1", "CampaignBudgetService", ops)

    # -------- PLAN-SLM-KW-1 --------
    plan = json.loads((PKG / "PLAN-SLM-KW-1.json").read_text(encoding="utf-8"))
    ops = []
    for a in plan["actions"]:
        op = client.get_type("AdGroupCriterionOperation")
        op.update.resource_name = "customers/%s/adGroupCriteria/%s~%s" % (
            CID, a["ad_group_id"], a["criterion_id"])
        op.update.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ops.append(op)
    run("PLAN-SLM-KW-1", "AdGroupCriterionService", ops)

    # -------- PLAN-SLM-NEG-1 --------
    # NOTE: the 'asphalt' PHRASE negative on Pavers is validated here in the
    # pre-pause account state. If Google rejects it for colliding with a live
    # keyword the dependency on PLAN-SLM-KW-1 is confirmed by the API itself.
    negs = list(csv.DictReader((B / "06-negative-plan.csv").open(encoding="utf-8")))
    ops = []
    for n in negs:
        op = client.get_type("CampaignCriterionOperation")
        c = op.create
        c.campaign = "customers/%s/campaigns/%s" % (CID, n["campaign_id"])
        c.negative = True
        c.keyword.text = n["text"]
        c.keyword.match_type = getattr(client.enums.KeywordMatchTypeEnum,
                                       n["match_type"])
        ops.append(op)
    run("PLAN-SLM-NEG-1", "CampaignCriterionService", ops)

    (PKG / "00-validate-receipts.json").write_text(
        json.dumps(receipts, indent=2), encoding="utf-8")
    fails = [k for k, v in receipts["results"].items() if v["verdict"] != "PASS"]
    print("\nvalidate_only receipts -> %s" %
          (PKG / "00-validate-receipts.json").relative_to(ROOT))
    print("FAILED: %s" % (fails or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
