#!/usr/bin/env python3
"""Ambient | 2026-09-18 | validate_only for the three expansion plans. Nothing is created."""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-21"
TOPIC = re.compile(r'topic: "([A-Z_]+)"')
c = client(); identity_gate(c, verbose=False)
res = {"when": datetime.datetime.now(TZ).isoformat(), "validate_only": True,
       "external_writes": 0, "checks": {}}


def load(name, fp_want):
    p = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8"))
    fp = p.pop("fingerprint"); re_fp = approval_code(p); p["fingerprint"] = fp
    ok = fp == re_fp == fp_want
    print(f"{name}: disk={fp} recomputed={re_fp} approved={fp_want} MATCH={ok} "
          f"ops={p['operation_count']}")
    assert ok, f"FINGERPRINT MISMATCH {name}"
    return p


ex = load("AMB-0921-HEAT-EXPAND-1", "20A73EEA3023")
bu = load("AMB-0921-BUDGET-1", "6C665894E30D")
bd = load("AMB-0921-BID-1", "B520C42F2007")
snap = json.loads((SNAP / "heating-build-snapshot-2026-09-17.json").read_text(encoding="utf-8"))
GEO, SCHED = snap["reusable_geo_target_ids"], snap["reusable_schedule"]

# ------------------------------------------------------------- 1. new budgets
print("\n=== 1. NEW CAMPAIGN BUDGETS (2) ===")
ops = []
for k, v in ex["new_campaigns"].items():
    o = c.get_type("CampaignBudgetOperation"); b = o.create
    b.name = f"Budget | {v['name']}"
    b.amount_micros = int(round(v["daily_budget"] * 1e6))
    b.explicitly_shared = False
    b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
    ops.append(o)
r = c.get_type("MutateCampaignBudgetsRequest")
r.customer_id = CID; r.operations.extend(ops); r.validate_only = True
try:
    c.get_service("CampaignBudgetService").mutate_campaign_budgets(request=r)
    print(f"  VALIDATED_OK - {len(ops)} budgets"); res["checks"]["new_budgets"] = "OK"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["new_budgets"] = f"FAILED {str(e)[:200]}"

# ----------------------------------------------------------- 2. new campaigns
print("\n=== 2. NEW CAMPAIGNS, PAUSED (2) ===")
FREE = {"HEATPUMP": "15044731597", "TANKLESS": "15466378777"}   # reference_count = 0
ops = []
for k, v in ex["new_campaigns"].items():
    o = c.get_type("CampaignOperation"); x = o.create
    x.name = v["name"]
    x.status = c.enums.CampaignStatusEnum.PAUSED
    x.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.SEARCH
    x.campaign_budget = c.get_service(
        "CampaignBudgetService").campaign_budget_path(CID, FREE[k])
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
r = c.get_type("MutateCampaignsRequest")
r.customer_id = CID; r.operations.extend(ops); r.validate_only = True
try:
    c.get_service("CampaignService").mutate_campaigns(request=r)
    print(f"  VALIDATED_OK - {len(ops)} campaigns, PAUSED, EU field set")
    res["checks"]["new_campaigns"] = "OK"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["new_campaigns"] = f"FAILED {str(e)[:200]}"

# ------------------------------------------------------- 3. keywords per group
_nkw = sum(len(d["phrase"]) + len(d["exact"]) for d in ex["new_ad_groups"].values())
print(f"\n=== 3. KEYWORDS ({_nkw}) ===")
AGRN = c.get_service("AdGroupService").ad_group_path(CID, "199797580706")
ops = []
for ag, d in ex["new_ad_groups"].items():
    for t in d["phrase"]:
        o = c.get_type("AdGroupCriterionOperation"); x = o.create
        x.ad_group = AGRN; x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
        x.keyword.text = t; x.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
        ops.append(o)
    for t in d["exact"]:
        o = c.get_type("AdGroupCriterionOperation"); x = o.create
        x.ad_group = AGRN; x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
        x.keyword.text = t; x.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT
        ops.append(o)
r = c.get_type("MutateAdGroupCriteriaRequest")
r.customer_id = CID; r.operations.extend(ops)
r.partial_failure = False; r.validate_only = True
try:
    c.get_service("AdGroupCriterionService").mutate_ad_group_criteria(request=r)
    print(f"  VALIDATED_OK - {len(ops)} keywords"); res["checks"]["keywords"] = f"OK ({len(ops)})"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["keywords"] = f"FAILED {str(e)[:200]}"

# ------------------------------------------------------------------ 4. RSAs
print("\n=== 4. RSAs (10) - text, limits, destination policy ===")
per = {}
for ag, d in ex["new_ad_groups"].items():
    if not d["rsas"]:
        per[ag] = "SKIPPED - no RSA in plan (destination blocked)"
        continue
    ops = []
    for rsa in d["rsas"]:
        o = c.get_type("AdGroupAdOperation"); a = o.create
        a.ad_group = AGRN; a.status = c.enums.AdGroupAdStatusEnum.PAUSED
        a.ad.final_urls.append(d["url"])
        rr = a.ad.responsive_search_ad
        for h in rsa["h"]:
            t = c.get_type("AdTextAsset"); t.text = h; rr.headlines.append(t)
        for x in rsa["d"]:
            t = c.get_type("AdTextAsset"); t.text = x; rr.descriptions.append(t)
        ops.append(o)
    r = c.get_type("MutateAdGroupAdsRequest")
    r.customer_id = CID; r.operations.extend(ops)
    r.partial_failure = False; r.validate_only = True
    try:
        c.get_service("AdGroupAdService").mutate_ad_group_ads(request=r)
        per[ag] = f"VALIDATED_OK ({len(ops)})"
    except Exception as e:
        per[ag] = f"FAILED topics={sorted(set(TOPIC.findall(str(e))))} {str(e)[:150]}"
    print(f"  {ag[:44]:44s} {per[ag][:80]}")
res["checks"]["rsas"] = per

# ------------------------------------------------------- 5. budget + bid plans
print("\n=== 5. BUDGET REALLOCATION (6) ===")
ops = []
for o_ in bu["operations"]:
    o = c.get_type("CampaignBudgetOperation")
    o.update.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(
        CID, o_["budget_id"])
    o.update.amount_micros = int(round(o_["to_usd"] * 1e6))
    o.update_mask.paths.append("amount_micros")
    ops.append(o)
r = c.get_type("MutateCampaignBudgetsRequest")
r.customer_id = CID; r.operations.extend(ops); r.partial_failure = False; r.validate_only = True
try:
    c.get_service("CampaignBudgetService").mutate_campaign_budgets(request=r)
    print(f"  VALIDATED_OK - {len(ops)} budget updates"); res["checks"]["budget_0921"] = "OK"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["budget_0921"] = f"FAILED {str(e)[:200]}"

print("\n=== 6. CPC BID CEILINGS (2) ===")
ops = []
for o_ in bd["operations"]:
    o = c.get_type("CampaignOperation")
    o.update.resource_name = c.get_service("CampaignService").campaign_path(
        CID, o_["campaign_id"])
    o.update.target_spend.cpc_bid_ceiling_micros = int(round(o_["to_usd"] * 1e6))
    o.update_mask.paths.append("target_spend.cpc_bid_ceiling_micros")
    ops.append(o)
r = c.get_type("MutateCampaignsRequest")
r.customer_id = CID; r.operations.extend(ops); r.partial_failure = False; r.validate_only = True
try:
    c.get_service("CampaignService").mutate_campaigns(request=r)
    print(f"  VALIDATED_OK - {len(ops)} ceiling updates"); res["checks"]["bid1"] = "OK"
except Exception as e:
    print(f"  FAILED {str(e)[:400]}"); res["checks"]["bid1"] = f"FAILED {str(e)[:200]}"

# --------------------------------------------------- 7. campaign asset operations
print("\n=== 7. CAMPAIGN ASSETS ===")

# 7a. the two new structured snippets, created for real
snips = [o for o in ex["operations"] if o["op"] == "CREATE_STRUCTURED_SNIPPET_AND_LINK"]
ops = []
for o_ in snips:
    o = c.get_type("AssetOperation")
    a = o.create
    a.structured_snippet_asset.header = o_["header"]
    a.structured_snippet_asset.values.extend(o_["values"])
    ops.append(o)
r = c.get_type("MutateAssetsRequest")
r.customer_id = CID; r.operations.extend(ops); r.validate_only = True
try:
    c.get_service("AssetService").mutate_assets(request=r)
    print(f"  structured snippets  VALIDATED_OK ({len(ops)})")
    res["checks"]["structured_snippets"] = f"OK ({len(ops)})"
except Exception as e:
    print(f"  structured snippets  FAILED {str(e)[:300]}")
    res["checks"]["structured_snippets"] = f"FAILED {str(e)[:200]}"

# 7b. every reused asset must still exist and be approved before it is linked
reuse = sorted({a for o in ex["operations"]
                if o["op"] == "LINK_EXISTING_CALLOUT_ASSETS" for a in o["asset_ids"]}
               | {sl["asset_id"] for o in ex["operations"]
                  if o["op"] == "LINK_EXISTING_SITELINK_ASSETS" for sl in o["sitelinks"]}
               | {o["asset_id"] for o in ex["operations"]
                  if o["op"].startswith("LINK_EXISTING_") and "asset_id" in o})
seen, bad = {}, []
for row in q(c, f"""SELECT asset.id, asset.type, asset.final_urls,
                    asset.policy_summary.approval_status,
                    asset.policy_summary.review_status
                    FROM asset WHERE asset.id IN ({','.join(reuse)})"""):
    ap = E(row.asset.policy_summary.approval_status)
    seen[str(row.asset.id)] = {"type": E(row.asset.type_), "approval": ap,
                               "final_urls": list(row.asset.final_urls)}
    if ap == "DISAPPROVED":
        bad.append(str(row.asset.id))
missing = [a for a in reuse if a not in seen]
BLOCKED_URL = "https://ambientcoolingandheating.com/services/heating-services/heat-pumps"
points_at_blocked = [a for a, v in seen.items()
                     if any(u.rstrip("/") == BLOCKED_URL for u in v["final_urls"])]
print(f"  reused assets checked {len(reuse)}  missing={len(missing)}  "
      f"disapproved={len(bad)}  pointing_at_blocked_url={len(points_at_blocked)}")
res["checks"]["reused_assets"] = {
    "checked": len(reuse), "missing": missing, "disapproved": bad,
    "pointing_at_blocked_url": points_at_blocked,
    "verdict": "OK" if not (missing or bad or points_at_blocked) else "PROBLEM"}
print(f"  verdict: {res['checks']['reused_assets']['verdict']}")

VRECEIPTS.mkdir(parents=True, exist_ok=True)
p = VRECEIPTS / f"AMB-0921-EXPANSION-{STAMP}.json"
p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
for n, f, o in [("AMB-0921-HEAT-EXPAND-1", ex["fingerprint"], ex["operation_count"]),
                ("AMB-0921-BUDGET-1", bu["fingerprint"], bu["operation_count"]),
                ("AMB-0921-BID-1", bd["fingerprint"], bd["operation_count"])]:
    print(f"APPROVE {n} {f} {o} operations FOR {CID}")
print("NOTHING WAS CREATED OR CHANGED. EXTERNAL WRITES: 0")
