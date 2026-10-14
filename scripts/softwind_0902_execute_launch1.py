#!/usr/bin/env python3
"""EXECUTE PLAN-GA-LAUNCH-1 after approval. Fingerprint 92FFF603CAFD.

Creates 28 keywords + 12 RSAs, ALL PAUSED, in campaign 24103511039.
Atomic per batch (partial_failure=False). Stops on any failure.
Creation only - NOTHING is enabled, paused, or modified.
"""
from __future__ import annotations

import glob
import importlib.util
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

CID = "1521725229"
SURVIVOR = "24103511039"
RETIRING = "24145053510"
EXPECTED_FP = "92FFF603CAFD"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
PLN = ROOT / "clients/softwind-power-washing/plans"

spec = importlib.util.spec_from_file_location(
    "rec", ROOT / "scripts/softwind_0901_build_recovery_program.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
GROUPS, RSA = rec.GROUPS, rec.RSA

delta = json.loads(Path(sorted(glob.glob(str(SNAP / "launch1-delta-*.json")))[-1])
                   .read_text(encoding="utf-8"))["delta"]
KW_NEW = delta["keywords_to_create"]

log: dict = {"plan_id": "PLAN-GA-LAUNCH-1", "approved_fingerprint": EXPECTED_FP,
             "approved_by": "Walter Correa", "steps": [], "created": {},
             "aborted": False, "abort_reason": None}


def step(name, ok, detail=""):
    log["steps"].append({"step": name, "pass": bool(ok), "detail": str(detail)[:400]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {str(detail)[:150]}")
    return bool(ok)


def abort(reason):
    log["aborted"] = True
    log["abort_reason"] = reason
    print("\n*** ABORTED:", reason)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    cid = normalize_customer_id(CID)
    ga = client.get_service("GoogleAdsService")
    ag_svc = client.get_service("AdGroupService")
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
    if not step("identity", ok, f"{c.descriptive_name} / {c.id} / {enum_name(c.status)}"):
        abort("identity mismatch")
        return 2

    print("\n=== 2. RE-READ TARGET RESOURCES ===")
    ags = {str(r.ad_group.id): (r.ad_group.name, enum_name(r.ad_group.status),
                                str(r.campaign.id))
           for r in q("""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status
                         FROM ad_group WHERE ad_group.status != 'REMOVED'""")}
    for g, cfg in GROUPS.items():
        a = ags.get(cfg["ad_group_id"])
        if not a or a[2] != SURVIVOR:
            step(f"ad group {cfg['ad_group_id']} ({g})", False, str(a))
            abort(f"target ad group {cfg['ad_group_id']} missing or wrong campaign")
            return 2
    step("all 6 target ad groups exist in campaign " + SURVIVOR, True)

    existing = set()
    for r in q("""SELECT ad_group.id, ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type
                  FROM ad_group_criterion
                  WHERE ad_group_criterion.type='KEYWORD'
                    AND ad_group_criterion.negative=FALSE
                    AND ad_group_criterion.status != 'REMOVED'"""):
        existing.add((str(r.ad_group.id), r.ad_group_criterion.keyword.text,
                      enum_name(r.ad_group_criterion.keyword.match_type)))
    dupes = [r for r in KW_NEW
             if (r["ad_group_id"], r["text"], r["match_type"]) in existing]
    if not step("no planned keyword already exists (duplicate guard)", not dupes,
                f"{len(dupes)} collisions" if dupes else "0 collisions"):
        abort("duplicate keyword detected - plan would create a duplicate")
        return 2

    before = {
        "positive_keywords": len(q("""SELECT ad_group_criterion.criterion_id
                                      FROM ad_group_criterion
                                      WHERE ad_group_criterion.type='KEYWORD'
                                        AND ad_group_criterion.negative=FALSE
                                        AND ad_group_criterion.status != 'REMOVED'""")),
        "ads": len(q("""SELECT ad_group_ad.ad.id FROM ad_group_ad
                        WHERE ad_group_ad.status != 'REMOVED'""")),
        "ad_groups": len(ags),
        "ad_group_negatives": len(q("""SELECT ad_group_criterion.criterion_id
                                       FROM ad_group_criterion
                                       WHERE ad_group_criterion.negative=TRUE
                                         AND ad_group_criterion.type='KEYWORD'
                                         AND ad_group_criterion.status != 'REMOVED'""")),
    }
    camps_before = {str(r.campaign.id): (r.campaign.name, enum_name(r.campaign.status),
                                         r.campaign.target_spend.cpc_bid_ceiling_micros)
                    for r in q("""SELECT campaign.id, campaign.name, campaign.status,
                                         campaign.target_spend.cpc_bid_ceiling_micros
                                  FROM campaign WHERE campaign.status != 'REMOVED'""")}
    log["before"] = {"counts": before, "campaigns": camps_before}
    print("  before:", json.dumps(before))

    print("\n=== 3. RECOMPUTE FINGERPRINT ===")
    canonical = {
        "plan_id": "PLAN-GA-LAUNCH-1",
        "target": {"exact_child_account_name": "Softwind Power Washing - Live",
                   "child_customer_id": CID, "exact_service": "Power Washing",
                   "manager_customer_id": "3373711342", "campaign_id": SURVIVOR},
        "ad_groups_created": 0,
        "keywords": sorted([{"ad_group_id": r["ad_group_id"], "text": r["text"],
                             "match_type": r["match_type"], "status": "PAUSED"}
                            for r in KW_NEW],
                           key=lambda x: (x["ad_group_id"], x["text"], x["match_type"])),
        "rsas": sorted(
            [{"ad_group_id": GROUPS[g]["ad_group_id"], "rsa": "RSA %d" % ad["n"],
              "final_url": GROUPS[g]["page"], "path1": GROUPS[g]["p1"],
              "path2": GROUPS[g]["p2"], "status": "PAUSED",
              "headlines": ad["h"], "descriptions": ad["d"]}
             for g in GROUPS for ad in RSA[g]],
            key=lambda x: (x["ad_group_id"], x["rsa"])),
        "mutation_count": 40,
    }
    fp = approval_code(canonical)
    saved = json.loads((PLN / "2026-09-02-plan-ga-launch-1-payload.json")
                       .read_text(encoding="utf-8"))
    if not step("fingerprint == approved", fp == EXPECTED_FP, fp):
        abort(f"fingerprint mismatch: {fp} != {EXPECTED_FP}")
        return 2
    if not step("payload identical to the fingerprinted file", saved == canonical):
        abort("payload drift")
        return 2

    print("\n=== 4. BUILD OPERATIONS ===")
    kw_ops = []
    for r in KW_NEW:
        op = client.get_type("AdGroupCriterionOperation")
        cr = op.create
        cr.ad_group = ag_svc.ad_group_path(cid, r["ad_group_id"])
        cr.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
        cr.keyword.text = r["text"]
        cr.keyword.match_type = getattr(client.enums.KeywordMatchTypeEnum, r["match_type"])
        kw_ops.append(op)
    ad_ops, ad_index = [], []
    for g, cfg in GROUPS.items():
        for ad in RSA[g]:
            op = client.get_type("AdGroupAdOperation")
            a = op.create
            a.ad_group = ag_svc.ad_group_path(cid, cfg["ad_group_id"])
            a.status = client.enums.AdGroupAdStatusEnum.PAUSED
            a.ad.final_urls.append(cfg["page"])
            r_ = a.ad.responsive_search_ad
            r_.path1, r_.path2 = cfg["p1"], cfg["p2"]
            for h in ad["h"]:
                t = client.get_type("AdTextAsset")
                t.text = h
                r_.headlines.append(t)
            for d in ad["d"]:
                t = client.get_type("AdTextAsset")
                t.text = d
                r_.descriptions.append(t)
            ad_ops.append(op)
            ad_index.append((g, ad["n"], cfg["ad_group_id"]))
    step("operations built", len(kw_ops) == 28 and len(ad_ops) == 12,
         f"{len(kw_ops)} keywords + {len(ad_ops)} RSAs")

    print("\n=== 5. VALIDATE_ONLY ===")
    for label, svcname, reqtype, ops, method in (
            ("keywords", "AdGroupCriterionService", "MutateAdGroupCriteriaRequest",
             kw_ops, "mutate_ad_group_criteria"),
            ("RSAs", "AdGroupAdService", "MutateAdGroupAdsRequest", ad_ops,
             "mutate_ad_group_ads")):
        req = client.get_type(reqtype)
        req.customer_id = cid
        req.operations.extend(ops)
        req.validate_only = True
        req.partial_failure = False
        try:
            getattr(client.get_service(svcname), method)(request=req)
            step(f"validate_only {label}", True, f"{len(ops)} ops, 0 created")
        except Exception as exc:
            step(f"validate_only {label}", False, str(exc)[:400])
            abort(f"validate_only failed for {label}")
            return 2

    print("\n=== 6. EXECUTE - KEYWORDS (atomic) ===")
    req = client.get_type("MutateAdGroupCriteriaRequest")
    req.customer_id = cid
    req.operations.extend(kw_ops)
    req.validate_only = False
    req.partial_failure = False
    try:
        resp = client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(
            request=req)
        kw_ids = [r.resource_name for r in resp.results]
        log["created"]["keywords"] = kw_ids
        step("keyword mutate", len(kw_ids) == 28, f"{len(kw_ids)} created")
    except Exception as exc:
        step("keyword mutate", False, str(exc)[:600])
        abort("keyword creation failed - NOTHING was created (atomic batch)")
        write_log()
        return 2

    print("\n=== 7. EXECUTE - RSAs (atomic) ===")
    req2 = client.get_type("MutateAdGroupAdsRequest")
    req2.customer_id = cid
    req2.operations.extend(ad_ops)
    req2.validate_only = False
    req2.partial_failure = False
    try:
        resp2 = client.get_service("AdGroupAdService").mutate_ad_group_ads(request=req2)
        ad_ids = [r.resource_name for r in resp2.results]
        log["created"]["rsas"] = ad_ids
        step("RSA mutate", len(ad_ids) == 12, f"{len(ad_ids)} created")
    except Exception as exc:
        step("RSA mutate", False, str(exc)[:600])
        abort("PARTIAL STATE: 28 keywords were created, 0 RSAs. Do not rerun blindly - "
              "the keywords already exist. Recovery: create only the 12 RSAs.")
        write_log()
        return 2

    now = datetime.now(ZoneInfo("America/New_York"))
    log["completed_account_local"] = now.isoformat()
    write_log()
    return 0


def write_log():
    now = datetime.now(ZoneInfo("America/New_York"))
    p = SNAP / f"launch1-execution-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(log, indent=2, default=str), encoding="utf-8")
    print("\nWROTE", p)


if __name__ == "__main__":
    raise SystemExit(main())
