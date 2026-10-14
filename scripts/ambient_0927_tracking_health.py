#!/usr/bin/env python3
"""Ambient | 2026-09-27 | READ-ONLY tracking & attribution health check for the heating landing pages.

1. Cache state: clean headless loads (NO query parameters, so nothing is seeded) of every heating offer
   page. Reports x-proxy-cache and how many server-rendered attribution hidden fields carry a value
   (non-empty on a clean load = another visitor's values being replayed).
2. Where WhatConverts' lead-level click ID comes from: for 2026 form leads, compare lead gclid presence
   with the form's own hidden gclid field (booleans only; no PII printed).
3. Google Ads import health: offline_conversion_upload_conversion_action_summary for WC Lead / WC Calls.
4. Conversion goals: account + campaign-level biddable goals on the heating campaigns.
"""
from __future__ import annotations
import sys, json, re, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ambient_0909_lib import client, q, identity_gate, E, CLIENT_DIR, SNAP
from gm_gsa.config import load_dotenv_if_available
from gm_gsa.whatconverts import fetch_leads
from playwright.sync_api import sync_playwright

PAGES = ["no-heat-repair", "furnace-repair", "hvac-repair", "hvac-replacement", "hvac-installation", "gas-boiler-repair",
         "heat-pump-repair", "heat-pump-replacement", "heat-pump-installation", "boiler-replacement", "thermostat-repair",
         "thermostat-replacement", "smart-thermostat"]
out = {}

# 1. cache state
print("1) CLEAN LOADS (no parameters) - server HTML before JavaScript")
res = []
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(locale="en-US", viewport={"width": 390, "height": 844})
    pg = ctx.new_page()
    for p in PAGES:
        r = pg.goto(f"https://offer.ambientcoolingandheating.com/{p}/", wait_until="domcontentloaded", timeout=60000)
        html = r.text() if r else ""
        hdr = (r.headers.get("x-proxy-cache") if r else None)
        vals = re.findall(r'<input[^>]+id=[\'"]input_\d+_(?:9|1\d|2\d)[\'"][^>]*>', html)
        filled = sum(1 for v in vals if re.search(r'value=[\'"][^\'"]+[\'"]', v))
        res.append((p, r.status if r else None, hdr, len(vals), filled))
        print(f"   {p:24s} HTTP {r.status if r else '-'} cache={hdr} attribution fields={len(vals)} carrying a value={filled}")
    b.close()
out["cache"] = res

# 2. WhatConverts click-id source
load_dotenv_if_available(Path(__file__).resolve().parents[1] / ".env")
leads = []
for a, z in (("2026-01-01", "2026-06-30"), ("2026-07-01", "2026-09-27")):
    leads += fetch_leads("115814", "105803", a, z, client_yaml=CLIENT_DIR / "client.yaml")["leads"]
cmp = collections.Counter()
for l in leads:
    if l.get("lead_type") != "Web Form": continue
    blob = json.dumps(l.get("additional_fields") or {}) + json.dumps(l.get("custom_fields") or {}) + json.dumps(l.get("mapped_fields") or {})
    hid = re.search(r'gclid[^"]*"\s*:\s*"([^"]+)"', blob, re.I)
    lead_g = l.get("gclid") or ""
    key = ("lead has gclid" if lead_g else "lead no gclid",
           "form field has gclid" if hid else "form field empty/absent",
           "SAME" if (hid and lead_g and hid.group(1) == lead_g) else ("DIFFERENT" if (hid and lead_g) else "-"))
    cmp[key] += 1
print("\n2) 2026 WEB-FORM LEADS: WhatConverts gclid vs the form's hidden gclid field:", dict(cmp))
out["wc_gclid_source"] = {"|".join(k): v for k, v in cmp.items()}

# 3. import health
c = client(); identity_gate(c, verbose=False)
print("\n3) GOOGLE ADS IMPORT HEALTH (offline conversion upload summaries)")
try:
    for r in q(c, """SELECT offline_conversion_upload_conversion_action_summary.conversion_action_name,
            offline_conversion_upload_conversion_action_summary.status, offline_conversion_upload_conversion_action_summary.total_event_count,
            offline_conversion_upload_conversion_action_summary.successful_event_count, offline_conversion_upload_conversion_action_summary.pending_event_count,
            offline_conversion_upload_conversion_action_summary.last_upload_date_time, offline_conversion_upload_conversion_action_summary.alerts,
            offline_conversion_upload_conversion_action_summary.daily_summaries
            FROM offline_conversion_upload_conversion_action_summary"""):
        s = r.offline_conversion_upload_conversion_action_summary
        alerts = [(E(a.error.conversion_upload_error) if a.error else "", round(a.error_percentage * 100, 1)) for a in s.alerts]
        days = [(d.upload_date, d.successful_count, d.failed_count, d.pending_count) for d in s.daily_summaries][-10:]
        print(f"   {s.conversion_action_name:12s} status={E(s.status)} total={s.total_event_count} ok={s.successful_event_count} pending={s.pending_event_count} "
              f"last={s.last_upload_date_time} alerts={alerts}")
        print(f"      recent days (date, ok, failed, pending): {days}")
except Exception as ex:
    print("   not available:", re.findall(r'message: "([^"]+)"', str(ex))[:1])
try:
    for r in q(c, """SELECT offline_conversion_upload_client_summary.client, offline_conversion_upload_client_summary.status,
            offline_conversion_upload_client_summary.total_event_count, offline_conversion_upload_client_summary.successful_event_count,
            offline_conversion_upload_client_summary.success_rate, offline_conversion_upload_client_summary.last_upload_date_time,
            offline_conversion_upload_client_summary.alerts FROM offline_conversion_upload_client_summary"""):
        s = r.offline_conversion_upload_client_summary
        print(f"   client {E(s.client)}: status={E(s.status)} total={s.total_event_count} ok={s.successful_event_count} "
              f"success={round(s.success_rate * 100, 1)}% last={s.last_upload_date_time} alerts={[E(a.error.conversion_upload_error) for a in s.alerts]}")
except Exception as ex:
    print("   client summary not available:", re.findall(r'message: "([^"]+)"', str(ex))[:1])

# 4. goals
acts = {str(r.conversion_action.id): (r.conversion_action.name, r.conversion_action.primary_for_goal, E(r.conversion_action.status), E(r.conversion_action.category), E(r.conversion_action.origin))
        for r in q(c, "SELECT conversion_action.id, conversion_action.name, conversion_action.primary_for_goal, conversion_action.status, conversion_action.category, conversion_action.origin FROM conversion_action WHERE conversion_action.id IN (7643656486, 7643656075, 1068114183, 6885463625, 6885576934)")}
print("\n4) KEY CONVERSION ACTIONS:")
for k, v in acts.items(): print(f"   {k} {v[0]:40s} primary={v[1]} {v[2]} {v[3]}/{v[4]}")
goals = collections.defaultdict(list)
for r in q(c, """SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable
        FROM campaign_conversion_goal WHERE campaign.id IN (24257819463,24257819466,24132507744,24268690038,24268690041)"""):
    if r.campaign_conversion_goal.biddable: goals[str(r.campaign.id)].append(f"{E(r.campaign_conversion_goal.category)}/{E(r.campaign_conversion_goal.origin)}")
print("   biddable goals on core heating campaigns identical:", len({tuple(sorted(v)) for v in goals.values()}) == 1, sorted(next(iter(goals.values()))))
(SNAP / "tracking-health-2026-09-27.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
