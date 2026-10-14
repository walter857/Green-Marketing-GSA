#!/usr/bin/env python3
"""Read-only MTD (THIS_MONTH) performance pull across all '- live' child accounts.

Levels: campaign, ad_group, ad (ad_group_ad), keyword (keyword_view + quality score).
Writes one JSON bundle per account. No mutations of any kind.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.live_accounts import eligible_live_accounts, list_client_accounts

OUT = ROOT / "reports" / "portfolio-mtd-2026-08"

IS_FIELDS = {
    "search_absolute_top_impression_share",
    "search_rank_lost_absolute_top_impression_share",
    "search_budget_lost_absolute_top_impression_share",
    "search_impression_share",
}

BASE = [
    "impressions", "clicks", "ctr", "conversions", "cost_micros",
    "cost_per_conversion", "conversions_from_interactions_rate",
    "absolute_top_impression_percentage",
]
IS_FULL = [
    "search_absolute_top_impression_share",
    "search_rank_lost_absolute_top_impression_share",
    "search_budget_lost_absolute_top_impression_share",
    "search_impression_share",
]
IS_NOBUDGET = [
    "search_absolute_top_impression_share",
    "search_rank_lost_absolute_top_impression_share",
    "search_impression_share",
]


def m(row, names):
    """Extract metrics, preserving 'not set' (None) for impression-share fields."""
    out = {}
    pb = row.metrics._pb
    for n in names:
        if n in IS_FIELDS:
            out[n] = getattr(row.metrics, n) if pb.HasField(n) else None
        else:
            out[n] = getattr(row.metrics, n)
    return out


def run(service, cid, query):
    return list(service.search(customer_id=cid, query=query))


def try_run(service, cid, select, frm, where):
    """Run a query; on a field error, drop the fields the API named and retry once."""
    q = "SELECT " + ", ".join(select) + " FROM " + frm + " WHERE " + where
    try:
        return run(service, cid, q), select
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        kept = [f for f in select if f.split(".")[-1] not in msg]
        if kept and kept != select:
            dropped = sorted(set(select) - set(kept))
            print("    [bisect] dropped:", dropped)
            q2 = "SELECT " + ", ".join(kept) + " FROM " + frm + " WHERE " + where
            return run(service, cid, q2), kept
        raise


def metric_names(used, allowed):
    return [f.split(".")[-1] for f in used
            if f.startswith("metrics.") and f.split(".")[-1] in allowed]


def slugify(name):
    s = name.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    service = client.get_service("GoogleAdsService")
    manager_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    live = eligible_live_accounts(list_client_accounts(client, manager_id))
    OUT.mkdir(parents=True, exist_ok=True)

    DATE = "segments.date DURING THIS_MONTH"

    for acct in live:
        cid, name = acct.customer_id, acct.descriptive_name
        bundle = {"account": {"name": name, "customer_id": cid}}

        # ---------- account total ----------
        rows = run(service, cid,
                   "SELECT " + ", ".join("metrics." + x for x in BASE) +
                   " FROM customer WHERE " + DATE)
        bundle["account_total"] = m(rows[0], BASE) if rows else None

        # ---------- campaign ----------
        sel = ["campaign.id", "campaign.name", "campaign.status",
               "campaign.advertising_channel_type", "campaign_budget.amount_micros"] + \
              ["metrics." + x for x in BASE + IS_FULL]
        rows, used = try_run(service, cid, sel, "campaign",
                             DATE + " AND campaign.status != 'REMOVED'")
        camps = []
        for r in rows:
            d = {"campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
                 "status": r.campaign.status.name,
                 "channel": r.campaign.advertising_channel_type.name,
                 "daily_budget": r.campaign_budget.amount_micros / 1e6}
            d.update(m(r, BASE + metric_names(used, IS_FULL)))
            camps.append(d)
        bundle["campaigns"] = camps

        # ---------- ad group ----------
        sel = ["campaign.name", "ad_group.id", "ad_group.name", "ad_group.status"] + \
              ["metrics." + x for x in BASE + IS_NOBUDGET]
        rows, used = try_run(service, cid, sel, "ad_group",
                             DATE + " AND ad_group.status != 'REMOVED'")
        ags = []
        for r in rows:
            d = {"campaign": r.campaign.name, "ad_group_id": str(r.ad_group.id),
                 "ad_group": r.ad_group.name, "status": r.ad_group.status.name}
            d.update(m(r, BASE + metric_names(used, IS_NOBUDGET)))
            ags.append(d)
        bundle["ad_groups"] = ags

        # ---------- ad ----------
        sel = ["campaign.name", "ad_group.name", "ad_group_ad.ad.id",
               "ad_group_ad.status", "ad_group_ad.ad.type",
               "ad_group_ad.ad.responsive_search_ad.headlines",
               "ad_group_ad.ad_strength"] + ["metrics." + x for x in BASE]
        rows, used = try_run(service, cid, sel, "ad_group_ad",
                             DATE + " AND ad_group_ad.status != 'REMOVED'")
        ads = []
        for r in rows:
            hl = [h.text for h in r.ad_group_ad.ad.responsive_search_ad.headlines][:2]
            d = {"campaign": r.campaign.name, "ad_group": r.ad_group.name,
                 "ad_id": str(r.ad_group_ad.ad.id), "status": r.ad_group_ad.status.name,
                 "ad_type": r.ad_group_ad.ad.type_.name,
                 "ad_strength": r.ad_group_ad.ad_strength.name,
                 "headlines": hl}
            d.update(m(r, BASE))
            ads.append(d)
        bundle["ads"] = ads

        # ---------- keyword ----------
        sel = ["campaign.name", "ad_group.id", "ad_group.name",
               "ad_group_criterion.criterion_id", "ad_group_criterion.keyword.text",
               "ad_group_criterion.keyword.match_type", "ad_group_criterion.status",
               "ad_group_criterion.quality_info.quality_score",
               "ad_group_criterion.quality_info.creative_quality_score",
               "ad_group_criterion.quality_info.post_click_quality_score",
               "ad_group_criterion.quality_info.search_predicted_ctr"] + \
              ["metrics." + x for x in BASE + IS_NOBUDGET]
        rows, used = try_run(service, cid, sel, "keyword_view",
                             DATE + " AND ad_group_criterion.status != 'REMOVED'")
        kws = []
        for r in rows:
            qi = r.ad_group_criterion.quality_info
            d = {"campaign": r.campaign.name, "ad_group": r.ad_group.name,
                 "ad_group_id": str(r.ad_group.id),
                 "criterion_id": str(r.ad_group_criterion.criterion_id),
                 "keyword": r.ad_group_criterion.keyword.text,
                 "match_type": r.ad_group_criterion.keyword.match_type.name,
                 "status": r.ad_group_criterion.status.name,
                 "qs": qi.quality_score if qi._pb.HasField("quality_score") else None,
                 "qs_ad_relevance": qi.creative_quality_score.name,
                 "qs_lp_exp": qi.post_click_quality_score.name,
                 "qs_exp_ctr": qi.search_predicted_ctr.name}
            d.update(m(r, BASE + metric_names(used, IS_NOBUDGET)))
            kws.append(d)
        bundle["keywords"] = kws

        (OUT / (slugify(name) + ".json")).write_text(json.dumps(bundle, indent=1))
        t = bundle["account_total"] or {}
        print("{:38s} cid={} cost=${:9,.2f} conv={:6.1f} | camps={} ags={} ads={} kws={}".format(
            name, cid, t.get("cost_micros", 0) / 1e6, t.get("conversions", 0),
            len(camps), len(ags), len(ads), len(kws)))

    print("\nWROTE ->", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
