#!/usr/bin/env python3
"""Fresh search-term pull for the five campaigns. Writes to disk; prints aggregates only."""
from __future__ import annotations
import sys, json, csv, hashlib
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()

OUTDIR = EXPORTS
OUTDIR.mkdir(parents=True, exist_ok=True)


def pull(label, start, end, extra_select="", extra_where="", src="search_term_view",
         metrics=METRICS):
    rows = []
    sel = ("campaign.id, ad_group.id, search_term_view.search_term, "
           "search_term_view.status, segments.search_term_match_type, " + metrics)
    if extra_select:
        sel += ", " + extra_select
    where = f"campaign.id IN ({IN5}) AND segments.date BETWEEN '{start}' AND '{end}'"
    if extra_where:
        where += " AND " + extra_where
    for r in q(c, f"SELECT {sel} FROM {src} WHERE {where}"):
        if metrics is METRICS:
            d = m(r)
        else:
            d = {"conversions": round(r.metrics.conversions, 2),
                 "all_conversions": round(r.metrics.all_conversions, 2),
                 "conv_value": round(r.metrics.conversions_value, 2),
                 "all_conv_value": round(r.metrics.all_conversions_value, 2),
                 "impressions": 0, "clicks": 0, "cost": 0.0, "ctr": 0.0, "avg_cpc": 0.0}
        d.update({"camp": str(r.campaign.id), "ag": str(r.ad_group.id),
                  "term": r.search_term_view.search_term,
                  "st_status": E(r.search_term_view.status),
                  "st_match": E(r.segments.search_term_match_type)})
        if "segments.conversion_action_name" in extra_select:
            d["conv_action"] = r.segments.conversion_action_name
            d["conv_category"] = E(r.segments.conversion_action_category)
        if "segments.date" in extra_select:
            d["date"] = r.segments.date
        rows.append(d)
    return rows


summary = {}

# 1. Same window as the supplied CSV
win = pull("csv_window", "2026-07-15", "2026-09-09")
p = OUTDIR / "search-terms-api-2026-09-09-csvwindow.jsonl"
p.write_text("\n".join(json.dumps(r) for r in win), encoding="utf-8")
tot = {k: round(sum(x[k] for x in win), 2) for k in
       ("impressions", "clicks", "cost", "conversions", "all_conversions")}
summary["csv_window_2026_07_15_to_2026_09_09"] = {
    "rows": len(win), "distinct_terms": len({r["term"] for r in win}),
    "distinct_term_camp_ag": len({(r["term"], r["camp"], r["ag"]) for r in win}),
    "totals": tot, "by_campaign": {}, "file": str(p.relative_to(ROOT)),
    "sha256": hashlib.sha256(p.read_bytes()).hexdigest()[:16]}
bc = defaultdict(lambda: {"rows": 0, "impressions": 0, "clicks": 0, "cost": 0.0,
                          "conversions": 0.0, "all_conversions": 0.0})
for r in win:
    b = bc[NAME[r["camp"]]]
    b["rows"] += 1
    for k in ("impressions", "clicks", "cost", "conversions", "all_conversions"):
        b[k] += r[k]
for k in bc:
    bc[k]["cost"] = round(bc[k]["cost"], 2)
summary["csv_window_2026_07_15_to_2026_09_09"]["by_campaign"] = dict(bc)
print("CSV-window API pull:", len(win), "rows;", tot)
print("  st_status:", dict(Counter(r["st_status"] for r in win)))
print("  by campaign:", json.dumps(dict(bc), indent=1))

# 2. Settled only, for stable comparisons
settled = pull("settled", "2026-08-14", "2026-09-08")
p2 = OUTDIR / "search-terms-api-2026-09-09-settled.jsonl"
p2.write_text("\n".join(json.dumps(r) for r in settled), encoding="utf-8")
tot2 = {k: round(sum(x[k] for x in settled), 2) for k in
        ("impressions", "clicks", "cost", "conversions", "all_conversions")}
summary["settled_2026_08_14_to_2026_09_08"] = {
    "rows": len(settled), "distinct_terms": len({r["term"] for r in settled}),
    "totals": tot2, "file": str(p2.relative_to(ROOT)),
    "sha256": hashlib.sha256(p2.read_bytes()).hexdigest()[:16]}
print("\nSettled pull:", len(settled), "rows;", tot2)

# 3. Converting terms, all time, segmented by conversion action
CONV_ONLY = ("metrics.conversions, metrics.all_conversions, "
             "metrics.conversions_value, metrics.all_conversions_value")
conv = pull("converting", "2019-01-01", "2026-09-09",
            extra_select="segments.conversion_action_name, segments.conversion_action_category",
            metrics=CONV_ONLY)
convrows = [r for r in conv if r["all_conversions"] > 0 or r["conversions"] > 0]
p3 = OUTDIR / "search-terms-api-2026-09-09-converting.jsonl"
p3.write_text("\n".join(json.dumps(r) for r in convrows), encoding="utf-8")
summary["converting_all_time"] = {
    "rows": len(convrows), "distinct_terms": len({r["term"] for r in convrows}),
    "total_conversions": round(sum(r["conversions"] for r in convrows), 2),
    "total_all_conversions": round(sum(r["all_conversions"] for r in convrows), 2),
    "by_conversion_action": dict(Counter(r["conv_action"] for r in convrows)),
    "file": str(p3.relative_to(ROOT)),
    "sha256": hashlib.sha256(p3.read_bytes()).hexdigest()[:16]}
print("\nConverting-term rows (all time):", len(convrows),
      "distinct terms:", len({r['term'] for r in convrows}))
print("  by conversion action:", dict(Counter(r["conv_action"] for r in convrows)))
print("  by campaign:", dict(Counter(NAME[r["camp"]] for r in convrows)))

# 4. ACCOUNT-WIDE converting search terms, all time, all campaigns
allconv = []
for r in q(c, """
    SELECT campaign.id, campaign.name, search_term_view.search_term,
           segments.conversion_action_name, metrics.conversions, metrics.all_conversions
    FROM search_term_view
    WHERE segments.date BETWEEN '2019-01-01' AND '2026-09-09'
      AND metrics.all_conversions > 0
"""):
    allconv.append({"camp": str(r.campaign.id), "camp_name": r.campaign.name,
                    "term": r.search_term_view.search_term,
                    "conv_action": r.segments.conversion_action_name,
                    "conversions": round(r.metrics.conversions, 2),
                    "all_conversions": round(r.metrics.all_conversions, 2)})
p4 = OUTDIR / "search-terms-api-2026-09-09-converting-ACCOUNTWIDE.jsonl"
p4.write_text("\n".join(json.dumps(r) for r in allconv), encoding="utf-8")
summary["converting_account_wide_all_time"] = {
    "rows": len(allconv), "distinct_terms": len({r["term"] for r in allconv}),
    "campaigns": dict(Counter(r["camp_name"][:40] for r in allconv)),
    "file": str(p4.relative_to(ROOT)),
    "sha256": hashlib.sha256(p4.read_bytes()).hexdigest()[:16]}
print("\nACCOUNT-WIDE converting term rows (all time):", len(allconv),
      "distinct:", len({r['term'] for r in allconv}))
print("  by campaign:", json.dumps(dict(Counter(r['camp_name'][:44] for r in allconv)), indent=1))

write(EVID / "2026-09-09-search-term-pull-summary.json", summary)
