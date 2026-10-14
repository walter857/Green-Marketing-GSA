#!/usr/bin/env python3
"""Ambient | 2026-09-21b | All-time clearing CPC and conversion evidence per heating service.

READ-ONLY. EXTERNAL WRITES: 0.

CPC ceilings must come from actual clearing prices, not from the old $25/$30 defaults. The
account holds ~$108k of heating history across paused and removed campaigns, so the sweep
covers every campaign status, not just ENABLED.

Two regimes are reported separately and must never be averaged together:
  - PRE-CEILING (through 2026-09-04): uncapped Maximize Clicks. Prices are inflated; these
    are an upper bound on what the auction WILL take, not what it costs today.
  - POST-CEILING (2026-09-05 onward): CPC ceilings in force. CPCs pinned just under a cap
    prove the cap set the price, not the auction.

Per theme it reports cost, clicks, mean CPC, the CPC distribution (so one $106 outlier
cannot set a ceiling), conversions and CPA.
"""
from __future__ import annotations
import sys, json, re, datetime, statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21b"
SPLIT = "2026-09-05"
TODAY = "2026-09-21"

# Theme matchers run against "campaign name + ad group name". Order matters: the first
# match wins, so the most specific themes are listed first.
THEMES = [
    ("geothermal", re.compile(r"geothermal", re.I)),
    ("thermostat", re.compile(r"thermostat", re.I)),
    ("ductless_minisplit", re.compile(r"ductless|mini ?split", re.I)),
    ("heat_pump", re.compile(r"heat ?pump", re.I)),
    ("gas_boiler", re.compile(r"gas boiler", re.I)),
    ("oil_boiler", re.compile(r"oil boiler", re.I)),
    ("boiler", re.compile(r"boiler", re.I)),
    ("gas_furnace", re.compile(r"gas furnace", re.I)),
    ("electric_furnace", re.compile(r"electric furnace", re.I)),
    ("oil_furnace", re.compile(r"oil furnace", re.I)),
    ("furnace", re.compile(r"furnace", re.I)),
    ("no_heat_emergency", re.compile(r"no ?heat|emergency", re.I)),
    ("heating_generic", re.compile(r"heating", re.I)),
]
INTENTS = [
    ("maintenance", re.compile(r"maintenance|tune ?up|inspection", re.I)),
    ("replacement", re.compile(r"replace|replacement", re.I)),
    ("installation", re.compile(r"install", re.I)),
    ("repair", re.compile(r"repair|service|fix", re.I)),
]


def theme_of(name):
    for k, rx in THEMES:
        if rx.search(name):
            return k
    return None


def intent_of(name):
    for k, rx in INTENTS:
        if rx.search(name):
            return k
    return "unspecified"


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0, "regime_split": SPLIT}

    for tag, lo, hi in (("pre_ceiling", "2019-01-01", "2026-09-04"),
                        ("post_ceiling", SPLIT, TODAY)):
        print(f"\n{'=' * 78}\n=== {tag.upper()}  ({lo}..{hi}) ===")
        agg, agg_i = {}, {}
        for r in q(c, f"""SELECT campaign.id, campaign.name, campaign.status,
                          ad_group.id, ad_group.name,
                          metrics.cost_micros, metrics.clicks, metrics.impressions,
                          metrics.conversions, metrics.all_conversions
                          FROM ad_group
                          WHERE segments.date BETWEEN '{lo}' AND '{hi}'"""):
            nm = f"{r.campaign.name} {r.ad_group.name}"
            th = theme_of(nm)
            if not th:
                continue
            it = intent_of(nm)
            for key, store in ((th, agg), (f"{th}|{it}", agg_i)):
                a = store.setdefault(key, {"cost": 0.0, "clicks": 0, "impr": 0,
                                           "conv": 0.0, "all_conv": 0.0})
                a["cost"] += r.metrics.cost_micros / 1e6
                a["clicks"] += r.metrics.clicks
                a["impr"] += r.metrics.impressions
                a["conv"] += r.metrics.conversions
                a["all_conv"] += r.metrics.all_conversions

        # Per-day per-ad-group CPCs give a distribution, so one outlier cannot set a cap.
        dist = {}
        for r in q(c, f"""SELECT campaign.name, ad_group.name, segments.date,
                          metrics.cost_micros, metrics.clicks
                          FROM ad_group
                          WHERE segments.date BETWEEN '{lo}' AND '{hi}'
                            AND metrics.clicks > 0"""):
            nm = f"{r.campaign.name} {r.ad_group.name}"
            th = theme_of(nm)
            if not th:
                continue
            cpc = (r.metrics.cost_micros / 1e6) / r.metrics.clicks
            dist.setdefault(th, []).append(round(cpc, 2))

        rows = {}
        print(f"{'theme':22s} {'cost':>10s} {'clicks':>7s} {'meanCPC':>8s} "
              f"{'p50':>7s} {'p75':>7s} {'p90':>7s} {'conv':>7s} {'CPA':>9s}")
        for k, a in sorted(agg.items(), key=lambda x: -x[1]["cost"]):
            d = sorted(dist.get(k, []))
            mean = a["cost"] / a["clicks"] if a["clicks"] else None
            p = lambda q_: (statistics.quantiles(d, n=100)[q_ - 1] if len(d) > 2
                            else (d[0] if d else None))
            row = {"cost": round(a["cost"], 2), "clicks": a["clicks"],
                   "impressions": a["impr"],
                   "mean_cpc": round(mean, 2) if mean else None,
                   "cpc_p50": round(p(50), 2) if d else None,
                   "cpc_p75": round(p(75), 2) if d else None,
                   "cpc_p90": round(p(90), 2) if d else None,
                   "cpc_max": max(d) if d else None,
                   "conversions": round(a["conv"], 2),
                   "all_conversions": round(a["all_conv"], 2),
                   "cpa": round(a["cost"] / a["conv"], 2) if a["conv"] else None,
                   "cpc_sample_days": len(d)}
            rows[k] = row
            print(f"{k:22s} {row['cost']:10.2f} {row['clicks']:7d} "
                  f"{str(row['mean_cpc']):>8s} {str(row['cpc_p50']):>7s} "
                  f"{str(row['cpc_p75']):>7s} {str(row['cpc_p90']):>7s} "
                  f"{row['conversions']:7.2f} {str(row['cpa']):>9s}")
        out[tag] = rows
        out[f"{tag}_by_intent"] = {
            k: {"cost": round(a["cost"], 2), "clicks": a["clicks"],
                "conversions": round(a["conv"], 2),
                "mean_cpc": round(a["cost"] / a["clicks"], 2) if a["clicks"] else None,
                "cpa": round(a["cost"] / a["conv"], 2) if a["conv"] else None}
            for k, a in sorted(agg_i.items(), key=lambda x: -x[1]["cost"])}

        print(f"\n   --- {tag}: theme x intent (cost desc, top 24) ---")
        for k, v in list(out[f"{tag}_by_intent"].items())[:24]:
            print(f"      {k:36s} ${v['cost']:9.2f} {v['clicks']:5d}cl "
                  f"CPC ${str(v['mean_cpc']):>7s} conv {v['conversions']:6.2f} "
                  f"CPA ${str(v['cpa']):>9s}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"service-history-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
