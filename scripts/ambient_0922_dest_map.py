#!/usr/bin/env python3
"""Ambient | Destination mapping under the relaxed family-page standard.

READ-ONLY. No parameters, no forms, no tel activation.

The standard now is: a shared service-family page is acceptable when its ACTUAL CONTENT
clearly covers the advertised service. A different URL wording is not, by itself, a reason
to reject it. So this pulls the full visible copy of every candidate and looks for real
coverage - a heading or a sentence that addresses the intent - rather than counting bare
word hits, which the site-wide nav inflates on every page.
"""
from __future__ import annotations
import sys, re, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-22"
CANDIDATES = {
    "heating-hub": "https://ambientcoolingandheating.com/services/heating-services/",
    "furnace-repair": "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/",
    "boiler-repair": "https://ambientcoolingandheating.com/services/heating-services/boiler-repair/",
    "heat-pumps": "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/",
    "mini-splits": "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/",
    "geothermal": "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/",
    "offer-gas-boiler": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
    "offer-hvac-installation": "https://offer.ambientcoolingandheating.com/hvac-installation/",
    "offer-hvac-replacement": "https://offer.ambientcoolingandheating.com/hvac-replacement/",
    "offer-hvac-repair": "https://offer.ambientcoolingandheating.com/hvac-repair/",
}

# Sentence-level probes. A hit means the page says something about the intent, not that a
# word appears in the nav.
INTENT_SENT = {
    "furnace_install": re.compile(r"[^.]*\bfurnace[^.]*\binstall\w*[^.]*\.", re.I),
    "furnace_replace": re.compile(r"[^.]*\bfurnace[^.]*\breplac\w*[^.]*\.", re.I),
    "furnace_maint": re.compile(r"[^.]*\bfurnace[^.]*\b(maintenance|tune)\w*[^.]*\.", re.I),
    "boiler_install": re.compile(r"[^.]*\bboiler[^.]*\binstall\w*[^.]*\.", re.I),
    "boiler_replace": re.compile(r"[^.]*\bboiler[^.]*\breplac\w*[^.]*\.", re.I),
    "boiler_maint": re.compile(r"[^.]*\bboiler[^.]*\b(maintenance|servic)\w*[^.]*\.", re.I),
    "heating_install": re.compile(r"[^.]*\bheating[^.]*\binstall\w*[^.]*\.", re.I),
    "heating_replace": re.compile(r"[^.]*\bheating[^.]*\breplac\w*[^.]*\.", re.I),
    "heating_maint": re.compile(r"[^.]*\bheating[^.]*\bmaintenance[^.]*\.", re.I),
    "heating_tuneup": re.compile(r"[^.]*\btune[- ]?up[^.]*\.", re.I),
    "inspection": re.compile(r"[^.]*\binspect\w*[^.]*\.", re.I),
    "emergency": re.compile(r"[^.]*\bemergency\b[^.]*\.", re.I),
    "no_heat": re.compile(r"[^.]*\bno heat\b[^.]*\.", re.I),
    "thermostat": re.compile(r"[^.]*\bthermostat\w*[^.]*\.", re.I),
    "heat_pump_repair": re.compile(r"[^.]*\bheat[- ]?pump[^.]*\brepair\w*[^.]*\.", re.I),
    "heat_pump_install": re.compile(r"[^.]*\bheat[- ]?pump[^.]*\binstall\w*[^.]*\.", re.I),
    "heat_pump_maint": re.compile(r"[^.]*\bheat[- ]?pump[^.]*\b(maintenance|tune)\w*[^.]*\.", re.I),
    "ductless_repair": re.compile(r"[^.]*\b(ductless|mini[- ]?split)[^.]*\brepair\w*[^.]*\.", re.I),
    "ductless_install": re.compile(r"[^.]*\b(ductless|mini[- ]?split)[^.]*\binstall\w*[^.]*\.", re.I),
    "geothermal_install": re.compile(r"[^.]*\bgeothermal[^.]*\binstall\w*[^.]*\.", re.I),
    "gas_furnace": re.compile(r"[^.]*\bgas\b[^.]*\bfurnace[^.]*\.", re.I),
    "electric_furnace": re.compile(r"[^.]*\belectric\b[^.]*\bfurnace[^.]*\.", re.I),
    "heating_generic": re.compile(r"[^.]*\bheating\b[^.]*\b(repair|service|system)[^.]*\.", re.I),
}
BARRED = {
    "same_day": re.compile(r"\bsame[- ]day\b", re.I),
    "24_7": re.compile(r"\b(24/7|24-7|24 hours|round the clock)\b", re.I),
    "emergency_avail": re.compile(r"\bemergency (service|dispatch|repair) available\b", re.I),
    "guarantee": re.compile(r"\bguarantee\w*", re.I),
    "licensed_insured": re.compile(r"\blicen[cs]ed (and|&) insured\b", re.I),
    "free_quote": re.compile(r"\bfree (quote|estimate|consultation)\b", re.I),
    "best_top": re.compile(r"\b(best|top[- ]rated|most trusted|most knowledgeable)\b", re.I),
}


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "parameterised_requests": 0, "forms_submitted": 0,
           "tel_activated": 0, "pages": {}}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for label, u in CANDIDATES.items():
            for dev, cfg in (("desktop", {"viewport": {"width": 1440, "height": 900}}),
                             ("mobile", {"viewport": {"width": 390, "height": 844},
                                         "is_mobile": True, "has_touch": True,
                                         "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone "
                                         "OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
                                         "(KHTML, like Gecko) Version/17.5 Mobile/15E148 "
                                         "Safari/604.1"})):
                ctx = b.new_context(locale="en-US", timezone_id="America/New_York", **cfg)
                pg = ctx.new_page()
                rec = {"url": u, "device": dev}
                try:
                    r = pg.goto(u, wait_until="domcontentloaded", timeout=70000)
                    rec["status"] = r.status if r else None
                    pg.wait_for_timeout(2500)
                    pg.mouse.wheel(0, 1800)
                    pg.keyboard.press("PageDown")
                    pg.wait_for_timeout(5000)
                    pg.mouse.wheel(0, 3000)
                    pg.wait_for_timeout(3000)
                    txt = pg.evaluate("()=>document.body?document.body.innerText:''")
                    rec["h1"] = pg.evaluate(
                        "()=>[...document.querySelectorAll('h1')].map(e=>e.innerText.trim())")
                    rec["h2"] = pg.evaluate(
                        "()=>[...document.querySelectorAll('h2')].map(e=>e.innerText.trim()).slice(0,20)")
                    rec["canonical"] = pg.evaluate(
                        "()=>{const e=document.querySelector('link[rel=canonical]');return e?e.href:''}")
                    rec["forms"] = pg.evaluate("""()=>[...document.querySelectorAll('form')]
                        .map(f=>({id:f.id||'', fields:f.querySelectorAll('input,textarea,select').length,
                                  submit:!!f.querySelector('input[type=submit],button[type=submit],button:not([type])')}))""")
                    rec["tel"] = pg.evaluate("""()=>[...document.querySelectorAll('a[href^="tel:"]')]
                        .map(a=>({d:(a.getAttribute('href')||'').replace(/[^0-9]/g,''),
                                  t:(a.innerText||'').trim().slice(0,24),
                                  vis:!!(a.offsetWidth||a.offsetHeight)}))""")
                    rec["dup_ids"] = pg.evaluate("""()=>{const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
                        const d={};ids.forEach(i=>d[i]=(d[i]||0)+1);
                        return Object.entries(d).filter(([,n])=>n>1).length}""")
                    rec["overflow"] = pg.evaluate(
                        "()=>document.documentElement.scrollWidth-document.documentElement.clientWidth>4")
                    rec["intent_sentences"] = {k: len(rx.findall(txt))
                                               for k, rx in INTENT_SENT.items() if rx.search(txt)}
                    rec["barred_claims"] = sorted(k for k, rx in BARRED.items() if rx.search(txt))
                    rec["chars"] = len(txt)
                    if dev == "desktop":
                        rec["text"] = txt
                except Exception as ex:
                    rec["error"] = str(ex)[:200]
                finally:
                    ctx.close()
                out["pages"][f"{label}|{dev}"] = rec
            d = out["pages"][f"{label}|desktop"]
            m = out["pages"][f"{label}|mobile"]
            tels = sorted({t["d"] for t in (d.get("tel") or [])})
            print(f"\n=== {label} ===")
            print(f"  status D/M {d.get('status')}/{m.get('status')}  H1={d.get('h1')}")
            print(f"  forms={[f['id'] for f in (d.get('forms') or [])]} dupIDs={d.get('dup_ids')} "
                  f"overflowM={m.get('overflow')}  tel={tels}")
            print(f"  intents: {d.get('intent_sentences')}")
            print(f"  barred : {d.get('barred_claims')}")
        b.close()

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"dest-map-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("PARAMETERISED REQUESTS: 0 | FORMS SUBMITTED: 0 | TEL ACTIVATED: 0")


if __name__ == "__main__":
    main()
