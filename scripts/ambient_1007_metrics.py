#!/usr/bin/env python3
"""Ambient | 2026-10-07 | READ-ONLY performance pull for the tracking-repair / qualified-lead audit.

No mutations. Window 2026-09-01 .. today (today is PARTIAL). Writes snapshots/metrics-2026-10-07.json and
exports/click-view-2026-09-01_2026-10-07.jsonl (gclid -> campaign / ad group / keyword / click type, for lead
matching; gclids are not printed). Prints aggregates only.
"""
from __future__ import annotations

import collections
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP, EXPORTS  # noqa: E402

A = "2026-09-01"
NOW = datetime.datetime.now(TZ)
TODAY = NOW.date().isoformat()
money = lambda v: round(v / 1e6, 2)

c = client()
ident = identity_gate(c, verbose=False)
print(f"identity PASS {ident['descriptive_name']} {ident['customer_id']} read {NOW.isoformat(timespec='seconds')}")
out = {"read_local": NOW.isoformat(timespec="seconds"), "window": [A, TODAY], "today_partial": TODAY}
M = "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, metrics.all_conversions"


def mrow(x):
    return dict(impr=x.impressions, clicks=x.clicks, cost=money(x.cost_micros), conv=round(x.conversions, 2),
                all_conv=round(x.all_conversions, 2))


# campaign x day
out["campaign_day"] = [dict(campaign=str(r.campaign.id), name=r.campaign.name, channel=E(r.campaign.advertising_channel_type),
                            date=r.segments.date, **mrow(r.metrics))
                       for r in q(c, f"""SELECT campaign.id, campaign.name, campaign.advertising_channel_type, segments.date, {M}
                           FROM campaign WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0""")]
# impression share by campaign for fixed windows (never averaged by day)
WIN = {"sep": ("2026-09-01", "2026-09-30"), "oct_complete": ("2026-10-01", "2026-10-06"), "oct7_partial": (TODAY, TODAY),
       "repair_baseline": ("2026-09-24", "2026-09-30"), "repair_test_complete": ("2026-10-01", "2026-10-06")}
isr = {}
for w, (a, b) in WIN.items():
    for r in q(c, f"""SELECT campaign.id, metrics.search_impression_share, metrics.search_rank_lost_impression_share,
            metrics.search_budget_lost_impression_share, metrics.search_top_impression_share, metrics.search_absolute_top_impression_share,
            {M} FROM campaign WHERE segments.date BETWEEN '{a}' AND '{b}' AND metrics.impressions > 0"""):
        x = r.metrics
        isr.setdefault(w, {})[str(r.campaign.id)] = dict(is_=round(x.search_impression_share * 100, 1), lost_rank=round(x.search_rank_lost_impression_share * 100, 1),
                                                         lost_budget=round(x.search_budget_lost_impression_share * 100, 1),
                                                         top=round(x.search_top_impression_share * 100, 1), abs_top=round(x.search_absolute_top_impression_share * 100, 1),
                                                         **mrow(x))
out["impression_share"] = isr

# ad group x day, keyword x day
out["ad_group_day"] = [dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), date=r.segments.date, **mrow(r.metrics))
                       for r in q(c, f"""SELECT campaign.id, ad_group.id, segments.date, {M} FROM ad_group
                           WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0""")]
out["keyword_day"] = [dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), kw=str(r.ad_group_criterion.criterion_id),
                           text=r.ad_group_criterion.keyword.text, match=E(r.ad_group_criterion.keyword.match_type), date=r.segments.date, **mrow(r.metrics))
                      for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                          ad_group_criterion.keyword.match_type, segments.date, {M} FROM keyword_view
                          WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0""")]
# PMax asset group x day
out["asset_group_day"] = [dict(campaign=str(r.campaign.id), asset_group=str(r.asset_group.id), date=r.segments.date, **mrow(r.metrics))
                          for r in q(c, f"""SELECT campaign.id, asset_group.id, segments.date, {M} FROM asset_group
                              WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0""")]
# conversions by action, by click/interaction date and by conversion date
out["conv_by_action_click_date"] = [dict(campaign=str(r.campaign.id), date=r.segments.date, action=r.segments.conversion_action.split("/")[-1],
                                         action_name=r.segments.conversion_action_name, conv=round(r.metrics.conversions, 2),
                                         all_conv=round(r.metrics.all_conversions, 2))
                                    for r in q(c, f"""SELECT campaign.id, segments.date, segments.conversion_action, segments.conversion_action_name,
                                        metrics.conversions, metrics.all_conversions FROM campaign
                                        WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.all_conversions > 0""")]
out["conv_by_action_conv_date"] = [dict(campaign=str(r.campaign.id), date=r.segments.date, action=r.segments.conversion_action.split("/")[-1],
                                        action_name=r.segments.conversion_action_name,
                                        conv=round(r.metrics.conversions_by_conversion_date, 2),
                                        all_conv=round(r.metrics.all_conversions_by_conversion_date, 2))
                                   for r in q(c, f"""SELECT campaign.id, segments.date, segments.conversion_action, segments.conversion_action_name,
                                       metrics.conversions_by_conversion_date, metrics.all_conversions_by_conversion_date FROM campaign
                                       WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.all_conversions_by_conversion_date > 0""")]
# ad-group level conversions by action (click date)
out["conv_by_action_ad_group"] = [dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), date=r.segments.date,
                                       action=r.segments.conversion_action.split("/")[-1], conv=round(r.metrics.conversions, 2),
                                       all_conv=round(r.metrics.all_conversions, 2))
                                  for r in q(c, f"""SELECT campaign.id, ad_group.id, segments.date, segments.conversion_action, metrics.conversions,
                                      metrics.all_conversions FROM ad_group WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.all_conversions > 0""")]
# device, click type, hour (Search + PMax campaign level)
out["device_day"] = [dict(campaign=str(r.campaign.id), date=r.segments.date, device=E(r.segments.device), **mrow(r.metrics))
                     for r in q(c, f"""SELECT campaign.id, segments.date, segments.device, {M} FROM campaign
                         WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0""")]
out["click_type"] = [dict(campaign=str(r.campaign.id), date=r.segments.date, click_type=E(r.segments.click_type), **mrow(r.metrics))
                     for r in q(c, f"""SELECT campaign.id, segments.date, segments.click_type, {M} FROM campaign
                         WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0""")]
out["hour"] = [dict(campaign=str(r.campaign.id), date=r.segments.date, hour=r.segments.hour, **mrow(r.metrics))
               for r in q(c, f"""SELECT campaign.id, segments.date, segments.hour, {M} FROM campaign
                   WHERE segments.date BETWEEN '2026-09-24' AND '{TODAY}' AND metrics.impressions > 0""")]
# PMax channel split (ad_network_type) for PMax campaigns
out["network"] = [dict(campaign=str(r.campaign.id), date=r.segments.date, network=E(r.segments.ad_network_type), **mrow(r.metrics))
                  for r in q(c, f"""SELECT campaign.id, segments.date, segments.ad_network_type, {M} FROM campaign
                      WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0""")]
# user location (where the person was) and targeted location
def loc():
    rows = []
    for r in q(c, f"""SELECT campaign.id, user_location_view.country_criterion_id, user_location_view.targeting_location,
            segments.geo_target_most_specific_location, segments.geo_target_state, {M}
            FROM user_location_view WHERE segments.date BETWEEN '{A}' AND '{TODAY}' AND metrics.impressions > 0"""):
        rows.append(dict(campaign=str(r.campaign.id), country=r.user_location_view.country_criterion_id,
                         in_target=r.user_location_view.targeting_location, most_specific=r.segments.geo_target_most_specific_location,
                         state=r.segments.geo_target_state, **mrow(r.metrics)))
    return rows
try:
    out["user_location"] = loc()
except Exception as exc:
    out["user_location_error"] = str(exc).split("\n")[0][:300]
    print("user_location_view read gap:", out["user_location_error"])
# geo constants for names
geo_ids = sorted({r["most_specific"] for r in out.get("user_location", []) if r["most_specific"]} |
                 {r["state"] for r in out.get("user_location", []) if r["state"]})
names = {}
for i in range(0, len(geo_ids), 200):
    chunk = ",".join(f"'{g}'" for g in geo_ids[i:i + 200])
    for r in q(c, f"SELECT geo_target_constant.resource_name, geo_target_constant.canonical_name, geo_target_constant.target_type FROM geo_target_constant WHERE geo_target_constant.resource_name IN ({chunk})"):
        names[r.geo_target_constant.resource_name] = (r.geo_target_constant.canonical_name, E(r.geo_target_constant.target_type))
out["geo_names"] = names

# call_view
out["calls"] = [dict(campaign=str(r.campaign.id), ad_group=str(r.ad_group.id), start=r.call_view.start_call_date_time, end=r.call_view.end_call_date_time,
                     duration=r.call_view.call_duration_seconds, status=E(r.call_view.call_status), type=E(r.call_view.type),
                     tracking_display_location=E(r.call_view.call_tracking_display_location), caller_area=r.call_view.caller_area_code)
                for r in q(c, f"""SELECT campaign.id, ad_group.id, call_view.start_call_date_time, call_view.end_call_date_time, call_view.call_duration_seconds,
                    call_view.call_status, call_view.type, call_view.call_tracking_display_location, call_view.caller_area_code
                    FROM call_view WHERE call_view.start_call_date_time >= '{A} 00:00:00'""")]

# click_view per day (gclid map), written to an export file only
cv_path = EXPORTS / f"click-view-{A}_{TODAY}.jsonl"
n = 0
with cv_path.open("w", encoding="utf-8") as fh:
    d = datetime.date.fromisoformat(A)
    while d <= NOW.date():
        for r in q(c, f"""SELECT click_view.gclid, click_view.ad_group_ad, click_view.keyword, click_view.keyword_info.text,
                click_view.keyword_info.match_type, click_view.area_of_interest.city, click_view.location_of_presence.city,
                campaign.id, ad_group.id, segments.click_type, segments.device, segments.date FROM click_view
                WHERE segments.date = '{d.isoformat()}'"""):
            v = r.click_view
            fh.write(json.dumps(dict(gclid=v.gclid, date=r.segments.date, campaign=str(r.campaign.id), ad_group=str(r.ad_group.id),
                                     keyword=v.keyword_info.text, match=E(v.keyword_info.match_type), click_type=E(r.segments.click_type),
                                     device=E(r.segments.device), loc_presence=v.location_of_presence.city,
                                     aoi=v.area_of_interest.city)) + "\n")
            n += 1
        d += datetime.timedelta(days=1)
out["click_view_file"] = str(cv_path.name)
out["click_view_rows"] = n

path = SNAP / "metrics-2026-10-07.json"
path.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"WROTE {path.name}; click_view rows {n} -> {cv_path.name}; calls {len(out['calls'])}")
