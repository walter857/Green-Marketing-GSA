#!/usr/bin/env python3
"""2026-10-05 READ-ONLY: what the published GTM container and the WhatConverts profile script do.

GTM: fetches the public gtm.js for GTM-M545Z8T2 and reports the conversion labels, trigger
regexes, event names, the transaction-id variable and the call-tracking phone. WhatConverts:
fetches the public profile script 174313.js and decodes keyword_tracking_list (swap entries).
Both are anonymous public GETs. Nothing is changed. Business numbers only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "clients" / "apogee-lawns" / "audits" / "2026-10-05-conversion-plan" / "tag-config.json"
res = {}
g = requests.get("https://www.googletagmanager.com/gtm.js?id=GTM-M545Z8T2", timeout=30).text
res["gtm"] = {
    "version": (re.search(r'"version":"(\d+)"', g) or [None, None])[1],
    "aw_ids": sorted(set(re.findall(r"AW-\d+", g))),
    "conversion_labels": sorted(set(re.findall(r'"(KOL7CImirvocEPS8jt9E|lp3jCKf5vPocEPS8jt9E)"', g))),
    "regexes_mentioning_thank_you_or_lp": sorted(set(m for m in re.findall(r'"(\^/[^"]{3,80})"', g)
                                                     if "thank" in m or "permanent" in m)),
    "custom_event_present": "apg_permanent_lights_lead" in g,
    "lead_id_dlv": "lead_id" in g,
    "dot_plus_regex": '".+"' in g or "'.+'" in g,
    "hostname_offer": "offer.apogeelawns.com" in g,
    "call_number_in_container": sorted(set(re.findall(r"402-?526-?5754|4025265754", g))),
    "conversion_linker": "__gclidw" in g,
    "bytes": len(g),
}
w = requests.get("https://s.ksrndkehqnwntyxlhgto.com/174313.js?ver=7.1", timeout=30,
                 headers={"Accept-Encoding": "gzip, deflate"})
txt = w.text
m = re.search(r"var keyword_tracking_list\s*=\s*(\[\[.*?\]\]);", txt, re.S)
entries = json.loads(m.group(1)) if m else []
res["whatconverts"] = {"http": w.status_code, "bytes": len(txt), "entries": len(entries),
                       "swap_entries": [{"id": e[0], "source": e[1], "medium": e[2], "swap_pages_idx9": e[9],
                                         "dynamic_idx10": e[10]} for e in entries],
                       "numbers_in_script": sorted(set(re.findall(r"\b402\d{7}\b|402-\d{3}-\d{4}", txt)))[:12],
                       "form_list_present": "form_list" in txt,
                       "gform_1_tracked": "gform_1" in txt}
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
