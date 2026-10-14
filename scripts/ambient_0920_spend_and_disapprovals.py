#!/usr/bin/env python3
"""Ambient | 2026-09-20 | September pacing detail + disapproval detail + budget reachability.

READ-ONLY. EXTERNAL WRITES: 0.

Answers four things the budget plan depends on:
  1. September spend by day and by campaign, so "safe pace" rests on settled
     delivery rather than on nominal budgets.
  2. What the two DISAPPROVED Gas Boiler ads were disapproved for, because that
     campaign is about to receive a budget increase and a bid-ceiling raise.
  3. Whether each campaign is actually budget-limited, via impression share lost
     to budget. A budget cut is only cheap where nothing is being lost to budget.
  4. Heating-theme historical CPC from the legacy campaigns, split at the
     2026-09-04 16:56 boundary where CPC ceilings were introduced, because the
     uncapped Maximize Clicks regime before that inflates every average.
"""
from __future__ import annotations
import sys, json, datetime, calendar
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-20"
CAP_MONTH = 10000.00
CAP_DAY = 328.94
CEILING_REGIME_START = "2026-09-05"   # first full day under CPC ceilings


def main():
    c = client()
    identity_gate(c, verbose=False)
    now = datetime.datetime.now(TZ)
    first = now.replace(day=1).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")
    yest = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    dim = calendar.monthrange(now.year, now.month)[1]
    out = {"generated_local": now.isoformat(), "stamp": STAMP, "read_only": True,
           "external_writes": 0, "account_today": today}

    # ------------------------------------------------- 1. September by day
    print(f"=== 1. SEPTEMBER BY DAY ({first}..{today}) ===")
    byday, bycamp, tot = {}, {}, 0.0
    for r in q(c, f"""SELECT campaign.id, campaign.name, segments.date,
                      metrics.cost_micros, metrics.clicks, metrics.impressions,
                      metrics.conversions, metrics.all_conversions
                      FROM campaign
                      WHERE segments.date BETWEEN '{first}' AND '{today}'"""):
        d = r.segments.date
        v = r.metrics.cost_micros / 1e6
        tot += v
        a = byday.setdefault(d, {"cost": 0.0, "clicks": 0, "conv": 0.0})
        a["cost"] += v; a["clicks"] += r.metrics.clicks; a["conv"] += r.metrics.conversions
        b = bycamp.setdefault(r.campaign.name, {"id": str(r.campaign.id), "cost": 0.0,
                                                "clicks": 0, "impr": 0, "conv": 0.0,
                                                "all_conv": 0.0})
        b["cost"] += v; b["clicks"] += r.metrics.clicks; b["impr"] += r.metrics.impressions
        b["conv"] += r.metrics.conversions; b["all_conv"] += r.metrics.all_conversions
    for d in sorted(byday):
        a = byday[d]
        flag = "  <- PARTIAL (today)" if d == today else ""
        print(f"   {d}  ${a['cost']:8.2f}  {a['clicks']:4d} clicks  "
              f"{a['conv']:5.2f} conv{flag}")
    out["september_by_day"] = byday
    out["september_by_campaign"] = bycamp
    out["september_mtd_total"] = round(tot, 2)

    settled = {d: v for d, v in byday.items() if d < today}
    n_settled = len(settled)
    settled_cost = round(sum(v["cost"] for v in settled.values()), 2)
    avg_settled = round(settled_cost / n_settled, 2) if n_settled else 0.0
    last7 = sorted(settled)[-7:]
    avg7 = round(sum(settled[d]["cost"] for d in last7) / len(last7), 2) if last7 else 0.0

    print(f"\n   MTD total (incl. partial today) ${tot:,.2f}")
    print(f"   settled days {n_settled} ({sorted(settled)[0]}..{sorted(settled)[-1]}) "
          f"= ${settled_cost:,.2f}")
    print(f"   settled daily average          ${avg_settled:,.2f}")
    print(f"   last 7 settled daily average   ${avg7:,.2f}")

    days_left = dim - now.day + 1
    remaining = round(CAP_MONTH - tot, 2)
    reserve = round(remaining * 0.10, 2)
    safe_pace = round((remaining - reserve) / days_left, 2) if days_left else 0.0
    out["pace"] = {"days_in_month": dim, "days_left_incl_today": days_left,
                   "settled_days": n_settled, "settled_cost": settled_cost,
                   "settled_daily_avg": avg_settled, "last7_daily_avg": avg7,
                   "remaining_allowance": remaining, "reserve_10pct": reserve,
                   "max_safe_daily_pace": safe_pace,
                   "steady_state_daily_ceiling": round(CAP_MONTH / 30.4, 2)}
    print(f"\n   days left incl today {days_left}   remaining ${remaining:,.2f}   "
          f"reserve ${reserve:,.2f}")
    print(f"   MAX SAFE Sept daily pace ${safe_pace:,.2f}")
    print(f"   steady-state ceiling     ${CAP_MONTH/30.4:,.2f}/day")

    print("\n   September by campaign:")
    for n, v in sorted(bycamp.items(), key=lambda x: -x[1]["cost"]):
        if v["cost"] <= 0 and v["impr"] == 0:
            continue
        cpc = v["cost"] / v["clicks"] if v["clicks"] else 0
        print(f"      ${v['cost']:8.2f} {v['clicks']:4d}cl CPC ${cpc:7.2f} "
              f"conv {v['conv']:5.2f} allconv {v['all_conv']:5.2f}  {n[:50]}")

    # ------------------------------------------- 2. budget-limited check
    print("\n=== 2. IMPRESSION SHARE LOST TO BUDGET (settled September) ===")
    isr = {}
    if n_settled:
        lo, hi = sorted(settled)[0], sorted(settled)[-1]
        for r in q(c, f"""SELECT campaign.id, campaign.name, campaign.status,
                          metrics.search_impression_share,
                          metrics.search_budget_lost_impression_share,
                          metrics.search_rank_lost_impression_share,
                          metrics.cost_micros
                          FROM campaign
                          WHERE segments.date BETWEEN '{lo}' AND '{hi}'
                            AND campaign.status = 'ENABLED'"""):
            isr[r.campaign.name] = {
                "id": str(r.campaign.id),
                "is": round(r.metrics.search_impression_share * 100, 1),
                "lost_budget": round(r.metrics.search_budget_lost_impression_share * 100, 1),
                "lost_rank": round(r.metrics.search_rank_lost_impression_share * 100, 1),
                "cost": round(r.metrics.cost_micros / 1e6, 2)}
        for n, v in sorted(isr.items(), key=lambda x: -x[1]["lost_budget"]):
            print(f"      IS {v['is']:5.1f}%  lostBUDGET {v['lost_budget']:5.1f}%  "
                  f"lostRANK {v['lost_rank']:5.1f}%  ${v['cost']:8.2f}  {n[:46]}")
    out["impression_share_settled_september"] = isr

    # --------------------------------------------- 3. disapproval detail
    print("\n=== 3. DISAPPROVED ADS - detail ===")
    dis = {}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                     ad_group.id, ad_group.name, ad_group_ad.ad.id,
                     ad_group_ad.status,
                     ad_group_ad.policy_summary.approval_status,
                     ad_group_ad.policy_summary.policy_topic_entries,
                     ad_group_ad.ad.final_urls
                     FROM ad_group_ad
                     WHERE ad_group_ad.policy_summary.approval_status = 'DISAPPROVED'
                       AND ad_group_ad.status != 'REMOVED'"""):
        topics = [{"topic": e.topic, "type": E(e.type_)}
                  for e in r.ad_group_ad.policy_summary.policy_topic_entries]
        dis[str(r.ad_group_ad.ad.id)] = {
            "campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
            "campaign_status": E(r.campaign.status),
            "ad_group": r.ad_group.name, "ad_status": E(r.ad_group_ad.status),
            "final_urls": list(r.ad_group_ad.ad.final_urls), "topics": topics}
    out["disapproved_ads"] = dis
    print(f"   {len(dis)} disapproved non-removed ads")
    agg = {}
    for v in dis.values():
        for t in v["topics"]:
            agg[t["topic"]] = agg.get(t["topic"], 0) + 1
    print(f"   topic rollup: {agg}")
    out["disapproval_topic_rollup"] = agg
    for k, v in dis.items():
        if v["campaign_id"] in ("24132507744", "24257819463", "24257819466"):
            print(f"      ad {k} {v['ad_status']:8s} {v['ad_group'][:30]:30s} "
                  f"{[t['topic'] for t in v['topics']]}  {v['final_urls']}")

    # ------------------------- 4. heating CPC by regime from legacy campaigns
    print("\n=== 4. LEGACY HEATING CPC, SPLIT AT THE CEILING BOUNDARY ===")
    heat_terms = ("furnace", "boiler", "heat pump", "heatpump", "mini split", "minisplit",
                  "geothermal", "tankless", "oil heat", "oil furnace", "heating")
    reg = {}
    for tag, lo, hi in (("pre_ceiling_all_history", "2019-01-01", "2026-09-04"),
                        ("post_ceiling", CEILING_REGIME_START, today)):
        acc = {}
        for r in q(c, f"""SELECT campaign.id, campaign.name, ad_group.name,
                          metrics.cost_micros, metrics.clicks, metrics.conversions,
                          metrics.impressions
                          FROM ad_group
                          WHERE segments.date BETWEEN '{lo}' AND '{hi}'"""):
            nm = (r.campaign.name + " " + r.ad_group.name).lower()
            hit = next((t for t in heat_terms if t in nm), None)
            if not hit:
                continue
            a = acc.setdefault(hit, {"cost": 0.0, "clicks": 0, "conv": 0.0, "impr": 0})
            a["cost"] += r.metrics.cost_micros / 1e6
            a["clicks"] += r.metrics.clicks
            a["conv"] += r.metrics.conversions
            a["impr"] += r.metrics.impressions
        for k, a in acc.items():
            a["cpc"] = round(a["cost"] / a["clicks"], 2) if a["clicks"] else None
            a["cpa"] = round(a["cost"] / a["conv"], 2) if a["conv"] else None
            a["cost"] = round(a["cost"], 2)
        reg[tag] = acc
        print(f"   --- {tag} ({lo}..{hi}) ---")
        for k, a in sorted(acc.items(), key=lambda x: -x[1]["cost"]):
            print(f"      {k:14s} ${a['cost']:9.2f} {a['clicks']:5d}cl "
                  f"CPC ${str(a['cpc']):>8s}  conv {a['conv']:6.2f} CPA ${str(a['cpa']):>9s}")
    out["heating_cpc_by_regime"] = reg

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"spend-disapprovals-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
