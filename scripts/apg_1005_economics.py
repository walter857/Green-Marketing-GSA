#!/usr/bin/env python3
"""2026-10-05 economics and sensitivity for Apogee (pure math, inputs from the fresh snapshot).

Verified inputs only: spend, clicks, CPC from the snapshot. Conversion rates and the close rate
are ASSUMPTIONS and labelled as such. Missing outcomes (qualified leads, estimates, sales,
revenue, gross profit) are reported as unavailable, never as $0.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S = json.loads((ROOT / "clients/apogee-lawns/snapshots/2026-10-05-conversion-plan-snapshot.json").read_text(encoding="utf-8"))


def agg(w):
    m = S["windows"][w]["rows"][0]
    return int(m["cost_micros"]) / 1e6, int(m["clicks"]), int(m["impressions"])


out = {}
for w in ("launch_to_yesterday", "last_7"):
    cost, clicks, impr = agg(w)
    out[w] = {"spend": round(cost, 2), "clicks": clicks, "impressions": impr, "cpc": round(cost / clicks, 4)}
cpc_all, cpc_7 = out["launch_to_yesterday"]["cpc"], out["last_7"]["cpc"]
MONTHLY_CAP = round(16.44 * 30.4, 2)
CLOSE_ASSUMED = 0.20
rows = []
for cvr in (0.05, 0.08, 0.10):
    for label, cpc in (("full window", cpc_all), ("last 7 days", cpc_7)):
        cpl = cpc / cvr
        clicks_cap = MONTHLY_CAP / cpc
        rows.append({"cvr": cvr, "cpc_basis": label, "cpc": round(cpc, 2), "cpl": round(cpl, 2),
                     "cac_at_assumed_20pct_close": round(cpl / CLOSE_ASSUMED, 2),
                     "max_clicks_per_month_at_cap": round(clicks_cap, 1),
                     "leads_per_month_if_budget_fully_spent": round(clicks_cap * cvr, 2),
                     "p_zero_leads_in_7_clicks": round((1 - cvr) ** 7, 4),
                     "p_zero_leads_in_8_clicks": round((1 - cvr) ** 8, 4)})
out["sensitivity"] = rows
out["cvr_needed_for_100_cpl"] = {"full window": round(cpc_all / 100, 4), "last 7 days": round(cpc_7 / 100, 4)}
out["monthly_cap_usd"] = MONTHLY_CAP
out["observed"] = {"leads_google_ads": 0, "leads_whatconverts_paid": 0, "cpl": "unavailable (0 leads)",
                   "cpql": "unavailable", "cac": "unavailable", "revenue": "unavailable",
                   "gross_profit": "unavailable", "profit_after_ad_spend": "unavailable"}
out["break_even_note"] = ("ad-cost-only break-even gross profit per sold job = CAC; at the assumed 20% close rate "
                          "the job must earn at least the CAC above before any other cost")
print(json.dumps(out, indent=1))
(ROOT / "clients/apogee-lawns/audits/2026-10-05-conversion-plan/economics.json").write_text(json.dumps(out, indent=1))
