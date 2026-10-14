#!/usr/bin/env python3
"""Ambient | AUGUST 2026 ONLY: spend, paid leads, qualified leads, service mix, CPQL.

READ-ONLY. Transcripts/messages are read in memory to classify the service and then
discarded. No names, telephone numbers, email addresses, IPs, recordings or message
bodies are printed or written.
"""
from __future__ import annotations
import base64, json, os, re, sys, datetime, urllib.request
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import CID, IN5, NAME, SNAP, TZ, client, q, identity_gate  # noqa
from gm_gsa.config import load_dotenv_if_available  # noqa

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()
STAMP = "2026-09-15"
AUG_LO, AUG_HI = "2026-08-01", "2026-08-31"
LAUNCH = "2026-08-14"
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "window": f"{AUG_LO}..{AUG_HI}", "read_only": True}


def call(p):
    r = urllib.request.Request(f"https://app.whatconverts.com/api/v1/{p}",
                               headers={"Authorization": f"Basic {auth}",
                                        "Accept": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as z:
        return json.loads(z.read().decode("utf-8", "replace"))


rows, page = [], 1
while page <= 12:
    d = call(f"leads?profile_id=105803&start_date={AUG_LO}&end_date={AUG_HI}"
             f"&leads_per_page=250&page_number={page}")
    rows += d.get("leads", [])
    if page >= d.get("total_pages", 1) or not d.get("leads"):
        break
    page += 1
print(f"WhatConverts leads in AUGUST 2026: {len(rows)}")

SERVICE_PATTERNS = [
    ("AC Repair", r"\bac repair|air ?condition\w* repair|\bac (is )?not (cooling|working)"
                  r"|\bac (unit )?(broke|broken|down|out)|no cold air|ac service call"
                  r"|\bfix (my |the )?ac\b|cooling (issue|problem)"),
    ("HVAC Replacement", r"\breplace\w*\b.{0,24}(unit|system|hvac|furnace|ac|air ?condition|heat pump)"
                         r"|new (system|unit|hvac)|\bsystem replacement|upgrade (the |my )?system"),
    ("HVAC Installation", r"\binstall\w*\b|\bnew install|install(ation)? quote|ductwork install"),
    ("Gas Boiler Repair", r"\bboiler\b"),
    ("Heating / Furnace Repair", r"\bfurnace\b|\bheat(ing)? (repair|issue|problem|not working)"
                                 r"|no heat\b|heater (repair|broke|not)"),
    ("Maintenance / Tune-up", r"\bmaintenance\b|\btune ?up\b|\bservice (plan|agreement|contract)"
                              r"|seasonal check|clean(ing)? and check|annual (service|check)"),
    ("Thermostat", r"\bthermostat\b"),
    ("Duct / Airflow", r"\bduct\w*\b|\bairflow\b|\bvent(ilation|s)?\b"),
    ("Mini Split / Heat Pump", r"mini.?split|\bheat pump\b|\bductless\b"),
    ("Water Heater", r"water heater|\bhot water\b"),
    ("Commercial", r"\bcommercial\b|\brooftop\b|\brtu\b|\bbusiness (property|building)"),
    ("Estimate / Quote only", r"\bestimate\b|\bquote\b|\bpricing\b|how much"),
]
NON_SERVICE = [
    ("Existing customer / admin", r"already (a |an )?(customer|client)|existing customer"
                                  r"|\binvoice\b|\bbilling\b|reschedul|confirm (my |the )?appointment"
                                  r"|follow.?up on"),
    ("Vendor / solicitation", r"\bsolicit|sales call|marketing (call|company)|seo\b|\bvendor\b"),
    ("Job seeker", r"\bhiring\b|\bjob\b|\bapply\b|\bresume\b|\bemployment\b"),
    ("Wrong number / other co.", r"wrong number|looking for (another|a different)"),
]
LANDING_SERVICE = {"/ac-repair/": "AC Repair", "/hvac-repair/": "HVAC Repair",
                   "/hvac-installation/": "HVAC Installation",
                   "/hvac-replacement/": "HVAC Replacement",
                   "/gas-boiler-repair/": "Gas Boiler Repair",
                   "/commercial-hvac-installation/": "Commercial HVAC Installation"}


def classify(r):
    la = r.get("lead_analysis") or {}
    blobs = [str(la.get(k)) for k in ("Topic Detection", "Intent Detection",
                                      "Keyword Detection", "Lead Summary", "Call Type",
                                      "Customer Type") if la.get(k)]
    for k, v in (r.get("additional_fields") or {}).items():
        if "project" in str(k).lower() or "message" in str(k).lower():
            blobs.append(str(v))
    if r.get("message"):
        blobs.append(str(r["message"]))
    if r.get("call_transcription"):
        blobs.append(str(r["call_transcription"]))
    text = " \n ".join(blobs).lower()
    for label, pat in NON_SERVICE:
        if re.search(pat, text, re.I):
            return label, True
    for label, pat in SERVICE_PATTERNS:
        if re.search(pat, text, re.I):
            return label, False
    lu = str(r.get("landing_url") or "")
    for path, label in LANDING_SERVICE.items():
        if path in lu:
            return label, False
    return ("Unclassified" if text.strip() else "No service signal"), False


def is_paid(r):
    s = str(r.get("lead_source") or "").lower()
    m = str(r.get("lead_medium") or "").lower()
    return "lsa" not in s and s in ("google", "google ads", "adwords") \
        and m in ("cpc", "ppc", "paid")


print("\n=== 1. AUGUST SPEND ===")
c = client(); identity_gate(c, verbose=False)
five_aug = sum(r.metrics.cost_micros for r in q(c, f"""
    SELECT campaign.id, metrics.cost_micros FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '{AUG_LO}' AND '{AUG_HI}'""")) / 1e6
per_camp = defaultdict(float)
for r in q(c, f"""SELECT campaign.id, metrics.cost_micros, metrics.clicks,
                         metrics.impressions, metrics.conversions FROM campaign
                  WHERE campaign.id IN ({IN5})
                    AND segments.date BETWEEN '{AUG_LO}' AND '{AUG_HI}'"""):
    per_camp[str(r.campaign.id)] += r.metrics.cost_micros / 1e6
all_aug = defaultdict(float)
for r in q(c, f"""SELECT campaign.id, campaign.name, metrics.cost_micros FROM campaign
                  WHERE segments.date BETWEEN '{AUG_LO}' AND '{AUG_HI}'"""):
    all_aug[(str(r.campaign.id), r.campaign.name)] += r.metrics.cost_micros / 1e6
print(f"  FIVE BOFU campaigns : ${five_aug:,.2f}")
for cid, v in sorted(per_camp.items(), key=lambda x: -x[1]):
    print(f"      {NAME[cid]:20s} ${v:>9,.2f}")
other = {k: v for k, v in all_aug.items() if k[0] not in per_camp and v > 0}
print(f"  OTHER paid campaigns: ${sum(other.values()):,.2f}")
for (cid, nm), v in sorted(other.items(), key=lambda x: -x[1]):
    print(f"      {cid} ${v:>9,.2f}  {nm[:48]}")
print(f"  WHOLE ACCOUNT       : ${sum(all_aug.values()):,.2f}")
out["august_spend"] = {"five_campaigns": round(five_aug, 2),
                       "per_campaign": {NAME[k]: round(v, 2) for k, v in per_camp.items()},
                       "other_paid_campaigns": round(sum(other.values()), 2),
                       "whole_account": round(sum(all_aug.values()), 2)}

print("\n=== 2. AUGUST LEADS ===")
paid = [r for r in rows if is_paid(r)]
paid_pre = [r for r in paid if str(r.get("date_created"))[:10] < LAUNCH]
paid_post = [r for r in paid if str(r.get("date_created"))[:10] >= LAUNCH]
yes = [r for r in paid if str(r.get("quotable")) == "Yes"]
print(f"  all leads (every channel) : {len(rows)}")
ch = Counter()
for r in rows:
    s = str(r.get("lead_source") or "").lower()
    ch["LSA" if "lsa" in s else "GBP" if "gbp" in s else
       "paid search" if is_paid(r) else "other"] += 1
print(f"  channel mix              : {dict(ch)}")
print(f"  paid-search leads        : {len(paid)}  "
      f"(before {LAUNCH}: {len(paid_pre)}, on/after: {len(paid_post)})")
print(f"  qualified (quotable=Yes) : {len(yes)}")
print(f"  quotable breakdown       : "
      f"{dict(Counter(str(r.get('quotable')) for r in paid))}")
out["august_leads"] = {"all_channels": len(rows), "channel_mix": dict(ch),
                       "paid_search": len(paid), "paid_before_launch": len(paid_pre),
                       "paid_after_launch": len(paid_post), "qualified": len(yes)}

print("\n=== 3. AUGUST QUALIFIED PAID LEADS - SERVICE + ATTRIBUTION ===")
mix, non = Counter(), Counter()
att = Counter()
print(f"  {'date':11s} {'type':11s} {'gclid':6s} {'num':6s} {'service':26s} landing")
for r in sorted(yes, key=lambda x: str(x.get("date_created"))):
    label, isnon = classify(r)
    (non if isnon else mix)[label] += 1
    lu = str(r.get("landing_url") or "")
    m = re.match(r"https?://([^/]+)(/[^?#]*)", lu)
    path = (m.group(1) + m.group(2)) if m else "(none)"
    bucket = ("five_LP" if "offer.ambientcoolingandheating.com" in path
              else "no_url" if path == "(none)" else "other_page")
    att[bucket] += 1
    print(f"  {str(r.get('date_created'))[:10]:11s} {str(r.get('lead_type')):11s} "
          f"{'yes' if str(r.get('gclid') or '').strip() else '-':6s} "
          f"{re.sub(r'[^0-9]', '', str(r.get('tracking_number') or ''))[-4:] or '-':6s} "
          f"{label[:26]:26s} {path}")
print(f"\n  SERVICE MIX (new business): {dict(mix)}")
if non:
    print(f"  NON-SERVICE              : {dict(non)}")
print(f"  attribution buckets      : {dict(att)}")
out["august_qualified_service_mix"] = dict(mix)
out["august_qualified_non_service"] = dict(non)
out["august_attribution"] = dict(att)

print("\n=== 4. AUGUST CPL / CPQL ===")
new_biz = sum(mix.values())
rowsout = []
for label, spend, leads, qual in (
        ("five campaigns / all 8 qualified", five_aug, len(paid), len(yes)),
        ("five campaigns / new-business only", five_aug, len(paid), new_biz),
        ("whole-account paid spend / all qualified", sum(all_aug.values()), len(paid), len(yes)),
        ("five campaigns / provable five-LP only", five_aug, len(paid), att.get("five_LP", 0))):
    cpl = spend / leads if leads else None
    cpql = spend / qual if qual else None
    rowsout.append({"basis": label, "spend": round(spend, 2), "leads": leads,
                    "qualified": qual,
                    "cpl": round(cpl, 2) if cpl else None,
                    "cpql": round(cpql, 2) if cpql else None})
    print(f"  {label:42s} spend ${spend:>9,.2f}  qual {qual:>2}  "
          f"CPL ${cpl:>8,.2f}  CPQL ${cpql:>9,.2f}" if cpql else
          f"  {label:42s} spend ${spend:>9,.2f}  qual {qual:>2}")
out["august_cpql"] = rowsout

print("\n=== 5. AUGUST vs SEPTEMBER ===")
sep = sum(r.metrics.cost_micros for r in q(c, f"""
    SELECT campaign.id, metrics.cost_micros FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-09-01' AND '2026-09-14'""")) / 1e6
print(f"  August  1-31 : ${five_aug:>9,.2f} spend | {len(paid):>2} paid leads | "
      f"{len(yes):>2} qualified")
print(f"  Sept 1-14    : ${sep:>9,.2f} spend |  2 paid leads |  2 qualified")
print(f"  August was {five_aug/18:.0f}/day over 18 served days; Sept 1-14 "
      f"${sep/14:.2f}/day")
out["august_vs_september"] = {"august_spend": round(five_aug, 2),
                              "september_1_14_spend": round(sep, 2)}

p = SNAP / f"august-cpql-and-service-mix-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
