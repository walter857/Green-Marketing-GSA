#!/usr/bin/env python3
"""Independent date + today-delivery probe for Softwind Power Washing.

The owner-supplied checkpoint header says "August 28, 2026 09:52 America/New_York".
Before any pacing math is trusted, establish the ACTUAL account-local date from
three independent sources and establish exactly how far today's delivery has got.

READ ONLY.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402

TZ = ZoneInfo("America/New_York")
CID = "1521725229"
CAMP_A = "24103511039"
CAMP_B = "24145053510"
NAMES = {CAMP_A: "Power Washing", CAMP_B: "Power Washing #2"}
OUT = ROOT / "clients/softwind-power-washing/snapshots/dateprobe-2026-08-27.json"


def rows(svc, query):
    out = []
    for batch in svc.search_stream(customer_id=CID, query=query):
        for r in batch.results:
            out.append(r)
    return out


def usd(m):
    return round((m or 0) / 1_000_000, 2)


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")

    p = {}
    now_local = datetime.now(TZ)
    p["source_1_host_clock_account_local"] = now_local.isoformat()

    # Source 2: what does the Google Ads API itself call TODAY / YESTERDAY?
    for token in ("TODAY", "YESTERDAY"):
        q = ("SELECT campaign.id, segments.date, metrics.impressions, "
             "metrics.cost_micros, metrics.clicks FROM campaign "
             f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
             f"AND segments.date DURING {token}")
        got = rows(svc, q)
        p["source_2_api_%s" % token.lower()] = {
            "rows": [{"campaign": NAMES[str(r.campaign.id)],
                      "date": r.segments.date,
                      "impressions": r.metrics.impressions,
                      "clicks": r.metrics.clicks,
                      "cost": usd(r.metrics.cost_micros)} for r in got],
            "row_count": len(got),
            "note": ("zero rows means zero impressions AND zero cost for that "
                     "date; the API omits all-zero date rows"),
        }

    # Source 3: the newest change_event timestamp in the account. A change cannot
    # be stamped in the future, so it bounds the current date from below.
    end = (now_local + timedelta(days=2)).strftime("%Y-%m-%d")
    start = (now_local - timedelta(days=28)).strftime("%Y-%m-%d")
    q = ("SELECT change_event.change_date_time, change_event.change_resource_type, "
         "change_event.resource_change_operation, change_event.user_email, "
         "change_event.change_resource_name "
         "FROM change_event "
         f"WHERE change_event.change_date_time >= '{start}' "
         f"AND change_event.change_date_time <= '{end}' "
         "ORDER BY change_event.change_date_time DESC LIMIT 30")
    ce = rows(svc, q)
    p["source_3_recent_change_events"] = [
        {"when": r.change_event.change_date_time,
         "resource_type": r.change_event.change_resource_type.name,
         "op": r.change_event.resource_change_operation.name,
         "resource": r.change_event.change_resource_name.rsplit("/", 2)[-2:],
         "user": r.change_event.user_email} for r in ce]
    p["source_3_newest_change"] = (
        ce[0].change_event.change_date_time if ce else None)

    # Source 4 (corroboration only): the host OS clock as the shell sees it.
    try:
        p["source_4_host_utc"] = subprocess.run(
            [sys.executable, "-c",
             "import datetime;print(datetime.datetime.now(datetime.timezone.utc)"
             ".isoformat())"],
            capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as exc:
        p["source_4_host_utc"] = "error: %s" % str(exc)[:200]

    # ---- today's delivery, hour by hour, vs the same hours on recent days ----
    today = now_local.strftime("%Y-%m-%d")
    q = ("SELECT campaign.id, segments.date, segments.hour, "
         "metrics.impressions, metrics.clicks, metrics.cost_micros "
         f"FROM campaign WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND segments.date BETWEEN '2026-08-17' AND '%s'" % today)
    hourly = {}
    for r in rows(svc, q):
        hourly.setdefault(r.segments.date, {}).setdefault(
            int(r.segments.hour), {"impressions": 0, "clicks": 0, "cost": 0.0})
        h = hourly[r.segments.date][int(r.segments.hour)]
        h["impressions"] += r.metrics.impressions
        h["clicks"] += r.metrics.clicks
        h["cost"] = round(h["cost"] + usd(r.metrics.cost_micros), 2)
    p["hourly_by_day"] = {d: dict(sorted(v.items())) for d, v in sorted(hourly.items())}

    # How much of a normal day's impressions land before 10:00?
    early, total = 0, 0
    for d, hrs in hourly.items():
        if d == today:
            continue
        for h, v in hrs.items():
            total += v["impressions"]
            if h < 10:
                early += v["impressions"]
    p["share_of_impressions_before_10am"] = {
        "early": early, "total": total,
        "pct": round(early / total * 100, 1) if total else None,
        "interpretation": (
            "If this share is small, zero impressions by 10:00 today is normal "
            "variance and NOT evidence of a delivery blocker.")}

    # Full daily series since first spend, so 'did it spend after Aug 26' is exact
    q = ("SELECT campaign.id, segments.date, metrics.impressions, metrics.clicks, "
         "metrics.cost_micros FROM campaign "
         f"WHERE campaign.id IN ({CAMP_A}, {CAMP_B}) "
         "AND segments.date BETWEEN '2026-08-01' AND '%s'" % today)
    daily = {}
    for r in rows(svc, q):
        d = daily.setdefault(r.segments.date, {"impressions": 0, "clicks": 0,
                                               "cost": 0.0, "per_campaign": {}})
        d["impressions"] += r.metrics.impressions
        d["clicks"] += r.metrics.clicks
        d["cost"] = round(d["cost"] + usd(r.metrics.cost_micros), 2)
        d["per_campaign"][NAMES[str(r.campaign.id)]] = {
            "impressions": r.metrics.impressions, "clicks": r.metrics.clicks,
            "cost": usd(r.metrics.cost_micros)}
    p["daily_august"] = dict(sorted(daily.items()))
    p["august_mtd_total_cost"] = round(sum(v["cost"] for v in daily.values()), 2)

    OUT.write_text(json.dumps(p, indent=2), encoding="utf-8")

    print("=" * 70)
    print("DATE PROBE")
    print("=" * 70)
    print("source 1  host clock, America/New_York : %s"
          % p["source_1_host_clock_account_local"])
    print("source 4  host clock, UTC              : %s" % p["source_4_host_utc"])
    print("source 3  newest change_event in acct  : %s" % p["source_3_newest_change"])
    print("source 2  API 'TODAY'                  : %s"
          % json.dumps(p["source_2_api_today"]["rows"]))
    print("source 2  API 'YESTERDAY'              : %s"
          % json.dumps(p["source_2_api_yesterday"]["rows"]))
    print()
    print("OWNER-SUPPLIED CHECKPOINT HEADER       : 2026-08-28 09:52 America/New_York")
    print("ACTUAL ACCOUNT-LOCAL DATE              : %s" % now_local.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print()
    print("--- DAILY AUGUST (only days with any delivery appear) ---")
    for d, v in p["daily_august"].items():
        print("  %s  $%-8s %3di %2dc   %s"
              % (d, v["cost"], v["impressions"], v["clicks"],
                 json.dumps(v["per_campaign"])))
    print("  MTD TOTAL: $%s" % p["august_mtd_total_cost"])
    print()
    print("--- HOURLY BY DAY (2026-08-17 onward) ---")
    for d, hrs in p["hourly_by_day"].items():
        line = ", ".join("%02d:00 %si/%sc/$%s" % (h, v["impressions"], v["clicks"],
                                                  v["cost"]) for h, v in hrs.items())
        print("  %s  %s" % (d, line))
    print()
    print("--- EARLY-DAY DELIVERY SHARE ---")
    print("  %s" % json.dumps(p["share_of_impressions_before_10am"], indent=2))
    print()
    print("--- RECENT CHANGE EVENTS (newest first) ---")
    for e in p["source_3_recent_change_events"][:20]:
        print("  %s  %-28s %-8s %s" % (e["when"], e["resource_type"], e["op"],
                                       "/".join(e["resource"])))
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
