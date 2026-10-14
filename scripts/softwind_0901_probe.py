#!/usr/bin/env python3
"""Attribution probe: campaign rename chronology + Sept 1 delivery shape. READ-ONLY."""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

load_dotenv_if_available(ROOT / ".env")
client = load_google_ads_client()
svc = client.get_service("GoogleAdsService")
cid = normalize_customer_id("1521725229")
def q(s): return list(svc.search(customer_id=cid, query=s))

print("=== CHANGE EVENTS 2026-08-30 .. 2026-09-01 ===")
rows = q("""SELECT change_event.change_date_time, change_event.user_email,
                   change_event.client_type, change_event.change_resource_type,
                   change_event.change_resource_name, change_event.resource_change_operation,
                   change_event.changed_fields, change_event.campaign,
                   change_event.new_resource, change_event.old_resource
            FROM change_event
            WHERE change_event.change_date_time >= '2026-08-30 00:00:00'
              AND change_event.change_date_time <= '2026-09-01 23:59:59'
            ORDER BY change_event.change_date_time DESC LIMIT 200""")
print("rows:", len(rows))
for r in rows:
    e = r.change_event
    fields = list(e.changed_fields.paths) if e.changed_fields else []
    newname = ""
    try: newname = e.new_resource.campaign.name
    except Exception: pass
    oldname = ""
    try: oldname = e.old_resource.campaign.name
    except Exception: pass
    print(json.dumps({"when": e.change_date_time, "user": e.user_email,
                      "client": enum_name(e.client_type),
                      "res_type": enum_name(e.change_resource_type),
                      "op": enum_name(e.resource_change_operation),
                      "fields": fields, "campaign": e.campaign.split("/")[-1] if e.campaign else "",
                      "old_name": oldname, "new_name": newname,
                      "resource": e.change_resource_name.split("/")[-1] if e.change_resource_name else ""}))

print("\n=== SEPT 1 HOURLY, campaign level ===")
for r in q("""SELECT campaign.id, campaign.name, segments.hour, metrics.impressions,
                     metrics.clicks, metrics.cost_micros
              FROM campaign WHERE segments.date = '2026-09-01'
                AND campaign.status != 'REMOVED' ORDER BY segments.hour"""):
    print(r.campaign.id, r.campaign.name, "hour", r.segments.hour,
          "impr", r.metrics.impressions, "clicks", r.metrics.clicks,
          "cost", round(r.metrics.cost_micros/1e6, 2))

print("\n=== DAILY 08-28 .. 09-01 per campaign ===")
for r in q("""SELECT segments.date, campaign.id, campaign.name, metrics.impressions,
                     metrics.clicks, metrics.invalid_clicks, metrics.cost_micros,
                     metrics.search_impression_share, metrics.search_rank_lost_impression_share,
                     metrics.search_budget_lost_impression_share
              FROM campaign WHERE segments.date BETWEEN '2026-08-28' AND '2026-09-01'
                AND campaign.status != 'REMOVED' ORDER BY segments.date"""):
    m = r.metrics
    print(r.segments.date, r.campaign.id, f"{r.campaign.name[:22]:22}",
          "impr", f"{m.impressions:4}", "valid", f"{m.clicks:3}", "invalid", f"{m.invalid_clicks:3}",
          "cost", f"{m.cost_micros/1e6:8.2f}",
          "IS", f"{m.search_impression_share:.3f}", "lostRank", f"{m.search_rank_lost_impression_share:.3f}",
          "lostBud", f"{m.search_budget_lost_impression_share:.3f}")

print("\n=== AUGUST 31 vs prior: individual click prices all-time (keyword_view) ===")
for r in q("""SELECT segments.date, campaign.id, ad_group.name,
                     ad_group_criterion.keyword.text, metrics.clicks, metrics.cost_micros
              FROM keyword_view WHERE segments.date BETWEEN '2026-08-27' AND '2026-09-01'
                AND metrics.clicks > 0 ORDER BY segments.date"""):
    print(r.segments.date, r.campaign.id, f"{r.ad_group.name[:30]:30}",
          f"{r.ad_group_criterion.keyword.text[:32]:32}",
          "clicks", r.metrics.clicks, "cost", round(r.metrics.cost_micros/1e6,2),
          "cpc", round(r.metrics.cost_micros/1e6/max(r.metrics.clicks,1),2))
