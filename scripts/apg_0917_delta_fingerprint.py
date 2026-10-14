#!/usr/bin/env python3
"""Validate + fingerprint the two 2026-09-17 delta plans. No mutations."""
from __future__ import annotations
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_yaml            # noqa: E402
from gm_gsa.safety import approval_code, SECRET_KEY_PATTERN  # noqa: E402

PLANS = ROOT / "clients/apogee-lawns/plans"
fails = []
def chk(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' -> ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)

print("=" * 78 + "\nDELTA PLAN VALIDATION\n" + "=" * 78)

out = {}
for pid in ("APG-0917-CALL-N", "APG-0917-GTM-P"):
    p = PLANS / f"{pid}.yaml"
    print(f"\n--- {pid}")
    raw = p.read_text(encoding="utf-8")
    d = load_yaml(str(p))
    chk(isinstance(d, dict), "loads as a YAML mapping")
    chk(d["plan_id"] == pid, "plan_id matches filename", d["plan_id"])
    hits = [k for k in re.findall(r"^\s*([A-Za-z0-9_.-]+):", raw, re.M)
            if SECRET_KEY_PATTERN.search(k)]
    chk(not hits, "no key trips SECRET_KEY_PATTERN", str(hits))
    chk("8164626278" in raw, "child customer id present")
    chk("337-371-1342" not in raw, "manager id never written in dashed mutable form")
    fp = approval_code(d)
    out[pid] = fp
    print(f"  FINGERPRINT: {fp}")

print("\n" + "=" * 78 + "\nCROSS-PLAN + RED TEAM\n" + "=" * 78)
n = load_yaml(str(PLANS / "APG-0917-CALL-N.yaml"))
g = load_yaml(str(PLANS / "APG-0917-GTM-P.yaml"))

chk(out["APG-0917-CALL-N"] != out["APG-0917-GTM-P"], "the two fingerprints differ")
prior = {"9BA1F4AE3CCA", "D1CAB205DDDA", "849EAED2873F", "7BC3407302B2", "F0C6FA2128A9",
         "136E939A3206", "4022CBA7FD51", "5993F8998BCF", "FEB175ADDEEA", "C52D14071B08",
         "FC0E0B156F60", "DB9391A883A7", "2871DD2A5227"}
chk(not (set(out.values()) & prior), "neither collides with any prior fingerprint")

# CALL-N specifics
chk(n["mutation_summary"]["total_mutations"] == 2, "CALL-N mutation count is 2")
chk(len(n["objects"]) == 2, "CALL-N object count is 2")
chk(n["website_call_action_metadata_finding"]["mutations_proposed_against_7773043879"] == 0,
    "CALL-N proposes zero ops on 7773043879")
sched = n["objects"][0]["ad_schedule_targets"]
chk(len(sched) == 6, "6 ad-schedule targets")
chk(all(s["day_of_week"] != "SUNDAY" for s in sched), "SUNDAY absent")
wk = [s for s in sched if s["day_of_week"] != "SATURDAY"]
chk(all(s["start_hour"] == 8 and s["end_hour"] == 17 for s in wk), "Mon-Fri 08:00-17:00")
sat = [s for s in sched if s["day_of_week"] == "SATURDAY"][0]
chk(sat["start_hour"] == 8 and sat["end_hour"] == 12, "Sat 08:00-12:00")
chk(all(s["end_hour"] > s["start_hour"] for s in sched), "every window has end > start")
chk(len({s["day_of_week"] for s in sched}) == 6, "no duplicate day")
ph = n["objects"][0]["field_values"]["call_asset.phone_number"]
chk(re.fullmatch(r"\d{10}", ph) is not None, "phone is 10 raw digits", ph)
chk(ph == "4022027261", "phone is the verified receptionist line", ph)
chk(n["objects"][0]["field_values"]["call_asset.call_conversion_reporting_state"]
    == "USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION", "resource-level call conversion reporting")
chk(n["objects"][0]["field_values"]["call_asset.call_conversion_action"].endswith("/7773013199"),
    "points at the AD_CALL action 7773013199")
chk(n["objects"][1]["field_type"] == "CALL", "campaign_asset field_type CALL")
chk(n["objects"][1]["campaign"].endswith("/24257151015"), "linked to campaign 24257151015")
chk(n["target"]["campaign_status_after_this_plan"] == "PAUSED", "campaign stays PAUSED")

# GTM-P specifics
chk(g["publication_boundary"]["container_versions_to_create"] == 0, "GTM-P creates 0 versions")
chk(g["publication_boundary"]["publishes"] == 0, "GTM-P publishes 0")
chk(g["publication_boundary"]["submit_button_used"] is False, "GTM-P never presses Submit")
chk(g["publication_gate"]["state"] == "BLOCKED", "publication gate BLOCKED")
chk(g["whatconverts_dni_determination"]["verdict"]
    == "WHATCONVERTS_IS_ACTIVELY_REPLACING_THE_NUMBER", "DNI verdict recorded")
chk(g["mutation_summary"]["google_ads_api_mutations"] == 0, "GTM-P issues 0 Google Ads mutations")
chk(g["mutation_summary"]["wordpress_changes"] == 0, "GTM-P makes 0 WordPress changes")
chk(g["mutation_summary"]["whatconverts_changes"] == 0, "GTM-P makes 0 WhatConverts changes")
chk(len(g["objects"]) == 4, "GTM-P object count is 4")
t2 = next(o for o in g["objects"] if o["ordinal"] == 2)
chk(t2["condition_3_exact"]["value"] == ".+", "condition 3 regex is exactly .+")
chk(t2["condition_3_exact"]["variable"] == "{{DLV | lead_id}}", "condition 3 variable is DLV | lead_id")
chk(t2["conditions_before"] == t2["conditions_after"][:2], "conditions 1 and 2 untouched")
chk(len(t2["conditions_after"]) == 3, "trigger ends with 3 conditions")
t3 = next(o for o in g["objects"] if o["ordinal"] == 3)
chk(t3["trigger_type"] == "Page View", "new trigger is Page View")
chk(re.fullmatch(r"\^/permanent-christmas-lights-lincoln-ne/\?\$",
                 t3["conditions"][1].split("matches RegEx ")[1]) is not None,
    "LP path regex anchored both ends")
t4 = next(o for o in g["objects"] if o["ordinal"] == 4)
chk(t4["fields"]["conversion_id"] == "18453077620", "website-call conversion id")
chk(t4["fields"]["conversion_label"] == "lp3jCKf5vPocEPS8jt9E", "website-call label")
chk(t4["fields"]["phone_conversion_number"] == "402-526-5754",
    "number to replace matches what the paid page renders")
chk(t4["built_but_not_published"] is True, "website-call tag built, not published")
chk(t4["conversion_action_state_unchanged"] == "SECONDARY", "7773043879 stays SECONDARY")
chk(t4["triggering"] == t3["name"], "tag 4 fires on trigger 3")

# The two numbers must not be confused with each other
chk(n["objects"][0]["field_values"]["call_asset.phone_number"] == "4022027261"
    and t4["fields"]["phone_conversion_number"] == "402-526-5754",
    "ad-call number and page-replacement number are deliberately different")

print("\n" + "=" * 78)
if fails:
    print(f"RED TEAM: {len(fails)} FAILURES")
    for f in fails:
        print("   - " + f)
    sys.exit(1)
print("RED TEAM: 0 FAILURES\n")
print(f"  APG-0917-CALL-N   {out['APG-0917-CALL-N']}   ->  APPROVE APG CALL-ASSET {out['APG-0917-CALL-N']}")
print(f"  APG-0917-GTM-P    {out['APG-0917-GTM-P']}   ->  APPROVE APG GTM DELTA {out['APG-0917-GTM-P']}")
print("=" * 78)
