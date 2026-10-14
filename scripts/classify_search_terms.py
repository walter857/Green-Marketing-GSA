#!/usr/bin/env python3
"""Multi-stage search-term classification for the EKG Aeration & Overseeding build.

Reads the local snapshot only. Issues no API call and changes nothing in Google Ads.

Six verdicts, per the approved scheme. Non-service terms are NOT collapsed into a single
bucket: each is classified on its own evidence and reason.

  CANDIDATE_KEYWORD      service-relevant, bottom-of-funnel, enough evidence to act on
  WATCH                  plausibly related, needs service verification or more data
  AMBIGUOUS              intent cannot be settled from the term alone
  IRRELEVANT             not this service, with a recorded reason
  INSUFFICIENT_DATA      relevant shape, too little traffic to judge
  NEGATIVE_RECOMMENDATION proposed only, never applied automatically

Output policy: the complete term-level evidence table is written to disk. Only
service-relevant terms are printed. Non-service terms are reported as counts per reason,
never as strings.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Terms Green Marketing policy forbids negativing automatically.
PROTECTED = {"near me", "quote", "price", "pricing", "cost", "best", "hire", "local",
             "emergency"}

# Core service vocabulary, defined positively.
CORE_AERATION = re.compile(r"\b(aerat\w*|aeriat\w*)\b", re.I)
CORE_SEEDING = re.compile(r"\b(overseed\w*|over\s+seed\w*|reseed\w*|re\s+seed\w*|seeding|"
                          r"grass\s+seed\w*|lawn\s+seed\w*|slit\s+seed\w*|power\s+seed\w*|"
                          r"slice\s+seed\w*)\b", re.I)

# Step 16: related intents that are NOT verified EKG services. They may never be promoted
# to CANDIDATE_KEYWORD without verification.
RELATED_UNVERIFIED = re.compile(
    r"\b(lawn\s+renovation|renovat\w*|thin\s+grass|bare\s+spot\w*|bare\s+patch\w*|"
    r"lawn\s+restoration|restor\w*|fall\s+lawn|dethatch\w*|thatch\w*|"
    r"top\s*dress\w*|sod\b|hydroseed\w*)\b", re.I)

# Non-buying intent.
INFORMATIONAL = re.compile(
    r"\b(how\s+to|how\s+much\s+\w+\s+after|how\s+long|how\s+often|when\s+to|when\s+is|"
    r"what\s+is|why\s+|diy|do\s+it\s+yourself|guide|tutorial|video|calculator|meaning|"
    r"definition|vs\b|before\s+or\s+after)\b", re.I)

# Aftercare questions: someone who already had the work done, or is doing it themselves.
AFTERCARE = re.compile(r"\b(after\s+(overseed\w*|aerat\w*|seeding)|watering\s+schedule|"
                       r"fertiliz\w*\s+overseed\w*|mow\w*\s+after|cut\s+grass\s+after)\b", re.I)
EMPLOYMENT = re.compile(r"\b(job|jobs|hiring|career|careers|salary|employment|apply|"
                        r"resume|wages?|pay\s+rate)\b", re.I)
EQUIPMENT = re.compile(r"\b(rental|rent\b|rents\b|buy|for\s+sale|machine|equipment|tool|"
                       r"aerator\s+rental|home\s+depot|lowes|tractor\s+supply|amazon)\b", re.I)
FREE_INTENT = re.compile(r"\b(free|cheap|cheapest|volunteer)\b", re.I)

OTHER_SERVICE = re.compile(r"\b(mow\w*|mulch\w*|landscap\w*|irrigation|sprinkler|tree\s+"
                           r"removal|stump|snow|gutter|pressure\s+wash\w*|leaf\s+removal|"
                           r"fertiliz\w*|weed\s+control|pest|hardscape|patio|retaining\s+wall|"
                           r"fence|clean\s*up|cleanup|trim\w*|edging|planting|garden\w*|"
                           r"sod\s+install\w*|artificial\s+turf|pool|deck|driveway)\b", re.I)


def classify(term: str, impressions: int, clicks: int, conversions: float) -> tuple[str, str]:
    """Return (verdict, reason). Order matters: the most specific rule wins first."""
    t = term.lower().strip()
    is_core = bool(CORE_AERATION.search(t) or CORE_SEEDING.search(t))

    if EMPLOYMENT.search(t):
        return ("NEGATIVE_RECOMMENDATION", "employment_intent")
    if EQUIPMENT.search(t):
        return ("NEGATIVE_RECOMMENDATION", "equipment_purchase_or_rental_intent")
    if AFTERCARE.search(t):
        # Post-service or DIY aftercare. Not a buying intent even when it drew a click.
        return ("NEGATIVE_RECOMMENDATION", "aftercare_or_diy_maintenance_intent")
    if INFORMATIONAL.search(t) and not clicks:
        return ("NEGATIVE_RECOMMENDATION", "informational_no_click_intent")
    if INFORMATIONAL.search(t) and clicks:
        return ("AMBIGUOUS", "informational_phrasing_but_drew_a_click")
    if FREE_INTENT.search(t) and not is_core:
        return ("IRRELEVANT", "free_or_lowest_price_seeking_non_service")

    if is_core:
        # Step 16: a core word plus an unverified related service stays unverified.
        if RELATED_UNVERIFIED.search(t):
            return ("WATCH", "core_service_plus_unverified_related_service")
        if INFORMATIONAL.search(t):
            return ("AMBIGUOUS", "core_service_with_informational_modifier")
        if impressions < 5 and clicks == 0:
            return ("INSUFFICIENT_DATA", "core_service_but_negligible_traffic")
        if OTHER_SERVICE.search(t):
            return ("AMBIGUOUS", "core_service_bundled_with_another_service")
        return ("CANDIDATE_KEYWORD", "core_service_bofu")

    if RELATED_UNVERIFIED.search(t):
        # Never promoted without verification, per step 16.
        if impressions < 5 and clicks == 0:
            return ("INSUFFICIENT_DATA", "related_unverified_negligible_traffic")
        return ("WATCH", "related_intent_requires_service_verification")

    if OTHER_SERVICE.search(t):
        return ("IRRELEVANT", "different_service_line")

    if impressions < 5 and clicks == 0:
        return ("INSUFFICIENT_DATA", "non_service_negligible_traffic")
    return ("AMBIGUOUS", "no_service_signal_in_term")


def service_theme(term: str) -> str:
    """Which approved ad group a service-relevant term belongs to."""
    t = term.lower()
    a = bool(CORE_AERATION.search(t))
    s = bool(CORE_SEEDING.search(t))
    if a and s:
        return "COMBINED"
    if a:
        return "Lawn Aeration"
    if s:
        return "Lawn Overseeding"
    return "-"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-json", required=True)
    args = parser.parse_args()

    snap = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    rows = snap.get("search_terms", [])

    # Aggregate across windows, campaigns and ad groups.
    agg: dict[str, dict] = {}
    for r in rows:
        term = (r.get("term") or "").strip()
        if not term:
            continue
        b = agg.setdefault(term, {
            "term": term, "impressions": 0, "clicks": 0, "cost": 0.0,
            "conversions": 0.0, "conversions_value": 0.0,
            "campaigns": set(), "ad_groups": set(), "windows": set(),
            "matched_keywords": set(), "match_types": set(),
        })
        b["impressions"] += int(r.get("impressions", 0))
        b["clicks"] += int(r.get("clicks", 0))
        b["cost"] += float(r.get("cost", 0.0))
        b["conversions"] += float(r.get("conversions", 0.0))
        b["conversions_value"] += float(r.get("conversions_value", 0.0))
        b["campaigns"].add(r.get("campaign_name", ""))
        b["ad_groups"].add(r.get("ad_group_name", ""))
        b["windows"].add(r.get("window", ""))
        if r.get("matched_keyword"):
            b["matched_keywords"].add(r["matched_keyword"])
        if r.get("matched_match_type"):
            b["match_types"].add(r["matched_match_type"])

    records = []
    for term, b in agg.items():
        verdict, reason = classify(term, b["impressions"], b["clicks"], b["conversions"])
        protected_hit = sorted(p for p in PROTECTED if p in term.lower())
        if verdict == "NEGATIVE_RECOMMENDATION" and protected_hit:
            verdict, reason = ("WATCH", f"protected_commercial_term_never_auto_negative:"
                                        f"{'|'.join(protected_hit)}")
        records.append({
            "term": term, "verdict": verdict, "reason": reason,
            "theme": service_theme(term),
            "impressions": b["impressions"], "clicks": b["clicks"],
            "cost": round(b["cost"], 2), "conversions": round(b["conversions"], 2),
            "conversions_value": round(b["conversions_value"], 2),
            "cpc": round(b["cost"] / b["clicks"], 2) if b["clicks"] else None,
            "source_campaigns": "; ".join(sorted(x for x in b["campaigns"] if x)),
            "source_ad_groups": "; ".join(sorted(x for x in b["ad_groups"] if x)),
            "date_windows": "; ".join(sorted(x for x in b["windows"] if x)),
            "matched_keywords": "; ".join(sorted(b["matched_keywords"])),
            "matched_match_types": "; ".join(sorted(b["match_types"])),
            "protected_terms_present": "|".join(protected_hit),
            "auto_applied": False,
        })

    records.sort(key=lambda r: (-r["clicks"], -r["impressions"], r["term"]))

    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    Path(args.out_json).write_text(json.dumps(records, indent=2), encoding="utf-8")

    # ---------------- reporting: aggregates only for non-service terms ----------------
    total_clicks = sum(r["clicks"] for r in records) or 1
    total_cost = sum(r["cost"] for r in records) or 1.0

    print("=" * 78)
    print("SEARCH-TERM CLASSIFICATION")
    print("=" * 78)
    print(f"\nDistinct search terms analyzed: {len(records)}")
    print(f"Source rows                   : {len(rows)}")

    print("\n--- Verdict distribution ---")
    print(f"{'VERDICT':<24} {'TERMS':>6} {'CLICKS':>7} {'CLICK%':>7} {'COST':>10} {'COST%':>7} {'CONV':>7}")
    order = ["CANDIDATE_KEYWORD", "WATCH", "AMBIGUOUS", "INSUFFICIENT_DATA",
             "IRRELEVANT", "NEGATIVE_RECOMMENDATION"]
    for verdict in order:
        sub = [r for r in records if r["verdict"] == verdict]
        cl = sum(r["clicks"] for r in sub)
        co = sum(r["cost"] for r in sub)
        cv = sum(r["conversions"] for r in sub)
        print(f"{verdict:<24} {len(sub):>6} {cl:>7} {100*cl/total_clicks:>6.1f}% "
              f"${co:>9.2f} {100*co/total_cost:>6.1f}% {cv:>7.1f}")

    print("\n--- Reason counts (all verdicts, strings withheld) ---")
    reasons: dict[str, dict] = {}
    for r in records:
        k = f"{r['verdict']}::{r['reason'].split(':')[0]}"
        d = reasons.setdefault(k, {"terms": 0, "clicks": 0, "cost": 0.0})
        d["terms"] += 1
        d["clicks"] += r["clicks"]
        d["cost"] += r["cost"]
    for k in sorted(reasons, key=lambda x: -reasons[x]["cost"]):
        d = reasons[k]
        print(f"  {k:<64} terms={d['terms']:>5} clicks={d['clicks']:>5} cost=${d['cost']:>9.2f}")

    # Service-relevant terms are the campaign inputs, so these are shown.
    print("\n--- CANDIDATE_KEYWORD terms by approved ad group ---")
    for theme in ("Lawn Aeration", "Lawn Overseeding", "COMBINED"):
        sub = [r for r in records if r["verdict"] == "CANDIDATE_KEYWORD" and r["theme"] == theme]
        sub.sort(key=lambda r: (-r["clicks"], -r["impressions"]))
        cl = sum(r["clicks"] for r in sub)
        co = sum(r["cost"] for r in sub)
        cv = sum(r["conversions"] for r in sub)
        print(f"\n  [{theme}]  terms={len(sub)}  clicks={cl}  cost=${co:.2f}  conv={cv:.1f}")
        for r in sub[:25]:
            print(f"    {r['impressions']:>6} impr {r['clicks']:>4} clk ${r['cost']:>8.2f} "
                  f"{r['conversions']:>5.1f} conv  {r['term']}")
        if len(sub) > 25:
            print(f"    ... {len(sub)-25} more in the evidence table")

    print("\n--- WATCH terms (related intent, service NOT verified) ---")
    watch = [r for r in records if r["verdict"] == "WATCH"]
    watch.sort(key=lambda r: (-r["clicks"], -r["impressions"]))
    print(f"  total={len(watch)}  clicks={sum(r['clicks'] for r in watch)}  "
          f"cost=${sum(r['cost'] for r in watch):.2f}")
    for r in watch[:20]:
        print(f"    {r['impressions']:>6} impr {r['clicks']:>4} clk ${r['cost']:>8.2f}  "
              f"{r['term']}   [{r['reason']}]")
    if len(watch) > 20:
        print(f"    ... {len(watch)-20} more in the evidence table")

    neg = [r for r in records if r["verdict"] == "NEGATIVE_RECOMMENDATION"]
    print(f"\n--- NEGATIVE_RECOMMENDATION: {len(neg)} proposed, 0 applied ---")
    print("  Nothing is added automatically. Each requires review and approval.")
    by_reason: dict[str, dict] = {}
    for r in neg:
        d = by_reason.setdefault(r["reason"], {"terms": 0, "clicks": 0, "cost": 0.0})
        d["terms"] += 1
        d["clicks"] += r["clicks"]
        d["cost"] += r["cost"]
    for reason, d in sorted(by_reason.items(), key=lambda x: -x[1]["cost"]):
        print(f"    {reason:<44} terms={d['terms']:>5} clicks={d['clicks']:>5} "
              f"wasted=${d['cost']:>9.2f}")

    print(f"\nEvidence table: {out_csv}")
    print(f"JSON          : {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
