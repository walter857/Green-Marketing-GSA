#!/usr/bin/env python3
"""Ambient | 2026-09-22 | Read every created/changed resource back from the API.

READ-ONLY. EXTERNAL WRITES: 0.

Asserts against the SAVED MANIFEST, not against the execution summary, so a write that
silently did something else is caught rather than confirmed.
"""
from __future__ import annotations
import sys, json, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-22"
LIVE = ROOT / "receipts" / "live"
ap = argparse.ArgumentParser()
ap.add_argument("--after", default="A")
args = ap.parse_args()

c = client()
identity_gate(c, verbose=False)
build = json.loads((PLANS / "AMB-0922-BUILD-1.json").read_text(encoding="utf-8"))
AG = build["ad_groups"]
CAMPAIGNS = build["campaigns"]
XNEG = build["cross_negatives"]
SCHEDULE = build["schedule"]
made = json.loads((LIVE / f"AMB-0922-TRANSITION-{STAMP}-A.json").read_text(
    encoding="utf-8"))["committed"]

out = {"when": datetime.datetime.now(TZ).isoformat(), "after_stage": args.after,
       "read_only": True, "assertions": [], "FAIL": 0}


def check(label, ok, detail=""):
    out["assertions"].append({"check": label, "pass": bool(ok), "detail": str(detail)[:300]})
    if not ok:
        out["FAIL"] += 1
        print(f"   FAIL {label}: {detail}")


ALL_C = {k: (v["reuse"] or made["campaigns"].get(k)) for k, v in CAMPAIGNS.items()}
ids = ",".join(x for x in ALL_C.values() if x)

print("=== CAMPAIGNS ===")
live_c = {}
for r in q(c, f"""SELECT campaign.id, campaign.name, campaign.status,
                  campaign.advertising_channel_type,
                  campaign.target_spend.cpc_bid_ceiling_micros,
                  campaign.network_settings.target_google_search,
                  campaign.network_settings.target_search_network,
                  campaign.network_settings.target_content_network,
                  campaign.geo_target_type_setting.positive_geo_target_type,
                  campaign_budget.id, campaign_budget.amount_micros,
                  campaign_budget.explicitly_shared
                  FROM campaign WHERE campaign.id IN ({ids})"""):
    x = r.campaign
    live_c[str(x.id)] = {
        "name": x.name, "status": E(x.status), "channel": E(x.advertising_channel_type),
        "ceiling": round(x.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
        "search": x.network_settings.target_google_search,
        "partners": x.network_settings.target_search_network,
        "display": x.network_settings.target_content_network,
        "geo": E(x.geo_target_type_setting.positive_geo_target_type),
        "budget_id": str(r.campaign_budget.id),
        "daily": round(r.campaign_budget.amount_micros / 1e6, 2),
        "shared": r.campaign_budget.explicitly_shared}
for k, cid_ in ALL_C.items():
    v = live_c.get(cid_, {})
    want_name = CAMPAIGNS[k].get("rename_to") or CAMPAIGNS[k]["name"]
    print(f"   {k:4s} {cid_}  {v.get('status'):8s} ${v.get('daily'):7.2f} "
          f"ceil ${v.get('ceiling'):6.2f}  {v.get('name','')[:52]}")
    check(f"{k} exists", bool(v), cid_)
    check(f"{k} name", v.get("name") == want_name, f"{v.get('name')} != {want_name}")
    check(f"{k} channel SEARCH", v.get("channel") == "SEARCH", v.get("channel"))
    check(f"{k} search partners OFF", v.get("partners") is False, v.get("partners"))
    check(f"{k} display OFF", v.get("display") is False, v.get("display"))
    check(f"{k} geo PRESENCE", v.get("geo") == "PRESENCE", v.get("geo"))
    check(f"{k} budget not shared", v.get("shared") is False, v.get("shared"))
    if args.after == "A":
        check(f"{k} PAUSED after stage A",
              v.get("status") == "PAUSED" or CAMPAIGNS[k]["reuse"],
              v.get("status"))

print("\n=== AD SCHEDULE (must be Mon-Fri 08:00-16:00, 5 rows, no weekend) ===")
sched = {}
for r in q(c, f"""SELECT campaign.id, campaign_criterion.ad_schedule.day_of_week,
                  campaign_criterion.ad_schedule.start_hour,
                  campaign_criterion.ad_schedule.end_hour
                  FROM campaign_criterion
                  WHERE campaign_criterion.type='AD_SCHEDULE'
                    AND campaign.id IN ({ids})"""):
    a = r.campaign_criterion.ad_schedule
    sched.setdefault(str(r.campaign.id), []).append(
        (E(a.day_of_week), a.start_hour, a.end_hour))
for k, cid_ in ALL_C.items():
    rows = sorted(sched.get(cid_, []))
    days = {d for d, _, _ in rows}
    print(f"   {k:4s} {len(rows)} rows  {sorted(days)}  "
          f"{sorted({(s,e) for _,s,e in rows})}")
    check(f"{k} 5 schedule rows", len(rows) == 5, rows)
    check(f"{k} no weekend", not (days & {"SATURDAY", "SUNDAY"}), sorted(days))
    check(f"{k} hours 08-16", all(s == 8 and e == 16 for _, s, e in rows), rows)

print("\n=== LOCATIONS (75 per new campaign) ===")
loc = {}
for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id
                  FROM campaign_criterion
                  WHERE campaign_criterion.type='LOCATION'
                    AND campaign_criterion.negative=FALSE
                    AND campaign.id IN ({ids})"""):
    loc[str(r.campaign.id)] = loc.get(str(r.campaign.id), 0) + 1
for k, cid_ in ALL_C.items():
    print(f"   {k:4s} {loc.get(cid_,0)} locations")
    check(f"{k} 75 locations", loc.get(cid_, 0) == 75, loc.get(cid_, 0))

print("\n=== AD GROUPS ===")
agids = ",".join(made["ad_groups"].values())
live_ag = {}
for r in q(c, f"""SELECT ad_group.id, ad_group.name, ad_group.status,
                  ad_group.cpc_bid_micros, campaign.id
                  FROM ad_group WHERE ad_group.id IN ({agids})"""):
    live_ag[str(r.ad_group.id)] = {"name": r.ad_group.name,
                                   "status": E(r.ad_group.status),
                                   "campaign_id": str(r.campaign.id),
                                   "cpc": round(r.ad_group.cpc_bid_micros / 1e6, 2)}
n_paused = sum(1 for v in live_ag.values() if v["status"] == "PAUSED")
print(f"   {len(live_ag)}/30 found, {n_paused} PAUSED")
check("30 ad groups exist", len(live_ag) == 30, len(live_ag))
for n, agid in made["ad_groups"].items():
    v = live_ag.get(agid, {})
    check(f"ad group name {n}", v.get("name") == n, v.get("name"))
    want_c = ALL_C[AG[n]["campaign_key"]]
    check(f"ad group campaign {n}", v.get("campaign_id") == want_c,
          f"{v.get('campaign_id')} != {want_c}")
    if args.after == "A":
        # SKAG | Gas Boiler Repair was ALREADY ENABLED on the live boiler campaign before
        # this work and the plan never pauses it. Only resources this plan creates are
        # asserted PAUSED.
        if not AG[n]["existing_ad_group_id"]:
            check(f"ad group PAUSED {n}", v.get("status") == "PAUSED", v.get("status"))
        else:
            check(f"pre-existing ad group untouched {n}",
                  v.get("status") in ("PAUSED", "ENABLED"), v.get("status"))

print("\n=== KEYWORDS ===")
kw = {}
for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.keyword.text,
                  ad_group_criterion.keyword.match_type,
                  ad_group_criterion.status, ad_group_criterion.negative,
                  ad_group_criterion.approval_status,
                  ad_group_criterion.system_serving_status
                  FROM ad_group_criterion
                  WHERE ad_group.id IN ({agids})
                    AND ad_group_criterion.type='KEYWORD'
                    AND ad_group_criterion.status != 'REMOVED'"""):
    x = r.ad_group_criterion
    d = kw.setdefault(str(r.ad_group.id), {"pos": [], "neg": []})
    d["neg" if x.negative else "pos"].append(
        (x.keyword.text, E(x.keyword.match_type), E(x.status),
         E(x.approval_status), E(x.system_serving_status)))
tot_pos = sum(len(v["pos"]) for v in kw.values())
tot_neg = sum(len(v["neg"]) for v in kw.values())
print(f"   positive {tot_pos}   negative {tot_neg}")
for n, agid in made["ad_groups"].items():
    want_n = len(XNEG[n])
    got_n = len(kw.get(agid, {}).get("neg", []))
    check(f"cross-negatives {n}", got_n == want_n, f"{got_n} != {want_n}")
    if AG[n]["phrase"] or AG[n]["exact"]:
        want_p = len(AG[n]["phrase"]) + len(AG[n]["exact"])
        got_p = len(kw.get(agid, {}).get("pos", []))
        check(f"keywords {n}", got_p >= want_p, f"{got_p} < {want_p}")
# the two moved keywords must be gone from the furnace ad group
fr = kw.get("199797580706", {}).get("pos", [])
check("gas furnace repair removed from Furnace Repair",
      not any(t.lower() == "gas furnace repair" for t, *_ in fr),
      [t for t, *_ in fr])

print("\n=== ADS ===")
ads = {}
for r in q(c, f"""SELECT ad_group.id, ad_group.name, ad_group_ad.ad.id,
                  ad_group_ad.status, ad_group_ad.policy_summary.approval_status,
                  ad_group_ad.policy_summary.review_status,
                  ad_group_ad.ad.final_urls
                  FROM ad_group_ad
                  WHERE ad_group.id IN ({agids})
                    AND ad_group_ad.status != 'REMOVED'"""):
    ads.setdefault(str(r.ad_group.id), []).append(
        {"ad_id": str(r.ad_group_ad.ad.id), "status": E(r.ad_group_ad.status),
         "approval": E(r.ad_group_ad.policy_summary.approval_status),
         "review": E(r.ad_group_ad.policy_summary.review_status),
         "url": list(r.ad_group_ad.ad.final_urls)})
tot_ads = sum(len(v) for v in ads.values())
print(f"   {tot_ads} ads across {len(ads)} ad groups")
for n, agid in made["ad_groups"].items():
    got = ads.get(agid, [])
    if AG[n]["verdict"] == "READY":
        check(f"ads exist {n}", len(got) >= 2, len(got))
        for a in got:
            check(f"ad url {n}", a["url"] and a["url"][0] == AG[n]["url"],
                  f"{a['url']} != {AG[n]['url']}")
    else:
        check(f"NO ads on held ad group {n}", len(got) == 0,
              f"{len(got)} ads present on a held ad group")

print("\n=== ASSETS ON NEW CAMPAIGNS ===")
asset = {}
for r in q(c, f"""SELECT campaign.id, campaign.status, campaign_asset.field_type, asset.id
                  FROM campaign_asset
                  WHERE campaign.id IN ({ids})
                    AND campaign_asset.status != 'REMOVED'"""):
    asset.setdefault(str(r.campaign.id), {}).setdefault(
        E(r.campaign_asset.field_type), []).append(str(r.asset.id))
for k, cid_ in ALL_C.items():
    a = asset.get(cid_, {})
    print(f"   {k:4s} " + "  ".join(f"{ft}x{len(v)}" for ft, v in sorted(a.items())))
    if not CAMPAIGNS[k]["reuse"]:
        check(f"{k} call asset", "407995613637" in a.get("CALL", []), a.get("CALL"))
        check(f"{k} business name", "80516971145" in a.get("BUSINESS_NAME", []),
              a.get("BUSINESS_NAME"))
        check(f"{k} 5 callouts", len(a.get("CALLOUT", [])) == 5, len(a.get("CALLOUT", [])))
        check(f"{k} 3 sitelinks", len(a.get("SITELINK", [])) == 3,
              len(a.get("SITELINK", [])))
        check(f"{k} snippet", len(a.get("STRUCTURED_SNIPPET", [])) == 1,
              len(a.get("STRUCTURED_SNIPPET", [])))

print("\n=== CALL ASSET SCHEDULE ===")
for r in q(c, """SELECT asset.id, asset.call_asset.phone_number,
                 asset.call_asset.ad_schedule_targets
                 FROM asset WHERE asset.id = 407995613637"""):
    rows = [(E(t.day_of_week), t.start_hour, t.end_hour)
            for t in r.asset.call_asset.ad_schedule_targets]
    print(f"   {r.asset.call_asset.phone_number}  {len(rows)} rows  {sorted(rows)}")
    check("call asset 5 rows", len(rows) == 5, rows)
    check("call asset no weekend",
          not any(d in ("SATURDAY", "SUNDAY") for d, _, _ in rows), rows)
    check("call asset 08-16", all(s == 8 and e == 16 for _, s, e in rows), rows)
    check("call asset phone unchanged",
          r.asset.call_asset.phone_number.replace(" ", "").replace("(", "")
          .replace(")", "").replace("-", "") == "4107056354",
          r.asset.call_asset.phone_number)

print("\n=== COOLING (must be untouched after stage A) ===")
cool = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                 campaign_budget.amount_micros
                 FROM campaign
                 WHERE campaign.id IN (24132507741, 24132507750, 24132507747,
                                       24132507753)"""):
    cool[str(r.campaign.id)] = {"status": E(r.campaign.status),
                                "daily": round(r.campaign_budget.amount_micros / 1e6, 2)}
for cid_, v in cool.items():
    print(f"   {cid_}  {v['status']:8s} ${v['daily']:.2f}")
if args.after == "A":
    check("cooling still ENABLED after stage A",
          all(v["status"] == "ENABLED" for v in cool.values()), cool)

en = {k: v for k, v in live_c.items() if v["status"] == "ENABLED"}
print(f"\n=== ENABLED DAILY TOTAL (in-scope campaigns) ${sum(v['daily'] for v in en.values()):.2f}")

print(f"\n=== READBACK: {len(out['assertions'])} assertions, {out['FAIL']} FAIL ===")
LIVE.mkdir(parents=True, exist_ok=True)
p = LIVE / f"AMB-0922-READBACK-{STAMP}-{args.after}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"WROTE {p}")
print("EXTERNAL WRITES: 0")
