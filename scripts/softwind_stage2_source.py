#!/usr/bin/env python3
"""STAGE 2 - locate, copy unmodified, checksum and validate the client-approved
source file 'Location report (2).csv'.

Read-only with respect to Google Ads. The only write is a byte-for-byte copy of
the source file into the client sources directory.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "clients/softwind-power-washing"
SOURCES = CLIENT / "sources"
SNAP = CLIENT / "snapshots"
OUT = SNAP / "source-validation-2026-08-26.json"

SRC = Path("C:/Users/walte/Downloads/Location report (2).csv")
DEST = SOURCES / "Location report (2).csv"

EXPECTED = {"nonblank_location_rows": 78, "new_york_rows": 75,
            "named_new_york_locations": 44, "new_york_zip_codes": 31,
            "non_new_york_rows": 3, "duplicate_location_strings": 0}

EXPECTED_NON_NY = {
    "Kolkata, West Bengal, India",
    "Glenwood, Tennessee, United States",
    "Anchorage Municipality, Alaska, United States",
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    out = {"generated": "2026-08-26", "stage": 2}

    if not SRC.exists():
        print("SOURCE FILE NOT FOUND: %s" % SRC)
        return 1

    SOURCES.mkdir(parents=True, exist_ok=True)
    src_hash = sha256(SRC)
    shutil.copy2(SRC, DEST)          # byte-for-byte, preserves mtime
    dest_hash = sha256(DEST)

    out["source"] = {
        "found_at": str(SRC), "copied_to": str(DEST),
        "size_bytes": SRC.stat().st_size,
        "sha256_source": src_hash, "sha256_copy": dest_hash,
        "copy_is_byte_identical": src_hash == dest_hash,
        "modified": False}

    rows = list(csv.reader(DEST.open(encoding="utf-8-sig")))
    out["file_shape"] = {
        "raw_csv_rows": len(rows),
        "report_title": rows[0][0] if rows else None,
        "date_range": rows[1][0] if len(rows) > 1 else None,
        "column_header": rows[2] if len(rows) > 2 else None}

    data = [r for r in rows[3:] if r and r[0].strip()]
    totals = [r for r in rows[3:] if r and not r[0].strip()]
    locations = [r[0].strip() for r in data]

    def is_ny(s: str) -> bool:
        return s.endswith(", New York, United States")

    def is_zip(s: str) -> bool:
        return s.split(",")[0].strip().isdigit()

    ny = [s for s in locations if is_ny(s)]
    non_ny = [s for s in locations if not is_ny(s)]
    ny_zip = [s for s in ny if is_zip(s)]
    ny_named = [s for s in ny if not is_zip(s)]
    dupes = {s: c for s, c in Counter(locations).items() if c > 1}

    observed = {"nonblank_location_rows": len(locations),
                "new_york_rows": len(ny),
                "named_new_york_locations": len(ny_named),
                "new_york_zip_codes": len(ny_zip),
                "non_new_york_rows": len(non_ny),
                "duplicate_location_strings": len(dupes)}

    mismatches = {k: {"expected": EXPECTED[k], "observed": observed[k]}
                  for k in EXPECTED if EXPECTED[k] != observed[k]}
    non_ny_set = set(non_ny)
    non_ny_ok = non_ny_set == EXPECTED_NON_NY

    out["inventory"] = {"expected": EXPECTED, "observed": observed,
                        "mismatches": mismatches, "matches": not mismatches}
    out["non_new_york"] = {
        "observed": sorted(non_ny_set),
        "expected": sorted(EXPECTED_NON_NY),
        "exact_match": non_ny_ok,
        "disposition": "NOT_APPROVED_NON_NEW_YORK - never added to any plan"}
    out["duplicates"] = dupes
    out["total_rows_excluded_from_inventory"] = [r[1] for r in totals]
    out["performance_note"] = (
        "Every data row reports 0 clicks and 0 impressions, and the campaign "
        "total is 0. This export carries no delivery data, so it is a location "
        "LIST, not a performance record. It is used here strictly as the "
        "client-approved target inventory, which is what the owner designated it.")
    out["new_york_rows_ordered"] = ny

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("STAGE 2 - SOURCE FILE VALIDATION")
    print()
    print("  found at   : %s" % SRC)
    print("  copied to  : %s" % DEST)
    print("  size       : %d bytes" % SRC.stat().st_size)
    print("  sha256     : %s" % src_hash)
    print("  copy match : %s" % (src_hash == dest_hash))
    print()
    print("  title      : %s" % out["file_shape"]["report_title"])
    print("  date range : %s" % out["file_shape"]["date_range"])
    print()
    print("  %-32s %8s %8s  %s" % ("METRIC", "EXPECT", "OBSERVE", "OK"))
    for k in EXPECTED:
        print("  %-32s %8d %8d  %s"
              % (k, EXPECTED[k], observed[k],
                 "yes" if EXPECTED[k] == observed[k] else "NO"))
    print()
    print("  non-New-York rows (must not be added): exact_match=%s" % non_ny_ok)
    for s in sorted(non_ny_set):
        print("     %-52s %s" % (s, "expected" if s in EXPECTED_NON_NY else "UNEXPECTED"))
    print()
    if mismatches or not non_ny_ok:
        print("SOURCE FILE COUNT MISMATCH")
        for k, v in mismatches.items():
            print("   %s expected %s observed %s" % (k, v["expected"], v["observed"]))
        return 2
    print("SOURCE FILE VALIDATED - all six expected counts match exactly")
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
