#!/usr/bin/env python3
"""Ambient | 2026-09-23 | WhatConverts audit: profile, numbers, leads, upload delivery.

READ-ONLY against WhatConverts. EXTERNAL WRITES: 0.

Never prints a credential. Customer PII (names, emails, caller numbers) is reduced to
counts and masked forms before anything is written or printed - only the TRACKING numbers,
which are business infrastructure, are shown in full.
"""
from __future__ import annotations
import os, sys, json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from requests.auth import HTTPBasicAuth
from gm_gsa.config import load_dotenv_if_available
from ambient_0909_lib import TZ, SNAP  # noqa

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
if not TOKEN or not SECRET:
    sys.exit("WhatConverts credentials missing or empty.")
AUTH = HTTPBasicAuth(TOKEN, SECRET)
BASE = "https://app.whatconverts.com/api/v1"
STAMP = "2026-09-23"

EXPECTED_ACCOUNT = "115814"   # Ambient Cooling & Heating
EXPECTED_PROFILE = "105803"
WATCH = {"4102164650": "GLE Traffic / location-ad number (per screenshot)",
         "4107056354": "previously used Google Ads call asset",
         "4104159517": "GSA's Heat Traffic (per screenshot)",
         "4107610932": "approved main-site business number",
         "4109141456": "previously observed DNI number"}


def digits(s):
    return "".join(ch for ch in str(s or "") if ch.isdigit())[-10:]


def mask(s):
    d = digits(s)
    return f"***-***-{d[-4:]}" if len(d) >= 4 else "***"


def get(path, **params):
    try:
        r = requests.get(f"{BASE}/{path}", auth=AUTH, params=params, timeout=45)
        ct = r.headers.get("content-type", "")
        return r.status_code, (r.json() if ct.startswith("application/json")
                               else r.text[:400])
    except Exception as exc:
        return None, f"{type(exc).__name__}: {str(exc)[:200]}"


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0, "pii_redacted": True}

    print("=== 1. ACCOUNTS / PROFILES ===")
    code, body = get("accounts")
    print(f"  accounts HTTP {code}")
    accts = body.get("accounts", []) if isinstance(body, dict) else []
    amb = [a for a in accts if str(a.get("account_id")) == EXPECTED_ACCOUNT]
    print(f"    {len(accts)} accounts on this AGENCY-WIDE credential; "
          f"only Ambient is read")
    for a in amb:
        print(f"    account_id={a.get('account_id')}  {a.get('account_name')}")
    out["ambient_account"] = amb
    out["credential_is_agency_wide"] = True
    out["other_client_accounts_not_read"] = len(accts) - len(amb)

    code, body = get("profiles", account_id=EXPECTED_ACCOUNT)
    print(f"  profiles HTTP {code} (scoped to account {EXPECTED_ACCOUNT})")
    profs = body.get("profiles", []) if isinstance(body, dict) else []
    target = None
    for p in profs:
        pid = str(p.get("profile_id"))
        mark = ""
        if pid == EXPECTED_PROFILE:
            target = p
            mark = "   <<< MATCHES the recorded profile id"
        print(f"    profile_id={pid:10s} {str(p.get('profile_name'))[:44]}{mark}")
    out["profiles"] = profs
    out["expected_profile_found"] = bool(target)
    print(f"  profile {EXPECTED_PROFILE} verified: {bool(target)}")
    if not target and profs:
        cand = [p for p in profs if "ambient" in str(p.get("profile_name", "")).lower()]
        out["ambient_profiles_by_name"] = cand
        print(f"  profiles matching 'ambient' by name: "
              f"{[p.get('profile_id') for p in cand]}")

    pid = EXPECTED_PROFILE
    assert target, "Ambient profile 105803 not found under account 115814"

    print("\n=== 2. TRACKING NUMBERS ON THE PROFILE ===")
    code, body = get("tracking-numbers", account_id=EXPECTED_ACCOUNT, profile_id=pid, per_page=250)
    print(f"  HTTP {code}")
    nums = body.get("tracking_numbers", []) if isinstance(body, dict) else []
    if not nums:
        print(f"  body: {str(body)[:300]}")
    rows = []
    for n in nums:
        tn = digits(n.get("tracking_number") or n.get("number"))
        dest = digits(n.get("destination_number") or n.get("forwarding_number"))
        rows.append({
            "tracking_number": tn, "destination": dest,
            "name": n.get("number_name") or n.get("name"),
            "type": n.get("number_type") or n.get("type"),
            "source": n.get("source"), "medium": n.get("medium"),
            "campaign": n.get("campaign"),
            "status": n.get("status"), "pool": n.get("is_pool") or n.get("pool"),
            "raw_keys": sorted(n.keys())[:18]})
    out["tracking_numbers"] = rows
    print(f"  {len(rows)} tracking numbers")
    print(f"  {'tracking':12s} {'destination':12s} {'type':14s} {'source':14s} "
          f"{'medium':12s} name")
    for r in sorted(rows, key=lambda x: x["tracking_number"]):
        flag = "  <<< " + WATCH[r["tracking_number"]] if r["tracking_number"] in WATCH else ""
        print(f"  {r['tracking_number']:12s} {r['destination']:12s} "
              f"{str(r['type'])[:14]:14s} {str(r['source'])[:14]:14s} "
              f"{str(r['medium'])[:12]:12s} {str(r['name'])[:26]}{flag}")
    found = {r["tracking_number"] for r in rows}
    for w, why in WATCH.items():
        if w not in found:
            print(f"  NOT a WhatConverts tracking number: {w}  ({why})")
    out["watch_numbers_present"] = {w: (w in found) for w in WATCH}

    print("\n=== 3. SEPTEMBER LEADS (counts and attribution only, no PII) ===")
    leads, page = [], 1
    while page <= 12:
        code, body = get("leads", account_id=EXPECTED_ACCOUNT, profile_id=pid,
                         start_date="2026-09-01", end_date="2026-09-23",
                         page_number=page, leads_per_page=250)
        if code != 200 or not isinstance(body, dict):
            print(f"  leads page {page} HTTP {code} {str(body)[:200]}")
            break
        batch = body.get("leads", [])
        leads += batch
        if len(batch) < 250:
            break
        page += 1
    print(f"  {len(leads)} leads in September")
    by_type, by_src, by_num, gclid_n, quotable = {}, {}, {}, 0, 0
    detail = []
    for l in leads:
        lt = str(l.get("lead_type"))
        by_type[lt] = by_type.get(lt, 0) + 1
        src = f"{l.get('lead_source')}/{l.get('lead_medium')}"
        by_src[src] = by_src.get(src, 0) + 1
        tn = digits(l.get("tracking_number"))
        if tn:
            by_num[tn] = by_num.get(tn, 0) + 1
        g = l.get("gclid") or l.get("click_id")
        if g:
            gclid_n += 1
        if l.get("quotable") in (True, "Yes", "yes"):
            quotable += 1
        detail.append({"lead_id": l.get("lead_id"), "type": lt,
                       "source": l.get("lead_source"), "medium": l.get("lead_medium"),
                       "campaign": l.get("lead_campaign"),
                       "tracking_number": tn,
                       "has_click_id": bool(g),
                       "click_id_prefix": (str(g)[:12] + "...") if g else None,
                       "duration_sec": l.get("call_duration_seconds")
                       or l.get("call_duration"),
                       "quotable": l.get("quotable"),
                       "date": l.get("date_created"),
                       "contact_masked": mask(l.get("phone_number"))})
    out["september_leads_total"] = len(leads)
    out["by_lead_type"] = by_type
    out["by_source_medium"] = by_src
    out["by_tracking_number"] = by_num
    out["with_click_id"] = gclid_n
    out["quotable_count"] = quotable
    out["lead_detail_redacted"] = detail
    print(f"  by lead_type      : {by_type}")
    print(f"  by source/medium  : {by_src}")
    print(f"  by tracking number: {by_num}")
    print(f"  leads carrying a click id: {gclid_n} / {len(leads)}")
    print(f"  marked quotable          : {quotable}")

    print("\n=== 4. TODAY'S TEST SUBMISSIONS (2026-09-22/23) ===")
    code, body = get("leads", account_id=EXPECTED_ACCOUNT, profile_id=pid,
                     start_date="2026-09-22", end_date="2026-09-23",
                     leads_per_page=250)
    recent = body.get("leads", []) if isinstance(body, dict) else []
    print(f"  HTTP {code}  {len(recent)} leads on 22-23 Sept")
    tests = []
    for l in recent:
        blob = json.dumps(l).lower()
        if "do not dispatch" in blob or "test" in str(l.get("lead_analysis", "")).lower():
            tests.append({"lead_id": l.get("lead_id"), "type": l.get("lead_type"),
                          "source": l.get("lead_source"), "medium": l.get("lead_medium"),
                          "date": l.get("date_created"),
                          "has_click_id": bool(l.get("gclid") or l.get("click_id")),
                          "quotable": l.get("quotable"),
                          "page": str(l.get("landing_url"))[:90]})
    out["test_leads_found"] = tests
    print(f"  leads containing the TEST label: {len(tests)}")
    for t in tests:
        print(f"    lead {t['lead_id']} {t['type']} src={t['source']}/{t['medium']} "
              f"clickid={t['has_click_id']} quotable={t['quotable']} {t['page']}")
    if recent and not tests:
        print("  sample of available fields on a recent lead (keys only, no values):")
        print(f"    {sorted(recent[0].keys())}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"wc-audit-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0 | CREDENTIALS NEVER PRINTED | CUSTOMER PII REDACTED")


if __name__ == "__main__":
    main()
