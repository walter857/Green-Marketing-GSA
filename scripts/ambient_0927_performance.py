#!/usr/bin/env python3
"""Ambient | 2026-09-27 | READ-ONLY performance review of the heating campaigns and ad groups.

Windows: heating build to date (2026-09-17..2026-09-26) and post offer-page migration
(2026-09-24..2026-09-26). Campaign, ad group, keyword (QS components, CPC estimates), RSA ad strength,
device, daily pacing vs budget, conversions by action, WhatConverts leads and Google call records.
Search terms appear only as bucket aggregates. Writes snapshots/performance-2026-09-27.json.
"""
from __future__ import annotations
import sys, json, re, datetime, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, CLIENT_DIR
import ambient_0926_heating_st_negatives as st
from gm_gsa.config import load_dotenv_if_available
from gm_gsa.whatconverts import fetch_leads

SEVEN = st.SEVEN
SHORT = {"24257819463": "Repair", "24268690038": "Heat Pump", "24257819466": "Install/Replace", "24132507744": "Boiler",
         "24279798229": "Maintenance", "24268690041": "Thermostat", "24274160783": "Geothermal"}
A, B, END = "2026-09-17", "2026-09-24", "2026-09-26"
c = client(); identity_gate(c, verbose=False)
IN = ",".join(SEVEN)
out = {"windows": {"build_to_date": [A, END], "post_migration": [B, END]}}


def mrow(r):
    m = r.metrics
    return dict(impr=m.impressions, clicks=m.clicks, cost=round(m.cost_micros / 1e6, 2), conv=round(m.conversions, 2),
                allconv=round(m.all_conversions, 2))


def agg(rows):
    t = collections.Counter()
    for x in rows:
        for k in ("impr", "clicks", "cost", "conv", "allconv"): t[k] += x[k]
    t = dict(t); t["cost"] = round(t.get("cost", 0), 2)
    t["ctr"] = round(100 * t["clicks"] / t["impr"], 1) if t.get("impr") else 0
    t["cpc"] = round(t["cost"] / t["clicks"], 2) if t.get("clicks") else 0
    return t


# ---- campaigns ----
camp_meta = {str(r.campaign.id): dict(status=E(r.campaign.status), primary=E(r.campaign.primary_status), budget=r.campaign_budget.amount_micros / 1e6,
             ceiling=(r.campaign.target_spend.cpc_bid_ceiling_micros or 0) / 1e6)
             for r in q(c, f"SELECT campaign.id, campaign.status, campaign.primary_status, campaign_budget.amount_micros, campaign.target_spend.cpc_bid_ceiling_micros FROM campaign WHERE campaign.id IN ({IN})")}
daily = collections.defaultdict(dict)
for r in q(c, f"""SELECT campaign.id, segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions
        FROM campaign WHERE campaign.id IN ({IN}) AND segments.date BETWEEN '{A}' AND '{END}'"""):
    daily[str(r.campaign.id)][r.segments.date] = mrow(r)
IS = {}
for win, (s, e) in (("A", (A, END)), ("B", (B, END))):
    for r in q(c, f"""SELECT campaign.id, metrics.search_impression_share, metrics.search_budget_lost_impression_share,
            metrics.search_rank_lost_impression_share, metrics.search_top_impression_share, metrics.search_absolute_top_impression_share
            FROM campaign WHERE campaign.id IN ({IN}) AND segments.date BETWEEN '{s}' AND '{e}'"""):
        m = r.metrics
        IS[(str(r.campaign.id), win)] = dict(IS=round(m.search_impression_share * 100, 1), lostBudget=round(m.search_budget_lost_impression_share * 100, 1),
                                            lostRank=round(m.search_rank_lost_impression_share * 100, 1), top=round(m.search_top_impression_share * 100, 1),
                                            abstop=round(m.search_absolute_top_impression_share * 100, 1))
conv_by_action = collections.defaultdict(collections.Counter)
for r in q(c, f"""SELECT campaign.id, segments.conversion_action_name, metrics.conversions, metrics.all_conversions FROM campaign
        WHERE campaign.id IN ({IN}) AND segments.date BETWEEN '{A}' AND '{END}'"""):
    if r.metrics.all_conversions:
        conv_by_action[str(r.campaign.id)][r.segments.conversion_action_name] += round(r.metrics.all_conversions, 2)
device = collections.defaultdict(dict)
for r in q(c, f"""SELECT campaign.id, segments.device, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions
        FROM campaign WHERE campaign.id IN ({IN}) AND segments.date BETWEEN '{A}' AND '{END}'"""):
    device[str(r.campaign.id)][E(r.segments.device)] = mrow(r)

print("=== CAMPAIGNS (build to date 09-17..09-26 | post-migration 09-24..09-26) ===")
camp_out = {}
for cid in SEVEN:
    d = daily.get(cid, {}); tA = agg(d.values()); tB = agg(v for k, v in d.items() if k >= B)
    days_spend = {k: v["cost"] for k, v in d.items() if v["cost"] > 0}
    over = sum(1 for v in days_spend.values() if v >= 0.95 * camp_meta[cid]["budget"])
    cm = camp_meta[cid]
    camp_out[cid] = dict(meta=cm, A=tA, B=tB, IS_A=IS.get((cid, "A")), IS_B=IS.get((cid, "B")), days_with_spend=len(days_spend),
                         days_at_or_over_budget=over, conv_by_action=dict(conv_by_action[cid]), device=device[cid])
    print(f"\n{SHORT[cid]:15s} {cm['status']:7s} {cm['primary']:12s} budget ${cm['budget']:.0f} ceiling ${cm['ceiling']:.0f}")
    print(f"   A: {tA}  IS {IS.get((cid, 'A'))}")
    print(f"   B: {tB}  IS {IS.get((cid, 'B'))}")
    print(f"   spend days {len(days_spend)} (at/over budget {over}) daily: {dict(sorted((k[5:], round(v)) for k, v in days_spend.items()))}")
    if conv_by_action[cid]: print(f"   conversions by action (all): {dict(conv_by_action[cid])}")
    print(f"   device: {{" + ", ".join(f"{k}: {v['clicks']}cl ${v['cost']}" for k, v in device[cid].items() if v['impr']) + "}")
out["campaigns"] = camp_out

# ---- ad groups ----
ag_meta = {}
for r in q(c, f"""SELECT ad_group.id, ad_group.name, ad_group.status, ad_group.primary_status, ad_group.primary_status_reasons, campaign.id
        FROM ad_group WHERE campaign.id IN ({IN}) AND ad_group.status != 'REMOVED'"""):
    ag_meta[str(r.ad_group.id)] = dict(name=r.ad_group.name.replace("SKAG | ", ""), status=E(r.ad_group.status), primary=E(r.ad_group.primary_status),
                                       reasons=[E(x) for x in r.ad_group.primary_status_reasons], camp=str(r.campaign.id))
labels = collections.defaultdict(list)
for r in q(c, "SELECT ad_group.id, label.name FROM ad_group_label"): labels[str(r.ad_group.id)].append(r.label.name)
ag_perf = collections.defaultdict(dict)
for win, (s, e) in (("A", (A, END)), ("B", (B, END))):
    for r in q(c, f"""SELECT ad_group.id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions,
            metrics.search_impression_share, metrics.search_rank_lost_impression_share FROM ad_group WHERE campaign.id IN ({IN})
            AND segments.date BETWEEN '{s}' AND '{e}'"""):
        x = mrow(r); x["IS"] = round(r.metrics.search_impression_share * 100, 1); x["lostRank"] = round(r.metrics.search_rank_lost_impression_share * 100, 1)
        ag_perf[str(r.ad_group.id)][win] = x
en_ads = collections.defaultdict(list)
for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad_strength, ad_group_ad.policy_summary.approval_status,
        metrics.impressions, metrics.clicks FROM ad_group_ad WHERE campaign.id IN ({IN}) AND ad_group_ad.status = 'ENABLED'
        AND segments.date BETWEEN '{A}' AND '{END}'"""):
    en_ads[str(r.ad_group.id)].append((E(r.ad_group_ad.ad_strength), E(r.ad_group_ad.policy_summary.approval_status), r.metrics.impressions, r.metrics.clicks))
strength = {}
for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.ad_strength, ad_group_ad.policy_summary.approval_status FROM ad_group_ad
        WHERE campaign.id IN ({IN}) AND ad_group_ad.status = 'ENABLED'"""):
    strength.setdefault(str(r.ad_group.id), []).append((E(r.ad_group_ad.ad_strength), E(r.ad_group_ad.policy_summary.approval_status)))
kw = collections.defaultdict(list)
for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
        ad_group_criterion.status, ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons,
        ad_group_criterion.quality_info.quality_score, ad_group_criterion.quality_info.creative_quality_score,
        ad_group_criterion.quality_info.post_click_quality_score, ad_group_criterion.quality_info.search_predicted_ctr,
        ad_group_criterion.position_estimates.first_page_cpc_micros, ad_group_criterion.position_estimates.top_of_page_cpc_micros,
        ad_group_criterion.position_estimates.first_position_cpc_micros
        FROM ad_group_criterion WHERE campaign.id IN ({IN}) AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE
        AND ad_group_criterion.status = 'ENABLED'"""):
    k = r.ad_group_criterion; qi = k.quality_info; pe = k.position_estimates
    kw[str(r.ad_group.id)].append(dict(id=str(k.criterion_id), text=k.keyword.text, mt=E(k.keyword.match_type), primary=E(k.primary_status),
        reasons=[E(x) for x in k.primary_status_reasons], qs=qi.quality_score, ad_rel=E(qi.creative_quality_score), lp=E(qi.post_click_quality_score),
        ectr=E(qi.search_predicted_ctr), first_page=round(pe.first_page_cpc_micros / 1e6, 2), top=round(pe.top_of_page_cpc_micros / 1e6, 2),
        first_pos=round(pe.first_position_cpc_micros / 1e6, 2)))
kwperf = collections.defaultdict(lambda: collections.Counter())
for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.all_conversions
        FROM keyword_view WHERE campaign.id IN ({IN}) AND segments.date BETWEEN '{A}' AND '{END}'"""):
    kk = (str(r.ad_group.id), str(r.ad_group_criterion.criterion_id)); c_ = kwperf[kk]
    c_["impr"] += r.metrics.impressions; c_["clicks"] += r.metrics.clicks; c_["cost"] += r.metrics.cost_micros / 1e6; c_["allconv"] += r.metrics.all_conversions

# search-term buckets per ad group (aggregates only)
geo = set(json.loads(st.GEO.read_text()))
st_rows = collections.defaultdict(lambda: collections.Counter())
ever = collections.Counter()
for r in q(c, """SELECT search_term_view.search_term, metrics.all_conversions FROM search_term_view
        WHERE segments.date BETWEEN '2019-01-01' AND '2026-09-26' AND metrics.all_conversions > 0"""):
    ever[r.search_term_view.search_term.strip().lower()] += r.metrics.all_conversions
kws_all = {r.ad_group_criterion.keyword.text.strip().lower() for r in q(c, "SELECT ad_group_criterion.keyword.text FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE AND ad_group_criterion.status != 'REMOVED'")}
st.PROTECTED.clear()
for t in list(ever) + list(kws_all): st.PROTECTED.update(x for x in re.split(r"[^a-z0-9/']+", t) if x)
for r in q(c, f"""SELECT search_term_view.search_term, ad_group.id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.all_conversions
        FROM search_term_view WHERE campaign.id IN ({IN}) AND segments.date BETWEEN '{A}' AND '{END}'"""):
    t = r.search_term_view.search_term.strip().lower()
    b = st.classify(t, geo, r.metrics.all_conversions + ever.get(t, 0))
    x = st_rows[str(r.ad_group.id)]; x[b + "_cost"] += r.metrics.cost_micros / 1e6; x[b + "_clicks"] += r.metrics.clicks; x[b + "_impr"] += r.metrics.impressions

print("\n=== AD GROUPS (build to date) ===")
ag_out = {}
for cid in SEVEN:
    print(f"\n-- {SHORT[cid]}")
    for gid, g in sorted(ag_meta.items(), key=lambda x: x[1]["name"]):
        if g["camp"] != cid: continue
        pa = ag_perf[gid].get("A", {}); pb = ag_perf[gid].get("B", {})
        ks = kw.get(gid, [])
        qs = [k["qs"] for k in ks if k["qs"]]
        stg = collections.Counter(s for s, ap in strength.get(gid, []))
        stb = st_rows.get(gid, {})
        waste = round(stb.get("OUT_OF_SCOPE_cost", 0) + stb.get("COOLING_cost", 0), 2)
        ag_out[gid] = dict(meta=g, labels=labels[gid], A=pa, B=pb, keywords=ks, kwperf={k["id"]: dict(kwperf[(gid, k["id"])]) for k in ks},
                           ad_strength=dict(stg), st_buckets=dict(stb), offtopic_cost=waste)
        if not pa.get("impr") and "CORE_ACTIVE" not in labels[gid]:
            print(f"  {g['name'][:30]:30s} {','.join(labels[gid])[:40]:40s} no delivery (held)"); continue
        print(f"  {g['name'][:30]:30s} {g['primary'][:10]:10s} A {pa.get('impr',0)}i {pa.get('clicks',0)}cl ${pa.get('cost',0)} allconv {pa.get('allconv',0)} IS {pa.get('IS')} lostRank {pa.get('lostRank')} "
              f"| B {pb.get('impr',0)}i {pb.get('clicks',0)}cl ${pb.get('cost',0)} | QS {qs or '-'} | ads {dict(stg)} | off-topic ${waste}")
        for k in ks:
            p = kwperf[(gid, k["id"])]
            if p.get("impr") or k["reasons"]:
                print(f"      kw {k['mt'][:2]} qs={k['qs'] or '-'} ctr={k['ectr'][:5]} adrel={k['ad_rel'][:5]} lp={k['lp'][:5]} 1stpg=${k['first_page']} top=${k['top']} "
                      f"| {int(p.get('impr',0))}i {int(p.get('clicks',0))}cl ${round(p.get('cost',0),2)} | {','.join(r[:22] for r in k['reasons'])}")
out["ad_groups"] = ag_out

# ---- leads ----
load_dotenv_if_available(Path(__file__).resolve().parents[1] / ".env")
leads = fetch_leads("115814", "105803", A, "2026-09-27", client_yaml=CLIENT_DIR / "client.yaml")["leads"]
lc = collections.Counter((f"{l.get('lead_source')}/{l.get('lead_medium')}", l.get("lead_type"), "clickid" if (l.get("gclid") or l.get("gbraid") or l.get("wbraid")) else "-") for l in leads)
calls = [(r.call_view.start_call_date_time, r.call_view.call_duration_seconds, str(r.campaign.id)) for r in q(c,
         f"SELECT call_view.start_call_date_time, call_view.call_duration_seconds, campaign.id FROM call_view WHERE call_view.start_call_date_time >= '{A} 00:00:00'")]
paid = {k: v for k, v in lc.items() if k[2] == "clickid" or "cpc" in k[0]}
print(f"\n=== LEADS {A}..today (QA excluded): {len(leads)} total; paid-labelled or click-id: {paid}; Google call records: {calls}")
out["leads"] = {"|".join(k): v for k, v in lc.items()}; out["calls"] = calls
(SNAP / "performance-2026-09-27.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print("\nWROTE snapshots/performance-2026-09-27.json")
