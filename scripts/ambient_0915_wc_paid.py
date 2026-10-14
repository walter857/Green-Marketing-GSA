#!/usr/bin/env python3
"""Ambient | 2026-09-15 | paid-search slice of WhatConverts: qualification, numbers, CPQL bound.

READ-ONLY. No PII retained. Nothing in WhatConverts is modified.
"""
from __future__ import annotations
import base64, json, os, re, sys, datetime, urllib.request, urllib.error
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import CID, IN5, SNAP, TZ, client, q, identity_gate  # noqa
from gm_gsa.config import load_dotenv_if_available  # noqa

load_dotenv_if_available(ROOT / ".env")
TOKEN = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
SECRET = (os.environ.get("WHATCONVERTS_SECRET") or "").strip()
auth = base64.b64encode(f"{TOKEN}:{SECRET}".encode()).decode()
PROFILE, STAMP = "105803", "2026-09-15"
PAID, DEST, MIXED, UNEXPLAINED = "4107056354", "4107610932", "4109141456", "4104159517"
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "read_only": True}


def call(path):
    r = urllib.request.Request(f"https://app.whatconverts.com/api/v1/{path}",
                               headers={"Authorization": f"Basic {auth}",
                                        "Accept": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as e:
        return None, {"error": type(e).__name__}


def dg(s):
    d = re.sub(r"\D", "", str(s or ""))
    return d[-10:] if len(d) >= 10 else d


rows, page = [], 1
while page <= 12:
    st, d = call(f"leads?profile_id={PROFILE}&start_date=2026-06-17&end_date=2026-09-15"
                 f"&leads_per_page=250&page_number={page}")
    if st != 200:
        break
    rows += d.get("leads", [])
    if page >= d.get("total_pages", 1) or not d.get("leads"):
        break
    page += 1
print(f"leads pulled 2026-06-17..2026-09-15: {len(rows)}")

print("\n=== 1. FIELD INVENTORY (keys only, to confirm what WhatConverts actually returns) ===")
keys = Counter()
for r in rows:
    for k in r:
        keys[k] += 1
present = {k: v for k, v in keys.items()}
interesting = [k for k in sorted(present) if re.search(
    r"gclid|gbraid|wbraid|utm|source|medium|campaign|keyword|landing|url|quot|sale|"
    r"value|status|device|number|type|spam|dup", k, re.I)]
for k in interesting:
    nonempty = sum(1 for r in rows if str(r.get(k) or "").strip()
                   and str(r.get(k)) not in ("None", "Not Set"))
    print(f"  {k:26s} present_in={present[k]:>3}  non_empty={nonempty:>3}")
out["field_inventory"] = {k: {"present_in": present[k],
                              "non_empty": sum(1 for r in rows
                                               if str(r.get(k) or "").strip()
                                               and str(r.get(k)) not in ("None", "Not Set"))}
                          for k in interesting}


def is_paid_search(r):
    """Google Ads paid search only. LSA is a different department and is EXCLUDED."""
    s = str(r.get("lead_source") or "").lower()
    m = str(r.get("lead_medium") or "").lower()
    if "lsa" in s:
        return False
    return (s in ("google", "google ads", "adwords") and m in ("cpc", "ppc", "paid"))


def is_lsa(r):
    return "lsa" in str(r.get("lead_source") or "").lower()


def is_gbp(r):
    return "gbp" in str(r.get("lead_source") or "").lower()


paid = [r for r in rows if is_paid_search(r)]
lsa = [r for r in rows if is_lsa(r)]
gbp = [r for r in rows if is_gbp(r)]
other = [r for r in rows if not (is_paid_search(r) or is_lsa(r) or is_gbp(r))]
print(f"\n=== 2. CHANNEL SPLIT (90 days) ===")
print(f"  Google Ads paid search : {len(paid):>4}  ({100*len(paid)/len(rows):.1f}%)")
print(f"  LSA (out of scope)     : {len(lsa):>4}  ({100*len(lsa)/len(rows):.1f}%)")
print(f"  GBP                    : {len(gbp):>4}  ({100*len(gbp)/len(rows):.1f}%)")
print(f"  other/organic/direct   : {len(other):>4}  ({100*len(other)/len(rows):.1f}%)")
out["channel_split_90d"] = {"total": len(rows), "paid_search": len(paid),
                            "lsa_out_of_scope": len(lsa), "gbp": len(gbp),
                            "other": len(other)}

print(f"\n=== 3. PAID-SEARCH LEADS IN DETAIL ({len(paid)} leads) ===")
q_counter = Counter(str(r.get("quotable")) for r in paid)
t_counter = Counter(str(r.get("lead_type")) for r in paid)
n_counter = Counter("..." + (dg(r.get("tracking_number") or r.get("phone_number")) or "none")[-4:]
                    for r in paid)
g_have = sum(1 for r in paid if str(r.get("gclid") or "").strip())
lp_have = sum(1 for r in paid if str(r.get("landing_url") or "").strip())
print(f"  lead_type       : {dict(t_counter)}")
print(f"  quotable        : {dict(q_counter)}")
print(f"  tracking number : {dict(n_counter)}")
print(f"  with gclid      : {g_have}/{len(paid)}  ({100*g_have/len(paid) if paid else 0:.0f}%)")
print(f"  with landing_url: {lp_have}/{len(paid)}")
out["paid_detail_90d"] = {"lead_type": dict(t_counter), "quotable": dict(q_counter),
                          "tracking_number_last4": dict(n_counter),
                          "with_gclid": g_have, "with_landing_url": lp_have}

print(f"\n=== 4. QUALIFICATION RATE ===")
for label, grp in (("paid search", paid), ("GBP", gbp), ("LSA", lsa), ("ALL", rows)):
    yes = sum(1 for r in grp if str(r.get("quotable")) == "Yes")
    no = sum(1 for r in grp if str(r.get("quotable")) == "No")
    pend = sum(1 for r in grp if str(r.get("quotable")) == "Pending")
    notset = sum(1 for r in grp if str(r.get("quotable")) in ("Not Set", "None", ""))
    decided = yes + no
    print(f"  {label:12s} n={len(grp):>4}  Yes={yes:>3} No={no:>3} Pending={pend:>3} "
          f"NotSet={notset:>3}  qualified_rate_of_decided="
          f"{100*yes/decided if decided else 0:>5.1f}%")
    out.setdefault("qualification", {})[label] = {
        "n": len(grp), "yes": yes, "no": no, "pending": pend, "not_set": notset,
        "qualified_rate_of_decided_pct": round(100 * yes / decided, 1) if decided else None}

print(f"\n=== 5. THE MIXED-SOURCE NUMBER IS OUTPERFORMING THE PAID NUMBER ===")
by_num = defaultdict(lambda: {"n": 0, "yes": 0, "sources": Counter()})
for r in rows:
    d = dg(r.get("tracking_number") or r.get("phone_number"))
    k = d or "none"
    by_num[k]["n"] += 1
    if str(r.get("quotable")) == "Yes":
        by_num[k]["yes"] += 1
    by_num[k]["sources"][f"{r.get('lead_source')}/{r.get('lead_medium')}"] += 1
role = {PAID: "APPROVED PAID", MIXED: "MIXED SOURCE", DEST: "FORWARDING DEST",
        UNEXPLAINED: "UNEXPLAINED"}
for k, v in sorted(by_num.items(), key=lambda x: -x[1]["n"]):
    print(f"  ...{k[-4:]:4s} {role.get(k,''):16s} n={v['n']:>4} qualified={v['yes']:>3}  "
          f"top_sources={dict(v['sources'].most_common(3))}")
out["by_tracking_number"] = {("..." + k[-4:]): {"role": role.get(k, "OTHER/GBP/LSA"),
                                                "n": v["n"], "qualified_yes": v["yes"],
                                                "top_sources": dict(v["sources"].most_common(4))}
                             for k, v in sorted(by_num.items(), key=lambda x: -x[1]["n"])}

print(f"\n=== 6. REVENUE FIELDS ===")
qv = sum(1 for r in rows if r.get("quote_value"))
sv = sum(1 for r in rows if r.get("sales_value"))
print(f"  quote_value populated: {qv}/{len(rows)}")
print(f"  sales_value populated: {sv}/{len(rows)}")
print("  => sold-job revenue, gross profit, ROAS and CAC are NOT computable from WhatConverts")
out["revenue_fields"] = {"quote_value_populated": qv, "sales_value_populated": sv,
                         "computable": False}

print(f"\n=== 7. PAID-SEARCH CPQL BOUND, settled September ===")
c = client(); identity_gate(c, verbose=False)
spend = sum(r.metrics.cost_micros for r in q(c, f"""
    SELECT campaign.id, metrics.cost_micros FROM campaign WHERE campaign.id IN ({IN5})
      AND segments.date BETWEEN '2026-09-01' AND '2026-09-14'""")) / 1e6
sep_paid = [r for r in rows if is_paid_search(r)
            and "2026-09-01" <= str(r.get("date_created"))[:10] <= "2026-09-14"]
sep_yes = sum(1 for r in sep_paid if str(r.get("quotable")) == "Yes")
sep_pending = sum(1 for r in sep_paid if str(r.get("quotable")) == "Pending")
print(f"  Google Ads spend 09-01..09-14      : ${spend:,.2f}")
print(f"  WhatConverts paid-search leads     : {len(sep_paid)}")
print(f"  of those, quotable = Yes           : {sep_yes}")
print(f"  of those, quotable = Pending       : {sep_pending}")
if sep_yes:
    print(f"  CPQL upper bound (Yes only)        : ${spend/sep_yes:,.2f}")
if sep_yes + sep_pending:
    print(f"  CPQL lower bound (Yes + Pending)   : ${spend/(sep_yes+sep_pending):,.2f}")
print("  NOTE: an upper bound only - see the proxy-cache defect. Paid calls that lost their")
print("        click id are invisible here, so true paid volume is >= this count.")
out["cpql_bound_sep_settled"] = {
    "google_ads_spend": round(spend, 2), "paid_search_leads": len(sep_paid),
    "quotable_yes": sep_yes, "quotable_pending": sep_pending,
    "cpql_upper_bound": round(spend / sep_yes, 2) if sep_yes else None,
    "cpql_lower_bound": round(spend / (sep_yes + sep_pending), 2)
    if (sep_yes + sep_pending) else None,
    "caveat": "upper bound; click-id loss means true paid lead count is >= this"}

p = SNAP / f"wc-paid-analysis-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
