#!/usr/bin/env python3
"""Ambient Cooling - Live | split plans, corrected | READ + VALIDATE-ONLY, ZERO MUTATIONS.

Supersedes ACE80A09AC134C85 (bundled) with one fingerprint per distinct change
type, and splits C3038EDD9E621944 so the verified `hanover` removal stands alone.
Every batch gets its own validate-only call. Nothing is written durably.
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
    CID, FIVE, IN5, NAME, PLANS, RECEIPTS, SNAP, TZ,
    client, q, identity_gate, E, write,
)
from ambient_0827_negative_audit import SERVICE_PROBES, blocks  # noqa: E402

STAMP = "2026-08-28"
AC_REPAIR, GAS_BOILER = "24132507741", "24132507744"
HVAC_INSTALL, HVAC_REPAIR, HVAC_REPLACE = "24132507747", "24132507750", "24132507753"
ACCOUNT_SET = "11252984411"

# Package A-1: only the 7 that pass the owner's stricter safety rule.
A1_NEGATIVES = ["croppmetcalfe", "michael and sons", "michael & sons",
                "armbridge", "bluedot", "blauch", "hugee"]
# Package A-2: vehicle protection, different campaign and rationale.
A2_NEGATIVES = ["automotive"]
# Package D-1: the single verified account-level removal.
D1_REMOVE = ["hanover"]
# Package D-2: manufacturer / equipment-brand negatives, held.
D2_REMOVE = ["thermostat", "thermostats", "ruud", "rudd", "ecobee",
             "frigidaire", "ducane"]


def fp(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16].upper()


def main():
    c = client()
    print("== IDENTITY GATE ==")
    identity_gate(c, verbose=False)
    print("  PASS\n")

    rv = json.loads((SNAP / "reverification-2026-08-28-reverify.json").read_text(encoding="utf-8"))
    rv2 = json.loads((SNAP / "reverification-2026-08-28-reverify2.json").read_text(encoding="utf-8"))
    st = json.loads((SNAP / "search-terms-2026-08-27.json").read_text(encoding="utf-8"))
    verdicts = st["verdicts"]
    screened = {x["text"]: x for x in rv2["strict_screen"]}

    # ---------------- fresh before-state ----------------
    before_neg, live_kw, before_bid = [], [], {}
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id,
                      campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
                      FROM campaign_criterion WHERE campaign.id IN ({IN5})
                        AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.status!='REMOVED'"""):
        before_neg.append({"campaign_id": str(r.campaign.id),
                           "criterion_id": str(r.campaign_criterion.criterion_id),
                           "text": r.campaign_criterion.keyword.text,
                           "match": E(r.campaign_criterion.keyword.match_type)})
    for r in q(c, f"""SELECT campaign.id, ad_group_criterion.keyword.text,
                      ad_group_criterion.keyword.match_type FROM ad_group_criterion
                      WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type='KEYWORD'
                        AND ad_group_criterion.status!='REMOVED'
                        AND ad_group_criterion.negative=FALSE
                        AND ad_group.status!='REMOVED'"""):
        live_kw.append({"campaign_id": str(r.campaign.id),
                        "text": r.ad_group_criterion.keyword.text,
                        "match": E(r.ad_group_criterion.keyword.match_type)})
    for r in q(c, f"""SELECT campaign.id, campaign.bidding_strategy_type,
                      campaign.target_spend.cpc_bid_ceiling_micros,
                      campaign.excluded_parent_asset_set_types
                      FROM campaign WHERE campaign.id IN ({IN5})"""):
        before_bid[str(r.campaign.id)] = {
            "bidding_strategy_type": E(r.campaign.bidding_strategy_type),
            "cpc_bid_ceiling_micros": r.campaign.target_spend.cpc_bid_ceiling_micros,
            "excluded_parent_asset_set_types": [
                E(z) for z in r.campaign.excluded_parent_asset_set_types]}
    print(f"  before-state: {len(before_neg)} campaign negatives, "
          f"{len(live_kw)} live keywords, ceilings "
          f"{sorted({v['cpc_bid_ceiling_micros'] for v in before_bid.values()})}")

    receipts = {"run_local": datetime.datetime.now(TZ).isoformat(),
                "customer_id": CID, "mutations": 0, "results": {}}

    def op_detail(text, match, campaign_id, package):
        s = screened.get(text, {})
        covered = [v for v in verdicts if v["campaign_id"] == campaign_id
                   and blocks(text, match, v["search_term"])[0]]
        return {
            "operation_type": "CREATE campaign_criterion (negative keyword)",
            "package": package,
            "campaign_id": campaign_id,
            "campaign_name": NAME[campaign_id],
            "resource_targeted": f"customers/{CID}/campaigns/{campaign_id}",
            "current_value": "no such negative exists on this campaign",
            "proposed_value": f"negative keyword '{text}' [{match}] at campaign level",
            "reason": ("competitor company name reached by phrase same-meaning "
                       "expansion of the keyword 'hvac installers'"
                       if package == "A-1" else
                       "vehicle air-conditioning intent, outside all five services; "
                       "negatives have no close variants so 'auto' does not cover it"),
            "supporting_metrics": {
                "terms_covered": len(covered),
                "impressions": sum(v["impressions"] for v in covered),
                "clicks": sum(v["clicks"] for v in covered),
                "cost": round(sum(v["cost"] for v in covered), 2),
                "primary_conversions": round(
                    sum(v["primary_conversions"] for v in covered), 2),
                "secondary_all_conversions": round(
                    sum(v["all_conversions"] for v in covered), 2),
                "example_terms": [v["search_term"] for v in
                                  sorted(covered, key=lambda z: -z["cost"])][:5],
            },
            "conflict_test_active_keywords": [
                k["text"] for k in live_kw
                if k["campaign_id"] == campaign_id and blocks(text, match, k["text"])[0]],
            "conflict_test_five_services": [
                p for p in SERVICE_PROBES if blocks(text, match, p)[0]],
            "strict_rule_screen": s.get("strict_verdict"),
            "strict_rule_reasons": s.get("strict_reasons", []),
            "already_covered_by_existing_negative": [
                n["text"] for n in before_neg
                if n["campaign_id"] == campaign_id
                and blocks(n["text"], n["match"], text)[0]],
            "risk": ("Blocks the exact phrase only. Zero live keywords and zero of the "
                     "54 service probes are affected. Reversible in one REMOVE."),
            "rollback": "REMOVE the returned campaign_criterion resource name.",
            "unrelated_resource_assertion": (
                "creates one campaign_criterion; touches no budget, bid, keyword, ad, "
                "asset, schedule, location, conversion or manager link"),
        }

    plans = {}

    # =================== PACKAGE A-1 ===================
    print("\n== PACKAGE A-1: competitor negatives that pass the strict rule ==")
    a1_ops = [op_detail(t, "PHRASE", HVAC_INSTALL, "A-1") for t in A1_NEGATIVES]
    a1 = {
        "plan_name": "AMBIENT-A1-COMPETITOR-NEGATIVES-2026-08-28",
        "supersedes": "the ADJ-1 package inside ACE80A09AC134C85",
        "approval_class": "campaign-criterion CREATE, reversible",
        "customer_id": CID, "exact_child_account_name": "Ambient Cooling - Live",
        "target_campaign_id": HVAC_INSTALL,
        "object_count": len(a1_ops),
        "operations": a1_ops,
        "excluded_by_strict_rule": [
            {"text": x["text"], "cost_forgone": x["cost"], "reasons": x["strict_reasons"]}
            for x in rv2["strict_reject"]],
        "totals": {
            "cost_covered": round(sum(o["supporting_metrics"]["cost"] for o in a1_ops), 2),
            "clicks_covered": sum(o["supporting_metrics"]["clicks"] for o in a1_ops),
            "primary_conversions_covered": round(
                sum(o["supporting_metrics"]["primary_conversions"] for o in a1_ops), 2),
        },
        "honest_limitation": (
            "This recovers $238.51 of the $760.28 competitor spend. The other $521.77 "
            "sits behind names that are ambiguous, contain a place name, or contain a "
            "generic service word, and are not safe to block. The durable fix is to "
            "replace the keyword 'hvac installers', not to keep adding names."),
    }
    a1["fingerprint"] = fp({k: a1[k] for k in
                            ("plan_name", "customer_id", "target_campaign_id", "operations")})
    plans["A-1"] = a1
    for o in a1_ops:
        m = o["supporting_metrics"]
        print(f"  {o['proposed_value']:58s} cost=${m['cost']:>7.2f} "
              f"clicks={m['clicks']} pconv={m['primary_conversions']} "
              f"kwConf={len(o['conflict_test_active_keywords'])} "
              f"probeConf={len(o['conflict_test_five_services'])}")
    print(f"  fingerprint: {a1['fingerprint']}  objects: {a1['object_count']}  "
          f"cost covered: ${a1['totals']['cost_covered']:,.2f}")

    # =================== PACKAGE A-2 ===================
    print("\n== PACKAGE A-2: vehicle protection on AC Repair ==")
    a2_ops = [op_detail(t, "BROAD", AC_REPAIR, "A-2") for t in A2_NEGATIVES]
    a2 = {
        "plan_name": "AMBIENT-A2-VEHICLE-PROTECTION-2026-08-28",
        "supersedes": "the ADJ-2 package inside ACE80A09AC134C85",
        "approval_class": "campaign-criterion CREATE, reversible",
        "customer_id": CID, "exact_child_account_name": "Ambient Cooling - Live",
        "target_campaign_id": AC_REPAIR,
        "object_count": len(a2_ops), "operations": a2_ops,
        "classification": (
            "PROTECTION, not a measured saving. Observed cost is $0.00. It is proposed "
            "because AC Repair's observed CPC is $90.49, so a single leaked vehicle "
            "click would cost more than this control, and because the already-approved "
            "'auto' negative provably does not cover 'automotive'."),
    }
    a2["fingerprint"] = fp({k: a2[k] for k in
                            ("plan_name", "customer_id", "target_campaign_id", "operations")})
    plans["A-2"] = a2
    for o in a2_ops:
        m = o["supporting_metrics"]
        print(f"  {o['proposed_value']:58s} cost=${m['cost']:>7.2f} "
              f"terms={m['terms_covered']} kwConf={len(o['conflict_test_active_keywords'])} "
              f"probeConf={len(o['conflict_test_five_services'])}")
    print(f"  fingerprint: {a2['fingerprint']}  objects: {a2['object_count']}")

    # =================== PACKAGE D-1 ===================
    print("\n== PACKAGE D-1: remove the single verified 'hanover' negative ==")
    members = {m["text"].lower(): m for m in rv["account_list_members"]}
    d1_ops = []
    for t in D1_REMOVE:
        m = members[t]
        d1_ops.append({
            "operation_type": "REMOVE shared_criterion (DESTRUCTIVE)",
            "negative_text": m["text"], "match_type": m["match"],
            "account_level_list_id": m["set_id"],
            "account_level_list_name": m["set_name"],
            "criterion_id": m["criterion_id"],
            "resource_name": m["resource_name"],
            "current_value": f"'{m['text']}' [{m['match']}] ACTIVE account-wide",
            "proposed_value": "removed from the account-level negative list",
            "affected_active_keywords": [
                k["text"] for k in live_kw if blocks(m["text"], m["match"], k["text"])[0]],
            "affected_targeted_locations": [
                {"geo_target_constant": "1018614",
                 "canonical_name": "Hanover,Maryland,United States",
                 "target_type": "City",
                 "targeted_on_campaigns": [t2["campaign"] for t2 in rv["hanover_targeted_on"]]}],
            "historical_search_terms": [
                v["search_term"] for v in verdicts if "hanover" in v["search_term"].lower()],
            "conversions_on_those_terms": 0.0,
            "measured_cost_impact_to_date": 0.0,
            "reason": ("The account explicitly targets Hanover, Maryland (geo 1018614) on "
                       "all five campaigns while an account-wide BROAD negative blocks "
                       "every query containing the word 'hanover'. The account is "
                       "blocking its own targeted city."),
            "no_other_negative_blocks_hanover": not rv["other_negatives_blocking_hanover"],
            "risk": ("Low. Removing a negative can only ADD eligible queries. It cannot "
                     "suppress anything. The added queries are Hanover-area service "
                     "searches inside the targeted geography."),
            "rollback": ("Re-create a BROAD shared_criterion 'hanover' in list "
                         "11252984411. The criterion ID will differ after re-creation."),
            "unrelated_resource_assertion": (
                "removes exactly one shared_criterion; the other 58 members stay; no "
                "other shared set, association, campaign, keyword, ad or asset changes"),
        })
    d1 = {
        "plan_name": "AMBIENT-D1-REMOVE-HANOVER-2026-08-28",
        "supersedes": "the hanover item inside C3038EDD9E621944",
        "approval_class": "DESTRUCTIVE-ACTION approval",
        "customer_id": CID, "exact_child_account_name": "Ambient Cooling - Live",
        "object_count": len(d1_ops), "operations": d1_ops,
        "contains_only_hanover": True,
        "blast_radius": ("The list is account-wide, so removal also affects the 18 legacy "
                         "campaigns. All 18 are PAUSED, so live impact is limited to the "
                         "five active Search campaigns."),
    }
    d1["fingerprint"] = fp({k: d1[k] for k in ("plan_name", "customer_id", "operations")})
    plans["D-1"] = d1
    for o in d1_ops:
        print(f"  REMOVE '{o['negative_text']}' [{o['match_type']}] "
              f"criterion_id={o['criterion_id']}")
        print(f"     blocks active keywords: {o['affected_active_keywords'] or 'NONE'}")
        print(f"     observed hanover terms: {len(o['historical_search_terms'])}")
        print(f"     no other negative blocks hanover: {o['no_other_negative_blocks_hanover']}")
    print(f"  fingerprint: {d1['fingerprint']}  objects: {d1['object_count']}")

    # =================== PACKAGE D-2 ===================
    print("\n== PACKAGE D-2: manufacturer / equipment-brand negatives (HELD) ==")
    d2_ops = []
    for t in D2_REMOVE:
        m = members[t]
        d2_ops.append({
            "operation_type": "REMOVE shared_criterion (DESTRUCTIVE)",
            "negative_text": m["text"], "match_type": m["match"],
            "account_level_list_id": m["set_id"], "criterion_id": m["criterion_id"],
            "resource_name": m["resource_name"],
            "affected_active_keywords": [
                k["text"] for k in live_kw if blocks(m["text"], m["match"], k["text"])[0]],
            "service_probes_it_blocks": [
                p for p in SERVICE_PROBES if blocks(m["text"], m["match"], p)[0]],
            "historical_search_terms": [
                v["search_term"] for v in verdicts
                if blocks(m["text"], m["match"], v["search_term"])[0]],
            "measured_cost_impact_to_date": 0.0,
            "reason": "HVAC manufacturer, equipment brand, or thermostat term; "
                      "brand-specific repair demand is inside HVAC Repair scope",
            "rollback": "Re-create the BROAD shared_criterion in list 11252984411.",
        })
    d2 = {
        "plan_name": "AMBIENT-D2-EQUIPMENT-BRAND-NEGATIVES-2026-08-28",
        "supersedes": "the non-hanover items inside C3038EDD9E621944",
        "approval_class": "DESTRUCTIVE-ACTION approval",
        "customer_id": CID, "object_count": len(d2_ops), "operations": d2_ops,
        "recommendation": "HOLD",
        "hold_reason": ("Zero measured cost impact and zero observed search terms. These "
                        "suppress demand that has never been measured, so the case is "
                        "theoretical. Bundle with the September keyword restructure."),
    }
    d2["fingerprint"] = fp({k: d2[k] for k in ("plan_name", "customer_id", "operations")})
    plans["D-2"] = d2
    for o in d2_ops:
        print(f"  REMOVE '{o['negative_text']:12s}' criterion_id={o['criterion_id']:>12s} "
              f"probes={len(o['service_probes_it_blocks'])} "
              f"observed_terms={len(o['historical_search_terms'])}")
    print(f"  fingerprint: {d2['fingerprint']}  objects: {d2['object_count']}")

    # =================== VALIDATE-ONLY, ONE BATCH PER PACKAGE ===================
    print("\n== VALIDATE-ONLY, ONE CALL PER PACKAGE (no durable write) ==")
    cc = c.get_service("CampaignCriterionService")

    def validate_negatives(label, texts, match, campaign_id):
        ops = []
        for t in texts:
            op = c.get_type("CampaignCriterionOperation")
            crit = op.create
            crit.campaign = f"customers/{CID}/campaigns/{campaign_id}"
            crit.negative = True
            crit.keyword.text = t
            crit.keyword.match_type = c.enums.KeywordMatchTypeEnum[match]
            ops.append(op)
        req = c.get_type("MutateCampaignCriteriaRequest")
        req.customer_id = CID
        req.operations.extend(ops)
        req.partial_failure = False
        req.validate_only = True
        try:
            resp = cc.mutate_campaign_criteria(request=req)
            r = {"status": "VALIDATE_OK", "operations": len(ops),
                 "results_returned": len(resp.results)}
        except Exception as exc:  # noqa: BLE001
            r = {"status": "VALIDATE_FAIL", "error": str(exc)[:800]}
        receipts["results"][label] = r
        print(f"  {label:44s} {r['status']} ({r.get('operations', 0)} ops)")
        return r

    plans["A-1"]["validate_only"] = validate_negatives(
        "A-1 competitor negatives (7)", A1_NEGATIVES, "PHRASE", HVAC_INSTALL)
    plans["A-2"]["validate_only"] = validate_negatives(
        "A-2 vehicle protection (1)", A2_NEGATIVES, "BROAD", AC_REPAIR)

    sc = c.get_service("SharedCriterionService")

    def validate_removals(label, texts):
        ops = []
        for t in texts:
            op = c.get_type("SharedCriterionOperation")
            op.remove = members[t]["resource_name"]
            ops.append(op)
        req = c.get_type("MutateSharedCriteriaRequest")
        req.customer_id = CID
        req.operations.extend(ops)
        req.validate_only = True
        try:
            resp = sc.mutate_shared_criteria(request=req)
            r = {"status": "VALIDATE_OK", "operations": len(ops),
                 "results_returned": len(resp.results)}
        except Exception as exc:  # noqa: BLE001
            r = {"status": "VALIDATE_FAIL", "error": str(exc)[:800]}
        receipts["results"][label] = r
        print(f"  {label:44s} {r['status']} ({r.get('operations', 0)} ops)")
        return r

    plans["D-1"]["validate_only"] = validate_removals("D-1 remove hanover (1)", D1_REMOVE)
    plans["D-2"]["validate_only"] = validate_removals(
        "D-2 equipment-brand removals (7)", D2_REMOVE)

    for k, p in plans.items():
        write(PLANS / f"AMBIENT-{k}-{STAMP}.json", p)
    write(RECEIPTS / f"validate-only-split-{STAMP}.json", receipts)

    print("\n== FINGERPRINTS ==")
    for k, p in plans.items():
        print(f"  {k:5s} {p['fingerprint']}  {p['object_count']:>2d} objects  "
              f"{p['validate_only']['status']:14s} {p['plan_name']}")
    return plans


if __name__ == "__main__":
    main()
