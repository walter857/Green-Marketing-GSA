#!/usr/bin/env python3
"""Ambient | 2026-10-07 | Sept 1 - Oct 7 search-term verdicts (Search + PMax), live negative coverage, overblock review and
EXACT-only negative candidates. No API calls.

Inputs: snapshots/snapshot-2026-10-07.json, exports/search-terms-2026-10-07.jsonl, exports/pmax-search-terms-2026-10-07.jsonl,
exports/term-manual-labels-2026-10-07.json (manual intent calls made while reading every term; optional).
Periods: SEP 2026-09-01..30, OCT 2026-10-01..06 (complete), OCT7 2026-10-07 (PARTIAL).
Negative model: Google negatives match casing-insensitively but never close variants, synonyms, plurals or reorderings.
EXACT = whole query equal; PHRASE = contiguous; BROAD = every token present in any order.
Outputs: exports/search-term-verdicts-2026-10-07.csv, exports/negative-candidates-2026-10-07.json,
snapshots/search-term-analysis-2026-10-07.json. `--review CAMPAIGN_ID` prints that campaign's terms grouped by ad group.
"""
from __future__ import annotations

import collections
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CD = ROOT / "clients" / "ambient-cooling-heating"
S = json.loads((CD / "snapshots" / "snapshot-2026-10-07.json").read_text(encoding="utf-8"))
ROWS = [json.loads(l) for l in (CD / "exports" / "search-terms-2026-10-07.jsonl").read_text(encoding="utf-8").splitlines()]
PROWS = [json.loads(l) for l in (CD / "exports" / "pmax-search-terms-2026-10-07.jsonl").read_text(encoding="utf-8").splitlines()]
MAN_PATH = CD / "exports" / "term-manual-labels-2026-10-07.json"
MAN = json.loads(MAN_PATH.read_text(encoding="utf-8")) if MAN_PATH.exists() else {}
CAMPS, AGS = S["campaigns"], S["ad_groups"]
LIVE10 = ["24257819463", "24257819466", "24132507744", "24268690038", "24268690041",
          "24279798229", "24274160783", "24132507747", "24295088845", "24318905515"]
PMAX = {"24295088845", "24318905515"}
W = {"SEP": ("2026-09-01", "2026-09-30"), "OCT": ("2026-10-01", "2026-10-06"), "OCT7P": ("2026-10-07", "2026-10-07")}

# campaign service map (what each campaign is for) -> used for "another approved service" routing calls
SERVICE_OF = {
    "24257819463": "repair", "24257819466": "install_replace", "24132507744": "boiler", "24268690038": "heat_pump",
    "24268690041": "thermostat", "24279798229": "maintenance", "24274160783": "geothermal", "24132507747": "commercial",
    "24295088845": "replacement_pmax", "24318905515": "heat_pump_geo_pmax",
}


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


mem = S["shared_set_members"]
acct_sets = [x["shared_set"].split("/")[-1] for x in S["customer_negative_criteria"] if x["type"] == "NEGATIVE_KEYWORD_LIST"]
ACCT = [("account-level", m["text"], m["match"]) for sid in acct_sets for m in mem.get(sid, [])]
ATT = collections.defaultdict(list)
for a in S["campaign_shared_sets"]:
    if a["status"] == "ENABLED":
        ATT[a["campaign"]] += [(f"shared {a['shared_set']}", m["text"], m["match"]) for m in mem.get(a["shared_set"], [])]
CNEG = collections.defaultdict(list)
for cid, v in S["campaign_criteria"].items():
    CNEG[cid] = [("campaign", x["text"], x["match"]) for x in v.get("KEYWORD", []) if x["neg"]]
AGNEG, POS = collections.defaultdict(list), collections.defaultdict(list)
for k in S["keywords"]:
    (AGNEG[k["ad_group"]].append(("ad group", k["text"], k["match"])) if k["neg"] else POS[k["ad_group"]].append(k))


def covering(cid, gid, term):
    q = norm(term)
    layers = ACCT + ATT[cid] + CNEG[cid] + (AGNEG[gid] if gid else [])
    return [f"{l}: {m} [{t}]" for (l, t, m) in layers if blocks(t, m, q)]


SERVICE = r"\b(repair|repairs|fix|install|installation|installed|installer|installers|replace|replacement|service|services|servicing|tune|maintenance|cost|costs|price|prices|pricing|quote|estimate|contractor|contractors|company|companies|technician)\b"
COMPETITOR = {
    "booths hvac", "boothe's heating air plumbing & drains", "tevis modern comfort", "s f jones heating and cooling", "moon air elkton",
    "dodge heating and air", "max air heating & a c inc", "coastal hvac annapolis", "carroll mechanical columbia md", "allpro hvac", "b&d hvac",
    "belair engineering hvac", "del air heating", "go ecco climate control", "home team heating and cooling", "howard mechanical hvac",
    "joey taylor hvac", "maryland mechanical heating & cooling", "right way heating", "scotty's heating and cooling", "stanton hvac",
    "stivers hvac inc", "triple eee hvac", "bnb heating and cooling", "call dad", "classic air waldorf md", "climate care crofton md",
    "coastal heat and air", "cold comfort hvac rockville md", "compass energy laurel de", "falcon hvac", "frosty heating and air conditioning",
    "grove hvac maryland", "harbor point heating and air", "honest air mt airy", "hope plumbing heating and cooling", "jiffy hvac", "minnick hvac",
    "ocean air hvac", "powell and turner hvac", "pro tech hvac", "smock heating & air", "southern maryland heating and air waldorf md",
    "vito hvac", "xzavier hvac solutions llc baltimore reviews",
}
# withheld 2026-10-02 (names not confirmed as a business) - stay withheld unless new evidence
WITHHELD_1002 = {"b&d hvac", "stanton hvac", "coastal heat and air", "harbor point heating and air", "aube thermostat",
                 "what is geothermal heating", "what is a furnace tune up", "do plumbers do boilers"}


def has_model(t):
    for tok in t.split():
        if len(tok) >= 4 and re.search(r"\d", tok) and re.search(r"[a-z]", tok) and not re.fullmatch(r"\d+(k|st|nd|rd|th|s)", tok):
            return True
    return False


def classify(term, cid):
    """-> (category, reason, bucket, confidence). category uses the 2026-10-07 brief's nine classes."""
    t = " ".join(norm(term))
    has = lambda p: re.search(p, t) is not None
    svc = has(SERVICE)
    if t in MAN:
        return tuple(MAN[t])
    if t in COMPETITOR:
        return ("Competitor navigation", "another HVAC company's name (navigational)", "competitor", "high")
    if has(r"\bwebasto\b|\bdometic\b|\b(car|auto|truck|rv|camper|boat|marine|vehicle)\b"):
        return ("Clearly irrelevant", "vehicle / RV / marine equipment, not a home system", "vehicle", "high")
    if has(r"suntouch|heated floor|floor heat|radiant floor") and not svc:
        return ("Clearly irrelevant", "electric floor-heating product, not an Ambient service on record", "floor_heat", "high")
    if has(r"fireplace|gas log|heatilator|heat n glo"):
        return ("Clearly irrelevant", "fireplace; not an approved service", "fireplace", "high")
    if has(r"pellet stove|wood stove"):
        return ("Clearly irrelevant", "solid-fuel stove; not an approved service", "pellet_stove", "high")
    if has(r"water heater|hot water|tankless"):
        return ("Clearly irrelevant", "water heater; Tankless/water heaters OUT of approved scope", "water_heater", "high")
    if has(r"\b(job|jobs|career|careers|salary|hiring|apprentice|apprenticeship|school|training|certification|license exam|technician jobs)\b"):
        return ("Employment", "employment / training", "employment", "high")
    if has(r"24 hour|24hr|24/7|overnight|after hours|open now|open late|late night|weekend|sunday|saturday"):
        return ("Hiring intent", "availability wording; ads serve only Mon-Fri business hours when next-available booking is offered (no 24/7 claim)", "availability", "medium")
    if has(r"thermostat") and has(r"setup|set up|wiring|wire|wires|reset|program|programming|manual|instructions|battery|batteries|blank|troubleshoot|how to|myself"):
        return ("DIY/informational", "thermostat setup / wiring / programming, DIY rather than hiring", "thermostat_diy", "medium")
    if (has_model(t) or has(r"\b\d{2,6}k? ?btu\b|\bbtu\b") or has(r"^thermostat \d+$")) and not has(r"\b(repair|fix|install|installation|installed|replace|replacement|service|technician|cost|price|quote)\b"):
        return ("Parts/model shopping", "bare model / part / capacity lookup, no service-buying word", "model", "medium")
    if has(r"troubleshoot|fault|error|lockout|rollout|code \d|\bcodes?\b|flashing|green light|pilot light|reset"):
        return ("DIY/informational", "fault-code / troubleshooting lookup; may hire after diagnosing", "diy", "medium")
    if has(r"\boil\b|waste oil|kerosene|propane tank"):
        return ("Clearly irrelevant", "oil-fired equipment; Oil OUT of advertising scope (owner 2026-09-21)", "oil", "high")
    if has(r"^(how|what|why|when|which|can|does|do|is|are|should)\b") and not has(r"how much|cost|price|not (turning|working)|won t|no heat|near me"):
        return ("DIY/informational", "research question with no hire signal", "info", "medium")
    if has(r"how much|cost|price|prices|pricing|quote|estimate"):
        return ("Commercial research", "price research; a buying step - protected", "price", "high")
    if has(r"geotherm|^geo\b|ground source"):
        return ("Hiring intent" if SERVICE_OF.get(cid) in ("geothermal", "heat_pump_geo_pmax") else "Another approved service",
                "geothermal interest", "geothermal", "medium")
    if has(r"emergenc|urgent|same day"):
        return ("Hiring intent", "urgent business-hours repair intent (next-available booking)", "emergency", "high")
    if has(r"not working|won t turn|not turning|no heat|stopped working|not heating|blowing cold|not blowing"):
        return ("Hiring intent", "symptom-led; ready to hire", "no_heat", "high")
    if has(r"air condition|\ba ?c\b|\bac\b|central air|cooling") and not has(r"heat|furnace|boiler|hvac"):
        return ("Another approved service", "air conditioning only; cooling campaigns PAUSED by owner 2026-09-21", "ac", "high")
    if has(r"duct"):
        return ("Ambiguous", "ductwork; capability not in approved records", "duct", "medium")
    if has(r"thermostat"):
        return ("Hiring intent" if svc else "Commercial research", "thermostat product or service", "thermostat", "medium")
    if has(r"install|installation|replace|replacement|new (furnace|boiler|heat pump|system|unit)"):
        return ("Hiring intent", "installation / replacement", "install", "high")
    if has(r"maintenance|tune ?up|inspection|cleaning|clean"):
        return ("Hiring intent", "maintenance / tune-up / inspection / cleaning", "maintenance", "high")
    if has(r"furnace|boiler|heat pump|heating|heater") and has(r"repair|fix|service"):
        return ("Hiring intent", "heating/furnace/boiler/heat-pump repair or service", "repair", "high")
    if has(r"\bhvac\b|heating|cooling|\bheat\b|air\b|mechanical|climate|comfort|plumbing") and (has(r"near me|company|companies|contractor|contractors|service|services|in my area|local") or len(t.split()) <= 4):
        return ("Hiring intent", "local HVAC-contractor search; service not stated", "local_hvac", "medium")
    if has(r"furnace|boiler|heat pump|mini split|ductless"):
        return ("Ambiguous", "equipment named without a service word", "equipment_bare", "medium")
    return ("Ambiguous", "unclassified - manual review", "other", "low")


# service fit by campaign (does a hiring-intent query belong to THIS campaign's service?)
def routing(term, cid):
    t = " ".join(norm(term))
    has = lambda p: re.search(p, t) is not None
    svc = SERVICE_OF.get(cid)
    if svc in ("repair",) and has(r"\b(install|installation|replace|replacement|new)\b") and not has(r"repair|fix|not working|no heat"):
        return "install/replace query in Repair"
    if svc in ("install_replace", "replacement_pmax") and has(r"\brepair|fix|not working|no heat|broken\b") and not has(r"replace|install|new"):
        return "repair query in Install/Replace"
    if svc in ("maintenance",) and has(r"\brepair|fix|not working|no heat|broken\b") and not has(r"maint|tune|inspect|clean|service plan"):
        return "repair query in Maintenance"
    return ""


VERDICT = {"competitor": "EXACT candidate", "vehicle": "EXACT candidate", "floor_heat": "EXACT candidate", "fireplace": "EXACT candidate",
           "pellet_stove": "EXACT candidate", "water_heater": "EXACT candidate", "employment": "EXACT candidate",
           "availability": "Keep (monitor)", "thermostat_diy": "EXACT candidate", "model": "EXACT candidate", "oil": "EXACT candidate",
           "ac": "EXACT candidate", "info": "EXACT candidate", "diy": "Monitor", "price": "Keep", "geothermal": "Keep",
           "emergency": "Keep", "no_heat": "Keep", "duct": "Monitor (service confirmation)", "thermostat": "Keep",
           "install": "Keep", "maintenance": "Keep", "repair": "Keep", "local_hvac": "Keep (monitor)", "equipment_bare": "Monitor",
           "other": "Monitor", "manual_keep": "Keep", "manual_negative": "EXACT candidate", "manual_monitor": "Monitor",
           "manual_route": "Routing review", "competitor_withheld": "Monitor (name unconfirmed)"}


def window_of(d):
    for w, (a, b) in W.items():
        if a <= d <= b:
            return w
    return None


agg = collections.defaultdict(lambda: {w: collections.Counter() for w in W})
meta, dates = {}, collections.defaultdict(set)
for r in ROWS:
    key = (r["campaign"], r["ad_group"], r["term"], r["kw_id"], r["kw_text"], r["kw_match"], r["st_match"])
    meta[key] = r["status"]
    dates[key].add(r["date"])
    w = window_of(r["date"])
    if w:
        for m in ("impr", "clicks", "cost", "conv", "all_conv"):
            agg[key][w][m] += r[m]
for r in PROWS:
    key = (r["campaign"], "", r["term"], "", "(PMax)", "", "")
    meta[key] = ""
    dates[key].add(r["date"])
    w = window_of(r["date"])
    if w:
        for m in ("impr", "clicks", "cost", "conv", "all_conv"):
            agg[key][w][m] += r[m]

out = []
for key, v in agg.items():
    cid, gid, term, kid, kwt, kwm, stm = key
    cat, why, bucket, conf = classify(term, cid)
    tnorm = " ".join(norm(term))
    if tnorm in WITHHELD_1002 and bucket in ("competitor", "info"):
        bucket, why = "competitor_withheld" if bucket == "competitor" else "manual_monitor", why + " (withheld 2026-10-02, still unconfirmed)"
    route = routing(term, cid) if cat == "Hiring intent" else ""
    camp_status = CAMPS.get(cid, {}).get("status", "?")
    ag_status = AGS.get(gid, {}).get("status", "ENABLED" if cid in PMAX else "?")
    live = cid in LIVE10 and camp_status == "ENABLED"
    hit = covering(cid, gid, term) if live else []
    verdict = VERDICT[bucket]
    if route and verdict.startswith("Keep"):
        verdict = "Routing review"
    if not live:
        verdict, cov = "History only (campaign not live)", "n/a"
    elif hit:
        cov = "covered now"
        if verdict == "EXACT candidate":
            verdict = "Keep excluded (already covered)"
        elif verdict.startswith("Keep") or verdict in ("Monitor", "Routing review"):
            verdict = "OVERBLOCK REVIEW (hiring/ambiguous query is excluded)"
    else:
        cov = "not covered"
    if live and ag_status not in ("ENABLED",) and verdict == "EXACT candidate":
        verdict, cov = "History only (ad group paused)", cov + "; ad group paused"
    tot = {m: round(sum(v[w][m] for w in W), 2) for m in ("impr", "clicks", "cost", "conv", "all_conv")}
    out.append(dict(first_seen=min(dates[key]), last_seen=max(dates[key]), campaign=CAMPS.get(cid, {}).get("name", cid), campaign_id=cid,
                    campaign_status=camp_status, ad_group=AGS.get(gid, {}).get("name", "(PMax - no ad group)" if cid in PMAX else gid),
                    ad_group_id=gid, ad_group_status=ag_status, search_term=term, triggering_keyword=kwt, keyword_match_type=kwm,
                    keyword_criterion_id=kid, search_term_match_relationship=stm, term_status=meta[key],
                    **{f"{w}_{m}": (round(v[w][m], 2) if m == "cost" else v[w][m]) for w in W for m in ("impr", "clicks", "cost", "conv", "all_conv")},
                    total_impr=tot["impr"], total_clicks=tot["clicks"], total_cost=tot["cost"], recorded_conversions=tot["conv"],
                    all_conversions=tot["all_conv"], category=cat, reason=why, bucket=bucket, routing=route, coverage=cov,
                    covering_negatives=" | ".join(hit[:3]), verdict=verdict, confidence=conf))

if "--review" in sys.argv:
    cid = sys.argv[sys.argv.index("--review") + 1]
    flt = sys.argv[sys.argv.index("--review") + 2] if len(sys.argv) > sys.argv.index("--review") + 2 else ""
    rows = [x for x in out if x["campaign_id"] == cid]
    by = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.Counter()))
    info = {}
    for x in rows:
        k = x["search_term"]
        by[x["ad_group"]][k].update(dict(i=x["total_impr"], c=x["total_clicks"], s=x["total_cost"], o=x["OCT_impr"] + x["OCT7P_impr"]))
        info[(x["ad_group"], k)] = (x["bucket"], x["verdict"][:14], x["triggering_keyword"], x["keyword_match_type"][:2])
    for ag in sorted(by):
        print(f"\n## {ag}")
        for k, m in sorted(by[ag].items(), key=lambda z: (-z[1]["s"], -z[1]["i"], z[0])):
            b, vd, kw, mt = info[(ag, k)]
            if flt and flt not in vd and flt not in b:
                continue
            print(f"{m['i']:>3}i {m['c']}c ${m['s']:<6.2f} o{m['o']:<2} {b[:11]:11} {vd:14} | {k}  <{kw} {mt}>")
    sys.exit(0)

# ---------------- candidates: one per (live campaign, full query) ----------------
cands = {}
for x in out:
    if x["verdict"] != "EXACT candidate":
        continue
    k = (x["campaign_id"], x["search_term"])
    c = cands.setdefault(k, dict(query=x["search_term"], display=f"[{x['search_term']}]", match_type="EXACT", campaign=x["campaign"],
                                 campaign_id=x["campaign_id"], scope="campaign", category=x["category"], bucket=x["bucket"], reason=x["reason"],
                                 confidence=x["confidence"], impr=0, clicks=0, cost=0.0, sep_cost=0.0, oct_cost=0.0, ad_groups=set(),
                                 keywords=set(), first_seen=x["first_seen"], last_seen=x["last_seen"]))
    c["impr"] += x["total_impr"]
    c["clicks"] += x["total_clicks"]
    c["cost"] = round(c["cost"] + x["total_cost"], 2)
    c["sep_cost"] = round(c["sep_cost"] + x["SEP_cost"], 2)
    c["oct_cost"] = round(c["oct_cost"] + x["OCT_cost"] + x["OCT7P_cost"], 2)
    if x["ad_group_id"]:
        c["ad_groups"].add(x["ad_group_id"])
    if x["triggering_keyword"] and x["triggering_keyword"] != "(PMax)":
        c["keywords"].add(f"{x['triggering_keyword']} ({x['keyword_match_type']}, {x['keyword_criterion_id']})")
    c["first_seen"], c["last_seen"] = min(c["first_seen"], x["first_seen"]), max(c["last_seen"], x["last_seen"])

valid, too_long, conflicts = [], [], []
for c in cands.values():
    c["ad_groups"], c["keywords"] = sorted(c["ad_groups"]), sorted(c["keywords"])
    words = norm(c["query"])
    c["words"], c["chars"] = len(words), len(c["query"])
    clash = [f"{AGS.get(k['ad_group'], {}).get('name')} {k['match']} {k['text']}" for k in S["keywords"]
             if not k["neg"] and k["campaign"] == c["campaign_id"] and k["status"] == "ENABLED" and norm(k["text"]) == words]
    c["buyer_conflict_check"] = ("BLOCKS POSITIVE: " + "; ".join(clash)) if clash else "none: blocks only this full query; longer buyer queries stay eligible"
    c["priority"] = "P1 spent money" if c["cost"] > 0 else ("P2 recurring (>=3 impr)" if c["impr"] >= 3 else "P3 low volume")
    (too_long if (c["words"] > 10 or c["chars"] > 80) else conflicts if clash else valid).append(c)
valid.sort(key=lambda c: (c["campaign_id"], c["priority"], -c["cost"], -c["impr"], c["query"]))

with (CD / "exports" / "search-term-verdicts-2026-10-07.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    wr.writeheader()
    for x in sorted(out, key=lambda z: (z["campaign_id"] not in LIVE10, z["campaign_id"], z["ad_group"], -z["total_cost"], -z["total_impr"], z["search_term"])):
        wr.writerow(x)
(CD / "exports" / "negative-candidates-2026-10-07.json").write_text(json.dumps(dict(valid=valid, too_long=too_long, conflicts=conflicts), indent=1, default=list), encoding="utf-8")
live_rows = [x for x in out if x["campaign_id"] in LIVE10]
summ = dict(rows=len(out), live_rows=len(live_rows), distinct_terms_live=len({x["search_term"] for x in live_rows}),
            verdicts_live=dict(collections.Counter(x["verdict"] for x in live_rows)),
            categories_live=dict(collections.Counter(x["category"] for x in live_rows)),
            candidates=len(valid), too_long=len(too_long), conflicts=len(conflicts),
            candidates_by_campaign=dict(collections.Counter(c["campaign_id"] for c in valid)),
            candidates_by_bucket=dict(collections.Counter(c["bucket"] for c in valid)),
            candidate_cost=round(sum(c["cost"] for c in valid), 2))
for w in W:
    summ[f"{w}|live|visible"] = {m: round(sum(x[f"{w}_{m}"] for x in live_rows), 2) for m in ("impr", "clicks", "cost")}
    cc = collections.Counter()
    for x in live_rows:
        cc[x["category"]] += x[f"{w}_cost"]
    summ[f"{w}|live|cost_by_category"] = {k: round(v, 2) for k, v in cc.items()}
(CD / "snapshots" / "search-term-analysis-2026-10-07.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
print(json.dumps(summ, indent=1))
