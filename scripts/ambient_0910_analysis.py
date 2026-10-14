#!/usr/bin/env python3
"""Post-execution independent analysis: search terms, CTR/RSA/QS, CPC/bidding, invalid traffic."""
from __future__ import annotations
import sys, json, re, unicodedata, datetime, csv
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambient_0909_lib import *  # noqa
from gm_gsa.google_ads import enum_name as E

c = client()
out = {"generated_local": datetime.datetime.now(TZ).isoformat()}
SETTLED = "2026-09-09"
prot = json.load(open(EVID / "2026-09-09-protection-register.json", encoding="utf-8"))
conv_all = [json.loads(l) for l in
            (EXPORTS / "search-terms-api-2026-09-09-converting-ACCOUNTWIDE.jsonl")
            .read_text(encoding="utf-8").splitlines() if l.strip()]
CONV = {t["term"].lower().strip() for t in conv_all}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").lower()
    s = re.sub(r"[^a-z0-9\s&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# =========================================================== 1. SEARCH TERMS
print("=== 1. SEARCH-TERM AUDIT, MULTIPLE SETTLED WINDOWS ===")
WINS = {"since_last_audit_2026-09-09": ("2026-09-09", SETTLED),
        "last_7_settled": ("2026-09-03", SETTLED),
        "last_14_settled": ("2026-08-27", SETTLED),
        "last_30_settled": ("2026-08-11", SETTLED),
        "all_time": ("2026-08-14", SETTLED)}
rows = {}
for lbl, (s, e) in WINS.items():
    r = []
    for x in q(c, f"SELECT campaign.id, ad_group.id, search_term_view.search_term, "
                  f"search_term_view.status, segments.search_term_match_type, "
                  f"metrics.impressions, metrics.clicks, metrics.cost_micros, "
                  f"metrics.conversions, metrics.all_conversions FROM search_term_view "
                  f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '{s}' AND '{e}'"):
        r.append({"camp": str(x.campaign.id), "ag": str(x.ad_group.id),
                  "term": x.search_term_view.search_term,
                  "st_status": E(x.search_term_view.status),
                  "match": E(x.segments.search_term_match_type),
                  "impr": x.metrics.impressions, "clicks": x.metrics.clicks,
                  "cost": round(x.metrics.cost_micros / 1e6, 2),
                  "conv": round(x.metrics.conversions, 2),
                  "allconv": round(x.metrics.all_conversions, 2)})
    rows[lbl] = r
    print(f"  {lbl:<32} rows={len(r):<5} clicks={sum(z['clicks'] for z in r):<4} "
          f"cost=${sum(z['cost'] for z in r):<9.2f} conv={sum(z['conv'] for z in r):.0f}")

live_neg = defaultdict(lambda: {"BROAD": set(), "PHRASE": set(), "EXACT": set()})
for x in q(c, f"SELECT campaign.id, campaign_criterion.keyword.text, "
              f"campaign_criterion.keyword.match_type FROM campaign_criterion "
              f"WHERE campaign.id IN ({IN5}) AND campaign_criterion.type = 'KEYWORD' "
              f"AND campaign_criterion.negative = TRUE AND campaign_criterion.status = 'ENABLED'"):
    live_neg[str(x.campaign.id)][E(x.campaign_criterion.keyword.match_type)].add(
        norm(x.campaign_criterion.keyword.text))
acct_neg = {"BROAD": set(), "PHRASE": set(), "EXACT": set()}
for x in q(c, "SELECT shared_criterion.keyword.text, shared_criterion.keyword.match_type "
              "FROM shared_criterion WHERE shared_set.id = 11252984411"):
    m = E(x.shared_criterion.keyword.match_type)
    if m in acct_neg:
        acct_neg[m].add(norm(x.shared_criterion.keyword.text))
agneg = defaultdict(lambda: {"BROAD": set(), "PHRASE": set(), "EXACT": set()})
for x in q(c, f"SELECT ad_group.id, ad_group_criterion.keyword.text, "
              f"ad_group_criterion.keyword.match_type FROM ad_group_criterion "
              f"WHERE campaign.id IN ({IN5}) AND ad_group_criterion.type = 'KEYWORD' "
              f"AND ad_group_criterion.negative = TRUE AND ad_group_criterion.status = 'ENABLED'"):
    agneg[str(x.ad_group.id)][E(x.ad_group_criterion.keyword.match_type)].add(
        norm(x.ad_group_criterion.keyword.text))


def covered(term, camp, ag):
    tw = norm(term).split()
    tws, joined = set(tw), " " + " ".join(tw) + " "
    for b in (live_neg[camp], agneg[ag], acct_neg):
        for n in b["BROAD"]:
            if n.split() and set(n.split()) <= tws:
                return ("BROAD", n)
        for n in b["PHRASE"]:
            if (" " + n + " ") in joined:
                return ("PHRASE", n)
        if " ".join(tw) in b["EXACT"]:
            return ("EXACT", " ".join(tw))
    return None


SERVICES = (r"ac|a c|air ?con(?:d|ditioner|ditioning)?|hvac|heat(?:ing|er|pump)?|furnace|boiler|"
            r"duct(?:work|s)?|mini ?split|ductless|geothermal|thermostat|humidifier|dehumidifier|"
            r"tankless|water ?heater|condenser|compressor|coil|cooling|central air|air handler")
INTENT = (r"repair|fix|service|maintenance|tune ?up|install(?:er|ers|ation)?|replace|replacement|"
          r"company|companies|contractor|technician|specialist|estimate|quote|price|pricing|cost|"
          r"near me|nearby|local|open now|same day|emergency|best|top|affordable|cheap|"
          r"residential|commercial|free|hire|call|book|schedule|appointment|not working|broken|"
          r"leak|no heat|no air|blowing")
JOB = re.compile(r"\b(job|jobs|career|hiring|salary|apprentice|resume|employment|vacanc)\b", re.I)
LEARN = re.compile(r"\b(school|class|course|training|certification|degree|tutorial|how to|diy|"
                   r"youtube|pdf|manual|wiring diagram|epa 608)\b", re.I)
SUPPLY = re.compile(r"\b(supply house|wholesale|distributor|parts store|buy parts|amazon|ebay|"
                    r"home depot|lowes|for sale|catalog|rental)\b", re.I)
VEHICLE = re.compile(r"\b(car|cars|auto|automotive|truck|van|rv|boat|marine|vehicle)\b", re.I)
OTHER = re.compile(r"\b(plumber|plumbing|electrician|roofing|appliance repair|washer|dryer|"
                   r"refrigerator|garage door|siding|gutter|septic|chimney|pest control|"
                   r"landscap|lawn care|pressure wash|carpet clean|mold remediation)\b", re.I)
RESEARCH = re.compile(r"\b(reviews?|complaints|bbb|yelp|reddit|glassdoor|indeed|sq ft|"
                      r"square feet|how much)\b", re.I)
RE_SVC = re.compile(rf"\b({SERVICES})\b", re.I)
RE_INT = re.compile(rf"({INTENT})", re.I)

audit = rows["all_time"]
verdicts = []
for r in audit:
    t = norm(r["term"])
    cov = covered(r["term"], r["camp"], r["ag"])
    sig = []
    for nm, rx in (("JOB", JOB), ("EDU_DIY", LEARN), ("PARTS_SUPPLY", SUPPLY),
                   ("VEHICLE", VEHICLE), ("OTHER_TRADE", OTHER), ("RESEARCH", RESEARCH)):
        if rx.search(t):
            sig.append(nm)
    conv_protected = t in CONV or r["conv"] > 0
    bofu = bool(RE_SVC.search(t) and RE_INT.search(t))
    if cov:
        v, why = "ALREADY_COVERED", f"live {cov[0]} negative {cov[1]!r}"
    elif conv_protected:
        v, why = "KEEP_BOFU", "observed converting term - never negatived without verified " \
                              "unique lead-quality evidence"
    elif bofu and not sig:
        v, why = "KEEP_BOFU", "service + intent"
    elif bofu and sig:
        v, why = "HOLD", f"service intent AND {'/'.join(sig)}"
    elif sig:
        v, why = "NEGATIVE_EXACT", "/".join(sig)
    elif r["clicks"] == 0 and r["impr"] <= 2:
        v, why = "KEEP_TEST", "negligible exposure, no whitelist hit"
    else:
        v, why = "HOLD", "no whitelist hit and no clear irrelevance signal"
    verdicts.append({**r, "verdict": v, "reason": why,
                     "covered_by": f"{cov[0]}:{cov[1]}" if cov else ""})

print(f"\n  VERDICT COUNTS (all-time visible corpus, {len(verdicts)} rows):")
for k, n in Counter(v["verdict"] for v in verdicts).most_common():
    sub = [v for v in verdicts if v["verdict"] == k]
    print(f"    {k:<20} rows={n:<5} clicks={sum(z['clicks'] for z in sub):<4} "
          f"cost=${sum(z['cost'] for z in sub):<9.2f} conv={sum(z['conv'] for z in sub):.0f}")
print("\n  by campaign x verdict:")
for cid in FIVE:
    sub = [v for v in verdicts if v["camp"] == cid]
    if sub:
        print(f"    {NAME[cid]:<20} {dict(Counter(v['verdict'] for v in sub))}")
res = [v for v in verdicts if v["verdict"] in ("NEGATIVE_EXACT", "HOLD")]
print(f"\n  RESIDUE (NEGATIVE_EXACT + HOLD): {len(res)} rows, "
      f"{sum(z['clicks'] for z in res)} clicks, ${sum(z['cost'] for z in res):.2f}")
for r in sorted(res, key=lambda z: -z["cost"])[:25]:
    print(f"    {r['verdict']:<16} {NAME[r['camp']]:<18} impr={r['impr']:<4} clk={r['clicks']:<3} "
          f"${r['cost']:<8} :: {r['term']!r}  [{r['reason']}]")
newwin = [v for v in verdicts if v["camp"] and v["term"] in
          {z["term"] for z in rows["since_last_audit_2026-09-09"]}]
print(f"\n  terms observed in the newest settled day (2026-09-09): {len(newwin)}")
out["search_terms"] = {"windows": {k: len(v) for k, v in rows.items()},
                       "verdict_counts": dict(Counter(v["verdict"] for v in verdicts)),
                       "residue": res}
p = EXPORTS / "search-term-verdicts-2026-09-10.csv"
with p.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(verdicts[0].keys()))
    w.writeheader()
    w.writerows(verdicts)
print(f"  WROTE {p.relative_to(ROOT)}")

# =========================================================== 2. CTR / RSA / QS
print("\n\n=== 2. CTR, RSA, ASSET AND QUALITY-SCORE AUDIT ===")
camp = {}
for r in q(c, f"SELECT campaign.id, metrics.impressions, metrics.clicks, metrics.ctr, "
              f"metrics.average_cpc, metrics.cost_micros, metrics.conversions, "
              f"metrics.search_impression_share, metrics.search_top_impression_share, "
              f"metrics.search_absolute_top_impression_share, "
              f"metrics.search_budget_lost_impression_share, "
              f"metrics.search_rank_lost_impression_share FROM campaign "
              f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' "
              f"AND '{SETTLED}'"):
    x = r.metrics
    camp[NAME[str(r.campaign.id)]] = {
        "impressions": x.impressions, "clicks": x.clicks, "ctr": round(x.ctr * 100, 2),
        "cpc": round(x.average_cpc / 1e6, 2), "cost": round(x.cost_micros / 1e6, 2),
        "primary_records": round(x.conversions, 2),
        "raw_cpa": round((x.cost_micros / 1e6) / x.conversions, 2) if x.conversions else None,
        "is": round(x.search_impression_share * 100, 2),
        "top_is": round(x.search_top_impression_share * 100, 2),
        "abs_top_is": round(x.search_absolute_top_impression_share * 100, 2),
        "lost_budget": round(x.search_budget_lost_impression_share * 100, 2),
        "lost_rank": round(x.search_rank_lost_impression_share * 100, 2)}
out["campaign_performance"] = camp
print(f"  {'campaign':<20}{'impr':>7}{'clk':>5}{'CTR':>7}{'CPC':>9}{'cost':>10}"
      f"{'rec':>5}{'rawCPA':>9}{'IS':>7}{'lostBUD':>9}{'lostRANK':>9}")
for k, v in camp.items():
    cpa_s = f"{v['raw_cpa']:.2f}" if v['raw_cpa'] else "-"
    print(f"  {k:<20}{v['impressions']:>7}{v['clicks']:>5}{v['ctr']:>6.2f}%{v['cpc']:>9.2f}"
          f"{v['cost']:>10.2f}{v['primary_records']:>5.0f}{cpa_s:>9}"
          f"{v['is']:>6.1f}%{v['lost_budget']:>8.1f}%{v['lost_rank']:>8.1f}%")

qs = []
seen = set()
for r in q(c, f"SELECT campaign.id, ad_group_criterion.keyword.text, "
              f"ad_group_criterion.keyword.match_type, "
              f"ad_group_criterion.quality_info.quality_score, "
              f"ad_group_criterion.quality_info.creative_quality_score, "
              f"ad_group_criterion.quality_info.post_click_quality_score, "
              f"ad_group_criterion.quality_info.search_predicted_ctr FROM keyword_view "
              f"WHERE campaign.id IN ({IN5}) AND ad_group_criterion.status = 'ENABLED' "
              f"AND segments.date BETWEEN '2026-08-14' AND '{SETTLED}'"):
    x = r.ad_group_criterion
    k = (str(r.campaign.id), x.keyword.text, E(x.keyword.match_type))
    if k in seen:
        continue
    seen.add(k)
    qs.append({"camp": NAME[k[0]], "text": k[1], "match": k[2],
               "qs": x.quality_info.quality_score or None,
               "exp_ctr": E(x.quality_info.search_predicted_ctr),
               "ad_relevance": E(x.quality_info.creative_quality_score),
               "lp_experience": E(x.quality_info.post_click_quality_score)})
out["quality_score"] = qs
print(f"\n  Quality Score components (DIAGNOSTIC, not an auction input and not a KPI):")
for x in sorted(qs, key=lambda z: (z["camp"], z["match"])):
    if x["qs"]:
        print(f"    {x['camp']:<20} {x['match']:<7} QS={x['qs']}  expCTR={x['exp_ctr']:<14} "
              f"adRel={x['ad_relevance']:<14} lpExp={x['lp_experience']:<14} [{x['text']}]")

print(f"\n  --- AC REPAIR AD COMPARISON: 820900825416 vs 820900825419 ---")
adperf = {}
for r in q(c, f"SELECT ad_group_ad.ad.id, segments.device, metrics.impressions, metrics.clicks, "
              f"metrics.ctr, metrics.cost_micros, metrics.conversions, "
              f"metrics.absolute_top_impression_percentage, metrics.top_impression_percentage "
              f"FROM ad_group_ad WHERE campaign.id = 24132507741 "
              f"AND segments.date BETWEEN '2026-08-14' AND '{SETTLED}'"):
    aid = str(r.ad_group_ad.ad.id)
    d = E(r.segments.device)
    adperf.setdefault(aid, {}).setdefault(d, {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0,
                                              "abs_top": 0.0, "top": 0.0})
    z = adperf[aid][d]
    z["impr"] += r.metrics.impressions; z["clicks"] += r.metrics.clicks
    z["cost"] += r.metrics.cost_micros / 1e6; z["conv"] += r.metrics.conversions
    z["abs_top"] = round(r.metrics.absolute_top_impression_percentage * 100, 2)
    z["top"] = round(r.metrics.top_impression_percentage * 100, 2)
out["ac_repair_ad_comparison"] = adperf
for aid, dv in sorted(adperf.items()):
    tot_i = sum(z["impr"] for z in dv.values()); tot_c = sum(z["clicks"] for z in dv.values())
    print(f"    ad {aid}: total impr={tot_i} clicks={tot_c} "
          f"CTR={100*tot_c/tot_i if tot_i else 0:.2f}% "
          f"cost=${sum(z['cost'] for z in dv.values()):.2f} "
          f"records={sum(z['conv'] for z in dv.values()):.0f}")
    for d, z in sorted(dv.items()):
        print(f"        {d:<9} impr={z['impr']:<5} clk={z['clicks']:<3} "
              f"CTR={100*z['clicks']/z['impr'] if z['impr'] else 0:>5.2f}%  "
              f"topPct={z['top']:>5.1f}%  absTopPct={z['abs_top']:>5.1f}%")

# =========================================================== 3. INVALID TRAFFIC
print("\n\n=== 3. INVALID-TRAFFIC REFRESH (settled through 2026-09-09) ===")
inv = {}
for lbl, sel, keyf in (("campaign", "", lambda r: NAME[str(r.campaign.id)]),
                       ("device", "segments.device", lambda r: E(r.segments.device)),
                       ("click_type", "segments.click_type", lambda r: E(r.segments.click_type))):
    agg = defaultdict(lambda: {"clicks": 0, "invalid": 0, "cost": 0.0})
    for r in q(c, f"SELECT campaign.id{', ' + sel if sel else ''}, metrics.clicks, "
                  f"metrics.invalid_clicks, metrics.cost_micros FROM campaign "
                  f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' "
                  f"AND '{SETTLED}'"):
        k = keyf(r)
        agg[k]["clicks"] += r.metrics.clicks
        agg[k]["invalid"] += r.metrics.invalid_clicks
        agg[k]["cost"] += r.metrics.cost_micros / 1e6
    inv[lbl] = {k: {**v, "cost": round(v["cost"], 2),
                    "raw": v["clicks"] + v["invalid"],
                    "invalid_pct": round(100 * v["invalid"] / (v["clicks"] + v["invalid"]), 2)
                    if v["clicks"] + v["invalid"] else 0} for k, v in agg.items()}
    print(f"\n  by {lbl}:")
    for k, v in sorted(inv[lbl].items(), key=lambda kv: -kv[1]["invalid"]):
        print(f"    {k:<24} reported clicks={v['clicks']:<5} invalid={v['invalid']:<6} "
              f"raw={v['raw']:<6} invalid%={v['invalid_pct']:>6.2f}  cost=${v['cost']:.2f}")
out["invalid_traffic"] = inv
le = inv["click_type"].get("LOCATION_EXPANSION", {})
lconv = 0.0
for r in q(c, f"SELECT campaign.id, segments.click_type, metrics.conversions FROM campaign "
              f"WHERE campaign.id IN ({IN5}) AND segments.date BETWEEN '2026-08-14' "
              f"AND '{SETTLED}'"):
    if E(r.segments.click_type) == "LOCATION_EXPANSION":
        lconv += r.metrics.conversions
print(f"\n  LOCATION_EXPANSION also produced {lconv:.0f} raw Primary conversion records.")
print("  Qualification of those records is UNKNOWN, so no exclusion is recommended.")
out["location_expansion_primary_records"] = round(lconv, 2)

write(EVID / "2026-09-10-analysis.json", out)
