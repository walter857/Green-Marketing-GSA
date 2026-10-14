#!/usr/bin/env python3
"""Section 8.5 + 8.6 preflight for the four authorized Softwind L&M packages.

Read-only and local. Verifies, for each package:
  8.5  exactly one plan file, recomputed fingerprint, package id, subplan,
       target customer, operation count, current/proposed/rollback values, and
       that every operation appears in 20-all-operations.csv
  8.6  the package-specific safety assertions from the run instruction

Exits non-zero if any package fails. Writes 26-preflight-exec.json
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.safety import approval_code  # noqa: E402

B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PKG = B / "10-change-packages-v2"
CID = "2429758629"
PATIO, PAVERS = "23484806108", "23489296528"

AUTHORIZED = {
    "PLAN-SLM-BID-2": {"subplan": "EXISTING_RESOURCES", "fp": "8C71888E09CC", "ops": 2},
    "PLAN-SLM-BUD-2": {"subplan": "BUDGET", "fp": "BB9869E17E37", "ops": 2},
    "PLAN-SLM-KW-2": {"subplan": "STATUS", "fp": "B7A11B246D74", "ops": 7},
    "PLAN-SLM-NEG-2": {"subplan": "EXISTING_RESOURCES", "fp": "2CD5644B5504", "ops": 99},
}
PROTECTED_UNRESOLVED = [
    "driveway", "concrete", "bluestone", "blue stone", "masonry", "mason",
    "resurfac", "refinish", "pool deck", "pool patio", "coping",
]
PROTECTED_WORDS = {"near me", "quote", "price", "pricing", "cost", "best",
                   "hire", "local", "emergency"}
ASPHALT_INTENT = ("asphalt", "blacktop", "sealcoat", "tar and chip", "paving",
                  "macadam")
IN_SCOPE_KW_MARKERS = ("patio", "paver", "hardscape", "walkway", "stone")


def norm(t):
    return " ".join(str(t).lower().split())


def phrase_hits(q, n):
    return re.search(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", q) is not None


def main() -> int:
    snap = json.loads((B / "25-pre-execution-snapshot-2026-09-03-2303.json")
                      .read_text(encoding="utf-8"))
    ops_csv = list(csv.DictReader((B / "20-all-operations.csv").open(encoding="utf-8")))
    csv_ids = {(r["package_id"], r["action_id"]) for r in ops_csv}
    report, failed = {}, []

    for name, want in AUTHORIZED.items():
        res = {"checks": {}, "verdict": "PASS"}

        def check(k, ok, detail=""):
            res["checks"][k] = {"pass": bool(ok), "detail": detail}
            if not ok:
                res["verdict"] = "FAIL"

        # ---- 8.5 exactly one plan file ----
        matches = sorted(PKG.glob("%s*.yaml" % name))
        exact = [m for m in matches if m.stem == name]
        check("exactly_one_plan_file", len(exact) == 1 and len(matches) == 1,
              "found %s" % [m.name for m in matches])
        if len(exact) != 1:
            report[name] = res; failed.append(name); continue
        doc = yaml.safe_load(exact[0].read_text(encoding="utf-8"))["change_plan"]
        sp = doc["subplan_used"]
        actions = doc["subplans"][sp]["actions"]

        check("package_id", doc["plan_name"] == name, doc["plan_name"])
        check("subplan", sp == want["subplan"], sp)
        check("target_customer", doc["target"]["child_customer_id"] == CID,
              doc["target"]["child_customer_id"])
        check("target_account_name",
              doc["target"]["exact_child_account_name"]
              == "Softwind Landscape & Masonry - Live",
              doc["target"]["exact_child_account_name"])
        check("operation_count", len(actions) == want["ops"],
              "%d (want %d)" % (len(actions), want["ops"]))
        recomputed = approval_code({"target": doc["target"], "subplan": sp,
                                    "actions": actions})
        check("fingerprint_recomputed_matches_authorized",
              recomputed == want["fp"], "%s vs authorized %s" % (recomputed, want["fp"]))
        check("fingerprint_stored_in_file_matches",
              doc.get("fingerprint") == want["fp"], str(doc.get("fingerprint")))
        check("every_action_has_rollback",
              all(str(a.get("rollback_state", "")).strip() for a in actions))
        check("every_action_has_current_and_proposed",
              all(str(a.get("current_state", "")).strip()
                  and str(a.get("proposed_state", "")).strip() for a in actions))
        check("every_action_in_operations_csv",
              all((name, a["action_id"]) in csv_ids for a in actions))
        check("source_snapshot_recorded",
              bool(doc["target"].get("baseline_snapshot")),
              doc["target"].get("baseline_snapshot", ""))

        # ---- 8.6 per package ----
        if name == "PLAN-SLM-BID-2":
            camps = {a["resource_id"]: a for a in actions}
            check("targets_exactly_patio_and_pavers",
                  set(camps) == {PATIO, PAVERS}, str(sorted(camps)))
            live_ok, ceil_ok, strat_ok = True, True, True
            for cid, a in camps.items():
                c = snap["campaigns"][cid]
                live_ok &= (c["bidding_strategy_type"] == "TARGET_SPEND")
                strat_ok &= (c["portfolio_strategy"] is None)
                live_ok &= (c["cpc_bid_ceiling"] is None)
                micros = int(a["proposed_state"].split("= ")[1].split(" ")[0])
                want_m = 16000000 if cid == PATIO else 18000000
                ceil_ok &= (micros == want_m)
                check("no_strategy_field_in_proposal_%s" % cid,
                      "bidding_strategy" not in a["proposed_state"].lower()
                      and "maximize" not in a["proposed_state"].lower())
            check("both_still_maximize_clicks_and_unset_ceiling", live_ok)
            check("no_portfolio_strategy", strat_ok)
            check("ceilings_are_exactly_16_and_18", ceil_ok)

        if name == "PLAN-SLM-BUD-2":
            enabled = {k: v for k, v in snap["campaigns"].items()
                       if v["status"] == "ENABLED"}
            check("exactly_patio_and_pavers_enabled",
                  set(enabled) == {PATIO, PAVERS}, str(sorted(enabled)))
            check("no_shared_budget_anywhere",
                  not any(v["budget_explicitly_shared"] or v["budget_reference_count"] > 1
                          for v in snap["campaigns"].values()))
            prop = {}
            for a in actions:
                m = int(a["proposed_state"].split("amount_micros = ")[1].split(" ")[0])
                prop[a["campaign_id"]] = m / 1e6
                bid_now = snap["campaigns"][a["campaign_id"]]["budget_id"]
                check("budget_resource_id_matches_live_%s" % a["campaign_id"],
                      a["resource_id"] == bid_now,
                      "%s vs live %s" % (a["resource_id"], bid_now))
            check("budgets_are_exactly_24_and_32",
                  prop == {PATIO: 24.0, PAVERS: 32.0}, str(prop))
            mtd = snap["mtd_account"][0]["cost"]
            projection = mtd + sum(prop.values()) * 27
            check("projection_at_or_below_2000", projection <= 2000.0,
                  "$%.2f" % projection)
            res["projection"] = round(projection, 2)
            res["headroom"] = round(2000.0 - projection, 2)
            paused_mtd = sum(r["cost"] for r in snap["mtd_by_campaign"]
                             if snap["campaigns"].get(r["campaign_id"], {})
                             .get("status") != "ENABLED")
            check("paused_campaigns_spent_nothing_mtd", paused_mtd == 0.0,
                  "$%.2f" % paused_mtd)

        if name == "PLAN-SLM-KW-2":
            all_enabled, all_asphalt, none_inscope, all_pavers = True, True, True, True
            for a in actions:
                key = "%s~%s" % (a["ad_group_id"], a["criterion_id"])
                k = snap["keywords"].get(key)
                if not k:
                    check("criterion_exists_%s" % a["criterion_id"], False, key)
                    all_enabled = False; continue
                all_enabled &= (k["status"] == "ENABLED")
                all_pavers &= (k["campaign_id"] == PAVERS)
                t = norm(k["text"])
                all_asphalt &= any(w in t for w in ASPHALT_INTENT)
                # must not be an in-scope or protected-unresolved keyword
                if any(w in t for w in IN_SCOPE_KW_MARKERS):
                    none_inscope = False
                if any(w in t for w in PROTECTED_UNRESOLVED):
                    none_inscope = False
                check("live_text_matches_plan_%s" % a["criterion_id"],
                      norm(a["keyword_text"]) == t
                      and a["match_type"] == k["match_type"],
                      "%r/%s vs live %r/%s" % (a["keyword_text"], a["match_type"],
                                               k["text"], k["match_type"]))
            check("all_seven_currently_enabled", all_enabled)
            check("all_seven_in_pavers", all_pavers)
            check("all_seven_asphalt_blacktop_or_sealcoat_intent", all_asphalt)
            check("none_is_inscope_or_protected_unresolved", none_inscope)
            check("all_operations_are_pause_only",
                  all(a["operation"] == "PAUSE_AD_GROUP_CRITERION"
                      and a["proposed_state"] == "PAUSED" for a in actions))

        if name == "PLAN-SLM-NEG-2":
            check("exactly_99_operations", len(actions) == 99, str(len(actions)))
            check("all_phrase_match",
                  all(a["match_type"] == "PHRASE" for a in actions),
                  str(Counter(a["match_type"] for a in actions)))
            check("all_target_patio_or_pavers",
                  all(a["campaign_id"] in (PATIO, PAVERS) for a in actions),
                  str(Counter(a["campaign_id"] for a in actions)))
            check("all_campaign_level",
                  all(a["level"] == "CAMPAIGN" for a in actions))
            check("no_account_level_shared_list_touched",
                  all(a["operation"] == "ADD_CAMPAIGN_NEGATIVE_KEYWORD"
                      for a in actions))
            # collision vs currently ENABLED positive keywords
            enabled_kw = {}
            for k in snap["keywords"].values():
                if (not k["negative"] and k["campaign_id"] in (PATIO, PAVERS)
                        and k["status"] == "ENABLED"
                        and k["ad_group_status"] == "ENABLED"):
                    enabled_kw.setdefault(k["campaign_id"], []).append(norm(k["text"]))
            kw1_paused = {norm(a["keyword_text"]) for a in
                          yaml.safe_load((PKG / "PLAN-SLM-KW-2.yaml")
                                         .read_text(encoding="utf-8"))
                          ["change_plan"]["subplans"]["STATUS"]["actions"]}
            collisions, protected_hits, word_hits = [], [], []
            for a in actions:
                t = norm(a["negative_text"])
                for kw in enabled_kw.get(a["campaign_id"], []):
                    if phrase_hits(kw, t) and kw not in kw1_paused:
                        collisions.append((a["action_id"], t, kw))
                for th in PROTECTED_UNRESOLVED:
                    if th in t:
                        protected_hits.append((a["action_id"], t, th))
                if t in PROTECTED_WORDS:
                    word_hits.append((a["action_id"], t))
            check("no_collision_with_enabled_positive_keyword",
                  not collisions, str(collisions[:5]))
            check("no_protected_unresolved_service_blocked",
                  not protected_hits, str(protected_hits[:5]))
            check("no_bare_protected_buying_word", not word_hits, str(word_hits))
            existing = set()
            for v in snap["campaign_negatives"].values():
                existing.add((v["campaign_id"], norm(v["text"]), v["match_type"]))
            dupes = [a["action_id"] for a in actions
                     if (a["campaign_id"], norm(a["negative_text"]),
                         a["match_type"]) in existing]
            check("no_exact_duplicate_of_an_existing_negative",
                  not dupes, str(dupes[:5]))
            res["by_campaign"] = dict(Counter(a["campaign_name"] for a in actions))

        report[name] = res
        if res["verdict"] == "FAIL":
            failed.append(name)

    (B / "26-preflight-exec.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")

    for name, r in report.items():
        print("\n%-17s %s" % (name, r["verdict"]))
        for k, v in r["checks"].items():
            if not v["pass"]:
                print("   FAIL  %-52s %s" % (k, v["detail"]))
        npass = sum(1 for v in r["checks"].values() if v["pass"])
        print("   %d/%d checks passed" % (npass, len(r["checks"])))
        for extra in ("projection", "headroom", "by_campaign"):
            if extra in r:
                print("   %-14s %s" % (extra, r[extra]))
    print("\nPREFLIGHT: %s" % ("ALL PASS" if not failed else "FAILED: %s" % failed))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
