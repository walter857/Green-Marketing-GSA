#!/usr/bin/env python3
"""Ambient | 2026-09-17 | EXECUTE AMB-0917-HEAT-CREATE-1 / 7DE31D6B6A88.

Writes ONLY to child account 2401959466. Never to MCC 3373711342.
Everything is created PAUSED. Nothing is enabled. No budget, conversion action,
existing campaign or unrelated resource is touched.

Raw mutations are built from the SAVED MANIFEST, never from the written summary.
Each stage is one atomic mutate with partial_failure=False; committed resources are
recorded after every stage so a mid-sequence failure can be inventoried, not replayed.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-17"
APPROVED_FP, APPROVED_OPS = "7DE31D6B6A88", 23
LIVE = ROOT / "receipts" / "live"
rec = {"plan": "AMB-0917-HEAT-CREATE-1", "fingerprint": APPROVED_FP,
       "platform_mandated_field_added_at_execution": {
         "field": "campaign.contains_eu_political_advertising",
         "value": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
         "why": "Google returns field_error REQUIRED without it; campaign creation is "
                "impossible otherwise. One truthful value for an HVAC campaign in Central "
                "Maryland. Mirrors all five existing Ambient campaigns. No effect on "
                "budget, bid, targeting, status or delivery. The approved manifest is "
                "otherwise unchanged and still recomputes to 7DE31D6B6A88."},
       "started": datetime.datetime.now(TZ).isoformat(), "customer_id": CID,
       "mcc_never_written": GM_MANAGER, "stages": [], "committed": {}}


def save(tag=""):
    LIVE.mkdir(parents=True, exist_ok=True)
    (LIVE / f"AMB-0917-HEAT-CREATE-1-{STAMP}{tag}.json").write_text(
        json.dumps(rec, indent=1, default=str), encoding="utf-8")


def die(msg):
    rec["ABORT"] = msg
    save("-ABORT")
    print(f"\n*** ABORT: {msg} ***")
    print(f"*** COMMITTED SO FAR: {json.dumps(rec['committed'], default=str)[:900]} ***")
    sys.exit(2)


c = client()
row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
              customer.test_account, customer.status, customer.time_zone,
              customer.currency_code FROM customer""")[0].customer
assert row.descriptive_name == EXACT_NAME and str(row.id) == CID and not row.manager \
    and not row.test_account, "IDENTITY GATE FAILED"
print(f"identity re-confirmed: {row.descriptive_name} / {row.id}")

plan = json.loads((PLANS / "AMB-0917-HEAT-CREATE-1.json").read_text(encoding="utf-8"))
fp = plan.pop("fingerprint"); re_fp = approval_code(plan); plan["fingerprint"] = fp
if not (fp == re_fp == APPROVED_FP) or plan["operation_count"] != APPROVED_OPS:
    die(f"fingerprint/op-count mismatch: disk={fp} recomputed={re_fp} "
        f"ops={plan['operation_count']}")
print(f"fingerprint verified: {fp}  ops={plan['operation_count']}")

snap = json.loads((SNAP / f"heating-build-snapshot-{STAMP}.json").read_text(encoding="utf-8"))
GEO = snap["reusable_geo_target_ids"]
SCHED = snap["reusable_schedule"]
assert len(GEO) == 75 and len(SCHED) == 6

for cm in plan["campaigns"].values():
    if q(c, f"SELECT campaign.id FROM campaign WHERE campaign.name = '{cm['name']}'"):
        die(f"campaign already exists: {cm['name']}")
print("pre-write duplicate check: clean\n")

DAY = {"MONDAY": c.enums.DayOfWeekEnum.MONDAY, "TUESDAY": c.enums.DayOfWeekEnum.TUESDAY,
       "WEDNESDAY": c.enums.DayOfWeekEnum.WEDNESDAY,
       "THURSDAY": c.enums.DayOfWeekEnum.THURSDAY, "FRIDAY": c.enums.DayOfWeekEnum.FRIDAY,
       "SATURDAY": c.enums.DayOfWeekEnum.SATURDAY, "SUNDAY": c.enums.DayOfWeekEnum.SUNDAY}
MT = {"PHRASE": c.enums.KeywordMatchTypeEnum.PHRASE,
      "EXACT": c.enums.KeywordMatchTypeEnum.EXACT}

# ---------------------------------------------------------------- 1. budgets
print("=== STAGE 1: CAMPAIGN BUDGETS (2) ===")
# RESUME SAFETY: the first execution attempt committed both budgets before the campaign
# stage failed. Reuse them by exact name instead of creating duplicates.
existing = {}
for key, cm in plan["campaigns"].items():
    nm = f"Budget | {cm['name']}"
    got = q(c, f"""SELECT campaign_budget.id, campaign_budget.name,
                   campaign_budget.amount_micros, campaign_budget.status
                   FROM campaign_budget WHERE campaign_budget.name = '{nm}'
                     AND campaign_budget.status != 'REMOVED'""")
    for g in got:
        if g.campaign_budget.amount_micros == int(round(cm["daily_budget"] * 1e6)):
            existing[key] = f"customers/{CID}/campaignBudgets/{g.campaign_budget.id}"
            break
if len(existing) == len(plan["campaigns"]):
    budgets = existing
    rec["committed"]["campaign_budgets"] = budgets
    rec["committed"]["campaign_budgets_reused_from_aborted_run"] = True
    rec["stages"].append({"stage": "budgets", "ok": True, "reused": True,
                          "resources": budgets})
    for k, v in budgets.items():
        print(f"  REUSED {k:8s} {v}  ${plan['campaigns'][k]['daily_budget']}/day "
              f"(committed by the aborted first attempt - NOT duplicated)")
    save()
else:
    bops, keys = [], []
    for key, cm in plan["campaigns"].items():
        o = c.get_type("CampaignBudgetOperation"); b = o.create
        b.name = f"Budget | {cm['name']}"
        b.amount_micros = int(round(cm["daily_budget"] * 1e6))
        b.explicitly_shared = False
        b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
        bops.append(o); keys.append(key)
    try:
        r = c.get_service("CampaignBudgetService").mutate_campaign_budgets(
            customer_id=CID, operations=bops)
        budgets = {k: res.resource_name for k, res in zip(keys, r.results)}
    except Exception as ex:
        die(f"budget mutate failed (nothing committed): {str(ex)[:600]}")
    rec["committed"]["campaign_budgets"] = budgets
    rec["stages"].append({"stage": "budgets", "ok": True, "resources": budgets})
    for k, v in budgets.items():
        print(f"  {k:8s} {v}  ${plan['campaigns'][k]['daily_budget']}/day")
    save()

# ---------------------------------------------------------------- 2. campaigns
print("\n=== STAGE 2: CAMPAIGNS, STATUS=PAUSED (2) ===")
cops = []
for key, cm in plan["campaigns"].items():
    o = c.get_type("CampaignOperation"); x = o.create
    x.name = cm["name"]
    x.status = c.enums.CampaignStatusEnum.PAUSED
    x.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.SEARCH
    x.campaign_budget = budgets[key]
    x.target_spend.cpc_bid_ceiling_micros = int(round(cm["cpc_ceiling"] * 1e6))
    x.network_settings.target_google_search = True
    x.network_settings.target_search_network = False
    x.network_settings.target_content_network = False
    x.network_settings.target_partner_search_network = False
    x.geo_target_type_setting.positive_geo_target_type = \
        c.enums.PositiveGeoTargetTypeEnum.PRESENCE
    x.geo_target_type_setting.negative_geo_target_type = \
        c.enums.NegativeGeoTargetTypeEnum.PRESENCE
    # MANDATORY platform field discovered at execution: Google now rejects every new
    # campaign without an EU political-advertising declaration (field_error REQUIRED on
    # contains_eu_political_advertising). There is exactly one truthful value for an HVAC
    # service campaign in Central Maryland, and it mirrors all five existing Ambient
    # campaigns. No effect on budget, bid, targeting, status or delivery.
    x.contains_eu_political_advertising = (
        c.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
    cops.append(o)
try:
    r = c.get_service("CampaignService").mutate_campaigns(customer_id=CID, operations=cops)
    camps = {k: res.resource_name for k, res in zip(plan["campaigns"], r.results)}
except Exception as ex:
    die(f"campaign mutate failed: {str(ex)[:600]}")
rec["committed"]["campaigns"] = camps
rec["stages"].append({"stage": "campaigns", "ok": True, "resources": camps})
for k, v in camps.items():
    print(f"  {k:8s} {v}  PAUSED  ceiling ${plan['campaigns'][k]['cpc_ceiling']}")
save()

# ---------------------------------------------------------------- 3. campaign criteria
print("\n=== STAGE 3: CAMPAIGN CRITERIA (150 geo + 12 schedule + 47 negatives = 209) ===")
crops = []
for key, crn in camps.items():
    for g in GEO:
        o = c.get_type("CampaignCriterionOperation"); x = o.create
        x.campaign = crn
        x.location.geo_target_constant = f"geoTargetConstants/{g}"
        crops.append(o)
    for s in SCHED:
        o = c.get_type("CampaignCriterionOperation"); x = o.create
        x.campaign = crn
        x.ad_schedule.day_of_week = DAY[s["day"]]
        x.ad_schedule.start_hour = s["start"]
        x.ad_schedule.start_minute = c.enums.MinuteOfHourEnum.ZERO
        x.ad_schedule.end_hour = s["end"]
        x.ad_schedule.end_minute = c.enums.MinuteOfHourEnum.ZERO
        crops.append(o)
    negs = list(plan["campaign_negatives"]) + list(plan["cross_negatives"][key])
    for n in negs:
        o = c.get_type("CampaignCriterionOperation"); x = o.create
        x.campaign = crn
        x.negative = True
        x.keyword.text = n["text"]
        x.keyword.match_type = MT[n["match"]]
        crops.append(o)
print(f"  built {len(crops)} campaign criterion operations")
try:
    r = c.get_service("CampaignCriterionService").mutate_campaign_criteria(
        customer_id=CID, operations=crops)
    crits = [res.resource_name for res in r.results]
except Exception as ex:
    die(f"campaign criterion mutate failed: {str(ex)[:600]}")
rec["committed"]["campaign_criteria_count"] = len(crits)
rec["stages"].append({"stage": "campaign_criteria", "ok": True, "count": len(crits)})
print(f"  EXECUTED_OK: {len(crits)} criteria")
save()

# ---------------------------------------------------------------- 4. ad groups
print("\n=== STAGE 4: AD GROUPS, STATUS=PAUSED (2) ===")
aops, anames = [], []
for a in plan["ad_groups"]:
    o = c.get_type("AdGroupOperation"); x = o.create
    x.name = a["name"]
    x.campaign = camps[a["campaign"]]
    x.status = c.enums.AdGroupStatusEnum.PAUSED
    x.type_ = c.enums.AdGroupTypeEnum.SEARCH_STANDARD
    x.cpc_bid_micros = int(round(a["cpc_bid"] * 1e6))
    aops.append(o); anames.append(a["name"])
try:
    r = c.get_service("AdGroupService").mutate_ad_groups(customer_id=CID, operations=aops)
    ags = {n: res.resource_name for n, res in zip(anames, r.results)}
except Exception as ex:
    die(f"ad group mutate failed: {str(ex)[:600]}")
rec["committed"]["ad_groups"] = ags
rec["stages"].append({"stage": "ad_groups", "ok": True, "resources": ags})
for k, v in ags.items():
    print(f"  {v}  PAUSED  {k}")
save()

# ---------------------------------------------------------------- 5. keywords
print("\n=== STAGE 5: KEYWORDS, STATUS=PAUSED (18) ===")
kops = []
for a in plan["ad_groups"]:
    for t in a["phrase"]:
        o = c.get_type("AdGroupCriterionOperation"); x = o.create
        x.ad_group = ags[a["name"]]
        x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
        x.keyword.text = t; x.keyword.match_type = MT["PHRASE"]
        kops.append(o)
    for t in a["exact"]:
        o = c.get_type("AdGroupCriterionOperation"); x = o.create
        x.ad_group = ags[a["name"]]
        x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
        x.keyword.text = t; x.keyword.match_type = MT["EXACT"]
        kops.append(o)
try:
    r = c.get_service("AdGroupCriterionService").mutate_ad_group_criteria(
        customer_id=CID, operations=kops)
    kws = [res.resource_name for res in r.results]
except Exception as ex:
    die(f"keyword mutate failed: {str(ex)[:600]}")
rec["committed"]["keywords"] = kws
rec["stages"].append({"stage": "keywords", "ok": True, "count": len(kws)})
print(f"  EXECUTED_OK: {len(kws)} keywords, all PAUSED")
save()

# ---------------------------------------------------------------- 6. RSAs
print("\n=== STAGE 6: RSAs, STATUS=PAUSED (4) ===")
rops, rlabels = [], []
for o_ in plan["operations"]:
    if o_["op"] != "CREATE_RSA_PAUSED":
        continue
    o = c.get_type("AdGroupAdOperation"); a = o.create
    a.ad_group = ags[o_["ad_group"]]
    a.status = c.enums.AdGroupAdStatusEnum.PAUSED
    a.ad.final_urls.append(o_["final_url"])
    r_ = a.ad.responsive_search_ad
    r_.path1, r_.path2 = o_["path1"], o_["path2"]
    for h in o_["headlines_pinned_h1"]:
        t = c.get_type("AdTextAsset"); t.text = h
        t.pinned_field = c.enums.ServedAssetFieldTypeEnum.HEADLINE_1
        r_.headlines.append(t)
    for h in o_["headlines_unpinned"]:
        t = c.get_type("AdTextAsset"); t.text = h; r_.headlines.append(t)
    for dsc in o_["descriptions"]:
        t = c.get_type("AdTextAsset"); t.text = dsc; r_.descriptions.append(t)
    rops.append(o); rlabels.append(f"{o_['ad_group']} :: {o_['label']}")
try:
    r = c.get_service("AdGroupAdService").mutate_ad_group_ads(customer_id=CID,
                                                             operations=rops)
    rsas = {lbl: res.resource_name for lbl, res in zip(rlabels, r.results)}
except Exception as ex:
    die(f"RSA mutate failed: {str(ex)[:800]}")
rec["committed"]["rsas"] = rsas
rec["stages"].append({"stage": "rsas", "ok": True, "resources": rsas})
for k, v in rsas.items():
    print(f"  {v}  PAUSED  {k[:60]}")
save()

# ---------------------------------------------------------------- 7. assets
print("\n=== STAGE 7: ASSETS (5 callouts + 1 snippet + 3 sitelinks = 9) ===")
asops, asmeta = [], []
for t in plan["callouts"]:
    o = c.get_type("AssetOperation"); a = o.create
    a.callout_asset.callout_text = t
    a.name = f"GM | Heating | Callout | {t}"
    asops.append(o); asmeta.append(("CALLOUT", t))
sn = plan["structured_snippet"]
o = c.get_type("AssetOperation"); a = o.create
a.structured_snippet_asset.header = sn["header"]
a.structured_snippet_asset.values.extend(sn["values"])
a.name = "GM | Heating | Snippet | Services"
asops.append(o); asmeta.append(("STRUCTURED_SNIPPET", sn["header"]))
for s in plan["sitelinks"]:
    o = c.get_type("AssetOperation"); a = o.create
    a.sitelink_asset.link_text = s["text"]
    a.sitelink_asset.description1 = s["d1"]
    a.sitelink_asset.description2 = s["d2"]
    a.final_urls.append(s["url"])
    a.name = f"GM | Heating | Sitelink | {s['text']}"
    asops.append(o); asmeta.append(("SITELINK", s["text"]))
try:
    r = c.get_service("AssetService").mutate_assets(customer_id=CID, operations=asops)
    assets = [(m[0], m[1], res.resource_name) for m, res in zip(asmeta, r.results)]
except Exception as ex:
    die(f"asset mutate failed: {str(ex)[:600]}")
rec["committed"]["assets"] = [{"type": t, "label": l, "resource": rn}
                              for t, l, rn in assets]
rec["stages"].append({"stage": "assets", "ok": True, "count": len(assets)})
for t, l, rn in assets:
    print(f"  {rn}  {t:20s} {l}")
save()

# ---------------------------------------------------------------- 8. asset links
print("\n=== STAGE 8: CAMPAIGN ASSET LINKS, STATUS=PAUSED (22) ===")
FT = {"CALLOUT": c.enums.AssetFieldTypeEnum.CALLOUT,
      "STRUCTURED_SNIPPET": c.enums.AssetFieldTypeEnum.STRUCTURED_SNIPPET,
      "SITELINK": c.enums.AssetFieldTypeEnum.SITELINK,
      "CALL": c.enums.AssetFieldTypeEnum.CALL,
      "BUSINESS_NAME": c.enums.AssetFieldTypeEnum.BUSINESS_NAME}
lops, lmeta = [], []
for key, crn in camps.items():
    for t, l, rn in assets:
        o = c.get_type("CampaignAssetOperation"); x = o.create
        x.campaign = crn; x.asset = rn; x.field_type = FT[t]
        x.status = c.enums.AssetLinkStatusEnum.PAUSED
        lops.append(o); lmeta.append(f"{key}:{t}:{l}")
    for aid, ft in (("407995613637", "CALL"), ("80516971145", "BUSINESS_NAME")):
        o = c.get_type("CampaignAssetOperation"); x = o.create
        x.campaign = crn
        x.asset = c.get_service("AssetService").asset_path(CID, aid)
        x.field_type = FT[ft]
        x.status = c.enums.AssetLinkStatusEnum.PAUSED
        lops.append(o); lmeta.append(f"{key}:{ft}:REUSE {aid}")
print(f"  built {len(lops)} campaign asset links, all PAUSED")
try:
    r = c.get_service("CampaignAssetService").mutate_campaign_assets(
        customer_id=CID, operations=lops)
    links = [res.resource_name for res in r.results]
except Exception as ex:
    die(f"campaign asset link mutate failed: {str(ex)[:800]}")
rec["committed"]["campaign_asset_links"] = len(links)
rec["stages"].append({"stage": "asset_links", "ok": True, "count": len(links)})
print(f"  EXECUTED_OK: {len(links)} links, all PAUSED")

rec["finished"] = datetime.datetime.now(TZ).isoformat()
rec["raw_resources_created"] = (len(budgets) + len(camps) + len(crits) + len(ags)
                                + len(kws) + len(rsas) + len(assets) + len(links))
save()
print(f"\nTOTAL RAW RESOURCES CREATED: {rec['raw_resources_created']} (expected 268)")
print("EVERYTHING PAUSED. NOTHING ENABLED.")
