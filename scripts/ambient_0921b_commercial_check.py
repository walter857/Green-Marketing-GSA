#!/usr/bin/env python3
"""Ambient | 2026-09-21b | Can the Commercial HVAC Installation ad group actually serve?

READ-ONLY. EXTERNAL WRITES: 0.

This decides the shape of the cooling pause. Campaign 24132507747 carries BOTH the
residential SKAG | HVAC Installation ad group and SKAG | Commercial HVAC Installation
199748801029, so a campaign-level pause would stop an approved commercial service.

But the inventory shows the commercial ad group has 2 ads and 0 of them ENABLED. An ad
group with no enabled, approved ad cannot serve, so before designing around it we need to
know whether it is a live service that must be protected, or a structure that is already
dark. Also pulls its all-time delivery, so "protect it" is an evidence-based call.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21b"
COMM_AG = "199748801029"
RES_AG = "202339087634"
CAMP = "24132507747"


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0}

    print("=== ADS ON BOTH AD GROUPS OF CAMPAIGN 24132507747 ===")
    ads = {}
    for r in q(c, f"""SELECT ad_group.id, ad_group.name, ad_group.status,
                      ad_group_ad.ad.id, ad_group_ad.status,
                      ad_group_ad.policy_summary.approval_status,
                      ad_group_ad.policy_summary.review_status,
                      ad_group_ad.policy_summary.policy_topic_entries,
                      ad_group_ad.ad.final_urls
                      FROM ad_group_ad
                      WHERE ad_group.id IN ({COMM_AG}, {RES_AG})
                        AND ad_group_ad.status != 'REMOVED'"""):
        topics = [e.topic for e in r.ad_group_ad.policy_summary.policy_topic_entries]
        ads[str(r.ad_group_ad.ad.id)] = {
            "ad_group_id": str(r.ad_group.id), "ad_group": r.ad_group.name,
            "ad_group_status": E(r.ad_group.status),
            "ad_status": E(r.ad_group_ad.status),
            "approval": E(r.ad_group_ad.policy_summary.approval_status),
            "review": E(r.ad_group_ad.policy_summary.review_status),
            "topics": topics, "final_urls": list(r.ad_group_ad.ad.final_urls)}
    for k, v in sorted(ads.items(), key=lambda x: (x[1]["ad_group_id"], x[0])):
        print(f"   ag {v['ad_group_id']} ad {k}  ag={v['ad_group_status']:8s} "
              f"ad={v['ad_status']:8s} {v['approval']:12s} {v['review']:16s} {v['topics']}")
        print(f"      -> {v['final_urls']}")
    out["ads"] = ads
    comm_live = [k for k, v in ads.items()
                 if v["ad_group_id"] == COMM_AG and v["ad_status"] == "ENABLED"
                 and v["approval"] in ("APPROVED", "APPROVED_LIMITED")]
    out["commercial_servable_ads"] = comm_live
    print(f"\n   commercial ad group ENABLED+APPROVED ads: {len(comm_live)} "
          f"-> {'CAN SERVE' if comm_live else 'CANNOT SERVE TODAY'}")

    print("\n=== KEYWORDS ON BOTH AD GROUPS ===")
    kws = {}
    for r in q(c, f"""SELECT ad_group.id, ad_group.name,
                      ad_group_criterion.criterion_id,
                      ad_group_criterion.keyword.text,
                      ad_group_criterion.keyword.match_type,
                      ad_group_criterion.status,
                      ad_group_criterion.approval_status,
                      ad_group_criterion.system_serving_status
                      FROM ad_group_criterion
                      WHERE ad_group.id IN ({COMM_AG}, {RES_AG})
                        AND ad_group_criterion.type = 'KEYWORD'
                        AND ad_group_criterion.negative = FALSE
                        AND ad_group_criterion.status != 'REMOVED'"""):
        x = r.ad_group_criterion
        kws[f"{r.ad_group.id}:{x.criterion_id}"] = {
            "ad_group": r.ad_group.name, "text": x.keyword.text,
            "match": E(x.keyword.match_type), "status": E(x.status),
            "approval": E(x.approval_status), "serving": E(x.system_serving_status)}
    for k, v in sorted(kws.items(), key=lambda x: x[1]["ad_group"]):
        print(f"   {v['ad_group'][:34]:34s} {v['match']:7s} '{v['text'][:34]}' "
              f"{v['status']:8s} {v['approval']:10s} {v['serving']}")
    out["keywords"] = kws

    print("\n=== ALL-TIME DELIVERY BY AD GROUP ===")
    perf = {}
    for r in q(c, f"""SELECT ad_group.id, ad_group.name,
                      metrics.impressions, metrics.clicks, metrics.cost_micros,
                      metrics.conversions, metrics.all_conversions
                      FROM ad_group
                      WHERE ad_group.id IN ({COMM_AG}, {RES_AG})
                        AND segments.date BETWEEN '2019-01-01' AND '2026-09-21'"""):
        k = str(r.ad_group.id)
        a = perf.setdefault(k, {"name": r.ad_group.name, "impr": 0, "clicks": 0,
                                "cost": 0.0, "conv": 0.0, "all_conv": 0.0})
        a["impr"] += r.metrics.impressions
        a["clicks"] += r.metrics.clicks
        a["cost"] += r.metrics.cost_micros / 1e6
        a["conv"] += r.metrics.conversions
        a["all_conv"] += r.metrics.all_conversions
    for k, a in perf.items():
        print(f"   {k}  {a['name'][:36]:36s} impr={a['impr']:6d} clicks={a['clicks']:4d} "
              f"cost=${a['cost']:8.2f} conv={a['conv']:.2f} all_conv={a['all_conv']:.2f}")
    if not perf:
        print("   no delivery rows at all for either ad group")
    out["all_time_performance"] = perf

    print("\n=== SEPTEMBER DELIVERY BY AD GROUP (whole campaign) ===")
    sep = {}
    for r in q(c, f"""SELECT ad_group.id, ad_group.name, metrics.cost_micros,
                      metrics.clicks, metrics.impressions
                      FROM ad_group
                      WHERE campaign.id = {CAMP}
                        AND segments.date BETWEEN '2026-09-01' AND '2026-09-21'"""):
        k = str(r.ad_group.id)
        a = sep.setdefault(k, {"name": r.ad_group.name, "cost": 0.0,
                               "clicks": 0, "impr": 0})
        a["cost"] += r.metrics.cost_micros / 1e6
        a["clicks"] += r.metrics.clicks
        a["impr"] += r.metrics.impressions
    for k, a in sep.items():
        print(f"   {k}  {a['name'][:36]:36s} ${a['cost']:8.2f} {a['clicks']:3d}cl "
              f"{a['impr']:5d}impr")
    out["september_by_ad_group"] = sep

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"commercial-check-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
