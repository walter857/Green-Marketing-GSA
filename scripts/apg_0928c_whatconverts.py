#!/usr/bin/env python3
"""2026-09-28 (run C) READ-ONLY WhatConverts configuration + minimal sanitized lead read for Apogee.

GET only. Account 119788 / profile 174313. Every lead passes gm_gsa.wc_sanitize.sanitize_lead before any
count or print; no raw response is printed or saved. Configuration endpoints return business numbers
only, and only allowlisted fields are printed.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.wc_sanitize import field_names, sanitize_lead  # noqa: E402
from gm_gsa.whatconverts import BASE, _auth, fetch_leads  # noqa: E402

load_dotenv_if_available(ROOT / ".env")
ACC, PROF = "119788", "174313"
BUSINESS = ["4025265754", "4022027261", "4027838482", "4022567520", "4023832673"]
EV = ROOT / "reports" / "apogee-lawns" / "evidence"
out = {}

NUM_FIELDS = ("phone_number_id", "phone_name", "tracking_number", "destination_number", "swap_number",
              "call_flow", "trigger", "source", "medium", "last_used", "call_recording", "voice", "messaging",
              "pending_activation", "profile_id")
r = requests.get(f"{BASE}/tracking/numbers", auth=_auth(), timeout=60,
                 params={"account_id": ACC, "profile_id": PROF, "numbers_per_page": 250})
print("tracking/numbers HTTP", r.status_code)
nums = []
if r.ok:
    for n in r.json().get("numbers", r.json().get("phone_numbers", [])):
        if str(n.get("profile_id")) != PROF:
            continue
        nums.append({k: n.get(k) for k in NUM_FIELDS})
for n in nums:
    print("  NUMBER", json.dumps(n))
out["tracking_numbers"] = nums

FORM_FIELDS = ("form_id", "form_name", "attribute_type", "attribute_type_value", "submit_attribute_type",
               "submit_attribute_type_value", "profile_id")
r = requests.get(f"{BASE}/tracking/forms", auth=_auth(), timeout=60,
                 params={"account_id": ACC, "profile_id": PROF, "forms_per_page": 250})
print("tracking/forms HTTP", r.status_code)
forms = []
if r.ok:
    for f in r.json().get("forms", []):
        if str(f.get("profile_id")) != PROF:
            continue
        forms.append({k: f.get(k) for k in FORM_FIELDS})
for f in forms:
    print("  FORM", json.dumps(f))
out["tracking_forms"] = forms

prof = requests.get(f"{BASE}/accounts/{ACC}/profiles", auth=_auth(), timeout=60)
pk = [p for p in prof.json().get("profiles", []) if str(p.get("profile_id")) == PROF]
out["profile_field_names"] = sorted(pk[0].keys()) if pk else []
print("profile object field names:", out["profile_field_names"])

# Minimal lead read: default view, since the campaign went live, sanitized before anything else.
leads = fetch_leads(ACC, PROF, "2026-09-21", "2026-09-28", include_qa=True)["leads"]
names = Counter()
safe_name = re.compile(r"^[A-Za-z0-9 _\-\.\[\]]{1,60}$")
for lead in leads:
    for nme in field_names(lead):
        if safe_name.match(nme) and "@" not in nme and not re.search(r"\d{7,}", nme):
            names[nme] += 1
clean = [sanitize_lead(lead, BUSINESS) for lead in leads]
del leads
out["lead_count_2026_09_21_to_28"] = len(clean)
out["lead_field_names"] = sorted(names)
out["click_id_like_field_names"] = sorted(n for n in names if re.search(r"gclid|gbraid|wbraid|msclkid|click", n, re.I))
out["utm_like_field_names"] = sorted(n for n in names if re.search(r"utm|source|medium|campaign|keyword|landing", n, re.I))
out["by_type_tracking_source"] = Counter(f"{c['lead_type']}|{c['tracking_number']}|{c['lead_source']}" for c in clean)
out["web_forms"] = [c for c in clean if c["lead_type"] == "Web Form"]
out["leads_on_paid_number"] = sum(1 for c in clean if c["tracking_number"] == "4025265754")
print("leads 09-21..09-28 (default view):", len(clean))
print("click-id-like field names in schema:", out["click_id_like_field_names"])
print("utm/source-like field names in schema:", out["utm_like_field_names"])
print("by type|tracking|source:", dict(out["by_type_tracking_source"]))
print("leads on 402-526-5754:", out["leads_on_paid_number"])
for w in out["web_forms"]:
    print("  WEB FORM", json.dumps(w))
out["by_type_tracking_source"] = dict(out["by_type_tracking_source"])
(EV / "2026-09-28c-whatconverts-config-sanitized.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("saved sanitized output only")
