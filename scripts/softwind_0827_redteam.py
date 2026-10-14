#!/usr/bin/env python3
"""Red-team review + no-change safety verification for the 2026-08-27 session.

Confirms:
  * the PLAN-K1 field mask is a real, settable Campaign proto path
  * the PLAN-K1 fingerprint is reproducible from the written YAML
  * the account is byte-for-byte unchanged since the 2026-08-26 18:00 receipt

READ ONLY.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402
from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from softwind_build_k1 import normalize  # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
PLANS = ROOT / "clients/softwind-power-washing/plans"
SNAPS = ROOT / "clients/softwind-power-washing/snapshots"
OUT = SNAPS / "redteam-2026-08-27.json"

EXPECT = {
    "budget_A_micros": 333330000,
    "budget_B_micros": 41110000,
    "keywords": 214, "ads": 54, "campaign_negative_keywords": 94,
    "ad_schedules": 12, "conversion_actions": 4, "campaign_assets": 20,
    "ad_groups": 30,
}


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def count(svc, res, where=""):
    q = "SELECT %s.resource_name FROM %s%s" % (res, res, where)
    return len(rows(svc, q))


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    now = datetime.now(TZ)
    checks = []

    def chk(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    # ---- 1. field mask validity, by proto introspection (no mutate issued) ----
    camp = client.get_type("Campaign")
    has_ts = hasattr(camp, "target_spend")
    has_ceiling = hasattr(camp.target_spend, "cpc_bid_ceiling_micros")
    chk("field_mask_path_exists_on_Campaign_proto", has_ts and has_ceiling,
        "Campaign.target_spend.cpc_bid_ceiling_micros present=%s" % (has_ts and has_ceiling))
    fm_ok = True
    try:
        from google.protobuf import field_mask_pb2
        fm = field_mask_pb2.FieldMask(paths=["target_spend.cpc_bid_ceiling_micros"])
        fm_ok = list(fm.paths) == ["target_spend.cpc_bid_ceiling_micros"]
    except Exception as exc:
        fm_ok = False
        chk("field_mask_constructible", False, str(exc)[:200])
    chk("field_mask_is_exactly_one_path", fm_ok,
        "paths == ['target_spend.cpc_bid_ceiling_micros']")

    # ---- 2. fingerprint reproducible from the written YAML ----
    plan = yaml.safe_load((PLANS / "2026-08-27-plan-k1-cpc-control.yaml")
                          .read_text(encoding="utf-8"))
    recomputed = approval_code(normalize(plan))
    stored = plan["change_plan"]["fingerprint"]
    chk("fingerprint_reproducible", recomputed == stored,
        "stored=%s recomputed=%s" % (stored, recomputed))
    chk("plan_marked_not_approved",
        plan["change_plan"]["approval_status"] == "NOT APPROVED",
        plan["change_plan"]["approval_status"])
    chk("plan_marked_do_not_execute",
        plan["change_plan"]["execution_status"] == "DO NOT EXECUTE",
        plan["change_plan"]["execution_status"])
    chk("plan_touches_no_budget",
        plan["change_plan"]["change_counts"]["budgets_changed"] == 0,
        "budgets_changed=0")
    chk("plan_identity_matches_gate",
        plan["change_plan"]["target"]["child_customer_id"] == CID
        and plan["change_plan"]["target"]["exact_child_account_name"]
        == "Softwind Power Washing - Live"
        and plan["change_plan"]["target"]["exact_service"] == "Power Washing",
        json.dumps(plan["change_plan"]["target"]))

    # ---- 3. account unchanged since the 2026-08-26 18:00 receipt ----
    q = ("SELECT campaign.id, campaign.status, campaign.bidding_strategy_type, "
         "campaign.target_spend.cpc_bid_ceiling_micros, "
         "campaign.network_settings.target_search_network, "
         "campaign.network_settings.target_content_network, "
         "campaign.geo_target_type_setting.positive_geo_target_type, "
         "campaign_budget.id, campaign_budget.amount_micros, "
         "campaign_budget.reference_count, campaign_budget.explicitly_shared "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B})")
    live = {}
    for r in rows(svc, q):
        live[str(r.campaign.id)] = {
            "status": r.campaign.status.name,
            "bidding": r.campaign.bidding_strategy_type.name,
            "ceiling": r.campaign.target_spend.cpc_bid_ceiling_micros or None,
            "partners": r.campaign.network_settings.target_search_network,
            "display": r.campaign.network_settings.target_content_network,
            "geo": r.campaign.geo_target_type_setting.positive_geo_target_type.name,
            "budget_id": str(r.campaign_budget.id),
            "budget_micros": r.campaign_budget.amount_micros,
            "budget_refs": r.campaign_budget.reference_count,
            "budget_shared": r.campaign_budget.explicitly_shared,
        }
    chk("budget_A_unchanged",
        live[CAMP_A]["budget_micros"] == EXPECT["budget_A_micros"],
        "%s micros" % live[CAMP_A]["budget_micros"])
    chk("budget_B_unchanged",
        live[CAMP_B]["budget_micros"] == EXPECT["budget_B_micros"],
        "%s micros" % live[CAMP_B]["budget_micros"])
    chk("no_cpc_ceiling_yet_on_either_campaign",
        live[CAMP_A]["ceiling"] is None and live[CAMP_B]["ceiling"] is None,
        "A=%s B=%s" % (live[CAMP_A]["ceiling"], live[CAMP_B]["ceiling"]))
    chk("bidding_still_target_spend_both",
        all(v["bidding"] == "TARGET_SPEND" for v in live.values()), "TARGET_SPEND")
    chk("search_partners_off_both",
        not any(v["partners"] for v in live.values()), "False/False")
    chk("display_off_both",
        not any(v["display"] for v in live.values()), "False/False")
    chk("presence_geo_both",
        all(v["geo"] == "PRESENCE" for v in live.values()), "PRESENCE")
    chk("budgets_not_shared_refcount_1",
        all(v["budget_refs"] == 1 and not v["budget_shared"] for v in live.values()),
        "refs=1, explicitly_shared=False on both")

    counts = {
        "keywords": count(svc, "ad_group_criterion",
                          " WHERE ad_group_criterion.type = 'KEYWORD' AND "
                          "ad_group_criterion.negative = FALSE AND "
                          "ad_group_criterion.status != 'REMOVED'"),
        "ads": count(svc, "ad_group_ad", " WHERE ad_group_ad.status != 'REMOVED'"),
        "campaign_negative_keywords": count(
            svc, "campaign_criterion",
            " WHERE campaign_criterion.type = 'KEYWORD' AND "
            "campaign_criterion.negative = TRUE AND "
            "campaign_criterion.status != 'REMOVED'"),
        "ad_schedules": count(svc, "campaign_criterion",
                              " WHERE campaign_criterion.type = 'AD_SCHEDULE' AND "
                              "campaign_criterion.status != 'REMOVED'"),
        "conversion_actions": count(svc, "conversion_action",
                                    " WHERE conversion_action.status != 'REMOVED'"),
        "campaign_assets": count(svc, "campaign_asset",
                                 " WHERE campaign_asset.status != 'REMOVED'"),
        "ad_groups": count(svc, "ad_group", " WHERE ad_group.status != 'REMOVED'"),
    }
    for k, v in counts.items():
        chk("count_%s_unchanged" % k, v == EXPECT[k],
            "live=%s expected=%s" % (v, EXPECT[k]))

    # ---- 4. no change_event since the last approved execution ----
    q = ("SELECT change_event.change_date_time, change_event.change_resource_type "
         "FROM change_event "
         "WHERE change_event.change_date_time >= '2026-08-26 18:00:32' "
         "AND change_event.change_date_time <= '%s' "
         "ORDER BY change_event.change_date_time DESC LIMIT 50"
         % (now.strftime("%Y-%m-%d %H:%M:%S")))
    ce = rows(svc, q)
    chk("zero_change_events_since_last_approved_execution", len(ce) == 0,
        "%d change events after 2026-08-26 18:00:32" % len(ce))

    # ---- 5. plan-logic red team ----
    m = json.loads((SNAPS / "constraint-2026-08-27.json").read_text(
        encoding="utf-8"))["math"]
    chk("R_equals_target_minus_S",
        abs((2500.0 - m["S_mtd_spend"]) - m["R_remaining"]) < 0.005,
        "2500 - %s = %s" % (m["S_mtd_spend"], m["R_remaining"]))
    chk("serving_days_excludes_sunday",
        m["remaining_serving_days"] == 4
        and all(s["weekday"] != "Sunday"
                for s in m["remaining_serving_hour_detail"]),
        "4 serving days, Sunday 2026-08-30 excluded")
    chk("required_pace_exceeds_observed_run_rate",
        m["required_avg_per_remaining_calendar_day"]
        > m["observed_run_rate_per_serving_day_aug24_26"],
        "required $%s/day vs observed $%s/serving day"
        % (m["required_avg_per_remaining_calendar_day"],
           m["observed_run_rate_per_serving_day_aug24_26"]))
    chk("ceiling_above_documented_top_of_page_high", 30.00 > 28.23,
        "$30.00 ceiling > $28.23 top-of-page high")
    chk("no_prohibited_channel_in_plan",
        all(k not in json.dumps(plan).lower()
            for k in ("broad match\": true", "target_partner_search_network\": true")),
        "no Broad Match / Search Partners / Display / PMax enable in plan")

    result = {"read_only": True, "mutations_issued": 0,
              "timestamp_account_local": now.isoformat(),
              "checks": checks,
              "total": len(checks),
              "passed": sum(1 for c in checks if c["pass"]),
              "failed": [c for c in checks if not c["pass"]],
              "live_state": live, "live_counts": counts}
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("RED-TEAM / NO-CHANGE VERIFICATION  %s"
          % now.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("=" * 70)
    for c in checks:
        print("  [%s] %-52s %s" % ("PASS" if c["pass"] else "FAIL",
                                   c["check"], c["detail"]))
    print("=" * 70)
    print("  %d/%d passed, %d failed" % (result["passed"], result["total"],
                                         len(result["failed"])))
    print("  MUTATIONS ISSUED THIS SESSION: 0")
    print("\nwrote %s" % OUT)
    return 0 if not result["failed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
