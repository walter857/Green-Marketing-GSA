#!/usr/bin/env python3
"""Ambient | 2026-09-24 | Landing-page-only migration. BUILD + validate_only PREFLIGHT.

EXTERNAL WRITES: 0. Every mutate below runs with validate_only=True.

Produces two approval-ready plans and a draft of the third:

  AMB-0924-LP-PAUSE-1   pause 8 ENABLED ad groups that have no relevant offer page, and
                        pause 19 sitelink LINKS on enabled heating campaigns that send
                        clicks to the main site or to the cooling-only AC Repair page.
  AMB-0924-LP-CREATE-1  create, all PAUSED: 7 offer-page sitelink assets + 14 PAUSED
                        campaign links, 12 RSA copies that move 6 live ad groups to their
                        offer page, and 12 RSAs for 6 paused ad groups launching on
                        verified offer pages (incl. No Heat Repair 204129717087).
  AMB-0924-LP-ENABLE-1  DRAFT ONLY. Needs CREATE-1 resource ids and approved ads. Pauses
                        the old main-site RSAs BEFORE enabling copies (3-enabled-RSA cap).

Page verdicts come from the 2026-09-24 Chrome verification (desktop + 390px) recorded in
snapshots/lp-verify-2026-09-24.json.
"""
from __future__ import annotations
import sys, json, re, datetime, copy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import client, q, identity_gate, TZ, SNAP, PLANS, E, CID, EXACT_NAME
from gm_gsa.safety import approval_code
import ambient_0922_build_exec as B22

STAMP = "2026-09-24"
O = "https://offer.ambientcoolingandheating.com"

# ------------------------------------------------------------------ decisions
MIGRATE = {  # enabled ad group -> verified offer page that genuinely matches
    "199797580706": ("SKAG | Furnace Repair", f"{O}/furnace-repair/"),
    "204129717247": ("SKAG | Gas Furnace Repair", f"{O}/furnace-repair/"),
    "204129717287": ("SKAG | Electric Furnace Repair", f"{O}/furnace-repair/"),
    "204129717007": ("SKAG | Heating Repair", f"{O}/hvac-repair/"),
    "204129717767": ("SKAG | Furnace Replacement", f"{O}/hvac-replacement/"),
    "204129718047": ("SKAG | Boiler Repair", f"{O}/gas-boiler-repair/"),
}
PAUSE_NO_PAGE = {  # enabled ad group -> the exact page that is missing
    "204129719007": ("SKAG | Geothermal Heat Pump", "no geothermal page on offer subdomain"),
    "204129717727": ("SKAG | Ductless Heating Repair", "no ductless/mini-split repair page"),
    "199797580746": ("SKAG | Ductless Heating Installation", "no ductless/mini-split installation page"),
    "204129718447": ("SKAG | Furnace Maintenance", "no furnace maintenance page"),
    "204129718527": ("SKAG | Furnace Tune-Up", "no furnace tune-up page"),
    "204129718487": ("SKAG | Heating Maintenance", "no heating maintenance page"),
    "204129718727": ("SKAG | Heating System Inspection", "no heating inspection page"),
    "204129718687": ("SKAG | Heating Tune-Up", "no heating tune-up page"),
}
NOHEAT_A = {"h": ["No Heat Repair", "No Heat Repair Central MD", "No Heat In Your Home?",
                  "House Has No Heat?", "Book A Heating Repair Visit", "Heating Repair Near You",
                  "Severn Heating Repair", "Severna Park Heating Repair",
                  "Columbia MD Heating Repair", "Call Mon-Fri 8 AM-4 PM",
                  "Free Heating Repair Quote", "Talk To A Technician", "Clear Repair Options",
                  "Request A Heating Visit", "Maryland Heating Repair"],
            "d": ["No heat in your Severn, Severna Park or Columbia home? Request a repair visit.",
                  "We diagnose why your home has no heat and explain the repair options first.",
                  "Call Mon-Fri, 8 a.m.-4 p.m., or send a repair request online.",
                  "Request a free no heat repair quote from Ambient Cooling and Heating."],
            "label": "RSA A - service and hours led"}
NOHEAT_B = {"h": ["No Heat From The Vents?", "Furnace Running, No Heat?",
                  "Heating System Not Heating?", "No Heat Repair", "Thermostat On, House Cold?",
                  "Get Your Heating Checked", "No Heat Repair Near You",
                  "Heating Repair Specialists", "Central Maryland Heating",
                  "Talk To A Technician", "Clear Repair Options", "Open Mon-Fri, 8 AM-4 PM",
                  "Request A Repair Visit", "Columbia Heating Service", "Severn Heating Help"],
            "d": ["Thermostat calling for heat but the house stays cold? We find the cause.",
                  "We diagnose the no-heat fault and walk you through the repair options.",
                  "No heat repair for homes in Severn, Severna Park and Columbia, Maryland.",
                  "Open Monday to Friday, 8 a.m. to 4 p.m. Request your no heat repair visit."],
            "label": "RSA B - problem led"}
LAUNCH = {  # paused ad group -> (name, verified offer page, rsas, keywords to enable)
    "204129717087": ("SKAG | No Heat Repair", f"{O}/no-heat-repair/", [NOHEAT_A, NOHEAT_B],
                     {("no heat repair", "EXACT"), ("no heat repair", "PHRASE")}),
    "204129717327": ("SKAG | Heat Pump Repair", f"{O}/heat-pump-repair/", None, "ALL"),
    "204129717487": ("SKAG | Heat Pump Replacement", f"{O}/heat-pump-replacement/", None, "ALL"),
    "204129717527": ("SKAG | Heat Pump Installation", f"{O}/heat-pump-installation/", None, "ALL"),
    "204129717567": ("SKAG | Heat Pump Maintenance", f"{O}/heat-pump-maintenance/", None, "ALL"),
    "204129718207": ("SKAG | Boiler Replacement", f"{O}/boiler-replacement/", None, "ALL"),
    # thermostat pages verified 2026-09-24; the three groups already exist, paused, 0 ads
    "204129718767": ("SKAG | Thermostat Repair", f"{O}/thermostat-repair/", None, "ALL"),
    "204129718927": ("SKAG | Thermostat Replacement", f"{O}/thermostat-replacement/", None, "ALL"),
    # [nest thermostat installation] stays PAUSED: brands serviced is an unverified claim and
    # the page never mentions Nest
    "204129718967": ("SKAG | Smart Thermostat Installation", f"{O}/smart-thermostat/", None,
                     {("smart thermostat installation", "PHRASE"),
                      ("smart thermostat installation", "EXACT")}),
}
HOLD = {
    "204129718247": ("SKAG | Boiler Installation", f"{O}/boiler-installation/",
                     "page body is Boiler MAINTENANCE content (H1 'Boiler Maintenance in "
                     "Central MD', 0 'install' mentions)"),
    "204129718287": ("SKAG | Boiler Maintenance", f"{O}/boiler-maintenance/",
                     "H1 says maintenance but the body is Boiler INSTALLATION content "
                     "(23 install vs 4 maintenance mentions) - the two pages are swapped"),
}
NEW_SITELINKS = [  # key, text, url, d1, d2
    ("SL_FURNACE", "Furnace Repair", f"{O}/furnace-repair/", "Find the cause of the problem", "Clear repair options"),
    ("SL_NOHEAT", "No Heat Repair", f"{O}/no-heat-repair/", "House cold with the heat on?", "Call Mon-Fri, 8 a.m.-4 p.m."),
    ("SL_HPREP", "Heat Pump Repair", f"{O}/heat-pump-repair/", "Heat pump not heating?", "Repair or replace advice"),
    ("SL_HPINS", "Heat Pump Installation", f"{O}/heat-pump-installation/", "Installation assessment", "Request a free quote"),
    ("SL_HPREPL", "Heat Pump Replacement", f"{O}/heat-pump-replacement/", "Replace worn equipment", "Request a free quote"),
    ("SL_HPMAINT", "Heat Pump Maintenance", f"{O}/heat-pump-maintenance/", "Planned heat pump checks", "Request a free quote"),
    ("SL_BOILREPL", "Boiler Replacement", f"{O}/boiler-replacement/", "Replacement assessment", "Request a free quote"),
    ("SL_TREP", "Thermostat Repair", f"{O}/thermostat-repair/", "Check the controls first", "Request a free quote"),
    ("SL_TREPL", "Thermostat Replacement", f"{O}/thermostat-replacement/", "Choose a compatible model", "Request a free quote"),
    ("SL_SMART", "Smart Thermostat Install", f"{O}/smart-thermostat/", "Fit to your heating system", "Request a free quote"),
]
EXISTING_OFFER_SL = {"SL_HVACINST": "410638276380", "SL_HVACREPL": "410638278156",
                     "SL_HVACREP": "410638280067", "SL_GASBOIL": "410465469923"}
SITELINK_PLAN = {  # campaign -> sitelinks to link (PAUSED now, enabled by ENABLE-1)
    "24257819463": ["SL_FURNACE", "SL_NOHEAT", "SL_HPREP", "SL_HVACREP"],
    "24257819466": ["SL_HPINS", "SL_HPREPL", "SL_HVACINST", "SL_HVACREPL"],
    "24268690038": ["SL_HPREP", "SL_HPINS", "SL_HPREPL", "SL_HPMAINT"],
    "24132507744": ["SL_BOILREPL", "SL_GASBOIL"],
    "24268690041": ["SL_TREP", "SL_TREPL", "SL_SMART", "SL_NOHEAT"],
}
HEATING_ENABLED = ["24132507744", "24274160783", "24132507747", "24268690038",
                   "24257819466", "24257819463", "24279798229",
                   "24268690041"]  # Thermostat Services: PAUSED today, launches in ENABLE
AC_REPAIR_SL = "410638280061"

BARRED = re.compile(r"24/7|24-7|same[- ]day|emergenc|licens|insured|guarantee|warrant|"
                    r"financ|\$\d|% off|discount|years? (of )?experience|\d\.\d ?star|"
                    r"certified|fast response|within \d+ (min|hour)|nest|ecobee|honeywell|emerson|"
                    r"brands? we service", re.I)


def check_rsa(r, where):
    errs = []
    if not 3 <= len(r["h"]) <= 15: errs.append(f"{where}: {len(r['h'])} headlines")
    if not 2 <= len(r["d"]) <= 4: errs.append(f"{where}: {len(r['d'])} descriptions")
    for h in r["h"]:
        if len(h) > 30: errs.append(f"{where}: headline {len(h)}>30 '{h}'")
    for d in r["d"]:
        if len(d) > 90: errs.append(f"{where}: description {len(d)}>90 '{d}'")
    if len({h.lower() for h in r["h"]}) != len(r["h"]): errs.append(f"{where}: duplicate headline")
    if len({d.lower() for d in r["d"]}) != len(r["d"]): errs.append(f"{where}: duplicate description")
    for t in r["h"] + r["d"]:
        if BARRED.search(t): errs.append(f"{where}: barred claim in '{t}'")
    return errs


def toks(s):
    return s.lower().split()


def neg_blocks(neg_text, mt, query):
    n, qq = toks(neg_text), toks(query)
    if mt == "EXACT": return n == qq
    if mt == "PHRASE": return any(qq[i:i + len(n)] == n for i in range(len(qq) - len(n) + 1))
    return all(t in qq for t in n)                                    # BROAD


def pos_reaches(kw, mt, query):
    k, qq = toks(kw), toks(query)
    if mt == "EXACT": return k == qq
    return any(qq[i:i + len(k)] == k for i in range(len(qq) - len(k) + 1))  # PHRASE


def main():
    c = client()
    identity_gate(c, verbose=False)
    out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "external_writes": 0,
           "errors": [], "warnings": []}
    err, warn = out["errors"], out["warnings"]

    # --------------------------------------------------------- fresh reads
    ag_rows = {str(r.ad_group.id): r for r in q(c, """SELECT ad_group.id, ad_group.name,
               ad_group.status, campaign.id, campaign.name, campaign.status FROM ad_group
               WHERE campaign.status != 'REMOVED'""")}
    for gid, (name, *_r) in {**MIGRATE, **PAUSE_NO_PAGE, **{k: v[:1] for k, v in LAUNCH.items()},
                             **{k: v[:1] for k, v in HOLD.items()}}.items():
        r = ag_rows.get(gid)
        if not r or r.ad_group.name != name:
            err.append(f"ad group {gid} name drift: expected '{name}', live "
                       f"'{r.ad_group.name if r else None}'")
    for gid in list(MIGRATE) + list(PAUSE_NO_PAGE):
        if E(ag_rows[gid].ad_group.status) != "ENABLED":
            err.append(f"{gid} expected ENABLED, is {E(ag_rows[gid].ad_group.status)}")
    for gid in list(LAUNCH) + list(HOLD):
        if E(ag_rows[gid].ad_group.status) != "PAUSED":
            err.append(f"{gid} expected PAUSED, is {E(ag_rows[gid].ad_group.status)}")

    ads = {}
    for r in q(c, """SELECT ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.ad.final_urls,
                  ad_group_ad.ad.final_mobile_urls, ad_group_ad.ad.type,
                  ad_group_ad.ad.responsive_search_ad.headlines,
                  ad_group_ad.ad.responsive_search_ad.descriptions,
                  ad_group_ad.ad.responsive_search_ad.path1,
                  ad_group_ad.ad.responsive_search_ad.path2,
                  ad_group_ad.policy_summary.approval_status, ad_group.id
                  FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED'
                  AND campaign.status != 'REMOVED'"""):
        ads.setdefault(str(r.ad_group.id), []).append(r.ad_group_ad)

    kws = {}
    for r in q(c, """SELECT ad_group_criterion.criterion_id, ad_group_criterion.keyword.text,
                  ad_group_criterion.keyword.match_type, ad_group_criterion.status,
                  ad_group_criterion.negative, ad_group.id, campaign.id
                  FROM ad_group_criterion WHERE ad_group_criterion.type = 'KEYWORD'
                  AND ad_group_criterion.status != 'REMOVED' AND campaign.status != 'REMOVED'"""):
        kws.setdefault(str(r.ad_group.id), []).append(r)

    # ------------------------------------------------ migration RSA copies
    migrate_ops, old_ads = [], []
    for gid, (name, url) in MIGRATE.items():
        live = [a for a in ads.get(gid, []) if E(a.status) == "ENABLED"]
        if len(live) != 2:
            err.append(f"{name}: expected 2 ENABLED RSAs, found {len(live)}")
        for a in live:
            rsa = a.ad.responsive_search_ad
            old_ads.append({"ad_group_id": gid, "ad_id": str(a.ad.id),
                            "old_url": list(a.ad.final_urls)})
            migrate_ops.append({
                "op": "CREATE_RSA_PAUSED", "kind": "migration_copy", "ad_group_id": gid,
                "ad_group": name, "copy_of_ad_id": str(a.ad.id), "final_url": url,
                "old_final_url": list(a.ad.final_urls)[0],
                "headlines": [{"text": h.text, "pin": E(h.pinned_field)} for h in rsa.headlines],
                "descriptions": [{"text": d.text, "pin": E(d.pinned_field)} for d in rsa.descriptions],
                "path1": rsa.path1, "path2": rsa.path2})
            if a.ad.final_mobile_urls:
                err.append(f"{name} ad {a.ad.id} has a mobile URL override - not handled")

    # ------------------------------------------------ launch RSAs + keywords
    launch_ops, launch_kw = [], []
    for gid, (name, url, rsas, kwsel) in LAUNCH.items():
        if ads.get(gid):
            err.append(f"{name}: expected 0 ads, found {len(ads[gid])}")
        if rsas is None:
            d = B22.AG.get(name)
            if not d or len(d["rsas"]) != 2:
                err.append(f"{name}: no 2-RSA draft in the 2026-09-22 build"); continue
            rsas = [{"h": r["h"], "d": r["d"], "label": r["label"].split(" - ")[0] +
                     " - 2026-09-22 draft"} for r in d["rsas"]]
        for r in rsas:
            err += check_rsa(r, f"{name} {r['label']}")
            launch_ops.append({"op": "CREATE_RSA_PAUSED", "kind": "launch", "ad_group_id": gid,
                               "ad_group": name, "final_url": url, "label": r["label"],
                               "headlines": [{"text": h, "pin": "UNSPECIFIED"} for h in r["h"]],
                               "descriptions": [{"text": x, "pin": "UNSPECIFIED"} for x in r["d"]],
                               "path1": "", "path2": ""})
        for k in kws.get(gid, []):
            cr = k.ad_group_criterion
            if cr.negative:
                continue
            key = (cr.keyword.text, E(cr.keyword.match_type))
            if E(cr.status) == "ENABLED":
                warn.append(f"{name}: positive keyword {key} already ENABLED inside a PAUSED group")
            if kwsel == "ALL" or key in kwsel:
                launch_kw.append({"ad_group_id": gid, "ad_group": name,
                                  "criterion_id": str(cr.criterion_id), "text": key[0],
                                  "match": key[1], "campaign_id": str(k.campaign.id)})
    for op in migrate_ops:
        err += check_rsa({"h": [h["text"] for h in op["headlines"]],
                          "d": [d["text"] for d in op["descriptions"]]},
                         f"{op['ad_group']} copy of {op['copy_of_ad_id']}")

    # ------------------------------------------------ negative conflict test
    negs = []   # (level, owner, text, match)
    for gid in LAUNCH:
        for k in kws.get(gid, []):
            if k.ad_group_criterion.negative:
                negs.append(("ad_group", gid, k.ad_group_criterion.keyword.text,
                             E(k.ad_group_criterion.keyword.match_type)))
    camps = {kw["campaign_id"] for kw in launch_kw}
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.keyword.text,
                   campaign_criterion.keyword.match_type FROM campaign_criterion
                   WHERE campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE
                   AND campaign.id IN ({','.join(camps)})"""):
        negs.append(("campaign", str(r.campaign.id), r.campaign_criterion.keyword.text,
                     E(r.campaign_criterion.keyword.match_type)))
    shared = {}
    for r in q(c, f"""SELECT campaign.id, shared_set.id, shared_set.type, campaign_shared_set.status
                   FROM campaign_shared_set WHERE campaign.id IN ({','.join(camps)})
                   AND campaign_shared_set.status = 'ENABLED'"""):
        shared.setdefault(str(r.shared_set.id), set()).add(str(r.campaign.id))
    for r in q(c, """SELECT shared_set.id, shared_set.type, shared_set.status FROM shared_set
                  WHERE shared_set.type = 'ACCOUNT_LEVEL_NEGATIVE_KEYWORDS'
                  AND shared_set.status = 'ENABLED'"""):
        shared.setdefault(str(r.shared_set.id), set()).update(camps)
    if shared:
        for r in q(c, f"""SELECT shared_set.id, shared_criterion.keyword.text,
                       shared_criterion.keyword.match_type FROM shared_criterion
                       WHERE shared_set.id IN ({','.join(shared)})
                       AND shared_criterion.type = 'KEYWORD'"""):
            for cid in shared[str(r.shared_set.id)]:
                negs.append((f"shared:{r.shared_set.id}", cid, r.shared_criterion.keyword.text,
                             E(r.shared_criterion.keyword.match_type)))
    out["negatives_tested"] = len(negs)
    mods = ["", " near me", " service", " company", " cost", " maryland", " severn md",
            " severna park", " columbia md", " contractor"]
    pre = ["", "residential ", "home ", "local "]
    conflicts = []
    for kw in launch_kw:
        for p in pre:
            for m in mods:
                qy = f"{p}{kw['text']}{m}".strip()
                if not pos_reaches(kw["text"], kw["match"], qy):
                    continue
                for lvl, owner, nt, nm in negs:
                    applies = (owner == kw["ad_group_id"] if lvl == "ad_group"
                               else owner == kw["campaign_id"])
                    if applies and neg_blocks(nt, nm, qy):
                        conflicts.append({"keyword": f"{kw['text']} [{kw['match']}]",
                                          "ad_group": kw["ad_group"], "query": qy,
                                          "negative": f"{nt} [{nm}]", "level": lvl})
    MOVE_TEXTS = {"thermostat", "thermostats"}
    ACCT_LIST = "11252984411"
    resolved = [x for x in conflicts if x["level"] == f"shared:{ACCT_LIST}"
                and x["negative"].split(" [")[0] in MOVE_TEXTS]
    unresolved = [x for x in conflicts if x not in resolved]
    out["conflicts"] = unresolved
    out["conflicts_resolved_by_neg_move"] = len(resolved)
    if unresolved:
        err.append(f"{len(unresolved)} reachable negative conflicts")
    conflicts = unresolved
    info = [n for n in negs if n[2].lower() in ("how to", "diy", "youtube", "reddit", "jobs",
                                                 "salary", "training", "school", "course")]
    out["informational_negatives_present"] = sorted({f"{n[2]} [{n[3]}] {n[0]}" for n in info})

    # ------------------------------------------------ sitelink state
    sl = {}
    for r in q(c, """SELECT asset.id, asset.sitelink_asset.link_text, asset.final_urls
                  FROM asset WHERE asset.type = 'SITELINK'"""):
        sl[str(r.asset.id)] = (r.asset.sitelink_asset.link_text, list(r.asset.final_urls))
    for key, text, url, d1, d2 in NEW_SITELINKS:
        if len(text) > 25 or len(d1) > 35 or len(d2) > 35:
            err.append(f"sitelink {key} over length")
        if BARRED.search(text + d1 + d2):
            err.append(f"sitelink {key} barred claim")
        dup = [a for a, (t, u) in sl.items() if u and u[0] == url]
        if dup:
            warn.append(f"sitelink for {url} already exists as {dup}; plan still creates "
                        f"{key} - review")
    for k, aid in EXISTING_OFFER_SL.items():
        if aid not in sl or not sl[aid][1][0].startswith(O):
            err.append(f"existing sitelink {k} {aid} is not an offer-page sitelink")
    links = []
    for r in q(c, """SELECT campaign.id, campaign.status, campaign_asset.asset,
                  campaign_asset.status, campaign_asset.resource_name FROM campaign_asset
                  WHERE campaign_asset.field_type = 'SITELINK' AND campaign.status != 'REMOVED'"""):
        links.append({"campaign_id": str(r.campaign.id),
                      "asset_id": r.campaign_asset.asset.split("/")[-1],
                      "status": E(r.campaign_asset.status),
                      "rn": r.campaign_asset.resource_name})
    pause_links = []
    for l in links:
        if l["campaign_id"] not in HEATING_ENABLED or l["status"] != "ENABLED":
            continue
        url = (sl.get(l["asset_id"], ("", [""]))[1] or [""])[0]
        if not url.startswith(O) or l["asset_id"] == AC_REPAIR_SL:
            pause_links.append({**l, "text": sl.get(l["asset_id"], ("?",))[0], "url": url})
    for camp, keys in SITELINK_PLAN.items():
        for k in keys:
            if k in EXISTING_OFFER_SL:
                aid = EXISTING_OFFER_SL[k]
                if any(l["campaign_id"] == camp and l["asset_id"] == aid for l in links):
                    warn.append(f"{k} already linked to {camp}; link skipped")

    # ------------------------------------------------ plans
    pause_plan = {
        "customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342",
        "built_local": STAMP, "plan_name": "AMB-0924-LP-PAUSE-2", "supersedes": "AMB-0924-LP-PAUSE-1 ED3D506A68FF (never executed)",
        "approval_class": "status-change-pause-only", "nothing_created": True,
        "nothing_removed": True, "no_budget_bid_keyword_or_targeting_change": True,
        "why": "Landing-page-only standard: every paid website destination must be a verified "
               "offer.ambientcoolingandheating.com page. These ad groups have no relevant offer "
               "page; these sitelink links point at the main site or at the cooling-only AC "
               "Repair page.",
        "effect": "Campaigns 24274160783 (Geothermal) and 24279798229 (Heating Maintenance & "
                  "Inspection) are left with no enabled ad group and stop serving; 24268690038 "
                  "(Heat Pump & Ductless) stops until the heat-pump groups launch. Budgets "
                  "unchanged.",
        "operations": ([{"op": "PAUSE_AD_GROUP", "ad_group_id": g, "name": n, "missing_page": m,
                         "from": "ENABLED", "to": "PAUSED"}
                        for g, (n, m) in PAUSE_NO_PAGE.items()]
                       + [{"op": "PAUSE_CAMPAIGN_ASSET_LINK", "campaign_id": l["campaign_id"],
                           "asset_id": l["asset_id"], "text": l["text"], "url": l["url"],
                           "from": "ENABLED", "to": "PAUSED"} for l in pause_links])}
    pause_plan["operation_count"] = len(pause_plan["operations"])

    create_ops = ([{"op": "CREATE_SITELINK_ASSET", "key": k, "link_text": t, "final_url": u,
                    "description1": d1, "description2": d2}
                   for k, t, u, d1, d2 in NEW_SITELINKS]
                  + [{"op": "LINK_SITELINK_TO_CAMPAIGN_PAUSED", "campaign_id": camp, "sitelink": k,
                      "existing_asset_id": EXISTING_OFFER_SL.get(k)}
                     for camp, keys in SITELINK_PLAN.items() for k in keys]
                  + migrate_ops + launch_ops)
    create_plan = {
        "customer_id": CID, "exact_account_name": EXACT_NAME, "never_write_to_mcc": "3373711342",
        "built_local": STAMP, "plan_name": "AMB-0924-LP-CREATE-2", "supersedes": "AMB-0924-LP-CREATE-1 2A5C12587E7B (never executed)", "approval_class": "create-paused",
        "everything_created_paused": True, "nothing_enabled": True, "nothing_removed": True,
        "no_budget_bid_or_targeting_change": True,
        "no_heat_hold_released_by": "owner instruction 2026-09-24: build No Heat Repair with "
            "business-hour messaging and no 24/7 or same-day promise. Copy states the "
            "published hours Mon-Fri 8 a.m.-4 p.m.",
        "operations": create_ops}
    create_plan["operation_count"] = len(create_ops)

    enable_draft = {
        "plan_name": "AMB-0924-LP-ENABLE-2", "status": "DRAFT - not approvable until CREATE-1 "
        "executes, reads back clean and its ads are APPROVED",
        "order": ["1 pause the 12 old main-site RSAs", "2 enable the 12 migration copies",
                  "3 enable 12 launch RSAs", f"4 enable {len(launch_kw)} keywords",
                  f"5 enable {len(LAUNCH)} launch ad groups", "6 enable campaign 24268690041 (Thermostat Services)", f"7 enable {sum(len(v) for v in SITELINK_PLAN.values())} sitelink links"],
        "old_ads_to_pause": old_ads, "keywords_to_enable": launch_kw,
        "ad_groups_to_enable": [{"id": g, "name": v[0]} for g, v in LAUNCH.items()],
        "campaigns_to_enable": [{"id": "24268690041", "name": "Thermostat Services", "budget": 15.00,
                                 "enabled_heating_total_after": 305.00, "cap": 325.00}],
        "held_not_enabled": [{"id": g, "name": v[0], "url": v[1], "reason": v[2]}
                             for g, v in HOLD.items()]}

    # ------------------------------------------------ validate_only preflight
    pf = out["preflight"] = {}

    def vo(svc, method, req_type, ops, label):
        if not ops:
            pf[label] = "no ops"; return
        rq = c.get_type(req_type); rq.customer_id = CID; rq.operations.extend(ops)
        rq.partial_failure = False; rq.validate_only = True
        try:
            getattr(c.get_service(svc), method)(request=rq)
            pf[label] = f"VALIDATED {len(ops)}"
        except Exception as ex:
            msg = str(ex)
            m = re.findall(r'message: "([^"]+)"', msg)
            pf[label] = f"FAILED: {m[:3] or msg[:300]}"
            err.append(f"preflight {label}: {m[:3] or msg[:200]}")

    AGS, CAS, AS = (c.get_service("AdGroupService"), c.get_service("CampaignAssetService"),
                    c.get_service("AssetService"))
    from google.protobuf import field_mask_pb2
    fm = field_mask_pb2.FieldMask(paths=["status"])
    ops = []
    for o_ in pause_plan["operations"]:
        if o_["op"] != "PAUSE_AD_GROUP": continue
        o = c.get_type("AdGroupOperation")
        o.update.resource_name = AGS.ad_group_path(CID, o_["ad_group_id"])
        o.update.status = c.enums.AdGroupStatusEnum.PAUSED
        o.update_mask.CopyFrom(fm); ops.append(o)
    vo("AdGroupService", "mutate_ad_groups", "MutateAdGroupsRequest", ops, "PAUSE ad groups")
    ops = []
    for o_ in pause_plan["operations"]:
        if o_["op"] != "PAUSE_CAMPAIGN_ASSET_LINK": continue
        o = c.get_type("CampaignAssetOperation")
        o.update.resource_name = CAS.campaign_asset_path(CID, o_["campaign_id"], o_["asset_id"],
                                                          "SITELINK")
        o.update.status = c.enums.AssetLinkStatusEnum.PAUSED
        o.update_mask.CopyFrom(fm); ops.append(o)
    vo("CampaignAssetService", "mutate_campaign_assets", "MutateCampaignAssetsRequest", ops,
       "PAUSE sitelink links")

    ops = []
    for o_ in create_ops:
        if o_["op"] != "CREATE_SITELINK_ASSET": continue
        o = c.get_type("AssetOperation"); a = o.create
        a.final_urls.append(o_["final_url"])
        a.sitelink_asset.link_text = o_["link_text"]
        a.sitelink_asset.description1 = o_["description1"]
        a.sitelink_asset.description2 = o_["description2"]
        ops.append(o)
    vo("AssetService", "mutate_assets", "MutateAssetsRequest", ops, "CREATE sitelink assets")
    # links: validate against EXISTING offer sitelinks only (new assets have no id yet)
    ops = []
    for o_ in create_ops:
        if o_["op"] != "LINK_SITELINK_TO_CAMPAIGN_PAUSED" or not o_["existing_asset_id"]: continue
        o = c.get_type("CampaignAssetOperation"); x = o.create
        x.campaign = c.get_service("CampaignService").campaign_path(CID, o_["campaign_id"])
        x.asset = AS.asset_path(CID, o_["existing_asset_id"])
        x.field_type = c.enums.AssetFieldTypeEnum.SITELINK
        x.status = c.enums.AssetLinkStatusEnum.PAUSED
        ops.append(o)
    vo("CampaignAssetService", "mutate_campaign_assets", "MutateCampaignAssetsRequest", ops,
       "LINK existing offer sitelinks PAUSED (subset)")

    def rsa_op(o_):
        o = c.get_type("AdGroupAdOperation"); a = o.create
        a.ad_group = c.get_service("AdGroupService").ad_group_path(CID, o_["ad_group_id"])
        a.status = c.enums.AdGroupAdStatusEnum.PAUSED
        a.ad.final_urls.append(o_["final_url"])
        r = a.ad.responsive_search_ad
        for h in o_["headlines"]:
            t = c.get_type("AdTextAsset"); t.text = h["text"]
            if h["pin"] not in ("UNSPECIFIED", "UNKNOWN"):
                t.pinned_field = getattr(c.enums.ServedAssetFieldTypeEnum, h["pin"])
            r.headlines.append(t)
        for d in o_["descriptions"]:
            t = c.get_type("AdTextAsset"); t.text = d["text"]
            if d["pin"] not in ("UNSPECIFIED", "UNKNOWN"):
                t.pinned_field = getattr(c.enums.ServedAssetFieldTypeEnum, d["pin"])
            r.descriptions.append(t)
        if o_["path1"]: r.path1 = o_["path1"]
        if o_["path2"]: r.path2 = o_["path2"]
        return o
    vo("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest",
       [rsa_op(o_) for o_ in migrate_ops], "CREATE migration RSA copies PAUSED")
    vo("AdGroupAdService", "mutate_ad_group_ads", "MutateAdGroupAdsRequest",
       [rsa_op(o_) for o_ in launch_ops], "CREATE launch RSAs PAUSED")

    # ------------------------------------------------ routing-safe negative move
    NEG_TARGETS = [x for x in HEATING_ENABLED if x != "24268690041"] +         ["24132507741", "24132507750", "24132507753"]   # paused cooling, protect for later
    have = set()
    for r in q(c, f"""SELECT campaign.id, campaign_criterion.keyword.text FROM campaign_criterion
                   WHERE campaign_criterion.type = 'KEYWORD' AND campaign_criterion.negative = TRUE
                   AND campaign.id IN ({','.join(NEG_TARGETS)})"""):
        have.add((str(r.campaign.id), r.campaign_criterion.keyword.text.lower()))
    acct = {}
    for r in q(c, f"""SELECT shared_criterion.criterion_id, shared_criterion.keyword.text,
                   shared_criterion.keyword.match_type FROM shared_criterion
                   WHERE shared_set.id = {ACCT_LIST} AND shared_criterion.type = 'KEYWORD'"""):
        if r.shared_criterion.keyword.text.lower() in MOVE_TEXTS:
            acct[str(r.shared_criterion.criterion_id)] = (r.shared_criterion.keyword.text,
                                                          E(r.shared_criterion.keyword.match_type))
    neg_ops = [{"op": "ADD_CAMPAIGN_NEGATIVE", "campaign_id": cid, "text": t, "match": "PHRASE"}
               for cid in NEG_TARGETS for t in sorted(MOVE_TEXTS) if (cid, t) not in have]
    neg_ops += [{"op": "REMOVE_ACCOUNT_LEVEL_NEGATIVE", "shared_set_id": ACCT_LIST,
                 "criterion_id": k, "text": v[0], "match": v[1]} for k, v in sorted(acct.items())]
    neg_plan = {"customer_id": CID, "exact_account_name": EXACT_NAME,
                "never_write_to_mcc": "3373711342", "built_local": STAMP,
                "plan_name": "AMB-0924-NEG-THERMO-1", "approval_class": "negative-keyword-move",
                "order": "adds first (one mutate), then the two account-level removals",
                "why": "Account-level BROAD [thermostat]/[thermostats] block every keyword of the "
                       "approved thermostat services (124 reachable probes). The same exclusion is "
                       "re-created at campaign level on every other enabled heating campaign and the "
                       "three paused cooling campaigns, so no other ad group starts matching "
                       "thermostat searches. A one-word PHRASE negative blocks exactly what a "
                       "one-word BROAD negative blocks.",
                "reversible": "re-add the two account-level negatives",
                "serving_effect_today": "none: Thermostat Services 24268690041 stays PAUSED until ENABLE",
                "operations": neg_ops}
    neg_plan["operation_count"] = len(neg_ops)
    CCS = c.get_service("CampaignCriterionService"); SCS = c.get_service("SharedCriterionService")
    ops = []
    for o_ in neg_ops:
        if o_["op"] != "ADD_CAMPAIGN_NEGATIVE": continue
        o = c.get_type("CampaignCriterionOperation"); x = o.create
        x.campaign = c.get_service("CampaignService").campaign_path(CID, o_["campaign_id"])
        x.negative = True; x.keyword.text = o_["text"]
        x.keyword.match_type = c.enums.KeywordMatchTypeEnum.PHRASE
        ops.append(o)
    vo("CampaignCriterionService", "mutate_campaign_criteria", "MutateCampaignCriteriaRequest",
       ops, "NEG add campaign PHRASE negatives")
    ops = []
    for o_ in neg_ops:
        if o_["op"] != "REMOVE_ACCOUNT_LEVEL_NEGATIVE": continue
        o = c.get_type("SharedCriterionOperation")
        o.remove = SCS.shared_criterion_path(CID, o_["shared_set_id"], o_["criterion_id"])
        ops.append(o)
    vo("SharedCriterionService", "mutate_shared_criteria", "MutateSharedCriteriaRequest",
       ops, "NEG remove account-level thermostat")
    neg_plan["preflight"] = {k: v for k, v in pf.items() if k.startswith("NEG")}
    neg_plan["fingerprint"] = approval_code({k: v for k, v in neg_plan.items() if k != "fingerprint"})
    (PLANS / "AMB-0924-NEG-THERMO-1.json").write_text(json.dumps(neg_plan, indent=1), encoding="utf-8")
    print(f"PLAN AMB-0924-NEG-THERMO-1: {neg_plan['fingerprint']} / {len(neg_ops)} ops "
          f"({sum(1 for o in neg_ops if o['op'].startswith('ADD'))} adds, "
          f"{sum(1 for o in neg_ops if o['op'].startswith('REMOVE'))} removals)")

    # ------------------------------------------------ fingerprints + write
    PLANS.mkdir(parents=True, exist_ok=True)
    for p in (pause_plan, create_plan):
        p["preflight"] = {k: v for k, v in pf.items() if not k.startswith("NEG")
                          and (p is pause_plan) == k.startswith("PAUSE")}
        p["fingerprint"] = approval_code({k: v for k, v in p.items() if k != "fingerprint"})
        (PLANS / f"{p['plan_name']}.json").write_text(json.dumps(p, indent=1), encoding="utf-8")
    (PLANS / "AMB-0924-LP-ENABLE-2.DRAFT.json").write_text(json.dumps(enable_draft, indent=1),
                                                           encoding="utf-8")
    out["plans"] = {p["plan_name"]: {"fingerprint": p["fingerprint"],
                                     "operation_count": p["operation_count"]}
                    for p in (pause_plan, create_plan)}
    out["enable_draft_counts"] = {"old_ads": len(old_ads), "keywords": len(launch_kw),
                                  "ad_groups": len(LAUNCH)}
    (SNAP / f"lp-build-{STAMP}.json").write_text(json.dumps(out, indent=1, default=str),
                                                 encoding="utf-8")

    print("=== PREFLIGHT (validate_only) ===")
    for k, v in pf.items(): print(f"  {k:48s} {v}")
    print(f"\nnegatives tested: {out['negatives_tested']} | reachable conflicts: {len(conflicts)}")
    for x in conflicts[:12]: print("   CONFLICT", x)
    print(f"informational negatives present: {out['informational_negatives_present'][:12]}")
    print(f"\nPAUSE-1 ops: {pause_plan['operation_count']}  "
          f"({len(PAUSE_NO_PAGE)} ad groups + {len(pause_links)} sitelink links)")
    for l in pause_links: print(f"   link {l['campaign_id']} {l['asset_id']} '{l['text']}' -> {l['url']}")
    print(f"CREATE-1 ops: {create_plan['operation_count']} "
          f"({len(NEW_SITELINKS)} sitelinks, {sum(len(v) for v in SITELINK_PLAN.values())} links, "
          f"{len(migrate_ops)} migration RSAs, {len(launch_ops)} launch RSAs)")
    print(f"ENABLE-1 draft: {len(old_ads)} old ads to pause, {len(launch_kw)} keywords, "
          f"{len(LAUNCH)} ad groups")
    for kw in launch_kw: print(f"   kw {kw['ad_group'][7:30]:24s} [{kw['text']}] {kw['match']}")
    print(f"\nWARNINGS ({len(warn)}):"); [print("  ", w) for w in warn]
    print(f"ERRORS ({len(err)}):"); [print("  ", e) for e in err]
    for n, v in out["plans"].items(): print(f"PLAN {n}: {v['fingerprint']} / {v['operation_count']} ops")
    print("EXTERNAL WRITES: 0 (validate_only)")


if __name__ == "__main__":
    main()
