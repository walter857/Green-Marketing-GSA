#!/usr/bin/env python3
"""Local red-team of the Softwind Landscape & Masonry negative bundle.

No API calls. Everything is checked against the pulled corpus, the verdict table
and the agency policy rules in CLAUDE.md.
"""
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

# CLAUDE.md: these need an intent check and must never be auto-negatived.
PROTECTED = ["near me", "near you", "quote", "price", "pricing", "cost",
             "best", "hire", "local", "emergency"]
# broad-name-negative-guards: manufacturers are demand, never competitors.
MANUFACTURERS = ["nicolock", "belgard", "cambridge", "techo-bloc", "techo bloc",
                 "unilock", "ep henry", "nicolia"]
CEILING = 10000
LAYERS = ["NEG_CAMPAIGN_LEVEL", "NEG_NAME_BROAD", "NEG_CROSS_ACCOUNT_FENCE"]


def toks(s):
    return TOK.findall(s.lower())


def contiguous(sub, seq):
    n = len(sub)
    return bool(n) and n <= len(seq) and any(
        seq[i:i + n] == sub for i in range(len(seq) - n + 1))


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    fails = []

    negs = []  # (text, match_type, layer, campaign_id, campaign_name)
    for layer in LAYERS:
        for d in plan["subplans"][layer]["detail"]:
            for n in d["negatives"]:
                negs.append((n["text"], n["match_type"], layer,
                             d["campaign_id"], d["campaign_name"]))
    print("total objects across executable layers: {}".format(len(negs)))

    # 1 identity
    t = plan["target"]
    print("\n[1] identity")
    ok = (t["exact_child_account_name"] == "Softwind Landscape & Masonry - Live"
          and t["child_customer_id"] == "2429758629"
          and corpus["account_name"] == t["exact_child_account_name"]
          and corpus["customer_id"] == t["child_customer_id"])
    print("    bundle {} / {}".format(t["exact_child_account_name"],
                                      t["child_customer_id"]))
    print("    corpus {} / {}  -> {}".format(corpus["account_name"],
                                             corpus["customer_id"],
                                             "PASS" if ok else "FAIL"))
    if not ok:
        fails.append("identity mismatch")

    # 2 scope: only ENABLED campaigns, and only the work order's two
    print("\n[2] campaign scope")
    live = {c["id"]: c for c in corpus["campaigns"] if c["status"] == "ENABLED"}
    used = {(cid, cn) for _, _, _, cid, cn in negs}
    for cid, cn in sorted(used):
        state = "ENABLED" if cid in live else "NOT-ENABLED"
        print("    {:<14} {:<22} {}".format(cid, cn, state))
        if cid not in live:
            fails.append("targets non-enabled campaign " + cn)
    if {cn for _, cn in used} != {"Patio", "Pavers"}:
        fails.append("campaign set is not exactly Patio+Pavers")
    else:
        print("    exactly the work order's Patio + Pavers -> PASS")

    # 3 protected tokens never negatived standalone
    print("\n[3] policy-protected tokens (must not be auto-negatived)")
    hits = []
    for text, mt, layer, _, cn in negs:
        if " ".join(toks(text)) in PROTECTED:
            hits.append((text, mt, layer, cn))
    for text, mt, layer, cn in hits:
        print("    FAIL {!r} [{} {} {}]".format(text, mt, layer, cn))
        fails.append("protected token negatived: " + text)
    if not hits:
        print("    none negatived standalone -> PASS")

    # 4 manufacturers protected
    print("\n[4] paver manufacturers (demand, never negatives)")
    mh = [(text, layer) for text, _, layer, _, _ in negs
          if any(m in text.lower() for m in MANUFACTURERS)]
    for text, layer in mh:
        print("    FAIL {!r} in {}".format(text, layer))
        fails.append("manufacturer negatived: " + text)
    if not mh:
        print("    none present -> PASS")

    # 5 match types
    print("\n[5] match types by layer")
    bylayer = {}
    for text, mt, layer, _, _ in negs:
        bylayer.setdefault(layer, {})
        bylayer[layer][mt] = bylayer[layer].get(mt, 0) + 1
    for layer in LAYERS:
        print("    {:<26} {}".format(layer, bylayer.get(layer, {})))
    broad_outside = [x for x in bylayer
                     if "BROAD" in bylayer[x] and x != "NEG_NAME_BROAD"]
    if broad_outside:
        fails.append("BROAD outside the name layer: " + ",".join(broad_outside))
    else:
        print("    BROAD confined to NEG_NAME_BROAD -> PASS")

    # 6 nothing blocks a live positive keyword
    print("\n[6] blocks a live positive keyword?")
    live_ag = {a["id"] for a in corpus["ad_groups"]
               if a["status"] == "ENABLED" and a["campaign_id"] in live}
    pos = [(p["text"], toks(p["text"])) for p in corpus["positive_keywords"]
           if p["ad_group_id"] in live_ag and p["status"] == "ENABLED"]
    blocked = []
    for text, mt, layer, _, _ in negs:
        nt = toks(text)
        for ptext, pt in pos:
            if (pt == nt) if mt == "EXACT" else contiguous(nt, pt):
                blocked.append((text, mt, layer, ptext))
    for b in blocked[:20]:
        print("    FAIL {!r} [{} {}] blocks live keyword {!r}".format(*b))
    if blocked:
        fails.append("{} negatives block a live keyword".format(len(blocked)))
    else:
        print("    {} live positive keywords, none blocked -> PASS".format(len(pos)))

    # 7 nothing blocks a KEEP or converting search term
    print("\n[7] blocks a KEEP / converting search term?")
    keep = []
    with VERD.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["verdict"] == "KEEP" or float(r["conversions"]) > 0:
                keep.append((r["search_term"], toks(r["search_term"]),
                             float(r["conversions"])))
    bad = []
    for text, mt, layer, _, _ in negs:
        nt = toks(text)
        for kt, ktk, cv in keep:
            if (ktk == nt) if mt == "EXACT" else contiguous(nt, ktk):
                bad.append((text, mt, layer, kt, cv))
    for b in bad[:20]:
        print("    FAIL {!r} [{} {}] blocks KEEP {!r} (conv {})".format(*b))
    if bad:
        fails.append("{} negatives block a KEEP/converting term".format(len(bad)))
    else:
        print("    {} KEEP/converting terms, none blocked -> PASS".format(len(keep)))

    # 8 per-campaign ceiling
    print("\n[8] per-campaign negative ceiling ({})".format(CEILING))
    cur = {}
    for n in corpus["campaign_negatives"]:
        cur[n["campaign_id"]] = cur.get(n["campaign_id"], 0) + 1
    add = {}
    for _, _, _, cid, _ in negs:
        add[cid] = add.get(cid, 0) + 1
    for cid in sorted(add):
        before, plus = cur.get(cid, 0), add[cid]
        after = before + plus
        flag = "OK" if after < CEILING else "OVER CEILING"
        print("    {:<14} {:<10} {:>5} + {:>4} = {:>5}   {}".format(
            cid, live[cid]["name"], before, plus, after, flag))
        if after >= CEILING:
            fails.append("ceiling exceeded on " + live[cid]["name"])

    # 9 duplicates within a campaign
    print("\n[9] duplicates within a campaign")
    seen, dups = set(), []
    for text, mt, layer, cid, _ in negs:
        k = (cid, " ".join(toks(text)), mt)
        if k in seen:
            dups.append(k)
        seen.add(k)
    print("    {} -> {}".format(len(dups), "PASS" if not dups else "FAIL"))
    if dups:
        fails.append("{} duplicate negatives".format(len(dups)))

    # 10 name layer contents
    print("\n[10] NEG_NAME_BROAD contents")
    names = sorted({text for text, _, layer, _, _ in negs
                    if layer == "NEG_NAME_BROAD"})
    print("    {} distinct tokens:".format(len(names)))
    for i in range(0, len(names), 6):
        print("      " + "  ".join("{:<14}".format(n) for n in names[i:i + 6]))

    print("\n" + "=" * 70)
    print("RED TEAM: {} failure(s)".format(len(fails)))
    for f in fails:
        print("   FAIL " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
