#!/usr/bin/env python3
"""Ambient | 2026-09-22 | EXECUTION build for the heating transition. LOCAL DRAFT ONLY.

EXTERNAL WRITES: 0. Produces the manifest + fingerprints that the executor consumes.

Changes from the 2026-09-21b draft, each forced by new evidence:

  1. SCHEDULE. Ambient PUBLISHES Mon-Fri 08:00-16:00, closed Sat and Sun - in visible copy
     and in schema.org OpeningHoursSpecification. The live account schedule
     (Mon-Fri 08:00-20:00 + Sat 08:00-13:00) is an ADVERTISING schedule a human entered in
     the web client on 2026-08-17, not evidence of answered hours. All heating campaigns
     and the shared call asset move to 5 rows, Mon-Fri 08:00-16:00.

  2. DESTINATIONS. The offer subdomain carries purpose-built HVAC Installation and HVAC
     Replacement conversion pages whose own copy is explicitly about "heating and cooling
     system" installation and replacement. Under the family-page standard those are the
     right homes for Heating/Furnace Installation and Heating Replacement. The heating hub
     carries real maintenance, tune-up and inspection copy. That moves 6 ad groups from
     "no page" to "ready".

  3. THERMOSTAT capability is confirmed by the owner, but no page covers it, so the three
     thermostat ad groups are built PAUSED with RSA payloads prepared for later upload.

  4. BUDGETS follow serving capacity: money goes to campaigns that can actually deliver.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

STAMP = "2026-09-22"
CAP_DAY, CAP_MONTH, WORKING_TARGET = 328.94, 10000.00, 325.00

# --------------------------------------------------------------- destinations
U_FURNACE = "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/"
U_HUB = "https://ambientcoolingandheating.com/services/heating-services/"
U_BOILER = "https://ambientcoolingandheating.com/services/heating-services/boiler-repair/"
U_GASBOILER = "https://offer.ambientcoolingandheating.com/gas-boiler-repair/"
U_HEATPUMP = "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/"
U_MINISPLIT = "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/"
U_GEO = "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/"
U_OFFER_INSTALL = "https://offer.ambientcoolingandheating.com/hvac-installation/"
U_OFFER_REPLACE = "https://offer.ambientcoolingandheating.com/hvac-replacement/"

# Verified answered hours. 5 rows, Monday to Friday, 08:00-16:00.
SCHEDULE = [{"day": d, "start_hour": 8, "end_hour": 16}
            for d in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY")]

AG = {}


def rsa(h, d, label):
    return {"label": label, "h": h, "d": d}


def ag(name, ck, url, bid, phrase, exact, evidence, rsas=None, existing=None,
       rename_from=None, verdict="READY", gate=None, services=None,
       remove_keywords=None, page_evidence=None):
    AG[name] = {"campaign_key": ck, "url": url, "cpc_bid": bid, "phrase": phrase,
                "exact": exact, "evidence": evidence, "rsas": rsas or [],
                "existing_ad_group_id": existing, "rename_from": rename_from,
                "verdict": verdict, "launch_gate": gate,
                "remove_keywords": remove_keywords or [],
                "page_evidence": page_evidence,
                "services_covered": services or [name.split("| ")[-1]]}


L_SERV = "RSA A - service and location led"
L_PROB = "RSA B - problem led"
L_SEAS = "RSA B - seasonal led"

# ===================== C1 - HEATING & FURNACE REPAIR =========================
ag("SKAG | Furnace Repair", "C1", U_FURNACE, 42.00, [], [],
   "EXISTING 199797580706. 10 keywords APPROVED/ELIGIBLE, 2 RSAs APPROVED/REVIEWED. "
   "Account search terms: $2,084.77 / 50 clicks / 5 conversions, CPC $41.70.",
   existing="199797580706", services=["Furnace Repair"],
   remove_keywords=[("gas furnace repair", "PHRASE"), ("gas furnace repair", "EXACT")],
   page_evidence="H1 'Furnace Repair in Severn...', 21 repair sentences, 18 furnace.")

ag("SKAG | Heating Repair", "C1", U_HUB, 42.00,
   ["heating repair", "heater repair"],
   ["heating repair", "heater repair", "heating repair service", "residential heating repair"],
   "Largest converting heating theme in the account: $14,662.48 / 1,416 clicks / "
   "34 conversions, CPC $10.35, CPA $431.25.",
   page_evidence="Heating hub, H2 'Heating Services from Professionals You Can Trust', "
                 "19 generic heating-service sentences.",
   rsas=[rsa(["Heating Repair Central MD", "Heating Repair in Severn", "Severna Park Heating",
              "Columbia MD Heating Repair", "Book A Heating Repair", "Heating Repair Near You",
              "Local Heating Technicians", "Heating System Repair", "Schedule A Repair Visit",
              "Trained HVAC Technicians", "Maryland Heating Repair", "Request Heating Repair",
              "Home Heating Repair", "Talk To A Technician", "Heating Service Central MD"],
             ["Heating repair for homes across Severn, Severna Park and Columbia, Maryland.",
              "Our technicians diagnose the fault and explain your options clearly.",
              "Book a heating repair visit with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional heating services."], L_SERV),
         rsa(["Heating Not Working?", "Heat Running But Cold?", "Heating System Faulty?",
              "Get Your Heating Checked", "Heating Repair Near You", "Central Maryland Heating",
              "Heating Repair Specialists", "Severn Heating Repair", "Book A Heating Visit",
              "Talk To A Technician", "We Repair Home Heating", "Clear Repair Options",
              "Request Heating Service", "Columbia Heating Service", "Anne Arundel Heating"],
             ["Heating trouble in Severn, Severna Park or Columbia? Our technicians help.",
              "We diagnose the problem and walk you through the repair options.",
              "Heating repair for Maryland homes and commercial properties.",
              "Schedule a heating repair appointment with Ambient Cooling and Heating."], L_PROB)],
   services=["Heating Repair"])

ag("SKAG | Emergency Heating Repair", "C1", None, 42.00,
   ["emergency heating repair", "emergency heater repair"],
   ["emergency heating repair", "emergency heat repair", "emergency furnace repair"],
   "Account search terms: $881.40 / 52 clicks / 1 conversion, CPC $16.95.",
   verdict="HOLD - SERVICE OFFERING DOES NOT SUPPORT THE INTENT",
   gate="Ambient publishes Mon-Fri 08:00-16:00 and is CLOSED Saturday and Sunday "
        "(contact page text and schema.org OpeningHoursSpecification, read 2026-09-22). "
        "The owner confirms calls are answered during business hours only. An emergency "
        "searcher expects availability this business does not offer, so the ad group is "
        "built and held. RSA payload is prepared but deliberately makes NO availability, "
        "dispatch, arrival-time or same-day promise; it must not be uploaded until both a "
        "destination and a verified emergency offering exist.",
   rsas=[rsa(["Heating Emergency?", "Heating Failed Suddenly?", "Urgent Heating Problem?",
              "Book A Heating Visit", "Heating Repair Near You", "Severn Heating Repair",
              "Heating Repair Specialists", "Central Maryland Heating", "Talk To A Technician",
              "Request A Heating Visit", "We Repair Home Heating", "Columbia Heating Repair",
              "Severna Park Heating", "Heating System Repair", "Maryland Heating Repair"],
             ["Heating failure in Severn, Severna Park or Columbia? Request a visit.",
              "Tell us what the system is doing and we will book a technician.",
              "Heating repair for Maryland homes and commercial properties.",
              "Request a heating repair appointment with Ambient Cooling and Heating."],
             "RSA A - prepared, awaiting URL and a verified emergency offering"),
         rsa(["Heating Stopped Working?", "No Warmth From Your System?", "Heating Fault?",
              "Get Your Heating Checked", "Book A Heating Repair", "Heating Help Near You",
              "Severn Heating Technicians", "Central Maryland Heating", "Talk To A Technician",
              "Clear Repair Options", "Request Heating Service", "Home Heating Repair",
              "Columbia Heating Service", "Maryland Heating Help", "Heating Repair Visit"],
             ["Heating trouble across Severn, Severna Park and Columbia, Maryland.",
              "We diagnose the fault and walk you through the repair options.",
              "Request a heating repair visit with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional heating repair."],
             "RSA B - prepared, awaiting URL and a verified emergency offering")],
   services=["Emergency Heating Repair"])

ag("SKAG | No Heat Repair", "C1", None, 42.00,
   ["no heat repair", "no heat service"], ["no heat repair", "house has no heat"],
   "Account search terms: 28 distinct terms, 0 clicks, 0 conversions. EXACT "
   "[no heat in house] dropped - rejected GENERAL_DATING_AND_COMPANIONSHIP, a false "
   "positive; [house has no heat] carries the same intent and passes.",
   verdict="HOLD - SERVICE OFFERING DOES NOT SUPPORT THE INTENT",
   gate="Same gate as Emergency Heating Repair. A 'no heat' searcher in winter expects a "
        "same-day visit; Ambient answers Mon-Fri 08:00-16:00 only. Held.",
   rsas=[rsa(["No Heat At Home?", "House Gone Cold?", "Heating Not Producing Heat?",
              "Book A Heating Visit", "Heating Repair Near You", "Severn Heating Repair",
              "Heating Repair Specialists", "Central Maryland Heating", "Talk To A Technician",
              "Request A Heating Visit", "We Repair Home Heating", "Columbia Heating Repair",
              "Severna Park Heating", "Heating System Repair", "Maryland Heating Repair"],
             ["No heat in your Severn, Severna Park or Columbia home? Request a visit.",
              "Tell us what the system is doing and we will book a technician.",
              "Heating repair for Maryland homes and commercial properties.",
              "Request a heating repair appointment with Ambient Cooling and Heating."],
             "RSA A - prepared, awaiting URL"),
         rsa(["System Blowing Cold?", "No Warmth In The House?", "Heating Producing No Heat?",
              "Get Your Heating Checked", "Book A Heating Repair", "Heating Help Near You",
              "Severn Heating Technicians", "Central Maryland Heating", "Talk To A Technician",
              "Clear Repair Options", "Request Heating Service", "Home Heating Repair",
              "Columbia Heating Service", "Maryland Heating Help", "Heating Repair Visit"],
             ["A heating system producing no heat usually has a diagnosable fault.",
              "We diagnose the fault and walk you through the repair options.",
              "Request a heating repair visit with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional heating repair."],
             "RSA B - prepared, awaiting URL")],
   services=["No Heat Repair"])

ag("SKAG | Gas Furnace Repair", "C1", U_FURNACE, 42.00,
   ["gas furnace repair"], ["gas furnace repair"],
   "Account search terms: $90.18 / 8 clicks / 0 conversions, CPC $11.27. Keywords moved "
   "here from ad group 199797580706 rather than duplicated.",
   page_evidence="Furnace repair page. Fuel type is a qualifier on the same service; the "
                 "page never says 'gas', which is noted as a content improvement.",
   rsas=[rsa(["Gas Furnace Repair", "Gas Furnace Repair Severn", "Severna Park Gas Furnace",
              "Columbia Gas Furnace", "Book A Furnace Repair", "Furnace Repair Near You",
              "Gas Furnace Technicians", "Central Maryland Furnace", "Schedule A Repair Visit",
              "Trained HVAC Technicians", "Maryland Furnace Repair", "Request Furnace Repair",
              "Home Furnace Repair", "Talk To A Technician", "Furnace Repair Central MD"],
             ["Gas furnace repair for homes in Severn, Severna Park and Columbia, Maryland.",
              "Our technicians diagnose the fault and explain your options clearly.",
              "Book a furnace repair visit with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional furnace repair."], L_SERV),
         rsa(["Gas Furnace Not Working?", "Furnace Blowing Cold Air?", "Furnace Cutting Out?",
              "Get Your Furnace Checked", "Gas Furnace Repair Near You", "Severn Furnace Repair",
              "Furnace Repair Specialists", "Central Maryland Furnace", "Book A Furnace Visit",
              "Talk To A Technician", "We Repair Gas Furnaces", "Clear Repair Options",
              "Request Furnace Service", "Columbia Furnace Repair", "Anne Arundel Furnace"],
             ["Gas furnace trouble in Severn, Severna Park or Columbia? Our technicians help.",
              "We diagnose the problem and walk you through the repair options.",
              "Furnace repair for Maryland homes and commercial properties.",
              "Schedule a furnace repair appointment with Ambient Cooling and Heating."], L_PROB)],
   services=["Gas Furnace Repair"])

ag("SKAG | Electric Furnace Repair", "C1", U_FURNACE, 42.00,
   ["electric furnace repair"], ["electric furnace repair"],
   "Account search terms: $47.64 / 3 clicks / 0 conversions, CPC $15.88.",
   page_evidence="Furnace repair page, as above. The page never says 'electric'.",
   gate="client.yaml still lists 'Electric furnace repair' under "
        "services_capability_not_verified. The owner's service list places it in scope and "
        "instructs no reconfirmation, so it is built and enabled; the capability flag is "
        "left in client.yaml as an open item rather than silently cleared.",
   rsas=[rsa(["Electric Furnace Repair", "Electric Furnace Severn", "Severna Park Furnace",
              "Columbia Furnace Repair", "Book A Furnace Repair", "Furnace Repair Near You",
              "Electric Furnace Service", "Central Maryland Furnace", "Schedule A Repair Visit",
              "Trained HVAC Technicians", "Maryland Furnace Repair", "Request Furnace Repair",
              "Home Furnace Repair", "Talk To A Technician", "Furnace Repair Central MD"],
             ["Electric furnace repair for homes in Severn, Severna Park and Columbia, MD.",
              "Our technicians diagnose the fault and explain your options clearly.",
              "Book a furnace repair visit with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional furnace repair."], L_SERV),
         rsa(["Electric Furnace Faulty?", "Furnace Blowing Cold Air?", "Furnace Cutting Out?",
              "Get Your Furnace Checked", "Furnace Repair Near You", "Severn Furnace Repair",
              "Furnace Repair Specialists", "Central Maryland Furnace", "Book A Furnace Visit",
              "Talk To A Technician", "We Repair Electric Furnaces", "Clear Repair Options",
              "Request Furnace Service", "Columbia Furnace Repair", "Anne Arundel Furnace"],
             ["Electric furnace trouble in Severn, Severna Park or Columbia? We can help.",
              "We diagnose the problem and walk you through the repair options.",
              "Furnace repair for Maryland homes and commercial properties.",
              "Schedule a furnace repair appointment with Ambient Cooling and Heating."], L_PROB)],
   services=["Electric Furnace Repair"])

# ================== C2 - HEAT PUMP & DUCTLESS HEATING ========================
_HP = [
    ("Heat Pump Repair", ["heat pump repair"],
     ["heat pump repair", "heat pump not heating", "heat pump service"],
     "Account search terms: $1,088.79 / 43 clicks / 0 conversions, CPC $25.32. Campaign "
     "view: heat_pump|repair CPA $365.93 on 3 conversions.",
     [["Heat Pump Repair", "Heat Pump Repair Severn", "Severna Park Heat Pump",
       "Columbia Heat Pump Repair", "Book A Heat Pump Visit", "Heat Pump Repair Near You",
       "Heat Pump Technicians", "Central Maryland Heat Pump", "Schedule A Repair Visit",
       "Trained HVAC Technicians", "Maryland Heat Pump Repair", "Request Heat Pump Repair",
       "Home Heat Pump Repair", "Talk To A Technician", "Heat Pump Service Central MD"],
      ["Heat pump repair for homes in Severn, Severna Park and Columbia, Maryland.",
       "Our technicians diagnose the fault and explain your options clearly.",
       "Book a heat pump repair visit with Ambient Cooling and Heating.",
       "Serving Central Maryland with professional heat pump repair."],
      ["Heat Pump Not Heating?", "Heat Pump Running Cold?", "Heat Pump Icing Over?",
       "Get Your Heat Pump Checked", "Heat Pump Repair Near You", "Severn Heat Pump Repair",
       "Heat Pump Specialists", "Central Maryland Heat Pump", "Book A Heat Pump Visit",
       "Talk To A Technician", "We Repair Home Heat Pumps", "Clear Repair Options",
       "Request Heat Pump Service", "Columbia Heat Pump Help", "Anne Arundel Heat Pump"],
      ["Heat pump trouble in Severn, Severna Park or Columbia? Our technicians help.",
       "We diagnose the problem and walk you through the repair options.",
       "Heat pump repair for Maryland homes and commercial properties.",
       "Schedule a heat pump repair appointment with Ambient Cooling and Heating."]]),
    ("Heat Pump Replacement", ["heat pump replacement"],
     ["heat pump replacement", "replace heat pump"],
     "Account search terms: 30 terms, 2 clicks, 1 conversion on $6.27.",
     [["Heat Pump Replacement", "Replace Your Heat Pump", "Heat Pump Replace Severn",
       "Severna Park Heat Pump", "Columbia Heat Pump", "New Heat Pump Assessment",
       "Heat Pump Replacement Quote", "Central Maryland Heat Pump", "Book An Assessment",
       "Trained HVAC Technicians", "Maryland Heat Pump Service", "Request Replacement Info",
       "Plan Your Replacement", "Talk To A Technician", "Heat Pump Central MD"],
      ["Heat pump replacement for homes in Severn, Severna Park and Columbia, Maryland.",
       "We assess your current heat pump and explain the replacement options.",
       "Book a heat pump assessment with Ambient Cooling and Heating.",
       "Serving Central Maryland with professional heat pump replacement."],
      ["Heat Pump Near The End?", "Old Heat Pump Struggling?", "Repair Or Replace?",
       "Upgrade Your Heat Pump", "Heat Pump Replace Quote", "Severn Heat Pump Help",
       "Heat Pump Specialists", "Central Maryland Heat Pump", "Book An Assessment",
       "Talk To A Technician", "Plan The Replacement", "Clear Replacement Options",
       "Request An Assessment", "Columbia Heat Pump Help", "Warm Home This Winter"],
      ["An ageing heat pump gives little warning. Plan the replacement early.",
       "We assess your current heat pump and set out the replacement options.",
       "Heat pump replacement across Severn, Severna Park and Columbia homes.",
       "Schedule a heat pump assessment with Ambient Cooling and Heating."]]),
    ("Heat Pump Installation", ["heat pump installation"],
     ["heat pump installation", "heat pump installers near me"],
     "Campaign view: heat_pump|installation $6,128.74 / 397 clicks / 16 conversions, "
     "CPC $15.44, CPA $383.05 - the strongest heat-pump intent in the account.",
     [["Heat Pump Installation", "Heat Pump Install Severn", "Severna Park Heat Pump",
       "Columbia MD Heat Pump", "Install A New Heat Pump", "Heat Pump Installers",
       "Central Maryland Heat Pump", "Book A Heat Pump Quote", "Heat Pump Specialists",
       "Trained HVAC Technicians", "Maryland Heat Pump Fit", "Request Heat Pump Info",
       "Schedule An Assessment", "Talk To An Installer", "Heat Pump Install Central MD"],
      ["Heat pump installation for homes across Severn, Severna Park and Columbia, MD.",
       "We size the system to your home and explain the options clearly.",
       "Book a heat pump assessment with Ambient Cooling and Heating.",
       "Experienced heat pump installation across Central Maryland."],
      ["Need A New Heat Pump?", "Considering A Heat Pump?", "Upgrade Your Heating",
       "Heat Pump Install Quote", "Warm Home This Winter", "Heat Pump Installation",
       "Maryland Heat Pump Fitters", "Book A Heat Pump Visit", "Talk To An Installer",
       "Efficient Home Heating", "Severn Heat Pump Install", "Columbia Heat Pump Install",
       "Clear Installation Options", "Sized For Your Home", "Request An Assessment"],
      ["Planning a new heat pump in Central Maryland? Speak to our installers.",
       "We assess your home, size the system and explain each option.",
       "Heat pump installation for Severn, Severna Park and Columbia homes.",
       "Book a heat pump installation assessment with Ambient."]]),
    ("Heat Pump Maintenance", ["heat pump maintenance"],
     ["heat pump maintenance", "heat pump tune up"],
     "Campaign view: heat_pump|maintenance CPA $185.85 on 7 conversions - the BEST "
     "measured CPA of any heating intent in this account.",
     [["Heat Pump Maintenance", "Heat Pump Care Severn", "Severna Park Heat Pump Care",
       "Columbia Heat Pump Service", "Book Heat Pump Service", "Heat Pump Care Near You",
       "Heat Pump Service Visit", "Central Maryland Heat Pump", "Schedule A Service Visit",
       "Trained HVAC Technicians", "Maryland Heat Pump Care", "Request Heat Pump Service",
       "Home Heat Pump Care", "Talk To A Technician", "Heat Pump Care Central MD"],
      ["Heat pump maintenance for homes in Severn, Severna Park and Columbia, Maryland.",
       "Our technicians check the system and explain what it needs.",
       "Book a heat pump maintenance visit with Ambient Cooling and Heating.",
       "Serving Central Maryland with professional heat pump maintenance."],
      ["Heat Pump Due A Service?", "Keep Your Heat Pump Running", "Before The Cold Arrives",
       "Book Heat Pump Service", "Heat Pump Care Near You", "Severn Heat Pump Service",
       "Heat Pump Care Specialists", "Central Maryland Heat Pump", "Book A Service Visit",
       "Talk To A Technician", "Planned Heat Pump Care", "Clear Service Options",
       "Request A Service Visit", "Columbia Heat Pump Care", "Warm Home This Winter"],
      ["A heat pump checked before winter is less likely to fail during it.",
       "We inspect the system and set out anything that needs attention.",
       "Heat pump maintenance across Severn, Severna Park and Columbia homes.",
       "Schedule a heat pump maintenance visit with Ambient Cooling and Heating."]]),
]
for _n, _p, _e, _ev, _r in _HP:
    ag(f"SKAG | {_n}", "C2", U_HEATPUMP, 35.00, _p, _e, _ev,
       verdict="HOLD - DESTINATION BLOCKED BY GOOGLE",
       gate="The heat-pumps URL fails Google's destination check: DESTINATION_NOT_WORKING, "
            "0/3 trials on 2026-09-22, a fourth consecutive failing day, while EIGHT other "
            "Ambient destinations passed 3/3 in the same run with the IDENTICAL ad body. "
            "The page itself is healthy (HTTP 200 desktop and mobile, correct H1, working "
            "form). The API rejects any ad carrying this URL, so the RSA payloads below are "
            "PREPARED, NOT CREATED. No URL variant is substituted. Remedy is a policy "
            "re-review requested in the Google Ads interface.",
       rsas=[rsa(_r[0], _r[1], "RSA A - prepared, blocked destination"),
             rsa(_r[2], _r[3], "RSA B - prepared, blocked destination")],
       services=[_n],
       page_evidence="H1 'Heat Pumps in Severn...', 22 heat-pump sentences, install 8, "
                     "repair 10, maintenance 4. Content is fine; Google's verdict is not.")

ag("SKAG | Ductless Heating Repair", "C2", U_MINISPLIT, 35.00,
   ["ductless heating repair", "mini split repair"],
   ["ductless repair", "mini split repair", "ductless heating repair"],
   "Account search terms: $838.66 / 36 clicks / 3 conversions, CPC $23.30, CPA $279.55 - "
   "one of the better heating CPAs in the account.",
   page_evidence="Mini splits page, 4 real ductless-repair sentences, H2 'Comprehensive "
                 "Installation and Maintenance Services'.",
   rsas=[rsa(["Ductless Heating Repair", "Mini Split Repair Severn", "Severna Park Mini Split",
              "Columbia Ductless Repair", "Book A Ductless Repair", "Ductless Repair Near You",
              "Mini Split Technicians", "Central Maryland Ductless", "Schedule A Repair Visit",
              "Trained HVAC Technicians", "Maryland Mini Split Help", "Request Ductless Repair",
              "Home Ductless Repair", "Talk To A Technician", "Ductless Repair Central MD"],
             ["Ductless and mini split repair across Severn, Severna Park and Columbia, MD.",
              "Our technicians diagnose the fault and explain your options clearly.",
              "Book a ductless repair visit with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional mini split service."], L_SERV),
         rsa(["Mini Split Not Heating?", "Ductless Unit Faulty?", "Mini Split Leaking?",
              "Get Your Ductless Checked", "Ductless Repair Near You", "Severn Ductless Repair",
              "Mini Split Specialists", "Central Maryland Ductless", "Book A Ductless Visit",
              "Talk To A Technician", "We Repair Mini Splits", "Clear Repair Options",
              "Request Ductless Service", "Columbia Mini Split Help", "Anne Arundel Ductless"],
             ["Mini split trouble in Severn, Severna Park or Columbia? Our technicians help.",
              "We diagnose the problem and walk you through the repair options.",
              "Ductless heating repair for Maryland homes and businesses.",
              "Schedule a ductless repair appointment with Ambient Cooling and Heating."], L_PROB)],
   services=["Ductless Heating Repair"])

# ============ C3 - HEATING & FURNACE INSTALLATION AND REPLACEMENT ============
ag("SKAG | Furnace Replacement", "C3", U_FURNACE, 46.00,
   ["furnace replacement"], ["furnace replacement", "replace furnace", "new furnace cost"],
   "Account search terms: $321.79 / 7 clicks / 0 conversions, CPC $45.97.",
   page_evidence="Furnace repair page carries an explicit replacement H2 'Trusted Furnace "
                 "Repair and Replacement' plus 3 real replacement sentences.",
   rsas=[rsa(["Furnace Replacement", "Replace Your Furnace", "Furnace Replacement Severn",
              "Severna Park Furnace", "Columbia MD Furnace", "New Furnace Assessment",
              "Furnace Replacement Quote", "Central Maryland Furnace", "Book An Assessment",
              "Trained HVAC Technicians", "Maryland Furnace Service", "Request Replacement Info",
              "Plan Your Replacement", "Talk To A Technician", "Furnace Replace Central MD"],
             ["Furnace replacement for homes in Severn, Severna Park and Columbia, Maryland.",
              "We assess your current furnace and explain the replacement options.",
              "Book a furnace assessment with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional furnace replacement."], L_SERV),
         rsa(["Furnace Near The End?", "Old Furnace Failing?", "Repair Or Replace?",
              "Upgrade Your Furnace", "Furnace Replacement Quote", "Severn Furnace Help",
              "Furnace Specialists", "Central Maryland Furnace", "Book An Assessment",
              "Talk To A Technician", "Plan The Replacement", "Clear Replacement Options",
              "Request An Assessment", "Columbia Furnace Help", "Warm Home This Winter"],
             ["An ageing furnace gives little warning. Plan the replacement early.",
              "We assess your current furnace and set out the replacement options.",
              "Furnace replacement across Severn, Severna Park and Columbia homes.",
              "Schedule a furnace assessment with Ambient Cooling and Heating."], L_PROB)],
   services=["Furnace Replacement"])

ag("SKAG | Furnace Installation", "C3", U_OFFER_INSTALL, 46.00,
   ["furnace installation"], ["furnace installation", "furnace installers near me"],
   "Account search terms: $317.74 / 7 clicks / 0 conversions, CPC $45.39.",
   page_evidence="Offer HVAC Installation page. Its own copy is explicitly about installing "
                 "a heating system: 'professional guidance selecting and installing a "
                 "heating and cooling system', 'complete the new heating and cooling system "
                 "installation'. H2s are all installation. The furnace-repair page has ZERO "
                 "real installation sentences, so this is the correct home.",
   rsas=[rsa(["Furnace Installation", "Furnace Install Severn", "Severna Park Furnace",
              "Columbia MD Furnace", "Install A New Furnace", "Furnace Installers",
              "Central Maryland Furnace", "Book An Install Quote", "Heating Installers",
              "Trained HVAC Technicians", "Maryland Furnace Fitters", "Request Install Info",
              "Schedule An Assessment", "Talk To An Installer", "Furnace Install Central MD"],
             ["Furnace installation for homes across Severn, Severna Park and Columbia, MD.",
              "We size the system to your home and explain the options clearly.",
              "Book an installation assessment with Ambient Cooling and Heating.",
              "Experienced heating system installation across Central Maryland."], L_SERV),
         rsa(["Need A New Furnace?", "Planning A Furnace Install?", "Upgrade Your Heating",
              "Furnace Install Quote", "Warm Home This Winter", "Furnace Installation",
              "Maryland Heating Fitters", "Book An Install Visit", "Talk To An Installer",
              "Heating Done Properly", "Severn Furnace Install", "Columbia Furnace Install",
              "Clear Installation Options", "Sized For Your Home", "Request An Assessment"],
             ["Planning a new furnace in Central Maryland? Speak to our installers.",
              "We assess your home, size the system and explain each option.",
              "Heating system installation for Severn, Severna Park and Columbia homes.",
              "Book an installation assessment with Ambient Cooling and Heating."], L_PROB)],
   services=["Furnace Installation"])

ag("SKAG | Heating Installation", "C3", U_OFFER_INSTALL, 46.00,
   ["heating installation", "heating system installation"],
   ["heating installation", "heating system installation"],
   "Account search terms: $857.15 / 51 clicks / 2 conversions, CPC $16.81, CPA $428.57. "
   "Covers BOTH requested labels in one ad group - they are close variants Google groups "
   "into one demand bucket.",
   page_evidence="Offer HVAC Installation page, 5 real heating-installation sentences.",
   rsas=[rsa(["Heating Installation", "Heating Install Severn", "Severna Park Heating",
              "Columbia MD Heating", "New Heating System", "Heating Installers",
              "Central Maryland Heating", "Book An Install Quote", "Heating System Install",
              "Trained HVAC Technicians", "Maryland Heating Fitters", "Request Install Info",
              "Schedule An Assessment", "Talk To An Installer", "Heating Install Central MD"],
             ["Heating system installation across Severn, Severna Park and Columbia, MD.",
              "We size the system to your home and explain the options clearly.",
              "Book an installation assessment with Ambient Cooling and Heating.",
              "Experienced heating system installation across Central Maryland."], L_SERV),
         rsa(["Need A New Heating System?", "Planning A Heating Install?", "Upgrade Your Heating",
              "Heating Install Quote", "Warm Home This Winter", "Heating System Installation",
              "Maryland Heating Fitters", "Book An Install Visit", "Talk To An Installer",
              "Heating Done Properly", "Severn Heating Install", "Columbia Heating Install",
              "Clear Installation Options", "Sized For Your Home", "Request An Assessment"],
             ["Planning a new heating system in Central Maryland? Speak to our installers.",
              "We assess your property, size the system and explain each option.",
              "Heating installation for Severn, Severna Park and Columbia homes.",
              "Book an installation assessment with Ambient Cooling and Heating."], L_PROB)],
   services=["Heating Installation", "Heating System Installation"])

ag("SKAG | Heating Replacement", "C3", U_OFFER_REPLACE, 46.00,
   ["heating replacement", "heating system replacement"],
   ["heating replacement", "heating system replacement", "replace heating system"],
   "Account search terms: $215.27 / 15 clicks / 0 conversions, CPC $14.35. Covers BOTH "
   "requested labels in one ad group.",
   page_evidence="Offer HVAC Replacement page. Opens 'If your current heating and cooling "
                 "system is aging, unreliable, or no longer practical...'; H2s are all "
                 "system replacement. 4 real heating sentences.",
   rsas=[rsa(["Heating Replacement", "Replace Your Heating", "Heating Replace Severn",
              "Severna Park Heating", "Columbia MD Heating", "New Heating System",
              "Heating System Replacement", "Central Maryland Heating", "Book An Assessment",
              "Trained HVAC Technicians", "Maryland Heating Service", "Request Replacement Info",
              "Plan Your Replacement", "Talk To A Technician", "Heating Replace Central MD"],
             ["Heating system replacement across Severn, Severna Park and Columbia, MD.",
              "We assess your current system and explain the replacement options.",
              "Book a replacement assessment with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional system replacement."], L_SERV),
         rsa(["Heating System Aging?", "Old System Unreliable?", "Repair Or Replace?",
              "Upgrade Your Heating", "Heating Replace Quote", "Severn Heating Help",
              "Heating Specialists", "Central Maryland Heating", "Book An Assessment",
              "Talk To A Technician", "Plan The Replacement", "Clear Replacement Options",
              "Request An Assessment", "Columbia Heating Help", "Warm Home This Winter"],
             ["An aging or unreliable heating system is worth reviewing before winter.",
              "We assess your current system and set out the replacement options.",
              "Heating system replacement across Severn, Severna Park and Columbia.",
              "Schedule a replacement assessment with Ambient Cooling and Heating."], L_PROB)],
   services=["Heating Replacement", "Heating System Replacement"])

ag("SKAG | Ductless Heating Installation", "C3", U_MINISPLIT, 46.00, [], [],
   "RENAME of existing ad group 199797580746 'SKAG | Mini Split Installation' (2026-09-17, "
   "8 keywords, 2 APPROVED RSAs). Renamed rather than duplicated. Google Ads cannot move an "
   "ad group between campaigns, so it stays in campaign 24257819466 - which is the "
   "installation campaign, so this is the right home anyway.",
   existing="199797580746", rename_from="SKAG | Mini Split Installation",
   page_evidence="Mini splits page, 5 real ductless-installation sentences.",
   services=["Ductless Heating Installation"])

# ========================== C4 - BOILER SERVICES =============================
ag("SKAG | Gas Boiler Repair", "C4", U_GASBOILER, 60.00, [], [],
   "EXISTING 202339087594 on the live boiler campaign. 2 keywords APPROVED/ELIGIBLE, "
   "2 ENABLED APPROVED RSAs. Two older PAUSED RSAs are disapproved CONSUMER_FINANCE and are "
   "left untouched.",
   existing="202339087594", services=["Gas Boiler Repair"],
   page_evidence="Offer gas-boiler-repair page: 37 repair sentences, 37 gas, 50 boiler.")

ag("SKAG | Boiler Repair", "C4", U_BOILER, 60.00,
   ["boiler repair"],
   ["boiler repair", "residential boiler repair", "commercial boiler repair"],
   "Account search terms: $5,219.83 / 88 clicks / 12.33 conversions, CPC $59.32, "
   "CPA $423.34 - the second largest converting heating theme.",
   page_evidence="Boiler repair page: 5 real boiler-repair-service sentences, H2 'Expert "
                 "Boiler Repair to Get You Back in Business', which supports the commercial "
                 "EXACT variant.",
   rsas=[rsa(["Boiler Repair in Severn", "Boiler Repair Central MD", "Severna Park Boiler",
              "Columbia MD Boiler Repair", "Residential Boiler Repair", "Commercial Boiler Repair",
              "Boiler Repair Technicians", "Book A Boiler Repair", "Maryland Boiler Repair",
              "Boiler Diagnosis Explained", "Schedule Boiler Service", "Homes And Businesses",
              "Trained HVAC Technicians", "Boiler Service Central MD", "Request Boiler Repair"],
             ["Boiler repair for homes and businesses in Severn, Severna Park and Columbia.",
              "Our technicians diagnose the fault and explain your options clearly.",
              "Book a boiler repair visit with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional boiler repair."], L_SERV),
         rsa(["Boiler Stopped Working?", "No Heat From Your Boiler?", "Boiler Leaking?",
              "Get Your Boiler Looked At", "Boiler Repair Near You", "Central Maryland Boilers",
              "Boiler Repair Specialists", "Severn Boiler Repair", "Book A Boiler Inspection",
              "Talk To A Technician", "We Repair Home Boilers", "We Repair Business Boilers",
              "Clear Repair Options", "Request Boiler Service", "Columbia Boiler Service"],
             ["Boiler trouble in Severn, Severna Park or Columbia? Our technicians help.",
              "We diagnose the problem and walk you through the repair options.",
              "Boiler repair for Maryland homes and commercial properties.",
              "Schedule a boiler repair appointment with Ambient Cooling and Heating."], L_PROB)],
   services=["Boiler Repair"])

_BOILER_HOLD = [
    ("Boiler Replacement", ["boiler replacement"],
     ["boiler replacement", "replace boiler", "new boiler cost"],
     "Account search terms: $221.75 / 7 clicks / 0 conversions, CPC $31.68.",
     [["Boiler Replacement", "Replace Your Boiler", "Boiler Replace Severn",
       "Severna Park Boiler", "Columbia MD Boiler", "New Boiler Assessment",
       "Boiler Replacement Quote", "Central Maryland Boiler", "Book An Assessment",
       "Trained HVAC Technicians", "Maryland Boiler Service", "Request Replacement Info",
       "Plan Your Replacement", "Talk To A Technician", "Boiler Replace Central MD"],
      ["Boiler replacement for homes and businesses across Central Maryland.",
       "We assess your current boiler and explain the replacement options.",
       "Book a boiler assessment with Ambient Cooling and Heating.",
       "Serving Severn, Severna Park and Columbia with boiler replacement."],
      ["Boiler Near The End?", "Old Boiler Struggling?", "Repair Or Replace?",
       "Upgrade Your Boiler", "Boiler Replacement Quote", "Severn Boiler Help",
       "Boiler Specialists", "Central Maryland Boiler", "Book An Assessment",
       "Talk To A Technician", "Plan The Replacement", "Clear Replacement Options",
       "Request An Assessment", "Columbia Boiler Help", "Warm Home This Winter"],
      ["An ageing boiler gives little warning. Plan the replacement early.",
       "We assess your current boiler and set out the replacement options.",
       "Boiler replacement across Severn, Severna Park and Columbia.",
       "Schedule a boiler assessment with Ambient Cooling and Heating."]]),
    ("Boiler Installation", ["boiler installation"],
     ["boiler installation", "boiler installers near me"],
     "Account search terms: $95.51 / 2 clicks / 0 conversions, CPC $47.76. Campaign view: "
     "boiler|installation CPA $315.24 on 6 conversions.",
     [["Boiler Installation", "Boiler Install Severn", "Severna Park Boiler",
       "Columbia MD Boiler", "Install A New Boiler", "Boiler Installers",
       "Central Maryland Boiler", "Book An Install Quote", "Boiler Specialists",
       "Trained HVAC Technicians", "Maryland Boiler Fitters", "Request Install Info",
       "Schedule An Assessment", "Talk To An Installer", "Boiler Install Central MD"],
      ["Boiler installation for homes and businesses across Central Maryland.",
       "We size the boiler to your property and explain the options clearly.",
       "Book a boiler installation assessment with Ambient Cooling and Heating.",
       "Serving Severn, Severna Park and Columbia with boiler installation."],
      ["Need A New Boiler?", "Planning A Boiler Install?", "Upgrade Your Heating",
       "Boiler Install Quote", "Warm Home This Winter", "Boiler Installation",
       "Maryland Boiler Fitters", "Book An Install Visit", "Talk To An Installer",
       "Heating Done Properly", "Severn Boiler Install", "Columbia Boiler Install",
       "Clear Installation Options", "Sized For Your Property", "Request An Assessment"],
      ["Planning a new boiler in Central Maryland? Speak to our installers.",
       "We assess the property, size the boiler and explain each option.",
       "Boiler installation for Severn, Severna Park and Columbia.",
       "Book a boiler installation assessment with Ambient."]]),
    ("Boiler Maintenance", ["boiler maintenance", "boiler service"],
     ["boiler maintenance", "boiler service"],
     "Account search terms: $2,102.23 / 28 clicks / 4 conversions, CPC $75.08, CPA $525.56 "
     "- the most expensive heating clicks in the account.",
     [["Boiler Maintenance", "Boiler Care Severn MD", "Severna Park Boiler Care",
       "Columbia Boiler Service", "Book Boiler Maintenance", "Boiler Care Near You",
       "Boiler Service Visit", "Central Maryland Boiler", "Schedule A Service Visit",
       "Trained HVAC Technicians", "Maryland Boiler Care", "Request Boiler Service",
       "Home Boiler Maintenance", "Talk To A Technician", "Boiler Care Central MD"],
      ["Boiler maintenance for homes and businesses across Central Maryland.",
       "Our technicians check the boiler and explain what it needs.",
       "Book a boiler maintenance visit with Ambient Cooling and Heating.",
       "Serving Severn, Severna Park and Columbia with boiler maintenance."],
      ["Boiler Due A Service?", "Keep Your Boiler Running", "Before The Cold Arrives",
       "Book Boiler Maintenance", "Boiler Care Near You", "Severn Boiler Service",
       "Boiler Care Specialists", "Central Maryland Boiler", "Book A Service Visit",
       "Talk To A Technician", "Planned Boiler Care", "Clear Service Options",
       "Request A Service Visit", "Columbia Boiler Care", "Warm Home This Winter"],
      ["A boiler checked before winter is less likely to fail during it.",
       "We inspect the boiler and set out anything that needs attention.",
       "Boiler maintenance across Severn, Severna Park and Columbia.",
       "Schedule a boiler maintenance visit with Ambient Cooling and Heating."]]),
]
for _n, _p, _e, _ev, _r in _BOILER_HOLD:
    ag(f"SKAG | {_n}", "C4", None, 60.00, _p, _e, _ev,
       verdict="HOLD - NO ADEQUATE PAGE",
       gate="The boiler-repair page has ZERO real installation sentences and ZERO real "
            "replacement sentences once nav and footer are excluded; its only maintenance "
            "hits are the phrase 'boiler repair services'. It is a repair page. RSA payload "
            "PREPARED, awaiting the dedicated boiler installation / replacement / "
            "maintenance page.",
       rsas=[rsa(_r[0], _r[1], "RSA A - prepared, awaiting URL"),
             rsa(_r[2], _r[3], "RSA B - prepared, awaiting URL")],
       services=[_n])

# ================= C5 - HEATING MAINTENANCE AND INSPECTION ===================
ag("SKAG | Furnace Maintenance", "C5", U_FURNACE, 32.00,
   ["furnace maintenance"], ["furnace maintenance", "furnace cleaning"],
   "Account search terms: $2,554.67 / 48 clicks / 7 conversions, CPC $53.22, CPA $364.95. "
   "Campaign view: furnace|maintenance CPA $230.31 - among the best in the account.",
   page_evidence="Furnace repair page, H2 'Timely Furnace Repair and Maintenance Services' "
                 "plus 3 real maintenance sentences.",
   rsas=[rsa(["Furnace Maintenance", "Furnace Care Severn MD", "Severna Park Furnace Care",
              "Columbia Furnace Service", "Book Furnace Maintenance", "Furnace Care Near You",
              "Furnace Service Visit", "Central Maryland Furnace", "Schedule A Service Visit",
              "Trained HVAC Technicians", "Maryland Furnace Care", "Request Furnace Service",
              "Home Furnace Maintenance", "Talk To A Technician", "Furnace Care Central MD"],
             ["Furnace maintenance for homes in Severn, Severna Park and Columbia, Maryland.",
              "Our technicians check the system and explain what it needs.",
              "Book a furnace maintenance visit with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional furnace maintenance."], L_SERV),
         rsa(["Furnace Due A Service?", "Keep Your Furnace Running", "Before The Cold Arrives",
              "Book Furnace Maintenance", "Furnace Care Near You", "Severn Furnace Service",
              "Furnace Care Specialists", "Central Maryland Furnace", "Book A Service Visit",
              "Talk To A Technician", "Planned Furnace Care", "Clear Service Options",
              "Request A Service Visit", "Columbia Furnace Care", "Warm Home This Winter"],
             ["A furnace checked before winter is less likely to fail during it.",
              "We inspect the system and set out anything that needs attention.",
              "Furnace maintenance across Severn, Severna Park and Columbia homes.",
              "Schedule a furnace maintenance visit with Ambient Cooling and Heating."], L_SEAS)],
   services=["Furnace Maintenance"])

ag("SKAG | Heating Maintenance", "C5", U_HUB, 32.00,
   ["heating maintenance"], ["heating maintenance", "heating system maintenance"],
   "Account search terms: $1,816.70 / 273 clicks / 2 conversions, CPC $6.65 - the cheapest "
   "heating clicks in the account.",
   page_evidence="Heating hub, H2 'Comprehensive Heating Services and Maintenance Plans' "
                 "plus 4 real maintenance sentences.",
   rsas=[rsa(["Heating Maintenance", "Heating Care Severn MD", "Severna Park Heating Care",
              "Columbia Heating Service", "Book Heating Maintenance", "Heating Care Near You",
              "Heating Service Visit", "Central Maryland Heating", "Schedule A Service Visit",
              "Trained HVAC Technicians", "Maryland Heating Care", "Request Heating Service",
              "Home Heating Maintenance", "Talk To A Technician", "Heating Care Central MD"],
             ["Heating maintenance for homes in Severn, Severna Park and Columbia, Maryland.",
              "Our technicians check the system and explain what it needs.",
              "Book a heating maintenance visit with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional heating maintenance."], L_SERV),
         rsa(["Heating Due A Service?", "Keep Your Heating Running", "Before The Cold Arrives",
              "Book Heating Maintenance", "Heating Care Near You", "Severn Heating Service",
              "Heating Care Specialists", "Central Maryland Heating", "Book A Service Visit",
              "Talk To A Technician", "Planned Heating Care", "Clear Service Options",
              "Request A Service Visit", "Columbia Heating Care", "Warm Home This Winter"],
             ["A heating system checked before winter is less likely to fail during it.",
              "We inspect the system and set out anything that needs attention.",
              "Heating maintenance across Severn, Severna Park and Columbia homes.",
              "Schedule a heating maintenance visit with Ambient Cooling and Heating."], L_SEAS)],
   services=["Heating Maintenance"])

ag("SKAG | Furnace Tune-Up", "C5", U_HUB, 32.00,
   ["furnace tune up"], ["furnace tune up"],
   "Account search terms: $40.21 / 2 clicks / 0 conversions, CPC $20.11.",
   page_evidence="Heating hub carries real tune-up copy: 'From thorough inspections and "
                 "tune-ups to timely repairs and part replacements...' and 'We recommend "
                 "scheduling a professional tune-up at least once a year, ideally before "
                 "the start of the heating season.'",
   rsas=[rsa(["Furnace Tune Up", "Furnace Tune Up Severn", "Severna Park Furnace Tune Up",
              "Columbia Furnace Tune Up", "Book A Furnace Tune Up", "Annual Furnace Tune Up",
              "Furnace Tune Up Near You", "Central Maryland Furnace", "Schedule A Tune Up",
              "Trained HVAC Technicians", "Maryland Furnace Tune Up", "Request A Tune Up",
              "Home Furnace Tune Up", "Talk To A Technician", "Furnace Tune Up Central MD"],
             ["Furnace tune-ups for homes in Severn, Severna Park and Columbia, Maryland.",
              "A tune-up before the heating season checks the system over properly.",
              "Book a furnace tune-up with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional furnace tune-ups."], L_SERV),
         rsa(["Time For A Tune Up?", "Tune Up Before Winter", "Yearly Furnace Tune Up",
              "Book A Furnace Tune Up", "Furnace Tune Up Near You", "Severn Furnace Tune Up",
              "Furnace Tune Up Service", "Central Maryland Furnace", "Book A Service Visit",
              "Talk To A Technician", "Annual Furnace Check", "Clear Service Options",
              "Request A Tune Up", "Columbia Furnace Tune Up", "Warm Home This Winter"],
             ["We recommend a professional tune-up once a year, before the heating season.",
              "A tune-up checks the system over and flags anything needing attention.",
              "Furnace tune-ups across Severn, Severna Park and Columbia homes.",
              "Schedule a furnace tune-up with Ambient Cooling and Heating."], L_SEAS)],
   services=["Furnace Tune-Up"])

ag("SKAG | Heating Tune-Up", "C5", U_HUB, 32.00,
   ["heating tune up"], ["heating tune up"],
   "Account search terms: 11 terms, 0 clicks, 0 conversions.",
   page_evidence="Heating hub tune-up copy, as above.",
   rsas=[rsa(["Heating Tune Up", "Heating Tune Up Severn", "Severna Park Heating Tune Up",
              "Columbia Heating Tune Up", "Book A Heating Tune Up", "Annual Heating Tune Up",
              "Heating Tune Up Near You", "Central Maryland Heating", "Schedule A Tune Up",
              "Trained HVAC Technicians", "Maryland Heating Tune Up", "Request A Tune Up",
              "Home Heating Tune Up", "Talk To A Technician", "Heating Tune Up Central MD"],
             ["Heating tune-ups for homes in Severn, Severna Park and Columbia, Maryland.",
              "A tune-up before the heating season checks the system over properly.",
              "Book a heating tune-up with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional heating tune-ups."], L_SERV),
         rsa(["Time For A Tune Up?", "Tune Up Before Winter", "Yearly Heating Tune Up",
              "Book A Heating Tune Up", "Heating Tune Up Near You", "Severn Heating Tune Up",
              "Heating Tune Up Service", "Central Maryland Heating", "Book A Service Visit",
              "Talk To A Technician", "Annual Heating Check", "Clear Service Options",
              "Request A Tune Up", "Columbia Heating Tune Up", "Warm Home This Winter"],
             ["We recommend a professional tune-up once a year, before the heating season.",
              "A tune-up checks the system over and flags anything needing attention.",
              "Heating tune-ups across Severn, Severna Park and Columbia homes.",
              "Schedule a heating tune-up with Ambient Cooling and Heating."], L_SEAS)],
   services=["Heating Tune-Up"])

ag("SKAG | Heating System Inspection", "C5", U_HUB, 32.00,
   ["heating system inspection", "heating inspection"],
   ["heating system inspection", "heating inspection"],
   "Account search terms: 5 terms, 0 clicks, 0 conversions.",
   page_evidence="Heating hub names inspections inside the maintenance plan: 'From thorough "
                 "inspections and tune-ups to timely repairs and part replacements...'",
   rsas=[rsa(["Heating System Inspection", "Heating Inspection Severn", "Severna Park Heating",
              "Columbia Heating Inspection", "Book A Heating Inspection", "Heating Check Up",
              "Heating Inspection Near You", "Central Maryland Heating", "Schedule An Inspection",
              "Trained HVAC Technicians", "Maryland Heating Checks", "Request An Inspection",
              "Home Heating Inspection", "Talk To A Technician", "Heating Checks Central MD"],
             ["Heating system inspections across Severn, Severna Park and Columbia, MD.",
              "Our technicians inspect the system and report what they find.",
              "Book a heating system inspection with Ambient Cooling and Heating.",
              "Serving Central Maryland with professional heating inspections."], L_SERV),
         rsa(["Heating System Checked?", "Inspection Before Winter", "Know Your System",
              "Book A Heating Inspection", "Heating Inspection Near You", "Severn Heating Check",
              "Heating Inspection Service", "Central Maryland Heating", "Book An Inspection",
              "Talk To A Technician", "Thorough Heating Checks", "Clear Written Findings",
              "Request An Inspection", "Columbia Heating Check", "Warm Home This Winter"],
             ["A thorough inspection before winter shows what the system actually needs.",
              "We inspect the system and set out anything that needs attention.",
              "Heating system inspections across Severn, Severna Park and Columbia.",
              "Schedule a heating inspection with Ambient Cooling and Heating."], L_SEAS)],
   services=["Heating System Inspection"])

# ======================= C6 - THERMOSTAT SERVICES ============================
_THERMO = [
    ("Thermostat Repair", ["thermostat repair"], ["thermostat repair"],
     "Account search terms: $17.16 / 1 click / 0 conversions. Planner sample ~30/month.",
     [["Thermostat Repair", "Thermostat Repair Severn", "Severna Park Thermostat",
       "Columbia Thermostat Repair", "Book A Thermostat Visit", "Thermostat Repair Near You",
       "Thermostat Technicians", "Central Maryland Thermostat", "Schedule A Repair Visit",
       "Trained HVAC Technicians", "Maryland Thermostat Help", "Request Thermostat Repair",
       "Home Thermostat Repair", "Talk To A Technician", "Thermostat Repair Central MD"],
      ["Thermostat repair for homes in Severn, Severna Park and Columbia, Maryland.",
       "Our technicians diagnose the fault and explain your options clearly.",
       "Book a thermostat repair visit with Ambient Cooling and Heating.",
       "Serving Central Maryland with professional thermostat service."],
      ["Thermostat Not Responding?", "Wrong Temperature Reading?", "Thermostat Blank?",
       "Get Your Thermostat Checked", "Thermostat Repair Near You", "Severn Thermostat Repair",
       "Thermostat Specialists", "Central Maryland Thermostat", "Book A Thermostat Visit",
       "Talk To A Technician", "We Repair Thermostats", "Clear Repair Options",
       "Request Thermostat Service", "Columbia Thermostat Help", "Anne Arundel Thermostat"],
      ["Thermostat trouble in Severn, Severna Park or Columbia? Our technicians help.",
       "We diagnose the problem and walk you through the repair options.",
       "Thermostat repair for Maryland homes and commercial properties.",
       "Schedule a thermostat repair appointment with Ambient Cooling and Heating."]]),
    ("Thermostat Replacement", ["thermostat replacement"],
     ["thermostat replacement", "replace thermostat"],
     "Account search terms: 11 terms, 0 clicks, 0 conversions.",
     [["Thermostat Replacement", "Replace Your Thermostat", "Thermostat Replace Severn",
       "Severna Park Thermostat", "Columbia MD Thermostat", "New Thermostat Fitted",
       "Thermostat Replacement Quote", "Central Maryland Thermostat", "Book An Assessment",
       "Trained HVAC Technicians", "Maryland Thermostat Service", "Request Replacement Info",
       "Plan Your Replacement", "Talk To A Technician", "Thermostat Central MD"],
      ["Thermostat replacement for homes in Severn, Severna Park and Columbia, Maryland.",
       "We check what your system needs and explain the replacement options.",
       "Book a thermostat visit with Ambient Cooling and Heating.",
       "Serving Central Maryland with professional thermostat replacement."],
      ["Old Thermostat Failing?", "Upgrade Your Thermostat", "Thermostat Worn Out?",
       "Replace Your Thermostat", "Thermostat Replace Quote", "Severn Thermostat Help",
       "Thermostat Specialists", "Central Maryland Thermostat", "Book An Assessment",
       "Talk To A Technician", "Plan The Replacement", "Clear Replacement Options",
       "Request An Assessment", "Columbia Thermostat Help", "Better Home Comfort"],
      ["An older thermostat can leave a home warmer or cooler than it should be.",
       "We check compatibility with your system and set out the options.",
       "Thermostat replacement across Severn, Severna Park and Columbia homes.",
       "Schedule a thermostat visit with Ambient Cooling and Heating."]]),
    ("Smart Thermostat Installation", ["smart thermostat installation"],
     ["smart thermostat installation", "nest thermostat installation"],
     "Account search terms: $14.28 / 1 click / 0 conversions.",
     [["Smart Thermostat Install", "Smart Thermostat Severn", "Severna Park Smart Control",
       "Columbia Smart Thermostat", "Book A Smart Thermostat", "Smart Thermostat Fitting",
       "Smart Heating Controls", "Central Maryland Thermostat", "Schedule An Assessment",
       "Trained HVAC Technicians", "Maryland Smart Controls", "Request Install Info",
       "Home Smart Thermostat", "Talk To An Installer", "Smart Controls Central MD"],
      ["Smart thermostat installation across Severn, Severna Park and Columbia, Maryland.",
       "We check compatibility with your system and explain the options clearly.",
       "Book a smart thermostat assessment with Ambient Cooling and Heating.",
       "Serving Central Maryland with professional thermostat installation."],
      ["Want Smarter Heating?", "Upgrade To Smart Controls", "Control Heating By Phone",
       "Book A Smart Thermostat", "Smart Thermostat Near You", "Severn Smart Thermostat",
       "Smart Control Specialists", "Central Maryland Thermostat", "Book An Assessment",
       "Talk To An Installer", "Fitted And Set Up", "Clear Install Options",
       "Request An Assessment", "Columbia Smart Controls", "Better Home Comfort"],
      ["A smart thermostat lets you control your heating from your phone.",
       "We check compatibility with your system before recommending anything.",
       "Smart thermostat installation across Severn, Severna Park and Columbia.",
       "Schedule a smart thermostat assessment with Ambient Cooling and Heating."]]),
]
for _n, _p, _e, _ev, _r in _THERMO:
    ag(f"SKAG | {_n}", "C6", None, 20.00, _p, _e, _ev,
       verdict="HOLD - NO PAGE",
       gate="Capability is CONFIRMED by the owner (2026-09-22), which clears the previous "
            "capability gate. The remaining blocker is purely the destination: NO page on "
            "either domain covers thermostat work as a service. The nearest mention is the "
            "offer HVAC Repair page listing 'thermostat problems' as a diagnostic symptom, "
            "which is not a thermostat service page. RSA payload PREPARED, awaiting URL. "
            "No brand is named in any headline, because brands serviced are not verified.",
       rsas=[rsa(_r[0], _r[1], "RSA A - prepared, awaiting URL"),
             rsa(_r[2], _r[3], "RSA B - prepared, awaiting URL")],
       services=[_n])

# ======================== C7 - GEOTHERMAL HEAT PUMP ==========================
ag("SKAG | Geothermal Heat Pump", "C7", U_GEO, 38.00,
   ["geothermal heat pump", "geothermal heating"],
   ["geothermal heat pump", "geothermal heating", "geothermal installation"],
   "CONTROLLED TEST. Correction to the earlier premise: campaigns NAMED geothermal show "
   "$151.80 / 4 clicks / 0 conversions, but geothermal SEARCH TERMS wherever served show "
   "$1,310.03 / 59 clicks / 4 conversions, CPC $22.20, CPA $327.51 - better than the "
   "account's heating average.",
   page_evidence="Geothermal HVAC page, 5 real geothermal-installation sentences, H2 "
                 "'Energy-Efficient Heating and Cooling with Geothermal HVAC'.",
   rsas=[rsa(["Geothermal Heat Pumps", "Geothermal HVAC Install", "Severn Geothermal HVAC",
              "Severna Park Geothermal", "Columbia MD Geothermal", "Geothermal Installation",
              "Ground Source Heat Pumps", "Central Maryland Geothermal", "Book A Site Review",
              "Geothermal System Fitting", "Trained HVAC Technicians", "Energy Efficient Heating",
              "Geothermal Assessment", "Year Round Comfort", "Request Geothermal Info"],
             ["Geothermal heat pump installation for homes across Central Maryland.",
              "We assess the site and explain how a geothermal system would work.",
              "Geothermal heating and cooling for Severn, Severna Park and Columbia.",
              "Book a geothermal assessment with Ambient Cooling and Heating."], L_SERV),
         rsa(["Considering Geothermal?", "Ground Source Heating", "Geothermal Heat Pumps",
              "Efficient Year Round Comfort", "Geothermal For Your Home", "Maryland Geothermal",
              "Book A Site Assessment", "Talk To A Technician", "Geothermal HVAC Install",
              "Sustainable Home Heating", "Severn Geothermal Install", "Columbia Geothermal",
              "Clear System Options", "Geothermal Explained", "Request An Assessment"],
             ["Geothermal taps underground temperatures to heat and cool your home.",
              "We assess your property and set out whether geothermal suits it.",
              "Geothermal installation across Severn, Severna Park and Columbia.",
              "Schedule a geothermal consultation with Ambient Cooling and Heating."], L_PROB)],
   services=["Geothermal Heat Pump"])

# ============================== CAMPAIGNS =====================================
CAMPAIGNS = {
    "C1": {"reuse": "24257819463", "budget_id": "15885327972",
           "name": "Search | NonBrand | Heating Repair | Central MD | BOFU | 2026-09",
           "rename_to": "Search | NonBrand | Heating & Furnace Repair | Central MD | BOFU | 2026-09",
           "daily": 85.00, "ceiling": 42.00, "enable": True,
           "ready_ad_groups": 4, "total_ad_groups": 6,
           "ceiling_basis": "furnace p75 $42.19 (161 clicks), heating p75 $37.48 (1,413). "
                            "Account CPCs: Furnace Repair $41.70, Heating Repair $10.35. "
                            "Replaces $38.",
           "budget_basis": "Carries the two largest converting heating themes. 4 of 6 ad "
                           "groups can serve; Emergency and No Heat are held."},
    "C2": {"reuse": None,
           "name": "Search | NonBrand | Heat Pump & Ductless Heating | Central MD | BOFU | 2026-09",
           "daily": 15.00, "ceiling": 35.00, "enable": True,
           "ready_ad_groups": 1, "total_ad_groups": 5,
           "ceiling_basis": "heat_pump p75 $32.00 (556 clicks), ductless p75 $31.61 (940).",
           "budget_basis": "Cut to $15 because FOUR of five ad groups point at the blocked "
                           "heat-pumps URL and carry no ads. Only Ductless Heating Repair "
                           "can deliver. Raise to ~$50 in the same motion that unblocks "
                           "the heat-pump page - not before."},
    "C3": {"reuse": "24257819466", "budget_id": "15885327975",
           "name": "Search | NonBrand | Heating Installation | Central MD | BOFU | 2026-09",
           "rename_to": "Search | NonBrand | Heating & Furnace Install & Replace | Central MD | BOFU | 2026-09",
           "daily": 60.00, "ceiling": 46.00, "enable": True,
           "ready_ad_groups": 5, "total_ad_groups": 5,
           "ceiling_basis": "Furnace Replacement $45.97, Furnace Installation $45.39, "
                            "furnace p75 $42.19. Replaces $24, which sat below the "
                            "account's own $25.15 mini-split clearing price.",
           "budget_basis": "ALL five ad groups can serve, after the offer HVAC Installation "
                           "and HVAC Replacement pages were confirmed as genuine heating "
                           "destinations. Install and replace clicks are the most expensive "
                           "non-boiler heating clicks, so this needs real funding."},
    "C4": {"reuse": "24132507744", "budget_id": "15787409438",
           "name": "Search | NonBrand | Gas Boiler Repair | Central MD | BOFU | 2026-08",
           "rename_to": "Search | NonBrand | Boiler Services | Central MD | BOFU | 2026-09",
           "daily": 45.00, "ceiling": 60.00, "enable": True,
           "ready_ad_groups": 2, "total_ad_groups": 5,
           "ceiling_basis": "boiler p75 $55.80 (265 clicks), account Boiler Repair CPC "
                            "$59.32. Deliberately BELOW the gas-boiler p50 of $87.75, which "
                            "was set under uncapped Maximize Clicks. Evidence the current "
                            "$25 binds: this ENABLED campaign bought ONE click all season "
                            "($12.84) and loses 31.2% of impression share to budget.",
           "budget_basis": "The only genuinely budget-limited campaign in the account."},
    "C5": {"reuse": None,
           "name": "Search | NonBrand | Heating Maintenance & Inspection | Central MD | BOFU | 2026-09",
           "daily": 45.00, "ceiling": 32.00, "enable": True,
           "ready_ad_groups": 5, "total_ad_groups": 5,
           "ceiling_basis": "furnace|maintenance $24.80, heating|maintenance $23.38, "
                            "boiler|maintenance $29.22, heat_pump|maintenance $30.25. "
                            "$32 clears all four.",
           "budget_basis": "RAISED from the $30 drafted earlier to $45. All five ad groups "
                           "can serve once the heating hub's real tune-up and inspection "
                           "copy is credited, and this campaign carries the BEST measured "
                           "CPAs in the account (heat_pump|maintenance $185.85, "
                           "furnace|maintenance $230.31)."},
    "C6": {"reuse": None,
           "name": "Search | NonBrand | Thermostat Services | Central MD | BOFU | 2026-09",
           "daily": 15.00, "ceiling": 20.00, "enable": False,
           "ready_ad_groups": 0, "total_ad_groups": 3,
           "ceiling_basis": "No campaign-level history. Only evidence is two account search "
                            "term clicks at $17.16 and $14.28. Conservative cold start.",
           "budget_basis": "Campaign stays PAUSED, so it contributes $0 to the enabled "
                           "total. Budget set now so enabling later needs no budget "
                           "approval. No ad group can serve: no thermostat page exists."},
    "C7": {"reuse": None,
           "name": "Search | NonBrand | Geothermal Heat Pump | Central MD | BOFU | 2026-09",
           "daily": 20.00, "ceiling": 38.00, "enable": True,
           "ready_ad_groups": 1, "total_ad_groups": 1,
           "ceiling_basis": "Campaign-named geothermal mean $37.95, p50 $35.83. Geothermal "
                            "search terms $22.20 CPC on 59 clicks.",
           "budget_basis": "Controlled test with a stop-loss. Destination passes 3/3."},
}

COMMERCIAL = {
    "campaign_id": "24132507747", "budget_id": "15787409441",
    "campaign": "Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08",
    "from_usd": 95.00, "to_usd": 20.00,
    "residential_ad_group": "202339087634",
    "commercial_ad_group": "199748801029",
    "why": "The campaign carries BOTH the residential HVAC Installation ad group and the "
           "separately scoped Commercial HVAC Installation ad group. Pausing the campaign "
           "would stop an approved commercial service, so only the residential ad group is "
           "paused and the campaign stays ENABLED at a $20 holding allocation.",
    "commercial_state": "Ad group ENABLED, 2 keywords ELIGIBLE, 2 ads APPROVED but BOTH "
                        "PAUSED, destination live at HTTP 200, all-time delivery 0 "
                        "impressions and $0.00. It spends nothing until its ads are "
                        "enabled, which is a separate owner decision.",
}

# =========================== CROSS-NEGATIVES ==================================
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
    "SKAG | Geothermal Heat Pump": ["ductless", "mini split", "boiler", "furnace",
                                    "thermostat", "repair", "maintenance", "tune up"],
}

# ======================== COOLING PAUSE INVENTORY =============================
COOLING_PAUSE = {
    "24132507741": {"campaign": "Search | NonBrand | AC Repair | Central MD | BOFU | 2026-08",
                    "level": "CAMPAIGN",
                    "ad_groups": {"202339087834": "SKAG | AC Repair Near Me"},
                    "rollback": {"status": "ENABLED", "daily": 45.00,
                                 "budget_id": "15787409435", "ceiling": 25.00}},
    "24132507750": {"campaign": "Search | NonBrand | HVAC Repair | Central MD | BOFU | 2026-08",
                    "level": "CAMPAIGN",
                    "ad_groups": {"202339087674": "SKAG | HVAC Repair Near Me"},
                    "rollback": {"status": "ENABLED", "daily": 70.00,
                                 "budget_id": "15787409444", "ceiling": 25.00}},
    "24132507753": {"campaign": "Search | NonBrand | HVAC Replacement | Central MD | BOFU | 2026-08",
                    "level": "CAMPAIGN",
                    "ad_groups": {"200159223798": "SKAG | HVAC Replacement Near Me"},
                    "rollback": {"status": "ENABLED", "daily": 15.00,
                                 "budget_id": "15787409447", "ceiling": 30.00}},
    "24132507747": {"campaign": "Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08",
                    "level": "AD_GROUP",
                    "ad_groups": {"202339087634": "SKAG | HVAC Installation"},
                    "preserve": {"199748801029": "SKAG | Commercial HVAC Installation"},
                    "rollback": {"status": "ENABLED", "daily": 95.00,
                                 "budget_id": "15787409441", "ceiling": 30.00,
                                 "ad_group_202339087634_status": "ENABLED",
                                 "enabled_ads": ["821319509197", "821319509200"]}},
}

# ============================== VALIDATION ====================================
TOK = re.compile(r"[a-z0-9']+")
BARRED = {
    "same_day": re.compile(r"\bsame[- ]day\b", re.I),
    "always_open": re.compile(r"\b(24/7|24-7|24 hour|round the clock|any ?time)\b", re.I),
    "emergency_promise": re.compile(r"\bemergency (service|dispatch|repair|callout)\b", re.I),
    "arrival_promise": re.compile(r"\b(today|tonight|within \d+|fast response|rapid)\b", re.I),
    "guarantee": re.compile(r"\bguarantee", re.I),
    "licensed_insured": re.compile(r"\blicen[cs]ed\b|\binsured\b", re.I),
    "best_top_trusted": re.compile(r"\b(best|top[- ]rated|#1|number one|most trusted)\b", re.I),
    "free_offer": re.compile(r"\bfree (estimate|consultation|quote|service)\b", re.I),
    "ratings": re.compile(r"\b\d+(\.\d+)?\s*star|\b\d{2,}\+?\s*review", re.I),
    "financing": re.compile(r"\bfinanc|\bmonthly payment|\b0% apr\b", re.I),
    "phone": re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b|\(\d{3}\)\s*\d{3}[-. ]?\d{4}"),
    "brand_claim": re.compile(r"\b(nest|ecobee|honeywell|carrier|trane|lennox|rheem)\b", re.I),
}
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
SNIPPETS = {
    "C2": ["Heat Pump Repair", "Heat Pump Installation", "Ductless Heating",
           "Mini Split Service"],
    "C5": ["Furnace Maintenance", "Heating Maintenance", "Heating Tune-Up",
           "System Inspection"],
    "C6": ["Thermostat Repair", "Thermostat Replacement", "Smart Thermostat Install"],
    "C7": ["Geothermal Heat Pump", "Heat Pump Installation", "Heating Installation",
           "Ductless Heating"],
}
REUSE_CALLOUTS = ["422477374526", "422577760603", "422577771364",
                  "422577777430", "422577777442"]
REUSE_SITELINKS = ["422577777457", "422577771382", "422477374559"]


def toks(s):
    return TOK.findall(s.lower())


def pblocks(neg, q):
    a, b = toks(neg), toks(q)
    return bool(a) and any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))


def contig(inner, outer):
    a, b = toks(inner), toks(outer)
    return len(a) <= len(b) and any(b[i:i + len(a)] == a
                                    for i in range(len(b) - len(a) + 1))


def validate(live_kw):
    errs, warns = [], []
    for n, d in AG.items():
        for r in d["rsas"]:
            if len(r["h"]) != 15:
                errs.append(f"{n}/{r['label']}: {len(r['h'])} headlines, need 15")
            if len(r["d"]) != 4:
                errs.append(f"{n}/{r['label']}: {len(r['d'])} descriptions, need 4")
            for h in r["h"]:
                if len(h) > 30:
                    errs.append(f"{n}: headline {len(h)}>30 '{h}'")
            for x in r["d"]:
                if len(x) > 90:
                    errs.append(f"{n}: description {len(x)}>90 '{x}'")
            if len(set(r["h"])) != len(r["h"]):
                errs.append(f"{n}/{r['label']}: duplicate headline inside the RSA")
            if len(set(r["d"])) != len(r["d"]):
                errs.append(f"{n}/{r['label']}: duplicate description inside the RSA")
            for lab, rx in BARRED.items():
                for t in r["h"] + r["d"]:
                    if rx.search(t):
                        errs.append(f"{n}/{r['label']}: BARRED '{lab}' in '{t}'")
        if len(d["rsas"]) == 2 and set(d["rsas"][0]["h"]) == set(d["rsas"][1]["h"]):
            errs.append(f"{n}: RSA A and B are not differentiated")
        # A READY ad group must have a URL; a HOLD ad group must not be uploaded.
        if d["verdict"] == "READY" and not d["url"] and not d["existing_ad_group_id"]:
            errs.append(f"{n}: marked READY but has no final URL")
        if d["verdict"] == "READY" and not d["rsas"] and not d["existing_ad_group_id"]:
            errs.append(f"{n}: marked READY but no RSA drafted")
        if d["verdict"] != "READY" and not d["launch_gate"]:
            errs.append(f"{n}: held without a stated launch gate")
        for k in d["phrase"] + d["exact"]:
            if k != k.lower().strip():
                errs.append(f"{n}: keyword not normalised '{k}'")
        for x in d["phrase"]:
            cov = [y for y in d["phrase"] if y != x and contig(y, x)]
            if cov:
                errs.append(f"{n}: PHRASE '{x}' already matched by PHRASE {cov}")

    seen = {}
    for n, d in AG.items():
        for k in d["phrase"]:
            seen.setdefault((k, "PHRASE"), []).append(n)
        for k in d["exact"]:
            seen.setdefault((k, "EXACT"), []).append(n)
    for (k, m), owners in seen.items():
        if len(owners) > 1:
            errs.append(f"keyword collision '{k}' [{m}] in {owners}")

    for n, negs in XNEG.items():
        if n not in AG:
            errs.append(f"cross-negative set for unknown ad group '{n}'")
            continue
        gone = {(t.lower(), m) for t, m in AG[n].get("remove_keywords", [])}
        own = AG[n]["phrase"] + AG[n]["exact"] + [
            t for t, m in live_kw.get(n, []) if (t.lower(), m) not in gone]
        for neg in negs:
            for k in own:
                if pblocks(neg, k):
                    errs.append(f"SELF-BLOCK {n}: '{neg}' blocks own keyword '{k}'")
    for n in AG:
        if n not in XNEG:
            errs.append(f"{n}: no cross-negative set")

    for k, vals in SNIPPETS.items():
        if not 3 <= len(vals) <= 10:
            errs.append(f"SNIPPET {k}: {len(vals)} values, need 3-10")
        for v in vals:
            if len(v) > 25:
                errs.append(f"SNIPPET {k}: value {len(v)}>25 '{v}'")

    # schedule must sit inside verified answered hours
    for s in SCHEDULE:
        if s["start_hour"] < 8 or s["end_hour"] > 16:
            errs.append(f"SCHEDULE {s['day']} {s['start_hour']}-{s['end_hour']} is outside "
                        f"the verified answered hours 08:00-16:00")
    if any(s["day"] in ("SATURDAY", "SUNDAY") for s in SCHEDULE):
        errs.append("SCHEDULE includes a weekend day; Ambient publishes CLOSED Sat and Sun")

    enabled = round(sum(v["daily"] for v in CAMPAIGNS.values() if v["enable"])
                    + COMMERCIAL["to_usd"], 2)
    if enabled > WORKING_TARGET:
        errs.append(f"BUDGET enabled ${enabled} exceeds ${WORKING_TARGET}")
    if round(enabled * 30.4, 2) > CAP_MONTH:
        errs.append(f"BUDGET ${enabled}/day x 30.4 exceeds ${CAP_MONTH}")
    for k, v in CAMPAIGNS.items():
        if v["enable"] and v["ready_ad_groups"] == 0:
            errs.append(f"{k}: marked enable but has 0 ready ad groups")
        if not v["enable"] and v["ready_ad_groups"] > 0:
            warns.append(f"{k}: has {v['ready_ad_groups']} ready ad groups but stays paused")

    covered = set()
    for d in AG.values():
        covered |= set(d["services_covered"])
    missing = [s for s in REQUESTED_31 if s not in covered]
    extra = [s for s in covered if s not in REQUESTED_31 and s != "Gas Boiler Repair"]
    if missing:
        errs.append(f"COVERAGE missing {len(missing)}: {missing}")
    if extra:
        errs.append(f"COVERAGE unrequested: {extra}")
    return errs, warns, enabled


def main():
    c = client()
    identity_gate(c, verbose=True)

    live_kw = {}
    for r in q(c, """SELECT ad_group.id, ad_group_criterion.keyword.text,
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

    errs, warns, enabled = validate(live_kw)
    print("\n=== LOCAL VALIDATION ===")
    for w in warns:
        print(f"   WARN {w}")
    if errs:
        for e in errs:
            print(f"   FAIL {e}")
        print(f"\n{len(errs)} problems. Plans NOT fingerprinted.")
        sys.exit(1)
    print("   PASS - RSA limits and barred claims, keyword hygiene, self-block, snippets, "
          "schedule inside answered hours, budget, 31-service coverage")

    ready = [n for n, d in AG.items() if d["verdict"] == "READY"]
    held = [n for n, d in AG.items() if d["verdict"] != "READY"]
    new_ag = [n for n, d in AG.items() if not d["existing_ad_group_id"]]
    n_kw = sum(len(d["phrase"]) + len(d["exact"]) for d in AG.values())
    rsa_create = sum(len(d["rsas"]) for n, d in AG.items() if d["verdict"] == "READY")
    rsa_prep = sum(len(d["rsas"]) for n, d in AG.items() if d["verdict"] != "READY")

    print(f"\n=== STRUCTURE ===")
    print(f"   campaigns        7 ({sum(1 for v in CAMPAIGNS.values() if not v['reuse'])} "
          f"new, {sum(1 for v in CAMPAIGNS.values() if v['reuse'])} reused)")
    print(f"   ad groups       {len(AG)} ({len(new_ag)} new, {len(AG)-len(new_ag)} reused)")
    print(f"   READY to enable {len(ready)}")
    print(f"   HELD            {len(held)}")
    print(f"   keywords        {n_kw} new")
    print(f"   RSAs to create  {rsa_create}   prepared-awaiting-URL {rsa_prep}")
    print(f"\n=== BUDGET ===")
    for k, v in CAMPAIGNS.items():
        st = "ENABLE" if v["enable"] else "PAUSED"
        print(f"   {k:4s} {st:6s} ${v['daily']:6.2f}/day  ceil ${v['ceiling']:6.2f}  "
              f"ready {v['ready_ad_groups']}/{v['total_ad_groups']}")
    print(f"   COMM ENABLE ${COMMERCIAL['to_usd']:6.2f}/day  (holding)")
    print(f"   ENABLED TOTAL ${enabled:.2f}  cap ${WORKING_TARGET}  "
          f"monthly ${enabled*30.4:,.2f}")

    base = {"customer_id": CID, "exact_account_name": EXACT_NAME,
            "never_write_to_mcc": GM_MANAGER, "built_local": STAMP}
    BASIS = json.loads((SNAP / "budget-basis-2026-09-21.json").read_text(encoding="utf-8"))
    SEP = BASIS["september"]

    # -------- STAGE 1 : create paused -------------------------------------
    ops1 = (
        [{"op": "CREATE_CAMPAIGN_BUDGET", "campaign_key": k, "amount_usd": v["daily"]}
         for k, v in CAMPAIGNS.items() if not v["reuse"]]
        + [{"op": "CREATE_CAMPAIGN_PAUSED", "campaign_key": k, "name": v["name"],
            "cpc_bid_ceiling_usd": v["ceiling"]}
           for k, v in CAMPAIGNS.items() if not v["reuse"]]
        + [{"op": "RENAME_CAMPAIGN", "campaign_id": v["reuse"], "from": v["name"],
            "to": v["rename_to"]} for v in CAMPAIGNS.values()
           if v["reuse"] and v.get("rename_to")]
        + [{"op": "ADD_CAMPAIGN_LOCATIONS", "campaign_key": k, "count": 75}
           for k, v in CAMPAIGNS.items() if not v["reuse"]]
        + [{"op": "SET_CAMPAIGN_AD_SCHEDULE", "campaign_key": k, "schedule": SCHEDULE,
            "count": len(SCHEDULE),
            "why": "Mon-Fri 08:00-16:00, the hours Ambient publishes and answers."}
           for k in CAMPAIGNS]
        + [{"op": "CREATE_AD_GROUP_PAUSED", "ad_group": n, "campaign_key": d["campaign_key"],
            "final_url": d["url"], "cpc_bid_usd": d["cpc_bid"], "verdict": d["verdict"]}
           for n, d in AG.items() if not d["existing_ad_group_id"]]
        + [{"op": "RENAME_AD_GROUP", "ad_group_id": d["existing_ad_group_id"],
            "from": d["rename_from"], "to": n}
           for n, d in AG.items() if d.get("rename_from")]
        + [{"op": "REMOVE_KEYWORDS_FROM_EXISTING_AD_GROUP", "ad_group": n,
            "ad_group_id": d["existing_ad_group_id"],
            "keywords": [{"text": t, "match_type": m} for t, m in d["remove_keywords"]],
            "count": len(d["remove_keywords"])}
           for n, d in AG.items() if d.get("remove_keywords")]
        + [{"op": "ADD_KEYWORDS_PAUSED", "ad_group": n, "phrase": d["phrase"],
            "exact": d["exact"], "count": len(d["phrase"]) + len(d["exact"])}
           for n, d in AG.items() if d["phrase"] or d["exact"]]
        + [{"op": "CREATE_RSA_PAUSED", "ad_group": n, "label": r["label"],
            "final_url": d["url"], "headlines": r["h"], "descriptions": r["d"]}
           for n, d in AG.items() if d["verdict"] == "READY" for r in d["rsas"]]
        + [{"op": "ADD_AD_GROUP_CROSS_NEGATIVES", "ad_group": n, "match_type": "PHRASE",
            "negatives": XNEG[n], "count": len(XNEG[n])} for n in AG]
        + [{"op": "LINK_EXISTING_CALL_ASSET", "asset_id": "407995613637",
            "campaign_key": k} for k, v in CAMPAIGNS.items() if not v["reuse"]]
        + [{"op": "LINK_EXISTING_BUSINESS_NAME_ASSET", "asset_id": "80516971145",
            "campaign_key": k} for k, v in CAMPAIGNS.items() if not v["reuse"]]
        + [{"op": "LINK_EXISTING_CALLOUT_ASSETS", "campaign_key": k,
            "asset_ids": REUSE_CALLOUTS, "count": 5, "reused_not_created": True}
           for k, v in CAMPAIGNS.items() if not v["reuse"]]
        + [{"op": "LINK_EXISTING_SITELINK_ASSETS", "campaign_key": k,
            "asset_ids": REUSE_SITELINKS, "count": 3, "reused_not_created": True,
            "no_blocked_url": True}
           for k, v in CAMPAIGNS.items() if not v["reuse"]]
        + [{"op": "CREATE_STRUCTURED_SNIPPET_AND_LINK", "campaign_key": k,
            "header": "Services", "values": SNIPPETS[k], "count": 1}
           for k, v in CAMPAIGNS.items() if not v["reuse"]]
        + [{"op": "UPDATE_CALL_ASSET_SCHEDULE", "asset_id": "407995613637",
            "schedule": SCHEDULE, "count": len(SCHEDULE),
            "exclusivity_proven": "7 campaign links, all in-scope Ambient campaigns; 0 "
                                  "customer-level links; 0 ad-group links (checked "
                                  "2026-09-22). CallAsset.ad_schedule_targets lives on the "
                                  "ASSET, so this rewrites hours on every link - which is "
                                  "intended, because all 7 must respect answered hours.",
            "from": "Mon-Fri 08:00-20:00 + Sat 08:00-13:00 (6 rows)",
            "to": "Mon-Fri 08:00-16:00 (5 rows)"}])
    stage1 = dict(base, **{
        "plan_name": "AMB-0922-BUILD-1", "approval_class": "create-paused",
        "everything_created_paused": True, "nothing_enabled": True,
        "cooling_untouched": True,
        "campaigns": CAMPAIGNS, "ad_groups": AG, "cross_negatives": XNEG,
        "schedule": SCHEDULE,
        "schedule_evidence": "Ambient publishes Mon-Fri 08:00-16:00 and CLOSED Sat/Sun, in "
                             "contact-page copy AND schema.org OpeningHoursSpecification "
                             "(opens 08:00, closes 16:00), read 2026-09-22. The live "
                             "account schedule of Mon-Fri 08:00-20:00 + Sat 08:00-13:00 was "
                             "entered by a human in the Google Ads web client on 2026-08-17 "
                             "and is an advertising schedule, not evidence of answered "
                             "hours. No 24/7 claim appears anywhere on the site.",
        "ready_ad_groups": ready, "held_ad_groups": held,
        "rsas_prepared_awaiting_url": {
            n: [r["label"] for r in d["rsas"]]
            for n, d in AG.items() if d["verdict"] != "READY" and d["rsas"]},
        "search_settings": {
            "network": "Google Search only", "search_partners": False, "display": False,
            "performance_max": False, "ai_max": False, "dsa": False,
            "broad_match_expansion": False, "final_url_expansion": False,
            "automatically_created_assets": False, "geo": "PRESENCE / PRESENCE",
            "match_types": ["PHRASE", "EXACT"],
            "contains_eu_political_advertising":
                "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"},
        "operations": ops1})
    stage1["operation_count"] = len(ops1)
    stage1["fingerprint"] = approval_code(stage1)

    # -------- STAGE 2 : cooling pause + budgets (cooling FIRST) ------------
    ops2 = ([{"op": "PAUSE_CAMPAIGN", "campaign_id": cid, "campaign": v["campaign"]}
             for cid, v in COOLING_PAUSE.items() if v["level"] == "CAMPAIGN"]
            + [{"op": "PAUSE_AD_GROUP", "campaign_id": cid, "ad_group_id": agid,
                "ad_group": nm}
               for cid, v in COOLING_PAUSE.items() if v["level"] == "AD_GROUP"
               for agid, nm in v["ad_groups"].items()]
            + [{"op": "UPDATE_CAMPAIGN_BUDGET_AMOUNT",
                "budget_id": COMMERCIAL["budget_id"],
                "campaign_id": COMMERCIAL["campaign_id"],
                "from_usd": COMMERCIAL["from_usd"], "to_usd": COMMERCIAL["to_usd"]}]
            + [{"op": "UPDATE_CAMPAIGN_BUDGET_AMOUNT", "budget_id": v["budget_id"],
                "campaign_id": v["reuse"], "to_usd": v["daily"]}
               for v in CAMPAIGNS.values() if v["reuse"]]
            + [{"op": "UPDATE_CAMPAIGN_CPC_BID_CEILING", "campaign_id": v["reuse"],
                "to_usd": v["ceiling"]} for v in CAMPAIGNS.values() if v["reuse"]])
    stage2 = dict(base, **{
        "plan_name": "AMB-0922-COOLPAUSE-BUDGET-1",
        "approval_class": "pause-delivery-and-reallocate",
        "sequencing": "Cooling is paused and the commercial budget is reduced BEFORE any "
                      "heating budget rises, inside one plan, so the enabled total never "
                      "exceeds its end state even momentarily.",
        "nothing_deleted": True,
        "commercial_preserved": COMMERCIAL,
        "inventory": COOLING_PAUSE,
        "rollback": "Every original campaign status, budget, ceiling, ad-group status and "
                    "enabled ad ID is in 'inventory'. Reversal is a status flip back to the "
                    "recorded values; nothing is removed, so nothing must be recreated.",
        "operations": ops2})
    stage2["operation_count"] = len(ops2)
    stage2["fingerprint"] = approval_code(stage2)

    # -------- STAGE 3 : enable the ready heating services ------------------
    ops3 = ([{"op": "ENABLE_CAMPAIGN", "campaign_key": k,
              "campaign_id": v.get("reuse"), "name": v["name"]}
             for k, v in CAMPAIGNS.items() if v["enable"]]
            + [{"op": "ENABLE_AD_GROUP", "ad_group": n, "campaign_key": d["campaign_key"]}
               for n, d in AG.items() if d["verdict"] == "READY"]
            + [{"op": "ENABLE_KEYWORDS", "ad_group": n,
                "count": len(d["phrase"]) + len(d["exact"])}
               for n, d in AG.items()
               if d["verdict"] == "READY" and (d["phrase"] or d["exact"])]
            + [{"op": "ENABLE_RSAS", "ad_group": n, "count": len(d["rsas"])}
               for n, d in AG.items() if d["verdict"] == "READY" and d["rsas"]])
    stage3 = dict(base, **{
        "plan_name": "AMB-0922-ENABLE-1", "approval_class": "enable-delivery",
        "runs_only_after": "AMB-0922-BUILD-1 executed and read back, and "
                           "AMB-0922-COOLPAUSE-BUDGET-1 executed.",
        "enables_only_ready": True,
        "held_not_enabled": {n: AG[n]["launch_gate"] for n in held},
        "enabled_daily_total_after": enabled,
        "september": {"read_on": BASIS["account_today"],
                      "mtd": SEP["mtd_incl_partial_today"],
                      "days_left": SEP["days_left_incl_today"],
                      "remaining_allowance": SEP["remaining_allowance"],
                      "projection_worst_case": round(
                          SEP["mtd_incl_partial_today"]
                          + enabled * SEP["days_left_incl_today"], 2)},
        "operations": ops3})
    stage3["operation_count"] = len(ops3)
    stage3["fingerprint"] = approval_code(stage3)

    PLANS.mkdir(parents=True, exist_ok=True)
    print("\n=== PLANS ===")
    for p in (stage1, stage2, stage3):
        (PLANS / f"{p['plan_name']}.json").write_text(
            json.dumps(p, indent=1, default=str), encoding="utf-8")
        print(f"  {p['plan_name']} {p['fingerprint']} {p['operation_count']} operations")

    matrix = []
    for s in REQUESTED_31:
        n = next(n for n, d in AG.items() if s in d["services_covered"])
        d = AG[n]
        matrix.append({"service": s, "ad_group": n, "campaign_key": d["campaign_key"],
                       "final_url": d["url"], "verdict": d["verdict"],
                       "rsas": len(d["rsas"]),
                       "keywords": len(d["phrase"]) + len(d["exact"]),
                       "existing_ad_group_id": d["existing_ad_group_id"],
                       "launch_gate": d["launch_gate"]})
    (SNAP / f"coverage-{STAMP}.json").write_text(
        json.dumps({"matrix": matrix, "enabled_total": enabled}, indent=1, default=str),
        encoding="utf-8")
    print(f"\n=== 31-SERVICE MAP ===")
    for i, m in enumerate(matrix, 1):
        print(f"{i:3d} {m['service']:32s} {m['campaign_key']:4s} {m['verdict'][:34]:34s} "
              f"rsa={m['rsas']}")
    print("\nEXTERNAL WRITES: 0 (local draft only)")


if __name__ == "__main__":
    main()
