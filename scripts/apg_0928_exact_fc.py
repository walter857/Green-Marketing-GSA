#!/usr/bin/env python3
"""2026-09-28 READ-ONLY: exact-only vs exact+phrase forecasts for the synonym candidates, plus click types and calls."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, E, client, q, write  # noqa: E402
from apg_0928_synonyms_fc import forecast  # noqa: E402

c = client()
out = {}
CASES = {
    "holiday E": [("permanent holiday lights", "EXACT")],
    "holiday E + lighting E": [("permanent holiday lights", "EXACT"), ("permanent holiday lighting", "EXACT")],
    "holiday E+P + lighting E": [("permanent holiday lights", "EXACT"), ("permanent holiday lights", "PHRASE"),
                                 ("permanent holiday lighting", "EXACT")],
    "house lights E": [("permanent house lights", "EXACT")],
    "outdoor lighting E": [("permanent outdoor lighting", "EXACT")],
    "outdoor lights E": [("permanent outdoor lights", "EXACT")],
}
print(f"  {'case':<28} {'clicks':>7} {'cost':>8}")
for k, kws in CASES.items():
    r = forecast(c, kws)
    out[k] = r
    print(f"  {k:<28} {r.get('clicks', 'ERR'):>7} {r.get('cost', r.get('error', ''))!s:>8}")
    time.sleep(2)

print("\n=== click types since 2026-09-21 ===")
for r in q(c, """SELECT segments.click_type, metrics.clicks, metrics.impressions, metrics.cost_micros FROM campaign
    WHERE segments.date BETWEEN '2026-09-21' AND '2026-09-28'"""):
    print(f"  {E(r.segments.click_type):<22} clicks={r.metrics.clicks} impr={r.metrics.impressions} cost=${r.metrics.cost_micros/1e6:.2f}")
calls = q(c, """SELECT call_view.call_duration_seconds, call_view.call_status, call_view.start_call_date_time,
    call_view.type FROM call_view""")
print(f"  call_view rows (calls from ads, all time): {len(calls)}")
for r in calls:
    v = r.call_view
    print(f"    {v.start_call_date_time} {E(v.call_status)} {v.call_duration_seconds}s {E(v.type_)}")
out["calls_from_ads"] = len(calls)
write(EVID / "2026-09-28-exact-forecasts.json", out)
