#!/usr/bin/env python3
"""2026-09-16 READ-ONLY inventory pass 2: proper error extraction + corrected fields."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, EVID, client, q, write, E  # noqa: E402

c = client()
out = {}


def err(exc):
    parts = []
    fail = getattr(exc, "failure", None)
    if fail is not None:
        for e in fail.errors:
            code = e.error_code
            which = code.WhichOneof("error_code") if hasattr(code, "WhichOneof") else "?"
            val = getattr(code, which, None) if which else None
            loc = ""
            if e.location and e.location.field_path_elements:
                loc = ".".join(x.field_name for x in e.location.field_path_elements)
            parts.append(f"{which}={E(val) if val is not None else '?'} :: {e.message} :: {loc}")
    return parts or [f"{type(exc).__name__}: {str(exc)[:200]}"]


def try_q(title, query, key, render=None):
    print(f"\n=== {title} ===")
    try:
        rows = q(c, query)
    except Exception as exc:  # noqa: BLE001
        for p in err(exc):
            print(f"  ERROR: {p}")
        out[key] = {"error": err(exc)}
        return None
    recs = [render(r) for r in rows] if render else len(rows)
    out[key] = recs
    print(f"  rows: {len(rows)}")
    return rows


# --- bisect the campaign query -------------------------------------------
print("=== CAMPAIGN FIELD BISECT ===")
for f in [
    "campaign.id, campaign.name, campaign.status",
    "campaign.serving_status",
    "campaign.advertising_channel_type, campaign.advertising_channel_sub_type",
    "campaign.bidding_strategy_type, campaign.campaign_budget",
    "campaign.start_date, campaign.end_date",
    "campaign.network_settings.target_google_search, campaign.network_settings.target_search_network, campaign.network_settings.target_content_network",
    "campaign.network_settings.target_partner_search_network",
    "campaign.geo_target_type_setting.positive_geo_target_type",
    "campaign.optimization_score",
    "campaign.tracking_url_template, campaign.final_url_suffix",
]:
    try:
        n = len(q(c, f"SELECT {f} FROM campaign"))
        print(f"  [OK  rows={n}] {f[:95]}")
    except Exception as exc:  # noqa: BLE001
        print(f"  [FAIL] {f[:95]}")
        for p in err(exc):
            print(f"         -> {p}")

try_q(
    "CAMPAIGNS (safe field set, all statuses)",
    """
    SELECT campaign.id, campaign.name, campaign.status, campaign.serving_status,
           campaign.advertising_channel_type, campaign.bidding_strategy_type,
           campaign.start_date, campaign.end_date
    FROM campaign
    """,
    "campaigns",
    lambda r: {"id": str(r.campaign.id), "name": r.campaign.name,
               "status": E(r.campaign.status), "serving": E(r.campaign.serving_status),
               "channel": E(r.campaign.advertising_channel_type),
               "bidding": E(r.campaign.bidding_strategy_type),
               "start": r.campaign.start_date, "end": r.campaign.end_date},
)
for x in out.get("campaigns") or []:
    print(f"    {x}")

# --- shared sets -----------------------------------------------------------
rows = try_q(
    "SHARED SETS (detail)",
    """
    SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status,
           shared_set.member_count, shared_set.reference_count
    FROM shared_set
    """,
    "shared_sets",
    lambda r: {"id": str(r.shared_set.id), "name": r.shared_set.name,
               "type": E(r.shared_set.type_), "status": E(r.shared_set.status),
               "members": r.shared_set.member_count, "refs": r.shared_set.reference_count},
)
for x in out.get("shared_sets") or []:
    print(f"    {x['id']:>12} {x['type']:>32} {x['status']:>8} members={x['members']:>5} "
          f"refs={x['refs']} {x['name'][:40]}")

try_q(
    "SHARED CRITERIA (members of shared sets)",
    """
    SELECT shared_criterion.shared_set, shared_criterion.criterion_id,
           shared_criterion.type, shared_criterion.keyword.text,
           shared_criterion.keyword.match_type
    FROM shared_criterion
    """,
    "shared_criteria",
    lambda r: {"set": r.shared_criterion.shared_set.split("~")[-1],
               "text": r.shared_criterion.keyword.text,
               "match": E(r.shared_criterion.keyword.match_type)},
)

try_q(
    "CAMPAIGN SHARED SETS",
    "SELECT campaign_shared_set.campaign, campaign_shared_set.shared_set, campaign_shared_set.status FROM campaign_shared_set",
    "campaign_shared_sets",
    lambda r: {"campaign": r.campaign_shared_set.campaign.split("/")[-1],
               "shared_set": r.campaign_shared_set.shared_set.split("~")[-1],
               "status": E(r.campaign_shared_set.status)},
)

# --- account-level negative criteria (correct field set) -------------------
try_q(
    "ACCOUNT-LEVEL NEGATIVE CRITERIA",
    """
    SELECT customer_negative_criterion.id, customer_negative_criterion.type,
           customer_negative_criterion.placement.url,
           customer_negative_criterion.negative_keyword_list.shared_set
    FROM customer_negative_criterion
    """,
    "account_negatives",
    lambda r: {"id": str(r.customer_negative_criterion.id),
               "type": E(r.customer_negative_criterion.type_)},
)

# --- billing (full detail; this is a launch blocker) -----------------------
try_q(
    "BILLING SETUP (full)",
    """
    SELECT billing_setup.id, billing_setup.status, billing_setup.payments_account,
           billing_setup.payments_account_info.payments_account_id,
           billing_setup.payments_account_info.payments_account_name,
           billing_setup.payments_account_info.payments_profile_id,
           billing_setup.payments_account_info.payments_profile_name,
           billing_setup.payments_account_info.secondary_payments_profile_id,
           billing_setup.start_date_time, billing_setup.end_date_time,
           billing_setup.start_time_type, billing_setup.end_time_type
    FROM billing_setup
    """,
    "billing_setup",
    lambda r: {"id": str(r.billing_setup.id), "status": E(r.billing_setup.status),
               "pay_acct_id": r.billing_setup.payments_account_info.payments_account_id,
               "pay_acct_name": r.billing_setup.payments_account_info.payments_account_name,
               "profile_name": r.billing_setup.payments_account_info.payments_profile_name,
               "start": r.billing_setup.start_date_time,
               "end": r.billing_setup.end_date_time,
               "start_type": E(r.billing_setup.start_time_type),
               "end_type": E(r.billing_setup.end_time_type)},
)
for x in out.get("billing_setup") or []:
    print(f"    {x}")

# --- links -----------------------------------------------------------------
for title, query, key in [
    ("PRODUCT LINKS", "SELECT product_link.resource_name, product_link.product_link_id, product_link.type FROM product_link", "product_links"),
    ("GOOGLE ADS LINKS (GA4 legacy)", "SELECT third_party_app_analytics_link.resource_name FROM third_party_app_analytics_link", "tpaa_links"),
    ("CUSTOMER CLIENT LINKS", "SELECT customer_client_link.client_customer, customer_client_link.status, customer_client_link.manager_link_id FROM customer_client_link", "client_links"),
    ("RECOMMENDATION SUBSCRIPTION", "SELECT recommendation_subscription.type FROM recommendation_subscription", "rec_subs"),
    ("ACCESSIBLE BIDDING STRATEGIES", "SELECT bidding_strategy.id, bidding_strategy.name, bidding_strategy.type FROM bidding_strategy", "bidding_strategies"),
    ("CONVERSION VALUE RULES", "SELECT conversion_value_rule.id, conversion_value_rule.status FROM conversion_value_rule", "conv_value_rules"),
    ("CONVERSION CUSTOM VARIABLES", "SELECT conversion_custom_variable.id, conversion_custom_variable.name, conversion_custom_variable.status FROM conversion_custom_variable", "conv_custom_vars"),
    ("CUSTOMER LABELS", "SELECT label.id, label.name, label.status FROM label", "labels"),
]:
    try_q(title, query, key)

# --- change history --------------------------------------------------------
try_q(
    "CHANGE STATUS (recent resource changes)",
    """
    SELECT change_status.resource_name, change_status.last_change_date_time,
           change_status.resource_type, change_status.resource_status
    FROM change_status
    WHERE change_status.last_change_date_time >= '2026-08-16'
    ORDER BY change_status.last_change_date_time DESC
    LIMIT 100
    """,
    "change_status",
    lambda r: {"type": E(r.change_status.resource_type),
               "when": r.change_status.last_change_date_time,
               "status": E(r.change_status.resource_status),
               "rn": r.change_status.resource_name},
)
for x in (out.get("change_status") or [])[:30]:
    print(f"    {x['when']} {x['type']:>24} {x['status']}")

write(EVID / "2026-09-16-inventory2.json", out)
print("\nPASS 2 COMPLETE")
