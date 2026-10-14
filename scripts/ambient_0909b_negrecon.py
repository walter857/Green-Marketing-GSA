#!/usr/bin/env python3
"""Reconcile 88 / 23 / 33 / 107 and emit row-level removal evidence."""
from __future__ import annotations
import sys, json, csv, re, unicodedata
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa

coll = json.load(open(EVID / "2026-09-09-collision-audit.json", encoding="utf-8"))
rem = json.load(open(EVID / "2026-09-09-removal-plan-analysis.json", encoding="utf-8"))
acct = json.load(open(EVID / "2026-09-09-account-level-triage.json", encoding="utf-8"))
state = json.load(open(EVID / "2026-09-09b-state-and-drift.json", encoding="utf-8"))
plans = {p.stem: json.loads(p.read_text(encoding="utf-8"))
         for p in (CLIENT_DIR / "plans").glob("AMB-0909-*.json")}

print("=== RECONCILIATION OF THE FOUR CONFLICTING COUNTS ===\n")

conv_c = {(h["match"], h["negative"]) for h in coll["converting_term_collisions"]}
probe_c = {(h["match"], h["negative"]) for h in coll["bofu_probe_collisions"]}
both = conv_c | probe_c
print(f"  A. distinct (match, text) CAMPAIGN-level negatives colliding with a converting term:"
      f" {len(conv_c)}")
print(f"  B. distinct (match, text) CAMPAIGN-level negatives colliding with a BOFU probe:"
      f" {len(probe_c)}")
print(f"  C. union of A and B  = THE '88' FIGURE                                     : {len(both)}")
print(f"     -> the September 9 report first printed 80 (= |A| only) in one place and 88")
print(f"        (= |A union B|) in another. 88 is correct; 80 omitted probe-only collisions.")

tri = rem["triage"]
vc = Counter(r["verdict"] for r in tri)
print(f"\n  D. triage of those {len(tri)} campaign-level colliding negatives:")
for k, v in vc.items():
    print(f"       {k:<10} {v}")
print(f"     -> THE '23' FIGURE is the REMOVE bucket at CAMPAIGN level only.")

rm1 = plans["AMB-0909-NEG-RM-1"]["operations"]
rm2 = plans["AMB-0909-NEG-RM-2"]["operations"]
t1 = {o["negative_text"].lower() for o in rm1}
t2 = {o["negative_text"].lower() for o in rm2}
print(f"\n  E. AMB-0909-NEG-RM-1: {len(rm1)} operations, {len(t1)} distinct texts")
print(f"     AMB-0909-NEG-RM-2: {len(rm2)} operations, {len(t2)} distinct texts")
print(f"     overlap (present at BOTH layers): {len(t1 & t2)}  -> {sorted(t1 & t2)}")
print(f"  F. distinct texts across both packages = {len(t1 | t2)}   <- THE '33' FIGURE")
print(f"  G. total operations across both packages = {len(rm1)} + {len(rm2)} = "
      f"{len(rm1)+len(rm2)}   <- THE '107' FIGURE")

print(f"\n  WHY 23 REMOVE VERDICTS BECOME {len(rm1)} CAMPAIGN OPERATIONS:")
per = Counter(o["negative_text"].lower() for o in rm1)
print(f"     the 23 REMOVE verdicts resolve to {len(t1)} distinct texts actually present as")
print(f"     live campaign criteria; each text exists on 1-5 campaigns, and PHRASE 'savage'")
print(f"     was added separately after the geo sweep. Placement counts:")
for txt, n in sorted(per.items(), key=lambda kv: (-kv[1], kv[0])):
    print(f"       x{n}  {txt!r}")
print(f"     sum of placements = {sum(per.values())} = the {len(rm1)} operations.")

recon = {
    "collisions_converting_only": len(conv_c),
    "collisions_probe_only": len(probe_c),
    "collisions_union_88": len(both),
    "campaign_triage": dict(vc),
    "rm1_ops": len(rm1), "rm1_texts": len(t1),
    "rm2_ops": len(rm2), "rm2_texts": len(t2),
    "overlap_texts": sorted(t1 & t2),
    "distinct_texts_33": len(t1 | t2),
    "total_ops_107": len(rm1) + len(rm2),
    "placements_per_text": dict(per),
}

# ---------------- row-level evidence ----------------
live = {(n["camp"], n["crit"]): n for n in state["live"]["campaign_negatives"]}
acct_live = {a["rn"]: a for a in state["live"]["account_level"]}
harm = coll["converting_term_collisions"]
probes = coll["bofu_probe_collisions"]
byneg_terms = defaultdict(list)
byneg_probes = defaultdict(list)
for h in harm:
    byneg_terms[(h["match"], h["negative"])].append(h)
for h in probes:
    byneg_probes[(h["match"], h["negative"])].append(h["probe"])

rows = []
for o in rm1:
    k = (o["match_type"], o["negative_text"].lower())
    lv = live.get((o["campaign_id"], o["criterion_id"]))
    terms = byneg_terms.get(k, [])
    mine = [t for t in terms if t["campaign"] == o["campaign"]]
    rows.append({
        "package": "RM-1", "scope": "CAMPAIGN", "campaign": o["campaign"],
        "campaign_id": o["campaign_id"], "criterion_id": o["criterion_id"],
        "resource_name": o["resource_name"], "match_type": o["match_type"],
        "negative_text": o["negative_text"],
        "live_and_enabled": bool(lv),
        "blocked_protected_probes": "|".join(sorted(set(byneg_probes.get(k, [])))),
        "n_blocked_probes": len(set(byneg_probes.get(k, []))),
        "blocked_historical_terms": "|".join(sorted({t["term"] for t in mine})),
        "n_blocked_terms": len({t["term"] for t in mine}),
        "primary_conv_at_risk": o.get("conversions_at_risk_if_left", 0),
        "all_conv_at_risk": o.get("all_conversions_at_risk_if_left", 0),
        "reason": o["reason"]})
for o in rm2:
    k = (o["match_type"], o["negative_text"].lower())
    lv = acct_live.get(o["shared_criterion_resource_name"])
    terms = byneg_terms.get(k, [])
    rows.append({
        "package": "RM-2", "scope": "ACCOUNT (shared set 11252984411)", "campaign": "ALL 23",
        "campaign_id": "", "criterion_id": o["criterion_id"],
        "resource_name": o["shared_criterion_resource_name"], "match_type": o["match_type"],
        "negative_text": o["negative_text"],
        "live_and_enabled": bool(lv),
        "blocked_protected_probes": "|".join(sorted(set(o.get("bofu_probes_unblocked", [])))),
        "n_blocked_probes": len(set(o.get("bofu_probes_unblocked", []))),
        "blocked_historical_terms": "|".join(sorted({t["term"] for t in terms})),
        "n_blocked_terms": len({t["term"] for t in terms}),
        "primary_conv_at_risk": o.get("conversions_at_risk_if_left", 0),
        "all_conv_at_risk": o.get("all_conversions_at_risk_if_left", 0),
        "reason": o["reason"]})

p = EVID / "2026-09-09b-removal-row-evidence.csv"
with p.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"\n=== ROW-LEVEL EVIDENCE: {len(rows)} rows -> {p.relative_to(ROOT)} ===")
print(f"  all rows confirmed live+ENABLED: {all(r['live_and_enabled'] for r in rows)}")
print(f"  by package: {dict(Counter(r['package'] for r in rows))}")
print(f"  by scope:   {dict(Counter(r['scope'] for r in rows))}")

recon["row_evidence_file"] = str(p.relative_to(ROOT))
recon["row_count"] = len(rows)
write(EVID / "2026-09-09b-negative-reconciliation.json", recon)

# ---------------- intent grouping for packages A-D ----------------
print("\n=== INTENT GROUPING FOR THE REPLACEMENT PACKAGES ===")
MANU = {"carrier", "trane", "lennox", "goodman", "rheem", "mitsubishi", "daikin", "amana",
        "bosch", "bryant", "armstrong", "ruud"}
SERVICE = {"thermostat", "thermostats", "humidifier", "dehumidifier", "geothermal maryland",
           "air duct cleaning"}
GROUPS = {"A_high_confidence": [], "B_manufacturers": [], "C_additional_services": [],
          "D_dealer_installer": [], "HOLD_names": []}
DEALER = {"daikin cerca de mi", "geothermal maryland", "trane authorized dealers near me",
          "trane installers near me"}
SUPPLY_KEEP = {"carrier enterprise laurel", "carrier mid atlantic hanover maryland",
               "carrier mid atlantic near me", "ce carrier enterprise near me",
               "daikin comfort technologies locations", "daikin elkridge md"}
HOLDN = {"al", "american", "mr"}
for r in rows:
    t = r["negative_text"].lower()
    if t in HOLDN:
        GROUPS["HOLD_names"].append(r)
    elif t in ("savage", "free", "licensed", "commercial"):
        GROUPS["A_high_confidence"].append(r)
    elif t in DEALER:
        GROUPS["D_dealer_installer"].append(r)
    elif t in SUPPLY_KEEP:
        GROUPS["B_manufacturers"].append(r)   # these are the RETAIN list, flagged below
    elif any(w in MANU for w in t.split()) or t in MANU:
        GROUPS["B_manufacturers"].append(r)
    elif t in SERVICE:
        GROUPS["C_additional_services"].append(r)
    else:
        GROUPS["HOLD_names"].append(r)
for g, v in GROUPS.items():
    print(f"  {g:<24} rows={len(v):<4} distinct texts={len({x['negative_text'].lower() for x in v})}")
    for t in sorted({x["negative_text"].lower() for x in v}):
        n = sum(1 for x in v if x["negative_text"].lower() == t)
        sc = sorted({x["scope"].split(" ")[0] for x in v if x["negative_text"].lower() == t})
        retain = "  [RETAIN - supply house/corporate/location]" if t in SUPPLY_KEEP else ""
        print(f"      x{n} {sc} {t!r}{retain}")
json.dump({k: v for k, v in GROUPS.items()},
          open(EVID / "2026-09-09b-removal-groups.json", "w", encoding="utf-8"),
          indent=1, default=str)
print(f"\nWROTE {(EVID / '2026-09-09b-removal-groups.json').relative_to(ROOT)}")
