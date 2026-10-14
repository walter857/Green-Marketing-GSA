#!/usr/bin/env python3
"""Split PLAN-E into E1 (create-paused only) and E2 (live negatives only).

Generated programmatically from the source plan so the SKAG and RSA content is
carried over byte-for-byte rather than retyped. Local file operation only.
"""
from __future__ import annotations

import json
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "clients/softwind-power-washing/plans"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
SRC = PLANS / "2026-08-25-plan-e-create-paused-expansion.yaml"

src = yaml.safe_load(SRC.read_text(encoding="utf-8"))["change_plan"]
drift = json.loads((SNAP / "drift-check-2026-08-25b.json").read_text(encoding="utf-8"))
deep = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
AG = {a["id"]: a for a in deep["ad_groups"]}
LIVE_KW = {k["text"] for k in deep["keywords"]
           if k["status"] == "ENABLED" and AG[k["ad_group_id"]]["status"] == "ENABLED"}

VOID = {"plan_id": "PLAN-E", "fingerprint": "F453AD249497", "status": "VOID"}
TARGET = src["target"]

# ---------------------------------------------------------------- E1
e1_actions = [a for a in src["actions"]
              if a["action_id"] in ("P1-E01", "P1-E02", "P1-E03",
                                    "P1-E04", "P1-E05", "P1-E06")]
e1 = {
    "change_plan": {
        "plan_id": "PLAN-E1",
        "plan_title": "Create paused - Pressure Washing Near Me and House Washing Near Me",
        "approval_type": "CREATE_PAUSED",
        "priority": "P1",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "recommended_approval_order": 7,
        "ads_mutation_count": sum(a["object_count"] for a in e1_actions),
        "requires_separate_enable_approval": True,
        "supersedes": VOID,
        "split_rationale": (
            "PLAN-E incorrectly combined resources created PAUSED (which cannot "
            "serve until a second enable approval) with negative keywords that go "
            "LIVE the instant they are created. Those are different risk classes "
            "and different approval gates, so they must never share a fingerprint. "
            "The negatives now live in PLAN-E2."),
        "contains_no_live_changes": (
            "Every object in this plan is created PAUSED or is a child of a paused "
            "ad group. Nothing in this plan can serve an impression."),
        "target": TARGET,
        "ownership_rule": src["ownership_rule"],
        "skag_1": src["skag_1"],
        "skag_2": src["skag_2"],
        "rsa_validation": src["rsa_validation"],
        "rsas": src["rsas"],
        "cross_campaign_check": src["cross_campaign_check"],
        "candidates_researched_and_rejected": src["candidates_researched_and_rejected"],
        "actions": e1_actions,
        "post_creation_requirements": [
            "READBACK QA: re-read every created resource from the API and compare "
            "against this plan before any enable is proposed.",
            "SEPARATE ENABLE APPROVAL: creation does not authorise delivery. "
            "Enabling these two ad groups is a second approval with its own "
            "fingerprint.",
            "PLAN-E2 (the three out-of-scope negatives) should be approved BEFORE "
            "these ad groups are enabled, not before they are created.",
        ],
        "change_counts": {
            "campaigns_changed": 0, "campaigns_paused": 0, "budgets_changed": 0,
            "bidding_settings_changed": 0, "ad_schedules_changed": 0,
            "ad_groups_enabled": 0, "ad_groups_created_paused": 2,
            "keywords_enabled": 0, "keywords_created_paused": 4,
            "rsas_created_paused": 4, "ads_changed": 0,
            "negatives_added": 0, "assets_changed": 0, "final_urls_changed": 0,
            "conversion_actions_changed": 0,
            "google_ads_mutations_total": sum(a["object_count"] for a in e1_actions),
            "objects_that_can_serve_immediately": 0,
        },
        "approval_owner": src["approval_owner"],
        "approver_email": src["approver_email"],
    }
}

# ---------------------------------------------------------------- E2
NEG = [
    ("roof cleaning", "PHRASE", r"roof\s*clean"),
    ("roof washing", "PHRASE", r"roof\s*wash"),
    ("house cleaning", "PHRASE", r"house\s*clean"),
]
CAMPS = [("24103511039", "Power Washing"), ("24145053510", "Power Washing #2")]

REASONS = {
    "roof cleaning": (
        "Roof cleaning is explicitly listed under services_excluded in "
        "work-order.yaml and client.yaml. It is outside the approved Power "
        "Washing scope for this work order and Softwind is not being advertised "
        "for it."),
    "roof washing": (
        "Same out-of-scope service, different phrasing. 'roof washing near me' "
        "reached the account through the power washing company near me PHRASE "
        "keyword, so the phrasing is demonstrably reachable."),
    "house cleaning": (
        "'house cleaning' reads as interior maid service, a different industry "
        "entirely. It is not exterior house washing and Softwind does not offer "
        "it."),
}
RISKS = {
    "roof cleaning": (
        "LOW. A PHRASE negative matches only the exact word sequence 'roof "
        "cleaning'. It cannot block any live keyword - all 11 live keyword texts "
        "were checked and none contains both words. The residual risk is a query "
        "like 'house and roof cleaning near me' from a homeowner who wants both "
        "services; that query would be blocked, and the house-washing half of the "
        "job would be lost. Given roof cleaning is out of scope and cannot be "
        "quoted, that is an acceptable trade."),
    "roof washing": (
        "LOW. Same mechanics. Residual risk is a combined 'roof and house "
        "washing' query, same trade-off as above."),
    "house cleaning": (
        "LOW-MEDIUM, and the one worth watching. A PHRASE negative on 'house "
        "cleaning' will NOT block 'house washing' - different words - and none of "
        "the 11 live keyword texts contains both 'house' and 'cleaning'. But if a "
        "future SKAG ever used the phrasing 'exterior house cleaning', which is a "
        "legitimate service phrasing, this negative would block it. If PLAN-E1's "
        "House Washing Near Me SKAG is later extended with cleaning phrasing, "
        "revisit this negative first."),
}

e2_actions = []
for i, (cid, cname) in enumerate(CAMPS, start=1):
    for j, (text, mt, rx) in enumerate(NEG, start=1):
        hits = [s for s in drift["search_terms_now"]
                if re.search(rx, s["search_term"], re.I)]
        blocked = [t for t in LIVE_KW
                   if all(w in t.split() for w in text.split())]
        e2_actions.append({
            "action_id": "P1-E2-%02d" % ((i - 1) * 3 + j),
            "priority": "P1",
            "resource_type": "CAMPAIGN_CRITERION",
            "operation": "CREATE_NEGATIVE_KEYWORD",
            "customer_id": TARGET["child_customer_id"],
            "campaign_id": cid,
            "campaign_name": cname,
            "ad_group_id": None,
            "resource_id": "NEW negative keyword",
            "exact_term": text,
            "match_type": mt,
            "level": "CAMPAIGN",
            "current_value": ("47 campaign negatives on this campaign; none blocks "
                              "this term"),
            "proposed_value": {"text": text, "match_type": mt, "negative": True},
            "current_matching_search_terms": [
                {"search_term": h["search_term"], "impressions": h["impressions"],
                 "clicks": h["clicks"], "cost": round(h["cost"], 2),
                 "matched_keyword": h["matched_keyword"],
                 "ad_group": h["ad_group"], "campaign": h["campaign"]}
                for h in hits] or "none observed to date on this campaign",
            "why": REASONS[text],
            "risk_of_blocking_valid_demand": RISKS[text],
            "live_keywords_this_negative_would_block": blocked or "NONE - verified against all 11 live keyword texts",
            "goes_live_immediately": True,
            "expected_effect": ("Blocks a small number of out-of-scope impressions. "
                                "Total observed exposure across the whole account "
                                "is 4 impressions and 0 clicks, so the measurable "
                                "saving is near zero; the value is preventing "
                                "out-of-scope spend as volume grows."),
            "rollback": ("Remove the campaign_criterion. Negative keywords are "
                         "removable in one operation and leave no residue. "
                         "Delivery on the previously-blocked queries resumes "
                         "immediately."),
            "approval_required": ("YES - LIVE CHANGE. These take effect the moment "
                                  "they are created; they are not paused resources."),
            "object_count": 1,
        })

e2 = {
    "change_plan": {
        "plan_id": "PLAN-E2",
        "plan_title": "Live out-of-scope negative keywords (3 terms x 2 campaigns)",
        "approval_type": "LIVE_NEGATIVE_KEYWORDS",
        "priority": "P1",
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "recommended_approval_order": 6,
        "ads_mutation_count": len(e2_actions),
        "requires_separate_enable_approval": False,
        "supersedes": VOID,
        "split_rationale": (
            "Separated from PLAN-E1 because a negative keyword goes LIVE the "
            "instant it is created. It is not a paused resource and it has no "
            "second enable gate, so bundling it with create-paused work would "
            "have let one approval authorise an immediate delivery change."),
        "immediate_effect_warning": (
            "Every action in this plan changes live delivery on creation. There "
            "is no paused intermediate state and no second approval gate."),
        "target": TARGET,
        "policy_check": (
            "Green Marketing policy forbids auto-negativing near me, quote, "
            "price, pricing, cost, best, hire, local and emergency "
            "(config/agency.yaml negative_keyword_policy.protected_terms). NONE "
            "of those appears here. All three terms are out-of-scope SERVICES, "
            "not buyer-intent modifiers."),
        "not_proposed_as_negatives": (
            "The cost-research cluster - average cost to power wash a house, "
            "powerwash cost, cost to power wash, price to powerwash house, how "
            "much is powerwashing a house - carries 36% of all account spend "
            "across 2 clicks with no lead. It stays WATCH, not NEGATIVE. Two "
            "clicks prove nothing and agency policy protects cost terms."),
        "separate_observation": (
            "The existing campaign negative 'how to' is at BROAD match, so it "
            "blocks any query containing both 'how' and 'to' - including 'how "
            "much does it cost TO power wash a house'. Narrowing it to PHRASE is "
            "a real improvement but it modifies an EXISTING negative rather than "
            "adding one, so it is deliberately excluded from this plan."),
        "actions": e2_actions,
        "verification_after_execution": [
            "Read back campaign_criterion on both campaigns and assert 50 negative "
            "keywords each (47 existing + 3 new).",
            "Re-check the search terms report after 7 days and confirm no in-scope "
            "query disappeared.",
        ],
        "change_counts": {
            "campaigns_changed": 0, "campaigns_paused": 0, "budgets_changed": 0,
            "bidding_settings_changed": 0, "ad_schedules_changed": 0,
            "ad_groups_enabled": 0, "ad_groups_created_paused": 0,
            "keywords_enabled": 0, "keywords_created_paused": 0,
            "rsas_created_paused": 0, "ads_changed": 0,
            "negatives_added": len(e2_actions),
            "assets_changed": 0, "final_urls_changed": 0,
            "conversion_actions_changed": 0,
            "google_ads_mutations_total": len(e2_actions),
            "objects_that_go_live_immediately": len(e2_actions),
        },
        "approval_owner": src["approval_owner"],
        "approver_email": src["approver_email"],
    }
}

HDR_E1 = """# PLAN-E1 - CREATE-PAUSED SKAGS ONLY
#
# STATUS: NOT APPROVED. DO NOT EXECUTE.
# SUPERSEDES PLAN-E (fingerprint F453AD249497, now VOID).
#
# Contains ONLY resources created PAUSED. Nothing in this plan can serve an
# impression. The three negative keywords that were wrongly bundled into PLAN-E
# have been moved to PLAN-E2, because a negative goes live on creation.
#
# Creating is one approval. ENABLING the result is a SECOND approval after
# readback QA.

"""
HDR_E2 = """# PLAN-E2 - LIVE NEGATIVE KEYWORDS
#
# STATUS: NOT APPROVED. DO NOT EXECUTE.
# SUPERSEDES PLAN-E (fingerprint F453AD249497, now VOID).
#
# EVERY ACTION HERE GOES LIVE ON CREATION. There is no paused state and no
# second enable gate. Split out of PLAN-E for exactly that reason.

"""

(PLANS / "2026-08-26-plan-e1-create-paused-skags.yaml").write_text(
    HDR_E1 + yaml.safe_dump(e1, sort_keys=False, width=88, allow_unicode=True),
    encoding="utf-8")
(PLANS / "2026-08-26-plan-e2-live-negative-keywords.yaml").write_text(
    HDR_E2 + yaml.safe_dump(e2, sort_keys=False, width=88, allow_unicode=True),
    encoding="utf-8")

print("wrote PLAN-E1: %d actions, %d objects"
      % (len(e1_actions), sum(a["object_count"] for a in e1_actions)))
print("wrote PLAN-E2: %d actions, %d objects"
      % (len(e2_actions), sum(a["object_count"] for a in e2_actions)))
for a in e2_actions:
    print("   %-11s %-16s %-8s %s" % (a["action_id"], a["exact_term"],
                                      a["match_type"], a["campaign_name"]))
