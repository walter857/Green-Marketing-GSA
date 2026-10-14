#!/usr/bin/env python3
"""Build the 2026-09-09 CORRECTION packages. Supersedes five of the six prior fingerprints."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

state = json.load(open(EVID / "2026-09-09b-state-and-drift.json", encoding="utf-8"))
groups = json.load(open(EVID / "2026-09-09b-removal-groups.json", encoding="utf-8"))
bud = json.load(open(EVID / "2026-09-09b-budget-analysis.json", encoding="utf-8"))

STAMP = "2026-09-09b"
NOW = datetime.datetime.now(TZ).isoformat()
TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "AC Repair",
          "related_services": ["HVAC Repair", "HVAC Installation", "HVAC Replacement",
                               "Gas Boiler Repair"]}
plans = {}


def finalise(name, klass, summary, ops, notes):
    p = {"plan_name": name, "approval_class": klass, "generated_local": NOW,
         "supersedes": notes.get("supersedes"), "target": TARGET, "summary": summary,
         "object_count": len(ops), "partial_failure": False, "atomic": True,
         "operations": ops, "notes": notes}
    p["fingerprint"] = approval_code({"target": TARGET, "plan": name, "operations": ops})
    plans[name] = p
    print(f"\n=== {name} [{klass}] ops={len(ops)} fingerprint={p['fingerprint']} ===")
    print(f"    {summary}")
    return p


# ---------------------------------------------------------------- 1. BUDGET
DAYS = 30.4
MAXM = 13000.0
HARD = MAXM / DAYS
CUR = {"15787409435": ("AC Repair", 141450000), "15787409438": ("Gas Boiler Repair", 42760000),
       "15787409441": ("HVAC Installation", 176150000),
       "15787409444": ("HVAC Repair", 78950000),
       "15787409447": ("HVAC Replacement", 26320000)}
NEW = {"15787409438": 5000000, "15787409447": 20000000}
prop = {k: NEW.get(k, v[1]) for k, v in CUR.items()}
tot_before = sum(v[1] for v in CUR.values()) / 1e6
tot_after = sum(prop.values()) / 1e6
ops = []
for bid, micros in NEW.items():
    label, cur = CUR[bid]
    why = {
        "15787409438": ("Zero clicks since launch on 2026-08-14 (34 impressions all time). "
                        "Keyword Planner across the live 10-city Maryland sample returns 20 "
                        "monthly searches for the strongest boiler term and no top-of-page bid "
                        "estimate at all. The /gas-boiler-repair/ landing page still carries "
                        "the heading 'Your HVAC Replacement in 3 Simple Steps', so the campaign "
                        "is service-gated regardless of budget. $5.00/day keeps it measurable "
                        "without reserving unspendable capacity."),
        "15787409447": ("5 clicks and 0 primary conversions since launch. Quality Score 2 with "
                        "BELOW_AVERAGE landing-page experience. Search lost impression share to "
                        "BUDGET is 0.00% in every window measured, so this budget has never "
                        "been the constraint and reducing it cannot cost delivery."),
    }[bid]
    ops.append({
        "operation": "UPDATE_CAMPAIGN_BUDGET", "resource": "campaign_budget",
        "resource_id": bid, "resource_name": f"customers/{CID}/campaignBudgets/{bid}",
        "campaign": label,
        "current_state": f"amount_micros = {cur} (${cur/1e6:.2f}/day)",
        "proposed_state": f"amount_micros = {micros} (${micros/1e6:.2f}/day)",
        "field_mask": ["amount_micros"], "reason": why,
        "rollback": f"set amount_micros back to {cur}",
        "risk": "LOW - both campaigns have 0.00% Search lost IS (budget) in every window",
        "unrelated_resource_assertion":
            "budgets 15787409435, 15787409441 and 15787409444 must be unchanged; combined "
            f"daily total must read ${tot_after:.2f}"})
finalise("AMB-0909B-BUD-1", "reversible-budget-change",
         f"Reduce Gas Boiler Repair to $5.00/day and HVAC Replacement to $20.00/day. Combined "
         f"daily total ${tot_before:.2f} -> ${tot_after:.2f}, which is ${tot_after*DAYS:,.2f} "
         f"over a 30.4-day month against the ${MAXM:,.0f} maximum.", ops,
         {"supersedes": "AMB-0909-BUD-1 (D448BFDE4650) - SUPERSEDED, DO_NOT_EXECUTE",
          "corrected_arithmetic": {
              "denominator": "30.4 (Google's average-month multiplier), NOT 30",
              "hard_daily_max": round(HARD, 7),
              "prior_package_daily": 433.33,
              "prior_package_x30_4": round(433.33 * DAYS, 2),
              "prior_package_overrun": round(433.33 * DAYS - MAXM, 2),
              "prior_package_compliant": False,
              "why_prior_was_wrong": "AMB-0909-BUD-1 multiplied $433.33 by 30 and reported "
                                     "$12,999.90 as compliant. Google applies 30.4, giving "
                                     "$13,173.23 - a $173.23 breach. The prior compliance "
                                     "claim was arithmetically wrong and is retracted."},
          "future_uninterrupted_month": {
              "proposed_daily_total": round(tot_after, 2),
              "x30_4": round(tot_after * DAYS, 2),
              "headroom_vs_13000": round(MAXM - tot_after * DAYS, 2),
              "compliant": tot_after * DAYS <= MAXM},
          "current_month_september": {
              "september_budget_changes_found": 0,
              "billed_basis": "served cost; Google Ads exposes no per-month billed figure "
                              "through this API surface without monthly invoicing",
              "served_through_2026_09_09": 1319.49,
              "change_day_uses_highest_budget_in_force": round(tot_before, 2),
              "remaining_calendar_days_after_change_day": 20,
              "september_maximum_if_executed_2026_09_10":
                  round(1319.49 + tot_before + tot_after * 20, 2),
              "headroom_vs_13000":
                  round(MAXM - (1319.49 + tot_before + tot_after * 20), 2),
              "method": "billed-to-date + highest budget in force on the change day + new "
                        "daily total x remaining CALENDAR days. Remaining scheduled "
                        "advertising days are deliberately NOT used."},
          "hvac_installation_budget_deliberately_unchanged":
              "AMB-0909-BUD-1 raised HVAC Installation on a 53.16% Search lost IS (budget) "
              "figure measured across 2026-08-14..09-08. That window is contaminated by the "
              "'hvac installers' keyword, live 08-14..08-28. On the CLEAN post-swap window "
              "2026-08-29..09-03 the same metric is 4.38%, with 35.62% lost to RANK instead. "
              "The budget increase is not supported and is withdrawn.",
          "peak_observed_daily_spend": 448.36,
          "two_x_single_day_ceiling_after": round(tot_after * 2, 2)})

# ------------------------------------------------- 2. CPC, INSTALLATION ONLY
camps = state["live"]["campaigns"]
inst = "24132507747"
cur_ceiling = camps[inst]["ceiling_micros"]
ops = [{
    "operation": "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING", "resource": "campaign",
    "resource_id": inst, "resource_name": NAME[inst], "campaign_name": camps[inst]["name"],
    "current_state": f"target_spend.cpc_bid_ceiling_micros = {cur_ceiling} "
                     f"(${cur_ceiling/1e6:.2f})",
    "proposed_state": "target_spend.cpc_bid_ceiling_micros = 65000000 ($65.00)",
    "field_mask": ["target_spend.cpc_bid_ceiling_micros"],
    "reason": ("All three of this campaign's primary conversions came from clicks priced "
               "between $50.00 and $62.13. The live $30 ceiling admits 76% of its historical "
               "click volume while excluding every one of those converting clicks. $65 covers "
               "the highest observed converting CPC with headroom and stops the ceiling "
               "binding."),
    "modelled_effect": ("Descriptive sensitivity test on 62 visible clicks, NOT an auction "
                        "forecast: at $30, 47 clicks and 0 of 3 conversions survive; at $65, "
                        "62 clicks and 3 of 3 survive."),
    "rollback": f"set target_spend.cpc_bid_ceiling_micros back to {cur_ceiling}",
    "risk": "MEDIUM - restores paid delivery and therefore spend",
    "unrelated_resource_assertion":
        "bidding_strategy_type stays TARGET_SPEND; AC Repair and HVAC Repair ceilings must "
        "remain 25000000; budgets, networks, geo, schedules, keywords and negatives unchanged"}]
finalise("AMB-0909B-CPC-INST-1", "reversible-setting-change",
         "HVAC Installation ONLY: raise the Maximize Clicks CPC bid ceiling from $30 to $65. "
         "No other campaign is touched.", ops,
         {"supersedes": "AMB-0909-CPC-1 (46C39C6B7091) - SUPERSEDED, DO_NOT_EXECUTE "
                        "(it bundled HVAC Repair on a recommendation now withdrawn)",
          "live_keyword_verified": {
              "campaign": "HVAC Installation", "ad_group": "202339087634",
              "keywords": ["hvac installers near me [PHRASE] crit 295495761070 ELIGIBLE",
                           "hvac installers near me [EXACT] crit 315030681341 ELIGIBLE"],
              "removed_keyword_hvac_installers_still_live": False},
          "bid_adjustment_audit": {
              "campaign_criterion_modifiers_not_equal_1": 5,
              "all_five_are": "DEVICE / TABLET / bid_modifier x0.0 (tablet exclusion)",
              "ad_group_bid_modifier_rows_not_equal_1": 0,
              "audience_or_demographic_criteria": 0,
              "highest_modifier_found": 0.0,
              "conclusion": "No modifier above x1.0 exists anywhere on the five campaigns. "
                            "Nothing can push the effective bid above the ceiling. A $65 "
                            "ceiling means $65."},
          "economics_labelling": {
              "post_swap_window": "2026-08-29..2026-09-03",
              "figure": 141.87,
              "label": "RAW CPA - NOT CPQL, and NOT a qualified-lead cost",
              "sample": "3 raw primary conversions from 9 clicks. This is a small sample and "
                        "no confidence claim is attached to it.",
              "min_qualification_rate_to_meet_280_cpql_pct": 50.7,
              "confidence": "The delivery-restoration case is strong. The ECONOMICS are NOT "
                            "high-confidence: qualified-lead outcomes are unavailable because "
                            "WHATCONVERTS_API_TOKEN is empty."},
          "privacy_hidden_traffic": {
              "campaign_clicks": 112, "visible_in_search_terms": 62, "hidden": 50,
              "hidden_primary_conversions": 0,
              "note": "44.6% of this campaign's clicks are privacy-hidden, but 0 of its 3 "
                      "primary conversions are, so the visible-click model sees every "
                      "converting click."}})

# ------------------------------------------------- 3. NEGATIVES, PACKAGE A
A = groups["A_high_confidence"]
ops = []
for r in sorted(A, key=lambda r: (r["package"], r["negative_text"], r["campaign"])):
    if r["package"] == "RM-1":
        ops.append({
            "operation": "REMOVE_CAMPAIGN_NEGATIVE_KEYWORD", "resource": "campaign_criterion",
            "resource_name": r["resource_name"], "campaign_id": r["campaign_id"],
            "campaign": r["campaign"], "criterion_id": r["criterion_id"],
            "match_type": r["match_type"], "negative_text": r["negative_text"],
            "current_state": f"negative KEYWORD [{r['match_type']}] {r['negative_text']!r} ENABLED",
            "proposed_state": "REMOVED",
            "reason": {
                "savage": "Savage, Maryland (geoTargetConstants/1018704) is one of the 75 live "
                          "location targets on all five campaigns. This PHRASE negative blocked "
                          "300 of 300 service-by-place probes for that city.",
                "free": "Blocks 'hvac free estimate near me'. Free estimates are an approved, "
                        "verified Ambient proposition, and Green Marketing rules forbid "
                        "negativing value-intent words.",
                "licensed": "Blocks 'licensed hvac contractor near me'. Licensed and insured is "
                            "an approved, verified Ambient claim.",
            }[r["negative_text"].lower()],
            "blocked_protected_probes": r["blocked_protected_probes"],
            "primary_conv_at_risk_if_left": r["primary_conv_at_risk"],
            "rollback": f"re-create campaign negative {r['negative_text']!r} "
                        f"[{r['match_type']}] on campaign {r['campaign_id']}",
            "risk": "LOW - each restores a verified Ambient proposition or a targeted city",
            "unrelated_resource_assertion":
                "only this one campaign_criterion is removed"})
    else:
        ops.append({
            "operation": "REMOVE_SHARED_LIST_NEGATIVE", "resource": "shared_criterion",
            "shared_set_id": "11252984411",
            "shared_criterion_resource_name": r["resource_name"],
            "criterion_id": r["criterion_id"], "match_type": r["match_type"],
            "negative_text": r["negative_text"],
            "current_state": f"account-level negative KEYWORD [{r['match_type']}] "
                             f"{r['negative_text']!r} in shared set 11252984411",
            "proposed_state": "REMOVED from the account-level list",
            "reason": ("Ambient's live website advertises commercial work: the homepage and the "
                       "furnace-repair page both name commercial service, /services/hvac/"
                       "condominium-hvac/ is a dedicated page, and the site carries a "
                       "/category/commercial-hvac/ blog category including a Maryland BEPS "
                       "compliance article. Two commercial queries have already produced "
                       "primary conversions in this account: 'commercial ac repair near me' "
                       "and 'commercial hvac companies near me'. BROAD 'commercial' is also "
                       "named in the Green Marketing rules as a word that must not be "
                       "broad-negatived."),
            "blocked_protected_probes": r["blocked_protected_probes"],
            "blocked_historical_terms": r["blocked_historical_terms"],
            "primary_conv_at_risk_if_left": r["primary_conv_at_risk"],
            "all_conv_at_risk_if_left": r["all_conv_at_risk"],
            "rollback": "re-add 'commercial' [BROAD] to shared set 11252984411",
            "risk": "MEDIUM - account-level scope reaches all 23 non-removed campaigns, but "
                    "only the 5 ENABLED ones can serve",
            "unrelated_resource_assertion":
                "shared set 11252984411 member count must fall from 272 to 271; the other 16 "
                "shared sets untouched; still 0 shared lists attached to the five campaigns"})
finalise("AMB-0909B-NEG-A", "DESTRUCTIVE-removal",
         f"Package A, high-confidence unblock: {len(ops)} removals. PHRASE 'savage', 'free' and "
         f"'licensed' from all five campaigns, plus account-level BROAD 'commercial'.", ops,
         {"supersedes": "part of AMB-0909-NEG-RM-1 (CE289F3508A2) and AMB-0909-NEG-RM-2 "
                        "(A435FA09AC97) - both SUPERSEDED, DO_NOT_EXECUTE",
          "mixed_scope_is_deliberate":
              "This package pairs campaign-level and account-level removals in ONE atomic "
              "mutate so the two layers cannot end up half-applied.",
          "row_evidence": "reports/ambient-cooling-heating/evidence/"
                          "2026-09-09b-removal-row-evidence.csv",
          "commercial_evidence": {
              "website_pages": ["https://ambientcoolingandheating.com/",
                                "https://ambientcoolingandheating.com/services/hvac/condominium-hvac/",
                                "https://ambientcoolingandheating.com/category/commercial-hvac/"],
              "converting_terms_blocked": ["commercial ac repair near me",
                                           "commercial hvac companies near me",
                                           "commercial furnace repair"],
              "primary_conversions_at_risk": 3.83},
          "what_is_NOT_in_this_package":
              "The 11 manufacturer tokens, the 6 supply-house EXACT negatives, the additional-"
              "service terms and the dealer/installer terms are all held. See packages B, C "
              "and D in the correction report, none of which has executable operations."})

# ------------------------------------------------- 4. VERIFIED COMPETITORS
INSTALL = "24132507747"
ARUNDEL_EV = {
    "entity": "Arundel Cooling & Heating Co., Inc.",
    "address": "707 Nursery Rd, Linthicum Heights, MD 21090",
    "note": "Linthicum Heights is one of Ambient's 75 live location targets. Operating since "
            "1971, now part of Service Experts. Residential and light commercial HVAC across "
            "Baltimore, Columbia, Annapolis, Ellicott City and Bowie - direct footprint "
            "overlap. Also a Carrier dealer.",
    "sources": ["https://www.bbb.org/us/md/linthicum/profile/heating-and-air-conditioning/"
                "arundel-cooling-heating-co-inc-0011-563",
                "https://www.yelp.com/biz/arundel-cooling-and-heating-linthicum-heights-2",
                "https://www.carrier.com/us/en/residential/dealers/md/linthicum-heights/"
                "707-nursery-rd-3274-loc"],
    "match_choice": "EXACT, not PHRASE and never BROAD. Local preflight proved that PHRASE "
                    "'arundel cooling and heating' also blocks 'anne arundel cooling and "
                    "heating', which produced a primary phone-call conversion in the legacy "
                    "Heating Maintenance campaign, and sits one word away from 'hvac anne "
                    "arundel county'. Anne Arundel County is Ambient's core service area. "
                    "EXACT on the two unambiguous brand queries leaves both county queries "
                    "free.",
    "deliberately_not_blocked": [
        "anne arundel cooling and heating - 1 primary conversion (Calls from ads)",
        "hvac anne arundel county - county intent",
        "arundel cooling and heating - too close to the county queries; 6 impressions, "
        "0 clicks, $0.00, not worth the risk"]}
VERIFIED = [
    ("EXACT", "arundel cooling and heating reviews",
     dict(ARUNDEL_EV,
          observed={"rows": 2, "impressions": 8, "clicks": 1, "cost": 20.44,
                    "conversions": 0.0,
                    "terms": ["arundel cooling and heating reviews"]},
          why_this_one="Unambiguous brand-research query and the only Arundel term that took "
                       "a click. It carries all $20.44 of the measured Arundel waste.")),
    ("EXACT", "arundel heating and cooling maryland",
     dict(ARUNDEL_EV,
          observed={"rows": 1, "impressions": 1, "clicks": 0, "cost": 0.0, "conversions": 0.0,
                    "terms": ["arundel heating and cooling maryland"]},
          why_this_one="Unambiguous brand-plus-state query. Zero cost so far, but a clear "
                       "competitor-brand pattern and EXACT carries no collision risk.")),
    ("PHRASE", "maryland mechanical heating",
     {"entity": "Maryland Mechanical Heating & Cooling LLC",
      "address": "Maryland; HVACR licence #22169; marylandhvacs.com; founded 2023",
      "note": "A separate company, Maryland Mechanical Services LLC (mmshvacllc.com), also "
              "trades in MD/VA/DC. The PHRASE covers the observed brand query for both.",
      "sources": ["https://marylandhvacs.com/", "https://mmshvacllc.com/",
                  "https://www.labor.maryland.gov/license/hvacr/"],
      "observed": {"rows": 1, "impressions": 4, "clicks": 1, "cost": 50.17, "conversions": 0.0,
                   "terms": ["maryland mechanical heating & cooling"]},
      "match_choice": "PHRASE on the three-word brand fragment. The individual words maryland, "
                      "mechanical and heating are all left usable."}),
]
ops = []
for mt, txt, ev in VERIFIED:
    ops.append({
        "operation": "ADD_CAMPAIGN_NEGATIVE_KEYWORD", "resource": "campaign_criterion",
        "resource_id": INSTALL, "campaign_id": INSTALL, "campaign": NAME[INSTALL],
        "match_type": mt, "negative_text": txt,
        "current_state": "not present at campaign, ad group or account level",
        "proposed_state": f"negative KEYWORD [{mt}] {txt!r} ENABLED",
        "reason": f"Verified competing HVAC contractor: {ev['entity']}. {ev['note']}",
        "entity_verification": ev,
        "word_count": len(txt.split()), "char_count": len(txt),
        "conflict_tests": {
            "active_positive_keywords": "clear - the only live positives are "
                                        "'hvac installers near me' PHRASE and EXACT",
            "converting_terms_all_time_account_wide": "clear - 0 of 304 blocked",
            "bofu_probes": "clear - 0 of 67 blocked",
            "service_area": "clear - blocks none of the 80 live Maryland place tokens, none "
                            "of the 67 BOFU probes and none of the 304 account-wide "
                            "converting terms, including 'anne arundel cooling and heating'",
            "manufacturers": "clear - contains no manufacturer token"},
        "rollback": f"remove the campaign negative {txt!r} [{mt}] from {INSTALL}",
        "risk": "LOW",
        "unrelated_resource_assertion":
            "HVAC Installation ENABLED campaign negatives must rise from 1435 to 1437 "
            "(or from 1420 to 1422 if AMB-0909B-NEG-A ran first); no other campaign changes"})
finalise("AMB-0909B-COMP-1", "reversible-addition",
         f"Verified competitors only: {len(ops)} negatives on HVAC Installation - two EXACT "
         f"for Arundel Cooling & Heating brand queries and one PHRASE for Maryland "
         f"Mechanical Heating & Cooling.", ops,
         {"supersedes": "AMB-0909-NEG-ADD-1 (23BE8FF0F24C) - SUPERSEDED, DO_NOT_EXECUTE",
          "dropped_from_the_prior_package": {
              '"sq ft house"': "WITHDRAWN. Square-footage sizing queries are legitimate "
                               "installation research from prospective buyers.",
              '[how much is hvac system]': "WITHDRAWN. A price question is buyer research, not "
                                           "an irrelevant query.",
              '"all about air"': "NOT ADDED. Could not be verified as a Maryland HVAC "
                                 "contractor. 4 impressions, 0 clicks, $0.00.",
              '"home comfort hvac"': "NOT ADDED. No uniquely identifiable 'Home Comfort HVAC' "
                                     "entity in Maryland; several unrelated 'Comfort'-named "
                                     "contractors exist and 'home comfort' is generic trade "
                                     "language. 3 impressions, 0 clicks, $0.00."},
          "no_broad_negatives": "No operation uses BROAD. No negative is created from home, "
                                "comfort, maryland, mechanical, heating, air or cooling.",
          "preflight_caught": "The first draft used PHRASE 'arundel cooling and heating'. "
                              "Local preflight proved it blocks 'anne arundel cooling and "
                              "heating', a term that produced a primary phone-call "
                              "conversion. The package was narrowed to EXACT before any "
                              "API quota was spent."})

# ------------------------------------------------- write
out = TOPPLANS / f"AMBIENT-{STAMP}-packages.json"
out.write_text(json.dumps(plans, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {out.relative_to(ROOT)}")
for name, p in plans.items():
    ind = CLIENT_DIR / "plans" / f"{name}.json"
    ind.write_text(json.dumps(p, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {ind.relative_to(ROOT)}")

print("\n=== NEW FINGERPRINT MANIFEST ===")
for name, p in plans.items():
    print(f"  {name:<24} {p['approval_class']:<26} ops={p['object_count']:<4} "
          f"{p['fingerprint']}")
print(f"\n  TOTAL NEW OPERATIONS: {sum(p['object_count'] for p in plans.values())}")
