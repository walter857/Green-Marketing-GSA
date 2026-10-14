#!/usr/bin/env python3
"""Ambient | 2026-10-01 | READ-ONLY routing context for the search-term / landing-page work orders.

Reads ONLY positive keywords, negatives (campaign + ad group + attached shared lists), ad-group statuses, enabled-ad
final URLs and labels for the other ENABLED heating campaigns, so that boiler / emergency / geothermal routing and the
reverse (over-blocking) probe test can be evaluated. This is not an audit of those campaigns. No mutations.
Writes snapshots/routing-context-2026-10-01.json.
"""
from __future__ import annotations
import sys, json, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, SNAP  # noqa: E402

HEAT = ["24257819463", "24257819466", "24132507744", "24268690038", "24268690041", "24279798229", "24274160783", "24132507747"]
IN = ",".join(HEAT)
c = client()
identity_gate(c, verbose=False)
out = {"campaigns": {}, "ad_groups": {}, "keywords": [], "campaign_negatives": [], "attachments": [], "enabled_ads": []}
for r in q(c, f"SELECT campaign.id, campaign.name, campaign.status FROM campaign WHERE campaign.id IN ({IN})"):
    out["campaigns"][str(r.campaign.id)] = dict(name=r.campaign.name, status=E(r.campaign.status))
for r in q(c, f"SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status, ad_group.labels FROM ad_group WHERE campaign.id IN ({IN}) AND ad_group.status != 'REMOVED'"):
    out["ad_groups"][str(r.ad_group.id)] = dict(campaign_id=str(r.campaign.id), name=r.ad_group.name, status=E(r.ad_group.status))
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, ad_group_criterion.negative,
        ad_group_criterion.status FROM ad_group_criterion WHERE campaign.id IN ({IN}) AND ad_group_criterion.type = 'KEYWORD'
        AND ad_group_criterion.status != 'REMOVED'"""):
    k = r.ad_group_criterion
    out["keywords"].append(dict(campaign_id=str(r.campaign.id), ad_group_id=str(r.ad_group.id), text=k.keyword.text, match=E(k.keyword.match_type),
                                negative=k.negative, status=E(k.status)))
for r in q(c, f"""SELECT campaign.id, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type FROM campaign_criterion
        WHERE campaign.id IN ({IN}) AND campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE"""):
    out["campaign_negatives"].append(dict(campaign_id=str(r.campaign.id), text=r.campaign_criterion.keyword.text, match=E(r.campaign_criterion.keyword.match_type)))
for r in q(c, f"SELECT campaign.id, shared_set.id, campaign_shared_set.status FROM campaign_shared_set WHERE campaign.id IN ({IN})"):
    out["attachments"].append(dict(campaign_id=str(r.campaign.id), set_id=str(r.shared_set.id), status=E(r.campaign_shared_set.status)))
for r in q(c, f"""SELECT campaign.id, ad_group.id, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls FROM ad_group_ad
        WHERE campaign.id IN ({IN}) AND ad_group_ad.status = 'ENABLED'"""):
    out["enabled_ads"].append(dict(campaign_id=str(r.campaign.id), ad_group_id=str(r.ad_group.id), ad_id=str(r.ad_group_ad.ad.id),
                                   final_urls=list(r.ad_group_ad.ad.final_urls)))
(SNAP / "routing-context-2026-10-01.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print("campaigns", {k: (v["status"], v["name"][18:60]) for k, v in out["campaigns"].items()})
print("ad groups", len(out["ad_groups"]), "keywords", sum(1 for k in out["keywords"] if not k["negative"]),
      "ag negatives", sum(1 for k in out["keywords"] if k["negative"]), "campaign negatives", len(out["campaign_negatives"]),
      "attachments", collections.Counter((a["campaign_id"], a["set_id"], a["status"]) for a in out["attachments"]))
for gid, g in sorted(out["ad_groups"].items(), key=lambda kv: (kv[1]["campaign_id"], kv[1]["name"])):
    pos = sorted((k["match"][0], k["text"], k["status"][0]) for k in out["keywords"] if k["ad_group_id"] == gid and not k["negative"])
    urls = sorted({u for a in out["enabled_ads"] if a["ad_group_id"] == gid for u in a["final_urls"]})
    print(f"  {g['campaign_id']} {gid} {g['status']:7s} {g['name'][7:]:30s} ads_enabled={sum(1 for a in out['enabled_ads'] if a['ad_group_id'] == gid)} {urls} kw={pos}")
