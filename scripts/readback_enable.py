#!/usr/bin/env python3
"""Readback QA for an executed ENABLE subplan. Read-only. Exit 1 on any failure."""
from __future__ import annotations

import argparse
import json
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
    ap.add_argument("--enable-plan", required=True)
    ap.add_argument("--phase2-plan", required=True)
    ap.add_argument("--preflight", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = load_yaml(args.enable_plan)["change_plan"]
    p2 = load_yaml(args.phase2_plan)["change_plan"]
    cid = plan["target"]["child_customer_id"]
    actions = plan["subplans"]["ENABLE"]["actions"]
    planned = {a["resource_id"]: a for a in p2["subplans"]["CREATE_PAUSED"]["actions"]}
    before = json.loads(Path(args.preflight).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))

    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    after: dict = {"customer_id": cid, "purpose": "ENABLE readback"}

    c = q("""SELECT customer.id, customer.descriptive_name, customer.tracking_url_template
             FROM customer LIMIT 1""")[0].customer
    after["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                         "tracking_url_template": c.tracking_url_template}
    check("identity: still the authorised account",
          str(c.id) == cid and c.descriptive_name == plan["target"]["exact_child_account_name"])
    check("UNTOUCHED: tracking template was not written",
          c.tracking_url_template == before["identity"]["tracking_url_template"])

    ads = []
    for r in q("""SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.resource_name,
                         ad_group_ad.ad.final_urls, ad_group_ad.ad.tracking_url_template,
                         ad_group_ad.ad.final_url_suffix,
                         ad_group_ad.ad.responsive_search_ad.headlines,
                         ad_group_ad.ad.responsive_search_ad.descriptions,
                         ad_group_ad.ad.responsive_search_ad.path1,
                         ad_group_ad.ad.responsive_search_ad.path2,
                         ad_group_ad.ad_strength,
                         ad_group_ad.policy_summary.approval_status,
                         ad_group_ad.policy_summary.review_status,
                         ad_group_ad.policy_summary.policy_topic_entries,
                         ad_group.id, ad_group.name, campaign.id, campaign.name,
                         campaign.status
                  FROM ad_group_ad WHERE campaign.status = ENABLED"""):
        a = r.ad_group_ad.ad
        rsa = a.responsive_search_ad
        ads.append({
            "resource_name": r.ad_group_ad.resource_name, "ad_id": str(a.id),
            "status": E(r.ad_group_ad.status), "final_urls": list(a.final_urls),
            "tracking_url_template": a.tracking_url_template or "",
            "final_url_suffix": a.final_url_suffix or "",
            "path1": rsa.path1, "path2": rsa.path2,
            "headlines": [h.text for h in rsa.headlines],
            "descriptions": [d.text for d in rsa.descriptions],
            "pinned": [E(h.pinned_field) for h in rsa.headlines if h.pinned_field]
                      + [E(d.pinned_field) for d in rsa.descriptions if d.pinned_field],
            "ad_strength": E(r.ad_group_ad.ad_strength),
            "approval_status": E(r.ad_group_ad.policy_summary.approval_status),
            "review_status": E(r.ad_group_ad.policy_summary.review_status),
            "policy_topics": [t.topic for t in
                              r.ad_group_ad.policy_summary.policy_topic_entries],
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
        })
    after["ads"] = ads
    by_rn = {a["resource_name"]: a for a in ads}
    target_rn = {a["resource_name"] for a in actions}
    targets = [by_rn[rn] for rn in target_rn if rn in by_rn]
    originals = [a for a in ads if a["resource_name"] not in target_rn]

    check("execution: 24 status updates returned", len(receipt["results"]) == 24,
          f"{len(receipt['results'])}")
    check("execution: returned resource names match the approved targets",
          {r["resource_name"] for r in receipt["results"]} == target_rn)
    check("targets: all 24 readable from the API", len(targets) == 24, f"{len(targets)}")
    check("targets: all 24 now read ENABLED",
          all(a["status"] == "ENABLED" for a in targets),
          str(dict(Counter(a["status"] for a in targets))))
    check("originals: all 24 still ENABLED",
          len(originals) == 24 and all(a["status"] == "ENABLED" for a in originals),
          f"{len(originals)} originals, {dict(Counter(a['status'] for a in originals))}")
    check("inventory: 48 ENABLED RSAs total",
          dict(Counter(a["status"] for a in ads)) == {"ENABLED": 48},
          str(dict(Counter(a["status"] for a in ads))))
    check("inventory: zero PAUSED Phase 2 RSAs remain",
          not [a for a in ads if a["status"] == "PAUSED"])
    per_ag = Counter(a["ad_group_id"] for a in ads)
    check("inventory: exactly two ENABLED RSAs per live ad group",
          len(per_ag) == 24 and set(per_ag.values()) == {2},
          f"{len(per_ag)} ad groups, per-group {sorted(set(per_ag.values()))}")

    # content unchanged by the status write
    drift = []
    for a in targets:
        want = planned.get(a["ad_group_id"])
        if not want:
            drift.append(f"{a['ad_id']} unknown ad group")
            continue
        if a["campaign_id"] != want["campaign_id"]:
            drift.append(f"{a['ad_id']} campaign")
        if a["final_urls"] != [want["final_url"]]:
            drift.append(f"{a['ad_id']} final_url")
        if a["path1"] != want["path1"] or a["path2"] != want["path2"]:
            drift.append(f"{a['ad_id']} paths")
        if a["headlines"] != want["headlines"]:
            drift.append(f"{a['ad_id']} headlines")
        if a["descriptions"] != want["descriptions"]:
            drift.append(f"{a['ad_id']} descriptions")
        if a["pinned"]:
            drift.append(f"{a['ad_id']} pinning")
        if a["tracking_url_template"] or a["final_url_suffix"]:
            drift.append(f"{a['ad_id']} tracking template or suffix")
    check("content: every enabled ad still matches the approved campaign, ad group, URL, "
          "paths, 15 headlines, 4 descriptions and pinning state",
          not drift, "; ".join(drift[:6]))

    before_by_rn = {a["resource_name"]: a for a in before["ads"]}
    odrift = []
    for a in originals:
        b = before_by_rn.get(a["resource_name"])
        if not b:
            continue
        if a["headlines"] != b["headlines"] or a["descriptions"] != b["descriptions"] \
           or a["final_urls"] != b["final_urls"]:
            odrift.append(a["ad_id"])
    check("UNTOUCHED: no original ad edited", not odrift, "; ".join(odrift[:6]))

    bad = [a for a in targets
           if a["approval_status"] != "APPROVED" or a["review_status"] != "REVIEWED"
           or a["policy_topics"]]
    after["policy"] = [{"ad_id": a["ad_id"], "ad_group": a["ad_group_name"],
                        "approval": a["approval_status"], "review": a["review_status"],
                        "strength": a["ad_strength"], "topics": a["policy_topics"]}
                       for a in targets]
    check("policy: no ad became disapproved or limited during the mutation",
          not bad, str([(a["ad_id"], a["approval_status"], a["review_status"]) for a in bad]))

    # ---- unrelated resources -------------------------------------------------
    camps = {}
    for r in q("""SELECT campaign.id, campaign.status, campaign.bidding_strategy_type,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.excluded_parent_asset_field_types,
                         campaign_budget.id, campaign_budget.amount_micros
                  FROM campaign WHERE campaign.status = ENABLED"""):
        camps[str(r.campaign.id)] = {
            "ceiling": int(r.campaign.target_spend.cpc_bid_ceiling_micros or 0),
            "budget": int(r.campaign_budget.amount_micros),
            "budget_id": str(r.campaign_budget.id),
            "bidding": E(r.campaign.bidding_strategy_type),
            "excluded": sorted(E(x) for x in r.campaign.excluded_parent_asset_field_types)}
    after["campaigns"] = camps
    budgets = sorted(v["budget"] for v in camps.values())
    check("UNTOUCHED: budgets $26.31 and $39.47", budgets == [26310000, 39470000],
          str([b / 1e6 for b in budgets]))
    check("UNTOUCHED: combined $65.78/day",
          abs(sum(budgets) / 1e6 - 65.78) < 1e-9, f"${sum(budgets)/1e6:.2f}")
    check("UNTOUCHED: $22.00 CPC ceilings",
          all(v["ceiling"] == 22000000 for v in camps.values()))
    check("UNTOUCHED: bidding still TARGET_SPEND",
          all(v["bidding"] == "TARGET_SPEND" for v in camps.values()))
    check("UNTOUCHED: parent asset exclusions intact",
          all(v["excluded"] == ["SITELINK", "STRUCTURED_SNIPPET"] for v in camps.values()))

    kw = q("""SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
              WHERE ad_group_criterion.type = KEYWORD
                AND ad_group_criterion.negative = FALSE AND campaign.status = ENABLED""")
    check("UNTOUCHED: 48 keywords", len(kw) == 48, f"{len(kw)}")
    ng = q("""SELECT campaign_criterion.criterion_id FROM campaign_criterion
              WHERE campaign_criterion.type = KEYWORD
                AND campaign_criterion.negative = TRUE AND campaign.status = ENABLED""")
    check("UNTOUCHED: 88 campaign negatives", len(ng) == 88, f"{len(ng)}")
    sc = q("""SELECT campaign_criterion.criterion_id,
                     campaign_criterion.ad_schedule.start_hour,
                     campaign_criterion.ad_schedule.end_hour FROM campaign_criterion
              WHERE campaign_criterion.type = AD_SCHEDULE AND campaign.status = ENABLED""")
    check("UNTOUCHED: 14 ad-schedule criteria, all 09:00-18:00",
          len(sc) == 14 and all(r.campaign_criterion.ad_schedule.start_hour == 9
                                and r.campaign_criterion.ad_schedule.end_hour == 18
                                for r in sc), f"{len(sc)}")
    loc = defaultdict(set)
    negloc = 0
    for r in q("""SELECT campaign.id, campaign_criterion.location.geo_target_constant,
                         campaign_criterion.negative FROM campaign_criterion
                  WHERE campaign_criterion.type = LOCATION AND campaign.status = ENABLED"""):
        if r.campaign_criterion.negative:
            negloc += 1
        else:
            loc[str(r.campaign.id)].add(
                r.campaign_criterion.location.geo_target_constant.split("/")[-1])
    check("UNTOUCHED: 24 locations per campaign, zero exclusions",
          len(loc) == 2 and all(len(v) == 24 for v in loc.values()) and negloc == 0,
          str({k: len(v) for k, v in loc.items()}))
    conv = q("""SELECT conversion_action.id, conversion_action.primary_for_goal,
                       conversion_action.include_in_conversions_metric
                FROM conversion_action WHERE conversion_action.status = ENABLED""")
    prim = sorted(str(r.conversion_action.id) for r in conv
                  if r.conversion_action.primary_for_goal
                  and r.conversion_action.include_in_conversions_metric)
    check("UNTOUCHED: exactly 3 primary conversion actions",
          prim == ["6566620547", "6885610317", "7644242327"], str(prim))
    ca = q("""SELECT asset.id, campaign.status, campaign_asset.field_type,
                     campaign_asset.status FROM campaign_asset
              WHERE campaign.status = ENABLED""")
    ft = Counter(E(r.campaign_asset.field_type) for r in ca
                 if E(r.campaign_asset.status) == "ENABLED")
    after["campaign_assets"] = dict(ft)
    check("UNTOUCHED: 12 sitelinks, 16 callouts, 2 snippets, 2 call, 2 logo",
          ft.get("SITELINK") == 12 and ft.get("CALLOUT") == 16
          and ft.get("STRUCTURED_SNIPPET") == 2 and ft.get("CALL") == 2
          and ft.get("BUSINESS_LOGO") == 2, str(dict(ft)))
    subs = q("""SELECT recommendation_subscription.type,
                       recommendation_subscription.status
                FROM recommendation_subscription""")
    check("UNTOUCHED: no recommendation auto-apply subscription exists",
          not subs, f"{len(subs)}")

    Path(args.out).write_text(json.dumps(after, indent=2, default=str), encoding="utf-8")

    print("=" * 98)
    print("ENABLE READBACK QA")
    print("=" * 98)
    failed = 0
    for name, ok, detail in results:
        if not ok:
            failed += 1
        print(f"  [{'PASS' if ok else '**FAIL**':8}] {name}" + (f"  ({detail})" if detail else ""))
    print("-" * 98)
    print(f"  {len(results) - failed} passed, {failed} failed")
    print("\n  POLICY STATE OF THE 24 NEWLY ENABLED ADS")
    print(f"    approval: {dict(Counter(x['approval'] for x in after['policy']))}")
    print(f"    review:   {dict(Counter(x['review'] for x in after['policy']))}")
    print(f"    strength: {dict(Counter(x['strength'] for x in after['policy']))}")
    print(f"  after-snapshot: {args.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
