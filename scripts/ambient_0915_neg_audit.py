#!/usr/bin/env python3
"""Ambient | 2026-09-15 | negative-keyword reachability audit. READ-ONLY.

Two-stage reachability, per the standing rule that a negative only costs money if the
query it blocks could actually have matched a positive keyword:

  stage 1  does the negative block a live positive keyword, a historical search term,
           or a historically CONVERTING search term?
  stage 2  is that blocked query reachable at all - i.e. could it have matched one of
           this campaign's live positive keywords under PHRASE/EXACT close-variant rules?

A negative that blocks nothing reachable is DUPLICATE_NO_EFFECT, not a problem.
Nothing is removed. Removal expands traffic and needs its own destructive approval.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
from collections import defaultdict, Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-15"
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "read_only": True}
c = client(); identity_gate(c, verbose=False)

# Terms agency policy says must never be auto-negatived.
PROTECTED = {"near", "me", "quote", "estimate", "price", "pricing", "cost", "best",
             "hire", "local", "emergency", "company", "companies", "contractor",
             "contractors", "licensed", "certified", "service", "services", "repair",
             "install", "installation", "replace", "replacement", "hvac", "ac",
             "air", "heating", "cooling", "furnace", "boiler", "commercial"}
# Equipment / capability words worth flagging if blocked.
CAPABILITY = {"rooftop", "roof", "industrial", "hydronics", "hydronic", "combustion",
              "ductless", "ductwork", "duct", "heat", "pump", "thermostat", "mini",
              "split", "condenser", "compressor", "coil", "refrigerant", "boiler",
              "radiant", "zoning", "ventilation"}


def toks(s):
    return re.findall(r"[a-z0-9']+", str(s).lower())


def tokset(s):
    return set(toks(s))


def blocks(neg_text, neg_match, query):
    """Does this negative block this query?

    GUARD: a negative whose text has no ASCII alphanumeric token (Korean, Chinese,
    emoji, pure punctuation) tokenises to []. An empty set is a subset of EVERY set,
    so a naive BROAD test would report it as blocking all traffic. It does not - the
    tokeniser simply cannot represent it. Return False and count it separately.
    """
    nt, qt = toks(neg_text), toks(query)
    if not nt:
        return False
    if neg_match == "BROAD":
        return set(nt) <= set(qt)
    if neg_match == "PHRASE":
        n = len(nt)
        return any(qt[i:i + n] == nt for i in range(len(qt) - n + 1))
    return qt == nt  # EXACT


def matches_positive(query, pos_text, pos_match):
    """Could this query have matched this positive keyword? (ignoring close variants)"""
    qt, pt = toks(query), toks(pos_text)
    if pos_match == "EXACT":
        return qt == pt
    n = len(pt)                      # PHRASE: contiguous, in order
    return any(qt[i:i + n] == pt for i in range(len(qt) - n + 1))


def reachable_conflict(neg, positives):
    """Stage 2. Build candidate queries that WOULD match a live positive, then ask
    whether this negative blocks one. A negative that blocks only unreachable queries
    costs nothing."""
    nt = toks(neg["text"])
    if not nt:
        return None
    for p_ in positives:
        for cand in (f"{p_['text']} {neg['text']}", f"{neg['text']} {p_['text']}"):
            if matches_positive(cand, p_["text"], p_["match"]) and \
                    blocks(neg["text"], neg["match"], cand):
                return {"candidate_query": cand, "positive": p_["text"],
                        "positive_match": p_["match"],
                        "campaign_id": p_["campaign_id"]}
    return None


print("=== 1. GATHER EVERY NEGATIVE THAT CAN AFFECT THE FIVE CAMPAIGNS ===")
camp_negs = []
for r in q(c, f"""SELECT campaign.id, campaign.name, campaign_criterion.criterion_id,
                         campaign_criterion.keyword.text,
                         campaign_criterion.keyword.match_type,
                         campaign_criterion.status
                  FROM campaign_criterion WHERE campaign.id IN ({IN5})
                    AND campaign_criterion.negative = TRUE
                    AND campaign_criterion.type = KEYWORD"""):
    cc = r.campaign_criterion
    camp_negs.append({"level": "CAMPAIGN", "campaign_id": str(r.campaign.id),
                      "campaign_name": r.campaign.name, "criterion_id": str(cc.criterion_id),
                      "text": cc.keyword.text, "match": E(cc.keyword.match_type),
                      "status": E(cc.status)})
ag_negs = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name,
                         ad_group_criterion.criterion_id,
                         ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type,
                         ad_group_criterion.status
                  FROM ad_group_criterion WHERE campaign.id IN ({IN5})
                    AND ad_group_criterion.negative = TRUE"""):
    a = r.ad_group_criterion
    ag_negs.append({"level": "AD_GROUP", "campaign_id": str(r.campaign.id),
                    "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
                    "criterion_id": str(a.criterion_id), "text": a.keyword.text,
                    "match": E(a.keyword.match_type), "status": E(a.status)})
# Account-level negative keywords do NOT live on customer_negative_criterion (that
# resource carries placement / content-label exclusions and has no keyword field).
# They live in a shared set whose type is ACCOUNT_LEVEL_NEGATIVE_KEYWORDS, which never
# appears in campaign_shared_set and reports member_count 0 - but applies account-wide.
ACCT_SET_TYPE = "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"
set_types = {str(r.shared_set.id): (E(r.shared_set.type), r.shared_set.name,
                                    E(r.shared_set.status))
             for r in q(c, """SELECT shared_set.id, shared_set.name, shared_set.type,
                                     shared_set.status FROM shared_set""")}
acct_set_ids = {sid for sid, (t, _, _) in set_types.items() if t == ACCT_SET_TYPE}
print(f"  ACCOUNT_LEVEL_NEGATIVE_KEYWORDS sets: {sorted(acct_set_ids)}")

attached = {r.campaign_shared_set.shared_set.split("/")[-1]
            for r in q(c, f"""SELECT campaign.id, campaign_shared_set.shared_set,
                                     campaign_shared_set.status
                              FROM campaign_shared_set WHERE campaign.id IN ({IN5})""")}
acct_negs, shared_negs = [], []
for r in q(c, """SELECT shared_set.id, shared_set.name, shared_criterion.criterion_id,
                        shared_criterion.keyword.text, shared_criterion.keyword.match_type
                 FROM shared_criterion WHERE shared_criterion.type = KEYWORD"""):
    sid = str(r.shared_set.id)
    row = {"shared_set_id": sid, "shared_set_name": r.shared_set.name,
           "criterion_id": f"{sid}~{r.shared_criterion.criterion_id}",
           "text": r.shared_criterion.keyword.text,
           "match": E(r.shared_criterion.keyword.match_type), "status": "ENABLED"}
    if sid in acct_set_ids:
        row["level"] = "ACCOUNT"
        acct_negs.append(row)
    else:
        row["level"] = "SHARED_SET"
        row["attached_to_the_five"] = sid in attached
        shared_negs.append(row)
print(f"  campaign-level   : {len(camp_negs)}")
print(f"  ad-group-level   : {len(ag_negs)}")
print(f"  account-level    : {len(acct_negs)}")
print(f"  shared-set rows  : {len(shared_negs)}  "
      f"(attached to the five: {sum(1 for x in shared_negs if x['attached_to_the_five'])})")
out["counts"] = {"campaign": len(camp_negs), "ad_group": len(ag_negs),
                 "account": len(acct_negs), "shared_set_rows": len(shared_negs),
                 "shared_sets_attached_to_the_five": len(attached)}

print("\n=== 2. LIVE POSITIVES + HISTORICAL SEARCH TERMS ===")
pos = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.status,
                         ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type,
                         ad_group_criterion.status
                  FROM ad_group_criterion WHERE campaign.id IN ({IN5})
                    AND ad_group_criterion.type = KEYWORD
                    AND ad_group_criterion.negative = FALSE"""):
    if E(r.ad_group.status) == "REMOVED" or E(r.ad_group_criterion.status) != "ENABLED":
        continue
    pos.append({"campaign_id": str(r.campaign.id), "ad_group_id": str(r.ad_group.id),
                "text": r.ad_group_criterion.keyword.text,
                "match": E(r.ad_group_criterion.keyword.match_type)})
print(f"  live ENABLED positives in non-REMOVED ad groups: {len(pos)}")
for p_ in pos:
    print(f"    {p_['campaign_id']} {p_['match']:6s} {p_['text']}")

terms = {}
for r in q(c, f"""SELECT campaign.id, search_term_view.search_term,
                         metrics.impressions, metrics.clicks, metrics.cost_micros,
                         metrics.conversions
                  FROM search_term_view WHERE campaign.id IN ({IN5})
                    AND segments.date BETWEEN '2026-08-01' AND '2026-09-14'"""):
    t = r.search_term_view.search_term
    d = terms.setdefault(t, {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0,
                             "campaigns": set(), "conv_by_campaign": defaultdict(float)})
    d["impr"] += r.metrics.impressions; d["clicks"] += r.metrics.clicks
    d["cost"] += r.metrics.cost_micros / 1e6; d["conv"] += r.metrics.conversions
    d["campaigns"].add(str(r.campaign.id))
    d["conv_by_campaign"][str(r.campaign.id)] += r.metrics.conversions
converting = {t: d for t, d in terms.items() if d["conv"] > 0}
print(f"  historical search terms: {len(terms)}  of which CONVERTING: {len(converting)}")
out["historical_terms"] = len(terms)
out["converting_terms"] = sorted(converting)

print("\n=== 3. STAGE 1 - does any negative block a live positive or a real query? ===")
active = ([n for n in camp_negs if n["status"] == "ENABLED"]
          + [n for n in ag_negs if n["status"] == "ENABLED"]
          + acct_negs
          + [n for n in shared_negs if n["attached_to_the_five"]])
print(f"  ACTIVE negatives in scope: {len(active)}")
inert_shared = [n for n in shared_negs if not n["attached_to_the_five"]]
print(f"  INERT shared-set rows (no set attached to the five): {len(inert_shared)}"
      f"  -> DUPLICATE_NO_EFFECT")

hits_pos, hits_term, hits_conv, hits_reach, non_latin = [], [], [], [], []
for n in active:
    if not toks(n["text"]):
        non_latin.append(n)
        continue
    # scope the positives and the terms this negative can actually affect
    if n["level"] == "CAMPAIGN":
        scope = [p_ for p_ in pos if p_["campaign_id"] == n["campaign_id"]]
        tscope = {t: d for t, d in terms.items() if n["campaign_id"] in d["campaigns"]}
        conv_key = n["campaign_id"]          # conversions must be IN this campaign
    elif n["level"] == "AD_GROUP":
        scope = [p_ for p_ in pos if p_["ad_group_id"] == n.get("ad_group_id")]
        tscope = {t: d for t, d in terms.items() if n["campaign_id"] in d["campaigns"]}
        conv_key = n["campaign_id"]
    else:
        scope, tscope, conv_key = pos, terms, None
    for p_ in scope:
        if blocks(n["text"], n["match"], p_["text"]):
            hits_pos.append({"negative": n, "positive": p_})
    rc = reachable_conflict(n, scope)
    if rc:
        hits_reach.append({"negative": n, **rc})
    for t, d in tscope.items():
        if blocks(n["text"], n["match"], t):
            # a conversion only counts against THIS negative if it happened in the
            # campaign the negative governs - otherwise the negative is doing correct
            # cross-campaign routing, not destroying demand
            conv_here = (d["conv"] if conv_key is None
                         else d["conv_by_campaign"].get(conv_key, 0.0))
            rec = {"negative_text": n["text"], "negative_match": n["match"],
                   "negative_level": n["level"],
                   "negative_campaign": n.get("campaign_name"),
                   "criterion_id": n["criterion_id"], "term": t,
                   "impressions": d["impr"], "clicks": d["clicks"],
                   "cost": round(d["cost"], 2),
                   "conversions_total": round(d["conv"], 2),
                   "conversions_in_this_scope": round(conv_here, 2)}
            hits_term.append(rec)
            if conv_here > 0:
                hits_conv.append(rec)
print(f"  negatives with NO evaluable ASCII token (non-Latin / punctuation): "
      f"{len(non_latin)} -> NON_LATIN_UNEVALUATED, not counted as blocking")
for n in non_latin[:10]:
    print(f"    {n['level']} {n['match']} {n['text']!r} crit={n['criterion_id']}")
print(f"  negatives with a STAGE-2 REACHABLE conflict: {len(hits_reach)}")
for h in hits_reach[:25]:
    print(f"    !! {h['negative']['level']} {h['negative']['match']} "
          f"'{h['negative']['text']}' would block reachable query "
          f"'{h['candidate_query']}' (positive '{h['positive']}')")
print(f"\n  negatives blocking a LIVE POSITIVE KEYWORD : {len(hits_pos)}")
for h in hits_pos[:20]:
    print(f"    !! {h['negative']['level']} {h['negative']['match']} "
          f"'{h['negative']['text']}' blocks positive '{h['positive']['text']}'")
print(f"  negatives blocking a HISTORICAL SEARCH TERM: {len(hits_term)}")
print(f"  negatives blocking a CONVERTING SEARCH TERM: {len(hits_conv)}")
for h in hits_conv:
    print(f"    !! {h['negative_level']} {h['negative_match']} '{h['negative_text']}' "
          f"blocks CONVERTING '{h['term']}' (conv={h['conversions']}, ${h['cost']})")
out["blocks_live_positive"] = [
    {"negative": h["negative"]["text"], "match": h["negative"]["match"],
     "level": h["negative"]["level"], "criterion_id": h["negative"]["criterion_id"],
     "positive": h["positive"]["text"]} for h in hits_pos]
out["blocks_historical_term"] = hits_term
out["blocks_converting_term"] = hits_conv
out["stage2_reachable_conflicts"] = [
    {"text": h["negative"]["text"], "match": h["negative"]["match"],
     "level": h["negative"]["level"], "criterion_id": h["negative"]["criterion_id"],
     "campaign": h["negative"].get("campaign_name"),
     "candidate_query": h["candidate_query"], "positive": h["positive"]}
    for h in hits_reach]
out["non_latin_unevaluated"] = [
    {"text": n["text"], "match": n["match"], "level": n["level"],
     "criterion_id": n["criterion_id"]} for n in non_latin]

print("\n=== 4. RISK SCAN - protected words and capability words used as negatives ===")
prot_hits, cap_hits, single = [], [], []
for n in active:
    tl = n["text"].lower().strip()
    tk = tokset(tl)
    if len(tk) == 1:
        single.append(n)
    if tl in PROTECTED:
        prot_hits.append(n)
    if tk & CAPABILITY and len(tk) <= 2:
        cap_hits.append(n)
print(f"  single-word ACTIVE negatives      : {len(single)}")
print(f"  ACTIVE negatives that are a PROTECTED agency term exactly: {len(prot_hits)}")
for n in prot_hits[:25]:
    print(f"    !! {n['level']} {n['match']} '{n['text']}' ({n.get('campaign_name','')[:34]})")
print(f"  ACTIVE short negatives touching a CAPABILITY word: {len(cap_hits)}")
for n in cap_hits[:30]:
    print(f"    ?  {n['level']} {n['match']} '{n['text']}' ({n.get('campaign_name','')[:34]})")
out["protected_word_negatives"] = [
    {"text": n["text"], "match": n["match"], "level": n["level"],
     "criterion_id": n["criterion_id"], "campaign": n.get("campaign_name")}
    for n in prot_hits]
out["capability_word_negatives"] = [
    {"text": n["text"], "match": n["match"], "level": n["level"],
     "criterion_id": n["criterion_id"], "campaign": n.get("campaign_name")}
    for n in cap_hits]
out["single_word_active_negatives"] = len(single)

print("\n=== 5. DUPLICATES ACROSS LEVELS ===")
by_text = defaultdict(list)
for n in active:
    by_text[(n["text"].lower(), n["match"])].append(n["level"])
dups = {k: v for k, v in by_text.items() if len(v) > 1}
print(f"  same (text, match) present at more than one active level: {len(dups)}")
out["cross_level_duplicates"] = len(dups)

print("\n=== 6. VERDICT TABLE ===")
verdicts = Counter()
rows = []
blocked_conv_ids = {h["criterion_id"] for h in hits_conv}
blocked_term_ids = {h["criterion_id"] for h in hits_term}
blocked_pos_ids = {h["negative"]["criterion_id"] for h in hits_pos}
reach_ids = {h["negative"]["criterion_id"] for h in hits_reach}
reach_by_id = {h["negative"]["criterion_id"]: h for h in hits_reach}
prot_ids = {n["criterion_id"] for n in prot_hits}
cap_ids = {n["criterion_id"] for n in cap_hits}
for n in active:
    cid = n["criterion_id"]
    if cid in blocked_pos_ids:
        v, why = "REMOVE", "blocks a LIVE positive keyword"
    elif cid in blocked_conv_ids:
        v, why = "REMOVE", "blocks a historically CONVERTING search term"
    elif cid in prot_ids:
        v, why = "NARROW", "is an agency-protected term that must not be a blanket negative"
    elif cid in reach_ids:
        v, why = ("NARROW", "STAGE-2 REACHABLE: blocks a query that could match a live "
                            "positive -> " + reach_by_id[cid]["candidate_query"])
    elif cid in cap_ids:
        v, why = "HOLD", "touches a serviced equipment/capability word - verify capability"
    elif cid in blocked_term_ids:
        v, why = "KEEP", "blocks a real historical query that did not convert"
    else:
        v, why = "KEEP", "blocks nothing reachable in the measured window"
    verdicts[v] += 1
    rows.append({"criterion_id": cid, "text": n["text"], "match": n["match"],
                 "level": n["level"], "campaign": n.get("campaign_name"),
                 "ad_group": n.get("ad_group_name"), "verdict": v, "reason": why})
for n in inert_shared:
    verdicts["DUPLICATE_NO_EFFECT"] += 1
for n in non_latin:
    verdicts["NON_LATIN_UNEVALUATED"] += 1
    rows.append({"criterion_id": n["criterion_id"], "text": n["text"],
                 "match": n["match"], "level": n["level"],
                 "campaign": n.get("campaign_name"), "ad_group": n.get("ad_group_name"),
                 "verdict": "NON_LATIN_UNEVALUATED",
                 "reason": "no ASCII token; this tokeniser cannot evaluate it. Review by hand."})
print(f"  {dict(verdicts)}")
out["verdicts"] = dict(verdicts)
out["verdict_rows_non_keep"] = [r for r in rows if r["verdict"] != "KEEP"]
print(f"\n  non-KEEP rows: {len(out['verdict_rows_non_keep'])}")
for r in out["verdict_rows_non_keep"][:40]:
    print(f"    {r['verdict']:20s} {r['level']:10s} {r['match']:6s} '{r['text']}' - {r['reason']}")

p = SNAP / f"negative-reachability-audit-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print("\nNo negative was removed. Removal expands traffic and needs APPROVE DESTRUCTIVE.")
