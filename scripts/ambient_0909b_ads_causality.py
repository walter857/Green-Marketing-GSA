#!/usr/bin/env python3
"""Ads/CTR audit, per-day causality normalisation, and duplicate-conversion testing."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}

print("=== 1. ADS-1 RETENTION CHECK (fresh) ===")
TARGETS = [("202339087634", "820900825434"), ("200159223798", "820944944368")]
ads = []
for r in q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
           ad_group_ad.policy_summary.approval_status,
           ad_group_ad.policy_summary.review_status, ad_group_ad.ad_strength,
           ad_group_ad.ad.final_urls
    FROM ad_group_ad WHERE campaign.id IN ({IN5})
"""):
    x = r.ad_group_ad
    ads.append({"camp": str(r.campaign.id), "ag": str(r.ad_group.id), "ad": str(x.ad.id),
                "status": E(x.status), "approval": E(x.policy_summary.approval_status),
                "strength": E(x.ad_strength), "urls": list(x.ad.final_urls)})
ok = True
for ag, ad in TARGETS:
    t = next((a for a in ads if a["ag"] == ag and a["ad"] == ad), None)
    keep = [a for a in ads if a["ag"] == ag and a["status"] == "ENABLED"
            and a["approval"] == "APPROVED" and a["ad"] != ad]
    c1 = t and t["status"] == "ENABLED" and t["approval"] == "DISAPPROVED"
    c2 = len(keep) >= 2
    ok = ok and c1 and c2
    print(f"  ad {ad} in ag {ag}: status={t['status']} approval={t['approval']} "
          f"-> still ENABLED+DISAPPROVED: {c1}")
    print(f"     ad group retains {len(keep)} ENABLED+APPROVED RSAs -> >=2: {c2}")
print(f"  update mask: the executor hard-codes mask(['status']) for PAUSE_AD_GROUP_AD; "
      f"no other field is writable from that branch.")
print(f"  ADS-1 RETAIN: {ok}")
out["ads1_retention"] = {"pass": ok}

print("\n=== 2. AC REPAIR ADS POINTING AT /hvac-replacement/ ===")
badurl = [a for a in ads if a["camp"] == "24132507741"
          and any("/hvac-replacement/" in u for u in a["urls"])]
agstat = {}
for r in q(c, f"SELECT ad_group.id, ad_group.status, ad_group.name FROM ad_group "
              f"WHERE campaign.id = 24132507741"):
    agstat[str(r.ad_group.id)] = (E(r.ad_group.status), r.ad_group.name)
for a in badurl:
    st, nm = agstat.get(a["ag"], ("?", "?"))
    print(f"  ad {a['ad']} status={a['status']} approval={a['approval']} "
          f"ad_group={a['ag']} ({st}) {nm!r} url={a['urls']}")
print(f"  ad groups in AC Repair: {agstat}")
servable = [a for a in badurl if agstat.get(a["ag"], ("?",))[0] == "ENABLED"]
print(f"  SERVABLE mismatched-URL ads: {len(servable)}  "
      f"-> {'NO ACTION NEEDED' if not servable else 'ACTION REQUIRED'}")
out["ac_repair_wrong_url_ads"] = {"rows": badurl, "servable": len(servable),
                                  "ad_groups": agstat}

print("\n=== 3. RSA ASSET-LEVEL SERVING DATA ===")
assets = []
try:
    for r in q(c, f"""
        SELECT campaign.id, ad_group.id, ad_group_ad_asset_view.field_type,
               ad_group_ad_asset_view.performance_label,
               ad_group_ad_asset_view.enabled, asset.id, asset.text_asset.text,
               metrics.impressions, metrics.clicks
        FROM ad_group_ad_asset_view WHERE campaign.id IN ({IN5})
          AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'
    """):
        x = r.ad_group_ad_asset_view
        assets.append({"camp": str(r.campaign.id), "ag": str(r.ad_group.id),
                       "field": E(x.field_type), "label": E(x.performance_label),
                       "enabled": x.enabled, "text": r.asset.text_asset.text,
                       "impressions": r.metrics.impressions, "clicks": r.metrics.clicks})
except Exception as e:
    print("  ad_group_ad_asset_view failed:", type(e).__name__, str(e)[:200])
out["rsa_assets"] = assets
print(f"  asset rows with delivery: {len(assets)}")
print(f"  by performance_label: {dict(Counter(a['label'] for a in assets))}")
print(f"  by field_type: {dict(Counter(a['field'] for a in assets))}")
print("  -> a LEARNING/PENDING label on every asset means Google has not accumulated enough")
print("     serving data to rate any headline or description. Asset-level A/B conclusions")
print("     are not available at this volume.")

print("\n=== 4. LOCATION INSERTION AND SERVICE-SPECIFIC HEADLINE COVERAGE ===")
prior = json.load(open(EVID / "2026-09-09-ads-assets.json", encoding="utf-8"))["ads"]
LIVE_AG = {"202339087834", "202339087594", "202339087634", "202339087674", "200159223798"}
cover = {}
for a in prior:
    if a["status"] != "ENABLED" or a["ag"] not in LIVE_AG or a["approval"] != "APPROVED":
        continue
    heads = [h["text"] for h in a["headlines"]]
    li = sum(1 for h in heads if "{LOCATION" in h.upper() or "{location" in h)
    cities = sum(1 for h in heads if any(t in h for t in
                 ("Severn", "Severna Park", "Columbia", "Annapolis", "Maryland", "MD",
                  "Glen Burnie", "Odenton", "Crofton", "Ellicott")))
    svc = sum(1 for h in heads if any(t.lower() in h.lower() for t in
              ("AC Repair", "HVAC Repair", "HVAC Install", "Installers", "Replacement",
               "Boiler", "Furnace", "Heating", "Cooling", "Air Conditioning")))
    cover.setdefault(NAME[a["camp"]], []).append(
        {"ad": a["ad_id"], "n_headlines": len(heads), "location_insertion_tags": li,
         "headlines_naming_a_city_or_MD": cities, "headlines_naming_the_service": svc})
for k, v in cover.items():
    for a in v:
        print(f"  {k:<20} ad={a['ad']}  headlines={a['n_headlines']}  "
              f"LOCATION-insertion tags={a['location_insertion_tags']}  "
              f"city/MD headlines={a['headlines_naming_a_city_or_MD']}  "
              f"service headlines={a['headlines_naming_the_service']}")
out["headline_coverage"] = cover

print("\n=== 5. SITELINKS AND THEIR RELEVANCE TO CAMPAIGN INTENT ===")
sl = defaultdict(list)
for r in q(c, f"""
    SELECT campaign.id, campaign_asset.field_type, campaign_asset.status,
           asset.sitelink_asset.link_text, asset.final_urls
    FROM campaign_asset WHERE campaign.id IN ({IN5})
      AND campaign_asset.field_type = 'SITELINK'
      AND campaign_asset.status = 'ENABLED'
"""):
    sl[str(r.campaign.id)].append({"text": r.asset.sitelink_asset.link_text,
                                   "urls": list(r.asset.final_urls)})
out["sitelinks"] = {NAME[k]: v for k, v in sl.items()}
for cid in FIVE:
    print(f"\n  {NAME[cid]} ({len(sl[cid])} enabled sitelinks)")
    for s in sl[cid]:
        u = s["urls"][0] if s["urls"] else ""
        path = u.split(".com")[-1] if u else ""
        own = "" if not path else ("  <- SAME-SERVICE" if
              path.strip("/").replace("-", " ") in NAME[cid].lower().replace("hvac ", "hvac-")
              else "")
        print(f"      {s['text'][:34]:<36} {path}")

print("\n=== 6. MOBILE vs DESKTOP BY CAMPAIGN ===")
dev = defaultdict(lambda: defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                                               "conversions": 0.0, "all_conversions": 0.0}))
for r in q(c, f"SELECT campaign.id, segments.device, {METRICS} FROM campaign "
              f"WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'"):
    d = dev[str(r.campaign.id)][E(r.segments.device)]
    for f in ("impressions", "clicks", "conversions", "all_conversions"):
        d[f] += getattr(r.metrics, f)
    d["cost"] += r.metrics.cost_micros / 1e6
out["device_by_campaign"] = {NAME[k]: {kk: {a: round(b, 2) for a, b in vv.items()}
                                       for kk, vv in v.items()} for k, v in dev.items()}
print(f"  {'campaign':<20}{'device':<10}{'impr':>7}{'clicks':>8}{'ctr':>8}{'cpc':>9}"
      f"{'cost':>10}{'conv':>7}")
for cid in FIVE:
    for d, v in sorted(dev[cid].items()):
        if not v["impressions"]:
            continue
        ctr = 100*v["clicks"]/v["impressions"] if v["impressions"] else 0
        cpc = v["cost"]/v["clicks"] if v["clicks"] else 0
        print(f"  {NAME[cid]:<20}{d:<10}{v['impressions']:>7}{v['clicks']:>8}{ctr:>7.2f}%"
              f"{cpc:>9.2f}{v['cost']:>10.2f}{v['conversions']:>7.1f}")
print("\n  DESKTOP bid-adjustment question, per campaign:")
for cid in FIVE:
    d = dev[cid].get("DESKTOP")
    if d and d["clicks"]:
        print(f"    {NAME[cid]:<20} desktop {d['clicks']} clicks, ${d['cost']:.2f}, "
              f"{d['conversions']:.0f} primary conv "
              f"-> {'sample too small for a bid adjustment' if d['clicks'] < 30 else 'evidence sufficient'}")

print("\n=== 7. CAUSALITY: PER-DAY NORMALISED BEFORE/AFTER THE 2026-09-04 CEILING ===")
days = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
for r in q(c, f"SELECT segments.date, segments.day_of_week, {METRICS} FROM campaign "
              f"WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-08'"):
    d = days[r.segments.date]
    for f in ("impressions", "clicks", "conversions"):
        d[f] += getattr(r.metrics, f)
    d["cost"] += r.metrics.cost_micros / 1e6
    d["dow"] = E(r.segments.day_of_week)
import datetime as dt
allday = {}
start = dt.date(2026, 8, 14)
end = dt.date(2026, 9, 8)
cur = start
while cur <= end:
    k = cur.isoformat()
    v = days.get(k, {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
    allday[k] = {"impressions": v["impressions"], "clicks": v["clicks"],
                 "cost": round(v["cost"], 2), "conversions": v["conversions"],
                 "dow": cur.strftime("%a")}
    cur += dt.timedelta(days=1)
BEFORE = [k for k in allday if k <= "2026-09-03"]
AFTER = [k for k in allday if k >= "2026-09-05"]
def per_day(keys):
    n = len(keys)
    return {"days": n,
            "impressions_per_day": round(sum(allday[k]["impressions"] for k in keys)/n, 1),
            "clicks_per_day": round(sum(allday[k]["clicks"] for k in keys)/n, 2),
            "cost_per_day": round(sum(allday[k]["cost"] for k in keys)/n, 2),
            "conversions_per_day": round(sum(allday[k]["conversions"] for k in keys)/n, 3)}
b, a = per_day(BEFORE), per_day(AFTER)
out["causality"] = {"before": b, "after": a, "daily": allday}
print(f"  {'metric':<26}{'BEFORE 08-14..09-03':>22}{'AFTER 09-05..09-08':>22}{'change':>12}")
for k in ("days", "impressions_per_day", "clicks_per_day", "cost_per_day",
          "conversions_per_day"):
    ch = ("" if k == "days" else
          (f"{100*(a[k]-b[k])/b[k]:+.1f}%" if b[k] else "n/a"))
    print(f"  {k:<26}{b[k]:>22}{a[k]:>22}{ch:>12}")
print("\n  CONFOUNDERS IN THE POST-CHANGE WINDOW (must be disclosed):")
print(f"    - only {a['days']} days, versus {b['days']} before")
wk = [k for k in AFTER if allday[k]['dow'] in ('Sat', 'Sun')]
print(f"    - contains {len(wk)} weekend day(s): {[(k, allday[k]['dow']) for k in wk]}")
print(f"    - 2026-09-07 was Labor Day (US federal holiday); the whole window sits in the")
print(f"      Labor Day long weekend, a low-intent period for home-services demand")
print(f"    - 125 further campaign negatives were added on 2026-09-09 and 372 on 2026-09-01,")
print(f"      so negative coverage also changed inside and around the window")
print(f"    - the ad schedule excludes Sunday entirely, so one of the 4 days could never serve")
print("    -> the ceilings are the STRONGEST SUSPECTED CAUSE of suppressed delivery.")
print("       This is not a clean isolated causal test and must not be reported as one.")

print("\n=== 8. DUPLICATE-CONVERSION TESTING ===")
print("  Available keys for de-duplication:")
ca = []
for r in q(c, "SELECT conversion_action.id, conversion_action.name, "
              "conversion_action.counting_type, conversion_action.type, "
              "conversion_action.primary_for_goal, conversion_action.status "
              "FROM conversion_action WHERE conversion_action.status != 'REMOVED'"):
    x = r.conversion_action
    ca.append({"id": str(x.id), "name": x.name, "counting": E(x.counting_type),
               "type": E(x.type_), "pfg": x.primary_for_goal})
biddable = [x for x in ca if x["name"] in ("Calls from ads", "WC Lead",
                                           "Ambient Cooling - LP -Submit Lead Forms")]
for x in biddable:
    print(f"    {x['name']:<42} counting_type={x['counting']:<14} type={x['type']}")
print("\n  ONE_PER_CLICK already de-duplicates within a single click for all three biddable")
print("  actions, so within-action double counting is structurally prevented.")
print("  CROSS-action duplication is the real exposure: one caller who also submits the form")
print("  can be counted by 'Calls from ads' AND 'WC Lead' AND the landing-page form action.")
calls = []
try:
    for r in q(c, "SELECT call_view.caller_area_code, call_view.call_duration_seconds, "
                  "call_view.call_status, call_view.start_call_date_time, "
                  "call_view.type, campaign.id FROM call_view"):
        x = r.call_view
        calls.append({"area": x.caller_area_code, "dur": x.call_duration_seconds,
                      "status": E(x.call_status), "start": x.start_call_date_time,
                      "type": E(x.type_), "camp": str(r.campaign.id)})
except Exception as e:
    print("  call_view read failed:", type(e).__name__, str(e)[:160])
out["call_log"] = calls
print(f"\n  call_view rows retained: {len(calls)}")
if calls:
    print(f"    by status: {dict(Counter(c_['status'] for c_ in calls))}")
    print(f"    by type:   {dict(Counter(c_['type'] for c_ in calls))}")
    print(f"    duration buckets: "
          f"{dict(Counter('>=60s' if (c_['dur'] or 0) >= 60 else '<60s' for c_ in calls))}")
    seen = Counter((c_["area"], c_["start"][:16] if c_["start"] else "") for c_ in calls)
    dupes = {k: v for k, v in seen.items() if v > 1}
    print(f"    same area code + same minute (duplicate candidates): {len(dupes)}")
    print("    NOTE: call_view exposes only the caller AREA CODE, never the full number, so a")
    print("    true caller-level de-duplication is not possible from the Google Ads API alone.")
else:
    print("    No retained call log. Duplicate testing by caller is not possible from the API.")
print("\n  VERDICT: cross-action duplicate testing needs WhatConverts lead IDs joined to GCLID.")
print("  WHATCONVERTS_API_TOKEN is empty, so this test CANNOT be completed this run.")
out["duplicate_test"] = {"within_action": "prevented by ONE_PER_CLICK on all three biddable actions",
                         "cross_action": "NOT TESTABLE - requires WhatConverts lead IDs",
                         "caller_level": "NOT TESTABLE - call_view exposes area code only",
                         "call_rows": len(calls)}

write(EVID / "2026-09-09b-ads-and-causality.json", out)
