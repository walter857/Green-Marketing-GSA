#!/usr/bin/env python3
"""Ambient | 2026-09-16 | build heating work orders, scorecard and fingerprinted plans.

LOCAL FILE WRITES ONLY. No Google Ads mutate, no validate_only, no external write.
"""
from __future__ import annotations
import sys, json, csv, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

STAMP = "2026-09-16"
CLIENT_DIR = ROOT / "clients" / "ambient-cooling-heating"
WO = CLIENT_DIR / "work-orders"
WO.mkdir(parents=True, exist_ok=True)
EXPORTS.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- normalization
NORM = [
    # original, canonical cluster, intent, equipment, action, own_ad_group, own_page, reason
    ("Furnace repair", "Furnace & Heating Repair", "BOFU fix-it", "Furnace", "Repair", "YES", "YES", "Highest heating demand (320+140/mo) and the account's best historical CPA ($252.83). Anchor of the cluster."),
    ("Gas furnace repair", "Furnace & Heating Repair", "BOFU fix-it", "Gas furnace", "Repair", "no", "no", "20/mo. Fuel type is a qualifier, not a separate buying decision. Covered by Phrase 'furnace repair'."),
    ("Electric furnace repair", "HOLD", "BOFU fix-it", "Electric furnace", "Repair", "no", "no", "No capability evidence on the site and no Planner volume returned."),
    ("Heating repair", "Furnace & Heating Repair", "BOFU fix-it", "Any heating", "Repair", "no", "no", "70+20/mo. Same page, same ad, same technician visit as furnace repair."),
    ("Emergency heating repair", "HOLD", "BOFU urgent", "Any heating", "Repair", "no", "no", "10/mo, and 'emergency' is a BARRED CLAIM in client.yaml. Cannot be advertised without verified 24/7 staffing."),
    ("No-heat repair", "Furnace & Heating Repair", "BOFU urgent", "Any heating", "Repair", "no", "no", "0/mo in Planner. Folded in as a Phrase keyword only, not its own group."),
    ("Heating system inspection", "Heating Maintenance", "MOFU", "Any heating", "Maintenance", "no", "no", "10/mo. Same job as a tune-up."),
    ("Furnace maintenance", "Heating Maintenance", "MOFU", "Furnace", "Maintenance", "TIER B", "no", "70/mo, but a tune-up ticket cannot carry a $250+ CPQL."),
    ("Furnace tune-up", "Heating Maintenance", "MOFU", "Furnace", "Maintenance", "no", "no", "30/mo. Exact synonym of furnace maintenance - one bucket."),
    ("Heating maintenance", "Heating Maintenance", "MOFU", "Any heating", "Maintenance", "no", "no", "10/mo. Same bucket."),
    ("Heating tune-up", "Heating Maintenance", "MOFU", "Any heating", "Maintenance", "no", "no", "10/mo. Same bucket."),
    ("Furnace installation", "Heating Installation & Replacement", "BOFU high-ticket", "Furnace", "Install", "YES", "YES", "70+30/mo. High ticket. Historical Heating Installation CPA $515."),
    ("Furnace replacement", "Heating Installation & Replacement", "BOFU high-ticket", "Furnace", "Replace", "no", "no", "Buyer treats install and replace as one decision; both end in a new furnace quote."),
    ("Heating installation", "Heating Installation & Replacement", "BOFU high-ticket", "Any heating", "Install", "no", "no", "10/mo alone; merges into the furnace install page."),
    ("Heating system installation", "Heating Installation & Replacement", "BOFU high-ticket", "Any heating", "Install", "no", "no", "Exact synonym of heating installation."),
    ("Heating replacement", "Heating Installation & Replacement", "BOFU high-ticket", "Any heating", "Replace", "no", "no", "Synonym cluster."),
    ("Heating system replacement", "Heating Installation & Replacement", "BOFU high-ticket", "Any heating", "Replace", "no", "no", "Synonym cluster."),
    ("Heat pump repair", "Heat Pump & Ductless", "BOFU fix-it", "Heat pump", "Repair", "YES", "YES", "140/mo and 21 qualified WhatConverts leads in 12 months - the single largest heating cluster by qualified leads."),
    ("Heat pump installation", "Heat Pump & Ductless", "BOFU high-ticket", "Heat pump", "Install", "no", "no", "50/mo. Same dedicated /heat-pumps/ page covers repair and install."),
    ("Heat pump replacement", "Heat Pump & Ductless", "BOFU high-ticket", "Heat pump", "Replace", "no", "no", "10/mo. Same decision as install."),
    ("Heat pump maintenance", "Heat Pump & Ductless", "MOFU", "Heat pump", "Maintenance", "no", "no", "No standalone volume."),
    ("Ductless mini-split installation", "Heat Pump & Ductless", "BOFU high-ticket", "Mini-split", "Install", "no", "no", "40/mo. Ambient's own heat-pump page names ductless mini-splits as a heat-pump type."),
    ("Mini-split installs", "Heat Pump & Ductless", "BOFU high-ticket", "Mini-split", "Install", "no", "no", "20/mo. Same bucket as ductless mini-split installation."),
    ("Ductless heating installation", "Heat Pump & Ductless", "BOFU high-ticket", "Mini-split", "Install", "no", "no", "10/mo. Same bucket."),
    ("Ductless heating repair", "Heat Pump & Ductless", "BOFU fix-it", "Mini-split", "Repair", "no", "no", "Folded into heat pump repair."),
    ("Boiler repair", "Boiler", "BOFU fix-it", "Boiler", "Repair", "TIER B", "existing", "30/mo but historical CPC $89.90-$106.03 and only 8 of 20 paid leads qualified. An ENABLED Gas Boiler Repair campaign already exists - do not duplicate."),
    ("Boiler replacement", "Boiler", "BOFU high-ticket", "Boiler", "Replace", "TIER B", "no", "10/mo. Same economics problem."),
    ("Boiler installation", "Boiler", "BOFU high-ticket", "Boiler", "Install", "TIER B", "no", "10/mo. Gas Boilers Installs historically cost $106.03/click for 11 conversions."),
    ("Boiler maintenance", "Boiler", "MOFU", "Boiler", "Maintenance", "no", "no", "No measurable volume."),
    ("Thermostat repair", "HOLD", "BOFU low-ticket", "Thermostat", "Repair", "no", "no", "40/mo but NO capability evidence on the Ambient site. HOLD - CLIENT CAPABILITY NOT VERIFIED."),
    ("Thermostat replacement", "HOLD", "BOFU low-ticket", "Thermostat", "Replace", "no", "no", "30/mo, capability unverified, and a thermostat ticket cannot carry heating CPQL."),
    ("Smart thermostat installation", "HOLD", "BOFU low-ticket", "Thermostat", "Install", "no", "no", "10/mo, capability unverified."),
    ("Geothermal heat pump", "EXCLUDE", "BOFU high-ticket", "Geothermal", "Install", "no", "no", "Dedicated page exists, but Geothermal HVAC spent $151.80 for 4 clicks and ZERO conversions, and Planner returns no meaningful local volume."),
]

# ---------------------------------------------------------------- scorecard
SCORE = [
    {"cluster": "Furnace & Heating Repair", "capability": "VERIFIED (dedicated page /services/heating-services/furnace-repair/)",
     "planner_demand_10city": 460, "planner_competition": "LOW", "planner_jan_peak": 720,
     "hist_campaign": "Heating Repair (PAUSED)", "hist_spend": 17445.53, "hist_clicks": 930,
     "hist_cpc": 18.76, "hist_conv": 69.0, "hist_cpa": 252.83,
     "wc_qualified_12mo": 24, "wc_paid_12mo": 8,
     "ticket": "MID - repair ticket, MD benchmark $150-$450",
     "tier": "A", "confidence": "HIGH",
     "why": "Best CPA in the entire account history, largest heating demand, LOW competition, verified capability, strong seasonal ramp."},
    {"cluster": "Heat Pump & Ductless", "capability": "VERIFIED (dedicated page /services/heating-services/heat-pumps/ + /cooling-services/mini-splits/)",
     "planner_demand_10city": 260, "planner_competition": "LOW", "planner_jan_peak": 480,
     "hist_campaign": "Mini Split (PAUSED)", "hist_spend": 22183.67, "hist_clicks": 882,
     "hist_cpc": 25.15, "hist_conv": 28.5, "hist_cpa": 778.38,
     "wc_qualified_12mo": 36, "wc_paid_12mo": 9,
     "ticket": "HIGH - system install, MD benchmark $5,000-$13,500",
     "tier": "A", "confidence": "HIGH",
     "why": "Largest qualified-lead cluster in WhatConverts (36 of 98 heating qualified). Year-round relevance - heat pumps both heat and cool. High ticket."},
    {"cluster": "Heating Installation & Replacement", "capability": "VERIFIED (8 pages; dedicated /oil-furnace-installations/ and /oil-replacement/)",
     "planner_demand_10city": 200, "planner_competition": "LOW-MEDIUM", "planner_jan_peak": 110,
     "hist_campaign": "Heating Installation (PAUSED) + #2 (REMOVED)", "hist_spend": 23142.58,
     "hist_clicks": 1429, "hist_cpc": 16.19, "hist_conv": 47.0, "hist_cpa": 492.40,
     "wc_qualified_12mo": 8, "wc_paid_12mo": 4,
     "ticket": "HIGH - MD benchmark $5,000-$13,500",
     "tier": "A", "confidence": "MEDIUM-HIGH",
     "why": "Highest ticket value, cheap historical clicks ($16.19), and the August cooling analysis already proved install/replace intent carries 94% of pipeline value."},
    {"cluster": "Heating Maintenance", "capability": "VERIFIED (heating-services hub names inspections, tune-ups and maintenance plans)",
     "planner_demand_10city": 130, "planner_competition": "LOW", "planner_jan_peak": 170,
     "hist_campaign": "Heating Maintenance (PAUSED)", "hist_spend": 7435.88, "hist_clicks": 289,
     "hist_cpc": 25.73, "hist_conv": 23.3, "hist_cpa": 318.68,
     "wc_qualified_12mo": 10, "wc_paid_12mo": 3,
     "ticket": "LOW - MD tune-up benchmark ~$165",
     "tier": "B", "confidence": "MEDIUM",
     "why": "Decent CPA history, but a ~$165 tune-up ticket cannot carry a $250-$320 CPQL. Viable only as a loss-leader into replacement, which requires proof we do not have."},
    {"cluster": "Boiler", "capability": "VERIFIED (dedicated page /services/heating-services/boiler-repair/)",
     "planner_demand_10city": 120, "planner_competition": "LOW-HIGH mixed", "planner_jan_peak": None,
     "hist_campaign": "Gas Boilers Installs + Gas Boilers Repair (PAUSED)", "hist_spend": 15819.82,
     "hist_clicks": 160, "hist_cpc": 98.87, "hist_conv": 20.0, "hist_cpa": 790.99,
     "wc_qualified_12mo": 8, "wc_paid_12mo": 20,
     "ticket": "HIGH - but CPC is punishing",
     "tier": "B", "confidence": "MEDIUM",
     "why": "$98.87 historical CPC and the WORST qualification rate of any heating cluster - 8 qualified from 20 paid leads (40%). An ENABLED Gas Boiler Repair campaign already exists at $5/day; expand that rather than build a duplicate."},
    {"cluster": "Oil Furnace", "capability": "VERIFIED (two dedicated pages)",
     "planner_demand_10city": 30, "planner_competition": "UNSPECIFIED", "planner_jan_peak": None,
     "hist_campaign": "n/a", "hist_spend": 3930.63, "hist_clicks": 53, "hist_cpc": 74.16,
     "hist_conv": 8.0, "hist_cpa": 491.33,
     "wc_qualified_12mo": 0, "wc_paid_12mo": 0,
     "ticket": "HIGH", "tier": "B", "confidence": "LOW-MEDIUM",
     "why": "Genuinely differentiated (two dedicated pages) and oil is common in older Anne Arundel housing, but only ~30/mo demand and $74 historical CPC on oil terms."},
    {"cluster": "Thermostat", "capability": "HOLD - NOT VERIFIED",
     "planner_demand_10city": 80, "planner_competition": "LOW-HIGH", "planner_jan_peak": None,
     "hist_campaign": "none", "hist_spend": 0, "hist_clicks": 0, "hist_cpc": None,
     "hist_conv": 0, "hist_cpa": None, "wc_qualified_12mo": 6, "wc_paid_12mo": 2,
     "ticket": "LOW", "tier": "HOLD", "confidence": "N/A",
     "why": "No capability evidence anywhere on the Ambient website. Demand exists (80/mo) but we cannot advertise a service we cannot verify Ambient sells."},
    {"cluster": "Water Heater / Tankless", "capability": "VERIFIED (dedicated page)",
     "planner_demand_10city": None, "planner_competition": None, "planner_jan_peak": None,
     "hist_campaign": "Tankless Water Heaters (PAUSED)", "hist_spend": 12531.77,
     "hist_clicks": 268, "hist_cpc": 46.76, "hist_conv": 2.0, "hist_cpa": 6265.89,
     "wc_qualified_12mo": 4, "wc_paid_12mo": 3, "ticket": "MID-HIGH",
     "tier": "EXCLUDE", "confidence": "HIGH",
     "why": "$12,531.77 spent for TWO conversions - a $6,265.89 CPA, the worst in the account by a factor of eight. Also not an HVAC heating service. Exclude."},
    {"cluster": "Geothermal", "capability": "VERIFIED (dedicated page)",
     "planner_demand_10city": 0, "planner_competition": None, "planner_jan_peak": None,
     "hist_campaign": "Geothermal HVAC + Water Source Heat Pump", "hist_spend": 286.60,
     "hist_clicks": 7, "hist_cpc": 40.94, "hist_conv": 0.0, "hist_cpa": None,
     "wc_qualified_12mo": 2, "wc_paid_12mo": 4, "ticket": "VERY HIGH",
     "tier": "EXCLUDE", "confidence": "MEDIUM",
     "why": "Zero conversions across two historical campaigns and no meaningful local Planner volume. Not enough demand to fund a test."},
    {"cluster": "Emergency / No-Heat", "capability": "BARRED CLAIM",
     "planner_demand_10city": 20, "planner_competition": "LOW", "planner_jan_peak": None,
     "hist_campaign": "none", "hist_spend": 0, "hist_clicks": 0, "hist_cpc": None,
     "hist_conv": 0, "hist_cpa": None, "wc_qualified_12mo": 0, "wc_paid_12mo": 0,
     "ticket": "MID", "tier": "HOLD", "confidence": "N/A",
     "why": "client.yaml bars same_day_or_emergency_availability. The approved ad schedule ends at 20:00 and excludes Sunday, so a 24/7 emergency promise would be untrue."},
]

TIER_A = ["Furnace & Heating Repair", "Heat Pump & Ductless",
          "Heating Installation & Replacement"]

# ---------------------------------------------------------------- work orders
COMMON_ACCOUNT = """  account:
    # IDENTITY GATE PASSED 2026-09-16 by fresh read-only API lookup, 10/10 checks.
    # Evidence: clients/ambient-cooling-heating/snapshots/heating-identity-baseline-2026-09-16.json
    #   descriptive_name "Ambient Cooling - Live" == expected
    #   customer.id 2401959466 == expected (CHILD id, not the Green Marketing MCC)
    #   manager=false  test=false  status=ENABLED  USD  America/New_York
    #   manager 3373711342 Green Marketing ACTIVE; 2815082755 ClickCease ACTIVE
    exact_child_account_name: "Ambient Cooling - Live"
    child_customer_id: "2401959466"
    manager_customer_id: "3373711342"
"""


def work_order(slug, service, request, extra=""):
    return f"""work_order:
  client_slug: ambient-cooling-heating
  business_name: Ambient Cooling & Heating
{COMMON_ACCOUNT}  service:
    vertical: heating-cooling
    exact_primary_service: {service}
    related_services: []
  task:
    type: keyword-research
    mode: draft
    request: >-
      {request}
      READ + DRAFT ONLY. This work order confers NO write authority. No campaign, ad group,
      keyword, negative, ad, asset, budget, bid, conversion, WhatConverts, GTM or website
      change is authorized. Every future external change requires its own fingerprinted plan
      and its own explicit approval.
    date_range: >-
      CURRENT AS AT 2026-09-16. Latest fully settled day = 2026-09-15. 2026-09-16 is PARTIAL
      and is never mixed into a settled comparison. Windows used: all-time account history
      (2019-01-01 onward); last heating season 2025-10-01..2026-03-31; trailing 12 months
      2025-09-16..2026-09-15; August clean window 2026-08-01..2026-08-31;
      September 2026-09-01..2026-09-15.
  scope_approval:
    approved: false
    approved_by: ""
    reason: "Not required. heating-cooling is a core Green Marketing vertical."
  inputs:
    website_or_final_url: https://ambientcoolingandheating.com/services/heating-services/
    service_area:
      - "Severn, Maryland, United States"
      - "Severna Park, Maryland, United States"
      - "Columbia, Maryland, United States"
    daily_budget: null
    primary_conversion_goal: "unique qualified heating lead (form or call)"
    source_files:
      - clients/ambient-cooling-heating/client.yaml
      - clients/ambient-cooling-heating/work-order.yaml
    search_monthly_maximum_usd: 13000
    search_monthly_maximum_basis: "daily budget x 30.4, never x 30"
    max_combined_daily_usd: 427.63
    heating_is_funded_by_reallocation_not_addition: true
    live_geo_targets: 75
    live_geo_composition: "28 City + 5 Neighborhood + 42 Postal Code, zero containment overlap"
    launch_authorized: false
{extra}  approval_owner: Green Marketing
"""


def main():
    written = []

    # composite research manifest
    p = WO / "work-order-heating-research-manifest.yaml"
    p.write_text(work_order(
        "heating-research", "Heating Repair",
        "COMPOSITE READ-ONLY RESEARCH MANIFEST covering the full 33-service heating "
        "candidate universe: capability verification against the official website, "
        "all-time historical Google Ads mining across 15 heating campaigns, WhatConverts "
        "heating-intent lead classification, local Keyword Planner demand and seasonality, "
        "candidate normalization, profitability scoring, and Tier A/B/Hold selection.",
        extra="""    manifest_role: >-
      This is the COMPOSITE research manifest. Agency policy allows one exact primary
      service per work order, so the primary service here is set to the anchor Tier A
      service (Heating Repair). Service-specific work orders exist alongside it for each
      canonical Tier A cluster. This manifest exists to record the research scope across
      all 33 candidates; it is not an authorization to advertise all of them.
    candidate_universe_count: 33
    tier_a_clusters: 3
    tier_b_clusters: 3
    hold_or_excluded: 5
"""), encoding="utf-8")
    written.append(p)

    for svc, slug, req in (
        ("Heating Repair", "heating-repair",
         "Tier A canonical cluster 'Furnace & Heating Repair'. Research, keyword package, "
         "negative and routing plan, landing-page content draft and two RSA drafts."),
        ("Heat Pump Installation", "heat-pump",
         "Tier A canonical cluster 'Heat Pump & Ductless'. Covers heat pump repair, "
         "installation and replacement plus ductless mini-split installation, which "
         "Ambient's own heat-pump page names as a heat-pump type."),
        ("Heating Installation", "heating-installation",
         "Tier A canonical cluster 'Heating Installation & Replacement'. Covers furnace "
         "installation and replacement and whole heating-system installation and "
         "replacement, including the verified oil furnace installation and oil "
         "replacement services."),
    ):
        p = WO / f"work-order-{slug}.yaml"
        p.write_text(work_order(slug, svc, req), encoding="utf-8")
        written.append(p)

    # normalization CSV
    p = EXPORTS / f"heating-candidate-normalization-{STAMP}.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["original_service", "canonical_cluster", "user_intent",
                    "equipment_type", "action_intent", "own_ad_group", "own_landing_page",
                    "reason"])
        for r in NORM:
            w.writerow(r)
    written.append(p)

    # scorecard CSV
    p = EXPORTS / f"heating-profitability-scorecard-{STAMP}.csv"
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(SCORE[0].keys()))
        w.writeheader()
        for r in SCORE:
            w.writerow(r)
    written.append(p)

    # ------------------------------------------------------------ future plans
    plans = {}

    plans["AMB-0916-HEAT-STRATEGY-1"] = {
        "plan_name": "AMB-0916-HEAT-STRATEGY-1",
        "approval_class": "strategy-approval (no external write)",
        "customer_id": CID, "exact_account_name": EXACT_NAME,
        "exact_service": "Heating Repair (anchor of a 3-ad-group Heating Services campaign)",
        "summary": ("Approve the heating portfolio selection: 3 Tier A ad groups inside one "
                    "new Heating Services Search campaign, funded entirely by reallocation "
                    "inside the existing $13,000/month cap."),
        "tier_a": TIER_A,
        "tier_b": ["Heating Maintenance", "Boiler (expand the EXISTING campaign, do not duplicate)",
                   "Oil Furnace"],
        "hold_or_excluded": {
            "HOLD - capability not verified": ["Thermostat repair", "Thermostat replacement",
                                               "Smart thermostat installation",
                                               "Electric furnace repair"],
            "HOLD - barred claim": ["Emergency heating repair"],
            "EXCLUDE - proven uneconomic": ["Water heater / tankless ($6,265.89 CPA)",
                                            "Geothermal (0 conversions)"]},
        "requested_campaign_label": "HEATING SERVICES",
        "proposed_exact_campaign_name": "Search | NonBrand | Heating Services | Central MD | BOFU | 2026-10",
        "naming_reason": ("Matches the existing five-campaign convention "
                          "'Search | NonBrand | <Service> | Central MD | BOFU | <YYYY-MM>', "
                          "which keeps reporting filters and the repository's plan lineage "
                          "consistent."),
        "campaign_settings": {
            "channel": "SEARCH only", "google_search": True, "search_partners": False,
            "display_expansion": False, "ai_max": False, "dsa": False,
            "final_url_expansion": False, "automatically_created_assets": False,
            "text_customization": False, "broad_match": False,
            "match_types": ["PHRASE", "EXACT"],
            "location_option": "PRESENCE",
            "locations": "inherit the verified 75 Central MD targets (28 City, 5 Neighborhood, 42 Postal Code, zero containment)",
            "schedule": "Mon-Fri 08:00-20:00 + Sat 08:00-13:00 America/New_York, no Sunday - identical to the five live campaigns",
            "no_overnight": "Ambient cannot answer and qualify overnight leads; the approved schedule already excludes it",
            "bidding": "Maximize Clicks (TARGET_SPEND) with a per-ad-group-informed CPC ceiling",
            "cpc_ceiling_rationale": ("NOT the arbitrary $25/$30 used on the cooling campaigns. "
                                      "Derived from actual auction history: Heating Repair ran at "
                                      "$18.76 average CPC and Heating Installation at $16.47 over "
                                      "1,962 combined clicks. Planner shows LOW competition on "
                                      "nearly every heating term. Proposed ceiling $45.00 - roughly "
                                      "2.4x the historical average CPC, leaving headroom for the "
                                      "December-January seasonal premium (historical Nov-Jan CPC "
                                      "reached $78-$90) without reopening uncapped bidding."),
            "proposed_cpc_ceiling_usd": 45.00},
        "ad_groups": [
            {"name": "SKAG | Furnace & Heating Repair", "canonical": "Furnace & Heating Repair",
             "final_url": "https://offer.ambientcoolingandheating.com/furnace-heating-repair/",
             "h1": "Furnace & Heating Repair in Central Maryland",
             "budget_share_pct": 45, "launch_order": 1,
             "keywords_phrase": ["furnace repair", "furnace repair near me",
                                 "heating repair near me", "heating system repair",
                                 "gas furnace repair", "furnace not working",
                                 "heating repair", "no heat repair"],
             "keywords_exact": ["furnace repair", "furnace repair near me",
                                "heating repair near me", "heating repair"],
             "expected_cpc_usd": [16, 25, 40], "confidence": "HIGH"},
            {"name": "SKAG | Heat Pump & Ductless", "canonical": "Heat Pump & Ductless",
             "final_url": "https://offer.ambientcoolingandheating.com/heat-pump-mini-split/",
             "h1": "Heat Pump & Ductless Mini-Split Service in Central Maryland",
             "budget_share_pct": 35, "launch_order": 2,
             "keywords_phrase": ["heat pump repair", "heat pump repair near me",
                                 "heat pump installation", "heat pump replacement",
                                 "ductless mini split installation", "mini split installation",
                                 "ductless heating installation"],
             "keywords_exact": ["heat pump repair", "heat pump installation",
                                "mini split installation", "ductless mini split installation"],
             "expected_cpc_usd": [13, 25, 45], "confidence": "HIGH"},
            {"name": "SKAG | Heating Installation & Replacement",
             "canonical": "Heating Installation & Replacement",
             "final_url": "https://offer.ambientcoolingandheating.com/furnace-installation-replacement/",
             "h1": "Furnace Installation & Replacement in Central Maryland",
             "budget_share_pct": 20, "launch_order": 3,
             "keywords_phrase": ["furnace installation", "furnace installation near me",
                                 "furnace replacement", "new furnace installation",
                                 "heating system installation", "heating system replacement",
                                 "oil furnace installation"],
             "keywords_exact": ["furnace installation", "furnace replacement",
                                "furnace installation near me", "heating system replacement"],
             "expected_cpc_usd": [15, 22, 40], "confidence": "MEDIUM-HIGH"}],
        "negatives_and_routing": {
            "principle": ("Every negative reviewed individually. NO one-word BROAD negatives. "
                          "near me / quote / price / pricing / cost / best / hire / local / "
                          "emergency are NEVER auto-negatived."),
            "campaign_level_phrase_negatives": [
                "air conditioning repair", "ac repair", "ac installation",
                "water heater", "tankless water heater", "hot water heater",
                "geothermal", "pool heater", "hvac school", "hvac training",
                "hvac jobs", "hvac salary", "furnace filter", "furnace parts",
                "diy furnace", "used furnace", "furnace manual"],
            "cross_negatives_into_existing_campaigns": [
                {"campaign": "HVAC Repair 24132507750", "add_phrase_negative": "furnace repair",
                 "reason": "route furnace-repair intent to the new heating ad group"},
                {"campaign": "HVAC Repair 24132507750", "add_phrase_negative": "heating repair",
                 "reason": "same"},
                {"campaign": "HVAC Installation 24132507747",
                 "add_phrase_negative": "furnace installation",
                 "reason": "route furnace-install intent to the heating campaign"},
                {"campaign": "HVAC Installation 24132507747",
                 "add_phrase_negative": "heat pump installation",
                 "reason": "route heat-pump intent to the heating campaign"},
                {"campaign": "HVAC Replacement 24132507753",
                 "add_phrase_negative": "furnace replacement",
                 "reason": "route furnace-replacement intent to the heating campaign"}],
            "cross_negatives_into_heating": [
                {"add_phrase_negative": "boiler",
                 "reason": "the ENABLED Gas Boiler Repair campaign 24132507744 already owns boiler intent"}],
            "explicitly_not_negatived": ["near me", "quote", "price", "pricing", "cost",
                                         "best", "hire", "local", "emergency", "company",
                                         "companies", "contractor", "contractors"]},
        "gas_boiler_audit": {
            "existing_campaign": "24132507744 Search | NonBrand | Gas Boiler Repair | Central MD | BOFU | 2026-08",
            "status": "ENABLED, $5.00/day, $25 ceiling, 1 ad group, 2 keywords, 2 ENABLED+APPROVED ads, 1,131 campaign negatives",
            "all_time": "39 impressions, 0 clicks, $0.00 spend, 0 conversions",
            "verdict": "DO NOT DUPLICATE. Boiler intent stays with this campaign. Tier B expansion would raise its budget, not create a second boiler structure."},
        "external_writes_authorized": 0,
        "risk": "NONE - this is a strategy approval with no external write.",
        "next_stage": "landing-page content approval, then create-paused plan, then budget reallocation, then readback, then enablement - each separately fingerprinted.",
    }

    plans["AMB-0916-HEAT-BUDGET-1"] = {
        "plan_name": "AMB-0916-HEAT-BUDGET-1",
        "approval_class": "budget-reallocation",
        "customer_id": CID, "exact_account_name": EXACT_NAME,
        "summary": ("Fund the Heating Services test entirely by reallocation inside the "
                    "$13,000/month cap. Combined daily stays at $421.55. 6 operations."),
        "hard_cap": {"monthly_usd": 13000.0, "max_combined_daily_usd": 427.63,
                     "basis": "daily x 30.4, never x 30"},
        "view_1_current_pre_heating": {
            "AC Repair 24132507741": 141.45, "HVAC Repair 24132507750": 78.95,
            "HVAC Installation 24132507747": 176.15, "HVAC Replacement 24132507753": 20.00,
            "Gas Boiler Repair 24132507744": 5.00, "Heating Services (new)": 0.00,
            "total_daily": 421.55, "total_monthly_30_4": 12815.12,
            "headroom_monthly": 184.88},
        "view_2_initial_heating_test_october": {
            "changes": [
                {"campaign": "AC Repair 24132507741", "from": 141.45, "to": 70.00,
                 "delta": -71.45,
                 "reason": "August proved AC Repair returns 0.51:1 on revenue alone - $2,550.59 spent for ~$1,298 of pipeline. It is the largest budget line and the weakest economics. Cooling demand also falls from October.",
                 "risk": "MEDIUM - reduces the campaign that produced 3 of 7 August qualified leads, though they were the lowest-value ones.",
                 "stop_loss": "restore if AC Repair qualified leads fall to zero for 14 settled days while impression share holds"},
                {"campaign": "HVAC Repair 24132507750", "from": 78.95, "to": 40.00,
                 "delta": -38.95,
                 "reason": "$1,665.16 spent in August with ZERO qualified leads traceable to it. Keywords sit at Quality Score 2 with below-average landing-page experience.",
                 "risk": "LOW", "stop_loss": "n/a - it is not currently producing"},
                {"campaign": "HVAC Installation 24132507747", "from": 176.15, "to": 176.15,
                 "delta": 0.0,
                 "reason": "UNCHANGED. Best performer - carries the commercial ad group and produced the highest-value August leads.",
                 "risk": "NONE", "stop_loss": "n/a"},
                {"campaign": "HVAC Replacement 24132507753", "from": 20.00, "to": 20.00,
                 "delta": 0.0, "reason": "UNCHANGED. High ticket, minimal spend.",
                 "risk": "NONE", "stop_loss": "n/a"},
                {"campaign": "Gas Boiler Repair 24132507744", "from": 5.00, "to": 5.00,
                 "delta": 0.0,
                 "reason": "UNCHANGED. Dormant but it is the designated boiler route; do not duplicate it elsewhere.",
                 "risk": "NONE", "stop_loss": "n/a"},
                {"campaign": "Heating Services (NEW)", "from": 0.00, "to": 110.40,
                 "delta": 110.40,
                 "reason": "Funded entirely by the two reductions above (71.45 + 38.95 = 110.40). Splits 45/35/20 across the three Tier A ad groups.",
                 "risk": "MEDIUM - a new campaign with no account history in its current form.",
                 "stop_loss": "$450 incremental spend per ad group with zero verified qualified lead"}],
            "total_daily": 421.55, "total_monthly_30_4": 12815.12,
            "within_cap": True,
            "heating_share_monthly": 3356.16},
        "view_3_colder_season_november_february": {
            "changes": [
                {"campaign": "AC Repair 24132507741", "from": 70.00, "to": 40.00, "delta": -30.00,
                 "reason": "Cooling demand troughs Nov-Feb; historical AC search volume collapses."},
                {"campaign": "HVAC Repair 24132507750", "from": 40.00, "to": 30.00, "delta": -10.00,
                 "reason": "Continued underperformance; keep a floor for year-round HVAC repair intent."},
                {"campaign": "HVAC Installation 24132507747", "from": 176.15, "to": 130.00,
                 "delta": -46.15,
                 "reason": "Retains the commercial ad group and year-round install intent at a reduced winter level."},
                {"campaign": "HVAC Replacement 24132507753", "from": 20.00, "to": 20.00, "delta": 0.0,
                 "reason": "UNCHANGED."},
                {"campaign": "Gas Boiler Repair 24132507744", "from": 5.00, "to": 15.00,
                 "delta": 10.00,
                 "reason": "Tier B expansion of the EXISTING boiler campaign during peak boiler season. Not a new campaign."},
                {"campaign": "Heating Services", "from": 110.40, "to": 186.55, "delta": 76.15,
                 "reason": "Planner shows furnace repair peaking at 720/mo in January versus 110 in September - a 6.5x seasonal swing. WhatConverts heating leads peaked at 57 in December."}],
            "total_daily": 421.55, "total_monthly_30_4": 12815.12,
            "within_cap": True, "heating_share_monthly": 5671.12},
        "operation_count": 6,
        "unrelated_resource_assertion": (
            "Only campaign_budget.amount_micros changes on the named budgets. No bid, "
            "ceiling, status, network, geo, schedule, keyword, negative, ad, asset or "
            "conversion setting is touched."),
        "HARD_GATE": ("DO NOT EXECUTE until the Heating Services campaign exists paused AND "
                      "the measurement prerequisites in section 17 pass. Reallocating budget "
                      "to a campaign that does not exist would simply cut cooling for nothing."),
    }

    lines = []
    PLANS.mkdir(parents=True, exist_ok=True)
    print("=" * 78)
    for name, plan in plans.items():
        fp = approval_code(plan)
        plan["fingerprint"] = fp
        p = PLANS / f"{name}.json"
        p.write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
        written.append(p)
        n = plan.get("operation_count", 0)
        print(f"{name:30s} {fp}  ops={n}")
        lines.append(f"APPROVE {name} {fp} "
                     + (f"{n} operations FOR {CID}" if n else f"strategy FOR {CID}"))
    print("\n--- FUTURE APPROVAL LINES (do not execute now) ---")
    for l in lines:
        print(l)
    print("\n--- FILES WRITTEN ---")
    for p in written:
        print(" ", p.relative_to(ROOT))
    print(f"\nTOTAL LOCAL FILES: {len(written)}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    sys.exit(main())
