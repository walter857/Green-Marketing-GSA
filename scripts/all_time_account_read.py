#!/usr/bin/env python3
"""Complete available-history read-only account read.

GAQL SELECT statements only, routed through the repository's read-only guard. Nothing is
written to Google Ads. Every query is isolated: one failure is recorded and skipped rather
than ending the run, so a single unsupported field never becomes a silent gap.

Output policy: aggregates and counts go to stdout. Row-level data, including every search
term, is written to a JSON snapshot on disk. Raw search-term strings are never printed.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.audit import ReadOnlyAudit as AuditReader, metrics_dict, scrub_text  # noqa: E402
from gm_gsa.config import load_dotenv_if_available, load_yaml  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402


def _name(value):
    try:
        return enum_name(value)
    except Exception:  # noqa: BLE001
        return str(value)


def windows_back(as_of: date, years: int = 6) -> list[tuple[str, str]]:
    """Yearly windows walking backwards, newest first. Keeps each query small."""
    out = []
    end = as_of
    for _ in range(years):
        start = end - timedelta(days=364)
        out.append((start.isoformat(), end.isoformat()))
        end = start - timedelta(days=1)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--years", type=int, default=6)
    args = parser.parse_args()

    profile = load_yaml(args.client)["client"]
    customer_id = str(profile["google_ads"]["child_customer_id"])
    expected_name = profile["google_ads"]["exact_child_account_name"]

    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    reader = AuditReader(client, customer_id)

    today = date.today()
    snap: dict = {
        "customer_id": customer_id,
        "expected_account_name": expected_name,
        "generated_on": today.isoformat(),
        "coverage": {},
        "campaigns": [],
        "ad_groups": [],
        "keywords": [],
        "search_terms": [],
        "ads": [],
        "assets": [],
        "conversion_actions": [],
        "segments": {},
        "month_to_date": {},
        "read_errors": [],
    }

    print("=" * 78)
    print("ALL-TIME ACCOUNT READ (read-only)")
    print("=" * 78)

    # --- identity re-confirmation inside this same process
    rows = reader.rows("customer", """
        SELECT customer.id, customer.descriptive_name, customer.currency_code,
               customer.time_zone, customer.status, customer.manager, customer.test_account
        FROM customer LIMIT 1
    """)
    if not rows:
        print("FAIL: could not read the customer record.")
        return 1
    c = rows[0].customer
    if c.descriptive_name != expected_name:
        print(f"FAIL: observed {c.descriptive_name!r}, expected {expected_name!r}. Stopping.")
        return 1
    snap["identity"] = {
        "id": str(c.id), "descriptive_name": c.descriptive_name,
        "currency_code": c.currency_code, "time_zone": c.time_zone,
        "status": _name(c.status), "manager": bool(c.manager),
        "test_account": bool(c.test_account),
    }
    print(f"\nIdentity confirmed: {c.descriptive_name!r} | {c.id} | {c.currency_code} | {c.time_zone}")

    # --- campaign inventory, every status, no date filter
    print("\n--- Campaign inventory (all statuses) ---")
    rows = reader.rows("campaigns", """
        SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
               campaign.advertising_channel_sub_type,
               campaign.bidding_strategy_type, campaign.campaign_budget,
               campaign.network_settings.target_google_search,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.network_settings.target_partner_search_network,
               campaign.geo_target_type_setting.positive_geo_target_type,
               campaign.geo_target_type_setting.negative_geo_target_type,
               campaign.tracking_url_template, campaign.serving_status,
               campaign.experiment_type
        FROM campaign
        ORDER BY campaign.id
    """)
    for r in rows:
        cp = r.campaign
        ns = cp.network_settings
        snap["campaigns"].append({
            "id": str(cp.id), "name": cp.name, "status": _name(cp.status),
            "channel": _name(cp.advertising_channel_type),
            "sub_type": _name(cp.advertising_channel_sub_type),
            "bidding_strategy_type": _name(cp.bidding_strategy_type),
            "budget_resource": cp.campaign_budget,
            "serving_status": _name(cp.serving_status),
            "experiment_type": _name(cp.experiment_type),
            "google_search": bool(ns.target_google_search),
            "search_network": bool(ns.target_search_network),
            "content_network": bool(ns.target_content_network),
            "partner_network": bool(ns.target_partner_search_network),
            "positive_geo": _name(cp.geo_target_type_setting.positive_geo_target_type),
            "negative_geo": _name(cp.geo_target_type_setting.negative_geo_target_type),
            "has_tracking_template": bool(cp.tracking_url_template),
        })
    by_status: dict[str, int] = {}
    for cp in snap["campaigns"]:
        by_status[cp["status"]] = by_status.get(cp["status"], 0) + 1
    print(f"Campaigns found: {len(snap['campaigns'])}  by status: {by_status or '(none)'}")
    for cp in snap["campaigns"]:
        print(f"  [{cp['status']:8}] {cp['id']}  {cp['name']!r}  ({cp['channel']})")

    # --- budgets
    rows = reader.rows("budgets", """
        SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
               campaign_budget.explicitly_shared, campaign_budget.status,
               campaign_budget.delivery_method, campaign_budget.resource_name
        FROM campaign_budget
    """)
    snap["budgets"] = [{
        "id": str(r.campaign_budget.id), "name": r.campaign_budget.name,
        "amount": r.campaign_budget.amount_micros / 1_000_000,
        "explicitly_shared": bool(r.campaign_budget.explicitly_shared),
        "status": _name(r.campaign_budget.status),
        "delivery": _name(r.campaign_budget.delivery_method),
        "resource_name": r.campaign_budget.resource_name,
    } for r in rows]
    print(f"\nBudgets found: {len(snap['budgets'])}")
    for b in snap["budgets"]:
        print(f"  {b['id']}  {b['name']!r}  ${b['amount']:.2f}/day  shared={b['explicitly_shared']}  {b['status']}")

    # --- coverage probe + campaign performance by year
    print("\n--- Data coverage probe (yearly windows, newest first) ---")
    coverage = []
    earliest = None
    latest = None
    for start, end in windows_back(today, args.years):
        rows = reader.rows(f"perf_{start}", f"""
            SELECT campaign.id, campaign.name, campaign.status, segments.date,
                   metrics.cost_micros, metrics.impressions, metrics.clicks,
                   metrics.conversions, metrics.conversions_value
            FROM campaign
            WHERE segments.date BETWEEN '{start}' AND '{end}'
        """)
        cost = sum(r.metrics.cost_micros for r in rows) / 1_000_000
        impr = sum(r.metrics.impressions for r in rows)
        clicks = sum(r.metrics.clicks for r in rows)
        conv = sum(r.metrics.conversions for r in rows)
        dates = [r.segments.date for r in rows]
        if dates:
            lo, hi = min(dates), max(dates)
            earliest = lo if earliest is None else min(earliest, lo)
            latest = hi if latest is None else max(latest, hi)
        coverage.append({
            "window": f"{start}..{end}", "rows": len(rows), "cost": round(cost, 2),
            "impressions": impr, "clicks": clicks, "conversions": round(conv, 2),
            "first_date": min(dates) if dates else None,
            "last_date": max(dates) if dates else None,
        })
        print(f"  {start}..{end}  rows={len(rows):6}  cost=${cost:10.2f}  impr={impr:8}  clicks={clicks:6}  conv={conv:7.2f}")
        for row in rows:
            snap.setdefault("campaign_daily", []).append({
                "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
                "status": _name(row.campaign.status), "date": row.segments.date,
                **metrics_dict(row.metrics),
            })
    snap["coverage"] = {"windows": coverage, "earliest_date_with_data": earliest,
                        "latest_date_with_data": latest}
    print(f"\nEarliest date with data: {earliest or '(none)'}")
    print(f"Latest date with data  : {latest or '(none)'}")

    # --- month to date
    mtd_start = today.replace(day=1).isoformat()
    rows = reader.rows("mtd", f"""
        SELECT campaign.id, campaign.name, campaign.status, metrics.cost_micros,
               metrics.impressions, metrics.clicks, metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '{mtd_start}' AND '{today.isoformat()}'
    """)
    mtd_cost = sum(r.metrics.cost_micros for r in rows) / 1_000_000
    snap["month_to_date"] = {
        "start": mtd_start, "end": today.isoformat(), "cost": round(mtd_cost, 2),
        "clicks": sum(r.metrics.clicks for r in rows),
        "impressions": sum(r.metrics.impressions for r in rows),
        "conversions": round(sum(r.metrics.conversions for r in rows), 2),
        "per_campaign": [{"id": str(r.campaign.id), "name": r.campaign.name,
                          "status": _name(r.campaign.status),
                          "cost": r.metrics.cost_micros / 1_000_000} for r in rows],
    }
    print(f"\nMonth-to-date ({mtd_start}..{today}): ${mtd_cost:.2f}")

    # --- ad groups / keywords / ads / conversions
    for label, key, query, mapper in [
        ("ad groups", "ad_groups", """
            SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.type,
                   campaign.id, campaign.name, campaign.status
            FROM ad_group ORDER BY ad_group.id
        """, lambda r: {"id": str(r.ad_group.id), "name": r.ad_group.name,
                        "status": _name(r.ad_group.status), "type": _name(r.ad_group.type_),
                        "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name}),
        ("keywords", "keywords", """
            SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                   ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                   ad_group_criterion.negative, ad_group.id, ad_group.name,
                   campaign.id, campaign.name
            FROM ad_group_criterion
            WHERE ad_group_criterion.type = KEYWORD
        """, lambda r: {"criterion_id": str(r.ad_group_criterion.criterion_id),
                        "text": r.ad_group_criterion.keyword.text,
                        "match_type": _name(r.ad_group_criterion.keyword.match_type),
                        "status": _name(r.ad_group_criterion.status),
                        "negative": bool(r.ad_group_criterion.negative),
                        "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
                        "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name}),
        ("conversion actions", "conversion_actions", """
            SELECT conversion_action.id, conversion_action.name, conversion_action.status,
                   conversion_action.type, conversion_action.category,
                   conversion_action.primary_for_goal,
                   conversion_action.counting_type,
                   conversion_action.attribution_model_settings.attribution_model,
                   conversion_action.phone_call_duration_seconds,
                   conversion_action.click_through_lookback_window_days,
                   conversion_action.include_in_conversions_metric
            FROM conversion_action
        """, lambda r: {"id": str(r.conversion_action.id), "name": r.conversion_action.name,
                        "status": _name(r.conversion_action.status),
                        "type": _name(r.conversion_action.type_),
                        "category": _name(r.conversion_action.category),
                        "primary_for_goal": bool(r.conversion_action.primary_for_goal),
                        "counting_type": _name(r.conversion_action.counting_type),
                        "attribution": _name(r.conversion_action.attribution_model_settings.attribution_model),
                        "phone_call_duration_seconds": r.conversion_action.phone_call_duration_seconds,
                        "lookback_days": r.conversion_action.click_through_lookback_window_days,
                        "included_in_conversions": bool(r.conversion_action.include_in_conversions_metric)}),
    ]:
        rows = reader.rows(key, query)
        snap[key] = [mapper(r) for r in rows]
        print(f"\n{label.capitalize()} found: {len(snap[key])}")

    for ca in snap["conversion_actions"]:
        print(f"  [{ca['status']:8}] {ca['name']!r}  type={ca['type']}  primary={ca['primary_for_goal']}  counting={ca['counting_type']}")

    # --- ads
    rows = reader.rows("ads", """
        SELECT ad_group_ad.ad.id, ad_group_ad.ad.type, ad_group_ad.status,
               ad_group_ad.policy_summary.approval_status,
               ad_group_ad.ad.final_urls,
               ad_group_ad.ad.responsive_search_ad.headlines,
               ad_group_ad.ad.responsive_search_ad.descriptions,
               ad_group_ad.ad.responsive_search_ad.path1,
               ad_group_ad.ad.responsive_search_ad.path2,
               ad_group.id, ad_group.name, campaign.id, campaign.name
        FROM ad_group_ad
    """)
    for r in rows:
        ad = r.ad_group_ad.ad
        rsa = ad.responsive_search_ad
        snap["ads"].append({
            "ad_id": str(ad.id), "type": _name(ad.type_),
            "status": _name(r.ad_group_ad.status),
            "approval": _name(r.ad_group_ad.policy_summary.approval_status),
            "final_urls": list(ad.final_urls),
            "headlines": [a.text for a in rsa.headlines],
            "descriptions": [a.text for a in rsa.descriptions],
            "path1": rsa.path1, "path2": rsa.path2,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
        })
    print(f"\nAds found: {len(snap['ads'])}")

    # --- assets
    rows = reader.rows("assets", """
        SELECT asset.id, asset.type, asset.name,
               asset.sitelink_asset.link_text, asset.callout_asset.callout_text,
               asset.structured_snippet_asset.header,
               asset.structured_snippet_asset.values,
               asset.call_asset.phone_number, asset.final_urls
        FROM asset
    """)
    snap["assets"] = [{
        "id": str(r.asset.id), "type": _name(r.asset.type_), "name": r.asset.name,
        "sitelink_text": r.asset.sitelink_asset.link_text,
        "callout_text": r.asset.callout_asset.callout_text,
        "snippet_header": r.asset.structured_snippet_asset.header,
        "snippet_values": list(r.asset.structured_snippet_asset.values),
        "has_call_number": bool(r.asset.call_asset.phone_number),
        "final_urls": list(r.asset.final_urls),
    } for r in rows]
    print(f"Assets found: {len(snap['assets'])}")

    # --- search terms across every campaign, yearly windows
    print("\n--- Search terms (all campaigns, yearly windows) ---")
    seen_terms = 0
    for start, end in windows_back(today, args.years):
        rows = reader.rows(f"terms_{start}", f"""
            SELECT search_term_view.search_term, search_term_view.status,
                   campaign.id, campaign.name, ad_group.id, ad_group.name,
                   segments.keyword.info.text, segments.keyword.info.match_type,
                   metrics.impressions, metrics.clicks, metrics.cost_micros,
                   metrics.conversions, metrics.conversions_value
            FROM search_term_view
            WHERE segments.date BETWEEN '{start}' AND '{end}'
        """)
        for r in rows:
            snap["search_terms"].append({
                "term": scrub_text(r.search_term_view.search_term),
                "status": _name(r.search_term_view.status),
                "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
                "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
                "matched_keyword": r.segments.keyword.info.text,
                "matched_match_type": _name(r.segments.keyword.info.match_type),
                "window": f"{start}..{end}",
                "impressions": int(r.metrics.impressions), "clicks": int(r.metrics.clicks),
                "cost": r.metrics.cost_micros / 1_000_000,
                "conversions": float(r.metrics.conversions),
                "conversions_value": float(r.metrics.conversions_value),
            })
        seen_terms += len(rows)
        print(f"  {start}..{end}  search-term rows={len(rows)}")
    print(f"Total search-term rows: {seen_terms}")

    # --- segments
    for seg_label, seg_field in [("device", "segments.device"),
                                 ("day_of_week", "segments.day_of_week"),
                                 ("network", "segments.ad_network_type")]:
        rows = reader.rows(f"seg_{seg_label}", f"""
            SELECT {seg_field}, metrics.impressions, metrics.clicks,
                   metrics.cost_micros, metrics.conversions
            FROM campaign
            WHERE segments.date BETWEEN '{(today - timedelta(days=364)).isoformat()}'
                                    AND '{today.isoformat()}'
        """)
        agg: dict[str, dict] = {}
        for r in rows:
            key = _name(getattr(r.segments, seg_field.split(".")[-1]))
            bucket = agg.setdefault(key, {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
            bucket["impressions"] += int(r.metrics.impressions)
            bucket["clicks"] += int(r.metrics.clicks)
            bucket["cost"] += r.metrics.cost_micros / 1_000_000
            bucket["conversions"] += float(r.metrics.conversions)
        snap["segments"][seg_label] = agg

    snap["read_errors"] = reader.read_errors
    snap["queries_executed"] = reader.queries_executed

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snap, indent=2, default=str), encoding="utf-8")

    print(f"\n--- Read errors: {len(reader.read_errors)} ---")
    for err in reader.read_errors:
        print(f"  {err['query']}: {err['error'][:150]}")
    print(f"\nSnapshot written: {out}")
    print(f"Queries executed: {len(reader.queries_executed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
