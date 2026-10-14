#!/usr/bin/env python3
"""MasterGrass - Live | 2026-09-27 | second-approval packages after readback QA (27 PASS / 0 FAIL).

MG-0927-ENABLE     enable drainage PMax campaign 24287457516 + asset group 6752116688, the 20 new RSAs
                   (MG-0926-RSA receipt) and the 6 new callout links.
MG-0927-OLD-PAUSE  pause each ad group's old city RSA ONLY when both new RSAs there read APPROVED or
                   APPROVED_LIMITED, so no ad group is left without an approved ad. Re-runnable: pauses
                   what has cleared review, reports the rest as waiting.

Modes: plan | validate --pkg X | execute --pkg X --fp CODE
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

from google.protobuf import field_mask_pb2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import CID, EXACT_NAME, GM_MANAGER, PLANS, ROOT, TZ, E, client, q  # noqa: E402
from mg_0926b_copy import NEW_CALLOUTS  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

REC = ROOT / "clients" / "mastergrass-lawn-care" / "receipts"
PMAX, AG = "24287457516", "6752116688"
LAND, HARD = "23905193676", "23914692658"
rsa_rec = json.loads((REC / "MG-0926-RSA-EXECUTED.json").read_text(encoding="utf-8"))
NEW_ADS = sorted(n for n in rsa_rec["created_or_updated"] if "/adGroupAds/" in n)
OLD_ADS = {  # ad_group_id -> old RSA id (the 10 city RSAs live before 2026-09-26)
    "195877148086": "811758936855", "195877148126": "811758936858", "195877148286": "811758936861",
    "195877148326": "811758936864", "194944952537": "811758936867", "194944952577": "811758936870",
    "194944952617": "811758936873", "194944952777": "811758936876", "194944952817": "811758936879",
    "194944952857": "811758936882"}


def callout_links(c):
    out = []
    for r in q(c, f"""SELECT campaign.id, campaign_asset.resource_name, campaign_asset.status, asset.callout_asset.callout_text
                      FROM campaign_asset WHERE campaign.id IN ({LAND},{HARD}) AND campaign_asset.field_type = 'CALLOUT'"""):
        if r.asset.callout_asset.callout_text in NEW_CALLOUTS:
            out.append(r.campaign_asset.resource_name)
    return sorted(out)


BASE = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": GM_MANAGER}


def plans(c):
    return {
        "MG-0927-ENABLE": {**BASE, "package": "MG-0927-ENABLE", "enable": {"pmax_campaign": PMAX, "asset_group": AG,
                           "rsas": NEW_ADS, "callout_links": callout_links(c)},
                           "precondition": "readback MG-0926-READBACK-2026-09-27.json 27 PASS / 0 FAIL"},
        "MG-0927-OLD-PAUSE": {**BASE, "package": "MG-0927-OLD-PAUSE", "pause_old": OLD_ADS,
                              "gate": "pause an ad group's old RSA only when both new RSAs there are APPROVED or APPROVED_LIMITED"},
    }


def build(c, pkg, m):
    ops = []
    svc_ad = c.get_service("AdGroupAdService")
    if pkg == "MG-0927-ENABLE":
        o = c.get_type("MutateOperation")
        o.campaign_operation.update.resource_name = c.get_service("CampaignService").campaign_path(CID, PMAX)
        o.campaign_operation.update.status = c.enums.CampaignStatusEnum.ENABLED
        o.campaign_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
        ops.append(o)
        o = c.get_type("MutateOperation")
        o.asset_group_operation.update.resource_name = c.get_service("AssetGroupService").asset_group_path(CID, AG)
        o.asset_group_operation.update.status = c.enums.AssetGroupStatusEnum.ENABLED
        o.asset_group_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
        ops.append(o)
        for rn in m["enable"]["rsas"]:
            o = c.get_type("MutateOperation")
            o.ad_group_ad_operation.update.resource_name = rn
            o.ad_group_ad_operation.update.status = c.enums.AdGroupAdStatusEnum.ENABLED
            o.ad_group_ad_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
            ops.append(o)
        for rn in m["enable"]["callout_links"]:
            o = c.get_type("MutateOperation")
            o.campaign_asset_operation.update.resource_name = rn
            o.campaign_asset_operation.update.status = c.enums.AssetLinkStatusEnum.ENABLED
            o.campaign_asset_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
            ops.append(o)
        return ops, {}
    # OLD-PAUSE: gate on new-ad approval per ad group
    appr = {}
    for r in q(c, f"SELECT ad_group.id, ad_group_ad.resource_name, ad_group_ad.policy_summary.approval_status FROM ad_group_ad WHERE campaign.id IN ({LAND},{HARD})"):
        if r.ad_group_ad.resource_name in NEW_ADS:
            appr.setdefault(str(r.ad_group.id), []).append(E(r.ad_group_ad.policy_summary.approval_status))
    status = {}
    for ag, old in m["pause_old"].items():
        ok = len(appr.get(ag, [])) == 2 and all(s in ("APPROVED", "APPROVED_LIMITED") for s in appr[ag])
        status[ag] = "PAUSE" if ok else f"WAIT {appr.get(ag)}"
        if ok:
            o = c.get_type("MutateOperation")
            o.ad_group_ad_operation.update.resource_name = svc_ad.ad_group_ad_path(CID, ag, old)
            o.ad_group_ad_operation.update.status = c.enums.AdGroupAdStatusEnum.PAUSED
            o.ad_group_ad_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
            ops.append(o)
    return ops, status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["plan", "validate", "execute"])
    ap.add_argument("--pkg", choices=["MG-0927-ENABLE", "MG-0927-OLD-PAUSE"])
    ap.add_argument("--fp")
    a = ap.parse_args()
    c = client()
    row = q(c, "SELECT customer.id, customer.descriptive_name, customer.manager FROM customer")[0].customer
    if str(row.id) != CID or row.descriptive_name != EXACT_NAME or row.manager:
        sys.exit("IDENTITY GATE FAIL")
    P = plans(c)
    fps = {k: approval_code(v) for k, v in P.items()}
    if a.mode == "plan":
        for k, v in P.items():
            (PLANS / f"{k}.json").write_text(json.dumps(dict(v, fingerprint=fps[k]), indent=1), encoding="utf-8")
            print(f"PLAN {k:<18} {fps[k]}  ({len(v.get('enable', {}).get('rsas', [])) or len(v.get('pause_old', {}))} ads)")
        return
    k = a.pkg
    ops, status = build(c, k, P[k])
    rq = c.get_type("MutateGoogleAdsRequest")
    rq.customer_id = CID
    rq.mutate_operations.extend(ops)
    if a.mode == "validate":
        rq.validate_only = True
        if ops:
            c.get_service("GoogleAdsService").mutate(request=rq)
        print(f"VALIDATE {k} PASS {len(ops)} ops fp {fps[k]} {status or ''}")
        return
    if a.fp != fps[k]:
        sys.exit(f"ABORT fingerprint {fps[k]} != {a.fp}")
    if ops:
        c.get_service("GoogleAdsService").mutate(request=rq)
    rec = {"package": k, "fingerprint": fps[k], "executed_local": datetime.datetime.now(TZ).isoformat(),
           "ops": len(ops), "gate_status": status}
    (REC / f"{k}-EXECUTED-{datetime.datetime.now(TZ):%Y%m%dT%H%M}.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(f"EXECUTED {k}: {len(ops)} ops {status or ''}")


if __name__ == "__main__":
    main()
