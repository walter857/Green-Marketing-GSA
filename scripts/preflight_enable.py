#!/usr/bin/env python3
"""Preflight for an approved ENABLE subplan.

Read-only. SELECT queries only, no mutation. Exit code 1 on any failure, which voids the
approval and stops execution.

Includes a hard Google policy-review gate: every target ad must be fully cleared before any
status change is permitted.
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
# Anything not in this pair blocks the run.
CLEARED_APPROVAL = {"APPROVED"}
CLEARED_REVIEW = {"REVIEWED"}
BLOCKING_REVIEW = {"REVIEW_IN_PROGRESS", "UNDER_APPEAL", "UNKNOWN", "UNSPECIFIED",
                   "ELIGIBLE_MAY_SERVE"}

results: list[tuple[str, bool, str]] = []
gate_detail: dict = {}


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--enable-plan", required=True)
    ap.add_argument("--phase2-plan", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--create-receipt", required=True)
    ap.add_argument("--create-preflight", required=True)
    ap.add_argument("--expect-master", required=True)
    ap.add_argument("--expect-subplan-fp", required=True)
    ap.add_argument("--expect-objects", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = load_yaml(args.enable_plan)["change_plan"]
    p2 = load_yaml(args.phase2_plan)["change_plan"]
    tgt = plan["target"]
    cid = tgt["child_customer_id"]
    actions = plan["subplans"]["ENABLE"]["actions"]
    planned_p2 = {a["resource_id"]: a for a in p2["subplans"]["CREATE_PAUSED"]["actions"]}
    receipt = json.loads(Path(args.create_receipt).read_text(encoding="utf-8"))
    before_create = json.loads(Path(args.create_preflight).read_text(encoding="utf-8"))

    # ---- 2/3/4 fingerprints from the frozen plan ---------------------------
    master = approval_code({"target": tgt,
                            "subplans": {n: plan["subplans"].get(n) for n in SUBPLANS}})
    sub = approval_code({"target": tgt, "subplan": "ENABLE", "actions": actions})
    check("fingerprint: ENABLE recomputed from the frozen plan",
          sub == args.expect_subplan_fp.upper(),
          f"computed={sub} expected={args.expect_subplan_fp.upper()}")
    check("fingerprint: master recomputed from the frozen plan",
          master == args.expect_master.upper(),
          f"computed={master} expected={args.expect_master.upper()}")
    check("scope: exactly 24 actions", len(actions) == 24, f"{len(actions)}")
    check("scope: exactly 24 objects",
          sum(int(a.get("object_count", 1)) for a in actions) == args.expect_objects)
    check("scope: no other subplan carries an action",
          all(not (plan["subplans"].get(n) or {}).get("actions")
              for n in SUBPLANS if n != "ENABLE"))
    check("scope: every action changes only the status field",
          all(a["field_mask"] == "status" for a in actions))
    check("scope: every action sets ENABLED",
          all(a["proposed_state"] == "status = ENABLED" for a in actions))

    # ---- 6: the plan targets exactly the ads created under 13B70F010DDF ----
    created_rn = {r["resource_name"] for r in receipt["results"]}
    plan_rn = {a["resource_name"] for a in actions}
    check("provenance: CREATE_PAUSED receipt fingerprint is 13B70F010DDF",
          receipt["fingerprint"] == "13B70F010DDF", receipt["fingerprint"])
    check("provenance: ENABLE targets exactly the 24 ads created under CREATE_PAUSED",
          plan_rn == created_rn,
          f"plan={len(plan_rn)} created={len(created_rn)} diff={len(plan_rn ^ created_rn)}")

    # ---- live account ------------------------------------------------------
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    snap: dict = {"customer_id": cid, "purpose": "ENABLE preflight"}

    # ---- 5: identity -------------------------------------------------------
    c = q("""SELECT customer.id, customer.descriptive_name, customer.manager,
                    customer.test_account, customer.status, customer.tracking_url_template
             FROM customer LIMIT 1""")[0].customer
    snap["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                        "manager": bool(c.manager), "test": bool(c.test_account),
                        "tracking_url_template": c.tracking_url_template}
    check("identity: exact account name", c.descriptive_name == tgt["exact_child_account_name"],
          c.descriptive_name)
    check("identity: exact customer ID", str(c.id) == cid, str(c.id))
    check("identity: NOT a manager account", not c.manager)
    check("identity: NOT a test account", not c.test_account)
    wo = load_yaml(ROOT / "clients/pro-green-austin/work-order.yaml")["work_order"]
    prof = load_yaml(ROOT / "clients/pro-green-austin/client.yaml")["client"]
    check("scope: service is still outdoor design & build",
          wo["service"]["exact_primary_service"] == prof["primary_service"]
          == tgt["exact_service"] == "outdoor design & build")

    # ---- full ad inventory --------------------------------------------------
    ads = []
    for r in q("""SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type,
                         ad_group_ad.resource_name, ad_group_ad.ad.final_urls,
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
                         ad_group.id, ad_group.name, campaign.id, campaign.name,
                         campaign.status
                  FROM ad_group_ad WHERE campaign.status = ENABLED"""):
        a = r.ad_group_ad.ad
        rsa = a.responsive_search_ad
        ads.append({
            "resource_name": r.ad_group_ad.resource_name, "ad_id": str(a.id),
            "status": E(r.ad_group_ad.status), "type": E(a.type_),
            "final_urls": list(a.final_urls),
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
            "policy_topics": [{"topic": t.topic, "type": E(t.type_)}
                              for t in r.ad_group_ad.policy_summary.policy_topic_entries],
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
        })
    snap["ads"] = ads
    by_rn = {a["resource_name"]: a for a in ads}
    targets = [by_rn[a["resource_name"]] for a in actions if a["resource_name"] in by_rn]
    old_ids = {a["ad_id"] for a in before_create["existing_ads"]}
    old_ads = [a for a in ads if a["ad_id"] in old_ids]

    # ---- 7: inventory ------------------------------------------------------
    check("inventory: 48 total RSAs on live campaigns", len(ads) == 48, f"{len(ads)}")
    check("inventory: 24 ENABLED + 24 PAUSED",
          dict(Counter(a["status"] for a in ads)) == {"ENABLED": 24, "PAUSED": 24},
          str(dict(Counter(a["status"] for a in ads))))
    per_ag = Counter(a["ad_group_id"] for a in ads)
    check("inventory: exactly two RSAs in each of the 24 live ad groups",
          len(per_ag) == 24 and set(per_ag.values()) == {2},
          f"{len(per_ag)} ad groups, per-group {sorted(set(per_ag.values()))}")
    check("inventory: all 24 original RSAs are ENABLED",
          all(a["status"] == "ENABLED" for a in old_ads), f"{len(old_ads)} originals")

    # ---- 12/13: targets still exist, still paused, not edited --------------
    check("targets: all 24 target ads still exist", len(targets) == 24, f"{len(targets)}")
    already = [a for a in targets if a["status"] != "PAUSED"]
    check("targets: none has already been enabled by another user or process",
          not already, str([(a["ad_id"], a["status"]) for a in already]))
    check("targets: none duplicated - each ad group holds exactly one target",
          len({a["ad_group_id"] for a in targets}) == 24)

    # ---- 8: originals byte-identical to the before snapshot ----------------
    before_by_id = {a["ad_id"]: a for a in before_create["existing_ads"]}
    drift_old = []
    for a in old_ads:
        b = before_by_id[a["ad_id"]]
        if a["headlines"] != b["headlines"]:
            drift_old.append(f"{a['ad_id']} headlines")
        if a["descriptions"] != b["descriptions"]:
            drift_old.append(f"{a['ad_id']} descriptions")
        if a["final_urls"] != b["final_urls"]:
            drift_old.append(f"{a['ad_id']} final_urls")
        if a["status"] != b["status"]:
            drift_old.append(f"{a['ad_id']} status")
    check("no drift: all 24 original RSAs byte-identical to the before snapshot",
          not drift_old, "; ".join(drift_old[:6]))

    # ---- 9/10: new ads byte-identical to the frozen Phase 2 plan -----------
    drift_new = []
    for a in targets:
        want = planned_p2.get(a["ad_group_id"])
        if not want:
            drift_new.append(f"{a['ad_id']} ad group not in the approved plan")
            continue
        if a["headlines"] != want["headlines"]:
            drift_new.append(f"{a['ad_id']} headlines")
        if a["descriptions"] != want["descriptions"]:
            drift_new.append(f"{a['ad_id']} descriptions")
        if a["final_urls"] != [want["final_url"]]:
            drift_new.append(f"{a['ad_id']} final_url")
        if a["path1"] != want["path1"] or a["path2"] != want["path2"]:
            drift_new.append(f"{a['ad_id']} paths")
        if a["campaign_id"] != want["campaign_id"]:
            drift_new.append(f"{a['ad_id']} campaign association")
        if a["pinned"]:
            drift_new.append(f"{a['ad_id']} pinning appeared")
        if len(a["headlines"]) != 15 or len(a["descriptions"]) != 4:
            drift_new.append(f"{a['ad_id']} counts")
        if a["tracking_url_template"] or a["final_url_suffix"]:
            drift_new.append(f"{a['ad_id']} tracking template or suffix appeared")
    check("no drift: all 24 paused RSAs byte-identical to the approved Phase 2 plan "
          "(headlines, descriptions, URL, paths, ad group, pinning)",
          not drift_new, "; ".join(drift_new[:6]))

    # CSV cross-check
    rows = {r["ad_group_id"]: r for r in
            csv.DictReader(Path(args.csv).open(encoding="utf-8"))}
    csv_drift = []
    for a in targets:
        r = rows.get(a["ad_group_id"])
        if not r:
            csv_drift.append(a["ad_group_id"])
            continue
        if r["final_url"] != a["final_urls"][0]:
            csv_drift.append(f"{a['ad_id']} url")
        for i, h in enumerate(a["headlines"], 1):
            if r.get(f"H{i:02d}") != h:
                csv_drift.append(f"{a['ad_id']} H{i:02d}")
    check("no drift: live copy also matches 16_rsa_rebuild_plan.csv",
          not csv_drift, "; ".join(csv_drift[:6]))

    # ---- 11: landing-page mapping ------------------------------------------
    dests = Counter(a["final_urls"][0] for a in targets)
    check("mapping: 13 unique destinations", len(dests) == 13, f"{len(dests)}")
    check("mapping: maximum reuse of any destination is two ad groups",
          max(dests.values()) == 2, f"max {max(dests.values())}")
    main_site = [a for a in targets if "offeraustin." not in a["final_urls"][0]]
    check("mapping: exactly one main-site exception, Hardscaping | Near Me",
          len(main_site) == 1 and main_site[0]["ad_group_name"] == "Hardscaping | Near Me",
          str([a["ad_group_name"] for a in main_site]))
    themed = defaultdict(set)
    for a in targets:
        themed[a["ad_group_name"].split("|")[0].strip()].add(a["final_urls"][0])
    cross = {t: sorted(u) for t, u in themed.items() if len(u) > 1}
    check("mapping: each theme's pair shares one offer page, except the approved exception",
          set(cross) <= {"Hardscaping"}, str(list(cross)))
    snap["destination_map"] = {a["ad_id"]: a["final_urls"][0] for a in targets}

    # ---- GOOGLE POLICY REVIEW GATE -----------------------------------------
    blocked = []
    for a in targets:
        reasons = []
        if a["approval_status"] not in CLEARED_APPROVAL:
            reasons.append(f"approval_status={a['approval_status']}")
        if a["review_status"] not in CLEARED_REVIEW:
            reasons.append(f"review_status={a['review_status']}")
        if a["policy_topics"]:
            reasons.append(f"policy_topics={a['policy_topics']}")
        if reasons:
            blocked.append({"ad_id": a["ad_id"], "ad_group": a["ad_group_name"],
                            "campaign": a["campaign_name"],
                            "approval_status": a["approval_status"],
                            "review_status": a["review_status"],
                            "ad_strength": a["ad_strength"],
                            "policy_topics": a["policy_topics"],
                            "reasons": reasons})
    gate_detail["blocked"] = blocked
    gate_detail["approval_tally"] = dict(Counter(a["approval_status"] for a in targets))
    gate_detail["review_tally"] = dict(Counter(a["review_status"] for a in targets))
    snap["policy_gate"] = gate_detail
    check("POLICY GATE: all 24 ads fully cleared by Google review "
          "(APPROVED + REVIEWED + zero policy topics)",
          not blocked, f"{len(blocked)} of 24 not cleared")

    Path(args.out).write_text(json.dumps(snap, indent=2, default=str), encoding="utf-8")

    print("=" * 98)
    print("ENABLE PREFLIGHT")
    print("=" * 98)
    failed = 0
    for name, ok, detail in results:
        if not ok:
            failed += 1
        print(f"  [{'PASS' if ok else '**STOP**':8}] {name}" + (f"  ({detail})" if detail else ""))
    print("-" * 98)
    print(f"  {len(results) - failed} passed, {failed} failed")

    print("\n  POLICY STATE OF ALL 24 TARGET ADS")
    print(f"    approval_status: {gate_detail['approval_tally']}")
    print(f"    review_status:   {gate_detail['review_tally']}")
    if blocked:
        print(f"\n  {len(blocked)} AD(S) BLOCK EXECUTION:")
        for b in blocked:
            print(f"    {b['ad_id']:<14} {b['ad_group']:<28} {b['campaign'][:34]:<34} "
                  f"{'; '.join(b['reasons'])}")
    if failed:
        print("\n  STOP. Approval is VOID for this run. No external change may be made.")
    else:
        print("\n  All gates passed. The approved ENABLE fingerprint is valid for execution.")
    print(f"  preflight snapshot: {args.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
