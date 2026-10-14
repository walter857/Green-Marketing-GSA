#!/usr/bin/env python3
"""Ambient | 2026-09-30e | Plan AMB-0930-REPAIR-CPC-2 (supersedes REPAIR-CPC-1 / CB667F2D4610, $21): lower the Maximize Clicks CPC ceiling of campaign 24257819463.

    python ambient_0930d_repair_cpc_plan.py plan
    python ambient_0930d_repair_cpc_plan.py execute --fp <FP>      # ONLY after explicit approval of this fingerprint

One operation: campaign.target_spend.cpc_bid_ceiling_micros 42,000,000 -> 18,000,000. Nothing else changes: the
unrelated-resource baseline (all campaigns' status/bidding/ceiling/budget; this campaign's networks, criteria, asset links,
shared sets; every repair ad group's status, ads and keywords) is hashed into the fingerprint and compared after execution.
No ad group is paused. The hashed payload is rebuilt from fresh state at execution; any drift changes the fingerprint.
"""
from __future__ import annotations
import sys, json, argparse, datetime, copy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS, CLIENT_DIR, ROOT  # noqa: E402
from ambient_0930_cpl_contain_plans import baseline  # read-only baseline builder (same account-wide + campaign scope)  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets, assert_target_matches  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402
import yaml  # noqa: E402

PLAN = "AMB-0930-REPAIR-CPC-2"
CAMP = "24257819463"
FROM, TO = 42_000_000, 18_000_000
WO = CLIENT_DIR / "work-orders" / "work-order-heating-repair-cpc-ceiling-2026-09-30.yaml"


def build(c):
    r = q(c, f"""SELECT campaign.id, campaign.name, campaign.status, campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros,
            campaign_budget.id, campaign_budget.amount_micros, campaign.network_settings.target_search_network,
            campaign.network_settings.target_content_network FROM campaign WHERE campaign.id = {CAMP}""")[0]
    base = baseline(c)
    errs = []
    if E(r.campaign.bidding_strategy_type) != "TARGET_SPEND": errs.append("bidding is not Maximize Clicks (TARGET_SPEND)")
    if r.campaign.target_spend.cpc_bid_ceiling_micros != FROM: errs.append(f"ceiling drift {r.campaign.target_spend.cpc_bid_ceiling_micros}")
    if E(r.campaign.status) != "ENABLED": errs.append("campaign not ENABLED")
    enabled_groups = sorted(g for g, v in base["repair_groups"].items() if v["status"] == "ENABLED")
    plan = {
        "plan": PLAN, "target": {"child_customer_id": CID, "exact_child_account_name": EXACT_NAME},
        "work_order": str(WO.relative_to(ROOT)).replace("\\", "/"),
        "approval_type": "EXPLICIT APPROVAL (bid ceiling only)",
        "supersedes": {"plan": "AMB-0930-REPAIR-CPC-1", "fingerprint": "CB667F2D4610", "why": "v23 forecast with impressions, negatives and the live 75 locations: $18 keeps ~95% of $21 clicks on the highest-intent furnace keywords; the $18->$21 increment is mostly NEAR_PHRASE traffic from the heating repair phrase keyword"},
        "preconditions": {"campaign": {"id": CAMP, "name": r.campaign.name, "status": E(r.campaign.status),
                                       "bidding": E(r.campaign.bidding_strategy_type), "ceiling_micros": r.campaign.target_spend.cpc_bid_ceiling_micros,
                                       "budget_id": str(r.campaign_budget.id), "budget_micros": r.campaign_budget.amount_micros,
                                       "search_partners": r.campaign.network_settings.target_search_network,
                                       "display": r.campaign.network_settings.target_content_network},
                          "enabled_repair_ad_groups": enabled_groups},
        "operations": [{"op": "UPDATE", "resource": "campaign", "id": CAMP, "field": "target_spend.cpc_bid_ceiling_micros",
                        "from": FROM, "to": TO}],
        "unchanged": ["every repair ad group stays ENABLED (none paused)", "keywords and Phrase/Exact match types", "ads and landing pages",
                      "budget $85/day", "locations", "schedule", "negative lists", "conversion goals", "Search-only networks"],
        "unrelated_resource_baseline": base,
        "readback_assertions": [f"campaign {CAMP} target_spend.cpc_bid_ceiling_micros == {TO}",
                                "every other baseline value identical after execution"],
        "evaluation": "No automatic restart or reversal. Judge on complete days against the full history: a before/after comparison on "
                      "the same weekdays, reconciled genuine paid leads, CPL bands ($280 target / $350 ceiling), clicks, impression share "
                      "lost to rank and budget. Any further bid, budget or status change needs its own exact approval.",
        "rollback": "Restoring $42 (or trying $21) is a separate single-field plan requiring its own approval.",
    }
    return plan, errs


def expected_after(b0):
    b = copy.deepcopy(b0)
    b["campaigns"][CAMP][2] = TO
    return b


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["plan", "execute"]); ap.add_argument("--fp"); a = ap.parse_args()
    c = client(); ident = identity_gate(c, verbose=True)
    cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
    e = validate_work_order(yaml.safe_load(WO.read_text(encoding="utf-8")), cl)
    if e: sys.exit(f"work order invalid: {e}")
    plan, errs = build(c)
    assert_no_embedded_secrets(plan); assert_target_matches(plan, cl, observed_account_name=ident["descriptive_name"])
    fp = approval_code(plan)
    m = c.get_type("MutateOperation"); u = m.campaign_operation.update
    u.resource_name = c.get_service("CampaignService").campaign_path(CID, CAMP); u.target_spend.cpc_bid_ceiling_micros = TO
    m.campaign_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["target_spend.cpc_bid_ceiling_micros"]))
    rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.mutate_operations.append(m)
    if a.cmd == "plan":
        rq.validate_only = True
        try:
            c.get_service("GoogleAdsService").mutate(request=rq); vo = "VALIDATE_OK"
        except Exception as ex:  # noqa: BLE001
            vo = "VALIDATE_FAIL " + str(ex)[-300:]; errs.append(vo)
        doc = dict(plan, fingerprint=fp, operation_count=1, validate_only=vo, errors=errs, generated_local=datetime.datetime.now(TZ).isoformat())
        (PLANS / f"{PLAN}.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
        print(f"PLAN {PLAN} {fp} ops=1 {vo} errors={errs}")
        return
    if a.fp != fp or errs:
        sys.exit(f"ABORT: fingerprint {fp} != {a.fp} or errors {errs}")
    rec = {"plan": PLAN, "fingerprint": fp, "started_local": datetime.datetime.now(TZ).isoformat()}
    out = RECEIPTS / f"{PLAN}-EXECUTED.json"
    try:
        resp = c.get_service("GoogleAdsService").mutate(request=rq)
    except Exception as ex:  # noqa: BLE001
        rec["error"] = str(ex)[:1500]; out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        sys.exit(f"STOP: mutate failed, nothing applied: {str(ex)[:400]}")
    rec["results"] = [str(x) for x in resp.mutate_operation_responses]
    after, want = baseline(c), expected_after(plan["unrelated_resource_baseline"])
    fails = [] if after == want else ["drift: " + json.dumps({k: [after[k], want[k]] for k in want if after[k] != want[k]})[:1500]]
    rec.update(readback_fail=len(fails), readback_fails=fails, finished_local=datetime.datetime.now(TZ).isoformat())
    out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(f"{PLAN} EXECUTED; readback {'PASS' if not fails else fails}")


if __name__ == "__main__":
    main()
