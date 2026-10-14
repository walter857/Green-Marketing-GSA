#!/usr/bin/env python3
"""2026-09-09 CORRECTION RUN: identity gate, fresh live state, drift check against all six
plan files, and change history through the current timestamp with user_email attribution."""
from __future__ import annotations
import sys, json, datetime, hashlib
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

c = client()
out = {"run": "2026-09-09 CORRECTION", "started_local": datetime.datetime.now(TZ).isoformat()}

print("=== 1. SIX-FIELD IDENTITY GATE ===")
ident = identity_gate(c)
out["identity"] = ident
print(f"  descriptive_name    : {ident['descriptive_name']}")
print(f"  customer_id         : {ident['customer_id']}")
print(f"  time_zone           : {ident['time_zone']}")
print(f"  currency            : {ident['currency']}")
print(f"  manager             : {ident['manager']}  (must be False)")
print(f"  test_account        : {ident['test_account']}  (must be False)")
print(f"  manager links       : {ident['manager_links']}")

print("\n=== 2. ACCOUNT-LOCAL CLOCK (authoritative, from the API) ===")
rows = q(c, "SELECT segments.date, metrics.impressions, metrics.cost_micros "
            "FROM customer WHERE segments.date DURING TODAY")
if rows:
    print(f"  segments.date DURING TODAY -> {rows[0].segments.date} "
          f"impr={rows[0].metrics.impressions} cost=${rows[0].metrics.cost_micros/1e6:.2f}")
    out["account_today"] = rows[0].segments.date
else:
    print("  segments.date DURING TODAY -> no rows (zero impressions AND zero cost today)")
    out["account_today"] = None
y = q(c, "SELECT segments.date, metrics.impressions, metrics.clicks, metrics.cost_micros "
         "FROM customer WHERE segments.date DURING YESTERDAY")
if y:
    print(f"  segments.date DURING YESTERDAY -> {y[0].segments.date} "
          f"impr={y[0].metrics.impressions} clicks={y[0].metrics.clicks} "
          f"cost=${y[0].metrics.cost_micros/1e6:.2f}")
    out["account_yesterday"] = y[0].segments.date

print("\n=== 3. FRESH LIVE STATE OF EVERY PLAN'S BEFORE-STATE ===")
live = {}
camps = {}
for r in q(c, f"""
    SELECT campaign.id, campaign.name, campaign.status, campaign.bidding_strategy_type,
           campaign.target_spend.cpc_bid_ceiling_micros, campaign.campaign_budget,
           campaign.serving_status
    FROM campaign WHERE campaign.id IN ({IN5})
"""):
    x = r.campaign
    camps[str(x.id)] = {"name": x.name, "status": E(x.status), "bidding": E(x.bidding_strategy_type),
                        "ceiling_micros": x.target_spend.cpc_bid_ceiling_micros,
                        "budget": x.campaign_budget.split("/")[-1],
                        "serving": E(x.serving_status)}
live["campaigns"] = camps
for cid in FIVE:
    x = camps[cid]
    print(f"  {NAME[cid]:<20} {x['status']:<8} {x['bidding']:<14} "
          f"ceiling=${x['ceiling_micros']/1e6:>7.2f} budget={x['budget']}")

buds = {}
for r in q(c, "SELECT campaign_budget.id, campaign_budget.amount_micros, "
              "campaign_budget.status, campaign_budget.reference_count, "
              "campaign_budget.delivery_method, campaign_budget.explicitly_shared "
              "FROM campaign_budget WHERE campaign_budget.status = 'ENABLED'"):
    x = r.campaign_budget
    buds[str(x.id)] = {"amount_micros": x.amount_micros, "daily": round(x.amount_micros/1e6, 2),
                       "refs": x.reference_count, "delivery": E(x.delivery_method),
                       "shared": x.explicitly_shared}
live["budgets"] = {b: buds.get(b) for b in
                   ["15787409435", "15787409438", "15787409441", "15787409444", "15787409447"]}
print()
tot = 0.0
for b, v in live["budgets"].items():
    tot += v["daily"]
    print(f"  budget {b}  ${v['daily']:>8.2f}/day  refs={v['refs']}  {v['delivery']}")
print(f"  TOTAL DAILY = ${tot:.2f}")
live["daily_total"] = round(tot, 2)

negs = []
for r in q(c, f"""
    SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.keyword.text,
           campaign_criterion.keyword.match_type, campaign_criterion.status
    FROM campaign_criterion
    WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'KEYWORD'
      AND campaign_criterion.negative = TRUE AND campaign_criterion.status = 'ENABLED'
"""):
    x = r.campaign_criterion
    negs.append({"camp": str(r.campaign.id), "crit": str(x.criterion_id),
                 "text": x.keyword.text, "match": E(x.keyword.match_type)})
live["campaign_negatives"] = negs
print(f"\n  ENABLED campaign negatives on the five: {len(negs)}")
print(f"    {dict(Counter(NAME[n['camp']] for n in negs))}")

acct = []
for r in q(c, "SELECT shared_criterion.resource_name, shared_criterion.criterion_id, "
              "shared_criterion.keyword.text, shared_criterion.keyword.match_type "
              "FROM shared_criterion WHERE shared_set.id = 11252984411"):
    x = r.shared_criterion
    acct.append({"rn": x.resource_name, "crit": str(x.criterion_id), "text": x.keyword.text,
                 "match": E(x.keyword.match_type)})
live["account_level"] = acct
print(f"  account-level set 11252984411 members: {len(acct)}")

ads = []
for r in q(c, f"""
    SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
           ad_group_ad.policy_summary.approval_status,
           ad_group_ad.policy_summary.review_status, ad_group_ad.ad_strength,
           ad_group_ad.ad.final_urls
    FROM ad_group_ad WHERE campaign.id IN ({IN5})
"""):
    x = r.ad_group_ad
    ads.append({"camp": str(r.campaign.id), "ag": str(r.ad_group.id), "ad": str(x.ad.id),
                "status": E(x.status), "approval": E(x.policy_summary.approval_status),
                "review": E(x.policy_summary.review_status), "strength": E(x.ad_strength),
                "final_urls": list(x.ad.final_urls)})
live["ads"] = ads
print(f"  ad rows on the five: {len(ads)}  {dict(Counter(a['status'] for a in ads))}")

out["live"] = live

print("\n=== 4. DRIFT CHECK AGAINST ALL SIX PLAN FILES ===")
drift = {}
plans = {}
for p in sorted((CLIENT_DIR / "plans").glob("AMB-0909-*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    plans[d["plan_name"]] = d
    rec = approval_code({"target": d["target"], "plan": d["plan_name"],
                         "operations": d["operations"]})
    fp_ok = rec == d["fingerprint"]
    drift[d["plan_name"]] = {"file": str(p.relative_to(ROOT)), "fingerprint": d["fingerprint"],
                             "fingerprint_recomputes": fp_ok, "ops": d["object_count"],
                             "class": d["approval_class"], "before_state_ok": None,
                             "executed": None, "notes": []}
    print(f"\n  {d['plan_name']:<20} fp={d['fingerprint']}  ops={d['object_count']:<4} "
          f"recompute={'OK' if fp_ok else 'MISMATCH'}")

negkey = {(n["camp"], n["crit"]): n for n in negs}
acctkey = {a["rn"]: a for a in acct}
adkey = {(a["ag"], a["ad"]): a for a in ads}

# CPC-1
p = plans["AMB-0909-CPC-1"]
bad = []
for a in p["operations"]:
    cur = camps[a["resource_id"]]["ceiling_micros"]
    stated = int(a["current_state"].split("= ")[1].split(" ")[0])
    if cur != stated:
        bad.append(f"{NAME[a['resource_id']]}: plan says {stated}, live is {cur}")
drift["AMB-0909-CPC-1"]["before_state_ok"] = not bad
drift["AMB-0909-CPC-1"]["notes"] = bad
drift["AMB-0909-CPC-1"]["executed"] = False
print(f"  CPC-1 before-state: {'UNCHANGED' if not bad else bad}")

# BUD-1
p = plans["AMB-0909-BUD-1"]
bad = []
for a in p["operations"]:
    cur = buds[a["resource_id"]]["amount_micros"]
    stated = int(a["current_state"].split("= ")[1].split(" ")[0])
    if cur != stated:
        bad.append(f"budget {a['resource_id']}: plan says {stated}, live is {cur}")
drift["AMB-0909-BUD-1"]["before_state_ok"] = not bad
drift["AMB-0909-BUD-1"]["notes"] = bad
drift["AMB-0909-BUD-1"]["executed"] = False
print(f"  BUD-1 before-state: {'UNCHANGED' if not bad else bad}")

# NEG-RM-1
p = plans["AMB-0909-NEG-RM-1"]
missing = [a for a in p["operations"] if (a["campaign_id"], a["criterion_id"]) not in negkey]
drift["AMB-0909-NEG-RM-1"]["before_state_ok"] = not missing
drift["AMB-0909-NEG-RM-1"]["notes"] = [f"{len(missing)} targets no longer live"] if missing else []
drift["AMB-0909-NEG-RM-1"]["executed"] = bool(missing)
print(f"  NEG-RM-1 before-state: {len(p['operations'])-len(missing)}/{len(p['operations'])} "
      f"targets still live ENABLED -> {'UNCHANGED' if not missing else 'DRIFT'}")

# NEG-RM-2
p = plans["AMB-0909-NEG-RM-2"]
missing = [a for a in p["operations"] if a["shared_criterion_resource_name"] not in acctkey]
drift["AMB-0909-NEG-RM-2"]["before_state_ok"] = not missing
drift["AMB-0909-NEG-RM-2"]["notes"] = [f"{len(missing)} members no longer present"] if missing else []
drift["AMB-0909-NEG-RM-2"]["executed"] = bool(missing)
print(f"  NEG-RM-2 before-state: {len(p['operations'])-len(missing)}/{len(p['operations'])} "
      f"members still present -> {'UNCHANGED' if not missing else 'DRIFT'}")

# ADS-1
p = plans["AMB-0909-ADS-1"]
bad = []
for a in p["operations"]:
    k = (a["ad_group_id"], a["ad_id"])
    x = adkey.get(k)
    if not x:
        bad.append(f"ad {a['ad_id']} missing")
    elif x["status"] != "ENABLED" or x["approval"] != "DISAPPROVED":
        bad.append(f"ad {a['ad_id']} now {x['status']}/{x['approval']}")
drift["AMB-0909-ADS-1"]["before_state_ok"] = not bad
drift["AMB-0909-ADS-1"]["notes"] = bad
drift["AMB-0909-ADS-1"]["executed"] = bool(bad)
print(f"  ADS-1 before-state: {'UNCHANGED' if not bad else bad}")

# NEG-ADD-1
p = plans["AMB-0909-NEG-ADD-1"]
import re, unicodedata
def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()
present = {(n["camp"], n["match"], norm(n["text"])) for n in negs}
already = [a for a in p["operations"]
           if (a["campaign_id"], a["match_type"], norm(a["negative_text"])) in present]
drift["AMB-0909-NEG-ADD-1"]["before_state_ok"] = not already
drift["AMB-0909-NEG-ADD-1"]["notes"] = [f"{len(already)} already present"] if already else []
drift["AMB-0909-NEG-ADD-1"]["executed"] = bool(already)
print(f"  NEG-ADD-1 before-state: {len(already)}/{len(p['operations'])} already present -> "
      f"{'UNCHANGED (none created)' if not already else 'DRIFT'}")

out["drift"] = drift

print("\n=== 5. VALIDATE-ONLY RECEIPTS ON DISK ===")
rec = {}
for f in sorted((ROOT / "receipts" / "validate-only").glob("AMB-0909-*2026-09-09.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    rec[d["plan_name"]] = {"fingerprint": d["fingerprint"], "status": d["status"],
                           "validate_only": d["validate_only"], "ops": d["operation_count"],
                           "partial_failure": d["partial_failure"],
                           "resource_names": d.get("resource_names")}
    print(f"  {d['plan_name']:<20} {d['fingerprint']}  {d['status']:<14} "
          f"validate_only={d['validate_only']}  ops={d['operation_count']}  "
          f"resource_names={'NONE (no write)' if not d.get('resource_names') else 'PRESENT'}")
out["validate_only_receipts"] = rec

print("\n=== 6. CHANGE HISTORY THROUGH NOW, WITH user_email ===")
ch = []
for r in q(c, """
    SELECT change_event.change_date_time, change_event.change_resource_type,
           change_event.change_resource_name, change_event.client_type,
           change_event.user_email, change_event.resource_change_operation,
           change_event.changed_fields, change_event.campaign, change_event.ad_group,
           change_event.new_resource, change_event.old_resource
    FROM change_event
    WHERE change_event.change_date_time >= '2026-08-11 00:00:00'
      AND change_event.change_date_time <= '2026-09-09 23:59:59'
    ORDER BY change_event.change_date_time DESC
    LIMIT 10000
"""):
    x = r.change_event
    ch.append({"ts": x.change_date_time, "type": E(x.change_resource_type),
               "rn": x.change_resource_name, "client_type": E(x.client_type),
               "user_email": x.user_email, "op": E(x.resource_change_operation),
               "fields": list(x.changed_fields.paths) if x.changed_fields else [],
               "campaign": x.campaign.split("/")[-1] if x.campaign else None,
               "new_ceiling": x.new_resource.campaign.target_spend.cpc_bid_ceiling_micros or None,
               "old_ceiling": x.old_resource.campaign.target_spend.cpc_bid_ceiling_micros or None,
               "new_budget": x.new_resource.campaign_budget.amount_micros or None,
               "old_budget": x.old_resource.campaign_budget.amount_micros or None})
out["change_events"] = ch
print(f"  rows: {len(ch)}   latest: {ch[0]['ts'] if ch else 'none'}")
print(f"  by client_type x user_email:")
for k, v in sorted(Counter((r["client_type"], r["user_email"]) for r in ch).items()):
    print(f"    {k[0]:<24} {k[1]:<44} n={v}")

print("\n  --- ALL CAMPAIGN-level and BUDGET-level changes on the five, with attribution ---")
for r in sorted([r for r in ch if r["type"] in ("CAMPAIGN", "CAMPAIGN_BUDGET")],
                key=lambda r: r["ts"]):
    lab = NAME.get(r["campaign"], r["campaign"])
    extra = ""
    if r["old_ceiling"] or r["new_ceiling"]:
        extra = f" ceiling {r['old_ceiling']}->{r['new_ceiling']}"
    if r["old_budget"] or r["new_budget"]:
        extra = f" budget ${(r['old_budget'] or 0)/1e6:.2f}->${(r['new_budget'] or 0)/1e6:.2f}"
    print(f"    {r['ts'][:19]}  {r['type']:<16} {str(lab):<18} {r['op']:<7} "
          f"{r['client_type']:<22} {r['user_email']:<40} {r['fields']}{extra}")

print("\n  --- ANY change after 2026-09-09 15:10 (the prior run's last read) ---")
after = [r for r in ch if r["ts"] > "2026-09-09 15:10:00"]
print(f"    count: {len(after)}")
for r in after:
    print(f"    {r['ts'][:19]}  {r['type']:<18} {NAME.get(r['campaign'], r['campaign'])} "
          f"{r['op']} {r['client_type']} {r['user_email']} {r['fields']}")
out["changes_after_prior_run"] = after

write(EVID / "2026-09-09b-state-and-drift.json", out)
