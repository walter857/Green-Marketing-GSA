#!/usr/bin/env python3
"""Ambient | 2026-09-21 | Policy status of the assets the plan would reuse, plus exposure
from the 11 sitelinks that point at the destination-blocked heat-pumps URL.

READ-ONLY. EXTERNAL WRITES: 0.

Two questions:
  1. Is every asset the expansion plan intends to REUSE actually approved and serving?
     Reusing a disapproved asset imports a defect into a new campaign.
  2. Are any of the 11 sitelink assets targeting the blocked heat-pumps URL currently
     linked to an ENABLED campaign? If so that is a live liability that exists right now,
     independent of the expansion.
"""
from __future__ import annotations
import sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

STAMP = "2026-09-21"
BLOCKED = ["186596746650", "193727047168", "218980811224", "219144213651", "236889113433",
           "310932601685", "310932934583", "310933036511", "311020737385", "311048254797",
           "311048602374"]
REUSE = {
    "CALL": ["407995613637"],
    "BUSINESS_NAME": ["80516971145"],
    "CALLOUT": ["422477374526", "422577760603", "422577771364",
                "422577777430", "422577777442"],
    "SITELINK": ["422477374559", "422577771382", "422577777457", "185161619511"],
    "STRUCTURED_SNIPPET": ["422477374541"],
}


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "stamp": STAMP,
           "read_only": True, "external_writes": 0}

    want = {a for v in REUSE.values() for a in v} | set(BLOCKED)
    ids = ",".join(sorted(want))

    print("=== ASSET POLICY SUMMARY ===")
    pol = {}
    for r in q(c, f"""SELECT asset.id, asset.type, asset.name,
                      asset.policy_summary.approval_status,
                      asset.policy_summary.review_status
                      FROM asset WHERE asset.id IN ({ids})"""):
        pol[str(r.asset.id)] = {"type": E(r.asset.type_),
                                "approval": E(r.asset.policy_summary.approval_status),
                                "review": E(r.asset.policy_summary.review_status)}
    out["asset_policy"] = pol

    print("\n   REUSE SET:")
    bad = []
    for ft, aids in REUSE.items():
        for a in aids:
            p = pol.get(a, {})
            ok = p.get("approval") in ("APPROVED", "APPROVED_LIMITED", "UNKNOWN", None)
            if p.get("approval") == "DISAPPROVED":
                bad.append(a)
                ok = False
            print(f"      {ft:20s} {a:16s} {p.get('approval', 'n/a'):18s} "
                  f"{p.get('review', 'n/a'):16s} {'OK' if ok else 'PROBLEM'}")
    out["reuse_disapproved"] = bad

    print("\n=== EXPOSURE FROM BLOCKED-URL SITELINKS ===")
    exposure = {}
    for r in q(c, f"""SELECT campaign.id, campaign.name, campaign.status,
                      campaign_asset.asset, campaign_asset.field_type,
                      campaign_asset.status, asset.id
                      FROM campaign_asset
                      WHERE campaign_asset.status != 'REMOVED'
                        AND campaign.status != 'REMOVED'
                        AND asset.id IN ({",".join(BLOCKED)})"""):
        exposure.setdefault(str(r.asset.id), []).append(
            {"campaign_id": str(r.campaign.id), "campaign": r.campaign.name,
             "campaign_status": E(r.campaign.status),
             "link_status": E(r.campaign_asset.status)})
    live = {a: [x for x in v if x["campaign_status"] == "ENABLED"]
            for a, v in exposure.items()}
    live = {a: v for a, v in live.items() if v}
    if not exposure:
        print("   none of the 11 is linked to any non-removed campaign")
    for a, v in exposure.items():
        st = "ON AN ENABLED CAMPAIGN" if a in live else "paused campaigns only"
        print(f"   asset {a}  {len(v)} link(s)  {st}")
        for x in v[:4]:
            print(f"      {x['campaign_status']:8s} {x['link_status']:8s} "
                  f"{x['campaign'][:52]}")
    out["blocked_sitelink_links"] = exposure
    out["blocked_sitelinks_on_enabled_campaigns"] = live
    print(f"\n   VERDICT: {len(live)} of the 11 are on an ENABLED campaign "
          f"-> {'LIVE LIABILITY' if live else 'no live exposure'}")

    # Also check account-level links, which serve everywhere.
    cl = []
    for r in q(c, f"""SELECT customer_asset.asset, customer_asset.field_type,
                      customer_asset.status, asset.id
                      FROM customer_asset
                      WHERE customer_asset.status != 'REMOVED'
                        AND asset.id IN ({",".join(BLOCKED)})"""):
        cl.append({"asset_id": str(r.asset.id),
                   "field_type": E(r.customer_asset.field_type),
                   "status": E(r.customer_asset.status)})
    out["blocked_sitelinks_at_account_level"] = cl
    print(f"   account-level links among the 11: {len(cl)}")

    SNAP.mkdir(parents=True, exist_ok=True)
    p = SNAP / f"asset-policy-{STAMP}.json"
    p.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(f"\nWROTE {p}")
    print("EXTERNAL WRITES: 0")


if __name__ == "__main__":
    main()
