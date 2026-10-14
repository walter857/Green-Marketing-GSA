#!/usr/bin/env python3
"""Read-only: recover the CPC-ceiling history and the AI Max / automation settings."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
OUT = ROOT / "clients/softwind-power-washing/snapshots/bid-and-automation-2026-08-25.json"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    out = {}
    errors = []

    def rows(name, q):
        try:
            return list(svc.search(customer_id=CID, query=q))
        except Exception as exc:
            m = str(exc)
            for k in ("message: ", "FaultMessage: "):
                if k in m:
                    m = m.split(k, 1)[1][:300]
                    break
            errors.append({"q": name, "e": m[:300]})
            print("  !!", name, m[:200], file=sys.stderr)
            return []

    q = """
      SELECT change_event.change_date_time, change_event.change_resource_name,
             change_event.changed_fields, change_event.resource_change_operation,
             change_event.old_resource, change_event.new_resource,
             change_event.client_type, change_event.user_email
      FROM change_event
      WHERE change_event.change_date_time >= '2026-07-27'
        AND change_event.change_date_time <= '2026-08-25 23:59:59'
        AND change_event.change_resource_type = CAMPAIGN
      ORDER BY change_event.change_date_time ASC
      LIMIT 500
    """
    hist = []
    for r in rows("campaign_changes", q):
        e = r.change_event
        old, new = e.old_resource.campaign, e.new_resource.campaign

        def snap(c):
            return {
                "name": c.name,
                "status": enum_name(c.status),
                "bidding_strategy_type": enum_name(c.bidding_strategy_type),
                "target_spend_cpc_bid_ceiling": (
                    c.target_spend.cpc_bid_ceiling_micros / 1_000_000
                    if c.target_spend.cpc_bid_ceiling_micros else None),
                "manual_cpc_enhanced": bool(c.manual_cpc.enhanced_cpc_enabled),
                "positive_geo_target_type": enum_name(
                    c.geo_target_type_setting.positive_geo_target_type),
                "search_partners": bool(c.network_settings.target_search_network),
                "display": bool(c.network_settings.target_content_network),
            }

        hist.append({
            "when": e.change_date_time,
            "resource": e.change_resource_name,
            "operation": enum_name(e.resource_change_operation),
            "changed_fields": list(e.changed_fields.paths) if e.changed_fields else [],
            "client_type": enum_name(e.client_type),
            "user": e.user_email or "",
            "old": snap(old),
            "new": snap(new),
        })
    out["campaign_change_history"] = hist

    # AI Max / asset automation, explicit read.
    for field in [
        "campaign.ai_max_setting.enable_ai_max",
        "campaign.asset_automation_settings",
        "campaign.ad_serving_optimization_status",
        "campaign.keyword_match_type",
        "campaign.excluded_parent_asset_field_types",
        "campaign.excluded_parent_asset_set_types",
        "campaign.contains_eu_political_advertising",
    ]:
        q = "SELECT campaign.id, campaign.name, %s FROM campaign ORDER BY campaign.id" % field
        got = rows("field:" + field, q)
        vals = []
        for r in got:
            c = r.campaign
            if field.endswith("enable_ai_max"):
                v = bool(c.ai_max_setting.enable_ai_max)
            elif field.endswith("asset_automation_settings"):
                v = [{"type": enum_name(a.asset_automation_type),
                      "status": enum_name(a.asset_automation_status)}
                     for a in c.asset_automation_settings]
            elif field.endswith("ad_serving_optimization_status"):
                v = enum_name(c.ad_serving_optimization_status)
            elif field.endswith("keyword_match_type"):
                v = enum_name(c.keyword_match_type)
            elif field.endswith("excluded_parent_asset_field_types"):
                v = [enum_name(x) for x in c.excluded_parent_asset_field_types]
            elif field.endswith("excluded_parent_asset_set_types"):
                v = [enum_name(x) for x in c.excluded_parent_asset_set_types]
            else:
                v = enum_name(c.contains_eu_political_advertising)
            vals.append({"campaign": c.name, "value": v})
        out[field] = vals

    # Customer-level negative criteria (account-level exclusions).
    q = """
      SELECT customer_negative_criterion.id, customer_negative_criterion.type,
             customer_negative_criterion.placement.url,
             customer_negative_criterion.content_label.type
      FROM customer_negative_criterion
    """
    out["customer_negative_criteria"] = [
        {"id": str(x.customer_negative_criterion.id),
         "type": enum_name(x.customer_negative_criterion.type_)}
        for x in rows("customer_negative_criterion", q)
    ]

    out["read_errors"] = errors
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("=== CAMPAIGN CHANGE HISTORY ===")
    for h in hist:
        print("  %s  %s  %s" % (h["when"], h["operation"], h["resource"].split("/")[-1]))
        print("      fields: %s" % ", ".join(h["changed_fields"])[:170])
        for k in ("bidding_strategy_type", "target_spend_cpc_bid_ceiling",
                  "manual_cpc_enhanced", "positive_geo_target_type",
                  "search_partners", "display", "status"):
            o, n = h["old"].get(k), h["new"].get(k)
            if o != n:
                print("      %-32s %s  ->  %s" % (k, o, n))
    print()
    for k, v in out.items():
        if k.startswith("campaign."):
            print("%-52s %s" % (k, v))
    print("customer_negative_criteria:", out["customer_negative_criteria"])
    if errors:
        print("ERRORS:", errors)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
