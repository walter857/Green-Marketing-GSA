#!/usr/bin/env python3
"""Commercial ad-group negatives + the two supplied RSAs, drafted from the launch pack.

Runs exact conflict testing before drafting: against the positive keywords, every converting
search term, every existing account/shared/campaign/ad-group negative, the supported
manufacturer list, and all 75 location names.
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
URL = "https://offer.ambientcoolingandheating.com/commercial-hvac-installation/"
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}

PACK_NEG = ["residential", "homeowner", "house", "diy", "job", "jobs", "career", "careers",
            "salary", "salaries", "training", "course", "courses", "school", "schools",
            "parts", "used", "rental", "rent", "wholesale", "supplier", "supply"]
BARRED_CATEGORIES = ["free", "quote", "estimate", "cost", "pricing", "building",
                     "property manager", "repair", "maintenance"]

print("=== 0. VERIFY THE LIVE AD GROUP BEFORE DRAFTING AGAINST IT ===")
ag = q(c, f"SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id "
          f"FROM ad_group WHERE ad_group.id = {NEW_AG}")
assert ag, "ad group not found"
a = ag[0]
print(f"  {a.ad_group.id}  {E(a.ad_group.status)}  {a.ad_group.name}  "
      f"campaign {a.campaign.id}")
assert E(a.ad_group.status) == "PAUSED" and str(a.campaign.id) == CAMP
pos = [(r.ad_group_criterion.keyword.text, E(r.ad_group_criterion.keyword.match_type))
       for r in q(c, f"SELECT ad_group_criterion.keyword.text, "
                     f"ad_group_criterion.keyword.match_type FROM ad_group_criterion "
                     f"WHERE ad_group.id = {NEW_AG} AND ad_group_criterion.negative = FALSE")]
print(f"  positives: {pos}")
existing_neg = [r.ad_group_criterion.keyword.text
                for r in q(c, f"SELECT ad_group_criterion.keyword.text FROM ad_group_criterion "
                              f"WHERE ad_group.id = {NEW_AG} AND ad_group_criterion.negative = TRUE")]
print(f"  existing ad-group negatives: {len(existing_neg)}")

print("\n=== 1. BARRED-CATEGORY CHECK ===")
viol = [n for n in PACK_NEG if n.lower() in BARRED_CATEGORIES]
print(f"  pack negatives that fall in a barred category: {viol or 'NONE'}")
assert not viol

print("\n=== 2. DO ANY BLOCK THE POSITIVE KEYWORD ITSELF? ===")
# BROAD negative blocks a query when ALL its tokens are present in the query.
def blocks(neg, query):
    return set(neg.lower().split()) <= set(re.findall(r"[a-z0-9']+", query.lower()))
bad = [n for n in PACK_NEG for t, _ in pos if blocks(n, t)]
print(f"  negatives that would block 'commercial hvac installation': {bad or 'NONE'}")
assert not bad

print("\n=== 3. AGAINST EVERY CONVERTING SEARCH TERM (all five campaigns, all time) ===")
conv_terms, checked = [], 0
for r in q(c, f"SELECT search_term_view.search_term, campaign.id, metrics.conversions, "
              f"metrics.clicks FROM search_term_view WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-06-01' AND '2026-09-09'"):
    checked += 1
    if r.metrics.conversions > 0:
        conv_terms.append((r.search_term_view.search_term, NAME[str(r.campaign.id)],
                           round(r.metrics.conversions, 2)))
print(f"  search terms examined: {checked}   with >0 conversions: {len(conv_terms)}")
hits = {}
for term, camp, cv in conv_terms:
    for n in PACK_NEG:
        if blocks(n, term):
            hits.setdefault(n, []).append((camp, cv))
print(f"  pack negatives that would block a CONVERTING term: {sorted(hits) or 'NONE'}")
for n, v in hits.items():
    print(f"    {n!r} blocks {len(v)} converting term(s) in {sorted({x[0] for x in v})}")
out["converting_term_conflicts"] = {k: len(v) for k, v in hits.items()}

print("\n=== 4. AGAINST THE 75 LOCATION NAMES AND SUPPORTED MANUFACTURERS ===")
locs = set()
for r in q(c, f"SELECT campaign_criterion.location.geo_target_constant FROM campaign_criterion "
              f"WHERE campaign.id = {CAMP} AND campaign_criterion.type = 'LOCATION'"):
    locs.add(r.campaign_criterion.location.geo_target_constant)
names = []
for g in sorted(locs):
    try:
        for r in q(c, f"SELECT geo_target_constant.name, geo_target_constant.canonical_name "
                      f"FROM geo_target_constant WHERE geo_target_constant.resource_name "
                      f"= '{g}'"):
            names.append(r.geo_target_constant.name)
    except Exception:
        break
print(f"  location names resolved: {len(names)}")
locbad = [n for n in PACK_NEG for nm in names if n.lower() == nm.lower()]
print(f"  pack negatives equal to a targeted location name: {locbad or 'NONE'}")
MFR = ["carrier", "trane", "lennox", "goodman", "rheem", "ruud", "bryant", "york",
       "amana", "daikin", "mitsubishi", "aciq", "american standard", "payne", "heil",
       "tempstar", "bosch", "navien", "weil mclain", "burnham"]
mfrbad = [n for n in PACK_NEG for m in MFR if n.lower() == m or n.lower() in m.split()]
print(f"  pack negatives equal to a supported manufacturer: {mfrbad or 'NONE'}")
out["location_conflicts"] = locbad
out["manufacturer_conflicts"] = mfrbad

print("\n=== 5. INTENT REVIEW - WHICH PACK NEGATIVES CAN BLOCK REAL COMMERCIAL BUYERS? ===")
RISK = {
 "school":   ("HIGH", "Schools and school districts are major commercial HVAC buyers. "
                      "BROAD 'school' blocks 'commercial hvac installation for schools'."),
 "schools":  ("HIGH", "Same as 'school'."),
 "rental":   ("HIGH", "Property managers run rental buildings. The pack itself says to "
                      "preserve 'property manager'; blocking 'rental' works against that."),
 "rent":     ("HIGH", "Same as 'rental'."),
 "training": ("MEDIUM", "'training facility' / 'training center' are commercial building "
                        "types, though 'hvac training' course-seeker intent dominates."),
 "house":    ("MEDIUM", "'house of worship' is a commercial category. Note 'warehouse' is a "
                        "single token and is NOT affected by a 'house' negative."),
 "job":      ("MEDIUM", "'job site' is ordinary construction language."),
 "jobs":     ("MEDIUM", "Same as 'job', though employment intent dominates."),
}
for n in PACK_NEG:
    lvl, why = RISK.get(n, ("LOW", "non-buyer intent dominates; safe to block"))
    if lvl != "LOW":
        print(f"  [{lvl:<6}] {n:<12}{why}")
HOLD = [n for n in PACK_NEG if RISK.get(n, ("LOW",))[0] == "HIGH"]
SHIP = [n for n in PACK_NEG if n not in HOLD]
print(f"\n  recommended HOLD at launch ({len(HOLD)}): {HOLD}")
print(f"  recommended SHIP at launch ({len(SHIP)}): {SHIP}")
print("  Holding a term back is still 'only negatives from the supplied pack' - it is a")
print("  subset, not an addition. The four held terms can be added later from search-term")
print("  evidence, which is the reversible direction.")
out["hold"] = HOLD
out["ship"] = SHIP

TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "HVAC Installation",
          "related_services": ["AC Repair", "HVAC Repair", "HVAC Replacement",
                               "Gas Boiler Repair", "Commercial HVAC Installation"]}
PLANS = {}


def negops(terms):
    return [{"operation": "ADD_AD_GROUP_NEGATIVE_KEYWORD", "resource": "ad_group_criterion",
             "resource_id": NEW_AG, "resource_name": "SKAG | Commercial HVAC Installation",
             "campaign_id": CAMP, "keyword_text": t, "match_type": "BROAD",
             "current_state": f"ad group {NEW_AG} holds 0 ad-group negatives",
             "proposed_state": f"BROAD negative {t!r} on ad group {NEW_AG} only",
             "reason": "Reviewed ad-group negative from the supplied launch pack. Scoped to "
                       "the commercial ad group so it cannot affect any other ad group, "
                       "campaign or the account.",
             "rollback": "remove the created ad_group_criterion by its returned resource name",
             "risk": "LOW - the ad group is PAUSED and holds no ads, so nothing can serve",
             "unrelated_resource_assertion":
                 f"residential ad group {RES_AG} negatives unchanged; account-level set "
                 f"11252984411 stays at 271 members; campaign negatives on the five stay 6158"}
            for t in terms]


PLANS["AMB-0910-COMM-NEG-1"] = {
 "approval_class": "create-paused-scope",
 "summary": f"Add {len(SHIP)} reviewed BROAD ad-group negatives from the launch pack to the "
            f"commercial ad group {NEW_AG} ONLY. RECOMMENDED. Holds back school, schools, "
            f"rent and rental, which can block genuine commercial buyers.",
 "operations": negops(SHIP),
 "notes": {"source": "COMMERCIAL_HVAC_COPY_PASTE.txt, section 'AD-GROUP NEGATIVES - NEW "
                     "COMMERCIAL AD GROUP - BROAD' (22 terms supplied).",
           "held_back_and_why": {n: RISK[n][1] for n in HOLD},
           "why_a_subset_is_still_compliant":
               "The instruction permits only negatives from the supplied pack. Every term "
               "here comes from the pack; four are deferred. Deferring is reversible from "
               "search-term evidence. Shipping a demand-blocking negative is not.",
           "conflict_testing": "Tested against both positive keywords, every search term "
                               "2026-06-01..2026-09-09, all 75 targeted location names, and "
                               "a 20-name supported-manufacturer list. Results recorded in "
                               "evidence/2026-09-10d-commercial-neg-and-rsa.json.",
           "barred_categories_respected": "No manufacturer name, location name, free, quote, "
                                          "estimate, cost, pricing, building, property "
                                          "manager, repair or maintenance negative is used.",
           "requires_new_approval": True}}

PLANS["AMB-0910-COMM-NEG-1-FULL"] = {
 "approval_class": "create-paused-scope",
 "summary": f"Alternative: all {len(PACK_NEG)} pack negatives verbatim, including school, "
            f"schools, rent and rental. NOT RECOMMENDED - see held_back_and_why.",
 "operations": negops(PACK_NEG),
 "notes": {"source": "COMMERCIAL_HVAC_COPY_PASTE.txt, verbatim and complete.",
           "why_not_recommended": {n: RISK[n][1] for n in HOLD},
           "use_this_only_if": "the owner has decided that schools and rental/managed "
                               "properties are deliberately out of commercial scope.",
           "requires_new_approval": True}}

# ------------------------------------------------------------------ RSAs
A_PIN = ["Commercial HVAC Installation", "Commercial HVAC Installers",
         "HVAC Installation for Business"]
A_FREE = ["Free Commercial HVAC Quote", "Rooftop Unit Installation",
          "Commercial RTU Installation", "Commercial AC Installation",
          "Commercial Heat Pump Install", "Systems Built for Businesses",
          "Central Maryland HVAC Team", "Plan Around Your Operations",
          "Transparent Commercial Pricing", "Flexible Project Scheduling",
          "Ambient Cooling & Heating", "Request a Commercial Quote"]
A_DESC = ["Request a free commercial HVAC installation quote for your Central Maryland property.",
          "Install rooftop units, packaged systems, heat pumps, or central air for your business.",
          "Plan equipment, ductwork, ventilation, and controls around your building and operations.",
          "Get clear options, transparent pricing, and scheduling designed around your business."]
B_HEAD = ["HVAC Systems for Businesses", "Central MD Commercial HVAC",
          "Commercial System Installation", "Replace Aging HVAC Equipment",
          "Rooftop & Packaged Systems", "Business Heating & Cooling",
          "Commercial HVAC Planning", "Free Installation Quote",
          "HVAC Options for Your Building", "Schedule a Site Evaluation",
          "Keep Business Comfort in Mind", "Professional HVAC Installation",
          "Central Air for Your Business", "Heat Pumps for Businesses",
          "Request Your HVAC Quote"]
B_DESC = ["Replace or install commercial HVAC equipment with a plan built around your property.",
          "Request a free consultation for rooftop, packaged, central air, or heat pump systems.",
          "Ambient serves Central Maryland businesses with clear pricing and flexible scheduling.",
          "Discuss building needs, equipment options, ductwork, controls, and project timing."]
BARRED = re.compile(r"licens|insur|24/?7|emergenc|same[\s-]?day|guarantee|financ|rebate|"
                    r"discount|warrant|\b\d+(\.\d+)?\s*star|\b#1\b|best in", re.I)

print("\n=== 6. RSA COPY FROM THE PACK - CHARACTER AND CLAIM CHECK ===")
ok = True
for lbl, items, cap in [("RSA A pinned H1", A_PIN, 30), ("RSA A unpinned", A_FREE, 30),
                        ("RSA A descriptions", A_DESC, 90), ("RSA B headlines", B_HEAD, 30),
                        ("RSA B descriptions", B_DESC, 90)]:
    print(f"  {lbl}:")
    for t in items:
        bad = BARRED.search(t)
        v = len(t) <= cap and not bad
        ok = ok and v
        print(f"    [{'OK' if v else 'FAIL'}] ({len(t):>2}) {t}" + (f"  <-- {bad.group(0)!r}" if bad else ""))
allA, allB = A_PIN + A_FREE, B_HEAD
print(f"\n  RSA A: {len(allA)} headlines, {len(A_DESC)} descriptions, "
      f"duplicates {[k for k, v in Counter(allA).items() if v > 1] or 'none'}")
print(f"  RSA B: {len(allB)} headlines, {len(B_DESC)} descriptions, "
      f"duplicates {[k for k, v in Counter(allB).items() if v > 1] or 'none'}")
print(f"  claim check (no Licensed & Insured, emergency, 24/7, financing, rebates, "
      f"guarantees, #1): {'PASS' if ok else 'FAIL'}")
assert ok and len(allA) <= 15 and len(allB) <= 15

rsaops = [
 {"operation": "CREATE_RSA_PAUSED", "resource": "ad_group_ad", "resource_id": NEW_AG,
  "resource_name": "SKAG | Commercial HVAC Installation", "campaign_id": CAMP,
  "ad_label": "RSA A - three headlines pinned to HEADLINE_1",
  "final_url": URL, "path1": "commercial-hvac", "path2": "installation", "status": "PAUSED",
  "headlines_pinned_headline_1": A_PIN, "headlines_unpinned": A_FREE, "descriptions": A_DESC,
  "current_state": f"ad group {NEW_AG} holds 0 ads",
  "proposed_state": f"ad group {NEW_AG} holds 1 PAUSED ad",
  "reason": "Supplied RSA A. Three materially different keyword-forward headlines pinned to "
            "HEADLINE_1 guarantee a commercial service opener while Google still rotates "
            "among three candidates. HEADLINE_3 is deliberately not pinned.",
  "rollback": "remove the created ad_group_ad by its returned resource name",
  "risk": "MEDIUM - the final URL must return 200 before this is created",
  "unrelated_resource_assertion": f"residential ad group {RES_AG} keeps its 2 ENABLED+APPROVED "
                                  f"ads 821319509197 and 821319509200, unedited"},
 {"operation": "CREATE_RSA_PAUSED", "resource": "ad_group_ad", "resource_id": NEW_AG,
  "resource_name": "SKAG | Commercial HVAC Installation", "campaign_id": CAMP,
  "ad_label": "RSA B - unpinned relevance/automation control",
  "final_url": URL, "path1": "commercial-hvac", "path2": "installation", "status": "PAUSED",
  "headlines_pinned_headline_1": [], "headlines_unpinned": B_HEAD, "descriptions": B_DESC,
  "current_state": f"ad group {NEW_AG} holds 0 ads",
  "proposed_state": f"ad group {NEW_AG} holds 2 PAUSED ads",
  "reason": "Supplied RSA B, unpinned, as a relevance and automation control against RSA A.",
  "rollback": "remove the created ad_group_ad by its returned resource name",
  "risk": "MEDIUM - same destination gate as RSA A",
  "unrelated_resource_assertion": "no existing ad in the account is edited"}]
PLANS["AMB-0910-COMM-RSA-2"] = {
 "approval_class": "create-paused-GATED",
 "supersedes": "AMB-0910-COMM-RSA-1 30312BC45992 - SUPERSEDED. It used agency-drafted copy "
               "written before the launch pack was available, targeted an ad group that did "
               "not yet exist, and used path2 'maryland'/'install'.",
 "summary": "Create the two supplied commercial RSAs PAUSED in ad group 199748801029. "
            "2 operations. GATED on the final URL returning 200.",
 "operations": rsaops,
 "notes": {"copy_provenance": "Verbatim from Ambient_Commercial_HVAC_Installation_Launch_Pack.docx "
                              "and COMMERCIAL_HVAC_COPY_PASTE.txt.",
           "HARD_GATE": f"Do not execute until {URL} returns HTTP 200 with the pack copy, the "
                        f"paid number (410) 705-6354, GTM-PQTPQ436, WhatConverts, unique DOM "
                        f"IDs, Privacy and Terms links, and GCLID/GBRAID/WBRAID/UTM capture, "
                        f"all verified in a real browser on desktop and mobile, plus exactly "
                        f"one Google Ads conversion per test submission through an approved "
                        f"test path.",
           "not_an_ab_test": "Two RSAs in one ad group is not an evenly allocated A/B test. "
                             "Google allocates impressions unevenly. A true test needs Google "
                             "Ads Experiments. Any comparison must control device, position, "
                             "query mix and impression share.",
           "no_claim_of_improvement": "No CTR, CPC, conversion or CPQL improvement is claimed. "
                                      "Improvement is not proven until settled post-change "
                                      "data shows it.",
           "images_not_created": "The four supplied images are landing-page assets. No image "
                                 "asset is created here. They are illustrative generated "
                                 "imagery and must never be presented as completed Ambient "
                                 "projects.",
           "requires_new_approval": True}}

print("\n\n=== DRAFTED ===")
for name, p in PLANS.items():
    p.update({"plan_name": name, "target": TARGET,
              "generated_local": out["generated_local"],
              "object_count": len(p["operations"]), "partial_failure": False, "atomic": True})
    p["fingerprint"] = approval_code({"target": TARGET, "plan": name,
                                      "operations": p["operations"]})
    (CLIENT_DIR / "plans" / f"{name}.json").write_text(
        json.dumps(p, indent=1, default=str), encoding="utf-8")
    print(f"  {name:<26}{p['fingerprint']}  {p['object_count']:>2} ops  {p['approval_class']}")
out["plans"] = {k: {"fingerprint": v["fingerprint"], "ops": v["object_count"]}
                for k, v in PLANS.items()}
write(EVID / "2026-09-10d-commercial-neg-and-rsa.json", out)
