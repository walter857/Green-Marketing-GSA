#!/usr/bin/env python3
"""One row per proposed operation, across all five v2 packages.

Writes 20-all-operations.csv and 20-all-operations.md with the exact columns the
pre-approval QA gate requires. Local only.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PKG = B / "10-change-packages-v2"

COLUMNS = ["package_id", "priority", "action_id", "resource_type", "campaign",
           "ad_group", "resource_id", "current_value", "proposed_value",
           "evidence", "reason", "expected_effect", "risk", "rollback_value",
           "dependency", "approval_token", "package_fingerprint"]

PRIORITY = {"PLAN-SLM-BID-2": "P0-1", "PLAN-SLM-BUD-2": "P0-2",
            "PLAN-SLM-KW-2": "P0-3", "PLAN-SLM-NEG-2": "P0-4",
            "PLAN-SLM-CONV-2": "P0-5"}


def short(v, n=300):
    s = " ".join(str(v).split())
    return s if len(s) <= n else s[:n - 1] + "…"


def main() -> int:
    idx = json.loads((PKG / "00-index.json").read_text(encoding="utf-8"))
    rows = []
    for name, meta in idx.items():
        doc = yaml.safe_load((ROOT / meta["file"]).read_text(encoding="utf-8"))["change_plan"]
        sp = doc["subplan_used"]
        fp = doc["fingerprint"]
        token = ("python scripts/execute_approved_plan.py --plan %s --subplan %s "
                 "--fingerprint %s --out <receipt.json>" % (meta["file"], sp, fp))
        dep = "; ".join(doc.get("dependencies") or []) or "none"
        for a in doc["subplans"][sp]["actions"]:
            if name == "PLAN-SLM-BID-2":
                ev = ("strategy=%s, ceiling today=%s, avgCPC by month=%s, most "
                      "expensive day=%s, converting keyword CPCs=%s" % (
                          a["evidence"]["bidding_strategy_type"],
                          a["evidence"]["ceiling_today"],
                          a["evidence"]["avg_cpc_by_month"],
                          a["evidence"]["most_expensive_day_observed"],
                          [c["avg_cpc"] for c in a["evidence"]["converting_keyword_cpcs"]]))
                reason = ("No CPC ceiling exists, so nothing bounds the price of a "
                          "click under Maximize Clicks.")
                eff = a["expected_effect"]; risk = a["risk"]
            elif name == "PLAN-SLM-BUD-2":
                ev = a["evidence"]
                reason = ("Projected September spend exceeds the $2,000 account cap at "
                          "the current budgets.")
                eff = ("Reduces this campaign's daily exposure; combined projection "
                       "falls to $%s." % doc["account_wide_pacing"]["projection_proposed"])
                risk = "Fewer daily clicks in an account already buying 3-6 a day."
            elif name == "PLAN-SLM-KW-2":
                ev = ("authority=%s | all-time spend $%s, %s clicks, %s raw credits, "
                      "qualified leads %s" % (short(a["authority"], 200),
                                              a["alltime_cost"], a["alltime_clicks"],
                                              a["alltime_raw_credits"],
                                              a["qualified_leads"]))
                reason = a["reason"]
                eff = "Keyword stops entering auctions; history and ID are preserved."
                risk = ("Loses the asphalt lead route, which is the intent. Reversible "
                        "by setting status back to ENABLED.")
            elif name == "PLAN-SLM-NEG-2":
                ev = ("class=%s | authority=%s | blocks %s terms, $%s, %s clicks, %s "
                      "credits | source terms: %s | collision: %s (tested vs %s own "
                      "keywords, %s protected terms, %s existing negatives)" % (
                          a["classification"], short(a["authority"], 160),
                          a["blocks_terms"], a["blocks_cost"], a["blocks_clicks"],
                          a["blocks_conversions"], short(a["source_search_terms"], 120),
                          a["collision_test"], a["keywords_tested"],
                          a["protected_terms_tested"], a["existing_negatives_tested"]))
                reason = "Wrong-service or non-buyer intent, excluded by declared scope."
                eff = "Query no longer reaches this campaign."
                risk = ("A negative that is too broad blocks real demand. Every "
                        "candidate was collision-tested and 53 were rejected.")
            else:
                ev = ("day-level co-occurrence: fired %s days, twin fired %s days, "
                      "both %s days, alone %s days, identical counts %s" % (
                          a["duplicate_proof"]["days_demoted_action_fired"],
                          a["duplicate_proof"]["days_kept_action_fired"],
                          a["duplicate_proof"]["days_both_fired"],
                          a["duplicate_proof"]["days_demoted_action_fired_ALONE"],
                          a["duplicate_proof"]["same_day_identical_counts"]))
                reason = short(a["duplicate_proof"]["conclusion"], 260)
                eff = a["reporting_impact"]
                risk = a["campaign_learning_impact"]
            rows.append({
                "package_id": name, "priority": PRIORITY[name],
                "action_id": a["action_id"], "resource_type": a["resource_type"],
                "campaign": a.get("campaign_name") or a.get("resource_name") or "-",
                "ad_group": a.get("ad_group_name", "-"),
                "resource_id": a["resource_id"],
                "current_value": short(a["current_state"], 160),
                "proposed_value": short(a["proposed_state"], 160),
                "evidence": short(ev, 600), "reason": short(reason, 300),
                "expected_effect": short(eff, 300), "risk": short(risk, 300),
                "rollback_value": short(a["rollback_state"], 160),
                "dependency": a.get("dependency", dep) if name == "PLAN-SLM-NEG-2" else dep,
                "approval_token": token, "package_fingerprint": fp,
            })

    with (B / "20-all-operations.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader(); w.writerows(rows)

    # Markdown: full detail for the small packages, grouped detail for NEG.
    out = ["# Every proposed operation, one row each",
           "",
           "Total operations across the five packages: **%d**." % len(rows),
           "No operation below has been executed. All five passed `validate_only`",
           "through `scripts/execute_approved_plan.py` on 2026-09-03.", ""]
    for name in ("PLAN-SLM-BID-2", "PLAN-SLM-BUD-2", "PLAN-SLM-KW-2",
                 "PLAN-SLM-CONV-2", "PLAN-SLM-NEG-2"):
        rs = [r for r in rows if r["package_id"] == name]
        fp = rs[0]["package_fingerprint"]
        out += ["## %s  (%s) - %d operation(s), fingerprint `%s`"
                % (name, PRIORITY[name], len(rs), fp), ""]
        if name == "PLAN-SLM-NEG-2":
            out += ["| # | Campaign | Negative text | Match | Class | Blocks $ | Blocks clicks | Dependency |",
                    "|---|---|---|---|---|---|---|---|"]
            for r in rs:
                ev = r["evidence"]
                cls = ev.split("class=")[1].split(" |")[0]
                cost = ev.split(", $")[1].split(",")[0]
                clicks = ev.split("$%s, " % cost)[1].split(" clicks")[0]
                out.append("| %s | %s | `%s` | PHRASE | %s | %s | %s | %s |" % (
                    r["action_id"], r["campaign"],
                    r["proposed_value"].split("PHRASE ")[1].strip("'"),
                    cls, cost, clicks, r["dependency"]))
            out += ["", "Full per-row evidence including source search terms and the "
                        "collision-test result is in `20-all-operations.csv` and "
                        "`06-negative-plan-v2.csv`.", ""]
        else:
            for r in rs:
                out += ["### %s - %s `%s`" % (r["action_id"], r["resource_type"],
                                              r["resource_id"]),
                        "", "| Field | Value |", "|---|---|",
                        "| Campaign | %s |" % r["campaign"],
                        "| Ad group | %s |" % r["ad_group"],
                        "| Current | %s |" % r["current_value"],
                        "| Proposed | **%s** |" % r["proposed_value"],
                        "| Rollback | %s |" % r["rollback_value"],
                        "| Evidence | %s |" % r["evidence"],
                        "| Reason | %s |" % r["reason"],
                        "| Expected effect | %s |" % r["expected_effect"],
                        "| Risk | %s |" % r["risk"],
                        "| Dependency | %s |" % r["dependency"], ""]
    (B / "20-all-operations.md").write_text("\n".join(out), encoding="utf-8")
    print("wrote 20-all-operations.csv and .md  (%d operations)" % len(rows))
    for name in idx:
        print("   %-17s %3d rows" % (name, sum(1 for r in rows
                                               if r["package_id"] == name)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
