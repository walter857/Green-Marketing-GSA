#!/usr/bin/env python3
"""Ambient | 2026-10-01 | Reverse (over-blocking) probe test + hypothetical EXACT candidates + boiler assessment. No API calls.

Uses the negative stacks read this session (snapshot + routing context). For every probe and every relevant ad group:
blocked? (which layer/negative) and literally reachable? (a PHRASE/EXACT positive contains/equals it). Only a probe that is
BOTH blocked and reachable is a real loss; blocked-but-routed-elsewhere is reported as routing.
Writes snapshots/probe-test-2026-10-01.json.
"""
from __future__ import annotations
import json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CD = ROOT / "clients" / "ambient-cooling-heating"
S = json.loads((CD / "snapshots" / "snapshot-2026-10-01.json").read_text(encoding="utf-8"))
R = json.loads((CD / "snapshots" / "routing-context-2026-10-01.json").read_text(encoding="utf-8"))
members, sets = S["shared_set_members"], S["shared_sets"]
RG = R["ad_groups"]


def norm(t):
    t = t.lower().replace("’", "'")
    return re.sub(r"[^\w&'+\- ]", " ", t).split()


def blocks(n_text, match, q):
    n = norm(n_text)
    if match == "EXACT":
        return n == q
    if match == "PHRASE":
        return any(q[i:i + len(n)] == n for i in range(len(q) - len(n) + 1))
    return all(t in q for t in n)


acct = [("account-level", m["text"], m["match"]) for sid in S["account_level_negative_sets"] for m in members.get(sid, [])]
att = collections.defaultdict(list)
for a in R["attachments"]:
    if a["status"] == "ENABLED":
        att[a["campaign_id"]] += [(f"shared {a['set_id']}", m["text"], m["match"]) for m in members.get(a["set_id"], [])]
cn = collections.defaultdict(list)
for x in R["campaign_negatives"]:
    cn[x["campaign_id"]].append(("campaign", x["text"], x["match"]))
an = collections.defaultdict(list)
pos = collections.defaultdict(list)
for x in R["keywords"]:
    (an if x["negative"] else pos)[x["ad_group_id"]].append(x if not x["negative"] else ("ad group", x["text"], x["match"]))


def stack(gid):
    c = RG[gid]["campaign_id"]
    return acct + att[c] + cn[c] + an[gid]


def test(gid, probe, include_paused=True):
    q = norm(probe)
    hit = [f"{l}: {m} [{t}]" for (l, t, m) in stack(gid) if blocks(t, m, q)]
    reach = []
    for k in pos[gid]:
        if k["status"] != "ENABLED" and not include_paused:
            continue
        n = norm(k["text"])
        if (k["match"] == "EXACT" and n == q) or (k["match"] == "PHRASE" and any(q[i:i + len(n)] == n for i in range(len(q) - len(n) + 1))):
            reach.append(f"{k['match']} {k['text']}{'' if k['status'] == 'ENABLED' else ' (PAUSED)'}")
    return hit, reach


def gid_by_name(name):
    return next(g for g, v in RG.items() if v["name"] == f"SKAG | {name}")


GROUPS = {n: gid_by_name(n) for n in ("Heating Repair", "Furnace Repair", "Gas Furnace Repair", "Electric Furnace Repair", "No Heat Repair",
                                       "Emergency Heating Repair", "Geothermal Heat Pump", "Boiler Repair", "Gas Boiler Repair", "Heat Pump Repair",
                                       "Heat Pump Installation", "Heat Pump Replacement", "Furnace Replacement", "Heating Installation")}
PROBES = {
    "repair": ["heating repair", "heating repair near me", "heating repair cost", "heating repair price", "heating repair quote", "best heating repair near me",
               "local heating repair", "hire heating repair", "heating repair severn md", "heating repair columbia md", "heater repair near me",
               "furnace repair", "furnace repair near me", "furnace repair cost", "furnace repair price", "furnace repair quote", "best furnace repair near me",
               "local furnace repair", "furnace repair severna park", "furnace repair glen burnie", "furnace not working", "gas furnace repair near me",
               "electric furnace repair near me", "no heat repair near me", "no heat repair", "carrier furnace repair", "trane furnace repair",
               "lennox furnace repair", "goodman furnace repair", "rheem furnace repair", "bryant furnace repair", "american standard furnace repair",
               "york furnace repair", "amana furnace repair", "ruud furnace repair", "furnace repair free estimate", "licensed furnace repair",
               "commercial furnace repair", "residential heating repair", "heating repair service"],
    "emergency": ["emergency heating repair", "emergency heating repair near me", "emergency furnace repair", "emergency furnace repair near me",
                  "emergency heater repair", "emergency heat repair", "emergency heating repair cost", "emergency furnace repair severn",
                  "emergency gas furnace repair", "emergency heating repair columbia md", "24 hour heating repair", "same day furnace repair",
                  "emergency no heat repair"],
    "geothermal": ["geothermal heat pump", "geothermal heat pump installation", "geothermal heat pump installers near me", "geothermal heat pump cost",
                   "geothermal heat pump price", "geothermal heat pump near me", "geothermal heat pump replacement", "geothermal heat pump repair",
                   "geothermal heat pump repair near me", "geothermal heat pump service", "geothermal heat pump maintenance", "geothermal heating",
                   "geothermal heating and cooling", "geothermal heating installation", "geothermal installation", "geothermal installation cost",
                   "geothermal hvac", "geothermal system installation", "geothermal heat pump contractor", "geothermal heat pump annapolis",
                   "geothermal heat pump rebate", "geothermal heat pump tax credit", "ground source heat pump", "geothermal heat pump quote"],
    "boiler": ["boiler repair", "boiler repair near me", "boiler repair in severn", "boiler repair cost", "boiler", "how to repair a boiler yourself",
               "boiler repair jobs", "gas boiler repair", "oil boiler repair", "boiler repair severn md"],
}
out = {"probes": {}, "summary": {}}
for fam, probes in PROBES.items():
    rows = []
    for p in probes:
        per = {}
        for name, gid in GROUPS.items():
            hit, reach = test(gid, p)
            if hit or reach:
                per[name] = dict(blocked_by=hit, reachable_via=reach, real_loss=bool(hit and reach), serves=bool(reach and not hit))
        servers = [n for n, v in per.items() if v["serves"]]
        losses = [n for n, v in per.items() if v["real_loss"]]
        rows.append(dict(probe=p, literally_served_by=servers, blocked_where_reachable=losses, detail=per))
    out["probes"][fam] = rows
    print(f"\n== {fam}")
    for r in rows:
        print(f"  {r['probe']:42s} serves={r['literally_served_by'] or '-'} | blocked-where-reachable={[(n, r['detail'][n]['blocked_by'][:2]) for n in r['blocked_where_reachable']] or '-'}")

# manufacturer / never-negate words present in any layer reaching the in-scope groups?
NEVER = ["near me", "quote", "price", "pricing", "cost", "best", "hire", "local", "emergency", "repair", "heating", "furnace", "geothermal", "service"]
for name in ("Heating Repair", "Furnace Repair", "Emergency Heating Repair", "Geothermal Heat Pump"):
    gid = GROUPS[name]
    found = [(l, m, t) for (l, t, m) in stack(gid) if " ".join(norm(t)) in NEVER]
    out["summary"][f"never_negate_words_in_stack|{name}"] = found
    print(f"never-negate words negated in {name} stack: {found}")

# ---------- hypothetical EXACT candidates (max 25) ----------
HYPO = [
    # (query, scope, basis, label)
    ("furnace repair jobs", "campaign 24257819463", "employment; campaign already negates PHRASE 'hvac jobs' but not 'furnace ... jobs'", "generic hypothesis"),
    ("heating repair jobs", "campaign 24257819463", "employment", "generic hypothesis"),
    ("how to repair a furnace yourself", "campaign 24257819463", "DIY", "generic hypothesis"),
    ("buy furnace control board", "campaign 24257819463", "parts-only shopping; campaign negates 'furnace parts' not 'control board'", "generic hypothesis"),
    ("car heater repair near me", "campaign 24257819463", "vehicle heater; observed pattern: webasto heater repair near me (09-30)", "pattern-based"),
    ("webasto heater repair", "campaign 24257819463", "vehicle heater; observed sibling 'webasto heater repair near me'", "pattern-based"),
    ("rv furnace repair", "campaign 24257819463", "vehicle (RV) furnace; extends the observed vehicle-heater leak", "pattern-based"),
    ("pellet stove repair", "campaign 24257819463", "observed: 3 pellet-stove repair/service queries 09-23..09-29", "pattern-based"),
    ("pellet stove service", "campaign 24257819463", "observed: 'pellet stove service near me' 09-29", "pattern-based"),
    ("wood stove repair near me", "campaign 24257819463", "solid-fuel stove, same family as observed pellet stove leak", "pattern-based"),
    ("oil furnace repair near me", "campaign 24257819463", "Oil OUT of scope (owner 2026-09-21); observed 6 oil queries", "pattern-based"),
    ("oil burner repair", "campaign 24257819463", "Oil OUT of scope; observed 'oil burner service near me'", "pattern-based"),
    ("oil furnace service near me", "campaign 24257819463", "Oil OUT of scope; observed 'oil furnace cleaning service near me'", "pattern-based"),
    ("space heater repair", "campaign 24257819463", "portable heater, not a home heating system", "generic hypothesis"),
    ("air conditioner repair", "campaign 24257819463", "observed 18 AC-only queries; campaign negates 'ac repair' + 'air conditioning repair' but not 'air conditioner repair'", "pattern-based"),
    ("ac repair near me", "campaign 24257819463", "COVERED already by campaign PHRASE 'ac repair' - listed to show it is NOT needed", "coverage check"),
    ("heat pump repair", "Heating Repair 204129717007 / Furnace Repair", "COVERED by ad-group PHRASE 'heat pump' (routes to Heat Pump Repair) - NOT needed", "coverage check"),
    ("furnace repair technician salary", "campaign 24257819463", "employment", "generic hypothesis"),
    ("furnace error code 33", "campaign 24257819463", "fault-code lookup; observed 7 fault-code queries but kept on MONITOR (hire risk)", "pattern-based - NOT recommended"),
    ("webasto repair near me", "campaign 24257819463", "vehicle heater brand; observed 'webasto heater repair near me'", "pattern-based"),
    ("diesel heater repair", "campaign 24257819463", "vehicle/marine diesel heater; extends the observed webasto leak", "pattern-based"),
    ("boat heater repair", "campaign 24257819463", "marine heater", "generic hypothesis"),
    ("pellet stove repair near me", "campaign 24257819463", "OBSERVED already (candidate list) - listed to show no duplicate is needed", "coverage check"),
    ("pellet stove technician", "campaign 24257819463", "pellet stove family", "pattern-based"),
    ("oil furnace repair", "campaign 24257819463", "Oil OUT of scope", "pattern-based"),
    ("oil burner service", "campaign 24257819463", "Oil OUT of scope; observed 'oil burner service near me'", "pattern-based"),
    ("oil heater repair", "campaign 24257819463", "Oil OUT of scope; observed 'oil heater service'", "pattern-based"),
    ("air conditioner repair company near me", "campaign 24257819463", "observed 'air conditioner repair company' (10-01)", "pattern-based"),
    ("ac unit repair", "campaign 24257819463", "observed 'ac unit repair near me'", "pattern-based"),
    ("fix air conditioner", "campaign 24257819463", "observed 'fix air conditioner near me'", "pattern-based"),
    ("hvac technician jobs", "campaign 24257819463", "employment", "generic hypothesis"),
    ("furnace parts near me", "campaign 24257819463", "parts-only shopping", "generic hypothesis"),
    ("furnace manual", "campaign 24257819463", "manual lookup", "generic hypothesis"),
    ("hvac certification near me", "campaign 24257819463", "training/certification", "generic hypothesis"),
]
hyp = []
for qtext, scope, basis, label in HYPO:
    hits = {n: test(GROUPS[n], qtext) for n in ("Heating Repair", "Furnace Repair")}
    covered = all(h[0] for h in hits.values())
    hyp.append(dict(query=qtext, display=f"[{qtext}]", match_type="EXACT", scope=scope, basis=basis, label=label,
                    covered_now={n: h[0][:2] for n, h in hits.items()}, already_covered_everywhere=covered,
                    literally_reachable={n: h[1] for n, h in hits.items()}))
out["hypothetical"] = hyp
print("\n== hypothetical")
for h in hyp:
    print(f"  {h['query']:38s} covered_everywhere={h['already_covered_everywhere']} covered={ {k: v for k, v in h['covered_now'].items() if v} } reach={ {k: v for k, v in h['literally_reachable'].items() if v} }")
(CD / "snapshots" / "probe-test-2026-10-01.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
