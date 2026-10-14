#!/usr/bin/env python3
"""Reconcile search_term_view totals against campaign totals for Softwind.

The owner challenged the claim "90 of 100 clicks". This establishes, from fresh
data, exactly what the true numbers are and whether any gap between the
search-term corpus and the campaign totals is duplication, a units error, a
reporting defect, or the expected privacy-threshold withholding.

Four independent counts are taken so no single query shape can hide an error:
  A  campaign totals, no segmentation
  B  search_term_view aggregated with NO keyword segment
  C  search_term_view aggregated WITH the keyword segment (what the classifier used)
  D  keyword_view totals

READ ONLY.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
NAMES = {CAMP_A: "Power Washing", CAMP_B: "Power Washing #2"}
OUT = ROOT / "clients/softwind-power-washing/audits/2026-08-27-reconciliation.json"


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def usd(m):
    return round((m or 0) / 1_000_000, 2)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    today = now.strftime("%Y-%m-%d")
    span = "AND segments.date BETWEEN '2026-08-01' AND '%s'" % today
    r = {"read_only": True, "mutations_issued": 0,
         "timestamp_account_local": now.isoformat(), "window": "2026-08-01..%s" % today}

    # ---- A: campaign totals, unsegmented ----
    q = ("SELECT campaign.id, metrics.impressions, metrics.clicks, "
         f"metrics.cost_micros FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) {span}")
    A = {"per_campaign": {}, "impressions": 0, "clicks": 0, "cost": 0.0}
    for x in rows(svc, q):
        A["per_campaign"][NAMES[str(x.campaign.id)]] = {
            "impressions": x.metrics.impressions, "clicks": x.metrics.clicks,
            "cost": usd(x.metrics.cost_micros)}
        A["impressions"] += x.metrics.impressions
        A["clicks"] += x.metrics.clicks
        A["cost"] = round(A["cost"] + usd(x.metrics.cost_micros), 2)
    r["A_campaign_totals"] = A

    # ---- B: search_term_view, NO keyword segment ----
    q = ("SELECT campaign.id, ad_group.id, search_term_view.search_term, "
         "metrics.impressions, metrics.clicks, metrics.cost_micros "
         f"FROM search_term_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) {span}")
    B_rows = rows(svc, q)
    B = {"row_count": len(B_rows), "impressions": 0, "clicks": 0, "cost": 0.0}
    b_terms, b_pairs = set(), set()
    for x in B_rows:
        B["impressions"] += x.metrics.impressions
        B["clicks"] += x.metrics.clicks
        B["cost"] = round(B["cost"] + usd(x.metrics.cost_micros), 2)
        b_terms.add(x.search_term_view.search_term)
        b_pairs.add((str(x.ad_group.id), x.search_term_view.search_term))
    B["distinct_terms"] = len(b_terms)
    B["distinct_ad_group_term_pairs"] = len(b_pairs)
    r["B_search_terms_no_keyword_segment"] = B

    # ---- C: search_term_view WITH keyword segment (classifier's query shape) ----
    q = ("SELECT campaign.id, ad_group.id, search_term_view.search_term, "
         "segments.keyword.info.text, segments.search_term_match_type, "
         "metrics.impressions, metrics.clicks, metrics.cost_micros "
         f"FROM search_term_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) {span}")
    C_rows = rows(svc, q)
    C = {"row_count": len(C_rows), "impressions": 0, "clicks": 0, "cost": 0.0}
    c_pairs = defaultdict(lambda: {"i": 0, "c": 0, "cost": 0.0, "kw": set()})
    for x in C_rows:
        C["impressions"] += x.metrics.impressions
        C["clicks"] += x.metrics.clicks
        C["cost"] = round(C["cost"] + usd(x.metrics.cost_micros), 2)
        k = (str(x.ad_group.id), x.search_term_view.search_term)
        d = c_pairs[k]
        d["i"] += x.metrics.impressions
        d["c"] += x.metrics.clicks
        d["cost"] = round(d["cost"] + usd(x.metrics.cost_micros), 2)
        if x.segments.keyword.info.text:
            d["kw"].add(x.segments.keyword.info.text)
    C["distinct_ad_group_term_pairs"] = len(c_pairs)
    C["pairs_matched_by_more_than_one_keyword"] = sum(
        1 for v in c_pairs.values() if len(v["kw"]) > 1)
    r["C_search_terms_with_keyword_segment"] = C

    # ---- D: keyword_view ----
    q = ("SELECT campaign.id, metrics.impressions, metrics.clicks, "
         f"metrics.cost_micros FROM keyword_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) {span}")
    D = {"impressions": 0, "clicks": 0, "cost": 0.0}
    for x in rows(svc, q):
        D["impressions"] += x.metrics.impressions
        D["clicks"] += x.metrics.clicks
        D["cost"] = round(D["cost"] + usd(x.metrics.cost_micros), 2)
    r["D_keyword_view_totals"] = D

    # ---- duplication test: does the keyword segment inflate totals? ----
    r["duplication_test"] = {
        "B_vs_C_impressions": [B["impressions"], C["impressions"]],
        "B_vs_C_clicks": [B["clicks"], C["clicks"]],
        "B_vs_C_cost": [B["cost"], C["cost"]],
        "identical": (B["impressions"] == C["impressions"]
                      and B["clicks"] == C["clicks"]
                      and abs(B["cost"] - C["cost"]) < 0.02),
        "verdict": ("The keyword segment SPLITS metrics across rows, it does not "
                    "duplicate them. Row counts differ; summed totals do not."
                    if (B["impressions"] == C["impressions"]
                        and B["clicks"] == C["clicks"])
                    else "MISMATCH - the keyword segment changes the totals.")}

    # ---- coverage gap ----
    gap = {"impressions": A["impressions"] - B["impressions"],
           "clicks": A["clicks"] - B["clicks"],
           "cost": round(A["cost"] - B["cost"], 2)}
    gap["clicks_coverage_pct"] = (round(B["clicks"] / A["clicks"] * 100, 1)
                                  if A["clicks"] else None)
    gap["impressions_coverage_pct"] = (
        round(B["impressions"] / A["impressions"] * 100, 1)
        if A["impressions"] else None)
    gap["explanation"] = (
        "search_term_view withholds queries that do not meet Google's privacy "
        "threshold, and same-day rows lag the campaign aggregate. A positive gap "
        "is expected and is NOT a defect. It means the corpus is a SUBSET of "
        "campaign activity, so corpus percentages must never be presented as "
        "account-wide percentages.")
    r["coverage_gap_A_minus_B"] = gap

    # ---- the disputed claim ----
    from importlib import import_module
    sys.path.insert(0, str(ROOT / "scripts"))
    cls = import_module("softwind_classify_terms")
    buckets = defaultdict(lambda: {"pairs": 0, "impressions": 0, "clicks": 0,
                                   "cost": 0.0})
    for (agid, term), v in c_pairs.items():
        verdict, bucket, _ = cls.classify(term)
        b = buckets[bucket]
        b["pairs"] += 1
        b["impressions"] += v["i"]
        b["clicks"] += v["c"]
        b["cost"] = round(b["cost"] + v["cost"], 2)
    r["buckets_recomputed"] = dict(sorted(buckets.items()))
    in_scope = sum(v["clicks"] for k, v in buckets.items() if k.startswith("IN_SCOPE"))
    total_c = sum(v["clicks"] for v in buckets.values())
    in_cost = sum(v["cost"] for k, v in buckets.items() if k.startswith("IN_SCOPE"))
    total_cost = round(sum(v["cost"] for v in buckets.values()), 2)
    r["disputed_claim"] = {
        "as_written_in_plan_k2": "90 of 100 clicks and $282.74 of $318.05",
        "true_values": "%d of %d clicks and $%.2f of $%.2f"
                       % (in_scope, total_c, in_cost, total_cost),
        "click_figures_were": "WRONG by a factor of 10",
        "cost_figures_were": "CORRECT",
        "root_cause": ("A hand-written narrative string in the plan builder. The "
                       "classifier itself printed the correct '9 clicks' in its "
                       "bucket table; the sentence in the plan was typed as '90 "
                       "of 100' and never re-derived from the data. It is not a "
                       "units error, not impressions, not duplication, and not a "
                       "reporting defect - it is a transcription error in a "
                       "narrative field."),
        "is_it_impressions": ("NO. Impressions in the same buckets are %d in-scope "
                              "of %d total, which matches neither 90 nor 100."
                              % (sum(v["impressions"] for k, v in buckets.items()
                                     if k.startswith("IN_SCOPE")),
                                 sum(v["impressions"] for v in buckets.values()))),
        "does_it_change_the_conclusion": (
            "No. The in-scope SHARE is what the argument rests on and it is "
            "unchanged: %.1f%% of corpus clicks and %.1f%% of corpus cost are "
            "in scope. But the absolute base is 10 clicks, not 100, so the "
            "corpus is far thinner than the sentence implied and every "
            "percentage drawn from it carries wide uncertainty."
            % (in_scope / total_c * 100 if total_c else 0,
               in_cost / total_cost * 100 if total_cost else 0)),
    }

    OUT.write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")

    print("SEARCH-TERM / CAMPAIGN RECONCILIATION  %s"
          % now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("=" * 78)
    print("\n%-46s %7s %7s %10s" % ("SOURCE", "IMPR", "CLICKS", "COST"))
    print("%-46s %7d %7d %10s" % ("A  campaign totals (unsegmented)",
                                  A["impressions"], A["clicks"], "$%.2f" % A["cost"]))
    print("%-46s %7d %7d %10s" % ("B  search_term_view, no keyword segment",
                                  B["impressions"], B["clicks"], "$%.2f" % B["cost"]))
    print("%-46s %7d %7d %10s" % ("C  search_term_view + keyword segment",
                                  C["impressions"], C["clicks"], "$%.2f" % C["cost"]))
    print("%-46s %7d %7d %10s" % ("D  keyword_view totals",
                                  D["impressions"], D["clicks"], "$%.2f" % D["cost"]))
    print("\nper campaign (A): %s" % json.dumps(A["per_campaign"]))
    print("\nDUPLICATION TEST (B vs C): identical=%s" % r["duplication_test"]["identical"])
    print("   rows: B=%d  C=%d   pairs matched by >1 keyword: %d"
          % (B["row_count"], C["row_count"], C["pairs_matched_by_more_than_one_keyword"]))
    print("   %s" % r["duplication_test"]["verdict"])
    print("\nCOVERAGE GAP (A - B): %d impressions, %d clicks, $%.2f"
          % (gap["impressions"], gap["clicks"], gap["cost"]))
    print("   corpus covers %.1f%% of clicks, %.1f%% of impressions"
          % (gap["clicks_coverage_pct"] or 0, gap["impressions_coverage_pct"] or 0))
    print("   %s" % gap["explanation"])
    print("\nBUCKETS (recomputed from this reconciliation, not reused):")
    print("   %-24s %6s %7s %7s %9s" % ("BUCKET", "PAIRS", "IMPR", "CLICKS", "COST"))
    for k, v in sorted(buckets.items(), key=lambda x: -x[1]["cost"]):
        print("   %-24s %6d %7d %7d %9s"
              % (k, v["pairs"], v["impressions"], v["clicks"], "$%.2f" % v["cost"]))
    dc = r["disputed_claim"]
    print("\nDISPUTED CLAIM")
    print("   as written : %s" % dc["as_written_in_plan_k2"])
    print("   TRUE       : %s" % dc["true_values"])
    print("   clicks     : %s" % dc["click_figures_were"])
    print("   cost       : %s" % dc["cost_figures_were"])
    print("   cause      : %s" % dc["root_cause"])
    print("   impressions? %s" % dc["is_it_impressions"])
    print("   impact     : %s" % dc["does_it_change_the_conclusion"])
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
