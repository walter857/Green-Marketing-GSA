#!/usr/bin/env python3
"""2026-09-26 READ-ONLY: custom conversion goal contents, conversion action types, campaign assets."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from google.protobuf.json_format import MessageToDict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import SNAP, client, q  # noqa: E402

OUT = SNAP / "audit-2026-09-26"
c = client()


def run(name, query):
    try:
        rows = [MessageToDict(r._pb, preserving_proto_field_name=True) for r in q(c, query)]
    except Exception as exc:  # noqa: BLE001
        print(f"  [ERR] {name}: {str(exc)[:400]}")
        return None
    (OUT / f"{name}.json").write_text(json.dumps(rows, indent=0), encoding="utf-8")
    print(f"  [OK ] {name}: {len(rows)} rows")
    return rows


run("custom_conversion_goals", """
SELECT custom_conversion_goal.id, custom_conversion_goal.name,
       custom_conversion_goal.conversion_actions, custom_conversion_goal.status
FROM custom_conversion_goal""")

run("conversion_action_types", """
SELECT conversion_action.id, conversion_action.name, conversion_action.type,
       conversion_action.status, conversion_action.google_analytics_4_settings.event_name,
       conversion_action.third_party_app_analytics_settings.provider_name
FROM conversion_action""")

run("campaign_assets", """
SELECT campaign.id, campaign.name, campaign_asset.field_type, campaign_asset.status,
       campaign_asset.primary_status, campaign_asset.primary_status_reasons,
       campaign_asset.source, asset.id, asset.type, asset.name,
       asset.sitelink_asset.link_text, asset.sitelink_asset.description1,
       asset.sitelink_asset.description2, asset.final_urls,
       asset.callout_asset.callout_text, asset.call_asset.phone_number,
       asset.call_asset.call_conversion_reporting_state,
       asset.call_asset.call_conversion_action,
       asset.structured_snippet_asset.header, asset.structured_snippet_asset.values,
       asset.policy_summary.approval_status
FROM campaign_asset""")

run("asset_perf_30", """
SELECT campaign.id, campaign_asset.field_type, asset.id, segments.click_type,
       metrics.impressions, metrics.clicks, metrics.cost_micros
FROM campaign_asset WHERE segments.date BETWEEN '2026-08-28' AND '2026-09-26'""")

run("ad_policy_detail", """
SELECT ad_group_ad.ad.id, ad_group.id, ad_group.name, campaign.id, ad_group_ad.status,
       ad_group_ad.policy_summary.approval_status,
       ad_group_ad.policy_summary.policy_topic_entries,
       ad_group_ad.ad.final_urls
FROM ad_group_ad
WHERE campaign.status = 'ENABLED' AND ad_group_ad.status != 'REMOVED'""")

run("geo_constants_targeted", """
SELECT campaign.id, campaign_criterion.location.geo_target_constant,
       campaign_criterion.negative, campaign_criterion.type
FROM campaign_criterion
WHERE campaign.status = 'ENABLED' AND campaign_criterion.type IN ('LOCATION','PROXIMITY')""")
