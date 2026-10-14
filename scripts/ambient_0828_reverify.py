#!/usr/bin/env python3
"""Ambient Cooling - Live | re-verification pass | READ ONLY, ZERO MUTATIONS.

Re-checks every claim behind ACE80A09AC134C85, EE6CFAD6667A95A1 and
C3038EDD9E621944 against fresh live data:

  1. CPC distribution per campaign (max, mean, median, p75, p90, converting-term CPC)
  2. WC Lead: is it an ACTIVE bidding defect or a HISTORICAL reporting artifact?
  3. Business Profile / LOCATION_SYNC asset: exact IDs, levels, performance, local actions
  4. hanover: exact member, what it blocks, what else blocks Hanover
  5. Sitelinks: fresh association read, offer subdomain vs main website
  6. Competitor negatives re-tested under the stricter safety rule
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, SNAP, TZ, client, q, identity_gate, E, write,
)
from ambient_0827_negative_audit import SERVICE_PROBES, blocks, words  # noqa: E402

STAMP = "2026-08-28-reverify"
WC_LEAD = "7643656486"
LOCATION_ASSET_SET = "8620443109"
ACCOUNT_SET = "11252984411"


def pct(sorted_vals, p):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * p / 100.0
    lo, hi = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    return round(sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo), 2)


def main():
    c = client()
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "read_only": True, "mutations": 0}
    print("== IDENTITY GATE ==")
    out["identity"] = identity_gate(c)

    # =====================================================================
    # 1. CPC DISTRIBUTION PER CAMPAIGN
    # =====================================================================
    print("\n== 1. CPC DISTRIBUTION (click-weighted, from keyword x date cells) ==")
    cells = defaultdict(list)
    for r in q(c, f"""SELECT campaign.id, segments.date,
                      ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
                      metrics.clicks, metrics.cost_micros, metrics.average_cpc
                      FROM keyword_view WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-27'
                        AND metrics.clicks > 0"""):
        cpc = r.metrics.cost_micros / 1e6 / r.metrics.clicks
        cells[str(r.campaign.id)].append({
            "date": r.segments.date,
            "keyword": r.ad_group_criterion.keyword.text,
            "match": E(r.ad_group_criterion.keyword.match_type),
            "clicks": r.metrics.clicks,
            "cost": round(r.metrics.cost_micros / 1e6, 2),
            "cell_cpc": round(cpc, 2)})

    cpc_stats = {}
    for cid in FIVE:
        rows = cells.get(cid, [])
        weighted = []
        for x in rows:
            weighted.extend([x["cell_cpc"]] * x["clicks"])
        weighted.sort()
        clicks = sum(x["clicks"] for x in rows)
        cost = round(sum(x["cost"] for x in rows), 2)
        cpc_stats[cid] = {
            "campaign": NAME[cid], "cells": len(rows), "clicks": clicks, "cost": cost,
            "mean_cpc": round(cost / clicks, 2) if clicks else None,
            "max_cell_cpc": max(weighted) if weighted else None,
            "min_cell_cpc": min(weighted) if weighted else None,
            "median_cpc": pct(weighted, 50),
            "p75_cpc": pct(weighted, 75),
            "p90_cpc": pct(weighted, 90),
            "distribution": weighted,
            "cells_detail": sorted(rows, key=lambda z: -z["cell_cpc"]),
        }
        s = cpc_stats[cid]
        print(f"  {NAME[cid]:20s} clicks={clicks:>3d} cost=${cost:>9,.2f} "
              f"mean=${s['mean_cpc'] or 0:>7.2f} median=${s['median_cpc'] or 0:>7.2f} "
              f"p75=${s['p75_cpc'] or 0:>7.2f} p90=${s['p90_cpc'] or 0:>7.2f} "
              f"max=${s['max_cell_cpc'] or 0:>7.2f}")
    out["cpc_distribution"] = cpc_stats

    print("\n  Every priced cell, highest CPC first:")
    for cid in FIVE:
        for x in cpc_stats[cid]["cells_detail"]:
            print(f"     {NAME[cid]:20s} {x['date']} [{x['match'][:6]:6s}] "
                  f"{x['keyword']:26s} clicks={x['clicks']:>2d} "
                  f"cost=${x['cost']:>8.2f} cellCPC=${x['cell_cpc']:>7.2f}")

    # converting-term CPC
    print("\n  CPC on terms that produced a PRIMARY conversion:")
    conv_cpc = []
    for r in q(c, f"""SELECT campaign.id, search_term_view.search_term,
                      metrics.clicks, metrics.cost_micros, metrics.conversions,
                      metrics.all_conversions
                      FROM search_term_view WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-27'
                        AND metrics.conversions > 0"""):
        cl = r.metrics.clicks
        conv_cpc.append({"campaign": NAME[str(r.campaign.id)],
                         "term": r.search_term_view.search_term,
                         "clicks": cl,
                         "cost": round(r.metrics.cost_micros / 1e6, 2),
                         "cpc": round(r.metrics.cost_micros / 1e6 / cl, 2) if cl else None,
                         "primary_conversions": round(r.metrics.conversions, 2)})
    out["converting_term_cpc"] = conv_cpc
    for x in sorted(conv_cpc, key=lambda z: -(z["cpc"] or 0)):
        print(f"     {x['campaign']:20s} CPC=${x['cpc'] or 0:>7.2f} clicks={x['clicks']} "
              f"cost=${x['cost']:>7.2f} conv={x['primary_conversions']}  '{x['term']}'")
    cc = [x["cpc"] for x in conv_cpc if x["cpc"]]
    out["converting_term_cpc_summary"] = {
        "n": len(cc), "min": min(cc) if cc else None, "max": max(cc) if cc else None,
        "mean": round(sum(cc) / len(cc), 2) if cc else None}
    print(f"     summary: n={len(cc)} min=${min(cc) if cc else 0:.2f} "
          f"max=${max(cc) if cc else 0:.2f} mean=${(sum(cc)/len(cc)) if cc else 0:.2f}")

    # =====================================================================
    # 2. WC LEAD - ACTIVE DEFECT OR HISTORICAL ARTIFACT?
    # =====================================================================
    print("\n== 2. WC LEAD: ACTIVE DEFECT OR HISTORICAL ARTIFACT? ==")
    wc = None
    for r in q(c, f"""SELECT conversion_action.id, conversion_action.name,
                      conversion_action.status, conversion_action.type,
                      conversion_action.category, conversion_action.origin,
                      conversion_action.primary_for_goal,
                      conversion_action.include_in_conversions_metric,
                      conversion_action.counting_type,
                      conversion_action.click_through_lookback_window_days,
                      conversion_action.attribution_model_settings.attribution_model,
                      conversion_action.owner_customer
                      FROM conversion_action
                      WHERE conversion_action.id = {WC_LEAD}"""):
        x = r.conversion_action
        wc = {"id": str(x.id), "name": x.name, "status": E(x.status),
              "type": E(x.type_), "category": E(x.category), "origin": E(x.origin),
              "primary_for_goal": x.primary_for_goal,
              "include_in_conversions_metric": x.include_in_conversions_metric,
              "counting_type": E(x.counting_type),
              "click_lookback_days": x.click_through_lookback_window_days,
              "attribution": E(x.attribution_model_settings.attribution_model),
              "owner": x.owner_customer.split("/")[-1] if x.owner_customer else ""}
    print(f"  {json.dumps(wc, indent=2)}")
    out["wc_lead_config"] = wc

    # the decisive test: conversions vs all_conversions BY DATE
    print("\n  WC Lead by date: metrics.conversions vs metrics.all_conversions")
    by_date = []
    for r in q(c, f"""SELECT segments.date, campaign.id,
                      segments.conversion_action, segments.conversion_action_name,
                      metrics.conversions, metrics.all_conversions
                      FROM campaign WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-27'
                        AND segments.conversion_action = 'customers/{CID}/conversionActions/{WC_LEAD}'
                        AND metrics.all_conversions > 0"""):
        by_date.append({"date": r.segments.date, "campaign": NAME[str(r.campaign.id)],
                        "conversions": round(r.metrics.conversions, 2),
                        "all_conversions": round(r.metrics.all_conversions, 2)})
    by_date.sort(key=lambda z: z["date"])
    out["wc_lead_by_date"] = by_date
    for x in by_date:
        flag = "  <== COUNTED in the Conversions column" if x["conversions"] > 0 else ""
        print(f"     {x['date']} {x['campaign']:20s} conversions={x['conversions']:.1f} "
              f"all_conversions={x['all_conversions']:.1f}{flag}")
    counted = [x for x in by_date if x["conversions"] > 0]
    not_counted = [x for x in by_date if x["conversions"] == 0]
    print(f"\n     dates where WC Lead COUNTED   : {[x['date'] for x in counted]}")
    print(f"     dates where WC Lead DID NOT   : {[x['date'] for x in not_counted]}")

    # conversion goals
    print("\n  Conversion goals that could carry WC Lead (CONTACT):")
    cust_goals = []
    for r in q(c, """SELECT customer_conversion_goal.category,
                     customer_conversion_goal.origin, customer_conversion_goal.biddable
                     FROM customer_conversion_goal"""):
        x = r.customer_conversion_goal
        cust_goals.append({"category": E(x.category), "origin": E(x.origin),
                           "biddable": x.biddable})
    camp_goals = []
    for r in q(c, f"""SELECT campaign.id, campaign_conversion_goal.category,
                      campaign_conversion_goal.origin, campaign_conversion_goal.biddable
                      FROM campaign_conversion_goal WHERE campaign.id IN ({IN5})"""):
        x = r.campaign_conversion_goal
        camp_goals.append({"campaign": NAME[str(r.campaign.id)], "category": E(x.category),
                           "origin": E(x.origin), "biddable": x.biddable})
    out["customer_conversion_goals"] = cust_goals
    out["campaign_conversion_goals"] = camp_goals
    for g in cust_goals:
        if g["category"] == "CONTACT":
            print(f"     customer goal CONTACT/{g['origin']:16s} biddable={g['biddable']}")
    for g in camp_goals:
        if g["category"] == "CONTACT":
            print(f"     campaign {g['campaign']:20s} CONTACT/{g['origin']:16s} "
                  f"biddable={g['biddable']}")

    # custom conversion goals
    ccg = []
    try:
        for r in q(c, """SELECT custom_conversion_goal.id, custom_conversion_goal.name,
                         custom_conversion_goal.conversion_actions,
                         custom_conversion_goal.status FROM custom_conversion_goal"""):
            x = r.custom_conversion_goal
            ccg.append({"id": str(x.id), "name": x.name, "status": E(x.status),
                        "conversion_actions": [a.split("/")[-1] for a in x.conversion_actions]})
    except Exception as exc:  # noqa: BLE001
        ccg = [{"error": str(exc)[:200]}]
    out["custom_conversion_goals"] = ccg
    print(f"     custom conversion goals: {ccg}")

    # which campaigns bid toward WC Lead: selective optimization
    sel = []
    for r in q(c, f"""SELECT campaign.id, campaign.selective_optimization.conversion_actions,
                      campaign.bidding_strategy_type
                      FROM campaign WHERE campaign.id IN ({IN5})"""):
        sel.append({"campaign": NAME[str(r.campaign.id)],
                    "bidding_strategy": E(r.campaign.bidding_strategy_type),
                    "selective_optimization": [
                        a.split("/")[-1] for a in
                        r.campaign.selective_optimization.conversion_actions]})
    out["selective_optimization"] = sel
    for s in sel:
        print(f"     {s['campaign']:20s} strategy={s['bidding_strategy']} "
              f"selective_optimization={s['selective_optimization'] or 'none'}")

    # change history on conversion actions
    print("\n  change_event rows touching CONVERSION_ACTION (API caps at 30 days):")
    ce = []
    try:
        for r in q(c, """SELECT change_event.change_date_time,
                         change_event.change_resource_type,
                         change_event.resource_change_operation,
                         change_event.changed_fields,
                         change_event.change_resource_name,
                         change_event.user_email, change_event.client_type
                         FROM change_event
                         WHERE change_event.change_date_time >= '2026-07-29'
                           AND change_event.change_date_time <= '2026-08-29'
                           AND change_event.change_resource_type = 'CONVERSION_ACTION'
                         ORDER BY change_event.change_date_time DESC LIMIT 200"""):
            x = r.change_event
            ce.append({"when": x.change_date_time, "op": E(x.resource_change_operation),
                       "resource": x.change_resource_name,
                       "fields": list(x.changed_fields.paths) if x.changed_fields else [],
                       "user": x.user_email, "client": E(x.client_type)})
    except Exception as exc:  # noqa: BLE001
        ce = [{"error": str(exc)[:300]}]
    out["conversion_action_change_events"] = ce
    if ce and "error" not in ce[0]:
        for x in ce:
            mark = "  <== WC Lead" if WC_LEAD in x["resource"] else ""
            print(f"     {x['when']} {x['op']:8s} {x['fields']} {x['user']}{mark}")
        if not ce:
            print("     (none returned)")
    else:
        print(f"     {ce}")
    if not ce:
        print("     ZERO change_event rows for CONVERSION_ACTION in the last 30 days.")

    # =====================================================================
    # 3. BUSINESS PROFILE / LOCATION ASSET
    # =====================================================================
    print("\n== 3. BUSINESS PROFILE LOCATION ASSET ==")
    asset_sets = []
    for r in q(c, """SELECT asset_set.id, asset_set.name, asset_set.type,
                     asset_set.status, asset_set.resource_name FROM asset_set"""):
        x = r.asset_set
        asset_sets.append({"id": str(x.id), "name": x.name, "type": E(x.type_),
                           "status": E(x.status), "resource_name": x.resource_name})
    cust_as = []
    for r in q(c, """SELECT customer_asset_set.asset_set, customer_asset_set.status,
                     customer_asset_set.resource_name FROM customer_asset_set"""):
        x = r.customer_asset_set
        cust_as.append({"asset_set": x.asset_set.split("/")[-1], "status": E(x.status),
                        "association_resource_name": x.resource_name})
    camp_as = []
    try:
        for r in q(c, """SELECT campaign.id, campaign_asset_set.asset_set,
                         campaign_asset_set.status, campaign_asset_set.resource_name
                         FROM campaign_asset_set"""):
            x = r.campaign_asset_set
            camp_as.append({"campaign": str(r.campaign.id),
                            "campaign_name": NAME.get(str(r.campaign.id), "(legacy)"),
                            "asset_set": x.asset_set.split("/")[-1],
                            "status": E(x.status),
                            "association_resource_name": x.resource_name})
    except Exception as exc:  # noqa: BLE001
        camp_as = [{"error": str(exc)[:200]}]
    out["asset_sets"] = asset_sets
    out["customer_asset_set_associations"] = cust_as
    out["campaign_asset_set_associations"] = camp_as
    for a in asset_sets:
        print(f"  asset_set {a['id']} {a['type']:16s} {a['status']:8s} {a['name']}")
    print(f"  customer-level associations: {cust_as}")
    print(f"  campaign-level associations on ANY campaign: "
          f"{[x for x in camp_as if not x.get('error')] or 'none'}")

    # the location assets inside the set
    asa = []
    try:
        for r in q(c, f"""SELECT asset_set_asset.asset, asset_set_asset.asset_set,
                          asset_set_asset.status FROM asset_set_asset
                          WHERE asset_set.id = {LOCATION_ASSET_SET}"""):
            x = r.asset_set_asset
            asa.append({"asset": x.asset.split("/")[-1], "status": E(x.status)})
    except Exception as exc:  # noqa: BLE001
        asa = [{"error": str(exc)[:200]}]
    out["location_assets_in_set"] = asa
    print(f"  assets inside LOCATION_SYNC set {LOCATION_ASSET_SET}: {asa}")

    # performance by click type per campaign
    print("\n  Click-type performance on the five (2026-08-01..2026-08-27):")
    ctype = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0,
                                 "conv": 0.0, "all_conv": 0.0})
    for r in q(c, f"""SELECT campaign.id, segments.click_type, metrics.impressions,
                      metrics.clicks, metrics.cost_micros, metrics.conversions,
                      metrics.all_conversions FROM campaign
                      WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-27'"""):
        k = (NAME[str(r.campaign.id)], E(r.segments.click_type))
        e = ctype[k]
        e["impr"] += r.metrics.impressions
        e["clicks"] += r.metrics.clicks
        e["cost"] += r.metrics.cost_micros / 1e6
        e["conv"] += r.metrics.conversions
        e["all_conv"] += r.metrics.all_conversions
    ct = {f"{k[0]}|{k[1]}": {**v, "cost": round(v["cost"], 2),
                             "conv": round(v["conv"], 2),
                             "all_conv": round(v["all_conv"], 2)}
          for k, v in ctype.items()}
    out["click_type_by_campaign"] = ct
    for k, v in sorted(ct.items(), key=lambda z: -z[1]["cost"]):
        if v["clicks"] or v["cost"]:
            print(f"     {k:44s} impr={v['impr']:>5d} clicks={v['clicks']:>3d} "
                  f"cost=${v['cost']:>8,.2f} conv={v['conv']:.1f} all_conv={v['all_conv']:.1f}")

    # local action conversion actions detail
    print("\n  Google-hosted Local action conversions (2026-08-01..2026-08-27):")
    la = []
    for r in q(c, f"""SELECT campaign.id, segments.conversion_action_name,
                      segments.conversion_action_category,
                      metrics.conversions, metrics.all_conversions
                      FROM campaign WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-27'
                        AND metrics.all_conversions > 0"""):
        la.append({"campaign": NAME[str(r.campaign.id)],
                   "action": r.segments.conversion_action_name,
                   "category": E(r.segments.conversion_action_category),
                   "conversions": round(r.metrics.conversions, 2),
                   "all_conversions": round(r.metrics.all_conversions, 2)})
    agg_la = defaultdict(lambda: {"conversions": 0.0, "all_conversions": 0.0,
                                  "campaigns": []})
    for x in la:
        e = agg_la[x["action"]]
        e["conversions"] += x["conversions"]
        e["all_conversions"] += x["all_conversions"]
        e["campaigns"].append(f"{x['campaign']}={x['all_conversions']}")
    out["conversion_actions_august"] = {
        k: {"conversions": round(v["conversions"], 2),
            "all_conversions": round(v["all_conversions"], 2),
            "campaigns": v["campaigns"]} for k, v in agg_la.items()}
    for k, v in sorted(agg_la.items(), key=lambda z: -z[1]["all_conversions"]):
        print(f"     {k:52s} conv={v['conversions']:>5.1f} all={v['all_conversions']:>5.1f} "
              f"{v['campaigns']}")

    # =====================================================================
    # 4. HANOVER
    # =====================================================================
    print("\n== 4. HANOVER NEGATIVE ==")
    members = []
    for r in q(c, f"""SELECT shared_criterion.resource_name, shared_criterion.criterion_id,
                      shared_criterion.keyword.text, shared_criterion.keyword.match_type,
                      shared_set.id, shared_set.name FROM shared_criterion
                      WHERE shared_set.id = {ACCOUNT_SET}"""):
        members.append({"resource_name": r.shared_criterion.resource_name,
                        "criterion_id": str(r.shared_criterion.criterion_id),
                        "text": r.shared_criterion.keyword.text,
                        "match": E(r.shared_criterion.keyword.match_type),
                        "set_id": str(r.shared_set.id), "set_name": r.shared_set.name})
    han = [m for m in members if m["text"].lower() == "hanover"]
    out["account_list_members"] = members
    out["hanover_member"] = han
    print(f"  account-level list members: {len(members)}")
    print(f"  hanover member: {json.dumps(han, indent=2)}")

    # anything else blocking Hanover
    others = [m for m in members
              if m["text"].lower() != "hanover"
              and blocks(m["text"], m["match"], "ac repair hanover md")[0]]
    print(f"  other account-level negatives that also block 'ac repair hanover md': "
          f"{[(m['text'], m['match']) for m in others] or 'NONE'}")
    out["other_negatives_blocking_hanover"] = others

    # geo target confirmation
    geo = []
    for r in q(c, """SELECT geo_target_constant.id, geo_target_constant.name,
                     geo_target_constant.canonical_name, geo_target_constant.target_type,
                     geo_target_constant.status FROM geo_target_constant
                     WHERE geo_target_constant.resource_name = 'geoTargetConstants/1018614'"""):
        g = r.geo_target_constant
        geo.append({"id": str(g.id), "name": g.name, "canonical": g.canonical_name,
                    "type": E(g.target_type), "status": E(g.status)})
    targeted = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id,
                      campaign_criterion.negative,
                      campaign_criterion.location.geo_target_constant
                      FROM campaign_criterion WHERE campaign.id IN ({IN5})
                        AND campaign_criterion.type='LOCATION'
                        AND campaign_criterion.status != 'REMOVED'"""):
        if r.campaign_criterion.location.geo_target_constant.endswith("/1018614"):
            targeted.append({"campaign": NAME[str(r.campaign.id)],
                             "criterion_id": str(r.campaign_criterion.criterion_id),
                             "negative": r.campaign_criterion.negative})
    out["hanover_geo_constant"] = geo
    out["hanover_targeted_on"] = targeted
    print(f"  geo constant 1018614: {geo}")
    print(f"  Hanover targeted on {len(targeted)} of the five campaigns: "
          f"{[t['campaign'] for t in targeted]}")

    # observed Hanover search terms
    st = json.loads((SNAP / "search-terms-2026-08-27.json").read_text(encoding="utf-8"))
    han_terms = [v for v in st["verdicts"] if "hanover" in v["search_term"].lower()]
    out["hanover_observed_terms"] = han_terms
    print(f"  observed search terms containing 'hanover': {len(han_terms)}")

    # would removing hanover unblock anything harmful?
    kws = []
    for r in q(c, f"""SELECT campaign.id, ad_group_criterion.keyword.text,
                      ad_group_criterion.keyword.match_type FROM ad_group_criterion
                      WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type='KEYWORD'
                        AND ad_group_criterion.status!='REMOVED'
                        AND ad_group_criterion.negative=FALSE
                        AND ad_group.status!='REMOVED'"""):
        kws.append({"campaign": NAME[str(r.campaign.id)],
                    "text": r.ad_group_criterion.keyword.text,
                    "match": E(r.ad_group_criterion.keyword.match_type)})
    out["live_keywords"] = kws
    print(f"  live positive keywords: {len(kws)}")
    print(f"  hanover blocks any active keyword: "
          f"{[k['text'] for k in kws if blocks('hanover', 'BROAD', k['text'])[0]] or 'NONE'}")

    # =====================================================================
    # 5. SITELINKS - FRESH ASSOCIATION READ
    # =====================================================================
    print("\n== 5. SITELINK VERIFICATION (fresh) ==")
    sl_assoc = []
    for r in q(c, f"""SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type,
                      campaign_asset.status, campaign_asset.source,
                      asset.id, asset.sitelink_asset.link_text, asset.final_urls
                      FROM campaign_asset WHERE campaign.id IN ({IN5})
                        AND campaign_asset.field_type = 'SITELINK'"""):
        sl_assoc.append({"campaign_id": str(r.campaign.id),
                         "campaign": NAME[str(r.campaign.id)],
                         "asset_id": str(r.asset.id),
                         "link_text": r.asset.sitelink_asset.link_text,
                         "final_urls": list(r.asset.final_urls),
                         "association_status": E(r.campaign_asset.status),
                         "source": E(r.campaign_asset.source)})
    active = [x for x in sl_assoc if x["association_status"] != "REMOVED"]
    out["sitelink_associations"] = sl_assoc
    out["active_sitelink_associations"] = active
    print(f"  campaign_asset SITELINK rows: {len(sl_assoc)}  active: {len(active)}")
    uniq = {}
    for x in active:
        uniq.setdefault(x["asset_id"], {"link_text": x["link_text"],
                                        "final_urls": x["final_urls"],
                                        "campaigns": []})["campaigns"].append(x["campaign"])
    offer, mainsite, other = [], [], []
    for aid, v in sorted(uniq.items(), key=lambda z: z[1]["link_text"]):
        url = v["final_urls"][0] if v["final_urls"] else ""
        bucket = ("offer subdomain" if "offer.ambientcoolingandheating.com" in url
                  else "MAIN WEBSITE" if "ambientcoolingandheating.com" in url
                  else "other")
        (offer if bucket == "offer subdomain" else
         mainsite if bucket == "MAIN WEBSITE" else other).append((aid, v, url))
        print(f"     {aid} {v['link_text']:24s} [{bucket:15s}] {url}")
        print(f"        on {len(v['campaigns'])} campaigns: {v['campaigns']}")
    out["sitelink_summary"] = {
        "distinct_active_sitelinks": len(uniq),
        "pointing_to_offer_subdomain": len(offer),
        "pointing_to_main_website": len(mainsite),
        "other": len(other),
        "main_website_sitelinks": [{"asset_id": a, "link_text": v["link_text"],
                                    "url": u} for a, v, u in mainsite],
    }
    print(f"\n  offer subdomain: {len(offer)} | MAIN WEBSITE: {len(mainsite)} | other: {len(other)}")
    print(f"  CLICKUP CLAIM 'every sitelink points to the paid offer pages' is "
          f"{'FALSE' if mainsite else 'TRUE'}")

    write(SNAP / f"reverification-{STAMP}.json", out)
    return out


if __name__ == "__main__":
    main()
