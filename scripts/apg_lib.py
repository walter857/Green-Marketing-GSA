#!/usr/bin/env python3
"""Shared read-only helpers for the Apogee Lawns LLC permanent-Christmas-light build."""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.service_discovery import run_read_only_query  # noqa: E402
from gm_gsa.google_ads import enum_name as E  # noqa: E402

CID = "8164626278"
EXACT_NAME = "Apogee Lawns LLC - Live"
GM_MANAGER = "3373711342"
TZ = ZoneInfo("America/Chicago")

CLIENT_DIR = ROOT / "clients" / "apogee-lawns"
SNAP = CLIENT_DIR / "snapshots"
EXPORTS = CLIENT_DIR / "exports"
RECEIPTS = CLIENT_DIR / "receipts"
PLANS = CLIENT_DIR / "plans"
REPORTS = ROOT / "reports" / "apogee-lawns"
EVID = REPORTS / "evidence"

TODAY = datetime.date(2026, 9, 16)


def client():
    load_dotenv_if_available(ROOT / ".env")
    return load_google_ads_client()


def q(c, query, cid=CID):
    return list(run_read_only_query(c, cid, query))


def write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")
