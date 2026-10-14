#!/usr/bin/env python3
"""validate_only preflight for the negative-keyword plan.

Builds the real AdGroupCriterion / CampaignCriterion mutate operations and sends
them to Google with validate_only=True. Google parses and validates every
operation and writes NOTHING. This proves field validity, match types, text
limits, duplicate handling and scope ids before any approval is requested.

Nothing here can mutate the account.

QUOTA WARNING. validate_only writes nothing, but every operation still counts
against the developer token's basic-access DAILY OPERATION budget, at exactly
the same rate as a real mutate. Running this unfiltered on 2026-08-30 sent
~14,000 operations and exhausted the whole day's budget for reads and writes
alike, pushing a ready-to-execute account to the next window.

neg_preflight_local.py already checks text validity, duplicates, match types,
already-live redundancy and the keyword-blocking rules with NO API calls. Use
that by default. Reach for this only when you specifically need Google's own
field validation, and scope it with --slug/--layer. It now requires --spend-quota.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402

PLANS = ROOT / "reports" / "st-plans"
OUT = ROOT / "reports" / "st-validate"
BATCH = 1000


def chunk(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layer", choices=["a", "b", "both"], default="both")
    ap.add_argument("--slug", action="append", default=[],
                    help="restrict to these account slugs; repeatable")
    ap.add_argument("--spend-quota", action="store_true",
                    help="required: acknowledge that validate_only consumes the "
                         "same daily operation budget as a real mutate")
    args = ap.parse_args()

    if not args.spend_quota:
        print(__doc__)
        print("REFUSING: this sends validate_only operations to Google and each "
              "one spends the daily basic-access budget.")
        print("  Use scripts/neg_preflight_local.py for local validation "
              "(no API, no quota).")
        print("  If you genuinely need Google-side validation, scope it and "
              "pass --spend-quota, e.g.:")
        print("    neg_validate.py --slug softwind-landscape-masonry "
              "--layer a --spend-quota")
        return 2

    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    OUT.mkdir(parents=True, exist_ok=True)
    mt_enum = client.enums.KeywordMatchTypeEnum
    results = {}

    for plan_path in sorted(PLANS.glob("*-negative-plan.json")):
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        cid = plan["customer_id"]
        slug = plan["slug"]
        if args.slug and slug not in args.slug:
            continue
        rec = {"customer_id": cid, "account_name": plan["account_name"], "layers": {}}
        print("=" * 76)
        print("{}  {}  ({})".format(slug, plan["account_name"], cid))
        print("=" * 76)

        # ---------- LAYER A : campaign-level ----------
        if args.layer in ("a", "both"):
            svc = client.get_service("CampaignCriterionService")
            ops = []
            for block in plan["layer_a_campaign_level"]:
                for n in block["negatives"]:
                    op = client.get_type("CampaignCriterionOperation")
                    c = op.create
                    c.campaign = "customers/{}/campaigns/{}".format(
                        cid, block["campaign_id"])
                    c.negative = True
                    c.keyword.text = n["text"]
                    c.keyword.match_type = (mt_enum.PHRASE if n["match_type"] == "PHRASE"
                                            else mt_enum.EXACT)
                    ops.append(op)
            ok, errs = 0, []
            for i, batch in enumerate(chunk(ops, BATCH)):
                req = client.get_type("MutateCampaignCriteriaRequest")
                req.customer_id = cid
                req.operations = batch
                req.validate_only = True
                req.partial_failure = False
                try:
                    svc.mutate_campaign_criteria(request=req)
                    ok += len(batch)
                except Exception as exc:  # noqa: BLE001
                    msg = str(exc)
                    errs.append({"batch": i, "size": len(batch), "error": msg[:600]})
            rec["layers"]["A_campaign"] = {"operations": len(ops), "validated_ok": ok,
                                           "errors": errs}
            print("  LAYER A campaign-level : {} ops  validated_ok={}  batches_failed={}".format(
                len(ops), ok, len(errs)))
            for e in errs[:3]:
                print("      ERROR batch {}: {}".format(e["batch"], e["error"][:300]))

        # ---------- LAYER B : ad-group-level ----------
        if args.layer in ("b", "both"):
            svc = client.get_service("AdGroupCriterionService")
            ops = []
            for block in plan["layer_b_ad_group_level"]:
                for n in block["negatives"]:
                    op = client.get_type("AdGroupCriterionOperation")
                    c = op.create
                    c.ad_group = "customers/{}/adGroups/{}".format(
                        cid, block["ad_group_id"])
                    c.negative = True
                    c.keyword.text = n["text"]
                    c.keyword.match_type = (mt_enum.PHRASE if n["match_type"] == "PHRASE"
                                            else mt_enum.EXACT)
                    ops.append(op)
            ok, errs = 0, []
            for i, batch in enumerate(chunk(ops, BATCH)):
                req = client.get_type("MutateAdGroupCriteriaRequest")
                req.customer_id = cid
                req.operations = batch
                req.validate_only = True
                req.partial_failure = False
                try:
                    svc.mutate_ad_group_criteria(request=req)
                    ok += len(batch)
                except Exception as exc:  # noqa: BLE001
                    msg = str(exc)
                    errs.append({"batch": i, "size": len(batch), "error": msg[:600]})
            rec["layers"]["B_ad_group"] = {"operations": len(ops), "validated_ok": ok,
                                           "errors": errs}
            print("  LAYER B ad-group-level : {} ops  validated_ok={}  batches_failed={}".format(
                len(ops), ok, len(errs)))
            for e in errs[:3]:
                print("      ERROR batch {}: {}".format(e["batch"], e["error"][:300]))

        results[slug] = rec
        print()

    (OUT / "validate-only.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("receipt -> {}".format((OUT / "validate-only.json").relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
