#!/usr/bin/env python3
"""Emit the approval bundle: per-client plan files plus deterministic fingerprints.

Local only. Writes nothing to Google Ads.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

PLANS = ROOT / "reports" / "st-plans"
COMPS = ROOT / "reports" / "st-competitors"
NAMES = ROOT / "reports" / "st-names"
RUN = date.today().isoformat()

CLIENT_DIR = {
    "ambient-cooling-heating": "ambient-cooling-heating",
    "pro-green-austin": "pro-green-austin",
    "softwind-power-washing": "softwind-power-washing",
    "softwind-landscape-masonry": "softwind-landscape-masonry",
}
SERVICE = {
    "ambient-cooling-heating": "AC Repair (+ HVAC Repair, HVAC Installation, "
                               "HVAC Replacement, Gas Boiler Repair)",
    "pro-green-austin": "outdoor design & build",
    "softwind-power-washing": "Power Washing",
    # work-order.yaml: exact_primary_service Pavers, related_services [Patio].
    "softwind-landscape-masonry": "Pavers (+ Patio)",
}


def main() -> int:
    out = {}
    for plan_path in sorted(PLANS.glob("*-negative-plan.json")):
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        slug = plan["slug"]
        cid = plan["customer_id"]

        target = {
            "exact_child_account_name": plan["account_name"],
            "child_customer_id": cid,
            "exact_service": SERVICE[slug],
            "manager_customer_id": "3373711342",
        }

        # name / entity BROAD layer, campaign level, owner-approved 2026-08-28
        nm = json.loads((NAMES / (slug + "-name-negatives.json")).read_text(
            encoding="utf-8"))
        name_negs = [{"text": n["text"], "match_type": "BROAD",
                      "category": n["category"]} for n in nm["negatives"]]
        plan["layer_n_name_broad"] = [
            {"campaign_id": b["campaign_id"], "campaign_name": b["campaign_name"],
             "negatives": name_negs}
            for b in plan["layer_a_campaign_level"]]

        subplans = {}
        for key, layer, svc in (
            ("NEG_CAMPAIGN_LEVEL", "layer_a_campaign_level", "CampaignCriterionService"),
            ("NEG_AD_GROUP_LEVEL", "layer_b_ad_group_level", "AdGroupCriterionService"),
            ("NEG_CROSS_AD_GROUP", "layer_x_cross_negatives", "AdGroupCriterionService"),
            ("NEG_NAME_BROAD", "layer_n_name_broad", "CampaignCriterionService"),
        ):
            blocks = plan[layer]
            objects = sum(len(b["negatives"]) for b in blocks)
            scopes = [b.get("campaign_id") or b.get("ad_group_id") for b in blocks]
            body = {
                "target": target, "subplan": key, "service": svc,
                "mutation": "create",
                "status_on_create": "ENABLED (a negative keyword has no paused state)",
                "scopes": sorted(str(s) for s in scopes),
                "object_count": objects,
                "match_types": dict(Counter(
                    n["match_type"] for b in blocks for n in b["negatives"])),
                "categories": dict(Counter(
                    n["category"] for b in blocks for n in b["negatives"])),
            }
            subplans[key] = {
                "fingerprint": approval_code(body) if objects else "",
                "object_count": objects,
                "scope_count": len(blocks),
                "summary": body,
                "detail": blocks,
            }

        comp_path = COMPS / (slug + "-competitor-candidates.csv")
        bundle = {
            "plan_id": "NEG-{}-{}".format(slug.upper(), RUN),
            "generated": RUN,
            "mode": "DRAFT - read-only research and local plan. No external write performed.",
            "target": target,
            "evidence": {
                "search_term_range": "2019-01-01..2026-08-28 (all available history)",
                "negative_verdict_terms": plan["coverage"]["negative_terms"],
                "wasted_spend_usd": plan["coverage"]["wasted_spend_usd"],
                "spend_the_plan_would_have_blocked_usd":
                    plan["coverage"]["spend_blocked_usd"],
                "verdict_table": "reports/st-verdicts/{}-verdicts.csv".format(slug),
                "competitor_review_file": str(comp_path.relative_to(ROOT)),
                "name_layer_file": "reports/st-names/{}-name-negatives.csv".format(slug),
                "name_layer_spend_usd": nm.get("total_objects") and round(
                    sum(n.get("cost_usd", 0) for n in nm["negatives"]), 2),
                "name_layer_held_back": len(nm["held_back"]),
            },
            "guards_enforced": [
                "never blocks a KEEP or WATCH term",
                "never blocks a term that produced a conversion",
                "never blocks a live positive keyword",
                "never equals a Green Marketing PROTECTED phrase "
                "(near me, quote, price, cost, best, hire, local, emergency, ...)",
                "client brand terms are exempt from negation",
                "max 10 words and 80 characters per negative",
                "Phrase and Exact for the term layer; BROAD only in the name layer, "
                "on explicit owner approval 2026-08-28",
                "a name is negated only if it is NOT an English dictionary word, "
                "is not an equipment manufacturer, is not a US place name in the "
                "market region, and appears in no in-scope KEEP term",
                "per-scope redundancy against account list, linked shared lists, "
                "campaign negatives and ad group negatives",
            ],
            "subplans": subplans,
        }
        master = approval_code({
            "target": target,
            "subplans": {k: v["summary"] for k, v in subplans.items()},
        })
        bundle["master_fingerprint"] = master
        assert_no_embedded_secrets(bundle)

        dest = ROOT / "clients" / CLIENT_DIR[slug] / "plans"
        dest.mkdir(parents=True, exist_ok=True)
        p = dest / "{}-negative-expansion.json".format(RUN)
        p.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

        print("=" * 78)
        print("{}   {}   {}".format(plan["account_name"], cid, SERVICE[slug]))
        print("=" * 78)
        print("  MASTER FINGERPRINT  {}".format(master))
        for k, v in subplans.items():
            if v["object_count"]:
                print("    {:<20} objects={:<6} scopes={:<3} {}".format(
                    k, v["object_count"], v["scope_count"], v["fingerprint"]))
                print("        APPROVE {} {} FOR {}".format(k, v["fingerprint"], cid))
            else:
                print("    {:<20} EMPTY".format(k))
        print("  bundle -> {}\n".format(p.relative_to(ROOT)))
        out[slug] = {"master": master,
                     "subplans": {k: v["fingerprint"] for k, v in subplans.items()}}

    (PLANS / "fingerprints.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
