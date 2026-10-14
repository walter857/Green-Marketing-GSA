#!/usr/bin/env python3
"""Continuation drift check for the 2026-08-31 Softwind recovery audit.

Fresh read-only identity gate, then a targeted re-read of every configuration
surface, compared against the opening forensic snapshot. Classifies each
difference as EXPECTED METRIC DRIFT, CONFIGURATION DRIFT or MANUAL OWNER CHANGE.

SELECT statements only. Constructs no operation, calls no mutate service.
"""
from __future__ import annotations

import glob
import json
import sys
from collections import Counter, defaultdict
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

# The four links the interrupted run detected as owner-made, 10:21 -> 10:52.
KNOWN_OWNER_LINKS = {
    ("24103511039", "413928453094", "SITELINK"),
    ("24103511039", "404844116658", "STRUCTURED_SNIPPET"),
    ("24103511039", "404773124911", "CALLOUT"),
    ("24145053510", "404773124911", "CALLOUT"),
}


def micros(v) -> float:
    return round(int(v) / 1_000_000, 4)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    # ---------------- identity gate ----------------
    r = q("""SELECT customer.id, customer.descriptive_name, customer.currency_code,
                    customer.time_zone, customer.manager, customer.test_account,
                    customer.status, customer.auto_tagging_enabled,
                    customer.tracking_url_template, customer.final_url_suffix,
                    customer.optimization_score
             FROM customer LIMIT 1""")[0].customer
    tz = r.time_zone or "America/New_York"
    now = datetime.now(ZoneInfo(tz))
    identity = {
        "customer_id": normalize_customer_id(r.id),
        "descriptive_name": r.descriptive_name,
        "currency": r.currency_code,
        "time_zone": tz,
        "manager": bool(r.manager),
        "test_account": bool(r.test_account),
        "status": enum_name(r.status),
        "auto_tagging_enabled": bool(r.auto_tagging_enabled),
        "tracking_url_template": r.tracking_url_template or "",
        "final_url_suffix": r.final_url_suffix or "",
        "optimization_score": round(float(r.optimization_score or 0), 6),
        "live_marker_present": "- live" in (r.descriptive_name or "").lower(),
        "checked_account_local": now.isoformat(),
    }
    gate = {
        "name_matches": identity["descriptive_name"] == EXPECTED_NAME,
        "id_matches": identity["customer_id"] == CID,
        "not_manager": identity["manager"] is False,
        "not_test": identity["test_account"] is False,
        "live_marker": identity["live_marker_present"],
    }
    if not all(gate.values()):
        print("IDENTITY GATE FAILED:", json.dumps(gate, indent=2))
        return 2

    opening = json.loads(
        Path(sorted(glob.glob(str(SNAP / "forensic-structure-*.json")))[0])
        .read_text(encoding="utf-8"))

    config_drift: list[dict] = []
    owner_changes: list[dict] = []
    metric_drift: list[dict] = []
    unchanged: list[str] = []

    def cmp(label, before, after, bucket=None):
        if before == after:
            unchanged.append(label)
            return
        row = {"surface": label, "opening_10_21": before, "now": after}
        (bucket if bucket is not None else config_drift).append(row)

    # ---------------- campaigns ----------------
    rows = q("""SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
                       campaign.primary_status, campaign.primary_status_reasons,
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
                       campaign.tracking_url_template, campaign.final_url_suffix
                FROM campaign WHERE campaign.status != 'REMOVED'""")
    ob = {c["id"]: c for c in opening["campaigns"] if c["status"] != "REMOVED"}
    cmp("campaign count (non-removed)", len(ob), len(rows))
    live_now = {}
    for row in rows:
        c = row.campaign
        i = str(c.id)
        o = ob.get(i, {})
        live_now[i] = c
        cmp(f"campaign {i} name", o.get("name"), c.name)
        cmp(f"campaign {i} status", o.get("status"), enum_name(c.status))
        cmp(f"campaign {i} serving_status", o.get("serving_status"), enum_name(c.serving_status))
        cmp(f"campaign {i} primary_status", o.get("primary_status"), enum_name(c.primary_status),
            metric_drift)
        cmp(f"campaign {i} bidding_strategy_type", o.get("bidding_strategy_type"),
            enum_name(c.bidding_strategy_type))
        cmp(f"campaign {i} cpc_bid_ceiling_usd", o.get("cpc_bid_ceiling"),
            micros(c.target_spend.cpc_bid_ceiling_micros))
        cmp(f"campaign {i} budget_id", o.get("budget_id"), c.campaign_budget.split("/")[-1])
        cmp(f"campaign {i} search_partners", o.get("net_search_partners"),
            bool(c.network_settings.target_search_network))
        cmp(f"campaign {i} display", o.get("net_display"),
            bool(c.network_settings.target_content_network))
        cmp(f"campaign {i} partner_search", o.get("net_partner_search"),
            bool(c.network_settings.target_partner_search_network))
        cmp(f"campaign {i} geo_positive", o.get("geo_positive"),
            enum_name(c.geo_target_type_setting.positive_geo_target_type))
        cmp(f"campaign {i} geo_negative", o.get("geo_negative"),
            enum_name(c.geo_target_type_setting.negative_geo_target_type))
        cmp(f"campaign {i} ai_max", o.get("ai_max"), bool(c.ai_max_setting.enable_ai_max))
        cmp(f"campaign {i} asset_automation",
            {a["type"]: a["status"] for a in o.get("asset_automation", [])},
            {enum_name(a.asset_automation_type): enum_name(a.asset_automation_status)
             for a in c.asset_automation_settings})
        cmp(f"campaign {i} tracking_url_template", o.get("tracking_url_template"),
            c.tracking_url_template or "")
        cmp(f"campaign {i} final_url_suffix", o.get("final_url_suffix"),
            c.final_url_suffix or "")

    # ---------------- budgets ----------------
    rows = q("""SELECT campaign_budget.id, campaign_budget.amount_micros,
                       campaign_budget.status, campaign_budget.delivery_method
                FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'""")
    ob = {b["id"]: b for b in opening["budgets"] if b["status"] != "REMOVED"}
    cmp("budget count", len(ob), len(rows))
    budgets_now = {}
    for row in rows:
        b = row.campaign_budget
        o = ob.get(str(b.id), {})
        budgets_now[str(b.id)] = micros(b.amount_micros)
        cmp(f"budget {b.id} amount_usd", o.get("amount"), micros(b.amount_micros))
        cmp(f"budget {b.id} delivery", o.get("delivery"), enum_name(b.delivery_method))

    # ---------------- ad groups ----------------
    rows = q("""SELECT ad_group.id, ad_group.name, ad_group.status
                FROM ad_group WHERE ad_group.status != 'REMOVED'""")
    after = {str(r.ad_group.id): (r.ad_group.name, enum_name(r.ad_group.status)) for r in rows}
    before = {a["ad_group_id"]: (a["ad_group_name"], a["status"]) for a in opening["ad_groups"]}
    cmp("ad group count", len(before), len(after))
    cmp("ad group name+status map", before, after)

    # ---------------- keywords ----------------
    rows = q("""SELECT ad_group.id, ad_group_criterion.criterion_id,
                       ad_group_criterion.keyword.text,
                       ad_group_criterion.keyword.match_type,
                       ad_group_criterion.status, ad_group_criterion.approval_status,
                       ad_group_criterion.system_serving_status
                FROM keyword_view""")
    after = sorted((str(r.ad_group.id), r.ad_group_criterion.keyword.text,
                    enum_name(r.ad_group_criterion.keyword.match_type),
                    enum_name(r.ad_group_criterion.status)) for r in rows)
    before = sorted((k["ad_group_id"], k["text"], k["match_type"], k["status"])
                    for k in opening["keywords"])
    cmp("keyword count", len(before), len(after))
    cmp("keyword set (ad_group, text, match, status)", before == after, True)
    cmp("keywords not APPROVED", 0,
        sum(1 for r in rows if enum_name(r.ad_group_criterion.approval_status) != "APPROVED"))
    cmp("keywords not ELIGIBLE", 0,
        sum(1 for r in rows
            if enum_name(r.ad_group_criterion.system_serving_status) != "ELIGIBLE"))

    # ---------------- ads ----------------
    rows = q("""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                       ad_group_ad.policy_summary.approval_status,
                       ad_group_ad.ad.final_urls
                FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'""")
    after = {str(r.ad_group_ad.ad.id): enum_name(r.ad_group_ad.status) for r in rows}
    before = {a["ad_id"]: a["status"] for a in opening["ads"]}
    cmp("ad count", len(before), len(after))
    cmp("ad id+status map", before, after)
    cmp("ads not APPROVED", 0,
        sum(1 for r in rows
            if enum_name(r.ad_group_ad.policy_summary.approval_status) != "APPROVED"))
    urls_after = sorted({u for r in rows for u in r.ad_group_ad.ad.final_urls})
    urls_before = sorted({u for a in opening["ads"] for u in a["final_urls"]})
    cmp("distinct ad final URLs", urls_before, urls_after)

    # ---------------- campaign criteria ----------------
    rows = q("""SELECT campaign.id, campaign_criterion.type, campaign_criterion.negative,
                       campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
                       campaign_criterion.location.geo_target_constant,
                       campaign_criterion.ad_schedule.day_of_week,
                       campaign_criterion.ad_schedule.start_hour,
                       campaign_criterion.ad_schedule.end_hour
                FROM campaign_criterion WHERE campaign_criterion.status != 'REMOVED'""")
    negs_after = sorted((str(r.campaign.id), r.campaign_criterion.keyword.text,
                         enum_name(r.campaign_criterion.keyword.match_type))
                        for r in rows
                        if enum_name(r.campaign_criterion.type_) == "KEYWORD"
                        and r.campaign_criterion.negative)
    negs_before = sorted((c["campaign_id"], c["text"], c["match_type"])
                         for c in opening["campaign_criteria"]
                         if c["type"] == "KEYWORD" and c["negative"])
    cmp("campaign negative keyword count", len(negs_before), len(negs_after))
    cmp("campaign negative keyword set", negs_before == negs_after, True)

    loc_after = sorted((str(r.campaign.id),
                        (r.campaign_criterion.location.geo_target_constant or "").split("/")[-1],
                        bool(r.campaign_criterion.negative))
                       for r in rows if enum_name(r.campaign_criterion.type_) == "LOCATION")
    loc_before = sorted((c["campaign_id"], c["geo_id"], c["negative"])
                        for c in opening["campaign_criteria"] if c["type"] == "LOCATION")
    cmp("location criterion count", len(loc_before), len(loc_after))
    cmp("location criterion set", loc_before == loc_after, True)

    sch_after = sorted((str(r.campaign.id), enum_name(r.campaign_criterion.ad_schedule.day_of_week),
                        int(r.campaign_criterion.ad_schedule.start_hour),
                        int(r.campaign_criterion.ad_schedule.end_hour))
                       for r in rows if enum_name(r.campaign_criterion.type_) == "AD_SCHEDULE")
    sch_before = sorted((c["campaign_id"], c["day"], c["start_hour"], c["end_hour"])
                        for c in opening["campaign_criteria"] if c["type"] == "AD_SCHEDULE")
    cmp("ad schedule set", sch_before, sch_after)
    for t in ("GENDER", "AGE_RANGE", "INCOME_RANGE", "USER_LIST", "IP_BLOCK"):
        cmp(f"{t} criteria count",
            sum(1 for c in opening["campaign_criteria"] if c["type"] == t),
            sum(1 for r in rows if enum_name(r.campaign_criterion.type_) == t))

    # ---------------- assets ----------------
    rows = q("""SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type,
                       campaign_asset.status, campaign_asset.primary_status
                FROM campaign_asset WHERE campaign_asset.status != 'REMOVED'""")
    ca_after = {(str(r.campaign.id), r.campaign_asset.asset.split("/")[-1],
                 enum_name(r.campaign_asset.field_type)) for r in rows}
    ca_before = {(c["campaign_id"], c["asset_id"], c["field_type"])
                 for c in opening["campaign_assets"]}
    new_links = ca_after - ca_before
    lost_links = ca_before - ca_after
    if new_links or lost_links:
        owner_changes.append({
            "surface": "campaign_asset links",
            "opening_10_21": len(ca_before),
            "now": len(ca_after),
            "added": sorted(new_links),
            "removed": sorted(lost_links),
            "all_added_are_known_owner_links": new_links == KNOWN_OWNER_LINKS,
            "unexpected_added": sorted(new_links - KNOWN_OWNER_LINKS),
        })
    else:
        unchanged.append("campaign_asset links")

    ca_counts = defaultdict(Counter)
    for camp, aid, ft in ca_after:
        ca_counts[camp][ft] += 1

    rows = q("""SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status
                FROM customer_asset WHERE customer_asset.status != 'REMOVED'""")
    acct_after = sorted((r.customer_asset.asset.split("/")[-1],
                         enum_name(r.customer_asset.field_type)) for r in rows)
    acct_before = sorted((c["asset_id"], c["field_type"]) for c in opening["customer_assets"])
    cmp("account-level asset links", acct_before, acct_after)

    rows = q("""SELECT ad_group_asset.asset FROM ad_group_asset
                WHERE ad_group_asset.status != 'REMOVED'""")
    cmp("ad-group asset links", len(opening["ad_group_assets"]), len(rows))

    # ---------------- conversion actions ----------------
    rows = q("""SELECT conversion_action.id, conversion_action.name, conversion_action.status,
                       conversion_action.primary_for_goal,
                       conversion_action.include_in_conversions_metric,
                       conversion_action.counting_type
                FROM conversion_action""")
    after = {str(r.conversion_action.id): (
        r.conversion_action.name, enum_name(r.conversion_action.status),
        bool(r.conversion_action.primary_for_goal),
        bool(r.conversion_action.include_in_conversions_metric)) for r in rows}
    before = {a["id"]: (a["name"], a["status"], a["primary_for_goal"],
                        a["include_in_conversions_metric"])
              for a in opening["conversion_actions"]}
    cmp("conversion actions", before, after)

    rows = q("""SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
                       customer_conversion_goal.biddable FROM customer_conversion_goal""")
    cmp("customer_conversion_goal biddable count", 0,
        sum(1 for r in rows if r.customer_conversion_goal.biddable))

    # ---------------- live metrics (expected drift) ----------------
    rows = q("""SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks,
                       metrics.cost_micros, metrics.conversions, metrics.all_conversions
                FROM campaign WHERE campaign.status != 'REMOVED'""")
    live = {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0,
            "all_conversions": 0.0, "per_campaign": {}}
    for r in rows:
        m = r.metrics
        live["per_campaign"][str(r.campaign.id)] = {
            "name": r.campaign.name, "impressions": int(m.impressions),
            "clicks": int(m.clicks), "cost": micros(m.cost_micros),
            "conversions": round(float(m.conversions), 4),
            "all_conversions": round(float(m.all_conversions), 4)}
        live["impressions"] += int(m.impressions)
        live["clicks"] += int(m.clicks)
        live["cost"] += micros(m.cost_micros)
        live["conversions"] += float(m.conversions)
        live["all_conversions"] += float(m.all_conversions)
    live["cost"] = round(live["cost"], 2)
    snap_tot = {"impressions": 0, "clicks": 0, "cost": 0.0}
    for c in opening["campaigns"]:
        if c["status"] != "REMOVED":
            for k in snap_tot:
                snap_tot[k] += c["metrics_all_time"][k]
    snap_tot["cost"] = round(snap_tot["cost"], 2)
    for k in ("impressions", "clicks", "cost"):
        if snap_tot[k] != live[k]:
            metric_drift.append({"surface": f"all-time {k}",
                                 "audit_snapshot_10_21": snap_tot[k], "current_live": live[k]})

    out = {
        "generated_account_local": now.isoformat(),
        "mode": "READ-ONLY",
        "identity": identity,
        "identity_gate": gate,
        "identity_gate_pass": all(gate.values()),
        "surfaces_checked": len(unchanged) + len(config_drift) + len(owner_changes)
                            + len(metric_drift),
        "unchanged_count": len(unchanged),
        "configuration_drift": config_drift,
        "manual_owner_changes": owner_changes,
        "expected_metric_drift": metric_drift,
        "audit_snapshot_totals": snap_tot,
        "current_live_totals": live,
        "campaign_asset_counts_now": {k: dict(v) for k, v in ca_counts.items()},
        "budgets_now": budgets_now,
        "unchanged_surfaces": sorted(unchanged),
    }
    p = SNAP / f"continuation-drift-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("IDENTITY GATE: PASS")
    for k, v in identity.items():
        print(f"  {k}: {v}")
    print(f"\nSURFACES CHECKED: {out['surfaces_checked']}   UNCHANGED: {len(unchanged)}")
    print(f"CONFIGURATION DRIFT: {len(config_drift)}")
    for d in config_drift:
        print(f"  ! {d['surface']}: {d['opening_10_21']!r} -> {d['now']!r}")
    print(f"MANUAL OWNER CHANGES: {len(owner_changes)}")
    for d in owner_changes:
        print(f"  * {d['surface']}: {d['opening_10_21']} -> {d['now']}")
        print(f"      added={d['added']}")
        print(f"      removed={d['removed']}")
        print(f"      all added are the 4 known owner links: {d['all_added_are_known_owner_links']}")
        print(f"      unexpected: {d['unexpected_added'] or 'none'}")
    print(f"EXPECTED METRIC DRIFT: {len(metric_drift)}")
    for d in metric_drift:
        print(f"  ~ {d}")
    print("\nCAMPAIGN ASSET COUNTS NOW:")
    for camp, cnt in ca_counts.items():
        print(f"  {camp}: {dict(cnt)}")
    print(f"\nWROTE {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
