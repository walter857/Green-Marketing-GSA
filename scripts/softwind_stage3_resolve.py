#!/usr/bin/env python3
"""STAGE 3 - resolve every approved New York row against current Google Ads geo
target constants. SELECT / suggest only. No mutations.

Matching is EXACT on canonical name. A row that does not produce an exact
canonical match is reported UNRESOLVED. It is never silently replaced with a
similarly named location.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available          # noqa: E402
from gm_gsa.credentials import load_google_ads_client       # noqa: E402
from gm_gsa.google_ads import enum_name                     # noqa: E402

CID = "1521725229"
CAMPAIGNS = {"24103511039": "Power Washing", "24145053510": "Power Washing #2"}
CLIENT = ROOT / "clients/softwind-power-washing"
SNAP = CLIENT / "snapshots"
SRC = CLIENT / "sources/Location report (2).csv"
OUT = SNAP / "stage3-geo-resolution-2026-08-26.json"

Q_GEO = """
SELECT geo_target_constant.id, geo_target_constant.name,
       geo_target_constant.canonical_name, geo_target_constant.status,
       geo_target_constant.target_type, geo_target_constant.country_code,
       geo_target_constant.parent_geo_target
FROM geo_target_constant
WHERE geo_target_constant.resource_name IN (%s)
"""


def norm(s: str) -> str:
    return ",".join(p.strip() for p in s.split(",")).lower()


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    svc = client.get_service("GoogleAdsService")
    gts = client.get_service("GeoTargetConstantService")

    rows = list(csv.reader(SRC.open(encoding="utf-8-sig")))
    data = [r[0].strip() for r in rows[3:] if r and r[0].strip()]
    ny = [s for s in data if s.endswith(", New York, United States")]
    non_ny = [s for s in data if not s.endswith(", New York, United States")]
    assert len(ny) == 75, "expected 75 New York rows, got %d" % len(ny)

    # ---- current live criteria ----------------------------------------
    state = json.loads((SNAP / "stage1-state-2026-08-26.json").read_text("utf-8"))
    live = {c: {p["geo_target_constant_id"] for p in
                state["location_criteria"][c]["positive"]} for c in CAMPAIGNS}

    # ---- suggest, batched ----------------------------------------------
    suggestions = {}
    names = [s.split(",")[0].strip() for s in ny]
    uniq = list(dict.fromkeys(names))
    for i in range(0, len(uniq), 25):
        batch = uniq[i:i + 25]
        req = client.get_type("SuggestGeoTargetConstantsRequest")
        req.locale = "en"
        req.country_code = "US"
        req.location_names.names.extend(batch)
        for attempt in range(4):
            try:
                resp = gts.suggest_geo_target_constants(request=req)
                for s in resp.geo_target_constant_suggestions:
                    g = s.geo_target_constant
                    suggestions.setdefault(norm(g.canonical_name), []).append({
                        "id": str(g.id), "name": g.name,
                        "canonical_name": g.canonical_name,
                        "target_type": g.target_type,
                        "status": enum_name(g.status),
                        "country_code": g.country_code,
                        "reach": int(s.reach) if s.reach else None})
                break
            except Exception as exc:                        # noqa: BLE001
                if attempt == 3:
                    print("   suggest failed for batch %d: %s" % (i, str(exc)[:160]))
                else:
                    time.sleep(2 * (attempt + 1))
        time.sleep(0.3)

    # ---- resolve each row exactly ---------------------------------------
    resolved, unresolved, seen_ids = [], [], {}
    for src in ny:
        key = norm(src)
        cands = suggestions.get(key, [])
        enabled = [c for c in cands if c["status"] == "ENABLED"]
        uniq_ids = {c["id"] for c in enabled}
        if not enabled:
            unresolved.append({"source_row": src, "reason":
                               "no ENABLED constant with an exact canonical match",
                               "candidates_seen": len(cands)})
            continue
        if len(uniq_ids) > 1:
            unresolved.append({"source_row": src, "reason":
                               "ambiguous - %d distinct constants share this exact "
                               "canonical name" % len(uniq_ids),
                               "ids": sorted(uniq_ids)})
            continue
        g = enabled[0]
        resolved.append({"source_row": src, **g})
        seen_ids.setdefault(g["id"], []).append(src)

    # ---- enrich with parent + campaign membership -----------------------
    ids = sorted({r["id"] for r in resolved})
    parents = {}
    for i in range(0, len(ids), 50):
        cond = ",".join("'geoTargetConstants/%s'" % x for x in ids[i:i + 50])
        for row in svc.search(customer_id=CID, query=Q_GEO % cond):
            g = row.geo_target_constant
            parents[str(g.id)] = (g.parent_geo_target.split("/")[-1]
                                  if g.parent_geo_target else None)

    table, add_ids = [], []
    for r in resolved:
        gid = r["id"]
        dup = len(seen_ids[gid]) > 1
        in_a = gid in live["24103511039"]
        in_b = gid in live["24145053510"]
        is_ny = ",New York,United States" in r["canonical_name"]
        first_for_id = seen_ids[gid][0] == r["source_row"]
        if not is_ny:
            action = "NOT_APPROVED_NON_NEW_YORK"
        elif r["status"] != "ENABLED":
            action = "INVALID"
        elif dup and not first_for_id:
            action = "NO_ACTION_DUPLICATE"
        elif in_a and in_b:
            action = "KEEP_EXISTING"
        else:
            action = "ADD_TO_BOTH"
            add_ids.append(gid)
        table.append({
            "source_row": r["source_row"], "geo_target_constant_id": gid,
            "current_google_name": r["name"],
            "canonical_name": r["canonical_name"],
            "target_type": r["target_type"], "status": r["status"],
            "parent_geo_target_id": parents.get(gid),
            "new_york_confirmed": is_ny,
            "existing_in_campaign_A": in_a, "existing_in_campaign_B": in_b,
            "duplicate_target_id": dup,
            "duplicate_of_rows": seen_ids[gid] if dup else None,
            "proposed_action": action})
    for u in unresolved:
        table.append({"source_row": u["source_row"],
                      "geo_target_constant_id": None,
                      "current_google_name": None, "canonical_name": None,
                      "target_type": None, "status": None,
                      "parent_geo_target_id": None, "new_york_confirmed": None,
                      "existing_in_campaign_A": False,
                      "existing_in_campaign_B": False,
                      "duplicate_target_id": False, "duplicate_of_rows": None,
                      "proposed_action": "UNRESOLVED",
                      "unresolved_reason": u["reason"]})

    add_unique = sorted(set(add_ids))

    # ---- live targets NOT present in the approved CSV -------------------
    csv_ids = {r["id"] for r in resolved}
    disc = []
    all_live = sorted(live["24103511039"] | live["24145053510"])
    if all_live:
        cond = ",".join("'geoTargetConstants/%s'" % x for x in all_live)
        for row in svc.search(customer_id=CID, query=Q_GEO % cond):
            g = row.geo_target_constant
            if str(g.id) not in csv_ids:
                disc.append({"geo_target_constant_id": str(g.id),
                             "canonical_name": g.canonical_name,
                             "target_type": g.target_type,
                             "in_campaign_A": str(g.id) in live["24103511039"],
                             "in_campaign_B": str(g.id) in live["24145053510"],
                             "disposition": "KEEP UNCHANGED - not in the approved "
                                            "CSV, but removal needs its own approval"})

    counts = {a: sum(1 for t in table if t["proposed_action"] == a)
              for a in ("KEEP_EXISTING", "ADD_TO_BOTH", "NO_ACTION_DUPLICATE",
                        "UNRESOLVED", "INVALID", "NOT_APPROVED_NON_NEW_YORK")}

    out = {"generated": "2026-08-26", "stage": 3,
           "source_file": str(SRC),
           "source_sha256": json.loads(
               (SNAP / "source-validation-2026-08-26.json").read_text("utf-8")
           )["source"]["sha256_source"],
           "new_york_rows": len(ny),
           "non_new_york_rows_excluded": non_ny,
           "resolution_table": table,
           "action_counts": counts,
           "unique_new_target_ids": add_unique,
           "unique_new_target_count": len(add_unique),
           "existing_live_targets_not_in_csv": disc,
           "matching_rule": ("EXACT canonical-name match, case and whitespace "
                             "normalised. No fuzzy or nearest-name substitution."),
           "dedupe_rule": "Only EXACT duplicate geo target constant IDs are skipped."}
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("STAGE 3 - GEO RESOLUTION")
    print("  New York source rows      : %d" % len(ny))
    print("  Resolved to a constant    : %d" % len(resolved))
    print("  Unresolved                : %d" % len(unresolved))
    print()
    for a, n in counts.items():
        print("     %-28s %d" % (a, n))
    print()
    print("  Unique NET-NEW target ids : %d" % len(add_unique))
    print()
    dups = [t for t in table if t["duplicate_target_id"]]
    if dups:
        print("  EXACT DUPLICATE TARGET IDS (collapsed, %d rows affected)" % len(dups))
        shown = set()
        for t in dups:
            if t["geo_target_constant_id"] in shown:
                continue
            shown.add(t["geo_target_constant_id"])
            print("     %-10s %-40s <- %s"
                  % (t["geo_target_constant_id"], t["canonical_name"],
                     t["duplicate_of_rows"]))
        print()
    if unresolved:
        print("  UNRESOLVED ROWS (never substituted)")
        for u in unresolved:
            print("     %-46s %s" % (u["source_row"], u["reason"]))
        print()
    print("  EXISTING LIVE TARGETS NOT IN THE APPROVED CSV: %d" % len(disc))
    for d in disc:
        print("     %-10s %-44s A=%s B=%s  KEEP"
              % (d["geo_target_constant_id"], d["canonical_name"],
                 d["in_campaign_A"], d["in_campaign_B"]))
    print()
    print("wrote %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
