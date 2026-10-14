#!/usr/bin/env python3
"""Pinning analysis + a drafted AC Repair RSA challenger. VALIDATE-ONLY. Creates nothing."""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
LIVE_AG = {"202339087834", "202339087594", "202339087634", "202339087674", "200159223798"}

print("=== PINNING DIAGNOSTIC: DOES POSITION 1 ALREADY CARRY THE SERVICE KEYWORD? ===")
SVC = {"24132507741": r"\bac repair\b|\bair conditioner repair\b|\bac\b",
       "24132507744": r"\bboiler\b", "24132507747": r"\bhvac install",
       "24132507750": r"\bhvac repair\b", "24132507753": r"\bhvac replacement\b"}
rows = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.ad_strength,
       ad_group_ad.policy_summary.approval_status,
       ad_group_ad.ad.responsive_search_ad.headlines FROM ad_group_ad
       WHERE campaign.id IN ({IN5}) AND ad_group_ad.status = 'ENABLED'"""):
    x = r.ad_group_ad
    if str(r.ad_group.id) not in LIVE_AG or E(x.policy_summary.approval_status) != "APPROVED":
        continue
    hs = [h.text for h in x.ad.responsive_search_ad.headlines]
    pat = SVC[str(r.campaign.id)]
    with_svc = [h for h in hs if re.search(pat, h, re.I)]
    rows.append({"camp": NAME[str(r.campaign.id)], "ad": str(x.ad.id),
                 "strength": E(x.ad_strength), "n": len(hs),
                 "pinned": sum(1 for h in x.ad.responsive_search_ad.headlines
                               if E(h.pinned_field) != "UNSPECIFIED"),
                 "with_service_kw": len(with_svc),
                 "first3_have_service_kw": sum(1 for h in hs[:3] if re.search(pat, h, re.I)),
                 "h1": hs[0] if hs else ""})
print(f"  {'campaign':<20}{'ad':<14}{'strength':<11}{'pins':>5}{'svc/15':>8}{'svc in H1-3':>13}"
      f"   H1")
for x in sorted(rows, key=lambda z: (z["camp"], z["ad"])):
    print(f"  {x['camp']:<20}{x['ad']:<14}{x['strength']:<11}{x['pinned']:>5}"
          f"{x['with_service_kw']:>8}{x['first3_have_service_kw']:>13}   {x['h1'][:34]}")
out["pinning_diagnostic"] = rows
print(f"\n  TOTAL PINS ACROSS ALL 10 LIVE APPROVED ADS: {sum(x['pinned'] for x in rows)}")
weak = [x for x in rows if x["first3_have_service_kw"] < 2]
print(f"  ads whose first three headlines carry fewer than 2 service-keyword mentions: "
      f"{[(x['camp'], x['ad'], x['first3_have_service_kw']) for x in weak]}")

# ---------------------------------------------------------------- CHALLENGER
print("\n\n=== DRAFTED CHALLENGER: AC Repair ad group 202339087834 ===")
AG = "202339087834"
URL = "https://offer.ambientcoolingandheating.com/ac-repair/"
PINNED_H1 = [
    "AC Repair in Severn, MD",
    "AC Repair Near You Today",
    "Air Conditioner Repair MD",
]
UNPINNED = [
    "Licensed & Insured AC Repair",
    "Free AC Repair Estimate",
    "AC Not Cooling? We Can Help",
    "Local Anne Arundel AC Repair",
    "AC Repair in Severna Park",
    "AC Repair in Columbia, MD",
    "Book Your AC Repair Visit",
    "Talk to a Real Technician",
    "Straight AC Repair Pricing",
    "Residential & Commercial AC",
    "Fix My AC Unit",
    "Call for AC Repair Help",
]
DESCS = [
    "Licensed and insured AC repair across Severn, Severna Park and Columbia. Free estimates.",
    "AC not cooling? Book a repair visit and get straight pricing before any work begins.",
    "Local Anne Arundel County technicians. Residential and commercial air conditioning repair.",
    "Request your free AC repair estimate today and get your home comfortable again.",
]
BARRED = re.compile(r"24/?7|emergency|same[\s-]?day|guarantee|financ|rebate|discount|warrant|"
                    r"\b\d+(\.\d+)?\s*star|\b#1\b|best in", re.I)
print(f"  pinned to position 1 ({len(PINNED_H1)}):")
ok = True
for h in PINNED_H1:
    bad = BARRED.search(h)
    v = len(h) <= 30 and not bad
    ok = ok and v
    print(f"    [{'OK' if v else 'FAIL'}] ({len(h):>2}) {h}")
print(f"  unpinned ({len(UNPINNED)}):")
for h in UNPINNED:
    bad = BARRED.search(h)
    v = len(h) <= 30 and not bad
    ok = ok and v
    print(f"    [{'OK' if v else 'FAIL'}] ({len(h):>2}) {h}")
print(f"  descriptions ({len(DESCS)}):")
for d in DESCS:
    bad = BARRED.search(d)
    v = len(d) <= 90 and not bad
    ok = ok and v
    print(f"    [{'OK' if v else 'FAIL'}] ({len(d):>2}) {d}")
allh = PINNED_H1 + UNPINNED
print(f"\n  total headlines {len(allh)} (max 15), descriptions {len(DESCS)} (max 4)")
print(f"  duplicates: {[k for k, v in Counter(allh).items() if v > 1] or 'none'}")
AC_TOK = re.compile(r"ac|air condition", re.I)
n_ac = sum(1 for h in allh if AC_TOK.search(h))
print(f"  headlines containing an AC service token: {n_ac}/{len(allh)}")
print(f"  claim check (no 24/7, emergency, same-day, financing, rebate, discount, warranty, "
      f"rating): {'PASS' if ok else 'FAIL'}")
print(f"  'Licensed & Insured' used: {sum(1 for t in allh + DESCS if re.search('licens', t, re.I))}"
      f" assets - authorized by client 2026-09-10, recorded in work-order.yaml")

TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "AC Repair",
          "related_services": ["HVAC Repair", "HVAC Installation", "HVAC Replacement",
                               "Gas Boiler Repair"]}
ops = [{
    "operation": "CREATE_RSA_PAUSED", "resource": "ad_group_ad",
    "resource_id": AG, "resource_name": "SKAG | AC Repair Near Me",
    "campaign_id": "24132507741", "campaign": "AC Repair",
    "final_url": URL, "path1": "ac-repair", "path2": "severn-md",
    "status": "PAUSED",
    "headlines_pinned_headline_1": PINNED_H1,
    "headlines_unpinned": UNPINNED,
    "descriptions": DESCS,
    "current_state": "ad group 202339087834 holds 2 ENABLED APPROVED RSAs "
                     "(820900825416, 820900825419)",
    "proposed_state": "one additional RSA created PAUSED; both existing RSAs untouched",
    "reason": ("Challenger for ad 820900825419, whose 15 headlines are largely non-specific "
               "('Stop Guessing About Your AC', 'Get Clear Answers First', 'Bring Comfortable "
               "Air Back') and which measured 2.77% CTR against 820900825416's 3.56% at "
               "equivalent auction position. Three headlines are pinned to position 1 so the "
               "service keyword always leads, while Google still chooses among the three."),
    "rollback": "remove the created ad_group_ad by its returned resource name; it is created "
                "PAUSED so it can never serve before a separate enable approval",
    "risk": "LOW - created PAUSED, no existing ad is edited",
    "unrelated_resource_assertion":
        "ads 820900825416 and 820900825419 must remain ENABLED and APPROVED; ad group "
        "202339087834 must hold 3 ads afterwards, exactly 2 of them ENABLED"}]
plan = {"plan_name": "AMB-0910-RSA-ACR-1", "approval_class": "create-paused",
        "generated_local": out["generated_local"], "target": TARGET,
        "summary": "Create ONE paused AC Repair RSA challenger with 3 headlines pinned to "
                   "position 1. Nothing is enabled and no existing ad is edited.",
        "object_count": 1, "partial_failure": False, "atomic": True, "operations": ops,
        "notes": {
            "pinning_rationale":
                "Pinning exactly one headline to position 1 removes all variation from the most "
                "visible slot and stops Google testing openers. Pinning THREE to position 1 "
                "guarantees a service-keyword opener while preserving rotation. Three is the "
                "safer of the two options.",
            "claims_used": ["Licensed & Insured - authorized by the client 2026-09-10",
                            "Free Estimates - approved baseline claim",
                            "Residential & Commercial - corroborated on the live site and by a "
                            "third-party directory"],
            "claims_deliberately_avoided": ["24/7", "emergency service", "same-day service",
                                            "guaranteed response", "financing", "rebates",
                                            "discounts", "warranty", "ratings or review counts"],
            "outstanding_before_enable":
                "Obtain the Maryland Master HVACR licence number and the certificate of "
                "insurance and record them in work-order.yaml. The landing page also does not "
                "yet say licensed and insured; message match should be fixed before enabling.",
            "measurement_plan":
                "Do not enable both challenger and control at once. After a separate enable "
                "approval, run at least 14 settled days and at least 500 impressions per ad, "
                "compare relevant CTR by device at equivalent position, and require no "
                "deterioration in unique qualified CVR and no breach of the $150 AC Repair CPQL.",
            "requires_new_approval": True}}
plan["fingerprint"] = approval_code({"target": TARGET, "plan": plan["plan_name"],
                                     "operations": ops})
(CLIENT_DIR / "plans" / f"{plan['plan_name']}.json").write_text(
    json.dumps(plan, indent=1, default=str), encoding="utf-8")
print(f"\n=== {plan['plan_name']} ops=1 fingerprint={plan['fingerprint']} ===")
print(f"WROTE clients/ambient-cooling-heating/plans/{plan['plan_name']}.json")
out["challenger"] = plan
write(EVID / "2026-09-10-rsa-pinning-and-challenger.json", out)
