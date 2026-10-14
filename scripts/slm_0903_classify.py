#!/usr/bin/env python3
"""Classify the Softwind Landscape & Masonry search-term corpus.

Corpus isolation rule (memory search-term-corpus-context-isolation):
raw terms stay on disk. This script writes the full verdict CSV and prints
AGGREGATES plus, at most, the service-vocabulary tokens that drive a bucket.
It never prints the residual OUT_OF_SCOPE strings.

Classification is by WHITELIST first (in-scope intent), then by explicit
wrong-service markers. Anything matching neither lands in UNCLASSIFIED and is
reported only as a count and a cost share.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PATIO, PAVERS = "23484806108", "23489296528"

# ---------------------------------------------------------------- vocabulary
# In-scope service nouns. A term needs at least one of these to be considered.
CORE = {
    "patio", "patios", "paver", "pavers", "paving stone", "paving stones",
    "paving", "pave", "paved", "hardscape", "hardscaping", "hardscapes",
    "walkway", "walkways", "walk way", "interlocking", "brick paver",
    "stone paver", "travertine", "flagstone", "cobblestone", "bluestone",
    "coping", "stepping stone", "stepping stones", "porch", "belgard",
    "cambridge", "techo", "unilock", "nicolock",
}
# Buyer-intent qualifiers. Presence strengthens a KEEP/PROMOTE verdict.
INTENT = {
    "install", "installation", "installer", "installers", "installed",
    "contractor", "contractors", "builder", "builders", "build", "construction",
    "company", "companies", "service", "services", "near me", "quote",
    "estimate", "cost", "price", "pricing", "hire", "local", "best",
}
# Explicit wrong-service markers. Each maps to the exclusion family it proves.
WRONG = {
    "asphalt": "asphalt",
    "blacktop": "asphalt",
    "tar and chip": "asphalt",
    "tar & chip": "asphalt",
    "sealcoat": "sealcoating",
    "sealcoating": "sealcoating",
    "seal coating": "sealcoating",
    "seal coat": "sealcoating",
    "sealer": "sealing",
    "sealing": "sealing",
    "sealant": "sealing",
    "resand": "restoration",
    "re-sand": "restoration",
    "resanding": "restoration",
    "polymeric sand": "restoration",
    "restoration": "restoration",
    "restore": "restoration",
    "releveling": "restoration",
    "releveled": "restoration",
    "resurfacing": "resurfacing",
    "resurface": "resurfacing",
    "refinish": "resurfacing",
    "power wash": "cleaning",
    "powerwash": "cleaning",
    "pressure wash": "cleaning",
    "soft wash": "cleaning",
    "house wash": "cleaning",
    "cleaning": "cleaning",
    "cleaner": "cleaning",
    "patio cover": "patio-cover",
    "patio covers": "patio-cover",
    "covered patio": "patio-cover",
    "patio roof": "patio-cover",
    "patio awning": "patio-cover",
    "awning": "patio-cover",
    "canopy": "patio-cover",
    "pergola": "patio-cover",
    "gazebo": "patio-cover",
    "screened": "enclosure",
    "screen room": "enclosure",
    "sunroom": "enclosure",
    "enclosure": "enclosure",
    "enclosures": "enclosure",
    "patio door": "not-a-service",
    "patio doors": "not-a-service",
    "patio furniture": "retail",
    "patio set": "retail",
    "patio umbrella": "retail",
    "patio heater": "retail",
    "patio lights": "retail",
    "home depot": "retail",
    "lowes": "retail",
    "lowe's": "retail",
    "menards": "retail",
    "for sale": "retail",
    "supplier": "retail",
    "suppliers": "retail",
    "wholesale": "retail",
    "supply": "retail",
    "yard": "retail",
    "per pallet": "retail",
    "pallet": "retail",
    "square foot": "diy-pricing",
    "sq ft": "diy-pricing",
    "calculator": "diy",
    "how to": "diy",
    "diy": "diy",
    "yourself": "diy",
    "youtube": "diy",
    "ideas": "research",
    "designs": "research",
    "design software": "research",
    "pictures": "research",
    "photos": "research",
    "jobs": "employment",
    "hiring": "employment",
    "salary": "employment",
    "careers": "employment",
    "rental": "equipment",
    "rent": "equipment",
    "machine": "equipment",
    "tool": "equipment",
    "mold": "equipment",
    "molds": "equipment",
    "repair": "repair",
    "repairs": "repair",
    "fix": "repair",
    "replacement": "repair",
    "wood deck": "deck",
    "composite deck": "deck",
    "trex": "deck",
    "deck builder": "deck",
    "decking": "deck",
}
# Themes the owner has NOT resolved. Never negate, never promote.
UNRESOLVED = {
    "driveway": "driveway-pavers",
    "concrete": "concrete",
    "bluestone": "bluestone",
    "blue stone": "bluestone",
    "masonry": "masonry",
    "mason": "masonry",
    "stoop": "masonry",
    "steps": "masonry",
    "retaining wall": "retaining-wall-other-campaign",
    "pool deck": "pool-deck",
    "pool patio": "pool-deck",
    "pavement": "pavement-ambiguous",
    "deck": "deck-ambiguous",
    "decks": "deck-ambiguous",
}


def has(t: str, needles) -> list[str]:
    return [n for n in needles if re.search(r"(?<![a-z])" + re.escape(n) + r"(?![a-z])", t)]


def classify(term: str):
    t = " " + term.lower().strip() + " "
    wrong = sorted({WRONG[n] for n in has(t, WRONG)})
    unres = sorted({UNRESOLVED[n] for n in has(t, UNRESOLVED)})
    core = has(t, CORE)
    intent = has(t, INTENT)
    if wrong:
        return "NEGATIVE", wrong, unres, core, intent
    if unres:
        return "UNRESOLVED", wrong, unres, core, intent
    if core and intent:
        return "KEEP", wrong, unres, core, intent
    if core:
        return "WATCH", wrong, unres, core, intent
    return "UNCLASSIFIED", wrong, unres, core, intent


def main() -> int:
    d = json.loads((B / "01b-before-performance.json").read_text(encoding="utf-8"))
    rows = d["st_alltime"]

    agg = defaultdict(lambda: {"cost": 0.0, "clicks": 0, "impr": 0, "conv": 0.0,
                               "allconv": 0.0, "campaigns": set(), "ad_groups": set(),
                               "keywords": set()})
    for r in rows:
        a = agg[(r["campaign_id"], r["term"])]
        a["cost"] += r["cost"] or 0.0
        a["clicks"] += r["clicks"]
        a["impr"] += r["impressions"]
        a["conv"] += r["conversions"]
        a["allconv"] += r["all_conversions"]
        a["campaigns"].add(r["campaign_name"])
        a["ad_groups"].add(r["ad_group_name"])
        a["keywords"].add("%s [%s]" % (r["keyword"], r["keyword_match_type"]))

    out_rows, buckets = [], defaultdict(lambda: {"n": 0, "cost": 0.0, "clicks": 0,
                                                 "impr": 0, "conv": 0.0})
    fam = defaultdict(lambda: {"n": 0, "cost": 0.0, "clicks": 0, "conv": 0.0})
    scope_cost = {"in": 0.0, "all": 0.0}
    for (cid, term), a in agg.items():
        verdict, wrong, unres, core, intent = classify(term)
        in_scope_campaign = cid in (PATIO, PAVERS)
        out_rows.append({
            "campaign_id": cid, "campaign": "|".join(sorted(a["campaigns"])),
            "ad_groups": "|".join(sorted(a["ad_groups"])),
            "matched_keywords": "|".join(sorted(a["keywords"])),
            "search_term": term, "verdict": verdict,
            "wrong_service_family": "|".join(wrong),
            "unresolved_theme": "|".join(unres),
            "core_tokens": "|".join(sorted(set(core))),
            "intent_tokens": "|".join(sorted(set(intent))),
            "impressions": a["impr"], "clicks": a["clicks"],
            "cost": round(a["cost"], 2), "conversions": round(a["conv"], 2),
            "all_conversions": round(a["allconv"], 2),
            "in_recovery_scope": in_scope_campaign,
        })
        if not in_scope_campaign:
            continue
        scope_cost["all"] += a["cost"]
        b = buckets[verdict]
        b["n"] += 1; b["cost"] += a["cost"]; b["clicks"] += a["clicks"]
        b["impr"] += a["impr"]; b["conv"] += a["conv"]
        for f in wrong:
            fam[f]["n"] += 1; fam[f]["cost"] += a["cost"]
            fam[f]["clicks"] += a["clicks"]; fam[f]["conv"] += a["conv"]
        for f in unres:
            fam["UNRESOLVED:" + f]["n"] += 1; fam["UNRESOLVED:" + f]["cost"] += a["cost"]
            fam["UNRESOLVED:" + f]["clicks"] += a["clicks"]
            fam["UNRESOLVED:" + f]["conv"] += a["conv"]

    p = B / "05-search-term-verdicts.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(sorted(out_rows, key=lambda r: -r["cost"]))

    total = scope_cost["all"]
    print("PATIO + PAVERS SEARCH-TERM CORPUS (all retained history, 2026-01-01 ->)")
    print("  unique (campaign, term) pairs in scope : %d" % sum(b["n"] for b in buckets.values()))
    print("  total in-scope search-term cost        : $%.2f" % total)
    print("\n%-14s %6s %10s %8s %8s %8s %8s" % ("verdict","terms","cost","cost%","clicks","impr","conv"))
    for k in ("KEEP", "WATCH", "UNRESOLVED", "NEGATIVE", "UNCLASSIFIED"):
        b = buckets[k]
        print("%-14s %6d %10.2f %7.1f%% %8d %8d %8.1f" % (
            k, b["n"], b["cost"], 100*b["cost"]/total if total else 0,
            b["clicks"], b["impr"], b["conv"]))
    print("\nWRONG-SERVICE / UNRESOLVED FAMILIES (in-scope campaigns)")
    print("%-38s %6s %10s %8s %8s %6s" % ("family","terms","cost","cost%","clicks","conv"))
    for k in sorted(fam, key=lambda x: -fam[x]["cost"]):
        v = fam[k]
        print("%-38s %6d %10.2f %7.1f%% %8d %6.1f" % (
            k, v["n"], v["cost"], 100*v["cost"]/total if total else 0, v["clicks"], v["conv"]))
    print("\nwrote %s (%d rows, all campaigns)" % (p.relative_to(ROOT), len(out_rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
