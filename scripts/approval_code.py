#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml
from gm_gsa.safety import approval_code
from gm_gsa.validators import assert_valid_campaign_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan")
    args = parser.parse_args()
    plan = load_yaml(args.plan)
    assert_valid_campaign_plan(plan)
    print(approval_code(plan))
    print("This code approves only the current normalized plan contents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

