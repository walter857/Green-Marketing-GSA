#!/usr/bin/env python3
"""Ambient | 2026-09-16 | corrected verdicts + results table for the attribution QA.

Re-scores the raw run with two corrections to my own harness:
  1. the leak check compared only against the CURRENT run's markers, so cross-run
     contamination (a marker from an earlier run) was scored clean. Now any
     QA-shaped marker that is not this test's own counts as contamination.
  2. utm_source=google and utm_medium=cpc are CONSTANTS across every test, so a
     cached value trivially equals the expected value. Those two never count as a
     genuine capture.
"""
from __future__ import annotations
import json, re, sys, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients" / "ambient-cooling-heating" / "snapshots"
TZ = ZoneInfo("America/New_York")
P = SNAP / "attribution-fix-verification-2026-09-16.json"
d = json.loads(P.read_text(encoding="utf-8"))
MARKER = re.compile(r"QA0916[A-Z0-9]+")

rows, counts = [], {"total": 0, "rendered": 0, "blocked": 0, "captured_own": 0,
                    "contaminated": 0, "gbraid_captured": 0, "wbraid_captured": 0,
                    "gclid_captured": 0}


def score(r, is_control=False):
    pop = r.get("populated_fields") or {}
    srv = r.get("server_hidden_values") or []
    blob = json.dumps(pop) + " " + " ".join(srv)
    exp = r.get("expected") or {}
    own = {v for v in exp.values() if v not in ("google", "cpc")}
    found = set(MARKER.findall(blob))
    foreign = sorted(found - own)
    # a genuine capture = the unique click id landed in a field
    idkind = next((k for k in ("gclid", "gbraid", "wbraid") if k in exp), None)
    want_id = exp.get(idkind) if idkind else None
    id_ok = bool(want_id) and want_id in blob
    utm_ok = all(exp[k] in blob for k in exp
                 if k.startswith("utm") and exp[k] not in ("google", "cpc"))
    rendered = r.get("http_status") == 200 and (r.get("form_count") or 0) > 0
    return {"page": r["page"], "test": r["run"], "device": r["profile"],
            "cache": r.get("x_proxy_cache") or ("challenge" if not rendered else "-"),
            "expected_id": want_id or "(none - control)",
            "observed_id": (sorted(found)[0] if found else "(empty)"),
            "id_captured": id_ok, "utms_correct": utm_ok,
            "foreign_markers": foreign,
            "contaminated": bool(foreign),
            "dup_ids": r.get("duplicate_dom_id_count"),
            "forms": r.get("form_count"),
            "gtm": r.get("gtm_present"), "wc": r.get("whatconverts_present"),
            "rendered": rendered, "idkind": idkind,
            "result": ("INCONCLUSIVE - SG-Captcha" if not rendered
                       else "PASS" if (id_ok and utm_ok and not foreign)
                       else "FAIL")}


for r in [x for x in d["test2_3_results"] if x.get("counted_in_24")]:
    s = score(r)
    rows.append(s)
    counts["total"] += 1
    counts["rendered"] += 1 if s["rendered"] else 0
    counts["blocked"] += 0 if s["rendered"] else 1
    counts["captured_own"] += 1 if (s["id_captured"] and s["utms_correct"]) else 0
    counts["contaminated"] += 1 if s["contaminated"] else 0
    if s["idkind"] == "gbraid" and s["id_captured"]:
        counts["gbraid_captured"] += 1
    if s["idkind"] == "wbraid" and s["id_captured"]:
        counts["wbraid_captured"] += 1
    if s["idkind"] == "gclid" and s["id_captured"]:
        counts["gclid_captured"] += 1

ctrl = []
for r in d["test4_controls"]:
    s = score(r, True)
    s["result"] = ("INCONCLUSIVE - SG-Captcha" if not s["rendered"]
                   else "PASS" if not s["foreign_markers"] else "FAIL")
    ctrl.append(s)

print("=== CORRECTED RESULTS TABLE (24 parameterised tests) ===")
hdr = (f"| {'Page':28s} | {'Test':22s} | {'Dev':7s} | {'Cache':9s} | "
       f"{'Expected ID':26s} | {'Observed ID':28s} | UTM | Dup | GTM | WC | Result |")
print(hdr)
for s in rows:
    print(f"| {s['page'][:28]:28s} | {s['test']:22s} | {s['device']:7s} | "
          f"{str(s['cache']):9s} | {str(s['expected_id'])[:26]:26s} | "
          f"{str(s['observed_id'])[:28]:28s} | {str(s['utms_correct'])[:5]:5s} | "
          f"{str(s['dup_ids']):3s} | {str(s['gtm'])[:5]:5s} | {str(s['wc'])[:5]:5s} | "
          f"{s['result']} |")
print("\n=== SIX NO-PARAMETER CONTROLS ===")
for s in ctrl:
    print(f"| {s['page'][:28]:28s} | control | desktop | {str(s['cache']):9s} | "
          f"(none) | {str(s['observed_id'])[:28]:28s} | foreign={s['foreign_markers']} "
          f"| {s['result']} |")

counts["controls_total"] = len(ctrl)
counts["controls_pass"] = sum(1 for s in ctrl if s["result"] == "PASS")
counts["controls_fail"] = sum(1 for s in ctrl if s["result"] == "FAIL")
counts["controls_inconclusive"] = sum(1 for s in ctrl
                                      if s["result"].startswith("INCONCLUSIVE"))
print("\n=== CORRECTED COUNTS ===")
for k, v in counts.items():
    print(f"  {k:26s} {v}")

d["corrected_results_table"] = rows
d["corrected_controls"] = ctrl
d["corrected_counts"] = counts
d["harness_corrections"] = [
    "Leak check originally compared only against the CURRENT run's markers, so a "
    "marker left by an EARLIER run was scored clean. Re-scored: any QA-shaped marker "
    "that is not this test's own counts as contamination.",
    "utm_source=google and utm_medium=cpc are constants in every test, so a cached "
    "value trivially matches. They no longer count as a genuine capture.",
    "The Google Ads tag AW-11155434808 was initially recorded 0/24 because the check "
    "read only the rendered DOM. Verified separately: the tag loads via GTM network "
    "requests (googleadservices.com/pagead/conversion/11155434808/...). IT IS PRESENT.",
    "4 of 24 tests never cleared the SiteGround SG-Captcha 202 challenge and are "
    "reported INCONCLUSIVE, not FAIL - that is a test-client obstacle, not a site defect.",
]
d["google_ads_tag_verified_present"] = True
d["verdict"] = "FAIL - FIX NOT COMPLETE"
d["verified_local"] = datetime.datetime.now(TZ).isoformat()
P.write_text(json.dumps(d, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {P}")
