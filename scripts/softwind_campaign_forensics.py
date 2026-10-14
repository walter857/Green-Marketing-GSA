#!/usr/bin/env python3
"""Forensic comparison of the two Softwind Power Washing campaigns. Read-only.

Answers one question with evidence: are 24103511039 and 24145053510 intentional
complementary campaigns, or duplicative/cannibalising campaigns?
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "campaign-forensics-2026-08-25.json"

A = "24103511039"   # Power Washing
B = "24145053510"   # Power Washing #2


def main() -> int:
    deep = json.loads((SNAP / "deep-read-2026-08-25.json").read_text(encoding="utf-8"))
    met = json.loads((SNAP / "metrics-2026-08-25.json").read_text(encoding="utf-8"))
    drift = json.loads((SNAP / "drift-check-2026-08-25b.json").read_text(encoding="utf-8"))
    geo = json.loads((SNAP / "geo-resolution-2026-08-25.json").read_text(encoding="utf-8"))

    camp = {c["id"]: c for c in deep["campaigns"]}
    AG = {a["id"]: a for a in deep["ad_groups"]}
    out = {"campaign_a": A, "campaign_b": B}

    # ---------- settings ----------
    def settings(cid):
        c = camp[cid]
        return {
            "name": c["name"], "status": c["status"],
            "serving_status": c["serving_status"], "primary_status": c["primary_status"],
            "primary_status_reasons": c["primary_status_reasons"],
            "created": c["start_date_time"], "end_date": c["end_date_time"] or "(none)",
            "channel": c["channel"],
            "bidding_strategy_type": c["bidding_strategy_type"],
            "cpc_bid_ceiling": c["target_spend_cpc_bid_ceiling"],
            "budget_id": c["budget"]["id"], "budget_name": c["budget"]["name"],
            "daily_budget": c["budget"]["amount"],
            "budget_shared": c["budget"]["explicitly_shared"],
            "budget_delivery": c["budget"]["delivery_method"],
            "network_google_search": c["network"]["google_search"],
            "network_search_partners": c["network"]["search_partners"],
            "network_display": c["network"]["display"],
            "geo_option": c["geo_target_type"]["positive"],
            "tracking_template": c["tracking_url_template"] or "(none)",
            "final_url_suffix": c["final_url_suffix"] or "(none)",
            "ai_max": False, "dsa": c["dsa_domain"] or "(none)",
            "targeting_restrictions": c["targeting_setting_restrictions"],
        }
    out["settings"] = {"A": settings(A), "B": settings(B)}
    out["settings_identical_fields"] = sorted(
        k for k in out["settings"]["A"]
        if k not in ("name", "created", "budget_id", "budget_name", "primary_status",
                     "primary_status_reasons")
        and out["settings"]["A"][k] == out["settings"]["B"][k])
    out["settings_differing_fields"] = {
        k: {"A": out["settings"]["A"][k], "B": out["settings"]["B"][k]}
        for k in out["settings"]["A"] if out["settings"]["A"][k] != out["settings"]["B"][k]}

    # ---------- geo ----------
    res = geo["resolved"]

    def geos(cid):
        ids = sorted(c["geo_target_constant"].split("/")[-1]
                     for c in deep["campaign_criteria"]
                     if c["campaign_id"] == cid and c["type"] == "LOCATION")
        return [{"id": g, "name": res.get(g, {}).get("canonical_name", "?"),
                 "type": res.get(g, {}).get("target_type", "?")} for g in ids]
    out["geo"] = {"A": geos(A), "B": geos(B)}
    out["geo_identical"] = ([g["id"] for g in out["geo"]["A"]]
                            == [g["id"] for g in out["geo"]["B"]])

    # ---------- schedule ----------
    def sched(cid):
        return sorted(
            "%s %02d:00-%02d:00" % (c["ad_schedule"]["day"],
                                    c["ad_schedule"]["start_hour"],
                                    c["ad_schedule"]["end_hour"])
            for c in deep["campaign_criteria"]
            if c["campaign_id"] == cid and c["type"] == "AD_SCHEDULE")
    out["schedule"] = {"A": sched(A), "B": sched(B)}
    out["schedule_identical"] = out["schedule"]["A"] == out["schedule"]["B"]

    # ---------- negatives ----------
    def negs(cid):
        return sorted((c["keyword"]["text"], c["keyword"]["match_type"])
                      for c in deep["campaign_criteria"]
                      if c["campaign_id"] == cid and c["type"] == "KEYWORD"
                      and c["negative"])
    na, nb = negs(A), negs(B)
    out["negatives"] = {"A_count": len(na), "B_count": len(nb),
                        "identical": na == nb,
                        "only_in_A": [x for x in na if x not in nb],
                        "only_in_B": [x for x in nb if x not in na]}

    # ---------- conversion goals ----------
    def goals(cid):
        return sorted((g["category"], g["origin"])
                      for g in drift["campaign_conversion_goals_now"]
                      if g["campaign_id"] == cid and g["biddable"])
    out["biddable_conversion_goals"] = {"A": goals(A), "B": goals(B)}
    out["conversion_goals_identical"] = goals(A) == goals(B)

    # ---------- assets ----------
    def assets(cid):
        return sorted(
            "%s:%s" % (a["field_type"],
                       a["sitelink_text"] or a["callout_text"] or a["snippet_header"]
                       or a["call_phone"] or a["asset_id"])
            for a in deep["campaign_assets"] if a["campaign_id"] == cid)
    out["assets"] = {"A": assets(A), "B": assets(B)}
    out["assets_identical"] = assets(A) == assets(B)
    out["shared_asset_ids"] = sorted(
        {a["asset_id"] for a in deep["campaign_assets"] if a["campaign_id"] == A}
        & {a["asset_id"] for a in deep["campaign_assets"] if a["campaign_id"] == B})

    # ---------- ad groups ----------
    def ags(cid, status=None):
        return {a["name"]: a for a in deep["ad_groups"]
                if a["campaign_id"] == cid and (status is None or a["status"] == status)}
    a_all, b_all = ags(A), ags(B)
    a_on, b_on = ags(A, "ENABLED"), ags(B, "ENABLED")
    out["ad_groups"] = {
        "A_total": len(a_all), "B_total": len(b_all),
        "A_enabled": sorted(a_on), "B_enabled": sorted(b_on),
        "same_name_in_both_campaigns": sorted(set(a_all) & set(b_all)),
        "ENABLED_IN_BOTH": sorted(set(a_on) & set(b_on)),
        "enabled_only_A": sorted(set(a_on) - set(b_on)),
        "enabled_only_B": sorted(set(b_on) - set(a_on)),
    }

    # ---------- keywords ----------
    def kws(cid, live_only):
        s = set()
        for k in deep["keywords"]:
            if k["campaign_id"] != cid:
                continue
            if live_only and not (k["status"] == "ENABLED"
                                  and AG[k["ad_group_id"]]["status"] == "ENABLED"):
                continue
            s.add((k["text"], k["match_type"]))
        return s
    la, lb = kws(A, True), kws(B, True)
    pa, pb = kws(A, False), kws(B, False)
    out["keywords"] = {
        "A_live_rows": len(la), "B_live_rows": len(lb),
        "A_all_rows": len(pa), "B_all_rows": len(pb),
        "LIVE_IN_BOTH": sorted(la & lb),
        "live_only_A": sorted(la - lb), "live_only_B": sorted(lb - la),
        "all_inventory_identical": pa == pb,
        "inventory_overlap_pct": round(100 * len(pa & pb) / len(pa | pb), 1),
    }

    # ---------- landing pages ----------
    def urls(cid):
        return sorted({u for a in deep["ads"]
                       if a["campaign_id"] == cid and a["status"] == "ENABLED"
                       and AG[a["ad_group_id"]]["status"] == "ENABLED"
                       for u in a["final_urls"]})
    out["landing_pages"] = {"A": urls(A), "B": urls(B),
                            "shared": sorted(set(urls(A)) & set(urls(B)))}

    # ---------- performance ----------
    perf = {r["campaign_id"]: r for r in drift["campaign_aggregate_now"]}
    out["performance"] = {"A": perf.get(A), "B": perf.get(B)}

    # ---------- search-term overlap ----------
    st = defaultdict(lambda: {"A": 0, "B": 0})
    for s in drift["search_terms_now"]:
        side = "A" if s["campaign"] == "Power Washing" else "B"
        st[s["search_term"]][side] += s["impressions"]
    both = {k: v for k, v in st.items() if v["A"] and v["B"]}
    out["search_terms"] = {
        "distinct_terms_A": sum(1 for v in st.values() if v["A"]),
        "distinct_terms_B": sum(1 for v in st.values() if v["B"]),
        "terms_seen_by_BOTH_campaigns": both,
        "term_overlap_count": len(both),
    }

    # ---------- the duplicate ad group, head to head ----------
    dup = out["ad_groups"]["ENABLED_IN_BOTH"]
    dupdetail = []
    agperf = {r["ad_group_id"]: r for r in met["ad_group_performance"]}
    for name in dup:
        for cid, label in ((A, "A"), (B, "B")):
            g = ags(cid, "ENABLED")[name]
            p = agperf.get(g["id"], {})
            dupdetail.append({
                "campaign": label, "campaign_id": cid, "ad_group_id": g["id"],
                "ad_group": name,
                "keywords": sorted({(k["text"], k["match_type"])
                                    for k in deep["keywords"]
                                    if k["ad_group_id"] == g["id"]
                                    and k["status"] == "ENABLED"}),
                "rsas": len([x for x in deep["ads"] if x["ad_group_id"] == g["id"]
                             and x["status"] == "ENABLED"]),
                "final_urls": sorted({u for x in deep["ads"]
                                      if x["ad_group_id"] == g["id"]
                                      and x["status"] == "ENABLED"
                                      for u in x["final_urls"]}),
                "impressions": p.get("impressions", 0), "clicks": p.get("clicks", 0),
                "cost": round(p.get("cost", 0), 2)})
    out["duplicate_ad_group_head_to_head"] = dupdetail

    # ---------- verdict ----------
    signals = {
        "identical_geo": out["geo_identical"],
        "identical_schedule": out["schedule_identical"],
        "identical_negatives": out["negatives"]["identical"],
        "identical_conversion_goals": out["conversion_goals_identical"],
        "identical_assets": out["assets_identical"],
        "identical_bidding": (out["settings"]["A"]["bidding_strategy_type"]
                              == out["settings"]["B"]["bidding_strategy_type"]),
        "identical_budget_amount": (out["settings"]["A"]["daily_budget"]
                                    == out["settings"]["B"]["daily_budget"]),
        "identical_keyword_inventory": out["keywords"]["all_inventory_identical"],
        "same_ad_group_names_in_both": len(
            out["ad_groups"]["same_name_in_both_campaigns"]),
        "ad_group_enabled_in_both": len(out["ad_groups"]["ENABLED_IN_BOTH"]),
        "keyword_rows_live_in_both": len(out["keywords"]["LIVE_IN_BOTH"]),
        "shared_landing_pages": len(out["landing_pages"]["shared"]),
        "search_terms_seen_by_both": out["search_terms"]["term_overlap_count"],
        "shared_asset_ids": len(out["shared_asset_ids"]),
    }
    out["duplication_signals"] = signals
    dup_score = sum([
        bool(signals["identical_geo"]), bool(signals["identical_schedule"]),
        bool(signals["identical_negatives"]), bool(signals["identical_conversion_goals"]),
        bool(signals["identical_assets"]), bool(signals["identical_bidding"]),
        bool(signals["identical_budget_amount"]),
        bool(signals["identical_keyword_inventory"]),
        signals["ad_group_enabled_in_both"] > 0,
        signals["keyword_rows_live_in_both"] > 0,
        signals["shared_landing_pages"] > 0,
        signals["search_terms_seen_by_both"] > 0,
    ])
    out["duplication_score"] = "%d/12" % dup_score
    out["verdict"] = ("DUPLICATIVE / CANNIBALIZING" if dup_score >= 9
                      else "INTENTIONAL COMPLEMENTARY" if dup_score <= 4
                      else "MIXED - REQUIRES JUDGEMENT")

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("SETTINGS IDENTICAL ON: %s" % ", ".join(out["settings_identical_fields"]))
    print()
    print("SETTINGS DIFFERING:")
    for k, v in out["settings_differing_fields"].items():
        print("   %-28s A=%r  B=%r" % (k, v["A"], v["B"]))
    print()
    print("geo identical: %s (%d targets each)"
          % (out["geo_identical"], len(out["geo"]["A"])))
    print("schedule identical: %s -> %s" % (out["schedule_identical"], out["schedule"]["A"]))
    print("negatives identical: %s (A=%d B=%d)"
          % (out["negatives"]["identical"], out["negatives"]["A_count"],
             out["negatives"]["B_count"]))
    print("conversion goals identical: %s -> %s"
          % (out["conversion_goals_identical"], out["biddable_conversion_goals"]["A"]))
    print("assets identical: %s (%d shared asset IDs)"
          % (out["assets_identical"], len(out["shared_asset_ids"])))
    print("keyword inventory identical: %s (overlap %.1f%%)"
          % (out["keywords"]["all_inventory_identical"],
             out["keywords"]["inventory_overlap_pct"]))
    print()
    print("AD GROUPS")
    print("  same NAME in both campaigns: %d of %d"
          % (len(out["ad_groups"]["same_name_in_both_campaigns"]),
             out["ad_groups"]["A_total"]))
    print("  ENABLED IN BOTH: %s" % out["ad_groups"]["ENABLED_IN_BOTH"])
    print("  enabled only A : %s" % out["ad_groups"]["enabled_only_A"])
    print("  enabled only B : %s" % out["ad_groups"]["enabled_only_B"])
    print()
    print("KEYWORD ROWS LIVE IN BOTH: %s" % out["keywords"]["LIVE_IN_BOTH"])
    print("SHARED LANDING PAGES: %s" % out["landing_pages"]["shared"])
    print()
    print("SEARCH TERMS SEEN BY BOTH CAMPAIGNS: %d" % out["search_terms"]["term_overlap_count"])
    for k, v in out["search_terms"]["terms_seen_by_BOTH_campaigns"].items():
        print("   '%s'  A=%d impr  B=%d impr" % (k, v["A"], v["B"]))
    print()
    print("DUPLICATE AD GROUP HEAD TO HEAD")
    for d in out["duplicate_ad_group_head_to_head"]:
        print("   %s %s  ag=%s  impr=%d clk=%d $%.2f  kw=%s  urls=%s"
              % (d["campaign"], d["ad_group"], d["ad_group_id"], d["impressions"],
                 d["clicks"], d["cost"], d["keywords"], d["final_urls"]))
    print()
    print("DUPLICATION SIGNALS: %s" % json.dumps(signals, indent=2))
    print("SCORE: %s" % out["duplication_score"])
    print("VERDICT: %s" % out["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
