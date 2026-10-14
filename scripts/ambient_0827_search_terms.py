#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | complete search-term corpus + verdicts.

Pulls every search term the API will return for the five live Search campaigns
across every required window, preserves source campaign / ad group / matched
keyword / match type / date window / metrics / conversion-action detail, then
classifies every term deterministically against the five approved services.

Read-only. Emits a full verdict CSV plus a JSON evidence pack.
"""
from __future__ import annotations

import csv
import datetime
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, EXPORTS, SNAP, TZ, client, q, identity_gate, E, write,
)

STAMP = "2026-08-27"

WINDOWS = {
    "august_mtd_settled": ("2026-08-01", "2026-08-26"),
    "today_partial": ("2026-08-27", "2026-08-27"),
    "post_negatives": ("2026-08-23", "2026-08-26"),
    "pre_negatives": ("2026-08-14", "2026-08-21"),
    "all_history": ("2019-01-01", "2026-08-27"),
    "last_365": ("2025-08-28", "2026-08-27"),
}

MET = ("metrics.impressions, metrics.clicks, metrics.cost_micros, "
       "metrics.conversions, metrics.all_conversions")

# ---------------------------------------------------------------------------
# Classification model. Whitelist-first: a term is IN SCOPE when it expresses
# demand for one of the five approved services (or an unambiguous HVAC problem
# that Ambient's five services answer). Everything else needs positive evidence
# of being out of scope before it can become a negative candidate.
# ---------------------------------------------------------------------------

SERVICE_CORE = {
    "AC Repair": [r"\bac\b", r"\ba/c\b", r"\bair ?condition", r"\bcooling\b"],
    "HVAC Repair": [r"\bhvac\b", r"\bheat ?pump", r"\bfurnace\b", r"\bheating\b"],
    "HVAC Installation": [r"\binstall", r"\bnew system", r"\bhvac\b"],
    "HVAC Replacement": [r"\breplac", r"\bnew (ac|hvac|system|unit|furnace)"],
    "Gas Boiler Repair": [r"\bboiler", r"\bgas\b"],
}
INTENT_TOKENS = [
    r"\brepair", r"\bfix", r"\bservic", r"\binstall", r"\breplac", r"\bnot (working|cooling|blowing)",
    r"\bbroken", r"\bcompany", r"\bcompanies", r"\bcontractor", r"\bnear me\b", r"\bnear you\b",
    r"\bemergency", r"\bsame day", r"\bquote", r"\bcost", r"\bprice", r"\bestimate",
    r"\btechnician", r"\btech\b", r"\bmaintenance", r"\btune ?up", r"\bcheck ?up",
]
HVAC_CONTEXT = [
    r"\bhvac\b", r"\bac\b", r"\ba/c\b", r"\bair ?condition", r"\bfurnace\b", r"\bboiler",
    r"\bheat ?pump", r"\bheating\b", r"\bcooling\b", r"\bduct", r"\bcondenser", r"\bcompressor",
    r"\bthermostat", r"\bmini ?split", r"\bfreon\b", r"\brefrigerant", r"\bevaporator",
    r"\bair handler", r"\bradiator", r"\bbaseboard", r"\ba c\b", r"\bac unit",
    r"\bheat and air\b", r"\bair and heat\b", r"\bcentral air\b", r"\bswamp cooler\b",
]

# Out-of-scope signals. Each carries the reason recorded in the plan.
OUT_OF_SCOPE = [
    (r"\b(car|cars|truck|trucks|van|vans|vehicle|vehicles|automotive|auto ?motive)\b",
     "vehicle AC, not building HVAC"),
    (r"\b(boat|boats|marine|yacht|rv|camper|motorhome)\b",
     "marine or RV AC, not building HVAC"),
    (r"\b(job|jobs|jobb|hiring|hire me|career|careers|salary|salaries|wage|wages|"
     r"apprentice|apprenticeship|union|employment|resume|vacanc)\b",
     "employment search, not a customer buying a service"),
    (r"\b(school|schools|class|classes|course|courses|training|certification|certified how|"
     r"license how|epa 608|degree|program|study)\b",
     "training or certification, not a service purchase"),
    (r"\b(diy|do it yourself|how to (fix|repair|install|replace|clean|wire)|tutorial|youtube|"
     r"video|manual|manuals|diagram|schematic|wiring diagram|troubleshoot(ing)? guide)\b",
     "self-help research, not a service purchase"),
    (r"\b(part|parts|capacitor|contactor|filter|filters|coil|motor|blower motor|"
     r"circuit board|fuse|belt|refrigerant for sale|buy freon)\b",
     "parts retail, not an installed service"),
    (r"\b(amazon|home ?depot|lowes|lowe's|walmart|costco|menards|ebay|for sale|"
     r"buy online|wholesale|supply house|supplier)\b",
     "retail or wholesale purchase, not a service"),
    (r"\b(window (ac|air condition)|portable (ac|air condition)|window unit)\b",
     "portable or window unit retail, not installed HVAC service"),
    (r"\b(free|cheap|cheapest)\s+(hvac|ac|repair|service)\b",
     "free or lowest-price-only intent"),
]

BRANDS_EQUIPMENT = re.compile(
    r"\b(carrier|trane|lennox|goodman|rheem|ruud|york|american standard|bryant|amana|"
    r"payne|daikin|mitsubishi|fujitsu|coleman|nordyne|ducane|frigidaire|ecobee|nest|"
    r"honeywell|bosch|navien|weil ?mclain|burnham|buderus|lochinvar)\b", re.I)

COMPETITOR_HINT = re.compile(
    r"\b(heating and air|htg|air experts|comfort|climate|breeze|arctic|polar)\b", re.I)


def classify(term: str, clicks: int, cost: float, conv: float):
    t = " " + term.lower().strip() + " "
    reasons = []
    for pattern, why in OUT_OF_SCOPE:
        if re.search(pattern, t):
            reasons.append(why)
    in_hvac = any(re.search(p, t) for p in HVAC_CONTEXT)
    has_intent = any(re.search(p, t) for p in INTENT_TOKENS)

    if conv > 0:
        return "KEEP", "produced a conversion; protected from negation", in_hvac, has_intent
    if reasons:
        return "NEGATIVE CANDIDATE", "; ".join(sorted(set(reasons))), in_hvac, has_intent
    if in_hvac and has_intent:
        return "KEEP", "HVAC service intent inside the approved services", in_hvac, has_intent
    if in_hvac:
        return "WATCH", "HVAC context but weak purchase intent", in_hvac, has_intent
    if clicks == 0:
        return "INSUFFICIENT EVIDENCE", "no clicks, no cost, no conversions", in_hvac, has_intent
    return "WATCH", "no HVAC context detected; needs manual read before negation", in_hvac, has_intent


def main():
    c = client()
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "read_only": True, "windows": WINDOWS}
    out["identity"] = identity_gate(c, verbose=False)
    print("IDENTITY: PASS\n")

    # ---------- pull every window, preserving source detail ----------
    rows = []
    coverage = {}
    for wname, (a, b) in WINDOWS.items():
        n = 0
        for r in q(c, f"""
            SELECT campaign.id, ad_group.id, ad_group.name,
                   search_term_view.search_term, search_term_view.status,
                   segments.search_term_match_type,
                   segments.keyword.info.text, segments.keyword.info.match_type,
                   {MET}
            FROM search_term_view
            WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '{a}' AND '{b}'
        """):
            rows.append({
                "window": wname, "window_start": a, "window_end": b,
                "campaign_id": str(r.campaign.id),
                "campaign": NAME[str(r.campaign.id)],
                "ad_group_id": str(r.ad_group.id), "ad_group": r.ad_group.name,
                "search_term": r.search_term_view.search_term,
                "st_status": E(r.search_term_view.status),
                "st_match_type": E(r.segments.search_term_match_type),
                "matched_keyword": r.segments.keyword.info.text,
                "keyword_match_type": E(r.segments.keyword.info.match_type),
                "impressions": r.metrics.impressions,
                "clicks": r.metrics.clicks,
                "cost": round(r.metrics.cost_micros / 1e6, 2),
                "conversions": round(r.metrics.conversions, 2),
                "all_conversions": round(r.metrics.all_conversions, 2),
            })
            n += 1
        coverage[wname] = n
        print(f"  {wname:22s} {a}..{b}  rows={n}")
    out["row_counts_by_window"] = coverage
    out["raw_rows"] = rows

    # ---------- conversion-action detail per term ----------
    conv_detail = defaultdict(dict)
    for r in q(c, f"""
        SELECT campaign.id, search_term_view.search_term,
               segments.conversion_action_name, metrics.all_conversions, metrics.conversions
        FROM search_term_view
        WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2019-01-01' AND '2026-08-27'
          AND metrics.all_conversions > 0
    """):
        k = r.search_term_view.search_term
        conv_detail[k][r.segments.conversion_action_name] = {
            "all_conversions": round(r.metrics.all_conversions, 2),
            "conversions": round(r.metrics.conversions, 2),
            "campaign": NAME[str(r.campaign.id)],
        }
    out["conversion_detail_by_term"] = {k: v for k, v in conv_detail.items()}
    print(f"\n  terms with any conversion attribution: {len(conv_detail)}")

    # ---------- deduplicate to one verdict per (term, campaign) ----------
    lifetime = [r for r in rows if r["window"] == "all_history"]
    key = lambda r: (r["search_term"], r["campaign_id"])  # noqa: E731
    agg = {}
    for r in lifetime:
        k = key(r)
        e = agg.setdefault(k, {
            "search_term": r["search_term"], "campaign_id": r["campaign_id"],
            "campaign": r["campaign"], "ad_group": r["ad_group"],
            "matched_keywords": set(), "st_match_types": set(),
            "impressions": 0, "clicks": 0, "cost": 0.0,
            "conversions": 0.0, "all_conversions": 0.0, "st_status": set(),
        })
        e["matched_keywords"].add(f"{r['matched_keyword']} [{r['keyword_match_type']}]")
        e["st_match_types"].add(r["st_match_type"])
        e["st_status"].add(r["st_status"])
        e["impressions"] += r["impressions"]
        e["clicks"] += r["clicks"]
        e["cost"] += r["cost"]
        e["conversions"] += r["conversions"]
        e["all_conversions"] += r["all_conversions"]

    # per-window presence for evidence
    presence = defaultdict(set)
    for r in rows:
        presence[key(r)].add(r["window"])

    verdicts = []
    for k, e in agg.items():
        e["cost"] = round(e["cost"], 2)
        e["conversions"] = round(e["conversions"], 2)
        e["all_conversions"] = round(e["all_conversions"], 2)
        verdict, reason, in_hvac, has_intent = classify(
            e["search_term"], e["clicks"], e["cost"], e["all_conversions"])
        verdicts.append({
            "search_term": e["search_term"],
            "campaign": e["campaign"], "campaign_id": e["campaign_id"],
            "ad_group": e["ad_group"],
            "matched_keywords": " | ".join(sorted(e["matched_keywords"])),
            "search_term_match_types": " | ".join(sorted(e["st_match_types"])),
            "search_term_status": " | ".join(sorted(e["st_status"])),
            "impressions": e["impressions"], "clicks": e["clicks"], "cost": e["cost"],
            "primary_conversions": e["conversions"],
            "all_conversions": e["all_conversions"],
            "conversion_actions": "; ".join(
                f"{n}={v['all_conversions']}" for n, v in
                conv_detail.get(e["search_term"], {}).items()) or "",
            "windows_present": " | ".join(sorted(presence[k])),
            "hvac_context": in_hvac, "purchase_intent": has_intent,
            "brand_or_equipment": bool(BRANDS_EQUIPMENT.search(e["search_term"])),
            "verdict": verdict, "reason": reason,
        })

    # ---------- already-blocked check against live negatives ----------
    live_neg = []
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.keyword.text,
                      campaign_criterion.keyword.match_type
                      FROM campaign_criterion WHERE campaign.id IN ({IN5})
                        AND campaign_criterion.type='KEYWORD'
                        AND campaign_criterion.negative=TRUE
                        AND campaign_criterion.status != 'REMOVED'"""):
        live_neg.append({"campaign": str(r.campaign.id),
                         "text": r.campaign_criterion.keyword.text,
                         "match": E(r.campaign_criterion.keyword.match_type)})
    acct_neg = []
    for r in q(c, """SELECT shared_set.id, shared_criterion.keyword.text,
                     shared_criterion.keyword.match_type FROM shared_criterion
                     WHERE shared_set.id = 11252984411"""):
        acct_neg.append({"text": r.shared_criterion.keyword.text,
                         "match": E(r.shared_criterion.keyword.match_type)})
    out["live_campaign_negatives"] = live_neg
    out["account_level_negative_list"] = acct_neg

    def blocked_by(term, campaign_id):
        """Google negative matching: BROAD negative blocks a query only when
        every term of the negative appears in the query. No close variants."""
        words = set(re.findall(r"[a-z0-9&']+", term.lower()))
        hits = []
        for n in live_neg:
            if n["campaign"] != campaign_id:
                continue
            nw = re.findall(r"[a-z0-9&']+", n["text"].lower())
            if not nw:
                # A negative whose text tokenizes to nothing in this alphabet
                # (for example the CJK entry) can never match a Latin query.
                continue
            if n["match"] == "BROAD" and all(w in words for w in nw):
                hits.append(f"campaign:{n['text']}[{n['match']}]")
            elif n["match"] == "PHRASE" and n["text"].lower() in term.lower():
                hits.append(f"campaign:{n['text']}[{n['match']}]")
            elif n["match"] == "EXACT" and n["text"].lower() == term.lower():
                hits.append(f"campaign:{n['text']}[{n['match']}]")
        for n in acct_neg:
            nw = re.findall(r"[a-z0-9&']+", n["text"].lower())
            if not nw:
                continue
            if n["match"] == "BROAD" and all(w in words for w in nw):
                hits.append(f"account:{n['text']}[{n['match']}]")
            elif n["match"] == "PHRASE" and n["text"].lower() in term.lower():
                hits.append(f"account:{n['text']}[{n['match']}]")
            elif n["match"] == "EXACT" and n["text"].lower() == term.lower():
                hits.append(f"account:{n['text']}[{n['match']}]")
        return hits

    for v in verdicts:
        hits = blocked_by(v["search_term"], v["campaign_id"])
        v["already_blocked_by"] = "; ".join(hits)
        if hits and v["verdict"] == "NEGATIVE CANDIDATE":
            v["verdict"] = "ALREADY BLOCKED"
            v["reason"] += " | already covered by an existing negative"

    verdicts.sort(key=lambda z: (-z["cost"], -z["impressions"], z["search_term"]))
    out["verdicts"] = verdicts

    print(f"\n== TOTAL DISTINCT (term, campaign) PAIRS: {len(verdicts)} ==")
    from collections import Counter
    print("  ", dict(Counter(v["verdict"] for v in verdicts)))

    print("\n== FULL VERDICT TABLE (all-history corpus) ==")
    print(f"  {'verdict':22s} {'campaign':18s} {'impr':>5s} {'clk':>4s} {'cost':>9s} "
          f"{'conv':>5s}  search term")
    for v in verdicts:
        print(f"  {v['verdict']:22s} {v['campaign']:18s} {v['impressions']:>5d} "
              f"{v['clicks']:>4d} ${v['cost']:>8,.2f} {v['all_conversions']:>5.1f}  "
              f"{v['search_term']}")
        if v["reason"]:
            print(f"      reason: {v['reason']}")
        if v["already_blocked_by"]:
            print(f"      blocked by: {v['already_blocked_by']}")
        if v["conversion_actions"]:
            print(f"      conversion actions: {v['conversion_actions']}")

    # ---------- coverage caveats ----------
    st_rows = coverage["all_history"]
    imp_covered = sum(v["impressions"] for v in verdicts)
    clk_covered = sum(v["clicks"] for v in verdicts)
    cost_covered = round(sum(v["cost"] for v in verdicts), 2)
    out["coverage"] = {
        "distinct_term_campaign_pairs": len(verdicts),
        "search_term_rows_all_history": st_rows,
        "impressions_covered_by_search_terms": imp_covered,
        "clicks_covered_by_search_terms": clk_covered,
        "cost_covered_by_search_terms": cost_covered,
        "campaign_impressions_all_history": 4218,
        "campaign_clicks_all_history": 118,
        "campaign_cost_all_history": 4943.69,
    }
    print("\n== COVERAGE ==")
    print(f"  search-term rows cover {imp_covered} impressions, {clk_covered} clicks, "
          f"${cost_covered:,.2f} cost")
    print("  campaign totals (all history): 4218 impressions, 118 clicks, $4,943.69")
    print("  Google withholds search terms below its privacy threshold, so the "
          "difference is unreportable, not missing from the account.")

    # ---------- write artifacts ----------
    csv_path = EXPORTS / f"search-term-verdicts-{STAMP}.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["verdict", "search_term", "campaign", "campaign_id", "ad_group",
            "matched_keywords", "search_term_match_types", "search_term_status",
            "windows_present", "impressions", "clicks", "cost",
            "primary_conversions", "all_conversions", "conversion_actions",
            "hvac_context", "purchase_intent", "brand_or_equipment",
            "already_blocked_by", "reason"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for v in verdicts:
            w.writerow({k: v[k] for k in cols})
    print(f"WROTE {csv_path}")

    write(SNAP / f"search-terms-{STAMP}.json", out)
    return out


if __name__ == "__main__":
    main()
