#!/usr/bin/env python3
"""PLAN-R3A control-integrity check: is campaign B a valid independent control?

Only one ad from an account enters a given auction. When two campaigns both hold
an eligible keyword for the same query, Google picks one - and Ad Rank (bid x
Quality Score) is a major input. So capping campaign A at $12 while campaign B
stays at $30 could shift shared query space from A to B, which would confound
any read of A's post-change decline.

This script measures how much of the account's query space is actually shared.
SELECT statements only. Constructs no operation, calls no mutate service.
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

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
A, B = "24103511039", "24145053510"
LO, HI = "2026-07-01", "2026-08-31"


def mic(v):
    return round(int(v) / 1_000_000, 4)


def phrase_matches(kw: str, term: str) -> bool:
    """Conservative phrase-match test: the keyword words appear in order, contiguous."""
    return re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", term) is not None


def token_overlap(kw: str, term: str) -> float:
    a, b = set(kw.split()), set(term.split())
    return len(a & b) / len(a) if a else 0.0


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    now = datetime.now(ZoneInfo("America/New_York"))

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    # ---------- serving keyword inventory per campaign ----------
    serving = defaultdict(list)      # campaign_id -> [(text, match_type, ad_group)]
    ag_status = {}
    for r in q("""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status,
                         ad_group_criterion.keyword.text,
                         ad_group_criterion.keyword.match_type,
                         ad_group_criterion.status
                  FROM keyword_view"""):
        ag_status[str(r.ad_group.id)] = enum_name(r.ad_group.status)
        if (enum_name(r.ad_group.status) == "ENABLED"
                and enum_name(r.ad_group_criterion.status) == "ENABLED"):
            serving[str(r.campaign.id)].append((
                r.ad_group_criterion.keyword.text,
                enum_name(r.ad_group_criterion.keyword.match_type),
                r.ad_group.name, str(r.ad_group.id)))

    # ---------- landing pages per campaign ----------
    lps = defaultdict(set)
    ag_lp = {}
    for r in q("""SELECT campaign.id, ad_group.id, ad_group_ad.ad.final_urls
                  FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'"""):
        for u in r.ad_group_ad.ad.final_urls:
            lps[str(r.campaign.id)].add(u)
            ag_lp[str(r.ad_group.id)] = u

    # ---------- observed search terms ----------
    terms = defaultdict(lambda: defaultdict(lambda: {
        "impr": 0, "clicks": 0, "cost": 0.0, "ad_group": "", "ad_group_id": "",
        "keyword": "", "kw_match": "", "term_match": ""}))
    for r in q(f"""SELECT campaign.id, campaign.name, ad_group.id, ad_group.name,
                          search_term_view.search_term,
                          segments.keyword.info.text, segments.keyword.info.match_type,
                          segments.search_term_match_type,
                          metrics.impressions, metrics.clicks, metrics.cost_micros
                   FROM search_term_view
                   WHERE segments.date BETWEEN '{LO}' AND '{HI}'"""):
        t = r.search_term_view.search_term
        c = str(r.campaign.id)
        d = terms[t][c]
        d["impr"] += int(r.metrics.impressions)
        d["clicks"] += int(r.metrics.clicks)
        d["cost"] += mic(r.metrics.cost_micros)
        d["ad_group"] = r.ad_group.name
        d["ad_group_id"] = str(r.ad_group.id)
        d["keyword"] = r.segments.keyword.info.text
        d["kw_match"] = enum_name(r.segments.keyword.info.match_type)
        d["term_match"] = enum_name(r.segments.search_term_match_type)

    # ---------- eligibility test ----------
    def eligible(campaign_id, term):
        """Return (verdict, evidence). PROVEN if it actually served there."""
        if campaign_id in terms[term] and terms[term][campaign_id]["impr"] >= 0 and \
                terms[term][campaign_id]["keyword"]:
            return "PROVEN", f"served via '{terms[term][campaign_id]['keyword']}'"
        best, why = None, ""
        for kw, mt, agn, agid in serving.get(campaign_id, []):
            if kw == term:
                return "PROVEN-EXACT-KEYWORD", f"exact keyword '{kw}' [{mt}] in {agn}"
            if mt == "PHRASE" and phrase_matches(kw, term):
                return "LIKELY", f"phrase keyword '{kw}' contained in term ({agn})"
            ov = token_overlap(kw, term)
            if ov >= 0.8 and (best is None or ov > best):
                best, why = ov, f"close-variant candidate '{kw}' [{mt}] in {agn} (token overlap {ov:.0%})"
        if best:
            return "PLAUSIBLE", why
        return "NO", "no serving keyword in this campaign plausibly matches"

    rows = []
    for t, bycamp in terms.items():
        matched = [c for c in bycamp]
        ea, wa = eligible(A, t)
        eb, wb = eligible(B, t)
        both_served = A in bycamp and B in bycamp
        if both_served:
            klass = "BOTH CAMPAIGNS ELIGIBLE"
        elif ea in ("PROVEN", "PROVEN-EXACT-KEYWORD", "LIKELY") and \
                eb in ("PROVEN", "PROVEN-EXACT-KEYWORD", "LIKELY"):
            klass = "BOTH CAMPAIGNS ELIGIBLE"
        elif ea == "NO" and eb in ("PROVEN", "PROVEN-EXACT-KEYWORD", "LIKELY"):
            klass = "CAMPAIGN B ONLY"
        elif eb == "NO" and ea in ("PROVEN", "PROVEN-EXACT-KEYWORD", "LIKELY"):
            klass = "CAMPAIGN A ONLY"
        elif "PLAUSIBLE" in (ea, eb):
            klass = "INCONCLUSIVE"
        else:
            klass = "INCONCLUSIVE"
        impr = sum(v["impr"] for v in bycamp.values())
        clk = sum(v["clicks"] for v in bycamp.values())
        cost = round(sum(v["cost"] for v in bycamp.values()), 2)
        agids = {v["ad_group_id"] for v in bycamp.values()}
        lp = {ag_lp.get(g, "") for g in agids}
        rows.append({
            "search_term": t,
            "matched_campaigns": [("A" if c == A else "B") for c in matched],
            "matched_ad_groups": sorted({v["ad_group"] for v in bycamp.values()}),
            "matched_keywords": sorted({v["keyword"] for v in bycamp.values() if v["keyword"]}),
            "match_types": sorted({v["kw_match"] for v in bycamp.values() if v["kw_match"]}),
            "term_match_types": sorted({v["term_match"] for v in bycamp.values() if v["term_match"]}),
            "campaign_A_eligible": ea, "campaign_A_evidence": wa,
            "campaign_B_eligible": eb, "campaign_B_evidence": wb,
            "campaign_A_ceiling_usd": 30.00, "campaign_B_ceiling_usd": 30.00,
            "landing_pages": sorted(x for x in lp if x),
            "served_in_both": both_served,
            "classification": klass,
            "could_shift_A_to_B_after_cap": klass == "BOTH CAMPAIGNS ELIGIBLE",
            "impressions": impr, "clicks": clk, "cost_usd": cost,
        })
    rows.sort(key=lambda r: (-r["cost_usd"], -r["impressions"]))

    # ---------- overlap totals ----------
    tot_i = sum(r["impressions"] for r in rows)
    tot_c = sum(r["clicks"] for r in rows)
    tot_k = sum(r["cost_usd"] for r in rows)
    ov = [r for r in rows if r["classification"] == "BOTH CAMPAIGNS ELIGIBLE"]
    ov_i = sum(r["impressions"] for r in ov)
    ov_c = sum(r["clicks"] for r in ov)
    ov_k = sum(r["cost_usd"] for r in ov)

    # keyword-text overlap between the serving sets
    sa = {(k, m) for k, m, _, _ in serving.get(A, [])}
    sb = {(k, m) for k, m, _, _ in serving.get(B, [])}
    ta = {k for k, _ in sa}
    tb = {k for k, _ in sb}

    out = {
        "generated_account_local": now.isoformat(),
        "mode": "READ-ONLY",
        "campaign_A": A, "campaign_B": B,
        "serving_keyword_rows": {"A": len(serving.get(A, [])), "B": len(serving.get(B, []))},
        "serving_keyword_texts": {"A": sorted(ta), "B": sorted(tb)},
        "serving_text_intersection": sorted(ta & tb),
        "serving_text_A_only": sorted(ta - tb),
        "serving_text_B_only": sorted(tb - ta),
        "landing_pages": {"A": sorted(lps.get(A, [])), "B": sorted(lps.get(B, []))},
        "landing_page_intersection": sorted(set(lps.get(A, [])) & set(lps.get(B, []))),
        "totals": {
            "distinct_terms": len(rows), "impressions": tot_i, "clicks": tot_c,
            "cost_usd": round(tot_k, 2)},
        "overlap": {
            "terms": len(ov),
            "impressions": ov_i, "clicks": ov_c, "cost_usd": round(ov_k, 2),
            "impressions_pct": round(100 * ov_i / tot_i, 1) if tot_i else 0,
            "clicks_pct": round(100 * ov_c / tot_c, 1) if tot_c else 0,
            "cost_pct": round(100 * ov_k / tot_k, 1) if tot_k else 0},
        "classification_counts": {
            k: sum(1 for r in rows if r["classification"] == k)
            for k in ("BOTH CAMPAIGNS ELIGIBLE", "CAMPAIGN A ONLY",
                      "CAMPAIGN B ONLY", "INCONCLUSIVE")},
        "terms": rows,
    }
    p = SNAP / f"control-integrity-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("=== SERVING KEYWORD INVENTORY ===")
    print(f"  campaign A serving keyword rows: {len(serving.get(A, []))}  "
          f"distinct texts: {len(ta)}")
    print(f"  campaign B serving keyword rows: {len(serving.get(B, []))}  "
          f"distinct texts: {len(tb)}")
    print(f"  texts serving in BOTH: {len(ta & tb)} -> {sorted(ta & tb)}")
    print(f"  A only: {sorted(ta - tb)}")
    print(f"  B only: {sorted(tb - ta)}")

    print("\n=== LANDING PAGES ===")
    print(f"  A: {len(lps.get(A, []))}   B: {len(lps.get(B, []))}   "
          f"shared: {len(set(lps.get(A, [])) & set(lps.get(B, [])))}")
    for u in sorted(set(lps.get(A, [])) & set(lps.get(B, []))):
        print(f"    SHARED  {u}")

    print(f"\n=== OVERLAP TOTALS (n={len(rows)} distinct terms) ===")
    o = out["overlap"]
    print(f"  terms in overlapping query space: {o['terms']} of {len(rows)}")
    print(f"  impressions in overlap: {o['impressions']} of {tot_i} = {o['impressions_pct']}%")
    print(f"  valid clicks in overlap: {o['clicks']} of {tot_c} = {o['clicks_pct']}%")
    print(f"  spend in overlap: ${o['cost_usd']} of ${round(tot_k,2)} = {o['cost_pct']}%")
    print(f"  classification counts: {out['classification_counts']}")

    print("\n=== TERM-BY-TERM ===")
    print(f"{'search term':44s} {'srvd':5s} {'A elig':10s} {'B elig':10s} "
          f"{'class':24s} {'shift?':6s} impr clk    cost")
    for r in rows:
        print(f"{r['search_term'][:44]:44s} {'/'.join(r['matched_campaigns']):5s} "
              f"{r['campaign_A_eligible'][:10]:10s} {r['campaign_B_eligible'][:10]:10s} "
              f"{r['classification'][:24]:24s} "
              f"{'YES' if r['could_shift_A_to_B_after_cap'] else 'no':6s} "
              f"{r['impressions']:4d} {r['clicks']:3d} {r['cost_usd']:7.2f}")

    print(f"\nWROTE {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
