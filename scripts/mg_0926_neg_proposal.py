#!/usr/bin/env python3
"""2026-09-26 LOCAL: Master Grass negative-keyword proposal, built from agency vocabulary.

Each proposed negative below is written by the strategist (not copied from a search term). Every
one is tested against: live enabled positive keywords, converting live-campaign terms, KEEP/WATCH
terms, the agency PROTECTED list, and existing negatives. Only negatives whose guard is "ok" are
proposed. stdout prints the proposed negatives (strategist text) with counts and cost they would
have blocked; raw search terms never print.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from neg_lexicon import PROTECTED  # noqa: E402

SNAP = ROOT / "clients" / "mastergrass-lawn-care" / "snapshots" / "audit-2026-09-26"
ST = ROOT / "reports" / "mastergrass-lawn-care" / "st"
LIVE = {"23905193676": "Landscaping Search - BOFU", "23914692658": "Hardscaping Search - BOFU"}
TOK = re.compile(r"[a-z0-9']+")


def toks(s):
    return TOK.findall(s.lower())


def blocks(neg, mt, q):
    if mt == "EXACT":
        return neg == q
    if mt == "PHRASE":
        n = len(neg)
        return any(q[i:i + n] == neg for i in range(len(q) - n + 1)) if n and n <= len(q) else False
    return bool(neg) and set(neg) <= set(q)


# Strategist-authored candidates: (text, match, reason, scope)
# scope "both" = both live campaigns; "land" / "hard" = one campaign (cross-negative).
PROPOSED = [
    # Other Master Grass services these BOFU landscaping/hardscaping pages do not sell.
    ("lawn care", "PHRASE", "maintenance service, not landscape install", "both"),
    ("lawn service", "PHRASE", "maintenance service", "both"),
    ("lawn services", "PHRASE", "maintenance service", "both"),
    ("lawn mowing", "PHRASE", "maintenance service", "both"),
    ("mowing", "PHRASE", "maintenance service", "both"),
    ("fertilization", "PHRASE", "lawn treatment", "both"),
    ("fertilizer", "PHRASE", "lawn treatment / product", "both"),
    ("weed control", "PHRASE", "lawn treatment", "both"),
    ("aeration", "PHRASE", "lawn treatment", "both"),
    ("overseeding", "PHRASE", "lawn treatment", "both"),
    ("tree removal", "PHRASE", "tree service", "both"),
    ("tree trimming", "PHRASE", "tree service", "both"),
    ("stump", "PHRASE", "tree service", "both"),
    ("snow removal", "PHRASE", "seasonal service", "both"),
    ("snow plowing", "PHRASE", "seasonal service", "both"),
    ("leaf removal", "PHRASE", "seasonal service", "both"),
    ("christmas lights", "PHRASE", "seasonal service", "both"),
    ("sprinkler", "PHRASE", "irrigation, separate trade here", "both"),
    ("irrigation", "PHRASE", "irrigation, separate trade here", "both"),
    ("sod", "PHRASE", "sod install not advertised", "both"),
    # Intent / audience the agency never wants on BOFU
    ("jobs", "PHRASE", "employment", "both"),
    ("hiring", "PHRASE", "employment", "both"),
    ("salary", "PHRASE", "employment", "both"),
    ("diy", "PHRASE", "do it yourself", "both"),
    ("how to", "PHRASE", "informational", "both"),
    ("ideas", "PHRASE", "inspiration", "both"),
    ("pictures", "PHRASE", "inspiration", "both"),
    ("supply", "PHRASE", "materials buyer", "both"),
    ("supplies", "PHRASE", "materials buyer", "both"),
    ("home depot", "PHRASE", "retail", "both"),
    ("menards", "PHRASE", "retail", "both"),
    ("lowes", "PHRASE", "retail", "both"),
    ("rental", "PHRASE", "equipment rental", "both"),
    ("software", "PHRASE", "B2B", "both"),
    ("school", "PHRASE", "training", "both"),
    ("degree", "PHRASE", "training", "both"),
    ("free", "PHRASE", "freebie seekers", "both"),
    ("tree service", "PHRASE", "tree service", "both"),
    ("tree", "PHRASE", "tree service", "both"),
    ("trees", "PHRASE", "tree service", "both"),
    ("hedge", "PHRASE", "shrub care", "both"),
    ("shrub", "PHRASE", "shrub care", "both"),
    ("bush", "PHRASE", "shrub care", "both"),
    ("weed", "PHRASE", "lawn treatment", "both"),
    ("mower", "PHRASE", "equipment / mowing", "both"),
    ("seeding", "PHRASE", "lawn seeding", "both"),
    # Cross-negatives so the two campaigns stop competing for each other's services
    ("retaining wall", "PHRASE", "belongs to Hardscaping", "land"),
    ("pavers", "PHRASE", "belongs to Hardscaping", "land"),
    ("paver", "PHRASE", "belongs to Hardscaping", "land"),
    ("patio", "PHRASE", "belongs to Hardscaping", "land"),
    ("fire pit", "PHRASE", "belongs to Hardscaping", "land"),
    ("outdoor kitchen", "PHRASE", "belongs to Hardscaping", "land"),
    ("french drain", "PHRASE", "belongs to Landscaping", "hard"),
    ("drainage", "PHRASE", "belongs to Landscaping", "hard"),
    ("grading", "PHRASE", "belongs to Landscaping", "hard"),
    ("mulch", "PHRASE", "belongs to Landscaping", "hard"),
]

kw = json.loads((SNAP / "keywords.json").read_text(encoding="utf-8"))
live_pos = {cid: set() for cid in LIVE}
for r in kw:
    a = r["ad_group_criterion"]
    if r["campaign"]["id"] in LIVE and not a.get("negative") and a.get("status") == "ENABLED":
        live_pos[r["campaign"]["id"]].add(a["keyword"]["text"].lower())
existing = {cid: set() for cid in LIVE}
for r in json.loads((SNAP / "campaign_criteria.json").read_text(encoding="utf-8")):
    cc = r["campaign_criterion"]
    if r["campaign"]["id"] in LIVE and cc.get("negative") and cc.get("keyword"):
        existing[r["campaign"]["id"]].add(cc["keyword"]["text"].lower().strip('"[] '))

terms = []
with (ST / "verdicts.csv").open(encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        terms.append({"t": toks(row["term"]), "v": row["verdict"], "cat": row["category"],
                      "camps": row["campaigns"], "cost": float(row["cost_all"]),
                      "conv": float(row["conv_all"]), "cost30": float(row["cost_l30"])})
prot = [toks(p) for p in PROTECTED]
scopes = {"both": list(LIVE), "land": ["23905193676"], "hard": ["23914692658"]}

ok_rows, bad_rows = [], []
for text, mt, reason, scope in PROPOSED:
    nt = toks(text)
    problems = []
    if text in PROTECTED or any(nt == p for p in prot):
        problems.append("protected")
    for cid in scopes[scope]:
        hit = [p for p in live_pos[cid] if blocks(nt, mt, toks(p))]
        if hit:
            problems.append(f"blocks {len(hit)} live keyword(s) in {LIVE[cid][:11]}: {sorted(hit)[:3]}")
        if text in existing[cid]:
            problems.append(f"already negative in {LIVE[cid][:11]}")
    camp_names = {LIVE[c] for c in scopes[scope]}
    blocked = [t for t in terms if blocks(nt, mt, t["t"]) and (set(t["camps"].split("|")) & camp_names)]
    conv_hit = [t for t in blocked if t["conv"] > 0]
    keep_hit = [t for t in blocked if t["v"] == "KEEP" and t["cat"] == "IN_SCOPE_COMMERCIAL"]
    if conv_hit:
        problems.append(f"blocks {len(conv_hit)} converting term(s)")
    row = (text, mt, scope, reason, len(blocked), sum(t["cost"] for t in blocked),
           sum(t["cost30"] for t in blocked), len(keep_hit))
    (bad_rows if problems else ok_rows).append((row, problems))

print(f"{'negative':<18}{'match':<7}{'scope':<6}{'terms':>6}{'cost_all':>10}{'cost_30d':>10}{'keep_hit':>9}  reason")
for (text, mt, scope, reason, n, c, c30, kh), _ in sorted(ok_rows, key=lambda x: -x[0][5]):
    print(f"{text:<18}{mt:<7}{scope:<6}{n:>6}{c:>10.2f}{c30:>10.2f}{kh:>9}  {reason}")
print(f"\nPASS {len(ok_rows)} | tot blocked all-time ${sum(r[0][5] for r in ok_rows):,.2f} | 30d ${sum(r[0][6] for r in ok_rows):,.2f}")
print("\nREJECTED by guard:")
for (text, mt, scope, *_), probs in bad_rows:
    print(f"  {text:<18}{mt:<7}{scope:<6} {probs}")

with (ST / "negative-proposal-strategist.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["negative", "match_type", "scope", "reason", "terms_blocked_hist", "cost_all", "cost_30d", "keep_terms_hit", "guard"])
    for row, probs in ok_rows + bad_rows:
        w.writerow(list(row) + ["; ".join(probs) or "ok"])
