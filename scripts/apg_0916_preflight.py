#!/usr/bin/env python3
"""2026-09-16 LOCAL-ONLY pre-approval red team for the Apogee Lawns plans.

Issues no API call of any kind. validate_only burns the same daily mutate quota as
a real write, so nothing here touches Google.
"""
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

CONV = ROOT / "clients/apogee-lawns/plans/APG-0916-CONV-A.yaml"
CAMP = ROOT / "clients/apogee-lawns/plans/APG-0916-CAMP-B.yaml"

fails: list[str] = []
warns: list[str] = []


def check(ok, msg, warn=False):
    tag = "PASS" if ok else ("WARN" if warn else "FAIL")
    print(f"  [{tag}] {msg}")
    if not ok:
        (warns if warn else fails).append(msg)


conv = load_yaml(str(CONV))
camp = load_yaml(str(CAMP))

# ---------------------------------------------------------------- 1. secrets
print("\n=== 1. SECRET SCAN ===")
for name, doc in (("CONV-A", conv), ("CAMP-B", camp)):
    try:
        assert_no_embedded_secrets(doc)
        check(True, f"{name}: no secret-like values embedded")
    except Exception as exc:  # noqa: BLE001
        check(False, f"{name}: {exc}")

# ---------------------------------------------------------------- 2. identity
print("\n=== 2. CLIENT TRUTH / IDENTITY ===")
client = load_yaml(str(ROOT / "clients/apogee-lawns/client.yaml"))["client"]
wo = load_yaml(str(ROOT / "clients/apogee-lawns/work-order.yaml"))["work_order"]
for name, doc in (("CONV-A", conv), ("CAMP-B", camp)):
    t = doc["target"]
    check(t["child_customer_id"] == "8164626278", f"{name}: child_customer_id == 8164626278")
    check(t["child_customer_id"] != t["manager_customer_id"], f"{name}: child ID is not the MCC ID")
    check(t["exact_child_account_name"] == "Apogee Lawns LLC - Live", f"{name}: exact account name")
    check("- live" in t["exact_child_account_name"].lower(), f"{name}: '- live' marker present")
    check(t["exact_child_account_name"] == client["google_ads"]["exact_child_account_name"],
          f"{name}: account name matches client.yaml")
    check(t["child_customer_id"] == client["google_ads"]["child_customer_id"],
          f"{name}: customer ID matches client.yaml")
    check(t["vertical"] == wo["service"]["vertical"], f"{name}: vertical matches the work order")
    check(t["exact_primary_service"] == wo["service"]["exact_primary_service"],
          f"{name}: exact service matches the work order")

# ---------------------------------------------------------------- 3. gate
print("\n=== 3. SCOPE / APPROVAL GATE ===")
sc = wo["scope_approval"]
check(sc.get("approved") is True,
      "similar-local-service scope_approval.approved is true (BLK-001)")
check("[[" not in str(sc.get("approved_by")), "scope_approval.approved_by is a real name (BLK-001)")
check("[[" not in str(sc.get("reason")), "scope_approval.reason is filled in (BLK-001)")
check(wo["task"]["mode"] == "read", "work order mode is READ on this pass (no write authorized)")

# ---------------------------------------------------------------- 4. CONV-A
print("\n=== 4. CONV-A FIELD VALIDITY ===")
VALID_TYPE = {"WEBPAGE", "AD_CALL", "WEBSITE_CALL"}
VALID_CAT = {"SUBMIT_LEAD_FORM", "PHONE_CALL_LEAD"}
objs = conv["objects"]
check(len(objs) == 3, f"CONV-A has exactly 3 objects (found {len(objs)})")
names = [o["name"] for o in objs]
check(len(set(names)) == 3, "CONV-A action names are unique")
for o in objs:
    f = o["fields"]
    p = f"CONV-A[{o['ordinal']}] {o['name'][:40]}"
    check(f["type"] in VALID_TYPE, f"{p}: type {f['type']} is a valid ConversionActionType")
    check(f["category"] in VALID_CAT, f"{p}: category {f['category']} is valid")
    check(f["primary_for_goal"] is False, f"{p}: created SECONDARY (primary_for_goal false)")
    check(f["counting_type"] == "ONE_PER_CLICK", f"{p}: counting_type ONE_PER_CLICK")
    check(f["value_settings.default_value"] == 0.0, f"{p}: no invented revenue value")
    check(f["value_settings.always_use_default_value"] is False, f"{p}: always_use_default_value false")
    if f["category"] == "PHONE_CALL_LEAD":
        check(f.get("phone_call_duration_seconds") == 60, f"{p}: 60-second minimum duration")
    else:
        check("phone_call_duration_seconds" not in f, f"{p}: no call duration on a web action")
check(sum(1 for o in objs if o["fields"]["type"] == "AD_CALL") == 1, "exactly one calls-from-ads action")
check(sum(1 for o in objs if o["fields"]["type"] == "WEBSITE_CALL") == 1, "exactly one calls-from-website action")
check(conv["object_counts"]["TOTAL_MUTATIONS"] == len(objs), "CONV-A object count matches the object list")
check(conv["object_counts"]["any_delete_or_remove"] == 0, "CONV-A performs no delete or remove")
check(conv["conversion_ownership"]["google_ads_conversion_customer"] == "8164626278",
      "CONV-A targets the owning account (no cross-account ownership change)")

# ---------------------------------------------------------------- 5. CAMP-B
print("\n=== 5. CAMP-B AGAINST validate_campaign_plan ===")
errs = validate_campaign_plan(camp)
if not errs:
    print("  [PASS] campaign plan validator returned no errors")
else:
    print(f"  campaign plan validator returned {len(errs)} error(s):")
    for e in errs:
        print(f"    - {e}")
        fails.append(f"CAMP-B validator: {e}")

# ---------------------------------------------------------------- 6. copy
print("\n=== 6. RSA CHARACTER LIMITS AND CLAIM SCAN ===")
BANNED = [
    (r"\b\d+\s*[- ]?year\b.{0,20}warranty", "warranty term"),
    (r"\bwarrant", "warranty claim"),
    (r"\bcertified\b", "certification claim"),
    (r"\bdealer\b", "dealer claim"),
    (r"\beverlights?\b", "EverLights trademark"),
    (r"\bip\s?6\d\b", "IP rating claim"),
    (r"\bfinanc", "financing claim"),
    (r"\bsame[- ]day\b", "response-time claim"),
    (r"\b24/7\b", "availability claim"),
    (r"\bguarantee", "guarantee claim"),
    (r"\blicensed\b|\binsured\b", "licence/insurance claim"),
    (r"\b\d+\s*(\+)?\s*(star|stars|reviews|years in business)\b", "rating/tenure claim"),
    (r"\b\d{3}[-.]\d{3}[-.]\d{4}\b", "phone number in ad text"),
    (r"\bno\.? ?1\b|\b#1\b|\bbest in\b", "superlative claim"),
]
ads_seen = 0
for c in camp["campaigns"]:
    for g in c["ad_groups"]:
        for pn in ("path1", "path2"):
            v = str(g.get(pn, ""))
            check(len(v) <= 15, f"{g['name']}.{pn} '{v}' is {len(v)}/15 chars")
        for ad in g["ads"]:
            ads_seen += 1
            p = f"{g['name']} / {ad['label']}"
            hs = [h["text"] for h in ad["headlines"]]
            ds = [d["text"] for d in ad["descriptions"]]
            check(3 <= len(hs) <= 15, f"{p}: {len(hs)} headlines (3-15)")
            check(2 <= len(ds) <= 4, f"{p}: {len(ds)} descriptions (2-4)")
            over = [(t, len(t)) for t in hs if len(t) > 30]
            check(not over, f"{p}: all headlines <= 30 chars" + (f" -- OVER: {over}" if over else ""))
            overd = [(t, len(t)) for t in ds if len(t) > 90]
            check(not overd, f"{p}: all descriptions <= 90 chars" + (f" -- OVER: {overd}" if overd else ""))
            check(len({t.casefold() for t in hs}) == len(hs), f"{p}: no duplicate headlines")
            check(len({t.casefold() for t in ds}) == len(ds), f"{p}: no duplicate descriptions")
            pins = [h for h in ad["headlines"] if h.get("pin") == "HEADLINE_1"]
            check(len(pins) == 1, f"{p}: exactly one HEADLINE_1 pin (found {len(pins)})")
            check(all("pin" not in h for h in ad["headlines"][1:]),
                  f"{p}: only the service-defining headline is pinned")
            check(all("pin" not in d for d in ad["descriptions"]), f"{p}: no description pins")
            blob = " | ".join(hs + ds).lower()
            for pat, label in BANNED:
                hit = re.search(pat, blob)
                check(hit is None, f"{p}: no {label}" + (f" -- FOUND '{hit.group(0)}'" if hit else ""))
check(ads_seen == 4, f"exactly 4 RSAs across the build (found {ads_seen})")

print("\n=== 6b. ASSET CHARACTER LIMITS ===")
for c in camp["campaigns"]:
    for g in c["ad_groups"]:
        a = g.get("assets") or {}
        for co in a.get("callouts") or []:
            check(len(co) <= 25, f"callout '{co}' is {len(co)}/25 chars")
        for ss in a.get("structured_snippets") or []:
            check(len(ss.get("values") or []) >= 3, f"snippet '{ss.get('header')}' has >= 3 values")
            for v in ss.get("values") or []:
                check(len(v) <= 25, f"snippet value '{v}' is {len(v)}/25 chars")

# ---------------------------------------------------------------- 7. negatives
print("\n=== 7. NEGATIVE KEYWORD SAFETY ===")
c0 = camp["campaigns"][0]
nb = [str(x) for x in c0["negatives_match_broad"]]
np_ = [str(x) for x in c0["negatives_match_phrase"]]
allneg = [(t, "BROAD") for t in nb] + [(t, "PHRASE") for t in np_]
print(f"  broad={len(nb)}  phrase={len(np_)}  total={len(allneg)}")
declared = camp["object_counts_if_executed"]["campaign_criterion.create_negative_keyword"]
check(declared == len(allneg), f"declared negative count {declared} == actual {len(allneg)}")
check(len({t.casefold() for t, _ in allneg}) == len(allneg), "no duplicate negative keywords")
for t, m in allneg:
    norm = t.strip().strip('"').strip("[]").strip().casefold()
    check(norm not in PROTECTED_NEGATIVES, f"negative '{t}' is not a protected buyer-intent term")


def toks(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def blocks(neg, match, query):
    nt, qt = toks(neg), toks(query)
    if not nt:
        return False
    if match == "EXACT":
        return nt == qt
    if match == "PHRASE":
        n = len(nt)
        return any(qt[i:i + n] == nt for i in range(len(qt) - n + 1))
    return all(t in qt for t in nt)


print("\n=== 8. REVERSE AUDIT: do OUR negatives block OUR positives? ===")
positives = []
for g in c0["ad_groups"]:
    for k in g["keywords"]:
        positives.append(k["text"])
probe = sorted(set(positives + [
    "permanent christmas lights lincoln ne", "permanent christmas lights cost",
    "permanent christmas lights price", "permanent christmas lights near me",
    "permanent christmas lights installer", "permanent christmas light installer",
    "best permanent christmas lights", "permanent christmas lights quote",
    "permanent christmas light installation cost",
    "permanent christmas lights company near me",
]))
conflicts = 0
for q_ in probe:
    hits = [f"{t} [{m}]" for t, m in allneg if blocks(t, m, q_)]
    if hits:
        conflicts += 1
        print(f"  [FAIL] '{q_}' would be blocked by {hits}")
        fails.append(f"negative blocks positive: {q_} <- {hits}")
check(conflicts == 0, f"no proposed negative blocks any proposed positive or protected query "
                      f"({len(probe)} probes)")

print("\n=== 9. NEGATIVE REACHABILITY (is each negative even reachable?) ===")
reachable, unreachable = [], []
for t, m in allneg:
    if any(blocks(t, "BROAD", p) or blocks(t, m, p) for p in positives):
        reachable.append(t)
    else:
        unreachable.append(t)
print(f"  negatives that could intersect a positive keyword's own text: {len(reachable)}")
print(f"  negatives that only guard QUERY space (normal and expected): {len(unreachable)}")
check(not reachable, f"no negative overlaps a positive keyword's literal text"
                     + (f" -- {reachable}" if reachable else ""))

print("\n=== 10. STRUCTURE / POLICY DEFAULTS ===")
check(c0["status"] == "PAUSED", "campaign created PAUSED")
check(c0["network_settings"]["target_search_network"] is False, "Search Partners OFF")
check(c0["network_settings"]["target_content_network"] is False, "Display OFF")
check(c0["network_settings"]["target_partner_search_network"] is False, "partner search OFF")
check(c0["ai_max"] is False, "AI Max OFF")
check(c0["keyword_match_expansion"] is False, "campaign broad match OFF")
check(c0["dynamic_search_ads"] is False, "DSA OFF")
check(c0["final_url_expansion"] == "OPTED_OUT", "Final URL expansion OFF")
check(c0["text_customization"] == "OPTED_OUT", "text customization OFF")
check(c0["automatically_created_assets"] == "OPTED_OUT", "automatically created assets OFF")
check(c0["location"]["option"] == "PRESENCE", "location option PRESENCE")
check(len(c0["location"]["geo_target_constant_ids"]) == 14, "all 14 geo targets present")
check(21162 not in c0["location"]["geo_target_constant_ids"], "state of Nebraska is NOT targeted")
check(c0["shared_negative_lists_attached"] == [], "no pre-existing shared negative list attached")
mt = {k["match_type"] for g in c0["ad_groups"] for k in g["keywords"]}
check(mt == {"PHRASE", "EXACT"}, f"match types are Phrase and Exact only (found {mt})")
check(len(c0["ad_groups"]) == 2, "2 ad groups")
check(all(len(g["keywords"]) == 2 for g in c0["ad_groups"]), "2 keywords per ad group")
check(all(len(g["ads"]) == 2 for g in c0["ad_groups"]), "2 RSAs per ad group")

print("\n=== 11. BUDGET MATH ===")
d = c0["daily_budget"]
monthly = round(d * 30.4, 2)
check(abs(d - 16.44) < 1e-9, f"daily budget is $16.44 (found ${d})")
check(monthly <= 500.00, f"daily x 30.4 = ${monthly} is at or under the $500 monthly limit")
print(f"    ${d} x 30.4 = ${monthly}   (x30 would be ${round(d*30,2)} -- 30.4 is the correct multiplier)")

print("\n=== 12. UNRESOLVED PLACEHOLDERS ===")
blob = CAMP.read_text(encoding="utf-8") + CONV.read_text(encoding="utf-8")
ph = sorted(set(re.findall(r"\[\[[A-Z_]+\]\]", blob)))
print(f"  placeholders still open: {ph}")
check(not ph, f"no unresolved placeholder remains" + (f" -- {ph}" if ph else ""))

print("\n=== 13. FINGERPRINTS ===")
fp_conv = approval_code(conv)
fp_camp = approval_code(camp)
print(f"  APG-0916-CONV-A : {fp_conv}")
print(f"  APG-0916-CAMP-B : {fp_camp}")

print("\n" + "=" * 78)
print(f"RED TEAM RESULT: {len(fails)} FAIL, {len(warns)} WARN")
for f in fails:
    print(f"  FAIL: {f}")
print("=" * 78)

out = {
    "fails": fails, "warns": warns,
    "fingerprints": {"APG-0916-CONV-A": fp_conv, "APG-0916-CAMP-B": fp_camp},
    "negative_counts": {"broad": len(nb), "phrase": len(np_), "total": len(allneg)},
    "monthly_budget_at_30_4": monthly,
    "open_placeholders": ph,
}
p = ROOT / "reports/apogee-lawns/evidence/2026-09-16-preflight.json"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(f"WROTE {p.relative_to(ROOT)}")
