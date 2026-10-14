#!/usr/bin/env python3
"""Commercial HVAC Installation build - DRAFTS ONLY, nothing executed.

Three deterministic packages with independent fingerprints, because they have genuinely
different preconditions:
  AMB-0910-COMM-1      ad group + 2 keywords, create-PAUSED. Independent of the landing page.
  AMB-0910-COMM-RSA-1  the 2 RSAs, create-PAUSED. GATED: the final URL is a 404 right now.
  AMB-0910-COMM-XNEG-1 the residential cross-negative. GATED on the commercial group serving.

The supplied launch pack (docx, COPY_PASTE.txt, images/) is NOT present on this machine,
so the RSA copy below is an agency draft written to the stated spec, not the supplied copy.
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
CAMP, RES_AG = "24132507747", "202339087634"
URL = "https://offer.ambientcoolingandheating.com/commercial-hvac-installation/"
AGNAME = "SKAG | Commercial HVAC Installation"

BARRED = re.compile(r"licens|insur|24/?7|emergenc|same[\s-]?day|guarantee|financ|rebate|"
                    r"discount|warrant|\b\d+(\.\d+)?\s*star|\b#1\b|best in|cheapest|"
                    r"lowest price|save \$", re.I)

A_PINNED = ["Commercial HVAC Installation",
            "Commercial HVAC Installers",
            "Commercial HVAC in Maryland"]
A_FREE = ["Rooftop Unit Installation", "Free Commercial HVAC Quote",
          "Serving Central Maryland", "Built for Business Uptime",
          "Office & Retail HVAC", "Request a Site Walkthrough",
          "Talk to a Commercial Tech", "Clear Project Pricing",
          "Multi-Unit HVAC Projects", "New System Installation",
          "Schedule a Site Visit", "HVAC for Your Building"]
A_DESC = [
    "Commercial HVAC installation across Central Maryland. Request a free on-site quote.",
    "Rooftop units and multi-zone installs for offices, retail and light industrial sites.",
    "Talk to a commercial technician about your building. Free quote before any work begins.",
    "Serving Severn, Severna Park, Columbia and nearby Maryland business districts."]

B_HEADLINES = ["Commercial HVAC Installation", "HVAC Install for Business",
               "Commercial HVAC Contractor", "Rooftop HVAC Installation",
               "Office HVAC Installation", "Retail Space HVAC Install",
               "Free On-Site HVAC Quote", "Central Maryland HVAC Team",
               "Built for Business Uptime", "Multi-Zone HVAC Systems",
               "Book a Site Walkthrough", "Commercial HVAC Upgrades",
               "New Commercial HVAC System", "Speak With a Technician",
               "HVAC Projects Done Right"]
B_DESC = [
    "Commercial HVAC installation for Maryland offices, retail and light industrial sites.",
    "Request a free on-site quote and get clear project pricing before work begins.",
    "Rooftop units, split systems and multi-zone installations for commercial buildings.",
    "Serving Severn, Severna Park, Columbia and the surrounding Maryland service area."]


def check(name, items, cap):
    ok = True
    for t in items:
        bad = BARRED.search(t)
        v = len(t) <= cap and not bad
        ok = ok and v
        print(f"    [{'OK' if v else 'FAIL'}] ({len(t):>2}) {t}"
              + (f"   <-- barred claim {bad.group(0)!r}" if bad else ""))
    return ok


print("=== LANDING PAGE GATE ===")
print(f"  {URL}")
print("  measured 2026-09-10: HTTP 404 on the offer subdomain.")
print("  https://ambientcoolingandheating.com/commercial-hvac-installation/ returns 200 but")
print("  renders the generic site shell and the ORGANIC number (410) 761-0932, so it is not")
print("  a usable paid destination either.")
print("  -> RSAs cannot be created against a 404 final URL. COMM-RSA-1 is gated.")

print("\n=== SUPPLIED PACK ===")
for f in ["Ambient_Commercial_HVAC_Installation_Launch_Pack.docx",
          "COMMERCIAL_HVAC_COPY_PASTE.txt", "images/"]:
    print(f"  NOT FOUND on this machine: {f}")
print("  -> RSA copy below is an agency draft to spec, and must be reconciled against the")
print("     supplied pack before it is created.")

print("\n\n=== RSA A (3 headlines pinned to HEADLINE_1) ===")
print("  pinned:")
okA1 = check("A pinned", A_PINNED, 30)
print("  unpinned:")
okA2 = check("A free", A_FREE, 30)
print("  descriptions:")
okA3 = check("A desc", A_DESC, 90)
allA = A_PINNED + A_FREE
print(f"  headlines {len(allA)}/15  descriptions {len(A_DESC)}/4  "
      f"duplicates {[k for k, v in Counter(allA).items() if v > 1] or 'none'}")

print("\n=== RSA B (no pins - relevance/automation control) ===")
okB1 = check("B head", B_HEADLINES, 30)
print("  descriptions:")
okB2 = check("B desc", B_DESC, 90)
print(f"  headlines {len(B_HEADLINES)}/15  descriptions {len(B_DESC)}/4  "
      f"duplicates {[k for k, v in Counter(B_HEADLINES).items() if v > 1] or 'none'}")
CLAIM_OK = all([okA1, okA2, okA3, okB1, okB2])
print(f"\n  claim check across both RSAs (no licence, insurance, 24/7, emergency, same-day,")
print(f"  financing, rebate, discount, warranty, guarantee, rating or #1): "
      f"{'PASS' if CLAIM_OK else 'FAIL'}")
assert CLAIM_OK, "claim check failed - fix copy before drafting"
assert len(allA) <= 15 and len(B_HEADLINES) <= 15

TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "HVAC Installation",
          "related_services": ["AC Repair", "HVAC Repair", "HVAC Replacement",
                               "Gas Boiler Repair", "Commercial HVAC Installation"]}
PLANS = {}

# ------------------------------------------------------------- COMM-1
ops1 = [
 {"operation": "CREATE_AD_GROUP_PAUSED", "resource": "ad_group",
  "campaign_id": CAMP, "campaign": "HVAC Installation",
  "campaign_name": "Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08",
  "resource_name": AGNAME, "ad_group_type": "SEARCH_STANDARD", "status": "PAUSED",
  "cpc_bid_micros": 10000,
  "current_state": f"campaign {CAMP} holds exactly 1 ad group ({RES_AG} "
                   f"'SKAG | HVAC Installation', ENABLED)",
  "proposed_state": f"campaign {CAMP} holds 2 ad groups; the new one is PAUSED and empty of ads",
  "reason": "Commercial HVAC installation is approved paid scope. It needs its own SKAG so "
            "the commercial query, the commercial ad and the commercial destination stay "
            "aligned, instead of routing commercial intent to a residential page.",
  "inherits": "75 Maryland PRESENCE geo targets, the approved ad schedule, conversion "
              "configuration, account tracking template, call asset and the $30.00 "
              "Maximize Clicks ceiling, all from campaign 24132507747. None of these is "
              "modified by this package.",
  "rollback": "remove the created ad_group by its returned resource name",
  "risk": "LOW - created PAUSED with no ads, so it cannot serve",
  "unrelated_resource_assertion":
      f"ad group {RES_AG} must remain ENABLED with its 2 ENABLED+APPROVED RSAs "
      f"(821319509197, 821319509200) and its 2 ENABLED keywords; campaign "
      f"{CAMP} budget stays 176150000 and ceiling stays 30000000"},
]
for mt in ["PHRASE", "EXACT"]:
    ops1.append(
     {"operation": "CREATE_AD_GROUP_KEYWORD", "resource": "ad_group_criterion",
      "ad_group_ref": AGNAME, "campaign_id": CAMP,
      "keyword_text": "commercial hvac installation", "match_type": mt, "status": "ENABLED",
      "current_state": "does not exist",
      "proposed_state": f"{mt} 'commercial hvac installation' ENABLED in the new PAUSED "
                        f"ad group",
      "reason": "The canonical BOFU commercial theme. Phrase and Exact only - no Broad at "
                "launch, per agency policy and the launch instruction.",
      "rollback": "remove the created ad_group_criterion by its returned resource name",
      "risk": "LOW - the parent ad group is PAUSED, so the keyword cannot serve",
      "unrelated_resource_assertion":
          "the 10 serving positive keywords on the five campaigns must be unchanged"})
PLANS["AMB-0910-COMM-1"] = {
 "approval_class": "create-paused",
 "summary": "Create the Commercial HVAC Installation SKAG PAUSED inside the existing HVAC "
            "Installation campaign, with Phrase + Exact 'commercial hvac installation'. "
            "3 operations. No ad is created, nothing is enabled, no separate campaign.",
 "operations": ops1,
 "notes": {
   "no_ad_group_negatives_at_launch":
       "The launch instruction says to add only the reviewed ad-group negatives in the "
       "supplied pack. The pack is not present, so there are none to add. Independently, a "
       "SKAG carrying only Phrase and Exact 'commercial hvac installation' already requires "
       "that contiguous phrase in the query, so speculative negatives would buy little and "
       "risk blocking valid commercial intent. Barred categories are respected either way: "
       "no manufacturer name, city name, free, quote, estimate, cost, pricing, building or "
       "property manager negative is proposed.",
   "commercial_is_not_blocked_anywhere":
       "Verified 2026-09-10: 0 campaign-level negatives containing 'commercial' on 24132507747; "
       "the account-level negative was removed by AMB-0909C-NEG-COMMERCIAL 9F88FEE76803. The 41 "
       "shared-set rows containing 'commercial' are landscaping/tree/masonry BROAD terms in "
       "sets 11807294063 / 11811255121 / 11840874961 / 11840890006, all of which have ZERO "
       "campaign links, and BROAD word-subset matching means none of them could block "
       "'commercial hvac installation' even if attached.",
   "why_paused": "Workflow step 10-11: create paused, read back, then a separate enable "
                 "approval. Enabling additionally requires the landing page to exist.",
   "requires_new_approval": True}}

# ------------------------------------------------------------- COMM-RSA-1
ops2 = [
 {"operation": "CREATE_RSA_PAUSED", "resource": "ad_group_ad", "ad_group_ref": AGNAME,
  "campaign_id": CAMP, "resource_name": "Commercial RSA A - pinned",
  "final_url": URL, "path1": "commercial-hvac", "path2": "maryland", "status": "PAUSED",
  "headlines_pinned_headline_1": A_PINNED, "headlines_unpinned": A_FREE,
  "descriptions": A_DESC,
  "current_state": "the commercial ad group does not exist yet",
  "proposed_state": "one PAUSED RSA with 3 headlines pinned to HEADLINE_1",
  "reason": "Guarantees a commercial service-keyword opener while leaving Google three "
            "candidates to rotate in the most visible slot.",
  "rollback": "remove the created ad_group_ad by its returned resource name",
  "risk": "MEDIUM - the final URL currently returns 404; creating it now would put a "
          "broken destination into policy review",
  "unrelated_resource_assertion": "no existing ad is edited"},
 {"operation": "CREATE_RSA_PAUSED", "resource": "ad_group_ad", "ad_group_ref": AGNAME,
  "campaign_id": CAMP, "resource_name": "Commercial RSA B - unpinned control",
  "final_url": URL, "path1": "commercial-hvac", "path2": "install", "status": "PAUSED",
  "headlines_pinned_headline_1": [], "headlines_unpinned": B_HEADLINES,
  "descriptions": B_DESC,
  "current_state": "the commercial ad group does not exist yet",
  "proposed_state": "one PAUSED RSA with no pins",
  "reason": "Relevance/automation control against RSA A.",
  "rollback": "remove the created ad_group_ad by its returned resource name",
  "risk": "MEDIUM - same 404 destination gate as RSA A",
  "unrelated_resource_assertion": "no existing ad is edited"}]
PLANS["AMB-0910-COMM-RSA-1"] = {
 "approval_class": "create-paused-GATED",
 "summary": "Create the two commercial RSAs PAUSED. 2 operations. GATED: the final URL "
            "returns 404 today.",
 "operations": ops2,
 "notes": {
   "HARD_GATE": f"Do not execute until {URL} returns HTTP 200 with the commercial content, "
                f"the paid number (410) 705-6354, GTM GTM-PQTPQ436, WhatConverts, unique "
                f"DOM ids, and Privacy + Terms links, all verified in a real browser on "
                f"desktop and mobile.",
   "copy_provenance": "AGENCY DRAFT written to the stated spec. The supplied "
                      "Ambient_Commercial_HVAC_Installation_Launch_Pack.docx and "
                      "COMMERCIAL_HVAC_COPY_PASTE.txt are not present on this machine. "
                      "Reconcile against them before creating.",
   "not_an_ab_test": "Two RSAs in one ad group is not an evenly allocated A/B test. Google "
                     "allocates impressions unevenly. A true test needs Google Ads "
                     "Experiments. Any comparison must control device, position, query mix "
                     "and impression share.",
   "images_not_used": "The four supplied images are landing-page assets. No image asset is "
                      "created by this package. Generated images must never be presented as "
                      "completed Ambient projects.",
   "claims_avoided": ["licensed", "insured", "24/7", "emergency", "same-day", "financing",
                      "rebates", "discounts", "warranty", "guarantees",
                      "guaranteed savings", "#1", "ratings", "review counts"],
   "requires_new_approval": True}}

# ------------------------------------------------------------- COMM-XNEG-1
ops3 = [
 {"operation": "ADD_AD_GROUP_NEGATIVE_KEYWORD", "resource": "ad_group_criterion",
  "resource_id": RES_AG, "resource_name": "SKAG | HVAC Installation",
  "campaign_id": CAMP, "keyword_text": "commercial", "match_type": "BROAD",
  "current_state": f"ad group {RES_AG} has no ad-group negative containing 'commercial'",
  "proposed_state": f"BROAD negative 'commercial' on ad group {RES_AG} only",
  "reason": "Routes commercial intent to the new commercial SKAG instead of the residential "
            "one. Scoped to the ad group so it can never suppress the commercial ad group "
            "or any other campaign.",
  "rollback": "remove the created ad_group_criterion by its returned resource name",
  "risk": "MEDIUM - applied before the commercial ad group serves, this would suppress "
          "commercial queries entirely instead of redirecting them",
  "unrelated_resource_assertion":
      "no campaign-level or account-level negative is added; the account-level set "
      "11252984411 must stay at 271 members with 'commercial' absent"}]
PLANS["AMB-0910-COMM-XNEG-1"] = {
 "approval_class": "reversible-GATED",
 "summary": "Add BROAD 'commercial' as an AD-GROUP negative on the residential HVAC "
            "Installation SKAG only. 1 operation.",
 "operations": ops3,
 "notes": {
   "HARD_GATE": "Execute ONLY after the commercial ad group, its destination, its keywords "
                "and its ads are ENABLED and ELIGIBLE. Applying it earlier suppresses "
                "commercial demand rather than redirecting it.",
   "scope": "Ad-group level only. The instruction explicitly forbids a campaign-level or "
            "account-level 'commercial' negative here, and AMB-0909C-NEG-COMMERCIAL "
            "9F88FEE76803 removed the account-level one on 2026-09-10.",
   "requires_new_approval": True}}

print("\n\n=== DRAFTED PACKAGES ===")
for name, p in PLANS.items():
    p.update({"plan_name": name, "target": TARGET,
              "generated_local": datetime.datetime.now(TZ).isoformat(),
              "object_count": len(p["operations"]), "partial_failure": False, "atomic": True})
    p["fingerprint"] = approval_code({"target": TARGET, "plan": name,
                                      "operations": p["operations"]})
    (CLIENT_DIR / "plans" / f"{name}.json").write_text(
        json.dumps(p, indent=1, default=str), encoding="utf-8")
    gate = "  GATED" if "GATED" in p["approval_class"] else ""
    print(f"  {name:<24}{p['fingerprint']}  {p['object_count']} ops  "
          f"{p['approval_class']}{gate}")
print("\n  none of these has been executed or validated against the API by this script.")
