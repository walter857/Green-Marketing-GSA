#!/usr/bin/env python3
"""Build PLAN-K2 - search-term cleaning via negative keywords (DRAFT).

Negative keywords go LIVE the instant they are created, so this is an external
write and needs its own fingerprint and its own exact approval.

READ ONLY against Google Ads. Writes the local plan + fingerprint only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
CLIENT = ROOT / "clients/softwind-power-washing"
OUT_YAML = CLIENT / "plans/2026-08-27-plan-k2-search-term-cleaning.yaml"
OUT_FP = CLIENT / "plans/2026-08-27-k2-fingerprint.json"
ANALYSIS = CLIENT / "audits/2026-08-27-search-term-classification.json"


def normalize(plan: dict) -> dict:
    p = plan["change_plan"]
    t = p["target"]
    actions = []
    for a in p.get("actions", []):
        actions.append({
            "action_id": a["action_id"], "priority": a["priority"],
            "resource_type": a["resource_type"], "operation": a["operation"],
            "customer_id": a.get("customer_id", t["child_customer_id"]),
            "campaign_id": a.get("campaign_id"),
            "ad_group_id": a.get("ad_group_id"),
            "resource_id": a.get("resource_id"),
            "current_value": a.get("current_value"),
            "proposed_value": a.get("proposed_value"),
            "object_count": a.get("object_count", 1)})
    actions.sort(key=lambda x: x["action_id"])
    return {"target": {"exact_child_account_name": t["exact_child_account_name"],
                       "child_customer_id": t["child_customer_id"],
                       "exact_service": t["exact_service"]},
            "plan_id": p["plan_id"], "approval_type": p["approval_type"],
            "actions": actions, "action_count": len(actions),
            "object_count": sum(a["object_count"] for a in actions)}


AG_NEGATIVES = [
    {"ad_group_id": "202870585390", "ad_group": "Power Washing Near Me",
     "campaign_id": CAMP_A, "ad_group_status": "ENABLED",
     "text": "gas station pressure washing near me",
     "bucket": "COMMERCIAL_INDUSTRIAL", "impressions": 4, "clicks": 1,
     "cost": 35.31, "confidence": "HIGH",
     "why": ("Industrial forecourt degreasing. The ad group's landing page is "
             "residential power washing in Islip / West Islip / Dix Hills. This "
             "single query took $35.31 - the most expensive out-of-scope click "
             "in the account's history.")},
    {"ad_group_id": "202870585390", "ad_group": "Power Washing Near Me",
     "campaign_id": CAMP_A, "ad_group_status": "ENABLED",
     "text": "commercial power washing company near me",
     "bucket": "COMMERCIAL_INDUSTRIAL", "impressions": 2, "clicks": 0,
     "cost": 0.0, "confidence": "MEDIUM - depends on K1-W2",
     "why": ("Commercial intent against a residential landing page. Kept as a "
             "NARROW exact negative rather than a broad 'commercial' phrase "
             "negative precisely because whether Softwind takes commercial work "
             "is still unanswered (K1-W2). This blocks one exact query, not the "
             "commercial theme, and is trivially reversible.")},
    {"ad_group_id": "202870585590", "ad_group": "Power Washing Company Near Me",
     "campaign_id": CAMP_A, "ad_group_status": "ENABLED",
     "text": "roof washing near me",
     "bucket": "EXCLUDED_SERVICE", "impressions": 2, "clicks": 0, "cost": 0.0,
     "confidence": "HIGH",
     "why": ("Roof cleaning is named in work-order.yaml excluded_services. Not "
             "an approved service under this work order.")},
    {"ad_group_id": "202870585910", "ad_group": "House Washing Company Near Me",
     "campaign_id": CAMP_A, "ad_group_status": "PAUSED",
     "text": "slate roof cleaning near me",
     "bucket": "EXCLUDED_SERVICE", "impressions": 1, "clicks": 0, "cost": 0.0,
     "confidence": "HIGH",
     "why": ("Roof cleaning, explicitly excluded. The ad group is currently "
             "PAUSED so this negative is inert today; it is added as hygiene so "
             "the term cannot leak if the ad group is ever re-enabled.")},
    {"ad_group_id": "202870585910", "ad_group": "House Washing Company Near Me",
     "campaign_id": CAMP_A, "ad_group_status": "PAUSED",
     "text": "house cleaning services near me",
     "bucket": "INTERIOR_CLEANING", "impressions": 1, "clicks": 0, "cost": 0.0,
     "confidence": "MEDIUM - judgment call",
     "why": ("'House cleaning services' without an exterior qualifier reads as "
             "interior maid service, against a /house-washing-company/ exterior "
             "landing page. Note the contrast with 'outdoor house cleaning "
             "services near me', which IS kept - the word 'outdoor' resolves the "
             "ambiguity in favour of the approved service.")},
]

CAMPAIGN_NEGATIVES = [
    {"text": "roof", "match": "PHRASE", "confidence": "HIGH",
     "why": ("Roof cleaning is an excluded service. Verified against all 55 "
             "distinct live keyword texts: ZERO contain 'roof', so this blocks "
             "no live keyword. Stops the excluded theme leaking into any other "
             "ad group, which an ad-group exact negative cannot do.")},
    {"text": "gas station", "match": "PHRASE", "confidence": "HIGH",
     "why": ("Industrial forecourt work. Verified against all 55 live keyword "
             "texts: ZERO contain 'gas station'. Prevents the same $35.31 "
             "mistake recurring through a different ad group.")},
]


def main() -> int:
    now = datetime.now(TZ)
    an = json.loads(ANALYSIS.read_text(encoding="utf-8"))

    actions = []
    obj = 0
    for i, n in enumerate(AG_NEGATIVES, 1):
        obj += 1
        actions.append({
            "action_id": "K2-01-%02d" % i, "priority": "P1",
            "resource_type": "AD_GROUP_CRITERION", "operation": "CREATE_NEGATIVE",
            "customer_id": CID, "campaign_id": n["campaign_id"],
            "ad_group_id": n["ad_group_id"],
            "resource_id": "ad_group %s negative keyword" % n["ad_group_id"],
            "current_value": "not present as a negative in this ad group",
            "proposed_value": {"keyword_text": n["text"], "match_type": "EXACT",
                               "negative": True},
            "ad_group_name": n["ad_group"],
            "ad_group_status": n["ad_group_status"],
            "bucket": n["bucket"], "confidence": n["confidence"],
            "observed_impressions": n["impressions"],
            "observed_clicks": n["clicks"], "observed_cost": n["cost"],
            "why": n["why"],
            "blocks_live_keyword": False,
            "rollback": "Remove the ad_group_criterion negative.",
            "object_count": 1})
    for i, n in enumerate(CAMPAIGN_NEGATIVES, 1):
        for cid_ in (CAMP_A, CAMP_B):
            obj += 1
            actions.append({
                "action_id": "K2-02-%02d-%s" % (i, cid_[-4:]), "priority": "P1",
                "resource_type": "CAMPAIGN_CRITERION",
                "operation": "CREATE_NEGATIVE",
                "customer_id": CID, "campaign_id": cid_, "ad_group_id": None,
                "resource_id": "campaign %s negative keyword" % cid_,
                "current_value": "not present as a campaign negative",
                "proposed_value": {"keyword_text": n["text"],
                                   "match_type": n["match"], "negative": True},
                "confidence": n["confidence"], "why": n["why"],
                "blocks_live_keyword": False,
                "rollback": "Remove the campaign_criterion negative.",
                "object_count": 1})

    plan = {"change_plan": {
        "plan_id": "PLAN-K2",
        "plan_title": "Search-term cleaning - ad-group exact and campaign phrase negatives",
        "approval_type": "NEGATIVES",
        "priority": "P1",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "ads_mutation_count": obj,
        "requires_separate_enable_approval": False,
        "goes_live_immediately": (
            "YES. Negative keywords take effect the moment they are created. "
            "There is no paused state for a negative, which is why this plan is "
            "separate from every create-paused plan and carries its own "
            "fingerprint."),
        "target": {"exact_child_account_name": NAME, "child_customer_id": CID,
                   "manager_customer_id": "3373711342",
                   "exact_service": "Power Washing",
                   "vertical": "similar-local-service"},
        "request_as_received": (
            "Clean all search terms, add as many as negative based on their ad "
            "group's keywords and landing-page intention, and add bad search "
            "terms as EXACT match inside each ad group so they show as excluded "
            "in the ad-group search-term report."),
        "headline_finding_the_owner_should_read_first": (
            "THERE IS VERY LITTLE TO CLEAN, AND 'AS MANY AS POSSIBLE' IS THE "
            "WRONG TARGET FOR THIS ACCOUNT. Of 56 ad-group x search-term pairs, "
            "49 (87.5%) are in-scope power-washing intent, carrying 90 of 100 "
            "clicks and $282.74 of $318.05 in matched cost. Only 4 pairs are "
            "genuinely out of scope and only ONE of them ever cost money. This "
            "account holds 43-70% impression share and Google reports campaign "
            "B as LIMITED_BY_INVENTORY: it is starved of volume, not drowning "
            "in junk. Every unnecessary negative removes reach from an account "
            "that just started delivering. The five ad-group negatives below are "
            "the complete defensible list, not a shortlist."),
        "classification_method": {
            "approach": ("WHITELIST-FIRST. A positive in-scope vocabulary for "
                         "the approved Power Washing service family was defined; "
                         "anything failing it was bucketed by the reason it "
                         "failed. No blocklist was imported or written."),
            "corpus": an["corpus"],
            "buckets": an["buckets"],
            "protected_terms_never_negatived": [
                "near me", "near you", "quote", "price", "pricing", "cost",
                "best", "hire", "local", "emergency", "estimate", "free",
                "cheap", "affordable", "company", "service", "services",
                "contractor", "professional", "residential"],
            "protected_terms_note": (
                "CLAUDE.md forbids auto-negativing these. Several appear inside "
                "the proposed negatives - 'near me' is in four of the five - but "
                "each is negatived as a COMPLETE EXACT PHRASE, never as a token. "
                "'gas station pressure washing near me' EXACT does not block "
                "'power washing near me'."),
            "collision_check": (
                "Every proposed negative was tested against all 55 distinct live "
                "keyword texts. ZERO collisions. No proposed negative blocks any "
                "live keyword in any ad group."),
            "evidence": ["audits/2026-08-27-search-term-classification.json",
                         "audits/2026-08-27-negative-candidates.csv"]},
        "deliberately_kept_not_negatived": [
            {"term": "jet wash near me", "impressions": 3, "clicks": 0,
             "verdict": "KEEP",
             "why": ("'Jet wash' is a common synonym for pressure washing, not "
                     "an out-of-scope intent. It is in fact a KEYWORD "
                     "OPPORTUNITY, not a negative - it currently reaches the "
                     "account only through a close variant.")},
            {"term": "outdoor house cleaning services near me", "impressions": 2,
             "clicks": 0, "verdict": "KEEP",
             "why": ("'Outdoor' qualifies this as exterior washing, which is the "
                     "approved service. Contrast with 'house cleaning services "
                     "near me', which lacks the qualifier and IS negatived.")},
            {"term": "all remaining in-scope terms", "count": 49,
             "verdict": "KEEP",
             "why": ("Core BOFU power-washing and pressure-washing intent, "
                     "correctly matched to the ad group's keywords and to an "
                     "offer-subdomain landing page for the same service.")}],
        "why_two_tiers": (
            "K2-01 does exactly what was asked: ad-group EXACT negatives, which "
            "make each term show as Excluded in that ad group's search-term "
            "report. But an ad-group exact negative only stops the term in ONE "
            "ad group - the same query can still be served by another ad group "
            "whose keyword also close-variant matches it. K2-02 adds two "
            "campaign-level PHRASE negatives for the two genuinely excluded "
            "themes, so the leak cannot simply move. Both were collision-tested "
            "against every live keyword."),
        "commercial_intent_held_out": (
            "No broad 'commercial' negative is proposed. Whether Softwind takes "
            "commercial work is still unanswered (K1-W2). A broad phrase "
            "negative could block real revenue, so only the single observed "
            "exact query is negatived. Answer K1-W2 and the theme can be handled "
            "properly - either a campaign phrase negative, or its own ad group "
            "and landing page."),
        "actions": actions,
        "change_counts": {
            "ad_group_negatives_added": len(AG_NEGATIVES),
            "campaign_negatives_added": len(CAMPAIGN_NEGATIVES) * 2,
            "budgets_changed": 0, "bidding_settings_changed": 0,
            "keywords_changed": 0, "ads_changed": 0, "assets_changed": 0,
            "locations_changed": 0, "schedules_changed": 0,
            "conversion_actions_changed": 0,
            "google_ads_mutations_total": obj},
        "expected_effect": {
            "spend_impact": (
                "Slightly NEGATIVE on volume and roughly neutral to positive on "
                "quality. The negatived terms account for 10 impressions and 1 "
                "click ($35.31) across the whole month. Removing them will not "
                "meaningfully reduce August spend, and it prevents repeat "
                "purchases of the single worst click type in the account."),
            "does_not_help_the_2500_goal": (
                "This plan does not move the spend goal and is not intended to. "
                "It protects quality. The $2,500 goal remains unreachable for "
                "the reasons in the 2026-08-27 delivery diagnosis."),
            "search_term_report": (
                "Each negatived term will show as Excluded in the ad-group "
                "search-term report, which is what was asked for.")},
        "readback_qa": [
            "Re-read ad_group_criterion negatives and assert the 5 new EXACT "
            "negatives exist on the named ad groups.",
            "Re-read campaign_criterion negatives and assert 94 + 4 = 98.",
            "Assert the live keyword count is still 214 and none became "
            "ineligible.",
            "Assert budgets, CPC ceilings, bidding, locations, schedules, ads "
            "and assets are all unchanged.",
            "Re-run the search-term classifier after 7 days and confirm the "
            "negatived terms no longer appear as serving."],
        "rollback": (
            "Remove the created negative criteria. No positive keyword, ad, "
            "asset, budget or setting is touched by this plan."),
        "approval_owner": "Walter Correa",
        "approver_email": "access@greenmarketing.com",
    }}

    assert_no_embedded_secrets(plan)
    payload = normalize(plan)
    fp = approval_code(payload)
    plan["change_plan"]["fingerprint"] = fp
    plan["change_plan"]["approval_phrase"] = "APPROVE PLAN-K2 %s FOR %s" % (fp, CID)

    OUT_YAML.write_text(
        "# PLAN-K2 - SEARCH-TERM CLEANING VIA NEGATIVE KEYWORDS\n#\n"
        "# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
        "# Negative keywords go LIVE the instant they are created. There is no\n"
        "# paused state for a negative, so this plan carries its own fingerprint\n"
        "# and needs its own exact approval.\n\n"
        + yaml.safe_dump(plan, sort_keys=False, width=96, allow_unicode=True),
        encoding="utf-8")
    OUT_FP.write_text(json.dumps({
        "generated_account_local": now.isoformat(),
        "plan_id": "PLAN-K2", "plan_file": OUT_YAML.name,
        "fingerprint": fp, "approval_type": "NEGATIVES",
        "action_count": payload["action_count"],
        "object_count": payload["object_count"],
        "approval_status": "NOT APPROVED", "execution_status": "DO NOT EXECUTE",
        "approval_phrase": "APPROVE PLAN-K2 %s FOR %s" % (fp, CID),
        "canonical_payload": payload}, indent=2), encoding="utf-8")

    print("PLAN-K2 built.")
    print("  file        : %s" % OUT_YAML.name)
    print("  fingerprint : %s" % fp)
    print("  actions     : %d   objects: %d   mutations: %d"
          % (payload["action_count"], payload["object_count"], obj))
    print("  approval    : APPROVE PLAN-K2 %s FOR %s" % (fp, CID))
    print()
    print("  K2-01 ad-group EXACT negatives (%d):" % len(AG_NEGATIVES))
    for n in AG_NEGATIVES:
        print("    %-38s -> %-30s [%s] %s"
              % (n["text"], n["ad_group"][:30], n["ad_group_status"],
                 n["confidence"]))
    print("  K2-02 campaign PHRASE negatives (%d objects, both campaigns):"
          % (len(CAMPAIGN_NEGATIVES) * 2))
    for n in CAMPAIGN_NEGATIVES:
        print("    %-38s PHRASE  %s" % (n["text"], n["confidence"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
