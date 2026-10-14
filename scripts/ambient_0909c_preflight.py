#!/usr/bin/env python3
"""LOCAL preflight for the third-pass packages. Zero API operations."""
from __future__ import annotations
import sys, json, re, unicodedata
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

state = json.load(open(EVID / "2026-09-09b-state-and-drift.json", encoding="utf-8"))
prot = json.load(open(EVID / "2026-09-09-protection-register.json", encoding="utf-8"))
neg = json.load(open(EVID / "2026-09-09c-negative-evidence.json", encoding="utf-8"))
plans = json.load(open(TOPPLANS / "AMBIENT-2026-09-09c-packages.json", encoding="utf-8"))
conv_all = [json.loads(l) for l in
            (EXPORTS / "search-terms-api-2026-09-09-converting-ACCOUNTWIDE.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
conv_five = [json.loads(l) for l in (EXPORTS / "search-terms-api-2026-09-09-converting.jsonl")
             .read_text(encoding="utf-8").splitlines() if l.strip()]
CONV = sorted({t["term"] for t in conv_all} | {t["term"] for t in conv_five})

fails = []


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

print("\n=== FINGERPRINTS DISJOINT FROM ALL PRIOR PACKAGES ===")
OLD = {"46C39C6B7091", "D448BFDE4650", "23BE8FF0F24C", "CE289F3508A2", "A435FA09AC97",
       "11A79347A296", "752BF95EBD7C", "DE376F91F449", "18143479027D", "05FBCBD34B4A"}
new = {p["fingerprint"] for p in plans.values()}
check(not (new & OLD), f"the {len(new)} new fingerprints collide with none of the 10 prior ones")

print("\n=== AMB-0909C-BUD-1 ===")
p = plans["AMB-0909C-BUD-1"]
DAYS, MAXM = 30.4, 13000.0
FIVE_B = {"15787409435": 141.45, "15787409438": 42.76, "15787409441": 176.15,
          "15787409444": 78.95, "15787409447": 26.32}
proposed = dict(FIVE_B)
for a in p["operations"]:
    bid = a["resource_id"]
    cur = int(a["current_state"].split("= ")[1].split(" ")[0])
    nm = int(a["proposed_state"].split("= ")[1].split(" ")[0])
    check(abs(buds[bid]["daily"] - cur / 1e6) < 0.005,
          f"budget {bid} before-state ${cur/1e6:.2f} matches live ${buds[bid]['daily']:.2f}")
    check(buds[bid]["refs"] == 1, f"budget {bid} referenced by exactly one campaign")
    check("per_campaign_limits" in a, f"budget {bid} carries its per-campaign limit block")
    proposed[bid] = nm / 1e6
tot = sum(proposed.values())
check(abs(tot - 421.55) < 0.005, f"combined daily total ${tot:.2f}")
check(tot * DAYS <= MAXM, f"steady-state ${tot*DAYS:,.2f} within ${MAXM:,.0f} "
                          f"(headroom ${MAXM-tot*DAYS:,.2f})")
check("15787409441" not in {a["resource_id"] for a in p["operations"]},
      "HVAC Installation budget untouched")
env = p["notes"]["future_safe_rollback"]
check(env["blind_restore_forbidden"] is True, "rollback block forbids a blind restore")
check(env["blind_restore_x30_4"] > MAXM,
      f"blind restore would be ${env['blind_restore_x30_4']:,.2f} = a breach, correctly flagged")
check(abs(env["compliant_envelope_for_the_two_campaigns_daily"] - (MAXM/DAYS - 396.55)) < 0.01,
      f"compliant two-campaign envelope ${env['compliant_envelope_for_the_two_campaigns_daily']:.2f}"
      f" is arithmetically correct")
check(25.00 <= env["compliant_envelope_for_the_two_campaigns_daily"],
      "the proposed $5 + $20 = $25 fits inside that envelope")

print("\n=== AMB-0909C-CPC-INST-2 ===")
p = plans["AMB-0909C-CPC-INST-2"]
check(len(p["operations"]) == 1, "exactly one operation")
a = p["operations"][0]
check(a["resource_id"] == "24132507747", "targets HVAC Installation only")
check(int(a["current_state"].split("= ")[1].split(" ")[0]) ==
      camps["24132507747"]["ceiling_micros"], "before-state matches live")
check(camps["24132507741"]["ceiling_micros"] == 25000000, "AC Repair still $25")
check(camps["24132507750"]["ceiling_micros"] == 25000000, "HVAC Repair still $25")
sl = p["notes"]["outcome_based_stop_loss"]
check(sl["gate_1"]["incremental_spend_since_execution"] == 280.00, "gate 1 is $280 incremental")
check(sl["gate_2"]["incremental_spend_since_execution"] == 560.00, "gate 2 is $560 incremental")
check("30-click" in sl["no_30_click_threshold"], "the 30-click threshold is explicitly excluded")
check("30000000" in sl["rollback_target"], "rollback target is exactly $30.00")
check("UNVERIFIED" in p["notes"]["TEST_STATUS"], "the test is labelled UNVERIFIED")
check(p["notes"]["corrected_economics"]["CORRECTED_campaign_level_raw_cpa"] == 161.33,
      "corrected raw CPA is $161.33, not $141.87")
check(p["notes"]["unique_lead_bounding"]["unique_leads_known"] is False,
      "unique lead count is stated as unknown, range 1-3")
check("7 SETTLED days" in p["notes"]["sequencing_constraint"]["separation"],
      "search-term expansion separation of >=7 settled days is stated")

print("\n=== AMB-0909C-NEG-SAVAGE ===")
p = plans["AMB-0909C-NEG-SAVAGE"]
check(len(p["operations"]) == 5, f"exactly 5 operations (got {len(p['operations'])})")
miss = [a for a in p["operations"] if (a["campaign_id"], a["criterion_id"]) not in negkey]
check(not miss, "all 5 targets live and ENABLED")
check(all(a["negative_text"].lower() == "savage" for a in p["operations"]),
      "every operation targets exactly 'savage'")
check(all(a["match_type"] == "PHRASE" for a in p["operations"]), "all PHRASE")
check(len({a["campaign_id"] for a in p["operations"]}) == 5, "one per campaign, all five")
check(neg["neg_core_savage_targeted"]["proven"] is True,
      "Savage MD proven ENABLED positive target on all five")
check(not any("licensed" in a["negative_text"].lower() for a in p["operations"]),
      "'licensed' is NOT in this package (held separately)")

print("\n=== AMB-0909C-NEG-COMMERCIAL ===")
p = plans["AMB-0909C-NEG-COMMERCIAL"]
check(len(p["operations"]) == 1, f"exactly 1 operation (got {len(p['operations'])})")
a = p["operations"][0]
check(a["shared_criterion_resource_name"] in acct, "target is a live member of set 11252984411")
check(a["match_type"] == "BROAD", "the live member is BROAD")
d = p["notes"]["duplicate_sweep"]
check(d["on_the_five_live_campaigns"] == 0,
      "duplicate sweep proves 0 duplicate 'commercial' negatives on the five live campaigns")
check(d["exact_token_commercial_negatives_account_wide"] == 5,
      "5 exact-token 'commercial' negatives exist account-wide, 4 of them in PAUSED campaigns")
check("BROAD" in a["rollback"], "rollback recreates 'commercial' as BROAD")
check(p["notes"]["effect_across_non_removed_campaigns"]["total_non_removed"] == 23,
      "effect documented across all 23 non-removed campaigns")
check("RAW" in a["raw_records_not_qualified_leads"],
      "historical records are labelled raw, not qualified leads")

print("\n=== AMB-0909C-COMP-1 ===")
p = plans["AMB-0909C-COMP-1"]
observed = {t["term"] for t in neg["competitor_observed_terms"]}
check(len(p["operations"]) == 3, f"exactly 3 operations (got {len(p['operations'])})")
for a in p["operations"]:
    txt, mt, cid = a["negative_text"], a["match_type"], a["campaign_id"]
    check(mt == "EXACT", f"{txt!r} uses EXACT (no PHRASE, no BROAD)")
    check(txt in observed, f"{txt!r} is a VERBATIM observed query, not an invented variant")
    check((cid, mt, norm(txt)) not in present, f"{txt!r} not already present")
    check(len(txt.split()) <= 10 and len(txt) <= 80, f"{txt!r} within word and char limits")
    n = norm(txt)
    bp = [x for x in prot["bofu_probes"] if norm(x) == n]
    bc = [x for x in CONV if norm(x) == n]
    bl = [x for x in prot["md_place_tokens"] if x and norm(x) == n]
    check(not bp, f"{txt!r} blocks 0 of 67 BOFU probes")
    check(not bc, f"{txt!r} blocks 0 of {len(CONV)} converting terms")
    check(not bl, f"{txt!r} blocks 0 of {len(prot['md_place_tokens'])} Maryland place tokens")
    check(not any(m in n.split() for m in
                  ("carrier", "trane", "lennox", "goodman", "daikin", "rheem", "york",
                   "mitsubishi", "amana", "bosch", "bryant", "ruud")),
          f"{txt!r} contains no manufacturer token")
print("\n  --- Anne Arundel county guard ---")
GUARD = ["anne arundel cooling and heating", "hvac anne arundel county",
         "hvac companies anne arundel county", "anne arundel county hvac repair",
         "hvac repair anne arundel county md", "arundel cooling and heating"]
for a in p["operations"]:
    n = norm(a["negative_text"])
    for g in GUARD:
        check(norm(g) != n, f"{a['negative_text']!r} [EXACT] does NOT block {g!r}")
check(not any(norm("maryland mechanical heating") == norm(a["negative_text"])
              for a in p["operations"]),
      "the withdrawn PHRASE 'maryland mechanical heating' is absent")

print("\n=== OPERATION COUNT ===")
tot_ops = sum(p["object_count"] for p in plans.values())
print(f"  new packages: {tot_ops} operations across {len(plans)} packages")
for n, p in plans.items():
    print(f"    {n:<28} {p['object_count']:>3}")
print(f"  carried-forward AMB-0909-ADS-1: 2")
print(f"  APPROVAL BLOCK TOTAL: {tot_ops + 2}")

print("\n" + "=" * 76)
print(f"PREFLIGHT: {len(fails)} FAIL")
for f in fails:
    print("  FAIL:", f)
print("=" * 76)
write(EVID / "2026-09-09c-local-preflight.json",
      {"fails": fails,
       "packages": {k: {"fingerprint": v["fingerprint"], "ops": v["object_count"],
                        "class": v["approval_class"]} for k, v in plans.items()},
       "new_operations_total": tot_ops, "approval_block_total": tot_ops + 2})
sys.exit(1 if fails else 0)
