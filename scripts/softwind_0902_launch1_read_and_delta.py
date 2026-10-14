#!/usr/bin/env python3
"""Targeted implementation read + delta against the authoritative inventory.

Purpose: prevent duplicate resources and detect plan drift. NOT a performance audit.
SELECT statements only.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402

CID = "1521725229"
SURVIVOR = "24103511039"
RETIRING = "24145053510"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
BASE = "https://offer.softwindli.com"

# Authoritative final architecture (2026-09-01), reused not rebuilt.
TARGET = {
    "Power Washing": dict(ag="202870585390", page=f"{BASE}/power-washing-services-islip-west-islip-dix-hills/",
                          p1="power-washing", p2="free-quote",
                          texts=["power washing", "power washing near me", "power washing service",
                                 "power washing services near me", "power washing company near me"]),
    "Pressure Washing": dict(ag="202870585870", page=f"{BASE}/residential-pressure-washing/",
                             p1="pressure-wash", p2="residential",
                             texts=["pressure washing", "pressure washing near me",
                                    "residential pressure washing near me"]),
    "House Washing": dict(ag="202870585910", page=f"{BASE}/house-washing-company/",
                          p1="house-washing", p2="free-quote",
                          texts=["house washing near me", "house pressure washing near me",
                                 "house power washing near me", "exterior house washing near me"]),
    "Soft Washing": dict(ag="202870586310", page=f"{BASE}/soft-house-washing/",
                         p1="soft-washing", p2="house-washing",
                         texts=["soft house washing near me", "soft washing near me"]),
    "Driveway Pressure Washing": dict(ag="202870586110", page=f"{BASE}/driveway-pressure-washing/",
                                      p1="driveway", p2="pressure-wash",
                                      texts=["driveway pressure washing near me",
                                             "driveway power washing near me"]),
    "Patio Pressure Washing": dict(ag="202870586150", page=f"{BASE}/patio-power-washing/",
                                   p1="patio", p2="pressure-wash",
                                   texts=["patio pressure washing near me",
                                          "patio power washing near me",
                                          "concrete pressure washing near me"]),
}


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)

    def q(s):
        return list(svc.search(customer_id=cid, query=s))

    out = {"mode": "READ-ONLY", "generated": None}
    c = q("""SELECT customer.id, customer.descriptive_name, customer.manager,
                    customer.test_account, customer.status, customer.currency_code,
                    customer.time_zone FROM customer LIMIT 1""")[0].customer
    tz = c.time_zone or "America/New_York"
    now = datetime.now(ZoneInfo(tz))
    out["generated"] = now.isoformat()
    out["identity"] = {"name": c.descriptive_name, "id": str(c.id), "manager": bool(c.manager),
                       "test": bool(c.test_account), "status": enum_name(c.status),
                       "currency": c.currency_code, "tz": tz}
    gate = (c.descriptive_name == "Softwind Power Washing - Live" and str(c.id) == CID
            and not c.manager and not c.test_account and enum_name(c.status) == "ENABLED"
            and c.currency_code == "USD" and tz == "America/New_York")
    out["identity_gate_pass"] = gate
    if not gate:
        print("IDENTITY GATE FAILED", json.dumps(out["identity"], indent=2))
        return 2

    # ---------- campaign configuration ----------
    camps = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
                         campaign.bidding_strategy_type, campaign.campaign_budget,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.network_settings.target_partner_search_network,
                         campaign.network_settings.target_content_network,
                         campaign.ai_max_setting.enable_ai_max,
                         campaign.geo_target_type_setting.positive_geo_target_type
                  FROM campaign WHERE campaign.status != 'REMOVED'"""):
        k = r.campaign
        camps[str(k.id)] = {"name": k.name, "status": enum_name(k.status),
                            "serving": enum_name(k.serving_status),
                            "bidding": enum_name(k.bidding_strategy_type),
                            "cpc_ceiling_usd": round(k.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
                            "budget_id": k.campaign_budget.split("/")[-1],
                            "search_partners": bool(k.network_settings.target_partner_search_network),
                            "display": bool(k.network_settings.target_content_network),
                            "ai_max": bool(k.ai_max_setting.enable_ai_max),
                            "geo": enum_name(k.geo_target_type_setting.positive_geo_target_type)}
    for r in q("""SELECT campaign_budget.id, campaign_budget.amount_micros
                  FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'"""):
        for v in camps.values():
            if v["budget_id"] == str(r.campaign_budget.id):
                v["daily_budget_usd"] = round(r.campaign_budget.amount_micros / 1e6, 2)
    out["campaigns"] = camps

    # ---------- ad groups ----------
    ags = {}
    for r in q("""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status
                  FROM ad_group WHERE ad_group.status != 'REMOVED'"""):
        ags[str(r.ad_group.id)] = {"campaign": str(r.campaign.id), "name": r.ad_group.name,
                                   "status": enum_name(r.ad_group.status)}
    out["ad_group_count"] = len(ags)

    # ---------- positive keywords ----------
    kws = defaultdict(set)
    kw_status = {}
    for r in q("""SELECT ad_group.id, ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type, ad_group_criterion.status
                  FROM ad_group_criterion
                  WHERE ad_group_criterion.type='KEYWORD'
                    AND ad_group_criterion.negative=FALSE
                    AND ad_group_criterion.status != 'REMOVED'"""):
        k = r.ad_group_criterion
        key = (str(r.ad_group.id), k.keyword.text, enum_name(k.keyword.match_type))
        kws[str(r.ad_group.id)].add((k.keyword.text, enum_name(k.keyword.match_type)))
        kw_status[key] = enum_name(k.status)
    out["positive_keyword_objects_total"] = sum(len(v) for v in kws.values())

    # ---------- ads in the six target groups ----------
    ads = defaultdict(list)
    for r in q("""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                         ad_group_ad.ad.type, ad_group_ad.ad.final_urls
                  FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        ads[str(r.ad_group.id)].append({"ad_id": str(r.ad_group_ad.ad.id),
                                        "status": enum_name(r.ad_group_ad.status),
                                        "type": enum_name(r.ad_group_ad.ad.type_),
                                        "final_urls": list(r.ad_group_ad.ad.final_urls)})

    # ---------- negatives / assets / goals / locations / schedules ----------
    negs = defaultdict(int)
    locs = defaultdict(int)
    sched = defaultdict(int)
    for r in q("""SELECT campaign.id, campaign_criterion.type, campaign_criterion.negative
                  FROM campaign_criterion WHERE campaign_criterion.status != 'REMOVED'"""):
        t = enum_name(r.campaign_criterion.type_)
        if t == "KEYWORD" and r.campaign_criterion.negative:
            negs[str(r.campaign.id)] += 1
        elif t == "LOCATION":
            locs[str(r.campaign.id)] += 1
        elif t == "AD_SCHEDULE":
            sched[str(r.campaign.id)] += 1
    agneg = len(q("""SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
                     WHERE ad_group_criterion.negative=TRUE
                       AND ad_group_criterion.type='KEYWORD'
                       AND ad_group_criterion.status != 'REMOVED'"""))
    assets = defaultdict(int)
    for r in q("""SELECT campaign.id, campaign_asset.field_type FROM campaign_asset
                  WHERE campaign_asset.status != 'REMOVED'"""):
        assets[str(r.campaign.id)] += 1
    goals = defaultdict(list)
    for r in q("""SELECT campaign.id, campaign_conversion_goal.category,
                         campaign_conversion_goal.origin, campaign_conversion_goal.biddable
                  FROM campaign_conversion_goal"""):
        if r.campaign_conversion_goal.biddable:
            goals[str(r.campaign.id)].append(
                f"{enum_name(r.campaign_conversion_goal.category)}/"
                f"{enum_name(r.campaign_conversion_goal.origin)}")
    out["campaign_negatives"] = dict(negs)
    out["ad_group_negatives_total"] = agneg
    out["locations"] = dict(locs)
    out["ad_schedules"] = dict(sched)
    out["campaign_assets"] = dict(assets)
    out["biddable_goals"] = {k: sorted(v) for k, v in goals.items()}

    # ---------- DELTA ----------
    delta = {"ad_groups": [], "keywords_reuse": [], "keywords_to_create": [],
             "rsas_to_create": [], "conflicts": []}
    for name, cfg in TARGET.items():
        agid = cfg["ag"]
        live = ags.get(agid)
        row = {"final_group": name, "ad_group_id": agid,
               "exists": bool(live), "live_name": live["name"] if live else None,
               "live_status": live["status"] if live else None,
               "in_surviving_campaign": (live["campaign"] == SURVIVOR) if live else False,
               "action": "REUSE EXISTING" if live else "CREATE PAUSED"}
        if live and live["campaign"] != SURVIVOR:
            delta["conflicts"].append(f"{name}: ad group {agid} is in campaign "
                                      f"{live['campaign']}, not {SURVIVOR}")
        delta["ad_groups"].append(row)
        have = kws.get(agid, set())
        for t in cfg["texts"]:
            for mt in ("PHRASE", "EXACT"):
                rec = {"final_group": name, "ad_group_id": agid, "text": t, "match_type": mt,
                       "landing_page": cfg["page"]}
                if (t, mt) in have:
                    rec["existing_status"] = kw_status.get((agid, t, mt))
                    delta["keywords_reuse"].append(rec)
                else:
                    delta["keywords_to_create"].append(rec)
        existing_ads = [a for a in ads.get(agid, []) if a["status"] != "REMOVED"]
        for n in (1, 2):
            delta["rsas_to_create"].append({"final_group": name, "ad_group_id": agid,
                                            "rsa": f"RSA {n}", "final_url": cfg["page"],
                                            "path1": cfg["p1"], "path2": cfg["p2"],
                                            "existing_ads_in_group": len(existing_ads)})
    # duplicate-ownership guard across the WHOLE account
    owner = {}
    for name, cfg in TARGET.items():
        for t in cfg["texts"]:
            if t in owner:
                delta["conflicts"].append(f"DUPLICATE OWNER for '{t}'")
            owner[t] = name
    # any target text already living in a NON-owner ad group anywhere
    for agid, pairs in kws.items():
        for t, mt in pairs:
            if t in owner and agid != TARGET[owner[t]]["ag"]:
                delta["conflicts"].append(
                    f"text '{t}' [{mt}] also exists in ad group {agid} "
                    f"({ags.get(agid, {}).get('name')}, {ags.get(agid, {}).get('status')}) "
                    f"- owner is {owner[t]} ({TARGET[owner[t]]['ag']}). "
                    f"Displaced duplicate: retire later, do NOT touch now.")
    out["delta"] = delta
    out["counts"] = {
        "target_ad_groups": len(TARGET),
        "ad_groups_to_create": sum(1 for r in delta["ad_groups"] if r["action"] == "CREATE PAUSED"),
        "ad_groups_reused": sum(1 for r in delta["ad_groups"] if r["action"] == "REUSE EXISTING"),
        "unique_keyword_texts": len(owner),
        "keyword_objects_final": len(owner) * 2,
        "keyword_objects_reused": len(delta["keywords_reuse"]),
        "keyword_objects_to_create": len(delta["keywords_to_create"]),
        "rsas_to_create": len(delta["rsas_to_create"]),
        "total_new_objects": len(delta["keywords_to_create"]) + len(delta["rsas_to_create"]),
        "displaced_duplicate_notices": len([x for x in delta["conflicts"]
                                            if "Displaced duplicate" in x]),
        "blocking_conflicts": len([x for x in delta["conflicts"]
                                   if "Displaced duplicate" not in x]),
    }
    p = SNAP / f"launch1-delta-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "delta"}, indent=2, default=str))
    print("\nAD GROUPS:")
    for r in delta["ad_groups"]:
        print(f"  {r['ad_group_id']} {r['final_group']:26} exists={r['exists']} "
              f"status={r['live_status']} campaign_ok={r['in_surviving_campaign']} "
              f"-> {r['action']}  [{r['live_name']}]")
    print(f"\nKEYWORDS REUSED ({len(delta['keywords_reuse'])}):")
    for r in delta["keywords_reuse"]:
        print(f"  {r['ad_group_id']} {r['match_type']:6} {r['existing_status']:8} {r['text']}")
    print(f"\nKEYWORDS TO CREATE PAUSED ({len(delta['keywords_to_create'])}):")
    for r in delta["keywords_to_create"]:
        print(f"  {r['ad_group_id']} {r['match_type']:6} {r['text']}")
    print(f"\nCONFLICTS / NOTICES ({len(delta['conflicts'])}):")
    for x in delta["conflicts"]:
        print("  -", x)
    print("\nWROTE", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
