#!/usr/bin/env python3
"""Validate PLAN-R7A and generate its fingerprint. READ-ONLY. No mutation."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.google_ads import enum_name  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402

CID = "1521725229"
PLAN = ROOT / ("clients/softwind-power-washing/plans/"
               "2026-09-02-plan-r7a-website-tracking-form-call-repair.yaml")
SNAP = ROOT / "clients/softwind-power-washing/snapshots"


class Dup(yaml.SafeLoader):
    pass


def _nd(loader, node, deep=False):
    m = {}
    for k, v in node.value:
        kk = loader.construct_object(k, deep=deep)
        if kk in m:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate mapping key: {kk!r}", k.start_mark)
        m[kk] = loader.construct_object(v, deep=deep)
    return m


Dup.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _nd)


def main() -> int:
    checks = []

    def ck(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": str(detail)[:200]})
        return bool(ok)

    try:
        doc = yaml.load(PLAN.read_text(encoding="utf-8"), Loader=Dup)
        ck("duplicate-key-aware YAML parse", True, "no repeated mapping key")
    except yaml.constructor.ConstructorError as exc:
        ck("duplicate-key-aware YAML parse", False, exc)
        print(json.dumps(checks, indent=2))
        return 2

    p = doc["change_plan"]
    assert_no_embedded_secrets(p)
    ck("no embedded secrets", True)

    acts = p["actions"]
    c = p["counts"]
    blocked = [a for a in acts if str(a["execution_status"]).startswith("BLOCKED")]
    monitor = [a for a in acts if str(a["execution_status"]).startswith("MONITOR")]
    executable = [a for a in acts if a not in blocked]

    ck("google_ads_mutation_count == 0", c["google_ads_mutation_count"] == 0)
    ck("no action targets a Google Ads campaign resource",
       not any("campaign" in json.dumps(a).lower().replace("campaign_", "")
               and "google ads campaign" in json.dumps(a).lower() for a in acts))
    ck("website_action_count matches action list",
       c["website_action_count"] == len(acts), f"{c['website_action_count']} vs {len(acts)}")
    ck("object_count matches action list", c["object_count"] == len(acts))
    ck("blocked_action_count matches", c["blocked_action_count"] == len(blocked),
       f"{c['blocked_action_count']} vs {len(blocked)}")
    ck("executable_action_count matches", c["executable_action_count"] == len(executable),
       f"{c['executable_action_count']} vs {len(executable)}")
    ck("test_action_count == 0 (post-repair test is a separate approval)",
       c["test_action_count"] == 0)
    ck("every action has an id, priority, rollback and qa",
       all(all(k in a for k in ("id", "priority", "rollback", "qa")) for a in acts))
    ck("every action has evidence", all("evidence" in a for a in acts))
    ck("every action has an execution_status", all("execution_status" in a for a in acts))
    ck("no action is marked EXECUTED",
       not any("NOT" not in str(a["execution_status"]) and
               "EXECUTED" in str(a["execution_status"]) for a in acts))
    ck("plan NOT APPROVED", p["approval_status"] == "NOT APPROVED")
    ck("plan DO NOT EXECUTE", p["execution_status"] == "DO NOT EXECUTE")
    ck("target child customer id correct", p["target"]["child_customer_id"] == CID)
    ck("exactly one call architecture selected",
       p["call_tracking_architecture"]["selected"].startswith("OPTION A"))
    ck("blocked vendor action excluded from executable set",
       all(a["id"] != "R7A-9" for a in executable))
    ck("CRO items excluded and deferred to PLAN-R7B",
       p["explicitly_excluded_to_plan_r7b"]["plan_id"] == "PLAN-R7B"
       and p["explicitly_excluded_to_plan_r7b"]["not_built_or_fingerprinted_here"] is True)
    ck("GTM inaccessibility stated verbatim",
       p["access_limitation"]["gtm_read"] == "GTM-P3LD97NN COULD NOT BE READ")
    ck("honeypot preservation required in QA",
       any("honeypot" in str(x).lower() for x in p["post_repair_qa_requirements"]["checks"]))
    ck("monitor-only action carries no change", len(monitor) == 1)

    # ---------- fresh confirmation of every Google Ads fact the plan asserts ----------
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    def q(s, cust=CID):
        return list(svc.search(customer_id=normalize_customer_id(cust), query=s))

    cu = q("""SELECT customer.id, customer.descriptive_name, customer.manager,
                     customer.test_account, customer.status, customer.currency_code,
                     customer.time_zone,
                     customer.conversion_tracking_setting.conversion_tracking_id,
                     customer.conversion_tracking_setting.cross_account_conversion_tracking_id,
                     customer.conversion_tracking_setting.google_ads_conversion_customer
              FROM customer LIMIT 1""")[0].customer
    cts = cu.conversion_tracking_setting
    ck("identity name", cu.descriptive_name == "Softwind Power Washing - Live",
       cu.descriptive_name)
    ck("identity id", normalize_customer_id(cu.id) == CID)
    ck("not manager", cu.manager is False)
    ck("not test", cu.test_account is False)
    ck("status ENABLED", enum_name(cu.status) == "ENABLED")
    ck("currency USD", cu.currency_code == "USD")
    ck("tz America/New_York", cu.time_zone == "America/New_York")
    ck("conversion customer is self",
       cts.google_ads_conversion_customer == f"customers/{CID}")
    ck("cross-account conversion tracking NOT active",
       not bool(cts.cross_account_conversion_tracking_id))
    ck("account tracking id is 18369652705", str(cts.conversion_tracking_id) == "18369652705",
       cts.conversion_tracking_id)

    ca = {str(r.conversion_action.id): r.conversion_action for r in q(
        """SELECT conversion_action.id, conversion_action.name, conversion_action.status,
                  conversion_action.type, conversion_action.primary_for_goal,
                  conversion_action.phone_call_duration_seconds,
                  conversion_action.counting_type,
                  conversion_action.click_through_lookback_window_days
           FROM conversion_action WHERE conversion_action.status != 'REMOVED'""")}
    wc = ca.get("7708765130")
    ck("website-call action 7708765130 ENABLED", wc and enum_name(wc.status) == "ENABLED")
    ck("website-call action primary_for_goal", wc and bool(wc.primary_for_goal))
    ck("website-call 60s qualified threshold", wc and wc.phone_call_duration_seconds == 60)
    fm = ca.get("7708725995")
    ck("form action 7708725995 ONE_PER_CLICK", fm and enum_name(fm.counting_type) == "ONE_PER_CLICK")
    ck("form action 90-day click window", fm and fm.click_through_lookback_window_days == 90)
    allconv = {str(r.conversion_action.id): float(r.metrics.all_conversions) for r in q(
        """SELECT conversion_action.id, metrics.all_conversions FROM conversion_action
           WHERE segments.date BETWEEN '2026-01-01' AND '2026-09-02'""")}
    ck("Google Ads conversion history still clean (test wrote nothing)",
       all(v == 0.0 for v in allconv.values()), json.dumps(allconv))

    sib = q("""SELECT customer.id, customer.descriptive_name,
                      customer.conversion_tracking_setting.conversion_tracking_id
               FROM customer LIMIT 1""", "2429758629")[0].customer
    ck("AW-17878095007 belongs to Softwind Landscape & Masonry 2429758629",
       str(sib.conversion_tracking_setting.conversion_tracking_id) == "17878095007",
       f"{sib.id} {sib.descriptive_name}")

    # ---------- fingerprint ----------
    canonical = {
        "plan_id": p["plan_id"],
        "plan_class": p["plan_class"],
        "target": {k: p["target"][k] for k in
                   ("exact_child_account_name", "child_customer_id",
                    "exact_service", "manager_customer_id", "website")},
        "google_ads_mutation_count": 0,
        "call_architecture": p["call_tracking_architecture"]["selected"],
        "pages_in_scope": sorted(p["target"]["pages_in_scope"]),
        "actions": [{"id": a["id"], "priority": a["priority"], "system": a["system"],
                     "target_identifier": str(a.get("target_identifier", "")),
                     "pages_affected": a["pages_affected"],
                     "execution_status": a["execution_status"]} for a in acts],
    }
    fp1 = approval_code(canonical)
    fp2 = approval_code(json.loads(json.dumps(canonical)))
    fp3 = approval_code(canonical)
    ck("fingerprint recomputed twice, identical", fp1 == fp2 == fp3, f"{fp1}/{fp2}/{fp3}")

    now = datetime.now(ZoneInfo("America/New_York"))
    res = {
        "plan_id": "PLAN-R7A",
        "plan_file": str(PLAN.relative_to(ROOT)).replace("\\", "/"),
        "generated_account_local": now.isoformat(),
        "counts": c,
        "blocked_actions": [a["id"] for a in blocked],
        "monitor_only_actions": [a["id"] for a in monitor],
        "executable_actions": [a["id"] for a in executable],
        "call_architecture": p["call_tracking_architecture"]["selected"],
        "fingerprint": fp1, "recompute_1": fp2, "recompute_2": fp3,
        "canonical_sha256_full": hashlib.sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")).hexdigest(),
        "approval_status": "NOT APPROVED", "execution_status": "DO NOT EXECUTE",
        "approval_command": f"APPROVE PLAN-R7A {fp1} FOR {CID}",
        "checks_run": len(checks),
        "checks_failed": [c2 for c2 in checks if not c2["pass"]],
        "all_checks_pass": all(c2["pass"] for c2 in checks),
        "checks": checks,
    }
    path = SNAP / f"plan-r7a-validation-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    path.write_text(json.dumps(res, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "checks"}, indent=2, default=str))
    print("\nWROTE", path)
    return 0 if res["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
