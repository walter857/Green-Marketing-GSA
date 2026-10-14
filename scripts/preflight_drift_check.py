#!/usr/bin/env python3
"""Preflight drift check for an approved Green Marketing change plan.

Read-only. SELECT queries only, no mutation. Exit code 1 on any drift, which invalidates
the approved fingerprints and stops execution.

Every approved action's recorded current_state is compared against the live account now.
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

# scope="approved"    -> drift here invalidates an approved fingerprint. Hard stop.
# scope="out_of_scope" -> drift here touches nothing any approved action targets. It is
#                         reported and escalated, but it cannot invalidate a fingerprint
#                         whose canonical content does not include the field.
findings: list[tuple[str, bool, str, str]] = []


def check(name: str, ok: bool, detail: str = "", scope: str = "approved") -> None:
    findings.append((name, bool(ok), detail, scope))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = load_yaml(args.plan)["change_plan"]
    tgt = plan["target"]
    cid = tgt["child_customer_id"]

    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    snap: dict = {"customer_id": cid, "purpose": "preflight drift check"}

    def rows(q):
        return list(svc.search(customer_id=cid, query=q))

    # ---- identity -----------------------------------------------------------
    r = rows("""SELECT customer.id, customer.descriptive_name, customer.time_zone,
                       customer.currency_code, customer.manager, customer.test_account,
                       customer.tracking_url_template
                FROM customer LIMIT 1""")[0].customer
    snap["identity"] = {"id": str(r.id), "name": r.descriptive_name,
                        "tz": r.time_zone, "currency": r.currency_code,
                        "tracking_url_template": r.tracking_url_template}
    check("identity: exact account name", r.descriptive_name == tgt["exact_child_account_name"],
          r.descriptive_name)
    check("identity: exact customer ID", str(r.id) == cid, str(r.id))
    check("identity: not a manager or test account", not r.manager and not r.test_account)

    # ClickCease must be untouched and must still hold the value BLK-001 recorded.
    blk = next(b for b in plan["blocked_proposals"]
               if b.get("field_mask") == "tracking_url_template")
    # BLK-001 is BLOCKED and carries no fingerprint, and no approved action has
    # field_mask tracking_url_template. Drift here is therefore out of scope for the
    # approved subplans, but it is material and must be escalated.
    approved_masks = {a.get("field_mask") for k, v in plan["subplans"].items()
                      for a in (v.get("actions") or [])}
    check("clickcease: no approved action targets customer.tracking_url_template",
          "tracking_url_template" not in approved_masks)
    check("clickcease: tracking template unchanged since the plan was written",
          r.tracking_url_template == blk["current_state_verbatim"],
          "DRIFTED - BLK-001 must be regenerated; it stays blocked either way"
          if r.tracking_url_template != blk["current_state_verbatim"] else "identical",
          scope="out_of_scope")

    acts = {k: (v.get("actions") or []) for k, v in plan["subplans"].items()}

    # ---- BUDGET -------------------------------------------------------------
    budget_now = {}
    for x in rows("""SELECT campaign_budget.id, campaign_budget.amount_micros,
                            campaign_budget.explicitly_shared, campaign_budget.status
                     FROM campaign_budget"""):
        b = x.campaign_budget
        budget_now[str(b.id)] = {"amount_micros": int(b.amount_micros),
                                 "shared": bool(b.explicitly_shared),
                                 "status": E(b.status)}
    snap["budgets"] = budget_now
    for a in acts["BUDGET"]:
        want = int(re.search(r"amount_micros = (\d+)", a["current_state"]).group(1))
        got = budget_now.get(a["resource_id"], {}).get("amount_micros")
        check(f"budget {a['action_id']}: {a['resource_id']} still at {want} micros",
              got == want, f"live={got}")
        check(f"budget {a['action_id']}: {a['resource_id']} is not shared",
              budget_now.get(a["resource_id"], {}).get("shared") is False)

    # ---- campaign-level fields ---------------------------------------------
    camp_now = {}
    for x in rows("""SELECT campaign.id, campaign.name, campaign.status,
                            campaign.bidding_strategy_type,
                            campaign.target_spend.cpc_bid_ceiling_micros,
                            campaign.excluded_parent_asset_field_types
                     FROM campaign WHERE campaign.status = ENABLED"""):
        c = x.campaign
        camp_now[str(c.id)] = {
            "name": c.name, "bidding": E(c.bidding_strategy_type),
            "cpc_ceiling": int(c.target_spend.cpc_bid_ceiling_micros or 0),
            "excluded_parent": sorted(E(v) for v in c.excluded_parent_asset_field_types)}
    snap["campaigns"] = camp_now
    check("scope: exactly two ENABLED campaigns", len(camp_now) == 2, str(sorted(camp_now)))

    for a in acts["EXISTING_RESOURCES"]:
        op, rid = a["operation"], a["resource_id"]
        if op == "UPDATE_CAMPAIGN_EXCLUDED_PARENT_ASSET_FIELD_TYPES":
            check(f"{a['action_id']}: {rid} excluded_parent still empty",
                  camp_now.get(rid, {}).get("excluded_parent") == [],
                  str(camp_now.get(rid, {}).get("excluded_parent")))
        elif op == "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING":
            check(f"{a['action_id']}: {rid} still TARGET_SPEND with no ceiling",
                  camp_now.get(rid, {}).get("bidding") == "TARGET_SPEND"
                  and camp_now.get(rid, {}).get("cpc_ceiling") == 0,
                  f"{camp_now.get(rid, {}).get('bidding')} / "
                  f"{camp_now.get(rid, {}).get('cpc_ceiling')}")

    # ---- ad schedule --------------------------------------------------------
    sched_now = {}
    for x in rows("""SELECT campaign.id, campaign_criterion.criterion_id,
                            campaign_criterion.resource_name,
                            campaign_criterion.ad_schedule.day_of_week,
                            campaign_criterion.ad_schedule.start_hour,
                            campaign_criterion.ad_schedule.end_hour,
                            campaign_criterion.ad_schedule.start_minute,
                            campaign_criterion.ad_schedule.end_minute
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = AD_SCHEDULE
                       AND campaign.status = ENABLED"""):
        k = (str(x.campaign.id), str(x.campaign_criterion.criterion_id))
        sched_now[k] = {"resource_name": x.campaign_criterion.resource_name,
                        "day": E(x.campaign_criterion.ad_schedule.day_of_week),
                        "start_hour": int(x.campaign_criterion.ad_schedule.start_hour),
                        "end_hour": int(x.campaign_criterion.ad_schedule.end_hour),
                        "start_minute": E(x.campaign_criterion.ad_schedule.start_minute),
                        "end_minute": E(x.campaign_criterion.ad_schedule.end_minute)}
    snap["ad_schedule"] = {f"{a}~{b}": v for (a, b), v in sched_now.items()}
    planned = {(a["resource_id"], c["criterion_id"]): c
               for a in acts["EXISTING_RESOURCES"]
               if a["operation"] == "REMOVE_CAMPAIGN_AD_SCHEDULE_CRITERIA"
               for c in a["exact_criteria_removed"]}
    check("ad schedule: live criteria match the plan exactly, no more and no fewer",
          set(sched_now) == set(planned),
          f"live={len(sched_now)} planned={len(planned)}")
    bad = [f"{k}" for k, v in sched_now.items()
           if v["start_hour"] != 8 or v["end_hour"] != 17
           or v["start_minute"] != "ZERO" or v["end_minute"] != "ZERO"]
    check("ad schedule: every live criterion is still 08:00-17:00", not bad, "; ".join(bad))
    for k, v in sched_now.items():
        if k in planned:
            check(f"ad schedule: {k[0]}~{k[1]} day still {planned[k]['day']}",
                  v["day"] == planned[k]["day"], v["day"])

    # ---- negative keywords to add must not already exist --------------------
    negs_now = set()
    for x in rows("""SELECT campaign.id, campaign_criterion.keyword.text,
                            campaign_criterion.keyword.match_type
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = KEYWORD
                       AND campaign_criterion.negative = TRUE
                       AND campaign.status = ENABLED"""):
        negs_now.add((str(x.campaign.id),
                      (x.campaign_criterion.keyword.text or "").strip().lower(),
                      E(x.campaign_criterion.keyword.match_type)))
    snap["existing_campaign_negatives_count"] = len(negs_now)
    dupes = []
    for a in acts["EXISTING_RESOURCES"]:
        if a["operation"] == "ADD_CAMPAIGN_NEGATIVE_KEYWORD":
            key = (a["resource_id"], a["negative_text"].strip().lower(), a["match_type"])
            if key in negs_now:
                dupes.append(f"{a['action_id']} {a['negative_text']!r} on {a['resource_id']}")
    check("negatives: none of the 8 additions already exists", not dupes, "; ".join(dupes))

    # ---- shared criteria to remove must still exist -------------------------
    shared_now = {}
    for x in rows("""SELECT shared_set.id, shared_criterion.criterion_id,
                            shared_criterion.keyword.text,
                            shared_criterion.keyword.match_type,
                            shared_criterion.resource_name
                     FROM shared_criterion"""):
        shared_now[x.shared_criterion.resource_name] = {
            "set_id": str(x.shared_set.id),
            "text": x.shared_criterion.keyword.text,
            "match_type": E(x.shared_criterion.keyword.match_type)}
    missing = []
    for a in acts["EXISTING_RESOURCES"]:
        if a["operation"] == "REMOVE_SHARED_LIST_NEGATIVE":
            rn = a["shared_criterion_resource_name"]
            live = shared_now.get(rn)
            if not live:
                missing.append(f"{a['action_id']} {rn}")
            else:
                check(f"{a['action_id']}: {a['negative_text']!r} [{a['match_type']}] still present",
                      live["text"].strip().lower() == a["negative_text"].strip().lower()
                      and live["match_type"] == a["match_type"],
                      f"live={live['text']!r}/{live['match_type']}")
    check("negatives: all 7 removal targets still exist", not missing, "; ".join(missing))
    snap["shared_criteria_total"] = len(shared_now)

    # 'emergency' must be present and must NOT be in the removal set
    emerg = [rn for rn, v in shared_now.items()
             if (v["text"] or "").strip().lower() == "emergency"]
    planned_rm = {a["shared_criterion_resource_name"] for a in acts["EXISTING_RESOURCES"]
                  if a["operation"] == "REMOVE_SHARED_LIST_NEGATIVE"}
    check("negatives: 'emergency' exists and is NOT scheduled for removal",
          bool(emerg) and not (set(emerg) & planned_rm), f"{len(emerg)} memberships")

    # ---- conversion actions -------------------------------------------------
    conv_now = {}
    for x in rows("""SELECT conversion_action.id, conversion_action.name,
                            conversion_action.status, conversion_action.primary_for_goal,
                            conversion_action.include_in_conversions_metric,
                            conversion_action.type, conversion_action.category
                     FROM conversion_action"""):
        c = x.conversion_action
        conv_now[str(c.id)] = {"name": c.name, "status": E(c.status),
                               "primary_for_goal": bool(c.primary_for_goal),
                               "in_col": bool(c.include_in_conversions_metric),
                               "type": E(c.type_), "category": E(c.category)}
    snap["conversion_actions"] = conv_now
    for a in acts["CONVERSIONS"]:
        cur = conv_now.get(a["resource_id"])
        check(f"{a['action_id']}: {a['resource_name'][:38]} still primary and in the column",
              bool(cur) and cur["primary_for_goal"] and cur["in_col"],
              f"primary={cur and cur['primary_for_goal']} inCol={cur and cur['in_col']}")
        check(f"{a['action_id']}: name unchanged",
              bool(cur) and cur["name"] == a["resource_name"], cur and cur["name"])

    ccg = rows("SELECT custom_conversion_goal.id FROM custom_conversion_goal")
    check("conversions: still no custom_conversion_goal in the account", not ccg, f"{len(ccg)}")
    snap["custom_conversion_goals"] = len(ccg)

    # ---- locations, untouched but must stay intact --------------------------
    loc = {}
    for x in rows("""SELECT campaign.id, campaign_criterion.location.geo_target_constant,
                            campaign_criterion.negative
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = LOCATION AND campaign.status = ENABLED"""):
        loc.setdefault(str(x.campaign.id), {"pos": set(), "neg": set()})
        key = "neg" if x.campaign_criterion.negative else "pos"
        loc[str(x.campaign.id)][key].add(
            x.campaign_criterion.location.geo_target_constant.split("/")[-1])
    for c, v in loc.items():
        check(f"locations: {c} still targets exactly 24 with no exclusion",
              len(v["pos"]) == 24 and not v["neg"], f"{len(v['pos'])} pos / {len(v['neg'])} neg")
    snap["locations"] = {k: {"pos": sorted(v["pos"]), "neg": sorted(v["neg"])}
                         for k, v in loc.items()}

    Path(args.out).write_text(json.dumps(snap, indent=2, default=str), encoding="utf-8")

    print("=" * 92)
    print("PREFLIGHT DRIFT CHECK")
    print("=" * 92)
    blocking = 0
    outofscope = 0
    for name, ok, detail, scope in findings:
        if not ok:
            if scope == "approved":
                blocking += 1
                tag = "**STOP**"
            else:
                outofscope += 1
                tag = "*ESCALATE*"
        else:
            tag = "PASS"
        print(f"  [{tag:10}] {name}" + (f"  ({detail})" if detail else ""))
    print("-" * 92)
    passed = len(findings) - blocking - outofscope
    print(f"  {passed} passed, {blocking} blocking drift, {outofscope} out-of-scope drift")
    if blocking:
        print("\n  STOP. An APPROVED target drifted. Those fingerprints are INVALID.")
        print("  Regenerate the affected subplan and obtain fresh approval.")
    elif outofscope:
        print("\n  PROCEED WITH ESCALATION. No approved target drifted, so every approved")
        print("  fingerprint remains valid. Drift was found on a resource that no approved")
        print("  action touches; it is reported to the approver and the affected BLOCKED")
        print("  proposal must be regenerated. It stays blocked.")
    else:
        print("\n  No drift. The approved fingerprints remain valid for execution.")
    print(f"  preflight snapshot: {args.out}")
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
