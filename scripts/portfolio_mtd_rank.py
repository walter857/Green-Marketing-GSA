#!/usr/bin/env python3
"""Rank every level worst -> best from the MTD bundles. Read-only, local files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "portfolio-mtd-2026-08"


def load():
    return [json.loads(p.read_text()) for p in sorted(OUT.glob("*.json"))]


def norm(row):
    """Normalize one entity row into the common shape."""
    cost = row.get("cost_micros", 0) / 1e6
    conv = row.get("conversions", 0.0)
    return {
        "cost": cost,
        "conv": conv,
        "impr": row.get("impressions", 0),
        "clicks": row.get("clicks", 0),
        "ctr": row.get("ctr", 0.0) * 100,
        "cvr": row.get("conversions_from_interactions_rate", 0.0) * 100,
        "cpa": (cost / conv) if conv else None,
        "abs_top": row.get("absolute_top_impression_percentage", 0.0) * 100,
        "abs_top_is": pct(row.get("search_absolute_top_impression_share")),
        "lost_abs_rank": pct(row.get("search_rank_lost_absolute_top_impression_share")),
        "lost_abs_budget": pct(row.get("search_budget_lost_absolute_top_impression_share")),
        "is": pct(row.get("search_impression_share")),
    }


def pct(v):
    return None if v is None else v * 100


def rank_key(e):
    """Tier 1 = spend with zero conversions (worst, biggest waste first).
       Tier 2 = has conversions, worst CPA first.  Tier 3 = no spend."""
    if e["cost"] > 0 and e["conv"] == 0:
        return (0, -e["cost"])
    if e["conv"] > 0:
        return (1, -(e["cpa"] or 0))
    return (2, 0)


def fmt(v, kind="n"):
    if v is None:
        return "  --"
    if kind == "p":
        return f"{v:5.1f}%"
    if kind == "m":
        return f"${v:,.2f}"
    return f"{v:,.1f}"


def line(e, label, width=58):
    return (f"{label[:width]:<{width}} {fmt(e['cost'],'m'):>10} {e['conv']:5.1f} "
            f"{fmt(e['cpa'],'m'):>10} {fmt(e['ctr'],'p')} {fmt(e['cvr'],'p')} "
            f"{fmt(e['abs_top'],'p')} {fmt(e['lost_abs_rank'],'p')} {fmt(e['lost_abs_budget'],'p')}")


HDR = (f"{'ENTITY':<58} {'COST':>10} {'CONV':>5} {'CPA':>10} {'CTR':>6} "
       f"{'CVR':>6} {'ABSTOP':>6} {'LOSTrnk':>6} {'LOSTbdg':>6}")


def main():
    bundles = load()

    # ================= ACCOUNT =================
    accts = []
    for b in bundles:
        t = b.get("account_total")
        if not t:
            t = {}
        e = norm(t)
        e["label"] = b["account"]["name"]
        e["cid"] = b["account"]["customer_id"]
        accts.append(e)
    accts.sort(key=rank_key)

    tot_cost = sum(a["cost"] for a in accts)
    tot_conv = sum(a["conv"] for a in accts)
    print("=" * 130)
    print(f"PORTFOLIO MTD  spend=${tot_cost:,.2f}  conv={tot_conv:.1f}  "
          f"blended CPA=${tot_cost/tot_conv if tot_conv else 0:,.2f}")
    print("=" * 130)
    print("\n### ACCOUNT LEVEL (worst -> best)")
    print(HDR)
    for a in accts:
        print(line(a, f"{a['label']} [{a['cid']}]"))

    # ================= CAMPAIGN =================
    print("\n\n### CAMPAIGN LEVEL (worst -> best, all accounts pooled)")
    camps = []
    for b in bundles:
        for c in b["campaigns"]:
            e = norm(c)
            e["label"] = f"{b['account']['name'].replace(' - Live','')} | {c['campaign']}"
            e["acct"] = b["account"]["name"]
            e["status"] = c["status"]
            e["channel"] = c["channel"]
            e["budget"] = c["daily_budget"]
            camps.append(e)
    camps.sort(key=rank_key)
    print(HDR)
    for c in camps:
        if c["cost"] > 0:
            print(line(c, c["label"]))
    zero = [c for c in camps if c["cost"] == 0]
    print(f"\n[{len(zero)} campaigns with $0 MTD spend: "
          + ", ".join(sorted({c['label'] for c in zero}))[:600] + "]")

    # ================= AD GROUP =================
    print("\n\n### AD GROUP LEVEL - worst 30 (spend, zero conv first)")
    ags = []
    for b in bundles:
        for g in b["ad_groups"]:
            e = norm(g)
            e["label"] = f"{b['account']['name'].replace(' - Live','')} | {g['campaign'][:22]} | {g['ad_group']}"
            ags.append(e)
    ags.sort(key=rank_key)
    print(HDR)
    for g in ags[:30]:
        if g["cost"] > 0:
            print(line(g, g["label"]))
    spend_ags = [g for g in ags if g["cost"] > 0]
    waste_ags = [g for g in spend_ags if g["conv"] == 0]
    print(f"\n[ad groups with spend: {len(spend_ags)} | of those zero-conv: {len(waste_ags)} "
          f"= ${sum(g['cost'] for g in waste_ags):,.2f}]")

    # ================= AD =================
    print("\n\n### AD LEVEL - worst 30")
    ads = []
    for b in bundles:
        for a in b["ads"]:
            e = norm(a)
            hl = " / ".join(a["headlines"]) if a["headlines"] else a["ad_type"]
            e["label"] = f"{b['account']['name'].replace(' - Live','')} | {a['ad_group'][:20]} | {hl[:30]}"
            e["strength"] = a["ad_strength"]
            ads.append(e)
    ads.sort(key=rank_key)
    print(f"{'ENTITY':<58} {'COST':>10} {'CONV':>5} {'CPA':>10} {'CTR':>6} {'CVR':>6} {'ABSTOP':>6}")
    for a in ads[:30]:
        if a["cost"] > 0:
            print(f"{a['label'][:58]:<58} {fmt(a['cost'],'m'):>10} {a['conv']:5.1f} "
                  f"{fmt(a['cpa'],'m'):>10} {fmt(a['ctr'],'p')} {fmt(a['cvr'],'p')} {fmt(a['abs_top'],'p')}")
    spend_ads = [a for a in ads if a["cost"] > 0]
    waste_ads = [a for a in spend_ads if a["conv"] == 0]
    print(f"\n[ads with spend: {len(spend_ads)} | zero-conv: {len(waste_ads)} "
          f"= ${sum(a['cost'] for a in waste_ads):,.2f}]")

    # ================= KEYWORD =================
    print("\n\n### KEYWORD LEVEL - worst 40 by wasted spend, with Quality Score")
    kws = []
    for b in bundles:
        for k in b["keywords"]:
            e = norm(k)
            e["label"] = (f"{b['account']['name'].replace(' - Live','')} | "
                          f"{k['keyword']} [{k['match_type'][:3]}]")
            e["qs"] = k["qs"]
            e["qs_ad"] = k["qs_ad_relevance"]
            e["qs_lp"] = k["qs_lp_exp"]
            e["qs_ctr"] = k["qs_exp_ctr"]
            kws.append(e)
    kws.sort(key=rank_key)
    print(f"{'KEYWORD':<52} {'COST':>9} {'CONV':>5} {'CPA':>9} {'CTR':>6} "
          f"{'QS':>3} {'ADREL':>14} {'LP':>14} {'EXPCTR':>14}")
    for k in kws[:40]:
        if k["cost"] > 0:
            print(f"{k['label'][:52]:<52} {fmt(k['cost'],'m'):>9} {k['conv']:5.1f} "
                  f"{fmt(k['cpa'],'m'):>9} {fmt(k['ctr'],'p')} "
                  f"{str(k['qs'] or '-'):>3} {k['qs_ad'][:14]:>14} {k['qs_lp'][:14]:>14} "
                  f"{k['qs_ctr'][:14]:>14}")

    spend_kws = [k for k in kws if k["cost"] > 0]
    waste_kws = [k for k in spend_kws if k["conv"] == 0]
    print(f"\n[keywords with spend: {len(spend_kws)} | zero-conv: {len(waste_kws)} "
          f"= ${sum(k['cost'] for k in waste_kws):,.2f}]")

    # ---- QS distribution among spending keywords ----
    print("\n### QUALITY SCORE DISTRIBUTION (keywords with MTD spend)")
    buckets = {}
    for k in spend_kws:
        q = k["qs"]
        key = "no QS" if not q else ("1-3 poor" if q <= 3 else "4-6 mid" if q <= 6 else "7-10 good")
        b_ = buckets.setdefault(key, {"n": 0, "cost": 0.0, "conv": 0.0})
        b_["n"] += 1
        b_["cost"] += k["cost"]
        b_["conv"] += k["conv"]
    for key in ["1-3 poor", "4-6 mid", "7-10 good", "no QS"]:
        if key in buckets:
            v = buckets[key]
            print(f"  {key:<10} keywords={v['n']:4d}  cost=${v['cost']:9,.2f}  conv={v['conv']:5.1f}  "
                  f"CPA={fmt(v['cost']/v['conv'] if v['conv'] else None,'m')}")

    print("\n### QS BY ACCOUNT (spending keywords only, weighted by cost)")
    per = {}
    for b in bundles:
        acc = b["account"]["name"]
        rows = [k for k in b["keywords"] if k["cost_micros"] > 0]
        scored = [k for k in rows if k["qs"]]
        if not rows:
            continue
        cost = sum(k["cost_micros"] for k in rows) / 1e6
        wq = (sum(k["qs"] * k["cost_micros"] for k in scored) / sum(k["cost_micros"] for k in scored)
              if scored and sum(k["cost_micros"] for k in scored) else None)
        low = [k for k in scored if k["qs"] <= 5]
        per[acc] = (len(rows), len(scored), wq, cost,
                    sum(k["cost_micros"] for k in low) / 1e6)
    for acc, (n, ns, wq, cost, lowcost) in sorted(per.items(), key=lambda x: (x[1][2] or 99)):
        print(f"  {acc:<38} kws_w_spend={n:4d} scored={ns:4d} "
              f"cost-wtd QS={wq if wq is None else round(wq,2)!s:>5} "
              f"spend_on_QS<=5=${lowcost:,.2f} of ${cost:,.2f}")


if __name__ == "__main__":
    main()
