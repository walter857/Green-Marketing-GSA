#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | consolidated adjustment plan.

Builds ONE normalized plan, conflict-tests every proposed negative against the
live keywords, the 54 service probes and the full 750-pair observed corpus,
computes the short SHA-256 fingerprint, and runs Google's validate-only check
on the exact operations. NOTHING is written durably.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys
from pathlib import Path

from google.protobuf import field_mask_pb2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, PLANS, SNAP, RECEIPTS, TZ,
    client, q, identity_gate, E, write,
)
from ambient_0827_negative_audit import SERVICE_PROBES, blocks, words  # noqa: E402

STAMP = "2026-08-27"

AC_REPAIR = "24132507741"
GAS_BOILER = "24132507744"
HVAC_INSTALL = "24132507747"
HVAC_REPAIR = "24132507750"
HVAC_REPLACE = "24132507753"

# ---------------------------------------------------------------------------
# ADJ-1  Competitor company-name negatives, HVAC Installation only.
# Every entry is the narrowest distinctive token observed in the corpus.
# ---------------------------------------------------------------------------
COMPETITOR_NEGATIVES = [
    "croppmetcalfe", "furr", "michaels", "michael and sons", "michael & sons",
    "woodfin", "blauch", "armbridge", "bluedot", "mccrea", "barstow",
    "elmar mechanical", "hugee", "kirkland", "bahr", "beltway hvac",
    "supreme service today", "total comfort", "maryland mechanical",
    "amazing plumbing", "amazing heating", "hvac precision services",
    "horizon services", "len the plumber",
]

# ---------------------------------------------------------------------------
# ADJ-3  Maximum CPC bid limit on the five TARGET_SPEND strategies.
# Stage 1 removes only the extreme tail. All five are currently uncapped (0).
# ---------------------------------------------------------------------------
BID_CEILINGS = {
    AC_REPAIR:     60_000_000,
    HVAC_REPAIR:   60_000_000,
    HVAC_INSTALL:  40_000_000,
    HVAC_REPLACE:  40_000_000,
    GAS_BOILER:    40_000_000,
}


def fingerprint(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16].upper()


def main():
    c = client()
    print("== IDENTITY GATE ==")
    ident = identity_gate(c)

    st = json.loads((SNAP / f"search-terms-{STAMP}.json").read_text(encoding="utf-8"))
    verdicts = st["verdicts"]

    # ---------------- live before-state ----------------
    print("\n== BEFORE-STATE (fresh read) ==")
    live_kw = []
    for r in q(c, f"""SELECT campaign.id, ad_group.name, ad_group_criterion.keyword.text,
                      ad_group_criterion.keyword.match_type FROM ad_group_criterion
                      WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type='KEYWORD'
                        AND ad_group_criterion.status != 'REMOVED'
                        AND ad_group_criterion.negative = FALSE
                        AND ad_group.status != 'REMOVED'"""):
        live_kw.append({"campaign_id": str(r.campaign.id),
                        "campaign": NAME[str(r.campaign.id)],
                        "text": r.ad_group_criterion.keyword.text,
                        "match": E(r.ad_group_criterion.keyword.match_type)})

    before_neg = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id,
                      campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
                      FROM campaign_criterion WHERE campaign.id IN ({IN5})
                        AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.status != 'REMOVED'"""):
        before_neg.append({"campaign_id": str(r.campaign.id),
                           "criterion_id": str(r.campaign_criterion.criterion_id),
                           "text": r.campaign_criterion.keyword.text,
                           "match": E(r.campaign_criterion.keyword.match_type)})

    before_bid = {}
    for r in q(c, f"""SELECT campaign.id, campaign.bidding_strategy_type,
                      campaign.target_spend.cpc_bid_ceiling_micros,
                      campaign.excluded_parent_asset_set_types,
                      campaign.campaign_budget
                      FROM campaign WHERE campaign.id IN ({IN5})"""):
        before_bid[str(r.campaign.id)] = {
            "bidding_strategy_type": E(r.campaign.bidding_strategy_type),
            "cpc_bid_ceiling_micros": r.campaign.target_spend.cpc_bid_ceiling_micros,
            "excluded_parent_asset_set_types": [
                E(z) for z in r.campaign.excluded_parent_asset_set_types],
            "budget_id": r.campaign.campaign_budget.split("/")[-1]}

    before_budgets = {}
    for r in q(c, """SELECT campaign_budget.id, campaign_budget.amount_micros
                     FROM campaign_budget WHERE campaign_budget.id IN
                     (15787409435,15787409438,15787409441,15787409444,15787409447)"""):
        before_budgets[str(r.campaign_budget.id)] = r.campaign_budget.amount_micros

    print(f"  live positive keywords            : {len(live_kw)}")
    print(f"  campaign-level negatives (all five): {len(before_neg)} "
          f"{[n['text'] for n in before_neg]}")
    for cid in FIVE:
        b = before_bid[cid]
        print(f"  {NAME[cid]:20s} {b['bidding_strategy_type']:14s} "
              f"ceiling={b['cpc_bid_ceiling_micros']} "
              f"excluded_asset_sets={b['excluded_parent_asset_set_types']}")
    print(f"  budgets: {before_budgets}")

    # ---------------- replay protection ----------------
    print("\n== REPLAY PROTECTION ==")
    have = {(n["campaign_id"], n["text"]) for n in before_neg}
    replay = {
        "car_auto_boat_present_on_ac_repair": sorted(
            t for (cid, t) in have if cid == AC_REPAIR),
        "hvac_installation_budget_micros": before_budgets.get("15787409441"),
        "hvac_installation_budget_matches_executed_176_15":
            before_budgets.get("15787409441") == 176_150_000,
    }
    for k, v in replay.items():
        print(f"  {k}: {v}")
    assert replay["car_auto_boat_present_on_ac_repair"] == ["auto", "boat", "car"], \
        "car/auto/boat state changed - stop"
    assert replay["hvac_installation_budget_matches_executed_176_15"], \
        "HVAC Installation budget is not the executed value - stop"
    print("  PASS: completed work is intact and is NOT re-proposed.")

    # ---------------- conflict test every proposed negative ----------------
    print("\n== CONFLICT TEST ON EVERY PROPOSED NEGATIVE ==")
    proposed = []
    for text in COMPETITOR_NEGATIVES:
        proposed.append({"campaign_id": HVAC_INSTALL, "campaign": NAME[HVAC_INSTALL],
                         "text": text, "match": "PHRASE", "package": "ADJ-1"})
    proposed.append({"campaign_id": AC_REPAIR, "campaign": NAME[AC_REPAIR],
                     "text": "automotive", "match": "BROAD", "package": "ADJ-2"})

    rows = []
    hard_stop = []
    for p in proposed:
        kw_conf = [k for k in live_kw
                   if k["campaign_id"] == p["campaign_id"]
                   and blocks(p["text"], p["match"], k["text"])[0]]
        probe_conf = [x for x in SERVICE_PROBES if blocks(p["text"], p["match"], x)[0]]
        covered = [v for v in verdicts
                   if v["campaign_id"] == p["campaign_id"]
                   and blocks(p["text"], p["match"], v["search_term"])[0]]
        conv_conf = [v for v in covered if v["all_conversions"] > 0]
        primary_conf = [v for v in covered if v["primary_conversions"] > 0]
        dup = [n for n in before_neg
               if n["campaign_id"] == p["campaign_id"]
               and n["text"].lower() == p["text"].lower()]
        already = [n for n in before_neg
                   if n["campaign_id"] == p["campaign_id"]
                   and blocks(n["text"], n["match"], p["text"])[0]]
        p.update({
            "blocks_live_keywords": [k["text"] for k in kw_conf],
            "blocks_service_probes": probe_conf,
            "terms_covered": len(covered),
            "impressions_covered": sum(v["impressions"] for v in covered),
            "clicks_covered": sum(v["clicks"] for v in covered),
            "cost_covered": round(sum(v["cost"] for v in covered), 2),
            "primary_conversions_covered": round(
                sum(v["primary_conversions"] for v in covered), 2),
            "all_conversions_covered": round(
                sum(v["all_conversions"] for v in covered), 2),
            "blocks_a_converting_term": [v["search_term"] for v in conv_conf],
            "blocks_a_primary_converting_term": [v["search_term"] for v in primary_conf],
            "example_terms": [v["search_term"] for v in
                              sorted(covered, key=lambda z: -z["cost"])][:5],
            "duplicate_of_existing_negative": bool(dup),
            "already_covered_by_existing_negative": [n["text"] for n in already],
        })
        if kw_conf or probe_conf or primary_conf or dup:
            hard_stop.append(p)
        rows.append(p)

    print(f"  {'pkg':6s} {'match':7s} {'negative':24s} {'terms':>5s} {'impr':>5s} "
          f"{'clk':>4s} {'cost':>8s} {'pconv':>6s} {'kwConf':>7s} {'probeConf':>10s}")
    for p in sorted(rows, key=lambda z: -z["cost_covered"]):
        print(f"  {p['package']:6s} {p['match']:7s} {p['text']:24s} "
              f"{p['terms_covered']:>5d} {p['impressions_covered']:>5d} "
              f"{p['clicks_covered']:>4d} ${p['cost_covered']:>7.2f} "
              f"{p['primary_conversions_covered']:>6.1f} "
              f"{len(p['blocks_live_keywords']):>7d} {len(p['blocks_service_probes']):>10d}")
    if hard_stop:
        print("\n  HARD STOP - these proposed negatives fail a conflict test:")
        for p in hard_stop:
            print(f"     {p['text']} kw={p['blocks_live_keywords']} "
                  f"probes={p['blocks_service_probes']} "
                  f"primary={p['blocks_a_primary_converting_term']} "
                  f"dup={p['duplicate_of_existing_negative']}")
        sys.exit("Plan not generated: a proposed negative conflicts.")
    print("\n  PASS: 0 live keywords blocked, 0 service probes blocked, "
          "0 Primary-converting terms blocked, 0 duplicates.")

    tot = {
        "negatives": len(rows),
        "terms_covered": sum(p["terms_covered"] for p in rows),
        "impressions": sum(p["impressions_covered"] for p in rows),
        "clicks": sum(p["clicks_covered"] for p in rows),
        "cost": round(sum(p["cost_covered"] for p in rows), 2),
        "primary_conversions": round(sum(p["primary_conversions_covered"] for p in rows), 2),
        "all_conversions": round(sum(p["all_conversions_covered"] for p in rows), 2),
    }
    print(f"  coverage: {tot}")

    # ---------------- assemble the normalized plan ----------------
    perf = json.loads((SNAP / f"performance-{STAMP}.json").read_text(encoding="utf-8"))
    plan = {
        "plan_name": "AMBIENT-CONSOLIDATED-2026-08-27",
        "generated_local": datetime.datetime.now(TZ).isoformat(),
        "customer_id": CID,
        "exact_child_account_name": "Ambient Cooling - Live",
        "vertical": "heating-cooling",
        "primary_service": "AC Repair",
        "related_services": ["HVAC Repair", "HVAC Installation",
                             "HVAC Replacement", "Gas Boiler Repair"],
        "approval_owner": "Green Marketing",
        "mode": "create-and-update, all reversible, nothing removed",
        "packages": {
            "ADJ-1": {
                "title": "Competitor company-name negatives on HVAC Installation",
                "target_campaign_id": HVAC_INSTALL,
                "target_campaign_name":
                    "Search | NonBrand | HVAC Installation | Central MD | BOFU | 2026-08",
                "operation": "CREATE campaign_criterion (negative keyword)",
                "match_type": "PHRASE",
                "object_count": len(COMPETITOR_NEGATIVES),
                "negatives": sorted(COMPETITOR_NEGATIVES),
                "evidence": {
                    "mechanism": ("Google phrase-match same-meaning expansion maps the "
                                  "keyword 'hvac installers' onto local contractor brand "
                                  "searches."),
                    "observed_terms": 44,
                    "observed_impressions": 189,
                    "observed_clicks": 29,
                    "observed_cost": 760.28,
                    "observed_primary_conversions": 0.0,
                    "share_of_hvac_installation_spend": "38.2% of $1,987.98",
                },
            },
            "ADJ-2": {
                "title": "Complete the vehicle-AC protection on AC Repair",
                "target_campaign_id": AC_REPAIR,
                "target_campaign_name":
                    "Search | NonBrand | AC Repair | Central MD | BOFU | 2026-08",
                "operation": "CREATE campaign_criterion (negative keyword)",
                "match_type": "BROAD",
                "object_count": 1,
                "negatives": ["automotive"],
                "evidence": {
                    "mechanism": ("Negative keywords have no close variants, so the live "
                                  "'auto' BROAD negative does not block 'automotive'."),
                    "observed_terms": 2,
                    "observed_impressions": 3,
                    "observed_clicks": 0,
                    "observed_cost": 0.0,
                    "classification": ("PROTECTION, not a measured saving. AC Repair's "
                                       "observed CPC is $90.49, so one leaked click "
                                       "would cost more than this control."),
                },
            },
            "ADJ-3": {
                "title": "Stage 1 maximum CPC bid limit on all five Maximize Clicks strategies",
                "operation": "UPDATE campaign.target_spend.cpc_bid_ceiling_micros",
                "object_count": 5,
                "before": {NAME[k]: before_bid[k]["cpc_bid_ceiling_micros"] for k in FIVE},
                "after": {NAME[k]: BID_CEILINGS[k] for k in FIVE},
                "after_dollars": {NAME[k]: round(BID_CEILINGS[k] / 1e6, 2) for k in FIVE},
                "evidence": {
                    "account_average_cpc_launch_to_date": 42.66,
                    "ac_repair_exact_cpc": 130.42,
                    "hvac_repair_exact_cpc": 153.06,
                    "ac_repair_phrase_cpc": 72.06,
                    "hvac_repair_phrase_cpc": 77.99,
                    "hvac_installation_cpc": 25.16,
                    "hvac_replacement_cpc": 33.94,
                    "quality_scores": "AC Repair 4, HVAC Repair 2, HVAC Replacement 2",
                    "why": ("TARGET_SPEND with cpc_bid_ceiling_micros = 0 is uncapped. "
                            "With very low query volume and Quality Score 2-4, Maximize "
                            "Clicks bids to the top of the range to spend the budget."),
                    "risk": ("A ceiling can reduce impression share. Stage 1 is set above "
                             "the observed mean for every campaign so only the tail is cut."),
                    "rollback": "Set cpc_bid_ceiling_micros back to 0 on all five.",
                },
            },
            "ADJ-4": {
                "title": ("Stop the inherited Business Profile location asset from serving "
                          "on the five paid Search campaigns"),
                "operation": "UPDATE campaign.excluded_parent_asset_set_types += LOCATION_SYNC",
                "object_count": 5,
                "target_campaign_ids": FIVE,
                "before": {NAME[k]: before_bid[k]["excluded_parent_asset_set_types"]
                           for k in FIVE},
                "after": {NAME[k]: ["LOCATION_SYNC"] for k in FIVE},
                "evidence": {
                    "source": ("customer-level LOCATION_SYNC asset set 8620443109 "
                               "'Business Profile', status ENABLED"),
                    "location_expansion_clicks": 14,
                    "location_expansion_cost": 739.09,
                    "get_directions_clicks": 6,
                    "get_directions_cost": 199.88,
                    "combined_cost": 938.97,
                    "share_of_mtd_spend": "19.5% of $4,820.12",
                    "primary_conversions_produced": 0.0,
                    "hvac_repair_detail": ("$534.45 of HVAC Repair's $1,010.98, or 52.9%, "
                                           "went to location-asset and directions clicks"),
                    "why": ("These clicks go to the Business Profile, not to the paid "
                            "offer landing page, and only produce Google-hosted Local "
                            "actions, which are excluded from the Conversions column."),
                    "scope_note": ("Campaign-scoped. The account-level Business Profile "
                                   "link and all 18 legacy campaigns are untouched."),
                    "rollback": "Clear excluded_parent_asset_set_types on the five.",
                },
            },
        },
        "negative_detail": sorted(
            [{k: p[k] for k in (
                "package", "campaign_id", "campaign", "text", "match",
                "terms_covered", "impressions_covered", "clicks_covered",
                "cost_covered", "primary_conversions_covered",
                "all_conversions_covered", "blocks_live_keywords",
                "blocks_service_probes", "blocks_a_converting_term",
                "blocks_a_primary_converting_term", "example_terms",
                "duplicate_of_existing_negative",
                "already_covered_by_existing_negative")} for p in rows],
            key=lambda z: (z["package"], z["text"])),
        "totals": tot,
        "before_state": {
            "campaign_level_negatives": sorted(
                before_neg, key=lambda z: (z["campaign_id"], z["text"])),
            "bidding": {NAME[k]: before_bid[k] for k in FIVE},
            "budgets_micros": before_budgets,
            "live_positive_keywords": sorted(
                live_kw, key=lambda z: (z["campaign_id"], z["match"], z["text"])),
        },
        "expected_object_count": {
            "campaign_criterion_creates": len(rows),
            "campaign_updates": 5,
            "total_mutate_operations": len(rows) + 5,
        },
        "unrelated_resource_assertions": [
            "campaign count unchanged at 23",
            "ad group count on the five unchanged",
            "positive keyword count on the five unchanged at 10 live",
            "ad count on the five unchanged at 20",
            "the three AC Repair negatives car/auto/boat unchanged "
            "(criterion ids 10008241, 10000390, 10019071)",
            "all five daily budgets unchanged",
            "HVAC Installation budget 15787409441 stays 176150000",
            "2796 ClickCease IP exclusions on legacy campaigns unchanged",
            "both manager links 3373711342 and 2815082755 stay ACTIVE",
            "zero shared negative lists attached to the five",
            "conversion actions and conversion goals unchanged by this plan",
            "ad schedules unchanged at 6 rows per campaign",
            "location targets unchanged at 75 per campaign",
            "account tracking template unchanged",
            "no resource removed, paused, or enabled",
        ],
        "rollback": {
            "ADJ-1": "REMOVE the 24 created campaign_criterion resource names.",
            "ADJ-2": "REMOVE the 1 created campaign_criterion resource name.",
            "ADJ-3": "Set target_spend.cpc_bid_ceiling_micros back to 0 on all five.",
            "ADJ-4": "Clear excluded_parent_asset_set_types on all five.",
        },
        "not_in_this_plan": [
            "Gas Boiler keyword package 3D823A10CB3C0B25 stays BLOCKED: the live page "
            "still shows 'Your HVAC Replacement in 3 Simple Steps' as at 2026-08-27.",
            "Landing-page deployment 93A9DF4AA19675E8 stays BLOCKED: no source, staging, "
            "backup or deploy authority in this environment.",
            "Conversion-goal biddability correction: separate approval class.",
            "Account-level negative removals: destructive-action approval class.",
            "No budget change is proposed.",
            "No campaign, ad, keyword or asset is enabled, paused or removed.",
        ],
    }

    fp_input = {k: plan[k] for k in
                ("plan_name", "customer_id", "packages", "negative_detail",
                 "expected_object_count", "before_state")}
    fp = fingerprint(fp_input)
    plan["fingerprint"] = fp
    plan["fingerprint_inputs"] = sorted(fp_input.keys())

    print(f"\n== PLAN FINGERPRINT: {fp} ==")
    print(f"   objects: {plan['expected_object_count']}")

    # ---------------- validate-only ----------------
    print("\n== VALIDATE-ONLY (no durable write) ==")
    receipt = {"plan": plan["plan_name"], "fingerprint": fp, "customer_id": CID,
               "run_local": datetime.datetime.now(TZ).isoformat(), "results": {}}

    cc = c.get_service("CampaignCriterionService")
    ops = []
    for p in rows:
        op = c.get_type("CampaignCriterionOperation")
        crit = op.create
        crit.campaign = f"customers/{CID}/campaigns/{p['campaign_id']}"
        crit.negative = True
        crit.keyword.text = p["text"]
        crit.keyword.match_type = c.enums.KeywordMatchTypeEnum[p["match"]]
        ops.append(op)
    req = c.get_type("MutateCampaignCriteriaRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    req.partial_failure = False
    req.validate_only = True
    try:
        resp = cc.mutate_campaign_criteria(request=req)
        receipt["results"]["ADJ-1+ADJ-2 negatives"] = {
            "status": "VALIDATE_OK", "operations": len(ops),
            "results_returned": len(resp.results)}
        print(f"  ADJ-1 + ADJ-2 negatives : VALIDATE_OK ({len(ops)} operations)")
    except Exception as exc:  # noqa: BLE001
        receipt["results"]["ADJ-1+ADJ-2 negatives"] = {
            "status": "VALIDATE_FAIL", "error": str(exc)[:1500]}
        print(f"  ADJ-1 + ADJ-2 negatives : VALIDATE_FAIL\n{str(exc)[:1200]}")

    cs = c.get_service("CampaignService")
    ops2 = []
    for cid in FIVE:
        op = c.get_type("CampaignOperation")
        cam = op.update
        cam.resource_name = f"customers/{CID}/campaigns/{cid}"
        cam.target_spend.cpc_bid_ceiling_micros = BID_CEILINGS[cid]
        cam.excluded_parent_asset_set_types.append(
            c.enums.AssetSetTypeEnum.LOCATION_SYNC)
        c.copy_from(op.update_mask, field_mask_pb2.FieldMask(
            paths=["target_spend.cpc_bid_ceiling_micros",
                   "excluded_parent_asset_set_types"]))
        ops2.append(op)
    req2 = c.get_type("MutateCampaignsRequest")
    req2.customer_id = CID
    req2.operations.extend(ops2)
    req2.partial_failure = False
    req2.validate_only = True
    try:
        resp2 = cs.mutate_campaigns(request=req2)
        receipt["results"]["ADJ-3+ADJ-4 campaign updates"] = {
            "status": "VALIDATE_OK", "operations": len(ops2),
            "results_returned": len(resp2.results)}
        print(f"  ADJ-3 + ADJ-4 campaigns : VALIDATE_OK ({len(ops2)} operations)")
    except Exception as exc:  # noqa: BLE001
        receipt["results"]["ADJ-3+ADJ-4 campaign updates"] = {
            "status": "VALIDATE_FAIL", "error": str(exc)[:1500]}
        print(f"  ADJ-3 + ADJ-4 campaigns : VALIDATE_FAIL\n{str(exc)[:1200]}")

    plan["validate_only"] = receipt["results"]
    fp2 = fingerprint(fp_input)
    assert fp2 == fp, "fingerprint drifted while validating"
    plan["fingerprint_reproduces"] = True

    write(PLANS / f"AMBIENT-CONSOLIDATED-{STAMP}.json", plan)
    write(RECEIPTS / f"validate-only-{STAMP}.json", receipt)
    print(f"\nAPPROVAL LINE:\n  APPROVE CONSOLIDATED AMBIENT PLAN {fp} FOR {CID}")
    return plan


if __name__ == "__main__":
    main()
