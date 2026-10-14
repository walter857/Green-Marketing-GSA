#!/usr/bin/env python3
"""Audit every keyword row PLAN-I2 would enable, for SKAG integrity. READ-ONLY."""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
AUD = ROOT / "clients/softwind-power-washing/audits"
OUTJ = SNAP / "plan-i2-keyword-audit-2026-08-26.json"
OUTC = AUD / "2026-08-26-plan-i2-62-keyword-audit.csv"

TARGETS = [("205713509704", "24103511039", "Power Washing", "Pressure & Power Washing"),
           ("198082078943", "24145053510", "Power Washing #2", "Soft & House Washing")]

# canonical intent classifier
INTENT = [
    ("POWER WASHING - generic service", re.compile(r"^power washing (service|company|contractor|estimate|quote)$|^power washing service long island$|^residential power washing service$", re.I)),
    ("POWER WASHING - geo modified", re.compile(r"power washing long island", re.I)),
    ("PRESSURE WASHING - generic service", re.compile(r"^pressure washing (service|company|contractor|estimate|quote)$|^professional pressure washing$|^residential pressure washing service$|^exterior pressure washing service$", re.I)),
    ("PRESSURE WASHING - geo modified", re.compile(r"pressure washing long island", re.I)),
    ("HOUSE WASHING", re.compile(r"house washing|house soft washing", re.I)),
    ("SOFT WASHING", re.compile(r"^soft washing", re.I)),
]


def canonical(text):
    for label, rx in INTENT:
        if rx.search(text):
            return label
    return "UNCLASSIFIED"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    deep = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
    snap = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))
    inv = json.loads((SNAP / "rescue-inventory-ranking-2026-08-26.json").read_text(encoding="utf-8"))
    AG = snap["ad_groups"]
    live = [k for k in snap["enabled_keywords_live"]]
    live_texts = {k["text"] for k in live}
    live_by_camp = defaultdict(set)
    for k in live:
        live_by_camp[k["campaign_id"]].add(k["text"])
    # all paused SKAG texts too, for duplicate detection
    paused_skag = defaultdict(set)
    for k in snap["keywords"]:
        g = AG[k["ad_group_id"]]
        if g["status"] != "ENABLED":
            paused_skag[g["name"]].add(k["text"])

    # historical keyword performance
    hist = {}
    for r in svc.search(customer_id=CID, query="""
        SELECT ad_group.id, ad_group_criterion.criterion_id,
               metrics.impressions, metrics.clicks, metrics.cost_micros,
               metrics.conversions
        FROM keyword_view WHERE segments.date BETWEEN '2026-08-01' AND '2026-08-26'"""):
        hist[(str(r.ad_group.id), str(r.ad_group_criterion.criterion_id))] = {
            "impressions": int(r.metrics.impressions),
            "clicks": int(r.metrics.clicks),
            "cost": round(r.metrics.cost_micros / 1_000_000, 2),
            "conversions": float(r.metrics.conversions)}

    rows = []
    per_group = defaultdict(lambda: {"intents": defaultdict(int), "rows": 0})

    for gid, cid, cname, gname in TARGETS:
        rank = [r for r in inv["rankings"] if r["ad_group_name"] == gname][0]
        pd = rank["planner_detail"]
        ads = [a for a in deep["ads"] if a["ad_group_id"] == gid]
        final_urls = sorted({u for a in ads for u in a["final_urls"]})
        rsa_headlines = [h["text"] for a in ads for h in a["headlines"]]
        rsa_blob = " ".join(rsa_headlines).lower()

        for k in sorted([x for x in snap["keywords"] if x["ad_group_id"] == gid],
                        key=lambda x: (x["text"], x["match_type"])):
            t = k["text"]
            p = pd.get(t) or {}
            h = hist.get((gid, k["criterion_id"]),
                         {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
            ci = canonical(t)
            per_group[gname]["intents"][ci] += 1
            per_group[gname]["rows"] += 1

            # RSA relevance: does any headline contain the keyword's head noun phrase?
            head = re.sub(r"\b(service|services|company|contractor|estimate|quote|"
                          r"near me|long island)\b", "", t, flags=re.I).strip()
            rsa_rel = "MATCH" if head and head in rsa_blob else "WEAK"

            # landing-page relevance
            lp = final_urls[0] if final_urls else ""
            if "power-washing-soft-washing" in lp:
                if ci.startswith("POWER WASHING"):
                    lp_rel = "PARTIAL - page names power washing but no city"
                elif ci.startswith("PRESSURE"):
                    lp_rel = "PARTIAL - page mentions pressure washing 5x, no city"
                elif ci in ("HOUSE WASHING", "SOFT WASHING"):
                    lp_rel = "PARTIAL - page covers soft washing, no city, generic"
                else:
                    lp_rel = "WEAK"
            else:
                lp_rel = "UNKNOWN"

            # duplicate / semantic overlap
            dupe, overlap = "NONE", []
            if t in live_texts:
                dupe = "EXACT TEXT ALREADY LIVE"
            # semantic overlap against live texts
            tw = set(t.split())
            for lt in live_texts:
                lw = set(lt.split())
                shared = tw & lw
                if len(shared) >= 2 and (
                        "washing" in shared or "wash" in shared):
                    # ignore the trivial 'washing' only overlap
                    core = shared - {"washing", "wash", "near", "me"}
                    if core:
                        overlap.append(lt)
            if overlap and dupe == "NONE":
                dupe = "SEMANTIC OVERLAP"

            # recommended destination
            dest = {
                "POWER WASHING - generic service": "NEW SKAG: Power Washing Service",
                "POWER WASHING - geo modified": "NEW SKAG: Power Washing Long Island",
                "PRESSURE WASHING - generic service": "NEW SKAG: Pressure Washing Service",
                "PRESSURE WASHING - geo modified": "NEW SKAG: Pressure Washing Long Island",
                "HOUSE WASHING": "NEW SKAG: House Washing Near Me",
                "SOFT WASHING": "NEW SKAG: Soft Washing Near Me",
            }.get(ci, "REVIEW")

            rows.append({
                "campaign": cname, "campaign_id": cid,
                "ad_group": gname, "ad_group_id": gid,
                "criterion_id": k["criterion_id"],
                "keyword_text": t, "match_type": k["match_type"],
                "status": k["status"], "approval": k["approval"],
                "hist_impressions": h["impressions"], "hist_clicks": h["clicks"],
                "hist_cost": h["cost"], "hist_conversions": h["conversions"],
                "planner_local_volume": p.get("avg_monthly_searches"),
                "planner_competition": p.get("competition"),
                "planner_bid_low": p.get("low_bid"), "planner_bid_high": p.get("high_bid"),
                "planner_trend_pct": p.get("recent_trend_pct_last3_vs_prev3"),
                "search_intent": ("BOFU service-hire" if p.get("avg_monthly_searches")
                                  else "BOFU service-hire (below reporting threshold)"),
                "canonical_service_intent": ci,
                "rsa_relevance": rsa_rel,
                "current_final_url": lp,
                "landing_page_relevance": lp_rel,
                "duplicate_or_overlap": dupe,
                "overlapping_live_keywords": ";".join(sorted(set(overlap))) or "",
                "recommended_destination_ad_group": dest,
            })

    # per-group verdict
    verdicts = {}
    for gname, d in per_group.items():
        n_int = len([i for i in d["intents"] if i != "UNCLASSIFIED"])
        verdicts[gname] = {
            "keyword_rows": d["rows"],
            "distinct_canonical_intents": n_int,
            "intent_breakdown": dict(d["intents"]),
            "CONTAINS_EXACTLY_ONE_CANONICAL_INTENT": "YES" if n_int <= 1 else "NO",
        }

    out = {"generated": "2026-08-26", "plan_under_audit": "PLAN-I2",
           "fingerprint_under_audit": "6AF733F709E2",
           "total_keyword_rows": len(rows),
           "verdicts": verdicts, "keywords": rows}
    OUTJ.write_text(json.dumps(out, indent=2), encoding="utf-8")

    AUD.mkdir(parents=True, exist_ok=True)
    with OUTC.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("TOTAL KEYWORD ROWS AUDITED: %d" % len(rows))
    print()
    for gname, v in verdicts.items():
        print("=" * 92)
        print("AD GROUP: %s" % gname)
        print("  keyword rows: %d" % v["keyword_rows"])
        print("  DOES THIS AD GROUP CONTAIN EXACTLY ONE CANONICAL CUSTOMER INTENT? -> %s"
              % v["CONTAINS_EXACTLY_ONE_CANONICAL_INTENT"])
        print("  distinct canonical intents: %d" % v["distinct_canonical_intents"])
        for i, n in sorted(v["intent_breakdown"].items(), key=lambda x: -x[1]):
            print("      %-42s %d rows" % (i, n))
    print()
    print("DUPLICATE / OVERLAP SUMMARY")
    from collections import Counter
    print("  ", dict(Counter(r["duplicate_or_overlap"] for r in rows)))
    print()
    print("RSA RELEVANCE  ", dict(Counter(r["rsa_relevance"] for r in rows)))
    print("LANDING PAGE   ", dict(Counter(r["landing_page_relevance"] for r in rows)))
    print()
    print("HISTORICAL DELIVERY OF ALL 62 ROWS:")
    print("  impressions=%d clicks=%d cost=$%.2f conversions=%.0f"
          % (sum(r["hist_impressions"] for r in rows),
             sum(r["hist_clicks"] for r in rows),
             sum(r["hist_cost"] for r in rows),
             sum(r["hist_conversions"] for r in rows)))
    print()
    print("wrote %s" % OUTC)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
