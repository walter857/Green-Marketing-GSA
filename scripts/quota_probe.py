#!/usr/bin/env python3
"""Honest quota probe.

A single-row `FROM customer` read squeezes through the rolling window even when
the budget is effectively gone -- observed 2026-08-29 09:57 EDT, when that read
succeeded and the executor died seconds later on its pre-write snapshot. So this
probe runs the SAME multi-row query the executor needs (`campaign_criterion`,
the heaviest read in neg_execute.snapshot) and only reports OPEN if that works.

Reports the API's `Retry in <n> seconds` as an Eastern wall-clock time.
Exit 0 = open, 1 = exhausted, 3 = other error.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available
from gm_gsa.credentials import load_google_ads_client

TARGETS = {
    "ambient-cooling-heating": "2401959466",
    "pro-green-austin": "7380491929",
    "softwind-power-washing": "1521725229",
    "softwind-landscape-masonry": "2429758629",
}

# The executor's heaviest pre-write read. If this cannot run, the executor
# cannot even take its "before" snapshot, let alone mutate.
HEAVY = ("SELECT campaign.id, campaign_criterion.criterion_id "
         "FROM campaign_criterion WHERE campaign_criterion.negative = true "
         "AND campaign_criterion.type = 'KEYWORD' "
         "AND campaign.status != 'REMOVED'")


def eastern(dt):
    try:
        from zoneinfo import ZoneInfo
        return dt.astimezone(ZoneInfo("America/New_York"))
    except Exception:
        return dt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="ambient-cooling-heating", choices=sorted(TARGETS))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    cid = TARGETS[args.slug]

    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")

    now = datetime.now(timezone.utc)
    stamp = eastern(now).strftime("%Y-%m-%d %H:%M:%S %Z")

    try:
        n = len(list(svc.search(customer_id=cid, query=HEAVY)))
        print("{}  QUOTA OPEN  {}  (read {} campaign negatives)".format(
            stamp, args.slug, n))
        return 0
    except Exception as exc:  # noqa: BLE001
        text = str(exc)
        m = re.search(r"Retry in (\d+) seconds", text)
        if not m:
            print("{}  QUOTA UNKNOWN  non-quota error: {}".format(stamp, text[:200]))
            return 3
        secs = int(m.group(1))
        opens = eastern(now + timedelta(seconds=secs)).strftime("%Y-%m-%d %H:%M %Z")
        print("{}  QUOTA EXHAUSTED  retry in {}s ({:.1f}h)  opens ~{}".format(
            stamp, secs, secs / 3600, opens))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
