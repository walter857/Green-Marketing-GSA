#!/usr/bin/env python3
"""Ambient | 2026-10-02 | AMB-1002-EMER-ENABLE-1: enable the Emergency Heating Repair ads and keywords. BUILD / EXECUTE.

  build                      fresh read, gates, plan + fingerprint, validate_only (0 writes)
  execute <FINGERPRINT> <N>  only after the exact approval line; re-verifies state, writes, reads back

Gates (all re-checked at execute): AMB-1002-EMER-CREATE-1 receipt EXECUTED with readback 18/18; owner confirmed business-hours
dispatch 2026-10-02 (work order); every target resource exists in the exact pre-state below; campaign 24257819463 still
ENABLED, $85 budget, $18 ceiling, Mon-Fri 08-16, 75 locations, tablet -100%. Ads under Google review may be enabled: they
serve only after approval. No budget, bid, schedule, location, conversion, negative or URL change.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, PLANS, RECEIPTS, E, CID, EXACT_NAME, CLIENT_DIR  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402
import yaml  # noqa: E402

NAME = "AMB-1002-EMER-ENABLE-1"
CAMP, AG = "24257819463", "204129717047"
ADS = ["826702584886", "826702584889"]
KWS = {"3304047112": ("emergency furnace repair", "EXACT"), "320791640594": ("emergency heat repair", "EXACT"),
       "777693505": ("emergency heater repair", "PHRASE"), "1734598708": ("emergency heating repair", "PHRASE"),
       "299713058575": ("emergency heating repair", "EXACT"), "4213560696": ("emergency furnace repair", "PHRASE")}
LABELS = {"22294515713": "WAITING_LP", "22294515722": "WAITING_AVAILABILITY"}
WO = "work-order-emergency-heating-repair-lp-2026-10-01.yaml"


def state(c):
    s = {}
    r = q(c, f"""SELECT campaign.status, campaign.target_spend.cpc_bid_ceiling_micros, campaign_budget.amount_micros, campaign_budget.id
            FROM campaign WHERE campaign.id = {CAMP}""")[0]
    s["campaign"] = dict(status=E(r.campaign.status), ceiling=r.campaign.target_spend.cpc_bid_ceiling_micros, budget=r.campaign_budget.amount_micros,
                         budget_id=str(r.campaign_budget.id))
    crit = q(c, f"""SELECT campaign_criterion.type, campaign_criterion.negative, campaign_criterion.device.type, campaign_criterion.bid_modifier,
            campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour
            FROM campaign_criterion WHERE campaign.id = {CAMP}""")
    s["schedule"] = sorted((E(x.campaign_criterion.ad_schedule.day_of_week), x.campaign_criterion.ad_schedule.start_hour, x.campaign_criterion.ad_schedule.end_hour)
                           for x in crit if E(x.campaign_criterion.type) == "AD_SCHEDULE")
    s["locations"] = sum(1 for x in crit if E(x.campaign_criterion.type) == "LOCATION" and not x.campaign_criterion.negative)
    s["tablet"] = [("bid_modifier" in x.campaign_criterion, x.campaign_criterion.bid_modifier) for x in crit
                   if E(x.campaign_criterion.type) == "DEVICE" and E(x.campaign_criterion.device.type) == "TABLET"]
    r = q(c, f"SELECT ad_group.status, ad_group.labels, ad_group.name FROM ad_group WHERE ad_group.id = {AG}")[0]
    s["ad_group"] = dict(status=E(r.ad_group.status), name=r.ad_group.name, labels=sorted(l.split("/")[-1] for l in r.ad_group.labels))
    s["ads"] = {str(x.ad_group_ad.ad.id): dict(status=E(x.ad_group_ad.status), url=list(x.ad_group_ad.ad.final_urls),
                                               approval=E(x.ad_group_ad.policy_summary.approval_status), review=E(x.ad_group_ad.policy_summary.review_status))
                for x in q(c, f"""SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls, ad_group_ad.policy_summary.approval_status,
                    ad_group_ad.policy_summary.review_status FROM ad_group_ad WHERE ad_group.id = {AG} AND ad_group_ad.status != 'REMOVED'""")}
    s["keywords"] = {str(x.ad_group_criterion.criterion_id): dict(text=x.ad_group_criterion.keyword.text, match=E(x.ad_group_criterion.keyword.match_type),
                                                                  status=E(x.ad_group_criterion.status), approval=E(x.ad_group_criterion.approval_status),
                                                                  negative=x.ad_group_criterion.negative)
                     for x in q(c, f"""SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
                         ad_group_criterion.status, ad_group_criterion.approval_status, ad_group_criterion.negative FROM ad_group_criterion
                         WHERE ad_group.id = {AG} AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'""")}
    return s


def gates(s):
    g = []
    rec = json.loads((RECEIPTS / "AMB-1002-EMER-CREATE-1-EXECUTED.json").read_text(encoding="utf-8"))
    g.append(("CREATE receipt EXECUTED, readback all PASS", rec["status"] == "EXECUTED" and all(x["pass"] for x in rec["readback"])))
    wo = yaml.safe_load((CLIENT_DIR / "work-orders" / WO).read_text(encoding="utf-8"))
    cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
    g.append(("work order valid", not validate_work_order(wo, cl)))
    g.append(("owner dispatch confirmation recorded", "OWNER CONFIRMED" in str(wo["work_order"]["inputs"].get("availability_confirmed_2026_10_02", ""))))
    g.append(("campaign ENABLED, $85, $18 ceiling", s["campaign"]["status"] == "ENABLED" and s["campaign"]["budget"] == 85_000_000 and s["campaign"]["ceiling"] == 18_000_000))
    g.append(("schedule Mon-Fri 08-16 (5 rows)", len(s["schedule"]) == 5 and all(x[1:] == (8, 16) for x in s["schedule"])))
    g.append(("75 locations", s["locations"] == 75))
    g.append(("tablet -100%", s["tablet"] == [(True, 0.0)]))
    g.append(("ad group ENABLED", s["ad_group"]["status"] == "ENABLED" and s["ad_group"]["name"] == "SKAG | Emergency Heating Repair"))
    g.append(("exactly the 2 new ads exist, PAUSED, on the emergency URL", sorted(s["ads"]) == sorted(ADS) and all(
        a["status"] == "PAUSED" and a["url"] == ["https://offer.ambientcoolingandheating.com/emergency-heating-repair/"] for a in s["ads"].values())))
    g.append(("no ad DISAPPROVED", all(a["approval"] != "DISAPPROVED" for a in s["ads"].values())))
    pos = {k: v for k, v in s["keywords"].items() if not v["negative"]}
    g.append(("the 6 keywords exist PAUSED with expected text/match", sorted(pos) == sorted(KWS) and all(
        (pos[k]["text"], pos[k]["match"]) == KWS[k] and pos[k]["status"] == "PAUSED" for k in KWS)))
    g.append(("no keyword DISAPPROVED", all(v["approval"] != "DISAPPROVED" for v in pos.values())))
    g.append(("both holding labels present", all(l in s["ad_group"]["labels"] for l in LABELS)))
    return g


def ops_payload():
    return ([dict(op="ENABLE_AD", ad_group_id=AG, ad_id=a) for a in ADS] +
            [dict(op="ENABLE_KEYWORD", ad_group_id=AG, criterion_id=k, text=t, match=m) for k, (t, m) in KWS.items()] +
            [dict(op="REMOVE_AD_GROUP_LABEL", ad_group_id=AG, label_id=l, label=n) for l, n in LABELS.items()])


def build_ops(c, payload):
    AGA, AGC, AGL = c.get_service("AdGroupAdService"), c.get_service("AdGroupCriterionService"), c.get_service("AdGroupLabelService")
    fm = field_mask_pb2.FieldMask(paths=["status"])
    ad_ops, kw_ops, lb_ops = [], [], []
    for p in payload:
        if p["op"] == "ENABLE_AD":
            o = c.get_type("AdGroupAdOperation"); o.update.resource_name = AGA.ad_group_ad_path(CID, AG, p["ad_id"])
            o.update.status = c.enums.AdGroupAdStatusEnum.ENABLED; o.update_mask.CopyFrom(fm); ad_ops.append(o)
        elif p["op"] == "ENABLE_KEYWORD":
            o = c.get_type("AdGroupCriterionOperation"); o.update.resource_name = AGC.ad_group_criterion_path(CID, AG, p["criterion_id"])
            o.update.status = c.enums.AdGroupCriterionStatusEnum.ENABLED; o.update_mask.CopyFrom(fm); kw_ops.append(o)
        elif p["op"] == "REMOVE_AD_GROUP_LABEL":
            o = c.get_type("AdGroupLabelOperation"); o.remove = AGL.ad_group_label_path(CID, AG, p["label_id"]); lb_ops.append(o)
    return [("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest", ad_ops, "enable 2 RSAs"),
            ("AdGroupCriterionService", "mutate_ad_group_criteria", "MutateAdGroupCriteriaRequest", kw_ops, "enable 6 keywords"),
            ("AdGroupLabelService", "mutate_ad_group_labels", "MutateAdGroupLabelsRequest", lb_ops, "remove 2 holding labels")]


def send(c, svc, method, req_type, ops, validate):
    rq = c.get_type(req_type); rq.customer_id = CID; rq.operations.extend(ops); rq.partial_failure = False; rq.validate_only = validate
    return getattr(c.get_service(svc), method)(request=rq)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    c = client()
    identity_gate(c, verbose=True)
    s = state(c)
    g = gates(s)
    for k, v in g:
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    if not all(v for _, v in g):
        sys.exit("HARD STOP: a gate failed")
    plan = dict(plan_name=NAME, customer_id=CID, exact_account_name=EXACT_NAME, never_write_to_mcc="3373711342", approval_class="enable",
                exact_service="Emergency Heating Repair", work_order=f"work-orders/{WO}",
                campaign={"id": CAMP, "name": "Search | NonBrand | Heating & Furnace Repair | Central MD | BOFU | 2026-09"},
                ad_group={"id": AG, "name": "SKAG | Emergency Heating Repair"},
                effective_url_after="https://offer.ambientcoolingandheating.com/emergency-heating-repair/",
                follows="AMB-1002-EMER-CREATE-1 AF13621050E2 (EXECUTED, readback 18/18)",
                unchanged={"budget": "$85/day 15885327972 (shared by all six repair ad groups - Emergency now competes for it)",
                           "bidding": "Maximize Clicks, $18 ceiling", "schedule": "Mon-Fri 08:00-16:00", "locations": "75 PRESENCE",
                           "devices": "tablet -100%", "conversions": "unchanged", "negatives": "unchanged; Heating/Furnace Repair keep PHRASE 'emergency' (routing)"},
                policy_note="Ads may still be UNDER REVIEW at execution; they serve only after Google approves them.",
                experiment_note="Activating Emergency changes traffic and budget competition inside 24257819463; from this timestamp the repair "
                                "comparison is configuration optimization, not a pure $18-ceiling test.",
                operations=ops_payload())
    plan["operation_count"] = len(plan["operations"])
    plan["fingerprint"] = approval_code({k: v for k, v in plan.items() if k != "fingerprint"})
    if mode == "build":
        pf = {}
        for svc, method, req, ops, label in build_ops(c, plan["operations"]):
            try:
                send(c, svc, method, req, ops, True); pf[label] = f"VALIDATED {len(ops)}"
            except Exception as ex:
                pf[label] = "FAILED: " + str(re.findall(r'message: "([^"]+)"', str(ex))[:3] or str(ex)[:300])
        print("preflight:", pf)
        if any(v.startswith("FAILED") for v in pf.values()):
            sys.exit("HARD STOP: validate_only failed - no plan written")
        (PLANS / f"{NAME}.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print(f"PLAN {NAME}: {plan['fingerprint']} / {plan['operation_count']} ops   state: ads {[(k, v['approval'], v['review']) for k, v in s['ads'].items()]}")
        return
    if mode != "execute" or len(sys.argv) != 4:
        sys.exit("usage: build | execute <FINGERPRINT> <N>")
    saved = json.loads((PLANS / f"{NAME}.json").read_text(encoding="utf-8"))
    fp = saved.pop("fingerprint")
    if not (fp == approval_code(saved) == plan["fingerprint"] == sys.argv[2].upper() and int(sys.argv[3]) == plan["operation_count"]):
        sys.exit(f"ABORT: fingerprint mismatch (file {fp}, live rebuild {plan['fingerprint']}, approved {sys.argv[2]})")
    out = RECEIPTS / f"{NAME}-EXECUTED.json"
    if out.exists():
        sys.exit(f"ABORT: receipt {out.name} already exists")
    rec = dict(plan=NAME, fingerprint=fp, started_local=datetime.datetime.now(TZ).isoformat(), done=[])
    for svc, method, req, ops, label in build_ops(c, plan["operations"]):
        try:
            resp = send(c, svc, method, req, ops, False)
            rec["done"].append({"step": label, "results": [r.resource_name for r in resp.results]})
        except Exception as ex:
            rec["status"] = "PARTIAL" if rec["done"] else "FAILED_NOTHING_WRITTEN"
            rec["failure"] = {"step": label, "error": re.findall(r'message: "([^"]+)"', str(ex))[:3] or str(ex)[:300]}
            out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
            sys.exit(f"STOPPED at {label}: {rec['failure']} (no retry)")
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat()
    s2 = state(c)
    chk = [("2 ads ENABLED", all(s2["ads"][a]["status"] == "ENABLED" for a in ADS)),
           ("6 keywords ENABLED", all(s2["keywords"][k]["status"] == "ENABLED" for k in KWS)),
           ("holding labels removed", not any(l in s2["ad_group"]["labels"] for l in LABELS)),
           ("campaign unchanged", s2["campaign"] == s["campaign"] and s2["schedule"] == s["schedule"] and s2["locations"] == s["locations"] and s2["tablet"] == s["tablet"]),
           ("URL unchanged", all(s2["ads"][a]["url"] == ["https://offer.ambientcoolingandheating.com/emergency-heating-repair/"] for a in ADS))]
    rec["readback"] = [{"check": k, "pass": v} for k, v in chk]
    rec["policy_at_readback"] = {a: (s2["ads"][a]["approval"], s2["ads"][a]["review"]) for a in ADS}
    rec["status"] = "EXECUTED" if all(v for _, v in chk) else "EXECUTED_READBACK_FAIL"
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    for k, v in chk:
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(f"{NAME} {fp}: {rec['status']} at {rec['finished_local']}; policy {rec['policy_at_readback']}")


if __name__ == "__main__":
    main()
