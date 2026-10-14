#!/usr/bin/env python3
"""LOCAL preflight for the correction packages. Zero API operations."""
from __future__ import annotations
import sys, json, re, unicodedata
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

state = json.load(open(EVID / "2026-09-09b-state-and-drift.json", encoding="utf-8"))
prot = json.load(open(EVID / "2026-09-09-protection-register.json", encoding="utf-8"))
plans = json.load(open(TOPPLANS / "AMBIENT-2026-09-09b-packages.json", encoding="utf-8"))
conv_all = [json.loads(l) for l in
            (EXPORTS / "search-terms-api-2026-09-09-converting-ACCOUNTWIDE.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
conv_five = [json.loads(l) for l in (EXPORTS / "search-terms-api-2026-09-09-converting.jsonl")
             .read_text(encoding="utf-8").splitlines() if l.strip()]
CONV = sorted({t["term"] for t in conv_all} | {t["term"] for t in conv_five})

fails, warns = [], []


def check(cond, msg):
    print(f"  [{'PASS' if cond else 'FAIL'}] {msg}")
    if not cond:
        fails.append(msg)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


negs = state["live"]["campaign_negatives"]
negkey = {(n["camp"], n["crit"]): n for n in negs}
present = {(n["camp"], n["match"], norm(n["text"])) for n in negs}
acct = {a["rn"]: a for a in state["live"]["account_level"]}
buds = state["live"]["budgets"]
camps = state["live"]["campaigns"]

print("=== FINGERPRINT INTEGRITY ===")
for n, p in plans.items():
    rec = approval_code({"target": p["target"], "plan": n, "operations": p["operations"]})
    check(rec == p["fingerprint"], f"{n} recomputes to {rec}")

print("\n=== NO FINGERPRINT COLLIDES WITH A PRIOR PACKAGE ===")
OLD = {"46C39C6B7091", "D448BFDE4650", "23BE8FF0F24C", "CE289F3508A2", "A435FA09AC97",
       "11A79347A296"}
new = {p["fingerprint"] for p in plans.values()}
check(not (new & OLD), f"new fingerprints {sorted(new)} are disjoint from the six prior ones")

print("\n=== AMB-0909B-BUD-1 ===")
p = plans["AMB-0909B-BUD-1"]
DAYS, MAXM = 30.4, 13000.0
FIVE_B = {"15787409435": 141.45, "15787409438": 42.76, "15787409441": 176.15,
          "15787409444": 78.95, "15787409447": 26.32}
proposed = dict(FIVE_B)
for a in p["operations"]:
    bid = a["resource_id"]
    cur = int(a["current_state"].split("= ")[1].split(" ")[0])
    new_m = int(a["proposed_state"].split("= ")[1].split(" ")[0])
    check(abs(buds[bid]["daily"] - cur / 1e6) < 0.005,
          f"budget {bid} before-state ${cur/1e6:.2f} matches live ${buds[bid]['daily']:.2f}")
    check(buds[bid]["refs"] == 1, f"budget {bid} referenced by exactly one campaign")
    check(new_m < cur, f"budget {bid} decreases ${cur/1e6:.2f} -> ${new_m/1e6:.2f}")
    proposed[bid] = new_m / 1e6
tot = sum(proposed.values())
check(abs(tot - 421.55) < 0.005, f"proposed combined daily total is ${tot:.2f}")
check(tot * DAYS <= MAXM,
      f"30.4-day exposure ${tot*DAYS:,.2f} is within the ${MAXM:,.0f} maximum "
      f"(headroom ${MAXM - tot*DAYS:,.2f})")
check(433.33 * DAYS > MAXM,
      f"confirms the superseded package: $433.33 x 30.4 = ${433.33*DAYS:,.2f} BREACHES the cap")
untouched = set(FIVE_B) - {a["resource_id"] for a in p["operations"]}
check(all(abs(proposed[b] - FIVE_B[b]) < 0.005 for b in untouched),
      f"the {len(untouched)} untouched budgets keep their live amounts")
check("15787409441" in untouched, "HVAC Installation budget is NOT changed (contaminated-IS fix)")
sept_max = 1319.49 + 465.63 + tot * 20
check(sept_max <= MAXM,
      f"September maximum if executed 2026-09-10 = ${sept_max:,.2f} "
      f"(billed $1,319.49 + change-day $465.63 + {tot:.2f} x 20 calendar days)")

print("\n=== AMB-0909B-CPC-INST-1 ===")
p = plans["AMB-0909B-CPC-INST-1"]
check(len(p["operations"]) == 1, "exactly one operation (Installation only)")
a = p["operations"][0]
check(a["resource_id"] == "24132507747", "targets HVAC Installation 24132507747")
cur = camps[a["resource_id"]]["ceiling_micros"]
stated = int(a["current_state"].split("= ")[1].split(" ")[0])
check(stated == cur, f"before-state {stated} matches live {cur}")
check(camps["24132507747"]["bidding"] == "TARGET_SPEND", "bidding is TARGET_SPEND")
check(a["field_mask"] == ["target_spend.cpc_bid_ceiling_micros"], "field mask is ceiling-only")
check(camps["24132507741"]["ceiling_micros"] == 25000000,
      "AC Repair ceiling untouched at $25.00 (effective delivery hold)")
check(camps["24132507750"]["ceiling_micros"] == 25000000,
      "HVAC Repair ceiling untouched at $25.00 ($60 recommendation withdrawn)")
check(p["notes"]["bid_adjustment_audit"]["highest_modifier_found"] <= 1.0,
      "no bid modifier above x1.0 can raise the effective bid past $65")

print("\n=== AMB-0909B-NEG-A ===")
p = plans["AMB-0909B-NEG-A"]
camp_ops = [a for a in p["operations"] if a["operation"] == "REMOVE_CAMPAIGN_NEGATIVE_KEYWORD"]
acct_ops = [a for a in p["operations"] if a["operation"] == "REMOVE_SHARED_LIST_NEGATIVE"]
check(len(camp_ops) == 15, f"15 campaign-level removals (got {len(camp_ops)})")
check(len(acct_ops) == 1, f"1 account-level removal (got {len(acct_ops)})")
miss = [a for a in camp_ops if (a["campaign_id"], a["criterion_id"]) not in negkey]
check(not miss, f"all {len(camp_ops)} campaign targets resolve to a live ENABLED negative")
mism = [a for a in camp_ops
        if (a["campaign_id"], a["criterion_id"]) in negkey
        and (norm(negkey[(a['campaign_id'], a['criterion_id'])]["text"]) != norm(a["negative_text"])
             or negkey[(a['campaign_id'], a['criterion_id'])]["match"] != a["match_type"])]
check(not mism, "every campaign target's text and match type match the live resource")
check(all(a["shared_criterion_resource_name"] in acct for a in acct_ops),
      "the account-level target is still a live member of set 11252984411")
texts = sorted({a["negative_text"].lower() for a in p["operations"]})
check(texts == ["commercial", "free", "licensed", "savage"],
      f"exactly the four Package A texts: {texts}")
check(len({(a.get('campaign_id'), a['criterion_id']) for a in camp_ops}) == len(camp_ops),
      "no duplicate campaign removal targets")
for t in ["savage", "free", "licensed"]:
    n = sum(1 for a in camp_ops if a["negative_text"].lower() == t)
    check(n == 5, f"{t!r} removed from all 5 campaigns ({n})")
NOT_IN_A = {"carrier", "trane", "lennox", "goodman", "rheem", "mitsubishi", "daikin", "amana",
            "bosch", "bryant", "armstrong", "ruud", "thermostat", "thermostats", "humidifier",
            "dehumidifier", "al", "american", "mr", "geothermal maryland",
            "daikin cerca de mi", "trane installers near me",
            "trane authorized dealers near me", "carrier enterprise laurel",
            "carrier mid atlantic near me", "carrier mid atlantic hanover maryland",
            "ce carrier enterprise near me", "daikin comfort technologies locations",
            "daikin elkridge md"}
check(not (set(texts) & NOT_IN_A),
      f"none of the {len(NOT_IN_A)} held terms (manufacturers, services, dealer, supply-house, "
      f"al/american/mr) appears in Package A")

print("\n=== AMB-0909B-COMP-1 ===")
p = plans["AMB-0909B-COMP-1"]
for a in p["operations"]:
    txt, mt, cid = norm(a["negative_text"]), a["match_type"], a["campaign_id"]
    check(mt in ("PHRASE", "EXACT"), f"{a['negative_text']!r} uses {mt}, not BROAD")
    check(len(a["negative_text"].split()) <= 10,
          f"{a['negative_text']!r} within the 10-word limit ({len(a['negative_text'].split())})")
    check(len(a["negative_text"]) <= 80, f"{a['negative_text']!r} within the 80-char limit")
    check((cid, mt, txt) not in present, f"{a['negative_text']!r} not already present")
    check("entity_verification" in a and a["entity_verification"].get("sources"),
          f"{a['negative_text']!r} carries entity verification with sources")
    # collision tests
    def blocks(term):
        if mt == "EXACT":
            return norm(term) == txt
        return (" " + txt + " ") in (" " + norm(term) + " ")
    bad_probe = [x for x in prot["bofu_probes"] if blocks(x)]
    bad_conv = [x for x in CONV if blocks(x)]
    bad_place = [x for x in prot["md_place_tokens"] if x and blocks(x)]
    check(not bad_probe, f"{a['negative_text']!r} blocks 0 of 67 BOFU probes")
    check(not bad_conv, f"{a['negative_text']!r} blocks 0 of {len(CONV)} converting terms")
    check(not bad_place, f"{a['negative_text']!r} blocks 0 of "
                         f"{len(prot['md_place_tokens'])} Maryland place tokens")
PROTECTED_COUNTY = ["anne arundel cooling and heating", "hvac anne arundel county",
                    "hvac companies anne arundel county", "anne arundel county hvac repair",
                    "hvac repair anne arundel county md"]
print("\n  --- explicit Anne Arundel County guard ---")
for a in p["operations"]:
    _t, _m = norm(a["negative_text"]), a["match_type"]
    for probe in PROTECTED_COUNTY:
        hit = (norm(probe) == _t) if _m == "EXACT" else (
            (" " + _t + " ") in (" " + norm(probe) + " "))
        check(not hit, f"{a['negative_text']!r} [{_m}] does NOT block {probe!r}")

DROPPED = {"sq ft house", "how much is hvac system", "all about air", "home comfort hvac",
           "arundel cooling and heating"}
check(not ({norm(a["negative_text"]) for a in p["operations"]} & DROPPED),
      "none of the four withdrawn candidates is present")

print("\n" + "=" * 76)
print(f"PREFLIGHT: {len(fails)} FAIL, {len(warns)} WARN")
for f in fails:
    print("  FAIL:", f)
print("=" * 76)
write(EVID / "2026-09-09b-local-preflight.json",
      {"fails": fails, "warns": warns,
       "packages": {k: {"fingerprint": v["fingerprint"], "ops": v["object_count"],
                        "class": v["approval_class"]} for k, v in plans.items()}})
sys.exit(1 if fails else 0)
