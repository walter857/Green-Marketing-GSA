#!/usr/bin/env python3
"""Ambient | 2026-09-20 | Heat Pump destination revalidation + live ad policy status.

Two jobs:

  1. Revalidate the Heat Pump final URL against Google Ads itself. The earlier
     verdict was DESTINATION_NOT_WORKING (4/4 trials on 2026-09-17, 3/3 on
     2026-09-18). This repeats the trial today and runs the SAME ad text against a
     known-good URL as a positive control, so a pass/fail cannot be confused with
     a problem in the ad copy. Every other expansion URL is trialled too, so the
     verdict is comparative rather than isolated.

  2. Read back the policy status of every ad and every ad-group criterion that
     already exists on the heating structure, plus the five legacy campaigns.

validate_only = True on every mutate. EXTERNAL WRITES: 0.
Note: validate_only consumes the same daily mutate quota as a real write, so the
trial count is kept deliberately small.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-22"
TRIALS = 3
TOPIC = re.compile(r'topic: "([A-Z_]+)"')
ERRCODE = re.compile(r'(policy_finding_error|ad_error|url_field_error|[a-z_]+_error): ([A-Z_]+)')

URLS = {
    "Heat Pump Installation": "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/",
    "Boiler Repair": "https://ambientcoolingandheating.com/services/heating-services/boiler-repair/",
    "Oil Furnace Installation": "https://ambientcoolingandheating.com/services/heating-services/oil-furnace-installations/",
    "Oil Heating System Replacement": "https://ambientcoolingandheating.com/services/heating-services/oil-replacement/",
    "Tankless Water Heater Installation": "https://ambientcoolingandheating.com/services/heating-services/tankless-water-heaters/",
    "Geothermal HVAC Installation": "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/",
    "CONTROL Furnace Repair (live, already serving)": "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/",
    "CONTROL Mini Splits (live, already serving)": "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/",
    "CONTROL Gas Boiler offer page (live)": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
}

# One neutral, policy-clean ad body used for EVERY url so the only variable is the
# destination. Nothing here is a claim: no superlative, no availability promise.
H = ["Heating Service Central MD", "Book A Heating Visit", "Severn Heating Company",
     "Local Heating Technicians", "Request A Heating Quote", "Heating Help Near You",
     "Serving Anne Arundel County", "Heating System Service", "Schedule Your Service",
     "Talk To A Technician", "Heating Service Columbia MD", "Severna Park Heating",
     "Get Your Heating Checked", "Heating Repair And Install", "Call For An Appointment"]
D = ["Local heating technicians serving Severn, Severna Park and Columbia, Maryland.",
     "Request a visit online and a technician will get back to you about your system.",
     "Serving homes across Anne Arundel County and the surrounding Central Maryland area.",
     "Tell us what your heating system is doing and we will schedule a service visit."]


def main():
    c = client()
    identity_gate(c, verbose=True)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "validate_only": True, "external_writes": 0, "trials_per_url": TRIALS,
           "ad_body_identical_across_urls": True}

    agrn = c.get_service("AdGroupService").ad_group_path(CID, "199797580706")

    # ------------------------------------------------- 1. destination trials
    print(f"\n=== 1. DESTINATION POLICY TRIALS ({TRIALS} per URL, identical ad body) ===")
    dest = {}
    for label, url in URLS.items():
        topics, errs, passes = [], [], 0
        for _ in range(TRIALS):
            o = c.get_type("AdGroupAdOperation")
            a = o.create
            a.ad_group = agrn
            a.status = c.enums.AdGroupAdStatusEnum.PAUSED
            a.ad.final_urls.append(url)
            rr = a.ad.responsive_search_ad
            for h in H:
                t = c.get_type("AdTextAsset"); t.text = h; rr.headlines.append(t)
            for x in D:
                t = c.get_type("AdTextAsset"); t.text = x; rr.descriptions.append(t)
            r = c.get_type("MutateAdGroupAdsRequest")
            r.customer_id = CID
            r.operations.append(o)
            r.partial_failure = False
            r.validate_only = True
            try:
                c.get_service("AdGroupAdService").mutate_ad_group_ads(request=r)
                passes += 1
            except Exception as e:
                s = str(e)
                topics += TOPIC.findall(s)
                errs += [f"{a}:{b}" for a, b in ERRCODE.findall(s)]
        dest[label] = {"url": url, "trials": TRIALS, "passes": passes,
                       "failures": TRIALS - passes,
                       "policy_topics": sorted(set(topics)),
                       "error_codes": sorted(set(errs)),
                       "verdict": "PASS" if passes == TRIALS else
                                  ("INTERMITTENT" if passes else "BLOCKED")}
        print(f"  {label[:46]:46s} {passes}/{TRIALS} pass  {dest[label]['verdict']:12s} "
              f"{sorted(set(topics))}")
    out["destination_trials"] = dest

    # ------------------------------------------------ 2. live ad policy status
    print("\n=== 2. EXISTING AD POLICY STATUS ===")
    ads = {}
    for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                     ad_group.id, ad_group.name, ad_group.status,
                     ad_group_ad.ad.id, ad_group_ad.status,
                     ad_group_ad.policy_summary.approval_status,
                     ad_group_ad.policy_summary.review_status,
                     ad_group_ad.ad.final_urls, ad_group_ad.ad.type
                     FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        ads[str(r.ad_group_ad.ad.id)] = {
            "campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
            "campaign_status": E(r.campaign.status),
            "ad_group_id": str(r.ad_group.id), "ad_group": r.ad_group.name,
            "ad_group_status": E(r.ad_group.status),
            "ad_status": E(r.ad_group_ad.status),
            "approval": E(r.ad_group_ad.policy_summary.approval_status),
            "review": E(r.ad_group_ad.policy_summary.review_status),
            "final_urls": list(r.ad_group_ad.ad.final_urls),
            "type": E(r.ad_group_ad.ad.type_)}
    out["ads"] = ads
    heat = {k: v for k, v in ads.items()
            if v["campaign_id"] in ("24257819463", "24257819466", "24132507744")}
    print(f"   {len(ads)} non-removed ads in the account; "
          f"{len(heat)} on the heating/boiler campaigns")
    for k, v in sorted(heat.items(), key=lambda x: (x[1]["ad_group"], x[0])):
        print(f"      ad {k}  {v['ad_status']:8s} {v['approval']:20s} {v['review']:18s} "
              f"{v['ad_group'][:34]}")
    agg = {}
    for v in ads.values():
        agg[v["approval"]] = agg.get(v["approval"], 0) + 1
    out["approval_rollup_all_ads"] = agg
    print(f"   account-wide approval rollup: {agg}")

    # --------------------------------------- 3. criterion-level policy status
    print("\n=== 3. HEATING KEYWORD POLICY / SYSTEM STATUS ===")
    kws = {}
    for r in q(c, """SELECT campaign.id, ad_group.id, ad_group.name,
                     ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                     ad_group_criterion.keyword.match_type,
                     ad_group_criterion.status,
                     ad_group_criterion.approval_status,
                     ad_group_criterion.system_serving_status
                     FROM ad_group_criterion
                     WHERE ad_group_criterion.type = 'KEYWORD'
                       AND ad_group_criterion.status != 'REMOVED'
                       AND campaign.id IN (24257819463, 24257819466, 24132507744)
                       AND ad_group_criterion.negative = FALSE"""):
        x = r.ad_group_criterion
        kws[f"{r.ad_group.id}:{x.criterion_id}"] = {
            "ad_group": r.ad_group.name, "text": x.keyword.text,
            "match": E(x.keyword.match_type), "status": E(x.status),
            "approval": E(x.approval_status),
            "serving": E(x.system_serving_status)}
    out["heating_keywords"] = kws
    print(f"   {len(kws)} positive keywords on heating/boiler campaigns")
    rol = {}
    for v in kws.values():
        key = (v["approval"], v["serving"])
        rol[str(key)] = rol.get(str(key), 0) + 1
    print(f"   rollup (approval, serving): {rol}")
    out["heating_keyword_rollup"] = rol

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"dest-policy-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
