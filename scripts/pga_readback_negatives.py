#!/usr/bin/env python3
"""Post-write readback QA for the Pro Green Austin campaign-negative execution.

Reads all 68 created criteria back from Google Ads and compares them against the frozen
plan AND the immediate pre-execution snapshot. Read-only; changes nothing.

Exit code 0 only when every assertion passes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from gm_gsa.audit import ReadOnlyAudit  # noqa: E402
from gm_gsa.config import load_dotenv_if_available, load_yaml  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402

CAMPAIGNS = {"24053505504": "Progreen Austin | Search | Outdoor Living & Design",
             "24053505501": "Progreen Austin | Search | Hardscape Construction"}
BASELINE = 44
EXPECTED_AFTER = 78


def E(v):
    try:
        return enum_name(v)
    except Exception:  # noqa: BLE001
        return str(v)


def norm(t):
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


class Checks:
    def __init__(self):
        self.rows = []

    def add(self, name, ok, detail=""):
        self.rows.append((name, bool(ok), detail))
        return ok

    def report(self):
        w = max(len(n) for n, _, _ in self.rows)
        failed = sum(1 for _, ok, _ in self.rows if not ok)
        for n, ok, d in self.rows:
            print(f"  [{'PASS' if ok else 'FAIL'}] {n:<{w}}  {d}")
        print(f"\n  {len(self.rows) - failed}/{len(self.rows)} assertions passed")
        return failed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = yaml.safe_load(Path(args.plan).read_text(encoding="utf-8"))["change_plan"]
    actions = plan["subplans"]["EXISTING_RESOURCES"]["actions"]
    before = json.loads(Path(args.before).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))

    profile = load_yaml(args.client)["client"]
    cid = str(profile["google_ads"]["child_customer_id"])
    expected_name = profile["google_ads"]["exact_child_account_name"]

    load_dotenv_if_available(ROOT / ".env")
    r = ReadOnlyAudit(load_google_ads_client(), cid)

    ident = r.rows("identity", """
        SELECT customer.id, customer.descriptive_name, customer.manager,
               customer.test_account, customer.currency_code, customer.time_zone
        FROM customer
    """)[0].customer

    camp_neg = [{"campaign_id": str(x.campaign.id),
                 "criterion_id": str(x.campaign_criterion.criterion_id),
                 "text": x.campaign_criterion.keyword.text,
                 "match_type": E(x.campaign_criterion.keyword.match_type),
                 "negative": bool(x.campaign_criterion.negative),
                 "status": E(x.campaign_criterion.status),
                 "resource_name": x.campaign_criterion.resource_name}
                for x in r.rows("campaign_negatives", """
        SELECT campaign.id, campaign_criterion.criterion_id,
               campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
               campaign_criterion.negative, campaign_criterion.status,
               campaign_criterion.resource_name
        FROM campaign_criterion
        WHERE campaign_criterion.type = KEYWORD AND campaign_criterion.negative = TRUE
    """)]
    ag_neg = r.rows("ad_group_negatives", f"""
        SELECT ad_group.id FROM ad_group_criterion
        WHERE ad_group_criterion.type = KEYWORD AND ad_group_criterion.negative = TRUE
          AND campaign.id IN ({','.join(sorted(CAMPAIGNS))})
    """)
    pos = r.rows("positive_keywords", f"""
        SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
        WHERE ad_group_criterion.type = KEYWORD AND ad_group_criterion.negative = FALSE
          AND ad_group_criterion.status = 'ENABLED'
          AND campaign.id IN ({','.join(sorted(CAMPAIGNS))})
    """)
    ads = r.rows("ads", f"""
        SELECT ad_group_ad.ad.id FROM ad_group_ad
        WHERE ad_group_ad.status = 'ENABLED'
          AND campaign.id IN ({','.join(sorted(CAMPAIGNS))})
    """)
    shared = r.rows("shared_criteria", """
        SELECT shared_criterion.criterion_id FROM shared_criterion
        WHERE shared_criterion.type = KEYWORD
    """)
    camps = [{"id": str(x.campaign.id), "status": E(x.campaign.status),
              "budget": x.campaign_budget.amount_micros / 1_000_000,
              "bidding": E(x.campaign.bidding_strategy_type),
              "ceiling": x.campaign.target_spend.cpc_bid_ceiling_micros / 1_000_000}
             for x in r.rows("campaigns", """
        SELECT campaign.id, campaign.status, campaign.bidding_strategy_type,
               campaign.target_spend.cpc_bid_ceiling_micros, campaign_budget.amount_micros
        FROM campaign WHERE campaign.status = 'ENABLED'
    """)]
    ag_rows = r.rows("ad_groups", f"""
        SELECT ad_group.id FROM ad_group
        WHERE ad_group.status = 'ENABLED' AND campaign.id IN ({','.join(sorted(CAMPAIGNS))})
    """)

    c = Checks()
    c.add("identity.name", ident.descriptive_name == expected_name, ident.descriptive_name)
    c.add("identity.id", str(ident.id) == cid, str(ident.id))
    c.add("identity.not_manager", not ident.manager)
    c.add("identity.not_test", not ident.test_account)
    c.add("readback.zero_read_errors", not r.read_errors, str(len(r.read_errors)))

    live = defaultdict(dict)
    for x in camp_neg:
        if x["campaign_id"] in CAMPAIGNS:
            live[x["campaign_id"]][(norm(x["text"]), x["match_type"])] = x

    after = {k: len(v) for k, v in live.items()}
    c.add("counts.outdoor_living_44_to_78", after.get("24053505504") == EXPECTED_AFTER,
          f"{before_count(before, '24053505504')} -> {after.get('24053505504')}")
    c.add("counts.hardscape_44_to_78", after.get("24053505501") == EXPECTED_AFTER,
          f"{before_count(before, '24053505501')} -> {after.get('24053505501')}")
    c.add("counts.total_new_is_68",
          sum(after.values()) - sum(before_count(before, k) for k in CAMPAIGNS) == 68,
          f"{sum(after.values())} - {sum(before_count(before, k) for k in CAMPAIGNS)}")

    # every approved object present, exact
    missing, wrong, created = [], [], []
    for a in actions:
        key = (norm(a["negative_text"]), "PHRASE")
        got = live[a["resource_id"]].get(key)
        if not got:
            missing.append((a["action_id"], a["negative_text"], a["resource_id"]))
            continue
        if (got["text"] != a["negative_text"] or got["match_type"] != "PHRASE"
                or not got["negative"] or got["status"] != "ENABLED"):
            wrong.append((a["action_id"], got))
        created.append({
            "action_id": a["action_id"], "negative_text": got["text"],
            "match_type": got["match_type"], "negative": got["negative"],
            "status": got["status"], "campaign_id": a["resource_id"],
            "campaign_name": CAMPAIGNS[a["resource_id"]],
            "criterion_id": got["criterion_id"], "resource_name": got["resource_name"],
        })
    c.add("objects.all_68_present", not missing, str(missing[:3]))
    c.add("objects.all_exact_text_match_negative_enabled", not wrong, str(wrong[:2]))
    c.add("objects.68_readback_records", len(created) == 68, str(len(created)))
    c.add("objects.34_phrases_on_outdoor_living",
          sum(1 for x in created if x["campaign_id"] == "24053505504") == 34)
    c.add("objects.34_phrases_on_hardscape",
          sum(1 for x in created if x["campaign_id"] == "24053505501") == 34)
    c.add("objects.every_match_type_is_phrase",
          {x["match_type"] for x in created} == {"PHRASE"})
    c.add("objects.every_criterion_is_negative", all(x["negative"] for x in created))
    c.add("objects.every_criterion_enabled",
          {x["status"] for x in created} == {"ENABLED"})
    c.add("objects.no_duplicate_within_a_campaign",
          all(n == 1 for n in Counter((x["negative_text"], x["campaign_id"])
                                      for x in created).values()))
    c.add("objects.resource_names_returned",
          all(x["resource_name"].startswith(f"customers/{cid}/campaignCriteria/")
              for x in created))

    # nothing unexpected appeared
    approved_keys = {(norm(a["negative_text"]), a["resource_id"]) for a in actions}
    before_keys = {(norm(t), cid_) for cid_ in CAMPAIGNS
                   for t in before_texts(before, cid_)}
    now_keys = {(k[0], cid_) for cid_, v in live.items() for k in v}
    unexpected = sorted(now_keys - before_keys - approved_keys)
    c.add("objects.no_unexpected_negative_appeared", not unexpected, str(unexpected[:5]))
    lost = sorted(before_keys - now_keys)
    c.add("objects.no_pre_existing_negative_lost", not lost, str(lost[:5]))

    # unchanged resources
    b_ag = sum(1 for k in before["ad_group_keywords"]
               if k["negative"] and k["campaign_id"] in CAMPAIGNS)
    b_pos = sum(1 for k in before["ad_group_keywords"]
                if not k["negative"] and k["campaign_id"] in CAMPAIGNS
                and k["status"] == "ENABLED")
    b_ads = len([a for a in before["ad_final_urls"]
                 if a["campaign_id"] in CAMPAIGNS and a["status"] == "ENABLED"])
    c.add("unchanged.ad_group_negatives_246", len(ag_neg) == b_ag == 246,
          f"{b_ag} -> {len(ag_neg)}")
    c.add("unchanged.positive_keywords_48", len(pos) == b_pos == 48,
          f"{b_pos} -> {len(pos)}")
    c.add("unchanged.enabled_ads_48", len(ads) == b_ads == 48, f"{b_ads} -> {len(ads)}")
    c.add("unchanged.enabled_ad_groups_24", len(ag_rows) == 24, str(len(ag_rows)))
    c.add("unchanged.shared_criteria_8689",
          len(shared) == len(before["shared_criteria"]) == 8689,
          f"{len(before['shared_criteria'])} -> {len(shared)}")
    budgets = {x["id"]: round(x["budget"], 2) for x in camps}
    c.add("unchanged.budgets", budgets == {"24053505504": 39.47, "24053505501": 26.31},
          str(budgets))
    c.add("unchanged.total_daily_budget_65_78",
          round(sum(budgets.values()), 2) == 65.78, f"${round(sum(budgets.values()), 2)}")
    c.add("unchanged.bidding_and_ceiling",
          all(x["bidding"] == "TARGET_SPEND" and round(x["ceiling"], 2) == 22.00
              for x in camps),
          str([(x["id"], x["bidding"], x["ceiling"]) for x in camps]))
    c.add("unchanged.both_campaigns_enabled",
          {x["id"] for x in camps} == set(CAMPAIGNS))

    c.add("receipt.68_operations", receipt["api_operations"] == 68)
    c.add("receipt.68_responses", len(receipt["results"]) == 68)
    c.add("receipt.partial_failure_false", receipt["partial_failure"] is False)
    c.add("receipt.fingerprint", receipt["fingerprint"] == "628D3E61A9C2",
          receipt["fingerprint"])

    out = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "identity": {"id": str(ident.id), "descriptive_name": ident.descriptive_name,
                     "manager": bool(ident.manager),
                     "test_account": bool(ident.test_account),
                     "currency": ident.currency_code, "timezone": ident.time_zone},
        "campaign_negatives_before": {k: before_count(before, k) for k in CAMPAIGNS},
        "campaign_negatives_after": after,
        "created_objects": created,
        "unchanged": {
            "ad_group_negatives": {"before": b_ag, "after": len(ag_neg)},
            "positive_keywords": {"before": b_pos, "after": len(pos)},
            "enabled_ads": {"before": b_ads, "after": len(ads)},
            "enabled_ad_groups": len(ag_rows),
            "shared_criteria": {"before": len(before["shared_criteria"]),
                                "after": len(shared)},
            "budgets": budgets, "campaigns": camps,
        },
        "unexpected_negatives": unexpected,
        "lost_negatives": lost,
        "missing_objects": missing,
        "read_errors": r.read_errors,
    }
    failed = 0
    print(f"IDENTITY  {ident.descriptive_name} | {ident.id}\n")
    failed = c.report()
    out["all_assertions_passed"] = failed == 0
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\n  written: {args.out}")
    if failed:
        print("\nREADBACK FAILED.")
        return 1
    print("\nREADBACK PASSED. All 68 approved negatives are live and exact.")
    return 0


def before_count(before, campaign_id):
    return sum(1 for x in before["campaign_negative_keywords"]
               if x["campaign_id"] == campaign_id)


def before_texts(before, campaign_id):
    return [x["text"] for x in before["campaign_negative_keywords"]
            if x["campaign_id"] == campaign_id]


if __name__ == "__main__":
    raise SystemExit(main())
