#!/usr/bin/env python3
"""AMB-0910-COMM-NEG-3: exactly 17 BROAD ad-group negatives on the commercial SKAG.

Supersedes AMB-0910-COMM-NEG-2 A9C9BCBDDD74. 'training' is now HELD alongside school,
schools, rent and rental, because BROAD 'training' blocks reachable commercial buyer intent
such as 'commercial hvac installation for a training facility'.

Every conflict test is re-run from scratch against the live account. Nothing is executed.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

c = client()
identity_gate(c, verbose=False)
CAMP, RES_AG, NEW_AG = "24132507747", "202339087634", "199748801029"
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}

SHIP = ["residential", "homeowner", "house", "diy", "job", "jobs", "career", "careers",
        "salary", "salaries", "course", "courses", "parts", "used",
        "wholesale", "supplier", "supply"]
HOLD = ["school", "schools", "rent", "rental", "training"]
HOLD_REASON = {
    "school": "schools and school districts are institutional commercial HVAC buyers",
    "schools": "schools and school districts are institutional commercial HVAC buyers",
    "rent": "property managers, landlords and commercial rental-property owners",
    "rental": "property managers, landlords and commercial rental-property owners",
    "training": "BROAD 'training' blocks reachable commercial buyer intent such as "
                "'commercial hvac installation for a training facility'"}
assert len(SHIP) == 17 and len(set(SHIP)) == 17, len(SHIP)
assert "training" not in SHIP and "training" in HOLD
PREV = ["residential", "homeowner", "house", "diy", "job", "jobs", "career", "careers",
        "salary", "salaries", "training", "course", "courses", "parts", "used",
        "wholesale", "supplier", "supply"]
assert set(PREV) - set(SHIP) == {"training"}, "the only delta must be 'training'"


def toks(s):
    return set(re.findall(r"[a-z0-9']+", str(s).lower()))


def blocks(neg, query):
    """BROAD negative: blocks when every token of the negative appears in the query."""
    return toks(neg) <= toks(query)


print("=== 0. LIVE STATE OF THE TARGET AD GROUP ===")
ag = q(c, f"SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id FROM ad_group "
          f"WHERE ad_group.id = {NEW_AG}")
assert ag and E(ag[0].ad_group.status) == "PAUSED" and str(ag[0].campaign.id) == CAMP
print(f"  {NEW_AG}  PAUSED  {ag[0].ad_group.name}  campaign {CAMP}")
existing = q(c, f"SELECT ad_group_criterion.keyword.text FROM ad_group_criterion "
                f"WHERE ad_group.id = {NEW_AG} AND ad_group_criterion.negative = TRUE")
nads = len(q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group.id = {NEW_AG}"))
print(f"  existing ad-group negatives: {len(existing)}   ads: {nads}")
assert len(existing) == 0, "already has negatives - NEG-2 must NOT have been executed"
assert nads == 0, "ad group must hold no ads while gated"
print("  confirmed: AMB-0910-COMM-NEG-2 was NOT executed")

pos = [(r.ad_group_criterion.keyword.text, E(r.ad_group_criterion.keyword.match_type))
       for r in q(c, f"SELECT ad_group_criterion.keyword.text, "
                     f"ad_group_criterion.keyword.match_type FROM ad_group_criterion "
                     f"WHERE ad_group.id = {NEW_AG} AND ad_group_criterion.negative = FALSE")]


def reachable(ph):
    """A negative can only cost money if the query could match a positive keyword."""
    t = " ".join(re.findall(r"[a-z0-9']+", ph.lower()))
    for kw, mt in pos:
        k = " ".join(re.findall(r"[a-z0-9']+", kw.lower()))
        if mt == "PHRASE" and k in t:
            return True
        if mt == "EXACT" and k == t:
            return True
    return False


print("\n=== 1. AGAINST BOTH POSITIVE COMMERCIAL KEYWORDS ===")
print(f"  positives: {pos}")
b1 = sorted({n for n in SHIP for t, _ in pos if blocks(n, t)})
print(f"  negatives that block a positive keyword: {b1 or 'NONE'}")
assert not b1

print("\n=== 2. AGAINST EVERY ACTIVE KEYWORD IN CAMPAIGN 24132507747 ===")
camp_kw = [(r.ad_group_criterion.keyword.text, str(r.ad_group.id), E(r.ad_group.status))
           for r in q(c, f"SELECT ad_group.id, ad_group.status, "
                         f"ad_group_criterion.keyword.text FROM ad_group_criterion "
                         f"WHERE campaign.id = {CAMP} AND ad_group_criterion.negative = FALSE "
                         f"AND ad_group_criterion.status = 'ENABLED' "
                         f"AND ad_group_criterion.type = 'KEYWORD'")]
for t, agid, st in camp_kw:
    print(f"    [{st:<8}] ag {agid}  {t}")
b2 = sorted({f"{n} -> {t}" for n in SHIP for t, _, _ in camp_kw if blocks(n, t)})
print(f"  negatives that block one of them: {b2 or 'NONE'}")
assert not b2

print("\n=== 3. AGAINST ALL HISTORICALLY CONVERTING SEARCH TERMS ===")
seen, conv = 0, []
for r in q(c, f"SELECT search_term_view.search_term, campaign.id, metrics.conversions, "
              f"metrics.all_conversions FROM search_term_view "
              f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-01-01' "
              f"AND '2026-09-09'"):
    seen += 1
    if r.metrics.conversions > 0 or r.metrics.all_conversions > 0:
        conv.append((r.search_term_view.search_term, NAME[str(r.campaign.id)]))
print(f"  search terms examined: {seen}   with Primary or All conversions: {len(conv)}")
hits = {}
for term, camp in conv:
    for n in SHIP:
        if blocks(n, term):
            hits.setdefault(n, []).append(camp)
print(f"  negatives that block a converting term: {sorted(hits) or 'NONE'}")
assert not hits, f"CONFLICT: {hits}"

print("\n=== 4. AGAINST COMMERCIAL BUYER-INTENT PHRASES (reachability-aware) ===")
INTENT = {
 "property manager / landlord": [
     "commercial hvac installation for property managers",
     "commercial hvac installation for my rental building",
     "commercial hvac installation multi tenant building",
     "commercial hvac installation apartment complex",
     "hvac installation property management company"],
 "institutional / education / government": [
     "commercial hvac installation for schools",
     "commercial hvac installation for a school district",
     "commercial hvac installation for a university building",
     "commercial hvac installation for a training facility",
     "commercial hvac installation for a training center",
     "commercial hvac installation government building",
     "commercial hvac installation for a church",
     "commercial hvac installation hospital",
     "commercial hvac installation for a daycare",
     "commercial hvac installation for a warehouse"],
 "ordinary commercial": [
     "commercial hvac installation near me",
     "commercial hvac installation cost",
     "commercial hvac installation quote",
     "commercial hvac installation office building",
     "commercial hvac installation retail store",
     "commercial hvac installation restaurant",
     "commercial hvac installation for a gym",
     "commercial hvac installation new construction"],
 "equipment types": [
     "commercial hvac installation rooftop unit",
     "commercial hvac installation packaged system",
     "commercial hvac installation heat pump",
     "commercial hvac installation central air",
     "commercial hvac installation ductwork",
     "commercial hvac installation vrf system"],
 "manufacturers": [
     "carrier commercial hvac installation",
     "trane commercial hvac installation",
     "lennox commercial hvac installation",
     "daikin commercial hvac installation",
     "mitsubishi commercial hvac installation",
     "aciq commercial hvac installation"],
 "non-buyer intent that SHOULD be blocked": [
     "commercial hvac installation jobs near me",
     "commercial hvac installation salary",
     "commercial hvac installation career",
     "commercial hvac installation course",
     "commercial hvac installation diy",
     "commercial hvac installation parts supplier",
     "used commercial hvac installation equipment",
     "residential hvac installation near me"]}
bad, unreach, correctly_blocked = {}, {}, {}
for grp, phrases in INTENT.items():
    print(f"\n  {grp}:")
    for ph in phrases:
        blk = [n for n in SHIP if blocks(n, ph)]
        held = [n for n in HOLD if blocks(n, ph)]
        rch = reachable(ph)
        want_blocked = grp.startswith("non-buyer")
        if blk and rch and not want_blocked:
            verd, mark = "FAIL", f"BLOCKED by {blk} AND matches a positive"
            bad[ph] = blk
        elif blk and want_blocked:
            verd, mark = "OK", f"correctly blocked by {blk}"
            correctly_blocked[ph] = blk
        elif blk:
            verd, mark = "n/a", f"blocked by {blk}, unreachable by these keywords"
            unreach[ph] = blk
        elif want_blocked:
            verd, mark = "MISS", "NOT blocked - non-buyer intent will get through"
        else:
            verd, mark = "OK", ("clear, matches a positive" if rch
                                else "clear (does not match a positive)")
        note = f"   (HELD would have blocked: {held})" if held and rch else ""
        print(f"    [{verd:<4}] {ph:<52}{mark}{note}")
print(f"\n  buyer phrases BOTH reachable AND blocked by the 17: {bad or 'NONE'}")
assert not bad, f"CONFLICT: {bad}"
saved = {ph: [n for n in HOLD if blocks(n, ph)]
         for g in INTENT.values() for ph in g
         if any(blocks(n, ph) for n in HOLD) and reachable(ph)}
print(f"  buyer phrases preserved BECAUSE the five terms are held: {len(saved)}")
for ph, ns in sorted(saved.items()):
    print(f"    {ph:<54}<- would have been blocked by {ns}")
print(f"  non-buyer phrases still correctly blocked: {len(correctly_blocked)}/8")
out["preserved_by_holding"] = saved
out["correctly_blocked"] = correctly_blocked
out["blocked_but_unreachable"] = unreach

print("\n=== 5. THE DELTA FROM NEG-2: WHAT DOES DROPPING 'training' CHANGE? ===")
train_ph = [ph for g in INTENT.values() for ph in g if blocks("training", ph)]
print(f"  phrases that BROAD 'training' would have blocked: {len(train_ph)}")
for ph in train_ph:
    print(f"    {'REACHABLE' if reachable(ph) else 'unreachable':<12}{ph}")
regained = [ph for ph in train_ph if reachable(ph)]
print(f"  reachable commercial buyer phrases regained by holding it: {len(regained)}")
for ph in regained:
    print(f"    + {ph}")
lost = [ph for g in [INTENT['non-buyer intent that SHOULD be blocked']] for ph in g
        if blocks("training", ph) and not any(blocks(n, ph) for n in SHIP)]
print(f"  non-buyer phrases now UNBLOCKED because 'training' was dropped: {lost or 'NONE'}")
out["training_delta"] = {"blocked_phrases": train_ph, "reachable_regained": regained,
                         "non_buyer_now_unblocked": lost}

print("\n=== 6. DUPLICATE CHECK AGAINST EVERY EXISTING NEGATIVE ===")
camp_neg, ag_neg, sh_neg = {}, {}, {}
for r in q(c, f"SELECT campaign.id, campaign_criterion.keyword.text, "
              f"campaign_criterion.keyword.match_type FROM campaign_criterion "
              f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.negative = TRUE "
              f"AND campaign_criterion.type = 'KEYWORD'"):
    camp_neg.setdefault(r.campaign_criterion.keyword.text.strip().lower(), set()).add(
        E(r.campaign_criterion.keyword.match_type))
for r in q(c, f"SELECT ad_group.id, ad_group_criterion.keyword.text FROM ad_group_criterion "
              f"WHERE campaign.id IN ({IN5}) AND ad_group_criterion.negative = TRUE"):
    ag_neg.setdefault(r.ad_group_criterion.keyword.text.strip().lower(), set()).add(
        str(r.ad_group.id))
for r in q(c, "SELECT shared_set.id, shared_criterion.keyword.text FROM shared_criterion "
              "WHERE shared_criterion.type = 'KEYWORD'"):
    sh_neg.setdefault(r.shared_criterion.keyword.text.strip().lower(), set()).add(
        str(r.shared_set.id))
attached = set()
for r in q(c, "SELECT campaign.id, campaign_shared_set.shared_set FROM campaign_shared_set"):
    if str(r.campaign.id) in FIVE:
        attached.add(r.campaign_shared_set.shared_set.split("/")[-1])
print(f"  shared sets actually attached to the five campaigns: {sorted(attached) or 'NONE'}")
dupes = {}
for n in SHIP:
    k = n.lower()
    d = {}
    if k in camp_neg:
        d["campaign_level"] = sorted(camp_neg[k])
    if k in ag_neg:
        d["ad_group_level"] = sorted(ag_neg[k])
    live_sets = sorted(sh_neg.get(k, set()) & attached)
    if live_sets:
        d["ATTACHED_shared_set"] = live_sets
    inert = sorted(sh_neg.get(k, set()) - attached)
    if inert:
        d["inert_shared_sets"] = len(inert)
    if d:
        dupes[n] = d
print(f"  of the 17, present elsewhere: {sorted(dupes)}")
for n, d in sorted(dupes.items()):
    print(f"    {n:<12}{d}")
acct = {r.shared_criterion.keyword.text.strip().lower()
        for r in q(c, "SELECT shared_criterion.keyword.text FROM shared_criterion "
                      "WHERE shared_set.id = 11252984411")}
print(f"\n  account-level list 11252984411: {len(acct)} members")
print(f"  of the 17 already on it: {sorted(n for n in SHIP if n.lower() in acct) or 'NONE'}")
print(f"  'commercial' on it: {'commercial' in acct}")
out["duplicates"] = dupes

print("\n=== 7. HELD TERMS ===")
for n in HOLD:
    print(f"  HELD  {n:<10}{HOLD_REASON[n]}")

TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "HVAC Installation",
          "related_services": ["AC Repair", "HVAC Repair", "HVAC Replacement",
                               "Gas Boiler Repair", "Commercial HVAC Installation"]}
ops = [{"operation": "ADD_AD_GROUP_NEGATIVE_KEYWORD", "resource": "ad_group_criterion",
        "resource_id": NEW_AG, "resource_name": "SKAG | Commercial HVAC Installation",
        "campaign_id": CAMP, "keyword_text": t, "match_type": "BROAD",
        "current_state": f"ad group {NEW_AG} holds 0 ad-group negatives and 0 ads, PAUSED",
        "proposed_state": f"BROAD negative {t!r} on ad group {NEW_AG} only",
        "reason": "Reviewed non-buyer-intent negative from the supplied launch pack. "
                  "Conflict-tested clean against both positive keywords, every ENABLED "
                  "keyword in campaign 24132507747, every converting search term since "
                  "2026-01-01, and 43 intent phrases spanning property managers, "
                  "institutional buyers, ordinary commercial intent, equipment types, "
                  "manufacturers and non-buyer controls.",
        "rollback": "remove the created ad_group_criterion by its returned resource name",
        "risk": "LOW - the ad group is PAUSED with 0 ads, so nothing can serve or be "
                "suppressed today",
        "unrelated_resource_assertion":
            f"residential ad group {RES_AG} negatives unchanged; account-level set "
            f"11252984411 stays at 271 members; campaign negatives on the five stay 6158; "
            f"no campaign-level or account-level negative is created"}
       for t in SHIP]
plan = {"plan_name": "AMB-0910-COMM-NEG-3", "approval_class": "create-scope-paused",
        "supersedes": ["AMB-0910-COMM-NEG-2 A9C9BCBDDD74 - SUPERSEDED, DO_NOT_EXECUTE. It "
                       "contained BROAD 'training', which blocks the reachable commercial "
                       "buyer phrase 'commercial hvac installation for a training facility'.",
                       "AMB-0910-COMM-NEG-1 C4142D5D5DE0 - SUPERSEDED",
                       "AMB-0910-COMM-NEG-1-FULL A774B9C14896 - REJECTED"],
        "generated_local": out["generated_local"], "target": TARGET,
        "summary": f"Add exactly {len(SHIP)} reviewed BROAD ad-group negatives to the "
                   f"commercial SKAG {NEW_AG} ONLY. The ad group stays PAUSED. No "
                   f"campaign-level or account-level negative is created.",
        "object_count": len(ops), "partial_failure": False, "atomic": True, "operations": ops,
        "notes": {
          "held_deliberately": HOLD_REASON,
          "delta_from_NEG_2": "'training' removed. That is the only change. 17 operations "
                              "instead of 18.",
          "why_training_was_dropped":
              "BROAD 'training' blocks any query containing the token. "
              "'commercial hvac installation for a training facility' and "
              "'commercial hvac installation for a training center' both match the live "
              "PHRASE keyword and would both have been suppressed. Training facilities and "
              "training centres are ordinary commercial buildings.",
          "cost_of_dropping_it":
              "Course-seeker queries containing 'training' are no longer blocked by this "
              "list. 'course' and 'courses' remain, and 'commercial hvac installation "
              "course' is still correctly blocked. Monitor the search-term report; if "
              "'hvac training' style non-buyer queries appear at volume, add a narrower "
              "PHRASE negative such as \"hvac training\" rather than BROAD 'training'.",
          "why_holding_is_the_safe_direction":
              "A missing negative is recoverable from search-term evidence. A shipped "
              "negative silently removes demand that never appears in any report.",
          "conflict_tests_run": [
              "both positive commercial keywords",
              "every ENABLED positive keyword in campaign 24132507747",
              "every search term with Primary or All conversions, 2026-01-01..2026-09-09",
              "43 intent phrases: property manager/landlord, institutional "
              "(schools, districts, universities, training facilities, government, church, "
              "hospital, daycare, warehouse), ordinary commercial, equipment types, "
              "manufacturers, and 8 non-buyer controls that SHOULD be blocked",
              "reachability filter: a phrase counts as a conflict only if it could match a "
              "positive keyword",
              "duplicate sweep across every campaign, ad-group, account-level and "
              "shared-list negative, distinguishing ATTACHED shared sets from inert ones"],
          "barred_categories_respected":
              "No manufacturer name, location name, free, quote, estimate, cost, pricing, "
              "building, property manager, repair or maintenance negative is used.",
          "scope": "Ad-group level only, on the commercial SKAG. 'commercial' is NOT added "
                   "anywhere by this plan.",
          "requires_new_approval": True}}
plan["fingerprint"] = approval_code({"target": TARGET, "plan": plan["plan_name"],
                                     "operations": ops})
(CLIENT_DIR / "plans" / f"{plan['plan_name']}.json").write_text(
    json.dumps(plan, indent=1, default=str), encoding="utf-8")
print(f"\n\n=== {plan['plan_name']}  {plan['object_count']} ops  "
      f"fingerprint {plan['fingerprint']} ===")
print(f"  SHIP ({len(SHIP)}): {SHIP}")
print(f"  HOLD ({len(HOLD)}): {HOLD}")
out["plan"] = {"name": plan["plan_name"], "fingerprint": plan["fingerprint"],
               "ops": plan["object_count"], "ship": SHIP, "hold": HOLD}
write(EVID / "2026-09-10f-neg3-conflict-tests.json", out)
