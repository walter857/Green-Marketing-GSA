#!/usr/bin/env python3
"""Campaign architecture + BOFU intent review for Softwind Power Washing.

Fresh read of the renamed campaigns, full ad-group and keyword inventory, query
ownership matrix, and cross-campaign eligibility. Answers whether renaming the
campaigns produced real traffic separation.

SELECT statements only. Constructs no operation, calls no mutate service.
"""
from __future__ import annotations

import json
import re
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
EXPECT_NAME = "Softwind Power Washing - Live"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
LO, HI = "2026-07-01", "2026-08-31"

MISSPELLINGS = [
    "preassure", "presure", "pressuer", "pressue", "powerwashng", "powerwahing",
    "washng", "wahing", "wasing", "pressur ", "poweer", "powr",
]


def mic(v):
    return round(int(v) / 1_000_000, 4)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    now = datetime.now(ZoneInfo("America/New_York"))

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    # ---------- identity ----------
    c = q("""SELECT customer.id, customer.descriptive_name, customer.currency_code,
                    customer.time_zone, customer.manager, customer.test_account,
                    customer.status FROM customer LIMIT 1""")[0].customer
    if c.descriptive_name != EXPECT_NAME or normalize_customer_id(c.id) != CID \
            or c.manager or c.test_account:
        print("IDENTITY GATE FAILED"); return 2
    print(f"IDENTITY GATE: PASS  {c.descriptive_name} | {c.id} | manager={c.manager} | "
          f"test={c.test_account} | {enum_name(c.status)} | {c.currency_code} | {c.time_zone}")
    print(f"Account local: {now.isoformat()}\n")

    out = {"generated_account_local": now.isoformat(), "mode": "READ-ONLY"}

    # ---------- campaigns, names verified fresh ----------
    budgets = {str(r.campaign_budget.id): mic(r.campaign_budget.amount_micros)
               for r in q("""SELECT campaign_budget.id, campaign_budget.amount_micros
                             FROM campaign_budget
                             WHERE campaign_budget.status != 'REMOVED'""")}
    camps = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
                         campaign.primary_status, campaign.primary_status_reasons,
                         campaign.bidding_strategy_type,
                         campaign.bidding_strategy_system_status,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.campaign_budget,
                         campaign.geo_target_type_setting.positive_geo_target_type,
                         campaign.network_settings.target_search_network,
                         campaign.network_settings.target_content_network,
                         metrics.impressions, metrics.clicks, metrics.cost_micros,
                         metrics.average_cpc, metrics.ctr, metrics.conversions,
                         metrics.search_impression_share,
                         metrics.search_rank_lost_impression_share,
                         metrics.search_budget_lost_impression_share
                  FROM campaign WHERE campaign.status != 'REMOVED'"""):
        x, m = r.campaign, r.metrics
        bid = x.campaign_budget.split("/")[-1]
        name = x.name
        camps[str(x.id)] = {
            "campaign_id": str(x.id), "name": name,
            "name_lower": name.lower(),
            "misspellings_found": [w for w in MISSPELLINGS if w in name.lower()],
            "status": enum_name(x.status), "serving": enum_name(x.serving_status),
            "primary_status": enum_name(x.primary_status),
            "primary_status_reasons": [enum_name(z) for z in x.primary_status_reasons],
            "bidding": enum_name(x.bidding_strategy_type),
            "bidding_system_status": enum_name(x.bidding_strategy_system_status),
            "cpc_ceiling_micros": int(x.target_spend.cpc_bid_ceiling_micros),
            "cpc_ceiling_usd": mic(x.target_spend.cpc_bid_ceiling_micros),
            "budget_id": bid, "daily_budget_usd": budgets.get(bid),
            "geo_option": enum_name(x.geo_target_type_setting.positive_geo_target_type),
            "search_partners": bool(x.network_settings.target_search_network),
            "display": bool(x.network_settings.target_content_network),
            "impressions": int(m.impressions), "clicks": int(m.clicks),
            "cost_usd": mic(m.cost_micros), "avg_cpc_usd": mic(m.average_cpc),
            "ctr_pct": round(float(m.ctr) * 100, 2),
            "conversions": round(float(m.conversions), 2),
            "search_is_pct": round(float(m.search_impression_share) * 100, 2),
            "lost_is_rank_pct": round(float(m.search_rank_lost_impression_share) * 100, 2),
            "lost_is_budget_pct": round(float(m.search_budget_lost_impression_share) * 100, 2),
        }

    # criteria per campaign
    for r in q("""SELECT campaign.id, campaign_criterion.type, campaign_criterion.negative,
                         campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
                         campaign_criterion.ad_schedule.day_of_week,
                         campaign_criterion.ad_schedule.start_hour,
                         campaign_criterion.ad_schedule.end_hour
                  FROM campaign_criterion WHERE campaign_criterion.status != 'REMOVED'"""):
        ci = str(r.campaign.id)
        if ci not in camps:
            continue
        d = camps[ci].setdefault("_crit", {"loc": 0, "loc_neg": 0, "neg_kw": [], "sched": []})
        t = enum_name(r.campaign_criterion.type_)
        if t == "LOCATION":
            d["loc_neg" if r.campaign_criterion.negative else "loc"] += 1
        elif t == "KEYWORD" and r.campaign_criterion.negative:
            d["neg_kw"].append((r.campaign_criterion.keyword.text,
                                enum_name(r.campaign_criterion.keyword.match_type)))
        elif t == "AD_SCHEDULE":
            d["sched"].append(f"{enum_name(r.campaign_criterion.ad_schedule.day_of_week)[:3]}"
                              f" {r.campaign_criterion.ad_schedule.start_hour:02d}-"
                              f"{r.campaign_criterion.ad_schedule.end_hour:02d}")
    for ci, cc in camps.items():
        d = cc.pop("_crit", {"loc": 0, "loc_neg": 0, "neg_kw": [], "sched": []})
        cc["locations_targeted"] = d["loc"]
        cc["locations_excluded"] = d["loc_neg"]
        cc["negative_keywords"] = len(d["neg_kw"])
        cc["schedule"] = sorted(set(d["sched"]))

    # goals
    goals = defaultdict(list)
    for r in q("""SELECT campaign.id, campaign_conversion_goal.category,
                         campaign_conversion_goal.origin, campaign_conversion_goal.biddable
                  FROM campaign_conversion_goal"""):
        if r.campaign_conversion_goal.biddable:
            goals[str(r.campaign.id)].append(
                f"{enum_name(r.campaign_conversion_goal.category)}/"
                f"{enum_name(r.campaign_conversion_goal.origin)}")
    for ci in camps:
        camps[ci]["biddable_goals"] = sorted(goals.get(ci, []))

    # assets
    assets = defaultdict(lambda: defaultdict(int))
    for r in q("""SELECT campaign.id, campaign_asset.field_type FROM campaign_asset
                  WHERE campaign_asset.status != 'REMOVED'"""):
        assets[str(r.campaign.id)][enum_name(r.campaign_asset.field_type)] += 1
    for ci in camps:
        camps[ci]["assets"] = dict(assets.get(ci, {}))

    out["campaigns"] = camps

    # ---------- ad groups ----------
    ags = {}
    for r in q(f"""SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
                          ad_group.status, metrics.impressions, metrics.clicks,
                          metrics.cost_micros, metrics.average_cpc, metrics.ctr,
                          metrics.conversions
                   FROM ad_group"""):
        a, m = r.ad_group, r.metrics
        ags[str(a.id)] = {
            "ad_group_id": str(a.id), "ad_group_name": a.name,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "status": enum_name(a.status),
            "impressions": int(m.impressions), "clicks": int(m.clicks),
            "cost_usd": mic(m.cost_micros), "avg_cpc_usd": mic(m.average_cpc),
            "ctr_pct": round(float(m.ctr) * 100, 2),
            "conversions": round(float(m.conversions), 2),
            "keywords": [], "final_urls": set(), "rsa_count": 0,
        }
    for r in q("""SELECT ad_group.id, ad_group_ad.ad.final_urls, ad_group_ad.status
                  FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        g = ags.get(str(r.ad_group.id))
        if g:
            g["rsa_count"] += 1
            for u in r.ad_group_ad.ad.final_urls:
                g["final_urls"].add(u)

    kws = []
    for r in q("""SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
                         ad_group.status,
                         ad_group_criterion.criterion_id,
                         ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type,
                         ad_group_criterion.status,
                         ad_group_criterion.approval_status,
                         ad_group_criterion.system_serving_status,
                         ad_group_criterion.quality_info.quality_score,
                         ad_group_criterion.quality_info.creative_quality_score,
                         ad_group_criterion.quality_info.post_click_quality_score,
                         ad_group_criterion.quality_info.search_predicted_ctr,
                         metrics.impressions, metrics.clicks, metrics.cost_micros,
                         metrics.average_cpc, metrics.ctr, metrics.conversions
                  FROM keyword_view"""):
        k, m = r.ad_group_criterion, r.metrics
        serving = (enum_name(r.ad_group.status) == "ENABLED"
                   and enum_name(k.status) == "ENABLED")
        row = {
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "ad_group_status": enum_name(r.ad_group.status),
            "keyword": k.keyword.text, "match_type": enum_name(k.keyword.match_type),
            "kw_status": enum_name(k.status), "serving": serving,
            "approval": enum_name(k.approval_status),
            "eligibility": enum_name(k.system_serving_status),
            "quality_score": int(k.quality_info.quality_score or 0),
            "exp_ctr": enum_name(k.quality_info.search_predicted_ctr),
            "ad_relevance": enum_name(k.quality_info.creative_quality_score),
            "lp_experience": enum_name(k.quality_info.post_click_quality_score),
            "impressions": int(m.impressions), "clicks": int(m.clicks),
            "cost_usd": mic(m.cost_micros), "avg_cpc_usd": mic(m.average_cpc),
            "ctr_pct": round(float(m.ctr) * 100, 2),
            "conversions": round(float(m.conversions), 2),
        }
        kws.append(row)
        g = ags.get(str(r.ad_group.id))
        if g:
            g["keywords"].append(f"{k.keyword.text} [{enum_name(k.keyword.match_type)}]")
    for g in ags.values():
        g["final_urls"] = sorted(g["final_urls"])
        g["keyword_count"] = len(g["keywords"])
    out["ad_groups"] = list(ags.values())
    out["keywords"] = kws

    # ---------- search terms ----------
    terms = defaultdict(lambda: defaultdict(lambda: {
        "impr": 0, "clicks": 0, "cost": 0.0, "ad_group": "", "keyword": "",
        "kw_match": "", "term_match": ""}))
    for r in q(f"""SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
                          search_term_view.search_term, segments.keyword.info.text,
                          segments.keyword.info.match_type,
                          segments.search_term_match_type,
                          metrics.impressions, metrics.clicks, metrics.cost_micros
                   FROM search_term_view
                   WHERE segments.date BETWEEN '{LO}' AND '{HI}'"""):
        d = terms[r.search_term_view.search_term][str(r.campaign.id)]
        d["impr"] += int(r.metrics.impressions)
        d["clicks"] += int(r.metrics.clicks)
        d["cost"] += mic(r.metrics.cost_micros)
        d["ad_group"] = r.ad_group.name
        d["ad_group_id"] = str(r.ad_group.id)
        d["keyword"] = r.segments.keyword.info.text
        d["kw_match"] = enum_name(r.segments.keyword.info.match_type)
        d["term_match"] = enum_name(r.segments.search_term_match_type)
    out["search_terms"] = {t: {c: v for c, v in d.items()} for t, d in terms.items()}

    # ---------- console ----------
    print("=== CAMPAIGNS (names verified fresh) ===")
    for ci, cc in sorted(camps.items(), key=lambda x: -x[1]["impressions"]):
        print(f"\n  NAME: \"{cc['name']}\"   ID: {ci}")
        print(f"    misspellings detected: {cc['misspellings_found'] or 'none'}")
        print(f"    status={cc['status']}/{cc['serving']} primary={cc['primary_status']} "
              f"{cc['primary_status_reasons']}")
        print(f"    bidding={cc['bidding']} sys={cc['bidding_system_status']} "
              f"ceiling=${cc['cpc_ceiling_usd']} budget=${cc['daily_budget_usd']} ({cc['budget_id']})")
        print(f"    goals={cc['biddable_goals']}")
        print(f"    locations={cc['locations_targeted']}+{cc['locations_excluded']}excl "
              f"option={cc['geo_option']} negatives={cc['negative_keywords']}")
        print(f"    schedule={cc['schedule']}")
        print(f"    assets={cc['assets']}")
        print(f"    partners={cc['search_partners']} display={cc['display']}")
        print(f"    impr={cc['impressions']} clicks={cc['clicks']} ${cc['cost_usd']} "
              f"cpc=${cc['avg_cpc_usd']} ctr={cc['ctr_pct']}% conv={cc['conversions']}")
        print(f"    IS={cc['search_is_pct']}% lostRank={cc['lost_is_rank_pct']}% "
              f"lostBudget={cc['lost_is_budget_pct']}%")
        mine = [g for g in ags.values() if g["campaign_id"] == ci]
        en = [g for g in mine if g["status"] == "ENABLED"]
        pa = [g for g in mine if g["status"] == "PAUSED"]
        ek = [k for k in kws if k["campaign_id"] == ci and k["serving"]]
        pk = [k for k in kws if k["campaign_id"] == ci and not k["serving"]]
        print(f"    ad groups: {len(en)} enabled / {len(pa)} paused")
        print(f"    keywords: {len(ek)} serving / {len(pk)} dormant")
        urls = sorted({u for g in mine for u in g["final_urls"]})
        print(f"    final URLs ({len(urls)}):")
        for u in urls:
            print(f"       {u}")

    print("\n=== ENABLED AD GROUPS ===")
    print(f"{'campaign':22s} {'ad group':34s} {'id':14s} {'kw':3s} {'rsa':3s} "
          f"impr clk    cost    cpc   ctr%")
    for g in sorted(ags.values(), key=lambda x: (-x["cost_usd"], x["campaign_name"])):
        if g["status"] != "ENABLED":
            continue
        print(f"{g['campaign_name'][:22]:22s} {g['ad_group_name'][:34]:34s} "
              f"{g['ad_group_id']:14s} {g['keyword_count']:3d} {g['rsa_count']:3d} "
              f"{g['impressions']:4d} {g['clicks']:3d} {g['cost_usd']:7.2f} "
              f"{g['avg_cpc_usd']:6.2f} {g['ctr_pct']:6.2f}")
        print(f"{'':22s}   kw: {'; '.join(sorted(g['keywords']))[:110]}")
        print(f"{'':22s}   LP: {g['final_urls']}")

    print("\n=== SERVING KEYWORDS ===")
    print(f"{'campaign':22s} {'ad group':30s} {'keyword':34s} {'mt':6s} impr clk    cost "
          f"  cpc  QS  ctr/rel/lp")
    for k in sorted([x for x in kws if x["serving"]],
                    key=lambda x: (-x["cost_usd"], x["campaign_name"])):
        print(f"{k['campaign_name'][:22]:22s} {k['ad_group_name'][:30]:30s} "
              f"{k['keyword'][:34]:34s} {k['match_type'][:6]:6s} {k['impressions']:4d} "
              f"{k['clicks']:3d} {k['cost_usd']:7.2f} {k['avg_cpc_usd']:6.2f} "
              f"{k['quality_score'] or '-':>2} "
              f"{k['exp_ctr'][:5]}/{k['ad_relevance'][:5]}/{k['lp_experience'][:5]}")

    p = SNAP / f"architecture-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
