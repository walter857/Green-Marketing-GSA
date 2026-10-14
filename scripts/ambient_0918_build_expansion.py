#!/usr/bin/env python3
"""Ambient | 2026-09-18 | Build the heating expansion plans. LOCAL DRAFT ONLY, no writes.

  AMB-0918-HEAT-EXPAND-1  create-paused: 2 campaigns, 2 budgets, 6 ad groups,
                          keywords, RSAs, ad-group cross-negatives, assets
  AMB-0918-BUDGET-2       reallocate existing enabled budgets under the cap
  AMB-0918-BID-1          CPC ceiling corrections on two existing campaigns
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

STAMP = "2026-09-21"
CAP_DAY, CAP_MONTH = 328.94, 10000.00
WORKING_TARGET = 325.00

# Claims barred by the owner instruction and client.yaml. The landing page's own copy is
# NOT verification - the geothermal page says "most knowledgeable", which we must not mirror.
BARRED = {
    "same day": re.compile(r"same[- ]day", re.I),
    "emergency availability": re.compile(r"\b24/7|24-7|emergency (service|available)", re.I),
    "guarantee": re.compile(r"guarantee", re.I),
    "most trusted": re.compile(r"most trusted", re.I),
    "best/top": re.compile(r"\b(best|top[- ]rated|#1|number one)\b", re.I),
    "most knowledgeable": re.compile(r"most knowledgeable", re.I),
    "free estimate/consultation/quote": re.compile(r"\bfree\b", re.I),
    "licensed/insured": re.compile(r"licen[cs]ed|insured", re.I),
    "rating/reviews": re.compile(r"\b\d+(\.\d+)?\s*star|\b\d{2,}\+?\s*review", re.I),
    "price": re.compile(r"\$\d|\bprice[sd]?\b|\bdiscount\b|\d+%\s*off", re.I),
    "financing": re.compile(r"financ", re.I),
    "warranty": re.compile(r"warrant", re.I),
    "response time": re.compile(r"\bwithin \d+\s*(min|hour)|\bfast response\b", re.I),
}

# ---------------------------------------------------------------- ad groups
# Every keyword set is de-duplicated by Planner close-variant bucket, and verified against
# the live negative pool for its own campaign (2026-09-18): only 'oil boiler replacement'
# was blocked, by the PHRASE cross-negative 'boiler' - correctly - so it is dropped.
AG = {
 "SKAG | Boiler Repair": {
   "campaign_key": "BOILER", "existing_campaign_id": "24132507744",
   "url": "https://ambientcoolingandheating.com/services/heating-services/boiler-repair/",
   "cpc_bid": 60.00,
   "phrase": ["boiler repair"],
   "exact": ["boiler repair", "residential boiler repair", "commercial boiler repair"],
   "pruned_2026_09_21": {
     "phrase_removed": ["boiler repair near me", "boiler repair service",
                        "residential boiler repair", "boiler repair company",
                        "commercial boiler repair"],
     "exact_removed": ["boiler repair near me"],
     "why": "PHRASE 'boiler repair' matches any query containing that contiguous "
            "phrase, so all five removed PHRASE terms were strict subsets of it. "
            "EXACT [boiler repair near me] collapses into [boiler repair] as an "
            "implied-location close variant. The residential and commercial EXACT "
            "terms are genuinely different queries and are retained."},
   "evidence": "Legacy 'Gas Boilers Repair' all-time: $6,383.12 / 71 clicks / 9 conversions, "
               "CPC $89.90, CPA $709.24. 'Heating & Boiler Repair - Calls': 14 conversions "
               "at CPA $334.83. Boiler repair converts; the current $25 ceiling is the reason "
               "the live campaign has bought 1 click all season.",
   "rsas": [
     {"label": "RSA A - service-first",
      "h": ["Boiler Repair in Severn", "Boiler Repair Central MD",
            "Severna Park Boiler Repair", "Columbia MD Boiler Repair",
            "Residential Boiler Repair", "Commercial Boiler Repair",
            "Boiler Repair Technicians", "Book a Boiler Repair Visit",
            "Maryland Boiler Repair", "Boiler Diagnosis Explained",
            "Schedule Boiler Service", "Homes and Businesses",
            "Trained HVAC Technicians", "Boiler Service Central MD",
            "Request Boiler Repair"],
      "d": ["Boiler repair for homes and businesses in Severn, Severna Park and Columbia.",
            "Our technicians diagnose the fault and explain your options clearly.",
            "Book a boiler repair visit with Ambient Cooling and Heating.",
            "Serving Central Maryland with professional boiler repair."]},
     {"label": "RSA B - symptom-led",
      "h": ["Boiler Stopped Working?", "No Heat From Your Boiler?",
            "Boiler Leaking or Faulty?", "Get Your Boiler Looked At",
            "Boiler Repair Near You", "Central Maryland Boilers",
            "Boiler Repair Specialists", "Severn Boiler Repair",
            "Book a Boiler Inspection", "Talk to a Technician",
            "We Repair Home Boilers", "We Repair Business Boilers",
            "Clear Repair Options", "Request Boiler Service",
            "Columbia Boiler Service"],
      "d": ["Boiler trouble in Severn, Severna Park or Columbia? Our technicians help.",
            "We diagnose the problem and walk you through the repair options.",
            "Boiler repair for Maryland homes and commercial properties.",
            "Schedule a boiler repair appointment with Ambient today."]}]},

 "SKAG | Oil Furnace Installation": {
   "campaign_key": "INSTALL", "existing_campaign_id": "24257819466",
   "url": "https://ambientcoolingandheating.com/services/heating-services/oil-furnace-installations/",
   "cpc_bid": 30.00,
   "phrase": ["oil furnace installation"],
   "exact": ["oil furnace installation"],
   "pruned_2026_09_21": {
     "phrase_removed": ["oil furnace installation cost"],
     "exact_removed": [],
     "why": "Strict subset of PHRASE 'oil furnace installation'."},
   "evidence": "Page sells oil furnace installation only. Legacy 'Heating Installation' "
               "all-time CPC $15.20 on 865 clicks, 17 conversions. Planner 10-city sample "
               "shows 10/mo for the installation bucket; 'install oil furnace' and 'oil "
               "furnace install' collapse into it and are not duplicated.",
   "rsas": [
     {"label": "RSA A - service-first",
      "h": ["Oil Furnace Installation", "Oil Furnace Install Severn",
            "Severna Park Oil Furnace", "Columbia MD Oil Furnace",
            "Install a New Oil Furnace", "Oil Furnace Installers",
            "Central Maryland Oil Heat", "Book an Oil Furnace Quote",
            "Oil Furnace Specialists", "Replace Your Oil Furnace",
            "Oil Heating Installation", "Trained HVAC Technicians",
            "Schedule an Assessment", "Oil Furnace Fitting",
            "Request Oil Furnace Info"],
      "d": ["Oil furnace installation for homes across Severn, Severna Park and Columbia.",
            "We size the system to your home and explain the options clearly.",
            "Book an oil furnace assessment with Ambient Cooling and Heating.",
            "Experienced oil furnace installation across Central Maryland."]},
     {"label": "RSA B - outcome-led",
      "h": ["Need a New Oil Furnace?", "Old Oil Furnace Failing?",
            "Upgrade Your Oil Furnace", "Oil Furnace Install Quote",
            "Warm Home This Winter", "Oil Furnace Installation",
            "Maryland Oil Furnace Fitters", "Book an Oil Furnace Visit",
            "Talk to an Installer", "Oil Heat Done Properly",
            "Severn Oil Furnace Install", "Columbia Oil Furnace Install",
            "Clear Installation Options", "Sized for Your Home",
            "Request an Assessment"],
      "d": ["Planning a new oil furnace in Central Maryland? Speak to our installers.",
            "We assess your home, size the furnace and explain each option.",
            "Oil furnace installation for Severn, Severna Park and Columbia homes.",
            "Book an oil furnace installation assessment with Ambient."]}]},

 "SKAG | Oil Heating System Replacement": {
   "campaign_key": "INSTALL", "existing_campaign_id": "24257819466",
   "url": "https://ambientcoolingandheating.com/services/heating-services/oil-replacement/",
   "cpc_bid": 30.00,
   "phrase": ["oil furnace replacement", "replace oil furnace cost",
              "oil heating system replacement"],
   "exact": ["oil furnace replacement", "oil heating system replacement"],
   "evidence": "Page H1 'Outstanding Oil Replacement' and body text 'helps homeowners "
               "replace aging oil equipment' - replacement intent, distinct from the "
               "installation page. 'oil boiler replacement' DROPPED: blocked by the PHRASE "
               "cross-negative 'boiler' on this campaign, which is routing boiler queries "
               "to the boiler campaign correctly.",
   "rsas": [
     {"label": "RSA A - service-first",
      "h": ["Oil Heating Replacement", "Replace Your Oil System",
            "Oil Furnace Replacement", "Severn Oil Replacement",
            "Severna Park Oil Heating", "Columbia Oil Replacement",
            "Aging Oil System?", "Oil System Assessment",
            "Central Maryland Oil Heat", "Book an Oil Assessment",
            "Oil Heating Specialists", "Trained HVAC Technicians",
            "Plan Your Replacement", "Oil Equipment Replacement",
            "Request Replacement Info"],
      "d": ["Replace aging oil heating equipment before the cold weather arrives.",
            "We assess your current system and explain the replacement options.",
            "Oil heating replacement for Severn, Severna Park and Columbia.",
            "Book an oil system assessment with Ambient Cooling and Heating."]},
     {"label": "RSA B - timing-led",
      "h": ["Oil System Near the End?", "Replace Before Winter",
            "Oil Heating Replacement", "Old Oil Equipment?",
            "Upgrade Oil Heating", "Oil Replacement Quote",
            "Maryland Oil Heating", "Book an Assessment",
            "Talk to a Technician", "Plan the Replacement",
            "Severn Oil Heating Help", "Columbia Oil Heating Help",
            "Clear Replacement Options", "Oil System Review",
            "Request an Assessment"],
      "d": ["Oil systems give little warning before they fail. Plan the replacement early.",
            "We review your oil equipment and set out the replacement options.",
            "Oil heating replacement across Central Maryland homes.",
            "Schedule an oil system assessment with Ambient today."]}]},

 "SKAG | Heat Pump Installation": {
   "campaign_key": "HEATPUMP", "existing_campaign_id": None,
   "url": "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/",
   "cpc_bid": 40.00,
   "phrase": ["heat pump installation", "heat pump installers near me"],
   "exact": ["heat pump installation", "heat pump installers near me"],
   "pruned_2026_09_21": {
     "phrase_removed": ["heat pump installation cost"],
     "exact_removed": [],
     "why": "Strict subset of PHRASE 'heat pump installation'. 'installers' is a "
            "different head noun and is retained."},
   "evidence": "Planner 10-city sample: 50/mo for the installation bucket, the strongest of "
               "the six new themes. Legacy 'Water Source Heat Pump' CPC $44.93 on 3 clicks.",
   "rsas": [],
   "BLOCKED": "DESTINATION_NOT_WORKING on the required URL, 3/3 validate_only trials "
              "2026-09-18 (and 4/4 on 2026-09-17). Ad group and keywords are created PAUSED "
              "so the structure exists, but NO RSA is included - the API rejects any ad "
              "pointing at this URL, which would abort the whole batch. An ad group with no "
              "ads cannot serve. Do not enable until the page is fixed, a policy re-review "
              "is requested in the Google Ads UI, and RSAs are added under a later plan. "
              "A different URL must NOT be substituted."},

 "SKAG | Geothermal HVAC Installation": {
   "campaign_key": "HEATPUMP", "existing_campaign_id": None,
   "url": "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/",
   "cpc_bid": 40.00,
   "phrase": ["geothermal hvac installation", "geothermal heat pump installation",
              "geothermal system installation"],
   "exact": ["geothermal hvac installation", "geothermal heat pump installation"],
   "evidence": "CONTROLLED TEST. Legacy 'Geothermal HVAC': $151.80 / 4 clicks / 0 "
               "conversions, CPC $37.95; plus $134.80 on 'Water Source Heat Pump', 0 "
               "conversions. Combined $286.60 with zero conversions is why the service sits "
               "in client.yaml services_excluded. Included at owner instruction as a tightly "
               "controlled test with an explicit stop-loss.",
   "rsas": [
     {"label": "RSA A - service-first",
      "h": ["Geothermal HVAC Install", "Geothermal Heat Pumps",
            "Severn Geothermal HVAC", "Severna Park Geothermal",
            "Columbia MD Geothermal", "Geothermal Installation",
            "Ground Source Heat Pumps", "Central Maryland Geothermal",
            "Book a Geothermal Review", "Geothermal System Fitting",
            "Trained HVAC Technicians", "Energy Efficient Heating",
            "Geothermal Assessment", "Year Round Comfort",
            "Request Geothermal Info"],
      "d": ["Geothermal HVAC installation for homes across Central Maryland.",
            "We assess the site and explain how a geothermal system would work.",
            "Geothermal heating and cooling for Severn, Severna Park and Columbia.",
            "Book a geothermal assessment with Ambient Cooling and Heating."]},
     {"label": "RSA B - efficiency-led",
      "h": ["Considering Geothermal?", "Ground Source Heating",
            "Geothermal HVAC Install", "Efficient Year Round Comfort",
            "Geothermal for Your Home", "Maryland Geothermal HVAC",
            "Book a Site Assessment", "Talk to a Technician",
            "Geothermal Heat Pumps", "Sustainable Home Heating",
            "Severn Geothermal Install", "Columbia Geothermal Install",
            "Clear System Options", "Geothermal Explained",
            "Request an Assessment"],
      "d": ["Geothermal taps underground temperatures to heat and cool your home.",
            "We assess your property and set out whether geothermal suits it.",
            "Geothermal HVAC installation across Severn, Severna Park and Columbia.",
            "Schedule a geothermal consultation with Ambient today."]}]},

 "SKAG | Tankless Water Heater Installation": {
   "campaign_key": "TANKLESS", "existing_campaign_id": None,
   "url": "https://ambientcoolingandheating.com/services/heating-services/tankless-water-heaters/",
   "cpc_bid": 35.00,
   "phrase": ["tankless water heater installation",
              "tankless water heater installers near me"],
   "exact": ["tankless water heater installation"],
   "pruned_2026_09_21": {
     "phrase_removed": ["tankless water heater installation cost"],
     "exact_removed": [],
     "why": "Strict subset of PHRASE 'tankless water heater installation'."},
   "evidence": "CONTROLLED TEST. Legacy 'Tankless Water Heaters': $12,531.77 / 268 clicks / "
               "2 conversions, CPC $46.76, CPA $6,265.89 - the worst measured economics in "
               "the account and the reason it sits in client.yaml services_excluded. "
               "Included at owner instruction, isolated in its own campaign, tightly capped, "
               "with an explicit stop-loss. Page covers installation and maintenance.",
   "rsas": [
     {"label": "RSA A - service-first",
      "h": ["Tankless Water Heaters", "Tankless Install Severn",
            "Severna Park Tankless", "Columbia MD Tankless",
            "Tankless Installation", "Endless Hot Water",
            "Tankless Water Heater Fit", "Central Maryland Tankless",
            "Book a Tankless Quote", "Tankless Specialists",
            "Trained HVAC Technicians", "Space Saving Hot Water",
            "Tankless Assessment", "Energy Efficient Hot Water",
            "Request Tankless Info"],
      "d": ["Tankless water heater installation for Central Maryland homes.",
            "Tankless models heat water on demand rather than storing a hot tank.",
            "Tankless installation for Severn, Severna Park and Columbia.",
            "Book a tankless water heater assessment with Ambient."]},
     {"label": "RSA B - benefit-led",
      "h": ["Tired of Running Out?", "Switch to Tankless",
            "Endless Hot Water at Home", "Tankless Water Heaters",
            "Tankless Install Quote", "Save Space in Your Home",
            "Maryland Tankless Fitting", "Book an Assessment",
            "Talk to a Technician", "Tankless Explained",
            "Severn Tankless Install", "Columbia Tankless Install",
            "Clear Install Options", "Efficient Hot Water",
            "Request an Assessment"],
      "d": ["Tankless units heat water on demand instead of storing it in a tank.",
            "A compact tankless unit frees the space a storage tank takes up.",
            "Tankless water heater installation across Central Maryland.",
            "Schedule a tankless consultation with Ambient Cooling and Heating."]}]},
}


# --------------------------------------------------- ad-group cross-negatives
# PHRASE only. The instruction forbids campaign-level broad negatives, and BROAD subsumes
# PHRASE by word-subset, which over-blocks. These sit on the AD GROUP so they steer routing
# without touching any other ad group. Tested 2026-09-20 against every positive keyword
# (zero self-blocks) and against all 69 historically converting heating queries - every
# exclusion routes the query to the ad group that owns that service.
XNEG = {
 "SKAG | Furnace Repair":
   {"existing_ad_group_id": "199797580706", "status": "PAUSED",
    "negatives": ["oil", "boiler", "heat pump", "tankless", "geothermal", "mini split"]},
 "SKAG | Mini Split Installation":
   {"existing_ad_group_id": "199797580746", "status": "PAUSED",
    "negatives": ["heat pump", "geothermal", "boiler", "furnace", "tankless"]},
 "SKAG | Gas Boiler Repair":
   {"existing_ad_group_id": "202339087594", "status": "ENABLED",
    "negatives": ["oil", "tankless", "furnace", "heat pump"],
    "live_change_note": "This ad group is ENABLED. The four negatives are additive and none "
                        "matches its only keyword 'gas boiler repair', so no existing traffic "
                        "is lost; they prevent collision with the new Boiler Repair ad group "
                        "in the same campaign."},
 "SKAG | Boiler Repair":
   {"new": True, "negatives": ["gas", "oil", "tankless", "furnace", "heat pump"],
    "why_gas": "Routes gas-boiler queries to the existing Gas Boiler Repair ad group, which "
               "owns that theme and its own offer-subdomain landing page."},
 "SKAG | Oil Furnace Installation":
   {"new": True, "negatives": ["repair", "replacement", "boiler", "heat pump", "tankless",
                               "mini split"]},
 "SKAG | Oil Heating System Replacement":
   {"new": True, "negatives": ["repair", "installation", "tankless", "mini split",
                               "heat pump"]},
 "SKAG | Heat Pump Installation":
   {"new": True, "negatives": ["geothermal", "mini split", "ductless", "boiler", "furnace",
                               "tankless", "repair"]},
 "SKAG | Geothermal HVAC Installation":
   {"new": True, "negatives": ["mini split", "ductless", "boiler", "furnace", "tankless",
                               "repair"],
    "why_no_heat_pump_negative": "'geothermal heat pump installation' is one of this ad "
                                 "group's own keywords, so 'heat pump' must NOT be negated "
                                 "here. The one-way split is enforced from the Heat Pump ad "
                                 "group, which negates 'geothermal'."},
 "SKAG | Tankless Water Heater Installation":
   {"new": True, "negatives": ["boiler", "furnace", "heat pump", "mini split", "geothermal",
                               "repair"]},
}

# --------------------------------------------------------------- new campaigns
NEW_CAMPAIGNS = {
 "HEATPUMP": {"name": "Search | NonBrand | Heat Pump & Geothermal | Central MD | BOFU | 2026-09",
              "daily_budget": 18.00, "cpc_ceiling": 40.00,
              "ceiling_basis": "Legacy geothermal CPC $37.95 and water-source heat pump "
                               "$44.93. $40 sits between them so the campaign can clear the "
                               "auction without chasing the uncapped-Max-Clicks era prices.",
              "controlled_test": "Geothermal is a controlled test. STOP-LOSS: pause the "
                                 "geothermal ad group once it has spent $250 with zero "
                                 "qualified leads. Heat pump cannot serve until its page is "
                                 "fixed."},
 "TANKLESS": {"name": "Search | NonBrand | Tankless Water Heaters | Central MD | BOFU | 2026-09",
              "daily_budget": 12.00, "cpc_ceiling": 35.00,
              "ceiling_basis": "Legacy tankless CPC $46.76. $35 deliberately sits below it "
                               "to cap exposure on a service with a $6,265.89 historical "
                               "CPA, accepting lower impression share as the trade.",
              "controlled_test": "CONTROLLED TEST, isolated by instruction. STOP-LOSS: pause "
                                 "the campaign once it has spent $250 with zero qualified "
                                 "leads. At $12/day and a $35 ceiling it buys roughly one "
                                 "click every three days - deliberate."},
}

# ------------------------------------------------------- budget reallocation
BUDGET = [
 {"campaign": "Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08",
  "campaign_id": "24132507747", "budget_id": "15787409441", "from": 95.00, "to": 55.00,
  "why": "Best conversion volume in the account, but cooling-season installation demand "
         "falls through autumn. Settled September delivery is $45.44/day, so $55 still "
         "exceeds actual spend."},
 {"campaign": "Search | NonBrand | HVAC Repair | Central MD | BOFU | 2026-08",
  "campaign_id": "24132507750", "budget_id": "15787409444", "from": 70.00, "to": 55.00,
  "why": "Best CPA in the account ($277.53) and year-round repair demand. Protected: "
         "trimmed only $15 and still above its $17.92/day settled delivery."},
 {"campaign": "Search | NonBrand | AC Repair | Central MD | BOFU | 2026-08",
  "campaign_id": "24132507741", "budget_id": "15787409435", "from": 45.00, "to": 25.00,
  "why": "Cut first and deepest, as instructed. Worst measured economics in the account "
         "(CPA $637.65 August, $534.28 September) and the most expensive clicks ($106+ CPC "
         "in both windows), against falling autumn cooling demand. NOT eliminated - repair "
         "coverage is retained."},
 {"campaign": "Search | NonBrand | HVAC Replacement | Central MD | BOFU | 2026-08",
  "campaign_id": "24132507753", "budget_id": "15787409447", "from": 15.00, "to": 12.00,
  "why": "Zero September delivery and zero conversions in both windows. Small trim only; "
         "replacement jobs carry high ticket value and the campaign stays reachable."},
 {"campaign": "Search | NonBrand | Gas Boiler Repair | Central MD | BOFU | 2026-08",
  "campaign_id": "24132507744", "budget_id": "15787409438", "from": 12.00, "to": 38.00,
  "why": "INCREASE. This campaign becomes the boiler campaign and will carry two ad groups "
         "(existing Gas Boiler Repair plus the new Boiler Repair). Boiler clicks have "
         "historically cleared at $89.90-$106.03, so $12/day could never buy one."},
 {"campaign": "Search | NonBrand | Heating Installation | Central MD | BOFU | 2026-09",
  "campaign_id": "24257819466", "budget_id": "15885327975", "from": 35.00, "to": 55.00,
  "why": "INCREASE. Goes from one ad group to three (Mini Split, Oil Furnace Installation, "
         "Oil Heating System Replacement). $35 split three ways could not fund a single "
         "$25 mini-split click per day."},
]
UNCHANGED_BUDGET = [
 {"campaign": "Search | NonBrand | Heating Repair | Central MD | BOFU | 2026-09",
  "campaign_id": "24257819463", "budget_id": "15885327972", "daily": 55.00,
  "why": "Unchanged. Still one ad group (Furnace Repair). Legacy Heating Repair is the best "
         "converting heating theme in the account: 35 conversions at CPA $339.37."},
]

# --------------------------------------------------------------- bid ceilings
BIDS = [
 {"campaign": "Search | NonBrand | Gas Boiler Repair | Central MD | BOFU | 2026-08",
  "campaign_id": "24132507744", "from": 25.00, "to": 60.00,
  "why": "The live campaign has spent $12.84 on ONE click since launch because the $25 "
         "ceiling sits far below the boiler clearing price. Legacy boiler CPCs were $89.90 "
         "(repair) and $106.03 (installs), though both ran under the uncapped Maximize "
         "Clicks regime that inflated prices, so $60 is a deliberate midpoint rather than a "
         "return to historical levels. Without this, the budget increase buys nothing.",
  "risk": "Raises cost per click on an ENABLED campaign. Bounded by the $38/day budget."},
 {"campaign": "Search | NonBrand | Heating Installation | Central MD | BOFU | 2026-09",
  "campaign_id": "24257819466", "from": 24.00, "to": 30.00,
  "why": "Mini Split has cleared at $25.15 all-time, just ABOVE the current $24 ceiling, so "
         "the campaign is priced out of its own best theme. $30 restores participation.",
  "risk": "Campaign is PAUSED, so no immediate spend effect."},
]


def vlen(s):
    return len(s)


def validate():
    errs = []
    for ag, d in AG.items():
        seen_h, seen_d = set(), set()
        for rsa in d["rsas"]:
            if len(rsa["h"]) != 15:
                errs.append(f"{ag}/{rsa['label']}: {len(rsa['h'])} headlines, need 15")
            if len(rsa["d"]) != 4:
                errs.append(f"{ag}/{rsa['label']}: {len(rsa['d'])} descriptions, need 4")
            for h in rsa["h"]:
                if vlen(h) > 30:
                    errs.append(f"{ag}/{rsa['label']}: headline {vlen(h)}>30 '{h}'")
            for x in rsa["d"]:
                if vlen(x) > 90:
                    errs.append(f"{ag}/{rsa['label']}: description {vlen(x)}>90 '{x}'")
            if len(set(rsa["h"])) != len(rsa["h"]):
                errs.append(f"{ag}/{rsa['label']}: duplicate headline within the RSA")
            if len(set(rsa["d"])) != len(rsa["d"]):
                errs.append(f"{ag}/{rsa['label']}: duplicate description within the RSA")
            for label, rx in BARRED.items():
                for t in rsa["h"] + rsa["d"]:
                    if rx.search(t):
                        errs.append(f"{ag}/{rsa['label']}: BARRED CLAIM '{label}' in '{t}'")
            seen_h |= set(rsa["h"]); seen_d |= set(rsa["d"])
        if len(d["rsas"]) == 2:
            a, b = d["rsas"]
            if set(a["h"]) == set(b["h"]):
                errs.append(f"{ag}: RSA A and B are not differentiated")
        for k in d["phrase"] + d["exact"]:
            if k != k.lower().strip():
                errs.append(f"{ag}: keyword not normalised '{k}'")
    return errs


errs = validate()
print("=== RSA / KEYWORD VALIDATION ===")
if errs:
    for e in errs:
        print(f"  FAIL {e}")
    print(f"\n{len(errs)} problems. Plans NOT fingerprinted.")
    sys.exit(1)
print("  PASS - character limits, counts, duplication, barred claims, normalisation")

# --------------------------------------------------------------- budget maths
existing_after = sum(b["to"] for b in BUDGET if b["campaign_id"] in
                     ("24132507747", "24132507750", "24132507741", "24132507753",
                      "24132507744"))
heating_after = (sum(b["to"] for b in BUDGET if b["campaign_id"] == "24257819466")
                 + sum(u["daily"] for u in UNCHANGED_BUDGET)
                 + sum(v["daily_budget"] for v in NEW_CAMPAIGNS.values()))
total_after = round(existing_after + heating_after, 2)
print("\n=== BUDGET MATHS ===")
print(f"  existing five (after)     ${existing_after:7.2f}/day")
print(f"  heating four (after)      ${heating_after:7.2f}/day")
print(f"  TOTAL when all enabled    ${total_after:7.2f}/day")
print(f"  monthly equivalent        ${total_after * 30.4:,.2f}  (cap ${CAP_MONTH:,.0f})")
print(f"  vs daily cap ${CAP_DAY}     headroom ${CAP_DAY - total_after:.2f}")
assert total_after <= CAP_DAY, f"{total_after} exceeds {CAP_DAY}"
assert total_after * 30.4 <= CAP_MONTH, "monthly over cap"

n_kw = sum(len(d["phrase"]) + len(d["exact"]) for d in AG.values())
n_rsa = sum(len(d["rsas"]) for d in AG.values())

base = {"customer_id": CID, "exact_account_name": EXACT_NAME,
        "never_write_to_mcc": GM_MANAGER, "built_local": STAMP}

# September pacing is read from the live read-only basis snapshot, never hardcoded,
# so a plan built on a later account date cannot carry an earlier day's arithmetic.
BASIS = json.loads((SNAP / f"budget-basis-{STAMP}.json").read_text(encoding="utf-8"))
SEP = BASIS["september"]
assert BASIS["account_today"].startswith(STAMP), (
    f"basis snapshot is for {BASIS['account_today']}, not {STAMP}")
MTD = SEP["mtd_incl_partial_today"]
DAYS_LEFT = SEP["days_left_incl_today"]
RESERVE = SEP["reserve_10pct"]
WORST = round(MTD + total_after * DAYS_LEFT, 2)

# ---------------------------------------------------------------- campaign assets
# Every comparable campaign in this account carries 5 callouts, 1 structured snippet and
# 3-8 sitelinks alongside the call and business-name assets (verified 2026-09-21,
# snapshots/asset-audit-2026-09-21.json). Linking only CALL + BUSINESS_NAME would launch
# the two new campaigns below the account's own standard, so the gap is closed here.
#
# Callouts and sitelinks are REUSED, never duplicated - all five callouts and all four
# sitelinks below read APPROVED / REVIEWED on 2026-09-21
# (snapshots/asset-policy-2026-09-21.json).
#
# No sitelink may point at the heat-pumps URL: 11 existing sitelink assets do, and while
# none is currently on an ENABLED campaign, adding one to a new campaign would import the
# DESTINATION_NOT_WORKING defect.
REUSE_CALLOUTS = [
    "422477374526",   # Homes and Businesses
    "422577760603",   # Central Maryland Service
    "422577771364",   # Trained Technicians
    "422577777430",   # Diagnosis Explained
    "422577777442",   # Repair and Maintenance
]
REUSE_SITELINKS = {
    # Service-specific and relevant. Deliberately NO heat-pumps sitelink.
    "HEATPUMP": [
        ("185161619511", "Geothermal HVAC",
         "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/"),
        ("422577777457", "Heating Services",
         "https://ambientcoolingandheating.com/services/heating-services/"),
        ("422477374559", "Mini Splits",
         "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/"),
    ],
    "TANKLESS": [
        ("422577777457", "Heating Services",
         "https://ambientcoolingandheating.com/services/heating-services/"),
        ("422577771382", "Furnace Repair",
         "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/"),
        ("422477374559", "Mini Splits",
         "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/"),
    ],
}
# The one existing structured snippet lists Furnace Repair / Mini Split / Boiler Repair /
# Heating Maintenance / Ductless Systems - none of which is what either new campaign sells.
# Two new campaign-relevant snippets are created instead. Every value names a service with
# its own verified page on the site.
NEW_SNIPPETS = {
    "HEATPUMP": {"header": "Services",
                 "values": ["Heat Pump Installation", "Geothermal HVAC",
                            "Mini Split Installation", "Furnace Repair"]},
    "TANKLESS": {"header": "Services",
                 "values": ["Tankless Water Heaters", "Boiler Repair",
                            "Furnace Repair", "Mini Split Installation"]},
}

expand = dict(base, **{
 "plan_name": "AMB-0921-HEAT-EXPAND-1", "approval_class": "create-paused",
 "everything_created_paused": True, "nothing_enabled": True,
 "reuses_not_duplicates": {
   "campaigns": {"BOILER": "24132507744 (existing ENABLED Gas Boiler Repair campaign)",
                 "REPAIR": "24257819463 (existing PAUSED, untouched by this plan)",
                 "INSTALL": "24257819466 (existing PAUSED)"},
   "ad_groups_already_live_not_recreated": {
     "SKAG | Furnace Repair": "199797580706",
     "SKAG | Mini Split Installation": "199797580746",
     "SKAG | Gas Boiler Repair": "202339087594"},
   "assets": {"call": "407995613637 = (410) 705-6354",
              "business_name": "80516971145",
              "callouts": "5 reused, all APPROVED/REVIEWED 2026-09-21",
              "sitelinks": "3 reused per new campaign, all APPROVED/REVIEWED 2026-09-21",
              "structured_snippets": "2 created, one per new campaign, because the single "
                                     "existing snippet lists none of the services these "
                                     "campaigns sell",
              "sitelink_safety": "No sitelink points at the heat-pumps URL. 11 existing "
                                 "sitelink assets do; none is on an ENABLED campaign "
                                 "(checked 2026-09-21) and none is reused here."}},
 "new_campaigns": NEW_CAMPAIGNS,
 "new_ad_groups": AG,
 "keyword_total": n_kw, "rsa_total": n_rsa,
 "cross_negatives": XNEG,
 "cross_negative_total": sum(len(d["negatives"]) for d in XNEG.values()),
 "cross_negative_tests_2026_09_20": {
   "self_block_check": "PASS - no cross-negative blocks its own ad group's keywords",
   "historically_converting_heating_queries_tested": 69,
   "method": "PHRASE containment against every distinct heating search term with conversions > 0 since 2024-01-01. Raw search terms were never printed or retained.",
   "verdict": "Every exclusion routes the query to the ad group that owns that service."},
 "search_settings": {"network": "Google Search only", "search_partners": False,
                     "display": False, "ai_max": False, "dsa": False,
                     "broad_match_expansion": False, "final_url_expansion": False,
                     "automatically_created_assets": False, "text_customization": False,
                     "geo": "PRESENCE / PRESENCE", "locations": "75 approved Central MD",
                     "schedule": "6 approved business-hour rows",
                     "match_types": ["PHRASE", "EXACT"],
                     "contains_eu_political_advertising":
                         "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"},
 "blocked_within_this_plan": {
   "SKAG | Heat Pump Installation": AG["SKAG | Heat Pump Installation"]["BLOCKED"]},
 "landing_page_defect_noted": {
   "url": "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/",
   "issue": "Page copy claims 'most knowledgeable and experienced experts' and 'Top "
            "Geothermal HVAC Technicians'. Both are barred superlatives. No RSA mirrors "
            "them, but the page itself should be corrected.",
   "launch_blocking": False},
})
expand["operations"] = (
  [{"op": "CREATE_CAMPAIGN_BUDGET", "campaign_key": k, "amount_usd": v["daily_budget"]}
   for k, v in NEW_CAMPAIGNS.items()]
+ [{"op": "CREATE_CAMPAIGN_PAUSED", "campaign_key": k, "name": v["name"],
    "cpc_bid_ceiling_usd": v["cpc_ceiling"]} for k, v in NEW_CAMPAIGNS.items()]
+ [{"op": "ADD_CAMPAIGN_LOCATIONS", "campaign_key": k, "count": 75} for k in NEW_CAMPAIGNS]
+ [{"op": "ADD_CAMPAIGN_AD_SCHEDULE", "campaign_key": k, "count": 6} for k in NEW_CAMPAIGNS]
+ [{"op": "CREATE_AD_GROUP_PAUSED", "ad_group": ag, "campaign_key": d["campaign_key"],
    "final_url": d["url"], "cpc_bid_usd": d["cpc_bid"]} for ag, d in AG.items()]
+ [{"op": "ADD_KEYWORDS_PAUSED", "ad_group": ag,
    "phrase": d["phrase"], "exact": d["exact"],
    "count": len(d["phrase"]) + len(d["exact"])} for ag, d in AG.items()]
+ [{"op": "CREATE_RSA_PAUSED", "ad_group": ag, "label": r["label"],
    "final_url": d["url"], "headlines": r["h"], "descriptions": r["d"]}
   for ag, d in AG.items() for r in d["rsas"]]
+ [{"op": "ADD_AD_GROUP_CROSS_NEGATIVES", "ad_group": ag,
    "existing_ad_group_id": d.get("existing_ad_group_id"),
    "match_type": "PHRASE", "negatives": d["negatives"], "count": len(d["negatives"])}
   for ag, d in XNEG.items()]
+ [{"op": "LINK_EXISTING_CALL_ASSET_PAUSED", "asset_id": "407995613637",
    "campaign_key": k} for k in NEW_CAMPAIGNS]
+ [{"op": "LINK_EXISTING_BUSINESS_NAME_ASSET_PAUSED", "asset_id": "80516971145",
    "campaign_key": k} for k in NEW_CAMPAIGNS]
+ [{"op": "LINK_EXISTING_CALLOUT_ASSETS", "campaign_key": k,
    "asset_ids": REUSE_CALLOUTS, "count": len(REUSE_CALLOUTS),
    "reused_not_created": True} for k in NEW_CAMPAIGNS]
+ [{"op": "LINK_EXISTING_SITELINK_ASSETS", "campaign_key": k,
    "sitelinks": [{"asset_id": a, "text": t, "final_url": u}
                  for a, t, u in REUSE_SITELINKS[k]],
    "count": len(REUSE_SITELINKS[k]), "reused_not_created": True,
    "no_blocked_url": all(
        u.rstrip("/") != "https://ambientcoolingandheating.com/services/"
                         "heating-services/heat-pumps".rstrip("/")
        for _, _, u in REUSE_SITELINKS[k])} for k in NEW_CAMPAIGNS]
+ [{"op": "CREATE_STRUCTURED_SNIPPET_AND_LINK", "campaign_key": k,
    "header": NEW_SNIPPETS[k]["header"], "values": NEW_SNIPPETS[k]["values"],
    "count": 1} for k in NEW_CAMPAIGNS])

expand["operation_count"] = len(expand["operations"])
expand["fingerprint"] = approval_code(expand)

budget2 = dict(base, **{
 "plan_name": "AMB-0921-BUDGET-1", "approval_class": "update-existing-budgets",
 "supersedes_allocation_of": "AMB-0918-BUDGET-1 (already executed; this is a NEW allocation, "
                             "not a replay)",
 "math": {"permanent_daily_ceiling": CAP_DAY, "monthly_cap": CAP_MONTH,
          "working_target": WORKING_TARGET,
          "existing_five_after": round(existing_after, 2),
          "heating_four_after": round(heating_after, 2),
          "total_when_all_enabled": total_after,
          "monthly_equivalent": round(total_after * 30.4, 2),
          "headroom_under_daily_cap": round(CAP_DAY - total_after, 2),
          "september_read_on": BASIS["account_today"],
          "september_mtd_spend_incl_partial_today": MTD,
          "september_settled_calendar_days": SEP["settled_calendar_days"],
          "september_days_with_any_delivery": SEP["days_with_delivery"],
          "september_settled_daily_avg_calendar": SEP["settled_daily_avg"],
          "september_last7_calendar_daily_avg": SEP["last7_daily_avg"],
          "september_days_left_incl_today": DAYS_LEFT,
          "september_remaining_allowance": SEP["remaining_allowance"],
          "september_reserve_10pct": RESERVE,
          "september_max_safe_daily_pace": SEP["max_safe_daily_pace"],
          "september_projection_worst_case": WORST,
          "september_projection_worst_plus_reserve": round(WORST + RESERVE, 2),
          "september_projection_evidence_case":
              round(MTD + SEP["last7_daily_avg"] * DAYS_LEFT, 2),
          "september_under_10k_worst_case": (WORST + RESERVE) <= CAP_MONTH,
          "projection_basis": "Worst case assumes every enabled budget spends in full on "
                              "every remaining day. Evidence case continues the observed "
                              "last-7 calendar-day delivery rate. Neither is a forecast of "
                              "leads, CPL, CPQL, revenue or profit."},
 "changes": BUDGET, "unchanged": UNCHANGED_BUDGET,
 "no_incremental_budget": "Every dollar for heating comes from cooling reductions. Total "
                          "account budget does not increase.",
 "honest_limitation": "These are ceilings, not spend predictions. Measured September "
                      "delivery is $87.32/day averaged over 20 settled calendar days and "
                      "$49.13/day over the last 7, against $237.00/day of enabled budget - "
                      "the account is not spending what it already has. Impression share "
                      "lost to BUDGET is 0.0-8.9% on four of the five enabled campaigns "
                      "while share lost to RANK is 43.6-67.3%, so the binding constraint is "
                      "the CPC bid ceiling, not the budget. Gas Boiler Repair is the single "
                      "exception at 31.2% lost to budget. Reallocation is therefore a "
                      "necessary guardrail and a correct architecture, but on its own it "
                      "will not move delivery. No CPL, CPQL, lead-volume, revenue or "
                      "profitability improvement is claimed.",
 "operations": [{"op": "UPDATE_CAMPAIGN_BUDGET_AMOUNT", "budget_id": b["budget_id"],
                 "campaign": b["campaign"], "from_usd": b["from"], "to_usd": b["to"],
                 "field_mask": "amount_micros"} for b in BUDGET]})
budget2["operation_count"] = len(budget2["operations"])
budget2["fingerprint"] = approval_code(budget2)

bid1 = dict(base, **{
 "plan_name": "AMB-0921-BID-1", "approval_class": "update-cpc-bid-ceiling",
 "why_separate": "These are BID changes, not budget changes. One lands on an ENABLED "
                 "campaign and raises cost per click, so it is listed as its own approval "
                 "category rather than folded into the budget plan.",
 "changes": BIDS,
 "operations": [{"op": "UPDATE_CAMPAIGN_CPC_BID_CEILING", "campaign_id": b["campaign_id"],
                 "campaign": b["campaign"], "from_usd": b["from"], "to_usd": b["to"],
                 "field_mask": "target_spend.cpc_bid_ceiling_micros"} for b in BIDS]})
bid1["operation_count"] = len(bid1["operations"])
bid1["fingerprint"] = approval_code(bid1)

PLANS.mkdir(parents=True, exist_ok=True)
for p in (expand, budget2, bid1):
    (PLANS / f"{p['plan_name']}.json").write_text(
        json.dumps(p, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {PLANS / (p['plan_name'] + '.json')}")
    print(f"  APPROVE {p['plan_name']} {p['fingerprint']} {p['operation_count']} "
          f"operations FOR {CID}")
print(f"\nkeywords={n_kw}  rsas={n_rsa}  new ad groups={len(AG)}  "
      f"new campaigns={len(NEW_CAMPAIGNS)}")
print("EXTERNAL WRITES: 0 (local draft only)")
