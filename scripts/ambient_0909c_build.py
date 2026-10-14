#!/usr/bin/env python3
"""Build the 2026-09-09 THIRD-PASS packages."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

state = json.load(open(EVID / "2026-09-09b-state-and-drift.json", encoding="utf-8"))
neg = json.load(open(EVID / "2026-09-09c-negative-evidence.json", encoding="utf-8"))
cpa = json.load(open(EVID / "2026-09-09c-cpa-and-budget.json", encoding="utf-8"))
conv = json.load(open(EVID / "2026-09-09c-conversion-reconciliation.json", encoding="utf-8"))

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


DAYS, MAXM = 30.4, 13000.0
camps = state["live"]["campaigns"]
negs = state["live"]["campaign_negatives"]
acct = state["live"]["account_level"]

# ---------------------------------------------------------------- BUDGET
CUR = {"15787409435": ("AC Repair", 141450000), "15787409438": ("Gas Boiler Repair", 42760000),
       "15787409441": ("HVAC Installation", 176150000),
       "15787409444": ("HVAC Repair", 78950000),
       "15787409447": ("HVAC Replacement", 26320000)}
NEW = {"15787409438": 5000000, "15787409447": 20000000}
tot_after = sum(NEW.get(k, v[1]) for k, v in CUR.items()) / 1e6
pc = cpa["per_campaign_budget"]
ops = []
for bid, micros in NEW.items():
    label, cur = CUR[bid]
    j = cpa["cut_justification"][label]
    ops.append({
        "operation": "UPDATE_CAMPAIGN_BUDGET", "resource": "campaign_budget",
        "resource_id": bid, "resource_name": f"customers/{CID}/campaignBudgets/{bid}",
        "campaign": label,
        "current_state": f"amount_micros = {cur} (${cur/1e6:.2f}/day)",
        "proposed_state": f"amount_micros = {micros} (${micros/1e6:.2f}/day)",
        "field_mask": ["amount_micros"],
        "reason": (f"Fresh data 2026-08-14..2026-09-08: {j['impressions']} impressions, "
                   f"{j['clicks']} clicks, ${j['cost']:.2f}, {j['conversions']:.0f} primary "
                   f"conversions. Search lost impression share to BUDGET is "
                   f"{j['lost_is_budget_pct']:.2f}% and to RANK is {j['lost_is_rank_pct']:.2f}%. "
                   f"September spend to the preflight read is ${j['september_spend']:.2f}. "
                   f"Budget has never been this campaign's constraint, so the reduction "
                   f"cannot cost delivery."),
        "per_campaign_limits": pc[label],
        "rollback": f"see the rollback envelope in notes - a blind restore to {cur} is NOT "
                    f"permitted",
        "risk": "LOW",
        "unrelated_resource_assertion":
            "budgets 15787409435, 15787409441 and 15787409444 must be unchanged"})
finalise("AMB-0909C-BUD-1", "reversible-budget-change",
         f"Gas Boiler Repair $42.76 -> $5.00 and HVAC Replacement $26.32 -> $20.00. Combined "
         f"daily ${sum(v[1] for v in CUR.values())/1e6:.2f} -> ${tot_after:.2f}; steady-state "
         f"30.4-day exposure ${tot_after*DAYS:,.2f} against the ${MAXM:,.0f} maximum.", ops,
         {"supersedes": "AMB-0909B-BUD-1 (752BF95EBD7C) - SUPERSEDED, DO_NOT_EXECUTE",
          "per_campaign_limits": pc,
          "combined": cpa["budget_totals"],
          "hard_daily_max": round(MAXM / DAYS, 7),
          "method_correction":
              "The prior package computed a September maximum as account spend-to-date plus a "
              "COMBINED budget formula. That is wrong: each campaign carries its own monthly "
              "limit. This package sums PER-CAMPAIGN maxima instead. Only Gas Boiler Repair and "
              "HVAC Replacement change; AC Repair, HVAC Installation and HVAC Repair keep their "
              "own unchanged campaign-level limits.",
          "future_safe_rollback": {
              "blind_restore_forbidden": True,
              "blind_restore_daily": 465.63,
              "blind_restore_x30_4": round(465.63 * DAYS, 2),
              "blind_restore_breach": round(465.63 * DAYS - MAXM, 2),
              "compliant_envelope_for_the_two_campaigns_daily":
                  cpa["rollback_envelope"]["two_campaign_compliant_envelope_daily"],
              "rule": "Gas Boiler + HVAC Replacement combined must stay at or below $31.08/day "
                      "while the other three hold $141.45 + $176.15 + $78.95 = $396.55. Any "
                      "restoration above that needs an offsetting reduction elsewhere, a fresh "
                      "cap calculation and a NEW approval fingerprint.",
              "example_compliant_partial_restore": "Gas Boiler $10.00 + HVAC Replacement $21.00 "
                                                   "= $31.00 combined, $427.55/day total, "
                                                   "$12,997.52 over 30.4 days"},
          "realistic_projection": cpa["projection"]})

# ---------------------------------------------------------------- CPC
inst = "24132507747"
cur_ceiling = camps[inst]["ceiling_micros"]
ib = cpa["installation_unique_lead_bounds"]
ips = cpa["installation_post_swap"]
ops = [{
    "operation": "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING", "resource": "campaign",
    "resource_id": inst, "resource_name": NAME[inst], "campaign_name": camps[inst]["name"],
    "current_state": f"target_spend.cpc_bid_ceiling_micros = {cur_ceiling} "
                     f"(${cur_ceiling/1e6:.2f})",
    "proposed_state": "target_spend.cpc_bid_ceiling_micros = 65000000 ($65.00)",
    "field_mask": ["target_spend.cpc_bid_ceiling_micros"],
    "reason": ("All three of this campaign's primary conversion RECORDS came from clicks priced "
               "$50.00-$62.13 on 2026-09-01. The live $30 ceiling admits 76% of historical click "
               "volume while excluding every one of those clicks. $65 covers the highest "
               "observed converting CPC with headroom."),
    "modelled_effect": ("Descriptive sensitivity test on 62 visible historical clicks, NOT an "
                        "auction forecast: at $30, 47 clicks and 0 of 3 conversion records "
                        "survive; at $65, 62 clicks and 3 of 3 survive."),
    "rollback": f"set target_spend.cpc_bid_ceiling_micros back to {cur_ceiling} "
                f"(${cur_ceiling/1e6:.2f}) - the VERIFIED pre-test value. Any other rollback "
                f"amount requires separate approval.",
    "risk": "MEDIUM - restores paid delivery and therefore spend",
    "unrelated_resource_assertion":
        "AC Repair and HVAC Repair ceilings must remain 25000000; bidding stays TARGET_SPEND; "
        "budgets, geo, schedules, keywords and negatives unchanged"}]
finalise("AMB-0909C-CPC-INST-2", "reversible-setting-change-UNVERIFIED-TEST",
         "HVAC Installation ONLY: CPC bid ceiling $30 -> $65, run as an outcome-gated test with "
         "hard spend stop-losses. No other campaign is touched.", ops,
         {"supersedes": "AMB-0909B-CPC-INST-1 (DE376F91F449) - SUPERSEDED, DO_NOT_EXECUTE "
                        "(its rationale quoted a $141.87 CPA that mixed measurement grains)",
          "corrected_economics": {
              "prior_quoted_cpa": 141.87,
              "prior_cpa_defect": ips["prior_figure_defect"],
              "CORRECTED_campaign_level_raw_cpa": ips["correct_campaign_raw_cpa"],
              "window": ips["window"],
              "campaign_clicks": ips["campaign_clicks"],
              "campaign_cost": ips["campaign_cost"],
              "primary_conversion_RECORDS": ips["primary_conversions"],
              "label": "RAW CPA on RAW CONVERSION RECORDS. Not CPQL. Not qualified leads."},
          "unique_lead_bounding": {
              "records": 3, "unique_leads_known": False, "unique_lead_range": [1, 3],
              "cost_per_unique_lead": ib["cost_per_unique_lead"],
              "why": "All three records landed on 2026-09-01, a day with only 3 clicks - a 100% "
                     "click-to-record rate. 'Ambient Cooling - LP -Submit Lead Forms' (WEBPAGE, "
                     "fires on the thank-you view) and 'WC Lead' (UPLOAD_CLICKS, WhatConverts "
                     "uploading the same submission back against the same GCLID) both counted "
                     "that day, alongside GA4 form_submission and Clicks to call in All "
                     "conversions. One interaction can produce records under several actions.",
              "if_one_unique_lead": "cost per unique lead $483.98, which EXCEEDS the $280 "
                                    "target. This is the downside case and it is not excluded "
                                    "by the available evidence.",
              "resolvable_from_google_ads_api": False},
          "TEST_STATUS": "UNVERIFIED. Qualified-lead outcomes are unavailable "
                         "(WHATCONVERTS_API_TOKEN is empty). No CPQL compliance is claimed by "
                         "this package.",
          "outcome_based_stop_loss": {
              "gate_1": {"incremental_spend_since_execution": 280.00,
                         "requirement": "at least ONE verified unique qualified lead",
                         "verification_source": "WhatConverts, or an anonymised lead export "
                                                "joined on GCLID",
                         "if_not_met": "roll back to $30 immediately"},
              "gate_2": {"incremental_spend_since_execution": 560.00,
                         "requirement": "at least TWO verified unique qualified leads",
                         "if_not_met": "roll back to $30 immediately"},
              "no_30_click_threshold": "The superseded plan used a 30-click rollback trigger. At "
                                       "a $65 ceiling 30 clicks could cost up to $1,950 before "
                                       "intervention. Click counts are not used as a gate.",
              "rollback_target": "exactly 30000000 micros ($30.00), the verified pre-test value",
              "if_outcome_data_unavailable": "the test is labelled UNVERIFIED, no CPQL claim is "
                                             "made, and gate 1 still applies as a hard spend "
                                             "stop at $280 incremental"},
          "sequencing_constraint": {
              "rule": "Do NOT execute this CPC increase and any material HVAC Installation "
                      "search-term expansion in the same change window.",
              "separation": "at least 7 SETTLED days, or the $280 gate-1 spend threshold, "
                            "whichever comes first",
              "affected_packages": "AMB-0909C-COMP-1 adds three negatives to HVAC Installation. "
                                   "Negatives NARROW matching, so they do not conflict with the "
                                   "gate. AMB-0909C-NEG-COMMERCIAL widens matching on all five "
                                   "campaigns including Installation and MUST be separated from "
                                   "this package by the stated interval."},
          "live_keyword_verified": ["hvac installers near me [PHRASE] crit 295495761070 ELIGIBLE",
                                    "hvac installers near me [EXACT] crit 315030681341 ELIGIBLE"],
          "bid_modifier_audit": "5 modifiers exist, all DEVICE/TABLET x0.0. Highest modifier "
                                "anywhere is x0.0. Nothing can raise the effective bid above "
                                "$65."})

# ---------------------------------------------------------------- NEG-SAVAGE
sav = [n for n in negs if n["text"].strip().lower() == "savage" and n["match"] == "PHRASE"]
ops = []
for n in sorted(sav, key=lambda n: NAME[n["camp"]]):
    ops.append({
        "operation": "REMOVE_CAMPAIGN_NEGATIVE_KEYWORD", "resource": "campaign_criterion",
        "resource_name": f"customers/{CID}/campaignCriteria/{n['camp']}~{n['crit']}",
        "campaign_id": n["camp"], "campaign": NAME[n["camp"]], "criterion_id": n["crit"],
        "match_type": n["match"], "negative_text": n["text"],
        "current_state": f"negative KEYWORD [PHRASE] 'savage' ENABLED",
        "proposed_state": "REMOVED",
        "reason": ("geoTargetConstants/1018704 'Savage,Savage,Maryland,United States' is an "
                   "ENABLED, non-negative positive LOCATION criterion on this campaign. The "
                   "PHRASE negative blocks every query naming that targeted place. Verified "
                   "against the 22,500-probe service-by-place grid: 300 of 300 Savage probes "
                   "blocked, and it was the only negative responsible."),
        "conflict_tests": {
            "active_keywords": "clear - the 10 live positives contain no 'savage' token",
            "converting_terms_account_wide_all_time": "clear - 0 of 304 contain 'savage'",
            "targeted_locations": "RESTORES one - Savage MD, geoTargetConstants/1018704",
            "bofu_probes": "clear - removal unblocks, never blocks",
            "observed_search_terms": "0 rows since launch, which is the expected consequence "
                                     "of the negative suppressing them before reporting"},
        "rollback": f"re-create campaign negative 'savage' [PHRASE] on campaign {n['camp']}",
        "risk": "LOW - restores a targeted location",
        "unrelated_resource_assertion": "only this one campaign_criterion is removed"})
finalise("AMB-0909C-NEG-SAVAGE", "DESTRUCTIVE-removal",
         f"Remove PHRASE negative 'savage' from all five campaigns. {len(ops)} operations. "
         f"Savage, Maryland is proven to be an ENABLED positive location target on every one.",
         ops,
         {"supersedes": "part of AMB-0909B-NEG-A (18143479027D) - SUPERSEDED, DO_NOT_EXECUTE",
          "split_note": "The correction brief asked for a 10-operation NEG-CORE combining "
                        "'savage' and 'licensed'. The 'licensed' half could not clear its "
                        "required proof and is held separately. See the report.",
          "proof_savage_targeted": neg["neg_core_savage_targeted"],
          "geo_constant": neg["savage_geo_constant"]})

# ---------------------------------------------------------------- NEG-COMMERCIAL
cm = [a for a in acct if a["text"].strip().lower() == "commercial"]
dup = neg["commercial_duplicate_sweep"]
ops = []
for a in cm:
    ops.append({
        "operation": "REMOVE_SHARED_LIST_NEGATIVE", "resource": "shared_criterion",
        "shared_set_id": "11252984411",
        "shared_criterion_resource_name": a["rn"], "criterion_id": a["crit"],
        "match_type": a["match"], "negative_text": a["text"],
        "current_state": f"account-level negative KEYWORD [{a['match']}] 'commercial' "
                         f"in shared set 11252984411",
        "proposed_state": "REMOVED from the account-level list",
        "reason": ("Ambient's live website advertises commercial work: the homepage and the "
                   "furnace-repair page both name it, /services/hvac/condominium-hvac/ is a "
                   "dedicated page, and /category/commercial-hvac/ carries a Maryland BEPS "
                   "compliance article. Eleven historical search-term rows containing "
                   "'commercial' produced 3.83 RAW primary conversion records across five "
                   "legacy campaigns. BROAD 'commercial' is also named in the Green Marketing "
                   "operating rules as a word that must not be broad-negatived."),
        "raw_records_not_qualified_leads":
            "The 3.83 figure is a count of RAW CONVERSION RECORDS. Qualification is unknown and "
            "none of these is described as a qualified lead.",
        "rollback": "re-create 'commercial' as a BROAD negative keyword in shared set "
                    "11252984411 (shared_criterion create, keyword.text='commercial', "
                    "keyword.match_type=BROAD)",
        "risk": "MEDIUM - account-level scope reaches all 23 non-removed campaigns",
        "unrelated_resource_assertion":
            "shared set 11252984411 member count must fall from 272 to 271; the other 16 shared "
            "sets untouched; still 0 shared lists attached to the five campaigns"})
finalise("AMB-0909C-NEG-COMMERCIAL", "DESTRUCTIVE-removal-ACCOUNT-LEVEL",
         f"Remove the account-level BROAD negative 'commercial' from shared set 11252984411. "
         f"Exactly {len(ops)} operation.", ops,
         {"supersedes": "part of AMB-0909B-NEG-A (18143479027D) - SUPERSEDED, DO_NOT_EXECUTE",
          "duplicate_sweep": {
              "exact_token_commercial_negatives_account_wide": 5,
              "account_level_shared_set_11252984411": 1,
              "other_shared_sets": 0,
              "campaign_level": 2,
              "ad_group_level": 2,
              "on_the_five_live_campaigns": 0,
              "detail": [
                  "campaign 22822619680 'Leads-Performance Max-HVAC & A/C Install' - PAUSED",
                  "campaign 23883756382 'Leads-Performance Max-HVAC & A/C Install #2' - PAUSED",
                  "ad group 159023127588 in campaign 20293627152 'HVAC Install' - campaign PAUSED",
                  "ad group 201974220664 in campaign 20293627152 'HVAC Install' - campaign PAUSED"],
              "conclusion": "ZERO duplicates sit on the five live campaigns. Removing the "
                            "account-level member is therefore SUFFICIENT to unblock "
                            "'commercial' on everything that can currently serve. The four "
                            "duplicates affect only PAUSED campaigns and would need separate "
                            "handling if any of those were ever re-enabled.",
              "criterion_id_note": "All five share criterion_id 10061081. Criterion ids are not "
                                   "unique across resources; the resource_name is the key."},
          "effect_across_non_removed_campaigns": {
              "total_non_removed": 23, "enabled": 5, "paused": 18,
              "delivery_effect": "only the 5 ENABLED campaigns can serve, so only they change "
                                 "in delivery. The 18 PAUSED campaigns change in configuration "
                                 "only.",
              "enabled_campaigns": [NAME[c] for c in FIVE]},
          "historical_records": neg["commercial_historical_records"]})

# ---------------------------------------------------------------- COMPETITOR
INSTALL = "24132507747"
obs = {t["term"]: t for t in neg["competitor_observed_terms"]}
EXACTS = [
    ("arundel cooling and heating reviews",
     {"entity": "Arundel Cooling & Heating Co., Inc.",
      "address": "707 Nursery Rd, Linthicum Heights, MD 21090 - itself a live target location",
      "sources": ["https://www.bbb.org/us/md/linthicum/profile/heating-and-air-conditioning/"
                  "arundel-cooling-heating-co-inc-0011-563",
                  "https://www.yelp.com/biz/arundel-cooling-and-heating-linthicum-heights-2"]}),
    ("arundel heating and cooling maryland",
     {"entity": "Arundel Cooling & Heating Co., Inc.",
      "address": "707 Nursery Rd, Linthicum Heights, MD 21090",
      "sources": ["https://www.bbb.org/us/md/linthicum/profile/heating-and-air-conditioning/"
                  "arundel-cooling-heating-co-inc-0011-563"]}),
    ("maryland mechanical heating & cooling",
     {"entity": "Maryland Mechanical Heating & Cooling LLC",
      "address": "marylandhvacs.com, Maryland HVACR licence #22169, founded 2023",
      "sources": ["https://marylandhvacs.com/",
                  "https://www.labor.maryland.gov/license/hvacr/"]}),
]
ops = []
for txt, ev in EXACTS:
    o = obs.get(txt)
    ops.append({
        "operation": "ADD_CAMPAIGN_NEGATIVE_KEYWORD", "resource": "campaign_criterion",
        "resource_id": INSTALL, "campaign_id": INSTALL, "campaign": NAME[INSTALL],
        "match_type": "EXACT", "negative_text": txt,
        "current_state": "not present at campaign, ad group or account level",
        "proposed_state": f"negative KEYWORD [EXACT] {txt!r} ENABLED",
        "reason": f"Verified competing HVAC contractor: {ev['entity']}. EXACT match on the "
                  f"VERBATIM OBSERVED QUERY, not an invented variant.",
        "entity_verification": ev,
        "observed_query_verbatim": txt,
        "observed_metrics": ({"impressions": o["impr"], "clicks": o["clicks"],
                              "cost": o["cost"], "conversions": o["conv"],
                              "campaign": o["camp"], "status": o["status"]} if o else None),
        "word_count": len(txt.split()), "char_count": len(txt),
        "rollback": f"remove the campaign negative {txt!r} [EXACT] from {INSTALL}",
        "risk": "LOW - EXACT match on one observed brand query",
        "unrelated_resource_assertion":
            "HVAC Installation ENABLED campaign negatives rise by exactly 3; no other campaign "
            "changes"})
finalise("AMB-0909C-COMP-1", "reversible-addition",
         f"Verified competitors, EXACT match only: {len(ops)} negatives on HVAC Installation, "
         f"each reproducing a verbatim observed query.", ops,
         {"supersedes": "AMB-0909B-COMP-1 (05FBCBD34B4A) - SUPERSEDED, DO_NOT_EXECUTE",
          "match_type_correction":
              "The superseded package used PHRASE 'maryland mechanical heating'. That is "
              "withdrawn: it can overlap generic Maryland mechanical-heating intent. All three "
              "operations are now EXACT on the verbatim observed query, ampersand included.",
          "verbatim_spellings_used": [t for t, _ in EXACTS],
          "deliberately_not_blocked": {
              "arundel cooling and heating": "6 impressions, 0 clicks, $0.00. Sits one word from "
                                             "'anne arundel cooling and heating' (1 primary "
                                             "conversion record) and 'hvac anne arundel county'. "
                                             "Not worth the risk.",
              "anne arundel cooling and heating": "produced a primary phone-call record in the "
                                                  "legacy Heating Maintenance campaign",
              "hvac anne arundel county": "county intent in the core service area"},
          "observed_terms": neg["competitor_observed_terms"]})

# ---------------------------------------------------------------- write
out = TOPPLANS / "AMBIENT-2026-09-09c-packages.json"
out.write_text(json.dumps(plans, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {out.relative_to(ROOT)}")
for name, p in plans.items():
    ind = CLIENT_DIR / "plans" / f"{name}.json"
    ind.write_text(json.dumps(p, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {ind.relative_to(ROOT)}")

print("\n=== NEW FINGERPRINT MANIFEST ===")
for name, p in plans.items():
    print(f"  {name:<28} {p['approval_class']:<40} ops={p['object_count']:<3} "
          f"{p['fingerprint']}")
tot = sum(p["object_count"] for p in plans.values())
print(f"\n  NEW PACKAGES TOTAL: {tot} operations")
print(f"  + carried-forward AMB-0909-ADS-1 (11A79347A296): 2 operations")
print(f"  = APPROVAL BLOCK TOTAL: {tot + 2} operations")
