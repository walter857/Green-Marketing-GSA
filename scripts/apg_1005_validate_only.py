#!/usr/bin/env python3
"""2026-10-05 VALIDATE-ONLY dry run of APG-1005-KWNEG and APG-1005-ADS. Writes nothing.

Builds the exact operations from the plan files and sends them with validate_only=True and
partial_failure=False. The send helper refuses any call without validate_only=True. A fresh
identity gate runs first. (Note: validate_only consumes the same daily operation quota as a
real write; 13 operations here.)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, ROOT, client, q  # noqa: E402

from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

c = client()
PL = ROOT / "clients" / "apogee-lawns" / "plans"
FP = json.loads((ROOT / "clients/apogee-lawns/audits/2026-10-05-conversion-plan/bundle-fingerprints.json").read_text())["fingerprints"]
out = {}

cust = q(c, "SELECT customer.id, customer.descriptive_name, customer.manager, customer.test_account FROM customer")[0].customer
assert str(cust.id) == CID and cust.descriptive_name == EXACT_NAME and not cust.manager and not cust.test_account, "IDENTITY GATE FAIL"
print("identity gate PASS:", cust.descriptive_name, cust.id)


def send(ops, validate_only):
    assert validate_only is True, "this script may only validate"
    svc = c.get_service("GoogleAdsService")
    req = c.get_type("MutateGoogleAdsRequest")
    req.customer_id = CID
    req.mutate_operations.extend(ops)
    req.partial_failure = False
    req.validate_only = True
    assert req.validate_only is True
    return svc.mutate(request=req)


def kwneg_ops(plan):
    ops = []
    for o in plan["objects"]:
        op = c.get_type("MutateOperation")
        if o["resource"] == "ad_group_criterion":
            cr = op.ad_group_criterion_operation.create
            cr.ad_group = f"customers/{CID}/adGroups/{o['ad_group_id']}"
            cr.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
            cr.keyword.text = o["keyword"]["text"]
            cr.keyword.match_type = c.enums.KeywordMatchTypeEnum[o["keyword"]["match_type"]]
        elif o["operation"] == "create":
            cr = op.campaign_criterion_operation.create
            cr.campaign = f"customers/{CID}/campaigns/{o['campaign_id']}"
            cr.negative = True
            cr.keyword.text = o["keyword"]["text"]
            cr.keyword.match_type = c.enums.KeywordMatchTypeEnum[o["keyword"]["match_type"]]
        else:
            op.campaign_criterion_operation.remove = o["resource_name"]
        ops.append(op)
    return ops


def ads_ops(plan):
    ops = []
    for o in plan["objects"]:
        op = c.get_type("MutateOperation")
        if o["resource"] == "ad_group_ad":
            spec = o["responsive_search_ad"]
            aga = op.ad_group_ad_operation.create
            aga.ad_group = f"customers/{CID}/adGroups/{spec['ad_group_id']}"
            aga.status = c.enums.AdGroupAdStatusEnum.PAUSED
            aga.ad.final_urls.extend(spec["final_urls"])
            r = aga.ad.responsive_search_ad
            r.path1, r.path2 = spec["path1"], spec["path2"]
            for h in spec["headlines"]:
                a = c.get_type("AdTextAsset")
                a.text = h["text"]
                if h["pinned_field"]:
                    a.pinned_field = c.enums.ServedAssetFieldTypeEnum[h["pinned_field"]]
                r.headlines.append(a)
            for d in spec["descriptions"]:
                a = c.get_type("AdTextAsset")
                a.text = d["text"]
                r.descriptions.append(a)
        elif o["resource"] == "asset":
            a = op.asset_operation.create
            a.resource_name = f"customers/{CID}/assets/-1"
            a.callout_asset.callout_text = o["callout_text"]
        elif o["resource"] == "campaign_asset":
            ca = op.campaign_asset_operation.create
            ca.campaign = f"customers/{CID}/campaigns/{o['campaign_id']}"
            ca.asset = f"customers/{CID}/assets/-1"
            ca.field_type = c.enums.AssetFieldTypeEnum.CALLOUT
            ca.status = c.enums.AssetLinkStatusEnum.PAUSED
        ops.append(op)
    return ops


for plan_id, builder in (("APG-1005-KWNEG", kwneg_ops), ("APG-1005-ADS", ads_ops)):
    plan = load_yaml(str(PL / f"{plan_id}.yaml"))
    fp = approval_code(plan)
    assert fp == FP[plan_id]["fingerprint"], f"{plan_id}: plan changed since fingerprinting"
    try:
        ops = builder(plan)
        resp = send(ops, validate_only=True)
        out[plan_id] = {"fingerprint": fp, "operations": len(ops), "validate_only": "ACCEPTED",
                        "results_returned": len(resp.mutate_operation_responses)}
    except Exception as exc:  # noqa: BLE001
        failure = getattr(exc, "failure", None)
        if failure is not None:
            detail = [{"code": str(e.error_code).strip(), "message": e.message,
                       "op_index": [f.index for f in e.location.field_path_elements if f.field_name == "mutate_operations"][:1],
                       "field": ".".join(f.field_name for f in e.location.field_path_elements)} for e in failure.errors]
        else:
            detail = f"{type(exc).__name__}: {str(exc)[:600]}"
        out[plan_id] = {"fingerprint": fp, "operations": len(plan["objects"]), "validate_only": "REJECTED", "detail": detail}
    print(plan_id, json.dumps(out[plan_id], indent=1)[:1800])
(ROOT / "clients/apogee-lawns/audits/2026-10-05-conversion-plan/validate-only-results.json").write_text(json.dumps(out, indent=1))
