#!/usr/bin/env python3
"""Ambient | 2026-09-24 | Build + validate_only the ENABLE plans from the CREATE-2 receipt.

Owner authorized enablement in this run (2026-09-24) after clean create-paused readback
(107/0 FAIL). Two plans, so the migration swap can wait for Google's review of the copies:

  AMB-0924-LP-ENABLE-2A  launch: 9 reused ad groups, their approved keyword set, their 18 new
                         RSAs, campaign 24268690041 (Thermostat Services, $15/day), and the
                         18 new offer-page sitelink links.
  AMB-0924-LP-ENABLE-2B  migration swap for 6 live ad groups: PAUSE the 12 old main-site RSAs
                         first, then ENABLE their 12 offer-page copies (3-enabled-RSA cap).
"""
from __future__ import annotations
import sys, json, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, PLANS, RECEIPTS
from gm_gsa.safety import approval_code
from google.protobuf import field_mask_pb2

c = client(); identity_gate(c, verbose=False)
cr = json.loads((RECEIPTS / "AMB-0924-LP-CREATE-2-EXECUTED.json").read_text(encoding="utf-8"))
draft = json.loads((PLANS / "AMB-0924-LP-ENABLE-2.DRAFT.json").read_text(encoding="utf-8"))
cp = json.loads((PLANS / "AMB-0924-LP-CREATE-2.json").read_text(encoding="utf-8"))
LAUNCH = [g["id"] for g in draft["ad_groups_to_enable"]]
rsas = cr["committed"]["rsas"]
new_launch = [m for m in rsas if m["kind"] == "launch"]
new_copies = [m for m in rsas if m["kind"] == "migration_copy"]

# fresh state
ag = {str(r.ad_group.id): (r.ad_group.name, E(r.ad_group.status), str(r.campaign.id)) for r in q(c,
      "SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id FROM ad_group WHERE campaign.status != 'REMOVED'")}
ads = {str(r.ad_group_ad.ad.id): (E(r.ad_group_ad.status), str(r.ad_group.id), E(r.ad_group_ad.policy_summary.approval_status),
       E(r.ad_group_ad.policy_summary.review_status)) for r in q(c,
       "SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group.id, ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'")}
kw = {(str(r.ad_group.id), str(r.ad_group_criterion.criterion_id)): (r.ad_group_criterion.keyword.text, E(r.ad_group_criterion.keyword.match_type), E(r.ad_group_criterion.status), r.ad_group_criterion.negative)
      for r in q(c, "SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.status, ad_group_criterion.negative FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED' AND campaign.status != 'REMOVED'")}
camp = {str(r.campaign.id): E(r.campaign.status) for r in q(c, "SELECT campaign.id, campaign.status FROM campaign WHERE campaign.id = 24268690041")}
errs = []
# children of paused launch groups: nothing ENABLED except negatives
for g in LAUNCH:
    for (gid, cid), (t, mt, st, neg) in kw.items():
        if gid == g and not neg and st == "ENABLED":
            errs.append(f"{ag[g][0]}: positive keyword [{t}] already ENABLED")
    for aid, (st, gid, ap, rv) in ads.items():
        if gid == g and st == "ENABLED":
            errs.append(f"{ag[g][0]}: ad {aid} already ENABLED")
    if ag[g][1] != "PAUSED": errs.append(f"{g} not PAUSED")
kw_enable = [(k["ad_group_id"], k["criterion_id"]) for k in draft["keywords_to_enable"]]
for key in kw_enable:
    if key not in kw or kw[key][2] != "PAUSED": errs.append(f"keyword {key} not PAUSED/present")
old_ads = [(a["ad_group_id"], a["ad_id"]) for a in draft["old_ads_to_pause"]]
for gid, aid in old_ads:
    if ads.get(aid, ("",))[0] != "ENABLED": errs.append(f"old ad {aid} not ENABLED")
links = [o for o in cp["operations"] if o["op"] == "LINK_SITELINK_TO_CAMPAIGN_PAUSED"]
allsl = {"SL_HVACINST": "410638276380", "SL_HVACREPL": "410638278156", "SL_HVACREP": "410638280067",
         "SL_GASBOIL": "410465469923", **cr["committed"]["sitelink_assets"]}

A = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342",
     "built_local": "2026-09-24", "plan_name": "AMB-0924-LP-ENABLE-2A", "approval_class": "enable",
     "authorized_by": "owner instruction 2026-09-24 (this run), after CREATE-2 readback 107/0 FAIL",
     "operations": (
        [{"op": "ENABLE_RSA", "ad_group_id": m["ad_group_id"], "ad_id": m["ad_id"]} for m in new_launch]
        + [{"op": "ENABLE_KEYWORD", "ad_group_id": g, "criterion_id": k, "text": kw[(g, k)][0], "match": kw[(g, k)][1]} for g, k in kw_enable]
        + [{"op": "ENABLE_AD_GROUP", "ad_group_id": g, "name": ag[g][0]} for g in LAUNCH]
        + [{"op": "ENABLE_SITELINK_LINK", "campaign_id": o["campaign_id"], "asset_id": allsl[o["sitelink"]], "sitelink": o["sitelink"]} for o in links]
        + [{"op": "ENABLE_CAMPAIGN", "campaign_id": "24268690041", "name": "Thermostat Services", "budget": 15.00}]),
     "order": "RSAs and keywords first, then ad groups, then sitelink links, campaign last",
     "budget_effect": "enabled heating budget $290.00 -> $305.00/day (cap $325.00)"}
B = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342",
     "built_local": "2026-09-24", "plan_name": "AMB-0924-LP-ENABLE-2B", "approval_class": "enable+pause (swap)",
     "authorized_by": A["authorized_by"],
     "operations": ([{"op": "PAUSE_OLD_RSA", "ad_group_id": g, "ad_id": a} for g, a in old_ads]
                    + [{"op": "ENABLE_RSA_COPY", "ad_group_id": m["ad_group_id"], "ad_id": m["ad_id"], "final_url": m["final_url"]} for m in new_copies]),
     "execute_when": "copies are APPROVED or APPROVED_LIMITED (replacement ready)",
     "order": "pause old first (3-enabled-RSA cap)"}
for p in (A, B): p["operation_count"] = len(p["operations"])

fm = lambda: field_mask_pb2.FieldMask(paths=["status"])
def ad_op(g, a, status):
    o = c.get_type("AdGroupAdOperation")
    o.update.resource_name = c.get_service("AdGroupAdService").ad_group_ad_path(CID, g, a)
    o.update.status = getattr(c.enums.AdGroupAdStatusEnum, status); o.update_mask.CopyFrom(fm()); return o
def vo(svc, meth, req, ops, label, pf):
    rq = c.get_type(req); rq.customer_id = CID; rq.operations.extend(ops); rq.validate_only = True
    try:
        getattr(c.get_service(svc), meth)(request=rq); pf[label] = f"VALIDATED {len(ops)}"
    except Exception as ex:
        pf[label] = "FAILED " + str(re.findall(r'message: "([^"]+)"', str(ex))[:3]); errs.append(f"{label}: {pf[label]}")
pfA, pfB = {}, {}
vo("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest",
   [ad_op(o["ad_group_id"], o["ad_id"], "ENABLED") for o in A["operations"] if o["op"] == "ENABLE_RSA"], "RSAs", pfA)
ops = []
for o_ in A["operations"]:
    if o_["op"] != "ENABLE_KEYWORD": continue
    o = c.get_type("AdGroupCriterionOperation")
    o.update.resource_name = c.get_service("AdGroupCriterionService").ad_group_criterion_path(CID, o_["ad_group_id"], o_["criterion_id"])
    o.update.status = c.enums.AdGroupCriterionStatusEnum.ENABLED; o.update_mask.CopyFrom(fm()); ops.append(o)
vo("AdGroupCriterionService", "mutate_ad_group_criteria", "MutateAdGroupCriteriaRequest", ops, "keywords", pfA)
ops = []
for o_ in A["operations"]:
    if o_["op"] != "ENABLE_AD_GROUP": continue
    o = c.get_type("AdGroupOperation"); o.update.resource_name = c.get_service("AdGroupService").ad_group_path(CID, o_["ad_group_id"])
    o.update.status = c.enums.AdGroupStatusEnum.ENABLED; o.update_mask.CopyFrom(fm()); ops.append(o)
vo("AdGroupService", "mutate_ad_groups", "MutateAdGroupsRequest", ops, "ad groups", pfA)
ops = []
for o_ in A["operations"]:
    if o_["op"] != "ENABLE_SITELINK_LINK": continue
    o = c.get_type("CampaignAssetOperation")
    o.update.resource_name = c.get_service("CampaignAssetService").campaign_asset_path(CID, o_["campaign_id"], o_["asset_id"], "SITELINK")
    o.update.status = c.enums.AssetLinkStatusEnum.ENABLED; o.update_mask.CopyFrom(fm()); ops.append(o)
vo("CampaignAssetService", "mutate_campaign_assets", "MutateCampaignAssetsRequest", ops, "sitelink links", pfA)
o = c.get_type("CampaignOperation"); o.update.resource_name = c.get_service("CampaignService").campaign_path(CID, "24268690041")
o.update.status = c.enums.CampaignStatusEnum.ENABLED; o.update_mask.CopyFrom(fm())
vo("CampaignService", "mutate_campaigns", "MutateCampaignsRequest", [o], "campaign", pfA)
vo("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest",
   [ad_op(o["ad_group_id"], o["ad_id"], "PAUSED") for o in B["operations"] if o["op"] == "PAUSE_OLD_RSA"]
   + [ad_op(o["ad_group_id"], o["ad_id"], "ENABLED") for o in B["operations"] if o["op"] == "ENABLE_RSA_COPY"], "swap", pfB)
A["preflight"], B["preflight"] = pfA, pfB
for p in (A, B):
    p["fingerprint"] = approval_code({k: v for k, v in p.items() if k != "fingerprint"})
    (PLANS / f"{p['plan_name']}.json").write_text(json.dumps(p, indent=1), encoding="utf-8")
    print(f"PLAN {p['plan_name']}: {p['fingerprint']} / {p['operation_count']} ops / {p['preflight']}")
copy_review = {}
for m in new_copies + new_launch:
    st = ads.get(m["ad_id"], ("?", "", "?", "?"))
    copy_review[(m["kind"], st[2], st[3])] = copy_review.get((m["kind"], st[2], st[3]), 0) + 1
print("review now:", copy_review)
print("ERRORS:", errs or "none")
