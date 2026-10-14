#!/usr/bin/env python3
"""2026-10-05 READ-ONLY funnel checks for Apogee Lawns (8164626278).

1. WhatConverts leads 2026-09-21..2026-10-05 for account 119788 / profile 174313, in the default,
   duplicate=true and spam=true sets (the default set hides both). Every lead passes
   gm_gsa.wc_sanitize.sanitize_lead; only aggregate counts are printed or saved.
2. One GET each: the paid landing page, the planned thank-you path, and the published GTM
   container script. No form is submitted, no number dialled, no ad clicked, no cache-buster.
"""
from __future__ import annotations

import re
import sys
import time
from collections import Counter
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.wc_sanitize import assert_no_pii, sanitize_lead  # noqa: E402
from gm_gsa.whatconverts import fetch_leads  # noqa: E402
from apg_lib import EVID, write  # noqa: E402

load_dotenv_if_available(ROOT / ".env")
ACC, PROF = "119788", "174313"
BUSINESS = ["4025265754", "4022027261", "4027838482", "4022567520", "4023832673"]
CLIENT_YAML = ROOT / "clients" / "apogee-lawns" / "client.yaml"
LP = "https://offer.apogeelawns.com/permanent-christmas-lights-lincoln-ne/"
TY = "https://offer.apogeelawns.com/thank-you/permanent-christmas-lights/"
GTM = "https://www.googletagmanager.com/gtm.js?id=GTM-M545Z8T2"
out = {"window": ["2026-09-21", "2026-10-05"], "whatconverts": {}, "web": {}}

# ---------------------------------------------------------------- WhatConverts (aggregates only)
for label, filters in (("default", {}), ("duplicates", {"duplicate": "true"}), ("spam", {"spam": "true"})):
    try:
        res = fetch_leads(ACC, PROF, "2026-09-21", "2026-10-05", client_yaml=CLIENT_YAML, **filters)
    except Exception as exc:  # noqa: BLE001
        out["whatconverts"][label] = {"error": str(exc)[:200]}
        print(f"WC {label}: ERROR {str(exc)[:160]}")
        continue
    rows = [sanitize_lead(lead, BUSINESS) for lead in res["leads"]]
    agg = Counter((r.get("lead_type"), r.get("lead_source"), r.get("lead_medium"), r.get("landing"),
                   r.get("tracking_number"), r.get("quotable"), bool(r["click_ids_present"].get("gclid")),
                   bool(r["utms_present"].get("utm_campaign"))) for r in rows)
    out["whatconverts"][label] = {"kept": len(rows), "qa_excluded": len(res["qa_excluded"]),
                                  "raw": res["raw_count"],
                                  "by_type_source_medium_landing_number_quotable_gclid_utm":
                                      [list(k) + [v] for k, v in agg.most_common()]}
    print(f"WC {label}: raw={res['raw_count']} kept={len(rows)} qa_excluded={len(res['qa_excluded'])}")
    for k, v in agg.most_common():
        print(f"   {v:>3}  type={k[0]} src={k[1]} med={k[2]} landing={k[3]} num={k[4]} quotable={k[5]} gclid={k[6]} utm={k[7]}")
    time.sleep(2)

# ---------------------------------------------------------------- web (one GET each)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/129.0 Safari/537.36"}
NOTES = ["Reconfirm", "require client confirmation", "approved surrounding"]
for label, url in (("landing_page", LP), ("thank_you", TY)):
    try:
        r = requests.get(url, headers=UA, timeout=30, allow_redirects=True)
        html = r.text
        h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
        out["web"][label] = {
            "status": r.status_code, "final_url": r.url, "redirects": [h.status_code for h in r.history],
            "bytes": len(html), "title": (re.search(r"<title>(.*?)</title>", html, re.S | re.I) or [None, None])[1],
            "h1": [re.sub(r"<[^>]+>|\s+", " ", x).strip() for x in h1][:3],
            "sg_captcha_stub": "sgcaptcha" in html.lower() or "sg-captcha" in html.lower(),
            "gtm_container": html.count("GTM-M545Z8T2"), "whatconverts_script": "ksrndkehqnwntyxlhgto" in html,
            "ppc_number_occurrences": html.count("526-5754") + html.count("5265754"),
            "gform_ids": sorted(set(re.findall(r"gform_(\d+)", html))),
            "datalayer_event_occurrences": html.count("apg_permanent_lights_lead"),
            "noindex": bool(re.search(r"<meta[^>]+robots[^>]+noindex", html, re.I)),
            "drafting_notes_found": [n for n in NOTES if n.lower() in html.lower()],
        }
    except Exception as exc:  # noqa: BLE001
        out["web"][label] = {"error": str(exc)[:200]}
    print(f"WEB {label}: {out['web'][label]}")
    time.sleep(3)
try:
    r = requests.get(GTM, timeout=30)
    js = r.text
    out["web"]["gtm_published"] = {
        "status": r.status_code, "bytes": len(js),
        "version": (re.search(r'"version":"(\d+)"', js) or [None, None])[1],
        "form_label": "KOL7CImirvocEPS8jt9E" in js, "website_call_label": "lp3jCKf5vPocEPS8jt9E" in js,
        "thank_you_path_regex": "thank-you" in js, "custom_event_name": "apg_permanent_lights_lead" in js,
        "conversion_linker": "__gclidw" in js, "aw_id": "AW-18453077620" in js,
    }
except Exception as exc:  # noqa: BLE001
    out["web"]["gtm_published"] = {"error": str(exc)[:200]}
print(f"WEB gtm_published: {out['web']['gtm_published']}")

rendered = repr(out)
assert_no_pii(rendered, [])
write(EVID / "2026-10-05-funnel-checks.json", out)
