#!/usr/bin/env python3
"""Ambient | 2026-09-25 | Owner-approved: reuse 410-415-9517 as the heating call-asset number.

Creates ONE new call asset (410) 415-9517 that mirrors 407995613637 exactly except the number:
same Mon-Fri 08:00-16:00 schedule (the authorized call hours), same
USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION reporting (Google call reporting stays on). On every
HEATING campaign that links 407995613637, it adds a link to the new asset with the SAME status the
old link has, then pauses the old link. Commercial (24132507747) and paused cooling campaigns keep
705-6354. Landing-page 705-6354, paid Maps 216-4650 and GBP numbers are untouched.

    python ambient_0925_call_9517.py plan | execute --fp X | readback
"""
from __future__ import annotations
import sys, json, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS
from gm_gsa.safety import approval_code
from google.protobuf import field_mask_pb2

NAME = "AMB-0925-CALL-9517-1"
OLD = "407995613637"
HEATING = ["24257819463", "24268690038", "24257819466", "24132507744", "24279798229", "24268690041",
           "24274160783", "24295088845"]
NUMBER = "(410) 415-9517"
DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]


def state(c):
    old = q(c, f"""SELECT asset.id, asset.call_asset.phone_number, asset.call_asset.country_code,
            asset.call_asset.call_conversion_reporting_state, asset.call_asset.ad_schedule_targets
            FROM asset WHERE asset.id = {OLD}""")[0].asset.call_asset
    links = {str(r.campaign.id): E(r.campaign_asset.status) for r in q(c, f"""SELECT campaign.id, campaign_asset.status
             FROM campaign_asset WHERE campaign_asset.field_type = 'CALL' AND campaign_asset.asset = 'customers/{CID}/assets/{OLD}'
             AND campaign_asset.status != 'REMOVED'""")}
    new = [str(r.asset.id) for r in q(c, "SELECT asset.id, asset.name FROM asset WHERE asset.type = 'CALL' AND asset.name = 'Heating call asset 410-415-9517 (WhatConverts Google Ads Extension)'")]
    return old, links, new


def build(c):
    old, links, new = state(c)
    sched = [(E(s.day_of_week), s.start_hour, E(s.start_minute), s.end_hour, E(s.end_minute)) for s in old.ad_schedule_targets]
    errs = []
    if sorted(x[0] for x in sched) != sorted(DAYS) or any(x[1] != 8 or x[3] != 16 for x in sched):
        errs.append(f"old schedule changed: {sched}")
    if new: errs.append(f"new asset already exists {new}")
    plan = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342", "plan_name": NAME,
            "built_local": datetime.datetime.now(TZ).date().isoformat(), "authority": "owner approval 2026-09-25 (reuse 410-415-9517, no purchase)",
            "new_call_asset": {"phone_number": NUMBER, "country_code": old.country_code,
                               "call_conversion_reporting_state": E(old.call_conversion_reporting_state),
                               "schedule": "Mon-Fri 08:00-16:00 (mirrors 407995613637)"},
            "relinks": [{"campaign": k, "new_link_status": links[k], "old_link": "PAUSED"} for k in HEATING if k in links],
            "untouched": {k: v for k, v in links.items() if k not in HEATING},
            "errors": errs}
    plan["operation_count"] = 1 + 2 * len(plan["relinks"])
    return plan


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["plan", "execute", "readback"]); ap.add_argument("--fp")
    a = ap.parse_args()
    c = client(); identity_gate(c, verbose=False)
    if a.mode == "readback":
        return readback(c)
    plan = build(c); fp = approval_code(plan)
    if a.mode == "plan":
        plan["fingerprint"] = fp
        (PLANS / f"{NAME}.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print(f"PLAN {NAME} {fp} ops={plan['operation_count']} errors={plan['errors']}")
        for r in plan["relinks"]: print("  ", r)
        print("  untouched:", plan["untouched"]); return
    if a.fp != fp or plan["errors"]: sys.exit(f"ABORT fp {fp} != {a.fp} or {plan['errors']}")
    ga = c.get_service("GoogleAdsService"); apath = c.get_service("AssetService").asset_path
    ops = []
    m = c.get_type("MutateOperation"); x = m.asset_operation.create
    x.resource_name = apath(CID, -1); x.name = "Heating call asset 410-415-9517 (WhatConverts Google Ads Extension)"
    x.call_asset.phone_number = NUMBER; x.call_asset.country_code = plan["new_call_asset"]["country_code"]
    x.call_asset.call_conversion_reporting_state = c.enums.CallConversionReportingStateEnum.USE_ACCOUNT_LEVEL_CALL_CONVERSION_ACTION
    for d in DAYS:
        s = c.get_type("AdScheduleInfo"); s.day_of_week = getattr(c.enums.DayOfWeekEnum, d)
        s.start_hour = 8; s.end_hour = 16; s.start_minute = c.enums.MinuteOfHourEnum.ZERO; s.end_minute = c.enums.MinuteOfHourEnum.ZERO
        x.call_asset.ad_schedule_targets.append(s)
    ops.append(m)
    casvc = c.get_service("CampaignAssetService")
    for r in plan["relinks"]:
        m = c.get_type("MutateOperation"); l = m.campaign_asset_operation.create
        l.campaign = c.get_service("CampaignService").campaign_path(CID, r["campaign"]); l.asset = apath(CID, -1)
        l.field_type = c.enums.AssetFieldTypeEnum.CALL; l.status = getattr(c.enums.AssetLinkStatusEnum, r["new_link_status"])
        ops.append(m)
        m = c.get_type("MutateOperation"); u = m.campaign_asset_operation.update
        u.resource_name = casvc.campaign_asset_path(CID, r["campaign"], OLD, "CALL"); u.status = c.enums.AssetLinkStatusEnum.PAUSED
        m.campaign_asset_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"])); ops.append(m)
    rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.mutate_operations.extend(ops)
    rq.validate_only = True; ga.mutate(request=rq); print("validate_only PASS")
    rq.validate_only = False; resp = ga.mutate(request=rq)
    names = [getattr(r, f).resource_name for r in resp.mutate_operation_responses for f in ("asset_result", "campaign_asset_result") if r._pb.HasField(f)]
    rec = {"plan": NAME, "fingerprint": fp, "executed_local": datetime.datetime.now(TZ).isoformat(), "resources": names}
    (RECEIPTS / f"{NAME}-EXECUTED.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("EXECUTED", len(names), names[0])


def readback(c):
    fails = []
    new = q(c, """SELECT asset.id, asset.call_asset.phone_number, asset.call_asset.call_conversion_reporting_state,
            asset.call_asset.ad_schedule_targets, asset.policy_summary.approval_status, asset.policy_summary.review_status
            FROM asset WHERE asset.type = 'CALL' AND asset.name = 'Heating call asset 410-415-9517 (WhatConverts Google Ads Extension)'""")
    if len(new) != 1: sys.exit(f"FAIL: {len(new)} new assets")
    n = new[0].asset; nid = str(n.id)
    print(f"asset {nid} {n.call_asset.phone_number} {E(n.call_asset.call_conversion_reporting_state)} "
          f"{[(E(s.day_of_week)[:3], s.start_hour, s.end_hour) for s in n.call_asset.ad_schedule_targets]} "
          f"review {E(n.policy_summary.approval_status)}/{E(n.policy_summary.review_status)}")
    links = {}
    for r in q(c, "SELECT campaign.id, campaign.name, campaign.status, campaign_asset.asset, campaign_asset.status FROM campaign_asset WHERE campaign_asset.field_type = 'CALL' AND campaign_asset.status != 'REMOVED'"):
        links.setdefault(str(r.campaign.id), {})[r.campaign_asset.asset.split("/")[-1]] = (E(r.campaign_asset.status), E(r.campaign.status), r.campaign.name[:45])
    rec = json.loads((RECEIPTS / f"{NAME}-EXECUTED.json").read_text(encoding="utf-8"))
    plan = json.loads((PLANS / f"{NAME}.json").read_text(encoding="utf-8"))
    for r in plan["relinks"]:
        got = links.get(r["campaign"], {})
        ok = got.get(nid, ("-",))[0] == r["new_link_status"] and got.get(OLD, ("-",))[0] == "PAUSED"
        print(f"  {'PASS' if ok else 'FAIL'} {r['campaign']} new={got.get(nid, ('-',))[0]} old705={got.get(OLD, ('-',))[0]} {got.get(OLD, ('','',''))[2]}")
        if not ok: fails.append(r["campaign"])
    for k, v in plan["untouched"].items():
        ok = links.get(k, {}).get(OLD, ("-",))[0] == v and nid not in links.get(k, {})
        print(f"  {'PASS' if ok else 'FAIL'} untouched {k} old705={links.get(k, {}).get(OLD, ('-',))[0]}")
        if not ok: fails.append(k)
    cs = q(c, "SELECT customer.call_reporting_setting.call_reporting_enabled FROM customer")[0].customer.call_reporting_setting
    print("  call reporting enabled:", cs.call_reporting_enabled)
    if not cs.call_reporting_enabled: fails.append("call reporting off")
    rec["readback"] = {"asset_id": nid, "fails": fails}
    (RECEIPTS / f"{NAME}-EXECUTED.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("READBACK FAILS:", fails or 0)


if __name__ == "__main__":
    main()
