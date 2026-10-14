#!/usr/bin/env python3
"""Read-only Google Ads account audit.

Validates the work order and client profile, confirms account identity and the
manager relationship with a fresh lookup, then runs GAQL SELECT queries only and
writes a redacted snapshot. It never creates, edits, pauses, enables, removes,
deletes, uploads, or publishes anything.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa import audit as A
from gm_gsa.config import load_dotenv_if_available, load_yaml, normalize_customer_id
from gm_gsa.safety import assert_no_embedded_secrets, redact_secrets
from gm_gsa.service_discovery import (
    DiscoveryError,
    DiscoveryTarget,
    assert_discovery_identity,
    assert_manager_link,
    get_manager_link,
)
from gm_gsa.work_orders import assert_valid_work_order


def build_target(order: dict, profile: dict) -> DiscoveryTarget:
    account = order["work_order"]["account"]
    ads = profile["client"]["google_ads"]
    return DiscoveryTarget(
        client_slug=order["work_order"]["client_slug"],
        business_name=order["work_order"]["business_name"],
        exact_child_account_name=account["exact_child_account_name"],
        child_customer_id=normalize_customer_id(account["child_customer_id"]),
        manager_customer_id=normalize_customer_id(
            account.get("manager_customer_id") or ads["manager_customer_id"]
        ),
    )


def collect_window(runner: A.ReadOnlyAudit, window: A.DateWindow) -> dict:
    label = window.label

    def q(name, query, mapper):
        return [mapper(row) for row in runner.rows(f"{name}[{label}]", query)]

    customer_rows = [
        {
            **A.metrics_dict(row.metrics),
            "invalid_clicks": int(getattr(row.metrics, "invalid_clicks", 0)),
            "invalid_click_rate": float(getattr(row.metrics, "invalid_click_rate", 0.0)),
        }
        for row in runner.rows(f"customer[{label}]", A.customer_query(window))
    ]
    phone = [
        {
            "campaign_name": row.campaign.name or "",
            "phone_calls": int(row.metrics.phone_calls),
            "phone_impressions": int(row.metrics.phone_impressions),
            "phone_through_rate": float(row.metrics.phone_through_rate),
        }
        for row in runner.rows(f"phone_metrics[{label}]", A.phone_metrics_query(window))
    ]
    campaigns = [
        {
            "campaign_id": str(row.campaign.id),
            "campaign_name": row.campaign.name or "",
            "status": A.enum_name(row.campaign.status),
            "channel_type": A.enum_name(row.campaign.advertising_channel_type),
            "daily_budget": (row.campaign_budget.amount_micros or 0) / 1_000_000,
            "invalid_clicks": int(getattr(row.metrics, "invalid_clicks", 0)),
            **A.metrics_dict(row.metrics),
        }
        for row in runner.rows(
            f"campaign_performance[{label}]", A.campaign_performance_query(window)
        )
    ]
    ad_groups = [
        {
            "campaign_id": str(row.campaign.id),
            "campaign_name": row.campaign.name or "",
            "ad_group_id": str(row.ad_group.id),
            "ad_group_name": row.ad_group.name or "",
            "status": A.enum_name(row.ad_group.status),
            **A.metrics_dict(row.metrics),
        }
        for row in runner.rows(
            f"ad_group_performance[{label}]", A.ad_group_performance_query(window)
        )
    ]

    segments = {}
    for name, expression in (
        ("device", "segments.device"),
        ("network", "segments.ad_network_type"),
        ("day_of_week", "segments.day_of_week"),
        ("hour", "segments.hour"),
    ):
        rows = runner.rows(f"segment_{name}[{label}]", A._segment_query(window, expression))
        segments[name] = [
            {
                "campaign_name": row.campaign.name or "",
                "value": A.enum_name(getattr(row.segments, expression.split(".")[-1])),
                **A.metrics_dict(row.metrics),
            }
            for row in rows
        ]

    geo = [
        {
            "campaign_name": row.campaign.name or "",
            "location_type": A.enum_name(row.geographic_view.location_type),
            "geo_target_city": str(row.segments.geo_target_city or ""),
            "geo_target_metro": str(row.segments.geo_target_metro or ""),
            **A.metrics_dict(row.metrics),
        }
        for row in runner.rows(f"geographic_view[{label}]", A.geo_query(window))
    ]

    daily = [
        {
            "campaign_name": row.campaign.name or "",
            "date": str(row.segments.date),
            **A.metrics_dict(row.metrics),
        }
        for row in runner.rows(f"daily_series[{label}]", A.daily_series_query(window))
    ]

    return {
        "window": window.to_dict(),
        "customer": customer_rows[0] if customer_rows else None,
        "phone": phone,
        "campaigns": campaigns,
        "ad_groups": ad_groups,
        "keywords": q("keyword_performance", A.keyword_performance_query(window), A.map_keyword),
        "search_terms": q("search_terms", A.search_term_query(window), A.map_search_term),
        "ads": q("ad_performance", A.ad_performance_query(window), A.map_ad),
        "ad_assets": q(
            "ad_asset_performance", A.ad_asset_performance_query(window), A.map_ad_asset
        ),
        "conversion_breakdown": q(
            "conversion_breakdown", A.conversion_breakdown_query(window), A.map_conversion_breakdown
        ),
        "segments": segments,
        "geo": geo,
        "daily": daily,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-order", required=True)
    parser.add_argument("--client", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--as-of", default=date.today().isoformat())
    args = parser.parse_args()

    order = load_yaml(args.work_order)
    profile = load_yaml(args.client)
    assert_valid_work_order(order, profile)
    task = order["work_order"]["task"]
    if task["mode"] != "read" or task["type"] != "audit":
        print("STOP: this command only runs a read-only audit work order.")
        return 1
    target = build_target(order, profile)
    windows = A.audit_windows(date.fromisoformat(args.as_of))

    print("Read-only audit target")
    print(f"  Account   : {target.exact_child_account_name}")
    print(f"  Child ID  : {target.child_customer_id}")
    print(f"  Manager ID: {target.manager_customer_id}")
    print(f"  Service   : {order['work_order']['service']['exact_primary_service']}")
    for window in windows:
        print(f"  {window.label:12}: {window.start} .. {window.end}")

    load_dotenv_if_available(ROOT / ".env")
    from gm_gsa.credentials import google_ads_config, load_google_ads_client

    if google_ads_config()["login_customer_id"] != target.manager_customer_id:
        print("\nSTOP: configured login customer ID does not match the work-order manager ID.")
        return 1
    google_client = load_google_ads_client()

    from gm_gsa.google_ads import get_customer_identity

    try:
        identity = get_customer_identity(google_client, target.child_customer_id)
        assert_discovery_identity(identity, target)
        link = get_manager_link(
            google_client, target.manager_customer_id, target.child_customer_id
        )
        assert_manager_link(link, target)
    except DiscoveryError as exc:
        print(f"\nSTOP: {exc}")
        return 1

    print("\nIdentity verification")
    print(f"  name={identity.descriptive_name} id={identity.customer_id}")
    print(f"  currency={identity.currency_code} time_zone={identity.time_zone}")
    print(f"  manager={identity.manager} test_account={identity.test_account}")
    print(f"  manager link: level {link.level} under {link.manager_customer_id} ({link.status})")

    runner = A.ReadOnlyAudit(google_client, target.child_customer_id)
    settings = {
        "conversion_actions": [
            A.map_conversion_action(row)
            for row in runner.rows("conversion_action", A.CONVERSION_ACTION_QUERY)
        ],
        "campaigns": [
            A.map_campaign_settings(row)
            for row in runner.rows("campaign_settings", A.CAMPAIGN_SETTINGS_QUERY)
        ],
        "campaign_criteria": [
            A.map_campaign_criterion(row)
            for row in runner.rows("campaign_criterion", A.CAMPAIGN_CRITERION_QUERY)
        ],
        "negative_keywords_ad_group": [
            {
                "campaign_name": row.campaign.name or "",
                "ad_group_name": row.ad_group.name or "",
                "criterion_id": str(row.ad_group_criterion.criterion_id),
                "text": row.ad_group_criterion.keyword.text or "",
                "match_type": A.enum_name(row.ad_group_criterion.keyword.match_type),
            }
            for row in runner.rows(
                "ad_group_negatives", A.AD_GROUP_CRITERION_NEGATIVE_QUERY
            )
        ],
        "shared_sets": [
            {
                "id": str(row.shared_set.id),
                "name": row.shared_set.name or "",
                "type": A.enum_name(row.shared_set.type_),
                "status": A.enum_name(row.shared_set.status),
                "member_count": int(row.shared_set.member_count),
            }
            for row in runner.rows("shared_set", A.SHARED_SET_QUERY)
        ],
        "shared_criteria": [
            {
                "shared_set_name": row.shared_set.name or "",
                "criterion_id": str(row.shared_criterion.criterion_id),
                "text": row.shared_criterion.keyword.text or "",
                "match_type": A.enum_name(row.shared_criterion.keyword.match_type),
            }
            for row in runner.rows("shared_criterion", A.SHARED_CRITERION_QUERY)
        ],
        "campaign_shared_sets": [
            {
                "campaign_name": row.campaign.name or "",
                "shared_set_name": row.shared_set.name or "",
                "type": A.enum_name(row.shared_set.type_),
                "status": A.enum_name(row.campaign_shared_set.status),
            }
            for row in runner.rows("campaign_shared_set", A.CAMPAIGN_SHARED_SET_QUERY)
        ],
        "assets": [
            A.map_asset_policy(row) for row in runner.rows("asset_policy", A.ASSET_POLICY_QUERY)
        ],
    }

    geo_names = {
        item["geo_target_constant"]
        for item in settings["campaign_criteria"]
        if item.get("geo_target_constant")
    }
    if geo_names:
        settings["geo_target_constants"] = [
            {
                "id": str(row.geo_target_constant.id),
                "name": row.geo_target_constant.name or "",
                "canonical_name": row.geo_target_constant.canonical_name or "",
                "target_type": row.geo_target_constant.target_type or "",
                "country_code": row.geo_target_constant.country_code or "",
            }
            for row in runner.rows(
                "geo_target_constant", A.geo_target_constant_query(geo_names)
            )
        ]

    by_window = {window.label: collect_window(runner, window) for window in windows}

    report = {
        "workflow": "read-only-account-audit",
        "as_of": args.as_of,
        "target": target.to_dict(),
        "service": order["work_order"]["service"],
        "identity": identity.to_dict(),
        "manager_link": link.to_dict(),
        "windows": [window.to_dict() for window in windows],
        "settings": settings,
        "by_window": by_window,
        "read_errors": runner.read_errors,
        "queries_executed": runner.queries_executed,
        "google_ads_changes_made": False,
    }
    report = redact_secrets(report)
    assert_no_embedded_secrets(report)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\nQueries executed: {len(runner.queries_executed)}")
    if runner.read_errors:
        print(f"Read errors ({len(runner.read_errors)}):")
        for failure in runner.read_errors:
            print(f"- {failure['query']}: {failure['error']}")
    for label, data in by_window.items():
        customer = data["customer"] or {}
        print(
            f"{label:12} cost={customer.get('cost')} clicks={customer.get('clicks')} "
            f"conv={customer.get('conversions')} all_conv={customer.get('all_conversions')}"
        )
    print(f"\nWrote redacted audit snapshot: {output}")
    print("No Google Ads changes were made. This audit is read-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
