#!/usr/bin/env python3
"""BOFU search-term classifier for Ambient Cooling, 2026-09-09.

Design rules:
  * Whitelist-first. Protection beats negation on every tie.
  * Every negative candidate is dedupe-tested against the live negative corpus
    (campaign + ad group + account-level shared set) using real Google matching
    semantics: BROAD = word-subset, PHRASE = contiguous word subsequence,
    EXACT = full normalised equality.
  * Every negative candidate is collision-tested against active positives,
    converting terms (account-wide, all time), the service catalogue, supported
    manufacturers, every live geo target and a BOFU probe set.
  * Detail goes to disk. stdout carries aggregates plus the competitor/entity
    tokens that the deliverable itself requires.
"""
from __future__ import annotations
import sys, json, re, csv, hashlib, unicodedata
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa

# ----------------------------------------------------------------------------
# 0. Load evidence
# ----------------------------------------------------------------------------
struct = json.load(open(EVID / "2026-09-09-structure.json", encoding="utf-8"))
geo = json.load(open(EVID / "2026-09-09-geo-targets.json", encoding="utf-8"))

terms = []
for line in (EXPORTS / "search-terms-api-2026-09-09-csvwindow.jsonl").read_text(
        encoding="utf-8").splitlines():
    if line.strip():
        terms.append(json.loads(line))
print(f"search-term rows loaded: {len(terms)}")

conv_five = [json.loads(l) for l in (EXPORTS / "search-terms-api-2026-09-09-converting.jsonl")
             .read_text(encoding="utf-8").splitlines() if l.strip()]
conv_all = [json.loads(l) for l in
            (EXPORTS / "search-terms-api-2026-09-09-converting-ACCOUNTWIDE.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
CONVERTING = {t["term"].lower().strip() for t in conv_five} | \
             {t["term"].lower().strip() for t in conv_all}
print(f"protected converting terms (five + account-wide, all time): {len(CONVERTING)}")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def words(s: str):
    return norm(s).split()


# ----------------------------------------------------------------------------
# 1. Live negative corpus
# ----------------------------------------------------------------------------
live_neg = defaultdict(lambda: {"BROAD": set(), "PHRASE": set(), "EXACT": set()})
acct_neg = {"BROAD": set(), "PHRASE": set(), "EXACT": set()}

for n in struct["campaign_negatives"]:
    if n["status"] == "ENABLED" and n["campaign_id"] in FIVE:
        live_neg[n["campaign_id"]][n["match"]].add(norm(n["text"]))
for n in struct["ad_group_negatives"]:
    if n["status"] == "ENABLED" and n["campaign_id"] in FIVE:
        live_neg[("AG", n["ad_group_id"])][n["match"]].add(norm(n["text"]))
ACCT_SET = "11252984411"
for sc in struct["shared_criteria"]:
    if sc["shared_set"] == ACCT_SET:
        acct_neg[sc["match"]].add(norm(sc["text"]))

print("\nLIVE NEGATIVE CORPUS")
for cid in FIVE:
    d = live_neg[cid]
    print(f"  {NAME[cid]:<20} campaign-level  B={len(d['BROAD']):<5} P={len(d['PHRASE']):<5} "
          f"E={len(d['EXACT']):<5} total={sum(len(v) for v in d.values())}")
print(f"  account-level shared set {ACCT_SET}: B={len(acct_neg['BROAD'])} "
      f"P={len(acct_neg['PHRASE'])} E={len(acct_neg['EXACT'])} "
      f"total={sum(len(v) for v in acct_neg.values())}")
agn = {k: v for k, v in live_neg.items() if isinstance(k, tuple)}
print(f"  ad-group-level buckets: {len(agn)}  total members="
      f"{sum(sum(len(x) for x in v.values()) for v in agn.values())}")

# shared sets attached to the five (should be none)
attached = [l for l in struct["campaign_shared_sets"] if l["campaign"] in FIVE]
print(f"  shared negative lists attached to the five: {len(attached)}")


def blocked_by(term, buckets):
    """Return the (match_type, negative_text) that blocks `term`, or None."""
    tw = words(term)
    tws = set(tw)
    joined = " " + " ".join(tw) + " "
    for b in buckets:
        for neg in b["BROAD"]:
            nw = neg.split()
            if nw and set(nw) <= tws:
                return ("BROAD", neg)
        for neg in b["PHRASE"]:
            if (" " + neg + " ") in joined:
                return ("PHRASE", neg)
        for neg in b["EXACT"]:
            if neg == " ".join(tw):
                return ("EXACT", neg)
    return None


# ----------------------------------------------------------------------------
# 2. Protection whitelist
# ----------------------------------------------------------------------------
SERVICES = (r"ac|a c|air ?con(?:d|ditioner|ditioning)?|hvac|heat(?:ing|er|pump)?|furnace|boiler|"
            r"duct(?:work|s)?|air ?duct|mini ?split|ductless|geothermal|thermostat|humidifier|"
            r"dehumidifier|tankless|water ?heater|condenser|compressor|evaporator|coil|"
            r"refrigerant|freon|cooling|climate control|central air|split system|air handler")
INTENT = (r"repair|fix|service|servicing|maintenance|maintain|tune ?up|install(?:er|ers|ation)?|"
          r"replace|replacement|company|companies|contractor|technician|tech|specialist|"
          r"professional|pro|expert|estimate|quote|price|pricing|cost|near me|near by|nearby|"
          r"local|open now|same day|emergency|24 ?hour|best|top|affordable|cheap|"
          r"residential|commercial|free|hire|call|book|schedule|appointment|diagnos|"
          r"not working|not cooling|not heating|broken|leak|no heat|no air|blowing")
MANUFACTURERS = (r"lennox|carrier|trane|goodman|daikin|rheem|amana|bosch|mitsubishi|armstrong|"
                 r"burnham|spacepak|aciq|york|american standard|bryant|payne|ruud|weil ?mclain|"
                 r"navien|rinnai|nortek|maytag|coleman|luxaire|tempstar|heil|comfortmaker")

RE_SERVICE = re.compile(rf"\b({SERVICES})\b")
RE_INTENT = re.compile(rf"({INTENT})")
RE_MANU = re.compile(rf"\b({MANUFACTURERS})\b")

MD_PLACES = set()
for gid, meta in geo["geo_names"].items():
    can = meta.get("canonical", "")
    if ",Maryland," in can or can.startswith("Maryland,"):
        MD_PLACES.add(norm(can.split(",")[0]))
MD_PLACES |= {"maryland", "md", "baltimore", "anne arundel", "howard county", "annapolis"}
RE_MD = re.compile(r"\b(" + "|".join(sorted(re.escape(p) for p in MD_PLACES if p)) + r")\b")
print(f"\nprotected Maryland place tokens: {len(MD_PLACES)}")

# 50+ BOFU probes that must never be blocked by a proposed negative
BOFU_PROBES = [
    "ac repair near me", "air conditioner repair near me", "ac repair company near me",
    "emergency air conditioning repair near me", "repair my ac", "ac not cooling",
    "air conditioning repair severn md", "ac repair columbia md", "ac repair annapolis",
    "cheap hvac service near me", "affordable ac repair near me", "ac repair cost",
    "ac repair estimate", "ac repair quote", "24 hour ac repair near me",
    "hvac repair near me", "hvac company near me", "hvac near me",
    "hvac companies near me open now", "heat and air repair", "hvac contractor near me",
    "hvac technician near me", "heating repair near me", "furnace repair near me",
    "furnace not working", "no heat call", "heating and cooling near me",
    "hvac service near me", "hvac repair severna park", "residential hvac repair",
    "commercial hvac repair near me", "hvac installers near me", "hvac installation near me",
    "new hvac system cost", "hvac ductwork installation near me",
    "heating and cooling installation near me", "central air installation near me",
    "mini split installation near me", "ductless mini split installer near me",
    "hvac replacement near me", "ac replacement near me", "furnace replacement near me",
    "air conditioner replacement cost", "heat pump replacement near me",
    "hvac system replacement cost", "gas boiler repair", "boiler repair near me",
    "gas boiler repair near me", "boiler service near me", "steam boiler repair near me",
    "geothermal hvac near me", "tankless water heater installation near me",
    "thermostat replacement near me", "whole house humidifier installation",
    "dehumidifier installation near me", "air duct cleaning and repair near me",
    "lennox dealer near me", "carrier hvac repair near me", "trane furnace repair",
    "goodman ac repair near me", "mitsubishi mini split installer near me",
    "rheem water heater repair near me", "best hvac company near me",
    "top rated hvac contractor near me", "licensed hvac contractor near me",
    "hvac free estimate near me", "same day ac repair near me",
]
print(f"BOFU protection probes: {len(BOFU_PROBES)}")


def is_protected(term):
    t = norm(term)
    if t in CONVERTING:
        return "CONVERTER"
    if RE_MANU.search(t) and RE_INTENT.search(t):
        return "MANUFACTURER_INTENT"
    if RE_SERVICE.search(t) and RE_INTENT.search(t):
        return "SERVICE_INTENT"
    return None


# ----------------------------------------------------------------------------
# 3. Irrelevance signals (whitelist-failure explanations, never a blocklist)
# ----------------------------------------------------------------------------
JOB = re.compile(r"\b(job|jobs|career|careers|hiring|salary|salaries|wage|apprentice|"
                 r"apprenticeship|resume|employment|vacancy|vacancies|internship|"
                 r"union local|helper wanted)\b")
LEARN = re.compile(r"\b(school|schools|class|classes|course|courses|training|certification|"
                   r"certificate|license exam|degree|diploma|program|tutorial|how to|diy|"
                   r"youtube|pdf|manual|wiring diagram|troubleshooting chart|"
                   r"study guide|practice test|epa 608)\b")
SUPPLY = re.compile(r"\b(supply house|wholesale|distributor|parts store|buy parts|"
                    r"replacement parts|amazon|ebay|home depot|lowes|lowe s|walmart|"
                    r"for sale|price list|catalog|rental|rent a)\b")
VEHICLE = re.compile(r"\b(car|cars|auto|automotive|truck|van|rv|motorhome|boat|marine|"
                     r"vehicle|jeep|honda|toyota|ford|chevy|bmw|audi|tesla|"
                     r"windshield|radiator)\b")
NOT_OUR_TRADE = re.compile(r"\b(plumber|plumbing|electrician|electrical|roofing|roofer|"
                           r"appliance repair|washer|dryer|refrigerator|fridge|freezer|"
                           r"oven|stove|dishwasher|garage door|window replacement|"
                           r"siding|gutter|septic|well pump|chimney sweep|"
                           r"pest control|landscap|lawn care|pressure wash|"
                           r"carpet clean|mold remediation|restoration)\b")
BRAND_SHOP = re.compile(r"\b(reviews|review|complaints|bbb|yelp|reddit|glassdoor|indeed|"
                        r"phone number|hours|address|location of|near me address|"
                        r"customer service number|corporate office|login|portal|"
                        r"pay bill|payment)\b")

SIGNALS = [("JOB_SEEKER", JOB), ("EDUCATION_DIY", LEARN), ("PARTS_SUPPLY", SUPPLY),
           ("VEHICLE_AC", VEHICLE), ("OTHER_TRADE", NOT_OUR_TRADE),
           ("BRAND_RESEARCH", BRAND_SHOP)]

# ----------------------------------------------------------------------------
# 4. Classify
# ----------------------------------------------------------------------------
rows = []
for t in terms:
    term = t["term"]
    cid = t["camp"]
    agid = t["ag"]
    buckets = [live_neg[cid], live_neg[("AG", agid)], acct_neg]
    cov = blocked_by(term, buckets)
    prot = is_protected(term)
    sigs = [nm for nm, rx in SIGNALS if rx.search(norm(term))]
    md = bool(RE_MD.search(norm(term)))

    if cov:
        verdict, reason = "ALREADY_COVERED", f"live {cov[0]} negative"
    elif prot == "CONVERTER":
        verdict, reason = "KEEP_BOFU", "observed converting term (all-time, account-wide)"
    elif prot and not sigs:
        verdict, reason = "KEEP_BOFU", prot.lower().replace("_", " ")
    elif prot and sigs:
        verdict, reason = "HOLD", f"service intent AND {'/'.join(sigs)} - manual read"
    elif sigs:
        verdict = "NEGATIVE_CANDIDATE"
        reason = "/".join(sigs)
    elif t["clicks"] == 0 and t["impressions"] <= 2:
        verdict, reason = "KEEP_TEST", "no whitelist hit, negligible exposure"
    else:
        verdict, reason = "HOLD", "no whitelist hit and no clear irrelevance signal"

    rows.append({**t, "verdict": verdict, "reason": reason, "protected": prot,
                 "signals": sigs, "covered_by": cov, "names_md_place": md})

print("\n=== VERDICT COUNTS ===")
vc = Counter(r["verdict"] for r in rows)
for k, v in vc.most_common():
    cost = round(sum(x["cost"] for x in rows if x["verdict"] == k), 2)
    clicks = sum(x["clicks"] for x in rows if x["verdict"] == k)
    conv = round(sum(x["conversions"] for x in rows if x["verdict"] == k), 2)
    ac = round(sum(x["all_conversions"] for x in rows if x["verdict"] == k), 2)
    print(f"  {k:<22} rows={v:<5} clicks={clicks:<4} ${cost:<10} conv={conv:<5} allconv={ac}")

print("\n=== VERDICT x CAMPAIGN ===")
for cid in FIVE:
    sub = [r for r in rows if r["camp"] == cid]
    if not sub:
        continue
    print(f"  {NAME[cid]} (rows={len(sub)}, clicks={sum(r['clicks'] for r in sub)}, "
          f"${round(sum(r['cost'] for r in sub), 2)})")
    for k, v in Counter(r["verdict"] for r in sub).most_common():
        cost = round(sum(x["cost"] for x in sub if x["verdict"] == k), 2)
        clk = sum(x["clicks"] for x in sub if x["verdict"] == k)
        print(f"      {k:<22} rows={v:<5} clicks={clk:<4} ${cost}")

print("\n=== NEGATIVE_CANDIDATE breakdown by signal ===")
cands = [r for r in rows if r["verdict"] == "NEGATIVE_CANDIDATE"]
sc = Counter(s for r in cands for s in r["signals"])
for k, v in sc.most_common():
    cost = round(sum(r["cost"] for r in cands if k in r["signals"]), 2)
    clk = sum(r["clicks"] for r in cands if k in r["signals"])
    print(f"  {k:<18} rows={v:<5} clicks={clk:<4} ${cost}")

print("\n=== ALREADY_COVERED: which live negative layer caught them ===")
cov_rows = [r for r in rows if r["verdict"] == "ALREADY_COVERED"]
print("  by match type of the blocking negative:",
      dict(Counter(r["covered_by"][0] for r in cov_rows)))
print("  Google's own search_term_view.status on those rows:",
      dict(Counter(r["st_status"] for r in cov_rows)))
print("  Google says EXCLUDED but our matcher says not covered:",
      sum(1 for r in rows if r["st_status"] == "EXCLUDED" and r["verdict"] != "ALREADY_COVERED"))
print("  our matcher says covered but Google says NONE:",
      sum(1 for r in rows if r["st_status"] == "NONE" and r["verdict"] == "ALREADY_COVERED"))

# ----------------------------------------------------------------------------
# 5. Write detail
# ----------------------------------------------------------------------------
outcsv = EXPORTS / "search-term-verdicts-2026-09-09.csv"
with outcsv.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["term", "campaign", "campaign_id", "ad_group_id", "st_status", "st_match",
                "impressions", "clicks", "cost", "conversions", "all_conversions",
                "verdict", "reason", "protected", "signals", "covered_by_match",
                "covered_by_text", "names_md_place"])
    for r in rows:
        w.writerow([r["term"], NAME[r["camp"]], r["camp"], r["ag"], r["st_status"], r["st_match"],
                    r["impressions"], r["clicks"], r["cost"], r["conversions"],
                    r["all_conversions"], r["verdict"], r["reason"], r["protected"] or "",
                    "|".join(r["signals"]), r["covered_by"][0] if r["covered_by"] else "",
                    r["covered_by"][1] if r["covered_by"] else "", r["names_md_place"]])
print(f"\nWROTE {outcsv.relative_to(ROOT)}  sha256="
      f"{hashlib.sha256(outcsv.read_bytes()).hexdigest()[:16]}")

json.dump(rows, open(EVID / "2026-09-09-verdicts.json", "w", encoding="utf-8"),
          indent=1, default=str)
print(f"WROTE {(EVID / '2026-09-09-verdicts.json').relative_to(ROOT)}")

json.dump({"bofu_probes": BOFU_PROBES, "converting_terms_count": len(CONVERTING),
           "md_place_tokens": sorted(MD_PLACES),
           "live_negative_counts": {
               **{NAME[c]: {k: len(v) for k, v in live_neg[c].items()} for c in FIVE},
               "account_level": {k: len(v) for k, v in acct_neg.items()}},
           "shared_lists_attached_to_five": len(attached)},
          open(EVID / "2026-09-09-protection-register.json", "w", encoding="utf-8"), indent=1)
print(f"WROTE {(EVID / '2026-09-09-protection-register.json').relative_to(ROOT)}")
