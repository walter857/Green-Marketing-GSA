#!/usr/bin/env python3
"""Ambient | 2026-10-02 | Two Performance Max campaigns - build PAUSED, read back, enable (staged authorization 2026-10-02).
Supersedes the never-executed AMB-1002-PMAX-A-1 / B-1 drafts (HELD names, $32.89, PHRASE/BROAD shared list, no geothermal group).

Service choice (owner 2026-10-02): highest per-job revenue heating services Ambient offers - furnace & boiler replacement (A),
heat pump installation/replacement + geothermal consultation/replacement (B). Repairs and tune-ups are excluded.

  plan   live reads, local checks, validate_only of every stage, fingerprints -> plans/AMB-1002-PMAX-{A,B}-2.json
  run    A + B create/update PAUSED -> read back (tablet, opt-outs, URLs, budgets, lists, goals) -> enable -> read back
"""
from __future__ import annotations
import sys, json, re, datetime, hashlib, math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, EXACT_NAME, TZ, PLANS, RECEIPTS, CLIENT_DIR  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402

O = "https://offer.ambientcoolingandheating.com"
SHELL, SHELL_BUDGET = "24295088845", "15897049193"
A_GROUP_FURNACE, A_GROUP_HP_OLD = "6751612859", "6751752096"     # furnace group launches; old HP group stays PAUSED (portfolio moved to B)
MONTHLY = 1000.00
A_NAME = "PMax | Furnace & Boiler Replacement | Central MD | 2026-10"
B_NAME = "PMax | Heat Pump & Geothermal | Central MD | 2026-10"
AUDIENCE = "customers/2401959466/audiences/360614515"   # Ambient PMax signal - All Converters
CTA = "218982354502"
COMMON_D5 = "424734013138"      # "Call Mon-Fri, 8 a.m. to 4 p.m., or request your free quote online."
BRAND = {"80516971145": "BUSINESS_NAME", "218982449635": "LOGO", "218984456832": "LANDSCAPE_LOGO"}
GEO_SITELINK = "426109948970"   # created by AMB-1002-SEARCH-LAUNCH-1
B_CAMPAIGN_ASSETS = {**BRAND, "424764337810": "CALL", "424803398337": "STRUCTURED_SNIPPET",
                     "424666395915": "SITELINK", "424481139482": "SITELINK", GEO_SITELINK: "SITELINK", "410638278156": "SITELINK", "410638276380": "SITELINK",
                     "422577771364": "CALLOUT", "407418646876": "CALLOUT", "422577760603": "CALLOUT", "349923938310": "CALLOUT",
                     "407418627430": "CALLOUT", "407418646882": "CALLOUT", "422477374526": "CALLOUT", "89063098370": "CALLOUT"}
SHARED_NEG_LISTS_B = ["12252013691"]     # EXACT-only list (78 EXACT). 12249470554 holds PHRASE/BROAD and is NOT attached.
OWN_BRAND_EXACT = ["ambient cooling and heating", "ambient heating and cooling", "ambient cooling", "ambient heating", "ambient hvac"]
SCOPE_EXACT_B = ["heat pump repair", "heat pump repair near me", "geothermal repair", "geothermal heat pump repair", "geothermal repair near me"]
SCOPE_EXACT_A = ["furnace repair", "furnace repair near me", "boiler repair", "boiler repair near me"]
OPT_OUT = ["TEXT_ASSET_AUTOMATION", "FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION", "GENERATE_IMAGE_EXTRACTION", "GENERATE_IMAGE_ENHANCEMENT",
           "GENERATE_DESIGN_VERSIONS_FOR_IMAGES", "GENERATE_ENHANCED_YOUTUBE_VIDEOS"]
# GENERATE_LANDING_PAGE_PREVIEW, GENERATE_VIDEOS_FROM_OTHER_ASSETS, GENERATE_ANIMATED_IMAGES_FROM_OTHER_ASSETS: validate_only
# 2026-10-02 returned "The enum value is not permitted." for Performance Max, so these are not settable on PMax via the API.
IMG_DIR = CLIENT_DIR / "assets" / "pmax-geothermal-2026-10-02"

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
# Geothermal: every claim is on /geothermal-heat-pump/ (read 2026-10-02): free quote, property-specific review, replacement planning,
# new-system consultation, ground-loop arrangement, serves Severn / Severna Park / Columbia / Annapolis. No repair framing (paid scope).
GEO = dict(name="Geothermal Heat Pump", final_url=f"{O}/geothermal-heat-pump/", path1="Geothermal", path2="Heat-Pump",
           headlines=["Geothermal Heat Pumps", "Geothermal Consultation", "New Geothermal System", "Geothermal Replacement", "Plan A Geothermal System",
                      "Free Geothermal Quote", "Geothermal Heating & Cooling", "Ground-Loop System Review", "Severn Geothermal Systems",
                      "Columbia Geothermal Systems", "Annapolis Geothermal Quote", "Property-Specific Review", "Geothermal", "Replacement Planning",
                      "Central MD Geothermal"],
           long_headlines=["Geothermal heat pump consultation for homes in Severn, Severna Park and Columbia, MD",
                           "Considering geothermal? Start with a property-specific review of your home",
                           "Plan a geothermal heat pump replacement with Ambient Cooling & Heating",
                           "Explore whether a geothermal system fits your home, property and comfort goals",
                           "Request a free geothermal heat pump quote from Ambient Cooling & Heating"],
           descriptions=["Request a free geothermal heat pump quote.",
                         "Discuss your home, current heating setup and goals before choosing equipment.",
                         "Replacement planning starts with the condition of your current geothermal equipment.",
                         "Geothermal consultation for Severn, Severna Park, Columbia and Annapolis homes.", ("id", COMMON_D5)],
           images={f.name: {"_L_": "MARKETING_IMAGE", "_S_": "SQUARE_MARKETING_IMAGE", "_P_": "PORTRAIT_MARKETING_IMAGE"}[re.search(r"_[LSP]_", f.name).group(0)]
                   for f in sorted(IMG_DIR.glob("*_[LSP]_*.jpg"))},
           search_themes=["geothermal heat pump installation", "geothermal heat pump replacement", "geothermal heating and cooling", "geothermal hvac",
                          "geothermal heat pump cost", "geothermal system installation", "ground source heat pump", "geothermal installer near me",
                          "new geothermal system", "geothermal heat pump", "geothermal heating system", "geothermal contractor"])
HP_REPL_THEMES = ["heat pump replacement", "replace heat pump", "heat pump replacement near me", "heat pump replacement cost", "heat pump system replacement",
                  "new heat pump", "heat pump replacement contractor", "upgrade heat pump"]
BARRED = re.compile(r"24/7|24-7|24 hour|same[- ]day|emergenc|licens|insured|guarantee|warrant|financ|\$\d|% off|discount|years? (of )?experience|"
                    r"\d\.\d ?star|certified|fast response|within \d+ (min|hour)|repair|maint|tune|inspect|ductless|mini split|\bbest\b|cheap|rebate", re.I)


def text_checks(g):
    errs, lit = [], (lambda xs: [x for x in xs if isinstance(x, str)])
    h, lh, d = g["headlines"], g["long_headlines"], g["descriptions"]
    if len(h) != 15 or len({str(x).lower() for x in h}) != 15: errs.append(f"{g['name']}: headline count/duplicates")
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


def month_budget(c, cid):
    today = datetime.datetime.now(TZ).date()
    days_left = (datetime.date(2026, 10, 31) - today).days + 1      # the change day counts as a full day (Google mid-month rule)
    mtd = 0.0 if cid is None else sum(r.metrics.cost_micros for r in q(c, f"SELECT campaign.id, metrics.cost_micros FROM campaign WHERE campaign.id = {cid} AND segments.date DURING THIS_MONTH")) / 1e6
    return math.floor((MONTHLY - mtd) / days_left * 100) / 100, mtd, days_left, str(today)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "plan"
    c = client(); identity_gate(c, verbose=False)
    svc = c.get_service
    errs = text_checks(BOILER) + text_checks(HP_INSTALL) + text_checks(GEO)
    if not (3 <= len(GEO["images"]) <= 20 and "MARKETING_IMAGE" in GEO["images"].values() and "SQUARE_MARKETING_IMAGE" in GEO["images"].values()):
        errs.append(f"geothermal images incomplete {GEO['images']}")
    img_manifest = json.loads((IMG_DIR / "manifest.json").read_text(encoding="utf-8"))
    for f in GEO["images"]:
        if hashlib.sha256((IMG_DIR / f).read_bytes()).hexdigest()[:16] != img_manifest[f]["sha256"]: errs.append(f"image hash drift {f}")
    # ---------------- live reads ----------------
    sh = q(c, f"SELECT campaign.status, campaign.name, campaign_budget.amount_micros, campaign_budget.id FROM campaign WHERE campaign.id = {SHELL}")[0]
    if E(sh.campaign.status) != "PAUSED" or str(sh.campaign_budget.id) != SHELL_BUDGET: errs.append("shell not PAUSED or budget id changed")
    groups = {str(r.asset_group.id): (r.asset_group.name, E(r.asset_group.status)) for r in q(c,
              f"SELECT asset_group.id, asset_group.name, asset_group.status FROM asset_group WHERE campaign.id = {SHELL} AND asset_group.status != 'REMOVED'")}
    if sorted(groups) != sorted([A_GROUP_FURNACE, A_GROUP_HP_OLD]): errs.append(f"shell groups changed: {groups}")
    hp_assets = [(str(r.asset.id), E(r.asset_group_asset.field_type)) for r in q(c, f"""SELECT asset.id, asset_group_asset.field_type FROM asset_group_asset
                 WHERE asset_group.id = {A_GROUP_HP_OLD} AND asset_group_asset.status != 'REMOVED'""")]
    hp_images = {a: ft for a, ft in hp_assets if ft.endswith("IMAGE")}
    geo = sorted(r.campaign_criterion.location.geo_target_constant for r in q(c, f"""SELECT campaign_criterion.location.geo_target_constant FROM campaign_criterion
                 WHERE campaign.id = {SHELL} AND campaign_criterion.type = 'LOCATION' AND campaign_criterion.negative = FALSE"""))
    if len(geo) != 75: errs.append(f"shell has {len(geo)} locations, expected 75")
    if q(c, f"SELECT campaign.id FROM campaign WHERE campaign.name = '{B_NAME}' AND campaign.status != 'REMOVED'"): errs.append("campaign B already exists")
    lst = {E(r.shared_criterion.keyword.match_type) for r in q(c, f"SELECT shared_criterion.keyword.match_type FROM shared_criterion WHERE shared_set.id = {SHARED_NEG_LISTS_B[0]}")}
    if lst != {"EXACT"}: errs.append(f"shared list {SHARED_NEG_LISTS_B[0]} is not EXACT-only: {lst}")
    a_negs = {(r.campaign_criterion.keyword.text, E(r.campaign_criterion.keyword.match_type)) for r in q(c, f"""SELECT campaign_criterion.keyword.text,
              campaign_criterion.keyword.match_type FROM campaign_criterion WHERE campaign.id = {SHELL} AND campaign_criterion.type = 'KEYWORD'""")}
    a_goals = {(E(r.campaign_conversion_goal.category), E(r.campaign_conversion_goal.origin)): r.campaign_conversion_goal.biddable for r in q(c,
               f"SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id = {SHELL}")}
    bud_a, mtd_a, days_left, today = month_budget(c, SHELL)
    bud_b, _, _, _ = month_budget(c, None)
    if bud_a > 34 or bud_b > 34: errs.append(f"budget math out of range {bud_a} {bud_b}")
    # ---------------- operations ----------------
    apath = lambda i: svc("AssetService").asset_path(CID, i)
    ops_a, ops_b, man = [], [], {"A": [], "B": []}

    def op(lst_):
        m = c.get_type("MutateOperation"); lst_.append(m); return m

    def automation(x):
        for t in OPT_OUT:
            s = c.get_type("Campaign").AssetAutomationSetting(); s.asset_automation_type = getattr(c.enums.AssetAutomationTypeEnum, t)
            s.asset_automation_status = c.enums.AssetAutomationStatusEnum.OPTED_OUT; x.asset_automation_settings.append(s)

    m = op(ops_a); x = m.campaign_operation.update; x.resource_name = svc("CampaignService").campaign_path(CID, SHELL); x.name = A_NAME; automation(x)
    m.campaign_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["name", "asset_automation_settings"]))
    man["A"].append(f"rename {SHELL} -> '{A_NAME}'; {len(OPT_OUT)} automation opt-outs (re-asserted; unchanged)")
    m = op(ops_a); x = m.campaign_budget_operation.update; x.resource_name = svc("CampaignBudgetService").campaign_budget_path(CID, SHELL_BUDGET)
    x.amount_micros = int(round(bud_a * 100)) * 10000; m.campaign_budget_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["amount_micros"]))
    man["A"].append(f"budget {SHELL_BUDGET} ${sh.campaign_budget.amount_micros / 1e6:.2f} -> ${bud_a} (= ($1,000 - ${mtd_a:.2f} MTD) / {days_left} days incl. {today})")
    m = op(ops_a); x = m.campaign_criterion_operation.update; x.resource_name = svc("CampaignCriterionService").campaign_criterion_path(CID, SHELL, "30002")
    x.bid_modifier = 0.0; m.campaign_criterion_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["bid_modifier"]))
    man["A"].append("tablet criterion 30002: bid_modifier unset -> 0 (exclude tablets; it was NOT excluded)")
    for w in SCOPE_EXACT_A:
        if (w, "EXACT") in a_negs: continue
        m = op(ops_a); cc = m.campaign_criterion_operation.create; cc.campaign = svc("CampaignService").campaign_path(CID, SHELL); cc.negative = True
        cc.keyword.text = w; cc.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT
    man["A"].append(f"{len(SCOPE_EXACT_A)} scope EXACT negatives {SCOPE_EXACT_A} (repair is served by Search)")

    def build_group(lst_, campaign_path, g, tmp_group, tmp_start, image_map, new_images=None):
        tid, links = tmp_start, []
        for fname, ft in (new_images or {}).items():
            m = op(lst_); a = m.asset_operation.create; a.resource_name = apath(tid); a.name = f"Ambient PMax AG_GEO {fname[:-4]}"
            a.type_ = c.enums.AssetTypeEnum.IMAGE; a.image_asset.data = (IMG_DIR / fname).read_bytes()
            links.append((tid, ft)); tid -= 1
        for field, items in (("HEADLINE", g["headlines"]), ("LONG_HEADLINE", g["long_headlines"]), ("DESCRIPTION", g["descriptions"])):
            for it in items:
                if isinstance(it, tuple):
                    links.append((int(it[1]), field))
                else:
                    m = op(lst_); a = m.asset_operation.create; a.resource_name = apath(tid); a.text_asset.text = it
                    links.append((tid, field)); tid -= 1
        links.append((int(CTA), "CALL_TO_ACTION_SELECTION"))
        links += [(int(k), v) for k, v in image_map.items()]
        agp = svc("AssetGroupService").asset_group_path(CID, tmp_group)
        m = op(lst_); ag = m.asset_group_operation.create
        ag.resource_name = agp; ag.campaign = campaign_path; ag.name = g["name"]; ag.final_urls.append(g["final_url"])
        ag.path1, ag.path2 = g["path1"], g["path2"]; ag.status = c.enums.AssetGroupStatusEnum.PAUSED
        for aid, ft in links:
            m = op(lst_); l_ = m.asset_group_asset_operation.create; l_.asset_group = agp; l_.asset = apath(aid); l_.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
        for th in g["search_themes"]:
            m = op(lst_); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.search_theme.text = th
        m = op(lst_); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.audience.audience = AUDIENCE
        return len(links)

    n = build_group(ops_a, svc("CampaignService").campaign_path(CID, SHELL), BOILER, -11, -100, BOILER["images"])
    man["A"].append(f"PAUSED asset group 'Boiler Replacement' -> {BOILER['final_url']} ({n} links, {len(BOILER['search_themes'])} themes + audience)")
    # ---- B ----
    bpath, cpath = svc("CampaignBudgetService").campaign_budget_path(CID, -1), svc("CampaignService").campaign_path(CID, -2)
    m = op(ops_b); b = m.campaign_budget_operation.create; b.resource_name = bpath; b.name = f"{B_NAME} budget"
    b.amount_micros = int(round(bud_b * 100)) * 10000; b.explicitly_shared = False; b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
    m = op(ops_b); x = m.campaign_operation.create
    x.resource_name = cpath; x.name = B_NAME; x.campaign_budget = bpath; x.status = c.enums.CampaignStatusEnum.PAUSED
    x.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.PERFORMANCE_MAX; x.maximize_conversions.target_cpa_micros = 0
    x.contains_eu_political_advertising = c.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    x.geo_target_type_setting.positive_geo_target_type = c.enums.PositiveGeoTargetTypeEnum.PRESENCE
    x.geo_target_type_setting.negative_geo_target_type = c.enums.NegativeGeoTargetTypeEnum.PRESENCE
    x.brand_guidelines_enabled = True; automation(x)
    for g_rn in geo:
        m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath; cc.location.geo_target_constant = g_rn
    m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath; cc.language.language_constant = "languageConstants/1000"
    for day in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"):
        m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath
        cc.ad_schedule.day_of_week = getattr(c.enums.DayOfWeekEnum, day); cc.ad_schedule.start_hour = 8; cc.ad_schedule.end_hour = 16
        cc.ad_schedule.start_minute = c.enums.MinuteOfHourEnum.ZERO; cc.ad_schedule.end_minute = c.enums.MinuteOfHourEnum.ZERO
    m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath; cc.device.type_ = c.enums.DeviceEnum.TABLET; cc.bid_modifier = 0.0
    for w in OWN_BRAND_EXACT + SCOPE_EXACT_B:
        m = op(ops_b); cc = m.campaign_criterion_operation.create; cc.campaign = cpath; cc.negative = True
        cc.keyword.text = w; cc.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT
    for sid in SHARED_NEG_LISTS_B:
        m = op(ops_b); s_ = m.campaign_shared_set_operation.create; s_.campaign = cpath; s_.shared_set = svc("SharedSetService").shared_set_path(CID, sid)
    for aid, ft in B_CAMPAIGN_ASSETS.items():
        m = op(ops_b); ca = m.campaign_asset_operation.create; ca.campaign = cpath; ca.asset = apath(int(aid)); ca.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
    agp = svc("AssetGroupService").asset_group_path(CID, -21)
    m = op(ops_b); ag = m.asset_group_operation.create; ag.resource_name = agp; ag.campaign = cpath; ag.name = "Heat Pump Replacement"
    ag.final_urls.append(f"{O}/heat-pump-replacement/"); ag.path1, ag.path2 = "Heat-Pump", "Replacement"; ag.status = c.enums.AssetGroupStatusEnum.PAUSED
    for aid, ft in hp_assets:
        m = op(ops_b); l_ = m.asset_group_asset_operation.create; l_.asset_group = agp; l_.asset = apath(int(aid)); l_.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
    for th in HP_REPL_THEMES:
        m = op(ops_b); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.search_theme.text = th
    m = op(ops_b); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.audience.audience = AUDIENCE
    n2 = build_group(ops_b, cpath, HP_INSTALL, -22, -300, hp_images)
    n3 = build_group(ops_b, cpath, GEO, -23, -500, {}, new_images=GEO["images"])
    man["B"] = [f"budget ${bud_b} non-shared (= $1,000 / {days_left} days incl. {today})",
                f"PAUSED PMax '{B_NAME}': Max Conversions (no target, no value bidding), presence, brand guidelines, {len(OPT_OUT)} automation opt-outs",
                f"{len(geo)} locations (copied from A), English, Mon-Fri 08-16, tablet bid_modifier 0",
                f"{len(OWN_BRAND_EXACT)} own-brand + {len(SCOPE_EXACT_B)} repair-scope EXACT negatives; shared list {SHARED_NEG_LISTS_B} (EXACT only)",
                f"{len(B_CAMPAIGN_ASSETS)} campaign asset links (brand x3, call, snippet, 5 sitelinks incl. geothermal {GEO_SITELINK}, 8 callouts)",
                f"PAUSED 'Heat Pump Replacement' -> /heat-pump-replacement/ ({len(hp_assets)} existing assets, {len(HP_REPL_THEMES)} themes + audience)",
                f"PAUSED 'Heat Pump Installation' -> /heat-pump-installation/ ({n2} links)",
                f"PAUSED 'Geothermal Heat Pump' -> {GEO['final_url']} ({n3} links: {len(GEO['images'])} new images from the client page, text from the page)",
                "post-create: B campaign_conversion_goal biddable flags set equal to A's"]
    plan_a = dict(plan_name="AMB-1002-PMAX-A-2", supersedes="AMB-1002-PMAX-A-1 (never executed)", customer_id=CID, exact_account_name=EXACT_NAME,
                  never_write_to_mcc="3373711342", authorization="staged authorization 2026-10-02", work_order="work-orders/work-order-pmax-furnace-boiler-replacement-2026-10-02.yaml",
                  campaign=SHELL, campaign_name_after=A_NAME, budget=bud_a, boiler_payload=BOILER, actions=man["A"],
                  enable_after_readback=[f"campaign {SHELL}", f"asset group {A_GROUP_FURNACE} Heating & Furnace Replacement", "asset group Boiler Replacement (new)"],
                  stays_paused=[f"asset group {A_GROUP_HP_OLD} Heat Pump Replacement (portfolio moved to B)"], operation_count=len(ops_a))
    plan_b = dict(plan_name="AMB-1002-PMAX-B-2", supersedes="AMB-1002-PMAX-B-1 (never executed)", customer_id=CID, exact_account_name=EXACT_NAME,
                  never_write_to_mcc="3373711342", authorization="staged authorization 2026-10-02", work_order="work-orders/work-order-pmax-heat-pump-geothermal-2026-10-02.yaml",
                  campaign_name=B_NAME, budget=bud_b, hp_install_payload=HP_INSTALL, geothermal_payload={k: v for k, v in GEO.items()},
                  geothermal_image_sha256={f: img_manifest[f]["sha256"] for f in GEO["images"]}, hp_replacement_assets_linked=hp_assets, actions=man["B"],
                  goal_mirror_of_A={f"{k[0]}~{k[1]}": v for k, v in a_goals.items()},
                  enable_after_readback=["campaign B", "asset groups Heat Pump Replacement, Heat Pump Installation, Geothermal Heat Pump"], operation_count=len(ops_b))
    if errs:
        sys.exit("HARD STOP:\n  " + "\n  ".join(errs))

    def send(ops, validate):
        rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False; rq.validate_only = validate
        rq.mutate_operations.extend(ops); return svc("GoogleAdsService").mutate(request=rq)

    def emsg(ex):
        msgs = re.findall(r'message: "([^"]+)"', str(ex))[:4]
        idx = re.findall(r"index: (\d+)", str(ex))[:6]
        return f"{msgs} at {idx}"

    if mode == "plan":
        res = {}
        for p, ops in ((plan_a, ops_a), (plan_b, ops_b)):
            try:
                send(ops, True); res[p["plan_name"]] = f"VALIDATED {len(ops)}"
            except Exception as ex:
                res[p["plan_name"]] = "FAILED " + emsg(ex)
        print("preflight:", res)
        if any(v.startswith("FAILED") for v in res.values()):
            sys.exit("HARD STOP: validate_only failed - no plan written")
        for p in (plan_a, plan_b):
            p["preflight"] = res[p["plan_name"]]
            p["fingerprint"] = approval_code({k: v for k, v in p.items() if k != "fingerprint"})
            (PLANS / f"{p['plan_name']}.json").write_text(json.dumps(p, indent=1), encoding="utf-8")
            print(f"PLAN {p['plan_name']}: {p['fingerprint']} / {p['operation_count']} ops")
            for a in p["actions"]:
                print("   -", a)
        return
    # ---------------- run ----------------
    for p in (plan_a, plan_b):
        saved = json.loads((PLANS / f"{p['plan_name']}.json").read_text(encoding="utf-8")); fp = saved.pop("fingerprint")
        p["preflight"] = saved.get("preflight")
        if not (fp == approval_code(saved) == approval_code({k: v for k, v in p.items() if k != "fingerprint"})):
            sys.exit(f"ABORT {p['plan_name']}: payload changed since plan (rebuild)")
        p["fingerprint"] = fp
    out = RECEIPTS / "AMB-1002-PMAX-LAUNCH-EXECUTED.json"
    if out.exists():
        sys.exit("ABORT: receipt exists")
    rec = dict(plans={p["plan_name"]: p["fingerprint"] for p in (plan_a, plan_b)}, started_local=datetime.datetime.now(TZ).isoformat())

    def save(status):
        rec["status"] = status; rec["at"] = datetime.datetime.now(TZ).isoformat(); out.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")

    for key, ops in (("A", ops_a), ("B", ops_b)):
        try:
            resp = send(ops, False)
        except Exception as ex:
            rec[f"{key}_error"] = emsg(ex); save(f"STOPPED_{key}_FAILED_ATOMIC" + ("_A_WRITTEN" if key == "B" else "")); sys.exit(rec[f"{key}_error"])
        rec[f"{key}_created"] = [getattr(r, f).resource_name for r in resp.mutate_operation_responses for f in
                                 ("campaign_result", "campaign_budget_result", "asset_group_result", "asset_result") if r._pb.HasField(f)]
    cid_b = next(n.split("/")[-1] for n in rec["B_created"] if "/campaigns/" in n); rec["B_campaign_id"] = cid_b
    # goals on B mirror A
    try:
        gops = []
        bg = {(E(r.campaign_conversion_goal.category), E(r.campaign_conversion_goal.origin)): r.campaign_conversion_goal.biddable for r in q(c,
              f"SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id = {cid_b}")}
        for k, v in a_goals.items():
            if k in bg and bg[k] != v:
                g = c.get_type("CampaignConversionGoalOperation"); g.update.resource_name = f"customers/{CID}/campaignConversionGoals/{cid_b}~{k[0]}~{k[1]}"
                g.update.biddable = v; g.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["biddable"])); gops.append(g)
        if gops:
            svc("CampaignConversionGoalService").mutate_campaign_conversion_goals(customer_id=CID, operations=gops)
        rec["B_goal_updates"] = len(gops)
    except Exception as ex:
        rec["B_goal_error"] = emsg(ex); save("STOPPED_GOALS_FAILED_A_B_PAUSED"); sys.exit(rec["B_goal_error"])
    # ---- readback (paused) ----
    chk = []

    def camp_checks(cid, name, bud, n_groups_expected):
        r = q(c, f"""SELECT campaign.name, campaign.status, campaign.advertising_channel_type, campaign.bidding_strategy_type, campaign.maximize_conversions.target_cpa_micros,
                campaign_budget.amount_micros, campaign.asset_automation_settings, campaign.brand_guidelines_enabled FROM campaign WHERE campaign.id = {cid}""")[0]
        chk.append((f"{cid} name/PAUSED/PMax/MaxConv no target", r.campaign.name == name and E(r.campaign.status) == "PAUSED"
                    and E(r.campaign.bidding_strategy_type) == "MAXIMIZE_CONVERSIONS" and r.campaign.maximize_conversions.target_cpa_micros == 0))
        chk.append((f"{cid} budget ${bud}", r.campaign_budget.amount_micros == int(round(bud * 100)) * 10000))
        oo = {E(s.asset_automation_type) for s in r.campaign.asset_automation_settings if E(s.asset_automation_status) == "OPTED_OUT"}
        chk.append((f"{cid} opted out of all {len(OPT_OUT)} automations incl. Final URL expansion + text customization", set(OPT_OUT) <= oo))
        cc = q(c, f"SELECT campaign_criterion.type, campaign_criterion.negative, campaign_criterion.device.type, campaign_criterion.bid_modifier, campaign_criterion.keyword.match_type FROM campaign_criterion WHERE campaign.id = {cid}")
        dev = {E(x.campaign_criterion.device.type): ("bid_modifier" in x.campaign_criterion, x.campaign_criterion.bid_modifier) for x in cc if E(x.campaign_criterion.type) == "DEVICE"}
        chk.append((f"{cid} TABLET excluded (bid_modifier present = 0); desktop + mobile not excluded", dev.get("TABLET") == (True, 0.0)
                    and dev.get("DESKTOP", (False, 0))[0] is False and dev.get("MOBILE", (False, 0))[0] is False))
        chk.append((f"{cid} 75 locations + 5 schedule rows", sum(1 for x in cc if E(x.campaign_criterion.type) == "LOCATION") == 75
                    and sum(1 for x in cc if E(x.campaign_criterion.type) == "AD_SCHEDULE") == 5))
        return cc

    camp_checks(SHELL, A_NAME, bud_a, 3)
    ccb = camp_checks(cid_b, B_NAME, bud_b, 3)
    chk.append(("B negatives all EXACT (10)", sum(1 for x in ccb if E(x.campaign_criterion.type) == "KEYWORD" and x.campaign_criterion.negative
                                                    and E(x.campaign_criterion.keyword.match_type) == "EXACT") == len(OWN_BRAND_EXACT + SCOPE_EXACT_B)))
    sl = [str(r.shared_set.id) for r in q(c, f"SELECT shared_set.id FROM campaign_shared_set WHERE campaign.id = {cid_b} AND campaign_shared_set.status = 'ENABLED'")]
    chk.append(("B shared lists = EXACT-only list only", sl == SHARED_NEG_LISTS_B))
    ga = {r.asset_group.name: (str(r.asset_group.id), E(r.asset_group.status), list(r.asset_group.final_urls)) for r in q(c,
          f"SELECT asset_group.id, asset_group.name, asset_group.status, asset_group.final_urls FROM asset_group WHERE campaign.id IN ({SHELL},{cid_b}) AND asset_group.status != 'REMOVED'")}
    want = {"Heating & Furnace Replacement": f"{O}/hvac-replacement/", "Heat Pump Replacement": None, "Boiler Replacement": BOILER["final_url"],
            "Heat Pump Installation": HP_INSTALL["final_url"], "Geothermal Heat Pump": GEO["final_url"]}
    chk.append(("all asset groups PAUSED before enable", all(v[1] == "PAUSED" for v in ga.values())))
    chk.append(("geothermal group on the required URL", ga.get("Geothermal Heat Pump", ("", "", []))[2] == [GEO["final_url"]]))
    new_groups = {}
    for r in q(c, f"SELECT asset_group.id, asset_group.name, campaign.id, asset_group.final_urls FROM asset_group WHERE campaign.id IN ({SHELL},{cid_b}) AND asset_group.status = 'PAUSED'"):
        new_groups[(str(r.campaign.id), r.asset_group.name)] = (str(r.asset_group.id), list(r.asset_group.final_urls))
    chk.append(("B Heat Pump Replacement on /heat-pump-replacement/", new_groups.get((cid_b, "Heat Pump Replacement"), ("", []))[1] == [f"{O}/heat-pump-replacement/"]))
    geo_links = q(c, f"SELECT asset_group_asset.field_type FROM asset_group_asset WHERE asset_group.id = {new_groups[(cid_b, 'Geothermal Heat Pump')][0]} AND asset_group_asset.status != 'REMOVED'")
    chk.append((f"geothermal group links {len(geo_links)} assets incl. {len(GEO['images'])} images",
                sum(1 for x in geo_links if E(x.asset_group_asset.field_type).endswith("IMAGE")) == len(GEO["images"])))
    gb = {(E(r.campaign_conversion_goal.category), E(r.campaign_conversion_goal.origin)): r.campaign_conversion_goal.biddable for r in q(c,
          f"SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id = {cid_b}")}
    chk.append(("B biddable goals equal A's", all(gb.get(k) == v for k, v in a_goals.items() if k in gb)))
    rec["readback_paused"] = [{"check": k, "pass": v} for k, v in chk]
    if not all(v for _, v in chk):
        save("STOPPED_READBACK_FAIL_ALL_PAUSED"); [print(f"  [{'PASS' if v else 'FAIL'}] {k}") for k, v in chk]; sys.exit("readback failed - nothing enabled")
    # ---- enable ----
    enable_groups = [A_GROUP_FURNACE, new_groups[(SHELL, "Boiler Replacement")][0], new_groups[(cid_b, "Heat Pump Replacement")][0],
                     new_groups[(cid_b, "Heat Pump Installation")][0], new_groups[(cid_b, "Geothermal Heat Pump")][0]]
    eops = []
    for g in enable_groups:
        m = op(eops); x = m.asset_group_operation.update; x.resource_name = svc("AssetGroupService").asset_group_path(CID, g)
        x.status = c.enums.AssetGroupStatusEnum.ENABLED; m.asset_group_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
    for cid in (SHELL, cid_b):
        m = op(eops); x = m.campaign_operation.update; x.resource_name = svc("CampaignService").campaign_path(CID, cid)
        x.status = c.enums.CampaignStatusEnum.ENABLED; m.campaign_operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
    try:
        send(eops, False)
    except Exception as ex:
        rec["enable_error"] = emsg(ex); save("STOPPED_ENABLE_FAILED_ATOMIC_ALL_PAUSED"); sys.exit(rec["enable_error"])
    rec["enabled_groups"] = enable_groups
    chk2 = []
    st = {str(r.campaign.id): E(r.campaign.status) for r in q(c, f"SELECT campaign.id, campaign.status FROM campaign WHERE campaign.id IN ({SHELL},{cid_b})")}
    chk2.append(("A and B campaigns ENABLED", st == {SHELL: "ENABLED", cid_b: "ENABLED"}))
    gs = {str(r.asset_group.id): (r.asset_group.name, E(r.asset_group.status), E(r.asset_group.primary_status), [E(x) for x in r.asset_group.primary_status_reasons])
          for r in q(c, f"SELECT asset_group.id, asset_group.name, asset_group.status, asset_group.primary_status, asset_group.primary_status_reasons FROM asset_group WHERE campaign.id IN ({SHELL},{cid_b})")}
    chk2.append(("5 intended asset groups ENABLED", all(gs[g][1] == "ENABLED" for g in enable_groups)))
    chk2.append((f"old A heat pump group {A_GROUP_HP_OLD} still PAUSED", gs[A_GROUP_HP_OLD][1] == "PAUSED"))
    for cid in (SHELL, cid_b):
        d = {E(x.campaign_criterion.device.type): ("bid_modifier" in x.campaign_criterion, x.campaign_criterion.bid_modifier) for x in q(c,
             f"SELECT campaign_criterion.device.type, campaign_criterion.bid_modifier FROM campaign_criterion WHERE campaign.id = {cid} AND campaign_criterion.type = 'DEVICE'")}
        chk2.append((f"{cid} tablet exclusion still saved after enable", d.get("TABLET") == (True, 0.0)))
    rec["asset_group_status_after_enable"] = gs
    rec["readback_enabled"] = [{"check": k, "pass": v} for k, v in chk2]
    save("EXECUTED" if all(v for _, v in chk2) else "EXECUTED_READBACK_FAIL")
    for k, v in chk + chk2:
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print(rec["status"], rec["at"], "B campaign", cid_b, "groups", {g: gs[g][:3] for g in enable_groups})


if __name__ == "__main__":
    main()
