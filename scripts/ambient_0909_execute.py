#!/usr/bin/env python3
"""Execute (or validate-only) one approved 2026-09-09 Ambient package.

Safety contract:
  * refuses to run unless --fingerprint matches the on-disk plan byte-for-byte
  * one atomic GoogleAdsService.mutate per package, partial_failure = False
  * every operation is built from the plan's recorded values, never a literal here
  * --validate-only performs full server-side validation with no write
  * the ClickCease tracking template, geo targets, ad schedules, conversion actions,
    shared sets and manager links are unreachable from every branch by construction
"""
from __future__ import annotations
import argparse, json, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import CID, EXACT_NAME, TZ, NAME, FIVE, client, q, identity_gate  # noqa
from gm_gsa.safety import approval_code  # noqa
from gm_gsa.google_ads import enum_name as E  # noqa
from google.protobuf import field_mask_pb2  # noqa

ALLOWED = {
    "AMB-0909-CPC-1": {"SET_MAXIMIZE_CLICKS_CPC_BID_CEILING"},
    "AMB-0909-NEG-RM-1": {"REMOVE_CAMPAIGN_NEGATIVE_KEYWORD"},
    "AMB-0909-ADS-1": {"PAUSE_AD_GROUP_AD"},
    "AMB-0909-NEG-ADD-1": {"ADD_CAMPAIGN_NEGATIVE_KEYWORD"},
    "AMB-0909-BUD-1": {"UPDATE_CAMPAIGN_BUDGET"},
    "AMB-0909-NEG-RM-2": {"REMOVE_SHARED_LIST_NEGATIVE"},
    # --- 2026-09-09 correction run -------------------------------------------------
    "AMB-0909B-BUD-1": {"UPDATE_CAMPAIGN_BUDGET"},
    "AMB-0909B-CPC-INST-1": {"SET_MAXIMIZE_CLICKS_CPC_BID_CEILING"},
    # NEG-A is deliberately mixed-scope: campaign-level and account-level removals must
    # land together or not at all, so both op types are allowed inside ONE atomic mutate.
    "AMB-0909B-NEG-A": {"REMOVE_CAMPAIGN_NEGATIVE_KEYWORD", "REMOVE_SHARED_LIST_NEGATIVE"},
    "AMB-0909B-COMP-1": {"ADD_CAMPAIGN_NEGATIVE_KEYWORD"},
    # --- 2026-09-09 third pass -----------------------------------------------------
    "AMB-0909C-BUD-1": {"UPDATE_CAMPAIGN_BUDGET"},
    "AMB-0909C-CPC-INST-2": {"SET_MAXIMIZE_CLICKS_CPC_BID_CEILING"},
    "AMB-0909C-NEG-SAVAGE": {"REMOVE_CAMPAIGN_NEGATIVE_KEYWORD"},
    "AMB-0909C-NEG-COMMERCIAL": {"REMOVE_SHARED_LIST_NEGATIVE"},
    "AMB-0909C-COMP-1": {"ADD_CAMPAIGN_NEGATIVE_KEYWORD"},
    "AMB-0910-BUD-2": {"UPDATE_CAMPAIGN_BUDGET"},
    # --- 2026-09-10 -----------------------------------------------------------------
    "AMB-0910-CPC-CAP-1": {"SET_MAXIMIZE_CLICKS_CPC_BID_CEILING"},
    # Commercial build. COMM-1 creates an ad group and its keywords in ONE atomic
    # mutate, so the keywords reference the ad group by temporary resource name.
    "AMB-0910-COMM-1": {"CREATE_AD_GROUP_PAUSED", "CREATE_AD_GROUP_KEYWORD"},
    "AMB-0910-COMM-XNEG-1": {"ADD_AD_GROUP_NEGATIVE_KEYWORD"},
    "AMB-0910-COMM-NEG-1": {"ADD_AD_GROUP_NEGATIVE_KEYWORD"},
    "AMB-0910-COMM-NEG-1-FULL": {"ADD_AD_GROUP_NEGATIVE_KEYWORD"},
    "AMB-0910-COMM-NEG-2": {"ADD_AD_GROUP_NEGATIVE_KEYWORD"},
    "AMB-0910-COMM-NEG-3": {"ADD_AD_GROUP_NEGATIVE_KEYWORD"},
}
ACCOUNT_LEVEL_SET = "11252984411"
# Temporary resource name so an ad group and its keywords can be created in
# ONE atomic mutate. Negative ids are the documented Google Ads convention.
AG_TEMP = f"customers/{CID}/adGroups/-1"


def mask(paths):
    return field_mask_pb2.FieldMask(paths=list(paths))


def build(c, plan):
    name = plan["plan_name"]
    ops, log = [], []
    allowed = ALLOWED[name]
    for a in plan["operations"]:
        o = a["operation"]
        if o not in allowed:
            raise SystemExit(f"{name} refuses operation {o!r}; allowed = {sorted(allowed)}")

        if o == "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING":
            micros = int(a["proposed_state"].split("= ")[1].split(" ")[0])
            if a["field_mask"] != ["target_spend.cpc_bid_ceiling_micros"]:
                raise SystemExit(f"{name}: unexpected field mask on {a['resource_id']}")
            op = c.get_type("MutateOperation")
            x = op.campaign_operation.update
            x.resource_name = f"customers/{CID}/campaigns/{a['resource_id']}"
            x.target_spend.cpc_bid_ceiling_micros = micros
            c.copy_from(op.campaign_operation.update_mask,
                        mask(["target_spend.cpc_bid_ceiling_micros"]))
            ops.append(op)
            log.append(f"UPDATE campaign {a['resource_id']} ({a['resource_name']}) "
                       f"cpc_bid_ceiling_micros -> {micros}")

        elif o == "REMOVE_CAMPAIGN_NEGATIVE_KEYWORD":
            rn = a["resource_name"]
            if not rn.startswith(f"customers/{CID}/campaignCriteria/"):
                raise SystemExit(f"{name}: refusing resource name {rn!r}")
            if a["campaign_id"] not in FIVE:
                raise SystemExit(f"{name}: campaign {a['campaign_id']} is not one of the five")
            if a["proposed_state"] != "REMOVED":
                raise SystemExit(f"{name}: proposed_state must be REMOVED")
            op = c.get_type("MutateOperation")
            op.campaign_criterion_operation.remove = rn
            ops.append(op)
            log.append(f"REMOVE negative [{a['match_type']}] {a['negative_text']!r} "
                       f"from {a['campaign']} ({rn})")

        elif o == "PAUSE_AD_GROUP_AD":
            if a["proposed_state"] != "PAUSED":
                raise SystemExit(f"{name}: this branch pauses and nothing else")
            op = c.get_type("MutateOperation")
            x = op.ad_group_ad_operation.update
            x.resource_name = a["resource_name"]
            x.status = c.enums.AdGroupAdStatusEnum.PAUSED
            c.copy_from(op.ad_group_ad_operation.update_mask, mask(["status"]))
            ops.append(op)
            log.append(f"PAUSE ad {a['ad_id']} in {a['campaign']} ({a['resource_name']})")

        elif o == "ADD_CAMPAIGN_NEGATIVE_KEYWORD":
            txt = a["negative_text"]
            if len(txt.split()) > 10 or len(txt) > 80:
                raise SystemExit(f"{name}: {txt!r} breaches the 10-word / 80-char limit")
            if a["campaign_id"] not in FIVE:
                raise SystemExit(f"{name}: campaign {a['campaign_id']} is not one of the five")
            op = c.get_type("MutateOperation")
            x = op.campaign_criterion_operation.create
            x.campaign = f"customers/{CID}/campaigns/{a['campaign_id']}"
            x.negative = True
            x.keyword.text = txt
            x.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, a["match_type"])
            ops.append(op)
            log.append(f"CREATE negative [{a['match_type']}] {txt!r} on {a['campaign']}")

        elif o == "REMOVE_SHARED_LIST_NEGATIVE":
            rn = a["shared_criterion_resource_name"]
            if not rn.startswith(f"customers/{CID}/sharedCriteria/{ACCOUNT_LEVEL_SET}~"):
                raise SystemExit(
                    f"{name}: refusing {rn!r}. This branch may only touch shared set "
                    f"{ACCOUNT_LEVEL_SET} (the account-level negative keyword list).")
            if a["proposed_state"] != "REMOVED from the account-level list":
                raise SystemExit(f"{name}: unexpected proposed_state on {rn}")
            op = c.get_type("MutateOperation")
            op.shared_criterion_operation.remove = rn
            ops.append(op)
            log.append(f"REMOVE account-level negative [{a['match_type']}] "
                       f"{a['negative_text']!r} ({rn})")

        elif o == "CREATE_AD_GROUP_PAUSED":
            if a["campaign_id"] != "24132507747":
                raise SystemExit(f"{name}: this branch may only add an ad group to the "
                                 f"HVAC Installation campaign 24132507747")
            if a["status"] != "PAUSED":
                raise SystemExit(f"{name}: refusing to create an ad group with status "
                                 f"{a['status']!r}; this branch creates PAUSED only")
            op = c.get_type("MutateOperation")
            x = op.ad_group_operation.create
            x.resource_name = AG_TEMP
            x.name = a["resource_name"]
            x.campaign = f"customers/{CID}/campaigns/{a['campaign_id']}"
            x.status = c.enums.AdGroupStatusEnum.PAUSED
            x.type_ = getattr(c.enums.AdGroupTypeEnum, a["ad_group_type"])
            x.cpc_bid_micros = int(a["cpc_bid_micros"])
            ops.append(op)
            log.append(f"CREATE ad group {a['resource_name']!r} PAUSED in "
                       f"campaign {a['campaign_id']} (temp {AG_TEMP})")

        elif o == "CREATE_AD_GROUP_KEYWORD":
            if a["match_type"] not in ("PHRASE", "EXACT"):
                raise SystemExit(f"{name}: match type {a['match_type']!r} refused; this "
                                 f"branch permits PHRASE and EXACT only, never BROAD")
            if not any(z["operation"] == "CREATE_AD_GROUP_PAUSED"
                       and z["resource_name"] == a["ad_group_ref"]
                       for z in plan["operations"]):
                raise SystemExit(f"{name}: {a['ad_group_ref']!r} is not created by this "
                                 f"same plan; refusing to attach a keyword to an ad group "
                                 f"this package did not create")
            op = c.get_type("MutateOperation")
            x = op.ad_group_criterion_operation.create
            x.ad_group = AG_TEMP
            x.status = c.enums.AdGroupCriterionStatusEnum.ENABLED
            x.keyword.text = a["keyword_text"]
            x.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, a["match_type"])
            ops.append(op)
            log.append(f"CREATE keyword [{a['match_type']}] {a['keyword_text']!r} "
                       f"in {a['ad_group_ref']!r}")

        elif o == "ADD_AD_GROUP_NEGATIVE_KEYWORD":
            # 202339087634 = residential SKAG (routing negative)
            # 199748801029 = commercial SKAG (pack negatives)
            if a["resource_id"] not in ("202339087634", "199748801029"):
                raise SystemExit(f"{name}: refusing ad group {a['resource_id']}; this branch "
                                 f"may only touch the residential SKAG 202339087634 or the "
                                 f"commercial SKAG 199748801029")
            if a["match_type"] != "BROAD":
                raise SystemExit(f"{name}: ad-group negatives in this branch are BROAD only")
            op = c.get_type("MutateOperation")
            x = op.ad_group_criterion_operation.create
            x.ad_group = f"customers/{CID}/adGroups/{a['resource_id']}"
            x.negative = True
            x.keyword.text = a["keyword_text"]
            x.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, a["match_type"])
            ops.append(op)
            log.append(f"CREATE ad-group negative [{a['match_type']}] "
                       f"{a['keyword_text']!r} on {a['resource_name']}")

        elif o == "UPDATE_CAMPAIGN_BUDGET":
            micros = int(a["proposed_state"].split("= ")[1].split(" ")[0])
            op = c.get_type("MutateOperation")
            x = op.campaign_budget_operation.update
            x.resource_name = a["resource_name"]
            x.amount_micros = micros
            c.copy_from(op.campaign_budget_operation.update_mask, mask(["amount_micros"]))
            ops.append(op)
            log.append(f"UPDATE budget {a['resource_id']} ({a['campaign']}) "
                       f"amount_micros -> {micros}")
    return ops, log


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--fingerprint", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    expect = approval_code({"target": plan["target"], "plan": plan["plan_name"],
                            "operations": plan["operations"]})
    if expect != plan["fingerprint"]:
        raise SystemExit(f"PLAN FILE TAMPERED: recomputed {expect}, file says "
                         f"{plan['fingerprint']}")
    if args.fingerprint.strip().upper() != plan["fingerprint"]:
        raise SystemExit(f"FINGERPRINT MISMATCH: plan is {plan['fingerprint']}, "
                         f"you supplied {args.fingerprint}")
    if plan["target"]["customer_id"] != CID:
        raise SystemExit("plan targets a different customer id")

    c = client()
    print("=== IDENTITY GATE ===")
    ident = identity_gate(c)

    ops, log = build(c, plan)
    print(f"\n=== {plan['plan_name']} : {len(ops)} operations "
          f"({'VALIDATE-ONLY' if args.validate_only else 'LIVE WRITE'}) ===")
    for line in log:
        print("  " + line)
    if len(ops) != plan["object_count"]:
        raise SystemExit(f"operation count {len(ops)} != plan object_count "
                         f"{plan['object_count']}")

    svc = c.get_service("GoogleAdsService")
    req = c.get_type("MutateGoogleAdsRequest")
    req.customer_id = CID
    req.mutate_operations.extend(ops)
    req.partial_failure = False
    req.validate_only = bool(args.validate_only)

    receipt = {"plan_name": plan["plan_name"], "fingerprint": plan["fingerprint"],
               "customer_id": CID, "exact_child_account_name": EXACT_NAME,
               "validate_only": bool(args.validate_only),
               "partial_failure": False, "operation_count": len(ops),
               "operations_log": log, "identity": ident["checks"],
               "started_local": datetime.datetime.now(TZ).isoformat()}
    try:
        resp = svc.mutate(request=req)
        results = list(resp.mutate_operation_responses)
        receipt["status"] = "VALIDATED_OK" if args.validate_only else "EXECUTED_OK"
        receipt["results_returned"] = len(results)
        if not args.validate_only:
            names = []
            for r in results:
                for f in ("campaign_result", "campaign_criterion_result",
                          "ad_group_ad_result", "campaign_budget_result",
                          "shared_criterion_result"):
                    v = getattr(r, f, None)
                    if v and v.resource_name:
                        names.append(v.resource_name)
            receipt["resource_names"] = names
        print(f"\n{receipt['status']}: {len(results)} results returned")
    except Exception as e:
        receipt["status"] = "FAILED"
        receipt["error"] = str(e)[:4000]
        print(f"\nFAILED: {type(e).__name__}")
        print(str(e)[:2000])
    receipt["finished_local"] = datetime.datetime.now(TZ).isoformat()
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(receipt, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {outp}")
    return 0 if receipt["status"] != "FAILED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
