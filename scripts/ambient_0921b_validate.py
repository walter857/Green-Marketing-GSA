#!/usr/bin/env python3
"""Ambient | 2026-09-21b | validate_only for the four transition plans. Nothing is created.

Every mutate carries validate_only = True. EXTERNAL WRITES: 0.
Note: validate_only consumes the same daily mutate quota as a real write.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-21b"
TOPIC = re.compile(r'topic: "([A-Z_]+)"')
FP = {"AMB-0921B-HEAT-BUILD-1": "08F6BD427AFD",
      "AMB-0921B-BUDGET-1": "55D77907F8FF",
      "AMB-0921B-BID-1": "B30C02B776CD",
      "AMB-0921B-COOLPAUSE-1": "38471B0B0971"}
# Unattached budgets (reference_count = 0) used only as validate_only stand-ins so each
# probe campaign gets its own budget. Google rejects two campaigns sharing one
# non-shared budget, which is a harness artefact, not a plan defect. In execution each
# new campaign receives the budget created for it in stage 1.
FREE_BUDGETS = ["15044731597", "15466378777", "13433692985", "14810347898"]

c = client()
identity_gate(c, verbose=False)
res = {"when": datetime.datetime.now(TZ).isoformat(), "validate_only": True,
       "external_writes": 0, "checks": {}}


def load(name):
    p = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8"))
    fp = p.pop("fingerprint"); re_fp = approval_code(p); p["fingerprint"] = fp
    ok = fp == re_fp == FP[name]
    print(f"{name}: disk={fp} recomputed={re_fp} expected={FP[name]} MATCH={ok} "
          f"ops={p['operation_count']}")
    assert ok, f"FINGERPRINT MISMATCH {name}"
    return p


build = load("AMB-0921B-HEAT-BUILD-1")
budget = load("AMB-0921B-BUDGET-1")
bid = load("AMB-0921B-BID-1")
cool = load("AMB-0921B-COOLPAUSE-1")

AG = build["ad_groups"]
CAMPAIGNS = build["campaigns"]
NEWC = [k for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]]

# ------------------------------------------------------------- 1. new budgets
print("\n=== 1. NEW CAMPAIGN BUDGETS ===")
ops = []
for k in NEWC:
    o = c.get_type("CampaignBudgetOperation"); b = o.create
    b.name = f"Budget | {CAMPAIGNS[k]['name']}"
    b.amount_micros = int(round(CAMPAIGNS[k]["daily_budget"] * 1e6))
    b.explicitly_shared = False
    b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
    ops.append(o)
r = c.get_type("MutateCampaignBudgetsRequest")
r.customer_id = CID; r.operations.extend(ops); r.validate_only = True
try:
    c.get_service("CampaignBudgetService").mutate_campaign_budgets(request=r)
    print(f"  VALIDATED_OK - {len(ops)} budgets"); res["checks"]["new_budgets"] = "OK"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["new_budgets"] = f"FAILED {str(e)[:250]}"

# ----------------------------------------------------------- 2. new campaigns
print("\n=== 2. NEW CAMPAIGNS, PAUSED ===")
ops = []
for i, k in enumerate(NEWC):
    v = CAMPAIGNS[k]
    o = c.get_type("CampaignOperation"); x = o.create
    x.name = v["name"]
    x.status = c.enums.CampaignStatusEnum.PAUSED
    x.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.SEARCH
    x.campaign_budget = c.get_service("CampaignBudgetService").campaign_budget_path(
        CID, FREE_BUDGETS[0])
    x.target_spend.cpc_bid_ceiling_micros = int(round(v["cpc_ceiling"] * 1e6))
    x.network_settings.target_google_search = True
    x.network_settings.target_search_network = False
    x.network_settings.target_content_network = False
    x.network_settings.target_partner_search_network = False
    x.geo_target_type_setting.positive_geo_target_type = \
        c.enums.PositiveGeoTargetTypeEnum.PRESENCE
    x.geo_target_type_setting.negative_geo_target_type = \
        c.enums.NegativeGeoTargetTypeEnum.PRESENCE
    x.contains_eu_political_advertising = (
        c.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
    ops.append(o)
per_c = {}
for o in ops:
    r = c.get_type("MutateCampaignsRequest")
    r.customer_id = CID; r.operations.append(o); r.validate_only = True
    try:
        c.get_service("CampaignService").mutate_campaigns(request=r)
        per_c[o.create.name] = "VALIDATED_OK"
    except Exception as e:
        per_c[o.create.name] = f"FAILED {str(e)[:160]}"
    print(f"  {o.create.name[:62]:62s} {per_c[o.create.name][:40]}")
res["checks"]["new_campaigns"] = per_c
res["checks"]["new_campaigns_note"] = (
    "Validated one campaign per request against a single non-shared unattached budget. "
    "Batching them shares one non-shared budget, which Google rejects; that is a harness "
    "artefact, not a plan defect, because execution creates a budget per campaign.")

# ------------------------------------------------------------- 3. ad groups
print("\n=== 3. NEW AD GROUPS, PAUSED ===")
NEWAG = [(n, d) for n, d in AG.items() if not d["existing_ad_group_id"]]
CAMP_STAND_IN = "24257819463"   # a real paused campaign, used only as a validate target
ops = []
for n, d in NEWAG:
    o = c.get_type("AdGroupOperation"); x = o.create
    x.name = n
    x.campaign = c.get_service("CampaignService").campaign_path(CID, CAMP_STAND_IN)
    x.status = c.enums.AdGroupStatusEnum.PAUSED
    x.type_ = c.enums.AdGroupTypeEnum.SEARCH_STANDARD
    x.cpc_bid_micros = int(round(d["cpc_bid"] * 1e6))
    ops.append(o)
r = c.get_type("MutateAdGroupsRequest")
r.customer_id = CID; r.operations.extend(ops); r.partial_failure = False
r.validate_only = True
try:
    c.get_service("AdGroupService").mutate_ad_groups(request=r)
    print(f"  VALIDATED_OK - {len(ops)} ad groups PAUSED")
    res["checks"]["new_ad_groups"] = f"OK ({len(ops)})"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["new_ad_groups"] = f"FAILED {str(e)[:250]}"

# --------------------------------------------------------------- 4. keywords
print("\n=== 4. KEYWORDS ===")
AGRN = c.get_service("AdGroupService").ad_group_path(CID, "199797580706")
MOVED = {(k["text"].lower(), k["match_type"])
         for o in build["operations"]
         if o["op"] == "REMOVE_KEYWORDS_FROM_EXISTING_AD_GROUP" for k in o["keywords"]}
ops, skipped = [], []
for n, d in AG.items():
    for t in d["phrase"]:
        if (t.lower(), "PHRASE") in MOVED:
            skipped.append(f"{t} [PHRASE]"); continue
        o = c.get_type("AdGroupCriterionOperation"); x = o.create
        x.ad_group = AGRN; x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
        x.keyword.text = t; x.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
        ops.append(o)
    for t in d["exact"]:
        if (t.lower(), "EXACT") in MOVED:
            skipped.append(f"{t} [EXACT]"); continue
        o = c.get_type("AdGroupCriterionOperation"); x = o.create
        x.ad_group = AGRN; x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
        x.keyword.text = t; x.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT
        ops.append(o)
print(f"  {len(skipped)} keyword(s) excluded from the probe because the plan MOVES them "
      f"off the stand-in ad group first: {skipped}")
r = c.get_type("MutateAdGroupCriteriaRequest")
r.customer_id = CID; r.operations.extend(ops); r.partial_failure = False
r.validate_only = True
try:
    c.get_service("AdGroupCriterionService").mutate_ad_group_criteria(request=r)
    print(f"  VALIDATED_OK - {len(ops)} keywords")
    res["checks"]["keywords"] = f"OK ({len(ops)} probed, {len(skipped)} moved-not-probed)"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["keywords"] = f"FAILED {str(e)[:250]}"

# ------------------------------------------------------- 5. cross-negatives
print("\n=== 5. AD-GROUP CROSS-NEGATIVES ===")
ops = []
for n, negs in build["cross_negatives"].items():
    for t in negs:
        o = c.get_type("AdGroupCriterionOperation"); x = o.create
        x.ad_group = AGRN; x.negative = True
        x.keyword.text = t; x.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
        ops.append(o)
r = c.get_type("MutateAdGroupCriteriaRequest")
r.customer_id = CID; r.operations.extend(ops); r.partial_failure = False
r.validate_only = True
try:
    c.get_service("AdGroupCriterionService").mutate_ad_group_criteria(request=r)
    print(f"  VALIDATED_OK - {len(ops)} negatives")
    res["checks"]["cross_negatives"] = f"OK ({len(ops)})"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}")
    res["checks"]["cross_negatives"] = f"FAILED {str(e)[:250]}"

# --------------------------------------------------------------------- 6. RSAs
print("\n=== 6. RSAs - text, limits, destination policy ===")
per = {}
for n, d in AG.items():
    if not d["rsas"]:
        per[n] = f"NO RSA - {d['page_verdict']}"
        continue
    ops = []
    for rs in d["rsas"]:
        o = c.get_type("AdGroupAdOperation"); a = o.create
        a.ad_group = AGRN; a.status = c.enums.AdGroupAdStatusEnum.PAUSED
        a.ad.final_urls.append(d["url"])
        rr = a.ad.responsive_search_ad
        for h in rs["h"]:
            t = c.get_type("AdTextAsset"); t.text = h; rr.headlines.append(t)
        for x in rs["d"]:
            t = c.get_type("AdTextAsset"); t.text = x; rr.descriptions.append(t)
        ops.append(o)
    r = c.get_type("MutateAdGroupAdsRequest")
    r.customer_id = CID; r.operations.extend(ops); r.partial_failure = False
    r.validate_only = True
    try:
        c.get_service("AdGroupAdService").mutate_ad_group_ads(request=r)
        per[n] = f"VALIDATED_OK ({len(ops)})"
    except Exception as e:
        per[n] = f"FAILED topics={sorted(set(TOPIC.findall(str(e))))} {str(e)[:130]}"
    print(f"  {n[:44]:44s} {per[n][:76]}")
res["checks"]["rsas"] = per

# ------------------------------------------------ 7. keyword removal from 199797580706
print("\n=== 7. KEYWORD REMOVAL FROM THE REUSED FURNACE REPAIR AD GROUP ===")
rm = [o for o in build["operations"]
      if o["op"] == "REMOVE_KEYWORDS_FROM_EXISTING_AD_GROUP"]
found = {}
for r_ in q(c, """SELECT ad_group.id, ad_group_criterion.criterion_id,
                  ad_group_criterion.keyword.text,
                  ad_group_criterion.keyword.match_type,
                  ad_group_criterion.status
                  FROM ad_group_criterion
                  WHERE ad_group.id = 199797580706
                    AND ad_group_criterion.type = 'KEYWORD'
                    AND ad_group_criterion.negative = FALSE
                    AND ad_group_criterion.status != 'REMOVED'"""):
    x = r_.ad_group_criterion
    found[(x.keyword.text.lower(), E(x.keyword.match_type))] = str(x.criterion_id)
targets = [(k["text"].lower(), k["match_type"]) for o in rm for k in o["keywords"]]
missing = [t for t in targets if t not in found]
print(f"  targets {len(targets)}; resolved to live criterion ids "
      f"{len(targets) - len(missing)}; missing {len(missing)}")
for t in targets:
    print(f"    {t[1]:7s} '{t[0]}' -> criterion {found.get(t, 'NOT FOUND')}")
res["checks"]["keyword_removal"] = {
    "targets": len(targets), "resolved": len(targets) - len(missing),
    "missing": missing,
    "criterion_ids": {f"{t[0]} [{t[1]}]": found.get(t) for t in targets},
    "verdict": "OK" if not missing else "PROBLEM"}

# ------------------------------------------------------- 8. budget + bid + pause
print("\n=== 8. BUDGET REALLOCATION ===")
ops = []
for o_ in budget["operations"]:
    o = c.get_type("CampaignBudgetOperation")
    o.update.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(
        CID, o_["budget_id"])
    o.update.amount_micros = int(round(o_["to_usd"] * 1e6))
    o.update_mask.paths.append("amount_micros")
    ops.append(o)
r = c.get_type("MutateCampaignBudgetsRequest")
r.customer_id = CID; r.operations.extend(ops); r.partial_failure = False
r.validate_only = True
try:
    c.get_service("CampaignBudgetService").mutate_campaign_budgets(request=r)
    print(f"  VALIDATED_OK - {len(ops)} budget updates"); res["checks"]["budget"] = "OK"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["budget"] = f"FAILED {str(e)[:250]}"

print("\n=== 9. CPC BID CEILINGS ===")
ops = []
for o_ in bid["operations"]:
    o = c.get_type("CampaignOperation")
    o.update.resource_name = c.get_service("CampaignService").campaign_path(
        CID, o_["campaign_id"])
    o.update.target_spend.cpc_bid_ceiling_micros = int(round(o_["to_usd"] * 1e6))
    o.update_mask.paths.append("target_spend.cpc_bid_ceiling_micros")
    ops.append(o)
r = c.get_type("MutateCampaignsRequest")
r.customer_id = CID; r.operations.extend(ops); r.partial_failure = False
r.validate_only = True
try:
    c.get_service("CampaignService").mutate_campaigns(request=r)
    print(f"  VALIDATED_OK - {len(ops)} ceiling updates"); res["checks"]["bid"] = "OK"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["bid"] = f"FAILED {str(e)[:250]}"

print("\n=== 10. COOLING PAUSE ===")
cops, aops = [], []
for o_ in cool["operations"]:
    if o_["op"] == "PAUSE_CAMPAIGN":
        o = c.get_type("CampaignOperation")
        o.update.resource_name = c.get_service("CampaignService").campaign_path(
            CID, o_["campaign_id"])
        o.update.status = c.enums.CampaignStatusEnum.PAUSED
        o.update_mask.paths.append("status")
        cops.append(o)
    else:
        o = c.get_type("AdGroupOperation")
        o.update.resource_name = c.get_service("AdGroupService").ad_group_path(
            CID, o_["ad_group_id"])
        o.update.status = c.enums.AdGroupStatusEnum.PAUSED
        o.update_mask.paths.append("status")
        aops.append(o)
ok = True
if cops:
    r = c.get_type("MutateCampaignsRequest")
    r.customer_id = CID; r.operations.extend(cops); r.partial_failure = False
    r.validate_only = True
    try:
        c.get_service("CampaignService").mutate_campaigns(request=r)
        print(f"  VALIDATED_OK - {len(cops)} campaign pauses")
    except Exception as e:
        ok = False; print(f"  FAILED campaigns {str(e)[:300]}")
if aops:
    r = c.get_type("MutateAdGroupsRequest")
    r.customer_id = CID; r.operations.extend(aops); r.partial_failure = False
    r.validate_only = True
    try:
        c.get_service("AdGroupService").mutate_ad_groups(request=r)
        print(f"  VALIDATED_OK - {len(aops)} ad-group pauses")
    except Exception as e:
        ok = False; print(f"  FAILED ad groups {str(e)[:300]}")
res["checks"]["cooling_pause"] = "OK" if ok else "FAILED"

# ------------------------------------------- 11. structured snippets + assets
print("\n=== 11. NEW STRUCTURED SNIPPETS ===")
snips = [o for o in build["operations"] if o["op"] == "CREATE_STRUCTURED_SNIPPET_AND_LINK"]
ops = []
for o_ in snips:
    o = c.get_type("AssetOperation"); a = o.create
    a.structured_snippet_asset.header = o_["header"]
    a.structured_snippet_asset.values.extend(o_["values"])
    ops.append(o)
r = c.get_type("MutateAssetsRequest")
r.customer_id = CID; r.operations.extend(ops); r.validate_only = True
try:
    c.get_service("AssetService").mutate_assets(request=r)
    print(f"  VALIDATED_OK - {len(ops)} structured snippets")
    res["checks"]["structured_snippets"] = f"OK ({len(ops)})"
except Exception as e:
    print(f"  FAILED {str(e)[:350]}")
    res["checks"]["structured_snippets"] = f"FAILED {str(e)[:250]}"

print("\n=== 12. REUSED ASSETS STILL VALID ===")
reuse = sorted({a for o in build["operations"]
                if o["op"] == "LINK_EXISTING_CALLOUT_ASSETS" for a in o["asset_ids"]}
               | {a for o in build["operations"]
                  if o["op"] == "LINK_EXISTING_SITELINK_ASSETS" for a in o["asset_ids"]}
               | {o["asset_id"] for o in build["operations"]
                  if o["op"].startswith("LINK_EXISTING_") and "asset_id" in o})
BLOCKED_URL = "https://ambientcoolingandheating.com/services/heating-services/heat-pumps"
seen, bad, blocked = {}, [], []
for row in q(c, f"""SELECT asset.id, asset.type, asset.final_urls,
                    asset.policy_summary.approval_status
                    FROM asset WHERE asset.id IN ({','.join(reuse)})"""):
    ap = E(row.asset.policy_summary.approval_status)
    seen[str(row.asset.id)] = ap
    if ap == "DISAPPROVED":
        bad.append(str(row.asset.id))
    if any(u.rstrip("/") == BLOCKED_URL for u in row.asset.final_urls):
        blocked.append(str(row.asset.id))
missing = [a for a in reuse if a not in seen]
print(f"  checked {len(reuse)}  missing={len(missing)}  disapproved={len(bad)}  "
      f"pointing_at_blocked_url={len(blocked)}")
res["checks"]["reused_assets"] = {
    "checked": len(reuse), "missing": missing, "disapproved": bad,
    "pointing_at_blocked_url": blocked,
    "verdict": "OK" if not (missing or bad or blocked) else "PROBLEM"}
print(f"  verdict: {res['checks']['reused_assets']['verdict']}")

VRECEIPTS.mkdir(parents=True, exist_ok=True)
p = VRECEIPTS / f"AMB-0921B-TRANSITION-{STAMP}.json"
p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
for n in FP:
    pl = json.loads((PLANS / f"{n}.json").read_text(encoding="utf-8"))
    print(f"APPROVE {n} {pl['fingerprint']} {pl['operation_count']} operations FOR {CID}")
print("NOTHING WAS CREATED, CHANGED OR PAUSED. EXTERNAL WRITES: 0")
