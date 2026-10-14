#!/usr/bin/env python3
"""Ambient | 2026-09-20 | Host-scoped negative conflict test for the expansion keywords.

READ-ONLY. EXTERNAL WRITES: 0.

The 2026-09-18 conflict pass listed every negative anywhere in the account that
matched a proposed keyword. Most of those hits sit on legacy PAUSED campaigns or
on campaigns the new ad groups will never live in, so they cannot block anything.
That is a false-alarm list, not a verdict.

This pass is host-scoped. For each new ad group it resolves the campaign that will
actually host it, then assembles ONLY the negatives that can reach a query in that
campaign:

  a. campaign-level negative criteria on the host campaign
  b. every shared negative list ATTACHED to the host campaign
  c. account-level negative keywords, which apply everywhere and never appear in
     campaign_shared_set (they report member_count 0, so the members are read
     from the shared set directly)
  d. ad-group negatives already on the host ad group, where it already exists
  e. the cross-negatives this very plan proposes for that ad group

Negative match semantics, per Google Ads:
  BROAD negative  - blocks when every token of the negative appears in the query,
                    any order, no close variants
  PHRASE negative - blocks when the negative's tokens appear contiguously, in order
  EXACT negative  - blocks only on an exact whole-query match

Two separate verdicts are produced:
  SELF-BLOCK  - a negative that would stop the ad group's own keyword. Launch-fatal.
  MISROUTE    - a cross-negative that correctly diverts a query to the ad group
                that owns that service. Intended, and reported as such.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21"
PLAN = "AMB-0921-HEAT-EXPAND-1"

# Which campaign will host each new ad group. Taken from the plan, re-stated here
# so the test cannot silently inherit an error from the plan it is checking.
HOST = {
    "SKAG | Boiler Repair": "24132507744",                    # Gas Boiler Repair campaign
    "SKAG | Oil Furnace Installation": "24257819466",         # Heating Installation
    "SKAG | Oil Heating System Replacement": "24257819466",   # Heating Installation
    "SKAG | Heat Pump Installation": "NEW:HEATPUMP",          # new Heat Pump & Geothermal
    "SKAG | Geothermal HVAC Installation": "NEW:HEATPUMP",
    "SKAG | Tankless Water Heater Installation": "NEW:TANKLESS",
}
# Ad groups that already exist and only receive cross-negatives.
EXISTING = {
    "SKAG | Furnace Repair": ("24257819463", "199797580706"),
    "SKAG | Mini Split Installation": ("24257819466", "199797580746"),
    "SKAG | Gas Boiler Repair": ("24132507744", "202339087594"),
}
TOK = re.compile(r"[a-z0-9']+")


def toks(s: str):
    return TOK.findall(s.lower())


def blocks(neg_text: str, neg_match: str, query: str) -> bool:
    q, n = toks(query), toks(neg_text)
    if not n:
        return False
    if neg_match == "EXACT":
        return q == n
    if neg_match == "PHRASE":
        return any(q[i:i + len(n)] == n for i in range(len(q) - len(n) + 1))
    return all(t in q for t in n)          # BROAD


def main():
    c = client()
    identity_gate(c, verbose=False)
    plan = json.loads((PLANS / f"{PLAN}.json").read_text(encoding="utf-8"))
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0, "plan": PLAN}

    # ---------------------------------------------- a. campaign-level negatives
    camp_neg = {}
    for r in q(c, """SELECT campaign.id, campaign.name,
                     campaign_criterion.keyword.text,
                     campaign_criterion.keyword.match_type,
                     campaign_criterion.negative, campaign_criterion.type
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = 'KEYWORD'
                       AND campaign_criterion.negative = TRUE
                       AND campaign.status != 'REMOVED'"""):
        camp_neg.setdefault(str(r.campaign.id), []).append(
            (r.campaign_criterion.keyword.text,
             E(r.campaign_criterion.keyword.match_type)))
    print("=== campaign-level negatives ===")
    for cid in ("24132507744", "24257819463", "24257819466"):
        print(f"   campaign {cid}: {len(camp_neg.get(cid, []))} negatives")

    # ------------------------------------- b. shared sets attached per campaign
    attach = {}
    for r in q(c, """SELECT campaign.id, campaign.name, shared_set.id, shared_set.name,
                     shared_set.type, campaign_shared_set.status
                     FROM campaign_shared_set
                     WHERE campaign_shared_set.status = 'ENABLED'"""):
        attach.setdefault(str(r.campaign.id), []).append(
            (str(r.shared_set.id), r.shared_set.name, E(r.shared_set.type_)))

    # all shared sets, incl. the account-level ones that never show in the above
    sets = {}
    for r in q(c, """SELECT shared_set.id, shared_set.name, shared_set.type,
                     shared_set.status, shared_set.member_count
                     FROM shared_set WHERE shared_set.status != 'REMOVED'"""):
        sets[str(r.shared_set.id)] = {"name": r.shared_set.name,
                                      "type": E(r.shared_set.type_),
                                      "member_count": r.shared_set.member_count}
    members = {}
    for r in q(c, """SELECT shared_set.id, shared_criterion.keyword.text,
                     shared_criterion.keyword.match_type, shared_criterion.type
                     FROM shared_criterion
                     WHERE shared_criterion.type = 'KEYWORD'"""):
        members.setdefault(str(r.shared_set.id), []).append(
            (r.shared_criterion.keyword.text, E(r.shared_criterion.keyword.match_type)))
    print("\n=== shared sets ===")
    acct_level = []
    for sid, s in sets.items():
        n = len(members.get(sid, []))
        where = [cid for cid, lst in attach.items() if any(x[0] == sid for x in lst)]
        if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS":
            acct_level.append(sid)
        print(f"   {sid} {s['type']:34s} reported={s['member_count']:5d} "
              f"read={n:5d} attached_to={len(where)} campaigns  {s['name'][:36]}")
    out["shared_sets"] = {sid: {**s, "members_read": len(members.get(sid, []))}
                          for sid, s in sets.items()}
    out["account_level_set_ids"] = acct_level

    def negatives_reaching(cid: str, ag_id: str | None):
        """Every negative that can suppress a query inside this campaign/ad group."""
        got = []
        for t, m in camp_neg.get(cid, []):
            got.append((f"campaign:{cid}", t, m))
        for sid, nm, ty in attach.get(cid, []):
            for t, m in members.get(sid, []):
                got.append((f"sharedset:{sid}:{nm[:24]}", t, m))
        for sid in acct_level:
            for t, m in members.get(sid, []):
                got.append((f"account-level:{sid}", t, m))
        if ag_id:
            for t, m in ag_neg.get(ag_id, []):
                got.append((f"adgroup:{ag_id}", t, m))
        return got

    # ------------------------------------------------- d. ad-group negatives
    ag_neg = {}
    for r in q(c, """SELECT ad_group.id, ad_group.name,
                     ad_group_criterion.keyword.text,
                     ad_group_criterion.keyword.match_type
                     FROM ad_group_criterion
                     WHERE ad_group_criterion.type = 'KEYWORD'
                       AND ad_group_criterion.negative = TRUE
                       AND ad_group_criterion.status != 'REMOVED'"""):
        ag_neg.setdefault(str(r.ad_group.id), []).append(
            (r.ad_group_criterion.keyword.text,
             E(r.ad_group_criterion.keyword.match_type)))

    # ------------------------------------------------------ THE TEST: new groups
    print("\n=== SELF-BLOCK TEST: does anything stop a NEW keyword in its OWN home? ===")
    verdict = {}
    fatal = 0
    for ag, d in plan["new_ad_groups"].items():
        cid = HOST[ag]
        kws = [(t, "PHRASE") for t in d["phrase"]] + [(t, "EXACT") for t in d["exact"]]
        # A brand-new campaign starts with no campaign negatives and no shared sets,
        # so only the account-level negatives and this plan's own cross-negatives reach it.
        existing = ([] if cid.startswith("NEW:")
                    else negatives_reaching(cid, None))
        if cid.startswith("NEW:"):
            for sid in acct_level:
                for t, m in members.get(sid, []):
                    existing.append((f"account-level:{sid}", t, m))
        own_cross = [(f"THIS PLAN:{ag}", t, "PHRASE")
                     for t in plan["cross_negatives"][ag]["negatives"]]
        hits_existing, hits_cross = [], []
        for kt, km in kws:
            for src, nt, nm in existing:
                if blocks(nt, nm, kt):
                    hits_existing.append({"keyword": kt, "kw_match": km,
                                          "negative": nt, "neg_match": nm, "source": src})
            for src, nt, nm in own_cross:
                if blocks(nt, nm, kt):
                    hits_cross.append({"keyword": kt, "kw_match": km,
                                       "negative": nt, "neg_match": nm, "source": src})
        verdict[ag] = {"host_campaign": cid, "keywords": len(kws),
                       "negatives_reaching_host": len(existing),
                       "blocked_by_existing": hits_existing,
                       "blocked_by_own_cross_negatives": hits_cross,
                       "SELF_BLOCK": bool(hits_existing or hits_cross)}
        fatal += len(hits_existing) + len(hits_cross)
        st = "FAIL" if verdict[ag]["SELF_BLOCK"] else "PASS"
        print(f"   {ag[:44]:44s} host={cid:16s} kws={len(kws):2d} "
              f"reaching={len(existing):5d}  {st}")
        for h in hits_existing + hits_cross:
            print(f"        BLOCKED '{h['keyword']}' by {h['neg_match']} "
                  f"'{h['negative']}' from {h['source']}")
    out["new_ad_group_selfblock"] = verdict

    # ------------------------------- existing ad groups vs their NEW cross-negs
    print("\n=== SELF-BLOCK TEST: new cross-negatives vs EXISTING ad-group keywords ===")
    ex_v = {}
    for ag, (cid, agid) in EXISTING.items():
        kws = []
        for r in q(c, f"""SELECT ad_group_criterion.keyword.text,
                          ad_group_criterion.keyword.match_type
                          FROM ad_group_criterion
                          WHERE ad_group.id = {agid}
                            AND ad_group_criterion.type = 'KEYWORD'
                            AND ad_group_criterion.negative = FALSE
                            AND ad_group_criterion.status != 'REMOVED'"""):
            kws.append((r.ad_group_criterion.keyword.text,
                        E(r.ad_group_criterion.keyword.match_type)))
        negs = plan["cross_negatives"][ag]["negatives"]
        hits = [{"keyword": kt, "negative": nt}
                for kt, km in kws for nt in negs if blocks(nt, "PHRASE", kt)]
        ex_v[ag] = {"ad_group_id": agid, "campaign_id": cid, "live_keywords": len(kws),
                    "new_cross_negatives": negs, "self_block_hits": hits,
                    "SELF_BLOCK": bool(hits)}
        print(f"   {ag[:44]:44s} ag={agid} kws={len(kws)} negs={len(negs)} "
              f"{'FAIL' if hits else 'PASS'}")
        for h in hits:
            print(f"        BLOCKED '{h['keyword']}' by PHRASE '{h['negative']}'")
        fatal += len(hits)
    out["existing_ad_group_selfblock"] = ex_v

    # ---------------------- converting heating queries vs the whole negative wall
    print("\n=== HISTORICALLY CONVERTING HEATING QUERIES vs new cross-negatives ===")
    terms = set()
    for r in q(c, """SELECT search_term_view.search_term, metrics.conversions
                     FROM search_term_view
                     WHERE segments.date BETWEEN '2024-01-01' AND '2026-09-19'
                       AND metrics.conversions > 0"""):
        terms.add(r.search_term_view.search_term.lower())
    heatwords = ("furnace", "boiler", "heat pump", "heatpump", "mini split", "minisplit",
                 "ductless", "geothermal", "tankless", "oil heat", "heating", "radiator",
                 "baseboard", "water heater")
    heat_terms = sorted(t for t in terms if any(w in t for w in heatwords))
    # Raw terms are never printed or retained - only counts and the routing verdict.
    routing = {}
    orphan = []
    for t in heat_terms:
        homes = []
        for ag, d in plan["new_ad_groups"].items():
            negs = plan["cross_negatives"][ag]["negatives"]
            if any(blocks(n, "PHRASE", t) for n in negs):
                continue
            if any(blocks(k, "PHRASE", t) for k in d["phrase"]) or t in d["exact"]:
                homes.append(ag)
        for ag, (cid, agid) in EXISTING.items():
            negs = plan["cross_negatives"][ag]["negatives"]
            if any(blocks(n, "PHRASE", t) for n in negs):
                continue
            homes.append(ag + " (existing)")
        routing[len(homes)] = routing.get(len(homes), 0) + 1
    out["converting_heating_queries"] = {
        "distinct_terms_tested": len(heat_terms),
        "window": "2024-01-01..2026-09-19",
        "raw_terms_retained": False,
        "eligible_ad_group_count_distribution": routing}
    print(f"   distinct converting heating queries tested: {len(heat_terms)}")
    print(f"   eligible-ad-group-count distribution: {routing}")
    print("   (raw search terms were never printed or written to disk)")

    out["FATAL_SELF_BLOCKS"] = fatal
    print(f"\n=== TOTAL FATAL SELF-BLOCKS: {fatal} ===")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"negative-reachability-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
