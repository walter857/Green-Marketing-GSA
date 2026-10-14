#!/usr/bin/env python3
"""Ambient Cooling - Live | 2026-08-27 | read-only performance extract.

Every required window, plus per-campaign, per-keyword, per-ad, per-conversion-
action, per-device, per-hour and per-day breakouts, impression share, invalid
clicks and pacing math. NO mutation.
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0827_lib import (  # noqa: E402
    AUGUST_MAX, CID, FIVE, IN5, NAME, SNAP, TZ, WINDOWS,
    client, q, identity_gate, E, write,
)

STAMP = "2026-08-27"
MET = ("metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr, "
       "metrics.average_cpc, metrics.conversions, metrics.all_conversions, "
       "metrics.conversions_value, metrics.invalid_clicks, metrics.invalid_click_rate")
MET_BASIC = ("metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.ctr, "
             "metrics.average_cpc, metrics.conversions, metrics.all_conversions, "
             "metrics.conversions_value")
ISM = ("metrics.search_impression_share, metrics.search_budget_lost_impression_share, "
       "metrics.search_rank_lost_impression_share, "
       "metrics.search_absolute_top_impression_share, metrics.search_top_impression_share")


def mm(x):
    return {
        "impr": x.impressions, "clicks": x.clicks,
        "cost": round(x.cost_micros / 1e6, 2),
        "ctr": round(x.ctr * 100, 2),
        "cpc": round(x.average_cpc / 1e6, 2),
        "conv": round(x.conversions, 2),
        "all_conv": round(x.all_conversions, 2),
        "conv_value": round(x.conversions_value, 2),
        "invalid_clicks": getattr(x, "invalid_clicks", 0),
        "invalid_click_rate": round(getattr(x, "invalid_click_rate", 0.0) * 100, 2),
    }


def agg(rows):
    t = {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0, "all_conv": 0.0,
         "conv_value": 0.0, "invalid_clicks": 0}
    for r in rows:
        x = r.metrics
        t["impr"] += x.impressions
        t["clicks"] += x.clicks
        t["cost"] += x.cost_micros / 1e6
        t["conv"] += x.conversions
        t["all_conv"] += x.all_conversions
        t["conv_value"] += x.conversions_value
        t["invalid_clicks"] += x.invalid_clicks
    t["cost"] = round(t["cost"], 2)
    t["conv"] = round(t["conv"], 2)
    t["all_conv"] = round(t["all_conv"], 2)
    t["conv_value"] = round(t["conv_value"], 2)
    t["ctr"] = round(t["clicks"] / t["impr"] * 100, 2) if t["impr"] else 0.0
    t["cpc"] = round(t["cost"] / t["clicks"], 2) if t["clicks"] else 0.0
    t["cvr"] = round(t["conv"] / t["clicks"] * 100, 2) if t["clicks"] else 0.0
    t["cpl"] = round(t["cost"] / t["conv"], 2) if t["conv"] else None
    return t


def main():
    c = client()
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(),
           "customer_id": CID, "read_only": True, "windows": WINDOWS}
    print("== IDENTITY GATE ==")
    out["identity"] = identity_gate(c, verbose=False)
    print("  PASS (all checks)")

    # ---------- account totals per window ----------
    print("\n== ACCOUNT TOTALS BY WINDOW (five live Search campaigns only) ==")
    acct = {}
    for wname, (a, b) in WINDOWS.items():
        rows = q(c, f"""SELECT campaign.id, {MET} FROM campaign
                        WHERE campaign.id IN ({IN5})
                          AND segments.date BETWEEN '{a}' AND '{b}'""")
        acct[wname] = agg(rows)
        t = acct[wname]
        print(f"  {wname:22s} {a}..{b}  impr={t['impr']:>6d} clicks={t['clicks']:>5d} "
              f"cost=${t['cost']:>9,.2f} ctr={t['ctr']:>5.2f}% cpc=${t['cpc']:>5.2f} "
              f"conv={t['conv']:>5.2f} cvr={t['cvr']:>5.2f}% "
              f"cpl={('$%.2f' % t['cpl']) if t['cpl'] else 'n/a':>9s} inv={t['invalid_clicks']}")
    out["account_by_window"] = acct

    # ---------- whole-account (every campaign) August, to catch legacy spend ----------
    print("\n== WHOLE ACCOUNT (ALL campaigns) AUGUST SETTLED + PARTIAL ==")
    whole = {}
    for wname in ("mtd_settled", "today_partial"):
        a, b = WINDOWS[wname]
        rows = q(c, f"""SELECT campaign.id, campaign.name, {MET} FROM campaign
                        WHERE segments.date BETWEEN '{a}' AND '{b}'""")
        whole[wname] = agg(rows)
        detail = [(r.campaign.name, round(r.metrics.cost_micros / 1e6, 2)) for r in rows
                  if r.metrics.cost_micros > 0]
        whole[wname + "_by_campaign"] = detail
        print(f"  {wname:16s} cost=${whole[wname]['cost']:,.2f} across "
              f"{len(detail)} spending campaigns")
        for n, cost in sorted(detail, key=lambda z: -z[1]):
            print(f"      ${cost:>9,.2f}  {n}")
    out["whole_account_august"] = whole

    # ---------- per campaign per window ----------
    print("\n== PER CAMPAIGN ==")
    per = {}
    for wname in ("mtd_settled", "today_partial", "since_last_audit",
                  "before_change", "change_day_partial", "after_change", "launch_to_date"):
        a, b = WINDOWS[wname]
        rows = q(c, f"""SELECT campaign.id, {MET}, {ISM} FROM campaign
                        WHERE campaign.id IN ({IN5})
                          AND segments.date BETWEEN '{a}' AND '{b}'""")
        d = {}
        for r in rows:
            x = r.metrics
            d[str(r.campaign.id)] = {
                **mm(x),
                "cvr": round(x.conversions / x.clicks * 100, 2) if x.clicks else 0.0,
                "cpl": round(x.cost_micros / 1e6 / x.conversions, 2) if x.conversions else None,
                "search_is": round(x.search_impression_share * 100, 2),
                "budget_lost_is": round(x.search_budget_lost_impression_share * 100, 2),
                "rank_lost_is": round(x.search_rank_lost_impression_share * 100, 2),
                "abs_top_is": round(x.search_absolute_top_impression_share * 100, 2),
            }
        per[wname] = d
        print(f"\n  --- {wname} ({a}..{b}) ---")
        hdr = (f"  {'campaign':20s} {'impr':>6s} {'clk':>5s} {'cost':>10s} {'ctr':>7s} "
               f"{'cpc':>7s} {'conv':>6s} {'cvr':>7s} {'cpl':>9s} {'IS':>7s} "
               f"{'budgLost':>9s} {'rankLost':>9s}")
        print(hdr)
        for cid in FIVE:
            v = d.get(cid)
            if not v:
                print(f"  {NAME[cid]:20s} (no rows)")
                continue
            print(f"  {NAME[cid]:20s} {v['impr']:>6d} {v['clicks']:>5d} "
                  f"${v['cost']:>9,.2f} {v['ctr']:>6.2f}% ${v['cpc']:>6.2f} "
                  f"{v['conv']:>6.2f} {v['cvr']:>6.2f}% "
                  f"{('$%.2f' % v['cpl']) if v['cpl'] else 'n/a':>9s} "
                  f"{v['search_is']:>6.2f}% {v['budget_lost_is']:>8.2f}% {v['rank_lost_is']:>8.2f}%")
    out["per_campaign"] = per

    # ---------- daily spend ----------
    print("\n== DAILY SPEND, FIVE CAMPAIGNS, AUGUST ==")
    daily = {}
    for r in q(c, f"""SELECT segments.date, campaign.id, {MET} FROM campaign
                      WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-27'"""):
        d = r.segments.date
        e = daily.setdefault(d, {"cost": 0.0, "clicks": 0, "impr": 0, "conv": 0.0})
        e["cost"] += r.metrics.cost_micros / 1e6
        e["clicks"] += r.metrics.clicks
        e["impr"] += r.metrics.impressions
        e["conv"] += r.metrics.conversions
    run = 0.0
    for d in sorted(daily):
        daily[d]["cost"] = round(daily[d]["cost"], 2)
        daily[d]["conv"] = round(daily[d]["conv"], 2)
        run += daily[d]["cost"]
        flag = " <-- PARTIAL (today)" if d == "2026-08-27" else ""
        print(f"  {d}  ${daily[d]['cost']:>8,.2f}  cum=${run:>9,.2f}  "
              f"clicks={daily[d]['clicks']:>4d} impr={daily[d]['impr']:>5d} "
              f"conv={daily[d]['conv']:.2f}{flag}")
    out["daily"] = daily
    out["august_to_date_five"] = round(run, 2)

    # ---------- HVAC Installation daily (budget change subject) ----------
    print("\n== HVAC INSTALLATION (24132507747) DAILY ==")
    hi = {}
    for r in q(c, """SELECT segments.date, metrics.impressions, metrics.clicks,
                     metrics.cost_micros, metrics.conversions, metrics.average_cpc
                     FROM campaign WHERE campaign.id = 24132507747
                       AND segments.date BETWEEN '2026-08-14' AND '2026-08-27'"""):
        hi[r.segments.date] = {
            "impr": r.metrics.impressions, "clicks": r.metrics.clicks,
            "cost": round(r.metrics.cost_micros / 1e6, 2),
            "conv": round(r.metrics.conversions, 2),
            "cpc": round(r.metrics.average_cpc / 1e6, 2)}
    for d in sorted(hi):
        v = hi[d]
        mark = "  <== budget $138.16 -> $176.15 at 01:23 ET" if d == "2026-08-22" else ""
        print(f"  {d} cost=${v['cost']:>7,.2f} clicks={v['clicks']:>3d} "
              f"impr={v['impr']:>4d} cpc=${v['cpc']:>6.2f} conv={v['conv']:.2f}{mark}")
    out["hvac_installation_daily"] = hi

    # ---------- AC Repair daily (negatives subject) ----------
    print("\n== AC REPAIR (24132507741) DAILY ==")
    ac = {}
    for r in q(c, """SELECT segments.date, metrics.impressions, metrics.clicks,
                     metrics.cost_micros, metrics.conversions, metrics.average_cpc
                     FROM campaign WHERE campaign.id = 24132507741
                       AND segments.date BETWEEN '2026-08-14' AND '2026-08-27'"""):
        ac[r.segments.date] = {
            "impr": r.metrics.impressions, "clicks": r.metrics.clicks,
            "cost": round(r.metrics.cost_micros / 1e6, 2),
            "conv": round(r.metrics.conversions, 2),
            "cpc": round(r.metrics.average_cpc / 1e6, 2)}
    for d in sorted(ac):
        v = ac[d]
        mark = "  <== car/auto/boat added 09:36 ET" if d == "2026-08-22" else ""
        print(f"  {d} cost=${v['cost']:>7,.2f} clicks={v['clicks']:>3d} "
              f"impr={v['impr']:>4d} cpc=${v['cpc']:>6.2f} conv={v['conv']:.2f}{mark}")
    out["ac_repair_daily"] = ac

    # ---------- conversions by action ----------
    print("\n== CONVERSIONS BY ACTION (five campaigns) ==")
    ca = {}
    for wname in ("mtd_settled", "launch_to_date", "before_change", "after_change"):
        a, b = WINDOWS[wname]
        rows = q(c, f"""SELECT campaign.id, segments.conversion_action_name,
                        segments.conversion_action_category, metrics.conversions,
                        metrics.all_conversions
                        FROM campaign WHERE campaign.id IN ({IN5})
                          AND segments.date BETWEEN '{a}' AND '{b}'
                          AND metrics.all_conversions > 0""")
        d = {}
        for r in rows:
            k = (r.segments.conversion_action_name, E(r.segments.conversion_action_category))
            e = d.setdefault(str(k), {"conversions": 0.0, "all_conversions": 0.0,
                                      "campaigns": {}})
            e["conversions"] += r.metrics.conversions
            e["all_conversions"] += r.metrics.all_conversions
            e["campaigns"][NAME[str(r.campaign.id)]] = round(
                e["campaigns"].get(NAME[str(r.campaign.id)], 0) + r.metrics.all_conversions, 2)
        for v in d.values():
            v["conversions"] = round(v["conversions"], 2)
            v["all_conversions"] = round(v["all_conversions"], 2)
        ca[wname] = d
        print(f"  --- {wname} ---")
        if not d:
            print("     (no conversion rows)")
        for k, v in sorted(d.items(), key=lambda z: -z[1]["all_conversions"]):
            print(f"     {k:70s} conv={v['conversions']:>6.2f} "
                  f"all={v['all_conversions']:>6.2f} {v['campaigns']}")
    out["conversions_by_action"] = ca

    # ---------- device / network / hour / day ----------
    print("\n== DEVICE (MTD settled) ==")
    dev = {}
    for r in q(c, f"""SELECT campaign.id, segments.device, {MET} FROM campaign
                      WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-26'"""):
        k = E(r.segments.device)
        e = dev.setdefault(k, {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0})
        e["impr"] += r.metrics.impressions
        e["clicks"] += r.metrics.clicks
        e["cost"] += r.metrics.cost_micros / 1e6
        e["conv"] += r.metrics.conversions
    for k, v in sorted(dev.items(), key=lambda z: -z[1]["cost"]):
        v["cost"] = round(v["cost"], 2)
        v["conv"] = round(v["conv"], 2)
        print(f"  {k:12s} impr={v['impr']:>6d} clicks={v['clicks']:>5d} "
              f"cost=${v['cost']:>9,.2f} conv={v['conv']:.2f}")
    out["device"] = dev

    print("\n== NETWORK (MTD settled) ==")
    net = {}
    for r in q(c, f"""SELECT campaign.id, segments.ad_network_type, {MET} FROM campaign
                      WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-26'"""):
        k = E(r.segments.ad_network_type)
        e = net.setdefault(k, {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0})
        e["impr"] += r.metrics.impressions
        e["clicks"] += r.metrics.clicks
        e["cost"] += r.metrics.cost_micros / 1e6
        e["conv"] += r.metrics.conversions
    for k, v in net.items():
        v["cost"] = round(v["cost"], 2)
        print(f"  {k:24s} impr={v['impr']:>6d} clicks={v['clicks']:>5d} cost=${v['cost']:,.2f}")
    out["network"] = net

    print("\n== HOUR OF DAY (MTD settled) - out-of-schedule check ==")
    hour = {}
    MET_NOINV = ("metrics.impressions, metrics.clicks, metrics.cost_micros, "
                 "metrics.conversions")
    for r in q(c, f"""SELECT campaign.id, segments.hour, segments.day_of_week, {MET_NOINV}
                      FROM campaign WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-01' AND '2026-08-26'"""):
        k = (E(r.segments.day_of_week), r.segments.hour)
        e = hour.setdefault(str(k), {"impr": 0, "clicks": 0, "cost": 0.0})
        e["impr"] += r.metrics.impressions
        e["clicks"] += r.metrics.clicks
        e["cost"] += r.metrics.cost_micros / 1e6
    allowed = {"MONDAY": (8, 20), "TUESDAY": (8, 20), "WEDNESDAY": (8, 20),
               "THURSDAY": (8, 20), "FRIDAY": (8, 20), "SATURDAY": (8, 13)}
    viol = []
    for k, v in hour.items():
        day, hr = eval(k)  # noqa: S307 - our own tuple string
        v["cost"] = round(v["cost"], 2)
        rng = allowed.get(day)
        if rng is None or not (rng[0] <= hr < rng[1]):
            if v["impr"] or v["cost"]:
                viol.append({"day": day, "hour": hr, **v})
    out["hour_of_week"] = hour
    out["out_of_schedule_delivery"] = viol
    if viol:
        print("  OUT-OF-SCHEDULE DELIVERY DETECTED:")
        for v in sorted(viol, key=lambda z: -z["cost"]):
            print(f"     {v['day']:10s} {v['hour']:02d}:00  impr={v['impr']} "
                  f"clicks={v['clicks']} cost=${v['cost']:.2f}")
    else:
        print("  PASS: zero impressions outside Mon-Fri 08-20 / Sat 08-13.")

    # ---------- keyword performance ----------
    print("\n== KEYWORD PERFORMANCE (launch to date, settled) ==")
    kws = []
    for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group.name,
                      ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
                      ad_group_criterion.status, {MET_BASIC}
                      FROM keyword_view WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-14' AND '2026-08-26'"""):
        x = r.ad_group_criterion
        kws.append({"campaign": NAME[str(r.campaign.id)], "ad_group": r.ad_group.name,
                    "text": x.keyword.text, "match": E(x.keyword.match_type),
                    "status": E(x.status), **mm(r.metrics)})
    out["keyword_performance"] = kws
    for k in sorted(kws, key=lambda z: -z["cost"]):
        print(f"  {k['campaign']:18s} [{k['match'][:6]:6s}] {k['text']:30s} "
              f"impr={k['impr']:>5d} clk={k['clicks']:>4d} cost=${k['cost']:>8,.2f} "
              f"cpc=${k['cpc']:>6.2f} conv={k['conv']:.2f}")

    # ---------- ad performance ----------
    print("\n== AD PERFORMANCE (launch to date, settled) ==")
    ads = []
    for r in q(c, f"""SELECT campaign.id, ad_group.name, ad_group_ad.ad.id,
                      ad_group_ad.status, {MET_BASIC}
                      FROM ad_group_ad WHERE campaign.id IN ({IN5})
                        AND segments.date BETWEEN '2026-08-14' AND '2026-08-26'"""):
        ads.append({"campaign": NAME[str(r.campaign.id)], "ad_group": r.ad_group.name,
                    "ad_id": str(r.ad_group_ad.ad.id), "status": E(r.ad_group_ad.status),
                    **mm(r.metrics)})
    out["ad_performance"] = ads
    for a in sorted(ads, key=lambda z: -z["cost"]):
        print(f"  {a['campaign']:18s} ad {a['ad_id']} {a['status']:8s} "
              f"impr={a['impr']:>5d} clk={a['clicks']:>4d} cost=${a['cost']:>8,.2f} "
              f"ctr={a['ctr']:>5.2f}% conv={a['conv']:.2f}")

    # ---------- geo ----------
    print("\n== TOP LOCATIONS BY SPEND (MTD settled) ==")
    geo = []
    try:
        MET_G = ("metrics.impressions, metrics.clicks, metrics.cost_micros, "
                 "metrics.ctr, metrics.average_cpc, metrics.conversions, "
                 "metrics.all_conversions, metrics.conversions_value")
        for r in q(c, f"""SELECT campaign.id, geographic_view.country_criterion_id,
                          geographic_view.location_type, {MET_G}
                          FROM geographic_view WHERE campaign.id IN ({IN5})
                            AND segments.date BETWEEN '2026-08-01' AND '2026-08-26'"""):
            geo.append({"campaign": NAME[str(r.campaign.id)],
                        "country": str(r.geographic_view.country_criterion_id),
                        "location_type": E(r.geographic_view.location_type),
                        "impr": r.metrics.impressions, "clicks": r.metrics.clicks,
                        "cost": round(r.metrics.cost_micros / 1e6, 2),
                        "conv": round(r.metrics.conversions, 2)})
    except Exception as exc:  # noqa: BLE001
        geo = [{"error": str(exc)[:200]}]
    out["geographic"] = geo
    agg_geo = {}
    for g in geo:
        if "error" in g:
            print("  ", g["error"]); break
        k = (g["country"], g["location_type"])
        e = agg_geo.setdefault(str(k), {"impr": 0, "clicks": 0, "cost": 0.0})
        e["impr"] += g["impr"]; e["clicks"] += g["clicks"]; e["cost"] += g["cost"]
    for k, v in sorted(agg_geo.items(), key=lambda z: -z[1]["cost"]):
        print(f"  {k:40s} impr={v['impr']:>6d} clicks={v['clicks']:>5d} cost=${v['cost']:,.2f}")

    # ---------- pacing ----------
    print("\n== AUGUST PACING vs $13,000 MAXIMUM ==")
    settled_days = 26  # 2026-08-01..2026-08-26
    live_days = 13     # 2026-08-14..2026-08-26 (campaigns launched 08-14)
    five_mtd = acct["mtd_settled"]["cost"]
    today = acct["today_partial"]["cost"]
    whole_mtd = whole["mtd_settled"]["cost"]
    whole_today = whole["today_partial"]["cost"]
    remaining_days = 4  # 2026-08-28..2026-08-31
    avg_live = five_mtd / live_days
    avg_last7 = sum(v["cost"] for d, v in daily.items()
                    if "2026-08-20" <= d <= "2026-08-26") / 7
    budget_cap_daily = 465.63
    proj_realistic = whole_mtd + whole_today + avg_last7 * remaining_days
    proj_conservative = whole_mtd + whole_today + budget_cap_daily * 2 * remaining_days
    pacing = {
        "five_campaign_mtd_settled": five_mtd,
        "five_campaign_today_partial": today,
        "whole_account_mtd_settled": whole_mtd,
        "whole_account_today_partial": whole_today,
        "whole_account_august_to_date": round(whole_mtd + whole_today, 2),
        "settled_days_in_month": settled_days,
        "live_days": live_days,
        "avg_daily_since_launch": round(avg_live, 2),
        "avg_daily_last_7_settled": round(avg_last7, 2),
        "sum_of_five_daily_budgets": budget_cap_daily,
        "remaining_days_after_today": remaining_days,
        "projection_realistic_last7_runrate": round(proj_realistic, 2),
        "projection_conservative_2x_budget_cap": round(proj_conservative, 2),
        "august_maximum": AUGUST_MAX,
        "headroom_realistic": round(AUGUST_MAX - proj_realistic, 2),
        "headroom_conservative": round(AUGUST_MAX - proj_conservative, 2),
    }
    out["pacing"] = pacing
    for k, v in pacing.items():
        print(f"  {k:42s} {v}")

    write(SNAP / f"performance-{STAMP}.json", out)
    return out


if __name__ == "__main__":
    main()
