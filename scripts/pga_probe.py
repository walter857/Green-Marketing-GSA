#!/usr/bin/env python3
"""Read-only console probe over the fresh Pro Green Austin snapshot.

Prints counts, aggregates and structural facts only. Raw search-term strings are
printed only for the small, explicitly named diagnostic families.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SNAP = Path(sys.argv[1])
D = json.loads(SNAP.read_text(encoding="utf-8"))

TARGETS = {
    "24053505504": "Progreen Austin | Search | Outdoor Living & Design",
    "24053505501": "Progreen Austin | Search | Hardscape Construction",
}


def norm(t):
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


print("== IDENTITY ==")
print(json.dumps(D["identity"], indent=1))

print("\n== CAMPAIGNS ==")
for c in D["campaigns"]:
    flag = "  <== IN SCOPE" if c["id"] in TARGETS else ""
    print(f"  {c['id']:>12}  {c['status']:<8} {c['channel']:<18} {c['name']}{flag}")

print("\n== IN-SCOPE CAMPAIGN NAME/ID MATCH ==")
for cid, name in TARGETS.items():
    hit = [c for c in D["campaigns"] if c["id"] == cid]
    if not hit:
        print(f"  {cid}  MISSING")
        continue
    c = hit[0]
    print(f"  {cid}  name_match={c['name'] == name}  status={c['status']}  "
          f"resource={c['resource_name']}")

print("\n== AD GROUPS (in-scope campaigns) ==")
ags = [a for a in D["ad_groups"] if a["campaign_id"] in TARGETS]
print(f"  total={len(ags)}  by status={dict(Counter(a['status'] for a in ags))}")
print(f"  by campaign={dict(Counter(a['campaign_name'] for a in ags))}")

print("\n== AD-GROUP KEYWORD CRITERIA (in-scope) ==")
kws = [k for k in D["ad_group_keywords"] if k["campaign_id"] in TARGETS]
pos = [k for k in kws if not k["negative"]]
neg = [k for k in kws if k["negative"]]
print(f"  total={len(kws)}  positive={len(pos)}  ad_group_negative={len(neg)}")
print(f"  positive by status={dict(Counter(k['status'] for k in pos))}")
print(f"  positive ENABLED by match={dict(Counter(k['match_type'] for k in pos if k['status'] == 'ENABLED'))}")
print(f"  ad-group negatives by match={dict(Counter(k['match_type'] for k in neg))}")
print(f"  ad groups holding negatives={len({k['ad_group_id'] for k in neg})}")

print("\n== ADS (in-scope) ==")
ads = [a for a in D["ad_final_urls"] if a["campaign_id"] in TARGETS]
print(f"  total={len(ads)}  by status={dict(Counter(a['status'] for a in ads))}")
per_ag = Counter(a["ad_group_id"] for a in ads if a["status"] == "ENABLED")
print(f"  enabled ads per ad group distribution={dict(Counter(per_ag.values()))}")
urls = Counter(u for a in ads for u in a["final_urls"])
print(f"  distinct final URLs={len(urls)}")
for u, n in urls.most_common():
    print(f"    {n:>3}  {u}")

print("\n== CAMPAIGN NEGATIVE KEYWORDS ==")
cn = defaultdict(list)
for x in D["campaign_negative_keywords"]:
    cn[x["campaign_id"]].append(x)
for cid, name in TARGETS.items():
    rows = cn.get(cid, [])
    print(f"  {cid} {name}: {len(rows)} negatives, "
          f"match={dict(Counter(r['match_type'] for r in rows))}")
print(f"  campaigns with any negative: {len(cn)}  grand total rows="
      f"{len(D['campaign_negative_keywords'])}")

print("\n== SHARED SETS ==")
for s in D["shared_sets"]:
    print(f"  {s['id']:>12} {s['type']:<34} status={s['status']:<8} "
          f"members={s['member_count']:<6} {s['name']}")
links = defaultdict(list)
for l in D["campaign_shared_sets"]:
    links[l["campaign_id"]].append((l["shared_set_id"], l["link_status"]))
print("  links to in-scope campaigns:")
for cid in TARGETS:
    print(f"    {cid}: {links.get(cid, [])}")
sc = Counter(x["shared_set_id"] for x in D["shared_criteria"])
print(f"  shared_criteria rows by set: {dict(sc)}")

print("\n== ACCOUNT-LEVEL NEGATIVE CRITERIA ==")
print(f"  customer_negative_criterion rows={len(D['customer_negative_criteria'])} "
      f"types={dict(Counter(x['type'] for x in D['customer_negative_criteria']))}")

print("\n== SEARCH TERMS, WINDOW (not date-segmented) ==")
rows = D["search_terms_window"]
print(f"  rows={len(rows)}")
print(f"  by campaign status={dict(Counter(r['campaign_status'] for r in rows))}")
print(f"  by campaign={dict(Counter(r['campaign_name'] for r in rows))}")
print(f"  distinct raw terms={len({r['term'] for r in rows})}")
print(f"  distinct normalized terms={len({norm(r['term']) for r in rows})}")
print(f"  impressions={sum(r['impressions'] for r in rows)} "
      f"clicks={sum(r['clicks'] for r in rows)} "
      f"cost=${sum(r['cost'] for r in rows):,.2f} "
      f"conv={sum(r['conversions'] for r in rows):.2f} "
      f"allconv={sum(r['all_conversions'] for r in rows):.2f} "
      f"convval={sum(r['conversions_value'] for r in rows):.2f}")
print(f"  added_excluded={dict(Counter(r['added_excluded'] for r in rows))}")
print(f"  search_term_match_type={dict(Counter(r['search_term_match_type'] for r in rows))}")
print(f"  matched keyword match types={dict(Counter(r['matched_match_type'] for r in rows))}")
zero = [r for r in rows if r["impressions"] == 0]
print(f"  zero-impression rows={len(zero)}")

print("\n== SEARCH TERMS, WINDOW, BY DATE ==")
bd = D["search_terms_window_by_date"]
print(f"  rows={len(bd)}")
byd = defaultdict(lambda: [0, 0, 0, 0.0, 0.0])
for r in bd:
    v = byd[r["date"]]
    v[0] += 1; v[1] += r["impressions"]; v[2] += r["clicks"]
    v[3] += r["cost"]; v[4] += r["conversions"]
for d in sorted(byd):
    v = byd[d]
    print(f"    {d}  rows={v[0]:4} impr={v[1]:5} clicks={v[2]:4} "
          f"cost=${v[3]:8,.2f} conv={v[4]:.2f}")

print("\n== CAMPAIGN TOTALS, WINDOW ==")
tot = 0.0
for t in sorted(D["campaign_totals_window"], key=lambda x: -x["cost"]):
    mark = " <== IN SCOPE" if t["campaign_id"] in TARGETS else ""
    print(f"  {t['campaign_id']:>12} {t['status']:<9} impr={t['impressions']:>6} "
          f"clicks={t['clicks']:>5} cost=${t['cost']:>9,.2f} conv={t['conversions']:>5.2f}  "
          f"{t['campaign_name']}{mark}")
    tot += t["cost"]
print(f"  ACCOUNT TOTAL cost=${tot:,.2f}")
inscope = [t for t in D["campaign_totals_window"] if t["campaign_id"] in TARGETS]
print(f"  IN-SCOPE TOTAL cost=${sum(t['cost'] for t in inscope):,.2f} "
      f"clicks={sum(t['clicks'] for t in inscope)} "
      f"impr={sum(t['impressions'] for t in inscope)} "
      f"conv={sum(t['conversions'] for t in inscope):.2f}")

print("\n== CAMPAIGN TOTALS BY DATE (in-scope) ==")
cbd = defaultdict(lambda: [0, 0, 0.0, 0.0])
for r in D["campaign_totals_window_by_date"]:
    if r["campaign_id"] not in TARGETS:
        continue
    v = cbd[r["date"]]
    v[0] += r["impressions"]; v[1] += r["clicks"]; v[2] += r["cost"]; v[3] += r["conversions"]
for d in sorted(cbd):
    v = cbd[d]
    print(f"    {d}  impr={v[0]:5} clicks={v[1]:4} cost=${v[2]:8,.2f} conv={v[3]:.2f}")

print("\n== ALL-TIME CONVERTING QUERIES ==")
conv = D["search_terms_all_time_converting"]
print(f"  rows={len(conv)}  distinct normalized={len({norm(r['term']) for r in conv})}")
allc = D["search_terms_all_time_all_conv"]
print(f"  all_conversions>0 rows={len(allc)}  "
      f"distinct normalized={len({norm(r['term']) for r in allc})}")

print("\n== CHANGE EVENTS ==")
print(f"  rows={len(D['change_events'])}")
print(f"  by resource type={dict(Counter(e['resource_type'] for e in D['change_events']))}")
print(f"  by operation={dict(Counter(e['operation'] for e in D['change_events']))}")
