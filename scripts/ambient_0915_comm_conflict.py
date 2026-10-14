#!/usr/bin/env python3
"""Ambient | 2026-09-15 | do campaign 24132507747's negatives block real commercial demand?

Targeted, not synthetic. Tests REAL commercial buyer phrases against the live campaign
negative set, and only counts a conflict when the phrase could actually match one of the
two live commercial keywords. READ-ONLY.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-15"
CAMP, COMM_AG = "24132507747", "199748801029"
c = client(); identity_gate(c, verbose=False)
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "read_only": True}


def toks(s):
    return re.findall(r"[a-z0-9']+", str(s).lower())


def blocks(nt_text, nm, query):
    nt, qt = toks(nt_text), toks(query)
    if not nt:
        return False
    if nm == "BROAD":
        return set(nt) <= set(qt)
    if nm == "PHRASE":
        n = len(nt)
        return any(qt[i:i + n] == nt for i in range(len(qt) - n + 1))
    return qt == nt


def matches(query, pt_text, pm):
    qt, pt = toks(query), toks(pt_text)
    if pm == "EXACT":
        return qt == pt
    n = len(pt)
    return any(qt[i:i + n] == pt for i in range(len(qt) - n + 1))


POS = [("commercial hvac installation", "PHRASE"), ("commercial hvac installation", "EXACT")]

# Real commercial buyer phrases a Central Maryland business would actually type.
# Every one of these is a phrase the live landing page explicitly addresses.
BUYER = [
    "commercial hvac installation",
    "commercial hvac installation near me",
    "commercial hvac installation rooftop",
    "commercial hvac installation rooftop unit",
    "commercial hvac installation for my building",
    "commercial hvac installation ventilation",
    "commercial hvac installation ductwork",
    "commercial hvac installation cost",
    "commercial hvac installation quote",
    "commercial hvac installation company",
    "commercial hvac installation contractor",
    "commercial hvac installation companies near me",
    "commercial hvac installation maryland",
    "commercial hvac installation baltimore",
    "commercial hvac installation annapolis",
    "commercial hvac installation for restaurants",
    "commercial hvac installation for warehouse",
    "commercial hvac installation for office building",
    "commercial hvac installation for retail store",
    "commercial hvac installation for schools",
    "commercial hvac installation heat pump",
    "commercial hvac installation packaged unit",
    "commercial hvac installation central air",
    "commercial hvac installation replacement",
    "commercial hvac installation licensed",
    "commercial hvac installation certified",
    "commercial hvac installation industrial",
    "commercial hvac installation service",
    "commercial hvac installation estimate",
    "commercial hvac installation price",
    "licensed commercial hvac installation",
    "certified commercial hvac installation",
    "rooftop commercial hvac installation",
    "industrial commercial hvac installation",
    "best commercial hvac installation",
    "local commercial hvac installation",
    "emergency commercial hvac installation",
]

print("=== 1. NEGATIVES IN SCOPE FOR THE COMMERCIAL AD GROUP ===")
cneg = [{"level": "CAMPAIGN", "criterion_id": str(r.campaign_criterion.criterion_id),
         "text": r.campaign_criterion.keyword.text,
         "match": E(r.campaign_criterion.keyword.match_type)}
        for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id,
                                 campaign_criterion.keyword.text,
                                 campaign_criterion.keyword.match_type
                          FROM campaign_criterion WHERE campaign.id = {CAMP}
                            AND campaign_criterion.negative = TRUE
                            AND campaign_criterion.type = KEYWORD
                            AND campaign_criterion.status = ENABLED""")]
aneg = [{"level": "AD_GROUP", "criterion_id": str(r.ad_group_criterion.criterion_id),
         "text": r.ad_group_criterion.keyword.text,
         "match": E(r.ad_group_criterion.keyword.match_type)}
        for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id,
                                 ad_group_criterion.keyword.text,
                                 ad_group_criterion.keyword.match_type
                          FROM ad_group_criterion WHERE ad_group.id = {COMM_AG}
                            AND ad_group_criterion.negative = TRUE""")]
acct_sets = {str(r.shared_set.id) for r in q(c, """SELECT shared_set.id, shared_set.type
    FROM shared_set""") if E(r.shared_set.type) == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"}
accneg = [{"level": "ACCOUNT", "criterion_id": str(r.shared_criterion.criterion_id),
           "text": r.shared_criterion.keyword.text,
           "match": E(r.shared_criterion.keyword.match_type)}
          for r in q(c, """SELECT shared_set.id, shared_criterion.criterion_id,
                                  shared_criterion.keyword.text,
                                  shared_criterion.keyword.match_type
                           FROM shared_criterion WHERE shared_criterion.type = KEYWORD""")
          if str(r.shared_set.id) in acct_sets]
ALL = cneg + aneg + accneg
print(f"  campaign {len(cneg)} + ad group {len(aneg)} + account {len(accneg)} = {len(ALL)}")

print("\n=== 2. REAL COMMERCIAL BUYER PHRASES vs THE LIVE NEGATIVE SET ===")
conflicts, clean = [], []
for phrase in BUYER:
    reachable = any(matches(phrase, t, m) for t, m in POS)
    blockers = [n for n in ALL if blocks(n["text"], n["match"], phrase)]
    if not reachable:
        status = "NOT_REACHABLE (would not match either commercial keyword anyway)"
    elif blockers:
        status = "BLOCKED"
        conflicts.append({"phrase": phrase, "blockers": blockers})
    else:
        status = "OK"
        clean.append(phrase)
    flag = "!!" if status == "BLOCKED" else ("  " if status == "OK" else " ~")
    print(f"  {flag} {status:14s} {phrase}")
    for b in blockers[:4]:
        print(f"        blocked by {b['level']} {b['match']} '{b['text']}' "
              f"(crit {b['criterion_id']})")
out["buyer_phrases_tested"] = len(BUYER)
out["reachable_and_clean"] = clean
out["reachable_and_blocked"] = conflicts
print(f"\n  tested {len(BUYER)} | reachable+clean {len(clean)} | "
      f"reachable+BLOCKED {len(conflicts)}")

print("\n=== 3. VERDICT ===")
if conflicts:
    print("  The following campaign/account negatives block REAL, reachable commercial")
    print("  buyer demand for the new ad group. Each needs a decision:")
    seen = set()
    for cf in conflicts:
        for b in cf["blockers"]:
            k = (b["level"], b["match"], b["text"])
            if k in seen:
                continue
            seen.add(k)
            hits = [x["phrase"] for x in conflicts if any(
                bb["criterion_id"] == b["criterion_id"] for bb in x["blockers"])]
            print(f"    {b['level']:9s} {b['match']:6s} '{b['text']}' crit={b['criterion_id']} "
                  f"-> blocks {len(hits)} buyer phrase(s)")
            for h in hits[:4]:
                print(f"         {h}")
    out["negatives_needing_a_decision"] = [
        {"level": k[0], "match": k[1], "text": k[2]} for k in sorted(seen)]
else:
    print("  No live negative blocks any reachable commercial buyer phrase.")
    out["negatives_needing_a_decision"] = []

p = SNAP / f"commercial-negative-conflict-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print("\nNothing removed. Any removal needs APPROVE DESTRUCTIVE.")
