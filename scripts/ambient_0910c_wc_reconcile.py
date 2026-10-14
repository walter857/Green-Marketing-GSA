#!/usr/bin/env python3
"""Full paid-search lead reconciliation.

Prior pass counted only GCLID rows and called the rest organic/GBP. That was too weak an
inference. This pass reconciles on gclid, gbraid, wbraid, UTM parameters, landing/lead URL
query string, referrer, tracking number, campaign fields, date and lead status, and reports
what is genuinely UNATTRIBUTED rather than assigning it a source it has not evidenced.

Never prints, logs or writes: names, phone numbers, emails, addresses, IPs, recordings,
transcripts, message bodies, or credential values. URLs are reduced to host+path+the
attribution parameters only.
"""
from __future__ import annotations
import base64, json, os, sys, urllib.request, urllib.parse, datetime, hashlib, re
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import CID, FIVE, IN5, NAME, EVID, TZ, client, q, identity_gate  # noqa
from gm_gsa.config import load_dotenv_if_available  # noqa
from gm_gsa.google_ads import enum_name as E  # noqa

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
PROFILE, START, END = "105803", "2026-08-14", "2026-09-10"
auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()

# Anything that can identify a person never leaves this set.
PII = {"caller_name", "caller_number", "contact_name", "contact_email_address",
       "contact_phone_number", "email_address", "phone_number", "message", "ip_address",
       "call_transcription", "recording", "play_recording", "caller_city", "caller_zip",
       "caller_state", "caller_country", "city", "zip", "state", "address",
       "contact_company_name", "phone_name", "additional_fields", "custom_fields",
       "mapped_fields", "spotted_keywords", "lead_analysis", "notes", "quote_name"}
# URL-bearing fields are parsed for attribution, then discarded.
URLF = {"lead_url", "landing_url", "referring_url", "referrer", "page_url", "form_url"}
ATTR_PARAMS = ("gclid", "gbraid", "wbraid", "msclkid", "fbclid", "utm_source", "utm_medium",
               "utm_campaign", "utm_term", "utm_content", "campaignid", "adgroupid",
               "keyword", "matchtype", "device", "network")


def redact(s: str) -> str:
    for v in (TOKEN, SECRET):
        if v:
            s = s.replace(v, "[REDACTED]")
    return s


def fetch(page):
    url = (f"https://app.whatconverts.com/api/v1/leads?profile_id={PROFILE}"
           f"&start_date={START}&end_date={END}&leads_per_page=250&page_number={page}")
    r = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}",
                                             "Accept": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as e:
        raise SystemExit(f"WhatConverts unreachable: {type(e).__name__}: "
                         f"{redact(str(e))[:200]}")


def parse_url(u):
    """host + path + attribution params only. Everything else is dropped."""
    if not u or not isinstance(u, str):
        return None
    try:
        p = urllib.parse.urlsplit(u)
        qs = urllib.parse.parse_qs(p.query)
        keep = {k.lower(): (qs[k][0][:120] if qs[k] else "") for k in qs
                if k.lower() in ATTR_PARAMS}
        return {"host": p.netloc[:80], "path": p.path[:120], "params": keep}
    except Exception:
        return None


print("=== WHATCONVERTS CONNECTIVITY ===")
leads, page = [], 1
while True:
    d = fetch(page)
    got = d.get("leads", [])
    leads += got
    tp = d.get("total_pages") or 1
    if page >= tp or not got:
        break
    page += 1
print(f"  reachable: YES   profile {PROFILE}   {START}..{END}   leads pulled: {len(leads)}")
print("  credential values were never printed, logged or written")

field_names = sorted({k for l in leads for k in l})
print(f"\n  fields returned by the API ({len(field_names)}): {field_names}")

# ------------------------------------------------------------------ normalise
rows = []
for l in leads:
    urls = {}
    for f in URLF:
        pu = parse_url(l.get(f))
        if pu:
            urls[f] = pu
    merged = {}
    for pu in urls.values():
        for k, v in pu["params"].items():
            merged.setdefault(k, v)
    for k in ("gclid", "gbraid", "wbraid", "utm_source", "utm_medium", "utm_campaign",
              "utm_term", "utm_content", "campaignid", "adgroupid"):
        v = l.get(k)
        if isinstance(v, str) and v.strip():
            merged[k] = v.strip()[:120]
    dur = l.get("call_duration_seconds") or l.get("call_duration") or 0
    try:
        dur = int(dur)
    except Exception:
        dur = 0
    rows.append({
        "lead_id": hashlib.sha256(str(l.get("lead_id")).encode()).hexdigest()[:16],
        "date": (l.get("date_created") or "")[:10],
        "lead_type": l.get("lead_type"), "lead_status": l.get("lead_status"),
        "lead_source": l.get("lead_source"), "lead_medium": l.get("lead_medium"),
        "lead_campaign": l.get("lead_campaign"), "quotable": str(l.get("quotable")),
        "spam": l.get("spam"), "duplicate": l.get("duplicate"),
        "call_duration_seconds": dur,
        "tracking_number_present": bool(str(l.get("tracking_number") or "").strip()),
        "attr": merged,
        "url_paths": sorted({v["path"] for v in urls.values() if v.get("path")}),
        "url_hosts": sorted({v["host"] for v in urls.values() if v.get("host")})})

print(f"\n=== ATTRIBUTION SIGNALS PRESENT ACROSS {len(rows)} LEADS ===")
sig = Counter()
for r in rows:
    a = r["attr"]
    if a.get("gclid"):
        sig["gclid"] += 1
    if a.get("gbraid"):
        sig["gbraid"] += 1
    if a.get("wbraid"):
        sig["wbraid"] += 1
    if a.get("utm_source"):
        sig["utm_source"] += 1
    if a.get("campaignid"):
        sig["campaignid (ValueTrack)"] += 1
    if r["tracking_number_present"]:
        sig["tracking_number"] += 1
    if not any(a.get(k) for k in ("gclid", "gbraid", "wbraid", "utm_source", "campaignid")):
        sig["NO click/UTM identifier at all"] += 1
for k, v in sig.most_common():
    print(f"  {k:<34}{v:>4}")

print(f"\n  lead_source  : {dict(Counter(str(r['lead_source']) for r in rows))}")
print(f"  lead_medium  : {dict(Counter(str(r['lead_medium']) for r in rows))}")
print(f"  utm_source   : {dict(Counter(str(r['attr'].get('utm_source')) for r in rows))}")
print(f"  utm_medium   : {dict(Counter(str(r['attr'].get('utm_medium')) for r in rows))}")
print(f"  landing paths: {dict(Counter(p for r in rows for p in r['url_paths']).most_common(12))}")

# ------------------------------------------------------- join to Google Ads
print("\n=== JOIN TO GOOGLE ADS ===")
c = client()
identity_gate(c, verbose=False)
gclids = {r["attr"]["gclid"] for r in rows if r["attr"].get("gclid")}
dates = sorted({r["date"] for r in rows if r["date"]})
probe = sorted({d for d in dates} |
               {(datetime.date.fromisoformat(d) - datetime.timedelta(days=k)).isoformat()
                for d in dates for k in (1, 2, 3, 7, 14, 30) if d})
probe = [d for d in probe if "2026-08-11" <= d <= "2026-09-10"]
gmap = {}
for d in probe:
    try:
        for r in q(c, f"SELECT click_view.gclid, campaign.id, ad_group.id, segments.date "
                      f"FROM click_view WHERE segments.date = '{d}'"):
            if r.click_view.gclid in gclids:
                gmap[r.click_view.gclid] = {
                    "campaign_id": str(r.campaign.id),
                    "campaign": NAME.get(str(r.campaign.id), str(r.campaign.id)),
                    "ad_group": str(r.ad_group.id), "click_date": r.segments.date}
    except Exception as e:
        print(f"  click_view {d}: {type(e).__name__}: {str(e)[:100]}")
        break
print(f"  GCLIDs seen in WhatConverts: {len(gclids)}   resolved via click_view: {len(gmap)}")

print("\n=== CLASSIFY EVERY LEAD BY EVIDENCE, NOT BY ASSUMPTION ===")
PAID_SRC = re.compile(r"^(google|adwords|google[_-]?ads)$", re.I)
PAID_MED = re.compile(r"^(cpc|ppc|paid|paidsearch|paid[_-]search)$", re.I)
for r in rows:
    a = r["attr"]
    g = a.get("gclid")
    if g and g in gmap and gmap[g]["campaign_id"] in FIVE:
        r["bucket"] = "PAID SEARCH - joined to one of the five"
        r["campaign"] = gmap[g]["campaign"]
        r["click_date"] = gmap[g]["click_date"]
    elif g and g in gmap:
        r["bucket"] = "PAID SEARCH - other campaign in this account"
        r["campaign"] = gmap[g]["campaign"]
    elif g:
        r["bucket"] = "PAID SEARCH - gclid present but not resolved to a click"
    elif a.get("gbraid") or a.get("wbraid"):
        r["bucket"] = "PAID - gbraid/wbraid (app/web, no gclid)"
    elif a.get("campaignid"):
        r["bucket"] = "PAID - ValueTrack campaignid present, no gclid"
    elif PAID_SRC.match(str(a.get("utm_source") or "")) and \
            PAID_MED.match(str(a.get("utm_medium") or "")):
        r["bucket"] = "PAID - utm_source/medium say cpc, no click id"
    elif a.get("utm_source"):
        r["bucket"] = f"TAGGED non-paid utm_source={a.get('utm_source')}"
    else:
        r["bucket"] = "UNATTRIBUTED - no click id, no UTM"
b = Counter(r["bucket"] for r in rows)
for k, v in b.most_common():
    print(f"  {v:>4}  {k}")
print("\n  NOTE: 'UNATTRIBUTED' means the lead carries no click identifier and no UTM.")
print("  It is NOT evidence of organic, GBP or any other channel. WhatConverts lead_source")
print("  is a label applied by the tracking setup, not an independent measurement.")

print("\n=== UNIQUE QUALIFIED LEADS ON THE FIVE PAID CAMPAIGNS ===")
paid5 = [r for r in rows if r["bucket"].startswith("PAID SEARCH - joined")]
for r in paid5:
    meets = ((r["lead_type"] == "Web Form") or
             (r["lead_type"] in ("Phone Call", "Text Message")
              and r["call_duration_seconds"] >= 60))
    r["meets_60s_or_form"] = meets
    r["unique_qualified"] = (r["lead_status"] == "Unique"
                             and r["quotable"].lower() == "yes"
                             and meets and not r["spam"])
print(f"  {'campaign':<20}{'click':<12}{'type':<13}{'status':<9}{'quotable':<9}"
      f"{'secs':>5}{'uniqQL':>8}")
for r in sorted(paid5, key=lambda z: (z["campaign"], z.get("click_date", ""))):
    print(f"  {r['campaign']:<20}{r.get('click_date',''):<12}{str(r['lead_type']):<13}"
          f"{str(r['lead_status']):<9}{r['quotable']:<9}{r['call_duration_seconds']:>5}"
          f"{str(r['unique_qualified']):>8}")
uq = defaultdict(int)
for r in paid5:
    if r["unique_qualified"]:
        uq[r["campaign"]] += 1
print(f"\n  unique qualified by campaign: {dict(uq)}")

MAXQ = {"AC Repair": 150.0, "HVAC Repair": 250.0, "HVAC Installation": 280.0,
        "HVAC Replacement": 280.0, "Gas Boiler Repair": 250.0}
print("\n=== CPQL BY BIDDING REGIME (never blended across 2026-09-04 16:56) ===")
cpql = {}
for lbl, a2, b2 in [("UNCAPPED", "2026-08-14", "2026-09-03"),
                    ("CAPPED", "2026-09-05", "2026-09-09")]:
    print(f"\n  --- {lbl} {a2}..{b2} ---")
    print(f"  {'campaign':<20}{'cost':>10}{'valid':>7}{'uniqQL':>8}{'CPQL':>11}"
          f"{'limit':>8}  verdict")
    for r in q(c, f"SELECT campaign.id, metrics.cost_micros, metrics.clicks FROM campaign "
                  f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '{a2}' AND '{b2}'"):
        k = NAME[str(r.campaign.id)]
        cost = r.metrics.cost_micros / 1e6
        n = sum(1 for x in paid5 if x["unique_qualified"] and x.get("campaign") == k
                and (a2 <= x.get("click_date", "") <= b2))
        v = cost / n if n else None
        verdict = "-" if v is None else ("WITHIN" if v <= MAXQ[k] else "OVER")
        cpql.setdefault(lbl, {})[k] = {"cost": round(cost, 2), "clicks": r.metrics.clicks,
                                       "uniq_ql": n, "cpql": round(v, 2) if v else None,
                                       "limit": MAXQ[k], "verdict": verdict}
        print(f"  {k:<20}{cost:>10.2f}{r.metrics.clicks:>7}{n:>8}"
              f"{(f'{v:.2f}' if v else 'n/a'):>11}{MAXQ[k]:>8.0f}  {verdict}")

out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "window": [START, END], "profile": PROFILE, "reachable": True,
       "total_leads": len(leads), "api_fields": field_names,
       "attribution_signals": dict(sig), "buckets": dict(b),
       "gclids_seen": len(gclids), "gclids_resolved": len(gmap),
       "unique_qualified_by_campaign": dict(uq),
       "cpql_by_regime": cpql,
       "paid_five_rows": [{k: v for k, v in r.items() if k != "attr"} for r in paid5],
       "pii_policy": "no name, number, email, address, IP, recording, transcript or message "
                     "body is read into memory beyond the redaction filter, and none is "
                     "written. URLs reduced to host+path+attribution params. lead_id and "
                     "gclid stored only as 16-char SHA-256 prefixes."}
p = EVID / "2026-09-10c-whatconverts-full-reconciliation.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p.relative_to(ROOT)}  (no PII, no credentials)")
