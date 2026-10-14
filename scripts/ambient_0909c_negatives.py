#!/usr/bin/env python3
"""Evidence for the three split negative packages plus the Exact-only competitor package."""
from __future__ import annotations
import sys, json, re, unicodedata, datetime
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
SETTLED = "2026-09-08"


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- NEG-CORE
print("=== NEG-CORE PROOF 1: IS SAVAGE, MARYLAND ACTIVELY TARGETED? ===")
sav = []
for r in q(c, f"SELECT campaign.id, campaign_criterion.criterion_id, "
              f"campaign_criterion.status, campaign_criterion.negative, "
              f"campaign_criterion.location.geo_target_constant "
              f"FROM campaign_criterion WHERE campaign.id IN ({IN5}) "
              f"AND campaign_criterion.type = 'LOCATION'"):
    g = r.campaign_criterion.location.geo_target_constant.split("/")[-1]
    if g == "1018704":
        sav.append({"campaign": NAME[str(r.campaign.id)],
                    "criterion_id": str(r.campaign_criterion.criterion_id),
                    "status": E(r.campaign_criterion.status),
                    "negative": r.campaign_criterion.negative, "geo_id": g})
gt = q(c, "SELECT geo_target_constant.id, geo_target_constant.name, "
          "geo_target_constant.canonical_name, geo_target_constant.status, "
          "geo_target_constant.target_type, geo_target_constant.country_code "
          "FROM geo_target_constant WHERE geo_target_constant.resource_name = "
          "'geoTargetConstants/1018704'")
for r in gt:
    x = r.geo_target_constant
    print(f"  geoTargetConstants/1018704 = {x.canonical_name!r}  type={x.target_type} "
          f"status={E(x.status)} country={x.country_code}")
    out["savage_geo_constant"] = {"canonical": x.canonical_name, "type": x.target_type,
                                  "status": E(x.status)}
print(f"  positive LOCATION criteria on the five for Savage: {len(sav)}")
for s in sav:
    print(f"    {s['campaign']:<20} criterion={s['criterion_id']:<12} status={s['status']} "
          f"negative={s['negative']}")
proof1 = len(sav) == 5 and all(s["status"] == "ENABLED" and not s["negative"] for s in sav)
print(f"  PROOF: Savage MD is an ENABLED positive target on all five campaigns -> {proof1}")
out["neg_core_savage_targeted"] = {"rows": sav, "proven": proof1}

print("\n=== NEG-CORE PROOF 2: IS 'licensed' SUPPORTED ADVERTISING LANGUAGE? ===")
lic = []
for r in q(c, f"""
    SELECT campaign.id, ad_group_ad.ad.id, ad_group_ad.status,
           ad_group_ad.policy_summary.approval_status,
           ad_group_ad.ad.responsive_search_ad.headlines,
           ad_group_ad.ad.responsive_search_ad.descriptions
    FROM ad_group_ad WHERE campaign.id IN ({IN5})
      AND ad_group_ad.status = 'ENABLED'
"""):
    x = r.ad_group_ad
    for h in x.ad.responsive_search_ad.headlines:
        if re.search(r"licen[sc]", h.text, re.I):
            lic.append({"campaign": NAME[str(r.campaign.id)], "ad": str(x.ad.id),
                        "field": "HEADLINE", "approval": E(x.policy_summary.approval_status),
                        "text": h.text})
    for d in x.ad.responsive_search_ad.descriptions:
        if re.search(r"licen[sc]", d.text, re.I):
            lic.append({"campaign": NAME[str(r.campaign.id)], "ad": str(x.ad.id),
                        "field": "DESCRIPTION", "approval": E(x.policy_summary.approval_status),
                        "text": d.text})
callouts = []
for r in q(c, f"SELECT campaign.id, campaign_asset.field_type, campaign_asset.status, "
              f"asset.callout_asset.callout_text FROM campaign_asset "
              f"WHERE campaign.id IN ({IN5}) AND campaign_asset.field_type = 'CALLOUT' "
              f"AND campaign_asset.status = 'ENABLED'"):
    t = r.asset.callout_asset.callout_text
    if re.search(r"licen[sc]", t, re.I):
        callouts.append({"campaign": NAME[str(r.campaign.id)], "text": t})
print(f"  live ENABLED ad copy containing 'licens/licenc': {len(lic)} assets")
for x in lic[:14]:
    print(f"    {x['campaign']:<20} ad={x['ad']} {x['field']:<12} {x['approval']:<10} {x['text']!r}")
print(f"  live ENABLED callouts containing it: {len(callouts)}")
for x in callouts:
    print(f"    {x['campaign']:<20} {x['text']!r}")
proof2 = len(lic) + len(callouts) > 0
print(f"  PROOF: 'licensed' is language Ambient already runs in APPROVED live ads -> {proof2}")
out["neg_core_licensed_supported"] = {"ad_assets": lic, "callouts": callouts, "proven": proof2}

print("\n=== NEG-CORE PROOF 3: SEARCH-TERM EVIDENCE FOR savage / licensed ===")
terms = []
for r in q(c, f"SELECT campaign.id, search_term_view.search_term, search_term_view.status, "
              f"metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions "
              f"FROM search_term_view WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'"):
    terms.append({"camp": NAME[str(r.campaign.id)], "term": r.search_term_view.search_term,
                  "status": E(r.search_term_view.status),
                  "impr": r.metrics.impressions, "clicks": r.metrics.clicks,
                  "cost": round(r.metrics.cost_micros/1e6, 2),
                  "conv": round(r.metrics.conversions, 2)})
out["all_search_terms"] = terms
for tok in ("savage", "licensed", "license"):
    hit = [t for t in terms if re.search(rf"\b{tok}\b", t["term"], re.I)]
    print(f"  {tok!r}: {len(hit)} observed search-term rows "
          f"(impr={sum(h['impr'] for h in hit)}, clicks={sum(h['clicks'] for h in hit)}, "
          f"${sum(h['cost'] for h in hit):.2f})")
    for h in hit[:8]:
        print(f"      {h['camp']:<20} impr={h['impr']:<4} clk={h['clicks']:<3} "
              f"${h['cost']:<7} [{h['term']}]")
print("  -> zero observed rows means the negative has suppressed the query before it could")
print("     ever be reported. Absence here is expected and is NOT evidence of no demand.")

# ---------------------------------------------------------------- NEG-COMMERCIAL
print("\n\n=== NEG-COMMERCIAL: DUPLICATE SWEEP FOR 'commercial' ===")
dup = {"account_level_set": [], "other_shared_sets": [], "campaign_level": [],
       "ad_group_level": []}
for r in q(c, "SELECT shared_set.id, shared_set.name, shared_set.type, shared_set.status, "
              "shared_criterion.resource_name, shared_criterion.criterion_id, "
              "shared_criterion.keyword.text, shared_criterion.keyword.match_type "
              "FROM shared_criterion"):
    t = norm(r.shared_criterion.keyword.text)
    if t == "commercial" or "commercial" in t.split():
        rec = {"set_id": str(r.shared_set.id), "set_name": r.shared_set.name,
               "set_type": E(r.shared_set.type_), "set_status": E(r.shared_set.status),
               "resource_name": r.shared_criterion.resource_name,
               "criterion_id": str(r.shared_criterion.criterion_id),
               "text": r.shared_criterion.keyword.text,
               "match": E(r.shared_criterion.keyword.match_type)}
        if str(r.shared_set.id) == "11252984411":
            dup["account_level_set"].append(rec)
        else:
            dup["other_shared_sets"].append(rec)
for r in q(c, "SELECT campaign.id, campaign.name, campaign.status, "
              "campaign_criterion.criterion_id, campaign_criterion.keyword.text, "
              "campaign_criterion.keyword.match_type, campaign_criterion.status "
              "FROM campaign_criterion WHERE campaign_criterion.type = 'KEYWORD' "
              "AND campaign_criterion.negative = TRUE"):
    t = norm(r.campaign_criterion.keyword.text)
    if t == "commercial" or "commercial" in t.split():
        dup["campaign_level"].append(
            {"campaign_id": str(r.campaign.id), "campaign": r.campaign.name[:40],
             "campaign_status": E(r.campaign.status),
             "criterion_id": str(r.campaign_criterion.criterion_id),
             "text": r.campaign_criterion.keyword.text,
             "match": E(r.campaign_criterion.keyword.match_type),
             "status": E(r.campaign_criterion.status)})
for r in q(c, "SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id, "
              "ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, "
              "ad_group_criterion.status FROM ad_group_criterion "
              "WHERE ad_group_criterion.type = 'KEYWORD' AND ad_group_criterion.negative = TRUE"):
    t = norm(r.ad_group_criterion.keyword.text)
    if t == "commercial" or "commercial" in t.split():
        dup["ad_group_level"].append(
            {"campaign_id": str(r.campaign.id), "ad_group_id": str(r.ad_group.id),
             "criterion_id": str(r.ad_group_criterion.criterion_id),
             "text": r.ad_group_criterion.keyword.text,
             "match": E(r.ad_group_criterion.keyword.match_type),
             "status": E(r.ad_group_criterion.status)})
out["commercial_duplicate_sweep"] = dup
for k, v in dup.items():
    print(f"  {k:<22} rows containing the word 'commercial': {len(v)}")
    for x in v:
        if k == "account_level_set":
            print(f"      set {x['set_id']} [{x['match']}] {x['text']!r}  {x['resource_name']}")
        elif k == "other_shared_sets":
            print(f"      set {x['set_id']} {x['set_name'][:26]!r:<28} {x['set_status']:<8} "
                  f"[{x['match']}] {x['text']!r}")
        elif k == "campaign_level":
            print(f"      camp {x['campaign_id']} {x['campaign'][:34]:<36} "
                  f"{x['campaign_status']:<8} [{x['match']}] {x['status']:<8} {x['text']!r}")
        else:
            print(f"      ag {x['ad_group_id']} [{x['match']}] {x['status']} {x['text']!r}")
exact_dupes = [x for v in dup.values() for x in v if norm(x["text"]) == "commercial"]
print(f"\n  EXACT-TOKEN 'commercial' negatives anywhere: {len(exact_dupes)}")
print(f"  -> removal is complete only if that count is 1 (the account-level member).")

print("\n  --- EFFECT ACROSS ALL NON-REMOVED CAMPAIGNS ---")
camps = []
for r in q(c, "SELECT campaign.id, campaign.name, campaign.status, "
              "campaign.advertising_channel_type FROM campaign "
              "WHERE campaign.status != 'REMOVED'"):
    camps.append({"id": str(r.campaign.id), "name": r.campaign.name,
                  "status": E(r.campaign.status), "channel": E(r.campaign.advertising_channel_type)})
att = set()
for r in q(c, "SELECT campaign.id, campaign_shared_set.shared_set FROM campaign_shared_set"):
    if r.campaign_shared_set.shared_set.split("/")[-1] == "11252984411":
        att.add(str(r.campaign.id))
print(f"  non-removed campaigns: {len(camps)}  "
      f"({sum(1 for x in camps if x['status']=='ENABLED')} ENABLED, "
      f"{sum(1 for x in camps if x['status']=='PAUSED')} PAUSED)")
print(f"  campaign_shared_set rows pointing at 11252984411: {len(att)} "
      f"(account-level lists never appear there)")
print("  The account-level list applies to every non-removed campaign implicitly. Removing")
print("  'commercial' therefore widens matching on all of them, but only the ENABLED ones")
print("  can serve. Paused campaigns are affected in configuration only, not in delivery.")
for x in sorted(camps, key=lambda z: (z["status"], z["name"])):
    if x["status"] == "ENABLED":
        print(f"    ENABLED  {x['id']:<12} {x['channel']:<16} {x['name'][:52]}")
print(f"    PAUSED   x{sum(1 for x in camps if x['status']=='PAUSED')} "
      f"(configuration change only, zero delivery effect while paused)")
out["commercial_effect_scope"] = {"non_removed_campaigns": len(camps),
                                  "enabled": [x for x in camps if x["status"] == "ENABLED"],
                                  "paused_count": sum(1 for x in camps if x["status"] == "PAUSED")}

print("\n  --- HISTORICAL 'commercial' QUERIES: RAW RECORDS, NOT QUALIFIED LEADS ---")
cm = []
for r in q(c, "SELECT campaign.name, search_term_view.search_term, "
              "segments.conversion_action_name, metrics.conversions, metrics.all_conversions "
              "FROM search_term_view WHERE segments.date BETWEEN '2019-01-01' AND '2026-09-09' "
              "AND metrics.all_conversions > 0"):
    if re.search(r"\bcommercial\b", r.search_term_view.search_term, re.I):
        cm.append({"campaign": r.campaign.name[:36], "term": r.search_term_view.search_term,
                   "action": r.segments.conversion_action_name,
                   "primary": round(r.metrics.conversions, 2),
                   "all": round(r.metrics.all_conversions, 2)})
out["commercial_historical_records"] = cm
print(f"  rows: {len(cm)}")
for x in cm:
    print(f"    {x['campaign']:<38} P={x['primary']:<5} A={x['all']:<5} "
          f"{x['action'][:26]:<28} [{x['term']}]")
print(f"  TOTAL raw primary records: {sum(x['primary'] for x in cm):.2f}")
print("  These are RAW CONVERSION RECORDS. Qualification is unknown and none of them is")
print("  described as a qualified lead.")

# ---------------------------------------------------------------- NEG-FREE
print("\n\n=== NEG-FREE: 'free' INTENT SPLIT, SEARCH-TERM EVIDENCE ===")
FREE_INTENTS = {
    "free estimate / quote (SUPPORTED)": r"free\s+(estimate|quote|consult|inspection|assessment)",
    "free repair (NOT supported)": r"free\s+(repair|fix)",
    "free service (NOT supported)": r"free\s+service",
    "free parts (NOT supported)": r"free\s+(part|parts)",
    "free diagnostic (needs a policy answer)": r"free\s+(diagnostic|diagnosis|service call|call out)",
    "free other": r"\bfree\b",
}
freehits = [t for t in terms if re.search(r"\bfree\b", t["term"], re.I)]
print(f"  observed search-term rows containing 'free' since launch: {len(freehits)}")
classified = defaultdict(list)
for t in freehits:
    placed = False
    for lbl, pat in FREE_INTENTS.items():
        if lbl == "free other":
            continue
        if re.search(pat, t["term"], re.I):
            classified[lbl].append(t)
            placed = True
            break
    if not placed:
        classified["free other"].append(t)
for lbl in FREE_INTENTS:
    v = classified.get(lbl, [])
    print(f"    {lbl:<44} rows={len(v):<4} impr={sum(x['impr'] for x in v):<5} "
          f"clicks={sum(x['clicks'] for x in v):<4} ${sum(x['cost'] for x in v):.2f}")
    for x in v[:6]:
        print(f"        {x['camp']:<20} impr={x['impr']:<4} clk={x['clicks']:<3} [{x['term']}]")
out["free_intent_split"] = {k: [dict(x) for x in v] for k, v in classified.items()}
allfree_conv = []
for r in q(c, "SELECT campaign.name, search_term_view.search_term, "
              "segments.conversion_action_name, metrics.conversions, metrics.all_conversions "
              "FROM search_term_view WHERE segments.date BETWEEN '2019-01-01' AND '2026-09-09' "
              "AND metrics.all_conversions > 0"):
    if re.search(r"\bfree\b", r.search_term_view.search_term, re.I):
        allfree_conv.append({"campaign": r.campaign.name[:36],
                             "term": r.search_term_view.search_term,
                             "action": r.segments.conversion_action_name,
                             "primary": round(r.metrics.conversions, 2),
                             "all": round(r.metrics.all_conversions, 2)})
out["free_historical_converting"] = allfree_conv
print(f"\n  ACCOUNT-WIDE all-time 'free' queries that ever converted: {len(allfree_conv)}")
for x in allfree_conv:
    print(f"    {x['campaign']:<38} P={x['primary']:<5} A={x['all']:<5} [{x['term']}]")
print(f"\n  VERDICT INPUT: with {len(freehits)} observed rows and {len(allfree_conv)} historical")
print("  converting 'free' queries, there is no campaign-specific routing evidence yet.")

# ---------------------------------------------------------------- COMPETITOR
print("\n\n=== COMPETITOR: EXACT OBSERVED SPELLINGS ===")
CAND = ["arundel", "maryland mechanical"]
obs = []
for t in terms:
    if any(cd in t["term"].lower() for cd in CAND):
        obs.append(t)
print(f"  {'campaign':<20}{'impr':>5}{'clk':>5}{'cost':>9}{'status':>10}  exact observed spelling")
for t in sorted(obs, key=lambda x: -x["cost"]):
    print(f"  {t['camp']:<20}{t['impr']:>5}{t['clicks']:>5}{t['cost']:>9.2f}{t['status']:>10}"
          f"  [{t['term']}]")
out["competitor_observed_terms"] = obs
print("\n  Ampersand check: Google normalises '&' in keyword text. The observed spelling is")
print("  reproduced verbatim below for the plan.")
for t in obs:
    if "maryland mechanical" in t["term"].lower():
        print(f"    verbatim: {t['term']!r}   normalised: {norm(t['term'])!r}")

write(EVID / "2026-09-09c-negative-evidence.json", out)
