#!/usr/bin/env python3
"""MasterGrass - Live | MG-0927-SEPT-PACE | land September 2026 spend at $1,500.00.

Owner instruction 2026-09-27: "September needs to finish with 1500 so make the math and make sure
spending is perfect to achieve this."

Mechanics (Google Ads):
  * a campaign can spend up to 2x its daily budget on one day;
  * after a mid-month budget change its remaining-month charges are limited to about
    new daily budget x days left in the month (including today) - so on Sep 30 each campaign can
    spend at most its budget, which is what makes the last day precise.

Rules (fingerprinted; every run logs its numbers):
  need          = 1500.00 - September spend to date (all campaigns, account time zone)
  D             = calendar days left including today (serving every day while the push runs)
  e_L, e_H      = expected spend per day for Landscaping / Hardscaping: average of completed push days,
                  else priors $70 (Landscaping, Max Clicks $25 cap, 14 h/day) and $5 (Hardscaping, starved)
  Landscaping   = e_L x 1.15 on Sep 27-29, exactly e_L on Sep 30; floor $28, ceiling $150
  Hardscaping   = $13 (owner-approved, unchanged)
  PMax          = (need - (min(B_L, e_L) + e_H) x D) / D; floor $20, ceiling $200
  Push schedule = all 3 campaigns every day 08:00-22:00 ET (7 a.m.-9 p.m. Central), Sep 27-30 only;
                  GBP lists the business as open 24 hours and forms work any time
  Reset (after 22:00 ET Sep 30, before 10:00 ET Oct 1) = Landscaping $28 / Hardscaping $13 / PMax $20 and
                  schedule back to Mon-Fri 10:00-18:00 ET on all 3 campaigns (the October $1,500 plan)
Worst-case overshoot on any morning run is bounded by the Landscaping 15% margin plus Hardscaping's unused
budget; the next run corrects it, and on Sep 30 the bound is Hardscaping's unused $13 only.

Modes: status | apply --fp CODE | reset --fp CODE
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

from google.protobuf import field_mask_pb2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import CID, EXACT_NAME, GM_MANAGER, ROOT, TZ, E, client, q  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

REC = ROOT / "clients" / "mastergrass-lawn-care" / "receipts"
LAND, HARD, PMAX = "23905193676", "23914692658", "24287457516"
BUDGET = {LAND: "15630863938", HARD: "15625559646", PMAX: "15899496440"}
NAME = {LAND: "Landscaping", HARD: "Hardscaping", PMAX: "PMax drainage"}
TARGET, END, START = 1500.00, datetime.date(2026, 9, 30), datetime.date(2026, 9, 27)
PUSH_SCHEDULE = [(d, 8, 22) for d in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY")]
BASE_SCHEDULE = [(d, 10, 18) for d in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY")]
RESET_BUDGETS = {LAND: 28.00, HARD: 13.00, PMAX: 20.00}
RULES = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": GM_MANAGER,
         "package": "MG-0927-SEPT-PACE", "target": TARGET, "window": [str(START), str(END)],
         "priors": {"landscaping": 70.0, "hardscaping": 5.0}, "landscaping_margin": 1.15,
         "floors": {LAND: 28.0, HARD: 13.0, PMAX: 20.0}, "ceilings": {LAND: 150.0, PMAX: 200.0},
         "hardscaping_budget": 13.0, "estimator": "completed push weekdays only, else priors (v2 2026-09-28)", "push_schedule": PUSH_SCHEDULE, "reset_budgets": RESET_BUDGETS,
         "reset_schedule": BASE_SCHEDULE, "campaigns": [LAND, HARD, PMAX], "budgets": BUDGET}
FP = approval_code(RULES)


def gate(c):
    row = q(c, "SELECT customer.id, customer.descriptive_name, customer.manager, customer.test_account FROM customer")[0].customer
    if str(row.id) != CID or row.descriptive_name != EXACT_NAME or row.manager or row.test_account:
        sys.exit("IDENTITY GATE FAIL")
    st = {str(r.campaign.id): (E(r.campaign.status), r.campaign_budget.id) for r in q(c, f"SELECT campaign.id, campaign.status, campaign_budget.id FROM campaign WHERE campaign.id IN ({LAND},{HARD},{PMAX})")}
    for cid in (LAND, HARD, PMAX):
        if st.get(cid, ("", 0))[0] != "ENABLED" or str(st[cid][1]) != BUDGET[cid]:
            sys.exit(f"ABORT: {NAME[cid]} state {st.get(cid)}")


def spend(c):
    mtd, by_day = 0.0, {}
    for r in q(c, "SELECT campaign.id, segments.date, metrics.cost_micros FROM campaign WHERE segments.date BETWEEN '2026-09-01' AND '2026-09-30' AND metrics.cost_micros > 0"):
        v = r.metrics.cost_micros / 1e6
        mtd += v
        if r.segments.date >= str(START):
            by_day.setdefault(str(r.campaign.id), {}).setdefault(r.segments.date, 0.0)
            by_day[str(r.campaign.id)][r.segments.date] += v
    return round(mtd, 2), by_day


def plan(c, now):
    today = now.date()
    mtd, by_day = spend(c)
    need = round(TARGET - mtd, 2)
    D = (END - today).days + 1
    # completed push WEEKDAYS only: a Sunday (0 clicks while the bid switch was learning) is not a weekday forecast
    done = [str(d) for d in (START + datetime.timedelta(days=i) for i in range((today - START).days)) if d.weekday() < 5]

    def avg(cid, prior):
        vals = [by_day.get(cid, {}).get(d, 0.0) for d in done]
        return round(sum(vals) / len(vals), 2) if vals else prior
    e_l, e_h = avg(LAND, RULES["priors"]["landscaping"]), avg(HARD, RULES["priors"]["hardscaping"])
    b_l = e_l if today == END else e_l * RULES["landscaping_margin"]
    b_l = round(min(max(b_l, RULES["floors"][LAND]), RULES["ceilings"][LAND]), 2)
    b_h = RULES["hardscaping_budget"]
    b_p = round(min(max((need - (min(b_l, e_l) + e_h) * D) / D, RULES["floors"][PMAX]), RULES["ceilings"][PMAX]), 2)
    exp_total = round(mtd + (min(b_l, e_l) + e_h + b_p) * D, 2)
    max_total = round(mtd + (b_l + b_h + b_p) * D, 2)  # month-end ceiling implied by rest-of-month limits
    return {"now": now.isoformat(timespec="minutes"), "mtd": mtd, "need": need, "days_left": D, "e_landscaping": e_l,
            "e_hardscaping": e_h, "budgets": {LAND: b_l, HARD: b_h, PMAX: b_p}, "expected_month_end": exp_total,
            "max_month_end": max_total,
            "push_days_spend": by_day}


def set_budgets(c, budgets):
    ops = []
    for cid, amt in budgets.items():
        o = c.get_type("CampaignBudgetOperation")
        o.update.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(CID, BUDGET[cid])
        o.update.amount_micros = int(round(amt, 2) * 1e6)
        o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["amount_micros"]))
        ops.append(o)
    c.get_service("CampaignBudgetService").mutate_campaign_budgets(customer_id=CID, operations=ops)


def current_schedule(c, cid):
    return {r.campaign_criterion.resource_name: (E(r.campaign_criterion.ad_schedule.day_of_week), r.campaign_criterion.ad_schedule.start_hour, r.campaign_criterion.ad_schedule.end_hour)
            for r in q(c, f"SELECT campaign.id, campaign_criterion.resource_name, campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.end_hour FROM campaign_criterion WHERE campaign.id = {cid} AND campaign_criterion.type = 'AD_SCHEDULE'")}


def set_schedule(c, target):
    changed = []
    for cid in (LAND, HARD, PMAX):
        cur = current_schedule(c, cid)
        if sorted(cur.values()) == sorted(target):
            continue
        ops = []
        for rn in cur:
            o = c.get_type("CampaignCriterionOperation")
            o.remove = rn
            ops.append(o)
        for day, s, e in target:
            o = c.get_type("CampaignCriterionOperation")
            cc = o.create
            cc.campaign = c.get_service("CampaignService").campaign_path(CID, cid)
            cc.ad_schedule.day_of_week = getattr(c.enums.DayOfWeekEnum, day)
            cc.ad_schedule.start_hour, cc.ad_schedule.end_hour = s, e
            cc.ad_schedule.start_minute = c.enums.MinuteOfHourEnum.ZERO
            cc.ad_schedule.end_minute = c.enums.MinuteOfHourEnum.ZERO
            ops.append(o)
        c.get_service("CampaignCriterionService").mutate_campaign_criteria(customer_id=CID, operations=ops)
        changed.append(NAME[cid])
    return changed


def readback(c):
    b = {str(r.campaign.id): r.campaign_budget.amount_micros / 1e6 for r in q(c, f"SELECT campaign.id, campaign_budget.amount_micros FROM campaign WHERE campaign.id IN ({LAND},{HARD},{PMAX})")}
    s = {cid: sorted(current_schedule(c, cid).values()) for cid in (LAND, HARD, PMAX)}
    return b, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["status", "apply", "reset"])
    ap.add_argument("--fp")
    a = ap.parse_args()
    c = client()
    gate(c)
    now = datetime.datetime.now(TZ)
    if a.mode != "status" and a.fp != FP:
        sys.exit(f"ABORT fingerprint {FP} != {a.fp}")
    if a.mode == "reset":
        set_budgets(c, RESET_BUDGETS)
        ch = set_schedule(c, BASE_SCHEDULE)
        b, s = readback(c)
        ok = b == {k: v for k, v in RESET_BUDGETS.items()} and all(v == sorted(BASE_SCHEDULE) for v in s.values())
        rec = {"package": "MG-0927-SEPT-PACE", "mode": "reset", "fingerprint": FP, "at": now.isoformat(), "budgets": b, "schedule_changed": ch, "readback_ok": ok}
        (REC / f"MG-0927-SEPT-PACE-reset-{now:%Y%m%dT%H%M}.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
        print(f"RESET {'PASS' if ok else 'FAIL'} budgets {b} schedule changed on {ch}")
        return
    p = plan(c, now)
    print(f"{p['now']} | Sept to date ${p['mtd']:,.2f} | need ${p['need']:,.2f} over {p['days_left']} day(s) | "
          f"e_L ${p['e_landscaping']} e_H ${p['e_hardscaping']}")
    for cid, v in p["budgets"].items():
        print(f"  {NAME[cid]:<14} budget ${v:,.2f}/day")
    print(f"  expected month end ${p['expected_month_end']:,.2f} | reachable max ${p['max_month_end']:,.2f}   (rules fingerprint {FP})")
    if p["max_month_end"] < TARGET:
        print("  WARNING: budgets cannot reach the target even at full delivery")
    if a.mode == "status":
        return
    if now.date() > END or now.date() < START:
        sys.exit("ABORT: outside the Sep 27-30 push window; use reset")
    set_budgets(c, p["budgets"])
    ch = set_schedule(c, PUSH_SCHEDULE)
    b, s = readback(c)
    ok = all(abs(b[k] - v) < 0.005 for k, v in p["budgets"].items()) and all(v == sorted(PUSH_SCHEDULE) for v in s.values())
    rec = dict(p, package="MG-0927-SEPT-PACE", mode="apply", fingerprint=FP, schedule_changed=ch, readback=b, readback_ok=ok)
    (REC / f"MG-0927-SEPT-PACE-apply-{now:%Y%m%dT%H%M}.json").write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print(f"APPLY readback {'PASS' if ok else 'FAIL'} budgets {b} | schedule changed on {ch or 'none (already set)'}")


if __name__ == "__main__":
    main()
