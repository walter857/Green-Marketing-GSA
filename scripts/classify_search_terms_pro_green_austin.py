#!/usr/bin/env python3
"""Search-term classification for Pro Green Austin, outdoor design & build.

Reads the local snapshot only. Issues no API call and changes nothing in Google Ads.

The service vocabulary is defined POSITIVELY (a whitelist). A term is only treated as
service-relevant when it matches a verified Pro Green Austin design-and-build theme. Every
other term is classified on its own recorded reason, never swept into one bucket.

Verdicts, per the Green Marketing scheme:
  KEEP                  matched keyword should stay as is
  WATCH                 plausibly relevant, needs more data or service verification
  ADD_AS_EXACT          strong buying intent, worth its own exact keyword
  ADD_AS_PHRASE         strong buying intent, worth a phrase keyword
  NEGATIVE_EXACT        block this exact query only
  NEGATIVE_PHRASE       block this phrase
  NEGATIVE_BROAD        entire concept is irrelevant; only when conflict checks pass
  MOVE_OR_RESTRUCTURE   relevant, but matched in the wrong ad group
  LANDING_PAGE_GAP      relevant intent with no aligned destination
  INSUFFICIENT_DATA     relevant shape, too little traffic to judge

Output policy: the complete term-level evidence table is written to CSV/JSON on disk.
Only service-relevant terms and per-reason counts are printed. Non-service term strings
are never printed.
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

# Green Marketing policy: these may never be negatived automatically.
PROTECTED = {"near me", "quote", "price", "pricing", "cost", "best", "hire", "local",
             "emergency", "free"}
PROTECTED_RE = re.compile(
    r"\b(near\s+me|quotes?|prices?|pricing|costs?|best|hire|local|emergency|free)\b", re.I)

# ---------------------------------------------------------------------------
# Verified Pro Green Austin outdoor design-and-build themes.
# Sourced from the account's own live ad-group themes and confirmed against the
# first-party Austin site. Anything outside this map is not a claimed service.
# ---------------------------------------------------------------------------
THEMES = {
    "patio": re.compile(r"\b(patios?|patio\s+(cover|installer|contractor|builder)s?)\b", re.I),
    "paver": re.compile(r"\b(pavers?|paving\s+stones?|hardscape\s+pavers?|"
                        r"interlocking\s+pavers?|brick\s+pavers?)\b", re.I),
    "driveway": re.compile(r"\b(driveways?)\b", re.I),
    "walkway": re.compile(r"\b(walkways?|pathways?|garden\s+paths?|stepping\s+stones?)\b", re.I),
    "retaining_wall": re.compile(r"\b(retaining\s+walls?|seat(ing)?\s+walls?|"
                                 r"garden\s+walls?|block\s+walls?)\b", re.I),
    "hardscape": re.compile(r"\b(hardscap\w*|stonework|masonry|flagstone|"
                            r"limestone\s+(patio|wall|steps?))\b", re.I),
    "outdoor_living": re.compile(r"\b(outdoor\s+living|outdoor\s+space|backyard\s+(design|"
                                 r"remodel|renovat\w*|makeover|transformation)|"
                                 r"outdoor\s+oasis)\b", re.I),
    "outdoor_kitchen": re.compile(r"\b(outdoor\s+kitchens?|built\s*-?in\s+grills?|"
                                  r"outdoor\s+bars?)\b", re.I),
    "fire_feature": re.compile(r"\b(fire\s*pits?|fire\s*places?\s+outdoor|outdoor\s+fireplaces?|"
                               r"fire\s+features?)\b", re.I),
    "pergola": re.compile(r"\b(pergolas?|arbors?|shade\s+structures?|patio\s+covers?|"
                          r"gazebos?|cabanas?)\b", re.I),
    "landscape_design": re.compile(r"\b(landscape\s+(design\w*|architect\w*|plan\w*)|"
                                   r"landscaping\s+design\w*|yard\s+design\w*)\b", re.I),
    "landscape_lighting": re.compile(r"\b(landscape\s+light\w*|outdoor\s+light\w*|"
                                     r"garden\s+light\w*|path\s+light\w*)\b", re.I),
    "artificial_turf": re.compile(r"\b(artificial\s+(turf|grass)|synthetic\s+(turf|grass)|"
                                  r"fake\s+grass|turf\s+install\w*)\b", re.I),
    "design_build": re.compile(r"\b(design\s*(and|&|-|\+)?\s*build|outdoor\s+contractors?|"
                               r"landscape\s+contractors?)\b", re.I),
}

# Commercial-buyer signals. Strong intent when combined with a theme.
BUYER = re.compile(r"\b(contractors?|companies|company|installers?|installation|install|"
                   r"builders?|build|services?|near\s+me|quotes?|estimates?|costs?|prices?|"
                   r"pricing|hire|professional|pros?|specialists?|experts?|"
                   r"remodel\w*|renovat\w*|replace\w*|repair\w*)\b", re.I)

# ---------------------------------------------------------------------------
# Non-service intents. Each carries its own recorded reason. None of these is a
# blanket blocklist: a term only lands here when the intent is unambiguous AND no
# protected buyer token is present.
# ---------------------------------------------------------------------------
REASONS = [
    ("employment_intent", re.compile(
        r"\b(jobs?|hiring|hire\s+me|careers?|salar(y|ies)|employment|apply|resume|"
        r"wages?|pay\s+rate|apprentice\w*|internships?|help\s+wanted|"
        r"now\s+hiring|job\s+openings?)\b", re.I)),
    ("diy_or_instructional", re.compile(
        r"\b(diy|do\s+it\s+yourself|how\s+to|how\s+do\s+(i|you)|tutorials?|"
        r"instructions?|step\s+by\s+step|guides?|courses?|classes?|schools?|"
        r"certification|training|learn\s+to|youtube|calculators?)\b", re.I)),
    ("equipment_rental_or_purchase", re.compile(
        r"\b(rentals?|rent\b|renting|for\s+sale|buy\b|purchase|machine\w*|equipment|"
        r"tools?|plate\s+compactor|excavator|skid\s+steer|bobcat|"
        r"home\s+depot|lowes?|menards?|tractor\s+supply|amazon|harbor\s+freight)\b", re.I)),
    ("materials_only_retail", re.compile(
        r"\b(suppl(y|ies|ier)|wholesale|distributors?|yards?\s+near|per\s+(ton|pallet|"
        r"square\s+foot|sq\s*ft)|bulk\b|delivery\s+of|by\s+the\s+pallet|"
        r"stone\s+yard|paver\s+suppl\w*|sand\s+and\s+gravel)\b", re.I)),
    ("software_or_template", re.compile(
        r"\b(software|apps?\b|cad\b|autocad|sketchup|templates?|3d\s+(design|model)|"
        r"online\s+(design|planner|tool)|design\s+program|planner\s+tool)\b", re.I)),
    ("unrelated_service", re.compile(
        r"\b(mow\w*|lawn\s+(care|maintenance|mowing|service|treatment)|fertiliz\w*|"
        r"weed\s+control|aerat\w*|overseed\w*|sod\s+install\w*|"
        r"sprinkler\w*|irrigation|drip\s+line|backflow|"
        r"tree\s+(removal|trimming|service|cutting)|stump\s+grind\w*|arborist|"
        r"pool\s+(install\w*|build\w*|construction|resurfac\w*|remodel\w*)|"
        r"pest\s+control|exterminat\w*|mosquito|"
        r"gutter\w*|roof\w*|siding|window\s+replace\w*|"
        r"pressure\s+wash\w*|power\s+wash\w*|window\s+clean\w*|"
        r"snow\s+(removal|plow\w*)|leaf\s+removal|"
        r"fenc(e|ing)\s+(install\w*|contractor|compan\w*|repair)|"
        r"deck\s+(build\w*|install\w*|repair|stain\w*)|"
        r"septic|foundation\s+repair|junk\s+removal|dumpster|"
        r"christmas\s+light\w*|holiday\s+light\w*)\b", re.I)),
    ("inspiration_or_research_only", re.compile(
        r"\b(pictures?|photos?|images?|ideas?|inspiration|examples?|gallery|"
        r"pinterest|instagram|before\s+and\s+after\s+photos?|"
        r"what\s+is\b|definition|meaning|vs\b|versus|difference\s+between|"
        r"pros\s+and\s+cons|reviews?\s+of|reddit)\b", re.I)),
    ("wrong_geography", re.compile(
        r"\b(dallas|fort\s+worth|dfw|houston|san\s+antonio|el\s+paso|lubbock|amarillo|"
        r"corpus\s+christi|mcallen|laredo|waco|tyler|beaumont|midland|odessa|"
        r"college\s+station|galveston|katy\b|the\s+woodlands|sugar\s+land|plano|"
        r"frisco|arlington|irving|garland|mckinney|denton|"
        r"oklahoma|louisiana|arkansas|new\s+mexico|arizona|colorado|california|"
        r"florida|georgia|tennessee|nevada|utah|kansas|missouri|"
        r"phoenix|denver|atlanta|nashville|chicago|new\s+york|los\s+angeles|"
        r"miami|seattle|portland|boston|philadelphia)\b", re.I)),
    ("commercial_or_municipal", re.compile(
        r"\b(commercial|municipal|hoa\b|apartment\s+complex|shopping\s+center|"
        r"industrial|city\s+of\b|county\s+of\b|government|school\s+district)\b", re.I)),
    ("brand_or_competitor", re.compile(
        r"\b(belgard|techo\s*-?\s*bloc|unilock|pavestone|keystone\s+wall|versa\s*-?\s*lok|"
        r"trex|azek|yardzen|tilly|thumbtack|angi|angie'?s\s+list|homeadvisor|"
        r"houzz|nextdoor|yelp|bbb\b|home\s*advisor|porch\.com|lawnstarter|taskrabbit)\b", re.I)),
    ("real_estate_or_unrelated_noun", re.compile(
        r"\b(homes?\s+for\s+sale|apartments?\s+for\s+rent|realtors?|zillow|redfin|"
        r"hotels?|restaurants?|menu|directions\s+to|weather|map\s+of)\b", re.I)),
]


def normalize(term: str) -> str:
    t = term.lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def themes_for(term: str) -> list[str]:
    return [name for name, rx in THEMES.items() if rx.search(term)]


def classify(term: str, impressions: int, clicks: int, cost: float,
             conversions: float, matched_theme: str | None,
             live_themes: set[str] | None = None) -> tuple[str, str, str, str, str]:
    """Return (verdict, reason, negative_text, negative_match_type, confidence)."""
    t = normalize(term)
    hits = themes_for(t)
    protected = bool(PROTECTED_RE.search(t))

    # Non-service intents first. Most specific wins. Employment and DIY beat a theme
    # match, because 'paver installer jobs' is not a buyer.
    for reason, rx in REASONS:
        if not rx.search(t):
            continue
        if reason in ("employment_intent", "diy_or_instructional", "software_or_template",
                      "equipment_rental_or_purchase", "materials_only_retail"):
            # Concept-level irrelevance. Safe as a phrase negative on the offending token.
            m = rx.search(t)
            return ("NEGATIVE_PHRASE", reason, m.group(0).lower(), "PHRASE",
                    "high" if clicks else "medium")
        if reason == "unrelated_service":
            m = rx.search(t)
            if hits:
                # Mixed intent: a real theme plus an unrelated service. Do not negative.
                return ("WATCH", "mixed_service_intent_needs_review", "", "",
                        "low")
            return ("NEGATIVE_PHRASE", reason, m.group(0).lower(), "PHRASE",
                    "high" if clicks else "medium")
        if reason == "wrong_geography":
            m = rx.search(t)
            return ("NEGATIVE_PHRASE", reason, m.group(0).lower(), "PHRASE",
                    "high" if clicks else "medium")
        if reason in ("brand_or_competitor", "real_estate_or_unrelated_noun"):
            m = rx.search(t)
            return ("NEGATIVE_PHRASE", reason, m.group(0).lower(), "PHRASE",
                    "medium")
        if reason == "commercial_or_municipal":
            # Only exclude when the client has said residential-only. Not verified.
            return ("WATCH", "commercial_intent_client_scope_unverified", "", "", "low")
        if reason == "inspiration_or_research_only":
            if protected or hits and clicks:
                # Design-and-build buyers do browse. Never auto-block a paying journey.
                return ("WATCH", "inspiration_term_with_buying_signal", "", "", "low")
            return ("NEGATIVE_PHRASE", reason, m.group(0).lower() if (m := rx.search(t)) else t,
                    "PHRASE", "medium" if clicks else "low")

    if not hits:
        return ("WATCH", "no_verified_service_theme_matched", "", "", "low")

    # Service-relevant from here down.
    buyer = bool(BUYER.search(t))
    off_theme = matched_theme is not None and matched_theme not in hits

    if off_theme and conversions > 0:
        return ("MOVE_OR_RESTRUCTURE",
                f"converted_but_matched_in_{matched_theme}_reads_as_{hits[0]}", "", "", "high")
    if conversions > 0:
        return ("KEEP", "converted_on_this_term", "", "", "high")
    # A verified theme with no live ad group and no aligned destination is a gap,
    # not a negative. Blocking it would discard real design-and-build demand.
    if live_themes is not None and clicks > 0 and not (set(hits) & live_themes):
        return ("LANDING_PAGE_GAP", f"no_live_ad_group_or_destination_for_{hits[0]}",
                "", "", "medium")
    if off_theme:
        return ("MOVE_OR_RESTRUCTURE", f"matched_in_{matched_theme}_but_reads_as_{hits[0]}",
                "", "", "medium")
    if buyer and clicks >= 2:
        return ("ADD_AS_EXACT", "service_theme_plus_buyer_intent_with_traffic", "", "", "medium")
    if buyer and clicks == 1:
        return ("ADD_AS_PHRASE", "service_theme_plus_buyer_intent_thin_traffic", "", "", "low")
    if impressions < 5 and clicks == 0:
        return ("INSUFFICIENT_DATA", "fewer_than_five_impressions", "", "", "low")
    if clicks == 0 and cost == 0:
        return ("WATCH", "service_theme_no_click_yet", "", "", "low")
    return ("WATCH", "service_theme_needs_more_evidence", "", "", "low")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--window", default="all_time")
    args = ap.parse_args()

    S = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    rows = S["search_terms"][args.window]
    live = {c["id"] for c in S["campaigns"] if c["status"] == "ENABLED"}

    # Ad-group name -> canonical theme, so an off-theme match can be detected.
    ag_theme: dict[str, str] = {}
    live_themes: set[str] = set()
    for ag in S["ad_groups"]:
        hits = themes_for(normalize(ag["name"]))
        if hits:
            ag_theme[ag["id"]] = hits[0]
            if ag["campaign_id"] in live and ag["status"] == "ENABLED":
                live_themes.update(hits)

    # Aggregate a term to one row per (term, campaign, ad group, matched keyword).
    agg: dict[tuple, dict] = {}
    for r in rows:
        key = (r["term"], r["campaign_id"], r["ad_group_id"], r["matched_keyword"],
               r["matched_keyword_match_type"])
        a = agg.setdefault(key, {
            "term": r["term"], "campaign_id": r["campaign_id"],
            "campaign_name": r["campaign_name"], "campaign_status": r["campaign_status"],
            "ad_group_id": r["ad_group_id"], "ad_group_name": r["ad_group_name"],
            "matched_keyword": r["matched_keyword"],
            "matched_keyword_match_type": r["matched_keyword_match_type"],
            "added_excluded": r["added_excluded"],
            "impressions": 0, "clicks": 0, "cost": 0.0,
            "conversions": 0.0, "all_conversions": 0.0, "conversions_value": 0.0,
        })
        a["impressions"] += r["impressions"]; a["clicks"] += r["clicks"]
        a["cost"] += r["cost"]; a["conversions"] += r["conversions"]
        a["all_conversions"] += r["all_conversions"]
        a["conversions_value"] += r["conversions_value"]

    # Every normalized query that ever converted. A phrase negative conflicts when it
    # appears as a whole-word sub-phrase of one of these, which is exactly how a phrase
    # negative would block it.
    converting_terms = sorted({normalize(a["term"]) for a in agg.values()
                               if a["conversions"] > 0})

    out_rows = []
    for a in agg.values():
        theme = ag_theme.get(a["ad_group_id"])
        verdict, reason, neg_text, neg_match, conf = classify(
            a["term"], a["impressions"], a["clicks"], a["cost"], a["conversions"], theme,
            live_themes)
        norm = normalize(a["term"])
        protected = bool(PROTECTED_RE.search(norm))
        if protected and verdict.startswith("NEGATIVE"):
            # Policy override: a protected buyer token can never be auto-negatived.
            verdict, reason, neg_text, neg_match, conf = (
                "WATCH", f"protected_term_override__was_{reason}", "", "", "low")
        # Conflict risk: would the proposed negative also block a live positive keyword?
        conflict = ""
        if neg_text:
            for k in S["keywords"]:
                if k["negative"] or k["campaign_id"] not in live or k["status"] != "ENABLED":
                    continue
                if neg_text in normalize(k["text"]):
                    conflict = f"BLOCKS live keyword {k['criterion_id']} {k['text']!r}"
                    break
            if not conflict:
                rx = re.compile(r"\b" + re.escape(neg_text) + r"\b")
                hits_conv = [t for t in converting_terms if rx.search(t)]
                if hits_conv:
                    conflict = (f"BLOCKS {len(hits_conv)} query/queries that converted "
                                f"(e.g. {hits_conv[0]!r})")
        level = ""
        if neg_text:
            level = "campaign" if a["campaign_id"] in live else "ad_group"
        out_rows.append({
            "original_search_term": a["term"],
            "normalized_term": norm,
            "campaign_id": a["campaign_id"], "campaign_name": a["campaign_name"],
            "campaign_status": a["campaign_status"],
            "ad_group_id": a["ad_group_id"], "ad_group_name": a["ad_group_name"],
            "matched_keyword_text": a["matched_keyword"],
            "matched_keyword_match_type": a["matched_keyword_match_type"],
            "date_window": args.window,
            "impressions": a["impressions"], "clicks": a["clicks"],
            "cost": round(a["cost"], 2), "conversions": a["conversions"],
            "all_conversions": a["all_conversions"],
            "conversions_value": a["conversions_value"],
            "qualified_leads": "", "sold_jobs": "",
            "current_search_term_status": a["added_excluded"],
            "verdict": verdict,
            "recommended_negative_text": neg_text,
            "recommended_negative_match_type": neg_match,
            "recommended_level": level,
            "reason": reason,
            "conflict_risk": conflict or ("none_detected" if neg_text else ""),
            "protected_term": "YES" if protected else "",
            "confidence": conf,
            "service_themes": "|".join(themes_for(norm)),
        })

    out_rows.sort(key=lambda r: (-r["cost"], -r["clicks"], r["normalized_term"]))
    csv_path = Path(args.out_csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    Path(args.out_json).write_text(json.dumps(out_rows, indent=2), encoding="utf-8")

    # ---- aggregate reporting only ----
    print(f"window={args.window}  rows={len(out_rows)}  "
          f"cost=${sum(r['cost'] for r in out_rows):,.2f}  "
          f"clicks={sum(r['clicks'] for r in out_rows)}  "
          f"conv={sum(r['conversions'] for r in out_rows):.1f}")
    print("\nVERDICT COUNTS (rows / clicks / cost)")
    vc = defaultdict(lambda: [0, 0, 0.0])
    for r in out_rows:
        v = vc[r["verdict"]]
        v[0] += 1; v[1] += r["clicks"]; v[2] += r["cost"]
    for k, v in sorted(vc.items(), key=lambda kv: -kv[1][2]):
        print(f"  {k:<22} rows={v[0]:5} clicks={v[1]:5} cost=${v[2]:10,.2f}")

    print("\nREASON COUNTS for non-service verdicts (counts only, no term strings)")
    rc = defaultdict(lambda: [0, 0, 0.0])
    for r in out_rows:
        if r["verdict"].startswith("NEGATIVE") or r["verdict"] == "WATCH":
            v = rc[r["reason"]]
            v[0] += 1; v[1] += r["clicks"]; v[2] += r["cost"]
    for k, v in sorted(rc.items(), key=lambda kv: -kv[1][2]):
        print(f"  {k:<46} rows={v[0]:5} clicks={v[1]:4} cost=${v[2]:9,.2f}")

    print("\nPROTECTED-TERM OVERRIDES APPLIED: "
          f"{sum(1 for r in out_rows if r['reason'].startswith('protected_term_override'))}")
    print("CONFLICT RISKS FOUND: "
          f"{sum(1 for r in out_rows if r['conflict_risk'].startswith('BLOCKS'))}")

    print("\nSERVICE-RELEVANT TERMS ON LIVE CAMPAIGNS (printable: these are buying queries)")
    for r in out_rows:
        if r["campaign_id"] in live and r["verdict"] in (
                "KEEP", "ADD_AS_EXACT", "ADD_AS_PHRASE", "MOVE_OR_RESTRUCTURE",
                "LANDING_PAGE_GAP"):
            print(f"  [{r['verdict']:<20}] ${r['cost']:7.2f} clk={r['clicks']:2} "
                  f"conv={r['conversions']:.0f} impr={r['impressions']:4} "
                  f"{r['original_search_term']!r}  <- {r['ad_group_name']}")

    print(f"\nwritten: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
