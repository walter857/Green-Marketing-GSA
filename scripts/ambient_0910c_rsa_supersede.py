#!/usr/bin/env python3
"""AMB-0910-RSA-ACR-1 19E2F2FFC311 used 'Licensed & Insured'. That claim is withdrawn from
this workstream, so the fingerprint is STALE. Mark it superseded and issue a clean
replacement that keeps the 3-pin structure and drops the claim entirely."""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

c = client()
identity_gate(c, verbose=False)
AG, CAMP = "202339087834", "24132507741"
URL = "https://offer.ambientcoolingandheating.com/ac-repair/"

# ---------------------------------------------------------------- supersede
old = json.load(open(CLIENT_DIR / "plans" / "AMB-0910-RSA-ACR-1.json", encoding="utf-8"))
oldfp = approval_code({"target": old["target"], "plan": old["plan_name"],
                       "operations": old["operations"]})
print(f"=== SUPERSEDING {old['plan_name']} {oldfp} ===")
assert oldfp == "19E2F2FFC311", f"fingerprint drift: {oldfp}"
hits = [t for t in (old["operations"][0]["headlines_pinned_headline_1"]
                    + old["operations"][0]["headlines_unpinned"]
                    + old["operations"][0]["descriptions"])
        if re.search(r"licens|insur", t, re.I)]
print(f"  assets carrying the withdrawn claim: {hits}")
sup = {"plan_name": old["plan_name"], "fingerprint": oldfp, "status": "SUPERSEDED",
       "status_recorded_local": datetime.datetime.now(TZ).isoformat(),
       "do_not_execute": True, "executed": False,
       "google_ads_operations_performed": 0,
       "reason": "The package used 'Licensed & Insured' in one headline and one description. "
                 "That claim is withdrawn from this workstream by instruction on 2026-09-10, "
                 "so every fingerprint containing it is stale. No licence number or "
                 "certificate of insurance is required, because the claim will not be used.",
       "assets_carrying_the_withdrawn_claim": hits,
       "superseded_by": "AMB-0910-RSA-ACR-2",
       "what_was_kept": "the 3-headlines-pinned-to-HEADLINE_1 structure, the create-paused "
                        "class, the ad group, the final URL and the measurement plan"}
(CLIENT_DIR / "plans" / "AMB-0910-RSA-ACR-1.SUPERSEDED.json").write_text(
    json.dumps(sup, indent=1, default=str), encoding="utf-8")
print("  WROTE plans/AMB-0910-RSA-ACR-1.SUPERSEDED.json")

# ---------------------------------------------------------------- replacement
PINNED = ["AC Repair in Severn, MD", "AC Repair Near You Today",
          "Air Conditioner Repair MD"]
FREE = ["Free AC Repair Estimate", "AC Not Cooling? We Can Help",
        "Local Anne Arundel AC Repair", "AC Repair in Severna Park",
        "AC Repair in Columbia, MD", "Book Your AC Repair Visit",
        "Talk to a Real Technician", "Straight AC Repair Pricing",
        "Residential & Commercial AC", "Fix My AC Unit",
        "Call for AC Repair Help", "AC Repair Done Right"]
DESCS = ["AC repair across Severn, Severna Park and Columbia. Free estimates before any work.",
         "AC not cooling? Book a repair visit and get straight pricing before any work begins.",
         "Local Anne Arundel technicians. Residential and commercial air conditioning repair.",
         "Request your free AC repair estimate today and get your home comfortable again."]
BARRED = re.compile(r"licens|insur|24/?7|emergenc|same[\s-]?day|guarantee|financ|rebate|"
                    r"discount|warrant|\b\d+(\.\d+)?\s*star|\b#1\b|best in", re.I)

print("\n=== AMB-0910-RSA-ACR-2 ASSETS ===")
ok = True
for lbl, items, cap in [("pinned to HEADLINE_1", PINNED, 30), ("unpinned", FREE, 30),
                        ("descriptions", DESCS, 90)]:
    print(f"  {lbl}:")
    for t in items:
        bad = BARRED.search(t)
        v = len(t) <= cap and not bad
        ok = ok and v
        print(f"    [{'OK' if v else 'FAIL'}] ({len(t):>2}) {t}"
              + (f"   <-- {bad.group(0)!r}" if bad else ""))
allh = PINNED + FREE
print(f"  headlines {len(allh)}/15  descriptions {len(DESCS)}/4  "
      f"duplicates {[k for k, v in Counter(allh).items() if v > 1] or 'none'}")
print(f"  claim check: {'PASS' if ok else 'FAIL'}")
assert ok and len(allh) <= 15 and len(DESCS) <= 4

TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "AC Repair",
          "related_services": ["HVAC Repair", "HVAC Installation", "HVAC Replacement",
                               "Gas Boiler Repair"]}
live = q(c, f"SELECT ad_group_ad.ad.id, ad_group_ad.status, "
            f"ad_group_ad.policy_summary.approval_status FROM ad_group_ad "
            f"WHERE ad_group.id = {AG}")
enabled = [str(r.ad_group_ad.ad.id) for r in live
           if E(r.ad_group_ad.status) == "ENABLED"
           and E(r.ad_group_ad.policy_summary.approval_status) == "APPROVED"]
print(f"\n  verified live state of ad group {AG}: {len(live)} ads, "
      f"{len(enabled)} ENABLED+APPROVED {enabled}")

ops = [{"operation": "CREATE_RSA_PAUSED", "resource": "ad_group_ad",
        "resource_id": AG, "resource_name": "SKAG | AC Repair Near Me",
        "campaign_id": CAMP, "campaign": "AC Repair",
        "final_url": URL, "path1": "ac-repair", "path2": "severn-md", "status": "PAUSED",
        "headlines_pinned_headline_1": PINNED, "headlines_unpinned": FREE,
        "descriptions": DESCS,
        "current_state": f"ad group {AG} holds {len(live)} ads, {len(enabled)} ENABLED and "
                         f"APPROVED ({', '.join(enabled)})",
        "proposed_state": f"ad group {AG} holds {len(live)+1} ads; the new one is PAUSED; "
                          f"both existing ENABLED ads are untouched",
        "reason": "Challenger for ad 820900825419, whose 15 headlines are largely "
                  "non-specific ('Stop Guessing About Your AC', 'Get Clear Answers First', "
                  "'Bring Comfortable Air Back'). Three materially different keyword-forward "
                  "headlines are pinned to HEADLINE_1 so the service keyword always leads "
                  "while Google still rotates among three candidates in the most visible slot.",
        "rollback": "remove the created ad_group_ad by its returned resource name; it is "
                    "PAUSED so it can never serve before a separate enable approval",
        "risk": "LOW - created PAUSED, no existing ad is edited",
        "unrelated_resource_assertion":
            f"ads {', '.join(enabled)} must remain ENABLED and APPROVED; ad group {AG} must "
            f"hold {len(live)+1} ads afterwards, exactly {len(enabled)} of them ENABLED"}]
plan = {"plan_name": "AMB-0910-RSA-ACR-2", "approval_class": "create-paused",
        "supersedes": "AMB-0910-RSA-ACR-1 19E2F2FFC311 - SUPERSEDED, DO_NOT_EXECUTE "
                      "(used the withdrawn 'Licensed & Insured' claim)",
        "generated_local": datetime.datetime.now(TZ).isoformat(), "target": TARGET,
        "summary": "Create ONE paused AC Repair RSA challenger with 3 headlines pinned to "
                   "position 1 and no licence or insurance claim. Nothing is enabled and no "
                   "existing ad is edited.",
        "object_count": 1, "partial_failure": False, "atomic": True, "operations": ops,
        "notes": {
          "why_three_pins_not_one":
              "Pinning one headline to position 1 fixes the most visible slot to a single "
              "asset and stops Google testing openers, so asset-level reporting on that slot "
              "collapses to one data point. Pinning three materially different keyword-forward "
              "headlines guarantees a service-keyword opener AND preserves rotation, so the "
              "winning opener is still learnable. HEADLINE_3 is deliberately not pinned "
              "because position 3 is not guaranteed to show.",
          "claim_withdrawn": "'Licensed & Insured' is not used anywhere in this package. No "
                             "licence number or certificate of insurance is needed.",
          "claims_avoided": ["licensed", "insured", "24/7", "emergency", "same-day",
                             "guaranteed response", "financing", "rebates", "discounts",
                             "warranty", "ratings", "review counts"],
          "claims_used": ["Free Estimates - approved baseline claim",
                          "Residential & Commercial - corroborated on the live site and by a "
                          "third-party directory, and commercial is approved paid scope"],
          "ctr_evidence_is_a_hypothesis":
              "Ad 820900825419 measured 2.77% CTR against 820900825416's 3.56% in aggregate, "
              "but on DESKTOP 825419 wins 1.82% vs 0.51%. The aggregate gap is substantially "
              "a device-mix artefact. This package tests a hypothesis; it does not rest on a "
              "proven CTR deficit, and no CTR improvement is claimed.",
          "ad_strength": "Pinning will probably lower reported Ad Strength. Ad Strength is "
                         "not an optimization target under agency policy; that is an "
                         "accepted cost, not a regression.",
          "measurement_plan":
              "Do not enable challenger and control at once. After a separate enable "
              "approval, run at least 14 settled days and at least 500 impressions per ad, "
              "compare relevant CTR BY DEVICE at equivalent position with query mix and "
              "impression share controlled, and require no deterioration in unique qualified "
              "conversion rate and no breach of the $150 AC Repair CPQL. Improvement is not "
              "proven until settled post-change data shows it.",
          "requires_new_approval": True}}
plan["fingerprint"] = approval_code({"target": TARGET, "plan": plan["plan_name"],
                                     "operations": ops})
(CLIENT_DIR / "plans" / f"{plan['plan_name']}.json").write_text(
    json.dumps(plan, indent=1, default=str), encoding="utf-8")
print(f"\n=== {plan['plan_name']} ops=1 fingerprint={plan['fingerprint']} ===")
print(f"WROTE clients/ambient-cooling-heating/plans/{plan['plan_name']}.json")
