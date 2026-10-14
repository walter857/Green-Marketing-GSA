#!/usr/bin/env python3
"""Ambient | 2026-09-25 | Create the two PMax asset groups (PAUSED) in held campaign 24295088845.

Owner direction 2026-09-25: take images from the landing pages. Images were fetched in the
browser from offer.ambientcoolingandheating.com (same-origin), cropped without stretching to
1.91:1 / 1:1 / 4:5 by scratchpad/make_crops.py, and reviewed. Text comes from
AMB-0925-PMAX-1 (already validated). Campaign stays PAUSED; groups are created PAUSED.

    python ambient_0925_pmax_groups.py validate|execute
"""
from __future__ import annotations
import sys, json, re, argparse, datetime, hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, CID, TZ, RECEIPTS, SNAP
from ambient_0925_pmax_build import ASSET_GROUPS, checks

CAMPAIGN = "24295088845"
CROPS = Path(r"C:\Users\walte\AppData\Local\Temp\claude\D--MG-green-marketing-gsa\e9093d43-7335-4a82-89d5-4762b093785f\scratchpad\crops")
SLOT = {"L": "MARKETING_IMAGE", "S": "SQUARE_MARKETING_IMAGE", "P": "PORTRAIT_MARKETING_IMAGE"}
GROUP_DIR = {"AG_HEAT": "heat", "AG_HP": "hp"}
NEED = {"MARKETING_IMAGE": 4, "SQUARE_MARKETING_IMAGE": 4, "PORTRAIT_MARKETING_IMAGE": 2}


def images_for(key):
    out = []
    for p in sorted((CROPS / GROUP_DIR[key]).glob("*.jpg")):
        slot = SLOT[p.name.split("_")[1]]
        data = p.read_bytes()
        out.append((slot, p.name, data))
    return out


def build(c):
    from PIL import Image
    import io
    errs = checks()
    ga = c.get_service("GoogleAdsService")
    cpath = c.get_service("CampaignService").campaign_path(CID, CAMPAIGN)
    apath = lambda i: c.get_service("AssetService").asset_path(CID, i)
    ops, manifest, tid = [], {}, -1000
    def op(): m = c.get_type("MutateOperation"); ops.append(m); return m
    groups = []
    for gi, (k, g) in enumerate(ASSET_GROUPS.items()):
        links = []
        imgs = images_for(k)
        counts = {s: sum(1 for x in imgs if x[0] == s) for s in NEED}
        if counts != NEED: errs.append(f"{k}: image counts {counts} != {NEED}")
        for slot, name, data in imgs:
            im = Image.open(io.BytesIO(data)); w, h = im.size
            ratio = {"MARKETING_IMAGE": 1.91, "SQUARE_MARKETING_IMAGE": 1.0, "PORTRAIT_MARKETING_IMAGE": 0.8}[slot]
            if abs(w / h - ratio) > 0.01 or len(data) > 5_000_000: errs.append(f"{k}: {name} {w}x{h} {len(data)}")
            m = op(); a = m.asset_operation.create; a.resource_name = apath(tid)
            a.name = f"Ambient PMax {k} {name[:60]} {hashlib.sha1(data).hexdigest()[:8]}"
            a.type_ = c.enums.AssetTypeEnum.IMAGE; a.image_asset.data = data
            links.append((tid, slot)); manifest[name] = dict(group=k, slot=slot, size=f"{w}x{h}", kb=len(data) // 1024); tid -= 1
        texts = [(t, "HEADLINE") for t in g["headlines"]] + [(t, "LONG_HEADLINE") for t in g["long_headlines"]] + \
                [(t, "DESCRIPTION") for t in g["descriptions"]]
        for t, ft in texts:
            m = op(); a = m.asset_operation.create; a.resource_name = apath(tid); a.text_asset.text = t
            links.append((tid, ft)); tid -= 1
        m = op(); a = m.asset_operation.create; a.resource_name = apath(tid)
        a.call_to_action_asset.call_to_action = c.enums.CallToActionTypeEnum.GET_QUOTE
        links.append((tid, "CALL_TO_ACTION_SELECTION")); tid -= 1
        groups.append((c.get_service("AssetGroupService").asset_group_path(CID, -10 - gi), g, links))
    for agp, g, links in groups:
        m = op(); ag = m.asset_group_operation.create
        ag.resource_name = agp; ag.campaign = cpath; ag.name = g["name"]; ag.final_urls.append(g["final_url"])
        ag.path1 = g["path1"]; ag.path2 = g["path2"]; ag.status = c.enums.AssetGroupStatusEnum.PAUSED
        for aid, ft in links:
            m = op(); l = m.asset_group_asset_operation.create; l.asset_group = agp; l.asset = apath(aid)
            l.field_type = getattr(c.enums.AssetFieldTypeEnum, ft)
    for agp, g, links in groups:
        for th in g["search_themes"]:
            m = op(); s_ = m.asset_group_signal_operation.create; s_.asset_group = agp; s_.search_theme.text = th
    return ops, manifest, errs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["validate", "execute"]); a = ap.parse_args()
    c = client(); identity_gate(c, verbose=False)
    st = q(c, f"SELECT campaign.status, campaign.advertising_channel_type FROM campaign WHERE campaign.id = {CAMPAIGN}")
    if not st or E(st[0].campaign.status) != "PAUSED": sys.exit("ABORT: campaign not PAUSED")
    existing = q(c, f"SELECT asset_group.id, campaign.id FROM asset_group WHERE campaign.id = {CAMPAIGN} AND asset_group.status != 'REMOVED'")
    if existing: sys.exit(f"ABORT: asset groups already exist {[r.asset_group.id for r in existing]}")
    ops, manifest, errs = build(c)
    print(f"{len(ops)} ops | images {len(manifest)} | errors {errs or 0}")
    if errs: sys.exit(1)
    rq = c.get_type("MutateGoogleAdsRequest"); rq.customer_id = CID; rq.partial_failure = False
    rq.mutate_operations.extend(ops); rq.validate_only = a.mode == "validate"
    try:
        resp = c.get_service("GoogleAdsService").mutate(request=rq)
    except Exception as ex:
        msgs = re.findall(r'message: "([^"]+)"', str(ex)); idx = re.findall(r"index: (\d+)", str(ex))
        print("FAIL", msgs[:6], idx[:8]); sys.exit(1)
    if a.mode == "validate":
        print("VALIDATE PASS"); return
    names = []
    for r in resp.mutate_operation_responses:
        for f in ("asset_result", "asset_group_result", "asset_group_asset_result", "asset_group_signal_result"):
            if r._pb.HasField(f): names.append(getattr(r, f).resource_name)
    rec = {"plan": "AMB-0925-PMAX-GROUPS-1", "campaign": CAMPAIGN, "executed_local": datetime.datetime.now(TZ).isoformat(),
           "image_manifest": manifest, "image_source": "offer.ambientcoolingandheating.com page images, cropped, not stretched",
           "created": names}
    (RECEIPTS / "AMB-0925-PMAX-GROUPS-1-EXECUTED.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print("CREATED", len(names), "resources;", [n for n in names if "/assetGroups/" in n])


if __name__ == "__main__":
    main()
