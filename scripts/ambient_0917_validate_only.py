#!/usr/bin/env python3
"""Ambient | 2026-09-17 | validate_only for AMB-0917-HEAT-CREATE-1. Nothing is created."""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.safety import approval_code

TOPIC = re.compile(r'topic: "([A-Z_]+)"')
c = client(); identity_gate(c, verbose=False)
plan = json.loads((PLANS / "AMB-0917-HEAT-CREATE-1.json").read_text(encoding="utf-8"))
fp = plan.pop("fingerprint"); re_fp = approval_code(plan); plan["fingerprint"] = fp
print(f"fingerprint on disk = {fp}")
print(f"recomputed          = {re_fp}")
print(f"MATCH               = {fp == re_fp}")
assert fp == re_fp, "FINGERPRINT MISMATCH"

res = {"plan": "AMB-0917-HEAT-CREATE-1", "fingerprint": fp,
       "when": datetime.datetime.now(TZ).isoformat(), "validate_only": True,
       "nothing_created": True, "checks": {}}

print("\n=== 1. CAMPAIGN BUDGETS ===")
bops = []
for key, cm in plan["campaigns"].items():
    o = c.get_type("CampaignBudgetOperation"); b = o.create
    b.name = f"Budget | {cm['name']}"
    b.amount_micros = int(cm["daily_budget"] * 1e6)
    b.explicitly_shared = False
    b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
    bops.append(o)
req = c.get_type("MutateCampaignBudgetsRequest")
req.customer_id = CID; req.operations.extend(bops); req.validate_only = True
try:
    c.get_service("CampaignBudgetService").mutate_campaign_budgets(request=req)
    print(f"  VALIDATED_OK - {len(bops)} budgets, not shared, STANDARD delivery")
    res["checks"]["campaign_budgets"] = "VALIDATED_OK"
except Exception as ex:
    print(f"  FAILED: {str(ex)[:500]}")
    res["checks"]["campaign_budgets"] = f"FAILED: {str(ex)[:300]}"

print("\n=== 2. RSA PAYLOADS (text, pins, paths, final URLs, destination policy) ===")
agrn = c.get_service("AdGroupService").ad_group_path(CID, "199748801029")
ops = []
for o in plan["operations"]:
    if o["op"] != "CREATE_RSA_PAUSED":
        continue
    op = c.get_type("AdGroupAdOperation"); a = op.create
    a.ad_group = agrn
    a.status = c.enums.AdGroupAdStatusEnum.PAUSED
    a.ad.final_urls.append(o["final_url"])
    r = a.ad.responsive_search_ad
    r.path1, r.path2 = o["path1"], o["path2"]
    for h in o["headlines_pinned_h1"]:
        t = c.get_type("AdTextAsset"); t.text = h
        t.pinned_field = c.enums.ServedAssetFieldTypeEnum.HEADLINE_1
        r.headlines.append(t)
    for h in o["headlines_unpinned"]:
        t = c.get_type("AdTextAsset"); t.text = h; r.headlines.append(t)
    for d in o["descriptions"]:
        t = c.get_type("AdTextAsset"); t.text = d; r.descriptions.append(t)
    ops.append(op)
print(f"  built {len(ops)} RSA operations from the plan")
req2 = c.get_type("MutateAdGroupAdsRequest")
req2.customer_id = CID; req2.operations.extend(ops)
req2.partial_failure = False; req2.validate_only = True
try:
    c.get_service("AdGroupAdService").mutate_ad_group_ads(request=req2)
    print(f"  VALIDATED_OK - all {len(ops)} RSAs accepted, nothing created")
    res["checks"]["rsas"] = f"VALIDATED_OK ({len(ops)})"
except Exception as ex:
    t = sorted(set(TOPIC.findall(str(ex))))
    print(f"  FAILED - policy topics: {t}")
    print(str(ex)[:500])
    res["checks"]["rsas"] = f"FAILED topics={t}"

print("\n=== 3. FINAL-URL DESTINATION POLICY, PER URL ===")
urls = sorted({o["final_url"] for o in plan["operations"] if o.get("final_url")})
for u in urls:
    op = c.get_type("AdGroupAdOperation"); a = op.create
    a.ad_group = agrn; a.status = c.enums.AdGroupAdStatusEnum.PAUSED
    a.ad.final_urls.append(u)
    r = a.ad.responsive_search_ad
    for h in ["Heating Service Central MD", "Maryland HVAC Technicians", "Book a Service Visit"]:
        t = c.get_type("AdTextAsset"); t.text = h; r.headlines.append(t)
    for d in ["Heating service for homes and businesses across Central Maryland.",
              "Our technicians diagnose the issue and explain the options clearly."]:
        t = c.get_type("AdTextAsset"); t.text = d; r.descriptions.append(t)
    rq = c.get_type("MutateAdGroupAdsRequest")
    rq.customer_id = CID; rq.operations.append(op); rq.validate_only = True
    try:
        c.get_service("AdGroupAdService").mutate_ad_group_ads(request=rq)
        print(f"  OK        {u}")
        res["checks"].setdefault("final_urls", {})[u] = "OK"
    except Exception as ex:
        t = sorted(set(TOPIC.findall(str(ex))))
        print(f"  REJECTED  {u}  topics={t}")
        res["checks"].setdefault("final_urls", {})[u] = f"REJECTED {t}"

print("\n=== 4. KEYWORD TEXT VALIDITY ===")
kops = []
for o in plan["operations"]:
    if o["op"] != "ADD_KEYWORDS_PAUSED":
        continue
    for txt in o["phrase"]:
        k = c.get_type("AdGroupCriterionOperation"); x = k.create
        x.ad_group = agrn
        x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
        x.keyword.text = txt
        x.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
        kops.append(k)
    for txt in o["exact"]:
        k = c.get_type("AdGroupCriterionOperation"); x = k.create
        x.ad_group = agrn
        x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
        x.keyword.text = txt
        x.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT
        kops.append(k)
req3 = c.get_type("MutateAdGroupCriteriaRequest")
req3.customer_id = CID; req3.operations.extend(kops)
req3.partial_failure = False; req3.validate_only = True
try:
    c.get_service("AdGroupCriterionService").mutate_ad_group_criteria(request=req3)
    print(f"  VALIDATED_OK - {len(kops)} keywords accepted, nothing created")
    res["checks"]["keywords"] = f"VALIDATED_OK ({len(kops)})"
except Exception as ex:
    print(f"  FAILED: {str(ex)[:500]}")
    res["checks"]["keywords"] = f"FAILED: {str(ex)[:300]}"

VRECEIPTS.mkdir(parents=True, exist_ok=True)
p = VRECEIPTS / "AMB-0917-HEAT-CREATE-1-2026-09-17.json"
p.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p}")
print(f"\nAPPROVE AMB-0917-HEAT-CREATE-1 {fp} {plan['operation_count']} operations FOR {CID}")
print("NOTHING WAS CREATED. EXTERNAL WRITES: 0")
