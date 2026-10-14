#!/usr/bin/env python3
"""Ambient | 2026-09-30d | READ-ONLY Phase 1 for the Heating & Furnace Repair CPC-ceiling investigation. No mutations.

Campaign 24257819463. Complete days 2026-09-17..2026-09-29; 2026-09-30 shown separately as PROVISIONAL.
Keyword metrics, impression share, reconciled leads (from the v2 reconciliation file), search terms (raw terms to disk
only; aggregates and CPC buckets printed), daily CPC, and legacy repair CPC/conversion history.
Writes snapshots/repair-cpc-snapshot-2026-09-30.json.
"""
from __future__ import annotations
import sys, json, re, collections, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, EXPORTS, CLIENT_DIR, ROOT  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
import yaml  # noqa: E402

CAMP = "24257819463"
A, B, T = "2026-09-17", "2026-09-29", "2026-09-30"
REPAIR = re.compile(r"repair|fix|not (working|heating|turning)|no heat|broken|won'?t|stopped|service|technician|troubleshoot", re.I)
HEAT = re.compile(r"heat|furnace|boiler|hvac|heater", re.I)
BUCKETS = [(0, 8), (8, 10), (10, 12), (12, 15), (15, 18), (18, 21), (21, 25), (25, 30), (30, 42), (42, 1e9)]

cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
wo = yaml.safe_load((CLIENT_DIR / "work-orders" / "work-order-heating-repair-cpc-ceiling-2026-09-30.yaml").read_text(encoding="utf-8"))
err = validate_work_order(wo, cl)
print("work order:", "VALID" if not err else err)
c = client()
ident = identity_gate(c, verbose=True)
out = {"identity": {k: ident[k] for k in ("customer_id", "descriptive_name")}, "windows": {"complete": [A, B], "provisional": T}}


def m(x):
    return dict(impr=x.impressions, clicks=x.clicks, cost=round(x.cost_micros / 1e6, 2), conv=round(x.conversions, 2),
                cpc=round(x.cost_micros / 1e6 / x.clicks, 2) if x.clicks else None)


r = q(c, f"""SELECT campaign.id, campaign.name, campaign.status, campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros,
        campaign_budget.id, campaign_budget.amount_micros FROM campaign WHERE campaign.id = {CAMP}""")[0]
out["campaign"] = dict(name=r.campaign.name, status=E(r.campaign.status), bidding=E(r.campaign.bidding_strategy_type),
                       ceiling=r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6, budget_id=str(r.campaign_budget.id),
                       budget=r.campaign_budget.amount_micros / 1e6)
print("\nCAMPAIGN", out["campaign"])
for label, (a, b) in (("complete", (A, B)), ("provisional", (T, T))):
    x = q(c, f"""SELECT campaign.id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
            metrics.search_impression_share, metrics.search_rank_lost_impression_share, metrics.search_budget_lost_impression_share,
            metrics.search_top_impression_share, metrics.search_absolute_top_impression_share
            FROM campaign WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{a}' AND '{b}'""")
    if x:
        mm = x[0].metrics
        out[f"campaign_{label}"] = dict(**m(mm), IS=round(mm.search_impression_share * 100, 1),
                                        lost_rank=round(mm.search_rank_lost_impression_share * 100, 1),
                                        lost_budget=round(mm.search_budget_lost_impression_share * 100, 1),
                                        top=round(mm.search_top_impression_share * 100, 1), abs_top=round(mm.search_absolute_top_impression_share * 100, 1))
        print(f"  {label:11s}", out[f"campaign_{label}"])
daily = {}
for x in q(c, f"SELECT campaign.id, segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros FROM campaign WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{A}' AND '{T}'"):
    if x.metrics.impressions:
        daily[x.segments.date] = m(x.metrics)
out["daily"] = daily
print("  daily:", {k: (v["clicks"], v["cost"], v["cpc"]) for k, v in sorted(daily.items())})

# ---- keywords ----
groups = {str(x.ad_group.id): dict(name=x.ad_group.name, status=E(x.ad_group.status)) for x in q(c,
          f"SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status FROM ad_group WHERE campaign.id = {CAMP} AND ad_group.status != 'REMOVED'")}
kws = {}
for x in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
        ad_group_criterion.status, ad_group_criterion.system_serving_status, ad_group_criterion.quality_info.quality_score,
        ad_group_criterion.position_estimates.first_page_cpc_micros, ad_group_criterion.position_estimates.top_of_page_cpc_micros,
        ad_group_criterion.position_estimates.first_position_cpc_micros
        FROM ad_group_criterion WHERE campaign.id = {CAMP} AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE
        AND ad_group_criterion.status != 'REMOVED'"""):
    k = x.ad_group_criterion
    pe = k.position_estimates
    kws[(str(x.ad_group.id), str(k.criterion_id))] = dict(
        ad_group=groups[str(x.ad_group.id)]["name"][7:], ag_status=groups[str(x.ad_group.id)]["status"], text=k.keyword.text,
        match=E(k.keyword.match_type), status=E(k.status), serving=E(k.system_serving_status), qs=k.quality_info.quality_score,
        first_page_cpc=round(pe.first_page_cpc_micros / 1e6, 2) if pe.first_page_cpc_micros else None,
        top_of_page_cpc=round(pe.top_of_page_cpc_micros / 1e6, 2) if pe.top_of_page_cpc_micros else None,
        first_position_cpc=round(pe.first_position_cpc_micros / 1e6, 2) if pe.first_position_cpc_micros else None)
for label, (a, b) in (("complete", (A, B)), ("provisional", (T, T))):
    for x in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions,
            metrics.search_impression_share, metrics.search_rank_lost_impression_share, metrics.search_top_impression_share,
            metrics.search_absolute_top_impression_share
            FROM keyword_view WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{a}' AND '{b}'"""):
        key = (str(x.ad_group.id), str(x.ad_group_criterion.criterion_id))
        if key in kws:
            mm = x.metrics
            kws[key][label] = dict(**m(mm), IS=round(mm.search_impression_share * 100, 1) if mm.search_impression_share else None,
                                   lost_rank=round(mm.search_rank_lost_impression_share * 100, 1) if mm.search_rank_lost_impression_share else None,
                                   top=round(mm.search_top_impression_share * 100, 1) if mm.search_top_impression_share else None,
                                   abs_top=round(mm.search_absolute_top_impression_share * 100, 1) if mm.search_absolute_top_impression_share else None)
rec = json.loads((SNAP / "cpl-reconciliation-2026-09-30.json").read_text(encoding="utf-8"))
leads_by_ag = collections.Counter(r["ad_group"] for r in rec["leads"] if r.get("campaign") == CAMP and r["verification"] == "VERIFIED"
                                  and r["paid"] in ("CLICK_ID", "CALL_VIEW"))
unverified_calls = [cv for cv in rec["unmatched_call_views"] if cv["campaign"] == CAMP]
out["keywords"] = {f"{k[0]}|{k[1]}": v for k, v in kws.items()}
out["verified_leads_by_ad_group"] = dict(leads_by_ag)
out["unverified_google_calls"] = unverified_calls
print("\nKEYWORDS (enabled ad groups; complete days | provisional today)")
for (g, cid), v in sorted(kws.items(), key=lambda z: (z[1]["ad_group"], z[1]["text"], z[1]["match"])):
    cmp_, p = v.get("complete", {}), v.get("provisional", {})
    print(f"  {v['ad_group'][:22]:22s} {v['text'][:30]:30s} {v['match']:6s} {v['status']:7s} QS {v['qs'] or '-'} "
          f"| {cmp_.get('impr', 0):4d}i {cmp_.get('clicks', 0):3d}c ${cmp_.get('cost', 0):7.2f} cpc {cmp_.get('cpc') or '-'} conv {cmp_.get('conv', 0)} "
          f"IS {cmp_.get('IS')} rankLost {cmp_.get('lost_rank')} top {cmp_.get('top')} | today {p.get('clicks', 0)}c ${p.get('cost', 0):.2f} "
          f"| est first-page {v['first_page_cpc']} top {v['top_of_page_cpc']} pos1 {v['first_position_cpc']}")
print("verified leads by ad group:", dict(leads_by_ag) or 0, "| unverified Google calls:", [(cv["start"], cv["dur"]) for cv in unverified_calls])

# ---- search terms: raw to disk, aggregates printed ----
rows = []
for x in q(c, f"""SELECT ad_group.id, search_term_view.search_term, segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
        FROM search_term_view WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{A}' AND '{T}'"""):
    rows.append(dict(ad_group=str(x.ad_group.id), term=x.search_term_view.search_term, date=x.segments.date, impr=x.metrics.impressions,
                     clicks=x.metrics.clicks, cost=x.metrics.cost_micros / 1e6, conv=x.metrics.conversions))
with (EXPORTS / "repair-search-terms-2026-09-30.jsonl").open("w", encoding="utf-8") as f:
    for r0 in rows:
        f.write(json.dumps(r0) + "\n")
st = collections.defaultdict(collections.Counter)
cpc_b = collections.Counter(); cpc_cost = collections.Counter()
for r0 in rows:
    if r0["date"] > B:
        continue
    bucket = "repair_intent" if (REPAIR.search(r0["term"]) and HEAT.search(r0["term"])) else ("heating_other" if HEAT.search(r0["term"]) else "out_of_scope")
    agn = groups.get(r0["ad_group"], {}).get("name", r0["ad_group"])[7:]
    st[(agn, bucket)].update(dict(terms=1, impr=r0["impr"], clicks=r0["clicks"], cost=r0["cost"], conv=r0["conv"]))
    if r0["clicks"]:
        tcpc = r0["cost"] / r0["clicks"]
        lab = next(f"${lo:g}-{hi:g}" if hi < 1e9 else f">${lo:g}" for lo, hi in BUCKETS if lo <= tcpc < hi)
        cpc_b[lab] += r0["clicks"]; cpc_cost[lab] += r0["cost"]
vis_cost = sum(v["cost"] for v in st.values())
out["search_terms"] = {f"{k[0]}|{k[1]}": {kk: round(vv, 2) for kk, vv in v.items()} for k, v in st.items()}
out["search_term_click_cpc_buckets"] = {k: dict(clicks=cpc_b[k], cost=round(cpc_cost[k], 2)) for k in cpc_b}
camp_cost = out.get("campaign_complete", {}).get("cost", 0)
print(f"\nSEARCH TERMS (complete days; raw on disk): {len(rows)} rows; visible cost ${vis_cost:.2f} of campaign ${camp_cost:.2f} ({100 * vis_cost / camp_cost if camp_cost else 0:.0f}%)")
for k, v in sorted(st.items()):
    print(f"  {k[0][:24]:24s} {k[1]:14s} {dict((kk, round(vv, 2)) for kk, vv in v.items())}")
print("  clicks by term-level CPC bucket (a term with 1 click = that click's price):")
for lo, hi in BUCKETS:
    lab = f"${lo:g}-{hi:g}" if hi < 1e9 else f">${lo:g}"
    if cpc_b[lab]:
        print(f"     {lab:9s} clicks {cpc_b[lab]:3d} cost ${cpc_cost[lab]:.2f}")

# ---- legacy repair history (conversions are Google's historical counts, known to double-count) ----
leg = {}
for x in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros,
        metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions FROM campaign
        WHERE segments.date BETWEEN '2019-01-01' AND '2026-09-16' AND metrics.clicks > 0"""):
    n = x.campaign.name.lower()
    if re.search(r"heating|furnace|boiler repair", n) and "install" not in n and "maint" not in n:
        leg[str(x.campaign.id)] = dict(name=x.campaign.name, status=E(x.campaign.status), bidding=E(x.campaign.bidding_strategy_type),
                                       ceiling=x.campaign.target_spend.cpc_bid_ceiling_micros / 1e6, **m(x.metrics))
out["legacy_repair_campaigns"] = leg
print("\nLEGACY heating/furnace repair campaigns, all time to 2026-09-16:")
for k, v in leg.items():
    print(f"  {k} {v['name'][:40]:40s} {v['status']:7s} {v['bidding']:18s} ceil {v['ceiling']} | {v['clicks']}c ${v['cost']:.2f} cpc {v['cpc']} conv {v['conv']} "
          f"cost/conv {round(v['cost'] / v['conv'], 2) if v['conv'] else '-'}")
# by heating season for the main legacy Heating Repair campaign(s)
seas = collections.defaultdict(collections.Counter)
if leg:
    for x in q(c, f"""SELECT campaign.id, segments.month, metrics.clicks, metrics.cost_micros, metrics.conversions FROM campaign
            WHERE campaign.id IN ({','.join(leg)}) AND segments.date BETWEEN '2019-01-01' AND '2026-09-16'"""):
        mo = x.segments.month[:7]
        y, mth = int(mo[:4]), int(mo[5:7])
        season = f"{y}-{y + 1}" if mth >= 9 else f"{y - 1}-{y}"
        seas[season].update(dict(clicks=x.metrics.clicks, cost=x.metrics.cost_micros / 1e6, conv=x.metrics.conversions))
out["legacy_by_season"] = {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in seas.items()}
for k, v in sorted(seas.items()):
    if v["clicks"]:
        print(f"  season {k}: {v['clicks']:.0f}c ${v['cost']:.2f} cpc ${v['cost'] / v['clicks']:.2f} conv {v['conv']:.1f} "
              f"conv rate {100 * v['conv'] / v['clicks']:.1f}% cost/conv {'$%.0f' % (v['cost'] / v['conv']) if v['conv'] else '-'}")

# ---- all-time repair-intent search terms, account-wide: converting vs non-converting price (aggregates only) ----
agg = {"converting": collections.Counter(), "non_converting": collections.Counter()}
conv_b = collections.Counter()
for x in q(c, """SELECT search_term_view.search_term, metrics.clicks, metrics.cost_micros, metrics.conversions FROM search_term_view
        WHERE segments.date BETWEEN '2019-01-01' AND '2026-09-29' AND metrics.clicks > 0"""):
    t = x.search_term_view.search_term
    if not (REPAIR.search(t) and HEAT.search(t)) or re.search(r"install|replac|new |maint|tune|water heater|tankless|\bac\b|air cond|cool", t, re.I):
        continue
    k = "converting" if x.metrics.conversions > 0 else "non_converting"
    agg[k].update(dict(terms=1, clicks=x.metrics.clicks, cost=x.metrics.cost_micros / 1e6, conv=x.metrics.conversions))
    if k == "converting":
        tcpc = x.metrics.cost_micros / 1e6 / x.metrics.clicks
        lab = next(f"${lo:g}-{hi:g}" if hi < 1e9 else f">${lo:g}" for lo, hi in BUCKETS if lo <= tcpc < hi)
        conv_b[lab] += x.metrics.conversions
out["alltime_heating_repair_terms"] = {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in agg.items()}
out["alltime_converting_repair_conv_by_term_cpc"] = dict(conv_b)
print("\nALL-TIME heating/furnace REPAIR-intent search terms, account-wide (Google conversions, historically double-counted):")
for k, v in agg.items():
    if v["clicks"]:
        print(f"  {k:15s} terms {v['terms']:.0f} clicks {v['clicks']:.0f} cost ${v['cost']:.2f} avg cpc ${v['cost'] / v['clicks']:.2f} conv {v['conv']:.1f}")
print("  converting-term conversions by the term's average CPC:", {k: round(v, 1) for k, v in conv_b.items()})
(SNAP / "repair-cpc-snapshot-2026-09-30.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print("\nwrote snapshots/repair-cpc-snapshot-2026-09-30.json")
