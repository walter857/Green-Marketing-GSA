#!/usr/bin/env python3
"""Fresh read-only drift check before building the Softwind P0/P1 plans.

Separates CONFIGURATION drift (which would invalidate the plan) from METRIC drift
(expected, since the campaigns are live and spending). SELECT-only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
TZ = ZoneInfo("America/New_York")
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "drift-check-2026-08-25b.json"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    out = {"drift_check_account_local": now.isoformat(),
           "baseline_snapshot": "2026-08-25T16:57:08.439068-04:00"}
    before = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
    base_daily = json.loads(
        (SNAP / "chronology-2026-08-25.json").read_text(encoding="utf-8"))["campaign_daily"]

    # ---------- identity ----------
    r = next(iter(svc.search(customer_id=CID, query="""
        SELECT customer.id, customer.descriptive_name, customer.manager,
               customer.test_account, customer.currency_code, customer.time_zone,
               customer.conversion_tracking_setting.conversion_tracking_id,
               customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
               customer.auto_tagging_enabled
        FROM customer LIMIT 1""")))
    c = r.customer
    out["identity"] = {
        "descriptive_name": c.descriptive_name,
        "customer_id": normalize_customer_id(c.id),
        "manager": bool(c.manager), "test_account": bool(c.test_account),
        "currency": c.currency_code, "time_zone": c.time_zone,
        "conversion_tracking_id": str(
            c.conversion_tracking_setting.conversion_tracking_id or ""),
        "enhanced_conversions_for_leads": bool(
            c.conversion_tracking_setting.enhanced_conversions_for_leads_enabled),
        "auto_tagging": bool(c.auto_tagging_enabled),
    }
    out["identity_gate"] = {
        "name_matches": c.descriptive_name == "Softwind Power Washing - Live",
        "id_matches": normalize_customer_id(c.id) == CID,
        "not_manager": not bool(c.manager),
        "not_test": not bool(c.test_account),
    }

    # ---------- configuration drift ----------
    config_drift = []

    now_camp = {}
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
               campaign.primary_status, campaign.bidding_strategy_type,
               campaign.target_spend.cpc_bid_ceiling_micros,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.geo_target_type_setting.positive_geo_target_type,
               campaign_budget.id, campaign_budget.amount_micros
        FROM campaign ORDER BY campaign.id"""):
        cp = row.campaign
        now_camp[str(cp.id)] = {
            "name": cp.name, "status": enum_name(cp.status),
            "serving_status": enum_name(cp.serving_status),
            "primary_status": enum_name(cp.primary_status),
            "bidding_strategy_type": enum_name(cp.bidding_strategy_type),
            "cpc_bid_ceiling": (cp.target_spend.cpc_bid_ceiling_micros / 1_000_000
                                if cp.target_spend.cpc_bid_ceiling_micros else None),
            "search_partners": bool(cp.network_settings.target_search_network),
            "display": bool(cp.network_settings.target_content_network),
            "geo_option": enum_name(
                cp.geo_target_type_setting.positive_geo_target_type),
            "budget_id": str(row.campaign_budget.id),
            "budget": row.campaign_budget.amount_micros / 1_000_000,
        }
    out["campaigns_now"] = now_camp

    for b in before["campaigns"]:
        n = now_camp.get(b["id"])
        if n is None:
            config_drift.append({"field": "campaign %s" % b["id"],
                                 "was": b["name"], "now": "MISSING"})
            continue
        for key, was in [
            ("name", b["name"]), ("status", b["status"]),
            ("bidding_strategy_type", b["bidding_strategy_type"]),
            ("cpc_bid_ceiling", b["target_spend_cpc_bid_ceiling"]),
            ("search_partners", b["network"]["search_partners"]),
            ("display", b["network"]["display"]),
            ("geo_option", b["geo_target_type"]["positive"]),
            ("budget", b["budget"]["amount"]),
            ("budget_id", b["budget"]["id"]),
        ]:
            if n[key] != was:
                config_drift.append({"field": "campaign %s .%s" % (b["id"], key),
                                     "was": was, "now": n[key]})

    # ad groups
    now_ag = {}
    for row in svc.search(customer_id=CID, query="""
        SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id
        FROM ad_group ORDER BY ad_group.id"""):
        now_ag[str(row.ad_group.id)] = {"name": row.ad_group.name,
                                        "status": enum_name(row.ad_group.status),
                                        "campaign_id": str(row.campaign.id)}
    out["ad_group_count_now"] = len(now_ag)
    for a in before["ad_groups"]:
        n = now_ag.get(a["id"])
        if n is None:
            config_drift.append({"field": "ad_group %s" % a["id"],
                                 "was": a["name"], "now": "MISSING"})
        elif n["status"] != a["status"] or n["name"] != a["name"]:
            config_drift.append({"field": "ad_group %s (%s)" % (a["id"], a["name"]),
                                 "was": a["status"], "now": n["status"]})
    for gid in set(now_ag) - {a["id"] for a in before["ad_groups"]}:
        config_drift.append({"field": "ad_group %s" % gid, "was": "ABSENT",
                             "now": now_ag[gid]["name"]})

    # keywords
    now_kw = {}
    for row in svc.search(customer_id=CID, query="""
        SELECT ad_group.id, ad_group_criterion.criterion_id,
               ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
               ad_group_criterion.status, ad_group_criterion.system_serving_status,
               ad_group_criterion.approval_status
        FROM ad_group_criterion WHERE ad_group_criterion.type = KEYWORD"""):
        k = row.ad_group_criterion
        now_kw[(str(row.ad_group.id), str(k.criterion_id))] = {
            "text": k.keyword.text, "match": enum_name(k.keyword.match_type),
            "status": enum_name(k.status),
            "serving": enum_name(k.system_serving_status),
            "approval": enum_name(k.approval_status)}
    out["keyword_row_count_now"] = len(now_kw)
    for k in before["keywords"]:
        n = now_kw.get((k["ad_group_id"], k["criterion_id"]))
        if n is None:
            config_drift.append({"field": "keyword %s '%s'"
                                 % (k["criterion_id"], k["text"]),
                                 "was": k["status"], "now": "MISSING"})
        elif n["status"] != k["status"] or n["approval"] != k["approval_status"]:
            config_drift.append({"field": "keyword %s '%s'"
                                 % (k["criterion_id"], k["text"]),
                                 "was": "%s/%s" % (k["status"], k["approval_status"]),
                                 "now": "%s/%s" % (n["status"], n["approval"])})

    # ads
    now_ads = {}
    for row in svc.search(customer_id=CID, query="""
        SELECT ad_group_ad.ad.id, ad_group_ad.status,
               ad_group_ad.policy_summary.approval_status,
               ad_group_ad.ad.final_urls
        FROM ad_group_ad"""):
        a = row.ad_group_ad
        now_ads[str(a.ad.id)] = {
            "status": enum_name(a.status),
            "approval": enum_name(a.policy_summary.approval_status),
            "final_urls": sorted(a.ad.final_urls)}
    out["ad_count_now"] = len(now_ads)
    for a in before["ads"]:
        n = now_ads.get(a["ad_id"])
        if n is None:
            config_drift.append({"field": "ad %s" % a["ad_id"],
                                 "was": a["status"], "now": "MISSING"})
        elif (n["status"] != a["status"] or n["approval"] != a["approval_status"]
              or n["final_urls"] != sorted(a["final_urls"])):
            config_drift.append({"field": "ad %s (%s)" % (a["ad_id"], a["ad_group_name"]),
                                 "was": "%s/%s/%s" % (a["status"], a["approval_status"],
                                                      sorted(a["final_urls"])),
                                 "now": "%s/%s/%s" % (n["status"], n["approval"],
                                                      n["final_urls"])})

    # campaign criteria (schedule / geo / negatives)
    now_crit = {}
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.type,
               campaign_criterion.negative, campaign_criterion.status,
               campaign_criterion.display_name
        FROM campaign_criterion"""):
        cc = row.campaign_criterion
        now_crit[(str(row.campaign.id), str(cc.criterion_id))] = {
            "type": enum_name(cc.type_), "negative": bool(cc.negative),
            "status": enum_name(cc.status), "display_name": cc.display_name}
    out["campaign_criterion_count_now"] = len(now_crit)
    before_crit = {(c["campaign_id"], c["criterion_id"]) for c in before["campaign_criteria"]}
    for key in before_crit - set(now_crit):
        config_drift.append({"field": "campaign_criterion %s/%s" % key,
                             "was": "PRESENT", "now": "MISSING"})
    for key in set(now_crit) - before_crit:
        config_drift.append({"field": "campaign_criterion %s/%s" % key,
                             "was": "ABSENT", "now": now_crit[key]["type"]})

    # conversion actions
    now_ca = {}
    for row in svc.search(customer_id=CID, query="""
        SELECT conversion_action.id, conversion_action.name, conversion_action.status,
               conversion_action.primary_for_goal, conversion_action.counting_type,
               conversion_action.category, conversion_action.type,
               conversion_action.value_settings.default_value,
               conversion_action.value_settings.always_use_default_value,
               conversion_action.phone_call_duration_seconds,
               conversion_action.click_through_lookback_window_days
        FROM conversion_action ORDER BY conversion_action.id"""):
        ca = row.conversion_action
        now_ca[str(ca.id)] = {
            "name": ca.name, "status": enum_name(ca.status),
            "primary_for_goal": bool(ca.primary_for_goal),
            "counting_type": enum_name(ca.counting_type),
            "category": enum_name(ca.category), "type": enum_name(ca.type_),
            "default_value": ca.value_settings.default_value,
            "always_use_default_value": bool(
                ca.value_settings.always_use_default_value),
            "phone_call_duration_seconds": int(ca.phone_call_duration_seconds),
            "click_lookback_days": int(ca.click_through_lookback_window_days)}
    out["conversion_actions_now"] = now_ca
    for x in before["conversion_actions"]:
        n = now_ca.get(x["id"])
        if n is None:
            config_drift.append({"field": "conversion_action %s" % x["id"],
                                 "was": x["name"], "now": "MISSING"})
        elif (n["status"] != x["status"]
              or n["primary_for_goal"] != x["primary_for_goal"]
              or n["counting_type"] != x["counting_type"]):
            config_drift.append({
                "field": "conversion_action %s (%s)" % (x["id"], x["name"]),
                "was": "%s/primary=%s/%s" % (x["status"], x["primary_for_goal"],
                                             x["counting_type"]),
                "now": "%s/primary=%s/%s" % (n["status"], n["primary_for_goal"],
                                             n["counting_type"])})

    # campaign conversion goals
    goals = []
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, campaign_conversion_goal.category,
               campaign_conversion_goal.origin, campaign_conversion_goal.biddable
        FROM campaign_conversion_goal"""):
        g = row.campaign_conversion_goal
        goals.append({"campaign_id": str(row.campaign.id),
                      "category": enum_name(g.category),
                      "origin": enum_name(g.origin), "biddable": bool(g.biddable)})
    out["campaign_conversion_goals_now"] = goals

    # assets (sitelinks / call)
    assets = []
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, campaign_asset.asset,
               campaign_asset.field_type, campaign_asset.status,
               asset.id, asset.name, asset.type, asset.final_urls,
               asset.sitelink_asset.link_text, asset.callout_asset.callout_text,
               asset.call_asset.phone_number,
               asset.structured_snippet_asset.header
        FROM campaign_asset"""):
        assets.append({
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "asset_id": str(row.asset.id),
            "field_type": enum_name(row.campaign_asset.field_type),
            "status": enum_name(row.campaign_asset.status),
            "sitelink_text": row.asset.sitelink_asset.link_text or "",
            "callout_text": row.asset.callout_asset.callout_text or "",
            "snippet_header": row.asset.structured_snippet_asset.header or "",
            "call_phone": row.asset.call_asset.phone_number or "",
            "final_urls": list(row.asset.final_urls)})
    out["campaign_assets_now"] = assets

    cust_assets = []
    for row in svc.search(customer_id=CID, query="""
        SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status,
               asset.id, asset.type, asset.final_urls,
               asset.sitelink_asset.link_text, asset.callout_asset.callout_text
        FROM customer_asset"""):
        cust_assets.append({
            "asset_id": str(row.asset.id),
            "field_type": enum_name(row.customer_asset.field_type),
            "status": enum_name(row.customer_asset.status),
            "sitelink_text": row.asset.sitelink_asset.link_text or "",
            "callout_text": row.asset.callout_asset.callout_text or "",
            "final_urls": list(row.asset.final_urls)})
    out["customer_assets_now"] = cust_assets

    out["configuration_drift"] = config_drift
    out["configuration_drift_count"] = len(config_drift)

    # ---------- metric drift (expected) ----------
    end = now.date().isoformat()
    daily_now = []
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, segments.date, metrics.impressions,
               metrics.clicks, metrics.cost_micros, metrics.conversions,
               metrics.all_conversions, metrics.ctr, metrics.average_cpc
        FROM campaign WHERE segments.date BETWEEN '2026-08-01' AND '%s'
        ORDER BY segments.date""" % end):
        m = row.metrics
        daily_now.append({"campaign_id": str(row.campaign.id),
                          "campaign": row.campaign.name, "date": row.segments.date,
                          "impressions": int(m.impressions), "clicks": int(m.clicks),
                          "cost": m.cost_micros / 1_000_000,
                          "conversions": float(m.conversions),
                          "all_conversions": float(m.all_conversions)})
    out["campaign_daily_now"] = daily_now

    def tot(rows):
        return {"impressions": sum(r["impressions"] for r in rows),
                "clicks": sum(r["clicks"] for r in rows),
                "cost": round(sum(r["cost"] for r in rows), 2),
                "conversions": sum(r["conversions"] for r in rows),
                "all_conversions": sum(r["all_conversions"] for r in rows)}

    out["mtd_baseline_1657"] = tot(base_daily)
    out["mtd_now"] = tot(daily_now)
    out["metric_delta"] = {
        k: round(out["mtd_now"][k] - out["mtd_baseline_1657"][k], 2)
        for k in out["mtd_now"]}

    # fresh CPC distribution for the bidding plan
    clicks_rows = []
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.name, ad_group.name, segments.date,
               ad_group_criterion.keyword.text, metrics.clicks, metrics.cost_micros,
               metrics.average_cpc, metrics.impressions
        FROM keyword_view WHERE segments.date BETWEEN '2026-08-01' AND '%s'
          AND metrics.clicks > 0 ORDER BY segments.date""" % end):
        clicks_rows.append({"date": row.segments.date, "campaign": row.campaign.name,
                            "ad_group": row.ad_group.name,
                            "keyword": row.ad_group_criterion.keyword.text,
                            "clicks": int(row.metrics.clicks),
                            "cost": row.metrics.cost_micros / 1_000_000,
                            "avg_cpc": row.metrics.average_cpc / 1_000_000})
    out["click_level_cpc"] = clicks_rows

    # fresh impression share
    isrows = []
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks,
               metrics.cost_micros, metrics.ctr, metrics.average_cpc,
               metrics.search_impression_share,
               metrics.search_budget_lost_impression_share,
               metrics.search_rank_lost_impression_share,
               metrics.search_top_impression_share,
               metrics.search_absolute_top_impression_share,
               metrics.top_impression_percentage,
               metrics.absolute_top_impression_percentage,
               metrics.invalid_clicks
        FROM campaign WHERE segments.date BETWEEN '2026-08-01' AND '%s'""" % end):
        m = row.metrics
        isrows.append({
            "campaign_id": str(row.campaign.id), "campaign": row.campaign.name,
            "impressions": int(m.impressions), "clicks": int(m.clicks),
            "cost": m.cost_micros / 1_000_000, "ctr": float(m.ctr),
            "avg_cpc": m.average_cpc / 1_000_000 if m.average_cpc else 0.0,
            "search_is": float(m.search_impression_share) or None,
            "lost_is_budget": float(m.search_budget_lost_impression_share) or None,
            "lost_is_rank": float(m.search_rank_lost_impression_share) or None,
            "search_top_is": float(m.search_top_impression_share) or None,
            "search_abs_top_is": float(m.search_absolute_top_impression_share) or None,
            "top_pct": float(m.top_impression_percentage) or None,
            "abs_top_pct": float(m.absolute_top_impression_percentage) or None,
            "invalid_clicks": int(m.invalid_clicks)})
    out["campaign_aggregate_now"] = isrows

    # fresh search terms
    st = []
    for row in svc.search(customer_id=CID, query="""
        SELECT campaign.name, ad_group.name, search_term_view.search_term,
               segments.keyword.info.text, segments.keyword.info.match_type,
               metrics.impressions, metrics.clicks, metrics.cost_micros,
               metrics.conversions
        FROM search_term_view WHERE segments.date BETWEEN '2026-08-01' AND '%s'
        ORDER BY metrics.impressions DESC""" % end):
        st.append({"campaign": row.campaign.name, "ad_group": row.ad_group.name,
                   "search_term": row.search_term_view.search_term,
                   "matched_keyword": row.segments.keyword.info.text,
                   "match_type": enum_name(row.segments.keyword.info.match_type),
                   "impressions": int(row.metrics.impressions),
                   "clicks": int(row.metrics.clicks),
                   "cost": row.metrics.cost_micros / 1_000_000,
                   "conversions": float(row.metrics.conversions)})
    out["search_terms_now"] = st

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("DRIFT CHECK  %s" % now.isoformat())
    print("  baseline: %s" % out["baseline_snapshot"])
    print()
    print("IDENTITY GATE")
    for k, v in out["identity_gate"].items():
        print("  %-16s %s" % (k, "PASS" if v else "*** FAIL ***"))
    print()
    print("CONFIGURATION DRIFT: %d" % len(config_drift))
    for d in config_drift:
        print("  !! %s : %r -> %r" % (d["field"], d["was"], d["now"]))
    if not config_drift:
        print("  none - every mutable surface identical to the 16:57 snapshot")
    print()
    print("METRIC DRIFT (expected - campaigns are live)")
    print("  baseline 16:57 : %s" % out["mtd_baseline_1657"])
    print("  now            : %s" % out["mtd_now"])
    print("  delta          : %s" % out["metric_delta"])
    print()
    print("Wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
