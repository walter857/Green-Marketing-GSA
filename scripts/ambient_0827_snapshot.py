#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | full read-only structural snapshot.

Covers identity, campaigns, budgets, bidding, schedules, locations, ad groups,
keywords, negatives at every level, shared sets, RSAs, assets, conversion
actions, campaign goals and tracking. NO mutation.
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, EXACT_NAME, FIVE, IN5, NAME, SNAP, TZ,
    client, q, identity_gate, E, write,
)

STAMP = "2026-08-27"


def main():
    c = client()
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "read_only": True}

    print("== IDENTITY GATE ==")
    out["identity"] = identity_gate(c)

    print("\n== CAMPAIGNS ==")
    camps = []
    for r in q(c, """
        SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
               campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
               campaign.start_date_time, campaign.end_date_time,
               campaign.primary_status, campaign.primary_status_reasons,
               campaign.ai_max_setting.enable_ai_max,
               campaign.asset_automation_settings,
               campaign.dynamic_search_ads_setting.use_supplied_urls_only,
               campaign.network_settings.target_google_search,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.network_settings.target_partner_search_network,
               campaign.bidding_strategy_type, campaign.bidding_strategy,
               campaign.maximize_conversions.target_cpa_micros,
               campaign.maximize_conversion_value.target_roas,
               campaign.target_cpa.target_cpa_micros,
               campaign.target_spend.cpc_bid_ceiling_micros,
               campaign.manual_cpc.enhanced_cpc_enabled,
               campaign.percent_cpc.cpc_bid_ceiling_micros,
               campaign.campaign_budget, campaign.optimization_score,
               campaign.geo_target_type_setting.positive_geo_target_type,
               campaign.geo_target_type_setting.negative_geo_target_type,
               campaign.tracking_url_template, campaign.final_url_suffix,
               campaign.dynamic_search_ads_setting.domain_name,
               campaign.ad_serving_optimization_status,
               campaign.payment_mode, campaign.experiment_type,
               campaign.optimization_goal_setting.optimization_goal_types
        FROM campaign WHERE campaign.status != 'REMOVED'
    """):
        x = r.campaign
        camps.append({
            "id": str(x.id), "name": x.name, "status": E(x.status),
            "serving_status": E(x.serving_status),
            "channel": E(x.advertising_channel_type),
            "sub_type": E(x.advertising_channel_sub_type),
            "start": x.start_date_time, "end": x.end_date_time,
            "primary_status": E(x.primary_status),
            "primary_status_reasons": [E(z) for z in x.primary_status_reasons],
            "ai_max_enabled": x.ai_max_setting.enable_ai_max,
            "asset_automation_settings": [
                {"type": E(z.asset_automation_type), "status": E(z.asset_automation_status)}
                for z in x.asset_automation_settings],
            "dsa_use_supplied_urls_only": x.dynamic_search_ads_setting.use_supplied_urls_only,
            "ad_serving_optimization_status": E(x.ad_serving_optimization_status),
            "net_google_search": x.network_settings.target_google_search,
            "net_search_partners": x.network_settings.target_search_network,
            "net_display": x.network_settings.target_content_network,
            "net_partner_search": x.network_settings.target_partner_search_network,
            "bidding_strategy_type": E(x.bidding_strategy_type),
            "portfolio_strategy": x.bidding_strategy or "",
            "maxconv_target_cpa_micros": x.maximize_conversions.target_cpa_micros,
            "target_spend_cpc_ceiling_micros": x.target_spend.cpc_bid_ceiling_micros,
            "budget_resource": x.campaign_budget,
            "budget_id": x.campaign_budget.split("/")[-1] if x.campaign_budget else "",
            "optimization_score": x.optimization_score,
            "positive_geo_target_type": E(x.geo_target_type_setting.positive_geo_target_type),
            "negative_geo_target_type": E(x.geo_target_type_setting.negative_geo_target_type),
            "tracking_url_template": x.tracking_url_template,
            "final_url_suffix": x.final_url_suffix,
            "dsa_domain": x.dynamic_search_ads_setting.domain_name,
            "payment_mode": E(x.payment_mode),
            "experiment_type": E(x.experiment_type),
        })
    out["campaigns"] = camps
    for x in sorted(camps, key=lambda z: z["name"]):
        print(f"  {x['id']} {x['status']:8s} {E and x['serving_status']:10s} "
              f"{x['bidding_strategy_type']:22s} {x['name']}")

    print("\n== BUDGETS ==")
    buds = []
    for r in q(c, """
        SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
               campaign_budget.total_amount_micros, campaign_budget.delivery_method,
               campaign_budget.explicitly_shared, campaign_budget.reference_count,
               campaign_budget.status, campaign_budget.period,
               campaign_budget.has_recommended_budget,
               campaign_budget.recommended_budget_amount_micros
        FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'
    """):
        x = r.campaign_budget
        buds.append({
            "id": str(x.id), "name": x.name,
            "amount": round(x.amount_micros / 1e6, 2), "amount_micros": x.amount_micros,
            "delivery": E(x.delivery_method), "explicitly_shared": x.explicitly_shared,
            "reference_count": x.reference_count, "status": E(x.status),
            "period": E(x.period),
            "recommended_micros": x.recommended_budget_amount_micros,
        })
    out["budgets"] = buds
    tot = 0.0
    for b in sorted(buds, key=lambda z: -z["amount"]):
        print(f"  {b['id']} ${b['amount']:>8.2f}/day shared={b['explicitly_shared']} "
              f"refs={b['reference_count']} {b['delivery']:9s} {b['name']}")
        tot += b["amount"]
    print(f"  TOTAL DAILY ACROSS NON-REMOVED BUDGETS: ${tot:,.2f}")
    out["total_daily_budget"] = round(tot, 2)

    print("\n== AD SCHEDULES (campaign criteria type AD_SCHEDULE) ==")
    sched = []
    for r in q(c, f"""
        SELECT campaign.id, campaign.name, campaign_criterion.criterion_id,
               campaign_criterion.ad_schedule.day_of_week,
               campaign_criterion.ad_schedule.start_hour,
               campaign_criterion.ad_schedule.start_minute,
               campaign_criterion.ad_schedule.end_hour,
               campaign_criterion.ad_schedule.end_minute,
               campaign_criterion.bid_modifier, campaign_criterion.status
        FROM campaign_criterion
        WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'AD_SCHEDULE'
              AND campaign_criterion.status != 'REMOVED'
    """):
        a = r.campaign_criterion.ad_schedule
        sched.append({
            "campaign": str(r.campaign.id), "criterion_id": str(r.campaign_criterion.criterion_id),
            "day": E(a.day_of_week), "start_hour": a.start_hour,
            "start_minute": E(a.start_minute), "end_hour": a.end_hour,
            "end_minute": E(a.end_minute),
            "bid_modifier": r.campaign_criterion.bid_modifier,
            "status": E(r.campaign_criterion.status),
        })
    out["ad_schedules"] = sched
    from collections import Counter
    cnt = Counter(s["campaign"] for s in sched)
    for cid in FIVE:
        rows = sorted([s for s in sched if s["campaign"] == cid], key=lambda z: z["day"])
        print(f"  {NAME[cid]:20s} rows={cnt[cid]}")
        for s in rows:
            print(f"     {s['day']:10s} {s['start_hour']:02d}:{s['start_minute']}"
                  f" - {s['end_hour']:02d}:{s['end_minute']}  mod={s['bid_modifier']}")

    print("\n== LOCATIONS ==")
    locs = []
    for r in q(c, f"""
        SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.negative,
               campaign_criterion.type, campaign_criterion.location.geo_target_constant,
               campaign_criterion.proximity.radius,
               campaign_criterion.proximity.geo_point.latitude_in_micro_degrees,
               campaign_criterion.proximity.geo_point.longitude_in_micro_degrees,
               campaign_criterion.status, campaign_criterion.bid_modifier
        FROM campaign_criterion
        WHERE campaign.id IN ({IN5})
              AND campaign_criterion.type IN ('LOCATION','PROXIMITY')
              AND campaign_criterion.status != 'REMOVED'
    """):
        x = r.campaign_criterion
        locs.append({
            "campaign": str(r.campaign.id), "criterion_id": str(x.criterion_id),
            "type": E(x.type_), "negative": x.negative,
            "geo_target": x.location.geo_target_constant.split("/")[-1] if x.location.geo_target_constant else "",
            "status": E(x.status), "bid_modifier": x.bid_modifier,
        })
    out["locations"] = locs
    for cid in FIVE:
        pos = [l for l in locs if l["campaign"] == cid and not l["negative"]]
        neg = [l for l in locs if l["campaign"] == cid and l["negative"]]
        print(f"  {NAME[cid]:20s} positive={len(pos)} excluded={len(neg)}")
    out["location_counts"] = {
        NAME[cid]: {
            "positive": len([l for l in locs if l["campaign"] == cid and not l["negative"]]),
            "excluded": len([l for l in locs if l["campaign"] == cid and l["negative"]]),
        } for cid in FIVE
    }

    print("\n== LANGUAGE / OTHER CAMPAIGN CRITERIA (non-keyword, non-location, non-schedule) ==")
    other = []
    for r in q(c, f"""
        SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.type,
               campaign_criterion.negative, campaign_criterion.status,
               campaign_criterion.language.language_constant,
               campaign_criterion.device.type,
               campaign_criterion.bid_modifier
        FROM campaign_criterion
        WHERE campaign.id IN ({IN5})
              AND campaign_criterion.type NOT IN ('KEYWORD','LOCATION','AD_SCHEDULE','PROXIMITY')
              AND campaign_criterion.status != 'REMOVED'
    """):
        x = r.campaign_criterion
        other.append({
            "campaign": str(r.campaign.id), "criterion_id": str(x.criterion_id),
            "type": E(x.type_), "negative": x.negative, "status": E(x.status),
            "language": x.language.language_constant.split("/")[-1] if x.language.language_constant else "",
            "device": E(x.device.type_) if x.device else "",
            "bid_modifier": x.bid_modifier,
        })
    out["other_campaign_criteria"] = other
    from collections import Counter as C2
    print("  ", dict(C2(o["type"] for o in other)))

    print("\n== AD GROUPS ==")
    ags = []
    for r in q(c, f"""
        SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group.type,
               ad_group.cpc_bid_micros, ad_group.target_cpa_micros,
               ad_group.tracking_url_template, ad_group.final_url_suffix
        FROM ad_group WHERE campaign.id IN ({IN5}) AND ad_group.status != 'REMOVED'
    """):
        x = r.ad_group
        ags.append({
            "campaign": str(r.campaign.id), "id": str(x.id), "name": x.name,
            "status": E(x.status), "type": E(x.type_),
            "cpc_bid": round(x.cpc_bid_micros / 1e6, 2) if x.cpc_bid_micros else 0,
            "tracking_url_template": x.tracking_url_template,
        })
    out["ad_groups"] = ags
    for a in sorted(ags, key=lambda z: (NAME.get(z["campaign"], ""), z["name"])):
        print(f"  {NAME.get(a['campaign']):20s} {a['id']} {a['status']:8s} {a['name']}")

    print("\n== POSITIVE KEYWORDS ==")
    kws = []
    for r in q(c, f"""
        SELECT campaign.id, ad_group.id, ad_group.name,
               ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               ad_group_criterion.negative, ad_group_criterion.system_serving_status,
               ad_group_criterion.approval_status, ad_group_criterion.quality_info.quality_score,
               ad_group_criterion.quality_info.creative_quality_score,
               ad_group_criterion.quality_info.post_click_quality_score,
               ad_group_criterion.quality_info.search_predicted_ctr,
               ad_group_criterion.effective_cpc_bid_micros,
               ad_group_criterion.position_estimates.first_page_cpc_micros,
               ad_group_criterion.position_estimates.top_of_page_cpc_micros,
               ad_group_criterion.final_urls
        FROM ad_group_criterion
        WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type = 'KEYWORD'
              AND ad_group_criterion.status != 'REMOVED'
    """):
        x = r.ad_group_criterion
        kws.append({
            "campaign": str(r.campaign.id), "ad_group": str(r.ad_group.id),
            "ad_group_name": r.ad_group.name, "criterion_id": str(x.criterion_id),
            "text": x.keyword.text, "match": E(x.keyword.match_type),
            "status": E(x.status), "negative": x.negative,
            "serving": E(x.system_serving_status), "approval": E(x.approval_status),
            "qs": x.quality_info.quality_score,
            "ad_relevance": E(x.quality_info.creative_quality_score),
            "lp_experience": E(x.quality_info.post_click_quality_score),
            "expected_ctr": E(x.quality_info.search_predicted_ctr),
            "effective_cpc_bid": round(x.effective_cpc_bid_micros / 1e6, 2) if x.effective_cpc_bid_micros else 0,
            "top_of_page_cpc": round(x.position_estimates.top_of_page_cpc_micros / 1e6, 2),
            "final_urls": list(x.final_urls),
        })
    out["keywords"] = kws
    pos = [k for k in kws if not k["negative"]]
    agneg = [k for k in kws if k["negative"]]
    print(f"  positive keywords (non-removed): {len(pos)}")
    print(f"  AD-GROUP-LEVEL negatives (non-removed): {len(agneg)}")
    for cid in FIVE:
        cp = [k for k in pos if k["campaign"] == cid]
        print(f"  {NAME[cid]:20s} {len(cp)} positive")
        for k in sorted(cp, key=lambda z: (z["ad_group_name"], z["match"], z["text"])):
            print(f"     [{k['match'][:6]:6s}] {k['text']:38s} {k['status']:8s} "
                  f"{k['serving']:22s} QS={k['qs'] or '-'} "
                  f"rel={k['ad_relevance']} lp={k['lp_experience']} ctr={k['expected_ctr']}")

    print("\n== CAMPAIGN-LEVEL NEGATIVE KEYWORDS ==")
    cneg = []
    for r in q(c, f"""
        SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.keyword.text,
               campaign_criterion.keyword.match_type, campaign_criterion.negative,
               campaign_criterion.status, campaign_criterion.resource_name
        FROM campaign_criterion
        WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'KEYWORD'
              AND campaign_criterion.status != 'REMOVED'
    """):
        x = r.campaign_criterion
        cneg.append({
            "campaign": str(r.campaign.id), "criterion_id": str(x.criterion_id),
            "text": x.keyword.text, "match": E(x.keyword.match_type),
            "negative": x.negative, "status": E(x.status),
            "resource_name": x.resource_name,
        })
    out["campaign_level_negatives"] = cneg
    for cid in FIVE:
        rows = [n for n in cneg if n["campaign"] == cid]
        print(f"  {NAME[cid]:20s} {len(rows)}")
        for n in rows:
            print(f"     [{n['match']:6s}] {n['text']:20s} id={n['criterion_id']} neg={n['negative']}")

    print("\n== ACCOUNT-LEVEL NEGATIVE KEYWORDS ==")
    acct_neg = []
    for r in q(c, """
        SELECT customer_negative_criterion.id, customer_negative_criterion.type,
               customer_negative_criterion.ip_block.ip_address,
               customer_negative_criterion.placement.url,
               customer_negative_criterion.negative_keyword_list.shared_set
        FROM customer_negative_criterion
    """):
        x = r.customer_negative_criterion
        acct_neg.append({
            "id": str(x.id), "type": E(x.type_),
            "ip": x.ip_block.ip_address, "placement": x.placement.url,
            "negative_keyword_list": x.negative_keyword_list.shared_set,
        })
    out["account_level_negatives"] = acct_neg
    from collections import Counter as C0
    print("  ", dict(C0(a["type"] for a in acct_neg)))
    nkl = [a for a in acct_neg if a["type"] == "NEGATIVE_KEYWORD_LIST"]
    for a in nkl:
        print(f"     NEGATIVE_KEYWORD_LIST -> {a['negative_keyword_list']}")
    out["account_negative_counts"] = dict(C0(a["type"] for a in acct_neg))

    print("\n== SHARED SETS AND ASSOCIATIONS ==")
    sets = []
    for r in q(c, """
        SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status,
               shared_set.member_count, shared_set.reference_count
        FROM shared_set
    """):
        x = r.shared_set
        sets.append({"id": str(x.id), "name": x.name, "type": E(x.type_),
                     "status": E(x.status), "member_count": x.member_count,
                     "reference_count": x.reference_count})
    out["shared_sets"] = sets
    for s in sets:
        print(f"  {s['id']} {s['type']:32s} status={s['status']:8s} "
              f"members={s['member_count']} refs={s['reference_count']} {s['name']}")

    assoc = []
    for r in q(c, """
        SELECT campaign.id, campaign.name, campaign_shared_set.shared_set,
               campaign_shared_set.status
        FROM campaign_shared_set
    """):
        assoc.append({"campaign": str(r.campaign.id), "campaign_name": r.campaign.name,
                      "shared_set": r.campaign_shared_set.shared_set.split("/")[-1],
                      "status": E(r.campaign_shared_set.status)})
    out["campaign_shared_set_associations"] = assoc
    print(f"  campaign_shared_set rows: {len(assoc)}")
    for a in assoc:
        print(f"     {a['campaign']} <- set {a['shared_set']} ({a['status']}) {a['campaign_name']}")

    members = []
    for r in q(c, """
        SELECT shared_set.id, shared_set.name, shared_criterion.criterion_id,
               shared_criterion.type, shared_criterion.keyword.text,
               shared_criterion.keyword.match_type
        FROM shared_criterion
    """):
        members.append({"set": str(r.shared_set.id), "set_name": r.shared_set.name,
                        "criterion_id": str(r.shared_criterion.criterion_id),
                        "type": E(r.shared_criterion.type_),
                        "text": r.shared_criterion.keyword.text,
                        "match": E(r.shared_criterion.keyword.match_type)})
    out["shared_criteria"] = members
    print(f"  shared_criterion rows: {len(members)}")
    from collections import Counter as C3
    print("  ", dict(C3(x["set_name"] for x in members)))

    print("\n== ADS ==")
    ads = []
    for r in q(c, f"""
        SELECT campaign.id, ad_group.id, ad_group.name, ad_group_ad.ad.id,
               ad_group_ad.ad.type, ad_group_ad.status, ad_group_ad.policy_summary.approval_status,
               ad_group_ad.policy_summary.review_status,
               ad_group_ad.ad.final_urls, ad_group_ad.ad.responsive_search_ad.headlines,
               ad_group_ad.ad.responsive_search_ad.descriptions,
               ad_group_ad.ad.responsive_search_ad.path1,
               ad_group_ad.ad.responsive_search_ad.path2,
               ad_group_ad.ad_strength
        FROM ad_group_ad
        WHERE campaign.id IN ({IN5}) AND ad_group_ad.status != 'REMOVED'
    """):
        x = r.ad_group_ad
        rsa = x.ad.responsive_search_ad
        ads.append({
            "campaign": str(r.campaign.id), "ad_group": str(r.ad_group.id),
            "ad_group_name": r.ad_group.name, "ad_id": str(x.ad.id),
            "type": E(x.ad.type_), "status": E(x.status),
            "approval": E(x.policy_summary.approval_status),
            "review": E(x.policy_summary.review_status),
            "ad_strength": E(x.ad_strength),
            "final_urls": list(x.ad.final_urls),
            "path1": rsa.path1, "path2": rsa.path2,
            "headlines": [{"text": h.text, "pin": E(h.pinned_field)} for h in rsa.headlines],
            "descriptions": [{"text": d.text, "pin": E(d.pinned_field)} for d in rsa.descriptions],
        })
    out["ads"] = ads
    for cid in FIVE:
        rows = [a for a in ads if a["campaign"] == cid]
        en = [a for a in rows if a["status"] == "ENABLED"]
        print(f"  {NAME[cid]:20s} total={len(rows)} enabled={len(en)} "
              f"approval={sorted(set(a['approval'] for a in rows))}")
        for a in rows:
            print(f"     ad {a['ad_id']} {a['status']:8s} {a['approval']:20s} "
                  f"strength={a['ad_strength']:12s} url={a['final_urls']}")

    print("\n== ASSETS (campaign + account level) ==")
    assets = []
    for r in q(c, """
        SELECT asset.id, asset.type, asset.name, asset.final_urls,
               asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
               asset.sitelink_asset.description2,
               asset.callout_asset.callout_text,
               asset.structured_snippet_asset.header,
               asset.structured_snippet_asset.values,
               asset.call_asset.phone_number, asset.call_asset.country_code,
               asset.call_asset.call_conversion_action,
               asset.call_asset.call_conversion_reporting_state
        FROM asset WHERE asset.type IN ('SITELINK','CALLOUT','STRUCTURED_SNIPPET','CALL')
    """):
        x = r.asset
        assets.append({
            "id": str(x.id), "type": E(x.type_), "name": x.name,
            "final_urls": list(x.final_urls),
            "sitelink_text": x.sitelink_asset.link_text,
            "sitelink_d1": x.sitelink_asset.description1,
            "sitelink_d2": x.sitelink_asset.description2,
            "callout_text": x.callout_asset.callout_text,
            "snippet_header": x.structured_snippet_asset.header,
            "snippet_values": list(x.structured_snippet_asset.values),
            "call_phone": x.call_asset.phone_number,
            "call_country": x.call_asset.country_code,
            "call_conv_action": x.call_asset.call_conversion_action,
            "call_conv_state": E(x.call_asset.call_conversion_reporting_state),
        })
    out["assets"] = assets
    from collections import Counter as C4
    print("  ", dict(C4(a["type"] for a in assets)))
    for a in assets:
        if a["type"] == "CALL":
            print(f"     CALL asset {a['id']} phone={a['call_phone']} "
                  f"country={a['call_country']} state={a['call_conv_state']}")

    camp_assets = []
    for r in q(c, f"""
        SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type,
               campaign_asset.status
        FROM campaign_asset WHERE campaign.id IN ({IN5})
    """):
        camp_assets.append({"campaign": str(r.campaign.id),
                            "asset": r.campaign_asset.asset.split("/")[-1],
                            "field_type": E(r.campaign_asset.field_type),
                            "status": E(r.campaign_asset.status)})
    out["campaign_assets"] = camp_assets
    for cid in FIVE:
        rows = [x for x in camp_assets if x["campaign"] == cid and x["status"] != "REMOVED"]
        print(f"  {NAME[cid]:20s} {dict(C4(x['field_type'] for x in rows))}")

    cust_assets = []
    for r in q(c, """
        SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status
        FROM customer_asset
    """):
        cust_assets.append({"asset": r.customer_asset.asset.split("/")[-1],
                            "field_type": E(r.customer_asset.field_type),
                            "status": E(r.customer_asset.status)})
    out["customer_assets"] = cust_assets
    print(f"  account-level assets: {dict(C4(x['field_type'] for x in cust_assets if x['status'] != 'REMOVED'))}")

    print("\n== CALL ASSET SCHEDULES (asset_field_type_view / asset ad_schedule) ==")
    # Ad schedules attached to an asset live on the asset itself.
    asset_scheds = []
    try:
        for r in q(c, """
            SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type,
                   campaign_asset.status
            FROM campaign_asset WHERE campaign_asset.field_type = 'CALL'
        """):
            asset_scheds.append({"campaign": str(r.campaign.id),
                                 "asset": r.campaign_asset.asset.split("/")[-1],
                                 "status": E(r.campaign_asset.status)})
    except Exception as exc:  # noqa: BLE001
        asset_scheds = [{"error": str(exc)[:300]}]
    out["call_asset_links"] = asset_scheds
    print("  ", asset_scheds)

    print("\n== CONVERSION ACTIONS ==")
    convs = []
    for r in q(c, """
        SELECT conversion_action.id, conversion_action.name, conversion_action.status,
               conversion_action.type, conversion_action.category,
               conversion_action.origin, conversion_action.primary_for_goal,
               conversion_action.counting_type,
               conversion_action.attribution_model_settings.attribution_model,
               conversion_action.attribution_model_settings.data_driven_model_status,
               conversion_action.value_settings.default_value,
               conversion_action.value_settings.always_use_default_value,
               conversion_action.phone_call_duration_seconds,
               conversion_action.click_through_lookback_window_days,
               conversion_action.view_through_lookback_window_days,
               conversion_action.include_in_conversions_metric,
               conversion_action.owner_customer
        FROM conversion_action
    """):
        x = r.conversion_action
        convs.append({
            "id": str(x.id), "name": x.name, "status": E(x.status),
            "type": E(x.type_), "category": E(x.category), "origin": E(x.origin),
            "primary_for_goal": x.primary_for_goal,
            "counting": E(x.counting_type),
            "attribution": E(x.attribution_model_settings.attribution_model),
            "default_value": x.value_settings.default_value,
            "always_default": x.value_settings.always_use_default_value,
            "phone_call_duration_seconds": x.phone_call_duration_seconds,
            "click_lookback_days": x.click_through_lookback_window_days,
            "include_in_conversions_metric": x.include_in_conversions_metric,
            "owner": x.owner_customer.split("/")[-1] if x.owner_customer else "",
        })
    out["conversion_actions"] = convs
    for x in sorted(convs, key=lambda z: (not z["primary_for_goal"], z["name"])):
        print(f"  {x['id']} {x['status']:8s} primary={str(x['primary_for_goal']):5s} "
              f"incl={str(x['include_in_conversions_metric']):5s} {x['category']:22s} "
              f"{x['counting']:12s} {x['type']:28s} {x['name']}")

    print("\n== CUSTOMER CONVERSION GOALS ==")
    goals = []
    for r in q(c, """
        SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
               customer_conversion_goal.biddable
        FROM customer_conversion_goal
    """):
        x = r.customer_conversion_goal
        goals.append({"category": E(x.category), "origin": E(x.origin), "biddable": x.biddable})
    out["customer_conversion_goals"] = goals
    for g in goals:
        if g["biddable"]:
            print(f"  BIDDABLE  {g['category']:24s} {g['origin']}")
    print(f"  total goal rows={len(goals)} biddable={sum(1 for g in goals if g['biddable'])}")

    print("\n== CAMPAIGN CONVERSION GOALS (campaign-level overrides) ==")
    cgoals = []
    for r in q(c, f"""
        SELECT campaign.id, campaign_conversion_goal.category,
               campaign_conversion_goal.origin, campaign_conversion_goal.biddable
        FROM campaign_conversion_goal WHERE campaign.id IN ({IN5})
    """):
        x = r.campaign_conversion_goal
        cgoals.append({"campaign": str(r.campaign.id), "category": E(x.category),
                       "origin": E(x.origin), "biddable": x.biddable})
    out["campaign_conversion_goals"] = cgoals
    for cid in FIVE:
        b = [g for g in cgoals if g["campaign"] == cid and g["biddable"]]
        print(f"  {NAME[cid]:20s} biddable={len(b)} -> "
              f"{sorted(set((g['category'], g['origin']) for g in b))}")

    print("\n== CAMPAIGN SETTINGS THAT MATTER (AI Max / auto assets / text customization) ==")
    settings = []
    for r in q(c, f"""
        SELECT campaign.id, campaign.name, campaign.keyword_match_type,
               campaign.ai_max_setting.enable_ai_max,
               campaign.asset_automation_settings,
               campaign.excluded_parent_asset_field_types
        FROM campaign WHERE campaign.id IN ({IN5})
    """):
        settings.append({"campaign": str(r.campaign.id),
                         "keyword_match_type": E(r.campaign.keyword_match_type),
                         "ai_max_enabled": r.campaign.ai_max_setting.enable_ai_max,
                         "asset_automation": [
                             {"type": E(z.asset_automation_type),
                              "status": E(z.asset_automation_status)}
                             for z in r.campaign.asset_automation_settings],
                         "excluded_parent_asset_field_types": [
                             E(z) for z in r.campaign.excluded_parent_asset_field_types]})
    out["campaign_search_settings"] = settings
    for s in settings:
        print(f"  {NAME[s['campaign']]:20s} keyword_match_type={s['keyword_match_type']} "
              f"ai_max={s['ai_max_enabled']} auto_assets={s['asset_automation']} "
              f"excluded_parent={s['excluded_parent_asset_field_types']}")

    write(SNAP / f"snapshot-structure-{STAMP}.json", out)
    return out


if __name__ == "__main__":
    main()
