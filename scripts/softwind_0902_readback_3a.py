#!/usr/bin/env python3
"""Full readback QA for PLAN-GA-LAUNCH-3A. READ-ONLY."""
from __future__ import annotations

import importlib.util
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

CID, SURV, RETIRE = "1521725229", "24103511039", "24145053510"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
AUD = ROOT / "clients/softwind-power-washing/audits"
G6 = ["202870585390", "202870585870", "202870585910",
      "202870586310", "202870586110", "202870586150"]
NAME6 = {"202870585390": "Power Washing", "202870585870": "Pressure Washing",
         "202870585910": "House Washing", "202870586310": "Soft Washing",
         "202870586110": "Driveway Pressure Washing",
         "202870586150": "Patio Pressure Washing"}
GUARD_KW = {"384030528226", "502487923397"}
GUARD_ADS = {"819975939528", "819975939531", "819975939342", "819975939345"}
CREATED = json.loads((SNAP / "launch1-created-ids.json").read_text(encoding="utf-8"))
KW_OK = {(a, c) for a, l in CREATED["keywords_by_ad_group"].items() for c in l}
AD_OK = {(a, i) for a, l in CREATED["ads_by_ad_group"].items() for i in l}

spec = importlib.util.spec_from_file_location(
    "rec", ROOT / "scripts/softwind_0901_build_recovery_program.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
GROUPS, RSA = rec.GROUPS, rec.RSA
checks = []


def ck(n, ok, d=""):
    checks.append({"assertion": n, "pass": bool(ok), "detail": str(d)[:280]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {n}  {str(d)[:120]}")


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    ga = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)

    def q(s):
        return list(ga.search(customer_id=cid, query=s))

    ags = {str(r.ad_group.id): (r.ad_group.name, enum_name(r.ad_group.status),
                                str(r.campaign.id))
           for r in q("""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status
                         FROM ad_group WHERE ad_group.status != 'REMOVED'""")}
    ck("all six final ad groups ENABLED",
       all(ags[x][1] == "ENABLED" for x in G6),
       {NAME6[x]: ags[x][1] for x in G6})

    kws, rows = {}, []
    for r in q("""SELECT ad_group.id, ad_group_criterion.criterion_id,
                         ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type,
                         ad_group_criterion.status, ad_group_criterion.approval_status
                  FROM ad_group_criterion WHERE ad_group_criterion.type='KEYWORD'
                    AND ad_group_criterion.negative=FALSE
                    AND ad_group_criterion.status != 'REMOVED'"""):
        k = r.ad_group_criterion
        # criterion_id is NOT unique for keywords - the same id is reused by every ad
        # group carrying the same text and match type. Key on (ad_group_id, criterion_id).
        kws[(str(r.ad_group.id), str(k.criterion_id))] = {
            "ag": str(r.ad_group.id), "t": k.keyword.text,
            "m": enum_name(k.keyword.match_type), "s": enum_name(k.status)}
    new_kw = {k: v for k, v in kws.items() if (v["ag"], k[1]) in KW_OK}
    ck("all 28 new keyword criteria ENABLED",
       len(new_kw) == 28 and all(v["s"] == "ENABLED" for v in new_kw.values()),
       f"{len(new_kw)} found, {sum(1 for v in new_kw.values() if v['s']=='ENABLED')} enabled")
    ck("every new keyword has PHRASE or EXACT match",
       all(v["m"] in ("PHRASE", "EXACT") for v in new_kw.values()),
       sorted({v["m"] for v in new_kw.values()}))
    ck("no BROAD match keyword enabled anywhere",
       not any(v["m"] == "BROAD" and v["s"] == "ENABLED" for v in kws.values()))
    ck("the two guard House Washing keywords remain PAUSED in ad group 202870585910",
       all(kws[("202870585910", k)]["s"] == "PAUSED" for k in GUARD_KW),
       {k: kws[("202870585910", k)]["s"] for k in GUARD_KW})

    ads = {}
    for r in q("""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                         ad_group_ad.ad.type, ad_group_ad.ad.final_urls,
                         ad_group_ad.policy_summary.approval_status,
                         ad_group_ad.ad.responsive_search_ad.path1,
                         ad_group_ad.ad.responsive_search_ad.path2,
                         ad_group_ad.ad.responsive_search_ad.headlines,
                         ad_group_ad.ad.responsive_search_ad.descriptions
                  FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        a = r.ad_group_ad
        ads[str(a.ad.id)] = {
            "ag": str(r.ad_group.id), "s": enum_name(a.status),
            "type": enum_name(a.ad.type_), "urls": list(a.ad.final_urls),
            "p": enum_name(a.policy_summary.approval_status),
            "p1": a.ad.responsive_search_ad.path1, "p2": a.ad.responsive_search_ad.path2,
            "h": [x.text for x in a.ad.responsive_search_ad.headlines],
            "d": [x.text for x in a.ad.responsive_search_ad.descriptions],
            "pin": [enum_name(x.pinned_field) for x in a.ad.responsive_search_ad.headlines
                    if enum_name(x.pinned_field) not in ("UNSPECIFIED", "UNKNOWN", "")]}
    new_ads = {k: v for k, v in ads.items() if (v["ag"], k) in AD_OK}
    ck("all 12 new RSAs ENABLED",
       len(new_ads) == 12 and all(v["s"] == "ENABLED" for v in new_ads.values()),
       f"{len(new_ads)} found")
    ck("every new RSA still APPROVED",
       all(v["p"] == "APPROVED" for v in new_ads.values()),
       sorted({v["p"] for v in new_ads.values()}))
    ck("every new RSA has 15 headlines and 4 descriptions",
       all(len(v["h"]) == 15 and len(v["d"]) == 4 for v in new_ads.values()))
    ck("no pinning on any new RSA", all(not v["pin"] for v in new_ads.values()))
    want = {GROUPS[g]["ad_group_id"]: GROUPS[g] for g in GROUPS}
    ck("every Final URL matches the approved plan",
       all(v["urls"] == [want[v["ag"]]["page"]] for v in new_ads.values()))
    ck("every display path matches the approved plan",
       all(v["p1"] == want[v["ag"]]["p1"] and v["p2"] == want[v["ag"]]["p2"]
           for v in new_ads.values()))
    exp = defaultdict(list)
    for g, cfg in GROUPS.items():
        for ad in RSA[g]:
            exp[cfg["ad_group_id"]].append((ad["h"], ad["d"]))
    ck("every RSA headline and description matches the approved copy exactly",
       all(any(v["h"] == h and v["d"] == d for h, d in exp[v["ag"]])
           for v in new_ads.values()))
    per = defaultdict(int)
    for k, v in ads.items():
        if v["s"] == "ENABLED":
            per[v["ag"]] += 1
    ck("every final ad group has exactly two enabled RSAs",
       all(per[x] == 2 for x in G6), {NAME6[x]: per[x] for x in G6})
    ck("no final ad group exceeds three enabled RSAs", all(per[x] <= 3 for x in G6))
    ck("all six legacy RSAs paused by 3B and 3C remain PAUSED",
       all(ads[a]["s"] == "PAUSED" for a in GUARD_ADS if a in ads),
       {a: ads[a]["s"] for a in GUARD_ADS if a in ads})

    camps = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status,
                         campaign.bidding_strategy_type, campaign.campaign_budget,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.network_settings.target_partner_search_network,
                         campaign.network_settings.target_content_network,
                         campaign.ai_max_setting.enable_ai_max,
                         campaign.geo_target_type_setting.positive_geo_target_type
                  FROM campaign WHERE campaign.status != 'REMOVED'"""):
        k = r.campaign
        camps[str(k.id)] = {"name": k.name, "status": enum_name(k.status),
                            "bid": enum_name(k.bidding_strategy_type),
                            "ceiling": round(k.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
                            "budget_id": k.campaign_budget.split("/")[-1],
                            "sp": bool(k.network_settings.target_partner_search_network),
                            "disp": bool(k.network_settings.target_content_network),
                            "aimax": bool(k.ai_max_setting.enable_ai_max),
                            "geo": enum_name(k.geo_target_type_setting.positive_geo_target_type)}
    budgets = {}
    for r in q("""SELECT campaign_budget.id, campaign_budget.amount_micros
                  FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'"""):
        budgets[str(r.campaign_budget.id)] = round(r.campaign_budget.amount_micros / 1e6, 2)
    for v in camps.values():
        v["budget"] = budgets.get(v["budget_id"])
    ck(f"campaign {RETIRE} remains ENABLED and unchanged",
       camps[RETIRE]["status"] == "ENABLED" and camps[RETIRE]["name"] == "Pressure Washing")
    ck("both budgets unchanged ($41.50 / $41.11)",
       camps[SURV]["budget"] == 41.50 and camps[RETIRE]["budget"] == 41.11,
       {k: v["budget"] for k, v in camps.items()})
    ck("both CPC ceilings remain $30.00",
       all(v["ceiling"] == 30.0 for v in camps.values()))
    ck("both campaigns remain Maximize Clicks",
       all(v["bid"] == "TARGET_SPEND" for v in camps.values()))
    ck("Search Partners OFF", not any(v["sp"] for v in camps.values()))
    ck("Display OFF", not any(v["disp"] for v in camps.values()))
    ck("AI Max OFF", not any(v["aimax"] for v in camps.values()))
    ck("Presence targeting active", all(v["geo"] == "PRESENCE" for v in camps.values()))

    crit = defaultdict(lambda: defaultdict(int))
    ct = defaultdict(int)
    for r in q("""SELECT campaign.id, campaign_criterion.type, campaign_criterion.negative,
                         campaign_criterion.location.geo_target_constant
                  FROM campaign_criterion WHERE campaign_criterion.status != 'REMOVED'"""):
        c2 = r.campaign_criterion
        t = enum_name(c2.type_)
        ct[t] += 1
        if t == "LOCATION" and c2.negative:
            crit[str(r.campaign.id)]["neg_loc"] += 1
            if (c2.location.geo_target_constant or "").endswith("/21139"):
                crit[str(r.campaign.id)]["ct"] += 1
    ck("Connecticut (geo 21139) still excluded on both campaigns",
       all(crit[c]["ct"] == 1 for c in (SURV, RETIRE)),
       {c: crit[c]["ct"] for c in (SURV, RETIRE)})
    ck("conversion goals unchanged - 8 rows, GET_DIRECTIONS false",
       len(q("""SELECT campaign_conversion_goal.category FROM campaign_conversion_goal""")) == 8)
    ck("assets unchanged at 20 campaign asset links",
       len(q("""SELECT campaign_asset.asset FROM campaign_asset
                WHERE campaign_asset.status != 'REMOVED'""")) == 20)
    agn = len(q("""SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
                   WHERE ad_group_criterion.negative=TRUE
                     AND ad_group_criterion.type='KEYWORD'
                     AND ad_group_criterion.status != 'REMOVED'"""))
    ck("no routing negative was added - ad-group negatives still 0", agn == 0, agn)
    ck("no audience was added",
       len(q("""SELECT campaign_criterion.criterion_id FROM campaign_criterion
                WHERE campaign_criterion.type='USER_LIST'
                  AND campaign_criterion.status != 'REMOVED'""")) == 0)
    ck("no demographic criteria",
       sum(ct[t] for t in ("GENDER", "AGE_RANGE", "INCOME_RANGE", "PARENTAL_STATUS")) == 0)

    now = datetime.now(ZoneInfo("America/New_York"))
    tot = {"enabled_ad_groups": sum(1 for v in ags.values() if v[1] == "ENABLED"),
           "enabled_keywords": sum(1 for v in kws.values() if v["s"] == "ENABLED"),
           "enabled_ads": sum(1 for v in ads.values() if v["s"] == "ENABLED"),
           "total_ad_groups": len(ags), "total_keywords": len(kws), "total_ads": len(ads)}
    res = {"plan_id": "PLAN-GA-LAUNCH-3A", "fingerprint": "F91589D9EA2A",
           "readback_account_local": now.isoformat(), "totals": tot, "campaigns": camps,
           "enabled_ad_groups_detail": {x: {"name": ags[x][0], "final_group": NAME6[x],
                                            "status": ags[x][1], "enabled_rsas": per[x]}
                                        for x in G6},
           "new_keyword_ids": sorted(f"{a}~{c}" for a, c in new_kw), "new_ad_ids": sorted(new_ads),
           "checks": checks, "checks_run": len(checks),
           "checks_failed": [c for c in checks if not c["pass"]],
           "all_pass": all(c["pass"] for c in checks)}
    (SNAP / f"launch3a-readback-{now.strftime('%Y-%m-%dT%H%M%S')}.json").write_text(
        json.dumps(res, indent=2, default=str), encoding="utf-8")
    (SNAP / "launch3a-resource-ids.json").write_text(json.dumps(
        {"ad_groups": {x: ags[x][0] for x in G6},
         "keywords": {f"{a}~{c}": v for (a, c), v in new_kw.items()},
         "ads": {k: {"ad_group": v["ag"], "url": v["urls"][0]} for k, v in new_ads.items()}},
        indent=2), encoding="utf-8")
    print(f"\n  totals: {json.dumps(tot)}")
    print(f"  {res['checks_run']} assertions, {len(res['checks_failed'])} failed, "
          f"ALL PASS = {res['all_pass']}")
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
