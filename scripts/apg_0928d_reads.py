#!/usr/bin/env python3
"""2026-09-28 (run D) READ-ONLY checks for recording owner answers: identity, campaign status, tablet rows,
the three labor-only negatives, conversion actions, and the WhatConverts number -> call-flow assignment
(allowlisted business fields only). Nothing mutates."""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, EXACT_NAME, GM_MANAGER, E, ROOT, client, q, write  # noqa: E402
from gm_gsa.whatconverts import BASE, _auth  # noqa: E402

c = client()
R = {"run_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
mgr = q(c, f"SELECT customer_client.id, customer_client.descriptive_name FROM customer_client "
           f"WHERE customer_client.id = {CID}", cid=GM_MANAGER)
cu = q(c, "SELECT customer.id, customer.descriptive_name, customer.manager, customer.test_account, customer.time_zone FROM customer")[0].customer
R["identity_pass"] = (str(cu.id) == CID and cu.descriptive_name == EXACT_NAME and not cu.manager and not cu.test_account
                      and len(mgr) == 1 and mgr[0].customer_client.descriptive_name == EXACT_NAME)
print(f"IDENTITY {'PASS' if R['identity_pass'] else 'FAIL'}: {cu.id} '{cu.descriptive_name}' manager={cu.manager} test={cu.test_account} tz={cu.time_zone}")
if not R["identity_pass"]:
    sys.exit("HARD STOP")
cp = q(c, "SELECT campaign.status, campaign.serving_status, campaign.target_spend.cpc_bid_ceiling_micros, "
          "campaign_budget.amount_micros FROM campaign WHERE campaign.id = 24257151015")[0]
R["campaign"] = {"status": E(cp.campaign.status), "serving": E(cp.campaign.serving_status),
                 "cap": cp.campaign.target_spend.cpc_bid_ceiling_micros / 1e6, "budget": cp.campaign_budget.amount_micros / 1e6}
print("CAMPAIGN", R["campaign"])
tab = []
for r in q(c, "SELECT campaign_criterion.resource_name, campaign_criterion.bid_modifier FROM campaign_criterion "
              "WHERE campaign_criterion.type = 'DEVICE' AND campaign_criterion.device.type = 'TABLET'"):
    tab.append({"res": r.campaign_criterion.resource_name, "set": r.campaign_criterion._pb.HasField("bid_modifier"),
                "value": r.campaign_criterion.bid_modifier})
for r in q(c, "SELECT ad_group_bid_modifier.resource_name, ad_group_bid_modifier.bid_modifier FROM ad_group_bid_modifier "
              "WHERE ad_group_bid_modifier.device.type = 'TABLET'"):
    tab.append({"res": r.ad_group_bid_modifier.resource_name, "set": r.ad_group_bid_modifier._pb.HasField("bid_modifier"),
                "value": r.ad_group_bid_modifier.bid_modifier})
R["tablet"] = tab
print("TABLET", tab)
negs = []
for r in q(c, "SELECT campaign.id, campaign_criterion.resource_name, campaign_criterion.criterion_id, campaign_criterion.status, "
              "campaign_criterion.keyword.text, campaign_criterion.keyword.match_type FROM campaign_criterion "
              "WHERE campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE"):
    k = r.campaign_criterion
    negs.append({"campaign_id": str(r.campaign.id), "res": k.resource_name, "id": str(k.criterion_id),
                 "status": E(k.status), "text": k.keyword.text, "mt": E(k.keyword.match_type)})
R["negative_count"] = len(negs)
R["labor_only_negatives"] = [n for n in negs if n["text"] in ("labor only", "customer supplied", "my own lights")]
R["all_negatives"] = negs
print("NEGATIVES total", len(negs))
for n in R["labor_only_negatives"]:
    print("  ", n)
R["conversion_actions"] = [{"id": str(r.conversion_action.id), "type": E(r.conversion_action.type_),
                            "primary": r.conversion_action.primary_for_goal,
                            "duration": r.conversion_action.phone_call_duration_seconds}
                           for r in q(c, "SELECT conversion_action.id, conversion_action.type, conversion_action.primary_for_goal, "
                                         "conversion_action.phone_call_duration_seconds FROM conversion_action")]
print("CONV", R["conversion_actions"])

KEEP = ("phone_number_id", "phone_name", "tracking_number", "swap_number", "call_flow", "trigger", "source", "medium",
        "last_used", "call_recording", "voice", "messaging", "pending_activation", "profile_id")
r = requests.get(f"{BASE}/tracking/numbers", auth=_auth(), timeout=60,
                 params={"account_id": "119788", "profile_id": "174313", "numbers_per_page": 250})
R["wc_numbers_http"] = r.status_code
R["wc_numbers"] = [{k: n.get(k) for k in KEEP} for n in (r.json().get("numbers", []) if r.ok else [])
                   if str(n.get("profile_id")) == "174313"]
paid = [n for n in R["wc_numbers"] if str(n["tracking_number"]).endswith("4025265754")]
print("WC tracking/numbers HTTP", r.status_code, "| paid number record:", json.dumps(paid))
write(EVID / "2026-09-28d-reads.json", R)
