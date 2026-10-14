#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-09-15 session A | identity gate + fresh before-state."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-15"
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP}

c = client()
print("=== 1. FRESH IDENTITY GATE (read-only) ===")
row = q(c, """
    SELECT customer.id, customer.descriptive_name, customer.currency_code,
           customer.time_zone, customer.manager, customer.test_account,
           customer.auto_tagging_enabled, customer.status,
           customer.tracking_url_template, customer.final_url_suffix,
           customer.conversion_tracking_setting.conversion_tracking_id,
           customer.conversion_tracking_setting.google_ads_conversion_customer,
           customer.conversion_tracking_setting.conversion_tracking_status,
           customer.optimization_score
    FROM customer
""")[0].customer
links = {}
for x in q(c, "SELECT customer_manager_link.manager_customer, customer_manager_link.status FROM customer_manager_link"):
    links[x.customer_manager_link.manager_customer.split("/")[-1]] = E(x.customer_manager_link.status)

checks = {
    "descriptive_name == 'Ambient Cooling - Live'": row.descriptive_name == EXACT_NAME,
    "customer.id == 2401959466": str(row.id) == CID,
    "NOT a manager account": not row.manager,
    "NOT a test account": not row.test_account,
    "time_zone == America/New_York": row.time_zone == "America/New_York",
    "currency_code == USD": row.currency_code == "USD",
    "status ENABLED": E(row.status) == "ENABLED",
    "name contains '- live'": "- live" in row.descriptive_name.casefold(),
    "GM manager 3373711342 ACTIVE": links.get(GM_MANAGER) == "ACTIVE",
    "ClickCease manager 2815082755 ACTIVE": links.get(CC_MANAGER) == "ACTIVE",
}
for k, v in checks.items():
    print(f"  [{'PASS' if v else 'FAIL'}] {k}")
out["identity"] = {
    "observed_name": row.descriptive_name, "observed_id": str(row.id),
    "manager": row.manager, "test_account": row.test_account,
    "currency": row.currency_code, "time_zone": row.time_zone,
    "status": E(row.status), "auto_tagging": row.auto_tagging_enabled,
    "conversion_tracking_id": row.conversion_tracking_setting.conversion_tracking_id,
    "google_ads_conversion_customer": row.conversion_tracking_setting.google_ads_conversion_customer,
    "conversion_tracking_status": E(row.conversion_tracking_setting.conversion_tracking_status),
    "customer_tracking_url_template": row.tracking_url_template or None,
    "customer_final_url_suffix": row.final_url_suffix or None,
    "manager_links": links, "checks": checks,
    "all_pass": all(checks.values()),
}
assert all(checks.values()), "IDENTITY GATE FAILED - STOP"
print("\n  Ambient Cooling - Live | 2401959466 | Commercial HVAC Installation")
print(f"  conversion_tracking_id={row.conversion_tracking_setting.conversion_tracking_id} "
      f"owner={row.conversion_tracking_setting.google_ads_conversion_customer}")

print("\n=== 2. ACCOUNT DATE / SETTLED BOUNDARY ===")
now = datetime.datetime.now(TZ)
out["account_local_now"] = now.isoformat()
out["today_partial"] = str(now.date())
out["last_settled"] = str(now.date() - datetime.timedelta(days=1))
print(f"  account local now = {now.isoformat()}")
print(f"  today_partial={now.date()}  last_settled={now.date()-datetime.timedelta(days=1)}")

print("\n=== 3. THE FIVE CAMPAIGNS - FULL CONFIG ===")
camps = q(c, f"""
    SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
           campaign.advertising_channel_type, campaign.advertising_channel_sub_type,
           campaign.bidding_strategy_type,
           campaign.target_spend.cpc_bid_ceiling_micros,
           campaign.network_settings.target_google_search,
           campaign.network_settings.target_search_network,
           campaign.network_settings.target_content_network,
           campaign.network_settings.target_partner_search_network,
           campaign.geo_target_type_setting.positive_geo_target_type,
           campaign.geo_target_type_setting.negative_geo_target_type,
           campaign.tracking_url_template, campaign.final_url_suffix,
           campaign.start_date_time, campaign.end_date_time,
           campaign.campaign_budget, campaign.optimization_score,
           campaign.keyword_match_type, campaign.ai_max_setting.enable_ai_max,
           campaign.asset_automation_settings, campaign.ad_serving_optimization_status,
           campaign_budget.id, campaign_budget.amount_micros,
           campaign_budget.explicitly_shared, campaign_budget.delivery_method,
           campaign_budget.status
    FROM campaign WHERE campaign.id IN ({IN5}) ORDER BY campaign.name
""")
cdat = {}
for r in camps:
    cm, cb = r.campaign, r.campaign_budget
    cdat[str(cm.id)] = {
        "name": cm.name, "status": E(cm.status), "serving_status": E(cm.serving_status),
        "channel": E(cm.advertising_channel_type),
        "sub_type": E(cm.advertising_channel_sub_type),
        "bidding": E(cm.bidding_strategy_type),
        "cpc_ceiling_micros": cm.target_spend.cpc_bid_ceiling_micros,
        "cpc_ceiling_usd": round(cm.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
        "net_google_search": cm.network_settings.target_google_search,
        "net_search_partners": cm.network_settings.target_search_network,
        "net_display": cm.network_settings.target_content_network,
        "net_partner": cm.network_settings.target_partner_search_network,
        "geo_positive": E(cm.geo_target_type_setting.positive_geo_target_type),
        "geo_negative": E(cm.geo_target_type_setting.negative_geo_target_type),
        "tracking_url_template": cm.tracking_url_template or None,
        "final_url_suffix": cm.final_url_suffix or None,
        "start_date_time": cm.start_date_time or None, "end_date_time": cm.end_date_time or None,
        "keyword_match_type": E(cm.keyword_match_type),
        "ai_max_enabled": cm.ai_max_setting.enable_ai_max,
        "asset_automation_settings": [f"{E(x.asset_automation_type)}={E(x.asset_automation_status)}" for x in cm.asset_automation_settings],
        "ad_serving_optimization_status": E(cm.ad_serving_optimization_status),
        "budget_id": str(cb.id), "budget_micros": cb.amount_micros,
        "budget_usd": round(cb.amount_micros / 1e6, 2),
        "budget_shared": cb.explicitly_shared, "budget_delivery": E(cb.delivery_method),
        "budget_status": E(cb.status),
    }
    print(f"  {cm.id} {E(cm.status):8s} serv={E(cm.serving_status):10s} "
          f"${cb.amount_micros/1e6:>7.2f}/d ceil=${cm.target_spend.cpc_bid_ceiling_micros/1e6:>5.2f} "
          f"{E(cm.bidding_strategy_type):14s} SP={cm.network_settings.target_search_network} "
          f"D={cm.network_settings.target_content_network} "
          f"geo={E(cm.geo_target_type_setting.positive_geo_target_type)} {cm.name}")
out["campaigns"] = cdat
tot = sum(v["budget_usd"] for v in cdat.values())
out["combined_daily_budget"] = round(tot, 2)
out["planning_30_4"] = round(tot * 30.4, 2)
out["monthly_max"] = 13000.0
out["headroom"] = round(13000.0 - tot * 30.4, 2)
print(f"\n  combined daily = ${tot:.2f}   x30.4 = ${tot*30.4:.2f}   "
      f"headroom vs $13,000 = ${13000-tot*30.4:.2f}")

print("\n=== 4. AD GROUPS IN THE FIVE ===")
ags = q(c, f"""
    SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
           ad_group.cpc_bid_micros, ad_group.tracking_url_template,
           ad_group.final_url_suffix, campaign.id, campaign.name
    FROM ad_group WHERE campaign.id IN ({IN5}) ORDER BY campaign.name, ad_group.name
""")
agd = {}
for r in ags:
    a = r.ad_group
    agd[str(a.id)] = {"name": a.name, "status": E(a.status), "type": E(a.type),
                      "cpc_bid_micros": a.cpc_bid_micros,
                      "tracking_url_template": a.tracking_url_template or None,
                      "final_url_suffix": a.final_url_suffix or None,
                      "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name}
    print(f"  {a.id} {E(a.status):8s} cpc={a.cpc_bid_micros:>9} "
          f"{r.campaign.name[:42]:42s} | {a.name}")
out["ad_groups"] = agd

print("\n=== 5. POSITIVE KEYWORDS ===")
kws = q(c, f"""
    SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status,
           ad_group_criterion.approval_status, ad_group_criterion.final_urls,
           ad_group_criterion.quality_info.quality_score,
           ad_group_criterion.quality_info.creative_quality_score,
           ad_group_criterion.quality_info.post_click_quality_score,
           ad_group_criterion.quality_info.search_predicted_ctr,
           ad_group_criterion.cpc_bid_micros, ad_group_criterion.effective_cpc_bid_micros,
           ad_group_criterion.system_serving_status,
           ad_group.id, ad_group.name, ad_group.status, campaign.id, campaign.name
    FROM ad_group_criterion
    WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type = KEYWORD
      AND ad_group_criterion.negative = FALSE
    ORDER BY campaign.name, ad_group.name
""")
kd = []
for r in kws:
    k = r.ad_group_criterion
    rec = {"criterion_id": str(k.criterion_id), "text": k.keyword.text,
           "match": E(k.keyword.match_type), "status": E(k.status),
           "approval": E(k.approval_status), "system_serving": E(k.system_serving_status),
           "final_urls": list(k.final_urls),
           "qs": k.quality_info.quality_score or None,
           "qs_ad_relevance": E(k.quality_info.creative_quality_score),
           "qs_lp_experience": E(k.quality_info.post_click_quality_score),
           "qs_exp_ctr": E(k.quality_info.search_predicted_ctr),
           "cpc_bid_micros": k.cpc_bid_micros, "eff_cpc_micros": k.effective_cpc_bid_micros,
           "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
           "ad_group_status": E(r.ad_group.status),
           "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name}
    kd.append(rec)
    print(f"  [{E(r.ad_group.status):8s}] {r.campaign.name[:28]:28s} | {E(k.keyword.match_type):6s} "
          f"{k.keyword.text[:36]:36s} {E(k.status):8s} {E(k.approval_status):10s} "
          f"QS={k.quality_info.quality_score or '-'} "
          f"({E(k.quality_info.search_predicted_ctr)[:16]}/"
          f"{E(k.quality_info.creative_quality_score)[:16]}/"
          f"{E(k.quality_info.post_click_quality_score)[:16]})")
out["keywords"] = kd
print(f"  total positive keyword rows: {len(kd)}  "
      f"(non-REMOVED parents: {sum(1 for x in kd if x['ad_group_status']!='REMOVED')})")

Path(SNAP).mkdir(parents=True, exist_ok=True)
p = SNAP / f"identity-and-structure-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
