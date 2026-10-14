#!/usr/bin/env python3
"""Correction 1 - re-derive incrementality from ACTUAL search_term_view history.

Modern Phrase Match matches the MEANING of the keyword, not its literal word
sequence, so raw Keyword Planner volume must NOT be credited as incremental.
This script asks a different question: which of the proposed keywords' query
space is ALREADY being matched by an enabled keyword today?

READ-ONLY. SELECT queries only.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
AUD = ROOT / "clients/softwind-power-washing/audits"
OUT = SNAP / "netnew-demand-2026-08-26.json"

# every keyword PLAN-I2A-C and PLAN-I5 propose
PROPOSED = [
    ("PLAN-I2A-C", "Power Washing Service", "power washing service", "24103511039"),
    ("PLAN-I2A-C", "Pressure Washing Service", "pressure washing service", "24145053510"),
    ("PLAN-I2A-C", "House Washing Near Me", "house washing near me", "24145053510"),
    ("PLAN-I2A-C", "Power Washing Long Island", "power washing long island", "24103511039"),
    ("PLAN-I5", "Pressure Washing Near Me", "pressure washing near me", "24145053510"),
]

STOP = {"near", "me", "a", "the", "my", "your", "for", "in", "of", "and"}


def toks(s):
    return [w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP]


def core(s):
    """Semantic core of a query: washing-verb + surface/qualifier tokens."""
    t = toks(s)
    t = ["wash" if w.startswith("wash") else w for w in t]
    t = ["power" if w in ("powerwash", "powerwashing") else w for w in t]
    return set(t)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    snap = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))
    AG = snap["ad_groups"]

    # ---- ALL search term history ----
    terms = []
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
               search_term_view.search_term, search_term_view.status,
               segments.keyword.info.text, segments.keyword.info.match_type,
               segments.search_term_match_type,
               metrics.impressions, metrics.clicks, metrics.cost_micros,
               metrics.conversions
        FROM search_term_view
        WHERE segments.date BETWEEN '2026-01-01' AND '2026-08-26'"""):
        terms.append({
            "campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group": r.ad_group.name,
            "search_term": r.search_term_view.search_term,
            "matched_keyword": r.segments.keyword.info.text,
            "keyword_match_type": enum_name(r.segments.keyword.info.match_type),
            "search_term_match_type": enum_name(r.segments.search_term_match_type),
            "impressions": int(r.metrics.impressions),
            "clicks": int(r.metrics.clicks),
            "cost": round(r.metrics.cost_micros / 1_000_000, 2),
            "conversions": float(r.metrics.conversions)})

    live = [k for k in snap["enabled_keywords_live"]]
    live_texts = sorted({k["text"] for k in live})

    out = {"generated": "2026-08-26",
           "matching_note": (
               "Modern Phrase Match matches the MEANING of a keyword, not its literal "
               "word sequence, and Exact Match matches close variants including "
               "same-meaning reformulations. Planner volume is therefore NOT credited "
               "as incremental. Incrementality is judged from whether an enabled "
               "keyword is ALREADY matching the query space."),
           "total_search_terms_all_time": len(terms),
           "total_impressions": sum(t["impressions"] for t in terms),
           "live_keyword_texts": live_texts,
           "proposals": []}

    for plan, agname, kw, cid in PROPOSED:
        kcore = core(kw)
        # every historical search term whose semantic core overlaps this keyword
        overlapping = []
        for t in terms:
            tc = core(t["search_term"])
            if not kcore:
                continue
            inter = kcore & tc
            # require the washing verb plus at least one other shared concept,
            # OR full containment of the keyword core in the query core
            if kcore <= tc or (len(inter) >= 2 and "wash" in inter):
                overlapping.append(t)

        by_kw = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0,
                                     "conv": 0.0, "terms": set(), "ad_groups": set(),
                                     "campaigns": set(), "match_types": set()})
        for t in overlapping:
            d = by_kw[t["matched_keyword"]]
            d["impr"] += t["impressions"]
            d["clicks"] += t["clicks"]
            d["cost"] += t["cost"]
            d["conv"] += t["conversions"]
            d["terms"].add(t["search_term"])
            d["ad_groups"].add(t["ad_group"])
            d["campaigns"].add(t["campaign"])
            d["match_types"].add(t["keyword_match_type"])

        already = []
        for k2, d in sorted(by_kw.items(), key=lambda x: -x[1]["impr"]):
            is_live = k2 in {x["text"] for x in live}
            already.append({
                "matched_keyword": k2,
                "keyword_is_currently_enabled": is_live,
                "match_types_seen": sorted(d["match_types"]),
                "campaigns": sorted(d["campaigns"]),
                "ad_groups": sorted(d["ad_groups"]),
                "search_terms": sorted(d["terms"]),
                "impressions": d["impr"], "clicks": d["clicks"],
                "cost": round(d["cost"], 2), "conversions": d["conv"]})

        covered_impr = sum(a["impressions"] for a in already
                           if a["keyword_is_currently_enabled"])
        covered_terms = sorted({s for a in already
                                if a["keyword_is_currently_enabled"]
                                for s in a["search_terms"]})
        # exact-text queries already seen
        exact_seen = [t for t in terms if t["search_term"].lower() == kw]

        # classification
        if covered_impr == 0 and not exact_seen:
            cls = "NET-NEW DEMAND (unobserved)"
            rationale = ("No enabled keyword has matched this query space in the "
                         "account's entire history. But note the account has only 105 "
                         "lifetime impressions, so absence of evidence here is weak "
                         "evidence of absence.")
        elif covered_impr > 0 and any(a["clicks"] == 0 for a in already
                                      if a["keyword_is_currently_enabled"]):
            cls = "ROUTING / RELEVANCE IMPROVEMENT"
            rationale = ("Enabled keywords are ALREADY matching this query space and "
                         "collecting impressions. A dedicated SKAG changes WHICH ad "
                         "serves, not WHETHER the query is reachable. Credit it as a "
                         "CTR/relevance fix, not as incremental volume.")
        else:
            cls = "ROUTING / RELEVANCE IMPROVEMENT"
            rationale = "Query space already reached by an enabled keyword."

        out["proposals"].append({
            "plan": plan, "proposed_ad_group": agname, "proposed_keyword": kw,
            "proposed_campaign_id": cid,
            "exact_query_already_observed": len(exact_seen),
            "already_matched_by": already,
            "impressions_already_covered_by_enabled_keywords": covered_impr,
            "search_terms_already_covered": covered_terms,
            "classification": cls,
            "rationale": rationale,
        })

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("SEARCH TERM HISTORY: %d rows, %d impressions all time"
          % (len(terms), sum(t["impressions"] for t in terms)))
    print()
    for p in out["proposals"]:
        print("=" * 92)
        print("%s  ->  %s   keyword: '%s'"
              % (p["plan"], p["proposed_ad_group"], p["proposed_keyword"]))
        print("  CLASSIFICATION: %s" % p["classification"])
        print("  impressions already covered by ENABLED keywords: %d"
              % p["impressions_already_covered_by_enabled_keywords"])
        print("  exact query text already observed: %d times"
              % p["exact_query_already_observed"])
        if p["already_matched_by"]:
            print("  already matched by:")
            for a in p["already_matched_by"]:
                flag = "LIVE" if a["keyword_is_currently_enabled"] else "paused"
                print("     [%s] '%s' %s  impr=%d clk=%d $%.2f conv=%.0f  ag=%s"
                      % (flag, a["matched_keyword"], a["match_types_seen"],
                         a["impressions"], a["clicks"], a["cost"], a["conversions"],
                         a["ad_groups"]))
                for s in a["search_terms"][:6]:
                    print("          term: '%s'" % s)
        else:
            print("  already matched by: NOTHING in account history")
        print("  %s" % p["rationale"])
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
