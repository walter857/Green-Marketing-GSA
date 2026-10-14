#!/usr/bin/env python3
"""Self-review of the Apogee 2026-09-28 run-C measurement-repair package. Local files only; no API call.
Prints check names and counts only. Exit 1 on any failure."""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.work_orders import validate_work_order  # noqa: E402

CL = ROOT / "clients" / "apogee-lawns"
PKG = CL / "audits" / "2026-09-28-measurement-repair"
EV = ROOT / "reports" / "apogee-lawns" / "evidence"
res: list[tuple[str, bool, str]] = []


def check(n, ok, d=""):
    res.append((n, bool(ok), str(d)))


prof = yaml.safe_load((CL / "client.yaml").read_text(encoding="utf-8"))
for wo in (CL / "work-order.yaml", CL / "work-orders" / "work-order-measurement-repair-handoff-2026-09-28.yaml"):
    e = validate_work_order(yaml.safe_load(wo.read_text(encoding="utf-8")), prof)
    check(f"work order valid: {wo.name}", not e, "; ".join(e))
task = yaml.safe_load((CL / "work-orders" / "work-order-measurement-repair-handoff-2026-09-28.yaml").read_text(encoding="utf-8"))
check("task mode is draft/read", task["work_order"]["task"]["mode"] in ("read", "draft"))

R = json.loads((EV / "2026-09-28c-reads.json").read_text(encoding="utf-8"))
check("fresh identity PASS", R["identity_pass"])
check("fresh reads had 0 errors", not R["errors"], list(R["errors"]))
check("campaign status preserved as ENABLED", R["campaign"]["status"] == "ENABLED")
check("timezone America/Chicago", R["timezone"] == "America/Chicago")

req = ["00_README.md", "01_current_state_reconciliation.md", "02_developer_form_and_content_handoff.md",
       "03_form_acceptance_matrix.csv", "04_gtm_delta_and_readiness.md", "05_call_measurement_plan.md",
       "06_tablet_plan_evaluation.md", "07_pii_incident_note.md", "08_action_register.csv", "08_validation_and_register.md"]
miss = [f for f in req if not (PKG / f).exists()]
check("bundle completeness", not miss, miss)

fm = list(csv.DictReader((PKG / "03_form_acceptance_matrix.csv").open(encoding="utf-8")))
check("form matrix has F01-F12", [r["case_id"] for r in fm] == [f"F{i:02d}" for i in range(1, 13)])
check("form matrix statuses in {VERIFIED, FAILED, NOT TESTED}", all(r["current_status"] in ("VERIFIED", "FAILED", "NOT TESTED") for r in fm))
check("form matrix rows complete", all(all(r[k] for k in r) for r in fm))
check("F01 is not claimed as tested end to end", "not by submission" in fm[0]["current_evidence"])

H = (PKG / "02_developer_form_and_content_handoff.md").read_text(encoding="utf-8")
for s in ("apg_permanent_lights_lead", "offer.apogeelawns.com", "/thank-you/permanent-christmas-lights/", "18453077620",
          "KOL7CImirvocEPS8jt9E", "402-526-5754", "lead_id"):
    check(f"handoff carries '{s}'", s in H)
for note in ("Reconfirm the current EverLights relationship and commercial availability before publication.",
             "Exact consultation steps and estimate timing require client confirmation.",
             "Exact installation timing and handoff process require client confirmation."):
    check(f"handoff quotes live note: {note[:40]}...", note in H)
check("handoff never assigns 402-202-7261 or 402-783-8482 as the page number", "402-202-7261" not in H and "402-783-8482" not in H)

G = yaml.safe_load((CL / "plans" / "APG-0928-GTM-LID.yaml").read_text(encoding="utf-8"))
check("GTM-LID not fingerprinted", G["fingerprint"] == "NONE" and G["publication_gate"]["fingerprint_now"] == "NONE")
guard_yaml = G["change_fully_specified_now"][0]["after"].split("matches RegEx (ignore case)")[1].strip()
t = (ROOT / "tests" / "test_apg_lead_id_guard.py").read_text(encoding="utf-8")
m = re.search(r'GUARD = \(r"(.+?)"\n\s+r"(.+?)"\)', t, re.S)
guard_test = (m.group(1) + m.group(2)).replace('\\"', '"') if m else None
check("GTM-LID guard == tested guard", guard_yaml == guard_test, f"{guard_yaml!r} vs {guard_test!r}")
V = json.loads((EV / "2026-09-28b-gtm-published-v2-v3.json").read_text(encoding="utf-8"))["v3"]
tag_ids = sorted(t_.get("tag_id") for t_ in V["tags"])
check("GTM inventory tag IDs match published v3 (6,7,9,10)", tag_ids == [6, 7, 9, 10], tag_ids)
aw = next(t_ for t_ in V["tags"] if t_["function"] == "__awct")
check("published form tag ID/label match the plan", aw["vtp_conversionId"] == "18453077620" and aw["vtp_conversionLabel"] == "KOL7CImirvocEPS8jt9E")

T2 = yaml.safe_load((CL / "plans" / "APG-0928-DEV-T2.yaml").read_text(encoding="utf-8"))
live = {d["resource"]: d for d in R["device_modifiers"]}
check("DEV-T2 closed as REJECTED (owner-confirmed exclusion) without fingerprint",
      T2["status"] == "REJECTED" and T2["status_reason"] == "OWNER_CONFIRMED_DELIBERATE_EXCLUSION" and T2["fingerprint"] == "NONE")
check("DEV-T2 history keeps the evaluated 3-update payload",
      T2["mutation_counts_evaluated"]["updates"] == 3 and len(T2["objects_if_owner_answers_restore"]) == 3)
check("DEV-T2 'from' values match live explicit 0.0",
      all(live[o["resource_name"]]["bid_modifier_set"] and live[o["resource_name"]]["bid_modifier"] == 0.0 for o in T2["objects_if_owner_answers_restore"]))
check("DEV-T marked VOID in place", (CL / "plans" / "APG-0928-DEV-T.yaml").read_text(encoding="utf-8").startswith("# ####") and
      "VOID" in (CL / "plans" / "APG-0928-DEV-T.yaml").read_text(encoding="utf-8")[:400])

AR = list(csv.DictReader((PKG / "08_action_register.csv").open(encoding="utf-8")))
check("action register rows complete", all(all(r[k] for k in r) for r in AR), f"{len(AR)} rows")
check("no action register row claims approval",
      not any(re.search(r"\bAPPROVED\b", r["readiness_2026_09_28_run_d"]) for r in AR))

# ---------------- run D (owner answers) ----------------
D = json.loads((EV / "2026-09-28d-reads.json").read_text(encoding="utf-8"))
check("run D fresh identity PASS", D["identity_pass"])
check("run D campaign still ENABLED, $8 cap, $16.44",
      D["campaign"]["status"] == "ENABLED" and D["campaign"]["cap"] == 8.0 and D["campaign"]["budget"] == 16.44)
check("tablets still excluded (3 rows explicit 0.0)",
      len(D["tablet"]) == 3 and all(x["set"] and x["value"] == 0.0 for x in D["tablet"]))
for req2 in ("09_owner_decisions_and_reporting.md", "10_website_claim_matrix.csv", "11_labor_only_negatives.md"):
    check(f"run D file present: {req2}", (PKG / req2).exists())
O = (PKG / "09_owner_decisions_and_reporting.md").read_text(encoding="utf-8")
for quote in ("Landing pages are not tablet optimized so I excluded them.",
              "A qualified lead is someone who asks for the service on the form or on the call."):
    check(f"owner statement recorded verbatim: {quote[:35]}...", quote in O)
cy = (CL / "client.yaml").read_text(encoding="utf-8")
check("client.yaml records tablet decision + qualified definition",
      "EXCLUDE_TABLETS" in cy and "asks for permanent Christmas light installation" in cy)
qline = [ln for ln in cy.splitlines() if ln.strip().startswith("qualified:")][0]
check("qualified definition adds no duration/appointment/budget rule",
      not re.search(r"60|second|appointment|budget|estimate|booked", qline, re.I), qline)
NL = yaml.safe_load((CL / "plans" / "APG-0928-NEG-LO.yaml").read_text(encoding="utf-8"))
from gm_gsa.safety import approval_code  # noqa: E402
fp_nl = approval_code({k: v for k, v in NL.items() if k != "approval_grant"})
check("NEG-LO fingerprint recomputes to 58362D536336", fp_nl == "58362D536336", fp_nl)
live_n = {n["res"]: n for n in D["all_negatives"]}
check("NEG-LO objects exist live with exact text/match/ENABLED",
      all(live_n.get(o["resource_name"], {}).get("text") == o["keyword"]["text"]
          and live_n[o["resource_name"]]["mt"] == o["keyword"]["match_type"]
          and live_n[o["resource_name"]]["status"] == "ENABLED" for o in NL["objects"]))
check("NEG-LO removes exactly 2 and keeps 'customer supplied'",
      NL["mutation_counts"]["removes"] == 2 and len(NL["objects"]) == 2
      and NL["kept_unchanged"][0]["keyword"]["text"] == "customer supplied")
check("NEG-LO touches nothing else", all(v == 0 for k, v in NL["mutation_counts"].items() if k != "removes"))
PR = json.loads((EV / "2026-09-28d-negative-probes.json").read_text(encoding="utf-8"))
check("probes: DIY/job/trade variants stay blocked after removal",
      all(p_["blocked_after"] for p_ in PR if p_["kind"] in ("diy", "job", "trade")))
check("probes: buyer variants unblocked after removal", all(not p_["blocked_after"] for p_ in PR if p_["kind"] == "buyer"))
WM = list(csv.DictReader((PKG / "10_website_claim_matrix.csv").open(encoding="utf-8")))
check("website matrix rows complete with retrieval time",
      all(r["claim"] and r["evidence_type"] and r["retrieved_utc"] for r in WM), f"{len(WM)} rows")
check("website matrix keeps customer-supplied as an owner answer",
      any(r["claim"] == "Customer-supplied lights" and "OWNER ANSWER" in r["evidence_type"] for r in WM))
H2 = (PKG / "02_developer_form_and_content_handoff.md").read_text(encoding="utf-8")
check("handoff no longer promises test conversions stay clean",
      "stay\n    clean" not in H2 and "stays clean" not in H2 and "not guaranteed" in H2)
C5 = (PKG / "05_call_measurement_plan.md").read_text(encoding="utf-8")
check("call plan carries the corrected capture wording",
      "Successful routing, recording, and attribution remain untested" in C5)
check("register: tablet action CLOSED", next(r for r in AR if r["id"] == "A15")["readiness_2026_09_28_run_d"].startswith("CLOSED"))
check("register has 22 rows", len(AR) == 22)

allpkg = " ".join(f.read_text(encoding="utf-8") for f in PKG.glob("*") if f.is_file())
check("no Omaha geo target or Omaha plan in the package", "1021721" not in allpkg)

ALLOWED = {"4025265754", "4022027261", "4027838482", "4022567520", "4023832673", "4027043396", "4027818399",
           "5550100111", "5550100222", "5550100333",
           "8164626278"}  # the Google Ads child customer ID written 816-462-6278 - an account ID, not a phone number
phone_re = re.compile(r"(?:\+1(\d{3})(\d{3})(\d{4})(?!\d))|(?:(?<!\d)\(?(\d{3})\)?[-. ](\d{3})[-. ](\d{4})(?!\d))")
email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
scan = [f for f in PKG.glob("*") if f.is_file()] + [f for f in EV.glob("2026-09-28c-*")] + \
       [f for f in EV.glob("2026-09-28d-*")] + \
       [CL / "plans" / "APG-0928-GTM-LID.yaml", CL / "plans" / "APG-0928-DEV-T2.yaml", CL / "plans" / "APG-0928-NEG-LO.yaml",
        CL / "work-orders" / "work-order-measurement-repair-handoff-2026-09-28.yaml", CL / "client.yaml"]
bad_p, bad_e, where = 0, 0, {}
for f in scan:
    s = f.read_text(encoding="utf-8", errors="ignore")
    for mm in phone_re.finditer(s):
        n = "".join(g for g in mm.groups() if g)
        if n not in ALLOWED:
            bad_p += 1
            where[f.name] = where.get(f.name, 0) + 1
    bad_e += len([x for x in email_re.findall(s) if not x.endswith("example.com") and x != "access@greenmarketingfl.com"])
check("privacy: only allowlisted business/synthetic numbers", bad_p == 0, f"{bad_p} in {where}")
check("privacy: no emails beyond documented/example", bad_e == 0, bad_e)

r = subprocess.run([sys.executable, "-m", "pytest", "-q"] + [str(ROOT / "tests" / x) for x in (
    "test_wc_sanitize.py", "test_apg_lead_id_guard.py", "test_apg_lead_id_contract.py", "test_apg_negmatch.py")],
    capture_output=True, text=True)
check("unit tests pass", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-200:])

fails = [x for x in res if not x[1]]
for n, ok, d in res:
    print(("PASS  " if ok else "FAIL  ") + n + (f"  [{d}]" if d and not ok else ""))
print(f"\n{len(res) - len(fails)} passed, {len(fails)} failed")
sys.exit(1 if fails else 0)
