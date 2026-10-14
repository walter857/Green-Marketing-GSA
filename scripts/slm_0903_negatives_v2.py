#!/usr/bin/env python3
"""NEG-1 rebuild for the pre-approval QA gate.

Adds three things the first pass did not do:

  1. BROAD-SUBSET REDUNDANCY. An existing BROAD negative N blocks any query
     containing all of N's words. A proposed PHRASE negative P blocks only
     queries containing P's words contiguously. If words(N) is a subset of
     words(P), then everything P would block is already blocked by N and P is
     redundant. The first pass only compared PHRASE-to-PHRASE, so this class of
     redundancy was invisible.
  2. SEVEN-WAY CLASSIFICATION, so ambiguous and owner-confirmation rows can be
     held out of the executable package.
  3. FULL PER-ROW EXPORT including the source search terms each negative stops.

Read-only. Writes 06-negative-plan-v2.csv, 06b-negative-rejected-v2.csv,
06d-negative-annex-nonexecutable.csv, 06c-coverage-v2.json.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from slm_0903_negatives import CANDIDATES, PROTECTED_WORDS  # noqa: E402

B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PATIO, PAVERS = "23484806108", "23489296528"
CAMP = {PATIO: "Patio", PAVERS: "Pavers"}

# Which of the seven QA-gate buckets each candidate family belongs to, and
# whether that bucket may appear in an EXECUTABLE package.
FAMILY_CLASS = {
    "asphalt":        ("high_confidence_wrong_service", True),
    "sealcoating":    ("high_confidence_wrong_service", True),
    "sealing":        ("high_confidence_wrong_service", True),
    "restoration":    ("high_confidence_wrong_service", True),
    "patio-cover":    ("high_confidence_wrong_service", True),
    "enclosure":      ("high_confidence_wrong_service", True),
    "deck-structure": ("high_confidence_wrong_service", True),
    "cleaning":       ("high_confidence_wrong_service", True),
    "employment":     ("employment_intent", True),
    "retail-diy":     ("diy_information_and_materials_intent", True),
    "equipment":      ("diy_information_and_materials_intent", True),
    # resurfacing is NOT owner-confirmed as out of scope. Held out.
    "resurfacing":    ("requires_business_confirmation", False),
}
HOLD_REASON = {
    "resurfacing": ("SLM-Q9 asks whether Softwind offers patio resurfacing. The "
                    "recovery brief lists it among the themes not to assume, but "
                    "no authoritative client source excludes it. Held out of the "
                    "executable package until the owner answers."),
}
# Owner-confirmation status per family, so nothing rests on search-term
# performance alone.
FAMILY_AUTHORITY = {
    "asphalt": "USER-2026-09-03 recovery prompt lists asphalt paving/repair/blacktop as out of scope",
    "sealcoating": "USER-2026-09-03 lists sealcoating and tar-and-chip as out of scope",
    "sealing": "USER-2026-09-03 lists paver sealing as out of scope for these work orders; this account runs a separate PAUSED Paver Sealing campaign (23914857298)",
    "restoration": "USER-2026-09-03 lists paver restoration, resanding and leveling as out of scope",
    "patio-cover": "USER-2026-09-03 lists patio covers, roofs, pergolas and gazebos as out of scope",
    "enclosure": "USER-2026-09-03 lists patio enclosures and screened patios as out of scope",
    "deck-structure": "USER-2026-09-03 lists decks as out of scope",
    "cleaning": "OWNER-2026-08-28 cross-account scope fence; cleaning belongs to 1521725229",
    "employment": "Not a buyer intent. Conservative agency default; no service claim involved",
    "retail-diy": "USER-2026-09-03 lists material-only/retail paver sales and DIY instruction as out of scope",
    "equipment": "Equipment rental and DIY casting are not a service this account sells",
    "resurfacing": "NO AUTHORITATIVE SOURCE. See SLM-Q9.",
}


def norm(t):
    return " ".join(str(t).lower().replace("+", " ").replace('"', " ").split())


def phrase_hits(q, n):
    return re.search(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", q) is not None


def broad_hits(q, n):
    qs = set(q.split())
    return all(w in qs for w in n.split())


def blocks(q, n, mt):
    if mt == "EXACT":
        return q == n
    if mt == "BROAD":
        return broad_hits(q, n)
    return phrase_hits(q, n)


PAUSED_BY_KW1 = {
    "asphalt contractor near me", "asphalt paving services near me",
    "asphalt services near me", "asphalt and paving companies near me",
    "local asphalt companies near me", "local asphalt paving companies",
    "local asphalt paving contractors",
}


def main() -> int:
    snap = json.loads((B / "01e-baseline-2.json").read_text(encoding="utf-8"))
    terms = list(csv.DictReader((B / "05-search-term-verdicts.csv").open(encoding="utf-8")))

    # ---- protected keyword texts, live AND paused, per campaign ----
    kw_protected = defaultdict(list)
    for key, k in snap["keywords"].items():
        if k["negative"] or k["campaign_id"] not in CAMP:
            continue
        kw_protected[k["campaign_id"]].append({
            "text": norm(k["text"]), "match": k["match_type"],
            "kw_status": k["status"], "ag_status": k["ad_group_status"],
            "ad_group": k["ad_group"],
            "live": k["status"] == "ENABLED" and k["ad_group_status"] == "ENABLED"})

    # ---- protected + target search terms ----
    st_protected, st_target = defaultdict(list), defaultdict(list)
    for t in terms:
        if t["campaign_id"] not in CAMP:
            continue
        row = {"term": norm(t["search_term"]), "verdict": t["verdict"],
               "cost": float(t["cost"]), "clicks": int(t["clicks"]),
               "conv": float(t["conversions"]), "impr": int(t["impressions"]),
               "family": t["wrong_service_family"],
               "ad_groups": t["ad_groups"], "kw": t["matched_keywords"]}
        (st_protected if t["verdict"] in ("KEEP", "WATCH", "UNRESOLVED", "UNCLASSIFIED")
         else st_target)[t["campaign_id"]].append(row)

    # ---- everything already blocking each campaign, with match type ----
    sc = snap["_shared_criteria"]
    existing = {}
    for cid in CAMP:
        S = set()
        for v in snap["campaign_negatives"].values():
            if v["campaign_id"] == cid:
                S.add((norm(v["text"]), v["match_type"]))
        for l in snap["shared_set_links"]:
            if l["campaign_id"] == cid:
                for t, m in sc.get(l["shared_set"], []):
                    S.add((norm(t), m))
        for t, m in sc.get("11980673249", []):
            S.add((norm(t), m))
        existing[cid] = S

    accepted, rejected, annex = [], [], []
    for family, items in CANDIDATES.items():
        bucket, executable = FAMILY_CLASS[family]
        for text, mt, reason in items:
            t = norm(text)
            words, chars = len(t.split()), len(t)
            wordset = set(t.split())
            for cid, cname in CAMP.items():
                rec = {
                    "package": "PLAN-SLM-NEG-2", "family": family,
                    "classification": bucket,
                    "authority": FAMILY_AUTHORITY[family],
                    "campaign_id": cid, "campaign": cname,
                    "negative_text": t, "match_type": mt, "level": "CAMPAIGN",
                    "target_resource_id": cid, "reason": reason,
                    "words": words, "chars": chars,
                    "rollback": "remove this campaign_criterion; no other object changes",
                }
                if words > 10 or chars > 80:
                    rec.update(decision="REJECT",
                               reject_reason="exceeds Google limit (10 words / 80 chars)")
                    rejected.append(rec); continue
                if t in PROTECTED_WORDS:
                    rec.update(decision="REJECT",
                               reject_reason="agency protected term")
                    rejected.append(rec); continue

                # 1. own-keyword collision
                hits = [k for k in kw_protected[cid] if blocks(k["text"], t, mt)]
                survivors = [h for h in hits if h["text"] not in PAUSED_BY_KW1]
                if survivors:
                    rec.update(
                        decision="REJECT",
                        reject_reason="collides with %d own keyword text(s), %d live"
                                      % (len(survivors),
                                         sum(1 for h in survivors if h["live"])),
                        collides_with="|".join(sorted({h["text"] for h in survivors})))
                    rejected.append(rec); continue
                dep = ""
                if hits:
                    dep = "PLAN-SLM-KW-2"
                    rec["dependency_note"] = (
                        "collides only with %d keyword(s) PLAN-SLM-KW-2 pauses; create "
                        "this negative only after that pause reads back" % len(hits))

                # 2. protected search-term collision
                sthits = [s for s in st_protected[cid] if blocks(s["term"], t, mt)]
                if sthits:
                    rec.update(
                        decision="REJECT",
                        reject_reason=("would block %d protected term(s), $%.2f, %d clicks, "
                                       "%.1f conv" % (len(sthits),
                                                      sum(s["cost"] for s in sthits),
                                                      sum(s["clicks"] for s in sthits),
                                                      sum(s["conv"] for s in sthits))),
                        collides_verdicts="|".join(sorted({s["verdict"] for s in sthits})))
                    rejected.append(rec); continue

                # 3a. exact duplicate of an existing negative
                if (t, mt) in existing[cid]:
                    rec.update(decision="REJECT",
                               reject_reason="already present as %s %s" % (mt, t))
                    rejected.append(rec); continue
                # 3b. NEW: subsumed by an existing BROAD negative
                subsumers = [n for n, m in existing[cid]
                             if m == "BROAD" and set(n.split()) <= wordset]
                if subsumers:
                    rec.update(
                        decision="REJECT",
                        reject_reason=("redundant: existing BROAD negative %r already "
                                       "blocks every query this would block"
                                       % sorted(subsumers, key=len)[0]),
                        subsumed_by="|".join(sorted(subsumers)[:5]))
                    rejected.append(rec); continue
                # 3c. subsumed by an existing PHRASE negative
                ph = [n for n, m in existing[cid] if m == "PHRASE" and phrase_hits(t, n)]
                if ph:
                    rec.update(decision="REJECT",
                               reject_reason="already covered by existing PHRASE negative",
                               subsumed_by="|".join(sorted(ph)[:5]))
                    rejected.append(rec); continue

                # 4. what it actually stops
                stopped = [s for s in st_target[cid] if blocks(s["term"], t, mt)]
                rec.update(
                    blocks_terms=len(stopped),
                    blocks_cost=round(sum(s["cost"] for s in stopped), 2),
                    blocks_clicks=sum(s["clicks"] for s in stopped),
                    blocks_impressions=sum(s["impr"] for s in stopped),
                    blocks_conversions=round(sum(s["conv"] for s in stopped), 1),
                    source_search_terms_blocked=len(stopped),
                    top_source_terms_by_cost="|".join(
                        s["term"] for s in sorted(stopped, key=lambda x: -x["cost"])[:5]),
                    source_campaign=cname,
                    collision_test="PASS - 0 own keywords, 0 protected terms, not redundant",
                    keywords_tested=len(kw_protected[cid]),
                    protected_terms_tested=len(st_protected[cid]),
                    existing_negatives_tested=len(existing[cid]),
                    dependency=dep or "none",
                    decision="ACCEPT")
                (accepted if executable else annex).append(rec)
                if not executable:
                    annex[-1]["hold_reason"] = HOLD_REASON.get(family, "")
                    annex[-1]["package"] = "ANNEX - NOT EXECUTABLE"

    # ---- coverage ----
    cov = {}
    for cid, cname in CAMP.items():
        tgt = st_target[cid]
        plan = [a for a in accepted if a["campaign_id"] == cid]
        hit = [s for s in tgt
               if any(blocks(s["term"], a["negative_text"], a["match_type"]) for a in plan)]
        cov[cname] = {
            "wrong_service_terms": len(tgt),
            "covered_terms": len(hit),
            "wrong_service_cost": round(sum(s["cost"] for s in tgt), 2),
            "covered_cost": round(sum(s["cost"] for s in hit), 2),
            "covered_clicks": sum(s["clicks"] for s in hit),
            "covered_conversions": round(sum(s["conv"] for s in hit), 1),
            "coverage_pct": round(100 * sum(s["cost"] for s in hit)
                                  / max(1e-9, sum(s["cost"] for s in tgt)), 1),
        }

    for name, rows in (("06-negative-plan-v2.csv", accepted),
                       ("06b-negative-rejected-v2.csv", rejected),
                       ("06d-negative-annex-nonexecutable.csv", annex)):
        if not rows:
            (B / name).write_text("", encoding="utf-8"); continue
        keys = sorted({k for r in rows for k in r})
        with (B / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader(); w.writerows(rows)
    (B / "06c-coverage-v2.json").write_text(json.dumps(cov, indent=2), encoding="utf-8")

    print("NEG REBUILD  candidates=%d  ACCEPT=%d  ANNEX(held)=%d  REJECT=%d"
          % (len(accepted) + len(annex) + len(rejected), len(accepted),
             len(annex), len(rejected)))
    byclass = defaultdict(lambda: [0, 0.0])
    for a in accepted:
        c = byclass[a["classification"]]
        c[0] += 1; c[1] += a["blocks_cost"]
    print("\n%-42s %6s %10s" % ("classification", "negs", "cost"))
    for k, v in sorted(byclass.items(), key=lambda x: -x[1][1]):
        print("%-42s %6d %10.2f" % (k, v[0], v[1]))
    print("\nREJECTIONS BY CAUSE")
    rr = defaultdict(int)
    for r in rejected:
        rr[r["reject_reason"].split(":")[0].split(",")[0]] += 1
    for k, v in sorted(rr.items(), key=lambda x: -x[1]):
        print("  %-64s %d" % (k[:64], v))
    print("\nCOVERAGE")
    for k, v in cov.items():
        print("  %-7s $%.2f of $%.2f (%.1f%%), %d terms, %d clicks, %.1f conv"
              % (k, v["covered_cost"], v["wrong_service_cost"], v["coverage_pct"],
                 v["covered_terms"], v["covered_clicks"], v["covered_conversions"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
