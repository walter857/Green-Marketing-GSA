#!/usr/bin/env python3
"""Ambient | 2026-10-07 | READ-ONLY configuration snapshot for the tracking-repair / qualified-lead audit.

No mutations. Writes snapshots/snapshot-2026-10-07.json and prints aggregates only.
Covers: identity gate + work-order validation; all non-removed campaigns (config, bidding, networks,
AI Max, PMax automation opt-outs, budgets); campaign criteria (schedule, devices, locations, languages,
negatives, audiences, demographics, brand lists); ad groups; ads with policy; keywords with QS;
campaign / ad-group / customer assets with policy and primary status; PMax asset groups, assets and
signals; shared sets and members; conversion actions; customer / campaign conversion goals; custom goals
and goal-config; user lists; change_event and change_status since 2026-10-02.
"""
from __future__ import annotations

import collections
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, CLIENT_DIR  # noqa: E402
from gm_gsa.work_orders import validate_work_order  # noqa: E402
import yaml  # noqa: E402

LIVE10 = ["24257819463", "24257819466", "24132507744", "24268690038", "24268690041",
          "24279798229", "24274160783", "24132507747", "24295088845", "24318905515"]
LIVE = ",".join(LIVE10)
NOW = datetime.datetime.now(TZ)
WO = "work-order-tracking-repairs-qualified-leads-2026-10-07.yaml"
money = lambda v: round(v / 1e6, 2)

cl = yaml.safe_load((CLIENT_DIR / "client.yaml").read_text(encoding="utf-8"))
err = validate_work_order(yaml.safe_load((CLIENT_DIR / "work-orders" / WO).read_text(encoding="utf-8")), cl)
print(f"work order {WO}: {'VALID' if not err else err}")
if err:
    sys.exit("HARD STOP: work order invalid")
c = client()
ident = identity_gate(c, verbose=True)
out = {"read_local": NOW.isoformat(timespec="seconds"), "identity": {k: v for k, v in ident.items() if k != "checks"},
       "identity_checks": ident["checks"]}


def safe(label, fn):
    try:
        return fn()
    except Exception as exc:  # record and continue; a read failure is a gap, not a stop
        msg = str(exc).split("\n")[0][:300]
        print(f"  [READ-GAP] {label}: {msg}")
        out.setdefault("read_gaps", {})[label] = msg
        return None


# ---------------- campaigns ----------------
camps = {}
for r in q(c, """SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status, campaign.primary_status,
        campaign.primary_status_reasons, campaign.advertising_channel_type, campaign.bidding_strategy_type,
        campaign.target_spend.cpc_bid_ceiling_micros, campaign.maximize_conversions.target_cpa_micros,
        campaign.maximize_conversion_value.target_roas, campaign.campaign_budget, campaign.network_settings.target_google_search,
        campaign.network_settings.target_search_network, campaign.network_settings.target_content_network,
        campaign.network_settings.target_partner_search_network,
        campaign.geo_target_type_setting.positive_geo_target_type, campaign.geo_target_type_setting.negative_geo_target_type,
        campaign.ai_max_setting.enable_ai_max, campaign.tracking_url_template,
        campaign.final_url_suffix, campaign.brand_guidelines_enabled,
        campaign.contains_eu_political_advertising, campaign.labels
        FROM campaign WHERE campaign.status != 'REMOVED'"""):
    x = r.campaign
    camps[str(x.id)] = dict(
        name=x.name, status=E(x.status), serving=E(x.serving_status), primary=E(x.primary_status),
        reasons=[E(v) for v in x.primary_status_reasons], channel=E(x.advertising_channel_type),
        bidding=E(x.bidding_strategy_type), ceiling=money(x.target_spend.cpc_bid_ceiling_micros),
        tcpa=money(x.maximize_conversions.target_cpa_micros), budget_rn=x.campaign_budget,
        search=x.network_settings.target_google_search, partners=x.network_settings.target_search_network,
        display=x.network_settings.target_content_network, geo_pos=E(x.geo_target_type_setting.positive_geo_target_type),
        geo_neg=E(x.geo_target_type_setting.negative_geo_target_type), ai_max=x.ai_max_setting.enable_ai_max,
        tracking_template=x.tracking_url_template, final_url_suffix=x.final_url_suffix,
        brand_guidelines=x.brand_guidelines_enabled, live10=str(x.id) in LIVE10)
out["campaigns"] = camps

# PMax / campaign automation opt-outs
auto = collections.defaultdict(dict)
def _auto():
    for r in q(c, f"""SELECT campaign.id, campaign.asset_automation_settings FROM campaign WHERE campaign.id IN ({LIVE})"""):
        for s in r.campaign.asset_automation_settings:
            auto[str(r.campaign.id)][E(s.asset_automation_type)] = E(s.asset_automation_status)
safe("asset_automation_settings", _auto)
out["asset_automation"] = dict(auto)

# text customization / search automation for Search campaigns (AI Max sub-settings live under ai_max_setting)
budgets = {}
for r in q(c, """SELECT campaign_budget.resource_name, campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
        campaign_budget.period, campaign_budget.delivery_method, campaign_budget.explicitly_shared, campaign_budget.status,
        campaign_budget.reference_count, campaign_budget.total_amount_micros FROM campaign_budget WHERE campaign_budget.status != 'REMOVED'"""):
    b = r.campaign_budget
    budgets[b.resource_name] = dict(id=str(b.id), name=b.name, amount=money(b.amount_micros), period=E(b.period),
                                    delivery=E(b.delivery_method), shared=b.explicitly_shared, refs=b.reference_count,
                                    total=money(b.total_amount_micros))
for cid, x in camps.items():
    x["budget"] = budgets.get(x["budget_rn"], {})
out["budgets"] = budgets

# ---------------- campaign criteria ----------------
crit = collections.defaultdict(lambda: collections.defaultdict(list))
for r in q(c, f"""SELECT campaign.id, campaign_criterion.criterion_id, campaign_criterion.type, campaign_criterion.negative,
        campaign_criterion.status, campaign_criterion.bid_modifier, campaign_criterion.device.type,
        campaign_criterion.ad_schedule.day_of_week, campaign_criterion.ad_schedule.start_hour, campaign_criterion.ad_schedule.start_minute,
        campaign_criterion.ad_schedule.end_hour, campaign_criterion.ad_schedule.end_minute,
        campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, campaign_criterion.location.geo_target_constant,
        campaign_criterion.proximity.radius, campaign_criterion.language.language_constant, campaign_criterion.brand_list.shared_set,
        campaign_criterion.user_list.user_list, campaign_criterion.user_interest.user_interest_category,
        campaign_criterion.custom_audience.custom_audience, campaign_criterion.combined_audience.combined_audience,
        campaign_criterion.age_range.type, campaign_criterion.gender.type, campaign_criterion.income_range.type,
        campaign_criterion.parental_status.type, campaign_criterion.ip_block.ip_address, campaign_criterion.placement.url,
        campaign_criterion.content_label.type, campaign_criterion.webpage.criterion_name
        FROM campaign_criterion WHERE campaign.id IN ({LIVE})"""):
    k = r.campaign_criterion
    t = E(k.type)
    row = dict(id=str(k.criterion_id), neg=k.negative, status=E(k.status))
    if t == "DEVICE":
        row.update(device=E(k.device.type), bid_modifier_set="bid_modifier" in k, bid_modifier=k.bid_modifier)
    elif t == "AD_SCHEDULE":
        a = k.ad_schedule
        row.update(day=E(a.day_of_week), start=a.start_hour, start_min=E(a.start_minute), end=a.end_hour, end_min=E(a.end_minute),
                   bid_modifier=k.bid_modifier)
    elif t == "KEYWORD":
        row.update(text=k.keyword.text, match=E(k.keyword.match_type))
    elif t == "LOCATION":
        row.update(geo=k.location.geo_target_constant, bid_modifier=k.bid_modifier)
    elif t == "PROXIMITY":
        row.update(radius=k.proximity.radius)
    elif t == "LANGUAGE":
        row.update(lang=k.language.language_constant)
    elif t == "BRAND_LIST":
        row.update(shared_set=k.brand_list.shared_set)
    elif t == "USER_LIST":
        row.update(user_list=k.user_list.user_list, bid_modifier=k.bid_modifier)
    elif t == "USER_INTEREST":
        row.update(user_interest=k.user_interest.user_interest_category, bid_modifier=k.bid_modifier)
    elif t == "CUSTOM_AUDIENCE":
        row.update(custom_audience=k.custom_audience.custom_audience)
    elif t == "COMBINED_AUDIENCE":
        row.update(combined=k.combined_audience.combined_audience)
    elif t in ("AGE_RANGE", "GENDER", "INCOME_RANGE", "PARENTAL_STATUS"):
        row.update(value=E(getattr(k, t.lower()).type), bid_modifier=k.bid_modifier)
    elif t == "IP_BLOCK":
        row.update(ip="<redacted-count-only>")
    elif t == "PLACEMENT":
        row.update(url=k.placement.url)
    elif t == "CONTENT_LABEL":
        row.update(label=E(k.content_label.type))
    elif t == "WEBPAGE":
        row.update(name=k.webpage.criterion_name)
    crit[str(r.campaign.id)][t].append(row)
out["campaign_criteria"] = {cid: dict(v) for cid, v in crit.items()}

# targeting setting (observation vs targeting) for Search campaigns
tset = {}
def _tset():
    for r in q(c, f"SELECT campaign.id, campaign.targeting_setting.target_restrictions FROM campaign WHERE campaign.id IN ({LIVE})"):
        tset[str(r.campaign.id)] = [dict(dim=E(t.targeting_dimension), bid_only=t.bid_only) for t in r.campaign.targeting_setting.target_restrictions]
safe("campaign_targeting_setting", _tset)
out["campaign_targeting_setting"] = tset

# ---------------- ad groups ----------------
labels = {r.label.resource_name: r.label.name for r in q(c, "SELECT label.resource_name, label.name FROM label")}
ags = {}
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group.primary_status,
        ad_group.primary_status_reasons, ad_group.labels, ad_group.type, ad_group.targeting_setting.target_restrictions
        FROM ad_group WHERE campaign.id IN ({LIVE}) AND ad_group.status != 'REMOVED'"""):
    g = r.ad_group
    ags[str(g.id)] = dict(campaign=str(r.campaign.id), name=g.name, status=E(g.status), primary=E(g.primary_status),
                          reasons=[E(v) for v in g.primary_status_reasons], labels=[labels.get(l, l) for l in g.labels],
                          type=E(g.type), targeting=[dict(dim=E(t.targeting_dimension), bid_only=t.bid_only) for t in g.targeting_setting.target_restrictions])
out["ad_groups"] = ags

# ad-group criteria (audiences, demographics, negatives, keywords)
agc = collections.defaultdict(lambda: collections.defaultdict(list))
kws = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.type, ad_group_criterion.negative,
        ad_group_criterion.status, ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons,
        ad_group_criterion.system_serving_status, ad_group_criterion.approval_status,
        ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.quality_info.quality_score,
        ad_group_criterion.quality_info.creative_quality_score, ad_group_criterion.quality_info.post_click_quality_score,
        ad_group_criterion.quality_info.search_predicted_ctr, ad_group_criterion.bid_modifier,
        ad_group_criterion.user_list.user_list, ad_group_criterion.user_interest.user_interest_category,
        ad_group_criterion.custom_audience.custom_audience, ad_group_criterion.age_range.type, ad_group_criterion.gender.type,
        ad_group_criterion.income_range.type, ad_group_criterion.parental_status.type, ad_group_criterion.final_urls
        FROM ad_group_criterion WHERE campaign.id IN ({LIVE}) AND ad_group_criterion.status != 'REMOVED'"""):
    k = r.ad_group_criterion
    t = E(k.type)
    if t == "KEYWORD":
        kws.append(dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), id=str(k.criterion_id), text=k.keyword.text,
                        match=E(k.keyword.match_type), neg=k.negative, status=E(k.status), primary=E(k.primary_status),
                        reasons=[E(v) for v in k.primary_status_reasons], serving=E(k.system_serving_status),
                        approval=E(k.approval_status), qs=k.quality_info.quality_score,
                        ad_rel=E(k.quality_info.creative_quality_score), lp=E(k.quality_info.post_click_quality_score),
                        ectr=E(k.quality_info.search_predicted_ctr), final_urls=list(k.final_urls)))
    else:
        row = dict(id=str(k.criterion_id), neg=k.negative, status=E(k.status), bid_modifier=k.bid_modifier)
        if t == "USER_LIST":
            row.update(user_list=k.user_list.user_list)
        elif t == "USER_INTEREST":
            row.update(user_interest=k.user_interest.user_interest_category)
        elif t == "CUSTOM_AUDIENCE":
            row.update(custom_audience=k.custom_audience.custom_audience)
        elif t in ("AGE_RANGE", "GENDER", "INCOME_RANGE", "PARENTAL_STATUS"):
            row.update(value=E(getattr(k, t.lower()).type))
        agc[str(r.ad_group.id)][t].append(row)
out["keywords"] = kws
out["ad_group_criteria_non_keyword"] = {g: dict(v) for g, v in agc.items()}

# ---------------- ads + policy ----------------
ads = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.ad.name, ad_group_ad.status, ad_group_ad.primary_status,
        ad_group_ad.primary_status_reasons, ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status,
        ad_group_ad.policy_summary.policy_topic_entries, ad_group_ad.ad.final_urls, ad_group_ad.ad.type, ad_group_ad.ad_strength,
        ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.ad.responsive_search_ad.descriptions
        FROM ad_group_ad WHERE campaign.id IN ({LIVE}) AND ad_group_ad.status != 'REMOVED'"""):
    a = r.ad_group_ad
    topics = []
    for t in a.policy_summary.policy_topic_entries:
        cons = []
        for con in t.constraints:
            if con.country_constraint_list.countries:
                cons.append("country")
            if con.reseller_constraint:
                cons.append("reseller")
            if con.certificate_missing_in_country_list.countries:
                cons.append("cert")
        topics.append(dict(topic=t.topic, type=E(t.type), constraints=cons))
    ads.append(dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), id=str(a.ad.id), status=E(a.status),
                    primary=E(a.primary_status), reasons=[E(v) for v in a.primary_status_reasons],
                    approval=E(a.policy_summary.approval_status), review=E(a.policy_summary.review_status), topics=topics,
                    final_urls=list(a.ad.final_urls), type=E(a.ad.type), strength=E(a.ad_strength),
                    headlines=[h.text for h in a.ad.responsive_search_ad.headlines],
                    descriptions=[d.text for d in a.ad.responsive_search_ad.descriptions]))
out["ads"] = ads

# ---------------- assets (campaign / ad group / customer) ----------------
def asset_rows(level, frm, where):
    rows = []
    sel_parent = "campaign.id, " if level != "customer" else ""
    sel_ag = "ad_group.id, " if level == "ad_group" else ""
    for r in q(c, f"""SELECT {sel_parent}{sel_ag}{frm}.field_type, {frm}.status, {frm}.primary_status, {frm}.primary_status_reasons,
            asset.policy_summary.approval_status, asset.policy_summary.review_status, asset.policy_summary.policy_topic_entries,
            asset.id, asset.type, asset.final_urls, asset.sitelink_asset.link_text, asset.callout_asset.callout_text,
            asset.call_asset.phone_number, asset.call_asset.country_code, asset.call_asset.call_conversion_reporting_state,
            asset.call_asset.call_conversion_action, asset.call_asset.ad_schedule_targets,
            asset.structured_snippet_asset.header, asset.location_asset.place_id
            FROM {frm} WHERE {where}"""):
        x = getattr(r, frm)
        a = r.asset
        row = dict(level=level, field=E(x.field_type), status=E(x.status), primary=E(x.primary_status),
                   reasons=[E(v) for v in x.primary_status_reasons], approval=E(r.asset.policy_summary.approval_status),
                   review=E(r.asset.policy_summary.review_status),
                   topics=[dict(topic=t.topic, type=E(t.type)) for t in r.asset.policy_summary.policy_topic_entries],
                   asset=str(a.id), asset_type=E(a.type), final_urls=list(a.final_urls))
        if level != "customer":
            row["campaign"] = str(r.campaign.id)
        if level == "ad_group":
            row["ad_group"] = str(r.ad_group.id)
        if a.sitelink_asset.link_text:
            row["text"] = a.sitelink_asset.link_text
        if a.callout_asset.callout_text:
            row["text"] = a.callout_asset.callout_text
        if a.call_asset.phone_number:
            row.update(phone=a.call_asset.phone_number, call_reporting=E(a.call_asset.call_conversion_reporting_state),
                       call_conv_action=a.call_asset.call_conversion_action,
                       call_schedule=[(E(s.day_of_week), s.start_hour, s.end_hour) for s in a.call_asset.ad_schedule_targets])
        if a.structured_snippet_asset.header:
            row["text"] = a.structured_snippet_asset.header
        rows.append(row)
    return rows

out["campaign_assets"] = safe("campaign_asset", lambda: asset_rows("campaign", "campaign_asset", f"campaign.id IN ({LIVE}) AND campaign_asset.status != 'REMOVED'")) or []
out["ad_group_assets"] = safe("ad_group_asset", lambda: asset_rows("ad_group", "ad_group_asset", f"campaign.id IN ({LIVE}) AND ad_group_asset.status != 'REMOVED'")) or []
out["customer_assets"] = safe("customer_asset", lambda: asset_rows("customer", "customer_asset", "customer_asset.status != 'REMOVED'")) or []

# asset sets (location / business profile) and their campaign links
def _asset_sets():
    sets = [dict(id=str(r.asset_set.id), name=r.asset_set.name, type=E(r.asset_set.type), status=E(r.asset_set.status))
            for r in q(c, "SELECT asset_set.id, asset_set.name, asset_set.type, asset_set.status FROM asset_set WHERE asset_set.status != 'REMOVED'")]
    links = [dict(campaign=str(r.campaign.id), asset_set=r.campaign_asset_set.asset_set, status=E(r.campaign_asset_set.status))
             for r in q(c, f"SELECT campaign.id, campaign_asset_set.asset_set, campaign_asset_set.status FROM campaign_asset_set WHERE campaign.id IN ({LIVE})")]
    cust = [dict(asset_set=r.customer_asset_set.asset_set, status=E(r.customer_asset_set.status))
            for r in q(c, "SELECT customer_asset_set.asset_set, customer_asset_set.status FROM customer_asset_set")]
    return dict(sets=sets, campaign_links=links, customer_links=cust)
out["asset_sets"] = safe("asset_sets", _asset_sets)

# ---------------- PMax asset groups ----------------
agrp = {}
for r in q(c, f"""SELECT campaign.id, asset_group.id, asset_group.name, asset_group.status, asset_group.primary_status,
        asset_group.primary_status_reasons, asset_group.final_urls, asset_group.final_mobile_urls, asset_group.ad_strength,
        asset_group.path1, asset_group.path2 FROM asset_group WHERE campaign.id IN ({LIVE}) AND asset_group.status != 'REMOVED'"""):
    g = r.asset_group
    agrp[str(g.id)] = dict(campaign=str(r.campaign.id), name=g.name, status=E(g.status), primary=E(g.primary_status),
                           reasons=[E(v) for v in g.primary_status_reasons], final_urls=list(g.final_urls), strength=E(g.ad_strength),
                           assets=collections.Counter(), asset_status=collections.Counter(), asset_policy=collections.Counter(),
                           signals=dict(search_themes=[], audiences=[]))
def _aga():
    for r in q(c, f"""SELECT asset_group.id, asset_group_asset.field_type, asset_group_asset.status, asset_group_asset.primary_status,
            asset_group_asset.policy_summary.approval_status, asset_group_asset.policy_summary.review_status,
            asset_group_asset.policy_summary.policy_topic_entries, asset.id, asset.type
            FROM asset_group_asset WHERE campaign.id IN ({LIVE}) AND asset_group_asset.status != 'REMOVED'"""):
        g = agrp.get(str(r.asset_group.id))
        if g is None:
            continue
        x = r.asset_group_asset
        g["assets"][E(x.field_type)] += 1
        g["asset_status"][f"{E(x.status)}/{E(x.primary_status)}"] += 1
        g["asset_policy"][f"{E(x.policy_summary.approval_status)}/{E(x.policy_summary.review_status)}"] += 1
        for t in x.policy_summary.policy_topic_entries:
            g.setdefault("asset_topics", collections.Counter())[f"{t.topic}:{E(t.type)}"] += 1
safe("asset_group_asset", _aga)
def _sig():
    for r in q(c, f"""SELECT asset_group.id, asset_group_signal.search_theme.text, asset_group_signal.audience.audience,
            asset_group_signal.approval_status, asset_group_signal.disapproval_reasons
            FROM asset_group_signal WHERE campaign.id IN ({LIVE})"""):
        g = agrp.get(str(r.asset_group.id))
        if g is None:
            continue
        s = r.asset_group_signal
        if s.search_theme.text:
            g["signals"]["search_themes"].append(dict(text=s.search_theme.text, approval=E(s.approval_status),
                                                      disapproval=[E(d) for d in s.disapproval_reasons]))
        if s.audience.audience:
            g["signals"]["audiences"].append(s.audience.audience)
safe("asset_group_signal", _sig)
def _lg():
    rows = []
    for r in q(c, f"""SELECT asset_group.id, asset_group_listing_group_filter.type FROM asset_group_listing_group_filter WHERE campaign.id IN ({LIVE})"""):
        rows.append(str(r.asset_group.id))
    return collections.Counter(rows)
out["asset_group_listing_filters"] = safe("listing_group_filter", _lg)
for g in agrp.values():
    for k in ("assets", "asset_status", "asset_policy"):
        g[k] = dict(g[k])
    if "asset_topics" in g:
        g["asset_topics"] = dict(g["asset_topics"])
out["asset_groups"] = agrp

# audiences (PMax signals resource)
def _aud():
    rows = {}
    for r in q(c, "SELECT audience.resource_name, audience.id, audience.name, audience.status, audience.description, audience.dimensions, audience.exclusion_dimension FROM audience"):
        a = r.audience
        dims = []
        for d in a.dimensions:
            if d.audience_segments.segments:
                for s in d.audience_segments.segments:
                    if s.user_list.user_list:
                        dims.append(("user_list", s.user_list.user_list))
                    if s.user_interest.user_interest_category:
                        dims.append(("user_interest", s.user_interest.user_interest_category))
                    if s.life_event.life_event:
                        dims.append(("life_event", s.life_event.life_event))
                    if s.detailed_demographic.detailed_demographic:
                        dims.append(("detailed_demographic", s.detailed_demographic.detailed_demographic))
                    if s.custom_audience.custom_audience:
                        dims.append(("custom_audience", s.custom_audience.custom_audience))
            if d.age.age_ranges:
                dims.append(("age", [E(x.min_age) + "-" + E(x.max_age) for x in d.age.age_ranges]))
            if d.gender.genders:
                dims.append(("gender", [E(x) for x in d.gender.genders]))
            if d.household_income.income_ranges:
                dims.append(("income", [E(x) for x in d.household_income.income_ranges]))
            if d.parental_status.parental_statuses:
                dims.append(("parental", [E(x) for x in d.parental_status.parental_statuses]))
        excl = []
        for s in a.exclusion_dimension.exclusions:
            if s.user_list.user_list:
                excl.append(("user_list", s.user_list.user_list))
        rows[a.resource_name] = dict(id=str(a.id), name=a.name, status=E(a.status), description=a.description, dims=dims, exclusions=excl)
    return rows
out["audiences"] = safe("audience", _aud)

def _ca():
    rows = {}
    for r in q(c, "SELECT custom_audience.resource_name, custom_audience.id, custom_audience.name, custom_audience.status, custom_audience.type, custom_audience.members FROM custom_audience"):
        a = r.custom_audience
        rows[a.resource_name] = dict(id=str(a.id), name=a.name, status=E(a.status), type=E(a.type),
                                     members=[(E(m.member_type), m.keyword or m.url or m.app or str(m.place_category)) for m in a.members])
    return rows
out["custom_audiences"] = safe("custom_audience", _ca)

def _ul():
    rows = {}
    for r in q(c, """SELECT user_list.resource_name, user_list.id, user_list.name, user_list.type, user_list.membership_status,
            user_list.size_for_search, user_list.size_for_display, user_list.size_range_for_search, user_list.eligible_for_search,
            user_list.eligible_for_display, user_list.membership_life_span, user_list.access_reason, user_list.account_user_list_status,
            user_list.match_rate_percentage, user_list.description, user_list.read_only, user_list.closing_reason
            FROM user_list"""):
        u = r.user_list
        rows[u.resource_name] = dict(id=str(u.id), name=u.name, type=E(u.type), membership=E(u.membership_status),
                                     size_search=u.size_for_search, size_display=u.size_for_display,
                                     size_range_search=E(u.size_range_for_search), eligible_search=u.eligible_for_search,
                                     eligible_display=u.eligible_for_display, life_span=u.membership_life_span,
                                     access=E(u.access_reason), account_status=E(u.account_user_list_status),
                                     match_rate=u.match_rate_percentage, description=u.description, read_only=u.read_only,
                                     closing=E(u.closing_reason))
    return rows
out["user_lists"] = safe("user_list", _ul)

# ---------------- shared sets / negatives ----------------
ss = {str(r.shared_set.id): dict(name=r.shared_set.name, type=E(r.shared_set.type), status=E(r.shared_set.status), members=r.shared_set.member_count)
      for r in q(c, "SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status, shared_set.member_count FROM shared_set WHERE shared_set.status != 'REMOVED'")}
css = [dict(campaign=str(r.campaign.id), shared_set=str(r.shared_set.id), status=E(r.campaign_shared_set.status))
       for r in q(c, f"SELECT campaign.id, shared_set.id, campaign_shared_set.status FROM campaign_shared_set WHERE campaign.id IN ({LIVE})")]
cust_neg = []
def _cn():
    for r in q(c, """SELECT customer_negative_criterion.id, customer_negative_criterion.type, customer_negative_criterion.negative_keyword_list.shared_set,
            customer_negative_criterion.placement.url, customer_negative_criterion.content_label.type,
            customer_negative_criterion.ip_block.ip_address FROM customer_negative_criterion"""):
        x = r.customer_negative_criterion
        cust_neg.append(dict(id=str(x.id), type=E(x.type), shared_set=x.negative_keyword_list.shared_set,
                             placement=x.placement.url, content_label=E(x.content_label.type)))
safe("customer_negative_criterion", _cn)
members = {}
for sid, s in ss.items():
    if s["type"] in ("NEGATIVE_KEYWORDS", "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS", "BRANDS", "NEGATIVE_PLACEMENTS"):
        rows = []
        for r in q(c, f"""SELECT shared_criterion.criterion_id, shared_criterion.type, shared_criterion.keyword.text,
                shared_criterion.keyword.match_type, shared_criterion.brand.entity_id, shared_criterion.brand.display_name,
                shared_criterion.placement.url FROM shared_criterion WHERE shared_set.id = {sid}"""):
            k = r.shared_criterion
            rows.append(dict(id=str(k.criterion_id), type=E(k.type), text=k.keyword.text, match=E(k.keyword.match_type),
                             brand=getattr(k.brand, "display_name", "") if E(k.type) == "BRAND" else "",
                             brand_id=getattr(k.brand, "entity_id", "") if E(k.type) == "BRAND" else "", placement=k.placement.url))
        members[sid] = rows
out["shared_sets"] = ss
out["campaign_shared_sets"] = css
out["customer_negative_criteria"] = cust_neg
out["shared_set_members"] = members

# ---------------- conversions ----------------
convs = []
for r in q(c, """SELECT conversion_action.id, conversion_action.name, conversion_action.type, conversion_action.category,
        conversion_action.status, conversion_action.primary_for_goal, conversion_action.include_in_conversions_metric,
        conversion_action.counting_type, conversion_action.origin, conversion_action.click_through_lookback_window_days,
        conversion_action.view_through_lookback_window_days, conversion_action.attribution_model_settings.attribution_model,
        conversion_action.value_settings.default_value, conversion_action.value_settings.always_use_default_value,
        conversion_action.phone_call_duration_seconds, conversion_action.owner_customer,
        conversion_action.firebase_settings.event_name, conversion_action.google_analytics_4_settings.event_name,
        conversion_action.google_analytics_4_settings.property_name, conversion_action.tag_snippets
        FROM conversion_action WHERE conversion_action.status != 'REMOVED'"""):
    a = r.conversion_action
    labels_ = []
    for t in a.tag_snippets:
        ev = t.event_snippet or ""
        i = ev.find("send_to")
        if i >= 0:
            labels_.append(ev[i:i + 60].split("'")[2] if ev[i:i + 60].count("'") >= 3 else ev[i:i + 60])
    convs.append(dict(id=str(a.id), name=a.name, type=E(a.type), category=E(a.category), status=E(a.status),
                      primary=a.primary_for_goal, include=a.include_in_conversions_metric, counting=E(a.counting_type),
                      origin=E(a.origin), ct_window=a.click_through_lookback_window_days, vt_window=a.view_through_lookback_window_days,
                      attribution=E(a.attribution_model_settings.attribution_model), default_value=a.value_settings.default_value,
                      always_default=a.value_settings.always_use_default_value, call_seconds=a.phone_call_duration_seconds,
                      owner=a.owner_customer, ga4_event=a.google_analytics_4_settings.event_name,
                      ga4_property=a.google_analytics_4_settings.property_name, send_to=sorted(set(labels_))))
out["conversion_actions"] = convs
out["customer_conversion_goals"] = [dict(category=E(r.customer_conversion_goal.category), origin=E(r.customer_conversion_goal.origin),
                                         biddable=r.customer_conversion_goal.biddable)
                                    for r in q(c, "SELECT customer_conversion_goal.category, customer_conversion_goal.origin, customer_conversion_goal.biddable FROM customer_conversion_goal")]
out["campaign_conversion_goals"] = [dict(campaign=str(r.campaign.id), category=E(r.campaign_conversion_goal.category),
                                         origin=E(r.campaign_conversion_goal.origin), biddable=r.campaign_conversion_goal.biddable)
                                    for r in q(c, f"SELECT campaign.id, campaign_conversion_goal.category, campaign_conversion_goal.origin, campaign_conversion_goal.biddable FROM campaign_conversion_goal WHERE campaign.id IN ({LIVE})")]
def _gcfg():
    return [dict(campaign=str(r.campaign.id), level=E(r.conversion_goal_campaign_config.goal_config_level),
                 custom_goal=r.conversion_goal_campaign_config.custom_conversion_goal)
            for r in q(c, f"SELECT campaign.id, conversion_goal_campaign_config.goal_config_level, conversion_goal_campaign_config.custom_conversion_goal FROM conversion_goal_campaign_config WHERE campaign.id IN ({LIVE})")]
out["goal_campaign_config"] = safe("conversion_goal_campaign_config", _gcfg)
def _cg():
    return [dict(id=str(r.custom_conversion_goal.id), name=r.custom_conversion_goal.name, status=E(r.custom_conversion_goal.status),
                 actions=list(r.custom_conversion_goal.conversion_actions))
            for r in q(c, "SELECT custom_conversion_goal.id, custom_conversion_goal.name, custom_conversion_goal.status, custom_conversion_goal.conversion_actions FROM custom_conversion_goal")]
out["custom_conversion_goals"] = safe("custom_conversion_goal", _cg)

# ---------------- change history ----------------
def _ce():
    rows = []
    for r in q(c, f"""SELECT change_event.change_date_time, change_event.change_resource_type, change_event.change_resource_name,
            change_event.client_type, change_event.user_email, change_event.resource_change_operation, change_event.changed_fields,
            change_event.campaign FROM change_event WHERE change_event.change_date_time >= '2026-10-02 08:45:00'
            AND change_event.change_date_time <= '{(NOW + datetime.timedelta(days=1)).date().isoformat()} 00:00:00'
            ORDER BY change_event.change_date_time LIMIT 10000"""):
        x = r.change_event
        rows.append(dict(at=x.change_date_time, type=E(x.change_resource_type), resource=x.change_resource_name, client=E(x.client_type),
                         user_is_agency=("greenmarketing" in (x.user_email or "").lower()), user_domain=(x.user_email or "").split("@")[-1],
                         op=E(x.resource_change_operation), fields=list(x.changed_fields.paths), campaign=x.campaign))
    return rows
out["change_events"] = safe("change_event", _ce) or []
def _cs():
    return [dict(at=r.change_status.last_change_date_time, type=E(r.change_status.resource_type), status=E(r.change_status.resource_status),
                 campaign=r.change_status.campaign, ad_group=r.change_status.ad_group)
            for r in q(c, f"""SELECT change_status.last_change_date_time, change_status.resource_type, change_status.resource_status,
                change_status.campaign, change_status.ad_group FROM change_status
                WHERE change_status.last_change_date_time >= '2026-10-02 08:45:00'
                AND change_status.last_change_date_time <= '{(NOW + datetime.timedelta(days=1)).date().isoformat()} 00:00:00' LIMIT 10000""")]
out["change_status"] = safe("change_status", _cs) or []

out_path = SNAP / "snapshot-2026-10-07.json"
out_path.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"WROTE {out_path}")

# ---------------- aggregate print ----------------
print(f"\nread {out['read_local']}")
for cid in LIVE10:
    x = camps.get(cid)
    if not x:
        print(f"  {cid}: NOT FOUND")
        continue
    cr = out["campaign_criteria"].get(cid, {})
    dev = {d["device"]: (round(d["bid_modifier"], 2) if d["bid_modifier_set"] else "unset") for d in cr.get("DEVICE", [])}
    sched = sorted({(s["day"][:3], s["start"], s["end"]) for s in cr.get("AD_SCHEDULE", [])})
    print(f"  {cid} {x['name'][:60]!r} {x['status']}/{x['primary']} {x['reasons']} {x['channel']} {x['bidding']} ceil={x['ceiling']} "
          f"budget=${x['budget'].get('amount')} part={x['partners']} disp={x['display']} geo={x['geo_pos']} aimax={x['ai_max']} "
          f"locs={sum(1 for l in cr.get('LOCATION', []) if not l['neg'])} neglocs={sum(1 for l in cr.get('LOCATION', []) if l['neg'])} dev={dev} sched={sched}")
other_enabled = [f"{k} {v['name'][:50]}" for k, v in camps.items() if not v["live10"] and v["status"] == "ENABLED"]
print(f"  other ENABLED campaigns: {other_enabled}")
print(f"  change_events since 10-02 08:45: {len(out['change_events'])}; change_status rows: {len(out['change_status'])}")
cnt = collections.Counter((e["at"][:10], e["type"], e["client"], e["user_is_agency"]) for e in out["change_events"])
for k, v in sorted(cnt.items()):
    print(f"    {k}: {v}")
