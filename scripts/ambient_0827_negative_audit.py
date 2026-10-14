#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | negative inventory and conflict audit.

Audits every negative that can affect the five live Search campaigns:
  * 3 campaign-level negatives on AC Repair (car, auto, boat)
  * 59 members of the ACCOUNT_LEVEL_NEGATIVE_KEYWORDS shared set 11252984411
  * every shared negative list and its live associations
against every active positive keyword and against the entire observed
search-term corpus. Read-only. Removes nothing.

Google negative matching rules applied here:
  * negatives never use close variants (car does not block cars)
  * BROAD negative blocks a query only when EVERY word of the negative
    appears somewhere in the query, in any order
  * PHRASE negative blocks a query containing the words in order
  * EXACT negative blocks only the identical query
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, SNAP, TZ, client, q, identity_gate, E, write,
)

STAMP = "2026-08-27"
ACCOUNT_SET = "11252984411"

# The five approved services, expressed as the phrases a customer would type.
SERVICE_PROBES = [
    "ac repair near me", "ac repair", "air conditioning repair near me",
    "air conditioner repair", "emergency ac repair", "ac repair cost",
    "commercial ac repair", "residential ac repair", "ac not cooling repair",
    "hvac repair near me", "hvac repair", "hvac service near me",
    "hvac company near me", "hvac contractor near me", "heating repair near me",
    "furnace repair near me", "heat pump repair near me",
    "hvac installation near me", "hvac installers", "hvac installation cost",
    "new hvac system installation", "air conditioning installation near me",
    "furnace installation near me", "heat pump installation near me",
    "hvac replacement near me", "hvac replacement cost", "ac replacement near me",
    "furnace replacement near me", "replace hvac system",
    "gas boiler repair", "gas boiler repair near me", "boiler repair near me",
    "boiler not working", "no heat boiler repair", "steam boiler repair",
    "oil boiler repair", "commercial boiler repair",
    # location intent inside the recorded service area
    "ac repair severn md", "hvac repair severna park", "hvac installation columbia md",
    "ac repair hanover md", "hvac repair annapolis", "boiler repair glen burnie",
    "hvac repair anne arundel county", "ac repair howard county",
    # brand and equipment intent
    "carrier ac repair near me", "trane hvac repair", "lennox dealers near me",
    "ruud furnace repair", "rheem ac repair near me", "goodman hvac installation",
    "thermostat not working hvac repair", "ecobee thermostat installation",
]


def words(s):
    return re.findall(r"[a-z0-9&']+", s.lower())


def blocks(neg_text, neg_match, query):
    nw = words(neg_text)
    if not nw:
        return False, "negative tokenizes to nothing in the Latin alphabet"
    qw = words(query)
    if neg_match == "BROAD":
        hit = all(w in qw for w in nw)
        return hit, "every negative word present" if hit else ""
    if neg_match == "PHRASE":
        # Google phrase negatives match a contiguous run of WHOLE words, never a
        # raw substring. "rv" must not match inside "service".
        n = len(nw)
        hit = any(qw[i:i + n] == nw for i in range(len(qw) - n + 1))
        return hit, "phrase present as whole words in order" if hit else ""
    if neg_match == "EXACT":
        hit = nw == qw
        return hit, "identical query" if hit else ""
    return False, ""


def main():
    c = client()
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "read_only": True}
    out["identity"] = identity_gate(c, verbose=False)
    print("IDENTITY: PASS\n")

    # ---------- live negative inventory ----------
    camp_neg = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id,
                      campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
                      campaign_criterion.negative, campaign_criterion.status,
                      campaign_criterion.resource_name
                      FROM campaign_criterion WHERE campaign.id IN ({IN5})
                        AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.status != 'REMOVED'"""):
        x = r.campaign_criterion
        camp_neg.append({"scope": f"campaign:{NAME[str(r.campaign.id)]}",
                         "campaign_id": str(r.campaign.id),
                         "criterion_id": str(x.criterion_id), "text": x.keyword.text,
                         "match": E(x.keyword.match_type), "negative": x.negative,
                         "status": E(x.status), "resource_name": x.resource_name})
    acct_neg = []
    for r in q(c, f"""SELECT shared_criterion.criterion_id, shared_criterion.keyword.text,
                      shared_criterion.keyword.match_type FROM shared_criterion
                      WHERE shared_set.id = {ACCOUNT_SET}"""):
        acct_neg.append({"scope": "account-level list 11252984411",
                         "criterion_id": str(r.shared_criterion.criterion_id),
                         "text": r.shared_criterion.keyword.text,
                         "match": E(r.shared_criterion.keyword.match_type),
                         "negative": True, "status": "ENABLED"})
    out["campaign_level_negatives"] = camp_neg
    out["account_level_negatives"] = acct_neg
    print(f"== NEGATIVE INVENTORY AFFECTING THE FIVE ==")
    print(f"  campaign-level negatives (AC Repair only): {len(camp_neg)}")
    for n in camp_neg:
        print(f"     [{n['match']:6s}] {n['text']:12s} id={n['criterion_id']} "
              f"negative={n['negative']} status={n['status']}")
    print(f"  account-level negative list members: {len(acct_neg)}")

    # ---------- shared lists and associations ----------
    sets_ = []
    for r in q(c, """SELECT shared_set.id, shared_set.name, shared_set.type,
                     shared_set.status, shared_set.member_count, shared_set.reference_count
                     FROM shared_set"""):
        x = r.shared_set
        sets_.append({"id": str(x.id), "name": x.name, "type": E(x.type_),
                      "status": E(x.status), "member_count": x.member_count,
                      "reference_count": x.reference_count})
    assoc = defaultdict(list)
    for r in q(c, """SELECT campaign.id, campaign.name, campaign_shared_set.shared_set,
                     campaign_shared_set.status FROM campaign_shared_set"""):
        assoc[r.campaign_shared_set.shared_set.split("/")[-1]].append(
            {"campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
             "status": E(r.campaign_shared_set.status)})
    for s in sets_:
        s["associations"] = assoc.get(s["id"], [])
        s["attached_to_any_of_the_five"] = [
            a for a in s["associations"] if a["campaign_id"] in FIVE]
    out["shared_sets"] = sets_
    print("\n== SHARED NEGATIVE LISTS ==")
    for s in sorted(sets_, key=lambda z: -z["member_count"]):
        flag = ("  <== ATTACHED TO A LIVE CAMPAIGN"
                if s["attached_to_any_of_the_five"] else "")
        print(f"  {s['id']} {s['type']:32s} {s['status']:8s} members={s['member_count']:>5d} "
              f"refs={s['reference_count']:>3d} attached_to_five={len(s['attached_to_any_of_the_five'])} "
              f"{s['name']}{flag}")
    dangerous = [s for s in sets_ if s["id"] == "11813144900"]
    out["general_list_11813144900"] = dangerous[0] if dangerous else None
    print("\n  General List 11813144900 attachment check:")
    if dangerous:
        d = dangerous[0]
        print(f"     associations: {d['associations']}")
        print(f"     attached to any of the five: "
              f"{'YES - HARD STOP' if d['attached_to_any_of_the_five'] else 'NO - correct'}")

    # ---------- live positive keywords ----------
    kws = []
    for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status,
                      ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
                      ad_group_criterion.status, ad_group_criterion.negative
                      FROM ad_group_criterion WHERE campaign.id IN ({IN5})
                        AND ad_group_criterion.type='KEYWORD'
                        AND ad_group_criterion.status != 'REMOVED'
                        AND ad_group_criterion.negative = FALSE
                        AND ad_group.status != 'REMOVED'"""):
        kws.append({"campaign_id": str(r.campaign.id),
                    "campaign": NAME[str(r.campaign.id)],
                    "ad_group": r.ad_group.name,
                    "text": r.ad_group_criterion.keyword.text,
                    "match": E(r.ad_group_criterion.keyword.match_type)})
    out["live_positive_keywords"] = kws
    print(f"\n== LIVE POSITIVE KEYWORDS (ad group not REMOVED): {len(kws)} ==")
    for k in kws:
        print(f"  {k['campaign']:18s} [{k['match'][:6]:6s}] {k['text']}")

    # ---------- conflict test 1: negatives vs live keywords ----------
    print("\n== CONFLICT TEST 1: does any live negative block an active keyword? ==")
    c1 = []
    for n in camp_neg + acct_neg:
        for k in kws:
            if n["scope"].startswith("campaign:") and n["campaign_id"] != k["campaign_id"]:
                continue
            hit, why = blocks(n["text"], n["match"], k["text"])
            if hit:
                c1.append({"negative": n["text"], "match": n["match"], "scope": n["scope"],
                           "keyword": k["text"], "keyword_campaign": k["campaign"],
                           "why": why})
    out["conflicts_negatives_vs_keywords"] = c1
    if c1:
        for x in c1:
            print(f"  CONFLICT {x['scope']} [{x['match']}] '{x['negative']}' blocks "
                  f"'{x['keyword']}' ({x['keyword_campaign']}) - {x['why']}")
    else:
        print("  PASS: zero live negatives block any active positive keyword.")

    # ---------- conflict test 2: negatives vs the observed search-term corpus ----------
    st = json.loads((SNAP / f"search-terms-{STAMP}.json").read_text(encoding="utf-8"))
    verdicts = st["verdicts"]
    converted = {v["search_term"] for v in verdicts if v["all_conversions"] > 0}
    primary_converted = {v["search_term"] for v in verdicts if v["primary_conversions"] > 0}
    print(f"\n== CONFLICT TEST 2: negatives vs the observed corpus "
          f"({len(verdicts)} term/campaign pairs) ==")
    c2 = []
    for n in camp_neg + acct_neg:
        blocked = []
        for v in verdicts:
            if n["scope"].startswith("campaign:") and n["campaign_id"] != v["campaign_id"]:
                continue
            hit, _ = blocks(n["text"], n["match"], v["search_term"])
            if hit:
                blocked.append(v)
        if blocked:
            c2.append({
                "negative": n["text"], "match": n["match"], "scope": n["scope"],
                "terms_blocked": len(blocked),
                "impressions_blocked": sum(b["impressions"] for b in blocked),
                "clicks_blocked": sum(b["clicks"] for b in blocked),
                "cost_blocked": round(sum(b["cost"] for b in blocked), 2),
                "conversions_blocked": round(sum(b["all_conversions"] for b in blocked), 2),
                "primary_conversions_blocked": round(
                    sum(b["primary_conversions"] for b in blocked), 2),
                "example_terms": [b["search_term"] for b in blocked][:6],
            })
    out["conflicts_negatives_vs_corpus"] = c2
    harmful = [x for x in c2 if x["conversions_blocked"] > 0]
    print(f"  negatives that match at least one observed term: {len(c2)}")
    for x in sorted(c2, key=lambda z: -z["cost_blocked"]):
        mark = "  <== BLOCKS A CONVERTING TERM" if x["conversions_blocked"] > 0 else ""
        print(f"     {x['scope']:34s} [{x['match']:6s}] '{x['negative']}' "
              f"terms={x['terms_blocked']} impr={x['impressions_blocked']} "
              f"clicks={x['clicks_blocked']} cost=${x['cost_blocked']:.2f} "
              f"conv={x['conversions_blocked']}{mark}")
        print(f"        examples: {x['example_terms']}")
    out["negatives_blocking_a_converting_term"] = harmful

    # ---------- conflict test 3: negatives vs service demand probes ----------
    print("\n== CONFLICT TEST 3: negatives vs the five approved services (probe set) ==")
    c3 = []
    for n in camp_neg + acct_neg:
        for probe in SERVICE_PROBES:
            hit, why = blocks(n["text"], n["match"], probe)
            if hit:
                c3.append({"negative": n["text"], "match": n["match"], "scope": n["scope"],
                           "probe": probe, "why": why})
    out["conflicts_negatives_vs_service_probes"] = c3
    if c3:
        by_neg = defaultdict(list)
        for x in c3:
            by_neg[(x["scope"], x["match"], x["negative"])].append(x["probe"])
        print(f"  {len(by_neg)} negative(s) suppress in-scope service demand:")
        for k, v in sorted(by_neg.items(), key=lambda z: -len(z[1])):
            print(f"     {k[0]:34s} [{k[1]:6s}] '{k[2]}' suppresses {len(v)} probe(s)")
            for p in v:
                print(f"        - {p}")
    else:
        print("  PASS: no live negative suppresses any of the 54 service probes.")

    # ---------- car / auto / boat specific re-verification ----------
    print("\n== RE-VERIFICATION: car, auto, boat on AC Repair 24132507741 ==")
    cab = {}
    for t in ("car", "auto", "boat"):
        n = next((x for x in camp_neg if x["text"] == t), None)
        if not n:
            cab[t] = {"present": False}
            print(f"  {t:5s} MISSING FROM THE ACCOUNT")
            continue
        kw_hits = [k["text"] for k in kws
                   if k["campaign_id"] == "24132507741" and blocks(t, "BROAD", k["text"])[0]]
        conv_hits = [v["search_term"] for v in verdicts
                     if v["campaign_id"] == "24132507741" and v["all_conversions"] > 0
                     and blocks(t, "BROAD", v["search_term"])[0]]
        blocked_terms = [v for v in verdicts
                         if v["campaign_id"] == "24132507741"
                         and blocks(t, "BROAD", v["search_term"])[0]]
        cab[t] = {"present": True, "criterion_id": n["criterion_id"],
                  "match": n["match"], "status": n["status"], "negative": n["negative"],
                  "active_keywords_blocked": kw_hits,
                  "converting_terms_blocked": conv_hits,
                  "observed_terms_blocked": [b["search_term"] for b in blocked_terms],
                  "impressions_blocked": sum(b["impressions"] for b in blocked_terms),
                  "cost_that_had_already_been_spent": round(
                      sum(b["cost"] for b in blocked_terms), 2)}
        print(f"  {t:5s} id={n['criterion_id']} match={n['match']} status={n['status']} "
              f"negative={n['negative']}")
        print(f"        active keywords blocked : {len(kw_hits)} {kw_hits}")
        print(f"        converting terms blocked: {len(conv_hits)} {conv_hits}")
        print(f"        observed terms it covers: {len(blocked_terms)} "
              f"{[b['search_term'] for b in blocked_terms]}")
    out["car_auto_boat_reverification"] = cab

    # ---------- plural / semantic variants that leak past car, auto, boat ----------
    print("\n== VARIANT LEAK TEST (negatives have no close variants) ==")
    variants = ["cars", "automotive", "vehicle", "vehicles", "boats", "marine",
                "truck", "trucks", "van", "rv", "motorhome", "auto",
                "job", "jobs", "salary", "training", "diy", "parts", "manuals",
                "retail", "vehicle ac", "marine ac"]
    leak = []
    for var in variants:
        covered = any(blocks(n["text"], n["match"], var)[0]
                      for n in camp_neg if n["campaign_id"] == "24132507741")
        covered = covered or any(blocks(n["text"], n["match"], var)[0] for n in acct_neg)
        obs = [v for v in verdicts if var in words(v["search_term"])]
        leak.append({"variant": var, "already_covered_on_ac_repair": covered,
                     "observed_terms": len(obs),
                     "observed_impressions": sum(o["impressions"] for o in obs),
                     "observed_clicks": sum(o["clicks"] for o in obs),
                     "observed_cost": round(sum(o["cost"] for o in obs), 2),
                     "observed_conversions": round(sum(o["all_conversions"] for o in obs), 2),
                     "examples": [o["search_term"] for o in obs][:4]})
    out["variant_leak_test"] = leak
    print(f"  {'variant':12s} {'covered':8s} {'terms':>6s} {'impr':>5s} {'clk':>4s} "
          f"{'cost':>8s} {'conv':>5s}  examples")
    for x in leak:
        print(f"  {x['variant']:12s} {str(x['already_covered_on_ac_repair']):8s} "
              f"{x['observed_terms']:>6d} {x['observed_impressions']:>5d} "
              f"{x['observed_clicks']:>4d} ${x['observed_cost']:>7.2f} "
              f"{x['observed_conversions']:>5.1f}  {x['examples']}")

    # ---------- competitor-brand spend concentration in HVAC Installation ----------
    print("\n== COMPETITOR / COMPANY-NAME SPEND (the dominant observed waste) ==")
    COMPETITOR = re.compile(
        r"\b(croppmetcalfe|fh furr|f h furr|furr|woodfin|blauch|armbridge|bluedot|"
        r"michael and sons|michael & sons|aj michaels|a j michaels|mccrea|barstow|"
        r"elmar mechanical|hugee|w n kirkland|d w bahr|bahr|beltway hvac|"
        r"supreme service today|total comfort|maryland mechanical|"
        r"amazing plumbing|amazing heating|hvac precision services|"
        r"snell|horizon services|len the plumber|griffith energy|bge home)\b", re.I)
    comp = [v for v in verdicts if COMPETITOR.search(v["search_term"])]
    comp.sort(key=lambda z: -z["cost"])
    out["competitor_brand_terms"] = comp
    print(f"  terms={len(comp)} impressions={sum(x['impressions'] for x in comp)} "
          f"clicks={sum(x['clicks'] for x in comp)} "
          f"cost=${round(sum(x['cost'] for x in comp), 2):,.2f} "
          f"primary_conversions={round(sum(x['primary_conversions'] for x in comp), 2)} "
          f"all_conversions={round(sum(x['all_conversions'] for x in comp), 2)}")
    for v in comp:
        print(f"     {v['campaign']:18s} impr={v['impressions']:>3d} clk={v['clicks']:>2d} "
              f"${v['cost']:>7.2f} primary={v['primary_conversions']:.1f} "
              f"all={v['all_conversions']:.1f}  '{v['search_term']}'")

    out["protected_terms"] = {"any_conversion": sorted(converted),
                              "primary_conversion": sorted(primary_converted)}
    write(SNAP / f"negative-conflict-audit-{STAMP}.json", out)
    return out


if __name__ == "__main__":
    main()
