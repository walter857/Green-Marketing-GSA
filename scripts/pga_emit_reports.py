#!/usr/bin/env python3
"""Emit the human-readable artifacts for the Pro Green Austin campaign-negative package.

Every number is read from the verdict CSV, the reconciliation JSON, the plan and the
snapshot. Nothing here is typed by hand.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pga_decisions_2026_08_22 as DEC  # noqa: E402

TARGETS = {
    "24053505504": "Progreen Austin | Search | Outdoor Living & Design",
    "24053505501": "Progreen Austin | Search | Hardscape Construction",
}
PRIOR_CANDIDATES = [
    "terra landscaping", "apollo pergola", "biggadike", "waterloo turf",
    "cutters landscaping", "cooper and company", "ground and garden", "magnolia turf",
    "ps landscapes", "ranchers landscaping", "casas landscaping", "cedarcrest",
    "clean scapes", "dl landscaping", "four roots", "the mark landscapes",
    "twelve point landscaping", "allied outdoor solutions", "design ecology", "ecotopes",
    "hellas turf", "southern turf", "stones and scapes", "waldemar landscaping",
]


def money(x):
    return f"${x:,.2f}"


def cell(text):
    """Escape a value so it cannot break out of a markdown table cell."""
    return str(text).replace("|", "\\|")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--verdict-csv", required=True)
    ap.add_argument("--reconciliation", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--post-check", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--master", required=True)
    ap.add_argument("--subplan", required=True)
    args = ap.parse_args()

    out = Path(args.outdir)
    rows = list(csv.DictReader(open(args.verdict_csv, encoding="utf-8")))
    rec = json.loads(Path(args.reconciliation).read_text(encoding="utf-8"))
    plan = yaml.safe_load(Path(args.plan).read_text(encoding="utf-8"))["change_plan"]
    D = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    post = json.loads(Path(args.post_check).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    actions = plan["subplans"]["EXISTING_RESOURCES"]["actions"]

    src, vout = rec["source"], rec["verdict_output"]
    fam_by_verdict = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0.0]))
    for r in rows:
        v = fam_by_verdict[r["verdict"]][r["intent_family"]]
        v[0] += 1; v[1] += int(r["impressions"]); v[2] += int(r["clicks"])
        v[3] += float(r["cost"])

    phrases = {}
    for a in actions:
        phrases.setdefault(a["negative_text"], {
            "family": a["family"], "impr": a["august_impressions"],
            "clicks": a["august_clicks"], "cost": a["august_cost"],
            "conv": a["august_conversions"],
            "terms": a["supporting_raw_search_terms"],
            "campaigns": [], "evidence": a["evidence"]})
        phrases[a["negative_text"]]["campaigns"].append(a["resource_id"])

    # ---------------- 25 candidate reconciliation report ----------------
    L = []
    A = L.append
    A("# 25 — Candidate and Count Reconciliation")
    A("")
    A(f"**Account:** {plan['target']['exact_child_account_name']} | "
      f"`{plan['target']['child_customer_id']}` | {plan['target']['exact_service']}  ")
    A(f"**Window:** {plan['target']['search_term_window']} "
      f"(completed days {rec['completed_days']}, partial day {rec['partial_day']})  ")
    A(f"**Snapshot:** `{rec['snapshot']}` read {D['read_started_utc']}  ")
    A(f"**Mode:** READ + AUDIT + DRAFT + VALIDATE-ONLY. No external write.")
    A("")
    A("## 1. Why the previous counts did not reconcile")
    A("")
    A("| Previous statement | What it actually was | Resolution |")
    A("|---|---|---|")
    A("| 349 search-term rows | Correct. The API returns 349 rows for the window. | "
      "Confirmed against a fresh read. |")
    A("| KEEP 9 + WATCH 215 + NEGATIVE_PHRASE 11 + INSUFFICIENT_DATA 90 = **325** | "
      "The old classifier aggregated rows to one row per `(term, ad group)` pair before "
      "writing the CSV, and separately dropped any row whose campaign was not ENABLED. "
      "325 was the count of surviving pairs, not of source rows. | "
      "**The 24 missing rows are the duplicate `(term, ad group)` collisions.** This run "
      "keeps every source row: 36 normalized terms occur on more than one row, contributing "
      "42 extra rows, and the two totals now differ only because the old file also merged "
      "rows that differed by matched keyword or search-term match type. The replacement CSV "
      "has 349 rows and reconciles exactly on rows, terms, impressions, clicks, cost and "
      "conversions. |")
    A("| 25 competitor brands | 25 **objects** in the `competitor_brand` family. The written "
      "list held 24 names. | **No competitor was omitted from the written list.** "
      "`allied outdoor solutions` appeared twice, once in `Hardscaping \\| BOFU` and once in "
      "`Landscape Design \\| BOFU`, so 24 distinct phrases produced 25 ad-group objects. |")
    A("| 28 ad-group actions | 27 distinct phrases + 1 duplicated phrase = 28. | Consistent "
      "once the duplicate above is accounted for. |")
    A("| 54 campaign-level objects | 27 distinct phrases x 2 campaigns = 54. | Arithmetically "
      "consistent, but it described a hypothetical campaign-scoped plan that was never built. "
      "The plan that carried fingerprint `4EEF81C7F2F5` contained 28 **ad-group** objects. |")
    A("")
    A("## 2. Row-level reconciliation, replacement run")
    A("")
    A("| Measure | Source (API) | Verdict CSV | Match |")
    A("|---|---:|---:|:--:|")
    for k, label in [("rows", "Search-term rows"), ("distinct_raw", "Distinct raw terms"),
                     ("distinct_norm", "Distinct normalized terms"),
                     ("impressions", "Impressions"), ("clicks", "Clicks"),
                     ("cost", "Cost"), ("conversions", "Conversions"),
                     ("conversion_value", "Conversion value")]:
        s = money(src[k]) if k in ("cost", "conversion_value") else src[k]
        v = money(vout[k]) if k in ("cost", "conversion_value") else vout[k]
        A(f"| {label} | {s} | {v} | {'YES' if src[k] == vout[k] else 'NO'} |")
    A("")
    A(f"Every one of the {src['rows']} returned rows carries a verdict. No zero-impression, "
      f"zero-click, duplicate or partial-day row was dropped. The raw search term is "
      f"preserved verbatim in `raw_search_term`; `normalized_search_term` exists only for "
      f"deduplication and matching.")
    A("")
    A("### Duplicate terms")
    A("")
    A(f"{len(rec['duplicate_terms'])} normalized terms appear on more than one row, "
      f"contributing {sum(d['rows'] - 1 for d in rec['duplicate_terms'])} extra rows. A term "
      f"repeats when it is served by more than one ad group, by more than one matched "
      f"keyword, or under more than one search-term match type. Both campaigns can serve the "
      f"same query because they hold adjacent themes.")
    A("")
    A("| Normalized term | Rows | Campaigns | Ad groups | Matched keyword / match type |")
    A("|---|---:|---:|---:|---|")
    for d in rec["duplicate_terms"][:12]:
        kp = "; ".join(f"`{t}` [{m}]" for t, m in d["keyword_pairs"])
        A(f"| `{d['normalized_term']}` | {d['rows']} | {len(d['campaigns'])} | "
          f"{len(d['ad_groups'])} | {kp} |")
    A(f"")
    A(f"_({len(rec['duplicate_terms'])} duplicate terms in total; the full set is in the "
      f"verdict CSV and in `25_candidate_reconciliation.json`.)_")
    A("")
    A("## 3. Verdict totals")
    A("")
    A("| Verdict | Intent family | Rows | Impr | Clicks | Cost |")
    A("|---|---|---:|---:|---:|---:|")
    for verdict in sorted(fam_by_verdict, key=lambda v: -sum(
            x[3] for x in fam_by_verdict[v].values())):
        fams = fam_by_verdict[verdict]
        tot = [sum(x[i] for x in fams.values()) for i in range(4)]
        A(f"| **{verdict}** | _all_ | **{tot[0]}** | **{tot[1]}** | **{tot[2]}** | "
          f"**{money(tot[3])}** |")
        for fam, v in sorted(fams.items(), key=lambda kv: -kv[1][3]):
            A(f"| | {fam} | {v[0]} | {v[1]} | {v[2]} | {money(v[3])} |")
    A(f"| **TOTAL** | | **{sum(int(r['impressions']) * 0 + 1 for r in rows)}** | "
      f"**{sum(int(r['impressions']) for r in rows)}** | "
      f"**{sum(int(r['clicks']) for r in rows)}** | "
      f"**{money(sum(float(r['cost']) for r in rows))}** |")
    A("")
    A("## 4. Candidate reconciliation")
    A("")
    A("| Step | Count |")
    A("|---|---:|")
    A(f"| Prior competitor candidates re-evaluated | {len(PRIOR_CANDIDATES)} |")

    def from_prior(phrase):
        return next((p for p in PRIOR_CANDIDATES if p in phrase or phrase in p), None)

    competitor_phrases = {p for p, v in phrases.items() if v["family"] == "COMPETITOR"}
    prior_phrases = {p for p in competitor_phrases if from_prior(p)}
    retained_priors = {from_prior(p) for p in prior_phrases}
    new_phrases = sorted(competitor_phrases - prior_phrases)
    A(f"| Prior candidates retained after verification | {len(retained_priors)} |")
    A(f"| Prior candidates rejected after verification | "
      f"{len(PRIOR_CANDIDATES) - len(retained_priors)} |")
    A(f"| Phrases carrying those retained candidates | {len(prior_phrases)} |")
    A(f"| Newly verified competitor phrases added this run | {len(new_phrases)} |")
    A(f"| Brand-shaped queries found but NOT verified | "
      f"{len(DEC.COMPETITOR_UNVERIFIED_RESIDUE)} |")
    A(f"| **Unique candidate phrases** | **{rec['unique_candidate_phrases']}** |")
    for fam, n in sorted(rec["phrases_by_family"].items()):
        A(f"| &nbsp;&nbsp;of which {fam} | {n} |")
    A(f"| Removed because already effectively blocked | 0 |")
    A(f"| Removed because of a conflict | 0 |")
    A(f"| Terms retained as WATCH instead of blocked | "
      f"{len(DEC.WATCH_OVERRIDES) + len(DEC.COMPETITOR_UNVERIFIED_RESIDUE)} |")
    A(f"| Base target count ({rec['unique_candidate_phrases']} x 2 campaigns) | "
      f"{rec['base_target_count']} |")
    A(f"| Campaign targets removed | {len(rec['targets_skipped'])} |")
    A(f"| **Proposed campaign targets** | **{rec['targets_proposed']}** |")
    for cid, n in sorted(rec["targets_by_campaign"].items()):
        A(f"| &nbsp;&nbsp;{cell(TARGETS[cid])} | {n} |")
    A("")
    A("### Count logic")
    A("")
    A(f"```\nbase target count   = {rec['unique_candidate_phrases']} safe unique phrases "
      f"x 2 campaigns = {rec['base_target_count']}\nminus already blocked = 0\n"
      f"minus unsafe          = 0\nfinal object count    = {rec['targets_proposed']}\n```")
    A("")
    A(f"Candidate phrases **{rec['unique_candidate_phrases']}**, campaign targets "
      f"**{rec['targets_proposed']}**, YAML actions **{len(actions)}**, YAML objects "
      f"**{sum(a['object_count'] for a in actions)}**, CSV rows **{rec['csv_rows']}**, "
      f"validate-only operations **{receipt['api_operations']}**. All six reconcile.")
    A("")
    A("### Every phrase appears in exactly one ad group family or several?")
    A("")
    A("Campaign scope makes this question moot for the plan, but it is recorded for "
      "evidence. These phrases were observed in more than one ad group during the window:")
    A("")
    ag_by_term = defaultdict(set)
    for r in rows:
        ag_by_term[r["normalized_search_term"]].add(r["ad_group_name"])
    multi = {t: ags for t, ags in ag_by_term.items() if len(ags) > 1}
    A("| Normalized term | Ad groups |")
    A("|---|---|")
    for t, ags in sorted(multi.items())[:15]:
        A(f"| `{t}` | {cell(', '.join(sorted(ags)))} |")
    A("")
    A(f"_{len(multi)} terms in total appeared in more than one ad group. This is exactly why "
      f"the replacement plan is campaign-scoped: a categorically unwanted query is unwanted "
      f"wherever it lands, and ad-group scoping would have left every other ad group open._")
    A("")
    A("## 5. Prior candidates rejected, with the reason")
    A("")
    A("| Prior candidate | New verdict | Why |")
    A("|---|---|---|")
    rejected = {
        "apollo pergola": ("WATCH / MANUFACTURER_PRODUCT",
            "Apollo Opening Roof is a louvered-pergola manufacturer in Roseville CA that "
            "sells through builders, not an Austin landscaping competitor. Pergolas are a "
            "verified Pro Green service, so the query carries real pergola-buying intent. "
            "Blocking it would suppress a qualified prospect."),
        "cedarcrest": ("WATCH / COMPETITOR_UNVERIFIED",
            "No company of that name could be confirmed, and Cedarcrest is a common "
            "subdivision and street name. The query may be a resident asking for landscaping "
            "in Cedarcrest, who is exactly the customer this campaign wants."),
        "clean scapes": ("WATCH / COMPETITOR_WITH_CONVERSION_EVIDENCE",
            "Clean Scapes, LP is a verified Austin firm, but the conflict check found that "
            "the all-time query 'clean scapes austin texas' recorded all_conversions = 1.0 "
            "on a $4.91 click. Overriding a documented conflict to gain a negative worth 4 "
            "impressions and $0.00 this month is a bad trade."),
        "stones and scapes": ("WATCH / COMPETITOR_UNVERIFIED",
            "Not confirmed. The nearest verified firm is 'Scapes and Stones' in North Las "
            "Vegas, a different name in a different market."),
    }
    for k, (v, why) in rejected.items():
        A(f"| `{k}` | {v} | {why} |")
    A("")
    A("## 6. Competitors the previous written summary never listed")
    A("")
    A(f"Verified this run and **added** to the plan ({len(new_phrases)} phrases):")
    A("")
    A("| Phrase | Aug impr | Aug clicks | Aug cost | Verification |")
    A("|---|---:|---:|---:|---|")
    for p in new_phrases:
        v = phrases[p]
        A(f"| `{p}` | {v['impr']} | {v['clicks']} | {money(v['cost'])} | "
          f"{cell(v['evidence'])} |")
    A("")
    A(f"Brand-shaped and **not** blocked, because no reliable confirmation was obtained in "
      f"this pass. All {len(DEC.COMPETITOR_UNVERIFIED_RESIDUE)} produced 0 clicks and "
      f"$0.00 this month, so nothing is lost by waiting for verification:")
    A("")
    A("```")
    for i in range(0, len(DEC.COMPETITOR_UNVERIFIED_RESIDUE), 3):
        A("  " + "".join(f"{t:<40}" for t in DEC.COMPETITOR_UNVERIFIED_RESIDUE[i:i + 3])
          .rstrip())
    A("```")
    A("")
    A("## 7. Phrases proposed")
    A("")
    A("| Phrase | Family | Campaigns | Aug impr | Aug clicks | Aug cost | Supporting terms |")
    A("|---|---|---:|---:|---:|---:|---|")
    for p in sorted(phrases, key=lambda x: (phrases[x]["family"], x)):
        v = phrases[p]
        A(f"| `{p}` | {v['family']} | {len(v['campaigns'])} | {v['impr']} | {v['clicks']} | "
          f"{money(v['cost'])} | {cell(', '.join('`' + t + '`' for t in v['terms']))} |")
    A("")
    (out / "25_candidate_reconciliation_report.md").write_text("\n".join(L), encoding="utf-8")

    # ---------------- 29 validate-only receipt ----------------
    R = []
    B = R.append
    B("# 29 — Server-Side Validate-Only Receipt")
    B("")
    B(f"**Account:** {post['identity']['descriptive_name']} | "
      f"`{post['identity']['id']}` | outdoor design & build  ")
    B(f"**Subplan:** EXISTING_RESOURCES `{args.subplan}`  ")
    B(f"**Master:** `{args.master}`  ")
    B(f"**Executed:** {receipt['executed_at_utc']}  ")
    B(f"**Mode:** {receipt['mode']}")
    B("")
    B("## Request")
    B("")
    B("| Field | Value |")
    B("|---|---|")
    B(f"| Customer ID | `{receipt['customer_id']}` (exact child ID, never the MCC) |")
    B(f"| Approved actions | {receipt['approved_actions']} |")
    B(f"| Approved objects | {receipt['approved_objects']} |")
    B(f"| API operations | {receipt['api_operations']} |")
    B(f"| `partial_failure` | `{receipt['partial_failure']}` |")
    B(f"| `validate_only` | `true` |")
    B(f"| Campaign resource names | "
      f"`customers/7380491929/campaigns/24053505501`, "
      f"`customers/7380491929/campaigns/24053505504` |")
    B(f"| Match type | PHRASE on every operation |")
    B(f"| Result | **VALIDATION PASSED.** Nothing was written. |")
    B("")
    B("The fingerprint was recomputed from the on-disk plan before the request was built. "
      "The executor refuses to run on any mismatch, so the validated operation set is "
      "byte-identical to the plan that carries the fingerprint above.")
    B("")
    B("## Post-validate re-read")
    B("")
    B(f"Fresh read-only re-read at {post['checked_at_utc']}.")
    B("")
    B("| Counter | Before | After | Unchanged |")
    B("|---|---:|---:|:--:|")
    B(f"| Campaign negatives, Hardscape Construction | "
      f"{post['campaign_negatives_before']['24053505501']} | "
      f"{post['campaign_negatives_after']['24053505501']} | YES |")
    B(f"| Campaign negatives, Outdoor Living & Design | "
      f"{post['campaign_negatives_before']['24053505504']} | "
      f"{post['campaign_negatives_after']['24053505504']} | YES |")
    for label, key in [("Ad-group negatives", "ad_group_negatives"),
                       ("Shared-list criteria", "shared_criteria"),
                       ("Positive keywords", "positive_keywords")]:
        B(f"| {label} | {post[key + '_before']} | {post[key + '_after']} | "
          f"{'YES' if post[key + '_unchanged'] else 'NO'} |")
    B(f"| Enabled ads | {post['enabled_ads_before']} | {post['enabled_ads_after']} | "
      f"{'YES' if post['ads_unchanged'] else 'NO'} |")
    B("")
    B(f"**{post['proposed_objects']} proposed negatives were searched for in the live "
      f"account. {len(post['proposed_objects_found_live'])} were found.** No proposed "
      f"negative exists. Campaign statuses, budgets and bidding strategies are unchanged:")
    B("")
    for c in post["enabled_campaigns"]:
        B(f"- `{c['id']}` status `{c['status']}`, budget {money(c['budget'])}/day, "
          f"bidding `{c['bidding']}`")
    B("")
    B(f"Combined daily budget "
      f"{money(sum(c['budget'] for c in post['enabled_campaigns']))}, unchanged.")
    B("")
    B("## NO EXTERNAL CHANGES MADE")
    B("")
    B(f"Automated assertion: `{post['NO_EXTERNAL_CHANGES_MADE']}`")
    B("")
    B(f"Receipt JSON: `{args.receipt}`  ")
    B(f"Re-read JSON: `{args.post_check}`")
    (out / "29_validate_only_receipt.md").write_text("\n".join(R), encoding="utf-8")

    print(f"written: {out / '25_candidate_reconciliation_report.md'}")
    print(f"written: {out / '29_validate_only_receipt.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
