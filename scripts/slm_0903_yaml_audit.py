#!/usr/bin/env python3
"""Key-by-key audit of the Softwind L&M client.yaml.

Answers the pre-approval QA gate's specific questions:
  - does any mapping key appear more than once, anywhere?
  - are the named keys present, and what shape is each one?
  - is verified_usps defined twice (inline empty list plus block list)?
  - are lists structurally valid?
  - are Google Ads facts separated from unconfirmed business claims?

Read-only. Reports; changes nothing.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from yaml_strict import DuplicateKeyError, load_strict  # noqa: E402

TARGET = ROOT / "clients/softwind-landscape-masonry/client.yaml"

NAMED = [
    "client.google_ads.live_campaigns",
    "client.identity_gate.per_account_confirmation_date",
    "client.identity_gate.per_account_confirmation_checks.name_match",
    "client.identity_gate.per_account_confirmation_checks.id_match",
    "client.offer.services_excluded",
    "client.offer.verified_usps",
    "client.service_area.geo_target_constant_ids",
    "client.service_area.exclusions",
]


def walk(node, prefix=""):
    """Yield (dotted_path, value) for every key in the document."""
    if isinstance(node, dict):
        for k, v in node.items():
            p = "%s.%s" % (prefix, k) if prefix else str(k)
            yield p, v
            yield from walk(v, p)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, "%s[%d]" % (prefix, i))


def raw_key_occurrences(text):
    """Count every `key:` occurrence per indent-scope, straight from the text.

    This is independent of any YAML parser, so it catches a duplicate even if a
    loader would have merged it.
    """
    stack, counts = [], {}
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^(\s*)(-\s+)?([A-Za-z_][\w.\-]*)\s*:(\s|$)", line)
        if not m:
            continue
        indent = len(m.group(1)) + (len(m.group(2)) if m.group(2) else 0)
        key = m.group(3)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = ".".join([s[1] for s in stack] + [key])
        # A list item resets the sibling scope, so scope the count by item index.
        if m.group(2):
            path = path + "#item"
        counts.setdefault(path, []).append(lineno)
        stack.append((indent, key))
    return counts


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    print("FILE: %s" % TARGET.relative_to(ROOT))
    print("bytes=%d lines=%d" % (len(text.encode()), len(text.splitlines())))

    print("\n--- 1. STRICT PARSE (duplicate keys rejected) ---")
    try:
        doc = load_strict(TARGET)
        print("  PASS - no duplicate mapping key anywhere in the document")
    except DuplicateKeyError as exc:
        print("  FAIL - %s" % exc)
        return 1

    print("\n--- 2. PARSER-INDEPENDENT TEXT SCAN ---")
    dupes = {k: v for k, v in raw_key_occurrences(text).items() if len(v) > 1}
    real = {k: v for k, v in dupes.items() if not k.endswith("#item")}
    if real:
        print("  FAIL - repeated key paths:")
        for k, v in sorted(real.items()):
            print("     %-60s lines %s" % (k, v))
        return 1
    print("  PASS - no key path repeats within its own mapping scope")
    if dupes:
        print("  (%d repeats are list-item keys in sibling records, which is legal)"
              % len(dupes))

    print("\n--- 3. THE SPECIFICALLY NAMED KEYS ---")
    flat = dict(walk(doc))
    for path in NAMED:
        if path in flat:
            v = flat[path]
            kind = type(v).__name__
            shown = v if not isinstance(v, (list, dict)) else (
                "%s(len=%d) %s" % (kind, len(v), v if len(str(v)) < 90 else "..."))
            print("  PRESENT  %-62s %s" % (path, shown))
        else:
            print("  ABSENT   %-62s (key does not exist in this file)" % path)

    print("\n--- 4. verified_usps SHAPE CHECK ---")
    occurrences = [(i + 1, l) for i, l in enumerate(text.splitlines())
                   if re.match(r"^\s*verified_usps\s*:", l)]
    print("  textual occurrences of 'verified_usps:' = %d" % len(occurrences))
    for ln, l in occurrences:
        print("     line %-4d %r" % (ln, l))
    v = flat.get("client.offer.verified_usps", "<<absent>>")
    print("  parsed value: %r (type %s)" % (v, type(v).__name__))
    if len(occurrences) == 1 and isinstance(v, list):
        print("  PASS - defined exactly once, as a list. No inline/block conflict.")

    print("\n--- 5. LIST STRUCTURAL VALIDITY ---")
    bad = 0
    for path, val in walk(doc):
        if isinstance(val, list):
            for i, item in enumerate(val):
                if item is None:
                    print("  FAIL %s[%d] is null (empty list item)" % (path, i))
                    bad += 1
    print("  PASS - every list item is a real value" if not bad
          else "  FAIL - %d empty list item(s)" % bad)

    print("\n--- 6. UNKNOWN PRESERVATION ---")
    unknowns = [(p, v) for p, v in walk(doc) if v == "UNKNOWN"]
    print("  %d fields still explicitly UNKNOWN:" % len(unknowns))
    for p, _ in unknowns:
        print("     %s" % p)

    print("\n--- 7. FACT vs UNCONFIRMED-CLAIM SEPARATION ---")
    buckets = {
        "google_ads facts (read live)": "client.google_ads",
        "identity gate (read live)": "client.identity_gate",
        "approved services": "client.offer.services_in_scope",
        "excluded - sibling account scope": "client.offer.services_excluded",
        "excluded - pending confirmation": "client.offer.services_excluded_pending_confirmation",
        "unresolved - never negate or promote": "client.offer.services_unresolved",
        "claims banned until verified": "client.offer.unverified_claims_do_not_use",
    }
    for label, path in buckets.items():
        v = flat.get(path)
        n = len(v) if isinstance(v, (list, dict)) else ("absent" if v is None else 1)
        print("  %-40s %-58s %s" % (label, path, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
