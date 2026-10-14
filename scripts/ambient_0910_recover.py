#!/usr/bin/env python3
"""2026-09-10 EXECUTION RUN: reboot-safe recovery, identity gate, full before-state snapshot,
change history, fingerprint reproduction and package classification."""
from __future__ import annotations
import sys, json, hashlib, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

c = client()
STAMP = datetime.datetime.now(TZ).isoformat()
out = {"run": "2026-09-10 EXECUTION", "started_local": STAMP}

print("=== 1. SIX-FIELD IDENTITY GATE ===")
ident = identity_gate(c)
out["identity"] = ident
for k in ("descriptive_name", "customer_id", "manager", "test_account", "time_zone", "currency"):
    print(f"  {k:<20} {ident[k]}")

print("\n=== 2. ACCOUNT-LOCAL CLOCK ===")
t = q(c, "SELECT segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros "
         "FROM customer WHERE segments.date DURING TODAY")
y = q(c, "SELECT segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros "
         "FROM customer WHERE segments.date DURING YESTERDAY")
TODAY = t[0].segments.date if t else None
YEST = y[0].segments.date if y else None
print(f"  TODAY (partial): {TODAY}  " +
      (f"impr={t[0].metrics.impressions} clicks={t[0].metrics.clicks} "
       f"cost=${t[0].metrics.cost_micros/1e6:.2f}" if t else "no rows = zero delivery"))
print(f"  YESTERDAY      : {YEST}  " +
      (f"impr={y[0].metrics.impressions} clicks={y[0].metrics.clicks} "
       f"cost=${y[0].metrics.cost_micros/1e6:.2f}" if y else "no rows"))
LAST_SETTLED = YEST or "2026-09-09"
out["today_partial"], out["last_settled"] = TODAY, LAST_SETTLED
print(f"  -> LATEST SETTLED DATE: {LAST_SETTLED}")

print("\n=== 3. FULL BEFORE-STATE SNAPSHOT ===")
snap = {"taken_local": STAMP}

camps = {}
for r in q(c, "SELECT campaign.id, campaign.name, campaign.status, "
              "campaign.advertising_channel_type, campaign.serving_status, "
              "campaign.bidding_strategy_type, campaign.bidding_strategy, "
              "campaign.campaign_budget, campaign.target_spend.cpc_bid_ceiling_micros, "
              "campaign.geo_target_type_setting.positive_geo_target_type, "
              "campaign.geo_target_type_setting.negative_geo_target_type, "
              "campaign.network_settings.target_google_search, "
              "campaign.network_settings.target_search_network, "
              "campaign.network_settings.target_content_network "
              "FROM campaign WHERE campaign.status != 'REMOVED'"):
    x = r.campaign
    camps[str(x.id)] = {
        "name": x.name, "status": E(x.status), "channel": E(x.advertising_channel_type),
        "serving": E(x.serving_status), "bidding": E(x.bidding_strategy_type),
        "portfolio_strategy": x.bidding_strategy.split("/")[-1] if x.bidding_strategy else None,
        "budget": x.campaign_budget.split("/")[-1], "ceiling_micros":
            x.target_spend.cpc_bid_ceiling_micros,
        "positive_geo": E(x.geo_target_type_setting.positive_geo_target_type),
        "negative_geo": E(x.geo_target_type_setting.negative_geo_target_type),
        "net_search": x.network_settings.target_google_search,
        "net_partners": x.network_settings.target_search_network,
        "net_display": x.network_settings.target_content_network}
snap["campaigns"] = camps
print(f"  campaigns non-removed: {len(camps)}  "
      f"({sum(1 for v in camps.values() if v['status']=='ENABLED')} ENABLED)")
for cid in FIVE:
    v = camps[cid]
    print(f"    {NAME[cid]:<20} {v['status']:<8} {v['bidding']:<14} "
          f"ceiling=${v['ceiling_micros']/1e6:>6.2f} budget={v['budget']} "
          f"portfolio={v['portfolio_strategy']} geo={v['positive_geo']}")

buds = {}
for r in q(c, "SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros, "
              "campaign_budget.status, campaign_budget.explicitly_shared, "
              "campaign_budget.reference_count, campaign_budget.delivery_method, "
              "campaign_budget.type FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'"):
    x = r.campaign_budget
    buds[str(x.id)] = {"name": x.name, "amount_micros": x.amount_micros,
                       "daily": round(x.amount_micros/1e6, 2), "status": E(x.status),
                       "explicitly_shared": x.explicitly_shared,
                       "reference_count": x.reference_count,
                       "delivery": E(x.delivery_method), "type": E(x.type_)}
snap["budgets"] = buds
FIVE_B = ["15787409435", "15787409438", "15787409441", "15787409444", "15787409447"]
print(f"\n  the five budgets (shared? / refs):")
tot = 0.0
for b in FIVE_B:
    v = buds[b]
    tot += v["daily"]
    print(f"    {b}  ${v['daily']:>8.2f}  explicitly_shared={v['explicitly_shared']}  "
          f"refs={v['reference_count']}  {v['delivery']}  {v['type']}")
print(f"    COMBINED DAILY = ${tot:.2f}")
snap["five_budget_total"] = round(tot, 2)

mods = []
for r in q(c, f"SELECT campaign.id, campaign_criterion.type, campaign_criterion.criterion_id, "
              f"campaign_criterion.bid_modifier, campaign_criterion.status, "
              f"campaign_criterion.device.type FROM campaign_criterion "
              f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.bid_modifier != 1.0"):
    x = r.campaign_criterion
    mods.append({"camp": NAME[str(r.campaign.id)], "type": E(x.type_),
                 "bid_modifier": round(x.bid_modifier, 4), "status": E(x.status),
                 "device": E(x.device.type_)})
agm = []
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group_bid_modifier.bid_modifier, "
              f"ad_group_bid_modifier.device.type FROM ad_group_bid_modifier "
              f"WHERE campaign.id IN ({IN5})"):
    if abs((r.ad_group_bid_modifier.bid_modifier or 1.0) - 1.0) > 1e-9:
        agm.append({"camp": NAME[str(r.campaign.id)], "ag": str(r.ad_group.id),
                    "bid_modifier": round(r.ad_group_bid_modifier.bid_modifier, 4),
                    "device": E(r.ad_group_bid_modifier.device.type_)})
snap["bid_modifiers"] = {"campaign": mods, "ad_group": agm}
raising = [m for m in mods + agm if m["bid_modifier"] > 1.0]
print(f"\n  bid modifiers != 1.0: campaign {len(mods)}, ad group {len(agm)}")
print(f"  modifiers ABOVE 1.0 (could raise effective bid): {len(raising)}")
for m in mods:
    print(f"    {m['camp']:<20} {m['type']:<10} x{m['bid_modifier']} device={m['device']}")

ags, kws, agneg = [], [], []
for r in q(c, "SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id "
              "FROM ad_group WHERE ad_group.status != 'REMOVED'"):
    ags.append({"id": str(r.ad_group.id), "name": r.ad_group.name,
                "status": E(r.ad_group.status), "camp": str(r.campaign.id)})
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group.status, "
              f"ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
              f"ad_group_criterion.keyword.match_type, ad_group_criterion.status, "
              f"ad_group_criterion.negative, ad_group_criterion.system_serving_status, "
              f"ad_group_criterion.final_urls FROM ad_group_criterion "
              f"WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type = 'KEYWORD'"):
    x = r.ad_group_criterion
    rec = {"camp": str(r.campaign.id), "ag": str(r.ad_group.id),
           "ag_status": E(r.ad_group.status), "crit": str(x.criterion_id),
           "text": x.keyword.text, "match": E(x.keyword.match_type), "status": E(x.status),
           "serving": E(x.system_serving_status), "final_urls": list(x.final_urls)}
    (agneg if x.negative else kws).append(rec)
snap["ad_groups"], snap["five_positive_keywords"], snap["five_ad_group_negatives"] = ags, kws, agneg
live_kw = [k for k in kws if k["status"] == "ENABLED" and k["ag_status"] == "ENABLED"]
print(f"\n  ad groups non-removed: {len(ags)}")
print(f"  five-campaign positive keyword rows: {len(kws)}  LIVE(enabled x2): {len(live_kw)}")
for k in sorted(live_kw, key=lambda k: (NAME[k["camp"]], k["match"])):
    print(f"    {NAME[k['camp']]:<20} {k['match']:<7} {k['serving']:<10} crit={k['crit']:<14} "
          f"[{k['text']}]")
print(f"  five-campaign ad-group negatives: {len(agneg)}")

cneg = []
for r in q(c, "SELECT campaign.id, campaign_criterion.criterion_id, "
              "campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, "
              "campaign_criterion.status FROM campaign_criterion "
              "WHERE campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE "
              "AND campaign_criterion.status = 'ENABLED'"):
    x = r.campaign_criterion
    cneg.append({"camp": str(r.campaign.id), "crit": str(x.criterion_id),
                 "text": x.keyword.text, "match": E(x.keyword.match_type)})
snap["campaign_negatives_enabled"] = cneg
on5 = [n for n in cneg if n["camp"] in FIVE]
print(f"\n  ENABLED campaign negatives account-wide: {len(cneg)}  on the five: {len(on5)}")
print(f"    by campaign: {dict(Counter(NAME[n['camp']] for n in on5))}")

acct = []
for r in q(c, "SELECT shared_criterion.resource_name, shared_criterion.criterion_id, "
              "shared_criterion.keyword.text, shared_criterion.keyword.match_type "
              "FROM shared_criterion WHERE shared_set.id = 11252984411"):
    x = r.shared_criterion
    acct.append({"rn": x.resource_name, "crit": str(x.criterion_id), "text": x.keyword.text,
                 "match": E(x.keyword.match_type)})
snap["account_level_negatives"] = acct
links = [{"camp": str(r.campaign.id),
          "set": r.campaign_shared_set.shared_set.split("/")[-1],
          "status": E(r.campaign_shared_set.status)}
         for r in q(c, "SELECT campaign.id, campaign_shared_set.shared_set, "
                       "campaign_shared_set.status FROM campaign_shared_set")]
snap["campaign_shared_sets"] = links
print(f"  account-level set 11252984411 members: {len(acct)}")
print(f"  shared sets attached to the five: "
      f"{len([l for l in links if l['camp'] in FIVE])}")

ads = []
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, "
              f"ad_group_ad.policy_summary.approval_status, ad_group_ad.ad_strength, "
              f"ad_group_ad.ad.final_urls FROM ad_group_ad WHERE campaign.id IN ({IN5})"):
    x = r.ad_group_ad
    ads.append({"camp": str(r.campaign.id), "ag": str(r.ad_group.id), "ad": str(x.ad.id),
                "status": E(x.status), "approval": E(x.policy_summary.approval_status),
                "strength": E(x.ad_strength), "urls": list(x.ad.final_urls)})
snap["ads"] = ads
print(f"\n  ad rows on the five: {len(ads)}  {dict(Counter(a['status'] for a in ads))}")

geo = [{"camp": str(r.campaign.id), "crit": str(r.campaign_criterion.criterion_id),
        "geo": r.campaign_criterion.location.geo_target_constant.split("/")[-1],
        "negative": r.campaign_criterion.negative,
        "status": E(r.campaign_criterion.status)}
       for r in q(c, f"SELECT campaign.id, campaign_criterion.criterion_id, "
                     f"campaign_criterion.location.geo_target_constant, "
                     f"campaign_criterion.negative, campaign_criterion.status "
                     f"FROM campaign_criterion WHERE campaign.id IN ({IN5}) "
                     f"AND campaign_criterion.type = 'LOCATION'")]
snap["geo_criteria"] = geo
sched = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                 f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'AD_SCHEDULE'"))
snap["ad_schedule_count"] = sched
snap["ip_blocks"] = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                             "WHERE campaign_criterion.type = 'IP_BLOCK'"))
snap["ip_blocks_on_five"] = len(q(c, f"SELECT campaign_criterion.criterion_id FROM "
                                     f"campaign_criterion WHERE campaign.id IN ({IN5}) "
                                     f"AND campaign_criterion.type = 'IP_BLOCK'"))
sav = [g for g in geo if g["geo"] == "1018704" and not g["negative"]
       and g["status"] == "ENABLED"]
print(f"  geo criteria on the five: {len(geo)}  (negatives: "
      f"{sum(1 for g in geo if g['negative'])})")
print(f"  Savage MD (1018704) ENABLED positive targets: {len(sav)} / 5")
print(f"  ad schedules on the five: {sched}")
print(f"  IP blocks: account {snap['ip_blocks']}, on the five {snap['ip_blocks_on_five']}")

ca = [{"id": str(r.conversion_action.id), "name": r.conversion_action.name,
       "status": E(r.conversion_action.status),
       "primary_for_goal": r.conversion_action.primary_for_goal,
       "category": E(r.conversion_action.category), "type": E(r.conversion_action.type_)}
      for r in q(c, "SELECT conversion_action.id, conversion_action.name, "
                    "conversion_action.status, conversion_action.primary_for_goal, "
                    "conversion_action.category, conversion_action.type FROM conversion_action "
                    "WHERE conversion_action.status != 'REMOVED'")]
snap["conversion_actions"] = ca
snap["customer_conversion_goals"] = [
    {"category": E(r.customer_conversion_goal.category),
     "origin": E(r.customer_conversion_goal.origin),
     "biddable": r.customer_conversion_goal.biddable}
    for r in q(c, "SELECT customer_conversion_goal.category, customer_conversion_goal.origin, "
                  "customer_conversion_goal.biddable FROM customer_conversion_goal")]
snap["goal_config_levels"] = [
    {"camp": NAME[str(r.campaign.id)],
     "level": E(r.conversion_goal_campaign_config.goal_config_level)}
    for r in q(c, f"SELECT campaign.id, conversion_goal_campaign_config.goal_config_level "
                  f"FROM conversion_goal_campaign_config WHERE campaign.id IN ({IN5})")]
snap["manager_links"] = ident["manager_links"]
snap["tracking_url_template_is_clickcease"] = "clickcease" in (
    ident.get("tracking_url_template") or "").lower()
print(f"  conversion actions non-removed: {len(ca)}  "
      f"primary_for_goal: {sum(1 for x in ca if x['primary_for_goal'])}")
print(f"  goal_config_level: {set(x['level'] for x in snap['goal_config_levels'])}")

sp = SNAP / f"before-state-2026-09-10.json"
sp.parent.mkdir(parents=True, exist_ok=True)
sp.write_text(json.dumps(snap, indent=1, default=str), encoding="utf-8")
print(f"\n  WROTE {sp.relative_to(ROOT)}  sha256="
      f"{hashlib.sha256(sp.read_bytes()).hexdigest()[:16]}")
out["snapshot_file"] = str(sp.relative_to(ROOT))

print("\n=== 4. CHANGE HISTORY SINCE THE THIRD-PASS SNAPSHOT ===")
ch = []
for r in q(c, """
    SELECT change_event.change_date_time, change_event.change_resource_type,
           change_event.change_resource_name, change_event.client_type,
           change_event.user_email, change_event.resource_change_operation,
           change_event.changed_fields, change_event.campaign
    FROM change_event
    WHERE change_event.change_date_time >= '2026-09-09 00:00:00'
      AND change_event.change_date_time <= '2026-09-10 23:59:59'
    ORDER BY change_event.change_date_time DESC LIMIT 10000
"""):
    x = r.change_event
    ch.append({"ts": x.change_date_time, "type": E(x.change_resource_type),
               "rn": x.change_resource_name, "client_type": E(x.client_type),
               "user_email": x.user_email, "op": E(x.resource_change_operation),
               "fields": list(x.changed_fields.paths) if x.changed_fields else [],
               "campaign": x.campaign.split("/")[-1] if x.campaign else None})
out["change_events_since_0909"] = ch
print(f"  change events 2026-09-09 00:00 .. now: {len(ch)}")
print(f"  by (type, op, client_type): "
      f"{dict(Counter((r['type'], r['op'], r['client_type']) for r in ch))}")
after = [r for r in ch if r["ts"] > "2026-09-10 00:00:00"]
print(f"  events after 2026-09-10 00:00 (i.e. after the third-pass run): {len(after)}")
for r in after[:20]:
    print(f"    {r['ts'][:19]} {r['type']} {r['op']} {r['client_type']} {r['user_email']} "
          f"{r['fields']}")

print("\n=== 5. PACKAGE CLASSIFICATION ===")
negkey = {(n["camp"], n["crit"]) for n in cneg}
acctrn = {a["rn"] for a in acct}
adkey = {(a["ag"], a["ad"]): a for a in ads}
present_neg = {(n["camp"], n["match"], n["text"].strip().lower()) for n in cneg}
PKG = ["AMB-0909C-BUD-1", "AMB-0909C-COMP-1", "AMB-0909-ADS-1", "AMB-0909C-NEG-SAVAGE",
       "AMB-0909C-NEG-COMMERCIAL", "AMB-0909C-CPC-INST-2"]
cls = {}
for name in PKG:
    p = json.loads((CLIENT_DIR / "plans" / f"{name}.json").read_text(encoding="utf-8"))
    rec = approval_code({"target": p["target"], "plan": p["plan_name"],
                         "operations": p["operations"]})
    exact = rec == p["fingerprint"]
    st, notes = "UNEXECUTED_AND_EXACT", []
    for a in p["operations"]:
        o = a["operation"]
        if o == "UPDATE_CAMPAIGN_BUDGET":
            cur = buds[a["resource_id"]]["amount_micros"]
            want = int(a["current_state"].split("= ")[1].split(" ")[0])
            tgt = int(a["proposed_state"].split("= ")[1].split(" ")[0])
            if cur == tgt:
                st = "ALREADY_EXECUTED"
            elif cur != want:
                st, _ = "DRIFTED", notes.append(f"budget {a['resource_id']} live {cur} != {want}")
        elif o == "SET_MAXIMIZE_CLICKS_CPC_BID_CEILING":
            cur = camps[a["resource_id"]]["ceiling_micros"]
            want = int(a["current_state"].split("= ")[1].split(" ")[0])
            tgt = int(a["proposed_state"].split("= ")[1].split(" ")[0])
            if cur == tgt:
                st = "ALREADY_EXECUTED"
            elif cur != want:
                st, _ = "DRIFTED", notes.append(f"ceiling live {cur} != {want}")
        elif o == "REMOVE_CAMPAIGN_NEGATIVE_KEYWORD":
            if (a["campaign_id"], a["criterion_id"]) not in negkey:
                st, _ = "ALREADY_EXECUTED", notes.append(
                    f"{a['negative_text']!r} on {a['campaign']} no longer live")
        elif o == "REMOVE_SHARED_LIST_NEGATIVE":
            if a["shared_criterion_resource_name"] not in acctrn:
                st, _ = "ALREADY_EXECUTED", notes.append("account-level member gone")
        elif o == "ADD_CAMPAIGN_NEGATIVE_KEYWORD":
            if (a["campaign_id"], a["match_type"],
                    a["negative_text"].strip().lower()) in present_neg:
                st, _ = "ALREADY_EXECUTED", notes.append(f"{a['negative_text']!r} already present")
        elif o == "PAUSE_AD_GROUP_AD":
            x = adkey.get((a["ad_group_id"], a["ad_id"]))
            if not x:
                st, _ = "DRIFTED", notes.append(f"ad {a['ad_id']} missing")
            elif x["status"] == "PAUSED":
                st, _ = "ALREADY_EXECUTED", notes.append(f"ad {a['ad_id']} already PAUSED")
            elif x["status"] != "ENABLED" or x["approval"] != "DISAPPROVED":
                st, _ = "DRIFTED", notes.append(
                    f"ad {a['ad_id']} now {x['status']}/{x['approval']}")
    if not exact:
        st = "DRIFTED"
        notes.append(f"fingerprint recomputes to {rec}")
    cls[name] = {"fingerprint": p["fingerprint"], "recomputed": rec, "exact": exact,
                 "ops": p["object_count"], "status": st, "notes": notes,
                 "class": p["approval_class"]}
    print(f"  {name:<28} {p['fingerprint']}  ops={p['object_count']:<3} "
          f"exact={str(exact):<6} -> {st}")
    for n in notes:
        print(f"      {n}")
out["package_classification"] = cls

print("\n=== 6. DO_NOT_EXECUTE REGISTER ===")
DNE = ["752BF95EBD7C", "DE376F91F449", "05FBCBD34B4A", "18143479027D", "46C39C6B7091",
       "D448BFDE4650", "23BE8FF0F24C", "CE289F3508A2", "A435FA09AC97"]
for f in DNE:
    print(f"  {f}  DO_NOT_EXECUTE (confirmed)")
out["do_not_execute"] = DNE

write(EVID / "2026-09-10-recovery-and-classification.json", out)
