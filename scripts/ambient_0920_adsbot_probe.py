#!/usr/bin/env python3
"""Ambient | 2026-09-20 | AdsBot reachability probe for the nine expansion destinations.

READ-ONLY. No parameters, no form, no tel activation, no CAPTCHA bypass.

Why this exists: the AdsBot leg inside ambient_0918_url_policy_qa.py called
page.evaluate() straight after domcontentloaded. SiteGround's SG-Captcha stub
navigates itself, which destroys the execution context, so every AdsBot row came
back "Execution context was destroyed" instead of a verdict. Two probes replace it:

  A. raw HTTP with the AdsBot UA and no JS at all - this is what a non-rendering
     crawl sees, and it is where a 202 challenge stub shows up unambiguously;
  B. a browser render with the AdsBot UA that waits for the stub to settle before
     reading the DOM, so a challenge that resolves into the real page is scored as
     reachable rather than as an error.

Each probe is repeated so an intermittent challenge cannot be mistaken for a
permanent block, and a normal-UA control run is included as a positive control.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import TZ, SNAP  # noqa
import urllib.request
import urllib.error
from playwright.sync_api import sync_playwright

STAMP = "2026-09-20"
TRIALS = 3

DEST = {
    "Furnace Repair": "https://ambientcoolingandheating.com/services/heating-services/furnace-repair/",
    "Mini Split Installation": "https://ambientcoolingandheating.com/services/cooling-services/mini-splits/",
    "Gas Boiler Repair": "https://offer.ambientcoolingandheating.com/gas-boiler-repair/",
    "Boiler Repair": "https://ambientcoolingandheating.com/services/heating-services/boiler-repair/",
    "Oil Furnace Installation": "https://ambientcoolingandheating.com/services/heating-services/oil-furnace-installations/",
    "Oil Heating System Replacement": "https://ambientcoolingandheating.com/services/heating-services/oil-replacement/",
    "Heat Pump Installation": "https://ambientcoolingandheating.com/services/heating-services/heat-pumps/",
    "Tankless Water Heater Installation": "https://ambientcoolingandheating.com/services/heating-services/tankless-water-heaters/",
    "Geothermal HVAC Installation": "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/",
}

ADSBOT = "AdsBot-Google (+http://www.google.com/adsbot.html)"
ADSBOT_MOBILE = ("Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
                 "Chrome/125.0.0.0 Mobile Safari/537.36 (compatible; AdsBot-Google-Mobile; "
                 "+http://www.google.com/mobile/adsbot.html)")
CONTROL = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
           "Chrome/125.0.0.0 Safari/537.36")

# SG-Captcha's challenge stub is a tiny self-submitting page. Real service pages
# on this site are >100 KB. 20 KB is a wide margin between the two.
STUB_BYTES = 20000


def raw(url: str, ua: str) -> dict:
    """Plain HTTP GET, no JavaScript. Mirrors a non-rendering crawl."""
    req = urllib.request.Request(url, headers={
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        # No Accept-Encoding: urllib does not transparently decompress, and a
        # compressed body would make every byte-count and grep lie.
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            body = r.read()
            hd = {k.lower(): v for k, v in r.headers.items()}
            return {"status": r.status, "bytes": len(body),
                    "sg_captcha": hd.get("sg-captcha"),
                    "x_proxy_cache": hd.get("x-proxy-cache"),
                    "content_type": hd.get("content-type"),
                    "looks_like_stub": r.status == 202 or len(body) < STUB_BYTES,
                    "has_h1": b"<h1" in body.lower(),
                    "final_url": r.url}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "bytes": 0, "error": f"HTTPError {e.code}",
                "looks_like_stub": True, "has_h1": False}
    except Exception as e:
        return {"status": None, "bytes": 0, "error": str(e)[:180],
                "looks_like_stub": None, "has_h1": False}


def rendered(b, url: str, ua: str) -> dict:
    """Render with the given UA, tolerating the SG-Captcha self-navigation."""
    ctx = b.new_context(user_agent=ua, viewport={"width": 1280, "height": 800},
                        locale="en-US", timezone_id="America/New_York")
    pg = ctx.new_page()
    out = {"status": None, "html_bytes": 0, "h1": None, "error": None}
    try:
        r = pg.goto(url, wait_until="domcontentloaded", timeout=70000)
        out["status"] = r.status if r else None
        # The challenge stub replaces itself. Wait for the document to stop
        # changing instead of reading it mid-navigation.
        for _ in range(6):
            try:
                pg.wait_for_load_state("domcontentloaded", timeout=15000)
                n = pg.evaluate("()=>document.documentElement.outerHTML.length")
                if n > STUB_BYTES:
                    break
            except Exception:
                pass
            pg.wait_for_timeout(2500)
        try:
            out["html_bytes"] = pg.evaluate("()=>document.documentElement.outerHTML.length")
            out["h1"] = pg.evaluate(
                "()=>{const e=document.querySelector('h1');return e?e.innerText.trim():null}")
            out["final_url"] = pg.evaluate("()=>location.href")
        except Exception as ex:
            out["error"] = str(ex)[:180]
    except Exception as ex:
        out["error"] = str(ex)[:180]
    finally:
        ctx.close()
    out["reachable"] = bool(out["html_bytes"] and out["html_bytes"] > STUB_BYTES and out["h1"])
    return out


def main():
    res = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "trials_per_probe": TRIALS,
           "parameterised_requests": 0, "forms_submitted": 0, "tel_activated": 0,
           "captcha_bypass_attempted": False, "website_changes": 0,
           "stub_threshold_bytes": STUB_BYTES, "destinations": {}}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        for label, url in DEST.items():
            d = {"url": url,
                 "raw_adsbot": [raw(url, ADSBOT) for _ in range(TRIALS)],
                 "raw_adsbot_mobile": [raw(url, ADSBOT_MOBILE) for _ in range(TRIALS)],
                 "raw_control": [raw(url, CONTROL) for _ in range(TRIALS)],
                 "rendered_adsbot": [rendered(b, url, ADSBOT) for _ in range(2)]}
            rs = [x["status"] for x in d["raw_adsbot"]]
            cs = [x["status"] for x in d["raw_control"]]
            stubs = sum(1 for x in d["raw_adsbot"] if x.get("looks_like_stub"))
            ok = sum(1 for x in d["rendered_adsbot"] if x.get("reachable"))
            d["verdict"] = {
                "raw_adsbot_statuses": rs,
                "raw_control_statuses": cs,
                "raw_adsbot_stub_trials": f"{stubs}/{TRIALS}",
                "rendered_adsbot_reachable": f"{ok}/2",
                # Reachable if a rendering crawl gets the real page at least once.
                # A 202 on the raw leg is a challenge, not a refusal, as long as
                # the rendered leg resolves to real content.
                "adsbot_can_reach_page": ok > 0,
                "raw_non_js_blocked": stubs == TRIALS,
            }
            res["destinations"][label] = d
            print(f"{label[:32]:32s} rawAdsBot={rs} ctl={cs} stub={stubs}/{TRIALS} "
                  f"rendered={ok}/2 -> {'REACHABLE' if ok else 'BLOCKED'}")
        b.close()
    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"adsbot-probe-{STAMP}.json"
    p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("PARAMETERISED REQUESTS: 0 | FORMS SUBMITTED: 0 | TEL ACTIVATED: 0 | CHANGES: 0")


if __name__ == "__main__":
    main()
