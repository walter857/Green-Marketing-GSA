#!/usr/bin/env python3
"""Ambient | 2026-09-30 | LOCAL two-stage negative reachability test for the maintenance ad groups. No API calls.

Reads the negatives captured in snapshots/maint-eval-2026-09-30.json (account-level list, host-campaign
negatives, host-campaign shared lists, ad-group negatives). Probes are authored phrases, never search terms.
Stage 1: is the probe blocked (BROAD = every token present; PHRASE = contiguous; EXACT = equal)?
Stage 2: could the probe match a positive keyword of the target ad group at all (PHRASE contiguous / EXACT equal)?
Only blocked AND reachable counts as a real conflict. Negative texts are printed only when every token is
in a known service vocabulary; anything else is reported as a count.
"""
from __future__ import annotations
import json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
snap = json.loads((ROOT / "clients/ambient-cooling-heating/snapshots/maint-eval-2026-09-30.json").read_text(encoding="utf-8"))
NEG = None
# negatives were not stored by the snapshot's structure() for campaign level; rebuild from ad_groups + a fresh local copy
import sys
sys.path.insert(0, str(ROOT / "scripts"))

CITIES = ["annapolis", "arbutus", "arnold", "bowie", "brooklyn park", "catonsville", "crofton", "edgewater", "elkridge",
          "ellicott city", "ferndale", "fort meade", "fulton", "gambrills", "glen burnie", "halethorpe", "hanover", "jessup",
          "laurel", "linthicum heights", "north laurel", "odenton", "parole", "pasadena", "severn", "severna park",
          "timonium", "woodlawn", "columbia", "savage", "millersville", "anne arundel county", "howard county", "maryland", "md"]
VOCAB = set("heat pump boiler boilers furnace maintenance service services servicing tune up tuneup annual inspection check "
            "cleaning clean plan plans repair replacement replace installation install installers near me cost price oil gas "
            "steam hot water residential commercial company companies contractor contractors preventive before winter "
            "ductless mini split geothermal thermostat tankless electric".split())


def probes_for(base: list[str]) -> list[str]:
    out = []
    for b in base:
        out += [b, f"{b} near me", f"{b} service", f"{b} services", f"{b} cost", f"{b} price", f"{b} company",
                f"{b} companies", f"{b} contractor", f"annual {b}", f"residential {b}", f"{b} plan", f"preventive {b}",
                f"{b} before winter"]
        out += [f"{b} {c}" for c in CITIES] + [f"{b} in {c}" for c in CITIES]
    return out


TARGETS = {
    "204129717567": dict(name="Heat Pump Maintenance", campaign="24268690038",
                         positives=[("heat pump maintenance", "PHRASE"), ("heat pump maintenance", "EXACT"), ("heat pump tune up", "EXACT")],
                         probes=probes_for(["heat pump maintenance", "heat pump tune up"]) + ["heat pump maintenance and repair"]),
    "204129718287": dict(name="Boiler Maintenance", campaign="24132507744",
                         positives=[("boiler maintenance", "PHRASE"), ("boiler maintenance", "EXACT")],
                         probes=probes_for(["boiler maintenance", "gas boiler maintenance", "hot water boiler maintenance"])
                         + ["oil boiler maintenance", "boiler maintenance and repair"]),
}


def toks(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def blocks(neg, mt, query):
    n, qt = toks(neg), toks(query)
    if not n:
        return False
    if mt == "EXACT":
        return n == qt
    if mt == "PHRASE":
        return any(qt[i:i + len(n)] == n for i in range(len(qt) - len(n) + 1))
    return set(n) <= set(qt)


def reachable(query, positives):
    qt = toks(query)
    for kw, mt in positives:
        k = toks(kw)
        if mt == "EXACT" and k == qt:
            return True
        if mt == "PHRASE" and any(qt[i:i + len(k)] == k for i in range(len(qt) - len(k) + 1)):
            return True
    return False


def main():
    # negatives by layer: pulled fresh (read-only) because campaign negatives were only counted in the snapshot print
    from ambient_0909_lib import client, q, identity_gate, E
    c = client(); identity_gate(c, verbose=False)
    layers = collections.defaultdict(list)
    acct = [(r.shared_criterion.keyword.text, E(r.shared_criterion.keyword.match_type)) for r in
            q(c, "SELECT shared_set.id, shared_criterion.keyword.text, shared_criterion.keyword.match_type FROM shared_criterion WHERE shared_set.id = 11252984411")]
    for cid in {t["campaign"] for t in TARGETS.values()}:
        layers[(cid, "account_level")] = acct
        layers[(cid, "campaign")] = [(r.campaign_criterion.keyword.text, E(r.campaign_criterion.keyword.match_type)) for r in q(c, f"""
            SELECT campaign.id, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type FROM campaign_criterion
            WHERE campaign.id = {cid} AND campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE""")]
        sets = [str(r.shared_set.id) for r in q(c, f"""SELECT campaign.id, shared_set.id, campaign_shared_set.status FROM campaign_shared_set
            WHERE campaign.id = {cid} AND campaign_shared_set.status = 'ENABLED'""")]
        for sid in sets:
            layers[(cid, f"shared_{sid}")] = [(r.shared_criterion.keyword.text, E(r.shared_criterion.keyword.match_type)) for r in
                                             q(c, f"SELECT shared_set.id, shared_criterion.keyword.text, shared_criterion.keyword.match_type FROM shared_criterion WHERE shared_set.id = {sid}")]
    result = {}
    for gid, t in TARGETS.items():
        adgrp_neg = [tuple(x) for x in snap["ad_groups"][gid]["neg"]]
        stack = [(lay, n, m) for (cid, lay), lst in layers.items() if cid == t["campaign"] for n, m in lst] + \
                [("ad_group", n, m) for n, m in adgrp_neg]
        stats = collections.Counter(); hits = collections.Counter(); named = collections.Counter()
        for p in t["probes"]:
            reach = reachable(p, t["positives"])
            b = [(lay, n, m) for lay, n, m in stack if blocks(n, m, p)]
            stats["probes"] += 1
            stats["reachable"] += reach
            if b:
                stats["blocked"] += 1
                if reach:
                    stats["REAL_CONFLICT"] += 1
                for lay, n, m in b:
                    hits[lay] += 1
                    if set(toks(n)) <= VOCAB:
                        named[(lay, n.lower(), m, "reachable" if reach else "unreachable")] += 1
                    else:
                        named[(lay, "[non-vocabulary term]", m, "reachable" if reach else "unreachable")] += 1
        result[gid] = dict(stats=dict(stats), blocked_by_layer=dict(hits),
                           blockers={" | ".join(k): v for k, v in named.items()})
        print(f"\n=== {t['name']} ({gid}) in campaign {t['campaign']} ===")
        print("  stack sizes:", {lay: len(lst) for (cid, lay), lst in layers.items() if cid == t["campaign"]}, "ad_group", len(adgrp_neg))
        print("  ", dict(stats))
        print("   blocked by layer:", dict(hits))
        for k, v in sorted(named.items(), key=lambda x: -x[1]):
            print(f"     {v:3d}  {k}")
    (ROOT / "clients/ambient-cooling-heating/snapshots/maint-neg-reach-2026-09-30.json").write_text(json.dumps(result, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
