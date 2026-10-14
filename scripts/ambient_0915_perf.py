#!/usr/bin/env python3
"""Ambient | 2026-09-15 | regime-split performance, conversion duplication, IS, search terms."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-15"
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
c = client(); identity_gate(c, verbose=False)

# Regimes. 2026-09-04 16:56 = CPC ceilings first created (uncapped -> capped).
# 2026-09-09 = negative changes. 2026-09-10 = budget/cap/ad-group/negative changes.
# Today 2026-09-15 is PARTIAL; last settled = 2026-09-14.
REG = {
    "R1_aug_baseline":        ("2026-08-01", "2026-08-31"),
    "R2_sep_precap":          ("2026-09-01", "2026-09-04"),
    "R3_postcap_preneg":      ("2026-09-05", "2026-09-08"),
    "R4_post_0909_neg":       ("2026-09-09", "2026-09-09"),
    "R5_post_0910_changes":   ("2026-09-10", "2026-09-14"),
    "R_settled_mtd":          ("2026-09-01", "2026-09-14"),
    "R_today_partial":        ("2026-09-15", "2026-09-15"),
    "R_all_history":          ("2019-01-01", "2026-09-14"),
    "R_last14_settled":       ("2026-09-01", "2026-09-14"),
}

def camp_block(lo, hi):
    rows = q(c, f"""
        SELECT campaign.id, campaign.name,
               metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr,
               metrics.average_cpc, metrics.conversions, metrics.all_conversions,
               metrics.search_impression_share,
               metrics.search_budget_lost_impression_share,
               metrics.search_rank_lost_impression_share,
               metrics.search_top_impression_share,
               metrics.search_absolute_top_impression_share,
               metrics.search_click_share
        FROM campaign WHERE campaign.id IN ({IN5})
          AND segments.date BETWEEN '{lo}' AND '{hi}'
    """)
    agg = {}
    for r in rows:
        k = str(r.campaign.id); m = r.metrics
        a = agg.setdefault(k, {"name": r.campaign.name, "impr": 0, "clicks": 0,
                               "cost": 0.0, "conv": 0.0, "all_conv": 0.0,
                               "is_num": 0.0, "is_den": 0, "bl_num": 0.0,
                               "rl_num": 0.0, "top_num": 0.0, "atop_num": 0.0})
        a["impr"] += m.impressions; a["clicks"] += m.clicks
        a["cost"] += m.cost_micros / 1e6
        a["conv"] += m.conversions; a["all_conv"] += m.all_conversions
        a["is_num"] += (m.search_impression_share or 0) * m.impressions
        a["bl_num"] += (m.search_budget_lost_impression_share or 0) * m.impressions
        a["rl_num"] += (m.search_rank_lost_impression_share or 0) * m.impressions
        a["top_num"] += (m.search_top_impression_share or 0) * m.impressions
        a["atop_num"] += (m.search_absolute_top_impression_share or 0) * m.impressions
        a["is_den"] += m.impressions
    for k, a in agg.items():
        d = a["is_den"] or 1
        a["cpc"] = round(a["cost"] / a["clicks"], 2) if a["clicks"] else 0.0
        a["ctr_pct"] = round(100 * a["clicks"] / a["impr"], 2) if a["impr"] else 0.0
        a["is_pct"] = round(100 * a["is_num"] / d, 2)
        a["lost_budget_pct"] = round(100 * a["bl_num"] / d, 2)
        a["lost_rank_pct"] = round(100 * a["rl_num"] / d, 2)
        a["top_pct"] = round(100 * a["top_num"] / d, 2)
        a["abs_top_pct"] = round(100 * a["atop_num"] / d, 2)
        a["cost"] = round(a["cost"], 2)
        for x in ("is_num", "bl_num", "rl_num", "top_num", "atop_num", "is_den"):
            a.pop(x)
    return agg

print("=== 1. REGIME-SPLIT CAMPAIGN PERFORMANCE ===")
out["regimes"] = {}
for name, (lo, hi) in REG.items():
    agg = camp_block(lo, hi)
    out["regimes"][name] = {"window": [lo, hi], "campaigns": agg}
    ti = sum(a["impr"] for a in agg.values()); tc = sum(a["clicks"] for a in agg.values())
    ts = sum(a["cost"] for a in agg.values()); tv = sum(a["conv"] for a in agg.values())
    tav = sum(a["all_conv"] for a in agg.values())
    print(f"\n  --- {name}  {lo}..{hi} ---")
    print(f"      TOTAL impr={ti:>7} clicks={tc:>4} cost=${ts:>9.2f} "
          f"cpc=${ts/tc if tc else 0:>7.2f} conv={tv:>5.1f} all_conv={tav:>6.1f}")
    for k, a in sorted(agg.items(), key=lambda x: -x[1]["cost"]):
        print(f"      {a['name'][22:45]:24s} impr={a['impr']:>6} clk={a['clicks']:>4} "
              f"${a['cost']:>8.2f} cpc=${a['cpc']:>6.2f} ctr={a['ctr_pct']:>5.2f}% "
              f"conv={a['conv']:>4.1f} IS={a['is_pct']:>5.2f}% "
              f"lostBud={a['lost_budget_pct']:>5.2f}% lostRank={a['lost_rank_pct']:>5.2f}%")

print("\n\n=== 2. CONVERSION ACTION x DATE on the five (settled Sept) ===")
rows = q(c, f"""
    SELECT campaign.id, campaign.name, segments.date,
           segments.conversion_action, segments.conversion_action_name,
           segments.conversion_action_category,
           metrics.conversions, metrics.all_conversions
    FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-09-01' AND '2026-09-14'
""")
byact = defaultdict(lambda: {"conv": 0.0, "all": 0.0, "dates": set(), "camps": set()})
for r in rows:
    k = (r.segments.conversion_action.split("/")[-1], r.segments.conversion_action_name)
    byact[k]["conv"] += r.metrics.conversions
    byact[k]["all"] += r.metrics.all_conversions
    byact[k]["dates"].add(r.segments.date)
    byact[k]["camps"].add(r.campaign.name[22:45])
print(f"  {'action_id':>14} {'conv':>7} {'all':>7}  name")
tot_c = tot_a = 0.0
acts = []
for (aid, nm), v in sorted(byact.items(), key=lambda x: -x[1]["all"]):
    tot_c += v["conv"]; tot_a += v["all"]
    acts.append({"action_id": aid, "name": nm, "conversions": round(v["conv"], 2),
                 "all_conversions": round(v["all"], 2),
                 "dates": sorted(v["dates"]), "campaigns": sorted(v["camps"])})
    print(f"  {aid:>14} {v['conv']:>7.2f} {v['all']:>7.2f}  {nm}")
    print(f"                 dates={sorted(v['dates'])} camps={sorted(v['camps'])}")
print(f"  {'TOTAL':>14} {tot_c:>7.2f} {tot_a:>7.2f}")
out["conversion_by_action_sep_settled"] = acts

print("\n=== 3. ALL-TIME CONVERSION ACTION TOTALS on the five ===")
rows = q(c, f"""
    SELECT campaign.id, segments.conversion_action, segments.conversion_action_name,
           metrics.conversions, metrics.all_conversions
    FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-08-01' AND '2026-09-14'
""")
allact = defaultdict(lambda: {"conv": 0.0, "all": 0.0})
for r in rows:
    k = (r.segments.conversion_action.split("/")[-1], r.segments.conversion_action_name)
    allact[k]["conv"] += r.metrics.conversions
    allact[k]["all"] += r.metrics.all_conversions
out["conversion_by_action_launch_to_date"] = [
    {"action_id": a, "name": n, "conversions": round(v["conv"], 2),
     "all_conversions": round(v["all"], 2)}
    for (a, n), v in sorted(allact.items(), key=lambda x: -x[1]["all"])]
for x in out["conversion_by_action_launch_to_date"]:
    print(f"  {x['action_id']:>14} conv={x['conversions']:>7.2f} all={x['all_conversions']:>7.2f}  {x['name']}")

print("\n=== 4. HVAC INSTALLATION campaign: ad group split, settled Sept ===")
rows = q(c, f"""
    SELECT ad_group.id, ad_group.name, ad_group.status,
           metrics.impressions, metrics.clicks, metrics.cost_micros,
           metrics.conversions, metrics.all_conversions
    FROM ad_group WHERE campaign.id = 24132507747
      AND segments.date BETWEEN '2026-09-01' AND '2026-09-14'
""")
agg = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0, "all": 0.0})
for r in rows:
    k = (str(r.ad_group.id), r.ad_group.name, E(r.ad_group.status))
    agg[k]["impr"] += r.metrics.impressions; agg[k]["clicks"] += r.metrics.clicks
    agg[k]["cost"] += r.metrics.cost_micros / 1e6
    agg[k]["conv"] += r.metrics.conversions; agg[k]["all"] += r.metrics.all_conversions
for k, v in agg.items():
    print(f"  {k[0]} {k[2]:8s} {k[1][:40]:40s} impr={v['impr']:>5} clk={v['clicks']:>4} "
          f"${v['cost']:>8.2f} conv={v['conv']:.1f} all={v['all']:.1f}")
out["hvac_install_adgroup_split"] = [
    {"ad_group_id": k[0], "name": k[1], "status": k[2], **{kk: (round(vv, 2) if isinstance(vv, float) else vv)
                                                          for kk, vv in v.items()}}
    for k, v in agg.items()]

print("\n=== 5. SEARCH TERMS on the five, settled Sept, with cost or conversions ===")
rows = q(c, f"""
    SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
           search_term_view.search_term, search_term_view.status,
           segments.keyword.info.text, segments.keyword.info.match_type,
           metrics.impressions, metrics.clicks, metrics.cost_micros,
           metrics.conversions, metrics.all_conversions
    FROM search_term_view WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-09-01' AND '2026-09-14'
""")
terms = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0,
                             "all": 0.0, "camps": set(), "kws": set()})
for r in rows:
    k = r.search_term_view.search_term
    t = terms[k]
    t["impr"] += r.metrics.impressions; t["clicks"] += r.metrics.clicks
    t["cost"] += r.metrics.cost_micros / 1e6
    t["conv"] += r.metrics.conversions; t["all"] += r.metrics.all_conversions
    t["camps"].add(r.campaign.name[22:42]); t["kws"].add(r.segments.keyword.info.text)
out["search_terms_sep"] = [
    {"term": k, "impressions": v["impr"], "clicks": v["clicks"],
     "cost": round(v["cost"], 2), "conversions": round(v["conv"], 2),
     "all_conversions": round(v["all"], 2),
     "campaigns": sorted(v["camps"]), "matched_keywords": sorted(v["kws"])}
    for k, v in sorted(terms.items(), key=lambda x: -x[1]["cost"])]
print(f"  distinct search terms: {len(terms)}")
print(f"  {'cost':>8} {'clk':>4} {'imp':>5} {'conv':>5}  term  | campaigns")
for x in out["search_terms_sep"][:40]:
    print(f"  {x['cost']:>8.2f} {x['clicks']:>4} {x['impressions']:>5} "
          f"{x['conversions']:>5.1f}  {x['term'][:44]:44s} | {x['campaigns']}")
multi = [x for x in out["search_terms_sep"] if len(x["campaigns"]) > 1]
print(f"\n  terms appearing in MORE THAN ONE campaign: {len(multi)}")
for x in multi[:25]:
    print(f"    ${x['cost']:>7.2f} {x['term'][:44]:44s} {x['campaigns']}")
out["multi_campaign_terms"] = multi

p = SNAP / f"performance-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
