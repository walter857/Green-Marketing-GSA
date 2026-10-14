#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml
from gm_gsa.validators import assert_valid_campaign_plan


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def asset_text(asset: object) -> str:
    return str(asset.get("text", "")) if isinstance(asset, dict) else str(asset)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    plan = load_yaml(args.plan)
    assert_valid_campaign_plan(plan)
    output_dir = Path(args.output_dir)
    campaign_rows = []
    group_rows = []
    keyword_rows = []
    ad_rows = []

    for campaign in plan["campaigns"]:
        campaign_rows.append(
            {
                "Campaign": campaign["name"],
                "Campaign status": "Paused",
                "Campaign type": "Search",
                "Budget": campaign["daily_budget"],
                "Budget type": "Daily",
                "Networks": "Google Search",
            }
        )
        for group in campaign["ad_groups"]:
            group_rows.append(
                {
                    "Campaign": campaign["name"],
                    "Ad group": group["name"],
                    "Ad group status": "Paused",
                }
            )
            for keyword in group["keywords"]:
                keyword_rows.append(
                    {
                        "Campaign": campaign["name"],
                        "Ad group": group["name"],
                        "Keyword": keyword["text"],
                        "Match type": keyword["match_type"].title(),
                        "Status": "Enabled",
                        "Final URL": campaign["final_url"],
                    }
                )
            for ad in group["ads"]:
                row = {
                    "Campaign": campaign["name"],
                    "Ad group": group["name"],
                    "Ad status": "Paused",
                    "Final URL": campaign["final_url"],
                    "Path 1": group.get("path1", ""),
                    "Path 2": group.get("path2", ""),
                }
                for index, headline in enumerate(ad["headlines"], 1):
                    row[f"Headline {index}"] = asset_text(headline)
                for index, description in enumerate(ad["descriptions"], 1):
                    row[f"Description {index}"] = asset_text(description)
                ad_rows.append(row)

    write_rows(
        output_dir / "campaigns.csv",
        ["Campaign", "Campaign status", "Campaign type", "Budget", "Budget type", "Networks"],
        campaign_rows,
    )
    write_rows(
        output_dir / "ad-groups.csv",
        ["Campaign", "Ad group", "Ad group status"],
        group_rows,
    )
    write_rows(
        output_dir / "keywords.csv",
        ["Campaign", "Ad group", "Keyword", "Match type", "Status", "Final URL"],
        keyword_rows,
    )
    ad_fields = (
        ["Campaign", "Ad group", "Ad status"]
        + [f"Headline {index}" for index in range(1, 16)]
        + [f"Description {index}" for index in range(1, 5)]
        + ["Final URL", "Path 1", "Path 2"]
    )
    write_rows(output_dir / "responsive-search-ads.csv", ad_fields, ad_rows)
    print(f"Editor CSV set created in: {output_dir}")
    print("Review the Google Ads Editor column mapping before posting changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

