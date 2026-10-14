#!/usr/bin/env python3
"""Split PLAN-K2 into PLAN-K2A (unambiguous) and PLAN-K2B (commercial-scope).

PLAN-K2 (57FECB3D6901) is VOIDED: it bundled negatives that the validated work
order settles with negatives that depend on an unanswered client question, and
its narrative carried a wrong click count.

READ ONLY against Google Ads. Writes local plan + fingerprint files only.
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
from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
NAMES = {CAMP_A: "Power Washing", CAMP_B: "Power Washing #2"}
CLIENT = ROOT / "clients/softwind-power-washing"
RECON = CLIENT / "audits/2026-08-27-reconciliation.json"
OUT_A = CLIENT / "plans/2026-08-27-plan-k2a-unambiguous-negatives.yaml"
OUT_B = CLIENT / "plans/2026-08-27-plan-k2b-commercial-scope.yaml"
OUT_FP = CLIENT / "plans/2026-08-27-k2ab-fingerprints.json"

VOIDED_K2 = "57FECB3D6901"

TARGET_ROOF = {"roof cleaning", "roof washing"}
HOUSE_TERM = "house cleaning services near me"
HOUSE_AG = {"id": "202870585910", "name": "House Washing Company Near Me",
            "campaign": CAMP_A, "status": "PAUSED"}
COMMERCIAL_TERMS = [
    {"text": "gas station pressure washing near me", "ad_group_id": "202870585390",
     "ad_group": "Power Washing Near Me", "campaign_id": CAMP_A,
     "ad_group_status": "ENABLED", "impressions": 4, "clicks": 1, "cost": 35.31},
    {"text": "commercial power washing company near me",
     "ad_group_id": "202870585390", "ad_group": "Power Washing Near Me",
     "campaign_id": CAMP_A, "ad_group_status": "ENABLED",
     "impressions": 2, "clicks": 0, "cost": 0.0},
]


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


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)
    recon = json.loads(RECON.read_text(encoding="utf-8"))

    # ---------- fresh collision check ----------
    q = ("SELECT ad_group.id, ad_group.name, ad_group_criterion.keyword.text, "
         "ad_group_criterion.keyword.match_type, ad_group_criterion.status "
         f"FROM ad_group_criterion WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND ad_group_criterion.type = 'KEYWORD' "
         "AND ad_group_criterion.negative = FALSE "
         "AND ad_group_criterion.status != 'REMOVED'")
    live_kw = {}
    for x in rows(svc, q):
        live_kw.setdefault(x.ad_group_criterion.keyword.text.lower(), set()).add(
            str(x.ad_group.id))

    q = ("SELECT campaign.id, ad_group.id, search_term_view.search_term, "
         "metrics.impressions, metrics.clicks, metrics.cost_micros "
         f"FROM search_term_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND segments.date BETWEEN '2026-08-01' AND '%s'"
         % now.strftime("%Y-%m-%d"))
    corpus = {}
    for x in rows(svc, q):
        t = x.search_term_view.search_term
        d = corpus.setdefault(t, {"impressions": 0, "clicks": 0, "cost": 0.0})
        d["impressions"] += x.metrics.impressions
        d["clicks"] += x.metrics.clicks
        d["cost"] = round(d["cost"] + x.metrics.cost_micros / 1e6, 2)

    def collide(text, match):
        """What would this negative block, among live keywords and served terms?"""
        t = text.lower()
        if match == "EXACT":
            kw = [k for k in live_kw if k == t]
            terms = [s for s in corpus if s.lower() == t]
        else:  # PHRASE
            kw = [k for k in live_kw if t in k]
            terms = [s for s in corpus if t in s.lower()]
        return {"live_keywords_blocked": sorted(kw),
                "live_keyword_block_count": len(kw),
                "served_terms_matched": sorted(terms),
                "served_terms_matched_count": len(terms),
                "served_terms_detail": {s: corpus[s] for s in terms}}

    collisions = {}
    for t in sorted(TARGET_ROOF):
        collisions[t + " [PHRASE]"] = collide(t, "PHRASE")
    collisions[HOUSE_TERM + " [EXACT]"] = collide(HOUSE_TERM, "EXACT")
    for c in COMMERCIAL_TERMS:
        collisions[c["text"] + " [EXACT]"] = collide(c["text"], "EXACT")

    # ---------- shared blocks ----------
    reconciliation_block = {
        "why_this_is_here": (
            "The owner challenged the claim '90 of 100 clicks' in PLAN-K2. It was "
            "wrong. This block records the correction and the reconciliation so "
            "the corrected figures travel with the plans."),
        "four_independent_counts": {
            "A_campaign_totals": recon["A_campaign_totals"],
            "B_search_term_view_no_keyword_segment":
                recon["B_search_terms_no_keyword_segment"],
            "C_search_term_view_with_keyword_segment":
                recon["C_search_terms_with_keyword_segment"],
            "D_keyword_view": recon["D_keyword_view_totals"]},
        "is_it_duplication": (
            "NO. B and C return identical impressions, clicks and cost (163 / 10 "
            "/ $318.05) from 58 and 70 rows respectively. The keyword segment "
            "SPLITS metrics across rows, it does not duplicate them."),
        "is_it_a_reporting_defect": (
            "NO. keyword_view (D) reconciles EXACTLY with campaign totals (A) at "
            "196 impressions, 13 clicks, $448.65."),
        "is_it_impressions": (
            "NO. In-scope impressions are 151 of 163, which matches neither 90 "
            "nor 100."),
        "what_it_actually_was": (
            "A transcription error in a hand-written narrative sentence in the "
            "plan builder. The classifier printed the correct '9 clicks' in its "
            "bucket table; the sentence said '90 of 100' and was never re-derived "
            "from the data. TRUE VALUE: 9 of 10 corpus clicks are in scope, and "
            "$282.74 of $318.05 - the COST figures were correct."),
        "the_material_caveat_that_was_missing": (
            "search_term_view is a SUBSET of campaign activity. It covers 76.9% "
            "of clicks and 83.2% of impressions; the gap is 33 impressions, 3 "
            "clicks and $130.60 that Google withholds below its privacy "
            "threshold, plus same-day lag. Corpus percentages are therefore NOT "
            "account-wide percentages, and with a base of only 10 corpus clicks "
            "every percentage drawn from it carries wide uncertainty. PLAN-K2 "
            "presented corpus shares as if they described the account. They do "
            "not."),
        "does_the_conclusion_survive": (
            "Yes, but stated more carefully. The in-scope share of the VISIBLE "
            "corpus is 90% of clicks and 88.9% of cost. The direction is "
            "unchanged - this account is starved of volume, not drowning in junk "
            "- but it rests on 10 observed clicks, not 100, so it is a weak-"
            "evidence conclusion and is labelled as one."),
        "evidence": "audits/2026-08-27-reconciliation.json"}

    target = {"exact_child_account_name": NAME, "child_customer_id": CID,
              "manager_customer_id": "3373711342", "exact_service": "Power Washing",
              "vertical": "similar-local-service"}

    # ================= PLAN-K2A =================
    a_actions = []
    a_actions.append({
        "action_id": "K2A-01", "priority": "P1",
        "resource_type": "AD_GROUP_CRITERION", "operation": "CREATE_NEGATIVE",
        "customer_id": CID, "campaign_id": HOUSE_AG["campaign"],
        "ad_group_id": HOUSE_AG["id"],
        "resource_id": "ad_group %s negative keyword" % HOUSE_AG["id"],
        "current_value": "not present as a negative in this ad group",
        "proposed_value": {"keyword_text": HOUSE_TERM, "match_type": "EXACT",
                           "negative": True},
        "ad_group_name": HOUSE_AG["name"], "ad_group_status": HOUSE_AG["status"],
        "scope": "AD GROUP - %s (%s), campaign %s"
                 % (HOUSE_AG["name"], HOUSE_AG["id"], NAMES[HOUSE_AG["campaign"]]),
        "why": ("'House cleaning services' with no exterior qualifier reads as "
                "interior maid service, against a /house-washing-company/ "
                "exterior landing page. Contrast 'outdoor house cleaning services "
                "near me', which is KEPT because 'outdoor' resolves it to the "
                "approved service."),
        "caveat": ("This ad group is PAUSED, so the negative is inert today. It "
                   "is added as hygiene so the term cannot serve if the ad group "
                   "is re-enabled. If you want it to bite immediately regardless "
                   "of ad-group state, say so and I will re-scope it to campaign "
                   "level as EXACT - equally narrow, wider protection."),
        "collision": collisions[HOUSE_TERM + " [EXACT]"],
        "rollback": "Remove the ad_group_criterion negative.",
        "object_count": 1})
    i = 2
    for t in sorted(TARGET_ROOF):
        for cid_ in (CAMP_A, CAMP_B):
            a_actions.append({
                "action_id": "K2A-%02d-%s" % (i, cid_[-4:]), "priority": "P1",
                "resource_type": "CAMPAIGN_CRITERION",
                "operation": "CREATE_NEGATIVE",
                "customer_id": CID, "campaign_id": cid_, "ad_group_id": None,
                "resource_id": "campaign %s negative keyword" % cid_,
                "current_value": "not present as a campaign negative",
                "proposed_value": {"keyword_text": t, "match_type": "PHRASE",
                                   "negative": True},
                "scope": "CAMPAIGN - %s (%s)" % (NAMES[cid_], cid_),
                "why": ("Roof cleaning is confirmed OUT OF SCOPE by the validated "
                        "work order, not by inference - see "
                        "scope_confirmation below."),
                "collision": collisions[t + " [PHRASE]"],
                "rollback": "Remove the campaign_criterion negative.",
                "object_count": 1})
        i += 1

    plan_a = {"change_plan": {
        "plan_id": "PLAN-K2A",
        "plan_title": "Unambiguous negatives - interior cleaning and roof cleaning",
        "approval_type": "NEGATIVES",
        "priority": "P1",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "ads_mutation_count": len(a_actions),
        "supersedes": {"plan_id": "PLAN-K2", "fingerprint": VOIDED_K2,
                       "status": "VOID",
                       "reason": ("Bundled negatives settled by the validated "
                                  "work order with negatives that depend on an "
                                  "unanswered client question, and its narrative "
                                  "carried a click count that was wrong by 10x.")},
        "goes_live_immediately": (
            "YES. Negative keywords take effect the moment they are created. "
            "There is no paused state for a negative."),
        "target": target,
        "scope_confirmation": {
            "question": "Is roof cleaning confirmed out of scope?",
            "answer": "YES - CONFIRMED BY THE VALIDATED WORK ORDER, not inferred.",
            "evidence": [
                "clients/softwind-power-washing/work-order.yaml -> "
                "service.excluded_services includes 'roof cleaning'",
                "clients/softwind-power-washing/client.yaml -> "
                "offer.services_excluded includes 'Roof Cleaning'"],
            "consequence": ("The roof negatives are therefore included in K2A "
                            "rather than held for confirmation.")},
        "match_type_note": (
            "The two roof negatives are PHRASE, following the owner's own "
            "quoting. PHRASE is correct here because the excluded thing is a "
            "THEME, not one query: 'roof cleaning' PHRASE catches both observed "
            "roof terms ('slate roof cleaning near me' and, with 'roof washing', "
            "'roof washing near me') and any future variant, which five separate "
            "EXACT negatives could not. The interior-cleaning negative stays "
            "EXACT because only that one precise query is out of scope - "
            "'outdoor house cleaning services near me' must keep serving."),
        "reconciliation_and_correction": reconciliation_block,
        "deliberately_kept": [
            {"term": "outdoor house cleaning services near me", "verdict": "KEEP",
             "why": "'outdoor' resolves it to exterior washing, the approved service."},
            {"term": "jet wash near me", "verdict": "KEEP / KEYWORD CANDIDATE",
             "why": ("'Jet wash' is a synonym for pressure washing, not an "
                     "out-of-scope intent. It reaches the account only via close "
                     "variant today and is a keyword opportunity.")}],
        "actions": a_actions,
        "change_counts": {
            "ad_group_negatives_added": 1, "campaign_negatives_added": 4,
            "budgets_changed": 0, "bidding_settings_changed": 0,
            "keywords_changed": 0, "ads_changed": 0, "assets_changed": 0,
            "locations_changed": 0, "schedules_changed": 0,
            "conversion_actions_changed": 0,
            "google_ads_mutations_total": len(a_actions)},
        "readback_qa": [
            "Assert 1 new ad_group_criterion negative on ad group 202870585910.",
            "Assert campaign negatives go 94 -> 98 (4 added, 2 per campaign).",
            "Assert live keyword count is still 214 and none became ineligible.",
            "Assert budgets, CPC ceilings, bidding, locations, schedules, ads and "
            "assets are unchanged.",
            "Re-run the classifier after 7 days; negatived terms must show as "
            "excluded and must not serve."],
        "rollback": "Remove the created negative criteria. Nothing else is touched.",
        "approval_owner": "Walter Correa",
        "approver_email": "access@greenmarketing.com"}}

    # ================= PLAN-K2B =================
    b_actions = []
    for n, c in enumerate(COMMERCIAL_TERMS, 1):
        b_actions.append({
            "action_id": "K2B-%02d" % n, "priority": "P2",
            "resource_type": "AD_GROUP_CRITERION", "operation": "CREATE_NEGATIVE",
            "customer_id": CID, "campaign_id": c["campaign_id"],
            "ad_group_id": c["ad_group_id"],
            "resource_id": "ad_group %s negative keyword" % c["ad_group_id"],
            "current_value": "not present as a negative in this ad group",
            "proposed_value": {"keyword_text": c["text"], "match_type": "EXACT",
                               "negative": True},
            "ad_group_name": c["ad_group"], "ad_group_status": c["ad_group_status"],
            "scope": "AD GROUP - %s (%s), campaign %s"
                     % (c["ad_group"], c["ad_group_id"], NAMES[c["campaign_id"]]),
            "observed": {"impressions": c["impressions"], "clicks": c["clicks"],
                         "cost": c["cost"]},
            "collision": collisions[c["text"] + " [EXACT]"],
            "rollback": "Remove the ad_group_criterion negative.",
            "object_count": 1})

    plan_b = {"change_plan": {
        "plan_id": "PLAN-K2B",
        "plan_title": "Commercial-scope decision - gas station and commercial queries",
        "approval_type": "NEGATIVES",
        "priority": "P2",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE - BLOCKED ON CLIENT CONFIRMATION",
        "ads_mutation_count": len(b_actions),
        "supersedes": {"plan_id": "PLAN-K2", "fingerprint": VOIDED_K2,
                       "status": "VOID"},
        "target": target,
        "blocked_on": [
            "K1-W2: does Softwind accept COMMERCIAL power washing work "
            "(gas stations, storefronts, lots, HOA, fleet)?"],
        "blocking_rule": (
            "This plan MUST NOT execute until that question is answered. "
            "Negativing commercial intent while Softwind actually sells it would "
            "destroy real revenue; leaving it live while Softwind does NOT sell "
            "it keeps buying clicks like the $35.31 gas-station click against a "
            "residential landing page. The cost of guessing wrong is asymmetric "
            "in both directions, so it is a client decision, not a technical one."),
        "two_branches": {
            "branch_1_commercial_NOT_accepted": {
                "verdict": "EXECUTE the two negatives in actions below",
                "match_type_rationale": (
                    "EXACT, not PHRASE. Even when commercial is out of scope, a "
                    "broad 'commercial' PHRASE negative would also block "
                    "'commercial' appearing incidentally. Start with the two "
                    "observed queries; widen only on evidence."),
                "follow_up": ("Re-run the classifier weekly; if further commercial "
                              "variants appear, propose a PHRASE negative then.")},
            "branch_2_commercial_IS_accepted": {
                "verdict": "VOID this plan. Do NOT create these negatives.",
                "reclassification": [
                    {"term": "gas station pressure washing near me",
                     "new_verdict": "KEEP",
                     "note": ("It already took a real click at $35.31. If "
                              "commercial is sold, that was a LEAD, not waste - "
                              "and the conversion simply had nowhere to land.")},
                    {"term": "commercial power washing company near me",
                     "new_verdict": "NEW KEYWORD CANDIDATE",
                     "note": ("Strong BOFU commercial intent with an explicit "
                              "'company near me' modifier. Would justify its own "
                              "SKAG.")}],
                "required_before_serving_commercial_traffic": (
                    "A commercial landing page. Every current offer page is "
                    "residential - house washing, driveways, patios. Sending "
                    "commercial queries to a residential page is the message "
                    "mismatch that makes these clicks expensive regardless of "
                    "whether the service is sold."),
                "would_require": "A new plan: ad group, keywords, RSAs, landing page."},
        },
        "reconciliation_and_correction": reconciliation_block,
        "actions": b_actions,
        "change_counts": {
            "ad_group_negatives_added": len(b_actions),
            "campaign_negatives_added": 0,
            "budgets_changed": 0, "bidding_settings_changed": 0,
            "keywords_changed": 0, "ads_changed": 0, "assets_changed": 0,
            "google_ads_mutations_total": len(b_actions)},
        "rollback": "Remove the created negative criteria.",
        "approval_owner": "Walter Correa",
        "approver_email": "access@greenmarketing.com"}}

    out = {}
    for plan, path, label in ((plan_a, OUT_A, "PLAN-K2A"),
                              (plan_b, OUT_B, "PLAN-K2B")):
        assert_no_embedded_secrets(plan)
        payload = normalize(plan)
        fp = approval_code(payload)
        plan["change_plan"]["fingerprint"] = fp
        plan["change_plan"]["approval_phrase"] = (
            "APPROVE %s %s FOR %s" % (label, fp, CID))
        hdr = ("# %s\n#\n# STATUS: NOT APPROVED. DO NOT EXECUTE.\n"
               "# Supersedes PLAN-K2 (%s), now VOID.\n"
               "# Negative keywords go LIVE on creation - there is no paused state.\n\n"
               % (label, VOIDED_K2))
        if label == "PLAN-K2B":
            hdr += ("# ADDITIONALLY BLOCKED on K1-W2: does Softwind accept\n"
                    "# commercial power washing work? Do not execute either way\n"
                    "# until that is answered.\n\n")
        path.write_text(hdr + yaml.safe_dump(plan, sort_keys=False, width=96,
                                             allow_unicode=True), encoding="utf-8")
        out[label] = {"fingerprint": fp, "file": path.name,
                      "actions": payload["action_count"],
                      "objects": payload["object_count"],
                      "approval_phrase": plan["change_plan"]["approval_phrase"]}

    out["voided"] = {"plan_id": "PLAN-K2", "fingerprint": VOIDED_K2,
                     "status": "VOID", "voided_on": now.isoformat()}
    out["collision_check"] = collisions
    OUT_FP.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("PLAN-K2 %s is VOID. Split into K2A and K2B.\n" % VOIDED_K2)
    for label in ("PLAN-K2A", "PLAN-K2B"):
        d = out[label]
        print("%s  fingerprint %s  actions %d  objects %d  mutations %d"
              % (label, d["fingerprint"], d["actions"], d["objects"], d["objects"]))
        print("   %s" % d["approval_phrase"])
    print("\nCOLLISION CHECK (fresh):")
    for k, v in collisions.items():
        print("   %-46s live_kw_blocked=%d  served_terms_matched=%d %s"
              % (k, v["live_keyword_block_count"], v["served_terms_matched_count"],
                 v["served_terms_matched"] if v["served_terms_matched"] else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
