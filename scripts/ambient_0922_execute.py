#!/usr/bin/env python3
"""Ambient | 2026-09-22 | EXECUTE the heating transition.

Writes ONLY to child account 2401959466. Never to MCC 3373711342.

Stages, in order, each an atomic mutate with partial_failure=False:
  A  AMB-0922-BUILD-1              create everything PAUSED, fix schedules
  B  AMB-0922-COOLPAUSE-BUDGET-1   pause cooling FIRST, then reallocate
  C  AMB-0922-ENABLE-1             enable only the ad groups that passed every check

Run with --preflight to validate_only every stage and write nothing.
Run with --stage A|B|C to execute one stage.

Committed resource IDs are recorded after every stage, so a mid-sequence failure can be
inventoried rather than replayed.
"""
from __future__ import annotations
import sys, json, argparse, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-22"
LIVE = ROOT / "receipts" / "live"
FP = {"AMB-0922-BUILD-1": ("8DD927A1B208", 159),
      "AMB-0922-COOLPAUSE-BUDGET-1": ("44EAF19FC7D6", 11),
      "AMB-0922-ENABLE-1": ("6493C57EDAC1", 54)}
DAY = {"MONDAY": "MONDAY", "TUESDAY": "TUESDAY", "WEDNESDAY": "WEDNESDAY",
       "THURSDAY": "THURSDAY", "FRIDAY": "FRIDAY"}

rec = {"started": datetime.datetime.now(TZ).isoformat(), "customer_id": CID,
       "mcc_never_written": GM_MANAGER, "stages": [], "committed": {}}


def save(tag=""):
    LIVE.mkdir(parents=True, exist_ok=True)
    (LIVE / f"AMB-0922-TRANSITION-{STAMP}{tag}.json").write_text(
        json.dumps(rec, indent=1, default=str), encoding="utf-8")


def die(msg):
    rec["ABORT"] = msg
    save("-ABORT")
    print(f"\n*** ABORT: {msg} ***")
    print(f"*** COMMITTED SO FAR: {json.dumps(rec['committed'], default=str)[:1500]} ***")
    sys.exit(2)


def load(name):
    p = json.loads((PLANS / f"{name}.json").read_text(encoding="utf-8"))
    fp = p.pop("fingerprint"); re_fp = approval_code(p); p["fingerprint"] = fp
    want_fp, want_ops = FP[name]
    if not (fp == re_fp == want_fp) or p["operation_count"] != want_ops:
        die(f"{name}: fingerprint/op-count mismatch disk={fp} recomputed={re_fp} "
            f"expected={want_fp} ops={p['operation_count']} expected_ops={want_ops}")
    print(f"  {name}: fingerprint {fp} verified, {p['operation_count']} operations")
    return p


def _pf_key(o):
    """Identify what a preflight operation actually TARGETS, so only true stand-in
    collisions collapse and genuinely distinct payloads all get tested."""
    def ohas(f):
        try:
            return o._pb.HasField(f)
        except ValueError:
            return False

    if ohas("update"):
        return ("u", o.update.resource_name)
    if ohas("remove"):
        return ("r", o.remove)
    cr = o.create
    parts = ["c", getattr(cr, "campaign", ""), getattr(cr, "ad_group", "")]
    for f in ("name", "asset"):
        parts.append(str(getattr(cr, f, "")))
    parts.append(str(getattr(cr, "field_type", "")))
    def has(f):
        try:
            return cr._pb.HasField(f)
        except ValueError:
            return False

    if has("keyword"):
        parts += [cr.keyword.text, str(cr.keyword.match_type), str(cr.negative)]
    if has("ad_schedule"):
        parts += [str(cr.ad_schedule.day_of_week), str(cr.ad_schedule.start_hour)]
    if has("location"):
        parts.append(cr.location.geo_target_constant)
    if has("ad"):
        hs = cr.ad.responsive_search_ad.headlines
        parts.append(hs[0].text if hs else "")
        parts.append(cr.ad.final_urls[0] if cr.ad.final_urls else "")
    if has("structured_snippet_asset"):
        parts.append("|".join(cr.structured_snippet_asset.values))
    return tuple(parts)


def _dedupe_for_preflight(ops, label):
    """Under --preflight every NEW resource collapses onto ONE real stand-in, so a batch
    can target the same resource twice. Google then returns ID_EXISTS_IN_MULTIPLE_MUTATES
    or AD_SCHEDULE_TIME_INTERVALS_OVERLAP - artefacts of the probe, not plan defects,
    because in execution each resource has its own id. Only exact target collisions are
    dropped; every distinct keyword, ad, negative and asset is still validated."""
    seen, keep, dropped = set(), [], 0
    for o in ops:
        k = _pf_key(o)
        if k in seen:
            dropped += 1
            continue
        seen.add(k)
        keep.append(o)
    if dropped:
        print(f"    {label}: preflight de-duplicated {dropped} stand-in collision(s)")
    return keep


def mutate(svc, req_type, ops, dry, label, partial=False):
    """One atomic mutate. Returns resource names, or [] under --preflight."""
    if dry:
        ops = _dedupe_for_preflight(ops, label)
    r = c.get_type(req_type)
    r.customer_id = CID
    r.operations.extend(ops)
    r.partial_failure = partial
    r.validate_only = dry
    try:
        resp = getattr(c.get_service(svc), MUT[svc])(request=r)
    except Exception as ex:
        if dry:
            print(f"    {label}: VALIDATE FAILED {str(ex)[:300]}")
            rec.setdefault("preflight_failures", []).append(f"{label}: {str(ex)[:400]}")
            return None
        die(f"{label}: {str(ex)[:600]}")
    names = [x.resource_name for x in resp.results] if not dry else []
    print(f"    {label}: {'VALIDATED' if dry else 'COMMITTED'} {len(ops)} ops")
    return names


MUT = {"CampaignBudgetService": "mutate_campaign_budgets",
       "CampaignService": "mutate_campaigns",
       "CampaignCriterionService": "mutate_campaign_criteria",
       "AdGroupService": "mutate_ad_groups",
       "AdGroupCriterionService": "mutate_ad_group_criteria",
       "AdGroupAdService": "mutate_ad_group_ads",
       "AssetService": "mutate_assets",
       "CampaignAssetService": "mutate_campaign_assets"}


def rid(resource_name):
    return resource_name.rsplit("/", 1)[-1].split("~")[-1]


# ============================================================== identity gate
c = client()
row = q(c, """SELECT customer.id, customer.descriptive_name, customer.manager,
              customer.test_account, customer.time_zone, customer.currency_code
              FROM customer""")[0].customer
assert (row.descriptive_name == EXACT_NAME and str(row.id) == CID
        and not row.manager and not row.test_account
        and row.time_zone == "America/New_York"), "IDENTITY GATE FAILED"
print(f"identity re-confirmed: {row.descriptive_name} / {row.id} / {row.time_zone}")

ap = argparse.ArgumentParser()
ap.add_argument("--preflight", action="store_true")
ap.add_argument("--stage", default="")
args = ap.parse_args()
DRY = args.preflight
rec["mode"] = "PREFLIGHT validate_only" if DRY else f"EXECUTE stage {args.stage}"
print(f"\nMODE: {rec['mode']}\n")

print("=== plans ===")
build = load("AMB-0922-BUILD-1")
coolb = load("AMB-0922-COOLPAUSE-BUDGET-1")
enab = load("AMB-0922-ENABLE-1")

AG = build["ad_groups"]
CAMPAIGNS = build["campaigns"]
XNEG = build["cross_negatives"]
SCHEDULE = build["schedule"]
NEWC = [k for k, v in CAMPAIGNS.items() if not v["reuse"]]

snap = json.loads((SNAP / "heating-build-snapshot-2026-09-17.json").read_text(
    encoding="utf-8"))
GEO = snap["reusable_geo_target_ids"]
assert len(GEO) == 75, f"expected 75 geo targets, got {len(GEO)}"

CS = c.get_service("CampaignService")
AGS = c.get_service("AdGroupService")
CBS = c.get_service("CampaignBudgetService")

# resolve live ad-group ids for the three reused ad groups
EXIST_AG = {"SKAG | Furnace Repair": "199797580706",
            "SKAG | Ductless Heating Installation": "199797580746",
            "SKAG | Gas Boiler Repair": "202339087594"}
made = {"budgets": {}, "campaigns": {}, "ad_groups": dict(EXIST_AG), "snippets": {}}
if (LIVE / f"AMB-0922-TRANSITION-{STAMP}-A.json").exists() and args.stage in ("B", "C"):
    prev = json.loads((LIVE / f"AMB-0922-TRANSITION-{STAMP}-A.json").read_text(
        encoding="utf-8"))
    made.update(prev.get("committed", {}))
    print(f"loaded stage A receipt: {len(made.get('campaigns', {}))} campaigns, "
          f"{len(made.get('ad_groups', {}))} ad groups")


STAND_IN_CAMPAIGN = "24257819463"    # real, PAUSED
SCHED_STAND_IN = "20509039406"       # real, PAUSED, carries ZERO ad-schedule rows
STAND_IN_AD_GROUP = "199797580706"   # real, PAUSED


def camp_rn(key):
    if CAMPAIGNS[key]["reuse"]:
        return CS.campaign_path(CID, CAMPAIGNS[key]["reuse"])
    return CS.campaign_path(CID, made["campaigns"].get(key, STAND_IN_CAMPAIGN))


def ag_rn(name):
    return AGS.ad_group_path(CID, made["ad_groups"].get(name, STAND_IN_AD_GROUP))


def camp_id(key):
    return CAMPAIGNS[key]["reuse"] or made["campaigns"][key]


# =========================================================== STAGE A : BUILD
def stage_a():
    print("\n################ STAGE A - CREATE PAUSED ################")

    # A1 budgets ------------------------------------------------------------
    ops = []
    for k in NEWC:
        o = c.get_type("CampaignBudgetOperation"); b = o.create
        b.name = f"Budget | {CAMPAIGNS[k]['name']}"
        b.amount_micros = int(round(CAMPAIGNS[k]["daily"] * 1e6))
        b.explicitly_shared = False
        b.delivery_method = c.enums.BudgetDeliveryMethodEnum.STANDARD
        ops.append(o)
    names = mutate("CampaignBudgetService", "MutateCampaignBudgetsRequest", ops, DRY,
                   "A1 budgets")
    if not DRY:
        for k, n in zip(NEWC, names):
            made["budgets"][k] = rid(n)
        rec["committed"] = made; save("-A")

    # A2 campaigns ----------------------------------------------------------
    for i, k in enumerate(NEWC):
        v = CAMPAIGNS[k]
        o = c.get_type("CampaignOperation"); x = o.create
        x.name = v["name"]
        x.status = c.enums.CampaignStatusEnum.PAUSED
        x.advertising_channel_type = c.enums.AdvertisingChannelTypeEnum.SEARCH
        x.campaign_budget = CBS.campaign_budget_path(
            CID, made["budgets"].get(k, "15044731597"))
        x.target_spend.cpc_bid_ceiling_micros = int(round(v["ceiling"] * 1e6))
        x.network_settings.target_google_search = True
        x.network_settings.target_search_network = False
        x.network_settings.target_content_network = False
        x.network_settings.target_partner_search_network = False
        x.geo_target_type_setting.positive_geo_target_type = \
            c.enums.PositiveGeoTargetTypeEnum.PRESENCE
        x.geo_target_type_setting.negative_geo_target_type = \
            c.enums.NegativeGeoTargetTypeEnum.PRESENCE
        x.contains_eu_political_advertising = (
            c.enums.EuPoliticalAdvertisingStatusEnum
            .DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING)
        n = mutate("CampaignService", "MutateCampaignsRequest", [o], DRY,
                   f"A2 campaign {k}")
        if not DRY:
            made["campaigns"][k] = rid(n[0])
            rec["committed"] = made; save("-A")

    # A3 locations on the new campaigns -------------------------------------
    ops = []
    for k in NEWC:
        for g in GEO:
            o = c.get_type("CampaignCriterionOperation"); x = o.create
            x.campaign = camp_rn(k)
            x.location.geo_target_constant = f"geoTargetConstants/{g}"
            ops.append(o)
    mutate("CampaignCriterionService", "MutateCampaignCriteriaRequest", ops, DRY,
           f"A3 locations ({len(ops)})")

    # A4 ad schedule: remove the old rows on reused campaigns, add 5 new rows
    old = []
    for r in q(c, """SELECT campaign.id, campaign_criterion.resource_name
                     FROM campaign_criterion
                     WHERE campaign_criterion.type = 'AD_SCHEDULE'
                       AND campaign.id IN (24257819463, 24257819466, 24132507744)"""):
        old.append(r.campaign_criterion.resource_name)
    if old:
        ops = []
        for rn in old:
            o = c.get_type("CampaignCriterionOperation"); o.remove = rn
            ops.append(o)
        mutate("CampaignCriterionService", "MutateCampaignCriteriaRequest", ops, DRY,
               f"A4a remove old schedule rows ({len(ops)})")
    ops = []
    # Under --preflight A4a was validate_only, so the OLD Mon-Fri 08:00-20:00 rows are
    # still on the three reused campaigns and any new row overlaps them. That is an
    # ordering artefact of the probe, not a payload defect: in execution A4a removes them
    # first. Probe the four NEW campaigns only, which carry no rows yet.
    sched_targets = NEWC[:1] if DRY else list(CAMPAIGNS)
    for k in sched_targets:
        for s in SCHEDULE:
            o = c.get_type("CampaignCriterionOperation"); x = o.create
            x.campaign = (CS.campaign_path(CID, SCHED_STAND_IN) if DRY
                          else camp_rn(k))
            x.ad_schedule.day_of_week = getattr(c.enums.DayOfWeekEnum, DAY[s["day"]])
            x.ad_schedule.start_hour = s["start_hour"]
            x.ad_schedule.start_minute = c.enums.MinuteOfHourEnum.ZERO
            x.ad_schedule.end_hour = s["end_hour"]
            x.ad_schedule.end_minute = c.enums.MinuteOfHourEnum.ZERO
            ops.append(o)
    mutate("CampaignCriterionService", "MutateCampaignCriteriaRequest", ops, DRY,
           f"A4b add Mon-Fri 08:00-16:00 ({len(ops)})")

    # A5 rename reused campaigns -------------------------------------------
    ops = []
    for v in CAMPAIGNS.values():
        if v["reuse"] and v.get("rename_to"):
            o = c.get_type("CampaignOperation")
            o.update.resource_name = CS.campaign_path(CID, v["reuse"])
            o.update.name = v["rename_to"]
            o.update_mask.paths.append("name")
            ops.append(o)
    mutate("CampaignService", "MutateCampaignsRequest", ops, DRY,
           f"A5 rename campaigns ({len(ops)})")

    # A6 rename the reused ad group + A7 remove the moved keywords ----------
    ops = []
    for n, d in AG.items():
        if d.get("rename_from"):
            o = c.get_type("AdGroupOperation")
            o.update.resource_name = AGS.ad_group_path(CID, d["existing_ad_group_id"])
            o.update.name = n
            o.update_mask.paths.append("name")
            ops.append(o)
    if ops:
        mutate("AdGroupService", "MutateAdGroupsRequest", ops, DRY,
               f"A6 rename ad group ({len(ops)})")

    rm_targets = {(k["text"].lower(), k["match_type"])
                  for o in build["operations"]
                  if o["op"] == "REMOVE_KEYWORDS_FROM_EXISTING_AD_GROUP"
                  for k in o["keywords"]}
    ops = []
    for r in q(c, """SELECT ad_group_criterion.resource_name,
                     ad_group_criterion.keyword.text,
                     ad_group_criterion.keyword.match_type
                     FROM ad_group_criterion
                     WHERE ad_group.id = 199797580706
                       AND ad_group_criterion.type = 'KEYWORD'
                       AND ad_group_criterion.negative = FALSE
                       AND ad_group_criterion.status != 'REMOVED'"""):
        x = r.ad_group_criterion
        if (x.keyword.text.lower(), E(x.keyword.match_type)) in rm_targets:
            o = c.get_type("AdGroupCriterionOperation"); o.remove = x.resource_name
            ops.append(o)
    if ops:
        mutate("AdGroupCriterionService", "MutateAdGroupCriteriaRequest", ops, DRY,
               f"A7 remove moved keywords ({len(ops)})")

    # A8 ad groups ----------------------------------------------------------
    new_ag = [(n, d) for n, d in AG.items() if not d["existing_ad_group_id"]]
    ops = []
    for n, d in new_ag:
        o = c.get_type("AdGroupOperation"); x = o.create
        x.name = n
        x.campaign = camp_rn(d["campaign_key"])
        x.status = c.enums.AdGroupStatusEnum.PAUSED
        x.type_ = c.enums.AdGroupTypeEnum.SEARCH_STANDARD
        x.cpc_bid_micros = int(round(d["cpc_bid"] * 1e6))
        ops.append(o)
    names = mutate("AdGroupService", "MutateAdGroupsRequest", ops, DRY,
                   f"A8 ad groups ({len(ops)})")
    if not DRY:
        for (n, _), rn in zip(new_ag, names):
            made["ad_groups"][n] = rid(rn)
        rec["committed"] = made; save("-A")

    # A9 keywords -----------------------------------------------------------
    ops = []
    for n, d in AG.items():
        if not (d["phrase"] or d["exact"]):
            continue
        agrn = ag_rn(n)
        for t in d["phrase"]:
            o = c.get_type("AdGroupCriterionOperation"); x = o.create
            x.ad_group = agrn; x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
            x.keyword.text = t; x.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
            ops.append(o)
        for t in d["exact"]:
            o = c.get_type("AdGroupCriterionOperation"); x = o.create
            x.ad_group = agrn; x.status = c.enums.AdGroupCriterionStatusEnum.PAUSED
            x.keyword.text = t; x.keyword.match_type = c.enums.KeywordMatchTypeEnum.EXACT
            ops.append(o)
    if DRY:
        # Everything lands on ONE stand-in ad group under preflight, so keywords the
        # stand-in already owns report a duplicate that cannot occur in execution.
        have = {(r.ad_group_criterion.keyword.text.lower(),
                 E(r.ad_group_criterion.keyword.match_type))
                for r in q(c, f"""SELECT ad_group_criterion.keyword.text,
                                  ad_group_criterion.keyword.match_type
                                  FROM ad_group_criterion
                                  WHERE ad_group.id = {STAND_IN_AD_GROUP}
                                    AND ad_group_criterion.type = 'KEYWORD'
                                    AND ad_group_criterion.negative = FALSE
                                    AND ad_group_criterion.status != 'REMOVED'""")}
        before = len(ops)
        ops = [o for o in ops
               if (o.create.keyword.text.lower(),
                   E(o.create.keyword.match_type)) not in have]
        if before != len(ops):
            print(f"    A9 preflight: excluded {before - len(ops)} keyword(s) the "
                  f"stand-in ad group already owns")
    mutate("AdGroupCriterionService", "MutateAdGroupCriteriaRequest", ops, DRY,
           f"A9 keywords ({len(ops)})")

    # A10 RSAs, READY ad groups only ---------------------------------------
    ops = []
    for n, d in AG.items():
        if d["verdict"] != "READY" or not d["rsas"]:
            continue
        agrn = ag_rn(n)
        for rs in d["rsas"]:
            o = c.get_type("AdGroupAdOperation"); a = o.create
            a.ad_group = agrn; a.status = c.enums.AdGroupAdStatusEnum.PAUSED
            a.ad.final_urls.append(d["url"])
            rr = a.ad.responsive_search_ad
            for h in rs["h"]:
                t = c.get_type("AdTextAsset"); t.text = h; rr.headlines.append(t)
            for x in rs["d"]:
                t = c.get_type("AdTextAsset"); t.text = x; rr.descriptions.append(t)
            ops.append(o)
    mutate("AdGroupAdService", "MutateAdGroupAdsRequest", ops, DRY,
           f"A10 RSAs ({len(ops)})")

    # A11 cross-negatives ---------------------------------------------------
    ops = []
    for n, negs in XNEG.items():
        agrn = ag_rn(n)
        for t in negs:
            o = c.get_type("AdGroupCriterionOperation"); x = o.create
            x.ad_group = agrn; x.negative = True
            x.keyword.text = t; x.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
            ops.append(o)
    mutate("AdGroupCriterionService", "MutateAdGroupCriteriaRequest", ops, DRY,
           f"A11 cross-negatives ({len(ops)})")

    # A12 structured snippets, then A13 all campaign asset links ------------
    sn = [o for o in build["operations"]
          if o["op"] == "CREATE_STRUCTURED_SNIPPET_AND_LINK"]
    ops = []
    for o_ in sn:
        o = c.get_type("AssetOperation"); a = o.create
        a.structured_snippet_asset.header = o_["header"]
        a.structured_snippet_asset.values.extend(o_["values"])
        ops.append(o)
    names = mutate("AssetService", "MutateAssetsRequest", ops, DRY,
                   f"A12 structured snippets ({len(ops)})")
    if not DRY:
        for o_, rn in zip(sn, names):
            made["snippets"][o_["campaign_key"]] = rid(rn)
        rec["committed"] = made; save("-A")

    CALLOUTS = ["422477374526", "422577760603", "422577771364",
                "422577777430", "422577777442"]
    SITELINKS = ["422577777457", "422577771382", "422477374559"]
    AS = c.get_service("AssetService")
    ops = []
    # The default stand-in already carries every one of these assets, so re-linking them
    # returns RESOURCE_ALREADY_EXISTS. Probe against a campaign with NO asset links.
    asset_targets = NEWC[:1] if DRY else NEWC
    for k in asset_targets:
        for aid, ft in ([("407995613637", "CALL"), ("80516971145", "BUSINESS_NAME")]
                        + [(a, "CALLOUT") for a in CALLOUTS]
                        + [(a, "SITELINK") for a in SITELINKS]
                        + ([(made["snippets"][k], "STRUCTURED_SNIPPET")]
                           if not DRY and k in made["snippets"] else [])):
            o = c.get_type("CampaignAssetOperation"); x = o.create
            x.campaign = (CS.campaign_path(CID, SCHED_STAND_IN) if DRY else camp_rn(k))
            x.asset = AS.asset_path(CID, aid)
            x.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
            ops.append(o)
    mutate("CampaignAssetService", "MutateCampaignAssetsRequest", ops, DRY,
           f"A13 campaign asset links ({len(ops)})")

    # A14 call-asset schedule ----------------------------------------------
    o = c.get_type("AssetOperation")
    o.update.resource_name = AS.asset_path(CID, "407995613637")
    ca = o.update.call_asset
    ca.phone_number = "(410)705-6354"
    ca.country_code = "US"
    for s in SCHEDULE:
        t = c.get_type("AdScheduleInfo")
        t.day_of_week = getattr(c.enums.DayOfWeekEnum, DAY[s["day"]])
        t.start_hour = s["start_hour"]
        t.start_minute = c.enums.MinuteOfHourEnum.ZERO
        t.end_hour = s["end_hour"]
        t.end_minute = c.enums.MinuteOfHourEnum.ZERO
        ca.ad_schedule_targets.append(t)
    o.update_mask.paths.append("call_asset.ad_schedule_targets")
    mutate("AssetService", "MutateAssetsRequest", [o], DRY, "A14 call-asset schedule")

    rec["stages"].append({"stage": "A", "when": datetime.datetime.now(TZ).isoformat(),
                          "dry": DRY})
    if not DRY:
        rec["committed"] = made
        save("-A")


# ================================================== STAGE B : PAUSE + BUDGET
def stage_b():
    print("\n########## STAGE B - PAUSE COOLING, THEN REALLOCATE ##########")
    inv = coolb["inventory"]

    ops = []
    for cid_, v in inv.items():
        if v["level"] == "CAMPAIGN":
            o = c.get_type("CampaignOperation")
            o.update.resource_name = CS.campaign_path(CID, cid_)
            o.update.status = c.enums.CampaignStatusEnum.PAUSED
            o.update_mask.paths.append("status")
            ops.append(o)
    mutate("CampaignService", "MutateCampaignsRequest", ops, DRY,
           f"B1 pause cooling campaigns ({len(ops)})")

    ops = []
    for cid_, v in inv.items():
        if v["level"] == "AD_GROUP":
            for agid in v["ad_groups"]:
                o = c.get_type("AdGroupOperation")
                o.update.resource_name = AGS.ad_group_path(CID, agid)
                o.update.status = c.enums.AdGroupStatusEnum.PAUSED
                o.update_mask.paths.append("status")
                ops.append(o)
    mutate("AdGroupService", "MutateAdGroupsRequest", ops, DRY,
           f"B2 pause residential cooling ad group ({len(ops)})")

    ops = []
    for o_ in coolb["operations"]:
        if o_["op"] != "UPDATE_CAMPAIGN_BUDGET_AMOUNT":
            continue
        o = c.get_type("CampaignBudgetOperation")
        o.update.resource_name = CBS.campaign_budget_path(CID, o_["budget_id"])
        o.update.amount_micros = int(round(o_["to_usd"] * 1e6))
        o.update_mask.paths.append("amount_micros")
        ops.append(o)
    mutate("CampaignBudgetService", "MutateCampaignBudgetsRequest", ops, DRY,
           f"B3 budgets ({len(ops)})")

    ops = []
    for o_ in coolb["operations"]:
        if o_["op"] != "UPDATE_CAMPAIGN_CPC_BID_CEILING":
            continue
        o = c.get_type("CampaignOperation")
        o.update.resource_name = CS.campaign_path(CID, o_["campaign_id"])
        o.update.target_spend.cpc_bid_ceiling_micros = int(round(o_["to_usd"] * 1e6))
        o.update_mask.paths.append("target_spend.cpc_bid_ceiling_micros")
        ops.append(o)
    mutate("CampaignService", "MutateCampaignsRequest", ops, DRY,
           f"B4 CPC ceilings ({len(ops)})")

    rec["stages"].append({"stage": "B", "when": datetime.datetime.now(TZ).isoformat(),
                          "dry": DRY})
    if not DRY:
        save("-B")


# ============================================================ STAGE C : ENABLE
def stage_c():
    print("\n################ STAGE C - ENABLE READY SERVICES ################")
    ready = [n for n, d in AG.items() if d["verdict"] == "READY"]
    ready_ids = {made["ad_groups"].get(n, STAND_IN_AD_GROUP) for n in ready}

    ops = []
    for k, v in CAMPAIGNS.items():
        if not v["enable"]:
            continue
        o = c.get_type("CampaignOperation")
        o.update.resource_name = camp_rn(k)
        o.update.status = c.enums.CampaignStatusEnum.ENABLED
        o.update_mask.paths.append("status")
        ops.append(o)
    mutate("CampaignService", "MutateCampaignsRequest", ops, DRY,
           f"C1 enable campaigns ({len(ops)})")

    ops = []
    for n in ready:
        o = c.get_type("AdGroupOperation")
        o.update.resource_name = ag_rn(n)
        o.update.status = c.enums.AdGroupStatusEnum.ENABLED
        o.update_mask.paths.append("status")
        ops.append(o)
    mutate("AdGroupService", "MutateAdGroupsRequest", ops, DRY,
           f"C2 enable ad groups ({len(ops)})")

    # Enable every PAUSED positive keyword on a READY ad group, including the ones
    # that already existed on the three reused ad groups.
    ops = []
    ids = ",".join(sorted(ready_ids))
    for r in q(c, f"""SELECT ad_group.id, ad_group_criterion.resource_name,
                      ad_group_criterion.status
                      FROM ad_group_criterion
                      WHERE ad_group.id IN ({ids})
                        AND ad_group_criterion.type = 'KEYWORD'
                        AND ad_group_criterion.negative = FALSE
                        AND ad_group_criterion.status = 'PAUSED'"""):
        o = c.get_type("AdGroupCriterionOperation")
        o.update.resource_name = r.ad_group_criterion.resource_name
        o.update.status = c.enums.AdGroupCriterionStatusEnum.ENABLED
        o.update_mask.paths.append("status")
        ops.append(o)
    if ops:
        mutate("AdGroupCriterionService", "MutateAdGroupCriteriaRequest", ops, DRY,
               f"C3 enable keywords ({len(ops)})")

    # Enable every PAUSED ad on a READY ad group, EXCEPT ones already disapproved.
    ops, skipped = [], []
    for r in q(c, f"""SELECT ad_group.id, ad_group.name, ad_group_ad.resource_name,
                      ad_group_ad.ad.id, ad_group_ad.status,
                      ad_group_ad.policy_summary.approval_status
                      FROM ad_group_ad
                      WHERE ad_group.id IN ({ids})
                        AND ad_group_ad.status = 'PAUSED'"""):
        if E(r.ad_group_ad.policy_summary.approval_status) == "DISAPPROVED":
            skipped.append({"ad_id": str(r.ad_group_ad.ad.id),
                            "ad_group": r.ad_group.name,
                            "why": "DISAPPROVED - not enabled"})
            continue
        o = c.get_type("AdGroupAdOperation")
        o.update.resource_name = r.ad_group_ad.resource_name
        o.update.status = c.enums.AdGroupAdStatusEnum.ENABLED
        o.update_mask.paths.append("status")
        ops.append(o)
    rec["ads_not_enabled_because_disapproved"] = skipped
    if skipped:
        print(f"    C4 skipping {len(skipped)} DISAPPROVED ad(s)")
    if ops:
        mutate("AdGroupAdService", "MutateAdGroupAdsRequest", ops, DRY,
               f"C4 enable ads ({len(ops)})")

    rec["stages"].append({"stage": "C", "when": datetime.datetime.now(TZ).isoformat(),
                          "dry": DRY})
    if not DRY:
        save("-C")


if DRY:
    stage_a(); stage_b(); stage_c()
    save("-PREFLIGHT")
    fails = rec.get("preflight_failures", [])
    print(f"\n=== PREFLIGHT: {len(fails)} failures ===")
    for f in fails:
        print(f"   {f}")
    print("EXTERNAL WRITES: 0")
else:
    {"A": stage_a, "B": stage_b, "C": stage_c}[args.stage]()
    print(f"\nSTAGE {args.stage} COMMITTED")
    print(json.dumps(made, indent=1)[:2000])
