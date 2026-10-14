#!/usr/bin/env python3
"""Complete conversion-goal hierarchy read for Softwind Power Washing.

Four layers: customer conversion tracking settings, conversion_goal_campaign_config,
customer_conversion_goal, campaign_conversion_goal, plus full conversion_action detail.

SELECT statements only. Constructs no operation, calls no mutate service.
"""
from __future__ import annotations

import json
import sys
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
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Pressure Washing"}
SNAP = ROOT / "clients/softwind-power-washing/snapshots"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    out: dict = {"mode": "READ-ONLY", "customer_id": CID}

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    # ---------------- A. identity + conversion tracking settings ----------------
    c = q("""SELECT customer.id, customer.descriptive_name, customer.currency_code,
                    customer.time_zone, customer.manager, customer.test_account,
                    customer.status,
                    customer.conversion_tracking_setting.conversion_tracking_id,
                    customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
                    customer.conversion_tracking_setting.conversion_tracking_status,
                    customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
                    customer.conversion_tracking_setting.google_ads_conversion_customer,
                    customer.conversion_tracking_setting.accepted_customer_data_terms
             FROM customer LIMIT 1""")[0].customer
    cts = c.conversion_tracking_setting
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
        "live_marker_present": "- live" in (c.descriptive_name or "").lower(),
        "account_local_datetime": now.isoformat(),
    }
    tracking = {
        "google_ads_conversion_customer": cts.google_ads_conversion_customer or "",
        "google_ads_conversion_customer_id":
            (cts.google_ads_conversion_customer or "").split("/")[-1],
        "conversion_tracking_status": enum_name(cts.conversion_tracking_status),
        "conversion_tracking_id": str(cts.conversion_tracking_id or ""),
        "cross_account_conversion_tracking_id":
            str(cts.cross_account_conversion_tracking_id or ""),
        "enhanced_conversions_for_leads_enabled":
            bool(cts.enhanced_conversions_for_leads_enabled),
        "accepted_customer_data_terms": bool(cts.accepted_customer_data_terms),
    }
    tracking["cross_account_tracking_active"] = bool(
        cts.cross_account_conversion_tracking_id)
    tracking["conversion_customer_is_self"] = (
        tracking["google_ads_conversion_customer_id"] == CID)
    out["identity"] = identity
    out["conversion_tracking_setting"] = tracking
    gate = {
        "name_matches": identity["descriptive_name"] == EXPECTED_NAME,
        "id_matches": identity["customer_id"] == CID,
        "not_manager": identity["manager"] is False,
        "not_test": identity["test_account"] is False,
        "status_enabled": identity["status"] == "ENABLED",
        "currency_usd": identity["currency"] == "USD",
        "tz_ny": identity["time_zone"] == "America/New_York",
    }
    out["identity_gate"] = gate
    if not all(gate.values()):
        print("IDENTITY GATE FAILED:", json.dumps(gate, indent=2))
        return 2

    # ---------------- campaigns: exact observed names ----------------
    camps = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status,
                         campaign.advertising_channel_type
                  FROM campaign WHERE campaign.status != 'REMOVED'"""):
        camps[str(r.campaign.id)] = {"name": r.campaign.name,
                                     "status": enum_name(r.campaign.status),
                                     "channel": enum_name(r.campaign.advertising_channel_type)}
    out["campaigns_observed"] = camps
    out["campaign_name_match"] = {
        i: {"expected": exp, "observed": camps.get(i, {}).get("name"),
            "match": camps.get(i, {}).get("name") == exp}
        for i, exp in CAMPAIGNS.items()}

    # ---------------- B. conversion_goal_campaign_config ----------------
    cfg = {}
    for r in q("""SELECT conversion_goal_campaign_config.campaign,
                         conversion_goal_campaign_config.goal_config_level,
                         conversion_goal_campaign_config.custom_conversion_goal,
                         conversion_goal_campaign_config.resource_name,
                         campaign.id, campaign.name
                  FROM conversion_goal_campaign_config"""):
        g = r.conversion_goal_campaign_config
        cfg[str(r.campaign.id)] = {
            "campaign_id": str(r.campaign.id),
            "campaign_name": r.campaign.name,
            "resource_name": g.resource_name,
            "goal_config_level": enum_name(g.goal_config_level),
            "custom_conversion_goal": g.custom_conversion_goal or "",
        }
    out["conversion_goal_campaign_config"] = cfg

    # ---------------- C. customer_conversion_goal ----------------
    ccg = []
    for r in q("""SELECT customer_conversion_goal.resource_name,
                         customer_conversion_goal.category,
                         customer_conversion_goal.origin,
                         customer_conversion_goal.biddable
                  FROM customer_conversion_goal"""):
        g = r.customer_conversion_goal
        ccg.append({"resource_name": g.resource_name,
                    "category": enum_name(g.category),
                    "origin": enum_name(g.origin),
                    "biddable": bool(g.biddable)})
    out["customer_conversion_goals"] = sorted(ccg, key=lambda x: (x["category"], x["origin"]))

    # ---------------- D. campaign_conversion_goal ----------------
    cmg = []
    for r in q("""SELECT campaign.id, campaign.name,
                         campaign_conversion_goal.resource_name,
                         campaign_conversion_goal.campaign,
                         campaign_conversion_goal.category,
                         campaign_conversion_goal.origin,
                         campaign_conversion_goal.biddable
                  FROM campaign_conversion_goal"""):
        g = r.campaign_conversion_goal
        cmg.append({"campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
                    "resource_name": g.resource_name,
                    "category": enum_name(g.category), "origin": enum_name(g.origin),
                    "biddable": bool(g.biddable)})
    out["campaign_conversion_goals"] = sorted(
        cmg, key=lambda x: (x["campaign_id"], x["category"], x["origin"]))
    out["campaign_conversion_goals_biddable_only"] = sorted(
        [g for g in cmg if g["biddable"]],
        key=lambda x: (x["campaign_id"], x["category"], x["origin"]))

    # ---------------- conversion actions, full detail ----------------
    ca = []
    for r in q("""SELECT conversion_action.id, conversion_action.resource_name,
                         conversion_action.name, conversion_action.status,
                         conversion_action.type, conversion_action.category,
                         conversion_action.origin,
                         conversion_action.owner_customer,
                         conversion_action.primary_for_goal,
                         conversion_action.include_in_conversions_metric,
                         conversion_action.counting_type,
                         conversion_action.attribution_model_settings.attribution_model,
                         conversion_action.attribution_model_settings.data_driven_model_status,
                         conversion_action.click_through_lookback_window_days,
                         conversion_action.view_through_lookback_window_days,
                         conversion_action.phone_call_duration_seconds,
                         conversion_action.value_settings.default_value,
                         conversion_action.value_settings.default_currency_code,
                         conversion_action.value_settings.always_use_default_value,
                         conversion_action.tag_snippets,
                         conversion_action.google_analytics_4_settings.property_name,
                         conversion_action.app_id
                  FROM conversion_action WHERE conversion_action.status != 'REMOVED'"""):
        a = r.conversion_action
        snips = []
        for s in a.tag_snippets:
            snips.append({"type": enum_name(s.type_), "page_format": enum_name(s.page_format),
                          "event_snippet_len": len(s.event_snippet or ""),
                          "global_site_tag_len": len(s.global_site_tag or "")})
        # extract AW- id and label from the event snippet, without printing the snippet
        awid, label = "", ""
        for s in a.tag_snippets:
            es = s.event_snippet or ""
            if "AW-" in es and "send_to" in es:
                seg = es.split("send_to", 1)[1]
                for tok in seg.replace("'", '"').split('"'):
                    if tok.startswith("AW-") and "/" in tok:
                        awid, label = tok.split("/", 1)
                        break
            if awid:
                break
        ca.append({
            "id": str(a.id), "resource_name": a.resource_name, "name": a.name,
            "status": enum_name(a.status), "type": enum_name(a.type_),
            "category": enum_name(a.category), "origin": enum_name(a.origin),
            "owner_customer": a.owner_customer or "",
            "owner_customer_id": (a.owner_customer or "").split("/")[-1],
            "primary_for_goal": bool(a.primary_for_goal),
            "include_in_conversions_metric": bool(a.include_in_conversions_metric),
            "counting_type": enum_name(a.counting_type),
            "attribution_model": enum_name(a.attribution_model_settings.attribution_model),
            "data_driven_model_status":
                enum_name(a.attribution_model_settings.data_driven_model_status),
            "click_window_days": int(a.click_through_lookback_window_days),
            "view_window_days": int(a.view_through_lookback_window_days),
            "phone_call_duration_seconds": int(a.phone_call_duration_seconds),
            "default_value": float(a.value_settings.default_value),
            "default_currency": a.value_settings.default_currency_code or "",
            "always_use_default_value": bool(a.value_settings.always_use_default_value),
            "tag_snippet_count": len(snips), "tag_snippets": snips,
            "google_tag_id": awid, "conversion_label": label,
            "ga4_property": a.google_analytics_4_settings.property_name or "",
        })
    out["conversion_actions"] = sorted(ca, key=lambda x: (x["category"], x["origin"], x["id"]))
    out["conversion_actions_all_owned_by_this_customer"] = all(
        a["owner_customer_id"] in ("", CID) for a in ca)

    # ---------------- per-action conversion metrics, all time ----------------
    per_action = {}
    # NOTE: metrics.conversions is PROHIBITED FROM conversion_action; only all_conversions
    # is selectable there. Per-action `conversions` comes from the campaign segment below.
    for r in q("""SELECT conversion_action.id, conversion_action.name,
                         metrics.all_conversions, metrics.all_conversions_value
                  FROM conversion_action
                  WHERE segments.date BETWEEN '2026-01-01' AND '2026-09-01'"""):
        per_action[str(r.conversion_action.id)] = {
            "name": r.conversion_action.name,
            "all_conversions": round(float(r.metrics.all_conversions), 4),
            "all_conversions_value": round(float(r.metrics.all_conversions_value), 4),
        }
    out["per_action_alltime_metrics"] = per_action

    # ---------------- account-level all_conversions by action, campaign segmented ----------------
    seg = []
    for r in q("""SELECT campaign.id, segments.conversion_action,
                         segments.conversion_action_name,
                         metrics.all_conversions, metrics.conversions
                  FROM campaign
                  WHERE segments.date BETWEEN '2026-01-01' AND '2026-09-01'"""):
        seg.append({"campaign": str(r.campaign.id),
                    "action": (r.segments.conversion_action or "").split("/")[-1],
                    "action_name": r.segments.conversion_action_name,
                    "all_conversions": round(float(r.metrics.all_conversions), 4),
                    "conversions": round(float(r.metrics.conversions), 4)})
    out["campaign_conversion_action_segments"] = seg
    out["campaign_conversion_action_segment_rows"] = len(seg)

    stamp = now.strftime("%Y-%m-%dT%H%M%S")
    path = SNAP / f"goal-hierarchy-{stamp}.json"
    path.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps(out, indent=2, default=str))
    print("\nWROTE", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
