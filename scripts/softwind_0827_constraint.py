#!/usr/bin/env python3
"""Constraint analysis for Softwind Power Washing - 2026-08-27.

Answers, from fresh data only:
  * what each individual click actually cost
  * whether the 80-location geo expansion is live and ENABLED
  * whether budget, rank, demand or schedule is the binding constraint
  * the exact remaining-month math on the ACTUAL account-local date

READ ONLY.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
NAMES = {CAMP_A: "Power Washing", CAMP_B: "Power Washing #2"}
OUT = ROOT / "clients/softwind-power-washing/snapshots/constraint-2026-08-27.json"
TARGET = 2500.0


def rows(svc, query):
    out = []
    for batch in svc.search_stream(customer_id=CID, query=query):
        for r in batch.results:
            out.append(r)
    return out


def usd(m):
    return round((m or 0) / 1_000_000, 2)


def pct(v):
    return None if v is None else round(v * 100, 2)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")

    now = datetime.now(TZ)
    today = now.strftime("%Y-%m-%d")
    a = {"read_only": True, "mutations_issued": 0,
         "snapshot_account_local": now.isoformat(), "today": today}

    # ---------- 1. per-click economics: keyword x day ----------
    q = ("SELECT campaign.id, ad_group.name, "
         "ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
         "segments.date, metrics.impressions, metrics.clicks, "
         "metrics.cost_micros, metrics.average_cpc "
         f"FROM keyword_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-17' AND '{today}' "
         "AND metrics.clicks > 0")
    clicks = []
    for r in rows(svc, q):
        clicks.append({
            "date": r.segments.date, "campaign": NAMES[str(r.campaign.id)],
            "ad_group": r.ad_group.name,
            "keyword": r.ad_group_criterion.keyword.text,
            "match": r.ad_group_criterion.keyword.match_type.name,
            "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
            "cost": usd(r.metrics.cost_micros),
            "avg_cpc": usd(r.metrics.average_cpc)})
    clicks.sort(key=lambda x: (x["date"], -x["cost"]))
    a["billable_clicks_since_aug17"] = clicks
    a["click_count"] = sum(c["clicks"] for c in clicks)
    a["click_cost_total"] = round(sum(c["cost"] for c in clicks), 2)

    # ---------- 2. search terms driving the spend ----------
    q = ("SELECT campaign.id, search_term_view.search_term, "
         "segments.keyword.info.text, segments.search_term_match_type, "
         "metrics.impressions, metrics.clicks, metrics.cost_micros "
         f"FROM search_term_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-17' AND '{today}'")
    st = []
    for r in rows(svc, q):
        st.append({"campaign": NAMES[str(r.campaign.id)],
                   "term": r.search_term_view.search_term,
                   "matched_keyword": r.segments.keyword.info.text,
                   "match": r.segments.search_term_match_type.name,
                   "impressions": r.metrics.impressions,
                   "clicks": r.metrics.clicks,
                   "cost": usd(r.metrics.cost_micros)})
    st.sort(key=lambda x: (-x["cost"], -x["clicks"], -x["impressions"]))
    a["search_terms_since_aug17"] = st
    a["search_term_row_count"] = len(st)

    # ---------- 3. geo criteria really live? ----------
    q = ("SELECT campaign.id, campaign_criterion.criterion_id, "
         "campaign_criterion.negative, campaign_criterion.status, "
         "campaign_criterion.location.geo_target_constant "
         f"FROM campaign_criterion WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND campaign_criterion.type = 'LOCATION'")
    geo = {}
    for r in rows(svc, q):
        cc = r.campaign_criterion
        g = geo.setdefault(str(r.campaign.id),
                           {"positive": {}, "negative": {}, "status_tally": {}})
        gid = cc.location.geo_target_constant.rsplit("/", 1)[-1]
        bucket = "negative" if cc.negative else "positive"
        g[bucket][gid] = cc.status.name
        g["status_tally"][cc.status.name] = g["status_tally"].get(cc.status.name, 0) + 1
    a["geo_criteria"] = {
        k: {"positive_count": len(v["positive"]),
            "negative_count": len(v["negative"]),
            "status_tally": v["status_tally"],
            "non_enabled_positive": {g: s for g, s in v["positive"].items()
                                     if s != "ENABLED"},
            "negative_detail": v["negative"]}
        for k, v in geo.items()}

    # geo performance since the expansion went live (2026-08-26 17:49)
    q = ("SELECT campaign.id, campaign_criterion.criterion_id, "
         "metrics.impressions, metrics.clicks, metrics.cost_micros "
         f"FROM location_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-26' AND '{today}'")
    try:
        lv = [{"campaign": NAMES[str(r.campaign.id)],
               "criterion": r.campaign_criterion.criterion_id,
               "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
               "cost": usd(r.metrics.cost_micros)} for r in rows(svc, q)]
        lv.sort(key=lambda x: -x["impressions"])
        a["location_view_since_expansion"] = lv
    except Exception as exc:
        a["location_view_since_expansion"] = {"error": str(exc)[:300]}

    # ---------- 4. exact remaining-month math ----------
    mtd = 0.0
    q = ("SELECT campaign.id, metrics.cost_micros FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         f"AND segments.date BETWEEN '2026-08-01' AND '{today}'")
    per_campaign_mtd = {}
    for r in rows(svc, q):
        c = usd(r.metrics.cost_micros)
        per_campaign_mtd[NAMES[str(r.campaign.id)]] = c
        mtd += c
    mtd = round(mtd, 2)

    month_end = datetime(2026, 9, 1, 0, 0, 0, tzinfo=TZ)
    H = round((month_end - now).total_seconds() / 3600, 2)
    D = (datetime(2026, 8, 31, tzinfo=TZ).date() - now.date()).days + 1
    R = round(TARGET - mtd, 2)

    # remaining SCHEDULED serving hours, Mon-Sat 08:00-18:00, Sunday off
    serving = []
    cur = now
    while cur < month_end:
        day_start = cur.replace(hour=8, minute=0, second=0, microsecond=0)
        day_end = cur.replace(hour=18, minute=0, second=0, microsecond=0)
        if cur.weekday() != 6:  # 6 = Sunday, no daypart
            s = max(cur, day_start)
            e = min(month_end, day_end)
            if e > s:
                serving.append({"date": cur.strftime("%Y-%m-%d"),
                                "weekday": cur.strftime("%A"),
                                "from": s.strftime("%H:%M"),
                                "to": e.strftime("%H:%M"),
                                "hours": round((e - s).total_seconds() / 3600, 2)})
        cur = (cur + timedelta(days=1)).replace(hour=0, minute=0, second=0,
                                                microsecond=0)
    serving_hours = round(sum(s["hours"] for s in serving), 2)

    combined_budget = 374.44
    a["math"] = {
        "TARGET": TARGET,
        "S_mtd_spend": mtd,
        "S_per_campaign": per_campaign_mtd,
        "R_remaining": R,
        "D_remaining_calendar_days_incl_today": D,
        "H_remaining_hours_to_sept_1_0000": H,
        "required_avg_per_remaining_calendar_day": round(R / D, 2),
        "required_rolling_24h_pace": round(R / (H / 24), 2),
        "remaining_scheduled_serving_hours": serving_hours,
        "remaining_serving_hour_detail": serving,
        "required_spend_per_scheduled_serving_hour": round(R / serving_hours, 2),
        "current_combined_daily_budget": combined_budget,
        "current_combined_daily_delivery_ceiling_2x": round(combined_budget * 2, 2),
        "remaining_month_billing_capacity_at_1x": round(combined_budget * D, 2),
        "remaining_month_billing_capacity_at_2x": round(combined_budget * 2 * D, 2),
        "projected_august_at_current_run_rate": None,  # filled below
    }

    # projection from observed delivery, not from budget
    q = ("SELECT campaign.id, segments.date, metrics.cost_micros FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND segments.date BETWEEN '2026-08-24' AND '2026-08-26'")
    recent = {}
    for r in rows(svc, q):
        recent[r.segments.date] = round(
            recent.get(r.segments.date, 0.0) + usd(r.metrics.cost_micros), 2)
    serving_days_recent = [v for k, v in recent.items()]
    run_rate = round(sum(serving_days_recent) / max(len(serving_days_recent), 1), 2)
    remaining_serving_days = len({s["date"] for s in serving})
    a["math"]["observed_run_rate_per_serving_day_aug24_26"] = run_rate
    a["math"]["recent_daily_detail"] = recent
    a["math"]["remaining_serving_days"] = remaining_serving_days
    a["math"]["projected_august_at_current_run_rate"] = round(
        mtd + run_rate * remaining_serving_days, 2)

    # what a $333.33/$41.11 pair could physically bill
    a["math"]["projected_august_if_budgets_fully_spent_1x"] = round(
        mtd + combined_budget * remaining_serving_days, 2)

    # ---------- 5. impression-share evidence for the constraint call ----------
    q = ("SELECT campaign.id, metrics.impressions, metrics.clicks, "
         "metrics.cost_micros, metrics.search_impression_share, "
         "metrics.search_budget_lost_impression_share, "
         "metrics.search_rank_lost_impression_share, "
         "metrics.search_top_impression_share, "
         "metrics.search_absolute_top_impression_share "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND segments.date BETWEEN '2026-08-20' AND '2026-08-26'")
    a["impression_share_aug20_26"] = {
        NAMES[str(r.campaign.id)]: {
            "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
            "cost": usd(r.metrics.cost_micros),
            "search_is_pct": pct(r.metrics.search_impression_share),
            "lost_is_budget_pct": pct(r.metrics.search_budget_lost_impression_share),
            "lost_is_rank_pct": pct(r.metrics.search_rank_lost_impression_share),
            "top_is_pct": pct(r.metrics.search_top_impression_share),
            "abs_top_is_pct": pct(r.metrics.search_absolute_top_impression_share),
        } for r in rows(svc, q)}

    OUT.write_text(json.dumps(a, indent=2), encoding="utf-8")

    print("=" * 72)
    print("CONSTRAINT ANALYSIS  %s" % now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("=" * 72)

    print("\n--- 1. EVERY BILLABLE CLICK SINCE 2026-08-17 ---")
    print("%-12s %-17s %-34s %-8s %6s %9s" %
          ("DATE", "CAMPAIGN", "KEYWORD", "MATCH", "CLICKS", "COST"))
    for c in clicks:
        print("%-12s %-17s %-34s %-8s %6d %9s" %
              (c["date"], c["campaign"][:17], c["keyword"][:34], c["match"][:8],
               c["clicks"], "$%s" % c["cost"]))
    print("  TOTAL: %d clicks / $%s   AVG CPC $%s"
          % (a["click_count"], a["click_cost_total"],
             round(a["click_cost_total"] / a["click_count"], 2)
             if a["click_count"] else 0))

    print("\n--- 2. SEARCH TERMS SINCE 2026-08-17 (%d rows) ---" % len(st))
    print("%-17s %-40s %6s %6s %9s" % ("CAMPAIGN", "SEARCH TERM", "IMPR", "CLKS", "COST"))
    for s in st[:40]:
        print("%-17s %-40s %6d %6d %9s" %
              (s["campaign"][:17], s["term"][:40], s["impressions"], s["clicks"],
               "$%s" % s["cost"]))

    print("\n--- 3. GEO CRITERIA STATE ---")
    print(json.dumps(a["geo_criteria"], indent=2)[:1500])
    lv = a["location_view_since_expansion"]
    if isinstance(lv, list):
        print("  location_view rows since 2026-08-26: %d" % len(lv))
        for x in lv[:15]:
            print("    %s crit=%s %si/%sc/$%s" % (x["campaign"][:17], x["criterion"],
                                                  x["impressions"], x["clicks"],
                                                  x["cost"]))
    else:
        print("  %s" % json.dumps(lv))

    print("\n--- 4. REMAINING-MONTH MATH (ACTUAL DATE) ---")
    m = a["math"]
    for k in ("TARGET", "S_mtd_spend", "S_per_campaign", "R_remaining",
              "D_remaining_calendar_days_incl_today",
              "H_remaining_hours_to_sept_1_0000",
              "required_avg_per_remaining_calendar_day",
              "required_rolling_24h_pace",
              "remaining_scheduled_serving_hours",
              "required_spend_per_scheduled_serving_hour",
              "current_combined_daily_budget",
              "current_combined_daily_delivery_ceiling_2x",
              "remaining_month_billing_capacity_at_1x",
              "remaining_month_billing_capacity_at_2x",
              "remaining_serving_days",
              "observed_run_rate_per_serving_day_aug24_26",
              "recent_daily_detail",
              "projected_august_at_current_run_rate",
              "projected_august_if_budgets_fully_spent_1x"):
        print("  %-46s %s" % (k, json.dumps(m[k])))
    print("  remaining serving-hour detail:")
    for s in m["remaining_serving_hour_detail"]:
        print("    %s %-9s %s-%s  %5.2fh" % (s["date"], s["weekday"], s["from"],
                                             s["to"], s["hours"]))

    print("\n--- 5. IMPRESSION SHARE 2026-08-20 .. 2026-08-26 ---")
    print(json.dumps(a["impression_share_aug20_26"], indent=2))
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
