#!/usr/bin/env python3
"""Detail behind the three red-team failures on the SLM bundle."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "softwind-landscape-masonry"
PLAN = ROOT / "clients" / SLUG / "plans" / "2026-08-30-negative-expansion.json"
CORPUS = ROOT / "reports" / "st-corpus" / (SLUG + "-corpus.json")
VERD = ROOT / "reports" / "st-verdicts" / (SLUG + "-verdicts.csv")
TOK = re.compile(r"[a-z0-9]+")
LAYERS = ["NEG_CAMPAIGN_LEVEL", "NEG_NAME_BROAD", "NEG_CROSS_ACCOUNT_FENCE"]
ENTITY = {"llc", "inc", "corp", "corporation", "incorporated", "ltd"}


def toks(s):
    return TOK.findall(s.lower())


def contiguous(sub, seq):
    n = len(sub)
    return bool(n) and n <= len(seq) and any(
        seq[i:i + n] == sub for i in range(len(seq) - n + 1))


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))

    negs = []
    for layer in LAYERS:
        for d in plan["subplans"][layer]["detail"]:
            for n in d["negatives"]:
                negs.append((n["text"], n["match_type"], layer,
                             d["campaign_id"], d["campaign_name"]))

    print("=" * 74)
    print("A. CROSS-LAYER DUPLICATES")
    print("=" * 74)
    seen, dups = {}, []
    for text, mt, layer, cid, cn in negs:
        k = (cid, " ".join(toks(text)), mt)
        if k in seen:
            dups.append((text, mt, seen[k], layer, cn))
        else:
            seen[k] = layer
    pairs = {}
    for text, mt, first, second, cn in dups:
        pairs[(first, second)] = pairs.get((first, second), 0) + 1
    for (a, b), n in pairs.items():
        print("  {} objects appear in BOTH {} and {}".format(n, a, b))
    print("  distinct duplicated texts: {}".format(
        len({d[0] for d in dups})))
    for text in sorted({d[0] for d in dups}):
        print("     {}".format(text))

    print()
    print("=" * 74)
    print("B. ENTITY MARKERS vs KEEP TERMS  (BROAD llc / inc / ...)")
    print("=" * 74)
    keep = []
    with VERD.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            keep.append(r)
    ent_hits = []
    for r in keep:
        tk = toks(r["search_term"])
        for e in ENTITY:
            if e in tk:
                ent_hits.append((r["search_term"], r["verdict"], e,
                                 float(r["cost_usd"]), float(r["conversions"])))
    print("  search terms in the WHOLE corpus containing an entity marker: {}"
          .format(len(ent_hits)))
    byv = {}
    for _, v, _, c, cv in ent_hits:
        d = byv.setdefault(v, [0, 0.0, 0.0])
        d[0] += 1
        d[1] += c
        d[2] += cv
    for v in sorted(byv):
        n, c, cv = byv[v]
        print("    {:<10} terms={:<4} cost=${:<10.2f} conv={}".format(v, n, c, cv))
    print("  KEEP/converting terms that BROAD entity markers would block:")
    for t, v, e, c, cv in sorted(ent_hits, key=lambda x: -x[3]):
        if v == "KEEP" or cv > 0:
            print("    {:<46} marker={:<6} cost=${:<8.2f} conv={}".format(
                t[:46], e, c, cv))
    # brand-block risk
    brand_hits = [h for h in ent_hits if "softwind" in h[0].lower()]
    print("  OWN-BRAND terms containing an entity marker: {}".format(len(brand_hits)))
    for t, v, e, c, cv in brand_hits:
        print("    {:<46} {:<8} cost=${:.2f} conv={}".format(t[:46], v, c, cv))

    print()
    print("=" * 74)
    print("C. MANUFACTURER TERMS PROPOSED AS NEGATIVES")
    print("=" * 74)
    MAN = ["nicolock", "belgard", "cambridge", "techo", "unilock",
           "ep henry", "nicolia"]
    prop = sorted({(text, mt, layer) for text, mt, layer, _, _ in negs
                   if any(m in text.lower() for m in MAN)})
    for text, mt, layer in prop:
        print("  {:<34} {:<8} {}".format(text, mt, layer))
    print()
    print("  every corpus term mentioning a manufacturer:")
    rows = []
    for r in keep:
        if any(m in r["search_term"].lower() for m in MAN):
            rows.append((r["search_term"], r["verdict"], float(r["cost_usd"]),
                         float(r["conversions"])))
    for t, v, c, cv in sorted(rows, key=lambda x: -x[2]):
        print("    {:<46} {:<9} cost=${:<8.2f} conv={}".format(t[:46], v, c, cv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
