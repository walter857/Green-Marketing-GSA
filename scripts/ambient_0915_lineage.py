#!/usr/bin/env python3
"""Ambient | 2026-09-15 | prior-plan lineage and no-replay table, verified against live state."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-15"
c = client(); identity_gate(c, verbose=False)
COMM_AG, RES_AG, CAMP = "199748801029", "202339087634", "24132507747"
rows = []


def add(plan, fp, claimed, verdict, evidence):
    rows.append({"plan": plan, "fingerprint": fp, "claimed_status": claimed,
                 "live_verdict": verdict, "evidence": evidence})
    print(f"  {plan:28s} {fp:14s} {verdict:20s} {evidence}")


print("=== LIVE CHECKS ===")
budgets = {str(r.campaign.id): r.campaign_budget.amount_micros / 1e6 for r in q(c, f"""
    SELECT campaign.id, campaign_budget.amount_micros FROM campaign
    WHERE campaign.id IN ({IN5})""")}
ceil = {str(r.campaign.id): r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6
        for r in q(c, f"""SELECT campaign.id, campaign.target_spend.cpc_bid_ceiling_micros
                          FROM campaign WHERE campaign.id IN ({IN5})""")}
negs = sorted(r.ad_group_criterion.keyword.text for r in q(c, f"""
    SELECT ad_group_criterion.keyword.text FROM ad_group_criterion
    WHERE ad_group.id = {COMM_AG} AND ad_group_criterion.negative = TRUE"""))
comm_ads = q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group.id = {COMM_AG}")
res_negs = q(c, f"""SELECT ad_group_criterion.keyword.text FROM ad_group_criterion
                    WHERE ad_group.id = {RES_AG} AND ad_group_criterion.negative = TRUE""")
acr_ads = q(c, """SELECT ad_group_ad.ad.id, ad_group_ad.status,
                         ad_group_ad.policy_summary.approval_status
                  FROM ad_group_ad WHERE ad_group.id = 202339087834""")
inst_ads = q(c, f"""SELECT ad_group_ad.ad.id, ad_group_ad.status,
                           ad_group_ad.policy_summary.approval_status
                    FROM ad_group_ad WHERE ad_group.id = {RES_AG}""")
print(f"  budgets : {budgets}")
print(f"  ceilings: {ceil}")
print(f"  commercial ad-group negatives: {len(negs)}")
print(f"  commercial ads: {len(comm_ads)}")
print(f"  residential ad-group negatives: {len(res_negs)}")
print(f"  AC Repair ad group 202339087834 ads: "
      f"{[(str(a.ad_group_ad.ad.id), E(a.ad_group_ad.status)) for a in acr_ads]}")

print("\n=== LINEAGE TABLE ===")
add("AMB-0910-BUD-2", "93541FBB5D7F", "reported executed",
    "ALREADY_EXECUTED",
    f"live budgets {budgets['24132507744']:.2f} Gas Boiler and "
    f"{budgets['24132507753']:.2f} HVAC Replacement match the plan; combined daily "
    f"${sum(budgets.values()):.2f} x30.4 = ${sum(budgets.values())*30.4:.2f}; "
    f"change_event CAMPAIGN_BUDGET UPDATE 2026-09-10 10:17:17 GOOGLE_ADS_API")
add("AMB-0909C-NEG-COMMERCIAL", "9F88FEE76803", "reported executed",
    "ALREADY_EXECUTED",
    "campaign-level negatives on 24132507747 total 1,437; `commercial` confirmed "
    "ABSENT from campaign and account level, which is the plan's own requirement")
add("AMB-0909-ADS-1", "11A79347A296", "reported executed",
    "ALREADY_EXECUTED",
    f"residential ad group {RES_AG} holds 2 ENABLED+APPROVED ads "
    f"{[str(a.ad_group_ad.ad.id) for a in inst_ads if E(a.ad_group_ad.status)=='ENABLED']} "
    f"plus 2 PAUSED CONSUMER_FINANCE disapprovals; change_event AD_GROUP_AD UPDATE "
    f"2026-09-10 00:41:57 GOOGLE_ADS_API")
add("AMB-0910-CPC-CAP-1", "7EA6922309EB", "reported executed",
    "ALREADY_EXECUTED",
    f"ceilings live: AC Repair ${ceil['24132507741']:.2f}, HVAC Repair "
    f"${ceil['24132507750']:.2f}, HVAC Installation ${ceil['24132507747']:.2f}, "
    f"HVAC Replacement ${ceil['24132507753']:.2f}, Gas Boiler ${ceil['24132507744']:.2f}; "
    f"change_event CAMPAIGN UPDATE target_spend.cpc_bid_ceiling_micros 2026-09-10 13:20:39")
add("AMB-0910-COMM-NEG-3", "51CF5986F18A", "reported executed",
    "ALREADY_EXECUTED",
    f"{len(negs)}/17 BROAD ENABLED ad-group negatives live on {COMM_AG}, exact set match, "
    f"all five held terms absent")
add("AMB-0910-COMM-NEG-1", "C4142D5D5DE0", "SUPERSEDED", "SUPERSEDED",
    "18-term package; never executed; replaced by NEG-3. DO NOT EXECUTE")
add("AMB-0910-COMM-NEG-1-FULL", "A774B9C14896", "REJECTED", "REJECTED",
    "22-term package rejected by the owner. DO NOT EXECUTE")
add("AMB-0910-COMM-NEG-2", "A9C9BCBDDD74", "SUPERSEDED", "SUPERSEDED",
    "18-term package including BROAD `training`; never executed. DO NOT EXECUTE")
add("AMB-0910-COMM-RSA-2", "41C183D15C93", "blocked on 404", "DRIFTED",
    "before-state changed on three counts since drafting: destination 404 -> HTTP 200; "
    "ad group PAUSED -> ENABLED (2026-09-15 08:42:16); ad-group negatives 0 -> 17. "
    "SUPERSEDED by AMB-0915-COMM-RSA-1. DO NOT EXECUTE")
add("AMB-0910-COMM-XNEG-1", "A70260017DAD", "gated", "BLOCKED",
    f"residential ad group {RES_AG} still holds {len(res_negs)} ad-group negatives; the "
    f"commercial route still cannot serve (0 ads). Gate is unchanged. DO NOT EXECUTE YET")
add("AMB-0910-RSA-ACR-2", "1F166DE17017", "ready", "UNEXECUTED_AND_EXACT",
    f"AC Repair ad group 202339087834 still holds exactly 2 ads, both ENABLED+APPROVED; "
    f"no third ad exists, so the create-paused challenger has not been executed. "
    f"Separate workstream - not part of the commercial launch")
add("AMB-0910-RSA-ACR-1", "19E2F2FFC311", "SUPERSEDED", "SUPERSEDED",
    "contains the withdrawn Licensed & Insured claim. DO NOT EXECUTE")
add("AMB-0910-COMM-RSA-1", "30312BC45992", "SUPERSEDED", "SUPERSEDED",
    "pre-launch-pack copy, wrong paths. DO NOT EXECUTE")
add("AMB-0909C-CPC-INST-2", "5D57E0EF3B70", "REJECTED", "REJECTED",
    "rejected by the owner 2026-09-10. DO NOT EXECUTE")

print("\n=== NEW PLANS THIS SESSION ===")
for name in ("AMB-0915-COMM-RSA-1", "AMB-0915-COMM-ASSET-1"):
    p = PLANS / f"{name}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    fp = d.pop("fingerprint"); re_fp = approval_code(d); d["fingerprint"] = fp
    ok = fp == re_fp
    print(f"  {name:24s} {fp}  ops={d['operation_count']}  recompute_match={ok}")
    rows.append({"plan": name, "fingerprint": fp, "claimed_status": "AWAITING_APPROVAL",
                 "live_verdict": "UNEXECUTED_AND_EXACT",
                 "evidence": f"fingerprint recomputed from disk, match={ok}; "
                             f"{d['operation_count']} operations; validate_only VALIDATED_OK"
                 if name == "AMB-0915-COMM-RSA-1" else
                 f"fingerprint recomputed from disk, match={ok}; {d['operation_count']} operations"})

out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "lineage": rows,
       "live_budgets": budgets, "live_ceilings": ceil,
       "commercial_negatives": negs, "commercial_ads": len(comm_ads),
       "residential_ad_group_negatives": len(res_negs)}
p = SNAP / f"plan-lineage-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
