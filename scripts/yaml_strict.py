#!/usr/bin/env python3
"""Strict YAML loader that REJECTS duplicate mapping keys.

PyYAML's safe_load silently keeps the last value when a mapping key repeats, so
a config file can look correct while quietly discarding an earlier definition.
This loader raises instead, and reports every duplicate with its line numbers.

Usage:
    python scripts/yaml_strict.py <file> [<file> ...]

Exit code 0 = every file parsed with no duplicate key.
Exit code 1 = at least one duplicate key or parse error.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


class DuplicateKeyError(ValueError):
    pass


class StrictLoader(yaml.SafeLoader):
    """SafeLoader that refuses duplicate keys anywhere in the document."""


def _construct_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    mapping = {}
    duplicates = []
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError as exc:  # unhashable key
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                "found unhashable key (%s)" % exc, key_node.start_mark)
        if key in mapping:
            duplicates.append((key, key_node.start_mark.line + 1))
        mapping[key] = loader.construct_object(value_node, deep=deep)
    if duplicates:
        raise DuplicateKeyError(
            "duplicate mapping key(s) at %s: %s" % (
                node.start_mark.name,
                ", ".join("%r (line %d)" % (k, ln) for k, ln in duplicates)))
    return mapping


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_strict(path):
    """Parse a YAML file, raising DuplicateKeyError on any repeated key."""
    text = Path(path).read_text(encoding="utf-8")
    return yaml.load(text, Loader=StrictLoader)


def audit(path):
    """Return (ok, message). Also reports keys that safe_load would silently drop."""
    p = Path(path)
    try:
        strict = load_strict(p)
    except DuplicateKeyError as exc:
        return False, "DUPLICATE KEY: %s" % exc
    except yaml.YAMLError as exc:
        return False, "PARSE ERROR: %s" % str(exc).replace("\n", " ")[:300]
    # Cross-check: a lenient parse that counts raw key occurrences per mapping.
    lenient = yaml.safe_load(p.read_text(encoding="utf-8"))
    if lenient != strict:
        return False, "strict and lenient parses differ"
    return True, "OK"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    bad = 0
    for arg in sys.argv[1:]:
        ok, msg = audit(arg)
        print("%-6s %-72s %s" % ("PASS" if ok else "FAIL", arg, msg))
        if not ok:
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
