#!/usr/bin/env python3
"""Ambient | 2026-09-15 | policy re-check, AC Repair challenger revalidation, logo, anchors."""
from __future__ import annotations
import sys, json, re, datetime, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

STAMP = "2026-09-15"
COMM_AG, ACR_AG, CAMP = "199748801029", "202339087834", "24132507747"
c = client(); identity_gate(c, verbose=False)
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}

print("=== 1. POLICY STATUS OF THE TWO NEW COMMERCIAL RSAs ===")
pol = []
for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                         ad_group_ad.policy_summary.approval_status,
                         ad_group_ad.policy_summary.review_status,
                         ad_group_ad.policy_summary.policy_topic_entries,
                         ad_group_ad.ad_strength
                  FROM ad_group_ad WHERE ad_group.id = {COMM_AG}"""):
    a = r.ad_group_ad
    rec = {"ad_id": str(a.ad.id), "status": E(a.status),
           "approval": E(a.policy_summary.approval_status),
           "review": E(a.policy_summary.review_status),
           "topics": [f"{E(t.topic_entry_type)}:{t.topic}"
                      for t in a.policy_summary.policy_topic_entries],
           "ad_strength": E(a.ad_strength)}
    pol.append(rec)
    print(f"  ad {rec['ad_id']} {rec['status']:8s} approval={rec['approval']:14s} "
          f"review={rec['review']:22s} strength={rec['ad_strength']:10s} "
          f"topics={rec['topics'] or 'none'}")
out["commercial_ad_policy"] = pol
print("  -> APPROVED is required before any enablement plan is prepared.")

print("\n=== 2. ASSET POLICY STATUS ===")
ap = []
for r in q(c, f"""SELECT ad_group.id, ad_group_asset.asset, ad_group_asset.field_type,
                         ad_group_asset.status, asset.id,
                         asset.policy_summary.approval_status,
                         asset.policy_summary.review_status
                  FROM ad_group_asset WHERE ad_group.id = {COMM_AG}"""):
    ap.append({"asset_id": str(r.asset.id), "field_type": E(r.ad_group_asset.field_type),
               "link_status": E(r.ad_group_asset.status),
               "approval": E(r.asset.policy_summary.approval_status),
               "review": E(r.asset.policy_summary.review_status)})
for x in ap:
    print(f"  {x['field_type']:20s} link={x['link_status']:8s} "
          f"approval={x['approval']:14s} review={x['review']}")
out["commercial_asset_policy"] = ap

print("\n=== 3. AC REPAIR CHALLENGER AMB-0910-RSA-ACR-2 / 1F166DE17017 REVALIDATION ===")
p = PLANS / "AMB-0910-RSA-ACR-2.json"
d = json.loads(p.read_text(encoding="utf-8"))
fp = d.pop("fingerprint", None)
re_fp = approval_code(d)
if fp:
    d["fingerprint"] = fp
print(f"  on-disk fingerprint={fp}  recomputed={re_fp}  match={fp == re_fp}")
acr = [{"ad_id": str(r.ad_group_ad.ad.id), "status": E(r.ad_group_ad.status),
        "approval": E(r.ad_group_ad.policy_summary.approval_status),
        "final_urls": list(r.ad_group_ad.ad.final_urls)}
       for r in q(c, f"""SELECT ad_group.id, ad_group_ad.ad.id, ad_group_ad.status,
                                ad_group_ad.policy_summary.approval_status,
                                ad_group_ad.ad.final_urls
                         FROM ad_group_ad WHERE ad_group.id = {ACR_AG}""")]
print(f"  AC Repair ad group {ACR_AG} currently holds {len(acr)} ads:")
for x in acr:
    print(f"    {x['ad_id']} {x['status']:8s} {x['approval']:12s} {x['final_urls']}")
# does the plan's copy contain the withdrawn claim?
blob = json.dumps(d).lower()
withdrawn = [w for w in ("licensed", "insured", "24/7", "same-day", "same day",
                         "emergency", "guarantee", "financing") if w in blob]
print(f"  withdrawn/barred claim tokens found in the plan copy: {withdrawn or 'NONE'}")
# 3-RSA cap check
print(f"  creating 1 more would make {len(acr) + 1} ads "
      f"(Google allows at most 3 RSAs per ad group): "
      f"{'OK' if len(acr) + 1 <= 3 else 'WOULD BREACH'}")
out["acr2_revalidation"] = {
    "fingerprint_on_disk": fp, "recomputed": re_fp, "match": fp == re_fp,
    "ad_group_ads_now": acr, "withdrawn_claim_tokens": withdrawn,
    "would_breach_3_rsa_cap": len(acr) + 1 > 3,
    "operation_count": d.get("operation_count"),
    "verdict": ("UNEXECUTED_AND_EXACT" if fp == re_fp and not withdrawn and len(acr) + 1 <= 3
                else "NEEDS_SUPERSEDE")}
print(f"  VERDICT: {out['acr2_revalidation']['verdict']}")

print("\n=== 4. BUSINESS LOGO HUNT ===")
logos = []
for r in q(c, """SELECT asset.id, asset.name, asset.type,
                        asset.image_asset.full_size.url,
                        asset.image_asset.full_size.width_pixels,
                        asset.image_asset.full_size.height_pixels,
                        asset.image_asset.file_size,
                        asset.policy_summary.approval_status
                 FROM asset WHERE asset.type = IMAGE"""):
    a = r.asset
    logos.append({"asset_id": str(a.id), "name": a.name or None,
                  "w": a.image_asset.full_size.width_pixels,
                  "h": a.image_asset.full_size.height_pixels,
                  "bytes": a.image_asset.file_size,
                  "approval": E(a.policy_summary.approval_status)})
print(f"  IMAGE assets in the account: {len(logos)}")
for x in logos[:20]:
    ratio = round(x["w"] / x["h"], 3) if x["h"] else None
    sq = "SQUARE_1:1" if ratio == 1.0 else ("LANDSCAPE_4:1" if ratio and abs(ratio - 4) < 0.05
                                            else f"ratio {ratio}")
    print(f"    {x['asset_id']:>14} {x['w']:>5}x{x['h']:<5} {sq:16s} "
          f"{x['bytes']:>8}B {x['approval']:12s} {str(x['name'])[:40]}")
out["image_assets"] = logos
sq_ok = [x for x in logos if x["h"] and x["w"] == x["h"] and x["w"] >= 128]
ls_ok = [x for x in logos if x["h"] and abs(x["w"] / x["h"] - 4) < 0.05 and x["w"] >= 512]
print(f"  Google logo spec: 1:1 >=128x128 (required) and 4:1 >=512x128 (optional)")
print(f"  existing 1:1 candidates: {[x['asset_id'] for x in sq_ok]}")
print(f"  existing 4:1 candidates: {[x['asset_id'] for x in ls_ok]}")
out["logo_candidates"] = {"square_1_1": sq_ok, "landscape_4_1": ls_ok}

print("\n=== 5. COMMERCIAL PAGE SECTION ANCHORS (for possible sitelinks) ===")
try:
    req = urllib.request.Request(
        "https://offer.ambientcoolingandheating.com/commercial-hvac-installation/",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/141.0.0.0 Safari/537.36"})
    with urllib.request.urlopen(req, timeout=45) as r:
        html = r.read().decode("utf-8", errors="replace")
    ids = sorted(set(re.findall(r'id="([a-zA-Z][\w\-]{2,40})"', html)))
    anchors = sorted(set(re.findall(r'href="#([\w\-]{2,40})"', html)))
    named = [i for i in ids if re.search(
        r"quote|form|system|process|step|faq|gallery|contact|about|why|service", i, re.I)]
    print(f"  in-page href=\"#...\" anchors actually linked: {anchors}")
    print(f"  candidate section ids: {named[:25]}")
    out["page_anchors"] = {"linked_anchors": anchors, "candidate_ids": named[:40]}
    print(f"  -> usable, DISTINCT, meaningful sitelink destinations: {len(set(anchors))}")
    print("  -> Google requires 4+ sitelinks with unique destinations. "
          f"{'SUFFICIENT' if len(set(anchors)) >= 4 else 'NOT SUFFICIENT - do not create'}")
except Exception as ex:
    print("  ERR", str(ex)[:200])
    out["page_anchors"] = {"error": str(ex)[:200]}

print("\n=== 6. CAMPAIGN SITELINK LEAKAGE ON 24132507747 ===")
sl = [{"asset_id": str(r.asset.id), "text": r.asset.sitelink_asset.link_text,
       "final_urls": list(r.asset.final_urls), "status": E(r.campaign_asset.status)}
      for r in q(c, f"""SELECT campaign.id, campaign_asset.status, asset.id,
                               asset.sitelink_asset.link_text, asset.final_urls
                        FROM campaign_asset WHERE campaign.id = {CAMP}
                          AND campaign_asset.field_type = SITELINK""")]
for x in sl:
    off = any("offer.ambientcoolingandheating.com" in u for u in x["final_urls"])
    print(f"  {x['status']:8s} {x['text'][:26]:26s} "
          f"{'PAID LP ' if off else 'MAIN SITE'} {x['final_urls']}")
out["campaign_sitelinks"] = sl
leak = [x for x in sl if x["status"] == "ENABLED"
        and not any("offer.ambientcoolingandheating.com" in u for u in x["final_urls"])]
print(f"  ENABLED sitelinks pointing at the MAIN site (not a paid LP): {len(leak)}")
out["sitelink_leakage"] = leak

p2 = SNAP / f"misc-checks-{STAMP}.json"
p2.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(f"\nWROTE {p2}")
