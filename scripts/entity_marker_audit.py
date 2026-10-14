#!/usr/bin/env python3
"""Does the entity-marker defect fixed on 2026-08-30 affect the accounts that
already executed?

neg_names.py added BROAD entity markers (llc, inc, corp, ...) without checking
whether the token also sits inside a KEEP-verdict search term, whether it is an
English word, or whether the corpus holds any evidence for it at all. Those
guards now exist. The three executed accounts were built and written BEFORE the
fix, so their live negatives may carry markers the guards would now refuse.

Reads the FROZEN 2026-08-28 bundles (what was actually executed) plus each
account's verdict table. No API calls.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERD = ROOT / "reports" / "st-verdicts"
LEX = ROOT / "reports" / "lexicons"
TOK = re.compile(r"[a-z0-9]+")
MARKERS = {"llc", "inc", "corp", "corporation", "incorporated", "ltd"}

EXECUTED = {
    "ambient-cooling-heating":
        "clients/ambient-cooling-heating/plans/2026-08-28-negative-expansion.json",
    "pro-green-austin":
        "clients/pro-green-austin/plans/2026-08-28-negative-expansion.json",
    "softwind-power-washing":
        "clients/softwind-power-washing/plans/2026-08-28-negative-expansion.json",
}


def toks(s):
    return TOK.findall(s.lower())


def main() -> int:
    english = {w.strip() for w in
               (LEX / "english_words.txt").read_text(encoding="utf-8").splitlines()
               if w.strip()}

    for slug, rel in EXECUTED.items():
        plan = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        sub = plan["subplans"].get("NEG_NAME_BROAD")
        print("=" * 74)
        print("{}  ({})".format(slug, plan["target"]["child_customer_id"]))
        print("=" * 74)
        if not sub or not sub.get("detail"):
            print("  no NEG_NAME_BROAD layer")
            continue

        live_markers = sorted({n["text"].lower()
                               for d in sub["detail"] for n in d["negatives"]
                               if n["text"].lower() in MARKERS})
        print("  entity markers LIVE as BROAD negatives: {}".format(
            ", ".join(live_markers) if live_markers else "none"))
        if not live_markers:
            continue

        vp = VERD / (slug + "-verdicts.csv")
        if not vp.exists():
            print("  no verdict table on disk; cannot assess")
            continue

        rows = list(csv.DictReader(vp.open(encoding="utf-8")))
        for m in live_markers:
            blocked = [r for r in rows
                       if m in toks(r["search_term"])
                       and (r["verdict"] == "KEEP" or float(r["conversions"]) > 0)]
            allhits = [r for r in rows if m in toks(r["search_term"])]
            cost = sum(float(r["cost_usd"]) for r in allhits)
            conv = sum(float(r["conversions"]) for r in blocked)
            flags = []
            if blocked:
                flags.append("blocks {} KEEP/converting".format(len(blocked)))
            if m in english:
                flags.append("english word")
            if not allhits:
                flags.append("no corpus evidence")
            print("    {:<14} corpus_terms={:<4} cost=${:<9.2f} "
                  "blocked_conv={:<5} {}".format(
                      m, len(allhits), cost, conv,
                      ("<-- " + "; ".join(flags)) if flags else "clean"))
            for r in blocked[:6]:
                print("        KEEP {:<44} cost=${:<8} conv={}".format(
                    r["search_term"][:44], r["cost_usd"], r["conversions"]))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
