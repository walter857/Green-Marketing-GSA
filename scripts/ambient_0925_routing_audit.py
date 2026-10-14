#!/usr/bin/env python3
"""Ambient | 2026-09-25 | READ-ONLY cross-service routing + inherited-asset + geo-type audit.

Search terms are classified by a whitelist of intent patterns and reported as AGGREGATES only
(see memory: search-term corpus context isolation). No raw query text is printed.
"""
from __future__ import annotations
import sys, json, re, collections, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, E, TZ, SNAP

SEVEN = ["24257819463", "24268690038", "24257819466", "24132507744", "24279798229", "24268690041", "24274160783"]
IN7 = ",".join(SEVEN)
c = client(); identity_gate(c, verbose=False)
out = {"when": datetime.datetime.now(TZ).isoformat()}

INTENT = [
    ("maintenance", re.compile(r"maint|tune[\s-]?up|inspect|clean|service plan|check[\s-]?up|annual", re.I)),
    ("ductless", re.compile(r"ductless|mini[\s-]?split|minisplit", re.I)),
    ("geothermal", re.compile(r"geotherm|ground source|water source", re.I)),
    ("emergency", re.compile(r"emergenc|24\s*(hr|hour|/7)|after hours|same day", re.I)),
    ("thermostat", re.compile(r"thermostat|nest|ecobee", re.I)),
    ("cooling", re.compile(r"\bac\b|a/c|air condition|cooling", re.I)),
    ("jobs_diy", re.compile(r"\bjob|career|salary|hiring|school|training|how to|diy|youtube|manual|parts?\b", re.I)),
]
def intent(t):
    for k, rx in INTENT:
        if rx.search(t): return k
    return "core_or_other"

ags = {str(r.ad_group.id): r.ad_group.name for r in q(c, f"SELECT ad_group.id, ad_group.name FROM ad_group WHERE campaign.id IN ({IN7})")}
st = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0.0, 0.0]))
for r in q(c, f"""SELECT search_term_view.search_term, ad_group.id, metrics.impressions, metrics.clicks,
        metrics.cost_micros, metrics.all_conversions FROM search_term_view
        WHERE campaign.id IN ({IN7}) AND segments.date BETWEEN '2026-09-15' AND '2026-09-25'"""):
    k = intent(r.search_term_view.search_term)
    a = st[str(r.ad_group.id)][k]
    a[0] += r.metrics.impressions; a[1] += r.metrics.clicks; a[2] += r.metrics.cost_micros / 1e6; a[3] += r.metrics.all_conversions
out["search_term_intent_by_group"] = {ags.get(g, g): {k: [v[0], v[1], round(v[2], 2), v[3]] for k, v in d.items()} for g, d in st.items()}
print("SEARCH-TERM INTENT (impr, clicks, cost, allconv) since 2026-09-15, by ad group:")
for g, d in out["search_term_intent_by_group"].items():
    off = {k: v for k, v in d.items() if k not in ("core_or_other",)}
    print(f"  {g[:36]:36s} core/other={d.get('core_or_other')} OFF-SERVICE={off}")

# keywords: match types and generic stems in active groups
kw = collections.Counter()
for r in q(c, f"""SELECT ad_group_criterion.keyword.match_type, ad_group_criterion.keyword.text, ad_group.status, ad_group_criterion.status
        FROM ad_group_criterion WHERE campaign.id IN ({IN7}) AND ad_group_criterion.type = 'KEYWORD'
        AND ad_group_criterion.negative = FALSE AND ad_group_criterion.status != 'REMOVED'"""):
    kw[(E(r.ad_group_criterion.keyword.match_type), intent(r.ad_group_criterion.keyword.text))] += 1
print("positive keywords by match type x intent:", dict(kw))

# assets linked at customer / campaign / ad group level for the seven campaigns
assets = {}
for r in q(c, """SELECT asset.id, asset.type, asset.name, asset.final_urls, asset.sitelink_asset.link_text,
        asset.sitelink_asset.description1, asset.sitelink_asset.description2, asset.callout_asset.callout_text,
        asset.structured_snippet_asset.header, asset.structured_snippet_asset.values, asset.call_asset.phone_number,
        asset.policy_summary.approval_status FROM asset WHERE asset.type IN ('SITELINK','CALLOUT','STRUCTURED_SNIPPET','CALL')"""):
    a = r.asset
    txt = a.sitelink_asset.link_text or a.callout_asset.callout_text or (a.structured_snippet_asset.header + ": " + "|".join(a.structured_snippet_asset.values)) or a.call_asset.phone_number
    assets[str(a.id)] = dict(type=E(a.type), text=txt, d1=a.sitelink_asset.description1, d2=a.sitelink_asset.description2,
                             url=(list(a.final_urls) or [""])[0].replace("https://", ""), approval=E(a.policy_summary.approval_status))
links = []
for r in q(c, f"""SELECT campaign.id, campaign.name, campaign_asset.asset, campaign_asset.field_type, campaign_asset.status
        FROM campaign_asset WHERE campaign.id IN ({IN7}) AND campaign_asset.status != 'REMOVED'"""):
    links.append(("campaign", str(r.campaign.id), r.campaign_asset.asset.split("/")[-1], E(r.campaign_asset.field_type), E(r.campaign_asset.status)))
for r in q(c, """SELECT customer_asset.asset, customer_asset.field_type, customer_asset.status FROM customer_asset WHERE customer_asset.status != 'REMOVED'"""):
    links.append(("account", "-", r.customer_asset.asset.split("/")[-1], E(r.customer_asset.field_type), E(r.customer_asset.status)))
for r in q(c, f"""SELECT ad_group.id, campaign.id, ad_group_asset.asset, ad_group_asset.field_type, ad_group_asset.status, campaign.status
        FROM ad_group_asset WHERE campaign.id IN ({IN7}) AND ad_group_asset.status != 'REMOVED'"""):
    links.append(("ad_group", str(r.ad_group.id), r.ad_group_asset.asset.split("/")[-1], E(r.ad_group_asset.field_type), E(r.ad_group_asset.status)))
out["asset_links"] = [dict(level=l[0], owner=l[1], asset=l[2], field=l[3], status=l[4], **assets.get(l[2], {})) for l in links]
print("\nENABLED asset links (level owner field text -> url):")
agg = collections.defaultdict(set)
for l in out["asset_links"]:
    if l["status"] != "ENABLED": continue
    agg[(l["level"], l["field"], str(l.get("text")), l.get("url") or "", l.get("approval") or "?")].add(l["owner"])
for (lvl, f, t, u, ap), owners in sorted(agg.items(), key=lambda x: (x[0][1], str(x[0][2]))):
    flag = "  <-- OFF-PRIORITY" if re.search(r"maint|tune|inspect|ductless|mini|geotherm|emergenc|24/7|same", f"{t} {u}", re.I) else ""
    print(f"  {lvl:8s} {f:18s} {str(t)[:40]:40s} {u[:48]:48s} {ap:16s} on {len(owners)}{flag}")

# location criteria target types (housing policy: postal codes / radius)
geo_ids = collections.defaultdict(set)
for r in q(c, f"""SELECT campaign.id, campaign_criterion.location.geo_target_constant, campaign_criterion.negative
        FROM campaign_criterion WHERE campaign.id IN ({IN7}) AND campaign_criterion.type = 'LOCATION'"""):
    geo_ids[r.campaign_criterion.location.geo_target_constant].add(str(r.campaign.id))
types = collections.Counter()
for rn in geo_ids:
    g = q(c, f"SELECT geo_target_constant.target_type, geo_target_constant.canonical_name FROM geo_target_constant WHERE geo_target_constant.resource_name = '{rn}'")
    if g: types[g[0].geo_target_constant.target_type] += 1
out["geo_target_types"] = dict(types)
print("\nlocation target types across the seven campaigns:", dict(types))
prox = q(c, f"SELECT campaign.id FROM campaign_criterion WHERE campaign.id IN ({IN7}) AND campaign_criterion.type = 'PROXIMITY'")
print("proximity criteria:", len(prox))

# policy detail for RESTRICTED_HOUSING ads
for r in q(c, f"""SELECT ad_group_ad.ad.id, ad_group.name, ad_group_ad.status, ad_group_ad.policy_summary.policy_topic_entries
        FROM ad_group_ad WHERE campaign.id IN ({IN7}) AND ad_group_ad.status != 'REMOVED'"""):
    for t in r.ad_group_ad.policy_summary.policy_topic_entries:
        if t.topic == "RESTRICTED_HOUSING":
            cons = [(E(x.country_constraint_list.total_targeted_countries) if False else "", [cc.country_criterion for cc in x.country_constraint_list.countries], E(x.reseller_constraint) if False else "") for x in t.constraints]
            ev = [list(e.text_list.texts) for e in t.evidences]
            print(f"  HOUSING {r.ad_group_ad.ad.id} {r.ad_group.name} {E(r.ad_group_ad.status)} type={E(t.type_)} evidences={ev} constraints={cons}")
(SNAP / "routing-audit-2026-09-25.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
