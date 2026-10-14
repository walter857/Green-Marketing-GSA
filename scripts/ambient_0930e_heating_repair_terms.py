#!/usr/bin/env python3
"""Ambient | 2026-09-30e | READ-ONLY search-term relevance review for the PHRASE keyword "heating repair"
(ad group 204129717007, campaign 24257819463). Raw terms stay on disk (exports/heating-repair-terms-2026-09-30.jsonl);
stdout carries category aggregates only. Complete days 2026-09-17..29; 2026-09-30 provisional shown separately.
Also: live budget pacing vs the forecast. No mutations, no negatives, no match-type changes.
"""
from __future__ import annotations
import sys, json, re, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, SNAP, EXPORTS  # noqa: E402

CAMP, AG = "24257819463", "204129717007"
A, B, T = "2026-09-17", "2026-09-29", "2026-09-30"
CATS = [
    ("ambiguous/off-target", re.compile(r"water heater|hot water|tankless|\bac\b|a/c|air cond|cooling|\bcool\b|plumb|\bjobs?\b|career|salary|hiring|"
                                        r"school|course|training|\bcar\b|\bauto|truck|\brv\b|pool|boiler|heat pump|mini ?split|ductless|thermostat|"
                                        r"fireplace|space heater|baseboard|radiant floor|parts?\b|supply|supplies|home depot|lowes|amazon", re.I)),
    ("informational", re.compile(r"how (to|do|does|much does)|\bwhat\b|\bwhy\b|\bdiy\b|yourself|reset|troubleshoot|meaning|symptom|\bsigns?\b|guide|tips|"
                                 r"video|youtube|reddit|manual|\bcode\b|error|\?$", re.I)),
    ("installation/replacement", re.compile(r"install|replac|\bnew (furnace|heater|heat|heating|system)|upgrade|\bbuy\b", re.I)),
    ("no-heat", re.compile(r"no heat|not heating|won'?t heat|not working|stopped working|cold air|blowing cold|heat not|isn'?t heating|"
                           r"won'?t turn on|not turning on|no warm|broken", re.I)),
    ("furnace repair", re.compile(r"furnace.*(repair|fix|service|technician|\btech\b|company|contractor|near me|specialist|emergency)|"
                                  r"(repair|fix|service).*furnace", re.I)),
    ("direct heating repair", re.compile(r"(heating|heater|\bheat\b|hvac).*(repair|fix|service|technician|\btech\b|company|contractor|specialist|"
                                         r"near me|emergency)|(repair|fix|service).*(heating|heater|\bheat\b)", re.I)),
]


def cat(t):
    return next((n for n, rx in CATS if rx.search(t)), "ambiguous/off-target")


c = client()
identity_gate(c, verbose=False)
rows = []
for r in q(c, f"""SELECT ad_group.id, segments.keyword.info.text, segments.keyword.info.match_type, segments.search_term_match_type,
        search_term_view.search_term, segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions
        FROM search_term_view WHERE campaign.id = {CAMP} AND segments.date BETWEEN '{A}' AND '{T}'"""):
    rows.append(dict(ad_group=str(r.ad_group.id), kw=r.segments.keyword.info.text.lower(), kw_mt=E(r.segments.keyword.info.match_type),
                     stmt=E(r.segments.search_term_match_type), term=r.search_term_view.search_term, date=r.segments.date,
                     impr=r.metrics.impressions, clicks=r.metrics.clicks, cost=r.metrics.cost_micros / 1e6, conv=r.metrics.conversions))
with (EXPORTS / "heating-repair-terms-2026-09-30.jsonl").open("w", encoding="utf-8") as f:
    for x in rows:
        f.write(json.dumps(x) + "\n")
kv = {}
for label, (a, b) in (("complete", (A, B)), ("provisional", (T, T))):
    for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, metrics.impressions,
            metrics.clicks, metrics.cost_micros FROM keyword_view WHERE ad_group.id = {AG} AND segments.date BETWEEN '{a}' AND '{b}'"""):
        if r.ad_group_criterion.keyword.text.lower() == "heating repair" and E(r.ad_group_criterion.keyword.match_type) == "PHRASE":
            kv[label] = dict(impr=r.metrics.impressions, clicks=r.metrics.clicks, cost=round(r.metrics.cost_micros / 1e6, 2))
out = {"keyword_view": kv}
for label, keep in (("complete", lambda d: A <= d <= B), ("provisional", lambda d: d == T)):
    sel = [x for x in rows if x["ad_group"] == AG and x["kw"] == "heating repair" and x["kw_mt"] == "PHRASE" and keep(x["date"])]
    agg = collections.defaultdict(collections.Counter); lit = collections.defaultdict(collections.Counter); stmt = collections.defaultdict(collections.Counter)
    terms = collections.defaultdict(set)
    for x in sel:
        k = cat(x["term"])
        agg[k].update(dict(impr=x["impr"], clicks=x["clicks"], cost=x["cost"], conv=x["conv"])); terms[k].add(x["term"])
        l = "contains 'heating repair'" if "heating repair" in x["term"].lower() else "semantic match (no 'heating repair' in query)"
        lit[l].update(dict(impr=x["impr"], clicks=x["clicks"], cost=x["cost"])); terms[l].add(x["term"])
        stmt[x["stmt"]].update(dict(impr=x["impr"], clicks=x["clicks"], cost=x["cost"]))
    tot = collections.Counter()
    for v in agg.values():
        tot.update(v)
    out[label] = {"categories": {k: dict(v, terms=len(terms[k])) for k, v in agg.items()}, "literal": {k: dict(v, terms=len(terms[k])) for k, v in lit.items()},
                  "search_term_match_type": {k: dict(v) for k, v in stmt.items()}, "visible": dict(tot)}
    kvv = kv.get(label, {})
    print(f"\n=== 'heating repair' PHRASE, {label}: keyword total {kvv} | visible in search terms: impr {tot['impr']}, clicks {tot['clicks']}, "
          f"cost ${tot['cost']:.2f} ({100 * tot['cost'] / kvv['cost']:.0f}% of keyword cost)" if kvv.get("cost") else f"\n=== {label}: {kvv} visible {dict(tot)}")
    print(f"  {'category':28s} {'terms':>5s} {'impr':>5s} {'%impr':>6s} {'clicks':>6s} {'cost':>8s} {'%cost':>6s} conv")
    for k, _ in CATS:
        v = agg.get(k)
        if v:
            print(f"  {k:28s} {len(terms[k]):5d} {v['impr']:5d} {100 * v['impr'] / tot['impr']:5.0f}% {v['clicks']:6d} {v['cost']:8.2f} "
                  f"{(100 * v['cost'] / tot['cost']) if tot['cost'] else 0:5.0f}% {v['conv']:.0f}")
    for k, v in lit.items():
        print(f"  {k:52s} terms {len(terms[k]):4d} impr {v['impr']:5d} clicks {v['clicks']:3d} cost ${v['cost']:.2f}")
    print("  Google search_term_match_type:", {k: dict(v) for k, v in stmt.items()})

# ---- live pacing vs budget ----
daily = {r.segments.date: (r.metrics.cost_micros / 1e6, r.metrics.clicks) for r in q(c, f"""SELECT campaign.id, segments.date, metrics.cost_micros,
        metrics.clicks FROM campaign WHERE campaign.id = {CAMP} AND segments.date BETWEEN '2026-09-22' AND '{T}'""")}
hours = collections.Counter()
for r in q(c, f"""SELECT campaign.id, segments.hour, metrics.cost_micros FROM campaign WHERE campaign.id = {CAMP}
        AND segments.date BETWEEN '2026-09-24' AND '{B}'"""):
    hours[r.segments.hour] += r.metrics.cost_micros / 1e6
out["pacing"] = {"daily": daily, "cost_by_hour_0924_0929": dict(hours)}
print("\n=== LIVE PACING (budget $85/day; Google may spend up to 2x on a day; monthly limit 30.4 x $85 = $2,584) ===")
for d, (cost, cl) in sorted(daily.items()):
    print(f"  {d} ${cost:7.2f} {cl} clicks  = {cost / 85:.2f}x budget{'  (provisional)' if d == T else ''}")
print("  cost by hour (Sep 24-29):", {h: round(v, 2) for h, v in sorted(hours.items()) if v})
(SNAP / "heating-repair-terms-2026-09-30.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
