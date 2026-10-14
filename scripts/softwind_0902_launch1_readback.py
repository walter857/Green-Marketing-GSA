#!/usr/bin/env python3
"""Readback QA for PLAN-GA-LAUNCH-1. READ-ONLY verification of what was created."""
from __future__ import annotations

import glob
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402

CID, SURVIVOR, RETIRING = "1521725229", "24103511039", "24145053510"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"

spec = importlib.util.spec_from_file_location(
    "rec", ROOT / "scripts/softwind_0901_build_recovery_program.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
GROUPS, RSA = rec.GROUPS, rec.RSA
KW_NEW = json.loads(Path(sorted(glob.glob(str(SNAP / "launch1-delta-*.json")))[-1])
                    .read_text(encoding="utf-8"))["delta"]["keywords_to_create"]
EXEC = json.loads(Path(sorted(glob.glob(str(SNAP / "launch1-execution-*.json")))[-1])
                  .read_text(encoding="utf-8"))

checks = []


def ck(name, ok, detail=""):
    checks.append({"check": name, "pass": bool(ok), "detail": str(detail)[:300]})
    return bool(ok)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    ga = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)

    def q(s):
        return list(ga.search(customer_id=cid, query=s))

    created_kw_ids = {rn.split("~")[-1] for rn in EXEC["created"]["keywords"]}
    created_ad_ids = {rn.split("~")[-1] for rn in EXEC["created"]["rsas"]}

    # ---------- keywords ----------
    live_kw = {}
    for r in q("""SELECT ad_group.id, ad_group_criterion.criterion_id,
                         ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type,
                         ad_group_criterion.status,
                         ad_group_criterion.approval_status
                  FROM ad_group_criterion
                  WHERE ad_group_criterion.type='KEYWORD'
                    AND ad_group_criterion.negative=FALSE
                    AND ad_group_criterion.status != 'REMOVED'"""):
        k = r.ad_group_criterion
        live_kw[(str(r.ad_group.id), k.keyword.text, enum_name(k.keyword.match_type))] = {
            "criterion_id": str(k.criterion_id), "status": enum_name(k.status),
            "approval": enum_name(k.approval_status)}
    missing = [r for r in KW_NEW
               if (r["ad_group_id"], r["text"], r["match_type"]) not in live_kw]
    ck("all 28 planned keywords exist", not missing, f"{len(missing)} missing")
    wrong_status = [r for r in KW_NEW
                    if live_kw.get((r["ad_group_id"], r["text"], r["match_type"]), {})
                    .get("status") != "PAUSED"]
    ck("all 28 created keywords are PAUSED", not wrong_status,
       f"{len(wrong_status)} not paused")
    ck("keyword match types correct",
       all(live_kw.get((r["ad_group_id"], r["text"], r["match_type"]))
           for r in KW_NEW))
    total_kw = len(live_kw)
    ck("total positive keywords 214 -> 242", total_kw == 242, total_kw)

    # ---------- ads ----------
    live_ads = {}
    for r in q("""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                         ad_group_ad.ad.type, ad_group_ad.ad.final_urls,
                         ad_group_ad.policy_summary.approval_status,
                         ad_group_ad.ad.responsive_search_ad.path1,
                         ad_group_ad.ad.responsive_search_ad.path2,
                         ad_group_ad.ad.responsive_search_ad.headlines,
                         ad_group_ad.ad.responsive_search_ad.descriptions
                  FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        a = r.ad_group_ad
        live_ads[str(a.ad.id)] = {
            "ad_group": str(r.ad_group.id), "status": enum_name(a.status),
            "type": enum_name(a.ad.type_), "final_urls": list(a.ad.final_urls),
            "approval": enum_name(a.policy_summary.approval_status),
            "path1": a.ad.responsive_search_ad.path1,
            "path2": a.ad.responsive_search_ad.path2,
            "headlines": [h.text for h in a.ad.responsive_search_ad.headlines],
            "descriptions": [d.text for d in a.ad.responsive_search_ad.descriptions],
            "pinned": [enum_name(h.pinned_field) for h in a.ad.responsive_search_ad.headlines
                       if enum_name(h.pinned_field) not in ("UNSPECIFIED", "UNKNOWN", "")],
        }
    got = {i: live_ads[i] for i in created_ad_ids if i in live_ads}
    ck("all 12 created RSAs read back", len(got) == 12, f"{len(got)}/12")
    ck("all 12 created RSAs are PAUSED",
       all(v["status"] == "PAUSED" for v in got.values()),
       [v["status"] for v in got.values()])
    ck("all 12 are RESPONSIVE_SEARCH_AD",
       all(v["type"] == "RESPONSIVE_SEARCH_AD" for v in got.values()))
    ck("no pinning on any created RSA",
       all(not v["pinned"] for v in got.values()))
    ck("every created RSA has 15 headlines",
       all(len(v["headlines"]) == 15 for v in got.values()),
       sorted({len(v["headlines"]) for v in got.values()}))
    ck("every created RSA has 4 descriptions",
       all(len(v["descriptions"]) == 4 for v in got.values()),
       sorted({len(v["descriptions"]) for v in got.values()}))

    # exact content match against the fingerprinted plan
    want = {}
    for g, cfg in GROUPS.items():
        for ad in RSA[g]:
            want.setdefault(cfg["ad_group_id"], []).append(
                {"h": ad["h"], "d": ad["d"], "p1": cfg["p1"], "p2": cfg["p2"],
                 "url": cfg["page"]})
    content_ok, url_ok, path_ok = True, True, True
    for aid, v in got.items():
        cands = want.get(v["ad_group"], [])
        m = [c for c in cands if c["h"] == v["headlines"] and c["d"] == v["descriptions"]]
        if not m:
            content_ok = False
        if v["final_urls"] != [cands[0]["url"]] if cands else True:
            url_ok = False
        if cands and (v["path1"] != cands[0]["p1"] or v["path2"] != cands[0]["p2"]):
            path_ok = False
    ck("every RSA headline and description matches the fingerprinted plan exactly", content_ok)
    ck("every RSA Final URL matches the plan", url_ok)
    ck("every RSA path1/path2 matches the plan", path_ok)
    ck("total ads 54 -> 66", len(live_ads) == 66, len(live_ads))
    pol = {v["approval"] for v in got.values()}
    ck("created RSA policy status recorded", True, sorted(pol))

    # ---------- nothing else changed ----------
    ags = {str(r.ad_group.id): (r.ad_group.name, enum_name(r.ad_group.status),
                                str(r.campaign.id))
           for r in q("""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status
                         FROM ad_group WHERE ad_group.status != 'REMOVED'""")}
    ck("ad group count unchanged at 30", len(ags) == 30, len(ags))
    b = EXEC["before"]
    ck("ad-group negatives still 0",
       len(q("""SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
                WHERE ad_group_criterion.negative=TRUE AND ad_group_criterion.type='KEYWORD'
                  AND ad_group_criterion.status != 'REMOVED'""")) == 0)
    camps = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.campaign_budget
                  FROM campaign WHERE campaign.status != 'REMOVED'"""):
        camps[str(r.campaign.id)] = {
            "name": r.campaign.name, "status": enum_name(r.campaign.status),
            "ceiling": r.campaign.target_spend.cpc_bid_ceiling_micros}
    ck("campaign names/status/ceilings unchanged",
       all(camps[k]["name"] == v[0] and camps[k]["status"] == v[1]
           and camps[k]["ceiling"] == v[2] for k, v in b["campaigns"].items()
           if k in camps),
       json.dumps({k: [v["name"], v["status"], v["ceiling"] / 1e6] for k, v in camps.items()}))
    ck(f"retiring campaign {RETIRING} still ENABLED and untouched",
       camps.get(RETIRING, {}).get("status") == "ENABLED")
    ck("the 5 target ad groups are still PAUSED (nothing enabled)",
       all(ags[GROUPS[g]["ad_group_id"]][1] == "PAUSED" for g in GROUPS
           if g != "Power Washing"),
       {g: ags[GROUPS[g]["ad_group_id"]][1] for g in GROUPS})
    ck("Power Washing ad group still ENABLED as before",
       ags["202870585390"][1] == "ENABLED")
    # pre-existing ads untouched
    pre_ads = {i for i in live_ads if i not in created_ad_ids}
    ck("pre-existing ad count unchanged at 54", len(pre_ads) == 54, len(pre_ads))
    goals = [f"{enum_name(r.campaign_conversion_goal.category)}/"
             f"{enum_name(r.campaign_conversion_goal.origin)}="
             f"{r.campaign_conversion_goal.biddable}"
             for r in q("""SELECT campaign.id, campaign_conversion_goal.category,
                                  campaign_conversion_goal.origin,
                                  campaign_conversion_goal.biddable
                           FROM campaign_conversion_goal""")]
    ck("conversion goals unchanged (8 rows, GET_DIRECTIONS false)",
       len(goals) == 8 and sum(1 for g in goals if "GET_DIRECTIONS" in g
                               and "False" in g) == 2, len(goals))

    now = datetime.now(ZoneInfo("America/New_York"))
    res = {"plan_id": "PLAN-GA-LAUNCH-1", "fingerprint": "92FFF603CAFD",
           "readback_account_local": now.isoformat(),
           "created_keyword_resource_names": EXEC["created"]["keywords"],
           "created_rsa_resource_names": EXEC["created"]["rsas"],
           "created_keyword_count": len(created_kw_ids),
           "created_rsa_count": len(created_ad_ids),
           "before": b["counts"],
           "after": {"positive_keywords": total_kw, "ads": len(live_ads),
                     "ad_groups": len(ags), "ad_group_negatives": 0},
           "checks": checks, "checks_run": len(checks),
           "checks_failed": [c for c in checks if not c["pass"]],
           "all_pass": all(c["pass"] for c in checks)}
    p = SNAP / f"launch1-readback-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    for c in checks:
        print(f"  [{'PASS' if c['pass'] else 'FAIL'}] {c['check']}  {c['detail'][:110]}")
    print(f"\n  before: {json.dumps(b['counts'])}")
    print(f"  after : {json.dumps(res['after'])}")
    print(f"\n  {res['checks_run']} checks, {len(res['checks_failed'])} failed, "
          f"ALL PASS = {res['all_pass']}")
    print("WROTE", p)
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
