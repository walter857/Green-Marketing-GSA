#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml
from gm_gsa.safety import assert_no_embedded_secrets
from gm_gsa.validators import assert_valid_campaign_plan
from gm_gsa.work_orders import assert_valid_work_order


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--work-order", required=True)
    parser.add_argument("--brief", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    profile_document = load_yaml(args.client)
    work_order = load_yaml(args.work_order)
    assert_valid_work_order(work_order, profile_document)
    profile = profile_document["client"]
    exact_service = work_order["work_order"]["service"]["exact_primary_service"]
    if work_order["work_order"]["task"]["mode"] not in ("draft", "create-paused"):
        raise ValueError("Campaign drafts require a draft or create-paused work order.")
    draft = copy.deepcopy(load_yaml(args.brief))
    ads = profile["google_ads"]
    draft["target"] = {
        "child_customer_id": str(ads["child_customer_id"]),
        "exact_child_account_name": ads["exact_child_account_name"],
        "vertical": profile["vertical"],
        "exact_primary_service": exact_service,
    }

    service_area = profile.get("service_area") or {}
    schedule = profile.get("schedule") or {}
    website = profile.get("website") or {}
    for campaign in draft.get("campaigns", []):
        campaign["status"] = "PAUSED"
        campaign["currency"] = ads["currency"]
        campaign["schedule"] = copy.deepcopy(schedule.get("windows") or campaign.get("schedule"))
        current_location = campaign.setdefault("location", {})
        current_location["option"] = "PRESENCE"
        if service_area.get("geo_target_constant_ids"):
            current_location["geo_target_constant_ids"] = copy.deepcopy(
                service_area["geo_target_constant_ids"]
            )
        if service_area.get("radius", {}).get("distance"):
            current_location["radius"] = copy.deepcopy(service_area["radius"])
        if service_area.get("exclusions"):
            current_location["exclusions"] = copy.deepcopy(service_area["exclusions"])
        base_url = website.get("landing_page_base_url")
        if base_url and "example.com" in str(campaign.get("final_url", "")):
            campaign["final_url"] = base_url

    assert_no_embedded_secrets(draft)
    assert_valid_campaign_plan(draft)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        yaml.safe_dump(draft, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Draft created: {output}")
    print("No external changes were made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
