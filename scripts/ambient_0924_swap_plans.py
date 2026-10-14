#!/usr/bin/env python3
"""Ambient | 2026-09-24 | Revised migration swap (replaces ENABLE-2B D787B42AA8E6, not executed).

Reason: the 12 offer-page copies are still REVIEW_IN_PROGRESS. Pausing all 12 old main-site
RSAs now would leave six live ad groups with no approved ad. The owner's instruction is to
pause superseded ads when their replacements are ready, so the swap is split:

  AMB-0924-LP-SWAP-1  per group: pause ONE old main-site RSA (the one with fewer impressions
                      in the last 30 days), enable BOTH copies -> 3 enabled RSAs per group
                      (the cap), one approved old ad keeps serving during review.
  AMB-0924-LP-SWAP-2  pause the remaining six old RSAs. Execute once the copies are APPROVED
                      / APPROVED_LIMITED.
"""
from __future__ import annotations
import sys, json, re, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, PLANS
from gm_gsa.safety import approval_code
from google.protobuf import field_mask_pb2

c = client(); identity_gate(c, verbose=False)
old = json.loads((PLANS / "AMB-0924-LP-ENABLE-2B.json").read_text(encoding="utf-8"))
olds = [o for o in old["operations"] if o["op"] == "PAUSE_OLD_RSA"]
copies = [o for o in old["operations"] if o["op"] == "ENABLE_RSA_COPY"]
impr = collections.Counter()
for r in q(c, """SELECT ad_group_ad.ad.id, metrics.impressions FROM ad_group_ad
                 WHERE segments.date DURING LAST_30_DAYS AND ad_group_ad.status = 'ENABLED'"""):
    impr[str(r.ad_group_ad.ad.id)] += r.metrics.impressions
by_group = collections.defaultdict(list)
for o in olds: by_group[o["ad_group_id"]].append(o)
first, second = [], []
for g, lst in by_group.items():
    lst.sort(key=lambda o: impr[o["ad_id"]])
    first.append({**lst[0], "impr_30d": impr[lst[0]["ad_id"]]})
    second += [{**x, "impr_30d": impr[x["ad_id"]]} for x in lst[1:]]
base = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342",
        "built_local": "2026-09-24", "authorized_by": "owner instruction 2026-09-24 (this run)",
        "supersedes": "AMB-0924-LP-ENABLE-2B D787B42AA8E6 (never executed)"}
S1 = {**base, "plan_name": "AMB-0924-LP-SWAP-1", "approval_class": "enable+pause (interim swap)",
      "operations": [{"op": "PAUSE_OLD_RSA", **{k: o[k] for k in ("ad_group_id", "ad_id", "impr_30d")}} for o in first]
      + copies, "order": "pause first (3-enabled-RSA cap)"}
S2 = {**base, "plan_name": "AMB-0924-LP-SWAP-2", "approval_class": "pause (complete swap)",
      "operations": [{"op": "PAUSE_OLD_RSA", **{k: o[k] for k in ("ad_group_id", "ad_id", "impr_30d")}} for o in second],
      "execute_when": "all 12 copies APPROVED or APPROVED_LIMITED"}
fm = field_mask_pb2.FieldMask(paths=["status"])


def ad_op(g, a, st):
    o = c.get_type("AdGroupAdOperation")
    o.update.resource_name = c.get_service("AdGroupAdService").ad_group_ad_path(CID, g, a)
    o.update.status = getattr(c.enums.AdGroupAdStatusEnum, st); o.update_mask.CopyFrom(fm); return o


for p in (S1, S2):
    ops = [ad_op(o["ad_group_id"], o["ad_id"], "PAUSED" if o["op"] == "PAUSE_OLD_RSA" else "ENABLED") for o in p["operations"]]
    rq = c.get_type("MutateAdGroupAdsRequest"); rq.customer_id = CID; rq.operations.extend(ops); rq.validate_only = True
    try:
        c.get_service("AdGroupAdService").mutate_ad_group_ads(request=rq); p["preflight"] = f"VALIDATED {len(ops)}"
    except Exception as ex:
        p["preflight"] = "FAILED " + str(re.findall(r'message: "([^"]+)"', str(ex))[:2])
    p["operation_count"] = len(p["operations"])
    p["fingerprint"] = approval_code({k: v for k, v in p.items() if k != "fingerprint"})
    (PLANS / f"{p['plan_name']}.json").write_text(json.dumps(p, indent=1), encoding="utf-8")
    print(f"PLAN {p['plan_name']}: {p['fingerprint']} / {p['operation_count']} ops / {p['preflight']}")
print("paused first (lower 30d impressions):", [(o["ad_group_id"], o["ad_id"], o["impr_30d"]) for o in first])
