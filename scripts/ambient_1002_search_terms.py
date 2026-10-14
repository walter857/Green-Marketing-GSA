#!/usr/bin/env python3
"""Ambient | 2026-10-02 | Full Sep 1 - Oct 2 search-term verdicts, negative coverage and EXACT-only candidates. No API calls.

Inputs: snapshots/snapshot-2026-10-02.json + exports/search-terms-2026-10-02.jsonl (both read 2026-10-02 07:10 ET).
Periods kept separate: SEP 2026-09-01..30, OCT 2026-10-01..today (today PARTIAL; 10-02 had no rows at the read).
Paused campaigns are history only (no negatives proposed). Negative model as in ambient_1001_search_terms.py (Google: negatives
account for casing and misspellings, never close variants, synonyms, plurals or reorderings).
Outputs: exports/search-term-verdicts-2026-10-02.csv, exports/negative-candidates-2026-10-02.json,
         snapshots/search-term-analysis-2026-10-02.json; `--review` prints terms that need a manual intent call.
"""
from __future__ import annotations
import csv, json, re, collections, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CD = ROOT / "clients" / "ambient-cooling-heating"
S = json.loads((CD / "snapshots" / "snapshot-2026-10-02.json").read_text(encoding="utf-8"))
ROWS = [json.loads(l) for l in (CD / "exports" / "search-terms-2026-10-02.jsonl").read_text(encoding="utf-8").splitlines()]
CAMPS, AGS = S["campaigns"], S["ad_groups"]
W = {"SEP": ("2026-09-01", "2026-09-30"), "OCT": ("2026-10-01", "2026-10-31")}
CREATED = {"12252013691": "2026-09-26 16:15", "12249470554": "2026-09-26 16:36 (+2 on 09-27)", "11252984411": "before 2026-09-01"}


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
acct = [("account-level", m["text"], m["match"], CREATED.get(sid, "?")) for sid in S["account_level_sets"] for m in mem.get(sid, [])]
att = collections.defaultdict(list)
for a in S["attachments"]:
    if a["status"] == "ENABLED":
        att[a["campaign"]] += [(f"shared {a['set']}", m["text"], m["match"], CREATED.get(a["set"], "?")) for m in mem.get(a["set"], [])]
cneg = collections.defaultdict(list)
for cid, v in S["campaign_criteria"].items():
    cneg[cid] = [("campaign", x["text"], x["match"], "build") for x in v.get("KEYWORD", []) if x["neg"]]
agneg, pos = collections.defaultdict(list), collections.defaultdict(list)
for k in S["keywords"]:
    (agneg[k["ad_group"]].append(("ad group", k["text"], k["match"], "build")) if k["negative"] else pos[k["ad_group"]].append(k))


def covering(cid, gid, term):
    q = norm(term)
    return [f"{l}: {m} [{t}] ({c})" for (l, t, m, c) in acct + att[cid] + cneg[cid] + agneg[gid] if blocks(t, m, q)]


SERVICE = r"\b(repair|repairs|fix|install|installation|installed|installer|installers|replace|replacement|service|services|servicing|tune|maintenance|cost|costs|price|prices|pricing|quote|estimate|contractor|company|companies|technician)\b"
COMPETITOR = {
    # high-confidence other-company navigation (distinctive proper name + trade term), observed in this corpus
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
NAME_UNCERTAIN = {"comfort care heating", "quick service hvac", "clean air baltimore", "all weather heating and air", "fixed hvac annapolis",
                  "maryland heating and cooling ellicott city", "bel air hvac", "quality heating cooling plumbing & electrical", "handyman hvac"}
EXTRA = json.loads((CD / "exports" / "term-manual-labels-2026-10-02.json").read_text(encoding="utf-8")) if (CD / "exports" / "term-manual-labels-2026-10-02.json").exists() else {}
# 2026-10-02 08:30 ET: Maintenance and Commercial launch under the staged authorization, so neither is "no-serve" any more.
# The residential HVAC Installation group in 24132507747 stays PAUSED and is handled by the ad-group-paused rule.
NO_SERVE = {}
LOCAL_HVAC_FLAGGED = {"hvac annapolis", "hvac in annapolis", "hvac glen burnie md", "hvac companies near me", "hvac contractor near me", "annapolis hvac companies"}


def has_model(t):
    for tok in t.split():
        if len(tok) >= 4 and re.search(r"\d", tok) and re.search(r"[a-z]", tok) and not re.fullmatch(r"\d+(k|st|nd|rd|th|s)", tok):
            return True
    return False


def classify(term, cid):
    t = " ".join(norm(term))
    has = lambda p: re.search(p, t) is not None
    svc = has(SERVICE)
    if t in EXTRA:
        return tuple(EXTRA[t])
    if t in COMPETITOR:
        return ("Clearly irrelevant", "another HVAC company's name (navigational)", "competitor", "high")
    if has(r"\bwebasto\b|\bdometic\b|\b(car|auto|truck|rv|camper|boat|marine|vehicle)\b"):
        return ("Clearly irrelevant", "vehicle / RV / marine equipment, not a home system", "vehicle", "high")
    if has(r"suntouch|heated floor|floor heat|radiant floor") and not svc:
        return ("Other equipment repair", "electric floor-heating product / thermostat, not an Ambient service on record", "floor_heat", "high")
    if has(r"fireplace|gas log|heatilator|heat n glo"):
        return ("Other equipment repair", "fireplace; not an approved service", "fireplace", "high")
    if has(r"pellet stove|wood stove"):
        return ("Other equipment repair", "solid-fuel stove; not an approved service", "pellet_stove", "high")
    if has(r"water heater|hot water|tankless"):
        return ("Other equipment repair", "water heater; Tankless OUT of scope", "water_heater", "high")
    if has(r"\b(job|jobs|career|salary|hiring|apprentice|school|training|certification|license exam)\b"):
        return ("Clearly irrelevant", "employment / training", "employment", "high")
    if has(r"24 hour|24hr|24/7|overnight|after hours|open now|open late|late night|weekend|sunday|saturday"):
        return ("Emergency repair", "requests availability outside Mon-Fri 08-16, which Ambient does not offer", "availability", "medium")
    if has(r"thermostat") and has(r"setup|set up|wiring|wire|wires|reset|program|manual|instructions|battery|batteries|blank|not working|troubleshoot|how to|replacement dometic"):
        return ("Informational or DIY", "thermostat setup / wiring / troubleshooting, DIY rather than hiring", "thermostat_diy", "medium")
    if (has_model(t) or has(r"\b\d{2,6}k? ?btu\b|\bbtu\b") or has(r"^thermostat \d+$")) and not has(r"\b(repair|fix|install|installation|installed|replace|replacement|service|technician|cost|price|quote)\b"):
        return ("Informational or DIY", "bare model / part / capacity lookup (product or spec shopping), no service-buying word", "model", "medium")
    if has(r"troubleshoot|fault|error|lockout|rollout|code \d|\bcodes?\b|flashing|green light|pilot light|reset"):
        return ("Informational or DIY", "fault-code / troubleshooting lookup; may hire after diagnosing", "diy", "medium")
    if has(r"\boil\b|waste oil|kerosene|propane tank"):
        return ("Furnace repair", "oil-fired equipment; Oil OUT of advertising scope (owner 2026-09-21)", "oil", "high")
    if has(r"^(how|what|why|when|which|can|does|is|are)\b") and not has(r"how much|cost|price|not (turning|working)|won t|no heat"):
        return ("Informational or DIY", "research question with no hire signal", "info", "medium")
    if has(r"how much|cost|price|prices|pricing|quote|estimate"):
        return ("Installation or replacement" if has(r"new|install|replace|replacement|system|unit|furnace|heat pump|boiler|ac\b|air condition") else "Ambiguous",
                "price research; a buying step - protected", "price", "high")
    if has(r"geotherm|^geo\b"):
        return ("Ambiguous", "geothermal interest", "geothermal", "medium")
    if has(r"emergenc|urgent|same day"):
        return ("Emergency repair", "urgent business-hours repair intent (Ambient books next available visit)", "emergency", "high")
    if has(r"not working|won t turn|not turning|no heat|stopped working|not heating|blowing cold"):
        return ("No-heat repair", "symptom-led; ready to hire", "no_heat", "high")
    if has(r"air condition|\ba ?c\b|\bac\b|central air|cooling") and not has(r"heat|furnace|boiler"):
        return ("Other equipment repair", "air conditioning only; cooling PAUSED by owner 2026-09-21", "ac", "high")
    if has(r"duct"):
        return ("Other equipment repair", "ductwork; capability not in approved records", "duct", "medium")
    if has(r"thermostat"):
        return ("Other equipment repair" if not svc else "Installation or replacement", "thermostat product or service", "thermostat", "medium")
    if t in NAME_UNCERTAIN:
        return ("Ambiguous", "may be a business name or a descriptive search", "name_uncertain", "low")
    if has(r"install|installation|replace|replacement|new (furnace|boiler|heat pump|system|unit)"):
        return ("Installation or replacement", "installation / replacement", "install", "high")
    if has(r"maintenance|tune ?up|inspection|cleaning|clean"):
        return ("Maintenance", "maintenance / tune-up / cleaning", "maintenance", "high")
    if has(r"furnace|boiler|heat pump|heating|heater") and has(r"repair|fix|service"):
        return ("Direct heating repair" if not has(r"furnace") else "Furnace repair", "heating/furnace/boiler/heat-pump repair or service", "repair", "high")
    if has(r"\bhvac\b|heating|cooling|\bheat\b|air\b|mechanical|climate|comfort|plumbing") and (has(r"near me|company|companies|contractor|contractors|service|services|in my area|local") or len(t.split()) <= 4):
        return ("Ambiguous", "local HVAC-contractor search; service not stated", "local_hvac", "medium")
    if has(r"furnace|boiler|heat pump|mini split|ductless"):
        return ("Ambiguous", "equipment named without a service word", "equipment_bare", "medium")
    return ("Ambiguous", "unclassified - manual review", "other", "low")


VERDICT = {"competitor": "Exact-negative candidate", "vehicle": "Exact-negative candidate", "floor_heat": "Exact-negative candidate",
           "fireplace": "Exact-negative candidate", "pellet_stove": "Exact-negative candidate", "water_heater": "Exact-negative candidate",
           "employment": "Exact-negative candidate", "availability": "Exact-negative candidate", "thermostat_diy": "Exact-negative candidate",
           "model": "Exact-negative candidate", "oil": "Exact-negative candidate", "ac": "Exact-negative candidate", "info": "Exact-negative candidate",
           "diy": "Monitor", "price": "Keep", "geothermal": "Keep", "emergency": "Keep", "no_heat": "Keep", "duct": "Service confirmation",
           "thermostat": "Keep", "name_uncertain": "Monitor", "install": "Keep", "maintenance": "Routing review", "repair": "Keep",
           "local_hvac": "Monitor", "equipment_bare": "Monitor", "other": "Monitor", "manual_keep": "Keep", "manual_negative": "Exact-negative candidate",
           "manual_monitor": "Monitor", "manual_route": "Routing review"}

agg = collections.defaultdict(lambda: {w: collections.Counter() for w in W})
meta, dates = {}, collections.defaultdict(set)
for r in ROWS:
    key = (r["campaign"], r["ad_group"], r["term"], r["kw_id"], r["kw_text"], r["kw_match"], r["st_match"])
    meta[key] = r["status"]; dates[key].add(r["date"])
    for w, (a, b) in W.items():
        if a <= r["date"] <= b:
            for m in ("impr", "clicks", "cost", "conv", "all_conv"):
                agg[key][w][m] += r[m]

out = []
for key, v in agg.items():
    cid, gid, term, kid, kwt, kwm, stm = key
    intent, why, bucket, conf = classify(term, cid)
    camp_status = CAMPS.get(cid, {}).get("status", "?")
    ag_status = AGS.get(gid, {}).get("status", "?")
    hit = covering(cid, gid, term) if camp_status == "ENABLED" else []
    verdict = VERDICT[bucket]
    if camp_status != "ENABLED":
        verdict, cov = "History only (campaign PAUSED)", "n/a - campaign paused"
    elif cid in NO_SERVE and verdict == "Exact-negative candidate":
        verdict, cov = "History (campaign has no servable ads)", NO_SERVE[cid]
    elif hit:
        cov = "already covered" + (" (added after this term last served)" if max(dates[key]) < "2026-09-28" and all("shared" in h for h in hit) else "")
        if verdict == "Exact-negative candidate":
            verdict = "Keep excluded (already covered)"
    else:
        cov = "newly uncovered"
    if camp_status == "ENABLED" and ag_status != "ENABLED" and verdict == "Exact-negative candidate":
        verdict, cov = "History only (ad group PAUSED)", cov + "; ad group paused"
    tot = {m: round(sum(v[w][m] for w in W), 2) for m in ("impr", "clicks", "cost", "conv", "all_conv")}
    out.append(dict(period_first=min(dates[key]), period_last=max(dates[key]), campaign=CAMPS.get(cid, {}).get("name", cid), campaign_id=cid,
                    campaign_status=camp_status, ad_group=AGS.get(gid, {}).get("name", gid), ad_group_id=gid, ad_group_status=ag_status, search_term=term,
                    triggering_keyword=kwt, keyword_match_type=kwm, keyword_criterion_id=kid, search_term_match_relationship=stm, term_status=meta[key],
                    **{f"{w}_{m}": (round(v[w][m], 2) if m == "cost" else v[w][m]) for w in W for m in ("impr", "clicks", "cost", "conv", "all_conv")},
                    total_impr=tot["impr"], total_clicks=tot["clicks"], total_cost=tot["cost"],
                    ctr=f"{100 * tot['clicks'] / tot['impr']:.1f}%" if tot["impr"] else "", cpc=round(tot["cost"] / tot["clicks"], 2) if tot["clicks"] else "",
                    recorded_conversions=tot["conv"], all_conversions=tot["all_conv"], verified_paid_leads="see reconciliation (0 matched to a term)",
                    intent=intent, fit=why, bucket=bucket, coverage=cov, covering_negatives=" | ".join(hit[:3]), verdict=verdict, confidence=conf))

if "--review" in sys.argv:
    seen = set()
    for x in sorted(out, key=lambda z: (z["bucket"], z["search_term"])):
        if x["bucket"] in sys.argv[sys.argv.index("--review") + 1].split(",") and x["search_term"] not in seen:
            seen.add(x["search_term"])
            print(f"{x['bucket']:14s}|{x['campaign_status'][:3]}|{x['campaign_id'][-4:]}|{x['total_impr']:>3}i {x['total_clicks']}c ${x['total_cost']:<7}| {x['search_term']}")
    sys.exit(0)

# candidates: one per (enabled campaign, full query); scope = campaign unless the query is routing-only
cands = {}
for x in out:
    if x["verdict"] != "Exact-negative candidate":
        continue
    k = (x["campaign_id"], x["search_term"])
    c = cands.setdefault(k, dict(query=x["search_term"], display=f"[{x['search_term']}]", match_type="EXACT", campaign=x["campaign"],
                                 campaign_id=x["campaign_id"], scope="campaign", bucket=x["bucket"], reason=x["fit"], confidence=x["confidence"],
                                 impr=0, clicks=0, cost=0.0, ad_groups=set(), first_seen=x["period_first"], last_seen=x["period_last"]))
    c["impr"] += x["total_impr"]; c["clicks"] += x["total_clicks"]; c["cost"] = round(c["cost"] + x["total_cost"], 2); c["ad_groups"].add(x["ad_group_id"])
    c["first_seen"] = min(c["first_seen"], x["period_first"]); c["last_seen"] = max(c["last_seen"], x["period_last"])
valid, too_long, conflicts = [], [], []
for c in cands.values():
    c["ad_groups"] = sorted(c["ad_groups"])
    words = norm(c["query"])
    c["words"], c["chars"] = len(words), len(c["query"])
    clash = [f"{AGS.get(k['ad_group'], {}).get('name')} {k['match']} {k['text']}" for k in S["keywords"]
             if not k["negative"] and k["campaign"] == c["campaign_id"] and norm(k["text"]) == words]
    c["conflict_check"] = ("BLOCKS POSITIVE: " + "; ".join(clash)) if clash else "none: blocks only this full query; longer buyer queries stay eligible"
    c["priority"] = "P1 spent money" if c["cost"] > 0 else ("P2 recurring (>=3 impr)" if c["impr"] >= 3 else "P3 low volume")
    (too_long if (c["words"] > 10 or c["chars"] > 80) else conflicts if clash else valid).append(c)
valid.sort(key=lambda c: (c["campaign_id"], c["priority"], -c["cost"], -c["impr"], c["query"]))
EXP = CD / "exports"
with (EXP / "search-term-verdicts-2026-10-02.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(out[0].keys())); wr.writeheader()
    for x in sorted(out, key=lambda z: (z["campaign_status"] != "ENABLED", z["campaign_id"], z["ad_group"], -z["total_cost"], -z["total_impr"], z["search_term"])):
        wr.writerow(x)
(EXP / "negative-candidates-2026-10-02.json").write_text(json.dumps(dict(valid=valid, too_long=too_long, conflicts=conflicts), indent=1), encoding="utf-8")
summ = dict(rows=len(out), distinct_terms=len({x["search_term"] for x in out}), verdicts=dict(collections.Counter(x["verdict"] for x in out)),
            buckets=dict(collections.Counter(x["bucket"] for x in out)), candidates=len(valid), too_long=len(too_long), conflicts=len(conflicts),
            candidates_by_campaign=dict(collections.Counter(c["campaign_id"] for c in valid)), candidates_by_bucket=dict(collections.Counter(c["bucket"] for c in valid)),
            candidate_cost=round(sum(c["cost"] for c in valid), 2))
for w, (a, b) in W.items():
    for st in ("ENABLED", "PAUSED"):
        xs = [x for x in out if x["campaign_status"] == st]
        summ[f"{w}|{st}|visible"] = {m: round(sum(x[f"{w}_{m}"] for x in xs), 2) for m in ("impr", "clicks", "cost")}
        summ[f"{w}|{st}|by_intent_cost"] = {k: round(v, 2) for k, v in collections.Counter({i: sum(x[f"{w}_cost"] for x in xs if x["intent"] == i) for i in {x['intent'] for x in xs}}).items()}
(CD / "snapshots" / "search-term-analysis-2026-10-02.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
print(json.dumps(summ, indent=1))
