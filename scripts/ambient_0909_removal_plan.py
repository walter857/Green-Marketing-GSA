#!/usr/bin/env python3
"""Split the 80 colliding live negatives into HARMFUL (remove) vs INTENTIONAL (keep),
and prove sibling-campaign eligibility for every cross-negatived converter."""
from __future__ import annotations
import sys, json, re, unicodedata, csv
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa

struct = json.load(open(EVID / "2026-09-09-structure.json", encoding="utf-8"))
coll = json.load(open(EVID / "2026-09-09-collision-audit.json", encoding="utf-8"))
geo = json.load(open(EVID / "2026-09-09-geo-targets.json", encoding="utf-8"))
prot = json.load(open(EVID / "2026-09-09-protection-register.json", encoding="utf-8"))


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ---- Confirmed Ambient service catalogue (work order + client.yaml) ----
SERVICE_TOKENS = {
    "ac", "hvac", "air", "conditioner", "conditioning", "heating", "heat", "heater", "furnace",
    "boiler", "boilers", "duct", "ducts", "ductwork", "mini", "split", "ductless", "geothermal",
    "thermostat", "thermostats", "humidifier", "dehumidifier", "tankless", "water", "condenser",
    "compressor", "coil", "refrigerant", "cooling", "central", "pump", "handler", "chiller",
    "radiator", "maintenance", "install", "installation", "installer", "installers", "repair",
    "replacement", "replace", "service", "servicing", "tune",
}
MANUFACTURERS = {"lennox", "carrier", "trane", "goodman", "daikin", "rheem", "amana", "bosch",
                 "mitsubishi", "armstrong", "burnham", "spacepak", "aciq", "york",
                 "american standard", "bryant", "ruud", "navien", "rinnai", "weil", "mclain"}
# Generic words the operating instructions forbid broad-negativing
FORBIDDEN_BROAD = {"al", "american", "mr", "ambient", "cheap", "affordable", "emergency", "cost",
                   "price", "pricing", "company", "companies", "contractor", "technician",
                   "dealer", "repair", "replace", "replacement", "installation", "install",
                   "service", "commercial", "residential", "maryland", "md", "near", "me",
                   "local", "best", "hire", "quote", "free", "licensed", "insured", "estimate",
                   "same", "day", "open", "now", "24", "hour"}
MD_PLACES = set(prot["md_place_tokens"])

harm = coll["converting_term_collisions"]
probe = coll["bofu_probe_collisions"]

# every distinct blocking negative, with what it caught
negs = defaultdict(lambda: {"terms": set(), "probes": set(), "campaigns": set(),
                            "conv": 0.0, "allconv": 0.0})
for h in harm:
    k = (h["match"], h["negative"])
    negs[k]["terms"].add(h["term"])
    negs[k]["campaigns"].add(h["campaign"])
for h in probe:
    k = (h["match"], h["negative"])
    negs[k]["probes"].add(h["probe"])
    negs[k]["campaigns"].add(h["campaign"])
# conversion weight per negative (dedup by term)
convmeta = {}
for h in harm:
    convmeta[h["term"]] = (h["conversions"], h["all_conversions"])
for k, v in negs.items():
    v["conv"] = round(sum(convmeta.get(t, (0, 0))[0] for t in v["terms"]), 2)
    v["allconv"] = round(sum(convmeta.get(t, (0, 0))[1] for t in v["terms"]), 2)


def verdict(match, neg):
    nw = norm(neg).split()
    nset = set(nw)
    # 1. blocks a supported manufacturer outright
    if nset & MANUFACTURERS or norm(neg) in MANUFACTURERS:
        return "REMOVE", "supported manufacturer token; blocks manufacturer+service intent"
    # 2. broad-negatives a word the operating instructions forbid
    if match == "BROAD" and nset & FORBIDDEN_BROAD:
        return "REMOVE", ("BROAD negative on a word the Green Marketing rules forbid "
                          f"({sorted(nset & FORBIDDEN_BROAD)})")
    if match == "PHRASE" and len(nw) == 1 and nw[0] in FORBIDDEN_BROAD:
        return "REMOVE", f"single-word PHRASE negative on a forbidden generic ({nw[0]})"
    # 3. blocks a confirmed Ambient service with no company-name component
    if nset <= SERVICE_TOKENS and nset:
        return "REMOVE", "blocks a confirmed Ambient service with no competitor component"
    if match in ("PHRASE", "BROAD") and len(nw) == 1 and nw[0] in SERVICE_TOKENS:
        return "REMOVE", f"single-token negative on confirmed service word '{nw[0]}'"
    # 4. in-footprint Maryland place
    if nset & MD_PLACES and not (nset - MD_PLACES - SERVICE_TOKENS):
        return "REMOVE", "names a live Maryland target location"
    # 5. multi-word service phrase that is entirely service vocabulary
    if all(w in SERVICE_TOKENS or w in ("near", "me", "my", "a", "the", "in", "and", "for")
           for w in nw) and any(w in SERVICE_TOKENS for w in nw):
        return "ROUTING", "pure service phrase - intentional cross-campaign routing, verify sibling"
    return "KEEP", "competitor / entity / out-of-area token - intentional"


rows = []
for (match, neg), v in sorted(negs.items(), key=lambda kv: (-kv[1]["conv"], -kv[1]["allconv"])):
    vd, why = verdict(match, neg)
    rows.append({"match": match, "negative": neg, "verdict": vd, "why": why,
                 "n_converting_terms": len(v["terms"]), "n_bofu_probes": len(v["probes"]),
                 "conversions_at_risk": v["conv"], "all_conversions_at_risk": v["allconv"],
                 "campaigns": sorted(v["campaigns"]),
                 "sample_probes": sorted(v["probes"])})

print("=== 80 COLLIDING LIVE NEGATIVES, TRIAGED ===")
print(dict(Counter(r["verdict"] for r in rows)))
for vd in ("REMOVE", "ROUTING", "KEEP"):
    sub = [r for r in rows if r["verdict"] == vd]
    print(f"\n--- {vd} ({len(sub)}) ---")
    for r in sub:
        print(f"  {r['match']:<7} {r['negative']!r:<36} convTerms={r['n_converting_terms']:<3} "
              f"probes={r['n_bofu_probes']:<3} conv={r['conversions_at_risk']:<5} "
              f"allconv={r['all_conversions_at_risk']:<6} camps={len(r['campaigns'])}  {r['why']}")

# ---------- resolve REMOVE / ROUTING rows to real criterion IDs ----------
live = [n for n in struct["campaign_negatives"]
        if n["status"] == "ENABLED" and n["campaign_id"] in FIVE]
bykey = defaultdict(list)
for n in live:
    bykey[(n["match"], norm(n["text"]))].append(n)

ops = []
for r in rows:
    if r["verdict"] != "REMOVE":
        continue
    for n in bykey.get((r["match"], norm(r["negative"])), []):
        ops.append({"op": "remove", "resource": "campaign_criterion",
                    "resource_name": f"customers/{CID}/campaignCriteria/"
                                     f"{n['campaign_id']}~{n['criterion_id']}",
                    "campaign_id": n["campaign_id"], "campaign": NAME[n["campaign_id"]],
                    "criterion_id": n["criterion_id"], "match": n["match"], "text": n["text"],
                    "reason": r["why"], "conversions_at_risk": r["conversions_at_risk"],
                    "all_conversions_at_risk": r["all_conversions_at_risk"],
                    "bofu_probes_unblocked": r["sample_probes"]})

print(f"\n=== REMOVAL OPERATIONS RESOLVED TO LIVE CRITERION IDs: {len(ops)} ===")
print("  by campaign:", dict(Counter(o["campaign"] for o in ops)))
print("  by match:", dict(Counter(o["match"] for o in ops)))
print("  distinct texts:", len({(o['match'], o['text']) for o in ops}))

# ---------- sibling-eligibility proof for ROUTING rows ----------
print("\n=== SIBLING-ELIGIBILITY PROOF FOR CROSS-CAMPAIGN ROUTING NEGATIVES ===")
live_neg = defaultdict(lambda: {"BROAD": set(), "PHRASE": set(), "EXACT": set()})
for n in live:
    live_neg[n["campaign_id"]][n["match"]].add(norm(n["text"]))
acct = {"BROAD": set(), "PHRASE": set(), "EXACT": set()}
for sc in struct["shared_criteria"]:
    if sc["shared_set"] == "11252984411" and sc["match"] in acct:
        acct[sc["match"]].add(norm(sc["text"]))
AGOF = {"24132507741": "202339087834", "24132507744": "202339087594",
        "24132507747": "202339087634", "24132507750": "202339087674",
        "24132507753": "200159223798"}
agneg = defaultdict(lambda: {"BROAD": set(), "PHRASE": set(), "EXACT": set()})
for n in struct["ad_group_negatives"]:
    if n["status"] == "ENABLED":
        agneg[n["ad_group_id"]][n["match"]].add(norm(n["text"]))


def blocked(term, cid):
    tw = norm(term).split()
    tws, joined = set(tw), " " + " ".join(tw) + " "
    for b in (live_neg[cid], agneg[AGOF[cid]], acct):
        for neg in b["BROAD"]:
            if set(neg.split()) <= tws and neg.split():
                return True
        for neg in b["PHRASE"]:
            if (" " + neg + " ") in joined:
                return True
        if " ".join(tw) in b["EXACT"]:
            return True
    return False


routing_terms = sorted({t for r in rows if r["verdict"] == "ROUTING"
                        for h in harm if h["negative"] == r["negative"]
                        and h["match"] == r["match"] for t in [h["term"]]})
orphans = []
print(f"  cross-negatived converting terms to check: {len(routing_terms)}")
for t in routing_terms:
    free = [NAME[c] for c in FIVE if not blocked(t, c)]
    conv = convmeta.get(t, (0, 0))
    status = "OK" if free else "ORPHANED"
    if not free:
        orphans.append({"term": t, "conversions": conv[0], "all_conversions": conv[1]})
    print(f"    [{status:<9}] conv={conv[0]:<4} allconv={conv[1]:<5} servable_in={free}  {t!r}")
print(f"\n  ORPHANED converting terms (blocked in ALL FIVE campaigns): {len(orphans)}")

# every converting term, orphan check across the whole protected register
allorph = []
for t in sorted({h["term"] for h in harm}):
    free = [NAME[c] for c in FIVE if not blocked(t, c)]
    if not free:
        allorph.append({"term": t, "conversions": convmeta.get(t, (0, 0))[0],
                        "all_conversions": convmeta.get(t, (0, 0))[1]})
print(f"  ORPHANED across ALL 81 colliding converting terms: {len(allorph)}")
print("  of which produced >=1 PRIMARY conversion:",
      sum(1 for o in allorph if o["conversions"] >= 1))

json.dump({"triage": rows, "removal_operations": ops, "orphaned_converting_terms": allorph},
          open(EVID / "2026-09-09-removal-plan-analysis.json", "w", encoding="utf-8"),
          indent=1, default=str)
with (EVID / "2026-09-09-negative-triage.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["match", "negative", "verdict", "why", "n_converting_terms", "n_bofu_probes",
                "conversions_at_risk", "all_conversions_at_risk", "campaigns"])
    for r in rows:
        w.writerow([r["match"], r["negative"], r["verdict"], r["why"], r["n_converting_terms"],
                    r["n_bofu_probes"], r["conversions_at_risk"], r["all_conversions_at_risk"],
                    "|".join(r["campaigns"])])
print("\nWROTE", (EVID / "2026-09-09-removal-plan-analysis.json").relative_to(ROOT))
print("WROTE", (EVID / "2026-09-09-negative-triage.csv").relative_to(ROOT))
