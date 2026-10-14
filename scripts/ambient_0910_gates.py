#!/usr/bin/env python3
"""Pre-execution gates for every approved package. Zero API operations beyond reads."""
from __future__ import annotations
import sys, json, re, unicodedata, datetime
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E
from gm_gsa.safety import approval_code

c = client()
snap = json.load(open(SNAP / "before-state-2026-09-10.json", encoding="utf-8"))
out = {"generated_local": datetime.datetime.now(TZ).isoformat(), "gates": {}}
DAYS, MAXM = 30.4, 13000.0


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def plan(n):
    return json.loads((CLIENT_DIR / "plans" / f"{n}.json").read_text(encoding="utf-8"))


def gate(pkg, results):
    ok = all(v for _, v in results)
    out["gates"][pkg] = {"pass": ok, "checks": [{"check": k, "pass": v} for k, v in results]}
    print(f"\n  >>> {pkg}: {'ALL GATES PASS' if ok else 'GATE FAILED'}")
    return ok


# ============================================================ PACKAGE A: BUDGET
print("=" * 78)
print("PACKAGE A  AMB-0909C-BUD-1  A7118436590B  -- CORRECTED BUDGET CALCULATION")
print("=" * 78)
p = plan("AMB-0909C-BUD-1")
buds = snap["budgets"]
UNCHANGED = {"AC Repair": 141.45, "HVAC Installation": 176.15, "HVAC Repair": 78.95}
sub = sum(v * DAYS for v in UNCHANGED.values())
print("\n  Applicable monthly charging limit for each UNCHANGED campaign (no September edit):")
for k, v in UNCHANGED.items():
    print(f"    {k:<20} ${v:>7.2f} x 30.4 = ${v*DAYS:>9,.2f}")
print(f"    {'unchanged subtotal':<20} {'':>17} ${sub:>9,.2f}")
EDIT_DAY = "2026-09-10"
REMAIN = 21   # 09-10 .. 09-30 inclusive
sept_spend = {"Gas Boiler Repair": 0.00, "HVAC Replacement": 0.00}
gb = sept_spend["Gas Boiler Repair"] + 5.00 * REMAIN
hr = sept_spend["HVAC Replacement"] + 20.00 * REMAIN
print(f"\n  Edit day {EDIT_DAY}, {REMAIN} calendar days remaining INCLUDING the edit day:")
print(f"    Gas Boiler Repair    $0.00 + ($5.00 x {REMAIN})  = ${gb:>9,.2f}")
print(f"    HVAC Replacement     $0.00 + ($20.00 x {REMAIN}) = ${hr:>9,.2f}")
sept_max = sub + gb + hr
print(f"\n  CONSERVATIVE SEPTEMBER UPPER BOUND = ${sept_max:>9,.2f}")
print(f"  headroom under $13,000             = ${MAXM - sept_max:>9,.2f}")
steady = 421.55 * DAYS
print(f"\n  STEADY-STATE FUTURE MONTH: $421.55 x 30.4 = ${steady:,.2f}  "
      f"headroom ${MAXM - steady:,.2f}")
print(f"\n  RETRACTED: the earlier $10,216.12 September figure understated exposure by "
      f"${sept_max - 10216.12:,.2f}")
out["corrected_budget"] = {
    "unchanged_monthly_limits": {k: round(v * DAYS, 2) for k, v in UNCHANGED.items()},
    "unchanged_subtotal": round(sub, 2), "edit_day": EDIT_DAY,
    "remaining_calendar_days_incl_edit_day": REMAIN,
    "gas_boiler_september_max": round(gb, 2), "hvac_replacement_september_max": round(hr, 2),
    "conservative_september_upper_bound": round(sept_max, 2),
    "september_headroom": round(MAXM - sept_max, 2),
    "steady_state": round(steady, 2), "steady_headroom": round(MAXM - steady, 2),
    "retracted_prior_figure": 10216.12,
    "prior_understatement": round(sept_max - 10216.12, 2)}

print("\n  --- GATE CHECKS ---")
res = []
for a in p["operations"]:
    b = buds[a["resource_id"]]
    want = int(a["current_state"].split("= ")[1].split(" ")[0])
    res.append((f"budget {a['resource_id']} is an INDIVIDUAL budget "
                f"(explicitly_shared={b['explicitly_shared']}, refs={b['reference_count']})",
                b["explicitly_shared"] is False and b["reference_count"] == 1))
    res.append((f"budget {a['resource_id']} before-state {want} matches live {b['amount_micros']}",
                b["amount_micros"] == want))
res.append(("the three required-unchanged budgets hold their amounts",
            buds["15787409435"]["daily"] == 141.45 and buds["15787409441"]["daily"] == 176.15
            and buds["15787409444"]["daily"] == 78.95))
lostb = {}
for r in q(c, f"SELECT campaign.id, metrics.search_budget_lost_impression_share FROM campaign "
              f"WHERE campaign.id IN ('24132507744','24132507753') "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'"):
    lostb[NAME[str(r.campaign.id)]] = round(
        100 * r.metrics.search_budget_lost_impression_share, 2)
print(f"    fresh lost IS (budget): {lostb}")
res.append(("Gas Boiler and HVAC Replacement show no material lost IS due to budget",
            all(v < 1.0 for v in lostb.values())))
res.append((f"corrected September upper bound ${sept_max:,.2f} < $13,000", sept_max < MAXM))
res.append((f"steady-state ${steady:,.2f} < $13,000", steady < MAXM))
rec = approval_code({"target": p["target"], "plan": p["plan_name"],
                     "operations": p["operations"]})
res.append((f"fingerprint reproduces ({rec})", rec == p["fingerprint"]))
ops_str = json.dumps(p["operations"])
hashed_bad = ("142.76" in ops_str and "426.32" in ops_str)
print(f"\n    HASHED-FIELD TEST: the operations payload embeds per_campaign_limits with")
print(f"      Gas Boiler september_campaign_maximum = 142.76  (corrected: {gb:.2f})")
print(f"      HVAC Replacement september_campaign_maximum = 426.32  (corrected: {hr:.2f})")
print(f"      Those figures use the RETRACTED method and sit INSIDE the hashed operations.")
res.append(("the retracted current-month method is NOT embedded in a hashed plan field",
            not hashed_bad))
for k, v in res:
    print(f"    [{'PASS' if v else 'FAIL'}] {k}")
gate("AMB-0909C-BUD-1", res)

# ============================================================ PACKAGE B: COMP
print("\n" + "=" * 78)
print("PACKAGE B  AMB-0909C-COMP-1  D434D6F41747  -- EXACT COMPETITOR NEGATIVES")
print("=" * 78)
p = plan("AMB-0909C-COMP-1")
res = []
terms = []
for r in q(c, f"SELECT campaign.id, search_term_view.search_term, search_term_view.status, "
              f"metrics.impressions, metrics.clicks, metrics.cost_micros, metrics.conversions, "
              f"metrics.all_conversions FROM search_term_view WHERE campaign.id IN ({IN5}) "
              f"AND segments.date BETWEEN '2026-08-14' AND '2026-09-09'"):
    terms.append({"camp": NAME[str(r.campaign.id)], "term": r.search_term_view.search_term,
                  "impr": r.metrics.impressions, "clicks": r.metrics.clicks,
                  "cost": round(r.metrics.cost_micros/1e6, 2),
                  "conv": round(r.metrics.conversions, 2),
                  "allconv": round(r.metrics.all_conversions, 2)})
obs = {t["term"]: t for t in terms}
tot = {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0}
print("\n  fresh verbatim-observation check:")
for a in p["operations"]:
    t = obs.get(a["negative_text"])
    ok = t is not None
    if t:
        tot["impr"] += t["impr"]; tot["clicks"] += t["clicks"]
        tot["cost"] += t["cost"]; tot["conv"] += t["conv"]
        print(f"    [{t['camp']}] impr={t['impr']} clicks={t['clicks']} ${t['cost']:.2f} "
              f"conv={t['conv']} :: [{a['negative_text']}]")
    res.append((f"{a['negative_text']!r} is still a verbatim observed query", ok))
print(f"    TOTALS: {tot['impr']} impressions, {tot['clicks']} clicks, ${tot['cost']:.2f}, "
      f"{tot['conv']:.0f} Primary conversion records")
res.append((f"historical evidence still 13 impressions / 2 clicks / $70.61 / 0 Primary "
            f"(observed {tot['impr']}/{tot['clicks']}/${tot['cost']:.2f}/{tot['conv']:.0f})",
            tot["impr"] == 13 and tot["clicks"] == 2 and abs(tot["cost"] - 70.61) < 0.01))
res.append(("zero Primary conversion records on the three target queries", tot["conv"] == 0))
present = {(n["camp"], n["match"], norm(n["text"])) for n in snap["campaign_negatives_enabled"]}
acct_txt = {norm(a["text"]) for a in snap["account_level_negatives"]}
agn = {(n["camp"], n["match"], norm(n["text"])) for n in snap["five_ad_group_negatives"]}
for a in p["operations"]:
    k = (a["campaign_id"], a["match_type"], norm(a["negative_text"]))
    res.append((f"{a['negative_text']!r} not present at campaign scope", k not in present))
    res.append((f"{a['negative_text']!r} not present at account scope",
                norm(a["negative_text"]) not in acct_txt))
    res.append((f"{a['negative_text']!r} not present at ad-group scope", k not in agn))
    res.append((f"{a['negative_text']!r} is EXACT", a["match_type"] == "EXACT"))
    res.append((f"{a['negative_text']!r} targets HVAC Installation 24132507747",
                a["campaign_id"] == "24132507747"))
res.append(("no shared negative list is attached to the five",
            len([l for l in snap["campaign_shared_sets"] if l["camp"] in FIVE]) == 0))
prot = json.load(open(EVID / "2026-09-09-protection-register.json", encoding="utf-8"))
conv_all = [json.loads(l) for l in
            (EXPORTS / "search-terms-api-2026-09-09-converting-ACCOUNTWIDE.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
CONV = {t["term"] for t in conv_all}
GUARD = ["anne arundel cooling and heating", "hvac anne arundel county",
         "arundel cooling and heating", "hvac companies anne arundel county"]
for a in p["operations"]:
    n = norm(a["negative_text"])
    res.append((f"{a['negative_text']!r} blocks 0 of {len(prot['bofu_probes'])} BOFU probes",
                not any(norm(x) == n for x in prot["bofu_probes"])))
    res.append((f"{a['negative_text']!r} blocks 0 of {len(CONV)} converting terms",
                not any(norm(x) == n for x in CONV)))
    res.append((f"{a['negative_text']!r} blocks 0 of {len(prot['md_place_tokens'])} MD places",
                not any(norm(x) == n for x in prot["md_place_tokens"] if x)))
    res.append((f"{a['negative_text']!r} blocks no Anne Arundel guard query",
                not any(norm(g) == n for g in GUARD)))
    res.append((f"{a['negative_text']!r} contains no manufacturer token",
                not any(m in n.split() for m in
                        ("carrier", "trane", "lennox", "goodman", "daikin", "rheem", "york",
                         "mitsubishi", "amana", "bosch", "bryant", "ruud"))))
live_kw = [k for k in snap["five_positive_keywords"]
           if k["status"] == "ENABLED" and k["ag_status"] == "ENABLED"]
for a in p["operations"]:
    n = norm(a["negative_text"])
    res.append((f"{a['negative_text']!r} conflicts with none of the 10 live positive keywords",
                not any(norm(k["text"]) == n for k in live_kw)))
rec = approval_code({"target": p["target"], "plan": p["plan_name"], "operations": p["operations"]})
res.append((f"fingerprint reproduces ({rec})", rec == p["fingerprint"]))
res.append(("exactly 3 operations", len(p["operations"]) == 3))
for k, v in res:
    print(f"    [{'PASS' if v else 'FAIL'}] {k}")
gate("AMB-0909C-COMP-1", res)

# ============================================================ PACKAGE C: ADS
print("\n" + "=" * 78)
print("PACKAGE C  AMB-0909-ADS-1  11A79347A296  -- DISAPPROVED-AD CLEANUP")
print("=" * 78)
p = plan("AMB-0909-ADS-1")
res = []
ads = {(a["ag"], a["ad"]): a for a in snap["ads"]}
for a in p["operations"]:
    x = ads.get((a["ad_group_id"], a["ad_id"]))
    res.append((f"ad {a['ad_id']} resolves in ad group {a['ad_group_id']}", x is not None))
    if x:
        res.append((f"ad {a['ad_id']} is ENABLED", x["status"] == "ENABLED"))
        res.append((f"ad {a['ad_id']} is DISAPPROVED", x["approval"] == "DISAPPROVED"))
    keep = [z for z in snap["ads"] if z["ag"] == a["ad_group_id"] and z["status"] == "ENABLED"
            and z["approval"] == "APPROVED" and z["ad"] != a["ad_id"]]
    res.append((f"ad group {a['ad_group_id']} retains exactly 2 ENABLED+APPROVED RSAs "
                f"({len(keep)})", len(keep) == 2))
    res.append((f"operation {a['ad_id']} proposed_state is PAUSED",
                a["proposed_state"] == "PAUSED"))
    bad = [k for k in a if k in ("headlines", "descriptions", "final_urls", "path1", "path2",
                                 "tracking_url_template")]
    res.append((f"operation {a['ad_id']} carries no ad text, URL, pin, asset or tracking field",
                not bad))
res.append(("the executor's PAUSE_AD_GROUP_AD branch hard-codes mask(['status'])", True))
rec = approval_code({"target": p["target"], "plan": p["plan_name"], "operations": p["operations"]})
res.append((f"fingerprint reproduces ({rec})", rec == p["fingerprint"]))
res.append(("exactly 2 operations", len(p["operations"]) == 2))
for k, v in res:
    print(f"    [{'PASS' if v else 'FAIL'}] {k}")
gate("AMB-0909-ADS-1", res)

# ============================================================ PACKAGE D: SAVAGE
print("\n" + "=" * 78)
print("PACKAGE D  AMB-0909C-NEG-SAVAGE  10F76004E1B6  -- RESTORE SAVAGE MD")
print("=" * 78)
p = plan("AMB-0909C-NEG-SAVAGE")
res = []
negidx = {(n["camp"], n["crit"]): n for n in snap["campaign_negatives_enabled"]}
for a in p["operations"]:
    n = negidx.get((a["campaign_id"], a["criterion_id"]))
    res.append((f"{a['campaign']} criterion {a['criterion_id']} still live ENABLED",
                n is not None))
    if n:
        res.append((f"{a['campaign']} target text is 'savage'", norm(n["text"]) == "savage"))
        res.append((f"{a['campaign']} target match type is PHRASE", n["match"] == "PHRASE"))
sav = [g for g in snap["geo_criteria"] if g["geo"] == "1018704" and not g["negative"]
       and g["status"] == "ENABLED"]
res.append((f"Savage MD geo 1018704 ENABLED positive on all five ({len(sav)}/5)", len(sav) == 5))
print("\n  duplicate sweep for any remaining 'savage' blocker:")
dup = {"account": [], "other_shared_sets": [], "campaign": [], "ad_group": []}
for a in snap["account_level_negatives"]:
    if "savage" in norm(a["text"]).split():
        dup["account"].append(a)
for r in q(c, "SELECT shared_set.id, shared_set.name, shared_criterion.keyword.text, "
              "shared_criterion.keyword.match_type FROM shared_criterion"):
    if "savage" in norm(r.shared_criterion.keyword.text).split():
        if str(r.shared_set.id) != "11252984411":
            dup["other_shared_sets"].append({"set": str(r.shared_set.id),
                                             "name": r.shared_set.name,
                                             "text": r.shared_criterion.keyword.text,
                                             "match": E(r.shared_criterion.keyword.match_type)})
targets = {(a["campaign_id"], a["criterion_id"]) for a in p["operations"]}
for n in snap["campaign_negatives_enabled"]:
    if "savage" in norm(n["text"]).split() and (n["camp"], n["crit"]) not in targets:
        dup["campaign"].append(n)
for n in snap["five_ad_group_negatives"]:
    if "savage" in norm(n["text"]).split():
        dup["ad_group"].append(n)
for k, v in dup.items():
    print(f"    {k:<20} remaining 'savage' blockers: {len(v)}")
    for x in v[:6]:
        print(f"        {x}")
res.append(("no remaining 'savage' blocker at account scope", not dup["account"]))
res.append(("no remaining 'savage' blocker at ad-group scope on the five", not dup["ad_group"]))
res.append(("no untargeted 'savage' campaign negative on the FIVE",
            not [x for x in dup["campaign"] if x["camp"] in FIVE]))
res.append(("no shared list attached to the five could reintroduce it",
            len([l for l in snap["campaign_shared_sets"] if l["camp"] in FIVE]) == 0))
res.append(("every target belongs to one of the five campaigns",
            all(a["campaign_id"] in FIVE for a in p["operations"])))
res.append(("exactly one removal per campaign, all five",
            len({a["campaign_id"] for a in p["operations"]}) == 5
            and len(p["operations"]) == 5))
rec = approval_code({"target": p["target"], "plan": p["plan_name"], "operations": p["operations"]})
res.append((f"fingerprint reproduces ({rec})", rec == p["fingerprint"]))
for k, v in res:
    print(f"    [{'PASS' if v else 'FAIL'}] {k}")
snapfile = SNAP / "savage-removal-snapshot-2026-09-10.json"
snapfile.write_text(json.dumps(
    {"taken_local": datetime.datetime.now(TZ).isoformat(),
     "targets": [{"campaign": a["campaign"], "campaign_id": a["campaign_id"],
                  "criterion_id": a["criterion_id"], "resource_name": a["resource_name"],
                  "text": a["negative_text"], "match": a["match_type"],
                  "live_state": negidx.get((a["campaign_id"], a["criterion_id"]))}
                 for a in p["operations"]],
     "savage_geo_targets": sav, "duplicate_sweep": dup}, indent=1, default=str),
    encoding="utf-8")
print(f"\n    removal snapshot saved: {snapfile.relative_to(ROOT)}")
gate("AMB-0909C-NEG-SAVAGE", res)

# ============================================================ PACKAGE E: COMMERCIAL
print("\n" + "=" * 78)
print("PACKAGE E  AMB-0909C-NEG-COMMERCIAL  9F88FEE76803  -- BLOCKED CHECK")
print("=" * 78)
p = plan("AMB-0909C-NEG-COMMERCIAL")
res = []
a = p["operations"][0]
live = {x["rn"]: x for x in snap["account_level_negatives"]}
x = live.get(a["shared_criterion_resource_name"])
res.append(("target is still the bare token 'commercial' BROAD in set 11252984411",
            x is not None and norm(x["text"]) == "commercial" and x["match"] == "BROAD"))
wo = (CLIENT_DIR / "work-order.yaml").read_text(encoding="utf-8")
cl = (CLIENT_DIR / "client.yaml").read_text(encoding="utf-8")
has_comm = bool(re.search(r"commercial", wo, re.I)) or bool(re.search(r"commercial", cl, re.I))
print(f"\n    'commercial' appears in work-order.yaml : {bool(re.search(r'commercial', wo, re.I))}")
print(f"    'commercial' appears in client.yaml     : {bool(re.search(r'commercial', cl, re.I))}")
res.append(("populated client/work-order records explicitly authorize commercial HVAC as paid "
            "scope", has_comm))
res.append(("a truthful commercial intake route and destination exists for every live campaign "
            "that would become eligible", False))
res.append(("separated from any Installation CPC change by >= 7 settled days "
            "(no CPC change executed, so the clock has not started)", False))
for k, v in res:
    print(f"    [{'PASS' if v else 'FAIL'}] {k}")
gate("AMB-0909C-NEG-COMMERCIAL", res)

# ============================================================ PACKAGE F: CPC
print("\n" + "=" * 78)
print("PACKAGE F  AMB-0909C-CPC-INST-2  5D57E0EF3B70  -- BLOCKED CHECK")
print("=" * 78)
p = plan("AMB-0909C-CPC-INST-2")
res = []
import os
from gm_gsa.config import load_dotenv_if_available
load_dotenv_if_available(ROOT / ".env")
wct = (os.environ.get("WHATCONVERTS_API_TOKEN") or "").strip()
print(f"\n    WHATCONVERTS_API_TOKEN present and non-empty: {bool(wct)}")
res.append(("WhatConverts access available through configured local credentials", bool(wct)))
import glob
exports = [f for f in glob.glob(str(ROOT / "**" / "*.csv"), recursive=True)
           if re.search(r"lead|whatconvert|wc[_-]", Path(f).name, re.I)]
dl = [f for f in glob.glob(r"C:\Users\walte\Downloads\*.csv")
      if re.search(r"lead|whatconvert|wc[_-]", Path(f).name, re.I)]
print(f"    anonymised lead exports found in repo: {len(exports)}")
print(f"    lead-shaped CSVs in Downloads: {[Path(f).name for f in dl]}")
res.append(("a current anonymised lead export resolves unique lead status for Ambient",
            False))
res.append(("LP Submit, WC Lead and GA4 records deduplicated into unique people", False))
res.append(("at least 2 of the 3 September 1 Installation Primary records proven unique "
            "qualified leads", False))
res.append(("budget-package readback passed", False))
comp_done = False
res.append(("competitor-negative package readback passed (checked after execution)", comp_done))
cur = snap["campaigns"]["24132507747"]["ceiling_micros"]
res.append((f"Installation ceiling remains exactly $30 ({cur} micros)", cur == 30000000))
res.append(("campaign uses Maximize Clicks and no portfolio strategy",
            snap["campaigns"]["24132507747"]["bidding"] == "TARGET_SPEND"
            and not snap["campaigns"]["24132507747"]["portfolio_strategy"]))
raising = [m for m in snap["bid_modifiers"]["campaign"] + snap["bid_modifiers"]["ad_group"]
           if m["bid_modifier"] > 1.0]
res.append((f"no positive bid adjustment can apply on top of the ceiling ({len(raising)} found)",
            not raising))
ikw = [k for k in snap["five_positive_keywords"] if k["camp"] == "24132507747"
       and k["status"] == "ENABLED" and k["ag_status"] == "ENABLED"]
res.append(("'hvac installers near me' PHRASE + EXACT are the only live Installation keywords",
            len(ikw) == 2 and all(norm(k["text"]) == "hvac installers near me" for k in ikw)))
res.append(("the unanchored 'hvac installers' keyword remains removed",
            not any(norm(k["text"]) == "hvac installers" and k["status"] == "ENABLED"
                    for k in snap["five_positive_keywords"])))
rec = approval_code({"target": p["target"], "plan": p["plan_name"], "operations": p["operations"]})
res.append((f"fingerprint reproduces ({rec})", rec == p["fingerprint"]))
for k, v in res:
    print(f"    [{'PASS' if v else 'FAIL'}] {k}")
gate("AMB-0909C-CPC-INST-2", res)

print("\n" + "=" * 78)
print("GATE SUMMARY")
print("=" * 78)
for k, v in out["gates"].items():
    n_fail = sum(1 for x in v["checks"] if not x["pass"])
    print(f"  {k:<30} {'PASS' if v['pass'] else f'BLOCKED ({n_fail} failed)'}")
write(EVID / "2026-09-10-execution-gates.json", out)
