#!/usr/bin/env python3
"""Ambient | 2026-09-25 | Service-priority pass on the seven heating Search campaigns.

Owner decision 2026-09-25 (budget concentration; authorized in-run, no routine re-approval):
  * every in-scope heating ad group ENABLED for visibility;
  * deferred / page-less / availability-unverified groups keep EVERY ad PAUSED, and the ads are
    paused and read back BEFORE the group is enabled;
  * ready core groups keep their approved offer-page ads serving;
  * labels CORE_ACTIVE, GEOTHERMAL_TEST, DEFERRED_BUDGET, EVALUATE_DUCTLESS, WAITING_LP,
    WAITING_TRACKING, WAITING_POLICY, WAITING_AVAILABILITY;
  * inherited assets that still promote deferred services are unlinked from serving campaigns.

    python ambient_0925_priority.py plan
    python ambient_0925_priority.py execute --fp <fingerprint>
Stages (each one atomic, partial_failure=False, receipt written after each):
  S1 create labels · S2 pause 18 ads · READBACK gate (0 enabled ads in held groups) ·
  S3 enable 11 groups + 30 label links · S4 asset hygiene (2 new snippets, 7 link pauses/links)
"""
from __future__ import annotations
import sys, json, re, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS
from gm_gsa.safety import approval_code
from google.protobuf import field_mask_pb2

PLAN_NAME = "AMB-0925-PRIORITY-1"
LABELS = ["CORE_ACTIVE", "GEOTHERMAL_TEST", "DEFERRED_BUDGET", "EVALUATE_DUCTLESS", "WAITING_LP",
          "WAITING_TRACKING", "WAITING_POLICY", "WAITING_AVAILABILITY"]
LABEL_DESC = {
    "CORE_ACTIVE": "Funded priority service; approved offer-page ads serving",
    "GEOTHERMAL_TEST": "Controlled geothermal Search test inside the existing $20/day",
    "DEFERRED_BUDGET": "Budget-concentration deferral 2026-09-25; group enabled, every ad paused",
    "EVALUATE_DUCTLESS": "Ductless installation conditional expansion review",
    "WAITING_LP": "No correct published offer page for this service",
    "WAITING_TRACKING": "Waiting on a tracking gate",
    "WAITING_POLICY": "Waiting on a policy review",
    "WAITING_AVAILABILITY": "Service availability claim not verified",
}
SEVEN = ["24257819463", "24268690038", "24257819466", "24132507744", "24279798229", "24268690041", "24274160783"]
# ad group -> (name, labels, reason)
GROUPS = {
    # core, serving
    "204129717087": ("No Heat Repair", ["CORE_ACTIVE"], "core repair; /no-heat-repair/ passes"),
    "204129717007": ("Heating Repair", ["CORE_ACTIVE"], "core repair; /hvac-repair/ passes"),
    "199797580706": ("Furnace Repair", ["CORE_ACTIVE"], "core repair; /furnace-repair/ passes"),
    "204129717247": ("Gas Furnace Repair", ["CORE_ACTIVE"], "core repair; 1 of 2 ads FULLY_LIMITED (housing)"),
    "204129717287": ("Electric Furnace Repair", ["CORE_ACTIVE"], "core repair; /furnace-repair/ passes"),
    "204129717327": ("Heat Pump Repair", ["CORE_ACTIVE"], "core repair; /heat-pump-repair/ passes"),
    "204129717807": ("Furnace Installation", ["CORE_ACTIVE"], "core install; /hvac-installation/ passes"),
    "204129717767": ("Furnace Replacement", ["CORE_ACTIVE"], "core replace; /hvac-replacement/ passes"),
    "204129717967": ("Heating Installation", ["CORE_ACTIVE"], "core install; /hvac-installation/ passes"),
    "204129718007": ("Heating Replacement", ["CORE_ACTIVE"], "core replace; /hvac-replacement/ passes"),
    "204129717527": ("Heat Pump Installation", ["CORE_ACTIVE"], "core install; D4 heading defect only"),
    "204129717487": ("Heat Pump Replacement", ["CORE_ACTIVE"], "core replace; D4 heading defect only"),
    "204129718047": ("Boiler Repair", ["CORE_ACTIVE"], "core repair; /gas-boiler-repair/ passes"),
    "202339087594": ("Gas Boiler Repair", ["CORE_ACTIVE"], "core repair; /gas-boiler-repair/ passes"),
    "204129718207": ("Boiler Replacement", ["CORE_ACTIVE"], "core replace; D4 FAQ heading defect only"),
    "204129718767": ("Thermostat Repair", ["CORE_ACTIVE"], "existing thermostat traffic kept at $15; 1 of 2 ads FULLY_LIMITED (housing)"),
    "204129718927": ("Thermostat Replacement", ["CORE_ACTIVE"], "existing thermostat traffic kept at $15"),
    "204129718967": ("Smart Thermostat Installation", ["CORE_ACTIVE"], "existing thermostat traffic kept at $15"),
    # held: group enabled, every ad paused
    "204129718247": ("Boiler Installation", ["WAITING_LP"], "core service; /boiler-installation/ still shows Boiler MAINTENANCE content (D2)"),
    "204129719007": ("Geothermal Heat Pump", ["GEOTHERMAL_TEST", "WAITING_LP"], "$20 test; /geothermal-heat-pump/ returns 404"),
    "199797580746": ("Ductless Heating Installation", ["DEFERRED_BUDGET", "EVALUATE_DUCTLESS", "WAITING_LP"], "review not passed; page 404"),
    "204129717727": ("Ductless Heating Repair", ["DEFERRED_BUDGET", "WAITING_LP"], "deferred; page 404"),
    "204129717567": ("Heat Pump Maintenance", ["DEFERRED_BUDGET"], "deferred; page published and correct"),
    "204129718287": ("Boiler Maintenance", ["DEFERRED_BUDGET", "WAITING_LP"], "deferred; page body is Boiler INSTALLATION content (D2)"),
    "204129718447": ("Furnace Maintenance", ["DEFERRED_BUDGET", "WAITING_LP"], "deferred; page 404"),
    "204129718527": ("Furnace Tune-Up", ["DEFERRED_BUDGET", "WAITING_LP"], "deferred; page 404"),
    "204129718487": ("Heating Maintenance", ["DEFERRED_BUDGET", "WAITING_LP"], "deferred; page 404"),
    "204129718687": ("Heating Tune-Up", ["DEFERRED_BUDGET", "WAITING_LP"], "deferred; page 404"),
    "204129718727": ("Heating System Inspection", ["DEFERRED_BUDGET", "WAITING_LP"], "deferred; page 404"),
    "204129717047": ("Emergency Heating Repair", ["WAITING_LP", "WAITING_AVAILABILITY"], "no page; emergency availability unverified (barred claim)"),
}
HELD = [g for g, v in GROUPS.items() if "CORE_ACTIVE" not in v[1]]
O = "https://offer.ambientcoolingandheating.com"
NEW_SNIPPETS = {  # key -> (header, values, campaign, replaces_asset)
    "SNIP_HP": ("Services", ["Heat Pump Repair", "Heat Pump Replacement", "Heat Pump Installation"], "24268690038", "423727603969"),
    "SNIP_GEO": ("Services", ["Geothermal Heat Pump", "Heat Pump Installation", "Heating Installation"], "24274160783", "423727603972"),
}
LINK_PAUSES = [  # (campaign, asset, field_type, why)
    ("24268690038", "424481133551", "SITELINK", "Heat Pump Maintenance sitelink promotes a deferred service"),
    ("24268690038", "422577777442", "CALLOUT", "'Repair and Maintenance' promotes a deferred service"),
    ("24268690041", "422577777442", "CALLOUT", "'Repair and Maintenance' promotes a deferred service"),
    ("24274160783", "422577777442", "CALLOUT", "'Repair and Maintenance' promotes a deferred service"),
    ("24268690038", "423727603969", "STRUCTURED_SNIPPET", "snippet lists Ductless Heating + Mini Split Service"),
    ("24274160783", "423727603972", "STRUCTURED_SNIPPET", "snippet lists Ductless Heating"),
]


def fresh(c):
    ags = {str(r.ad_group.id): (r.ad_group.name, E(r.ad_group.status), str(r.campaign.id)) for r in q(c,
           f"SELECT ad_group.id, ad_group.name, ad_group.status, campaign.id FROM ad_group WHERE campaign.id IN ({','.join(SEVEN)}) AND ad_group.status != 'REMOVED'")}
    ads = [(str(r.ad_group.id), str(r.ad_group_ad.ad.id), E(r.ad_group_ad.status), list(r.ad_group_ad.ad.final_urls)) for r in q(c,
           f"SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls FROM ad_group_ad WHERE campaign.id IN ({','.join(SEVEN)}) AND ad_group_ad.status != 'REMOVED'")]
    labels = {r.label.name: str(r.label.id) for r in q(c, "SELECT label.id, label.name FROM label WHERE label.status = 'ENABLED'")}
    links = {(str(r.campaign.id), r.campaign_asset.asset.split("/")[-1], E(r.campaign_asset.field_type)): E(r.campaign_asset.status) for r in q(c,
             f"SELECT campaign.id, campaign_asset.asset, campaign_asset.field_type, campaign_asset.status FROM campaign_asset WHERE campaign.id IN ({','.join(SEVEN)}) AND campaign_asset.status != 'REMOVED'")}
    return ags, ads, labels, links


def build(c):
    ags, ads, labels, links = fresh(c)
    errs = []
    if sorted(ags) != sorted(GROUPS): errs.append(f"group set drift: extra {set(ags)-set(GROUPS)} missing {set(GROUPS)-set(ags)}")
    for g, (n, lb, why) in GROUPS.items():
        if g in ags and n not in ags[g][0]: errs.append(f"{g} name drift {ags[g][0]}")
    pause_ads = sorted((g, a) for g, a, st, u in ads if g in HELD and st == "ENABLED")
    enable_groups = sorted(g for g in HELD if ags[g][1] == "PAUSED")
    for g in GROUPS:
        if "CORE_ACTIVE" in GROUPS[g][1]:
            live = [a for gg, a, st, u in ads if gg == g and st == "ENABLED"]
            if ags[g][1] != "ENABLED" or not live: errs.append(f"core group {GROUPS[g][0]} not enabled with ads")
            if any(not u[0].startswith(O) for gg, a, st, u in ads if gg == g and st == "ENABLED"): errs.append(f"core {g} main-site ad enabled")
    for camp, asset, ft, why in LINK_PAUSES:
        if links.get((camp, asset, ft)) != "ENABLED": errs.append(f"link {camp}/{asset}/{ft} is {links.get((camp, asset, ft))}")
    for bad in re.compile(r"maint|tune|ductless|mini", re.I), :
        for k, (h, vals, camp, _) in NEW_SNIPPETS.items():
            if any(bad.search(v) for v in vals) or any(len(v) > 25 for v in vals) or len(vals) < 3: errs.append(f"snippet {k} invalid")
    plan = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342",
            "plan_name": PLAN_NAME, "built_local": datetime.datetime.now(TZ).date().isoformat(),
            "authority": "owner instruction 2026-09-25 (service priorities; authorized in-run)",
            "labels_to_create": [l for l in LABELS if l not in labels],
            "ads_to_pause": [{"ad_group_id": g, "ad_group": GROUPS[g][0], "ad_id": a} for g, a in pause_ads],
            "groups_to_enable_after_readback": [{"ad_group_id": g, "ad_group": GROUPS[g][0]} for g in enable_groups],
            "group_labels": {g: {"name": v[0], "labels": v[1], "reason": v[2]} for g, v in GROUPS.items()},
            "snippets_to_create": {k: {"header": v[0], "values": v[1], "campaign": v[2], "replaces": v[3]} for k, v in NEW_SNIPPETS.items()},
            "campaign_asset_links_to_pause": [dict(campaign=a, asset=b, field_type=f, why=w) for a, b, f, w in LINK_PAUSES],
            "unchanged": ["all budgets", "all campaign statuses", "all keywords", "core ads", "conversion actions"],
            "errors": errs}
    plan["operation_count"] = (len(plan["labels_to_create"]) + len(pause_ads) + len(enable_groups)
                               + sum(len(v[1]) for v in GROUPS.values()) + 2 * len(NEW_SNIPPETS) + len(LINK_PAUSES))
    return plan


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["plan", "execute"]); ap.add_argument("--fp")
    a = ap.parse_args()
    c = client(); identity_gate(c, verbose=False)
    plan = build(c)
    fp = approval_code(plan)
    if a.mode == "plan":
        plan["fingerprint"] = fp
        (PLANS / f"{PLAN_NAME}.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print(f"PLAN {PLAN_NAME} {fp} ops={plan['operation_count']} errors={plan['errors']}")
        print(f"  labels {len(plan['labels_to_create'])} | pause ads {len(plan['ads_to_pause'])} | enable groups {len(plan['groups_to_enable_after_readback'])} | link pauses {len(LINK_PAUSES)}")
        return
    if a.fp != fp or plan["errors"]:
        sys.exit(f"ABORT: fingerprint {fp} != {a.fp} or errors {plan['errors']}")
    rec = {"plan": PLAN_NAME, "fingerprint": fp, "started_local": datetime.datetime.now(TZ).isoformat(), "stages": []}
    out = RECEIPTS / f"{PLAN_NAME}-EXECUTED.json"
    save = lambda: out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    gas = c.get_service("GoogleAdsService")

    def run(stage, mops):
        if not mops: rec["stages"].append({stage: "nothing to do"}); save(); return []
        rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False
        rq.mutate_operations.extend(mops)
        try:
            resp = gas.mutate(request=rq)
        except Exception as ex:
            rec["stages"].append({stage: "FAILED", "error": str(ex)[:1500]}); save()
            sys.exit(f"STOP at {stage}: {str(ex)[:600]}")
        names = []
        for r in resp.mutate_operation_responses:
            for f in ("label_result", "ad_group_ad_result", "ad_group_result", "ad_group_label_result", "asset_result", "campaign_asset_result"):
                if r._pb.HasField(f): names.append(getattr(r, f).resource_name)
        rec["stages"].append({stage: "OK", "resources": names}); save()
        print(f"  {stage}: OK {len(names)}")
        return names

    # S1 labels
    mops = []
    for ln in plan["labels_to_create"]:
        m = c.get_type("MutateOperation"); m.label_operation.create.name = ln
        m.label_operation.create.text_label.description = LABEL_DESC[ln]; mops.append(m)
    run("S1_create_labels", mops)
    # S2 pause ads
    agas = c.get_service("AdGroupAdService"); mops = []
    for x in plan["ads_to_pause"]:
        m = c.get_type("MutateOperation"); o = m.ad_group_ad_operation
        o.update.resource_name = agas.ad_group_ad_path(CID, x["ad_group_id"], x["ad_id"])
        o.update.status = c.enums.AdGroupAdStatusEnum.PAUSED
        o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"])); mops.append(m)
    run("S2_pause_held_ads", mops)
    # READBACK gate
    ags, ads, labels, links = fresh(c)
    still = [(g, a) for g, a, st, u in ads if g in HELD and st == "ENABLED"]
    rec["readback_gate"] = {"held_groups": len(HELD), "enabled_ads_in_held_groups": still}; save()
    if still: sys.exit(f"STOP: enabled ads remain in held groups {still}")
    print(f"  READBACK gate PASS: 0 enabled ads across {len(HELD)} held groups")
    # S3 enable groups + label links
    ags_svc = c.get_service("AdGroupService"); mops = []
    for x in plan["groups_to_enable_after_readback"]:
        m = c.get_type("MutateOperation"); o = m.ad_group_operation
        o.update.resource_name = ags_svc.ad_group_path(CID, x["ad_group_id"]); o.update.status = c.enums.AdGroupStatusEnum.ENABLED
        o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"])); mops.append(m)
    for g, v in GROUPS.items():
        for ln in v[1]:
            m = c.get_type("MutateOperation"); o = m.ad_group_label_operation
            o.create.ad_group = ags_svc.ad_group_path(CID, g)
            o.create.label = c.get_service("LabelService").label_path(CID, labels[ln]); mops.append(m)
    run("S3_enable_groups_and_label", mops)
    # S4 asset hygiene
    mops = []; tmp = -1; tmpmap = {}
    asvc = c.get_service("AssetService"); casvc = c.get_service("CampaignAssetService")
    for k, (h, vals, camp, _) in NEW_SNIPPETS.items():
        m = c.get_type("MutateOperation"); a_ = m.asset_operation.create
        a_.resource_name = asvc.asset_path(CID, tmp); a_.name = f"GM 2026-09-25 {k}"
        a_.structured_snippet_asset.header = h; a_.structured_snippet_asset.values.extend(vals)
        tmpmap[k] = a_.resource_name; tmp -= 1; mops.append(m)
    for k, (h, vals, camp, _) in NEW_SNIPPETS.items():
        m = c.get_type("MutateOperation"); o = m.campaign_asset_operation.create
        o.campaign = c.get_service("CampaignService").campaign_path(CID, camp); o.asset = tmpmap[k]
        o.field_type = c.enums.AssetFieldTypeEnum.STRUCTURED_SNIPPET; mops.append(m)
    for camp, asset, ft, why in LINK_PAUSES:
        m = c.get_type("MutateOperation"); o = m.campaign_asset_operation
        o.update.resource_name = casvc.campaign_asset_path(CID, camp, asset, ft)
        o.update.status = c.enums.AssetLinkStatusEnum.PAUSED
        o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"])); mops.append(m)
    run("S4_asset_hygiene", mops)
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat(); save()
    print("DONE", out.name)


if __name__ == "__main__":
    main()
