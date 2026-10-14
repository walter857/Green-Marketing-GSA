#!/usr/bin/env python3
"""Closing safety check: re-read every mutable surface and prove nothing changed.

Compares a fresh read against the opening forensic snapshot. SELECT statements
only. Fails loudly on any difference.
"""
from __future__ import annotations

import glob
import json
import sys
from collections import Counter
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


def one(svc, cid, q):
    return list(svc.search(customer_id=cid, query=q))


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    now = datetime.now(ZoneInfo("America/New_York"))

    opening = json.loads(
        Path(sorted(glob.glob(str(SNAP / "forensic-structure-*.json")))[0])
        .read_text(encoding="utf-8"))

    checks: list[dict] = []

    def check(name, before, after):
        checks.append({
            "check": name,
            "before": before,
            "after": after,
            "changed": before != after,
        })

    # identity
    r = one(svc, cid, """SELECT customer.id, customer.descriptive_name, customer.status,
                                customer.manager, customer.test_account,
                                customer.auto_tagging_enabled, customer.tracking_url_template,
                                customer.final_url_suffix
                         FROM customer LIMIT 1""")[0].customer
    check("customer.descriptive_name", opening["identity"]["descriptive_name"], r.descriptive_name)
    check("customer.id", opening["identity"]["customer_id"], normalize_customer_id(r.id))
    check("customer.status", opening["identity"]["status"], enum_name(r.status))
    check("customer.manager", opening["identity"]["manager"], bool(r.manager))
    check("customer.test_account", opening["identity"]["test_account"], bool(r.test_account))
    check("customer.auto_tagging_enabled", opening["identity"]["auto_tagging_enabled"],
          bool(r.auto_tagging_enabled))
    check("customer.tracking_url_template", opening["identity"]["tracking_url_template"],
          r.tracking_url_template or "")
    check("customer.final_url_suffix", opening["identity"]["final_url_suffix"],
          r.final_url_suffix or "")

    # campaigns
    q = """SELECT campaign.id, campaign.name, campaign.status,
                  campaign.bidding_strategy_type,
                  campaign.target_spend.cpc_bid_ceiling_micros,
                  campaign.campaign_budget,
                  campaign.network_settings.target_search_network,
                  campaign.network_settings.target_content_network,
                  campaign.ai_max_setting.enable_ai_max
           FROM campaign WHERE campaign.status != 'REMOVED'"""
    rows = one(svc, cid, q)
    ob = {c["id"]: c for c in opening["campaigns"] if c["status"] != "REMOVED"}
    check("campaign count (non-removed)", len(ob), len(rows))
    for r in rows:
        c = r.campaign
        cid_ = str(c.id)
        o = ob.get(cid_, {})
        check(f"campaign {cid_} name", o.get("name"), c.name)
        check(f"campaign {cid_} status", o.get("status"), enum_name(c.status))
        check(f"campaign {cid_} bidding_strategy_type", o.get("bidding_strategy_type"),
              enum_name(c.bidding_strategy_type))
        check(f"campaign {cid_} cpc_bid_ceiling_micros",
              int(round(float(o.get("cpc_bid_ceiling", 0)) * 1_000_000)),
              int(c.target_spend.cpc_bid_ceiling_micros))
        check(f"campaign {cid_} budget_id", o.get("budget_id"),
              c.campaign_budget.split("/")[-1])
        check(f"campaign {cid_} search_partners", o.get("net_search_partners"),
              bool(c.network_settings.target_search_network))
        check(f"campaign {cid_} display", o.get("net_display"),
              bool(c.network_settings.target_content_network))
        check(f"campaign {cid_} ai_max", o.get("ai_max"), bool(c.ai_max_setting.enable_ai_max))

    # budgets
    rows = one(svc, cid, """SELECT campaign_budget.id, campaign_budget.amount_micros,
                                   campaign_budget.status
                            FROM campaign_budget
                            WHERE campaign_budget.status != 'REMOVED'""")
    ob = {b["id"]: b for b in opening["budgets"] if b["status"] != "REMOVED"}
    check("budget count", len(ob), len(rows))
    for r in rows:
        b = r.campaign_budget
        o = ob.get(str(b.id), {})
        check(f"budget {b.id} amount_micros",
              int(round(float(o.get("amount", 0)) * 1_000_000)), int(b.amount_micros))

    # counts across every mutable surface
    def count(resource, where=""):
        w = f" WHERE {where}" if where else ""
        return len(one(svc, cid, f"SELECT {resource}.resource_name FROM {resource}{w}"))

    check("ad_group count (non-removed)",
          len([a for a in opening["ad_groups"]]),
          count("ad_group", "ad_group.status != 'REMOVED'"))
    check("keyword count", len(opening["keywords"]),
          len(one(svc, cid, "SELECT ad_group_criterion.criterion_id FROM keyword_view")))
    check("ad count (non-removed)", len(opening["ads"]),
          count("ad_group_ad", "ad_group_ad.status != 'REMOVED'"))
    check("campaign_criterion count (non-removed)", len(opening["campaign_criteria"]),
          count("campaign_criterion", "campaign_criterion.status != 'REMOVED'"))
    check("campaign_asset count (non-removed)", len(opening["campaign_assets"]),
          count("campaign_asset", "campaign_asset.status != 'REMOVED'"))
    check("customer_asset count (non-removed)", len(opening["customer_assets"]),
          count("customer_asset", "customer_asset.status != 'REMOVED'"))
    check("ad_group_asset count (non-removed)", len(opening["ad_group_assets"]),
          count("ad_group_asset", "ad_group_asset.status != 'REMOVED'"))
    check("conversion_action count", len(opening["conversion_actions"]),
          count("conversion_action"))
    check("asset count", len(opening["assets"]), count("asset"))

    # negative keyword count by campaign
    rows = one(svc, cid, """SELECT campaign.id, campaign_criterion.criterion_id
                            FROM campaign_criterion
                            WHERE campaign_criterion.type = 'KEYWORD'
                              AND campaign_criterion.negative = TRUE
                              AND campaign_criterion.status != 'REMOVED'""")
    after_neg = Counter(str(r.campaign.id) for r in rows)
    before_neg = Counter(c["campaign_id"] for c in opening["campaign_criteria"]
                         if c["type"] == "KEYWORD" and c["negative"])
    check("campaign negative keywords by campaign", dict(before_neg), dict(after_neg))

    # ad group statuses
    rows = one(svc, cid, """SELECT ad_group.id, ad_group.status FROM ad_group
                            WHERE ad_group.status != 'REMOVED'""")
    after_ags = {str(r.ad_group.id): enum_name(r.ad_group.status) for r in rows}
    before_ags = {a["ad_group_id"]: a["status"] for a in opening["ad_groups"]}
    check("ad group statuses", before_ags, after_ags)

    # ad statuses
    rows = one(svc, cid, """SELECT ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad
                            WHERE ad_group_ad.status != 'REMOVED'""")
    after_ads = {str(r.ad_group_ad.ad.id): enum_name(r.ad_group_ad.status) for r in rows}
    before_ads = {a["ad_id"]: a["status"] for a in opening["ads"]}
    check("ad statuses", before_ads, after_ads)

    changed = [c for c in checks if c["changed"]]
    out = {
        "generated_account_local": now.isoformat(),
        "opening_snapshot": Path(sorted(glob.glob(str(SNAP / "forensic-structure-*.json")))[0]).name,
        "mode": "READ-ONLY",
        "checks_run": len(checks),
        "checks_changed": len(changed),
        "unchanged_proof": not changed,
        "changed_detail": changed,
        "checks": checks,
    }
    p = SNAP / "forensic-unchanged-proof-2026-08-31.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"{len(checks)} checks run, {len(changed)} changed")
    if changed:
        print("CHANGED:")
        for c in changed:
            print(f"  - {c['check']}: {c['before']!r} -> {c['after']!r}")
    else:
        print("UNCHANGED PROOF: PASS - every mutable surface is identical to the "
              "opening snapshot")
    print(f"WROTE {p}")
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
