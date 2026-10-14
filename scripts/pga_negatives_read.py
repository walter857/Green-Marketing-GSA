#!/usr/bin/env python3
"""Fresh read-only account read for the Pro Green Austin campaign-negative package.

GAQL SELECT only, routed through the repository read-only guard. Every query is
isolated: one failure is recorded in read_errors and skipped.

Output policy: row-level data goes to JSON on disk. Only counts and aggregates are
printed. Raw search-term strings are never printed to the console.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.audit import ReadOnlyAudit  # noqa: E402
from gm_gsa.config import load_dotenv_if_available, load_yaml  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402


def E(v):
    try:
        return enum_name(v)
    except Exception:  # noqa: BLE001
        return str(v)


def micros(v):
    try:
        return int(v) / 1_000_000
    except Exception:  # noqa: BLE001
        return 0.0


def last_id(resource_name):
    return str(resource_name or "").rsplit("/", 1)[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    args = ap.parse_args()

    profile = load_yaml(args.client)["client"]
    cid = str(profile["google_ads"]["child_customer_id"])
    expected = profile["google_ads"]["exact_child_account_name"]

    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    r = ReadOnlyAudit(client, cid)

    snap = {
        "customer_id": cid,
        "expected_account_name": expected,
        "read_started_utc": datetime.now(timezone.utc).isoformat(),
        "window": {"start": args.start, "end": args.end},
    }

    # ---------------- 1. identity gate ----------------
    ident = r.rows("identity", """
        SELECT customer.id, customer.descriptive_name, customer.manager,
               customer.test_account, customer.currency_code, customer.time_zone,
               customer.status, customer.auto_tagging_enabled
        FROM customer
    """)
    if not ident:
        print("IDENTITY READ FAILED", json.dumps(r.read_errors, indent=2))
        return 2
    c = ident[0].customer
    snap["identity"] = {
        "id": str(c.id), "descriptive_name": c.descriptive_name,
        "manager": bool(c.manager), "test_account": bool(c.test_account),
        "currency_code": c.currency_code, "time_zone": c.time_zone,
        "status": E(c.status), "auto_tagging_enabled": bool(c.auto_tagging_enabled),
    }
    if str(c.id) != cid or c.descriptive_name != expected or c.manager or c.test_account:
        print("IDENTITY MISMATCH", json.dumps(snap["identity"], indent=2))
        return 3

    # ---------------- 2. campaigns ----------------
    snap["campaigns"] = [{
        "id": str(x.campaign.id), "name": x.campaign.name,
        "status": E(x.campaign.status), "channel": E(x.campaign.advertising_channel_type),
        "resource_name": x.campaign.resource_name,
    } for x in r.rows("campaigns", """
        SELECT campaign.id, campaign.name, campaign.status,
               campaign.advertising_channel_type, campaign.resource_name
        FROM campaign
    """)]
    live_ids = [c["id"] for c in snap["campaigns"] if c["status"] == "ENABLED"]
    in_list = "(" + ",".join(live_ids) + ")" if live_ids else "(0)"

    # ---------------- 3. ad groups ----------------
    snap["ad_groups"] = [{
        "id": str(x.ad_group.id), "name": x.ad_group.name, "status": E(x.ad_group.status),
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
    } for x in r.rows("ad_groups", """
        SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id, campaign.name
        FROM ad_group WHERE campaign.id IN {}
    """.format(in_list))]

    # ---------------- 4. ad-group keyword criteria (positive + negative) ----------
    snap["ad_group_keywords"] = [{
        "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
        "campaign_id": str(x.campaign.id),
        "criterion_id": str(x.ad_group_criterion.criterion_id),
        "text": x.ad_group_criterion.keyword.text,
        "match_type": E(x.ad_group_criterion.keyword.match_type),
        "status": E(x.ad_group_criterion.status),
        "negative": bool(x.ad_group_criterion.negative),
        "resource_name": x.ad_group_criterion.resource_name,
    } for x in r.rows("ad_group_keywords", """
        SELECT ad_group.id, ad_group.name, campaign.id,
               ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type, ad_group_criterion.status,
               ad_group_criterion.negative, ad_group_criterion.resource_name
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = KEYWORD AND campaign.id IN {}
    """.format(in_list))]

    # ---------------- 5. campaign negative keywords ----------------
    snap["campaign_negative_keywords"] = [{
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "criterion_id": str(x.campaign_criterion.criterion_id),
        "text": x.campaign_criterion.keyword.text,
        "match_type": E(x.campaign_criterion.keyword.match_type),
        "status": E(x.campaign_criterion.status),
        "resource_name": x.campaign_criterion.resource_name,
    } for x in r.rows("campaign_negative_keywords", """
        SELECT campaign.id, campaign.name, campaign_criterion.criterion_id,
               campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
               campaign_criterion.status, campaign_criterion.resource_name
        FROM campaign_criterion
        WHERE campaign_criterion.type = KEYWORD AND campaign_criterion.negative = TRUE
    """)]

    # ---------------- 6. shared sets / links / members ----------------
    snap["shared_sets"] = [{
        "id": str(x.shared_set.id), "name": x.shared_set.name,
        "type": E(x.shared_set.type_), "status": E(x.shared_set.status),
        "member_count": int(x.shared_set.member_count),
    } for x in r.rows("shared_sets", """
        SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status,
               shared_set.member_count FROM shared_set
    """)]
    snap["campaign_shared_sets"] = [{
        "campaign_id": str(x.campaign.id), "shared_set_id": str(x.shared_set.id),
        "link_status": E(x.campaign_shared_set.status),
    } for x in r.rows("campaign_shared_sets", """
        SELECT campaign.id, shared_set.id, campaign_shared_set.status
        FROM campaign_shared_set
    """)]
    snap["shared_criteria"] = [{
        "shared_set_id": str(x.shared_set.id),
        "criterion_id": str(x.shared_criterion.criterion_id),
        "keyword_text": x.shared_criterion.keyword.text,
        "match_type": E(x.shared_criterion.keyword.match_type),
    } for x in r.rows("shared_criteria", """
        SELECT shared_set.id, shared_criterion.criterion_id, shared_criterion.keyword.text,
               shared_criterion.keyword.match_type, shared_criterion.type
        FROM shared_criterion WHERE shared_criterion.type = KEYWORD
    """)]
    snap["customer_negative_criteria"] = [{
        "criterion_id": str(x.customer_negative_criterion.id),
        "type": E(x.customer_negative_criterion.type_),
    } for x in r.rows("customer_negative_criteria", """
        SELECT customer_negative_criterion.id, customer_negative_criterion.type
        FROM customer_negative_criterion
    """)]

    # ---------------- 7. search terms, window, NOT segmented by date -------------
    st_cols = """
          search_term_view.search_term, search_term_view.status,
          segments.search_term_match_type, segments.keyword.info.text,
          segments.keyword.info.match_type, segments.keyword.ad_group_criterion,
          campaign.id, campaign.name, campaign.status, ad_group.id, ad_group.name,
          metrics.impressions, metrics.clicks, metrics.cost_micros,
          metrics.conversions, metrics.all_conversions, metrics.conversions_value,
          metrics.all_conversions_value
    """

    def st_row(x, with_date=False):
        d = {
            "term": x.search_term_view.search_term,
            "added_excluded": E(x.search_term_view.status),
            "search_term_match_type": E(x.segments.search_term_match_type),
            "matched_keyword": x.segments.keyword.info.text,
            "matched_match_type": E(x.segments.keyword.info.match_type),
            "matched_keyword_criterion": x.segments.keyword.ad_group_criterion,
            "matched_keyword_id": last_id(x.segments.keyword.ad_group_criterion),
            "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
            "campaign_status": E(x.campaign.status),
            "ad_group_id": str(x.ad_group.id), "ad_group_name": x.ad_group.name,
            "impressions": int(x.metrics.impressions), "clicks": int(x.metrics.clicks),
            "cost": micros(x.metrics.cost_micros),
            "conversions": float(x.metrics.conversions),
            "all_conversions": float(x.metrics.all_conversions),
            "conversions_value": float(x.metrics.conversions_value),
            "all_conversions_value": float(x.metrics.all_conversions_value),
        }
        if with_date:
            d["date"] = x.segments.date
        return d

    snap["search_terms_window"] = [st_row(x) for x in r.rows("search_terms_window", """
        SELECT {} FROM search_term_view
        WHERE segments.date BETWEEN '{}' AND '{}'
    """.format(st_cols, args.start, args.end))]
    snap["search_terms_window_by_date"] = [
        st_row(x, True) for x in r.rows("search_terms_window_by_date", """
        SELECT segments.date, {} FROM search_term_view
        WHERE segments.date BETWEEN '{}' AND '{}'
    """.format(st_cols, args.start, args.end))]

    # ---------------- 8. all-time converting queries ----------------
    snap["search_terms_all_time_converting"] = [
        st_row(x) for x in r.rows("search_terms_all_time_converting", """
        SELECT {} FROM search_term_view
        WHERE segments.date BETWEEN '2023-01-01' AND '{}'
          AND metrics.conversions > 0
    """.format(st_cols, args.end))]
    snap["search_terms_all_time_all_conv"] = [
        st_row(x) for x in r.rows("search_terms_all_time_all_conv", """
        SELECT {} FROM search_term_view
        WHERE segments.date BETWEEN '2023-01-01' AND '{}'
          AND metrics.all_conversions > 0
    """.format(st_cols, args.end))]

    # ---------------- 9. campaign spend for the same window ----------------
    snap["campaign_totals_window"] = [{
        "campaign_id": str(x.campaign.id), "campaign_name": x.campaign.name,
        "status": E(x.campaign.status), "channel": E(x.campaign.advertising_channel_type),
        "impressions": int(x.metrics.impressions), "clicks": int(x.metrics.clicks),
        "cost": micros(x.metrics.cost_micros), "conversions": float(x.metrics.conversions),
        "all_conversions": float(x.metrics.all_conversions),
        "conversions_value": float(x.metrics.conversions_value),
    } for x in r.rows("campaign_totals_window", """
        SELECT campaign.id, campaign.name, campaign.status,
               campaign.advertising_channel_type, metrics.impressions, metrics.clicks,
               metrics.cost_micros, metrics.conversions, metrics.all_conversions,
               metrics.conversions_value
        FROM campaign WHERE segments.date BETWEEN '{}' AND '{}'
    """.format(args.start, args.end))]
    snap["campaign_totals_window_by_date"] = [{
        "date": x.segments.date, "campaign_id": str(x.campaign.id),
        "impressions": int(x.metrics.impressions), "clicks": int(x.metrics.clicks),
        "cost": micros(x.metrics.cost_micros), "conversions": float(x.metrics.conversions),
    } for x in r.rows("campaign_totals_window_by_date", """
        SELECT segments.date, campaign.id, metrics.impressions, metrics.clicks,
               metrics.cost_micros, metrics.conversions
        FROM campaign WHERE segments.date BETWEEN '{}' AND '{}'
          AND campaign.id IN {}
    """.format(args.start, args.end, in_list))]

    # ---------------- 10. final URLs in the live campaigns ----------------
    snap["ad_final_urls"] = [{
        "campaign_id": str(x.campaign.id), "ad_group_id": str(x.ad_group.id),
        "ad_group_name": x.ad_group.name, "ad_id": str(x.ad_group_ad.ad.id),
        "status": E(x.ad_group_ad.status),
        "final_urls": list(x.ad_group_ad.ad.final_urls),
    } for x in r.rows("ad_final_urls", """
        SELECT campaign.id, ad_group.id, ad_group.name, ad_group_ad.ad.id,
               ad_group_ad.status, ad_group_ad.ad.final_urls
        FROM ad_group_ad WHERE campaign.id IN {}
    """.format(in_list))]

    # ---------------- 11. change events (negative-keyword history) --------------
    end_dt = args.end + " 23:59:59"
    start_dt = (date.fromisoformat(args.end) - timedelta(days=29)).isoformat() + " 00:00:00"
    snap["change_events"] = [{
        "change_date_time": x.change_event.change_date_time,
        "resource_type": E(x.change_event.change_resource_type),
        "operation": E(x.change_event.resource_change_operation),
        "changed_fields": list(x.change_event.changed_fields.paths),
        "campaign": x.change_event.campaign, "ad_group": x.change_event.ad_group,
        "change_resource_name": x.change_event.change_resource_name,
        "new_keyword_text": x.change_event.new_resource.ad_group_criterion.keyword.text,
        "new_keyword_match_type": E(
            x.change_event.new_resource.ad_group_criterion.keyword.match_type),
        "new_campaign_keyword_text": (
            x.change_event.new_resource.campaign_criterion.keyword.text),
        "new_campaign_keyword_match_type": E(
            x.change_event.new_resource.campaign_criterion.keyword.match_type),
        "client_type": E(x.change_event.client_type),
    } for x in r.rows("change_events", """
        SELECT change_event.change_date_time, change_event.change_resource_type,
               change_event.resource_change_operation, change_event.changed_fields,
               change_event.campaign, change_event.ad_group,
               change_event.change_resource_name, change_event.new_resource,
               change_event.client_type
        FROM change_event
        WHERE change_event.change_date_time >= '{}'
          AND change_event.change_date_time <= '{}'
        ORDER BY change_event.change_date_time DESC LIMIT 10000
    """.format(start_dt, end_dt))]
    snap["change_event_limitation"] = (
        "change_event is capped at the last 30 days by the Google Ads API.")

    snap["read_errors"] = r.read_errors
    snap["queries_executed"] = r.queries_executed
    snap["read_finished_utc"] = datetime.now(timezone.utc).isoformat()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snap, indent=1), encoding="utf-8")

    ident_line = snap["identity"]
    print("IDENTITY  {} | {} | manager={} test={} | {} | {}".format(
        ident_line["descriptive_name"], ident_line["id"], ident_line["manager"],
        ident_line["test_account"], ident_line["currency_code"], ident_line["time_zone"]))
    for k in ("campaigns", "ad_groups", "ad_group_keywords", "campaign_negative_keywords",
              "shared_sets", "campaign_shared_sets", "shared_criteria",
              "customer_negative_criteria", "search_terms_window",
              "search_terms_window_by_date", "search_terms_all_time_converting",
              "search_terms_all_time_all_conv", "campaign_totals_window",
              "campaign_totals_window_by_date", "ad_final_urls", "change_events"):
        print("  {:<36} {}".format(k, len(snap[k])))
    print("  read_errors                          {}".format(len(snap["read_errors"])))
    for e in snap["read_errors"]:
        print("   !", e["query"], "->", e["error"][:300])
    print("written:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
