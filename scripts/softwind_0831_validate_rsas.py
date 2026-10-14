#!/usr/bin/env python3
"""Validate every drafted RSA in the PLAN-R5 / PLAN-R6 files.

Checks Google Ads hard limits and Green Marketing copy policy. Local only; no API
call, no mutation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "clients/softwind-power-washing/plans"

HEADLINE_MAX = 30
DESCRIPTION_MAX = 90
PATH_MAX = 15

# Claims the client profile marks unverified. Substring match, case-insensitive.
FORBIDDEN = [
    r"\bbest\b", r"#1", r"\bno\.?\s*1\b", r"\blicens", r"\binsured\b", r"\bbonded\b",
    r"\bguarantee", r"\bwarrant", r"\byears?\s+(of\s+)?experience", r"\b\d+\+?\s*years\b",
    r"\b\d(\.\d)?\s*star", r"\breviews?\b", r"\brated\b", r"\bsame[- ]day\b",
    r"\b24/7\b", r"\bwithin\s+\d+\s*(hour|minute)", r"\bdiscount\b", r"\b\d+%\s*off\b",
    r"\bcheapest\b", r"\bhurry\b", r"\blimited\s+time\b", r"\bact\s+now\b",
    r"\bfree\s+estimate\s+guarantee", r"\bcertified\b", r"\baward\b",
]
PHONE = re.compile(r"\(?\b\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}\b")
NEAR_ME = re.compile(r"\bnear\s+me\b", re.I)


def check_ad(label: str, ad: dict) -> list[str]:
    errs: list[str] = []
    hs = ad.get("headlines", [])
    ds = ad.get("descriptions", [])
    if not 3 <= len(hs) <= 15:
        errs.append(f"{label}: headline count {len(hs)} outside 3..15")
    if not 2 <= len(ds) <= 4:
        errs.append(f"{label}: description count {len(ds)} outside 2..4")
    for i, h in enumerate(hs, 1):
        if len(h) > HEADLINE_MAX:
            errs.append(f"{label}: H{i} is {len(h)} chars (max {HEADLINE_MAX}) -> {h!r}")
    for i, d in enumerate(ds, 1):
        if len(d) > DESCRIPTION_MAX:
            errs.append(f"{label}: D{i} is {len(d)} chars (max {DESCRIPTION_MAX}) -> {d!r}")
    for key in ("path1", "path2"):
        v = ad.get(key) or ""
        if len(v) > PATH_MAX:
            errs.append(f"{label}: {key} is {len(v)} chars (max {PATH_MAX}) -> {v!r}")
    if len(set(hs)) != len(hs):
        dupes = sorted({h for h in hs if hs.count(h) > 1})
        errs.append(f"{label}: duplicate headlines {dupes}")
    if len(set(ds)) != len(ds):
        errs.append(f"{label}: duplicate descriptions")
    blob = " || ".join(hs + ds)
    for pat in FORBIDDEN:
        m = re.search(pat, blob, re.I)
        if m:
            errs.append(f"{label}: unsupported/forbidden claim {m.group(0)!r} (pattern {pat})")
    if PHONE.search(blob):
        errs.append(f"{label}: phone number in copy")
    if NEAR_ME.search(blob):
        errs.append(f"{label}: awkward 'near me' in copy - policy prefers 'near you'")
    if not ad.get("final_url", "").startswith("https://"):
        errs.append(f"{label}: final_url missing or not https")
    if ad.get("status") != "PAUSED":
        errs.append(f"{label}: status must be PAUSED at creation, got {ad.get('status')!r}")
    return errs


def collect(doc: dict) -> list[tuple[str, dict]]:
    out = []
    p = doc["change_plan"]
    for a in p.get("actions", []):
        if "ad" in a:
            out.append((f"{p['plan_id']}/{a['action_id']}", a["ad"]))
    return out


def main() -> int:
    errs: list[str] = []
    total = 0
    for path in sorted(PLANS.glob("2026-08-31-plan-r*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        ads = collect(doc)
        for label, ad in ads:
            total += 1
            e = check_ad(label, ad)
            errs.extend(e)
            hs = ad.get("headlines", [])
            ds = ad.get("descriptions", [])
            print(f"{label}: {len(hs)} headlines (max len {max(len(h) for h in hs)}), "
                  f"{len(ds)} descriptions (max len {max(len(d) for d in ds)}), "
                  f"path1={len(ad.get('path1') or '')} path2={len(ad.get('path2') or '')} "
                  f"-> {'OK' if not e else 'FAIL'}")
    print(f"\n{total} ads validated")
    if errs:
        print(f"{len(errs)} PROBLEM(S):")
        for e in errs:
            print("  -", e)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
