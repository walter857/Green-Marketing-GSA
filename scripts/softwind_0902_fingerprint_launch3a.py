#!/usr/bin/env python3
"""Fingerprint PLAN-GA-LAUNCH-3A now that both gates have cleared. validate_only only."""
from __future__ import annotations

import glob
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from google.protobuf.field_mask_pb2 import FieldMask  # noqa: E402

CID, SURVIVOR = "1521725229", "24103511039"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
PLN = ROOT / "clients/softwind-power-washing/plans"

R = json.loads(Path(sorted(glob.glob(str(SNAP / "launch3a-read-*.json")))[-1])
               .read_text(encoding="utf-8"))
E = R["enable_set"]
errors = []


def main() -> int:
    # ---- gates ----
    gates = {
        "GATE-1 no legacy activation conflicts remain":
            len(R["legacy_activation_conflicts"]) == 0,
        "GATE-2 all 12 new RSAs APPROVED AND ELIGIBLE, none DISAPPROVED":
            all(a["policy_class"] == "APPROVED AND ELIGIBLE"
                for rows in R["ad_children"].values() for a in rows
                if a["created_by_launch1"]),
        "all six Final URLs HTTPS 200, no redirect, form + phone present":
            all(v.get("status") == 200 and v.get("https") and not v.get("redirected")
                and v.get("has_form") and v.get("has_phone_cta")
                for v in R["final_urls"].values()),
        "no BROAD match keyword": len(R["broad_match_present"]) == 0,
        "every target in campaign 24103511039":
            all(v["campaign"] == SURVIVOR for v in R["target_ad_groups"].values()),
        "campaign 24145053510 still ENABLED":
            R["campaigns"]["24145053510"]["status"] == "ENABLED",
        "both ceilings still $30.00":
            all(v["ceiling_usd"] == 30.0 for v in R["campaigns"].values()),
        "both campaigns MAXIMIZE CLICKS":
            all(v["bidding"] == "TARGET_SPEND" for v in R["campaigns"].values()),
        "enable count is 45, recalculated live":
            len(E["ad_groups"]) + len(E["keywords"]) + len(E["ads"]) == 45,
    }
    for k, v in gates.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
        if not v:
            errors.append(k)
    if errors:
        print("\nGATES NOT MET:", errors)
        return 2

    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    cid = normalize_customer_id(CID)
    ags = client.get_service("AdGroupService")
    agc = client.get_service("AdGroupCriterionService")
    ada = client.get_service("AdGroupAdService")

    ag_ops, kw_ops, ad_ops = [], [], []
    for x in E["ad_groups"]:
        op = client.get_type("AdGroupOperation")
        op.update.resource_name = ags.ad_group_path(cid, x["ad_group_id"])
        op.update.status = client.enums.AdGroupStatusEnum.ENABLED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ag_ops.append(op)
    for x in E["keywords"]:
        op = client.get_type("AdGroupCriterionOperation")
        op.update.resource_name = agc.ad_group_criterion_path(
            cid, x["ad_group_id"], x["criterion_id"])
        op.update.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        kw_ops.append(op)
    for x in E["ads"]:
        op = client.get_type("AdGroupAdOperation")
        op.update.resource_name = ada.ad_group_ad_path(cid, x["ad_group_id"], x["ad_id"])
        op.update.status = client.enums.AdGroupAdStatusEnum.ENABLED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ad_ops.append(op)

    vo = {}
    for label, svc, reqt, ops, meth in (
            ("ad_groups", ags, "MutateAdGroupsRequest", ag_ops, "mutate_ad_groups"),
            ("keywords", agc, "MutateAdGroupCriteriaRequest", kw_ops,
             "mutate_ad_group_criteria"),
            ("ads", ada, "MutateAdGroupAdsRequest", ad_ops, "mutate_ad_group_ads")):
        req = client.get_type(reqt)
        req.customer_id = cid
        req.operations.extend(ops)
        req.validate_only = True
        req.partial_failure = False
        try:
            getattr(svc, meth)(request=req)
            vo[label] = f"PASS - {len(ops)} enable operations validated, 0 applied"
        except Exception as exc:
            vo[label] = f"FAIL - {str(exc)[:500]}"
            errors.append(f"validate_only {label}")
    print("\nVALIDATE_ONLY:", json.dumps(vo, indent=2))

    canonical = {
        "plan_id": "PLAN-GA-LAUNCH-3A",
        "target": {"exact_child_account_name": "Softwind Power Washing - Live",
                   "child_customer_id": CID, "exact_service": "Power Washing",
                   "manager_customer_id": "3373711342", "campaign_id": SURVIVOR},
        "actions": sorted(
            [{"type": "ad_group", "resource_id": x["ad_group_id"],
              "final_group": x["final_group"], "current": "PAUSED", "proposed": "ENABLED",
              "field_mask": "status"} for x in E["ad_groups"]]
            + [{"type": "ad_group_criterion", "ad_group_id": x["ad_group_id"],
                "resource_id": x["criterion_id"], "keyword_text": x["text"],
                "match_type": x["match_type"], "current": "PAUSED", "proposed": "ENABLED",
                "field_mask": "status"} for x in E["keywords"]]
            + [{"type": "ad_group_ad", "ad_group_id": x["ad_group_id"],
                "resource_id": x["ad_id"], "current": "PAUSED", "proposed": "ENABLED",
                "field_mask": "status"} for x in E["ads"]],
            key=lambda x: (x["type"], x["resource_id"])),
        "mutation_count": 45,
    }
    f1 = approval_code(canonical)
    f2 = approval_code(json.loads(json.dumps(canonical)))
    f3 = approval_code(canonical)
    if not f1 == f2 == f3:
        errors.append("fingerprint unstable")

    now = datetime.now(ZoneInfo("America/New_York"))
    res = {"plan_id": "PLAN-GA-LAUNCH-3A", "generated_account_local": now.isoformat(),
           "gates": gates, "validate_only": vo,
           "counts": {"ad_groups": len(ag_ops), "keywords": len(kw_ops), "ads": len(ad_ops),
                      "action_count": 45, "object_count": 45, "mutation_count": 45},
           "fingerprint": f1, "recompute_1": f2, "recompute_2": f3,
           "canonical_sha256_full": hashlib.sha256(
               json.dumps(canonical, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False).encode("utf-8")).hexdigest(),
           "approval_status": "NOT APPROVED", "execution_status": "DO NOT EXECUTE",
           "approval_command": f"APPROVE PLAN-GA-LAUNCH-3A {f1} FOR {CID}",
           "errors": errors, "all_pass": not errors}
    (SNAP / f"launch3a-fingerprint-{now.strftime('%Y-%m-%dT%H%M%S')}.json").write_text(
        json.dumps(res, indent=2, default=str), encoding="utf-8")
    (PLN / "2026-09-02-plan-ga-launch-3a-payload.json").write_text(
        json.dumps(canonical, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "gates"}, indent=2, default=str))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
