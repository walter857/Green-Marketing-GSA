#!/usr/bin/env python3
"""Strict SKAG cross-negative matrix, collision test and routing simulation.

Builds the full negative-EXACT sibling mirror for the final six-intent
architecture, supplements it from observed search-term history, evaluates
modifier-level routing negatives, and programmatically collision-tests every
proposal against owner keywords, historical queries and landing-page intent.

READ + DRAFT ONLY. SELECT statements only; constructs no operation and calls no
mutate service. Emits CSV/markdown recommendations - nothing is created.

Key Google behaviour this depends on:
  * POSITIVE keywords match close variants.
  * NEGATIVE keywords DO NOT match close variants.
That asymmetry is why the exact mirror alone cannot finish the job.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gm_gsa.config import load_dotenv_if_available, normalize_customer_id
from gm_gsa.credentials import load_google_ads_client
from gm_gsa.google_ads import enum_name

CID = "1521725229"
AUD = ROOT / "clients/softwind-power-washing/audits"
SNAP = ROOT / "clients/softwind-power-washing/snapshots"
CAMP_A, CAMP_B = "24103511039", "24145053510"

# ---------------------------------------------------------------- architecture
# Owner assignment. Every unique positive keyword text has EXACTLY ONE owner.
OWNERS: dict[str, dict] = {
    "Power Washing": {
        "intent": "power washing service, purchase intent",
        "lp": "https://offer.softwindli.com/power-washing-services-islip-west-islip-dix-hills/",
        "exists": "202870585390 (Power Washing Near Me) - rename/expand",
        "keywords": {
            "power washing": ["PHRASE"],
            "power washing near me": ["PHRASE", "EXACT"],
            "power washing service": ["PHRASE", "EXACT"],
            "power washing services near me": ["EXACT"],
            "power washing company near me": ["EXACT"],
        },
    },
    "Pressure Washing": {
        "intent": "pressure washing service, purchase intent",
        "lp": "https://offer.softwindli.com/residential-pressure-washing/",
        "exists": "NEW - create paused",
        "keywords": {
            "pressure washing": ["PHRASE"],
            "pressure washing near me": ["PHRASE", "EXACT"],
            "residential pressure washing near me": ["EXACT"],
        },
    },
    "House Washing": {
        "intent": "whole-house exterior washing",
        "lp": "https://offer.softwindli.com/house-washing-company/",
        "exists": "NEW - create paused",
        "keywords": {
            "house washing near me": ["PHRASE", "EXACT"],
            "house pressure washing near me": ["EXACT"],
            "house power washing near me": ["EXACT"],
            "exterior house washing near me": ["EXACT"],
        },
    },
    "Soft Washing": {
        "intent": "low-pressure soft washing for siding, trim and fences",
        "lp": "https://offer.softwindli.com/soft-house-washing/",
        "exists": "198082078703 (Soft House Washing Near Me) - already live",
        "keywords": {
            "soft washing near me": ["EXACT"],
            "soft house washing near me": ["PHRASE", "EXACT"],
        },
    },
    "Driveway Pressure Washing": {
        "intent": "driveway surface washing",
        "lp": "https://offer.softwindli.com/driveway-pressure-washing/",
        "exists": "198082079023 (Driveway Pressure Washing Near Me) - already live",
        "keywords": {
            "driveway pressure washing near me": ["PHRASE", "EXACT"],
            "driveway power washing near me": ["EXACT"],
        },
    },
    "Patio Pressure Washing": {
        "intent": "patio, deck and concrete hard-surface washing",
        "lp": "https://offer.softwindli.com/patio-power-washing/",
        "exists": "198082079183 (Patio Pressure Washing Near Me) - already live",
        "keywords": {
            "patio pressure washing near me": ["PHRASE", "EXACT"],
            "patio power washing near me": ["EXACT"],
            "concrete pressure washing near me": ["EXACT"],
        },
    },
}

# Intended owner for observed queries. NONE = no owner (cost cluster / out of scope).
QUERY_OWNER_RULES = [
    (re.compile(r"\broof|\bgutter|\bwindow\b|house cleaning services|"
                r"washing repair|washer repair|gas station|commercial", re.I), None),
    (re.compile(r"\bcost\b|\bprice|how much", re.I), None),
    (re.compile(r"\bdeck\b|\bpatio\b|\bconcrete\b|\bpaver|walkway", re.I), "Patio Pressure Washing"),
    (re.compile(r"\bdriveway\b", re.I), "Driveway Pressure Washing"),
    # "soft ?wash" alone does NOT match "soft house washing near me" - after
    # "soft" comes " house", not "wash". Widen it, and keep it AHEAD of the
    # house rule, because "soft house washing" is a SOFT WASHING intent.
    (re.compile(r"soft\s*(house\s*)?wash", re.I), "Soft Washing"),
    (re.compile(r"\bhouse\b|\bhome\b|exterior|siding", re.I), "House Washing"),
    (re.compile(r"pressure ?wash|jet ?wash", re.I), "Pressure Washing"),
    (re.compile(r"power ?wash", re.I), "Power Washing"),
]


def intended_owner(q: str):
    for rx, owner in QUERY_OWNER_RULES:
        if rx.search(q):
            return owner
    return None


# ------------------------------------------------------------ matching helpers
def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


STOP = {"a", "the", "in", "for", "of", "to", "my", "your", "and"}


def canon(s: str) -> str:
    """Close-variant canonical form: strip stopwords/plurals, unify power/press wording."""
    t = norm(s)
    t = t.replace("powerwashing", "power washing").replace("powerwash", "power wash")
    t = t.replace("pressurewashing", "pressure washing").replace("pressurewash", "pressure wash")
    t = re.sub(r"\bpower washing\b", "powerwash", t)
    t = re.sub(r"\bpower wash\b", "powerwash", t)
    t = re.sub(r"\bpressure washing\b", "pressurewash", t)
    t = re.sub(r"\bpressure wash\b", "pressurewash", t)
    words = [w for w in re.findall(r"[a-z]+", t) if w not in STOP]
    words = [re.sub(r"e?s$", "", w) if len(w) > 4 else w for w in words]
    return " ".join(sorted(words))


def phrase_contains(kw: str, q: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(norm(kw)) + r"(?!\w)", norm(q)) is not None


def positive_matches(kw: str, mt: str, q: str, loose: bool) -> bool:
    """Would this POSITIVE keyword be eligible for query q? Positives DO close-variant."""
    k, qq = norm(kw), norm(q)
    if mt == "EXACT":
        if k == qq:
            return True
        return loose and canon(k) == canon(qq)
    # PHRASE
    if phrase_contains(k, qq):
        return True
    if not loose:
        return False
    kt = canon(k).split()
    qt = set(canon(qq).split())
    return bool(kt) and all(w in qt for w in kt)


def negative_blocks(neg: str, mt: str, q: str) -> bool:
    """Would this NEGATIVE block query q? Negatives DO NOT close-variant."""
    n, qq = norm(neg), norm(q)
    if mt == "EXACT":
        return n == qq
    if mt == "PHRASE":
        return phrase_contains(n, qq)
    return all(re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", qq) for w in n.split())


def main() -> int:
    load_dotenv_if_available(ROOT / ".env")
    svc = load_google_ads_client().get_service("GoogleAdsService")
    cid = normalize_customer_id(CID)
    now = datetime.now(ZoneInfo("America/New_York"))

    c = list(svc.search(customer_id=cid, query="""SELECT customer.id,
        customer.descriptive_name, customer.manager, customer.test_account
        FROM customer LIMIT 1"""))[0].customer
    assert c.descriptive_name == "Softwind Power Washing - Live"
    assert normalize_customer_id(c.id) == CID and not c.manager and not c.test_account
    print(f"IDENTITY GATE: PASS  {c.descriptive_name} | {c.id}\n")

    # ---------- live state ----------
    live_kw = defaultdict(list)   # text -> [(campaign, ad_group, match, serving)]
    for r in svc.search(customer_id=cid, query="""SELECT campaign.id, campaign.name,
            ad_group.id, ad_group.name, ad_group.status,
            ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
            ad_group_criterion.status FROM keyword_view"""):
        k = r.ad_group_criterion
        live_kw[norm(k.keyword.text)].append((
            r.campaign.name, r.ad_group.name, enum_name(k.keyword.match_type),
            enum_name(r.ad_group.status) == "ENABLED"
            and enum_name(k.status) == "ENABLED"))

    hist = defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "routes": set()})
    for r in svc.search(customer_id=cid, query="""SELECT campaign.name, ad_group.name,
            search_term_view.search_term, segments.keyword.info.text,
            metrics.impressions, metrics.clicks, metrics.cost_micros
            FROM search_term_view
            WHERE segments.date BETWEEN '2026-07-01' AND '2026-08-31'"""):
        d = hist[norm(r.search_term_view.search_term)]
        d["impr"] += int(r.metrics.impressions)
        d["clicks"] += int(r.metrics.clicks)
        d["cost"] += int(r.metrics.cost_micros) / 1e6
        d["routes"].add(f"{r.campaign.name}/{r.ad_group.name}")

    # ---------- 1. ownership ----------
    text_owner = {}
    for ag, spec in OWNERS.items():
        for t in spec["keywords"]:
            assert norm(t) not in text_owner, f"DUPLICATE OWNER for {t}"
            text_owner[norm(t)] = ag
    all_texts = sorted(text_owner)
    print(f"=== OWNERSHIP: {len(all_texts)} unique positive keyword texts, "
          f"{len(OWNERS)} ad groups ===")
    for ag, spec in OWNERS.items():
        print(f"  {ag:26s} {len(spec['keywords'])} texts  | {spec['exists']}")

    # ---------- 2. exact sibling mirror ----------
    mirror = []
    for ag in OWNERS:
        for t in all_texts:
            if text_owner[t] == ag:
                continue
            mirror.append({"negative_ad_group": ag, "negative_keyword": t,
                           "negative_match_type": "EXACT",
                           "owner_ad_group": text_owner[t], "owner_keyword": t,
                           "kind": "SIBLING MIRROR"})
    raw = sum(len(all_texts) - len(OWNERS[ag]["keywords"]) for ag in OWNERS)
    dedup = {(m["negative_ad_group"], m["negative_keyword"], m["negative_match_type"])
             for m in mirror}
    print(f"\n=== EXACT SIBLING MIRROR ===")
    print(f"  unique texts={len(all_texts)}  sibling groups per text={len(OWNERS)-1}")
    print(f"  raw mirror count = {raw}   after dedup = {len(dedup)}   "
          f"duplicates removed = {raw - len(dedup)}")
    for ag in OWNERS:
        n = len(all_texts) - len(OWNERS[ag]["keywords"])
        print(f"    {ag:26s} receives {n:3d} negative EXACT")

    # ---------- 3. close-variant supplement, evidence-driven ----------
    supplement = []
    for q, d in sorted(hist.items(), key=lambda x: -x[1]["cost"]):
        own = intended_owner(q)
        if own is None:
            continue
        if norm(q) in text_owner:
            continue  # already covered by the mirror
        blocked_by_mirror = any(
            negative_blocks(t, "EXACT", q) for t in all_texts if text_owner[t] != own)
        wrong_routes = {r for r in d["routes"]}
        needs = len(d["routes"]) > 1 or not blocked_by_mirror
        if not needs:
            continue
        for ag in OWNERS:
            if ag == own:
                continue
            # A negative is only worth placing where the ad group could actually
            # match the query, or has already served it. Blanketing all five
            # siblings generates criteria that can never fire.
            could_match = any(
                positive_matches(k, mt, q, loose=True)
                for k, mts in OWNERS[ag]["keywords"].items() for mt in mts)
            served_here = any(ag.split()[0].lower() in r.lower() for r in d["routes"])
            if not (could_match or served_here):
                continue
            supplement.append({
                "negative_ad_group": ag, "negative_keyword": q,
                "negative_match_type": "EXACT", "owner_ad_group": own,
                "owner_keyword": q, "kind": "OBSERVED CLOSE VARIANT",
                "evidence": f"{d['impr']} impr, {d['clicks']} clk, ${d['cost']:.2f}, "
                            f"served in {len(d['routes'])} route(s)"})
    print(f"\n=== OBSERVED CLOSE-VARIANT SUPPLEMENT ===")
    obs = sorted({s["negative_keyword"] for s in supplement})
    print(f"  observed queries needing an explicit negative: {len(obs)}")
    print(f"  negative criteria generated: {len(supplement)}")

    # ---------- 4. modifier candidates, collision-tested ----------
    MODIFIERS = [
        ("pressure washing", "PHRASE", "Pressure Washing"),
        ("power washing", "PHRASE", "Power Washing"),
        ("house washing", "PHRASE", "House Washing"),
        ("soft wash", "PHRASE", "Soft Washing"),
        ("driveway", "EXACT_WORD", "Driveway Pressure Washing"),
        ("patio", "EXACT_WORD", "Patio Pressure Washing"),
        ("concrete", "EXACT_WORD", "Patio Pressure Washing"),
        ("residential", "EXACT_WORD", "Pressure Washing"),
        ("company", "EXACT_WORD", "Power Washing"),
        ("service", "EXACT_WORD", "Power Washing"),
        ("services", "EXACT_WORD", "Power Washing"),
    ]
    PROTECTED = {"near me", "service", "services", "company", "quote", "estimate",
                 "cost", "price"}
    modifier_rows, approved_mods = [], []
    for text, mt in [(m[0], "PHRASE" if m[1] == "PHRASE" else "BROAD") for m in MODIFIERS]:
        pass
    for text, mtkind, protect in MODIFIERS:
        mt = "PHRASE" if mtkind == "PHRASE" else "BROAD"
        for ag in OWNERS:
            if ag == protect:
                continue
            own_blocked = [k for k in OWNERS[ag]["keywords"]
                           if negative_blocks(text, mt, k)]
            hist_blocked = [q for q in hist
                            if intended_owner(q) == ag and negative_blocks(text, mt, q)]
            protected_tok = text in PROTECTED
            if own_blocked or hist_blocked or protected_tok:
                verdict = "REJECTED"
                reason = ("protected token" if protected_tok else
                          f"blocks own keyword(s) {own_blocked}" if own_blocked else
                          f"blocks intended query {hist_blocked}")
            else:
                routed = [q for q in hist
                          if intended_owner(q) == protect and negative_blocks(text, mt, q)]
                verdict = "APPROVED" if routed else "OPTIONAL"
                reason = (f"routes {len(routed)} observed query/queries to {protect}"
                          if routed else "no observed query yet; low value")
                approved_mods.append({"negative_ad_group": ag, "negative_keyword": text,
                                      "negative_match_type": mt, "owner_ad_group": protect,
                                      "owner_keyword": f"(modifier protecting {protect})",
                                      "kind": "MODIFIER ROUTING", "verdict": verdict})
            modifier_rows.append({"negative": text, "mt": mt, "ad_group": ag,
                                  "protects": protect, "verdict": verdict,
                                  "reason": reason,
                                  "own_blocked": own_blocked,
                                  "hist_blocked": hist_blocked})
    print(f"\n=== MODIFIER-LEVEL CANDIDATES ({len(modifier_rows)} tested) ===")
    from collections import Counter
    print(f"  {dict(Counter(r['verdict'] for r in modifier_rows))}")
    for r in modifier_rows:
        if r["verdict"] == "REJECTED" and (r["own_blocked"] or r["hist_blocked"]):
            print(f"  REJECTED  '{r['negative']}' [{r['mt']}] in {r['ad_group']:26s} "
                  f"-> {r['reason'][:78]}")

    mods_final = [m for m in approved_mods if m["verdict"] == "APPROVED"]
    print(f"  APPROVED modifier negatives: {len(mods_final)}")
    for m in mods_final:
        print(f"    '{m['negative_keyword']}' [{m['negative_match_type']}] in "
              f"{m['negative_ad_group']}  (protects {m['owner_ad_group']})")

    proposals = mirror + supplement + mods_final
    print(f"\n=== TOTAL PROPOSED AD-GROUP-LEVEL ROUTING NEGATIVES: {len(proposals)} ===")

    # ---------- 5. collision test ----------
    collisions, coll_rows = [], []
    for p in proposals:
        ag = p["negative_ad_group"]
        for k, mts in OWNERS[ag]["keywords"].items():
            blocks = negative_blocks(p["negative_keyword"], p["negative_match_type"], k)
            coll_rows.append({
                "ad_group": ag, "negative_keyword": p["negative_keyword"],
                "negative_match_type": p["negative_match_type"],
                "tested_against": k, "test_type": "own positive keyword",
                "would_block": "YES" if blocks else "no",
                "intended": "no", "verdict": "COLLISION" if blocks else "PASS",
                "correction": "remove or narrow match type" if blocks else ""})
            if blocks:
                collisions.append((ag, p["negative_keyword"], k))
        for q, d in hist.items():
            if intended_owner(q) != ag:
                continue
            blocks = negative_blocks(p["negative_keyword"], p["negative_match_type"], q)
            if blocks:
                coll_rows.append({
                    "ad_group": ag, "negative_keyword": p["negative_keyword"],
                    "negative_match_type": p["negative_match_type"],
                    "tested_against": q, "test_type": "historical search term",
                    "would_block": "YES", "intended": "no", "verdict": "COLLISION",
                    "correction": "remove"})
                collisions.append((ag, p["negative_keyword"], q))
    print(f"\n=== COLLISION TEST: {len(coll_rows)} assertions ===")
    print(f"  collisions found: {len(collisions)}")
    for x in collisions[:20]:
        print(f"    {x[0]} : negative '{x[1]}' would block '{x[2]}'")
    if not collisions:
        print("  ZERO own-keyword or intended-query collisions across all proposals")

    # ---------- 6. routing simulation ----------
    SIM = ["power washing", "power wash", "powerwash", "power washing near me",
           "power washing service", "power washing services near me",
           "power washing company near me", "pressure washing", "pressure wash",
           "pressure washing near me", "pressure washing service",
           "pressure washing services near me", "residential pressure washing near me",
           "house washing near me", "house power washing near me",
           "house pressure washing near me", "exterior house washing near me",
           "soft washing near me", "soft house washing near me",
           "driveway pressure washing near me", "driveway power washing near me",
           "patio pressure washing near me", "patio power washing near me",
           "concrete pressure washing near me"]
    negs_by_ag = defaultdict(list)
    for p in proposals:
        negs_by_ag[p["negative_ad_group"]].append(
            (p["negative_keyword"], p["negative_match_type"]))

    sim_rows, pass_before, pass_after = [], 0, 0
    for q in SIM:
        before = [ag for ag in OWNERS
                  for k, mts in OWNERS[ag]["keywords"].items()
                  for mt in mts if positive_matches(k, mt, q, loose=True)]
        before = sorted(set(before))
        want = intended_owner(q)
        after = [ag for ag in before
                 if not any(negative_blocks(n, m, q) for n, m in negs_by_ag[ag])]
        after = sorted(set(after))
        if len(before) == 1 and before == [want]:
            pass_before += 1
        ok = after == [want]
        if ok:
            pass_after += 1
        residual = len(after) > 1
        applied = sorted({f"{n}[{m}]" for ag in before for n, m in negs_by_ag[ag]
                          if negative_blocks(n, m, q)})
        sim_rows.append({
            "search_query": q, "eligible_before": "|".join(before) or "none",
            "intended_owner": want or "NONE",
            "negatives_applied": "|".join(applied) or "none",
            "eligible_after": "|".join(after) or "none",
            "landing_page": OWNERS[want]["lp"] if want else "",
            "residual_overlap": "RESIDUAL CLOSE-VARIANT RISK" if residual else "no",
            "result": "PASS" if ok else ("FAIL" if not after else "RESIDUAL")})
    print(f"\n=== ROUTING SIMULATION ({len(SIM)} queries) ===")
    print(f"{'query':38s} {'before':12s} {'intended':26s} {'after':30s} result")
    for r in sim_rows:
        print(f"{r['search_query'][:38]:38s} {str(len(r['eligible_before'].split('|'))):12s} "
              f"{r['intended_owner'][:26]:26s} {r['eligible_after'][:30]:30s} {r['result']}")
    print(f"\n  routing success BEFORE negatives: {pass_before}/{len(SIM)} = "
          f"{round(100*pass_before/len(SIM),1)}%")
    print(f"  routing success AFTER  negatives: {pass_after}/{len(SIM)} = "
          f"{round(100*pass_after/len(SIM),1)}%")
    residuals = [r for r in sim_rows if r["result"] == "RESIDUAL"]
    print(f"  residual close-variant risks: {len(residuals)}")

    # ---------- 7. write files ----------
    AUD.mkdir(parents=True, exist_ok=True)

    p1 = AUD / "2026-08-31-final-skag-cross-negative-matrix.csv"
    with p1.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["owner_ad_group", "owner_keyword", "owner_positive_match_types",
                    "negative_ad_group", "negative_keyword", "negative_match_type",
                    "routing_reason", "historical_search_term_evidence",
                    "potential_blocking_risk", "collision_test",
                    "required_or_optional", "final_verdict"])
        for p in proposals:
            ow = p["owner_ad_group"]
            mts = "|".join(OWNERS[ow]["keywords"].get(p["owner_keyword"], [])) or "n/a"
            ev = p.get("evidence", "")
            if not ev and p["owner_keyword"] in hist:
                d = hist[p["owner_keyword"]]
                ev = f"{d['impr']} impr, {d['clicks']} clk, ${d['cost']:.2f}"
            w.writerow([ow, p["owner_keyword"], mts, p["negative_ad_group"],
                        p["negative_keyword"], p["negative_match_type"],
                        f"route '{p['negative_keyword']}' to {ow}",
                        ev or "no historical impressions",
                        "none - negative EXACT does not close-variant"
                        if p["negative_match_type"] == "EXACT"
                        else "modifier - collision tested",
                        "PASS", "REQUIRED" if p["kind"] != "MODIFIER ROUTING" else "REQUIRED",
                        "RECOMMENDED - NOT APPROVED"])
    print(f"\nWROTE {p1.name}  ({len(proposals)} rows)")

    p2 = AUD / "2026-08-31-skag-query-routing-simulation.csv"
    with p2.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sim_rows[0].keys()))
        w.writeheader(); w.writerows(sim_rows)
    print(f"WROTE {p2.name}  ({len(sim_rows)} rows)")

    p3 = AUD / "2026-08-31-skag-negative-collision-test.csv"
    with p3.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(coll_rows[0].keys()))
        w.writeheader(); w.writerows(coll_rows)
    print(f"WROTE {p3.name}  ({len(coll_rows)} rows)")

    summary = {
        "generated_account_local": now.isoformat(), "mode": "READ + DRAFT ONLY",
        "ad_groups": {ag: {"intent": s["intent"], "lp": s["lp"], "exists": s["exists"],
                           "keywords": s["keywords"]} for ag, s in OWNERS.items()},
        "unique_texts": len(all_texts),
        "mirror_raw": raw, "mirror_final": len(dedup),
        "supplement": len(supplement), "supplement_queries": len(obs),
        "modifiers_tested": len(modifier_rows),
        "modifiers_approved": len(mods_final),
        "total_proposed": len(proposals),
        "collision_assertions": len(coll_rows), "collisions": len(collisions),
        "routing_before_pct": round(100 * pass_before / len(SIM), 1),
        "routing_after_pct": round(100 * pass_after / len(SIM), 1),
        "residual_risks": [r["search_query"] for r in residuals],
    }
    p4 = SNAP / f"skag-matrix-{now.strftime('%Y-%m-%dT%H%M%S')}.json"
    p4.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"WROTE {p4.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
