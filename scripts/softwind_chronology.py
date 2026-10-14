#!/usr/bin/env python3
"""Read-only campaign chronology for Softwind Power Washing.

Reconstructs created / enabled / first-delivery timestamps from change_event
(30-day API cap) plus daily metrics. SELECT-only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
TZ = ZoneInfo("America/New_York")
OUT = ROOT / "clients/softwind-power-washing/snapshots/chronology-2026-08-25.json"


class Reader:
    def __init__(self):
        load_dotenv_if_available(ROOT / ".env")
        self.svc = load_google_ads_client().get_service("GoogleAdsService")
        self.errors = []

    def rows(self, name, query):
        try:
            return list(self.svc.search(customer_id=CID, query=query))
        except Exception as exc:
            msg = str(exc)
            for m in ("message: ", "FaultMessage: "):
                if m in msg:
                    msg = msg.split(m, 1)[1][:400]
                    break
            self.errors.append({"query": name, "error": msg[:400]})
            print("  !! %s: %s" % (name, msg[:200]), file=sys.stderr)
            return []


def main() -> int:
    r = Reader()
    out = {"customer_id": CID}
    now = datetime.now(TZ)
    out["snapshot_taken_account_local"] = now.isoformat()

    # change_event is capped at 30 days by the API.
    start = (now - timedelta(days=29)).date().isoformat()
    end = now.date().isoformat()
    out["change_event_window"] = {"start": start, "end": end,
                                  "api_cap_note": "change_event supports a 30-day window only"}

    q = """
      SELECT change_event.change_date_time, change_event.change_resource_type,
             change_event.change_resource_name, change_event.client_type,
             change_event.user_email, change_event.resource_change_operation,
             change_event.changed_fields,
             change_event.campaign, change_event.ad_group,
             change_event.old_resource, change_event.new_resource,
             change_event.asset
      FROM change_event
      WHERE change_event.change_date_time >= '%s'
        AND change_event.change_date_time <= '%s 23:59:59'
      ORDER BY change_event.change_date_time ASC
      LIMIT 10000
    """ % (start, end)
    events = []
    for row in r.rows("change_event", q):
        e = row.change_event
        events.append({
            "when": e.change_date_time,
            "resource_type": enum_name(e.change_resource_type),
            "resource": e.change_resource_name,
            "operation": enum_name(e.resource_change_operation),
            "client_type": enum_name(e.client_type),
            "user_email": e.user_email or "",
            "changed_fields": list(e.changed_fields.paths) if e.changed_fields else [],
            "campaign": e.campaign or "",
            "ad_group": e.ad_group or "",
        })
    out["change_events"] = events

    # change_status carries last_change_date_time beyond the change_event window
    q = """
      SELECT change_status.resource_name, change_status.last_change_date_time,
             change_status.resource_type, change_status.campaign,
             change_status.ad_group, change_status.resource_status,
             change_status.ad_group_ad, change_status.ad_group_criterion,
             change_status.campaign_criterion
      FROM change_status
      WHERE change_status.last_change_date_time >= '%s'
        AND change_status.last_change_date_time <= '%s 23:59:59'
      ORDER BY change_status.last_change_date_time ASC
      LIMIT 10000
    """ % (start, end)
    out["change_status"] = [
        {"resource": x.change_status.resource_name,
         "when": x.change_status.last_change_date_time,
         "resource_type": enum_name(x.change_status.resource_type),
         "status": enum_name(x.change_status.resource_status),
         "campaign": x.change_status.campaign or "",
         "ad_group": x.change_status.ad_group or ""}
        for x in r.rows("change_status", q)
    ]

    # ---- daily campaign metrics, all time ----
    q = """
      SELECT campaign.id, campaign.name, segments.date,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions, metrics.all_conversions,
             metrics.conversions_value, metrics.all_conversions_value,
             metrics.average_cpc, metrics.ctr,
             metrics.search_impression_share,
             metrics.search_budget_lost_impression_share,
             metrics.search_rank_lost_impression_share,
             metrics.search_top_impression_share,
             metrics.search_absolute_top_impression_share,
             metrics.top_impression_percentage,
             metrics.absolute_top_impression_percentage,
             metrics.interactions, metrics.interaction_rate,
             metrics.phone_calls, metrics.phone_impressions
      FROM campaign
      WHERE segments.date BETWEEN '2026-01-01' AND '%s'
      ORDER BY campaign.id, segments.date
    """ % end
    daily = []
    for row in r.rows("campaign_daily", q):
        m = row.metrics
        daily.append({
            "campaign_id": str(row.campaign.id), "campaign_name": row.campaign.name,
            "date": row.segments.date,
            "impressions": int(m.impressions), "clicks": int(m.clicks),
            "cost": m.cost_micros / 1_000_000,
            "conversions": float(m.conversions),
            "all_conversions": float(m.all_conversions),
            "conversions_value": float(m.conversions_value),
            "all_conversions_value": float(m.all_conversions_value),
            "avg_cpc": m.average_cpc / 1_000_000 if m.average_cpc else 0.0,
            "ctr": float(m.ctr),
            "search_is": float(m.search_impression_share) if m.search_impression_share else None,
            "lost_is_budget": float(m.search_budget_lost_impression_share)
                              if m.search_budget_lost_impression_share else None,
            "lost_is_rank": float(m.search_rank_lost_impression_share)
                            if m.search_rank_lost_impression_share else None,
            "search_top_is": float(m.search_top_impression_share)
                             if m.search_top_impression_share else None,
            "search_abs_top_is": float(m.search_absolute_top_impression_share)
                                 if m.search_absolute_top_impression_share else None,
            "top_pct": float(m.top_impression_percentage) if m.top_impression_percentage else None,
            "abs_top_pct": float(m.absolute_top_impression_percentage)
                           if m.absolute_top_impression_percentage else None,
            "interactions": int(m.interactions),
            "phone_calls": int(m.phone_calls),
            "phone_impressions": int(m.phone_impressions),
        })
    out["campaign_daily"] = daily

    # ---- daily account-level totals (catches anything outside the 2 campaigns) ----
    q = """
      SELECT segments.date, metrics.impressions, metrics.clicks,
             metrics.cost_micros, metrics.conversions, metrics.all_conversions
      FROM customer
      WHERE segments.date BETWEEN '2026-01-01' AND '%s'
      ORDER BY segments.date
    """ % end
    out["account_daily"] = [
        {"date": x.segments.date, "impressions": int(x.metrics.impressions),
         "clicks": int(x.metrics.clicks), "cost": x.metrics.cost_micros / 1_000_000,
         "conversions": float(x.metrics.conversions),
         "all_conversions": float(x.metrics.all_conversions)}
        for x in r.rows("account_daily", q)
    ]

    # ---- conversions by action and date ----
    q = """
      SELECT segments.date, segments.conversion_action_name,
             segments.conversion_action_category, campaign.name,
             metrics.conversions, metrics.all_conversions,
             metrics.conversions_value, metrics.all_conversions_value
      FROM campaign
      WHERE segments.date BETWEEN '2026-01-01' AND '%s'
      ORDER BY segments.date
    """ % end
    out["conversions_by_action_date"] = [
        {"date": x.segments.date,
         "action": x.segments.conversion_action_name,
         "category": enum_name(x.segments.conversion_action_category),
         "campaign": x.campaign.name,
         "conversions": float(x.metrics.conversions),
         "all_conversions": float(x.metrics.all_conversions),
         "value": float(x.metrics.conversions_value),
         "all_value": float(x.metrics.all_conversions_value)}
        for x in r.rows("conversions_by_action_date", q)
    ]

    # ---- ad group first-delivery ----
    q = """
      SELECT campaign.name, ad_group.id, ad_group.name, segments.date,
             metrics.impressions, metrics.clicks, metrics.cost_micros,
             metrics.conversions
      FROM ad_group
      WHERE segments.date BETWEEN '2026-01-01' AND '%s'
      ORDER BY ad_group.id, segments.date
    """ % end
    out["ad_group_daily"] = [
        {"campaign": x.campaign.name, "ad_group_id": str(x.ad_group.id),
         "ad_group": x.ad_group.name, "date": x.segments.date,
         "impressions": int(x.metrics.impressions), "clicks": int(x.metrics.clicks),
         "cost": x.metrics.cost_micros / 1_000_000,
         "conversions": float(x.metrics.conversions)}
        for x in r.rows("ad_group_daily", q)
    ]

    out["read_errors"] = r.errors
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote %s" % OUT)
    for k, v in out.items():
        if isinstance(v, list):
            print("  %s: %d" % (k, len(v)))
    for e in r.errors:
        print(" ERR", e["query"], "::", e["error"][:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
