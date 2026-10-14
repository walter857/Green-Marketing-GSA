#!/usr/bin/env python3
"""Softwind August month-end pacing checkpoint. READ-ONLY.

Run manually at 09:00, 13:00, 17:00 and end of day America/New_York.
SELECT queries only. It NEVER writes a budget or any other field.

    python scripts/softwind_pacing_check.py
    python scripts/softwind_pacing_check.py --label 13:00
"""
from __future__ import annotations

import argparse
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
TZ = ZoneInfo("America/New_York")
TARGET = 2500.0
SEP1 = datetime(2026, 9, 1, 0, 0, 0, tzinfo=TZ)
OUTDIR = ROOT / "clients/softwind-power-washing/receipts"

# Emergency high-CPC stop condition thresholds (monitoring rule, not a mutation)
SINGLE_CLICK_INVESTIGATE = 40.00
SINGLE_CLICK_STOP = 60.00
ROLLING_CPC_INVESTIGATE = 38.00
ROLLING_CPC_STOP = 45.00

QUALIFIED = None  # loaded from the search-term verdict CSV if present


def load_verdicts():
    import csv
    p = ROOT / "clients/softwind-power-washing/audits/2026-08-25-search-term-verdicts.csv"
    if not p.exists():
        return {}
    out = {}
    with p.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["search_term"].lower()] = row["verdict"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default=None, help="checkpoint label, e.g. 13:00")
    args = ap.parse_args()

    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    today = now.date().isoformat()
    label = args.label or now.strftime("%H:%M")
    verdicts = load_verdicts()

    # identity gate on every checkpoint
    c = next(iter(svc.search(customer_id=CID, query="""
        SELECT customer.id, customer.descriptive_name, customer.manager,
               customer.test_account FROM customer LIMIT 1"""))).customer
    if (c.descriptive_name != "Softwind Power Washing - Live"
            or normalize_customer_id(c.id) != CID or c.manager or c.test_account):
        print("*** IDENTITY GATE FAILED - STOP ***")
        return 1

    def agg(lo, hi):
        t = {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0}
        per = {}
        for r in svc.search(customer_id=CID, query="""
            SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks,
                   metrics.cost_micros, metrics.conversions,
                   metrics.search_budget_lost_impression_share,
                   metrics.search_rank_lost_impression_share,
                   metrics.search_impression_share
            FROM campaign WHERE segments.date BETWEEN '%s' AND '%s'""" % (lo, hi)):
            m = r.metrics
            d = {"campaign": r.campaign.name, "impressions": int(m.impressions),
                 "clicks": int(m.clicks), "cost": m.cost_micros / 1_000_000,
                 "conversions": float(m.conversions),
                 "lost_is_budget": float(m.search_budget_lost_impression_share) or None,
                 "lost_is_rank": float(m.search_rank_lost_impression_share) or None,
                 "search_is": float(m.search_impression_share) or None}
            per[str(r.campaign.id)] = d
            for k in t:
                t[k] += d[k]
        return t, per

    mtd, mtd_per = agg("2026-08-01", today)
    tod, tod_per = agg(today, today)

    S = round(mtd["cost"], 2)
    R = round(TARGET - S, 2)
    H = (SEP1 - now).total_seconds() / 3600.0
    req_pace = R / (H / 24) if H > 0 else 0
    # actual rolling pace: today's spend extrapolated over the elapsed portion of today
    elapsed_today = (now - now.replace(hour=0, minute=0, second=0,
                                       microsecond=0)).total_seconds() / 3600.0
    actual_pace = (tod["cost"] / elapsed_today * 24) if elapsed_today > 0 else 0
    projected = S + actual_pace * (H / 24)

    # budgets
    budgets = {}
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, campaign_budget.id,
               campaign_budget.amount_micros FROM campaign"""):
        budgets[str(r.campaign.id)] = {
            "campaign": r.campaign.name,
            "budget_id": str(r.campaign_budget.id),
            "daily_budget": r.campaign_budget.amount_micros / 1_000_000}
    comb_budget = sum(b["daily_budget"] for b in budgets.values())

    # click-level CPC today and rolling 3 days
    clicks = []
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.name, ad_group.name, segments.date,
               ad_group_criterion.keyword.text, metrics.clicks, metrics.cost_micros
        FROM keyword_view WHERE segments.date BETWEEN '2026-08-01' AND '%s'
          AND metrics.clicks > 0""" % today):
        n = int(r.metrics.clicks)
        cpc = (r.metrics.cost_micros / 1_000_000) / n
        for _ in range(n):
            clicks.append({"date": r.segments.date, "campaign": r.campaign.name,
                           "ad_group": r.ad_group.name,
                           "keyword": r.ad_group_criterion.keyword.text,
                           "cpc": round(cpc, 2)})
    today_clicks = [c for c in clicks if c["date"] == today]
    rolling_cpc = (sum(c["cpc"] for c in clicks) / len(clicks)) if clicks else 0

    # search terms today, with qualification
    terms = []
    for r in svc.search(customer_id=CID, query="""
        SELECT search_term_view.search_term, ad_group.name, campaign.name,
               metrics.impressions, metrics.clicks, metrics.cost_micros,
               metrics.conversions
        FROM search_term_view WHERE segments.date BETWEEN '%s' AND '%s'
        ORDER BY metrics.cost_micros DESC""" % (today, today)):
        t = r.search_term_view.search_term
        terms.append({"search_term": t, "ad_group": r.ad_group.name,
                      "campaign": r.campaign.name,
                      "impressions": int(r.metrics.impressions),
                      "clicks": int(r.metrics.clicks),
                      "cost": round(r.metrics.cost_micros / 1_000_000, 2),
                      "conversions": float(r.metrics.conversions),
                      "verdict": verdicts.get(t.lower(), "UNCLASSIFIED - review")})

    # ---- emergency high-CPC stop condition ----
    alerts = []
    for c2 in today_clicks:
        if c2["cpc"] >= SINGLE_CLICK_STOP:
            alerts.append({"level": "STOP", "type": "single_click",
                           "detail": "$%.2f on '%s'" % (c2["cpc"], c2["keyword"])})
        elif c2["cpc"] >= SINGLE_CLICK_INVESTIGATE:
            alerts.append({"level": "INVESTIGATE", "type": "single_click",
                           "detail": "$%.2f on '%s'" % (c2["cpc"], c2["keyword"])})
    if rolling_cpc >= ROLLING_CPC_STOP:
        alerts.append({"level": "STOP", "type": "rolling_cpc",
                       "detail": "rolling avg CPC $%.2f" % rolling_cpc})
    elif rolling_cpc >= ROLLING_CPC_INVESTIGATE:
        alerts.append({"level": "INVESTIGATE", "type": "rolling_cpc",
                       "detail": "rolling avg CPC $%.2f" % rolling_cpc})
    for cid_, d in mtd_per.items():
        if (d["lost_is_rank"] or 1) < 0.15 and (d["search_is"] or 0) > 0.85:
            alerts.append({"level": "INVESTIGATE", "type": "overpaying_for_position",
                           "detail": ("%s holds %.0f%% IS with only %.0f%% rank loss - "
                                      "paying for position it already owns"
                                      % (d["campaign"], (d["search_is"] or 0) * 100,
                                         (d["lost_is_rank"] or 0) * 100))})
    for t in terms:
        if t["cost"] >= SINGLE_CLICK_INVESTIGATE and t["verdict"] not in ("KEEP",):
            alerts.append({"level": "STOP", "type": "unqualified_expensive_click",
                           "detail": ("$%.2f on '%s' verdict=%s"
                                      % (t["cost"], t["search_term"], t["verdict"]))})

    # ---- final-day stop ----
    final_day_stop = None
    if today == "2026-08-31":
        final_day_stop = {
            "active": True,
            "remaining_before_target": R,
            "rule": ("If MTD reaches $2,450 at any checkpoint on 2026-08-31, request "
                     "immediate approval to reduce both budgets to $1.00/day for the "
                     "remainder of the day. DO NOT execute without that approval."),
        }

    rec = None
    if R <= 0:
        rec = "TARGET REACHED OR EXCEEDED - request approval to reduce budgets immediately."
    elif projected > TARGET * 1.02:
        rec = ("Projected $%.2f exceeds the $2,500 target. Request approval to REDUCE "
               "the combined budget toward $%.2f/day." % (projected, R / max(H / 24, 0.01)))
    elif projected < TARGET * 0.80:
        rec = ("Projected $%.2f is well short. The constraint is demand, not budget - "
               "raising budget further will inflate CPC, not volume. Escalate the "
               "PLAN-I4 service-area confirmation instead." % projected)
    else:
        rec = "On pace. No budget change recommended at this checkpoint."

    out = {
        "checkpoint": label, "timestamp_account_local": now.isoformat(),
        "mtd_spend": S, "today_spend": round(tod["cost"], 2),
        "remaining_budget": R, "remaining_hours": round(H, 2),
        "required_rolling_pace_per_24h": round(req_pace, 2),
        "actual_rolling_pace_per_24h": round(actual_pace, 2),
        "projected_month_end_spend": round(projected, 2),
        "mtd": mtd, "today": tod, "per_campaign_mtd": mtd_per,
        "budgets": budgets, "combined_daily_budget": round(comb_budget, 2),
        "clicks_mtd": len(clicks), "clicks_today": len(today_clicks),
        "rolling_avg_cpc": round(rolling_cpc, 2),
        "today_click_cpcs": [c["cpc"] for c in today_clicks],
        "leads_mtd": mtd["conversions"],
        "search_terms_today": terms,
        "qualified_terms_today": [t for t in terms if t["verdict"] == "KEEP"],
        "alerts": alerts,
        "final_day_stop": final_day_stop,
        "budget_adjustment_recommendation": rec,
        "reminder": "READ-ONLY. Every budget adjustment requires its own explicit approval.",
    }

    OUTDIR.mkdir(parents=True, exist_ok=True)
    f = OUTDIR / ("pacing-%s-%s.json" % (today, label.replace(":", "")))
    f.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("=" * 78)
    print("SOFTWIND PACING CHECKPOINT  %s  %s" % (label, now.isoformat()))
    print("=" * 78)
    print("  MTD spend                    $%.2f" % S)
    print("  Today's spend                $%.2f" % tod["cost"])
    print("  Remaining budget             $%.2f" % R)
    print("  Remaining hours              %.2f" % H)
    print("  Required rolling 24h pace    $%.2f" % req_pace)
    print("  Actual rolling 24h pace      $%.2f" % actual_pace)
    print("  Projected month-end spend    $%.2f" % projected)
    print("  Combined daily budget        $%.2f" % comb_budget)
    print("  Clicks MTD / today           %d / %d" % (len(clicks), len(today_clicks)))
    print("  Rolling average CPC          $%.2f" % rolling_cpc)
    print("  Leads MTD                    %.0f" % mtd["conversions"])
    print()
    print("  PER CAMPAIGN (MTD)")
    for cid_, d in mtd_per.items():
        f2 = lambda v: ("%.1f%%" % (v * 100)) if v is not None else "  -  "
        print("    %-18s $%8.2f  impr=%4d clk=%2d  IS=%s lostBud=%s lostRank=%s"
              % (d["campaign"][:18], d["cost"], d["impressions"], d["clicks"],
                 f2(d["search_is"]), f2(d["lost_is_budget"]), f2(d["lost_is_rank"])))
    print()
    print("  SEARCH TERMS TODAY (%d)" % len(terms))
    for t in terms[:12]:
        print("    $%7.2f impr=%2d clk=%d  %-40s [%s]"
              % (t["cost"], t["impressions"], t["clicks"],
                 t["search_term"][:40], t["verdict"]))
    if not terms:
        print("    none yet")
    print()
    if alerts:
        print("  *** EMERGENCY HIGH-CPC STOP CONDITION ***")
        for a in alerts:
            print("    [%s] %s: %s" % (a["level"], a["type"], a["detail"]))
    else:
        print("  Emergency high-CPC stop condition: no trigger")
    if final_day_stop:
        print()
        print("  FINAL-DAY STOP ACTIVE: %s" % final_day_stop["rule"])
    print()
    print("  RECOMMENDATION: %s" % rec)
    print()
    print("  READ-ONLY. No budget was changed. Any adjustment needs its own approval.")
    print("  written: %s" % f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
