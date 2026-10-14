#!/usr/bin/env python3
"""Ambient Cooling - Live | PREFLIGHT for the three approved fingerprints.

READ + VALIDATE-ONLY. Writes nothing durable. Hard-stops on any mismatch.

  82ACD4953536C020  A-1  7 x CREATE PHRASE negative, campaign 24132507747
  6F2B6ABBCEB992E4  A-2  1 x CREATE BROAD  negative, campaign 24132507741
  E50EDFE7644A9B5F  D-1  1 x REMOVE shared_criterion 11252984411~11143481
  TOTAL 9 operations
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, PLANS, RECEIPTS, SNAP, TZ,
    client, q, identity_gate, E, write,
)
from ambient_0827_negative_audit import SERVICE_PROBES, blocks  # noqa: E402

STAMP = "2026-08-28"
HVAC_INSTALL, AC_REPAIR = "24132507747", "24132507741"
ACCOUNT_SET, HANOVER_CRIT = "11252984411", "11143481"

A1_EXPECT = ["croppmetcalfe", "michael and sons", "michael & sons",
             "armbridge", "bluedot", "blauch", "hugee"]
A2_EXPECT = ["automotive"]
FP_A1, FP_A2, FP_D1 = "82ACD4953536C020", "6F2B6ABBCEB992E4", "E50EDFE7644A9B5F"
TOTAL_OPS = 9

HVAC_BRANDS = ["carrier", "trane", "lennox", "goodman", "rheem", "ruud", "york",
               "bryant", "amana", "payne", "daikin", "mitsubishi", "fujitsu",
               "coleman", "ducane", "frigidaire", "ecobee", "nest", "honeywell",
               "bosch", "navien", "burnham", "buderus", "lochinvar", "american standard"]
SERVICE_AREA = ["severn md", "severna park md", "columbia md", "hanover md",
                "annapolis md", "glen burnie md", "odenton md", "crofton md",
                "pasadena md", "arnold md", "elkridge md", "ellicott city md",
                "jessup md", "laurel md", "linthicum heights md", "halethorpe md",
                "gambrills md", "fort meade md", "catonsville md", "arbutus md"]

FAILS = []


def check(label, ok, detail=""):
    FAILS.append(label) if not ok else None
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" :: {detail}" if detail else ""))
    return ok


def fp(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16].upper()


def main():
    c = client()
    rec = {"stage": "PREFLIGHT", "run_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "mutations": 0,
           "approved_fingerprints": [FP_A1, FP_A2, FP_D1],
           "expected_total_operations": TOTAL_OPS, "checks": {}}

    # ---------- 1-4 identity ----------
    print("== 1-4. IDENTITY GATE ==")
    ident = identity_gate(c)
    rec["identity"] = ident
    check("account is exactly 'Ambient Cooling - Live' / 2401959466",
          ident["descriptive_name"] == "Ambient Cooling - Live" and ident["customer_id"] == CID)
    check("non-manager, non-test", not ident["manager"] and not ident["test_account"])
    check("both manager links ACTIVE",
          ident["manager_links"].get("3373711342") == "ACTIVE"
          and ident["manager_links"].get("2815082755") == "ACTIVE",
          str(ident["manager_links"]))

    # ---------- 5 concurrent writer ----------
    print("\n== 5. CONCURRENT WRITER ==")
    last = q(c, """SELECT change_event.change_date_time, change_event.user_email,
                   change_event.change_resource_type
                   FROM change_event
                   WHERE change_event.change_date_time >= '2026-08-22'
                     AND change_event.change_date_time <= '2026-08-29'
                   ORDER BY change_event.change_date_time DESC LIMIT 5""")
    latest = last[0].change_event.change_date_time if last else None
    rec["latest_change_event"] = latest
    check("no account change since 2026-08-22 09:36:07",
          latest == "2026-08-22 09:36:07.725231", str(latest))

    # ---------- 6 fingerprints reproduce ----------
    print("\n== 6. FINGERPRINTS REPRODUCE ==")
    a1 = json.loads((PLANS / f"AMBIENT-A-1-{STAMP}.json").read_text(encoding="utf-8"))
    a2 = json.loads((PLANS / f"AMBIENT-A-2-{STAMP}.json").read_text(encoding="utf-8"))
    d1 = json.loads((PLANS / f"AMBIENT-D-1-{STAMP}.json").read_text(encoding="utf-8"))
    r_a1 = fp({k: a1[k] for k in ("plan_name", "customer_id", "target_campaign_id", "operations")})
    r_a2 = fp({k: a2[k] for k in ("plan_name", "customer_id", "target_campaign_id", "operations")})
    r_d1 = fp({k: d1[k] for k in ("plan_name", "customer_id", "operations")})
    rec["fingerprints"] = {"A-1": {"approved": FP_A1, "in_file": a1["fingerprint"], "recomputed": r_a1},
                           "A-2": {"approved": FP_A2, "in_file": a2["fingerprint"], "recomputed": r_a2},
                           "D-1": {"approved": FP_D1, "in_file": d1["fingerprint"], "recomputed": r_d1}}
    check(f"A-1 {FP_A1} reproduces", r_a1 == FP_A1 == a1["fingerprint"], r_a1)
    check(f"A-2 {FP_A2} reproduces", r_a2 == FP_A2 == a2["fingerprint"], r_a2)
    check(f"D-1 {FP_D1} reproduces", r_d1 == FP_D1 == d1["fingerprint"], r_d1)

    # ---------- plan contents match the approval exactly ----------
    print("\n== PLAN CONTENTS MATCH THE APPROVAL ==")
    a1_texts = [o["proposed_value"].split("'")[1] for o in a1["operations"]]
    a2_texts = [o["proposed_value"].split("'")[1] for o in a2["operations"]]
    check("A-1 contains exactly the 7 approved terms, in order",
          a1_texts == A1_EXPECT, str(a1_texts))
    check("A-1 every match type is PHRASE",
          all("[PHRASE]" in o["proposed_value"] for o in a1["operations"]))
    check("A-1 every target campaign is 24132507747",
          all(o["campaign_id"] == HVAC_INSTALL for o in a1["operations"]))
    check("A-2 contains exactly ['automotive']", a2_texts == A2_EXPECT, str(a2_texts))
    check("A-2 match type is BROAD", "[BROAD]" in a2["operations"][0]["proposed_value"])
    check("A-2 target campaign is 24132507741",
          a2["operations"][0]["campaign_id"] == AC_REPAIR)
    check("D-1 contains exactly one removal", len(d1["operations"]) == 1)
    check("D-1 removal is hanover / BROAD / list 11252984411 / criterion 11143481",
          d1["operations"][0]["negative_text"] == "hanover"
          and d1["operations"][0]["match_type"] == "BROAD"
          and d1["operations"][0]["account_level_list_id"] == ACCOUNT_SET
          and d1["operations"][0]["criterion_id"] == HANOVER_CRIT)
    total = len(a1["operations"]) + len(a2["operations"]) + len(d1["operations"])
    check(f"total operation count is exactly {TOTAL_OPS}", total == TOTAL_OPS, str(total))
    rec["operation_counts"] = {"A-1": len(a1["operations"]), "A-2": len(a2["operations"]),
                               "D-1": len(d1["operations"]), "total": total}

    # ---------- 7 none already exists at the approved scope ----------
    print("\n== 7. NONE OF THE 8 NEW NEGATIVES ALREADY EXISTS AT SCOPE ==")
    existing = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id,
                      campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
                      campaign_criterion.negative
                      FROM campaign_criterion WHERE campaign.id IN ({IN5})
                        AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.status!='REMOVED'"""):
        existing.append({"campaign_id": str(r.campaign.id),
                         "criterion_id": str(r.campaign_criterion.criterion_id),
                         "text": r.campaign_criterion.keyword.text,
                         "match": E(r.campaign_criterion.keyword.match_type),
                         "negative": r.campaign_criterion.negative})
    rec["existing_campaign_negatives_before"] = existing
    check("before-state has exactly 3 campaign negatives (car, auto, boat)",
          len(existing) == 3
          and sorted(x["text"] for x in existing) == ["auto", "boat", "car"],
          str(sorted(x["text"] for x in existing)))
    dupes = []
    for t in A1_EXPECT:
        if any(x["campaign_id"] == HVAC_INSTALL and x["text"].lower() == t.lower()
               and x["match"] == "PHRASE" for x in existing):
            dupes.append(("A-1", t))
    for t in A2_EXPECT:
        if any(x["campaign_id"] == AC_REPAIR and x["text"].lower() == t.lower()
               and x["match"] == "BROAD" for x in existing):
            dupes.append(("A-2", t))
    check("zero of the 8 already exist at the approved scope", not dupes, str(dupes))
    rec["duplicates_found"] = dupes

    # ---------- 8 hanover criterion unchanged ----------
    print("\n== 8. ACCOUNT-LEVEL CRITERION 11143481 ==")
    members = []
    for r in q(c, f"""SELECT shared_criterion.resource_name, shared_criterion.criterion_id,
                      shared_criterion.keyword.text, shared_criterion.keyword.match_type,
                      shared_set.id FROM shared_criterion
                      WHERE shared_set.id = {ACCOUNT_SET}"""):
        members.append({"resource_name": r.shared_criterion.resource_name,
                        "criterion_id": str(r.shared_criterion.criterion_id),
                        "text": r.shared_criterion.keyword.text,
                        "match": E(r.shared_criterion.keyword.match_type),
                        "set_id": str(r.shared_set.id)})
    rec["account_list_members_before"] = members
    rec["account_list_member_count_before"] = len(members)
    han = [m for m in members if m["criterion_id"] == HANOVER_CRIT]
    check("account-level list has 59 members before", len(members) == 59, str(len(members)))
    check("criterion 11143481 exists as hanover / BROAD / list 11252984411",
          len(han) == 1 and han[0]["text"] == "hanover" and han[0]["match"] == "BROAD"
          and han[0]["set_id"] == ACCOUNT_SET, str(han))
    rec["hanover_member_before"] = han[0] if han else None

    # ---------- 9 Hanover geo still targeted ----------
    print("\n== 9. HANOVER GEO 1018614 TARGETED ON ALL FIVE ==")
    targeted = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id,
                      campaign_criterion.negative,
                      campaign_criterion.location.geo_target_constant
                      FROM campaign_criterion WHERE campaign.id IN ({IN5})
                        AND campaign_criterion.type='LOCATION'
                        AND campaign_criterion.status!='REMOVED'"""):
        if r.campaign_criterion.location.geo_target_constant.endswith("/1018614"):
            targeted.append({"campaign_id": str(r.campaign.id),
                             "campaign": NAME[str(r.campaign.id)],
                             "criterion_id": str(r.campaign_criterion.criterion_id),
                             "negative": r.campaign_criterion.negative})
    rec["hanover_geo_targeted_before"] = targeted
    check("Hanover geo 1018614 positively targeted on all five campaigns",
          len(targeted) == 5 and not any(t["negative"] for t in targeted),
          str([t["campaign"] for t in targeted]))

    # ---------- 10-12 conflict testing ----------
    print("\n== 10-12. CONFLICT TESTING ==")
    live_kw = []
    for r in q(c, f"""SELECT campaign.id, ad_group.name, ad_group_criterion.keyword.text,
                      ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                      ad_group_criterion.system_serving_status
                      FROM ad_group_criterion WHERE campaign.id IN ({IN5})
                        AND ad_group_criterion.type='KEYWORD'
                        AND ad_group_criterion.status!='REMOVED'
                        AND ad_group_criterion.negative=FALSE
                        AND ad_group.status!='REMOVED'"""):
        live_kw.append({"campaign_id": str(r.campaign.id),
                        "campaign": NAME[str(r.campaign.id)],
                        "text": r.ad_group_criterion.keyword.text,
                        "match": E(r.ad_group_criterion.keyword.match_type),
                        "status": E(r.ad_group_criterion.status),
                        "serving": E(r.ad_group_criterion.system_serving_status)})
    rec["live_keywords_before"] = live_kw
    check("10 live positive keywords, all PHRASE or EXACT", len(live_kw) == 10
          and all(k["match"] in ("PHRASE", "EXACT") for k in live_kw), str(len(live_kw)))
    check("all 10 keywords ENABLED and ELIGIBLE",
          all(k["status"] == "ENABLED" and k["serving"] == "ELIGIBLE" for k in live_kw))

    st = json.loads((SNAP / "search-terms-2026-08-27.json").read_text(encoding="utf-8"))
    converting = [v for v in st["verdicts"] if v["all_conversions"] > 0]
    primary_converting = [v for v in st["verdicts"] if v["primary_conversions"] > 0]
    rec["converting_terms_tested"] = len(converting)
    rec["primary_converting_terms_tested"] = len(primary_converting)

    conflicts = {"keywords": [], "service_probes": [], "converting_terms": [],
                 "service_area_locations": [], "hvac_brands": []}
    proposals = [(t, "PHRASE", HVAC_INSTALL) for t in A1_EXPECT] + \
                [(t, "BROAD", AC_REPAIR) for t in A2_EXPECT]
    for text, match, camp in proposals:
        for k in live_kw:
            if k["campaign_id"] == camp and blocks(text, match, k["text"])[0]:
                conflicts["keywords"].append((text, k["text"]))
        for p in SERVICE_PROBES:
            if blocks(text, match, p)[0]:
                conflicts["service_probes"].append((text, p))
        for v in converting:
            if v["campaign_id"] == camp and blocks(text, match, v["search_term"])[0]:
                conflicts["converting_terms"].append((text, v["search_term"]))
        for loc in SERVICE_AREA:
            for svc in ("ac repair ", "hvac repair ", "hvac installation "):
                if blocks(text, match, svc + loc)[0]:
                    conflicts["service_area_locations"].append((text, svc + loc))
        for b in HVAC_BRANDS:
            for svc in (" ac repair", " hvac repair", " furnace repair", " installation"):
                if blocks(text, match, b + svc)[0]:
                    conflicts["hvac_brands"].append((text, b + svc))
    rec["conflict_tests"] = {k: v for k, v in conflicts.items()}
    check("zero conflicts vs all active Phrase/Exact keywords",
          not conflicts["keywords"], str(conflicts["keywords"]))
    check(f"zero conflicts vs all {len(SERVICE_PROBES)} five-service probes",
          not conflicts["service_probes"], str(conflicts["service_probes"]))
    check(f"zero conflicts vs all {len(converting)} historical converting terms",
          not conflicts["converting_terms"], str(conflicts["converting_terms"]))
    check(f"zero conflicts vs {len(SERVICE_AREA)} service-area location queries",
          not conflicts["service_area_locations"], str(conflicts["service_area_locations"]))
    check(f"zero conflicts vs {len(HVAC_BRANDS)} HVAC manufacturer/equipment queries",
          not conflicts["hvac_brands"], str(conflicts["hvac_brands"]))

    # ---------- 13 removal isolation ----------
    print("\n== 13. HANOVER REMOVAL ISOLATION ==")
    others_blocking = [m for m in members if m["criterion_id"] != HANOVER_CRIT
                       and blocks(m["text"], m["match"], "ac repair hanover md")[0]]
    check("no other account-level negative also blocks Hanover",
          not others_blocking, str([(m["text"], m["match"]) for m in others_blocking]))
    held = ["thermostat", "thermostats", "ruud", "rudd", "ecobee", "frigidaire", "ducane"]
    held_present = [m["text"] for m in members if m["text"].lower() in held]
    rec["held_members_present_before"] = sorted(held_present)
    check("all 7 HELD members present and NOT in this plan",
          sorted(held_present) == sorted(held), str(sorted(held_present)))
    check("D-1 targets exactly one resource name",
          d1["operations"][0]["resource_name"] ==
          f"customers/{CID}/sharedCriteria/{ACCOUNT_SET}~{HANOVER_CRIT}",
          d1["operations"][0]["resource_name"])

    # ---------- structural baseline for the final diff ----------
    print("\n== STRUCTURAL BASELINE ==")
    base = {}
    base["campaigns"] = len(q(c, "SELECT campaign.id FROM campaign WHERE campaign.status!='REMOVED'"))
    base["ad_groups_on_five"] = len(q(c, f"SELECT ad_group.id FROM ad_group WHERE campaign.id IN ({IN5}) AND ad_group.status!='REMOVED'"))
    base["ads_on_five"] = len(q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE campaign.id IN ({IN5}) AND ad_group_ad.status!='REMOVED'"))
    base["positive_keywords"] = len(live_kw)
    base["campaign_negatives"] = len(existing)
    base["account_list_members"] = len(members)
    base["budgets"] = {str(r.campaign_budget.id): r.campaign_budget.amount_micros for r in q(c,
        """SELECT campaign_budget.id, campaign_budget.amount_micros FROM campaign_budget
        WHERE campaign_budget.id IN (15787409435,15787409438,15787409441,15787409444,15787409447)""")}
    base["cpc_ceilings"] = sorted({r.campaign.target_spend.cpc_bid_ceiling_micros for r in q(c,
        f"SELECT campaign.id, campaign.target_spend.cpc_bid_ceiling_micros FROM campaign WHERE campaign.id IN ({IN5})")})
    base["excluded_asset_set_types"] = sorted({tuple(E(z) for z in r.campaign.excluded_parent_asset_set_types)
        for r in q(c, f"SELECT campaign.id, campaign.excluded_parent_asset_set_types FROM campaign WHERE campaign.id IN ({IN5})")})
    base["ip_exclusions"] = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion WHERE campaign_criterion.type='IP_BLOCK' AND campaign_criterion.status!='REMOVED'"))
    base["ad_schedule_rows"] = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion WHERE campaign.id IN ({IN5}) AND campaign_criterion.type='AD_SCHEDULE' AND campaign_criterion.status!='REMOVED'"))
    base["location_criteria"] = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion WHERE campaign.id IN ({IN5}) AND campaign_criterion.type='LOCATION' AND campaign_criterion.status!='REMOVED'"))
    base["conversion_actions"] = len(q(c, "SELECT conversion_action.id FROM conversion_action WHERE conversion_action.status!='REMOVED'"))
    base["wc_lead_include_in_conversions"] = [r.conversion_action.include_in_conversions_metric for r in q(c,
        "SELECT conversion_action.id, conversion_action.include_in_conversions_metric FROM conversion_action WHERE conversion_action.id = 7643656486")]
    base["sitelink_associations"] = len([r for r in q(c,
        f"SELECT campaign.id, campaign_asset.status FROM campaign_asset WHERE campaign.id IN ({IN5}) AND campaign_asset.field_type='SITELINK'")
        if E(r.campaign_asset.status) != "REMOVED"])
    base["campaign_shared_sets_on_five"] = len(q(c, f"SELECT campaign.id FROM campaign_shared_set WHERE campaign.id IN ({IN5})"))
    base["location_asset_set_status"] = [E(r.customer_asset_set.status) for r in q(c,
        "SELECT customer_asset_set.asset_set, customer_asset_set.status FROM customer_asset_set")
        if r.customer_asset_set.asset_set.endswith("8620443109")]
    base["manager_links"] = ident["manager_links"]
    rec["structural_baseline"] = base
    for k, v in base.items():
        print(f"  {k:36s} {v}")

    # ---------- 14 validate-only on the exact nine ----------
    print("\n== 14. VALIDATE-ONLY ON THE EXACT NINE OPERATIONS ==")
    vres = {}
    cc = c.get_service("CampaignCriterionService")

    def vneg(label, texts, match, camp):
        ops = []
        for t in texts:
            op = c.get_type("CampaignCriterionOperation")
            crit = op.create
            crit.campaign = f"customers/{CID}/campaigns/{camp}"
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
            v = {"status": "VALIDATE_OK", "operations": len(ops),
                 "results_returned": len(resp.results)}
        except Exception as exc:  # noqa: BLE001
            v = {"status": "VALIDATE_FAIL", "error": str(exc)[:800]}
        vres[label] = v
        check(f"{label} validate-only", v["status"] == "VALIDATE_OK", str(v))
        return v

    vneg("A-1 (7 PHRASE on 24132507747)", A1_EXPECT, "PHRASE", HVAC_INSTALL)
    vneg("A-2 (1 BROAD on 24132507741)", A2_EXPECT, "BROAD", AC_REPAIR)

    sc = c.get_service("SharedCriterionService")
    op = c.get_type("SharedCriterionOperation")
    op.remove = f"customers/{CID}/sharedCriteria/{ACCOUNT_SET}~{HANOVER_CRIT}"
    req = c.get_type("MutateSharedCriteriaRequest")
    req.customer_id = CID
    req.operations.append(op)
    req.validate_only = True
    try:
        resp = sc.mutate_shared_criteria(request=req)
        v = {"status": "VALIDATE_OK", "operations": 1, "results_returned": len(resp.results)}
    except Exception as exc:  # noqa: BLE001
        v = {"status": "VALIDATE_FAIL", "error": str(exc)[:800]}
    vres["D-1 (1 REMOVE 11252984411~11143481)"] = v
    check("D-1 validate-only", v["status"] == "VALIDATE_OK", str(v))
    rec["validate_only"] = vres

    # ---------- verdict ----------
    rec["preflight_result"] = "PASS" if not FAILS else "FAIL"
    rec["failed_checks"] = FAILS
    write(RECEIPTS / f"preflight-approved-{STAMP}.json", rec)
    print(f"\n== PREFLIGHT: {rec['preflight_result']} ==")
    if FAILS:
        print("  FAILED CHECKS:")
        for f in FAILS:
            print(f"    - {f}")
        sys.exit("HARD STOP: preflight failed. No mutation will run.")
    print("  All checks passed. 9 operations cleared for execution.")
    return rec


if __name__ == "__main__":
    main()
