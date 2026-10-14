#!/usr/bin/env python3
"""Ambient | 2026-09-15 | qualified paid-search leads: which SERVICE, and revenue basis.

READ-ONLY. No PII is retained or printed: no names, telephone numbers, email addresses,
IP addresses, recordings, transcripts or message bodies. Transcripts and messages are
read in memory ONLY to classify the service, then discarded. Only counts and service
labels are written out.
"""
from __future__ import annotations
import base64, json, os, re, sys, datetime, urllib.request
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import CID, IN5, SNAP, TZ, client, q, identity_gate  # noqa
from gm_gsa.config import load_dotenv_if_available  # noqa

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()
PROFILE, STAMP = "105803", "2026-09-15"
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "read_only": True,
       "pii_policy": "transcripts/messages read in memory for classification only, "
                     "never retained; no names, numbers, emails, IPs or recordings stored"}


def call(p):
    r = urllib.request.Request(f"https://app.whatconverts.com/api/v1/{p}",
                               headers={"Authorization": f"Basic {auth}",
                                        "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as z:
        return json.loads(z.read().decode("utf-8", "replace"))


rows, page = [], 1
while page <= 12:
    d = call(f"leads?profile_id={PROFILE}&start_date=2026-06-17&end_date=2026-09-15"
             f"&leads_per_page=250&page_number={page}")
    rows += d.get("leads", [])
    if page >= d.get("total_pages", 1) or not d.get("leads"):
        break
    page += 1
print(f"leads 2026-06-17..2026-09-15: {len(rows)}")

# ---------------------------------------------------------------- service classifier
SERVICE_PATTERNS = [
    ("AC Repair",            r"\bac repair|air ?condition\w* repair|\bac (is )?not (cooling|working)"
                             r"|\bac (unit )?(broke|broken|down|out)|no cold air|ac service call"
                             r"|\bfix (my |the )?ac\b|cooling (issue|problem)"),
    ("HVAC Replacement",     r"\breplace\w*\b.{0,24}(unit|system|hvac|furnace|ac|air ?condition|heat pump)"
                             r"|new (system|unit|hvac)|\bsystem replacement|upgrade (the |my )?system"),
    ("HVAC Installation",    r"\binstall\w*\b|\bnew install|install(ation)? quote|ductwork install"),
    ("Gas Boiler Repair",    r"\bboiler\b"),
    ("Heating / Furnace Repair", r"\bfurnace\b|\bheat(ing)? (repair|issue|problem|not working)"
                                 r"|no heat\b|heater (repair|broke|not)"),
    ("Maintenance / Tune-up", r"\bmaintenance\b|\btune ?up\b|\bservice (plan|agreement|contract)"
                              r"|seasonal check|clean(ing)? and check|annual (service|check)"),
    ("Thermostat",           r"\bthermostat\b"),
    ("Duct / Airflow",       r"\bduct\w*\b|\bairflow\b|\bvent(ilation|s)?\b"),
    ("Mini Split / Heat Pump", r"mini.?split|\bheat pump\b|\bductless\b"),
    ("Water Heater",         r"water heater|\bhot water\b"),
    ("Commercial",           r"\bcommercial\b|\brooftop\b|\brtu\b|\bbusiness (property|building)"),
    ("Estimate / Quote only", r"\bestimate\b|\bquote\b|\bpricing\b|how much"),
]
NON_SERVICE = [
    ("Existing customer / admin", r"already (a |an )?(customer|client)|existing customer"
                                  r"|\binvoice\b|\bbilling\b|reschedul|confirm (my |the )?appointment"
                                  r"|follow.?up on"),
    ("Vendor / solicitation",     r"\bsolicit|sales call|marketing (call|company)|seo\b|\bvendor\b"),
    ("Job seeker",                r"\bhiring\b|\bjob\b|\bapply\b|\bresume\b|\bemployment\b"),
    ("Wrong number / other co.",  r"wrong number|looking for (another|a different)"),
]
LANDING_SERVICE = {
    "/ac-repair/": "AC Repair", "/hvac-repair/": "HVAC Repair",
    "/hvac-installation/": "HVAC Installation",
    "/hvac-replacement/": "HVAC Replacement",
    "/gas-boiler-repair/": "Gas Boiler Repair",
    "/commercial-hvac-installation/": "Commercial HVAC Installation",
}


def classify(r):
    """Return (service_label, evidence_source). PII text is used here and discarded."""
    la = r.get("lead_analysis") or {}
    blobs = []
    for k in ("Topic Detection", "Intent Detection", "Keyword Detection", "Lead Summary",
              "Call Type", "Customer Type"):
        v = la.get(k)
        if v:
            blobs.append(str(v))
    af = r.get("additional_fields") or {}
    for k, v in af.items():
        if "project" in str(k).lower() or "message" in str(k).lower():
            blobs.append(str(v))
    if r.get("message"):
        blobs.append(str(r["message"]))
    if r.get("call_transcription"):
        blobs.append(str(r["call_transcription"]))
    text = " \n ".join(blobs).lower()

    for label, pat in NON_SERVICE:
        if re.search(pat, text, re.I):
            return label, "analysis/transcript", True
    for label, pat in SERVICE_PATTERNS:
        if re.search(pat, text, re.I):
            return label, "analysis/transcript", False
    lu = str(r.get("landing_url") or "")
    for path, label in LANDING_SERVICE.items():
        if path in lu:
            return label, "landing_url", False
    if text.strip():
        return "Unclassified (text present, no service match)", "analysis/transcript", False
    return "No service signal captured", "none", False


def is_paid_search(r):
    s = str(r.get("lead_source") or "").lower()
    m = str(r.get("lead_medium") or "").lower()
    if "lsa" in s:
        return False
    return s in ("google", "google ads", "adwords") and m in ("cpc", "ppc", "paid")


print("\n=== 1. lead_analysis COVERAGE ===")
la_present = sum(1 for r in rows if (r.get("lead_analysis") or {}))
print(f"  leads with lead_analysis: {la_present}/{len(rows)}")
vals = defaultdict(Counter)
for r in rows:
    for k, v in (r.get("lead_analysis") or {}).items():
        if v and len(str(v)) < 60:
            vals[k][str(v)] += 1
for k in ("Call Type", "Customer Type", "Sentiment Detection", "Sales Agent"):
    if vals[k]:
        print(f"  {k}: {dict(vals[k].most_common(8))}")
out["lead_analysis_coverage"] = la_present
out["lead_analysis_enums"] = {k: dict(v.most_common(10)) for k, v in vals.items()}

print("\n=== 2. QUALIFIED PAID-SEARCH LEADS - SERVICE MIX ===")
paid = [r for r in rows if is_paid_search(r)]
paid_yes = [r for r in paid if str(r.get("quotable")) == "Yes"]
print(f"  paid-search leads: {len(paid)}   of which quotable=Yes: {len(paid_yes)}")
mix, nonsvc = Counter(), Counter()
detail = []
for r in paid_yes:
    label, src, non = classify(r)
    (nonsvc if non else mix)[label] += 1
    detail.append({"lead_id": r.get("lead_id"), "service": label, "evidence": src,
                   "lead_type": r.get("lead_type"),
                   "date": str(r.get("date_created"))[:10],
                   "has_gclid": bool(str(r.get("gclid") or "").strip()),
                   "tracking_last4": re.sub(r"\D", "", str(r.get("tracking_number") or ""))[-4:]
                   or None})
print("\n  SERVICE REQUESTED (qualified paid-search leads):")
for k, v in mix.most_common():
    print(f"    {v:>3}  {k}")
if nonsvc:
    print("  NON-SERVICE among them:")
    for k, v in nonsvc.most_common():
        print(f"    {v:>3}  {k}")
out["paid_qualified_service_mix"] = dict(mix)
out["paid_qualified_non_service"] = dict(nonsvc)
out["paid_qualified_detail"] = detail

print("\n=== 3. ALL QUALIFIED LEADS (every channel) - SERVICE MIX ===")
all_yes = [r for r in rows if str(r.get("quotable")) == "Yes"]
mix2, non2 = Counter(), Counter()
for r in all_yes:
    label, src, non = classify(r)
    (non2 if non else mix2)[label] += 1
print(f"  qualified leads, all channels: {len(all_yes)}")
for k, v in mix2.most_common():
    print(f"    {v:>3}  {k}")
if non2:
    print("  NON-SERVICE:")
    for k, v in non2.most_common():
        print(f"    {v:>3}  {k}")
out["all_qualified_service_mix"] = dict(mix2)
out["all_qualified_non_service"] = dict(non2)

print("\n=== 4. REVENUE FIELDS - what WhatConverts actually holds ===")
rev = {"quote_value_non_empty": sum(1 for r in rows if r.get("quote_value")),
       "sales_value_non_empty": sum(1 for r in rows if r.get("sales_value")),
       "lead_score_non_empty": sum(1 for r in rows if r.get("lead_score")),
       "custom_fields_non_empty": sum(1 for r in rows if (r.get("custom_fields") or {})),
       "total_leads": len(rows)}
for k, v in rev.items():
    print(f"  {k}: {v}")
print("  -> NO monetary value is recorded on ANY lead. Revenue cannot be read from "
      "WhatConverts.")
out["revenue_fields"] = rev

print("\n=== 5. SPEND + CPQL ===")
c = client(); identity_gate(c, verbose=False)
spend90 = sum(r.metrics.cost_micros for r in q(c, f"""
    SELECT campaign.id, metrics.cost_micros FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-06-17' AND '2026-09-14'""")) / 1e6
print(f"  Google Ads spend 2026-06-17..09-14 : ${spend90:,.2f}")
print(f"  paid-search leads                  : {len(paid)}")
print(f"  qualified (quotable = Yes)         : {len(paid_yes)}")
print(f"  CPL                                : ${spend90/len(paid):,.2f}" if paid else "")
print(f"  CPQL                               : ${spend90/len(paid_yes):,.2f}" if paid_yes else "")
out["spend_90d"] = round(spend90, 2)
out["cpl"] = round(spend90 / len(paid), 2) if paid else None
out["cpql"] = round(spend90 / len(paid_yes), 2) if paid_yes else None

print("\n=== 6. CPQL BY SERVICE (qualified paid leads) ===")
if paid_yes:
    per = spend90 / len(paid_yes)
    print(f"  spend is not attributable per service (only {sum(1 for r in paid_yes if str(r.get('gclid') or '').strip())}"
          f"/{len(paid_yes)} qualified paid leads carry a gclid), so this apportions")
    print(f"  the ${spend90:,.2f} evenly at ${per:,.2f} per qualified lead:")
    for k, v in mix.most_common():
        print(f"    {k:34s} {v:>2} qualified  ->  ${per*v:>9,.2f} of spend")
    out["cpql_even_apportioned"] = {k: round(per * v, 2) for k, v in mix.items()}
    out["gclid_on_qualified_paid"] = sum(1 for r in paid_yes
                                         if str(r.get("gclid") or "").strip())

p = SNAP / f"service-mix-and-revenue-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
