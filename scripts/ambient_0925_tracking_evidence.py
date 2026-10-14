#!/usr/bin/env python3
"""Ambient | 2026-09-25 | READ-ONLY tracking evidence for the completion matrix. Counts only, no PII.

Separates four layers per lead route: capture (WhatConverts record), attribution (click id /
session), upload acceptance (not readable via API v1 - UI only), Google credit (conversion by
conversion date). QA leads excluded through client.yaml.
"""
from __future__ import annotations
import sys, json, collections, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, CLIENT_DIR
from gm_gsa.whatconverts import fetch_leads

c = client(); identity_gate(c, verbose=False)
today = datetime.datetime.now(TZ).date().isoformat()
out = {"when": datetime.datetime.now(TZ).isoformat()}

wc = fetch_leads("115814", "105803", "2026-09-20", today, client_yaml=CLIENT_DIR / "client.yaml")
rows = []
for l in wc["leads"]:
    rows.append(dict(id=str(l.get("lead_id")), date=str(l.get("date_created"))[:16], type=l.get("lead_type"),
                     src=f"{l.get('lead_source')}/{l.get('lead_medium')}", num=str(l.get("tracking_number") or "")[-4:],
                     click="gclid" if l.get("gclid") else ("gbraid" if l.get("gbraid") else ("wbraid" if l.get("wbraid") else "-")),
                     page=str(l.get("landing_url") or l.get("lead_url") or "").split("?")[0].replace("https://", "")[:55],
                     quotable=l.get("quotable"), spam=l.get("spam")))
out["wc_since_0920"] = rows
print(f"WhatConverts since 2026-09-20: {wc['raw_count']} raw, {len(wc['qa_excluded'])} QA excluded -> {len(rows)}")
for r in sorted(rows, key=lambda x: x["date"]):
    if r["click"] != "-" or "offer." in r["page"] or r["src"].endswith("/cpc") or r["num"] in ("6354", "4650", "9517"):
        print(f"  {r['id']} {r['date']} {r['type']:12s} {r['src']:22s} num..{r['num']} {r['click']:6s} q={r['quotable']} {r['page']}")
print("  by source/medium x type:", dict(collections.Counter((r["src"], r["type"]) for r in rows)))

# Google credit by conversion date
acts = {"7643656486": "WC Lead", "7643656075": "WC Calls", "1068114183": "Calls from ads", "6885463625": "Native form (secondary)",
        "6885576934": "Website call (secondary)"}
cred = collections.defaultdict(lambda: collections.Counter())
for r in q(c, f"""SELECT segments.conversion_action, segments.date, metrics.all_conversions_by_conversion_date, campaign.id
        FROM campaign WHERE segments.date BETWEEN '2026-09-15' AND '{today}' AND metrics.all_conversions_by_conversion_date > 0"""):
    a = r.segments.conversion_action.split("/")[-1]
    cred[acts.get(a, a)][f"{r.segments.date} c{r.campaign.id}"] += round(r.metrics.all_conversions_by_conversion_date, 2)
out["google_credit_by_conversion_date"] = {k: dict(v) for k, v in cred.items()}
print("\nGoogle all-conversions by conversion date since 09-15:")
for k, v in cred.items(): print(f"  {k}: {dict(v)}")

calls = collections.Counter()
for r in q(c, f"""SELECT call_view.call_status, call_view.type, call_view.call_duration_seconds, call_view.start_call_date_time, campaign.id
        FROM call_view WHERE call_view.start_call_date_time >= '2026-09-15 00:00:00'"""):
    calls[(r.call_view.start_call_date_time[:10], str(r.campaign.id), E(r.call_view.type), E(r.call_view.call_status), r.call_view.call_duration_seconds >= 60)] += 1
out["call_view_since_0915"] = [list(k) + [v] for k, v in calls.items()]
print("\ncall_view since 09-15 (date, campaign, display location, status, >=60s): ", dict(calls))

# paid Maps override number vs organic GBP numbers, 2026 YTD labels
wc26 = fetch_leads("115814", "105803", "2026-01-01", today, client_yaml=CLIENT_DIR / "client.yaml")["leads"]
maps = collections.Counter()
for l in wc26:
    n = str(l.get("tracking_number") or "")[-4:]
    if n in ("4650", "7280", "4021", "9803"):
        maps[(n, f"{l.get('lead_source')}/{l.get('lead_medium')}", "click-id" if (l.get("gclid") or l.get("gbraid") or l.get("wbraid")) else "no-click-id")] += 1
out["maps_numbers_2026"] = [list(k) + [v] for k, v in maps.items()]
print("\n2026 leads by Maps/GBP number (last4, source/medium, click id):", dict(maps))
(SNAP / "tracking-evidence-2026-09-25.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
