#!/usr/bin/env python3
"""Validate a client location-target manifest.

Read-only. Issues no API call and writes nothing.

The manifest exists because `client.yaml` carries a single `service_area.radius` object
and cannot represent several distinct proximity radii. This validator enforces the rules
that make that safe: every approved target is present, radii are untouched, coordinates
round-trip exactly, exact duplicates are reported rather than silently merged, and a
postal-code target may not claim resolution it has not had.

`named_targets` covers approved city, neighborhood, county and region targets, which are
neither a radius nor a postal code. They carry the same resolution discipline as postal
targets: a target may not claim RESOLVED without a geo target constant, a canonical name
and a targetable flag.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml  # noqa: E402

ALLOWED_RADIUS_UNITS = {"MILES", "KILOMETERS"}
ALLOWED_GEO_TYPES = {"PRESENCE", "PRESENCE_OR_INTEREST"}


def validate(document: dict) -> list[str]:
    errors: list[str] = []
    block = document.get("location_targets")
    if not isinstance(block, dict):
        return ["location_targets must be a mapping"]

    proximity = block.get("proximity_targets") or []
    postal = block.get("postal_code_targets") or []
    named = block.get("named_targets") or []

    declared = block.get("total_positive_targets")
    actual = len(proximity) + len(postal) + len(named)
    if declared != actual:
        errors.append(
            f"total_positive_targets is {declared} but {actual} targets are listed"
        )

    setting = block.get("geo_target_type_setting") or {}
    positive = str(setting.get("positive_geo_target_type", "")).strip()
    if positive not in ALLOWED_GEO_TYPES:
        errors.append("geo_target_type_setting.positive_geo_target_type is missing or invalid")
    elif positive != "PRESENCE":
        errors.append(
            "positive_geo_target_type must be PRESENCE. Presence-or-interest is not approved."
        )

    seen: dict[tuple, str] = {}
    for target in proximity:
        tid = target.get("id", "(unnamed)")
        for field in ("radius", "radius_units", "latitude", "longitude"):
            if target.get(field) in (None, ""):
                errors.append(f"{tid}: {field} is required")

        units = str(target.get("radius_units", "")).strip().upper()
        if units and units not in ALLOWED_RADIUS_UNITS:
            errors.append(f"{tid}: radius_units {units!r} is not a Google Ads unit")
        if units == "KILOMETERS":
            errors.append(
                f"{tid}: radius is in kilometers. The approved radii are in miles and "
                "must not be converted."
            )

        # Micro-degree fields must round-trip exactly, or a coordinate was altered.
        for axis in ("latitude", "longitude"):
            degrees = target.get(axis)
            micro = target.get(f"{axis}_micro_degrees")
            if degrees is None or micro is None:
                continue
            expected = round(float(degrees) * 1_000_000)
            if int(micro) != expected:
                errors.append(
                    f"{tid}: {axis}_micro_degrees is {micro} but {degrees} converts to "
                    f"{expected}. The coordinate was altered."
                )

        lat, lon = target.get("latitude"), target.get("longitude")
        if lat is not None and not (-90 <= float(lat) <= 90):
            errors.append(f"{tid}: latitude {lat} is out of range")
        if lon is not None and not (-180 <= float(lon) <= 180):
            errors.append(f"{tid}: longitude {lon} is out of range")

        key = (lat, lon, target.get("radius"), units)
        if key in seen:
            errors.append(
                f"{tid}: exactly duplicates {seen[key]}. Remove a duplicate only after a "
                "fresh read-only inventory confirms it."
            )
        else:
            seen[key] = tid

    for target in postal:
        tid = target.get("id", "(unnamed)")
        if not str(target.get("postal_code", "")).strip():
            errors.append(f"{tid}: postal_code is required")
        status = str(target.get("lookup_status", "")).strip().upper()
        resolved = target.get("geo_target_constant_resource_name")
        if status == "RESOLVED":
            for field in (
                "geo_target_constant_resource_name",
                "canonical_name",
                "resolved_country_code",
                "target_type",
                "targetable",
            ):
                if target.get(field) in (None, ""):
                    errors.append(f"{tid}: lookup_status is RESOLVED but {field} is empty")
            if target.get("targetable") is False:
                errors.append(f"{tid}: geo target constant is not targetable")
        elif status == "PENDING_API_ACCESS":
            if resolved:
                errors.append(
                    f"{tid}: lookup_status is PENDING_API_ACCESS but a resource name is set"
                )
        else:
            errors.append(f"{tid}: lookup_status must be RESOLVED or PENDING_API_ACCESS")

    seen_named: dict[str, str] = {}
    for target in named:
        tid = target.get("id", "(unnamed)")
        if not str(target.get("canonical_name", "")).strip():
            errors.append(f"{tid}: canonical_name is required")
        status = str(target.get("lookup_status", "")).strip().upper()
        if status == "RESOLVED":
            for field in (
                "geo_target_constant_resource_name",
                "canonical_name",
                "resolved_country_code",
                "target_type",
                "targetable",
            ):
                if target.get(field) in (None, ""):
                    errors.append(f"{tid}: lookup_status is RESOLVED but {field} is empty")
            if target.get("targetable") is False:
                errors.append(f"{tid}: geo target constant is not targetable")
        elif status == "PENDING_API_ACCESS":
            if target.get("geo_target_constant_resource_name"):
                errors.append(
                    f"{tid}: lookup_status is PENDING_API_ACCESS but a resource name is set"
                )
        else:
            errors.append(f"{tid}: lookup_status must be RESOLVED or PENDING_API_ACCESS")

        rn = str(target.get("geo_target_constant_resource_name", "")).strip()
        if rn:
            if rn in seen_named:
                errors.append(
                    f"{tid}: targets the same geo target constant as {seen_named[rn]}. "
                    "Remove a duplicate only after a fresh read-only inventory confirms it."
                )
            else:
                seen_named[rn] = tid

    # A named target and a postal target may legitimately overlap, for example a city and a
    # ZIP inside it. That is recorded, never silently merged, because the approved list is fixed.
    postal_rns = {
        str(t.get("geo_target_constant_resource_name", "")).strip()
        for t in postal
    } - {""}
    for rn in sorted(postal_rns & set(seen_named)):
        errors.append(
            f"{seen_named[rn]}: the same geo target constant {rn} appears as both a named "
            "target and a postal-code target"
        )

    supplied = block.get("as_supplied") or []
    if supplied and len(supplied) != actual:
        errors.append(
            f"as_supplied lists {len(supplied)} strings but {actual} targets are defined"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a client location-target manifest.")
    parser.add_argument("manifest")
    args = parser.parse_args()

    document = load_yaml(args.manifest)
    errors = validate(document)
    if errors:
        print("Location targets: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    block = document["location_targets"]
    proximity = block.get("proximity_targets") or []
    postal = block.get("postal_code_targets") or []
    named = block.get("named_targets") or []
    pending = [
        t for t in (postal + named)
        if str(t.get("lookup_status", "")).upper() == "PENDING_API_ACCESS"
    ]
    print(
        f"Location targets: PASS | {len(proximity)} proximity + {len(postal)} postal "
        f"+ {len(named)} named = {block.get('total_positive_targets')} positive | "
        f"{block['geo_target_type_setting']['positive_geo_target_type']}"
    )
    for target in proximity:
        print(
            f"  {target['id']}: {target['radius']} {target['radius_units']} @ "
            f"{target['latitude']}, {target['longitude']}"
        )
    for target in postal:
        print(f"  {target['id']}: postal {target['postal_code']} "
              f"-> {target.get('canonical_name', '')} [{target['lookup_status']}]")
    for target in named:
        print(f"  {target['id']}: {target.get('target_type', '?')} "
              f"{target.get('canonical_name', '')} [{target['lookup_status']}]")
    if pending:
        print(
            f"\nNOTE: {len(pending)} postal target(s) await a geo-target-constant lookup. "
            "The campaign cannot be built until they resolve."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
