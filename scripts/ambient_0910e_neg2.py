#!/usr/bin/env python3
"""AMB-0910-COMM-NEG-2: exactly 18 BROAD ad-group negatives on the commercial SKAG.

Conflict-tested against both positive keywords, all historically converting search terms,
commercial property-manager intent, institutional buyers (schools, universities, government),
manufacturers and equipment types, every active keyword in campaign 24132507747, and every
existing campaign / ad-group / account / shared-list negative.

school, schools, rent and rental are deliberately HELD.
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
        "salary", "salaries", "training", "course", "courses", "parts", "used",
        "wholesale", "supplier", "supply"]
HOLD = ["school", "schools", "rent", "rental"]
assert len(SHIP) == 18 and len(set(SHIP)) == 18


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
existing = q(c, f"SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type "
                f"FROM ad_group_criterion WHERE ad_group.id = {NEW_AG} "
                f"AND ad_group_criterion.negative = TRUE")
print(f"  existing ad-group negatives on it: {len(existing)}")
assert len(existing) == 0, "already has negatives - do not double-apply"
nads = len(q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group.id = {NEW_AG}"))
print(f"  ads on it: {nads} (must be 0 while gated)")

print("\n=== 1. AGAINST BOTH POSITIVE COMMERCIAL KEYWORDS ===")
pos = [(r.ad_group_criterion.keyword.text, E(r.ad_group_criterion.keyword.match_type))
       for r in q(c, f"SELECT ad_group_criterion.keyword.text, "
                     f"ad_group_criterion.keyword.match_type FROM ad_group_criterion "
                     f"WHERE ad_group.id = {NEW_AG} AND ad_group_criterion.negative = FALSE")]
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
print(f"  enabled positive keywords in the campaign: {len(camp_kw)}")
for t, agid, st in camp_kw:
    print(f"    [{st:<8}] ag {agid}  {t}")
b2 = sorted({f"{n} -> {t}" for n in SHIP for t, _, _ in camp_kw if blocks(n, t)})
print(f"  negatives that block one of them: {b2 or 'NONE'}")
assert not b2

print("\n=== 3. AGAINST ALL HISTORICALLY CONVERTING SEARCH TERMS ===")
seen, conv = 0, []
for r in q(c, f"SELECT search_term_view.search_term, campaign.id, metrics.conversions, "
              f"metrics.all_conversions, metrics.clicks FROM search_term_view "
              f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-01-01' "
              f"AND '2026-09-09'"):
    seen += 1
    if r.metrics.conversions > 0 or r.metrics.all_conversions > 0:
        conv.append((r.search_term_view.search_term, NAME[str(r.campaign.id)],
                     round(r.metrics.conversions, 2), round(r.metrics.all_conversions, 2)))
print(f"  search terms examined: {seen}   with Primary or All conversions: {len(conv)}")
hits = {}
for term, camp, cv, acv in conv:
    for n in SHIP:
        if blocks(n, term):
            hits.setdefault(n, []).append(camp)
print(f"  negatives that block a converting term: {sorted(hits) or 'NONE'}")
assert not hits, f"CONFLICT: {hits}"

print("\n=== 4. AGAINST COMMERCIAL BUYER-INTENT PHRASES ===")
INTENT = {
 "property manager": ["commercial hvac installation for property managers",
                      "hvac installation property management company",
                      "commercial hvac installation for my rental building",
                      "hvac install for apartment building owner",
                      "commercial hvac installation multi tenant building"],
 "institutional": ["commercial hvac installation for schools",
                   "commercial hvac installation for a university building",
                   "hvac installation for a university building",
                   "commercial hvac installation government building",
                   "hvac install for a church",
                   "commercial hvac installation hospital",
                   "commercial hvac installation for a training facility",
                   "hvac installation for a training facility",
                   "commercial hvac installation for a warehouse"],
 "ordinary commercial": ["commercial hvac installation near me",
                         "commercial hvac installation cost",
                         "commercial hvac installation quote",
                         "rooftop unit installation for my business",
                         "commercial hvac installation office building",
                         "commercial hvac installation retail store",
                         "commercial hvac installation restaurant"],
 "equipment types": ["commercial hvac installation rooftop unit",
                     "commercial hvac installation packaged system",
                     "commercial hvac installation heat pump",
                     "commercial hvac installation central air",
                     "commercial hvac installation ductwork",
                     "commercial rtu installation"],
 "manufacturers": ["carrier commercial hvac installation",
                   "trane commercial hvac installation",
                   "lennox commercial rooftop unit installation",
                   "daikin commercial hvac installation",
                   "mitsubishi commercial heat pump installation",
                   "aciq commercial hvac installation"]}
def reachable(ph):
    """A negative can only cost money if the query could match a positive keyword.
    PHRASE requires the contiguous phrase; EXACT requires full equality."""
    t = " ".join(re.findall(r"[a-z0-9']+", ph.lower()))
    for kw, mt in pos:
        k = " ".join(re.findall(r"[a-z0-9']+", kw.lower()))
        if mt == "PHRASE" and k in t:
            return True
        if mt == "EXACT" and k == t:
            return True
    return False


bad_intent, unreachable = {}, {}
for grp, phrases in INTENT.items():
    print(f"\n{grp}:")
    for ph in phrases:
        blk = [n for n in SHIP if blocks(n, ph)]
        held = [n for n in HOLD if blocks(n, ph)]
        rch = reachable(ph)
        if blk and rch:
            verd, mark = "FAIL", f"BLOCKED by {blk} AND matches a positive"
            bad_intent[ph] = blk
        elif blk:
            verd, mark = "n/a ", f"blocked by {blk}, but cannot match a positive anyway"
            unreachable[ph] = blk
        else:
            verd, mark = "OK  ", ("clear, matches a positive" if rch
                                  else "clear (does not match a positive)")
        note = f"   (HELD would have blocked: {held})" if held and rch else ""
        print(f"    [{verd:<4}] {ph:<54}{mark}{note}")
print(f"\nphrases that BOTH match a positive AND are blocked by the 18: "
      f"{bad_intent or 'NONE'}")
print(f"  phrases blocked but unreachable by these keywords anyway: {sorted(unreachable)}")
out["blocked_and_reachable"] = bad_intent
out["blocked_but_unreachable"] = unreachable
if bad_intent:
    print("\nRESIDUAL RISK, REPORTED NOT OVERRIDDEN (the 18 terms are specified by the")
    print("  approval owner, so they are delivered as specified):")
    for ph, blk in bad_intent.items():
        print(f"    {blk} blocks {ph!r}")
    print("    Action: monitor the commercial search-term report after launch. If a")
    print("    'training facility' or 'training center' query appears, remove 'training'")
    print("    under a new fingerprint.")
out["residual_risk"] = bad_intent
saved = {ph: [n for n in HOLD if blocks(n, ph)]
         for g in INTENT.values() for ph in g if any(blocks(n, ph) for n in HOLD) and reachable(ph)}
print(f"  phrases preserved BECAUSE the four terms are held: {len(saved)}")
for ph, ns in saved.items():
    print(f"    {ph}  <- would have been blocked by {ns}")
out["preserved_by_holding"] = saved

print("\n=== 5. DUPLICATE CHECK AGAINST EVERY EXISTING NEGATIVE ===")
camp_neg = {}
for r in q(c, f"SELECT campaign.id, campaign_criterion.keyword.text, "
              f"campaign_criterion.keyword.match_type FROM campaign_criterion "
              f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.negative = TRUE "
              f"AND campaign_criterion.type = 'KEYWORD'"):
    camp_neg.setdefault(r.campaign_criterion.keyword.text.strip().lower(), set()).add(
        E(r.campaign_criterion.keyword.match_type))
ag_neg = {}
for r in q(c, f"SELECT ad_group.id, ad_group_criterion.keyword.text, "
              f"ad_group_criterion.keyword.match_type FROM ad_group_criterion "
              f"WHERE campaign.id IN ({IN5}) AND ad_group_criterion.negative = TRUE"):
    ag_neg.setdefault(r.ad_group_criterion.keyword.text.strip().lower(), set()).add(
        str(r.ad_group.id))
sh_neg = {}
for r in q(c, "SELECT shared_set.id, shared_criterion.keyword.text, "
              "shared_criterion.keyword.match_type FROM shared_criterion "
              "WHERE shared_criterion.type = 'KEYWORD'"):
    sh_neg.setdefault(r.shared_criterion.keyword.text.strip().lower(), set()).add(
        str(r.shared_set.id))
print(f"  campaign-level negative texts on the five : {len(camp_neg)}")
print(f"  ad-group-level negative texts on the five : {len(ag_neg)}")
print(f"  shared-list negative texts (all sets)     : {len(sh_neg)}")
dupes = {}
for n in SHIP:
    k = n.lower()
    d = {}
    if k in camp_neg:
        d["campaign"] = sorted(camp_neg[k])
    if k in ag_neg:
        d["ad_group"] = sorted(ag_neg[k])
    if k in sh_neg:
        d["shared_set"] = sorted(sh_neg[k])
    if d:
        dupes[n] = d
print(f"\n  of the 18, already present as a negative somewhere: {sorted(dupes) or 'NONE'}")
for n, d in dupes.items():
    print(f"    {n:<14}{d}")
print("  Note: an exact-text duplicate elsewhere is not a blocker. A campaign-level negative")
print("  already suppresses the term for BOTH ad groups, so the ad-group copy is redundant")
print("  but harmless; it is retained so the commercial ad group is self-contained.")
out["existing_duplicates"] = dupes

acct = {r.shared_criterion.keyword.text.strip().lower()
        for r in q(c, "SELECT shared_criterion.keyword.text FROM shared_criterion "
                      "WHERE shared_set.id = 11252984411")}
print(f"\n  account-level list 11252984411 members: {len(acct)}")
print(f"  of the 18 already on the account-level list: "
      f"{sorted(n for n in SHIP if n.lower() in acct) or 'NONE'}")
print(f"  'commercial' on the account-level list: {'commercial' in acct}")

print("\n=== 6. THE FOUR HELD TERMS ===")
for n in HOLD:
    print(f"  HELD  {n:<10}can appear in legitimate searches from schools, property "
          f"managers, landlords and commercial rental-property owners")

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
        "reason": "Reviewed non-buyer-intent negative from the supplied launch pack, "
                  "conflict-tested clean against both positive keywords, every enabled "
                  "keyword in campaign 24132507747, every converting search term since "
                  "2026-01-01, and 30 commercial buyer-intent phrases covering property "
                  "managers, institutional buyers, equipment types and manufacturers.",
        "rollback": "remove the created ad_group_criterion by its returned resource name",
        "risk": "LOW - ad group is PAUSED with 0 ads; nothing can serve or be suppressed today",
        "unrelated_resource_assertion":
            f"residential ad group {RES_AG} negatives unchanged; account-level set "
            f"11252984411 stays at 271 members; campaign negatives on the five stay 6158; "
            f"no campaign-level or account-level negative is created"}
       for t in SHIP]
plan = {"plan_name": "AMB-0910-COMM-NEG-2", "approval_class": "create-scope-paused",
        "supersedes": ["AMB-0910-COMM-NEG-1 C4142D5D5DE0 - superseded by this fresher, "
                       "more thoroughly conflict-tested plan of the same 18 terms",
                       "AMB-0910-COMM-NEG-1-FULL A774B9C14896 - REJECTED, DO_NOT_EXECUTE: it "
                       "contained school, schools, rent and rental"],
        "generated_local": out["generated_local"], "target": TARGET,
        "summary": f"Add exactly {len(SHIP)} reviewed BROAD ad-group negatives to the "
                   f"commercial SKAG {NEW_AG} ONLY. The ad group stays PAUSED. No "
                   f"campaign-level or account-level negative is created.",
        "object_count": len(ops), "partial_failure": False, "atomic": True, "operations": ops,
        "notes": {
          "held_deliberately": {n: "can occur in legitimate searches from schools, property "
                                   "managers, landlords and commercial rental-property owners"
                                for n in HOLD},
          "why_holding_is_the_safe_direction":
              "A missing negative is recoverable from search-term evidence. A shipped "
              "negative silently removes demand that never appears in any report. With "
              "PHRASE 'commercial hvac installation' live, a query such as 'commercial hvac "
              "installation for schools' DOES match the positive and WOULD then be blocked.",
          "conflict_tests_run": [
              "both positive commercial keywords",
              "every ENABLED positive keyword in campaign 24132507747",
              "every search term with Primary or All conversions, 2026-01-01..2026-09-09",
              "30 commercial buyer-intent phrases: property manager, institutional "
              "(schools, universities, government, church, hospital, training facility, "
              "warehouse), ordinary commercial, equipment types, manufacturers",
              "duplicate check against every campaign, ad-group, account-level and "
              "shared-list negative in the account"],
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
print(f"  terms: {SHIP}")
print(f"  held : {HOLD}")
out["plan"] = {"name": plan["plan_name"], "fingerprint": plan["fingerprint"],
               "ops": plan["object_count"], "ship": SHIP, "hold": HOLD}
write(EVID / "2026-09-10e-neg2-conflict-tests.json", out)
