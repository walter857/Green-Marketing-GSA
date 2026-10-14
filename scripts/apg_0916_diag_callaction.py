#!/usr/bin/env python3
"""Diagnose which field WEBSITE_CALL / AD_CALL rejects. validate_only = NO durable write.

Object 1 is already live (7772803337). This script never touches it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, client, E  # noqa: E402

c = client()
svc = c.get_service("ConversionActionService")
E_TYPE = c.enums.ConversionActionTypeEnum
E_CAT = c.enums.ConversionActionCategoryEnum
E_STATUS = c.enums.ConversionActionStatusEnum
E_COUNT = c.enums.ConversionActionCountingTypeEnum
E_ATTR = c.enums.AttributionModelEnum


def err_detail(exc):
    out = []
    fail = getattr(exc, "failure", None)
    if fail is not None:
        for e in fail.errors:
            loc = ""
            if e.location and e.location.field_path_elements:
                loc = ".".join(x.field_name for x in e.location.field_path_elements)
            code = e.error_code
            which = code.WhichOneof("error_code") if hasattr(code, "WhichOneof") else "?"
            out.append(f"{which}: {e.message} @ FIELD_PATH='{loc}'")
    return out or [str(exc)[:200]]


def attempt(label, type_name, cat_name, include):
    """include = set of optional field names to set."""
    op = c.get_type("ConversionActionOperation")
    ca = op.create
    ca.name = f"ZZ DIAG DO NOT USE {label}"
    ca.type_ = getattr(E_TYPE, type_name)
    ca.category = getattr(E_CAT, cat_name)
    ca.status = E_STATUS.ENABLED
    if "primary_for_goal" in include:
        ca.primary_for_goal = False
    if "counting" in include:
        ca.counting_type = E_COUNT.ONE_PER_CLICK
    if "click_window" in include:
        ca.click_through_lookback_window_days = 30
    if "view_window" in include:
        ca.view_through_lookback_window_days = 1
    if "attribution" in include:
        ca.attribution_model_settings.attribution_model = E_ATTR.GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN
    if "value" in include:
        ca.value_settings.default_value = 0.0
        ca.value_settings.always_use_default_value = False
    if "duration" in include:
        ca.phone_call_duration_seconds = 60
    try:
        req = c.get_type("MutateConversionActionsRequest")
        req.customer_id = CID
        req.operations.append(op)
        req.validate_only = True
        svc.mutate_conversion_actions(request=req)
        print(f"  [OK  ] {label:<52} include={sorted(include)}")
        return True
    except Exception as exc:  # noqa: BLE001
        for d in err_detail(exc):
            print(f"  [FAIL] {label:<52} {d}")
        return False


ALL = {"primary_for_goal", "counting", "click_window", "view_window", "attribution", "value", "duration"}

for type_name, cat_name in [("WEBSITE_CALL", "PHONE_CALL_LEAD"), ("AD_CALL", "PHONE_CALL_LEAD")]:
    print(f"\n=== {type_name} / {cat_name} ===")
    print("  -- full field set (what the executor sent) --")
    attempt(f"{type_name} FULL", type_name, cat_name, set(ALL))

    print("  -- leave-one-out to find the offending field --")
    for drop in sorted(ALL):
        attempt(f"{type_name} minus {drop}", type_name, cat_name, ALL - {drop})

    print("  -- minimal --")
    attempt(f"{type_name} MINIMAL", type_name, cat_name, set())
    attempt(f"{type_name} MINIMAL+duration", type_name, cat_name, {"duration"})

print("\nNOTE: every call above used validate_only=True. No conversion action was created.")
