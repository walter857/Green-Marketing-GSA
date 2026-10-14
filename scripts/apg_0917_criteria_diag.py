#!/usr/bin/env python3
"""Diagnose the campaign_criterion count discrepancy (expected 90, observed 93).
Read-only."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apg_lib import client, q, E  # noqa: E402

c = client()
rows = q(c, """SELECT campaign_criterion.criterion_id, campaign_criterion.type,
                      campaign_criterion.negative, campaign_criterion.display_name,
                      campaign_criterion.keyword.text, campaign_criterion.keyword.match_type,
                      campaign_criterion.location.geo_target_constant,
                      campaign_criterion.language.language_constant,
                      campaign_criterion.status
               FROM campaign_criterion""")
print(f"TOTAL campaign_criterion rows: {len(rows)}\n")

by_type = Counter(E(x.campaign_criterion.type_) for x in rows)
for k, v in sorted(by_type.items()):
    print(f"  {k:<28} {v}")

print("\nNEGATIVE keywords by match type:")
negkw = [x.campaign_criterion for x in rows
         if E(x.campaign_criterion.type_) == "KEYWORD" and x.campaign_criterion.negative]
print("  ", dict(Counter(E(k.keyword.match_type) for k in negkw)), " total:", len(negkw))

print("\nNon-keyword, non-location, non-language rows (the likely +3):")
for x in rows:
    cr = x.campaign_criterion
    t = E(cr.type_)
    if t not in ("KEYWORD", "LOCATION", "LANGUAGE"):
        print(f"  criterion_id={cr.criterion_id}  type={t}  negative={cr.negative} "
              f"status={E(cr.status)}  display_name='{cr.display_name}'")

print("\nPOSITIVE keywords at campaign level (should be 0):")
poskw = [x.campaign_criterion for x in rows
         if E(x.campaign_criterion.type_) == "KEYWORD" and not x.campaign_criterion.negative]
print(f"  {len(poskw)}")

print("\nLOCATION rows:", sum(1 for x in rows if E(x.campaign_criterion.type_) == "LOCATION"))
print("LANGUAGE rows:", sum(1 for x in rows if E(x.campaign_criterion.type_) == "LANGUAGE"))
