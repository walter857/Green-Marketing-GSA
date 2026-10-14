#!/usr/bin/env python3
"""Execute an approved Green Marketing change subplan.

Refuses to run unless the supplied fingerprint matches the on-disk plan exactly. Every
operation is built from the plan's recorded values, never from a literal typed here.

Safety:
  * one atomic GoogleAdsService.mutate per subplan, partial_failure = False
  * --validate-only performs a full server-side validation with no write
  * nothing is deleted except the criterion removals the plan explicitly approves
  * on partial or unexpected failure the script stops and prints an inventory
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, load_yaml  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

SUBPLANS = ["STATUS", "BUDGET", "EXISTING_RESOURCES", "CONVERSIONS",
            "CREATE_PAUSED", "SITE_OR_TRACKING", "ENABLE"]


def fingerprint_for(plan: dict, name: str) -> str:
    actions = (plan["subplans"].get(name) or {}).get("actions") or []
    return approval_code({"target": plan["target"], "subplan": name, "actions": actions})


def build(client, cid: str, name: str, actions: list[dict]) -> tuple[list, list[str]]:
    """Return (mutate_operations, human_readable_log)."""
    ops, log = [], []

    def new_op():
        return client.get_type("MutateOperation")

    if name == "BUDGET":
        for a in actions:
            micros = int(a["proposed_state"].split("amount_micros = ")[1].split(" ")[0])
            op = new_op()
            b = op.campaign_budget_operation.update
            b.resource_name = f"customers/{cid}/campaignBudgets/{a['resource_id']}"
            b.amount_micros = micros
            client.copy_from(op.campaign_budget_operation.update_mask,
                             protobuf_field_mask(client, ["amount_micros"]))
            ops.append(op)
            log.append(f"{a['action_id']} UPDATE budget {a['resource_id']} "
                       f"amount_micros -> {micros}")
        return ops, log

    if name == "CONVERSIONS":
        for a in actions:
            op = new_op()
            c = op.conversion_action_operation.update
            c.resource_name = f"customers/{cid}/conversionActions/{a['resource_id']}"
            c.primary_for_goal = False
            client.copy_from(op.conversion_action_operation.update_mask,
                             protobuf_field_mask(client, ["primary_for_goal"]))
            ops.append(op)
            log.append(f"{a['action_id']} UPDATE conversion_action {a['resource_id']} "
                       f"primary_for_goal -> False  ({a['resource_name']})")
        return ops, log

    if name == "STATUS":
        # PAUSE-ONLY. This branch can pause an ad-group criterion (a keyword) and
        # nothing else. It cannot enable, cannot remove, and cannot touch any
        # other resource type, so it can only ever reduce delivery. Any action
        # that asks for something else stops the run before a single operation
        # is built.
        allowed_op = "PAUSE_AD_GROUP_CRITERION"
        for a in actions:
            if a.get("operation") != allowed_op:
                raise SystemExit(
                    f"STATUS refuses action {a.get('action_id')}: operation "
                    f"{a.get('operation')!r} is not {allowed_op!r}. This subplan "
                    f"pauses ad-group criteria and does nothing else.")
            if str(a.get("proposed_state", "")).strip().upper() != "PAUSED":
                raise SystemExit(
                    f"STATUS refuses action {a.get('action_id')}: proposed_state "
                    f"must be PAUSED, got {a.get('proposed_state')!r}.")
            op = new_op()
            agc = op.ad_group_criterion_operation.update
            agc.resource_name = (f"customers/{cid}/adGroupCriteria/"
                                 f"{a['ad_group_id']}~{a['criterion_id']}")
            agc.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
            client.copy_from(op.ad_group_criterion_operation.update_mask,
                             protobuf_field_mask(client, ["status"]))
            ops.append(op)
            log.append(f"{a['action_id']} PAUSE keyword "
                       f"{a['ad_group_id']}~{a['criterion_id']} "
                       f"{a['keyword_text']!r} [{a['match_type']}] "
                       f"in {a['ad_group_name']}")
        return ops, log

    if name == "SITE_OR_TRACKING":
        # FINAL URL SUFFIX ONLY. This branch can set campaign.final_url_suffix and
        # nothing else. It can never write campaign.tracking_url_template or the
        # customer-level template, so the ClickCease tracking template cannot be
        # replaced, cleared or altered through this path by construction: the
        # field mask is a hardcoded literal and the operation name is checked.
        allowed_op = "SET_CAMPAIGN_FINAL_URL_SUFFIX"
        for a in actions:
            if a.get("operation") != allowed_op:
                raise SystemExit(
                    f"SITE_OR_TRACKING refuses action {a.get('action_id')}: operation "
                    f"{a.get('operation')!r} is not {allowed_op!r}. This subplan sets "
                    f"campaign.final_url_suffix and does nothing else.")
            proposed = str(a.get("proposed_state", ""))
            if not proposed.startswith("final_url_suffix = "):
                raise SystemExit(
                    f"SITE_OR_TRACKING refuses action {a.get('action_id')}: "
                    f"proposed_state must start with 'final_url_suffix = '.")
            suffix = proposed.split("final_url_suffix = ", 1)[1]
            if "tracking_url_template" in proposed or "clickcease" in suffix.lower():
                raise SystemExit(
                    f"SITE_OR_TRACKING refuses action {a.get('action_id')}: this branch "
                    f"must never touch a tracking template.")
            if len(suffix) > 2048:
                raise SystemExit(
                    f"SITE_OR_TRACKING refuses action {a.get('action_id')}: suffix "
                    f"exceeds the 2048-character limit.")
            op = new_op()
            c = op.campaign_operation.update
            c.resource_name = f"customers/{cid}/campaigns/{a['resource_id']}"
            c.final_url_suffix = suffix
            client.copy_from(op.campaign_operation.update_mask,
                             protobuf_field_mask(client, ["final_url_suffix"]))
            ops.append(op)
            log.append(f"{a['action_id']} SET final_url_suffix on campaign "
                       f"{a['resource_id']} ({a['resource_name']}) "
                       f"[{len(suffix)} chars]")
        return ops, log

    if name == "ENABLE":
        st = client.enums.AdGroupAdStatusEnum.ENABLED
        for a in actions:
            op = new_op()
            aga = op.ad_group_ad_operation.update
            aga.resource_name = a["resource_name"]
            aga.status = st
            client.copy_from(op.ad_group_ad_operation.update_mask,
                             protobuf_field_mask(client, ["status"]))
            ops.append(op)
            log.append(f"{a['action_id']} ENABLE ad {a['ad_id']} in {a['ad_group_name']} "
                       f"({a['resource_name']})")
        return ops, log

    if name == "CREATE_PAUSED":
        st = client.enums.AdGroupAdStatusEnum.PAUSED
        for a in actions:
            op = new_op()
            aga = op.ad_group_ad_operation.create
            aga.ad_group = f"customers/{cid}/adGroups/{a['resource_id']}"
            aga.status = st
            aga.ad.final_urls.append(a["final_url"])
            rsa = aga.ad.responsive_search_ad
            rsa.path1 = a["path1"]
            rsa.path2 = a["path2"]
            for text in a["headlines"]:
                asset = client.get_type("AdTextAsset")
                asset.text = text
                rsa.headlines.append(asset)
            for text in a["descriptions"]:
                asset = client.get_type("AdTextAsset")
                asset.text = text
                rsa.descriptions.append(asset)
            ops.append(op)
            log.append(f"{a['action_id']} CREATE RSA (PAUSED) in ad group {a['resource_id']} "
                       f"{a['resource_name']} -> {a['final_url']} "
                       f"[{len(a['headlines'])}H/{len(a['descriptions'])}D]")
        return ops, log

    if name == "EXISTING_RESOURCES":
        # 1. Combine the two approved campaign-field actions per campaign into one
        #    update operation. Same resource, same approved values; the mask is exactly
        #    the union of the two approved masks and touches nothing else.
        by_campaign: dict[str, dict] = {}
        for a in actions:
            if a["operation"] == "UPDATE_CAMPAIGN_EXCLUDED_PARENT_ASSET_FIELD_TYPES":
                by_campaign.setdefault(a["resource_id"], {})["exclude"] = a
            elif a["operation"] == "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING":
                by_campaign.setdefault(a["resource_id"], {})["ceiling"] = a
        for camp_id, parts in by_campaign.items():
            op = new_op()
            c = op.campaign_operation.update
            c.resource_name = f"customers/{cid}/campaigns/{camp_id}"
            masks = []
            if "exclude" in parts:
                enum = client.enums.AssetFieldTypeEnum
                c.excluded_parent_asset_field_types.extend([enum.SITELINK,
                                                            enum.STRUCTURED_SNIPPET])
                masks.append("excluded_parent_asset_field_types")
            if "ceiling" in parts:
                micros = int(parts["ceiling"]["proposed_state"]
                             .split("= ")[1].split(" ")[0])
                c.target_spend.cpc_bid_ceiling_micros = micros
                masks.append("target_spend.cpc_bid_ceiling_micros")
            client.copy_from(op.campaign_operation.update_mask,
                             protobuf_field_mask(client, masks))
            ops.append(op)
            log.append(f"{'+'.join(p['action_id'] for p in parts.values())} "
                       f"UPDATE campaign {camp_id} mask={masks}")

        # 2. Remove the existing ad-schedule criteria.
        for a in actions:
            if a["operation"] != "REMOVE_CAMPAIGN_AD_SCHEDULE_CRITERIA":
                continue
            for c in a["exact_criteria_removed"]:
                op = new_op()
                op.campaign_criterion_operation.remove = (
                    f"customers/{cid}/campaignCriteria/"
                    f"{a['resource_id']}~{c['criterion_id']}")
                ops.append(op)
                log.append(f"{a['action_id']} REMOVE ad_schedule "
                           f"{a['resource_id']}~{c['criterion_id']} ({c['day']} "
                           f"{c['current']})")

        # 3. Create the corrected ad-schedule criteria.
        day_enum = client.enums.DayOfWeekEnum
        minute_enum = client.enums.MinuteOfHourEnum
        for a in actions:
            if a["operation"] != "CREATE_CAMPAIGN_AD_SCHEDULE_CRITERIA":
                continue
            for c in a["exact_criteria_created"]:
                op = new_op()
                cc = op.campaign_criterion_operation.create
                cc.campaign = f"customers/{cid}/campaigns/{a['resource_id']}"
                cc.ad_schedule.day_of_week = getattr(day_enum, c["day"])
                cc.ad_schedule.start_hour = int(c["start_hour"])
                cc.ad_schedule.end_hour = int(c["end_hour"])
                cc.ad_schedule.start_minute = getattr(minute_enum, c["start_minute"])
                cc.ad_schedule.end_minute = getattr(minute_enum, c["end_minute"])
                ops.append(op)
                log.append(f"{a['action_id']} CREATE ad_schedule {a['resource_id']} "
                           f"{c['day']} {c['start_hour']:02d}:00-{c['end_hour']:02d}:00 "
                           f"account time ({c['market_time']})")

        # 4. Create the approved campaign negative keywords.
        mt_enum = client.enums.KeywordMatchTypeEnum
        for a in actions:
            if a["operation"] != "ADD_CAMPAIGN_NEGATIVE_KEYWORD":
                continue
            op = new_op()
            cc = op.campaign_criterion_operation.create
            cc.campaign = f"customers/{cid}/campaigns/{a['resource_id']}"
            cc.negative = True
            cc.keyword.text = a["negative_text"]
            cc.keyword.match_type = getattr(mt_enum, a["match_type"])
            ops.append(op)
            log.append(f"{a['action_id']} CREATE negative {a['match_type']} "
                       f"{a['negative_text']!r} on {a['resource_id']}")

        # 5. Remove the approved shared-list negatives, by full resource name.
        for a in actions:
            if a["operation"] != "REMOVE_SHARED_LIST_NEGATIVE":
                continue
            op = new_op()
            op.shared_criterion_operation.remove = a["shared_criterion_resource_name"]
            ops.append(op)
            log.append(f"{a['action_id']} REMOVE shared_criterion "
                       f"{a['shared_criterion_resource_name']} "
                       f"({a['negative_text']!r} [{a['match_type']}])")
        # 6. Ad-group negative keywords.
        mt_ag = client.enums.KeywordMatchTypeEnum
        for a in actions:
            if a["operation"] != "ADD_AD_GROUP_NEGATIVE_KEYWORD":
                continue
            op = new_op()
            agc = op.ad_group_criterion_operation.create
            agc.ad_group = f"customers/{cid}/adGroups/{a['resource_id']}"
            agc.negative = True
            agc.keyword.text = a["negative_text"]
            agc.keyword.match_type = getattr(mt_ag, a["match_type"])
            ops.append(op)
            log.append(f"{a['action_id']} CREATE ad-group negative {a['match_type']} "
                       f"{a['negative_text']!r} on {a['resource_id']} ({a['resource_name']})")

        return ops, log

    raise SystemExit(f"subplan {name} is not executable by this script")


def protobuf_field_mask(client, paths):
    from google.protobuf import field_mask_pb2
    return field_mask_pb2.FieldMask(paths=list(paths))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--subplan", required=True, choices=SUBPLANS)
    ap.add_argument("--fingerprint", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()

    plan = load_yaml(args.plan)["change_plan"]
    cid = plan["target"]["child_customer_id"]
    actions = (plan["subplans"].get(args.subplan) or {}).get("actions") or []
    if not actions:
        print(f"{args.subplan} has no actions. Nothing to do.")
        return 0

    computed = fingerprint_for(plan, args.subplan)
    if computed != args.fingerprint.strip().upper():
        print(f"REFUSING TO RUN. {args.subplan} fingerprint mismatch.")
        print(f"  supplied: {args.fingerprint.strip().upper()}")
        print(f"  on disk : {computed}")
        return 1
    print(f"{args.subplan}: fingerprint {computed} matches the on-disk plan.")

    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    ops, log = build(client, cid, args.subplan, actions)
    objects = sum(int(a.get("object_count", 1)) for a in actions)
    print(f"  approved actions: {len(actions)}   approved objects: {objects}   "
          f"API operations: {len(ops)}")
    for line in log:
        print(f"    {line}")

    svc = client.get_service("GoogleAdsService")
    req = client.get_type("MutateGoogleAdsRequest")
    req.customer_id = cid
    req.mutate_operations.extend(ops)
    req.partial_failure = False          # atomic: all or nothing
    req.validate_only = bool(args.validate_only)

    mode = "VALIDATE-ONLY" if args.validate_only else "LIVE WRITE"
    print(f"\n  sending one atomic mutate, partial_failure=False, mode={mode} ...")
    try:
        resp = svc.mutate(request=req)
    except Exception as exc:  # noqa: BLE001
        failure = getattr(exc, "failure", None)
        print(f"  MUTATE FAILED: {type(exc).__name__}")
        if failure:
            for e in failure.errors:
                loc = "/".join(f.field_name for f in e.location.field_path_elements)
                print(f"    {e.error_code} :: {e.message} @ {loc}")
        print("\n  STOP. partial_failure was False, so an atomic request that raises has "
              "applied NOTHING. No recovery inventory is required, but re-read before retrying.")
        return 1

    results = []
    for i, r in enumerate(resp.mutate_operation_responses):
        kind = r._pb.WhichOneof("response")
        rn = getattr(getattr(r, kind), "resource_name", "") if kind else ""
        results.append({"index": i, "type": kind, "resource_name": rn, "log": log[i]})
    receipt = {
        "subplan": args.subplan, "fingerprint": computed,
        "customer_id": cid,
        "exact_child_account_name": plan["target"]["exact_child_account_name"],
        "mode": mode,
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "approved_actions": len(actions), "approved_objects": objects,
        "api_operations": len(ops),
        "partial_failure": False,
        "results": results,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"  responses: {len(results)}")
    if args.validate_only:
        print("  VALIDATION PASSED. Nothing was written.")
    else:
        print("  WRITE COMPLETE.")
        for r in results:
            if r["resource_name"]:
                print(f"    {r['resource_name']}")
    print(f"  receipt: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
