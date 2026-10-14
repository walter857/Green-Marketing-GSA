#!/usr/bin/env python3
"""Read-only portfolio pull: search terms (all time), every negative layer,
live structure and positive keywords, for the validated accounts only.

Raw search terms are written to disk. Only aggregates print to stdout.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

ACCOUNTS = {
    "pro-green-austin": ("7380491929", "Pro Green - Austin - Live"),
    "softwind-power-washing": ("1521725229", "Softwind Power Washing - Live"),
    "ambient-cooling-heating": ("2401959466", "Ambient Cooling - Live"),
    "softwind-landscape-masonry": ("2429758629", "Softwind Landscape & Masonry - Live"),
}
START = "2019-01-01"
END = "2026-08-28"
OUT = ROOT / "reports" / "st-corpus"


def rows(svc, cid, q):
    return list(svc.search(customer_id=cid, query=q))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    # A re-pull OVERWRITES reports/st-corpus/<slug>.json. The 2026-08-28 approval
    # bundles were derived from that corpus and carry fingerprints, so silently
    # re-pulling an already-planned account invalidates an approved plan (Google
    # restates conversions retroactively, so a re-pull is not idempotent).
    # --only is therefore required whenever any corpus already exists.
    ap.add_argument("--only", action="append", default=[], choices=sorted(ACCOUNTS),
                    help="pull just these slugs; repeatable")
    ap.add_argument("--allow-overwrite", action="store_true",
                    help="permit overwriting an existing corpus file")
    args = ap.parse_args()

    selected = {s_: v for s_, v in ACCOUNTS.items()
                if not args.only or s_ in args.only}
    if not selected:
        print("nothing selected")
        return 2

    clashes = [s_ for s_ in selected if (OUT / (s_ + "-corpus.json")).exists()]
    if clashes and not args.allow_overwrite:
        print("REFUSING: corpus already on disk for: {}".format(", ".join(sorted(clashes))))
        print("  A re-pull rewrites it and invalidates the approved plan fingerprints")
        print("  built from it. Use --only to select untouched accounts, or pass")
        print("  --allow-overwrite deliberately and re-run neg_preflight_local.py after.")
        return 2

    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    OUT.mkdir(parents=True, exist_ok=True)

    for slug, (cid, expected_name) in selected.items():
        ident = rows(svc, cid, "SELECT customer.id, customer.descriptive_name, "
                               "customer.manager, customer.test_account, customer.time_zone, "
                               "customer.currency_code FROM customer LIMIT 1")[0]
        obs_name = ident.customer.descriptive_name
        obs_id = str(ident.customer.id)
        ok = (obs_name == expected_name and obs_id == cid
              and not ident.customer.manager and not ident.customer.test_account)
        print("[{}] identity name_match={} id_match={} manager={} test={} GATE={}".format(
            slug, obs_name == expected_name, obs_id == cid, ident.customer.manager,
            ident.customer.test_account, "PASS" if ok else "FAIL"))
        if not ok:
            print("[{}] ABORT: identity gate failed".format(slug))
            continue

        camps = rows(svc, cid,
            "SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type, "
            "campaign_budget.amount_micros FROM campaign WHERE campaign.status != 'REMOVED'")
        campaigns = [{
            "id": str(r.campaign.id), "name": r.campaign.name,
            "status": enum_name(r.campaign.status),
            "channel": enum_name(r.campaign.advertising_channel_type),
            "daily_budget": r.campaign_budget.amount_micros / 1e6,
        } for r in camps]

        ags = rows(svc, cid,
            "SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id, campaign.name, "
            "campaign.status FROM ad_group WHERE ad_group.status != 'REMOVED' "
            "AND campaign.status != 'REMOVED'")
        adgroups = [{
            "id": str(r.ad_group.id), "name": r.ad_group.name,
            "status": enum_name(r.ad_group.status),
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "campaign_status": enum_name(r.campaign.status),
        } for r in ags]

        kws = rows(svc, cid,
            "SELECT ad_group.id, ad_group.name, campaign.id, campaign.name, "
            "ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
            "ad_group_criterion.keyword.match_type, ad_group_criterion.status "
            "FROM keyword_view "
            "WHERE ad_group_criterion.status != 'REMOVED' AND ad_group.status != 'REMOVED' "
            "AND campaign.status != 'REMOVED'")
        positives = [{
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "criterion_id": str(r.ad_group_criterion.criterion_id),
            "text": r.ad_group_criterion.keyword.text,
            "match_type": enum_name(r.ad_group_criterion.keyword.match_type),
            "status": enum_name(r.ad_group_criterion.status),
        } for r in kws]

        cneg = rows(svc, cid,
            "SELECT campaign.id, campaign.name, campaign_criterion.criterion_id, "
            "campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, "
            "campaign_criterion.negative, campaign_criterion.type FROM campaign_criterion "
            "WHERE campaign_criterion.negative = true AND campaign_criterion.type = 'KEYWORD' "
            "AND campaign.status != 'REMOVED'")
        campaign_negatives = [{
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "criterion_id": str(r.campaign_criterion.criterion_id),
            "text": r.campaign_criterion.keyword.text,
            "match_type": enum_name(r.campaign_criterion.keyword.match_type),
        } for r in cneg]

        agneg = rows(svc, cid,
            "SELECT campaign.id, campaign.name, ad_group.id, ad_group.name, "
            "ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, "
            "ad_group_criterion.keyword.match_type FROM ad_group_criterion "
            "WHERE ad_group_criterion.negative = true AND ad_group_criterion.type = 'KEYWORD' "
            "AND ad_group_criterion.status != 'REMOVED' AND ad_group.status != 'REMOVED' "
            "AND campaign.status != 'REMOVED'")
        adgroup_negatives = [{
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "criterion_id": str(r.ad_group_criterion.criterion_id),
            "text": r.ad_group_criterion.keyword.text,
            "match_type": enum_name(r.ad_group_criterion.keyword.match_type),
        } for r in agneg]

        sets = rows(svc, cid,
            "SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status "
            "FROM shared_set WHERE shared_set.status != 'REMOVED'")
        shared_sets = [{
            "id": str(r.shared_set.id), "name": r.shared_set.name,
            "type": enum_name(r.shared_set.type), "status": enum_name(r.shared_set.status),
        } for r in sets]

        shared_members = []
        for s in shared_sets:
            try:
                mem = rows(svc, cid,
                    "SELECT shared_criterion.criterion_id, shared_criterion.keyword.text, "
                    "shared_criterion.keyword.match_type, shared_set.id FROM shared_criterion "
                    "WHERE shared_set.id = " + s["id"])
                for r in mem:
                    shared_members.append({
                        "shared_set_id": s["id"], "shared_set_name": s["name"],
                        "shared_set_type": s["type"],
                        "criterion_id": str(r.shared_criterion.criterion_id),
                        "text": r.shared_criterion.keyword.text,
                        "match_type": enum_name(r.shared_criterion.keyword.match_type),
                    })
            except Exception as exc:  # noqa: BLE001
                print("[{}] shared_criterion {} ERROR {}".format(slug, s["id"], type(exc).__name__))

        css = rows(svc, cid,
            "SELECT campaign.id, campaign.name, shared_set.id, shared_set.name, shared_set.type "
            "FROM campaign_shared_set WHERE campaign.status != 'REMOVED'")
        campaign_shared_sets = [{
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "shared_set_id": str(r.shared_set.id), "shared_set_name": r.shared_set.name,
            "shared_set_type": enum_name(r.shared_set.type),
        } for r in css]

        st = rows(svc, cid,
            "SELECT search_term_view.search_term, search_term_view.status, "
            "campaign.id, campaign.name, ad_group.id, ad_group.name, "
            "segments.keyword.info.text, segments.keyword.info.match_type, "
            "metrics.impressions, metrics.clicks, metrics.cost_micros, "
            "metrics.conversions, metrics.conversions_value, metrics.all_conversions "
            "FROM search_term_view "
            "WHERE segments.date BETWEEN '" + START + "' AND '" + END + "'")
        terms = [{
            "term": r.search_term_view.search_term,
            "st_status": enum_name(r.search_term_view.status),
            "campaign_id": str(r.campaign.id), "campaign_name": r.campaign.name,
            "ad_group_id": str(r.ad_group.id), "ad_group_name": r.ad_group.name,
            "matched_keyword": r.segments.keyword.info.text,
            "matched_match_type": enum_name(r.segments.keyword.info.match_type),
            "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
            "cost": r.metrics.cost_micros / 1e6,
            "conversions": r.metrics.conversions,
            "conv_value": r.metrics.conversions_value,
            "all_conversions": r.metrics.all_conversions,
        } for r in st]

        payload = {
            "slug": slug, "customer_id": cid, "account_name": obs_name,
            "time_zone": ident.customer.time_zone,
            "currency": ident.customer.currency_code,
            "pulled_range": [START, END],
            "campaigns": campaigns, "ad_groups": adgroups,
            "positive_keywords": positives,
            "campaign_negatives": campaign_negatives,
            "ad_group_negatives": adgroup_negatives,
            "shared_sets": shared_sets, "shared_members": shared_members,
            "campaign_shared_sets": campaign_shared_sets,
            "search_terms": terms,
        }
        path = OUT / (slug + "-corpus.json")
        path.write_text(json.dumps(payload), encoding="utf-8")

        enabled_c = [c for c in campaigns if c["status"] == "ENABLED"]
        enabled_ag = [a for a in adgroups
                      if a["status"] == "ENABLED" and a["campaign_status"] == "ENABLED"]
        uniq_terms = len({t["term"] for t in terms})
        print("[{}] campaigns={} enabled={} | ad_groups={} enabled={} | positives={}".format(
            slug, len(campaigns), len(enabled_c), len(adgroups), len(enabled_ag), len(positives)))
        print("[{}] negatives: campaign={} ad_group={} shared_sets={} shared_members={} links={}".format(
            slug, len(campaign_negatives), len(adgroup_negatives), len(shared_sets),
            len(shared_members), len(campaign_shared_sets)))
        print("[{}] search_term rows={} unique_terms={} clicks={} cost=${:,.2f} conv={:.2f}".format(
            slug, len(terms), uniq_terms, sum(t["clicks"] for t in terms),
            sum(t["cost"] for t in terms), sum(t["conversions"] for t in terms)))
        print("[{}] written -> {}\n".format(slug, path.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
