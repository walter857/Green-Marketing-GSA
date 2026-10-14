#!/usr/bin/env python3
"""Inventory Google Ads write-capable Python entrypoints without running them."""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEARCH_ROOTS = ("scripts", "src")
METHOD_PREFIXES = ("mutate", "upload_", "apply_recommendation")
DENY_MARKER = "assert_legacy_writer_disabled"


def scan():
    findings = []
    for directory in SEARCH_ROOTS:
        for path in sorted((ROOT / directory).rglob("*.py")):
            if path.name == "security_inventory.py":
                continue
            source = path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source, filename=str(path))
            except SyntaxError as exc:
                findings.append({"path": path.relative_to(ROOT).as_posix(),
                                 "error": str(exc)})
                continue
            calls = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    method = node.func.attr
                    if method.startswith(METHOD_PREFIXES):
                        calls.append({"line": node.lineno, "method": method})
            if calls:
                findings.append({
                    "path": path.relative_to(ROOT).as_posix(),
                    "write_calls": calls,
                    "quarantined": DENY_MARKER in source,
                })
    return findings


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    findings = scan()
    legacy = [f for f in findings if f["path"].startswith("scripts/")
              and f["path"] not in {
                  "scripts/execute_approved_plan.py",
                  "scripts/publish_campaign.py",
                  "scripts/neg_execute.py",
              }]
    unquarantined = [f for f in legacy if not f.get("quarantined")]
    print(json.dumps({"write_surface_count": len(findings),
                      "legacy_write_surface_count": len(legacy),
                      "unquarantined_legacy_count": len(unquarantined),
                      "legacy_unquarantined_paths": [f["path"] for f in unquarantined]},
                     indent=2))
    return 1 if args.enforce and unquarantined else 0


if __name__ == "__main__":
    raise SystemExit(main())
