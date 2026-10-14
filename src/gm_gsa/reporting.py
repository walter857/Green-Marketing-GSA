from __future__ import annotations

from typing import Any


def safe_divide(numerator: float, denominator: float) -> float | None:
    return None if denominator == 0 else numerator / denominator


def profit_metrics(
    *,
    ad_spend: float,
    leads: int,
    qualified_leads: int,
    sales: int,
    revenue: float,
    fulfillment_cost: float = 0.0,
    sales_cost: float = 0.0,
) -> dict[str, Any]:
    gross_profit = revenue - fulfillment_cost
    profit_after_ads = gross_profit - ad_spend - sales_cost
    return {
        "ad_spend": ad_spend,
        "leads": leads,
        "qualified_leads": qualified_leads,
        "sales": sales,
        "revenue": revenue,
        "gross_profit": gross_profit,
        "profit_after_ads": profit_after_ads,
        "cpl": safe_divide(ad_spend, leads),
        "cpql": safe_divide(ad_spend, qualified_leads),
        "cac": safe_divide(ad_spend + sales_cost, sales),
        "roas": safe_divide(revenue, ad_spend),
        "gross_profit_roas": safe_divide(gross_profit, ad_spend),
        "lead_to_sale_rate": safe_divide(sales, leads),
        "qualified_to_sale_rate": safe_divide(sales, qualified_leads),
    }

