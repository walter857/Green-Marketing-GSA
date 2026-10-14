#!/usr/bin/env python3
"""STAGE 11 - execute PLAN-K1 under exact approval.

APPROVED PHRASE: APPROVE PLAN-K1 3B77F0F4C879 FOR 1521725229

BIDDING ONLY. Sets target_spend.cpc_bid_ceiling_micros = 30000000 ($30.00) on
both Power Washing campaigns. Touches NO budget.

Guard rails, in order: identity gate, same-minute drift snapshot, fingerprint
recomputation, explicit one-path update mask, validate_only dry run, atomic
mutate (partial_failure=False), full readback, immediate pacing report.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.safety import approval_code                     # noqa: E402
from softwind_build_k1 import normalize                     # noqa: E402

APPROVED_PLAN = "PLAN-K1"
APPROVED_FP = "3B77F0F4C879"
APPROVED_PHRASE = "APPROVE PLAN-K1 3B77F0F4C879 FOR 1521725229"
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
TZ = ZoneInfo("America/New_York")
TARGET = 2500.0
CEILING_MICROS = 30_000_000
MASK = "target_spend.cpc_bid_ceiling_micros"

CLIENT = ROOT / "clients/softwind-power-washing"
PLAN_FILE = CLIENT / "plans/2026-08-27-plan-k1-cpc-control.yaml"
OUT = CLIENT / "snapshots/k1-execution-2026-08-27.json"

# Structural baseline that MUST NOT change. Filters recorded alongside counts.
BASELINE = {
    "budget_micros": {"24103511039": 333330000, "24145053510": 41110000},
    "keywords": 214, "ads": 54, "campaign_negative_keywords": 94,
    "ad_schedules": 12, "conversion_actions": 4, "campaign_assets": 20,
    "ad_groups": 30, "positive_locations": 80, "negative_locations": 1,
}

log = {"approved_plan": APPROVED_PLAN, "approved_fingerprint": APPROVED_FP,
       "approved_phrase": APPROVED_PHRASE, "stage": 11}
fail = False


def gate(label, ok, detail=""):
    global fail
    print("   [%s] %-52s %s" % ("PASS" if ok else "FAIL", label, detail))
    log.setdefault("gates", []).append(
        {"gate": label, "pass": bool(ok), "detail": detail})
    if not ok:
        fail = True
    return ok


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def usd(m):
    return round((m or 0) / 1_000_000, 2)


def snapshot(svc):
    """Full comparable state: campaigns, budgets, locations, counts."""
    s = {"campaigns": {}, "locations": {}, "counts": {}}
    q = ("SELECT campaign.id, campaign.name, campaign.status, "
         "campaign.serving_status, campaign.bidding_strategy_type, "
         "campaign.target_spend.cpc_bid_ceiling_micros, "
         "campaign.network_settings.target_google_search, "
         "campaign.network_settings.target_search_network, "
         "campaign.network_settings.target_content_network, "
         "campaign.geo_target_type_setting.positive_geo_target_type, "
         "campaign.start_date_time, campaign.end_date_time, "
         "campaign_budget.id, campaign_budget.amount_micros, "
         "campaign_budget.reference_count, campaign_budget.explicitly_shared, "
         "campaign_budget.delivery_method "
         "FROM campaign WHERE campaign.id IN (%s)" % ", ".join(CAMPAIGNS))
    for r in rows(svc, q):
        s["campaigns"][str(r.campaign.id)] = {
            "name": r.campaign.name,
            "status": r.campaign.status.name,
            "serving_status": r.campaign.serving_status.name,
            "bidding": r.campaign.bidding_strategy_type.name,
            "cpc_ceiling_micros":
                r.campaign.target_spend.cpc_bid_ceiling_micros or None,
            "cpc_ceiling_usd":
                usd(r.campaign.target_spend.cpc_bid_ceiling_micros) or None,
            "google_search": r.campaign.network_settings.target_google_search,
            "partners": r.campaign.network_settings.target_search_network,
            "display": r.campaign.network_settings.target_content_network,
            "positive_geo":
                r.campaign.geo_target_type_setting.positive_geo_target_type.name,
            "start_date_time": r.campaign.start_date_time,
            "end_date_time": r.campaign.end_date_time or None,
            "budget_id": str(r.campaign_budget.id),
            "budget_micros": r.campaign_budget.amount_micros,
            "budget_usd": usd(r.campaign_budget.amount_micros),
            "budget_refs": r.campaign_budget.reference_count,
            "budget_shared": r.campaign_budget.explicitly_shared,
            "budget_delivery": r.campaign_budget.delivery_method.name,
        }
    q = ("SELECT campaign.id, campaign_criterion.criterion_id, "
         "campaign_criterion.negative, campaign_criterion.status "
         "FROM campaign_criterion WHERE campaign.id IN (%s) "
         "AND campaign_criterion.type = 'LOCATION' "
         "AND campaign_criterion.status != 'REMOVED'" % ", ".join(CAMPAIGNS))
    for r in rows(svc, q):
        d = s["locations"].setdefault(str(r.campaign.id),
                                      {"positive": 0, "negative": 0,
                                       "non_enabled": 0})
        d["negative" if r.campaign_criterion.negative else "positive"] += 1
        if r.campaign_criterion.status.name != "ENABLED":
            d["non_enabled"] += 1

    def count(res, where):
        return len(rows(svc, "SELECT %s.resource_name FROM %s%s" % (res, res, where)))

    s["counts"] = {
        "keywords": count("ad_group_criterion",
                          " WHERE ad_group_criterion.type = 'KEYWORD' AND "
                          "ad_group_criterion.negative = FALSE AND "
                          "ad_group_criterion.status != 'REMOVED'"),
        "ads": count("ad_group_ad", " WHERE ad_group_ad.status != 'REMOVED'"),
        "campaign_negative_keywords": count(
            "campaign_criterion",
            " WHERE campaign_criterion.type = 'KEYWORD' AND "
            "campaign_criterion.negative = TRUE AND "
            "campaign_criterion.status != 'REMOVED'"),
        "ad_schedules": count("campaign_criterion",
                              " WHERE campaign_criterion.type = 'AD_SCHEDULE' AND "
                              "campaign_criterion.status != 'REMOVED'"),
        "conversion_actions": count("conversion_action",
                                    " WHERE conversion_action.status != 'REMOVED'"),
        "campaign_assets": count("campaign_asset",
                                 " WHERE campaign_asset.status != 'REMOVED'"),
        "ad_groups": count("ad_group", " WHERE ad_group.status != 'REMOVED'"),
    }
    return s


def main() -> int:
    global fail
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cs = client.get_service("CampaignService")
    started = datetime.now(TZ)
    log["started_account_local"] = started.isoformat()
    print("=" * 74)
    print("STAGE 11 - EXECUTE %s  (%s)" % (APPROVED_PLAN,
                                           started.strftime("%Y-%m-%d %H:%M:%S %Z")))
    print("=" * 74)

    # ---------------- 1. identity ----------------
    print("\n1. FRESH IDENTITY")
    c = rows(svc, "SELECT customer.id, customer.descriptive_name, customer.manager, "
                  "customer.test_account, customer.currency_code, "
                  "customer.time_zone, customer.status FROM customer LIMIT 1"
             )[0].customer
    log["identity"] = {"id": str(c.id), "name": c.descriptive_name,
                       "manager": c.manager, "test_account": c.test_account,
                       "currency": c.currency_code, "time_zone": c.time_zone,
                       "status": c.status.name}
    gate("account name exact", c.descriptive_name == NAME, c.descriptive_name)
    gate("customer id exact", str(c.id) == CID, str(c.id))
    gate("manager is false", c.manager is False, str(c.manager))
    gate("test_account is false", c.test_account is False, str(c.test_account))
    gate("currency USD", c.currency_code == "USD", c.currency_code)
    gate("time zone America/New_York", c.time_zone == "America/New_York", c.time_zone)
    gate("live marker in name", "- live" in c.descriptive_name.lower(), "'- live'")
    if fail:
        print("\nABORT - identity gate failed. Nothing was changed.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 2

    # ---------------- 2. drift snapshot ----------------
    print("\n2. DRIFT SNAPSHOT (before)")
    before = snapshot(svc)
    log["before"] = before
    for cid_, cp in before["campaigns"].items():
        print("   %-17s status=%s bidding=%s ceiling=%s budget=$%s refs=%s"
              % (cp["name"], cp["status"], cp["bidding"], cp["cpc_ceiling_usd"],
                 cp["budget_usd"], cp["budget_refs"]))
    for cid_ in CAMPAIGNS:
        cp = before["campaigns"].get(cid_)
        gate("campaign %s present" % cid_, cp is not None)
        if not cp:
            continue
        gate("  %s ENABLED" % CAMPAIGNS[cid_], cp["status"] == "ENABLED", cp["status"])
        gate("  %s bidding TARGET_SPEND" % CAMPAIGNS[cid_],
             cp["bidding"] == "TARGET_SPEND", cp["bidding"])
        gate("  %s ceiling still UNSET" % CAMPAIGNS[cid_],
             cp["cpc_ceiling_micros"] is None, str(cp["cpc_ceiling_usd"]))
        gate("  %s budget unchanged" % CAMPAIGNS[cid_],
             cp["budget_micros"] == BASELINE["budget_micros"][cid_],
             "%d micros" % cp["budget_micros"])
        gate("  %s partners off" % CAMPAIGNS[cid_], cp["partners"] is False)
        gate("  %s display off" % CAMPAIGNS[cid_], cp["display"] is False)
        gate("  %s geo PRESENCE" % CAMPAIGNS[cid_], cp["positive_geo"] == "PRESENCE")
        gate("  %s no end date" % CAMPAIGNS[cid_], not cp["end_date_time"])
        loc = before["locations"].get(cid_, {})
        gate("  %s 80 positive locations" % CAMPAIGNS[cid_],
             loc.get("positive") == BASELINE["positive_locations"],
             str(loc.get("positive")))
        gate("  %s 1 negative location" % CAMPAIGNS[cid_],
             loc.get("negative") == BASELINE["negative_locations"],
             str(loc.get("negative")))
    for k, v in BASELINE.items():
        if k in ("budget_micros", "positive_locations", "negative_locations"):
            continue
        gate("count %s == %d" % (k, v), before["counts"][k] == v,
             str(before["counts"][k]))
    if fail:
        print("\nABORT - drift detected. Nothing was changed.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 2

    # ---------------- 3. fingerprint ----------------
    print("\n3. FINGERPRINT RECOMPUTATION")
    plan = yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))
    recomputed = approval_code(normalize(plan))
    log["fingerprint_recomputed"] = recomputed
    gate("fingerprint matches approval", recomputed == APPROVED_FP,
         "%s == %s" % (recomputed, APPROVED_FP))
    gate("plan file fingerprint field matches",
         plan["change_plan"]["fingerprint"] == APPROVED_FP,
         plan["change_plan"]["fingerprint"])
    gate("plan identity matches gate",
         plan["change_plan"]["target"]["child_customer_id"] == CID
         and plan["change_plan"]["target"]["exact_child_account_name"] == NAME
         and plan["change_plan"]["target"]["exact_service"] == "Power Washing")
    gate("plan declares 0 budget changes",
         plan["change_plan"]["change_counts"]["budgets_changed"] == 0)
    gate("plan declares 2 mutations",
         plan["change_plan"]["change_counts"]["google_ads_mutations_total"] == 2)
    if fail:
        print("\nABORT - fingerprint or plan integrity failed. Nothing was changed.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 2

    # ---------------- 4. build operations ----------------
    print("\n4. BUILD OPERATIONS")
    ops, intended = [], {}
    for a in plan["change_plan"]["actions"]:
        cid_ = str(a["campaign_id"])
        want = int(a["proposed_value"]["target_spend_cpc_bid_ceiling_micros"])
        gate("action %s targets a plan campaign" % a["action_id"],
             cid_ in CAMPAIGNS, cid_)
        gate("action %s resource_type CAMPAIGN" % a["action_id"],
             a["resource_type"] == "CAMPAIGN", a["resource_type"])
        gate("action %s mask is the single authorised path" % a["action_id"],
             a["proposed_value"]["field_mask"] == MASK,
             a["proposed_value"]["field_mask"])
        gate("action %s ceiling == 30000000" % a["action_id"],
             want == CEILING_MICROS, str(want))
        op = client.get_type("CampaignOperation")
        cu = op.update
        cu.resource_name = cs.campaign_path(CID, cid_)
        cu.target_spend.cpc_bid_ceiling_micros = want
        # Explicit single-path mask. protobuf_helpers.field_mask would also list
        # resource_name and widen the mask beyond what this plan authorises.
        op.update_mask.paths.append(MASK)
        ops.append(op)
        intended[cid_] = want
        print("   %s %-18s ceiling: unset -> %d micros ($%.2f)"
              % (cid_, CAMPAIGNS[cid_], want, want / 1e6))
    gate("exactly 2 operations built", len(ops) == 2, str(len(ops)))
    for i, op in enumerate(ops):
        gate("op %d mask is exactly [%s]" % (i, MASK),
             list(op.update_mask.paths) == [MASK], str(list(op.update_mask.paths)))
    gate("no budget field in any operation",
         all("amount_micros" not in p for op in ops for p in op.update_mask.paths))
    gate("both plan campaigns covered", set(intended) == set(CAMPAIGNS))
    if fail:
        print("\nABORT - operation build failed. Nothing was changed.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 2

    # ---------------- 5. validate_only ----------------
    print("\n5. VALIDATE-ONLY DRY RUN (nothing is applied)")
    req = client.get_type("MutateCampaignsRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    req.partial_failure = False
    req.validate_only = True
    try:
        cs.mutate_campaigns(request=req)
        print("   dry run PASSED")
        log["dry_run"] = "PASSED"
    except Exception as exc:                                  # noqa: BLE001
        print("   dry run FAILED - nothing was applied")
        print("   %s" % str(exc)[:1200])
        log["dry_run"] = "FAILED"
        log["dry_run_error"] = str(exc)[:4000]
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    # ---------------- 6. execute ----------------
    print("\n6. EXECUTING - atomic, partial_failure=False")
    req.validate_only = False
    exec_at = datetime.now(TZ)
    try:
        resp = cs.mutate_campaigns(request=req)
    except Exception as exc:                                  # noqa: BLE001
        print("   MUTATE FAILED - request was atomic, nothing was applied")
        print("   %s" % str(exc)[:1500])
        log["execution"] = "FAILED_ATOMIC_NO_CHANGE"
        log["execution_error"] = str(exc)[:4000]
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1
    changed = [r.resource_name for r in resp.results]
    log["execution"] = "SUCCEEDED"
    log["executed_account_local"] = exec_at.isoformat()
    log["changed_resource_names"] = changed
    print("   updated %d campaign(s)" % len(changed))
    for r in changed:
        print("      %s" % r)

    # ---------------- 7. readback QA ----------------
    print("\n7. READBACK QA")
    after = snapshot(svc)
    log["after"] = after
    for cid_ in CAMPAIGNS:
        cp = after["campaigns"][cid_]
        gate("%s ceiling == $30.00" % CAMPAIGNS[cid_],
             cp["cpc_ceiling_micros"] == CEILING_MICROS,
             "%s micros" % cp["cpc_ceiling_micros"])
        gate("%s bidding still TARGET_SPEND" % CAMPAIGNS[cid_],
             cp["bidding"] == "TARGET_SPEND", cp["bidding"])
        gate("%s budget UNCHANGED" % CAMPAIGNS[cid_],
             cp["budget_micros"] == before["campaigns"][cid_]["budget_micros"],
             "$%s" % cp["budget_usd"])
        gate("%s status unchanged" % CAMPAIGNS[cid_],
             cp["status"] == before["campaigns"][cid_]["status"], cp["status"])
        gate("%s partners still off" % CAMPAIGNS[cid_], cp["partners"] is False)
        gate("%s display still off" % CAMPAIGNS[cid_], cp["display"] is False)
        gate("%s geo still PRESENCE" % CAMPAIGNS[cid_],
             cp["positive_geo"] == "PRESENCE", cp["positive_geo"])
        gate("%s budget refs still 1" % CAMPAIGNS[cid_], cp["budget_refs"] == 1)
        gate("%s locations unchanged" % CAMPAIGNS[cid_],
             after["locations"][cid_] == before["locations"][cid_],
             json.dumps(after["locations"][cid_]))
    gate("all structural counts unchanged", after["counts"] == before["counts"],
         json.dumps(after["counts"]))
    changed_fields = {k: (before["campaigns"][k], after["campaigns"][k])
                      for k in CAMPAIGNS
                      if before["campaigns"][k] != after["campaigns"][k]}
    diffs = {}
    for cid_, (b, a2) in changed_fields.items():
        diffs[cid_] = {k: [b[k], a2[k]] for k in b if b[k] != a2[k]}
    log["field_level_diff"] = diffs
    only_ceiling = all(set(d) <= {"cpc_ceiling_micros", "cpc_ceiling_usd"}
                       for d in diffs.values())
    gate("ONLY the cpc ceiling field changed", only_ceiling, json.dumps(diffs))

    # change_event corroboration
    win_lo = (exec_at - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    win_hi = (datetime.now(TZ) + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    ce = rows(svc, "SELECT change_event.change_date_time, "
                   "change_event.change_resource_type, "
                   "change_event.resource_change_operation, "
                   "change_event.changed_fields, "
                   "change_event.change_resource_name FROM change_event "
                   "WHERE change_event.change_date_time >= '%s' "
                   "AND change_event.change_date_time <= '%s' "
                   "ORDER BY change_event.change_date_time DESC LIMIT 20"
             % (win_lo, win_hi))
    evs = [{"when": e.change_event.change_date_time,
            "type": e.change_event.change_resource_type.name,
            "op": e.change_event.resource_change_operation.name,
            "fields": list(e.change_event.changed_fields.paths),
            "resource": e.change_event.change_resource_name} for e in ce]
    log["change_events_in_window"] = evs
    gate("exactly 2 change events in window", len(evs) == 2, str(len(evs)))
    gate("both change events are CAMPAIGN UPDATE",
         all(e["type"] == "CAMPAIGN" and e["op"] == "UPDATE" for e in evs),
         json.dumps([e["type"] + "/" + e["op"] for e in evs]))
    log["qa_failures"] = [g for g in log["gates"] if not g["pass"]]
    log["qa_passed"] = not fail

    # ---------------- 8. immediate pacing ----------------
    print("\n8. IMMEDIATE PACING REPORT")
    now = datetime.now(TZ)
    today = now.strftime("%Y-%m-%d")
    q = ("SELECT campaign.id, metrics.cost_micros, metrics.impressions, "
         "metrics.clicks FROM campaign WHERE campaign.id IN (%s) "
         "AND segments.date BETWEEN '2026-08-01' AND '%s'"
         % (", ".join(CAMPAIGNS), today))
    per, mtd = {}, 0.0
    for r in rows(svc, q):
        cst = usd(r.metrics.cost_micros)
        per[CAMPAIGNS[str(r.campaign.id)]] = {
            "cost": cst, "impressions": r.metrics.impressions,
            "clicks": r.metrics.clicks}
        mtd += cst
    mtd = round(mtd, 2)
    month_end = datetime(2026, 9, 1, tzinfo=TZ)
    H = round((month_end - now).total_seconds() / 3600, 2)
    D = (datetime(2026, 8, 31, tzinfo=TZ).date() - now.date()).days + 1
    R = round(TARGET - mtd, 2)
    sh, cur = 0.0, now
    while cur < month_end:
        if cur.weekday() != 6:
            s = max(cur, cur.replace(hour=8, minute=0, second=0, microsecond=0))
            e = min(month_end, cur.replace(hour=18, minute=0, second=0,
                                           microsecond=0))
            if e > s:
                sh += (e - s).total_seconds() / 3600
        cur = (cur + timedelta(days=1)).replace(hour=0, minute=0, second=0,
                                                microsecond=0)
    sh = round(sh, 2)
    log["pacing"] = {"timestamp": now.isoformat(), "mtd_spend_S": mtd,
                     "per_campaign": per, "remaining_R": R,
                     "remaining_days_D": D, "remaining_hours_H": H,
                     "remaining_scheduled_serving_hours": sh,
                     "required_rolling_24h_pace": round(R / (H / 24), 2),
                     "required_per_serving_hour": round(R / sh, 2),
                     "combined_daily_budget": 374.44,
                     "cpc_ceiling_now_usd": 30.00}
    print("   MTD $%s | remaining $%s | H %sh | serving hours %s" % (mtd, R, H, sh))
    print("   required 24h pace $%s | per serving hour $%s"
          % (log["pacing"]["required_rolling_24h_pace"],
             log["pacing"]["required_per_serving_hour"]))
    print("   per campaign: %s" % json.dumps(per))

    OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print("\n" + "=" * 74)
    print("RESULT: %s   gates %d/%d passed"
          % ("QA PASSED" if not fail else "QA FAILED",
             sum(1 for g in log["gates"] if g["pass"]), len(log["gates"])))
    print("=" * 74)
    print("wrote %s" % OUT)
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
