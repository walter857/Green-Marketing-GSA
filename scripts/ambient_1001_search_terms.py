#!/usr/bin/env python3
"""Ambient | 2026-10-01 | Search-term verdicts, negative coverage, EXACT-only candidates (DRAFT; no mutations, no API calls).

Inputs (already read this session, read-only):
  snapshots/snapshot-2026-10-01.json, snapshots/routing-context-2026-10-01.json, exports/search-terms-2026-10-01.jsonl
Raw search terms ARE written to the verdict CSV and report: Green Marketing's 2026-10-01 request requires the actual
full query on every row (HVAC corpus; recorded in the work order).

Negative matching model (Google Ads): EXACT negative = same words, same order, nothing extra; PHRASE negative = its words
contiguous in the query; BROAD negative = all its words anywhere in the query. Negatives are not expanded to close variants
(plurals, synonyms, reorderings). Casing is ignored. Punctuation is normalised the same way on both sides.
Outputs: exports/search-term-verdicts-2026-10-01.csv, exports/negative-candidates-2026-10-01.json,
         snapshots/search-term-analysis-2026-10-01.json
"""
from __future__ import annotations
import csv, json, re, collections, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CD = ROOT / "clients" / "ambient-cooling-heating"
S = json.loads((CD / "snapshots" / "snapshot-2026-10-01.json").read_text(encoding="utf-8"))
R = json.loads((CD / "snapshots" / "routing-context-2026-10-01.json").read_text(encoding="utf-8"))
ROWS = [json.loads(l) for l in (CD / "exports" / "search-terms-2026-10-01.jsonl").read_text(encoding="utf-8").splitlines()]
AGS, CAMPS = S["ad_groups"], S["campaigns"]
REPAIR, GEO = "24257819463", "24274160783"
W = {"history": ("2026-09-17", "2026-09-23"), "baseline": ("2026-09-24", "2026-09-30"), "post_1001": ("2026-10-01", "2026-10-01")}
SHARED_CREATED = {"12252013691": "2026-09-26 16:15", "12249470554": "2026-09-26 16:36 (+2 on 2026-09-27 12:22)",
                  "11252984411": "before 2026-09-17 (August rollout)"}
FIRST_SERVING_DAY_AFTER_SHARED = "2026-09-28"


def norm(t: str) -> list[str]:
    t = t.lower().replace("’", "'")
    t = re.sub(r"[^\w&'+\- ]", " ", t)
    return t.split()


def blocks(neg_text: str, match: str, q: list[str]) -> bool:
    n = norm(neg_text)
    if not n:
        return False
    if match == "EXACT":
        return n == q
    if match == "PHRASE":
        return any(q[i:i + len(n)] == n for i in range(len(q) - len(n) + 1))
    return all(tok in q for tok in n)  # BROAD


def near_miss(neg_text: str, match: str, q: list[str]) -> bool:
    """Would block if singular/plural were ignored (Google does NOT do this for negatives)."""
    stem = lambda w: w[:-1] if len(w) > 3 and w.endswith("s") else w
    return blocks(" ".join(stem(w) for w in norm(neg_text)), match, [stem(w) for w in q])


# ---------- negative stacks ----------
members = S["shared_set_members"]
sets = S["shared_sets"]
acct = [(f"account-level list {sid} '{sets.get(sid, {}).get('name')}'", m["text"], m["match"], SHARED_CREATED.get(sid, "?"))
        for sid in S["account_level_negative_sets"] for m in members.get(sid, [])]
attached = collections.defaultdict(list)
for a in R["attachments"]:
    if a["status"] == "ENABLED":
        for m in members.get(a["set_id"], []):
            attached[a["campaign_id"]].append((f"shared list {a['set_id']} '{sets.get(a['set_id'], {}).get('name')}'", m["text"], m["match"],
                                               SHARED_CREATED.get(a["set_id"], "?")))
camp_neg = collections.defaultdict(list)
for x in R["campaign_negatives"]:
    camp_neg[x["campaign_id"]].append(("campaign negative", x["text"], x["match"], "build 2026-09-21/22 (thermostat 2026-09-24)"))
ag_neg = collections.defaultdict(list)
for x in R["keywords"]:
    if x["negative"]:
        ag_neg[x["ad_group_id"]].append(("ad-group negative", x["text"], x["match"], "build 2026-09-21/22"))
positives = collections.defaultdict(list)
for x in R["keywords"]:
    if not x["negative"]:
        positives[x["ad_group_id"]].append(x)
RG = R["ad_groups"]


def stack(gid: str):
    cid = RG[gid]["campaign_id"]
    return acct + attached[cid] + camp_neg[cid] + ag_neg[gid]


def covering(gid: str, term: str):
    q = norm(term)
    hit = [dict(layer=l, text=t, match=m, created=c) for (l, t, m, c) in stack(gid) if blocks(t, m, q)]
    near = [dict(layer=l, text=t, match=m) for (l, t, m, c) in stack(gid) if not blocks(t, m, q) and near_miss(t, m, q)]
    return hit, near


def reachable(gid: str, term: str) -> list[str]:
    """Positive keywords in the ad group that could match the query LITERALLY (phrase contiguous / exact equal)."""
    q = norm(term)
    out = []
    for k in positives[gid]:
        if k["status"] != "ENABLED":
            continue
        n = norm(k["text"])
        if (k["match"] == "EXACT" and n == q) or (k["match"] == "PHRASE" and any(q[i:i + len(n)] == n for i in range(len(q) - len(n) + 1))):
            out.append(f"{k['match']} {k['text']}")
    return out


# ---------- intent model (whitelist-first, ordered) ----------
COMPETITOR_HIGH = {
    "booths hvac", "boothe's heating air plumbing & drains", "tevis modern comfort", "s f jones heating and cooling", "moon air elkton",
    "dodge heating and air", "max air heating & a c inc", "coastal hvac annapolis", "g & g mechanical heating & ac 305 e 31st st baltimore md 21218",
    "carroll mechanical columbia md", "allpro hvac", "b&d hvac", "belair engineering hvac", "del air heating", "go ecco climate control",
    "home team heating and cooling", "howard mechanical hvac", "joey taylor hvac", "maryland mechanical heating & cooling", "right way heating",
    "scotty's heating and cooling", "stanton hvac", "stivers hvac inc", "triple eee hvac", "bnb heating and cooling", "call dad",
    "classic air waldorf md", "climate care crofton md", "coastal heat and air", "cold comfort hvac rockville md", "compass energy laurel de",
    "falcon hvac", "frosty heating and air conditioning", "grove hvac maryland", "harbor point heating and air", "honest air mt airy",
    "hope plumbing heating and cooling", "jiffy hvac", "minnick hvac", "ocean air hvac", "powell and turner hvac", "pro tech hvac",
    "smock heating & air", "southern maryland heating and air waldorf md", "vito hvac", "xzavier hvac solutions llc baltimore reviews",
}
# Could be a business name OR a descriptive / place query: never a negative on this evidence.
NAME_UNCERTAIN = {"comfort care heating", "quick service hvac", "clean air baltimore", "all weather heating and air", "fixed hvac annapolis",
                  "maryland heating and cooling ellicott city", "bel air hvac", "quality heating cooling plumbing & electrical", "handyman hvac"}
OUT_OF_AREA = {"hvac easton md", "hvac company silver spring md", "hvac companies in frederick md", "hvac towson", "beltsville hvac"}


def classify(term: str, gid: str):
    t = " ".join(norm(term))
    has = lambda p: re.search(p, t) is not None
    if t in COMPETITOR_HIGH:
        return ("Clearly irrelevant", "another HVAC company's name (navigational); not Ambient", "competitor", "high")
    if has(r"\bwebasto\b|\b(car|auto|truck|rv|boat|marine|vehicle)\b"):
        return ("Clearly irrelevant", "vehicle/parking heater, not a home heating system", "vehicle", "high")
    if has(r"fireplace|gas log|heatilator|heat n glo"):
        return ("Other equipment repair", "fireplace service; not an approved Ambient service", "fireplace", "high")
    if has(r"pellet stove"):
        return ("Other equipment repair", "pellet stove; no approved-record or site evidence Ambient services it", "pellet_stove", "high")
    if has(r"water heater|hot water"):
        return ("Other equipment repair", "water heater / plumbing; Tankless is OUT of scope", "water_heater", "high")
    if has(r"waste oil"):
        return ("Clearly irrelevant", "waste-oil shop heater (commercial garage equipment), oil is OUT of scope", "oil", "high")
    if has(r"troubleshoot|fault|error|lockout|rollout|code \d|\bcodes?\b|flashing|green light|pilot light"):
        return ("Informational or DIY", "fault-code / troubleshooting lookup; some searchers hire after diagnosing", "diy", "medium")
    if has(r"\boil\b"):
        return ("Furnace repair", "oil-fired equipment; Oil services are OUT of advertising scope (owner, 2026-09-21)", "oil", "high")
    if has(r"^(how|what|why)\b") and not has(r"not (turning|working)|won t|no heat"):
        return ("Informational or DIY", "research question with no hire signal", "info", "medium")
    if has(r"geotherm|^geo\b"):
        if has(r"cost|price"):
            return ("Installation or replacement", "geothermal price research; a buyer signal", "geothermal", "medium")
        return ("Ambiguous", "geothermal system interest; repair vs installation not stated", "geothermal", "medium")
    if has(r"24 hour|emergenc|same day"):
        return ("Emergency repair", "urgent/after-hours intent; Ambient answers Mon-Fri 08-16 only (unverified beyond that)", "emergency", "medium")
    if has(r"not working|won t turn|not turning|no heat|stopped working"):
        return ("No-heat repair", "symptom-led; a homeowner ready to hire", "no_heat", "high")
    cooling = has(r"air condition|\ba ?c\b|\bac\b") and not has(r"heat")
    if cooling:
        return ("Other equipment repair", "air conditioning only; cooling campaigns PAUSED by owner 2026-09-21 and this campaign already negates 'ac repair'/'air conditioning repair'", "ac", "high")
    if has(r"duct"):
        return ("Other equipment repair", "ductwork repair; capability not in approved records", "duct", "medium")
    if has(r"radiant"):
        return ("Direct heating repair", "radiant/hydronic heat repair; capability not in approved records", "radiant", "medium")
    if has(r"reznor|rinnai"):
        return ("Other equipment repair", "manufacturer-specific (unit heater / tankless-boiler maker); fit unverified", "manufacturer", "medium")
    if t in NAME_UNCERTAIN:
        return ("Ambiguous", "may be a business name or a descriptive search; not proven navigational", "name_uncertain", "low")
    if t in OUT_OF_AREA:
        return ("Ambiguous", "generic HVAC search naming a place outside the 75 targets; service area beyond them unverified", "place", "medium")
    if has(r"furnace") and has(r"repair|fix"):
        return ("Furnace repair", "furnace repair", "furnace", "high")
    if has(r"furnace"):
        return ("Furnace repair", "furnace service (repair or maintenance not stated)", "furnace_service", "medium")
    if has(r"(heating|heater|heat) (repair|fix)|repair (heating|heater)"):
        return ("Direct heating repair", "heating repair", "heating_repair", "high")
    if has(r"commercial"):
        return ("Ambiguous", "commercial HVAC; commercial repair capability not separately verified", "commercial", "medium")
    if has(r"plumbing"):
        return ("Ambiguous", "combined plumbing + HVAC trade search", "plumbing_combo", "medium")
    if has(r"air handler"):
        return ("Other equipment repair", "air handler (heating and cooling component)", "air_handler", "medium")
    if has(r"heating|heat\b|hvac|repair|service"):
        return ("Ambiguous", "generic HVAC/heating company search; heating season makes repair plausible but unstated", "generic_hvac", "medium")
    return ("Ambiguous", "unclassified", "other", "low")


VERDICT_BY_BUCKET = {
    "competitor": "Exact-negative candidate", "vehicle": "Exact-negative candidate", "fireplace": "Exact-negative candidate",
    "pellet_stove": "Exact-negative candidate", "water_heater": "Exact-negative candidate", "oil": "Exact-negative candidate",
    "ac": "Exact-negative candidate", "diy": "Monitor", "info": "Exact-negative candidate", "geothermal": "Keep",
    "emergency": "Routing review", "no_heat": "Keep", "duct": "Service confirmation", "radiant": "Service confirmation",
    "manufacturer": "Service confirmation", "name_uncertain": "Monitor", "place": "Monitor", "furnace": "Keep", "furnace_service": "Keep",
    "heating_repair": "Keep", "commercial": "Service confirmation", "plumbing_combo": "Monitor", "air_handler": "Keep",
    "generic_hvac": "Keep", "other": "Monitor",
}

# ---------- aggregate observed rows ----------
agg = collections.defaultdict(lambda: {w: collections.Counter() for w in W})
meta, dates = {}, collections.defaultdict(set)
for r in ROWS:
    key = (r["campaign_id"], r["ad_group_id"], r["term"], r["kw_criterion"], r["kw_text"], r["kw_match"], r["st_match"])
    meta[key] = r["status"]
    dates[key].add(r["date"])
    for w, (a, b) in W.items():
        if a <= r["date"] <= b:
            for m in ("impr", "clicks", "cost", "conv", "all_conv"):
                agg[key][w][m] += r[m]

verdicts = []
for key, v in agg.items():
    cid, gid, term, crit, kwt, kwm, stm = key
    intent, why, bucket, conf = classify(term, gid)
    hit, near = covering(gid, term)
    status = meta[key]
    tot = {m: round(sum(v[w][m] for w in W), 2) for m in ("impr", "clicks", "cost", "conv", "all_conv")}
    verdict = VERDICT_BY_BUCKET[bucket]
    # coverage category
    if hit:
        first = min(dates[key])
        cov = "already covered"
        if any(h["layer"].startswith("shared list") for h in hit) and not any(not h["layer"].startswith("shared list") for h in hit) and first < FIRST_SERVING_DAY_AFTER_SHARED:
            cov = "already covered (negative added 2026-09-26, after this term served)"
    elif near:
        cov = "uncertain (plural/singular near-miss; Google does not expand negatives)"
    else:
        cov = "newly uncovered"
    if verdict == "Exact-negative candidate" and hit:
        verdict = "Keep excluded (already covered)"
    if status == "EXCLUDED" and not hit:
        cov = "Google reports EXCLUDED but no negative in the model matches - uncertain"
    conflict = []
    if verdict == "Exact-negative candidate":
        # an EXACT negative only blocks this full query; check it is not itself a positive keyword anywhere in the heating build
        same = [f"{RG[k['ad_group_id']]['name']} {k['match']} {k['text']}" for k in R["keywords"] if not k["negative"] and norm(k["text"]) == norm(term)]
        if same:
            conflict.append("is a positive keyword: " + "; ".join(same))
    reach = reachable(gid, term)
    verdicts.append(dict(
        campaign=CAMPS[cid]["name"], campaign_id=cid, ad_group=AGS[gid]["name"], ad_group_id=gid, search_term=term,
        triggering_keyword=kwt, keyword_criterion_id=crit, keyword_match_type=kwm, search_term_match_relationship=stm,
        literal_reach=", ".join(reach) or "none (semantic / close-variant match only)", term_status=status,
        first_seen=min(dates[key]), last_seen=max(dates[key]), serving_days=len(dates[key]),
        **{f"{w}_{m}": (round(v[w][m], 2) if m == "cost" else v[w][m]) for w in W for m in ("impr", "clicks", "cost", "all_conv")},
        total_impr=tot["impr"], total_clicks=tot["clicks"], total_cost=tot["cost"],
        total_ctr=f"{100 * tot['clicks'] / tot['impr']:.1f}%" if tot["impr"] else "", total_avg_cpc=round(tot["cost"] / tot["clicks"], 2) if tot["clicks"] else "",
        primary_conversions=tot["conv"], all_conversions=tot["all_conv"], verified_paid_leads="0 (see reconciliation)", qualified_leads="0",
        intent=intent, intent_reason=why, bucket=bucket, service_fit=why, coverage=cov,
        covering_negatives=" | ".join(f"{h['layer']}: {h['match']} [{h['text']}] (added {h['created']})" for h in hit[:3]),
        verdict=verdict, confidence=conf, conflict_check="; ".join(conflict) or "none: EXACT negative blocks only this full query"))

# ---------- the same query in several ad groups: covered in some only? ----------
by_term = collections.defaultdict(list)
for x in verdicts:
    by_term[x["search_term"]].append(x)
for term, xs in by_term.items():
    covs = {x["ad_group_id"]: bool(x["covering_negatives"]) for x in xs}
    if len(set(covs.values())) > 1:
        for x in xs:
            x["coverage"] += " | covered only in some ad groups"

# ---------- candidate list (one per campaign x full query; campaign scope unless a routing problem) ----------
cands = {}
for x in verdicts:
    if x["verdict"] != "Exact-negative candidate":
        continue
    k = (x["campaign_id"], x["search_term"])
    c = cands.setdefault(k, dict(query=x["search_term"], display=f"[{x['search_term']}]", match_type="EXACT", campaign=x["campaign"],
                                 campaign_id=x["campaign_id"], ad_group="(campaign scope)", ad_group_id="", scope="campaign",
                                 bucket=x["bucket"], reason=x["intent_reason"], confidence=x["confidence"],
                                 existing_coverage="none in account-level, shared, campaign or ad-group layers",
                                 conflict_check=x["conflict_check"], impr=0, clicks=0, cost=0.0, seen_in_ad_groups=set(),
                                 first_seen=x["first_seen"], last_seen=x["last_seen"], observed="observed"))
    c["impr"] += x["total_impr"]; c["clicks"] += x["total_clicks"]; c["cost"] = round(c["cost"] + x["total_cost"], 2)
    c["seen_in_ad_groups"].add(x["ad_group"]); c["first_seen"] = min(c["first_seen"], x["first_seen"]); c["last_seen"] = max(c["last_seen"], x["last_seen"])
for c in cands.values():
    c["seen_in_ad_groups"] = sorted(c["seen_in_ad_groups"])
    words = norm(c["query"])
    c["word_count"], c["char_count"] = len(words), len(c["query"])
    c["valid_negative_length"] = len(words) <= 10 and len(c["query"]) <= 80
    c["priority"] = "P1 (spent money)" if c["cost"] > 0 else ("P2 (recurring)" if c["impr"] >= 3 else "P3 (single sighting)")
not_addable = [c for c in cands.values() if not c["valid_negative_length"]]   # Google limit: 10 words / 80 chars
cand_list = sorted((c for c in cands.values() if c["valid_negative_length"]), key=lambda c: (c["priority"], -c["cost"], -c["impr"], c["query"]))
for x in verdicts:
    if x["verdict"] == "Exact-negative candidate" and any(c["query"] == x["search_term"] for c in not_addable):
        x["verdict"] = "Monitor (exceeds the 10-word negative limit; not addable as EXACT)"

# ---------- write ----------
EXP = CD / "exports"
with (EXP / "search-term-verdicts-2026-10-01.csv").open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(verdicts[0].keys()))
    wr.writeheader()
    for x in sorted(verdicts, key=lambda z: (z["campaign_id"], z["ad_group"], -z["total_cost"], -z["total_impr"], z["search_term"])):
        wr.writerow(x)
(EXP / "negative-candidates-2026-10-01.json").write_text(json.dumps(cand_list, indent=1), encoding="utf-8")

# ---------- coverage of visible vs total ----------
def camp_tot(cid, a, b, key="campaign_daily"):
    return {m: round(sum(v[m] for k, v in S["performance"][key].items() if k.split("|")[0] == cid and a <= k.split("|")[1] <= b), 2)
            for m in ("impr", "clicks", "cost")}


summary = {"rows": len(verdicts), "distinct_terms": len(by_term), "candidates": len(cand_list)}
for cid in (REPAIR, GEO):
    for w, (a, b) in W.items():
        tot = camp_tot(cid, a, b)
        vis = {m: round(sum(x[f"{w}_{m}"] for x in verdicts if x["campaign_id"] == cid), 2) for m in ("impr", "clicks", "cost")}
        summary[f"{cid}|{w}"] = dict(total=tot, visible=vis, hidden={m: round(tot[m] - vis[m], 2) for m in tot})
summary["by_intent_baseline"] = {}
for cid in (REPAIR, GEO):
    c = collections.defaultdict(collections.Counter)
    for x in verdicts:
        if x["campaign_id"] == cid:
            c[x["intent"]]["terms"] += 1 if x["baseline_impr"] else 0
            for m in ("impr", "clicks", "cost"):
                c[x["intent"]][m] += x[f"baseline_{m}"]
    summary["by_intent_baseline"][cid] = {k: dict(v) for k, v in c.items()}
summary["verdicts"] = dict(collections.Counter(x["verdict"] for x in verdicts))
summary["coverage"] = dict(collections.Counter(x["coverage"].split(" |")[0] for x in verdicts))
summary["candidates_by_bucket"] = dict(collections.Counter(c["bucket"] for c in cand_list))
summary["candidates_by_priority"] = dict(collections.Counter(c["priority"] for c in cand_list))
summary["candidate_spend_all_windows"] = round(sum(c["cost"] for c in cand_list), 2)
(CD / "snapshots" / "search-term-analysis-2026-10-01.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
