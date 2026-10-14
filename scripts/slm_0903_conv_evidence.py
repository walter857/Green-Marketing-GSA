#!/usr/bin/env python3
"""Event-level evidence for the CONV-1 duplicate-conversion question.

SELECT-only. The QA gate forbids demoting an action merely because two actions
COULD record the same form. This script gathers the strongest evidence the API
can give without submitting a live lead:

  1. day-level firing pattern per conversion action (co-occurrence)
  2. conversion-time-to-click lag, which separates a same-event duplicate from
     two genuinely different lead actions
  3. every attribute that governs counting, plus tag/goal dependencies

Writes 17-conv-evidence.json
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "2429758629"
TZ = ZoneInfo("America/New_York")
B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"

# The two actions CONV-1 proposes to demote, and their claimed twins.
PAIRS = {
    "form": {"demote": "7461619140", "keep": "7480764700",
             "third": "7635680357"},
    "call": {"demote": "7508686781", "keep": "7461572537",
             "third": "7635680543"},
}


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    now = datetime.now(TZ)
    out = {"read_at": now.isoformat(), "customer_id": CID}
    errs = []

    def q(name, query):
        try:
            r = list(svc.search(customer_id=CID, query=query))
            print("  ok  %-34s %4d" % (name, len(r)))
            return r
        except Exception as exc:  # noqa: BLE001
            m = str(exc)
            for k in ("message: ", "FaultMessage: "):
                if k in m:
                    m = m.split(k, 1)[1][:300]
                    break
            errs.append({"q": name, "e": m[:300]})
            print("  !!  %-34s %s" % (name, m[:130]), file=sys.stderr)
            return []

    # ---- 1. full attribute sheet, including enhanced-conversion status ----
    out["actions"] = {str(x.conversion_action.id): {
        "name": x.conversion_action.name,
        "status": enum_name(x.conversion_action.status),
        "type": enum_name(x.conversion_action.type_),
        "category": enum_name(x.conversion_action.category),
        "origin": enum_name(x.conversion_action.origin),
        "primary_for_goal": x.conversion_action.primary_for_goal,
        "include_in_conversions_metric":
            x.conversion_action.include_in_conversions_metric,
        "counting_type": enum_name(x.conversion_action.counting_type),
        "click_through_lookback_days":
            x.conversion_action.click_through_lookback_window_days,
        "view_through_lookback_days":
            x.conversion_action.view_through_lookback_window_days,
        "attribution_model":
            enum_name(x.conversion_action.attribution_model_settings.attribution_model),
        "data_driven_status": enum_name(
            x.conversion_action.attribution_model_settings.data_driven_model_status),
        "phone_call_duration_seconds":
            x.conversion_action.phone_call_duration_seconds or None,
        "default_value": x.conversion_action.value_settings.default_value,
        "always_use_default_value":
            x.conversion_action.value_settings.always_use_default_value,
        "owner_customer": x.conversion_action.owner_customer or None,
        "app_id": x.conversion_action.app_id or None,
    } for x in q("conversion_action", """
        SELECT conversion_action.id, conversion_action.name, conversion_action.status,
               conversion_action.type, conversion_action.category,
               conversion_action.origin, conversion_action.primary_for_goal,
               conversion_action.include_in_conversions_metric,
               conversion_action.counting_type,
               conversion_action.click_through_lookback_window_days,
               conversion_action.view_through_lookback_window_days,
               conversion_action.attribution_model_settings.attribution_model,
               conversion_action.attribution_model_settings.data_driven_model_status,
               conversion_action.phone_call_duration_seconds,
               conversion_action.value_settings.default_value,
               conversion_action.value_settings.always_use_default_value,
               conversion_action.owner_customer, conversion_action.app_id
        FROM conversion_action WHERE conversion_action.status != 'REMOVED'""")}

    # ---- 2. DAY-level firing per action, per campaign ----
    daily = defaultdict(lambda: defaultdict(float))
    daily_all = defaultdict(lambda: defaultdict(float))
    rows = q("daily_by_action", """
        SELECT segments.date, segments.conversion_action,
               segments.conversion_action_name, campaign.id, campaign.name,
               metrics.conversions, metrics.all_conversions
        FROM campaign WHERE segments.date BETWEEN '2026-01-01' AND '%s'
        ORDER BY segments.date""" % now.date())
    detail = []
    for r in rows:
        aid = r.segments.conversion_action.split("/")[-1]
        daily[r.segments.date][aid] += r.metrics.conversions
        daily_all[r.segments.date][aid] += r.metrics.all_conversions
        detail.append({"date": r.segments.date, "action_id": aid,
                       "action": r.segments.conversion_action_name,
                       "campaign_id": str(r.campaign.id),
                       "campaign": r.campaign.name,
                       "conversions": round(r.metrics.conversions, 3),
                       "all_conversions": round(r.metrics.all_conversions, 3)})
    out["daily_detail"] = detail

    # ---- 3. co-occurrence test for each claimed duplicate pair ----
    out["co_occurrence"] = {}
    for label, ids in PAIRS.items():
        a, b_, c = ids["demote"], ids["keep"], ids["third"]
        both, only_a, only_b, days_a, days_b, days_c = [], [], [], 0, 0, 0
        for day, m in sorted(daily_all.items()):
            va, vb, vc = m.get(a, 0.0), m.get(b_, 0.0), m.get(c, 0.0)
            if va:
                days_a += 1
            if vb:
                days_b += 1
            if vc:
                days_c += 1
            if va and vb:
                both.append({"date": day, "demote_candidate": round(va, 2),
                             "keep_candidate": round(vb, 2),
                             "third_action": round(vc, 2)})
            elif va and not vb:
                only_a.append({"date": day, "demote_candidate": round(va, 2)})
            elif vb and not va:
                only_b.append({"date": day, "keep_candidate": round(vb, 2)})
        out["co_occurrence"][label] = {
            "demote_candidate_id": a, "keep_candidate_id": b_, "third_action_id": c,
            "days_demote_fired": days_a, "days_keep_fired": days_b,
            "days_third_fired": days_c,
            "days_both_fired": len(both),
            "days_only_demote": len(only_a), "days_only_keep": len(only_b),
            "same_day_matches": both,
            "days_only_demote_detail": only_a,
            "days_only_keep_detail": only_b,
            "same_day_equal_counts": sum(
                1 for x in both
                if abs(x["demote_candidate"] - x["keep_candidate"]) < 0.001),
        }

    # ---- 4. conversion lag: same event or different events? ----
    out["conversion_lag"] = [{
        "action": r.segments.conversion_action_name,
        "action_id": r.segments.conversion_action.split("/")[-1],
        "lag_bucket": enum_name(r.segments.conversion_lag_bucket),
        "all_conversions": round(r.metrics.all_conversions, 3),
    } for r in q("conversion_lag", """
        SELECT segments.conversion_action, segments.conversion_action_name,
               segments.conversion_lag_bucket, metrics.all_conversions
        FROM campaign WHERE segments.date BETWEEN '2026-01-01' AND '%s'"""
                 % now.date())]

    # ---- 5. goal dependency: which goal does each action feed? ----
    out["customer_goals"] = [{
        "category": enum_name(x.customer_conversion_goal.category),
        "origin": enum_name(x.customer_conversion_goal.origin),
        "biddable": x.customer_conversion_goal.biddable,
    } for x in q("customer_conversion_goal", """
        SELECT customer_conversion_goal.category, customer_conversion_goal.origin,
               customer_conversion_goal.biddable FROM customer_conversion_goal""")]

    out["errors"] = errs
    (B / "17-conv-evidence.json").write_text(
        json.dumps(out, indent=2, default=str), encoding="utf-8")

    print("\n" + "=" * 74)
    for label, r in out["co_occurrence"].items():
        print("%s PAIR  demote=%s keep=%s third=%s"
              % (label.upper(), r["demote_candidate_id"], r["keep_candidate_id"],
                 r["third_action_id"]))
        print("  days demote fired=%d  days keep fired=%d  days third fired=%d"
              % (r["days_demote_fired"], r["days_keep_fired"], r["days_third_fired"]))
        print("  days BOTH fired=%d   only demote=%d   only keep=%d"
              % (r["days_both_fired"], r["days_only_demote"], r["days_only_keep"]))
        print("  same-day EQUAL counts=%d of %d overlapping days"
              % (r["same_day_equal_counts"], r["days_both_fired"]))
        for x in r["same_day_matches"][:12]:
            print("     %s  demote=%.1f keep=%.1f third=%.1f"
                  % (x["date"], x["demote_candidate"], x["keep_candidate"],
                     x["third_action"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
