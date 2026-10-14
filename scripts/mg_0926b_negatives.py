#!/usr/bin/env python3
"""2026-09-26 LOCAL (no API): MasterGrass negative-keyword build, round 2.

Owner instruction 2026-09-26: "add as many negative keywords as possible as exact match and
phrase match and also forecast possible future bad searched terms to add as negative in advance."

Layers
  SHARED  one new shared list for Landscaping + Hardscaping (and the drainage PMax):
          F  forecast PHRASE vocabulary (strategist-authored; Keyword Planner Iowa informed it)
          H  history: every NEGATIVE-verdict search term, PHRASE (covers the exact query and every
             longer variant); falls back to EXACT when the phrase form would block something good
  CROSS   campaign-level PHRASE cross-negatives so campaigns stop competing:
             Hardscaping <- drainage/grading/mulch;  PMax drainage <- hardscape + non-drainage services

Guards (a negative is dropped, or downgraded PHRASE -> EXACT, when it would):
  * block any live enabled keyword in an attached campaign (or a PMax search theme)
  * block a converting search term, or an IN_SCOPE_COMMERCIAL term
  * equal a PROTECTED word, or be a service-area town
  * look like a misspelling of a core service word (edit distance) - history layer only
  * duplicate a negative already live on EVERY attached campaign
A PHRASE negative already blocks its own exact query, so an EXACT copy of the same text is
redundant and is not added. Raw search terms stay on disk; stdout prints counts and the
strategist's own vocabulary only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from neg_lexicon import PROTECTED  # noqa: E402
from mg_0926b_copy import CITY, PMAX_TEXT  # noqa: E402

SNAP = ROOT / "clients" / "mastergrass-lawn-care" / "snapshots" / "audit-2026-09-26"
ST = ROOT / "reports" / "mastergrass-lawn-care" / "st"
PLANS = ROOT / "clients" / "mastergrass-lawn-care" / "plans"
LAND, HARD = "23905193676", "23914692658"
TOK = re.compile(r"[a-z0-9']+")

FORECAST = {
    "jobs_careers": "job|jobs|career|careers|hiring|salary|salaries|wage|wages|employment|resume|internship|"
                    "apprentice|apprenticeship|help wanted|now hiring|indeed|glassdoor|ziprecruiter",
    "training_licensing": "school|schools|course|courses|class|classes|degree|certification|certificate|training|"
                          "license|license requirements|license exam",
    "business_b2b": "software|app|apps|template|templates|invoice|marketing|seo|franchise|llc|logo|insurance|"
                    "wholesale|supplier|suppliers|supply|supplies|business plan|business for sale|for sale|"
                    "name ideas|business names|landscaping leads|lawn care leads|bid sheet",
    "diy_informational": "diy|do it yourself|how to|how do|how deep|how long|how wide|what is|what does|"
                         "definition|meaning|vs|versus|diagram|drawing|sketch|pdf|video|videos|youtube|reddit|"
                         "pinterest|ideas|pictures|photos|images|inspiration|examples|calculator|wikipedia|"
                         "quizlet|meme|game|minecraft|sims|animal crossing|coloring|clipart|png|svg|cartoon",
    "retail_brands": "home depot|lowes|lowe's|menards|amazon|walmart|costco|tractor supply|harbor freight|"
                     "kit|kits|buy|purchase",
    "equipment_rental": "rental|rentals|excavator|skid steer|bobcat|trencher|tractor|mini excavator|tiller|"
                        "rototiller|sod cutter|plate compactor|compactor|leveler|rake|lawn roller|attachment",
    "materials_buyer": "topsoil delivery|dirt delivery|bulk|pallet|per ton|by the ton|cubic yard|cubic yards|"
                       "by the yard",
    "drainage_products_diy": "perforated|pvc|corrugated|sock|grate|cleanout|nds|ez drain|flexdrain|flex drain|"
                             "rain barrel",
    "other_trades": "basement waterproofing|basement finishing|basement remodel|interior|crawl space encapsulation|"
                    "waterproofing|foundation repair|"
                    "septic|leach field|sewer|plumber|plumbing|floor drain|shower|sink|tub|toilet|roofing|roofer|roof repair|"
                    "gutter cleaning|gutter guard|gutter guards|siding|windows|hvac|air conditioner|condensate|"
                    "electrician|pest control|mosquito|pressure washing|power washing|window cleaning|"
                    "snow plowing|holiday lights|fence installation|fence company|fence repair|fencing|deck builder|deck staining|sealcoating|"
                    "concrete leveling|mudjacking|foam jacking|slab jacking|stamped|pool builder|pool builders|"
                    "hot tub|screened|screen room|enclosed|enclosure|sunroom|arborist|land clearing|"
                    "brush clearing|indoor|artificial turf|synthetic turf|artificial grass",
    "farm_tiling": "farm|field tile|tiling|tile plow|ag drainage|agricultural",
    "lawn_tree_services": "tree service|tree services|tree cutting|stump|stump grinding|hedge trimming|"
                          "bush trimming|weed killer|weed spray|mower|aeration|overseeding|fertilization|fertilizer|maintenance|"
                          "irrigation|sprinkler|sprinklers|snow removal|leaf removal|christmas lights",
    "legal_municipal": "lawyer|attorney|law|laws|legal|sue|lawsuit|regulations|ordinance|permit|permits|"
                       "public works|municipal|dnr|storm sewer|highway|government",
    "out_of_area": "cedar rapids|iowa city|davenport|sioux city|waterloo|cedar falls|council bluffs|dubuque|"
                   "mason city|fort dodge|ottumwa|burlington|muscatine|omaha|minneapolis|st paul|saint paul|"
                   "kansas city|chicago|sioux falls|quad cities|moline|dallas|dfw|houston|phoenix|denver|"
                   "las vegas|florida|texas|california|arizona|colorado|illinois|minnesota|missouri|"
                   "nebraska|wisconsin|south dakota|north dakota|kansas|oklahoma|georgia|ohio|michigan",
}
CROSS = {
    HARD: ["french drain", "french drains", "drainage", "grading", "regrading", "yard leveling", "mulch"],
    "PMAX": ["patio", "patios", "paver", "pavers", "retaining wall", "retaining walls", "fire pit", "fire pits",
             "firepit", "outdoor kitchen", "outdoor kitchens", "hardscaping", "hardscape", "mulch", "sod",
             "lawn care", "lawn service", "mowing", "landscaping company", "landscaping companies",
             "landscaping services", "landscape design", "flower bed", "flower beds"],
}
CORE_WORDS = ["landscaping", "landscaper", "landscape", "hardscaping", "hardscape", "paver", "pavers", "patio",
              "retaining", "drainage", "french", "grading", "mulch", "kitchen", "outdoor", "leveling", "firepit"]
BUYER_ADJ = re.compile(r"\b(makeover|renovat\w*|remodel\w*|redo|overhaul|curb appeal|outdoor living|backyard|"
                       r"front yard|yard design|garden design|yard work|yard service|yard company|landscapers?|"
                       r"lanscap\w*|landscap\w*|hardscap\w*)\b")


def toks(s):
    return TOK.findall(s.lower())


def blocks(neg, mt, q):
    if mt == "EXACT":
        return neg == q
    if mt == "PHRASE":
        n = len(neg)
        return any(q[i:i + n] == neg for i in range(len(q) - n + 1)) if n and n <= len(q) else False
    return bool(neg) and set(neg) <= set(q)


def lev(a, b):
    if abs(len(a) - len(b)) > 2:
        return 9
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def misspelled_core(t):
    return any(len(w) >= 5 and w not in CORE_WORDS and min(lev(w, c) for c in CORE_WORDS) <= 2 for w in toks(t))


kw = json.loads((SNAP / "keywords.json").read_text(encoding="utf-8"))
live = {c: [toks(r["ad_group_criterion"]["keyword"]["text"]) for r in kw if r["campaign"]["id"] == c
            and not r["ad_group_criterion"].get("negative") and r["ad_group_criterion"].get("status") == "ENABLED"]
        for c in (LAND, HARD)}
live["PMAX"] = [toks(t) for t in PMAX_TEXT["search_themes"]]
existing = {LAND: set(), HARD: set(), "PMAX": set()}
for r in json.loads((SNAP / "campaign_criteria.json").read_text(encoding="utf-8")):
    cc = r["campaign_criterion"]
    if r["campaign"]["id"] in (LAND, HARD) and cc.get("negative") and cc.get("keyword"):
        existing[r["campaign"]["id"]].add((" ".join(toks(cc["keyword"]["text"])), cc["keyword"]["match_type"]))
verd = list(csv.DictReader((ST / "verdicts.csv").open(encoding="utf-8")))
conv_t = [toks(r["term"]) for r in verd if float(r["conv_all"]) > 0]
keep_t = [toks(r["term"]) for r in verd if r["category"] == "IN_SCOPE_COMMERCIAL"]
prot = {p.lower() for p in PROTECTED}
CAMP_NAME = {LAND: "Landscaping Search - BOFU", HARD: "Hardscaping Search - BOFU"}
TERMS_BY = {c: ([toks(r["term"]) for r in verd if float(r["conv_all"]) > 0 and CAMP_NAME[c] in r["campaigns"]],
                [toks(r["term"]) for r in verd if r["category"] == "IN_SCOPE_COMMERCIAL" and CAMP_NAME[c] in r["campaigns"]])
            for c in (LAND, HARD)}
TERMS_BY["PMAX"] = ([], [])


def guard(text, mt, scope, terms_scope=None, town_check=True):
    nt = toks(text)
    if not nt or len(nt) > 10 or len(text) > 80:
        return "length"
    if text in prot or (len(nt) == 1 and nt[0] in prot):
        return "protected"
    if town_check and CITY.search(text):
        return "service_area_town"
    for c in scope:
        if any(blocks(nt, mt, p) for p in live[c]):
            return f"blocks_live_keyword:{c}"
    ct, kt = (conv_t, keep_t) if terms_scope is None else terms_scope
    if any(blocks(nt, mt, q) for q in ct):
        return "blocks_converting_term"
    if any(blocks(nt, mt, q) for q in kt):
        return "blocks_keep_term"
    if all((" ".join(nt), mt) in existing[c] or (" ".join(nt), "PHRASE") in existing[c] for c in scope):
        return "already_live_everywhere"
    return "ok"


SHARED_SCOPE = [LAND, HARD, "PMAX"]
rows, stats, cost = [], Counter(), Counter()
seen = set()
for cat, spec in FORECAST.items():
    for w in dict.fromkeys(x.strip().lower() for x in spec.split("|") if x.strip()):
        g = guard(w, "PHRASE", SHARED_SCOPE)
        stats[("F", cat, g)] += 1
        if g == "ok" and (w, "PHRASE") not in seen:
            seen.add((w, "PHRASE"))
            rows.append(("SHARED", w, "PHRASE", "F", cat))
        elif g != "ok":
            rows.append(("REJECT", w, "PHRASE", "F", f"{cat}:{g}"))

for r in verd:
    if r["verdict"] != "NEGATIVE":
        continue
    t = " ".join(toks(r["term"]))
    if BUYER_ADJ.search(t):
        stats[("H", "buyer_adjacent_kept", "skip")] += 1
        continue
    if misspelled_core(t):
        stats[("H", "misspelled_core_kept", "skip")] += 1
        continue
    BUYERISH = {"near", "me", "company", "companies", "contractor", "contractors", "service", "services", "install",
                "installation", "installer", "quote", "estimate", "local", "best", "cost", "price", "hire"}
    short_buyer = len(toks(t)) <= 3 and bool(set(toks(t)) & BUYERISH)
    mt = "EXACT" if (len(toks(t)) == 1 or CITY.search(t) or short_buyer) else "PHRASE"
    g = guard(t, mt, SHARED_SCOPE, town_check=False)
    if g != "ok" and not g.startswith("already") and mt == "PHRASE":
        g2 = guard(t, "EXACT", SHARED_SCOPE, town_check=False)
        if g2 == "ok":
            g, mt = g2, "EXACT"
    stats[("H", r["category"], f"{mt}:{g}")] += 1
    cost[("H", mt, g)] += float(r["cost_all"])
    if g == "ok" and (t, mt) not in seen:
        seen.add((t, mt))
        rows.append(("SHARED", t, mt, "H", r["category"]))

for r in verd:
    if r["category"] != "OTHER_MASTER_GRASS_SERVICE":
        continue
    t = " ".join(toks(r["term"]))
    g = guard(t, "EXACT", SHARED_SCOPE, town_check=False)
    stats[("H2", "OTHER_MG_SERVICE", f"EXACT:{g}")] += 1
    if g == "ok" and not any(r_[0] == "SHARED" and r_[2] == "PHRASE" and blocks(toks(r_[1]), "PHRASE", toks(t)) for r_ in rows)             and (t, "EXACT") not in seen:
        seen.add((t, "EXACT"))
        rows.append(("SHARED", t, "EXACT", "H2", "OTHER_MASTER_GRASS_SERVICE"))

for scope_key, words in CROSS.items():
    for w in words:
        g = guard(w, "PHRASE", [scope_key], terms_scope=TERMS_BY[scope_key])
        stats[("X", scope_key, g)] += 1
        rows.append((f"CAMPAIGN:{scope_key}" if g == "ok" else "REJECT", w, "PHRASE", "X", f"cross:{g}"))

print("layer / category / guard -> count")
for k, v in sorted(stats.items()):
    print(f"  {k[0]} {k[1]:<30} {k[2]:<42} {v}")
print("history cost blocked (all-time):", {f"{k[1]}:{k[2]}": round(v, 2) for k, v in cost.items()})
shared = [r for r in rows if r[0] == "SHARED"]
print(f"\nSHARED list members: {len(shared)} | PHRASE {sum(1 for r in shared if r[2] == 'PHRASE')} | "
      f"EXACT {sum(1 for r in shared if r[2] == 'EXACT')}")
for scope_key in CROSS:
    print(f"CAMPAIGN {scope_key} cross-negatives: {sum(1 for r in rows if r[0] == 'CAMPAIGN:' + scope_key)}")
print("REJECTED forecast/cross (strategist vocabulary only):")
for r in rows:
    if r[0] == "REJECT" and r[3] in ("F", "X"):
        print(f"  {r[1]:<22} {r[4]}")
PLANS.mkdir(parents=True, exist_ok=True)
out = PLANS / "NEG-0926-2-DRAFT.csv"
with out.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["target", "text", "match_type", "layer", "category_or_guard"])
    for r in rows:
        w.writerow(r)
print("wrote", out.relative_to(ROOT), "sha256[:12]", hashlib.sha256(out.read_bytes()).hexdigest()[:12].upper())
