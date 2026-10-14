#!/usr/bin/env python3
"""Ambient | 2026-09-15 | WhatConverts <-> Google Ads reconciliation. READ-ONLY.

No routing, number, profile or lead is modified. Credential values are never printed or
written. No lead PII is retained: no names, telephone numbers, email addresses, message
bodies or recordings. Leads are identified only by their WhatConverts lead_id.
"""
from __future__ import annotations
import base64, json, os, re, sys, datetime, urllib.request, urllib.error
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import CID, IN5, NAME, SNAP, TZ, client, q, identity_gate  # noqa
from gm_gsa.config import load_dotenv_if_available  # noqa
from gm_gsa.google_ads import enum_name as E  # noqa

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()
PROFILE = "105803"
STAMP = "2026-09-15"
PAID, DEST, MIXED = "4107056354", "4107610932", "4109141456"
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "read_only": True,
       "pii_policy": "no names, phones, emails, message bodies or recordings retained"}


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
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return e.code, {"error": redact(e.read().decode("utf-8", errors="replace"))[:300]}
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {redact(str(e))[:200]}"}


def dg(s):
    d = re.sub(r"\D", "", str(s or ""))
    return d[-10:] if len(d) >= 10 else d


print("=== 0. CREDENTIAL + ACCESS CHECK (values never printed) ===")
print(f"  WHATCONVERTS_API_TOKEN non-empty: {bool(TOKEN)}")
print(f"  WHATCONVERTS_SECRET    non-empty: {bool(SECRET)}")
st, acct = call("accounts")
print(f"  GET /accounts -> HTTP {st}")
if st != 200:
    out["access"] = {"status": st, "detail": acct}
    print(f"  BLOCKED: {acct}")
    (SNAP / f"wc-reconciliation-{STAMP}.json").write_text(
        json.dumps(out, indent=1, default=str), encoding="utf-8")
    sys.exit(0)
out["access"] = {"status": 200, "accounts": len(acct.get("accounts", []))}

print("\n=== 1. PROFILE + TRACKING NUMBER CONFIGURATION ===")
st, profs = call(f"profiles?account_id={acct['accounts'][0]['account_id']}"
                 if acct.get("accounts") else "profiles")
prof_rows = []
if st == 200:
    for p in profs.get("profiles", []):
        prof_rows.append({"profile_id": str(p.get("profile_id")),
                          "profile_name": p.get("profile_name")})
        print(f"  profile {p.get('profile_id')}  {p.get('profile_name')}")
out["profiles"] = prof_rows

st, nums = call(f"tracking-numbers?profile_id={PROFILE}&leads_per_page=250")
num_rows = []
if st == 200:
    for n in nums.get("tracking_numbers", nums.get("phone_numbers", [])):
        d = dg(n.get("tracking_number") or n.get("number"))
        role = ("APPROVED_PAID" if d == PAID else
                "MIXED_SOURCE" if d == MIXED else
                "FORWARDING_DESTINATION" if d == DEST else "OTHER")
        num_rows.append({"digits_last10": d, "role": role,
                         "name": n.get("number_name") or n.get("name"),
                         "source": n.get("source"), "medium": n.get("medium"),
                         "campaign": n.get("campaign"),
                         "swap_target": n.get("swap_target") or n.get("number_to_swap"),
                         "status": n.get("status")})
        print(f"  ...{d[-4:]:4s} {role:22s} name={n.get('number_name') or n.get('name')!r} "
              f"source={n.get('source')!r} medium={n.get('medium')!r}")
else:
    print(f"  tracking-numbers -> HTTP {st}: {nums}")
out["tracking_numbers"] = num_rows
out["tracking_number_endpoint_status"] = st

print("\n=== 2. PULL LEADS (Sept MTD + prior 90 days) ===")
WINDOWS = {"sep_mtd": ("2026-09-01", "2026-09-15"),
           "prior_90": ("2026-06-17", "2026-09-15")}
leads_by_window = {}
for wname, (lo, hi) in WINDOWS.items():
    rows, page = [], 1
    while page <= 12:
        st, d = call(f"leads?profile_id={PROFILE}&start_date={lo}&end_date={hi}"
                     f"&leads_per_page=250&page_number={page}")
        if st != 200:
            print(f"  {wname} page {page} -> HTTP {st}: {d}")
            break
        batch = d.get("leads", [])
        rows += batch
        tp = d.get("total_pages", 1)
        if page >= tp or not batch:
            break
        page += 1
    leads_by_window[wname] = rows
    print(f"  {wname} {lo}..{hi}: {len(rows)} leads")
out["lead_counts"] = {k: len(v) for k, v in leads_by_window.items()}


def analyse(rows, label):
    res = {"window": label, "total": len(rows)}
    src = Counter(f"{r.get('lead_source')}/{r.get('lead_medium')}" for r in rows)
    res["source_medium"] = dict(src.most_common(14))
    typ = Counter(r.get("lead_type") for r in rows)
    res["lead_type"] = dict(typ)
    paid = [r for r in rows if str(r.get("lead_medium") or "").lower() in
            ("cpc", "ppc", "paid", "paidsearch", "paid_search")
            or str(r.get("lead_source") or "").lower() in ("google ads", "adwords")]
    res["paid_labelled"] = len(paid)

    def has(r, *keys):
        return any(str(r.get(k) or "").strip() for k in keys)

    res["click_id_retention"] = {
        "gclid": sum(1 for r in rows if has(r, "gclid")),
        "gbraid": sum(1 for r in rows if has(r, "gbraid")),
        "wbraid": sum(1 for r in rows if has(r, "wbraid")),
        "msclkid": sum(1 for r in rows if has(r, "msclkid")),
        "any_click_id": sum(1 for r in rows if has(r, "gclid", "gbraid", "wbraid")),
    }
    res["paid_click_id_retention"] = {
        "paid_rows": len(paid),
        "with_gclid": sum(1 for r in paid if has(r, "gclid")),
        "with_any_click_id": sum(1 for r in paid if has(r, "gclid", "gbraid", "wbraid")),
    }
    res["utm_retention"] = {k: sum(1 for r in rows if has(r, k)) for k in
                            ("utm_source", "utm_medium", "utm_campaign",
                             "utm_term", "utm_content")}
    res["landing_url_present"] = sum(1 for r in rows if has(r, "landing_url"))
    # landing page distribution, path only - no query strings, no PII
    lp = Counter()
    for r in rows:
        u = str(r.get("landing_url") or "")
        m = re.match(r"https?://([^/]+)(/[^?#]*)", u)
        lp[(m.group(1) + m.group(2)) if m else "(none)"] += 1
    res["landing_paths"] = dict(lp.most_common(12))
    # tracking number used
    tn = Counter()
    for r in rows:
        d = dg(r.get("tracking_number") or r.get("phone_number"))
        tn["...{}".format(d[-4:]) if d else "(none)"] += 1
    res["tracking_number_last4"] = dict(tn.most_common(10))
    # qualification / booking / sale
    res["quotable"] = Counter(str(r.get("quotable")) for r in rows)
    res["quote_value_present"] = sum(1 for r in rows if r.get("quote_value"))
    res["sales_value_present"] = sum(1 for r in rows if r.get("sales_value"))
    res["lead_status"] = dict(Counter(str(r.get("lead_status")) for r in rows).most_common(10))
    # duplicate detection WITHOUT storing PII: hash of (type, tracking number, minute)
    import hashlib
    seen = defaultdict(list)
    for r in rows:
        key = hashlib.sha256(
            f"{r.get('lead_type')}|{dg(r.get('phone_number'))}|"
            f"{str(r.get('date_created'))[:16]}".encode()).hexdigest()[:16]
        seen[key].append(r.get("lead_id"))
    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    res["duplicate_groups"] = len(dupes)
    res["duplicate_extra_records"] = sum(len(v) - 1 for v in dupes.values())
    res["unique_lead_estimate"] = len(rows) - res["duplicate_extra_records"]
    return res


print("\n=== 3. ANALYSIS ===")
out["analysis"] = {}
for wname, rows in leads_by_window.items():
    if not rows:
        continue
    a = analyse(rows, wname)
    out["analysis"][wname] = a
    print(f"\n  --- {wname}: {a['total']} leads ---")
    print(f"    lead_type            : {a['lead_type']}")
    print(f"    source/medium (top)  : {dict(list(a['source_medium'].items())[:8])}")
    print(f"    paid-labelled rows   : {a['paid_labelled']}")
    print(f"    click-id retention   : {a['click_id_retention']}")
    print(f"    paid click-id        : {a['paid_click_id_retention']}")
    print(f"    utm retention        : {a['utm_retention']}")
    print(f"    landing_url present  : {a['landing_url_present']}/{a['total']}")
    print(f"    landing paths        : {dict(list(a['landing_paths'].items())[:6])}")
    print(f"    tracking number last4: {a['tracking_number_last4']}")
    print(f"    quotable             : {dict(a['quotable'])}")
    print(f"    quote_value present  : {a['quote_value_present']}  "
          f"sales_value present: {a['sales_value_present']}")
    print(f"    duplicate groups     : {a['duplicate_groups']} "
          f"(extra records {a['duplicate_extra_records']})")
    print(f"    UNIQUE LEAD ESTIMATE : {a['unique_lead_estimate']} of {a['total']}")

print("\n=== 4. GOOGLE ADS SIDE, SAME WINDOW ===")
c = client(); identity_gate(c, verbose=False)
g = q(c, f"""SELECT campaign.id, segments.conversion_action_name,
                    metrics.conversions, metrics.all_conversions
             FROM campaign WHERE campaign.id IN ({IN5})
               AND segments.date BETWEEN '2026-09-01' AND '2026-09-14'""")
ga = defaultdict(lambda: {"conv": 0.0, "all": 0.0})
for r in g:
    ga[r.segments.conversion_action_name]["conv"] += r.metrics.conversions
    ga[r.segments.conversion_action_name]["all"] += r.metrics.all_conversions
out["google_ads_sep_settled"] = {k: {"conversions": round(v["conv"], 2),
                                     "all_conversions": round(v["all"], 2)}
                                 for k, v in ga.items()}
for k, v in sorted(ga.items(), key=lambda x: -x[1]["all"]):
    print(f"  {v['conv']:>6.2f} / {v['all']:>6.2f}  {k}")
tot_primary = sum(v["conv"] for v in ga.values())
print(f"  Google Ads Primary conversions 09-01..09-14: {tot_primary:.2f}")
out["google_ads_primary_total"] = round(tot_primary, 2)

print("\n=== 5. RECONCILIATION VERDICT ===")
sep = out["analysis"].get("sep_mtd", {})
v = {
    "google_ads_primary_conversions": round(tot_primary, 2),
    "whatconverts_leads_same_window": sep.get("total"),
    "whatconverts_unique_estimate": sep.get("unique_lead_estimate"),
    "whatconverts_paid_labelled": sep.get("paid_labelled"),
    "whatconverts_paid_with_click_id": (sep.get("paid_click_id_retention") or {}).get("with_any_click_id"),
}
for k, x in v.items():
    print(f"  {k}: {x}")
out["verdict"] = v

p = SNAP / f"wc-reconciliation-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
