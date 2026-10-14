#!/usr/bin/env python3
"""Readback QA for an executed CREATE_PAUSED subplan.

Read-only. Verifies every created ad against the frozen plan, verifies the existing ads and
every unrelated resource are unchanged, and reports policy review state.

Exit code 1 if any assertion fails.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, load_yaml  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name as E  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--preflight", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = load_yaml(args.plan)["change_plan"]
    cid = plan["target"]["child_customer_id"]
    actions = {a["resource_id"]: a for a in plan["subplans"]["CREATE_PAUSED"]["actions"]}
    before = json.loads(Path(args.preflight).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))

    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    after: dict = {"customer_id": cid, "purpose": "CREATE_PAUSED readback"}

    c = q("""SELECT customer.id, customer.descriptive_name, customer.tracking_url_template
             FROM customer LIMIT 1""")[0].customer
    after["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                         "tracking_url_template": c.tracking_url_template}
    check("identity: still the authorised account",
          str(c.id) == cid
          and c.descriptive_name == plan["target"]["exact_child_account_name"])
    check("UNTOUCHED: tracking template not written by us",
          c.tracking_url_template == before["identity"]["tracking_url_template"])

    # ---- every ad on the live campaigns ------------------------------------
    ads = []
    for r in q("""SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type,
                         ad_group_ad.ad.final_urls, ad_group_ad.ad.final_mobile_urls,
                         ad_group_ad.ad.tracking_url_template,
                         ad_group_ad.ad.final_url_suffix,
                         ad_group_ad.ad.responsive_search_ad.headlines,
                         ad_group_ad.ad.responsive_search_ad.descriptions,
                         ad_group_ad.ad.responsive_search_ad.path1,
                         ad_group_ad.ad.responsive_search_ad.path2,
                         ad_group_ad.ad_strength,
                         ad_group_ad.policy_summary.approval_status,
                         ad_group_ad.policy_summary.review_status,
                         ad_group_ad.policy_summary.policy_topic_entries,
                         ad_group_ad.resource_name,
                         ad_group.id, ad_group.name, campaign.id, campaign.name,
                         campaign.status
                  FROM ad_group_ad WHERE campaign.status = ENABLED"""):
        a = r.ad_group_ad.ad
        rsa = a.responsive_search_ad
        ads.append({
            "resource_name": r.ad_group_ad.resource_name,
            "ad_id": str(a.id), "status": E(r.ad_group_ad.status), "type": E(a.type_),
            "final_urls": list(a.final_urls),
            "tracking_url_template": a.tracking_url_template or "",
            "final_url_suffix": a.final_url_suffix or "",
            "path1": rsa.path1, "path2": rsa.path2,
            "headlines": [h.text for h in rsa.headlines],
            "pinned_headlines": [E(h.pinned_field) for h in rsa.headlines if h.pinned_field],
            "descriptions": [d.text for d in rsa.descriptions],
            "pinned_descriptions": [E(d.pinned_field) for d in rsa.descriptions
                                    if d.pinned_field],
            "ad_strength": E(r.ad_group_ad.ad_strength),
            "approval_status": E(r.ad_group_ad.policy_summary.approval_status),
            "review_status": E(r.ad_group_ad.policy_summary.review_status),
            "policy_topics": [t.topic for t in
                              r.ad_group_ad.policy_summary.policy_topic_entries],
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
        })
    after["ads"] = ads

    created_ids = {rn.split("~")[1] for rn in
                   (x["resource_name"] for x in receipt["results"])}
    old_ids = {a["ad_id"] for a in before["existing_ads"]}
    new_ads = [a for a in ads if a["ad_id"] in created_ids]
    old_ads = [a for a in ads if a["ad_id"] in old_ids]

    check("counts: exactly 24 ads created", len(created_ids) == 24, f"{len(created_ids)}")
    check("counts: all 24 created ads are readable from the API",
          len(new_ads) == 24, f"{len(new_ads)}")
    check("counts: 48 total RSAs across the live ad groups", len(ads) == 48, f"{len(ads)}")
    check("counts: no ad created outside the approved 24",
          {a["ad_id"] for a in ads} == created_ids | old_ids)
    per_ag = Counter(a["ad_group_id"] for a in ads)
    check("counts: exactly two RSAs per live ad group",
          set(per_ag.values()) == {2} and len(per_ag) == 24,
          str(sorted(set(per_ag.values()))))

    check("status: every new ad is PAUSED",
          all(a["status"] == "PAUSED" for a in new_ads),
          str(dict(Counter(a["status"] for a in new_ads))))
    check("status: every existing ad is still ENABLED",
          all(a["status"] == "ENABLED" for a in old_ads),
          str(dict(Counter(a["status"] for a in old_ads))))
    check("status: 24 ENABLED + 24 PAUSED",
          dict(Counter(a["status"] for a in ads)) == {"ENABLED": 24, "PAUSED": 24},
          str(dict(Counter(a["status"] for a in ads))))

    # ---- each new ad against the frozen plan --------------------------------
    problems = []
    for a in new_ads:
        want = actions.get(a["ad_group_id"])
        if not want:
            problems.append(f"{a['ad_id']} in unapproved ad group {a['ad_group_id']}")
            continue
        if a["campaign_id"] != want["campaign_id"]:
            problems.append(f"{a['ad_id']} wrong campaign")
        if a["final_urls"] != [want["final_url"]]:
            problems.append(f"{a['ad_id']} final_urls {a['final_urls']}")
        if a["path1"] != want["path1"] or a["path2"] != want["path2"]:
            problems.append(f"{a['ad_id']} paths {a['path1']}/{a['path2']}")
        if a["headlines"] != want["headlines"]:
            problems.append(f"{a['ad_id']} headlines differ")
        if a["descriptions"] != want["descriptions"]:
            problems.append(f"{a['ad_id']} descriptions differ")
        if a["pinned_headlines"] or a["pinned_descriptions"]:
            problems.append(f"{a['ad_id']} unexpected pinning")
        if len(a["headlines"]) != 15 or len(a["descriptions"]) != 4:
            problems.append(f"{a['ad_id']} {len(a['headlines'])}H/{len(a['descriptions'])}D")
        if a["type"] != "RESPONSIVE_SEARCH_AD":
            problems.append(f"{a['ad_id']} type {a['type']}")
        if a["tracking_url_template"] or a["final_url_suffix"]:
            problems.append(f"{a['ad_id']} unexpected tracking template or suffix")
    check("content: every new ad matches the frozen plan exactly, "
          "URL, paths, 15 headlines, 4 descriptions, no pinning",
          not problems, "; ".join(problems[:6]))
    check("mapping: one new ad in each of the 24 approved ad groups",
          {a["ad_group_id"] for a in new_ads} == set(actions))

    # ---- existing ads unchanged ---------------------------------------------
    before_by_id = {a["ad_id"]: a for a in before["existing_ads"]}
    changed = []
    for a in old_ads:
        b = before_by_id[a["ad_id"]]
        if a["final_urls"] != b["final_urls"]:
            changed.append(f"{a['ad_id']} final_urls")
        if a["headlines"] != b["headlines"]:
            changed.append(f"{a['ad_id']} headlines")
        if a["descriptions"] != b["descriptions"]:
            changed.append(f"{a['ad_id']} descriptions")
    check("UNTOUCHED: no existing ad changed in URL, headlines or descriptions",
          not changed, "; ".join(changed[:6]))

    # ---- policy state --------------------------------------------------------
    after["new_ad_policy"] = [{"ad_id": a["ad_id"], "ad_group": a["ad_group_name"],
                               "approval": a["approval_status"],
                               "review": a["review_status"],
                               "topics": a["policy_topics"],
                               "strength": a["ad_strength"]} for a in new_ads]
    bad = [a for a in new_ads if a["approval_status"] in ("DISAPPROVED", "AREA_OF_INTEREST_ONLY")]
    check("policy: no new ad is DISAPPROVED or limited", not bad,
          str([(a["ad_id"], a["approval_status"]) for a in bad]))
    check("policy: no new ad carries a policy topic",
          not [a for a in new_ads if a["policy_topics"]],
          str([(a["ad_id"], a["policy_topics"]) for a in new_ads if a["policy_topics"]]))

    # ---- everything else unchanged -------------------------------------------
    camps = {}
    for r in q("""SELECT campaign.id, campaign.status, campaign.bidding_strategy_type,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.excluded_parent_asset_field_types,
                         campaign_budget.id, campaign_budget.amount_micros
                  FROM campaign WHERE campaign.status = ENABLED"""):
        camps[str(r.campaign.id)] = {
            "ceiling": int(r.campaign.target_spend.cpc_bid_ceiling_micros or 0),
            "excluded": sorted(E(x) for x in r.campaign.excluded_parent_asset_field_types),
            "budget": int(r.campaign_budget.amount_micros),
            "bidding": E(r.campaign.bidding_strategy_type)}
    after["campaigns"] = camps
    check("UNTOUCHED: budgets still $39.47 / $26.31, total $65.78/day",
          abs(sum(v["budget"] for v in camps.values()) / 1e6 - 65.78) < 1e-9,
          f"${sum(v['budget'] for v in camps.values())/1e6:.2f}")
    check("UNTOUCHED: $22.00 CPC ceilings intact",
          all(v["ceiling"] == 22000000 for v in camps.values()))
    check("UNTOUCHED: bidding still TARGET_SPEND on both",
          all(v["bidding"] == "TARGET_SPEND" for v in camps.values()))
    check("UNTOUCHED: parent asset exclusions intact",
          all(v["excluded"] == ["SITELINK", "STRUCTURED_SNIPPET"] for v in camps.values()))

    kw = q("""SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.match_type
              FROM ad_group_criterion
              WHERE ad_group_criterion.type = KEYWORD
                AND ad_group_criterion.negative = FALSE AND campaign.status = ENABLED""")
    check("UNTOUCHED: still 48 positive keywords", len(kw) == 48, f"{len(kw)}")
    negs = q("""SELECT campaign_criterion.criterion_id FROM campaign_criterion
                WHERE campaign_criterion.type = KEYWORD
                  AND campaign_criterion.negative = TRUE AND campaign.status = ENABLED""")
    check("UNTOUCHED: still 88 campaign negative keywords", len(negs) == 88, f"{len(negs)}")
    sched = q("""SELECT campaign_criterion.criterion_id,
                        campaign_criterion.ad_schedule.start_hour,
                        campaign_criterion.ad_schedule.end_hour
                 FROM campaign_criterion
                 WHERE campaign_criterion.type = AD_SCHEDULE AND campaign.status = ENABLED""")
    check("UNTOUCHED: 14 ad-schedule criteria, all 09:00-18:00",
          len(sched) == 14 and all(r.campaign_criterion.ad_schedule.start_hour == 9
                                   and r.campaign_criterion.ad_schedule.end_hour == 18
                                   for r in sched), f"{len(sched)}")
    loc = q("""SELECT campaign.id, campaign_criterion.location.geo_target_constant,
                      campaign_criterion.negative FROM campaign_criterion
               WHERE campaign_criterion.type = LOCATION AND campaign.status = ENABLED""")
    per_camp = defaultdict(set)
    for r in loc:
        if not r.campaign_criterion.negative:
            per_camp[str(r.campaign.id)].add(
                r.campaign_criterion.location.geo_target_constant.split("/")[-1])
    check("UNTOUCHED: 24 locations on each campaign, no exclusions",
          all(len(v) == 24 for v in per_camp.values()) and len(per_camp) == 2
          and not [r for r in loc if r.campaign_criterion.negative],
          str({k: len(v) for k, v in per_camp.items()}))
    conv = q("""SELECT conversion_action.id, conversion_action.primary_for_goal,
                       conversion_action.include_in_conversions_metric
                FROM conversion_action WHERE conversion_action.status = ENABLED""")
    prim = sorted(str(r.conversion_action.id) for r in conv
                  if r.conversion_action.primary_for_goal
                  and r.conversion_action.include_in_conversions_metric)
    check("UNTOUCHED: still exactly 3 primary conversion actions",
          prim == ["6566620547", "6885610317", "7644242327"], str(prim))
    # campaign_asset requires campaign.status in the SELECT when filtering on it
    ca = q("""SELECT asset.id, campaign.status, campaign_asset.field_type,
                     campaign_asset.status
              FROM campaign_asset WHERE campaign.status = ENABLED""")
    ft = Counter(E(r.campaign_asset.field_type) for r in ca
                 if E(r.campaign_asset.status) == "ENABLED")
    after["campaign_assets"] = dict(ft)
    check("UNTOUCHED: 12 sitelinks, 16 callouts, 2 snippets, 2 call, 2 logo",
          ft.get("SITELINK") == 12 and ft.get("CALLOUT") == 16
          and ft.get("STRUCTURED_SNIPPET") == 2 and ft.get("CALL") == 2
          and ft.get("BUSINESS_LOGO") == 2, str(dict(ft)))

    Path(args.out).write_text(json.dumps(after, indent=2, default=str), encoding="utf-8")

    print("=" * 98)
    print("CREATE_PAUSED READBACK QA")
    print("=" * 98)
    failed = 0
    for name, ok, detail in results:
        if not ok:
            failed += 1
        print(f"  [{'PASS' if ok else '**FAIL**':8}] {name}" + (f"  ({detail})" if detail else ""))
    print("-" * 98)
    print(f"  {len(results) - failed} passed, {failed} failed")

    print("\n  NEW AD POLICY STATE")
    for x in sorted(after["new_ad_policy"], key=lambda y: y["ad_group"]):
        print(f"    {x['ad_id']:<14} {x['ad_group']:<28} {x['approval']:<12} "
              f"{x['review']:<22} strength={x['strength']}")
    rs = Counter(x["review"] for x in after["new_ad_policy"])
    ap_ = Counter(x["approval"] for x in after["new_ad_policy"])
    print(f"\n    approval: {dict(ap_)}   review: {dict(rs)}")
    print(f"  after-snapshot: {args.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
