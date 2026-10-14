#!/usr/bin/env python3
"""Ambient | 2026-09-17 | SUPPLEMENTAL READBACK of AMB-0917-HEAT-CREATE-1.

Covers the readback items the first pass did not: AI Max, broad-match expansion,
Final URL expansion / automatically created assets (both now live under
campaign.asset_automation_settings in v25), optimization goals, keyword policy
eligibility, and RSA policy detail. Read-only.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-17"
LIVE = ROOT / "receipts" / "live"
out = {"plan": "AMB-0917-HEAT-CREATE-1", "when": datetime.datetime.now(TZ).isoformat(),
       "read_only": True, "external_writes": 0, "assertions": []}
P = F = 0


def chk(label, ok, detail=""):
    global P, F
    P, F = (P + 1, F) if ok else (P, F + 1)
    out["assertions"].append({"check": label, "result": "PASS" if ok else "FAIL",
                              "detail": str(detail)[:400]})
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  -- {detail}" if detail else ""))


c = client()
row = q(c, "SELECT customer.id, customer.descriptive_name FROM customer")[0].customer
assert row.descriptive_name == EXACT_NAME and str(row.id) == CID
rcpt = json.loads((LIVE / f"AMB-0917-HEAT-CREATE-1-{STAMP}.json").read_text(encoding="utf-8"))
com = rcpt["committed"]
cid_of = {k: v.rsplit("/", 1)[1] for k, v in com["campaigns"].items()}
agid_of = {k: v.rsplit("/", 1)[1] for k, v in com["ad_groups"].items()}
IDS = "', '".join(cid_of.values())
AGIDS = "', '".join(agid_of.values())
print(f"identity: {row.descriptive_name} / {row.id}\n")

print("=== 10. AUTOMATION / EXPANSION SETTINGS (campaign) ===")
for r in q(c, f"""
    SELECT campaign.id, campaign.name, campaign.ai_max_setting.enable_ai_max,
           campaign.ai_max_setting.bundling_required, campaign.keyword_match_type,
           campaign.asset_automation_settings,
           campaign.optimization_goal_setting.optimization_goal_types,
           campaign.excluded_parent_asset_field_types, campaign.primary_status
    FROM campaign WHERE campaign.id IN ('{IDS}')"""):
    x = r.campaign
    key = [k for k, v in cid_of.items() if v == str(x.id)][0]
    chk(f"{key} AI Max OFF", x.ai_max_setting.enable_ai_max is False,
        x.ai_max_setting.enable_ai_max)
    # bundling_required is an ENUM, not a bool. 21 of the 23 pre-existing campaigns
    # read UNSPECIFIED; comparing it to False can never pass.
    chk(f"{key} AI Max bundling UNSPECIFIED",
        E(x.ai_max_setting.bundling_required) in ("UNSPECIFIED", "UNKNOWN"),
        E(x.ai_max_setting.bundling_required))
    chk(f"{key} broad-match keyword setting not opted in",
        E(x.keyword_match_type) in ("UNSPECIFIED", "UNKNOWN"), E(x.keyword_match_type))
    aas = {E(a.asset_automation_type): E(a.asset_automation_status)
           for a in x.asset_automation_settings}
    # Final URL expansion and automatically created assets both live here in v25.
    bad = {k: v for k, v in aas.items() if v == "OPTED_IN"}
    chk(f"{key} no asset automation opted in "
        f"(Final URL expansion + auto-created assets)", not bad, aas or "none set")
    chk(f"{key} no optimization goal types set",
        len(x.optimization_goal_setting.optimization_goal_types) == 0,
        [E(g) for g in x.optimization_goal_setting.optimization_goal_types])
    chk(f"{key} primary_status PAUSED (cannot serve)", E(x.primary_status) == "PAUSED",
        E(x.primary_status))

print("\n=== 11. AD GROUP SERVING + AI MAX ===")
for r in q(c, f"""
    SELECT ad_group.id, ad_group.name, ad_group.status,
           ad_group.ai_max_ad_group_setting.disable_search_term_matching,
           ad_group.primary_status, ad_group.excluded_parent_asset_field_types
    FROM ad_group WHERE ad_group.id IN ('{AGIDS}')"""):
    a = r.ad_group
    chk(f"{a.name} primary_status not ELIGIBLE", E(a.primary_status) != "ELIGIBLE",
        E(a.primary_status))
    chk(f"{a.name} status PAUSED", E(a.status) == "PAUSED", E(a.status))

print("\n=== 12. KEYWORD POLICY ELIGIBILITY (18) ===")
kws = list(q(c, f"""
    SELECT ad_group.name, ad_group_criterion.keyword.text,
           ad_group_criterion.keyword.match_type, ad_group_criterion.status,
           ad_group_criterion.approval_status, ad_group_criterion.disapproval_reasons,
           ad_group_criterion.system_serving_status
    FROM ad_group_criterion WHERE ad_group.id IN ('{AGIDS}')
      AND ad_group_criterion.type = 'KEYWORD'
      AND ad_group_criterion.status != 'REMOVED'"""))
chk("18 keywords read back", len(kws) == 18, len(kws))
dis = [(r.ad_group_criterion.keyword.text,
        list(r.ad_group_criterion.disapproval_reasons)) for r in kws
       if E(r.ad_group_criterion.approval_status) == "DISAPPROVED"]
chk("no keyword DISAPPROVED", not dis, dis[:5])
by_status = {}
for r in kws:
    by_status.setdefault(E(r.ad_group_criterion.approval_status), []).append(
        r.ad_group_criterion.keyword.text)
for st, lst in sorted(by_status.items()):
    print(f"      approval_status {st}: {len(lst)}  e.g. {lst[:2]}")
out["keyword_approval_status"] = {k: len(v) for k, v in by_status.items()}
srv = {E(r.ad_group_criterion.system_serving_status) for r in kws}
print(f"      system_serving_status values: {sorted(srv)}")
out["keyword_system_serving_status"] = sorted(srv)
chk("no keyword RARELY_SERVED (low search volume)", "RARELY_SERVED" not in srv,
    sorted(srv))

print("\n=== 13. RSA POLICY DETAIL (4) ===")
ads = list(q(c, f"""
    SELECT ad_group.name, ad_group_ad.ad.id, ad_group_ad.status,
           ad_group_ad.policy_summary.approval_status,
           ad_group_ad.policy_summary.review_status,
           ad_group_ad.policy_summary.policy_topic_entries,
           ad_group_ad.ad_strength, ad_group_ad.primary_status
    FROM ad_group_ad WHERE ad_group.id IN ('{AGIDS}')
      AND ad_group_ad.status != 'REMOVED'"""))
chk("4 RSAs read back", len(ads) == 4, len(ads))
for r in ads:
    a = r.ad_group_ad
    topics = [t.topic for t in a.policy_summary.policy_topic_entries]
    print(f"      {a.ad.id}  approval={E(a.policy_summary.approval_status):12s} "
          f"review={E(a.policy_summary.review_status):18s} "
          f"strength={E(a.ad_strength):12s} primary={E(a.primary_status)}")
    chk(f"  RSA {a.ad.id} not DISAPPROVED",
        E(a.policy_summary.approval_status) != "DISAPPROVED",
        E(a.policy_summary.approval_status))
    chk(f"  RSA {a.ad.id} no destination policy topic",
        not any("DESTINATION" in t for t in topics), topics)
out["rsa_policy"] = [{"id": str(r.ad_group_ad.ad.id),
                      "approval": E(r.ad_group_ad.policy_summary.approval_status),
                      "review": E(r.ad_group_ad.policy_summary.review_status),
                      "topics": [t.topic for t in
                                 r.ad_group_ad.policy_summary.policy_topic_entries]}
                     for r in ads]

print("\n=== 14. NO UNINTENDED DUPLICATE ===")
for nm in [v["name"] for v in json.loads(
        (PLANS / "AMB-0917-HEAT-CREATE-1.json").read_text(encoding="utf-8"))
        ["campaigns"].values()]:
    n = len(q(c, f"""SELECT campaign.id FROM campaign WHERE campaign.name = '{nm}'
                     AND campaign.status != 'REMOVED'"""))
    chk(f"exactly one campaign named '{nm[:46]}...'", n == 1, n)
for nm in agid_of:
    n = len(q(c, f"""SELECT ad_group.id FROM ad_group WHERE ad_group.name = '{nm}'
                     AND ad_group.status != 'REMOVED'"""))
    chk(f"exactly one ad group named '{nm}'", n == 1, n)
PRE_EXISTING_ORPHANS = {"13433692985", "14810347898", "15044731597", "15466378777"}
orph = {str(b.campaign_budget.id): b.campaign_budget.name for b in q(c, """
    SELECT campaign_budget.id, campaign_budget.name
    FROM campaign_budget WHERE campaign_budget.reference_count = 0
      AND campaign_budget.status != 'REMOVED'""")}
new_orph = {k: v for k, v in orph.items() if k not in PRE_EXISTING_ORPHANS}
chk("the aborted first attempt left no orphaned budget "
    f"(4 pre-existing orphans untouched)", not new_orph, new_orph)
chk("both plan budgets are attached, not orphaned",
    not ({"15885327972", "15885327975"} & set(orph)), sorted(orph))

out["summary"] = {"pass": P, "fail": F, "total": P + F}
(LIVE / f"AMB-0917-HEAT-CREATE-1-{STAMP}-READBACK2.json").write_text(
    json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\n{'=' * 60}\nSUPPLEMENTAL READBACK: {P} PASS / {F} FAIL / {P + F} assertions")
print("EXTERNAL WRITES: 0")
