#!/usr/bin/env python3
"""2026-09-28 (run C) READ-ONLY targeted reads for the Apogee measurement-repair handoff.

Only the live fields needed for next actions: identity, campaign status/settings, device modifiers,
change history since 2026-09-24, delivery (completed days vs the partial current day), conversions by
action, call asset + conversion actions. Nothing mutates.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

from google.protobuf.json_format import MessageToDict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, EXACT_NAME, GM_MANAGER, E, client, q, write  # noqa: E402

c = client()
R = {"run_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "errors": {}}


def pb(m):
    return MessageToDict(m._pb, preserving_proto_field_name=True)


def run(label, query, cid=CID):
    try:
        return q(c, query, cid=cid)
    except Exception as exc:  # noqa: BLE001
        s = str(exc)
        i = s.find("message:")
        R["errors"][label] = s[i:i + 300] if i >= 0 else s[:300]
        print("  !!", label, R["errors"][label][:160])
        return []


mgr = run("mgr", f"SELECT customer_client.id, customer_client.descriptive_name, customer_client.manager, "
                 f"customer_client.test_account FROM customer_client WHERE customer_client.id = {CID}", cid=GM_MANAGER)
cu = run("cust", "SELECT customer.id, customer.descriptive_name, customer.manager, customer.test_account, customer.status, "
                 "customer.time_zone, customer.call_reporting_setting.call_conversion_action FROM customer")[0].customer
R["identity_pass"] = (str(cu.id) == CID and cu.descriptive_name == EXACT_NAME and not cu.manager and not cu.test_account
                      and len(mgr) == 1 and mgr[0].customer_client.descriptive_name == EXACT_NAME)
R["timezone"] = cu.time_zone
print(f"IDENTITY {'PASS' if R['identity_pass'] else 'FAIL'}: {cu.id} '{cu.descriptive_name}' manager={cu.manager} "
      f"test={cu.test_account} {E(cu.status)} tz={cu.time_zone}")
if not R["identity_pass"]:
    write(EVID / "2026-09-28c-reads.json", R)
    sys.exit("HARD STOP: identity mismatch")
R["clock"] = {lbl: [x.segments.date for x in run(lbl, f"SELECT segments.date, metrics.impressions FROM customer "
                                                        f"WHERE segments.date DURING {d}")]
              for lbl, d in (("yesterday", "YESTERDAY"), ("today", "TODAY"))}

camp = run("campaign", """SELECT campaign.id, campaign.status, campaign.serving_status, campaign.primary_status,
    campaign.primary_status_reasons, campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros,
    campaign.network_settings.target_google_search, campaign.network_settings.target_search_network,
    campaign.network_settings.target_content_network, campaign_budget.amount_micros, campaign_budget.explicitly_shared
    FROM campaign WHERE campaign.id = 24257151015""")
R["campaign"] = {**pb(camp[0].campaign), "budget_micros": camp[0].campaign_budget.amount_micros,
                 "budget_shared": camp[0].campaign_budget.explicitly_shared}
x = R["campaign"]
print(f"CAMPAIGN {x['status']}/{x['serving_status']}/{x['primary_status']} {x.get('primary_status_reasons')} "
      f"{x['bidding_strategy_type']} cap={int(x['target_spend']['cpc_bid_ceiling_micros'])/1e6} "
      f"budget={x['budget_micros']/1e6} shared={x['budget_shared']}")

dev = []
for r in run("dev_cc", """SELECT campaign_criterion.resource_name, campaign_criterion.device.type, campaign_criterion.bid_modifier
    FROM campaign_criterion WHERE campaign_criterion.type = 'DEVICE'"""):
    b = r.campaign_criterion
    dev.append({"level": "campaign", "resource": b.resource_name, "device": E(b.device.type_),
                "bid_modifier_set": b._pb.HasField("bid_modifier"), "bid_modifier": b.bid_modifier})
for r in run("dev_ag", """SELECT ad_group_bid_modifier.resource_name, ad_group_bid_modifier.device.type,
    ad_group_bid_modifier.bid_modifier FROM ad_group_bid_modifier"""):
    b = r.ad_group_bid_modifier
    dev.append({"level": "ad_group", "resource": b.resource_name, "device": E(b.device.type_),
                "bid_modifier_set": b._pb.HasField("bid_modifier"), "bid_modifier": b.bid_modifier})
R["device_modifiers"] = dev
for d in dev:
    print(f"  DEVICE {d['level']:<8} {d['resource'].split('/')[-1]:<22} {d['device']:<8} set={d['bid_modifier_set']} value={d['bid_modifier']}")

ch = run("change_event", """SELECT change_event.change_date_time, change_event.change_resource_type,
    change_event.resource_change_operation, change_event.client_type, change_event.changed_fields,
    change_event.change_resource_name, change_event.old_resource, change_event.new_resource
    FROM change_event WHERE change_event.change_date_time >= '2026-09-24 00:00:00'
    AND change_event.change_date_time <= '2026-09-28 23:59:59' ORDER BY change_event.change_date_time ASC LIMIT 500""")
R["change_events"] = [{"t": e.change_event.change_date_time, "type": E(e.change_event.change_resource_type),
                       "op": E(e.change_event.resource_change_operation), "client": E(e.change_event.client_type),
                       "fields": list(e.change_event.changed_fields.paths), "res": e.change_event.change_resource_name,
                       "old": pb(e.change_event.old_resource), "new": pb(e.change_event.new_resource)} for e in ch]
print(f"change_event rows 09-24..09-28: {len(R['change_events'])}")
for e in R["change_events"]:
    print(f"  {e['t']} {e['client']} {e['op']} {e['type']} {e['res']} fields={e['fields']} old={json.dumps(e['old'])[:200]} new={json.dumps(e['new'])[:200]}")
cs = run("change_status", """SELECT change_status.resource_type, change_status.resource_status,
    change_status.last_change_date_time, change_status.resource_name FROM change_status
    WHERE change_status.last_change_date_time >= '2026-09-24 00:00:00'
    AND change_status.last_change_date_time <= '2026-09-28 23:59:59' LIMIT 1000""")
R["change_status"] = [pb(r.change_status) for r in cs]
print(f"change_status rows 09-24..09-28: {len(R['change_status'])}")
for s in R["change_status"]:
    print(f"  {s['last_change_date_time']} {s['resource_type']} {s['resource_status']} {s['resource_name'].split('/')[-1]}")

MET = ("metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions, "
       "metrics.search_impression_share, metrics.search_budget_lost_impression_share, "
       "metrics.search_rank_lost_impression_share, metrics.search_click_share")
R["completed_days_09_21_to_09_27"] = [pb(r.metrics) for r in run("completed", f"SELECT {MET} FROM campaign "
                                      "WHERE segments.date BETWEEN '2026-09-21' AND '2026-09-27'")]
R["partial_today"] = [pb(r.metrics) for r in run("partial", f"SELECT {MET} FROM campaign WHERE segments.date DURING TODAY")]
print("COMPLETED 09-21..09-27:", R["completed_days_09_21_to_09_27"])
print("PARTIAL TODAY:", R["partial_today"])
R["all_conv_by_action_since_09_16"] = [{"id": str(r.conversion_action.id), **pb(r.metrics)} for r in run(
    "ca", "SELECT conversion_action.id, metrics.all_conversions FROM conversion_action "
          "WHERE segments.date BETWEEN '2026-09-16' AND '2026-09-28'")]
print("ALL_CONVERSIONS by action:", R["all_conv_by_action_since_09_16"])
R["conversion_actions"] = [pb(r.conversion_action) for r in run("cas", """SELECT conversion_action.id, conversion_action.name,
    conversion_action.status, conversion_action.type, conversion_action.primary_for_goal,
    conversion_action.include_in_conversions_metric, conversion_action.phone_call_duration_seconds,
    conversion_action.counting_type FROM conversion_action""")]
for a in R["conversion_actions"]:
    print("  CONV", a["id"], a["type_"], a["status"], "primary=", a.get("primary_for_goal", False),
          "in_conv=", a.get("include_in_conversions_metric", False), "dur=", a.get("phone_call_duration_seconds"),
          a.get("counting_type"))
ca = run("call_asset", """SELECT campaign.id, campaign_asset.status, asset.id, asset.call_asset.phone_number,
    asset.call_asset.country_code, asset.call_asset.call_conversion_reporting_state, asset.call_asset.call_conversion_action,
    asset.call_asset.ad_schedule_targets, asset.policy_summary.approval_status FROM campaign_asset
    WHERE campaign_asset.field_type = 'CALL'""")
R["call_assets"] = [{"campaign": str(r.campaign.id), "link_status": E(r.campaign_asset.status), **pb(r.asset)} for r in ca]
for a in R["call_assets"]:
    ca_ = a["call_asset"]
    print("  CALL ASSET", a["id"], a["link_status"], ca_["phone_number"], ca_["call_conversion_reporting_state"],
          ca_.get("call_conversion_action"), [(s["day_of_week"][:3], s["start_hour"], s["end_hour"]) for s in ca_["ad_schedule_targets"]],
          a["policy_summary"]["approval_status"])
R["call_view"] = len(run("call_view", "SELECT call_view.call_status, call_view.call_duration_seconds FROM call_view"))
print("call_view rows:", R["call_view"], "| account call_conversion_action:", cu.call_reporting_setting.call_conversion_action)
write(EVID / "2026-09-28c-reads.json", R)
print("errors:", R["errors"])
