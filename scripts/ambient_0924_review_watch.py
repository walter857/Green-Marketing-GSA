#!/usr/bin/env python3
"""Poll Google's review of the 30 new RSAs. READ-ONLY. Exits when all 12 migration copies are
APPROVED/APPROVED_LIMITED, any new ad is DISAPPROVED, or 60 minutes pass."""
from __future__ import annotations
import sys, json, time, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, E, RECEIPTS

cr = json.loads((RECEIPTS / "AMB-0924-LP-CREATE-2-EXECUTED.json").read_text(encoding="utf-8"))
kind = {m["ad_id"]: m["kind"] for m in cr["committed"]["rsas"]}
c = client()
for i in range(13):
    st = {}
    for r in q(c, """SELECT ad_group_ad.ad.id, ad_group_ad.policy_summary.approval_status,
                     ad_group_ad.policy_summary.review_status FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        a = str(r.ad_group_ad.ad.id)
        if a in kind:
            st[a] = (E(r.ad_group_ad.policy_summary.approval_status), E(r.ad_group_ad.policy_summary.review_status))
    summary = collections.Counter((kind[a], s[0]) for a, s in st.items())
    print(time.strftime("%H:%M:%S"), dict(summary), flush=True)
    copies_ok = all(s[0] in ("APPROVED", "APPROVED_LIMITED") for a, s in st.items() if kind[a] == "migration_copy")
    disapproved = [a for a, s in st.items() if s[0] == "DISAPPROVED"]
    if copies_ok or disapproved:
        print("DONE copies_ok=%s disapproved=%s" % (copies_ok, disapproved), flush=True)
        break
    time.sleep(300)
