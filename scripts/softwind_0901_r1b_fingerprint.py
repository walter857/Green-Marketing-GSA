#!/usr/bin/env python3
"""Validate PLAN-R1B and generate its fingerprint.

Duplicate-key-aware YAML load, fresh read-only confirmation of every asserted
current value, zero-Google-Ads-mutation assertion, GET_DIRECTIONS assertion, and
a doubly-recomputed repository-standard SHA-256 fingerprint.

SELECT statements only. Constructs no operation, calls no mutate service.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name
from gm_gsa.safety import approval_code, assert_no_embedded_secrets

CID = "1521725229"
PLAN = ROOT / "clients/softwind-power-washing/plans/2026-09-01-plan-r1b-controlled-form-test.yaml"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"


class DupSafeLoader(yaml.SafeLoader):
    pass


def _no_duplicates(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate mapping key: {key!r}", key_node.start_mark)
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


DupSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


def main() -> int:
    checks: list[dict] = []

    def check(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        return bool(ok)

    # ---------- 1. duplicate-key-aware YAML validation ----------
    try:
        doc = yaml.load(PLAN.read_text(encoding="utf-8"), Loader=DupSafeLoader)
        check("duplicate-key-aware YAML parse", True, "no repeated mapping key")
    except yaml.constructor.ConstructorError as exc:
        check("duplicate-key-aware YAML parse", False, str(exc))
        print(json.dumps(checks, indent=2))
        return 2

    plan = doc["change_plan"]
    assert_no_embedded_secrets(plan)
    check("no embedded secrets", True)

    # ---------- 2. structural / count assertions ----------
    counts = plan["counts"]
    actions = plan["actions"]
    writes = [a for a in actions if a.get("external_write") is True]
    reads = [a for a in actions if a.get("external_write") is False]

    check("google_ads_mutation_count == 0", counts["google_ads_mutation_count"] == 0,
          str(counts["google_ads_mutation_count"]))
    check("action_count matches the action list",
          counts["action_count"] == len(actions), f"{counts['action_count']} vs {len(actions)}")
    check("object_count matches the action list",
          counts["object_count"] == len(actions))
    check("external_test_action_count matches",
          counts["external_test_action_count"] == len(actions))
    check("external_write_action_count matches",
          counts["external_write_action_count"] == len(writes),
          f"{counts['external_write_action_count']} vs {len(writes)}")
    check("external_read_action_count matches",
          counts["external_read_action_count"] == len(reads),
          f"{counts['external_read_action_count']} vs {len(reads)}")
    check("calls placed == 0", counts["calls_placed_by_this_plan"] == 0)
    check("exactly one form submission", counts["forms_submitted_by_this_plan_when_executed"] == 1)
    check("no action mutates Google Ads",
          all(a["type"] in ("EXTERNAL_READ", "EXTERNAL_WRITE") for a in actions))
    check("plan marked NOT APPROVED", plan["approval_status"] == "NOT APPROVED")
    check("plan marked DO NOT EXECUTE", plan["execution_status"] == "DO NOT EXECUTE")
    check("target child customer id correct", plan["target"]["child_customer_id"] == CID)
    check("test phone is the reserved fictitious range",
          plan["test_identity"]["test_phone"] == "631-555-0147")
    check("test phone is not a real client line",
          plan["test_identity"]["test_phone"] not in ("(631) 502-7946", "(631) 502-5402"))

    # ---------- 3. fresh read-only confirmation of every asserted value ----------
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)

    def q(query):
        return list(svc.search(customer_id=cid, query=query))

    c = q("""SELECT customer.id, customer.descriptive_name, customer.manager,
                    customer.test_account, customer.status
             FROM customer LIMIT 1""")[0].customer
    check("fresh identity name", c.descriptive_name == "Softwind Power Washing - Live",
          c.descriptive_name)
    check("fresh identity id", normalize_customer_id(c.id) == CID)
    check("not manager", bool(c.manager) is False)
    check("not test account", bool(c.test_account) is False)

    cfg = {str(r.campaign.id): enum_name(r.conversion_goal_campaign_config.goal_config_level)
           for r in q("""SELECT campaign.id,
                                conversion_goal_campaign_config.goal_config_level
                         FROM conversion_goal_campaign_config""")}
    check("24103511039 goal_config_level == CAMPAIGN", cfg.get("24103511039") == "CAMPAIGN",
          str(cfg.get("24103511039")))
    check("24145053510 goal_config_level == CAMPAIGN", cfg.get("24145053510") == "CAMPAIGN",
          str(cfg.get("24145053510")))

    cmg = {(str(r.campaign.id), enum_name(r.campaign_conversion_goal.category),
            enum_name(r.campaign_conversion_goal.origin)): bool(r.campaign_conversion_goal.biddable)
           for r in q("""SELECT campaign.id, campaign_conversion_goal.category,
                                campaign_conversion_goal.origin,
                                campaign_conversion_goal.biddable
                         FROM campaign_conversion_goal""")}
    for camp in ("24103511039", "24145053510"):
        for cat, org in (("PHONE_CALL_LEAD", "WEBSITE"),
                         ("PHONE_CALL_LEAD", "CALL_FROM_ADS"),
                         ("SUBMIT_LEAD_FORM", "WEBSITE")):
            check(f"{camp} campaign goal {cat}/{org} biddable == true",
                  cmg.get((camp, cat, org)) is True)
        check(f"{camp} campaign goal GET_DIRECTIONS/GOOGLE_HOSTED biddable == FALSE",
              cmg.get((camp, "GET_DIRECTIONS", "GOOGLE_HOSTED")) is False)

    ccg = {(enum_name(r.customer_conversion_goal.category),
            enum_name(r.customer_conversion_goal.origin)): bool(r.customer_conversion_goal.biddable)
           for r in q("""SELECT customer_conversion_goal.category,
                                customer_conversion_goal.origin,
                                customer_conversion_goal.biddable
                         FROM customer_conversion_goal""")}
    check("customer GET_DIRECTIONS goal remains biddable == FALSE",
          ccg.get(("GET_DIRECTIONS", "GOOGLE_HOSTED")) is False)
    check("customer goals unchanged - all four still false",
          all(v is False for v in ccg.values()), json.dumps(
              {f"{k[0]}/{k[1]}": v for k, v in ccg.items()}))

    ca = {str(r.conversion_action.id): r.conversion_action
          for r in q("""SELECT conversion_action.id, conversion_action.name,
                               conversion_action.status, conversion_action.category,
                               conversion_action.origin, conversion_action.primary_for_goal,
                               conversion_action.include_in_conversions_metric,
                               conversion_action.counting_type,
                               conversion_action.click_through_lookback_window_days,
                               conversion_action.view_through_lookback_window_days,
                               conversion_action.owner_customer
                        FROM conversion_action WHERE conversion_action.status != 'REMOVED'""")}
    check("all four conversion actions present", len(ca) == 4, str(sorted(ca)))
    check("all actions primary_for_goal == true",
          all(bool(a.primary_for_goal) for a in ca.values()))
    check("all actions owned by this customer",
          all((a.owner_customer or "").split("/")[-1] == CID for a in ca.values()))
    form = ca.get("7708725995")
    ref = plan["expected_conversion_reference"]
    check("form action 7708725995 exists and is ENABLED",
          form is not None and enum_name(form.status) == "ENABLED")
    check("form action counting_type matches plan",
          enum_name(form.counting_type) == ref["counting_type"])
    check("form action click window matches plan",
          int(form.click_through_lookback_window_days) == ref["click_through_lookback_window_days"])
    check("form action view window matches plan",
          int(form.view_through_lookback_window_days) == ref["view_through_lookback_window_days"])
    check("form action primary_for_goal matches plan",
          bool(form.primary_for_goal) == ref["primary_for_goal"])
    check("form action include_in_conversions_metric matches plan",
          bool(form.include_in_conversions_metric) == ref["include_in_conversions_metric"])

    allconv = {str(r.conversion_action.id): float(r.metrics.all_conversions)
               for r in q("""SELECT conversion_action.id, metrics.all_conversions
                             FROM conversion_action
                             WHERE segments.date BETWEEN '2026-01-01' AND '2026-09-01'""")}
    check("all_conversions still 0.0 on every action",
          all(v == 0.0 for v in allconv.values()), json.dumps(allconv))

    ct = q("""SELECT customer.conversion_tracking_setting.conversion_tracking_id,
                     customer.conversion_tracking_setting.cross_account_conversion_tracking_id
              FROM customer LIMIT 1""")[0].customer.conversion_tracking_setting
    check("account conversion_tracking_id matches plan",
          str(ct.conversion_tracking_id) == ref["account_conversion_tracking_id"])
    check("no cross-account conversion tracking",
          not bool(ct.cross_account_conversion_tracking_id))

    # ---------- 4. validate_only ----------
    validate_only = {
        "applicable": False,
        "reason": ("PLAN-R1B contains ZERO Google Ads mutations, so there is no mutation "
                   "payload to validate. validate_only is not run. It would also consume "
                   "the same daily mutate quota as a real write for no information gain."),
    }
    check("validate_only correctly not applicable", counts["google_ads_mutation_count"] == 0)

    # ---------- 5. fingerprint ----------
    canonical = {
        "plan_id": plan["plan_id"],
        "plan_class": plan["plan_class"],
        "target": {
            "exact_child_account_name": plan["target"]["exact_child_account_name"],
            "child_customer_id": plan["target"]["child_customer_id"],
            "exact_service": plan["target"]["exact_service"],
            "manager_customer_id": plan["target"]["manager_customer_id"],
        },
        "google_ads_mutation_count": 0,
        "actions": [
            {"id": a["id"], "type": a["type"],
             "external_write": bool(a["external_write"])} for a in actions
        ],
        "page_under_test": plan["page_under_test"]["url"],
        "form_identifier": plan["page_under_test"]["form_identifier"],
        "submissions_permitted": plan["page_under_test"]["submissions_permitted"],
        "test_full_name": plan["test_identity"]["test_full_name"],
        "test_phone": plan["test_identity"]["test_phone"],
        "conversion_action_id": ref["conversion_action_id"],
        "arrival_synthetic_gclid": plan["arrival_url"]["synthetic_parameters"]["gclid"],
    }
    fp1 = approval_code(canonical)
    fp2 = approval_code(json.loads(json.dumps(canonical)))
    fp3 = approval_code(canonical)
    check("fingerprint recomputed twice, identical", fp1 == fp2 == fp3, f"{fp1}/{fp2}/{fp3}")

    tz = ZoneInfo("America/New_York")
    now = datetime.now(tz)
    result = {
        "plan_id": "PLAN-R1B",
        "plan_file": str(PLAN.relative_to(ROOT)).replace("\\", "/"),
        "generated_account_local": now.isoformat(),
        "action_count": counts["action_count"],
        "object_count": counts["object_count"],
        "google_ads_mutation_count": counts["google_ads_mutation_count"],
        "external_test_action_count": counts["external_test_action_count"],
        "external_write_action_count": counts["external_write_action_count"],
        "validate_only": validate_only,
        "fingerprint": fp1,
        "fingerprint_recompute_1": fp2,
        "fingerprint_recompute_2": fp3,
        "canonical_sha256_full": __import__("hashlib").sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")).hexdigest(),
        "approval_status": "NOT APPROVED",
        "execution_status": "DO NOT EXECUTE",
        "approval_command": f"APPROVE PLAN-R1B {fp1} FOR {CID}",
        "get_directions_remains_false": {
            "customer_level": ccg.get(("GET_DIRECTIONS", "GOOGLE_HOSTED")),
            "campaign_24103511039": cmg.get(("24103511039", "GET_DIRECTIONS", "GOOGLE_HOSTED")),
            "campaign_24145053510": cmg.get(("24145053510", "GET_DIRECTIONS", "GOOGLE_HOSTED")),
            "unchanged_by_this_plan": True,
        },
        "checks": checks,
        "checks_run": len(checks),
        "checks_failed": [c for c in checks if not c["pass"]],
        "all_checks_pass": all(c["pass"] for c in checks),
    }
    path = SNAP / f"plan-r1b-validation-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "checks"}, indent=2, default=str))
    print("\nFAILED CHECKS:", json.dumps(result["checks_failed"], indent=2))
    print("WROTE", path)
    return 0 if result["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
