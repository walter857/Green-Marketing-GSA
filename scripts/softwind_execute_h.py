#!/usr/bin/env python3
"""Execute PLAN-H under exact approval.

APPROVED PHRASE: APPROVE PLAN-H 1D63EC1EB68D FOR 1521725229

21 mutations, in the plan's mandated order:
  H01  create 4 sitelink assets                          (4)
  H02  link the 4 new assets to campaign 24103511039     (4)
  H03  link the 4 new assets to campaign 24145053510     (4)
  --- verify 8 sitelinks live on each campaign BEFORE unlinking anything ---
  H04  remove the 8 old campaign_asset links             (8)
  H05  remove the 1 old customer_asset link              (1)

Order matters: link new, verify, then unlink old, so there is never a window
with zero sitelinks. No asset is deleted anywhere - links only.
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
sys.path.insert(0, str(ROOT / "scripts"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.safety import approval_code                     # noqa: E402
from softwind_preflight_h import normalize                  # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
NAME = "Softwind Power Washing - Live"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
NAMES = {CAMP_A: "Power Washing", CAMP_B: "Power Washing #2"}
APPROVED_FP = "1D63EC1EB68D"
CLIENT = ROOT / "clients/softwind-power-washing"
PLAN_FILE = CLIENT / "plans/2026-08-25-plan-h-sitelink-destinations.yaml"
OUT = CLIENT / "snapshots/h-execution-2026-08-27.json"

OLD_CAMPAIGN_ASSETS = ["404411414183", "404512529608", "404512534036",
                       "404582047221"]
OLD_CUSTOMER_ASSET = "403671792813"

# Structural baseline that must not move.
BASELINE = {"keywords": 214, "ads": 54, "campaign_negative_keywords": 94,
            "ad_schedules": 12, "conversion_actions": 4, "ad_groups": 30,
            "budget_A": 333330000, "budget_B": 41110000,
            "ceiling": 30000000}

log = {"approved_plan": "PLAN-H", "approved_fingerprint": APPROVED_FP,
       "approved_phrase": "APPROVE PLAN-H 1D63EC1EB68D FOR 1521725229"}
fail = False


def gate(label, ok, detail=""):
    global fail
    print("   [%s] %-54s %s" % ("PASS" if ok else "FAIL", label, detail))
    log.setdefault("gates", []).append({"gate": label, "pass": bool(ok),
                                        "detail": str(detail)})
    if not ok:
        fail = True
    return ok


def rows(svc, q):
    out = []
    for b in svc.search_stream(customer_id=CID, query=q):
        out.extend(b.results)
    return out


def sitelink_state(svc):
    q = ("SELECT campaign.id, campaign_asset.resource_name, asset.id, "
         "asset.sitelink_asset.link_text, asset.final_urls, campaign_asset.status "
         f"FROM campaign_asset WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND campaign_asset.field_type = 'SITELINK' "
         "AND campaign_asset.status != 'REMOVED'")
    camp = {}
    for x in rows(svc, q):
        camp.setdefault(str(x.campaign.id), {})[str(x.asset.id)] = {
            "resource_name": x.campaign_asset.resource_name,
            "link_text": x.asset.sitelink_asset.link_text,
            "final_urls": list(x.asset.final_urls),
            "status": x.campaign_asset.status.name}
    q = ("SELECT customer_asset.resource_name, asset.id, "
         "asset.sitelink_asset.link_text, asset.final_urls, customer_asset.status "
         "FROM customer_asset WHERE customer_asset.field_type = 'SITELINK' "
         "AND customer_asset.status != 'REMOVED'")
    cust = {str(x.asset.id): {"resource_name": x.customer_asset.resource_name,
                              "link_text": x.asset.sitelink_asset.link_text,
                              "final_urls": list(x.asset.final_urls),
                              "status": x.customer_asset.status.name}
            for x in rows(svc, q)}
    return {"campaign": camp, "customer": cust}


def counts(svc):
    def c(res, where):
        return len(rows(svc, "SELECT %s.resource_name FROM %s%s" % (res, res, where)))
    return {"keywords": c("ad_group_criterion",
                          " WHERE ad_group_criterion.type = 'KEYWORD' AND "
                          "ad_group_criterion.negative = FALSE AND "
                          "ad_group_criterion.status != 'REMOVED'"),
            "ads": c("ad_group_ad", " WHERE ad_group_ad.status != 'REMOVED'"),
            "campaign_negative_keywords": c(
                "campaign_criterion",
                " WHERE campaign_criterion.type = 'KEYWORD' AND "
                "campaign_criterion.negative = TRUE AND "
                "campaign_criterion.status != 'REMOVED'"),
            "ad_schedules": c("campaign_criterion",
                              " WHERE campaign_criterion.type = 'AD_SCHEDULE' AND "
                              "campaign_criterion.status != 'REMOVED'"),
            "conversion_actions": c("conversion_action",
                                    " WHERE conversion_action.status != 'REMOVED'"),
            "ad_groups": c("ad_group", " WHERE ad_group.status != 'REMOVED'")}


def run(service, request, method, label):
    """validate_only pass, then the real call. Returns results or None."""
    request.partial_failure = False
    request.validate_only = True
    try:
        getattr(service, method)(request=request)
        print("   %s dry run PASSED" % label)
    except Exception as exc:                                   # noqa: BLE001
        print("   %s dry run FAILED - nothing applied" % label)
        print("   %s" % str(exc)[:1000])
        log.setdefault("failures", []).append(
            {"step": label, "phase": "dry_run", "error": str(exc)[:3000]})
        return None
    request.validate_only = False
    try:
        resp = getattr(service, method)(request=request)
    except Exception as exc:                                   # noqa: BLE001
        print("   %s MUTATE FAILED - atomic, nothing applied" % label)
        print("   %s" % str(exc)[:1000])
        log.setdefault("failures", []).append(
            {"step": label, "phase": "mutate", "error": str(exc)[:3000]})
        return None
    return list(resp.results)


def main() -> int:
    global fail
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    asvc = client.get_service("AssetService")
    casvc = client.get_service("CampaignAssetService")
    cusvc = client.get_service("CustomerAssetService")
    started = datetime.now(TZ)
    log["started_account_local"] = started.isoformat()

    print("=" * 78)
    print("EXECUTE PLAN-H  %s" % started.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("=" * 78)

    # ---- 1. identity ----
    print("\n1. IDENTITY")
    c = rows(svc, "SELECT customer.id, customer.descriptive_name, customer.manager, "
                  "customer.test_account, customer.currency_code, customer.time_zone "
                  "FROM customer LIMIT 1")[0].customer
    log["identity"] = {"id": str(c.id), "name": c.descriptive_name}
    gate("account name exact", c.descriptive_name == NAME, c.descriptive_name)
    gate("customer id exact", str(c.id) == CID, str(c.id))
    gate("manager false", c.manager is False)
    gate("test account false", c.test_account is False)
    gate("live marker present", "- live" in c.descriptive_name.lower())
    if fail:
        print("\nABORT - identity. Nothing changed.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 2

    # ---- 2. fingerprint ----
    print("\n2. FINGERPRINT")
    plan = yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))
    p = plan["change_plan"]
    fp = approval_code(normalize(plan))
    log["fingerprint_recomputed"] = fp
    gate("fingerprint matches approval", fp == APPROVED_FP,
         "%s == %s" % (fp, APPROVED_FP))
    gate("plan declares 21 mutations",
         p["change_counts"]["google_ads_mutations_total"] == 21)
    gate("plan deletes no assets", p["change_counts"]["assets_deleted"] == 0)
    gate("plan changes no budgets", p["change_counts"]["budgets_changed"] == 0)
    if fail:
        print("\nABORT - fingerprint. Nothing changed.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 2

    # ---- 3. drift ----
    print("\n3. DRIFT SNAPSHOT (before)")
    before = sitelink_state(svc)
    before_counts = counts(svc)
    log["before"] = {"sitelinks": before, "counts": before_counts}
    for cid_ in (CAMP_A, CAMP_B):
        got = set(before["campaign"].get(cid_, {}))
        gate("%s has the 4 expected old sitelinks" % NAMES[cid_],
             set(OLD_CAMPAIGN_ASSETS) <= got, sorted(got))
    gate("account-level asset %s still linked" % OLD_CUSTOMER_ASSET,
         OLD_CUSTOMER_ASSET in before["customer"],
         sorted(before["customer"]))
    for k, v in before_counts.items():
        gate("count %s == %d" % (k, BASELINE[k]), v == BASELINE[k], str(v))
    q = ("SELECT campaign.id, campaign.target_spend.cpc_bid_ceiling_micros, "
         "campaign_budget.amount_micros FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B})")
    for x in rows(svc, q):
        cid_ = str(x.campaign.id)
        gate("%s budget unchanged" % NAMES[cid_],
             x.campaign_budget.amount_micros == BASELINE[
                 "budget_A" if cid_ == CAMP_A else "budget_B"],
             str(x.campaign_budget.amount_micros))
        gate("%s CPC ceiling still $30" % NAMES[cid_],
             x.campaign.target_spend.cpc_bid_ceiling_micros == BASELINE["ceiling"],
             str(x.campaign.target_spend.cpc_bid_ceiling_micros))
    if fail:
        print("\nABORT - drift. Nothing changed.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 2

    # ---- 4. H01 create the four assets ----
    print("\n4. H01 - CREATE 4 SITELINK ASSETS")
    ops = []
    for s in p["proposed_sitelinks"]:
        op = client.get_type("AssetOperation")
        a = op.create
        a.final_urls.append(s["final_url"])
        a.sitelink_asset.link_text = s["sitelink_text"]
        a.sitelink_asset.description1 = s["description1"]
        a.sitelink_asset.description2 = s["description2"]
        ops.append(op)
        print("   + %-18s %s" % (s["sitelink_text"], s["final_url"]))
    req = client.get_type("MutateAssetsRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    res = run(asvc, req, "mutate_assets", "H01")
    if res is None:
        log["execution"] = "FAILED_AT_H01_NOTHING_APPLIED"
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1
    new_ids = [r.resource_name.rsplit("/", 1)[-1] for r in res]
    log["new_asset_ids"] = new_ids
    print("   created: %s" % new_ids)
    gate("4 assets created", len(new_ids) == 4, str(len(new_ids)))
    if fail:
        print("\nSTOP - partial create. Inventory above. No links made.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    # ---- 5. H02/H03 link the new assets to both campaigns ----
    print("\n5. H02/H03 - LINK 4 NEW ASSETS TO BOTH CAMPAIGNS (8 links)")
    ops = []
    for cid_ in (CAMP_A, CAMP_B):
        for aid in new_ids:
            op = client.get_type("CampaignAssetOperation")
            ca = op.create
            ca.campaign = svc.campaign_path(CID, cid_)
            ca.asset = asvc.asset_path(CID, aid)
            ca.field_type = client.enums.AssetFieldTypeEnum.SITELINK
            ops.append(op)
    req = client.get_type("MutateCampaignAssetsRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    res = run(casvc, req, "mutate_campaign_assets", "H02/H03")
    if res is None:
        log["execution"] = "FAILED_AT_H02_H03"
        log["recovery_note"] = (
            "The 4 assets in new_asset_ids WERE created but are NOT linked. "
            "They do not serve. Either retry the link step or remove them.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1
    log["new_link_resource_names"] = [r.resource_name for r in res]
    print("   created %d links" % len(res))
    gate("8 links created", len(res) == 8, str(len(res)))

    # ---- 6. VERIFY BEFORE UNLINKING ----
    print("\n6. VERIFY NEW SITELINKS ARE LIVE BEFORE ANY REMOVAL")
    mid = sitelink_state(svc)
    log["mid_state"] = mid
    ok_to_unlink = True
    for cid_ in (CAMP_A, CAMP_B):
        got = set(mid["campaign"].get(cid_, {}))
        have_new = set(new_ids) <= got
        print("   %-17s now has %d SITELINK links (new present: %s)"
              % (NAMES[cid_], len(got), have_new))
        gate("%s carries all 4 NEW sitelinks" % NAMES[cid_], have_new,
             sorted(got))
        if not have_new:
            ok_to_unlink = False
        for aid in new_ids:
            d = mid["campaign"].get(cid_, {}).get(aid)
            if d:
                gate("  %s -> %s" % (d["link_text"], d["final_urls"][0][:52]),
                     d["final_urls"] and "offer.softwindli.com" in d["final_urls"][0],
                     d["status"])
    if not ok_to_unlink or fail:
        print("\nSTOP - new sitelinks not confirmed live. OLD LINKS LEFT INTACT,")
        print("       so the campaigns still have serving sitelinks.")
        log["execution"] = "STOPPED_BEFORE_UNLINK"
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1

    # ---- 7. H04 remove the 8 old campaign links ----
    print("\n7. H04 - REMOVE 8 OLD CAMPAIGN SITELINK LINKS")
    ops, removing = [], []
    for cid_ in (CAMP_A, CAMP_B):
        for aid in OLD_CAMPAIGN_ASSETS:
            d = mid["campaign"].get(cid_, {}).get(aid)
            if not d:
                continue
            op = client.get_type("CampaignAssetOperation")
            op.remove = d["resource_name"]
            ops.append(op)
            removing.append("%s / %s (%s)" % (NAMES[cid_], d["link_text"], aid))
    for x in removing:
        print("   - %s" % x)
    gate("exactly 8 old links targeted", len(ops) == 8, str(len(ops)))
    if fail:
        log["execution"] = "STOPPED_BEFORE_UNLINK"
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1
    req = client.get_type("MutateCampaignAssetsRequest")
    req.customer_id = CID
    req.operations.extend(ops)
    res = run(casvc, req, "mutate_campaign_assets", "H04")
    if res is None:
        log["execution"] = "FAILED_AT_H04"
        log["recovery_note"] = ("New sitelinks ARE live and serving. Old links "
                                "remain. State is safe but has 8 sitelinks.")
        OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
        return 1
    log["removed_campaign_links"] = [r.resource_name for r in res]
    print("   removed %d links" % len(res))

    # ---- 8. H05 remove the account-level link ----
    print("\n8. H05 - REMOVE ACCOUNT-LEVEL SITELINK %s" % OLD_CUSTOMER_ASSET)
    d = mid["customer"].get(OLD_CUSTOMER_ASSET)
    gate("account-level link found", d is not None)
    if d:
        print("   - %s -> %s" % (d["link_text"], d["final_urls"][0]))
        op = client.get_type("CustomerAssetOperation")
        op.remove = d["resource_name"]
        req = client.get_type("MutateCustomerAssetsRequest")
        req.customer_id = CID
        req.operations.append(op)
        res = run(cusvc, req, "mutate_customer_assets", "H05")
        if res is None:
            log["execution"] = "FAILED_AT_H05"
            log["recovery_note"] = ("Campaign-level work COMPLETE and correct. "
                                    "Only the account-level link removal failed.")
            OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")
            return 1
        log["removed_customer_links"] = [r.resource_name for r in res]
        print("   removed %d link" % len(res))

    log["execution"] = "SUCCEEDED"
    log["executed_account_local"] = datetime.now(TZ).isoformat()

    # ---- 9. readback QA ----
    print("\n9. READBACK QA")
    after = sitelink_state(svc)
    after_counts = counts(svc)
    log["after"] = {"sitelinks": after, "counts": after_counts}
    for cid_ in (CAMP_A, CAMP_B):
        got = after["campaign"].get(cid_, {})
        gate("%s has exactly 4 SITELINK links" % NAMES[cid_], len(got) == 4,
             str(len(got)))
        gate("%s all sitelinks on offer subdomain" % NAMES[cid_],
             all("offer.softwindli.com" in d["final_urls"][0]
                 for d in got.values() if d["final_urls"]),
             ", ".join(sorted(d["link_text"] for d in got.values())))
        gate("%s no old asset still linked" % NAMES[cid_],
             not (set(OLD_CAMPAIGN_ASSETS) & set(got)), sorted(got))
    gate("account-level %s unlinked" % OLD_CUSTOMER_ASSET,
         OLD_CUSTOMER_ASSET not in after["customer"],
         sorted(after["customer"]))
    gate("other 3 account-level sitelinks untouched",
         len(after["customer"]) == 3, sorted(after["customer"]))

    # assets themselves must still exist - links only were removed
    q = ("SELECT asset.id, asset.sitelink_asset.link_text FROM asset "
         "WHERE asset.id IN (%s)" % ", ".join(OLD_CAMPAIGN_ASSETS + [OLD_CUSTOMER_ASSET]))
    still = {str(x.asset.id) for x in rows(svc, q)}
    gate("all 5 old ASSETS still exist (links only removed)",
         still == set(OLD_CAMPAIGN_ASSETS + [OLD_CUSTOMER_ASSET]), sorted(still))

    for k, v in after_counts.items():
        gate("count %s unchanged" % k, v == before_counts[k],
             "%s -> %s" % (before_counts[k], v))
    q = ("SELECT campaign.id, campaign.status, "
         "campaign.target_spend.cpc_bid_ceiling_micros, "
         "campaign_budget.amount_micros FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B})")
    for x in rows(svc, q):
        cid_ = str(x.campaign.id)
        gate("%s budget still unchanged" % NAMES[cid_],
             x.campaign_budget.amount_micros == BASELINE[
                 "budget_A" if cid_ == CAMP_A else "budget_B"])
        gate("%s ceiling still $30" % NAMES[cid_],
             x.campaign.target_spend.cpc_bid_ceiling_micros == BASELINE["ceiling"])
        gate("%s still ENABLED" % NAMES[cid_], x.campaign.status.name == "ENABLED")

    log["qa_failures"] = [g for g in log["gates"] if not g["pass"]]
    log["qa_passed"] = not fail
    OUT.write_text(json.dumps(log, indent=2), encoding="utf-8")

    print("\n" + "=" * 78)
    print("RESULT: %s   gates %d/%d passed"
          % ("QA PASSED" if not fail else "QA FAILED",
             sum(1 for g in log["gates"] if g["pass"]), len(log["gates"])))
    print("   mutations: 4 assets created, 8 links created, 9 links removed = 21")
    print("=" * 78)
    print("wrote %s" % OUT)
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
