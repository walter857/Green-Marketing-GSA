#!/usr/bin/env python3
"""EXECUTE PLAN-A1 - read-only conversion tracking inspection.

SELECT queries and GET navigation only. Creates no lead, no call, no CRM record
and no Google Ads mutation. No form is submitted. No call is placed.

The novel work is action A1-05: determining whether the foreign tag
AW-17878095007 is merely PRESENT in the page or is actively SENDING an event.
Google Ads conversion and remarketing pings carry the AW id in the request PATH,
so the network log answers the question without triggering a conversion.
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name
from playwright.sync_api import sync_playwright

CID = "1521725229"
TZ = ZoneInfo("America/New_York")
OUT = ROOT / "clients/softwind-power-washing/snapshots/plan-a1-inspection-2026-08-26.json"

OWN_AW = "18369652705"
FOREIGN_AW = "17878095007"

PAGES = [
    "https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/",
    "https://offer.softwindli.com/residential-pressure-washing/",
    "https://offer.softwindli.com/house-washing-company/",
]
PAID_QS = ("gclid=TESTGCLID_readonly_plan_a1"
           "&utm_source=google&utm_medium=cpc&utm_campaign=plan-a1")

# Google Ads conversion / remarketing endpoints carry the AW id in the path.
AW_IN_PATH = re.compile(
    r"(?:pagead/(?:viewthroughconversion|conversion|1p-conversion)|"
    r"ccm/conversion|pagead/landing)[/?]([0-9]{9,12})")
AW_IN_QS = re.compile(r"[?&](?:cv|tid|id)=(?:AW-)?([0-9]{9,12})")
CONV_LABEL = re.compile(r"AW-([0-9]{9,12})/([A-Za-z0-9_\-]{6,})")


def main() -> int:
    out = {"executed_account_local": datetime.now(TZ).isoformat(),
           "plan_id": "PLAN-A1", "mode": "READ-ONLY",
           "forms_submitted": 0, "calls_placed": 0,
           "google_ads_mutations": 0}

    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    # ---------------- A1-04 identifiers ----------------
    row = next(iter(svc.search(customer_id=CID, query="""
        SELECT customer.id, customer.descriptive_name,
               customer.conversion_tracking_setting.conversion_tracking_id,
               customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
               customer.conversion_tracking_setting.conversion_tracking_status,
               customer.conversion_tracking_setting.google_ads_conversion_customer,
               customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled,
               customer.auto_tagging_enabled
        FROM customer LIMIT 1""")))
    c = row.customer
    cts = c.conversion_tracking_setting
    out["A1_04_identifiers"] = {
        "customer_id": normalize_customer_id(c.id),
        "descriptive_name": c.descriptive_name,
        "conversion_tracking_id": str(cts.conversion_tracking_id or ""),
        "cross_account_conversion_tracking_id": str(
            cts.cross_account_conversion_tracking_id or ""),
        "conversion_tracking_status": enum_name(cts.conversion_tracking_status),
        "google_ads_conversion_customer": cts.google_ads_conversion_customer or "",
        "enhanced_conversions_for_leads_enabled": bool(
            cts.enhanced_conversions_for_leads_enabled),
        "auto_tagging_enabled": bool(c.auto_tagging_enabled),
        "own_aw_tag_expected": "AW-%s" % (cts.conversion_tracking_id or ""),
        "foreign_aw_tag_observed": "AW-%s" % FOREIGN_AW,
        "foreign_tag_belongs_to_this_account": str(
            cts.conversion_tracking_id or "") == FOREIGN_AW,
    }

    # ---------------- A1-01 configuration ----------------
    actions = []
    for r in svc.search(customer_id=CID, query="""
        SELECT conversion_action.id, conversion_action.name,
               conversion_action.status, conversion_action.type,
               conversion_action.category, conversion_action.origin,
               conversion_action.primary_for_goal,
               conversion_action.counting_type,
               conversion_action.attribution_model_settings.attribution_model,
               conversion_action.attribution_model_settings.data_driven_model_status,
               conversion_action.click_through_lookback_window_days,
               conversion_action.view_through_lookback_window_days,
               conversion_action.phone_call_duration_seconds,
               conversion_action.value_settings.default_value,
               conversion_action.value_settings.always_use_default_value,
               conversion_action.include_in_conversions_metric,
               conversion_action.owner_customer,
               conversion_action.tag_snippets
        FROM conversion_action ORDER BY conversion_action.id"""):
        a = r.conversion_action
        snips = []
        for t in a.tag_snippets:
            snips.append({
                "type": enum_name(t.type_),
                "page_format": enum_name(t.page_format),
                "has_global_site_tag": bool(t.global_site_tag),
                "has_event_snippet": bool(t.event_snippet),
                "event_snippet_mentions_send_to": bool(
                    t.event_snippet and "send_to" in t.event_snippet),
                "conversion_label_in_snippet": (
                    CONV_LABEL.search(t.event_snippet).group(0)
                    if t.event_snippet and CONV_LABEL.search(t.event_snippet) else None),
            })
        cfg_issues = []
        if a.value_settings.always_use_default_value and not a.value_settings.default_value:
            cfg_issues.append("every conversion valued $0.00")
        if a.category.name == "GET_DIRECTIONS" and a.primary_for_goal:
            cfg_issues.append("diagnostic action marked primary_for_goal at account level")
        if enum_name(a.type_) in ("WEBPAGE",) and not a.tag_snippets:
            cfg_issues.append("WEBPAGE action with no tag snippet")
        actions.append({
            "id": str(a.id), "name": a.name, "status": enum_name(a.status),
            "type": enum_name(a.type_), "category": enum_name(a.category),
            "origin": enum_name(a.origin),
            "primary_for_goal": bool(a.primary_for_goal),
            "counting_type": enum_name(a.counting_type),
            "attribution_model": enum_name(
                a.attribution_model_settings.attribution_model),
            "data_driven_status": enum_name(
                a.attribution_model_settings.data_driven_model_status),
            "click_lookback_days": int(a.click_through_lookback_window_days),
            "view_lookback_days": int(a.view_through_lookback_window_days),
            "phone_call_duration_seconds": int(a.phone_call_duration_seconds),
            "default_value": a.value_settings.default_value,
            "always_use_default_value": bool(a.value_settings.always_use_default_value),
            "include_in_conversions_metric": bool(a.include_in_conversions_metric),
            "owner_customer": a.owner_customer or "",
            "owner_is_this_account": a.owner_customer.endswith(CID) if a.owner_customer else False,
            "tag_snippet_count": len(a.tag_snippets),
            "tag_snippets": snips,
            "configuration_issues": cfg_issues,
            "technically_configured": not cfg_issues or all(
                "valued $0.00" in i or "primary_for_goal" in i for i in cfg_issues),
        })
    out["A1_01_conversion_actions"] = actions

    # ---------------- A1-02 goals ----------------
    goals = defaultdict(list)
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, campaign_conversion_goal.category,
               campaign_conversion_goal.origin, campaign_conversion_goal.biddable
        FROM campaign_conversion_goal"""):
        g = r.campaign_conversion_goal
        goals[str(r.campaign.id)].append(
            {"category": enum_name(g.category), "origin": enum_name(g.origin),
             "biddable": bool(g.biddable)})
    cust_goals = [{"category": enum_name(x.customer_conversion_goal.category),
                   "origin": enum_name(x.customer_conversion_goal.origin),
                   "biddable": bool(x.customer_conversion_goal.biddable)}
                  for x in svc.search(customer_id=CID, query="""
        SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
               customer_conversion_goal.biddable FROM customer_conversion_goal""")]
    out["A1_02_goals"] = {
        "per_campaign": {k: v for k, v in goals.items()},
        "per_campaign_biddable": {
            k: [g for g in v if g["biddable"]] for k, v in goals.items()},
        "customer_level": cust_goals,
        "get_directions_biddable_anywhere": any(
            g["category"] == "GET_DIRECTIONS" and g["biddable"]
            for v in goals.values() for g in v),
    }

    # ---------------- A1-03 recorded volume ----------------
    perf = []
    for r in svc.search(customer_id=CID, query="""
        SELECT conversion_action.name, conversion_action.category,
               metrics.all_conversions, metrics.all_conversions_value
        FROM conversion_action
        WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-26'"""):
        perf.append({"name": r.conversion_action.name,
                     "category": enum_name(r.conversion_action.category),
                     "all_conversions": float(r.metrics.all_conversions),
                     "value": float(r.metrics.all_conversions_value)})
    seg = list(svc.search(customer_id=CID, query="""
        SELECT segments.conversion_action_name, segments.date,
               metrics.all_conversions FROM campaign
        WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-26'"""))
    # phone_calls / phone_impressions are not selectable from CUSTOMER in v25;
    # they are campaign-level metrics, so aggregate across campaigns instead.
    tot = {"impressions": 0, "clicks": 0, "conversions": 0.0,
           "all_conversions": 0.0, "phone_calls": 0, "phone_impressions": 0}
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, metrics.impressions, metrics.clicks,
               metrics.conversions, metrics.all_conversions,
               metrics.phone_calls, metrics.phone_impressions
        FROM campaign WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-26'"""):
        m = r.metrics
        tot["impressions"] += int(m.impressions)
        tot["clicks"] += int(m.clicks)
        tot["conversions"] += float(m.conversions)
        tot["all_conversions"] += float(m.all_conversions)
        tot["phone_calls"] += int(m.phone_calls)
        tot["phone_impressions"] += int(m.phone_impressions)
    out["A1_03_recorded_volume"] = {
        "per_action": perf,
        "conversion_action_name_segment_rows": len(seg),
        "account_totals": tot,
        "any_action_has_ever_recorded": any(p["all_conversions"] > 0 for p in perf),
    }

    # ---------------- A1-05 tag activity ----------------
    pages_out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True,
                               args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"),
            locale="en-US", timezone_id="America/New_York")
        ctx.set_extra_http_headers({"Referer": "https://www.google.com/"})
        for url in PAGES:
            page = ctx.new_page()
            reqs: list[str] = []
            page.on("request", lambda r: reqs.append(r.url))
            target = url + ("&" if "?" in url else "?") + PAID_QS
            rec = {"url": url}
            try:
                resp = page.goto(target, wait_until="domcontentloaded", timeout=60000)
                rec["http_status"] = resp.status if resp else None
                page.wait_for_load_state("networkidle", timeout=30000)
            except Exception as e:
                rec["error"] = str(e)[:140]
            time.sleep(6)
            try:
                html = page.content()
            except Exception:
                html = ""

            aw_hits = defaultdict(list)
            for u in reqs:
                for m in AW_IN_PATH.finditer(u):
                    aw_hits[m.group(1)].append(u[:180])
                for m in AW_IN_QS.finditer(u):
                    aw_hits[m.group(1)].append(u[:180])
            rec["aw_ids_in_outbound_requests"] = {
                k: {"request_count": len(v), "sample": v[:3]}
                for k, v in sorted(aw_hits.items())}
            rec["own_tag_sending"] = OWN_AW in aw_hits
            rec["foreign_tag_sending"] = FOREIGN_AW in aw_hits
            rec["aw_ids_present_in_dom"] = sorted(
                set(re.findall(r"AW-([0-9]{9,12})", html)))
            rec["conversion_labels_in_dom"] = sorted(
                set(m.group(0) for m in CONV_LABEL.finditer(html)))
            rec["google_conversion_endpoints_hit"] = sorted({
                re.sub(r"\?.*", "", u) for u in reqs
                if re.search(r"googleadservices\.com/pagead/conversion|"
                             r"googleads\.g\.doubleclick\.net/pagead|"
                             r"google\.com/pagead/1p-conversion", u)})[:8]
            rec["total_requests"] = len(reqs)
            pages_out.append(rec)
            page.close()
            time.sleep(2)
        ctx.close()
        b.close()
    out["A1_05_tag_activity"] = pages_out

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # ---------------- report ----------------
    i = out["A1_04_identifiers"]
    print("A1-04  IDENTIFIERS")
    print("  account                     : %s / %s" % (i["descriptive_name"], i["customer_id"]))
    print("  conversion_tracking_id      : %s  -> own tag %s" % (
        i["conversion_tracking_id"], i["own_aw_tag_expected"]))
    print("  cross_account tracking id   : %s" % (i["cross_account_conversion_tracking_id"] or "(none)"))
    print("  tracking status             : %s" % i["conversion_tracking_status"])
    print("  conversion customer         : %s" % i["google_ads_conversion_customer"])
    print("  auto-tagging                : %s" % i["auto_tagging_enabled"])
    print("  enhanced conv. for leads    : %s" % i["enhanced_conversions_for_leads_enabled"])
    print("  foreign AW-%s belongs here? %s" % (FOREIGN_AW, i["foreign_tag_belongs_to_this_account"]))
    print()
    print("A1-01  CONVERSION ACTION CONFIGURATION")
    for a in out["A1_01_conversion_actions"]:
        print("  %s  %s" % (a["id"], a["name"]))
        print("      %s / %s / %s | primary_for_goal=%s | %s | attr=%s"
              % (a["status"], a["type"], a["category"], a["primary_for_goal"],
                 a["counting_type"], a["attribution_model"]))
        print("      click_lookback=%dd view=%dd call_min=%ds value=%.1f always_default=%s"
              % (a["click_lookback_days"], a["view_lookback_days"],
                 a["phone_call_duration_seconds"], a["default_value"],
                 a["always_use_default_value"]))
        print("      owner_is_this_account=%s  tag_snippets=%d"
              % (a["owner_is_this_account"], a["tag_snippet_count"]))
        for s in a["tag_snippets"]:
            print("         snippet: %s/%s global=%s event=%s label=%s"
                  % (s["type"], s["page_format"], s["has_global_site_tag"],
                     s["has_event_snippet"], s["conversion_label_in_snippet"]))
        print("      issues: %s" % (a["configuration_issues"] or "none"))
    print()
    print("A1-02  GOALS")
    for cid_, gl in out["A1_02_goals"]["per_campaign_biddable"].items():
        print("  campaign %s biddable: %s" % (cid_, [(g["category"], g["origin"]) for g in gl]))
    print("  customer-level goals: %s" % out["A1_02_goals"]["customer_level"])
    print("  GET_DIRECTIONS biddable anywhere: %s"
          % out["A1_02_goals"]["get_directions_biddable_anywhere"])
    print()
    print("A1-03  RECORDED VOLUME")
    for p in out["A1_03_recorded_volume"]["per_action"]:
        print("  %-52s all_conversions=%.1f" % (p["name"], p["all_conversions"]))
    print("  account totals: %s" % out["A1_03_recorded_volume"]["account_totals"])
    print("  conversion_action_name segment rows: %d"
          % out["A1_03_recorded_volume"]["conversion_action_name_segment_rows"])
    print("  any action ever recorded: %s"
          % out["A1_03_recorded_volume"]["any_action_has_ever_recorded"])
    print()
    print("A1-05  TAG ACTIVITY (which AW account actually receives a hit)")
    for p in out["A1_05_tag_activity"]:
        print("  %s" % p["url"])
        print("      status=%s requests=%s" % (p.get("http_status"), p.get("total_requests")))
        print("      AW ids in DOM            : %s" % p.get("aw_ids_present_in_dom"))
        print("      AW ids SENDING requests  : %s"
              % list(p.get("aw_ids_in_outbound_requests", {}).keys()))
        print("      own tag %s sending  : %s" % (OWN_AW, p.get("own_tag_sending")))
        print("      FOREIGN %s sending  : %s" % (FOREIGN_AW, p.get("foreign_tag_sending")))
        print("      conversion labels in DOM : %s" % p.get("conversion_labels_in_dom"))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
