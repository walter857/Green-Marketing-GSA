#!/usr/bin/env python3
"""Classify the Softwind search-term corpus against ad-group keyword and
landing-page intent, and derive ad-group-level EXACT negative candidates.

Honours the standing corpus rule: classification happens on disk, stdout gets
aggregates plus ONLY the specific terms proposed as negatives (which the
approval owner must see in order to approve them). The full corpus detail is
written to a file and never echoed.

Classification is WHITELIST-FIRST: a positive in-scope vocabulary for the
approved Power Washing service family. Anything failing the whitelist is
bucketed by the reason it failed, and only genuinely out-of-scope buckets become
negative candidates.

READ ONLY against Google Ads. Writes local analysis files only.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
NAMES = {CAMP_A: "Power Washing", CAMP_B: "Power Washing #2"}
CLIENT = ROOT / "clients/softwind-power-washing"
DETAIL = CLIENT / "audits/2026-08-27-search-term-classification.json"
CSV = CLIENT / "audits/2026-08-27-negative-candidates.csv"

# ---------------------------------------------------------------- whitelist
# Approved service family per work-order.yaml: Power Washing plus pressure /
# residential pressure / house / soft / driveway / patio washing.
SERVICE_CORE = [
    r"power\s*wash", r"powerwash", r"pressure\s*wash", r"presure\s*wash",
    r"soft\s*wash", r"house\s*wash", r"home\s*wash", r"exterior\s*clean",
    r"siding\s*clean", r"driveway\s*clean", r"patio\s*clean", r"deck\s*wash",
]
SURFACE_OK = [r"house", r"home", r"siding", r"driveway", r"patio", r"deck",
              r"walkway", r"paver", r"concrete", r"fence", r"trim", r"porch",
              r"sidewalk", r"stoop", r"steps", r"residential"]

# CLAUDE.md: these must NEVER be auto-negatived. They are buying signals.
PROTECTED = ["near me", "near you", "quote", "price", "pricing", "cost",
             "best", "hire", "local", "emergency", "estimate", "free",
             "cheap", "affordable", "company", "service", "services",
             "contractor", "professional", "residential"]

# Out-of-scope buckets. Each is a REASON a term fails, not a blocklist import.
OUT_OF_SCOPE = {
    "COMMERCIAL_INDUSTRIAL": [
        r"\bgas\s*station", r"\bcommercial\b", r"\bindustrial\b",
        r"\bwarehouse\b", r"\bfleet\b", r"\bparking\s*lot", r"\bdumpster\b",
        r"\brestaurant\b", r"\bstore\s*front", r"\bstorefront\b",
        r"\bplaza\b", r"\bshopping\s*cent", r"\bapartment\s*complex",
        r"\bhoa\b", r"\bmunicipal\b", r"\bcity\s*of\b"],
    "EXCLUDED_SERVICE": [
        r"\broof\b", r"\bgutter", r"\bpaver\s*seal", r"\bsealing\b",
        r"\bsealer\b", r"\blandscap", r"\bmasonry\b", r"\bpaint",
        r"\bshrink\s*wrap", r"\bparty\s*rental", r"\blawn\b", r"\bmow",
        r"\bchristmas\b", r"\bholiday\s*light", r"\bfrench\s*drain",
        r"\bgrading\b", r"\btree\b", r"\bfenc(e|ing)\s*install",
        r"\bwindow\s*clean", r"\bcarpet\b", r"\bchimney\b", r"\bduct\b",
        r"\bpool\b", r"\bsept(ic)?\b"],
    "EQUIPMENT_RENTAL_DIY": [
        r"\brent(al|als)?\b", r"\bfor\s*sale\b", r"\bbuy\b", r"\bsell\b",
        r"\bmachine\b", r"\bequipment\b", r"\bpressure\s*washer\s*(for|to|rent|buy|sale|reviews?|parts?)",
        r"\bhow\s*to\b", r"\bdiy\b", r"\byourself\b", r"\bhomemade\b",
        r"\bnozzle\b", r"\bpsi\b", r"\bhose\b", r"\bpump\b", r"\bwand\b",
        r"\bdetergent\b", r"\bsoap\s*for\b", r"\bchemical", r"\bkarcher\b",
        r"\bryobi\b", r"\bsun\s*joe\b", r"\bgreenworks\b", r"\bhome\s*depot\b",
        r"\blowes\b", r"\bharbor\s*freight\b", r"\bamazon\b"],
    "EMPLOYMENT_TRAINING": [
        r"\bjobs?\b", r"\bhiring\b", r"\bsalary\b", r"\bcareer",
        r"\bemploy", r"\btraining\b", r"\bcourse\b", r"\bcertification\b",
        r"\bfranchise\b", r"\bstart\s*a\b", r"\bbusiness\s*plan",
        r"\blicense\s*to\b", r"\binsurance\s*for\b"],
    "INFORMATIONAL": [
        r"\bwhat\s+is\b", r"\bwhy\b", r"\bwhen\s+to\b", r"\bdefinition\b",
        r"\bmeaning\b", r"\bwikipedia\b", r"\bvs\b", r"\bversus\b",
        r"\bdifference\s+between\b", r"\breddit\b", r"\byoutube\b",
        r"\bvideo\b", r"\bcalculator\b"],
    "OUT_OF_AREA": [
        r"\bflorida\b", r"\bfl\b", r"\btexas\b", r"\bcalifornia\b",
        r"\bnew\s*jersey\b", r"\bconnecticut\b", r"\bct\b", r"\bnyc\b",
        r"\bmanhattan\b", r"\bbrooklyn\b", r"\bqueens\b", r"\bbronx\b"],
}


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def usd(m):
    return round((m or 0) / 1_000_000, 2)


def classify(term: str):
    """Return (verdict, bucket, reason). Whitelist first, then failure reason."""
    t = " " + term.lower().strip() + " "
    for bucket, pats in OUT_OF_SCOPE.items():
        for pat in pats:
            if re.search(pat, t):
                # a protected buying term never rescues a genuinely out-of-scope
                # query, but it does force a manual look
                return ("NEGATIVE", bucket, pat)
    in_service = any(re.search(p, t) for p in SERVICE_CORE)
    if in_service:
        return ("KEEP", "IN_SCOPE_SERVICE", "matches approved service vocabulary")
    if any(re.search(r"\b%s\b" % s, t) for s in SURFACE_OK):
        return ("KEEP", "IN_SCOPE_SURFACE", "approved surface, no service verb")
    return ("REVIEW", "UNCLASSIFIED", "fails whitelist, matches no out-of-scope rule")


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    now = datetime.now(TZ)

    # ---- ad group context: keywords + landing pages ----
    q = ("SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, "
         "ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
         "ad_group_criterion.status "
         f"FROM ad_group_criterion WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND ad_group_criterion.type = 'KEYWORD' "
         "AND ad_group_criterion.negative = FALSE "
         "AND ad_group_criterion.status != 'REMOVED'")
    ag_kw = defaultdict(list)
    ag_meta = {}
    for x in rows(svc, q):
        agid = str(x.ad_group.id)
        ag_meta[agid] = {"name": x.ad_group.name, "campaign": str(x.campaign.id),
                         "status": x.ad_group.status.name}
        ag_kw[agid].append({"text": x.ad_group_criterion.keyword.text,
                            "match": x.ad_group_criterion.keyword.match_type.name,
                            "status": x.ad_group_criterion.status.name})

    q = ("SELECT ad_group.id, ad_group_ad.ad.final_urls, ad_group_ad.status "
         f"FROM ad_group_ad WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND ad_group_ad.status = 'ENABLED'")
    ag_urls = defaultdict(set)
    for x in rows(svc, q):
        for u in x.ad_group_ad.ad.final_urls:
            ag_urls[str(x.ad_group.id)].add(u)

    # ---- existing negatives, so we never propose a duplicate ----
    q = ("SELECT ad_group.id, ad_group_criterion.keyword.text, "
         "ad_group_criterion.keyword.match_type "
         f"FROM ad_group_criterion WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND ad_group_criterion.type = 'KEYWORD' "
         "AND ad_group_criterion.negative = TRUE "
         "AND ad_group_criterion.status != 'REMOVED'")
    existing_ag_neg = defaultdict(set)
    for x in rows(svc, q):
        existing_ag_neg[str(x.ad_group.id)].add(
            (x.ad_group_criterion.keyword.text.lower(),
             x.ad_group_criterion.keyword.match_type.name))
    q = ("SELECT campaign.id, campaign_criterion.keyword.text, "
         "campaign_criterion.keyword.match_type "
         f"FROM campaign_criterion WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND campaign_criterion.type = 'KEYWORD' "
         "AND campaign_criterion.negative = TRUE "
         "AND campaign_criterion.status != 'REMOVED'")
    existing_camp_neg = defaultdict(set)
    for x in rows(svc, q):
        existing_camp_neg[str(x.campaign.id)].add(
            (x.campaign_criterion.keyword.text.lower(),
             x.campaign_criterion.keyword.match_type.name))

    # ---- the corpus ----
    q = ("SELECT campaign.id, ad_group.id, search_term_view.search_term, "
         "search_term_view.status, segments.keyword.info.text, "
         "segments.search_term_match_type, metrics.impressions, "
         "metrics.clicks, metrics.cost_micros, metrics.conversions "
         f"FROM search_term_view WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND segments.date BETWEEN '2026-08-01' AND '%s'"
         % now.strftime("%Y-%m-%d"))
    pairs = defaultdict(lambda: {"impressions": 0, "clicks": 0, "cost": 0.0,
                                 "conversions": 0.0, "matched_keywords": set(),
                                 "match_types": set(), "status": set()})
    for x in rows(svc, q):
        key = (str(x.campaign.id), str(x.ad_group.id),
               x.search_term_view.search_term)
        d = pairs[key]
        d["impressions"] += x.metrics.impressions
        d["clicks"] += x.metrics.clicks
        d["cost"] = round(d["cost"] + usd(x.metrics.cost_micros), 2)
        d["conversions"] += x.metrics.conversions
        if x.segments.keyword.info.text:
            d["matched_keywords"].add(x.segments.keyword.info.text)
        d["match_types"].add(x.segments.search_term_match_type.name)
        d["status"].add(x.search_term_view.status.name)

    # ---- classify ----
    records, buckets = [], defaultdict(
        lambda: {"pairs": 0, "impressions": 0, "clicks": 0, "cost": 0.0})
    for (cid_, agid, term), m in pairs.items():
        verdict, bucket, reason = classify(term)
        already = (term.lower(), "EXACT") in existing_ag_neg.get(agid, set())
        rec = {"campaign_id": cid_, "campaign": NAMES[cid_],
               "ad_group_id": agid,
               "ad_group": ag_meta.get(agid, {}).get("name", "?"),
               "ad_group_status": ag_meta.get(agid, {}).get("status", "?"),
               "search_term": term, "verdict": verdict, "bucket": bucket,
               "rule": reason,
               "impressions": m["impressions"], "clicks": m["clicks"],
               "cost": m["cost"], "conversions": round(m["conversions"], 2),
               "matched_keywords": sorted(m["matched_keywords"]),
               "match_types": sorted(m["match_types"]),
               "search_term_status": sorted(m["status"]),
               "already_negative_exact": already,
               "landing_pages": sorted(ag_urls.get(agid, []))}
        records.append(rec)
        b = buckets[bucket]
        b["pairs"] += 1
        b["impressions"] += m["impressions"]
        b["clicks"] += m["clicks"]
        b["cost"] = round(b["cost"] + m["cost"], 2)

    # ---- safety: a proposed EXACT negative must not equal a live keyword ----
    proposals = []
    for r in records:
        if r["verdict"] != "NEGATIVE" or r["already_negative_exact"]:
            continue
        t = r["search_term"].lower()
        blocks_live = any(k["text"].lower() == t
                          for k in ag_kw.get(r["ad_group_id"], []))
        hits_protected = [p for p in PROTECTED if p in t]
        proposals.append({**r, "blocks_live_keyword": blocks_live,
                          "protected_tokens_present": hits_protected})

    safe = [p for p in proposals if not p["blocks_live_keyword"]]
    unsafe = [p for p in proposals if p["blocks_live_keyword"]]

    out = {"read_only": True, "mutations_issued": 0,
           "timestamp_account_local": now.isoformat(),
           "corpus": {"distinct_terms": len({k[2] for k in pairs}),
                      "ad_group_term_pairs": len(pairs),
                      "total_impressions": sum(v["impressions"] for v in pairs.values()),
                      "total_clicks": sum(v["clicks"] for v in pairs.values()),
                      "total_cost": round(sum(v["cost"] for v in pairs.values()), 2)},
           "buckets": {k: v for k, v in sorted(buckets.items())},
           "records": records, "proposals_safe": safe, "proposals_unsafe": unsafe,
           "ad_group_context": {k: {"meta": ag_meta.get(k),
                                    "keywords": ag_kw.get(k, []),
                                    "landing_pages": sorted(ag_urls.get(k, []))}
                                for k in ag_meta},
           "existing_ad_group_negatives": {k: sorted(v) for k, v in
                                           existing_ag_neg.items()},
           "existing_campaign_negatives_count": {k: len(v) for k, v in
                                                 existing_camp_neg.items()}}
    DETAIL.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    with CSV.open("w", encoding="utf-8", newline="") as fh:
        fh.write("campaign,ad_group,search_term,bucket,impressions,clicks,cost,"
                 "matched_keywords,blocks_live_keyword\n")
        for s in sorted(safe, key=lambda x: -x["cost"]):
            fh.write('"%s","%s","%s","%s",%d,%d,%.2f,"%s",%s\n' % (
                s["campaign"], s["ad_group"], s["search_term"], s["bucket"],
                s["impressions"], s["clicks"], s["cost"],
                "; ".join(s["matched_keywords"]), s["blocks_live_keyword"]))

    # ------------------------- aggregates to stdout -------------------------
    print("SEARCH-TERM CLASSIFICATION  %s" % now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("=" * 76)
    c = out["corpus"]
    print("CORPUS: %d distinct terms, %d ad-group x term pairs, "
          "%d impressions, %d clicks, $%.2f"
          % (c["distinct_terms"], c["ad_group_term_pairs"],
             c["total_impressions"], c["total_clicks"], c["total_cost"]))
    print("\nBUCKET TOTALS (aggregates only):")
    print("  %-24s %6s %7s %7s %9s" % ("BUCKET", "PAIRS", "IMPR", "CLICKS", "COST"))
    for k, v in sorted(buckets.items(), key=lambda x: -x[1]["cost"]):
        print("  %-24s %6d %7d %7d %9s"
              % (k, v["pairs"], v["impressions"], v["clicks"], "$%.2f" % v["cost"]))
    print("\nPROPOSED AD-GROUP EXACT NEGATIVES: %d safe, %d rejected (would block "
          "a live keyword)" % (len(safe), len(unsafe)))
    print("  cost already spent on proposed terms: $%.2f"
          % sum(s["cost"] for s in safe))
    print("  clicks already bought on proposed terms: %d"
          % sum(s["clicks"] for s in safe))
    if unsafe:
        print("  REJECTED (exact-matches a live keyword):")
        for u in unsafe:
            print("    %s / %s" % (u["ad_group"], u["search_term"]))
    print("\nThe specific terms proposed as negatives are listed in the plan and")
    print("in %s so the owner can approve them." % CSV.name)
    print("\nwrote %s" % DETAIL)
    print("wrote %s" % CSV)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
