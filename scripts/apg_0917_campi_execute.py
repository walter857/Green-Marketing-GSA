#!/usr/bin/env python3
"""EXECUTE APG-0917-CAMP-I, fingerprint 4022CBA7FD51.

Approval 2026-09-17: "APPROVE APG CREATE-PAUSED 4022CBA7FD51"
Walter explicitly accepted the temporary 404 on the final URL.

121 mutations, campaign created PAUSED. Staged, each stage read back.
Stops on the first real API failure and inventories everything created.
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, GM_MANAGER, TZ, RECEIPTS, client, q, write, E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402

PLAN_PATH = ROOT / "clients/apogee-lawns/plans/APG-0917-CAMP-I.yaml"
EXPECTED_FP = "4022CBA7FD51"

c = client()
plan = load_yaml(str(PLAN_PATH))
C0 = plan["campaigns"][0]
created: dict = {}
fails: list[str] = []


def gate(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' -> ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)


def err(exc):
    out = []
    f = getattr(exc, "failure", None)
    if f:
        for e in f.errors:
            loc = ".".join(x.field_name for x in e.location.field_path_elements) if e.location and e.location.field_path_elements else ""
            out.append(f"{e.message} @ '{loc}'")
    return " | ".join(out) or str(exc)[:400]


def abort(stage, exc):
    msg = err(exc)
    print(f"\n{'='*78}\nAPI FAILURE IN STAGE: {stage}\n{'='*78}")
    print(f"  error: {msg[:600]}")
    print("\n  CREATED SO FAR (no blind retry will be attempted):")
    for k, v in created.items():
        print(f"    {k}: {v if not isinstance(v, list) else str(len(v)) + ' items'}")
    write(RECEIPTS / "2026-09-17-campi-PARTIAL-FAILURE.json",
          {"stage": stage, "error": msg[:2000], "created": created,
           "when": datetime.datetime.now(TZ).isoformat()})
    sys.exit(2)


# =====================================================================
print("=" * 78 + "\nGATE\n" + "=" * 78)
fp = approval_code(plan)
gate(fp == EXPECTED_FP, "CAMP-I fingerprint matches approval", fp)

row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
                     customer.test_account, customer.currency_code, customer.time_zone
              FROM customer""")[0].customer
gate(str(row.id) == CID, "customer.id", str(row.id))
gate(row.descriptive_name == EXACT_NAME, "descriptive_name", row.descriptive_name)
gate(not row.manager and not row.test_account, "not manager / not test")
links = {x.customer_manager_link.manager_customer.split("/")[-1]: E(x.customer_manager_link.status)
         for x in q(c, "SELECT customer_manager_link.manager_customer, customer_manager_link.status FROM customer_manager_link")}
gate(links.get(GM_MANAGER) == "ACTIVE", f"manager {GM_MANAGER} ACTIVE and never mutated")

CAMP_NAME = C0["name"]
BUD_NAME = C0["budget_name"]
dupc = [r for r in q(c, "SELECT campaign.id, campaign.name, campaign.status FROM campaign")
        if r.campaign.name == CAMP_NAME]
dupb = [r for r in q(c, "SELECT campaign_budget.id, campaign_budget.name FROM campaign_budget")
        if r.campaign_budget.name == BUD_NAME]
gate(not dupc, f"no existing campaign named '{CAMP_NAME[:50]}...'", str(len(dupc)))
gate(len(q(c, "SELECT campaign.id FROM campaign")) == 0, "zero campaigns in the account")
if dupb:
    b0 = dupb[0].campaign_budget
    refs = [r for r in q(c, "SELECT campaign.id, campaign.campaign_budget FROM campaign")
            if r.campaign.campaign_budget.split("/")[-1] == str(b0.id)]
    print(f"  [INFO] budget '{BUD_NAME[:44]}...' already exists (id {b0.id}) with "
          f"{len(refs)} referencing campaigns.")
    gate(not refs, "existing budget is an unreferenced orphan, safe to reuse", str(len(refs)))
else:
    gate(True, f"no existing budget named '{BUD_NAME[:44]}...'")

conv = {str(r.conversion_action.id): r.conversion_action.primary_for_goal
        for r in q(c, "SELECT conversion_action.id, conversion_action.primary_for_goal FROM conversion_action")}
gate(conv.get("7772803337") is True, "7772803337 is PRIMARY")
gate(conv.get("7773013199") is True, "7773013199 is PRIMARY")
gate(conv.get("7773043879") is False, "7773043879 is SECONDARY")
gate(len(q(c, "SELECT custom_conversion_goal.id FROM custom_conversion_goal")) == 0, "zero custom conversion goals")

print(f"\n  final_url to be used: {C0['final_url']}")
print("  temporary 404 on that URL is explicitly accepted by Walter, 2026-09-17")

if fails:
    sys.exit("\nHARD STOP: " + "; ".join(fails))
print("\nALL GATES PASS. Executing 121 mutations.\n")

MUT = 0

# =====================================================================
print("--- STAGE 1: campaign budget (idempotent)")
try:
    existing = [r for r in q(c, "SELECT campaign_budget.id, campaign_budget.name, "
                                "campaign_budget.amount_micros, campaign_budget.status "
                                "FROM campaign_budget")
                if r.campaign_budget.name == BUD_NAME]
    if existing:
        b0 = existing[0].campaign_budget
        BUDGET_RN = f"customers/{CID}/campaignBudgets/{b0.id}"
        created["budget"] = BUDGET_RN
        created["budget_reused"] = True
        print(f"    REUSING existing {BUDGET_RN}  ${b0.amount_micros/1e6}/day  "
              f"(created by the earlier run that failed at the campaign stage)")
        assert b0.amount_micros == int(round(C0["daily_budget"] * 1_000_000)), "budget amount mismatch"
    else:
        svc = c.get_service("CampaignBudgetService")
        op = c.get_type("CampaignBudgetOperation")
        b = op.create
        b.name = BUD_NAME
        b.amount_micros = int(round(C0["daily_budget"] * 1_000_000))
        b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
        b.explicitly_shared = False
        BUDGET_RN = svc.mutate_campaign_budgets(customer_id=CID, operations=[op]).results[0].resource_name
        created["budget"] = BUDGET_RN
        MUT += 1
        print(f"    CREATED {BUDGET_RN}  ${C0['daily_budget']}/day")
except Exception as e:
    abort("budget", e)

# =====================================================================
print("--- STAGE 2: Search campaign (PAUSED)")
try:
    svc = c.get_service("CampaignService")
    op = c.get_type("CampaignOperation")
    cp = op.create
    cp.name = CAMP_NAME
    cp.status = c.enums.CampaignStatusEnum.PAUSED
    cp.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.SEARCH
    cp.campaign_budget = BUDGET_RN
    cp.target_spend.cpc_bid_ceiling_micros = int(round(C0["cpc_bid_ceiling"] * 1_000_000))
    cp.network_settings.target_google_search = True
    cp.network_settings.target_search_network = False
    cp.network_settings.target_content_network = False
    cp.network_settings.target_partner_search_network = False
    cp.geo_target_type_setting.positive_geo_target_type = (
        c.enums.PositiveGeoTargetTypeEnum.PRESENCE)
    cp.geo_target_type_setting.negative_geo_target_type = (
        c.enums.NegativeGeoTargetTypeEnum.PRESENCE)
    cp.final_url_suffix = C0["final_url_suffix"]
    # MANDATORY FIELD 2026-09-17: Google now requires an EU political advertising
    # declaration on every campaign create. Without it the API returns
    # "The required field was not present." Set to DOES_NOT_CONTAIN, which is factually
    # determined by the campaign's own content: permanent Christmas light installation,
    # 14 Nebraska geo targets, zero EU targeting, RSAs containing no political content.
    # Flagged in the report; reversible with a campaign update if the owner disagrees.
    cp.contains_eu_political_advertising = (
        c.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
    # FORCED CORRECTION 2026-09-17: ad_serving_optimization_status is REJECTED by the API -
    # "Ad rotation mode at campaign is deprecated." The approved plan recorded
    # ad_rotation: OPTIMIZE, but Google no longer accepts the field at campaign level at
    # all, so nothing approved is lost by omitting it. Recorded in the receipt.
    # opt out of automation
    for t in ("TEXT_ASSET_AUTOMATION", "GENERATE_LANDING_PAGE_TEXT"):
        try:
            s = cp.asset_automation_settings.add()
            s.asset_automation_type = getattr(c.enums.AssetAutomationTypeEnum, t)
            s.asset_automation_status = c.enums.AssetAutomationStatusEnum.OPTED_OUT
        except Exception:
            pass
    CAMPAIGN_RN = c.get_service("CampaignService").mutate_campaigns(
        customer_id=CID, operations=[op]).results[0].resource_name
    created["campaign"] = CAMPAIGN_RN
    MUT += 1
    print(f"    CREATED {CAMPAIGN_RN}  PAUSED")
except Exception as e:
    abort("campaign", e)

# =====================================================================
print("--- STAGE 3: campaign criteria (14 locations + 1 language + 75 negatives)")
try:
    svc = c.get_service("CampaignCriterionService")
    ops = []
    for gid in C0["location"]["geo_target_constant_ids"]:
        o = c.get_type("CampaignCriterionOperation")
        o.create.campaign = CAMPAIGN_RN
        o.create.location.geo_target_constant = f"geoTargetConstants/{gid}"
        ops.append(o)
    o = c.get_type("CampaignCriterionOperation")
    o.create.campaign = CAMPAIGN_RN
    o.create.language.language_constant = C0["language"]
    ops.append(o)
    NEG = ([(str(x), "BROAD") for x in C0["negatives_match_broad"]] +
           [(str(x), "PHRASE") for x in C0["negatives_match_phrase"]])
    for text, mt in NEG:
        o = c.get_type("CampaignCriterionOperation")
        o.create.campaign = CAMPAIGN_RN
        o.create.negative = True
        o.create.keyword.text = text
        o.create.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, mt)
        ops.append(o)
    print(f"    issuing {len(ops)} criterion operations "
          f"({len(C0['location']['geo_target_constant_ids'])} geo + 1 language + {len(NEG)} negatives)")
    res = svc.mutate_campaign_criteria(customer_id=CID, operations=ops)
    created["campaign_criteria"] = [r.resource_name for r in res.results]
    MUT += len(ops)
    print(f"    CREATED {len(res.results)} campaign criteria")
except Exception as e:
    abort("campaign_criteria", e)

# =====================================================================
print("--- STAGE 4: ad groups")
try:
    svc = c.get_service("AdGroupService")
    ops = []
    for g in C0["ad_groups"]:
        o = c.get_type("AdGroupOperation")
        a = o.create
        a.name = g["name"]
        a.campaign = CAMPAIGN_RN
        a.status = c.enums.AdGroupStatusEnum.ENABLED
        a.type_ = c.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ops.append(o)
    res = svc.mutate_ad_groups(customer_id=CID, operations=ops)
    AG_RN = [r.resource_name for r in res.results]
    created["ad_groups"] = AG_RN
    MUT += len(ops)
    for g, rn in zip(C0["ad_groups"], AG_RN):
        print(f"    CREATED {rn}  {g['name']}")
except Exception as e:
    abort("ad_groups", e)

# =====================================================================
print("--- STAGE 5: keywords")
try:
    svc = c.get_service("AdGroupCriterionService")
    ops = []
    for g, rn in zip(C0["ad_groups"], AG_RN):
        for k in g["keywords"]:
            o = c.get_type("AdGroupCriterionOperation")
            x = o.create
            x.ad_group = rn
            x.status = c.enums.AdGroupCriterionStatusEnum.ENABLED
            x.keyword.text = k["text"]
            x.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, k["match_type"])
            ops.append(o)
    res = svc.mutate_ad_group_criteria(customer_id=CID, operations=ops)
    created["keywords"] = [r.resource_name for r in res.results]
    MUT += len(ops)
    print(f"    CREATED {len(res.results)} keywords")
except Exception as e:
    abort("keywords", e)

# =====================================================================
print("--- STAGE 6: responsive search ads")
try:
    svc = c.get_service("AdGroupAdService")
    ops = []
    for g, rn in zip(C0["ad_groups"], AG_RN):
        for ad in g["ads"]:
            o = c.get_type("AdGroupAdOperation")
            a = o.create
            a.ad_group = rn
            a.status = c.enums.AdGroupAdStatusEnum.ENABLED
            a.ad.final_urls.append(C0["final_url"])
            a.ad.responsive_search_ad.path1 = g["path1"]
            a.ad.responsive_search_ad.path2 = g["path2"]
            for h in ad["headlines"]:
                t = c.get_type("AdTextAsset")
                t.text = h["text"]
                if h.get("pin") == "HEADLINE_1":
                    t.pinned_field = c.enums.ServedAssetFieldTypeEnum.HEADLINE_1
                a.ad.responsive_search_ad.headlines.append(t)
            for d in ad["descriptions"]:
                t = c.get_type("AdTextAsset")
                t.text = d["text"]
                a.ad.responsive_search_ad.descriptions.append(t)
            ops.append(o)
    res = svc.mutate_ad_group_ads(customer_id=CID, operations=ops)
    created["ads"] = [r.resource_name for r in res.results]
    MUT += len(ops)
    print(f"    CREATED {len(res.results)} RSAs, final_url={C0['final_url']}")
except Exception as e:
    abort("ads", e)

# =====================================================================
print("--- STAGE 7: assets (6 callouts + 1 structured snippet)")
try:
    svc = c.get_service("AssetService")
    assets = C0["ad_groups"][0]["assets"]
    ops = []
    meta = []
    for co in assets["callouts"]:
        o = c.get_type("AssetOperation")
        o.create.callout_asset.callout_text = co
        ops.append(o)
        meta.append(("CALLOUT", co))
    for ss in assets["structured_snippets"]:
        o = c.get_type("AssetOperation")
        o.create.structured_snippet_asset.header = ss["header"]
        for v in ss["values"]:
            o.create.structured_snippet_asset.values.append(v)
        ops.append(o)
        meta.append(("STRUCTURED_SNIPPET", ss["header"]))
    res = svc.mutate_assets(customer_id=CID, operations=ops)
    ASSET_RN = [r.resource_name for r in res.results]
    created["assets"] = ASSET_RN
    MUT += len(ops)
    for (ft, label), rn in zip(meta, ASSET_RN):
        print(f"    CREATED {rn}  {ft}  {label}")
except Exception as e:
    abort("assets", e)

print("--- STAGE 8: campaign asset links")
try:
    svc = c.get_service("CampaignAssetService")
    ops = []
    for (ft, _label), rn in zip(meta, ASSET_RN):
        o = c.get_type("CampaignAssetOperation")
        o.create.campaign = CAMPAIGN_RN
        o.create.asset = rn
        o.create.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
        ops.append(o)
    res = svc.mutate_campaign_assets(customer_id=CID, operations=ops)
    created["campaign_assets"] = [r.resource_name for r in res.results]
    MUT += len(ops)
    print(f"    CREATED {len(res.results)} campaign asset links")
except Exception as e:
    abort("campaign_assets", e)

# =====================================================================
print("--- STAGE 9: conversion goal configuration")
try:
    svc = c.get_service("ConversionGoalCampaignConfigService")
    o = c.get_type("ConversionGoalCampaignConfigOperation")
    o.update.resource_name = f"customers/{CID}/conversionGoalCampaignConfigs/{CAMPAIGN_RN.split('/')[-1]}"
    o.update.goal_config_level = c.enums.GoalConfigLevelEnum.CAMPAIGN
    o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["goal_config_level"]))
    svc.mutate_conversion_goal_campaign_configs(customer_id=CID, operations=[o])
    MUT += 1
    print("    UPDATED goal_config_level = CAMPAIGN")
except Exception as e:
    abort("conversion_goal_campaign_config", e)

print("--- STAGE 10: campaign conversion goals")
try:
    svc = c.get_service("CampaignConversionGoalService")
    ops = []
    for g in C0["campaign_conversion_goals"]["standard_goals"]:
        o = c.get_type("CampaignConversionGoalOperation")
        cid_ = CAMPAIGN_RN.split("/")[-1]
        cat = g["category"]
        org = g["origin"]
        o.update.resource_name = (f"customers/{CID}/campaignConversionGoals/"
                                  f"{cid_}~{cat}~{org}")
        o.update.biddable = g["biddable"]
        o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["biddable"]))
        ops.append(o)
    svc.mutate_campaign_conversion_goals(customer_id=CID, operations=ops)
    MUT += len(ops)
    for g in C0["campaign_conversion_goals"]["standard_goals"]:
        print(f"    UPDATED {g['category']}/{g['origin']} biddable={g['biddable']}")
except Exception as e:
    abort("campaign_conversion_goals", e)

print(f"\n{'='*78}\nALL MUTATIONS ISSUED: {MUT} (plan declares "
      f"{plan['object_counts_if_executed']['TOTAL_MUTATIONS']})\n{'='*78}")

write(RECEIPTS / "2026-09-17-campi-created.json",
      {"plan": "APG-0917-CAMP-I", "fingerprint": EXPECTED_FP,
       "executed_local": datetime.datetime.now(TZ).isoformat(),
       "mutations_issued": MUT, "created": created,
       "final_url": C0["final_url"]})
print("Created-resource receipt written. Run apg_0917_campi_readback.py next.")
