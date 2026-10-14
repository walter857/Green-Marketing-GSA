#!/usr/bin/env python3
"""Preflight for an approved CREATE_PAUSED subplan.

Read-only. SELECT queries only, no mutation. Exit code 1 on any failure, which voids the
approval and stops execution.

Verifies fingerprints against the frozen plan, identity, structural expectations, that the
CSV deliverable agrees with the YAML plan, that no planned ad already exists in any form,
and that every planned final URL matches the approved mapping.
"""
from __future__ import annotations

import argparse
import csv
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
from gm_gsa.safety import approval_code  # noqa: E402

SUBPLANS = ["STATUS", "BUDGET", "EXISTING_RESOURCES", "CONVERSIONS",
            "CREATE_PAUSED", "SITE_OR_TRACKING", "ENABLE"]
HMAX, DMAX = 30, 90
BANNED = [
    ("experience_years", re.compile(r"\b\d{1,3}\+?\s*(?:years?|yrs?)\b", re.I)),
    ("licensed_insured", re.compile(r"\b(licensed|insured|bonded|certified)\b", re.I)),
    ("warranty", re.compile(r"\b(warrant\w+|guarantee\w*|lifetime)\b", re.I)),
    ("rating_award", re.compile(r"\b(\d\.\d\s*star|\d+\s*reviews?|five[- ]star|top[- ]rated|"
                                r"award|#\s*1|number one|best)\b", re.I)),
    ("financing", re.compile(r"\b(financ\w+|payment plan|0%|no interest|affordable)\b", re.I)),
    ("response_time", re.compile(r"\b(same[- ]day|24[/ ]?7|next[- ]day|instant|fastest)\b", re.I)),
    ("pricing", re.compile(r"\$\s?\d|\bcheap\w*|\blowest\b|\bdiscount\w*|\b\d+%\s*off\b", re.I)),
    ("out_of_market", re.compile(r"\b(dallas|houston|fort worth|dfw|san antonio)\b", re.I)),
]

results: list[tuple[str, bool, str]] = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def norm(t):
    return re.sub(r"\s+", " ", (t or "").strip().lower())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--audit", required=True)
    ap.add_argument("--expect-master", required=True)
    ap.add_argument("--expect-subplan-fp", required=True)
    ap.add_argument("--expect-objects", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    doc = load_yaml(args.plan)
    plan = doc["change_plan"]
    tgt = plan["target"]
    cid = tgt["child_customer_id"]
    actions = plan["subplans"]["CREATE_PAUSED"]["actions"]

    # ---- 3/4/5: fingerprints recomputed from the frozen on-disk plan --------
    master = approval_code({"target": tgt,
                            "subplans": {n: plan["subplans"].get(n) for n in SUBPLANS}})
    sub = approval_code({"target": tgt, "subplan": "CREATE_PAUSED", "actions": actions})
    check("fingerprint: CREATE_PAUSED recomputed from the frozen plan",
          sub == args.expect_subplan_fp.upper(),
          f"computed={sub} expected={args.expect_subplan_fp.upper()}")
    check("fingerprint: master recomputed from the frozen plan",
          master == args.expect_master.upper(),
          f"computed={master} expected={args.expect_master.upper()}")
    objs = sum(int(a.get("object_count", 1)) for a in actions)
    check("scope: exactly 24 actions", len(actions) == 24, f"{len(actions)}")
    check("scope: exactly 24 objects", objs == args.expect_objects, f"{objs}")
    check("scope: no other subplan carries an action",
          all(not (plan["subplans"].get(n) or {}).get("actions")
              for n in SUBPLANS if n != "CREATE_PAUSED"))
    check("audit artifact present", Path(args.audit).exists())

    # ---- CSV must agree with the YAML, value for value ---------------------
    rows = list(csv.DictReader(Path(args.csv).open(encoding="utf-8")))
    check("csv: 24 rows", len(rows) == 24, f"{len(rows)}")
    by_ag_csv = {r["ad_group_id"]: r for r in rows}
    mismatch = []
    for a in actions:
        r = by_ag_csv.get(a["resource_id"])
        if not r:
            mismatch.append(f"{a['resource_id']} missing from csv")
            continue
        if r["final_url"] != a["final_url"]:
            mismatch.append(f"{a['resource_id']} final_url")
        if r["path1"] != a["path1"] or r["path2"] != a["path2"]:
            mismatch.append(f"{a['resource_id']} paths")
        for i, h in enumerate(a["headlines"], 1):
            if r.get(f"H{i:02d}") != h:
                mismatch.append(f"{a['resource_id']} H{i:02d}")
        for i, d in enumerate(a["descriptions"], 1):
            if r.get(f"D{i}") != d:
                mismatch.append(f"{a['resource_id']} D{i}")
        if r["created_status"] != "PAUSED":
            mismatch.append(f"{a['resource_id']} created_status")
    check("csv agrees with the yaml plan on every value", not mismatch,
          "; ".join(mismatch[:6]))

    # ---- copy compliance, re-checked from the frozen plan ------------------
    prob = []
    for a in actions:
        hs, ds = a["headlines"], a["descriptions"]
        if len(hs) != 15:
            prob.append(f"{a['action_id']} {len(hs)} headlines")
        if len(ds) != 4:
            prob.append(f"{a['action_id']} {len(ds)} descriptions")
        if any(len(h) > HMAX for h in hs):
            prob.append(f"{a['action_id']} headline over {HMAX}")
        if any(len(d) > DMAX for d in ds):
            prob.append(f"{a['action_id']} description over {DMAX}")
        if len(set(hs)) != len(hs):
            prob.append(f"{a['action_id']} duplicate headline in ad")
        if len(set(ds)) != len(ds):
            prob.append(f"{a['action_id']} duplicate description in ad")
        for text in hs + ds:
            for label, rx in BANNED:
                if rx.search(text):
                    prob.append(f"{a['action_id']} {label} in {text!r}")
        if a.get("pinning") not in (None, "", "none"):
            prob.append(f"{a['action_id']} unexpected pinning {a.get('pinning')!r}")
    check("copy: 15 headlines, 4 descriptions, limits, no duplicates, no banned claims, "
          "no pinning", not prob, "; ".join(prob[:6]))

    # ---- live account ------------------------------------------------------
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    snap: dict = {"customer_id": cid, "purpose": "CREATE_PAUSED preflight"}

    # ---- 6: identity -------------------------------------------------------
    c = q("""SELECT customer.id, customer.descriptive_name, customer.manager,
                    customer.test_account, customer.status, customer.currency_code,
                    customer.time_zone, customer.tracking_url_template
             FROM customer LIMIT 1""")[0].customer
    snap["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                        "manager": bool(c.manager), "test": bool(c.test_account),
                        "tracking_url_template": c.tracking_url_template}
    check("identity: exact account name", c.descriptive_name == tgt["exact_child_account_name"],
          c.descriptive_name)
    check("identity: exact customer ID", str(c.id) == cid, str(c.id))
    check("identity: NOT a manager account", not c.manager)
    check("identity: NOT a test account", not c.test_account)
    check("identity: account ENABLED", E(c.status) == "ENABLED", E(c.status))
    wo = load_yaml(ROOT / "clients/pro-green-austin/work-order.yaml")["work_order"]
    prof = load_yaml(ROOT / "clients/pro-green-austin/client.yaml")["client"]
    check("scope: work order service is still outdoor design & build",
          wo["service"]["exact_primary_service"] == "outdoor design & build"
          == prof["primary_service"] == tgt["exact_service"])
    check("scope: vertical is still hardscaping",
          wo["service"]["vertical"] == prof["vertical"] == "hardscaping")

    # ---- 8: Phase 1 still in place ----------------------------------------
    camps = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status,
                         campaign.bidding_strategy_type,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.excluded_parent_asset_field_types,
                         campaign_budget.id, campaign_budget.amount_micros
                  FROM campaign WHERE campaign.status = ENABLED"""):
        camps[str(r.campaign.id)] = {
            "name": r.campaign.name,
            "ceiling": int(r.campaign.target_spend.cpc_bid_ceiling_micros or 0),
            "excluded": sorted(E(x) for x in r.campaign.excluded_parent_asset_field_types),
            "budget_id": str(r.campaign_budget.id),
            "budget": int(r.campaign_budget.amount_micros)}
    snap["campaigns"] = camps
    check("phase 1 intact: exactly 2 ENABLED campaigns", len(camps) == 2, str(sorted(camps)))
    check("phase 1 intact: $22.00 CPC ceiling on both",
          all(v["ceiling"] == 22000000 for v in camps.values()),
          str({k: v["ceiling"] for k, v in camps.items()}))
    check("phase 1 intact: parent SITELINK + STRUCTURED_SNIPPET excluded on both",
          all(v["excluded"] == ["SITELINK", "STRUCTURED_SNIPPET"] for v in camps.values()))
    daily = sum(v["budget"] for v in camps.values()) / 1e6
    check("phase 1 intact: budgets total $65.78/day", abs(daily - 65.78) < 1e-9, f"${daily:.2f}")
    sched = defaultdict(list)
    for r in q("""SELECT campaign.id, campaign.status, campaign_criterion.criterion_id,
                         campaign_criterion.ad_schedule.day_of_week,
                         campaign_criterion.ad_schedule.start_hour,
                         campaign_criterion.ad_schedule.end_hour
                  FROM campaign_criterion
                  WHERE campaign_criterion.type = AD_SCHEDULE AND campaign.status = ENABLED"""):
        sched[str(r.campaign.id)].append((E(r.campaign_criterion.ad_schedule.day_of_week),
                                          int(r.campaign_criterion.ad_schedule.start_hour),
                                          int(r.campaign_criterion.ad_schedule.end_hour)))
    check("phase 1 intact: 7 ad-schedule criteria per campaign at 09:00-18:00",
          all(len(v) == 7 and all(s == 9 and e == 18 for _, s, e in v)
              for v in sched.values()),
          str({k: len(v) for k, v in sched.items()}))
    conv = q("""SELECT conversion_action.id, conversion_action.name,
                       conversion_action.primary_for_goal,
                       conversion_action.include_in_conversions_metric
                FROM conversion_action WHERE conversion_action.status = ENABLED""")
    prim = sorted(str(r.conversion_action.id) for r in conv
                  if r.conversion_action.primary_for_goal
                  and r.conversion_action.include_in_conversions_metric)
    check("phase 1 intact: exactly 3 primary conversion actions",
          prim == ["6566620547", "6885610317", "7644242327"], str(prim))

    # ---- 9: structure ------------------------------------------------------
    ags = {}
    for r in q("""SELECT ad_group.id, ad_group.name, ad_group.status,
                         campaign.id, campaign.name, campaign.status
                  FROM ad_group WHERE campaign.status = ENABLED"""):
        ags[str(r.ad_group.id)] = {"name": r.ad_group.name, "status": E(r.ad_group.status),
                                   "campaign_id": str(r.campaign.id),
                                   "campaign_name": r.campaign.name}
    snap["ad_groups"] = ags
    check("structure: 24 live ad groups", len(ags) == 24, f"{len(ags)}")
    themes = {n["name"].split("|")[0].strip() for n in ags.values()}
    variants = Counter(n["name"].split("|")[1].strip() for n in ags.values())
    check("structure: 12 distinct themes", len(themes) == 12, f"{len(themes)}")
    check("structure: 12 BOFU + 12 Near Me", variants.get("BOFU") == 12
          and variants.get("Near Me") == 12, str(dict(variants)))

    ads = []
    for r in q("""SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group.id,
                         ad_group_ad.ad.final_urls,
                         ad_group_ad.ad.responsive_search_ad.headlines,
                         ad_group_ad.ad.responsive_search_ad.descriptions,
                         campaign.status
                  FROM ad_group_ad WHERE campaign.status = ENABLED"""):
        ads.append({"ad_id": str(r.ad_group_ad.ad.id), "status": E(r.ad_group_ad.status),
                    "ad_group_id": str(r.ad_group.id),
                    "final_urls": list(r.ad_group_ad.ad.final_urls),
                    "headlines": [h.text for h in
                                  r.ad_group_ad.ad.responsive_search_ad.headlines],
                    "descriptions": [d.text for d in
                                     r.ad_group_ad.ad.responsive_search_ad.descriptions]})
    snap["existing_ads"] = ads
    check("structure: 24 existing ads on live campaigns", len(ads) == 24, f"{len(ads)}")
    check("structure: all 24 existing ads are ENABLED",
          all(a["status"] == "ENABLED" for a in ads),
          str(dict(Counter(a["status"] for a in ads))))
    check("structure: zero existing PAUSED ads on the live campaigns",
          not [a for a in ads if a["status"] == "PAUSED"])
    per_ag = Counter(a["ad_group_id"] for a in ads)
    check("structure: exactly one existing RSA per live ad group",
          set(per_ag.values()) == {1} and len(per_ag) == 24,
          str(sorted(set(per_ag.values()))))

    # ---- 10: no planned ad may already exist -------------------------------
    existing_sig = {}
    for a in ads:
        existing_sig[a["ad_group_id"]] = (
            {norm(h) for h in a["headlines"]}, {norm(d) for d in a["descriptions"]})
    dupes = []
    for a in actions:
        sig = existing_sig.get(a["resource_id"])
        if not sig:
            dupes.append(f"{a['action_id']} ad group {a['resource_id']} has no existing ad")
            continue
        eh, ed = sig
        nh = {norm(h) for h in a["headlines"]}
        nd = {norm(d) for d in a["descriptions"]}
        if nh == eh and nd == ed:
            dupes.append(f"{a['action_id']} EXACT duplicate of the existing ad")
        overlap_h = nh & eh
        overlap_d = nd & ed
        if overlap_h:
            dupes.append(f"{a['action_id']} shares headline(s) with existing: {sorted(overlap_h)}")
        if overlap_d:
            dupes.append(f"{a['action_id']} shares description(s): {sorted(overlap_d)}")
    check("duplicates: no planned ad duplicates an existing ad, exactly or normalized",
          not dupes, "; ".join(dupes[:6]))
    check("duplicates: each planned ad targets a distinct ad group",
          len({a["resource_id"] for a in actions}) == 24)
    check("duplicates: every planned ad group is a live ad group",
          all(a["resource_id"] in ags for a in actions))

    # ---- 11: final URL mapping --------------------------------------------
    existing_url = {a["ad_group_id"]: (a["final_urls"][0] if a["final_urls"] else "")
                    for a in ads}
    url_mismatch = [f"{a['action_id']} {a['resource_id']}"
                    for a in actions if a["final_url"] != existing_url.get(a["resource_id"])]
    check("urls: every planned final URL equals the approved URL for that ad group",
          not url_mismatch, "; ".join(url_mismatch[:6]))
    dests = Counter(a["final_url"] for a in actions)
    check("urls: 13 unique destinations", len(dests) == 13, f"{len(dests)}")
    check("urls: no single page is used by every ad",
          max(dests.values()) <= 2, f"max reuse {max(dests.values())}")
    main_site = [a for a in actions if "offeraustin." not in a["final_url"]]
    check("urls: exactly one approved main-site exception, Hardscaping | Near Me",
          len(main_site) == 1
          and ags[main_site[0]["resource_id"]]["name"] == "Hardscaping | Near Me",
          str([ags[m["resource_id"]]["name"] for m in main_site]))
    check("urls: the other 23 point at offeraustin.* offer pages",
          all("offeraustin.progreenlandscapesolutions.com" in a["final_url"]
              for a in actions if a not in main_site))
    themed = defaultdict(set)
    for a in actions:
        themed[ags[a["resource_id"]]["name"].split("|")[0].strip()].add(a["final_url"])
    cross = {t: sorted(u) for t, u in themed.items() if len(u) > 1}
    check("urls: each theme's pair shares one destination, except the approved exception",
          set(cross) <= {"Hardscaping"}, str(cross))
    snap["planned_url_map"] = {a["resource_id"]: a["final_url"] for a in actions}

    Path(args.out).write_text(json.dumps(snap, indent=2, default=str), encoding="utf-8")

    print("=" * 96)
    print("CREATE_PAUSED PREFLIGHT")
    print("=" * 96)
    failed = 0
    for name, ok, detail in results:
        if not ok:
            failed += 1
        print(f"  [{'PASS' if ok else '**STOP**':8}] {name}" + (f"  ({detail})" if detail else ""))
    print("-" * 96)
    print(f"  {len(results) - failed} passed, {failed} failed")
    if failed:
        print("\n  STOP. Approval is VOID. Do not execute. Regenerate and seek fresh approval.")
    else:
        print("\n  All checks passed. The approved fingerprint remains valid for execution.")
    print(f"  preflight snapshot: {args.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
