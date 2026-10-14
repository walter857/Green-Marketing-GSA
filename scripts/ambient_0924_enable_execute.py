#!/usr/bin/env python3
"""Ambient | 2026-09-24 | EXECUTE AMB-0924-LP-ENABLE-2A / -2B (owner-authorized this run).

Fingerprint recomputed from disk before any write. Stages are atomic. 2B pauses old RSAs
before enabling copies (3-enabled-RSA cap) inside ONE atomic mutate, ordered.

    python ambient_0924_enable_execute.py --plan A|B --fp <fingerprint>
"""
from __future__ import annotations
import sys, json, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, identity_gate, TZ, PLANS, RECEIPTS, CID
from gm_gsa.safety import approval_code
from google.protobuf import field_mask_pb2

ap = argparse.ArgumentParser(); ap.add_argument("--plan", choices=["A", "B"], required=True)
ap.add_argument("--fp", required=True); args = ap.parse_args()
name = f"AMB-0924-LP-ENABLE-2{args.plan}"
plan = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8"))
fp = plan.pop("fingerprint")
if not (fp == approval_code(plan) == args.fp):
    sys.exit(f"ABORT {name}: fingerprint mismatch disk={fp} expected={args.fp}")
c = client(); identity_gate(c, verbose=False)
rec = {"plan": name, "fingerprint": fp, "started_local": datetime.datetime.now(TZ).isoformat(), "stages": []}
out = RECEIPTS / f"{name}-EXECUTED.json"
fm = lambda: field_mask_pb2.FieldMask(paths=["status"])


def save(): out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")


def mutate(svc, meth, req, ops, label):
    if not ops: return
    rq = c.get_type(req); rq.customer_id = CID; rq.operations.extend(ops); rq.partial_failure = False
    try:
        resp = getattr(c.get_service(svc), meth)(request=rq)
    except Exception as ex:
        rec["ABORT"] = f"{label}: {str(ex)[:800]}"; save(); sys.exit(f"ABORT at {label}")
    rec["stages"].append({"label": label, "n": len(resp.results)}); save()
    print(f"  COMMITTED {label}: {len(resp.results)}")


def ad_op(g, a, st):
    o = c.get_type("AdGroupAdOperation")
    o.update.resource_name = c.get_service("AdGroupAdService").ad_group_ad_path(CID, g, a)
    o.update.status = getattr(c.enums.AdGroupAdStatusEnum, st); o.update_mask.CopyFrom(fm()); return o


ops_all = plan["operations"]
if args.plan == "A":
    mutate("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest",
           [ad_op(o["ad_group_id"], o["ad_id"], "ENABLED") for o in ops_all if o["op"] == "ENABLE_RSA"], "A1 RSAs")
    ops = []
    for o_ in ops_all:
        if o_["op"] != "ENABLE_KEYWORD": continue
        o = c.get_type("AdGroupCriterionOperation")
        o.update.resource_name = c.get_service("AdGroupCriterionService").ad_group_criterion_path(CID, o_["ad_group_id"], o_["criterion_id"])
        o.update.status = c.enums.AdGroupCriterionStatusEnum.ENABLED; o.update_mask.CopyFrom(fm()); ops.append(o)
    mutate("AdGroupCriterionService", "mutate_ad_group_criteria", "MutateAdGroupCriteriaRequest", ops, "A2 keywords")
    ops = []
    for o_ in ops_all:
        if o_["op"] != "ENABLE_AD_GROUP": continue
        o = c.get_type("AdGroupOperation"); o.update.resource_name = c.get_service("AdGroupService").ad_group_path(CID, o_["ad_group_id"])
        o.update.status = c.enums.AdGroupStatusEnum.ENABLED; o.update_mask.CopyFrom(fm()); ops.append(o)
    mutate("AdGroupService", "mutate_ad_groups", "MutateAdGroupsRequest", ops, "A3 ad groups")
    ops = []
    for o_ in ops_all:
        if o_["op"] != "ENABLE_SITELINK_LINK": continue
        o = c.get_type("CampaignAssetOperation")
        o.update.resource_name = c.get_service("CampaignAssetService").campaign_asset_path(CID, o_["campaign_id"], o_["asset_id"], "SITELINK")
        o.update.status = c.enums.AssetLinkStatusEnum.ENABLED; o.update_mask.CopyFrom(fm()); ops.append(o)
    mutate("CampaignAssetService", "mutate_campaign_assets", "MutateCampaignAssetsRequest", ops, "A4 sitelink links")
    o = c.get_type("CampaignOperation"); o.update.resource_name = c.get_service("CampaignService").campaign_path(CID, "24268690041")
    o.update.status = c.enums.CampaignStatusEnum.ENABLED; o.update_mask.CopyFrom(fm())
    mutate("CampaignService", "mutate_campaigns", "MutateCampaignsRequest", [o], "A5 Thermostat Services campaign")
else:
    mutate("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest",
           [ad_op(o["ad_group_id"], o["ad_id"], "PAUSED") for o in ops_all if o["op"] == "PAUSE_OLD_RSA"]
           + [ad_op(o["ad_group_id"], o["ad_id"], "ENABLED") for o in ops_all if o["op"] == "ENABLE_RSA_COPY"],
           "B1 pause old main-site RSAs then enable offer copies")
rec["finished_local"] = datetime.datetime.now(TZ).isoformat(); save()
print(f"{name} {fp}: EXECUTED -> {out}")
