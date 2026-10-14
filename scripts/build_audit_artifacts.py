#!/usr/bin/env python3
"""Build the Pro Green Austin audit deliverables from the local snapshot.

Reads local JSON only. Issues no API call and changes nothing in Google Ads.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

CID = "7380491929"
ACCOUNT = "Pro Green - Austin - Live"


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path}  ({len(rows)} rows)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()
    S = load(args.snapshot)
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    LIVE = {c["id"]: c["name"] for c in S["campaigns"] if c["status"] == "ENABLED"}

    # ---------------- 01 compact snapshot -------------------------------
    def perf(block, key, label):
        agg = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                                   "conversions": 0.0, "all_conversions": 0.0})
        for r in S[block][label]:
            a = agg[r[key]]
            a["impressions"] += r["impressions"]; a["clicks"] += r["clicks"]
            a["cost"] += r["cost"]; a["conversions"] += r["conversions"]
            a["all_conversions"] += r["all_conversions"]
        return {k: {kk: round(vv, 2) for kk, vv in v.items()} for k, v in agg.items()}

    camp_perf = {lbl: perf("campaign_performance", "campaign_id", lbl)
                 for lbl in S["campaign_performance"]}
    ag_perf = {lbl: perf("ad_group_performance", "ad_group_id", lbl)
               for lbl in S["ad_group_performance"]}

    compact = {
        "generated_on": S["generated_on"],
        "customer_id": CID,
        "exact_child_account_name": ACCOUNT,
        "identity": S["identity"],
        "windows": S["windows"],
        "campaigns": S["campaigns"],
        "campaign_performance_by_window": camp_perf,
        "ad_groups": S["ad_groups"],
        "ad_group_performance_by_window": ag_perf,
        "conversion_actions": S["conversion_actions"],
        "customer_conversion_goals": S["customer_conversion_goals"],
        "campaign_conversion_goals": S["campaign_conversion_goals"],
        "conversion_action_performance": S["conversion_action_performance"],
        "campaign_criteria_non_keyword": [
            c for c in S["campaign_criteria"] if c["type"] != "KEYWORD"],
        "campaign_negative_keyword_counts": {
            cid: sum(1 for c in S["campaign_criteria"]
                     if c["campaign_id"] == cid and c["type"] == "KEYWORD" and c["negative"])
            for cid in {c["campaign_id"] for c in S["campaign_criteria"]}},
        "shared_sets": S["shared_sets"],
        "campaign_shared_sets": S["campaign_shared_sets"],
        "shared_set_member_counts": {
            sid: sum(1 for m in S["shared_criteria"] if m["shared_set_id"] == sid)
            for sid in {m["shared_set_id"] for m in S["shared_criteria"]}},
        "customer_negative_criteria": S["customer_negative_criteria"],
        "keywords_positive": [k for k in S["keywords"] if not k["negative"]],
        "ad_group_negative_counts": {
            ag["id"]: sum(1 for k in S["keywords"]
                          if k["negative"] and k["ad_group_id"] == ag["id"])
            for ag in S["ad_groups"]},
        "ads": S["ads"],
        "campaign_assets": S["campaign_assets"],
        "ad_group_assets": S["ad_group_assets"],
        "customer_assets": S["customer_assets"],
        "assets_referenced": [a for a in S["assets"] if a["type"] != "IMAGE"],
        "asset_groups": S["asset_groups"],
        "landing_pages": S["landing_pages"],
        "geo_performance": S["geo_performance"],
        "segment_performance": S["segment_performance"],
        "calls": S["calls"],
        "recommendations": S["recommendations"],
        "recommendation_subscriptions": S["recommendation_subscriptions"],
        "change_events": S["change_events"],
        "change_event_limitation": S.get("change_event_limitation", ""),
        "read_errors": S["read_errors"],
        "queries_executed": S["queries_executed"],
        "note": ("Row-level search terms are excluded here and live in "
                 "05_search_term_verdicts.csv. No secrets or lead PII are present."),
    }
    p = out / "01_fresh_account_snapshot.json"
    p.write_text(json.dumps(compact, indent=2, default=str), encoding="utf-8")
    print(f"  wrote {p}  ({p.stat().st_size/1_000_000:.1f} MB)")

    # ---------------- 03 campaign + ad group verdicts --------------------
    def w(cid, label, key="campaign"):
        blk = camp_perf if key == "campaign" else ag_perf
        return blk[label].get(cid, {"impressions": 0, "clicks": 0, "cost": 0.0,
                                    "conversions": 0.0, "all_conversions": 0.0})

    rows = []
    for c in sorted(S["campaigns"], key=lambda x: (x["status"] != "ENABLED", x["name"])):
        at, l365, l30 = w(c["id"], "all_time"), w(c["id"], "last_365"), w(c["id"], "last_30")
        cpl = at["cost"] / at["conversions"] if at["conversions"] else ""
        if c["status"] == "ENABLED":
            verdict = "REPAIR_IN_PLACE"
            reason = ("Structure and geography are sound. The defects are bidding "
                      "(Maximize Clicks), an Eastern-time ad schedule in a Central-time "
                      "market, account-level cross-market sitelinks, and a conversion set "
                      "too noisy to bid on. All are repairable without a rebuild.")
        elif c["channel"] == "PERFORMANCE_MAX":
            verdict = "OUTSIDE_THIS_SERVICE_SCOPE"
            reason = ("Paused Performance Max. Green Marketing policy excludes PMax by "
                      "default and it needs its own audience, consent, budget and "
                      "measurement plan. No change proposed under this work order.")
        elif any(t in c["name"].lower() for t in ("sprinkler", "irrigation", "winter")):
            verdict = "OUTSIDE_THIS_SERVICE_SCOPE"
            reason = ("Paused irrigation-service campaign. A different exact service from "
                      "outdoor design & build. Left untouched; its history is preserved "
                      "as evidence and its converting queries must not be blocked "
                      "account-wide.")
        elif at["cost"] == 0 and at["impressions"] < 20:
            verdict = "INSUFFICIENT_DATA"
            reason = "Paused with effectively no delivery history. Nothing to judge."
        else:
            verdict = "KEEP"
            reason = ("Paused predecessor of the current build. Retain paused for "
                      "historical comparison; no spend and no proposed change.")
        rows.append({
            "level": "CAMPAIGN", "customer_id": CID, "resource_id": c["id"],
            "name": c["name"], "status": c["status"], "channel": c["channel"],
            "budget_id": c["budget_id"], "daily_budget": c["budget_amount"],
            "budget_shared": c["budget_shared"],
            "bidding_strategy": c["bidding_strategy_type"],
            "networks_search_partners": c["net_search_partners"],
            "networks_display": c["net_display"],
            "positive_geo": c["positive_geo"], "negative_geo": c["negative_geo"],
            "ai_max": c["ai_max_enabled"],
            "tracking_url_template": c["tracking_url_template"][:120],
            "all_time_cost": round(at["cost"], 2), "all_time_clicks": at["clicks"],
            "all_time_conversions": at["conversions"],
            "all_time_cost_per_conversion": round(cpl, 2) if cpl else "",
            "last_365_cost": round(l365["cost"], 2),
            "last_365_conversions": l365["conversions"],
            "last_30_cost": round(l30["cost"], 2), "last_30_conversions": l30["conversions"],
            "verdict": verdict, "evidence_and_reason": reason,
        })
    for ag in sorted(S["ad_groups"], key=lambda x: (x["campaign_name"], x["name"])):
        at, l30 = w(ag["id"], "all_time", "ag"), w(ag["id"], "last_30", "ag")
        live = ag["campaign_id"] in LIVE
        pos = sum(1 for k in S["keywords"]
                  if k["ad_group_id"] == ag["id"] and not k["negative"])
        neg = sum(1 for k in S["keywords"]
                  if k["ad_group_id"] == ag["id"] and k["negative"])
        ads = [a for a in S["ads"] if a["ad_group_id"] == ag["id"]]
        enabled_ads = sum(1 for a in ads if a["status"] == "ENABLED")
        if not live:
            verdict, reason = "OUTSIDE_THIS_SERVICE_SCOPE", "Belongs to a paused campaign."
        elif at["clicks"] == 0 and at["impressions"] < 20:
            verdict = "INSUFFICIENT_DATA"
            reason = (f"{at['impressions']} impressions, no clicks in the campaign's "
                      "27-day life. Cannot be judged; the cause is budget starvation, "
                      "not the ad group.")
        elif enabled_ads < 2:
            verdict = "REPAIR_IN_PLACE"
            reason = (f"{enabled_ads} enabled RSA against the Green Marketing default of 2. "
                      f"${at['cost']:.2f} spent, {at['clicks']} clicks, "
                      f"{at['conversions']:.0f} conversions.")
        else:
            verdict, reason = "KEEP", "Meets structure and RSA-count policy."
        rows.append({
            "level": "AD_GROUP", "customer_id": CID, "resource_id": ag["id"],
            "name": ag["name"], "status": ag["status"],
            "channel": f"in {ag['campaign_name']} ({ag['campaign_id']})",
            "budget_id": "", "daily_budget": "", "budget_shared": "",
            "bidding_strategy": f"ad_group cpc_bid={ag['cpc_bid']}",
            "networks_search_partners": "", "networks_display": "",
            "positive_geo": "", "negative_geo": "", "ai_max": "",
            "tracking_url_template": "",
            "all_time_cost": round(at["cost"], 2), "all_time_clicks": at["clicks"],
            "all_time_conversions": at["conversions"], "all_time_cost_per_conversion": "",
            "last_365_cost": "", "last_365_conversions": "",
            "last_30_cost": round(l30["cost"], 2), "last_30_conversions": l30["conversions"],
            "verdict": verdict,
            "evidence_and_reason": (f"positive_keywords={pos} ad_group_negatives={neg} "
                                    f"enabled_ads={enabled_ads}. {reason}"),
        })
    write_csv(out / "03_campaign_and_ad_group_verdicts.csv", rows)

    # ---------------- 04 keyword verdicts --------------------------------
    # A keyword criterion_id is shared by every ad group that uses the same text and match
    # type, so it is NOT a unique key. 188 criterion ids in this account appear in more than
    # one ad group. Aggregate on (criterion_id, ad_group_id) or metrics get summed across
    # unrelated ad groups and repeated on every row.
    kagg: dict[tuple, dict] = {}
    for lbl in ("all_time", "last_30"):
        for r in S["keyword_performance"][lbl]:
            a = kagg.setdefault((r["criterion_id"], r["ad_group_id"], lbl), {
                "impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
            a["impressions"] += r["impressions"]; a["clicks"] += r["clicks"]
            a["cost"] += r["cost"]; a["conversions"] += r["conversions"]

    rows = []
    for k in sorted((x for x in S["keywords"] if not x["negative"]),
                    key=lambda x: (x["campaign_status"] != "ENABLED",
                                   x["campaign_name"], x["ad_group_name"], x["text"])):
        at = kagg.get((k["criterion_id"], k["ad_group_id"], "all_time"),
                      {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
        l30 = kagg.get((k["criterion_id"], k["ad_group_id"], "last_30"),
                       {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
        live = k["campaign_id"] in LIVE
        cpc = at["cost"] / at["clicks"] if at["clicks"] else 0
        if not live:
            verdict = "OUTSIDE_THIS_SERVICE_SCOPE"
            reason = "Keyword in a paused campaign. No change proposed."
        elif at["conversions"] > 0:
            verdict = "KEEP"
            reason = f"Converted {at['conversions']:.0f} time(s) at ${cpc:.2f} CPC."
        elif at["clicks"] == 0 and at["impressions"] == 0:
            verdict = "WATCH"
            reason = ("Zero impressions in 27 days. The cause is budget starvation across "
                      "24 ad groups, not keyword quality. Judge after consolidation.")
        elif at["clicks"] == 0:
            verdict = "WATCH"
            reason = (f"{at['impressions']} impressions, no clicks. Too little evidence to "
                      "pause; re-evaluate after the bidding and schedule fixes.")
        elif cpc > 35:
            verdict = "WATCH"
            reason = (f"${cpc:.2f} average CPC on {at['clicks']} clicks with no conversion. "
                      "Cost driven by Maximize Clicks bidding with no bid ceiling, so the "
                      "keyword is not yet disproved. Re-judge after the bidding change.")
        else:
            verdict = "WATCH"
            reason = (f"{at['clicks']} clicks, ${at['cost']:.2f}, no conversion yet. "
                      "Sample far too small to pause.")
        rows.append({
            "customer_id": CID, "campaign_id": k["campaign_id"],
            "campaign_name": k["campaign_name"], "campaign_status": k["campaign_status"],
            "ad_group_id": k["ad_group_id"], "ad_group_name": k["ad_group_name"],
            "criterion_id": k["criterion_id"], "keyword_text": k["text"],
            "match_type": k["match_type"], "status": k["status"],
            "system_serving_status": k["system_serving_status"],
            "approval_status": k["approval_status"],
            "quality_score": k["quality_score"] or "",
            "expected_ctr": k["expected_ctr"], "ad_relevance": k["ad_relevance"],
            "landing_page_experience": k["landing_page_exp"],
            "keyword_final_urls": "|".join(k["final_urls"]),
            "all_time_impressions": at["impressions"], "all_time_clicks": at["clicks"],
            "all_time_cost": round(at["cost"], 2),
            "all_time_avg_cpc": round(cpc, 2) if cpc else "",
            "all_time_conversions": at["conversions"],
            "last_30_cost": round(l30["cost"], 2), "last_30_conversions": l30["conversions"],
            "verdict": verdict, "evidence_and_reason": reason,
        })
    write_csv(out / "04_keyword_verdicts.csv", rows)

    # ---------------- 08 ads, assets and policy --------------------------
    adperf = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                                  "conversions": 0.0})
    for r in S["ad_performance"]["all_time"]:
        a = adperf[r["ad_id"]]
        a["impressions"] += r["impressions"]; a["clicks"] += r["clicks"]
        a["cost"] += r["cost"]; a["conversions"] += r["conversions"]
    assets = {a["id"]: a for a in S["assets"]}
    rows = []
    for a in sorted(S["ads"], key=lambda x: (x["campaign_status"] != "ENABLED",
                                             x["campaign_name"], x["ad_group_name"])):
        p_ = adperf[a["ad_id"]]
        pins = [h["pinned"] for h in a["headlines"] if h["pinned"]]
        over = [h["text"] for h in a["headlines"] if len(h["text"]) > 30]
        over += [d["text"] for d in a["descriptions"] if len(d["text"]) > 90]
        rows.append({
            "object": "AD", "customer_id": CID, "campaign_id": a["campaign_id"],
            "campaign_name": a["campaign_name"], "campaign_status": a["campaign_status"],
            "ad_group_id": a["ad_group_id"], "ad_group_name": a["ad_group_name"],
            "resource_id": a["ad_id"], "type": a["type"], "status": a["status"],
            "ad_strength": a["ad_strength"], "approval_status": a["approval_status"],
            "review_status": a["review_status"],
            "policy_topics": "|".join(a["policy_topics"]),
            "final_urls": "|".join(a["final_urls"]),
            "tracking_url_template": a["tracking_url_template"][:120],
            "final_url_suffix": a["final_url_suffix"][:120],
            "headline_count": len(a["headlines"]),
            "description_count": len(a["descriptions"]),
            "pinned_count": len(pins),
            "over_limit_assets": "|".join(over),
            "all_time_impressions": p_["impressions"], "all_time_clicks": p_["clicks"],
            "all_time_cost": round(p_["cost"], 2),
            "all_time_conversions": p_["conversions"],
            "detail": "",
        })
    for link in S["customer_assets"]:
        a = assets.get(link["asset_id"], {})
        rows.append({
            "object": "ACCOUNT_ASSET", "customer_id": CID, "campaign_id": "",
            "campaign_name": "(account level - serves on every campaign)",
            "campaign_status": "", "ad_group_id": "", "ad_group_name": "",
            "resource_id": link["asset_id"], "type": link["field_type"],
            "status": link["status"], "ad_strength": "", "approval_status": "",
            "review_status": "", "policy_topics": "",
            "final_urls": "|".join(a.get("final_urls", [])),
            "tracking_url_template": "", "final_url_suffix": "",
            "headline_count": "", "description_count": "", "pinned_count": "",
            "over_limit_assets": "",
            "all_time_impressions": "", "all_time_clicks": "", "all_time_cost": "",
            "all_time_conversions": "",
            "detail": (f"source={link['source']} "
                       f"sitelink={a.get('sitelink_text', '')!r} "
                       f"snippet={a.get('snippet_header', '')}:{a.get('snippet_values', [])} "
                       f"callout={a.get('callout_text', '')!r}"),
        })
    for link in S["campaign_assets"]:
        if link["campaign_id"] not in LIVE:
            continue
        a = assets.get(link["asset_id"], {})
        rows.append({
            "object": "CAMPAIGN_ASSET", "customer_id": CID,
            "campaign_id": link["campaign_id"], "campaign_name": link["campaign_name"],
            "campaign_status": "ENABLED", "ad_group_id": "", "ad_group_name": "",
            "resource_id": link["asset_id"], "type": link["field_type"],
            "status": link["status"], "ad_strength": "", "approval_status": "",
            "review_status": "", "policy_topics": "",
            "final_urls": "|".join(a.get("final_urls", [])),
            "tracking_url_template": "", "final_url_suffix": "",
            "headline_count": "", "description_count": "", "pinned_count": "",
            "over_limit_assets": "",
            "all_time_impressions": "", "all_time_clicks": "", "all_time_cost": "",
            "all_time_conversions": "",
            "detail": (f"source={link['source']} "
                       f"sitelink={a.get('sitelink_text', '')!r} "
                       f"desc1={a.get('sitelink_desc1', '')!r} "
                       f"callout={a.get('callout_text', '')!r} "
                       f"snippet={a.get('snippet_header', '')}:{a.get('snippet_values', [])} "
                       f"call={a.get('call_phone_number', '')}"),
        })
    write_csv(out / "08_ads_assets_and_policy_audit.csv", rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
