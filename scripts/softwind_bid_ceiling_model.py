#!/usr/bin/env python3
"""Fresh evidence for choosing a Max CPC ceiling. Read-only.

The $5.00 ceiling that ran 2026-08-07 -> 2026-08-16 produced twelve consecutive
zero-click days, so the cost of setting this too low is proven and severe. This
script isolates the post-cap-removal auction window (2026-08-17 onward) and pulls
Keyword Planner top-of-page estimates for exactly the live keyword texts.
"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
TZ = ZoneInfo("America/New_York")
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "bid-ceiling-model-2026-08-25.json"

GEOS = ["1022729", "1023035", "1023415", "1023482",
        "9051836", "9052792", "9198508", "9214462"]

LIVE_KEYWORDS = [
    "power washing near me", "power washing services near me",
    "power washing company near me", "power washing islip",
    "power washing west islip", "power washing dix hills",
    "residential pressure washing near me", "house pressure washing estimate",
    "driveway pressure washing near me", "patio pressure washing near me",
    "soft house washing near me",
    # the paused SKAG proposed for enablement
    "house washing company near me",
]


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    end = datetime.now(TZ).date().isoformat()
    out = {"generated_account_local": datetime.now(TZ).isoformat()}

    # ---- auction state in the post-cap window only ----
    windows = {
        "all_time_2026-08-05_to_now": ("2026-08-05", end),
        "cap_5usd_in_force_2026-08-07_to_2026-08-16": ("2026-08-07", "2026-08-16"),
        "post_cap_removal_2026-08-17_to_now": ("2026-08-17", end),
    }
    out["auction_windows"] = {}
    for label, (lo, hi) in windows.items():
        rows = []
        for r in svc.search(customer_id=CID, query="""
            SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks,
                   metrics.cost_micros, metrics.ctr, metrics.average_cpc,
                   metrics.search_impression_share,
                   metrics.search_budget_lost_impression_share,
                   metrics.search_rank_lost_impression_share,
                   metrics.search_top_impression_share,
                   metrics.search_absolute_top_impression_share,
                   metrics.top_impression_percentage,
                   metrics.absolute_top_impression_percentage
            FROM campaign WHERE segments.date BETWEEN '%s' AND '%s'""" % (lo, hi)):
            m = r.metrics
            rows.append({
                "campaign": r.campaign.name, "campaign_id": str(r.campaign.id),
                "impressions": int(m.impressions), "clicks": int(m.clicks),
                "cost": round(m.cost_micros / 1_000_000, 2),
                "ctr": round(float(m.ctr), 4),
                "avg_cpc": round(m.average_cpc / 1_000_000, 2) if m.average_cpc else 0.0,
                "search_is": float(m.search_impression_share) or None,
                "lost_is_budget": float(m.search_budget_lost_impression_share) or None,
                "lost_is_rank": float(m.search_rank_lost_impression_share) or None,
                "search_top_is": float(m.search_top_impression_share) or None,
                "search_abs_top_is": float(
                    m.search_absolute_top_impression_share) or None,
                "top_pct": float(m.top_impression_percentage) or None,
                "abs_top_pct": float(m.absolute_top_impression_percentage) or None})
        out["auction_windows"][label] = {"start": lo, "end": hi, "campaigns": rows}

    # ---- every charged click ----
    clicks = []
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.name, ad_group.name, segments.date,
               ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
               metrics.clicks, metrics.cost_micros
        FROM keyword_view WHERE segments.date BETWEEN '2026-08-01' AND '%s'
          AND metrics.clicks > 0""" % end):
        n = int(r.metrics.clicks)
        cpc = (r.metrics.cost_micros / 1_000_000) / n
        for _ in range(n):
            clicks.append({"date": r.segments.date, "campaign": r.campaign.name,
                           "ad_group": r.ad_group.name,
                           "keyword": r.ad_group_criterion.keyword.text,
                           "match_type": enum_name(
                               r.ad_group_criterion.keyword.match_type),
                           "cpc": round(cpc, 2)})
    clicks.sort(key=lambda x: x["cpc"])
    cpcs = [c["cpc"] for c in clicks]
    out["charged_clicks"] = clicks
    out["cpc_distribution"] = {
        "n": len(cpcs), "min": min(cpcs), "max": max(cpcs),
        "median": statistics.median(cpcs),
        "mean": round(sum(cpcs) / len(cpcs), 2),
        "all_values": cpcs,
    }

    # ---- Planner top-of-page for exactly the live keyword texts ----
    kp = client.get_service("KeywordPlanIdeaService")
    req = client.get_type("GenerateKeywordIdeasRequest")
    req.customer_id = CID
    req.language = "languageConstants/1000"
    req.geo_target_constants.extend("geoTargetConstants/%s" % g for g in GEOS)
    req.include_adult_keywords = False
    req.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
    req.keyword_seed.keywords.extend(LIVE_KEYWORDS[:20])
    wanted = {k.lower() for k in LIVE_KEYWORDS}
    found = {}
    try:
        for r in kp.generate_keyword_ideas(request=req):
            if r.text.lower() in wanted:
                m = r.keyword_idea_metrics
                found[r.text.lower()] = {
                    "keyword": r.text,
                    "avg_monthly_searches": int(m.avg_monthly_searches),
                    "competition": enum_name(m.competition),
                    "low_top_of_page_bid": (m.low_top_of_page_bid_micros / 1_000_000
                                            if m.low_top_of_page_bid_micros else None),
                    "high_top_of_page_bid": (m.high_top_of_page_bid_micros / 1_000_000
                                             if m.high_top_of_page_bid_micros else None)}
    except Exception as exc:
        out["planner_error"] = str(exc)[:300]
    out["planner_live_keywords"] = found
    highs = [v["high_top_of_page_bid"] for v in found.values()
             if v["high_top_of_page_bid"]]
    lows = [v["low_top_of_page_bid"] for v in found.values()
            if v["low_top_of_page_bid"]]
    out["planner_live_keyword_summary"] = {
        "matched": len(found),
        "low_min": min(lows) if lows else None,
        "low_max": max(lows) if lows else None,
        "high_min": min(highs) if highs else None,
        "high_max": max(highs) if highs else None,
        "high_median": round(statistics.median(highs), 2) if highs else None,
    }

    # ---- ceiling scenarios against the observed click set ----
    scen = []
    for ceiling in [18.0, 20.0, 22.0, 24.0, 26.0, None]:
        if ceiling is None:
            scen.append({"ceiling": "uncapped", "clicks_priced_at_or_below": len(cpcs),
                         "clicks_above_ceiling": 0, "capped_spend_on_same_clicks":
                             round(sum(cpcs), 2),
                         "saving_vs_actual": 0.0,
                         "planner_high_coverage_pct": 100.0})
            continue
        below = [c for c in cpcs if c <= ceiling]
        above = [c for c in cpcs if c > ceiling]
        # Upper bound on spend if every click were still won at exactly the ceiling.
        capped = sum(below) + ceiling * len(above)
        cov = (100.0 * sum(1 for h in highs if h <= ceiling) / len(highs)) if highs else None
        scen.append({
            "ceiling": ceiling,
            "clicks_priced_at_or_below": len(below),
            "clicks_above_ceiling": len(above),
            "clicks_above_ceiling_values": above,
            "capped_spend_on_same_clicks": round(capped, 2),
            "saving_vs_actual": round(sum(cpcs) - capped, 2),
            "planner_high_coverage_pct": round(cov, 1) if cov is not None else None,
        })
    out["ceiling_scenarios"] = scen
    out["actual_spend_on_those_clicks"] = round(sum(cpcs), 2)

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("AUCTION STATE BY WINDOW")
    for label, w in out["auction_windows"].items():
        print("  %s  (%s .. %s)" % (label, w["start"], w["end"]))
        for r in w["campaigns"]:
            f = lambda v: ("%.1f%%" % (v * 100)) if v is not None else "   -  "
            print("    %-18s impr=%4d clk=%d $%7.2f CPC=$%6.2f IS=%s lostBud=%s "
                  "lostRank=%s top=%s absTop=%s"
                  % (r["campaign"][:18], r["impressions"], r["clicks"], r["cost"],
                     r["avg_cpc"], f(r["search_is"]), f(r["lost_is_budget"]),
                     f(r["lost_is_rank"]), f(r["top_pct"]), f(r["abs_top_pct"])))
    print()
    print("CPC DISTRIBUTION: %s" % out["cpc_distribution"])
    print()
    print("PLANNER TOP-OF-PAGE, LIVE KEYWORDS ONLY")
    for k, v in sorted(found.items(), key=lambda x: -(x[1]["high_top_of_page_bid"] or 0)):
        print("    %-38s vol=%-5s comp=%-7s low=%-7s high=%s"
              % (v["keyword"], v["avg_monthly_searches"], v["competition"],
                 ("$%.2f" % v["low_top_of_page_bid"]) if v["low_top_of_page_bid"] else "-",
                 ("$%.2f" % v["high_top_of_page_bid"]) if v["high_top_of_page_bid"] else "-"))
    print("  summary: %s" % out["planner_live_keyword_summary"])
    print()
    print("CEILING SCENARIOS (against the 6 charged clicks)")
    for s in scen:
        print("    ceiling=%-9s at_or_below=%d above=%d upper_bound_spend=$%s "
              "saving=$%s planner_high_covered=%s%%"
              % (s["ceiling"], s["clicks_priced_at_or_below"],
                 s["clicks_above_ceiling"], s["capped_spend_on_same_clicks"],
                 s["saving_vs_actual"], s["planner_high_coverage_pct"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
