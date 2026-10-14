#!/usr/bin/env python3
"""Ambient | 2026-10-02 | Two distinct Performance Max campaigns (owner instruction 2026-10-02). BUILD PAUSED. validate | execute.

Service choice (owner, 2026-10-02): the highest per-job revenue heating services that Ambient offers, by published 2026
installed-price ranges - geothermal heat pump ~$15k-45k, air-source heat pump install/replace ~$4k-14k, boiler replacement
~$3.5k-8.5k, gas furnace replacement ~$3.5k-9k; repairs ~$125-500 and tune-ups ~$70-200 are excluded. Margin and close rate
are unknown for Ambient.

  AMB-1002-PMAX-A-1  reuse paused shell 24295088845 -> "PMax | Furnace & Boiler Replacement": rename, budget $20 -> $32.89,
                     tablet exclusion, new PAUSED asset group Boiler Replacement (/boiler-replacement/). Existing Heating &
                     Furnace Replacement group kept; existing Heat Pump Replacement group stays PAUSED (portfolio moves to B).
  AMB-1002-PMAX-B-1  new PAUSED campaign "PMax | Heat Pump & Geothermal": own $32.89 budget, Max Conversions, 75 PRESENCE
                     locations, Mon-Fri 08-16, English, tablet excluded, automation opt-outs (incl. Final URL expansion and
                     text customization), brand guidelines, 5 own-brand EXACT negatives, the two existing heating shared
                     negative lists attached (contents untouched), PAUSED asset groups Heat Pump Replacement + Heat Pump
                     Installation. Geothermal asset group is a held payload (page countdown + no approved geothermal images).
Everything is created/left PAUSED. Enabling needs separate approvals after readback.
"""
from __future__ import annotations
import sys, json, re, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402

O = "https://offer.ambientcoolingandheating.com"
SHELL, SHELL_BUDGET = "24295088845", "15897049193"
STEADY = 32.89
A_NAME = "PMax | Furnace & Boiler Replacement | Central MD | 2026-10 | HELD"
B_NAME = "PMax | Heat Pump & Geothermal | Central MD | 2026-10 | HELD"
AUDIENCE = "customers/2401959466/audiences/360614515"   # Ambient PMax signal - All Converters
CTA = "218982354502"            # existing GET_QUOTE call-to-action asset
COMMON_D5 = "424734013138"      # "Call Mon-Fri, 8 a.m. to 4 p.m., or request your free quote online."
BRAND = {"80516971145": "BUSINESS_NAME", "218982449635": "LOGO", "218984456832": "LANDSCAPE_LOGO"}
B_CAMPAIGN_ASSETS = {**BRAND, "424764337810": "CALL", "424803398337": "STRUCTURED_SNIPPET",
                     "424666395915": "SITELINK", "424481139482": "SITELINK", "410638278156": "SITELINK", "410638276380": "SITELINK",
                     "422577771364": "CALLOUT", "407418646876": "CALLOUT", "422577760603": "CALLOUT", "349923938310": "CALLOUT",
                     "407418627430": "CALLOUT", "407418646882": "CALLOUT", "422477374526": "CALLOUT", "89063098370": "CALLOUT"}
SHARED_NEG_LISTS = ["12249470554", "12252013691"]
OWN_BRAND_EXACT = ["ambient cooling and heating", "ambient heating and cooling", "ambient cooling", "ambient heating", "ambient hvac"]
HP_GROUP_SOURCE = "6751752096"   # assets copied (linked) from the shell's Heat Pump Replacement group

BOILER = dict(name="Boiler Replacement", final_url=f"{O}/boiler-replacement/", path1="Boiler", path2="Replacement",
              headlines=["Boiler Replacement", "Replace Your Boiler", "New Boiler Quote", "Gas Boiler Replacement", "Severn Boiler Replacement",
                         "Columbia Boiler Replacement", "Severna Park Boilers", "Central Maryland Boilers", "Boiler Upgrade Options", "New Boiler",
                         "Plan Your Boiler Upgrade", ("id", "424734001078"), ("id", "409521516376"), ("id", "422477367425"), ("id", "423809914800")],
              long_headlines=["Boiler replacement for homes in Severn, Severna Park and Columbia, MD",
                              "Request a free boiler replacement quote from Ambient Cooling & Heating",
                              "Old boiler failing? Plan a replacement with trained technicians",
                              "Boiler replacement across Central Maryland, planned around your home",
                              "Compare boiler replacement options clearly before you decide"],
              descriptions=["Request a free boiler replacement quote.", "Trained technicians assess your boiler and explain replacement options clearly.",
                            "Boiler replacement for Severn, Severna Park and Columbia homes.",
                            "Plan a new boiler with Ambient Cooling & Heating in Central Maryland.", ("id", COMMON_D5)],
              images={"424734010279": "SQUARE_MARKETING_IMAGE", "424734010297": "PORTRAIT_MARKETING_IMAGE", "424632150521": "MARKETING_IMAGE"},
              search_themes=["boiler replacement", "boiler replacement near me", "replace boiler", "new boiler installation", "gas boiler replacement",
                             "boiler replacement cost", "new boiler cost", "residential boiler replacement", "boiler installer near me", "new boiler"])
HP_INSTALL = dict(name="Heat Pump Installation", final_url=f"{O}/heat-pump-installation/", path1="Heat-Pump", path2="Installation",
                  headlines=[("id", "310563102573"), "Install a Heat Pump", ("id", "424734001132"), "Heat Pump Installers", "Free Installation Quote",
                             "Severn Heat Pump Install", ("id", "424666402908"), ("id", "424632150596"), ("id", "424734004471"), ("id", "424734013285"),
                             ("id", "424734010534"), ("id", "409521516376"), ("id", "422477367425"), "Heat Pump Options Explained", "New Heat Pumps"],
                  long_headlines=["Heat pump installation for homes in Severn, Severna Park and Columbia, MD",
                                  "Request a free heat pump installation quote from Ambient Cooling & Heating",
                                  "Considering a heat pump? Plan the installation with trained technicians",
                                  ("id", "424734013318"), "Compare heat pump installation options clearly before you decide"],
                  descriptions=["Request a free heat pump installation quote.", "Trained technicians assess your home and explain heat pump options clearly.",
                                "Heat pump installation for Severn, Severna Park and Columbia homes.", ("id", "424734004492"), ("id", COMMON_D5)],
                  images="COPY_FROM_HP_SOURCE",
                  search_themes=["heat pump installation", "heat pump installation near me", "install heat pump", "new heat pump installation",
                                 "heat pump installer", "heat pump installation cost", "air source heat pump installation", "heat pump for house",
                                 "convert to heat pump", "electric heat pump installation"])
GEO_HELD = dict(name="Geothermal Heat Pump", final_url=f"{O}/geothermal-heat-pump/", path1="Geothermal", path2="Heat-Pump",
                status="HELD - not in any operation", blockers=["page shows a zeroed 'Offer Ends in' countdown (unverified time-limited offer)",
                "no approved geothermal images in the account (page / Drive images not yet uploaded)", "geothermal Search ads still under review"],
                headlines=["Geothermal Heat Pumps", "Geothermal Heat Pump Service", "Geothermal Heating & Cooling", "New Geothermal System Quote",
                           "Plan A Geothermal Install", "Geothermal Replacement Help", "Free Geothermal Quote", "Ground-Loop System Review"],
                search_themes=["geothermal heat pump installation", "geothermal heating and cooling", "geothermal system cost", "geothermal heat pump replacement",
                               "ground source heat pump", "geothermal hvac", "geothermal heat pump cost"])
BARRED = re.compile(r"24/7|24-7|24 hour|same[- ]day|emergenc|licens|insured|guarantee|warrant|financ|\$\d|% off|discount|years? (of )?experience|"
                    r"\d\.\d ?star|certified|fast response|within \d+ (min|hour)|repair|maint|tune|inspect|ductless|mini split|\bbest\b|cheap|rebate", re.I)


def text_checks(g):
    errs = []
    lit = lambda xs: [x for x in xs if isinstance(x, str)]
    h, lh, d = g["headlines"], g["long_headlines"], g["descriptions"]
    if len(h) != 15: errs.append(f"{g['name']}: {len(h)} headlines")
    errs += [f"{g['name']}: headline >30 {x}" for x in lit(h) if len(x) > 30]
    if len(lh) != 5: errs.append(f"{g['name']}: long headlines {len(lh)}")
    errs += [f"{g['name']}: long headline >90 {x}" for x in lit(lh) if len(x) > 90]
    if len(d) != 5: errs.append(f"{g['name']}: descriptions {len(d)}")
    errs += [f"{g['name']}: description >90 {x}" for x in lit(d) if len(x) > 90]
    if not any(isinstance(x, str) and len(x) <= 60 for x in d): errs.append(f"{g['name']}: no description <=60")
    if not any(isinstance(x, str) and len(x) <= 15 for x in h): errs.append(f"{g['name']}: no headline <=15")
    if len(g["path1"]) > 15 or len(g["path2"]) > 15: errs.append(f"{g['name']}: path >15")
    errs += [f"{g['name']}: barred/off-scope '{x}'" for x in lit(h) + lit(lh) + lit(d) if BARRED.search(x)]
    if len(g["search_themes"]) > 25: errs.append(f"{g['name']}: >25 themes")
    return errs


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "validate"
    c = client()
    identity_gate(c, verbose=False)
    errs = text_checks(BOILER) + text_checks(HP_INSTALL)
    # ---------------- live reads ----------------
    sh = q(c, f"SELECT campaign.status, campaign.name, campaign_budget.amount_micros, campaign_budget.id FROM campaign WHERE campaign.id = {SHELL}")[0]
    if E(sh.campaign.status) != "PAUSED" or str(sh.campaign_budget.id) != SHELL_BUDGET: errs.append("shell not PAUSED or budget id changed")
    groups = {str(r.asset_group.id): (r.asset_group.name, E(r.asset_group.status)) for r in q(c,
              f"SELECT asset_group.id, asset_group.name, asset_group.status FROM asset_group WHERE campaign.id = {SHELL} AND asset_group.status != 'REMOVED'")}
    if any(n == BOILER["name"] for n, _ in groups.values()): errs.append("Boiler Replacement group already exists")
    if any(s != "PAUSED" for _, s in groups.values()): errs.append(f"a shell asset group is not PAUSED: {groups}")
    hp_assets = [(str(r.asset.id), E(r.asset_group_asset.field_type)) for r in q(c, f"""SELECT asset.id, asset_group_asset.field_type FROM asset_group_asset
                 WHERE asset_group.id = {HP_GROUP_SOURCE} AND asset_group_asset.status != 'REMOVED'""")]
    hp_images = {a: ft for a, ft in hp_assets if ft.endswith("IMAGE")}
    geo = sorted(r.campaign_criterion.location.geo_target_constant for r in q(c, f"""SELECT campaign_criterion.location.geo_target_constant FROM campaign_criterion
                 WHERE campaign.id = {SHELL} AND campaign_criterion.type = 'LOCATION' AND campaign_criterion.negative = FALSE"""))
    if len(geo) != 75: errs.append(f"shell has {len(geo)} locations, expected 75")
    exists_b = [r.campaign.id for r in q(c, f"SELECT campaign.id FROM campaign WHERE campaign.name = '{B_NAME}' AND campaign.status != 'REMOVED'")]
    if exists_b: errs.append(f"campaign B already exists {exists_b}")
    enabled_daily = sum(r.campaign_budget.amount_micros for r in q(c, "SELECT campaign_budget.amount_micros FROM campaign WHERE campaign.status = 'ENABLED'")) / 1e6
    # ---------------- operations (GoogleAdsService.Mutate, temp ids) ----------------
    svc = lambda n: c.get_service(n)
    apath = lambda i: svc("AssetService").asset_path(CID, i)
    ops_a, ops_b, manifest = [], [], {"A": [], "B": []}

    def op(lst):
        m = c.get_type("MutateOperation"); lst.append(m); return m

    # ---- A: shell updates ----
    m = op(ops_a); x = m.campaign_operation.update; x.resource_name = svc("CampaignService").campaign_path(CID, SHELL); x.name = A_NAME
    m.campaign_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["name"])); manifest["A"].append(f"rename campaign {SHELL} -> {A_NAME}")
    m = op(ops_a); x = m.campaign_budget_operation.update; x.resource_name = svc("CampaignBudgetService").campaign_budget_path(CID, SHELL_BUDGET)
    x.amount_micros = int(STEADY * 100) * 10000; m.campaign_budget_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["amount_micros"]))
    manifest["A"].append(f"budget {SHELL_BUDGET} $20.00 -> ${STEADY} (campaign stays PAUSED)")
    m = op(ops_a); x = m.campaign_criterion_operation.update; x.resource_name = svc("CampaignCriterionService").campaign_criterion_path(CID, SHELL, "30002")
    x.bid_modifier = 0.0; m.campaign_criterion_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["bid_modifier"]))
    manifest["A"].append("tablet device criterion 30002 bid_modifier = 0 (exclude tablets)")

    def build_group(lst, campaign_path, g, tmp_group, tmp_start, image_map):
        tid, links = tmp_start, []
        for field, items in (("HEADLINE", g["headlines"]), ("LONG_HEADLINE", g["long_headlines"]), ("DESCRIPTION", g["descriptions"])):
            for it in items:
                if isinstance(it, tuple):
                    links.append((int(it[1]), field))
                else:
                    m = op(lst); a = m.asset_operation.create; a.resource_name = apath(tid); a.text_asset.text = it
                    links.append((tid, field)); tid -= 1
        links.append((int(CTA), "CALL_TO_ACTION_SELECTION"))
        links += [(int(k), v) for k, v in image_map.items()]
        agp = svc("AssetGroupService").asset_group_path(CID, tmp_group)
        m = op(lst); ag = m.asset_group_operation.create
        ag.resource_name = agp; ag.campaign = campaign_path; ag.name = g["name"]; ag.final_urls.append(g["final_url"])
        ag.path1, ag.path2 = g["path1"], g["path2"]; ag.status = c.enums.AssetGroupStatusEnum.PAUSED
        for aid, ft in links:
            m = op(lst); l = m.asset_group_asset_operation.create; l.asset_group = agp; l.asset = apath(aid); l.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
        for th in g["search_themes"]:
            m = op(lst); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.search_theme.text = th
        m = op(lst); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.audience.audience = AUDIENCE
        return tid, len(links)

    _, n = build_group(ops_a, svc("CampaignService").campaign_path(CID, SHELL), BOILER, -11, -100, BOILER["images"])
    manifest["A"].append(f"create PAUSED asset group 'Boiler Replacement' -> {BOILER['final_url']} ({n} asset links, {len(BOILER['search_themes'])} themes + audience)")
    # ---- B: new campaign ----
    bpath = svc("CampaignBudgetService").campaign_budget_path(CID, -1)
    cpath = svc("CampaignService").campaign_path(CID, -2)
    m = op(ops_b); b = m.campaign_budget_operation.create; b.resource_name = bpath; b.name = f"{B_NAME} budget"
    b.amount_micros = int(STEADY * 100) * 10000; b.explicitly_shared = False; b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
    m = op(ops_b); x = m.campaign_operation.create
    x.resource_name = cpath; x.name = B_NAME; x.campaign_budget = bpath; x.status = c.enums.CampaignStatusEnum.PAUSED
    x.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.PERFORMANCE_MAX; x.maximize_conversions.target_cpa_micros = 0
    x.contains_eu_political_advertising = c.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    x.geo_target_type_setting.positive_geo_target_type = c.enums.PositiveGeoTargetTypeEnum.PRESENCE
    x.geo_target_type_setting.negative_geo_target_type = c.enums.NegativeGeoTargetTypeEnum.PRESENCE
    x.brand_guidelines_enabled = True
    for t in ("TEXT_ASSET_AUTOMATION", "FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION", "GENERATE_IMAGE_EXTRACTION", "GENERATE_IMAGE_ENHANCEMENT",
              "GENERATE_DESIGN_VERSIONS_FOR_IMAGES", "GENERATE_ENHANCED_YOUTUBE_VIDEOS"):
        s = c.get_type("Campaign").AssetAutomationSetting(); s.asset_automation_type = getattr(c.enums.AssetAutomationTypeEnum, t)
        s.asset_automation_status = c.enums.AssetAutomationStatusEnum.OPTED_OUT; x.asset_automation_settings.append(s)
    for g_rn in geo:
        m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath; cc.location.geo_target_constant = g_rn
    m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath; cc.language.language_constant = "languageConstants/1000"
    for day in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"):
        m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath
        cc.ad_schedule.day_of_week = getattr(c.enums.DayOfWeekEnum, day); cc.ad_schedule.start_hour = 8; cc.ad_schedule.end_hour = 16
        cc.ad_schedule.start_minute = c.enums.MinuteOfHourEnum.ZERO; cc.ad_schedule.end_minute = c.enums.MinuteOfHourEnum.ZERO
    m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath; cc.device.type_ = c.enums.DeviceEnum.TABLET; cc.bid_modifier = 0.0
    for w in OWN_BRAND_EXACT:
        m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath; cc.negative = True
        cc.keyword.text = w; cc.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT
    for sid in SHARED_NEG_LISTS:
        m = op(ops_b); s_ = m.campaign_shared_set_operation.create; s_.campaign = cpath; s_.shared_set = svc("SharedSetService").shared_set_path(CID, sid)
    for aid, ft in B_CAMPAIGN_ASSETS.items():
        m = op(ops_b); ca = m.campaign_asset_operation.create; ca.campaign = cpath; ca.asset = apath(int(aid)); ca.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
    # B1: Heat Pump Replacement = links to the shell group's existing assets (no new text), new final URL group in B
    agp = svc("AssetGroupService").asset_group_path(CID, -21)
    m = op(ops_b); ag = m.asset_group_operation.create; ag.resource_name = agp; ag.campaign = cpath; ag.name = "Heat Pump Replacement"
    ag.final_urls.append(f"{O}/heat-pump-replacement/"); ag.path1, ag.path2 = "Heat-Pump", "Replacement"; ag.status = c.enums.AssetGroupStatusEnum.PAUSED
    for aid, ft in hp_assets:
        m = op(ops_b); l = m.asset_group_asset_operation.create; l.asset_group = agp; l.asset = apath(int(aid)); l.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
    hp_themes = ["heat pump replacement", "replace heat pump", "heat pump replacement near me", "heat pump replacement cost", "heat pump system replacement",
                 "new heat pump", "heat pump replacement contractor", "upgrade heat pump"]
    for th in hp_themes:
        m = op(ops_b); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.search_theme.text = th
    m = op(ops_b); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.audience.audience = AUDIENCE
    _, n2 = build_group(ops_b, cpath, HP_INSTALL, -22, -300, hp_images)
    manifest["B"] = [f"create budget ${STEADY} (non-shared)", f"create PAUSED PMax campaign '{B_NAME}' (Max Conversions, presence, brand guidelines, 6 automation opt-outs incl. Final URL expansion + text customization)",
                     f"{len(geo)} locations, English, Mon-Fri 08-16 (5 rows), tablet bid_modifier 0", f"{len(OWN_BRAND_EXACT)} own-brand EXACT negatives",
                     f"attach shared negative lists {SHARED_NEG_LISTS} (contents unchanged)", f"{len(B_CAMPAIGN_ASSETS)} campaign asset links (brand, call 415-9517, snippet, 4 offer-page sitelinks, 8 callouts)",
                     f"PAUSED asset group 'Heat Pump Replacement' -> /heat-pump-replacement/ ({len(hp_assets)} existing assets linked, {len(hp_themes)} themes + audience)",
                     f"PAUSED asset group 'Heat Pump Installation' -> /heat-pump-installation/ ({n2} asset links, {len(HP_INSTALL['search_themes'])} themes + audience)",
                     "AFTER CREATE (same executor, real campaign id): campaign_conversion_goal PHONE_CALL_LEAD/CALL_FROM_ADS biddable=false, mirroring shell A"]
    if enabled_daily + 0 > 328.94: errs.append(f"enabled daily {enabled_daily} already above cap")
    plan_a = dict(plan_name="AMB-1002-PMAX-A-1", customer_id=CID, exact_account_name=EXACT_NAME, never_write_to_mcc="3373711342", approval_class="create-paused",
                  work_order="work-orders/work-order-pmax-furnace-boiler-replacement-2026-10-02.yaml", campaign=SHELL, campaign_name_after=A_NAME,
                  portfolio=["Furnace & heating replacement -> /hvac-replacement/ (existing group 6751612859)", "Boiler replacement -> /boiler-replacement/ (new)"],
                  heat_pump_group_in_A="6751752096 stays PAUSED permanently - heat pump moves to campaign B", boiler_payload=BOILER, actions=manifest["A"],
                  stays_paused=True, operation_count=len(ops_a))
    plan_b = dict(plan_name="AMB-1002-PMAX-B-1", customer_id=CID, exact_account_name=EXACT_NAME, never_write_to_mcc="3373711342", approval_class="create-paused",
                  work_order="work-orders/work-order-pmax-heat-pump-geothermal-2026-10-02.yaml", campaign_name=B_NAME,
                  portfolio=["Heat pump replacement -> /heat-pump-replacement/", "Heat pump installation -> /heat-pump-installation/", "Geothermal -> HELD payload"],
                  hp_install_payload=HP_INSTALL, hp_replacement_assets_linked=hp_assets, geothermal_held=GEO_HELD, actions=manifest["B"],
                  own_brand_exact_negatives=OWN_BRAND_EXACT, shared_lists_attached=SHARED_NEG_LISTS, stays_paused=True, operation_count=len(ops_b))
    for p in (plan_a, plan_b):
        p["fingerprint"] = approval_code({k: v for k, v in p.items() if k != "fingerprint"})
    if errs:
        sys.exit("HARD STOP:\n  " + "\n  ".join(errs))

    def send(ops, validate):
        rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.validate_only = validate
        rq.mutate_operations.extend(ops)
        return svc("GoogleAdsService").mutate(request=rq)

    if mode == "validate":
        res = {}
        for name, ops in (("AMB-1002-PMAX-A-1", ops_a), ("AMB-1002-PMAX-B-1", ops_b)):
            try:
                send(ops, True); res[name] = f"VALIDATED {len(ops)}"
            except Exception as ex:
                msgs = re.findall(r'message: "([^"]+)"', str(ex)); idx = re.findall(r"index: (\d+)", str(ex))
                res[name] = f"FAILED {msgs[:4]} at ops {idx[:6]}"
        print("preflight:", res)
        if any(v.startswith("FAILED") for v in res.values()):
            sys.exit("HARD STOP: validate_only failed - no plan written")
        for p, key in ((plan_a, "AMB-1002-PMAX-A-1"), (plan_b, "AMB-1002-PMAX-B-1")):
            p["preflight"] = res[key]
            p["fingerprint"] = approval_code({k: v for k, v in p.items() if k != "fingerprint"})
            (PLANS / f"{key}.json").write_text(json.dumps(p, indent=1), encoding="utf-8")
            print(f"PLAN {key}: {p['fingerprint']} / {p['operation_count']} ops")
            for a in p["actions"]:
                print("   -", a)
        return
    # ---------------- execute <PLAN> <FINGERPRINT> <N> ----------------
    if mode != "execute" or len(sys.argv) != 5:
        sys.exit("usage: validate | execute <AMB-1002-PMAX-A-1|AMB-1002-PMAX-B-1> <FINGERPRINT> <N>")
    name, fp_ok, n_ok = sys.argv[2], sys.argv[3].upper(), int(sys.argv[4])
    live = {"AMB-1002-PMAX-A-1": (plan_a, ops_a), "AMB-1002-PMAX-B-1": (plan_b, ops_b)}[name]
    saved = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8")); fp = saved.pop("fingerprint")
    live[0]["preflight"] = saved.get("preflight")
    fp_live = approval_code({k: v for k, v in live[0].items() if k != "fingerprint"})
    if not (fp == approval_code(saved) == fp_live == fp_ok and n_ok == len(live[1])):
        sys.exit(f"ABORT {name}: fingerprint mismatch (file {fp}, rebuilt {fp_live}, approved {fp_ok}) - account or payload changed; rebuild")
    out = RECEIPTS / f"{name}-EXECUTED.json"
    if out.exists():
        sys.exit("ABORT: receipt exists")
    rec = dict(plan=name, fingerprint=fp, started_local=datetime.datetime.now(TZ).isoformat())
    try:
        resp = send(live[1], False)
    except Exception as ex:
        rec["status"] = "FAILED_NOTHING_WRITTEN"; rec["error"] = re.findall(r'message: "([^"]+)"', str(ex))[:4]
        out.write_text(json.dumps(rec, indent=1), encoding="utf-8"); sys.exit(f"FAILED (atomic, nothing written): {rec['error']}")
    names = []
    for r in resp.mutate_operation_responses:
        for f in ("campaign_result", "campaign_budget_result", "asset_group_result", "campaign_criterion_result"):
            if r._pb.HasField(f):
                names.append(getattr(r, f).resource_name)
    rec["created_or_updated"] = names
    chk = []
    if name == "AMB-1002-PMAX-A-1":
        r = q(c, f"SELECT campaign.name, campaign.status, campaign_budget.amount_micros FROM campaign WHERE campaign.id = {SHELL}")[0]
        chk += [("A renamed", r.campaign.name == A_NAME), ("A still PAUSED", E(r.campaign.status) == "PAUSED"), ("A budget $32.89", r.campaign_budget.amount_micros == 32_890_000)]
        d = q(c, f"SELECT campaign_criterion.bid_modifier FROM campaign_criterion WHERE campaign.id = {SHELL} AND campaign_criterion.criterion_id = 30002")[0]
        chk.append(("A tablet excluded", "bid_modifier" in d.campaign_criterion and d.campaign_criterion.bid_modifier == 0.0))
        g = q(c, f"SELECT asset_group.id, asset_group.status, asset_group.final_urls FROM asset_group WHERE campaign.id = {SHELL} AND asset_group.name = 'Boiler Replacement'")
        chk.append(("A Boiler Replacement group PAUSED on /boiler-replacement/", len(g) == 1 and E(g[0].asset_group.status) == "PAUSED" and list(g[0].asset_group.final_urls) == [BOILER["final_url"]]))
    else:
        cid = next(n.split("/")[-1] for n in names if "/campaigns/" in n)
        rec["campaign_id"] = cid
        r = q(c, f"""SELECT campaign.status, campaign.advertising_channel_type, campaign_budget.amount_micros, campaign_budget.explicitly_shared,
                campaign.asset_automation_settings FROM campaign WHERE campaign.id = {cid}""")[0]
        chk += [("B PAUSED PMax", E(r.campaign.status) == "PAUSED" and E(r.campaign.advertising_channel_type) == "PERFORMANCE_MAX"),
                ("B budget $32.89 non-shared", r.campaign_budget.amount_micros == 32_890_000 and not r.campaign_budget.explicitly_shared),
                ("B 6 automation opt-outs", sum(1 for s in r.campaign.asset_automation_settings if E(s.asset_automation_status) == "OPTED_OUT") == 6)]
        cc = q(c, f"SELECT campaign_criterion.type, campaign_criterion.negative, campaign_criterion.device.type, campaign_criterion.bid_modifier FROM campaign_criterion WHERE campaign.id = {cid}")
        chk += [("B 75 locations", sum(1 for x in cc if E(x.campaign_criterion.type) == "LOCATION") == 75),
                ("B 5 schedule rows", sum(1 for x in cc if E(x.campaign_criterion.type) == "AD_SCHEDULE") == 5),
                ("B tablet excluded", any(E(x.campaign_criterion.type) == "DEVICE" and E(x.campaign_criterion.device.type) == "TABLET" and "bid_modifier" in x.campaign_criterion
                                          and x.campaign_criterion.bid_modifier == 0.0 for x in cc)),
                ("B 5 own-brand EXACT negatives", sum(1 for x in cc if E(x.campaign_criterion.type) == "KEYWORD" and x.campaign_criterion.negative) == 5)]
        chk.append(("B 2 shared lists attached", len(q(c, f"SELECT shared_set.id FROM campaign_shared_set WHERE campaign.id = {cid} AND campaign_shared_set.status = 'ENABLED'")) == 2))
        gs = q(c, f"SELECT asset_group.name, asset_group.status, asset_group.final_urls FROM asset_group WHERE campaign.id = {cid}")
        chk.append(("B 2 PAUSED asset groups on HP pages", sorted((x.asset_group.name, E(x.asset_group.status), tuple(x.asset_group.final_urls)) for x in gs) ==
                    sorted([("Heat Pump Installation", "PAUSED", (HP_INSTALL["final_url"],)), ("Heat Pump Replacement", "PAUSED", (f"{O}/heat-pump-replacement/",))])))
        try:   # mirror shell A: native call-asset calls not biddable (avoids the call double count)
            g = c.get_type("CampaignConversionGoalOperation")
            g.update.resource_name = f"customers/{CID}/campaignConversionGoals/{cid}~PHONE_CALL_LEAD~CALL_FROM_ADS"; g.update.biddable = False
            g.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["biddable"]))
            c.get_service("CampaignConversionGoalService").mutate_campaign_conversion_goals(customer_id=CID, operations=[g])
            gb = {(E(x.campaign_conversion_goal.category), E(x.campaign_conversion_goal.origin)): x.campaign_conversion_goal.biddable for x in q(c,
                  f"SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id = {cid}")}
            chk.append(("B call-from-ads goal not biddable", gb.get(("PHONE_CALL_LEAD", "CALL_FROM_ADS")) is False))
        except Exception as ex:
            chk.append((f"B goal update FAILED {str(ex)[:120]}", False))
    rec["readback"] = [{"check": k, "pass": v} for k, v in chk]
    rec["status"] = "EXECUTED" if all(v for _, v in chk) else "EXECUTED_READBACK_FAIL"
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat()
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    for k, v in chk:
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(f"{name} {fp}: {rec['status']}")


if __name__ == "__main__":
    main()
