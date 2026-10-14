#!/usr/bin/env python3
"""Ambient | 2026-10-07 | READ-ONLY search-term pull, Sept 1 .. today, no threshold.

Search: search_term_view x ad group x triggering keyword x day (every row with impressions, clicks or cost).
PMax: campaign_search_term_view x day (search terms with cost metrics) + campaign_search_term_insight categories
(Sept 1 .. today, per PMax campaign). Writes exports/search-terms-2026-10-07.jsonl,
exports/pmax-search-terms-2026-10-07.jsonl, snapshots/pmax-search-insights-2026-10-07.json. Prints counts only.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, EXPORTS  # noqa: E402

A = "2026-09-01"
NOW = datetime.datetime.now(TZ)
TODAY = NOW.date().isoformat()
PMAX = ["24295088845", "24318905515"]
money = lambda v: round(v / 1e6, 2)

c = client()
identity_gate(c, verbose=False)
print(f"identity PASS; read {NOW.isoformat(timespec='seconds')}")

n = 0
with (EXPORTS / "search-terms-2026-10-07.jsonl").open("w", encoding="utf-8") as fh:
    for r in q(c, f"""SELECT campaign.id, campaign.status, ad_group.id, ad_group.status, search_term_view.search_term, search_term_view.status,
            segments.keyword.info.text, segments.keyword.info.match_type, segments.keyword.ad_group_criterion, segments.search_term_match_type,
            segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions
            FROM search_term_view WHERE segments.date BETWEEN '{A}' AND '{TODAY}'"""):
        x = r.metrics
        if not (x.impressions or x.clicks or x.cost_micros):
            continue
        fh.write(json.dumps(dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), term=r.search_term_view.search_term,
                                 status=E(r.search_term_view.status), kw_text=r.segments.keyword.info.text,
                                 kw_match=E(r.segments.keyword.info.match_type),
                                 kw_id=r.segments.keyword.ad_group_criterion.split("~")[-1] if r.segments.keyword.ad_group_criterion else "",
                                 st_match=E(r.segments.search_term_match_type), date=r.segments.date, impr=x.impressions, clicks=x.clicks,
                                 cost=money(x.cost_micros), conv=round(x.conversions, 2), all_conv=round(x.all_conversions, 2))) + "\n")
        n += 1
print(f"search_term_view rows: {n}")

pn = 0
with (EXPORTS / "pmax-search-terms-2026-10-07.jsonl").open("w", encoding="utf-8") as fh:
    for r in q(c, f"""SELECT campaign.id, campaign_search_term_view.search_term, segments.date, metrics.impressions, metrics.clicks,
            metrics.cost_micros, metrics.conversions, metrics.all_conversions FROM campaign_search_term_view
            WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND campaign.id IN ({",".join(PMAX)})"""):
        x = r.metrics
        fh.write(json.dumps(dict(campaign=str(r.campaign.id), term=r.campaign_search_term_view.search_term, date=r.segments.date,
                                 impr=x.impressions, clicks=x.clicks, cost=money(x.cost_micros), conv=round(x.conversions, 2),
                                 all_conv=round(x.all_conversions, 2))) + "\n")
        pn += 1
print(f"campaign_search_term_view (PMax) rows: {pn}")

ins = {}
for cid in PMAX:
    rows = []
    try:
        for r in q(c, f"""SELECT campaign_search_term_insight.category_label, campaign_search_term_insight.id, metrics.impressions, metrics.clicks,
                metrics.conversions FROM campaign_search_term_insight WHERE segments.date BETWEEN '2026-10-01' AND '{TODAY}'
                AND campaign_search_term_insight.campaign_id = '{cid}'"""):
            rows.append(dict(label=r.campaign_search_term_insight.category_label, id=r.campaign_search_term_insight.id,
                             impr=r.metrics.impressions, clicks=r.metrics.clicks, conv=round(r.metrics.conversions, 2)))
    except Exception as exc:
        rows = [dict(error=str(exc).split("\n")[0][:300])]
    ins[cid] = rows
    print(f"PMax {cid} insight categories: {len(rows)}")
(SNAP / "pmax-search-insights-2026-10-07.json").write_text(json.dumps(ins, indent=1), encoding="utf-8")
