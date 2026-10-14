#!/usr/bin/env python3
"""Post-write readback QA.

Read-only. Confirms every approved change landed exactly as planned, confirms the budget
and targeting invariants, and confirms unrelated resources were not touched by comparing
against the preflight snapshot taken immediately before the write.

Exit code 1 if any assertion fails.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, load_yaml  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name as E  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--preflight", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = load_yaml(args.plan)["change_plan"]
    before = json.loads(Path(args.preflight).read_text(encoding="utf-8"))
    cid = plan["target"]["child_customer_id"]
    acts = {k: (v.get("actions") or []) for k, v in plan["subplans"].items()}

    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    def rows(q):
        return list(svc.search(customer_id=cid, query=q))

    after: dict = {"customer_id": cid, "purpose": "post-write readback"}

    # ---- identity -----------------------------------------------------------
    c = rows("""SELECT customer.id, customer.descriptive_name, customer.time_zone,
                       customer.tracking_url_template
                FROM customer LIMIT 1""")[0].customer
    after["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                         "tracking_url_template": c.tracking_url_template}
    check("identity: still the authorised account",
          str(c.id) == cid and c.descriptive_name == plan["target"]["exact_child_account_name"])
    check("UNTOUCHED: customer.tracking_url_template was not written by us",
          c.tracking_url_template == before["identity"]["tracking_url_template"],
          "matches the value read at preflight")

    # ---- BUDGET -------------------------------------------------------------
    bnow = {}
    for x in rows("""SELECT campaign_budget.id, campaign_budget.amount_micros,
                            campaign_budget.explicitly_shared, campaign_budget.status
                     FROM campaign_budget"""):
        b = x.campaign_budget
        bnow[str(b.id)] = {"amount_micros": int(b.amount_micros),
                           "shared": bool(b.explicitly_shared), "status": E(b.status)}
    after["budgets"] = bnow
    for a in acts["BUDGET"]:
        want = int(re.search(r"amount_micros = (\d+)", a["proposed_state"]).group(1))
        got = bnow.get(a["resource_id"], {}).get("amount_micros")
        check(f"{a['action_id']}: budget {a['resource_id']} now {want} micros",
              got == want, f"live={got}")
    changed_budgets = {a["resource_id"] for a in acts["BUDGET"]}
    untouched = [bid for bid, v in bnow.items()
                 if bid not in changed_budgets
                 and before["budgets"].get(bid, {}).get("amount_micros") != v["amount_micros"]]
    check("UNTOUCHED: no other campaign budget changed", not untouched, ", ".join(untouched))

    # ---- budget invariant ----------------------------------------------------
    enabled = rows("""SELECT campaign.id, campaign.name, campaign.status,
                             campaign.bidding_strategy_type,
                             campaign.target_spend.cpc_bid_ceiling_micros,
                             campaign.excluded_parent_asset_field_types,
                             campaign_budget.id, campaign_budget.amount_micros,
                             campaign_budget.explicitly_shared
                      FROM campaign WHERE campaign.status = ENABLED""")
    cnow, seen_budgets = {}, {}
    for x in enabled:
        cnow[str(x.campaign.id)] = {
            "name": x.campaign.name, "bidding": E(x.campaign.bidding_strategy_type),
            "cpc_ceiling": int(x.campaign.target_spend.cpc_bid_ceiling_micros or 0),
            "excluded_parent": sorted(E(v)
                                      for v in x.campaign.excluded_parent_asset_field_types)}
        seen_budgets[str(x.campaign_budget.id)] = int(x.campaign_budget.amount_micros)
    after["campaigns"] = cnow
    daily = sum(seen_budgets.values()) / 1_000_000       # each shared budget counted once
    after["enabled_daily_total"] = daily
    check("budget invariant: enabled in-scope daily total is $65.78",
          abs(daily - 65.78) < 1e-9, f"${daily:.2f}")
    check("budget invariant: 30.4-day projection is $1,999.71 and at or under $2,000",
          abs(daily * 30.4 - 1999.712) < 0.01 and daily * 30.4 <= 2000.0,
          f"${daily * 30.4:.2f}")
    check("budget invariant: exactly two ENABLED campaigns, none newly enabled",
          set(cnow) == set(before["campaigns"]), f"{sorted(cnow)}")

    # ---- campaign field updates ---------------------------------------------
    for a in acts["EXISTING_RESOURCES"]:
        rid = a["resource_id"]
        if a["operation"] == "UPDATE_CAMPAIGN_EXCLUDED_PARENT_ASSET_FIELD_TYPES":
            check(f"{a['action_id']}: {rid} excludes parent SITELINK + STRUCTURED_SNIPPET",
                  cnow.get(rid, {}).get("excluded_parent")
                  == ["SITELINK", "STRUCTURED_SNIPPET"],
                  str(cnow.get(rid, {}).get("excluded_parent")))
        elif a["operation"] == "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING":
            check(f"{a['action_id']}: {rid} CPC ceiling is $22.00",
                  cnow.get(rid, {}).get("cpc_ceiling") == 22000000,
                  str(cnow.get(rid, {}).get("cpc_ceiling")))
            check(f"{a['action_id']}: {rid} bidding strategy unchanged at TARGET_SPEND",
                  cnow.get(rid, {}).get("bidding") == "TARGET_SPEND")

    # ---- ad schedule ---------------------------------------------------------
    snow = {}
    for x in rows("""SELECT campaign.id, campaign_criterion.criterion_id,
                            campaign_criterion.ad_schedule.day_of_week,
                            campaign_criterion.ad_schedule.start_hour,
                            campaign_criterion.ad_schedule.end_hour,
                            campaign_criterion.ad_schedule.start_minute,
                            campaign_criterion.ad_schedule.end_minute
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = AD_SCHEDULE
                       AND campaign.status = ENABLED"""):
        snow.setdefault(str(x.campaign.id), []).append({
            "criterion_id": str(x.campaign_criterion.criterion_id),
            "day": E(x.campaign_criterion.ad_schedule.day_of_week),
            "start_hour": int(x.campaign_criterion.ad_schedule.start_hour),
            "end_hour": int(x.campaign_criterion.ad_schedule.end_hour),
            "start_minute": E(x.campaign_criterion.ad_schedule.start_minute),
            "end_minute": E(x.campaign_criterion.ad_schedule.end_minute)})
    after["ad_schedule"] = snow
    DAYS = {"MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"}
    for camp in cnow:
        got = snow.get(camp, [])
        check(f"ad schedule: {camp} has exactly 7 criteria", len(got) == 7, f"{len(got)}")
        check(f"ad schedule: {camp} covers all seven days",
              {g['day'] for g in got} == DAYS)
        check(f"ad schedule: {camp} every criterion is 09:00-18:00 account time",
              all(g["start_hour"] == 9 and g["end_hour"] == 18
                  and g["start_minute"] == "ZERO" and g["end_minute"] == "ZERO"
                  for g in got),
              "= 08:00-17:00 America/Chicago")
        old_ids = {k.split("~")[1] for k in before["ad_schedule"] if k.startswith(camp)}
        check(f"ad schedule: {camp} none of the old 08:00-17:00 criteria survive",
              not (old_ids & {g["criterion_id"] for g in got}))

    # ---- negative keywords ---------------------------------------------------
    negs = set()
    for x in rows("""SELECT campaign.id, campaign_criterion.criterion_id,
                            campaign_criterion.keyword.text,
                            campaign_criterion.keyword.match_type
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = KEYWORD
                       AND campaign_criterion.negative = TRUE
                       AND campaign.status = ENABLED"""):
        negs.add((str(x.campaign.id),
                  (x.campaign_criterion.keyword.text or "").strip().lower(),
                  E(x.campaign_criterion.keyword.match_type)))
    after["enabled_campaign_negative_count"] = len(negs)
    for a in acts["EXISTING_RESOURCES"]:
        if a["operation"] != "ADD_CAMPAIGN_NEGATIVE_KEYWORD":
            continue
        key = (a["resource_id"], a["negative_text"].strip().lower(), a["match_type"])
        check(f"{a['action_id']}: negative {a['negative_text']!r} present on {a['resource_id']}",
              key in negs)
    added = sum(1 for a in acts["EXISTING_RESOURCES"]
                if a["operation"] == "ADD_CAMPAIGN_NEGATIVE_KEYWORD")
    check("negatives: campaign negative count rose by exactly the 16 added",
          len(negs) == before["existing_campaign_negatives_count"] + added,
          f"before={before['existing_campaign_negatives_count']} after={len(negs)}")

    # ---- shared criteria -----------------------------------------------------
    shared = {}
    for x in rows("""SELECT shared_criterion.resource_name, shared_criterion.keyword.text,
                            shared_criterion.keyword.match_type
                     FROM shared_criterion"""):
        shared[x.shared_criterion.resource_name] = (
            (x.shared_criterion.keyword.text or "").strip().lower(),
            E(x.shared_criterion.keyword.match_type))
    after["shared_criteria_total"] = len(shared)
    removed = [a for a in acts["EXISTING_RESOURCES"]
               if a["operation"] == "REMOVE_SHARED_LIST_NEGATIVE"]
    for a in removed:
        check(f"{a['action_id']}: {a['negative_text']!r} removed from "
              f"{a['resource_name'][:34]}",
              a["shared_criterion_resource_name"] not in shared)
    check("shared criteria: total fell by exactly the 7 removed",
          len(shared) == before["shared_criteria_total"] - len(removed),
          f"before={before['shared_criteria_total']} after={len(shared)}")
    emerg = [rn for rn, v in shared.items() if v[0] == "emergency"]
    check("UNTOUCHED: 'emergency' negatives all still present",
          len(emerg) == 6, f"{len(emerg)} memberships")

    # ---- conversion actions --------------------------------------------------
    conv = {}
    for x in rows("""SELECT conversion_action.id, conversion_action.name,
                            conversion_action.status, conversion_action.primary_for_goal,
                            conversion_action.include_in_conversions_metric,
                            conversion_action.type, conversion_action.category
                     FROM conversion_action"""):
        a_ = x.conversion_action
        conv[str(a_.id)] = {"name": a_.name, "status": E(a_.status),
                            "primary_for_goal": bool(a_.primary_for_goal),
                            "in_col": bool(a_.include_in_conversions_metric),
                            "type": E(a_.type_), "category": E(a_.category)}
    after["conversion_actions"] = conv
    for a in acts["CONVERSIONS"]:
        cur = conv.get(a["resource_id"], {})
        check(f"{a['action_id']}: {a['resource_name'][:40]} primary_for_goal is false",
              cur.get("primary_for_goal") is False, str(cur.get("primary_for_goal")))
        check(f"{a['action_id']}: still ENABLED and measurable as secondary",
              cur.get("status") == "ENABLED")
        # the readback assertion the plan demanded
        check(f"{a['action_id']}: include_in_conversions_metric followed to false",
              cur.get("in_col") is False,
              "PLAN REQUIRED A SEPARATE MUTATION IF THIS DID NOT FOLLOW"
              if cur.get("in_col") else "followed as expected")

    survivors = sorted(k for k, v in conv.items()
                       if v["status"] == "ENABLED" and v["primary_for_goal"] and v["in_col"])
    expected = sorted(d["id"] for d in
                      plan["subplans"]["CONVERSIONS"]["remaining_primary_after_this_change"])
    check("conversions: exactly the three declared primaries remain in the column",
          survivors == expected, f"live={survivors} expected={expected}")
    ccg = rows("SELECT custom_conversion_goal.id FROM custom_conversion_goal")
    check("conversions: still no custom_conversion_goal", not ccg, f"{len(ccg)}")

    # ---- untouched targeting -------------------------------------------------
    loc = {}
    for x in rows("""SELECT campaign.id, campaign_criterion.location.geo_target_constant,
                            campaign_criterion.negative
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = LOCATION AND campaign.status = ENABLED"""):
        loc.setdefault(str(x.campaign.id), {"pos": set(), "neg": set()})
        loc[str(x.campaign.id)]["neg" if x.campaign_criterion.negative else "pos"].add(
            x.campaign_criterion.location.geo_target_constant.split("/")[-1])
    after["locations"] = {k: {"pos": sorted(v["pos"]), "neg": sorted(v["neg"])}
                          for k, v in loc.items()}
    for camp, v in loc.items():
        check(f"UNTOUCHED: {camp} still targets the same 24 locations",
              sorted(v["pos"]) == before["locations"][camp]["pos"] and not v["neg"],
              f"{len(v['pos'])} positive / {len(v['neg'])} negative")
    geo = rows("""SELECT campaign.id, campaign.geo_target_type_setting.positive_geo_target_type
                  FROM campaign WHERE campaign.status = ENABLED""")
    check("UNTOUCHED: PRESENCE targeting intact on both campaigns",
          all(E(g.campaign.geo_target_type_setting.positive_geo_target_type) == "PRESENCE"
              for g in geo))

    kw = rows("""SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
                 WHERE ad_group_criterion.type = KEYWORD
                   AND ad_group_criterion.negative = FALSE
                   AND campaign.status = ENABLED""")
    check("UNTOUCHED: still 48 positive keywords on the live campaigns",
          len(kw) == 48, f"{len(kw)}")
    ads = rows("""SELECT ad_group_ad.ad.id FROM ad_group_ad
                  WHERE campaign.status = ENABLED AND ad_group_ad.status = ENABLED""")
    check("UNTOUCHED: still 24 enabled ads, none created or removed",
          len(ads) == 24, f"{len(ads)}")

    Path(args.out).write_text(json.dumps(after, indent=2, default=str), encoding="utf-8")

    print("=" * 94)
    print("READBACK QA")
    print("=" * 94)
    failed = 0
    for name, ok, detail in results:
        if not ok:
            failed += 1
        print(f"  [{'PASS' if ok else '**FAIL**':8}] {name}" + (f"  ({detail})" if detail else ""))
    print("-" * 94)
    print(f"  {len(results) - failed} passed, {failed} failed")
    print(f"  after-snapshot: {args.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
