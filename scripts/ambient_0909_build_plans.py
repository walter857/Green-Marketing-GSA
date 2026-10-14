#!/usr/bin/env python3
"""Build the 2026-09-09 approval-gated packages with deterministic fingerprints.

Packages (each independently approvable, no bundling of different risk classes):
  AMB-0909-CPC-1     raise the 2026-09-04 CPC ceilings that stopped delivery  (reversible)
  AMB-0909-NEG-RM-1  remove live negatives that block confirmed services      (DESTRUCTIVE)
  AMB-0909-ADS-1     pause two live DISAPPROVED RSAs                          (reversible)
  AMB-0909-NEG-ADD-1 add competitor / research negatives to HVAC Installation (reversible)
  AMB-0909-BUD-1     move unspendable Gas Boiler budget to HVAC Installation  (reversible)
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

struct = json.load(open(EVID / "2026-09-09-structure.json", encoding="utf-8"))
rem = json.load(open(EVID / "2026-09-09-removal-plan-analysis.json", encoding="utf-8"))
model = json.load(open(EVID / "2026-09-09-cpc-model.json", encoding="utf-8"))
sweep = json.load(open(EVID / "2026-09-09-geo-negative-sweep.json", encoding="utf-8"))
ident = json.load(open(EVID / "2026-09-09-identity-and-structure.json", encoding="utf-8"))

STAMP = "2026-09-09"
NOW = datetime.datetime.now(TZ).isoformat()
TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "AC Repair",
          "related_services": ["HVAC Repair", "HVAC Installation", "HVAC Replacement",
                               "Gas Boiler Repair"]}
plans = {}


def finalise(name, klass, summary, ops, notes):
    p = {"plan_name": name, "approval_class": klass, "generated_local": NOW,
         "target": TARGET, "summary": summary, "object_count": len(ops),
         "partial_failure": False, "atomic": True, "operations": ops, "notes": notes}
    p["fingerprint"] = approval_code({"target": TARGET, "plan": name, "operations": ops})
    plans[name] = p
    print(f"\n=== {name} [{klass}] ops={len(ops)} fingerprint={p['fingerprint']} ===")
    print(f"    {summary}")
    return p


# ---------------------------------------------------------------------------
# 1. AMB-0909-CPC-1
# ---------------------------------------------------------------------------
camps = {c["id"]: c for c in ident["campaigns"]}
CPC_DECISION = {
    "24132507747": {  # HVAC Installation
        "new": 65.00,
        "why": ("Post-keyword-swap window 2026-08-29..09-03 delivered 9 clicks, $425.61, "
                "3 primary conversions, CPA $141.87 against a $280 max CPQL, with a maximum "
                "observed CPC of $62.13. The $30 ceiling set on 2026-09-04 took the campaign "
                "to 0 clicks in the 4 settled days that followed. $65 preserves every "
                "observed converting click with headroom."),
        "modelled": "at $60 the settled window retains 98.4% of clicks and 100% of "
                    "conversions; at $30 it retains 75.8% of clicks and 0% of conversions"},
    "24132507750": {  # HVAC Repair
        "new": 60.00,
        "why": ("Median observed CPC $56.41; Keyword Planner top-of-page LOW for "
                "'hvac repair near me' in the live footprint is $14.87 and HIGH is $97.88. "
                "The $25 ceiling retains 24% of clicks. $60 restores roughly half the "
                "click volume at a $36.47 blended CPC, inside the optimistic economic band "
                "while Quality Score (currently 2, landing-page experience BELOW_AVERAGE) "
                "is remediated."),
        "modelled": "at $60 the settled window retains 52% of clicks and 26% of spend"},
}
ops = []
for cid, d in CPC_DECISION.items():
    cur = camps[cid]["target_spend_ceiling_micros"]
    ops.append({
        "operation": "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING",
        "resource": "campaign", "resource_id": cid, "resource_name": NAME[cid],
        "campaign_name": camps[cid]["name"],
        "current_state": f"target_spend.cpc_bid_ceiling_micros = {cur} (${cur/1e6:.2f})",
        "proposed_state": f"target_spend.cpc_bid_ceiling_micros = {int(d['new']*1e6)} "
                          f"(${d['new']:.2f})",
        "field_mask": ["target_spend.cpc_bid_ceiling_micros"],
        "reason": d["why"], "modelled_effect": d["modelled"],
        "rollback": f"set target_spend.cpc_bid_ceiling_micros back to {cur}",
        "risk": "MEDIUM - restores paid delivery and therefore spend",
        "unrelated_resource_assertion":
            "bidding_strategy_type stays TARGET_SPEND; budget, networks, geo, schedule, "
            "keywords, negatives and assets are not in the field mask and must be unchanged "
            "on readback"})
finalise("AMB-0909-CPC-1", "reversible-setting-change",
         "Raise the CPC bid ceilings on HVAC Installation ($30 to $65) and HVAC Repair "
         "($25 to $60). AC Repair's $25 ceiling is deliberately left in place.", ops,
         {"evidence": "reports/ambient-cooling-heating/evidence/2026-09-09-cpc-model.json",
          "ac_repair_deliberately_excluded":
              "AC Repair raw CPA is $616.97 against a $150 max CPQL. No modelled cap makes it "
              "profitable: $110 retains 3 of 5 conversions at CPA $298.35, $160 retains all "
              "five at CPA $365.82. Raising this ceiling would buy proven-unprofitable traffic, "
              "so the campaign is held at $25 pending Quality Score and landing-page work.",
          "who_set_the_current_ceilings":
              "GOOGLE_ADS_WEB_CLIENT on 2026-09-04 16:56 America/New_York (owner, in the UI). "
              "Not an agency change.",
          "delivery_impact_measured":
              "2026-08-14..09-03: $8,025.18, 172 clicks, 14 primary conversions. "
              "2026-09-05..09-08: $45.08, 2 clicks, 0 primary conversions."})

# ---------------------------------------------------------------------------
# 2. AMB-0909-NEG-RM-1  (DESTRUCTIVE)
# ---------------------------------------------------------------------------
live = [n for n in struct["campaign_negatives"]
        if n["status"] == "ENABLED" and n["campaign_id"] in FIVE]
ops = []
for o in rem["removal_operations"]:
    ops.append({
        "operation": "REMOVE_CAMPAIGN_NEGATIVE_KEYWORD",
        "resource": "campaign_criterion", "resource_name": o["resource_name"],
        "campaign_id": o["campaign_id"], "campaign": o["campaign"],
        "criterion_id": o["criterion_id"], "match_type": o["match"],
        "negative_text": o["text"],
        "current_state": f"negative KEYWORD [{o['match']}] {o['text']!r} ENABLED",
        "proposed_state": "REMOVED",
        "reason": o["reason"],
        "conversions_at_risk_if_left": o["conversions_at_risk"],
        "all_conversions_at_risk_if_left": o["all_conversions_at_risk"],
        "bofu_probes_unblocked": o["bofu_probes_unblocked"],
        "rollback": f"re-create campaign negative keyword {o['text']!r} [{o['match']}] "
                    f"on campaign {o['campaign_id']}",
        "risk": "MEDIUM - removing a negative widens matching",
        "unrelated_resource_assertion":
            "only this one campaign_criterion is removed; the other live negatives on this "
            "campaign must still be present on readback"})
# the 'savage' negative: Savage, Maryland is one of the 75 live geo targets
savage = [n for n in live if n["text"].strip().lower() == "savage" and n["match"] == "PHRASE"]
for n in savage:
    ops.append({
        "operation": "REMOVE_CAMPAIGN_NEGATIVE_KEYWORD",
        "resource": "campaign_criterion",
        "resource_name": f"customers/{CID}/campaignCriteria/"
                         f"{n['campaign_id']}~{n['criterion_id']}",
        "campaign_id": n["campaign_id"], "campaign": NAME[n["campaign_id"]],
        "criterion_id": n["criterion_id"], "match_type": n["match"],
        "negative_text": n["text"],
        "current_state": f"negative KEYWORD [{n['match']}] {n['text']!r} ENABLED",
        "proposed_state": "REMOVED",
        "reason": "Savage, Maryland (geoTargetConstants/1018704) is one of the 75 live "
                  "location targets on all five campaigns. This PHRASE negative blocks all "
                  "300 service-by-place probes for that city.",
        "conversions_at_risk_if_left": 0,
        "all_conversions_at_risk_if_left": 0,
        "bofu_probes_unblocked": ["<service> savage md", "<service> in savage",
                                  "<service> near savage maryland"],
        "rollback": f"re-create campaign negative keyword 'savage' [PHRASE] on campaign "
                    f"{n['campaign_id']}",
        "risk": "LOW - restores a targeted city",
        "unrelated_resource_assertion":
            "only this one campaign_criterion is removed"})
finalise("AMB-0909-NEG-RM-1", "DESTRUCTIVE-removal",
         f"Remove {len(ops)} live campaign negative keywords that block confirmed Ambient "
         f"services, supported manufacturers, a targeted Maryland city, or generic value "
         f"words the Green Marketing rules forbid negativing.", ops,
         {"evidence": "reports/ambient-cooling-heating/evidence/"
                      "2026-09-09-collision-audit.json and 2026-09-09-negative-triage.csv",
          "triage_totals": dict(Counter(r["verdict"] for r in rem["triage"])),
          "kept_deliberately": "60 colliding negatives are competitor company/person names, "
                               "supply houses or out-of-area places and are correct. 5 are "
                               "intentional cross-campaign routing negatives; sibling "
                               "eligibility was proved for each.",
          "destructive_note": "This package removes resources. It requires its own explicit "
                              "approval line and must not be bundled with any other package."})

# ---------------------------------------------------------------------------
# 3. AMB-0909-ADS-1
# ---------------------------------------------------------------------------
ads = json.load(open(EVID / "2026-09-09-ads-assets.json", encoding="utf-8"))["ads"]
LIVE_AG = {"202339087834", "202339087594", "202339087634", "202339087674", "200159223798"}
bad = [a for a in ads if a["status"] == "ENABLED" and a["approval"] == "DISAPPROVED"
       and a["ag"] in LIVE_AG]
ops = []
for a in bad:
    ops.append({
        "operation": "PAUSE_AD_GROUP_AD", "resource": "ad_group_ad",
        "resource_name": f"customers/{CID}/adGroupAds/{a['ag']}~{a['ad_id']}",
        "campaign_id": a["camp"], "campaign": NAME[a["camp"]],
        "ad_group_id": a["ag"], "ad_id": a["ad_id"],
        "current_state": "status = ENABLED, approval_status = DISAPPROVED "
                         "(policy topic CONSUMER_FINANCE, FULLY_LIMITED)",
        "proposed_state": "PAUSED",
        "reason": "A FULLY_LIMITED disapproved ad cannot serve. Leaving it ENABLED hides the "
                  "fact that the ad group is really running two RSAs, and keeps a "
                  "policy-flagged asset attached to a serving ad group. The approved "
                  "replacement RSAs created on 2026-08-21 are already live in the same "
                  "ad group.",
        "remaining_enabled_approved_ads_in_ad_group":
            [x["ad_id"] for x in ads if x["ag"] == a["ag"] and x["status"] == "ENABLED"
             and x["approval"] == "APPROVED"],
        "rollback": f"set ad_group_ad {a['ag']}~{a['ad_id']} status back to ENABLED",
        "risk": "LOW - the ad cannot serve today",
        "unrelated_resource_assertion":
            "each ad group must still hold at least two ENABLED APPROVED RSAs on readback"})
finalise("AMB-0909-ADS-1", "reversible-status-change",
         f"Pause {len(ops)} ENABLED-but-DISAPPROVED RSAs in live ad groups "
         f"(CONSUMER_FINANCE, FULLY_LIMITED). Each ad group keeps two ENABLED APPROVED "
         f"RSAs, satisfying agency policy.", ops,
         {"policy_topic": "CONSUMER_FINANCE / FULLY_LIMITED, review_status REVIEWED",
          "not_included": "The two AREA_OF_INTEREST_ONLY ads in AC Repair sit in REMOVED ad "
                          "group 202339087874 and cannot serve. No operation is needed."})

# ---------------------------------------------------------------------------
# 4. AMB-0909-NEG-ADD-1
# ---------------------------------------------------------------------------
INSTALL = "24132507747"
ADDS = [
    ("PHRASE", "arundel cooling and heating",
     "Competitor company name. PHRASE, not BROAD: 'arundel' alone is Anne Arundel County, "
     "the core service area, and must never be negatived."),
    ("PHRASE", "maryland mechanical heating",
     "Competitor company name (Maryland Mechanical). PHRASE keeps 'maryland' and "
     "'mechanical' usable on their own."),
    ("PHRASE", "all about air",
     "Competitor company name."),
    ("PHRASE", "home comfort hvac",
     "Competitor company name. 'comfort' alone is left usable."),
    ("PHRASE", "sq ft house",
     "Sizing-calculator research. Replaces two 12- and 13-word EXACT negatives that breached "
     "the 10-word negative-keyword limit (caught by local preflight). PHRASE on this "
     "3-word fragment blocks square-footage sizing research only; it cannot touch any "
     "service, location or value-intent query. Tested against all 67 BOFU probes: 0 hits."),
    ("EXACT", "how much is hvac system",
     "Price-research query with no service qualifier, no location and no hire verb. "
     "EXACT only, so 'how much', 'cost' and 'price' stay usable everywhere else."),
]
ops = []
for mt, txt, why in ADDS:
    ops.append({
        "operation": "ADD_CAMPAIGN_NEGATIVE_KEYWORD", "resource": "campaign_criterion",
        "resource_id": INSTALL, "campaign_id": INSTALL, "campaign": NAME[INSTALL],
        "match_type": mt, "negative_text": txt,
        "current_state": "not present at campaign, ad group or account level",
        "proposed_state": f"negative KEYWORD [{mt}] {txt!r} ENABLED",
        "reason": why,
        "word_count": len(txt.split()), "char_count": len(txt),
        "rollback": f"remove the campaign negative keyword {txt!r} [{mt}] from {INSTALL}",
        "risk": "LOW",
        "unrelated_resource_assertion":
            "campaign negative count on 24132507747 must rise from 1435 to "
            f"{1435 + len(ADDS)} and no other campaign may change"})
finalise("AMB-0909-NEG-ADD-1", "reversible-addition",
         f"Add {len(ops)} narrowly scoped negatives to HVAC Installation: four competitor "
         f"company PHRASE negatives, one sizing-research PHRASE and one EXACT price-research "
         f"query. Total visible waste addressed is $104.92 over 26 settled days.", ops,
         {"materiality": "LOW. The 6,160 live negatives already cover 419 of 952 visible "
                         "search-term rows. Only 20 rows survived classification as HOLD or "
                         "NEGATIVE_CANDIDATE, together worth $104.92.",
          "deliberately_not_added":
              "'hvac annapolis md', 'hvac in annapolis md', 'maryland hvac' and "
              "'hvac baltimore' are in-footprint service queries and were left live. "
              "'hvac companies with payment plans' is held pending a financing answer."})

# ---------------------------------------------------------------------------
# 5. AMB-0909-BUD-1
# ---------------------------------------------------------------------------
BUD = {"15787409438": ("Gas Boiler Repair", 42.76, 5.00,
                       "34 impressions and zero clicks since launch. Keyword Planner across "
                       "the live 10-city sample returns 20 monthly searches for the best "
                       "boiler term and no top-of-page bid estimate at all. The landing page "
                       "still carries the wrong service heading, so the campaign is gated "
                       "anyway. $5.00/day keeps it alive for measurement without reserving "
                       "unspendable budget."),
       "15787409441": ("HVAC Installation", 176.15, 181.61,
                       "Only budget-limited campaign in the account: 53.16% Search lost "
                       "impression share (budget) over the last 30 settled days, against "
                       "10.32% lost to rank. It also produced the account's only sub-target "
                       "CPA window (CPA $141.87 against a $280 max CPQL after the "
                       "2026-08-29 keyword swap). Receives $5.46 of the $37.76 released by "
                       "Gas Boiler; the remaining $32.30 is retired so that the five daily "
                       "budgets sum to exactly $433.33, which is $13,000 over 30 days.")}
ops = []
for bid, (label, cur, new, why) in BUD.items():
    ops.append({
        "operation": "UPDATE_CAMPAIGN_BUDGET", "resource": "campaign_budget",
        "resource_id": bid, "resource_name": f"customers/{CID}/campaignBudgets/{bid}",
        "campaign": label,
        "current_state": f"amount_micros = {int(cur*1e6)} (${cur:.2f}/day)",
        "proposed_state": f"amount_micros = {int(new*1e6)} (${new:.2f}/day)",
        "field_mask": ["amount_micros"], "reason": why,
        "rollback": f"set amount_micros back to {int(cur*1e6)}",
        "risk": "LOW - net daily total unchanged",
        "unrelated_resource_assertion":
            "sum of the five daily budgets must stay $465.63; the other three budgets "
            "(15787409435, 15787409444, 15787409447) must be unchanged"})
tot_before = 141.45 + 42.76 + 176.15 + 78.95 + 26.32
tot_after = 141.45 + 5.00 + 181.61 + 78.95 + 26.32
finalise("AMB-0909-BUD-1", "reversible-budget-change",
         f"Retire $37.76/day of unspendable Gas Boiler Repair budget: $5.46 goes to the "
         f"budget-limited HVAC Installation campaign and $32.30 is released, bringing the "
         f"five daily budgets to ${tot_after:.2f} - exactly $13,000 over 30 days.", ops,
         {"daily_total_before": round(tot_before, 2), "daily_total_after": round(tot_after, 2),
          "monthly_maximum_usd": 13000,
          "worst_case_30_day_exposure_before": round(tot_before * 30, 2),
          "worst_case_30_day_exposure_after": round(tot_after * 30, 2),
          "cap_note": "Before this package the five daily budgets summed to $465.63, which is "
                      "$13,968.90 over 30 days - $968.90 above the $13,000 monthly maximum. "
                      "Observed spend has never approached it (August settled at $6,842.80; "
                      "September stands at $1,260.86 through 8 settled days), but the "
                      "documented worst case did breach the cap. This package closes that "
                      "gap by construction: $433.33 x 30 = $13,000.00 exactly.",
          "ac_repair_budget_left_alone": "AC Repair keeps $141.45/day even though its $25 "
                                         "ceiling currently prevents it from spending. "
                                         "Cutting it would make the deliberate ceiling hold "
                                         "harder to reverse. Raised as an owner question "
                                         "instead."})

# ---------------------------------------------------------------------------
out = TOPPLANS / f"AMBIENT-{STAMP}-packages.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(plans, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {out.relative_to(ROOT)}")
for name, p in plans.items():
    ind = CLIENT_DIR / "plans" / f"{name}.json"
    ind.write_text(json.dumps(p, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {ind.relative_to(ROOT)}")

print("\n=== FINGERPRINT MANIFEST ===")
for name, p in plans.items():
    print(f"  {name:<22} {p['approval_class']:<26} ops={p['object_count']:<4} "
          f"{p['fingerprint']}")
print(f"\n  TOTAL OPERATIONS ACROSS ALL PACKAGES: {sum(p['object_count'] for p in plans.values())}")
