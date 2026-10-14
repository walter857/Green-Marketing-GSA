#!/usr/bin/env python3
"""Ambient | 2026-10-02 | Emergency Heating Repair + Geothermal Heat Pump landing-page activation. BUILD + validate_only.

EXTERNAL WRITES: 0. Every mutate below runs with validate_only=True.

Work orders: work-orders/work-order-emergency-heating-repair-lp-2026-10-01.yaml (Emergency Heating Repair, draft)
             work-orders/work-order-geothermal-heat-pump-lp-2026-10-01.yaml     (Geothermal Heat Pump, draft)
Page QA (Chrome, desktop + 390 px, 2026-10-01/02): both URLs HTTP 200, no redirect, noindex, H1 matches service,
every tel: link dials (410) 705-6354. Evidence: snapshots/lp-qa-2026-10-01.json.

Plans written (each service separately approvable):
  AMB-1002-EMER-CREATE-1   2 RSAs PAUSED + 1 PHRASE keyword PAUSED in SKAG | Emergency Heating Repair 204129717047
  AMB-1002-GEO-CREATE-1    2 RSAs PAUSED in SKAG | Geothermal Heat Pump 204129719007 + pause the ad-group sitelink link
                           290641223062 ('Dehumidification Services' -> main site)
  AMB-1002-EMER-ENABLE-1.DRAFT / AMB-1002-GEO-ENABLE-1.DRAFT   need created ids, approved ads, readback 0 FAIL and the gates.
No budget, bid, CPC-ceiling, schedule, location, conversion, negative-keyword, website or tracking change.
"""
from __future__ import annotations
import sys, json, re, hashlib, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, SNAP, PLANS, E, CID, EXACT_NAME, CLIENT_DIR  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
import yaml  # noqa: E402

STAMP = "2026-10-02"
O = "https://offer.ambientcoolingandheating.com"
REPAIR, GEO = "24257819463", "24274160783"
EMER_AG, GEO_AG = "204129717047", "204129719007"
EMER_URL, GEO_URL = f"{O}/emergency-heating-repair/", f"{O}/geothermal-heat-pump/"
STRAY_SITELINK = "290641223062"

H, D = "HEADLINE_1", "DESCRIPTION_1"
EMER_A = dict(label="RSA A - keyword and location led", path1="Emergency", path2="Heating", h=[
    "Emergency Heating Repair", "Emergency Furnace Repair", "Heating Stopped Working?", "No Heat? Call Mon-Fri 8-4",
    "Heating Repair In Central MD", "Severn Heating Repair", "Severna Park Heating Repair", "Columbia MD Heating Repair",
    "Ask About The Next Visit", "Free Heating Repair Quote", "No-Heat Diagnosis", "Clear Repair Options",
    "Furnace & Heating Repair", "Business-Hours Heating Help", "Local Maryland Service"], d=[
    ("Heating stopped? Call Mon-Fri, 8 a.m.-4 p.m. to check the next available repair visit.", D),
    "We assess the system, explain what failed and confirm the repair before work begins.",
    "Emergency heating repair for homes in Severn, Severna Park and Columbia, Maryland.",
    "Send a repair request online or call during business hours for a free quote."])
EMER_B = dict(label="RSA B - problem led", path1="Emergency", path2="Heating", h=[
    "Heat Not Working?", "Urgent Heating Repair", "Emergency Heater Repair", "Furnace Stopped Heating?",
    "Calls Answered Mon-Fri 8-4", "Next Available Appointment", "Heating Breakdown Help", "Central Maryland Heating",
    "Glen Burnie Heating Repair", "Annapolis Heating Repair", "Get A Free Repair Quote", "Assessment Before Repair",
    "Clear Scope Before Work", "Home Heating Repair", "Talk To Our Heating Team"], d=[
    ("Calls answered Mon-Fri, 8 a.m.-4 p.m. Ask about the next available heating repair visit.", D),
    "Tell us what the system is doing. We assess it and confirm the repair scope first.",
    "Heating repair for homes in Annapolis, Glen Burnie, Severn and Columbia, MD.",
    "Request a free heating repair quote online, or call during business hours."])
GEO_A = dict(label="RSA A - service and location led", path1="Geothermal", path2="Heat-Pump", h=[
    "Geothermal Heat Pumps", "Geothermal Heat Pump Service", "Geothermal Heating & Cooling", "New Geothermal System Quote",
    "Plan A Geothermal Install", "Geothermal Replacement Help", "Central MD Geothermal", "Severn Geothermal Heat Pumps",
    "Columbia Geothermal Systems", "Annapolis Geothermal Systems", "Free Geothermal Quote", "Property-Specific Review",
    "Ground-Loop System Review", "Clear Scope Before Work", "Talk To Our Geothermal Team"], d=[
    "Considering geothermal or replacing an existing system? Request a property review.",
    "We review your home, equipment and ground loop, then explain the options and scope.",
    "Geothermal heat pump systems for homes in Severn, Severna Park and Columbia, MD.",
    "Request a free geothermal quote online or call to discuss your next step."])
GEO_B = dict(label="RSA B - planning led", path1="Geothermal", path2="Heat-Pump", h=[
    "Considering Geothermal?", "Geothermal Heat Pump Quotes", "Replacing A Geothermal Unit?", "New Geothermal Consultation",
    "Geothermal For Your Home", "Maryland Geothermal Systems", "Assess Your Property First", "Geothermal Options Explained",
    "Glen Burnie Geothermal", "Crofton Geothermal Heat Pump", "Request Geothermal Service", "Get A Free Geothermal Quote",
    "Geothermal Project Planning", "Home Comfort Assessment", "Central Maryland Service"], d=[
    "Planning a new geothermal system? Start with an assessment of your home and property.",
    "Replacing an older geothermal heat pump? Learn what must be evaluated first.",
    "Confirm the work and schedule with our team before any geothermal project starts.",
    "Ambient Cooling & Heating serves Central Maryland homes. Request a free quote."])
NEW_KEYWORDS = [dict(ad_group_id=EMER_AG, text="emergency furnace repair", match="PHRASE",
                     why="EXACT [emergency furnace repair] exists; the PHRASE twin lets 'emergency furnace repair near me' and "
                         "'... severn' reach the group. Furnace Repair negates 'emergency', so those searches have no other destination.")]

# claims that are barred (client.yaml barred_claims) or unverified; ad text may not contain them
BARRED = [r"24\s*/\s*7", r"24[- ]hour", r"same[- ]day", r"\bimmediate", r"\bfast\b", r"\bquick", r"\bguarant", r"\bwarrant", r"\blicen[cs]",
          r"\binsured\b", r"\bcertified\b", r"\bbest\b", r"#1", r"\byears?\b", r"\$\d", r"\bdiscount", r"\bfinanc", r"\brated\b",
          r"\bcustomer reviews?\b|\b\d[\s-]*star\b|\breviewed\b", r"\bspecialist", r"\bexpert", r"\bcheap", r"\baffordable", r"\b\d{3}[-.\s)]+\d{3}[-.\s]+\d{4}\b", r"!",
          r"\brepair\b(?=.*geotherm)|geotherm.*\brepair\b"]
WO = {}
cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
for k, f in (("emer", "work-order-emergency-heating-repair-lp-2026-10-01"), ("geo", "work-order-geothermal-heat-pump-lp-2026-10-01")):
    WO[k] = yaml.safe_load((CLIENT_DIR / "work-orders" / f"{f}.yaml").read_text(encoding="utf-8"))
    errs = validate_work_order(WO[k], cl)
    print(f"work order {f}: {'VALID' if not errs else errs}")
    if errs:
        sys.exit("HARD STOP: work order invalid")


def copy_checks(rsa, service):
    errs = []
    hs = [h if isinstance(h, str) else h[0] for h in rsa["h"]]
    ds = [d if isinstance(d, str) else d[0] for d in rsa["d"]]
    if len(hs) != 15 or len(ds) != 4:
        errs.append(f"{rsa['label']}: {len(hs)} headlines / {len(ds)} descriptions")
    for t in hs:
        if len(t) > 30: errs.append(f"headline >30 ({len(t)}): {t}")
    for t in ds:
        if len(t) > 90: errs.append(f"description >90 ({len(t)}): {t}")
    for p in ("path1", "path2"):
        if len(rsa[p]) > 15: errs.append(f"{p} >15: {rsa[p]}")
    if len({t.lower() for t in hs}) != len(hs): errs.append(f"{rsa['label']}: duplicate headline")
    for t in hs + ds:
        for rx in BARRED:
            if service == "emer" and rx.startswith(r"\brepair\b(?=.*geotherm)"):
                continue
            if re.search(rx, t, re.I):
                errs.append(f"barred/unverified pattern {rx!r} in: {t}")
    return errs


def rsa_payload(ag_id, url, rsa):
    def item(x, slot):
        return {"text": x, "pin": "UNSPECIFIED"} if isinstance(x, str) else {"text": x[0], "pin": x[1]}
    return {"op": "CREATE_RSA_PAUSED", "ad_group_id": ag_id, "final_url": url, "label": rsa["label"], "path1": rsa["path1"],
            "path2": rsa["path2"], "headlines": [item(x, "H") for x in rsa["h"]], "descriptions": [item(x, "D") for x in rsa["d"]],
            "status": "PAUSED", "tracking_url_template": "", "final_url_suffix": "", "final_mobile_urls": []}


def read_state(c):
    """Fresh read of both campaigns and everything the plans must leave unchanged (shared by build and executor)."""
    camps = {}
    for r in q(c, f"""SELECT campaign.id, campaign.name, campaign.status, campaign.bidding_strategy_type, campaign.target_spend.cpc_bid_ceiling_micros,
            campaign_budget.id, campaign_budget.amount_micros, campaign.network_settings.target_search_network, campaign.network_settings.target_content_network,
            campaign.geo_target_type_setting.positive_geo_target_type, campaign.tracking_url_template, campaign.final_url_suffix, campaign.ai_max_setting.enable_ai_max
            FROM campaign WHERE campaign.id IN ({REPAIR},{GEO})"""):
        x = r.campaign
        camps[str(x.id)] = dict(name=x.name, status=E(x.status), bidding=E(x.bidding_strategy_type), ceiling=x.target_spend.cpc_bid_ceiling_micros,
                                budget_id=str(r.campaign_budget.id), budget=r.campaign_budget.amount_micros, partners=x.network_settings.target_search_network,
                                display=x.network_settings.target_content_network, geo=E(x.geo_target_type_setting.positive_geo_target_type),
                                tt=x.tracking_url_template, sfx=x.final_url_suffix, ai_max=x.ai_max_setting.enable_ai_max)
    ags = {}
    for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group.labels, ad_group.tracking_url_template, ad_group.final_url_suffix
            FROM ad_group WHERE campaign.id IN ({REPAIR},{GEO}) AND ad_group.status != 'REMOVED'"""):
        ags[str(r.ad_group.id)] = dict(campaign=str(r.campaign.id), name=r.ad_group.name, status=E(r.ad_group.status), labels=sorted(r.ad_group.labels),
                                       tt=r.ad_group.tracking_url_template, sfx=r.ad_group.final_url_suffix)
    ads = {}
    for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls, ad_group_ad.policy_summary.approval_status
            FROM ad_group_ad WHERE campaign.id IN ({REPAIR},{GEO}) AND ad_group_ad.status != 'REMOVED'"""):
        ads[str(r.ad_group_ad.ad.id)] = dict(ad_group=str(r.ad_group.id), status=E(r.ad_group_ad.status), urls=list(r.ad_group_ad.ad.final_urls),
                                             approval=E(r.ad_group_ad.policy_summary.approval_status))
    kws = {}
    for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
            ad_group_criterion.negative, ad_group_criterion.status, ad_group_criterion.approval_status, ad_group_criterion.final_urls
            FROM ad_group_criterion WHERE campaign.id IN ({REPAIR},{GEO}) AND ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.status != 'REMOVED'"""):
        k = r.ad_group_criterion
        kws[f"{r.ad_group.id}~{k.criterion_id}"] = dict(ad_group=str(r.ad_group.id), text=k.keyword.text, match=E(k.keyword.match_type), negative=k.negative,
                                                         status=E(k.status), approval=E(k.approval_status), url_override=list(k.final_urls))
    crit = sorted((str(r.campaign.id), E(r.campaign_criterion.type), str(r.campaign_criterion.criterion_id), r.campaign_criterion.negative,
                   E(r.campaign_criterion.status), round(r.campaign_criterion.bid_modifier, 4))
                  for r in q(c, f"""SELECT campaign.id, campaign_criterion.type, campaign_criterion.criterion_id, campaign_criterion.negative,
                      campaign_criterion.status, campaign_criterion.bid_modifier FROM campaign_criterion WHERE campaign.id IN ({REPAIR},{GEO})"""))
    att = sorted((str(r.campaign.id), str(r.shared_set.id), E(r.campaign_shared_set.status)) for r in q(c,
                 f"SELECT campaign.id, shared_set.id, campaign_shared_set.status FROM campaign_shared_set WHERE campaign.id IN ({REPAIR},{GEO})"))
    links = sorted((r.campaign_asset.resource_name, E(r.campaign_asset.status)) for r in q(c,
                   f"SELECT campaign.id, campaign_asset.resource_name, campaign_asset.status FROM campaign_asset WHERE campaign.id IN ({REPAIR},{GEO})"))
    aglinks = {r.ad_group_asset.resource_name: dict(status=E(r.ad_group_asset.status), field=E(r.ad_group_asset.field_type), asset=str(r.asset.id),
                                                     urls=list(r.asset.final_urls), text=r.asset.sitelink_asset.link_text)
               for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_asset.resource_name, ad_group_asset.status, ad_group_asset.field_type, asset.id,
                   asset.final_urls, asset.sitelink_asset.link_text FROM ad_group_asset WHERE campaign.id IN ({REPAIR},{GEO})""")}
    conv = sorted((str(r.conversion_action.id), r.conversion_action.primary_for_goal, E(r.conversion_action.status)) for r in q(c,
                  "SELECT conversion_action.id, conversion_action.primary_for_goal, conversion_action.status FROM conversion_action WHERE conversion_action.status = 'ENABLED'"))
    labels = {r.label.name: r.label.resource_name for r in q(c, "SELECT label.name, label.resource_name FROM label")}
    stray = f"customers/{CID}/adGroupAssets/{GEO_AG}~{STRAY_SITELINK}~SITELINK"

    return dict(camps=camps, ags=ags, ads=ads, kws=kws, crit=crit, att=att, links=links, aglinks=aglinks, conv=conv, labels=labels, stray=stray)


def baseline_hash(st, skip_ads=(), skip_kws=()):
    """Configuration-only fingerprint of every resource the plans must NOT change. Google policy-review fields are excluded
    because Google can change them on its own; the plan's own new resources and the stray link it pauses are excluded."""
    ads = {k: {kk: vv for kk, vv in v.items() if kk != "approval"} for k, v in st["ads"].items() if k not in skip_ads}
    kws = {k: {kk: vv for kk, vv in v.items() if kk != "approval"} for k, v in st["kws"].items() if k not in skip_kws}
    base = dict(campaigns=st["camps"], ad_groups=st["ags"], ads=ads, keywords=kws, campaign_criteria=st["crit"],
                shared_set_attachments=st["att"], campaign_asset_links=st["links"],
                ad_group_asset_links={k: v for k, v in st["aglinks"].items() if k != st["stray"]}, conversion_actions=st["conv"])
    return hashlib.sha256(json.dumps(base, sort_keys=True, default=str).encode()).hexdigest()[:16]


def main():
    c = client()
    ident = identity_gate(c, verbose=True)
    out = {"identity": {k: ident[k] for k in ("customer_id", "descriptive_name", "checked_local")}, "errors": [], "warnings": []}
    err, warn = out["errors"], out["warnings"]

    st = read_state(c)
    camps, ags, ads, kws, aglinks, labels, stray = (st[k] for k in ("camps", "ags", "ads", "kws", "aglinks", "labels", "stray"))

    # ---------------- gates on the live state ----------------
    if ags.get(EMER_AG, {}).get("name") != "SKAG | Emergency Heating Repair": err.append("Emergency ad group name/id mismatch")
    if ags.get(GEO_AG, {}).get("name") != "SKAG | Geothermal Heat Pump": err.append("Geothermal ad group name/id mismatch")
    emer_ads = [a for a in ads.values() if a["ad_group"] == EMER_AG]
    geo_ads = {i: a for i, a in ads.items() if a["ad_group"] == GEO_AG}
    if emer_ads: warn.append(f"Emergency ad group already has {len(emer_ads)} ads")
    if any(a["status"] == "ENABLED" for a in geo_ads.values()): err.append("Geothermal already has an ENABLED ad")
    if aglinks.get(stray, {}).get("status") != "ENABLED": warn.append(f"stray sitelink link not ENABLED: {aglinks.get(stray)}")
    if camps[REPAIR]["ceiling"] != 18_000_000 or camps[REPAIR]["budget"] != 85_000_000: err.append("repair ceiling/budget drifted from $18/$85")
    if camps[GEO]["budget"] != 20_000_000: err.append("geothermal budget drifted from $20")
    for k, v in kws.items():
        if v["url_override"]: warn.append(f"keyword URL override present {k} {v['url_override']}")
    for a in camps.values():
        if a["tt"] or a["sfx"]: warn.append(f"campaign tracking template/suffix present: {a}")
    emer_kw = sorted((v["text"], v["match"], v["status"], v["approval"]) for v in kws.values() if v["ad_group"] == EMER_AG and not v["negative"])
    geo_kw = sorted((v["text"], v["match"], v["status"], v["approval"]) for v in kws.values() if v["ad_group"] == GEO_AG and not v["negative"])
    for nk in NEW_KEYWORDS:
        if any(v["ad_group"] == nk["ad_group_id"] and v["text"] == nk["text"] and v["match"] == nk["match"] for v in kws.values()):
            err.append(f"keyword already exists: {nk}")

    # ---------------- local copy checks ----------------
    for rsa, svc in ((EMER_A, "emer"), (EMER_B, "emer"), (GEO_A, "geo"), (GEO_B, "geo")):
        e = copy_checks(rsa, svc)
        err.extend(e)
    for a, b in ((EMER_A, EMER_B), (GEO_A, GEO_B)):
        shared = {x.lower() for x in a["h"] if isinstance(x, str)} & {x.lower() for x in b["h"] if isinstance(x, str)}
        out.setdefault("rsa_headline_overlap", {})[a["label"][:5] + "/" + b["label"][:5]] = sorted(shared)

    # ---------------- unrelated-resource baseline (must be identical at execution and readback) ----------------
    base_hash = baseline_hash(st)

    # ---------------- validate_only preflight ----------------
    pf = out["preflight"] = {}

    def vo(svc, method, req_type, ops, label):
        rq = c.get_type(req_type); rq.customer_id = CID; rq.operations.extend(ops)
        rq.partial_failure = False; rq.validate_only = True
        try:
            getattr(c.get_service(svc), method)(request=rq)
            pf[label] = f"VALIDATED {len(ops)}"
        except Exception as ex:
            m = re.findall(r'message: "([^"]+)"', str(ex))
            pf[label] = f"FAILED: {m[:3] or str(ex)[:300]}"
            err.append(f"preflight {label}: {m[:3] or str(ex)[:200]}")

    def rsa_op(p):
        o = c.get_type("AdGroupAdOperation"); a = o.create
        a.ad_group = c.get_service("AdGroupService").ad_group_path(CID, p["ad_group_id"])
        a.status = c.enums.AdGroupAdStatusEnum.PAUSED
        a.ad.final_urls.append(p["final_url"])
        r = a.ad.responsive_search_ad
        for coll, items in ((r.headlines, p["headlines"]), (r.descriptions, p["descriptions"])):
            for h in items:
                t = c.get_type("AdTextAsset"); t.text = h["text"]
                if h["pin"] != "UNSPECIFIED":
                    t.pinned_field = getattr(c.enums.ServedAssetFieldTypeEnum, h["pin"])
                coll.append(t)
        r.path1, r.path2 = p["path1"], p["path2"]
        return o

    def kw_op(k):
        o = c.get_type("AdGroupCriterionOperation"); x = o.create
        x.ad_group = c.get_service("AdGroupService").ad_group_path(CID, k["ad_group_id"])
        x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
        x.keyword.text = k["text"]; x.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, k["match"])
        return o

    from google.protobuf import field_mask_pb2
    emer_ops = [rsa_payload(EMER_AG, EMER_URL, EMER_A), rsa_payload(EMER_AG, EMER_URL, EMER_B)] + \
               [dict(op="CREATE_KEYWORD_PAUSED", **k) for k in NEW_KEYWORDS]
    geo_ops = [rsa_payload(GEO_AG, GEO_URL, GEO_A), rsa_payload(GEO_AG, GEO_URL, GEO_B),
               dict(op="PAUSE_AD_GROUP_ASSET_LINK", resource_name=stray, ad_group_id=GEO_AG, asset_id=STRAY_SITELINK, field_type="SITELINK",
                    before=aglinks.get(stray), after_status="PAUSED",
                    why="main-site destination (owner rule 2026-09-24: paid destinations must be offer pages) and unrelated to geothermal; "
                        "it would serve beside the new geothermal ads")]
    vo("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest", [rsa_op(p) for p in emer_ops if p["op"] == "CREATE_RSA_PAUSED"], "EMER create 2 RSAs PAUSED")
    vo("AdGroupCriterionService", "mutate_ad_group_criteria", "MutateAdGroupCriteriaRequest", [kw_op(k) for k in NEW_KEYWORDS], "EMER create 1 PHRASE keyword PAUSED")
    vo("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest", [rsa_op(p) for p in geo_ops if p["op"] == "CREATE_RSA_PAUSED"], "GEO create 2 RSAs PAUSED")
    o = c.get_type("AdGroupAssetOperation"); o.update.resource_name = stray
    o.update.status = c.enums.AssetLinkStatusEnum.PAUSED; o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
    vo("AdGroupAssetService", "mutate_ad_group_assets", "MutateAdGroupAssetsRequest", [o], "GEO pause stray ad-group sitelink link")

    unchanged = {"budget": "$85 repair (15885327972) / $20 geothermal (15887323571), unchanged",
                 "bidding": "Maximize Clicks (TARGET_SPEND); repair ceiling $18.00, geothermal ceiling $38.00, unchanged",
                 "locations": "75 PRESENCE targets on both campaigns, unchanged", "schedule": "Mon-Fri 08:00-16:00 America/New_York, 5 rows, unchanged",
                 "conversions": "no conversion action or goal touched", "negatives": "no negative added, removed or changed",
                 "tracking": "no tracking template / final URL suffix exists at account, campaign, ad group, ad or keyword level; none added",
                 "website": "no website, GTM, WhatConverts or Business Profile change"}
    common = dict(customer_id=CID, exact_account_name=EXACT_NAME, never_write_to_mcc="3373711342", built_local=STAMP,
                  approval_class="create-paused", everything_created_paused=True, nothing_enabled=True, nothing_removed=True,
                  unchanged=unchanged, unrelated_resource_baseline_sha256_16=base_hash)
    emer = dict(plan_name="AMB-1002-EMER-CREATE-1", exact_service="Emergency Heating Repair",
                work_order="work-orders/work-order-emergency-heating-repair-lp-2026-10-01.yaml",
                campaign={"id": REPAIR, "name": camps[REPAIR]["name"]}, ad_group={"id": EMER_AG, "name": "SKAG | Emergency Heating Repair"},
                effective_url_before="none - the ad group has 0 ads, so it has no destination and cannot serve",
                effective_url_after_create="none - new RSAs are PAUSED; after ENABLE: " + EMER_URL,
                existing_keywords_untouched=emer_kw, supersedes_copy="AMB-0922-BUILD-1 held Emergency RSA payloads (never uploaded)", **common,
                operations=emer_ops)
    geo = dict(plan_name="AMB-1002-GEO-CREATE-1", exact_service="Geothermal Heat Pump",
               paid_sub_service="geothermal heat pump system inquiries + new-system installation / replacement consultation; geothermal REPAIR "
                                "stays out of paid scope (ad-group PHRASE negative 'repair' unchanged)",
               work_order="work-orders/work-order-geothermal-heat-pump-lp-2026-10-01.yaml",
               campaign={"id": GEO, "name": camps[GEO]["name"]}, ad_group={"id": GEO_AG, "name": "SKAG | Geothermal Heat Pump"},
               effective_url_before="none serving - 2 PAUSED RSAs " + ", ".join(sorted(geo_ads)) + " point at the main-site page "
                                    "https://ambientcoolingandheating.com/services/hvac/geothermal-hvac/ (left PAUSED and untouched)",
               effective_url_after_create="none - new RSAs are PAUSED; after ENABLE: " + GEO_URL,
               existing_keywords_untouched=geo_kw, supersedes_copy="AMB-0925-HELD-RSA-PAYLOADS geothermal entry (repair-led copy conflicts with the "
                                                                    "ad group's 'repair' negative)", **common, operations=geo_ops)
    for p, key in ((emer, "EMER"), (geo, "GEO")):
        p["operation_count"] = len(p["operations"])
        p["preflight"] = {k: v for k, v in pf.items() if k.startswith(key)}
        p["fingerprint"] = approval_code({k: v for k, v in p.items() if k != "fingerprint"})
    lbl = lambda n: labels.get(n, f"MISSING:{n}")
    emer_enable = dict(plan_name="AMB-1002-EMER-ENABLE-1", status="DRAFT - not approvable until AMB-1002-EMER-CREATE-1 executes, reads back "
                       "0 FAIL, both RSAs are APPROVED, and the availability fact below is confirmed",
                       gates=["Owner confirms: Ambient takes urgent no-heat / heating-breakdown repair calls Mon-Fri 08:00-16:00 and books the "
                              "next available technician visit (no time promise). Answering is already published; dispatch is the missing fact.",
                              "Both new RSAs APPROVED (or APPROVED_LIMITED) by Google policy review",
                              "Readback of the CREATE plan 0 FAIL and unrelated-resource baseline hash unchanged"],
                       operations=["enable RSA A (id from CREATE receipt)", "enable RSA B (id from CREATE receipt)",
                                   *[f"enable keyword {t} {m} (currently {s})" for t, m, s, _ in emer_kw], "enable new PHRASE emergency furnace repair",
                                   f"remove label WAITING_LP ({lbl('WAITING_LP')})", f"remove label WAITING_AVAILABILITY ({lbl('WAITING_AVAILABILITY')})"],
                       note="Ad group 204129717047 and campaign 24257819463 are already ENABLED; nothing else changes.")
    geo_enable = dict(plan_name="AMB-1002-GEO-ENABLE-1", status="DRAFT - not approvable until AMB-1002-GEO-CREATE-1 executes, reads back 0 FAIL "
                      "and both RSAs are APPROVED; developer removes the zeroed 'Offer Ends in' countdown from /geothermal-heat-pump/ first",
                      gates=["/geothermal-heat-pump/ no longer shows the 'Offer Ends in 00 DAY 00 HRS 00 MIN 00 SEC' countdown (an unverified "
                             "time-limited offer); re-checked in Chrome desktop + 390 px",
                             "Both new RSAs APPROVED (or APPROVED_LIMITED)", "Readback 0 FAIL and baseline hash unchanged"],
                      operations=["enable RSA A (id from CREATE receipt)", "enable RSA B (id from CREATE receipt)",
                                  f"remove label WAITING_LP ({lbl('WAITING_LP')})"],
                      note="Ad group, 5 keywords and campaign are already ENABLED; the $20/day budget is already inside the enabled total. "
                           "Enabling the two RSAs is the only switch that starts geothermal delivery.")
    if err:
        for e in err:
            print("  ERROR", e)
        sys.exit("HARD STOP: errors present - no plan written")
    PLANS.mkdir(parents=True, exist_ok=True)
    for p in (emer, geo):
        (PLANS / f"{p['plan_name']}.json").write_text(json.dumps(p, indent=1), encoding="utf-8")
    for p in (emer_enable, geo_enable):
        (PLANS / f"{p['plan_name']}.DRAFT.json").write_text(json.dumps(p, indent=1), encoding="utf-8")
    out["plans"] = {p["plan_name"]: dict(fingerprint=p["fingerprint"], operations=p["operation_count"]) for p in (emer, geo)}
    out["baseline_hash"] = base_hash
    out["live"] = dict(emer_keywords=emer_kw, geo_keywords=geo_kw, geo_ads={i: (a["status"], a["urls"], a["approval"]) for i, a in geo_ads.items()},
                       stray_link=aglinks.get(stray), emer_labels=ags[EMER_AG]["labels"], geo_labels=ags[GEO_AG]["labels"])
    (SNAP / f"launch-build-{STAMP}.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print("\n=== PREFLIGHT (validate_only) ===")
    for k, v in pf.items(): print(f"  {k:44s} {v}")
    print("headline overlap between paired RSAs:", out.get("rsa_headline_overlap"))
    print("live:", json.dumps(out["live"], default=str))
    print(f"baseline hash {base_hash}")
    print(f"WARNINGS ({len(warn)}):"); [print("  ", w) for w in warn]
    print(f"ERRORS ({len(err)}):"); [print("  ", e) for e in err]
    for n, v in out["plans"].items(): print(f"PLAN {n}: {v['fingerprint']} / {v['operations']} ops")
    print("EXTERNAL WRITES: 0 (validate_only)")


if __name__ == "__main__":
    main()
