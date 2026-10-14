#!/usr/bin/env python3
"""Ambient | 2026-10-02 | Search launch under the staged authorization (Green Marketing, 2026-10-02). stage A -> B -> C.

  A  create/update PAUSED: Furnace Maintenance ads -> required URL; 2 new Maintenance RSAs (replace the Housing-limited
     Furnace Tune-Up ad 825585199664 and the unverified-claim Inspection ad 825585199676, both left PAUSED); 2 Boiler
     Installation RSAs (held AMB-0925 payload; page D2 fixed 2026-10-02); 1 geothermal sitelink asset.
  B  read back every created/updated resource (status, URL, text, pins, paths).
  C  enable: Maintenance (10 ads), Boiler Installation (2 ads + 3 keywords), Commercial (2 ads), Geothermal (2 ads),
     No Heat keyword [house has no heat]; holding labels removed; sitelink/callout associations corrected.
  python scripts/ambient_1002_search_launch.py plan | run
`plan` = validate_only of stage A + C payloads and fingerprints; `run` = execute A, read back (B), then C, read back.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, PLANS, RECEIPTS, E, CID, EXACT_NAME  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402

MAINT_URL = "https://ambientcoolingandheating.com/services/heating-services/"
O = "https://offer.ambientcoolingandheating.com"
MAINT, BOILER, COMM, GEO, REPAIR, HP = "24279798229", "24132507744", "24132507747", "24274160783", "24257819463", "24268690038"
G = dict(FM="204129718447", HM="204129718487", FTU="204129718527", HTU="204129718687", HSI="204129718727", BI="204129718247",
         COMMG="199748801029", GEOG="204129719007", NOHEAT="204129717087")
D_ = "DESCRIPTION_1"
NEW_RSAS = {
    "MAINT_FTU_B": dict(ad_group=G["FTU"], url=MAINT_URL, path1="Furnace", path2="Tune-Up", h=[
        "Tune Up Before Winter", "Yearly Furnace Tune Up", "Furnace Check Before Winter", "Prevent Costly Breakdowns", "Furnace Maintenance Plans",
        "Tune Ups And Inspections", "Severn Furnace Tune Up", "Columbia Furnace Tune Up", "Glen Burnie Furnace Tune Up", "Keep Your Furnace Efficient",
        "Schedule Your Tune Up", "Skilled HVAC Technicians", "Ask About Maintenance Plans", "Furnace Tune Up Service", "Book A Fall Tune Up"], d=[
        "We recommend a professional furnace tune-up once a year, before the heating season starts.",
        "A yearly tune-up helps extend equipment life and prevent costly breakdowns.",
        "Ask about maintenance plans for homes in Severn, Severna Park and Columbia, Maryland.",
        "Call Mon-Fri, 8 a.m. to 4 p.m., or send a request to schedule your furnace tune-up."]),
    "MAINT_HSI_B": dict(ad_group=G["HSI"], url=MAINT_URL, path1="Heating", path2="Inspection", h=[
        "Inspect Before Winter", "Heating Inspection Service", "Thorough Heating Inspection", "Heating System Check", "Glen Burnie Heating Inspection",
        "Annapolis Heating Inspection", "Prevent Costly Breakdowns", "Heating Maintenance Plans", "Schedule Your Inspection", "Skilled HVAC Technicians",
        "Inspections And Tune Ups", "Know What Your System Needs", "Ask About Maintenance Plans", "Before The Cold Arrives", "Home Heating Check"], d=[
        "A thorough heating inspection before winter shows what your system needs.",
        "Inspections and tune-ups help extend equipment life and prevent costly breakdowns.",
        "Heating system inspections for homes in Severn, Severna Park and Columbia, MD.",
        "Call Mon-Fri, 8 a.m. to 4 p.m., or send a request to schedule your inspection."]),
}
HELD = json.loads((Path(__file__).resolve().parents[1] / "clients/ambient-cooling-heating/plans/AMB-0925-HELD-RSA-PAYLOADS.json").read_text(encoding="utf-8"))["payloads"][G["BI"]]
for i, r in enumerate(HELD["rsas"]):
    NEW_RSAS[f"BOILER_INST_{'AB'[i]}"] = dict(ad_group=G["BI"], url=HELD["final_url"], path1=HELD["path1"], path2=HELD["path2"], h=r["h"], d=r["d"])
GEO_SITELINK = dict(link_text="Geothermal Heat Pumps", description1="Installation consultation", description2="Replacement planning", url=f"{O}/geothermal-heat-pump/")
URL_FIX = ["825585199649", "825585199652"]   # Furnace Maintenance ads -> MAINT_URL
ENABLE_EXISTING_ADS = {G["FM"]: URL_FIX, G["HM"]: ["825585199655", "825585199658"], G["FTU"]: ["825585199661"], G["HTU"]: ["825585199667", "825585199670"],
                       G["HSI"]: ["825585199673"], G["COMMG"]: ["824781897834", "824781897837"], G["GEOG"]: ["826785945725", "826785945728"]}
KEEP_PAUSED_ADS = {"825585199664": "RESTRICTED_HOUSING / FULLY_LIMITED", "825585199676": "unverified claim 'Clear Written Findings'"}
ENABLE_KEYWORDS = {G["BI"]: ["*"], G["NOHEAT"]: ["410033471640"]}     # '*' = every PAUSED positive keyword in the group
REMOVE_LABELS = {g: ["DEFERRED_BUDGET", "WAITING_LP"] for g in (G["FM"], G["HM"], G["FTU"], G["HTU"], G["HSI"])} | {G["BI"]: ["WAITING_LP"], G["GEOG"]: ["WAITING_LP"]}
LINK_SITELINKS = {MAINT: ["424583525083", "424481123441", "424481133551", "410638278156"], GEO: ["424666395915", "424481139482"], HP: ["NEW_GEO_SITELINK"]}
PAUSE_CAMPAIGN_ASSET = [(COMM, "407418595411", "CALLOUT", "'Prompt, Reliable Service' implies a response-speed promise (barred claim)"),
                        (GEO, "422577777430", "CALLOUT", "'Diagnosis Explained' is repair framing; geothermal paid scope excludes repair")]
BARRED = re.compile(r"24/7|24 hour|same[- ]day|immediate|\bfast\b|guarant|warrant|licen[cs]|insured|certified|\bbest\b|\$\d|discount|financ|rated|\d{3}[-.\s]\d{3}[-.\s]\d{4}|!", re.I)


def checks():
    errs = []
    for k, r in NEW_RSAS.items():
        if len(r["h"]) != 15 or len(r["d"]) != 4: errs.append(f"{k}: counts")
        if len({x.lower() for x in r["h"]}) != 15: errs.append(f"{k}: duplicate headline")
        errs += [f"{k}: headline>30 {x}" for x in r["h"] if len(x) > 30] + [f"{k}: description>90 {x}" for x in r["d"] if len(x) > 90]
        errs += [f"{k}: barred '{x}'" for x in r["h"] + r["d"] if BARRED.search(x)]
        if len(r["path1"]) > 15 or len(r["path2"]) > 15: errs.append(f"{k}: path")
    if len(GEO_SITELINK["link_text"]) > 25 or max(len(GEO_SITELINK["description1"]), len(GEO_SITELINK["description2"])) > 35: errs.append("sitelink length")
    return errs


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "plan"
    c = client(); identity_gate(c, verbose=False)
    svc = c.get_service
    errs = checks()
    labels = {r.label.name: str(r.label.id) for r in q(c, "SELECT label.name, label.id FROM label")}
    paused_kw = {}
    for g, ids in ENABLE_KEYWORDS.items():
        for r in q(c, f"""SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                ad_group_criterion.approval_status FROM ad_group_criterion WHERE ad_group.id = {g} AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE
                AND ad_group_criterion.status = 'PAUSED'"""):
            k = r.ad_group_criterion
            if ids == ["*"] or str(k.criterion_id) in ids:
                paused_kw[(g, str(k.criterion_id))] = (k.keyword.text, E(k.keyword.match_type), E(k.approval_status))
    ad_state = {str(r.ad_group_ad.ad.id): (E(r.ad_group_ad.status), E(r.ad_group_ad.policy_summary.approval_status), list(r.ad_group_ad.ad.final_urls)) for r in q(c,
                f"SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.policy_summary.approval_status, ad_group_ad.ad.final_urls FROM ad_group_ad WHERE campaign.id IN ({MAINT},{COMM},{GEO})")}
    for g, ids in ENABLE_EXISTING_ADS.items():
        for a in ids:
            st = ad_state.get(a)
            if not st or st[1] in ("DISAPPROVED",): errs.append(f"ad {a} missing or disapproved: {st}")
    plan = dict(plan_name="AMB-1002-SEARCH-LAUNCH-1", customer_id=CID, exact_account_name=EXACT_NAME, never_write_to_mcc="3373711342",
                authorization="staged authorization 2026-10-02 (Green Marketing): create paused -> read back -> enable",
                stage_A=dict(url_fix={a: MAINT_URL for a in URL_FIX}, new_rsas=NEW_RSAS, new_sitelink=GEO_SITELINK),
                stage_C=dict(enable_ads=ENABLE_EXISTING_ADS, enable_new_rsas=list(NEW_RSAS), enable_keywords={f"{g}~{k}": v for (g, k), v in paused_kw.items()},
                             keep_paused=KEEP_PAUSED_ADS, remove_labels=REMOVE_LABELS, link_sitelinks=LINK_SITELINKS, pause_campaign_assets=PAUSE_CAMPAIGN_ASSET),
                unchanged="budgets, bidding/ceilings, schedules, locations, devices, conversions, negatives")
    plan["fingerprint"] = approval_code({k: v for k, v in plan.items() if k != "fingerprint"})
    if errs:
        sys.exit("HARD STOP:\n  " + "\n  ".join(errs))

    def mutate(ops, validate):
        rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.validate_only = validate
        rq.mutate_operations.extend(ops); return svc("GoogleAdsService").mutate(request=rq)

    def mo(lst):
        m = c.get_type("MutateOperation"); lst.append(m); return m

    def stage_a_ops():
        ops = []
        for a in URL_FIX:
            m = mo(ops); x = m.ad_operation.update; x.resource_name = svc("AdService").ad_path(CID, a); x.final_urls.append(MAINT_URL)
            m.ad_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["final_urls"]))
        for k, r in NEW_RSAS.items():
            m = mo(ops); x = m.ad_group_ad_operation.create
            x.ad_group = svc("AdGroupService").ad_group_path(CID, r["ad_group"]); x.status = c.enums.AdGroupAdStatusEnum.PAUSED
            x.ad.final_urls.append(r["url"]); rsa = x.ad.responsive_search_ad
            for coll, items in ((rsa.headlines, r["h"]), (rsa.descriptions, r["d"])):
                for t in items:
                    a = c.get_type("AdTextAsset"); a.text = t; coll.append(a)
            rsa.path1, rsa.path2 = r["path1"], r["path2"]
        m = mo(ops); a = m.asset_operation.create; a.resource_name = svc("AssetService").asset_path(CID, -1)
        a.final_urls.append(GEO_SITELINK["url"]); a.sitelink_asset.link_text = GEO_SITELINK["link_text"]
        a.sitelink_asset.description1 = GEO_SITELINK["description1"]; a.sitelink_asset.description2 = GEO_SITELINK["description2"]
        return ops

    def stage_c_ops(new_ad_ids, geo_sitelink_id):
        ops = []
        fm = field_mask_pb2.FieldMask(paths=["status"])
        for g, ids in ENABLE_EXISTING_ADS.items():
            for a in ids:
                m = mo(ops); x = m.ad_group_ad_operation.update; x.resource_name = svc("AdGroupAdService").ad_group_ad_path(CID, g, a)
                x.status = c.enums.AdGroupAdStatusEnum.ENABLED; m.ad_group_ad_operation.update_mask.CopyFrom(fm)
        for k, (g, a) in new_ad_ids.items():
            m = mo(ops); x = m.ad_group_ad_operation.update; x.resource_name = svc("AdGroupAdService").ad_group_ad_path(CID, g, a)
            x.status = c.enums.AdGroupAdStatusEnum.ENABLED; m.ad_group_ad_operation.update_mask.CopyFrom(fm)
        for (g, k) in paused_kw:
            m = mo(ops); x = m.ad_group_criterion_operation.update; x.resource_name = svc("AdGroupCriterionService").ad_group_criterion_path(CID, g, k)
            x.status = c.enums.AdGroupCriterionStatusEnum.ENABLED; m.ad_group_criterion_operation.update_mask.CopyFrom(fm)
        for g, names in REMOVE_LABELS.items():
            cur = {r.ad_group_label.label.split("/")[-1] for r in q(c, f"SELECT ad_group_label.label FROM ad_group_label WHERE ad_group.id = {g}")}
            for n in names:
                if labels.get(n) in cur:
                    m = mo(ops); m.ad_group_label_operation.remove = svc("AdGroupLabelService").ad_group_label_path(CID, g, labels[n])
        for cid, assets in LINK_SITELINKS.items():
            existing = {(str(r.asset.id), E(r.campaign_asset.status)) for r in q(c, f"SELECT campaign.id, asset.id, campaign_asset.status FROM campaign_asset WHERE campaign.id = {cid} AND campaign_asset.field_type = 'SITELINK'")}
            for aid in assets:
                aid = geo_sitelink_id if aid == "NEW_GEO_SITELINK" else aid
                if aid is None: continue
                if (aid, "ENABLED") in existing: continue
                if any(e[0] == aid for e in existing):
                    m = mo(ops); x = m.campaign_asset_operation.update; x.resource_name = svc("CampaignAssetService").campaign_asset_path(CID, cid, aid, "SITELINK")
                    x.status = c.enums.AssetLinkStatusEnum.ENABLED; m.campaign_asset_operation.update_mask.CopyFrom(fm)
                else:
                    m = mo(ops); x = m.campaign_asset_operation.create; x.campaign = svc("CampaignService").campaign_path(CID, cid)
                    x.asset = svc("AssetService").asset_path(CID, aid); x.field_type = c.enums.AssetFieldTypeEnum.SITELINK
        for cid, aid, ft, _ in PAUSE_CAMPAIGN_ASSET:
            m = mo(ops); x = m.campaign_asset_operation.update; x.resource_name = svc("CampaignAssetService").campaign_asset_path(CID, cid, aid, ft)
            x.status = c.enums.AssetLinkStatusEnum.PAUSED; m.campaign_asset_operation.update_mask.CopyFrom(fm)
        return ops

    if mode == "plan":
        res = {}
        try:
            mutate(stage_a_ops(), True); res["A"] = "VALIDATED"
        except Exception as ex:
            res["A"] = "FAILED " + str(re.findall(r'message: "([^"]+)"', str(ex))[:3]) + str(re.findall(r"index: (\d+)", str(ex))[:4])
        stand_in = {k: (r["ad_group"], "825585199661") for k, r in NEW_RSAS.items()}   # structure check only
        try:
            ops_c = stage_c_ops({}, "424481139482"); mutate(ops_c, True); res["C"] = f"VALIDATED {len(ops_c)} (new-RSA enables validated after creation)"
        except Exception as ex:
            res["C"] = "FAILED " + str(re.findall(r'message: "([^"]+)"', str(ex))[:3]) + str(re.findall(r"index: (\d+)", str(ex))[:4])
        plan["preflight"] = res
        plan["fingerprint"] = approval_code({k: v for k, v in plan.items() if k != "fingerprint"})
        (PLANS / "AMB-1002-SEARCH-LAUNCH-1.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print("preflight", res, "| keywords to enable", paused_kw, "| fingerprint", plan["fingerprint"])
        return
    # ---------------- run ----------------
    out = RECEIPTS / "AMB-1002-SEARCH-LAUNCH-1-EXECUTED.json"
    if out.exists():
        sys.exit("ABORT: receipt exists")
    saved = json.loads((PLANS / "AMB-1002-SEARCH-LAUNCH-1.json").read_text(encoding="utf-8"))
    rec = dict(plan="AMB-1002-SEARCH-LAUNCH-1", fingerprint=saved["fingerprint"], started_local=datetime.datetime.now(TZ).isoformat())
    try:
        resp = mutate(stage_a_ops(), False)
    except Exception as ex:
        rec["status"] = "FAILED_STAGE_A_NOTHING_WRITTEN"; rec["error"] = re.findall(r'message: "([^"]+)"', str(ex))[:4]
        out.write_text(json.dumps(rec, indent=1), encoding="utf-8"); sys.exit(rec["error"])
    res = [r for r in resp.mutate_operation_responses]
    names = [getattr(r, f).resource_name for r in res for f in ("ad_result", "ad_group_ad_result", "asset_result") if r._pb.HasField(f)]
    rec["stage_A"] = names
    new_ad_ids = {}
    keys = list(NEW_RSAS)
    for n in [x for x in names if "/adGroupAds/" in x]:
        g, a = n.split("/")[-1].split("~"); new_ad_ids[keys[len(new_ad_ids)]] = (g, a)
    geo_sl = next(x.split("/")[-1] for x in names if "/assets/" in x)
    rec["new_ad_ids"] = new_ad_ids; rec["geo_sitelink_asset"] = geo_sl
    # ---- stage B readback ----
    chk = []
    for a in URL_FIX:
        r = q(c, f"SELECT ad_group_ad.status, ad_group_ad.ad.final_urls FROM ad_group_ad WHERE ad_group_ad.ad.id = {a}")[0]
        chk.append((f"ad {a} URL -> heating-services, still PAUSED", list(r.ad_group_ad.ad.final_urls) == [MAINT_URL] and E(r.ad_group_ad.status) == "PAUSED"))
    for k, (g, a) in new_ad_ids.items():
        r = q(c, f"""SELECT ad_group_ad.status, ad_group_ad.ad.final_urls, ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions,
                ad_group_ad.ad.responsive_search_ad.path1, ad_group_ad.ad.responsive_search_ad.path2 FROM ad_group_ad WHERE ad_group_ad.ad.id = {a}""")[0].ad_group_ad
        rsa = r.ad.responsive_search_ad
        chk.append((f"{k} {a} PAUSED, URL, 15H/4D, paths", E(r.status) == "PAUSED" and list(r.ad.final_urls) == [NEW_RSAS[k]["url"]]
                    and sorted(h.text for h in rsa.headlines) == sorted(NEW_RSAS[k]["h"]) and sorted(d.text for d in rsa.descriptions) == sorted(NEW_RSAS[k]["d"])
                    and (rsa.path1, rsa.path2) == (NEW_RSAS[k]["path1"], NEW_RSAS[k]["path2"])))
    r = q(c, f"SELECT asset.sitelink_asset.link_text, asset.final_urls FROM asset WHERE asset.id = {geo_sl}")[0]
    chk.append(("geothermal sitelink text + URL", r.asset.sitelink_asset.link_text == GEO_SITELINK["link_text"] and list(r.asset.final_urls) == [GEO_SITELINK["url"]]))
    rec["stage_B_readback"] = [{"check": k, "pass": v} for k, v in chk]
    if not all(v for _, v in chk):
        rec["status"] = "STOPPED_AFTER_B_READBACK_FAIL"; out.write_text(json.dumps(rec, indent=1), encoding="utf-8"); sys.exit("readback B failed - stage C not run")
    # ---- stage C enable ----
    try:
        resp = mutate(stage_c_ops(new_ad_ids, geo_sl), False)
        rec["stage_C"] = len(resp.mutate_operation_responses)
    except Exception as ex:
        rec["status"] = "PARTIAL_STAGE_C_NOT_APPLIED"; rec["error"] = re.findall(r'message: "([^"]+)"', str(ex))[:4]
        out.write_text(json.dumps(rec, indent=1), encoding="utf-8"); sys.exit(f"stage C failed atomically (nothing from C written): {rec['error']}")
    chk2 = []
    all_ads = [a for ids in ENABLE_EXISTING_ADS.values() for a in ids] + [a for _, a in new_ad_ids.values()]
    st = {str(r.ad_group_ad.ad.id): (E(r.ad_group_ad.status), E(r.ad_group_ad.policy_summary.approval_status), E(r.ad_group_ad.policy_summary.review_status))
          for r in q(c, f"SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status FROM ad_group_ad WHERE ad_group_ad.ad.id IN ({','.join(all_ads)})")}
    chk2.append((f"{len(all_ads)} ads ENABLED", all(st[a][0] == "ENABLED" for a in all_ads)))
    kst = {f"{r.ad_group.id}~{r.ad_group_criterion.criterion_id}": E(r.ad_group_criterion.status) for r in q(c,
           f"SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.status FROM ad_group_criterion WHERE ad_group.id IN ({','.join(sorted(ENABLE_KEYWORDS))}) AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = FALSE")}
    chk2.append((f"{len(paused_kw)} keywords ENABLED", all(kst.get(f"{g}~{k}") == "ENABLED" for g, k in paused_kw)))
    kp = {str(r.ad_group_ad.ad.id): E(r.ad_group_ad.status) for r in q(c, f"SELECT ad_group_ad.ad.id, ad_group_ad.status FROM ad_group_ad WHERE ad_group_ad.ad.id IN ({','.join(KEEP_PAUSED_ADS)})")}
    chk2.append(("Housing-limited + unverified-claim ads still PAUSED", all(v == "PAUSED" for v in kp.values())))
    for cid, aid, ft, _ in PAUSE_CAMPAIGN_ASSET:
        r = q(c, f"SELECT campaign_asset.status FROM campaign_asset WHERE campaign_asset.resource_name = 'customers/{CID}/campaignAssets/{cid}~{aid}~{ft}'")
        chk2.append((f"campaign {cid} {ft} {aid} PAUSED", bool(r) and E(r[0].campaign_asset.status) == "PAUSED"))
    for cid, assets in LINK_SITELINKS.items():
        ex_ = {str(r.asset.id): E(r.campaign_asset.status) for r in q(c, f"SELECT campaign.id, asset.id, campaign_asset.status FROM campaign_asset WHERE campaign.id = {cid} AND campaign_asset.field_type = 'SITELINK'")}
        want = [geo_sl if a == "NEW_GEO_SITELINK" else a for a in assets]
        chk2.append((f"campaign {cid} sitelinks enabled {want}", all(ex_.get(a) == "ENABLED" for a in want)))
    rec["stage_C_readback"] = [{"check": k, "pass": v} for k, v in chk2]
    rec["policy_after_enable"] = st
    rec["status"] = "EXECUTED" if all(v for _, v in chk2) else "EXECUTED_READBACK_FAIL"
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat()
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    for k, v in chk + chk2:
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(rec["status"], rec["finished_local"], "new ads", new_ad_ids, "geo sitelink", geo_sl)


if __name__ == "__main__":
    main()
