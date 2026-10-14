#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | local record corrections + manifest rebuild.

Corrects ONLY work-order and client-profile facts that were directly verified by
a fresh read-only API call or a real-browser render today, records the exact
diff, revalidates the files, and rebuilds the fingerprint manifest from the plan
files on disk. Touches no external system.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import ROOT, CLIENT_DIR, PLANS, RECEIPTS, SNAP, TZ, write  # noqa: E402

STAMP = "2026-08-27"
WO = CLIENT_DIR / "work-order.yaml"
CL = CLIENT_DIR / "client.yaml"

# Every entry is (file, exact old text, exact new text, why it is verified).
EDITS = [
    # task.mode stays 'draft'. The schema allows only read, draft, create-paused
    # or enable, and this pass produces drafts pending approval. The 2026-08-27
    # scope is recorded in task.request instead.
    (WO,
     """      remediation drafts.
      READ AND DRAFT ONLY on this pass.""",
     """      remediation drafts.
      SUPERSEDED SCOPE, 2026-08-27: full current-month account audit of the same five
      services. Fresh identity gate, full structural snapshot, August performance and
      pacing, before/after review of the 2026-08-22 budget and automotive-negative
      changes, complete search-term verdict pass, negative and shared-list conflict
      audit, real-browser landing-page and tracking QA, and three approval-gated
      adjustment plans: ACE80A09AC134C85 consolidated, EE6CFAD6667A95A1 conversion
      goals, C3038EDD9E621944 destructive negative removals.
      READ AND DRAFT ONLY on this pass.""",
     "Records the 2026-08-27 audit scope without touching task.mode, which the "
     "schema restricts to read, draft, create-paused or enable."),

    (WO,
     """    date_range: >-
      since_launch = 2026-08-14 through 2026-08-18; last_30; last_90; last_365; and all
      available history (2019-01-01 onward) for search-term research. The identity gate
      was re-verified on 2026-08-18 by a fresh read-only lookup, so all windows are readable.""",
     """    date_range: >-
      CURRENT AS AT 2026-08-27. Latest fully settled day = 2026-08-26. 2026-08-27 is
      PARTIAL and is never mixed into a settled comparison.
      august_mtd_settled = 2026-08-01..2026-08-26; today_partial = 2026-08-27;
      since_last_audit = 2026-08-22..2026-08-26;
      before_change = 2026-08-18..2026-08-21; change_day_partial = 2026-08-22;
      after_change = 2026-08-23..2026-08-26; launch_to_date = 2026-08-14..2026-08-26;
      last_30; last_90; last_365; and all available history (2019-01-01 onward).
      VERIFIED 2026-08-27: last_30, last_90, last_365 and all_history all return the
      same totals as launch_to_date plus the partial day, because the five campaigns
      have no delivery before 2026-08-14. The identity gate was re-verified on
      2026-08-27 by a fresh read-only lookup.""",
     "Windows recomputed for the 2026-08-27 run and confirmed against the API."),

    (CL,
     "    optimization_score: 0.9678744",
     "    # OBSERVED 2026-08-27 by fresh read-only lookup. Was 0.9678744 on 2026-08-17.\n"
     "    # Recorded as an observed fact only. Optimization Score is NEVER an objective.\n"
     "    optimization_score: 0.7843765",
     "Fresh customer.optimization_score read on 2026-08-27."),
]

# Verified facts appended to the work order under inputs.
APPEND_TO_WORK_ORDER = """
    # -------------------------------------------------------------------------
    # OBSERVED ACCOUNT STATE, VERIFIED 2026-08-27 BY FRESH READ-ONLY API LOOKUP.
    # Recorded as observed facts. None of this is an approval to change anything.
    # -------------------------------------------------------------------------
    verified_2026_08_27:
      live_search_campaign_ids:
        ac_repair: "24132507741"
        gas_boiler_repair: "24132507744"
        hvac_installation: "24132507747"
        hvac_repair: "24132507750"
        hvac_replacement: "24132507753"
      budget_ids_and_daily_amounts_usd:
        "15787409435": 141.45   # AC Repair
        "15787409438": 42.76    # Gas Boiler Repair
        "15787409441": 176.15   # HVAC Installation, executed 2026-08-22
        "15787409444": 78.95    # HVAC Repair
        "15787409447": 26.32    # HVAC Replacement
        sum_of_five_daily: 465.63
      bidding_strategy_all_five: TARGET_SPEND
      cpc_bid_ceiling_all_five_micros: 0
      cpc_bid_ceiling_is_uncapped: true
      networks_all_five:
        google_search: true
        search_partners: false
        display: false
      ai_max_all_five: false
      text_asset_automation_all_five: OPTED_OUT
      final_url_expansion_all_five: OPTED_OUT
      location_targets_per_campaign: 75
      excluded_locations_per_campaign: 0
      location_option: PRESENCE
      ad_schedule_rows_per_campaign: 6
      live_positive_keywords_total: 10
      live_ad_groups_total: 5
      # An additional ad group 202339087874 'SKAG | HVAC Replacement Near Me' exists
      # inside the AC Repair campaign but its status is REMOVED, so it cannot serve.
      # Its child keywords and ads still report ENABLED. Counting children without
      # excluding REMOVED parents overstates the live structure. This is a query
      # definition difference, not account drift.
      removed_ad_group_inside_ac_repair: "202339087874"
      campaign_level_negatives:
        ac_repair: ["auto", "boat", "car"]
        other_four: []
      account_level_negative_list_id: "11252984411"
      account_level_negative_list_member_count: 59
      account_level_negative_list_member_count_reported_by_api: 0
      shared_negative_lists_attached_to_the_five: 0
      clickcease_ip_exclusions_account_total: 2796
      clickcease_ip_exclusions_on_the_five: 0
      # The 2796 exclusions sit on campaign_criterion of the 18 legacy campaigns.
      # customer_negative_criterion holds none. Reading the wrong resource returns 0
      # and looks like drift.
      business_profile_location_asset_set: "8620443109"
      business_profile_location_asset_set_status: ENABLED
      manager_links_active: ["3373711342", "2815082755"]
      last_account_change_event: "2026-08-22T09:36:07 America/New_York"
      # LANDING PAGE FACTS, VERIFIED 2026-08-27 IN A REAL JS BROWSER, DESKTOP+MOBILE.
      landing_page_paid_number_displayed: "(410) 705-6354"
      landing_page_whatconverts_tel_href_observed: "+14109141456"
      landing_page_main_site_number_observed: false
      landing_page_unexplained_number_observed: false
      landing_page_gtm_container_observed: "GTM-PQTPQ436"
      landing_page_google_ads_id_observed: "AW-11155434808"
      landing_page_ga4_id_observed: "G-9X9ZHNCRWF"
      landing_page_whatconverts_script_observed: true
      landing_page_clickcease_script_observed: false
      landing_page_barred_claims_observed: 0
      landing_page_privacy_or_terms_link_observed: false
      landing_page_duplicate_dom_ids_observed: true
      gas_boiler_step_heading_observed: "Your HVAC Replacement in 3 Simple Steps"
      gas_boiler_step_heading_expected: "Your Gas Boiler Repair in 3 Simple Steps"
      gas_boiler_landing_page_gate: FAIL
      whatconverts_api_token_present: false
      lead_quality_verifiable: false
"""


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    diff = {"generated_local": datetime.datetime.now(TZ).isoformat(),
            "customer_id": "2401959466", "edits": [], "files": {}}

    for path in (WO, CL):
        diff["files"][str(path.relative_to(ROOT))] = {"sha256_before": sha(path)}

    print("== LOCAL RECORD CORRECTIONS ==")
    for path, old, new, why in EDITS:
        s = path.read_text(encoding="utf-8")
        if old not in s:
            if new.strip().splitlines()[-1] in s:
                print(f"  SKIP (already applied) {path.name}: {why}")
                diff["edits"].append({"file": str(path.relative_to(ROOT)),
                                      "status": "already applied", "why": why})
                continue
            raise SystemExit(f"HARD STOP: anchor not found in {path}:\n{old[:200]}")
        path.write_text(s.replace(old, new, 1), encoding="utf-8")
        diff["edits"].append({"file": str(path.relative_to(ROOT)),
                              "status": "applied", "why": why,
                              "before": old, "after": new})
        print(f"  APPLIED {path.name}: {why}")

    s = WO.read_text(encoding="utf-8")
    if "verified_2026_08_27:" not in s:
        anchor = "  approval_owner: Green Marketing"
        assert anchor in s, "approval_owner anchor missing"
        s = s.replace(anchor, APPEND_TO_WORK_ORDER.rstrip() + "\n" + anchor, 1)
        WO.write_text(s, encoding="utf-8")
        diff["edits"].append({"file": str(WO.relative_to(ROOT)),
                              "status": "applied",
                              "why": "Appended the observed account and landing-page "
                                     "state verified 2026-08-27.",
                              "before": "(no verified_2026_08_27 block)",
                              "after": APPEND_TO_WORK_ORDER.strip()})
        print("  APPLIED work-order.yaml: appended verified_2026_08_27 block")
    else:
        print("  SKIP work-order.yaml: verified_2026_08_27 block already present")

    for path in (WO, CL):
        diff["files"][str(path.relative_to(ROOT))]["sha256_after"] = sha(path)

    # ---------------- revalidate ----------------
    print("\n== REVALIDATION ==")
    checks = {}
    for name, cmd in {
        "validate_work_order": [sys.executable, "scripts/validate_work_order.py",
                                str(WO.relative_to(ROOT)), "--client",
                                str(CL.relative_to(ROOT))],
        "verify_setup_online": [sys.executable, "scripts/verify_setup.py", "--client",
                                str(CL.relative_to(ROOT)), "--online"],
    }.items():
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        tail = [l for l in (p.stdout or "").splitlines() if not l.startswith("Request made")]
        checks[name] = {"returncode": p.returncode, "stdout": tail[-3:],
                        "stderr": (p.stderr or "")[-300:]}
        print(f"  {name}: exit={p.returncode} {tail[-1] if tail else ''}")
    diff["revalidation"] = checks
    if any(v["returncode"] != 0 for v in checks.values()):
        raise SystemExit("HARD STOP: a validator failed after the local corrections.")

    # ---------------- rebuild the fingerprint manifest ----------------
    print("\n== FINGERPRINT MANIFEST REBUILD ==")
    prior_path = RECEIPTS / "fingerprint-manifest-2026-08-22b.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    prior_by_file = {p["file"]: p for p in prior["plans"]}

    entries = []
    for f in sorted(PLANS.glob("*.json")):
        raw = f.read_text(encoding="utf-8")
        try:
            d = json.loads(raw)
        except json.JSONDecodeError:
            entries.append({"file": f.name, "status": "UNREADABLE JSON"})
            continue
        in_file = d.get("fingerprint") or d.get("approval_code") or ""
        void = bool(d.get("void") or d.get("VOID") or
                    re.search(r'"void"\s*:\s*true', raw, re.I))
        p = prior_by_file.get(f.name)
        entries.append({
            "file": f.name,
            "fingerprint_in_file": in_file,
            "approved_fingerprint": (p or {}).get("approved_fingerprint", in_file),
            "void": void or (p or {}).get("void", False),
            "status": (p or {}).get(
                "status",
                "NEW 2026-08-27 - awaiting approval" if f.name.startswith("AMBIENT-")
                else "unclassified"),
            "file_sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            "in_prior_manifest": p is not None,
        })

    new_files = [e["file"] for e in entries if not e["in_prior_manifest"]]
    dropped = [k for k in prior_by_file if k not in {e["file"] for e in entries}]
    manifest = {
        "generated": STAMP,
        "supersedes": "receipts/fingerprint-manifest-2026-08-22b.json",
        "note": ("Rebuilt from the plan files on disk. The 2026-08-22b manifest omitted "
                 "DEVELOPER-HANDOFF-ADDENDUM-C-2026-08-22.json, so the ledger and the "
                 "directory disagreed. Never execute on a fingerprint that does not "
                 "reproduce from its file."),
        "plan_files_on_disk": len(entries),
        "added_since_prior_manifest": new_files,
        "in_prior_manifest_but_missing_on_disk": dropped,
        "do_not_execute": sorted(set(prior.get("do_not_execute", []))),
        "awaiting_approval_2026_08_27": {
            "AMBIENT-CONSOLIDATED-2026-08-27.json": "ACE80A09AC134C85",
            "AMBIENT-CONV-1-2026-08-27.json": "EE6CFAD6667A95A1",
            "AMBIENT-DEL-1-2026-08-27.json": "C3038EDD9E621944",
        },
        "still_blocked": {
            "KEYWORD-GAS-BOILER-STAGE1-EXACT-2026-08-21-v2.json": {
                "fingerprint": "3D823A10CB3C0B25",
                "status": "APPROVED BUT STILL BLOCKED",
                "reverified": "2026-08-27 in a real JS browser, desktop and mobile",
                "detail": ("offer.ambientcoolingandheating.com/gas-boiler-repair/ still "
                           "renders 'Your HVAC Replacement in 3 Simple Steps'"),
            },
            "LANDING-PAGE-PRODUCTION-DEPLOYMENT-2026-08-21.json": {
                "fingerprint": "93A9DF4AA19675E8",
                "status": "APPROVED BUT STILL BLOCKED",
                "detail": ("no website source, staging, backup or deployment authority "
                           "in this environment"),
            },
        },
        "executed_do_not_re_execute": {
            "BUDGET-STAGE1-HVAC-INSTALLATION-2026-08-21-v2.json": {
                "fingerprint": "BFB9FD367F639CA4",
                "executed": "2026-08-22 01:23 ET",
                "reverified_2026_08_27": "budget 15787409441 = 176150000 micros",
            },
            "NEGATIVES-AUTOMOTIVE-AC-REPAIR-2026-08-22.json": {
                "fingerprint": "EACEC7CBAE85FF2B",
                "executed": "2026-08-22 09:36 ET",
                "reverified_2026_08_27": ("criterion ids 10008241 car, 10000390 auto, "
                                          "10019071 boat, all ENABLED BROAD negatives "
                                          "on campaign 24132507741"),
            },
            "HVAC-REPAIR-RSA-SWAP-2026-08-21.json": {
                "fingerprint": "D441DEFC58EB5643",
                "executed": "2026-08-21 08:36 ET",
                "reverified_2026_08_27": ("ads 821714108336 and 821714108339 ENABLED "
                                          "APPROVED; 820900825560 and 820900825563 PAUSED"),
            },
        },
        "plans": sorted(entries, key=lambda z: z["file"]),
    }
    write(RECEIPTS / f"fingerprint-manifest-{STAMP}.json", manifest)
    print(f"  plan files on disk : {len(entries)}")
    print(f"  added since 08-22b : {new_files}")
    print(f"  missing on disk    : {dropped}")

    write(RECEIPTS / f"local-record-diff-{STAMP}.json", diff)
    print("\n== DIFF SUMMARY ==")
    for e in diff["edits"]:
        print(f"  {e['status']:16s} {e['file']}  -- {e['why']}")
    for f, v in diff["files"].items():
        print(f"  {f}\n     sha256 before {v['sha256_before'][:16]}  "
              f"after {v['sha256_after'][:16]}")
    return diff


if __name__ == "__main__":
    main()
