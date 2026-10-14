#!/usr/bin/env python3
"""Ambient | 2026-09-21b | Full cooling + heating inventory ahead of the 31-service transition.

READ-ONLY. EXTERNAL WRITES: 0.

Three jobs:

  1. COOLING PAUSE SCOPE. The four residential cooling campaigns, every child ad group,
     keyword, ad and asset link, with current status and IDs recorded for rollback.
     Campaign 24132507747 (HVAC Installation) is known to carry a Commercial HVAC
     Installation ad group, which is NOT part of the cooling pause, so the pause scope has
     to be resolved at ad-group level there rather than at campaign level.

  2. HEATING RESOURCES TO REUSE. Everything the three completed plans created, so the new
     build reuses instead of duplicating.

  3. CANONICAL NAME COLLISION CHECK. Every non-removed campaign and ad group name in the
     account, so the seven new campaign names and ~29 new ad-group names cannot silently
     collide with something that already exists.
"""
from __future__ import annotations
import sys, json, datetime, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21b"
COOLING = {
    "24132507741": "AC Repair",
    "24132507750": "HVAC Repair",
    "24132507747": "HVAC Installation (may carry Commercial)",
    "24132507753": "HVAC Replacement",
}
HEATING_KEEP = {
    "24132507744": "Gas Boiler Repair - HEATING, never pause",
    "24257819463": "Heating Repair - paused, built 2026-09-17",
    "24257819466": "Heating Installation - paused, built 2026-09-17",
}
COMMERCIAL = re.compile(r"commercial", re.I)


def main():
    c = client()
    identity_gate(c, verbose=True)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0}

    # ------------------------------------------------------------ campaigns
    camps = {}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                     campaign.advertising_channel_type, campaign.bidding_strategy_type,
                     campaign.target_spend.cpc_bid_ceiling_micros,
                     campaign_budget.id, campaign_budget.amount_micros,
                     campaign_budget.explicitly_shared, campaign_budget.name,
                     campaign.primary_status
                     FROM campaign WHERE campaign.status != 'REMOVED'"""):
        x = r.campaign
        camps[str(x.id)] = {
            "name": x.name, "status": E(x.status), "channel": E(x.advertising_channel_type),
            "bidding": E(x.bidding_strategy_type),
            "ceiling": round(x.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
            "budget_id": str(r.campaign_budget.id),
            "budget_name": r.campaign_budget.name,
            "daily": round(r.campaign_budget.amount_micros / 1e6, 2),
            "shared": r.campaign_budget.explicitly_shared,
            "primary_status": E(x.primary_status)}
    out["campaigns"] = camps

    # ------------------------------------------------------------- ad groups
    ags = {}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                     ad_group.id, ad_group.name, ad_group.status,
                     ad_group.cpc_bid_micros, ad_group.type
                     FROM ad_group WHERE ad_group.status != 'REMOVED'"""):
        ags[str(r.ad_group.id)] = {
            "name": r.ad_group.name, "status": E(r.ad_group.status),
            "campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
            "campaign_status": E(r.campaign.status),
            "cpc_bid": round(r.ad_group.cpc_bid_micros / 1e6, 2)}
    out["ad_groups"] = ags

    # -------------------------------------------- keywords / ads per ad group
    kw_count, ad_count = {}, {}
    for r in q(c, """SELECT ad_group.id, ad_group_criterion.criterion_id,
                     ad_group_criterion.status, ad_group_criterion.negative
                     FROM ad_group_criterion
                     WHERE ad_group_criterion.type = 'KEYWORD'
                       AND ad_group_criterion.status != 'REMOVED'"""):
        k = str(r.ad_group.id)
        d = kw_count.setdefault(k, {"positive": 0, "negative": 0})
        d["negative" if r.ad_group_criterion.negative else "positive"] += 1
    for r in q(c, """SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                     ad_group_ad.policy_summary.approval_status
                     FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        k = str(r.ad_group.id)
        d = ad_count.setdefault(k, {"total": 0, "enabled": 0, "disapproved": 0})
        d["total"] += 1
        if E(r.ad_group_ad.status) == "ENABLED":
            d["enabled"] += 1
        if E(r.ad_group_ad.policy_summary.approval_status) == "DISAPPROVED":
            d["disapproved"] += 1
    out["keyword_counts"] = kw_count
    out["ad_counts"] = ad_count

    # ------------------------------------------------- 1. cooling pause scope
    print("\n=== 1. RESIDENTIAL COOLING INVENTORY (pause candidates) ===")
    cool = {}
    for cid, label in COOLING.items():
        v = camps[cid]
        kids = {k: a for k, a in ags.items() if a["campaign_id"] == cid}
        commercial = {k: a for k, a in kids.items() if COMMERCIAL.search(a["name"])}
        residential = {k: a for k, a in kids.items() if k not in commercial}
        cool[cid] = {"campaign": v["name"], "status": v["status"],
                     "daily": v["daily"], "budget_id": v["budget_id"],
                     "ceiling": v["ceiling"],
                     "ad_groups_total": len(kids),
                     "commercial_ad_groups": commercial,
                     "residential_ad_groups": residential}
        print(f"\n   {cid}  {v['name'][:56]}")
        print(f"      status={v['status']}  ${v['daily']:.2f}/day  ceiling=${v['ceiling']:.2f}  "
              f"budget={v['budget_id']}")
        for k, a in sorted(kids.items(), key=lambda x: x[1]["name"]):
            kwp = kw_count.get(k, {}).get("positive", 0)
            adn = ad_count.get(k, {})
            tag = "  <<< COMMERCIAL - NOT IN COOLING PAUSE" if k in commercial else ""
            print(f"      ag {k}  {a['status']:8s} kw={kwp:3d} ads={adn.get('total', 0):2d} "
                  f"(en {adn.get('enabled', 0)}) {a['name'][:38]}{tag}")
    out["cooling_inventory"] = cool
    any_commercial = {cid: v["commercial_ad_groups"] for cid, v in cool.items()
                      if v["commercial_ad_groups"]}
    out["campaigns_with_commercial_ad_groups"] = {
        k: list(v.keys()) for k, v in any_commercial.items()}
    print(f"\n   campaigns carrying a Commercial ad group: "
          f"{ {k: list(v.keys()) for k, v in any_commercial.items()} }")
    cool_daily = round(sum(cool[c]["daily"] for c in COOLING
                          if camps[c]["status"] == "ENABLED"), 2)
    out["cooling_enabled_daily_total"] = cool_daily
    print(f"   cooling enabled daily total: ${cool_daily:.2f}")

    # ------------------------------------------------ 2. heating to reuse
    print("\n=== 2. EXISTING HEATING RESOURCES (reuse, do not duplicate) ===")
    heat = {}
    for cid, label in HEATING_KEEP.items():
        v = camps[cid]
        kids = {k: a for k, a in ags.items() if a["campaign_id"] == cid}
        heat[cid] = {"campaign": v["name"], "status": v["status"], "daily": v["daily"],
                     "budget_id": v["budget_id"], "ceiling": v["ceiling"],
                     "ad_groups": kids}
        print(f"\n   {cid}  {v['name'][:56]}  [{label}]")
        print(f"      status={v['status']}  ${v['daily']:.2f}/day  ceiling=${v['ceiling']:.2f}")
        for k, a in sorted(kids.items(), key=lambda x: x[1]["name"]):
            kwp = kw_count.get(k, {}).get("positive", 0)
            adn = ad_count.get(k, {})
            print(f"      ag {k}  {a['status']:8s} kw={kwp:3d} ads={adn.get('total', 0):2d} "
                  f"(disapp {adn.get('disapproved', 0)}) {a['name'][:40]}")
    out["heating_reuse"] = heat

    # ---------------------------------------------- 3. name collision check
    print("\n=== 3. NAME COLLISION SURFACE ===")
    out["all_campaign_names"] = {k: v["name"] for k, v in camps.items()}
    out["all_ad_group_names"] = sorted({a["name"] for a in ags.values()})
    print(f"   {len(camps)} non-removed campaigns, "
          f"{len(out['all_ad_group_names'])} distinct non-removed ad-group names")
    heatish = sorted(n for n in out["all_ad_group_names"]
                     if re.search(r"furnace|boiler|heat|thermostat|ductless|mini ?split|"
                                  r"geothermal|no heat|emergency", n, re.I))
    out["heating_like_existing_ad_group_names"] = heatish
    print(f"   heating-like existing ad-group names ({len(heatish)}):")
    for n in heatish:
        print(f"      {n}")

    en = {k: v for k, v in camps.items() if v["status"] == "ENABLED"}
    out["enabled_daily_total"] = round(sum(v["daily"] for v in en.values()), 2)
    print(f"\n   ENABLED campaigns {len(en)}, daily total "
          f"${out['enabled_daily_total']:.2f}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"full-inventory-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
