#!/usr/bin/env python3
"""Map every WhatConverts tracking number to the traffic source it is assigned to, and list
the profiles on the account, so 410-914-1456 can be judged on configuration rather than on
its absence from an approved list. Read-only. No routing is changed. No PII retained."""
from __future__ import annotations
import base64, json, os, sys, urllib.request, urllib.error, datetime, re
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import EVID, TZ  # noqa
from gm_gsa.config import load_dotenv_if_available  # noqa

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()
PROFILE = "105803"
LABEL = {"4107056354": "PAID landing-page number",
         "4107610932": "ORGANIC / main line",
         "4109141456": "UNDER INVESTIGATION"}
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "read_only": True}


def redact(s):
    for v in (TOKEN, SECRET):
        if v:
            s = s.replace(v, "[REDACTED]")
    return s


def call(path):
    r = urllib.request.Request(f"https://app.whatconverts.com/api/v1/{path}",
                               headers={"Authorization": f"Basic {auth}",
                                        "Accept": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=45) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return e.code, {"error": redact(e.read().decode("utf-8", errors="replace"))[:200]}
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {redact(str(e))[:150]}"}


def dg(s):
    d = re.sub(r"\D", "", str(s or ""))
    return d[-10:] if len(d) >= 10 else d


print("=== ACCOUNTS AND PROFILES ON THIS WHATCONVERTS LOGIN ===")
st, acc = call("accounts")
rows = acc.get("accounts", []) if isinstance(acc, dict) else []
print(f"  /accounts HTTP {st}: {len(rows)} account(s)")
for a in rows:
    aid = a.get("account_id") or a.get("id")
    print(f"    account_id={aid}  name={str(a.get('account_name') or a.get('name'))!r}")
    out.setdefault("accounts", []).append({"account_id": aid,
                                           "name": a.get("account_name") or a.get("name")})
    for pp in [f"profiles?account_id={aid}", f"accounts/{aid}/profiles"]:
        s2, pr = call(pp)
        if s2 == 200:
            plist = pr.get("profiles", pr) if isinstance(pr, dict) else pr
            if isinstance(plist, list):
                print(f"      {pp} -> {len(plist)} profile(s)")
                for p in plist:
                    pid = p.get("profile_id") or p.get("id")
                    pnm = p.get("profile_name") or p.get("name")
                    print(f"        profile_id={pid}  name={pnm!r}")
                    out.setdefault("profiles", []).append({"profile_id": pid, "name": pnm})
                break
        else:
            print(f"      {pp} -> HTTP {s2}")

print("\n=== TRACKING NUMBER x TRAFFIC SOURCE (measured from lead records) ===")
leads, page = [], 1
while True:
    st, d = call(f"leads?profile_id={PROFILE}&start_date=2026-07-01&end_date=2026-09-10"
                 f"&leads_per_page=250&page_number={page}")
    if st != 200:
        break
    got = d.get("leads", [])
    leads += got
    if page >= (d.get("total_pages") or 1) or not got:
        break
    page += 1
print(f"  leads 2026-07-01..2026-09-10: {len(leads)}")

m = defaultdict(lambda: {"src": Counter(), "med": Counter(), "dest": Counter(),
                         "profile": Counter(), "n": 0, "gclid": 0})
for l in leads:
    t = dg(l.get("tracking_number"))
    if not t:
        continue
    e = m[t]
    e["n"] += 1
    e["src"][str(l.get("lead_source"))] += 1
    e["med"][str(l.get("lead_medium"))] += 1
    e["dest"][dg(l.get("destination_number"))] += 1
    e["profile"][str(l.get("profile"))] += 1
    if str(l.get("gclid") or "").strip():
        e["gclid"] += 1

print(f"\n  {'tracking #':<13}{'n':>4}{'gclid':>7}  {'lead_source(s)':<40}{'routes to':<13}profile")
for t, e in sorted(m.items(), key=lambda z: -z[1]["n"]):
    srcs = ", ".join(f"{k}({v})" for k, v in e["src"].most_common(3))
    dest = e["dest"].most_common(1)[0][0] if e["dest"] else "-"
    prof = e["profile"].most_common(1)[0][0] if e["profile"] else "-"
    star = "  <<<" if t in LABEL else ""
    print(f"  {t:<13}{e['n']:>4}{e['gclid']:>7}  {srcs[:38]:<40}{dest:<13}{prof[:26]}{star}")
out["tracking_number_map"] = {
    t: {"leads": e["n"], "with_gclid": e["gclid"],
        "lead_sources": dict(e["src"]), "lead_mediums": dict(e["med"]),
        "destinations": dict(e["dest"]), "profiles": dict(e["profile"]),
        "label": LABEL.get(t)} for t, e in m.items()}

print("\n=== THE THREE NAMED NUMBERS ===")
for num, lab in LABEL.items():
    e = m.get(num)
    print(f"\n  {num}  ({lab})")
    if not e:
        d2 = Counter(dg(l.get("destination_number")) for l in leads)
        if num in d2:
            print(f"    NOT a tracking number. Appears as a DESTINATION on {d2[num]} leads")
            print(f"    -> this is the line calls RING TO, not a number shown on a page.")
        else:
            print("    does not appear in lead data at all")
        continue
    print(f"    role      : TRACKING NUMBER (a number displayed to visitors and dialled)")
    print(f"    leads     : {e['n']}   of which carry a gclid: {e['gclid']}")
    print(f"    sources   : {dict(e['src'])}")
    print(f"    mediums   : {dict(e['med'])}")
    print(f"    routes to : {dict(e['dest'])}")
    print(f"    profile   : {dict(e['profile'])}")

print("\n=== VERDICT ON 410-914-1456 ===")
e = m.get("4109141456")
if e:
    gsa = any("gsa" in s.lower() or "cooling traffic" in s.lower()
              for s in list(e["src"]) + list(e["profile"]))
    print(f"  It IS a configured WhatConverts tracking number: {e['n']} leads.")
    print(f"  Assigned traffic source(s): {dict(e['src'])}")
    print(f"  Profile(s)                : {dict(e['profile'])}")
    print(f"  Leads carrying a gclid    : {e['gclid']}")
    print(f"  Names GSA / Cooling Traffic: {gsa}")
    out["verdict_4109141456"] = {"is_tracking_number": True, "leads": e["n"],
                                 "sources": dict(e["src"]), "profiles": dict(e["profile"]),
                                 "with_gclid": e["gclid"],
                                 "names_gsa_cooling_traffic": gsa}
else:
    print("  Not present as a tracking number in this window.")
p = EVID / "2026-09-10d-number-source-map.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p.relative_to(ROOT)}")
