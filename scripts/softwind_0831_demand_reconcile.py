#!/usr/bin/env python3
"""Demand-bucket reconciliation + intra-campaign routing overlap.

Every figure is interpolated from the computed data structure. No number in the
output is hand-typed - that is the specific error this script exists to correct.

SELECT statements only plus KeywordPlanIdeaService (creates no plan resource).
"""
from __future__ import annotations

import glob
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
A, B = "24103511039", "24145053510"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    now = datetime.now(ZoneInfo("America/New_York"))

    c = list(svc.search(customer_id=cid, query="""SELECT customer.id,
        customer.descriptive_name, customer.manager, customer.test_account
        FROM customer LIMIT 1"""))[0].customer
    assert c.descriptive_name == "Softwind Power Washing - Live"
    assert normalize_customer_id(c.id) == CID and not c.manager and not c.test_account
    print(f"IDENTITY GATE: PASS  {c.descriptive_name} | {c.id}\n")

    pl = json.loads(Path(sorted(glob.glob(str(SNAP / "planner-architecture-*.json")))[-1])
                    .read_text(encoding="utf-8"))["rows"]

    # ---------- 1. dedupe into buckets ----------
    buckets = defaultdict(list)
    for r in pl.values():
        buckets[(r["vol"], r["lo"], r["hi"])].append(r["kw"])
    blist = []
    for (vol, lo, hi), members in sorted(buckets.items(), key=lambda x: -x[0][0]):
        blist.append({"vol": vol, "lo": lo, "hi": hi, "members": sorted(members),
                      "representative": sorted(members)[0]})
    unique_total = sum(b["vol"] for b in blist)
    print("=== UNIQUE KEYWORD PLANNER DEMAND BUCKETS ===")
    print(f"{'#':>2s} {'vol':>5s} {'TOPlow':>7s} {'TOPhigh':>8s}  keywords sharing this bucket")
    for i, b in enumerate(blist, 1):
        print(f"{i:2d} {b['vol']:5d} {b['lo']:7.2f} {b['hi']:8.2f}  "
              f"{', '.join(b['members'])[:96]}")
    print(f"   UNIQUE DEMAND TOTAL (each bucket counted once): {unique_total}/mo")

    # ---------- 2. coverage under each candidate structure ----------
    # A keyword covers the bucket it belongs to. Map keyword -> bucket index.
    kw2bucket = {}
    for i, b in enumerate(blist):
        for m in b["members"]:
            kw2bucket[m.lower()] = i

    STRUCTURES = {
        "SIX-GROUP (previous proposal)": {
            "Power Washing Near Me": ["power washing near me"],
            "Pressure Washing Near Me": ["pressure washing near me"],
            "Power Washing Service": ["power washing service"],
            "House Washing Near Me": ["house washing near me"],
            "Power Washing (head)": ["power washing"],
            "Pressure Washing (head)": ["pressure washing"],
        },
        "THREE-GROUP (compact core)": {
            "Power Washing": ["power washing", "power washing near me",
                              "power washing service", "power washing services near me",
                              "power washing company near me"],
            "Pressure Washing": ["pressure washing", "pressure washing near me",
                                 "pressure washing services near me",
                                 "residential pressure washing near me"],
            "House Washing": ["house washing near me", "house pressure washing near me",
                              "house power washing near me"],
        },
        "SIX-GROUP COMPACT (3 core + 3 existing micro)": {
            "Power Washing": ["power washing", "power washing near me",
                              "power washing service", "power washing services near me",
                              "power washing company near me"],
            "Pressure Washing": ["pressure washing", "pressure washing near me",
                                 "pressure washing services near me",
                                 "residential pressure washing near me"],
            "House Washing": ["house washing near me", "house pressure washing near me",
                              "house power washing near me"],
            "Soft House Washing Near Me (exists)": ["soft washing near me",
                                                    "soft house washing near me"],
            "Driveway Pressure Washing Near Me (exists)": ["driveway pressure washing near me",
                                                           "driveway power washing near me"],
            "Patio Pressure Washing Near Me (exists)": ["patio pressure washing near me",
                                                        "concrete pressure washing near me"],
        },
        "FOUR-GROUP (3 core + House, micro retired)": {
            "Power Washing": ["power washing", "power washing near me",
                              "power washing service", "power washing services near me",
                              "power washing company near me"],
            "Pressure Washing": ["pressure washing", "pressure washing near me",
                                 "pressure washing services near me",
                                 "residential pressure washing near me"],
            "House Washing": ["house washing near me", "house pressure washing near me",
                              "house power washing near me"],
            "Exterior Surface Washing": ["soft washing near me", "soft house washing near me",
                                         "driveway pressure washing near me",
                                         "patio pressure washing near me"],
        },
    }

    print("\n=== COVERAGE BY STRUCTURE (each bucket counted ONCE) ===")
    results = {}
    for label, groups in STRUCTURES.items():
        covered, assign, collisions = set(), {}, []
        for g, kws in groups.items():
            gb = set()
            for k in kws:
                bi = kw2bucket.get(k.lower())
                if bi is None:
                    continue
                if bi in covered and assign.get(bi) != g:
                    collisions.append((blist[bi]["vol"], assign[bi], g,
                                       blist[bi]["representative"]))
                covered.add(bi); gb.add(bi)
                assign.setdefault(bi, g)
        vol = sum(blist[i]["vol"] for i in covered)
        results[label] = {"groups": len(groups), "buckets": len(covered), "vol": vol,
                          "pct": round(100 * vol / unique_total, 2),
                          "keywords": sum(len(v) for v in groups.values()),
                          "collisions": collisions}
        print(f"\n  {label}")
        print(f"    ad groups={len(groups)}  keyword texts={sum(len(v) for v in groups.values())}"
              f"  buckets covered={len(covered)}/{len(blist)}")
        print(f"    UNIQUE DEMAND COVERED = {vol}/{unique_total} = "
              f"{round(100*vol/unique_total,2)}%")
        if collisions:
            print("    BUCKET COLLISIONS (two ad groups claiming ONE demand pool):")
            for v, g1, g2, rep in collisions:
                print(f"      {v:4d}/mo bucket '{rep}' claimed by BOTH '{g1}' and '{g2}'")
        else:
            print("    bucket collisions: none")
        missing = [blist[i] for i in range(len(blist)) if i not in covered]
        if missing:
            print(f"    uncovered buckets: "
                  f"{[(m['vol'], m['representative']) for m in missing]}")

    # ---------- 3. intra-campaign routing overlap, from real data ----------
    print("\n=== INTRA-CAMPAIGN OVERLAP: terms served by MORE THAN ONE ad group ===")
    routes = defaultdict(lambda: defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0}))
    for r in svc.search(customer_id=cid, query="""SELECT campaign.id, campaign.name,
            ad_group.id, ad_group.name, search_term_view.search_term,
            segments.keyword.info.text, segments.keyword.info.match_type,
            segments.search_term_match_type, metrics.impressions, metrics.clicks,
            metrics.cost_micros FROM search_term_view
            WHERE segments.date BETWEEN '2026-07-01' AND '2026-08-31'"""):
        key = (r.campaign.name, r.ad_group.name, r.segments.keyword.info.text,
               enum_name(r.segments.keyword.info.match_type),
               enum_name(r.segments.search_term_match_type))
        d = routes[r.search_term_view.search_term][key]
        d["impr"] += int(r.metrics.impressions)
        d["clicks"] += int(r.metrics.clicks)
        d["cost"] += int(r.metrics.cost_micros) / 1e6

    multi = {t: v for t, v in routes.items() if len(v) > 1}
    ti = sum(sum(x["impr"] for x in v.values()) for v in routes.values())
    tc = sum(sum(x["clicks"] for x in v.values()) for v in routes.values())
    tk = sum(sum(x["cost"] for x in v.values()) for v in routes.values())
    mi = sum(sum(x["impr"] for x in v.values()) for v in multi.values())
    mc = sum(sum(x["clicks"] for x in v.values()) for v in multi.values())
    mk = sum(sum(x["cost"] for x in v.values()) for v in multi.values())

    same_camp = 0
    for t, v in sorted(multi.items(), key=lambda x: -sum(y["cost"] for y in x[1].values())):
        camps = {k[0] for k in v}
        ags = {k[1] for k in v}
        scope = ("SAME CAMPAIGN, different ad groups" if len(camps) == 1
                 else "ACROSS CAMPAIGNS")
        if len(camps) == 1:
            same_camp += 1
        tot = sum(x["cost"] for x in v.values())
        print(f"\n  '{t}'  [{scope}]  ${tot:.2f}")
        for k, x in sorted(v.items(), key=lambda y: -y[1]["cost"]):
            print(f"      {k[0][:18]:18s} / {k[1][:32]:32s} kw='{k[2]}' {k[3]}/{k[4]} "
                  f"impr={x['impr']} clk={x['clicks']} ${x['cost']:.2f}")

    print(f"\n  terms served by >1 ad group: {len(multi)} of {len(routes)}")
    print(f"    of those, SAME-CAMPAIGN multi-ad-group: {same_camp}")
    print(f"    impressions {mi}/{ti} = {round(100*mi/ti,1)}%   "
          f"clicks {mc}/{tc} = {round(100*mc/tc,1)}%   "
          f"spend ${round(mk,2)}/${round(tk,2)} = {round(100*mk/tk,1)}%")

    out = {"generated_account_local": now.isoformat(), "mode": "READ-ONLY",
           "unique_demand_total": unique_total, "buckets": blist,
           "structures": results,
           "multi_ad_group_terms": {t: {str(k): v for k, v in val.items()}
                                    for t, val in multi.items()},
           "multi_overlap_pct": {"impressions": round(100 * mi / ti, 1),
                                 "clicks": round(100 * mc / tc, 1),
                                 "spend": round(100 * mk / tk, 1)}}
    p = SNAP / f"demand-reconcile-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWROTE {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
