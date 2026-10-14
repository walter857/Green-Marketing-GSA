#!/usr/bin/env python3
"""Month-to-date search-term classification and ad-group negative plan.

Local files only. Proposes; never applies.

Every proposed negative is conflict-checked against the live positive keywords, every query
that ever converted, the Green Marketing protected-term list, and every negative that already
reaches the ad group at any level: ad group, campaign, linked shared list and the
account-level list.

Output policy: the full term-level table goes to CSV. The console prints service-relevant
buying queries and per-reason counts, never a bulk dump of the corpus.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PROTECTED_RE = re.compile(
    r"\b(near\s+me|quotes?|prices?|pricing|costs?|best|hire|local|emergency|free)\b", re.I)

# Verified Pro Green Austin design-and-build themes, from the first-party site.
THEMES = {
    "patio": re.compile(r"\b(patios?)\b", re.I),
    "paver": re.compile(r"\b(pavers?|paving\s+stones?)\b", re.I),
    "driveway": re.compile(r"\b(driveways?)\b", re.I),
    "walkway": re.compile(r"\b(walkways?|pathways?|stepping\s+stones?)\b", re.I),
    "retaining_wall": re.compile(r"\b(retaining\s+walls?|seat(ing)?\s+walls?|block\s+walls?)\b", re.I),
    "hardscape": re.compile(r"\b(hardscap\w*|stonework|masonry|flagstone)\b", re.I),
    "outdoor_living": re.compile(r"\b(outdoor\s+living|outdoor\s+space|backyard\s+(design|"
                                 r"remodel|renovat\w*|makeover)|outdoor\s+oasis)\b", re.I),
    "outdoor_kitchen": re.compile(r"\b(outdoor\s+kitchens?|built\s*-?in\s+grills?)\b", re.I),
    "fire_feature": re.compile(r"\b(fire\s*pits?|outdoor\s+fireplaces?|fire\s+features?)\b", re.I),
    "pergola": re.compile(r"\b(pergolas?|arbors?|shade\s+structures?|patio\s+covers?|gazebos?)\b", re.I),
    "landscape_design": re.compile(r"\b(landscape\s+(design\w*|architect\w*|plan\w*)|"
                                   r"landscaping\s+design\w*|yard\s+design\w*)\b", re.I),
    "landscape_lighting": re.compile(r"\b(landscape\s+light\w*|outdoor\s+light\w*|"
                                     r"path\s+light\w*)\b", re.I),
    "artificial_turf": re.compile(r"\b(artificial\s+(turf|grass)|synthetic\s+(turf|grass)|"
                                  r"fake\s+grass)\b", re.I),
    "design_build": re.compile(r"\b(design\s*(and|&|-|\+)?\s*build|outdoor\s+contractors?|"
                               r"landscape\s+contractors?)\b", re.I),
}

# Irrelevant intents. Each carries its own reason and a narrow negative token.
# (reason, detector, negative-token extractor)
REASONS = [
    ("employment_intent", re.compile(
        r"\b(jobs?|hiring|careers?|salar(y|ies)|employment|apply|resume|wages?|"
        r"apprentice\w*|internships?|help\s+wanted)\b", re.I)),
    ("diy_or_instructional", re.compile(
        r"\b(diy|do\s+it\s+yourself|how\s+to|how\s+do\s+(i|you)|tutorials?|instructions?|"
        r"step\s+by\s+step|guides?|courses?|classes?|schools?|certification|training|"
        r"youtube|calculators?)\b", re.I)),
    ("equipment_rental_or_purchase", re.compile(
        r"\b(rentals?|rent\b|renting|for\s+sale|machine\w*|equipment|plate\s+compactor|"
        r"excavator|skid\s+steer|bobcat|home\s+depot|lowes?|menards?|tractor\s+supply|"
        r"amazon|harbor\s+freight)\b", re.I)),
    ("materials_only_retail", re.compile(
        r"\b(suppl(y|ies|ier)|wholesale|distributors?|per\s+(ton|pallet|square\s+foot|sq\s*ft)|"
        r"bulk\b|stone\s+yard|sand\s+and\s+gravel|bags?\s+of)\b", re.I)),
    ("software_or_template", re.compile(
        r"\b(software|apps?\b|cad\b|autocad|sketchup|templates?|3d\s+(design|model)|"
        r"online\s+(design|planner|tool)|design\s+program)\b", re.I)),
    ("unrelated_service", re.compile(
        r"\b(mow\w*|lawn\s+(care|maintenance|mowing|service|treatment)|fertiliz\w*|"
        r"weed\s+control|aerat\w*|overseed\w*|sprinkler\w*|irrigation|backflow|"
        r"tree\s+(removal|trimming|service|cutting)|stump\s+grind\w*|arborist|"
        r"pool\s+(install\w*|build\w*|construction|resurfac\w*|remodel\w*|clean\w*)|"
        r"pest\s+control|exterminat\w*|mosquito|gutter\w*|roof\w*|siding|"
        r"pressure\s+wash\w*|power\s+wash\w*|window\s+clean\w*|snow\s+(removal|plow\w*)|"
        r"leaf\s+removal|fenc(e|ing)\s+(install\w*|contractor|compan\w*|repair)|"
        r"septic|foundation\s+repair|junk\s+removal|dumpster|christmas\s+light\w*|"
        r"holiday\s+light\w*|artificial\s+plants?|house\s+clean\w*|maid\b|"
        r"handyman|plumb\w*|electric(ian|al)\b|hvac|air\s+condition\w*|"
        r"appliance|carpet|flooring|paint\w*\s+(contractor|compan\w*|service))\b", re.I)),
    ("inspiration_or_research_only", re.compile(
        r"\b(pictures?|photos?|images?|ideas?|inspiration|examples?|gallery|pinterest|"
        r"instagram|what\s+is\b|definition|meaning|vs\b|versus|difference\s+between|"
        r"pros\s+and\s+cons|reddit|wikipedia)\b", re.I)),
    ("wrong_geography", re.compile(
        r"\b(dallas|fort\s+worth|dfw|houston|san\s+antonio|el\s+paso|lubbock|amarillo|"
        r"corpus\s+christi|mcallen|laredo|waco|tyler|beaumont|midland|odessa|"
        r"college\s+station|galveston|katy\b|the\s+woodlands|sugar\s+land|plano|frisco|"
        r"arlington|irving|garland|mckinney|denton|spring\s+texas|conroe|kingwood|"
        r"oklahoma|louisiana|arkansas|new\s+mexico|arizona|colorado|california|florida|"
        r"georgia|tennessee|nevada|utah|kansas|missouri|phoenix|denver|atlanta|nashville|"
        r"chicago|new\s+york|los\s+angeles|miami|seattle|portland|boston|philadelphia|"
        r"san\s+diego|las\s+vegas|tampa|orlando|charlotte|raleigh|columbus|indianapolis)\b",
        re.I)),
    ("commercial_or_municipal", re.compile(
        r"\b(commercial|municipal|hoa\b|apartment\s+complex|shopping\s+center|industrial|"
        r"city\s+of\b|county\s+of\b|government|school\s+district|warehouse)\b", re.I)),
    ("real_estate_or_unrelated_noun", re.compile(
        r"\b(homes?\s+for\s+sale|apartments?\s+for\s+rent|realtors?|zillow|redfin|hotels?|"
        r"restaurants?|menu|directions\s+to|weather|map\s+of|jobs\s+near)\b", re.I)),
]


def norm(t):
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def themes_for(t):
    return [n for n, rx in THEMES.items() if rx.search(t)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mtd", required=True)
    ap.add_argument("--deep", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-plan-json", required=True)
    args = ap.parse_args()

    M = json.loads(Path(args.mtd).read_text(encoding="utf-8"))
    D = json.loads(Path(args.deep).read_text(encoding="utf-8"))
    rows = M["rows"]
    LIVE = {c["id"]: c["name"] for c in D["campaigns"] if c["status"] == "ENABLED"}

    live_pos = [k for k in D["keywords"]
                if not k["negative"] and k["campaign_id"] in LIVE and k["status"] == "ENABLED"]
    converting = sorted({norm(r["term"]) for r in D["search_terms"]["all_time"]
                         if r["conversions"] > 0})

    # Every negative that already reaches a given ad group, at any level.
    live_sets = {l["shared_set_id"] for l in D["campaign_shared_sets"]
                 if l["campaign_id"] in LIVE and l["link_status"] == "ENABLED"}
    acct_sets = {s["id"] for s in D["shared_sets"]
                 if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"}
    account_wide = {(norm(m["keyword_text"]), m["match_type"]) for m in D["shared_criteria"]
                    if m["shared_set_id"] in live_sets | acct_sets}
    camp_negs = defaultdict(set)
    for c in D["campaign_criteria"]:
        if c["campaign_id"] in LIVE and c["type"] == "KEYWORD" and c["negative"]:
            camp_negs[c["campaign_id"]].add((norm(c["keyword_text"]), c["keyword_match_type"]))
    ag_negs = {k: {(norm(t), mt) for t, mt in v}
               for k, v in M["existing_ad_group_negatives"].items()}
    ag_campaign = {a["id"]: a["campaign_id"] for a in D["ad_groups"]}

    def already_blocked(ad_group_id, text, mt):
        key = (norm(text), mt)
        if key in account_wide:
            return "already in a shared or account-level list"
        if key in camp_negs.get(ag_campaign.get(ad_group_id, ""), set()):
            return "already a campaign negative"
        if key in ag_negs.get(ad_group_id, set()):
            return "already an ad-group negative"
        return ""

    def conflicts(text, mt):
        n = norm(text)
        rx = re.compile(r"\b" + re.escape(n) + r"\b")
        out = []
        for k in live_pos:
            kt = norm(k["text"])
            hit = (n == kt if mt == "EXACT" else bool(rx.search(kt)))
            if hit:
                out.append(f"blocks live keyword {k['criterion_id']} {k['text']!r}")
        for qq in converting:
            hit = (n == qq if mt == "EXACT" else bool(rx.search(qq)))
            if hit:
                out.append(f"blocks converting query {qq!r}")
        return out

    # aggregate per (term, ad group)
    agg = {}
    for r in rows:
        if r["campaign_id"] not in LIVE:
            continue
        k = (r["term"], r["ad_group_id"])
        a = agg.setdefault(k, {**r, "impressions": 0, "clicks": 0, "cost": 0.0,
                               "conversions": 0.0, "all_conversions": 0.0})
        a["impressions"] += r["impressions"]; a["clicks"] += r["clicks"]
        a["cost"] += r["cost"]; a["conversions"] += r["conversions"]
        a["all_conversions"] += r["all_conversions"]

    out_rows, proposals = [], []
    for (term, agid), a in agg.items():
        n = norm(term)
        hits = themes_for(n)
        protected = bool(PROTECTED_RE.search(n))
        verdict = reason = neg_text = neg_mt = ""
        conf = "low"

        matched_reason = None
        for label, rx in REASONS:
            m = rx.search(n)
            if m:
                matched_reason = (label, m.group(0).lower())
                break

        if a["conversions"] > 0:
            verdict, reason, conf = "KEEP", "converted_on_this_term", "high"
        elif matched_reason and not (matched_reason[0] == "unrelated_service" and hits):
            label, token = matched_reason
            if protected:
                verdict = "WATCH"
                reason = f"protected_term_override__was_{label}"
                conf = "low"
            else:
                verdict = "NEGATIVE_PHRASE"
                reason = label
                neg_text, neg_mt = token, "PHRASE"
                conf = "high" if a["clicks"] else "medium"
        elif matched_reason and hits:
            verdict, reason, conf = "WATCH", "mixed_service_intent_needs_review", "low"
        elif hits:
            if a["clicks"] >= 1:
                verdict, reason, conf = "KEEP", "service_theme_with_click", "medium"
            elif a["impressions"] < 3:
                verdict, reason = "INSUFFICIENT_DATA", "fewer_than_three_impressions"
            else:
                verdict, reason = "WATCH", "service_theme_no_click_yet"
        else:
            verdict, reason = "WATCH", "no_verified_service_theme_matched"

        dup = already_blocked(agid, neg_text, neg_mt) if neg_text else ""
        confl = conflicts(neg_text, neg_mt) if neg_text else []
        gate = "READY"
        if neg_text:
            if confl:
                gate = "BLOCKED_conflict"
            elif dup:
                gate = f"SKIP_{dup.replace(' ', '_')}"
        else:
            gate = "NO_ACTION"

        row = {
            "original_search_term": term, "normalized_term": n,
            "campaign_id": a["campaign_id"], "campaign_name": a["campaign_name"],
            "ad_group_id": agid, "ad_group_name": a["ad_group_name"],
            "matched_keyword_text": a["matched_keyword"],
            "matched_keyword_match_type": a["matched_match_type"],
            "date_window": f"{M['window']['start']}..{M['window']['end']}",
            "impressions": a["impressions"], "clicks": a["clicks"],
            "cost": round(a["cost"], 2), "conversions": a["conversions"],
            "all_conversions": a["all_conversions"],
            "qualified_leads": "", "sold_jobs": "",
            "verdict": verdict, "reason": reason,
            "recommended_negative_text": neg_text,
            "recommended_negative_match_type": neg_mt,
            "recommended_level": "ad_group" if neg_text else "",
            "conflict_risk": ("; ".join(confl) if confl else
                              (dup or ("none_detected" if neg_text else ""))),
            "protected_term": "YES" if protected else "",
            "confidence": conf, "service_themes": "|".join(hits), "gate": gate,
        }
        out_rows.append(row)
        if gate == "READY":
            proposals.append(row)

    out_rows.sort(key=lambda r: (-r["cost"], -r["clicks"], r["normalized_term"]))
    p = Path(args.out_csv)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader(); w.writerows(out_rows)

    # de-duplicate proposals to one (ad group, text, match type)
    seen, final = set(), []
    for r in sorted(proposals, key=lambda x: (-x["cost"], -x["clicks"])):
        key = (r["ad_group_id"], norm(r["recommended_negative_text"]),
               r["recommended_negative_match_type"])
        if key in seen:
            continue
        seen.add(key)
        final.append(r)
    Path(args.out_plan_json).write_text(json.dumps(final, indent=2), encoding="utf-8")

    print(f"window {M['window']['start']}..{M['window']['end']}  "
          f"live-campaign rows: {len(out_rows)}  "
          f"cost=${sum(r['cost'] for r in out_rows):,.2f}  "
          f"clicks={sum(r['clicks'] for r in out_rows)}  "
          f"conv={sum(r['conversions'] for r in out_rows):.1f}")
    print("\nVERDICTS")
    vc = defaultdict(lambda: [0, 0, 0.0])
    for r in out_rows:
        v = vc[r["verdict"]]; v[0] += 1; v[1] += r["clicks"]; v[2] += r["cost"]
    for k, v in sorted(vc.items(), key=lambda kv: -kv[1][2]):
        print(f"  {k:<22} rows={v[0]:4} clicks={v[1]:3} cost=${v[2]:8,.2f}")
    print("\nREASONS (counts only, no term strings)")
    rc = defaultdict(lambda: [0, 0, 0.0])
    for r in out_rows:
        v = rc[r["reason"]]; v[0] += 1; v[1] += r["clicks"]; v[2] += r["cost"]
    for k, v in sorted(rc.items(), key=lambda kv: -kv[1][2]):
        print(f"  {k:<48} rows={v[0]:4} clicks={v[1]:3} cost=${v[2]:8,.2f}")
    print(f"\nGATES: {dict(Counter(r['gate'] for r in out_rows))}")
    print(f"PROTECTED-TERM OVERRIDES: "
          f"{sum(1 for r in out_rows if r['reason'].startswith('protected_term_override'))}")
    print(f"CONFLICTS BLOCKING A PROPOSAL: "
          f"{sum(1 for r in out_rows if r['gate'] == 'BLOCKED_conflict')}")
    print(f"\nDISTINCT AD-GROUP NEGATIVES PROPOSED: {len(final)}")
    byag = Counter(r["ad_group_name"] for r in final)
    for k, v in sorted(byag.items()):
        print(f"    {k:<32} {v}")
    print("\nSERVICE-RELEVANT BUYING QUERIES KEPT (printable)")
    for r in out_rows:
        if r["verdict"] == "KEEP":
            print(f"  ${r['cost']:7.2f} clk={r['clicks']:2} impr={r['impressions']:4} "
                  f"{r['original_search_term']!r} <- {r['ad_group_name']}")
    print(f"\nwritten: {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
