#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | schedule compliance, invalid clicks,
bid diagnostics, change history. Read-only.
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    CID, FIVE, IN5, NAME, SNAP, TZ, client, q, identity_gate, E, write,
)

STAMP = "2026-08-27"
ALLOWED = {"MONDAY": (8, 20), "TUESDAY": (8, 20), "WEDNESDAY": (8, 20),
           "THURSDAY": (8, 20), "FRIDAY": (8, 20), "SATURDAY": (8, 13)}
BASIC = "metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions"


def main():
    c = client()
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "read_only": True}
    out["identity"] = identity_gate(c, verbose=False)
    print("IDENTITY: PASS\n")

    # ---------- schedule compliance, split at the Package C boundary ----------
    print("== SCHEDULE COMPLIANCE ==")
    print("Package C C6C3DFFC9BD5AF9B applied the delivery schedule 2026-08-20 11:29 ET.")
    print("Only 2026-08-21 onward is fully governed by it.\n")
    windows = {
        "pre_schedule_2026-08-14_to_2026-08-20": ("2026-08-14", "2026-08-20"),
        "post_schedule_2026-08-21_to_2026-08-26_SETTLED": ("2026-08-21", "2026-08-26"),
        "today_partial_2026-08-27": ("2026-08-27", "2026-08-27"),
    }
    sched = {}
    for label, (a, b) in windows.items():
        hour = {}
        for r in q(c, f"""SELECT campaign.id, segments.hour, segments.day_of_week, {BASIC}
                          FROM campaign WHERE campaign.id IN ({IN5})
                            AND segments.date BETWEEN '{a}' AND '{b}'"""):
            k = (E(r.segments.day_of_week), r.segments.hour, str(r.campaign.id))
            e = hour.setdefault(k, {"impr": 0, "clicks": 0, "cost": 0.0})
            e["impr"] += r.metrics.impressions
            e["clicks"] += r.metrics.clicks
            e["cost"] += r.metrics.cost_micros / 1e6
        viol = []
        for (day, hr, cid), v in hour.items():
            rng = ALLOWED.get(day)
            if (rng is None or not (rng[0] <= hr < rng[1])) and (v["impr"] or v["cost"]):
                viol.append({"day": day, "hour": hr, "campaign": NAME[cid],
                             "impr": v["impr"], "clicks": v["clicks"],
                             "cost": round(v["cost"], 2)})
        cost = round(sum(v["cost"] for v in viol), 2)
        clicks = sum(v["clicks"] for v in viol)
        impr = sum(v["impr"] for v in viol)
        sched[label] = {"violations": viol, "out_of_schedule_cost": cost,
                        "out_of_schedule_clicks": clicks,
                        "out_of_schedule_impressions": impr}
        print(f"  --- {label} ---")
        if viol:
            print(f"     rows={len(viol)} impr={impr} clicks={clicks} cost=${cost:,.2f}")
            for v in sorted(viol, key=lambda z: (-z["cost"], -z["impr"]))[:15]:
                print(f"       {v['day']:10s} {v['hour']:02d}:00 {v['campaign']:18s} "
                      f"impr={v['impr']:>3d} clicks={v['clicks']} cost=${v['cost']:.2f}")
        else:
            print("     PASS: zero impressions outside Mon-Fri 08:00-20:00 / Sat 08:00-13:00.")
        print()
    out["schedule_compliance"] = sched

    # ---------- invalid clicks ----------
    print("== INVALID CLICKS (Google-filtered, never charged) ==")
    inv = {}
    for label, (a, b) in {
            "launch_to_date_settled": ("2026-08-14", "2026-08-26"),
            "before_change": ("2026-08-18", "2026-08-21"),
            "after_change": ("2026-08-23", "2026-08-26"),
            "today_partial": ("2026-08-27", "2026-08-27")}.items():
        d = {}
        for r in q(c, f"""SELECT campaign.id, metrics.clicks, metrics.invalid_clicks,
                          metrics.invalid_click_rate, metrics.impressions, metrics.cost_micros
                          FROM campaign WHERE campaign.id IN ({IN5})
                            AND segments.date BETWEEN '{a}' AND '{b}'"""):
            d[NAME[str(r.campaign.id)]] = {
                "impr": r.metrics.impressions,
                "charged_clicks": r.metrics.clicks,
                "invalid_clicks": r.metrics.invalid_clicks,
                "invalid_click_rate_pct": round(r.metrics.invalid_click_rate * 100, 2),
                "cost": round(r.metrics.cost_micros / 1e6, 2)}
        inv[label] = d
        print(f"  --- {label} ({a}..{b}) ---")
        for k, v in sorted(d.items(), key=lambda z: -z[1]["invalid_clicks"]):
            print(f"     {k:20s} impr={v['impr']:>5d} charged={v['charged_clicks']:>4d} "
                  f"invalid={v['invalid_clicks']:>5d} rate={v['invalid_click_rate_pct']:>6.2f}% "
                  f"cost=${v['cost']:,.2f}")
    out["invalid_clicks"] = inv

    # ---------- bid diagnostics ----------
    print("\n== BID / CPC DIAGNOSTICS (launch to date, settled) ==")
    bid = []
    for r in q(c, f"""SELECT campaign.id, ad_group.name,
                      ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
                      ad_group_criterion.effective_cpc_bid_micros,
                      ad_group_criterion.position_estimates.first_page_cpc_micros,
                      ad_group_criterion.position_estimates.top_of_page_cpc_micros,
                      ad_group_criterion.position_estimates.estimated_add_clicks_at_first_position_cpc,
                      metrics.average_cpc, metrics.clicks, metrics.cost_micros,
                      metrics.impressions, metrics.top_impression_percentage,
                      metrics.absolute_top_impression_percentage
                      FROM keyword_view WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-14' AND '2026-08-26'
                        AND metrics.clicks > 0"""):
        x = r.ad_group_criterion
        bid.append({
            "campaign": NAME[str(r.campaign.id)], "text": x.keyword.text,
            "match": E(x.keyword.match_type),
            "effective_cpc_bid": round(x.effective_cpc_bid_micros / 1e6, 2),
            "first_page_cpc_estimate": round(x.position_estimates.first_page_cpc_micros / 1e6, 2),
            "top_of_page_cpc_estimate": round(x.position_estimates.top_of_page_cpc_micros / 1e6, 2),
            "actual_avg_cpc": round(r.metrics.average_cpc / 1e6, 2),
            "clicks": r.metrics.clicks,
            "cost": round(r.metrics.cost_micros / 1e6, 2),
            "impr": r.metrics.impressions,
            "top_impr_pct": round(r.metrics.top_impression_percentage * 100, 1),
            "abs_top_impr_pct": round(r.metrics.absolute_top_impression_percentage * 100, 1),
        })
    out["bid_diagnostics"] = bid
    print(f"  {'campaign':18s} {'match':7s} {'keyword':26s} {'clicks':>6s} {'avgCPC':>8s} "
          f"{'topPgEst':>9s} {'1stPgEst':>9s} {'top%':>6s} {'absTop%':>8s}")
    for b in sorted(bid, key=lambda z: -z["actual_avg_cpc"]):
        print(f"  {b['campaign']:18s} {b['match'][:6]:7s} {b['text']:26s} "
              f"{b['clicks']:>6d} ${b['actual_avg_cpc']:>7.2f} "
              f"${b['top_of_page_cpc_estimate']:>8.2f} ${b['first_page_cpc_estimate']:>8.2f} "
              f"{b['top_impr_pct']:>5.1f}% {b['abs_top_impr_pct']:>7.1f}%")

    # ---------- top-of-page auction context ----------
    print("\n== AUCTION INSIGHT PROXY: click-type + top/abs-top share (MTD settled) ==")
    ct = {}
    for r in q(c, f"""SELECT campaign.id, segments.click_type, {BASIC}
                      FROM campaign WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-26'"""):
        k = E(r.segments.click_type)
        e = ct.setdefault(k, {"impr": 0, "clicks": 0, "cost": 0.0})
        e["impr"] += r.metrics.impressions
        e["clicks"] += r.metrics.clicks
        e["cost"] += r.metrics.cost_micros / 1e6
    for k, v in sorted(ct.items(), key=lambda z: -z[1]["cost"]):
        v["cost"] = round(v["cost"], 2)
        print(f"  {k:26s} impr={v['impr']:>6d} clicks={v['clicks']:>5d} cost=${v['cost']:,.2f}")
    out["click_type"] = ct

    # ---------- change history ----------
    print("\n== GOOGLE ADS CHANGE HISTORY (change_event; API caps the window at 30 days) ==")
    ch = []
    try:
        rows = q(c, """
            SELECT change_event.change_date_time, change_event.change_resource_type,
                   change_event.resource_change_operation, change_event.changed_fields,
                   change_event.client_type, change_event.user_email,
                   change_event.campaign, change_event.ad_group,
                   change_event.change_resource_name
            FROM change_event
            WHERE change_event.change_date_time >= '2026-07-29'
              AND change_event.change_date_time <= '2026-08-28'
            ORDER BY change_event.change_date_time DESC
            LIMIT 500
        """)
        for r in rows:
            x = r.change_event
            ch.append({
                "when": x.change_date_time,
                "resource_type": E(x.change_resource_type),
                "op": E(x.resource_change_operation),
                "fields": list(x.changed_fields.paths) if x.changed_fields else [],
                "client_type": E(x.client_type),
                "user": x.user_email,
                "campaign": x.campaign.split("/")[-1] if x.campaign else "",
                "resource": x.change_resource_name,
            })
    except Exception as exc:  # noqa: BLE001
        ch = [{"error": str(exc)[:400]}]
    out["change_history"] = ch
    print(f"  rows returned: {len(ch)}")
    for e in ch[:60]:
        if "error" in e:
            print("  ERROR:", e["error"]); break
        camp = NAME.get(e["campaign"], e["campaign"])
        print(f"  {e['when']} {e['op']:8s} {e['resource_type']:26s} {camp:20s} "
              f"{e['client_type']:16s} {e['user']}")
        if e["fields"]:
            print(f"        fields: {e['fields']}")

    # ---------- change status (broader, resource-level) ----------
    print("\n== CHANGE_STATUS (last 30 days) ==")
    cs = []
    try:
        for r in q(c, """
            SELECT change_status.last_change_date_time, change_status.resource_type,
                   change_status.resource_status, change_status.campaign,
                   change_status.ad_group, change_status.resource_name
            FROM change_status
            WHERE change_status.last_change_date_time >= '2026-07-29'
            ORDER BY change_status.last_change_date_time DESC
            LIMIT 300
        """):
            x = r.change_status
            cs.append({"when": x.last_change_date_time, "type": E(x.resource_type),
                       "status": E(x.resource_status),
                       "campaign": x.campaign.split("/")[-1] if x.campaign else "",
                       "resource": x.resource_name})
    except Exception as exc:  # noqa: BLE001
        cs = [{"error": str(exc)[:400]}]
    out["change_status"] = cs
    print(f"  rows returned: {len(cs)}")
    from collections import Counter
    if cs and "error" not in cs[0]:
        print("  ", dict(Counter(x["type"] for x in cs)))
        for e in cs[:40]:
            camp = NAME.get(e["campaign"], e["campaign"])
            print(f"  {e['when']} {e['type']:26s} {e['status']:10s} {camp:20s} {e['resource']}")
    else:
        print("  ERROR:", cs[0].get("error"))

    write(SNAP / f"diagnostics-{STAMP}.json", out)
    return out


if __name__ == "__main__":
    main()
