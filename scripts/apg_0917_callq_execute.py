#!/usr/bin/env python3
"""EXECUTE APG-0917-CALL-Q, fingerprint E3214C210910.

Approval 2026-09-17: "APPROVE APG CALL-ASSET E3214C210910"

2 creates: a CALL asset carrying 402-526-5754, then its CampaignAsset link on
PAUSED campaign 24257151015. Nothing else is touched and nothing is enabled.
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EXACT_NAME, GM_MANAGER, TZ, RECEIPTS, client, q, write, E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

PLAN = ROOT / "clients/apogee-lawns/plans/APG-0917-CALL-Q.yaml"
EXPECTED_FP = "E3214C210910"
CAMPAIGN_ID = "24257151015"
CONV_ACTION = f"customers/{CID}/conversionActions/7773013199"
WANT_PHONE = "4025265754"
FORBIDDEN = ("4022027261", "402-202-7261", "+14022027261")

c = client()
fails = []
created = []


def gate(ok, label, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' -> ' + detail) if detail else ''}")
    if not ok:
        fails.append(label)


# ------------------------------------------------------------------ GATE
print("=" * 78 + "\nGATE\n" + "=" * 78)
plan = load_yaml(str(PLAN))
fp = approval_code(plan)
gate(fp == EXPECTED_FP, "CALL-Q fingerprint matches the approval line", fp)
gate(plan["plan_id"] == "APG-0917-CALL-Q", "plan_id", plan["plan_id"])
raw = PLAN.read_text(encoding="utf-8")
gate(not [f for f in FORBIDDEN if f in raw], "forwarding destination absent from the plan file")

cust = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
                      customer.test_account, customer.status, customer.time_zone,
                      customer.call_reporting_setting.call_reporting_enabled,
                      customer.call_reporting_setting.call_conversion_reporting_enabled,
                      customer.call_reporting_setting.call_conversion_action
               FROM customer""")[0].customer
gate(str(cust.id) == CID, "customer.id", str(cust.id))
gate(cust.descriptive_name == EXACT_NAME, "descriptive_name", cust.descriptive_name)
gate(not cust.manager and not cust.test_account, "not manager / not test")
gate(cust.time_zone == "America/Chicago", "time zone is account Central", cust.time_zone)
gate(cust.call_reporting_setting.call_reporting_enabled, "call reporting enabled")
gate(cust.call_reporting_setting.call_conversion_reporting_enabled,
     "call conversion reporting enabled")
stale_pointer = cust.call_reporting_setting.call_conversion_action
print(f"  [INFO] account-level call_conversion_action = '{stale_pointer}' (stale, left untouched)")

links = {x.customer_manager_link.manager_customer.split("/")[-1]: E(x.customer_manager_link.status)
         for x in q(c, """SELECT customer_manager_link.manager_customer,
                                 customer_manager_link.status FROM customer_manager_link""")}
gate(links.get(GM_MANAGER) == "ACTIVE", f"manager {GM_MANAGER} ACTIVE, never mutated")

print("\n  -- duplicate guard --")
pre_call_assets = q(c, "SELECT asset.id FROM asset WHERE asset.type = 'CALL'")
gate(len(pre_call_assets) == 0, "zero pre-existing CALL assets", str(len(pre_call_assets)))
pre_links = q(c, "SELECT campaign_asset.field_type FROM campaign_asset")
pre_call_links = sum(1 for x in pre_links if E(x.campaign_asset.field_type) == "CALL")
gate(pre_call_links == 0, "zero pre-existing CALL links", str(pre_call_links))
gate(len(pre_links) == 7, "7 pre-existing campaign_asset links", str(len(pre_links)))

print("\n  -- preconditions --")
camps = [(str(x.campaign.id), E(x.campaign.status))
         for x in q(c, "SELECT campaign.id, campaign.status FROM campaign")]
gate(camps == [(CAMPAIGN_ID, "PAUSED")], f"campaign {CAMPAIGN_ID} exists and is PAUSED", str(camps))
convs = {}
for x in q(c, """SELECT conversion_action.id, conversion_action.status, conversion_action.type,
                        conversion_action.category, conversion_action.origin,
                        conversion_action.primary_for_goal FROM conversion_action"""):
    a = x.conversion_action
    convs[str(a.id)] = {"status": E(a.status), "type": E(a.type_), "category": E(a.category),
                        "origin": E(a.origin), "primary_for_goal": a.primary_for_goal}
gate(len(convs) == 3, "exactly 3 conversion actions", str(len(convs)))
t = convs.get("7773013199", {})
gate(t.get("status") == "ENABLED" and t.get("type") == "AD_CALL"
     and t.get("category") == "PHONE_CALL_LEAD" and t.get("origin") == "CALL_FROM_ADS"
     and t.get("primary_for_goal") is True, "7773013199 ENABLED AD_CALL PHONE_CALL_LEAD CALL_FROM_ADS PRIMARY")
gate(convs.get("7773043879", {}).get("primary_for_goal") is False, "7773043879 still SECONDARY")
goals = {f"{E(x.campaign_conversion_goal.category)}/{E(x.campaign_conversion_goal.origin)}":
         x.campaign_conversion_goal.biddable
         for x in q(c, """SELECT campaign_conversion_goal.category,
                                 campaign_conversion_goal.origin,
                                 campaign_conversion_goal.biddable
                          FROM campaign_conversion_goal""")}
gate(goals.get("PHONE_CALL_LEAD/CALL_FROM_ADS") is True, "ad-call goal biddable")
gate(goals.get("PHONE_CALL_LEAD/WEBSITE") is False, "website-call goal non-biddable")
gate(len(q(c, "SELECT custom_conversion_goal.id FROM custom_conversion_goal")) == 0,
     "zero custom conversion goals")

if fails:
    sys.exit("\nHARD STOP, nothing was issued: " + "; ".join(fails))
print("\nALL GATES PASS. Issuing exactly 2 create operations.\n")


def err(exc):
    out = []
    f = getattr(exc, "failure", None)
    if f:
        for e in f.errors:
            loc = ".".join(x.field_name for x in e.location.field_path_elements) \
                if e.location and e.location.field_path_elements else ""
            out.append(f"{e.message} @ '{loc}'")
    return " | ".join(out) or str(exc)[:400]


# ------------------------------------------------------- 1. CALL ASSET
sched_plan = plan["objects"][0]["ad_schedule_targets"]
op = c.get_type("AssetOperation")
a = op.create
a.call_asset.country_code = "US"
a.call_asset.phone_number = WANT_PHONE
a.call_asset.call_conversion_reporting_state = (
    c.enums.CallConversionReportingStateEnum.USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION)
a.call_asset.call_conversion_action = CONV_ACTION
for s in sched_plan:
    t = c.get_type("AdScheduleInfo")
    t.day_of_week = c.enums.DayOfWeekEnum[s["day_of_week"]]
    t.start_hour = s["start_hour"]
    t.end_hour = s["end_hour"]
    t.start_minute = c.enums.MinuteOfHourEnum[s["start_minute"]]
    t.end_minute = c.enums.MinuteOfHourEnum[s["end_minute"]]
    a.call_asset.ad_schedule_targets.append(t)

payload = str(op)
flat = payload.replace("-", "").replace("+1", "")
if WANT_PHONE not in payload or any(f.replace("-", "").replace("+1", "") in flat for f in FORBIDDEN):
    sys.exit("HARD STOP: payload phone-number check failed before send.")

print(f"--- 1/2 creating CALL asset, phone {WANT_PHONE}, 6 schedule targets")
req = c.get_type("MutateAssetsRequest")
req.customer_id = CID
req.operations.append(op)
try:
    resp = c.get_service("AssetService").mutate_assets(request=req)
    asset_rn = resp.results[0].resource_name
    asset_id = asset_rn.split("/")[-1]
    created.append({"resource": "asset", "resource_name": asset_rn, "id": asset_id})
    print(f"    CREATED {asset_rn}")
except Exception as exc:  # noqa: BLE001
    msg = err(exc)
    print(f"    FAILED: {msg}")
    write(RECEIPTS / "2026-09-17-callq-FAILURE.json",
          {"stage": "asset", "error": msg, "created": created,
           "when": datetime.datetime.now(TZ).isoformat()})
    sys.exit(2)

# --------------------------------------------- 2. CAMPAIGN ASSET LINK
print(f"--- 2/2 linking asset {asset_id} to campaign {CAMPAIGN_ID} as field_type CALL")
cop = c.get_type("CampaignAssetOperation")
ca = cop.create
ca.campaign = f"customers/{CID}/campaigns/{CAMPAIGN_ID}"
ca.asset = asset_rn
ca.field_type = c.enums.AssetFieldTypeEnum.CALL
ca.status = c.enums.AssetLinkStatusEnum.ENABLED
creq = c.get_type("MutateCampaignAssetsRequest")
creq.customer_id = CID
creq.operations.append(cop)
try:
    cresp = c.get_service("CampaignAssetService").mutate_campaign_assets(request=creq)
    link_rn = cresp.results[0].resource_name
    created.append({"resource": "campaign_asset", "resource_name": link_rn})
    print(f"    CREATED {link_rn}")
except Exception as exc:  # noqa: BLE001
    msg = err(exc)
    print(f"    FAILED: {msg}")
    print("\n  PARTIAL SUCCESS. The asset exists but is NOT linked. Do not rerun blindly.")
    write(RECEIPTS / "2026-09-17-callq-FAILURE.json",
          {"stage": "campaign_asset", "error": msg, "created": created,
           "recovery": f"asset {asset_id} exists unlinked; link it or remove it deliberately",
           "when": datetime.datetime.now(TZ).isoformat()})
    sys.exit(2)

# ------------------------------------------------------------- READBACK
print("\n" + "=" * 78 + "\nREADBACK\n" + "=" * 78)
qa = []


def assert_(ok, label, detail=""):
    qa.append({"check": label, "pass": bool(ok), "detail": detail})
    print(f"  [{'OK  ' if ok else 'FAIL'}] {label}{(' -> ' + detail) if detail else ''}")


rows = q(c, """SELECT asset.id, asset.resource_name, asset.type,
                      asset.call_asset.country_code, asset.call_asset.phone_number,
                      asset.call_asset.call_conversion_reporting_state,
                      asset.call_asset.call_conversion_action,
                      asset.call_asset.ad_schedule_targets
               FROM asset WHERE asset.type = 'CALL'""")
assert_(len(rows) == 1, "exactly 1 CALL asset exists", str(len(rows)))
ca_read = rows[0].asset.call_asset
digits = re.sub(r"\D", "", ca_read.phone_number)
assert_(rows[0].asset.type_.name == "CALL", "asset.type == CALL")
assert_(ca_read.country_code == "US", "country_code == US", ca_read.country_code)
assert_(digits == WANT_PHONE, "phone digits == 4025265754", f"{ca_read.phone_number} -> {digits}")
assert_(WANT_PHONE not in (x for x in FORBIDDEN) and digits not in FORBIDDEN,
        "phone is NOT the forwarding destination")
assert_(E(ca_read.call_conversion_reporting_state) == "USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION",
        "reporting state resource-level", E(ca_read.call_conversion_reporting_state))
assert_(ca_read.call_conversion_action.endswith("/7773013199"),
        "call_conversion_action -> 7773013199", ca_read.call_conversion_action)

got_sched = sorted((E(s.day_of_week), s.start_hour, E(s.start_minute), s.end_hour, E(s.end_minute))
                   for s in ca_read.ad_schedule_targets)
want_sched = sorted((s["day_of_week"], s["start_hour"], s["start_minute"],
                     s["end_hour"], s["end_minute"]) for s in sched_plan)
assert_(len(got_sched) == 6, "6 ad-schedule targets", str(len(got_sched)))
assert_(got_sched == want_sched, "schedule matches the plan exactly")
assert_(all(d != "SUNDAY" for d, *_ in got_sched), "SUNDAY absent")
for row in got_sched:
    print(f"        {row[0]:<10} {row[1]:02d}:00 -> {row[3]:02d}:00")

lrows = q(c, """SELECT campaign_asset.campaign, campaign_asset.asset,
                       campaign_asset.field_type, campaign_asset.status,
                       campaign_asset.source FROM campaign_asset""")
call_links = [x for x in lrows if E(x.campaign_asset.field_type) == "CALL"]
assert_(len(call_links) == 1, "exactly 1 CALL link", str(len(call_links)))
lk = call_links[0].campaign_asset
assert_(lk.campaign.endswith(f"/{CAMPAIGN_ID}"), f"link campaign == {CAMPAIGN_ID}", lk.campaign)
assert_(lk.asset == asset_rn, "link points at the asset just created")
assert_(E(lk.status) == "ENABLED", "link status ENABLED", E(lk.status))
assert_(len(lrows) == 8, "total campaign_asset links == 8", str(len(lrows)))
assert_(sum(1 for x in lrows if E(x.campaign_asset.field_type) == "CALLOUT") == 6,
        "6 callout links unchanged")
assert_(sum(1 for x in lrows if E(x.campaign_asset.field_type) == "STRUCTURED_SNIPPET") == 1,
        "1 snippet link unchanged")

print("\n  -- invariants --")
after_camps = [(str(x.campaign.id), E(x.campaign.status))
               for x in q(c, "SELECT campaign.id, campaign.status FROM campaign")]
assert_(after_camps == [(CAMPAIGN_ID, "PAUSED")], "campaign still PAUSED, still the only one",
        str(after_camps))
bud = q(c, "SELECT campaign_budget.id, campaign_budget.amount_micros FROM campaign_budget")
assert_(len(bud) == 1 and bud[0].campaign_budget.amount_micros == 16440000,
        "budget unchanged at 16,440,000 micros",
        str(bud[0].campaign_budget.amount_micros) if bud else "none")
after_convs = {}
for x in q(c, """SELECT conversion_action.id, conversion_action.primary_for_goal,
                        conversion_action.status, conversion_action.type
                 FROM conversion_action"""):
    aa = x.conversion_action
    after_convs[str(aa.id)] = {"primary_for_goal": aa.primary_for_goal,
                               "status": E(aa.status), "type": E(aa.type_)}
assert_(len(after_convs) == 3, "conversion action count still 3, none created")
assert_(after_convs["7772803337"]["primary_for_goal"] is True, "7772803337 still PRIMARY")
assert_(after_convs["7773013199"]["primary_for_goal"] is True, "7773013199 still PRIMARY")
assert_(after_convs["7773043879"]["primary_for_goal"] is False, "7773043879 still SECONDARY")
after_goals = {f"{E(x.campaign_conversion_goal.category)}/{E(x.campaign_conversion_goal.origin)}":
               x.campaign_conversion_goal.biddable
               for x in q(c, """SELECT campaign_conversion_goal.category,
                                       campaign_conversion_goal.origin,
                                       campaign_conversion_goal.biddable
                                FROM campaign_conversion_goal""")}
assert_(after_goals == goals, "campaign conversion goals unchanged", str(after_goals))
assert_(len(q(c, "SELECT custom_conversion_goal.id FROM custom_conversion_goal")) == 0,
        "still 0 custom conversion goals")
n_sched_crit = len(q(c, """SELECT campaign_criterion.criterion_id FROM campaign_criterion
                           WHERE campaign_criterion.type = 'AD_SCHEDULE'"""))
assert_(n_sched_crit == 0, "campaign still has 0 ad-schedule criteria (24/7)", str(n_sched_crit))
n_crit = len(q(c, "SELECT campaign_criterion.criterion_id FROM campaign_criterion"))
assert_(n_crit == 90, "90 campaign criteria unchanged", str(n_crit))
n_ads = len(q(c, "SELECT ad_group_ad.ad.id FROM ad_group_ad"))
assert_(n_ads == 4, "4 RSAs unchanged", str(n_ads))
n_kw = len(q(c, """SELECT ad_group_criterion.criterion_id FROM ad_group_criterion
                   WHERE ad_group_criterion.type = 'KEYWORD'"""))
assert_(n_kw == 5, "5 keywords unchanged", str(n_kw))
after_pointer = q(c, """SELECT customer.call_reporting_setting.call_conversion_action
                        FROM customer""")[0].customer.call_reporting_setting.call_conversion_action
assert_(after_pointer == stale_pointer, "stale account-level pointer left untouched", after_pointer)
after_links = {x.customer_manager_link.manager_customer.split("/")[-1]:
               E(x.customer_manager_link.status)
               for x in q(c, """SELECT customer_manager_link.manager_customer,
                                       customer_manager_link.status
                                FROM customer_manager_link""")}
assert_(after_links.get(GM_MANAGER) == "ACTIVE", "manager link untouched")

n_fail = sum(1 for x in qa if not x["pass"])
print("\n" + "=" * 78)
print(f"CALL-Q RESULT: {n_fail} readback failures")
print("=" * 78)

write(RECEIPTS / "2026-09-17-callq-receipt.json", {
    "plan_id": "APG-0917-CALL-Q", "fingerprint": EXPECTED_FP,
    "approval": f"APPROVE APG CALL-ASSET {EXPECTED_FP}",
    "supersedes": {"plan_id": "APG-0917-CALL-N", "fingerprint": "A29431412E96",
                   "status": "SUPERSEDED_WRONG_PHONE"},
    "executed_local": datetime.datetime.now(TZ).isoformat(),
    "customer_id": CID, "account_name": EXACT_NAME, "campaign_id": CAMPAIGN_ID,
    "mutations": 2, "creates": 2, "updates": 0, "deletes": 0,
    "created": created,
    "call_asset": {
        "id": asset_id, "resource_name": asset_rn, "country_code": ca_read.country_code,
        "phone_number": ca_read.phone_number, "phone_digits": digits,
        "call_conversion_reporting_state": E(ca_read.call_conversion_reporting_state),
        "call_conversion_action": ca_read.call_conversion_action,
        "ad_schedule_targets": [{"day_of_week": d, "start_hour": sh, "start_minute": sm,
                                 "end_hour": eh, "end_minute": em}
                                for d, sh, sm, eh, em in got_sched]},
    "campaign_asset": {"resource_name": link_rn, "campaign": lk.campaign,
                       "asset": lk.asset, "field_type": E(lk.field_type),
                       "status": E(lk.status)},
    "campaign_status_after": after_camps,
    "conversion_actions_after": after_convs,
    "campaign_conversion_goals_after": after_goals,
    "stale_account_pointer_before": stale_pointer,
    "stale_account_pointer_after": after_pointer,
    "readback": qa, "qa_failures": n_fail,
    "campaign_enabled": False, "budget_changed": False, "deletes": 0,
})
print("Receipt: receipts/2026-09-17-callq-receipt.json")
print("CALL-Q COMPLETE." if n_fail == 0 else "CALL-Q COMPLETE WITH FAILURES.")
sys.exit(1 if n_fail else 0)
