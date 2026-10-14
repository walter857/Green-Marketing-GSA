#!/usr/bin/env python3
"""Ambient | 2026-10-02 | AMB-1002-NEG-EXACT-2: final high-confidence EXACT negatives (supersedes NEG-EXACT-1 D6ABF60771C3).

  build                      decide applied vs withheld per term, local checks, validate_only, fingerprint
  execute <FINGERPRINT> <N>  staged authorization 2026-10-02: write (explicit KeywordMatchType EXACT), read back match type + text

Decision rules (Green Marketing 2026-10-02): apply only high-confidence, in-scope terms; competitor names only when first-party
web evidence confirms the business (sources listed per term); 24-hour availability requests excluded; bare model / part /
capacity and thermostat setup/product queries excluded; AC-only, oil, water-heater, pellet-stove, vehicle and floor-heat
products are outside the approved heating services. Withheld: unconfirmed names, brand-only product queries, research
questions that can precede purchase. Never: near me, cost, price, quote, best, local, hire, emergency, manufacturers, places.
"""
from __future__ import annotations
import sys, json, re, csv, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, PLANS, RECEIPTS, E, CID, EXACT_NAME, CLIENT_DIR  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

NAME = "AMB-1002-NEG-EXACT-2"
C = json.loads((CLIENT_DIR / "exports" / "negative-candidates-2026-10-02.json").read_text(encoding="utf-8"))["valid"]
V = list(csv.DictReader((CLIENT_DIR / "exports" / "search-term-verdicts-2026-10-02.csv").open(encoding="utf-8")))
AGN = json.loads((CLIENT_DIR / "snapshots" / "snapshot-2026-10-02.json").read_text(encoding="utf-8"))["ad_groups"]
VERIFIED = {  # query -> first-party evidence (business website / listing found 2026-10-02)
    "booths hvac": "Boothe's HVAC company (confirmed 2026-10-02 web search)",
    "s f jones heating and cooling": "S.F. Jones Heating & Cooling (MD HVAC company)",
    "moon air elkton": "Moon Air (Elkton MD HVAC company)",
    "dodge heating and air": "Broady & Dodge Heating and Air (MD)",
    "coastal hvac annapolis": "Coastal Heating & Air Conditioning (Annapolis)",
    "max air heating & a c inc": "MaxAir Heating & A/C (MD)",
    "carroll mechanical columbia md": "Carroll Mechanical (Columbia MD)",
    "allpro hvac": "All-Pro Services (MD/DC HVAC)",
    "go ecco climate control": "Go Ecco Climate Control (Baltimore)",
    "home team heating and cooling": "HomeTeam Heating & Cooling (MD)",
    "howard mechanical hvac": "Howard Mechanical (Baltimore HVAC contractor)",
    "joey taylor hvac": "J.M. Taylor / Taylor Heating (owner name match; weaker identity, clearly not Ambient)",
    "maryland mechanical heating & cooling": "Maryland Mechanical Heating & Cooling (MD)",
    "stivers hvac inc": "Stivers HVAC Inc (Lexington KY)",
    "triple eee hvac": "Triple E Heating & Air (MD)",
    "bnb heating and cooling": "B&B Heating and Cooling Contractors (White Plains MD); B&B Air Conditioning & Heating (bbairconditioning.com, MD)",
    "cold comfort hvac rockville md": "Cold Comfort HVAC Services (Rockville MD)",
    "cold comfort hvac near me": "Cold Comfort HVAC Services (Rockville MD)",
    "falcon hvac": "Falcon HVAC (VA/MD)",
    "frosty heating and air conditioning": "Frosty's Heating & Cooling (frostysinc.com, Alexandria VA) and other Frosty's HVAC firms",
    "grove hvac maryland": "Grove Heating & Cooling (grovehvac.com, Crofton MD)",
    "grove heating and cooling crofton md": "Grove Heating & Cooling (grovehvac.com, Crofton MD)",
    "honest air mt airy": "Honest Air (honestairhvac.com, Mt Airy MD)",
    "hope plumbing heating and cooling": "Hope Plumbing, Heating & Cooling (hopeplumbing.com, Indiana)",
    "jiffy hvac": "Jiffy Plumbing & Heating (calljiffy.com, Hyattsville MD)",
    "ocean air hvac": "Ocean Air Heating & Cooling (oceanairhvac.com, Stevensville MD)",
    "powell and turner hvac": "Powell & Turner Heating & Cooling (Linthicum MD)",
    "smock heating & air": "Smock Heating & Air (smockhvac.com, Frederick MD)",
    "southern maryland heating and air waldorf md": "Southern Maryland Heating & Air (Waldorf MD)",
    "vito hvac": "Vito Services (vitoservices.com, Rockville MD)",
    "xzavier hvac solutions llc baltimore reviews": "Xzavier HVAC Solutions (xzavierhvacsolutionsllc.com)",
    "comfort zone heating and cooling": "Comfort Zone Heating & Air (Olney MD) / Comfort Zone Heating & Cooling (Parkton MD)",
    "highland hvac oakland md": "Highland HVAC LLC (Oakland MD)",
    "mays heating and air frederick md": "May's Heating & Air Conditioning (maysheatingandac.com, Frederick)",
}
UNVERIFIED = {"b&d hvac": "no Maryland 'B&D' HVAC firm found (only NY / MN / B&B variants)",
              "stanton hvac": "probably 'Staton' (Annapolis) but the spelling matches no firm - unproven",
              "coastal heat and air": "matches out-of-state firms and a Carrier product line - ambiguous",
              "harbor point heating and air": "no matching firm found"}
WITHHOLD = {"aube thermostat": "brand + product (manufacturer guard)", "what is geothermal heating": "research that can precede purchase",
            "do plumbers do boilers": "searcher choosing who services a boiler - possible buyer", "what is a furnace tune up": "research that can precede a tune-up purchase"}
norm = lambda t: " ".join(re.sub(r"[^\w&'+\- ]", " ", t.lower()).split())


def decide(c):
    q_ = c["query"]
    if q_ in WITHHOLD:
        return "WITHHELD", WITHHOLD[q_]
    if c["bucket"] == "competitor":
        if q_ in VERIFIED:
            return "APPLY", f"other-company navigation; verified: {VERIFIED[q_]}"
        return "WITHHELD", "competitor name unconfirmed: " + UNVERIFIED.get(q_, "no first-party evidence")
    reasons = {"availability": "explicit 24-hour request; Ambient books visits Mon-Fri 8-4 only",
               "model": "bare model / part / capacity lookup; no service-buying word",
               "thermostat_diy": "thermostat setup, programming, wiring or product spec - DIY/product, not a hire request",
               "info": "explicit DIY question", "ac": "air conditioning only; cooling is not an approved current service in these heating campaigns",
               "oil": "oil-fired equipment; Oil is OUT of the approved advertising scope", "water_heater": "water heater; not an approved heating service (Tankless OUT)",
               "pellet_stove": "pellet stove; not an approved service", "vehicle": "vehicle / RV equipment", "floor_heat": "electric floor-heat product"}
    return "APPLY", reasons.get(c["bucket"], c["reason"])


def rows_for(query, cid):
    return [v for v in V if v["search_term"] == query and v["campaign_id"] == cid]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    decisions = []
    for c in C:
        verdict, why = decide(c)
        rs = rows_for(c["query"], c["campaign_id"])
        conv = sum(float(r["recorded_conversions"]) for r in rs)
        if conv > 0 and verdict == "APPLY":
            verdict, why = "WITHHELD", f"has {conv} recorded conversion(s) - never negate a converting query without the lead record"
        decisions.append(dict(query=c["query"], match_type="EXACT", campaign=c["campaign"], campaign_id=c["campaign_id"],
                              ad_groups=[f"{AGN.get(g, {}).get('name', g)} ({g})" for g in c["ad_groups"]], scope="campaign",
                              sep=dict(impr=sum(int(r["SEP_impr"]) for r in rs), clicks=sum(int(r["SEP_clicks"]) for r in rs), cost=round(sum(float(r["SEP_cost"]) for r in rs), 2)),
                              oct=dict(impr=sum(int(r["OCT_impr"]) for r in rs), clicks=sum(int(r["OCT_clicks"]) for r in rs), cost=round(sum(float(r["OCT_cost"]) for r in rs), 2)),
                              reported_conversions=conv, verified_lead="none attributable (no click-ID or call-matched lead on this query)",
                              intent=rs[0]["intent"] if rs else "", decision=verdict, reason=why, bucket=c["bucket"],
                              existing_coverage="none (no account, shared, campaign or ad-group negative blocks it)",
                              conflict_check="blocks only this full query; no positive keyword equals it; longer buyer queries stay eligible"))
    applied = [d for d in decisions if d["decision"] == "APPLY"]
    applied.sort(key=lambda d: (d["campaign_id"], d["bucket"], d["query"]))
    plan = dict(plan_name=NAME, supersedes="AMB-1002-NEG-EXACT-1 D6ABF60771C3 (never executed; 98 terms; stale)", customer_id=CID, exact_account_name=EXACT_NAME,
                never_write_to_mcc="3373711342", approval_class="negative-keywords", authorization="staged authorization 2026-10-02 (Green Marketing)",
                work_order="work-orders/work-order-search-terms-sept-oct-2026-10-02.yaml", match_type="EXACT (explicit KeywordMatchType.EXACT)", scope="campaign level",
                operations=[dict(op="ADD_CAMPAIGN_NEGATIVE_EXACT", campaign_id=d["campaign_id"], text=d["query"]) for d in applied])
    plan["operation_count"] = len(plan["operations"])
    plan["fingerprint"] = approval_code({k: v for k, v in plan.items() if k != "fingerprint"})
    (CLIENT_DIR / "exports" / "negative-decisions-2026-10-02.json").write_text(json.dumps(decisions, indent=1), encoding="utf-8")
    c = client()
    identity_gate(c, verbose=False)
    have = {(str(r.campaign.id), norm(r.campaign_criterion.keyword.text), E(r.campaign_criterion.keyword.match_type)) for r in q(c,
            f"""SELECT campaign.id, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type FROM campaign_criterion
            WHERE campaign.id IN ({','.join(sorted({d['campaign_id'] for d in applied}))}) AND campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE""")}
    errs = [f"duplicate: {o}" for o in plan["operations"] if (o["campaign_id"], norm(o["text"]), "EXACT") in have]
    errs += [f"length: {o['text']}" for o in plan["operations"] if len(o["text"].split()) > 10 or len(o["text"]) > 80]
    if errs and mode == "build":
        sys.exit("HARD STOP:\n  " + "\n  ".join(errs))

    def ops():
        out = {}
        for o in plan["operations"]:
            x = c.get_type("CampaignCriterionOperation"); cr = x.create
            cr.campaign = c.get_service("CampaignService").campaign_path(CID, o["campaign_id"]); cr.negative = True
            cr.keyword.text = o["text"]; cr.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT
            out.setdefault(o["campaign_id"], []).append(x)
        return out

    def send(xs, validate):
        rq = c.get_type("MutateCampaignCriteriaRequest"); rq.customer_id = CID; rq.operations.extend(xs); rq.partial_failure = False; rq.validate_only = validate
        return c.get_service("CampaignCriterionService").mutate_campaign_criteria(request=rq)

    if mode == "build":
        pf = {}
        for cid, xs in ops().items():
            try:
                send(xs, True); pf[cid] = f"VALIDATED {len(xs)}"
            except Exception as ex:
                pf[cid] = "FAILED " + str(re.findall(r'message: "([^"]+)"', str(ex))[:3])
        if any(v.startswith("FAILED") for v in pf.values()):
            sys.exit(f"HARD STOP validate_only: {pf}")
        plan["preflight"] = pf
        plan["fingerprint"] = approval_code({k: v for k, v in plan.items() if k != "fingerprint"})
        (PLANS / f"{NAME}.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print(f"PLAN {NAME}: {plan['fingerprint']} / {plan['operation_count']} ops {pf}; withheld {sum(1 for d in decisions if d['decision'] == 'WITHHELD')}")
        return
    saved = json.loads((PLANS / f"{NAME}.json").read_text(encoding="utf-8")); fp = saved.pop("fingerprint")
    if not (fp == approval_code(saved) == sys.argv[2].upper() and int(sys.argv[3]) == saved["operation_count"] and saved["operations"] == plan["operations"]):
        sys.exit("ABORT: fingerprint or payload mismatch")
    out = RECEIPTS / f"{NAME}-EXECUTED.json"
    if out.exists():
        sys.exit("ABORT: receipt exists")
    rec = dict(plan=NAME, fingerprint=fp, started_local=datetime.datetime.now(TZ).isoformat(), created=[])
    for cid, xs in ops().items():
        try:
            rec["created"] += [r.resource_name for r in send(xs, False).results]
        except Exception as ex:
            rec["status"] = "PARTIAL" if rec["created"] else "FAILED_NOTHING_WRITTEN"; rec["failure"] = {"campaign": cid, "error": re.findall(r'message: "([^"]+)"', str(ex))[:3]}
            out.write_text(json.dumps(rec, indent=1), encoding="utf-8"); sys.exit(f"STOPPED at {cid}: {rec['failure']}")
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat()
    got = {}
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, campaign_criterion.negative
            FROM campaign_criterion WHERE campaign.id IN ({','.join(sorted({o['campaign_id'] for o in plan['operations']}))}) AND campaign_criterion.type = 'KEYWORD'"""):
        got[(str(r.campaign.id), norm(r.campaign_criterion.keyword.text))] = (E(r.campaign_criterion.keyword.match_type), r.campaign_criterion.negative, str(r.campaign_criterion.criterion_id))
    rec["readback"] = [dict(campaign=o["campaign_id"], text=o["text"], saved=got.get((o["campaign_id"], norm(o["text"]))),
                            ok=got.get((o["campaign_id"], norm(o["text"])), ("", False, ""))[:2] == ("EXACT", True)) for o in plan["operations"]]
    rec["status"] = "EXECUTED" if all(x["ok"] for x in rec["readback"]) else "EXECUTED_READBACK_FAIL"
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(f"{NAME} {fp}: {rec['status']} {sum(x['ok'] for x in rec['readback'])}/{len(rec['readback'])} EXACT verified at {rec['finished_local']}")


if __name__ == "__main__":
    main()
