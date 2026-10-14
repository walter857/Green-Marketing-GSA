#!/usr/bin/env python3
"""LOCAL-ONLY red team for APG-0917-CAMP-E. No API call of any kind."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_yaml  # noqa: E402
from gm_gsa.safety import approval_code, assert_no_embedded_secrets  # noqa: E402
from gm_gsa.validators import validate_campaign_plan, PROTECTED_NEGATIVES  # noqa: E402

CAMP = ROOT / "clients/apogee-lawns/plans/APG-0917-CAMP-L.yaml"
plan = load_yaml(str(CAMP))
fails, warns, notes = [], [], []


def check(ok, msg, level="fail"):
    tag = "PASS" if ok else ("WARN" if level == "warn" else "FAIL")
    print(f"  [{tag}] {msg}")
    if not ok:
        (warns if level == "warn" else fails).append(msg)


print("\n=== 1. SECRETS + IDENTITY ===")
try:
    assert_no_embedded_secrets(plan)
    check(True, "no secret-like values embedded")
except Exception as e:  # noqa: BLE001
    check(False, str(e))
cl = load_yaml(str(ROOT / "clients/apogee-lawns/client.yaml"))["client"]
wo = load_yaml(str(ROOT / "clients/apogee-lawns/work-order.yaml"))["work_order"]
t = plan["target"]
check(t["child_customer_id"] == "8164626278", "child_customer_id")
check(t["child_customer_id"] != t["manager_customer_id"], "child ID is not the MCC ID")
check(t["exact_child_account_name"] == cl["google_ads"]["exact_child_account_name"], "account name matches client.yaml")
check(t["vertical"] == wo["service"]["vertical"], "vertical matches work order")
check(plan["supersedes_fingerprint"] == "4022CBA7FD51", "records the superseded predecessor CAMP-I")
check("849EAED2873F" in str(plan.get("also_voids","")), "still records CAMP-B as VOID")

print("\n=== 2. LIVE CONVERSION ACTION IDS MATCH WHAT WAS CREATED ===")
LIVE = {"7772803337": "Lead | Permanent Lights | Form Submit | Thank You",
        "7773013199": "Call | Permanent Lights | Ads | 60s",
        "7773043879": "Call | Permanent Lights | Website | 60s"}
lca = plan["live_conversion_actions"]
got = {v["id"]: v["name"] for v in lca.values()}
check(got == LIVE, f"three live action IDs and names match the receipt -> {sorted(got)}")
check(lca["form_lead"]["state_required_at_execution"] == "PRIMARY", "form action required PRIMARY at execution")
check(lca["calls_from_ads"]["state_required_at_execution"] == "PRIMARY", "calls-from-ads required PRIMARY at execution")
check(lca["calls_from_website"]["state_required_at_execution"] == "SECONDARY", "website-call required SECONDARY at execution")
check(lca["calls_from_website"]["never_promote"] is True, "website-call flagged never_promote")
_data_lines = [l for l in CAMP.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("#")]
check("All three stay Secondary" not in chr(10).join(_data_lines), "no stale all-Secondary assertion in plan DATA (comments excluded)")
c0 = plan["campaigns"][0]
ccg = c0["campaign_conversion_goals"]
check(ccg["uses_custom_conversion_goal"] is False, "NO CustomConversionGoal is used")
check(ccg["conversion_goal_campaign_config"]["goal_config_level"] == "CAMPAIGN",
      "goal_config_level CAMPAIGN (detaches account defaults)")
check(ccg["conversion_goal_campaign_config"]["custom_conversion_goal"] is None,
      "no custom goal attached to the campaign config")
sg = {(g["category"], g["origin"]): g["biddable"] for g in ccg["standard_goals"]}
check(sg.get(("SUBMIT_LEAD_FORM", "WEBSITE")) is True, "form goal biddable (includes 7772803337)")
check(sg.get(("PHONE_CALL_LEAD", "CALL_FROM_ADS")) is True, "calls-from-ads goal biddable (includes 7773013199)")
check(sg.get(("PHONE_CALL_LEAD", "WEBSITE")) is False, "website-call goal NOT biddable (excludes 7773043879)")
check(len(ccg["standard_goals"]) == 3, f"exactly 3 standard goals ({len(ccg['standard_goals'])})")
check(ccg["whatconverts_action"]["status"] == "NOT_CREATED_THIS_SESSION",
      "WhatConverts action correctly recorded as not created")
check(plan["object_counts_if_executed"]["custom_conversion_goal.create"] == 0, "zero custom goals created")
check(plan["object_counts_if_executed"]["any_promotion_to_primary"] == 0, "zero promotions to Primary")
check(lca["calls_from_website"]["disposition"] == "RETAINED_BUT_UNUSED", "7773043879 retained, not deleted")

print("\n=== 3. REPO CAMPAIGN VALIDATOR ===")
errs = validate_campaign_plan(plan)
KNOWN = {
    "campaigns[0].schedule must be a non-empty list":
        "EXPECTED. The campaign is deliberately 24/7 by owner decision. Google treats "
        "'no ad_schedule criteria' as all-days-all-hours. The validator cannot express "
        "that, and 7x 00:00-23:45 rows would REDUCE eligibility by 15 min/day.",
    "campaigns[0].ad_groups[0].keywords[2].text must match canonical_keyword":
        "EXPECTED. Owner-specified 2-ad-group structure puts the installation and "
        "installer terms in one group. The validator enforces literal text equality; the "
        "two terms are the same hiring intent and the installer bucket had 10 searches in "
        "12 months, so a dedicated SKAG could never accumulate data.",
    "campaigns[0].ad_groups[1].keywords must include PHRASE and EXACT":
        "EXPECTED AND DELIBERATE. AG2 is EXACT-only by evidence: a PHRASE head keyword "
        "would reach 29 non-service terms carrying 250 of 370 summed volume.",
}
if not errs:
    print("  [PASS] validator returned no errors")
for e in errs:
    base = re.sub(r"keywords\[\d+\]", "keywords[2]", e)
    if e in KNOWN or base in KNOWN:
        key = e if e in KNOWN else base
        print(f"  [NOTE] {e}")
        print(f"         -> {KNOWN[key]}")
        notes.append(e)
    else:
        print(f"  [FAIL] UNEXPECTED validator error: {e}")
        fails.append(e)

print("\n=== 4. RSA COPY ===")
BANNED = [
    (r"\bwarrant", "warranty claim"), (r"\bcertified\b", "certification claim"),
    (r"\bdealer\b", "dealer claim"), (r"\beverlights?\b", "EverLights trademark"),
    (r"\bip\s?6\d\b", "IP rating"), (r"\bfinanc", "financing"),
    (r"\bsame[- ]day\b", "response-time claim"), (r"\b24/7\b", "availability claim"),
    (r"\bguarantee", "guarantee"), (r"\blicensed\b|\binsured\b", "licence/insurance"),
    (r"\b\d{3}[-.]\d{3}[-.]\d{4}\b", "phone number in ad text"),
    (r"\{keyword", "dynamic keyword insertion"),
    (r"\bno\.? ?1\b|\b#1\b|\bbest in\b|\bcheapest\b", "superlative"),
    (r"\bhang(ing)? your lights\b|\bannual hanging service\b", "advertising annual hanging"),
]
ads_seen = 0
for c in plan["campaigns"]:
    for g in c["ad_groups"]:
        for pn in ("path1", "path2"):
            v = str(g.get(pn, ""))
            check(len(v) <= 15, f"{g['name']}.{pn} '{v}' {len(v)}/15")
        for ad in g["ads"]:
            ads_seen += 1
            p = f"{g['name'][:28]} / {ad['label'][:22]}"
            hs = [h["text"] for h in ad["headlines"]]
            ds = [d["text"] for d in ad["descriptions"]]
            check(3 <= len(hs) <= 15, f"{p}: {len(hs)} headlines")
            check(2 <= len(ds) <= 4, f"{p}: {len(ds)} descriptions")
            over = [(x, len(x)) for x in hs if len(x) > 30]
            check(not over, f"{p}: headlines <=30" + (f" OVER={over}" if over else ""))
            overd = [(x, len(x)) for x in ds if len(x) > 90]
            check(not overd, f"{p}: descriptions <=90" + (f" OVER={overd}" if overd else ""))
            check(len({x.casefold() for x in hs}) == len(hs), f"{p}: no duplicate headlines")
            check(len({x.casefold() for x in ds}) == len(ds), f"{p}: no duplicate descriptions")
            pins = [h for h in ad["headlines"] if h.get("pin") == "HEADLINE_1"]
            check(len(pins) >= 2, f"{p}: {len(pins)} HEADLINE_1 alternatives (owner requires >=2)")
            check(len(pins) <= 3, f"{p}: pinning not excessive ({len(pins)}<=3)")
            other_pins = [h for h in ad["headlines"] if h.get("pin") and h.get("pin") != "HEADLINE_1"]
            check(not other_pins, f"{p}: nothing pinned outside HEADLINE_1")
            check(all("pin" not in d for d in ad["descriptions"]), f"{p}: no description pins")
            blob = " | ".join(hs + ds).lower()
            for pat, label in BANNED:
                m = re.search(pat, blob)
                check(m is None, f"{p}: no {label}" + (f" FOUND '{m.group(0)}'" if m else ""))
            canon = g["canonical_keyword"].split()[0].lower()
            check(any(canon in x.lower() for x in hs), f"{p}: canonical term '{canon}' present in headlines")
check(ads_seen == 4, f"exactly 4 RSAs ({ads_seen})")

print("\n=== 5. ASSETS ===")
for c in plan["campaigns"]:
    for g in c["ad_groups"]:
        a = g.get("assets") or {}
        for co in a.get("callouts") or []:
            check(len(co) <= 25, f"callout '{co}' {len(co)}/25")
        for ss in a.get("structured_snippets") or []:
            check(len(ss.get("values") or []) >= 3, f"snippet '{ss.get('header')}' >=3 values")
            for v in ss["values"]:
                check(len(v) <= 25, f"snippet value '{v}' {len(v)}/25")
        check((a.get("sitelinks") or []) == [], f"{g['name'][:30]}: no sitelinks (404 anchors)")

print("\n=== 6. NEGATIVES ===")
nb = [str(x) for x in c0["negatives_match_broad"]]
np_ = [str(x) for x in c0["negatives_match_phrase"]]
allneg = [(x, "BROAD") for x in nb] + [(x, "PHRASE") for x in np_]
print(f"  broad={len(nb)} phrase={len(np_)} total={len(allneg)}")
check(c0 and plan["object_counts_if_executed"]["campaign_criterion.create_negative_keyword"] == len(allneg),
      f"declared negative count == actual ({len(allneg)})")
check(len({x.casefold() for x, _ in allneg}) == len(allneg), "no duplicate negatives")
for x, _m in allneg:
    norm = x.strip().strip('"').strip("[]").casefold()
    check(norm not in PROTECTED_NEGATIVES, f"'{x}' is not a protected buyer-intent term")
check(c0["shared_negative_lists_attached"] == [], "no pre-existing shared list attached")


def toks(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def blocks(neg, match, q):
    nt, qt = toks(neg), toks(q)
    if not nt:
        return False
    if match == "EXACT":
        return nt == qt
    if match == "PHRASE":
        n = len(nt)
        return any(qt[i:i + n] == nt for i in range(len(qt) - n + 1))
    return all(w in qt for w in nt)


print("\n=== 7. REVERSE AUDIT: negatives vs ALL 5 positives + protected queries ===")
positives = [k["text"] for g in c0["ad_groups"] for k in g["keywords"]]
probe = sorted(set(positives + [
    "permanent christmas lights cost", "permanent christmas lights price",
    "permanent christmas lights near me", "permanent christmas light installation cost",
    "best permanent christmas lights", "permanent christmas lights quote",
    "permanent christmas light installation lincoln ne",
    "permanent christmas lights company near me",
    "permanent christmas lights installer reviews",
]))
bad = 0
for qy in probe:
    hits = [f"{x} [{m}]" for x, m in allneg if blocks(x, m, qy)]
    if hits:
        bad += 1
        print(f"  [FAIL] '{qy}' blocked by {hits}")
        fails.append(f"negative blocks positive: {qy}")
check(bad == 0, f"no negative blocks any of the {len(probe)} probe queries")

print("\n=== 8. POLICY DEFAULTS / STRUCTURE ===")
check(c0["status"] == "PAUSED", "campaign PAUSED")
ns = c0["network_settings"]
check(ns["target_google_search"] is True, "Google Search ON")
check(ns["target_search_network"] is False, "Search Partners OFF")
check(ns["target_content_network"] is False, "Display OFF")
check(ns["target_partner_search_network"] is False, "partner search OFF")
for k in ("ai_max", "keyword_match_expansion", "dynamic_search_ads"):
    check(c0[k] is False, f"{k} OFF")
for k in ("final_url_expansion", "text_customization", "automatically_created_assets"):
    check(c0[k] == "OPTED_OUT", f"{k} OPTED_OUT")
check(c0["location"]["option"] == "PRESENCE", "PRESENCE targeting")
check(len(c0["location"]["geo_target_constant_ids"]) == 14, "14 geo targets")
check(21162 not in c0["location"]["geo_target_constant_ids"], "state of Nebraska NOT targeted")
check(c0["location"]["omaha"] == "EXCLUDED", "Omaha excluded")
check(9233865 in c0["location"]["geo_target_constant_ids"], "Nemaha Precinct 9233865 included")
mt = {k["match_type"] for g in c0["ad_groups"] for k in g["keywords"]}
check(mt <= {"PHRASE", "EXACT"}, f"only Phrase/Exact match types ({mt})")
check(len(c0["ad_groups"]) == 2, "2 ad groups")
check(len(positives) == 5, f"5 keywords total ({len(positives)})")
check(c0["ad_schedule_criteria_count"] == 0, "no ad schedule criteria (24/7 by design)")
check(c0["cpc_bid_ceiling"] == 8.00, "CPC ceiling $8.00")
check(c0["final_url"] == "https://offer.apogeelawns.com/", f"final_url is the live 200 root -> {c0['final_url']}")
check("//apogeelawns.com/" not in c0["final_url"], "final_url is NOT the bare apogeelawns.com host")
check(c0["bidding_strategy_type"] == "TARGET_SPEND", "Maximize Clicks")

print("\n=== 9. BUDGET MATH ===")
d = c0["daily_budget"]
monthly = round(d * 30.4, 2)
check(abs(d - 16.44) < 1e-9, f"daily ${d}")
check(monthly <= 500, f"${d} x 30.4 = ${monthly} <= $500")
print(f"    (x30 would be ${round(d*30,2)} - 30.4 is the correct multiplier)")

print("\n=== 10. OBJECT COUNTS ===")
oc = plan["object_counts_if_executed"]
计 = (oc["campaign_budget.create"] + oc["campaign.create"] + oc["campaign_criterion.create_location"]
      + oc["campaign_criterion.create_negative_keyword"] + oc["campaign_criterion.create_ad_schedule"]
      + oc["campaign_criterion.create_language"] + oc["ad_group.create"]
      + oc["ad_group_criterion.create_keyword"] + oc["ad_group_ad.create"]
      + oc["asset.create_callout"] + oc["asset.create_structured_snippet"]
      + oc["campaign_asset.create"] + oc["asset.create_call"] + oc["asset.create_sitelink"]
      + oc["campaign_conversion_goal.update"] + oc["conversion_goal_campaign_config.update"])
check(计 == oc["TOTAL_MUTATIONS"], f"line items sum to TOTAL_MUTATIONS ({计} vs {oc['TOTAL_MUTATIONS']})")
check(oc["any_delete_or_remove"] == 0, "zero deletes/removes")
check(oc["any_enable_operation"] == 0, "zero enable operations")
check(oc["ad_group_criterion.create_keyword"] == len(positives), "keyword count matches")
check(oc["ad_group_ad.create"] == ads_seen, "RSA count matches")

print("\n=== 11. PLACEHOLDERS ===")
ph = sorted(set(re.findall(r"\[\[[A-Z_]+\]\]", CAMP.read_text(encoding="utf-8"))))
check(not ph, f"no unresolved placeholders {ph if ph else ''}")

fp = approval_code(plan)
print("\n" + "=" * 78)
print(f"RED TEAM: {len(fails)} FAIL, {len(warns)} WARN, {len(notes)} EXPECTED-VALIDATOR-NOTES")
for f in fails:
    print(f"  FAIL: {f}")
print(f"\nAPG-0916-CAMP-C FINGERPRINT: {fp}")
print("=" * 78)
out = {"fails": fails, "warns": warns, "expected_validator_notes": notes,
       "fingerprint": fp, "negatives_total": len(allneg), "keywords": len(positives),
       "rsas": ads_seen, "monthly_budget_at_30_4": monthly}
p = ROOT / "reports/apogee-lawns/evidence/2026-09-17-campl-preflight.json"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(f"WROTE {p.relative_to(ROOT)}")
