#!/usr/bin/env python3
"""Does the invalid-click flood have a shape we can act on?
click_view carries the RAW click population (valid + invalid). Compare its distribution
on flood days against the distribution of clicks that Google kept."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
DATES = ([f"2026-08-{x:02d}" for x in range(14, 32)] +
         [f"2026-09-{x:02d}" for x in range(1, 10)])

# metrics.clicks (kept) per campaign x click_type x device
kept = Counter()
for r in q(c, f"SELECT campaign.id, segments.click_type, segments.device, metrics.clicks "
              f"FROM campaign WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'"):
    if r.metrics.clicks:
        kept[(NAME[str(r.campaign.id)], E(r.segments.click_type), E(r.segments.device))] += \
            r.metrics.clicks

# click_view raw rows per campaign x click_type x device x date
raw = Counter(); raw_by_day = defaultdict(Counter)
for d in DATES:
    for r in q(c, f"SELECT campaign.id, segments.click_type, segments.device, segments.date, "
                  f"segments.slot FROM click_view WHERE segments.date = '{d}' "
                  f"AND campaign.id IN ({IN5})"):
        k = (NAME[str(r.campaign.id)], E(r.segments.click_type), E(r.segments.device))
        raw[k] += 1
        raw_by_day[d][k] += 1

print("=== RAW CLICKS (click_view) vs CLICKS GOOGLE KEPT (metrics.clicks) ===")
print(f"  {'campaign':<20}{'click_type':<22}{'device':<10}{'raw':>7}{'kept':>7}"
      f"{'discarded':>11}{'disc%':>8}")
agg = []
for k in sorted(set(raw) | set(kept), key=lambda z: -raw.get(z, 0)):
    rr, kk = raw.get(k, 0), kept.get(k, 0)
    if rr < 5 and kk < 3:
        continue
    disc = rr - kk
    agg.append({"campaign": k[0], "click_type": k[1], "device": k[2], "raw": rr, "kept": kk,
                "discarded": disc, "discard_pct": round(100*disc/rr, 1) if rr else None})
    print(f"  {k[0]:<20}{k[1]:<22}{k[2]:<10}{rr:>7}{kk:>7}{disc:>11}"
          f"{(100*disc/rr if rr else 0):>7.1f}%")
out["by_click_type_device"] = agg

print("\n=== BY CLICK TYPE ONLY, ALL FIVE CAMPAIGNS ===")
ct_raw, ct_kept = Counter(), Counter()
for k, v in raw.items(): ct_raw[k[1]] += v
for k, v in kept.items(): ct_kept[k[1]] += v
print(f"  {'click_type':<24}{'raw':>8}{'kept':>7}{'discarded':>11}{'disc%':>8}")
for t in sorted(set(ct_raw) | set(ct_kept), key=lambda z: -ct_raw.get(z, 0)):
    rr, kk = ct_raw.get(t, 0), ct_kept.get(t, 0)
    print(f"  {t:<24}{rr:>8}{kk:>7}{rr-kk:>11}{(100*(rr-kk)/rr if rr else 0):>7.1f}%")

print("\n=== BY DEVICE ONLY ===")
d_raw, d_kept = Counter(), Counter()
for k, v in raw.items(): d_raw[k[2]] += v
for k, v in kept.items(): d_kept[k[2]] += v
print(f"  {'device':<14}{'raw':>8}{'kept':>7}{'discarded':>11}{'disc%':>8}")
for t in sorted(set(d_raw) | set(d_kept), key=lambda z: -d_raw.get(z, 0)):
    rr, kk = d_raw.get(t, 0), d_kept.get(t, 0)
    print(f"  {t:<14}{rr:>8}{kk:>7}{rr-kk:>11}{(100*(rr-kk)/rr if rr else 0):>7.1f}%")

print("\n=== THE FLOOD DAYS: what shape did the raw clicks take? ===")
print(f"  {'date':<12}{'raw':>6}   top click_type x device buckets")
for d in DATES:
    tot = sum(raw_by_day[d].values())
    if tot < 40:
        continue
    top = raw_by_day[d].most_common(3)
    print(f"  {d:<12}{tot:>6}   " +
          "  ".join(f"{k[1]}/{k[2]}={v}" for k, v in top))

print("\n=== ARE THESE CAMPAIGNS EVEN ELIGIBLE FOR LOCATION_EXPANSION? ===")
n = 0
from collections import Counter as _C
ftypes = _C()
for r in q(c, f"SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type, "
              f"campaign_asset.status FROM campaign_asset WHERE campaign.id IN ({IN5})"):
    ft = E(r.campaign_asset.field_type)
    ftypes[ft] += 1
    if "LOCATION" in ft:
        n += 1
        print(f"  {NAME[str(r.campaign.id)]:<20}{ft} asset {r.campaign_asset.asset} "
              f"{E(r.campaign_asset.status)}")
print(f"  campaign-level LOCATION-family assets: {n}")
print(f"  all campaign_asset field types on the five: {dict(ftypes)}")
cft = _C()
for r in q(c, "SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status "
              "FROM customer_asset"):
    ft = E(r.customer_asset.field_type)
    cft[ft] += 1
    if "LOCATION" in ft:
        print(f"  ACCOUNT-level {ft} asset {r.customer_asset.asset} "
              f"{E(r.customer_asset.status)}")
print(f"  all customer_asset field types: {dict(cft)}")

write(EVID / "2026-09-10-invalid-click-signature.json", out)
