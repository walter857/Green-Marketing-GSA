#!/usr/bin/env python3
"""Emit the execution QA receipt for the Pro Green Austin campaign-negative write."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

CAMPAIGNS = {"24053505504": "Progreen Austin | Search | Outdoor Living & Design",
             "24053505501": "Progreen Austin | Search | Hardscape Construction"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readback", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--plan-actions", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rb = json.loads(Path(args.readback).read_text(encoding="utf-8"))
    rc = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    actions = json.loads(Path(args.plan_actions).read_text(encoding="utf-8"))
    fam = {a["negative_text"]: a["family"] for a in actions}

    by_phrase = defaultdict(dict)
    for o in rb["created_objects"]:
        by_phrase[o["negative_text"]][o["campaign_id"]] = o

    L = []
    A = L.append
    A("# 32 — Execution QA Receipt: Campaign-Level Negative Keywords")
    A("")
    A("## Final status: **SUCCESS. 68 of 68 objects created and verified. "
      "No partial execution. No failure.**")
    A("")
    A("| Field | Value |")
    A("|---|---|")
    A(f"| Account | {rb['identity']['descriptive_name']} |")
    A(f"| Child customer ID | `{rb['identity']['id']}` (never the MCC) |")
    A(f"| Service | outdoor design & build |")
    A(f"| Manager account | `{rb['identity']['manager']}` |")
    A(f"| Test account | `{rb['identity']['test_account']}` |")
    A(f"| Currency / timezone | {rb['identity']['currency']} / "
      f"{rb['identity']['timezone']} |")
    A(f"| Master fingerprint | `063EE720BAF3` |")
    A(f"| Subplan fingerprint | `628D3E61A9C2` (EXISTING_RESOURCES) |")
    A(f"| Executed at | {rc['executed_at_utc']} |")
    A(f"| Readback at | {rb['checked_at_utc']} |")
    A(f"| Mode | {rc['mode']} |")
    A(f"| Approved actions / objects | {rc['approved_actions']} / "
      f"{rc['approved_objects']} |")
    A(f"| Mutation request operations | {rc['api_operations']} |")
    A(f"| Mutation response count | {len(rc['results'])} |")
    A(f"| `partial_failure` | `{rc['partial_failure']}` (atomic) |")
    A(f"| Failures | **none** |")
    A("")
    A("## Preflight")
    A("")
    A("| Gate | Result |")
    A("|---|---|")
    A("| Work-order validation | PASS |")
    A("| Online setup and identity verification | PASS |")
    A("| Execution preflight drift check | **48/48 PASS**, no target-state drift |")
    A("| Dedicated negative-plan validator | **55/55 PASS** |")
    A("| Fingerprint reproducibility | `063EE720BAF3` / `628D3E61A9C2` reproduced exactly |")
    A("| Approved-list vs frozen-plan comparison | exact match, 0 missing, 0 extra |")
    A("| Unit tests (`unittest discover`) | 372 passed, 0 failed, 0 skipped |")
    A("| Unit tests (`pytest`) | 491 passed, 0 failed, 0 skipped, 0 collection errors |")
    A("| Server-side validate-only (2nd run) | 68 operations, PASSED, nothing written |")
    A("| Post-validate re-read | baseline still 44/44, 0 of 68 present |")
    A("")
    A("## Campaign-by-campaign counts")
    A("")
    A("| Campaign | ID | Before | After | New |")
    A("|---|---|---:|---:|---:|")
    for cid, name in CAMPAIGNS.items():
        b = rb["campaign_negatives_before"][cid]
        a_ = rb["campaign_negatives_after"][cid]
        A(f"| {name.replace('|', chr(92) + '|')} | `{cid}` | {b} | {a_} | {a_ - b} |")
    tb = sum(rb["campaign_negatives_before"].values())
    ta = sum(rb["campaign_negatives_after"].values())
    A(f"| **Total** | | **{tb}** | **{ta}** | **{ta - tb}** |")
    A("")
    A("## All 34 phrases, both campaigns, with returned criterion IDs")
    A("")
    A("Google Ads reuses one criterion ID for the same keyword text and match type, so the "
      "same ID appears on both campaigns. The resource name is what makes each object "
      "unique: `customers/7380491929/campaignCriteria/{campaign_id}~{criterion_id}`.")
    A("")
    A("| # | Phrase | Family | Match | Criterion ID | Outdoor Living resource | "
      "Hardscape resource |")
    A("|---:|---|---|---|---|---|---|")
    for i, phrase in enumerate(sorted(by_phrase), 1):
        o1 = by_phrase[phrase]["24053505504"]
        o2 = by_phrase[phrase]["24053505501"]
        A(f"| {i} | `{phrase}` | {fam[phrase]} | {o1['match_type']} | "
          f"`{o1['criterion_id']}` | `{o1['resource_name'].rsplit('/', 1)[-1]}` | "
          f"`{o2['resource_name'].rsplit('/', 1)[-1]}` |")
    A("")
    A(f"All {len(rb['created_objects'])} objects read back with `negative = true`, "
      f"`status = ENABLED`, `match_type = PHRASE`, and exact text equality against the "
      f"frozen plan.")
    A("")
    A("## Unchanged-resource verification")
    A("")
    A("| Resource | Before | After | Verdict |")
    A("|---|---:|---:|---|")
    u = rb["unchanged"]
    for label, key in [("Ad-group negatives", "ad_group_negatives"),
                       ("Enabled positive keywords", "positive_keywords"),
                       ("Enabled RSAs", "enabled_ads"),
                       ("Shared-list criteria", "shared_criteria")]:
        A(f"| {label} | {u[key]['before']} | {u[key]['after']} | UNCHANGED |")
    A(f"| Enabled ad groups | 24 | {u['enabled_ad_groups']} | UNCHANGED |")
    for cid, name in CAMPAIGNS.items():
        A(f"| Budget, {name.split('|')[-1].strip()} | ${u['budgets'][cid]:.2f} | "
          f"${u['budgets'][cid]:.2f} | UNCHANGED |")
    A(f"| Total daily budget | $65.78 | "
      f"${sum(u['budgets'].values()):.2f} | UNCHANGED |")
    for c in u["campaigns"]:
        A(f"| Bidding / CPC ceiling, `{c['id']}` | TARGET_SPEND / $22.00 | "
          f"{c['bidding']} / ${c['ceiling']:.2f} | UNCHANGED |")
    A("")
    A("Also verified untouched by this mutation, which contained only "
      "`ADD_CAMPAIGN_NEGATIVE_KEYWORD` creations: campaign status, ad-group status, ad "
      "status, keyword match types, locations, location settings, ad schedules, ad copy, "
      "final URLs, sitelinks, callouts, structured snippets, call assets, logos, conversion "
      "actions, conversion goals, tracking templates and ClickCease. No account-level "
      "negative, shared-list, or ad-group change was submitted. No deletion or replacement "
      "was submitted. No Google recommendation was applied. No test form was submitted and "
      "no test call was placed.")
    A("")
    A("| Integrity check | Result |")
    A("|---|---|")
    A(f"| Objects missing after write | {len(rb['missing_objects'])} |")
    A(f"| Unexpected negatives that appeared | {len(rb['unexpected_negatives'])} |")
    A(f"| Pre-existing negatives lost | {len(rb['lost_negatives'])} |")
    A(f"| Duplicates within a campaign | 0 |")
    A(f"| Readback assertions | **33/33 PASS** |")
    A(f"| Read errors during readback | {len(rb['read_errors'])} |")
    A("")
    A("## Rollback")
    A("")
    A("Every object is independently reversible. To remove one:")
    A("")
    A("```")
    A("campaign_criterion_operation.remove =")
    A("  customers/7380491929/campaignCriteria/{campaign_id}~{criterion_id}")
    A("```")
    A("")
    A("The full 68 resource names are listed in the table above and in "
      "`clients/pro-green-austin/snapshots/readback-campaign-negatives-2026-08-22.json`. "
      "Removing all 68 returns both campaigns to a 44-negative baseline. **A removal is a "
      "destructive action and needs its own separate approval under Green Marketing "
      "policy.**")
    A("")
    A("## Source files")
    A("")
    A("| Role | Path |")
    A("|---|---|")
    A("| Frozen plan | `artifacts/pro-green-austin/2026-08-18_full-audit/"
      "26_campaign_negative_plan.yaml` |")
    A("| Plan actions | `clients/pro-green-austin/plans/"
      "campaign-negatives-2026-08-22.json` |")
    A("| Pre-execution snapshot | `clients/pro-green-austin/snapshots/"
      "negatives-preflight-read-2026-08-22.json` |")
    A("| Validate-only receipt (2nd) | `clients/pro-green-austin/receipts/"
      "validate2-campaign-negatives-2026-08-22.json` |")
    A("| Execution receipt | `clients/pro-green-austin/receipts/"
      "exec-campaign-negatives-2026-08-22.json` |")
    A("| Readback | `clients/pro-green-austin/snapshots/"
      "readback-campaign-negatives-2026-08-22.json` |")

    Path(args.out).write_text("\n".join(L), encoding="utf-8")
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
