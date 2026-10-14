#!/usr/bin/env python3
"""EXECUTE PLAN-GA-LAUNCH-3B after approval. Fingerprint B9EDA34DA712.

Pauses 4 legacy resources that would otherwise activate on parent enable.
Status-only field mask. Atomic per batch. Creates nothing, enables nothing.
"""
from __future__ import annotations

import json
import sys
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
EXPECTED_FP = "B9EDA34DA712"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
PLN = ROOT / "clients/softwind-power-washing/plans"

GUARD_KW = [("202870585910", "384030528226", "house washing company near me", "PHRASE"),
            ("202870585910", "502487923397", "house washing company near me", "EXACT")]
GUARD_ADS = [("202870586310", "819975939528"), ("202870586310", "819975939531")]

log = {"plan_id": "PLAN-GA-LAUNCH-3B", "approved_fingerprint": EXPECTED_FP,
       "approved_by": "Walter Correa", "steps": [], "aborted": False}


def step(name, ok, detail=""):
    log["steps"].append({"step": name, "pass": bool(ok), "detail": str(detail)[:400]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {str(detail)[:160]}")
    return bool(ok)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    cid = normalize_customer_id(CID)
    ga = client.get_service("GoogleAdsService")
    agc = client.get_service("AdGroupCriterionService")
    ada = client.get_service("AdGroupAdService")
    now0 = datetime.now(ZoneInfo("America/New_York"))
    log["started_account_local"] = now0.isoformat()

    def q(s):
        return list(ga.search(customer_id=cid, query=s))

    print("=== 1. IDENTITY GATE ===")
    c = q("""SELECT customer.id, customer.descriptive_name, customer.manager,
                    customer.test_account, customer.status, customer.currency_code,
                    customer.time_zone FROM customer LIMIT 1""")[0].customer
    ok = (c.descriptive_name == "Softwind Power Washing - Live" and str(c.id) == CID
          and not c.manager and not c.test_account and enum_name(c.status) == "ENABLED"
          and c.currency_code == "USD" and c.time_zone == "America/New_York")
    if not step("identity", ok, f"{c.descriptive_name} / {c.id}"):
        log["aborted"] = True
        return 2

    print("\n=== 2. RE-READ THE 4 TARGET RESOURCES ===")
    kw_live = {}
    for r in q(f"""SELECT ad_group.id, ad_group_criterion.criterion_id,
                          ad_group_criterion.keyword.text,
                          ad_group_criterion.keyword.match_type,
                          ad_group_criterion.status
                   FROM ad_group_criterion
                   WHERE ad_group_criterion.criterion_id IN
                         ({','.join(g[1] for g in GUARD_KW)})
                     AND ad_group.id = 202870585910"""):
        k = r.ad_group_criterion
        kw_live[str(k.criterion_id)] = {"text": k.keyword.text,
                                        "match": enum_name(k.keyword.match_type),
                                        "status": enum_name(k.status)}
    ad_live = {}
    for r in q(f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status
                   FROM ad_group_ad
                   WHERE ad_group_ad.ad.id IN ({','.join(g[1] for g in GUARD_ADS)})"""):
        ad_live[str(r.ad_group_ad.ad.id)] = {"ad_group": str(r.ad_group.id),
                                             "status": enum_name(r.ad_group_ad.status)}
    for _, crit, text, mt in GUARD_KW:
        v = kw_live.get(crit)
        if not step(f"keyword {crit} present, ENABLED, text/match match",
                    v and v["status"] == "ENABLED" and v["text"] == text
                    and v["match"] == mt, json.dumps(v)):
            log["aborted"] = True
            log["abort_reason"] = f"target keyword {crit} drifted"
            write()
            return 2
    for agid, adid in GUARD_ADS:
        v = ad_live.get(adid)
        if not step(f"ad {adid} present, ENABLED, in {agid}",
                    v and v["status"] == "ENABLED" and v["ad_group"] == agid,
                    json.dumps(v)):
            log["aborted"] = True
            log["abort_reason"] = f"target ad {adid} drifted"
            write()
            return 2
    log["before"] = {"keywords": kw_live, "ads": ad_live}

    print("\n=== 3. RECOMPUTE FINGERPRINT ===")
    canonical = {
        "plan_id": "PLAN-GA-LAUNCH-3B",
        "target": {"exact_child_account_name": "Softwind Power Washing - Live",
                   "child_customer_id": CID, "exact_service": "Power Washing",
                   "manager_customer_id": "3373711342", "campaign_id": SURVIVOR},
        "actions": sorted(
            [{"type": "ad_group_criterion", "ad_group_id": a, "resource_id": c,
              "keyword_text": t, "match_type": m, "current": "ENABLED",
              "proposed": "PAUSED", "field_mask": "status"} for a, c, t, m in GUARD_KW]
            + [{"type": "ad_group_ad", "ad_group_id": a, "resource_id": i,
                "current": "ENABLED", "proposed": "PAUSED", "field_mask": "status"}
               for a, i in GUARD_ADS],
            key=lambda x: (x["type"], x["resource_id"])),
        "mutation_count": 4,
    }
    fp = approval_code(canonical)
    saved = json.loads((PLN / "2026-09-02-plan-ga-launch-3b-payload.json")
                       .read_text(encoding="utf-8"))
    if not step("fingerprint == approved", fp == EXPECTED_FP, fp):
        log["aborted"] = True
        log["abort_reason"] = f"fingerprint mismatch {fp}"
        write()
        return 2
    step("payload identical to the fingerprinted file", saved == canonical)

    print("\n=== 4. BUILD OPERATIONS ===")
    kw_ops = []
    for agid, crit, _, _ in GUARD_KW:
        op = client.get_type("AdGroupCriterionOperation")
        op.update.resource_name = agc.ad_group_criterion_path(cid, agid, crit)
        op.update.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        kw_ops.append(op)
    ad_ops = []
    for agid, adid in GUARD_ADS:
        op = client.get_type("AdGroupAdOperation")
        op.update.resource_name = ada.ad_group_ad_path(cid, agid, adid)
        op.update.status = client.enums.AdGroupAdStatusEnum.PAUSED
        op.update_mask.CopyFrom(FieldMask(paths=["status"]))
        ad_ops.append(op)
    step("operations built", len(kw_ops) == 2 and len(ad_ops) == 2,
         f"{len(kw_ops)} keyword + {len(ad_ops)} ad pauses")

    print("\n=== 5. VALIDATE_ONLY ===")
    for label, svc, reqt, ops, meth in (
            ("keywords", agc, "MutateAdGroupCriteriaRequest", kw_ops,
             "mutate_ad_group_criteria"),
            ("ads", ada, "MutateAdGroupAdsRequest", ad_ops, "mutate_ad_group_ads")):
        req = client.get_type(reqt)
        req.customer_id = cid
        req.operations.extend(ops)
        req.validate_only = True
        req.partial_failure = False
        try:
            getattr(svc, meth)(request=req)
            step(f"validate_only {label}", True, f"{len(ops)} ops, 0 applied")
        except Exception as exc:
            step(f"validate_only {label}", False, str(exc)[:400])
            log["aborted"] = True
            write()
            return 2

    print("\n=== 6. EXECUTE - KEYWORD PAUSES (atomic) ===")
    req = client.get_type("MutateAdGroupCriteriaRequest")
    req.customer_id = cid
    req.operations.extend(kw_ops)
    req.validate_only = False
    req.partial_failure = False
    try:
        resp = agc.mutate_ad_group_criteria(request=req)
        log["paused_keywords"] = [r.resource_name for r in resp.results]
        step("keyword pause mutate", len(resp.results) == 2, f"{len(resp.results)} paused")
    except Exception as exc:
        step("keyword pause mutate", False, str(exc)[:500])
        log["aborted"] = True
        log["abort_reason"] = "keyword pause failed - atomic batch, nothing changed"
        write()
        return 2

    print("\n=== 7. EXECUTE - AD PAUSES (atomic) ===")
    req2 = client.get_type("MutateAdGroupAdsRequest")
    req2.customer_id = cid
    req2.operations.extend(ad_ops)
    req2.validate_only = False
    req2.partial_failure = False
    try:
        resp2 = ada.mutate_ad_group_ads(request=req2)
        log["paused_ads"] = [r.resource_name for r in resp2.results]
        step("ad pause mutate", len(resp2.results) == 2, f"{len(resp2.results)} paused")
    except Exception as exc:
        step("ad pause mutate", False, str(exc)[:500])
        log["aborted"] = True
        log["abort_reason"] = ("PARTIAL STATE: 2 keywords paused, 0 ads paused. "
                               "Do not rerun blindly - recovery is to pause only the 2 ads.")
        write()
        return 2

    print("\n=== 8. READBACK QA ===")
    checks = []

    def ck(n, ok, d=""):
        checks.append({"check": n, "pass": bool(ok), "detail": str(d)[:250]})
        print(f"  [{'PASS' if ok else 'FAIL'}] {n}  {str(d)[:130]}")

    after_kw = {}
    for r in q(f"""SELECT ad_group_criterion.criterion_id, ad_group_criterion.status,
                          ad_group_criterion.keyword.text
                   FROM ad_group_criterion
                   WHERE ad_group_criterion.criterion_id IN
                         ({','.join(g[1] for g in GUARD_KW)})
                     AND ad_group.id = 202870585910"""):
        after_kw[str(r.ad_group_criterion.criterion_id)] = enum_name(
            r.ad_group_criterion.status)
    after_ad = {}
    for r in q(f"""SELECT ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad
                   WHERE ad_group_ad.ad.id IN ({','.join(g[1] for g in GUARD_ADS)})"""):
        after_ad[str(r.ad_group_ad.ad.id)] = enum_name(r.ad_group_ad.status)
    ck("both guard keywords now PAUSED",
       all(v == "PAUSED" for v in after_kw.values()), json.dumps(after_kw))
    ck("both guard ads now PAUSED",
       all(v == "PAUSED" for v in after_ad.values()), json.dumps(after_ad))
    en_ag = len(q("SELECT ad_group.id FROM ad_group WHERE ad_group.status='ENABLED'"))
    en_kw = len(q("""SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
                     WHERE ad_group_criterion.type='KEYWORD'
                       AND ad_group_criterion.negative=FALSE
                       AND ad_group_criterion.status='ENABLED'"""))
    en_ad = len(q("SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group_ad.status='ENABLED'"))
    ck("ENABLED ad groups still 12 (nothing enabled or disabled)", en_ag == 12, en_ag)
    ck("ENABLED keywords 214 -> 212 (only the 2 guard keywords paused)", en_kw == 212, en_kw)
    ck("ENABLED ads 44 -> 42 (only the 2 guard ads paused)", en_ad == 42, en_ad)
    ck("the 28 new keywords still PAUSED",
       len(q("""SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
                WHERE ad_group_criterion.type='KEYWORD'
                  AND ad_group_criterion.negative=FALSE
                  AND ad_group_criterion.status='PAUSED'""")) == 30, "28 new + 2 guard = 30")
    camps = {}
    for r in q("""SELECT campaign.id, campaign.name, campaign.status,
                         campaign.target_spend.cpc_bid_ceiling_micros,
                         campaign.bidding_strategy_type
                  FROM campaign WHERE campaign.status != 'REMOVED'"""):
        camps[str(r.campaign.id)] = {
            "name": r.campaign.name, "status": enum_name(r.campaign.status),
            "ceiling": round(r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
            "bidding": enum_name(r.campaign.bidding_strategy_type)}
    ck("both campaigns still ENABLED, $30.00, TARGET_SPEND",
       all(v["status"] == "ENABLED" and v["ceiling"] == 30.0
           and v["bidding"] == "TARGET_SPEND" for v in camps.values()),
       json.dumps(camps))
    ck("campaign 24145053510 untouched", camps["24145053510"]["status"] == "ENABLED")

    # GATE-2 re-check
    pol = {}
    for r in q("""SELECT ad_group_ad.ad.id, ad_group_ad.policy_summary.approval_status,
                         ad_group_ad.policy_summary.review_status
                  FROM ad_group_ad WHERE ad_group_ad.status='PAUSED'
                    AND ad_group.id IN (202870585390,202870585870,202870585910,
                                        202870586310,202870586110,202870586150)"""):
        a = r.ad_group_ad
        pol[str(a.ad.id)] = (enum_name(a.policy_summary.approval_status),
                             enum_name(a.policy_summary.review_status))
    new_ids = {"823152917197", "823152917200", "823152917203", "823152917206",
               "823152917209", "823152917212", "823152917215", "823152917218",
               "823152917221", "823152917224", "823152917227", "823152917230"}
    newpol = {k: v for k, v in pol.items() if k in new_ids}
    log["gate2_rsa_policy"] = newpol
    approved = sum(1 for v in newpol.values() if v[0] == "APPROVED")
    disapproved = sum(1 for v in newpol.values() if v[0] == "DISAPPROVED")
    print(f"\n  GATE-2 re-check: {approved}/12 APPROVED, {disapproved} DISAPPROVED")
    for k, v in sorted(newpol.items()):
        print(f"    {k}  approval={v[0]:16} review={v[1]}")

    log["checks"] = checks
    log["all_pass"] = all(c["pass"] for c in checks)
    log["after"] = {"enabled_ad_groups": en_ag, "enabled_keywords": en_kw,
                    "enabled_ads": en_ad, "campaigns": camps}
    log["completed_account_local"] = datetime.now(ZoneInfo("America/New_York")).isoformat()
    write()
    print(f"\n  {len(checks)} checks, {sum(1 for c in checks if not c['pass'])} failed, "
          f"ALL PASS = {log['all_pass']}")
    return 0 if log["all_pass"] else 1


def write():
    now = datetime.now(ZoneInfo("America/New_York"))
    p = SNAP / f"launch3b-execution-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(log, indent=2, default=str), encoding="utf-8")
    print("\nWROTE", p)


if __name__ == "__main__":
    raise SystemExit(main())
