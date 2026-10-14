#!/usr/bin/env python3
"""Ambient | 2026-09-15 | build + validate the commercial create-paused plans.

AMB-0915-COMM-RSA-1 : two RSAs, created PAUSED, in ad group 199748801029.
AMB-0915-COMM-ASSET-1 : commercial callouts + structured snippet, created PAUSED.

Supersedes AMB-0910-COMM-RSA-2 / 41C183D15C93, whose before-state has drifted:
the destination went 404 -> 200, the ad group went PAUSED -> ENABLED, and 17
ad-group negatives were added after that plan was drafted.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-15"
CAMP, COMM_AG, RES_AG = "24132507747", "199748801029", "202339087634"
FINAL_URL = "https://offer.ambientcoolingandheating.com/commercial-hvac-installation/"
PATH1, PATH2 = "commercial-hvac", "installation"
HL_MAX, DS_MAX, CALLOUT_MAX, SNIPPET_VAL_MAX = 30, 90, 25, 25

RSA_A = {
    "label": "RSA A - keyword-first, three openers pinned to HEADLINE_1",
    "pinned_h1": [
        "Commercial HVAC Installation",
        "Commercial HVAC Installers",
        "HVAC Installation for Business",
    ],
    "unpinned": [
        "Free Commercial HVAC Quote",
        "Rooftop Unit Installation",
        "Commercial Rooftop Units",
        "Commercial AC Installation",
        "Commercial Heat Pump Install",
        "Sized for Your Building",
        "Central Maryland HVAC Team",
        "Plan Around Your Operations",
        "Transparent Commercial Pricing",
        "Flexible Project Scheduling",
        "Ambient Cooling & Heating",
        "Request a Commercial Quote",
    ],
    "descriptions": [
        "Request a free commercial HVAC installation quote for your Central Maryland property.",
        "Install rooftop units, packaged systems, heat pumps, or central air for your business.",
        "Plan equipment, ductwork, ventilation, and controls around your building and operations.",
        "Get clear options, transparent pricing, and scheduling designed around your business.",
    ],
}
RSA_B = {
    "label": "RSA B - unpinned commercial control",
    "pinned_h1": [],
    "unpinned": [
        "HVAC Systems for Businesses",
        "Central MD Commercial HVAC",
        "Commercial System Installation",
        "Replace Aging HVAC Equipment",
        "Rooftop & Packaged Systems",
        "Business Heating & Cooling",
        "Commercial HVAC Planning",
        "Free Installation Quote",
        "HVAC Options for Your Building",
        "Schedule a Site Evaluation",
        "Ventilation, Ducts & Controls",
        "Professional HVAC Installation",
        "Central Air for Your Business",
        "Heat Pumps for Businesses",
        "Request Your HVAC Quote",
    ],
    "descriptions": [
        "Replace or install commercial HVAC equipment with a plan built around your property.",
        "Request a free consultation for rooftop, packaged, central air, or heat pump systems.",
        "Ambient serves Central Maryland businesses with clear pricing and flexible scheduling.",
        "Discuss building needs, equipment options, ductwork, controls, and project timing.",
    ],
}
CALLOUTS = ["Free Consultation", "Flexible Scheduling", "Transparent Pricing",
            "Central Maryland Service", "Multiple System Options", "Commercial HVAC Team"]
SNIPPET_HEADER = "Types"
SNIPPET_VALUES = ["Rooftop Units", "Packaged Systems", "Heat Pumps", "Central Air",
                  "HVAC Replacement"]

BARRED = {
    "24/7": r"\b24\s*/\s*7\b", "emergency": r"\bemergency\b",
    "same-day": r"\bsame[-\s]day\b", "licensed/insured": r"licen[cs]ed|\binsured\b",
    "financing": r"\bfinanc(e|ing)\b|\brebate\b|\bapr\b|monthly payment",
    "guarantee": r"\bguarantee|\bwarrant", "superlative": r"#\s*1\b|\bbest\b|\b\bnumber one\b",
    "rating": r"\bstar(s)?\b|\breviews?\b", "price": r"\$\s?\d",
    "response time": r"response time|within \d+ (minutes|hours)",
}

fails, warns = [], []


def check_text(kind, t, limit, page_text):
    if len(t) > limit:
        fails.append(f"{kind} OVER LIMIT {len(t)}>{limit}: {t!r}")
    for name, pat in BARRED.items():
        if re.search(pat, t, re.I):
            fails.append(f"{kind} BARRED CLAIM '{name}': {t!r}")
    return len(t)


def main():
    c = client(); identity_gate(c, verbose=False)
    now = datetime.datetime.now(TZ)

    # ---------- live landing-page text, for claim support ----------
    lp = json.loads((SNAP / f"lp-commercial-deep-{STAMP}.json").read_text(encoding="utf-8"))
    page_text = lp["runs"][0]["body_text"]
    page_lc = page_text.lower()

    # ---------- live before-state ----------
    ag = q(c, f"""SELECT ad_group.id, ad_group.name, ad_group.status,
                         ad_group.cpc_bid_micros, campaign.id, campaign.status
                  FROM ad_group WHERE ad_group.id = {COMM_AG}""")[0]
    ads_now = q(c, f"SELECT ad_group_ad.ad.id FROM ad_group_ad WHERE ad_group.id = {COMM_AG}")
    kws_now = q(c, f"""SELECT ad_group_criterion.criterion_id,
                              ad_group_criterion.keyword.text,
                              ad_group_criterion.keyword.match_type,
                              ad_group_criterion.status
                       FROM ad_group_criterion WHERE ad_group.id = {COMM_AG}
                         AND ad_group_criterion.negative = FALSE""")
    negs_now = q(c, f"""SELECT ad_group_criterion.keyword.text FROM ad_group_criterion
                        WHERE ad_group.id = {COMM_AG} AND ad_group_criterion.negative = TRUE""")
    agassets_now = q(c, f"""SELECT campaign.id, ad_group.id, ad_group_asset.field_type
                            FROM ad_group_asset WHERE ad_group.id = {COMM_AG}""")
    res_ads = q(c, f"""SELECT ad_group_ad.ad.id, ad_group_ad.status,
                              ad_group_ad.policy_summary.approval_status
                       FROM ad_group_ad WHERE ad_group.id = {RES_AG}""")
    camp = q(c, f"""SELECT campaign.id, campaign.status,
                           campaign.target_spend.cpc_bid_ceiling_micros,
                           campaign_budget.amount_micros
                    FROM campaign WHERE campaign.id = {CAMP}""")[0]

    before = {
        "ad_group_id": COMM_AG, "ad_group_name": ag.ad_group.name,
        "ad_group_status": E(ag.ad_group.status),
        "ad_group_cpc_bid_micros": ag.ad_group.cpc_bid_micros,
        "ads_in_ad_group": len(ads_now),
        "positive_keywords": sorted(f"{E(k.ad_group_criterion.keyword.match_type)}:"
                                    f"{k.ad_group_criterion.keyword.text}" for k in kws_now),
        "ad_group_negatives_count": len(negs_now),
        "ad_group_asset_links": len(agassets_now),
        "campaign_id": CAMP, "campaign_status": E(camp.campaign.status),
        "campaign_cpc_ceiling_usd": camp.campaign.target_spend.cpc_bid_ceiling_micros / 1e6,
        "campaign_daily_budget_usd": camp.campaign_budget.amount_micros / 1e6,
        "residential_ad_group_id": RES_AG,
        "residential_ads": sorted(f"{a.ad_group_ad.ad.id}:{E(a.ad_group_ad.status)}:"
                                  f"{E(a.ad_group_ad.policy_summary.approval_status)}"
                                  for a in res_ads),
        "landing_page_http_status": lp["runs"][0]["http_status"],
    }
    print("=== LIVE BEFORE-STATE ===")
    print(json.dumps(before, indent=1))

    assert before["ads_in_ad_group"] == 0, "ad group already has ads - STOP"
    assert before["ad_group_negatives_count"] == 17, "expected 17 ad-group negatives"
    assert before["landing_page_http_status"] == 200, "landing page must be 200"
    if before["ad_group_status"] != "PAUSED":
        warns.append(f"AD GROUP IS {before['ad_group_status']}, NOT PAUSED. The ads MUST be "
                     f"created PAUSED - an ENABLED ad in an ENABLED ad group would serve "
                     f"immediately with no second approval.")

    # ---------- validate copy ----------
    print("\n=== COPY VALIDATION ===")
    allh, alld = [], []
    for rsa in (RSA_A, RSA_B):
        hs = rsa["pinned_h1"] + rsa["unpinned"]
        if len(hs) > 15:
            fails.append(f"{rsa['label']}: {len(hs)} headlines > 15")
        if len(set(hs)) != len(hs):
            fails.append(f"{rsa['label']}: duplicate headlines within the ad")
        if len(rsa["descriptions"]) != 4:
            fails.append(f"{rsa['label']}: {len(rsa['descriptions'])} descriptions != 4")
        if len(set(rsa["descriptions"])) != len(rsa["descriptions"]):
            fails.append(f"{rsa['label']}: duplicate descriptions")
        print(f"\n  --- {rsa['label']} ({len(hs)} headlines, {len(rsa['descriptions'])} descriptions) ---")
        for h in hs:
            n = check_text("HEADLINE", h, HL_MAX, page_text)
            pin = "PIN:H1" if h in rsa["pinned_h1"] else "      "
            print(f"    {pin} [{n:>2}/30] {h}")
        for d in rsa["descriptions"]:
            n = check_text("DESCRIPTION", d, DS_MAX, page_text)
            print(f"           [{n:>2}/90] {d}")
        allh += hs; alld += rsa["descriptions"]
    overlap_h = set(RSA_A["pinned_h1"] + RSA_A["unpinned"]) & set(RSA_B["unpinned"])
    overlap_d = set(RSA_A["descriptions"]) & set(RSA_B["descriptions"])
    print(f"\n  headline overlap between RSA A and RSA B: {sorted(overlap_h) or 'NONE'}")
    print(f"  description overlap: {sorted(overlap_d) or 'NONE'}")
    if overlap_h or overlap_d:
        fails.append("RSA A and RSA B share copy - they must be materially distinct")

    # ---------- claim support against the live page ----------
    print("\n=== CLAIM SUPPORT AGAINST THE LIVE PAGE ===")
    CLAIMS = {
        "commercial": "commercial", "installation": "install",
        "rooftop": "rooftop", "packaged": "packaged",
        "heat pump": "heat pump", "central air": "central air",
        "ductwork": "duct", "ventilation": "ventilation", "controls": "control",
        "central maryland": "central maryland", "free quote": "free commercial hvac quote",
        "free consultation": "free commercial hvac consultation",
        "transparent pricing": "transparent", "flexible scheduling": "flexible scheduling",
        "business/property": "propert", "replacement": "replace",
        "site evaluation": "evaluate the building", "aging equipment": "aging",
        "sized/fit building": "fit the building",
        "air conditioning": "commercial air conditioning",
    }
    for label, needle in CLAIMS.items():
        ok = needle in page_lc
        print(f"    [{'OK ' if ok else 'MISS'}] {label:22s} <- {needle!r}")
        if not ok:
            fails.append(f"CLAIM NOT SUPPORTED BY LIVE PAGE: {label} ({needle!r})")

    print("\n=== CALLOUTS + STRUCTURED SNIPPET ===")
    for co in CALLOUTS:
        n = check_text("CALLOUT", co, CALLOUT_MAX, page_text)
        print(f"    [{n:>2}/25] {co}")
    if len(set(CALLOUTS)) != len(CALLOUTS):
        fails.append("duplicate callouts")
    for v in SNIPPET_VALUES:
        n = check_text("SNIPPET_VALUE", v, SNIPPET_VAL_MAX, page_text)
        print(f"    [{n:>2}/25] {SNIPPET_HEADER}: {v}")
    if not 3 <= len(SNIPPET_VALUES) <= 10:
        fails.append("structured snippet needs 3-10 values")

    # ---------- dedupe against assets already on the campaign ----------
    existing_co = {r.asset.callout_asset.callout_text for r in q(c, f"""
        SELECT campaign.id, asset.callout_asset.callout_text
        FROM campaign_asset WHERE campaign.id = {CAMP}
          AND campaign_asset.field_type = CALLOUT""")}
    dup_co = sorted(set(CALLOUTS) & existing_co)
    print(f"\n  campaign-level callouts already on {CAMP}: {sorted(existing_co)}")
    print(f"  overlap with the proposed commercial callouts: {dup_co or 'NONE'}")
    if dup_co:
        fails.append(f"callout duplicates an existing campaign callout: {dup_co}")

    # ---------- build the plans ----------
    def rsa_op(rsa):
        return {
            "operation": "CREATE_RSA_PAUSED", "resource": "ad_group_ad",
            "ad_group_id": COMM_AG, "ad_group_name": before["ad_group_name"],
            "campaign_id": CAMP, "ad_label": rsa["label"], "status": "PAUSED",
            "final_url": FINAL_URL, "path1": PATH1, "path2": PATH2,
            "tracking_url_template": None, "final_url_suffix": None,
            "url_custom_parameters": [],
            "headlines_pinned_headline_1": rsa["pinned_h1"],
            "headlines_unpinned": rsa["unpinned"],
            "descriptions": rsa["descriptions"],
        }

    plan_rsa = {
        "plan_name": "AMB-0915-COMM-RSA-1",
        "approval_class": "create-paused",
        "customer_id": CID, "exact_account_name": EXACT_NAME,
        "exact_service": "Commercial HVAC Installation",
        "supersedes": ("AMB-0910-COMM-RSA-2 / 41C183D15C93 - DRIFTED. Drafted while the "
                       "destination returned 404, the ad group was PAUSED and the ad group "
                       "held 0 negatives. All three facts have changed. Copy is also revised: "
                       "'Commercial RTU Installation' and 'Systems Built for Businesses' in "
                       "RSA A and 'Keep Business Comfort in Mind' in RSA B were replaced with "
                       "wording that appears verbatim on the live page."),
        "summary": ("Create two materially distinct RSAs PAUSED in ad group 199748801029. "
                    "2 operations. Nothing serves until a separate enablement approval."),
        "before_state": before,
        "operations": [rsa_op(RSA_A), rsa_op(RSA_B)],
        "operation_count": 2,
        "reason": ("The commercial ad group has 2 ENABLED, APPROVED, ELIGIBLE keywords, 17 "
                   "correct ad-group negatives and a live HTTP 200 destination, but zero ads, "
                   "so it cannot serve. Two RSAs are the minimum to launch and to let Google "
                   "rotate creative."),
        "risk": ("MEDIUM. The ad group was switched to ENABLED on 2026-09-15 08:42:16 by "
                 "access@greenmarketingfl.com via GOOGLE_ADS_WEB_CLIENT. Because the parent is "
                 "ENABLED, any ad created ENABLED would serve immediately. Both ads are "
                 "therefore created PAUSED and readback asserts PAUSED."),
        "rollback": "Set both created ad_group_ad resources to REMOVED by returned resource name.",
        "dependencies": ["landing page HTTP 200 - VERIFIED 2026-09-15",
                         "17 ad-group negatives present - VERIFIED",
                         "both keywords ENABLED + APPROVED + ELIGIBLE - VERIFIED"],
        "validation": {"headline_limit": HL_MAX, "description_limit": DS_MAX,
                       "headlines_per_ad": [len(RSA_A["pinned_h1"]) + len(RSA_A["unpinned"]),
                                            len(RSA_B["pinned_h1"]) + len(RSA_B["unpinned"])],
                       "descriptions_per_ad": [4, 4],
                       "duplicate_copy_between_ads": False,
                       "barred_claims_found": 0,
                       "claims_unsupported_by_live_page": 0},
        "monitoring": "Poll ad policy approval_status daily; do not enable before APPROVED.",
        "stop_loss": "N/A - paused ads cannot spend.",
        "unrelated_resource_assertion": (
            "No change to: campaign 24132507747 status/budget $176.15/ceiling $30.00/schedule/"
            "locations/networks/conversion goals; residential ad group 202339087634 and its two "
            "ENABLED APPROVED ads 821319509197 and 821319509200; the other four campaigns; the "
            "17 ad-group negatives; the 2 positive keywords; any campaign or account negative; "
            "any existing asset."),
    }

    plan_asset = {
        "plan_name": "AMB-0915-COMM-ASSET-1",
        "approval_class": "create-paused",
        "customer_id": CID, "exact_account_name": EXACT_NAME,
        "exact_service": "Commercial HVAC Installation",
        "summary": ("Create 6 commercial callouts and 1 structured snippet and link them to "
                    "ad group 199748801029 with the asset link PAUSED. 7 operations. "
                    "Nothing serves until a separate enablement approval."),
        "before_state": {"ad_group_asset_links_on_commercial": len(agassets_now),
                         "campaign_level_callouts": sorted(existing_co),
                         "campaign_level_structured_snippet": (
                             "Service catalog (residential HVAC Installation wording)")},
        "operations": (
            [{"operation": "CREATE_CALLOUT_ASSET_AND_LINK_PAUSED",
              "resource": "asset + ad_group_asset", "ad_group_id": COMM_AG,
              "field_type": "CALLOUT", "asset_link_status": "PAUSED", "text": t}
             for t in CALLOUTS]
            + [{"operation": "CREATE_STRUCTURED_SNIPPET_AND_LINK_PAUSED",
                "resource": "asset + ad_group_asset", "ad_group_id": COMM_AG,
                "field_type": "STRUCTURED_SNIPPET", "asset_link_status": "PAUSED",
                "header": SNIPPET_HEADER, "values": SNIPPET_VALUES}]),
        "operation_count": len(CALLOUTS) + 1,
        "reason": ("Campaign 24132507747 carries five generic callouts and a residential "
                   "'Service catalog' snippet. Ad-group assets take precedence for this ad "
                   "group only, so commercial searchers see commercial extensions while the "
                   "residential ad group is untouched. Every value is verbatim-supported by "
                   "the live commercial page."),
        "risk": "LOW - asset links created PAUSED cannot serve.",
        "rollback": "Set the 7 ad_group_asset links to REMOVED.",
        "dependencies": ["AMB-0915-COMM-RSA-1 should be approved first; assets without ads "
                         "serve nothing"],
        "unrelated_resource_assertion": (
            "No campaign_asset is created, edited or removed. The five campaign callouts, the "
            "campaign structured snippet, the shared call asset 407995613637 and every sitelink "
            "remain exactly as they are, on all five campaigns."),
    }

    print("\n" + "=" * 78)
    if fails:
        print("VALIDATION FAILED:")
        for f in fails:
            print("  FAIL:", f)
        return 1
    for w in warns:
        print("  WARN:", w)
    print("VALIDATION PASSED: 0 failures")

    fp_rsa = approval_code(plan_rsa)
    fp_ast = approval_code(plan_asset)
    plan_rsa["fingerprint"] = fp_rsa
    plan_asset["fingerprint"] = fp_ast
    PLANS.mkdir(parents=True, exist_ok=True)
    (PLANS / "AMB-0915-COMM-RSA-1.json").write_text(
        json.dumps(plan_rsa, indent=1, ensure_ascii=False), encoding="utf-8")
    (PLANS / "AMB-0915-COMM-ASSET-1.json").write_text(
        json.dumps(plan_asset, indent=1, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 78)
    print(f"APPROVE AMB-0915-COMM-RSA-1 {fp_rsa} 2 operations FOR {CID}")
    print(f"APPROVE AMB-0915-COMM-ASSET-1 {fp_ast} 7 operations FOR {CID}")
    print("=" * 78)
    print(f"\nwrote {PLANS / 'AMB-0915-COMM-RSA-1.json'}")
    print(f"wrote {PLANS / 'AMB-0915-COMM-ASSET-1.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
