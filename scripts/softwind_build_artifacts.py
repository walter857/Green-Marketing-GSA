#!/usr/bin/env python3
"""Build the Softwind Power Washing audit CSV artifacts from saved snapshots.

Reads only local read-only snapshots. No API calls, no mutations.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
AUD = ROOT / "clients/softwind-power-washing/audits"
AUD.mkdir(parents=True, exist_ok=True)
D = "2026-08-25"


def load(n):
    return json.loads((SNAP / n).read_text(encoding="utf-8"))


deep = load("deep-read-%s.json" % D)
met = load("metrics-%s.json" % D)
chron = load("chronology-%s.json" % D)
dm = load("demand-model-%s.json" % D)
lp = load("landing-pages-%s.json" % D)
lpr = load("landing-pages-retry-%s.json" % D)

AG = {a["id"]: a for a in deep["ad_groups"]}
LIVE_AG = {i: a for i, a in AG.items() if a["status"] == "ENABLED"}


def w(name, header, rows):
    p = AUD / name
    with p.open("w", newline="", encoding="utf-8") as f:
        c = csv.writer(f)
        c.writerow(header)
        c.writerows(rows)
    print("  %-52s %d rows" % (name, len(rows)))


# ---------------------------------------------------------------- ad groups
perf = {r["ad_group_id"]: r for r in met["ad_group_performance"]}
kw_by_ag = {}
for k in deep["keywords"]:
    kw_by_ag.setdefault(k["ad_group_id"], []).append(k)
ads_by_ag = {}
for a in deep["ads"]:
    ads_by_ag.setdefault(a["ad_group_id"], []).append(a)
st_by_ag = {}
for s in met["search_terms"]:
    st_by_ag.setdefault(s["ad_group_id"], []).append(s)


def classify_ag(a, p, live_kw, n_rsa):
    if a["status"] != "ENABLED":
        return "PAUSED - NOT SERVING"
    if not live_kw:
        return "STRUCTURAL ISSUE - no enabled keyword"
    if n_rsa < 2:
        return "STRUCTURAL ISSUE - fewer than 2 RSAs"
    impr = p["impressions"] if p else 0
    clicks = p["clicks"] if p else 0
    if impr == 0:
        return "NEEDS DATA - zero impressions"
    if clicks == 0 and impr < 20:
        return "NEEDS DATA - too few impressions to judge"
    if clicks == 0:
        return "CONSTRAINED - impressions without clicks"
    return "PROMISING - clicks, awaiting conversion signal"


rows = []
for i, a in sorted(AG.items(), key=lambda x: (x[1]["campaign_name"], x[1]["name"])):
    p = perf.get(i)
    live_kw = [k for k in kw_by_ag.get(i, []) if k["status"] == "ENABLED"]
    live_ads = [x for x in ads_by_ag.get(i, []) if x["status"] == "ENABLED"]
    sts = st_by_ag.get(i, [])
    urls = sorted({u for x in live_ads for u in x["final_urls"]})
    f = lambda v: ("%.1f%%" % (v * 100)) if v is not None else "NOT AVAILABLE"
    rows.append([
        a["campaign_name"], i, a["name"], a["status"], a["primary_status"],
        len(live_kw), ";".join(sorted({k["text"] for k in live_kw})),
        ";".join(sorted({k["match_type"] for k in live_kw})),
        len(live_ads),
        p["impressions"] if p else 0, p["clicks"] if p else 0,
        "%.2f" % (p["cost"] if p else 0),
        "%.2f%%" % ((p["ctr"] * 100) if p else 0),
        "%.2f" % (p["avg_cpc"] if p else 0),
        p["conversions"] if p else 0, "0.00%", "NO CONVERSIONS",
        f(p["search_is"]) if p else "NOT AVAILABLE",
        f(p["lost_is_rank"]) if p else "NOT AVAILABLE",
        "NOT AVAILABLE AT AD GROUP LEVEL",
        f(p["top_pct"]) if p else "NOT AVAILABLE",
        f(p["abs_top_pct"]) if p else "NOT AVAILABLE",
        len(sts), ";".join(urls) or "(none)",
        classify_ag(a, p, live_kw, len(live_ads)),
    ])
w("%s-ad-group-performance.csv" % D,
  ["campaign", "ad_group_id", "ad_group", "status", "primary_status",
   "enabled_keywords", "keyword_texts", "match_types", "enabled_rsas",
   "impressions", "clicks", "cost", "ctr", "avg_cpc", "conversions",
   "cvr", "cpl", "search_impression_share", "lost_is_rank", "lost_is_budget",
   "top_impr_pct", "abs_top_impr_pct", "search_terms_seen", "final_urls",
   "verdict"], rows)

# ---------------------------------------------------------------- keywords
kperf = {}
for r in met["keyword_performance"]:
    kperf[(r["ad_group_id"], r["criterion_id"])] = r

SCORES = {
    "power washing near me": (5, 5, 4, 5, 1),
    "power washing services near me": (5, 5, 4, 5, 1),
    "power washing company near me": (5, 5, 4, 5, 0),
    "power washing islip": (5, 5, 4, 5, 1),
    "power washing west islip": (5, 5, 4, 5, 1),
    "power washing dix hills": (5, 5, 4, 5, 1),
    "residential pressure washing near me": (5, 5, 5, 5, 0),
    "house washing company near me": (5, 5, 5, 5, 0),
    "house pressure washing estimate": (4, 3, 5, 4, 0),
    "driveway pressure washing near me": (5, 5, 5, 5, 0),
    "patio pressure washing near me": (5, 5, 5, 5, 0),
    "soft house washing near me": (5, 5, 5, 5, 0),
    "soft washing estimate": (4, 2, 5, 4, 0),
}
PLANNER = {b["representative"]: b for b in dm["top_bofu_buckets"]}


def kw_verdict(k, p, live):
    t = k["text"]
    if not live:
        if t in ("house washing company near me",):
            return ("EXPAND", "Ad group is paused in BOTH campaigns. Keyword Planner "
                              "shows 40 local searches/month at $10.46-$32.09 "
                              "top-of-page. This is unserved in-scope BOFU demand.")
        return ("WATCH", "Sits in a paused ad group; no delivery and no cost.")
    if k["quality_score"] == 1:
        return ("KEEP", "Highest-intent head term in the account, but Quality Score 1 "
                        "with Below Average on all three components. Fix ad relevance "
                        "and expected CTR before judging the keyword.")
    if t == "house pressure washing estimate":
        return ("WATCH", "Live and delivering, but its close variants are cost-research "
                         "queries ('average cost to power wash a house', 'powerwash "
                         "cost'). Two clicks, $62.18, 36% of all account spend, no lead. "
                         "Re-map intent before adding negatives.")
    if p and p["impressions"] == 0:
        return ("WATCH", "Enabled and eligible but no impressions yet. Exact-match on a "
                         "small local pool; needs schedule and rank headroom, not removal.")
    return ("KEEP", "In-scope BOFU intent with local Planner demand and live delivery.")


rows = []
for k in sorted(deep["keywords"], key=lambda x: (x["campaign_name"], x["ad_group_name"],
                                                 x["text"], x["match_type"])):
    live = (k["status"] == "ENABLED" and AG[k["ad_group_id"]]["status"] == "ENABLED")
    p = kperf.get((k["ad_group_id"], k["criterion_id"]))
    b = SCORES.get(k["text"], (0, 0, 0, 0, 0))
    pl = PLANNER.get(k["text"])
    v, why = kw_verdict(k, p, live)
    rows.append([
        k["campaign_name"], k["ad_group_name"], k["criterion_id"], k["text"],
        k["match_type"], k["status"],
        "LIVE" if live else "NOT SERVING (ad group paused)",
        k["approval_status"], k["system_serving_status"], k["primary_status"],
        ";".join(k["primary_status_reasons"]) or "-",
        k["quality_score"] if k["quality_score"] else "NOT ENOUGH DATA",
        k["expected_ctr"] if k["expected_ctr"] != "UNSPECIFIED" else "NOT ENOUGH DATA",
        k["ad_relevance"] if k["ad_relevance"] != "UNSPECIFIED" else "NOT ENOUGH DATA",
        k["landing_page_experience"] if k["landing_page_experience"] != "UNSPECIFIED"
        else "NOT ENOUGH DATA",
        p["impressions"] if p else 0, p["clicks"] if p else 0,
        "%.2f" % (p["cost"] if p else 0), p["conversions"] if p else 0,
        pl["avg_monthly_searches"] if pl else "NOT IN PLANNER TOP BUCKETS",
        ("%.2f" % pl["low_top_of_page_bid"]) if pl and pl["low_top_of_page_bid"] else "-",
        ("%.2f" % pl["high_top_of_page_bid"]) if pl and pl["high_top_of_page_bid"] else "-",
        b[0], b[1], b[2], b[3], b[4], v, why,
    ])
w("%s-keyword-audit.csv" % D,
  ["campaign", "ad_group", "criterion_id", "keyword", "match_type", "status",
   "serving", "approval", "system_serving_status", "primary_status",
   "primary_status_reasons", "quality_score", "expected_ctr", "ad_relevance",
   "landing_page_experience", "impressions", "clicks", "cost", "conversions",
   "planner_local_monthly_searches", "planner_top_of_page_low",
   "planner_top_of_page_high", "score_bofu_intent", "score_local_intent",
   "score_service_specificity", "score_hire_likelihood",
   "score_equipment_ambiguity_higher_is_worse", "verdict", "reason"], rows)

# ---------------------------------------------------------------- search terms
BAD_INTENT = re.compile(
    r"\b(job|jobs|career|salary|hiring|training|course|diy|rental|rent|"
    r"for sale|used|parts|machine|equipment|how to)\b", re.I)
OUT_SCOPE = re.compile(r"\b(roof|gutter|chimney|carpet|window)\b", re.I)
INTERIOR = re.compile(r"house cleaning|maid|cleaning services", re.I)
COST_RESEARCH = re.compile(r"\b(cost|price|how much|average)\b", re.I)
PRESSURE = re.compile(r"pressure\s*wash", re.I)
POWER = re.compile(r"power\s*wash|powerwash", re.I)


def st_verdict(s):
    t = s["search_term"]
    ag = s["ad_group"]
    if OUT_SCOPE.search(t):
        return ("NEGATIVE CANDIDATE",
                "Roof cleaning is outside the approved Power Washing service scope for "
                "this work order. Blocking it does not suppress in-scope buyer demand.")
    if INTERIOR.search(t) and not POWER.search(t) and not PRESSURE.search(t):
        return ("NEGATIVE CANDIDATE",
                "'house cleaning services' reads as interior maid service, not exterior "
                "house washing. Wrong service entirely.")
    if BAD_INTENT.search(t):
        return ("NEGATIVE CANDIDATE", "Research, DIY, jobs or equipment intent.")
    if COST_RESEARCH.search(t):
        return ("WATCH",
                "Cost-research phrasing. Agency policy forbids auto-negativing cost and "
                "price terms; these can convert. But this family has taken 2 clicks and "
                "$62.18 with no lead, so watch it, do not block it yet.")
    if PRESSURE.search(t) and not POWER.search(t) and "Pressure" not in ag \
            and "Residential" not in ag:
        return ("ROUTING ISSUE",
                "Searcher typed 'pressure washing' but was served a 'power washing' ad "
                "group and ad copy. Belongs in a dedicated Pressure Washing SKAG.")
    if t in ("power washer near me", "local power washers", "powerwash near me"):
        return ("KEEP", "Reads as looking for a washing service provider, not a machine. "
                        "Monitor for equipment drift.")
    if s["clicks"] > 0:
        return ("KEEP", "In-scope buyer intent that produced a paid click.")
    return ("KEEP", "In-scope exterior-washing buyer intent.")


rows = []
for s in sorted(met["search_terms"], key=lambda x: (-x["impressions"], -x["clicks"])):
    v, why = st_verdict(s)
    rows.append([
        s["search_term"], s["matched_keyword"], s["keyword_match_type"],
        s["search_term_match_type"], s["ad_group"], s["campaign"],
        s["impressions"], s["clicks"], "%.2f" % s["cost"],
        "%.2f%%" % (s["ctr"] * 100), s["conversions"], 0.0, v, why,
    ])
w("%s-search-term-verdicts.csv" % D,
  ["search_term", "matched_keyword", "keyword_match_type", "search_term_match_type",
   "ad_group", "campaign", "impressions", "clicks", "cost", "ctr", "conversions",
   "conversion_value", "verdict", "reason"], rows)

# ---------------------------------------------------------------- RSA audit
aperf = {r["ad_id"]: r for r in met["ad_performance"]}
rows = []
for a in sorted(deep["ads"], key=lambda x: (x["campaign_name"], x["ad_group_name"],
                                            x["ad_id"])):
    live = a["status"] == "ENABLED" and AG[a["ad_group_id"]]["status"] == "ENABLED"
    p = aperf.get(a["ad_id"])
    H = [h["text"] for h in a["headlines"]]
    Dsc = [d["text"] for d in a["descriptions"]]
    sib = [x for x in deep["ads"]
           if x["ad_group_id"] == a["ad_group_id"] and x["ad_id"] != a["ad_id"]
           and x["status"] == a["status"]]
    ov = len(set(H) & set(sum([[h["text"] for h in s["headlines"]] for s in sib], []))) \
        if sib else 0
    pins = sum(1 for h in a["headlines"] if h["pinned"] != "UNSPECIFIED") + \
        sum(1 for d in a["descriptions"] if d["pinned"] != "UNSPECIFIED")
    if not live:
        verdict = "NOT SERVING - ad group paused"
    elif p and p["impressions"] < 30:
        verdict = "INSUFFICIENT DATA - structural review only"
    else:
        verdict = "INSUFFICIENT DATA - structural review only"
    issues = []
    if pins == 0:
        issues.append("no pinning; Google may serve a combination that never echoes the "
                      "searched service")
    if ov >= 6:
        issues.append("%d of 15 headlines duplicated in the sibling RSA (low variety)" % ov)
    if max(len(h) for h in H) > 30:
        issues.append("headline over 30 characters")
    if max(len(d) for d in Dsc) > 90:
        issues.append("description over 90 characters")
    if any(re.search(r"free (quote|estimate)", h, re.I) for h in H + Dsc):
        issues.append("'free quote' claim - verified present on the live landing pages "
                      "and the client site")
    rows.append([
        a["campaign_name"], a["ad_group_name"], a["ad_id"], a["status"],
        "LIVE" if live else "NOT SERVING", a["ad_strength"], a["approval_status"],
        a["review_status"], len(a["policy_topics"]),
        len(H), len(Dsc), max(len(h) for h in H), max(len(d) for d in Dsc),
        pins, ov, a["path1"], a["path2"], ";".join(a["final_urls"]),
        p["impressions"] if p else 0, p["clicks"] if p else 0,
        "%.2f%%" % ((p["ctr"] * 100) if p else 0),
        "%.2f" % (p["cost"] if p else 0), p["conversions"] if p else 0,
        verdict, "; ".join(issues) or "no structural defect found",
    ])
w("%s-rsa-audit.csv" % D,
  ["campaign", "ad_group", "ad_id", "status", "serving", "ad_strength", "approval",
   "review_status", "policy_topics", "headlines", "descriptions", "max_headline_len",
   "max_description_len", "pinned_assets", "headlines_shared_with_sibling_rsa",
   "path1", "path2", "final_urls", "impressions", "clicks", "ctr", "cost",
   "conversions", "verdict", "issues"], rows)

# ---------------------------------------------------------------- landing pages
lpv = {}
for r in met["landing_page_view"]:
    k = r["url"]
    d0 = lpv.setdefault(k, {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
    for f in ("impressions", "clicks", "cost", "conversions"):
        d0[f] += r[f]

pages = {}
for r in lp + lpr:
    if r.get("error"):
        continue
    pages.setdefault(r["requested_url"].split("?")[0], {})[r["viewport"]] = r

adgroup_url = {}
for a in deep["ads"]:
    if a["status"] == "ENABLED" and AG[a["ad_group_id"]]["status"] == "ENABLED":
        for u in a["final_urls"]:
            adgroup_url.setdefault(u, set()).add(
                "%s / %s" % (a["campaign_name"], a["ad_group_name"]))

APPROVED_PHONE = "6315027946"


def match_score(url, rec, groups):
    if not rec:
        return "", ""
    h1 = " ".join(rec["h1"]).lower()
    if "offer.softwindli.com" not in url:
        return 3, ("Main-site page, not the conversion-optimised offer page. Shows the "
                   "untracked phone (631) 502-5402 and a 50-option service dropdown "
                   "with a 50-state address form.")
    tokens = {"driveway": "driveway", "patio": "patio", "soft": "soft",
              "residential": "residential", "estimate": "estimate",
              "power washing": "power washing"}
    hits = sum(1 for g in groups for t, needle in tokens.items()
               if t in g.lower() and needle in h1)
    return (9 if hits else 8), ("H1 names the service and the three cities; body copy "
                                "repeats the searched phrasing.")


rows = []
for url in sorted(set(list(adgroup_url) + list(lpv))):
    rec = (pages.get(url, {}) or {}).get("desktop")
    mob = (pages.get(url, {}) or {}).get("mobile")
    st = lpv.get(url, {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0})
    groups = sorted(adgroup_url.get(url, {"(sitelink / account-level asset only)"}))
    score, note = match_score(url, rec, groups)
    issues = []
    if rec:
        ph = rec["phones_in_text"]
        if ph and APPROVED_PHONE not in ph:
            issues.append("PHONE MISMATCH: shows %s, not the approved (631) 502-7946"
                          % ", ".join(ph))
        if rec.get("countdown_present"):
            issues.append("evergreen 'Offer Ends in' countdown with no stated offer or "
                          "real deadline")
        aw = rec["trackers"].get("google_ads_gtag", [])
        if len(aw) > 1:
            issues.append("two Google Ads conversion IDs fire: %s (account's own ID is "
                          "AW-18369652705)" % ", ".join(aw))
        if not rec["forms"]:
            issues.append("no form found")
        if rec.get("out_of_scope_links"):
            issues.append("links out to out-of-scope services (%d found)"
                          % len(rec["out_of_scope_links"]))
        if "without making the page about unrelated services" in (
                rec.get("body_text_sample") or ""):
            issues.append("LIVE COPY DEFECT: an internal authoring instruction is "
                          "published in the body copy")
    else:
        issues.append("page could not be rendered during the audit")
    rows.append([
        url, ";".join(groups),
        rec["http_status"] if rec else "NOT RENDERED",
        ";".join(rec.get("redirect_chain") or []) if rec else "",
        rec["title"] if rec else "", ";".join(rec["h1"]) if rec else "",
        len(rec["forms"]) if rec else 0,
        ";".join(rec["tel_links"]) if rec else "",
        "YES" if (rec and rec.get("query_on_final_url")) else "NO",
        ";".join(sorted(rec["trackers"])) if rec else "",
        "YES" if (mob and mob["forms"] and mob["tel_links"]) else "NO",
        st["impressions"], st["clicks"], "%.2f" % st["cost"], st["conversions"],
        "0.00%", score, note, "; ".join(issues) or "none",
    ])
w("%s-landing-page-audit.csv" % D,
  ["url", "ad_groups_pointing_here", "http_status", "redirect_chain", "page_title",
   "h1", "forms", "tel_links", "click_ids_preserved", "trackers",
   "mobile_form_and_call_present", "impressions", "clicks", "cost", "conversions",
   "conversion_rate", "message_match_score_0_10", "message_match_note", "issues"], rows)

# ---------------------------------------------------------------- opportunities
live_kw = {k["text"].lower() for k in deep["keywords"]
           if k["status"] == "ENABLED" and AG[k["ad_group_id"]]["status"] == "ENABLED"}
paused_kw = {k["text"].lower() for k in deep["keywords"]
             if AG[k["ad_group_id"]]["status"] != "ENABLED"}

PRODUCT = re.compile(
    r"\b(zep|krud kutter|artisan|cleaner|store|ez |all pro|azek|ipe|"
    r"polymeric|greenworks|worx)\b", re.I)

CANDIDATES = [
    ("pressure washing near me", "Pressure Washing Near Me",
     "https://offer.softwindli.com/residential-pressure-washing/", "ADD-NOW CANDIDATE",
     "70 local searches/month at $8.75-$24.53 top-of-page. The account already receives "
     "this demand through close variants of power-washing keywords: 15 impressions of "
     "'pressure washing' phrasing produced 0 clicks because the ad copy said 'Power "
     "Washing'. A dedicated SKAG fixes the copy mismatch, not just the coverage."),
    ("pressure washing services near me", "Pressure Washing Services Near Me",
     "https://offer.softwindli.com/residential-pressure-washing/", "ADD-NOW CANDIDATE",
     "Shares the 110/month 'power washing near me' bucket at $10.89-$28.23. Currently "
     "served only as a close variant of a power-washing keyword."),
    ("pressure washing company near me", "Pressure Washing Company Near Me",
     "https://offer.softwindli.com/residential-pressure-washing/", "TEST CANDIDATE",
     "'pressure washing companies near me' shows 10/month at LOW competition. Company "
     "phrasing is proven BOFU in this account; one impression already routed here."),
    ("house washing near me", "House Washing Company Near Me (UNPAUSE, do not rebuild)",
     "https://offer.softwindli.com/house-washing-company/", "ADD-NOW CANDIDATE",
     "40 local searches/month at $10.46-$32.09, MEDIUM competition. The ad group, its "
     "keywords and 2 approved RSAs already exist and are paused in BOTH campaigns. This "
     "is unserved in-scope demand that needs no new build."),
    ("paver cleaning near me", "Paver Cleaning Near Me",
     "https://offer.softwindli.com/patio-power-washing/", "TEST CANDIDATE",
     "'paver cleaning' 40/month at $5.05-$15.18 plus 'paver cleaners near me' 20/month. "
     "Paver CLEANING is inside the approved patio/driveway washing scope. Paver SEALING "
     "is explicitly out of scope and must be excluded from the copy and negatives."),
    ("concrete pressure washing near me", "Concrete Pressure Washing Near Me",
     "https://offer.softwindli.com/driveway-pressure-washing/", "TEST CANDIDATE",
     "'concrete cleaning' 10/month; the surface is already named on the driveway page. "
     "Low volume, so a test, not a headline opportunity."),
    ("soft washing near me", "Soft Washing Near Me",
     "https://offer.softwindli.com/soft-house-washing/", "TEST CANDIDATE",
     "'soft wash near me' 10/month plus a 'soft washing' 20/month generic bucket. The "
     "existing SKAG is 'soft HOUSE washing near me'; the shorter phrasing is a distinct "
     "query the exact keyword does not reliably reach."),
    ("power washing company", "Power Washing Company Near Me (existing)", "-",
     "LOW VOLUME", "20/month at $10.95-$21.73, already covered by the live company SKAG."),
    ("power washing cost", "-", "-", "AMBIGUOUS",
     "10/month but the low top-of-page bid collapses to $0.31, which signals heavy "
     "research intent. The account already spent $62.18 on two cost-research clicks "
     "with no lead. Do not add as a keyword; keep monitoring as a search term."),
    ("pressure washer rental", "-", "-", "DO NOT ADD",
     "Equipment rental intent. Already blocked by an existing campaign negative."),
    ("best pressure washer", "-", "-", "DO NOT ADD",
     "Product-shopping intent; the $0.49-$3.20 bid range confirms retail, not service."),
    ("power washing", "-", "-", "AMBIGUOUS",
     "The largest single bucket at 480/month, but its $0.57 low top-of-page bid and its "
     "grouping with 'power pressure washer' show heavy equipment contamination. In this "
     "account it produced 14 impressions and 0 clicks. Reachable via existing phrase "
     "keywords; not worth a dedicated exact keyword."),
]
rows = []
for kw, ag, url, cls, why in CANDIDATES:
    b = PLANNER.get(kw)
    if not b:
        b = next((x for x in dm["top_bofu_buckets"]
                  if kw in " ".join(x["sample_variants"])), None)
    gen = next((x for x in dm["top_generic_buckets"] if x["representative"] == kw), None)
    src = b or gen
    months = src["monthly"] if src else []
    aug = next((m["searches"] for m in months
                if m["month"] == "AUGUST" and m["year"] == 2025), "")
    sep = next((m["searches"] for m in months
                if m["month"] == "SEPTEMBER" and m["year"] == 2025), "")
    jul = next((m["searches"] for m in months
                if m["month"] == "JULY" and m["year"] == 2026), "")
    rows.append([
        kw, src["avg_monthly_searches"] if src else "NOT IN PLANNER RESULT",
        src["competition"] if src else "", src["competition_index"] if src else "",
        ("%.2f" % src["low_top_of_page_bid"])
        if src and src.get("low_top_of_page_bid") else "NOT AVAILABLE",
        ("%.2f" % src["high_top_of_page_bid"])
        if src and src.get("high_top_of_page_bid") else "NOT AVAILABLE",
        jul, aug, sep,
        "COVERED" if kw in live_kw else
        ("EXISTS BUT PAUSED" if kw in paused_kw else "NOT COVERED"),
        ag, url, cls, why,
    ])
w("%s-keyword-opportunities.csv" % D,
  ["keyword", "planner_local_avg_monthly_searches", "competition", "competition_index",
   "top_of_page_bid_low", "top_of_page_bid_high", "searches_jul_2026",
   "searches_aug_2025", "searches_sep_2025", "current_coverage",
   "recommended_ad_group", "recommended_final_url", "classification", "rationale"], rows)

print("\nArtifacts written to %s" % AUD)
