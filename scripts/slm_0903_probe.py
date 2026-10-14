#!/usr/bin/env python3
"""Targeted follow-up SELECTs for the Softwind L&M recovery: audience targeting
setting, asset-automation opt-ins, budget/account-budget state, and the audience
criteria themselves. SELECT-only."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "2429758629"
OUT = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers/01c-probe.json"


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    out, errs = {}, []

    def q(name, query, fn):
        try:
            rows = list(svc.search(customer_id=CID, query=query))
            out[name] = [fn(r) for r in rows]
            print("  ok  %-34s %4d rows" % (name, len(rows)))
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            for k in ("message: ", "FaultMessage: "):
                if k in msg:
                    msg = msg.split(k, 1)[1][:300]
                    break
            errs.append({"q": name, "e": msg[:300]})
            print("  !!  %-34s %s" % (name, msg[:140]), file=sys.stderr)

    q("targeting_setting", """
        SELECT campaign.id, campaign.name,
               campaign.targeting_setting.target_restrictions,
               campaign.asset_automation_settings,
               campaign.optimization_goal_setting.optimization_goal_types
        FROM campaign WHERE campaign.status != 'REMOVED'""",
      lambda r: {
          "campaign_id": str(r.campaign.id), "name": r.campaign.name,
          "target_restrictions": [
              {"dimension": enum_name(t.targeting_dimension),
               "bid_only": t.bid_only}
              for t in r.campaign.targeting_setting.target_restrictions],
          "asset_automation": [
              {"type": enum_name(a.asset_automation_type),
               "status": enum_name(a.asset_automation_status)}
              for a in r.campaign.asset_automation_settings],
          "optimization_goals": [enum_name(g) for g in
                                 r.campaign.optimization_goal_setting.optimization_goal_types],
      })

    q("audience_criteria", """
        SELECT campaign.id, campaign.name, campaign_criterion.criterion_id,
               campaign_criterion.type, campaign_criterion.status,
               campaign_criterion.bid_modifier,
               campaign_criterion.user_interest.user_interest_category,
               campaign_criterion.user_list.user_list
        FROM campaign_criterion
        WHERE campaign_criterion.type IN ('USER_INTEREST','USER_LIST')
          AND campaign_criterion.status != 'REMOVED'""",
      lambda r: {
          "campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
          "criterion_id": str(r.campaign_criterion.criterion_id),
          "type": enum_name(r.campaign_criterion.type_),
          "user_interest": r.campaign_criterion.user_interest.user_interest_category,
          "user_list": r.campaign_criterion.user_list.user_list,
          "bid_modifier": r.campaign_criterion.bid_modifier or None,
      })

    q("account_budget", """
        SELECT account_budget.status, account_budget.approved_spending_limit_type,
               account_budget.adjusted_spending_limit_type,
               account_budget.approved_spending_limit_micros,
               account_budget.amount_served_micros, account_budget.total_adjustments_micros
        FROM account_budget""",
      lambda r: {
          "status": enum_name(r.account_budget.status),
          "approved_limit_type": enum_name(r.account_budget.approved_spending_limit_type),
          "adjusted_limit_type": enum_name(r.account_budget.adjusted_spending_limit_type),
          "approved_limit": r.account_budget.approved_spending_limit_micros / 1e6
                            if r.account_budget.approved_spending_limit_micros else None,
          "amount_served": r.account_budget.amount_served_micros / 1e6,
      })

    q("billing_setup", """
        SELECT billing_setup.id, billing_setup.status
        FROM billing_setup""",
      lambda r: {"id": str(r.billing_setup.id),
                 "status": enum_name(r.billing_setup.status)})

    # Which conversion actions have a live tag snippet / recent activity.
    q("conversion_recency", """
        SELECT segments.date, segments.conversion_action_name,
               metrics.all_conversions
        FROM campaign
        WHERE segments.date BETWEEN '2026-07-01' AND '2026-09-03'
        ORDER BY segments.date DESC""",
      lambda r: {"date": r.segments.date,
                 "action": r.segments.conversion_action_name,
                 "all_conversions": round(r.metrics.all_conversions, 3)})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out["errors"] = errs
    OUT.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("\nwrote %s  errors=%d" % (OUT.relative_to(ROOT), len(errs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
