#!/usr/bin/env python3
"""What actually changed in the account today. Read-only.

Used to prove the CALL-Q execution created exactly 2 objects and nothing else,
and to establish whether the 3 DEVICE campaign_criterion rows are mine.
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import client, q, E  # noqa: E402

c = client()
today = datetime.date.today()
start = (today - datetime.timedelta(days=2)).isoformat()
# bare-date upper bounds exclude that whole day, so push the ceiling out
end = (today + datetime.timedelta(days=1)).isoformat()

print(f"change_status window {start} .. {end}\n")
rows = q(c, f"""SELECT change_status.resource_name, change_status.resource_type,
                       change_status.resource_status, change_status.last_change_date_time,
                       change_status.campaign, change_status.asset,
                       change_status.campaign_criterion
                FROM change_status
                WHERE change_status.last_change_date_time >= '{start}'
                  AND change_status.last_change_date_time <= '{end}'
                ORDER BY change_status.last_change_date_time DESC
                LIMIT 200""")
print(f"rows: {len(rows)}\n")
from collections import Counter
print("by resource_type:", dict(Counter(E(x.change_status.resource_type) for x in rows)))
print()
for x in rows[:60]:
    s = x.change_status
    extra = ""
    if s.asset:
        extra = f" asset={s.asset.split('/')[-1]}"
    if s.campaign_criterion:
        extra += f" criterion={s.campaign_criterion.split('/')[-1]}"
    print(f"  {s.last_change_date_time}  {E(s.resource_type):<22} {E(s.resource_status):<10}{extra}")

print("\n--- CAMPAIGN_CRITERION changes specifically ---")
crit = [x for x in rows if E(x.change_status.resource_type) == "CAMPAIGN_CRITERION"]
print(f"  {len(crit)} campaign_criterion change rows in this window")
for x in crit[:20]:
    s = x.change_status
    print(f"    {s.last_change_date_time} {E(s.resource_status)} {s.campaign_criterion}")
