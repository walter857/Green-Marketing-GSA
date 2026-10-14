#!/usr/bin/env python3
"""validate_only dry run of APG-0917-CALL-N ordinal 1 (the CALL asset).
Nothing is created. Proves the exact field set the API will accept.
Run leave-one-out on failure so a hidden second error cannot masquerade as one.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import CID, client  # noqa: E402

c = client()
SCHED = [("MONDAY", 8, 17), ("TUESDAY", 8, 17), ("WEDNESDAY", 8, 17),
         ("THURSDAY", 8, 17), ("FRIDAY", 8, 17), ("SATURDAY", 8, 12)]
CONV = f"customers/{CID}/conversionActions/7773013199"


def build(include=("schedule", "conv_action", "reporting_state")):
    op = c.get_type("AssetOperation")
    a = op.create
    a.call_asset.country_code = "US"
    a.call_asset.phone_number = "4022027261"
    if "reporting_state" in include:
        a.call_asset.call_conversion_reporting_state = (
            c.enums.CallConversionReportingStateEnum.USE_RESOURCE_LEVEL_CALL_CONVERSION_ACTION)
    if "conv_action" in include:
        a.call_asset.call_conversion_action = CONV
    if "schedule" in include:
        for day, sh, eh in SCHED:
            s = c.get_type("AdScheduleInfo")
            s.day_of_week = c.enums.DayOfWeekEnum[day]
            s.start_hour = sh
            s.end_hour = eh
            s.start_minute = c.enums.MinuteOfHourEnum.ZERO
            s.end_minute = c.enums.MinuteOfHourEnum.ZERO
            a.call_asset.ad_schedule_targets.append(s)
    return op


def run(include, label):
    req = c.get_type("MutateAssetsRequest")
    req.customer_id = CID
    req.operations.append(build(include))
    req.validate_only = True
    try:
        c.get_service("AssetService").mutate_assets(request=req)
        print(f"  [OK  ] {label}")
        return True
    except Exception as exc:  # noqa: BLE001
        msgs = []
        f = getattr(exc, "failure", None)
        if f:
            for e in f.errors:
                loc = ".".join(x.field_name for x in e.location.field_path_elements) \
                    if e.location and e.location.field_path_elements else ""
                msgs.append(f"{e.message} @ '{loc}'")
        print(f"  [FAIL] {label}: {' | '.join(msgs) or str(exc)[:300]}")
        return False


print("=" * 74 + "\nCALL-N ordinal 1 -- validate_only dry run\n" + "=" * 74)
full = ("schedule", "conv_action", "reporting_state")
ok = run(full, "full field set as planned")
if not ok:
    print("\n  leave-one-out bisection:")
    for drop in full:
        run(tuple(x for x in full if x != drop), f"without {drop}")
    run((), "bare country_code + phone_number only")
print("\nNo asset was created. validate_only = True on every request.")
sys.exit(0 if ok else 1)
