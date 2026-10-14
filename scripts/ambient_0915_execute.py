#!/usr/bin/env python3
"""Ambient | 2026-09-15 | EXECUTE AMB-0915-COMM-RSA-1 and AMB-0915-COMM-ASSET-1.

Approved:
  APPROVE AMB-0915-COMM-RSA-1   6C32B210CF5B 2 operations FOR 2401959466
  APPROVE AMB-0915-COMM-ASSET-1 02F6EECCCDF8 7 operations FOR 2401959466

Order of work, with a hard stop at any drift:
  1 fresh identity gate
  2 re-read campaign + ad group + keywords + negatives + ads + assets
  3 recompute both fingerprints from disk
  4 assert the before-state still matches
  5 validate_only both packages
  6 create 2 RSAs PAUSED
  7 create 7 assets, then link them to the ad group with the link PAUSED
  8 read everything back field by field
  9 prove unrelated resources unchanged
 10 write execution receipts

A landing-page reachability check is deliberately made WITHOUT query parameters so this
run cannot seed the SiteGround proxy cache with another synthetic marker.
"""
from __future__ import annotations
import sys, json, datetime, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-15"
CAMP, COMM_AG, RES_AG = "24132507747", "199748801029", "202339087634"
APPROVED = {
    "AMB-0915-COMM-RSA-1": ("6C32B210CF5B", 2),
    "AMB-0915-COMM-ASSET-1": ("02F6EECCCDF8", 7),
}
LIVE = ROOT / "receipts" / "live"
rec = {"stamp": STAMP, "started_local": datetime.datetime.now(TZ).isoformat(),
       "approvals": APPROVED, "steps": []}


def step(name, data):
    rec["steps"].append({"step": name, "at": datetime.datetime.now(TZ).isoformat(),
                         "data": data})


def die(msg, data=None):
    step("ABORT", {"reason": msg, "data": data})
    LIVE.mkdir(parents=True, exist_ok=True)
    (LIVE / f"AMB-0915-ABORT-{STAMP}.json").write_text(
        json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(f"\n*** ABORT: {msg} ***")
    sys.exit(2)


c = client()

# ---------------------------------------------------------------- 1. identity
print("=== 1. FRESH IDENTITY GATE ===")
row = q(c, """SELECT customer.id, customer.descriptive_name, customer.currency_code,
                     customer.time_zone, customer.manager, customer.test_account,
                     customer.status FROM customer""")[0].customer
links = {x.customer_manager_link.manager_customer.split("/")[-1]:
         E(x.customer_manager_link.status)
         for x in q(c, """SELECT customer_manager_link.manager_customer,
                                 customer_manager_link.status FROM customer_manager_link""")}
checks = {
    "name == 'Ambient Cooling - Live'": row.descriptive_name == EXACT_NAME,
    "id == 2401959466": str(row.id) == CID,
    "not manager": not row.manager, "not test": not row.test_account,
    "TZ America/New_York": row.time_zone == "America/New_York",
    "USD": row.currency_code == "USD", "ENABLED": E(row.status) == "ENABLED",
    "GM 3373711342 ACTIVE": links.get(GM_MANAGER) == "ACTIVE",
    "ClickCease 2815082755 ACTIVE": links.get(CC_MANAGER) == "ACTIVE",
}
for k, v in checks.items():
    print(f"  [{'PASS' if v else 'FAIL'}] {k}")
if not all(checks.values()):
    die("identity gate failed", checks)
step("identity_gate", {"checks": checks, "observed_name": row.descriptive_name,
                       "observed_id": str(row.id)})
print(f"\n  Ambient Cooling - Live | 2401959466 | Commercial HVAC Installation")

# ---------------------------------------------------------------- 2. re-read targets
print("\n=== 2. RE-READ TARGET CAMPAIGN AND AD GROUP ===")
cm = q(c, f"""SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
                     campaign.target_spend.cpc_bid_ceiling_micros,
                     campaign.network_settings.target_search_network,
                     campaign.network_settings.target_content_network,
                     campaign.geo_target_type_setting.positive_geo_target_type,
                     campaign_budget.amount_micros, campaign_budget.id
              FROM campaign WHERE campaign.id = {CAMP}""")[0]
ag = q(c, f"""SELECT ad_group.id, ad_group.name, ad_group.status,
                     ad_group.cpc_bid_micros, ad_group.tracking_url_template,
                     ad_group.final_url_suffix
              FROM ad_group WHERE ad_group.id = {COMM_AG}""")[0]
kws = q(c, f"""SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                      ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                      ad_group_criterion.approval_status,
                      ad_group_criterion.system_serving_status
               FROM ad_group_criterion WHERE ad_group.id = {COMM_AG}
                 AND ad_group_criterion.negative = FALSE""")
negs = sorted(r.ad_group_criterion.keyword.text for r in q(c, f"""
    SELECT ad_group_criterion.keyword.text FROM ad_group_criterion
    WHERE ad_group.id = {COMM_AG} AND ad_group_criterion.negative = TRUE"""))
ads_before = q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group.id = {COMM_AG}")
agassets_before = q(c, f"""SELECT campaign.id, ad_group.id, ad_group_asset.asset,
                                  ad_group_asset.field_type, ad_group_asset.status
                           FROM ad_group_asset WHERE ad_group.id = {COMM_AG}""")
camp_callouts = sorted(r.asset.callout_asset.callout_text for r in q(c, f"""
    SELECT campaign.id, asset.callout_asset.callout_text FROM campaign_asset
    WHERE campaign.id = {CAMP} AND campaign_asset.field_type = CALLOUT"""))

live_before = {
    "campaign_status": E(cm.campaign.status),
    "campaign_serving": E(cm.campaign.serving_status),
    "campaign_cpc_ceiling_usd": cm.campaign.target_spend.cpc_bid_ceiling_micros / 1e6,
    "campaign_budget_usd": cm.campaign_budget.amount_micros / 1e6,
    "campaign_budget_id": str(cm.campaign_budget.id),
    "search_partners": cm.campaign.network_settings.target_search_network,
    "display": cm.campaign.network_settings.target_content_network,
    "geo": E(cm.campaign.geo_target_type_setting.positive_geo_target_type),
    "ad_group_name": ag.ad_group.name, "ad_group_status": E(ag.ad_group.status),
    "ad_group_cpc_bid_micros": ag.ad_group.cpc_bid_micros,
    "ad_group_tracking_url_template": ag.ad_group.tracking_url_template or None,
    "ad_group_final_url_suffix": ag.ad_group.final_url_suffix or None,
    "keywords": sorted(f"{E(k.ad_group_criterion.keyword.match_type)}:"
                       f"{k.ad_group_criterion.keyword.text}:"
                       f"{E(k.ad_group_criterion.status)}:"
                       f"{E(k.ad_group_criterion.approval_status)}:"
                       f"{E(k.ad_group_criterion.system_serving_status)}" for k in kws),
    "negatives_count": len(negs), "negatives": negs,
    "ads_count": len(ads_before),
    "ad_group_asset_links": len(agassets_before),
    "campaign_callouts": camp_callouts,
}
for k, v in live_before.items():
    print(f"  {k}: {v if not isinstance(v, list) or len(v) < 5 else str(v)[:110]+'...'}")
step("live_before_state", live_before)

# landing page reachability, NO query parameters so the proxy cache is not re-seeded
FINAL_URL = "https://offer.ambientcoolingandheating.com/commercial-hvac-installation/"
try:
    req = urllib.request.Request(FINAL_URL, method="GET",
                                 headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; "
                                                        "Win64; x64) AppleWebKit/537.36 "
                                                        "(KHTML, like Gecko) Chrome/141.0.0.0 "
                                                        "Safari/537.36"})
    with urllib.request.urlopen(req, timeout=45) as r:
        lp_status, lp_final = r.status, r.geturl()
except Exception as ex:
    lp_status, lp_final = None, str(ex)[:200]
print(f"  landing page (no params): HTTP {lp_status} -> {lp_final}")
step("landing_page_check", {"status": lp_status, "final_url": lp_final,
                            "params_sent": False})

# ---------------------------------------------------------------- 3. fingerprints
print("\n=== 3. RECOMPUTE FINGERPRINTS FROM DISK ===")
plans = {}
for name, (fp_expected, ops_expected) in APPROVED.items():
    d = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8"))
    claimed = d.pop("fingerprint")
    recomputed = approval_code(d)
    d["fingerprint"] = claimed
    ok = (claimed == recomputed == fp_expected and d["operation_count"] == ops_expected)
    print(f"  {name:24s} approved={fp_expected} on_disk={claimed} "
          f"recomputed={recomputed} ops={d['operation_count']}/{ops_expected} "
          f"{'MATCH' if ok else 'MISMATCH'}")
    if not ok:
        die(f"fingerprint/op-count mismatch for {name}",
            {"approved": fp_expected, "on_disk": claimed, "recomputed": recomputed})
    plans[name] = d
step("fingerprints", {n: plans[n]["fingerprint"] for n in plans})

# ---------------------------------------------------------------- 4. drift gate
print("\n=== 4. BEFORE-STATE DRIFT GATE ===")
rsa_before = plans["AMB-0915-COMM-RSA-1"]["before_state"]
gates = {
    "ads in ad group still 0": live_before["ads_count"] == 0
                               == rsa_before["ads_in_ad_group"],
    "ad-group negatives still 17": live_before["negatives_count"] == 17
                                   == rsa_before["ad_group_negatives_count"],
    "negative set unchanged": negs == sorted([
        "career", "careers", "course", "courses", "diy", "homeowner", "house", "job",
        "jobs", "parts", "residential", "salaries", "salary", "supplier", "supply",
        "used", "wholesale"]),
    "both keywords ENABLED+APPROVED+ELIGIBLE": all(
        x.endswith(":ENABLED:APPROVED:ELIGIBLE") for x in live_before["keywords"]
    ) and len(live_before["keywords"]) == 2,
    "campaign still ENABLED": live_before["campaign_status"] == "ENABLED",
    "campaign budget still $176.15": live_before["campaign_budget_usd"] == 176.15,
    "campaign ceiling still $30.00": live_before["campaign_cpc_ceiling_usd"] == 30.0,
    "ad group has 0 asset links": live_before["ad_group_asset_links"] == 0,
    "landing page HTTP 200": lp_status == 200,
    "campaign callouts unchanged (5, no overlap)": (
        len(camp_callouts) == 5
        and not set(camp_callouts) & {o["text"] for o in
                                      plans["AMB-0915-COMM-ASSET-1"]["operations"]
                                      if o.get("text")}),
}
for k, v in gates.items():
    print(f"  [{'PASS' if v else 'FAIL'}] {k}")
if not all(gates.values()):
    die("before-state has DRIFTED - plan must be superseded", gates)
step("drift_gate", gates)

# NOTE: the ad group is ENABLED (owner action 2026-09-15 08:42:16). That is recorded in
# the plan's risk field and is why every created resource below is PAUSED.
print(f"\n  ad group status = {live_before['ad_group_status']} "
      f"-> every created ad and asset link MUST be PAUSED")

# ---------------------------------------------------------------- 5. build operations
print("\n=== 5. BUILD OPERATIONS ===")
ad_group_rn = c.get_service("AdGroupService").ad_group_path(CID, COMM_AG)

rsa_ops = []
for op in plans["AMB-0915-COMM-RSA-1"]["operations"]:
    o = c.get_type("AdGroupAdOperation")
    a = o.create
    a.ad_group = ad_group_rn
    a.status = c.enums.AdGroupAdStatusEnum.PAUSED
    a.ad.final_urls.append(op["final_url"])
    r_ = a.ad.responsive_search_ad
    r_.path1, r_.path2 = op["path1"], op["path2"]
    for h in op["headlines_pinned_headline_1"]:
        t = c.get_type("AdTextAsset"); t.text = h
        t.pinned_field = c.enums.ServedAssetFieldTypeEnum.HEADLINE_1
        r_.headlines.append(t)
    for h in op["headlines_unpinned"]:
        t = c.get_type("AdTextAsset"); t.text = h
        r_.headlines.append(t)
    for d_ in op["descriptions"]:
        t = c.get_type("AdTextAsset"); t.text = d_
        r_.descriptions.append(t)
    rsa_ops.append(o)
print(f"  {len(rsa_ops)} AdGroupAdOperation, status=PAUSED")

asset_ops, asset_meta = [], []
for op in plans["AMB-0915-COMM-ASSET-1"]["operations"]:
    o = c.get_type("AssetOperation")
    a = o.create
    if op["field_type"] == "CALLOUT":
        a.callout_asset.callout_text = op["text"]
        a.name = f"GM | Commercial | Callout | {op['text']}"
        asset_meta.append({"field_type": "CALLOUT", "text": op["text"]})
    else:
        a.structured_snippet_asset.header = op["header"]
        a.structured_snippet_asset.values.extend(op["values"])
        a.name = "GM | Commercial | Snippet | Types"
        asset_meta.append({"field_type": "STRUCTURED_SNIPPET",
                           "header": op["header"], "values": op["values"]})
    asset_ops.append(o)
print(f"  {len(asset_ops)} AssetOperation (6 CALLOUT + 1 STRUCTURED_SNIPPET)")
if len(rsa_ops) != 2 or len(asset_ops) != 7:
    die("operation count mismatch after build",
        {"rsa": len(rsa_ops), "asset": len(asset_ops)})

# ---------------------------------------------------------------- 6. validate_only
print("\n=== 6. VALIDATE_ONLY BOTH PACKAGES ===")
vo = {}
req = c.get_type("MutateAdGroupAdsRequest")
req.customer_id = CID; req.operations.extend(rsa_ops)
req.partial_failure = False; req.validate_only = True
try:
    c.get_service("AdGroupAdService").mutate_ad_group_ads(request=req)
    vo["rsa"] = "VALIDATED_OK"
except Exception as ex:
    vo["rsa"] = f"FAILED: {str(ex)[:1500]}"
req2 = c.get_type("MutateAssetsRequest")
req2.customer_id = CID; req2.operations.extend(asset_ops)
req2.validate_only = True
try:
    c.get_service("AssetService").mutate_assets(request=req2)
    vo["assets"] = "VALIDATED_OK"
except Exception as ex:
    vo["assets"] = f"FAILED: {str(ex)[:1500]}"
for k, v in vo.items():
    print(f"  {k}: {v[:200]}")
step("validate_only", vo)
if not all(v == "VALIDATED_OK" for v in vo.values()):
    die("validate_only failed", vo)

# ---------------------------------------------------------------- 7. EXECUTE RSAs
print("\n=== 7. EXECUTE AMB-0915-COMM-RSA-1 (2 ops, PAUSED) ===")
req = c.get_type("MutateAdGroupAdsRequest")
req.customer_id = CID; req.operations.extend(rsa_ops)
req.partial_failure = False; req.validate_only = False
try:
    resp = c.get_service("AdGroupAdService").mutate_ad_group_ads(request=req)
    created_ads = [r.resource_name for r in resp.results]
    print(f"  EXECUTED_OK: {len(created_ads)} results")
    for r_ in created_ads:
        print(f"    {r_}")
    step("execute_rsa", {"status": "EXECUTED_OK", "resources": created_ads,
                         "partial_failure": bool(resp.partial_failure_error)})
except Exception as ex:
    die(f"RSA mutate failed: {str(ex)[:1500]}")

# ---------------------------------------------------------------- 8. EXECUTE assets
print("\n=== 8. EXECUTE AMB-0915-COMM-ASSET-1 step 1/2: create 7 assets ===")
req2 = c.get_type("MutateAssetsRequest")
req2.customer_id = CID; req2.operations.extend(asset_ops); req2.validate_only = False
try:
    resp2 = c.get_service("AssetService").mutate_assets(request=req2)
    created_assets = [r.resource_name for r in resp2.results]
    print(f"  EXECUTED_OK: {len(created_assets)} assets")
    for r_, m in zip(created_assets, asset_meta):
        print(f"    {r_}  {m}")
    step("execute_assets", {"status": "EXECUTED_OK", "resources": created_assets,
                            "meta": asset_meta})
except Exception as ex:
    step("execute_assets", {"status": "FAILED", "error": str(ex)[:1500]})
    die(f"asset create failed AFTER the 2 RSAs were committed: {str(ex)[:800]}. "
        f"RSAs created: {created_ads}. Nothing to roll back automatically - "
        f"the RSAs are PAUSED and inert.")

print("\n=== 8b. link the 7 assets to the ad group, link status PAUSED ===")
link_ops = []
for rn, m in zip(created_assets, asset_meta):
    o = c.get_type("AdGroupAssetOperation")
    l = o.create
    l.ad_group = ad_group_rn
    l.asset = rn
    l.field_type = (c.enums.AssetFieldTypeEnum.CALLOUT
                    if m["field_type"] == "CALLOUT"
                    else c.enums.AssetFieldTypeEnum.STRUCTURED_SNIPPET)
    l.status = c.enums.AssetLinkStatusEnum.PAUSED
    link_ops.append(o)
req3 = c.get_type("MutateAdGroupAssetsRequest")
req3.customer_id = CID; req3.operations.extend(link_ops)
req3.partial_failure = False; req3.validate_only = True
try:
    c.get_service("AdGroupAssetService").mutate_ad_group_assets(request=req3)
    print("  validate_only on links: VALIDATED_OK")
except Exception as ex:
    step("link_validate", {"status": "FAILED", "error": str(ex)[:1500]})
    die(f"ad_group_asset link validation failed. 7 assets exist but are UNLINKED "
        f"(inert, serving nothing): {created_assets}. Error: {str(ex)[:800]}")
req3.validate_only = False
try:
    resp3 = c.get_service("AdGroupAssetService").mutate_ad_group_assets(request=req3)
    created_links = [r.resource_name for r in resp3.results]
    print(f"  EXECUTED_OK: {len(created_links)} links, all PAUSED")
    for r_ in created_links:
        print(f"    {r_}")
    step("execute_links", {"status": "EXECUTED_OK", "resources": created_links})
except Exception as ex:
    step("execute_links", {"status": "FAILED", "error": str(ex)[:1500],
                           "orphan_assets": created_assets})
    die(f"link mutate failed. 7 assets exist UNLINKED and inert: {created_assets}")

rec["finished_local"] = datetime.datetime.now(TZ).isoformat()
rec["created"] = {"ads": created_ads, "assets": created_assets, "links": created_links}
LIVE.mkdir(parents=True, exist_ok=True)
p = LIVE / f"AMB-0915-EXECUTED-{STAMP}.json"
p.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print("\nEXECUTION COMPLETE - run ambient_0915_readback.py next")
