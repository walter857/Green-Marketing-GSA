#!/usr/bin/env python3
"""Ambient | 2026-09-30 | Heat Pump Maintenance plans + held Boiler Maintenance payload.

    python ambient_0930_hpm_plans.py plan                     # fresh read, validators, validate_only, fingerprints
    python ambient_0930_hpm_plans.py readback                 # Phase 6 read-only QA of the existing resources
    python ambient_0930_hpm_plans.py execute --plan AMB-0930-HPM-BUDGET-1 --fp <FP>
    python ambient_0930_hpm_plans.py execute --plan AMB-0930-HPM-ENABLE-1 --fp <FP>

The hashed plan content is rebuilt from FRESH account state at execution, so any drift in the observed
preconditions changes the fingerprint and the run refuses. Each plan is one atomic mutate,
partial_failure=False, followed by a readback. ENABLE-1 refuses unless the BUDGET-1 receipt exists with a
clean readback. Boiler Maintenance is a HELD local payload only: never submitted while its page fails D2.
"""
from __future__ import annotations
import sys, json, re, argparse, datetime, hashlib
from urllib.parse import unquote
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS, SNAP, CLIENT_DIR, ROOT  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets, assert_target_matches  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402
import yaml  # noqa: E402

HP_CAMP, MAINT_CAMP, BOILER_CAMP, PMAX_CAMP = "24268690038", "24279798229", "24132507744", "24295088845"
HPM_AG, BM_AG = "204129717567", "204129718287"
HPM_ADS = ["825863405664", "825863405667"]
HPM_URL = "https://offer.ambientcoolingandheating.com/heat-pump-maintenance/"
BM_URL = "https://offer.ambientcoolingandheating.com/boiler-maintenance/"
HPM_SITELINK = "424481133551"
DEFERRED_LABEL_NAME, NEW_LABEL = "DEFERRED_BUDGET", "MAINTENANCE_TEST"
NEW_LABEL_DESC = "Maintenance service re-admitted 2026-09-30 as a monitored test with its own budget room"
BUDGET_PLAN, ENABLE_PLAN, HELD_PAYLOAD = "AMB-0930-HPM-BUDGET-1", "AMB-0930-HPM-ENABLE-1", "AMB-0930-BM-HELD-PAYLOAD"
WO_HPM = CLIENT_DIR / "work-orders" / "work-order-heat-pump-maintenance-2026-09-30.yaml"
WO_BM = CLIENT_DIR / "work-orders" / "work-order-boiler-maintenance-2026-09-30.yaml"
CAP_MONTHLY, CAP_DAILY, DAYS = 10000.00, 325.00, 30.4
TARGET = {"child_customer_id": CID, "exact_child_account_name": EXACT_NAME}
BARRED = re.compile(r"24/7|24-7|24 hours|same[- ]day|emergenc|licens|insured|guarantee|warrant|financ|\$\s?\d|% off|discount|"
                    r"rebate|tax credit|years? (of )?experience|\d+\+? years|\d(\.\d)? ?stars?|top[- ]rated|best\b|#1|"
                    r"certified|fast response|within \d+ (min|hour)|award|propert", re.I)


def fresh(c):
    s = {"campaigns": {}, "budgets": {}}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, campaign_budget.id,
            campaign_budget.amount_micros, campaign_budget.explicitly_shared, campaign.target_spend.cpc_bid_ceiling_micros
            FROM campaign WHERE campaign.status != 'REMOVED'"""):
        s["campaigns"][str(r.campaign.id)] = dict(name=r.campaign.name, status=E(r.campaign.status),
                                                  type=E(r.campaign.advertising_channel_type), budget_id=str(r.campaign_budget.id),
                                                  micros=r.campaign_budget.amount_micros, shared=r.campaign_budget.explicitly_shared,
                                                  ceiling_micros=r.campaign.target_spend.cpc_bid_ceiling_micros)
    s["enabled_total"] = round(sum(v["micros"] for v in s["campaigns"].values() if v["status"] == "ENABLED") / 1e6, 2)
    s["pmax"] = s["campaigns"].get(PMAX_CAMP)
    ag = q(c, f"SELECT campaign.id, ad_group.id, ad_group.status, ad_group.name FROM ad_group WHERE ad_group.id IN ({HPM_AG},{BM_AG})")
    s["ad_groups"] = {str(r.ad_group.id): dict(status=E(r.ad_group.status), name=r.ad_group.name, campaign=str(r.campaign.id)) for r in ag}
    s["ads"] = {}
    for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.type, ad_group_ad.ad.final_urls,
            ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.policy_topic_entries,
            ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions
            FROM ad_group_ad WHERE ad_group.id IN ({HPM_AG},{BM_AG}) AND ad_group_ad.status != 'REMOVED'"""):
        a = r.ad_group_ad
        s["ads"][str(a.ad.id)] = dict(ad_group=str(r.ad_group.id), status=E(a.status), type=E(a.ad.type), urls=list(a.ad.final_urls),
                                      approval=E(a.policy_summary.approval_status),
                                      topics=[(t.topic, E(t.type_)) for t in a.policy_summary.policy_topic_entries],
                                      h=[x.text for x in a.ad.responsive_search_ad.headlines],
                                      d=[x.text for x in a.ad.responsive_search_ad.descriptions])
    s["keywords"] = {}
    s["ag_negatives"] = {}
    for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type, ad_group_criterion.negative, ad_group_criterion.status,
            ad_group_criterion.approval_status, ad_group_criterion.system_serving_status FROM ad_group_criterion
            WHERE ad_group.id IN ({HPM_AG},{BM_AG}) AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'"""):
        k = r.ad_group_criterion
        row = dict(text=k.keyword.text, match=E(k.keyword.match_type), status=E(k.status), approval=E(k.approval_status),
                   serving=E(k.system_serving_status))
        (s["ag_negatives"] if k.negative else s["keywords"]).setdefault(str(r.ad_group.id), []).append(row)
    for v in list(s["keywords"].values()) + list(s["ag_negatives"].values()):
        v.sort(key=lambda x: (x["text"], x["match"]))
    s["labels"] = {r.label.name: str(r.label.id) for r in q(c, "SELECT label.id, label.name FROM label WHERE label.status = 'ENABLED'")}
    s["hpm_labels"] = sorted(r.label.name for r in q(c, f"SELECT ad_group.id, label.name FROM ad_group_label WHERE ad_group.id = {HPM_AG}"))
    s["hpm_sitelink_link"] = [E(r.campaign_asset.status) for r in q(c, f"""SELECT campaign.id, asset.id, campaign_asset.status,
            campaign_asset.field_type FROM campaign_asset WHERE campaign.id = {HP_CAMP} AND asset.id = {HPM_SITELINK}
            AND campaign_asset.field_type = 'SITELINK'""")]
    return s


def lp_gate():
    d = json.loads((SNAP / "maint-lp-qa-2026-09-30.json").read_text(encoding="utf-8"))
    out = {}
    for svc, key in (("Heat Pump Maintenance", "HPM"), ("Boiler Maintenance", "BM")):
        r = d[svc]["desktop"]; m = d[svc]["mobile"]
        rendered_bad = r["analysis"]["rendered_phone_counts"]["761-0932"] + m["analysis"]["rendered_phone_counts"]["761-0932"]
        tel_ok = all(re.sub(r"\D", "", unquote(t["href"]))[-10:] in ("4107056354", "4109141456") for t in r["tel"] + m["tel"])
        out[key] = dict(http=r["status"], final_url=r["final_url"], h1=r["h1"], off_service=r["analysis"]["off_service_headings_or_ctas"],
                        barred=[b for b in r["analysis"]["barred_hits"] if b not in ("review", "guarantee")],
                        forms=sorted({f["id"] for f in r["forms"]}), rendered_761=rendered_bad, tel_ok=tel_ok,
                        d7_server_side=d[svc]["d7_probe"]["marker_in_probe_server_html"],
                        d7_replay=d[svc]["d7_probe"]["marker_in_clean_server_html"])
    out["HPM"]["gate"] = ("PASS_WITH_DEFECTS" if out["HPM"]["http"] == 200 and out["HPM"]["final_url"] == HPM_URL
                          and any("Heat Pump Maintenance" in h for h in out["HPM"]["h1"]) and out["HPM"]["rendered_761"] == 0
                          and out["HPM"]["tel_ok"] and out["HPM"]["forms"] == ["gform_1"] and not out["HPM"]["barred"] else "FAIL")
    installation_heads = [h for h in out["BM"]["off_service"] if h.startswith("installation")]
    out["BM"]["gate"] = "FAIL_D2" if len(installation_heads) >= 3 else "RECHECK"
    return out


def build(c):
    s = fresh(c)
    errors, eb, ee = [], [], []  # general, BUDGET-1, ENABLE-1
    hp, mt = s["campaigns"][HP_CAMP], s["campaigns"][MAINT_CAMP]
    lp = lp_gate()
    # ---------------- BUDGET-1 ----------------
    hp_to, mt_to = 30_000_000, 30_000_000
    after_total = round(s["enabled_total"] + (hp_to - hp["micros"]) / 1e6 + (mt_to - mt["micros"]) / 1e6, 2)
    pmax_micros = s["pmax"]["micros"] if s["pmax"] else 0
    maint_enabled_ads = [a for a in q(c, f"SELECT campaign.id, ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad WHERE campaign.id = {MAINT_CAMP} AND ad_group_ad.status = 'ENABLED'")]
    budget = {
        "plan": BUDGET_PLAN, "target": TARGET, "work_order": str(WO_HPM.relative_to(ROOT)).replace("\\", "/"),
        "approval_type": "SEPARATE EXPLICIT BUDGET APPROVAL",
        "preconditions": {
            "hp_campaign": {"id": HP_CAMP, "status": hp["status"], "budget_id": hp["budget_id"], "amount_micros": hp["micros"], "shared": hp["shared"]},
            "maintenance_campaign": {"id": MAINT_CAMP, "status": mt["status"], "budget_id": mt["budget_id"], "amount_micros": mt["micros"],
                                     "shared": mt["shared"], "enabled_ads": len(maint_enabled_ads)},
            "enabled_daily_total_usd": s["enabled_total"],
            "pmax_pilot": {"id": PMAX_CAMP, "status": s["pmax"]["status"] if s["pmax"] else None, "budget_usd": pmax_micros / 1e6},
        },
        "operations": [
            {"op": "UPDATE", "resource": "campaign_budget", "id": hp["budget_id"], "campaign": HP_CAMP, "field": "amount_micros",
             "from": hp["micros"], "to": hp_to},
            {"op": "UPDATE", "resource": "campaign_budget", "id": mt["budget_id"], "campaign": MAINT_CAMP, "field": "amount_micros",
             "from": mt["micros"], "to": mt_to},
        ],
        "math": {"enabled_daily_total_after_usd": after_total, "monthly_max_enabled_usd": round(after_total * DAYS, 2),
                 "monthly_max_if_pmax_enabled_usd": round((after_total + pmax_micros / 1e6) * DAYS, 2),
                 "cap_monthly_usd": CAP_MONTHLY, "cap_daily_usd": CAP_DAILY, "basis": "daily x 30.4",
                 "real_spend_effect": "HP campaign monthly ceiling $456.00 -> $912.00; Maintenance campaign has 0 enabled ads, so its cut changes no delivery. Net possible real spend increase <= $456.00/month."},
        "readback_assertions": [f"budget {hp['budget_id']} amount_micros == {hp_to}", f"budget {mt['budget_id']} amount_micros == {mt_to}",
                                f"enabled daily total == {after_total:.2f}", "no campaign/ad group/ad/keyword status changed",
                                "PMax 24295088845 still PAUSED at its own $20 budget"],
    }
    if hp["micros"] != 15_000_000 or mt["micros"] != 45_000_000:
        eb.append("budget preconditions drifted")
    if hp["shared"] or mt["shared"]:
        eb.append("a budget is shared")
    if maint_enabled_ads:
        eb.append("Maintenance campaign has enabled ads - its budget is not idle")
    if after_total > CAP_DAILY or after_total * DAYS > CAP_MONTHLY or (after_total + pmax_micros / 1e6) * DAYS > CAP_MONTHLY:
        eb.append("cap breach")
    # ---------------- ENABLE-1 ----------------
    hpm_ads = {k: v for k, v in s["ads"].items() if v["ad_group"] == HPM_AG}
    kws = s["keywords"].get(HPM_AG, [])
    negs = s["ag_negatives"].get(HPM_AG, [])
    enable = {
        "plan": ENABLE_PLAN, "target": TARGET, "work_order": str(WO_HPM.relative_to(ROOT)).replace("\\", "/"),
        "approval_type": "SEPARATE EXPLICIT ENABLE APPROVAL, only after Phase 6 readback QA",
        "requires": {"executed_first": BUDGET_PLAN, "receipt": f"receipts/{BUDGET_PLAN}-EXECUTED.json with readback_fail == 0"},
        "preconditions": {
            "campaign": {"id": HP_CAMP, "status": hp["status"], "budget_micros_required": hp_to},
            "ad_group": {"id": HPM_AG, **s["ad_groups"][HPM_AG]},
            "ads": {k: {kk: v[kk] for kk in ("status", "type", "urls", "approval", "topics")} for k, v in sorted(hpm_ads.items())},
            "enabled_ads_before": sum(1 for v in hpm_ads.values() if v["status"] == "ENABLED"),
            "keywords": kws, "ad_group_negatives": negs,
            "labels_on_ad_group": s["hpm_labels"], "label_exists": {NEW_LABEL: NEW_LABEL in s["labels"], DEFERRED_LABEL_NAME: s["labels"].get(DEFERRED_LABEL_NAME)},
            "hp_maintenance_sitelink_link": s["hpm_sitelink_link"],
            "landing_page_gate": {k: lp["HPM"][k] for k in ("gate", "http", "final_url", "forms", "rendered_761", "tel_ok")},
        },
        "operations": [
            {"op": "CREATE", "resource": "label", "temp_id": -1, "name": NEW_LABEL, "description": NEW_LABEL_DESC},
            {"op": "CREATE", "resource": "ad_group_label", "ad_group": HPM_AG, "label": "temp:-1"},
            {"op": "REMOVE", "resource": "ad_group_label", "ad_group": HPM_AG, "label_id": s["labels"].get(DEFERRED_LABEL_NAME)},
            *[{"op": "UPDATE", "resource": "ad_group_ad", "ad_group": HPM_AG, "ad": a, "field": "status", "from": "PAUSED", "to": "ENABLED"}
              for a in HPM_ADS],
        ],
        "not_changed": ["keywords (3 already ENABLED)", "ad-group routing negatives (10)", "final URLs", "HP Maintenance sitelink stays PAUSED",
                        "budgets and CPC ceilings", "conversion goals", "every other ad group"],
        "stop_loss": ["pause both ads if HP Maintenance spend >= $300 with no WhatConverts lead carrying a click id",
                      "pause both ads if Heat Pump campaign search_budget_lost_impression_share > 10% over 7 complete days",
                      "pause both ads if Heat Pump Repair/Installation/Replacement impressions fall > 30% vs the 14 days before enablement "
                      "while Maintenance takes > 30% of campaign spend",
                      "pause both ads if either ad or the page picks up a policy limit or the page fails QA"],
        "checkpoints": ["day 2", "day 7", "day 14"],
        "readback_assertions": ["label MAINTENANCE_TEST exists and is linked to 204129717567", "DEFERRED_BUDGET no longer linked to 204129717567",
                                "ads 825863405664 and 825863405667 ENABLED, final URL == canonical, approval APPROVED",
                                "enabled RSAs in 204129717567 == 2 (cap 3)", "3 keywords ENABLED/ELIGIBLE, 10 negatives unchanged",
                                "HP campaign budget $30 / ceiling $35 / Mon-Fri 08-16 / 75 presence targets unchanged",
                                "sitelink 424481133551 link still PAUSED", "no other ad group or ad changed"],
    }
    # ---------------- validators ----------------
    for k, v in hpm_ads.items():
        if v["status"] != "PAUSED" or v["approval"] != "APPROVED" or v["urls"] != [HPM_URL] or v["topics"]:
            ee.append(f"ad {k} precondition drift: {v['status']} {v['approval']} {v['urls']} {v['topics']}")
        for t in v["h"]:
            if len(t) > 30: ee.append(f"headline > 30: {t}")
            if BARRED.search(t): ee.append(f"barred headline: {t}")
        for t in v["d"]:
            if len(t) > 90: ee.append(f"description > 90: {t}")
            if BARRED.search(t): ee.append(f"barred description: {t}")
    if sorted(hpm_ads) != sorted(HPM_ADS): ee.append(f"HP Maintenance ad set changed: {sorted(hpm_ads)}")
    if any(k["match"] == "BROAD" for k in kws): ee.append("broad keyword present")
    if len([k for k in kws if k["status"] == "ENABLED" and k["serving"] == "ELIGIBLE"]) != 3: ee.append("expected 3 enabled eligible keywords")
    if s["ad_groups"][HPM_AG]["status"] != "ENABLED" or hp["status"] != "ENABLED": ee.append("HP campaign or ad group not ENABLED")
    if NEW_LABEL in s["labels"]: ee.append("MAINTENANCE_TEST label already exists")
    if DEFERRED_LABEL_NAME not in s["hpm_labels"]: ee.append("DEFERRED_BUDGET not linked")
    if s["hpm_sitelink_link"] != ["PAUSED"]: ee.append(f"HP maintenance sitelink link state {s['hpm_sitelink_link']}")
    if lp["HPM"]["gate"] != "PASS_WITH_DEFECTS": ee.append(f"HP maintenance page gate {lp['HPM']}")
    reach = json.loads((SNAP / "maint-neg-reach-2026-09-30.json").read_text(encoding="utf-8"))
    rc = reach[HPM_AG]["stats"].get("REAL_CONFLICT", 0)
    only_routing = all(k.startswith("ad_group | repair") for k in reach[HPM_AG]["blockers"])
    enable["preconditions"]["negative_reachability"] = {"real_conflicts": rc, "all_are_intended_routing": only_routing}
    if rc and not only_routing: ee.append("negative reachability conflict")
    return s, lp, budget, enable, {'general': errors, BUDGET_PLAN: eb, ENABLE_PLAN: ee}


def held_boiler_payload(s, lp):
    rsas = [
        dict(h=["Boiler Maintenance", "Boiler Maintenance Visit", "Severn Boiler Maintenance", "Columbia Boiler Maintenance",
                "Severna Park Boiler Care", "Book Boiler Maintenance", "Request a Free Quote", "Trained HVAC Technicians",
                "Central Maryland Service", "Boiler Care Near You", "Plan Routine Boiler Care", "Boiler Maintenance Quote",
                "Boiler System Check-Up", "Call Mon-Fri, 8 a.m.-4 p.m.", "Maryland Boiler Maintenance"],
             d=["Boiler maintenance for homes in Severn, Severna Park and Columbia, Maryland.",
                "Our technicians review the boiler's condition and explain what it needs.",
                "Request a free boiler maintenance quote from Ambient Cooling and Heating.",
                "Call Mon-Fri, 8 a.m. to 4 p.m., or request your free quote online."],
             path=["Boiler", "Maintenance"]),
        dict(h=["Boiler Due For A Service?", "Last Boiler Service Unknown?", "Uneven Heat From Your Boiler?", "Book A Boiler Visit",
                "Boiler Maintenance Near You", "Severn Boiler Service", "Annapolis Boiler Maintenance", "Glen Burnie Boiler Care",
                "Routine Boiler Care", "Request A Maintenance Visit", "Free Boiler Maintenance Quote", "Clear Service Options",
                "Discuss Your Boiler's Needs", "Central Maryland Boilers", "Ambient Cooling & Heating"],
             d=["Not sure when your boiler was last serviced? Request a maintenance visit.",
                "We review operation and condition, then explain any recommended next steps.",
                "Boiler maintenance across Central Maryland from Ambient Cooling and Heating.",
                "Request a free quote online or call Mon-Fri, 8 a.m. to 4 p.m."],
             path=["Boiler", "Maintenance"]),
    ]
    errs = []
    boiler_heads = set()
    for r in q(client_c, f"SELECT campaign.id, ad_group_ad.ad.responsive_search_ad.headlines FROM ad_group_ad WHERE campaign.id = {BOILER_CAMP} AND ad_group_ad.status != 'REMOVED'"):
        boiler_heads |= {x.text.lower() for x in r.ad_group_ad.ad.responsive_search_ad.headlines}
    overlap = []
    for i, r in enumerate(rsas):
        if len(r["h"]) != 15 or len(set(x.lower() for x in r["h"])) != 15: errs.append(f"RSA{i} needs 15 distinct headlines")
        if len(r["d"]) != 4: errs.append(f"RSA{i} needs 4 descriptions")
        for t in r["h"]:
            if len(t) > 30: errs.append(f"RSA{i} headline > 30: {t} ({len(t)})")
            if BARRED.search(t): errs.append(f"RSA{i} barred: {t}")
        for t in r["d"]:
            if len(t) > 90: errs.append(f"RSA{i} description > 90: {t} ({len(t)})")
            if BARRED.search(t): errs.append(f"RSA{i} barred: {t}")
        for p in r["path"]:
            if len(p) > 15: errs.append(f"RSA{i} path > 15: {p}")
        overlap.append(sorted(x for x in r["h"] if x.lower() in boiler_heads))
    shared_between = sorted(set(x.lower() for x in rsas[0]["h"]) & set(x.lower() for x in rsas[1]["h"]))
    if shared_between: errs.append(f"RSA A/B share headlines {shared_between}")
    payload = {
        "payload": HELD_PAYLOAD, "status": "HELD - NOT FOR APPROVAL - do not create while the destination fails D2",
        "target": TARGET, "work_order": str(WO_BM.relative_to(ROOT)).replace("\\", "/"),
        "ad_group": {"id": BM_AG, **s["ad_groups"][BM_AG]}, "final_url": BM_URL,
        "destination_gate_2026_09_30": lp["BM"],
        "when_page_passes": {
            "create_paused": [f"2 RSAs below -> {BM_URL}"],
            "keywords_to_enable": ["boiler maintenance PHRASE", "boiler maintenance EXACT"],
            "keywords_to_keep_paused": ["boiler service PHRASE", "boiler service EXACT (mixed repair/maintenance intent; Boiler Repair owns repair)"],
            "ad_group_negative_to_add": ["oil PHRASE (oil is out of scope; Boiler Repair already carries it)"],
            "budget_gate": "Boiler Services is pacing above its monthly allowance at $45/day; enabling maintenance inside it needs budget room first",
        },
        "rsas": rsas, "validator_errors": errs, "headline_overlap_with_existing_boiler_ads": overlap,
    }
    payload["content_sha256_12"] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12].upper()
    return payload


def mutate_ops(c, plan, s):
    ops = []
    if plan["plan"] == BUDGET_PLAN:
        for o in plan["operations"]:
            m = c.get_type("MutateOperation"); u = m.campaign_budget_operation.update
            u.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(CID, o["id"]); u.amount_micros = o["to"]
            m.campaign_budget_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["amount_micros"])); ops.append(m)
        return ops
    lsvc, agsvc, aga = c.get_service("LabelService"), c.get_service("AdGroupService"), c.get_service("AdGroupAdService")
    for o in plan["operations"]:
        m = c.get_type("MutateOperation")
        if o["resource"] == "label":
            m.label_operation.create.resource_name = lsvc.label_path(CID, o["temp_id"])
            m.label_operation.create.name = o["name"]; m.label_operation.create.text_label.description = o["description"]
        elif o["resource"] == "ad_group_label" and o["op"] == "CREATE":
            m.ad_group_label_operation.create.ad_group = agsvc.ad_group_path(CID, o["ad_group"])
            m.ad_group_label_operation.create.label = lsvc.label_path(CID, -1)
        elif o["resource"] == "ad_group_label" and o["op"] == "REMOVE":
            m.ad_group_label_operation.remove = c.get_service("AdGroupLabelService").ad_group_label_path(CID, o["ad_group"], o["label_id"])
        elif o["resource"] == "ad_group_ad":
            u = m.ad_group_ad_operation.update
            u.resource_name = aga.ad_group_ad_path(CID, o["ad_group"], o["ad"]); u.status = c.enums.AdGroupAdStatusEnum.ENABLED
            m.ad_group_ad_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
        else:
            raise SystemExit(f"unsupported op {o}")
        ops.append(m)
    return ops


def send(c, ops, validate_only):
    rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.validate_only = validate_only
    rq.mutate_operations.extend(ops)
    return c.get_service("GoogleAdsService").mutate(request=rq)


def readback(c, which):
    s = fresh(c); fails = []
    hp, mt = s["campaigns"][HP_CAMP], s["campaigns"][MAINT_CAMP]
    if which in ("budget", "enable"):
        if hp["micros"] != 30_000_000: fails.append(f"HP budget {hp['micros']}")
        if mt["micros"] != 30_000_000: fails.append(f"Maintenance budget {mt['micros']}")
        if s["enabled_total"] != 305.00: fails.append(f"enabled total {s['enabled_total']}")
        if not s["pmax"] or s["pmax"]["status"] != "PAUSED": fails.append("PMax not paused")
    if which == "enable":
        for a in HPM_ADS:
            v = s["ads"][a]
            if v["status"] != "ENABLED" or v["urls"] != [HPM_URL] or v["approval"] != "APPROVED": fails.append(f"ad {a} {v['status']} {v['approval']}")
        if NEW_LABEL not in s["hpm_labels"] or DEFERRED_LABEL_NAME in s["hpm_labels"]: fails.append(f"labels {s['hpm_labels']}")
    if which == "prep":
        for a in HPM_ADS:
            v = s["ads"][a]
            if v["status"] != "PAUSED" or v["urls"] != [HPM_URL] or v["approval"] != "APPROVED" or v["topics"]: fails.append(f"ad {a} {v}")
    if s["hpm_sitelink_link"] != ["PAUSED"]: fails.append("HP maintenance sitelink link changed")
    if s["ad_groups"][BM_AG]["status"] != "ENABLED" or any(v["status"] == "ENABLED" for v in s["ads"].values() if v["ad_group"] == BM_AG):
        fails.append("Boiler Maintenance changed")
    if any(k["status"] == "ENABLED" for k in s["keywords"].get(BM_AG, [])): fails.append("Boiler Maintenance keyword enabled")
    return s, fails


client_c = None


def main():
    global client_c
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["plan", "readback", "execute"])
    ap.add_argument("--plan"); ap.add_argument("--fp"); a = ap.parse_args()
    c = client(); client_c = c
    ident = identity_gate(c, verbose=True)
    s, lp, budget, enable, errs = build(c)
    errors = errs['general']
    cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
    for p in (budget, enable):
        assert_no_embedded_secrets(p)
        assert_target_matches(p, cl, observed_account_name=ident["descriptive_name"])
    for wo in (WO_HPM, WO_BM):
        e = validate_work_order(yaml.safe_load(wo.read_text(encoding="utf-8")), cl)
        if e: errors.append(f"{wo.name}: {e}")
    fps = {BUDGET_PLAN: approval_code(budget), ENABLE_PLAN: approval_code(enable)}
    if a.cmd == "plan":
        for p in (budget, enable):
            try:
                send(c, mutate_ops(c, p, s), validate_only=True); p_vo = "VALIDATE_OK"
            except Exception as ex:  # noqa: BLE001
                p_vo = "VALIDATE_FAIL: " + str(ex)[-400:]; errs[p["plan"]].append(p_vo)
            doc = dict(p); doc["fingerprint"] = fps[p["plan"]]; doc["operation_count"] = len(p["operations"])
            doc["validate_only"] = p_vo; doc["generated_local"] = datetime.datetime.now(TZ).isoformat(); doc["errors"] = errors + errs[p["plan"]]
            (PLANS / f"{p['plan']}.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
            print(f"PLAN {p['plan']:24s} {fps[p['plan']]}  ops={len(p['operations'])}  {p_vo[:80]}")
        held = held_boiler_payload(s, lp)
        (PLANS / f"{HELD_PAYLOAD}.json").write_text(json.dumps(held, indent=1), encoding="utf-8")
        print(f"HELD {HELD_PAYLOAD} sha {held['content_sha256_12']} errors={held['validator_errors']} overlap={held['headline_overlap_with_existing_boiler_ads']}")
        print("LP gate HPM:", lp["HPM"]["gate"], "| BM:", lp["BM"]["gate"])
        print("budget math:", budget["math"])
        print("errors:", errs)
        return
    if a.cmd == "readback":
        _, fails = readback(c, "prep")
        print("PHASE 6 READBACK (no writes):", "PASS" if not fails else fails)
        return
    # execute
    sys.exit("WITHDRAWN 2026-09-30b: AMB-0930-HPM-BUDGET-1 / AMB-0930-HPM-ENABLE-1 must never execute (client CPL requirement; Heat Pump Maintenance on HOLD).")
    if a.plan not in fps or a.fp != fps[a.plan] or errors or errs[a.plan]:
        sys.exit(f"ABORT: {a.plan} fingerprint {fps.get(a.plan)} != {a.fp} or errors {errors + errs.get(a.plan, [])}")
    plan = budget if a.plan == BUDGET_PLAN else enable
    if a.plan == ENABLE_PLAN:
        rp = RECEIPTS / f"{BUDGET_PLAN}-EXECUTED.json"
        if not rp.exists() or json.loads(rp.read_text(encoding="utf-8")).get("readback_fail") != 0:
            sys.exit("ABORT: BUDGET-1 not executed with a clean readback")
    rec = {"plan": a.plan, "fingerprint": a.fp, "started_local": datetime.datetime.now(TZ).isoformat()}
    out = RECEIPTS / f"{a.plan}-EXECUTED.json"
    try:
        resp = send(c, mutate_ops(c, plan, s), validate_only=False)
    except Exception as ex:  # noqa: BLE001
        rec["error"] = str(ex)[:1500]; out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        sys.exit(f"STOP: mutate failed, nothing partial (atomic): {str(ex)[:400]}")
    rec["results"] = [str(r) for r in resp.mutate_operation_responses]
    _, fails = readback(c, "budget" if a.plan == BUDGET_PLAN else "enable")
    rec["readback_fail"] = len(fails); rec["readback_fails"] = fails
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat()
    out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(f"{a.plan} EXECUTED; readback {'PASS' if not fails else fails}")


if __name__ == "__main__":
    main()
