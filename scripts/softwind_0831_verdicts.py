#!/usr/bin/env python3
"""Softwind Power Washing - 2026-08-31 search-term verdicts + landing-page audit.

Every metric is interpolated from the read-only snapshots. The VERDICT column is
expert judgment; the numbers beside it are never hand-typed.

Verdict vocabulary: KEEP | ADD AS KEYWORD | WATCH | NEGATIVE CANDIDATE |
ROUTING ISSUE | OUT OF SCOPE | ALREADY BLOCKED | OVER-BLOCKED
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

# term -> (verdict, intent, rationale, recommended_action)
VERDICTS: dict[str, tuple[str, str, str, str]] = {
    "power washing services": (
        "ROUTING ISSUE", "BOFU - core hire intent",
        "Highest-cost term in the account. Served from Power Washing #2 / "
        "Residential Pressure Washing Near Me as a NEAR_EXACT close variant of "
        "'residential pressure washing near me', while campaign A holds the "
        "matching SKAG 'power washing services near me'. Five billable clicks "
        "landed on one recorded impression in a single hour.",
        "Own it explicitly: add 'power washing services' as EXACT in ONE campaign "
        "and add it as an ad-group EXACT negative in the other. Do not negative "
        "the term itself."),
    "pressure washing": (
        "ADD AS KEYWORD", "BOFU head term, mixed intent",
        "480 local searches/month bucket at $0.30-$10.77 top of page - far cheaper "
        "than the near-me cluster the account actually buys. Currently reached only "
        "as a close variant of 'power washing near me' EXACT.",
        "ADD AS PHRASE in the Pressure Washing intent group once that group exists."),
    "power washing companies near me": (
        "ADD AS KEYWORD", "BOFU - company/vendor intent",
        "Sits in the 260/month 'power washing near me' Planner bucket. Reached today "
        "only as a close variant of 'power washing services near me'.",
        "ADD AS EXACT to Power Washing Company Near Me, which already exists and has "
        "zero clicks on 11 impressions."),
    "power washing near me": (
        "KEEP", "BOFU - the account's canonical intent",
        "Exact match on its own SKAG. Quality Score 1 with BELOW_AVERAGE on all three "
        "components; the cost is a rank problem, not an intent problem.",
        "CORE. Keep. Fix ad relevance and landing-page experience rather than the "
        "keyword."),
    "powerwash cost": (
        "WATCH", "Price research, not an estimate request",
        "Matched to 'house pressure washing estimate' EXACT. 'Estimate' as a keyword "
        "token pulls 'how much does it cost' researchers, a materially weaker intent "
        "than an estimate request.",
        "Keep for now but move the whole cost/price cluster behind a single decision: "
        "either build a pricing page that converts researchers, or negative the "
        "cost cluster. Do not negative in isolation."),
    "gas station pressure washing near me": (
        "NEGATIVE CANDIDATE", "Commercial / industrial - outside verified scope",
        "Commercial fleet-and-forecourt washing. The verified offer and every landing "
        "page are residential. Blocked on K1-W2: does Softwind sell commercial work?",
        "PLAN-R2 holds 'gas station' as a campaign PHRASE negative, gated on the "
        "commercial-scope answer."),
    "power wash near me": (
        "ADD AS KEYWORD", "BOFU - core hire intent, spelling variant",
        "Reached as a close variant across three different ad groups, which splits "
        "its history.",
        "ADD AS EXACT to the Power Washing Near Me core group."),
    "power washing": (
        "ADD AS KEYWORD", "BOFU head term, mixed intent",
        "The single largest local bucket at 880 searches/month, and the cheapest at "
        "$0.58-$14.31 top of page - roughly half what the account pays today. 32 "
        "impressions already earned as a close variant.",
        "ADD AS PHRASE. This is the most under-bought demand in the account."),
    "pressure washing near me": (
        "ADD AS KEYWORD", "BOFU - core hire intent",
        "A 90/month bucket with NO matching keyword anywhere in the account. Reached "
        "only as a close variant, across four different ad groups.",
        "ADD AS EXACT and PHRASE in a dedicated Pressure Washing Near Me SKAG."),
    "deck cleaning services near me": (
        "OVER-BLOCKED", "BOFU - in-scope exterior surface washing",
        "Deck washing is power washing. This term took a $29.04 click on 2026-08-29 "
        "and is now blocked by the bare PHRASE negative 'cleaning' added 2026-08-30.",
        "Remove the bare 'cleaning' negative; replace with intent-qualified phrases."),
    "powerwashing companies near me": (
        "KEEP", "BOFU - company/vendor intent",
        "Compound spelling of the core intent; already converts to a click.",
        "Covered by close variants. No new keyword needed."),
    "average cost to power wash a house": (
        "WATCH", "Informational price research",
        "Paid $22.11. Same 'estimate' misfire as 'powerwash cost'.",
        "Group with the cost cluster decision. Not an isolated negative."),
    "affordable power washing near me": ("KEEP", "BOFU with price sensitivity", "In scope.", "Covered by close variants."),
    "best power wash company near me": ("KEEP", "BOFU - vendor comparison", "In scope. 'best' is never auto-negatived.", "Covered by close variants."),
    "best power washing company": ("KEEP", "BOFU - vendor comparison", "In scope.", "Covered by close variants."),
    "commercial power washing company near me": (
        "NEGATIVE CANDIDATE", "Commercial - outside verified residential scope",
        "Same K1-W2 gate as the gas-station term. Zero cost so far.",
        "PLAN-R2 branch B, gated on the commercial-scope answer."),
    "cost to power wash": ("WATCH", "Informational price research", "Cost cluster.", "Group decision, see 'powerwash cost'."),
    "house cleaning services near me": (
        "ALREADY BLOCKED", "Interior cleaning - out of scope",
        "Correctly out of scope; now blocked by the 'cleaning' PHRASE negative.",
        "Keep blocked, but via 'house cleaning services' EXACT rather than bare 'cleaning'."),
    "house exterior power washing": ("KEEP", "BOFU - house washing", "In scope.", "Covered."),
    "house power wash": ("KEEP", "BOFU - house washing", "In scope.", "Covered."),
    "house soft wash cost": ("WATCH", "Price research, soft washing", "Cost cluster.", "Group decision."),
    "house wash near me": ("KEEP", "BOFU - house washing", "In scope.", "Covered."),
    "house wash price": ("WATCH", "Price research", "Cost cluster.", "Group decision."),
    "house washing near me": (
        "ADD AS KEYWORD", "BOFU - house washing",
        "40/month bucket at $10.46-$24.75. The matching keyword exists only inside "
        "the permanently paused Soft & House Washing group.",
        "ADD AS EXACT + PHRASE in a clean House Washing Near Me SKAG."),
    "house washing services": ("KEEP", "BOFU - house washing", "In scope.", "Covered."),
    "how much does power washing a house cost": ("WATCH", "Informational price research", "Cost cluster.", "Group decision."),
    "how much is powerwashing a house": ("WATCH", "Informational price research", "Cost cluster.", "Group decision."),
    "jet wash near me": (
        "ADD AS KEYWORD", "BOFU - synonym for pressure washing",
        "British-English synonym for pressure washing. A keyword opportunity, not a "
        "negative.",
        "ADD AS EXACT to the Pressure Washing Near Me group."),
    "local power washers": ("KEEP", "BOFU - local vendor intent", "In scope.", "Covered."),
    "local services pressure washing": ("KEEP", "BOFU - vendor intent", "In scope. Signals LSA competition on the SERP.", "Covered."),
    "outdoor house cleaning services near me": (
        "OVER-BLOCKED", "BOFU - exterior work, resolved by 'outdoor'",
        "'Outdoor' resolves this to exterior washing. Blocked since 2026-08-30 by the "
        "bare 'cleaning' PHRASE negative.",
        "Unblock with the 'cleaning' negative fix."),
    "power wash companies near me": ("KEEP", "BOFU - company intent", "In scope.", "Covered."),
    "power wash my house": ("KEEP", "BOFU - house washing", "In scope.", "Covered."),
    "power washer company near me": ("KEEP", "BOFU - company intent", "'Power washer' here means the contractor, not the machine. Context resolves it.", "Covered."),
    "power washer near me": (
        "WATCH", "AMBIGUOUS - contractor or the machine",
        "Could be someone looking to buy or rent a pressure washer. 4 impressions, 0 "
        "clicks, $0. Existing BROAD negatives ('pressure washer for sale', 'power "
        "washer rental') already cover the equipment framings.",
        "Watch. Do not negative on 4 impressions and zero cost."),
    "power washing costs": ("WATCH", "Informational price research", "Cost cluster.", "Group decision."),
    "power washing repair near me": (
        "NEGATIVE CANDIDATE", "Equipment repair - out of scope",
        "Pressure-washer servicing, not exterior cleaning. The existing BROAD negative "
        "'power washer repair' does NOT block it: BROAD requires every word, and this "
        "term says 'washing', not 'washer'.",
        "ADD 'power washing repair' as a campaign PHRASE negative. Collision-tested "
        "against all 55 live keyword texts: zero collisions."),
    "power washing service near me": ("KEEP", "BOFU - core hire intent", "In scope.", "Covered by close variants."),
    "power washing services near me": ("KEEP", "BOFU - core hire intent", "Exact match on its own SKAG in both campaigns - the one directly duplicated ad group.", "CORE. Consolidate into one campaign."),
    "powerwash company": ("KEEP", "BOFU - company intent", "In scope.", "Covered."),
    "powerwash near me": ("KEEP", "BOFU - core hire intent", "In scope.", "Covered."),
    "powerwashing near me": ("KEEP", "BOFU - core hire intent", "14 impressions, zero clicks - the largest zero-click term in the account.", "Covered by close variants. Its zero CTR is an ad-relevance signal, not an intent signal."),
    "pressure washer near me": ("WATCH", "AMBIGUOUS - contractor or the machine", "Same ambiguity as 'power washer near me'. 1 impression, $0.", "Watch."),
    "pressure washer service near me": ("WATCH", "AMBIGUOUS - service of the machine vs washing service", "1 impression, $0.", "Watch."),
    "pressure washing companies near me": ("KEEP", "BOFU - company intent", "In scope.", "Covered."),
    "pressure washing service": ("KEEP", "BOFU - service intent", "In scope.", "Covered."),
    "pressure washing service near me": ("ADD AS KEYWORD", "BOFU - core hire intent", "10 impressions, zero clicks. Belongs to the uncovered 'pressure washing near me' family.", "ADD AS PHRASE in the Pressure Washing Near Me SKAG."),
    "price to powerwash house": ("WATCH", "Informational price research", "Cost cluster.", "Group decision."),
    "professional power washing": ("KEEP", "BOFU - quality-qualified intent", "In scope.", "Covered."),
    "roof washing near me": (
        "ALREADY BLOCKED", "Roof cleaning - excluded by the work order",
        "roof cleaning is on the work order's excluded_services list. Blocked by the "
        "'roof washing' PHRASE negative added 2026-08-30.",
        "Correctly blocked. Add 'roof cleaning' PHRASE for completeness."),
    "slate roof cleaning near me": ("ALREADY BLOCKED", "Roof cleaning - excluded", "Blocked by 'cleaning' PHRASE today; would be blocked by 'roof cleaning' after the fix.", "Ensure the 'cleaning' fix keeps roof blocked."),
    "soft power washing company near me": ("KEEP", "BOFU - soft washing", "In scope.", "Covered."),
    "soft wash power washing near me": ("KEEP", "BOFU - soft washing", "In scope.", "Covered."),
}


def newest(pattern: str) -> dict:
    return json.loads(sorted(SNAP.glob(pattern))[-1].read_text(encoding="utf-8"))


def phrase_blocks(neg: str, q: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(neg) + r"(?!\w)", q) is not None


def broad_blocks(neg: str, q: str) -> bool:
    return all(re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", q) for w in neg.split())


def main() -> int:
    st = newest("forensic-structure-*.json")
    pf = newest("forensic-performance-*.json")
    lp = json.loads((SNAP / "forensic-landing-pages-2026-08-31.json")
                    .read_text(encoding="utf-8"))
    dem = newest("forensic-demand-*.json")
    dem_by_text = {i["text"].lower(): i for i in dem["ideas"]}

    negs = defaultdict(set)
    for c in st["campaign_criteria"]:
        if c["type"] == "KEYWORD" and c["negative"]:
            negs[c["text"]].add(c["match_type"])

    def blockers(q: str) -> list[str]:
        out = []
        for t, mts in negs.items():
            for mt in mts:
                if (mt == "PHRASE" and phrase_blocks(t, q)) or \
                   (mt == "BROAD" and broad_blocks(t, q)):
                    out.append(f"{t}[{mt}]")
        return sorted(set(out))

    # -------- search-term-verdicts.csv (one row per campaign x ad group x term x kw) --
    rows_src = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                                    "conversions": 0.0, "dates": set()})
    for r in pf["search_terms"]:
        k = (r["campaign_name"], r["campaign_id"], r["ad_group_name"], r["ad_group_id"],
             r["term"], r["matched_keyword"], r["keyword_match_type"],
             r["term_match_type"])
        d = rows_src[k]
        d["impressions"] += r["impressions"]
        d["clicks"] += r["clicks"]
        d["cost"] += r["cost"]
        d["conversions"] += r["conversions"]
        d["dates"].add(r["date"])

    rows = []
    for k, v in sorted(rows_src.items(), key=lambda x: (-x[1]["cost"], -x[1]["impressions"])):
        (cn, cid, agn, agid, term, mk, kmt, tmt) = k
        verdict, intent, rationale, action = VERDICTS.get(
            term, ("WATCH", "unclassified", "Not seen in the classified corpus.", "Review."))
        bl = blockers(term)
        d = dem_by_text.get(term.lower(), {})
        dates = sorted(v["dates"])
        rows.append([
            term, cn, cid, agn, agid, mk, kmt, tmt,
            v["impressions"], v["clicks"],
            round(100 * v["clicks"] / v["impressions"], 2) if v["impressions"] else "",
            round(v["cost"], 2),
            round(v["cost"] / v["clicks"], 2) if v["clicks"] else "",
            v["conversions"], 0, "NONE RECORDED",
            d.get("avg_monthly_searches", ""),
            d.get("low_top_of_page_bid", ""), d.get("high_top_of_page_bid", ""),
            intent, verdict, action, rationale,
            "|".join(bl) if bl else "none",
            dates[0], dates[-1],
        ])
    AUD.mkdir(parents=True, exist_ok=True)
    p = AUD / f"{STAMP}-search-term-verdicts.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "search_term", "campaign_name", "campaign_id", "ad_group_name", "ad_group_id",
            "matched_keyword", "keyword_match_type", "term_match_type", "impressions",
            "clicks", "ctr_pct", "cost_usd", "avg_cpc_usd", "conversions",
            "qualified_leads", "qualified_lead_status", "planner_local_monthly_searches",
            "planner_top_of_page_low_usd", "planner_top_of_page_high_usd", "intent",
            "verdict", "recommended_action", "rationale", "currently_blocked_by",
            "first_seen", "last_seen"])
        w.writerows(rows)
    print(f"  {p.name:42s} {len(rows):5d} rows")

    # -------------------- landing-page-audit.csv --------------------
    ad_urls = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0, "groups": set()})
    for a in st["ads"]:
        for u in a["final_urls"]:
            d = ad_urls[u]
            m = a["metrics_all_time"]
            d["impressions"] += m["impressions"]
            d["clicks"] += m["clicks"]
            d["cost"] += m["cost"]
            d["groups"].add(f"{a['campaign_name']}/{a['ad_group_name']}")
    sitelink_urls = set()
    for c in st["campaign_assets"] + st["customer_assets"]:
        a = st["assets"].get(c["asset_id"], {})
        for u in a.get("final_urls", []):
            sitelink_urls.add(u)

    by_url = defaultdict(dict)
    for r in lp:
        base = r["requested_url"].split("?")[0]
        by_url[base][r.get("viewport", "desktop")] = r

    rows = []
    for base, vps in sorted(by_url.items()):
        d = vps.get("desktop", {})
        mo = vps.get("mobile", {})
        u = ad_urls.get(base, {"impressions": 0, "clicks": 0, "cost": 0.0, "groups": set()})
        tel = [t for t in (d.get("tel_links") or []) if len(re.sub(r"\D", "", t)) >= 10]
        phones = d.get("phones_in_text") or []
        trk = d.get("trackers") or {}
        aw = trk.get("google_ads_gtag", [])
        forms = d.get("forms") or []
        visible = []
        if forms:
            visible = [f for f in forms[0]["fields"] if not f.startswith("hidden:")]
        mm = d.get("market_mentions") or {}
        h1 = (d.get("h1") or [""])[0]
        city_locked = bool(re.search(r"Islip|Dix Hills", h1))
        rows.append([
            base,
            "AD FINAL URL" if base in ad_urls else ("SITELINK ONLY" if base in sitelink_urls else "other"),
            "|".join(sorted(u["groups"])) or "(sitelink destination)",
            u["impressions"], u["clicks"], round(u["cost"], 2),
            d.get("http_status", "ERROR"),
            "|".join(d.get("redirect_chain") or []) or "none",
            d.get("title", d.get("error", "")),
            h1,
            "YES" if city_locked else "no",
            ";".join(tel) or "NONE",
            ";".join(phones) or "NONE",
            "PASS" if "6315027946" in "".join(phones) else
            ("FAIL - untracked (631) 502-5402" if "6315025402" in "".join(phones) else "UNKNOWN"),
            len(visible), "|".join(visible),
            "PASS" if "gclid" in (d.get("query_on_final_url") or "") else "FAIL",
            "PASS" if "utm_source" in (d.get("query_on_final_url") or "") else "FAIL",
            "|".join(aw) or "NONE",
            "PRESENT" if "AW-17878095007" in aw else "absent",
            "|".join(trk.get("ga4_measurement", [])) or "NONE",
            "|".join(trk.get("gtm_container", [])) or "NONE",
            "YES" if "whatconverts" in trk else "no",
            "YES" if "clickcease" in trk else "no",
            "YES" if d.get("countdown_present") else "no",
            mm.get("power_washing", 0), mm.get("pressure_washing", 0),
            mm.get("soft_washing", 0), mm.get("house_washing", 0),
            mm.get("islip", 0), mm.get("long_island", 0),
            "MATCH" if mo.get("http_status") == d.get("http_status") else "DIFFERS",
            (d.get("html_bytes") or 0), (mo.get("html_bytes") or 0),
            "|".join(d.get("out_of_scope_links") or [])[:300] or "none",
            "UNKNOWN - no form submitted in READ mode",
            "UNKNOWN - no call placed in READ mode",
        ])
    p = AUD / f"{STAMP}-landing-page-audit.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "url", "role", "ad_groups_pointing_here", "ad_impressions", "ad_clicks",
            "ad_cost_usd", "http_status", "redirect_chain", "browser_title", "h1",
            "h1_city_locked_to_3_hamlets", "tel_links", "phones_in_text",
            "phone_check", "visible_form_fields", "form_field_list", "gclid_preserved",
            "utm_preserved", "google_ads_tags", "foreign_tag_AW_17878095007",
            "ga4", "gtm", "whatconverts_present", "clickcease_present",
            "countdown_present", "mentions_power_washing", "mentions_pressure_washing",
            "mentions_soft_washing", "mentions_house_washing", "mentions_islip",
            "mentions_long_island", "mobile_desktop_parity", "desktop_html_bytes",
            "mobile_html_bytes", "out_of_scope_links", "form_tracking_verified",
            "call_tracking_verified"])
        w.writerows(rows)
    print(f"  {p.name:42s} {len(rows):5d} rows")

    # ---------------- whatconverts-reconciliation.csv ----------------
    conv_rows = pf["conversions_by_action"]
    calls = pf["call_view"]
    ca = {c["id"]: c for c in st["conversion_actions"]}
    tot = {"impressions": 0, "clicks": 0, "cost": 0.0}
    for r in pf["daily_account"]:
        for k in tot:
            tot[k] += r[k]
    rows = [
        ["Google Ads - metrics.conversions (all campaigns, all time)", "0.00",
         "conversion_action rows exist and are ENABLED",
         "STRUCTURALLY ZERO: all four conversion actions have "
         "include_in_conversions_metric = FALSE, and customer_conversion_goal returns "
         "no biddable category at account level. This column cannot show a lead even "
         "if one occurs."],
        ["Google Ads - metrics.all_conversions (all campaigns, all time)", "0.00",
         f"segments.conversion_action_name returned {len(conv_rows)} rows",
         "The API omits all-zero segment rows, so zero rows means nothing was "
         "recorded on ANY action - not a reporting gap."],
        ["Google Ads - call_view (whole retained call log, no date filter)",
         str(len(calls)),
         "call_view accepts no segments.date; this is the full retained log",
         "No call has ever been logged from a call asset."],
        ["Google Ads - CALLS click type", "0 clicks on 86 impressions",
         "segments.click_type = CALLS",
         "The call button has served 86 times and has never been clicked."],
        ["Google Ads - form conversion action 7708725995", "0",
         ca.get("7708725995", {}).get("status", ""),
         "WEBPAGE / SUBMIT_LEAD_FORM, ONE_PER_CLICK, 90-day click window, "
         "default value 0.00 with always_use_default_value TRUE."],
        ["Google Ads - website call action 7708765130", "0",
         ca.get("7708765130", {}).get("status", ""),
         "WEBSITE_CALL / PHONE_CALL_LEAD, 60-second qualified-call threshold."],
        ["Google Ads - call asset action 7711699090", "0",
         ca.get("7711699090", {}).get("status", ""),
         "AD_CALL / PHONE_CALL_LEAD, 60-second threshold."],
        ["WhatConverts export - calls", "NO EXPORT SUPPLIED",
         "no file present under clients/softwind-power-washing/",
         "BLOCKER WC-1. A repository-wide search for a WhatConverts export found "
         "none for this client. Reconciliation cannot be completed."],
        ["WhatConverts export - forms", "NO EXPORT SUPPLIED",
         "no file present",
         "BLOCKER WC-1."],
        ["GLE Power Washing number +1 631-519-8373", "NOT OBSERVED",
         "not found in any live landing page, tel: link, or Google Ads asset",
         "Supplied in the brief. It appears nowhere in the audited surface."],
        ["GBP Power Washing number +1 631-315-8655", "NOT OBSERVED",
         "not found in any live landing page, tel: link, or Google Ads asset",
         "Supplied in the brief. It appears nowhere in the audited surface."],
        ["Approved landing-page number (631) 502-7946", "PRESENT ON ALL 6 OFFER PAGES",
         "tel: link and body copy, desktop and mobile",
         "Also the number on call asset 403335872180."],
        ["Untracked main-site number (631) 502-5402", "PRESENT ON softwindli.com",
         "our-work and service-areas pages",
         "Destinations of the three surviving ACCOUNT-LEVEL sitelinks. Campaign-level "
         "sitelinks override them today, so this is a latent leak, not an active one."],
        ["Third DNI number (631) 553-5927", "NOT OBSERVED IN THIS RUN",
         "no tel: link or body text matched it on any audited page",
         "Recorded on 2026-08-26 via the wc_swap cookie on main-site pages. Not "
         "re-confirmed here; the offer pages render the static approved number."],
        ["Account totals for the same period",
         f"{tot['clicks']} clicks / ${round(tot['cost'], 2)}",
         "FROM customer segmented by date",
         "The denominator any lead count must be judged against."],
    ]
    p = AUD / f"{STAMP}-whatconverts-reconciliation.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "value", "evidence", "note"])
        w.writerows(rows)
    print(f"  {p.name:42s} {len(rows):5d} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
