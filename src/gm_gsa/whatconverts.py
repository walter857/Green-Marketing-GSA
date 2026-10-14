"""Scoped WhatConverts lead reads for reporting. QA leads are removed by default.

The agency credential sees every client, so account_id AND profile_id are mandatory and
every returned row is checked against them. Nothing here writes to WhatConverts.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from gm_gsa.qa_exclusions import QARules, split_qa

BASE = "https://app.whatconverts.com/api/v1"


def _auth() -> HTTPBasicAuth:
    return HTTPBasicAuth(os.environ["WHATCONVERTS_API_TOKEN"].strip(),
                         os.environ["WHATCONVERTS_SECRET"].strip())


def fetch_leads(account_id: str, profile_id: str, start_date: str, end_date: str, *,
                client_yaml: str | Path | None = None, include_qa: bool = False,
                max_pages: int = 40, **filters: Any) -> dict[str, Any]:
    """Return {"leads": kept, "qa_excluded": [(id, reason)], "raw_count": n}.

    ``client_yaml`` is required unless ``include_qa`` is True, so a report cannot silently
    skip the exclusion.
    """
    if not include_qa and client_yaml is None:
        raise ValueError("client_yaml is required so QA leads can be excluded")
    leads, page = [], 1
    while page <= max_pages:
        r = requests.get(f"{BASE}/leads", auth=_auth(), timeout=60,
                         params=dict(account_id=account_id, profile_id=profile_id,
                                     start_date=start_date, end_date=end_date,
                                     leads_per_page=250, page_number=page, **filters))
        r.raise_for_status()
        batch = r.json().get("leads", [])
        leads += batch
        if len(batch) < 250:
            break
        page += 1
    bad = [l.get("lead_id") for l in leads
           if str(l.get("profile_id")) != str(profile_id)
           or str(l.get("account_id")) != str(account_id)]
    if bad:
        raise RuntimeError(f"{len(bad)} leads outside account {account_id} / profile {profile_id}")
    if include_qa:
        return {"leads": leads, "qa_excluded": [], "raw_count": len(leads)}
    kept, excluded = split_qa(leads, QARules.from_client_yaml(client_yaml))
    return {"leads": kept, "qa_excluded": excluded, "raw_count": len(leads)}
