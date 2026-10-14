#!/usr/bin/env python3
"""Correction 5 (PLAN-H account-level impact) + Correction 3 (PLAN-E2 revision).

READ-ONLY. SELECT queries only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAP / "h-impact-e2-revision-2026-08-26.json"
ASSET = "403671792813"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    out = {"generated": "2026-08-26"}

    # ---------------- PLAN-H account-level impact ----------------
    camps = []
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, campaign.status,
               campaign.advertising_channel_type, campaign.serving_status
        FROM campaign ORDER BY campaign.id"""):
        camps.append({"id": str(r.campaign.id), "name": r.campaign.name,
                      "status": enum_name(r.campaign.status),
                      "channel": enum_name(r.campaign.advertising_channel_type),
                      "serving": enum_name(r.campaign.serving_status)})
    out["every_campaign_in_account"] = camps

    ca = []
    for r in svc.search(customer_id=CID, query="""
        SELECT customer_asset.asset, customer_asset.field_type,
               customer_asset.status, asset.id, asset.name, asset.type,
               asset.final_urls, asset.sitelink_asset.link_text
        FROM customer_asset"""):
        ca.append({"asset_id": str(r.asset.id),
                   "field_type": enum_name(r.customer_asset.field_type),
                   "status": enum_name(r.customer_asset.status),
                   "sitelink_text": r.asset.sitelink_asset.link_text or "",
                   "final_urls": list(r.asset.final_urls)})
    out["customer_level_assets"] = ca

    # is the asset ALSO linked at campaign or ad group level anywhere?
    camp_links = []
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, campaign_asset.asset,
               campaign_asset.field_type, campaign_asset.status, asset.id
        FROM campaign_asset"""):
        if str(r.asset.id) == ASSET:
            camp_links.append({"campaign_id": str(r.campaign.id),
                               "campaign": r.campaign.name,
                               "field_type": enum_name(r.campaign_asset.field_type),
                               "status": enum_name(r.campaign_asset.status)})
    ag_links = []
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, ad_group.id, ad_group.name, ad_group_asset.asset,
               ad_group_asset.field_type, asset.id FROM ad_group_asset"""):
        if str(r.asset.id) == ASSET:
            ag_links.append({"campaign_id": str(r.campaign.id),
                             "ad_group_id": str(r.ad_group.id),
                             "ad_group": r.ad_group.name})

    # delivery attributable to that asset's destination
    lp = []
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name,
               landing_page_view.unexpanded_final_url,
               metrics.impressions, metrics.clicks, metrics.cost_micros
        FROM landing_page_view
        WHERE segments.date BETWEEN '2026-01-01' AND '2026-08-26'"""):
        if "services/landscaping/pressure-washing" in r.landing_page_view.unexpanded_final_url:
            lp.append({"campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
                       "url": r.landing_page_view.unexpanded_final_url,
                       "impressions": int(r.metrics.impressions),
                       "clicks": int(r.metrics.clicks),
                       "cost": round(r.metrics.cost_micros / 1_000_000, 2)})

    out["plan_h_asset_403671792813_impact"] = {
        "asset_id": ASSET,
        "asset_type": "SITELINK 'Pressure Washing'",
        "linked_at_customer_level": any(a["asset_id"] == ASSET for a in ca),
        "also_linked_at_campaign_level": camp_links or "NONE",
        "also_linked_at_ad_group_level": ag_links or "NONE",
        "total_campaigns_in_account": len(camps),
        "campaigns_that_would_be_affected": [
            {"id": c["id"], "name": c["name"], "status": c["status"],
             "channel": c["channel"]} for c in camps],
        "unrelated_service_campaigns_affected": [
            c for c in camps if c["id"] not in ("24103511039", "24145053510")],
        "delivery_attributable_to_its_destination": lp,
        "verdict": None,
    }
    others = out["plan_h_asset_403671792813_impact"]["unrelated_service_campaigns_affected"]
    out["plan_h_asset_403671792813_impact"]["verdict"] = (
        ("SAFE - the account contains exactly %d campaigns and BOTH are the Power "
         "Washing campaigns under this work order. An account-level unlink has a fully "
         "contained blast radius. No unrelated or other-service campaign exists to be "
         "affected." % len(camps)) if not others else
        ("REVISE PLAN-H - %d other campaign(s) would be affected: %s"
         % (len(others), [c["name"] for c in others])))
    out["plan_h_fingerprint_action"] = (
        "PRESERVE 1D63EC1EB68D - no other campaign is affected, so no action changes"
        if not others else "VOID and re-fingerprint")

    # ---------------- PLAN-E2 revision ----------------
    terms = []
    for r in svc.search(customer_id=CID, query="""
        SELECT campaign.id, campaign.name, ad_group.name,
               search_term_view.search_term, segments.keyword.info.text,
               metrics.impressions, metrics.clicks, metrics.cost_micros,
               metrics.conversions
        FROM search_term_view
        WHERE segments.date BETWEEN '2026-01-01' AND '2026-08-26'"""):
        terms.append({"campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
                      "ad_group": r.ad_group.name,
                      "search_term": r.search_term_view.search_term,
                      "matched_keyword": r.segments.keyword.info.text,
                      "impressions": int(r.metrics.impressions),
                      "clicks": int(r.metrics.clicks),
                      "cost": round(r.metrics.cost_micros / 1_000_000, 2),
                      "conversions": float(r.metrics.conversions)})

    # keyword universe that must NOT be blocked
    snap = json.loads((SNAP / "rescue-snapshot-2026-08-26.json").read_text(encoding="utf-8"))
    AG = snap["ad_groups"]
    live_kw = sorted({k["text"] for k in snap["enabled_keywords_live"]})
    planned_kw = ["pressure washing near me"]          # PLAN-I5, the only survivor
    i2ae_kw = ["house washing company near me"]        # PLAN-I2A-E
    universe = sorted(set(live_kw) | set(planned_kw) | set(i2ae_kw))

    NEG = [
        ("roof cleaning", "PHRASE", r"roof\s*clean"),
        ("roof washing", "PHRASE", r"roof\s*wash"),
        ("house cleaning services near me", "EXACT", r"^house cleaning services near me$"),
    ]
    CAMPS = [("24103511039", "Power Washing"), ("24145053510", "Power Washing #2")]
    REASON = {
        "roof cleaning": ("Roof cleaning is listed under services_excluded in both "
                          "work-order.yaml and client.yaml. Out of scope for this work "
                          "order. CONDITIONAL on Walter confirming roof cleaning is "
                          "genuinely not offered."),
        "roof washing": ("Same out-of-scope service, alternative phrasing. CONDITIONAL "
                         "on the same confirmation."),
        "house cleaning services near me": (
            "Interior maid service - a different industry. Narrowed from the previous "
            "PHRASE 'house cleaning' to EXACT so it blocks only the one observed query "
            "and cannot catch legitimate exterior phrasings such as 'exterior house "
            "cleaning' or 'house cleaning power wash'."),
    }
    revised = []
    idx = 0
    for cid, cname in CAMPS:
        for text, mt, rx in NEG:
            idx += 1
            hits = [t for t in terms if re.search(rx, t["search_term"], re.I)]
            # would this negative block any keyword in the universe?
            blocked = []
            for k in universe:
                if mt == "PHRASE":
                    if all(w in k.split() for w in text.split()):
                        blocked.append(k)
                else:
                    if k == text:
                        blocked.append(k)
            revised.append({
                "action_id": "R3-E2A-%02d" % idx,
                "negative_keyword": text, "match_type": mt,
                "campaign_id": cid, "campaign": cname,
                "triggering_search_terms": [
                    {"search_term": h["search_term"], "impressions": h["impressions"],
                     "clicks": h["clicks"], "cost": h["cost"],
                     "conversions": h["conversions"],
                     "matched_keyword": h["matched_keyword"],
                     "ad_group": h["ad_group"], "campaign": h["campaign"]}
                    for h in hits] or "none observed",
                "impressions": sum(h["impressions"] for h in hits),
                "clicks": sum(h["clicks"] for h in hits),
                "cost": round(sum(h["cost"] for h in hits), 2),
                "conversions": sum(h["conversions"] for h in hits),
                "reason_out_of_scope": REASON[text],
                "blocks_approved_keywords": blocked or "NONE",
                "blocks_planned_skag_keywords": [
                    k for k in blocked if k in planned_kw + i2ae_kw] or "NONE",
                "rollback": "Remove the campaign_criterion. Immediate, no residue.",
                "object_count": 1})
    out["plan_e2a_revised"] = {
        "supersedes_fingerprint": "09E91EA674C8",
        "change": ("Removed PHRASE 'house cleaning'. Replaced with EXACT "
                   "[house cleaning services near me] in both campaigns."),
        "keyword_universe_checked": universe,
        "actions": revised,
        "blocks_zero_approved_keywords": all(
            r["blocks_approved_keywords"] == "NONE" for r in revised),
        "blocks_zero_planned_skag_keywords": all(
            r["blocks_planned_skag_keywords"] == "NONE" for r in revised),
        "conditional_on": ("Walter confirming roof cleaning is out of scope. If Softwind "
                           "DOES offer roof cleaning, drop actions 01, 02, 04 and 05 and "
                           "re-fingerprint with only the two EXACT negatives."),
    }

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    h = out["plan_h_asset_403671792813_impact"]
    print("PLAN-H ACCOUNT-LEVEL IMPACT - asset %s" % ASSET)
    print("  every campaign in the account (%d):" % len(camps))
    for c in camps:
        print("     %s %-18s %s / %s / %s" % (c["id"], c["name"], c["status"],
                                              c["channel"], c["serving"]))
    print("  also linked at campaign level : %s" % h["also_linked_at_campaign_level"])
    print("  also linked at ad group level : %s" % h["also_linked_at_ad_group_level"])
    print("  unrelated campaigns affected  : %s"
          % (h["unrelated_service_campaigns_affected"] or "NONE"))
    print("  delivery to its destination   :")
    for r in h["delivery_attributable_to_its_destination"]:
        print("     %s impr=%d clk=%d $%.2f  %s" % (r["campaign"], r["impressions"],
                                                    r["clicks"], r["cost"], r["url"]))
    print("  VERDICT: %s" % h["verdict"])
    print("  FINGERPRINT: %s" % out["plan_h_fingerprint_action"])
    print()
    e = out["plan_e2a_revised"]
    print("PLAN-E2A REVISED - %d mutations" % len(e["actions"]))
    for a in e["actions"]:
        st = a["triggering_search_terms"]
        print("  %s '%s' [%s] campaign %s"
              % (a["action_id"], a["negative_keyword"], a["match_type"], a["campaign_id"]))
        if isinstance(st, list):
            for x in st:
                print("      trigger '%s' impr=%d clk=%d $%.2f conv=%.0f"
                      % (x["search_term"], x["impressions"], x["clicks"], x["cost"],
                         x["conversions"]))
        print("      blocks approved keywords: %s" % a["blocks_approved_keywords"])
        print("      blocks planned SKAG kw  : %s" % a["blocks_planned_skag_keywords"])
    print()
    print("  blocks ZERO approved keywords     : %s" % e["blocks_zero_approved_keywords"])
    print("  blocks ZERO planned SKAG keywords : %s" % e["blocks_zero_planned_skag_keywords"])
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
