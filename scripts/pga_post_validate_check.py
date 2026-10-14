#!/usr/bin/env python3
"""Prove the validate-only run created nothing in the Pro Green Austin account.

Fresh read-only re-read of every counter the plan could possibly have touched, compared
with the pre-validate snapshot. GAQL SELECT only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.audit import ReadOnlyAudit  # noqa: E402
from gm_gsa.config import load_dotenv_if_available, load_yaml  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402

TARGETS = {"24053505504", "24053505501"}


def E(v):
    try:
        return enum_name(v)
    except Exception:  # noqa: BLE001
        return str(v)


def norm(t):
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--plan-actions", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    actions = json.loads(Path(args.plan_actions).read_text(encoding="utf-8"))
    proposed = {(a["negative_text"], a["resource_id"]) for a in actions}

    profile = load_yaml(args.client)["client"]
    cid = str(profile["google_ads"]["child_customer_id"])
    expected = profile["google_ads"]["exact_child_account_name"]

    load_dotenv_if_available(ROOT / ".env")
    r = ReadOnlyAudit(load_google_ads_client(), cid)

    ident = r.rows("identity", """
        SELECT customer.id, customer.descriptive_name, customer.manager,
               customer.test_account, customer.currency_code, customer.time_zone
        FROM customer
    """)[0].customer
    if str(ident.id) != cid or ident.descriptive_name != expected:
        print("IDENTITY MISMATCH ON RE-READ. STOP.")
        return 2

    camp_neg = [{"campaign_id": str(x.campaign.id),
                 "text": x.campaign_criterion.keyword.text,
                 "match_type": E(x.campaign_criterion.keyword.match_type),
                 "criterion_id": str(x.campaign_criterion.criterion_id)}
                for x in r.rows("campaign_negative_keywords", """
        SELECT campaign.id, campaign_criterion.criterion_id,
               campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
        FROM campaign_criterion
        WHERE campaign_criterion.type = KEYWORD AND campaign_criterion.negative = TRUE
    """)]
    ag_neg = [{"ad_group_id": str(x.ad_group.id), "campaign_id": str(x.campaign.id),
               "text": x.ad_group_criterion.keyword.text}
              for x in r.rows("ad_group_negatives", f"""
        SELECT ad_group.id, campaign.id, ad_group_criterion.keyword.text
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = KEYWORD AND ad_group_criterion.negative = TRUE
          AND campaign.id IN ({','.join(sorted(TARGETS))})
    """)]
    shared = [{"shared_set_id": str(x.shared_set.id),
               "text": x.shared_criterion.keyword.text}
              for x in r.rows("shared_criteria", """
        SELECT shared_set.id, shared_criterion.keyword.text
        FROM shared_criterion WHERE shared_criterion.type = KEYWORD
    """)]
    pos = [x for x in r.rows("positive_keywords", f"""
        SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.status
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = KEYWORD AND ad_group_criterion.negative = FALSE
          AND campaign.id IN ({','.join(sorted(TARGETS))})
    """)]
    ads = [x for x in r.rows("ads", f"""
        SELECT ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad
        WHERE campaign.id IN ({','.join(sorted(TARGETS))})
    """)]
    camps = [{"id": str(x.campaign.id), "status": E(x.campaign.status),
              "budget": x.campaign_budget.amount_micros / 1_000_000,
              "bidding": E(x.campaign.bidding_strategy_type)}
             for x in r.rows("campaigns", """
        SELECT campaign.id, campaign.status, campaign.bidding_strategy_type,
               campaign_budget.amount_micros FROM campaign
        WHERE campaign.status = 'ENABLED'
    """)]

    def counts(rows, key):
        return dict(Counter(x[key] for x in rows))

    before_camp = {c: sum(1 for x in before["campaign_negative_keywords"]
                          if x["campaign_id"] == c) for c in TARGETS}
    after_camp = {c: sum(1 for x in camp_neg if x["campaign_id"] == c) for c in TARGETS}
    before_ag = sum(1 for k in before["ad_group_keywords"]
                    if k["negative"] and k["campaign_id"] in TARGETS)
    before_pos = sum(1 for k in before["ad_group_keywords"]
                     if not k["negative"] and k["campaign_id"] in TARGETS)
    before_shared = len(before["shared_criteria"])
    before_ads = len([a for a in before["ad_final_urls"] if a["campaign_id"] in TARGETS])

    created = sorted({(x["text"], x["campaign_id"]) for x in camp_neg} & proposed)

    result = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "identity": {"id": str(ident.id), "descriptive_name": ident.descriptive_name,
                     "manager": bool(ident.manager),
                     "test_account": bool(ident.test_account),
                     "currency_code": ident.currency_code, "time_zone": ident.time_zone},
        "campaign_negatives_before": before_camp,
        "campaign_negatives_after": after_camp,
        "campaign_negatives_unchanged": before_camp == after_camp,
        "ad_group_negatives_before": before_ag,
        "ad_group_negatives_after": len(ag_neg),
        "ad_group_negatives_unchanged": before_ag == len(ag_neg),
        "shared_criteria_before": before_shared,
        "shared_criteria_after": len(shared),
        "shared_criteria_unchanged": before_shared == len(shared),
        "positive_keywords_before": before_pos,
        "positive_keywords_after": len(pos),
        "positive_keywords_unchanged": before_pos == len(pos),
        "enabled_ads_before": before_ads,
        "enabled_ads_after": len(ads),
        "ads_unchanged": before_ads == len(ads),
        "enabled_campaigns": camps,
        "proposed_objects": len(proposed),
        "proposed_objects_found_live": created,
        "no_proposed_negative_was_created": not created,
        "coverage_of_proposed_phrases": {
            "phrases": sorted({a["negative_text"] for a in actions}),
            "present_live_after_validate_only": sorted({t for t, _ in created}),
        },
        "read_errors": r.read_errors,
    }
    result["NO_EXTERNAL_CHANGES_MADE"] = all([
        result["campaign_negatives_unchanged"], result["ad_group_negatives_unchanged"],
        result["shared_criteria_unchanged"], result["positive_keywords_unchanged"],
        result["ads_unchanged"], result["no_proposed_negative_was_created"],
        not r.read_errors,
    ])

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"IDENTITY  {ident.descriptive_name} | {ident.id} | "
          f"manager={bool(ident.manager)} test={bool(ident.test_account)}")
    for k in ("campaign_negatives", "ad_group_negatives", "shared_criteria",
              "positive_keywords"):
        print(f"  {k:<24} before={result[k + '_before']}  after={result[k + '_after']}  "
              f"unchanged={result[k + '_unchanged']}")
    print(f"  enabled_ads              before={before_ads}  after={len(ads)}  "
          f"unchanged={result['ads_unchanged']}")
    for c in camps:
        print(f"  campaign {c['id']} status={c['status']} budget=${c['budget']:.2f} "
              f"bidding={c['bidding']}")
    print(f"  proposed objects: {len(proposed)}   found live: {len(created)}")
    print(f"\n  NO EXTERNAL CHANGES MADE: {result['NO_EXTERNAL_CHANGES_MADE']}")
    print(f"  written: {args.out}")
    return 0 if result["NO_EXTERNAL_CHANGES_MADE"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
