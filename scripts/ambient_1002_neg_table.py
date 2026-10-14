#!/usr/bin/env python3
"""Ambient | 2026-10-02 | Render the complete negative table (applied + withheld + PMax scope) from local files. No API calls."""
from __future__ import annotations
import json
from pathlib import Path

CD = Path(__file__).resolve().parents[1] / "clients" / "ambient-cooling-heating"
d = json.loads((CD / "exports" / "negative-decisions-2026-10-02.json").read_text(encoding="utf-8"))
rec = json.loads((CD / "receipts" / "AMB-1002-NEG-EXACT-2-EXECUTED.json").read_text(encoding="utf-8"))
CN = {"24257819463": "Repair", "24257819466": "Install & Replace", "24268690038": "Heat Pump", "24268690041": "Thermostat",
      "24279798229": "Maintenance", "24132507744": "Boiler", "24274160783": "Geothermal", "24132507747": "HVAC Installation"}
CAT = {"competitor": "Competitor", "ac": "AC only", "model": "Model/part", "thermostat_diy": "Thermostat DIY/product", "oil": "Oil", "water_heater": "Water heater",
       "pellet_stove": "Pellet stove", "availability": "24-hour", "vehicle": "Vehicle/RV", "info": "DIY question", "floor_heat": "Floor heat"}
ids = {(x["campaign"], x["text"]): x["saved"][2] for x in rec["readback"]}
app = sorted([x for x in d if x["decision"] == "APPLY"], key=lambda x: (x["bucket"] != "competitor", x["bucket"], CN[x["campaign_id"]], x["query"]))
L = ["| # | Negative [EXACT] | Campaign | Category | Sept impr/clk/$ | Why | Criterion ID |", "|---|---|---|---|---|---|---|"]
for i, x in enumerate(app, 1):
    why = x["reason"].split("verified: ")[1] if "verified: " in x["reason"] else x["reason"]
    L.append(f"| {i} | {x['query']} | {CN[x['campaign_id']]} | {CAT[x['bucket']]} | {x['sep']['impr']}/{x['sep']['clicks']}/${x['sep']['cost']:.2f} | {why} | {ids[(x['campaign_id'], x['query'])]} |")
W = ["| Term | Campaign | Sept impr/clk/$ | Why withheld |", "|---|---|---|---|"]
W += [f"| {x['query']} | {CN[x['campaign_id']]} | {x['sep']['impr']}/{x['sep']['clicks']}/${x['sep']['cost']:.2f} | {x['reason']} |" for x in d if x["decision"] == "WITHHELD"]
(CD / "exports" / "negative-table-2026-10-02.md").write_text("\n".join(L) + "\n\n" + "\n".join(W) + "\n", encoding="utf-8")
print("\n".join(L)); print(); print("\n".join(W))
