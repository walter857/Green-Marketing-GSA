#!/usr/bin/env python3
"""Audit the ACCOUNT-LEVEL negative keyword list 11252984411 in its own right.

It applies to all 23 non-removed campaigns, is not visible in campaign_shared_set, and
reports member_count 0, so campaign-level removals cannot override it.
"""
from __future__ import annotations
import sys, json, re, unicodedata, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

c = client()
struct = json.load(open(EVID / "2026-09-09-structure.json", encoding="utf-8"))
prot = json.load(open(EVID / "2026-09-09-protection-register.json", encoding="utf-8"))
ident = json.load(open(EVID / "2026-09-09-identity-and-structure.json", encoding="utf-8"))
conv_all = [json.loads(l) for l in
            (EXPORTS / "search-terms-api-2026-09-09-converting-ACCOUNTWIDE.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
conv_five = [json.loads(l) for l in (EXPORTS / "search-terms-api-2026-09-09-converting.jsonl")
             .read_text(encoding="utf-8").splitlines() if l.strip()]
CONV = sorted({t["term"] for t in conv_all} | {t["term"] for t in conv_five})
convmeta = defaultdict(lambda: [0.0, 0.0])
for t in conv_all:
    convmeta[t["term"]][0] += t["conversions"]
    convmeta[t["term"]][1] += t["all_conversions"]
for t in conv_five:
    convmeta[t["term"]][0] += t["conversions"]
    convmeta[t["term"]][1] += t["all_conversions"]

SET_ID = "11252984411"

print("=== FRESH READ OF THE ACCOUNT-LEVEL SET, WITH RESOURCE NAMES ===")
members = []
for r in q(c, f"""
    SELECT shared_criterion.resource_name, shared_criterion.shared_set,
           shared_criterion.criterion_id, shared_criterion.type,
           shared_criterion.keyword.text, shared_criterion.keyword.match_type
    FROM shared_criterion
    WHERE shared_set.id = {SET_ID}
"""):
    x = r.shared_criterion
    members.append({"resource_name": x.resource_name, "criterion_id": str(x.criterion_id),
                    "text": x.keyword.text, "match": E(x.keyword.match_type),
                    "type": E(x.type_)})
print(f"members: {len(members)}  by match: {dict(Counter(m['match'] for m in members))}")

camps = [x for x in ident["campaigns"] if x["status"] != "REMOVED"]
print(f"campaigns this list applies to: {len(camps)} non-removed "
      f"({sum(1 for x in camps if x['status']=='ENABLED')} ENABLED, "
      f"{sum(1 for x in camps if x['status']=='PAUSED')} PAUSED)")
print("  -> a removal from this list can only change LIVE delivery on the 5 ENABLED campaigns")


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def blocks(neg, mt, term):
    tw = norm(term).split()
    n = norm(neg)
    if mt == "BROAD":
        return bool(n.split()) and set(n.split()) <= set(tw)
    if mt == "PHRASE":
        return (" " + n + " ") in (" " + " ".join(tw) + " ")
    return n == " ".join(tw)


# ---- what does each member block? ----
MANU = {"lennox", "carrier", "trane", "goodman", "daikin", "rheem", "amana", "bosch",
        "mitsubishi", "armstrong", "burnham", "spacepak", "aciq", "york", "bryant",
        "ruud", "navien", "rinnai"}
FORBIDDEN = {"al", "american", "mr", "ambient", "cheap", "affordable", "emergency", "cost",
             "price", "pricing", "company", "companies", "contractor", "technician", "dealer",
             "repair", "replace", "replacement", "installation", "install", "service",
             "commercial", "residential", "maryland", "md", "local", "best", "hire", "quote",
             "free", "licensed", "estimate", "near", "me"}
SERVICE_ONLY = {"thermostat", "thermostats", "humidifier", "dehumidifier", "ductwork",
                "ducts", "duct", "boiler", "furnace", "geothermal", "tankless", "condenser",
                "compressor", "coil", "heat", "heater", "heating", "cooling", "hvac", "ac"}
MD = set(prot["md_place_tokens"])

rows = []
for mmb in members:
    t = norm(mmb["text"])
    tw = set(t.split())
    probes = [p for p in prot["bofu_probes"] if blocks(mmb["text"], mmb["match"], p)]
    convs = [x for x in CONV if blocks(mmb["text"], mmb["match"], x)]
    if tw & MANU:
        v, why = "REMOVE", "supported manufacturer token, applied account-wide"
    elif mmb["match"] == "BROAD" and tw & FORBIDDEN:
        v, why = "REMOVE", f"BROAD negative on a forbidden generic {sorted(tw & FORBIDDEN)}"
    elif tw <= SERVICE_ONLY and tw:
        v, why = "REMOVE", "confirmed Ambient service word with no competitor component"
    elif tw & MD and not (tw - MD):
        v, why = "REMOVE", "names a live Maryland target location"
    elif probes:
        v, why = "REMOVE", f"blocks {len(probes)} protected BOFU probes"
    else:
        v, why = "KEEP", "competitor / entity / out-of-scope token"
    rows.append({**mmb, "verdict": v, "why": why, "n_probes": len(probes),
                 "n_converting": len(convs),
                 "conversions_at_risk": round(sum(convmeta[x][0] for x in convs), 2),
                 "all_conversions_at_risk": round(sum(convmeta[x][1] for x in convs), 2),
                 "probes": probes})

print(f"\n=== ACCOUNT-LEVEL TRIAGE: {dict(Counter(r['verdict'] for r in rows))} ===")
rm = [r for r in rows if r["verdict"] == "REMOVE"]
print(f"\n--- REMOVE ({len(rm)}) ---")
for r in sorted(rm, key=lambda r: (-r["n_probes"], -r["conversions_at_risk"], r["text"])):
    print(f"  {r['match']:<7} {r['text']!r:<28} probes={r['n_probes']:<3} "
          f"convTerms={r['n_converting']:<3} conv={r['conversions_at_risk']:<5} "
          f"allconv={r['all_conversions_at_risk']:<6} {r['why']}")
print(f"\n--- KEEP: {len(rows)-len(rm)} members retained ---")
print("  by match:", dict(Counter(r["match"] for r in rows if r["verdict"] == "KEEP")))

# ---- build the package ----
TARGET = {"customer_id": CID, "exact_child_account_name": EXACT_NAME,
          "manager_customer_id": GM_MANAGER, "vertical": "heating-cooling",
          "primary_service": "AC Repair",
          "related_services": ["HVAC Repair", "HVAC Installation", "HVAC Replacement",
                               "Gas Boiler Repair"]}
ops = []
for r in sorted(rm, key=lambda r: r["text"]):
    ops.append({
        "operation": "REMOVE_SHARED_LIST_NEGATIVE", "resource": "shared_criterion",
        "shared_set_id": SET_ID,
        "shared_criterion_resource_name": r["resource_name"],
        "criterion_id": r["criterion_id"], "match_type": r["match"],
        "negative_text": r["text"],
        "current_state": f"account-level negative KEYWORD [{r['match']}] {r['text']!r} "
                         f"in shared set {SET_ID}",
        "proposed_state": "REMOVED from the account-level list",
        "reason": r["why"],
        "bofu_probes_unblocked": r["probes"],
        "conversions_at_risk_if_left": r["conversions_at_risk"],
        "all_conversions_at_risk_if_left": r["all_conversions_at_risk"],
        "rollback": f"re-add {r['text']!r} [{r['match']}] to shared set {SET_ID}",
        "risk": "MEDIUM - account-level scope; affects all 23 non-removed campaigns, but "
                "only the 5 ENABLED ones can serve",
        "unrelated_resource_assertion":
            f"shared set {SET_ID} member count must fall from {len(members)} to "
            f"{len(members)-len(rm)}; the other 16 shared sets must be untouched and none "
            f"may become attached to the five campaigns"})

plan = {"plan_name": "AMB-0909-NEG-RM-2", "approval_class": "DESTRUCTIVE-removal-ACCOUNT-LEVEL",
        "generated_local": datetime.datetime.now(TZ).isoformat(), "target": TARGET,
        "summary": f"Remove {len(ops)} members from the ACCOUNT-LEVEL negative keyword list "
                   f"{SET_ID}. These block supported manufacturers and confirmed Ambient "
                   f"services across every campaign, and campaign-level removal cannot "
                   f"override them.",
        "object_count": len(ops), "partial_failure": False, "atomic": True,
        "operations": ops,
        "notes": {
            "why_a_separate_package":
                "Account-level negatives live in a shared_set of type "
                "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS. They never appear in campaign_shared_set, "
                "the API reports member_count 0 for the set, and a campaign-level removal "
                "does NOT override them. AMB-0909-NEG-RM-1 alone will not unblock the "
                "manufacturer terms.",
            "dependency":
                "AMB-0909-NEG-RM-1 and AMB-0909-NEG-RM-2 must BOTH be approved for the "
                "manufacturer unblock to take effect. Approving only one leaves the block "
                "in place at the other layer.",
            "scope_proof":
                f"The list applies to all {len(camps)} non-removed campaigns. "
                f"{sum(1 for x in camps if x['status']=='ENABLED')} are ENABLED (the five in "
                f"scope) and {sum(1 for x in camps if x['status']=='PAUSED')} are PAUSED and "
                f"cannot serve, so removal changes live delivery only on the five.",
            "set_member_count_before": len(members),
            "set_member_count_after": len(members) - len(rm)}}
plan["fingerprint"] = approval_code({"target": TARGET, "plan": plan["plan_name"],
                                     "operations": ops})
(CLIENT_DIR / "plans" / "AMB-0909-NEG-RM-2.json").write_text(
    json.dumps(plan, indent=1, default=str), encoding="utf-8")
allp = json.load(open(TOPPLANS / "AMBIENT-2026-09-09-packages.json", encoding="utf-8"))
allp["AMB-0909-NEG-RM-2"] = plan
(TOPPLANS / "AMBIENT-2026-09-09-packages.json").write_text(
    json.dumps(allp, indent=1, default=str), encoding="utf-8")
write(EVID / "2026-09-09-account-level-triage.json",
      {"members": rows, "set_id": SET_ID, "member_count": len(members),
       "campaigns_affected": len(camps)})
print(f"\n=== AMB-0909-NEG-RM-2 ops={len(ops)} fingerprint={plan['fingerprint']} ===")
print(f"    account-level set {SET_ID}: {len(members)} -> {len(members)-len(rm)} members")
