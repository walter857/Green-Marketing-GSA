#!/usr/bin/env python3
"""Passive cache-poisoning observation | 2026-09-17.

ZERO RISK. Sends NO tracking parameters, so it cannot seed or poison any cache.
It simply re-requests each page as an ordinary no-parameter visitor and records
whether the attribution hidden fields EVER become populated.

If a real paid visitor's click id appears in the cached HTML served to a
no-parameter request, that is proof of the cross-visitor leak obtained without
running the synthetic A/B test - and without needing a cache purge afterwards.

Any real value is SHA-256 hashed. Raw click ids are never stored or printed.
"""
from __future__ import annotations
import datetime, hashlib, json, re, sys, time, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "cross-client-attribution"
TZ = ZoneInfo("America/New_York")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
SITES = {
    "BEAVER": "https://offer.beaverbinsin.com/",
    "NOLTE": "https://offer.nolteandsons.com/landscaping-2/",
    "MASTERGRASS": "https://offer.mastergrasslawncare.com/landscaping-contractor/",
    "AMBIENT_CONTROL": "https://offer.ambientcoolingandheating.com/ac-repair/",
}
FIELD = re.compile(r'<input[^>]*name=[\'"](input_(?:[7-9]|1[0-5]))[\'"][^>]*>', re.I)
VAL = re.compile(r'value=[\'"]([^\'"]*)[\'"]')
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 14
GAP = int(sys.argv[2]) if len(sys.argv) > 2 else 45


def h(v):
    return "sha256:" + hashlib.sha256(str(v).encode()).hexdigest()[:16]


def probe(url):
    r = urllib.request.Request(url, headers={"User-Agent": UA,
                                             "Accept-Encoding": "identity"})
    with urllib.request.urlopen(r, timeout=45) as z:
        hd = {k.lower(): v for k, v in z.headers.items()}
        body = z.read().decode("utf-8", "replace")
    found = {}
    for m in FIELD.finditer(body):
        nm = m.group(1)
        v = VAL.search(m.group(0))
        v = v.group(1).strip() if v else ""
        if v:
            found[nm] = v
    return z.status, hd, found, len(body)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "method": "passive no-parameter polling; NO parameters sent; no cache seeded",
           "rounds": ROUNDS, "gap_seconds": GAP, "observations": [],
           "populated_events": []}
    print(f"passive watch: {ROUNDS} rounds x {GAP}s  (no parameters sent)\n")
    for i in range(1, ROUNDS + 1):
        for code, url in SITES.items():
            try:
                st, hd, found, n = probe(url)
                cache = (hd.get("x-proxy-cache") or hd.get("x-nitro-cache")
                         or hd.get("sg-f-cache") or "-")
                rec = {"round": i, "site": code,
                       "at": datetime.datetime.now(TZ).isoformat(),
                       "status": st, "cache": cache, "bytes": n,
                       "populated_fields": {k: h(v) for k, v in found.items()},
                       "populated_count": len(found)}
                log["observations"].append(rec)
                if found:
                    log["populated_events"].append({
                        **rec,
                        "note": "ATTRIBUTION FIELD POPULATED on a NO-PARAMETER request",
                        "value_lengths": {k: len(v) for k, v in found.items()},
                        "looks_like_real_click_id": {
                            k: bool(re.match(r"^(Cj0|CjwK|EAIa|Cj)", v)) for k, v in found.items()},
                        "looks_like_qa_marker": {
                            k: v.upper().startswith("QA") for k, v in found.items()}})
                    print(f"  !! r{i:02d} {code:16s} cache={cache:5s} "
                          f"POPULATED {list(found)} "
                          f"(hashed: {[h(v)[:22] for v in found.values()]})")
                else:
                    print(f"     r{i:02d} {code:16s} cache={cache:5s} status={st} "
                          f"fields empty")
            except Exception as e:
                print(f"     r{i:02d} {code:16s} ERROR {type(e).__name__}")
                log["observations"].append({"round": i, "site": code,
                                            "error": type(e).__name__})
        if i < ROUNDS:
            time.sleep(GAP)
    p = OUT / "passive-watch-2026-09-17.json"
    p.write_text(json.dumps(log, indent=1, default=str), encoding="utf-8")
    print(f"\npopulated events observed: {len(log['populated_events'])}")
    print(f"WROTE {p}")
    print("PARAMETERS SENT: NONE | CACHE SEEDED: NO | WEBSITE CHANGES: 0")


if __name__ == "__main__":
    sys.exit(main())
