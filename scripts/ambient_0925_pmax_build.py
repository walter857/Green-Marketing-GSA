#!/usr/bin/env python3
"""Ambient | 2026-09-25 | Performance Max pilot: build PAUSED, gated launch.

Owner instruction 2026-09-25: build one focused PMax pilot completely, fund and enable it only
when evidence and tracking gates pass. This script:

  plan      builds AMB-0925-PMAX-1 (campaign shell) + the two asset-group payloads, checks every
            character limit and claim, and prints the fingerprint.
  validate  validate_only of the FULL build (shell + both asset groups). Images are not yet
            reviewed, so the validation run borrows already-approved account images as stand-ins
            purely to prove the structure; stand-ins are never created.
  execute   creates ONLY the shell, PAUSED: budget (own, non-shared, staged at the $20 of
            unallocated headroom so an accidental enable cannot breach $325), campaign, geo,
            language, schedule, negatives, campaign-level assets. Then sets campaign goals.
Asset groups are created later, from this payload, once reviewed images exist.
"""
from __future__ import annotations
import sys, json, re, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS
from gm_gsa.safety import approval_code
from google.protobuf import field_mask_pb2

PLAN_NAME = "AMB-0925-PMAX-1"
O = "https://offer.ambientcoolingandheating.com"
GEO_SOURCE = "24257819466"          # core Install/Replace campaign: 75 verified presence targets
CAMPAIGN_NAME = "PMax | Heating Replacement Pilot | Central MD | 2026-09 | HELD"
BUDGET_STAGED = 20.00               # headroom: $325 cap - $305 enabled; launch plan raises to $45
BUSINESS_NAME_ASSET = "80516971145"  # 'Ambient Cooling & Heating' (25 chars, verified identity)
LOGO_SQUARE = "218982449635"         # website logo 356x356, approved
LOGO_LANDSCAPE = "218984456832"      # website logo 964x242 (~4:1), approved
CALL_ASSET = "407995613637"          # (410) 705-6354, Mon-Fri 8-16, approved
CALLOUTS = {"422577771364": "Trained Technicians", "407418646876": "Professional Technicians",
            "422577760603": "Central Maryland Service", "349923938310": "Local Maryland Service",
            "407418627430": "Clear Recommendations", "407418646882": "Clear Service Options",
            "422477374526": "Homes and Businesses", "89063098370": "Get Free Online Quote"}
SITELINKS = {"410638278156": "HVAC Replacement", "410638276380": "HVAC Installation",
             "424481139482": "Heat Pump Replacement", "424666395915": "Heat Pump Installation",
             "424666371474": "Boiler Replacement"}
SNIPPET = ("Services", ["Furnace Replacement", "Heating Replacement", "Heating Installation",
                        "Heat Pump Replacement", "Heat Pump Installation"])
NEGATIVES = {  # PHRASE; audited individually - employment, training, DIY, parts-only, own brand
    "own_brand": ["ambient cooling", "ambient heating", "ambient hvac"],
    "employment": ["job", "jobs", "career", "careers", "salary", "hiring", "apprentice"],
    "training": ["hvac school", "hvac training", "hvac course", "hvac certification"],
    "diy_parts": ["diy", "how to", "youtube", "manual", "parts", "filters"],
}
AUTOMATION_OFF = ["TEXT_ASSET_AUTOMATION", "FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION",
                  "GENERATE_IMAGE_EXTRACTION", "GENERATE_IMAGE_ENHANCEMENT",
                  "GENERATE_DESIGN_VERSIONS_FOR_IMAGES",
                  "GENERATE_ENHANCED_YOUTUBE_VIDEOS"]
AUDIENCE_SIGNAL_LIST = "7950039478"  # All Converters (64 in Search) - the only first-party converter list

COMMON_D5 = "Call Mon-Fri, 8 a.m. to 4 p.m., or request your free quote online."
ASSET_GROUPS = {
    "AG_HEAT": dict(
        name="Heating & Furnace Replacement", final_url=f"{O}/hvac-replacement/", path1="Heating", path2="Replacement",
        headlines=["Furnace Replacement", "Heating Replacement", "Replace Your Furnace", "New Furnace Installation",
                   "Heating System Replacement", "Free Replacement Quote", "Central Maryland HVAC",
                   "Severn Furnace Replacement", "Columbia Heating Replacement", "Severna Park Furnace Install",
                   "Trained HVAC Technicians", "Clear Replacement Options", "Request a Free Quote", "New Furnace",
                   "Talk to a Technician"],
        long_headlines=["Furnace and heating replacement for homes in Severn, Severna Park and Columbia, MD",
                        "Request a free replacement quote from Ambient Cooling & Heating",
                        "Old furnace failing? Plan a heating system replacement with trained technicians",
                        "Heating replacement across Central Maryland, planned around your home",
                        "Compare replacement options clearly before you choose a new furnace"],
        descriptions=["Request a free heating replacement quote.",
                      "Trained technicians assess your current system and explain replacement options clearly.",
                      "Furnace and heating replacement for Severn, Severna Park and Columbia homes.",
                      "Plan a new furnace installation with Ambient Cooling & Heating in Central Maryland.",
                      COMMON_D5],
        search_themes=["furnace replacement", "furnace replacement near me", "new furnace installation", "replace furnace",
                       "heating system replacement", "heating replacement", "gas furnace replacement",
                       "furnace installation", "furnace replacement cost", "new furnace cost",
                       "heating system installation", "furnace installation near me"]),
    "AG_HP": dict(
        name="Heat Pump Replacement", final_url=f"{O}/heat-pump-replacement/", path1="Heat-Pump", path2="Replacement",
        headlines=["Heat Pump Replacement", "Replace Your Heat Pump", "Heat Pump Installation", "New Heat Pump Quote",
                   "Free Replacement Quote", "Severn Heat Pump Service", "Columbia Heat Pump Install",
                   "Severna Park Heat Pumps", "Central Maryland Heat Pumps", "Trained HVAC Technicians",
                   "Clear Replacement Options", "Request a Free Quote", "Talk to a Technician", "Heat Pumps",
                   "Plan Your Heat Pump Upgrade"],
        long_headlines=["Heat pump replacement for homes in Severn, Severna Park and Columbia, MD",
                        "Request a free heat pump replacement quote from Ambient Cooling & Heating",
                        "Heat pump not keeping up? Plan a replacement with trained technicians",
                        "Heat pump installation and replacement across Central Maryland",
                        "Compare heat pump replacement options clearly before you decide"],
        descriptions=["Request a free heat pump replacement quote.",
                      "Trained technicians assess your heat pump and explain replacement options clearly.",
                      "Heat pump replacement for Severn, Severna Park and Columbia homes.",
                      "Plan a new heat pump installation with Ambient Cooling & Heating in Central Maryland.",
                      COMMON_D5],
        search_themes=["heat pump replacement", "heat pump installation", "replace heat pump", "new heat pump",
                       "heat pump replacement cost", "heat pump installation near me", "heat pump system replacement",
                       "heat pump installer", "air source heat pump installation", "heat pump replacement near me"]),
}
IMAGE_TARGET = {"MARKETING_IMAGE": (4, "1200x628"), "SQUARE_MARKETING_IMAGE": (4, "1200x1200"),
                "PORTRAIT_MARKETING_IMAGE": (2, "960x1200")}
STANDIN = {"MARKETING_IMAGE": "271238323325", "SQUARE_MARKETING_IMAGE": "271238380886",
           "PORTRAIT_MARKETING_IMAGE": "271238323247"}  # validate_only ONLY; never created
BARRED = re.compile(r"24/7|24-7|same[- ]day|emergenc|licens|insured|guarantee|warrant|financ|\$\d|% off|discount|"
                    r"years? (of )?experience|\d\.\d ?star|certified|fast response|within \d+ (min|hour)|"
                    r"maint|tune|inspect|ductless|mini split|geotherm|thermostat|propert", re.I)


def checks():
    errs = []
    for k, g in ASSET_GROUPS.items():
        h, lh, d = g["headlines"], g["long_headlines"], g["descriptions"]
        if len(h) != 15 or len({x.lower() for x in h}) != 15: errs.append(f"{k}: need 15 distinct headlines")
        if not any(len(x) <= 15 for x in h): errs.append(f"{k}: no headline <=15")
        errs += [f"{k}: headline {len(x)}>30 {x}" for x in h if len(x) > 30]
        if len(lh) != 5 or any(len(x) > 90 for x in lh): errs.append(f"{k}: long headlines")
        if len(d) != 5 or any(len(x) > 90 for x in d) or not any(len(x) <= 60 for x in d): errs.append(f"{k}: descriptions")
        if len(g["path1"]) > 15 or len(g["path2"]) > 15: errs.append(f"{k}: path")
        for x in h + lh + d:
            if BARRED.search(x): errs.append(f"{k}: barred/off-scope wording '{x}'")
        if len(g["search_themes"]) > 25: errs.append(f"{k}: >25 search themes")
    if any(len(v) > 25 for v in SNIPPET[1]) or len(SNIPPET[1]) < 4: errs.append("snippet")
    if len(CALLOUTS) != 8: errs.append("callouts")
    return errs


def build_ops(c, geo, include_groups, standin_images):
    """Return MutateOperations. Temp ids: budget -1, campaign -2, snippet -3, groups -10.., text assets -100.."""
    ga = c.get_service("GoogleAdsService")
    cpath = c.get_service("CampaignService").campaign_path(CID, -2)
    bpath = c.get_service("CampaignBudgetService").campaign_budget_path(CID, -1)
    apath = lambda i: c.get_service("AssetService").asset_path(CID, i)
    ops = []
    def op(): m = c.get_type("MutateOperation"); ops.append(m); return m
    m = op(); b = m.campaign_budget_operation.create
    b.resource_name = bpath; b.name = f"{CAMPAIGN_NAME} budget"; b.amount_micros = int(BUDGET_STAGED * 1e6)
    b.explicitly_shared = False; b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
    m = op(); x = m.campaign_operation.create
    x.resource_name = cpath; x.name = CAMPAIGN_NAME; x.campaign_budget = bpath
    x.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.PERFORMANCE_MAX
    x.status = c.enums.CampaignStatusEnum.PAUSED
    x.maximize_conversions.target_cpa_micros = 0
    x.contains_eu_political_advertising = c.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    x.geo_target_type_setting.positive_geo_target_type = c.enums.PositiveGeoTargetTypeEnum.PRESENCE
    x.geo_target_type_setting.negative_geo_target_type = c.enums.NegativeGeoTargetTypeEnum.PRESENCE
    x.brand_guidelines_enabled = True
    for t in AUTOMATION_OFF:
        s = c.get_type("Campaign").AssetAutomationSetting()
        s.asset_automation_type = getattr(c.enums.AssetAutomationTypeEnum, t)
        s.asset_automation_status = c.enums.AssetAutomationStatusEnum.OPTED_OUT
        x.asset_automation_settings.append(s)
    for g_rn, neg in geo:
        m = op(); cc = m.campaign_criterion_operation.create
        cc.campaign = cpath; cc.location.geo_target_constant = g_rn; cc.negative = neg
    m = op(); cc = m.campaign_criterion_operation.create; cc.campaign = cpath
    cc.language.language_constant = "languageConstants/1000"
    for day in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"):
        m = op(); cc = m.campaign_criterion_operation.create; cc.campaign = cpath
        cc.ad_schedule.day_of_week = getattr(c.enums.DayOfWeekEnum, day)
        cc.ad_schedule.start_hour = 8; cc.ad_schedule.end_hour = 16
        cc.ad_schedule.start_minute = c.enums.MinuteOfHourEnum.ZERO; cc.ad_schedule.end_minute = c.enums.MinuteOfHourEnum.ZERO
    for grp, words in NEGATIVES.items():
        for w in words:
            m = op(); cc = m.campaign_criterion_operation.create; cc.campaign = cpath; cc.negative = True
            cc.keyword.text = w; cc.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
    m = op(); a = m.asset_operation.create; a.resource_name = apath(-3); a.name = "GM 2026-09-25 PMax pilot services snippet"
    a.structured_snippet_asset.header = SNIPPET[0]; a.structured_snippet_asset.values.extend(SNIPPET[1])
    links = [(BUSINESS_NAME_ASSET, "BUSINESS_NAME"), (LOGO_SQUARE, "LOGO"), (LOGO_LANDSCAPE, "LANDSCAPE_LOGO"),
             (CALL_ASSET, "CALL"), ("-3", "STRUCTURED_SNIPPET")]
    links += [(k, "CALLOUT") for k in CALLOUTS] + [(k, "SITELINK") for k in SITELINKS]
    for aid, ft in links:
        m = op(); ca = m.campaign_asset_operation.create; ca.campaign = cpath
        ca.asset = apath(int(aid)); ca.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
    if not include_groups:
        return ops
    tid = -100
    plan_groups = []
    for gi, (k, g) in enumerate(ASSET_GROUPS.items()):
        agp = c.get_service("AssetGroupService").asset_group_path(CID, -10 - gi)
        texts = [(t, "HEADLINE") for t in g["headlines"]] + [(t, "LONG_HEADLINE") for t in g["long_headlines"]] +                 [(t, "DESCRIPTION") for t in g["descriptions"]]
        links = []
        for t, ft in texts:
            m = op(); a = m.asset_operation.create; a.resource_name = apath(tid); a.text_asset.text = t
            links.append((tid, ft)); tid -= 1
        m = op(); a = m.asset_operation.create; a.resource_name = apath(tid)
        a.call_to_action_asset.call_to_action = c.enums.CallToActionTypeEnum.GET_QUOTE
        links.append((tid, "CALL_TO_ACTION_SELECTION")); tid -= 1
        links += [(int(aid), ft) for ft, aid in standin_images.items()]
        plan_groups.append((agp, g, links))
    for agp, g, links in plan_groups:
        m = op(); ag = m.asset_group_operation.create
        ag.resource_name = agp; ag.campaign = cpath; ag.name = g["name"]; ag.final_urls.append(g["final_url"])
        ag.path1 = g["path1"]; ag.path2 = g["path2"]; ag.status = c.enums.AssetGroupStatusEnum.PAUSED
        for aid, ft in links:
            m = op(); l = m.asset_group_asset_operation.create; l.asset_group = agp; l.asset = apath(aid)
            l.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
    for agp, g, links in plan_groups:
        for th in g["search_themes"]:
            m = op(); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.search_theme.text = th
    return ops


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["plan", "validate", "execute"]); ap.add_argument("--fp")
    a = ap.parse_args()
    c = client(); identity_gate(c, verbose=False)
    geo = sorted((r.campaign_criterion.location.geo_target_constant, r.campaign_criterion.negative) for r in q(c,
          f"SELECT campaign_criterion.location.geo_target_constant, campaign_criterion.negative FROM campaign_criterion WHERE campaign.id = {GEO_SOURCE} AND campaign_criterion.type = 'LOCATION'"))
    existing = [r.campaign.id for r in q(c, f"SELECT campaign.id FROM campaign WHERE campaign.name = '{CAMPAIGN_NAME}' AND campaign.status != 'REMOVED'")]
    errs = checks() + ([f"campaign already exists {existing}"] if existing and a.mode != "validate" else [])
    enabled_total = sum(r.campaign_budget.amount_micros for r in q(c, "SELECT campaign_budget.amount_micros FROM campaign WHERE campaign.status = 'ENABLED'")) / 1e6
    if enabled_total + BUDGET_STAGED > 325.0: errs.append(f"staged budget would breach cap: {enabled_total}+{BUDGET_STAGED}")
    plan = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342", "plan_name": PLAN_NAME,
            "built_local": datetime.datetime.now(TZ).date().isoformat(), "campaign_name": CAMPAIGN_NAME,
            "status_on_create": "PAUSED", "budget": {"amount_staged": BUDGET_STAGED, "shared": False,
            "why_20": "unallocated headroom ($325 cap - $305 enabled); an accidental enable cannot breach the cap",
            "launch_plan": "AMB-0925-PMAX-LAUNCH: pause 24279798229 Heating Maintenance ($45 donor), raise this budget to $45, enable"},
            "bidding": "MAXIMIZE_CONVERSIONS, no target CPA", "goals": {"biddable": ["CONTACT/WEBSITE (WC Lead)", "CONTACT/CALL_FROM_ADS (WC Calls)"],
            "not_biddable_for_this_campaign": ["PHONE_CALL_LEAD/CALL_FROM_ADS (Calls from ads) - the same call-asset call is also uploaded as WC Lead"]},
            "geo": {"source_campaign": GEO_SOURCE, "criteria": len(geo), "type": "PRESENCE"}, "schedule": "Mon-Fri 08:00-16:00",
            "negatives": NEGATIVES, "asset_automation_opted_out": AUTOMATION_OFF, "brand_guidelines_enabled": True,
            "campaign_assets": {"business_name": BUSINESS_NAME_ASSET, "logo": LOGO_SQUARE, "landscape_logo": LOGO_LANDSCAPE,
                                "call": CALL_ASSET, "callouts": CALLOUTS, "sitelinks": SITELINKS, "snippet": SNIPPET},
            "sitelink_shortfall": "5 of 6: only five ready, in-scope replacement/installation destinations exist",
            "asset_groups_payload": ASSET_GROUPS, "images_required_per_group": IMAGE_TARGET,
            "images_status": "PENDING REVIEW - no verified service-specific imagery available (stock previews blocked, offer-site images carry unverified 'Ambient technician' captions)",
            "videos": "none supplied; automatic video generation opted out",
            "audience_signal": {"user_list": AUDIENCE_SIGNAL_LIST, "name": "All Converters"}, "errors": errs}
    plan["operation_count_shell"] = len(build_ops(c, geo, False, {}))
    fp = approval_code(plan)
    if a.mode == "plan":
        plan["fingerprint"] = fp
        (PLANS / f"{PLAN_NAME}.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print(f"PLAN {PLAN_NAME} {fp} shell ops={plan['operation_count_shell']} geo={len(geo)} errors={errs}")
        return
    rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False
    if a.mode == "validate":
        rq.mutate_operations.extend(build_ops(c, geo, True, STANDIN)); rq.validate_only = True
        try:
            c.get_service("GoogleAdsService").mutate(request=rq); print(f"VALIDATE full build ({len(rq.mutate_operations)} ops): PASS")
        except Exception as ex:
            msgs = re.findall(r'message: "([^"]+)"', str(ex)); idx = re.findall(r"index: (\d+)", str(ex))
            print("VALIDATE FAIL", msgs[:6], idx[:12])
        return
    if a.fp != fp or errs: sys.exit(f"ABORT fp {fp} != {a.fp} or errors {errs}")
    rq.mutate_operations.extend(build_ops(c, geo, False, {}))
    rec = {"plan": PLAN_NAME, "fingerprint": fp, "started_local": datetime.datetime.now(TZ).isoformat()}
    out = RECEIPTS / f"{PLAN_NAME}-EXECUTED.json"
    try:
        resp = c.get_service("GoogleAdsService").mutate(request=rq)
    except Exception as ex:
        rec["error"] = str(ex)[:2000]; out.write_text(json.dumps(rec, indent=1), encoding="utf-8"); sys.exit("STOP " + str(ex)[:800])
    names = []
    for r in resp.mutate_operation_responses:
        for f in ("campaign_budget_result", "campaign_result", "campaign_criterion_result", "asset_result", "campaign_asset_result"):
            if r._pb.HasField(f): names.append(getattr(r, f).resource_name)
    camp = [n for n in names if "/campaigns/" in n][0]; cid = camp.split("/")[-1]
    rec["created"] = names; rec["campaign_id"] = cid
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(f"CREATED shell campaign {cid}, {len(names)} resources")
    # goals: stop native call-asset calls counting twice in this campaign's bidding
    goals = {(E(r.campaign_conversion_goal.category), E(r.campaign_conversion_goal.origin)): r.campaign_conversion_goal.biddable
             for r in q(c, f"SELECT campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id = {cid}")}
    gops = []
    if goals.get(("PHONE_CALL_LEAD", "CALL_FROM_ADS")):
        o = c.get_type("CampaignConversionGoalOperation")
        o.update.resource_name = c.get_service("CampaignConversionGoalService").campaign_conversion_goal_path(CID, cid, "PHONE_CALL_LEAD", "CALL_FROM_ADS")
        o.update.biddable = False; o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["biddable"])); gops.append(o)
    if gops:
        c.get_service("CampaignConversionGoalService").mutate_campaign_conversion_goals(customer_id=CID, operations=gops)
    rec["goals_before"] = {f"{k[0]}/{k[1]}": v for k, v in goals.items()}
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat()
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("goals updated:", len(gops), "| receipt", out.name)


if __name__ == "__main__":
    main()
