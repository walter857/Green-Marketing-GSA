#!/usr/bin/env python3
"""Build the BROAD-match name / business-entity negative layer.

Owner instruction 2026-08-28: add, at campaign level, broad-match negatives for
personal names, business names and surnames (one per row) plus entity markers
like llc / inc / corp, so the accounts stop paying for name-driven queries.

Broad match is aggressive, so a token only qualifies when EVERY guard passes:

  1. it is a known first name or surname (census / public name lists)
  2. it is NOT an English dictionary word  <- the critical guard. This is what
     protects green, stone, mason, brown, hill, park, field, young, cook ...
  3. >= 4 characters
  4. not part of the client's own brand
  5. not matched by the account's core-service / intent / in-area-geo patterns
  6. not a token of any TARGETED location name (surnames double as place names)
  7. not a token of any live positive keyword
  8. not present in any search term that produced a conversion
  9. not a Green Marketing PROTECTED BOFU phrase, not a generic modifier

Everything held back is reported with its reason. Local only; no API calls.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from neg_lexicon import ACCOUNTS, PROTECTED, compile_account  # noqa: E402
from neg_competitors import GENERIC  # noqa: E402

CORPUS = ROOT / "reports" / "st-corpus"
VERD = ROOT / "reports" / "st-verdicts"
LEX = ROOT / "reports" / "lexicons"
OUT = ROOT / "reports" / "st-names"

TOKEN_RE = re.compile(r"[a-z0-9']+")

# Business-entity markers. Deliberately conservative: "co" and "limited" are
# excluded because they collide with legitimate queries ("ac repair co",
# "limited time"). These are added whether or not they appear in the corpus.
ENTITY_MARKERS = ["llc", "inc", "corp", "corporation", "incorporated", "ltd"]

# Equipment MANUFACTURER names are not competitors. "weil mclain boiler repair"
# or "lennox furnace repair near me" is high-intent service demand for a company
# that repairs those units. Broad-negating the brand would destroy that demand.
MANUFACTURERS = {
    "ambient-cooling-heating": {
        "trane", "carrier", "lennox", "goodman", "rheem", "ruud", "york", "amana",
        "bryant", "daikin", "mitsubishi", "fujitsu", "gree", "midea", "payne",
        "heil", "coleman", "tempstar", "comfortmaker", "luxaire", "armstrong",
        "ducane", "nordyne", "mrcool", "weil", "mclain", "burnham", "navien",
        "viessmann", "buderus", "lochinvar", "slant", "utica", "peerless",
        "crown", "laars", "munchkin", "bosch", "rinnai", "noritz", "bradford",
        "honeywell", "ecobee", "aprilaire", "unico", "sanyo", "haier",
    },
    "pro-green-austin": {
        "belgard", "techo", "unilock", "pavestone", "keystone", "versa",
        "rockwood", "oldcastle", "borgert", "nicolock", "cambridge", "henry",
        "synlawn", "foreverlawn", "trex", "azek", "kichler", "volt",
        "gilmour", "rainbird", "hunter", "toro", "orbit", "melnor",
    },
    "softwind-power-washing": {
        "karcher", "ryobi", "simpson", "generac", "dewalt", "greenworks",
        "craftsman", "briggs", "honda", "northstar", "mytee", "hotsy",
    },
}

# Service vocabulary in other languages spoken in the market. These are demand,
# not names. ("jardines de casa" is a Spanish landscaping query, not a surname.)
FOREIGN_SERVICE = {
    "jardin", "jardines", "jardineria", "paisajismo", "cesped", "concreto",
    "adoquines", "piscina", "reparacion", "acondicionado", "calefaccion",
    "calentador", "plomero", "limpieza", "lavado", "presion", "casa", "hogar",
    "instalacion", "mantenimiento", "empresa", "compania", "precio", "costo",
    "cerca", "gratis", "presupuesto",
}

# Geography is handled precisely by the core layer's GEO_OUT_OF_AREA phrase and
# exact negatives. A place name must never become a BROAD negative: "rosedale",
# "calvert" and "denton" are Maryland places, not competitors.
HOME_STATE = {
    "ambient-cooling-heating": "MD",
    "pro-green-austin": "TX",
    "softwind-power-washing": "NY",
    "softwind-landscape-masonry": "NY",
}
# Places a searcher in this market plausibly names. Any of them belongs in the
# precise geo layer, never in a blunt BROAD name negative.
NEIGHBOUR_STATES = {
    "ambient-cooling-heating": ["MD", "VA", "DC", "DE", "PA", "WV", "NJ"],
    "pro-green-austin": ["TX", "OK", "LA", "AR", "NM"],
    "softwind-power-washing": ["NY", "NJ", "CT", "PA", "MA", "VT", "RI"],
    # Same Long Island market as the sibling. Added 2026-08-30: without an entry
    # here state_places fell back to HOME_STATE, which was also missing, so the
    # US-place guard was INERT for this account and place names such as
    # "westbury" and "staten" were accepted as BROAD name negatives.
    "softwind-landscape-masonry": ["NY", "NJ", "CT", "PA", "MA", "VT", "RI"],
}

GEO_SNAPSHOTS = {
    "ambient-cooling-heating": [
        "clients/ambient-cooling-heating/snapshots/audit-2026-08-17.json"],
    "softwind-power-washing": [
        "clients/softwind-power-washing/snapshots/geo-confirmed-2026-08-26.json",
        "clients/softwind-power-washing/snapshots/geo-union-2026-08-26.json",
        "clients/softwind-power-washing/snapshots/stage3-geo-resolution-2026-08-26.json"],
    "pro-green-austin": [],   # uses location-targets.yaml below
}


def toks(s):
    return TOKEN_RE.findall(s.lower())


def load_geo_tokens(slug):
    """Tokens appearing in any TARGETED location name. Never negate these."""
    names = []
    for rel in GEO_SNAPSHOTS.get(slug, []):
        p = ROOT / rel
        if not p.exists():
            continue
        s = p.read_text(encoding="utf-8")
        names += re.findall(r'"canonical_name"\s*:\s*"([^"]+)"', s)
    if slug == "pro-green-austin":
        p = ROOT / "clients/pro-green-austin/location-targets.yaml"
        if p.exists():
            s = p.read_text(encoding="utf-8")
            names += re.findall(r"canonical_name:\s*(.+)", s)
            names += re.findall(r"as_supplied:\s*(.+)", s)
    tk = set()
    for n in names:
        tk.update(toks(n))
    return tk, len(names)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    english = {w.strip() for w in (LEX / "english_words.txt").read_text(
        encoding="utf-8").splitlines() if w.strip()}
    firsts = {w.strip() for w in (LEX / "first_names.txt").read_text(
        encoding="utf-8").splitlines() if w.strip()}
    sur_gh = {w.strip() for w in (LEX / "surnames_github.txt").read_text(
        encoding="utf-8").splitlines() if w.strip()}
    sur_census = json.loads((LEX / "surnames_census.json").read_text(encoding="utf-8"))
    all_names = firsts | sur_gh | set(sur_census)
    print("lexicons: english={} first={} surnames={} (census {})".format(
        len(english), len(firsts), len(sur_gh | set(sur_census)), len(sur_census)))

    places_by_state = json.loads(
        (LEX / "us_places_by_state.json").read_text(encoding="utf-8"))

    grand = {}
    for slug, cfg in ACCOUNTS.items():
        if not (CORPUS / (slug + "-corpus.json")).exists():
            print("[{}] SKIP: no corpus on disk yet".format(slug))
            continue
        try:
            comp = compile_account(cfg)
        except ValueError as exc:
            print("[{}] SKIP: {}".format(slug, exc))
            continue
        # A missing entry used to fall back to "" -> places_by_state[""] -> empty
        # set, silently disabling the US-place guard and letting place names
        # through as BROAD negatives. Fail loudly instead.
        if slug not in NEIGHBOUR_STATES and slug not in HOME_STATE:
            raise SystemExit(
                "{}: no NEIGHBOUR_STATES/HOME_STATE entry. The US-place guard "
                "would be inert and place names could be minted as BROAD "
                "negatives. Add the market's states before running.".format(slug))
        state_places = set()
        for st in NEIGHBOUR_STATES.get(slug, [HOME_STATE.get(slug, "")]):
            for nm in places_by_state.get(st, []):
                state_places.update(toks(nm))
        d = json.loads((CORPUS / (slug + "-corpus.json")).read_text(encoding="utf-8"))
        geo_tokens, geo_names = load_geo_tokens(slug)

        terms = {}
        with (VERD / (slug + "-verdicts.csv")).open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                terms[r["search_term"]] = {
                    "impr": int(r["impressions"]), "clicks": int(r["clicks"]),
                    "cost": float(r["cost_usd"]), "conv": float(r["conversions"]),
                    "verdict": r["verdict"],
                }
        # Decisive guard: a token that appears in ANY in-scope KEEP term is not a
        # competitor name, it is demand. This is what separates the boiler brand
        # Weil-McLain and the town of Owings Mills from the competitor F.H. Furr.
        keep_tokens, watch_tokens, neg_tokens = set(), set(), set()
        for t, v in terms.items():
            bucket = (keep_tokens if v["verdict"] == "KEEP"
                      else watch_tokens if v["verdict"] == "WATCH" else neg_tokens)
            bucket.update(toks(t))

        live_c = {c["id"]: c for c in d["campaigns"] if c["status"] == "ENABLED"}
        live_ag = {a["id"] for a in d["ad_groups"]
                   if a["status"] == "ENABLED" and a["campaign_id"] in live_c}
        pos_tokens = set()
        for p in d["positive_keywords"]:
            if p["ad_group_id"] in live_ag:
                pos_tokens.update(toks(p["text"]))
        conv_tokens = set()
        for t, v in terms.items():
            if v["conv"] > 0:
                conv_tokens.update(toks(t))
        protected_tokens = set()
        for p in PROTECTED:
            protected_tokens.update(toks(p))

        stats = defaultdict(lambda: {"terms": 0, "impr": 0, "clicks": 0, "cost": 0.0})
        for t, v in terms.items():
            for tok in set(toks(t)):
                s = stats[tok]
                s["terms"] += 1
                s["impr"] += v["impr"]
                s["clicks"] += v["clicks"]
                s["cost"] += v["cost"]

        accepted, held = [], []
        for tok, s in stats.items():
            if tok not in all_names:
                continue
            probe = " " + tok + " "
            reason = None
            if tok in english:
                reason = "is_an_english_word"
            elif len(tok) < 4:
                reason = "too_short"
            elif comp["brand"].search(probe):
                reason = "client_brand"
            elif comp["core"].search(probe) or comp["intent"].search(probe):
                reason = "service_or_intent_vocabulary"
            elif comp["geo_in"].search(probe) or tok in geo_tokens:
                reason = "targeted_location_name"
            elif tok in pos_tokens:
                reason = "live_positive_keyword"
            elif tok in conv_tokens:
                reason = "appears_in_a_converting_term"
            elif tok in protected_tokens or tok in GENERIC:
                reason = "protected_or_generic"
            elif tok in MANUFACTURERS.get(slug, set()):
                reason = "equipment_manufacturer_is_demand"
            elif tok in FOREIGN_SERVICE:
                reason = "foreign_language_service_vocabulary"
            elif tok in state_places:
                reason = "us_place_name_in_market_region"
            elif comp["geo_out"].search(probe):
                reason = "out_of_area_geo_handled_by_geo_layer"
            elif tok in keep_tokens:
                reason = "appears_in_an_in_scope_KEEP_term"
            elif tok not in neg_tokens:
                reason = "no_negative_verdict_evidence"
            if reason:
                held.append({"token": tok, "reason": reason,
                             "terms": s["terms"], "cost_usd": round(s["cost"], 2)})
            else:
                accepted.append({
                    "text": tok, "match_type": "BROAD",
                    "category": "NAME_OR_BUSINESS_NAME",
                    "census_surname_rank": sur_census.get(tok),
                    "distinct_terms": s["terms"], "impressions": s["impr"],
                    "clicks": s["clicks"], "cost_usd": round(s["cost"], 2),
                    "also_in_watch_terms": tok in watch_tokens})

        accepted.sort(key=lambda r: (-r["cost_usd"], -r["distinct_terms"]))

        entities = []
        for m in ENTITY_MARKERS:
            if m in pos_tokens or m in conv_tokens:
                held.append({"token": m, "reason": "entity_marker_in_use_by_account",
                             "terms": stats.get(m, {}).get("terms", 0), "cost_usd": 0})
                continue
            # An entity marker is a BROAD single token, so it blocks EVERY query
            # containing it, forever -- including the client's own "<brand> llc".
            # The surname layer already refuses a token that sits inside a KEEP
            # term (see keep_tokens above); the marker branch skipped that check,
            # so "llc" and "inc" were being minted while KEEP terms carried them.
            # Hold the marker back unless it earns its place on waste evidence.
            if m in keep_tokens:
                held.append({"token": m, "reason": "entity_marker_inside_KEEP_term",
                             "terms": stats.get(m, {}).get("terms", 0),
                             "cost_usd": round(stats.get(m, {}).get("cost", 0.0), 2)})
                continue
            # The surname layer refuses an English word because a BROAD negative
            # on one destroys demand. A marker is no different -- "corp" was
            # being held back as an English word by that guard and accepted here
            # in the same run.
            if m in english:
                held.append({"token": m, "reason": "entity_marker_is_an_english_word",
                             "terms": stats.get(m, {}).get("terms", 0),
                             "cost_usd": round(stats.get(m, {}).get("cost", 0.0), 2)})
                continue
            # Mutation necessity: a marker with no term and no impression in the
            # whole all-time corpus is a speculative object, not a finding.
            _s = stats.get(m, {"terms": 0, "impr": 0})
            if not _s.get("terms") and not _s.get("impr"):
                held.append({"token": m, "reason": "entity_marker_no_corpus_evidence",
                             "terms": 0, "cost_usd": 0})
                continue
            s = stats.get(m, {"terms": 0, "impr": 0, "clicks": 0, "cost": 0.0})
            entities.append({"text": m, "match_type": "BROAD",
                             "category": "BUSINESS_ENTITY_MARKER",
                             "distinct_terms": s["terms"], "impressions": s["impr"],
                             "clicks": s["clicks"], "cost_usd": round(s["cost"], 2)})

        layer = accepted + entities
        obj = len(layer) * len(live_c)
        spend = sum(r["cost_usd"] for r in layer)

        p = OUT / (slug + "-name-negatives.json")
        p.write_text(json.dumps({
            "slug": slug, "customer_id": cfg["customer_id"],
            "account_name": d["account_name"],
            "match_type": "BROAD (explicit owner approval 2026-08-28)",
            "placement": "campaign level",
            "geo_names_used_for_protection": geo_names,
            "negatives": layer,
            "held_back": sorted(held, key=lambda r: -r["cost_usd"]),
            "per_campaign_objects": len(layer),
            "total_objects": obj,
        }, indent=2), encoding="utf-8")

        with (OUT / (slug + "-name-negatives.csv")).open(
                "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["negative_keyword", "match_type", "category",
                        "census_surname_rank", "distinct_terms", "impressions",
                        "clicks", "cost_usd"])
            for r in layer:
                w.writerow([r["text"], r["match_type"], r["category"],
                            r.get("census_surname_rank", ""), r["distinct_terms"],
                            r["impressions"], r["clicks"], r["cost_usd"]])

        print("=" * 78)
        print("{}  ({})".format(d["account_name"], cfg["customer_id"]))
        print("=" * 78)
        print("  targeted location names used as protection : {} ({} tokens)".format(
            geo_names, len(geo_tokens)))
        print("  region place tokens protected ({:<20}): {}".format(
            ",".join(NEIGHBOUR_STATES.get(slug, [])), len(state_places)))
        print("  NAME negatives accepted                    : {}".format(len(accepted)))
        print("  ENTITY markers added                       : {}  {}".format(
            len(entities), [e["text"] for e in entities]))
        print("  spend those tokens currently sit on        : ${:,.2f}".format(spend))
        print("  objects at campaign level                  : {} x {} campaigns = {}".format(
            len(layer), len(live_c), obj))
        print("  name-like tokens HELD BACK by a guard      : {}".format(len(held)))
        hb = defaultdict(int)
        for h in held:
            hb[h["reason"]] += 1
        for reason, n in sorted(hb.items(), key=lambda x: -x[1]):
            print("      {:<34} {}".format(reason, n))
        print("  top accepted by spend:")
        for r in accepted[:12]:
            print("      {:<16} ${:>8,.2f}  terms={:<4} clicks={:<3} rank={:<8} watch={}".format(
                r["text"], r["cost_usd"], r["distinct_terms"], r["clicks"],
                str(r["census_surname_rank"]), r["also_in_watch_terms"]))
        print("  file -> {}\n".format(p.relative_to(ROOT)))
        grand[slug] = {"names": len(accepted), "entities": len(entities),
                       "per_campaign": len(layer), "objects": obj,
                       "spend_usd": round(spend, 2), "held_back": len(held)}

    (OUT / "summary.json").write_text(json.dumps(grand, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
