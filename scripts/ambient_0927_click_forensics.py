#!/usr/bin/env python3
"""Ambient | 2026-09-27 | READ-ONLY click forensics for the heating campaigns (2026-09-17..2026-09-26).

Per campaign and ad group: impressions, clicks, CTR, cost, CPC, share of OUR impressions shown in the
absolute-top slot (#1) and in the top block (above organic), impression share, invalid clicks.
Per click (click_view): date, hour-free, device, click type, ad group, landing page of the clicked ad,
user location (presence city). Landing pages by clicks and date (landing_page_view).
"""
from __future__ import annotations
import sys, json, datetime, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP

SEVEN = ["24257819463", "24268690038", "24257819466", "24132507744", "24279798229", "24268690041", "24274160783"]
SHORT = {"24257819463": "Heating & Furnace Repair", "24268690038": "Heat Pump", "24257819466": "Install/Replace", "24132507744": "Boiler Services",
         "24279798229": "Maintenance (deferred)", "24268690041": "Thermostat", "24274160783": "Geothermal (waiting page)"}
A, END = "2026-09-17", "2026-09-26"
IN = ",".join(SEVEN)
c = client(); identity_gate(c, verbose=False)
out = {}

MET = """metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.all_conversions, metrics.invalid_clicks,
         metrics.absolute_top_impression_percentage, metrics.top_impression_percentage,
         metrics.search_impression_share, metrics.search_absolute_top_impression_share, metrics.search_top_impression_share,
         metrics.search_rank_lost_impression_share"""


def fmt(m):
    i, cl, cost = m.impressions, m.clicks, m.cost_micros / 1e6
    return dict(impr=i, clicks=cl, ctr=round(100 * cl / i, 1) if i else 0, cost=round(cost, 2), cpc=round(cost / cl, 2) if cl else 0,
                conv=round(m.all_conversions, 2), invalid=getattr(m, 'invalid_clicks', 0),
                abs_top_pct=round(100 * m.absolute_top_impression_percentage, 1), top_pct=round(100 * m.top_impression_percentage, 1),
                IS=round(100 * m.search_impression_share, 1), abs_top_IS=round(100 * m.search_absolute_top_impression_share, 1),
                top_IS=round(100 * m.search_top_impression_share, 1), lost_rank=round(100 * m.search_rank_lost_impression_share, 1))


camp = {str(r.campaign.id): fmt(r.metrics) for r in q(c, f"SELECT campaign.id, {MET} FROM campaign WHERE campaign.id IN ({IN}) AND segments.date BETWEEN '{A}' AND '{END}'")}
tot = collections.Counter()
for v in camp.values():
    for k in ("impr", "clicks", "cost", "invalid"): tot[k] += v[k]
print(f"TOTAL {A}..{END}: {tot['impr']} impr, {tot['clicks']} clicks, CTR {round(100*tot['clicks']/tot['impr'],1)}%, ${round(tot['cost'],2)}, invalid clicks filtered {tot['invalid']}")
print("\nCAMPAIGN                    impr clicks  CTR    cost    CPC  |  #1 slot  top-block | IS  abs-top-IS top-IS lost-rank | invalid")
for cid in SEVEN:
    v = camp.get(cid)
    if not v: print(f"{SHORT[cid]:26s} no data"); continue
    print(f"{SHORT[cid]:26s} {v['impr']:5d} {v['clicks']:5d} {v['ctr']:5.1f}% ${v['cost']:7.2f} ${v['cpc']:6.2f} | {v['abs_top_pct']:6.1f}% {v['top_pct']:7.1f}%  | {v['IS']:4.1f} {v['abs_top_IS']:6.1f} {v['top_IS']:6.1f} {v['lost_rank']:6.1f} | {v['invalid']}")
out["campaigns"] = camp

names = {str(r.ad_group.id): r.ad_group.name.replace("SKAG | ", "") for r in q(c, f"SELECT ad_group.id, ad_group.name FROM ad_group WHERE campaign.id IN ({IN})")}
ags = {}
MET_AG = MET.replace("metrics.invalid_clicks,", "")
for r in q(c, f"SELECT ad_group.id, campaign.id, {MET_AG} FROM ad_group WHERE campaign.id IN ({IN}) AND segments.date BETWEEN '{A}' AND '{END}' AND metrics.impressions > 0"):
    ags[str(r.ad_group.id)] = (str(r.campaign.id), fmt(r.metrics))
print("\nAD GROUP (with impressions)        impr clicks  CTR    cost    CPC  |  #1 slot  top-block")
for gid, (cid, v) in sorted(ags.items(), key=lambda x: -x[1][1]["cost"]):
    print(f"  {names[gid][:30]:30s} {v['impr']:5d} {v['clicks']:5d} {v['ctr']:5.1f}% ${v['cost']:7.2f} ${v['cpc']:6.2f} | {v['abs_top_pct']:6.1f}% {v['top_pct']:7.1f}%   [{SHORT[cid][:18]}]")
out["ad_groups"] = {names[g]: v for g, (c_, v) in ags.items()}

# landing pages actually clicked, by date
lp = collections.defaultdict(lambda: collections.Counter())
for r in q(c, f"""SELECT landing_page_view.unexpanded_final_url, segments.date, campaign.id, metrics.clicks, metrics.cost_micros FROM landing_page_view
        WHERE campaign.id IN ({IN}) AND segments.date BETWEEN '{A}' AND '{END}' AND metrics.clicks > 0"""):
    url = r.landing_page_view.unexpanded_final_url.replace("https://", "").split("?")[0]
    lp[url][r.segments.date] += r.metrics.clicks
print("\nLANDING PAGES THAT RECEIVED CLICKS (clicks by date):")
for url, d in sorted(lp.items(), key=lambda x: -sum(x[1].values())):
    print(f"  {sum(d.values()):3d}  {url[:70]:70s} {dict(sorted((k[5:], v) for k, v in d.items()))}")
out["landing_pages"] = {u: dict(d) for u, d in lp.items()}

# every click (click_view needs one date per query)
clicks = []
day = datetime.date.fromisoformat(A)
while day <= datetime.date.fromisoformat(END):
    for r in q(c, f"""SELECT click_view.gclid, click_view.ad_group_ad, click_view.location_of_presence.city, click_view.area_of_interest.city,
            segments.device, segments.click_type, segments.slot, ad_group.id, campaign.id, segments.date FROM click_view
            WHERE segments.date = '{day}' AND campaign.id IN ({IN})"""):
        cv = r.click_view
        clicks.append(dict(date=str(day), ag=names.get(str(r.ad_group.id), str(r.ad_group.id)), camp=SHORT[str(r.campaign.id)],
                           device=E(r.segments.device), click_type=E(r.segments.click_type), slot=E(r.segments.slot),
                           ad=cv.ad_group_ad.split("~")[-1] if cv.ad_group_ad else "", presence_city=cv.location_of_presence.city))
    day += datetime.timedelta(days=1)
ad_urls = {}
for r in q(c, f"SELECT ad_group_ad.ad.id, ad_group_ad.ad.final_urls FROM ad_group_ad WHERE campaign.id IN ({IN})"):
    ad_urls[str(r.ad_group_ad.ad.id)] = (list(r.ad_group_ad.ad.final_urls) or [""])[0].replace("https://", "")
city_names = {}
cities = {x["presence_city"] for x in clicks if x["presence_city"]}
if cities:
    for r in q(c, f"SELECT geo_target_constant.resource_name, geo_target_constant.name FROM geo_target_constant WHERE geo_target_constant.resource_name IN ({','.join(repr(x) for x in cities)})"):
        city_names[r.geo_target_constant.resource_name] = r.geo_target_constant.name
print(f"\nEVERY CLICK recorded by click_view ({len(clicks)} rows; includes clicks Google later filtered as invalid):")
for x in sorted(clicks, key=lambda x: x["date"]):
    dest = ad_urls.get(x["ad"], "?")
    site = "OFFER" if dest.startswith("offer.") else ("MAIN" if dest else "?")
    print(f"  {x['date'][5:]} {x['camp'][:18]:18s} {x['ag'][:26]:26s} {x['device'][:7]:7s} {x['click_type'][:16]:16s} {x['slot'][:14]:14s} {site:5s} {dest[33:70]:37s} {city_names.get(x['presence_city'], '-')}")
summ = collections.Counter((x["click_type"]) for x in clicks)
print("click types:", dict(summ), "| slots:", dict(collections.Counter(x["slot"] for x in clicks)),
      "| devices:", dict(collections.Counter(x["device"] for x in clicks)))
print("destination site:", dict(collections.Counter(("OFFER" if ad_urls.get(x["ad"], "").startswith("offer.") else "MAIN/other") for x in clicks)))
out["clicks"] = clicks
(SNAP / "click-forensics-2026-09-27.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
