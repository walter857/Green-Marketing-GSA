from __future__ import annotations

import unittest

from gm_gsa.reporting import profit_metrics


class ReportingTests(unittest.TestCase):
    def test_profit_metrics_use_gross_profit(self):
        metrics = profit_metrics(
            ad_spend=1000,
            leads=20,
            qualified_leads=10,
            sales=5,
            revenue=10000,
            fulfillment_cost=4000,
            sales_cost=500,
        )
        self.assertEqual(metrics["gross_profit"], 6000)
        self.assertEqual(metrics["profit_after_ads"], 4500)
        self.assertEqual(metrics["cpl"], 50)
        self.assertEqual(metrics["cpql"], 100)
        self.assertEqual(metrics["cac"], 300)
        self.assertEqual(metrics["roas"], 10)
        self.assertEqual(metrics["gross_profit_roas"], 6)


if __name__ == "__main__":
    unittest.main()

