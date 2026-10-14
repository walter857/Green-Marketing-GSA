#!/usr/bin/env python3
"""Mine competitor / unknown-entity candidates.

A competitor query usually carries a real service token, so the whitelist marks
it KEEP. This finds the leak: KEEP/WATCH terms containing a token that is not
service vocabulary, not commercial intent, not a targeted place name, not the
client's own brand, and not a generic modifier.

Candidates are ranked and written to disk for term-level approval. Nothing here
auto-negatives: a competitor name is a business fact the owner confirms.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from neg_lexicon import ACCOUNTS, compile_account  # noqa: E402

CORPUS = ROOT / "reports" / "st-corpus"
VERD = ROOT / "reports" / "st-verdicts"
OUT = ROOT / "reports" / "st-competitors"

TOKEN_RE = re.compile(r"[a-z0-9']+")

GENERIC = {
    "the", "a", "an", "and", "or", "of", "for", "to", "in", "on", "at", "by",
    "with", "my", "me", "you", "your", "our", "it", "is", "are", "do", "does",
    "can", "how", "what", "who", "where", "when", "which", "that", "this",
    "there", "here", "from", "up", "out", "off", "over", "under", "about",
    "into", "than", "then", "them", "they", "we", "us", "i", "no", "not",
    "near", "nearby", "close", "closest", "around", "local", "locally",
    "best", "top", "good", "great", "cheap", "cheapest", "affordable",
    "quality", "professional", "pro", "expert", "experts", "trusted",
    "reliable", "licensed", "insured", "reviews", "rated", "rating",
    "cost", "costs", "price", "prices", "pricing", "quote", "quotes",
    "estimate", "estimates", "free", "same", "day", "hour", "hours",
    "24", "7", "247", "emergency", "urgent", "fast", "quick", "now",
    "today", "tonight", "weekend", "sunday", "saturday", "monday",
    "home", "homes", "house", "houses", "residential", "commercial",
    "small", "large", "big", "new", "old", "used", "full", "complete",
    "service", "services", "company", "companies", "contractor",
    "contractors", "business", "businesses", "shop", "specialist",
    "specialists", "team", "crew", "guy", "guys", "man", "men", "people",
    "number", "phone", "call", "contact", "address", "hours", "open",
    "front", "back", "side", "yard", "outdoor", "outside", "exterior",
    "square", "foot", "feet", "ft", "sq", "per", "average", "much",
    "one", "two", "three", "four", "five", "10", "100", "1000",
    "s", "llc", "inc", "co", "corp", "and",
}


def toks(s):
    return TOKEN_RE.findall(s.lower())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    grand = {}

    for slug, cfg in ACCOUNTS.items():
        corpus_path = CORPUS / (slug + "-corpus.json")
        if not corpus_path.exists():
            print("[{}] SKIP: no corpus on disk yet".format(slug))
            continue
        try:
            comp = compile_account(cfg)
        except ValueError as exc:
            print("[{}] SKIP: {}".format(slug, exc))
            continue
        d = json.loads(corpus_path.read_text(encoding="utf-8"))

        terms = {}
        with (VERD / (slug + "-verdicts.csv")).open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                terms[r["search_term"]] = {
                    "verdict": r["verdict"], "category": r["category"],
                    "impr": int(r["impressions"]), "clicks": int(r["clicks"]),
                    "cost": float(r["cost_usd"]), "conv": float(r["conversions"]),
                }

        # vocabulary a token is allowed to belong to
        known = set(GENERIC)
        for p in d["positive_keywords"]:
            known.update(toks(p["text"]))

        def is_known(tok: str) -> bool:
            if tok in known or len(tok) < 4 or tok.isdigit():
                return True
            probe = " " + tok + " "
            return bool(comp["core"].search(probe) or comp["intent"].search(probe)
                        or comp["geo_in"].search(probe) or comp["brand"].search(probe)
                        or comp["geo_out"].search(probe))

        cand = defaultdict(lambda: {"terms": set(), "impr": 0, "clicks": 0,
                                    "cost": 0.0, "conv": 0.0})
        for term, v in terms.items():
            if v["verdict"] not in ("KEEP", "WATCH"):
                continue
            if v["category"] == "BRAND_PROTECTED":
                continue
            for tok in set(toks(term)):
                if is_known(tok):
                    continue
                c = cand[tok]
                c["terms"].add(term)
                c["impr"] += v["impr"]
                c["clicks"] += v["clicks"]
                c["cost"] += v["cost"]
                c["conv"] += v["conv"]

        rows = []
        for tok, c in cand.items():
            if len(c["terms"]) < 2 and c["cost"] == 0:
                continue
            rows.append({
                "token": tok, "distinct_terms": len(c["terms"]),
                "impressions": c["impr"], "clicks": c["clicks"],
                "cost_usd": round(c["cost"], 2), "conversions": round(c["conv"], 2),
                "auto_negative_eligible": c["conv"] == 0,
            })
        rows.sort(key=lambda r: (-r["cost_usd"], -r["distinct_terms"]))

        p = OUT / (slug + "-competitor-candidates.csv")
        with p.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else
                               ["token", "distinct_terms", "impressions", "clicks",
                                "cost_usd", "conversions", "auto_negative_eligible"])
            w.writeheader()
            w.writerows(rows)

        spend = sum(r["cost_usd"] for r in rows)
        eligible = [r for r in rows if r["auto_negative_eligible"]]
        elig_spend = sum(r["cost_usd"] for r in eligible)
        blocked_by_conv = [r for r in rows if not r["auto_negative_eligible"]]

        print("=" * 78)
        print("{}  ({})".format(slug, cfg["customer_id"]))
        print("=" * 78)
        print("  unknown-entity tokens inside KEEP/WATCH terms : {}".format(len(rows)))
        print("  spend sitting on those terms                  : ${:,.2f}".format(spend))
        print("  eligible for negation (zero conversions)      : {}  (${:,.2f})".format(
            len(eligible), elig_spend))
        print("  held back by the conversion guard             : {}".format(
            len(blocked_by_conv)))
        print("  with >=$25 spend and zero conversions         : {}".format(
            len([r for r in eligible if r["cost_usd"] >= 25])))
        print("  review file -> {}\n".format(p.relative_to(ROOT)))

        grand[slug] = {"candidate_tokens": len(rows), "spend_usd": round(spend, 2),
                       "eligible": len(eligible), "eligible_spend": round(elig_spend, 2)}

    (OUT / "summary.json").write_text(json.dumps(grand, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
