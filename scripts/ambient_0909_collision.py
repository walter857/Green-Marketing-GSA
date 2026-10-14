#!/usr/bin/env python3
"""Reverse safety audit: do the 6,160 LIVE negatives block protected BOFU demand?
Also inspects the HOLD / NEGATIVE_CANDIDATE residue and the legacy shared lists."""
from __future__ import annotations
import sys, json, re, unicodedata
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa

struct = json.load(open(EVID / "2026-09-09-structure.json", encoding="utf-8"))
prot = json.load(open(EVID / "2026-09-09-protection-register.json", encoding="utf-8"))
verdicts = json.load(open(EVID / "2026-09-09-verdicts.json", encoding="utf-8"))
conv_all = [json.loads(l) for l in
            (EXPORTS / "search-terms-api-2026-09-09-converting-ACCOUNTWIDE.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
conv_five = [json.loads(l) for l in (EXPORTS / "search-terms-api-2026-09-09-converting.jsonl")
             .read_text(encoding="utf-8").splitlines() if l.strip()]


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


live_neg = defaultdict(lambda: {"BROAD": set(), "PHRASE": set(), "EXACT": set()})
acct_neg = {"BROAD": set(), "PHRASE": set(), "EXACT": set()}
for n in struct["campaign_negatives"]:
    if n["status"] == "ENABLED" and n["campaign_id"] in FIVE:
        live_neg[n["campaign_id"]][n["match"]].add(norm(n["text"]))
for n in struct["ad_group_negatives"]:
    if n["status"] == "ENABLED" and n["campaign_id"] in FIVE:
        live_neg[("AG", n["ad_group_id"])][n["match"]].add(norm(n["text"]))
for sc in struct["shared_criteria"]:
    if sc["shared_set"] == "11252984411":
        acct_neg[sc["match"]].add(norm(sc["text"]))

AGOF = {"24132507741": "202339087834", "24132507744": "202339087594",
        "24132507747": "202339087634", "24132507750": "202339087674",
        "24132507753": "200159223798"}


def blocked_by(term, buckets):
    tw = norm(term).split()
    tws, joined = set(tw), " " + " ".join(tw) + " "
    for b in buckets:
        for neg in b["BROAD"]:
            nw = neg.split()
            if nw and set(nw) <= tws:
                return ("BROAD", neg)
        for neg in b["PHRASE"]:
            if (" " + neg + " ") in joined:
                return ("PHRASE", neg)
        for neg in b["EXACT"]:
            if neg == " ".join(tw):
                return ("EXACT", neg)
    return None


print("=== TEST 1: 67 BOFU PROBES vs LIVE NEGATIVES, per campaign ===")
hits = []
for cid in FIVE:
    bk = [live_neg[cid], live_neg[("AG", AGOF[cid])], acct_neg]
    bad = []
    for p in prot["bofu_probes"]:
        b = blocked_by(p, bk)
        if b:
            bad.append((p, b))
    print(f"  {NAME[cid]:<20} probes blocked: {len(bad)} / {len(prot['bofu_probes'])}")
    for p, b in bad:
        print(f"      BLOCKED  probe={p!r}  by {b[0]} negative {b[1]!r}")
        hits.append({"campaign": NAME[cid], "probe": p, "match": b[0], "negative": b[1]})

print("\n=== TEST 2: 10 LIVE POSITIVE KEYWORDS vs LIVE NEGATIVES ===")
pk = [k for k in struct["positive_keywords"] if k["status"] == "ENABLED"
      and k["ad_group_status"] == "ENABLED" and k["campaign_status"] == "ENABLED"]
pos_hits = []
for k in pk:
    bk = [live_neg[k["campaign_id"]], live_neg[("AG", k["ad_group_id"])], acct_neg]
    b = blocked_by(k["text"], bk)
    flag = f"BLOCKED by {b[0]} {b[1]!r}" if b else "clear"
    print(f"  {NAME[k['campaign_id']]:<20} {k['match']:<7} [{k['text']}] -> {flag}")
    if b:
        pos_hits.append({"campaign": NAME[k["campaign_id"]], "keyword": k["text"],
                         "match": b[0], "negative": b[1]})

print("\n=== TEST 3: 304 ACCOUNT-WIDE CONVERTING TERMS vs the five campaigns' negatives ===")
conv_terms = sorted({t["term"] for t in conv_all} | {t["term"] for t in conv_five})
convmeta = defaultdict(lambda: {"conversions": 0.0, "all_conversions": 0.0, "campaigns": set()})
for t in conv_all:
    convmeta[t["term"]]["conversions"] += t["conversions"]
    convmeta[t["term"]]["all_conversions"] += t["all_conversions"]
    convmeta[t["term"]]["campaigns"].add(t["camp_name"][:34])
for t in conv_five:
    convmeta[t["term"]]["conversions"] += t["conversions"]
    convmeta[t["term"]]["all_conversions"] += t["all_conversions"]
    convmeta[t["term"]]["campaigns"].add(NAME[t["camp"]])

harm = []
for cid in FIVE:
    bk = [live_neg[cid], live_neg[("AG", AGOF[cid])], acct_neg]
    blocked = []
    for t in conv_terms:
        b = blocked_by(t, bk)
        if b:
            blocked.append((t, b))
    print(f"  {NAME[cid]:<20} converting terms blocked: {len(blocked)} / {len(conv_terms)}")
    for t, b in blocked:
        m = convmeta[t]
        harm.append({"campaign": NAME[cid], "term": t, "match": b[0], "negative": b[1],
                     "conversions": round(m["conversions"], 2),
                     "all_conversions": round(m["all_conversions"], 2),
                     "seen_in": sorted(m["campaigns"])})

print(f"\n  TOTAL (campaign, converting-term) collisions: {len(harm)}")
print("  distinct converting terms affected:", len({h['term'] for h in harm}))
print("  distinct blocking negatives:", len({(h['match'], h['negative']) for h in harm}))
print("\n  --- collisions ranked by primary conversions the term produced ---")
for h in sorted(harm, key=lambda h: (-h["conversions"], -h["all_conversions"]))[:60]:
    print(f"    {h['campaign']:<20} conv={h['conversions']:<5} allconv={h['all_conversions']:<6} "
          f"{h['match']:<7} neg={h['negative']!r:<34} term={h['term']!r}")

print("\n  --- blocking negatives ranked by how many converting terms each kills ---")
bl = Counter((h["match"], h["negative"]) for h in harm)
for (mt, neg), n in bl.most_common(40):
    terms_hit = {h["term"] for h in harm if h["negative"] == neg and h["match"] == mt}
    conv_hit = sum(convmeta[t]["conversions"] for t in terms_hit)
    ac_hit = sum(convmeta[t]["all_conversions"] for t in terms_hit)
    camps = sorted({h["campaign"] for h in harm if h["negative"] == neg and h["match"] == mt})
    print(f"    {mt:<7} {neg!r:<36} kills {len(terms_hit):<3} converting terms "
          f"(conv={round(conv_hit,1)}, allconv={round(ac_hit,1)}) in {camps}")

print("\n=== TEST 4: LEGACY SHARED LISTS - would attaching them break the five? ===")
sets_by_id = {s["id"]: s for s in struct["shared_sets"]}
members = defaultdict(lambda: {"BROAD": set(), "PHRASE": set(), "EXACT": set()})
for sc in struct["shared_criteria"]:
    if sc["match"] not in ("BROAD", "PHRASE", "EXACT") or not sc["text"]:
        continue
    members[sc["shared_set"]][sc["match"]].add(norm(sc["text"]))
for sid, mm in sorted(members.items()):
    s = sets_by_id.get(sid, {})
    if s.get("type") != "NEGATIVE_KEYWORDS" or s.get("status") != "ENABLED":
        continue
    probes_blocked = [p for p in prot["bofu_probes"] if blocked_by(p, [mm])]
    convs_blocked = [t for t in conv_terms if blocked_by(t, [mm])]
    pos_blocked = [k["text"] for k in pk if blocked_by(k["text"], [mm])]
    print(f"  set {sid} {s.get('name','')[:32]:<34} members={sum(len(v) for v in mm.values()):<5} "
          f"BOFU-probes-blocked={len(probes_blocked):<3} converting-blocked={len(convs_blocked):<4} "
          f"live-positives-blocked={len(pos_blocked)}")
    if pos_blocked:
        print(f"      would block LIVE POSITIVE keywords: {sorted(set(pos_blocked))}")

json.dump({"bofu_probe_collisions": hits, "positive_keyword_collisions": pos_hits,
           "converting_term_collisions": harm,
           "blocking_negatives_ranked": [{"match": k[0], "negative": k[1], "n_terms": v}
                                         for k, v in bl.most_common()]},
          open(EVID / "2026-09-09-collision-audit.json", "w", encoding="utf-8"),
          indent=1, default=str)
print("\nWROTE", (EVID / "2026-09-09-collision-audit.json").relative_to(ROOT))

print("\n=== TEST 5: THE RESIDUE (HOLD + NEGATIVE_CANDIDATE) ===")
res = [r for r in verdicts if r["verdict"] in ("HOLD", "NEGATIVE_CANDIDATE")]
for r in sorted(res, key=lambda r: -r["cost"]):
    print(f"  {r['verdict']:<20} {NAME[r['camp']]:<18} impr={r['impressions']:<4} "
          f"clk={r['clicks']:<3} ${r['cost']:<8} sig={r['signals']} :: {r['term']!r}")
