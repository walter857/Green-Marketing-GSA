#!/usr/bin/env python3
"""Resolve the commercial ad-group status contradiction: created ENABLED or later enabled?"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
identity_gate(c, verbose=False)
COMM_AG = "199748801029"

print("=== 1. AD_GROUP CREATE event, full old/new resource ===")
rows = q(c, """
    SELECT change_event.change_date_time, change_event.change_resource_type,
           change_event.resource_change_operation, change_event.changed_fields,
           change_event.user_email, change_event.client_type,
           change_event.change_resource_name,
           change_event.old_resource, change_event.new_resource
    FROM change_event
    WHERE change_event.change_date_time >= '2026-09-10'
      AND change_event.change_date_time <= '2026-09-15'
      AND change_event.change_resource_type = AD_GROUP
    ORDER BY change_event.change_date_time DESC
    LIMIT 50
""")
print(f"  AD_GROUP change_event rows in 09-10..09-15: {len(rows)}")
for r in rows:
    e = r.change_event
    print(f"  {e.change_date_time} {E(e.resource_change_operation)} {e.change_resource_name}")
    print(f"    changed_fields: {list(e.changed_fields.paths)}")
    print(f"    user={e.user_email} client_type={E(e.client_type)}")
    try:
        print(f"    OLD ad_group: id={e.old_resource.ad_group.id} status={E(e.old_resource.ad_group.status)} name={e.old_resource.ad_group.name!r}")
    except Exception as ex:
        print(f"    OLD ad_group: <{ex}>")
    try:
        print(f"    NEW ad_group: id={e.new_resource.ad_group.id} status={E(e.new_resource.ad_group.status)} name={e.new_resource.ad_group.name!r}")
    except Exception as ex:
        print(f"    NEW ad_group: <{ex}>")

print("\n=== 2. change_status for this ad group (different retention/resource) ===")
try:
    cs = q(c, f"""
        SELECT change_status.resource_name, change_status.last_change_date_time,
               change_status.resource_status, change_status.resource_type,
               change_status.ad_group, change_status.ad_group_criterion,
               change_status.campaign
        FROM change_status
        WHERE change_status.last_change_date_time >= '2026-09-01'
        ORDER BY change_status.last_change_date_time DESC
        LIMIT 200
    """)
    hits = [r for r in cs if r.change_status.ad_group and r.change_status.ad_group.split("/")[-1] == COMM_AG]
    print(f"  change_status rows since 09-01: {len(cs)}; touching {COMM_AG}: {len(hits)}")
    for r in hits[:30]:
        s = r.change_status
        print(f"    {s.last_change_date_time} {E(s.resource_type):22s} {E(s.resource_status):10s} {s.resource_name}")
    newest = cs[0].change_status.last_change_date_time if cs else None
    print(f"  NEWEST change_status in account: {newest}")
except Exception as ex:
    print("  change_status ERROR:", str(ex)[:500])

print("\n=== 3. What the prior session's own readback receipt recorded ===")
for pat in ["AMB-0910-COMM-NEG-3-2026-09-10-EXECUTED.json"]:
    for p in Path("receipts").rglob(pat):
        d = json.loads(p.read_text(encoding="utf-8"))
        print(f"  {p}")
        s = json.dumps(d)
        import re
        for m in re.finditer(r'"(ad_group_status|status|ad_group_state)"\s*:\s*"([A-Z_]+)"', s):
            print("   ", m.group(0))
        break

print("\n=== 4. Live serving-chain truth for the commercial route ===")
ag = q(c, f"SELECT ad_group.id, ad_group.status, campaign.status, campaign.serving_status FROM ad_group WHERE ad_group.id = {COMM_AG}")[0]
nads = q(c, f"SELECT ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad WHERE ad_group.id = {COMM_AG}")
kw = q(c, f"SELECT ad_group_criterion.criterion_id, ad_group_criterion.status, ad_group_criterion.system_serving_status FROM ad_group_criterion WHERE ad_group.id = {COMM_AG} AND ad_group_criterion.negative = FALSE")
print(f"  campaign  : {E(ag.campaign.status)} / serving {E(ag.campaign.serving_status)}")
print(f"  ad group  : {E(ag.ad_group.status)}")
print(f"  keywords  : {len(kw)} -> " + ", ".join(f"{E(k.ad_group_criterion.status)}/{E(k.ad_group_criterion.system_serving_status)}" for k in kw))
print(f"  ads       : {len(nads)}")
print(f"  CAN SERVE : {E(ag.ad_group.status)=='ENABLED' and len(nads)>0}  <-- zero ads blocks all delivery")

print("\n=== 5. Has the commercial ad group ever had an impression? ===")
m = q(c, f"""
    SELECT ad_group.id, metrics.impressions, metrics.clicks, metrics.cost_micros
    FROM ad_group
    WHERE ad_group.id = {COMM_AG}
      AND segments.date BETWEEN '2026-09-01' AND '2026-09-15'
""")
tot_i = sum(r.metrics.impressions for r in m)
tot_c = sum(r.metrics.clicks for r in m)
tot_s = sum(r.metrics.cost_micros for r in m) / 1e6
print(f"  rows={len(m)} impressions={tot_i} clicks={tot_c} cost=${tot_s:.2f}")
