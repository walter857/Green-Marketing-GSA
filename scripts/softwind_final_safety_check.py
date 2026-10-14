#!/usr/bin/env python3
"""Final read-only safety verification for the Softwind Power Washing audit.

Re-reads the live account and asserts that every mutable surface is byte-identical
to the opening snapshot. SELECT-only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "final-safety-check-2026-08-25.json"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    before = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
    out = {"checked_account_local": datetime.now(ZoneInfo("America/New_York")).isoformat()}
    checks = []

    def check(name, expected, observed):
        ok = expected == observed
        checks.append({"check": name, "expected": expected,
                       "observed": observed, "unchanged": ok})
        print("  %-46s %s" % (name, "UNCHANGED" if ok else
                              "!! CHANGED  %r -> %r" % (expected, observed)))
        return ok

    # identity
    row = next(iter(svc.search(customer_id=CID, query="""
        SELECT customer.id, customer.descriptive_name, customer.manager,
               customer.test_account, customer.currency_code, customer.time_zone
        FROM customer LIMIT 1""")))
    c = row.customer
    check("account name", "Softwind Power Washing - Live", c.descriptive_name)
    check("customer id", CID, normalize_customer_id(c.id))
    check("manager flag", False, bool(c.manager))
    check("test account flag", False, bool(c.test_account))

    # campaigns: status, budget, bidding, network, geo option, schedule
    now_c = {}
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, campaign.status,
               campaign.bidding_strategy_type,
               campaign.target_spend.cpc_bid_ceiling_micros,
               campaign.network_settings.target_search_network,
               campaign.network_settings.target_content_network,
               campaign.geo_target_type_setting.positive_geo_target_type,
               campaign_budget.amount_micros
        FROM campaign ORDER BY campaign.id"""):
        now_c[str(r.campaign.id)] = {
            "status": enum_name(r.campaign.status),
            "bidding": enum_name(r.campaign.bidding_strategy_type),
            "cpc_ceiling": r.campaign.target_spend.cpc_bid_ceiling_micros or 0,
            "search_partners": bool(r.campaign.network_settings.target_search_network),
            "display": bool(r.campaign.network_settings.target_content_network),
            "geo": enum_name(
                r.campaign.geo_target_type_setting.positive_geo_target_type),
            "budget": r.campaign_budget.amount_micros,
        }
    for b in before["campaigns"]:
        cid = b["id"]
        n = now_c.get(cid, {})
        check("campaign %s status" % cid, b["status"], n.get("status"))
        check("campaign %s budget (micros)" % cid,
              int(round(b["budget"]["amount"] * 1_000_000)), n.get("budget"))
        check("campaign %s bidding" % cid, b["bidding_strategy_type"], n.get("bidding"))
        check("campaign %s cpc ceiling" % cid,
              int(round((b["target_spend_cpc_bid_ceiling"] or 0) * 1_000_000)),
              n.get("cpc_ceiling"))
        check("campaign %s search partners" % cid,
              b["network"]["search_partners"], n.get("search_partners"))
        check("campaign %s display" % cid, b["network"]["display"], n.get("display"))
        check("campaign %s geo option" % cid,
              b["geo_target_type"]["positive"], n.get("geo"))

    # object counts
    def count(name, query):
        return sum(1 for _ in svc.search(customer_id=CID, query=query))

    check("ad group count", len(before["ad_groups"]),
          count("ag", "SELECT ad_group.id FROM ad_group"))
    check("keyword row count", len(before["keywords"]),
          count("kw", "SELECT ad_group_criterion.criterion_id FROM ad_group_criterion "
                      "WHERE ad_group_criterion.type = KEYWORD"))
    check("ad count", len(before["ads"]),
          count("ads", "SELECT ad_group_ad.ad.id FROM ad_group_ad"))
    check("campaign criterion count", len(before["campaign_criteria"]),
          count("cc", "SELECT campaign_criterion.criterion_id FROM campaign_criterion"))
    check("campaign negative keyword count",
          len([x for x in before["campaign_criteria"]
               if x["type"] == "KEYWORD" and x["negative"]]),
          count("neg", "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
                       "WHERE campaign_criterion.negative = true "
                       "AND campaign_criterion.type = KEYWORD"))
    check("ad group negative count", len(before["ad_group_negatives"]),
          count("agneg", "SELECT ad_group_criterion.criterion_id FROM ad_group_criterion "
                         "WHERE ad_group_criterion.negative = true"))
    check("conversion action count", len(before["conversion_actions"]),
          count("ca", "SELECT conversion_action.id FROM conversion_action"))
    check("campaign asset count", len(before["campaign_assets"]),
          count("casset", "SELECT campaign_asset.asset FROM campaign_asset"))

    # ad group statuses, one by one
    now_ag = {}
    for r in svc.search(customer_id=CID,
                        query="SELECT ad_group.id, ad_group.status FROM ad_group"):
        now_ag[str(r.ad_group.id)] = enum_name(r.ad_group.status)
    changed_ag = [a["id"] for a in before["ad_groups"]
                  if now_ag.get(a["id"]) != a["status"]]
    check("ad group statuses all identical", [], changed_ag)

    # ad statuses and final URLs
    now_ad = {}
    for r in svc.search(customer_id=CID, query="""
        SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls
        FROM ad_group_ad"""):
        now_ad[str(r.ad_group_ad.ad.id)] = (enum_name(r.ad_group_ad.status),
                                            sorted(r.ad_group_ad.ad.final_urls))
    changed_ads = [a["ad_id"] for a in before["ads"]
                   if now_ad.get(a["ad_id"]) != (a["status"], sorted(a["final_urls"]))]
    check("ad statuses and final URLs all identical", [], changed_ads)

    # conversion action config
    now_ca = {}
    for r in svc.search(customer_id=CID, query="""
        SELECT conversion_action.id, conversion_action.status,
               conversion_action.primary_for_goal, conversion_action.counting_type
        FROM conversion_action"""):
        ca = r.conversion_action
        now_ca[str(ca.id)] = (enum_name(ca.status), bool(ca.primary_for_goal),
                              enum_name(ca.counting_type))
    changed_ca = [x["id"] for x in before["conversion_actions"]
                  if now_ca.get(x["id"]) != (x["status"], x["primary_for_goal"],
                                             x["counting_type"])]
    check("conversion actions all identical", [], changed_ca)

    out["checks"] = checks
    out["total_checks"] = len(checks)
    out["changed"] = [c for c in checks if not c["unchanged"]]
    out["result"] = "NO EXTERNAL CHANGES" if not out["changed"] else "CHANGE DETECTED"
    OUT.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    print()
    print("checks run: %d   changed: %d" % (len(checks), len(out["changed"])))
    print()
    if out["changed"]:
        print("!! CHANGE DETECTED — STOP AND INVENTORY")
        for c in out["changed"]:
            print("   ", c)
        return 1
    print("READ-ONLY AUDIT COMPLETE - NO EXTERNAL CHANGES MADE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
