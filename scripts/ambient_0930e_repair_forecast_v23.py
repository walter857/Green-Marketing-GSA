#!/usr/bin/env python3
"""Ambient | 2026-09-30e | READ-ONLY Keyword Planner forecasts for campaign 24257819463 using API v23.

Why v23: google-ads 31.2.0 ships v21-v25. v24/v25 reduced CampaignToForecast to language/geo/bidding/ad-group keywords and
the response to clicks/cost/CPC/conversions. v21-v23 keep geo_modifiers, keyword_plan_network, negative_keywords (campaign
and ad group), and return impressions, CTR, conversions and conversion rate. The earlier "API cannot return impressions"
statement described v25 only and was wrong about the API.

Request: English; GOOGLE_SEARCH; the exact ENABLED Phrase/Exact keywords of the ENABLED repair ad groups (no additions);
campaign negatives + every attached shared negative list + the account-level negative list + each ad group's negatives
(raw negatives go to the API only, never printed); Maximize Clicks at the real $85/day; forecast 2026-10-01..2026-10-31.
Geo A: Maryland statewide (resolved from Google). Geo B: the campaign's 75 live location targets.
Not modelled by the API: the Mon-Fri 08:00-16:00 ad schedule and account-level pacing.
Google's forecast conversions are MODELLED OUTPUT, not verified Ambient leads, and are never used for CPL.
Writes snapshots/repair-forecast-v23-2026-09-30.json.
"""
from __future__ import annotations
import sys, json, re, time, collections, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, SNAP  # noqa: E402

V = "v23"
CAMP = "24257819463"
LANG = "languageConstants/1000"
START, END = "2026-10-01", "2026-10-31"
CEILS = [12, 15, 18, 21, 25, 30, 42]
c = client()
identity_gate(c, verbose=False)
svc = c.get_service("KeywordPlanIdeaService", version=V)
MT = c.get_type("KeywordMatchTypeEnum", version=V).KeywordMatchType
NET = c.get_type("KeywordPlanNetworkEnum", version=V).KeywordPlanNetwork
out = {"api_version": V, "window": [START, END], "doc": __doc__}

# ---- geos ----
gts = c.get_service("GeoTargetConstantService")
rq = c.get_type("SuggestGeoTargetConstantsRequest"); rq.locale = "en"; rq.country_code = "US"; rq.location_names.names.append("Maryland")
md = [s.geo_target_constant.resource_name for s in gts.suggest_geo_target_constants(request=rq).geo_target_constant_suggestions
      if s.geo_target_constant.canonical_name.replace(", ", ",") == "Maryland,United States" and s.geo_target_constant.target_type == "State"]
assert len(md) == 1, md
live_geo = [r.campaign_criterion.location.geo_target_constant for r in q(c, f"""SELECT campaign.id, campaign_criterion.location.geo_target_constant
        FROM campaign_criterion WHERE campaign.id = {CAMP} AND campaign_criterion.type = 'LOCATION' AND campaign_criterion.negative = FALSE
        AND campaign_criterion.status != 'REMOVED'""")]
GEOS = {"A_maryland_statewide": md, "B_live_75_targets": live_geo}
BATCH = 20  # API limit: max 20 locations per forecast request; the 75 targets are disjoint, so batches are summed
out["geos"] = {k: len(v) for k, v in GEOS.items()} | {"maryland": md[0]}
print("geos:", out["geos"])

# ---- keywords and negatives (fresh) ----
groups = collections.OrderedDict(); gneg = collections.defaultdict(list)
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
        ad_group_criterion.negative, ad_group_criterion.status FROM ad_group_criterion WHERE campaign.id = {CAMP}
        AND ad_group_criterion.type = 'KEYWORD' AND ad_group.status = 'ENABLED' AND ad_group_criterion.status != 'REMOVED'"""):
    g = r.ad_group.name[7:]; k = r.ad_group_criterion
    if k.negative:
        gneg[g].append((k.keyword.text, E(k.keyword.match_type)))
    elif E(k.status) == "ENABLED":
        groups.setdefault(g, []).append((k.keyword.text, E(k.keyword.match_type)))
cneg = [(r.campaign_criterion.keyword.text, E(r.campaign_criterion.keyword.match_type)) for r in q(c, f"""SELECT campaign.id,
        campaign_criterion.keyword.text, campaign_criterion.keyword.match_type FROM campaign_criterion WHERE campaign.id = {CAMP}
        AND campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE""")]
sets = [str(r.shared_set.id) for r in q(c, f"""SELECT campaign.id, shared_set.id, campaign_shared_set.status FROM campaign_shared_set
        WHERE campaign.id = {CAMP} AND campaign_shared_set.status = 'ENABLED'""")]
sets += [str(r.shared_set.id) for r in q(c, "SELECT shared_set.id FROM shared_set WHERE shared_set.type = 'ACCOUNT_LEVEL_NEGATIVE_KEYWORDS' AND shared_set.status = 'ENABLED'")]
for sid in sets:
    cneg += [(r.shared_criterion.keyword.text, E(r.shared_criterion.keyword.match_type)) for r in
             q(c, f"SELECT shared_set.id, shared_criterion.keyword.text, shared_criterion.keyword.match_type FROM shared_criterion WHERE shared_set.id = {sid}")]
cneg = sorted(set(cneg))
out["inputs"] = {"ad_groups": {g: len(v) for g, v in groups.items()}, "keywords": sum(len(v) for v in groups.values()),
                 "campaign_level_negatives_incl_shared_and_account": len(cneg), "shared_sets": sets,
                 "ad_group_negatives": {g: len(v) for g, v in gneg.items()},
                 "negative_match_types": dict(collections.Counter(m for _, m in cneg))}
print("inputs:", out["inputs"])


def kw(t, m):
    k = c.get_type("KeywordInfo", version=V); k.text = t; k.match_type = getattr(MT, m); return k


def call(fn, **kw_):
    for attempt in range(5):
        try:
            return fn(**kw_)
        except Exception as ex:  # noqa: BLE001
            s = str(ex)
            if "RESOURCE_EXHAUSTED" in s or "Too many" in s:
                m = re.search(r"Retry in (\d+)", s); w = min(90, int(m.group(1)) + 2) if m else 20 * (attempt + 1)
                print(f"   quota hit, waiting {w}s"); time.sleep(w); continue
            raise
    raise RuntimeError("quota retries exhausted")


def fc(geo, cap, grp=None, daily=85.0, with_neg=True):
    r = c.get_type("GenerateKeywordForecastMetricsRequest", version=V)
    r.customer_id = CID; r.currency_code = "USD"; r.forecast_period.start_date = START; r.forecast_period.end_date = END
    cp = r.campaign
    cp.language_constants.append(LANG)
    cp.keyword_plan_network = NET.GOOGLE_SEARCH
    for g in geo:
        gm = c.get_type("CriterionBidModifier", version=V); gm.geo_target_constant = g; cp.geo_modifiers.append(gm)
    if with_neg:
        cp.negative_keywords.extend([kw(t, m) for t, m in cneg])
    cp.bidding_strategy.maximize_clicks_bidding_strategy.daily_target_spend_micros = int(daily * 1e6)
    cp.bidding_strategy.maximize_clicks_bidding_strategy.max_cpc_bid_ceiling_micros = int(cap * 1e6)
    for g, kl in groups.items():
        sel = kl if grp is None else [x for x in kl if x[0].lower() in grp]
        if not sel:
            continue
        ag = c.get_type("ForecastAdGroup", version=V)
        for t, m in sel:
            b = c.get_type("BiddableKeyword", version=V); b.keyword.text = t; b.keyword.match_type = getattr(MT, m)
            ag.biddable_keywords.append(b)
        if with_neg:
            ag.negative_keywords.extend([kw(t, m) for t, m in gneg.get(g, [])])
        cp.ad_groups.append(ag)
    m = call(svc.generate_keyword_forecast_metrics, request=r).campaign_forecast_metrics
    time.sleep(1.2)
    return dict(impr=m.impressions, clicks=m.clicks, cost=m.cost_micros / 1e6, g_conv=m.conversions)


def fcg(geo, cap, **k):
    """Sum disjoint geo batches (<=20 locations each); derived rates computed from the sums."""
    tot = collections.Counter()
    for i in range(0, len(geo), BATCH):
        tot.update(fc(geo[i:i + BATCH], cap, **k))
    cl = tot["clicks"]
    return dict(impr=round(tot["impr"], 1), clicks=round(cl, 1), ctr=round(100 * cl / tot["impr"], 2) if tot["impr"] else 0,
                cpc=round(tot["cost"] / cl, 2) if cl else None, cost=round(tot["cost"], 2), g_conv=round(tot["g_conv"], 2),
                g_conv_rate=round(100 * tot["g_conv"] / cl, 2) if cl else 0, batches=-(-len(geo) // BATCH))


res = {"campaign": {}, "keyword": {}, "checks": {}}
for gname, geo in GEOS.items():
    res["campaign"][gname] = {cap: fcg(geo, cap) for cap in CEILS}
# budget-binding check and negatives effect at $42 on the live geo
res["checks"]["B_42_budget_1000"] = fcg(GEOS["B_live_75_targets"], 42, daily=1000)
res["checks"]["A_42_budget_1000"] = fcg(GEOS["A_maryland_statewide"], 42, daily=1000)
res["checks"]["A_42_no_negatives"] = fcg(GEOS["A_maryland_statewide"], 42, with_neg=False)
# highest-intent keyword texts, live geo, $18 / $21 / $42
for text in ["furnace repair near me", "furnace repair", "heating repair"]:
    res["keyword"][text] = {cap: fcg(GEOS["B_live_75_targets"], cap, grp={text}) for cap in (18, 21, 42)}
for text in ["furnace repair near me", "furnace repair", "heating repair", "heater repair", "gas furnace repair"]:
    res["keyword"][f"{text} [statewide]"] = {cap: fcg(GEOS["A_maryland_statewide"], cap, grp={text}) for cap in (18, 21, 42)}
out["results"] = res
(SNAP / "repair-forecast-v23-2026-09-30.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


def show(title, d):
    b = d[42]
    print(f"\n  {title}")
    print(f"    {'ceil':>5s} {'impr':>8s} {'clicks':>7s} {'CTR':>6s} {'avgCPC':>7s} {'cost':>9s} {'clicks vs $42':>13s} | Google-modelled conv / rate")
    for cap, v in sorted(d.items()):
        loss = f"{100 * (v['clicks'] - b['clicks']) / b['clicks']:+.0f}%" if b["clicks"] else "-"
        print(f"    ${cap:>4} {v['impr']:>8.0f} {v['clicks']:>7.1f} {v['ctr']:>5.2f}% {str(v['cpc']):>7s} {v['cost']:>9.2f} {loss:>13s} | {v['g_conv']} / {v['g_conv_rate']}%")


print(f"\n=== v23 FORECASTS, Maximize Clicks $85/day, {START}..{END}, English, Google Search, with negatives ===")
for g, d in res["campaign"].items():
    show(f"Campaign 24257819463, all enabled repair keywords, {g}", d)
print("\n  checks (live 75 geo, $42):", {k: v for k, v in res["checks"].items()}, "vs $85 w/ negatives:", res["campaign"]["B_live_75_targets"][42])
for t, d in res["keyword"].items():
    show(f"'{t}' (its Phrase/Exact keywords only), live 75 geo", d)
print("\nwrote snapshots/repair-forecast-v23-2026-09-30.json", datetime.datetime.now().isoformat(timespec="seconds"))
