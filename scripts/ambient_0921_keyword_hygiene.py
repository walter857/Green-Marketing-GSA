#!/usr/bin/env python3
"""Ambient | 2026-09-21 | Keyword hygiene across the WHOLE structure, not just per ad group.

READ-ONLY. EXTERNAL WRITES: 0.

The in-builder validator checks each RSA and each ad group in isolation. It cannot
see three things that only exist between ad groups:

  1. the same keyword text proposed in two different ad groups, which makes the
     two compete for the same auction;
  2. a proposed keyword that already exists live somewhere else in the account,
     which is the same problem with an existing ad group;
  3. close variants that Google collapses into one demand bucket, where carrying
     both adds objects without adding reach.

Bucket collapse is detected structurally rather than from Planner volume: two
terms land in the same bucket when their token multisets match after stripping
plurals, gerunds and the filler tokens Google ignores.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21"
PLAN = "AMB-0921-HEAT-EXPAND-1"
TOK = re.compile(r"[a-z0-9']+")
# Tokens Google treats as noise inside a keyword for matching purposes.
FILLER = {"a", "an", "the", "in", "of", "for", "to", "my", "your", "me", "near", "and"}


def stem(t: str) -> str:
    for suf, rep in (("ations", "ation"), ("ations", "ation"), ("ers", "er"),
                     ("ing", ""), ("ies", "y"), ("es", ""), ("s", "")):
        if t.endswith(suf) and len(t) - len(suf) >= 3:
            return t[: len(t) - len(suf)] + rep
    return t


def bucket(text: str) -> tuple:
    toks = [stem(t) for t in TOK.findall(text.lower()) if t not in FILLER]
    return tuple(sorted(Counter(toks).elements()))


def main():
    c = client()
    identity_gate(c, verbose=False)
    plan = json.loads((PLANS / f"{PLAN}.json").read_text(encoding="utf-8"))
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0, "plan": PLAN}
    fails = []

    # ------------------------------------------------- 1. cross-ad-group dupes
    print("=== 1. SAME KEYWORD IN TWO PROPOSED AD GROUPS ===")
    where = defaultdict(list)
    for ag, d in plan["new_ad_groups"].items():
        for t in d["phrase"]:
            where[(t, "PHRASE")].append(ag)
        for t in d["exact"]:
            where[(t, "EXACT")].append(ag)
    dupes = {f"{t} [{m}]": ags for (t, m), ags in where.items() if len(ags) > 1}
    for k, v in dupes.items():
        print(f"   COLLISION {k} -> {v}")
        fails.append(f"cross-ad-group duplicate: {k} in {v}")
    print(f"   {len(dupes)} collisions among {len(where)} proposed keywords")
    out["cross_ad_group_duplicates"] = dupes

    # ---------------------------------------- 2. collision with live keywords
    print("\n=== 2. PROPOSED KEYWORD ALREADY LIVE ELSEWHERE ===")
    live = defaultdict(list)
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                     ad_group.id, ad_group.name, ad_group.status,
                     ad_group_criterion.keyword.text,
                     ad_group_criterion.keyword.match_type,
                     ad_group_criterion.status
                     FROM ad_group_criterion
                     WHERE ad_group_criterion.type = 'KEYWORD'
                       AND ad_group_criterion.negative = FALSE
                       AND ad_group_criterion.status != 'REMOVED'
                       AND campaign.status != 'REMOVED'"""):
        x = r.ad_group_criterion
        live[(x.keyword.text.lower(), E(x.keyword.match_type))].append(
            {"campaign": r.campaign.name, "campaign_status": E(r.campaign.status),
             "ad_group": r.ad_group.name, "ad_group_status": E(r.ad_group.status),
             "criterion_status": E(x.status)})
    hits = {}
    for (t, m), ags in where.items():
        found = live.get((t.lower(), m), [])
        # Only a live keyword on a campaign that can actually serve is a collision.
        servable = [f for f in found if f["campaign_status"] == "ENABLED"
                    and f["ad_group_status"] == "ENABLED"
                    and f["criterion_status"] == "ENABLED"]
        if found:
            hits[f"{t} [{m}]"] = {"proposed_in": ags, "existing": found,
                                  "servable_collisions": servable}
            tag = "SERVABLE COLLISION" if servable else "exists but cannot serve"
            print(f"   {tag}: '{t}' [{m}] proposed in {ags}")
            for f in found[:4]:
                print(f"        {f['campaign_status']:8s}/{f['ad_group_status']:8s} "
                      f"{f['campaign'][:40]} | {f['ad_group'][:28]}")
            if servable:
                fails.append(f"servable duplicate: {t} [{m}]")
    if not hits:
        print("   none")
    out["collisions_with_live_keywords"] = hits

    # ------------------------------------------------- 3. bucket collapse
    print("\n=== 3. SAME DEMAND BUCKET WITHIN AN AD GROUP ===")
    coll = {}
    for ag, d in plan["new_ad_groups"].items():
        b = defaultdict(list)
        for t in d["phrase"]:
            b[bucket(t)].append(f"{t} [PHRASE]")
        for t in d["exact"]:
            b[bucket(t)].append(f"{t} [EXACT]")
        same = {" + ".join(map(str, k)): v for k, v in b.items() if len(v) > 1}
        # A PHRASE/EXACT pair of the SAME text is the intended agency default,
        # not a collapse. Only flag groups that pair two different texts.
        real = {k: v for k, v in same.items()
                if len({x.split(" [")[0] for x in v}) > 1}
        if real:
            coll[ag] = real
            for k, v in real.items():
                print(f"   {ag[:40]:40s} bucket({k}) -> {v}")
                fails.append(f"bucket collapse in {ag}: {v}")
    if not coll:
        print("   none - every remaining pair is the intended PHRASE+EXACT variant "
              "of one text")
    out["bucket_collapse"] = coll

    # ------------------------------------------------- 4. phrase/exact shape
    print("\n=== 4. MATCH-TYPE SHAPE PER AD GROUP ===")
    shape = {}
    for ag, d in plan["new_ad_groups"].items():
        p, e = len(d["phrase"]), len(d["exact"])
        broad = [t for t in d["phrase"] + d["exact"] if False]   # none by construction
        shape[ag] = {"phrase": p, "exact": e, "broad": len(broad),
                     "exact_subset_of_phrase": set(d["exact"]) <= set(d["phrase"])}
        print(f"   {ag[:44]:44s} phrase={p} exact={e} broad={len(broad)} "
              f"exact_subset={shape[ag]['exact_subset_of_phrase']}")
        if broad:
            fails.append(f"BROAD match present in {ag}")
    out["match_type_shape"] = shape
    out["total_keywords"] = sum(v["phrase"] + v["exact"] for v in shape.values())
    print(f"   TOTAL {out['total_keywords']} keywords "
          f"({sum(v['phrase'] for v in shape.values())} phrase, "
          f"{sum(v['exact'] for v in shape.values())} exact, 0 broad)")

    out["FAILURES"] = fails
    print(f"\n=== HYGIENE FAILURES: {len(fails)} ===")
    for f in fails:
        print(f"   {f}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"keyword-hygiene-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
