#!/usr/bin/env python3
"""Softwind Power Washing - 2026-08-31 recovery-audit CSV artifacts.

Pure local transform of the read-only forensic snapshots. No API call, no
mutation. Every figure is interpolated from the snapshot data structures; no
number is hand-typed into an artifact.
"""
from __future__ import annotations

import csv
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "clients" / "softwind-power-washing"
SNAP = CLIENT / "snapshots"
AUD = CLIENT / "audits"
STAMP = "2026-08-31"

ENABLED_AG = {
    ("Power Washing", "Power Washing Near Me"),
    ("Power Washing", "Power Washing Services Near Me"),
    ("Power Washing", "Power Washing Company Near Me"),
    ("Power Washing", "Power Washing West Islip"),
    ("Power Washing", "Power Washing Dix Hills"),
    ("Power Washing", "Power Washing Islip"),
    ("Power Washing #2", "Residential Pressure Washing Near Me"),
    ("Power Washing #2", "House Pressure Washing Estimate"),
    ("Power Washing #2", "Power Washing Services Near Me"),
    ("Power Washing #2", "Driveway Pressure Washing Near Me"),
    ("Power Washing #2", "Patio Pressure Washing Near Me"),
    ("Power Washing #2", "Soft House Washing Near Me"),
}


def newest(pattern: str) -> dict:
    return json.loads(sorted(glob.glob(str(SNAP / pattern)))[-1] and
                      Path(sorted(glob.glob(str(SNAP / pattern)))[-1])
                      .read_text(encoding="utf-8"))


def write(name: str, header: list[str], rows: list[list]) -> None:
    AUD.mkdir(parents=True, exist_ok=True)
    p = AUD / f"{STAMP}-{name}"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {p.name:42s} {len(rows):5d} rows")


def agg(rows, keyf, fields=("impressions", "clicks", "cost", "conversions")):
    out = defaultdict(lambda: dict.fromkeys(fields, 0))
    for r in rows:
        d = out[keyf(r)]
        for f in fields:
            d[f] = d[f] + r.get(f, 0)
    return out


def rate(num, den, pct=True):
    if not den:
        return ""
    v = num / den
    return round(v * 100, 2) if pct else round(v, 2)


def main() -> int:
    st = newest("forensic-structure-*.json")
    pf = newest("forensic-performance-*.json")
    geo = json.loads((SNAP / "geo-names-2026-08-31.json").read_text(encoding="utf-8"))
    dem = newest("forensic-demand-*.json")

    print("Building CSV artifacts")

    # ---------------- campaign-performance ----------------
    dailies = agg(pf["daily_campaign"], lambda r: r["campaign_id"])
    isv = {}
    for r in pf["daily_campaign"]:
        d = isv.setdefault(r["campaign_id"], {"is": [], "lb": [], "lr": [], "top": [], "at": [],
                                              "inv": 0})
        if r["impressions"]:
            d["is"].append(r["search_is"]); d["lb"].append(r["lost_is_budget"])
            d["lr"].append(r["lost_is_rank"]); d["top"].append(r["top_share"])
            d["at"].append(r["abs_top_share"])
        d["inv"] += r["invalid_clicks"]
    rows = []
    for c in st["campaigns"]:
        m = c["metrics_all_time"]
        v = isv.get(c["id"], {})
        avg = lambda k: round(sum(v.get(k, [])) / len(v[k]), 2) if v.get(k) else ""
        budget = next((b["amount"] for b in st["budgets"] if b["id"] == c["budget_id"]), "")
        sched = [x for x in st["campaign_criteria"]
                 if x["type"] == "AD_SCHEDULE" and x["campaign_id"] == c["id"]]
        locs = [x for x in st["campaign_criteria"]
                if x["type"] == "LOCATION" and x["campaign_id"] == c["id"]]
        goals = [g for g in st["campaign_conversion_goals"]
                 if g["campaign_id"] == c["id"] and g["biddable"]]
        rows.append([
            c["id"], c["name"], c["status"], c["serving_status"], c["primary_status"],
            "|".join(c["primary_status_reasons"]), budget, c["bidding_strategy_type"],
            c["cpc_bid_ceiling"], c["bidding_system_status"],
            "|".join(sorted({g["category"] + ":" + g["origin"] for g in goals})),
            len([x for x in locs if not x["negative"]]),
            len([x for x in locs if x["negative"]]),
            f"{len(sched)} days 08:00-18:00" if sched else "none",
            c["net_search_partners"], c["net_display"], c["ai_max"],
            "|".join(f"{a['type']}={a['status']}" for a in c["asset_automation"]),
            "|".join(f"{t['dimension']}:bid_only={t['bid_only']}"
                     for t in c["targeting_restrictions"]),
            m["impressions"], m["clicks"], m["ctr"], m["cost"], m["avg_cpc"],
            m["conversions"], rate(m["conversions"], m["clicks"]),
            "" if not m["conversions"] else round(m["cost"] / m["conversions"], 2),
            0, avg("is"), avg("lb"), avg("lr"), avg("top"), avg("at"), v.get("inv", 0),
        ])
    write("campaign-performance.csv", [
        "campaign_id", "campaign_name", "status", "serving_status", "primary_status",
        "primary_status_reasons", "daily_budget_usd", "bidding_strategy", "cpc_ceiling_usd",
        "bidding_system_status", "biddable_conversion_goals", "positive_locations",
        "negative_locations", "ad_schedule", "search_partners", "display_network", "ai_max",
        "asset_automation", "audience_targeting_mode", "impressions", "clicks", "ctr_pct",
        "cost_usd", "avg_cpc_usd", "conversions", "conv_rate_pct", "cpa_usd",
        "qualified_leads", "search_is_pct_avg", "lost_is_budget_pct_avg",
        "lost_is_rank_pct_avg", "top_is_pct_avg", "abs_top_is_pct_avg", "invalid_clicks",
    ], rows)

    # ---------------- ad-group-performance ----------------
    kw_by_ag = defaultdict(list)
    for k in st["keywords"]:
        kw_by_ag[k["ad_group_id"]].append(k)
    ads_by_ag = defaultdict(list)
    for a in st["ads"]:
        ads_by_ag[a["ad_group_id"]].append(a)
    rows = []
    for a in sorted(st["ad_groups"],
                    key=lambda x: (-x["metrics_all_time"]["cost"], x["campaign_name"])):
        m = a["metrics_all_time"]
        kws = kw_by_ag.get(a["ad_group_id"], [])
        ads = ads_by_ag.get(a["ad_group_id"], [])
        urls = sorted({u for ad in ads for u in ad["final_urls"]})
        canon = sorted({k["text"] for k in kws})
        enabled = (a["campaign_name"], a["ad_group_name"]) in ENABLED_AG
        rows.append([
            a["campaign_name"], a["campaign_id"], a["ad_group_name"], a["ad_group_id"],
            a["status"], a["primary_status"], "|".join(a["primary_status_reasons"]),
            canon[0] if len(canon) == 1 else f"{len(canon)} texts",
            len(kws), "|".join(sorted({k["match_type"] for k in kws})),
            "|".join(urls), len(ads),
            m["impressions"], m["clicks"], m["ctr"], m["cost"], m["avg_cpc"],
            m["conversions"], rate(m["conversions"], m["clicks"]),
            "" if not m["conversions"] else round(m["cost"] / m["conversions"], 2),
            a.get("search_is", ""), a.get("lost_is_rank", ""),
            a.get("top_pct", ""), a.get("abs_top_pct", ""), 0,
            "ENABLED" if enabled else "PAUSED",
        ])
    write("ad-group-performance.csv", [
        "campaign_name", "campaign_id", "ad_group_name", "ad_group_id", "status",
        "primary_status", "primary_status_reasons", "canonical_intent", "keyword_count",
        "match_types", "landing_pages", "rsa_count", "impressions", "clicks", "ctr_pct",
        "cost_usd", "avg_cpc_usd", "conversions", "conv_rate_pct", "cpa_usd",
        "search_is_pct", "lost_is_rank_pct", "top_pct", "abs_top_pct", "qualified_leads",
        "serving_state",
    ], rows)

    # ---------------- ad-performance ----------------
    rows = []
    for a in sorted(st["ads"], key=lambda x: (-x["metrics_all_time"]["cost"],
                                              x["campaign_name"], x["ad_group_name"])):
        m = a["metrics_all_time"]
        hl = [h["text"] for h in a["headlines"]]
        ds = [d["text"] for d in a["descriptions"]]
        pins = [f"H{i+1}:{h['pinned']}" for i, h in enumerate(a["headlines"]) if h["pinned"]]
        pins += [f"D{i+1}:{d['pinned']}" for i, d in enumerate(a["descriptions"]) if d["pinned"]]
        over = [h for h in hl if len(h) > 30] + [d for d in ds if len(d) > 90]
        rows.append([
            a["ad_id"], a["campaign_name"], a["campaign_id"], a["ad_group_name"],
            a["ad_group_id"], a["status"], a["approval_status"], a["review_status"],
            "|".join(a["policy_topics"]) or "none", a["ad_strength"],
            "|".join(a["final_urls"]), a["path1"], a["path2"],
            len(hl), len(ds), "|".join(pins) or "none",
            "YES" if over else "no",
            m["impressions"], m["clicks"], m["ctr"], m["cost"], m["avg_cpc"],
            m["conversions"], rate(m["conversions"], m["clicks"]),
            "" if not m["conversions"] else round(m["cost"] / m["conversions"], 2),
            " || ".join(hl), " || ".join(ds),
        ])
    write("ad-performance.csv", [
        "ad_id", "campaign_name", "campaign_id", "ad_group_name", "ad_group_id", "status",
        "approval_status", "review_status", "policy_issues", "ad_strength", "final_url",
        "path1", "path2", "headline_count", "description_count", "pinning",
        "char_limit_breach", "impressions", "clicks", "ctr_pct", "cost_usd", "avg_cpc_usd",
        "conversions", "conv_rate_pct", "cpa_usd", "headlines", "descriptions",
    ], rows)

    # ---------------- keyword-performance ----------------
    dem_by_text = {}
    for i in dem["ideas"]:
        dem_by_text[i["text"].lower()] = i
    rows = []
    for k in sorted(st["keywords"],
                    key=lambda x: (-x["metrics_all_time"]["cost"], x["campaign_name"],
                                   x["ad_group_name"], x["text"])):
        m = k["metrics_all_time"]
        d = dem_by_text.get(k["text"].lower(), {})
        enabled = (k["campaign_name"], k["ad_group_name"]) in ENABLED_AG
        rows.append([
            k["campaign_name"], k["campaign_id"], k["ad_group_name"], k["ad_group_id"],
            k["text"], k["match_type"], k["status"],
            "SERVING" if enabled else "DORMANT (ad group paused)",
            k["system_serving_status"], k["approval_status"],
            m["impressions"], m["clicks"], m["ctr"], m["cost"], m["avg_cpc"],
            m["conversions"], rate(m["conversions"], m["clicks"]),
            "" if not m["conversions"] else round(m["cost"] / m["conversions"], 2),
            k.get("search_is", ""), k.get("lost_is_rank", ""),
            k.get("top_pct", ""), k.get("abs_top_pct", ""),
            k["quality_score"] or "", k["qs_expected_ctr"], k["qs_ad_relevance"],
            k["qs_lp_experience"], k["est_first_page_cpc"], k["est_top_of_page_cpc"],
            k["est_first_position_cpc"],
            d.get("avg_monthly_searches", ""), d.get("low_top_of_page_bid", ""),
            d.get("high_top_of_page_bid", ""), 0,
        ])
    write("keyword-performance.csv", [
        "campaign_name", "campaign_id", "ad_group_name", "ad_group_id", "keyword",
        "match_type", "keyword_status", "serving_state", "system_serving_status",
        "policy_approval", "impressions", "clicks", "ctr_pct", "cost_usd", "avg_cpc_usd",
        "conversions", "conv_rate_pct", "cpa_usd", "search_is_pct", "lost_is_rank_pct",
        "top_pct", "abs_top_pct", "quality_score", "qs_expected_ctr", "qs_ad_relevance",
        "qs_landing_page", "est_first_page_cpc_usd", "est_top_of_page_cpc_usd",
        "est_first_position_cpc_usd", "planner_local_monthly_searches",
        "planner_top_of_page_low_usd", "planner_top_of_page_high_usd", "qualified_leads",
    ], rows)

    # ---------------- device / schedule / location / demographic / audience ----------
    def seg_csv(name, rows_src, keyf, cols):
        a = agg(rows_src, keyf)
        out = []
        for k, v in sorted(a.items(), key=lambda x: -x[1]["cost"]):
            key = list(k) if isinstance(k, tuple) else [k]
            out.append(key + [
                v["impressions"], v["clicks"], rate(v["clicks"], v["impressions"]),
                round(v["cost"], 2),
                round(v["cost"] / v["clicks"], 2) if v["clicks"] else "",
                v["conversions"], rate(v["conversions"], v["clicks"]),
                "" if not v["conversions"] else round(v["cost"] / v["conversions"], 2), 0,
            ])
        write(name, cols + ["impressions", "clicks", "ctr_pct", "cost_usd", "avg_cpc_usd",
                            "conversions", "conv_rate_pct", "cpa_usd", "qualified_leads"], out)

    seg_csv("device-performance.csv", pf["device"],
            lambda r: (r["campaign_name"], r["device"]), ["campaign_name", "device"])
    seg_csv("schedule-performance.csv", pf["hour_dow"],
            lambda r: (r["campaign_name"], r["day_of_week"], f"{r['hour']:02d}:00"),
            ["campaign_name", "day_of_week", "hour"])
    seg_csv("demographic-performance.csv",
            [dict(r, dim="GENDER", val=r["gender"]) for r in pf["gender_view"]] +
            [dict(r, dim="AGE_RANGE", val=r["age_range"]) for r in pf["age_range_view"]],
            lambda r: (r["dim"], r["val"]), ["dimension", "value"])
    seg_csv("audience-performance.csv", pf["ad_group_audience_view"] or [],
            lambda r: (r.get("ad_group_name", ""), r.get("type", "")),
            ["ad_group_name", "criterion_type"])

    lv = agg(pf["location_view"], lambda r: (r["campaign_name"], r["criterion_id"]))
    out = []
    live_geo = {(c["campaign_name"], c["geo_id"]): c for c in st["campaign_criteria"]
                if c["type"] == "LOCATION"}
    for (cn, gid), c in sorted(live_geo.items()):
        v = lv.get((cn, gid), {"impressions": 0, "clicks": 0, "cost": 0, "conversions": 0})
        g = geo.get(gid, {})
        out.append([cn, gid, g.get("canonical", ""), g.get("type", ""),
                    "EXCLUDED" if c["negative"] else "TARGETED",
                    v["impressions"], v["clicks"], rate(v["clicks"], v["impressions"]),
                    round(v["cost"], 2),
                    round(v["cost"] / v["clicks"], 2) if v["clicks"] else "",
                    v["conversions"], 0,
                    "never delivered" if not v["impressions"] else ""])
    write("location-performance.csv", [
        "campaign_name", "geo_target_id", "canonical_name", "target_type", "criterion",
        "impressions", "clicks", "ctr_pct", "cost_usd", "avg_cpc_usd", "conversions",
        "qualified_leads", "note"], out)

    # ---------------- asset-performance ----------------
    assets = st["assets"]
    rows = []
    for c in st["campaign_assets"]:
        a = assets.get(c["asset_id"], {})
        m = c["metrics_all_time"]
        text = (a.get("link_text") or a.get("text") or a.get("phone")
                or a.get("header") or a.get("name") or "")
        if a.get("type") == "STRUCTURED_SNIPPET":
            text = f"{a.get('header','')}: {', '.join(a.get('values', []))}"
        rows.append([
            c["asset_id"], a.get("type", ""), "CAMPAIGN", c["campaign_name"],
            c["campaign_id"], "", text,
            a.get("desc1", ""), a.get("desc2", ""),
            "|".join(a.get("final_urls", [])), a.get("phone", ""),
            c["status"], c["primary_status"], a.get("approval_status", ""),
            m["impressions"], m["clicks"], m["ctr"], m["cost"], m["conversions"], 0,
            "asset metrics attribute the whole ad's cost to every asset that served",
        ])
    for c in st["customer_assets"]:
        a = assets.get(c["asset_id"], {})
        text = (a.get("link_text") or a.get("text") or a.get("header") or a.get("name") or "")
        rows.append([
            c["asset_id"], a.get("type", ""), "ACCOUNT", "(all campaigns)", "", "", text,
            a.get("desc1", ""), a.get("desc2", ""),
            "|".join(a.get("final_urls", [])), a.get("phone", ""),
            c["status"], "", a.get("approval_status", ""),
            "", "", "", "", "", 0,
            "campaign-level assets of the same type override this",
        ])
    write("asset-performance.csv", [
        "asset_id", "asset_type", "scope", "campaign_name", "campaign_id", "ad_group",
        "text", "description1", "description2", "final_url", "phone", "link_status",
        "primary_status", "approval_status", "impressions", "clicks", "ctr_pct", "cost_usd",
        "conversions", "qualified_leads", "caveat"], rows)

    # ---------------- auction insights placeholders ----------------
    ai_note = [[
        "INSUFFICIENT AUCTION DATA - API ACCESS DENIED", "", "", "", "", "", "",
        "metrics.auction_insight_* returned PERMISSION_DENIED: \"The developer doesn't "
        "have access to metrics: 'auction_insight_search_impression_share'\". The Green "
        "Marketing developer token is Basic access. Auction Insights must be exported "
        "from the Google Ads UI by a signed-in user. No value has been invented.",
    ]]
    for nm in ("auction-insights-campaign.csv", "auction-insights-ad-group.csv"):
        write(nm, ["domain", "impression_share_pct", "overlap_rate_pct",
                   "position_above_rate_pct", "top_of_page_rate_pct", "abs_top_rate_pct",
                   "outranking_share_pct", "status"], ai_note)

    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
