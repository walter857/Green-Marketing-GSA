#!/usr/bin/env python3
"""Ambient | 2026-10-05 | READ-ONLY phone-path verification for the four reported numbers.

WhatConverts: GET /tracking/numbers and /tracking/forms for account 115814 / profile 105803 (configuration only:
business numbers, no caller data). Leads are never printed here; lead-level matching comes from
snapshots/cpl-reconciliation-2026-10-01.json (built by ambient_0930_cpl_reconcile.py, contact fields hashed).
Google Ads: call-asset links per heating campaign, customer call-reporting settings, location asset set, and
call_view rows for the in-scope campaigns. No mutations. Writes snapshots/phone-paths-2026-10-05.json.
"""
from __future__ import annotations
import sys, json, collections
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, SNAP, ROOT  # noqa: E402
from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.whatconverts import BASE, _auth  # noqa: E402

load_dotenv_if_available(ROOT / ".env")
ACC, PROF = "115814", "105803"
FOUR = {"4102164650": "paid Maps / location-asset override (Severn + Annapolis, 09-24)", "4107056354": "paid landing-page base number", "4109141456": "website DNI", "4104159517": "heating call-asset number",
        "4107610932": "final forwarding destination"}
NUM_FIELDS = ("phone_number_id", "phone_name", "tracking_number", "destination_number", "swap_number", "call_flow", "trigger",
              "source", "medium", "last_used", "call_recording", "pending_activation", "profile_id")
out = {"whatconverts_numbers": [], "whatconverts_forms": []}
r = requests.get(f"{BASE}/tracking/numbers", auth=_auth(), timeout=60, params={"account_id": ACC, "profile_id": PROF, "numbers_per_page": 250})
print("WC tracking/numbers HTTP", r.status_code)
if r.ok:
    for n in r.json().get("numbers", r.json().get("phone_numbers", [])):
        if str(n.get("profile_id")) == PROF:
            out["whatconverts_numbers"].append({k: n.get(k) for k in NUM_FIELDS})
digits = lambda s: "".join(ch for ch in str(s or "") if ch.isdigit())[-10:]
for n in out["whatconverts_numbers"]:
    tn = digits(n["tracking_number"])
    flag = FOUR.get(tn, "")
    print(f"  {tn} -> dest {digits(n['destination_number'])} swap={digits(n['swap_number']) or '-'} name={n['phone_name']!r} "
          f"src={n['source']}/{n['medium']} trigger={n['trigger']} last_used={n['last_used']} {('<< ' + flag) if flag else ''}")
r = requests.get(f"{BASE}/tracking/forms", auth=_auth(), timeout=60, params={"account_id": ACC, "profile_id": PROF, "forms_per_page": 250})
print("WC tracking/forms HTTP", r.status_code)
if r.ok:
    for f in r.json().get("forms", []):
        if str(f.get("profile_id")) == PROF:
            row = {k: f.get(k) for k in ("form_id", "form_name", "attribute_type", "attribute_type_value", "submit_attribute_type", "submit_attribute_type_value")}
            out["whatconverts_forms"].append(row)
            print("  FORM", json.dumps(row))

c = client()
identity_gate(c, verbose=False)
HEAT = "24257819463,24257819466,24132507744,24268690038,24268690041,24279798229,24274160783"
for x in q(c, "SELECT customer.call_reporting_setting.call_reporting_enabled, customer.call_reporting_setting.call_conversion_reporting_enabled, customer.call_reporting_setting.call_conversion_action FROM customer"):
    s = x.customer.call_reporting_setting
    out["call_reporting"] = dict(enabled=s.call_reporting_enabled, conversion_reporting=s.call_conversion_reporting_enabled, action=s.call_conversion_action)
print("call reporting:", out["call_reporting"])
links = []
for x in q(c, f"""SELECT campaign.id, campaign_asset.status, asset.id, asset.call_asset.phone_number, asset.call_asset.call_conversion_reporting_state,
        asset.call_asset.call_conversion_action FROM campaign_asset WHERE campaign.id IN ({HEAT}) AND campaign_asset.field_type = 'CALL' AND campaign_asset.status != 'REMOVED'"""):
    links.append(dict(campaign=str(x.campaign.id), status=E(x.campaign_asset.status), asset=str(x.asset.id), number=digits(x.asset.call_asset.phone_number),
                      reporting=E(x.asset.call_asset.call_conversion_reporting_state)))
out["call_asset_links"] = links
print("call-asset links (campaign, number, status):", sorted((l["campaign"], l["number"], l["status"]) for l in links))
cv = []
for x in q(c, f"""SELECT call_view.start_call_date_time, call_view.call_duration_seconds, call_view.call_status, call_view.type, call_view.caller_area_code,
        campaign.id, ad_group.id FROM call_view WHERE call_view.start_call_date_time >= '2026-08-14 00:00:00'"""):
    cv.append(dict(start=x.call_view.start_call_date_time, dur=x.call_view.call_duration_seconds, status=E(x.call_view.call_status),
                   type=E(x.call_view.type), campaign=str(x.campaign.id), ad_group=str(x.ad_group.id)))
out["call_view_since_0814"] = cv
print("call_view since 08-14:", [(v["start"], v["dur"], v["status"], v["type"], v["campaign"], v["ad_group"]) for v in cv])
(SNAP / "phone-paths-2026-10-05.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
