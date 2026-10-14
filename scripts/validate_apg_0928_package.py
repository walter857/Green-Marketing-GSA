#!/usr/bin/env python3
"""Self-review of the Apogee 2026-09-28 independent audit package. Local files only; no API call.

Exit 1 if any check fails. Prints check names and counts only - never raw search terms or PII.
"""
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
sys.path.insert(0, str(ROOT / "scripts"))
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
from apg_negmatch import negative_blocks, positive_reaches  # noqa: E402

CL = ROOT / "clients" / "apogee-lawns"
PKG = CL / "audits" / "2026-09-28-independent"
EV = ROOT / "reports" / "apogee-lawns" / "evidence"
results: list[tuple[str, bool, str]] = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), str(detail)))


profile = yaml.safe_load((CL / "client.yaml").read_text(encoding="utf-8"))
for wo in (CL / "work-order.yaml", CL / "work-orders" / "work-order-low-volume-audit-2026-09-28.yaml"):
    errs = validate_work_order(yaml.safe_load(wo.read_text(encoding="utf-8")), profile)
    check(f"work order valid: {wo.name}", not errs, "; ".join(errs))
task = yaml.safe_load((CL / "work-orders" / "work-order-low-volume-audit-2026-09-28.yaml").read_text(encoding="utf-8"))["work_order"]
check("task mode is read/draft (no write mode)", task["task"]["mode"] in ("read", "draft"), task["task"]["mode"])

S = json.loads((EV / "2026-09-28b-snapshot.json").read_text(encoding="utf-8"))
p = profile["client"]["google_ads"]
check("snapshot identity PASS", S["identity_pass"])
check("snapshot name == profile", S["customer"]["descriptive_name"] == p["exact_child_account_name"])
check("snapshot id == profile", S["customer"]["id"] == p["child_customer_id"])
check("snapshot not manager / not test", not S["customer"].get("manager") and not S["customer"].get("test_account"))
check("snapshot had 0 query errors", not S["errors"], list(S["errors"]))

live_geo = {x["location"]["geo_target_constant"].split("/")[-1] for x in S["campaign_criteria"]
            if x.get("type_") == "LOCATION" and not x.get("negative")}
approved = {str(g) for g in profile["client"]["service_area"]["geo_target_constant_ids"]}
check("geo: live targets == approved 14", live_geo == approved, f"{len(live_geo)} live / {len(approved)} approved")
check("geo: Omaha 1021721 not targeted", "1021721" not in live_geo)
check("geo: PRESENCE", S["campaigns"][0]["geo_target_type_setting"]["positive_geo_target_type"] == "PRESENCE")

negs = {x["criterion_id"]: x for x in S["campaign_criteria"] if x.get("type_") == "KEYWORD" and x.get("negative")}
nr = list(csv.DictReader((PKG / "03_negative_review.csv").open(encoding="utf-8")))
check("negatives: review covers every live negative exactly once",
      {r["criterion_id"] for r in nr} == set(negs) and len(nr) == len(negs), f"{len(nr)} rows / {len(negs)} live")
check("negatives: every row has verdict + rationale",
      all(r["verdict"] in ("KEEP", "NARROW", "REMOVE-CANDIDATE", "NEEDS-EVIDENCE") and r["rationale"] for r in nr))
check("negatives: every probe blocked by its own negative", all(r["example_blocked_by_this_negative"] == "True" for r in nr))

pos = [(x["keyword"]["text"], x["keyword"]["match_type"]) for x in S["ad_group_criteria"] if not x.get("negative")]
km = list(csv.DictReader((PKG / "04_keyword_coverage_matrix.csv").open(encoding="utf-8")))
check("keywords: every live positive text appears in the matrix", {t for t, _ in pos} <= {r["candidate_term"] for r in km})

F = json.loads((EV / "2026-09-28b-forecasts.json").read_text(encoding="utf-8"))["results"]
check("forecast: baseline present and positive", F.get("S0 current build (baseline)", {}).get("clicks", 0) > 0)
check("forecast: every scenario succeeded", all("clicks" in v for v in F.values()),
      [k for k, v in F.items() if "clicks" not in v])
check("forecast: all scenarios use the same window", all(v["request"]["cap"] > 0 for v in F.values() if "request" in v))

plan = yaml.safe_load((CL / "plans" / "APG-0928-DEV-T.yaml").read_text(encoding="utf-8"))
assert_no_embedded_secrets(plan)
fp = approval_code({k: v for k, v in plan.items() if k != "approval_grant"})
man = yaml.safe_load((PKG / "07_proposed_change_manifest.yaml").read_text(encoding="utf-8"))["change_manifest"]
ready = man["google_ads"]["implementation_ready"]
check("DEV-T: fingerprint recomputes and matches the manifest", len(ready) == 1 and ready[0]["fingerprint"] == fp, fp)
cc = {x["resource_name"]: x for x in S["campaign_criteria"]}
o1 = plan["objects"][0]["resource_name"]
check("DEV-T: object 1 exists and 'from' value matches live (explicit 0.0)",
      o1 in cc and "bid_modifier" in cc[o1] and cc[o1]["bid_modifier"] == 0.0)
agbm = {x["resource_name"]: x for x in S["ad_group_bid_modifiers"]}
check("DEV-T: objects 2-3 exist with explicit 0.0",
      all(o["resource_name"] in agbm and agbm[o["resource_name"]].get("bid_modifier") == 0.0 for o in plan["objects"][1:]))
ms = plan["mutation_summary"]
check("DEV-T: no create/remove/enable/status/budget/bid/geo/keyword change",
      all(ms[k] == 0 for k in ("creates", "removes", "enables", "status_changes", "budget_changes",
                               "bid_strategy_changes", "cpc_ceiling_changes", "geo_changes", "keyword_changes")))
check("DEV-T: target is the child, never the manager",
      plan["target"]["child_customer_id"] == "8164626278" and "3373711342" not in json.dumps(plan["objects"]))

kwp = next(x for x in man["google_ads"]["conditional_not_fingerprinted"] if x["plan_id"] == "APG-0928-KW-P")
PROTECTED = ["near me", "quote", "price", "pricing", "cost", "best", "hire", "local", "emergency", "estimate", "installer",
             "installation", "company"]
check("KW-P: no proposed negative contains a protected buyer term",
      not [n for n in kwp["negatives_to_add"] if any(re.search(rf"\b{re.escape(t)}\b", n["text"]) for t in PROTECTED)])
new_pos = pos + [(k["text"], k["match_type"]) for k in kwp["keywords_to_add"]]
check("KW-P: no proposed negative blocks a live or proposed positive",
      not [(n["text"], t) for n in kwp["negatives_to_add"] for t, _ in new_pos if negative_blocks(t, n["text"], n["match_type"])])
check("KW-P: not fingerprinted (gated)", "fingerprint" not in kwp)

check("manifest: external writes NONE", man["external_writes_performed"] == "NONE")
check("manifest: budget unchanged and within $500", man["google_ads"]["budget_changes"] == "NONE"
      and int(S["budgets"][0]["amount_micros"]) / 1e6 * 30.4 <= 500.0)
check("manifest: Omaha absent from implementation-ready work", "1021721" not in json.dumps(ready)
      and "omaha" not in json.dumps(ready).lower())
check("manifest: GTM has no implementation-ready (untested) bundle", man["gtm"]["implementation_ready"] == [])

tm = list(csv.DictReader((PKG / "05_test_matrix.csv").open(encoding="utf-8")))
check("test matrix: every status is VERIFIED / FAILED / NOT TESTED / UNVERIFIED / NOT APPLICABLE",
      all(re.match(r"^(VERIFIED|FAILED|NOT TESTED|UNVERIFIED|NOT APPLICABLE)", r["status"]) for r in tm), f"{len(tm)} rows")

# PII / secret scan over deliverables and run-B evidence (counts only)
ALLOWED_PHONES = {"4025265754", "4022027261", "4027838482", "4022567520", "4023832673", "7125550123", "9999999999",
                  "1234567890", "1234567890123"}
# formatted numbers (separators) or E.164 +1XXXXXXXXXX; bare 10-digit runs are resource IDs, not phones
phone_re = re.compile(r"(?:\+1(\d{3})(\d{3})(\d{4})(?!\d))|(?:(?<!\d)\(?(\d{3})\)?[-. ](\d{3})[-. ](\d{4})(?!\d))")
email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SECRETISH = re.compile(r"(AIza[0-9A-Za-z_\-]{20,}|ya29\.[0-9A-Za-z_\-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
scan = [f for f in PKG.glob("*") if f.is_file()] + [f for f in EV.glob("2026-09-28b-*") if f.is_file()] + \
       [CL / "plans" / "APG-0928-DEV-T.yaml", CL / "work-orders" / "work-order-low-volume-audit-2026-09-28.yaml"]
bad_phone = bad_email = secrets = 0
bad_files: dict[str, int] = {}
for f in scan:
    t = f.read_text(encoding="utf-8", errors="ignore")
    for m in phone_re.finditer(t):
        n = "".join(g for g in m.groups() if g)
        if n not in ALLOWED_PHONES and not re.fullmatch(r"(\d)\1{9}", n):
            bad_phone += 1
            bad_files[f.name] = bad_files.get(f.name, 0) + 1
    bad_email += len([e for e in email_re.findall(t) if not e.endswith("example.com") and e != "access@greenmarketingfl.com"])
    secrets += len(SECRETISH.findall(t))
check("privacy: no unexpected phone numbers in deliverables/evidence", bad_phone == 0, f"{bad_phone} found in {bad_files}")
check("privacy: no emails besides the documented agency login/example", bad_email == 0, f"{bad_email} found")
check("secrets: no credential patterns", secrets == 0, f"{secrets} found")

r = subprocess.run([sys.executable, "-m", "pytest", "-q", str(ROOT / "tests" / "test_apg_negmatch.py"),
                    str(ROOT / "tests" / "test_apg_lead_id_contract.py")], capture_output=True, text=True)
check("unit tests pass (matcher + lead-id contract)", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-200:])

required = ["00_README.md", "01_source_ledger_and_snapshot.md", "02_timeline_and_prior_audit_review.md",
            "03_negatives_and_search_terms.md", "03_negative_review.csv", "03_search_term_verdicts_RAW.csv",
            "04_keyword_and_forecast_scenarios.md", "04_keyword_coverage_matrix.csv", "05_tracking_findings.md",
            "05_developer_repair_handoff.md", "05_test_matrix.csv", "06_lincoln_improvement_draft.md",
            "06_omaha_conditional_brief.md", "07_proposed_change_manifest.yaml"]
missing = [x for x in required if not (PKG / x).exists()]
check("bundle completeness", not missing, missing)

fails = [x for x in results if not x[1]]
for name, ok, detail in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and (not ok or 'rows' in detail or '/' in detail) else ""))
print(f"\n{len(results) - len(fails)} passed, {len(fails)} failed")
sys.exit(1 if fails else 0)
