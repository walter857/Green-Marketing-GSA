#!/usr/bin/env python3
"""Evidence for the BID-1 and BUD-1 revalidation.

SELECT-only. Produces:
  15-bid-evidence.json   per-campaign CPC by month, plus a per-click price
                         distribution reconstructed from keyword-level data
  16-bud-evidence.json   account-wide pacing including EVERY campaign
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
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
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    today = now.date()

    def q(name, query):
        r = list(svc.search(customer_id=CID, query=query))
        print("  ok  %-34s %4d" % (name, len(r)))
        return r

    # ---------- BID EVIDENCE ----------
    bid = {"read_at": now.isoformat(), "campaigns": {}}

    for r in q("bidding_state", """
        SELECT campaign.id, campaign.name, campaign.bidding_strategy_type,
               campaign.bidding_strategy,
               campaign.target_spend.cpc_bid_ceiling_micros
        FROM campaign WHERE campaign.id IN (%s,%s)""" % (PATIO, PAVERS)):
        c = r.campaign
        bid["campaigns"][str(c.id)] = {
            "name": c.name,
            "bidding_strategy_type": enum_name(c.bidding_strategy_type),
            "portfolio_strategy": c.bidding_strategy or None,
            "cpc_bid_ceiling_micros": c.target_spend.cpc_bid_ceiling_micros or None,
            "cpc_bid_ceiling_display": (
                "$%.2f" % (c.target_spend.cpc_bid_ceiling_micros / 1e6)
                if c.target_spend.cpc_bid_ceiling_micros else "NONE"),
            "monthly": {}, "daily_max": None,
        }

    for r in q("cpc_by_month", """
        SELECT campaign.id, segments.month, metrics.cost_micros, metrics.clicks,
               metrics.impressions, metrics.conversions
        FROM campaign
        WHERE segments.date BETWEEN '2026-05-01' AND '%s'
          AND campaign.id IN (%s,%s) ORDER BY segments.month"""
                % (today, PATIO, PAVERS)):
        e = bid["campaigns"][str(r.campaign.id)]
        cost, clicks = r.metrics.cost_micros / 1e6, r.metrics.clicks
        e["monthly"][r.segments.month] = {
            "cost": round(cost, 2), "clicks": clicks,
            "impressions": r.metrics.impressions,
            "conversions": round(r.metrics.conversions, 2),
            "avg_cpc": round(cost / clicks, 2) if clicks else None,
            "cvr": round(r.metrics.conversions / clicks, 4) if clicks else None,
        }

    daily = defaultdict(list)
    for r in q("cpc_by_day", """
        SELECT campaign.id, segments.date, metrics.cost_micros, metrics.clicks
        FROM campaign WHERE segments.date BETWEEN '2026-05-01' AND '%s'
          AND campaign.id IN (%s,%s)""" % (today, PATIO, PAVERS)):
        if r.metrics.clicks:
            daily[str(r.campaign.id)].append({
                "date": r.segments.date,
                "cost": round(r.metrics.cost_micros / 1e6, 2),
                "clicks": r.metrics.clicks,
                "day_cpc": round(r.metrics.cost_micros / 1e6 / r.metrics.clicks, 2)})
    for cid, rows in daily.items():
        rows.sort(key=lambda x: -x["day_cpc"])
        e = bid["campaigns"][cid]
        e["daily_max"] = rows[0]
        e["top_10_most_expensive_days"] = rows[:10]
        e["days_with_clicks"] = len(rows)
        e["days_above_ceiling"] = {}
        for ceil in (14, 16, 18, 20, 22, 25, 30):
            over = [d for d in rows if d["day_cpc"] > ceil]
            e["days_above_ceiling"][str(ceil)] = {
                "days": len(over),
                "share_of_days": round(len(over) / len(rows), 3),
                "cost_on_those_days": round(sum(d["cost"] for d in over), 2),
                "clicks_on_those_days": sum(d["clicks"] for d in over)}

    kw = defaultdict(lambda: {"cost": 0.0, "clicks": 0, "conv": 0.0})
    for r in q("keyword_cpc", """
        SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id,
               metrics.cost_micros, metrics.clicks, metrics.conversions
        FROM keyword_view WHERE segments.date BETWEEN '2026-01-01' AND '%s'
          AND campaign.id IN (%s,%s)""" % (today, PATIO, PAVERS)):
        k = kw[(str(r.campaign.id), str(r.ad_group.id),
                str(r.ad_group_criterion.criterion_id))]
        k["cost"] += r.metrics.cost_micros / 1e6
        k["clicks"] += r.metrics.clicks
        k["conv"] += r.metrics.conversions
    for cid in (PATIO, PAVERS):
        pts = sorted((v["cost"] / v["clicks"], v["clicks"], v["conv"])
                     for k, v in kw.items() if k[0] == cid and v["clicks"])
        tot_c = sum(p[1] for p in pts)
        tot_v = sum(p[2] for p in pts)
        e = bid["campaigns"][cid]
        e["keyword_price_points"] = len(pts)
        e["total_clicks_priced"] = tot_c
        e["total_conversions_priced"] = round(tot_v, 1)
        e["ceiling_scenarios"] = {}
        for ceil in (14, 16, 18, 20, 22, 25, 30):
            keep = [p for p in pts if p[0] <= ceil]
            e["ceiling_scenarios"][str(ceil)] = {
                "keywords_retained": len(keep),
                "clicks_retained": sum(p[1] for p in keep),
                "click_retention": round(sum(p[1] for p in keep) / tot_c, 3) if tot_c else None,
                "conversions_retained": round(sum(p[2] for p in keep), 1),
                "conversion_retention": (round(sum(p[2] for p in keep) / tot_v, 3)
                                         if tot_v else None)}
        e["converting_keyword_cpcs"] = [
            {"avg_cpc": round(p[0], 2), "clicks": p[1], "conversions": round(p[2], 1)}
            for p in pts if p[2] > 0]

    (B / "15-bid-evidence.json").write_text(json.dumps(bid, indent=2), encoding="utf-8")

    # ---------- BUD EVIDENCE ----------
    bud = {"read_at": now.isoformat(), "hard_cap": 2000.00, "month": "2026-09"}
    allc = {}
    for r in q("all_campaign_budgets", """
        SELECT campaign.id, campaign.name, campaign.status,
               campaign_budget.id, campaign_budget.amount_micros,
               campaign_budget.explicitly_shared, campaign_budget.reference_count
        FROM campaign WHERE campaign.status != 'REMOVED'"""):
        allc[str(r.campaign.id)] = {
            "name": r.campaign.name, "status": enum_name(r.campaign.status),
            "budget_id": str(r.campaign_budget.id),
            "daily_budget": round(r.campaign_budget.amount_micros / 1e6, 2),
            "explicitly_shared": r.campaign_budget.explicitly_shared,
            "reference_count": r.campaign_budget.reference_count,
            "mtd_cost": 0.0}
    for r in q("mtd_all_campaigns", """
        SELECT campaign.id, metrics.cost_micros
        FROM campaign WHERE segments.date BETWEEN '2026-09-01' AND '%s'""" % today):
        if str(r.campaign.id) in allc:
            allc[str(r.campaign.id)]["mtd_cost"] = round(r.metrics.cost_micros / 1e6, 2)
    acct = q("mtd_account_total", """
        SELECT metrics.cost_micros FROM customer
        WHERE segments.date BETWEEN '2026-09-01' AND '%s'""" % today)
    mtd = round(acct[0].metrics.cost_micros / 1e6, 2) if acct else 0.0
    days = [{"date": r.segments.date, "cost": round(r.metrics.cost_micros / 1e6, 2)}
            for r in q("account_daily_sept", """
        SELECT segments.date, metrics.cost_micros FROM customer
        WHERE segments.date BETWEEN '2026-09-01' AND '%s'
        ORDER BY segments.date""" % today)]

    enabled = {k: v for k, v in allc.items() if v["status"] == "ENABLED"}
    paused = {k: v for k, v in allc.items() if v["status"] != "ENABLED"}
    remaining_days = 30 - int(str(today)[-2:])
    cur_daily = sum(v["daily_budget"] for v in enabled.values())
    proposed = {PATIO: 24.0, PAVERS: 32.0}
    prop_daily = sum(proposed.get(k, v["daily_budget"]) for k, v in enabled.items())
    complete = [d for d in days if d["date"] < str(today)]
    avg_complete = round(sum(d["cost"] for d in complete) / len(complete), 2) if complete else 0.0

    bud.update({
        "today": str(today), "remaining_days_excluding_today": remaining_days,
        "account_mtd_spend": mtd, "daily_series": days,
        "avg_daily_complete_days_only": avg_complete,
        "all_campaigns": allc,
        "enabled_campaign_count": len(enabled),
        "enabled_campaign_ids": sorted(enabled),
        "paused_campaign_count": len(paused),
        "paused_campaign_mtd_spend": round(sum(v["mtd_cost"] for v in paused.values()), 2),
        "any_shared_budget": any(v["explicitly_shared"] or v["reference_count"] > 1
                                 for v in allc.values()),
        "current_enabled_daily_total": round(cur_daily, 2),
        "proposed_enabled_daily_total": round(prop_daily, 2),
        "remaining_budget": round(max(0.0, 2000.0 - mtd), 2),
        "remaining_daily_allowance": round(max(0.0, 2000.0 - mtd) / remaining_days, 2),
        "projection_current": round(mtd + cur_daily * remaining_days, 2),
        "projection_proposed": round(mtd + prop_daily * remaining_days, 2),
        "projection_at_complete_day_run_rate": round(mtd + avg_complete * remaining_days, 2),
        "headroom_at_proposed": round(2000.0 - (mtd + prop_daily * remaining_days), 2),
        "worst_case_if_all_six_enabled_at_current_budgets": round(
            mtd + sum(v["daily_budget"] for v in allc.values()) * remaining_days, 2),
        "projection_method": ("Account MTD read FROM customer for 2026-09-01..today, "
                              "plus the summed daily budget of every ENABLED campaign "
                              "times the days remaining AFTER today. Today's spend is "
                              "already inside MTD and is still incomplete, so today is "
                              "not double counted."),
    })
    (B / "16-bud-evidence.json").write_text(json.dumps(bud, indent=2), encoding="utf-8")

    print("\nMTD account spend  : $%.2f" % mtd)
    print("enabled campaigns  : %d   paused: %d   paused MTD spend: $%.2f"
          % (len(enabled), len(paused), bud["paused_campaign_mtd_spend"]))
    print("any shared budget  : %s" % bud["any_shared_budget"])
    print("remaining allowance: $%.2f/day over %d days"
          % (bud["remaining_daily_allowance"], remaining_days))
    print("projection current : $%.2f" % bud["projection_current"])
    print("projection proposed: $%.2f  (headroom $%.2f)"
          % (bud["projection_proposed"], bud["headroom_at_proposed"]))
    print("worst case all six : $%.2f" % bud["worst_case_if_all_six_enabled_at_current_budgets"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
