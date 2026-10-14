#!/usr/bin/env python3
"""EXECUTE PLAN-GA-LAUNCH-3C (fingerprint 40F940130E6D), then re-fingerprint 3A.

3C pauses 2 legacy Power Washing RSAs. Then a fresh read regenerates PLAN-GA-LAUNCH-3A's
fingerprint with validate_only. 3A is NOT executed.
"""
from __future__ import annotations

import hashlib
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

CID, SURVIVOR = "1521725229", "24103511039"
FP3C = "40F940130E6D"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
PLN = ROOT / "clients/softwind-power-washing/plans"
GUARD = [("202870585390", "819975939342"), ("202870585390", "819975939345")]
G6 = ["202870585390", "202870585870", "202870585910",
      "202870586310", "202870586110", "202870586150"]
NAME6 = {"202870585390": "Power Washing", "202870585870": "Pressure Washing",
         "202870585910": "House Washing", "202870586310": "Soft Washing",
         "202870586110": "Driveway Pressure Washing",
         "202870586150": "Patio Pressure Washing"}
NEW_ADS = {"823152917197", "823152917200", "823152917203", "823152917206",
           "823152917209", "823152917212", "823152917215", "823152917218",
           "823152917221", "823152917224", "823152917227", "823152917230"}
log = {"plan_id": "PLAN-GA-LAUNCH-3C", "approved_fingerprint": FP3C, "steps": []}


def step(n, ok, d=""):
    log["steps"].append({"step": n, "pass": bool(ok), "detail": str(d)[:350]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {n}  {str(d)[:150]}")
    return bool(ok)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    cid = normalize_customer_id(CID)
    ga = client.get_service("GoogleAdsService")
    ada = client.get_service("AdGroupAdService")
    ags_svc = client.get_service("AdGroupService")
    agc = client.get_service("AdGroupCriterionService")

    def q(s):
        return list(ga.search(customer_id=cid, query=s))

    print("=== 1. IDENTITY ===")
    c = q("""SELECT customer.id, customer.descriptive_name, customer.manager,
                    customer.test_account, customer.status, customer.currency_code,
                    customer.time_zone FROM customer LIMIT 1""")[0].customer
    if not step("identity", c.descriptive_name == "Softwind Power Washing - Live"
                and str(c.id) == CID and not c.manager and not c.test_account
                and enum_name(c.status) == "ENABLED" and c.currency_code == "USD"
                and c.time_zone == "America/New_York",
                f"{c.descriptive_name} / {c.id}"):
        return 2

    print("\n=== 2. RE-READ 3C TARGETS ===")
    live = {}
    for r in q(f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status
                   FROM ad_group_ad
                   WHERE ad_group_ad.ad.id IN ({','.join(g[1] for g in GUARD)})"""):
        live[str(r.ad_group_ad.ad.id)] = (str(r.ad_group.id),
                                          enum_name(r.ad_group_ad.status))
    for ag, adid in GUARD:
        v = live.get(adid)
        if not step(f"ad {adid} ENABLED in {ag}",
                    v and v[0] == ag and v[1] == "ENABLED", json.dumps(v)):
            return 2

    print("\n=== 3. RECOMPUTE 3C FINGERPRINT ===")
    canon3c = {
        "plan_id": "PLAN-GA-LAUNCH-3C",
        "target": {"exact_child_account_name": "Softwind Power Washing - Live",
                   "child_customer_id": CID, "exact_service": "Power Washing",
                   "manager_customer_id": "3373711342", "campaign_id": SURVIVOR},
        "actions": sorted([{"type": "ad_group_ad", "ad_group_id": a, "resource_id": i,
                            "current": "ENABLED", "proposed": "PAUSED",
                            "field_mask": "status"} for a, i in GUARD],
                          key=lambda x: x["resource_id"]),
        "mutation_count": 2}
    fp = approval_code(canon3c)
    if not step("fingerprint == approved", fp == FP3C, fp):
        return 2
    saved = json.loads((PLN / "2026-09-02-plan-ga-launch-3c-payload.json")
                       .read_text(encoding="utf-8"))
    step("payload identical to fingerprinted file", saved == canon3c)

    ops = []
    for ag, adid in GUARD:
        op = client.get_type("AdGroupAdOperation")
        op.update.resource_name = ada.ad_group_ad_path(cid, ag, adid)
        op.update.status = client.enums.AdGroupAdStatusEnum.PAUSED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ops.append(op)

    print("\n=== 4. VALIDATE_ONLY ===")
    req = client.get_type("MutateAdGroupAdsRequest")
    req.customer_id = cid
    req.operations.extend(ops)
    req.validate_only = True
    req.partial_failure = False
    try:
        ada.mutate_ad_group_ads(request=req)
        step("validate_only", True, "2 ops, 0 applied")
    except Exception as exc:
        step("validate_only", False, str(exc)[:300])
        return 2

    print("\n=== 5. EXECUTE 3C (atomic) ===")
    req.validate_only = False
    try:
        resp = ada.mutate_ad_group_ads(request=req)
        log["paused"] = [r.resource_name for r in resp.results]
        step("pause mutate", len(resp.results) == 2, f"{len(resp.results)} paused")
    except Exception as exc:
        step("pause mutate", False, str(exc)[:400])
        log["aborted"] = True
        write()
        return 2

    print("\n=== 6. 3C READBACK ===")
    after = {}
    for r in q(f"""SELECT ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad
                   WHERE ad_group_ad.ad.id IN ({','.join(g[1] for g in GUARD)})"""):
        after[str(r.ad_group_ad.ad.id)] = enum_name(r.ad_group_ad.status)
    step("both legacy Power Washing RSAs now PAUSED",
         all(v == "PAUSED" for v in after.values()), json.dumps(after))
    en_ad = len(q("SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group_ad.status='ENABLED'"))
    en_ag = len(q("SELECT ad_group.id FROM ad_group WHERE ad_group.status='ENABLED'"))
    step("ENABLED ads 42 -> 40", en_ad == 40, en_ad)
    step("ENABLED ad groups still 12", en_ag == 12, en_ag)
    camps = {str(r.campaign.id): (r.campaign.name, enum_name(r.campaign.status),
                                  round(r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6, 2))
             for r in q("""SELECT campaign.id, campaign.name, campaign.status,
                                  campaign.target_spend.cpc_bid_ceiling_micros
                           FROM campaign WHERE campaign.status != 'REMOVED'""")}
    step("both campaigns ENABLED at $30.00",
         all(v[1] == "ENABLED" and v[2] == 30.0 for v in camps.values()), json.dumps(camps))
    log["after_3c"] = {"enabled_ads": en_ad, "enabled_ad_groups": en_ag, "campaigns": camps}

    # ---------------- 7. RE-FINGERPRINT 3A ----------------
    print("\n=== 7. FRESH READ + RE-FINGERPRINT PLAN-GA-LAUNCH-3A ===")
    ags = {str(r.ad_group.id): (r.ad_group.name, enum_name(r.ad_group.status))
           for r in q(f"""SELECT ad_group.id, ad_group.name, ad_group.status
                          FROM ad_group WHERE ad_group.id IN ({','.join(G6)})""")}
    kw_en = []
    for r in q(f"""SELECT ad_group.id, ad_group_criterion.criterion_id,
                          ad_group_criterion.keyword.text,
                          ad_group_criterion.keyword.match_type,
                          ad_group_criterion.status
                   FROM ad_group_criterion
                   WHERE ad_group_criterion.type='KEYWORD'
                     AND ad_group_criterion.negative=FALSE
                     AND ad_group_criterion.status='PAUSED'
                     AND ad_group.id IN ({','.join(G6)})"""):
        k = r.ad_group_criterion
        kw_en.append({"ad_group_id": str(r.ad_group.id), "criterion_id": str(k.criterion_id),
                      "text": k.keyword.text, "match": enum_name(k.keyword.match_type)})
    ad_en, pol_bad = [], []
    proj = defaultdict(int)
    for r in q(f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                          ad_group_ad.policy_summary.approval_status
                   FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'
                     AND ad_group.id IN ({','.join(G6)})"""):
        a = r.ad_group_ad
        adid = str(a.ad.id)
        if enum_name(a.status) == "ENABLED":
            proj[str(r.ad_group.id)] += 1
        if adid in NEW_ADS and enum_name(a.status) == "PAUSED":
            ad_en.append({"ad_group_id": str(r.ad_group.id), "ad_id": adid})
            proj[str(r.ad_group.id)] += 1
            if enum_name(a.policy_summary.approval_status) != "APPROVED":
                pol_bad.append(adid)
    ag_en = [g for g in G6 if ags[g][1] == "PAUSED"]
    over = {g: n for g, n in proj.items() if n > 3}
    step("3A: no ad group would exceed 3 enabled RSAs", not over, json.dumps(dict(proj)))
    step("3A: all new RSAs APPROVED", not pol_bad, pol_bad or "12/12 approved")
    step("3A: 28 paused final keywords found", len(kw_en) == 28, len(kw_en))
    step("3A: 12 paused new RSAs found", len(ad_en) == 12, len(ad_en))
    step("3A: 5 paused ad groups found", len(ag_en) == 5, len(ag_en))

    ag_ops = []
    for g in ag_en:
        op = client.get_type("AdGroupOperation")
        op.update.resource_name = ags_svc.ad_group_path(cid, g)
        op.update.status = client.enums.AdGroupStatusEnum.ENABLED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ag_ops.append(op)
    kw_ops = []
    for x in kw_en:
        op = client.get_type("AdGroupCriterionOperation")
        op.update.resource_name = agc.ad_group_criterion_path(
            cid, x["ad_group_id"], x["criterion_id"])
        op.update.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        kw_ops.append(op)
    ad_ops = []
    for x in ad_en:
        op = client.get_type("AdGroupAdOperation")
        op.update.resource_name = ada.ad_group_ad_path(cid, x["ad_group_id"], x["ad_id"])
        op.update.status = client.enums.AdGroupAdStatusEnum.ENABLED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ad_ops.append(op)

    vo = {}
    for label, svc, reqt, o, meth in (
            ("ad_groups", ags_svc, "MutateAdGroupsRequest", ag_ops, "mutate_ad_groups"),
            ("keywords", agc, "MutateAdGroupCriteriaRequest", kw_ops,
             "mutate_ad_group_criteria"),
            ("ads", ada, "MutateAdGroupAdsRequest", ad_ops, "mutate_ad_group_ads")):
        rq = client.get_type(reqt)
        rq.customer_id = cid
        rq.operations.extend(o)
        rq.validate_only = True
        rq.partial_failure = False
        try:
            getattr(svc, meth)(request=rq)
            vo[label] = f"PASS - {len(o)} enable operations validated, 0 applied"
        except Exception as exc:
            f = getattr(exc, "failure", None)
            vo[label] = "FAIL - " + str([(str(e.error_code).strip(), e.message)
                                         for e in f.errors] if f else str(exc)[:200])
    print("  validate_only 3A:", json.dumps(vo, indent=2))
    ok3a = all(v.startswith("PASS") for v in vo.values())

    canon3a = {
        "plan_id": "PLAN-GA-LAUNCH-3A",
        "target": {"exact_child_account_name": "Softwind Power Washing - Live",
                   "child_customer_id": CID, "exact_service": "Power Washing",
                   "manager_customer_id": "3373711342", "campaign_id": SURVIVOR},
        "actions": sorted(
            [{"type": "ad_group", "resource_id": g, "final_group": NAME6[g],
              "current": "PAUSED", "proposed": "ENABLED", "field_mask": "status"}
             for g in ag_en]
            + [{"type": "ad_group_criterion", "ad_group_id": x["ad_group_id"],
                "resource_id": x["criterion_id"], "keyword_text": x["text"],
                "match_type": x["match"], "current": "PAUSED", "proposed": "ENABLED",
                "field_mask": "status"} for x in kw_en]
            + [{"type": "ad_group_ad", "ad_group_id": x["ad_group_id"],
                "resource_id": x["ad_id"], "current": "PAUSED", "proposed": "ENABLED",
                "field_mask": "status"} for x in ad_en],
            key=lambda x: (x["type"], x["resource_id"])),
        "mutation_count": len(ag_ops) + len(kw_ops) + len(ad_ops)}
    a1 = approval_code(canon3a)
    a2 = approval_code(json.loads(json.dumps(canon3a)))
    a3 = approval_code(canon3a)
    now = datetime.now(ZoneInfo("America/New_York"))
    log["plan_3a"] = {
        "counts": {"ad_groups": len(ag_ops), "keywords": len(kw_ops), "ads": len(ad_ops),
                   "action_count": canon3a["mutation_count"],
                   "object_count": canon3a["mutation_count"],
                   "mutation_count": canon3a["mutation_count"]},
        "validate_only": vo, "all_validate_pass": ok3a,
        "fingerprint": a1, "recompute_1": a2, "recompute_2": a3,
        "canonical_sha256_full": hashlib.sha256(
            json.dumps(canon3a, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")).hexdigest(),
        "approval_command": f"APPROVE PLAN-GA-LAUNCH-3A {a1} FOR {CID}",
        "projected_enabled_rsas_per_ad_group": dict(proj)}
    (PLN / "2026-09-02-plan-ga-launch-3a-payload.json").write_text(
        json.dumps(canon3a, indent=2), encoding="utf-8")
    log["completed"] = now.isoformat()
    log["all_pass"] = all(s["pass"] for s in log["steps"]) and ok3a
    write()
    print("\n=== PLAN-GA-LAUNCH-3A ===")
    print(json.dumps(log["plan_3a"], indent=2))
    return 0 if log["all_pass"] else 1


def write():
    now = datetime.now(ZoneInfo("America/New_York"))
    p = SNAP / f"launch3c-execution-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(log, indent=2, default=str), encoding="utf-8")
    print("\nWROTE", p)


if __name__ == "__main__":
    raise SystemExit(main())
