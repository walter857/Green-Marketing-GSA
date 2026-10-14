#!/usr/bin/env python3
"""2026-09-26 LOCAL: assemble the Master Grass negative-keyword DRAFT plan (not executable).

Layer A  strategist phrase negatives that passed every guard (mg_0926_neg_proposal.py)
Layer B  classifier output: EXACT negatives for out-of-scope queries with spend + SHARED-lexicon
         phrase roots (mg_0926_search_terms.py negative-candidates.csv, guard == ok)
Layer C  EXACT negatives for other-Master-Grass-service queries with spend that Layer A does not
         already block, and that cannot be phrase-blocked without hitting a live keyword.
Every row is re-guarded here per campaign. Prints counts only; raw terms stay in the CSV.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "mastergrass-lawn-care" / "snapshots" / "audit-2026-09-26"
ST = ROOT / "reports" / "mastergrass-lawn-care" / "st"
PLANS = ROOT / "clients" / "mastergrass-lawn-care" / "plans"
PLANS.mkdir(parents=True, exist_ok=True)
LIVE = {"23905193676": "Landscaping Search - BOFU", "23914692658": "Hardscaping Search - BOFU"}
BYNAME = {v: k for k, v in LIVE.items()}
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


kw = json.loads((SNAP / "keywords.json").read_text(encoding="utf-8"))
live_pos = {c: [toks(r["ad_group_criterion"]["keyword"]["text"]) for r in kw
                if r["campaign"]["id"] == c and not r["ad_group_criterion"].get("negative")
                and r["ad_group_criterion"].get("status") == "ENABLED"] for c in LIVE}
existing = {c: set() for c in LIVE}
for r in json.loads((SNAP / "campaign_criteria.json").read_text(encoding="utf-8")):
    cc = r["campaign_criterion"]
    if r["campaign"]["id"] in LIVE and cc.get("negative") and cc.get("keyword"):
        existing[r["campaign"]["id"]].add((cc["keyword"]["text"].lower().strip('"[] '), cc["keyword"]["match_type"]))
verd = list(csv.DictReader((ST / "verdicts.csv").open(encoding="utf-8")))
conv_t = [toks(r["term"]) for r in verd if float(r["conv_all"]) > 0]
keep_t = [toks(r["term"]) for r in verd if r["category"] == "IN_SCOPE_COMMERCIAL"]

ops = []  # (campaign_id, text, match, layer, reason)
for r in csv.DictReader((ST / "negative-proposal-strategist.csv").open(encoding="utf-8")):
    if r["guard"] != "ok":
        continue
    for c in ({"both": list(LIVE), "land": ["23905193676"], "hard": ["23914692658"]}[r["scope"]]):
        ops.append((c, r["negative"], r["match_type"], "A", r["reason"]))
for r in csv.DictReader((ST / "negative-candidates.csv").open(encoding="utf-8")):
    if r["guard"] != "ok":
        continue
    for c in LIVE:
        ops.append((c, r["negative"], r["match_type"], "B", r["category"]))
layer_a = [(c, toks(t), m) for c, t, m, L, _ in ops if L == "A"]
for r in verd:
    if r["category"] != "OTHER_MASTER_GRASS_SERVICE" or float(r["cost_all"]) <= 0:
        continue
    qt = toks(r["term"])
    for name in r["campaigns"].split("|"):
        c = BYNAME[name]
        if any(cc == c and blocks(nt, m, qt) for cc, nt, m in layer_a):
            continue
        ops.append((c, r["term"], "EXACT", "C", "other Master Grass service, not advertised here"))

final, rejected = [], Counter()
seen = set()
for c, text, mt, layer, reason in ops:
    key = (c, text, mt)
    if key in seen:
        rejected["duplicate_op"] += 1
        continue
    seen.add(key)
    nt = toks(text)
    if (text, mt) in existing[c]:
        rejected["already_live"] += 1
        continue
    if any(blocks(nt, mt, p) for p in live_pos[c]):
        rejected["blocks_live_keyword"] += 1
        continue
    if any(blocks(nt, mt, q) for q in conv_t):
        rejected["blocks_converting_term"] += 1
        continue
    if mt != "EXACT" and any(blocks(nt, mt, q) for q in keep_t):
        rejected["phrase_blocks_keep_term"] += 1
        continue
    final.append((c, LIVE[c], text, mt, layer, reason))

path = PLANS / "NEG-0926-DRAFT.csv"
with path.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["customer_id", "campaign_id", "campaign_name", "negative_text", "match_type", "layer", "reason", "level"])
    for row in sorted(final):
        w.writerow(["9487471092", *row[:6], "CAMPAIGN"])
digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12].upper()
by = Counter((r[1][:11], r[4], r[3]) for r in final)
print("DRAFT negative plan (campaign-level):")
for k, v in sorted(by.items()):
    print(f"  {k[0]:<12} layer {k[1]} {k[2]:<6} {v:>3}")
print(f"total objects {len(final)} | rejected {dict(rejected)} | file sha256[:12] {digest}")
print("wrote", path.relative_to(ROOT))
