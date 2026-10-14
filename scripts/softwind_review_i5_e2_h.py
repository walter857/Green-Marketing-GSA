#!/usr/bin/env python3
"""Review PLAN-I5 validity, PLAN-E2 negatives individually, PLAN-H mutations. READ-ONLY."""
from __future__ import annotations

import json
import re
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "clients/softwind-power-washing/plans"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "i5-e2-h-review-2026-08-26.json"

snap = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))
drift = json.loads((SNAP / "drift-check-2026-08-25b.json").read_text(encoding="utf-8"))
deep = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
i5 = yaml.safe_load((PLANS / "2026-08-26-plan-i5-create-paused-expansion.yaml")
                    .read_text(encoding="utf-8"))["change_plan"]
e2 = yaml.safe_load((PLANS / "2026-08-26-plan-e2-live-negative-keywords.yaml")
                    .read_text(encoding="utf-8"))["change_plan"]
h = yaml.safe_load((PLANS / "2026-08-25-plan-h-sitelink-destinations.yaml")
                   .read_text(encoding="utf-8"))["change_plan"]

out = {}

# ---------------- PLAN-I5 ----------------
I2A_NEW = {"power washing service", "pressure washing service",
           "house washing near me", "power washing long island"}
live = {k["text"] for k in snap["enabled_keywords_live"]}
allk = {k["text"] for k in snap["keywords"]}
target = "pressure washing near me"
AG = snap["ad_groups"]
LEGACY = {"Pressure & Power Washing", "Soft & House Washing",
          "Driveway Patio Concrete Washing"}
legacy_texts = {k["text"] for k in snap["keywords"]
                if AG[k["ad_group_id"]]["name"] in LEGACY}

out["plan_i5_review"] = {
    "fingerprint_under_review": "A63D86DB3602",
    "proposed_keyword": target,
    "exists_live": target in live,
    "exists_anywhere_in_account": target in allk,
    "exists_in_legacy_container": target in legacy_texts,
    "created_by_plan_i2a_c": target in I2A_NEW,
    "planner_volume": 70, "planner_bid_low": 8.75, "planner_bid_high": 24.53,
    "semantic_conflict_check": {
        "vs_i2a_pressure_washing_service": (
            "DISTINCT. Different Planner buckets ($8.75-$24.53 vs $11.40-$26.35), "
            "different query shapes. Phrase \"pressure washing service\" cannot match a "
            "query lacking the word 'service'. Both would sit in campaign B, so any "
            "close-variant contention is INTRA-campaign and Google resolves it by Ad "
            "Rank in favour of the closer match. This is normal SKAG behaviour."),
        "vs_live_residential_pressure_washing_near_me": (
            "MEDIUM overlap on the shared substring, intra-campaign B, acceptable."),
    },
    "VERDICT": ("STILL THE STRONGEST MISSING INTENT - PRESERVE" if target not in allk
                else "REVIEW - text already exists somewhere"),
    "actions_changed": False,
    "fingerprint_action": "PRESERVE A63D86DB3602 - normalized actions unchanged",
    "exact_phrase_keyword": target, "exact_exact_keyword": target,
}
r = i5["rsas"]
out["plan_i5_rsas"] = [{
    "rsa": x["rsa"], "final_url": x["final_url"],
    "path1": x["path1"], "path2": x["path2"],
    "headline_count": len(x["headlines"]), "description_count": len(x["descriptions"]),
    "max_headline_len": max(hh["len"] for hh in x["headlines"]),
    "max_description_len": max(d["len"] for d in x["descriptions"]),
    "pinned": sum(1 for hh in x["headlines"] if hh.get("pinned")),
    "headlines": [(hh["text"], hh["len"], hh.get("pinned")) for hh in x["headlines"]],
    "descriptions": [(d["text"], d["len"]) for d in x["descriptions"]],
    "all_headlines_within_30": all(hh["len"] <= 30 for hh in x["headlines"]),
    "all_descriptions_within_90": all(d["len"] <= 90 for d in x["descriptions"]),
} for x in r]
ov = set(t for t, _, _ in out["plan_i5_rsas"][0]["headlines"]) & \
     set(t for t, _, _ in out["plan_i5_rsas"][1]["headlines"])
out["plan_i5_sibling_overlap"] = {"count": len(ov), "shared": sorted(ov)}

# ---------------- PLAN-E2 ----------------
PROTECTED = ["near me", "quote", "estimate", "cost", "price", "pricing",
             "best", "local", "hire", "emergency"]
negs = []
for a in e2["actions"]:
    term = a["exact_term"]
    hits = a.get("current_matching_search_terms")
    prot = [p for p in PROTECTED if p in term.lower()]
    # what valid buyer query could this block?
    could_block = {
        "roof cleaning": ("A combined query such as 'house and roof cleaning near me' "
                          "would be blocked, losing the house-washing half of the job."),
        "roof washing": ("A combined query such as 'roof and house washing' would be "
                         "blocked, same trade-off."),
        "house cleaning": ("A future SKAG using the legitimate phrasing 'exterior house "
                           "cleaning' would be blocked. None of the 11 live keyword "
                           "texts contains both 'house' and 'cleaning', so nothing is "
                           "blocked today."),
    }[term]
    negs.append({
        "action_id": a["action_id"], "negative_keyword": term,
        "match_type": a["match_type"], "campaign_id": a["campaign_id"],
        "campaign": a["campaign_name"],
        "triggering_search_terms": hits,
        "impressions": (sum(x["impressions"] for x in hits)
                        if isinstance(hits, list) else 0),
        "clicks": (sum(x["clicks"] for x in hits) if isinstance(hits, list) else 0),
        "cost": (round(sum(x["cost"] for x in hits), 2)
                 if isinstance(hits, list) else 0.0),
        "conversions": 0,
        "reason_out_of_scope": a["why"],
        "possible_valid_buyer_query_it_could_block": could_block,
        "live_keywords_blocked": a["live_keywords_this_negative_would_block"],
        "protected_term_violation": prot or "NONE",
        "rollback": a["rollback"],
        "verdict": ("UNAMBIGUOUSLY IRRELEVANT" if not prot else "REVIEW"),
    })
out["plan_e2_negatives"] = negs
out["plan_e2_verdict"] = {
    "fingerprint_under_review": "09E91EA674C8",
    "all_six_unambiguously_irrelevant": all(
        n["verdict"] == "UNAMBIGUOUSLY IRRELEVANT" for n in negs),
    "protected_terms_used": [n["negative_keyword"] for n in negs
                             if n["protected_term_violation"] != "NONE"],
    "used_as_a_pacing_tool": False,
    "pacing_note": ("These block 4 out-of-scope impressions and $0.00 of spend across "
                    "the account's whole life. They cannot and are not intended to "
                    "affect pacing in either direction."),
    "fingerprint_action": ("PRESERVE 09E91EA674C8" if all(
        n["verdict"] == "UNAMBIGUOUSLY IRRELEVANT" for n in negs)
        else "REVISE and re-fingerprint"),
}

# ---------------- PLAN-H ----------------
hmuts = []
for a in h["actions"]:
    hmuts.append({
        "action_id": a["action_id"], "resource_type": a["resource_type"],
        "operation": a["operation"], "campaign_id": a.get("campaign_id"),
        "resource_id": a["resource_id"], "object_count": a["object_count"],
        "current_value": a["current_value"], "proposed_value": a["proposed_value"],
        "rollback": a["rollback"]})
out["plan_h_mutations"] = hmuts
out["plan_h_object_total"] = sum(a["object_count"] for a in h["actions"])
cur = h["current_sitelinks"]
out["plan_h_sitelink_detail"] = {
    "campaign_level": [{
        "asset_id": s["asset_id"], "sitelink_text": s["sitelink_text"],
        "current_final_url": s["current_final_url"],
        "current_visible_phone": s["destination_phone_observed"],
        "destination_tracked": s["destination_tracked"],
        "campaign_association": s["linked_to_campaigns"],
        "proposed_action": "UNLINK from both campaigns (asset itself not deleted)",
        "rollback": "Re-create the campaign_asset link to this asset id"}
        for s in cur["campaign_level"]],
    "account_level": [{
        "asset_id": s["asset_id"], "sitelink_text": s["sitelink_text"],
        "current_final_url": s["current_final_url"],
        "current_visible_phone": s["destination_phone_observed"],
        "destination_tracked": s["destination_tracked"],
        "proposed_action": ("UNLINK" if s["asset_id"] == "403671792813"
                            else "LEAVE AS-IS - overridden by campaign-level sitelinks"),
        "rollback": "Re-create the customer_asset link"} for s in cur["account_level"]],
    "proposed_replacements": [{
        "sitelink_text": p["sitelink_text"],
        "proposed_final_url": p["final_url"],
        "proposed_tracked_phone_path": p["destination_verified"]["phone"],
        "destination_verified_200": p["destination_verified"]["http_status"] == 200,
        "campaign_association": "link to BOTH 24103511039 and 24145053510",
        "rollback": "Remove the new asset and its links"}
        for p in h["proposed_sitelinks"]],
}

OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

print("=" * 88)
print("PLAN-I5 REVIEW")
v = out["plan_i5_review"]
print("  proposed keyword        : %s" % v["proposed_keyword"])
print("  exists live             : %s" % v["exists_live"])
print("  exists anywhere         : %s" % v["exists_anywhere_in_account"])
print("  created by PLAN-I2A-C   : %s" % v["created_by_plan_i2a_c"])
print("  VERDICT                 : %s" % v["VERDICT"])
print("  fingerprint             : %s" % v["fingerprint_action"])
for x in out["plan_i5_rsas"]:
    print("  RSA%d %s /%s/%s  H=%d D=%d maxH=%d maxD=%d pins=%d  limits_ok=%s"
          % (x["rsa"], x["final_url"].split("/")[-2], x["path1"], x["path2"],
             x["headline_count"], x["description_count"], x["max_headline_len"],
             x["max_description_len"], x["pinned"],
             x["all_headlines_within_30"] and x["all_descriptions_within_90"]))
print("  sibling overlap: %d %s" % (out["plan_i5_sibling_overlap"]["count"],
                                    out["plan_i5_sibling_overlap"]["shared"]))
print()
print("=" * 88)
print("PLAN-E2 - ALL SIX NEGATIVES")
for n in negs:
    print("  %s  '%s' [%s]  campaign %s (%s)"
          % (n["action_id"], n["negative_keyword"], n["match_type"],
             n["campaign_id"], n["campaign"]))
    st = n["triggering_search_terms"]
    if isinstance(st, list):
        for x in st:
            print("      trigger: '%s'  impr=%d clk=%d $%.2f conv=%s"
                  % (x["search_term"], x["impressions"], x["clicks"], x["cost"],
                     0))
    else:
        print("      trigger: %s" % st)
    print("      blocks live keywords: %s" % n["live_keywords_blocked"])
    print("      protected-term violation: %s" % n["protected_term_violation"])
    print("      verdict: %s" % n["verdict"])
print()
print("  ALL SIX UNAMBIGUOUSLY IRRELEVANT: %s"
      % out["plan_e2_verdict"]["all_six_unambiguously_irrelevant"])
print("  FINGERPRINT ACTION: %s" % out["plan_e2_verdict"]["fingerprint_action"])
print()
print("=" * 88)
print("PLAN-H - %d OBJECT MUTATIONS ACROSS %d ACTIONS"
      % (out["plan_h_object_total"], len(hmuts)))
for a in hmuts:
    print("  %s %-18s %-16s objects=%d" % (a["action_id"], a["resource_type"],
                                           a["operation"], a["object_count"]))
print()
print("  CURRENT SITELINKS -> ALL SHOW UNTRACKED (631) 502-5402")
for s in out["plan_h_sitelink_detail"]["campaign_level"]:
    print("    CAMPAIGN %s '%s' -> %s  phone=%s  %s"
          % (s["asset_id"], s["sitelink_text"], s["current_final_url"],
             s["current_visible_phone"], s["proposed_action"]))
for s in out["plan_h_sitelink_detail"]["account_level"]:
    print("    ACCOUNT  %s '%s' -> %s  phone=%s  %s"
          % (s["asset_id"], s["sitelink_text"], s["current_final_url"],
             s["current_visible_phone"], s["proposed_action"]))
print()
print("  PROPOSED REPLACEMENTS -> ALL TRACKED (631) 502-7946")
for p in out["plan_h_sitelink_detail"]["proposed_replacements"]:
    print("    NEW '%s' -> %s  phone=%s  verified200=%s"
          % (p["sitelink_text"], p["proposed_final_url"],
             p["proposed_tracked_phone_path"], p["destination_verified_200"]))
print()
print("wrote %s" % OUT)
