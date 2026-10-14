#!/usr/bin/env python3
"""Ambient | 2026-09-26 | Second search-term pass + PHRASE and forecast negatives for the heating campaigns.

Corpus rule: raw search terms and tokens derived from them stay on disk; stdout is aggregates only.
The FORECAST list is authored vocabulary (not derived from the corpus) and may be displayed.

Layers
  E  EXACT additions      new OUT_OF_SCOPE/COOLING terms not yet blocked -> existing EXACT list
  P1 PHRASE full-term     phrase versions of every OUT_OF_SCOPE/COOLING term
  P2 PHRASE token         recurring off-scope tokens (>=2 OOS terms), non-dictionary, not geo/brand/manufacturer
  F  PHRASE forecast      authored low-intent / non-hiring vocabulary
  N  BROAD names          the guarded competitor-name BROAD negatives already on Boiler Services, extended to
                          the other heating campaigns
Every candidate is dropped if it would block: a BOFU probe, a geo-grid probe for the 75 targeted places, an
all-time converting search term (account-wide), a live positive keyword, or a KEEP/KEEP_CONV/DEFERRED term
from the heating corpus. Redundant candidates (already covered by an existing BROAD/PHRASE negative) are dropped.

    python ambient_0926_heating_neg_phrase.py plan | execute --fp X | readback
"""
from __future__ import annotations
import sys, json, re, argparse, datetime, hashlib, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS, CLIENT_DIR, ROOT
from gm_gsa.safety import approval_code
import ambient_0926_heating_st_negatives as st

PLAN_NAME = "AMB-0926-NEG-HEAT-2"
SEVEN = st.SEVEN
EXACT_LIST = "12252013691"
NEW_LIST = "Heating | Low-intent, off-topic & competitor negatives | 2026-09"
BOILER = "24132507744"
DICT = ROOT / "reports" / "lexicons" / "english_words.txt"

FORECAST = {
    "employment": ["job", "jobs", "career", "careers", "salary", "salaries", "wage", "wages", "employment",
                   "apprentice", "apprenticeship", "internship", "resume", "indeed", "glassdoor", "ziprecruiter"],
    "training": ["school", "schools", "training", "course", "courses", "class", "classes", "certification",
                 "certifications", "certificate", "college", "exam", "textbook", "trade school"],
    "diy_info": ["diy", "do it yourself", "how to", "youtube", "video", "videos", "tutorial",
                 "manual", "manuals", "diagram", "diagrams", "schematic", "pdf", "instructions", "reddit", "forum",
                 "quora", "wikipedia", "definition", "meaning", "calculator", "images", "pictures", "clipart"],
    "products_retail": ["parts", "for sale", "in stock", "amazon", "ebay", "craigslist", "walmart", "wholesale",
                        "supply", "supplies", "supplier", "distributor", "filter", "filters", "used furnace",
                        "used furnaces", "used boiler", "used heat pump"],
    "assistance_programs": ["free furnace program", "free boiler program", "free heat pump program", "assistance", "grant", "grants",
                            "liheap", "weatherization", "low income", "section 8"],
    "tenant_landlord": ["tenant", "tenants", "landlord", "landlords", "renter", "renters"],
    "legal_complaints": ["lawyer", "lawyers", "attorney", "lawsuit", "complaint", "complaints", "recall",
                         "recalls", "class action"],
    "vehicles": ["car", "cars", "auto", "automotive", "truck", "trucks", "rv", "camper", "boat", "boats",
                 "marine", "vehicle", "jeep", "heater core"],
    "other_heat_products": ["space heater", "space heaters", "portable heater", "portable heaters", "patio heater",
                            "infrared heater", "kerosene", "pellet", "wood stove", "wood burning", "fireplace",
                            "fireplaces", "water heater", "water heaters", "tankless", "pool heater", "pool",
                            "hot tub", "aquarium", "greenhouse", "electric blanket", "heating pad", "oil",
                            "industrial"],
    "unrelated_heat_senses": ["heat press", "heat gun", "heat lamp", "heat rash", "heat stroke", "heat wave",
                              "heat index", "heat sink", "heat map", "heat transfer", "heat exhaustion"],
    "b2b": ["marketing", "franchise", "software", "leads"],
}
NEVER = set("""near me quote quotes price prices pricing cost costs best hire hiring local emergency free licensed
commercial thermostat thermostats humidifier dehumidifier heating furnace furnaces boiler boilers heat pump pumps
hvac repair replacement install installation service services maintenance tune inspection ductless geothermal
al american mr ambient company companies contractor contractors new""".split())
NEIGHBOR = set("virginia va delaware de pennsylvania pa dc washington district columbia".split())

SERVICES = ["furnace repair", "gas furnace repair", "electric furnace repair", "heating repair", "no heat repair",
            "heat pump repair", "furnace replacement", "heating replacement", "furnace installation",
            "heating installation", "heat pump installation", "heat pump replacement", "boiler repair",
            "gas boiler repair", "boiler replacement", "boiler installation", "thermostat repair",
            "thermostat replacement", "smart thermostat installation", "geothermal heat pump", "ductless heating",
            "furnace maintenance", "furnace tune up", "heating maintenance", "heating system inspection",
            "hvac repair", "hvac company", "heating and cooling company", "hvac contractor"]
MODS = ["{s}", "{s} near me", "{s} cost", "{s} price", "{s} quote", "best {s}", "local {s}", "emergency {s}",
        "{s} company", "{s} companies", "{s} contractor", "{s} service", "{s} estimate", "free estimate {s}",
        "{s} near me open now", "same day {s}", "how much does {s} cost", "cost to {s}", "who does {s}",
        "{s} for my home", "residential {s}", "commercial {s}", "{s} financing", "{s} rebate", "licensed {s}",
        "affordable {s}", "cheap {s}", "{s} reviews", "top rated {s}"]
EXTRA = ["furnace not working", "heat pump not heating", "furnace blowing cold air", "no heat in house",
         "boiler not heating", "thermostat not working", "furnace making noise", "furnace won't turn on",
         "heat pump frozen", "hiring hvac company", "hire furnace repair", "replace furnace or repair",
         "furnace repair or replace", "should i replace my furnace", "what does a new furnace cost",
         "heat pump vs furnace", "gas furnace vs heat pump cost", "new furnace installation cost",
         "furnace replacement quote", "heat pump installation quote", "furnace igniter replacement",
         "furnace flame sensor replacement", "furnace blower motor replacement", "boiler pressure low",
         "radiator not heating", "baseboard heat not working", "hydronic heating repair",
         "weil mclain boiler repair", "burnham boiler repair", "navien boiler repair", "carrier furnace repair",
         "trane heat pump repair", "lennox furnace repair", "goodman furnace installation", "rheem furnace",
         "bryant furnace repair", "mitsubishi heat pump", "daikin heat pump installation", "nest thermostat installation",
         "ecobee thermostat installation", "honeywell thermostat replacement", "ambient cooling and heating",
         "ambient heating", "hvac company near me", "heating company near me", "furnace guy near me",
         "boiler plumber near me", "oil to gas conversion", "free furnace estimate", "free furnace quote",
         "free heat pump quote", "free boiler estimate", "thermostat 1 degree off", "furnace repair college park",
         "smart thermostat installation app", "how do you know when to replace a furnace"]


def load_dict():
    try:
        return {w.strip().lower() for w in DICT.read_text(encoding="utf-8", errors="ignore").splitlines() if w.strip()}
    except FileNotFoundError:
        return set()


def blocks(text, mt, query):
    qt = query.split(); nt = text.split()
    if mt == "EXACT": return text == query
    if mt == "PHRASE": return any(qt[i:i + len(nt)] == nt for i in range(len(qt) - len(nt) + 1))
    return set(nt) <= set(qt)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["plan", "execute", "readback"]); ap.add_argument("--fp")
    a = ap.parse_args()
    c = client(); identity_gate(c, verbose=False)
    if a.mode == "readback": return readback(c)
    geo = set(json.loads(st.GEO.read_text()))
    rows, ever, kws, negs, acct, _ = st.gather(c)
    st.PROTECTED.clear()
    for t in list(ever) + list(kws): st.PROTECTED.update(x for x in re.split(r"[^a-z0-9/']+", t) if x)
    exact_list = [r.shared_criterion.keyword.text.lower() for r in q(c, f"SELECT shared_criterion.keyword.text, shared_set.id FROM shared_criterion WHERE shared_set.id = {EXACT_LIST}")]
    existing_new = [str(r.shared_set.id) for r in q(c, f"SELECT shared_set.id, shared_set.name FROM shared_set WHERE shared_set.name = '{NEW_LIST}' AND shared_set.status = 'ENABLED'")]
    names = sorted({r.campaign_criterion.keyword.text.lower() for r in q(c, f"""SELECT campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
             campaign.id FROM campaign_criterion WHERE campaign.id = {BOILER} AND campaign_criterion.negative = TRUE AND campaign_criterion.keyword.match_type = 'BROAD'""")})

    # ---- classify corpus (raw stays on disk) ----
    buckets = {}
    for t, d in rows.items():
        buckets[t] = st.classify(t, geo, d["conv"] + ever.get(t, 0))
    oos = sorted(t for t, b in buckets.items() if b in ("OUT_OF_SCOPE", "COOLING"))
    protected_terms = [t for t, b in buckets.items() if b in ("KEEP", "KEEP_CONV", "DEFERRED")]
    hold_terms = [t for t, b in buckets.items() if b == "HOLD"]

    # E: new exact additions (not in exact list and not blocked elsewhere)
    exact_add = sorted(t for t in oos if t not in exact_list and t not in kws and len(t) <= 80 and len(t.split()) <= 10
                       and not any(st.blocked_by(t, negs[cid] + acct) for cid in rows[t]["camps"]))

    # token extraction for P2
    dictionary = load_dict()
    white = st.SERVICE | st.INTENT | st.MANUFACTURERS | st.BRAND | geo | st.QUESTION | st.PARTS | st.HOLD_ONLY | st.DEFERRED | st.COOLING
    tok_count = collections.Counter()
    for t in oos:
        for tok in set(x for x in re.split(r"[^a-z0-9/']+", t) if x):
            if tok not in white: tok_count[tok] += 1
    in_scope_tokens = set()
    for t in protected_terms + hold_terms: in_scope_tokens.update(re.split(r"[^a-z0-9/']+", t))
    p2 = sorted(tok for tok, n in tok_count.items() if n >= 2 and len(tok) >= 4 and tok not in dictionary
                and tok not in st.PROTECTED and tok not in in_scope_tokens and tok not in NEVER and tok not in NEIGHBOR
                and not tok.isdigit())

    cands = []  # (text, match_type, layer)
    cands += [(t, "PHRASE", "P1") for t in oos if len(t) <= 80 and len(t.split()) <= 10]
    cands += [(t, "PHRASE", "P2") for t in p2]
    cands += [(w, "PHRASE", "F") for grp in FORECAST.values() for w in grp]
    cands += [(n, "BROAD", "N") for n in names]

    # ---- protection sets ----
    places = sorted({r.geo_target_constant.name.lower() for r in q(c, f"""SELECT geo_target_constant.name, geo_target_constant.target_type
                     FROM geo_target_constant WHERE geo_target_constant.resource_name IN
                     ({','.join(repr(r.campaign_criterion.location.geo_target_constant) for r in q(c, "SELECT campaign_criterion.location.geo_target_constant, campaign.id FROM campaign_criterion WHERE campaign.id = 24257819466 AND campaign_criterion.type = 'LOCATION'"))})""")
                     if not r.geo_target_constant.name.isdigit()})
    probes = [m.format(s=s) for s in SERVICES for m in MODS] + EXTRA
    probes += [f"{s} {p}" for s in SERVICES[:12] for p in places] + [f"{s} in {p} md" for s in SERVICES[:12] for p in places]
    probes = [re.sub(r"\s+", " ", p.lower()).strip() for p in probes]
    protect = {"probe": probes, "converting": list(ever), "keyword": list(kws), "corpus_keep": protected_terms}

    kept, dropped = [], collections.Counter()
    drop_detail = collections.Counter()
    reason = {}
    existing_all = [(x, "BROAD") for x, _ in acct] + [n for cid in SEVEN for n in negs[cid]]
    seen = set()
    for text, mt, layer in cands:
        text = re.sub(r"\s+", " ", text.lower()).strip()
        if (text, mt) in seen: dropped["duplicate"] += 1; continue
        seen.add((text, mt))
        if layer in ("F", "P2") and len(text.split()) == 1 and text in geo:
            dropped["geo_word"] += 1; drop_detail[(layer, "geo_word")] += 1; reason[(text, layer)] = "Maryland place-name word"; continue
        if len(text.split()) == 1 and text in NEVER:
            dropped["never_list"] += 1; drop_detail[(layer, "never_list")] += 1; reason[(text, layer)] = "never-negate word"; continue
        hit = next((k for k, lst in protect.items() if any(blocks(text, mt, qq) for qq in lst)), None)
        if hit:
            dropped[f"blocks_{hit}"] += 1; drop_detail[(layer, hit)] += 1; reason[(text, layer)] = f"would block a {hit}"; continue
        # redundant only if the account-level list covers it, or EVERY heating campaign already has a covering negative
        def covered(neg_list):
            return any(blocks(x, "BROAD" if m == "BROAD" else "PHRASE", text) for x, m in neg_list if m in ("BROAD", "PHRASE"))
        if layer != "N" and (covered([(x, "BROAD") for x, _ in acct]) or all(covered(negs[cid]) for cid in SEVEN)):
            dropped["redundant_existing"] += 1; drop_detail[(layer, "redundant")] += 1; reason[(text, layer)] = "already covered on all 7"; continue
        kept.append((text, mt, layer))
    kept.sort()
    # effect on the heating corpus (counts only)
    eff = collections.Counter()
    for t, b in buckets.items():
        if any(blocks(x, m, t) for x, m, _ in kept): eff[b] += 1
    by_layer = collections.Counter(l for _, _, l in kept)
    f_kept = {g: [w for w in ws if (w, "PHRASE", "F") in kept] for g, ws in FORECAST.items()}
    f_dropped = sorted(w for ws in FORECAST.values() for w in ws if (w, "PHRASE", "F") not in kept)
    plan = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342", "plan_name": PLAN_NAME,
            "built_local": datetime.datetime.now(TZ).date().isoformat(), "authority": "owner request 2026-09-26: second check, phrase negatives, forecast low-intent negatives",
            "exact_list": EXACT_LIST, "exact_additions": exact_add, "new_list": NEW_LIST, "existing_new_list": existing_new,
            "members": [{"text": t, "match_type": m, "layer": l} for t, m, l in kept],  # contains corpus-derived text: never printed
            "members_sha1": hashlib.sha1("\n".join(f"{t}|{m}" for t, m, _ in kept).encode()).hexdigest()[:12],
            "by_layer": dict(by_layer), "dropped": dict(dropped), "drop_detail": {f"{k[0]}:{k[1]}": v for k, v in drop_detail.items()},
            "corpus_effect_terms_blocked_by_bucket": dict(eff), "forecast_kept": f_kept, "forecast_dropped": f_dropped,
            "probe_counts": {k: len(v) for k, v in protect.items()}, "campaigns": SEVEN,
            "forecast_drop_reasons": {w: reason.get((w, "F"), "?") for w in f_dropped}}
    plan["operation_count"] = len(exact_add) + (0 if existing_new else 1) + len(kept) + len(SEVEN)
    fp = approval_code(plan)
    if a.mode == "plan":
        plan["fingerprint"] = fp
        (PLANS / f"{PLAN_NAME}.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print(f"PLAN {PLAN_NAME} {fp} | ops {plan['operation_count']} | members sha1 {plan['members_sha1']}")
        print("  corpus buckets:", dict(collections.Counter(buckets.values())))
        print("  E exact additions (second check):", len(exact_add))
        print("  kept by layer:", dict(by_layer))
        print("  dropped:", dict(dropped))
        print("  drop detail:", plan["drop_detail"])
        print("  protection sets:", plan["probe_counts"])
        print("  heating corpus terms the new list would block, by bucket:", dict(eff))
        print("  FORECAST kept:", json.dumps(f_kept))
        print("  FORECAST dropped by guards:", {w: reason.get((w, "F"), "?") for w in f_dropped})
        return
    if a.fp != fp: sys.exit(f"ABORT fp {fp} != {a.fp}")
    if existing_new: sys.exit(f"ABORT: list exists {existing_new}")
    ga = c.get_service("GoogleAdsService"); ops = []
    for t in exact_add:
        m = c.get_type("MutateOperation"); cr = m.shared_criterion_operation.create
        cr.shared_set = c.get_service("SharedSetService").shared_set_path(CID, EXACT_LIST)
        cr.keyword.text = t; cr.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT; ops.append(m)
    sp = c.get_service("SharedSetService").shared_set_path(CID, -1)
    m = c.get_type("MutateOperation"); s = m.shared_set_operation.create
    s.resource_name = sp; s.name = NEW_LIST; s.type_ = c.enums.SharedSetTypeEnum.NEGATIVE_KEYWORDS; ops.append(m)
    for t, mt, _ in kept:
        m = c.get_type("MutateOperation"); cr = m.shared_criterion_operation.create
        cr.shared_set = sp; cr.keyword.text = t; cr.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, mt); ops.append(m)
    for cid in SEVEN:
        m = c.get_type("MutateOperation"); cs = m.campaign_shared_set_operation.create
        cs.campaign = c.get_service("CampaignService").campaign_path(CID, cid); cs.shared_set = sp; ops.append(m)
    rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.mutate_operations.extend(ops)
    rq.validate_only = True
    try:
        ga.mutate(request=rq)
    except Exception as ex:
        msgs = re.findall(r'message: "([^"]+)"', str(ex))
        sys.exit(f"VALIDATE FAIL {msgs[:3]}")
    print("validate_only PASS")
    rq.validate_only = False; resp = ga.mutate(request=rq)
    res = [getattr(r, f).resource_name for r in resp.mutate_operation_responses
           for f in ("shared_set_result", "shared_criterion_result", "campaign_shared_set_result") if r._pb.HasField(f)]
    new_set = next(x for x in res if "/sharedSets/" in x)
    rec = {"plan": PLAN_NAME, "fingerprint": fp, "executed_local": datetime.datetime.now(TZ).isoformat(),
           "created_count": len(res), "new_shared_set": new_set, "members_sha1": plan["members_sha1"], "exact_additions": len(exact_add)}
    (RECEIPTS / f"{PLAN_NAME}-EXECUTED.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("EXECUTED", len(res), "resources;", new_set)


def readback(c):
    plan = json.loads((PLANS / f"{PLAN_NAME}.json").read_text(encoding="utf-8"))
    sid = q(c, f"SELECT shared_set.id FROM shared_set WHERE shared_set.name = '{NEW_LIST}' AND shared_set.status = 'ENABLED'")[0].shared_set.id
    mem = sorted((r.shared_criterion.keyword.text.lower(), E(r.shared_criterion.keyword.match_type)) for r in q(c,
                 f"SELECT shared_criterion.keyword.text, shared_criterion.keyword.match_type, shared_set.id FROM shared_criterion WHERE shared_set.id = {sid}"))
    want = sorted((m["text"], m["match_type"]) for m in plan["members"])
    att = {str(r.campaign.id): E(r.campaign_shared_set.status) for r in q(c, f"SELECT campaign.id, campaign_shared_set.status, shared_set.id FROM campaign_shared_set WHERE shared_set.id = {sid}")}
    ex = {r.shared_criterion.keyword.text.lower() for r in q(c, f"SELECT shared_criterion.keyword.text, shared_set.id FROM shared_criterion WHERE shared_set.id = {EXACT_LIST}")}
    fails = []
    if mem != want: fails.append(f"members differ ({len(mem)} vs {len(want)})")
    if sorted(att) != sorted(SEVEN) or any(v != "ENABLED" for v in att.values()): fails.append(f"attachments {att}")
    if not set(plan["exact_additions"]) <= ex: fails.append("exact additions missing")
    kws = [r.ad_group_criterion.keyword.text.lower() for r in q(c, f"""SELECT ad_group_criterion.keyword.text, campaign.id FROM ad_group_criterion
            WHERE campaign.id IN ({','.join(SEVEN)}) AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE
            AND ad_group_criterion.status = 'ENABLED'""")]
    clash = sum(1 for k in kws if any(blocks(t, m, k) for t, m in mem))
    if clash: fails.append(f"{clash} enabled heating keywords blocked by the new list")
    print(f"new list {sid}: {len(mem)} members {dict(collections.Counter(m for _, m in mem))}, attached {len(att)} | exact list now {len(ex)} | "
          f"enabled heating keywords blocked: {clash}")
    print("READBACK FAILS:", fails or 0)
    p = RECEIPTS / f"{PLAN_NAME}-EXECUTED.json"; rec = json.loads(p.read_text(encoding="utf-8"))
    rec["readback"] = {"shared_set": str(sid), "members": len(mem), "fails": fails}; p.write_text(json.dumps(rec, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
