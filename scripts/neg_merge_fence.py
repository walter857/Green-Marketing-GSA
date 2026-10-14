#!/usr/bin/env python3
"""Merge a READY cross-account scope fence into an account's approval bundle as
a NEG_CROSS_ACCOUNT_FENCE subplan.

neg_bundle.py builds the four keyword-derived layers. The fence is built
separately by neg_cross_account.py from the owner's scope instruction rather
than from search-term evidence, and on 2026-08-28 it was merged into Softwind
Power Washing's bundle by hand. This script makes that step reproducible so
neg_preflight_local.py and neg_execute.py can consume the fence for any account.

Read/write local files only. No API calls, no mutations.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.safety import approval_code

FENCE_DIR = ROOT / "reports" / "st-cross-account"
CORPUS = ROOT / "reports" / "st-corpus"
CATEGORY = "CROSS_ACCOUNT_SCOPE_FENCE"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--plan", required=True, help="path to the bundle JSON")
    args = ap.parse_args()

    fence_p = FENCE_DIR / (args.slug + "-scope-fence.json")
    fence = json.loads(fence_p.read_text(encoding="utf-8"))
    if fence.get("status") != "READY":
        print("REFUSING: fence status is {!r}, not READY.".format(fence.get("status")))
        return 2

    plan_p = ROOT / args.plan if not Path(args.plan).is_absolute() else Path(args.plan)
    plan = json.loads(plan_p.read_text(encoding="utf-8"))

    target = plan["target"]
    if target["child_customer_id"] != fence["customer_id"]:
        print("REFUSING: bundle is {} but fence is {}.".format(
            target["child_customer_id"], fence["customer_id"]))
        return 2

    corpus = json.loads((CORPUS / (args.slug + "-corpus.json")).read_text(encoding="utf-8"))
    live = [c for c in corpus["campaigns"] if c["status"] == "ENABLED"]
    if len(live) != fence["live_campaigns"]:
        print("REFUSING: fence assumed {} live campaigns, corpus shows {}.".format(
            fence["live_campaigns"], len(live)))
        return 2

    phrases = [n["text"] if isinstance(n, dict) else n for n in fence["negatives"]]

    # Redundancy: never re-create a negative already live on that campaign.
    existing = {}
    for n in corpus["campaign_negatives"]:
        existing.setdefault(n["campaign_id"], set()).add(
            (n["text"].strip().lower(), n["match_type"]))

    # Cross-layer redundancy. NEG_CAMPAIGN_LEVEL is minted from waste evidence
    # and the fence is minted preventively from the owner's scope instruction,
    # so the same exterior-cleaning phrase can legitimately arrive from both.
    # Creating it twice on one campaign is a duplicate the API would reject or
    # silently drop, and neg_preflight_local.py only dedupes WITHIN a layer.
    # The evidence-derived layer wins; the fence yields.
    in_other_layer = {}
    for name, sub in plan["subplans"].items():
        if name in ("NEG_CROSS_ACCOUNT_FENCE", "NEG_AD_GROUP_LEVEL",
                    "NEG_CROSS_AD_GROUP"):
            continue
        for d in sub.get("detail") or []:
            for n in d["negatives"]:
                in_other_layer.setdefault(d["campaign_id"], set()).add(
                    (n["text"].strip().lower(), n["match_type"]))

    detail, total, skipped, deduped = [], 0, 0, 0
    for c in sorted(live, key=lambda x: x["id"]):
        have = existing.get(c["id"], set())
        already = in_other_layer.get(c["id"], set())
        negs = []
        for t in phrases:
            key = (t.strip().lower(), "PHRASE")
            if key in have:
                skipped += 1
                continue
            if key in already:
                deduped += 1
                continue
            negs.append({"text": t, "match_type": "PHRASE", "category": CATEGORY})
        total += len(negs)
        detail.append({"campaign_id": c["id"], "campaign_name": c["name"],
                       "negatives": negs})

    subplan = {
        # Placeholder; replaced below with approval_code(summary), which is the
        # convention every other subplan in the bundle uses and the value
        # neg_preflight_local.py recomputes and neg_execute.py checks --approve
        # against. Storing neg_cross_account's own code here instead would make
        # the printed approval code disagree with the executor's check.
        "fingerprint": None,
        "object_count": total,
        "scope_count": len(detail),
        "summary": {
            "target": target,
            "subplan": "NEG_CROSS_ACCOUNT_FENCE",
            "service": "CampaignCriterionService",
            "mutation": "create",
            "status_on_create": "ENABLED (a negative keyword has no paused state)",
            "scopes": [d["campaign_id"] for d in detail],
            "object_count": total,
            "match_types": {"PHRASE": total},
            "categories": {CATEGORY: total},
            "fence_reason": fence["fence_reason"],
            "already_live_skipped": skipped,
            "deduped_against_other_layers": deduped,
            "source_fence_fingerprint": fence["fingerprint"],
        },
        "detail": detail,
    }

    subplan["fingerprint"] = approval_code(subplan["summary"])
    plan["subplans"]["NEG_CROSS_ACCOUNT_FENCE"] = subplan
    plan.setdefault("evidence", {})["cross_account_fence_file"] = str(
        fence_p.relative_to(ROOT)).replace("\\", "/")
    plan["master_fingerprint"] = approval_code({
        "customer_id": target["child_customer_id"],
        "subplans": {k: v["fingerprint"] for k, v in sorted(plan["subplans"].items())}})

    plan_p.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    print("merged NEG_CROSS_ACCOUNT_FENCE into {}".format(plan_p.relative_to(ROOT)))
    print("  phrases per campaign : {}".format(len(phrases)))
    print("  live campaigns       : {}  ({})".format(
        len(detail), ", ".join(d["campaign_name"] for d in detail)))
    print("  objects              : {}".format(total))
    print("  already live, skipped: {}".format(skipped))
    print("  deduped vs other layer: {}".format(deduped))
    print("  source fence fp      : {}".format(fence["fingerprint"]))
    print("  SUBPLAN fingerprint  : {}".format(subplan["fingerprint"]))
    print("  NEW master           : {}".format(plan["master_fingerprint"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
