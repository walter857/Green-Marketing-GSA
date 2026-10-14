#!/usr/bin/env python3
"""Sweep all 6,160 live negatives against (a) the 75 live geo targets and
(b) a service x place x intent probe grid, to find any remaining self-inflicted block."""
from __future__ import annotations
import sys, json, re, unicodedata, csv
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa

struct = json.load(open(EVID / "2026-09-09-structure.json", encoding="utf-8"))
geo = json.load(open(EVID / "2026-09-09-geo-targets.json", encoding="utf-8"))


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


live = [n for n in struct["campaign_negatives"]
        if n["status"] == "ENABLED" and n["campaign_id"] in FIVE]
live_neg = defaultdict(lambda: {"BROAD": set(), "PHRASE": set(), "EXACT": set()})
for n in live:
    live_neg[n["campaign_id"]][n["match"]].add(norm(n["text"]))
acct = {"BROAD": set(), "PHRASE": set(), "EXACT": set()}
for sc in struct["shared_criteria"]:
    if sc["shared_set"] == "11252984411" and sc["match"] in acct:
        acct[sc["match"]].add(norm(sc["text"]))
agneg = defaultdict(lambda: {"BROAD": set(), "PHRASE": set(), "EXACT": set()})
for n in struct["ad_group_negatives"]:
    if n["status"] == "ENABLED":
        agneg[n["ad_group_id"]][n["match"]].add(norm(n["text"]))
AGOF = {"24132507741": "202339087834", "24132507744": "202339087594",
        "24132507747": "202339087634", "24132507750": "202339087674",
        "24132507753": "200159223798"}


def blocker(term, cid):
    tw = norm(term).split()
    tws, joined = set(tw), " " + " ".join(tw) + " "
    for lab, b in (("campaign", live_neg[cid]), ("ad_group", agneg[AGOF[cid]]), ("account", acct)):
        for neg in b["BROAD"]:
            nw = neg.split()
            if nw and set(nw) <= tws:
                return (lab, "BROAD", neg)
        for neg in b["PHRASE"]:
            if (" " + neg + " ") in joined:
                return (lab, "PHRASE", neg)
        if " ".join(tw) in b["EXACT"]:
            return (lab, "EXACT", " ".join(tw))
    return None


# ---- the 75 live target places ----
places = []
targets = sorted({g["geo_id"] for g in geo["campaign_geo_criteria"]
                  if g["type"] == "LOCATION" and not g["negative"]})
for gid in targets:
    can = geo["geo_names"].get(gid, {}).get("canonical", "")
    if can:
        places.append(can.split(",")[0])
print(f"live target places: {len(places)}")

SERVICES = ["ac repair", "air conditioning repair", "hvac repair", "hvac company",
            "heating repair", "furnace repair", "hvac installation", "hvac installers",
            "hvac replacement", "ac replacement", "gas boiler repair", "boiler repair",
            "heat pump repair", "mini split installation", "ductwork installation",
            "hvac contractor", "hvac service", "emergency ac repair", "same day ac repair",
            "hvac maintenance"]

print("\n=== SWEEP A: every service x every live target place, per campaign ===")
grid_hits = []
total = 0
for cid in FIVE:
    hits = []
    for pl in places:
        for sv in SERVICES:
            for tmpl in (f"{sv} {pl} md", f"{sv} in {pl}", f"{sv} near {pl} maryland"):
                total += 1
                b = blocker(tmpl, cid)
                if b:
                    hits.append({"campaign": NAME[cid], "probe": tmpl, "layer": b[0],
                                 "match": b[1], "negative": b[2], "place": pl, "service": sv})
    grid_hits.extend(hits)
    print(f"  {NAME[cid]:<20} blocked {len(hits)} of {len(places)*len(SERVICES)*3} probes "
          f"({100*len(hits)/(len(places)*len(SERVICES)*3):.2f}%)")
print(f"  total probes evaluated: {total}")

print("\n  blocking negatives responsible (ranked):")
bl = Counter((h["layer"], h["match"], h["negative"]) for h in grid_hits)
for (lay, mt, neg), n in bl.most_common(40):
    pls = sorted({h["place"] for h in grid_hits if h["negative"] == neg and h["match"] == mt})
    svs = sorted({h["service"] for h in grid_hits if h["negative"] == neg and h["match"] == mt})
    print(f"    {lay:<9} {mt:<7} {neg!r:<32} blocks {n:<5} probes | places={len(pls)} "
          f"services={len(svs)} | sample places={pls[:6]}")

print("\n=== SWEEP B: BROAD negatives that are single common words ===")
COMMON = set("""air heat cool hot cold water gas oil new old best top good cheap free fast
quick local near me my our your the a an and or for with in on at to of is are be
home house room unit system service repair fix install replace change clean check
company contractor tech technician man guy pro expert help need want get find call
price cost quote estimate deal offer sale save money pay bill open now today
day night week month year time hour emergency urgent same next last first second
small big large full half part whole extra more less most least very much many
maryland md baltimore county city town area zone north south east west central
inc llc co corp ltd group team crew shop store center place site""".split())
broad_all = defaultdict(set)
for n in live:
    if n["match"] == "BROAD":
        broad_all[norm(n["text"])].add(n["campaign_id"])
risky = []
for txt, camps in sorted(broad_all.items()):
    w = txt.split()
    if len(w) == 1 and w[0] in COMMON:
        risky.append((txt, sorted(NAME[c] for c in camps)))
print(f"  single-word BROAD negatives that are common English/geo words: {len(risky)}")
for txt, camps in risky:
    print(f"    BROAD {txt!r:<24} on {len(camps)} campaigns: {camps}")

print(f"\n  total distinct BROAD negative texts across the five: {len(broad_all)}")
print("  single-word BROAD negatives:", sum(1 for t in broad_all if len(t.split()) == 1))
print("  multi-word BROAD negatives:", sum(1 for t in broad_all if len(t.split()) > 1))

json.dump({"grid_probe_hits": grid_hits,
           "blocking_negatives_ranked": [{"layer": k[0], "match": k[1], "negative": k[2],
                                          "n_probes": v} for k, v in bl.most_common()],
           "risky_single_word_broad": [{"text": t, "campaigns": c} for t, c in risky],
           "probe_count": total, "places": places, "services": SERVICES},
          open(EVID / "2026-09-09-geo-negative-sweep.json", "w", encoding="utf-8"),
          indent=1, default=str)
print("\nWROTE", (EVID / "2026-09-09-geo-negative-sweep.json").relative_to(ROOT))
