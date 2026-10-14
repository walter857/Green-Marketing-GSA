#!/usr/bin/env python3
"""Pre-approval baseline re-read for Softwind L&M, run in the project venv.

SELECT-only. Re-reads every field the QA gate names, hashes the result, and
diffs it against the 18:12 baseline so drift is visible before any package is
rebuilt.

Writes:
  01e-baseline-2.json   the new snapshot
  01f-drift.json        field-level diff against 01-before-snapshot.json
"""
from __future__ import annotations

import hashlib
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

CID = "2429758629"
TZ = ZoneInfo("America/New_York")
B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PATIO, PAVERS = "23484806108", "23489296528"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    import google.ads.googleads
    now = datetime.now(TZ)
    out = {
        "read_at_account_local": now.isoformat(),
        "customer_id": CID,
        "library_version": google.ads.googleads.VERSION,
        "python": sys.version.split()[0],
        "interpreter": sys.executable,
        "read_scope": "SELECT-only; authorizes no mutation",
    }
    errs = []

    def rows(name, q):
        try:
            r = list(svc.search(customer_id=CID, query=q))
            print("  ok  %-30s %4d" % (name, len(r)))
            return r
        except Exception as exc:  # noqa: BLE001
            m = str(exc)
            for k in ("message: ", "FaultMessage: "):
                if k in m:
                    m = m.split(k, 1)[1][:300]
                    break
            errs.append({"q": name, "e": m[:300]})
            print("  !!  %-30s %s" % (name, m[:120]), file=sys.stderr)
            return []

    # ---- identity ----
    for r in rows("customer", """
        SELECT customer.id, customer.descriptive_name, customer.manager,
               customer.test_account, customer.currency_code, customer.time_zone,
               customer.status, customer.auto_tagging_enabled,
               customer.tracking_url_template, customer.final_url_suffix,
               customer.conversion_tracking_setting.conversion_tracking_id,
               customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled
        FROM customer LIMIT 1"""):
        c = r.customer
        out["identity"] = {
            "id": str(c.id), "descriptive_name": c.descriptive_name,
            "manager": c.manager, "test_account": c.test_account,
            "currency": c.currency_code, "time_zone": c.time_zone,
            "status": enum_name(c.status),
            "auto_tagging_enabled": c.auto_tagging_enabled,
            "tracking_url_template_present": bool(c.tracking_url_template),
            "tracking_url_template_host": (
                "monitor.clickcease.com" if "clickcease" in (c.tracking_url_template or "").lower()
                else "other"),
            "final_url_suffix": c.final_url_suffix or None,
            "conversion_tracking_id": str(c.conversion_tracking_setting.conversion_tracking_id),
            "enhanced_conversions_for_leads":
                c.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
        }

    # ---- manager hierarchy ----
    out["manager_links"] = [{
        "manager_customer_id": str(x.customer_manager_link.manager_customer),
        "status": enum_name(x.customer_manager_link.status),
    } for x in rows("customer_manager_link", """
        SELECT customer_manager_link.manager_customer,
               customer_manager_link.status
        FROM customer_manager_link""")]

    # ---- campaigns: budgets, status, bidding, ceilings, networks, geo ----
    camps = {}
    for r in rows("campaign", """
        SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
               campaign.advertising_channel_type, campaign.bidding_strategy_type,
               campaign.bidding_strategy, campaign.campaign_budget,
               campaign.target_spend.cpc_bid_ceiling_micros,
               campaign.network_settings.target_google_search,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.network_settings.target_partner_search_network,
               campaign.geo_target_type_setting.positive_geo_target_type,
               campaign.geo_target_type_setting.negative_geo_target_type,
               campaign.ai_max_setting.enable_ai_max,
               campaign.asset_automation_settings,
               campaign.tracking_url_template, campaign.final_url_suffix,
               campaign_budget.id, campaign_budget.amount_micros,
               campaign_budget.explicitly_shared, campaign_budget.reference_count,
               campaign_budget.delivery_method, campaign_budget.status
        FROM campaign WHERE campaign.status != 'REMOVED' ORDER BY campaign.name"""):
        c, b = r.campaign, r.campaign_budget
        camps[str(c.id)] = {
            "name": c.name, "status": enum_name(c.status),
            "serving_status": enum_name(c.serving_status),
            "channel": enum_name(c.advertising_channel_type),
            "bidding_strategy_type": enum_name(c.bidding_strategy_type),
            "portfolio_strategy": c.bidding_strategy or None,
            "cpc_bid_ceiling": (c.target_spend.cpc_bid_ceiling_micros / 1e6
                                if c.target_spend.cpc_bid_ceiling_micros else None),
            "budget_id": str(b.id), "budget_amount": b.amount_micros / 1e6,
            "budget_explicitly_shared": b.explicitly_shared,
            "budget_reference_count": b.reference_count,
            "budget_delivery": enum_name(b.delivery_method),
            "budget_status": enum_name(b.status),
            "search_partners": c.network_settings.target_search_network,
            "display": c.network_settings.target_content_network,
            "google_search": c.network_settings.target_google_search,
            "partner_search": c.network_settings.target_partner_search_network,
            "positive_geo": enum_name(c.geo_target_type_setting.positive_geo_target_type),
            "negative_geo": enum_name(c.geo_target_type_setting.negative_geo_target_type),
            "ai_max": c.ai_max_setting.enable_ai_max,
            "asset_automation": {enum_name(a.asset_automation_type):
                                 enum_name(a.asset_automation_status)
                                 for a in c.asset_automation_settings},
            "tracking_url_template": c.tracking_url_template or None,
            "final_url_suffix": c.final_url_suffix or None,
        }
    out["campaigns"] = camps

    # ---- keywords ----
    kws = {}
    for r in rows("keywords", """
        SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               ad_group_criterion.negative, ad_group.id, ad_group.name,
               ad_group.status, campaign.id, campaign.name
        FROM ad_group_criterion
        WHERE ad_group_criterion.type='KEYWORD'
          AND ad_group_criterion.status != 'REMOVED'"""):
        k = r.ad_group_criterion
        kws["%s~%s" % (r.ad_group.id, k.criterion_id)] = {
            "text": k.keyword.text, "match_type": enum_name(k.keyword.match_type),
            "status": enum_name(k.status), "negative": k.negative,
            "ad_group_id": str(r.ad_group.id), "ad_group": r.ad_group.name,
            "ad_group_status": enum_name(r.ad_group.status),
            "campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
        }
    out["keywords"] = kws

    # ---- campaign negatives + IP blocks + locations ----
    negs, ipb, locs = {}, {}, {}
    for r in rows("campaign_criterion", """
        SELECT campaign_criterion.criterion_id, campaign_criterion.type,
               campaign_criterion.negative, campaign_criterion.status,
               campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
               campaign_criterion.location.geo_target_constant, campaign.id
        FROM campaign_criterion WHERE campaign_criterion.status != 'REMOVED'"""):
        cc, cid = r.campaign_criterion, str(r.campaign.id)
        t = enum_name(cc.type_)
        key = "%s~%s" % (cid, cc.criterion_id)
        if t == "KEYWORD" and cc.negative:
            negs[key] = {"campaign_id": cid, "text": cc.keyword.text,
                         "match_type": enum_name(cc.keyword.match_type)}
        elif t == "IP_BLOCK":
            ipb[cid] = ipb.get(cid, 0) + 1
        elif t == "LOCATION":
            locs.setdefault(cid, []).append(cc.location.geo_target_constant.split("/")[-1])
    out["campaign_negatives"] = negs
    out["ip_blocks_per_campaign"] = ipb
    out["location_targets_per_campaign"] = {k: len(v) for k, v in locs.items()}

    # ---- shared sets ----
    out["shared_sets"] = {str(x.shared_set.id): {
        "name": x.shared_set.name, "type": enum_name(x.shared_set.type_),
        "member_count": x.shared_set.member_count,
    } for x in rows("shared_set", """
        SELECT shared_set.id, shared_set.name, shared_set.type,
               shared_set.member_count
        FROM shared_set WHERE shared_set.status != 'REMOVED'""")}
    out["shared_set_links"] = [{
        "campaign_id": str(x.campaign.id),
        "shared_set": x.campaign_shared_set.shared_set.split("/")[-1],
    } for x in rows("campaign_shared_set", """
        SELECT campaign_shared_set.shared_set, campaign.id
        FROM campaign_shared_set WHERE campaign_shared_set.status != 'REMOVED'""")]
    sc = {}
    for x in rows("shared_criterion", """
        SELECT shared_criterion.shared_set, shared_criterion.criterion_id,
               shared_criterion.keyword.text, shared_criterion.keyword.match_type
        FROM shared_criterion"""):
        s = x.shared_criterion.shared_set.split("/")[-1]
        sc.setdefault(s, []).append((x.shared_criterion.keyword.text,
                                     enum_name(x.shared_criterion.keyword.match_type)))
    out["shared_criteria_counts"] = {k: len(v) for k, v in sc.items()}
    out["_shared_criteria"] = sc

    # ---- conversion actions ----
    out["conversion_actions"] = {str(x.conversion_action.id): {
        "name": x.conversion_action.name,
        "status": enum_name(x.conversion_action.status),
        "type": enum_name(x.conversion_action.type_),
        "category": enum_name(x.conversion_action.category),
        "origin": enum_name(x.conversion_action.origin),
        "primary_for_goal": x.conversion_action.primary_for_goal,
        "include_in_conversions_metric":
            x.conversion_action.include_in_conversions_metric,
        "counting_type": enum_name(x.conversion_action.counting_type),
        "click_lookback": x.conversion_action.click_through_lookback_window_days,
        "view_lookback": x.conversion_action.view_through_lookback_window_days,
        "attribution":
            enum_name(x.conversion_action.attribution_model_settings.attribution_model),
        "call_seconds": x.conversion_action.phone_call_duration_seconds or None,
    } for x in rows("conversion_action", """
        SELECT conversion_action.id, conversion_action.name, conversion_action.status,
               conversion_action.type, conversion_action.category,
               conversion_action.origin, conversion_action.primary_for_goal,
               conversion_action.include_in_conversions_metric,
               conversion_action.counting_type,
               conversion_action.click_through_lookback_window_days,
               conversion_action.view_through_lookback_window_days,
               conversion_action.attribution_model_settings.attribution_model,
               conversion_action.phone_call_duration_seconds
        FROM conversion_action WHERE conversion_action.status != 'REMOVED'""")}

    # ---- campaign goal inclusion ----
    out["campaign_conversion_goals"] = [{
        "campaign_id": x.campaign_conversion_goal.campaign.split("/")[-1],
        "category": enum_name(x.campaign_conversion_goal.category),
        "origin": enum_name(x.campaign_conversion_goal.origin),
        "biddable": x.campaign_conversion_goal.biddable,
    } for x in rows("campaign_conversion_goal", """
        SELECT campaign_conversion_goal.campaign, campaign_conversion_goal.category,
               campaign_conversion_goal.origin, campaign_conversion_goal.biddable
        FROM campaign_conversion_goal""")]
    out["goal_config_level"] = {
        x.conversion_goal_campaign_config.campaign.split("/")[-1]:
        enum_name(x.conversion_goal_campaign_config.goal_config_level)
        for x in rows("goal_config", """
        SELECT conversion_goal_campaign_config.campaign,
               conversion_goal_campaign_config.goal_config_level
        FROM conversion_goal_campaign_config""")}

    # ---- change history (30-day cap, both bounds required) ----
    today = now.date()
    lo = (today - timedelta(days=28)).isoformat()
    out["change_events"] = [{
        "when": x.change_event.change_date_time,
        "type": enum_name(x.change_event.change_resource_type),
        "op": enum_name(x.change_event.resource_change_operation),
        "client_type": enum_name(x.change_event.client_type),
        "campaign": x.change_event.campaign.split("/")[-1] if x.change_event.campaign else None,
        "fields": list(x.change_event.changed_fields.paths) if x.change_event.changed_fields else [],
    } for x in rows("change_event_28d", """
        SELECT change_event.change_date_time, change_event.change_resource_type,
               change_event.resource_change_operation, change_event.client_type,
               change_event.campaign, change_event.changed_fields
        FROM change_event
        WHERE change_event.change_date_time >= '%s 00:00:00'
          AND change_event.change_date_time <= '%s 23:59:59'
        ORDER BY change_event.change_date_time DESC LIMIT 500""" % (lo, today))]

    # ---- MTD spend, every enabled campaign ----
    out["mtd_by_campaign"] = [{
        "campaign_id": str(x.campaign.id), "campaign": x.campaign.name,
        "status": enum_name(x.campaign.status),
        "cost": round(x.metrics.cost_micros / 1e6, 2),
        "clicks": x.metrics.clicks, "impressions": x.metrics.impressions,
        "conversions": round(x.metrics.conversions, 4),
    } for x in rows("mtd_by_campaign", """
        SELECT campaign.id, campaign.name, campaign.status, metrics.cost_micros,
               metrics.clicks, metrics.impressions, metrics.conversions
        FROM campaign WHERE segments.date BETWEEN '2026-09-01' AND '%s'""" % today)]
    out["mtd_account"] = [{
        "cost": round(x.metrics.cost_micros / 1e6, 2), "clicks": x.metrics.clicks,
        "conversions": round(x.metrics.conversions, 4),
    } for x in rows("mtd_account", """
        SELECT metrics.cost_micros, metrics.clicks, metrics.conversions
        FROM customer WHERE segments.date BETWEEN '2026-09-01' AND '%s'""" % today)]

    out["errors"] = errs
    payload = json.dumps({k: v for k, v in out.items()
                          if k not in ("read_at_account_local",)},
                         sort_keys=True, default=str).encode()
    out["evidence_sha256"] = hashlib.sha256(payload).hexdigest()
    out["evidence_sha256_short"] = out["evidence_sha256"][:16].upper()

    (B / "01e-baseline-2.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")

    # ---- drift vs the 18:12 baseline ----
    old = json.loads((B / "01-before-snapshot.json").read_text(encoding="utf-8"))
    drift = {"compared_at": now.isoformat(), "baseline_1": old["snapshot_taken_account_local"],
             "baseline_2": out["read_at_account_local"], "differences": []}
    for cid, c in camps.items():
        o = old["campaigns"].get(cid)
        if not o:
            drift["differences"].append({"what": "campaign appeared", "campaign_id": cid})
            continue
        ob = [b for b in old["campaign_budgets"].values()
              if b["id"] in o["campaign_budget_resource"]][0]
        for label, new_v, old_v in (
                ("status", c["status"], o["status"]),
                ("bidding_strategy_type", c["bidding_strategy_type"], o["bidding_strategy_type"]),
                ("cpc_bid_ceiling", c["cpc_bid_ceiling"], o["target_spend_cpc_bid_ceiling"]),
                ("budget_amount", c["budget_amount"], ob["amount"]),
                ("search_partners", c["search_partners"], o["network"]["search_partners"]),
                ("display", c["display"], o["network"]["display"]),
                ("ai_max", c["ai_max"], o["ai_max"]),
                ("positive_geo", c["positive_geo"], o["geo_target_type"]["positive"]),
                ("final_url_suffix", c["final_url_suffix"], o["final_url_suffix"])):
            if new_v != old_v:
                drift["differences"].append({
                    "what": label, "campaign_id": cid, "campaign": c["name"],
                    "baseline_1": old_v, "baseline_2": new_v})
    oldk = {"%s~%s" % (k["ad_group_id"], k["criterion_id"]): k for k in old["keywords"]}
    for key, k in kws.items():
        o = oldk.get(key)
        if o is None:
            drift["differences"].append({"what": "keyword appeared", "key": key,
                                         "text": k["text"]})
        elif o["status"] != k["status"]:
            drift["differences"].append({"what": "keyword status", "key": key,
                                         "text": k["text"],
                                         "baseline_1": o["status"],
                                         "baseline_2": k["status"]})
    for key in set(oldk) - set(kws):
        drift["differences"].append({"what": "keyword disappeared", "key": key})
    oldneg = len([x for x in old["campaign_criteria"]
                  if x["type"] == "KEYWORD" and x["negative"]])
    if oldneg != len(negs):
        drift["differences"].append({"what": "campaign negative count",
                                     "baseline_1": oldneg, "baseline_2": len(negs)})
    oldca = {c["id"]: c for c in old["conversion_actions"]}
    for cid, c in out["conversion_actions"].items():
        o = oldca.get(cid)
        if o and o["primary_for_goal"] != c["primary_for_goal"]:
            drift["differences"].append({"what": "conversion primary_for_goal",
                                         "id": cid, "name": c["name"],
                                         "baseline_1": o["primary_for_goal"],
                                         "baseline_2": c["primary_for_goal"]})
    drift["verdict"] = "NO DRIFT" if not drift["differences"] else "DRIFT DETECTED"
    (B / "01f-drift.json").write_text(json.dumps(drift, indent=2), encoding="utf-8")

    print("\nevidence sha256 : %s" % out["evidence_sha256_short"])
    print("library         : google-ads %s on python %s" % (out["library_version"],
                                                            out["python"]))
    print("query errors    : %d" % len(errs))
    print("DRIFT vs 18:12  : %s (%d differences)" % (drift["verdict"],
                                                     len(drift["differences"])))
    for d in drift["differences"][:20]:
        print("   %s" % d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
