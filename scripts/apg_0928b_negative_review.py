#!/usr/bin/env python3
"""2026-09-28 (run B) LOCAL negative review + search-term coverage for Apogee Lawns.

Inputs are the fresh snapshot and Planner files already on disk. No API call. No mutation.
Raw search terms are read from disk and written to one local CSV; stdout carries aggregates only.
Probe queries below are HYPOTHETICAL test strings written for this review; they carry no volume.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_negmatch import negative_blocks, positive_reaches, tokens  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "reports" / "apogee-lawns" / "evidence"
OUT = ROOT / "clients" / "apogee-lawns" / "audits" / "2026-09-28-independent"
OUT.mkdir(parents=True, exist_ok=True)
S = json.loads((EVID / "2026-09-28b-snapshot.json").read_text(encoding="utf-8"))
CT = json.loads((EVID / "2026-09-28b-negative-corpus-test.json").read_text(encoding="utf-8"))
CAMP = "24257151015"

negs = [x for x in S["campaign_criteria"] if x.get("type_") == "KEYWORD" and x.get("negative")]
pos = [(x["keyword"]["text"], x["keyword"]["match_type"]) for x in S["ad_group_criteria"]
       if x.get("type_") == "KEYWORD" and not x.get("negative") and x.get("status") == "ENABLED"]

EMPLOY = ("employment / hiring of workers", "permanent christmas light installation {w}", "none - not a buyer", "KEEP",
          "Employment intent; Green Marketing excludes employment work.")
DIY = ("do-it-yourself / instructions", None, "low", "KEEP",
       "DIY and instructional intent dominates; a buyer rarely phrases a hiring search this way.")
RETAIL = ("retail product purchase", "permanent christmas lights {w}", "none - product shopper", "KEEP",
          "Retail/product purchase intent, not installation.")
EVENT = ("holiday events, displays and attractions", "{w} lincoln", "none - not a buyer", "KEEP",
         "Event/attraction intent; cannot plausibly be a permanent-installation buyer.")
PRODUCT = ("decor products outside the service", "permanent christmas lights {w}", "none", "KEEP",
           "Product type Apogee does not install as part of this service.")
TRADE = ("trade / wholesale buyers", "permanent christmas lights {w}", "none", "KEEP", "Trade purchasing, not a homeowner hire.")
RENT = ("rental of lights", "{w} permanent christmas lights", "none", "KEEP", "Rental intent; not the service.")
COMPETITOR = ("competing permanent-lighting system brand", "{w} permanent christmas lights installer", "low-moderate",
              "KEEP", "Apogee's own site states it is an EverLights certified dealer; this is a competing system. "
              "Conquest bidding on competitor systems is a business preference, and the ad brief bars brand wording.")
SEASONAL_REMOVABLE = ("seasonal hanging / takedown (excluded service)", None, "moderate per query, volume unknown",
                      "REMOVE-CANDIDATE", "Every positive requires 'permanent', so the seasonal-only searches this was "
                      "meant to exclude cannot reach the campaign anyway (negative reachability). The only queries it "
                      "can still block also contain 'permanent', and those read as permanent-lighting buyers. No "
                      "observed volume: low priority, bundle into the next negative plan only.")
SEASONAL_KEEP = ("seasonal service or post-sale service not offered", None, "low", "KEEP",
                 "With 'permanent' present the query is about removing, storing or repairing a system, not buying one.")
LABOR = ("labor-only install of customer-supplied lights", None, "moderate - buyer of labor",
         "NEEDS-EVIDENCE", "Encodes an unverified business assumption that Apogee will not install customer-supplied "
         "lights. Keep until the owner confirms either way; remove if Apogee does offer labor-only installs.")
APP = ("existing-owner app/product support", "{w} permanent christmas lights", "none - existing owner", "KEEP",
       "Post-purchase support intent.")

RULES = {
    "job": EMPLOY, "jobs": EMPLOY, "career": EMPLOY, "careers": EMPLOY, "salary": EMPLOY,
    "laser": PRODUCT, "lasers": PRODUCT, "projector": PRODUCT, "projectors": PRODUCT,
    "inflatable": PRODUCT, "inflatables": PRODUCT, "wreath": PRODUCT, "wreaths": PRODUCT,
    "garland": PRODUCT, "garlands": PRODUCT,
    "indoor": ("indoor lighting products", "indoor permanent christmas lights", "none", "KEEP",
               "Permanent roofline lighting is exterior; indoor intent is a product search."),
    "tutorial": DIY, "tutorials": DIY, "instructions": DIY, "diy": DIY, "do it yourself": DIY,
    "how to": ("do-it-yourself / instructions", "how to hire a permanent christmas lights installer", "low",
               "KEEP", "Blocks rare buyer phrasings like the probe, but almost all 'how to' + permanent-lights "
               "searches are DIY installation. Revisit only if search terms show buyer wording being lost."),
    "rent": RENT, "rental": RENT, "rentals": RENT,
    "wholesale": TRADE, "supplier": TRADE, "suppliers": TRADE, "distributor": TRADE, "distributors": TRADE,
    "kit": ("DIY product kits", "permanent christmas light kit installation", "low", "KEEP",
            "Mostly DIY kit shoppers. The buyer-of-labor case is governed by the labor-only negatives."),
    "kits": ("DIY product kits", "permanent christmas lights kits installed", "low", "KEEP",
             "Mostly DIY kit shoppers. The buyer-of-labor case is governed by the labor-only negatives."),
    "costco": RETAIL, "ebay": RETAIL, "walmart": RETAIL, "amazon": RETAIL, "lowes": RETAIL, "menards": RETAIL,
    "temu": RETAIL, "home depot": RETAIL, "target christmas lights": RETAIL, "where to buy": RETAIL,
    "christmas lights for sale": RETAIL, "holiday lights for sale": RETAIL, "replacement christmas bulbs": RETAIL,
    "light show": EVENT, "lights show": EVENT, "christmas lights map": EVENT, "holiday lights map": EVENT,
    "christmas light tour": EVENT, "holiday light tour": EVENT, "zoo lights": EVENT, "christmas at the zoo": EVENT,
    "christmas parade": EVENT, "lighting festival": EVENT, "holiday event": EVENT, "drive through": EVENT,
    "best christmas displays": ("holiday display attractions", "best christmas displays lincoln", "none", "KEEP",
                                "Contains the protected word 'best' only inside an event phrase; 'best permanent "
                                "christmas light installer' is NOT blocked (verified by the matcher)."),
    "christmas light hanging service": dict(zip(("intent", "probe", "risk", "verdict", "why"), SEASONAL_REMOVABLE),
                                            probe="permanent christmas light hanging service"),
    "seasonal light installation": dict(zip(("intent", "probe", "risk", "verdict", "why"), SEASONAL_REMOVABLE),
                                        probe="permanent vs seasonal light installation cost"),
    "take down christmas lights": dict(zip(("intent", "probe", "risk", "verdict", "why"), SEASONAL_REMOVABLE),
                                       probe="permanent christmas lights never take down christmas lights again"),
    "christmas light removal": dict(zip(("intent", "probe", "risk", "verdict", "why"), SEASONAL_KEEP),
                                    probe="permanent christmas light removal"),
    "christmas light storage": dict(zip(("intent", "probe", "risk", "verdict", "why"), SEASONAL_KEEP),
                                    probe="permanent christmas light storage"),
    "christmas light repair": dict(zip(("intent", "probe", "risk", "verdict", "why"), SEASONAL_KEEP),
                                   probe="permanent christmas light repair"),
    "labor only": dict(zip(("intent", "probe", "risk", "verdict", "why"), LABOR),
                       probe="permanent christmas light installation labor only"),
    "customer supplied": dict(zip(("intent", "probe", "risk", "verdict", "why"), LABOR),
                              probe="permanent christmas light installation customer supplied"),
    "my own lights": dict(zip(("intent", "probe", "risk", "verdict", "why"), LABOR),
                          probe="permanent christmas light installation with my own lights"),
    "app download": APP, "app not working": APP,
    "trimlight": COMPETITOR, "jellyfish": COMPETITOR, "gemstone": COMPETITOR, "oelo": COMPETITOR,
    "celebright": COMPETITOR,
    "govee": ("DIY consumer permanent-light product", "govee permanent christmas lights installation", "low", "KEEP",
              "Highest-value negative: it matches 105 Planner ideas (740 summed bucket volume) in the approved "
              "area - the DIY product dominates the query space around this service."),
}

rows = []
for x in negs:
    t, mt = x["keyword"]["text"], x["keyword"]["match_type"]
    r = RULES[t]
    if isinstance(r, tuple):
        intent, probe, risk, verdict, why = r
        probe = (probe or "permanent christmas light installation {w}").replace("{w}", t)
    else:
        intent, probe, risk, verdict, why = r["intent"], r["probe"], r["risk"], r["verdict"], r["why"]
    probe_blocked = negative_blocks(probe, t, mt)
    probe_reach = any(positive_reaches(probe, k, m) for k, m in pos)
    rows.append({"negative_text": t, "match_type": mt, "criterion_id": x["criterion_id"],
                 "scope": f"campaign {CAMP}", "live_association": "ENABLED campaign negative (fresh read)",
                 "intended_exclusion": intent,
                 "query_example": probe, "query_example_kind": "HYPOTHETICAL (no volume)",
                 "example_blocked_by_this_negative": probe_blocked,
                 "example_reachable_by_a_positive_literal_proxy": probe_reach,
                 "planner_ideas_blocked_any_reach": CT["per_negative_corpus_hits"][x["criterion_id"]],
                 "planner_ideas_blocked_bucket_volume": CT["per_negative_corpus_vol"][x["criterion_id"]],
                 "purchase_intent_risk": risk, "verdict": verdict, "rationale": why})
with (OUT / "03_negative_review.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
from collections import Counter  # noqa: E402
print("negatives reviewed:", len(rows), "verdicts:", dict(Counter(r["verdict"] for r in rows)))
print("probe queries actually blocked by their own negative:", sum(r["example_blocked_by_this_negative"] for r in rows), "of", len(rows))
bad = [r["negative_text"] for r in rows if not r["example_blocked_by_this_negative"]]
print("probes NOT blocked (probe design error):", bad)

# ---- buyer modifiers: none may be blocked by any live negative
MODS = ["near me", "quote", "estimate", "price", "pricing", "cost", "best", "local", "hire", "installer",
        "installation", "contractor", "reviews", "free estimate", "company", "lincoln ne"]
mod_hits = {}
for m in MODS:
    for base in ("permanent christmas light installation {m}", "{m} permanent christmas lights installer",
                 "best permanent christmas light installer {m}"):
        qq = base.replace("{m}", m)
        hits = [n["keyword"]["text"] for n in negs if negative_blocks(qq, n["keyword"]["text"], n["keyword"]["match_type"])]
        if hits:
            mod_hits[qq] = hits
print("buyer-modifier probes blocked:", mod_hits or "NONE")

# ---- search-term coverage (aggregates only)
raw = json.loads((EVID / "2026-09-28b-search-terms-RAW.json").read_text(encoding="utf-8"))
tot = {"impr": 0, "clicks": 0, "cost": 0.0}
for d in S["daily"].values():
    tot["impr"] += int(d.get("impressions", 0))
    tot["clicks"] += int(d.get("clicks", 0))
    tot["cost"] += int(d.get("cost_micros", 0)) / 1e6
cov = {"impr": sum(x["impr"] for x in raw), "clicks": sum(x["clicks"] for x in raw), "cost": sum(x["cost"] for x in raw)}
SERVICE = re.compile(r"\b(install|installs|installer|installers|installation|installed|installing|company|companies|"
                     r"contractor|contractors|service|services|near me|quote|quotes|estimate|professional|pro|hire|"
                     r"cost|costs|price|prices|pricing)\b")
LOCAL = re.compile(r"\b(lincoln|nebraska|ne|waverly|eagle|crete|ashland|hickman|sprague|firth|roca)\b")
HEAD = {"permanent", "christmas", "xmas", "light", "lights"}
buck = defaultdict(lambda: {"rows": 0, "distinct": set(), "impr": 0, "clicks": 0, "cost": 0.0})
verdict_rows = []
for x in raw:
    t = x["term"].lower()
    if SERVICE.search(t):
        b, v = "SERVICE_MARKER", "KEEP ELIGIBLE - buyer marker present"
    elif LOCAL.search(t):
        b, v = "LOCAL_MARKER_ONLY", "KEEP ELIGIBLE - local provider marker"
    elif set(tokens(t)) <= HEAD:
        b, v = "BARE_HEAD_VARIANT", "KEEP ELIGIBLE - the approved head term; ambiguous but deliberately bought EXACT"
    else:
        b, v = "OUT_OF_SCOPE_BY_WHITELIST", "MONITOR - no whitelist marker; 0 clicks, $0; no negative proposed"
    k = buck[(b, x["kw"], x["kw_mt"])]
    k["rows"] += 1
    k["distinct"].add(t)
    k["impr"] += x["impr"]
    k["clicks"] += x["clicks"]
    k["cost"] += x["cost"]
    verdict_rows.append({**x, "bucket": b, "verdict": v})
with (OUT / "03_search_term_verdicts_RAW.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(verdict_rows[0]))
    w.writeheader()
    w.writerows(verdict_rows)
print(f"search-term rows: {len(raw)} (daily grain); distinct terms: {len({x['term'].lower() for x in raw})}")
print(f"coverage: impressions {cov['impr']}/{tot['impr']} = {cov['impr']/tot['impr']:.1%}; clicks {cov['clicks']}/{tot['clicks']}; "
      f"cost ${cov['cost']:.2f}/${tot['cost']:.2f}")
agg = []
for (b, kw, mt), v in sorted(buck.items()):
    print(f"  {b:<26} via {mt:<6} {kw:<40} distinct={len(v['distinct'])} impr={v['impr']} clicks={v['clicks']} cost=${v['cost']:.2f}")
    agg.append({"bucket": b, "keyword": kw, "match_type": mt, "distinct_terms": len(v["distinct"]),
                "impressions": v["impr"], "clicks": v["clicks"], "cost": round(v["cost"], 2)})
json.dump({"campaign_totals_2026_09_17_to_28": tot, "search_term_view_totals": cov, "buckets": agg,
           "buyer_modifier_probe_hits": mod_hits},
          (EVID / "2026-09-28b-search-term-coverage.json").open("w", encoding="utf-8"), indent=1)
