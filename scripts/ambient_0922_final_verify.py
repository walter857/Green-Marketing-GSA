#!/usr/bin/env python3
"""Ambient | 2026-09-22 | Final post-cutover verification + change_event audit.

READ-ONLY. EXTERNAL WRITES: 0.

Distinguishes ENABLED AND ELIGIBLE from ALREADY RECEIVING IMPRESSIONS, which are not the
same thing and must never be reported as if they were.
"""
from __future__ import annotations
import sys, json, datetime, calendar
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-22"
LIVE = ROOT / "receipts" / "live"
CAP_MONTH, WORKING = 10000.00, 325.00

c = client()
identity_gate(c, verbose=False)
build = json.loads((PLANS / "AMB-0922-BUILD-1.json").read_text(encoding="utf-8"))
AG = build["ad_groups"]
CAMPAIGNS = build["campaigns"]
made = json.loads((LIVE / f"AMB-0922-TRANSITION-{STAMP}-A.json").read_text(
    encoding="utf-8"))["committed"]
out = {"when": datetime.datetime.now(TZ).isoformat(), "read_only": True, "FAIL": 0,
       "assertions": []}


def check(label, ok, detail=""):
    out["assertions"].append({"check": label, "pass": bool(ok),
                              "detail": str(detail)[:300]})
    if not ok:
        out["FAIL"] += 1
        print(f"   FAIL {label}: {detail}")


ALL_C = {k: (v["reuse"] or made["campaigns"].get(k)) for k, v in CAMPAIGNS.items()}

print("=== ALL ENABLED CAMPAIGNS IN THE ACCOUNT ===")
enabled, tot = {}, 0.0
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                 campaign.primary_status, campaign.primary_status_reasons,
                 campaign.target_spend.cpc_bid_ceiling_micros,
                 campaign_budget.amount_micros
                 FROM campaign WHERE campaign.status = 'ENABLED'"""):
    d = r.campaign_budget.amount_micros / 1e6
    tot += d
    enabled[str(r.campaign.id)] = {
        "name": r.campaign.name, "daily": round(d, 2),
        "ceiling": round(r.campaign.target_spend.cpc_bid_ceiling_micros / 1e6, 2),
        "primary_status": E(r.campaign.primary_status),
        "reasons": [E(x) for x in r.campaign.primary_status_reasons]}
for k, v in sorted(enabled.items(), key=lambda x: -x[1]["daily"]):
    print(f"   {k}  ${v['daily']:7.2f} ceil ${v['ceiling']:6.2f} "
          f"{v['primary_status']:16s} {v['name'][:48]}")
    if v["reasons"]:
        print(f"        reasons: {v['reasons']}")
out["enabled_campaigns"] = enabled
out["enabled_daily_total"] = round(tot, 2)
print(f"\n   ENABLED DAILY TOTAL ${tot:.2f}   cap ${WORKING}")
check("enabled total <= 325", tot <= WORKING, tot)
check("monthly equivalent <= 10000", tot * 30.4 <= CAP_MONTH, round(tot * 30.4, 2))

print("\n=== RESIDENTIAL COOLING MUST BE OFF ===")
cool = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status,
                 campaign_budget.amount_micros FROM campaign
                 WHERE campaign.id IN (24132507741,24132507750,24132507747,24132507753)"""):
    cool[str(r.campaign.id)] = {"status": E(r.campaign.status), "name": r.campaign.name,
                                "daily": round(r.campaign_budget.amount_micros / 1e6, 2)}
for k, v in cool.items():
    print(f"   {k} {v['status']:8s} ${v['daily']:7.2f}  {v['name'][:50]}")
for k in ("24132507741", "24132507750", "24132507753"):
    check(f"cooling {k} PAUSED", cool[k]["status"] == "PAUSED", cool[k]["status"])
check("HVAC Installation campaign still ENABLED for Commercial",
      cool["24132507747"]["status"] == "ENABLED", cool["24132507747"]["status"])
ags747 = {}
for r in q(c, """SELECT ad_group.id, ad_group.name, ad_group.status FROM ad_group
                 WHERE campaign.id = 24132507747 AND ad_group.status != 'REMOVED'"""):
    ags747[str(r.ad_group.id)] = (r.ad_group.name, E(r.ad_group.status))
print(f"   24132507747 ad groups: {ags747}")
check("residential HVAC Installation ad group PAUSED",
      ags747.get("202339087634", ("", ""))[1] == "PAUSED", ags747.get("202339087634"))
check("Commercial HVAC Installation ad group still ENABLED",
      ags747.get("199748801029", ("", ""))[1] == "ENABLED", ags747.get("199748801029"))

print("\n=== HEATING AD GROUPS: STATUS, POLICY, SERVING ===")
agids = ",".join(made["ad_groups"].values())
agstat = {}
for r in q(c, f"""SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id,
                  campaign.status FROM ad_group WHERE ad_group.id IN ({agids})"""):
    agstat[str(r.ad_group.id)] = {"name": r.ad_group.name,
                                  "status": E(r.ad_group.status),
                                  "campaign_status": E(r.campaign.status)}
ads = {}
for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                  ad_group_ad.policy_summary.approval_status,
                  ad_group_ad.policy_summary.review_status,
                  ad_group_ad.ad.final_urls
                  FROM ad_group_ad WHERE ad_group.id IN ({agids})
                    AND ad_group_ad.status != 'REMOVED'"""):
    ads.setdefault(str(r.ad_group.id), []).append(
        {"id": str(r.ad_group_ad.ad.id), "status": E(r.ad_group_ad.status),
         "approval": E(r.ad_group_ad.policy_summary.approval_status),
         "review": E(r.ad_group_ad.policy_summary.review_status),
         "url": (list(r.ad_group_ad.ad.final_urls) or [""])[0]})
kwstat = {}
for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.status,
                  ad_group_criterion.approval_status,
                  ad_group_criterion.system_serving_status
                  FROM ad_group_criterion WHERE ad_group.id IN ({agids})
                    AND ad_group_criterion.type='KEYWORD'
                    AND ad_group_criterion.negative=FALSE
                    AND ad_group_criterion.status != 'REMOVED'"""):
    d = kwstat.setdefault(str(r.ad_group.id), {"enabled": 0, "eligible": 0, "total": 0})
    d["total"] += 1
    if E(r.ad_group_criterion.status) == "ENABLED":
        d["enabled"] += 1
    if E(r.ad_group_criterion.system_serving_status) == "ELIGIBLE":
        d["eligible"] += 1

rows = []
print(f"{'ad group':40s} {'verdict':12s} {'AG':8s} {'kw en/elig':11s} "
      f"{'ads':16s} url")
for n, agid in made["ad_groups"].items():
    d = AG[n]
    a = ads.get(agid, [])
    k = kwstat.get(agid, {"enabled": 0, "eligible": 0, "total": 0})
    en_ads = [x for x in a if x["status"] == "ENABLED"]
    appr = [x for x in en_ads if x["approval"] in ("APPROVED", "APPROVED_LIMITED")]
    under = [x for x in en_ads if x["review"] in ("REVIEW_IN_PROGRESS", "UNDER_REVIEW")]
    st = agstat.get(agid, {})
    can_serve = (st.get("status") == "ENABLED"
                 and st.get("campaign_status") == "ENABLED"
                 and len(appr) > 0 and k["eligible"] > 0)
    rows.append({"ad_group": n, "ad_group_id": agid, "verdict": d["verdict"][:24],
                 "ad_group_status": st.get("status"),
                 "campaign_status": st.get("campaign_status"),
                 "keywords_enabled": k["enabled"], "keywords_eligible": k["eligible"],
                 "ads_total": len(a), "ads_enabled": len(en_ads),
                 "ads_approved": len(appr), "ads_under_review": len(under),
                 "final_url": d["url"], "can_serve": can_serve,
                 "launch_gate": d["launch_gate"]})
    print(f"{n[:40]:40s} {d['verdict'][:12]:12s} {str(st.get('status'))[:8]:8s} "
          f"{k['enabled']:3d}/{k['eligible']:<7d} "
          f"{len(en_ads)}en {len(appr)}appr {len(under)}rev   "
          f"{'CAN SERVE' if can_serve else '-'}")
out["ad_groups"] = rows

ready = [r for r in rows if AG[r["ad_group"]]["verdict"] == "READY"]
held = [r for r in rows if AG[r["ad_group"]]["verdict"] != "READY"]
for r in ready:
    check(f"READY enabled {r['ad_group']}", r["ad_group_status"] == "ENABLED",
          r["ad_group_status"])
for r in held:
    check(f"HELD not enabled {r['ad_group']}", r["ad_group_status"] == "PAUSED",
          r["ad_group_status"])
    check(f"HELD has no enabled ad {r['ad_group']}", r["ads_enabled"] == 0,
          r["ads_enabled"])
out["can_serve_count"] = sum(1 for r in rows if r["can_serve"])
out["under_review_ads"] = sum(r["ads_under_review"] for r in rows)
print(f"\n   ad groups that CAN SERVE now: {out['can_serve_count']}")
print(f"   ads still UNDER REVIEW: {out['under_review_ads']}")

print("\n=== SEPTEMBER SPEND ===")
now = datetime.datetime.now(TZ)
first = now.replace(day=1).strftime("%Y-%m-%d")
today = now.strftime("%Y-%m-%d")
mtd = 0.0
for r in q(c, f"""SELECT campaign.id, metrics.cost_micros FROM campaign
                  WHERE segments.date BETWEEN '{first}' AND '{today}'"""):
    mtd += r.metrics.cost_micros / 1e6
dim = calendar.monthrange(now.year, now.month)[1]
left = dim - now.day + 1
proj = round(mtd + tot * left, 2)
print(f"   MTD ${mtd:,.2f}   days left incl today {left}")
print(f"   remaining allowance ${CAP_MONTH - mtd:,.2f}")
print(f"   worst case if every enabled budget spends in full: ${proj:,.2f}")
print(f"   + 10% overdelivery reserve: ${proj + (CAP_MONTH-mtd)*0.10:,.2f}")
out["september"] = {"mtd": round(mtd, 2), "days_left": left,
                    "remaining_allowance": round(CAP_MONTH - mtd, 2),
                    "projection_worst_case": proj,
                    "projection_plus_reserve": round(proj + (CAP_MONTH - mtd) * 0.10, 2),
                    "under_cap": proj + (CAP_MONTH - mtd) * 0.10 <= CAP_MONTH}
check("September projection under cap", out["september"]["under_cap"], proj)

print("\n=== CHANGE_EVENT AUDIT (last 2 days) ===")
lo = (now - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
hi = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
ce = {}
try:
    for r in q(c, f"""SELECT change_event.change_date_time, change_event.user_email,
                      change_event.client_type, change_event.change_resource_type,
                      change_event.resource_change_operation
                      FROM change_event
                      WHERE change_event.change_date_time >= '{lo}'
                        AND change_event.change_date_time <= '{hi}'
                      ORDER BY change_event.change_date_time DESC
                      LIMIT 9000"""):
        k = (E(r.change_event.change_resource_type),
             E(r.change_event.resource_change_operation),
             E(r.change_event.client_type))
        ce[str(k)] = ce.get(str(k), 0) + 1
except Exception as ex:
    ce = {"error": str(ex)[:200]}
for k, v in sorted(ce.items(), key=lambda x: -x[1] if isinstance(x[1], int) else 0):
    print(f"   {v:5} {k}")
out["change_events"] = ce

print(f"\n=== FINAL: {len(out['assertions'])} assertions, {out['FAIL']} FAIL ===")
p = LIVE / f"AMB-0922-FINAL-{STAMP}.json"
p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"WROTE {p}")
print("EXTERNAL WRITES: 0")
