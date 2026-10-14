#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | shared negative list conflict audit.

Tests every ENABLED shared negative list in the account against:
  * the 10 live positive keywords on the five campaigns
  * 54 in-scope service demand probes covering the five approved services
  * the 750 observed search-term / campaign pairs, including every term that
    has ever produced a conversion

A list is ATTACHABLE only when it blocks zero live keywords, zero converting
terms and zero service probes. Read-only: attaches nothing.
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, SNAP, TZ, client, q, identity_gate, E, write,
)
from ambient_0827_negative_audit import SERVICE_PROBES, blocks, words  # noqa: E402

STAMP = "2026-08-27"


def main():
    c = client()
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "read_only": True}
    out["identity"] = identity_gate(c, verbose=False)
    print("IDENTITY: PASS\n")

    kws = []
    for r in q(c, f"""SELECT campaign.id, ad_group.name, ad_group_criterion.keyword.text,
                      ad_group_criterion.keyword.match_type
                      FROM ad_group_criterion WHERE campaign.id IN ({IN5})
                        AND ad_group_criterion.type='KEYWORD'
                        AND ad_group_criterion.status != 'REMOVED'
                        AND ad_group_criterion.negative = FALSE
                        AND ad_group.status != 'REMOVED'"""):
        kws.append({"campaign_id": str(r.campaign.id),
                    "campaign": NAME[str(r.campaign.id)],
                    "text": r.ad_group_criterion.keyword.text,
                    "match": E(r.ad_group_criterion.keyword.match_type)})

    st = json.loads((SNAP / f"search-terms-{STAMP}.json").read_text(encoding="utf-8"))
    verdicts = st["verdicts"]
    converting = [v for v in verdicts if v["all_conversions"] > 0]
    costed = [v for v in verdicts if v["cost"] > 0]

    sets_ = []
    for r in q(c, """SELECT shared_set.id, shared_set.name, shared_set.type,
                     shared_set.status, shared_set.member_count, shared_set.reference_count
                     FROM shared_set WHERE shared_set.status = 'ENABLED'"""):
        x = r.shared_set
        if E(x.type_) != "NEGATIVE_KEYWORDS":
            continue
        sets_.append({"id": str(x.id), "name": x.name,
                      "member_count": x.member_count,
                      "reference_count": x.reference_count})

    members = defaultdict(list)
    for r in q(c, """SELECT shared_set.id, shared_criterion.criterion_id,
                     shared_criterion.type, shared_criterion.keyword.text,
                     shared_criterion.keyword.match_type FROM shared_criterion"""):
        members[str(r.shared_set.id)].append({
            "criterion_id": str(r.shared_criterion.criterion_id),
            "text": r.shared_criterion.keyword.text,
            "match": E(r.shared_criterion.keyword.match_type)})

    print("== SHARED NEGATIVE LIST CONFLICT AUDIT ==\n")
    report = []
    for s in sorted(sets_, key=lambda z: z["member_count"]):
        ms = members.get(s["id"], [])
        kw_conf, probe_conf, conv_conf, cost_hits = [], [], [], []
        for m in ms:
            for k in kws:
                hit, _ = blocks(m["text"], m["match"], k["text"])
                if hit:
                    kw_conf.append({"negative": m["text"], "match": m["match"],
                                    "blocks_keyword": k["text"], "campaign": k["campaign"]})
            for p in SERVICE_PROBES:
                hit, _ = blocks(m["text"], m["match"], p)
                if hit:
                    probe_conf.append({"negative": m["text"], "match": m["match"],
                                       "blocks_probe": p})
            for v in converting:
                hit, _ = blocks(m["text"], m["match"], v["search_term"])
                if hit:
                    conv_conf.append({"negative": m["text"], "match": m["match"],
                                      "blocks_converting_term": v["search_term"],
                                      "all_conversions": v["all_conversions"],
                                      "primary_conversions": v["primary_conversions"]})
            for v in costed:
                hit, _ = blocks(m["text"], m["match"], v["search_term"])
                if hit:
                    cost_hits.append({"negative": m["text"], "term": v["search_term"],
                                      "cost": v["cost"],
                                      "primary_conversions": v["primary_conversions"]})
        attachable = not kw_conf and not probe_conf and not conv_conf
        wasted_blocked = round(sum(
            h["cost"] for h in cost_hits if h["primary_conversions"] == 0), 2)
        rec = {**s, "attachable": attachable,
               "keyword_conflicts": kw_conf[:20], "keyword_conflict_count": len(kw_conf),
               "probe_conflicts": probe_conf[:20], "probe_conflict_count": len(probe_conf),
               "converting_term_conflicts": conv_conf[:20],
               "converting_term_conflict_count": len(conv_conf),
               "observed_wasted_cost_it_would_have_blocked": wasted_blocked,
               "observed_costed_terms_it_matches": len({h["term"] for h in cost_hits})}
        report.append(rec)
        verdict = "ATTACHABLE" if attachable else "DO NOT ATTACH"
        print(f"  {s['id']} members={s['member_count']:>5d} refs={s['reference_count']:>3d} "
              f"{verdict:14s} {s['name']}")
        print(f"      blocks live keywords: {len(kw_conf)} | blocks service probes: "
              f"{len(probe_conf)} | blocks converting terms: {len(conv_conf)}")
        print(f"      would have blocked ${wasted_blocked:,.2f} of observed zero-lead spend "
              f"across {rec['observed_costed_terms_it_matches']} costed terms")
        for x in kw_conf[:6]:
            print(f"        KEYWORD CONFLICT  [{x['match']}] '{x['negative']}' blocks "
                  f"'{x['blocks_keyword']}' ({x['campaign']})")
        seen = set()
        for x in probe_conf:
            k = (x["negative"], x["match"])
            if k in seen:
                continue
            seen.add(k)
            if len(seen) > 8:
                print(f"        ... and {len(probe_conf) - 8} more probe conflicts")
                break
            print(f"        PROBE CONFLICT    [{x['match']}] '{x['negative']}' blocks "
                  f"'{x['blocks_probe']}'")
        for x in conv_conf[:6]:
            print(f"        CONVERTING TERM   [{x['match']}] '{x['negative']}' blocks "
                  f"'{x['blocks_converting_term']}' (all={x['all_conversions']}, "
                  f"primary={x['primary_conversions']})")
        print()

    out["lists"] = report
    write(SNAP / f"shared-list-conflict-audit-{STAMP}.json", out)
    print("== SUMMARY ==")
    for r in report:
        print(f"  {'ATTACHABLE   ' if r['attachable'] else 'DO NOT ATTACH'} "
              f"{r['id']} {r['name']} (blocks ${r['observed_wasted_cost_it_would_have_blocked']:,.2f} "
              f"of observed waste)")
    return out


if __name__ == "__main__":
    main()
