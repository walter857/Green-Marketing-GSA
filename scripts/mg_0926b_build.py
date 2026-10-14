#!/usr/bin/env python3
"""MasterGrass - Live (9487471092) | 2026-09-26 | owner-requested build, gated.

Packages (each has its own fingerprint and its own approval):
  MG-0926-BUD    Hardscaping budget $33.00 -> $13.00 (frees $20 for the PMax; total unchanged)
  MG-0926-NEG    new shared negative list (NEG-0926-2-DRAFT.csv SHARED rows) attached to Landscaping
                 + Hardscaping, and 7 Hardscaping cross-negatives
  MG-0926-RSA    20 new city-free RSAs (2 per ad group) created PAUSED + 3 new callouts linked PAUSED
  MG-0926-PMAX   Drainage PMax created PAUSED: own $20 budget, Max Conversions (account-default goals),
                 Landscaping's geo/language/schedule, shared negative list + 24 cross-negatives, business
                 name + logo, sitelinks/callouts/snippet, 1 asset group PAUSED (15 H / 5 LH / 5 D /
                 17 images / CTA), 20 search themes, audience signal
  (enable is a separate plan built from the readback IDs after creation)

Modes:  plan | validate [--pkg X] | execute --pkg X --fp CODE
Order:  BUD -> NEG -> RSA -> PMAX (PMAX resolves the NEG shared list and the RSA callouts by name).
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

from google.protobuf import field_mask_pb2

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mg_lib import CID, EXACT_NAME, GM_MANAGER, PLANS, ROOT, TZ, E, client, q  # noqa: E402
from mg_0926b_copy import NEW_CALLOUTS, PMAX_TEXT, RSAS, check_all  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

RECEIPTS = ROOT / "clients" / "mastergrass-lawn-care" / "receipts"
RECEIPTS.mkdir(parents=True, exist_ok=True)
LAND, HARD = "23905193676", "23914692658"
HARD_BUDGET = "15625559646"
HARD_BUDGET_FROM, HARD_BUDGET_TO = 33.00, 13.00
PMAX_BUDGET = 20.00
NEG_LIST_NAME = "GM | MasterGrass | Low-intent & off-service | 2026-09"
PMAX_NAME = "PMax | Drainage | French Drain & Yard Drainage | 2026-09"
AG_NAME = "French Drain & Yard Drainage"
FINAL_URL = "https://offer.mastergrasslawncare.com/french-drain/"
IMG_DIR = ROOT / "clients" / "mastergrass-lawn-care" / "exports" / "pmax-drainage-images-2026-09-26"
BUSINESS_NAME_ASSET = "271703655260"  # 'Master Grass'
SITELINKS = {"389018280341": "French Drain Services", "389018280344": "Yard Grading Services",
             "421378509029": "Request A Grading Quote", "389018280338": "Landscaping Contractor",
             "389192654853": "Retaining Walls"}
CALLOUTS = {"389202648207": "Free Estimates", "389202648216": "Drainage Solutions",
            "389202648219": "French Drain Services", "389202648231": "Wet Yard Drainage Help",
            "389202648222": "Yard Grading Help", "389202648213": "Residential Projects",
            "389202648210": "Local Contractors"}
SNIPPET = ("Services", ["French Drains", "Yard Drainage", "Yard Grading", "Regrading", "Yard Leveling",
                        "Wet Yard Drainage"])
AUTOMATION_OFF = ["TEXT_ASSET_AUTOMATION", "FINAL_URL_EXPANSION_TEXT_ASSET_AUTOMATION",
                  "GENERATE_IMAGE_EXTRACTION", "GENERATE_IMAGE_ENHANCEMENT",
                  "GENERATE_DESIGN_VERSIONS_FOR_IMAGES", "GENERATE_ENHANCED_YOUTUBE_VIDEOS"]
CUSTOM_AUDIENCE_NAME = "GM | MasterGrass | Drainage search intent | 2026-09"
CUSTOM_AUDIENCE_TERMS = ["french drain", "french drain installation", "yard drainage", "yard drainage solutions",
                         "standing water in yard", "soggy yard", "drainage contractor", "water pooling in yard",
                         "wet yard", "backyard drainage", "lawn drainage", "yard grading"]
AUDIENCE_NAME = "GM | MasterGrass | Drainage PMax signal | 2026-09"
USER_LISTS = ["7884187726", "8012296976"]  # All visitors; Visited Offer Page but Did not Convert
STANDIN_CUSTOM_AUDIENCE = "736915159"      # validate_only ONLY
SLOT = {"L": "MARKETING_IMAGE", "S": "SQUARE_MARKETING_IMAGE", "P": "PORTRAIT_MARKETING_IMAGE"}


# ------------------------------------------------------------------ data
def neg_rows():
    rows = list(csv.DictReader((PLANS / "NEG-0926-2-DRAFT.csv").open(encoding="utf-8")))
    shared = [(r["text"], r["match_type"]) for r in rows if r["target"] == "SHARED"]
    hard = [r["text"] for r in rows if r["target"] == f"CAMPAIGN:{HARD}"]
    pmax = [r["text"] for r in rows if r["target"] == "CAMPAIGN:PMAX"]
    return shared, hard, pmax


def images():
    man = json.loads((IMG_DIR / "manifest.json").read_text(encoding="utf-8"))
    out = []
    for m in man:
        data = (IMG_DIR / m["file"]).read_bytes()
        slot = "LOGO" if m["slot"] == "LOGO" else SLOT[m["slot"]]
        out.append({"file": m["file"], "slot": slot, "size": m["size"], "sha256": hashlib.sha256(data).hexdigest(),
                    "source": m["source_url"]})
    return out


def identity(c):
    row = q(c, "SELECT customer.id, customer.descriptive_name, customer.manager, customer.test_account FROM customer")[0].customer
    ok = str(row.id) == CID and row.descriptive_name == EXACT_NAME and not row.manager and not row.test_account
    links = {x.customer_manager_link.manager_customer.split("/")[-1]: E(x.customer_manager_link.status)
             for x in q(c, "SELECT customer_manager_link.manager_customer, customer_manager_link.status FROM customer_manager_link")}
    if not ok or links.get(GM_MANAGER) != "ACTIVE":
        sys.exit(f"IDENTITY GATE FAIL {row.id} {row.descriptive_name} {links}")


def geo_from_landscaping(c):
    out = []
    for r in q(c, f"""SELECT campaign_criterion.type, campaign_criterion.negative, campaign_criterion.location.geo_target_constant,
                         campaign_criterion.proximity.radius, campaign_criterion.proximity.radius_units,
                         campaign_criterion.proximity.geo_point.latitude_in_micro_degrees,
                         campaign_criterion.proximity.geo_point.longitude_in_micro_degrees
                      FROM campaign_criterion WHERE campaign.id = {LAND} AND campaign_criterion.type IN ('LOCATION','PROXIMITY')"""):
        cc = r.campaign_criterion
        if E(cc.type_) == "LOCATION":
            out.append({"t": "LOCATION", "geo": cc.location.geo_target_constant, "neg": cc.negative})
        else:
            out.append({"t": "PROXIMITY", "radius": cc.proximity.radius, "units": E(cc.proximity.radius_units),
                        "lat": cc.proximity.geo_point.latitude_in_micro_degrees,
                        "lng": cc.proximity.geo_point.longitude_in_micro_degrees})
    return sorted(out, key=lambda x: json.dumps(x, sort_keys=True))


def schedule_from_landscaping(c):
    out = []
    for r in q(c, f"""SELECT campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour,
                         campaign_criterion.ad_schedule.end_hour FROM campaign_criterion
                      WHERE campaign.id = {LAND} AND campaign_criterion.type = 'AD_SCHEDULE'"""):
        a = r.campaign_criterion.ad_schedule
        out.append({"day": E(a.day_of_week), "start": a.start_hour, "end": a.end_hour})
    return sorted(out, key=lambda x: x["day"])


# ------------------------------------------------------------------ manifests (what gets fingerprinted)
def manifests(c):
    shared, hard, pmax_neg = neg_rows()
    geo = geo_from_landscaping(c)
    sched = schedule_from_landscaping(c)
    base = {"customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": GM_MANAGER}
    return {
        "MG-0926-BUD": {**base, "package": "MG-0926-BUD", "action": "UPDATE campaign_budget.amount_micros",
                        "budget": HARD_BUDGET, "campaign": HARD, "from": HARD_BUDGET_FROM, "to": HARD_BUDGET_TO,
                        "why": "free $20/day for the drainage PMax; account daily total unchanged"},
        "MG-0926-NEG": {**base, "package": "MG-0926-NEG", "shared_set": {"name": NEG_LIST_NAME, "type": "NEGATIVE_KEYWORDS"},
                        "members": shared, "attach_to": [LAND, HARD], "hardscaping_cross_negatives_phrase": hard,
                        "source": "clients/mastergrass-lawn-care/plans/NEG-0926-2-DRAFT.csv",
                        "counts": {"members": len(shared), "phrase": sum(1 for _, m in shared if m == "PHRASE"),
                                   "exact": sum(1 for _, m in shared if m == "EXACT"), "hard_cross": len(hard)}},
        "MG-0926-RSA": {**base, "package": "MG-0926-RSA", "status_on_create": "PAUSED",
                        "ads": {ag: {"campaign": g["campaign"], "ad_group": g["ad_group"], "final_url": g["url"],
                                     "path": list(g["path"]), "A": g["A"], "B": g["B"]} for ag, g in RSAS.items()},
                        "new_callouts": NEW_CALLOUTS, "callout_links": [LAND, HARD], "callout_link_status": "PAUSED",
                        "counts": {"rsas": 2 * len(RSAS), "callout_assets": len(NEW_CALLOUTS),
                                   "callout_links": 2 * len(NEW_CALLOUTS)}},
        "MG-0926-PMAX": {**base, "package": "MG-0926-PMAX", "campaign_name": PMAX_NAME, "status_on_create": "PAUSED",
                         "budget": {"amount": PMAX_BUDGET, "shared": False}, "bidding": "MAXIMIZE_CONVERSIONS, no target CPA",
                         "goals": "account default (PHONE_CALL_LEAD website+call-from-ads, SUBMIT_LEAD_FORM website); WC Call Lead (QUALIFIED_LEAD) stays non-biddable",
                         "geo": geo, "geo_type": "PRESENCE", "language": "languageConstants/1000", "schedule": sched,
                         "negatives": {"shared_list": NEG_LIST_NAME, "cross_phrase": pmax_neg},
                         "asset_automation_opted_out": AUTOMATION_OFF, "brand_guidelines_enabled": True,
                         "campaign_assets": {"business_name": BUSINESS_NAME_ASSET, "logo": "mg_logo_square_192.png",
                                             "sitelinks": SITELINKS, "callouts": CALLOUTS, "new_callouts_by_text": NEW_CALLOUTS,
                                             "snippet": SNIPPET},
                         "asset_group": {"name": AG_NAME, "final_url": FINAL_URL, "path": ["French-Drains", "Free-Quote"],
                                         "status": "PAUSED", "text": PMAX_TEXT, "cta": "GET_QUOTE",
                                         "images": [i for i in images() if i["slot"] != "LOGO"]},
                         "logo_image": [i for i in images() if i["slot"] == "LOGO"],
                         "audience_signal": {"custom_audience": {"name": CUSTOM_AUDIENCE_NAME, "type": "SEARCH",
                                                                 "keywords": CUSTOM_AUDIENCE_TERMS},
                                             "audience": AUDIENCE_NAME, "user_lists": USER_LISTS},
                         "videos": "none supplied; Google may auto-generate (not opt-out-able at create in v25)"},
    }


# ------------------------------------------------------------------ operation builders
def op(c, ops):
    m = c.get_type("MutateOperation")
    ops.append(m)
    return m


def build_bud(c, m):
    ops = []
    o = op(c, ops).campaign_budget_operation
    o.update.resource_name = c.get_service("CampaignBudgetService").campaign_budget_path(CID, HARD_BUDGET)
    o.update.amount_micros = int(HARD_BUDGET_TO * 1e6)
    o.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["amount_micros"]))
    return ops


def build_neg(c, m):
    ops = []
    ssp = c.get_service("SharedSetService").shared_set_path(CID, -1)
    s = op(c, ops).shared_set_operation.create
    s.resource_name = ssp
    s.name = NEG_LIST_NAME
    s.type_ = c.enums.SharedSetTypeEnum.NEGATIVE_KEYWORDS
    for text, mt in m["members"]:
        sc = op(c, ops).shared_criterion_operation.create
        sc.shared_set = ssp
        sc.keyword.text = text
        sc.keyword.match_type = getattr(c.enums.KeywordMatchTypeEnum, mt)
    for cid in m["attach_to"]:
        cs = op(c, ops).campaign_shared_set_operation.create
        cs.campaign = c.get_service("CampaignService").campaign_path(CID, cid)
        cs.shared_set = ssp
    for text in m["hardscaping_cross_negatives_phrase"]:
        cc = op(c, ops).campaign_criterion_operation.create
        cc.campaign = c.get_service("CampaignService").campaign_path(CID, HARD)
        cc.negative = True
        cc.keyword.text = text
        cc.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
    return ops


def build_rsa(c, m):
    ops = []
    agsvc = c.get_service("AdGroupService")
    for ag, g in m["ads"].items():
        for k in ("A", "B"):
            a = op(c, ops).ad_group_ad_operation.create
            a.ad_group = agsvc.ad_group_path(CID, ag)
            a.status = c.enums.AdGroupAdStatusEnum.PAUSED
            a.ad.final_urls.append(g["final_url"])
            rsa = a.ad.responsive_search_ad
            rsa.path1, rsa.path2 = g["path"]
            for text, pin in g[k]["headlines"]:
                h = c.get_type("AdTextAsset")
                h.text = text
                if pin:
                    h.pinned_field = getattr(c.enums.ServedAssetFieldTypeEnum, pin)
                rsa.headlines.append(h)
            for text in g[k]["descriptions"]:
                d = c.get_type("AdTextAsset")
                d.text = text
                rsa.descriptions.append(d)
    apath = c.get_service("AssetService").asset_path
    for i, text in enumerate(m["new_callouts"]):
        a = op(c, ops).asset_operation.create
        a.resource_name = apath(CID, -10 - i)
        a.callout_asset.callout_text = text
    for cid in m["callout_links"]:
        for i, _ in enumerate(m["new_callouts"]):
            ca = op(c, ops).campaign_asset_operation.create
            ca.campaign = c.get_service("CampaignService").campaign_path(CID, cid)
            ca.asset = apath(CID, -10 - i)
            ca.field_type = c.enums.AssetFieldTypeEnum.CALLOUT
            ca.status = c.enums.AssetLinkStatusEnum.PAUSED
    return ops


def resolve_pmax_refs(c, standin=False):
    """Shared list + new callouts created by NEG / RSA packages; stand-ins only for validate."""
    ss = [r.shared_set.resource_name for r in q(c, f"SELECT shared_set.resource_name FROM shared_set WHERE shared_set.name = '{NEG_LIST_NAME}' AND shared_set.status = 'ENABLED'")]
    co = {}
    for r in q(c, "SELECT asset.resource_name, asset.callout_asset.callout_text FROM asset WHERE asset.type = 'CALLOUT'"):
        if r.asset.callout_asset.callout_text in NEW_CALLOUTS:
            co.setdefault(r.asset.callout_asset.callout_text, r.asset.resource_name)
    if standin:
        if not ss:
            ss = [r.shared_set.resource_name for r in q(c, "SELECT shared_set.resource_name FROM shared_set WHERE shared_set.name = 'State Name List'")]
        for t, sid in zip(NEW_CALLOUTS, ("389205053181", "389205053184", "389205053187")):
            co.setdefault(t, c.get_service("AssetService").asset_path(CID, sid))  # validate_only stand-ins
    return (ss[0] if ss else None), co


def build_pmax(c, m, standin=False, custom_audience_rn=None):
    ops = []
    ga_path = c.get_service("AssetService").asset_path
    cpath = c.get_service("CampaignService").campaign_path(CID, -2)
    bpath = c.get_service("CampaignBudgetService").campaign_budget_path(CID, -1)
    b = op(c, ops).campaign_budget_operation.create
    b.resource_name = bpath
    b.name = f"{PMAX_NAME} budget"
    b.amount_micros = int(PMAX_BUDGET * 1e6)
    b.explicitly_shared = False
    b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
    x = op(c, ops).campaign_operation.create
    x.resource_name = cpath
    x.name = PMAX_NAME
    x.campaign_budget = bpath
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
    for g in m["geo"]:
        cc = op(c, ops).campaign_criterion_operation.create
        cc.campaign = cpath
        if g["t"] == "LOCATION":
            cc.location.geo_target_constant = g["geo"]
            cc.negative = g["neg"]
        else:
            cc.proximity.radius = g["radius"]
            cc.proximity.radius_units = getattr(c.enums.ProximityRadiusUnitsEnum, g["units"])
            cc.proximity.geo_point.latitude_in_micro_degrees = g["lat"]
            cc.proximity.geo_point.longitude_in_micro_degrees = g["lng"]
    cc = op(c, ops).campaign_criterion_operation.create
    cc.campaign = cpath
    cc.language.language_constant = m["language"]
    for s_ in m["schedule"]:
        cc = op(c, ops).campaign_criterion_operation.create
        cc.campaign = cpath
        cc.ad_schedule.day_of_week = getattr(c.enums.DayOfWeekEnum, s_["day"])
        cc.ad_schedule.start_hour = s_["start"]
        cc.ad_schedule.end_hour = s_["end"]
        cc.ad_schedule.start_minute = c.enums.MinuteOfHourEnum.ZERO
        cc.ad_schedule.end_minute = c.enums.MinuteOfHourEnum.ZERO
    for text in m["negatives"]["cross_phrase"]:
        cc = op(c, ops).campaign_criterion_operation.create
        cc.campaign = cpath
        cc.negative = True
        cc.keyword.text = text
        cc.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
    ss, new_co = resolve_pmax_refs(c, standin)
    if not ss or len(new_co) != len(NEW_CALLOUTS):
        raise SystemExit(f"ABORT: run MG-0926-NEG and MG-0926-RSA first (shared list {ss}, callouts {sorted(new_co)})")
    cs = op(c, ops).campaign_shared_set_operation.create
    cs.campaign = cpath
    cs.shared_set = ss
    # assets: snippet, logo, images, texts, CTA (temp ids)
    tid = [-100]

    def new_asset():
        a = op(c, ops).asset_operation.create
        a.resource_name = ga_path(CID, tid[0])
        tid[0] -= 1
        return a
    a = new_asset()
    a.name = "GM 2026-09-26 drainage PMax services snippet"
    a.structured_snippet_asset.header = SNIPPET[0]
    a.structured_snippet_asset.values.extend(SNIPPET[1])
    snippet_rn = a.resource_name
    logo = m["logo_image"][0]
    a = new_asset()
    a.name = "MasterGrass logo 192 square (website) 2026-09-26"
    a.type_ = c.enums.AssetTypeEnum.IMAGE
    a.image_asset.data = (IMG_DIR / logo["file"]).read_bytes()
    logo_rn = a.resource_name
    links = [(BUSINESS_NAME_ASSET, "BUSINESS_NAME"), (logo_rn, "LOGO"), (snippet_rn, "STRUCTURED_SNIPPET")]
    links += [(k, "SITELINK") for k in m["campaign_assets"]["sitelinks"]]
    links += [(k, "CALLOUT") for k in m["campaign_assets"]["callouts"]]
    links += [(new_co[t], "CALLOUT") for t in NEW_CALLOUTS]
    for aid, ft in links:
        ca = op(c, ops).campaign_asset_operation.create
        ca.campaign = cpath
        ca.asset = aid if "/" in str(aid) else ga_path(CID, aid)
        ca.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
    ag_links = []
    for img in m["asset_group"]["images"]:
        a = new_asset()
        a.name = f"MG drainage PMax {img['file']} {img['sha256'][:8]}"
        a.type_ = c.enums.AssetTypeEnum.IMAGE
        a.image_asset.data = (IMG_DIR / img["file"]).read_bytes()
        ag_links.append((a.resource_name, img["slot"]))
    t = m["asset_group"]["text"]
    for text, ft in [(h, "HEADLINE") for h in t["headlines"]] + [(h, "LONG_HEADLINE") for h in t["long_headlines"]] + \
                    [(d, "DESCRIPTION") for d in t["descriptions"]]:
        a = new_asset()
        a.text_asset.text = text
        ag_links.append((a.resource_name, ft))
    a = new_asset()
    a.call_to_action_asset.call_to_action = c.enums.CallToActionTypeEnum.GET_QUOTE
    ag_links.append((a.resource_name, "CALL_TO_ACTION_SELECTION"))
    agp = c.get_service("AssetGroupService").asset_group_path(CID, -3)
    ag = op(c, ops).asset_group_operation.create
    ag.resource_name = agp
    ag.campaign = cpath
    ag.name = m["asset_group"]["name"]
    ag.final_urls.append(m["asset_group"]["final_url"])
    ag.path1, ag.path2 = m["asset_group"]["path"]
    ag.status = c.enums.AssetGroupStatusEnum.PAUSED
    for rn, ft in ag_links:
        l_ = op(c, ops).asset_group_asset_operation.create
        l_.asset_group = agp
        l_.asset = rn
        l_.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
    for th in t["search_themes"]:
        s_ = op(c, ops).asset_group_signal_operation.create
        s_.asset_group = agp
        s_.search_theme.text = th
    # audience signal
    aud_rn = c.get_service("AudienceService").audience_path(CID, -4)
    au = op(c, ops).audience_operation.create
    au.resource_name = aud_rn
    au.name = AUDIENCE_NAME
    dim = c.get_type("AudienceDimension")
    for ul in USER_LISTS:
        seg = c.get_type("AudienceSegment")
        seg.user_list.user_list = c.get_service("UserListService").user_list_path(CID, ul)
        dim.audience_segments.segments.append(seg)
    seg = c.get_type("AudienceSegment")
    seg.custom_audience.custom_audience = custom_audience_rn or c.get_service("CustomAudienceService").custom_audience_path(CID, STANDIN_CUSTOM_AUDIENCE)
    dim.audience_segments.segments.append(seg)
    au.dimensions.append(dim)
    s_ = op(c, ops).asset_group_signal_operation.create
    s_.asset_group = agp
    s_.audience.audience = aud_rn
    return ops


def create_custom_audience(c, validate_only):
    svc = c.get_service("CustomAudienceService")
    o = c.get_type("CustomAudienceOperation")
    ca = o.create
    ca.name = CUSTOM_AUDIENCE_NAME
    ca.type_ = c.enums.CustomAudienceTypeEnum.SEARCH
    ca.status = c.enums.CustomAudienceStatusEnum.ENABLED
    for t in CUSTOM_AUDIENCE_TERMS:
        mem = c.get_type("CustomAudienceMember")
        mem.member_type = c.enums.CustomAudienceMemberTypeEnum.KEYWORD
        mem.keyword = t
        ca.members.append(mem)
    rq = c.get_type("MutateCustomAudiencesRequest")
    rq.customer_id = CID
    rq.operations.append(o)
    rq.validate_only = validate_only
    r = svc.mutate_custom_audiences(request=rq)
    return None if validate_only else r.results[0].resource_name


BUILDERS = {"MG-0926-BUD": build_bud, "MG-0926-NEG": build_neg, "MG-0926-RSA": build_rsa, "MG-0926-PMAX": build_pmax}


def mutate(c, ops, validate_only):
    rq = c.get_type("MutateGoogleAdsRequest")
    rq.customer_id = CID
    rq.partial_failure = False
    rq.validate_only = validate_only
    rq.mutate_operations.extend(ops)
    return c.get_service("GoogleAdsService").mutate(request=rq)


def err_summary(ex):
    msgs = re.findall(r'message: "([^"]+)"', str(ex))
    idx = re.findall(r"index: (\d+)", str(ex))
    return msgs[:6], idx[:8]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["plan", "validate", "execute"])
    ap.add_argument("--pkg", choices=list(BUILDERS))
    ap.add_argument("--fp")
    a = ap.parse_args()
    errs = check_all()
    if errs:
        sys.exit(f"COPY ERRORS {errs}")
    c = client()
    identity(c)
    man = manifests(c)
    fps = {k: approval_code(v) for k, v in man.items()}
    if a.mode == "plan":
        for k, v in man.items():
            v2 = dict(v, fingerprint=fps[k], built_local=datetime.datetime.now(TZ).isoformat(timespec="seconds"))
            (PLANS / f"{k}.json").write_text(json.dumps(v2, indent=1, default=str), encoding="utf-8")
            print(f"PLAN {k:<14} {fps[k]}")
        return
    pkgs = [a.pkg] if a.pkg else list(BUILDERS)
    if a.mode == "validate":
        for k in pkgs:
            try:
                if k == "MG-0926-PMAX":
                    create_custom_audience(c, validate_only=True)
                ops = BUILDERS[k](c, man[k], standin=True) if k == "MG-0926-PMAX" else BUILDERS[k](c, man[k])
                mutate(c, ops, True)
                print(f"VALIDATE {k:<14} {len(ops):>4} ops PASS  fp {fps[k]}")
            except SystemExit as ex:
                print(f"VALIDATE {k:<14} SKIP {ex}")
            except Exception as ex:  # noqa: BLE001
                print(f"VALIDATE {k:<14} FAIL {err_summary(ex)}")
        return
    k = a.pkg
    if not k or a.fp != fps[k]:
        sys.exit(f"ABORT: fingerprint mismatch for {k}: expected {fps.get(k)} got {a.fp}")
    rec = {"package": k, "fingerprint": fps[k], "started_local": datetime.datetime.now(TZ).isoformat()}
    out = RECEIPTS / f"{k}-EXECUTED.json"
    try:
        ca_rn = create_custom_audience(c, validate_only=False) if k == "MG-0926-PMAX" else None
        rec["custom_audience"] = ca_rn
        ops = BUILDERS[k](c, man[k], custom_audience_rn=ca_rn) if k == "MG-0926-PMAX" else BUILDERS[k](c, man[k])
        resp = mutate(c, ops, False)
    except Exception as ex:  # noqa: BLE001
        rec["error"] = str(ex)[:3000]
        out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
        sys.exit(f"STOP {k}: {err_summary(ex)} - receipt {out.name}")
    names = []
    for r in resp.mutate_operation_responses:
        for f in r._pb.DESCRIPTOR.fields:
            if r._pb.HasField(f.name):
                names.append(getattr(r, f.name).resource_name)
    rec["created_or_updated"] = names
    rec["finished_local"] = datetime.datetime.now(TZ).isoformat()
    out.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(f"EXECUTED {k}: {len(names)} resources | receipt {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
