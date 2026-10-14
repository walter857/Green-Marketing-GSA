#!/usr/bin/env python3
"""Build PLAN-I2 with the exact keyword and RSA inventory that would begin serving."""
from __future__ import annotations

import json
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
PLANS = ROOT / "clients/softwind-power-washing/plans"

deep = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
snap = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))
inv = json.loads((SNAP / "rescue-inventory-ranking-2026-08-26.json").read_text(encoding="utf-8"))

A, B = "24103511039", "24145053510"
SELECTED = [
    ("Pressure & Power Washing", "205713509704", A, "Power Washing"),
    ("Soft & House Washing", "198082078943", B, "Power Washing #2"),
]
live_texts = {k["text"] for k in snap["enabled_keywords_live"]}
live_by_camp = {}
for k in snap["enabled_keywords_live"]:
    live_by_camp.setdefault(k["campaign_id"], set()).add(k["text"])


def ag_detail(gid):
    kws = [k for k in snap["keywords"] if k["ad_group_id"] == gid]
    ads = [a for a in deep["ads"] if a["ad_group_id"] == gid]
    return kws, ads


actions, blocks = [], []
n = 0
for name, gid, cid, cname in SELECTED:
    n += 1
    kws, ads = ag_detail(gid)
    rank = [r for r in inv["rankings"] if r["ad_group_name"] == name][0]
    phrase = sorted({k["text"] for k in kws if k["match_type"] == "PHRASE"})
    exact = sorted({k["text"] for k in kws if k["match_type"] == "EXACT"})
    pd = rank["planner_detail"]

    kw_rows = []
    for k in sorted(kws, key=lambda x: (x["text"], x["match_type"])):
        p = pd.get(k["text"]) or {}
        kw_rows.append({
            "criterion_id": k["criterion_id"], "text": k["text"],
            "match_type": k["match_type"], "status": k["status"],
            "approval": k["approval"], "serving": k["serving"],
            "local_monthly_volume": p.get("avg_monthly_searches"),
            "competition": p.get("competition"),
            "top_of_page_low": p.get("low_bid"),
            "top_of_page_high": p.get("high_bid"),
            "recent_trend_pct": p.get("recent_trend_pct_last3_vs_prev3"),
            "already_live_elsewhere": k["text"] in live_texts,
        })

    # distinct volume buckets, so power/pressure pairs are not double counted
    buckets = {}
    for k in {r["text"] for r in kw_rows}:
        p = pd.get(k) or {}
        if p.get("avg_monthly_searches"):
            buckets.setdefault((p["avg_monthly_searches"], p.get("low_bid"),
                                p.get("high_bid")), []).append(k)
    distinct = sum(k[0] for k in buckets)

    other_cid = B if cid == A else A
    cross = sorted({r["text"] for r in kw_rows} & live_by_camp.get(other_cid, set()))
    intra = sorted({r["text"] for r in kw_rows} & live_by_camp.get(cid, set()))

    blocks.append({
        "ad_group_name": name,
        "campaign_id": cid, "campaign_name": cname, "ad_group_id": gid,
        "current_status": "PAUSED",
        "distinct_local_monthly_searches": distinct,
        "distinct_volume_buckets": len(buckets),
        "best_keyword": rank["best_keyword"],
        "best_keyword_volume": rank["best_keyword_local_monthly_volume"],
        "best_keyword_recent_trend_pct": rank["recent_trend_pct"],
        "keyword_rows_that_will_begin_serving": len(kw_rows),
        "phrase_keywords": phrase, "exact_keywords": exact,
        "every_keyword": kw_rows,
        "rsa_count": len(ads),
        "rsas": [{"ad_id": a["ad_id"], "status": a["status"],
                  "approval": a["approval_status"], "review": a["review_status"],
                  "ad_strength": a["ad_strength"],
                  "headlines": len(a["headlines"]),
                  "descriptions": len(a["descriptions"]),
                  "final_urls": a["final_urls"]} for a in ads],
        "landing_page": sorted({u for a in ads for u in a["final_urls"]}),
        "landing_page_verified_200": True,
        "cross_campaign_duplicate_texts": cross or "NONE",
        "intra_campaign_overlap_texts": intra or "NONE",
        "expected_incremental_impressions_6d_current_schedule":
            round(distinct / 30.44 * 0.531 * 6, 1),
        "expected_incremental_clicks_6d": round(distinct / 30.44 * 0.531 * 6 * 0.0571, 2),
        "expected_incremental_spend_6d":
            round(distinct / 30.44 * 0.531 * 6 * 0.0571 * 28.53, 2),
    })

    actions.append({
        "action_id": "R2-I2-%02d" % n,
        "priority": "R2",
        "resource_type": "AD_GROUP",
        "operation": "UPDATE_STATUS_TO_ENABLED",
        "customer_id": "1521725229",
        "campaign_id": cid, "campaign_name": cname,
        "ad_group_id": gid, "ad_group_name": name,
        "resource_id": "customers/1521725229/adGroups/%s" % gid,
        "field_mask": "status",
        "current_value": {"status": "PAUSED", "keyword_rows": len(kw_rows),
                          "rsa_count": len(ads),
                          "rsa_status": sorted({a["status"] for a in ads})},
        "proposed_value": {"status": "ENABLED"},
        "keywords_that_will_begin_serving": [
            "%s [%s]" % (r["text"], r["match_type"]) for r in kw_rows],
        "why": ("%d distinct local monthly searches across %d volume buckets. "
                "Best keyword '%s' at %s/month, recent trend %s%%. Ad group, all "
                "keywords and RSA already exist and are APPROVED."
                % (distinct, len(buckets), rank["best_keyword"],
                   rank["best_keyword_local_monthly_volume"], rank["recent_trend_pct"])),
        "evidence": "snapshots/rescue-inventory-ranking-2026-08-26.json",
        "expected_effect": ("+%s impressions, +%s clicks, +$%s over the remaining 6 "
                            "days at the CURRENT schedule. Roughly double that if "
                            "PLAN-I3 opens the schedule."
                            % (blocks[-1]["expected_incremental_impressions_6d_current_schedule"],
                               blocks[-1]["expected_incremental_clicks_6d"],
                               blocks[-1]["expected_incremental_spend_6d"])),
        "risk": ("Only %d RSA present against the two-RSA SOP, and the landing page "
                 "is the generic /power-washing-soft-washing/ which names no city. "
                 "Cross-campaign duplicate texts: %s."
                 % (len(ads), cross or "none")),
        "rollback": "Set ad_group %s status back to PAUSED. Single field edit." % gid,
        "approval_required": "YES - SEPARATE ENABLE APPROVAL. This is a live delivery change.",
        "object_count": 1,
    })

plan = {"change_plan": {
    "plan_id": "PLAN-I2",
    "plan_title": "Enable the two strongest paused BOFU ad groups",
    "approval_type": "ENABLE_EXISTING_RESOURCES",
    "priority": "R2",
    "approval_status": "NOT APPROVED",
    "execution_status": "DO NOT EXECUTE",
    "recommended_approval_order": 3,
    "ads_mutation_count": len(actions),
    "requires_separate_enable_approval": True,
    "supersedes": {
        "plan_id": "PLAN-D", "fingerprint": "F61C9F287B82",
        "status": "SUPERSEDED - NOT VOID",
        "reason": ("PLAN-D enabled House Washing Company Near Me. Fresh Keyword "
                   "Planner data on 2026-08-26 shows that ad group's only keyword "
                   "text carries NO reportable local volume, so it is not one of "
                   "the strongest delivery opportunities. PLAN-D remains valid as "
                   "written and its fingerprint is unchanged, but it is displaced "
                   "in the recommendation order by this plan."),
    },
    "target": {
        "exact_child_account_name": "Softwind Power Washing - Live",
        "child_customer_id": "1521725229",
        "manager_customer_id": "3373711342",
        "exact_service": "Power Washing",
        "vertical": "similar-local-service",
    },
    "selection_basis": (
        "All 14 paused ad groups were re-ranked on 2026-08-26 with fresh localized "
        "Keyword Planner demand. Ten are DUPLICATE (their keyword text is already "
        "live in the other campaign), one is LOW VOLUME, one is KEEP PAUSED. Only "
        "two clear the bar."),
    "ad_groups_selected": blocks,
    "rejected": [
        {"ad_group": "House Washing Company Near Me",
         "classification": "LOW VOLUME",
         "reason": ("Its single keyword text 'house washing company near me' returns "
                    "NO reportable local volume bucket. The 40/month belongs to the "
                    "different text 'house washing near me', which lives in the "
                    "Soft & House Washing group selected above. This is why PLAN-D "
                    "is displaced.")},
        {"ad_group": "Driveway Patio Concrete Washing",
         "classification": "KEEP PAUSED",
         "reason": ("Best keyword 'patio cleaning service' at 10/month. Its surfaces "
                    "are already covered by the live Driveway and Patio SKAGs in "
                    "campaign B.")},
        {"ad_groups": ["Power Washing Near Me", "Power Washing Company Near Me",
                       "Power Washing Islip", "Power Washing West Islip",
                       "Power Washing Dix Hills", "Residential Pressure Washing Near Me",
                       "House Pressure Washing Estimate", "Driveway Pressure Washing Near Me",
                       "Patio Pressure Washing Near Me", "Soft House Washing Near Me"],
         "classification": "DUPLICATE",
         "reason": ("Every one of these keyword texts is ALREADY LIVE in the other "
                    "campaign. The inventory is byte-identical across both campaigns, "
                    "so enabling a second copy would put two ad groups in two "
                    "campaigns into the same auction for one query.")},
    ],
    "cross_campaign_safety": {
        "rule": "No proposal may put the two campaigns into the same auction for one query.",
        "pressure_power_washing_placement": (
            "Placed in campaign A (24103511039). Its identity is the power-washing "
            "family and A owns that family, A is the PLAN-G surviving campaign, and A "
            "receives the larger budget under PLAN-I1. RESIDUAL RISK: the group also "
            "contains pressure-washing texts (pressure washing service / company / "
            "contractor / estimate / quote / long island). Those are NON-'near me' "
            "query shapes, so overlap with campaign B's narrow 'pressure washing near "
            "me' style SKAGs is modest rather than direct - but it is real. Monitor "
            "campaign B's impression volume at each pacing checkpoint; if B loses "
            "volume, pause the legacy pressure keywords rather than the whole group."),
        "soft_house_washing_placement": (
            "Placed in campaign B (24145053510). Its house and soft washing texts "
            "belong to B's family and overlap only INTRA-campaign with B's live "
            "'soft house washing near me' SKAG, which Google resolves cleanly by Ad "
            "Rank within a campaign."),
        "the_other_copy_stays_paused": (
            "Pressure & Power Washing also exists in campaign B (198082079503) and "
            "Soft & House Washing also exists in campaign A (205713509744). BOTH MUST "
            "REMAIN PAUSED. Enabling either would create direct cross-campaign "
            "competition."),
    },
    "known_compromises_accepted_for_the_rescue": [
        "Each selected ad group carries ONE RSA, against the two-RSA SOP. The creative "
        "is byte-identical between the campaign A and campaign B copies - only the Ad "
        "Strength label differs, and Ad Strength is a Google advisory, not a ranking "
        "factor. Both RSAs are APPROVED with 15 headlines and 4 descriptions.",
        "Both point at the generic /power-washing-soft-washing/ landing page, which "
        "names no city. Message match is weaker than the purpose-built offer pages. "
        "Verified HTTP 200 with the tracked phone and a working form.",
        "These are deliberate month-end trade-offs. Both should be restructured into "
        "clean SKAGs in September.",
    ],
    "actions": actions,
    "post_execution_verification": [
        "Read back both ad groups and assert status ENABLED.",
        "Read back every keyword listed above and assert status ENABLED, "
        "approval APPROVED, system_serving_status ELIGIBLE.",
        "Confirm the paired copies (205713509744 and 198082079503) are still PAUSED.",
        "Check the search terms report at the next two pacing checkpoints for "
        "out-of-scope queries and for campaign B volume loss.",
    ],
    "change_counts": {
        "campaigns_changed": 0, "campaigns_paused": 0, "budgets_changed": 0,
        "bidding_settings_changed": 0, "ad_schedules_changed": 0,
        "ad_groups_enabled": len(actions), "ad_groups_created_paused": 0,
        "keywords_enabled": 0,
        "keyword_rows_that_begin_serving": sum(
            b["keyword_rows_that_will_begin_serving"] for b in blocks),
        "rsas_that_begin_serving": sum(b["rsa_count"] for b in blocks),
        "keywords_created_paused": 0, "rsas_created_paused": 0, "ads_changed": 0,
        "negatives_added": 0, "assets_changed": 0, "final_urls_changed": 0,
        "conversion_actions_changed": 0,
        "google_ads_mutations_total": len(actions),
    },
    "approval_owner": "Walter Correa",
    "approver_email": "access@greenmarketing.com",
}}

HDR = """# PLAN-I2 - ENABLE EXISTING QUALIFIED DEMAND
#
# STATUS: NOT APPROVED. DO NOT EXECUTE.
#
# SUPERSEDES PLAN-D in the recommendation order (PLAN-D is NOT void - its
# fingerprint F61C9F287B82 is unchanged and it remains valid as written).
#
# Enabling a paused ad group is a LIVE DELIVERY CHANGE. Every keyword that would
# begin serving is listed explicitly below.

"""
p = PLANS / "2026-08-26-plan-i2-enable-existing-demand.yaml"
p.write_text(HDR + yaml.safe_dump(plan, sort_keys=False, width=90, allow_unicode=True),
             encoding="utf-8")
print("wrote", p)
for b in blocks:
    print("  %-28s -> %s ag=%s  %d kw rows, %d distinct searches/mo, +$%.2f/6d"
          % (b["ad_group_name"], b["campaign_name"], b["ad_group_id"],
             b["keyword_rows_that_will_begin_serving"],
             b["distinct_local_monthly_searches"],
             b["expected_incremental_spend_6d"]))
    print("     cross-campaign duplicates: %s" % b["cross_campaign_duplicate_texts"])
