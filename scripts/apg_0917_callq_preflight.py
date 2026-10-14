#!/usr/bin/env python3
"""APG-0917-CALL-Q preflight: duplicate check, validate_only, red team, fingerprint.

Creates nothing. Every Google Ads request is read-only or validate_only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, GM_MANAGER, client, q, E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code, SECRET_KEY_PATTERN  # noqa: E402

PLANS = ROOT / "clients/apogee-lawns/plans"
PLAN = PLANS / "APG-0917-CALL-Q.yaml"
WANT_PHONE = "4025265754"
FORBIDDEN = ("4022027261", "402-202-7261", "+14022027261")

fails = []


def chk(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' -> ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)


c = client()
raw = PLAN.read_text(encoding="utf-8")
d = load_yaml(str(PLAN))

print("=" * 78 + "\n1. IDENTITY GATE (live)\n" + "=" * 78)
cust = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
                      customer.test_account, customer.time_zone,
                      customer.call_reporting_setting.call_reporting_enabled,
                      customer.call_reporting_setting.call_conversion_reporting_enabled
               FROM customer""")[0].customer
chk(str(cust.id) == CID, "customer.id", str(cust.id))
chk(cust.descriptive_name == EXACT_NAME, "descriptive_name", cust.descriptive_name)
chk(not cust.manager and not cust.test_account, "not manager / not test")
chk(cust.time_zone == "America/Chicago", "account time zone is Central", cust.time_zone)
chk(cust.call_reporting_setting.call_reporting_enabled, "call reporting enabled")
chk(cust.call_reporting_setting.call_conversion_reporting_enabled,
    "call conversion reporting enabled")
links = {x.customer_manager_link.manager_customer.split("/")[-1]: E(x.customer_manager_link.status)
         for x in q(c, """SELECT customer_manager_link.manager_customer,
                                 customer_manager_link.status FROM customer_manager_link""")}
chk(links.get(GM_MANAGER) == "ACTIVE", f"manager {GM_MANAGER} ACTIVE, never mutated")

print("\n" + "=" * 78 + "\n2. DUPLICATE CHECK (live)\n" + "=" * 78)
call_assets = q(c, """SELECT asset.id, asset.call_asset.phone_number FROM asset
                      WHERE asset.type = 'CALL'""")
chk(len(call_assets) == 0, "zero existing CALL assets", str(len(call_assets)))
ca_links = q(c, "SELECT campaign_asset.field_type, campaign_asset.asset FROM campaign_asset")
n_call_links = sum(1 for x in ca_links if E(x.campaign_asset.field_type) == "CALL")
chk(n_call_links == 0, "zero existing campaign_asset CALL links", str(n_call_links))
chk(len(ca_links) == 7, "existing campaign_asset links == 7 (6 callout + 1 snippet)",
    str(len(ca_links)))
convs = q(c, """SELECT conversion_action.id, conversion_action.type,
                       conversion_action.primary_for_goal FROM conversion_action""")
chk(len(convs) == 3, "conversion action count is 3, none to duplicate", str(len(convs)))
states = {str(x.conversion_action.id): x.conversion_action.primary_for_goal for x in convs}
chk(states.get("7773013199") is True, "7773013199 PRIMARY")
chk(states.get("7773043879") is False, "7773043879 still SECONDARY")
goals = {(E(x.campaign_conversion_goal.category), E(x.campaign_conversion_goal.origin)):
         x.campaign_conversion_goal.biddable
         for x in q(c, """SELECT campaign_conversion_goal.category,
                                 campaign_conversion_goal.origin,
                                 campaign_conversion_goal.biddable
                          FROM campaign_conversion_goal""")}
chk(goals.get(("PHONE_CALL_LEAD", "CALL_FROM_ADS")) is True, "ad-call goal biddable true")
chk(goals.get(("PHONE_CALL_LEAD", "WEBSITE")) is False, "website-call goal still non-biddable")
camp = q(c, "SELECT campaign.id, campaign.status FROM campaign")
chk(len(camp) == 1 and str(camp[0].campaign.id) == "24257151015",
    "exactly one campaign, 24257151015")
chk(E(camp[0].campaign.status) == "PAUSED", "campaign PAUSED", E(camp[0].campaign.status))

print("\n" + "=" * 78 + "\n3. PLAN CONTENT / PHONE NUMBER RED TEAM\n" + "=" * 78)
chk(d["plan_id"] == "APG-0917-CALL-Q", "plan_id", d["plan_id"])
o1 = d["objects"][0]
chk(o1["field_values"]["call_asset.phone_number"] == WANT_PHONE, "asset phone is 4025265754",
    o1["field_values"]["call_asset.phone_number"])
chk(re.fullmatch(r"\d{10}", o1["field_values"]["call_asset.phone_number"]) is not None,
    "phone is 10 raw digits")
hits = [f for f in FORBIDDEN if f in raw]
chk(not hits, "forwarding destination appears NOWHERE in the plan file", str(hits))
digits_in_plan = (set(re.findall(r"\b\d{10}\b", raw))
                  | set(re.findall(r"\b\d{3}-\d{3}-\d{4}\b", raw)))
phone_like = {x for x in digits_in_plan if x.replace("-", "").startswith("402")}
chk(phone_like == {WANT_PHONE, "402-526-5754"},
    "402-prefixed numbers in the plan are only the approved one", str(sorted(phone_like)))
chk(o1["field_values"]["call_asset.call_conversion_reporting_state"]
    == "USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION", "resource-level reporting")
chk(o1["field_values"]["call_asset.call_conversion_action"].endswith("/7773013199"),
    "conversion action 7773013199")
sched = o1["ad_schedule_targets"]
chk(len(sched) == 6, "6 schedule targets")
chk(all(s["day_of_week"] != "SUNDAY" for s in sched), "SUNDAY absent")
chk(all(s["start_hour"] == 8 and s["end_hour"] == 17
        for s in sched if s["day_of_week"] != "SATURDAY"), "Mon-Fri 08:00-17:00")
sat = [s for s in sched if s["day_of_week"] == "SATURDAY"][0]
chk(sat["start_hour"] == 8 and sat["end_hour"] == 12, "Sat 08:00-12:00")
chk(len({s["day_of_week"] for s in sched}) == 6, "no duplicate day")
o2 = d["objects"][1]
chk(o2["field_type"] == "CALL" and o2["status"] == "ENABLED", "CALL link ENABLED")
chk(o2["campaign"].endswith("/24257151015"), "link targets 24257151015")
ms = d["mutation_summary"]
chk(ms["total_mutations"] == 2 and ms["creates"] == 2, "2 mutations, both creates")
for k in ("deletes", "campaign_enables", "budgets_touched", "conversion_actions_touched",
          "conversion_actions_created", "gtm_objects_touched", "whatconverts_changes",
          "wordpress_changes", "account_settings_touched"):
    chk(ms[k] == 0, f"mutation_summary.{k} == 0")
chk(d["target"]["campaign_status_after_this_plan"] == "PAUSED", "campaign stays PAUSED")
chk(d["supersedes"][0]["fingerprint"] == "A29431412E96"
    and d["supersedes"][0]["status"] == "SUPERSEDED_WRONG_PHONE", "supersedes CALL-N correctly")
keyhits = [k for k in re.findall(r"^\s*([A-Za-z0-9_.-]+):", raw, re.M)
           if SECRET_KEY_PATTERN.search(k)]
chk(not keyhits, "no key trips SECRET_KEY_PATTERN", str(keyhits))

print("\n" + "=" * 78 + "\n4. validate_only DRY RUN, EXACT CORRECTED PAYLOAD\n" + "=" * 78)
op = c.get_type("AssetOperation")
a = op.create
a.call_asset.country_code = "US"
a.call_asset.phone_number = WANT_PHONE
a.call_asset.call_conversion_reporting_state = (
    c.enums.CallConversionReportingStateEnum.USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION)
a.call_asset.call_conversion_action = f"customers/{CID}/conversionActions/7773013199"
for s in sched:
    t = c.get_type("AdScheduleInfo")
    t.day_of_week = c.enums.DayOfWeekEnum[s["day_of_week"]]
    t.start_hour = s["start_hour"]
    t.end_hour = s["end_hour"]
    t.start_minute = c.enums.MinuteOfHourEnum[s["start_minute"]]
    t.end_minute = c.enums.MinuteOfHourEnum[s["end_minute"]]
    a.call_asset.ad_schedule_targets.append(t)

payload = str(op)
flat = payload.replace("-", "").replace("+1", "")
chk(WANT_PHONE in payload, "payload contains 4025265754")
chk(not any(f.replace("-", "").replace("+1", "") in flat for f in FORBIDDEN),
    "payload contains NO forwarding destination")

req = c.get_type("MutateAssetsRequest")
req.customer_id = CID
req.operations.append(op)
req.validate_only = True
try:
    c.get_service("AssetService").mutate_assets(request=req)
    chk(True, "validate_only ACCEPTED the exact corrected payload")
except Exception as exc:  # noqa: BLE001
    msgs = []
    f = getattr(exc, "failure", None)
    if f:
        for e in f.errors:
            loc = ".".join(x.field_name for x in e.location.field_path_elements) \
                if e.location and e.location.field_path_elements else ""
            msgs.append(f"{e.message} @ '{loc}'")
    chk(False, "validate_only ACCEPTED the exact corrected payload",
        " | ".join(msgs) or str(exc)[:300])
print("  [INFO] nothing was created; validate_only = True")
print("\n  --- exact payload ---")
for line in payload.strip().splitlines():
    print("      " + line)

print("\n" + "=" * 78 + "\n5. FINGERPRINT\n" + "=" * 78)
fp = approval_code(d)
prior = {"9BA1F4AE3CCA", "D1CAB205DDDA", "849EAED2873F", "7BC3407302B2", "F0C6FA2128A9",
         "136E939A3206", "4022CBA7FD51", "5993F8998BCF", "FEB175ADDEEA", "C52D14071B08",
         "FC0E0B156F60", "DB9391A883A7", "2871DD2A5227", "A29431412E96", "B3C69A1E65C8"}
chk(fp not in prior, "fingerprint does not collide with any prior plan", fp)
chk(fp != "A29431412E96", "fingerprint differs from the rejected CALL-N")

print("\n" + "=" * 78)
if fails:
    print(f"RESULT: {len(fails)} FAILURES")
    for f in fails:
        print("   - " + f)
    sys.exit(1)
print("RESULT: 0 FAILURES")
print(f"\n  APPROVE APG CALL-ASSET {fp}\n")
print("=" * 78)
