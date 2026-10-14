#!/usr/bin/env python3
"""Ambient | 2026-09-15 | validate_only=True dry run of AMB-0915-COMM-RSA-1.

validate_only still consumes the daily mutate operation budget, so this runs once,
for 2 operations only. Nothing is committed.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-15"
COMM_AG = "199748801029"
PLAN = PLANS / "AMB-0915-COMM-RSA-1.json"

c = client(); identity_gate(c, verbose=False)
plan = json.loads(PLAN.read_text(encoding="utf-8"))
claimed = plan.pop("fingerprint")
recomputed = approval_code(plan)
plan["fingerprint"] = claimed
print(f"fingerprint claimed={claimed} recomputed={recomputed} "
      f"MATCH={claimed == recomputed}")
assert claimed == recomputed, "FINGERPRINT MISMATCH - plan on disk was edited"

svc = c.get_service("AdGroupAdService")
ad_group_rn = c.get_service("AdGroupService").ad_group_path(CID, COMM_AG)
ops = []
for op in plan["operations"]:
    o = c.get_type("AdGroupAdOperation")
    a = o.create
    a.ad_group = ad_group_rn
    a.status = c.enums.AdGroupAdStatusEnum.PAUSED
    a.ad.final_urls.append(op["final_url"])
    rsa = a.ad.responsive_search_ad
    rsa.path1, rsa.path2 = op["path1"], op["path2"]
    for h in op["headlines_pinned_headline_1"]:
        t = c.get_type("AdTextAsset")
        t.text = h
        t.pinned_field = c.enums.ServedAssetFieldTypeEnum.HEADLINE_1
        rsa.headlines.append(t)
    for h in op["headlines_unpinned"]:
        t = c.get_type("AdTextAsset")
        t.text = h
        rsa.headlines.append(t)
    for d in op["descriptions"]:
        t = c.get_type("AdTextAsset")
        t.text = d
        rsa.descriptions.append(t)
    ops.append(o)

print(f"\nbuilt {len(ops)} AdGroupAdOperation(s), all status=PAUSED, "
      f"ad_group={ad_group_rn}")
assert len(ops) == plan["operation_count"] == 2

res = {"plan": plan["plan_name"], "fingerprint": claimed, "operations": len(ops),
       "validate_only": True, "when": datetime.datetime.now(TZ).isoformat()}
try:
    req = c.get_type("MutateAdGroupAdsRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    req.partial_failure = False
    req.validate_only = True
    resp = svc.mutate_ad_group_ads(request=req)
    res["status"] = "VALIDATED_OK"
    res["results"] = len(resp.results)
    print(f"\nVALIDATED_OK - Google accepted all {len(ops)} operations. Nothing was created.")
except Exception as ex:
    res["status"] = "VALIDATION_FAILED"
    res["error"] = str(ex)[:4000]
    print("\nVALIDATION FAILED:")
    print(str(ex)[:4000])

VRECEIPTS.mkdir(parents=True, exist_ok=True)
p = VRECEIPTS / f"AMB-0915-COMM-RSA-1-{STAMP}.json"
p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
