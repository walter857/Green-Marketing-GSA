#!/usr/bin/env python3
"""September 1 2026 continuation snapshot for Softwind Power Washing.

Fresh read-only identity gate, targeted configuration drift check against the
2026-08-31 forensic baseline, final August 1-31 results, and September 1 partial
results reported separately.

SELECT statements only. Constructs no operation, calls no mutate service.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
EXPECTED_NAME = "Softwind Power Washing - Live"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
BASELINE = SNAP / "forensic-structure-2026-08-31T102120.json"
CAMPAIGNS = ("24103511039", "24145053510")


def micros(v) -> float:
    return round(int(v) / 1_000_000, 4)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    out: dict = {"mode": "READ-ONLY", "customer_id": CID}

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    # ------------------------------------------------ 1. identity gate
    c = q("""SELECT customer.id, customer.descriptive_name, customer.currency_code,
                    customer.time_zone, customer.manager, customer.test_account,
                    customer.status, customer.auto_tagging_enabled,
                    customer.tracking_url_template, customer.final_url_suffix,
                    customer.optimization_score
             FROM customer LIMIT 1""")[0].customer
    tz = c.time_zone or "America/New_York"
    now = datetime.now(ZoneInfo(tz))
    identity = {
        "customer_id": normalize_customer_id(c.id),
        "descriptive_name": c.descriptive_name,
        "currency": c.currency_code,
        "time_zone": tz,
        "manager": bool(c.manager),
        "test_account": bool(c.test_account),
        "status": enum_name(c.status),
        "auto_tagging_enabled": bool(c.auto_tagging_enabled),
        "tracking_url_template": c.tracking_url_template or "",
        "final_url_suffix": c.final_url_suffix or "",
        "optimization_score": round(float(c.optimization_score or 0), 6),
        "live_marker_present": "- live" in (c.descriptive_name or "").lower(),
        "account_local_datetime": now.isoformat(),
        "account_local_date": now.date().isoformat(),
        "account_local_time": now.strftime("%H:%M:%S"),
    }
    gate = {
        "name_matches": identity["descriptive_name"] == EXPECTED_NAME,
        "id_matches": identity["customer_id"] == CID,
        "not_manager": identity["manager"] is False,
        "not_test": identity["test_account"] is False,
        "live_marker": identity["live_marker_present"],
        "status_enabled": identity["status"] == "ENABLED",
    }
    out["identity"] = identity
    out["identity_gate"] = gate
    if not all(gate.values()):
        print("IDENTITY GATE FAILED:", json.dumps(gate, indent=2))
        return 2

    stamp = now.strftime("%Y-%m-%dT%H%M%S")
    out["snapshot_timestamp_account_local"] = now.isoformat()

    # ------------------------------------------------ 2. campaign configuration
    camp_cfg: dict = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status,
                         campaign.serving_status, campaign.primary_status,
                         campaign.primary_status_reasons,
                         campaign.advertising_channel_type,
                         campaign.bidding_strategy_type,
                         campaign.bidding_strategy_system_status,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.campaign_budget,
                         campaign.network_settings.target_search_network,
                         campaign.network_settings.target_content_network,
                         campaign.network_settings.target_partner_search_network,
                         campaign.geo_target_type_setting.positive_geo_target_type,
                         campaign.geo_target_type_setting.negative_geo_target_type,
                         campaign.ai_max_setting.enable_ai_max,
                         campaign.asset_automation_settings,
                         campaign.tracking_url_template, campaign.final_url_suffix,
                         campaign.start_date_time, campaign.end_date_time
                  FROM campaign WHERE campaign.status != 'REMOVED'"""):
        k = r.campaign
        camp_cfg[str(k.id)] = {
            "name": k.name,
            "status": enum_name(k.status),
            "serving_status": enum_name(k.serving_status),
            "primary_status": enum_name(k.primary_status),
            "primary_status_reasons": [enum_name(x) for x in k.primary_status_reasons],
            "channel": enum_name(k.advertising_channel_type),
            "bidding_strategy_type": enum_name(k.bidding_strategy_type),
            "bidding_system_status": enum_name(k.bidding_strategy_system_status),
            "cpc_bid_ceiling_micros": int(k.target_spend.cpc_bid_ceiling_micros),
            "cpc_bid_ceiling_usd": micros(k.target_spend.cpc_bid_ceiling_micros),
            "budget_id": k.campaign_budget.split("/")[-1],
            "search_partners": bool(k.network_settings.target_partner_search_network),
            "search_network": bool(k.network_settings.target_search_network),
            "display_network": bool(k.network_settings.target_content_network),
            "geo_positive": enum_name(k.geo_target_type_setting.positive_geo_target_type),
            "geo_negative": enum_name(k.geo_target_type_setting.negative_geo_target_type),
            "ai_max": bool(k.ai_max_setting.enable_ai_max),
            "asset_automation": {enum_name(a.asset_automation_type):
                                 enum_name(a.asset_automation_status)
                                 for a in k.asset_automation_settings},
            "tracking_url_template": k.tracking_url_template or "",
            "final_url_suffix": k.final_url_suffix or "",
            "start_date_time": k.start_date_time or "",
            "end_date_time": k.end_date_time or "",
        }
    for r in q("""SELECT campaign_budget.id, campaign_budget.amount_micros,
                         campaign_budget.status, campaign_budget.delivery_method,
                         campaign_budget.explicitly_shared
                  FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'"""):
        b = r.campaign_budget
        for cc in camp_cfg.values():
            if cc["budget_id"] == str(b.id):
                cc["daily_budget_usd"] = micros(b.amount_micros)
                cc["budget_delivery"] = enum_name(b.delivery_method)
                cc["budget_shared"] = bool(b.explicitly_shared)

    # conversion goals per campaign
    cg = defaultdict(list)
    for r in q("""SELECT campaign.id, campaign_conversion_goal.category,
                         campaign_conversion_goal.origin, campaign_conversion_goal.biddable
                  FROM campaign_conversion_goal"""):
        if r.campaign_conversion_goal.biddable:
            cg[str(r.campaign.id)].append(
                f"{enum_name(r.campaign_conversion_goal.category)}/"
                f"{enum_name(r.campaign_conversion_goal.origin)}")
    for i, v in camp_cfg.items():
        v["biddable_campaign_conversion_goals"] = sorted(cg.get(i, []))

    # criteria
    negs = defaultdict(list)
    locs = defaultdict(lambda: {"positive": 0, "negative": [], "ids": []})
    sched = defaultdict(list)
    other = defaultdict(lambda: defaultdict(int))
    for r in q("""SELECT campaign.id, campaign_criterion.type,
                         campaign_criterion.negative, campaign_criterion.keyword.text,
                         campaign_criterion.keyword.match_type,
                         campaign_criterion.location.geo_target_constant,
                         campaign_criterion.ad_schedule.day_of_week,
                         campaign_criterion.ad_schedule.start_hour,
                         campaign_criterion.ad_schedule.end_hour
                  FROM campaign_criterion WHERE campaign_criterion.status != 'REMOVED'"""):
        i = str(r.campaign.id)
        cc = r.campaign_criterion
        t = enum_name(cc.type_)
        other[i][t] += 1
        if t == "KEYWORD" and cc.negative:
            negs[i].append((cc.keyword.text, enum_name(cc.keyword.match_type)))
        elif t == "LOCATION":
            gid = (cc.location.geo_target_constant or "").split("/")[-1]
            if cc.negative:
                locs[i]["negative"].append(gid)
            else:
                locs[i]["positive"] += 1
                locs[i]["ids"].append(gid)
        elif t == "AD_SCHEDULE":
            sched[i].append((enum_name(cc.ad_schedule.day_of_week),
                             int(cc.ad_schedule.start_hour), int(cc.ad_schedule.end_hour)))
    for i, v in camp_cfg.items():
        v["campaign_negative_keywords"] = len(negs.get(i, []))
        v["positive_locations"] = locs[i]["positive"]
        v["negative_locations"] = sorted(locs[i]["negative"])
        v["ad_schedule"] = sorted(sched.get(i, []))
        v["criterion_type_counts"] = dict(other[i])

    # ad groups / keywords / ads / ad-group negatives / assets
    ag_by_camp = defaultdict(lambda: {"total": 0, "enabled": 0, "enabled_names": []})
    ag_camp = {}
    for r in q("""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status
                  FROM ad_group WHERE ad_group.status != 'REMOVED'"""):
        i, a = str(r.campaign.id), r.ad_group
        ag_camp[str(a.id)] = i
        ag_by_camp[i]["total"] += 1
        if enum_name(a.status) == "ENABLED":
            ag_by_camp[i]["enabled"] += 1
            ag_by_camp[i]["enabled_names"].append(a.name)

    kw = defaultdict(lambda: {"total": 0, "enabled": 0})
    for r in q("""SELECT campaign.id, ad_group.id, ad_group.status,
                         ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type,
                         ad_group_criterion.status
                  FROM keyword_view"""):
        i = str(r.campaign.id)
        kw[i]["total"] += 1
        if (enum_name(r.ad_group_criterion.status) == "ENABLED"
                and enum_name(r.ad_group.status) == "ENABLED"):
            kw[i]["enabled"] += 1

    ads = defaultdict(lambda: {"total": 0, "enabled_in_enabled_ag": 0})
    final_urls = defaultdict(set)
    for r in q("""SELECT campaign.id, ad_group.id, ad_group.status, ad_group_ad.ad.id,
                         ad_group_ad.status, ad_group_ad.ad.type,
                         ad_group_ad.ad.final_urls,
                         ad_group_ad.policy_summary.approval_status
                  FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        i = str(r.campaign.id)
        ads[i]["total"] += 1
        if (enum_name(r.ad_group_ad.status) == "ENABLED"
                and enum_name(r.ad_group.status) == "ENABLED"):
            ads[i]["enabled_in_enabled_ag"] += 1
            for u in r.ad_group_ad.ad.final_urls:
                final_urls[i].add(u)

    agneg = defaultdict(int)
    for r in q("""SELECT campaign.id, ad_group_criterion.keyword.text
                  FROM ad_group_criterion
                  WHERE ad_group_criterion.negative = TRUE
                    AND ad_group_criterion.type = 'KEYWORD'
                    AND ad_group_criterion.status != 'REMOVED'"""):
        agneg[str(r.campaign.id)] += 1

    assets = defaultdict(lambda: defaultdict(int))
    for r in q("""SELECT campaign.id, campaign_asset.field_type, campaign_asset.status
                  FROM campaign_asset WHERE campaign_asset.status != 'REMOVED'"""):
        assets[str(r.campaign.id)][enum_name(r.campaign_asset.field_type)] += 1

    for i, v in camp_cfg.items():
        v["ad_groups_total"] = ag_by_camp[i]["total"]
        v["ad_groups_enabled"] = ag_by_camp[i]["enabled"]
        v["ad_groups_enabled_names"] = sorted(ag_by_camp[i]["enabled_names"])
        v["keywords_total"] = kw[i]["total"]
        v["keywords_enabled_servable"] = kw[i]["enabled"]
        v["ads_total"] = ads[i]["total"]
        v["rsas_enabled_servable"] = ads[i]["enabled_in_enabled_ag"]
        v["ad_group_negative_keywords"] = agneg[i]
        v["campaign_assets"] = dict(assets[i])
        v["serving_final_urls"] = sorted(final_urls[i])

    out["campaign_configuration"] = {i: camp_cfg[i] for i in CAMPAIGNS if i in camp_cfg}
    out["other_campaigns_present"] = sorted(set(camp_cfg) - set(CAMPAIGNS))

    # ------------------------------------------------ 3. account-wide surfaces
    acct = {}
    acct["audiences"] = len(q("""SELECT campaign_criterion.criterion_id
                                 FROM campaign_criterion
                                 WHERE campaign_criterion.type = 'USER_LIST'
                                   AND campaign_criterion.status != 'REMOVED'"""))
    for t in ("GENDER", "AGE_RANGE", "INCOME_RANGE", "IP_BLOCK"):
        acct[f"{t.lower()}_criteria"] = len(q(
            f"""SELECT campaign_criterion.criterion_id FROM campaign_criterion
                WHERE campaign_criterion.type = '{t}'
                  AND campaign_criterion.status != 'REMOVED'"""))
    ca = []
    for r in q("""SELECT conversion_action.id, conversion_action.name,
                         conversion_action.status, conversion_action.type,
                         conversion_action.category,
                         conversion_action.primary_for_goal,
                         conversion_action.include_in_conversions_metric,
                         conversion_action.counting_type
                  FROM conversion_action WHERE conversion_action.status != 'REMOVED'"""):
        a = r.conversion_action
        ca.append({"id": str(a.id), "name": a.name, "status": enum_name(a.status),
                   "type": enum_name(a.type_), "category": enum_name(a.category),
                   "primary_for_goal": bool(a.primary_for_goal),
                   "include_in_conversions_metric": bool(a.include_in_conversions_metric),
                   "counting": enum_name(a.counting_type)})
    acct["conversion_actions"] = ca
    ccg = []
    for r in q("""SELECT customer_conversion_goal.category,
                         customer_conversion_goal.origin,
                         customer_conversion_goal.biddable
                  FROM customer_conversion_goal"""):
        g = r.customer_conversion_goal
        ccg.append({"category": enum_name(g.category), "origin": enum_name(g.origin),
                    "biddable": bool(g.biddable)})
    acct["customer_conversion_goals"] = ccg
    acct["customer_conversion_goals_biddable_count"] = sum(1 for g in ccg if g["biddable"])
    out["account_surfaces"] = acct

    # ------------------------------------------------ 4. AUGUST 1-31 final
    def perf(where: str) -> dict:
        res = {}
        for r in q(f"""SELECT campaign.id, campaign.name, metrics.impressions,
                              metrics.clicks, metrics.invalid_clicks,
                              metrics.invalid_click_rate, metrics.cost_micros,
                              metrics.ctr, metrics.average_cpc,
                              metrics.conversions, metrics.all_conversions,
                              metrics.conversions_from_interactions_rate,
                              metrics.search_impression_share,
                              metrics.search_rank_lost_impression_share,
                              metrics.search_budget_lost_impression_share,
                              metrics.search_absolute_top_impression_share
                       FROM campaign WHERE {where}
                         AND campaign.status != 'REMOVED'"""):
            m, k = r.metrics, r.campaign
            res[str(k.id)] = {
                "name": k.name,
                "impressions": int(m.impressions),
                "valid_clicks": int(m.clicks),
                "invalid_clicks": int(m.invalid_clicks),
                "invalid_click_rate": round(float(m.invalid_click_rate), 6),
                "raw_clicks": int(m.clicks) + int(m.invalid_clicks),
                "cost_usd": micros(m.cost_micros),
                "ctr_valid": round(float(m.ctr), 6),
                "avg_cpc_valid_usd": micros(m.average_cpc),
                "conversions": round(float(m.conversions), 4),
                "all_conversions": round(float(m.all_conversions), 4),
                "conv_rate": round(float(m.conversions_from_interactions_rate), 6),
                "search_is": round(float(m.search_impression_share), 6),
                "search_lost_is_rank": round(float(m.search_rank_lost_impression_share), 6),
                "search_lost_is_budget": round(float(m.search_budget_lost_impression_share), 6),
                "search_abs_top_is": round(float(m.search_absolute_top_impression_share), 6),
            }
        return res

    aug = perf("segments.date BETWEEN '2026-08-01' AND '2026-08-31'")
    sep = perf("segments.date BETWEEN '2026-09-01' AND '2026-09-01'")
    alltime = perf("segments.date BETWEEN '2026-01-01' AND '2026-09-01'")

    def combine(d):
        t = {"impressions": 0, "valid_clicks": 0, "invalid_clicks": 0, "raw_clicks": 0,
             "cost_usd": 0.0, "conversions": 0.0, "all_conversions": 0.0}
        for v in d.values():
            for k in t:
                t[k] = round(t[k] + v[k], 4)
        t["ctr_valid"] = round(t["valid_clicks"] / t["impressions"], 6) if t["impressions"] else 0
        t["avg_cpc_valid_usd"] = (round(t["cost_usd"] / t["valid_clicks"], 4)
                                  if t["valid_clicks"] else 0)
        t["invalid_click_rate"] = (round(t["invalid_clicks"] / t["raw_clicks"], 6)
                                   if t["raw_clicks"] else 0)
        return t

    out["august_final"] = {"per_campaign": aug, "combined": combine(aug),
                           "settled_as_of": now.isoformat()}
    out["september_1_partial"] = {"per_campaign": sep, "combined": combine(sep),
                                  "through": now.isoformat()}
    out["all_time"] = {"per_campaign": alltime, "combined": combine(alltime)}

    # August by day, to expose retroactive adjustment and the last serving days
    daily = []
    for r in q("""SELECT segments.date, campaign.id, metrics.impressions, metrics.clicks,
                         metrics.invalid_clicks, metrics.cost_micros
                  FROM campaign
                  WHERE segments.date BETWEEN '2026-08-25' AND '2026-09-01'
                    AND campaign.status != 'REMOVED'"""):
        daily.append({"date": r.segments.date, "campaign": str(r.campaign.id),
                      "impr": int(r.metrics.impressions), "valid_clicks": int(r.metrics.clicks),
                      "invalid_clicks": int(r.metrics.invalid_clicks),
                      "cost_usd": micros(r.metrics.cost_micros)})
    out["daily_tail"] = sorted(daily, key=lambda x: (x["date"], x["campaign"]))

    # device split, Sept 1 and August
    for label, rng in (("august", "'2026-08-01' AND '2026-08-31'"),
                       ("september_1", "'2026-09-01' AND '2026-09-01'")):
        dev = []
        for r in q(f"""SELECT segments.device, metrics.impressions, metrics.clicks,
                              metrics.invalid_clicks, metrics.cost_micros
                       FROM campaign WHERE segments.date BETWEEN {rng}
                         AND campaign.status != 'REMOVED'"""):
            dev.append({"device": enum_name(r.segments.device),
                        "impr": int(r.metrics.impressions),
                        "valid_clicks": int(r.metrics.clicks),
                        "invalid_clicks": int(r.metrics.invalid_clicks),
                        "cost_usd": micros(r.metrics.cost_micros)})
        agg = defaultdict(lambda: {"impr": 0, "valid_clicks": 0, "invalid_clicks": 0,
                                   "cost_usd": 0.0})
        for d in dev:
            for k in ("impr", "valid_clicks", "invalid_clicks", "cost_usd"):
                agg[d["device"]][k] = round(agg[d["device"]][k] + d[k], 4)
        out[f"device_{label}"] = dict(agg)

    # September 1 search terms
    st = []
    for r in q("""SELECT search_term_view.search_term, campaign.id, ad_group.name,
                         segments.search_term_match_type, metrics.impressions,
                         metrics.clicks, metrics.cost_micros, metrics.conversions
                  FROM search_term_view
                  WHERE segments.date BETWEEN '2026-09-01' AND '2026-09-01'"""):
        st.append({"term": r.search_term_view.search_term,
                   "campaign": str(r.campaign.id), "ad_group": r.ad_group.name,
                   "match": enum_name(r.segments.search_term_match_type),
                   "impr": int(r.metrics.impressions), "clicks": int(r.metrics.clicks),
                   "cost_usd": micros(r.metrics.cost_micros),
                   "conv": round(float(r.metrics.conversions), 4)})
    out["september_1_search_terms"] = st

    # September 1 individual click prices, to test the ceiling-as-price pattern
    clicks = []
    for r in q("""SELECT ad_group.name, ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type, campaign.id,
                         metrics.clicks, metrics.cost_micros, metrics.impressions
                  FROM keyword_view
                  WHERE segments.date BETWEEN '2026-09-01' AND '2026-09-01'
                    AND metrics.clicks > 0"""):
        clicks.append({"campaign": str(r.campaign.id), "ad_group": r.ad_group.name,
                       "keyword": r.ad_group_criterion.keyword.text,
                       "match": enum_name(r.ad_group_criterion.keyword.match_type),
                       "clicks": int(r.metrics.clicks),
                       "cost_usd": micros(r.metrics.cost_micros),
                       "cpc": round(micros(r.metrics.cost_micros) / int(r.metrics.clicks), 4)})
    out["september_1_click_prices"] = clicks

    # call view (no date filter permitted)
    out["call_view_rows"] = len(q("""SELECT call_view.call_status FROM call_view"""))

    # ------------------------------------------------ 5. drift vs 08-31 baseline
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    drift = {"config_drift": [], "unchanged": []}

    def cmp(label, before, after):
        (drift["config_drift"] if before != after else drift["unchanged"]).append(
            {"surface": label, "baseline_2026_08_31": before, "now_2026_09_01": after}
            if before != after else label)

    bc = {c["id"]: c for c in base["campaigns"] if c["status"] != "REMOVED"}
    cmp("campaign count (non-removed)", len(bc), len(camp_cfg))
    for i in CAMPAIGNS:
        o, n = bc.get(i, {}), camp_cfg.get(i, {})
        cmp(f"{i} name", o.get("name"), n.get("name"))
        cmp(f"{i} status", o.get("status"), n.get("status"))
        cmp(f"{i} serving_status", o.get("serving_status"), n.get("serving_status"))
        cmp(f"{i} bidding_strategy_type", o.get("bidding_strategy_type"),
            n.get("bidding_strategy_type"))
        cmp(f"{i} cpc_bid_ceiling_usd", o.get("cpc_bid_ceiling"), n.get("cpc_bid_ceiling_usd"))
        cmp(f"{i} search_partners", o.get("net_partner_search"), n.get("search_partners"))
        cmp(f"{i} display", o.get("net_display"), n.get("display_network"))
        cmp(f"{i} ai_max", o.get("ai_max"), n.get("ai_max"))
        cmp(f"{i} geo_positive", o.get("geo_positive"), n.get("geo_positive"))
        cmp(f"{i} geo_negative", o.get("geo_negative"), n.get("geo_negative"))
        cmp(f"{i} tracking_url_template", o.get("tracking_url_template"),
            n.get("tracking_url_template"))
    bb = {b["id"]: b for b in base["budgets"] if b["status"] != "REMOVED"}
    for i in CAMPAIGNS:
        bid = camp_cfg.get(i, {}).get("budget_id")
        cmp(f"{i} daily_budget_usd", bb.get(bid, {}).get("amount"),
            camp_cfg.get(i, {}).get("daily_budget_usd"))
    cmp("ad group count (non-removed)", len(base["ad_groups"]), sum(v["total"] for v in
                                                                   ag_by_camp.values()))
    cmp("ad groups ENABLED", sum(1 for a in base["ad_groups"] if a["status"] == "ENABLED"),
        sum(v["enabled"] for v in ag_by_camp.values()))
    cmp("keyword row count", len(base["keywords"]), sum(v["total"] for v in kw.values()))
    cmp("ad count (non-removed)", len(base["ads"]), sum(v["total"] for v in ads.values()))
    cmp("campaign negative keywords",
        sum(1 for c in base["campaign_criteria"] if c["type"] == "KEYWORD" and c["negative"]),
        sum(len(v) for v in negs.values()))
    cmp("ad-group negative keywords", 0, sum(agneg.values()))
    cmp("location criteria",
        sum(1 for c in base["campaign_criteria"] if c["type"] == "LOCATION"),
        sum(v["criterion_type_counts"].get("LOCATION", 0) for v in camp_cfg.values()))
    cmp("campaign_asset links", len(base["campaign_assets"]),
        sum(sum(v.values()) for v in assets.values()))
    cmp("USER_LIST criteria", 0, acct["audiences"])
    cmp("GENDER criteria", 0, acct["gender_criteria"])
    cmp("AGE_RANGE criteria", 0, acct["age_range_criteria"])
    cmp("INCOME_RANGE criteria", 0, acct["income_range_criteria"])
    cmp("IP_BLOCK criteria", 0, acct["ip_block_criteria"])
    cmp("customer_conversion_goal biddable count", 0,
        acct["customer_conversion_goals_biddable_count"])
    cmp("conversion actions with include_in_conversions_metric", 0,
        sum(1 for a in ca if a["include_in_conversions_metric"]))
    bca = {a["id"]: a["name"] for a in base["conversion_actions"]}
    cmp("conversion action id set", sorted(bca), sorted(a["id"] for a in ca))
    out["drift"] = drift
    out["drift_summary"] = {"surfaces_checked": len(drift["config_drift"]) +
                            len(drift["unchanged"]),
                            "config_drift_count": len(drift["config_drift"]),
                            "no_configuration_drift": not drift["config_drift"]}

    path = SNAP / f"sept1-continuation-{stamp}.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("campaign_configuration", "drift")}, indent=2, default=str))
    print("\nWROTE", path)
    print("\nCAMPAIGN CONFIG:\n", json.dumps(out["campaign_configuration"], indent=2,
                                             default=str))
    print("\nCONFIG DRIFT:\n", json.dumps(drift["config_drift"], indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
