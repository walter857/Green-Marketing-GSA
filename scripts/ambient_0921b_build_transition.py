#!/usr/bin/env python3
"""Ambient | 2026-09-21b | Build the 31-service heating transition plans. LOCAL DRAFT ONLY.

EXTERNAL WRITES: 0. Produces four fingerprinted plans:

  AMB-0921B-HEAT-BUILD-1   create-paused: 4 new campaigns, 27 new ad groups, keywords,
                           RSAs, cross-negatives, assets; 1 ad-group rename
  AMB-0921B-BUDGET-1       budget reallocation to the transition end state
  AMB-0921B-BID-1          evidence-based CPC bid ceilings
  AMB-0921B-COOLPAUSE-1    residential cooling pause, ad-group level, rollback inventory

Nothing here is executed and nothing is enabled. The cooling pause is a SEPARATE plan
because it must not run until heating is proven able to serve.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

STAMP = "2026-09-21b"
CAP_DAY, CAP_MONTH, WORKING_TARGET = 328.94, 10000.00, 325.00

# ---------------------------------------------------------------- destinations
U_FURNACE_REPAIR = "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/"
U_HEATING_HUB = "https://ambientcoolingandheating.com/services/heating-services/"
U_BOILER_REPAIR = "https://ambientcoolingandheating.com/services/heating-services/boiler-repair/"
U_GAS_BOILER = "https://offer.ambientcoolingandheating.com/gas-boiler-repair/"
U_HEAT_PUMPS = "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/"
U_MINI_SPLITS = "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/"
U_GEOTHERMAL = "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/"

# Page-support evidence, measured 2026-09-21 (snapshots/lp-discovery-2026-09-21b.json).
# Counts are body-text matches with the site-wide nav/footer baseline subtracted
# (nav contributes furnace 6, heat_pump 5, boiler 4, ductless 4, geothermal 4).
PAGE_SUPPORT = {
    U_FURNACE_REPAIR: {"furnace": 18, "repair": 21, "replace": 10, "install": 5,
                       "maintenance": 3, "tune_up": 0, "gas": 0, "electric": 0,
                       "h2": "Timely Furnace Repair and Maintenance Services / "
                             "Trusted Furnace Repair and Replacement"},
    U_HEATING_HUB: {"repair": 12, "replace": 6, "install": 7, "maintenance": 7,
                    "tune_up": 2, "inspection": 1, "emergency": 1, "thermostat": 1,
                    "h2": "Heating Services from Professionals You Can Trust / "
                          "Comprehensive Heating Services and Maintenance Plans"},
    U_BOILER_REPAIR: {"boiler": 19, "repair": 29, "replace": 5, "install": 5,
                      "maintenance": 2,
                      "h2": "Expert Boiler Repair to Get You Back in Business"},
    U_GAS_BOILER: {"boiler": 50, "gas": 37, "repair": 37, "emergency": 3,
                   "h2": "Common Signs You May Need Gas Boiler Repair"},
    U_HEAT_PUMPS: {"heat_pump": 22, "install": 8, "maintenance": 4, "repair": 10,
                   "replace": 5, "h2": "Comprehensive Heat Pump Installation Services"},
    U_MINI_SPLITS: {"ductless": 16, "install": 12, "repair": 11, "maintenance": 3,
                    "replace": 5,
                    "h2": "Comprehensive Installation and Maintenance Services"},
    U_GEOTHERMAL: {"geothermal": 16, "install": 11, "repair": 12, "maintenance": 3,
                   "h2": "Energy-Efficient Heating and Cooling with Geothermal HVAC"},
}

BLOCKED_DEST = {
    U_HEAT_PUMPS: "DESTINATION_NOT_WORKING - 0/3 validate_only trials 2026-09-21, while "
                  "8 other Ambient destinations passed 3/3 with the IDENTICAL ad body. "
                  "URL-specific, not ad copy and not account-wide. No RSA may be created "
                  "against it: the API rejects the ad and would abort the batch.",
}

# --------------------------------------------------------------- RSA copy blocks
# Every line below is supported by its own landing page. No barred claim appears:
# no same-day, 24/7, emergency promise, guarantee, licensed/insured, best/top/most
# trusted, free estimate, rating or review count, financing, or phone number.
def rsa(h, d, label):
    return {"label": label, "h": h, "d": d}


AG = {}


def ag(name, campaign_key, url, cpc_bid, phrase, exact, evidence, rsas=None,
       existing_ad_group_id=None, rename_from=None, page_verdict="ADEQUATE",
       launch_gate=None, services_covered=None, remove_keywords=None):
    AG[name] = {"campaign_key": campaign_key, "url": url, "cpc_bid": cpc_bid,
                "phrase": phrase, "exact": exact, "evidence": evidence,
                "rsas": rsas or [], "existing_ad_group_id": existing_ad_group_id,
                "rename_from": rename_from, "page_verdict": page_verdict,
                "launch_gate": launch_gate,
                "remove_keywords": remove_keywords or [],
                "services_covered": services_covered or [name.split("| ")[-1]]}


# ============================ CAMPAIGN 1 - Heating and Furnace Repair ==========
ag("SKAG | Furnace Repair", "C1_REPAIR", U_FURNACE_REPAIR, 42.00,
   [], [],  # existing ad group, keywords already live and audited - not re-added
   "EXISTING ad group 199797580706, built 2026-09-17, 10 keywords APPROVED/ELIGIBLE and "
   "2 RSAs APPROVED/REVIEWED. Reused, not recreated. Account search-term history: "
   "$2,084.77 / 50 clicks / 5 conversions, CPC $41.70, CPA $416.95. "
   "CHANGE REQUIRED: this ad group already carries 'gas furnace repair' in PHRASE and "
   "EXACT. The new scope gives Gas Furnace Repair its own SKAG, so those two keywords "
   "must move, not be duplicated. They are REMOVED here and recreated in "
   "'SKAG | Gas Furnace Repair'. Without this the 'gas' cross-negative would block this "
   "ad group's own live keyword and the two ad groups would compete for one query.",
   existing_ad_group_id="199797580706", services_covered=["Furnace Repair"],
   remove_keywords=[("gas furnace repair", "PHRASE"), ("gas furnace repair", "EXACT")])

ag("SKAG | Heating Repair", "C1_REPAIR", U_HEATING_HUB, 42.00,
   ["heating repair", "heater repair"],
   ["heating repair", "heater repair", "heating repair service",
    "residential heating repair"],
   "The single largest converting heating theme in the account: $14,662.48 / 1,416 clicks / "
   "34 conversions, CPC $10.35, CPA $431.25. Campaign-level view agrees "
   "(heating_generic|repair CPA $265.66 on 42 conversions).",
   rsas=[
     rsa(["Heating Repair Central MD", "Heating Repair in Severn", "Severna Park Heating",
          "Columbia MD Heating Repair", "Book A Heating Repair", "Heating Repair Near You",
          "Local Heating Technicians", "Heating System Repair", "Schedule A Repair Visit",
          "Trained HVAC Technicians", "Maryland Heating Repair", "Request Heating Repair",
          "Home Heating Repair", "Talk To A Technician", "Heating Service Central MD"],
         ["Heating repair for homes across Severn, Severna Park and Columbia, Maryland.",
          "Our technicians diagnose the fault and explain your options clearly.",
          "Book a heating repair visit with Ambient Cooling and Heating.",
          "Serving Central Maryland with professional heating services."],
         "RSA A - service and location led"),
     rsa(["Heating Not Working?", "Heat Running But Cold?", "Heating System Faulty?",
          "Get Your Heating Checked", "Heating Repair Near You", "Central Maryland Heating",
          "Heating Repair Specialists", "Severn Heating Repair", "Book A Heating Visit",
          "Talk To A Technician", "We Repair Home Heating", "Clear Repair Options",
          "Request Heating Service", "Columbia Heating Service", "Anne Arundel Heating"],
         ["Heating trouble in Severn, Severna Park or Columbia? Our technicians help.",
          "We diagnose the problem and walk you through the repair options.",
          "Heating repair for Maryland homes and commercial properties.",
          "Schedule a heating repair appointment with Ambient today."],
         "RSA B - problem led")],
   services_covered=["Heating Repair"])

ag("SKAG | Emergency Heating Repair", "C1_REPAIR", None, 42.00,
   ["emergency heating repair", "emergency heater repair"],
   ["emergency heating repair", "emergency heat repair", "emergency furnace repair"],
   "Account search-term history: $881.40 / 52 clicks / 1 conversion, CPC $16.95. Real "
   "demand exists, but no page supports an emergency promise and answering/dispatch hours "
   "are NOT verified in client.yaml.",
   page_verdict="NO PAGE",
   launch_gate="DOUBLE GATE. (1) No landing page supports emergency intent - the heating "
               "hub mentions 'emergency' once. (2) client.yaml records "
               "call_answering_hours_confirmed: false and can_answer_after_hours: null, "
               "and campaigns run Mon-Fri 08:00-20:00 + Sat 08:00-13:00, so the service "
               "cannot be promised outside those hours. No RSA is drafted: emergency copy "
               "would be an unverified availability claim, which is barred.",
   services_covered=["Emergency Heating Repair"])

ag("SKAG | No Heat Repair", "C1_REPAIR", None, 42.00,
   ["no heat repair", "no heat service"],
   ["no heat repair", "house has no heat"],
   "Account search-term history: 28 distinct terms, 0 clicks, 0 conversions. Demand is "
   "real but unbought. Same availability concern as emergency: a 'no heat' searcher "
   "expects a fast visit. "
   "DROPPED 2026-09-21: EXACT [no heat in house] was rejected by validate_only under "
   "GENERAL_DATING_AND_COMPANIONSHIP - a false positive from Google's classifier on an "
   "HVAC term. It is flagged exemptible, but [house has no heat] carries the same query "
   "intent and passes cleanly, so the keyword was dropped rather than an exemption filed.",
   page_verdict="NO PAGE",
   launch_gate="No landing page supports no-heat intent. No RSA drafted - copy cannot be "
               "verified against a page that does not exist.",
   services_covered=["No Heat Repair"])

ag("SKAG | Gas Furnace Repair", "C1_REPAIR", U_FURNACE_REPAIR, 42.00,
   ["gas furnace repair"], ["gas furnace repair"],
   "Account search-term history: $90.18 / 8 clicks / 0 conversions, CPC $11.27. The "
   "furnace-repair page supports furnace repair (repair 21, furnace 18) but never says "
   "'gas'. Acceptable because the service is furnace repair and fuel type is a qualifier, "
   "not a different service - but a fuel-specific page would match better.",
   page_verdict="ADEQUATE WITH CAVEAT",
   rsas=[
     rsa(["Gas Furnace Repair", "Gas Furnace Repair Severn", "Severna Park Gas Furnace",
          "Columbia Gas Furnace", "Book A Furnace Repair", "Furnace Repair Near You",
          "Gas Furnace Technicians", "Central Maryland Furnace", "Schedule A Repair Visit",
          "Trained HVAC Technicians", "Maryland Furnace Repair", "Request Furnace Repair",
          "Home Furnace Repair", "Talk To A Technician", "Furnace Repair Central MD"],
         ["Gas furnace repair for homes in Severn, Severna Park and Columbia, Maryland.",
          "Our technicians diagnose the fault and explain your options clearly.",
          "Book a furnace repair visit with Ambient Cooling and Heating.",
          "Serving Central Maryland with professional furnace repair."],
         "RSA A - service led"),
     rsa(["Gas Furnace Not Working?", "Furnace Blowing Cold Air?", "Furnace Cutting Out?",
          "Get Your Furnace Checked", "Gas Furnace Repair Near You", "Severn Furnace Repair",
          "Furnace Repair Specialists", "Central Maryland Furnace", "Book A Furnace Visit",
          "Talk To A Technician", "We Repair Gas Furnaces", "Clear Repair Options",
          "Request Furnace Service", "Columbia Furnace Repair", "Anne Arundel Furnace"],
         ["Gas furnace trouble in Severn, Severna Park or Columbia? Our technicians help.",
          "We diagnose the problem and walk you through the repair options.",
          "Furnace repair for Maryland homes and commercial properties.",
          "Schedule a furnace repair appointment with Ambient today."],
         "RSA B - problem led")],
   services_covered=["Gas Furnace Repair"])

ag("SKAG | Electric Furnace Repair", "C1_REPAIR", U_FURNACE_REPAIR, 42.00,
   ["electric furnace repair"], ["electric furnace repair"],
   "Account search-term history: $47.64 / 3 clicks / 0 conversions, CPC $15.88. NOTE: "
   "client.yaml lists 'Electric furnace repair' under services_capability_not_verified. "
   "The 2026-09-21 instruction places it in advertising scope, which supersedes that flag, "
   "but the capability itself has still not been independently verified and the page never "
   "says 'electric'.",
   page_verdict="ADEQUATE WITH CAVEAT",
   launch_gate="Confirm Ambient services electric furnaces before enabling. The scope "
               "instruction authorises advertising it; it does not verify the capability.",
   rsas=[
     rsa(["Electric Furnace Repair", "Electric Furnace Severn", "Severna Park Furnace",
          "Columbia Furnace Repair", "Book A Furnace Repair", "Furnace Repair Near You",
          "Electric Furnace Service", "Central Maryland Furnace", "Schedule A Repair Visit",
          "Trained HVAC Technicians", "Maryland Furnace Repair", "Request Furnace Repair",
          "Home Furnace Repair", "Talk To A Technician", "Furnace Repair Central MD"],
         ["Electric furnace repair for homes in Severn, Severna Park and Columbia, MD.",
          "Our technicians diagnose the fault and explain your options clearly.",
          "Book a furnace repair visit with Ambient Cooling and Heating.",
          "Serving Central Maryland with professional furnace repair."],
         "RSA A - service led"),
     rsa(["Electric Furnace Faulty?", "Furnace Blowing Cold Air?", "Furnace Cutting Out?",
          "Get Your Furnace Checked", "Furnace Repair Near You", "Severn Furnace Repair",
          "Furnace Repair Specialists", "Central Maryland Furnace", "Book A Furnace Visit",
          "Talk To A Technician", "We Repair Electric Furnaces", "Clear Repair Options",
          "Request Furnace Service", "Columbia Furnace Repair", "Anne Arundel Furnace"],
         ["Electric furnace trouble in Severn, Severna Park or Columbia? We can help.",
          "We diagnose the problem and walk you through the repair options.",
          "Furnace repair for Maryland homes and commercial properties.",
          "Schedule a furnace repair appointment with Ambient today."],
         "RSA B - problem led")],
   services_covered=["Electric Furnace Repair"])

# ==================== CAMPAIGN 2 - Heat Pump and Ductless Heating =============
for _n, _kwp, _kwe, _ev in [
    ("Heat Pump Repair", ["heat pump repair"],
     ["heat pump repair", "heat pump not heating", "heat pump service"],
     "Account search-term history: $1,088.79 / 43 clicks / 0 conversions, CPC $25.32. "
     "Campaign view: heat_pump|repair CPC $9.46, 3 conversions, CPA $365.93."),
    ("Heat Pump Replacement", ["heat pump replacement"],
     ["heat pump replacement", "replace heat pump"],
     "Account search-term history: 30 terms, 2 clicks, 1 conversion on $6.27."),
    ("Heat Pump Installation", ["heat pump installation"],
     ["heat pump installation", "heat pump installers near me"],
     "Campaign view: heat_pump|installation $6,128.74 / 397 clicks / 16 conversions, "
     "CPC $15.44, CPA $383.05 - the strongest heat-pump intent in the account."),
    ("Heat Pump Maintenance", ["heat pump maintenance"],
     ["heat pump maintenance", "heat pump tune up"],
     "Campaign view: heat_pump|maintenance CPA $185.85 on 7 conversions - the BEST "
     "measured CPA of any heating intent in this account."),
]:
    ag(f"SKAG | {_n}", "C2_HEATPUMP", U_HEAT_PUMPS, 35.00, _kwp, _kwe, _ev,
       page_verdict="DESTINATION BLOCKED",
       launch_gate="Heat Pump page fails Google's destination check. Ad group and keywords "
                   "are created PAUSED so the structure exists, but NO RSA is included - "
                   "the API rejects any ad pointing at this URL and would abort the batch. "
                   "An ad group with no ads cannot serve. Do not substitute another URL.",
       services_covered=[_n])

ag("SKAG | Ductless Heating Repair", "C2_HEATPUMP", U_MINI_SPLITS, 35.00,
   ["ductless heating repair", "mini split repair"],
   ["ductless repair", "mini split repair", "ductless heating repair"],
   "Account search-term history: $838.66 / 36 clicks / 3 conversions, CPC $23.30, "
   "CPA $279.55 - one of the better heating CPAs. The mini-splits page carries repair "
   "content (repair 11, ductless 16), not installation only.",
   rsas=[
     rsa(["Ductless Heating Repair", "Mini Split Repair Severn", "Severna Park Mini Split",
          "Columbia Ductless Repair", "Book A Ductless Repair", "Ductless Repair Near You",
          "Mini Split Technicians", "Central Maryland Ductless", "Schedule A Repair Visit",
          "Trained HVAC Technicians", "Maryland Mini Split Help", "Request Ductless Repair",
          "Home Ductless Repair", "Talk To A Technician", "Ductless Repair Central MD"],
         ["Ductless and mini split repair across Severn, Severna Park and Columbia, MD.",
          "Our technicians diagnose the fault and explain your options clearly.",
          "Book a ductless repair visit with Ambient Cooling and Heating.",
          "Serving Central Maryland with professional mini split service."],
         "RSA A - service led"),
     rsa(["Mini Split Not Heating?", "Ductless Unit Faulty?", "Mini Split Leaking?",
          "Get Your Ductless Checked", "Ductless Repair Near You", "Severn Ductless Repair",
          "Mini Split Specialists", "Central Maryland Ductless", "Book A Ductless Visit",
          "Talk To A Technician", "We Repair Mini Splits", "Clear Repair Options",
          "Request Ductless Service", "Columbia Mini Split Help", "Anne Arundel Ductless"],
         ["Mini split trouble in Severn, Severna Park or Columbia? Our technicians help.",
          "We diagnose the problem and walk you through the repair options.",
          "Ductless heating repair for Maryland homes and businesses.",
          "Schedule a ductless repair appointment with Ambient today."],
         "RSA B - problem led")],
   services_covered=["Ductless Heating Repair"])

# ========== CAMPAIGN 3 - Heating and Furnace Installation and Replacement =====
ag("SKAG | Furnace Replacement", "C3_INSTALL", U_FURNACE_REPAIR, 46.00,
   ["furnace replacement"], ["furnace replacement", "replace furnace", "new furnace cost"],
   "Account search-term history: $321.79 / 7 clicks / 0 conversions, CPC $45.97. The "
   "furnace-repair page carries an explicit replacement H2 ('Trusted Furnace Repair and "
   "Replacement') and 10 replacement mentions, so it genuinely supports this intent.",
   page_verdict="ADEQUATE",
   rsas=[
     rsa(["Furnace Replacement", "Replace Your Furnace", "Furnace Replacement Severn",
          "Severna Park Furnace", "Columbia MD Furnace", "New Furnace Assessment",
          "Furnace Replacement Quote", "Central Maryland Furnace", "Book An Assessment",
          "Trained HVAC Technicians", "Maryland Furnace Service", "Request Replacement Info",
          "Plan Your Replacement", "Talk To A Technician", "Furnace Replacement Central MD"],
         ["Furnace replacement for homes in Severn, Severna Park and Columbia, Maryland.",
          "We assess your current furnace and explain the replacement options.",
          "Book a furnace assessment with Ambient Cooling and Heating.",
          "Serving Central Maryland with professional furnace replacement."],
         "RSA A - service led"),
     rsa(["Furnace Near The End?", "Old Furnace Failing?", "Repair Or Replace?",
          "Upgrade Your Furnace", "Furnace Replacement Quote", "Severn Furnace Help",
          "Furnace Specialists", "Central Maryland Furnace", "Book An Assessment",
          "Talk To A Technician", "Plan The Replacement", "Clear Replacement Options",
          "Request An Assessment", "Columbia Furnace Help", "Warm Home This Winter"],
         ["An ageing furnace gives little warning. Plan the replacement early.",
          "We assess your current furnace and set out the replacement options.",
          "Furnace replacement across Severn, Severna Park and Columbia homes.",
          "Schedule a furnace assessment with Ambient today."],
         "RSA B - problem led")],
   services_covered=["Furnace Replacement"])

ag("SKAG | Furnace Installation", "C3_INSTALL", None, 46.00,
   ["furnace installation"], ["furnace installation", "furnace installers near me"],
   "Account search-term history: $317.74 / 7 clicks / 0 conversions, CPC $45.39.",
   page_verdict="INSUFFICIENT PAGE",
   launch_gate="The furnace-repair page mentions installation 5 times and has no "
               "installation section or heading. Sending installation traffic there is "
               "exactly the mismatch the instruction forbids. No RSA drafted - copy cannot "
               "be verified against a page that does not exist.",
   services_covered=["Furnace Installation"])

ag("SKAG | Heating Replacement", "C3_INSTALL", None, 46.00,
   ["heating replacement", "heating system replacement"],
   ["heating replacement", "heating system replacement", "replace heating system"],
   "Account search-term history: Heating Replacement $215.27 / 15 clicks / 0 conversions, "
   "CPC $14.35; Heating System Replacement 2 terms, no clicks. Covers BOTH requested "
   "service labels in one ad group, as instructed, because they are close variants that "
   "Google groups into one demand bucket.",
   page_verdict="INSUFFICIENT PAGE",
   launch_gate="The heating hub mentions replacement 6 times with no replacement section. "
               "No RSA drafted.",
   services_covered=["Heating Replacement", "Heating System Replacement"])

ag("SKAG | Heating Installation", "C3_INSTALL", None, 46.00,
   ["heating installation", "heating system installation"],
   ["heating installation", "heating system installation"],
   "Account search-term history: Heating Installation $857.15 / 51 clicks / 2 conversions, "
   "CPC $16.81, CPA $428.57; Heating System Installation 4 terms, no clicks. Covers BOTH "
   "requested labels in one ad group.",
   page_verdict="INSUFFICIENT PAGE",
   launch_gate="The heating hub mentions installation 7 times with no installation "
               "section. No RSA drafted.",
   services_covered=["Heating Installation", "Heating System Installation"])

ag("SKAG | Ductless Heating Installation", "C3_INSTALL", U_MINI_SPLITS, 46.00,
   [], [],
   "RENAME of existing ad group 199797580746 'SKAG | Mini Split Installation', built "
   "2026-09-17 with 8 keywords and 2 APPROVED RSAs. Renamed rather than duplicated, as "
   "instructed. NOTE: Google Ads cannot move an ad group between campaigns, so it stays in "
   "campaign 24257819466 (Campaign 3) rather than moving to Campaign 2. That is the right "
   "home anyway - it is an installation ad group in the installation campaign. Account "
   "history: $461.79 / 18 clicks / 0 conversions, CPC $25.66.",
   existing_ad_group_id="199797580746",
   rename_from="SKAG | Mini Split Installation",
   services_covered=["Ductless Heating Installation"])

# ========================= CAMPAIGN 4 - Boiler Services =======================
ag("SKAG | Gas Boiler Repair", "C4_BOILER", U_GAS_BOILER, 60.00, [], [],
   "EXISTING ad group 202339087594 on the live boiler campaign. 2 keywords "
   "APPROVED/ELIGIBLE, 2 ENABLED APPROVED RSAs (plus 2 older PAUSED RSAs disapproved for "
   "CONSUMER_FINANCE, left untouched). Reused, not recreated.",
   existing_ad_group_id="202339087594", services_covered=["Gas Boiler Repair"])

ag("SKAG | Boiler Repair", "C4_BOILER", U_BOILER_REPAIR, 60.00,
   ["boiler repair"],
   ["boiler repair", "residential boiler repair", "commercial boiler repair"],
   "Account search-term history: $5,219.83 / 88 clicks / 12.33 conversions, CPC $59.32, "
   "CPA $423.34 - the second largest converting heating theme. The boiler-repair page is "
   "strongly repair-weighted (repair 29, boiler 19) and explicitly serves businesses "
   "('Expert Boiler Repair to Get You Back in Business'), which supports the commercial "
   "EXACT variant.",
   rsas=[
     rsa(["Boiler Repair in Severn", "Boiler Repair Central MD", "Severna Park Boiler Repair",
          "Columbia MD Boiler Repair", "Residential Boiler Repair", "Commercial Boiler Repair",
          "Boiler Repair Technicians", "Book a Boiler Repair Visit", "Maryland Boiler Repair",
          "Boiler Diagnosis Explained", "Schedule Boiler Service", "Homes and Businesses",
          "Trained HVAC Technicians", "Boiler Service Central MD", "Request Boiler Repair"],
         ["Boiler repair for homes and businesses in Severn, Severna Park and Columbia.",
          "Our technicians diagnose the fault and explain your options clearly.",
          "Book a boiler repair visit with Ambient Cooling and Heating.",
          "Serving Central Maryland with professional boiler repair."],
         "RSA A - service led"),
     rsa(["Boiler Stopped Working?", "No Heat From Your Boiler?", "Boiler Leaking or Faulty?",
          "Get Your Boiler Looked At", "Boiler Repair Near You", "Central Maryland Boilers",
          "Boiler Repair Specialists", "Severn Boiler Repair", "Book a Boiler Inspection",
          "Talk to a Technician", "We Repair Home Boilers", "We Repair Business Boilers",
          "Clear Repair Options", "Request Boiler Service", "Columbia Boiler Service"],
         ["Boiler trouble in Severn, Severna Park or Columbia? Our technicians help.",
          "We diagnose the problem and walk you through the repair options.",
          "Boiler repair for Maryland homes and commercial properties.",
          "Schedule a boiler repair appointment with Ambient today."],
         "RSA B - problem led")],
   services_covered=["Boiler Repair"])

for _n, _kwp, _kwe, _ev in [
    ("Boiler Replacement", ["boiler replacement"],
     ["boiler replacement", "replace boiler", "new boiler cost"],
     "Account search-term history: $221.75 / 7 clicks / 0 conversions, CPC $31.68."),
    ("Boiler Installation", ["boiler installation"],
     ["boiler installation", "boiler installers near me"],
     "Account search-term history: $95.51 / 2 clicks / 0 conversions, CPC $47.76. "
     "Campaign view: boiler|installation CPA $315.24 on 6 conversions."),
    ("Boiler Maintenance", ["boiler maintenance", "boiler service"],
     ["boiler maintenance", "boiler service"],
     "Account search-term history: $2,102.23 / 28 clicks / 4 conversions, CPC $75.08, "
     "CPA $525.56 - the most expensive heating clicks in the account."),
]:
    ag(f"SKAG | {_n}", "C4_BOILER", None, 60.00, _kwp, _kwe, _ev,
       page_verdict="INSUFFICIENT PAGE",
       launch_gate="The boiler-repair page is repair-weighted (repair 29) with only 5 "
                   "replacement, 5 installation and 2 maintenance mentions and no section "
                   "for any of them. The instruction explicitly forbids sending Boiler "
                   "Installation traffic to a repair-only page. No RSA drafted.",
       services_covered=[_n])

# ============== CAMPAIGN 5 - Heating Maintenance and Inspection ===============
ag("SKAG | Furnace Maintenance", "C5_MAINT", U_FURNACE_REPAIR, 32.00,
   ["furnace maintenance"], ["furnace maintenance", "furnace cleaning"],
   "Account search-term history: $2,554.67 / 48 clicks / 7 conversions, CPC $53.22, "
   "CPA $364.95. Campaign view: furnace|maintenance CPA $230.31 - among the best in the "
   "account. The furnace page carries an explicit maintenance H2 ('Timely Furnace Repair "
   "and Maintenance Services').",
   page_verdict="ADEQUATE",
   rsas=[
     rsa(["Furnace Maintenance", "Furnace Maintenance Severn", "Severna Park Furnace Care",
          "Columbia Furnace Service", "Book Furnace Maintenance", "Furnace Care Near You",
          "Furnace Service Visit", "Central Maryland Furnace", "Schedule A Service Visit",
          "Trained HVAC Technicians", "Maryland Furnace Care", "Request Furnace Service",
          "Home Furnace Maintenance", "Talk To A Technician", "Furnace Care Central MD"],
         ["Furnace maintenance for homes in Severn, Severna Park and Columbia, Maryland.",
          "Our technicians check the system and explain what it needs.",
          "Book a furnace maintenance visit with Ambient Cooling and Heating.",
          "Serving Central Maryland with professional furnace maintenance."],
         "RSA A - service led"),
     rsa(["Furnace Due A Service?", "Keep Your Furnace Running", "Before The Cold Arrives",
          "Book Furnace Maintenance", "Furnace Care Near You", "Severn Furnace Service",
          "Furnace Care Specialists", "Central Maryland Furnace", "Book A Service Visit",
          "Talk To A Technician", "Planned Furnace Care", "Clear Service Options",
          "Request A Service Visit", "Columbia Furnace Care", "Warm Home This Winter"],
         ["A furnace checked before winter is less likely to fail during it.",
          "We inspect the system and set out anything that needs attention.",
          "Furnace maintenance across Severn, Severna Park and Columbia homes.",
          "Schedule a furnace maintenance visit with Ambient today."],
         "RSA B - seasonal led")],
   services_covered=["Furnace Maintenance"])

ag("SKAG | Heating Maintenance", "C5_MAINT", U_HEATING_HUB, 32.00,
   ["heating maintenance"], ["heating maintenance", "heating system maintenance"],
   "Account search-term history: $1,816.70 / 273 clicks / 2 conversions, CPC $6.65, "
   "CPA $908.35 - cheap clicks, weak conversion. The heating hub carries an explicit "
   "maintenance H2 ('Comprehensive Heating Services and Maintenance Plans', 7 mentions).",
   page_verdict="ADEQUATE",
   rsas=[
     rsa(["Heating Maintenance", "Heating Care Severn MD", "Severna Park Heating Care",
          "Columbia Heating Service", "Book Heating Maintenance", "Heating Care Near You",
          "Heating Service Visit", "Central Maryland Heating", "Schedule A Service Visit",
          "Trained HVAC Technicians", "Maryland Heating Care", "Request Heating Service",
          "Home Heating Maintenance", "Talk To A Technician", "Heating Care Central MD"],
         ["Heating maintenance for homes in Severn, Severna Park and Columbia, Maryland.",
          "Our technicians check the system and explain what it needs.",
          "Book a heating maintenance visit with Ambient Cooling and Heating.",
          "Serving Central Maryland with professional heating maintenance."],
         "RSA A - service led"),
     rsa(["Heating Due A Service?", "Keep Your Heating Running", "Before The Cold Arrives",
          "Book Heating Maintenance", "Heating Care Near You", "Severn Heating Service",
          "Heating Care Specialists", "Central Maryland Heating", "Book A Service Visit",
          "Talk To A Technician", "Planned Heating Care", "Clear Service Options",
          "Request A Service Visit", "Columbia Heating Care", "Warm Home This Winter"],
         ["A heating system checked before winter is less likely to fail during it.",
          "We inspect the system and set out anything that needs attention.",
          "Heating maintenance across Severn, Severna Park and Columbia homes.",
          "Schedule a heating maintenance visit with Ambient today."],
         "RSA B - seasonal led")],
   services_covered=["Heating Maintenance"])

for _n, _kwp, _kwe, _ev in [
    ("Furnace Tune-Up", ["furnace tune up"], ["furnace tune up"],
     "Account search-term history: $40.21 / 2 clicks / 0 conversions, CPC $20.11."),
    ("Heating Tune-Up", ["heating tune up"], ["heating tune up"],
     "Account search-term history: 11 terms, 0 clicks, 0 conversions."),
    ("Heating System Inspection", ["heating system inspection", "heating inspection"],
     ["heating system inspection", "heating inspection"],
     "Account search-term history: 5 terms, 0 clicks, 0 conversions."),
]:
    ag(f"SKAG | {_n}", "C5_MAINT", None, 32.00, _kwp, _kwe, _ev,
       page_verdict="INSUFFICIENT PAGE",
       launch_gate="No page carries tune-up or inspection content: the heating hub "
                   "mentions tune-up twice and inspection once, with no section for "
                   "either. Kept separate from Maintenance for ad relevance as instructed, "
                   "which makes a dedicated page necessary. No RSA drafted.",
       services_covered=[_n])

# ======================== CAMPAIGN 6 - Thermostat Services ====================
for _n, _kwp, _kwe, _ev in [
    ("Thermostat Repair", ["thermostat repair"], ["thermostat repair"],
     "Account search-term history: $17.16 / 1 click / 0 conversions, CPC $17.16. "
     "Planner sample: ~30 searches/month."),
    ("Thermostat Replacement", ["thermostat replacement"],
     ["thermostat replacement", "replace thermostat"],
     "Account search-term history: 11 terms, 0 clicks, 0 conversions."),
    ("Smart Thermostat Installation", ["smart thermostat installation"],
     ["smart thermostat installation", "nest thermostat installation"],
     "Account search-term history: $14.28 / 1 click / 0 conversions, CPC $14.28."),
]:
    ag(f"SKAG | {_n}", "C6_THERMOSTAT", None, 20.00, _kwp, _kwe, _ev,
       page_verdict="NO PAGE",
       launch_gate="NO page on either domain mentions thermostat work beyond a single "
                   "passing reference on the heating hub. ALSO: client.yaml records "
                   "'Thermostat repair', 'Thermostat replacement' and 'Smart thermostat "
                   "installation' under services_capability_not_verified. The scope "
                   "instruction authorises advertising them but does not verify the "
                   "capability. No RSA drafted.",
       services_covered=[_n])

# ======================= CAMPAIGN 7 - Geothermal Heat Pump ====================
ag("SKAG | Geothermal Heat Pump", "C7_GEO", U_GEOTHERMAL, 38.00,
   ["geothermal heat pump", "geothermal heating"],
   ["geothermal heat pump", "geothermal heating", "geothermal installation"],
   "CONTROLLED TEST. IMPORTANT CORRECTION TO THE STATED PREMISE: the instruction says "
   "geothermal shows 'spend with no confirmed conversions'. That is true of campaigns "
   "NAMED geothermal ($151.80 / 4 clicks / 0 conversions). But geothermal SEARCH TERMS, "
   "wherever they were served, show $1,310.03 / 59 clicks / 4 conversions, CPC $22.20, "
   "CPA $327.51 - better than the account's heating average. Kept as a controlled test as "
   "instructed, with a stop-loss, but the evidence is stronger than the premise assumed.",
   rsas=[
     rsa(["Geothermal Heat Pumps", "Geothermal HVAC Install", "Severn Geothermal HVAC",
          "Severna Park Geothermal", "Columbia MD Geothermal", "Geothermal Installation",
          "Ground Source Heat Pumps", "Central Maryland Geothermal", "Book A Geothermal Review",
          "Geothermal System Fitting", "Trained HVAC Technicians", "Energy Efficient Heating",
          "Geothermal Assessment", "Year Round Comfort", "Request Geothermal Info"],
         ["Geothermal heat pump installation for homes across Central Maryland.",
          "We assess the site and explain how a geothermal system would work.",
          "Geothermal heating and cooling for Severn, Severna Park and Columbia.",
          "Book a geothermal assessment with Ambient Cooling and Heating."],
         "RSA A - service led"),
     rsa(["Considering Geothermal?", "Ground Source Heating", "Geothermal Heat Pumps",
          "Efficient Year Round Comfort", "Geothermal For Your Home", "Maryland Geothermal",
          "Book A Site Assessment", "Talk To A Technician", "Geothermal HVAC Install",
          "Sustainable Home Heating", "Severn Geothermal Install", "Columbia Geothermal",
          "Clear System Options", "Geothermal Explained", "Request An Assessment"],
         ["Geothermal taps underground temperatures to heat and cool your home.",
          "We assess your property and set out whether geothermal suits it.",
          "Geothermal installation across Severn, Severna Park and Columbia.",
          "Schedule a geothermal consultation with Ambient today."],
         "RSA B - benefit led")],
   services_covered=["Geothermal Heat Pump"])



# ============================== CAMPAIGNS =====================================
# Three campaigns are REUSED. Google Ads cannot move an ad group between campaigns,
# so reuse is decided by where the ad groups that must be kept already live.
CAMPAIGNS = {
    "C1_REPAIR": {
        "reuse_campaign_id": "24257819463",
        "name": "Search | NonBrand | Heating Repair | Central MD | BOFU | 2026-09",
        "rename_to": "Search | NonBrand | Heating & Furnace Repair | Central MD | BOFU | 2026-09",
        "daily_budget": 90.00, "cpc_ceiling": 42.00, "budget_id": "15885327972",
        "ceiling_basis":
            "Pre-ceiling clearing prices: furnace p50 $23.04 / p75 $42.19 (161 clicks); "
            "heating_generic p50 $20.43 / p75 $37.48 (1,413 clicks). Account search-term "
            "CPCs: Furnace Repair $41.70, Heating Repair $10.35. $42 sits at the furnace "
            "p75, high enough to take three quarters of the auctions this theme has "
            "historically cleared, without chasing the $59.95-$63.50 p90 tail set under "
            "uncapped Maximize Clicks. Replaces the old $38.",
        "budget_basis":
            "Largest allocation because this campaign carries the two biggest converting "
            "heating themes in the account: Heating Repair (34 conversions, $14,662) and "
            "Furnace Repair (5 conversions). At a $42 ceiling, $90/day funds roughly two "
            "clicks a day across six ad groups.",
    },
    "C2_HEATPUMP": {
        "reuse_campaign_id": None,
        "name": "Search | NonBrand | Heat Pump & Ductless Heating | Central MD | BOFU | 2026-09",
        "daily_budget": 50.00, "cpc_ceiling": 35.00,
        "ceiling_basis":
            "heat_pump p50 $17.34 / p75 $32.00 (556 clicks); ductless p50 $22.26 / p75 "
            "$31.61 (940 clicks). Account search-term CPCs: Heat Pump Repair $25.32, "
            "Ductless Repair $23.30, Ductless Installation $25.66. $35 clears both p75s.",
        "budget_basis":
            "REDUCED from the proposed $65 to $50 on evidence, not preference: four of "
            "this campaign's six ad groups point at the heat-pumps URL, which fails "
            "Google's destination check, so they will carry no ads and cannot spend. Only "
            "Ductless Heating Repair can deliver at launch. $65 would fund capacity that "
            "physically cannot be used. Restore to $65 in the same motion that unblocks "
            "the heat-pump page.",
    },
    "C3_INSTALL": {
        "reuse_campaign_id": "24257819466",
        "name": "Search | NonBrand | Heating Installation | Central MD | BOFU | 2026-09",
        "rename_to": "Search | NonBrand | Heating & Furnace Install & Replace | Central MD | BOFU | 2026-09",
        "daily_budget": 55.00, "cpc_ceiling": 46.00, "budget_id": "15885327975",
        "ceiling_basis":
            "Installation clicks are the most expensive non-boiler heating clicks in the "
            "account: Furnace Replacement $45.97, Furnace Installation $45.39, oil furnace "
            "installation $28.22, furnace p75 $42.19. Heating-generic installation is much "
            "cheaper ($10.19-$16.81), so the ceiling is set by the furnace end of the "
            "campaign. $46 clears the observed furnace install/replace prices. Replaces "
            "the old $24, which sat below the account's own mini-split clearing price of "
            "$25.15 and priced the campaign out of its own best theme.",
        "budget_basis":
            "Holds the proposed $55. Three of five ad groups lack an adequate page and "
            "will carry no ads at launch, but the two that can run (Furnace Replacement, "
            "Ductless Heating Installation) are expensive per click, so the budget is not "
            "stranded the way Campaign 2's would be.",
    },
    "C4_BOILER": {
        "reuse_campaign_id": "24132507744",
        "name": "Search | NonBrand | Gas Boiler Repair | Central MD | BOFU | 2026-08",
        "rename_to": "Search | NonBrand | Boiler Services | Central MD | BOFU | 2026-09",
        "daily_budget": 45.00, "cpc_ceiling": 60.00, "budget_id": "15787409438",
        "ceiling_basis":
            "The most expensive heating theme in the account. Generic boiler p50 $29.83 / "
            "p75 $55.80 (265 clicks); gas boiler p50 $87.75, mean $98.87 (160 clicks); "
            "account search-term CPCs Boiler Repair $59.32, Boiler Maintenance $75.08, "
            "Boiler Installation $47.76. $60 clears the generic-boiler p75 and the account "
            "boiler-repair CPC, and sits deliberately BELOW the gas-boiler prices because "
            "those were set under uncapped Maximize Clicks. Evidence the current $25 is "
            "binding: this ENABLED campaign has bought ONE click all season ($12.84) and "
            "is losing 31.2% of impression share to budget with 6.2% to rank.",
        "budget_basis":
            "The only campaign in the account that is genuinely budget-limited (31.2% "
            "impression share lost to budget on $12/day). At a $60 ceiling, $45/day funds "
            "under one boiler click a day, which is the realistic shape of this theme.",
    },
    "C5_MAINT": {
        "reuse_campaign_id": None,
        "name": "Search | NonBrand | Heating Maintenance & Inspection | Central MD | BOFU | 2026-09",
        "daily_budget": 30.00, "cpc_ceiling": 32.00,
        "ceiling_basis":
            "Maintenance clearing prices: furnace|maintenance $24.80, heating|maintenance "
            "$23.38, boiler|maintenance $29.22, heat_pump|maintenance $30.25. $32 clears "
            "all four. Account search-term CPCs run higher (Furnace Maintenance $53.22, "
            "Boiler Maintenance $75.08) but those include boiler queries that belong to "
            "Campaign 4, not here.",
        "budget_basis":
            "Holds the proposed $30 even though this campaign carries the BEST measured "
            "CPAs in the account (heat_pump|maintenance $185.85, furnace|maintenance "
            "$230.31). It is not raised because three of five ad groups have no page and "
            "cannot run at launch. Revisit once the tune-up and inspection pages exist - "
            "on CPA evidence this is the campaign most likely to deserve more.",
    },
    "C6_THERMOSTAT": {
        "reuse_campaign_id": None,
        "name": "Search | NonBrand | Thermostat Services | Central MD | BOFU | 2026-09",
        "daily_budget": 15.00, "cpc_ceiling": 20.00,
        "ceiling_basis":
            "NO campaign-level history exists for this theme. The only evidence is "
            "account search terms: Thermostat Repair $17.16 CPC (1 click), Smart "
            "Thermostat Installation $14.28 (1 click). Planner sample shows roughly 30 "
            "searches a month for thermostat repair. $20 is a conservative cold-start "
            "ceiling anchored just above the two observed clicks.",
        "budget_basis":
            "REDUCED from the proposed $20 to $15. All three ad groups have NO landing "
            "page and cannot carry ads at launch, the theme has never converted, and "
            "client.yaml still lists all three thermostat services as capability-not-"
            "verified. $15 is a placeholder until a page and a capability confirmation "
            "exist.",
    },
    "C7_GEO": {
        "reuse_campaign_id": None,
        "name": "Search | NonBrand | Geothermal Heat Pump | Central MD | BOFU | 2026-09",
        "daily_budget": 20.00, "cpc_ceiling": 38.00,
        "ceiling_basis":
            "Campaign-named geothermal: mean $37.95, p50 $35.83 on 4 clicks. Geothermal "
            "SEARCH TERMS wherever served: $22.20 CPC on 59 clicks. $38 sits at the "
            "campaign-level observation and comfortably above the search-term CPC.",
        "budget_basis":
            "Holds the proposed $20 as a controlled test with a stop-loss. At a $38 "
            "ceiling this funds roughly one click every two days - small, but above the "
            "level where a budget cannot buy a click at all.",
    },
}

# Commercial HVAC Installation is NOT cooling and NOT heating. It keeps its own
# allocation inside the $325 so the service can be switched on without another
# budget approval.
COMMERCIAL_HOLDING = {
    "campaign_id": "24132507747",
    "campaign": "Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08",
    "budget_id": "15787409441",
    "from_usd": 95.00, "to_usd": 20.00,
    "why":
        "This campaign carries BOTH the residential SKAG | HVAC Installation ad group "
        "(202339087634) and SKAG | Commercial HVAC Installation (199748801029). Pausing "
        "the campaign would stop an approved commercial service, so the pause is taken at "
        "AD GROUP level and the campaign stays ENABLED. $20/day is a real commercial "
        "allocation, not a token: commercial HVAC installation clicks are expensive and "
        "the service must be able to buy one the moment its ads are enabled. It will "
        "spend $0 until then, because both of its ads are currently PAUSED.",
    "commercial_state_2026_09_21":
        "Ad group ENABLED, 2 keywords ENABLED/APPROVED/ELIGIBLE, 2 ads APPROVED/REVIEWED "
        "but BOTH PAUSED, destination offer.ambientcoolingandheating.com/"
        "commercial-hvac-installation/ live at HTTP 200. All-time delivery: 0 impressions, "
        "0 clicks, $0.00. It is one step from serving and has never served.",
}

# =========================== CROSS-NEGATIVES ==================================
# All PHRASE. No single-word BROAD negatives that could block a qualified search.
XNEG = {
    "SKAG | Furnace Repair": ["gas", "electric", "emergency", "no heat", "boiler",
                              "heat pump", "ductless", "mini split", "geothermal",
                              "thermostat", "maintenance", "tune up", "inspection",
                              "replacement", "installation"],
    "SKAG | Heating Repair": ["furnace", "boiler", "heat pump", "ductless", "mini split",
                              "geothermal", "thermostat", "emergency", "no heat",
                              "maintenance", "tune up", "inspection", "replacement",
                              "installation"],
    "SKAG | Emergency Heating Repair": ["maintenance", "tune up", "inspection",
                                        "replacement", "installation", "boiler",
                                        "heat pump", "ductless", "mini split",
                                        "geothermal", "thermostat"],
    "SKAG | No Heat Repair": ["maintenance", "tune up", "inspection", "replacement",
                              "installation", "boiler", "heat pump", "ductless",
                              "mini split", "geothermal", "thermostat"],
    "SKAG | Gas Furnace Repair": ["electric", "oil", "boiler", "heat pump", "ductless",
                                  "mini split", "geothermal", "thermostat", "maintenance",
                                  "tune up", "inspection", "replacement", "installation"],
    "SKAG | Electric Furnace Repair": ["gas", "oil", "boiler", "heat pump", "ductless",
                                       "mini split", "geothermal", "thermostat",
                                       "maintenance", "tune up", "inspection",
                                       "replacement", "installation"],
    "SKAG | Heat Pump Repair": ["geothermal", "ductless", "mini split", "boiler",
                                "furnace", "thermostat", "maintenance", "tune up",
                                "replacement", "installation", "installers"],
    "SKAG | Heat Pump Replacement": ["repair", "maintenance", "tune up", "inspection",
                                     "geothermal", "ductless", "mini split", "boiler",
                                     "furnace", "thermostat", "installation"],
    "SKAG | Heat Pump Installation": ["repair", "maintenance", "tune up", "inspection",
                                      "replacement", "geothermal", "ductless",
                                      "mini split", "boiler", "furnace", "thermostat"],
    "SKAG | Heat Pump Maintenance": ["repair", "replacement", "installation", "installers",
                                     "geothermal", "ductless", "mini split", "boiler",
                                     "furnace", "thermostat"],
    "SKAG | Ductless Heating Repair": ["installation", "installers", "replacement",
                                       "maintenance", "tune up", "inspection",
                                       "heat pump", "geothermal", "boiler", "furnace",
                                       "thermostat"],
    "SKAG | Furnace Replacement": ["repair", "maintenance", "tune up", "inspection",
                                   "installation", "installers", "boiler", "heat pump",
                                   "ductless", "mini split", "geothermal", "thermostat",
                                   "oil"],
    "SKAG | Furnace Installation": ["repair", "maintenance", "tune up", "inspection",
                                    "replacement", "boiler", "heat pump", "ductless",
                                    "mini split", "geothermal", "thermostat", "oil"],
    "SKAG | Heating Replacement": ["repair", "maintenance", "tune up", "inspection",
                                   "installation", "installers", "furnace", "boiler",
                                   "heat pump", "ductless", "mini split", "geothermal",
                                   "thermostat"],
    "SKAG | Heating Installation": ["repair", "maintenance", "tune up", "inspection",
                                    "replacement", "furnace", "boiler", "heat pump",
                                    "ductless", "mini split", "geothermal", "thermostat"],
    "SKAG | Ductless Heating Installation": ["repair", "maintenance", "tune up",
                                             "inspection", "heat pump", "geothermal",
                                             "boiler", "furnace", "thermostat"],
    "SKAG | Gas Boiler Repair": ["oil", "electric", "tankless", "furnace", "heat pump",
                                 "replacement", "installation", "installers",
                                 "maintenance", "tune up", "inspection"],
    "SKAG | Boiler Repair": ["gas", "oil", "tankless", "furnace", "heat pump",
                             "replacement", "installation", "installers", "maintenance",
                             "tune up", "inspection"],
    "SKAG | Boiler Replacement": ["repair", "maintenance", "tune up", "inspection",
                                  "installation", "installers", "furnace", "heat pump",
                                  "tankless"],
    "SKAG | Boiler Installation": ["repair", "maintenance", "tune up", "inspection",
                                   "replacement", "furnace", "heat pump", "tankless"],
    "SKAG | Boiler Maintenance": ["repair", "replacement", "installation", "installers",
                                  "furnace", "heat pump", "tankless"],
    "SKAG | Furnace Maintenance": ["repair", "replacement", "installation", "installers",
                                   "tune up", "inspection", "boiler", "heat pump",
                                   "ductless", "mini split", "geothermal", "thermostat",
                                   "oil"],
    "SKAG | Furnace Tune-Up": ["repair", "replacement", "installation", "installers",
                               "maintenance", "inspection", "boiler", "heat pump",
                               "ductless", "mini split", "geothermal", "thermostat"],
    "SKAG | Heating Maintenance": ["repair", "replacement", "installation", "installers",
                                   "tune up", "inspection", "furnace", "boiler",
                                   "heat pump", "ductless", "mini split", "geothermal",
                                   "thermostat"],
    "SKAG | Heating Tune-Up": ["repair", "replacement", "installation", "installers",
                               "maintenance", "inspection", "furnace", "boiler",
                               "heat pump", "ductless", "mini split", "geothermal",
                               "thermostat"],
    "SKAG | Heating System Inspection": ["repair", "replacement", "installation",
                                         "installers", "maintenance", "tune up",
                                         "furnace", "boiler", "heat pump", "ductless",
                                         "mini split", "geothermal", "thermostat"],
    "SKAG | Thermostat Repair": ["replacement", "installation", "installers", "smart",
                                 "nest", "ecobee", "furnace", "boiler", "heat pump",
                                 "heating system"],
    "SKAG | Thermostat Replacement": ["repair", "installation", "installers", "smart",
                                      "nest", "ecobee", "furnace", "boiler", "heat pump",
                                      "heating system"],
    "SKAG | Smart Thermostat Installation": ["repair", "replacement", "furnace", "boiler",
                                             "heat pump", "heating system"],
    # 'heat pump' is NOT negated here: 'geothermal heat pump' is this ad group's own
    # keyword. The one-way split is enforced from the four Heat Pump ad groups, which
    # each negate 'geothermal'.
    "SKAG | Geothermal Heat Pump": ["ductless", "mini split", "boiler", "furnace",
                                    "thermostat", "repair", "maintenance", "tune up"],
}

# ======================= COOLING PAUSE (SEPARATE PLAN) ========================
# Residential cooling only. Ad-group level where a campaign also carries a service
# that is NOT cooling. Nothing is deleted; every original ID, budget, status and
# setting is recorded so the pause is reversible.
COOLING_PAUSE = {
    "24132507741": {
        "campaign": "Search | NonBrand | AC Repair | Central MD | BOFU | 2026-08",
        "level": "CAMPAIGN",
        "why": "Contains only residential cooling (SKAG | AC Repair Near Me). Safe to "
               "pause at campaign level.",
        "ad_groups": {"202339087834": "SKAG | AC Repair Near Me"},
        "rollback": {"campaign_status": "ENABLED", "daily": 45.00,
                     "budget_id": "15787409435", "ceiling": 25.00},
    },
    "24132507750": {
        "campaign": "Search | NonBrand | HVAC Repair | Central MD | BOFU | 2026-08",
        "level": "CAMPAIGN",
        "why": "Contains only residential cooling (SKAG | HVAC Repair Near Me).",
        "ad_groups": {"202339087674": "SKAG | HVAC Repair Near Me"},
        "rollback": {"campaign_status": "ENABLED", "daily": 70.00,
                     "budget_id": "15787409444", "ceiling": 25.00},
    },
    "24132507753": {
        "campaign": "Search | NonBrand | HVAC Replacement | Central MD | BOFU | 2026-08",
        "level": "CAMPAIGN",
        "why": "Contains only residential cooling (SKAG | HVAC Replacement Near Me).",
        "ad_groups": {"200159223798": "SKAG | HVAC Replacement Near Me"},
        "rollback": {"campaign_status": "ENABLED", "daily": 15.00,
                     "budget_id": "15787409447", "ceiling": 30.00},
    },
    "24132507747": {
        "campaign": "Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08",
        "level": "AD_GROUP",
        "why": "DO NOT pause this campaign. It carries SKAG | Commercial HVAC "
               "Installation 199748801029, which is an approved non-cooling service with "
               "a live landing page. Only the residential ad group is paused; the "
               "campaign stays ENABLED at the $20 commercial holding budget.",
        "ad_groups": {"202339087634": "SKAG | HVAC Installation"},
        "preserve": {"199748801029": "SKAG | Commercial HVAC Installation - LEAVE ENABLED"},
        "rollback": {"campaign_status": "ENABLED", "daily": 95.00,
                     "budget_id": "15787409441", "ceiling": 30.00,
                     "ad_group_202339087634_status": "ENABLED",
                     "enabled_ads": ["821319509197", "821319509200"],
                     "keywords": ["hvac installers near me PHRASE",
                                  "hvac installers near me EXACT"]},
    },
}

# ============================== VALIDATION ====================================
TOK = re.compile(r"[a-z0-9']+")
BARRED = {
    "same_day": re.compile(r"\bsame[- ]day\b", re.I),
    "emergency_promise": re.compile(r"\b(24/7|24-7|round the clock|emergency service)\b", re.I),
    "guarantee": re.compile(r"\bguarantee", re.I),
    "licensed_insured": re.compile(r"\blicen[cs]ed\b|\binsured\b", re.I),
    "best_top_trusted": re.compile(r"\b(best|top[- ]rated|#1|number one|most trusted)\b", re.I),
    "free_estimate": re.compile(r"\bfree (estimate|consultation|quote)\b", re.I),
    "rating_or_reviews": re.compile(r"\b\d+(\.\d+)?\s*star|\b\d{2,}\+?\s*review", re.I),
    "financing": re.compile(r"\bfinanc|\bmonthly payment|\b0% apr\b", re.I),
    "phone_number": re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b|\(\d{3}\)\s*\d{3}[-. ]?\d{4}"),
    "response_time": re.compile(r"\bwithin \d+ (minutes|hours)\b|\bfast response\b", re.I),
}


def toks(s):
    return TOK.findall(s.lower())


def phrase_blocks(neg, query):
    q, n = toks(query), toks(neg)
    return bool(n) and any(q[i:i + len(n)] == n for i in range(len(q) - len(n) + 1))


def contig(inner, outer):
    a, b = toks(inner), toks(outer)
    return len(a) <= len(b) and any(b[i:i + len(a)] == a
                                    for i in range(len(b) - len(a) + 1))


def validate(live_kw):
    """live_kw: {ad_group_name: [(text, match_type), ...]} for EXISTING ad groups."""
    errs, warns = [], []

    # ---- RSA shape, limits, duplication, barred claims
    for name, d in AG.items():
        for r in d["rsas"]:
            if len(r["h"]) != 15:
                errs.append(f"{name}/{r['label']}: {len(r['h'])} headlines, need 15")
            if len(r["d"]) != 4:
                errs.append(f"{name}/{r['label']}: {len(r['d'])} descriptions, need 4")
            for h in r["h"]:
                if len(h) > 30:
                    errs.append(f"{name}/{r['label']}: headline {len(h)}>30 '{h}'")
            for x in r["d"]:
                if len(x) > 90:
                    errs.append(f"{name}/{r['label']}: description {len(x)}>90 '{x}'")
            if len(set(r["h"])) != len(r["h"]):
                errs.append(f"{name}/{r['label']}: duplicate headline inside the RSA")
            if len(set(r["d"])) != len(r["d"]):
                errs.append(f"{name}/{r['label']}: duplicate description inside the RSA")
            for lab, rx in BARRED.items():
                for t in r["h"] + r["d"]:
                    if rx.search(t):
                        errs.append(f"{name}/{r['label']}: BARRED '{lab}' in '{t}'")
        if len(d["rsas"]) == 2 and set(d["rsas"][0]["h"]) == set(d["rsas"][1]["h"]):
            errs.append(f"{name}: RSA A and B are not differentiated")
        # An RSA may only exist where the page supports the intent.
        if d["rsas"] and d["url"] is None:
            errs.append(f"{name}: has RSAs but no final URL")
        if d["rsas"] and d["url"] in BLOCKED_DEST:
            errs.append(f"{name}: RSA points at a BLOCKED destination")
        if d["rsas"] and d["page_verdict"] in ("NO PAGE", "INSUFFICIENT PAGE",
                                               "DESTINATION BLOCKED"):
            errs.append(f"{name}: RSA drafted against a {d['page_verdict']} destination")
        if not d["rsas"] and d["page_verdict"] == "ADEQUATE" \
                and not d["existing_ad_group_id"]:
            errs.append(f"{name}: page is ADEQUATE but no RSA was drafted")

    # ---- keyword normalisation, match types, subsumption
    for name, d in AG.items():
        for k in d["phrase"] + d["exact"]:
            if k != k.lower().strip():
                errs.append(f"{name}: keyword not normalised '{k}'")
        for x in d["phrase"]:
            cov = [y for y in d["phrase"] if y != x and contig(y, x)]
            if cov:
                errs.append(f"{name}: PHRASE '{x}' is already matched by PHRASE {cov}")

    # ---- the same keyword must not appear in two ad groups
    seen = {}
    for name, d in AG.items():
        for k in d["phrase"]:
            seen.setdefault((k, "PHRASE"), []).append(name)
        for k in d["exact"]:
            seen.setdefault((k, "EXACT"), []).append(name)
    for (k, m), owners in seen.items():
        if len(owners) > 1:
            errs.append(f"keyword collision: '{k}' [{m}] in {owners}")

    # ---- SELF-BLOCK: a cross-negative must never block its own ad group's keywords
    for name, negs in XNEG.items():
        if name not in AG:
            errs.append(f"cross-negative set for unknown ad group '{name}'")
            continue
        gone = {(t.lower(), m) for t, m in AG[name].get("remove_keywords", [])}
        own = AG[name]["phrase"] + AG[name]["exact"] + [
            t for t, m in live_kw.get(name, []) if (t.lower(), m) not in gone]
        for n in negs:
            for k in own:
                if phrase_blocks(n, k):
                    errs.append(f"SELF-BLOCK {name}: negative '{n}' blocks own keyword "
                                f"'{k}'")

    # ---- every ad group must carry a cross-negative set
    for name in AG:
        if name not in XNEG:
            errs.append(f"{name}: no cross-negative set")

    # ---- routing: required splits must actually be enforced
    REQUIRED_SPLITS = [
        ("SKAG | Furnace Repair", "gas"), ("SKAG | Furnace Repair", "electric"),
        ("SKAG | Heating Repair", "furnace"), ("SKAG | Heating Repair", "emergency"),
        ("SKAG | Heating Repair", "no heat"),
        ("SKAG | Heat Pump Repair", "geothermal"),
        ("SKAG | Heat Pump Replacement", "geothermal"),
        ("SKAG | Heat Pump Installation", "geothermal"),
        ("SKAG | Heat Pump Maintenance", "geothermal"),
        ("SKAG | Heat Pump Repair", "ductless"),
        ("SKAG | Boiler Repair", "gas"),
        ("SKAG | Boiler Repair", "furnace"),
        ("SKAG | Furnace Maintenance", "tune up"),
        ("SKAG | Furnace Tune-Up", "maintenance"),
        ("SKAG | Heating Maintenance", "tune up"),
        ("SKAG | Heating Tune-Up", "maintenance"),
        ("SKAG | Heating System Inspection", "maintenance"),
        ("SKAG | Thermostat Repair", "heating system"),
        ("SKAG | Thermostat Repair", "smart"),
    ]
    for agname, neg in REQUIRED_SPLITS:
        if neg not in XNEG.get(agname, []):
            errs.append(f"ROUTING: {agname} is missing required negative '{neg}'")

    # ---- structured snippet values are capped at 25 characters
    for k, vals in SNIPPETS.items():
        if not 3 <= len(vals) <= 10:
            errs.append(f"SNIPPET {k}: {len(vals)} values, Google requires 3-10")
        for v in vals:
            if len(v) > 25:
                errs.append(f"SNIPPET {k}: value {len(v)}>25 chars '{v}'")

    # ---- budget arithmetic
    heat_total = round(sum(v["daily_budget"] for v in CAMPAIGNS.values()), 2)
    grand = round(heat_total + COMMERCIAL_HOLDING["to_usd"], 2)
    if grand > WORKING_TARGET:
        errs.append(f"BUDGET: ${grand} exceeds the ${WORKING_TARGET} working target")
    if grand > CAP_DAY:
        errs.append(f"BUDGET: ${grand} exceeds the ${CAP_DAY} absolute ceiling")
    if round(grand * 30.4, 2) > CAP_MONTH:
        errs.append(f"BUDGET: ${grand}/day x 30.4 exceeds ${CAP_MONTH}")
    for k, v in CAMPAIGNS.items():
        if v["daily_budget"] < v["cpc_ceiling"] * 0.25:
            warns.append(f"{k}: ${v['daily_budget']}/day against a ${v['cpc_ceiling']} "
                         f"ceiling buys under one click every four days")

    # ---- coverage: all 31 requested services
    covered = set()
    for d in AG.values():
        covered |= set(d["services_covered"])
    missing = [s for s in REQUESTED_31 if s not in covered]
    # The instruction explicitly retains the existing Gas Boiler Repair ad group as one
    # ADDITIONAL heating ad group beyond the 31 requested services.
    PERMITTED_EXTRA = {"Gas Boiler Repair"}
    extra = [s for s in covered if s not in REQUESTED_31 and s not in PERMITTED_EXTRA]
    if missing:
        errs.append(f"COVERAGE: {len(missing)} requested services unmapped: {missing}")
    if extra:
        errs.append(f"COVERAGE: ad groups cover non-requested services: {extra}")

    return errs, warns, heat_total, grand


REQUESTED_31 = [
    "Furnace Repair", "Furnace Replacement", "Furnace Installation", "Furnace Maintenance",
    "Furnace Tune-Up", "Heat Pump Repair", "Heat Pump Replacement", "Heat Pump Installation",
    "Heat Pump Maintenance", "Boiler Repair", "Boiler Replacement", "Boiler Installation",
    "Boiler Maintenance", "Heating Repair", "Heating Replacement", "Heating Installation",
    "Heating Maintenance", "Heating Tune-Up", "Emergency Heating Repair", "No Heat Repair",
    "Thermostat Repair", "Thermostat Replacement", "Smart Thermostat Installation",
    "Ductless Heating Repair", "Ductless Heating Installation", "Gas Furnace Repair",
    "Electric Furnace Repair", "Heating System Inspection", "Heating System Replacement",
    "Heating System Installation", "Geothermal Heat Pump",
]


def main():
    c = client()
    identity_gate(c, verbose=True)

    # live keywords on the three reused ad groups, so the self-block test runs against
    # what is actually there rather than against an assumption
    live_kw = {}
    for r in q(c, """SELECT ad_group.id, ad_group.name,
                     ad_group_criterion.keyword.text,
                     ad_group_criterion.keyword.match_type
                     FROM ad_group_criterion
                     WHERE ad_group.id IN (199797580706, 199797580746, 202339087594)
                       AND ad_group_criterion.type = 'KEYWORD'
                       AND ad_group_criterion.negative = FALSE
                       AND ad_group_criterion.status != 'REMOVED'"""):
        nm = {"199797580706": "SKAG | Furnace Repair",
              "199797580746": "SKAG | Ductless Heating Installation",
              "202339087594": "SKAG | Gas Boiler Repair"}[str(r.ad_group.id)]
        live_kw.setdefault(nm, []).append(
            (r.ad_group_criterion.keyword.text,
             E(r.ad_group_criterion.keyword.match_type)))
    print("\n=== LIVE KEYWORDS ON REUSED AD GROUPS ===")
    for k, v in live_kw.items():
        print(f"   {k:42s} {len(v)} keywords")
        for t, m in sorted(v):
            print(f"      {m:7s} {t}")

    errs, warns, heat_total, grand = validate(live_kw)
    print("\n=== LOCAL VALIDATION ===")
    for w in warns:
        print(f"   WARN {w}")
    if errs:
        for e in errs:
            print(f"   FAIL {e}")
        print(f"\n{len(errs)} problems. Plans NOT fingerprinted.")
        sys.exit(1)
    print("   PASS - RSA limits/claims, keyword hygiene, self-block, routing splits, "
          "budget arithmetic, 31-service coverage")

    n_new_ag = sum(1 for d in AG.values() if not d["existing_ad_group_id"])
    n_kw = sum(len(d["phrase"]) + len(d["exact"]) for d in AG.values())
    n_rsa = sum(len(d["rsas"]) for d in AG.values())
    n_newc = sum(1 for v in CAMPAIGNS.values() if not v["reuse_campaign_id"])

    print(f"\n=== STRUCTURE ===")
    print(f"   campaigns            7  ({n_newc} new, {7 - n_newc} reused)")
    print(f"   ad groups           {len(AG)}  ({n_new_ag} new, "
          f"{len(AG) - n_new_ag} reused)")
    print(f"   keywords            {n_kw}  (new only; reused ad groups keep theirs)")
    print(f"   RSAs                {n_rsa}")
    print(f"   cross-negatives     {sum(len(v) for v in XNEG.values())}")
    print(f"\n=== BUDGET ===")
    for k, v in CAMPAIGNS.items():
        print(f"   {k:14s} ${v['daily_budget']:6.2f}/day  ceiling ${v['cpc_ceiling']:6.2f}"
              f"  {v['name'][:52]}")
    print(f"   {'COMMERCIAL':14s} ${COMMERCIAL_HOLDING['to_usd']:6.2f}/day  "
          f"(holding, campaign {COMMERCIAL_HOLDING['campaign_id']})")
    print(f"   {'HEATING TOTAL':14s} ${heat_total:6.2f}")
    print(f"   {'GRAND TOTAL':14s} ${grand:6.2f}   cap ${WORKING_TARGET}  "
          f"absolute ${CAP_DAY}")
    print(f"   monthly equivalent ${grand * 30.4:,.2f}  (cap ${CAP_MONTH:,.0f})")

    base = {"customer_id": CID, "exact_account_name": EXACT_NAME,
            "never_write_to_mcc": GM_MANAGER, "built_local": STAMP}

    BASIS = json.loads((SNAP / "budget-basis-2026-09-21.json").read_text(encoding="utf-8"))
    SEP = BASIS["september"]

    # ---------------------------------------------------------------- BUILD plan
    build = dict(base, **{
        "plan_name": "AMB-0921B-HEAT-BUILD-1",
        "approval_class": "create-paused",
        "everything_created_paused": True,
        "nothing_enabled": True,
        "cooling_untouched_by_this_plan": True,
        "supersedes": ["AMB-0921-HEAT-EXPAND-1 / 20A73EEA3023",
                       "AMB-0921-BUDGET-1 / 6C665894E30D",
                       "AMB-0921-BID-1 / B520C42F2007"],
        "reuses_not_duplicates": {
            "campaigns": {k: v["reuse_campaign_id"] for k, v in CAMPAIGNS.items()
                          if v["reuse_campaign_id"]},
            "ad_groups": {n: d["existing_ad_group_id"] for n, d in AG.items()
                          if d["existing_ad_group_id"]},
            "assets": {"call": "407995613637 = (410) 705-6354",
                       "business_name": "80516971145",
                       "callouts": "5 reused, APPROVED/REVIEWED",
                       "sitelinks": "3 reused per campaign, APPROVED/REVIEWED, none "
                                    "pointing at the blocked heat-pumps URL",
                       "structured_snippets": "1 created per new campaign"},
        },
        "campaigns": CAMPAIGNS,
        "commercial_holding": COMMERCIAL_HOLDING,
        "ad_groups": AG,
        "cross_negatives": XNEG,
        "cross_negative_total": sum(len(v) for v in XNEG.values()),
        "page_support_evidence": PAGE_SUPPORT,
        "blocked_destinations": BLOCKED_DEST,
        "search_settings": {
            "network": "Google Search only", "search_partners": False, "display": False,
            "ai_max": False, "dsa": False, "performance_max": False,
            "broad_match_expansion": False, "final_url_expansion": False,
            "automatically_created_assets": False, "text_customization": False,
            "geo": "PRESENCE / PRESENCE", "locations": "75 approved Central MD",
            "schedule": "6 approved rows, Mon-Fri 08:00-20:00 + Sat 08:00-13:00",
            "match_types": ["PHRASE", "EXACT"],
            "contains_eu_political_advertising":
                "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"},
        "counts": {"campaigns": 7, "new_campaigns": n_newc,
                   "ad_groups": len(AG), "new_ad_groups": n_new_ag,
                   "keywords_new": n_kw, "rsas": n_rsa,
                   "ad_groups_with_rsas": sum(1 for d in AG.values() if d["rsas"]),
                   "ad_groups_without_rsas_pending_pages":
                       sum(1 for d in AG.values()
                           if not d["rsas"] and not d["existing_ad_group_id"])},
    })
    ops = (
        [{"op": "CREATE_CAMPAIGN_BUDGET", "campaign_key": k,
          "amount_usd": v["daily_budget"]}
         for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]]
        + [{"op": "CREATE_CAMPAIGN_PAUSED", "campaign_key": k, "name": v["name"],
            "cpc_bid_ceiling_usd": v["cpc_ceiling"]}
           for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]]
        + [{"op": "RENAME_CAMPAIGN", "campaign_id": v["reuse_campaign_id"],
            "from": v["name"], "to": v["rename_to"]}
           for v in CAMPAIGNS.values()
           if v["reuse_campaign_id"] and v.get("rename_to")]
        + [{"op": "ADD_CAMPAIGN_LOCATIONS", "campaign_key": k, "count": 75}
           for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]]
        + [{"op": "ADD_CAMPAIGN_AD_SCHEDULE", "campaign_key": k, "count": 6}
           for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]]
        + [{"op": "CREATE_AD_GROUP_PAUSED", "ad_group": n,
            "campaign_key": d["campaign_key"], "final_url": d["url"],
            "cpc_bid_usd": d["cpc_bid"]}
           for n, d in AG.items() if not d["existing_ad_group_id"]]
        + [{"op": "RENAME_AD_GROUP", "ad_group_id": d["existing_ad_group_id"],
            "from": d["rename_from"], "to": n}
           for n, d in AG.items() if d.get("rename_from")]
        + [{"op": "REMOVE_KEYWORDS_FROM_EXISTING_AD_GROUP",
            "ad_group": n, "ad_group_id": d["existing_ad_group_id"],
            "keywords": [{"text": t, "match_type": m} for t, m in d["remove_keywords"]],
            "count": len(d["remove_keywords"]),
            "why": "Theme handed to its own SKAG in this plan. Removing rather than "
                   "duplicating prevents two ad groups bidding on one query."}
           for n, d in AG.items() if d.get("remove_keywords")]
        + [{"op": "ADD_KEYWORDS_PAUSED", "ad_group": n, "phrase": d["phrase"],
            "exact": d["exact"], "count": len(d["phrase"]) + len(d["exact"])}
           for n, d in AG.items() if d["phrase"] or d["exact"]]
        + [{"op": "CREATE_RSA_PAUSED", "ad_group": n, "label": r["label"],
            "final_url": d["url"], "headlines": r["h"], "descriptions": r["d"]}
           for n, d in AG.items() for r in d["rsas"]]
        + [{"op": "ADD_AD_GROUP_CROSS_NEGATIVES", "ad_group": n, "match_type": "PHRASE",
            "negatives": XNEG[n], "count": len(XNEG[n])} for n in AG]
        + [{"op": "LINK_EXISTING_CALL_ASSET_PAUSED", "asset_id": "407995613637",
            "campaign_key": k} for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]]
        + [{"op": "LINK_EXISTING_BUSINESS_NAME_ASSET", "asset_id": "80516971145",
            "campaign_key": k} for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]]
        + [{"op": "LINK_EXISTING_CALLOUT_ASSETS", "campaign_key": k,
            "asset_ids": ["422477374526", "422577760603", "422577771364",
                          "422577777430", "422577777442"], "count": 5,
            "reused_not_created": True}
           for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]]
        + [{"op": "LINK_EXISTING_SITELINK_ASSETS", "campaign_key": k,
            "asset_ids": ["422577777457", "422577771382", "422477374559"], "count": 3,
            "reused_not_created": True,
            "no_blocked_url": True}
           for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]]
        + [{"op": "CREATE_STRUCTURED_SNIPPET_AND_LINK", "campaign_key": k,
            "header": "Services", "values": SNIPPETS[k], "count": 1}
           for k, v in CAMPAIGNS.items() if not v["reuse_campaign_id"]])
    build["operations"] = ops
    build["operation_count"] = len(ops)
    build["fingerprint"] = approval_code(build)

    # --------------------------------------------------------------- BUDGET plan
    budget_changes = []
    for k, v in CAMPAIGNS.items():
        if v["reuse_campaign_id"]:
            budget_changes.append({
                "campaign_key": k, "campaign_id": v["reuse_campaign_id"],
                "campaign": v["name"], "budget_id": v["budget_id"],
                "to_usd": v["daily_budget"], "why": v["budget_basis"]})
    budget = dict(base, **{
        "plan_name": "AMB-0921B-BUDGET-1",
        "approval_class": "update-existing-budgets",
        "end_state": {
            "heating_daily_total": heat_total,
            "commercial_holding_daily": COMMERCIAL_HOLDING["to_usd"],
            "residential_cooling_daily": 0.0,
            "grand_total_daily": grand,
            "working_target": WORKING_TARGET, "absolute_ceiling": CAP_DAY,
            "monthly_equivalent": round(grand * 30.4, 2), "monthly_cap": CAP_MONTH,
            "headroom_under_working_target": round(WORKING_TARGET - grand, 2),
            "monthly_buffer": round(CAP_MONTH - grand * 30.4, 2)},
        "september": {
            "read_on": BASIS["account_today"],
            "mtd_incl_partial_today": SEP["mtd_incl_partial_today"],
            "settled_calendar_days": SEP["settled_calendar_days"],
            "days_with_any_delivery": SEP["days_with_delivery"],
            "settled_daily_avg_calendar": SEP["settled_daily_avg"],
            "last7_calendar_daily_avg": SEP["last7_daily_avg"],
            "days_left_incl_today": SEP["days_left_incl_today"],
            "remaining_allowance": SEP["remaining_allowance"],
            "reserve_10pct": SEP["reserve_10pct"],
            "max_safe_daily_pace": SEP["max_safe_daily_pace"],
            "projection_worst_case": round(
                SEP["mtd_incl_partial_today"] + grand * SEP["days_left_incl_today"], 2),
            "projection_worst_plus_reserve": round(
                SEP["mtd_incl_partial_today"] + grand * SEP["days_left_incl_today"]
                + SEP["reserve_10pct"], 2),
            "projection_evidence_case": round(
                SEP["mtd_incl_partial_today"]
                + SEP["last7_daily_avg"] * SEP["days_left_incl_today"], 2)},
        "changes": budget_changes,
        "commercial_holding": COMMERCIAL_HOLDING,
        "no_incremental_budget":
            "Every heating dollar comes from cooling. The account total does not rise.",
        "honest_limitation":
            "These are ceilings, not spend predictions. Measured September delivery is "
            "$87.32/day over 20 settled calendar days and $49.13/day over the last 7, "
            "against $237.00/day of enabled budget. Four of five enabled campaigns lose "
            "0.0-8.9% of impression share to BUDGET and 43.6-67.3% to RANK, so the "
            "binding constraint is the CPC ceiling, not the budget. AMB-0921B-BID-1 is "
            "the plan that changes delivery; this one sets the guardrail. No CPL, CPQL, "
            "lead-volume, revenue or profitability outcome is claimed."})
    budget["operations"] = (
        [{"op": "UPDATE_CAMPAIGN_BUDGET_AMOUNT", "budget_id": b["budget_id"],
          "campaign_id": b["campaign_id"], "campaign": b["campaign"],
          "to_usd": b["to_usd"], "field_mask": "amount_micros"}
         for b in budget_changes]
        + [{"op": "UPDATE_CAMPAIGN_BUDGET_AMOUNT",
            "budget_id": COMMERCIAL_HOLDING["budget_id"],
            "campaign_id": COMMERCIAL_HOLDING["campaign_id"],
            "campaign": COMMERCIAL_HOLDING["campaign"],
            "from_usd": COMMERCIAL_HOLDING["from_usd"],
            "to_usd": COMMERCIAL_HOLDING["to_usd"],
            "field_mask": "amount_micros"}])
    budget["operation_count"] = len(budget["operations"])
    budget["fingerprint"] = approval_code(budget)

    # ------------------------------------------------------------------ BID plan
    bid_changes = []
    for k, v in CAMPAIGNS.items():
        if v["reuse_campaign_id"]:
            bid_changes.append({
                "campaign_key": k, "campaign_id": v["reuse_campaign_id"],
                "campaign": v["name"], "to_usd": v["cpc_ceiling"],
                "evidence": v["ceiling_basis"]})
    bid = dict(base, **{
        "plan_name": "AMB-0921B-BID-1",
        "approval_class": "update-cpc-bid-ceiling",
        "why_separate":
            "These are BID changes, not budget changes. One lands on an ENABLED campaign "
            "(24132507744) and raises cost per click, so it carries its own approval.",
        "bidding_strategy_unchanged":
            "All campaigns stay on TARGET_SPEND (Maximize Clicks) with a CPC ceiling. No "
            "conversion-based Smart Bidding, because the primary-conversion and "
            "attribution signals are still unreliable: the website phone number is wrong, "
            "the positive-path GCLID test is incomplete, and no approved production form "
            "test has been run.",
        "changes": bid_changes,
        "new_campaign_ceilings": {k: v["cpc_ceiling"] for k, v in CAMPAIGNS.items()
                                  if not v["reuse_campaign_id"]},
        "operations": [{"op": "UPDATE_CAMPAIGN_CPC_BID_CEILING",
                        "campaign_id": b["campaign_id"], "campaign": b["campaign"],
                        "to_usd": b["to_usd"],
                        "field_mask": "target_spend.cpc_bid_ceiling_micros"}
                       for b in bid_changes]})
    bid["operation_count"] = len(bid["operations"])
    bid["fingerprint"] = approval_code(bid)

    # ------------------------------------------------------------ COOLPAUSE plan
    pause_ops = []
    for cid, v in COOLING_PAUSE.items():
        if v["level"] == "CAMPAIGN":
            pause_ops.append({"op": "PAUSE_CAMPAIGN", "campaign_id": cid,
                              "campaign": v["campaign"], "why": v["why"]})
        else:
            for agid, agname in v["ad_groups"].items():
                pause_ops.append({"op": "PAUSE_AD_GROUP", "campaign_id": cid,
                                  "ad_group_id": agid, "ad_group": agname,
                                  "why": v["why"]})
    cool = dict(base, **{
        "plan_name": "AMB-0921B-COOLPAUSE-1",
        "approval_class": "pause-existing-delivery",
        "runs_only_after":
            "Heating enablement is complete AND the heating campaigns are proven able to "
            "serve. If heating enablement fails, this plan does NOT run.",
        "nothing_deleted": True,
        "commercial_preserved": {
            "campaign_id": "24132507747",
            "ad_group_id": "199748801029",
            "note": "SKAG | Commercial HVAC Installation stays ENABLED. Its campaign "
                    "stays ENABLED at the $20 holding budget. Only the residential ad "
                    "group is paused."},
        "gas_boiler_preserved": {
            "campaign_id": "24132507744",
            "note": "Gas Boiler Repair is HEATING and becomes Campaign 4. Never paused."},
        "inventory": COOLING_PAUSE,
        "rollback":
            "Every original campaign status, budget, CPC ceiling, ad-group status, "
            "enabled ad ID and keyword is recorded in 'inventory'. Reversal is a status "
            "flip back to the recorded values; nothing is removed, so no resource has to "
            "be recreated.",
        "operations": pause_ops})
    cool["operation_count"] = len(pause_ops)
    cool["fingerprint"] = approval_code(cool)

    PLANS.mkdir(parents=True, exist_ok=True)
    print("\n=== PLANS ===")
    for p in (build, budget, bid, cool):
        (PLANS / f"{p['plan_name']}.json").write_text(
            json.dumps(p, indent=1, default=str), encoding="utf-8")
        print(f"  APPROVE {p['plan_name']} {p['fingerprint']} "
              f"{p['operation_count']} operations FOR {CID}")

    # --------------------------------------------------- 31-service coverage matrix
    matrix = []
    for s in REQUESTED_31:
        owners = [(n, d) for n, d in AG.items() if s in d["services_covered"]]
        n, d = owners[0]
        matrix.append({
            "service": s, "ad_group": n,
            "campaign": CAMPAIGNS[d["campaign_key"]]["rename_to"]
                        if CAMPAIGNS[d["campaign_key"]].get("rename_to")
                        else CAMPAIGNS[d["campaign_key"]]["name"],
            "campaign_key": d["campaign_key"],
            "existing_ad_group_id": d["existing_ad_group_id"],
            "final_url": d["url"], "page_verdict": d["page_verdict"],
            "rsas": len(d["rsas"]),
            "keywords": len(d["phrase"]) + len(d["exact"]),
            "launch_gate": d["launch_gate"]})
    (SNAP / f"coverage-matrix-{STAMP}.json").write_text(
        json.dumps({"generated_local": datetime.datetime.now(TZ).isoformat(),
                    "requested_services": len(REQUESTED_31),
                    "ad_groups": len(AG), "matrix": matrix}, indent=1, default=str),
        encoding="utf-8")
    print(f"\n=== 31-SERVICE COVERAGE MATRIX ===")
    print(f"{'#':>3} {'service':32s} {'ad group':38s} {'C':5s} {'page':22s} {'RSA':>3s}")
    for i, m in enumerate(matrix, 1):
        print(f"{i:3d} {m['service']:32s} {m['ad_group'][:38]:38s} "
              f"{m['campaign_key'][:5]:5s} {m['page_verdict']:22s} {m['rsas']:3d}")

    print("\nEXTERNAL WRITES: 0 (local draft only)")


SNIPPETS = {
    "C2_HEATPUMP": ["Heat Pump Repair", "Heat Pump Installation", "Ductless Heating",
                    "Mini Split Service"],
    "C5_MAINT": ["Furnace Maintenance", "Heating Maintenance", "Heating Tune-Up",
                 "System Inspection"],
    "C6_THERMOSTAT": ["Thermostat Repair", "Thermostat Replacement",
                      "Smart Thermostat Install"],
    "C7_GEO": ["Geothermal Heat Pump", "Heat Pump Installation", "Heating Installation",
               "Ductless Heating"],
}


if __name__ == "__main__":
    main()
