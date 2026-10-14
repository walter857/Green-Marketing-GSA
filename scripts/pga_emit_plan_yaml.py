#!/usr/bin/env python3
"""Emit the Pro Green Austin campaign-negative change plan in the project's plan shape."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

SUBPLANS = ["STATUS", "BUDGET", "EXISTING_RESOURCES", "CONVERSIONS",
            "CREATE_PAUSED", "SITE_OR_TRACKING", "ENABLE"]

VOID = {
    "MASTER": "2D87A5249784",
    "EXISTING_RESOURCES": "4EEF81C7F2F5",
    "status": "VOID. Never approved, never executed. The ad-group-scoped plan it "
              "fingerprinted is superseded by this campaign-scoped replacement. No external "
              "change is authorized under either code.",
    "superseded_artifacts": [
        "artifacts/pro-green-austin/2026-08-18_full-audit/21_search_term_verdicts_mtd.csv",
        "artifacts/pro-green-austin/2026-08-18_full-audit/22_adgroup_negative_plan_mtd.yaml",
        "artifacts/pro-green-austin/2026-08-18_full-audit/23_adgroup_negative_plan_mtd.csv",
        "clients/pro-green-austin/plans/adgroup-negatives-mtd-2026-08-21.json",
        "clients/pro-green-austin/receipts/validate-mtd-negatives-2026-08-21.json",
    ],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--actions", required=True)
    ap.add_argument("--reconciliation", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    actions = json.loads(Path(args.actions).read_text(encoding="utf-8"))
    rec = json.loads(Path(args.reconciliation).read_text(encoding="utf-8"))
    snap = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    ident = snap["identity"]

    plan = {
        "change_plan": {
            "version": 1,
            "phase": "PHASE 3 round 2 - month-to-date search-term hygiene, campaign scope. "
                     "Replaces the voided ad-group-scoped round 1.",
            "supersedes": VOID,
            "generated_on": "2026-08-22",
            "mode": "draft",
            "prepared_by": "Green Marketing Google Ads implementation agent",
            "approval_owner": "Green Marketing",
            "target": {
                "exact_child_account_name": ident["descriptive_name"],
                "child_customer_id": ident["id"],
                "manager_customer_id": "3373711342",
                "exact_service": "outdoor design & build",
                "vertical": "hardscaping",
                "market": "Austin, Texas",
                "account_timezone": ident["time_zone"],
                "market_timezone": "America/Chicago",
                "currency": ident["currency_code"],
                "manager_account": ident["manager"],
                "test_account": ident["test_account"],
                "snapshot": args.snapshot,
                "snapshot_read_started_utc": snap["read_started_utc"],
                "snapshot_read_finished_utc": snap["read_finished_utc"],
                "snapshot_read_errors": len(snap["read_errors"]),
                "search_term_window": f"{snap['window']['start']}..{snap['window']['end']}",
                "completed_days": rec["completed_days"],
                "partial_day": rec["partial_day"],
                "latest_available_search_term_date":
                    rec["latest_available_search_term_date"],
                "in_scope_campaigns": [
                    {"id": "24053505504",
                     "name": "Progreen Austin | Search | Outdoor Living & Design",
                     "resource_name": "customers/7380491929/campaigns/24053505504",
                     "status": "ENABLED"},
                    {"id": "24053505501",
                     "name": "Progreen Austin | Search | Hardscape Construction",
                     "resource_name": "customers/7380491929/campaigns/24053505501",
                     "status": "ENABLED"},
                ],
            },
            "external_writes_performed": "NONE",
            "findings": {
                "corpus": {
                    "search_term_rows": rec["source"]["rows"],
                    "distinct_raw_terms": rec["source"]["distinct_raw"],
                    "distinct_normalized_terms": rec["source"]["distinct_norm"],
                    "impressions": rec["source"]["impressions"],
                    "clicks": rec["source"]["clicks"],
                    "visible_search_term_cost": rec["source"]["cost"],
                    "conversions": rec["source"]["conversions"],
                    "conversion_value": rec["source"]["conversion_value"],
                    "in_scope_campaign_cost": rec["campaign_total_cost"],
                    "visible_cost_coverage_pct": rec["visible_cost_coverage_pct"],
                    "limitation":
                        "Google withholds low-volume search terms, so "
                        f"{round(100 - rec['visible_cost_coverage_pct'], 2)}% of this "
                        "month's in-scope spend has no visible search term. No negative "
                        "list can protect against queries Google does not disclose, and "
                        "nothing in this plan assumes the export is complete.",
                    "current_day_data":
                        "Google Ads had released no search-term or campaign rows for "
                        f"{rec['partial_day']} at the time of the read "
                        f"({snap['read_started_utc']}). The latest available date in both "
                        f"the search-term and the campaign series is "
                        f"{rec['latest_available_search_term_date']}. The partial-day "
                        "segment is therefore empty, not estimated.",
                },
                "verdicts": rec["by_verdict"],
                "reconciliation": {
                    "source_equals_verdict": rec["reconciles"],
                    "source": rec["source"],
                    "verdict_output": rec["verdict_output"],
                    "duplicate_terms": len(rec["duplicate_terms"]),
                    "extra_rows_from_duplicates":
                        sum(d["rows"] - 1 for d in rec["duplicate_terms"]),
                },
                "candidates": {
                    "unique_phrases": rec["unique_candidate_phrases"],
                    "by_family": rec["phrases_by_family"],
                    "base_target_count": rec["base_target_count"],
                    "removed_already_effectively_blocked": 0,
                    "removed_for_conflict": 0,
                    "proposed_targets": rec["targets_proposed"],
                    "by_campaign": rec["targets_by_campaign"],
                },
            },
            "families_deliberately_not_negatived": [
                {"family": "generic_landscaping",
                 "why_not": "Explicitly protected. 'landscaper near me' converted on this "
                            "account (1 conversion, $47.22 all-time) and the family "
                            "represents services the client sells. Negative keywords do not "
                            "match close variants, so blocking the plural would not block "
                            "the singular, and neither is proposed.",
                 "recommendation_only": "A dedicated generic-landscaping ad group with its "
                                        "own bid and destination is the correct structural "
                                        "fix. Not proposed here: the 48-RSA test started "
                                        "2026-08-20 and must not gain an unrelated variable."},
                {"family": "client_brand",
                 "why_not": "'progreen landscape solutions' converted. The client's own "
                            "brand is never blocked."},
                {"family": "protected_buyer_intent",
                 "why_not": "quote, price, pricing, cost, hire, contractor, company, local, "
                            "near me and emergency intent all stay eligible per Green "
                            "Marketing policy."},
                {"family": "adjacent_services",
                 "why_not": "'paving contractors near me' and 'deck builder near me' stay "
                            "eligible. Deck construction and concrete are verified "
                            "first-party Austin services, so these are landing-page gaps and "
                            "expansion candidates, not waste."},
                {"family": "manufacturer_product_brands",
                 "why_not": "Apollo Opening Roof, StruXure, SYNLawn and Vuba are product "
                            "manufacturers, not landscaping competitors. Pergolas and "
                            "artificial turf are verified Pro Green services, so these "
                            "queries carry real buying intent. This reverses the previous "
                            "plan's competitor classification of 'apollo pergola'."},
                {"family": "unverified_brand_shaped_queries",
                 "why_not": "76 brand-shaped queries were found that the previous summary "
                            "never listed. None could be confirmed against reliable evidence "
                            "in this pass, and all produced 0 clicks and $0.00. Reported in "
                            "the reconciliation report, not blocked."},
            ],
            "subplans": {name: {"actions": [], "empty_reason": "not part of this package"}
                         for name in SUBPLANS},
        }
    }
    plan["change_plan"]["subplans"]["EXISTING_RESOURCES"] = {"actions": actions}

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        yaml.safe_dump(plan, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8")
    print(f"written: {out}")
    print(f"  EXISTING_RESOURCES actions={len(actions)} "
          f"objects={sum(a['object_count'] for a in actions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
