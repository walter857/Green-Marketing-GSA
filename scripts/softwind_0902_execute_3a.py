#!/usr/bin/env python3
"""EXECUTE PLAN-GA-LAUNCH-3A. Fingerprint F91589D9EA2A. 45 status enables."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from google.protobuf.field_mask_pb2 import FieldMask  # noqa: E402

CID, SURV, RETIRE = "1521725229", "24103511039", "24145053510"
FP = "F91589D9EA2A"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
PLN = ROOT / "clients/softwind-power-washing/plans"
G6 = ["202870585390", "202870585870", "202870585910",
      "202870586310", "202870586110", "202870586150"]
NAME6 = {"202870585390": "Power Washing", "202870585870": "Pressure Washing",
         "202870585910": "House Washing", "202870586310": "Soft Washing",
         "202870586110": "Driveway Pressure Washing",
         "202870586150": "Patio Pressure Washing"}
GUARD_KW = {"384030528226", "502487923397"}
GUARD_ADS = {"819975939528", "819975939531", "819975939342", "819975939345"}
CREATED = json.loads((SNAP / "launch1-created-ids.json").read_text(encoding="utf-8"))
KW_OK = {(a, c) for a, l in CREATED["keywords_by_ad_group"].items() for c in l}
AD_OK = {(a, i) for a, l in CREATED["ads_by_ad_group"].items() for i in l}
PLAN = json.loads((PLN / "2026-09-02-plan-ga-launch-3a-payload.json").read_text(encoding="utf-8"))
log = {"plan_id": "PLAN-GA-LAUNCH-3A", "approved_fingerprint": FP, "gate": [], "aborted": False}


def g(n, ok, d=""):
    log["gate"].append({"check": n, "pass": bool(ok), "detail": str(d)[:300]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {n}  {str(d)[:130]}")
    return bool(ok)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    cl = load_google_ads_client()
    cid = normalize_customer_id(CID)
    ga = cl.get_service("GoogleAdsService")
    agsv, agc, ada = (cl.get_service("AdGroupService"),
                      cl.get_service("AdGroupCriterionService"),
                      cl.get_service("AdGroupAdService"))

    def q(s):
        return list(ga.search(customer_id=cid, query=s))

    print("=== PRE-EXECUTION GATE ===")
    c = q("""SELECT customer.id, customer.descriptive_name, customer.manager,
                    customer.test_account, customer.status, customer.currency_code,
                    customer.time_zone FROM customer LIMIT 1""")[0].customer
    if not g("1-4 identity", c.descriptive_name == "Softwind Power Washing - Live"
             and str(c.id) == CID and not c.manager and not c.test_account
             and enum_name(c.status) == "ENABLED" and c.currency_code == "USD"
             and c.time_zone == "America/New_York", f"{c.descriptive_name}/{c.id}"):
        return 2

    camps = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status,
                         campaign.bidding_strategy_type, campaign.campaign_budget,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.network_settings.target_partner_search_network,
                         campaign.network_settings.target_content_network,
                         campaign.ai_max_setting.enable_ai_max,
                         campaign.geo_target_type_setting.positive_geo_target_type
                  FROM campaign WHERE campaign.status != 'REMOVED'"""):
        k = r.campaign
        camps[str(k.id)] = {"name": k.name, "status": enum_name(k.status),
                            "bid": enum_name(k.bidding_strategy_type),
                            "ceiling": round(k.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
                            "budget_id": k.campaign_budget.split("/")[-1],
                            "sp": bool(k.network_settings.target_partner_search_network),
                            "disp": bool(k.network_settings.target_content_network),
                            "aimax": bool(k.ai_max_setting.enable_ai_max),
                            "geo": enum_name(k.geo_target_type_setting.positive_geo_target_type)}
    g("5-7 both campaigns ENABLED",
      camps[SURV]["status"] == "ENABLED" and camps[RETIRE]["status"] == "ENABLED")
    g("8 both TARGET_SPEND", all(v["bid"] == "TARGET_SPEND" for v in camps.values()))
    g("9 both ceilings $30.00", all(v["ceiling"] == 30.0 for v in camps.values()))

    ags = {str(r.ad_group.id): enum_name(r.ad_group.status)
           for r in q(f"""SELECT ad_group.id, ad_group.status FROM ad_group
                          WHERE ad_group.id IN ({','.join(G6)})""")}
    kws, ads = {}, {}
    for r in q(f"""SELECT ad_group.id, ad_group_criterion.criterion_id,
                          ad_group_criterion.keyword.text,
                          ad_group_criterion.keyword.match_type,
                          ad_group_criterion.status FROM ad_group_criterion
                   WHERE ad_group_criterion.type='KEYWORD'
                     AND ad_group_criterion.negative=FALSE
                     AND ad_group_criterion.status!='REMOVED'
                     AND ad_group.id IN ({','.join(G6)})"""):
        k = r.ad_group_criterion
        kws[str(k.criterion_id)] = {"ag": str(r.ad_group.id), "t": k.keyword.text,
                                    "m": enum_name(k.keyword.match_type),
                                    "s": enum_name(k.status)}
    for r in q(f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                          ad_group_ad.policy_summary.approval_status
                   FROM ad_group_ad WHERE ad_group_ad.status!='REMOVED'
                     AND ad_group.id IN ({','.join(G6)})"""):
        a = r.ad_group_ad
        ads[str(a.ad.id)] = {"ag": str(r.ad_group.id), "s": enum_name(a.status),
                             "p": enum_name(a.policy_summary.approval_status)}
    g("10 3B+3C guards still PAUSED",
      all(kws[k]["s"] == "PAUSED" for k in GUARD_KW if k in kws)
      and all(ads[a]["s"] == "PAUSED" for a in GUARD_ADS if a in ads))
    new_ads = [a for a in ads if (ads[a]["ag"], a) in AD_OK]
    g("11 all 12 new RSAs APPROVED",
      len(new_ads) == 12 and all(ads[a]["p"] == "APPROVED" for a in new_ads),
      f"{len(new_ads)} new, approvals={sorted({ads[a]['p'] for a in new_ads})}")
    g("12 the 2 House Washing guard keywords PAUSED",
      all(kws[k]["s"] == "PAUSED" for k in GUARD_KW))
    g("13 the 4 legacy RSAs from 3B/3C PAUSED",
      all(ads[a]["s"] == "PAUSED" for a in GUARD_ADS))
    tgt_kw = [k for k, v in kws.items() if (v["ag"], k) in KW_OK]
    g("14 the 28 target keywords PAUSED",
      len(tgt_kw) == 28 and all(kws[k]["s"] == "PAUSED" for k in tgt_kw), len(tgt_kw))
    g("15 the 12 target RSAs PAUSED", all(ads[a]["s"] == "PAUSED" for a in new_ads))
    g("16 five target ad groups PAUSED",
      sum(1 for x in G6 if ags[x] == "PAUSED") == 5)
    g("17 202870585390 already ENABLED", ags["202870585390"] == "ENABLED")

    plan_kw = {a["resource_id"] for a in PLAN["actions"] if a["type"] == "ad_group_criterion"}
    plan_ad = {a["resource_id"] for a in PLAN["actions"] if a["type"] == "ad_group_ad"}
    plan_ag = {a["resource_id"] for a in PLAN["actions"] if a["type"] == "ad_group"}
    g("18 no target resource ID changed",
      plan_kw == set(tgt_kw) and plan_ad == set(new_ads)
      and plan_ag == {x for x in G6 if ags[x] == "PAUSED"})
    fp = approval_code(PLAN)
    if not g("19-20 fingerprint == approved, payload byte-identical", fp == FP, fp):
        log["aborted"] = True
        write()
        return 2
    g("23 no guard keyword/legacy ad/foreign resource in the payload",
      not (plan_kw & GUARD_KW) and not (plan_ad & GUARD_ADS)
      and all(kws[k]["ag"] in G6 for k in plan_kw))

    ag_ops = []
    for x in sorted(plan_ag):
        o = cl.get_type("AdGroupOperation")
        o.update.resource_name = agsv.ad_group_path(cid, x)
        o.update.status = cl.enums.AdGroupStatusEnum.ENABLED
        o.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ag_ops.append(o)
    kw_ops = []
    for x in sorted(plan_kw):
        o = cl.get_type("AdGroupCriterionOperation")
        o.update.resource_name = agc.ad_group_criterion_path(cid, kws[x]["ag"], x)
        o.update.status = cl.enums.AdGroupCriterionStatusEnum.ENABLED
        o.update_mask.CopyFrom(FieldMask(paths=["status"]))
        kw_ops.append(o)
    ad_ops = []
    for x in sorted(plan_ad):
        o = cl.get_type("AdGroupAdOperation")
        o.update.resource_name = ada.ad_group_ad_path(cid, ads[x]["ag"], x)
        o.update.status = cl.enums.AdGroupAdStatusEnum.ENABLED
        o.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ad_ops.append(o)

    print("\n=== 21-22 VALIDATE_ONLY ===")
    batches = [("ad_groups", agsv, "MutateAdGroupsRequest", ag_ops, "mutate_ad_groups"),
               ("keywords", agc, "MutateAdGroupCriteriaRequest", kw_ops,
                "mutate_ad_group_criteria"),
               ("ads", ada, "MutateAdGroupAdsRequest", ad_ops, "mutate_ad_group_ads")]
    for lab, svc, rt, o, m in batches:
        rq = cl.get_type(rt)
        rq.customer_id = cid
        rq.operations.extend(o)
        rq.validate_only = True
        rq.partial_failure = False
        try:
            getattr(svc, m)(request=rq)
            g(f"validate_only {lab}", True, f"{len(o)} ops, 0 applied")
        except Exception as e:
            g(f"validate_only {lab}", False, str(e)[:300])
            log["aborted"] = True
            write()
            return 2
    if not all(x["pass"] for x in log["gate"]):
        print("\nGATE FAILED - NOT EXECUTING")
        log["aborted"] = True
        write()
        return 2

    print("\n=== EXECUTE (atomic per batch) ===")
    done = {}
    for lab, svc, rt, o, m in batches:
        rq = cl.get_type(rt)
        rq.customer_id = cid
        rq.operations.extend(o)
        rq.validate_only = False
        rq.partial_failure = False
        try:
            resp = getattr(svc, m)(request=rq)
            done[lab] = [r.resource_name for r in resp.results]
            print(f"  [PASS] {lab}: {len(resp.results)} enabled")
        except Exception as e:
            print(f"  [FAIL] {lab}: {str(e)[:300]}")
            log["aborted"] = True
            log["partial_state"] = done
            log["abort_reason"] = (f"{lab} batch failed. Batches already applied: "
                                   f"{list(done)}. DO NOT rerun blindly.")
            write()
            return 2
    log["enabled"] = done
    log["completed"] = datetime.now(ZoneInfo("America/New_York")).isoformat()
    write()
    print("\nEXECUTION COMPLETE")
    return 0


def write():
    now = datetime.now(ZoneInfo("America/New_York"))
    p = SNAP / f"launch3a-execution-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(log, indent=2, default=str), encoding="utf-8")
    print("WROTE", p)


if __name__ == "__main__":
    raise SystemExit(main())
