#!/usr/bin/env python3
"""Build and collision-test the Patio/Pavers wrong-service negative plan.

Every candidate is tested BEFORE it is proposed against:
  1. every live and paused positive keyword text in Patio and Pavers
     (a paused keyword is a future casualty - see the bare-noun trap),
  2. every KEEP / WATCH / UNRESOLVED search term in the corpus,
  3. the 1,4xx negatives already blocking each campaign (redundancy),
  4. Google's negative-keyword limits (<=10 words, <=80 chars).

A candidate that collides with any protected item is REJECTED, not softened.
Raw search-term strings stay on disk; stdout carries counts and the candidate
service vocabulary only.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "clients/softwind-landscape-masonry/recovery/2026-09-patio-pavers"
PATIO, PAVERS = "23484806108", "23489296528"
CAMP = {PATIO: "Patio", PAVERS: "Pavers"}

# --------------------------------------------------------------- candidates
# family -> [(text, match_type, rationale)]
# PHRASE = contiguous word sequence. EXACT = whole query.
# Never a bare noun the account sells. Every entry carries an intent qualifier
# or is a word this account can never legitimately serve.
CANDIDATES = {
    "asphalt": [
        ("asphalt", "PHRASE", "Softwind installs pavers, not asphalt. No in-scope keyword or KEEP term contains the word."),
        ("blacktop", "PHRASE", "Asphalt synonym. Never an in-scope intent."),
        ("tar and chip", "PHRASE", "Asphalt driveway surface, not a paver product."),
        ("macadam", "PHRASE", "Asphalt synonym."),
    ],
    "sealcoating": [
        ("sealcoating", "PHRASE", "Asphalt sealcoating. Out of scope for both work orders."),
        ("sealcoat", "PHRASE", "Sealcoating stem."),
        ("seal coating", "PHRASE", "Spaced spelling of sealcoating."),
        ("seal coat", "PHRASE", "Spaced spelling of sealcoat."),
    ],
    "sealing": [
        ("paver sealing", "PHRASE", "Belongs to this account's own PAUSED Paver Sealing campaign, not to Patio/Pavers."),
        ("paver sealer", "PHRASE", "Sealing product/service intent."),
        ("sealing service", "PHRASE", "Sealing service intent, qualified so it cannot catch install terms."),
        ("patio sealing", "PHRASE", "Sealing, not installation."),
        ("driveway sealing", "PHRASE", "Sealing, not installation."),
        ("concrete sealing", "PHRASE", "Sealing, not installation."),
        ("sealant", "PHRASE", "Sealing product."),
        ("stone sealer", "PHRASE", "Sealing product."),
    ],
    "restoration": [
        ("paver restoration", "PHRASE", "Restoration of existing pavers, not new installation."),
        ("paver resanding", "PHRASE", "Resanding existing pavers."),
        ("paver re sanding", "PHRASE", "Spaced spelling."),
        ("polymeric sand", "PHRASE", "Resanding material intent."),
        ("paver releveling", "PHRASE", "Releveling existing pavers."),
        ("paver leveling", "PHRASE", "Leveling existing pavers."),
        ("patio restoration", "PHRASE", "Restoration, not construction."),
    ],
    "resurfacing": [
        ("patio resurfacing", "PHRASE", "Resurfacing an existing slab, not building a patio."),
        ("concrete resurfacing", "PHRASE", "Resurfacing intent."),
        ("resurface", "PHRASE", "Resurfacing stem; no in-scope keyword or KEEP term uses it."),
        ("refinishing", "PHRASE", "Refinishing an existing surface."),
    ],
    "patio-cover": [
        ("patio cover", "PHRASE", "Roof/shade structure, not a patio surface."),
        ("covered patio", "PHRASE", "Roof/shade structure."),
        ("patio roof", "PHRASE", "Roof structure."),
        ("patio awning", "PHRASE", "Shade structure."),
        ("awning", "PHRASE", "Shade structure; never an in-scope intent."),
        ("canopy", "PHRASE", "Shade structure."),
        ("pergola", "PHRASE", "Structure, not hardscape surface."),
        ("gazebo", "PHRASE", "Structure, not hardscape surface."),
        ("patio shade", "PHRASE", "Shade structure."),
    ],
    "enclosure": [
        ("patio enclosure", "PHRASE", "Enclosure, not a patio surface."),
        ("screened patio", "PHRASE", "Enclosure."),
        ("screened in patio", "PHRASE", "Enclosure."),
        ("screen room", "PHRASE", "Enclosure."),
        ("sunroom", "PHRASE", "Enclosure."),
        ("patio enclosures", "PHRASE", "Enclosure plural."),
    ],
    "cleaning": [
        ("patio cleaning", "PHRASE", "Cleaning belongs to the sibling account Softwind Power Washing."),
        ("paver cleaning", "PHRASE", "Cleaning intent."),
        ("power washing", "PHRASE", "Sibling-account scope."),
        ("pressure washing", "PHRASE", "Sibling-account scope."),
        ("soft washing", "PHRASE", "Sibling-account scope."),
        ("house washing", "PHRASE", "Sibling-account scope."),
        ("patio washing", "PHRASE", "Cleaning intent."),
    ],
    "deck-structure": [
        ("wood deck", "PHRASE", "Wood decking, not hardscape. Bare 'deck' is NOT used: pool deck is in scope."),
        ("composite deck", "PHRASE", "Composite decking."),
        ("trex", "PHRASE", "Composite decking brand."),
        ("deck builder", "PHRASE", "Deck construction, not hardscape."),
        ("deck contractor", "PHRASE", "Deck construction."),
        ("decking", "PHRASE", "Decking material."),
        ("deck repair", "PHRASE", "Deck service."),
    ],
    "retail-diy": [
        ("home depot", "PHRASE", "Retail, not a contractor search."),
        ("lowes", "PHRASE", "Retail."),
        ("menards", "PHRASE", "Retail."),
        ("for sale", "PHRASE", "Material purchase intent."),
        ("wholesale", "PHRASE", "Material purchase intent."),
        ("supplier", "PHRASE", "Material purchase intent."),
        ("pavers for sale", "PHRASE", "Material purchase intent."),
        ("paver calculator", "PHRASE", "DIY planning."),
        ("how to install pavers", "PHRASE", "DIY instruction."),
        ("how to build a patio", "PHRASE", "DIY instruction."),
        ("do it yourself", "PHRASE", "DIY instruction."),
        ("diy", "PHRASE", "DIY instruction."),
        ("youtube", "PHRASE", "Instructional video intent."),
    ],
    "employment": [
        ("jobs", "PHRASE", "Employment, not a buyer."),
        ("hiring", "PHRASE", "Employment."),
        ("salary", "PHRASE", "Employment."),
        ("careers", "PHRASE", "Employment."),
        ("apprentice", "PHRASE", "Employment."),
    ],
    "equipment": [
        ("paver rental", "PHRASE", "Equipment rental."),
        ("plate compactor", "PHRASE", "Equipment."),
        ("paver machine", "PHRASE", "Equipment."),
        ("paver mold", "PHRASE", "DIY casting product."),
        ("paver molds", "PHRASE", "DIY casting product."),
    ],
}

PROTECTED_WORDS = {"near me", "quote", "price", "pricing", "cost", "best",
                   "hire", "local", "emergency"}

# Keyword texts that PLAN-SLM-KW-1 pauses. A negative whose ONLY keyword
# collision is with these is accepted with an explicit execution dependency:
# the pause must land and read back BEFORE the negative is created.
PAUSED_BY_KW1 = {
    "asphalt contractor near me",
    "asphalt paving services near me",
    "asphalt services near me",
    "asphalt and paving companies near me",
    "local asphalt companies near me",
    "local asphalt paving companies",
    "local asphalt paving contractors",
}


def norm(t: str) -> str:
    return " ".join(str(t).lower().replace("+", " ").replace('"', " ").split())


def phrase_hits(query: str, neg: str) -> bool:
    """PHRASE negative: neg's words appear contiguously, in order, in query."""
    return re.search(r"(?<![a-z0-9])" + re.escape(neg) + r"(?![a-z0-9])", query) is not None


def broad_hits(query: str, neg: str) -> bool:
    """BROAD negative: every word of neg appears somewhere in query."""
    qs = set(query.split())
    return all(w in qs for w in neg.split())


def blocks(query: str, neg: str, mt: str) -> bool:
    if mt == "EXACT":
        return query == neg
    if mt == "BROAD":
        return broad_hits(query, neg)
    return phrase_hits(query, neg)


def main() -> int:
    snap = json.loads((B / "01-before-snapshot.json").read_text(encoding="utf-8"))
    terms = list(csv.DictReader((B / "05-search-term-verdicts.csv").open(encoding="utf-8")))

    # ---- protected keyword texts, per campaign, live AND paused ----
    kw_protected = defaultdict(list)
    for k in snap["keywords"]:
        if k["negative"] or k["campaign_id"] not in CAMP:
            continue
        ag = snap["ad_groups"][k["ad_group_id"]]
        kw_protected[k["campaign_id"]].append({
            "text": norm(k["text"]), "match": k["match_type"],
            "kw_status": k["status"], "ag_status": ag["status"],
            "ad_group": ag["name"],
            "live": k["status"] == "ENABLED" and ag["status"] == "ENABLED",
        })

    # ---- protected search terms: KEEP, WATCH and UNRESOLVED, per campaign ----
    st_protected = defaultdict(list)
    st_target = defaultdict(list)
    for t in terms:
        if t["campaign_id"] not in CAMP:
            continue
        row = {"term": norm(t["search_term"]), "verdict": t["verdict"],
               "cost": float(t["cost"]), "clicks": int(t["clicks"]),
               "conv": float(t["conversions"])}
        if t["verdict"] in ("KEEP", "WATCH", "UNRESOLVED", "UNCLASSIFIED"):
            st_protected[t["campaign_id"]].append(row)
        else:
            st_target[t["campaign_id"]].append(row)

    # ---- negatives already blocking each campaign ----
    existing = json.loads((B / "_blocking_sets.json").read_text(encoding="utf-8"))
    existing = {c: [(norm(a), b) for a, b in v] for c, v in existing.items()}

    accepted, rejected = [], []
    for family, items in CANDIDATES.items():
        for text, mt, reason in items:
            t = norm(text)
            words, chars = len(t.split()), len(t)
            for cid, cname in CAMP.items():
                rec = {"family": family, "campaign_id": cid, "campaign": cname,
                       "text": t, "match_type": mt, "level": "CAMPAIGN",
                       "target_resource_id": cid, "reason": reason,
                       "words": words, "chars": chars}

                if words > 10 or chars > 80:
                    rec["decision"] = "REJECT"
                    rec["reject_reason"] = "exceeds Google negative limit (10 words / 80 chars)"
                    rejected.append(rec); continue
                if t in PROTECTED_WORDS:
                    rec["decision"] = "REJECT"
                    rec["reject_reason"] = "agency protected term"
                    rejected.append(rec); continue

                # 1. keyword collision (live or paused)
                hits = [k for k in kw_protected[cid] if blocks(k["text"], t, mt)]
                survivors = [h for h in hits if h["text"] not in PAUSED_BY_KW1]
                if survivors:
                    rec["decision"] = "REJECT"
                    rec["reject_reason"] = "collides with %d own keyword text(s), %d live" % (
                        len(survivors), sum(1 for h in survivors if h["live"]))
                    rec["collides_with"] = "|".join(sorted({h["text"] for h in survivors}))
                    rejected.append(rec); continue
                if hits:
                    rec["depends_on"] = "PLAN-SLM-KW-1"
                    rec["dependency_note"] = (
                        "collides only with %d keyword(s) that PLAN-SLM-KW-1 pauses; "
                        "create this negative only after that pause reads back" % len(hits))

                # 2. protected search-term collision
                sthits = [s for s in st_protected[cid] if blocks(s["term"], t, mt)]
                if sthits:
                    rec["decision"] = "REJECT"
                    rec["reject_reason"] = (
                        "would block %d protected search term(s) worth $%.2f, "
                        "%d clicks, %.1f conv" % (
                            len(sthits), sum(s["cost"] for s in sthits),
                            sum(s["clicks"] for s in sthits),
                            sum(s["conv"] for s in sthits)))
                    rec["collides_verdicts"] = "|".join(sorted({s["verdict"] for s in sthits}))
                    rejected.append(rec); continue

                # 3. redundancy against what already blocks this campaign
                red = [e for e in existing[cid] if e[0] == t and e[1] == mt]
                if red:
                    rec["decision"] = "REJECT"
                    rec["reject_reason"] = "already present as %s %s" % (mt, t)
                    rejected.append(rec); continue
                covered = [e for e in existing[cid]
                           if e[1] == "PHRASE" and phrase_hits(t, e[0])]
                if covered:
                    rec["decision"] = "REJECT"
                    rec["reject_reason"] = "already covered by existing PHRASE negative"
                    rejected.append(rec); continue

                # 4. what it actually stops
                stopped = [s for s in st_target[cid] if blocks(s["term"], t, mt)]
                rec["blocks_terms"] = len(stopped)
                rec["blocks_cost"] = round(sum(s["cost"] for s in stopped), 2)
                rec["blocks_clicks"] = sum(s["clicks"] for s in stopped)
                rec["blocks_conversions"] = round(sum(s["conv"] for s in stopped), 1)
                rec["decision"] = "ACCEPT"
                rec["rollback"] = "remove this campaign_criterion; no other object changes"
                accepted.append(rec)

    # ---- coverage: how much of the NEGATIVE bucket does the plan actually stop?
    cov = {}
    for cid, cname in CAMP.items():
        negterms = [s for s in st_target[cid]]
        plan = [a for a in accepted if a["campaign_id"] == cid]
        hit = [s for s in negterms
               if any(blocks(s["term"], a["text"], a["match_type"]) for a in plan)]
        cov[cname] = {
            "wrong_service_terms": len(negterms),
            "covered_terms": len(hit),
            "wrong_service_cost": round(sum(s["cost"] for s in negterms), 2),
            "covered_cost": round(sum(s["cost"] for s in hit), 2),
            "covered_clicks": sum(s["clicks"] for s in hit),
            "covered_conversions": round(sum(s["conv"] for s in hit), 1),
        }

    for name, rows in (("06-negative-plan.csv", accepted),
                       ("06b-negative-rejected.csv", rejected)):
        keys = sorted({k for r in rows for k in r})
        with (B / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)

    print("NEGATIVE PLAN - campaign level, Patio + Pavers")
    print("  candidates evaluated : %d" % (len(accepted) + len(rejected)))
    print("  ACCEPTED             : %d" % len(accepted))
    print("  REJECTED             : %d" % len(rejected))
    fam = defaultdict(lambda: [0, 0, 0.0, 0.0])
    for a in accepted:
        f = fam[a["family"]]
        f[0] += 1; f[1] += a["blocks_terms"]
        f[2] += a["blocks_cost"]; f[3] += a["blocks_conversions"]
    print("\n%-16s %5s %8s %10s %8s" % ("family", "negs", "terms", "cost", "conv"))
    for k in sorted(fam, key=lambda x: -fam[x][2]):
        v = fam[k]
        print("%-16s %5d %8d %10.2f %8.1f" % (k, v[0], v[1], v[2], v[3]))
    print("\nREJECTION REASONS")
    rr = defaultdict(int)
    for r in rejected:
        rr[r["reject_reason"].split(",")[0]] += 1
    for k, v in sorted(rr.items(), key=lambda x: -x[1]):
        print("  %-62s %d" % (k[:62], v))
    print("\nCOVERAGE OF THE CONFIRMED WRONG-SERVICE BUCKET")
    for k, v in cov.items():
        print("  %-7s %d/%d terms, $%.2f of $%.2f (%.1f%%), %d clicks, %.1f conv" % (
            k, v["covered_terms"], v["wrong_service_terms"], v["covered_cost"],
            v["wrong_service_cost"],
            100 * v["covered_cost"] / v["wrong_service_cost"] if v["wrong_service_cost"] else 0,
            v["covered_clicks"], v["covered_conversions"]))
    (B / "06c-coverage.json").write_text(json.dumps(cov, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
