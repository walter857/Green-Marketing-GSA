#!/usr/bin/env python3
"""Ambient | 2026-10-05 | Working list for manual intent review of every visible repair search term. No API calls.

Reads snapshots/repair-read-2026-10-05.json + exports/repair-search-terms-2026-10-05.jsonl and the 2026-10-02 verdict CSV.
Coverage uses every layer live now (account BROAD list, attached shared lists, campaign negatives incl. NEG-EXACT-2,
ad-group negatives). Google: negatives match casing/misspellings only, never close variants, plurals or reorderings.
Prints one line per distinct term: totals, windows, keyword relationship, coverage, prior verdict. HVAC corpus (raw terms
are in the deliverable by request, recorded in the work order).
"""
from __future__ import annotations
import csv, json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CD = ROOT / "clients" / "ambient-cooling-heating"
S = json.loads((CD / "snapshots" / "repair-read-2026-10-05.json").read_text(encoding="utf-8"))
ROWS = [json.loads(l) for l in (CD / "exports" / "repair-search-terms-2026-10-05.jsonl").read_text(encoding="utf-8").splitlines()]
AG = S["ad_groups"]


def norm(t):
    t = t.lower().replace("’", "'")
    return re.sub(r"[^\w&'+\- ]", " ", t).split()


def blocks(n_text, match, q):
    n = norm(n_text)
    if not n:
        return False
    if match == "EXACT":
        return n == q
    if match == "PHRASE":
        return any(q[i:i + len(n)] == n for i in range(len(q) - len(n) + 1))
    return all(t in q for t in n)


layers = []
for sid in S["account_level_sets"]:
    layers += [("acct", m["text"], m["match"], None) for m in S["shared_set_members"].get(sid, [])]
for a in S["attachments"]:
    if a["status"] == "ENABLED":
        layers += [(f"shared{a['set'][-4:]}", m["text"], m["match"], None) for m in S["shared_set_members"].get(a["set"], [])]
layers += [("camp", x["text"], x["match"], None) for x in S["campaign_criteria"].get("KEYWORD", []) if x["neg"]]
layers += [("ag", k["text"], k["match"], k["ad_group"]) for k in S["keywords"] if k["negative"]]


def covering(gid, term):
    q = norm(term)
    return [f"{l}:{m[0]}[{t}]" for (l, t, m, g) in layers if (g is None or g == gid) and blocks(t, m, q)]


prior = {}
p = CD / "exports" / "search-term-verdicts-2026-10-02.csv"
for r in csv.DictReader(p.open(encoding="utf-8")):
    if r["campaign_id"] == "24257819463":
        prior[r["search_term"]] = (r["bucket"], r["verdict"])

agg = collections.defaultdict(lambda: collections.defaultdict(float))
info = collections.defaultdict(set)
for r in ROWS:
    t = r["term"]
    for w, (a, b) in {"tot": ("2026-09-17", "2026-10-04"), "base": ("2026-09-24", "2026-09-30"), "test": ("2026-10-01", "2026-10-02")}.items():
        if a <= r["date"] <= b:
            agg[t][w + "_i"] += r["impr"]; agg[t][w + "_c"] += r["clicks"]; agg[t][w + "_$"] += r["cost"]
    info[t].add(f"{AG.get(r['ad_group'], {}).get('name', r['ad_group'])[7:12]}/{r['kw_text']}/{r['kw_match'][:2]}/{r['st_match'].replace('NEAR_', 'N')[:6]}")
    info[t + "#dates"].add(r["date"][5:])
    info[t + "#ag"].add(r["ad_group"])
for t in sorted(agg, key=lambda t: (-agg[t]["tot_$"], -agg[t]["tot_i"], t)):
    v = agg[t]
    cov = sorted({c for g in info[t + "#ag"] for c in covering(g, t)})
    print(f"{v['tot_i']:4.0f}i {v['tot_c']:2.0f}c ${v['tot_$']:6.2f} | b {v['base_i']:3.0f}/{v['base_c']:.0f}/${v['base_$']:.0f} t {v['test_i']:3.0f}/{v['test_c']:.0f}/${v['test_$']:.0f} | "
          f"{t} | {';'.join(sorted(info[t]))[:70]} | last {max(info[t + '#dates'])} | COV {','.join(cov)[:60] or '-'} | prior {prior.get(t, ('-', '-'))[0]}")
