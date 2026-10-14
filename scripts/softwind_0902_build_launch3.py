#!/usr/bin/env python3
"""Build PLAN-GA-LAUNCH-3B (legacy guard, fingerprinted) and PLAN-GA-LAUNCH-3A
(enablement, drafted but NOT fingerprinted because a pause mutation is required first).

validate_only only. Nothing is executed.
"""
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

GUARD_KW = [("202870585910", "384030528226", "house washing company near me", "PHRASE"),
            ("202870585910", "502487923397", "house washing company near me", "EXACT")]
GUARD_ADS = [("202870586310", "819975939528"), ("202870586310", "819975939531")]

errors = []


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    cid = normalize_customer_id(CID)
    agc = client.get_service("AdGroupCriterionService")
    ada = client.get_service("AdGroupAdService")

    # ---- guard the conflict set matches the fresh read exactly ----
    live_conf = R["legacy_activation_conflicts"]
    if len(live_conf) != 4:
        errors.append(f"expected 4 conflicts, fresh read shows {len(live_conf)}")
    kw_ids = {c.get("criterion_id") for c in live_conf if "criterion_id" in c}
    ad_ids = {c.get("ad_id") for c in live_conf if "ad_id" in c}
    if kw_ids != {g[1] for g in GUARD_KW}:
        errors.append("keyword conflict set drift")
    if ad_ids != {g[1] for g in GUARD_ADS}:
        errors.append("ad conflict set drift")

    # ---------------- 3B operations: 4 pauses ----------------
    kw_ops = []
    for agid, crit, text, mt in GUARD_KW:
        op = client.get_type("AdGroupCriterionOperation")
        op.update.resource_name = agc.ad_group_criterion_path(cid, agid, crit)
        op.update.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        kw_ops.append(op)
    ad_ops = []
    for agid, adid in GUARD_ADS:
        op = client.get_type("AdGroupAdOperation")
        op.update.resource_name = ada.ad_group_ad_path(cid, agid, adid)
        op.update.status = client.enums.AdGroupAdStatusEnum.PAUSED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ad_ops.append(op)

    vo = {}
    for label, svc, reqt, ops, meth in (
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
            vo[label] = f"PASS - {len(ops)} pause operations validated, 0 applied"
        except Exception as exc:
            vo[label] = f"FAIL - {str(exc)[:500]}"
            errors.append(f"validate_only failed for {label}")
    print("VALIDATE_ONLY 3B:", json.dumps(vo, indent=2))

    canonical3b = {
        "plan_id": "PLAN-GA-LAUNCH-3B",
        "target": {"exact_child_account_name": "Softwind Power Washing - Live",
                   "child_customer_id": CID, "exact_service": "Power Washing",
                   "manager_customer_id": "3373711342", "campaign_id": SURVIVOR},
        "actions": sorted(
            [{"type": "ad_group_criterion", "ad_group_id": a, "resource_id": c,
              "keyword_text": t, "match_type": m, "current": "ENABLED",
              "proposed": "PAUSED", "field_mask": "status"} for a, c, t, m in GUARD_KW]
            + [{"type": "ad_group_ad", "ad_group_id": a, "resource_id": i,
                "current": "ENABLED", "proposed": "PAUSED", "field_mask": "status"}
               for a, i in GUARD_ADS],
            key=lambda x: (x["type"], x["resource_id"])),
        "mutation_count": 4,
    }
    f1 = approval_code(canonical3b)
    f2 = approval_code(json.loads(json.dumps(canonical3b)))
    f3 = approval_code(canonical3b)
    if not f1 == f2 == f3:
        errors.append("3B fingerprint unstable")

    # ---------------- 3A enable set (NOT fingerprinted) ----------------
    e = R["enable_set"]
    enable_actions = (
        [{"type": "ad_group", "resource_id": x["ad_group_id"], "name": x["name"],
          "final_group": x["final_group"], "current": "PAUSED", "proposed": "ENABLED"}
         for x in e["ad_groups"]]
        + [{"type": "ad_group_criterion", "ad_group_id": x["ad_group_id"],
            "resource_id": x["criterion_id"], "keyword_text": x["text"],
            "match_type": x["match_type"], "current": x["status"], "proposed": "ENABLED",
            "policy": x["approval"]} for x in e["keywords"]]
        + [{"type": "ad_group_ad", "ad_group_id": x["ad_group_id"],
            "resource_id": x["ad_id"], "current": x["status"], "proposed": "ENABLED",
            "policy": x["policy_class"], "final_url": x["final_urls"][0]}
           for x in e["ads"]])
    counts3a = {"ad_groups": len(e["ad_groups"]), "keywords": len(e["keywords"]),
                "ads": len(e["ads"]), "total": len(enable_actions)}

    # validations for 3A
    urls_ok = all(v.get("status") == 200 and v.get("https") and not v.get("redirected")
                  and v.get("has_form") and v.get("has_phone_cta")
                  for v in R["final_urls"].values())
    checks3a = {
        "all six final URLs HTTPS 200, no redirect, form present, phone present": urls_ok,
        "no BROAD match keyword in the enable set": len(R["broad_match_present"]) == 0,
        "no DISAPPROVED RSA in the enable set":
            not any(x["policy_class"] == "DISAPPROVED" for x in e["ads"]),
        "every target belongs to campaign 24103511039":
            all(v["campaign"] == SURVIVOR for v in R["target_ad_groups"].values()),
        "campaign 24145053510 still ENABLED":
            R["campaigns"]["24145053510"]["status"] == "ENABLED",
        "both campaign ceilings still $30.00":
            all(v["ceiling_usd"] == 30.0 for v in R["campaigns"].values()),
        "both campaigns still MAXIMIZE CLICKS (TARGET_SPEND)":
            all(v["bidding"] == "TARGET_SPEND" for v in R["campaigns"].values()),
        "enable count recalculated from live account, not assumed":
            counts3a["total"] == 45,
        "zero legacy child resources would activate AFTER 3B":
            len(R["legacy_activation_conflicts"]) == 4,
    }
    now = datetime.now(ZoneInfo("America/New_York"))
    res = {
        "generated_account_local": now.isoformat(),
        "plan_3b": {
            "plan_id": "PLAN-GA-LAUNCH-3B", "action_count": 4, "object_count": 4,
            "mutation_count": 4, "validate_only": vo, "fingerprint": f1,
            "recompute_1": f2, "recompute_2": f3,
            "canonical_sha256_full": hashlib.sha256(
                json.dumps(canonical3b, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False).encode("utf-8")).hexdigest(),
            "approval_command": f"APPROVE PLAN-GA-LAUNCH-3B {f1} FOR {CID}",
            "actions": canonical3b["actions"]},
        "plan_3a": {
            "plan_id": "PLAN-GA-LAUNCH-3A", "counts": counts3a,
            "fingerprint": None,
            "fingerprint_withheld_because":
                "A new pause mutation is required first (PLAN-GA-LAUNCH-3B). Per the "
                "standing rule, stop and report the conflict before fingerprinting the "
                "enablement plan. It is also gated on the 12 new RSAs clearing review.",
            "checks": checks3a, "actions": enable_actions},
        "errors": errors, "all_pass": not errors and all(checks3a.values()),
    }
    (SNAP / f"launch3-build-{now.strftime('%Y-%m-%dT%H%M%S')}.json").write_text(
        json.dumps(res, indent=2, default=str), encoding="utf-8")
    (PLN / "2026-09-02-plan-ga-launch-3b-payload.json").write_text(
        json.dumps(canonical3b, indent=2), encoding="utf-8")
    (PLN / "2026-09-02-plan-ga-launch-3a-enable-actions.json").write_text(
        json.dumps({"plan_id": "PLAN-GA-LAUNCH-3A", "counts": counts3a,
                    "actions": enable_actions}, indent=2), encoding="utf-8")
    print(json.dumps({"3B": {k: v for k, v in res["plan_3b"].items() if k != "actions"},
                      "3A_counts": counts3a, "3A_checks": checks3a,
                      "errors": errors, "all_pass": res["all_pass"]},
                     indent=2, default=str))
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
