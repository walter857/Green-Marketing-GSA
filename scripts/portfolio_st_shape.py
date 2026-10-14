#!/usr/bin/env python3
"""Aggregate shape of the search-term corpus. Counts only, never raw terms."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "reports" / "st-corpus"

SLUGS = ["pro-green-austin", "softwind-power-washing", "ambient-cooling-heating"]


def main() -> int:
    for slug in SLUGS:
        d = json.loads((CORPUS / (slug + "-corpus.json")).read_text(encoding="utf-8"))
        print("=" * 78)
        print("{}  ({} / {})".format(slug, d["account_name"], d["customer_id"]))
        print("=" * 78)

        live_c = {c["id"]: c for c in d["campaigns"] if c["status"] == "ENABLED"}
        live_ag = {a["id"]: a for a in d["ad_groups"]
                   if a["status"] == "ENABLED" and a["campaign_id"] in live_c}

        print("LIVE CAMPAIGNS ({}):".format(len(live_c)))
        for c in sorted(live_c.values(), key=lambda x: x["name"]):
            ags = [a for a in live_ag.values() if a["campaign_id"] == c["id"]]
            print("  {:<38} id={} budget=${:.2f} ad_groups={}".format(
                c["name"][:38], c["id"], c["daily_budget"], len(ags)))

        # existing negatives by scope
        cneg_live = [n for n in d["campaign_negatives"] if n["campaign_id"] in live_c]
        agneg_live = [n for n in d["ad_group_negatives"] if n["ad_group_id"] in live_ag]
        acct_sets = [s for s in d["shared_sets"] if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"]
        acct_ids = {s["id"] for s in acct_sets}
        acct_members = [m for m in d["shared_members"] if m["shared_set_id"] in acct_ids]
        links_live = [l for l in d["campaign_shared_sets"] if l["campaign_id"] in live_c]
        linked_ids = {l["shared_set_id"] for l in links_live}
        list_members_live = [m for m in d["shared_members"] if m["shared_set_id"] in linked_ids]

        print("\nEXISTING NEGATIVES ON LIVE SCOPES:")
        print("  campaign-level negatives on live campaigns : {}".format(len(cneg_live)))
        print("  ad-group-level negatives on live ad groups : {}".format(len(agneg_live)))
        print("  shared lists linked to live campaigns      : {} (members {})".format(
            len(linked_ids), len(list_members_live)))
        print("  ACCOUNT-level negative lists               : {} (members {})".format(
            len(acct_sets), len(acct_members)))

        per_c = defaultdict(int)
        for n in cneg_live:
            per_c[n["campaign_name"]] += 1
        for name, cnt in sorted(per_c.items()):
            print("    campaign negatives  {:<36} {}".format(name[:36], cnt))
        per_ag = defaultdict(int)
        for n in agneg_live:
            per_ag[(n["campaign_name"], n["ad_group_name"])] += 1
        print("  live ad groups carrying ANY ad-group negative: {} of {}".format(
            len(per_ag), len(live_ag)))

        # search-term shape restricted to live scopes
        st_live = [t for t in d["search_terms"] if t["ad_group_id"] in live_ag]
        st_dead = [t for t in d["search_terms"] if t["ad_group_id"] not in live_ag]
        print("\nSEARCH TERMS:")
        print("  rows total={}  on LIVE ad groups={}  on paused/removed scopes={}".format(
            len(d["search_terms"]), len(st_live), len(st_dead)))
        print("  LIVE: unique terms={} clicks={} cost=${:,.2f} conv={:.2f}".format(
            len({t["term"] for t in st_live}), sum(t["clicks"] for t in st_live),
            sum(t["cost"] for t in st_live), sum(t["conversions"] for t in st_live)))

        by_status = defaultdict(lambda: [0, 0, 0.0])
        for t in st_live:
            b = by_status[t["st_status"]]
            b[0] += 1
            b[1] += t["clicks"]
            b[2] += t["cost"]
        print("  by search_term_view.status (live scopes):")
        for k, v in sorted(by_status.items()):
            print("    {:<16} rows={:<6} clicks={:<6} cost=${:,.2f}".format(k, v[0], v[1], v[2]))

        print("\n  per live ad group (rows / uniq terms / clicks / cost / conv):")
        agg = defaultdict(lambda: [0, set(), 0, 0.0, 0.0])
        for t in st_live:
            a = agg[t["ad_group_id"]]
            a[0] += 1
            a[1].add(t["term"])
            a[2] += t["clicks"]
            a[3] += t["cost"]
            a[4] += t["conversions"]
        for agid, a in sorted(agg.items(), key=lambda x: -x[1][3]):
            meta = live_ag[agid]
            print("    {:<26} | {:<24} {:>5} {:>6} {:>5} ${:>9,.2f} {:>6.2f}".format(
                meta["campaign_name"][:26], meta["name"][:24],
                a[0], len(a[1]), a[2], a[3], a[4]))
        empty = [agid for agid in live_ag if agid not in agg]
        print("    live ad groups with NO search-term history: {}".format(len(empty)))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
