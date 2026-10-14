#!/usr/bin/env python3
"""Ambient | Verify the EXISTING tag deployment on both domains before anything is added.

READ-ONLY. No parameters, no form submissions, no tel activation.

Answers: are GTM-PQTPQ436 / G-9X9ZHNCRWF / AW-11155434808 already present, what destination
ids do they actually send to, is anything duplicated, and what fires on a plain page view
versus only on a form submit. The point is to establish that nothing needs installing.
"""
from __future__ import annotations
import sys, re, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
from playwright.sync_api import sync_playwright

STAMP = "2026-09-25"
GTM, GA4, AW = "GTM-PQTPQ436", "G-9X9ZHNCRWF", "11155434808"
TARGETS = {
    "MAIN furnace-repair": "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/",
    "MAIN heating hub": "https://ambientcoolingandheating.com/services/heating-services/",
    "OFFER gas-boiler": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
    "OFFER hvac-installation": "https://offer.ambientcoolingandheating.com/hvac-installation/",
}


def main():
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "parameterised_requests": 0, "forms_submitted": 0,
           "tags_installed_by_this_script": 0, "pages": {}}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for label, url in TARGETS.items():
            ctx = b.new_context(locale="en-US", timezone_id="America/New_York",
                                viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            net = []
            pg.on("request", lambda r: net.append(r.url))
            rec = {"url": url}
            try:
                r = pg.goto(url, wait_until="domcontentloaded", timeout=70000)
                rec["status"] = r.status if r else None
                pg.wait_for_timeout(2500)
                pre = len(net)
                # NitroPack defers JS until interaction
                pg.mouse.move(420, 300)
                pg.mouse.wheel(0, 1800)
                pg.keyboard.press("PageDown")
                pg.wait_for_timeout(7000)
                pg.mouse.wheel(0, 3000)
                pg.wait_for_timeout(4000)

                rec["gtm_containers"] = pg.evaluate(
                    "()=>Object.keys(window.google_tag_manager||{})")
                rec["dataLayer_len"] = pg.evaluate(
                    "()=>Array.isArray(window.dataLayer)?window.dataLayer.length:-1")
                rec["gtag_present"] = pg.evaluate("()=>typeof window.gtag==='function'")
                # every inline/external script that names one of our ids
                rec["script_refs"] = pg.evaluate(f"""()=>{{
                    const ids=['{GTM}','{GA4}','{AW}'];
                    const out=[];
                    document.querySelectorAll('script').forEach(s=>{{
                      const t=(s.src||'')+' '+(s.textContent||'').slice(0,4000);
                      ids.forEach(i=>{{ if(t.includes(i)) out.push({{id:i, src:s.src||'(inline)'}}); }});
                    }});
                    return out;
                }}""")
                after = net[pre:]
                allnet = net[:]

                def count(rx):
                    return [u for u in allnet if re.search(rx, u, re.I)]

                gtm_loads = count(r"googletagmanager\.com/gtm\.js")
                gtag_loads = count(r"googletagmanager\.com/gtag/js")
                ga4_hits = count(r"/g/collect|analytics\.google\.com/g/")
                aw_hits = count(re.escape(AW))
                rec["gtm_js_loads"] = len(gtm_loads)
                rec["gtag_js_loads"] = len(gtag_loads)
                rec["ga4_collect_hits"] = len(ga4_hits)
                rec["aw_requests"] = len(aw_hits)
                # which destination ids appear in gtag/js?
                dest = set()
                for u in gtm_loads + gtag_loads:
                    m = re.search(r"[?&]id=([^&]+)", u)
                    if m:
                        dest.add(m.group(1))
                rec["tag_destination_ids"] = sorted(dest)
                # conversion-ish events observed WITHOUT submitting anything
                ev = {}
                for u in aw_hits:
                    m = re.search(r"[?&]en=([^&]+)", u)
                    if m:
                        ev[m.group(1)] = ev.get(m.group(1), 0) + 1
                rec["aw_events_on_pageview_only"] = ev
                rec["conversion_event_on_pageview"] = any(
                    k in ("conversion", "form_submit", "form_submission")
                    for k in ev)
                # duplicate tag check
                rec["duplicate_gtm_container"] = len(
                    [c for c in rec["gtm_containers"] if c.startswith("GTM-")]) > 1
                rec["wcm_call_swap"] = [u[:150] for u in allnet if "/wcm?" in u]
            except Exception as ex:
                rec["error"] = str(ex)[:200]
            finally:
                ctx.close()
            out["pages"][label] = rec
            print(f"\n=== {label} ===  HTTP {rec.get('status')}")
            print(f"  google_tag_manager keys : {rec.get('gtm_containers')}")
            print(f"  tag destination ids     : {rec.get('tag_destination_ids')}")
            print(f"  gtm.js loads={rec.get('gtm_js_loads')}  gtag/js loads="
                  f"{rec.get('gtag_js_loads')}  duplicate GTM container="
                  f"{rec.get('duplicate_gtm_container')}")
            print(f"  GA4 /g/collect hits     : {rec.get('ga4_collect_hits')}")
            print(f"  AW-{AW} requests : {rec.get('aw_requests')}")
            print(f"  AW events on PAGE VIEW ONLY (no submit): "
                  f"{rec.get('aw_events_on_pageview_only')}")
            print(f"  conversion fired on pageview alone: "
                  f"{rec.get('conversion_event_on_pageview')}")
            for w in (rec.get("wcm_call_swap") or [])[:1]:
                print(f"  call-swap request       : {w[:120]}")
            for s in (rec.get("script_refs") or [])[:6]:
                print(f"  script ref {s['id']:16s} <- {s['src'][:70]}")
        b.close()

    print("\n=== SUMMARY ===")
    allids = sorted({i for p in out["pages"].values()
                     for i in (p.get("tag_destination_ids") or [])})
    out["all_destination_ids_seen"] = allids
    print(f"  destination ids seen across all pages: {allids}")
    unexpected = [i for i in allids if i not in (GTM, GA4, f"AW-{AW}")]
    out["unexpected_destination_ids"] = unexpected
    print(f"  UNEXPECTED ids (would mean an extra tag): {unexpected or 'none'}")
    fired = [k for k, p in out["pages"].items() if p.get("conversion_event_on_pageview")]
    out["pages_firing_conversion_on_pageview"] = fired
    print(f"  pages firing a conversion event on PAGE VIEW alone: {fired or 'none'}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"tag-audit-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("TAGS INSTALLED: 0 | CONVERSION EVENTS CREATED: 0 | FORMS SUBMITTED: 0")


if __name__ == "__main__":
    main()
