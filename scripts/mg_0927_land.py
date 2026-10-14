#!/usr/bin/env python3
"""MasterGrass - Live | 2026-09-27 | MG-0927-LAND: Landscaping Search - BOFU bid + budget.

Owner instruction 2026-09-27: switch Landscaping from Maximize Conversions to Maximize Clicks with a
$25 CPC cap ("im fine with that") and set "the budget you consider the best"; goal is $1,500 spend
per month.

Budget math (monthly cap = daily x 30.4):
  PMax drainage   $20.00 -> $608 / month (spends its budget reliably once enabled)
  Hardscaping     $13.00 -> up to $395, but on Maximize Conversions it has spent $0 since 09-23
  Landscaping     $28.00 -> $851 / month; ~75 impressions per weekday since the 09-23 keywords,
                  ~3 clicks x ~$18-22 under a $25 cap = ~$55-65 of demand per weekday, so $28/day
                  (Google may spend 2x on a weekday) is the level that fills ~$850 without over-running
  Expected month  ~$1,460-1,550 = the $1,500 goal. Keeping $132 would allow up to $4,013 / month.

Modes: plan | validate | execute --fp CODE | readback
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
from gm_gsa.safety import approval_code  # noqa: E402

LAND, BUDGET = "23905193676", "15630863938"
CAP, BUDGET_TO, BUDGET_FROM = 25.00, 28.00, 132.00
REC = ROOT / "clients" / "mastergrass-lawn-care" / "receipts"
PLAN = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": GM_MANAGER,
        "package": "MG-0927-LAND", "campaign": LAND, "bidding": {"from": "MAXIMIZE_CONVERSIONS", "to": "TARGET_SPEND (Maximize Clicks)",
        "cpc_bid_ceiling": CAP}, "budget": {"id": BUDGET, "from": BUDGET_FROM, "to": BUDGET_TO},
        "approval_basis": "owner chat 2026-09-27: Max Clicks $25 cap approved; budget delegated inside a $1,500/month goal",
        "rollback": {"bidding": "MAXIMIZE_CONVERSIONS (no tCPA)", "budget": BUDGET_FROM}}


def ops(c):
    co = c.get_type("CampaignOperation")
    co.update.resource_name = c.get_service("CampaignService").campaign_path(CID, LAND)
    co.update.target_spend.cpc_bid_ceiling_micros = int(CAP * 1e6)
    co.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["target_spend.cpc_bid_ceiling_micros"]))
    bo = c.get_type("CampaignBudgetOperation")
    bo.update.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(CID, BUDGET)
    bo.update.amount_micros = int(BUDGET_TO * 1e6)
    bo.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["amount_micros"]))
    return co, bo


def state(c):
    r = q(c, f"""SELECT campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros, campaign.status,
                    campaign_budget.amount_micros FROM campaign WHERE campaign.id = {LAND}""")[0]
    return E(r.campaign.bidding_strategy_type), r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6, E(r.campaign.status), r.campaign_budget.amount_micros / 1e6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["plan", "validate", "execute", "readback"])
    ap.add_argument("--fp")
    a = ap.parse_args()
    fp = approval_code(PLAN)
    c = client()
    row = q(c, "SELECT customer.id, customer.descriptive_name, customer.manager FROM customer")[0].customer
    if str(row.id) != CID or row.descriptive_name != EXACT_NAME or row.manager:
        sys.exit("IDENTITY GATE FAIL")
    if a.mode == "plan":
        (PLANS / "MG-0927-LAND.json").write_text(json.dumps(dict(PLAN, fingerprint=fp), indent=1), encoding="utf-8")
        print("PLAN MG-0927-LAND", fp, "| before:", state(c))
        return
    if a.mode == "readback":
        s = state(c)
        ok = s == ("TARGET_SPEND", CAP, "ENABLED", BUDGET_TO)
        print(f"[{'PASS' if ok else 'FAIL'}] Landscaping {s}")
        return
    co, bo = ops(c)
    before = state(c)
    if a.mode == "validate":
        for svc, fn, o in ((c.get_service("CampaignService"), "mutate_campaigns", co),
                           (c.get_service("CampaignBudgetService"), "mutate_campaign_budgets", bo)):
            rq = c.get_type("MutateCampaignsRequest" if fn == "mutate_campaigns" else "MutateCampaignBudgetsRequest")
            rq.customer_id = CID
            rq.operations.append(o)
            rq.validate_only = True
            getattr(svc, fn)(request=rq)
        print("VALIDATE MG-0927-LAND PASS", fp, "| before:", before)
        return
    if a.fp != fp:
        sys.exit(f"ABORT fingerprint {fp} != {a.fp}")
    if before[0] != "MAXIMIZE_CONVERSIONS" or before[3] != BUDGET_FROM:
        sys.exit(f"ABORT drift: {before}")
    c.get_service("CampaignService").mutate_campaigns(customer_id=CID, operations=[co])
    c.get_service("CampaignBudgetService").mutate_campaign_budgets(customer_id=CID, operations=[bo])
    after = state(c)
    rec = {"package": "MG-0927-LAND", "fingerprint": fp, "executed_local": datetime.datetime.now(TZ).isoformat(),
           "before": before, "after": after}
    (REC / "MG-0927-LAND-EXECUTED.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("EXECUTED MG-0927-LAND", before, "->", after)


if __name__ == "__main__":
    main()
