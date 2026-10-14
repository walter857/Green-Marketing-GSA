#!/usr/bin/env python3
"""Ambient | 2026-09-24 | EXECUTE the owner-approved launch-preparation plans.

Owner approval 2026-09-24 (this run): AMB-0924-NEG-THERMO-1 27A2CBA6A008,
AMB-0924-LP-PAUSE-2 1ACEA26A07EF, AMB-0924-LP-CREATE-2 05A8D71DBBAB.

Each plan's fingerprint is recomputed from disk and must equal the approved value. Every
stage is one atomic mutate (partial_failure=False). Everything CREATE-2 makes is PAUSED.
Created resource ids are written to receipts/ after every stage, so a partial failure
leaves an exact inventory.

    python ambient_0924_lp_execute.py --plan NEG|PAUSE|CREATE
"""
from __future__ import annotations
import sys, json, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, PLANS, RECEIPTS, CID
from gm_gsa.safety import approval_code
from google.protobuf import field_mask_pb2

APPROVED = {"NEG": ("AMB-0924-NEG-THERMO-1", "27A2CBA6A008", 20),
            "PAUSE": ("AMB-0924-LP-PAUSE-2", "1ACEA26A07EF", 30),
            "CREATE": ("AMB-0924-LP-CREATE-2", "05A8D71DBBAB", 58)}
EXISTING_SL = {"SL_HVACINST": "410638276380", "SL_HVACREPL": "410638278156",
               "SL_HVACREP": "410638280067", "SL_GASBOIL": "410465469923"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--plan", required=True, choices=APPROVED)
    args = ap.parse_args()
    name, fp_ok, n_ok = APPROVED[args.plan]
    plan = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8"))
    fp = plan.pop("fingerprint")
    if not (fp == approval_code(plan) == fp_ok and plan["operation_count"] == n_ok):
        sys.exit(f"ABORT {name}: fingerprint/op-count mismatch {fp} vs {fp_ok}")
    c = client(); identity_gate(c, verbose=False)
    rec = {"plan": name, "fingerprint": fp, "started_local": datetime.datetime.now(TZ).isoformat(),
           "committed": {}, "stages": []}
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    out = RECEIPTS / f"{name}-EXECUTED.json"

    def save():
        out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")

    def mutate(svc, method, req_type, ops, label):
        rq = c.get_type(req_type); rq.customer_id = CID; rq.operations.extend(ops)
        rq.partial_failure = False
        try:
            resp = getattr(c.get_service(svc), method)(request=rq)
        except Exception as ex:
            rec["ABORT"] = f"{label}: {str(ex)[:800]}"; save()
            sys.exit(f"ABORT at {label}; committed so far: {json.dumps(rec['committed'])[:600]}")
        names = [r.resource_name for r in resp.results]
        rec["stages"].append({"label": label, "ops": len(ops), "results": names}); save()
        print(f"  COMMITTED {label}: {len(names)}")
        return names

    fm = lambda *p: field_mask_pb2.FieldMask(paths=list(p))
    ops_all = plan["operations"]

    if args.plan == "NEG":
        ops = []
        for o_ in ops_all:
            if o_["op"] != "ADD_CAMPAIGN_NEGATIVE": continue
            o = c.get_type("CampaignCriterionOperation"); x = o.create
            x.campaign = c.get_service("CampaignService").campaign_path(CID, o_["campaign_id"])
            x.negative = True; x.keyword.text = o_["text"]
            x.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE; ops.append(o)
        rec["committed"]["campaign_negatives"] = mutate(
            "CampaignCriterionService", "mutate_campaign_criteria",
            "MutateCampaignCriteriaRequest", ops, "NEG-1 add campaign PHRASE negatives")
        ops = []
        for o_ in ops_all:
            if o_["op"] != "REMOVE_ACCOUNT_LEVEL_NEGATIVE": continue
            o = c.get_type("SharedCriterionOperation")
            o.remove = c.get_service("SharedCriterionService").shared_criterion_path(
                CID, o_["shared_set_id"], o_["criterion_id"]); ops.append(o)
        rec["committed"]["account_negatives_removed"] = mutate(
            "SharedCriterionService", "mutate_shared_criteria", "MutateSharedCriteriaRequest",
            ops, "NEG-2 remove account-level thermostat negatives")

    elif args.plan == "PAUSE":
        ops = []
        for o_ in ops_all:
            if o_["op"] != "PAUSE_AD_GROUP": continue
            o = c.get_type("AdGroupOperation")
            o.update.resource_name = c.get_service("AdGroupService").ad_group_path(CID, o_["ad_group_id"])
            o.update.status = c.enums.AdGroupStatusEnum.PAUSED; o.update_mask.CopyFrom(fm("status"))
            ops.append(o)
        rec["committed"]["ad_groups_paused"] = mutate(
            "AdGroupService", "mutate_ad_groups", "MutateAdGroupsRequest", ops, "PAUSE-1 ad groups")
        ops = []
        for o_ in ops_all:
            if o_["op"] != "PAUSE_CAMPAIGN_ASSET_LINK": continue
            o = c.get_type("CampaignAssetOperation")
            o.update.resource_name = c.get_service("CampaignAssetService").campaign_asset_path(
                CID, o_["campaign_id"], o_["asset_id"], "SITELINK")
            o.update.status = c.enums.AssetLinkStatusEnum.PAUSED; o.update_mask.CopyFrom(fm("status"))
            ops.append(o)
        rec["committed"]["sitelink_links_paused"] = mutate(
            "CampaignAssetService", "mutate_campaign_assets", "MutateCampaignAssetsRequest",
            ops, "PAUSE-2 sitelink links")

    else:  # CREATE
        sl_ops, keys = [], []
        for o_ in ops_all:
            if o_["op"] != "CREATE_SITELINK_ASSET": continue
            o = c.get_type("AssetOperation"); a = o.create
            a.final_urls.append(o_["final_url"])
            a.sitelink_asset.link_text = o_["link_text"]
            a.sitelink_asset.description1 = o_["description1"]
            a.sitelink_asset.description2 = o_["description2"]
            sl_ops.append(o); keys.append(o_["key"])
        names = mutate("AssetService", "mutate_assets", "MutateAssetsRequest", sl_ops,
                       "CREATE-1 sitelink assets")
        sl = dict(EXISTING_SL); sl.update({k: n.rsplit("/", 1)[-1] for k, n in zip(keys, names)})
        rec["committed"]["sitelink_assets"] = {k: sl[k] for k in keys}; save()
        ops = []
        for o_ in ops_all:
            if o_["op"] != "LINK_SITELINK_TO_CAMPAIGN_PAUSED": continue
            o = c.get_type("CampaignAssetOperation"); x = o.create
            x.campaign = c.get_service("CampaignService").campaign_path(CID, o_["campaign_id"])
            x.asset = c.get_service("AssetService").asset_path(CID, sl[o_["sitelink"]])
            x.field_type = c.enums.AssetFieldTypeEnum.SITELINK
            x.status = c.enums.AssetLinkStatusEnum.PAUSED; ops.append(o)
        rec["committed"]["sitelink_links_paused"] = mutate(
            "CampaignAssetService", "mutate_campaign_assets", "MutateCampaignAssetsRequest",
            ops, "CREATE-2 sitelink links PAUSED")
        rsa_meta, ops = [], []
        for o_ in ops_all:
            if o_["op"] != "CREATE_RSA_PAUSED": continue
            o = c.get_type("AdGroupAdOperation"); a = o.create
            a.ad_group = c.get_service("AdGroupService").ad_group_path(CID, o_["ad_group_id"])
            a.status = c.enums.AdGroupAdStatusEnum.PAUSED
            a.ad.final_urls.append(o_["final_url"])
            r = a.ad.responsive_search_ad
            for h in o_["headlines"]:
                t = c.get_type("AdTextAsset"); t.text = h["text"]
                if h["pin"] not in ("UNSPECIFIED", "UNKNOWN"):
                    t.pinned_field = getattr(c.enums.ServedAssetFieldTypeEnum, h["pin"])
                r.headlines.append(t)
            for d in o_["descriptions"]:
                t = c.get_type("AdTextAsset"); t.text = d["text"]
                if d["pin"] not in ("UNSPECIFIED", "UNKNOWN"):
                    t.pinned_field = getattr(c.enums.ServedAssetFieldTypeEnum, d["pin"])
                r.descriptions.append(t)
            if o_["path1"]: r.path1 = o_["path1"]
            if o_["path2"]: r.path2 = o_["path2"]
            ops.append(o)
            rsa_meta.append({"kind": o_["kind"], "ad_group_id": o_["ad_group_id"],
                             "ad_group": o_["ad_group"], "final_url": o_["final_url"],
                             "copy_of_ad_id": o_.get("copy_of_ad_id"), "label": o_.get("label")})
        names = mutate("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest", ops,
                       "CREATE-3 RSAs PAUSED")
        for m, n in zip(rsa_meta, names):
            m["ad_id"] = n.rsplit("~", 1)[-1]
        rec["committed"]["rsas"] = rsa_meta
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat(); save()
    print(f"{name} {fp}: EXECUTED -> {out}")


if __name__ == "__main__":
    main()
