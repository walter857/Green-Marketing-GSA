#!/usr/bin/env python3
"""Build PLAN-GA-LAUNCH-1, validate it, run validate_only, and fingerprint it.

validate_only=True is set on the request message. NO resource is created.
"""
from __future__ import annotations

import csv
import glob
import hashlib
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gm_gsa.config import load_dotenv_if_available, normalize_customer_id  # noqa: E402
from gm_gsa.credentials import load_google_ads_client  # noqa: E402
from gm_gsa.safety import approval_code  # noqa: E402

CID = "1521725229"
SURVIVOR = "24103511039"
AUD = ROOT / "clients/softwind-power-washing/audits"
PLN = ROOT / "clients/softwind-power-washing/plans"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"

# Reuse the authoritative RSA copy and group config from the 2026-09-01 build. Not rebuilt.
spec = importlib.util.spec_from_file_location(
    "rec", ROOT / "scripts/softwind_0901_build_recovery_program.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
GROUPS, RSA, BANNED = rec.GROUPS, rec.RSA, rec.BANNED

delta = json.loads(Path(sorted(glob.glob(str(SNAP / "launch1-delta-*.json")))[-1])
                   .read_text(encoding="utf-8"))
D = delta["delta"]
errors: list[str] = []


def rsa_validate():
    rows = []
    for g, cfg in GROUPS.items():
        for ad in RSA[g]:
            hs, ds = ad["h"], ad["d"]
            for x in hs:
                if len(x) > 30:
                    errors.append(f"{g} RSA{ad['n']} headline {len(x)}>30: {x}")
            for x in ds:
                if len(x) > 90:
                    errors.append(f"{g} RSA{ad['n']} description {len(x)}>90")
            for p in (cfg["p1"], cfg["p2"]):
                if len(p) > 15:
                    errors.append(f"{g} path >15: {p}")
            if len(set(hs)) != len(hs):
                errors.append(f"{g} RSA{ad['n']} duplicate headline")
            if len(set(ds)) != len(ds):
                errors.append(f"{g} RSA{ad['n']} duplicate description")
            blob = " ".join(hs + ds).lower()
            for b in BANNED:
                if b in blob:
                    errors.append(f"{g} RSA{ad['n']} banned claim: {b}")
            if any(ch.isdigit() for ch in blob):
                errors.append(f"{g} RSA{ad['n']} digit found (phone guard)")
            if "near me" in blob:
                errors.append(f"{g} RSA{ad['n']} awkward 'near me' copy")
            canon = g.split()[0].lower()
            svc = sum(1 for x in hs if canon in x.lower())
            loc = sum(1 for x in hs if any(k in x for k in
                                           ("Long Island", "Nassau", "Suffolk", "Local", "Near You")))
            off = sum(1 for x in hs if "Free" in x or "Quote" in x or "Estimate" in x)
            if not 3 <= svc <= 8:
                errors.append(f"{g} RSA{ad['n']} service token in {svc} headlines")
            if loc < 2:
                errors.append(f"{g} RSA{ad['n']} local headlines {loc} < 2")
            if off < 2:
                errors.append(f"{g} RSA{ad['n']} offer headlines {off} < 2")
            if not any(canon in d.lower() for d in ds):
                errors.append(f"{g} RSA{ad['n']} service absent from all descriptions")
            rows.append({
                "ad_group": g, "ad_group_id": cfg["ad_group_id"], "rsa": f"RSA {ad['n']}",
                "angle": ad["angle"], "status_on_create": "PAUSED",
                "final_url": cfg["page"], "path1": cfg["p1"], "path2": cfg["p2"],
                "headlines": len(hs), "descriptions": len(ds),
                "max_headline_len": max(len(x) for x in hs),
                "max_description_len": max(len(x) for x in ds),
                "service_headlines": svc, "local_headlines": loc, "offer_headlines": off,
                "pinning": "NONE", "duplicate_headlines": 0, "duplicate_descriptions": 0,
                "banned_claims": 0, "digits_present": "NO", "near_me_copy": "NO",
                **{f"H{i+1}": hs[i] for i in range(len(hs))},
                **{f"H{i+1}_len": len(hs[i]) for i in range(len(hs))},
                **{f"D{i+1}": ds[i] for i in range(len(ds))},
                **{f"D{i+1}_len": len(ds[i]) for i in range(len(ds))},
            })
    for g in GROUPS:
        a, b = set(RSA[g][0]["h"]), set(RSA[g][1]["h"])
        ov = len(a & b) / max(len(a | b), 1)
        if ov > 0.20:
            errors.append(f"{g} RSA1/RSA2 headline overlap {ov:.0%} > 20%")
        if set(RSA[g][0]["d"]) & set(RSA[g][1]["d"]):
            errors.append(f"{g} RSA1/RSA2 share a description")
    return rows


def main() -> int:
    rsa_rows = rsa_validate()
    kw_new = D["keywords_to_create"]
    kw_reuse = D["keywords_reuse"]
    if len(kw_new) != 28:
        errors.append(f"expected 28 keywords to create, got {len(kw_new)}")
    if len(rsa_rows) != 12:
        errors.append(f"expected 12 RSAs, got {len(rsa_rows)}")
    if D and [r for r in D["ad_groups"] if r["action"] != "REUSE EXISTING"]:
        errors.append("an ad group would need creating - architecture drift")
    blocking = [c for c in D["conflicts"] if "Displaced duplicate" not in c]
    if blocking:
        errors.extend(blocking)

    load_dotenv_if_available(ROOT / ".env")
    client = load_google_ads_client()
    cid = normalize_customer_id(CID)
    ag_svc = client.get_service("AdGroupService")

    # ---------------- build the exact create payload ----------------
    kw_ops = []
    for r in kw_new:
        op = client.get_type("AdGroupCriterionOperation")
        c = op.create
        c.ad_group = ag_svc.ad_group_path(cid, r["ad_group_id"])
        c.status = client.enums.AdGroupCriterionStatusEnum.PAUSED
        c.keyword.text = r["text"]
        c.keyword.match_type = getattr(client.enums.KeywordMatchTypeEnum, r["match_type"])
        kw_ops.append(op)

    ad_ops = []
    for g, cfg in GROUPS.items():
        for ad in RSA[g]:
            op = client.get_type("AdGroupAdOperation")
            a = op.create
            a.ad_group = ag_svc.ad_group_path(cid, cfg["ad_group_id"])
            a.status = client.enums.AdGroupAdStatusEnum.PAUSED
            a.ad.final_urls.append(cfg["page"])
            rsa = a.ad.responsive_search_ad
            rsa.path1 = cfg["p1"]
            rsa.path2 = cfg["p2"]
            for h in ad["h"]:
                asset = client.get_type("AdTextAsset")
                asset.text = h
                rsa.headlines.append(asset)
            for d in ad["d"]:
                asset = client.get_type("AdTextAsset")
                asset.text = d
                rsa.descriptions.append(asset)
            ad_ops.append(op)

    # ---------------- validate_only ----------------
    vo = {"applicable": True, "keyword_request": None, "ad_request": None}
    try:
        req = client.get_type("MutateAdGroupCriteriaRequest")
        req.customer_id = cid
        req.operations.extend(kw_ops)
        req.validate_only = True
        req.partial_failure = False
        client.get_service("AdGroupCriterionService").mutate_ad_group_criteria(request=req)
        vo["keyword_request"] = f"PASS - {len(kw_ops)} keyword operations validated, 0 created"
    except Exception as exc:
        vo["keyword_request"] = f"FAIL - {str(exc)[:600]}"
        errors.append("validate_only FAILED for keywords")
    try:
        req2 = client.get_type("MutateAdGroupAdsRequest")
        req2.customer_id = cid
        req2.operations.extend(ad_ops)
        req2.validate_only = True
        req2.partial_failure = False
        client.get_service("AdGroupAdService").mutate_ad_group_ads(request=req2)
        vo["ad_request"] = f"PASS - {len(ad_ops)} RSA operations validated, 0 created"
    except Exception as exc:
        vo["ad_request"] = f"FAIL - {str(exc)[:900]}"
        errors.append("validate_only FAILED for RSAs")
    vo["resources_created"] = 0
    print("VALIDATE_ONLY:", json.dumps(vo, indent=2))

    # ---------------- CSV outputs ----------------
    inv = []
    for r in D["ad_groups"]:
        inv.append({"resource_type": "AD_GROUP", "final_group": r["final_group"],
                    "resource_id": r["ad_group_id"], "live_name": r["live_name"],
                    "current_state": r["live_status"], "proposed_state": "UNCHANGED (reuse)",
                    "action": "REUSE EXISTING", "keyword_text": "", "match_type": "",
                    "final_url": GROUPS[r["final_group"]]["page"], "in_plan": "NO"})
    for r in kw_reuse:
        inv.append({"resource_type": "KEYWORD", "final_group": r["final_group"],
                    "resource_id": r["ad_group_id"], "live_name": "",
                    "current_state": r.get("existing_status"), "proposed_state": "UNCHANGED",
                    "action": "REUSE EXISTING", "keyword_text": r["text"],
                    "match_type": r["match_type"], "final_url": r["landing_page"], "in_plan": "NO"})
    for r in kw_new:
        inv.append({"resource_type": "KEYWORD", "final_group": r["final_group"],
                    "resource_id": r["ad_group_id"], "live_name": "",
                    "current_state": "DOES NOT EXIST", "proposed_state": "PAUSED",
                    "action": "CREATE PAUSED", "keyword_text": r["text"],
                    "match_type": r["match_type"], "final_url": r["landing_page"], "in_plan": "YES"})
    for r in rsa_rows:
        inv.append({"resource_type": "RSA", "final_group": r["ad_group"],
                    "resource_id": r["ad_group_id"], "live_name": r["rsa"],
                    "current_state": "DOES NOT EXIST", "proposed_state": "PAUSED",
                    "action": "CREATE PAUSED", "keyword_text": "", "match_type": "",
                    "final_url": r["final_url"], "in_plan": "YES"})
    with (AUD / "2026-09-02-final-launch-resource-inventory.csv").open(
            "w", newline="", encoding="utf-8") as fh:
        wtr = csv.DictWriter(fh, fieldnames=list(inv[0].keys()))
        wtr.writeheader()
        wtr.writerows(inv)

    with (AUD / "2026-09-02-final-rsa-launch-qa.csv").open(
            "w", newline="", encoding="utf-8") as fh:
        keys = sorted({k for r in rsa_rows for k in r})
        order = [k for k in ["ad_group", "ad_group_id", "rsa", "angle", "status_on_create",
                             "final_url", "path1", "path2", "headlines", "descriptions",
                             "max_headline_len", "max_description_len", "service_headlines",
                             "local_headlines", "offer_headlines", "pinning",
                             "duplicate_headlines", "duplicate_descriptions", "banned_claims",
                             "digits_present", "near_me_copy"] if k in keys]
        order += [k for k in keys if k not in order]
        wtr = csv.DictWriter(fh, fieldnames=order)
        wtr.writeheader()
        wtr.writerows(rsa_rows)

    own = []
    for g, cfg in GROUPS.items():
        for t in cfg["texts"]:
            exists = {(x["text"], x["match_type"]) for x in kw_reuse
                      if x["ad_group_id"] == cfg["ad_group_id"]}
            own.append({"keyword_text": t, "owner_ad_group": g,
                        "owner_ad_group_id": cfg["ad_group_id"],
                        "match_types": "PHRASE + EXACT",
                        "phrase_action": "REUSE" if (t, "PHRASE") in exists else "CREATE PAUSED",
                        "exact_action": "REUSE" if (t, "EXACT") in exists else "CREATE PAUSED",
                        "landing_page": cfg["page"], "path1": cfg["p1"], "path2": cfg["p2"],
                        "unique_owner": "YES"})
    with (AUD / "2026-09-02-final-keyword-owner-map.csv").open(
            "w", newline="", encoding="utf-8") as fh:
        wtr = csv.DictWriter(fh, fieldnames=list(own[0].keys()))
        wtr.writeheader()
        wtr.writerows(own)

    # ---------------- fingerprint ----------------
    canonical = {
        "plan_id": "PLAN-GA-LAUNCH-1",
        "target": {"exact_child_account_name": "Softwind Power Washing - Live",
                   "child_customer_id": CID, "exact_service": "Power Washing",
                   "manager_customer_id": "3373711342", "campaign_id": SURVIVOR},
        "ad_groups_created": 0,
        "keywords": sorted([{"ad_group_id": r["ad_group_id"], "text": r["text"],
                             "match_type": r["match_type"], "status": "PAUSED"}
                            for r in kw_new], key=lambda x: (x["ad_group_id"], x["text"],
                                                             x["match_type"])),
        "rsas": sorted(
            [{"ad_group_id": GROUPS[g]["ad_group_id"], "rsa": "RSA %d" % ad["n"],
              "final_url": GROUPS[g]["page"], "path1": GROUPS[g]["p1"],
              "path2": GROUPS[g]["p2"], "status": "PAUSED",
              "headlines": ad["h"], "descriptions": ad["d"]}
             for g in GROUPS for ad in RSA[g]],
            key=lambda x: (x["ad_group_id"], x["rsa"])),
        "mutation_count": len(kw_ops) + len(ad_ops),
    }
    fp1 = approval_code(canonical)
    fp2 = approval_code(json.loads(json.dumps(canonical)))
    fp3 = approval_code(canonical)
    if not fp1 == fp2 == fp3:
        errors.append("fingerprint unstable")

    now = datetime.now(ZoneInfo("America/New_York"))
    res = {"plan_id": "PLAN-GA-LAUNCH-1", "generated_account_local": now.isoformat(),
           "counts": {"action_count": len(kw_ops) + len(ad_ops),
                      "object_count": len(kw_ops) + len(ad_ops),
                      "mutation_count": len(kw_ops) + len(ad_ops),
                      "ad_groups_created": 0, "ad_groups_reused": 6,
                      "keyword_objects_created_paused": len(kw_ops),
                      "keyword_objects_reused": len(kw_reuse),
                      "keyword_objects_final": len(kw_ops) + len(kw_reuse),
                      "unique_keyword_texts": 19, "rsas_created_paused": len(ad_ops),
                      "enablement_actions": 0, "pause_actions": 0, "negative_actions": 0,
                      "cpc_actions": 0, "budget_actions": 0, "asset_actions": 0,
                      "conversion_actions": 0, "website_actions": 0},
           "validate_only": vo, "fingerprint": fp1, "recompute_1": fp2, "recompute_2": fp3,
           "canonical_sha256_full": hashlib.sha256(
               json.dumps(canonical, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False).encode("utf-8")).hexdigest(),
           "approval_status": "NOT APPROVED", "execution_status": "DO NOT EXECUTE",
           "approval_command": f"APPROVE PLAN-GA-LAUNCH-1 {fp1} FOR {CID}",
           "rsa_validation_errors": errors, "all_pass": not errors}
    (SNAP / f"launch1-validation-{now.strftime('%Y-%m-%dT%H%M%S')}.json").write_text(
        json.dumps(res, indent=2, default=str), encoding="utf-8")
    (PLN / "2026-09-02-plan-ga-launch-1-payload.json").write_text(
        json.dumps(canonical, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "rsa_validation_errors"},
                     indent=2, default=str))
    print("\nERRORS:", json.dumps(errors, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
