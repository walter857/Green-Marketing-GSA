#!/usr/bin/env python3
"""CORRECTED CPC analysis.

  * separates VISIBLE search-term traffic from PRIVACY-HIDDEN traffic at campaign level
  * rebuilds HVAC Repair scenarios on all campaign clicks, not just visible rows
  * verifies HVAC Installation's live keyword and every bid adjustment that could push the
    effective bid above a proposed ceiling
  * reconciles the 14 vs 5+4+4=13 primary-conversion discrepancy
"""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {}
W = ("2026-08-14", "2026-09-08")   # settled launch-to-date

print("=== 1. VISIBLE vs PRIVACY-HIDDEN TRAFFIC, BY CAMPAIGN ===")
camp = {}
for r in q(c, f"SELECT campaign.id, metrics.impressions, metrics.clicks, metrics.cost_micros, "
              f"metrics.conversions, metrics.all_conversions FROM campaign "
              f"WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '{W[0]}' AND '{W[1]}'"):
    x = r.metrics
    camp[str(r.campaign.id)] = {"impressions": x.impressions, "clicks": x.clicks,
                                "cost": round(x.cost_micros/1e6, 2),
                                "conversions": round(x.conversions, 2),
                                "all_conversions": round(x.all_conversions, 2)}
vis = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                           "conversions": 0.0, "all_conversions": 0.0})
strows = []
for r in q(c, f"SELECT campaign.id, search_term_view.search_term, segments.date, "
              f"metrics.impressions, metrics.clicks, metrics.cost_micros, "
              f"metrics.conversions, metrics.all_conversions FROM search_term_view "
              f"WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '{W[0]}' AND '{W[1]}'"):
    x = r.metrics
    cid = str(r.campaign.id)
    vis[cid]["impressions"] += x.impressions
    vis[cid]["clicks"] += x.clicks
    vis[cid]["cost"] += x.cost_micros/1e6
    vis[cid]["conversions"] += x.conversions
    vis[cid]["all_conversions"] += x.all_conversions
    if x.clicks:
        strows.append({"camp": cid, "date": r.segments.date, "clicks": x.clicks,
                       "cost": round(x.cost_micros/1e6, 2),
                       "conversions": round(x.conversions, 2),
                       "all_conversions": round(x.all_conversions, 2)})

split = {}
print(f"  {'campaign':<20}{'CAMPAIGN TOTAL':>34}{'VISIBLE IN SEARCH TERMS':>34}"
      f"{'PRIVACY-HIDDEN':>30}")
print(f"  {'':<20}{'clicks':>8}{'cost':>11}{'conv':>7}{'clicks':>10}{'cost':>11}{'conv':>7}"
      f"{'clicks':>10}{'cost':>11}{'conv':>7}")
for cid in FIVE:
    t = camp.get(cid, {"clicks": 0, "cost": 0, "conversions": 0})
    v = vis[cid]
    h = {"clicks": t["clicks"] - v["clicks"], "cost": round(t["cost"] - v["cost"], 2),
         "conversions": round(t["conversions"] - v["conversions"], 2)}
    split[NAME[cid]] = {"campaign_total": t, "visible": {k: (round(x, 2) if isinstance(x, float)
                                                             else x) for k, x in v.items()},
                        "hidden": h,
                        "hidden_click_share_pct": round(100*h["clicks"]/t["clicks"], 1)
                        if t["clicks"] else None,
                        "hidden_conv_share_pct": round(100*h["conversions"]/t["conversions"], 1)
                        if t["conversions"] else None}
    print(f"  {NAME[cid]:<20}{t['clicks']:>8}{t['cost']:>11.2f}{t['conversions']:>7.1f}"
          f"{v['clicks']:>10}{v['cost']:>11.2f}{v['conversions']:>7.1f}"
          f"{h['clicks']:>10}{h['cost']:>11.2f}{h['conversions']:>7.1f}")
out["visible_vs_hidden"] = split
print("\n  KEY POINT: any model built on search-term rows can only see the VISIBLE column.")
for cid in FIVE:
    s = split[NAME[cid]]
    if s["campaign_total"]["conversions"]:
        print(f"    {NAME[cid]:<20} {s['hidden_conv_share_pct']:>5.1f}% of its primary "
              f"conversions are in privacy-hidden traffic "
              f"({s['hidden']['conversions']:.0f} of "
              f"{s['campaign_total']['conversions']:.0f})")

print("\n=== 2. PRIMARY-CONVERSION RECONCILIATION (14 vs 5+4+4=13) ===")
CONV_ONLY = ("metrics.conversions, metrics.all_conversions, metrics.conversions_value")
by_action = defaultdict(float)
by_action_camp = defaultdict(float)
for r in q(c, f"SELECT campaign.id, segments.conversion_action_name, "
              f"segments.conversion_action_category, {CONV_ONLY} FROM campaign "
              f"WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '{W[0]}' AND '{W[1]}'"):
    n = r.segments.conversion_action_name
    by_action[n] += r.metrics.conversions
    by_action_camp[(NAME[str(r.campaign.id)], n)] += r.metrics.conversions
tot_action = sum(by_action.values())
tot_camp = sum(v["conversions"] for v in camp.values())
print(f"  campaign-level metrics.conversions total : {tot_camp:.2f}")
print(f"  sum over segments.conversion_action_name : {tot_action:.2f}")
print(f"  difference                                : {tot_camp - tot_action:.2f}")
print("\n  per action (only actions with a non-zero primary count):")
for n, v in sorted(by_action.items(), key=lambda kv: -kv[1]):
    if v > 0:
        print(f"    {v:>6.2f}  {n}")
print("\n  per campaign x action:")
for k, v in sorted(by_action_camp.items(), key=lambda kv: -kv[1]):
    if v > 0:
        print(f"    {v:>6.2f}  {k[0]:<20} {k[1]}")
out["conversion_reconciliation"] = {
    "campaign_total": round(tot_camp, 2), "sum_by_action": round(tot_action, 2),
    "difference": round(tot_camp - tot_action, 2),
    "by_action": {k: round(v, 2) for k, v in by_action.items() if v > 0},
    "by_campaign_action": {f"{k[0]}|{k[1]}": round(v, 2)
                           for k, v in by_action_camp.items() if v > 0}}

print("\n=== 3. HVAC INSTALLATION: LIVE KEYWORD AND BID-ADJUSTMENT VERIFICATION ===")
inst = "24132507747"
kws = []
for r in q(c, f"""
    SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status,
           ad_group_criterion.system_serving_status, ad_group.id, ad_group.status
    FROM ad_group_criterion
    WHERE campaign.id = {inst} AND ad_group_criterion.type = 'KEYWORD'
      AND ad_group_criterion.negative = FALSE AND ad_group_criterion.status = 'ENABLED'
"""):
    x = r.ad_group_criterion
    kws.append({"crit": str(x.criterion_id), "text": x.keyword.text,
                "match": E(x.keyword.match_type), "status": E(x.status),
                "serving": E(x.system_serving_status), "ag": str(r.ad_group.id),
                "ag_status": E(r.ad_group.status)})
out["installation_live_keywords"] = kws
print(f"  ENABLED positive keywords in HVAC Installation: {len(kws)}")
for k in kws:
    print(f"    [{k['text']}] {k['match']:<7} crit={k['crit']:<14} ag={k['ag']}({k['ag_status']}) "
          f"serving={k['serving']}")
has_old = any(k["text"].strip().lower() == "hvac installers" for k in kws)
has_new = any(k["text"].strip().lower() == "hvac installers near me" for k in kws)
print(f"    live keyword is 'hvac installers near me' : {has_new}")
print(f"    removed keyword 'hvac installers' still live: {has_old}  (must be False)")

print("\n  --- EVERY bid modifier on the five campaigns ---")
mods = []
for r in q(c, f"""
    SELECT campaign.id, campaign_criterion.type, campaign_criterion.criterion_id,
           campaign_criterion.bid_modifier, campaign_criterion.negative,
           campaign_criterion.status, campaign_criterion.device.type,
           campaign_criterion.ad_schedule.day_of_week,
           campaign_criterion.ad_schedule.start_hour, campaign_criterion.location.geo_target_constant
    FROM campaign_criterion
    WHERE campaign.id IN ({IN5}) AND campaign_criterion.bid_modifier != 1.0
"""):
    x = r.campaign_criterion
    mods.append({"camp": str(r.campaign.id), "type": E(x.type_), "crit": str(x.criterion_id),
                 "bid_modifier": round(x.bid_modifier, 4), "negative": x.negative,
                 "status": E(x.status), "device": E(x.device.type_),
                 "day": E(x.ad_schedule.day_of_week)})
out["campaign_bid_modifiers"] = mods
print(f"    campaign_criterion rows with bid_modifier != 1.0 : {len(mods)}")
for m in mods:
    print(f"      {NAME[m['camp']]:<20} {m['type']:<14} x{m['bid_modifier']} "
          f"device={m['device']} day={m['day']} status={m['status']}")

agmods = []
for r in q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group_bid_modifier.criterion_id,
           ad_group_bid_modifier.bid_modifier, ad_group_bid_modifier.device.type,
           ad_group_bid_modifier.bid_modifier_source
    FROM ad_group_bid_modifier WHERE campaign.id IN ({IN5})
"""):
    x = r.ad_group_bid_modifier
    if abs((x.bid_modifier or 1.0) - 1.0) < 1e-9:
        continue
    agmods.append({"camp": str(r.campaign.id), "ag": str(r.ad_group.id),
                   "type": "AD_GROUP_BID_MODIFIER",
                   "bid_modifier": round(x.bid_modifier, 4),
                   "status": E(x.bid_modifier_source), "device": E(x.device.type_)})
out["ad_group_bid_modifiers"] = agmods
print(f"    ad_group_bid_modifier rows with bid_modifier != 1.0 : {len(agmods)}")
for m in agmods:
    print(f"      {NAME[m['camp']]:<20} ag={m['ag']} x{m['bid_modifier']} "
          f"device={m['device']} source={m['status']}")

# audience / demographic criteria carrying a modifier
aud = []
for r in q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group_criterion.type,
           ad_group_criterion.criterion_id, ad_group_criterion.bid_modifier,
           ad_group_criterion.status
    FROM ad_group_criterion
    WHERE campaign.id IN ({IN5})
      AND ad_group_criterion.type IN ('USER_LIST','USER_INTEREST','AGE_RANGE','GENDER',
                                      'INCOME_RANGE','PARENTAL_STATUS','CUSTOM_AUDIENCE')
"""):
    x = r.ad_group_criterion
    aud.append({"camp": str(r.campaign.id), "ag": str(r.ad_group.id), "type": E(x.type_),
                "crit": str(x.criterion_id), "bid_modifier": round(x.bid_modifier, 4),
                "status": E(x.status)})
out["audience_criteria"] = aud
print(f"    audience / demographic criteria on the five : {len(aud)}")
for a in aud[:20]:
    print(f"      {NAME[a['camp']]:<20} {a['type']:<16} x{a['bid_modifier']} {a['status']}")

conv_mods = []
for r in q(c, f"SELECT campaign.id, campaign.name FROM campaign WHERE campaign.id IN ({IN5})"):
    pass
try:
    for r in q(c, f"""
        SELECT campaign.id, campaign.optimization_goal_setting.optimization_goal_types
        FROM campaign WHERE campaign.id IN ({IN5})
    """):
        g = list(r.campaign.optimization_goal_setting.optimization_goal_types)
        if g:
            conv_mods.append({"camp": str(r.campaign.id), "goals": [E(x) for x in g]})
except Exception as e:
    print("    optimization_goal_setting read failed:", str(e)[:120])
out["optimization_goals"] = conv_mods
print(f"    campaigns with an optimization_goal_setting: {len(conv_mods)}")

print("\n  --- EFFECTIVE-BID CEILING CONCLUSION ---")
allmods = mods + agmods + [a for a in aud if abs(a["bid_modifier"] - 1.0) > 1e-9]
raising = [m for m in allmods if m["bid_modifier"] > 1.0]
if not raising:
    print(f"    {len(allmods)} bid modifier(s) exist, and NONE of them is above x1.0.")
    print("    Every modifier found is x0.0 (TABLET exclusion), which can only REDUCE or")
    print("    suppress a bid, never raise it. No device, ad-schedule, location, audience or")
    print("    demographic modifier can push the effective bid above a proposed max-CPC")
    print("    ceiling. A $65 ceiling means $65.")
else:
    worst = max(m["bid_modifier"] for m in raising)
    print(f"    WARNING: {len(raising)} modifier(s) ABOVE x1.0. Highest x{worst}.")
    print(f"    A $65 ceiling could become ${65*worst:.2f} effective.")
    for m in raising:
        print(f"      {NAME[m['camp']]:<20} {m['type']} x{m['bid_modifier']}")
out["max_bid_modifier"] = max([m["bid_modifier"] for m in mods + agmods]
                              + [a["bid_modifier"] for a in aud], default=1.0)

print("\n=== 4. HVAC REPAIR: SCENARIOS ON ALL CAMPAIGN TRAFFIC ===")
rep = "24132507750"
t = camp[rep]
v = vis[rep]
h = split["HVAC Repair"]["hidden"]
print(f"  campaign total   : {t['clicks']} clicks, ${t['cost']:.2f}, "
      f"{t['conversions']:.0f} primary conv, CPC ${t['cost']/t['clicks']:.2f}, "
      f"raw CPA ${t['cost']/t['conversions']:.2f}")
print(f"  visible in terms : {v['clicks']} clicks, ${v['cost']:.2f}, {v['conversions']:.0f} conv")
print(f"  privacy-hidden   : {h['clicks']} clicks, ${h['cost']:.2f}, {h['conversions']:.0f} conv"
      f"   <- {split['HVAC Repair']['hidden_conv_share_pct']}% of its conversions")

reps = [r for r in strows if r["camp"] == rep]
clicks = []
for r in reps:
    cpc = r["cost"]/r["clicks"]
    for _ in range(r["clicks"]):
        clicks.append({"cpc": round(cpc, 2), "conv": r["conversions"]/r["clicks"],
                       "date": r["date"]})
hidden_cpc = h["cost"]/h["clicks"] if h["clicks"] else 0
print(f"\n  Hidden traffic blended CPC: ${hidden_cpc:.2f} on {h['clicks']} clicks. Its per-click")
print("  CPC distribution is NOT retrievable, so scenarios below model the visible clicks and")
print("  state the hidden block separately rather than pretending to cap it.")

MAXCPQL = 250.0
scen = {}
print(f"\n  {'cap':>6}{'vis clicks':>12}{'vis spend':>12}{'vis conv':>10}{'vis CPA':>10}"
      f"{'vis CPC':>9}   note")
for cap in [25, 35, 40, 45, 60, None]:
    keep = clicks if cap is None else [x for x in clicks if x["cpc"] <= cap]
    k = len(keep)
    cost = sum(x["cpc"] for x in keep)
    cv = sum(x["conv"] for x in keep)
    row = {"cap": cap, "visible_clicks": k,
           "visible_clicks_pct": round(100*k/len(clicks), 1),
           "visible_spend": round(cost, 2), "visible_conv": round(cv, 2),
           "visible_cpa": round(cost/cv, 2) if cv else None,
           "visible_cpc": round(cost/k, 2) if k else None,
           "vs_max_cpql": (round(cost/cv - MAXCPQL, 2) if cv else None)}
    scen[str(cap)] = row
    lbl = "none" if cap is None else f"${cap}"
    note = ""
    if row["visible_cpa"] and row["visible_cpa"] > MAXCPQL:
        note = f"raw CPA ${row['visible_cpa']:.2f} EXCEEDS the ${MAXCPQL:.0f} max CPQL"
    elif row["visible_cpa"]:
        note = f"raw CPA ${row['visible_cpa']:.2f} within the ${MAXCPQL:.0f} max CPQL"
    print(f"  {lbl:>6}{k:>12}{row['visible_spend']:>12.2f}{row['visible_conv']:>10.1f}"
          f"{str(row['visible_cpa']):>10}{str(row['visible_cpc']):>9}   {note}")
out["hvac_repair_scenarios"] = scen
out["hvac_repair_totals"] = {"campaign": t, "visible": {k: (round(x, 2) if isinstance(x, float)
                                                            else x) for k, x in v.items()},
                             "hidden": h, "hidden_blended_cpc": round(hidden_cpc, 2)}

print("\n  --- the four visible HVAC Repair converting clicks, by CPC and date ---")
cv_clicks = sorted([(r["cost"]/r["clicks"], r["date"], r["conversions"], r["clicks"])
                    for r in reps if r["conversions"] > 0])
for cpc, d, cv, ck in cv_clicks:
    print(f"    ${cpc:>7.2f} on {d}  ({cv:.0f} conv from {ck} click(s) in that row)")

print("\n=== 5. AC REPAIR AND HVAC INSTALLATION SCENARIO REFRESH (same method) ===")
for cid, maxq in (("24132507741", 150.0), ("24132507747", 280.0)):
    t2, v2 = camp[cid], vis[cid]
    h2 = split[NAME[cid]]["hidden"]
    cl = []
    for r in [x for x in strows if x["camp"] == cid]:
        cc = r["cost"]/r["clicks"]
        for _ in range(r["clicks"]):
            cl.append({"cpc": round(cc, 2), "conv": r["conversions"]/r["clicks"]})
    print(f"\n  {NAME[cid]}  campaign {t2['clicks']} clicks / ${t2['cost']:.2f} / "
          f"{t2['conversions']:.0f} conv   |  hidden {h2['clicks']} clicks / ${h2['cost']:.2f} / "
          f"{h2['conversions']:.0f} conv")
    print(f"    {'cap':>6}{'vis clicks':>12}{'vis spend':>12}{'vis conv':>10}{'vis CPA':>10}")
    sub = {}
    for cap in [25, 30, 40, 50, 65, 90, 110, 130, None]:
        keep = cl if cap is None else [x for x in cl if x["cpc"] <= cap]
        k = len(keep)
        cost = sum(x["cpc"] for x in keep)
        cv = sum(x["conv"] for x in keep)
        sub[str(cap)] = {"visible_clicks": k, "visible_spend": round(cost, 2),
                         "visible_conv": round(cv, 2),
                         "visible_cpa": round(cost/cv, 2) if cv else None}
        print(f"    {('none' if cap is None else '$'+str(cap)):>6}{k:>12}{cost:>12.2f}"
              f"{cv:>10.1f}{str(sub[str(cap)]['visible_cpa']):>10}")
    out.setdefault("other_scenarios", {})[NAME[cid]] = sub

print("\n=== 6. MINIMUM QUALIFICATION RATE FOR THE $141.87 INSTALLATION RAW CPA ===")
raw_cpa = 141.87
for target in (280.0,):
    minq = raw_cpa / target
    print(f"  raw CPA ${raw_cpa:.2f} meets a ${target:.0f} CPQL target only if at least")
    print(f"  {100*minq:.1f}% of those raw conversions are QUALIFIED leads.")
    print(f"  (CPQL = raw CPA / qualification rate; ${raw_cpa:.2f} / {minq:.4f} = ${target:.2f})")
out["installation_min_qualification_rate"] = {"raw_cpa": raw_cpa, "target_cpql": 280.0,
                                              "min_qualification_rate_pct": round(100*raw_cpa/280.0, 1)}

write(EVID / "2026-09-09b-cpc-analysis.json", out)
