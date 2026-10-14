#!/usr/bin/env python3
"""READ-ONLY invalid-traffic audit. One segmentation dimension at a time, settled periods only.
Changes nothing: no IP exclusion, network, device, schedule or location is touched."""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
       "mode": "READ-ONLY. No IP exclusion, network, device, schedule or location changed."}
W = ("2026-08-14", "2026-09-08")   # settled only
print(f"=== SETTLED WINDOW {W[0]} .. {W[1]} ===")

M = ("metrics.clicks, metrics.invalid_clicks, metrics.invalid_click_rate, "
     "metrics.impressions, metrics.cost_micros")


def run(label, sel, keyfn, src="campaign", extra_where=""):
    print(f"\n=== {label} ===")
    agg = defaultdict(lambda: {"clicks": 0, "invalid": 0, "impressions": 0, "cost": 0.0})
    try:
        rows = q(c, f"SELECT campaign.id, {sel + ', ' if sel else ''}{M} FROM {src} "
                    f"WHERE campaign.id IN ({IN5}) "
                    f"AND segments.date BETWEEN '{W[0]}' AND '{W[1]}'{extra_where}")
    except Exception as e:
        print(f"  QUERY REJECTED: {type(e).__name__}: {str(e)[:200]}")
        out[label] = {"error": str(e)[:300]}
        return None
    for r in rows:
        k = keyfn(r)
        agg[k]["clicks"] += r.metrics.clicks
        agg[k]["invalid"] += r.metrics.invalid_clicks
        agg[k]["impressions"] += r.metrics.impressions
        agg[k]["cost"] += r.metrics.cost_micros / 1e6
    res = {}
    print(f"  {'segment':<34}{'impr':>8}{'billable':>10}{'invalid':>9}{'raw':>8}{'inv%':>8}"
          f"{'cost':>10}")
    for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["invalid"]):
        raw = v["clicks"] + v["invalid"]
        pct = 100 * v["invalid"] / raw if raw else 0
        v["cost"] = round(v["cost"], 2)
        v["raw_clicks"] = raw
        v["invalid_pct"] = round(pct, 2)
        res[str(k)] = v
        print(f"  {str(k)[:34]:<34}{v['impressions']:>8}{v['clicks']:>10}{v['invalid']:>9}"
              f"{raw:>8}{pct:>7.2f}%{v['cost']:>10.2f}")
    out[label] = res
    return res


tot = run("A_by_campaign", "", lambda r: NAME[str(r.campaign.id)])
run("B_by_date", "segments.date", lambda r: r.segments.date)
run("C_by_device", "segments.device", lambda r: E(r.segments.device))
run("D_by_network", "segments.ad_network_type", lambda r: E(r.segments.ad_network_type))
run("E_by_click_type", "segments.click_type", lambda r: E(r.segments.click_type))

print("\n=== F. SEGMENT COMPATIBILITY NOTES ===")
print("  metrics.invalid_clicks is a CAMPAIGN-level metric. It is rejected FROM keyword_view")
print("  and FROM ad_group_ad, and it cannot be combined with segments.hour. Each dimension")
print("  above was therefore queried on its own against `campaign`, and only then compared.")

print("\n=== G. ACCOUNT-WIDE CONTEXT (all campaigns, same settled window) ===")
acct = q(c, f"SELECT {M} FROM customer WHERE segments.date BETWEEN '{W[0]}' AND '{W[1]}'")
if acct:
    m2 = acct[0].metrics
    raw = m2.clicks + m2.invalid_clicks
    print(f"  whole account: impressions={m2.impressions}, billable clicks={m2.clicks}, "
          f"invalid clicks={m2.invalid_clicks}, raw={raw}, "
          f"invalid rate={100*m2.invalid_clicks/raw if raw else 0:.2f}%, "
          f"cost=${m2.cost_micros/1e6:,.2f}")
    out["account_total"] = {"impressions": m2.impressions, "clicks": m2.clicks,
                            "invalid_clicks": m2.invalid_clicks, "raw_clicks": raw,
                            "invalid_pct": round(100*m2.invalid_clicks/raw, 2) if raw else 0,
                            "cost": round(m2.cost_micros/1e6, 2)}

print("\n=== H. WHAT THE NUMBERS DO AND DO NOT PROVE ===")
print("  metrics.invalid_clicks counts clicks GOOGLE detected as invalid and filtered before")
print("  billing. Those clicks are already excluded from metrics.clicks and metrics.cost_micros,")
print("  so this is NOT unbilled spend and NOT a refund owed.")
print()
print("  It does NOT measure ClickCease. ClickCease works by adding IP exclusions, which")
print("  PREVENT an ad from being shown to a blocked IP - a prevented impression never becomes")
print("  a click and therefore never appears in either clicks or invalid_clicks. Google's")
print("  invalid-click count and ClickCease's blocked count are different populations measured")
print("  by different systems. Attributing one to the other is not supported by anything in")
print("  the Google Ads API.")
print()
ipb = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion "
               "WHERE campaign_criterion.type = 'IP_BLOCK'"))
ip5 = len(q(c, f"SELECT campaign_criterion.criterion_id FROM campaign_criterion "
               f"WHERE campaign_criterion.type = 'IP_BLOCK' AND campaign.id IN ({IN5})"))
print(f"  IP_BLOCK criteria in the account: {ipb}")
print(f"  IP_BLOCK criteria on the FIVE live campaigns: {ip5}")
out["ip_blocks"] = {"account": ipb, "on_the_five": ip5}
if ip5 == 0:
    print("  -> ClickCease's 2,796 IP exclusions sit on the 18 LEGACY campaigns and NONE of them")
    print("     is attached to the five live campaigns. Whatever is driving the invalid-click")
    print("     counts on the five, ClickCease IP blocking is demonstrably not filtering them.")

print("\n=== I. INDEPENDENT CLICKCEASE EVIDENCE ===")
print("  Required to attribute anything to ClickCease: the ClickCease dashboard's own blocked-")
print("  click report for 2401959466 over the same settled window. That is outside the Google")
print("  Ads API and was NOT available in this run. No ClickCease attribution is claimed.")
out["clickcease_attribution"] = "NOT CLAIMED - no independent ClickCease evidence available"

write(EVID / "2026-09-09c-invalid-click-audit.json", out)
