#!/usr/bin/env python3
"""2026-10-05 individual verdicts for every visible Apogee search term (work order permits raw terms)."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "clients/apogee-lawns/audits/2026-10-05-conversion-plan"
HIRE, LOCAL, COST = "installation hiring", "local installation hiring", "installation cost research"
MIX, PROD, INFO = "mixed: product or hiring", "product shopping or comparison", "informational"
V = {  # term: (intent class, action, reason)
    "permanent christmas lights": (MIX, "KEEP (head-term Exact trial)", "the keyword itself; installation-focused copy is being tested"),
    "brilliant by night nebraska": ("competitor navigational", "NEGATIVE phrase 'brilliant by night'", "Brilliant By Night is a permanent-lighting company serving Lincoln (brilliantbynight.com/lincoln); searcher wants that company"),
    "brilliant by night": ("competitor navigational", "NEGATIVE phrase 'brilliant by night'", "same competitor"),
    "permanent lighting on house": (MIX, "KEEP eligible; monitor", "roofline lighting phrasing; could be a buyer"),
    "permanent lights": (MIX, "KEEP eligible; monitor", "too generic to judge; Exact close variant"),
    "best permanent outdoor lights": (PROD, "KEEP eligible (protected 'best'); monitor", "comparison shopping; agency policy protects 'best'"),
    "permanent christmas lights lincoln ne": (LOCAL, "ADD Exact to installation ad group", "local buyer; only reached by meaning-based Phrase matching today"),
    "permanent lighting": (MIX, "KEEP eligible; monitor", "generic"),
    "permanent lights on house": (MIX, "KEEP eligible; monitor", "roofline lighting phrasing"),
    "permanent outdoor christmas lights": (MIX, "KEEP eligible; monitor", "service or product"),
    "permanent outdoor lighting": (MIX, "KEEP eligible; monitor", "may also mean landscape lighting; watch clicks"),
    "permanent outdoor lights": (PROD, "KEEP eligible; monitor", "product-leaning phrasing"),
    "outdoor permanent lights": (PROD, "KEEP eligible; monitor", "product-leaning phrasing"),
    "permanent house lights": (MIX, "KEEP eligible; monitor", "roofline lighting phrasing"),
    "best permanent christmas lights": (PROD, "KEEP eligible (protected 'best'); monitor", "comparison; protected word"),
    "cost of permanent lights on house": (COST, "KEEP eligible (protected 'cost')", "pricing research before hiring"),
    "cost to install permanent outdoor lights": (COST, "KEEP eligible (protected 'cost')", "installation cost question"),
    "high end permanent christmas lights": (PROD, "KEEP eligible; monitor", "premium shopper; could hire"),
    "how much do forever christmas lights cost": (COST, "KEEP eligible (protected 'cost')", "pricing research"),
    "how much does it cost to have permanent christmas lights installed": (COST, "KEEP eligible", "explicit installation cost question"),
    "how much does it cost to have permanent lights installed": (COST, "KEEP eligible", "explicit installation cost question"),
    "led permanent christmas lights": (PROD, "KEEP eligible; monitor", "product spec phrasing"),
    "outdoor permanent holiday lights": (MIX, "KEEP eligible; monitor", "service or product"),
    "permanent christmas lights installation near me": (LOCAL, "ADD Exact to installation ad group", "local buyer; Exact gives it its own row and bid"),
    "permanent holiday light installation near me": (LOCAL, "ADD Exact to installation ad group", "local buyer; only reached by meaning-based matching today"),
    "permanent light for house": (MIX, "KEEP eligible; monitor", "roofline lighting phrasing"),
    "permanent lighting installation": (HIRE, "ADD Exact to installation ad group", "hiring phrasing; only reached by meaning-based matching today"),
    "types of permanent outdoor christmas lights": (INFO, "NEGATIVE Exact (this query only)", "informational; narrow Exact, not a broad 'types of' exclusion"),
    "year round christmas lights": (MIX, "KEEP eligible; monitor", "service or product"),
    "inception permanent lighting": ("brand: Inception Lighting system", "HOLD (no negative)", "compatibility with customer-supplied Inception systems unconfirmed; owner question"),
    "permanent christmas light installation near me": (LOCAL, "KEEP (already matched literally by the Phrase keyword)", "no new keyword needed"),
    "permanent lights on house cost": (COST, "KEEP eligible (protected 'cost')", "pricing research"),
    "permanent outdoor light": (PROD, "KEEP eligible; monitor", "product-leaning phrasing"),
    "outdoor house lights permanent": (MIX, "KEEP eligible; monitor", "roofline lighting phrasing"),
    "permanent christmas": (MIX, "KEEP eligible; monitor", "truncated query"),
    "permanent outdoor holiday lights": (MIX, "KEEP eligible; monitor", "service or product"),
}
rows = list(csv.DictReader((AUD / "search_terms_2026-09-21_to_2026-10-05.csv").open(encoding="utf-8")))
missing = [r["search_term"] for r in rows if r["search_term"] not in V]
assert not missing, f"unclassified terms: {missing}"
with (AUD / "02_search_term_verdicts.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["search_term", "ad_group_id", "matched_keyword", "keyword_match", "query_match", "impressions",
                "clicks", "cost", "intent_class", "action", "reason"])
    for r in rows:
        cls, act, why = V[r["search_term"]]
        w.writerow([r["search_term"], r["ad_group_id"], r["keyword"], r["keyword_match"], r["query_match"],
                    r["impressions"], r["clicks"], r["cost"], cls, act, why])
from collections import Counter
cnt = Counter(V[r["search_term"]][0] for r in rows)
imp = Counter()
for r in rows:
    imp[V[r["search_term"]][0]] += int(r["impressions"])
print("terms:", len(rows), "impressions:", sum(int(r["impressions"]) for r in rows))
for k in cnt:
    print(f"  {k:32s} terms={cnt[k]:>2} impressions={imp[k]:>3}")
