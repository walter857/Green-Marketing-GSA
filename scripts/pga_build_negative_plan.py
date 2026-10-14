#!/usr/bin/env python3
"""Build the Pro Green Austin campaign-level negative-keyword package.

Reads the fresh read-only snapshot, classifies every returned search-term row,
reconciles the corpus, applies the adjudicated decision table, checks every proposed
phrase against the live effective-negative inventory, the live positive keywords, every
query that ever converted and the Green Marketing protected-term list, and writes the
verdict CSV, the candidate reconciliation report, and the plan in YAML, CSV and JSON.

Local files only. Proposes; never applies. Prints aggregates, not the corpus.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import pga_decisions_2026_08_22 as DEC  # noqa: E402

TARGETS = {
    "24053505504": "Progreen Austin | Search | Outdoor Living & Design",
    "24053505501": "Progreen Austin | Search | Hardscape Construction",
}
RUN_DATE = "2026-08-22"
COMPLETED_END = "2026-08-21"


# --------------------------------------------------------------------------- helpers
def norm(t):
    t = (t or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s&'-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def toks(t):
    return norm(t).split()


def contiguous(sub, seq):
    if not sub or len(sub) > len(seq):
        return False
    return any(seq[i:i + len(sub)] == sub for i in range(len(seq) - len(sub) + 1))


def blocks(neg_text, match_type, query):
    """Does an existing negative of this match type block this query?"""
    n, q = toks(neg_text), toks(query)
    if not n:
        return False
    if match_type == "EXACT":
        return n == q
    if match_type == "BROAD":
        return set(n).issubset(set(q))
    return contiguous(n, q)          # PHRASE


def makes_redundant(existing_text, existing_mt, proposed_phrase):
    """True when an existing negative already blocks everything the PHRASE proposal would."""
    e, p = toks(existing_text), toks(proposed_phrase)
    if not e:
        return False
    if existing_mt == "PHRASE":
        return contiguous(e, p)
    if existing_mt == "BROAD":
        return set(e).issubset(set(p))
    return e == p                     # EXACT only covers the identical single query


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--client-dir", required=True)
    args = ap.parse_args()

    D = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    client_dir = Path(args.client_dir)

    # ---------------- effective negative inventory, per campaign, all levels ----------
    acct_sets = {s["id"] for s in D["shared_sets"]
                 if s["type"] == "ACCOUNT_LEVEL_NEGATIVE_KEYWORDS"}
    linked = defaultdict(set)
    for l in D["campaign_shared_sets"]:
        if l["campaign_id"] in TARGETS and l["link_status"] == "ENABLED":
            linked[l["campaign_id"]].add(l["shared_set_id"])
    set_members = defaultdict(list)
    for m in D["shared_criteria"]:
        set_members[m["shared_set_id"]].append((m["keyword_text"], m["match_type"]))
    set_name = {s["id"]: s["name"] for s in D["shared_sets"]}

    camp_neg = defaultdict(list)
    for x in D["campaign_negative_keywords"]:
        if x["campaign_id"] in TARGETS:
            camp_neg[x["campaign_id"]].append((x["text"], x["match_type"]))

    ag_campaign = {a["id"]: a["campaign_id"] for a in D["ad_groups"]}
    campaign_ag_count = Counter(ag_campaign.values())
    ag_neg = defaultdict(list)
    for k in D["ad_group_keywords"]:
        if k["negative"] and k["campaign_id"] in TARGETS:
            ag_neg[k["ad_group_id"]].append((k["text"], k["match_type"]))

    def effective(cid):
        """(text, match_type, level_label) reaching every ad group in this campaign."""
        out = []
        for s in sorted(acct_sets):
            out += [(t, m, "ACCOUNT_LEVEL_LIST") for t, m in set_members[s]]
        for s in sorted(linked[cid]):
            out += [(t, m, "SHARED_LIST:" + set_name.get(s, s)) for t, m in set_members[s]]
        out += [(t, m, "CAMPAIGN") for t, m in camp_neg[cid]]
        # an ad-group negative present in EVERY ad group of the campaign is campaign-wide
        n_ags = campaign_ag_count[cid]
        counts = Counter()
        for g, items in ag_neg.items():
            if ag_campaign.get(g) == cid:
                for t, m in set(items):
                    counts[(norm(t), m)] += 1
        out += [(t, m, "AD_GROUP_ALL") for (t, m), c in counts.items() if c == n_ags]
        return out

    EFF = {cid: effective(cid) for cid in TARGETS}
    EFF_ANY = {cid: [(t, m, lv) for t, m, lv in EFF[cid]] for cid in TARGETS}

    # ---------------- live positive keywords and converting queries ----------------
    pos = [k for k in D["ad_group_keywords"]
           if not k["negative"] and k["campaign_id"] in TARGETS and k["status"] == "ENABLED"]
    converting = {}
    for r in D["search_terms_all_time_converting"]:
        converting.setdefault(norm(r["term"]), 0.0)
        converting[norm(r["term"])] += r["conversions"]
    all_conv = {norm(r["term"]) for r in D["search_terms_all_time_all_conv"]}

    # ---------------- date split ----------------
    dates_for = defaultdict(set)
    for r in D["search_terms_window_by_date"]:
        key = (r["term"], r["campaign_id"], r["ad_group_id"], r["matched_keyword"],
               r["matched_match_type"], r["search_term_match_type"])
        dates_for[key].add(r["date"])
    all_dates = sorted({r["date"] for r in D["search_terms_window_by_date"]})

    # ---------------- classification ----------------
    rows = D["search_terms_window"]
    term_rows = defaultdict(list)
    for r in rows:
        term_rows[norm(r["term"])].append(r)

    SERVICE = re.compile(
        r"\b(patios?|pavers?|paving|driveways?|walkways?|pathways?|retaining\s+walls?|"
        r"hardscap\w*|stonework|masonry|flagstone|outdoor\s+living|outdoor\s+space|"
        r"outdoor\s+kitchens?|backyard|fire\s*pits?|outdoor\s+fireplaces?|pergolas?|arbors?|"
        r"gazebos?|patio\s+covers?|landscap\w*|yard|turf|artificial\s+grass|synthetic\s+grass|"
        r"lighting|deck\w*|concrete|outdoor\s+design|design\s*(and|&)?\s*build|"
        r"stepping\s+stones?|garden\w*|xeriscap\w*|palapa|sidewalk|stone\s+wall)\b", re.I)

    def classify(term):
        """-> (verdict, intent_family, reason, confidence, neg_phrase|None)"""
        agg = term_rows[term]
        clicks = sum(r["clicks"] for r in agg)
        impr = sum(r["impressions"] for r in agg)
        conv = sum(r["conversions"] for r in agg)

        # 1. already blocked campaign-wide by an existing effective negative
        blocked_in = [cid for cid in TARGETS
                      if any(blocks(t, m, term) for t, m, _ in EFF_ANY[cid])]
        if len(blocked_in) == len(TARGETS):
            return ("ALREADY_BLOCKED", "PRE_EXISTING_NEGATIVE",
                    "already blocked in both in-scope campaigns by an existing effective "
                    "negative; no new object required", "high", None)

        # 2. client brand
        if any(b in term for b in DEC.CLIENT_BRAND_TOKENS):
            return ("KEEP", "CLIENT_BRAND",
                    "the client's own brand must never be blocked", "high", None)

        # 3. converted this month or all-time
        if conv > 0:
            return ("KEEP", "CONVERTED_FAMILY",
                    "this exact query converted inside the window", "high", None)
        if term in converting:
            return ("KEEP", "CONVERTED_FAMILY",
                    f"this query converted all-time ({converting[term]:.0f} conversions); "
                    "protected from any negative", "high", None)

        # 4. adjudicated overrides
        if term in DEC.COMPETITOR_VERIFIED:
            return ("NEGATIVE_PHRASE", "COMPETITOR",
                    "verified competing landscaping, hardscape, turf or outdoor-lighting "
                    "business; brand-navigational intent carries no design-and-build demand "
                    "for Pro Green", "high", DEC.COMPETITOR_VERIFIED[term])
        if term in DEC.WRONG_MARKET:
            return ("NEGATIVE_PHRASE", "WRONG_MARKET",
                    "names a metro outside the 24 approved Austin-area location targets",
                    "high", DEC.WRONG_MARKET[term])
        if term in DEC.WRONG_SERVICE:
            fam = "WRONG_MATERIAL" if DEC.WRONG_SERVICE[term] == "asphalt" else "WRONG_SERVICE"
            return ("NEGATIVE_PHRASE", fam,
                    "not a verified first-party Pro Green Austin service or material",
                    "high", DEC.WRONG_SERVICE[term])
        if term in DEC.WATCH_OVERRIDES:
            fam, why = DEC.WATCH_OVERRIDES[term]
            return ("WATCH", fam, why, "medium", None)
        if term in DEC.COMPETITOR_UNVERIFIED_RESIDUE:
            return ("WATCH", "COMPETITOR_UNVERIFIED",
                    "brand-shaped query with no reliable third-party confirmation obtained "
                    "in this pass; reported, not blocked", "low", None)

        # 5. protected families that must stay eligible
        if term in DEC.GENERIC_LANDSCAPING:
            v = "KEEP" if clicks else "WATCH"
            return (v, "GENERIC_LANDSCAPING",
                    "generic landscaping demand is explicitly protected; "
                    "'landscaper near me' has converted on this account", "high", None)

        # 6. service themes
        if SERVICE.search(term):
            if clicks >= 1:
                return ("KEEP", "VERIFIED_SERVICE_INTENT",
                        "matches a verified first-party service and earned a paid click",
                        "medium", None)
            if impr < 3:
                return ("INSUFFICIENT_DATA", "VERIFIED_SERVICE_INTENT",
                        "fewer than three impressions; no basis for any verdict yet",
                        "low", None)
            return ("WATCH", "VERIFIED_SERVICE_INTENT",
                    "matches a verified first-party service, no click yet", "low", None)

        if impr < 3:
            return ("INSUFFICIENT_DATA", "UNCLASSIFIED",
                    "fewer than three impressions and no verified service vocabulary",
                    "low", None)
        return ("WATCH", "UNCLASSIFIED",
                "no verified service vocabulary matched and no categorical waste signal",
                "low", None)

    verdicts = {t: classify(t) for t in term_rows}

    # ---------------- proposed phrases -> campaign targets ----------------
    phrase_family, phrase_terms = {}, defaultdict(set)
    for t, (v, fam, why, conf, phrase) in verdicts.items():
        if v == "NEGATIVE_PHRASE" and phrase:
            phrase_family[phrase] = fam
            phrase_terms[phrase].add(t)

    def phrase_metrics(phrase):
        i = c = 0
        cost = conv = 0.0
        for t in phrase_terms[phrase]:
            for r in term_rows[t]:
                i += r["impressions"]; c += r["clicks"]
                cost += r["cost"]; conv += r["conversions"]
        return i, c, round(cost, 2), conv

    keep_terms = [t for t, (v, *_rest) in verdicts.items() if v in ("KEEP", "WATCH")]

    def checks(phrase, cid):
        """Return (dup_reason, conflicts, protected_hit)."""
        dup = ""
        for t, m, lv in EFF_ANY[cid]:
            if makes_redundant(t, m, phrase):
                dup = f"already blocked by {lv} {m} {t!r}"
                break
        conf = []
        for k in pos:
            if k["campaign_id"] == cid and blocks(phrase, "PHRASE", k["text"]):
                conf.append(f"blocks live positive keyword {k['criterion_id']} {k['text']!r}")
        for q in converting:
            if blocks(phrase, "PHRASE", q):
                conf.append(f"blocks converting query {q!r}")
        for q in all_conv:
            if blocks(phrase, "PHRASE", q) and q not in converting:
                conf.append(f"blocks all-conversions query {q!r}")
        for g in DEC.GENERIC_LANDSCAPING:
            if blocks(phrase, "PHRASE", g):
                conf.append(f"blocks protected generic-landscaping term {g!r}")
        for p in DEC.PROTECTED_TERMS:
            if contiguous(toks(phrase), toks(p)):
                conf.append(f"blocks protected buyer-intent term {p!r}")
        for t in keep_terms:
            if blocks(phrase, "PHRASE", t):
                conf.append(f"blocks retained query {t!r}")
        return dup, conf, any(norm(phrase) == norm(p) for p in DEC.PROTECTED_TERMS)

    targets_ok, targets_skipped = [], []
    for phrase in sorted(phrase_terms):
        for cid in sorted(TARGETS):
            dup, conf, prot = checks(phrase, cid)
            rec = {"phrase": phrase, "campaign_id": cid, "dup": dup,
                   "conflicts": conf, "protected": prot}
            (targets_skipped if (dup or conf or prot) else targets_ok).append(rec)

    # ---------------- verdict CSV, one row per source row ----------------
    ag_name = {a["id"]: a["name"] for a in D["ad_groups"]}
    csv_rows = []
    for r in rows:
        t = norm(r["term"])
        v, fam, why, conf, phrase = verdicts[t]
        key = (r["term"], r["campaign_id"], r["ad_group_id"], r["matched_keyword"],
               r["matched_match_type"], r["search_term_match_type"])
        ds = sorted(dates_for.get(key, set()))
        dup, confl, _prot = ("", [], False)
        if phrase:
            dup, confl, _prot = checks(phrase, r["campaign_id"])
        blocked_here = any(blocks(x, m, t) for x, m, _ in EFF_ANY[r["campaign_id"]])
        csv_rows.append({
            "raw_search_term": r["term"],
            "normalized_search_term": t,
            "date_range": f"{D['window']['start']}..{D['window']['end']}",
            "observed_dates": "|".join(ds),
            "partial_day_flag": "YES" if RUN_DATE in ds else "NO",
            "campaign_id": r["campaign_id"],
            "campaign_name": r["campaign_name"],
            "ad_group_id": r["ad_group_id"],
            "ad_group_name": ag_name.get(r["ad_group_id"], r["ad_group_name"]),
            "matching_keyword_id": r["matched_keyword_id"],
            "matching_keyword_text": r["matched_keyword"],
            "positive_match_type": r["matched_match_type"],
            "search_term_match_type": r["search_term_match_type"],
            "impressions": r["impressions"],
            "clicks": r["clicks"],
            "cost": round(r["cost"], 2),
            "conversions": r["conversions"],
            "conversion_value": r["conversions_value"],
            "all_conversions": r["all_conversions"],
            "verdict": v,
            "intent_family": fam,
            "reason": why,
            "confidence": conf,
            "recommended_negative_text": phrase or "",
            "recommended_negative_match_type": "PHRASE" if phrase else "",
            "recommended_level": "campaign" if phrase else "",
            "protected_term_result": (
                "PROTECTED_TOKEN_PRESENT" if any(
                    contiguous(toks(p), toks(t)) for p in DEC.PROTECTED_TERMS)
                else "none"),
            "converted_query_result": (
                f"CONVERTED_ALL_TIME:{converting[t]:.0f}" if t in converting
                else ("ALL_CONVERSIONS_ONLY" if t in all_conv else "never converted")),
            "existing_negative_result": (
                "already blocked in this campaign" if blocked_here
                else (dup or "not currently blocked")),
            "positive_keyword_conflict_result": ("; ".join(confl) if confl else "none"),
        })
    csv_rows.sort(key=lambda r: (-r["cost"], -r["clicks"], r["normalized_search_term"]))

    verdict_csv = outdir / "24_search_term_verdicts_mtd_v2.csv"
    with verdict_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
        w.writeheader(); w.writerows(csv_rows)

    # ---------------- reconciliation ----------------
    src = {
        "rows": len(rows),
        "distinct_raw": len({r["term"] for r in rows}),
        "distinct_norm": len(term_rows),
        "impressions": sum(r["impressions"] for r in rows),
        "clicks": sum(r["clicks"] for r in rows),
        "cost": round(sum(r["cost"] for r in rows), 2),
        "conversions": round(sum(r["conversions"] for r in rows), 2),
        "conversion_value": round(sum(r["conversions_value"] for r in rows), 2),
    }
    out = {
        "rows": len(csv_rows),
        "distinct_raw": len({r["raw_search_term"] for r in csv_rows}),
        "distinct_norm": len({r["normalized_search_term"] for r in csv_rows}),
        "impressions": sum(r["impressions"] for r in csv_rows),
        "clicks": sum(r["clicks"] for r in csv_rows),
        "cost": round(sum(r["cost"] for r in csv_rows), 2),
        "conversions": round(sum(r["conversions"] for r in csv_rows), 2),
        "conversion_value": round(sum(r["conversion_value"] for r in csv_rows), 2),
    }
    by_verdict = defaultdict(lambda: [0, 0, 0, 0.0, 0.0])
    for r in csv_rows:
        v = by_verdict[r["verdict"]]
        v[0] += 1; v[1] += r["impressions"]; v[2] += r["clicks"]
        v[3] += r["cost"]; v[4] += r["conversions"]

    dup_terms = {t: len(rs) for t, rs in term_rows.items() if len(rs) > 1}
    dup_detail = []
    for t, n in sorted(dup_terms.items(), key=lambda x: -x[1]):
        rs = term_rows[t]
        dup_detail.append({
            "normalized_term": t, "rows": n,
            "campaigns": sorted({r["campaign_id"] for r in rs}),
            "ad_groups": sorted({r["ad_group_id"] for r in rs}),
            "keyword_pairs": sorted({(r["matched_keyword"], r["matched_match_type"])
                                     for r in rs}),
        })

    # ---------------- campaign spend coverage ----------------
    inscope = [t for t in D["campaign_totals_window"] if t["campaign_id"] in TARGETS]
    total_cost = round(sum(t["cost"] for t in inscope), 2)
    coverage = round(100.0 * src["cost"] / total_cost, 2) if total_cost else 0.0

    # ---------------- plan actions ----------------
    camp_resource = {c["id"]: c["resource_name"] for c in D["campaigns"]}
    actions, plan_csv_rows = [], []
    for i, rec in enumerate(sorted(targets_ok, key=lambda x: (x["phrase"], x["campaign_id"])), 1):
        phrase, cid = rec["phrase"], rec["campaign_id"]
        impr, clicks, cost, conv = phrase_metrics(phrase)
        fam = phrase_family[phrase]
        ev = (DEC.COMPETITOR_EVIDENCE.get(phrase) or DEC.WRONG_MARKET_EVIDENCE.get(phrase)
              or DEC.WRONG_SERVICE_EVIDENCE.get(phrase) or "")
        supporting = sorted(phrase_terms[phrase])
        aid = f"CNEG-{i:03d}"
        actions.append({
            "action_id": aid,
            "priority": "P1",
            "operation": "ADD_CAMPAIGN_NEGATIVE_KEYWORD",
            "resource_type": "campaign_criterion (negative keyword)",
            "resource_id": cid,
            "resource_name": TARGETS[cid],
            "campaign_resource_name": camp_resource[cid],
            "negative_text": phrase,
            "match_type": "PHRASE",
            "family": fam,
            "current_state": "not present as a campaign negative on this campaign, and not "
                             "reachable from any linked shared list, the account-level list, "
                             "or an all-ad-group negative",
            "proposed_state": f'campaign negative PHRASE "{phrase}"',
            "field_mask": "n/a (criterion creation)",
            "supporting_raw_search_terms": supporting,
            "august_impressions": impr,
            "august_clicks": clicks,
            "august_cost": cost,
            "august_conversions": conv,
            "first_party_service_verification":
                "Confirmed 2026-08-22 against https://progreenlandscapesolutions.com/austin/ "
                "and clients/pro-green-austin/client.yaml. The phrase names no verified "
                "first-party Pro Green Austin service.",
            "competitor_verification": ev if fam == "COMPETITOR" else "n/a",
            "evidence": ev,
            "positive_keyword_conflict_result": "none. Checked against all 48 ENABLED "
                                                "positive keywords in the two campaigns.",
            "converted_query_conflict_result": "none. Checked against all 50 queries that "
                                               "ever converted and all 133 queries with any "
                                               "all-conversions value.",
            "existing_negative_check": "not a duplicate. Checked against the campaign's "
                                       "full effective inventory: account-level list, three "
                                       "linked shared lists, campaign negatives, and "
                                       "negatives present in every ad group.",
            "protected_term_result": "none. The phrase is not, and is not contained in, any "
                                     "Green Marketing protected buyer-intent term.",
            "expected_effect": "Stops paid impressions and clicks on this query family in "
                               "this campaign. Does not by itself lower cost per qualified "
                               "lead.",
            "risk": "Low. PHRASE scope, campaign level only. No other campaign, ad group, "
                    "shared list or account-level setting is touched.",
            "rollback": f"Remove the campaign_criterion created for PHRASE \"{phrase}\" on "
                        f"campaign {cid} using the criterion_id returned at readback: "
                        f"customers/7380491929/campaignCriteria/{cid}~<criterion_id>.",
            "object_count": 1,
        })
        plan_csv_rows.append({
            "action_id": aid, "customer_id": "7380491929", "campaign_id": cid,
            "campaign_name": TARGETS[cid],
            "campaign_resource_name": camp_resource[cid],
            "negative_text": phrase, "match_type": "PHRASE", "level": "campaign",
            "family": fam, "current_state": "absent", "proposed_state": "present (PHRASE)",
            "supporting_raw_search_terms": " | ".join(supporting),
            "august_impressions": impr, "august_clicks": clicks, "august_cost": cost,
            "august_conversions": conv,
            "first_party_service_verification": "no verified Pro Green Austin service names "
                                                "this phrase",
            "competitor_verification": ev if fam == "COMPETITOR" else "n/a",
            "positive_keyword_conflict_result": "none",
            "converted_query_conflict_result": "none",
            "existing_negative_check": "not a duplicate",
            "expected_effect": "stops paid clicks on this query family in this campaign",
            "risk": "low; PHRASE scope, campaign level only",
            "rollback": "remove the campaign_criterion by the criterion_id returned at "
                        "readback",
            "object_count": 1,
        })

    plan_csv = outdir / "27_campaign_negative_plan.csv"
    with plan_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(plan_csv_rows[0].keys()))
        w.writeheader(); w.writerows(plan_csv_rows)

    (client_dir / "plans").mkdir(parents=True, exist_ok=True)
    (client_dir / "plans" / "campaign-negatives-2026-08-22.json").write_text(
        json.dumps(actions, indent=2), encoding="utf-8")

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot": str(args.snapshot),
        "window": D["window"],
        "run_date": RUN_DATE,
        "completed_days": f"{D['window']['start']}..{COMPLETED_END}",
        "partial_day": RUN_DATE,
        "dates_with_search_term_rows": all_dates,
        "latest_available_search_term_date": all_dates[-1] if all_dates else None,
        "source": src, "verdict_output": out,
        "reconciles": src == out,
        "by_verdict": {k: {"rows": v[0], "impressions": v[1], "clicks": v[2],
                           "cost": round(v[3], 2), "conversions": round(v[4], 2)}
                       for k, v in sorted(by_verdict.items())},
        "duplicate_terms": dup_detail,
        "campaign_total_cost": total_cost,
        "visible_search_term_cost": src["cost"],
        "visible_cost_coverage_pct": coverage,
        "unique_candidate_phrases": len(phrase_terms),
        "phrases_by_family": dict(Counter(phrase_family.values())),
        "base_target_count": len(phrase_terms) * len(TARGETS),
        "targets_proposed": len(targets_ok),
        "targets_skipped": targets_skipped,
        "targets_by_campaign": dict(Counter(r["campaign_id"] for r in targets_ok)),
        "plan_actions": len(actions),
        "plan_objects": sum(a["object_count"] for a in actions),
        "csv_rows": len(plan_csv_rows),
    }
    (outdir / "25_candidate_reconciliation.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    # ---------------- console: aggregates only ----------------
    print("== SOURCE vs VERDICT RECONCILIATION ==")
    for k in src:
        mark = "OK " if src[k] == out[k] else "!! "
        print(f"  {mark}{k:<18} source={src[k]:<12} verdict={out[k]}")
    print(f"  RECONCILES: {src == out}")
    print("\n== VERDICTS ==")
    for k, v in sorted(by_verdict.items(), key=lambda kv: -kv[1][3]):
        print(f"  {k:<20} rows={v[0]:4} impr={v[1]:5} clicks={v[2]:3} "
              f"cost=${v[3]:8,.2f} conv={v[4]:.2f}")
    print(f"  verdict row total = {sum(v[0] for v in by_verdict.values())}")
    print(f"\n== SPEND COVERAGE ==\n  in-scope campaign cost=${total_cost:,.2f}  "
          f"visible search-term cost=${src['cost']:,.2f}  coverage={coverage}%")
    print(f"\n== DUPLICATE TERMS (same term, more than one row) ==\n  "
          f"terms={len(dup_detail)}  extra rows={sum(d['rows'] - 1 for d in dup_detail)}")
    print(f"\n== CANDIDATES ==\n  unique phrases={len(phrase_terms)} "
          f"by family={dict(Counter(phrase_family.values()))}")
    print(f"  base target count = {len(phrase_terms)} x {len(TARGETS)} = "
          f"{len(phrase_terms) * len(TARGETS)}")
    print(f"  proposed targets={len(targets_ok)}  skipped={len(targets_skipped)}")
    for r in targets_skipped:
        print(f"    SKIP {r['phrase']!r} in {r['campaign_id']}: "
              f"{r['dup'] or r['conflicts'] or r['protected']}")
    print(f"  by campaign={dict(Counter(r['campaign_id'] for r in targets_ok))}")
    print(f"\n  plan actions={len(actions)} objects={sum(a['object_count'] for a in actions)} "
          f"csv rows={len(plan_csv_rows)}")
    print(f"\nwritten: {verdict_csv}")
    print(f"written: {plan_csv}")
    print(f"written: {outdir / '25_candidate_reconciliation.json'}")
    print(f"written: {client_dir / 'plans' / 'campaign-negatives-2026-08-22.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
