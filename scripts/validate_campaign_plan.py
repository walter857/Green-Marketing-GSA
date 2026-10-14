#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml
from gm_gsa.safety import assert_no_embedded_secrets
from gm_gsa.validators import validate_campaign_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan")
    args = parser.parse_args()
    plan = load_yaml(args.plan)
    assert_no_embedded_secrets(plan)
    errors = validate_campaign_plan(plan)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: plan is safe to present for approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

