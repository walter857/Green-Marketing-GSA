#!/usr/bin/env python3
"""Ambient | 2026-09-30d | READ-ONLY Keyword Planner work for the Heating & Furnace Repair CPC-ceiling decision.

Phase 2: GenerateKeywordHistoricalMetrics for every ENABLED keyword in the ENABLED ad groups of campaign 24257819463
         (Maryland resolved from Google at run time, English, Google Search, include_average_cpc).
Phase 3: GenerateKeywordForecastMetrics, Maximize Clicks, forecast 2026-10-01..2026-10-31, Maryland, English, at several
         CPC ceilings: campaign level at the real $85/day budget and at an unconstrained $1,000/day budget, per ad group and
         for the largest keyword texts (unconstrained budget).
Tool limits (introspected, google-ads v25): CampaignToForecast = language, geo, bidding strategy, ad groups (keywords
only). No negatives, no ad schedule, no network setting, no per-keyword output, and NO IMPRESSIONS in the response
(clicks, cost, average CPC only). Forecasts are Maryland-wide and 24/7, so absolute volumes exceed Ambient's 75-target,
Mon-Fri 08-16 footprint; compare ceilings on RELATIVE change. Planner never predicts Ambient's CPL or lead quality.
Writes snapshots/repair-planner-2026-09-30.json. No keyword is added anywhere.
"""
from __future__ import annotations
import sys, json, re, time, datetime, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, SNAP  # noqa: E402

CAMP = "24257819463"
LANG = "languageConstants/1000"
START, END = "2026-10-01", "2026-10-31"
CEILS_BUDGET = [8, 10, 12, 15, 18, 21, 25, 30, 42]
CEILS = [8, 10, 12, 15, 18, 42]
c = client()
identity_gate(c, verbose=False)
svc = c.get_service("KeywordPlanIdeaService")
KMT = c.enums.KeywordMatchTypeEnum
out = {"forecast_window": [START, END], "limits": __doc__}

# ---- resolve Maryland from Google ----
gts = c.get_service("GeoTargetConstantService")
req = c.get_type("SuggestGeoTargetConstantsRequest"); req.locale = "en"; req.country_code = "US"; req.location_names.names.append("Maryland")
md = [s.geo_target_constant for s in gts.suggest_geo_target_constants(request=req).geo_target_constant_suggestions
      if s.geo_target_constant.canonical_name.replace(", ", ",") == "Maryland,United States" and s.geo_target_constant.target_type == "State"]
if len(md) != 1:
    sys.exit(f"Maryland not resolved uniquely: {[x.resource_name for x in md]}")
GEO = md[0].resource_name
out["geo"] = {"resource": GEO, "canonical": md[0].canonical_name, "type": md[0].target_type, "status": E(md[0].status)}
print("Maryland resolved:", out["geo"])

# ---- keywords, fresh ----
kws = []
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
        ad_group_criterion.status FROM ad_group_criterion WHERE campaign.id = {CAMP} AND ad_group_criterion.type = 'KEYWORD'
        AND ad_group_criterion.negative = FALSE AND ad_group_criterion.status = 'ENABLED' AND ad_group.status = 'ENABLED'"""):
    kws.append((r.ad_group.name[7:], r.ad_group_criterion.keyword.text.lower(), E(r.ad_group_criterion.keyword.match_type)))
kws.sort()
groups = collections.defaultdict(list)
for g, t, mt in kws:
    groups[g].append((t, mt))
texts = sorted({t for _, t, _ in kws})
out["keywords"] = kws
print(f"enabled keywords: {len(kws)} across {len(groups)} ad groups; unique texts {len(texts)}")


def call(fn, *a, **k):
    for attempt in range(4):
        try:
            return fn(*a, **k)
        except Exception as ex:  # noqa: BLE001
            s = str(ex)
            if "RESOURCE_EXHAUSTED" in s or "429" in s or "Too many" in s:
                m = re.search(r"Retry in (\d+)", s)
                wait = min(90, int(m.group(1)) + 2) if m else 20 * (attempt + 1)
                print(f"   quota hit; waiting {wait}s"); time.sleep(wait); continue
            raise
    raise RuntimeError("quota retries exhausted")


# ---- Phase 2: historical metrics ----
hreq = c.get_type("GenerateKeywordHistoricalMetricsRequest")
hreq.customer_id = CID; hreq.keywords.extend(texts); hreq.language = LANG; hreq.geo_target_constants.append(GEO)
hreq.keyword_plan_network = c.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
hreq.historical_metrics_options.include_average_cpc = True
hist = {}
for r in call(svc.generate_keyword_historical_metrics, request=hreq).results:
    m = r.keyword_metrics
    hist[r.text.lower()] = dict(
        avg_monthly=m.avg_monthly_searches if m._pb.HasField("avg_monthly_searches") else None, competition=E(m.competition),
        competition_index=m.competition_index,
        top_low=round(m.low_top_of_page_bid_micros / 1e6, 2) if m.low_top_of_page_bid_micros else None,
        top_high=round(m.high_top_of_page_bid_micros / 1e6, 2) if m.high_top_of_page_bid_micros else None,
        planner_avg_cpc=round(m.average_cpc_micros / 1e6, 2) if m._pb.HasField("average_cpc_micros") else None,
        close_variants=sorted(v.lower() for v in r.close_variants),
        monthly={f"{x.year}-{E(x.month)[:3]}": x.monthly_searches for x in m.monthly_search_volumes})
out["historical"] = hist
snap = json.loads((SNAP / "repair-cpc-snapshot-2026-09-30.json").read_text(encoding="utf-8"))
act = collections.defaultdict(lambda: collections.Counter())
for v in snap["keywords"].values():
    if v["status"] == "ENABLED" and v["ag_status"] == "ENABLED":
        c0 = v.get("complete", {})
        act[v["text"].lower()].update(dict(impr=c0.get("impr", 0), clicks=c0.get("clicks", 0), cost=c0.get("cost", 0.0)))
print("\n=== PHASE 2: Maryland historical metrics vs Ambient actuals (Sep 17-29, complete days) ===")
print(f"  {'keyword':28s} {'MD/mo':>6s} {'comp':6s} {'idx':>3s} {'top low':>8s} {'top high':>8s} {'plnr cpc':>8s} | {'Amb clk':>7s} {'Amb cost':>9s} {'Amb cpc':>7s} ceil  leads")
for t in texts:
    h = hist.get(t, {}); a = act[t]
    cpc = f"{a['cost'] / a['clicks']:.2f}" if a["clicks"] else "-"
    print(f"  {t:28s} {str(h.get('avg_monthly')):>6s} {h.get('competition', '-')[:6]:6s} {str(h.get('competition_index')):>3s} "
          f"{str(h.get('top_low')):>8s} {str(h.get('top_high')):>8s} {str(h.get('planner_avg_cpc')):>8s} | {a['clicks']:>7d} {a['cost']:>9.2f} {cpc:>7s} $42   0"
          f"{'  (shares a volume bucket: ' + ', '.join(x for x in h.get('close_variants', []) if x != t)[:60] + ')' if len(h.get('close_variants', [])) > 1 else ''}")


# ---- Phase 3: forecasts ----
def fc(ad_groups, cap, daily):
    rq = c.get_type("GenerateKeywordForecastMetricsRequest")
    rq.customer_id = CID; rq.currency_code = "USD"
    rq.forecast_period.start_date = START; rq.forecast_period.end_date = END
    cp = rq.campaign
    cp.language_constants.append(LANG); cp.geo_target_constants.append(GEO)
    cp.bidding_strategy.maximize_clicks_bidding_strategy.daily_target_spend_micros = int(daily * 1e6)
    cp.bidding_strategy.maximize_clicks_bidding_strategy.max_cpc_bid_ceiling_micros = int(cap * 1e6)
    for kl in ad_groups:
        ag = c.get_type("ForecastAdGroup")
        for t, mt in kl:
            k = c.get_type("KeywordInfo"); k.text, k.match_type = t, getattr(KMT, mt); ag.keywords.append(k)
        cp.ad_groups.append(ag)
    m = call(svc.generate_keyword_forecast_metrics, request=rq).campaign_forecast_metrics
    time.sleep(1.5)
    return dict(clicks=round(m.clicks, 1), cost=round(m.cost_micros / 1e6, 2),
                cpc=round(m.average_cpc_micros / 1e6, 2) if m.average_cpc_micros else None)


F = {"campaign_budget85": {}, "campaign_unconstrained": {}, "ad_group": {}, "keyword_text": {}}
allg = list(groups.values())
for cap in CEILS_BUDGET:
    F["campaign_budget85"][cap] = fc(allg, cap, 85)
for cap in [8, 10, 12, 15, 18, 25, 42]:
    F["campaign_unconstrained"][cap] = fc(allg, cap, 1000)
for g, kl in groups.items():
    F["ad_group"][g] = {cap: fc([kl], cap, 1000) for cap in CEILS}
big = sorted(texts, key=lambda t: -(hist.get(t, {}).get("avg_monthly") or 0))[:3]
for t in big:
    kl = [(tt, mt) for _, tt, mt in kws if tt == t]
    F["keyword_text"][t] = {cap: fc([kl], cap, 1000) for cap in CEILS}
out["forecasts"] = F


def table(title, d, base_cap=42):
    b = d[base_cap]
    print(f"\n  {title}")
    print(f"    {'ceiling':>7s} {'clicks':>7s} {'cost':>9s} {'avg cpc':>7s} {'traffic vs $42':>15s}")
    for cap, v in sorted(d.items()):
        loss = f"{100 * (v['clicks'] - b['clicks']) / b['clicks']:+.0f}%" if b["clicks"] else "-"
        print(f"    ${cap:>6} {v['clicks']:>7.1f} {v['cost']:>9.2f} {str(v['cpc']):>7s} {loss:>15s}")


print(f"\n=== PHASE 3: Maximize Clicks forecasts, Maryland, {START}..{END} (24/7, no negatives, no impressions available) ===")
table("Campaign, all 5 enabled repair ad groups, real $85/day budget", F["campaign_budget85"])
table("Campaign, all 5 enabled repair ad groups, unconstrained $1,000/day (auction access only)", F["campaign_unconstrained"])
for g, d in F["ad_group"].items():
    table(f"Ad group {g} (unconstrained)", d)
for t, d in F["keyword_text"].items():
    table(f"Keyword '{t}' Phrase+Exact (unconstrained)", d)
(SNAP / "repair-planner-2026-09-30.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print("\nwrote snapshots/repair-planner-2026-09-30.json", datetime.datetime.now().isoformat(timespec="seconds"))
