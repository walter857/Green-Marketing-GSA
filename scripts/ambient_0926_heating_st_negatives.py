#!/usr/bin/env python3
"""Ambient | 2026-09-26 | Search-term review of the seven heating Search campaigns -> EXACT negatives.

Follows the repo's corpus-isolation rule: raw search terms are written to disk only and never
printed. Classification is by WHITELIST vocabulary (heating services, intent, symptoms,
manufacturers, Maryland places, question/cost words). Stdout carries aggregates only.

Buckets
  KEEP        every token is whitelisted heating/intent/geo/brand vocabulary
  KEEP_CONV   any conversion ever -> never negated
  HOLD        whitelisted, but contains a question, parts or propane word (could be a buyer)
  DEFERRED    maintenance / tune-up / ductless / geothermal vocabulary -> routing, not negated
              (protects the owner's future tests)
  COOLING     cooling-only vocabulary on a heating campaign while cooling is paused
  OUT_OF_SCOPE  at least one token outside every whitelist (never characterised or sampled)
Negatives: COOLING + OUT_OF_SCOPE terms become EXACT members of one shared negative list attached
to the seven heating Search campaigns. EXACT blocks only that identical query.
Guards: converted, already an account keyword, already blocked by an existing negative, or a
misspelling of a whitelisted service word -> not negated.

    python ambient_0926_heating_st_negatives.py plan | execute --fp X | readback
"""
from __future__ import annotations
import sys, json, re, argparse, datetime, hashlib, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS, CLIENT_DIR
from gm_gsa.safety import approval_code

PLAN_NAME = "AMB-0926-NEG-HEAT-1"
SEVEN = ["24257819463", "24268690038", "24257819466", "24132507744", "24279798229", "24268690041", "24274160783"]
SINCE = "2026-09-17"
LIST_NAME = "Heating | Out-of-scope search terms (EXACT) | 2026-09"
RAW = CLIENT_DIR / "exports" / "heating-search-terms-2026-09-26.jsonl"   # raw terms: disk only
GEO = Path(r"C:\Users\walte\AppData\Local\Temp\claude\D--MG-green-marketing-gsa\e9093d43-7335-4a82-89d5-4762b093785f\scratchpad\md_geo_tokens.json")

SERVICE = set("""furnace furnaces heat heating heater heaters pump pumps boiler boilers radiator radiators baseboard
hydronic radiant thermostat thermostats hvac system systems unit units central forced gas electric natural
steam hot""".split())
INTENT = set("""repair repairs repairing fix fixing fixed service services servicing replace replacement replacements
replacing install installation installations installer installers installing new estimate estimates quote
quotes cost costs price prices pricing much best top rated near me my local nearby company companies
contractor contractors technician technicians tech techs specialist specialists expert experts emergency
same day 24 7 24/7 hour hours open now today tonight weekend saturday sunday cheap affordable residential
home house homes houses for a an the in of and to on or vs versus with your upgrade upgrades efficient
efficiency high energy smart programmable wifi wireless no not working work works wont won't doesnt doesn't
isnt isn't turn turning on off cold blowing air noise noisy loud leaking leak leaks smell smells short
cycling cycle keeps keep shutting shut broken out stopped making running runs stuck light lights ignite
igniting lighting reset issue issues problem problems trouble troubleshooting diagnostic diagnosis get call
number phone contact schedule book appointment area md maryland county up down stop stops stopping start starts
starting started kick kicking come comes coming lukewarm warm enough barely freezing frozen ice icing iced defrost
constantly blinking flashing code codes error beeping rattling banging squealing humming clicking burning smoke
carbon monoxide detector tripping breaker low drops dropping losing old older age years life lifespan worth second
opinion removal remove disposal installed replaced repaired serviced repairman repairmen guy guys man people
business owned family licensed certified insured reliable reputable trusted good great recommended review reviews
rating ratings quick fast asap urgent immediate available availability free discount deal deals coupon special
specials financing finance payment plans plan rebate rebates warranty size sizing ton btu whole entire basement
attic garage condo apartment townhouse inside outside indoor outdoor mobile manufactured install repair
heats heated heaters temperature temp degrees setting settings program programming wiring wire setup set""".split())
MANUFACTURERS = set("""carrier trane lennox goodman rheem ruud mitsubishi daikin amana bosch bryant armstrong weil mclain
burnham york american standard heil tempstar coleman payne nordyne frigidaire navien buderus peerless utica
slant fin rinnai nest ecobee honeywell emerson sensi fujitsu lg ameristar comfortmaker arcoaire keeprite
luxaire janitrol williams""".split())
BRAND = {"ambient"}
QUESTION = set("what why when where which who is does do did should can could will would i it its it's".split())
PARTS = set("igniter ignitor ignition sensor flame pilot burner blower motor inducer board circuit filter filters "
            "part parts valve capacitor switch pressure limit transformer fan belt".split())
HOLD_ONLY = set("propane plumber plumbers plumbing water humidifier dehumidifier duct ducts ductwork vent vents venting chimney flue zoning zone quality mechanical".split())
DEFERRED = set("maintenance maintain tune tuneup tune-up tuneups inspection inspections inspect check checkup "
               "cleaning clean ductless mini split minisplit geothermal ground".split())
COOLING = set("ac a/c conditioner conditioners conditioning cooling cool".split())
PUMP_PHRASES = [("heat", "pump")]
PROTECTED: set = set()


def lev(a, b):
    if abs(len(a) - len(b)) > 2: return 9
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def classify(term, geo, conv):
    toks = [t for t in re.split(r"[^a-z0-9/']+", term.lower()) if t]
    if conv > 0: return "KEEP_CONV"
    if not toks: return "OUT_OF_SCOPE"
    if "how" in toks:
        i = toks.index("how")
        if i + 1 < len(toks) and toks[i + 1] == "much": toks = toks[:i] + toks[i + 2:]
        else: return "HOLD" if any(t in SERVICE for t in toks) else "OUT_OF_SCOPE"
    white = SERVICE | INTENT | MANUFACTURERS | BRAND | geo
    has_service = any(t in SERVICE or t in DEFERRED for t in toks)
    unknown = [t for t in toks if t not in white and t not in QUESTION and t not in PARTS and t not in HOLD_ONLY
               and t not in DEFERRED and t not in COOLING and not re.fullmatch(r"2[01]\d{3}", t)]
    # misspelling guard: an unknown token within edit distance 2 of a service word counts as that word
    unknown = [t for t in unknown if not (len(t) >= 5 and any(lev(t, s) <= 2 for s in SERVICE | DEFERRED if len(s) >= 5))]
    # backstop: a word that appears in any account-wide converting term or live keyword is vocabulary, not junk
    if unknown and all(t in PROTECTED for t in unknown): return "HOLD"
    if unknown: return "OUT_OF_SCOPE"
    if any(t in COOLING for t in toks) and not any(t in SERVICE - {"hvac", "system", "systems", "unit", "units", "central", "electric", "gas"} for t in toks):
        return "COOLING"
    if any(t in DEFERRED for t in toks): return "DEFERRED"
    if not has_service and not any(t in MANUFACTURERS or t in BRAND for t in toks): return "HOLD"
    if any(t in QUESTION or t in PARTS or t in HOLD_ONLY for t in toks): return "HOLD"
    return "KEEP"


def blocked_by(term, negs):
    toks = term.split()
    for text, mt in negs:
        nt = text.split()
        if mt == "EXACT" and text == term: return True
        if mt == "PHRASE" and any(toks[i:i + len(nt)] == nt for i in range(len(toks) - len(nt) + 1)): return True
        if mt == "BROAD" and set(nt) <= set(toks): return True
    return False


def gather(c):
    rows = collections.defaultdict(lambda: dict(impr=0, clicks=0, cost=0.0, conv=0.0, camps=set(), status=set()))
    for r in q(c, f"""SELECT search_term_view.search_term, search_term_view.status, campaign.id, metrics.impressions,
            metrics.clicks, metrics.cost_micros, metrics.all_conversions FROM search_term_view
            WHERE campaign.id IN ({','.join(SEVEN)}) AND segments.date BETWEEN '{SINCE}' AND '{datetime.datetime.now(TZ).date()}'"""):
        t = r.search_term_view.search_term.strip().lower()
        d = rows[t]; d["impr"] += r.metrics.impressions; d["clicks"] += r.metrics.clicks
        d["cost"] += r.metrics.cost_micros / 1e6; d["conv"] += r.metrics.all_conversions
        d["camps"].add(str(r.campaign.id)); d["status"].add(E(r.search_term_view.status))
    # all-time conversions for the same terms, account-wide (protects anything that ever converted)
    ever = collections.Counter()
    for r in q(c, """SELECT search_term_view.search_term, metrics.all_conversions FROM search_term_view
            WHERE segments.date BETWEEN '2019-01-01' AND '2026-09-26' AND metrics.all_conversions > 0"""):
        ever[r.search_term_view.search_term.strip().lower()] += r.metrics.all_conversions
    kws = {r.ad_group_criterion.keyword.text.strip().lower() for r in q(c, """SELECT ad_group_criterion.keyword.text
            FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE
            AND ad_group_criterion.status != 'REMOVED'""")}
    negs = collections.defaultdict(list)
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
            FROM campaign_criterion WHERE campaign.id IN ({','.join(SEVEN)}) AND campaign_criterion.negative = TRUE
            AND campaign_criterion.type = 'KEYWORD'"""):
        negs[str(r.campaign.id)].append((r.campaign_criterion.keyword.text.lower(), E(r.campaign_criterion.keyword.match_type)))
    acct = [(r.shared_criterion.keyword.text.lower(), E(r.shared_criterion.keyword.match_type)) for r in q(c, """SELECT
            shared_criterion.keyword.text, shared_criterion.keyword.match_type, shared_set.type, shared_set.status FROM shared_criterion
            WHERE shared_set.type = 'ACCOUNT_LEVEL_NEGATIVE_KEYWORDS' AND shared_set.status = 'ENABLED'""")]
    existing = [str(r.shared_set.id) for r in q(c, f"SELECT shared_set.id, shared_set.name FROM shared_set WHERE shared_set.name = '{LIST_NAME}' AND shared_set.status = 'ENABLED'")]
    return rows, ever, kws, negs, acct, existing


def build(c):
    geo = set(json.loads(GEO.read_text()))
    rows, ever, kws, negs, acct, existing = gather(c)
    PROTECTED.clear()
    for t in list(ever) + list(kws):
        PROTECTED.update(x for x in re.split(r"[^a-z0-9/']+", t) if x)
    with RAW.open("w", encoding="utf-8") as f:
        for t, d in rows.items():
            f.write(json.dumps({"term": t, **{k: (sorted(v) if isinstance(v, set) else v) for k, v in d.items()}}) + "\n")
    agg = collections.defaultdict(lambda: [0, 0, 0, 0.0])
    per_camp = collections.defaultdict(lambda: collections.Counter())
    neg_terms, skipped = [], collections.Counter()
    for t, d in rows.items():
        b = classify(t, geo, d["conv"] + ever.get(t, 0))
        a = agg[b]; a[0] += 1; a[1] += d["impr"]; a[2] += d["clicks"]; a[3] += d["cost"]
        for cid in d["camps"]: per_camp[cid][b] += 1
        if b not in ("OUT_OF_SCOPE", "COOLING"): continue
        if "ADDED" in d["status"] or "ADDED_EXCLUDED" in d["status"]: skipped["is_keyword"] += 1; continue
        if t in kws: skipped["equals_account_keyword"] += 1; continue
        if len(t) > 80 or len(t.split()) > 10: skipped["too_long_for_keyword"] += 1; continue
        if all(blocked_by(t, negs[cid] + acct) for cid in d["camps"]): skipped["already_blocked"] += 1; continue
        neg_terms.append(t)
    neg_terms = sorted(set(neg_terms))
    plan = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342", "plan_name": PLAN_NAME,
            "built_local": datetime.datetime.now(TZ).date().isoformat(), "window": f"{SINCE}..today",
            "authority": "owner request 2026-09-26: add bad search terms on the new heating campaigns as negatives",
            "campaigns": SEVEN, "shared_list": LIST_NAME, "match_type": "EXACT", "existing_list": existing,
            "negatives": neg_terms,  # raw terms: never printed
            "negatives_sha1": hashlib.sha1("\n".join(neg_terms).encode()).hexdigest()[:12],
            "buckets": {k: {"terms": v[0], "impr": v[1], "clicks": v[2], "cost": round(v[3], 2)} for k, v in agg.items()},
            "skipped": dict(skipped), "per_campaign": {k: dict(v) for k, v in per_camp.items()}}
    plan["operation_count"] = (0 if existing else 1) + len(neg_terms) + len(SEVEN)
    return plan


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["plan", "execute", "readback"]); ap.add_argument("--fp")
    a = ap.parse_args()
    c = client(); identity_gate(c, verbose=False)
    if a.mode == "readback": return readback(c)
    plan = build(c); fp = approval_code(plan)
    if a.mode == "plan":
        plan["fingerprint"] = fp
        (PLANS / f"{PLAN_NAME}.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print(f"PLAN {PLAN_NAME} {fp} | negatives {len(plan['negatives'])} (sha1 {plan['negatives_sha1']}) | ops {plan['operation_count']}")
        for k, v in sorted(plan["buckets"].items()): print(f"  {k:13s} {v}")
        print("  skipped:", plan["skipped"])
        names = {"24257819463": "Repair", "24268690038": "HeatPump", "24257819466": "Inst/Repl", "24132507744": "Boiler",
                 "24279798229": "Maint", "24268690041": "Thermo", "24274160783": "Geo"}
        for k, v in plan["per_campaign"].items(): print(f"  {names.get(k, k):9s} {v}")
        return
    if a.fp != fp: sys.exit(f"ABORT fp {fp} != {a.fp}")
    if plan["existing_list"]: sys.exit(f"ABORT: list already exists {plan['existing_list']}")
    ga = c.get_service("GoogleAdsService"); ops = []
    sp = c.get_service("SharedSetService").shared_set_path(CID, -1)
    m = c.get_type("MutateOperation"); s = m.shared_set_operation.create
    s.resource_name = sp; s.name = LIST_NAME; s.type_ = c.enums.SharedSetTypeEnum.NEGATIVE_KEYWORDS; ops.append(m)
    for t in plan["negatives"]:
        m = c.get_type("MutateOperation"); cr = m.shared_criterion_operation.create
        cr.shared_set = sp; cr.keyword.text = t; cr.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT; ops.append(m)
    for cid in SEVEN:
        m = c.get_type("MutateOperation"); cs = m.campaign_shared_set_operation.create
        cs.campaign = c.get_service("CampaignService").campaign_path(CID, cid); cs.shared_set = sp; ops.append(m)
    rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.mutate_operations.extend(ops)
    rq.validate_only = True
    try:
        ga.mutate(request=rq)
    except Exception as ex:
        msgs = re.findall(r'message: "([^"]+)"', str(ex)); sys.exit(f"VALIDATE FAIL {msgs[:3]}")
    print("validate_only PASS")
    rq.validate_only = False; resp = ga.mutate(request=rq)
    names = [getattr(r, f).resource_name for r in resp.mutate_operation_responses
             for f in ("shared_set_result", "shared_criterion_result", "campaign_shared_set_result") if r._pb.HasField(f)]
    rec = {"plan": PLAN_NAME, "fingerprint": fp, "executed_local": datetime.datetime.now(TZ).isoformat(),
           "created_count": len(names), "shared_set": names[0], "negatives_sha1": plan["negatives_sha1"]}
    (RECEIPTS / f"{PLAN_NAME}-EXECUTED.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("EXECUTED", len(names), "resources;", names[0])


def readback(c):
    plan = json.loads((PLANS / f"{PLAN_NAME}.json").read_text(encoding="utf-8"))
    ss = q(c, f"SELECT shared_set.id, shared_set.status, shared_set.type FROM shared_set WHERE shared_set.name = '{LIST_NAME}'")
    sid = str(ss[0].shared_set.id)
    members = [(r.shared_criterion.keyword.text, E(r.shared_criterion.keyword.match_type)) for r in q(c,
               f"SELECT shared_criterion.keyword.text, shared_criterion.keyword.match_type, shared_set.id FROM shared_criterion WHERE shared_set.id = {sid}")]
    att = {str(r.campaign.id): E(r.campaign_shared_set.status) for r in q(c,
           f"SELECT campaign.id, campaign_shared_set.status, shared_set.id FROM campaign_shared_set WHERE shared_set.id = {sid}")}
    fails = []
    if sorted(t for t, _ in members) != sorted(plan["negatives"]): fails.append("member set differs from plan")
    if any(mt != "EXACT" for _, mt in members): fails.append("non-EXACT member")
    if sorted(att) != sorted(SEVEN) or any(v != "ENABLED" for v in att.values()): fails.append(f"attachments {att}")
    kws = {r.ad_group_criterion.keyword.text.strip().lower() for r in q(c, """SELECT ad_group_criterion.keyword.text
            FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE
            AND ad_group_criterion.status != 'REMOVED'""")}
    clash = sum(1 for t, _ in members if t in kws)
    if clash: fails.append(f"{clash} members equal a positive keyword")
    print(f"shared set {sid} {E(ss[0].shared_set.status)} | members {len(members)} EXACT | attached to {len(att)} campaigns | "
          f"members equal to a positive keyword: {clash}")
    print("READBACK FAILS:", fails or 0)
    rec_p = RECEIPTS / f"{PLAN_NAME}-EXECUTED.json"
    rec = json.loads(rec_p.read_text(encoding="utf-8")); rec["readback"] = {"shared_set": sid, "members": len(members), "fails": fails}
    rec_p.write_text(json.dumps(rec, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
