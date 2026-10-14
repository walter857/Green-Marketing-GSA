#!/usr/bin/env python3
"""Post-GTM-P Google Ads invariant check + receipt.

GTM cannot mutate Google Ads, but GTM-P is the plan that feeds conversion action
7773043879, so prove that action and its campaign goal were NOT touched.
Read-only: zero mutate operations.
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, TZ, RECEIPTS, client, q, write, E  # noqa: E402

c = client()
fails = []


def chk(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' -> ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)


print("=" * 74 + "\nGOOGLE ADS INVARIANTS AFTER GTM-P\n" + "=" * 74)
convs = {}
for x in q(c, """SELECT conversion_action.id, conversion_action.name,
                        conversion_action.status, conversion_action.type,
                        conversion_action.category, conversion_action.origin,
                        conversion_action.primary_for_goal,
                        conversion_action.phone_call_duration_seconds
                 FROM conversion_action ORDER BY conversion_action.id"""):
    a = x.conversion_action
    convs[str(a.id)] = {"name": a.name, "status": E(a.status), "type": E(a.type_),
                        "category": E(a.category), "origin": E(a.origin),
                        "primary_for_goal": a.primary_for_goal,
                        "phone_call_duration_seconds": a.phone_call_duration_seconds}
    print(f"  {a.id} primary={str(a.primary_for_goal):<5} {E(a.type_):<13} {a.name}")

chk(len(convs) == 3, "conversion action count still 3, none duplicated", str(len(convs)))
chk(convs["7772803337"]["primary_for_goal"] is True, "7772803337 still PRIMARY")
chk(convs["7773013199"]["primary_for_goal"] is True, "7773013199 still PRIMARY")
chk(convs["7773043879"]["primary_for_goal"] is False, "7773043879 still SECONDARY")
chk(convs["7773043879"]["type"] == "WEBSITE_CALL", "7773043879 still WEBSITE_CALL")
chk(convs["7773043879"]["status"] == "ENABLED", "7773043879 still ENABLED")
chk(convs["7773043879"]["phone_call_duration_seconds"] == 60, "7773043879 still 60s")

goals = {}
for x in q(c, """SELECT campaign_conversion_goal.category, campaign_conversion_goal.origin,
                        campaign_conversion_goal.biddable FROM campaign_conversion_goal"""):
    g = x.campaign_conversion_goal
    goals[f"{E(g.category)}/{E(g.origin)}"] = g.biddable
for k, v in sorted(goals.items()):
    print(f"  goal {k:<32} biddable={v}")
chk(goals.get("PHONE_CALL_LEAD/WEBSITE") is False, "website-call goal still NON-biddable")
chk(goals.get("PHONE_CALL_LEAD/CALL_FROM_ADS") is True, "ad-call goal still biddable")
chk(goals.get("SUBMIT_LEAD_FORM/WEBSITE") is True, "form goal still biddable")

camps = [(str(x.campaign.id), E(x.campaign.status))
         for x in q(c, "SELECT campaign.id, campaign.status FROM campaign")]
print(f"  campaigns: {camps}")
chk(camps == [("24257151015", "PAUSED")], "campaign 24257151015 still PAUSED, still the only one")

n_call = len(q(c, "SELECT asset.id FROM asset WHERE asset.type = 'CALL'"))
chk(n_call == 0, "still 0 CALL assets (CALL-Q not executed)", str(n_call))
n_cust = len(q(c, "SELECT custom_conversion_goal.id FROM custom_conversion_goal"))
chk(n_cust == 0, "still 0 custom conversion goals", str(n_cust))

gtm = {
    "plan_id": "APG-0917-GTM-P", "fingerprint": "B3C69A1E65C8",
    "approval": "APPROVE APG GTM DELTA B3C69A1E65C8",
    "executed_local": datetime.datetime.now(TZ).isoformat(),
    "gtm_account_id": "6377231045", "gtm_container_id": "264326944",
    "gtm_container_public_id": "GTM-M545Z8T2", "gtm_workspace_id": "3",
    "gtm_workspace_name": "Apogee | PPC Tracking | 2026-09",
    "signed_in_as": "access@greenmarketingfl.com",
    "objects": [
        {"ordinal": 1, "type": "variable", "op": "update", "id": "4",
         "name": "DLV | lead_id",
         "change": "Set Default Value enabled, default value = empty string",
         "forced_deviation": None,
         "readback": {"variable_type": "Data Layer Variable",
                      "data_layer_variable_name": "lead_id",
                      "data_layer_version": "Version 2",
                      "set_default_value": True, "default_value": "",
                      "references": ["Google Ads | Lead | Permanent Lights Thank You (Tag)",
                                     "TR | Custom Event | apg_permanent_lights_lead (Trigger)"]}},
        {"ordinal": 2, "type": "trigger", "op": "update", "id": "5",
         "name": "TR | Custom Event | apg_permanent_lights_lead",
         "change": "ADD condition 3 only",
         "readback": {"trigger_type": "Custom Event",
                      "conditions": [
                          "Page Hostname equals offer.apogeelawns.com",
                          "Page Path matches RegEx ^/thank-you/permanent-christmas-lights/?$",
                          "DLV | lead_id matches RegEx .+"],
                      "folder": "Google Ads | Permanent Lights", "tags_referencing": 1}},
        {"ordinal": 3, "type": "trigger", "op": "create",
         "name": "TR | Page View | Permanent Lights LP",
         "readback": {"trigger_type": "Page View", "fires_on": "Some Page Views",
                      "conditions": [
                          "Page Hostname equals offer.apogeelawns.com",
                          "Page Path matches RegEx ^/permanent-christmas-lights-lincoln-ne/?$"],
                      "folder": "Google Ads | Permanent Lights",
                      "references": ["Google Ads | Call | Permanent Lights Website (Tag)"]}},
        {"ordinal": 4, "type": "tag", "op": "create",
         "name": "Google Ads | Call | Permanent Lights Website",
         "readback": {"tag_type": "Google Ads Calls from Website Conversion",
                      "displayed_phone_number_to_replace": "402-526-5754",
                      "conversion_id": "18453077620",
                      "conversion_label": "lp3jCKf5vPocEPS8jt9E",
                      "gtm_validation": "Google tag found in this container",
                      "firing_trigger": "TR | Page View | Permanent Lights LP",
                      "folder": "Google Ads | Permanent Lights"},
         "published": False}],
    "workspace_changes_before": 5,
    "workspace_changes_after": 7,
    "pending_changes_breakdown": {"modified": 0, "added": 7, "deleted": 0},
    "container_versions_created": 0,
    "container_publishes": 0,
    "submit_used": False,
    "live_container": "Empty Container is Live - 0 Tags, 0 Triggers, 0 Variables",
    "only_existing_version": "Version 1 'Empty Container' 09/16/2026 (container's own initial version)",
    "publication_gate": "BLOCKED - WhatConverts number replacement active on offer.apogeelawns.com",
    "google_ads_conversion_actions_after": convs,
    "campaign_conversion_goals_after": goals,
    "campaigns_after": camps,
    "call_assets_after": n_call,
    "qa_failures": len(fails),
    "failed_checks": fails,
}
write(RECEIPTS / "2026-09-17-gtmp-receipt.json", gtm)

print("\n" + "=" * 74)
print(f"GTM-P RESULT: {len(fails)} Google Ads invariant failures")
print("Receipt: receipts/2026-09-17-gtmp-receipt.json")
print("=" * 74)
sys.exit(1 if fails else 0)
