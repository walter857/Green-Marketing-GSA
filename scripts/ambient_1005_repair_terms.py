#!/usr/bin/env python3
"""Ambient | 2026-10-05 | Heating & Furnace Repair (24257819463) search-term verdicts, Phrase-vs-Exact evidence and negative drafts.
No API calls. Inputs: snapshots/repair-read-2026-10-05.json + exports/repair-search-terms-2026-10-05.jsonl (read 2026-10-05 06:47 ET).

Categories requested by Green Marketing 2026-10-05: direct heating repair / furnace repair / no-heat / installation-replacement /
informational / ambiguous / clearly irrelevant. Each term also gets a review flag (AC, space heater, fireplace, baseboard/radiant,
plumbing, water heater, non-HVAC equipment, DIY/info, oil, competitor, availability, location, local HVAC, duct, commercial).
Never-negate words (near me, cost, price, pricing, quote, best, local, hire, emergency, manufacturers, places) are never a reason.
Coverage = every live layer (account BROAD list, attached shared lists, campaign negatives incl. NEG-EXACT-2, ad-group negatives).
Google: negatives match casing/misspellings only, never close variants, plurals or reorderings.
Outputs: exports/repair-search-term-verdicts-2026-10-05.csv, snapshots/repair-search-term-analysis-2026-10-05.json.
"""
from __future__ import annotations
import csv, json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CD = ROOT / "clients" / "ambient-cooling-heating"
S = json.loads((CD / "snapshots" / "repair-read-2026-10-05.json").read_text(encoding="utf-8"))
ROWS = [json.loads(l) for l in (CD / "exports" / "repair-search-terms-2026-10-05.jsonl").read_text(encoding="utf-8").splitlines()]
AG = S["ad_groups"]
WIN = {"all": ("2026-09-17", "2026-10-04"), "base": ("2026-09-24", "2026-09-30"), "test": ("2026-10-01", "2026-10-02")}
HR_PHRASE = "142140741"


def norm(t):
    t = t.lower().replace("’", "'")
    return re.sub(r"[^\w&'+\- ]", " ", t).split()


def blocks(n_text, match, q):
    n = norm(n_text)
    if not n:
        return False
    if match == "EXACT":
        return n == q
    if match == "PHRASE":
        return any(q[i:i + len(n)] == n for i in range(len(q) - len(n) + 1))
    return all(t in q for t in n)


layers = []
for sid in S["account_level_sets"]:
    layers += [("account list " + sid, m["text"], m["match"], None) for m in S["shared_set_members"].get(sid, [])]
for a in S["attachments"]:
    if a["status"] == "ENABLED":
        layers += [("shared " + a["set"], m["text"], m["match"], None) for m in S["shared_set_members"].get(a["set"], [])]
layers += [("campaign", x["text"], x["match"], None) for x in S["campaign_criteria"].get("KEYWORD", []) if x["neg"]]
layers += [("ad group", k["text"], k["match"], k["ad_group"]) for k in S["keywords"] if k["negative"]]
POS = [k for k in S["keywords"] if not k["negative"] and k["status"] == "ENABLED"]


def covering(gid, term):
    q = norm(term)
    return [f"{l}: {m} [{t}]" for (l, t, m, g) in layers if (g is None or g == gid) and blocks(t, m, q)]


def literal_reach(term):
    q = norm(term)
    return [f"{AG[k['ad_group']]['name'][7:]} {k['match']} [{k['text']}]" for k in POS
            if (k["match"] == "EXACT" and norm(k["text"]) == q) or (k["match"] == "PHRASE" and blocks(k["text"], "PHRASE", q))]


COMPETITOR = {  # other businesses named in the query; sourced 2026-10-02 (see exports/negative-table-2026-10-02.md) unless noted
    "booths hvac", "boothe's heating air plumbing & drains", "tevis modern comfort", "s f jones heating and cooling", "moon air elkton",
    "dodge heating and air", "max air heating & a c inc", "coastal hvac annapolis", "carroll mechanical columbia md", "allpro hvac",
    "belair engineering hvac", "del air heating", "go ecco climate control", "home team heating and cooling", "howard mechanical hvac",
    "joey taylor hvac", "maryland mechanical heating & cooling", "right way heating", "scotty's heating and cooling", "stivers hvac inc",
    "triple eee hvac", "bnb heating and cooling", "call dad", "classic air waldorf md", "climate care crofton md", "cold comfort hvac rockville md",
    "compass energy laurel de", "falcon hvac", "frosty heating and air conditioning", "grove hvac maryland", "honest air mt airy",
    "hope plumbing heating and cooling", "jiffy hvac", "minnick hvac", "ocean air hvac", "powell and turner hvac", "pro tech hvac",
    "smock heating & air", "southern maryland heating and air waldorf md", "vito hvac", "xzavier hvac solutions llc baltimore reviews",
    # new 2026-10-05: Carrier dealer at 219 N River Rd NW, Warren, OH (carrier.com dealer pages)
    "thompson heating and cooling warren ohio",
}
ADDRESS_NAV = {"g & g mechanical heating & ac 305 e 31st st baltimore md 21218"}  # business name + street address, not an Ambient location
WITHHELD = {"b&d hvac", "stanton hvac", "coastal heat and air", "harbor point heating and air"}  # withheld 2026-10-02: name unconfirmed (settled)
NAME_UNCERTAIN = {"comfort care heating", "quick service hvac", "clean air baltimore", "all weather heating and air", "fixed hvac annapolis",
                  "maryland heating and cooling ellicott city", "bel air hvac", "quality heating cooling plumbing & electrical", "handyman hvac",
                  "comfort air eldersburg md", "connect heating and cooling", "clean air heating near me", "heating and air conditioning co"}
PLACES = r"annapolis|glen burnie|baltimore|silver spring|frederick|easton|towson|beltsville|bowie|crofton|odenton|pasadena|ellicott|howard county|anne arundel|eldersburg|davidsonville|severna park|severn|columbia|rockville|waldorf|elkton|laurel|mt airy|\b21218\b"


def classify(term):
    t = " ".join(norm(term))
    has = lambda p: re.search(p, t) is not None
    if t in COMPETITOR:
        return ("Clearly irrelevant / off-target", "competitor", "another business named in the query")
    if t in ADDRESS_NAV:
        return ("Clearly irrelevant / off-target", "competitor", "business name + street address (Baltimore 21218), not an Ambient location; firm not confirmed online")
    if t in WITHHELD:
        return ("Ambiguous", "name_uncertain", "possible business name; withheld 2026-10-02 because no matching firm was confirmed")
    if t in NAME_UNCERTAIN:
        return ("Ambiguous", "name_uncertain", "may be a business name or a descriptive search")
    if has(r"webasto|dometic|\b(car|auto|truck|rv|camper|boat|marine|vehicle)\b"):
        return ("Clearly irrelevant / off-target", "non_hvac_equipment", "vehicle / marine heater")
    if has(r"fireplace|gas log|heatilator|heat n glo"):
        return ("Clearly irrelevant / off-target", "fireplace", "fireplace; not an approved service")
    if has(r"pellet stove|wood stove"):
        return ("Clearly irrelevant / off-target", "non_hvac_equipment", "solid-fuel stove; not an approved service")
    if has(r"water heater|hot water|tankless"):
        return ("Clearly irrelevant / off-target", "water_heater", "water heater; Tankless OUT of scope")
    if has(r"space heater|portable heater"):
        return ("Clearly irrelevant / off-target", "space_heater", "portable / space heater")
    if has(r"\boil\b|waste oil|beckett"):
        return ("Clearly irrelevant / off-target", "oil", "oil-fired equipment; Oil OUT of advertising scope (owner 2026-09-21)")
    if has(r"24 hour|24hr|24/7"):
        return ("Clearly irrelevant / off-target", "availability_24h", "asks for 24-hour service; Ambient is Mon-Fri 8-4 (settled 2026-10-02)")
    if has(r"fault|error|\bcode\b|codes|lockout|rollout|pilot light|green light|flashing"):
        return ("Informational", "diy_info", "fault-code / troubleshooting lookup; may hire after diagnosing (Monitor, settled 2026-10-01)")
    if has(r"radiant|baseboard"):
        return ("Direct heating repair", "baseboard_radiant", "radiant/baseboard system repair; Ambient capability not on record")
    if has(r"air condition|\ba c\b|\bac\b|central air|cooling") and not has(r"heat|furnace|boiler"):
        return ("Clearly irrelevant / off-target", "ac_cooling", "air conditioning only; cooling PAUSED by owner 2026-09-21")
    if has(r"not working|won t|not turning|not coming on|no heat|stopped working|not heating|blowing cold"):
        return ("No-heat", "commercial" if has(r"reznor") else "none", "symptom-led, ready to hire" + ("; Reznor unit heater, often commercial" if has(r"reznor") else ""))
    if has(r"install|installation|replace|replacement|new (furnace|boiler|system|unit)"):
        return ("Installation / replacement", "none", "installation / replacement")
    if has(r"plumb"):
        return ("Ambiguous", "plumbing", "plumbing-and-heating company search; heating need plausible")
    if has(r"duct"):
        return ("Ambiguous", "duct", "duct repair; capability not on record")
    if has(r"furnace") and has(r"repair|service|services|fix|failed"):
        return ("Furnace repair", "commercial" if has(r"commercial") else ("location_name" if has(PLACES) else "none"), "furnace repair / service")
    if has(r"\b(heating|heater|heat)\b") and has(r"repair|service|services|fix") and not has(r"\bhvac\b"):
        return ("Direct heating repair", "location_name" if has(PLACES) else "none", "heating repair / service")
    if has(r"rinnai|reznor|air handler"):
        return ("Ambiguous", "commercial" if has(r"reznor") else "none", "equipment named; capability or system type unconfirmed")
    if has(r"commercial"):
        return ("Ambiguous", "commercial", "commercial HVAC repair/service; repair capability for commercial not on record")
    if has(r"\bhvac\b|heating|cooling|\bheat\b|\bair\b|furnace|mechanical|climate|comfort"):
        return ("Ambiguous", "location_name" if has(PLACES) else "local_hvac", "local HVAC company / contractor / repair search; heating vs cooling not stated")
    return ("Ambiguous", "other", "unclassified")


ACTION = {"competitor": "EXACT negative", "non_hvac_equipment": "EXACT negative", "fireplace": "EXACT negative", "water_heater": "EXACT negative",
          "space_heater": "EXACT negative", "oil": "EXACT negative", "availability_24h": "EXACT negative", "ac_cooling": "EXACT negative"}

agg = collections.defaultdict(lambda: collections.defaultdict(float))
meta = collections.defaultdict(lambda: dict(ags=set(), kws=set(), rel=set(), dates=set()))
for r in ROWS:
    t = r["term"]
    for w, (a, b) in WIN.items():
        if a <= r["date"] <= b:
            for m in ("impr", "clicks", "cost"):
                agg[t][f"{w}_{m}"] += r[m]
                if r["kw_id"] == HR_PHRASE:
                    agg[t][f"hrp_{w}_{m}"] += r[m]
    meta[t]["ags"].add(r["ad_group"]); meta[t]["kws"].add(f"{r['kw_text']} ({r['kw_match']})"); meta[t]["rel"].add(r["st_match"]); meta[t]["dates"].add(r["date"])

out = []
for t, v in agg.items():
    cat, flag, why = classify(t)
    cov = sorted({c for g in meta[t]["ags"] for c in covering(g, t)})
    if flag in ACTION:
        verdict = "Already excluded" if cov else ACTION[flag] + " (new)"
    elif flag in ("baseboard_radiant", "duct", "commercial") or (flag == "none" and cat == "Ambiguous" and "capability" in why):
        verdict = "Keep - service confirmation"
    elif cat in ("Informational", "Ambiguous"):
        verdict = "Monitor"
    else:
        verdict = "Keep"
    if verdict == "Monitor" and cov:
        verdict = "Already excluded"
    out.append(dict(search_term=t, category=cat, review_flag=flag, reason=why, verdict=verdict, coverage="; ".join(cov[:3]),
                    ad_groups="; ".join(sorted(AG.get(g, {}).get("name", g)[7:] for g in meta[t]["ags"])), triggering_keywords="; ".join(sorted(meta[t]["kws"])),
                    match_relationship="; ".join(sorted(meta[t]["rel"])), first_seen=min(meta[t]["dates"]), last_seen=max(meta[t]["dates"]),
                    **{k: round(v.get(k, 0), 2) for k in [f"{w}_{m}" for w in WIN for m in ("impr", "clicks", "cost")]},
                    hr_phrase_impr=round(v.get("hrp_all_impr", 0)), hr_phrase_cost=round(v.get("hrp_all_cost", 0), 2)))
out.sort(key=lambda x: (-x["all_cost"], -x["all_impr"], x["search_term"]))

# ---------------- negative drafts ----------------
cands = [dict(text=x["search_term"], match="EXACT", basis=x["reason"], seen=f"{x['first_seen']}..{x['last_seen']}", impr=x["all_impr"], cost=x["all_cost"])
         for x in out if x["verdict"].endswith("(new)")]
cands += [dict(text="g & g mechanical", match="PHRASE", basis="query names a business + Baltimore street address, recurs on 4 days; 14 words, too long for EXACT",
               seen="", impr=0, cost=0.0),
          dict(text="oil", match="PHRASE", basis="owner put oil OUT of advertising scope 2026-09-21; oil queries keep recurring in new wordings", seen="", impr=0, cost=0.0),
          dict(text="pellet stove", match="PHRASE", basis="pellet stoves are not an approved service; recurring wordings", seen="", impr=0, cost=0.0)]
for c in cands:
    if c["match"] == "PHRASE":
        hits = [x for x in out if blocks(c["text"], "PHRASE", norm(x["search_term"]))]
        c["impr"] = sum(x["all_impr"] for x in hits); c["cost"] = round(sum(x["all_cost"] for x in hits), 2)
        c["observed_terms_blocked"] = len(hits)
        c["blocks_non_irrelevant_terms"] = sorted({x["search_term"] for x in hits if x["category"] != "Clearly irrelevant / off-target"})
        firsts = sorted(x["first_seen"] for x in hits); lasts = sorted(x["last_seen"] for x in hits)
        c["seen"] = f"{firsts[0]}..{lasts[-1]}" if hits else ""
    c["conflicts_with_positive"] = [f"{AG[k['ad_group']]['name'][7:]} {k['match']} [{k['text']}]" for k in POS
                                    if blocks(c["text"], c["match"], norm(k["text"]))]
    c["never_negate_word"] = [w for w in ("near me", "cost", "price", "pricing", "quote", "best", "local", "hire", "emergency") if w in c["text"]]

# ---------------- requested-category probes (hypothetical wordings, not observed) ----------------
HR, FR = "204129717007", "199797580706"
PROBES = ["space heater repair", "portable heater repair", "baseboard heater repair", "electric baseboard heater repair", "radiant floor heating repair",
          "water heater repair", "hot water heater repair near me", "tankless water heater repair", "plumber near me", "plumbing and heating near me",
          "fireplace repair near me", "pellet stove repair", "oil furnace repair near me", "oil burner repair", "webasto repair", "rv furnace repair",
          "ac repair near me", "air conditioner repair", "central air repair", "heat pump repair", "boiler repair", "garage heater repair",
          "furnace repair cost", "heating repair near me", "best furnace repair near me", "emergency heating repair", "carrier furnace repair",
          "trane furnace repair", "york furnace repair", "lennox furnace repair", "furnace repair annapolis"]
probes = [dict(probe=p, blocked_heating_repair=covering(HR, p)[:2], blocked_furnace_repair=covering(FR, p)[:2], literal_reach=literal_reach(p)[:3]) for p in PROBES]

# ---------------- aggregates ----------------
CATS = ["Direct heating repair", "Furnace repair", "No-heat", "Installation / replacement", "Informational", "Ambiguous", "Clearly irrelevant / off-target"]
summ = {"rows": len(ROWS), "distinct_terms": len(out), "verdicts": dict(collections.Counter(x["verdict"] for x in out)),
        "flags": dict(collections.Counter(x["review_flag"] for x in out))}
for w in WIN:
    summ[f"by_category_{w}"] = {c: dict(terms=sum(1 for x in out if x["category"] == c and x[f"{w}_impr"] > 0), impr=round(sum(x[f"{w}_impr"] for x in out if x["category"] == c)),
                                        clicks=round(sum(x[f"{w}_clicks"] for x in out if x["category"] == c)), cost=round(sum(x[f"{w}_cost"] for x in out if x["category"] == c), 2))
                                for c in CATS}
    summ[f"visible_{w}"] = {m: round(sum(x[f"{w}_{m}"] for x in out), 2) for m in ("impr", "clicks", "cost")}
summ["by_flag_all"] = {f: dict(terms=n, impr=round(sum(x["all_impr"] for x in out if x["review_flag"] == f)), cost=round(sum(x["all_cost"] for x in out if x["review_flag"] == f), 2),
                               excluded=sum(1 for x in out if x["review_flag"] == f and x["verdict"] == "Already excluded"))
                       for f, n in collections.Counter(x["review_flag"] for x in out).items()}
hrp = collections.defaultdict(lambda: collections.Counter())
for r in ROWS:
    if r["kw_id"] == HR_PHRASE:
        for w, (a, b) in WIN.items():
            if a <= r["date"] <= b:
                hrp[w][r["st_match"]] += r["impr"]
                hrp[w]["literal_contains_heating_repair_impr"] += r["impr"] if "heating repair" in " ".join(norm(r["term"])) else 0
                hrp[w]["cost"] += r["cost"]; hrp[w]["clicks"] += r["clicks"]
                hrp[w]["cat:" + classify(r["term"])[0]] += r["cost"]
summ["heating_repair_phrase_visible"] = {w: {k: round(v, 2) for k, v in c.items()} for w, c in hrp.items()}
summ["candidates"] = cands
summ["probes"] = probes
(CD / "snapshots" / "repair-search-term-analysis-2026-10-05.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
with (CD / "exports" / "repair-search-term-verdicts-2026-10-05.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(out[0].keys())); wr.writeheader(); wr.writerows(out)

print(json.dumps({k: v for k, v in summ.items() if k not in ("probes", "candidates")}, indent=1))
print("\nCANDIDATES:")
for c in cands:
    print(" ", json.dumps(c, default=str))
print("\nPROBES:")
for p in probes:
    print(f"  {p['probe']:34s} HR:{p['blocked_heating_repair'] or '-'} FR:{p['blocked_furnace_repair'] or '-'} reach:{p['literal_reach'] or '-'}")
