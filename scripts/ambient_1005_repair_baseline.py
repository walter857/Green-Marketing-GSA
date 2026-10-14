#!/usr/bin/env python3
"""Ambient | 2026-10-05 | $18-ceiling test baseline + five-day comparison template for campaign 24257819463. No API calls.

Inputs (all read 2026-10-05): snapshots/repair-read-2026-10-05.json, snapshots/cpl-reconciliation-2026-10-05.json,
snapshots/repair-search-term-analysis-2026-10-05.json. Impression share comes from window-level API rows (never averaged by day).
Baseline 09-24..09-30 ($42 ceiling; 09-30 is old-$42 traffic, also shown alone). Test = complete serving days under $18:
10-01, 10-02, 10-05, 10-06, 10-07 (same Thu/Fri/Mon/Tue/Wed mix as the baseline). Only 10-01 and 10-02 are complete at this read.
Writes snapshots/repair-18-baseline-2026-10-05.json and exports/repair-18-test-template-2026-10-05.csv; prints the markdown table.
"""
from __future__ import annotations
import csv, json, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CD = ROOT / "clients" / "ambient-cooling-heating"
S = json.loads((CD / "snapshots" / "repair-read-2026-10-05.json").read_text(encoding="utf-8"))
R = json.loads((CD / "snapshots" / "cpl-reconciliation-2026-10-05.json").read_text(encoding="utf-8"))
T = json.loads((CD / "snapshots" / "repair-search-term-analysis-2026-10-05.json").read_text(encoding="utf-8"))
P, AG = S["performance"], S["ad_groups"]
CAMP, HRP = "24257819463", "204129717007~142140742"
COLS = {"baseline": ("2026-09-24", "2026-09-30", "base"), "0930_old42": ("2026-09-30", "2026-09-30", None),
        "1001": ("2026-10-01", "2026-10-01", None), "1002": ("2026-10-02", "2026-10-02", None), "test_to_date": ("2026-10-01", "2026-10-02", "test")}
WKEY = {"baseline": "baseline_0924_0930", "0930_old42": "d0930", "1001": "d1001", "1002": "d1002", "test_to_date": "test_complete_1001_1002"}


def sumd(src, a, b, pick=lambda k: True, part=lambda k: k.split("|")[1]):
    c = collections.Counter()
    for k, v in P[src].items():
        if a <= part(k) <= b and pick(k):
            for m in ("impr", "clicks", "cost"):
                c[m] += v[m]
    return {m: round(c[m], 2) for m in ("impr", "clicks", "cost")}


def leads(a, b):
    rows = [r for r in R["leads"] if r.get("campaign") == CAMP and r["paid"] in ("CLICK_ID", "CALL_VIEW") and a <= r.get("attr_date", "") <= b]
    ver = [r for r in rows if r["verification"] == "VERIFIED"]
    gcalls = [c for c in R["unmatched_call_views"] if c["campaign"] == CAMP and a <= c["start"][:10] <= b]
    return len(ver), sum(1 for r in ver if r["qualified"]), gcalls


out = {}
for col, (a, b, tw) in COLS.items():
    w = P["campaign_window"][WKEY[col]]
    days = sorted(d for d in P["campaign_daily"] if a <= d <= b and P["campaign_daily"][d]["impr"] > 0)
    n, nq, gc = leads(a, b)
    loc = sumd("click_type_daily", a, b, pick=lambda k: k.endswith("LOCATION_EXPANSION"))
    dev = {d: sumd("device_daily", a, b, pick=lambda k, d=d: k.endswith(d), part=lambda k: k.split("|")[0]) for d in ("MOBILE", "DESKTOP", "TABLET")}
    agd = {AG[g]["name"][7:]: sumd("ad_group_daily", a, b, pick=lambda k, g=g: k.startswith(g), part=lambda k: k.split("|")[1]) for g in AG}
    kw = sumd("keyword_daily", a, b, pick=lambda k: k.startswith("204129717007~142140741|"), part=lambda k: k.split("|")[1])
    vis = T.get(f"visible_{tw}") if tw else None
    cat = T.get(f"by_category_{tw}") if tw else None
    out[col] = dict(window=f"{a}..{b}", serving_days=len(days), impr=w["impr"], clicks=w["clicks"], cost=w["cost"],
                    ctr=round(100 * w["clicks"] / w["impr"], 2) if w["impr"] else None, cpc=round(w["cost"] / w["clicks"], 2) if w["clicks"] else None,
                    per_day=dict(impr=round(w["impr"] / len(days), 1), clicks=round(w["clicks"] / len(days), 2), cost=round(w["cost"] / len(days), 2)) if days else None,
                    IS=round(100 * w["IS"], 1), lost_rank=round(100 * w["lost_rank"], 1), lost_budget=round(100 * w["lost_budget"], 1),
                    top=round(100 * w["top"], 1), abs_top=round(100 * w["abs_top"], 1),
                    verified_paid_leads=n, qualified=nq, google_calls_without_wc=[(c["start"], c["dur"]) for c in gc],
                    cpl=round(w["cost"] / n, 2) if n else None, cpql=round(w["cost"] / nq, 2) if nq else None,
                    sensitivity_cpl=round(w["cost"] / (n + len(gc)), 2) if (n + len(gc)) else None,
                    location_asset=loc, device=dev, ad_group={k: v for k, v in agd.items() if v["impr"]}, heating_repair_phrase=kw,
                    visible_terms=vis, visible_by_category=cat)
(CD / "snapshots" / "repair-18-baseline-2026-10-05.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

ROWSPEC = [("Serving days", lambda c: c["serving_days"]), ("Impressions", lambda c: f"{c['impr']:,}"), ("Clicks", lambda c: c["clicks"]),
           ("CTR", lambda c: f"{c['ctr']}%"), ("Avg CPC", lambda c: f"${c['cpc']}" if c["cpc"] else "-"), ("Spend", lambda c: f"${c['cost']:,.2f}"),
           ("Per serving day: impr / clicks / spend", lambda c: f"{c['per_day']['impr']} / {c['per_day']['clicks']} / ${c['per_day']['cost']}"),
           ("Location-asset clicks / spend", lambda c: f"{c['location_asset']['clicks']:.0f} / ${c['location_asset']['cost']:.2f}"),
           ("Verified genuine paid leads", lambda c: c["verified_paid_leads"]), ("Qualified (Quotable Yes)", lambda c: c["qualified"]),
           ("CPL", lambda c: f"${c['cpl']}" if c["cpl"] else f"undefined (${c['cost']:.2f} / 0)"), ("CPQL", lambda c: f"${c['cpql']}" if c["cpql"] else "undefined"),
           ("Google calls with no WhatConverts record", lambda c: len(c["google_calls_without_wc"])),
           ("Search impression share", lambda c: f"{c['IS']}%"), ("Lost IS (rank)", lambda c: f"{c['lost_rank']}%"), ("Lost IS (budget)", lambda c: f"{c['lost_budget']}%"),
           ("Top / abs-top IS", lambda c: f"{c['top']}% / {c['abs_top']}%"),
           ("Mobile clicks / spend", lambda c: f"{c['device']['MOBILE']['clicks']:.0f} / ${c['device']['MOBILE']['cost']:.2f}"),
           ("Desktop clicks / spend", lambda c: f"{c['device']['DESKTOP']['clicks']:.0f} / ${c['device']['DESKTOP']['cost']:.2f}"),
           ("Tablet impr", lambda c: f"{c['device']['TABLET']['impr']:.0f}"),
           ("Heating Repair group clicks / spend", lambda c: f"{c['ad_group'].get('Heating Repair', {}).get('clicks', 0):.0f} / ${c['ad_group'].get('Heating Repair', {}).get('cost', 0):.2f}"),
           ("Other groups clicks / spend", lambda c: f"{sum(v['clicks'] for k, v in c['ad_group'].items() if k != 'Heating Repair'):.0f} / ${sum(v['cost'] for k, v in c['ad_group'].items() if k != 'Heating Repair'):.2f}"),
           ("`heating repair` Phrase clicks / spend", lambda c: f"{c['heating_repair_phrase']['clicks']:.0f} / ${c['heating_repair_phrase']['cost']:.2f}"),
           ("Visible search terms: spend (share)", lambda c: f"${c['visible_terms']['cost']:.2f} ({100 * c['visible_terms']['cost'] / c['cost']:.0f}%)" if c["visible_terms"] else "see test total"),
           ("Visible spend, clearly irrelevant", lambda c: f"${c['visible_by_category']['Clearly irrelevant / off-target']['cost']:.2f}" if c["visible_by_category"] else ""),
           ("Visible spend, ambiguous", lambda c: f"${c['visible_by_category']['Ambiguous']['cost']:.2f}" if c["visible_by_category"] else ""),
           ("Visible spend, heating / furnace / no-heat", lambda c: f"${sum(c['visible_by_category'][k]['cost'] for k in ('Direct heating repair', 'Furnace repair', 'No-heat')):.2f}" if c["visible_by_category"] else "")]
hdr = ["Metric", "Baseline 09-24..30 ($42)", "of which 09-30 (old $42)", "Oct 1", "Oct 2", "Oct 5", "Oct 6", "Oct 7", "Test total (to date: Oct 1-2)", "Change vs baseline, per serving day"]
print("| " + " | ".join(hdr) + " |\n|" + "---|" * len(hdr))
rows = []
for name, f in ROWSPEC:
    vals = [f(out[k]) for k in ("baseline", "0930_old42", "1001", "1002")] + ["", "", ""] + [f(out["test_to_date"]), ""]
    rows.append([name] + [str(v) for v in vals])
    print("| " + " | ".join([name] + [str(v) for v in vals]) + " |")
with (CD / "exports" / "repair-18-test-template-2026-10-05.csv").open("w", newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh); wr.writerow(hdr); wr.writerows(rows)
print("\nwrote snapshots/repair-18-baseline-2026-10-05.json and exports/repair-18-test-template-2026-10-05.csv")
