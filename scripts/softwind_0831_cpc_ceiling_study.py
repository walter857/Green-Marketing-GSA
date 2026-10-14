#!/usr/bin/env python3
"""CPC ceiling study for Softwind Power Washing - is $10 defensible?

Fresh read-only state, valid-click CPC distribution sliced every way the brief
asks, and the three historical bidding regimes verified rather than quoted.

SELECT statements only. Constructs no operation, calls no mutate service.
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
LO, HI = "2026-07-01", "2026-08-31"

# Regime boundaries, from change_event (account-local).
#   $5.00 ceiling set 2026-08-07 16:08:18, removed 2026-08-16 23:42:44
#   $30.00 ceiling set 2026-08-27 12:25:35 on both campaigns
REGIMES = [
    ("pre-$5 ceiling      (08-05 .. 08-07)", "2026-08-05", "2026-08-07"),
    ("$5.00 ceiling ACTIVE (08-08 .. 08-16)", "2026-08-08", "2026-08-16"),
    ("UNCAPPED            (08-17 .. 08-27)", "2026-08-17", "2026-08-27"),
    ("$30.00 ceiling      (08-28 .. 08-31)", "2026-08-28", "2026-08-31"),
]


def mic(v) -> float:
    return round(int(v) / 1_000_000, 4)


def pctile(sorted_vals, q):
    if not sorted_vals:
        return None
    import math
    n = len(sorted_vals)
    return sorted_vals[min(n - 1, max(0, math.ceil(q * n) - 1))]


def describe(vals, label):
    if not vals:
        return {"label": label, "n": 0}
    v = sorted(vals)
    return {
        "label": label, "n": len(v),
        "min": round(v[0], 2), "p25": round(pctile(v, .25), 2),
        "median": round(statistics.median(v), 2),
        "mean": round(sum(v) / len(v), 2),
        "p75": round(pctile(v, .75), 2), "p90": round(pctile(v, .90), 2),
        "max": round(v[-1], 2),
    }


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    now = datetime.now(ZoneInfo("America/New_York"))

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    out = {"generated_account_local": now.isoformat(), "mode": "READ-ONLY"}

    # ---------- 1. current campaign state, ceiling VERIFIED not assumed ----------
    rows = q("""SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
                       campaign.primary_status, campaign.bidding_strategy_type,
                       campaign.bidding_strategy_system_status,
                       campaign.target_spend.cpc_bid_ceiling_micros,
                       campaign.campaign_budget,
                       campaign.network_settings.target_search_network,
                       campaign.network_settings.target_content_network,
                       campaign.geo_target_type_setting.positive_geo_target_type,
                       metrics.impressions, metrics.clicks, metrics.cost_micros,
                       metrics.average_cpc, metrics.ctr,
                       metrics.search_impression_share,
                       metrics.search_rank_lost_impression_share,
                       metrics.search_budget_lost_impression_share,
                       metrics.search_top_impression_share,
                       metrics.search_absolute_top_impression_share
                FROM campaign WHERE campaign.status != 'REMOVED'""")
    budgets = {str(r.campaign_budget.id): mic(r.campaign_budget.amount_micros)
               for r in q("""SELECT campaign_budget.id, campaign_budget.amount_micros
                             FROM campaign_budget
                             WHERE campaign_budget.status != 'REMOVED'""")}
    camps = []
    for r in rows:
        c, m = r.campaign, r.metrics
        bid = c.campaign_budget.split("/")[-1]
        locs = q(f"""SELECT campaign_criterion.criterion_id, campaign_criterion.negative
                     FROM campaign_criterion
                     WHERE campaign.id = {c.id}
                       AND campaign_criterion.type = 'LOCATION'
                       AND campaign_criterion.status != 'REMOVED'""")
        camps.append({
            "campaign_id": str(c.id), "name": c.name, "status": enum_name(c.status),
            "serving_status": enum_name(c.serving_status),
            "primary_status": enum_name(c.primary_status),
            "bidding_strategy": enum_name(c.bidding_strategy_type),
            "bidding_system_status": enum_name(c.bidding_strategy_system_status),
            "cpc_bid_ceiling_micros": int(c.target_spend.cpc_bid_ceiling_micros),
            "cpc_bid_ceiling_usd": mic(c.target_spend.cpc_bid_ceiling_micros),
            "budget_id": bid, "daily_budget_usd": budgets.get(bid),
            "locations_targeted": sum(1 for x in locs if not x.campaign_criterion.negative),
            "locations_excluded": sum(1 for x in locs if x.campaign_criterion.negative),
            "location_option": enum_name(c.geo_target_type_setting.positive_geo_target_type),
            "search_partners": bool(c.network_settings.target_search_network),
            "display_network": bool(c.network_settings.target_content_network),
            "impressions": int(m.impressions), "clicks": int(m.clicks),
            "cost_usd": mic(m.cost_micros), "avg_cpc_usd": mic(m.average_cpc),
            "ctr_pct": round(float(m.ctr) * 100, 2),
            "search_is_pct": round(float(m.search_impression_share) * 100, 2),
            "lost_is_rank_pct": round(float(m.search_rank_lost_impression_share) * 100, 2),
            "lost_is_budget_pct": round(float(m.search_budget_lost_impression_share) * 100, 2),
            "top_is_pct": round(float(m.search_top_impression_share) * 100, 2),
            "abs_top_is_pct": round(float(m.search_absolute_top_impression_share) * 100, 2),
        })
    out["campaigns"] = camps

    # ---------- 2. valid billable clicks, every slice ----------
    def click_vals(resource, dims, extra_where=""):
        sel = ", ".join(dims)
        rows = q(f"""SELECT {sel}, segments.date, metrics.clicks, metrics.cost_micros,
                            metrics.average_cpc, metrics.impressions
                     FROM {resource}
                     WHERE segments.date BETWEEN '{LO}' AND '{HI}'{extra_where}""")
        return rows

    all_clicks = []          # every valid billable click as a CPC value
    ledger = []
    for r in click_vals("keyword_view",
                        ["campaign.id", "campaign.name", "ad_group.id", "ad_group.name",
                         "ad_group_criterion.keyword.text",
                         "ad_group_criterion.keyword.match_type"]):
        if r.metrics.clicks:
            cpc = mic(r.metrics.average_cpc)
            n = int(r.metrics.clicks)
            all_clicks += [cpc] * n
            ledger.append({
                "date": r.segments.date, "campaign_id": str(r.campaign.id),
                "campaign": r.campaign.name, "ad_group": r.ad_group.name,
                "keyword": r.ad_group_criterion.keyword.text,
                "match_type": enum_name(r.ad_group_criterion.keyword.match_type),
                "clicks": n, "cost_usd": mic(r.metrics.cost_micros), "cpc_usd": cpc,
            })
    ledger.sort(key=lambda x: x["date"])
    out["valid_click_ledger"] = ledger
    out["cpc_distribution_all"] = describe(all_clicks, "all valid billable clicks")

    def slice_by(resource, dims, keyfn, label):
        agg = defaultdict(lambda: {"clicks": 0, "cost": 0.0, "impr": 0})
        for r in click_vals(resource, dims):
            k = keyfn(r)
            a = agg[k]
            a["clicks"] += int(r.metrics.clicks)
            a["cost"] += mic(r.metrics.cost_micros)
            a["impr"] += int(r.metrics.impressions)
        res = []
        for k, v in agg.items():
            if v["clicks"]:
                res.append({"key": k, "clicks": v["clicks"], "impressions": v["impr"],
                            "cost_usd": round(v["cost"], 2),
                            "avg_cpc_usd": round(v["cost"] / v["clicks"], 2)})
        res.sort(key=lambda x: -x["cost_usd"])
        out[label] = res

    slice_by("campaign", ["campaign.id", "campaign.name"],
             lambda r: f"{r.campaign.name} ({r.campaign.id})", "cpc_by_campaign")
    slice_by("ad_group", ["campaign.name", "ad_group.id", "ad_group.name"],
             lambda r: f"{r.campaign.name} / {r.ad_group.name}", "cpc_by_ad_group")
    slice_by("keyword_view",
             ["ad_group_criterion.keyword.text", "ad_group_criterion.keyword.match_type"],
             lambda r: f"{r.ad_group_criterion.keyword.text} "
                       f"[{enum_name(r.ad_group_criterion.keyword.match_type)}]",
             "cpc_by_keyword")
    slice_by("search_term_view", ["search_term_view.search_term"],
             lambda r: r.search_term_view.search_term, "cpc_by_search_term")
    slice_by("campaign", ["campaign.id", "segments.device"],
             lambda r: enum_name(r.segments.device), "cpc_by_device")

    # hour needs its own query shape (no segments.date range issue)
    agg = defaultdict(lambda: {"clicks": 0, "cost": 0.0, "impr": 0})
    for r in q(f"""SELECT segments.hour, metrics.clicks, metrics.cost_micros,
                          metrics.impressions FROM campaign
                   WHERE segments.date BETWEEN '{LO}' AND '{HI}'"""):
        a = agg[int(r.segments.hour)]
        a["clicks"] += int(r.metrics.clicks)
        a["cost"] += mic(r.metrics.cost_micros)
        a["impr"] += int(r.metrics.impressions)
    out["cpc_by_hour"] = [
        {"hour": f"{h:02d}:00", "impressions": v["impr"], "clicks": v["clicks"],
         "cost_usd": round(v["cost"], 2),
         "avg_cpc_usd": round(v["cost"] / v["clicks"], 2) if v["clicks"] else None}
        for h, v in sorted(agg.items())]

    # ---------- 3. the three historical bidding regimes, VERIFIED ----------
    daily = {}
    for r in q(f"""SELECT segments.date, metrics.impressions, metrics.clicks,
                          metrics.cost_micros, metrics.invalid_clicks,
                          metrics.average_cpc FROM customer
                   WHERE segments.date BETWEEN '{LO}' AND '{HI}'"""):
        daily[r.segments.date] = {
            "impr": int(r.metrics.impressions), "clicks": int(r.metrics.clicks),
            "cost": mic(r.metrics.cost_micros), "invalid": int(r.metrics.invalid_clicks)}
    # impression-weighted position proxies per day
    pos = defaultdict(lambda: {"w": 0, "top": 0.0, "abs": 0.0, "lr": 0.0, "is": 0.0})
    for r in q(f"""SELECT segments.date, metrics.impressions,
                          metrics.search_top_impression_share,
                          metrics.search_absolute_top_impression_share,
                          metrics.search_rank_lost_impression_share,
                          metrics.search_impression_share FROM campaign
                   WHERE segments.date BETWEEN '{LO}' AND '{HI}'"""):
        if r.metrics.impressions:
            p = pos[r.segments.date]
            w = int(r.metrics.impressions)
            p["w"] += w
            p["top"] += float(r.metrics.search_top_impression_share) * 100 * w
            p["abs"] += float(r.metrics.search_absolute_top_impression_share) * 100 * w
            p["lr"] += float(r.metrics.search_rank_lost_impression_share) * 100 * w
            p["is"] += float(r.metrics.search_impression_share) * 100 * w

    regimes = []
    for label, lo, hi in REGIMES:
        days = [d for d in daily if lo <= d <= hi]
        i = sum(daily[d]["impr"] for d in days)
        c = sum(daily[d]["clicks"] for d in days)
        k = sum(daily[d]["cost"] for d in days)
        iv = sum(daily[d]["invalid"] for d in days)
        pw = sum(pos[d]["w"] for d in days if d in pos)
        cps = [x["cpc_usd"] for x in ledger if lo <= x["date"] <= hi
               for _ in range(x["clicks"])]
        regimes.append({
            "regime": label, "days_in_window": len(days),
            "calendar_days": (datetime.fromisoformat(hi) - datetime.fromisoformat(lo)).days + 1,
            "impressions": i, "valid_clicks": c, "invalid_clicks": iv,
            "cost_usd": round(k, 2),
            "avg_cpc_usd": round(k / c, 2) if c else None,
            "ctr_pct": round(100 * c / i, 2) if i else 0.0,
            "impr_per_serving_day": round(i / len(days), 1) if days else 0,
            "top_is_pct": round(sum(pos[d]["top"] for d in days if d in pos) / pw, 2) if pw else None,
            "abs_top_is_pct": round(sum(pos[d]["abs"] for d in days if d in pos) / pw, 2) if pw else None,
            "lost_is_rank_pct": round(sum(pos[d]["lr"] for d in days if d in pos) / pw, 2) if pw else None,
            "search_is_pct": round(sum(pos[d]["is"] for d in days if d in pos) / pw, 2) if pw else None,
            "cpc_distribution": describe(cps, label),
        })
    out["bidding_regimes"] = regimes

    # ---------- 4. auction-clearing model ----------
    # Under Maximize Clicks the price paid approximates the minimum needed to beat the
    # next competitor. A ceiling C therefore CANNOT have won an auction that cleared
    # above C at that position. This bounds coverage from the observed ledger.
    ceilings = [8, 10, 12, 15, 18, 22, 30]
    model = []
    n = len(all_clicks)
    for c in ceilings:
        winnable = [x for x in all_clicks if x <= c]
        model.append({
            "ceiling_usd": c,
            "observed_clicks_that_cleared_at_or_below": len(winnable),
            "share_of_observed_clicks_pct": round(100 * len(winnable) / n, 1),
            "spend_on_those_clicks_usd": round(sum(winnable), 2),
            "naive_capped_spend_usd": round(sum(min(x, c) for x in all_clicks), 2),
            "naive_capped_avg_cpc_usd": round(sum(min(x, c) for x in all_clicks) / n, 2),
        })
    out["auction_clearing_model"] = {
        "method": (
            "Under Maximize Clicks the CPC paid approximates the minimum required to "
            "outrank the next competitor at that position. A ceiling C cannot win an "
            "auction whose clearing price exceeded C at the same position, so the count "
            "of observed clicks priced at or below C is an UPPER BOUND on how many of "
            "those exact auctions a ceiling of C would still have won at that position. "
            "It is not a forecast: a lower bid can still win a LOWER position at a lower "
            "price, which the naive capped-spend column assumes and the clearing column "
            "does not. The truth sits between the two columns."),
        "total_valid_clicks": n,
        "rows": model,
    }

    stamp = now.strftime("%Y-%m-%dT%H%M%S")
    p = SNAP / f"cpc-ceiling-study-{stamp}.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # ---------- console ----------
    print("=== 1. CURRENT CAMPAIGN STATE (ceiling verified, not assumed) ===")
    for c in camps:
        print(f"\n  {c['name']} ({c['campaign_id']}) {c['status']}/{c['serving_status']} "
              f"primary={c['primary_status']}")
        print(f"    bidding={c['bidding_strategy']} sys={c['bidding_system_status']}")
        print(f"    CPC CEILING = ${c['cpc_bid_ceiling_usd']}  "
              f"(raw micros {c['cpc_bid_ceiling_micros']})")
        print(f"    daily budget=${c['daily_budget_usd']} (budget {c['budget_id']})")
        print(f"    locations={c['locations_targeted']} targeted / "
              f"{c['locations_excluded']} excluded, option={c['location_option']}")
        print(f"    search_partners={c['search_partners']} display={c['display_network']}")
        print(f"    impr={c['impressions']} clicks={c['clicks']} cost=${c['cost_usd']} "
              f"avgCPC=${c['avg_cpc_usd']} ctr={c['ctr_pct']}%")
        print(f"    IS={c['search_is_pct']}% lostRank={c['lost_is_rank_pct']}% "
              f"lostBudget={c['lost_is_budget_pct']}% top={c['top_is_pct']}% "
              f"absTop={c['abs_top_is_pct']}%")

    d = out["cpc_distribution_all"]
    print(f"\n=== 2. VALID BILLABLE CPC DISTRIBUTION (n={d['n']}) ===")
    print(f"  min=${d['min']} p25=${d['p25']} median=${d['median']} mean=${d['mean']} "
          f"p75=${d['p75']} p90=${d['p90']} max=${d['max']}")
    print(f"  all: {sorted(round(x,2) for x in all_clicks)}")

    print("\n=== 3. BIDDING REGIMES (verified from the account) ===")
    for r in regimes:
        print(f"\n  {r['regime']}")
        print(f"    serving days with data={r['days_in_window']} of {r['calendar_days']} calendar days")
        print(f"    impressions={r['impressions']} ({r['impr_per_serving_day']}/day) "
              f"valid_clicks={r['valid_clicks']} invalid={r['invalid_clicks']} "
              f"cost=${r['cost_usd']} ctr={r['ctr_pct']}%")
        print(f"    avgCPC={('$' + str(r['avg_cpc_usd'])) if r['avg_cpc_usd'] else 'n/a'}  "
              f"IS={r['search_is_pct']}% lostRank={r['lost_is_rank_pct']}% "
              f"top={r['top_is_pct']}% absTop={r['abs_top_is_pct']}%")
        cd = r["cpc_distribution"]
        if cd["n"]:
            print(f"    CPCs: min=${cd['min']} median=${cd['median']} max=${cd['max']}")

    print("\n=== 4. AUCTION-CLEARING MODEL ===")
    print(f"  {'ceiling':>8s} {'clicks<=C':>10s} {'share':>7s} {'spend on those':>15s} "
          f"{'naive capped spend':>19s} {'naive avgCPC':>13s}")
    for m in model:
        print(f"  ${m['ceiling_usd']:>7} {m['observed_clicks_that_cleared_at_or_below']:>10} "
              f"{m['share_of_observed_clicks_pct']:>6}% "
              f"${m['spend_on_those_clicks_usd']:>14} ${m['naive_capped_spend_usd']:>18} "
              f"${m['naive_capped_avg_cpc_usd']:>12}")

    print("\n=== 5. CPC BY SLICE ===")
    for lab in ("cpc_by_campaign", "cpc_by_ad_group", "cpc_by_keyword",
                "cpc_by_search_term", "cpc_by_device"):
        print(f"\n  -- {lab} --")
        for row in out[lab]:
            print(f"    {str(row['key'])[:52]:52s} impr={row['impressions']:4d} "
                  f"clicks={row['clicks']:3d} ${row['cost_usd']:8.2f} "
                  f"avgCPC=${row['avg_cpc_usd']:6.2f}")
    print("\n  -- cpc_by_hour --")
    for row in out["cpc_by_hour"]:
        cp = f"${row['avg_cpc_usd']:.2f}" if row["avg_cpc_usd"] else "-"
        print(f"    {row['hour']} impr={row['impressions']:4d} clicks={row['clicks']:3d} "
              f"${row['cost_usd']:8.2f} avgCPC={cp}")

    print(f"\nWROTE {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
