"""Importable forecast helper (Lincoln 14 geos, $8 cap, $16.44/day, 2026-09-29..12-20)."""
from apg_lib import CID  # noqa: E402

LANG = "languageConstants/1000"
GEOS14 = ["1021635", "1021647", "1021696", "1021783", "9024651", "9024671", "9024703",
          "9024728", "9024746", "9024748", "9024753", "9024754", "9195288", "9233865"]


def forecast(c, keywords):
    svc = c.get_service("KeywordPlanIdeaService")
    KMT = c.enums.KeywordMatchTypeEnum
    req = c.get_type("GenerateKeywordForecastMetricsRequest")
    req.customer_id = CID
    req.currency_code = "USD"
    req.forecast_period.start_date = "2026-09-29"
    req.forecast_period.end_date = "2026-12-20"
    camp = req.campaign
    camp.language_constants.append(LANG)
    camp.geo_target_constants.extend([f"geoTargetConstants/{g}" for g in GEOS14])
    camp.bidding_strategy.maximize_clicks_bidding_strategy.daily_target_spend_micros = 16_440_000
    camp.bidding_strategy.maximize_clicks_bidding_strategy.max_cpc_bid_ceiling_micros = 8_000_000
    ag = c.get_type("ForecastAdGroup")
    for text, mt in keywords:
        k = c.get_type("KeywordInfo")
        k.text = text
        k.match_type = getattr(KMT, mt)
        ag.keywords.append(k)
    camp.ad_groups.append(ag)
    try:
        m = svc.generate_keyword_forecast_metrics(request=req).campaign_forecast_metrics
        return {"clicks": round(m.clicks, 1), "cost": round(m.cost_micros / 1e6, 2)}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)[:200]}


