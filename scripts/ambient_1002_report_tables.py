#!/usr/bin/env python3
"""Ambient | 2026-10-02 | Render the search-term verdict appendix and candidate tables (markdown) from files on disk. No API."""
from __future__ import annotations
import csv, json, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CD = ROOT / "clients" / "ambient-cooling-heating"
REP = ROOT / "reports" / "ambient-cooling-heating"
V = list(csv.DictReader((CD / "exports" / "search-term-verdicts-2026-10-01.csv").open(encoding="utf-8")))
C = json.loads((CD / "exports" / "negative-candidates-2026-10-01.json").read_text(encoding="utf-8"))
P = json.loads((CD / "snapshots" / "probe-test-2026-10-01.json").read_text(encoding="utf-8"))
REC = json.loads((CD / "snapshots" / "cpl-reconciliation-2026-10-01.json").read_text(encoding="utf-8"))


def esc(s):
    return str(s).replace("|", "\\|")


def win(v, w):
    i, k, c = int(v[f"{w}_impr"]), int(v[f"{w}_clicks"]), float(v[f"{w}_cost"])
    if not i:
        return "-"
    return f"{i} / {k} / ${c:,.2f}" + (f" / CPC ${c / k:,.2f}" if k else "")


lines = ["# Appendix: every visible search term, Ambient Cooling - Live (2401959466), 2026-09-17..2026-10-01", "",
         "Source: `search_term_view` read 2026-10-02 00:08 ET (account time America/New_York), no filters other than the two in-scope",
         "campaigns. Windows: **H** history 09-17..09-23, **B** baseline 09-24..09-30 ($42 ceiling), **P** 10-01 (first $18 day,",
         "complete; conversions can still lag). Cells are impressions / clicks / cost / avg CPC. Totals add CTR.",
         "Recorded conversions are Google Primary records (0 on every row); `all` shows the 3 Business Profile local actions.",
         "Verified paid leads and qualified leads are **0 for every row** - the reconciliation found no click-ID or call_view-matched",
         "genuine lead in either campaign (see the main report). The relationship column is Google's search-term match label; the",
         "keyword column shows the keyword's real match type.", ""]
groups = collections.defaultdict(list)
for v in V:
    groups[(v["campaign"], v["campaign_id"], v["ad_group"], v["ad_group_id"])].append(v)
for (cn, cid, gn, gid), rows in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][2])):
    rows.sort(key=lambda r: (-float(r["total_cost"]), -int(r["total_impr"]), r["search_term"]))
    cost = sum(float(r["total_cost"]) for r in rows)
    lines += [f"## {esc(gn)} ({gid}) - campaign {cid}", "", f"{len(rows)} rows, ${cost:,.2f} visible cost across all windows.", "",
              "| Search term | Triggering keyword (real type) | Relationship | H | B | P | Total CTR | Rec. conv (all) | Intent | Service fit | Existing exclusion | Verdict | Conf. |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        excl = r["covering_negatives"].split(" | ")[0] if r["covering_negatives"] else r["coverage"]
        lines.append(f"| {esc(r['search_term'])} | {esc(r['triggering_keyword'])} ({r['keyword_match_type']}) | {r['search_term_match_relationship']} | "
                     f"{win(r, 'history')} | {win(r, 'baseline')} | {win(r, 'post_1001')} | {r['total_ctr'] or '-'} | "
                     f"{r['primary_conversions']} ({r['all_conversions']}) | {r['intent']} | {esc(r['service_fit'])} | {esc(excl)} | {r['verdict']} | {r['confidence']} |")
    lines.append("")
(REP / "2026-10-01-search-term-verdicts-appendix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# candidate table (for the main report)
cl = ["| # | Display | Match | Scope | Seen in | Impr / clicks / cost (09-17..10-01) | First..last seen | Why | Conf. | Priority |", "|---|---|---|---|---|---|---|---|---|---|"]
for i, c in enumerate(C, 1):
    cl.append(f"| {i} | `{esc(c['display'])}` | EXACT | campaign {c['campaign_id']} | {esc(', '.join(g[7:] for g in c['seen_in_ad_groups']))} | "
              f"{c['impr']} / {c['clicks']} / ${c['cost']:.2f} | {c['first_seen'][5:]}..{c['last_seen'][5:]} | {c['bucket']}: {esc(c['reason'][:70])} | "
              f"{c['confidence']} | {c['priority'][:2]} |")
(REP / "_tmp_candidates.md").write_text("\n".join(cl) + "\n", encoding="utf-8")
print("appendix rows", len(V), "groups", len(groups), "candidates", len(C))
print("geo candidate:", [c["display"] for c in C if c["campaign_id"] != "24257819463"])
