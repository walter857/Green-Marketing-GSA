#!/usr/bin/env python3
"""Duplicate-key-aware YAML validation for the Softwind R-series plans.

Plain PyYAML silently keeps the LAST value when a mapping key repeats, so a file
can parse cleanly while carrying a stale duplicate that changes meaning. This
loader raises instead. Local only; no API call, no mutation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "clients" / "softwind-power-washing"


class DuplicateKeyError(ValueError):
    pass


class DupCheckLoader(yaml.SafeLoader):
    """SafeLoader that refuses a mapping containing a repeated key."""


def _no_duplicates(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            mark = key_node.start_mark
            raise DuplicateKeyError(
                f"duplicate key {key!r} at line {mark.line + 1}, column {mark.column + 1}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


DupCheckLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


def check(path: Path) -> tuple[bool, str, dict | None]:
    text = path.read_text(encoding="utf-8")
    try:
        doc = yaml.load(text, Loader=DupCheckLoader)
    except DuplicateKeyError as exc:
        return False, f"DUPLICATE KEY: {exc}", None
    except yaml.YAMLError as exc:
        return False, f"YAML ERROR: {str(exc)[:200]}", None
    return True, "ok", doc


def main() -> int:
    targets = [CLIENT / "client.yaml", CLIENT / "work-order.yaml"]
    targets += sorted((CLIENT / "plans").glob("2026-08-31-plan-r*.yaml"))

    failures = 0
    for p in targets:
        good, msg, doc = check(p)
        extra = ""
        if good and "plan" in p.name:
            cp = doc.get("change_plan", {})
            acts = cp.get("actions") or []
            extra = (f"  plan_id={cp.get('plan_id')} "
                     f"actions={len(acts)} "
                     f"declared_mut={cp.get('ads_mutation_count')} "
                     f"status={cp.get('approval_status')!r}/{cp.get('execution_status')!r}")
        flag = "PASS" if good else "FAIL"
        if not good:
            failures += 1
        print(f"  [{flag}] {p.name:52s} {msg}{extra}")

    print(f"\n{len(targets)} files checked, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
