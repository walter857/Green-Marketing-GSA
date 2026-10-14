#!/usr/bin/env python3
"""2026-09-16 READ-ONLY inventory pass 3: billing, account negatives, shared-set audit."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, client, q, write, E  # noqa: E402

c = client()
out = {}

print("=== BILLING SETUP (corrected) ===")
rows = q(c, """
    SELECT billing_setup.id, billing_setup.status, billing_setup.payments_account,
           billing_setup.payments_account_info.payments_account_id,
           billing_setup.payments_account_info.payments_account_name,
           billing_setup.payments_account_info.payments_profile_id,
           billing_setup.payments_account_info.payments_profile_name,
           billing_setup.start_date_time, billing_setup.end_date_time
    FROM billing_setup
""")
bs = []
for r in rows:
    x = r.billing_setup
    bs.append({
        "id": str(x.id), "status": E(x.status),
        "pay_acct_name": x.payments_account_info.payments_account_name,
        "profile_name": x.payments_account_info.payments_profile_name,
        "start": x.start_date_time, "end": x.end_date_time,
    })
out["billing_setup"] = bs
for x in bs:
    print(f"  {x['id']:>12} {x['status']:>10} start={x['start']} end={x['end'] or '-'} "
          f"acct='{x['pay_acct_name']}' profile='{x['profile_name']}'")
approved = [x for x in bs if x["status"] in ("APPROVED", "APPROVED_HELD", "PENDING")]
print(f"  >>> APPROVED/PENDING billing setups: {len(approved)}  "
      f"({'BILLING OK' if approved else 'NO ACTIVE BILLING -- DELIVERY BLOCKER'})")

print("\n=== ACCOUNT-LEVEL NEGATIVE CRITERION (detail) ===")
for r in q(c, """
    SELECT customer_negative_criterion.id, customer_negative_criterion.type,
           customer_negative_criterion.resource_name,
           customer_negative_criterion.placement.url,
           customer_negative_criterion.content_label.type,
           customer_negative_criterion.negative_keyword_list.shared_set,
           customer_negative_criterion.youtube_video.video_id,
           customer_negative_criterion.youtube_channel.channel_id,
           customer_negative_criterion.mobile_application.app_id
    FROM customer_negative_criterion
"""):
    x = r.customer_negative_criterion
    rec = {
        "id": str(x.id), "type": E(x.type_),
        "placement_url": x.placement.url,
        "content_label": E(x.content_label.type_),
        "neg_kw_list": (x.negative_keyword_list.shared_set or "").split("~")[-1],
    }
    out.setdefault("account_negatives", []).append(rec)
    print(f"  {rec}")

print("\n=== SHARED SET MEMBERSHIP BY SET (aggregate only) ===")
sets = {}
for r in q(c, """
    SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status,
           shared_set.member_count, shared_set.reference_count
    FROM shared_set
"""):
    x = r.shared_set
    sets[str(x.id)] = {"name": x.name, "type": E(x.type_), "status": E(x.status),
                       "members": x.member_count, "refs": x.reference_count}

members = {}
match_mix = {}
for r in q(c, """
    SELECT shared_criterion.shared_set, shared_criterion.criterion_id,
           shared_criterion.type, shared_criterion.keyword.text,
           shared_criterion.keyword.match_type
    FROM shared_criterion
"""):
    sid = r.shared_criterion.shared_set.split("/")[-1].split("~")[0]
    members.setdefault(sid, []).append(
        (r.shared_criterion.keyword.text, E(r.shared_criterion.keyword.match_type))
    )
    match_mix.setdefault(sid, Counter())[E(r.shared_criterion.keyword.match_type)] += 1

for sid, meta in sorted(sets.items(), key=lambda kv: kv[1]["name"]):
    mm = dict(match_mix.get(sid, {}))
    print(f"  {sid:>12} {meta['status']:>8} refs={meta['refs']} declared={meta['members']:>5} "
          f"actual={len(members.get(sid, [])):>5} match_mix={mm} '{meta['name']}'")
out["shared_sets"] = {sid: {**meta, "match_mix": dict(match_mix.get(sid, {})),
                            "actual_members": len(members.get(sid, []))}
                      for sid, meta in sets.items()}

# --------- REVERSE NEGATIVE AUDIT against the proposed AG1 positives ---------
POSITIVES = [
    "permanent christmas light installation",
    "permanent christmas lights installer",
    "permanent holiday light installation",
    "permanent christmas lights",
    "permanent holiday lights",
    "permanent christmas light installer near me",
    "permanent christmas lights cost",
    "permanent christmas lights price",
    "permanent christmas light installation quote",
    "christmas light installation",
]


def toks(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def blocks(neg_text, neg_match, query):
    """Does this negative block the query? BROAD=all tokens present (any order);
    PHRASE=contiguous token run; EXACT=identical token sequence."""
    nt, qt = toks(neg_text), toks(query)
    if not nt:
        return False
    if neg_match == "EXACT":
        return nt == qt
    if neg_match == "PHRASE":
        n = len(nt)
        return any(qt[i:i + n] == nt for i in range(len(qt) - n + 1))
    return all(t in qt for t in nt)  # BROAD


print("\n=== REVERSE NEGATIVE AUDIT: which existing negatives would block our positives ===")
conflicts = {}
for sid, meta in sets.items():
    for pos in POSITIVES:
        hits = [f"{t} [{m}]" for (t, m) in members.get(sid, []) if blocks(t, m, pos)]
        if hits:
            conflicts.setdefault(f"{sid} :: {meta['name']} ({meta['status']}, refs={meta['refs']})",
                                 {})[pos] = hits
if not conflicts:
    print("  NONE of the 7 shared lists would block any proposed positive keyword.")
for k, v in conflicts.items():
    print(f"  LIST {k}")
    for pos, hits in v.items():
        print(f"    BLOCKS '{pos}'  <-  {hits}")
out["reverse_negative_conflicts"] = conflicts

# --------- what the Christmas list actually contains (aggregate themes) -----
XMAS = [sid for sid, m in sets.items() if "christmas" in m["name"].lower()]
for sid in XMAS:
    ms = members.get(sid, [])
    unigrams = Counter()
    for t, _m in ms:
        unigrams.update(toks(t))
    print(f"\n=== '{sets[sid]['name']}' ({sid}) top tokens, {len(ms)} members ===")
    print("  " + ", ".join(f"{w}({n})" for w, n in unigrams.most_common(40)))
    perm = [t for t, _ in ms if "permanent" in t]
    print(f"  members containing 'permanent': {len(perm)} -> {perm[:20]}")
    out[f"xmas_list_{sid}"] = {"count": len(ms), "top_tokens": unigrams.most_common(60),
                               "permanent_members": perm}

write(EVID / "2026-09-16-inventory3.json", out)
print("\nPASS 3 COMPLETE")
