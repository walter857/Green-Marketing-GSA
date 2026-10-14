#!/usr/bin/env python3
"""Staged executor for the approved negative-keyword plan.

Refuses to run without an explicit --execute flag AND an approval string whose
fingerprint matches the bundle byte-for-byte.

Order of operations per account:
  1. fresh identity re-check (name + id + not manager + not test)
  2. pre-change snapshot: campaign negative counts, campaign/budget/keyword counts
  3. batched creates with partial_failure=True (one bad op cannot kill a batch)
  4. readback: re-query campaign_criterion and diff against the plan
  5. unchanged-proof: campaign, budget and keyword counts must be identical
  6. EXCLUDED-label check: count search_term_view rows now marked EXCLUDED

Quota-aware. On RESOURCE_EXHAUSTED it stops immediately, writes an inventory of
everything already created, and exits non-zero. It never blindly reruns.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402

BUNDLES = {
    "ambient-cooling-heating": "clients/ambient-cooling-heating/plans/2026-08-28-negative-expansion.json",
    "pro-green-austin": "clients/pro-green-austin/plans/2026-08-28-negative-expansion.json",
    "softwind-power-washing": "clients/softwind-power-washing/plans/2026-08-28-negative-expansion.json",
    # Built 2026-08-30; SLM was quota-blocked when the other three were planned.
    "softwind-landscape-masonry": "clients/softwind-landscape-masonry/plans/2026-08-30-negative-expansion.json",
}
CAMPAIGN_LAYERS = {"NEG_CAMPAIGN_LEVEL", "NEG_NAME_BROAD",
                   "NEG_CROSS_ACCOUNT_FENCE"}
BATCH = 500


class QuotaExhausted(RuntimeError):
    pass


def is_quota(exc) -> bool:
    return "RESOURCE_EXHAUSTED" in str(exc) or "Resource has been exhausted" in str(exc)


def rows(svc, cid, q):
    return list(svc.search(customer_id=cid, query=q))


def snapshot(svc, cid):
    camps = rows(svc, cid, "SELECT campaign.id, campaign.status, "
                           "campaign_budget.amount_micros FROM campaign "
                           "WHERE campaign.status != 'REMOVED'")
    negs = rows(svc, cid, "SELECT campaign.id, campaign_criterion.criterion_id "
                          "FROM campaign_criterion WHERE campaign_criterion.negative = true "
                          "AND campaign_criterion.type = 'KEYWORD' "
                          "AND campaign.status != 'REMOVED'")
    kws = rows(svc, cid, "SELECT ad_group_criterion.criterion_id FROM keyword_view "
                         "WHERE ad_group_criterion.status != 'REMOVED' "
                         "AND ad_group.status != 'REMOVED' AND campaign.status != 'REMOVED'")
    per = {}
    for r in negs:
        per[str(r.campaign.id)] = per.get(str(r.campaign.id), 0) + 1
    return {
        "campaigns": len(camps),
        "budgets": {str(r.campaign.id): r.campaign_budget.amount_micros for r in camps},
        "campaign_negatives_total": len(negs),
        "campaign_negatives_per_campaign": per,
        "positive_keywords": len(kws),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True, choices=sorted(BUNDLES))
    ap.add_argument("--approve", action="append", default=[],
                    metavar="LAYER=FINGERPRINT",
                    help="e.g. --approve NEG_CAMPAIGN_LEVEL=A8E3523F7521")
    ap.add_argument("--execute", action="store_true",
                    help="without this the script only prints what it would do")
    args = ap.parse_args()

    bundle = json.loads((ROOT / BUNDLES[args.slug]).read_text(encoding="utf-8"))
    target = bundle["target"]
    cid = target["child_customer_id"]

    approvals = {}
    for a in args.approve:
        if "=" not in a:
            print("bad --approve value: {}".format(a))
            return 2
        k, v = a.split("=", 1)
        approvals[k.strip().upper()] = v.strip().upper()

    layers = []
    for key, fp in approvals.items():
        sub = bundle["subplans"].get(key)
        if not sub:
            print("FAIL unknown layer {}".format(key))
            return 2
        if sub["fingerprint"] != fp:
            print("FAIL fingerprint mismatch for {}: bundle has {}, you gave {}".format(
                key, sub["fingerprint"], fp))
            return 2
        if key not in CAMPAIGN_LAYERS:
            print("FAIL {} is not a campaign-level layer; this executor only "
                  "writes campaign criteria".format(key))
            return 2
        layers.append((key, sub))
    if not layers:
        print("Nothing approved. Pass --approve LAYER=FINGERPRINT.")
        return 2

    total = sum(s["object_count"] for _, s in layers)
    print("=" * 78)
    print("{}   {}".format(target["exact_child_account_name"], cid))
    print("service: {}".format(target["exact_service"]))
    print("=" * 78)
    for key, sub in layers:
        print("  {:<20} {:>6} objects across {} campaigns   fp={}".format(
            key, sub["object_count"], sub["scope_count"], sub["fingerprint"]))
    print("  TOTAL OPERATIONS: {}".format(total))
    if args.execute:
        print("REFUSED: legacy negative-keyword writes are disabled pending independent authorization.")
        return 1
    if not args.execute:
        print("\nDRY RUN. Re-run with --execute to apply.")
        return 0

    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    ccs = client.get_service("CampaignCriterionService")
    mt_enum = client.enums.KeywordMatchTypeEnum
    stamp = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    receipts = ROOT / "clients" / args.slug / "receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    ledger = {"slug": args.slug, "customer_id": cid, "started": stamp,
              "approved": {k: s["fingerprint"] for k, s in layers},
              "created": [], "errors": [], "stopped_early": False}

    # ---- 1. identity gate ------------------------------------------------
    try:
        ident = rows(svc, cid, "SELECT customer.id, customer.descriptive_name, "
                               "customer.manager, customer.test_account FROM customer LIMIT 1")[0]
    except Exception as exc:  # noqa: BLE001
        print("IDENTITY READ FAILED: {}".format(str(exc)[:200]))
        return 1
    ok = (ident.customer.descriptive_name == target["exact_child_account_name"]
          and str(ident.customer.id) == cid
          and not ident.customer.manager and not ident.customer.test_account)
    print("\nidentity: observed {!r} / {} -> {}".format(
        ident.customer.descriptive_name, ident.customer.id, "PASS" if ok else "FAIL"))
    if not ok:
        print("ABORT: identity gate failed. Nothing was written.")
        return 1

    # ---- 2. pre-change snapshot -----------------------------------------
    before = snapshot(svc, cid)
    ledger["before"] = before
    print("before: campaigns={} campaign_negatives={} positive_keywords={}".format(
        before["campaigns"], before["campaign_negatives_total"],
        before["positive_keywords"]))

    # ---- 3. batched creates ---------------------------------------------
    try:
        for key, sub in layers:
            ops = []
            for block in sub["detail"]:
                for n in block["negatives"]:
                    op = client.get_type("CampaignCriterionOperation")
                    c = op.create
                    c.campaign = "customers/{}/campaigns/{}".format(
                        cid, block["campaign_id"])
                    c.negative = True
                    c.keyword.text = n["text"]
                    c.keyword.match_type = getattr(mt_enum, n["match_type"])
                    ops.append(op)
            print("\n{}: sending {} operations".format(key, len(ops)))
            done = 0
            for i in range(0, len(ops), BATCH):
                batch = ops[i:i + BATCH]
                req = client.get_type("MutateCampaignCriteriaRequest")
                req.customer_id = cid
                req.operations = batch
                req.partial_failure = True
                req.validate_only = False
                try:
                    resp = ccs.mutate_campaign_criteria(request=req)
                except Exception as exc:  # noqa: BLE001
                    if is_quota(exc):
                        raise QuotaExhausted(str(exc)[:300]) from exc
                    ledger["errors"].append({"layer": key, "batch": i // BATCH,
                                             "error": str(exc)[:400]})
                    print("   batch {} FAILED: {}".format(i // BATCH, str(exc)[:160]))
                    continue
                made = [r.resource_name for r in resp.results if r.resource_name]
                ledger["created"] += made
                done += len(made)
                if resp.partial_failure_error and resp.partial_failure_error.message:
                    ledger["errors"].append({
                        "layer": key, "batch": i // BATCH,
                        "partial_failure": resp.partial_failure_error.message[:400]})
                print("   batch {:>3}: sent {:>4}  created {:>4}  running total {}".format(
                    i // BATCH, len(batch), len(made), done))
    except QuotaExhausted as exc:
        ledger["stopped_early"] = True
        ledger["stop_reason"] = "RESOURCE_EXHAUSTED: {}".format(exc)
        p = receipts / "neg-exec-PARTIAL-{}.json".format(stamp)
        p.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
        print("\nQUOTA EXHAUSTED MID-RUN. Stopped.")
        print("  created so far: {}".format(len(ledger["created"])))
        print("  inventory -> {}".format(p.relative_to(ROOT)))
        print("  Do NOT rerun blindly. Re-derive the remaining set against a fresh "
              "readback first: the redundancy filter will skip what already exists.")
        return 1

    # ---- 4/5. readback + unchanged proof ---------------------------------
    after = snapshot(svc, cid)
    ledger["after"] = after
    added = after["campaign_negatives_total"] - before["campaign_negatives_total"]
    print("\nreadback: campaign_negatives {} -> {}  (+{})".format(
        before["campaign_negatives_total"], after["campaign_negatives_total"], added))
    print("expected +{} | created resource names {}".format(total, len(ledger["created"])))
    unchanged = (before["campaigns"] == after["campaigns"]
                 and before["budgets"] == after["budgets"]
                 and before["positive_keywords"] == after["positive_keywords"])
    print("unrelated resources unchanged: {}".format("YES" if unchanged else "NO"))
    ledger["unchanged_proof"] = unchanged
    ledger["net_added"] = added
    ledger["expected"] = total

    # ---- 6. the owner's actual acceptance test ---------------------------
    try:
        st = rows(svc, cid,
                  "SELECT search_term_view.status, metrics.impressions "
                  "FROM search_term_view WHERE segments.date DURING LAST_30_DAYS")
        excl = sum(1 for r in st if enum_name(r.search_term_view.status) == "EXCLUDED")
        print("search terms now marked EXCLUDED (last 30 days): {} of {} rows".format(
            excl, len(st)))
        ledger["excluded_rows_after"] = excl
        ledger["search_term_rows_checked"] = len(st)
    except Exception as exc:  # noqa: BLE001
        print("EXCLUDED-label check skipped: {}".format(str(exc)[:160]))

    p = receipts / "neg-exec-{}.json".format(stamp)
    p.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print("\nreceipt -> {}".format(p.relative_to(ROOT)))
    return 0 if (added == total and unchanged and not ledger["errors"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
